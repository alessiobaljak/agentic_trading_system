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

    ranges = {s: stream.take_range(s) for s in symbols}
    stream.stop()

    print()
    if healthy_at is None:
        print("[check] ❌ stream NON disponibile su questa macchina.")
        print("[check]    Il bot funziona comunque: ripiega sulle candele 1m via REST.")
        print("[check]    Per silenziare i tentativi: EXEC_PRICE_STREAM_ENABLED=false in .env")
        return 1

    print("[check] range osservato per simbolo (max/min dei trade ricevuti):")
    silent = []
    for sym, (hi, lo) in ranges.items():
        if hi is None:
            silent.append(sym)
            print(f"[check]   {sym}: nessun trade ricevuto")
        else:
            print(f"[check]   {sym}: max={hi} min={lo}  (ampiezza {(hi - lo):.8f})")
    if silent:
        print(f"[check] nota: {', '.join(silent)} senza trade nella finestra — normale "
              "su coin sottili, non e' un errore.")
    print("\n[check] ✅ OK: il paper usera' lo stream (e le candele REST come rete di sicurezza).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
