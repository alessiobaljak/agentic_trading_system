"""Misura lo SPREAD REALE (bid/ask) dei perpetual USDT da Binance Futures.

Serve a sostituire le fasce di spread STIMATE (bot/core/costs.py) con dati veri:
spread round-trip = (ask - bid) / mid, misurato ora dall'order book. Raggruppa per
fascia di volume 24h e confronta con la mia stima, cosi' si vede quanto ero fuori.

Sola lettura. Uso sulla VPS (Binance raggiungibile):
    .venv/bin/python -m scripts.measure_spreads
"""
from __future__ import annotations

import requests

from bot.core.costs import liquidity_spread

FAPI = "https://fapi.binance.com"


def main() -> int:
    book = requests.get(f"{FAPI}/fapi/v1/ticker/bookTicker", timeout=20).json()
    tick = requests.get(f"{FAPI}/fapi/v1/ticker/24hr", timeout=20).json()
    vol = {t["symbol"]: float(t.get("quoteVolume", 0.0)) for t in tick}

    rows = []
    for b in book:
        sym = b["symbol"]
        if not sym.endswith("USDT"):
            continue
        bid, ask = float(b.get("bidPrice", 0) or 0), float(b.get("askPrice", 0) or 0)
        if bid <= 0 or ask <= 0:
            continue
        mid = (bid + ask) / 2
        spread = (ask - bid) / mid          # spread relativo (una gamba)
        rows.append((sym, vol.get(sym, 0.0), spread))

    # fasce di volume come nel modello di costo
    tiers = [(200e6, ">=200M"), (50e6, "50-200M"), (10e6, "10-50M"), (0, "<10M")]

    def tier(v):
        for thr, name in tiers:
            if v >= thr:
                return name
        return "<10M"

    from collections import defaultdict
    by_tier = defaultdict(list)
    for sym, v, s in rows:
        by_tier[tier(v)].append(s)

    print(f"Perp USDT con order book: {len(rows)}\n")
    print(f"{'fascia volume':<12} {'n':>4} {'spread REALE medio':>20} {'spread ROUND-TRIP':>18} {'mia STIMA (rt)':>16}")
    for _thr, name in tiers:
        ss = by_tier.get(name, [])
        if not ss:
            continue
        avg = sum(ss) / len(ss)
        # round-trip = attraversi lo spread all'entrata E all'uscita ~ 1x spread pieno
        rt = avg
        # la mia stima e' round-trip: uso il volume minimo della fascia per leggerla
        est = liquidity_spread({">=200M": 300e6, "50-200M": 80e6, "10-50M": 20e6, "<10M": 3e6}[name])
        print(f"{name:<12} {len(ss):>4} {avg*100:>18.4f}% {rt*100:>16.4f}% {est*100:>14.4f}%")

    print("\nLettura: confronta 'spread ROUND-TRIP' (reale) con 'mia STIMA'. Se sono")
    print("vicini, le fasce vanno bene; se no, aggiorno bot/core/costs.py coi valori veri")
    print("(o passo allo spread PER-COIN reale invece delle fasce).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
