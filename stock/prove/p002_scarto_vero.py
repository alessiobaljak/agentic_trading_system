"""Lo scarto VERO negli istanti in cui la prova 2 esegue su QQQ (controllo chiesto dal revisore, 24 ott 2026).

Lo scarto della prova 2 era la mediana misurata in momenti normali (`stock/dati/ESITO_CONTROLLI.md`); la
regola invece entra quando il prezzo si muove, e lo scarto può essere più largo. Qui: 400 ordini eseguiti,
scelti a caso con il seme 20261024, e per ognuno la prima quotazione valida nei 5 secondi dall'inizio del
minuto dell'esecuzione (l'ordine si esegue all'apertura di quella barra). Non cambia le regole: misura un
costo.

    python -m stock.prove.p002_scarto_vero
"""
from __future__ import annotations

from datetime import date

import numpy as np
import pandas as pd

from stock.dati import alpaca, archivio, controlli, scarto
from stock.prove.p001 import CAPITALE, IB_FISSO, MEZZO_SCARTO, PB, QUI
from stock.simulatore.costi import Costi
from stock.simulatore.motore import simula
from stock.strategie import ultima_mezzora as um
from stock.strategie import zona_di_rumore as zr

SEME = 20261024
CAMPIONE = 400


def main():
    cal = alpaca.calendario("2016-01-01", "2024-12-31")
    minuti = archivio.carica("QQQ", "1Min_raw")
    seduta = um.solo_seduta(minuti, cal)
    problemi, _ = controlli.controlla_minuti(minuti, cal)
    esclusi = {date.fromisoformat(p["quando"]) for p in problemi if p["controllo"] == "minuti mancanti"}
    seg = zr.prepara(seduta, cal, esclusi)
    r = simula(seduta, zr.strategia(seg), Costi(mezzo_scarto=MEZZO_SCARTO["QQQ"], slittamento=0.5 * PB, **IB_FISSO),
               capitale=CAPITALE)
    e = r.esecuzioni
    scelti = e.iloc[np.sort(np.random.default_rng(SEME).choice(len(e), size=min(CAMPIONE, len(e)), replace=False))]
    righe = []
    for _, x in scelti.iterrows():
        t0 = x["t"].to_pydatetime()
        q = scarto.quotazioni_valide(alpaca.quotazioni("QQQ", t0, t0 + pd.Timedelta(seconds=5), massimo=50))
        if q.empty:
            continue
        a = q.iloc[0]
        righe.append({"etichetta": x["etichetta"], "scarto": (a.ask - a.bid) / ((a.ask + a.bid) / 2)})
    df = pd.DataFrame(righe)
    usato = 2 * MEZZO_SCARTO["QQQ"]
    testo = ["# Prova 2 — lo scarto vero negli istanti degli ordini (QQQ)", "",
             f"Calcolato da `python -m stock.prove.p002_scarto_vero`: {len(df)} ordini misurati su {len(scelti)} scelti "
             f"(seme {SEME}) fra i {len(e)} eseguiti. Scarto usato nella prova: {usato / PB:.2f} punti base.", "",
             "| | Tutti | Decisioni | Fine giornata |", "|---|---|---|---|"]
    for nome, f in (("mediana", np.median), ("media", np.mean), ("90° percentile", lambda v: np.quantile(v, 0.9))):
        cel = [f(df["scarto"]) / PB, f(df.loc[df.etichetta == "decisione", "scarto"]) / PB,
               f(df.loc[df.etichetta == "fine giornata", "scarto"]) / PB]
        testo.append(f"| {nome} (punti base) | " + " | ".join(f"{c:.2f}" for c in cel) + " |")
    testo += ["", f"Rapporto fra la media misurata e lo scarto usato: **{df['scarto'].mean() / usato:.2f}**."]
    (QUI / "P002_scarto_vero.md").write_text("\n".join(testo) + "\n")
    print("\n".join(testo))


if __name__ == "__main__":
    main()
