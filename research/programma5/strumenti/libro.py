"""Programma 5, fase 4: il libro degli ordini (REGOLE.md, sezione 10).

Scarica i file giornalieri ``bookDepth`` di Binance (ogni 30 secondi il valore in USDT degli ordini entro l'1-5% sopra e
sotto il prezzo), verifica il CHECKSUM, e tiene **solo le misure a ore** in ``research/data/p5/<SIMBOLO>/libro_ore.pkl``
(i file grezzi non si tengono; le impronte in ``research/programma5/libro_impronte.json``):

* ``imb{k}_fine`` e ``imb{k}_media`` (k = 1, 2, 5): squilibrio ``(acquisti - vendite) / (acquisti + vendite)`` entro il
  k% all'ultima rilevazione dell'ora e in media nell'ora;
* ``liq1_fine``, ``liq5_fine``, ``liq1_media``, ``liq5_media``: liquidita' (acquisti + vendite, USDT) entro l'1% e il 5%;
* ``n``: rilevazioni nell'ora.

Indice = ora dall'epoca; le misure dell'ora t sono note alla fine dell'ora t.

Uso: python3 -m research.programma5.strumenti.libro SIMBOLO ...
"""
from __future__ import annotations

import hashlib
import io
import json
import sys
import zipfile
from concurrent.futures import ThreadPoolExecutor
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd

from research.programma5.strumenti import motore5 as m5
from research.programma5.strumenti.scarico import BASE, _prendi, elenca
from research.src.dati import leggi_checksum

QUI = Path(__file__).resolve().parents[1]
DAL, AL = "2023-09-23", "2026-10-17"


def aggrega_giorno(contenuto: bytes) -> pd.DataFrame:
    with zipfile.ZipFile(io.BytesIO(contenuto)) as z:
        df = pd.read_csv(io.BytesIO(z.read(z.namelist()[0])))
    df = df[df["percentage"].isin([-5, -2, -1, 1, 2, 5])]
    t = pd.to_datetime(df["timestamp"], utc=True, errors="coerce")
    df = df.assign(sec=(t.astype("int64") // 10 ** 9)).dropna(subset=["sec"])
    larga = df.pivot_table(index="sec", columns="percentage", values="notional", aggfunc="last").sort_index()
    out = pd.DataFrame(index=larga.index)
    for k in (1, 2, 5):
        b, a = larga.get(-k), larga.get(k)
        out[f"imb{k}"] = (b - a) / (b + a)
    out["liq1"] = larga.get(-1) + larga.get(1)
    out["liq5"] = larga.get(-5) + larga.get(5)
    out["ora"] = (out.index.to_numpy() // 3600).astype(np.int64)
    g = out.groupby("ora")
    ris = pd.concat([g[["imb1", "imb2", "imb5", "liq1", "liq5"]].last().add_suffix("_fine"),
                     g[["imb1", "imb2", "imb5", "liq1", "liq5"]].mean().add_suffix("_media"),
                     g.size().rename("n")], axis=1)
    return ris


def _giorno(chiave: str):
    contenuto = _prendi(BASE + chiave)
    if contenuto is None:
        return chiave, None, None
    somma = _prendi(BASE + chiave + ".CHECKSUM")
    impronta = hashlib.sha256(contenuto).hexdigest()
    if somma is not None and leggi_checksum(somma, chiave) != impronta:
        raise RuntimeError(f"CHECKSUM diverso per {chiave}")
    return chiave, impronta, aggrega_giorno(contenuto)


def scarica(simbolo: str) -> int:
    file = m5.DATI / simbolo / "libro_ore.pkl"
    impronte_file = QUI / "libro_impronte.json"
    impronte = json.loads(impronte_file.read_text()) if impronte_file.exists() else {}
    fatte = impronte.get(simbolo, {})
    chiavi = [k for k in elenca(f"data/futures/um/daily/bookDepth/{simbolo}/")
              if DAL <= k.rsplit("-bookDepth-", 1)[1][:10] <= AL and k.rsplit("/", 1)[1] not in fatte]
    vecchio = pd.read_pickle(file) if file.exists() else pd.DataFrame()
    parti = [vecchio] if len(vecchio) else []
    with ThreadPoolExecutor(max_workers=8) as ex:
        for chiave, impronta, df in ex.map(_giorno, chiavi):
            if impronta is None:
                continue
            fatte[chiave.rsplit("/", 1)[1]] = impronta
            parti.append(df)
    if parti:
        tutto = pd.concat(parti)
        tutto = tutto[~tutto.index.duplicated(keep="last")].sort_index()
        file.parent.mkdir(parents=True, exist_ok=True)
        tutto.to_pickle(file)
    impronte[simbolo] = fatte
    impronte_file.write_text(json.dumps(impronte, indent=0, sort_keys=True))
    return len(chiavi)


def libro(simbolo: str, periodo: str, idea=None, storia_giorni: int = 100) -> pd.DataFrame:
    """Le misure a ore del periodo (con la storia prima), passando dal guardiano dei periodi."""
    m5.controlla_periodo(periodo, idea)
    file = m5.DATI / simbolo / "libro_ore.pkl"
    if not file.exists():
        return pd.DataFrame()
    df = pd.read_pickle(file)
    inizio, fine = m5.PERIODI[periodo]
    da = date.fromordinal(inizio.toordinal() - storia_giorni)
    lo = m5._ms_giorno(da) // 3_600_000
    hi = (m5._ms_giorno(fine) + 86_400_000) // 3_600_000
    return df[(df.index >= lo) & (df.index < hi)]


if __name__ == "__main__":
    for s in sys.argv[1:]:
        n = scarica(s)
        print(f"[libro] {s}: {n} giorni nuovi", flush=True)
