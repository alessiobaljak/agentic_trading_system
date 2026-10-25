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
