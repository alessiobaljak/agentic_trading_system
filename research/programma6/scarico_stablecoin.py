"""Programma 6: l'offerta totale delle stablecoin ancorate al dollaro, giorno per giorno, da DefiLlama
(stablecoins.llama.fi/stablecoincharts/all). Scrive in ``research/data/stablecoin/totale.json`` (fuori da git) e in
``scarico_stablecoin.json`` quanti giorni e l'impronta.

Uso: python3 -m research.programma6.scarico_stablecoin
"""
from __future__ import annotations

import hashlib
import json
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

RADICE = Path(__file__).resolve().parents[2]
DATI = RADICE / "research" / "data" / "stablecoin"
QUI = Path(__file__).parent
URL = "https://stablecoins.llama.fi/stablecoincharts/all"


def main() -> int:
    DATI.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(URL, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=60) as r:
        grezzo = json.loads(r.read())
    righe = [{"giorno": int(x["date"]) // 86400, "offerta": float(x["totalCirculatingUSD"]["peggedUSD"])}
             for x in grezzo if x.get("totalCirculatingUSD", {}).get("peggedUSD") is not None]
    (DATI / "totale.json").write_text(json.dumps(righe), encoding="utf-8")
    testo = "\n".join(f"{x['giorno']} {x['offerta']:.0f}" for x in righe)
    imp = {"giorni": len(righe), "primo": righe[0]["giorno"], "ultimo": righe[-1]["giorno"],
           "sha256": hashlib.sha256(testo.encode()).hexdigest(), "scaricato": datetime.now(timezone.utc).strftime("%Y-%m-%d")}
    (QUI / "scarico_stablecoin.json").write_text(json.dumps(imp, indent=1), encoding="utf-8")
    print(f"[stablecoin] {len(righe)} giorni", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
