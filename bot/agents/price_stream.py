"""
Stream WebSocket dei prezzi (Binance Futures) — per il PAPER, non per il live.

PERCHE' ESISTE
In live vero gli ordini TP/SL stanno appoggiati sul book: e' la matching engine di
Binance a farli scattare, nell'istante in cui il prezzo tocca il livello. In PAPER
non c'e' nessuno che lo faccia per noi: e' il bot a dover decidere se un livello e'
stato toccato. Leggendo le candele 1m via REST sappiamo SE un livello e' stato
toccato, ma non in che ORDINE: se in un minuto il prezzo ha sfiorato sia il TP1 sia
lo stop, la candela non dice quale sia venuto prima, e il bot deve assumere il peggio.

Questo stream elimina proprio quell'ambiguita': riceve OGNI trade in tempo reale e
tiene il range (max/min) accumulato dall'ultima lettura. Il bot lo consuma a ogni
tick e vede la sequenza reale dei prezzi.

DESIGN
- La rete gira in un thread separato (asyncio dentro il thread); il bot resta sincrono.
- `take_range(symbol)` restituisce (hi, lo) accumulati DALL'ULTIMA chiamata e AZZERA:
  cosi' ogni tick vede esattamente cio' che e' successo dal tick precedente.
- Tutto degrada: se lo stream non e' sano (`is_healthy()` False) il chiamante ricade
  sulle candele REST. Nessun percorso critico dipende dal WebSocket.
- La logica pura (accumulo del range, parsing dei messaggi) e' separata dalla rete,
  quindi testabile senza connessione.
"""
from __future__ import annotations

import asyncio
import json
import threading
import time
from typing import Iterable, Optional

from bot.config import settings

# combined stream dei FUTURES. `@aggTrade` = ogni trade eseguito (prezzo REALE
# scambiato, la stessa grandezza da cui sono fatte le candele del gate).
WS_BASE = ("wss://stream.binancefuture.com" if settings.BINANCE_TESTNET
           else "wss://fstream.binance.com")


