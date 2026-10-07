"""Controllo rapido del modulo dati_btc: barre per timeframe, mark riempite, conteggi per periodo."""
from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import dati_btc as d

for tf in ["15m", "30m", "1h", "2h", "4h", "6h", "8h", "12h", "1d"]:
    x = d.carica(tf)
    c = d.fetta(x["last"], *d.COSTRUZIONE)
    v = d.fetta(x["last"], *d.VALIDAZIONE)
    assert len(x["last"]) == len(x["mark"]), tf
    assert all(a.ts == b.ts for a, b in zip(x["last"], x["mark"])), tf
    print(f"{tf:>4}: {len(x['last']):>7} barre, costruzione {len(c):>7}, validazione {len(v):>6}, mark riempite(15m) {x['mark_riempite_15m']}")
print("funding:", len(x["funding"]), "settlement; in costruzione", len(d.fetta_funding(x["funding"], *d.COSTRUZIONE)))
