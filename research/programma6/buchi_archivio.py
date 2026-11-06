"""I giorni che mancano nell'archivio pubblico di Binance (data.binance.vision) per le candele giornaliere dei perpetui.

Il 6 novembre 2026: il 28 ottobre 2026 manca per tutte le monete, nel file del giorno (404) e nel file mensile di ottobre (30 righe
invece di 31). Il pannello della ricerca aveva quel giorno vuoto: il rendimento dal 27 al 29 ottobre si perdeva nel conto a tavolino.
Questo script cerca, per ogni moneta, i giorni senza candela fra la sua prima e la sua ultima candela dal ``--dal`` in poi, e li prende
dall'interfaccia pubblica di Binance (``/fapi/v1/klines``, la stessa candela giornaliera), in
``research/data/p6g/<SIMBOLO>/giorni_api/<SIMBOLO>-1d-<giorno>.csv`` (fuori da git). L'elenco dei giorni riempiti va in
``buchi_archivio.json``. ``seconda.candele`` usa questi file solo dove l'archivio non ha il giorno.

Uso: python3 -m research.programma6.buchi_archivio [--dal 2026-09-01]
"""
from __future__ import annotations

import json
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import requests

from research.programma5.strumenti import motore5 as m5
from research.programma6 import seconda as sc

QUI = Path(__file__).parent
URL = "https://www.binance.com/fapi/v1/klines"


def giorni_mancanti(simbolo: str, dal: int) -> list:
    c = sc.candele(simbolo)
    if c.empty:
        return []
    tutti = set(range(max(int(c.index.min()), dal), int(c.index.max()) + 1))
    return sorted(tutti - set(int(g) for g in c.index))


def riempi(simbolo: str, giorni: list) -> list:
    fatti = []
    cartella = sc.DATI / simbolo / "giorni_api"
    for g in giorni:
        ms = g * 86_400_000
        r = requests.get(URL, params={"symbol": simbolo, "interval": "1d", "startTime": ms, "endTime": ms + 86_399_999,
                                      "limit": 1}, timeout=30)
        if r.status_code != 200:
            continue
        righe = [x for x in r.json() if int(x[0]) == ms]
        if not righe:
            continue
        cartella.mkdir(parents=True, exist_ok=True)
        pd.DataFrame(righe, columns=m5.KLINE).to_csv(cartella / f"{simbolo}-1d-{sc.data(g)}.csv", index=False)
        fatti.append(sc.data(g))
    return fatti


def main():
    dal = sc.giorno(*map(int, (sys.argv[sys.argv.index("--dal") + 1] if "--dal" in sys.argv else "2026-09-01").split("-")))
    simboli = sorted(p.name for p in sc.DATI.iterdir() if p.is_dir())
    with ThreadPoolExecutor(8) as ex:
        mancanti = dict(zip(simboli, ex.map(lambda s: giorni_mancanti(s, dal), simboli)))
    mancanti = {s: g for s, g in mancanti.items() if g}
    with ThreadPoolExecutor(4) as ex:
        fatti = dict(zip(mancanti, ex.map(lambda s: riempi(s, mancanti[s]), mancanti)))
    per_giorno: dict = {}
    for s, gg in fatti.items():
        for g in gg:
            per_giorno.setdefault(g, []).append(s)
    out = {"aggiornato": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"), "dal": sc.data(dal),
           "fonte": "Binance, /fapi/v1/klines (interfaccia pubblica, da www.binance.com), candela giornaliera 1d",
           "monete_con_giorni_mancanti": len(mancanti), "riempiti": {g: len(v) for g, v in sorted(per_giorno.items())},
           "non_riempiti": {s: [sc.data(g) for g in mancanti[s] if sc.data(g) not in fatti.get(s, [])]
                            for s in mancanti if len(fatti.get(s, [])) < len(mancanti[s])}}
    (QUI / "buchi_archivio.json").write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items() if k != "non_riempiti"}, ensure_ascii=False),
          "non riempiti:", len(out["non_riempiti"]))


if __name__ == "__main__":
    main()
