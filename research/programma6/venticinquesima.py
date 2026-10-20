"""Programma 6, venticinquesima prova (VENTICINQUESIMA.md): M7, la previsione di M6 (media dei ranghi di cinque semi) con
la banda di F5 (entrata nel 20%, uscita sotto il 40%); e F5 + M7 a rischio uguale. Dal 3 gennaio 2022.

Uso: python3 -m research.programma6.venticinquesima
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from research.programma6 import diciottesima as di
from research.programma6 import ottava as ot
from research.programma6 import quattordicesima as q
from research.programma6 import quindicesima as qd
from research.programma6 import seconda as sc
from research.programma6 import sesta as se
from research.programma6 import terza as te
from research.programma6 import ventiquattresima as vq
from research.programma6 import ventitreesima as vt

QUI = Path(__file__).parent
RIS = QUI / "risultati_venticinquesima"


def prove_fino_alla_ventiquattresima() -> list:
    sr = di.prove_fino_alla_diciassettesima()
    for n, f in (("N1", "risultati_diciottesima"), ("N2", "risultati_diciottesima"), ("P1", "risultati_diciannovesima"),
                 ("P2", "risultati_diciannovesima"), ("S1", "risultati_ventesima"), ("S2", "risultati_ventesima")):
        sr.append(json.loads((QUI / f / "esame.json").read_text())[n]["intero"]["sharpe"])
    for f in ("risultati_ventitreesima", "risultati_ventiquattresima"):
        sr.append(json.loads((QUI / f / "esame.json").read_text())["intero"]["sharpe"])
    return sr


def esegui(log=print) -> dict:
    pan = sc.pannello()
    ps = te.pannello_settimane(pan, log=lambda x: None)
    lun = ps["lunedi"] - pan["t0"]
    sig = ot.sigma_30(pan, lun)
    costo = sc.costi_moneta(ps["simboli"])
    X, _, Y = q.tabella_settimanale(pan, ps, ps["U"])
    Ps = []
    for s in vt.SEMI:
        Ps.append(vt.previsioni_seme(s, X, Y, ps["U"], ps["lunedi"]))
        log(f"[venticinquesima] seme {s} fatto")
    with np.errstate(all="ignore"):
        Pm = np.where(ps["U"], vt.media_ranghi(Ps, ps["U"]), np.nan)
    m6 = vt.portafoglio(Pm, ps, sig)
    W7 = vq.pesi_banda(np.where(np.isfinite(sig), Pm, np.nan), ps["U"], sig)
    m7 = te.conto(W7, ps["R"], ps["F"], costo)
    m7.index = ps["lunedi"]
    f5 = te.conto(vq.pesi_banda(np.where(np.isfinite(sig), -se.funding_7(pan, lun), np.nan), ps["U"], sig), ps["R"], ps["F"], costo)
    f5.index = ps["lunedi"]
    fm = qd.combina({"F5": f5, "M7": m7})
    RIS.mkdir(exist_ok=True)
    m7.to_csv(RIS / "settimane_M7.csv.gz")
    fm.to_csv(RIS / "settimane_F5_M7.csv.gz")
    jb = ps["simboli"].index("BTCUSDT")
    btc = pd.Series(ps["R"][:, jb], index=ps["lunedi"])
    sr = prove_fino_alla_ventiquattresima()
    esami = {}
    for nome, df in (("M7", m7), ("F5 + M7", fm)):
        e = te.esame(df, btc, inizio=q.INIZIO, anni_pieni=q.ANNI_PIENI)
        esami[nome] = e
        sr.append(e["intero"]["sharpe"])
    for nome, df in (("M6", m6), ("F5", f5)):
        d = df[df.index >= q.INIZIO]
        esami[nome] = {"intero": te.numeri_settimana(d["netto"]), "giro_medio": float(d["giro"].mean()),
                       "spese_annue": float(d["spese"].mean() * 52)}
    for nome in ("M7", "F5 + M7"):
        e = esami[nome]
        i = e["intero"]
        e["sharpe_corretto"] = te.sharpe_corretto(i["sharpe"], i["settimane"], i["asimmetria"], i["curtosi"], sr, 52)
        e["prove_nel_conto"] = len(sr)
        e["esito"] = te.esito(e, e["sharpe_corretto"])
    d5, d7 = f5[f5.index >= q.INIZIO]["netto"], m7[m7.index >= q.INIZIO]["netto"]
    esami["correlazione_F5_M7"] = float(np.corrcoef(d5, d7.reindex(d5.index).fillna(0.0))[0, 1])
    (RIS / "esame.json").write_text(json.dumps(esami, ensure_ascii=False, indent=1), encoding="utf-8")
    righe = ["# Programma 6 — risultati della venticinquesima prova (M7: il modello con la banda; F5 + M7)", "",
             "Regole in `VENTICINQUESIMA.md` (scritte prima). Le 100 monete più scambiate, dal 3 gennaio 2022, dati corretti.", "",
             "| Variante | Rendimento/anno | Volatilità | Sharpe | Discesa massima | Intervallo (settimana) | Sharpe corretto | "
             "Anni positivi | Ultimo anno | Giro, spese l'anno | Esito |", "|---|---|---|---|---|---|---|---|---|---|---|"]
    for nome in ("M7", "F5 + M7"):
        e = esami[nome]
        i = e["intero"]
        anni = sum(1 for x in e["per_anno"].values() if x > 0)
        gs = f"{e['giro_medio']:.2f}, {100 * e['spese_annue']:.1f}%" if nome == "M7" else "—"
        righe.append(f"| {nome} | {100 * i['annuo']:+.1f}% | {100 * i['volatilita']:.1f}% | {i['sharpe']:.2f} | "
                     f"{100 * i['discesa_max']:.1f}% | {100 * e['boot']['basso']:+.2f}%; {100 * e['boot']['alto']:+.2f}% | "
                     f"{e['sharpe_corretto']:.2f} | {anni}/{len(e['per_anno'])} | {100 * e['ultimo_anno']:+.1f}% | {gs} | {e['esito']} |")
    for nome in ("M6", "F5"):
        e = esami[nome]
        righe.append(f"| {nome} (confronto, stessi anni) | {100 * e['intero']['annuo']:+.1f}% | {100 * e['intero']['volatilita']:.1f}% | "
                     f"{e['intero']['sharpe']:.2f} | {100 * e['intero']['discesa_max']:.1f}% | — | — | — | — | "
                     f"{e['giro_medio']:.2f}, {100 * e['spese_annue']:.1f}% | — |")
    for nome in ("M7", "F5 + M7"):
        righe += ["", f"**{nome}, per anno**: " + ", ".join(f"{a} {100 * v:+.1f}%" for a, v in esami[nome]["per_anno"].items())]
    righe += ["", f"Correlazione settimanale fra F5 e M7: {esami['correlazione_F5_M7']:.2f}. Sharpe corretto con {len(sr)} prove."]
    testo = "\n".join(righe) + "\n"
    (QUI / "RISULTATI_VENTICINQUESIMA.md").write_text(testo, encoding="utf-8")
    log(testo)
    return esami


if __name__ == "__main__":
    esegui(log=lambda x: print(x, flush=True))
    print("VENTICINQUESIMA FINITA", flush=True)
