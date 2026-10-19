"""Programma 6: quanto costerebbe davvero il cambio di posizioni del lunedì di F3 con gli ordini limite (misura
descrittiva dell'esecuzione, non una strategia nuova).

Per ogni variazione di peso di F3 il lunedì (dal 2021-01-04): a mercato all'apertura costa commissione a mercato + scarto
(come nelle prove). Con un ordine limite a ``δ`` dall'apertura (sotto per comprare, sopra per vendere), eseguito se nella
prima ora il prezzo **attraversa** il livello: costa la commissione da limite meno ``δ``; se non è eseguito, si compra o
vende a mercato all'apertura della seconda ora: commissione a mercato + scarto + quanto il prezzo si è mosso contro.
Candele da 1 ora: le 100 monete del programma 5 (`research/data/p6`, dai minuti verificati) e le monete mai usate
(`research/data/p6h`, dall'archivio).

Uso: python3 -m research.programma6.esecuzione
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from research.programma5.strumenti import motore5 as m5
from research.programma6 import dati as d6
from research.programma6 import ottava as ot
from research.programma6 import quarta as qa
from research.programma6 import seconda as sc
from research.programma6 import sesta as se
from research.programma6 import terza as te
from research.programma6.motore import MAKER, TAKER

QUI = Path(__file__).parent
DELTE = (0.0, 0.0005, 0.001, 0.002)


def ore_di(s: str) -> pd.DataFrame:
    b = d6.barre(s, "1h")
    if not b.empty:
        out = b[["open", "high", "low", "close"]].astype(float).copy()
        out.index = (b["minuto"].to_numpy() // 60).astype(np.int64)
        return out
    return qa.ore(s)


def esegui() -> dict:
    pan = sc.pannello()
    ps = te.pannello_settimane(pan, log=lambda x: None, indicatori_si=False)
    lun_idx = ps["lunedi"] - pan["t0"]
    S7 = se.funding_7(pan, lun_idx)
    sig = ot.sigma_30(pan, lun_idx)
    ct = np.where(np.isfinite(sig), -S7, np.nan)
    Wt = te.pesi_portafoglio(ct, ps["U"], np.nan_to_num(1.0 / sig), True)
    R0 = np.nan_to_num(ps["R"])
    deriva = np.zeros(Wt.shape[1])
    voci = []                       # (settimana, moneta, variazione con segno)
    for w in range(Wt.shape[0]):
        x = Wt[w]
        d = x - deriva
        if ps["lunedi"][w] >= se.INIZIO:
            for j in np.flatnonzero(np.abs(d) > 1e-9):
                voci.append((w, j, float(d[j])))
        lordo = float((x * R0[w]).sum())
        deriva = x * (1 + R0[w]) / (1 + lordo) if 1 + lordo > 0 else np.zeros_like(x)
    simboli = ps["simboli"]
    per_moneta = {}
    for w, j, dw in voci:
        per_moneta.setdefault(simboli[j], []).append((w, dw))
    righe = []
    for s, lista in per_moneta.items():
        b = ore_di(s)
        if b.empty:
            continue
        o, h, l = b["open"], b["high"], b["low"]
        slip = m5.scarto(s)
        for w, dw in lista:
            ora = int(ps["lunedi"][w]) * 24
            if ora not in b.index or ora + 1 not in b.index:
                continue
            p0, hi, lo, p1 = o.loc[ora], h.loc[ora], l.loc[ora], o.loc[ora + 1]
            if not all(np.isfinite([p0, hi, lo, p1])):
                continue
            compra = dw > 0
            r = {"peso": abs(dw), "mercato": TAKER + slip}
            for dl in DELTE:
                liv = p0 * (1 - dl) if compra else p0 * (1 + dl)
                preso = (lo < liv) if compra else (hi > liv)
                if preso:
                    r[f"limite_{dl}"] = MAKER - dl
                    r[f"eseguito_{dl}"] = 1.0
                else:
                    deriva_px = (p1 / p0 - 1) if compra else (1 - p1 / p0)
                    r[f"limite_{dl}"] = TAKER + slip + deriva_px
                    r[f"eseguito_{dl}"] = 0.0
            righe.append(r)
    df = pd.DataFrame(righe)
    pesi = df["peso"] / df["peso"].sum()
    out = {"variazioni": int(len(voci)), "con_le_ore": int(len(df)),
           "mercato": float((pesi * df["mercato"]).sum())}
    for dl in DELTE:
        out[f"limite_{dl}"] = {"costo_medio": float((pesi * df[f"limite_{dl}"]).sum()),
                               "eseguiti": float((pesi * df[f"eseguito_{dl}"]).sum())}
    giro_annuo = float(np.abs(np.array([v[2] for v in voci])).sum() / ((len(np.flatnonzero(ps["lunedi"] >= se.INIZIO))) / 52))
    out["giro_annuo"] = giro_annuo
    (QUI / "risultati_ottava" / "esecuzione.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    righe_md = ["# Programma 6 — il cambio del lunedì di F3 con gli ordini limite (descrittivo)", "",
                "Calcolo di `esecuzione.py` (descrittivo: misura il costo dell'esecuzione, non cambia la strategia). Dal "
                f"2021-01-04: {out['variazioni']} variazioni di peso, {out['con_le_ore']} con le candele da 1 ora "
                f"({100 * out['con_le_ore'] / max(1, out['variazioni']):.0f}%); giro di {out['giro_annuo']:.0f} volte il "
                "capitale l'anno.", "",
                "| Modo | Costo medio per unità scambiata | Eseguiti con il limite | Costo l'anno (sul giro) |",
                "|---|---|---|---|",
                f"| a mercato all'apertura (come le prove) | {100 * out['mercato']:.3f}% | — | {100 * out['mercato'] * giro_annuo:.1f}% |"]
    for dl in DELTE:
        x = out[f"limite_{dl}"]
        righe_md.append(f"| limite a {100 * dl:.2f}% dall'apertura, poi a mercato | {100 * x['costo_medio']:.3f}% | "
                        f"{100 * x['eseguiti']:.0f}% | {100 * x['costo_medio'] * giro_annuo:.1f}% |")
    (QUI / "ESECUZIONE.md").write_text("\n".join(righe_md) + "\n", encoding="utf-8")
    print("\n".join(righe_md))
    return out


if __name__ == "__main__":
    esegui()
