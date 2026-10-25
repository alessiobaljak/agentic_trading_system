"""Le operazioni dei dirigenti sulle azioni delle loro aziende (moduli 3, 4 e 5 della SEC), dai dati trimestrali pubblicati
dalla SEC: https://www.sec.gov/files/structureddata/data/insider-transactions-data-sets/{anno}q{n}_form345.zip

La SEC chiede, a chi scarica in automatico, un'intestazione con un indirizzo di contatto. L'indirizzo si legge solo
dall'ambiente (`SEC_CONTATTO`, per esempio «nome del progetto indirizzo@email») e non si scrive mai in un file né nel
repository: autorizzato dal proprietario il 25 ottobre 2026, solo per la SEC. Al massimo una richiesta al secondo.

Dei file si tengono solo le tabelle che servono (SUBMISSION, REPORTINGOWNER, NONDERIV_TRANS), in `~/stock_dati/sec/form345/`.

    python -m stock.dati.dirigenti 2016 2026     # scarica i trimestri mancanti
"""
from __future__ import annotations

import io
import os
import sys
import time
import zipfile

import requests

from stock.dati.archivio import cartella_dati

URL = "https://www.sec.gov/files/structureddata/data/insider-transactions-data-sets/{t}_form345.zip"
TABELLE = ("SUBMISSION.tsv", "REPORTINGOWNER.tsv", "NONDERIV_TRANS.tsv")


def intestazione() -> dict:
    contatto = os.environ.get("SEC_CONTATTO", "")
    if "@" not in contatto:
        raise RuntimeError("manca SEC_CONTATTO nell'ambiente (vedi il commento in cima al file)")
    return {"User-Agent": contatto}


def cartella():
    p = cartella_dati() / "sec" / "form345"
    p.mkdir(parents=True, exist_ok=True)
    return p


def scarica_trimestre(t: str) -> bool:
    dest = cartella() / t
    if all((dest / x).exists() for x in TABELLE):
        return True
    r = requests.get(URL.format(t=t), headers=intestazione(), timeout=300)
    time.sleep(1.0)
    if r.status_code == 404:
        return False
    r.raise_for_status()
    dest.mkdir(exist_ok=True)
    with zipfile.ZipFile(io.BytesIO(r.content)) as z:
        for nome in z.namelist():
            base = nome.split("/")[-1]
            if base in TABELLE:
                (dest / base).write_bytes(z.read(nome))
    return True


def main(dal: int, al: int) -> None:
    for anno in range(dal, al + 1):
        for n in range(1, 5):
            t = f"{anno}q{n}"
            ok = scarica_trimestre(t)
            print(t, "fatto" if ok else "non c'è", flush=True)


if __name__ == "__main__":
    main(int(sys.argv[1]), int(sys.argv[2]))


def acquisti(dal: str, al: str, valore_minimo: float = 100_000.0, chiusure=None, scarto_massimo: float = 0.5):
    """Gli acquisti sul mercato (codice P) di dirigenti e consiglieri, sommati per azienda e giorno di deposito
    (`stock/prove/P018_acquisti_dirigenti.md`). Colonne: deposito (data), simbolo, valore (dollari), moduli."""
    import pandas as pd
    pezzi = []
    for t in sorted(p.name for p in cartella().iterdir() if p.is_dir()):
        d = cartella() / t
        sub = pd.read_csv(d / "SUBMISSION.tsv", sep="\t", dtype=str, usecols=["ACCESSION_NUMBER", "FILING_DATE", "DOCUMENT_TYPE",
                                                                               "ISSUERTRADINGSYMBOL"])
        own = pd.read_csv(d / "REPORTINGOWNER.tsv", sep="\t", dtype=str, usecols=["ACCESSION_NUMBER", "RPTOWNER_RELATIONSHIP"])
        tr = pd.read_csv(d / "NONDERIV_TRANS.tsv", sep="\t", dtype=str,
                         usecols=["ACCESSION_NUMBER", "TRANS_DATE", "TRANS_CODE", "TRANS_ACQUIRED_DISP_CD", "TRANS_SHARES",
                                  "TRANS_PRICEPERSHARE"])
        sub = sub[sub["DOCUMENT_TYPE"] == "4"]
        rel = own.groupby("ACCESSION_NUMBER")["RPTOWNER_RELATIONSHIP"].apply(lambda x: ",".join(x.fillna("")))
        dirigente = rel[rel.str.contains("Officer|Director", regex=True)].index
        tr = tr[(tr["TRANS_CODE"] == "P") & (tr["TRANS_ACQUIRED_DISP_CD"] == "A")]
        tr = tr[tr["ACCESSION_NUMBER"].isin(dirigente)]
        tr = tr.assign(valore=pd.to_numeric(tr["TRANS_SHARES"], errors="coerce") * pd.to_numeric(tr["TRANS_PRICEPERSHARE"], errors="coerce"))
        tr = tr.dropna(subset=["valore"])
        x = tr.merge(sub, on="ACCESSION_NUMBER")
        pezzi.append(x[["ACCESSION_NUMBER", "FILING_DATE", "TRANS_DATE", "ISSUERTRADINGSYMBOL", "valore", "TRANS_PRICEPERSHARE"]])
    df = pd.concat(pezzi, ignore_index=True)
    df["deposito"] = pd.to_datetime(df["FILING_DATE"], format="%d-%b-%Y").dt.date
    df["simbolo"] = df["ISSUERTRADINGSYMBOL"].str.upper().str.strip().str.replace("-", ".", regex=False)
    df = df[(df["deposito"] >= pd.Timestamp(dal).date()) & (df["deposito"] <= pd.Timestamp(al).date())]
    if chiusure is not None:
        # pulizia: il prezzo dell'operazione deve stare entro il 50% dalla chiusura di quel giorno (o del giorno di borsa prima)
        df["giorno_op"] = pd.to_datetime(df["TRANS_DATE"], format="%d-%b-%Y", errors="coerce").dt.date
        df["prezzo"] = pd.to_numeric(df["TRANS_PRICEPERSHARE"], errors="coerce")
        def chiusura(r):
            c = chiusure(r["simbolo"])
            if c is None or pd.isna(r["giorno_op"]):
                return float("nan")
            prima = c.loc[:r["giorno_op"]]
            return float(prima.iloc[-1]) if len(prima) else float("nan")
        df["chiusura"] = df.apply(chiusura, axis=1)
        df = df[(df["prezzo"] / df["chiusura"] - 1).abs() <= scarto_massimo]
    g = df.groupby(["deposito", "simbolo"]).agg(valore=("valore", "sum"), moduli=("ACCESSION_NUMBER", "nunique")).reset_index()
    return g[g["valore"] >= valore_minimo].reset_index(drop=True)
