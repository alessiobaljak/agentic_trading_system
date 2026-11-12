"""Costruisce l'elenco degli acquisti dei dirigenti fuori dall'S&P 500 per la prova 27, dai dati trimestrali della SEC già scaricati
(`stock/dati/dirigenti.py`) e dalla composizione storica dell'indice. Gira in locale (i dati della SEC non stanno su GitHub).

    python -m stock.prove.p027_acquisti --allora   # P027b_acquisti.csv.gz: l'indice con i simboli di allora (correzione dei dati)

L'elenco usato dalla prova 27 (`P027_acquisti.csv.gz`) era stato fatto a mano il 12 novembre 2026 portando anche i simboli dei
depositi ai nomi di oggi (UTX -> RTX...): questo programma senza `--allora` lo rifà quasi uguale (68 eventi in più su 23'447, quelli
con i simboli vecchi dei membri dell'indice) e scrive `P027_acquisti_rifatto.csv.gz`, per non sostituire il file usato dalla prova.

Filtri: moduli 4, codice P, dirigente o consigliere; deposito dal 2016-01-01 al 2024-11-30; simbolo fatto di 1-5 lettere (più una
classe); azienda fuori dall'S&P 500 il giorno del deposito; somma grezza degli acquisti dello stesso deposito almeno 100'000 dollari
(la pulizia sul prezzo si fa dopo, con i prezzi: `p027.eventi_puliti`). Una riga per operazione.
"""
from __future__ import annotations

import bisect
import sys
from datetime import date
from pathlib import Path

import pandas as pd

from stock.dati import dirigenti
from stock.prove.p001 import QUI
from stock.universo.costruisci import cambi_di_nome, carica_composizione

DAL, AL = date(2016, 1, 1), date(2024, 11, 30)


def operazioni() -> pd.DataFrame:
    pezzi = []
    for t in sorted(p.name for p in dirigenti.cartella().iterdir() if p.is_dir()):
        d = dirigenti.cartella() / t
        sub = pd.read_csv(d / "SUBMISSION.tsv", sep="\t", dtype=str,
                          usecols=["ACCESSION_NUMBER", "FILING_DATE", "DOCUMENT_TYPE", "ISSUERTRADINGSYMBOL"])
        own = pd.read_csv(d / "REPORTINGOWNER.tsv", sep="\t", dtype=str, usecols=["ACCESSION_NUMBER", "RPTOWNER_RELATIONSHIP"])
        tr = pd.read_csv(d / "NONDERIV_TRANS.tsv", sep="\t", dtype=str,
                         usecols=["ACCESSION_NUMBER", "TRANS_DATE", "TRANS_CODE", "TRANS_ACQUIRED_DISP_CD", "TRANS_SHARES",
                                  "TRANS_PRICEPERSHARE"])
        sub = sub[sub["DOCUMENT_TYPE"] == "4"]
        rel = own.groupby("ACCESSION_NUMBER")["RPTOWNER_RELATIONSHIP"].apply(lambda x: ",".join(x.fillna("")))
        tr = tr[(tr["TRANS_CODE"] == "P") & (tr["TRANS_ACQUIRED_DISP_CD"] == "A")]
        tr = tr[tr["ACCESSION_NUMBER"].isin(rel[rel.str.contains("Officer|Director", regex=True)].index)]
        tr = tr.assign(prezzo=pd.to_numeric(tr["TRANS_PRICEPERSHARE"], errors="coerce"))
        tr = tr.assign(valore=pd.to_numeric(tr["TRANS_SHARES"], errors="coerce") * tr["prezzo"]).dropna(subset=["valore"])
        pezzi.append(tr.merge(sub, on="ACCESSION_NUMBER"))
    df = pd.concat(pezzi, ignore_index=True)
    return pd.DataFrame({"deposito": pd.to_datetime(df["FILING_DATE"], format="%d-%b-%Y").dt.date,
                         "giorno_op": pd.to_datetime(df["TRANS_DATE"], format="%d-%b-%Y", errors="coerce").dt.date,
                         "simbolo": df["ISSUERTRADINGSYMBOL"].str.upper().str.strip().str.replace("-", ".", regex=False),
                         "valore": df["valore"], "prezzo": df["prezzo"], "modulo": df["ACCESSION_NUMBER"]})


def main(allora: bool = False):
    comp = carica_composizione(Path.home() / "stock_dati" / "sp500_storico.csv")
    cambi = {} if allora else cambi_di_nome()
    date_ = [d for d, _ in comp]
    insiemi = [{cambi.get(t, t) for t in m} for _, m in comp]
    df = operazioni()
    df = df[(df["deposito"] >= DAL) & (df["deposito"] <= AL)]
    df = df[df["simbolo"].fillna("").str.fullmatch(r"[A-Z]{1,5}(\.[A-Z])?")]
    nell_indice = [s in insiemi[max(bisect.bisect_right(date_, d) - 1, 0)] for d, s in zip(df["deposito"], df["simbolo"])]
    df = df[[not x for x in nell_indice]]
    somma = df.groupby(["deposito", "simbolo"])["valore"].transform("sum")
    df = df[somma >= 100_000].sort_values(["deposito", "simbolo", "modulo"]).reset_index(drop=True)
    nome = "P027b_acquisti.csv.gz" if allora else "P027_acquisti_rifatto.csv.gz"
    df.to_csv(QUI / "dati" / nome, index=False, compression="gzip")
    print(nome, len(df), df.groupby(["deposito", "simbolo"]).ngroups, df["simbolo"].nunique())


if __name__ == "__main__":
    main("--allora" in sys.argv)
