"""Programma 6: il DVOL di Deribit (volatilita' implicita a 30 giorni) di BTC ed ETH, chiusura giornaliera, dal 2021.
Scrive in ``research/data/dvol/<MONETA>.json`` (fuori da git) e in ``scarico_dvol.json`` quanti giorni e l'impronta.

Uso: python3 -m research.programma6.scarico_dvol
"""
from __future__ import annotations

import hashlib
import json
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

RADICE = Path(__file__).resolve().parents[2]
DATI = RADICE / "research" / "data" / "dvol"
QUI = Path(__file__).parent
URL = ("https://www.deribit.com/api/v2/public/get_volatility_index_data?currency={m}&start_timestamp={a}"
       "&end_timestamp={b}&resolution=1D")
INIZIO_MS = 1609459200000          # 2021-01-01


def scarica(moneta: str) -> dict:
    giorni, a = {}, INIZIO_MS
    fine = int(datetime.now(timezone.utc).timestamp() * 1000)
    while a < fine:
        b = min(fine, a + 900 * 86_400_000)
        req = urllib.request.Request(URL.format(m=moneta, a=a, b=b), headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=60) as r:
            for ts, _o, _h, _l, c in json.loads(r.read())["result"]["data"]:
                giorni[int(ts) // 86_400_000] = float(c)
        a = b
        time.sleep(0.5)
    return dict(sorted(giorni.items()))


def main() -> int:
    DATI.mkdir(parents=True, exist_ok=True)
    imp = {}
    for m in ("BTC", "ETH"):
        g = scarica(m)
        (DATI / f"{m}.json").write_text(json.dumps(g), encoding="utf-8")
        testo = "\n".join(f"{k} {v}" for k, v in g.items())
        imp[m] = {"giorni": len(g), "primo": min(g), "ultimo": max(g), "sha256": hashlib.sha256(testo.encode()).hexdigest()}
        print(f"[dvol] {m}: {len(g)} giorni", flush=True)
    imp["scaricato"] = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    (QUI / "scarico_dvol.json").write_text(json.dumps(imp, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
