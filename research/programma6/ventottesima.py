"""Programma 6, ventottesima prova (VENTOTTESIMA.md): K2, il segnale di K1 con la banda di F5 (costruzione), e F5 + M7 +
K2 a rischio uguale. Dal 3 gennaio 2022.

Uso: python3 -m research.programma6.ventottesima
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from research.programma6 import dodicesima as do
from research.programma6 import ottava as ot
from research.programma6 import quattordicesima as q
from research.programma6 import quindicesima as qd
from research.programma6 import seconda as sc
from research.programma6 import terza as te
from research.programma6 import undicesima as un
from research.programma6 import venticinquesima as v25
from research.programma6 import ventiquattresima as vq

QUI = Path(__file__).parent
RIS = QUI / "risultati_ventottesima"


def esegui(log=print) -> dict:
    pan = sc.pannello()
    ps = te.pannello_settimane(pan, log=lambda x: None, indicatori_si=False)
    pm = un.pannello_metrics(pan)
    sig = ot.sigma_30(pan, ps["lunedi"] - pan["t0"])
    costo = sc.costi_moneta(ps["simboli"])
    k = do.segnale_k1(pan, ps, pm)
    k2 = te.conto(vq.pesi_banda(np.where(np.isfinite(sig), k, np.nan), ps["U"], sig), ps["R"], ps["F"], costo)
    k2.index = ps["lunedi"]
    k1 = do.portafoglio_k1(pan, ps, pm, costo)
    f5 = pd.read_csv(QUI / "risultati_ventiquattresima" / "settimane_F5.csv.gz", index_col=0)
    m7 = pd.read_csv(QUI / "risultati_venticinquesima" / "settimane_M7.csv.gz", index_col=0)
    f57 = pd.read_csv(QUI / "risultati_venticinquesima" / "settimane_F5_M7.csv.gz", index_col=0)
    tre = qd.combina({"F5": f5, "M7": m7, "K2": k2})
    RIS.mkdir(exist_ok=True)
    k2.to_csv(RIS / "settimane_K2.csv.gz")
    tre.to_csv(RIS / "settimane_F5_M7_K2.csv.gz")
    jb = ps["simboli"].index("BTCUSDT")
    btc = pd.Series(ps["R"][:, jb], index=ps["lunedi"])
    sr = v25.prove_fino_alla_ventiquattresima()
    e25 = json.loads((QUI / "risultati_venticinquesima" / "esame.json").read_text())
    sr += [e25["M7"]["intero"]["sharpe"], e25["F5 + M7"]["intero"]["sharpe"]]
    esami = {}
    for nome, df in (("K2", k2), ("F5 + M7 + K2", tre)):
        esami[nome] = te.esame(df, btc, inizio=q.INIZIO, anni_pieni=q.ANNI_PIENI)
        sr.append(esami[nome]["intero"]["sharpe"])
    for nome, df in (("K1", k1), ("F5 + M7", f57)):
        d = df[df.index >= q.INIZIO]
        esami[nome] = {"intero": te.numeri_settimana(d["netto"])}
    for nome in ("K2", "F5 + M7 + K2"):
        e = esami[nome]
        i = e["intero"]
        e["sharpe_corretto"] = te.sharpe_corretto(i["sharpe"], i["settimane"], i["asimmetria"], i["curtosi"], sr, 52)
        e["prove_nel_conto"] = len(sr)
        e["esito"] = te.esito(e, e["sharpe_corretto"])
    dk = k2[k2.index >= q.INIZIO]
    esami["K2_giro_spese"] = {"giro": float(dk["giro"].mean()), "spese_annue": float(dk["spese"].mean() * 52)}
    dk1 = k1[k1.index >= q.INIZIO]
    esami["K1_giro_spese"] = {"giro": float(dk1["giro"].mean()), "spese_annue": float(dk1["spese"].mean() * 52)}
    (RIS / "esame.json").write_text(json.dumps(esami, ensure_ascii=False, indent=1), encoding="utf-8")
    righe = ["# Programma 6 — risultati della ventottesima prova (K2: K1 con la banda; F5 + M7 + K2)", "",
             "Regole in `VENTOTTESIMA.md` (scritte prima). Le 100 monete più scambiate, dal 3 gennaio 2022. **K2 è una "
             "costruzione** (come K1): sul passato è informazione.", "",
             "| Variante | Rendimento/anno | Volatilità | Sharpe | Discesa massima | Sharpe corretto | Anni positivi | Ultimo anno | Esito |",
             "|---|---|---|---|---|---|---|---|---|"]
    for nome in ("K2", "F5 + M7 + K2"):
        e = esami[nome]
        i = e["intero"]
        anni = sum(1 for x in e["per_anno"].values() if x > 0)
        righe.append(f"| {nome} | {100 * i['annuo']:+.1f}% | {100 * i['volatilita']:.1f}% | {i['sharpe']:.2f} | "
                     f"{100 * i['discesa_max']:.1f}% | {e['sharpe_corretto']:.2f} | {anni}/{len(e['per_anno'])} | "
                     f"{100 * e['ultimo_anno']:+.1f}% | {e['esito']} |")
    for nome in ("K1", "F5 + M7"):
        i = esami[nome]["intero"]
        righe.append(f"| {nome} (confronto) | {100 * i['annuo']:+.1f}% | {100 * i['volatilita']:.1f}% | {i['sharpe']:.2f} | "
                     f"{100 * i['discesa_max']:.1f}% | — | — | — | — |")
    g2, g1 = esami["K2_giro_spese"], esami["K1_giro_spese"]
    righe += ["", f"Giro a settimana e spese l'anno: K2 {g2['giro']:.2f}, {100 * g2['spese_annue']:.1f}%; K1 {g1['giro']:.2f}, "
              f"{100 * g1['spese_annue']:.1f}%."]
    for nome in ("K2", "F5 + M7 + K2"):
        righe += ["", f"**{nome}, per anno**: " + ", ".join(f"{a} {100 * v:+.1f}%" for a, v in esami[nome]["per_anno"].items())]
    righe += ["", f"Sharpe corretto con {len(sr)} prove."]
    testo = "\n".join(righe) + "\n"
    (QUI / "RISULTATI_VENTOTTESIMA.md").write_text(testo, encoding="utf-8")
    log(testo)
    return esami


if __name__ == "__main__":
    esegui(log=lambda x: print(x, flush=True))
    print("VENTOTTESIMA FINITA", flush=True)
