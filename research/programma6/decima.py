"""Programma 6, decima prova (DECIMA.md): C4 = CTREND (C1) con 30 indicatori, i 28 dell'articolo piu' il funding dei 7
giorni prima e la quota di acquisti a mercato dei 7 giorni prima; esame come la terza prova e conferma sulle 101-200.

Uso: python3 -m research.programma6.decima
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from research.programma6 import nona as no
from research.programma6 import ottava as ot
from research.programma6 import seconda as sc
from research.programma6 import sesta as se
from research.programma6 import settima as st
from research.programma6 import terza as te
from research.programma6.motore import TAKER

QUI = Path(__file__).parent
RIS = QUI / "risultati_decima"
PROVE_PROGRAMMA = 30


def indicatori_30(pan: dict, ps: dict) -> np.ndarray:
    lun_idx = ps["lunedi"] - pan["t0"]
    extra = np.stack([se.funding_7(pan, lun_idx), no.g1(pan, lun_idx)], axis=2)
    return np.concatenate([ps["Z"], extra], axis=2)


def corsa(pan: dict, ps: dict, Z: np.ndarray, U: np.ndarray, costo: np.ndarray) -> tuple:
    Zr = te.ranghi(Z, U)
    ct, tenute = te.segnale("C4", Zr, ps["R"], U, ps["peso"])
    Wt = te.pesi_portafoglio(ct, U, ps["peso"], True)
    df = te.conto(Wt, ps["R"], ps["F"], costo)
    df.index = ps["lunedi"]
    df["dal_funding"] = -df["funding"]
    return df, tenute


def esegui(log=print) -> dict:
    pan = sc.pannello()
    RIS.mkdir(exist_ok=True)
    ps = te.pannello_settimane(pan, log=lambda x: None)
    Z = indicatori_30(pan, ps)
    nomi = list(te.NOMI) + ["funding_7d", "acquisti_7d"]
    df, tenute = corsa(pan, ps, Z, ps["U"], sc.costi_moneta(ps["simboli"]))
    df.to_csv(RIS / "settimane_C4.csv.gz")
    jb = ps["simboli"].index("BTCUSDT")
    btc = pd.Series(ps["R"][:, jb], index=ps["lunedi"])
    e = te.esame(df, btc)
    sr = sc.sharpe_prove()
    for v in ("C1", "C2", "C3"):
        sr.append(json.loads((te.RIS / f"{v}.json").read_text())["intero"]["sharpe"])
    for v in ("F1", "F2"):
        sr.append(json.loads((se.RIS / f"{v}.json").read_text())["intero"]["sharpe"])
    sr.append(json.loads((ot.RIS / "esame.json").read_text())["cento"]["intero"]["sharpe"])
    nn = json.loads((no.RIS / "esame.json").read_text())
    sr += [nn["G1"]["cento"]["intero"]["sharpe"], nn["G2"]["cento"]["intero"]["sharpe"], e["intero"]["sharpe"]]
    i = e["intero"]
    e["sharpe_corretto"] = te.sharpe_corretto(i["sharpe"], i["settimane"], i["asimmetria"], i["curtosi"], sr, 52)
    e["prove_nel_conto"] = len(sr)
    e["esito"] = te.esito(e, e["sharpe_corretto"])
    conta = {}
    for s_ in tenute.values():
        for j in s_:
            conta[nomi[j]] = conta.get(nomi[j], 0) + 1
    e["indicatori_tenuti_quante_settimane"] = dict(sorted(conta.items(), key=lambda x: -x[1]))
    e["settimane_con_segnale"] = len(tenute)
    # conferma sulle monete 101-200: stessi indicatori, universo 101-200, costi piu' alti
    ps2 = te.pannello_settimane(pan, log=lambda x: None, da=100, a=200, indicatori_si=False)
    df2, _ = corsa(pan, ps, Z, ps2["U"], np.full(len(ps2["simboli"]), TAKER + st.SCARTO))
    df2.to_csv(RIS / "settimane_C4_101_200.csv.gz")
    c = no._conferma(df2)
    out = {"cento": e, "conferma_101_200": c,
           "esito": "VALIDA" if e["esito"] == "VALIDA" and c["esito"] == "CONFERMATA" else "non valida"}
    (RIS / "esame.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    log(f"[decima] cento: {e['esito']}; 101-200: {c['esito']}")
    return out


def rapporto() -> str:
    r = json.loads((RIS / "esame.json").read_text())
    e, c = r["cento"], r["conferma_101_200"]
    i, i2 = e["intero"], c["intero"]
    tenuti = e["indicatori_tenuti_quante_settimane"]
    righe = ["# Programma 6 — risultati della decima prova (CTREND con funding e acquisti aggressivi)", "",
             "Regole in `DECIMA.md` (scritte prima).", "", "## 1. Le 100 monete più scambiate (dal 6 giugno 2022)", "",
             f"* {100 * i['annuo']:+.1f}% l'anno, volatilità {100 * i['volatilita']:.1f}%, **Sharpe {i['sharpe']:.2f}**, discesa "
             f"massima {100 * i['discesa_max']:.1f}%; media settimanale {100 * e['boot']['media']:+.3f}% (intervallo "
             f"{100 * e['boot']['basso']:+.3f}; {100 * e['boot']['alto']:+.3f}).",
             f"* Sharpe corretto **{e['sharpe_corretto']:.2f}** con {e['prove_nel_conto']} prove; lato long "
             f"{100 * e['long_annuo']:+.1f}%, short {100 * e['short_annuo']:+.1f}% l'anno; a costi doppi "
             f"{100 * e['costi_doppi']:+.3f}% a settimana.",
             "* Per anno: " + ", ".join(f"{a} {100 * v:+.1f}%" for a, v in e["per_anno"].items())
             + f"; ultimo anno {100 * e['ultimo_anno']:+.1f}%; dopo l'aprile 2025 {100 * e['dopo_aprile_2025']['annuo']:+.1f}% "
               f"(Sharpe {e['dopo_aprile_2025']['sharpe']:.2f}).",
             f"* Quante settimane la rete elastica ha tenuto i due indicatori nuovi (su {e['settimane_con_segnale']}): funding "
             f"{tenuti.get('funding_7d', 0)}, acquisti {tenuti.get('acquisti_7d', 0)}.",
             f"* **Esito: {e['esito']}**", "", "## 2. Conferma sulle monete 101-200 (scarto 0,10%)", "",
             f"* {c['settimane_operate']} settimane dal {c['dal']}: {100 * i2['annuo']:+.1f}% l'anno, Sharpe {i2['sharpe']:.2f}; "
             f"p {c['boot']['p']:.4f}; ultimo anno {100 * c['ultimo_anno']:+.1f}%.",
             f"* **Esito: {c['esito']}**", "", f"**C4: {r['esito']}**"]
    testo = "\n".join(righe) + "\n"
    (QUI / "RISULTATI_DECIMA.md").write_text(testo, encoding="utf-8")
    return testo


if __name__ == "__main__":
    esegui(log=lambda x: print(x, flush=True))
    print(rapporto())
    print("DECIMA FINITA", flush=True)
