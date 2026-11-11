"""Le vendite allo scoperto delle azioni americane (FINRA, «consolidated short interest»), due volte al mese.

Fonte: l'API pubblica di FINRA, senza chiave (provata l'11 novembre 2026): https://api.finra.org/data/group/otcMarket/name/
consolidatedShortInterest. Ogni riga: simbolo, data di regolamento (`settlementDate`, il 15 e la fine del mese circa), azioni vendute
allo scoperto (`currentShortPositionQuantity`), volume medio giornaliero (`averageDailyVolumeQuantity`) e i giorni per ricomprarle
(`daysToCoverQuantity` = vendute / volume medio). I dati partono dal 2018 (il 15 giugno 2018 c'è, il 15 giugno 2017 no). FINRA li
pubblica circa 7 giorni di borsa dopo la data di regolamento: chi li usa deve aspettare (regole delle prove).

I dati stanno fuori dal repository, in `<cartella dati>/finra/vendite_scoperto.csv.gz`.

    python -m stock.dati.finra --dal 2018-01-01 --al 2026-10-31
"""
from __future__ import annotations

import argparse
import time
from datetime import date, timedelta

import pandas as pd
import requests

from stock.dati import archivio

URL = "https://api.finra.org/data/group/otcMarket/name/consolidatedShortInterest"
CAMPI = ["settlementDate", "symbolCode", "currentShortPositionQuantity", "averageDailyVolumeQuantity", "daysToCoverQuantity"]
PAGINA = 5000


def _post(corpo: dict, tentativi: int = 6) -> list:
    attesa = 2.0
    for n in range(tentativi):
        try:
            r = requests.post(URL, json=corpo, headers={"Accept": "application/json"}, timeout=60)
            if r.status_code == 200:
                return r.json() if r.text.strip() else []
            if r.status_code == 204:
                return []
        except requests.RequestException:
            pass
        time.sleep(attesa)
        attesa *= 2
    raise RuntimeError("FINRA non risponde")


def righe_del_giorno(giorno: str, limite: int | None = None) -> list[dict]:
    filtro = [{"compareType": "EQUAL", "fieldName": "settlementDate", "fieldValue": giorno}]
    out, offset = [], 0
    while True:
        pag = _post({"limit": limite or PAGINA, "offset": offset, "fields": CAMPI, "compareFilters": filtro})
        out += pag
        if limite or len(pag) < PAGINA:
            return out
        offset += PAGINA


def date_candidate(dal: date, al: date) -> list[str]:
    """I giorni feriali vicini al 15 e alla fine di ogni mese (le date di regolamento cadono lì)."""
    out, d = [], dal
    while d <= al:
        fine = (d.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)
        if d.weekday() < 5 and (9 <= d.day <= 17 or d.day >= fine.day - 6):
            out.append(d.isoformat())
        d += timedelta(days=1)
    return out


def scarica(dal: date, al: date) -> pd.DataFrame:
    righe = []
    for g in date_candidate(dal, al):
        if righe_del_giorno(g, limite=1):
            tutte = righe_del_giorno(g)
            righe += tutte
            print(g, len(tutte), flush=True)
    df = pd.DataFrame(righe, columns=CAMPI)
    d = archivio.cartella_dati() / "finra"
    d.mkdir(parents=True, exist_ok=True)
    df.to_csv(d / "vendite_scoperto.csv.gz", index=False)
    return df


def carica() -> pd.DataFrame:
    df = pd.read_csv(archivio.cartella_dati() / "finra" / "vendite_scoperto.csv.gz")
    df["settlementDate"] = pd.to_datetime(df["settlementDate"]).dt.date
    return df


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--dal", default="2018-01-01")
    ap.add_argument("--al", default="2026-10-31")
    a = ap.parse_args()
    df = scarica(date.fromisoformat(a.dal), date.fromisoformat(a.al))
    print(f"righe {len(df)}, date {df['settlementDate'].nunique()}")
