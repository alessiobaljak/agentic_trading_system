"""I giorni che mancano nell'archivio pubblico di Binance per le candele da 1 minuto delle 100 monete della prova in avanti.

Il 6 novembre 2026: il 28 ottobre 2026 manca per tutte le monete (il file del giorno da 404). Senza quel giorno la prova in avanti non
vede i prezzi di 24 ore: uno stop o un obiettivo toccati quel giorno non si vedono. Questo script cerca, dal 1° ottobre 2026 (il periodo
A) all'ultimo giorno dell'archivio, i giorni con meno di 1.440 minuti, e li prende dall'interfaccia pubblica di Binance
(``/fapi/v1/klines``, 1 minuto) in ``research/data/p5/<SIMBOLO>/klines_api/<SIMBOLO>-1m-<giorno>.csv`` (fuori da git).
``motore5.minuti`` li usa solo per i minuti che l'archivio non ha. L'elenco va in ``research/programma5/buchi_archivio_minuti.json``.

Uso: python3 -m research.programma5.strumenti.buchi_archivio_minuti
"""
from __future__ import annotations

import json
from concurrent.futures import ThreadPoolExecutor
from datetime import date, datetime, timedelta, timezone

import pandas as pd
import requests

from research.programma5.strumenti import motore5 as m5

URL = "https://www.binance.com/fapi/v1/klines"
INIZIO = date(2026, 10, 1)
FUORI = m5.RADICE / "research" / "programma5" / "buchi_archivio_minuti.json"


def minuti_per_giorno(simbolo: str) -> dict:
    fine = date.today()
    parti = [m5._csv_da_zip(p, m5.KLINE) for p in m5._file(simbolo, "klines") if m5._dentro(p.name, INIZIO, fine)]
    if not parti:
        return {}
    t = m5._ms(pd.concat(parti, ignore_index=True)["open_time"]) // 86_400_000
    return t.value_counts().to_dict()


def riempi(simbolo: str) -> list:
    conta = minuti_per_giorno(simbolo)
    if not conta:
        return []
    primo = (datetime(INIZIO.year, INIZIO.month, INIZIO.day, tzinfo=timezone.utc).timestamp()) // 86400
    ultimo = max(conta)
    fatti = []
    for g in range(int(primo), int(ultimo) + 1):
        if conta.get(g, 0) >= 1440:
            continue
        ms = g * 86_400_000
        r = requests.get(URL, params={"symbol": simbolo, "interval": "1m", "startTime": ms, "endTime": ms + 86_399_999,
                                      "limit": 1500}, timeout=60)
        if r.status_code != 200 or not r.json():
            continue
        cartella = m5.DATI / simbolo / "klines_api"
        cartella.mkdir(parents=True, exist_ok=True)
        giorno = (date(1970, 1, 1) + timedelta(days=g)).isoformat()
        pd.DataFrame(r.json(), columns=m5.KLINE).to_csv(cartella / f"{simbolo}-1m-{giorno}.csv", index=False)
        fatti.append(f"{giorno} ({conta.get(g, 0)} minuti nell'archivio, {len(r.json())} presi)")
    return fatti


def main():
    cento = json.loads((m5.RADICE / "research" / "programma5" / "universo_top100.json").read_text())["scelte"]
    with ThreadPoolExecutor(4) as ex:
        fatti = dict(zip(cento, ex.map(riempi, cento)))
    out = {"aggiornato": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
           "fonte": "Binance, /fapi/v1/klines a 1 minuto (interfaccia pubblica, da www.binance.com)",
           "riempiti": {s: v for s, v in fatti.items() if v}}
    FUORI.write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")
    giorni = sorted({x.split(" ")[0] for v in out["riempiti"].values() for x in v})
    print("monete riempite:", len(out["riempiti"]), "giorni:", giorni)


if __name__ == "__main__":
    main()
