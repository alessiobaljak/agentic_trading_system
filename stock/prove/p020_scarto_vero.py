"""Lo scarto vero alle 9:35 nei giorni in gioco della prova 20 (controllo previsto dalle regole, dopo il calcolo; non cambia l'esito).
400 eventi scelti a caso con il seme 20261025; per ognuno la prima quotazione valida nei 5 secondi dalle 9:35.

    python -m stock.prove.p020_scarto_vero
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from stock.dati import alpaca, scarto
from stock.prove.p001 import PB, QUI
from stock.prove.p003 import RADICE, scarti_misurati
from stock.prove.p011 import membri_dell_indice
from stock.prove.p020 import operazioni

NY = "America/New_York"


def main():
    membri, _ = membri_dell_indice()
    cal = sorted(alpaca.calendario("2016-01-01", "2024-12-31").index)
    ops = operazioni(cal, membri)
    misurati = scarti_misurati(RADICE / "dati" / "ESITO_CONTROLLI_UNIVERSO.md")
    scelti = [ops[i] for i in np.sort(np.random.default_rng(20261025).choice(len(ops), size=400, replace=False))]
    righe = []
    for g, s, salto in scelti:
        t0 = pd.Timestamp(f"{g} 09:35", tz=NY).tz_convert("UTC").to_pydatetime()
        q = scarto.quotazioni_valide(alpaca.quotazioni(s, t0, t0 + pd.Timedelta(seconds=5), massimo=50))
        if q.empty:
            continue
        a = q.iloc[0]
        righe.append({"simbolo": s, "misurato": s in misurati, "scarto": (a.ask - a.bid) / ((a.ask + a.bid) / 2)})
    df = pd.DataFrame(righe)
    altri = df[~df.misurato]["scarto"] / PB
    testo = ["# Prova 20 — lo scarto vero alle 9:35 nei giorni in gioco", "",
             f"Calcolato da `python -m stock.prove.p020_scarto_vero`: {len(df)} eventi misurati su 400 scelti a caso (seme 20261025) fra i "
             f"{len(ops)} in gioco. Nella prova, per i titoli senza misura, lo scarto usato era 10 punti base (metà: 5), più 2 di slittamento.", "",
             f"* Titoli senza misura ({len(altri)} eventi): scarto mediano **{altri.median():.2f}** punti base, media {altri.mean():.2f}, 90° "
             f"percentile {altri.quantile(0.9):.2f}.",
             f"* Tutti: mediana {(df.scarto / PB).median():.2f}, media {(df.scarto / PB).mean():.2f} punti base.", "",
             "Non cambia l'esito della prova (le regole fissavano i costi prima); dice se la prudenza era giusta."]
    (QUI / "P020_scarto_vero.md").write_text("\n".join(testo) + "\n")
    print("\n".join(testo))


if __name__ == "__main__":
    main()
