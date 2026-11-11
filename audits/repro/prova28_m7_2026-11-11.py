"""Audit della prova 28 (11 novembre 2026): ricalcolo di M7 con i dati e il codice di oggi, come
`research/programma6/venticinquesima.esegui`, senza scrivere nei file della ricerca.

Scrive solo nella cartella data come argomento (di solito la cartella temporanea della sessione):
  Ps_seme{1..5}.npy  le previsioni di ogni seme (settimane x monete)
  Pm.npy             la media dei ranghi dei cinque semi (il segnale di M7)
  m7.csv.gz          il conto settimanale di M7 ricalcolato

Uso: python3 audits/repro/prova28_m7_2026-11-11.py <cartella_uscita>
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

import numpy as np

from research.programma6 import ottava as ot
from research.programma6 import quattordicesima as q
from research.programma6 import seconda as sc
from research.programma6 import terza as te
from research.programma6 import ventiquattresima as vq
from research.programma6 import ventitreesima as vt


def main(out: Path) -> None:
    out.mkdir(parents=True, exist_ok=True)
    t = time.time()
    pan = sc.pannello()
    ps = te.pannello_settimane(pan, log=lambda x: None)          # con gli indicatori, come la venticinquesima
    lun = ps["lunedi"] - pan["t0"]
    sig = ot.sigma_30(pan, lun)
    costo = sc.costi_moneta(ps["simboli"])
    X, nomi, Y = q.tabella_settimanale(pan, ps, ps["U"])
    np.save(out / "lunedi.npy", ps["lunedi"])
    print(f"tabella pronta: {X.shape}, {len(nomi)} ingredienti, {time.time() - t:.0f}s", flush=True)
    Ps = []
    for s in vt.SEMI:
        P = vt.previsioni_seme(s, X, Y, ps["U"], ps["lunedi"])
        np.save(out / f"Ps_seme{s}.npy", P)
        Ps.append(P)
        print(f"seme {s} fatto, {time.time() - t:.0f}s", flush=True)
    with np.errstate(all="ignore"):
        Pm = np.where(ps["U"], vt.media_ranghi(Ps, ps["U"]), np.nan)
    np.save(out / "Pm.npy", Pm)
    W7 = vq.pesi_banda(np.where(np.isfinite(sig), Pm, np.nan), ps["U"], sig)
    m7 = te.conto(W7, ps["R"], ps["F"], costo)
    m7.index = ps["lunedi"]
    m7.to_csv(out / "m7.csv.gz")
    print(f"M7 FINITO, {time.time() - t:.0f}s", flush=True)


if __name__ == "__main__":
    main(Path(sys.argv[1]))
