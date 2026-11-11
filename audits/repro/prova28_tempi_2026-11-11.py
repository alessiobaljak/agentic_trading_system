"""Audit della prova 28 (11 novembre 2026): i tempi.

1. Prova del taglio per M7: le previsioni del modello (seme 1) di un lunedi' rifatte con un pannello che si ferma alla
   domenica prima (piu' l'apertura del lunedi'); devono essere uguali a quelle del calcolo intero.
2. Entrata all'01:00 e alle 04:00 del lunedi' (candele orarie, `esecuzione.ore_di`) al posto dell'apertura delle 00:00,
   con gli stessi pesi; uscita alla stessa ora del lunedi' dopo. Monete senza candele orarie: il rendimento giornaliero.

Solo lettura della ricerca. Scrive solo ``audits/repro/prova28_tempi_2026-11-11_esito.json``.

Uso: python3 audits/repro/prova28_tempi_2026-11-11.py <cartella_m7>
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
import importlib  # noqa: E402

from research.programma6 import esecuzione as es  # noqa: E402
from research.programma6 import quattordicesima as q  # noqa: E402
from research.programma6 import quindicesima as qd  # noqa: E402
from research.programma6 import seconda as sc  # noqa: E402
from research.programma6 import terza as te  # noqa: E402
from research.programma6 import undicesima as un  # noqa: E402
from research.programma6 import ventitreesima as vt  # noqa: E402

a28 = importlib.import_module("prova28_2026-11-11")
QUI = Path(__file__).parent


def taglio_m7(pan, pm, cartella, date) -> dict:
    P1 = np.load(cartella / "Ps_seme1.npy")
    lunedi = np.load(cartella / "lunedi.npy")
    taker = q._taker_ls(pan)
    orig_pm, orig_tk = q.un.pannello_metrics, q._taker_ls
    out = {}
    try:
        for d in date:
            g = sc.giorno(*d)
            m = g - pan["t0"]
            p2, pm2 = a28.tagliato(pan, pm, m)
            tk2 = np.full((m + 8, taker.shape[1]), np.nan)
            tk2[:m] = taker[:m]
            q.un.pannello_metrics = lambda pan_, pm2=pm2: pm2
            q._taker_ls = lambda pan_, tk2=tk2: tk2
            ps2 = te.pannello_settimane(p2, log=lambda x: None)
            X2, _, Y2 = q.tabella_settimanale(p2, ps2, ps2["U"])
            P2 = vt.previsioni_seme(1, X2, Y2, ps2["U"], ps2["lunedi"])
            w2 = int(np.flatnonzero(ps2["lunedi"] == g)[0])
            w1 = int(np.flatnonzero(lunedi == g)[0])
            a, b = P2[w2], P1[w1]
            ok = np.isfinite(a) | np.isfinite(b)
            out[sc.data(g)] = {"monete": int(ok.sum()), "stesse_mancanti": bool((np.isfinite(a) == np.isfinite(b)).all()),
                               "differenza_massima": float(np.nanmax(np.abs(a[ok] - b[ok]))) if ok.any() else None}
    finally:
        q.un.pannello_metrics, q._taker_ls = orig_pm, orig_tk
    return out


def entrata_oraria(pan, ps, W, ore=(1, 4)) -> dict:
    lun = ps["lunedi"] - pan["t0"]
    usate = np.flatnonzero(np.abs(np.stack([W[n] for n in W])).sum(axis=0).sum(axis=0) > 0)
    R = {h: ps["R"].copy() for h in ore}
    coperte, tot = 0, 0
    for j in usate:
        s = ps["simboli"][j]
        try:
            o = es.ore_di(s)
        except Exception:
            o = pd.DataFrame()
        if o.empty:
            continue
        op = o["open"]
        for w in range(len(lun)):
            if not any(W[n][w, j] != 0 for n in W):
                continue
            tot += 1
            ora0 = (int(ps["lunedi"][w])) * 24
            fatto = True
            for h in ore:
                a, b = op.get(ora0 + h), op.get(ora0 + 7 * 24 + h)
                if a is None or b is None or not np.isfinite(a) or not np.isfinite(b):
                    fatto = False
                    continue
                R[h][w, j] = b / a - 1
            coperte += int(fatto)
    out = {"posizioni_con_le_ore": round(coperte / max(tot, 1), 3)}
    costo = sc.costi_moneta(ps["simboli"])
    for h in ore:
        comp = {}
        for n in W:
            x = te.conto(W[n], R[h], ps["F"], costo)
            x.index = ps["lunedi"]
            comp[n] = x
        tre = qd.combina({"F5": comp["F5"], "M7": comp["M7"], "K2": comp["K2"]})
        f = a28.FINE_FUNDING_VERO
        out[f"ore_{h:02d}"] = {"K2": a28.sharpe(a28.periodo(comp["K2"], f)["netto"]),
                               "F5": a28.sharpe(a28.periodo(comp["F5"], f)["netto"]),
                               "M7": a28.sharpe(a28.periodo(comp["M7"], f)["netto"]),
                               "F5 + M7 + K2": a28.sharpe(a28.periodo(tre, f)["netto"]),
                               "anni_positivi_miscela": a28.misure(a28.periodo(tre, f)["netto"])["anni_positivi"]}
    return out


def main(cartella: Path) -> dict:
    pan = sc.pannello()
    ps = te.pannello_settimane(pan, log=lambda x: None, indicatori_si=False)
    pm = un.pannello_metrics(pan)
    costo = sc.costi_moneta(ps["simboli"])
    Pm = np.load(cartella / "Pm.npy")
    W, _ = a28.tre_pesi(pan, ps, pm, Pm, costo)
    out = {"taglio_M7_seme_1": taglio_m7(pan, pm, cartella, [(2024, 8, 5), (2026, 10, 12)])}
    print(json.dumps(out, ensure_ascii=False), flush=True)
    out["entrata_oraria"] = entrata_oraria(pan, ps, W)
    (QUI / "prova28_tempi_2026-11-11_esito.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    return out


if __name__ == "__main__":
    o = main(Path(sys.argv[1]))
    print(json.dumps(o["entrata_oraria"], ensure_ascii=False))
