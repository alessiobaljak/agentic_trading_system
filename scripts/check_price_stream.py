"""
Verifica che lo STREAM dei prezzi (WebSocket Binance) funzioni su QUESTA macchina.

Perche' serve: lo stream e' cio' che permette al paper di vedere la SEQUENZA dei
prezzi invece dei soli estremi di una candela 1m. Se il WebSocket e' bloccato
(firewall, proxy, provider) il bot NON si ferma: ripiega automaticamente sulle
candele REST — ma perde la capacita' di distinguere l'ordine dei prezzi dentro il
minuto. Meglio saperlo che scoprirlo dai numeri.

Uso (sul VPS):
    python -m scripts.check_price_stream                 # BTCUSDT+ETHUSDT, 15s
    python -m scripts.check_price_stream --symbols BTCUSDT --seconds 30
"""
from __future__ import annotations

import argparse
import time

from bot.agents.price_stream import PriceStream, WS_BASE


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--symbols", default="BTCUSDT,ETHUSDT",
                    help="simboli separati da virgola")
    ap.add_argument("--seconds", type=float, default=15.0,
                    help="quanto ascoltare prima di decidere")
    args = ap.parse_args()

    symbols = [s.strip().upper() for s in args.symbols.split(",") if s.strip()]
    print(f"[check] endpoint: {WS_BASE}")
    print(f"[check] simboli : {', '.join(symbols)}")
    print(f"[check] ascolto {args.seconds:.0f}s…\n")

    stream = PriceStream()
    stream.set_symbols(symbols)
    stream.start()

    deadline = time.time() + args.seconds
    healthy_at = None
    while time.time() < deadline:
        time.sleep(0.5)
        if healthy_at is None and stream.is_healthy():
            healthy_at = time.time()
            print(f"[check] ✅ stream SANO dopo ~{args.seconds - (deadline - healthy_at):.1f}s")

    taken = {s: stream.take(s) for s in symbols}
    st = stream.stats()
    stream.stop()

    print()
    print(f"[check] URL richiesta  : {st['last_url']}")
    print(f"[check] connesso ora   : {st['connected']}")
    print(f"[check] messaggi ricevuti  : {st['received']}")
    print(f"[check] messaggi interpretati: {st['parsed']}")
    if st["last_error"]:
        print(f"[check] ultimo errore rete : {st['last_error']}")
    if st["last_skip"]:
        print(f"[check] ultimo scarto      : {st['last_skip']}")
    if st["last_raw"]:
        print(f"[check] ultimo messaggio   : {st['last_raw'][:300]}")
    print()

    # Tre fallimenti DIVERSI, con rimedi diversi: distinguerli e' il punto di questo script.
    if not st["received"] and not st["connected"]:
        print("[check] ❌ mai connesso: rete/firewall bloccano il WebSocket.")
        print("[check]    Il bot funziona comunque: ripiega sulle candele 1m via REST.")
        print("[check]    Per silenziare i tentativi: EXEC_PRICE_STREAM_ENABLED=false in .env")
        return 1
    if not st["received"]:
        print("[check] ❌ connesso ma NESSUN messaggio ricevuto.")
        print("[check]    Sottoscrizione probabilmente rifiutata (nomi stream/endpoint).")
        print(f"[check]    Endpoint usato: {WS_BASE} · con BINANCE_TESTNET la base cambia.")
        return 1
    if not st["parsed"]:
        print("[check] ❌ messaggi ricevuti ma NESSUNO interpretato.")
        print("[check]    Il formato non e' quello atteso: vedi 'ultimo scarto' e")
        print("[check]    'ultimo messaggio' qui sopra — bastano per correggere il parser.")
        return 1

    print("[check] percorso e range per simbolo:")
    silent, broken = [], []
    for sym, (path, hi, lo, trunc) in taken.items():
        if hi is None:
            silent.append(sym)
            print(f"[check]   {sym}: nessun trade nella finestra")
            continue
        # INVARIANTE di fedelta': gli estremi del PERCORSO devono coincidere con quelli
        # del range. Se coincidono, il percorso copre tutta l'escursione e nessun
        # attraversamento e' stato perso — e' una PROVA, non un'impressione.
        # Pochi punti non sono un problema: un tratto monotono collassa in un segmento
        # e i prezzi identici (il bookTicker aggiorna anche solo le quantita') non
        # creano punti. Un percorso troncato, invece, per costruzione non la rispetta.
        ok = bool(path) and abs(max(path) - hi) < 1e-9 and abs(min(path) - lo) < 1e-9
        if not ok and not trunc:
            broken.append(sym)
        print(f"[check]   {sym}: max={hi} min={lo} (ampiezza {hi - lo:.8g}) · "
              f"{len(path)} punti · fedelta' {'OK' if ok else 'DA VERIFICARE'}"
              f"{' (TRONCATO)' if trunc else ''}")
    if broken:
        print(f"[check] ⚠️  {', '.join(broken)}: gli estremi del percorso NON coincidono")
        print("[check]    col range — il percorso sta perdendo movimenti, va indagato.")
    if silent:
        print(f"[check] nota: {', '.join(silent)} senza trade — normale su coin sottili.")
    if healthy_at is None:
        print("\n[check] ⚠️  messaggi interpretati ma is_healthy() era ancora False "
              "durante l'ascolto: possibile finestra di attesa troppo breve.")
        return 1
    print("\n[check] ✅ OK: il paper rigiochera' il percorso reale dei prezzi, in ordine.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
