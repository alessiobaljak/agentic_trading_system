"""Le date dei comunicati sui risultati (8-K, voce 2.02) delle aziende quotate, con il simbolo di allora e il settore (prova 34).

    python -m stock.dati.comunicati_piccole          # scarica dalla SEC e scrive stock/prove/dati/P034_comunicati.csv.gz

Le aziende: quelle che compaiono nei moduli dei dirigenti della SEC dal 2016 (`stock.dati.dirigenti`) con un simbolo di 1-4 lettere che
c'è nell'archivio di FINRA (quindi scambiato). Il simbolo di allora: quello scritto più spesso dall'azienda nei moduli dei dirigenti
depositati nei 365 giorni prima del comunicato. Dei file della SEC si tengono solo date e settore (`~/stock_dati/sec/piccole_202.csv`,
per riprendere se si ferma). Dati pubblici della SEC.
"""
from __future__ import annotations

import bisect
import json
import re
import time
from collections import Counter
from datetime import date, timedelta
from pathlib import Path

import pandas as pd
import requests

from stock.dati.archivio import cartella_dati
from stock.dati.bilanci import un_evento_per_trimestre
from stock.dati.dirigenti import cartella as cartella_form345

UA = {"User-Agent": "agentic-trading-system research"}
URL = "https://data.sec.gov/submissions/{nome}"
DAL, AL = date(2015, 12, 1), date(2024, 12, 31)
ORDINARIE = re.compile(r"[A-Z]{1,4}(\.[AB])?")
FINESTRA = timedelta(days=365)
QUI = Path(__file__).resolve().parent


def moduli_dirigenti() -> pd.DataFrame:
    pezzi = []
    for p in sorted(cartella_form345().iterdir()):
        f = p / "SUBMISSION.tsv"
        if f.exists() and p.name <= "2024q4":
            pezzi.append(pd.read_csv(f, sep="\t", dtype=str, keep_default_na=False,
                                     usecols=["FILING_DATE", "ISSUERCIK", "ISSUERTRADINGSYMBOL"]))
    s = pd.concat(pezzi)
    s = s[(s["ISSUERCIK"] != "") & (s["ISSUERTRADINGSYMBOL"] != "")]
    s["simbolo"] = s["ISSUERTRADINGSYMBOL"].str.upper().str.strip().str.replace("-", ".", regex=False)
    s["data"] = pd.to_datetime(s["FILING_DATE"], format="%d-%b-%Y").dt.date
    s["cik"] = s["ISSUERCIK"].astype(int)
    return s[s["simbolo"].str.fullmatch(ORDINARIE.pattern)][["cik", "simbolo", "data"]]


def simboli_finra() -> set[str]:
    d = pd.read_csv(cartella_dati() / "finra" / "vendite_scoperto.csv.gz", usecols=["settlementDate", "symbolCode",
                    "averageDailyVolumeQuantity"], dtype={"symbolCode": str}, keep_default_na=False)    # il simbolo «NA» non è vuoto
    d = d[(d["settlementDate"] <= AL.isoformat()) & (d["averageDailyVolumeQuantity"] > 0)]
    return {s for s in d["symbolCode"].astype(str).unique() if ORDINARIE.fullmatch(s)}


def _scarica(nome: str) -> dict | None:
    for prova in range(5):
        try:
            r = requests.get(URL.format(nome=nome), headers=UA, timeout=60)
        except requests.RequestException:
            time.sleep(2 * (prova + 1))
            continue
        time.sleep(0.17)
        if r.status_code == 200:
            return r.json()
        if r.status_code == 404:
            return None
        time.sleep(2 * (prova + 1))
    raise RuntimeError(f"SEC {nome}: non risponde")


def comunicati_e_settore(cik: int) -> tuple[int | None, list[date]]:
    """Il settore (SIC) e le date di deposito dei moduli 8-K con la voce 2.02 fra DAL e AL (con i file vecchi se servono)."""
    j = _scarica(f"CIK{cik:010d}.json")
    if j is None:
        return None, []
    sic = int(j["sic"]) if str(j.get("sic", "")).isdigit() else None
    pezzi = [j["filings"]["recent"]]
    for f in j["filings"].get("files", []):
        if f.get("filingTo", "9999") >= DAL.isoformat():
            x = _scarica(f["name"])
            if x:
                pezzi.append(x)
    giorni = set()
    for r in pezzi:
        for forma, d, voci in zip(r["form"], r["filingDate"], r["items"]):
            if forma == "8-K" and "2.02" in str(voci).split(",") and DAL.isoformat() <= d <= AL.isoformat():
                giorni.add(date.fromisoformat(d))
    return sic, sorted(giorni)


def simbolo_di_allora(date_moduli: list[date], simboli: list[str], giorno: date) -> str | None:
    a, b = bisect.bisect_left(date_moduli, giorno - FINESTRA), bisect.bisect_left(date_moduli, giorno)
    c = Counter(simboli[a:b])
    if not c:
        return None
    return sorted(c.items(), key=lambda x: (-x[1], x[0]))[0][0]


def main():
    m = moduli_dirigenti()
    traded = simboli_finra()
    ciks = sorted(set(m.loc[m["simbolo"].isin(traded), "cik"]))
    print(f"aziende da scaricare {len(ciks)}", flush=True)
    archivio = cartella_dati() / "sec" / "piccole_202.csv"
    fatti = {}
    if archivio.exists():
        a = pd.read_csv(archivio)
        fatti = {int(k): (None if v != v else int(v), json.loads(g)) for k, v, g in a[["cik", "sic", "date"]].itertuples(index=False)}
    with archivio.open("a") as f:
        if not fatti:
            f.write("cik,sic,date\n")
        for n, cik in enumerate(ciks):
            if cik in fatti:
                continue
            sic, giorni = comunicati_e_settore(cik)
            fatti[cik] = (sic, [g.isoformat() for g in giorni])
            f.write(f"{cik},{'' if sic is None else sic},\"{json.dumps(fatti[cik][1]).replace(chr(34), chr(34) * 2)}\"\n")
            f.flush()
            if n % 500 == 0:
                print(f"{n} su {len(ciks)}", flush=True)
    per_cik = {k: g.sort_values("data") for k, g in m.groupby("cik")}
    righe = []
    for cik, (sic, giorni) in fatti.items():
        if cik not in per_cik:
            continue
        g = per_cik[cik]
        dm, sm = list(g["data"]), list(g["simbolo"])
        for d in un_evento_per_trimestre([date.fromisoformat(x) for x in giorni]):
            s = simbolo_di_allora(dm, sm, d)
            if s:
                righe.append({"simbolo": s, "cik": cik, "deposito": d, "sic": sic})
    out = pd.DataFrame(righe).sort_values(["deposito", "simbolo"])
    out.to_csv(QUI.parent / "prove" / "dati" / "P034_comunicati.csv.gz", index=False)
    print(f"{len(out)} comunicati di {out['cik'].nunique()} aziende; settore 6770: {(out['sic'] == 6770).sum()}")


if __name__ == "__main__":
    main()
