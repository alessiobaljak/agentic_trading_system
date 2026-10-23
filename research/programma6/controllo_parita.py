"""Programma 6: il controllo delle parita' del funding (CONTROLLO_PARITA.md). F5, F9 (F5 a ordini limite), K2 e F5 + M7 + K2
prima e dopo l'arrotondamento di `sesta.funding_7`; descrittivo, non e' una prova nuova.

Uso: python3 -m research.programma6.controllo_parita
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from research.programma6 import asticella as ast
from research.programma6 import cinquantaseiesima as cs
from research.programma6 import dodicesima as do
from research.programma6 import ottava as ot
from research.programma6 import quindicesima as qd
from research.programma6 import seconda as sc
from research.programma6 import sesta as se
from research.programma6 import terza as te
from research.programma6 import undicesima as un
from research.programma6 import ventiquattresima as vq

QUI = Path(__file__).parent
RIS = QUI / "risultati_controllo_parita"


def esegui(log=print) -> dict:
    pan = sc.pannello()
    ps = te.pannello_settimane(pan, log=lambda x: None, indicatori_si=False)
    lun = ps["lunedi"] - pan["t0"]
    sig = ot.sigma_30(pan, lun)
    costo = sc.costi_moneta(ps["simboli"])
    btc = pd.Series(ps["R"][:, ps["simboli"].index("BTCUSDT")], index=ps["lunedi"])
    S7 = se.funding_7(pan, lun)
    W5 = vq.pesi_banda(np.where(np.isfinite(sig), -S7, np.nan), ps["U"], sig)
    dopo = {"F5": te.conto(W5, ps["R"], ps["F"], costo)}
    dopo["F5"].index = ps["lunedi"]
    f9 = dopo["F5"].copy()
    f9["spese"] = cs.spese_a_limite(W5, ps["R"], ps["lunedi"], ps["simboli"], costo)[0]
    f9["netto"] = f9["lordo"] - f9["spese"] - f9["funding"]
    f9["netto_doppio"] = f9["lordo"] - 2 * f9["spese"] - f9["funding"]
    dopo["F9"] = f9
    k = do.segnale_k1(pan, ps, un.pannello_metrics(pan))
    dopo["K2"] = te.conto(vq.pesi_banda(np.where(np.isfinite(sig), k, np.nan), ps["U"], sig), ps["R"], ps["F"], costo)
    dopo["K2"].index = ps["lunedi"]
    m7 = pd.read_csv(QUI / "risultati_venticinquesima" / "settimane_M7.csv.gz", index_col=0)
    dopo["F5+M7+K2"] = qd.combina({"F5": dopo["F5"], "M7": m7, "K2": dopo["K2"]})
    prima = {"F5": "risultati_ventiquattresima/settimane_F5.csv.gz", "F9": "risultati_cinquantaseiesima/settimane_F9.csv.gz",
             "K2": "risultati_ventottesima/settimane_K2.csv.gz", "F5+M7+K2": "risultati_ventottesima/settimane_F5_M7_K2.csv.gz"}
    inizio = {"F5": se.INIZIO, "F9": se.INIZIO, "K2": sc.giorno(2022, 1, 3), "F5+M7+K2": sc.giorno(2022, 1, 3)}
    out, esami = {}, {}
    RIS.mkdir(exist_ok=True)
    for n, f in prima.items():
        p = pd.read_csv(QUI / f, index_col=0)
        ep = te.esame(p, btc, inizio=inizio[n])
        ed = te.esame(dopo[n], btc, inizio=inizio[n])
        dopo[n].to_csv(RIS / f"settimane_{n.replace('+', '_')}.csv.gz")
        esami[n] = ed["intero"]
        c = p.index[p.index >= inizio[n]].intersection(dopo[n].index)
        out[n] = {"prima": {k_: ep["intero"][k_] for k_ in ("sharpe", "annuo", "discesa_max")},
                  "dopo": {k_: ed["intero"][k_] for k_ in ("sharpe", "annuo", "discesa_max")} | {"per_anno": ed["per_anno"]},
                  "settimane_diverse": int((np.abs(p.loc[c, "netto"] - dopo[n].loc[c, "netto"]) > 1e-9).sum()),
                  "settimane": int(len(c))}
    r = ast.corretto_rivisto(ast.serie_nuove(), esami)
    for n in out:
        out[n]["corretto_con_aggiunta"] = r["candidate"][n]["corretto_con_aggiunta"]
        out[n]["t"] = r["candidate"][n]["t"]
    (RIS / "esame.json").write_text(json.dumps(out, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    righe = ["| Strategia | Sharpe prima | Sharpe dopo | l'anno dopo | discesa dopo | settimane cambiate | t dopo | "
             "Sharpe corretto dopo |", "|---|---|---|---|---|---|---|---|"]
    for n, x in out.items():
        righe.append(f"| {n} | {x['prima']['sharpe']:.3f} | **{x['dopo']['sharpe']:.3f}** | {100 * x['dopo']['annuo']:+.1f}% | "
                     f"{100 * x['dopo']['discesa_max']:.1f}% | {x['settimane_diverse']} su {x['settimane']} | {x['t']:.2f} | "
                     f"{x['corretto_con_aggiunta']:.2f} |")
    righe += ["", "Per anno dopo la correzione:", ""]
    for n, x in out.items():
        righe.append(f"* {n}: " + ", ".join(f"{a} {100 * v:+.1f}%" for a, v in x["dopo"]["per_anno"].items()))
    log("\n".join(righe))
    return out


if __name__ == "__main__":
    esegui(log=lambda x: print(x, flush=True))
    print("CONTROLLO PARITA FINITO", flush=True)
