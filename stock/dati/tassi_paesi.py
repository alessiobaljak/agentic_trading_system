"""I tassi interbancari a tre mesi (media del mese) dell'OECD per i paesi delle sei valute della prova 43, dalla banca dati FRED della
Fed di St. Louis (dati pubblici, senza chiave). Scrive `stock/prove/dati/P043_tassi.csv`: mese, fondo, tasso.

    python -m stock.dati.tassi_paesi
"""
from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

USCITA = Path(__file__).resolve().parents[1] / "prove" / "dati" / "P043_tassi.csv"
SERIE = {"FXA": "IR3TIB01AUM156N", "FXB": "IR3TIB01GBM156N", "FXC": "IR3TIB01CAM156N", "FXE": "IR3TIB01EZM156N",
         "FXF": "IR3TIB01CHM156N", "FXY": "IR3TIB01JPM156N"}
URL = "https://fred.stlouisfed.org/graph/fredgraph.csv?id={serie}"


def scarica(dal: str = "2015-01-01", al: str = "2024-12-01") -> pd.DataFrame:
    pezzi = []
    for fondo, serie in SERIE.items():
        r = requests.get(URL.format(serie=serie), timeout=60)
        r.raise_for_status()
        d = pd.read_csv(io.StringIO(r.text))
        d.columns = ["mese", "tasso"]
        d["tasso"] = pd.to_numeric(d["tasso"], errors="coerce")
        d = d[(d["mese"] >= dal) & (d["mese"] <= al)].dropna()
        d["mese"] = d["mese"].str[:7]
        d["fondo"] = fondo
        pezzi.append(d[["mese", "fondo", "tasso"]])
    return pd.concat(pezzi).sort_values(["mese", "fondo"]).reset_index(drop=True)


if __name__ == "__main__":
    t = scarica()
    t.to_csv(USCITA, index=False)
    print(f"{len(t)} righe, {t['mese'].nunique()} mesi, dal {t['mese'].min()} al {t['mese'].max()}")