class PriceStream:
    """Range (max/min) vivo per simbolo, alimentato dai trade in tempo reale."""

    def __init__(self, base_url: str = WS_BASE, stale_after_s: float = 60.0) -> None:
        self.base = base_url
        self.stale_after_s = stale_after_s
        self._ranges: dict[str, list[float]] = {}     # symbol -> [hi, lo]
        self._symbols: set[str] = set()
        self._lock = threading.Lock()
        self._stop_evt = threading.Event()
        self._thread: Optional[threading.Thread] = None
        self._last_msg_ts: float = 0.0
        self._generation = 0        # cambia quando cambia l'insieme di simboli
        self._loop: Optional[asyncio.AbstractEventLoop] = None

    # ------------------------------------------------------------------ #
    # Logica pura (testabile senza rete)                                 #
    # ------------------------------------------------------------------ #
    def observe(self, symbol: str, price: float) -> None:
        """Registra un prezzo osservato, allargando il range del simbolo."""
        if price <= 0:
            return
        with self._lock:
            r = self._ranges.get(symbol)
            if r is None:
                self._ranges[symbol] = [price, price]
            else:
                if price > r[0]:
                    r[0] = price
                if price < r[1]:
                    r[1] = price
            self._last_msg_ts = time.time()

    def take_range(self, symbol: str) -> tuple[Optional[float], Optional[float]]:
        """(hi, lo) accumulati dall'ultima chiamata, poi AZZERA per questo simbolo.

        Azzerare e' il punto: ogni tick deve vedere la finestra [tick precedente, ora],
        non una finestra sovrapposta. (None, None) se non e' arrivato nulla -> il
        chiamante ricade sulle candele REST."""
        with self._lock:
            r = self._ranges.pop(symbol, None)
        return (r[0], r[1]) if r else (None, None)

    def reset(self, symbol: str) -> None:
        """Butta il range accumulato per un simbolo. Da chiamare all'APERTURA di una
        posizione: i prezzi visti PRIMA dell'ingresso non possono riempire i suoi TP."""
        with self._lock:
            self._ranges.pop(symbol, None)

    def is_healthy(self) -> bool:
        """True se lo stream e' vivo e ha ricevuto qualcosa di recente. Se False il
        chiamante deve usare le candele REST."""
        if not self._symbols or self._thread is None or not self._thread.is_alive():
            return False
        with self._lock:
            last = self._last_msg_ts
        return last > 0 and (time.time() - last) < self.stale_after_s

    def set_symbols(self, symbols: Iterable[str]) -> None:
        """Aggiorna l'insieme dei simboli seguiti. Se cambia, la connessione viene
        riaperta con la nuova lista (le posizioni si aprono/chiudono ogni poche ore:
        i riconnessi sono rari, e cosi' il codice resta semplice)."""
        new = {s.upper() for s in symbols if s}
        with self._lock:
            if new == self._symbols:
                return
            self._symbols = new
            self._generation += 1
            # i range dei simboli non piu' seguiti non servono
            for sym in list(self._ranges):
                if sym not in new:
                    self._ranges.pop(sym, None)
        self._wake()

    def _stream_path(self, symbols: set[str]) -> str:
        streams = "/".join(f"{s.lower()}@aggTrade" for s in sorted(symbols))
        return f"/stream?streams={streams}"

    def _handle_raw(self, raw: str) -> None:
        """Parsa un messaggio del combined stream e aggiorna il range.
        Formato: {"stream": "btcusdt@aggTrade", "data": {"s": "BTCUSDT", "p": "123.4", ...}}"""
        try:
            msg = json.loads(raw)
        except Exception:  # noqa: BLE001
            return
        data = msg.get("data") if isinstance(msg, dict) else None
        if not isinstance(data, dict):
            data = msg if isinstance(msg, dict) else None
        if not isinstance(data, dict):
            return
        sym, price = data.get("s"), data.get("p")
        if not sym or price is None:
            return
        try:
            self.observe(str(sym).upper(), float(price))
        except (TypeError, ValueError):
            return

    # ------------------------------------------------------------------ #
    # Rete (thread separato)                                             #
    # ------------------------------------------------------------------ #
    def start(self) -> None:
        if self._thread is not None and self._thread.is_alive():
            return
        self._stop_evt.clear()
        self._thread = threading.Thread(target=self._run, name="price-stream", daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop_evt.set()
        self._wake()
        t = self._thread
        if t is not None:
            t.join(timeout=5.0)
        self._thread = None

    def _wake(self) -> None:
        """Sveglia il loop di rete (cambio simboli o stop) senza attenderlo."""
        loop = self._loop
        if loop is not None and loop.is_running():
            loop.call_soon_threadsafe(lambda: None)

    def _run(self) -> None:
        try:
            asyncio.run(self._serve())
        except Exception as exc:  # noqa: BLE001
            print(f"[price_stream] loop terminato: {exc}")

    async def _serve(self) -> None:
        self._loop = asyncio.get_running_loop()
        backoff = 1.0
        while not self._stop_evt.is_set():
            with self._lock:
                symbols, generation = set(self._symbols), self._generation
            if not symbols:
                await asyncio.sleep(1.0)
                continue
            try:
                import websockets

                url = f"{self.base}{self._stream_path(symbols)}"
                async with websockets.connect(url, ping_interval=20, close_timeout=5) as ws:
                    print(f"[price_stream] connesso · {len(symbols)} simboli")
                    backoff = 1.0
                    while not self._stop_evt.is_set():
                        with self._lock:
                            if self._generation != generation:
                                break        # lista simboli cambiata -> riconnetti
                        try:
                            raw = await asyncio.wait_for(ws.recv(), timeout=30.0)
                        except asyncio.TimeoutError:
                            continue         # nessun trade: normale su coin sottili
                        self._handle_raw(raw)
            except Exception as exc:  # noqa: BLE001
                # rete assente/instabile: si riprova con backoff. Il bot intanto usa REST.
                print(f"[price_stream] disconnesso ({exc}) · riprovo in {backoff:.0f}s")
                await asyncio.sleep(backoff)
                backoff = min(backoff * 2, 30.0)
