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

    def __init__(self, base_url: str = WS_BASE, stale_after_s: float = 60.0,
                 min_move_frac: float | None = None,
                 max_path_points: int | None = None) -> None:
        self.base = base_url
        self.stale_after_s = stale_after_s
        # soglia sotto la quale un'inversione e' rumore (rimbalzo bid/ask) e non
        # apre un punto nuovo nel percorso; e tetto di punti per non crescere senza fine
        self.min_move_frac = (settings.EXEC_PATH_MIN_MOVE_FRAC
                              if min_move_frac is None else min_move_frac)
        self.max_path_points = (settings.EXEC_PATH_MAX_POINTS
                                if max_path_points is None else max_path_points)
        self._ranges: dict[str, list[float]] = {}     # symbol -> [hi, lo]
        self._paths: dict[str, list[float]] = {}      # symbol -> percorso ordinato (zigzag)
        self._truncated: set[str] = set()             # percorsi che hanno toccato il tetto
        self._symbols: set[str] = set()
        self._lock = threading.Lock()
        self._stop_evt = threading.Event()
        self._thread: Optional[threading.Thread] = None
        self._last_msg_ts: float = 0.0
        self._generation = 0        # cambia quando cambia l'insieme di simboli
        self._loop: Optional[asyncio.AbstractEventLoop] = None
        # --- diagnostica: distinguere "mai connesso" da "connesso ma muto" da
        # "messaggi ricevuti ma non interpretati". Senza questi un fallimento e'
        # indistinguibile da un altro e si finisce a indovinare.
        self._connected = False
        self._msgs_received = 0
        self._msgs_parsed = 0
        self._last_raw: Optional[str] = None      # campione dell'ultimo messaggio grezzo
        self._last_skip: Optional[str] = None     # perche' l'ultimo messaggio e' stato scartato
        self._last_error: Optional[str] = None    # ultimo errore di connessione
        self._last_url: Optional[str] = None      # URL richiesta (per vedere cosa chiediamo davvero)

    # ------------------------------------------------------------------ #
    # Logica pura (testabile senza rete)                                 #
    # ------------------------------------------------------------------ #
    def observe(self, symbol: str, price: float) -> None:
        """Registra un prezzo osservato: allarga il range E prolunga il PERCORSO.

        Il percorso e' la sequenza ORDINATA dei prezzi, compressa a zigzag: finche' il
        prezzo si muove nella stessa direzione si aggiorna l'ultimo punto (l'estremo
        raggiunto e' sempre conservato); a ogni INVERSIONE si aggiunge un punto nuovo.
        Cosi' il replay vede la stessa successione di livelli attraversati che avrebbe
        visto Binance, senza tenere in memoria ogni singolo trade.

        Le micro-inversioni sotto `min_move_frac` (rimbalzo bid/ask: rumore, non
        movimento) non creano punti. Non si perde nulla di sostanziale: il range vero
        continua ad allargarsi, e il chiamante lo usa come rete di sicurezza."""
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
            self._extend_path(symbol, price)
            self._last_msg_ts = time.time()

    def _extend_path(self, symbol: str, price: float) -> None:
        """Zigzag: estende il movimento in corso, o apre un punto nuovo se inverte.
        Da chiamare col lock GIA' preso."""
        pts = self._paths.setdefault(symbol, [])
        if not pts:
            pts.append(price)
            return
        if len(pts) >= self.max_path_points:
            self._truncated.add(symbol)   # tail coperto solo dal range aggregato
            return
        if len(pts) == 1:
            if price != pts[0]:
                pts.append(price)
            return
        going_up = pts[-1] > pts[-2]
        if (price > pts[-1]) if going_up else (price < pts[-1]):
            pts[-1] = price               # stesso verso: estende, non aggiunge
            return
        # inversione: solo se e' un movimento VERO, non rimbalzo bid/ask
        if abs(price - pts[-1]) >= self.min_move_frac * max(abs(pts[-1]), 1e-12):
            pts.append(price)

    def take(self, symbol: str) -> tuple[list[float], Optional[float], Optional[float], bool]:
        """(percorso, hi, lo, troncato) accumulati dall'ultima chiamata, poi AZZERA.

        Azzerare e' il punto: ogni tick deve vedere la finestra [tick precedente, ora],
        non una finestra sovrapposta. Il percorso serve per l'ORDINE dei livelli, il
        range come rete di sicurezza (non perde mai un estremo). `troncato` = il
        percorso ha raggiunto il tetto di punti, quindi la parte finale e' descritta
        solo dal range."""
        with self._lock:
            r = self._ranges.pop(symbol, None)
            path = self._paths.pop(symbol, [])
            trunc = symbol in self._truncated
            self._truncated.discard(symbol)
        if r is None:
            return [], None, None, False
        return path, r[0], r[1], trunc

    def take_range(self, symbol: str) -> tuple[Optional[float], Optional[float]]:
        """Solo (hi, lo), drenando come take(). Per chi non usa il percorso."""
        _, hi, lo, _ = self.take(symbol)
        return hi, lo

    def reset(self, symbol: str) -> None:
        """Butta quanto accumulato per un simbolo. Da chiamare all'APERTURA di una
        posizione: i prezzi visti PRIMA dell'ingresso non possono riempire i suoi TP."""
        with self._lock:
            self._ranges.pop(symbol, None)
            self._paths.pop(symbol, None)
            self._truncated.discard(symbol)

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
            for sym in list(self._paths):
                if sym not in new:
                    self._paths.pop(sym, None)
                    self._truncated.discard(sym)
        self._wake()

    def _stream_path(self, symbols: set[str]) -> str:
        streams = "/".join(f"{s.lower()}@aggTrade" for s in sorted(symbols))
        return f"/stream?streams={streams}"

    def _handle_raw(self, raw: str) -> None:
        """Parsa un messaggio del combined stream e aggiorna range + percorso.
        Formato: {"stream": "btcusdt@aggTrade", "data": {"s": "BTCUSDT", "p": "123.4", ...}}

        Ogni scarto viene REGISTRATO (`_last_skip`): un messaggio che non si interpreta
        e' la causa piu' probabile di "connesso ma mai sano", e senza traccia sarebbe
        invisibile."""
        with self._lock:
            self._msgs_received += 1
            if isinstance(raw, (bytes, bytearray)):
                self._last_raw = raw[:400].decode("utf-8", "replace")
            else:
                self._last_raw = str(raw)[:400]

        def skip(why: str) -> None:
            with self._lock:
                self._last_skip = why

        try:
            msg = json.loads(raw)
        except Exception as exc:  # noqa: BLE001
            return skip(f"JSON non valido: {exc}")
        # Binance segnala i problemi di sottoscrizione con {"error": {...}}: senza
        # questo ramo l'errore veniva ignorato e lo stream sembrava solo "muto".
        if isinstance(msg, dict) and msg.get("error"):
            return skip(f"errore dal server: {msg['error']}")
        data = msg.get("data") if isinstance(msg, dict) else None
        if not isinstance(data, dict):
            data = msg if isinstance(msg, dict) else None
        if not isinstance(data, dict):
            return skip(f"payload non riconosciuto: {type(msg).__name__}")
        sym, price = data.get("s"), data.get("p")
        if not sym or price is None:
            return skip(f"campi s/p assenti (chiavi: {sorted(data)[:8]})")
        try:
            value = float(price)
        except (TypeError, ValueError):
            return skip(f"prezzo non numerico: {price!r}")
        self.observe(str(sym).upper(), value)
        with self._lock:
            self._msgs_parsed += 1

    def stats(self) -> dict:
        """Fotografia diagnostica: serve a capire QUALE dei tre fallimenti possibili
        e' in corso (mai connesso / connesso ma muto / ricevuti ma non interpretati)."""
        with self._lock:
            return {
                "symbols": sorted(self._symbols),
                "connected": self._connected,
                "thread_alive": self._thread is not None and self._thread.is_alive(),
                "received": self._msgs_received,
                "parsed": self._msgs_parsed,
                "last_raw": self._last_raw,
                "last_skip": self._last_skip,
                "last_error": self._last_error,
                "last_url": self._last_url,
                "last_msg_age_s": (time.time() - self._last_msg_ts) if self._last_msg_ts else None,
            }

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
                with self._lock:
                    self._last_url = url
                async with websockets.connect(url, ping_interval=20, close_timeout=5) as ws:
                    print(f"[price_stream] connesso · {len(symbols)} simboli · {url}")
                    with self._lock:
                        self._connected = True
                        self._last_error = None
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
                with self._lock:
                    self._connected = False
                    self._last_error = f"{type(exc).__name__}: {exc}"
                print(f"[price_stream] disconnesso ({exc}) · riprovo in {backoff:.0f}s")
                await asyncio.sleep(backoff)
                backoff = min(backoff * 2, 30.0)
