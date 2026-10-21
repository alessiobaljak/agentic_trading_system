"""Programma 6, ventinovesima prova (VENTINOVESIMA.md): M8, il modello di M7 (cinque semi, media dei ranghi, banda) allenato
sul rendimento della settimana meno la media dell'universo, tagliato ai percentili 1 e 99 di ogni settimana, invece del rango.

Uso: python3 -m research.programma6.ventinovesima
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from research.programma6 import ottava as ot
from research.programma6 import quattordicesima as q
from research.programma6 import seconda as sc
from research.programma6 import terza as te
from research.programma6 import venticinquesima as v25
from research.programma6 import ventiquattresima as vq
from research.programma6 import ventitreesima as vt

QUI = Path(__file__).parent
RIS = QUI / "risultati_ventinovesima"


def rendimento_in_piu(R: np.ndarray, U: np.ndarray) -> np.ndarray:
    """Settimane × monete: rendimento meno la media delle monete dell'universo, tagliato ai percentili 1 e 99 della settimana."""
    out = np.full(R.shape, np.nan)
    for w in range(R.shape[0]):
        idx = np.flatnonzero(U[w] & np.isfinite(R[w]))
        if len(idx) < 2:
            continue
        x = R[w, idx] - R[w, idx].mean()
        lo, hi = np.percentile(x, [1, 99])
        out[w, idx] = np.clip(x, lo, hi)
    return out


def esegui(log=print) -> dict:
    pan = sc.pannello()
    ps = te.pannello_settimane(pan, log=lambda x: None)
    sig = ot.sigma_30(pan, ps["lunedi"] - pan["t0"])
    costo = sc.costi_moneta(ps["simboli"])
    X, _, _ = q.tabella_settimanale(pan, ps, ps["U"])
    Y = rendimento_in_piu(ps["R"], ps["U"])
    Ps = []
    for s in vt.SEMI:
        Ps.append(vt.previsioni_seme(s, X, Y, ps["U"], ps["lunedi"]))
        log(f"[ventinovesima] seme {s} fatto")
    with np.errstate(all="ignore"):
        Pm = np.where(ps["U"], vt.media_ranghi(Ps, ps["U"]), np.nan)
    m8 = te.conto(vq.pesi_banda(np.where(np.isfinite(sig), Pm, np.nan), ps["U"], sig), ps["R"], ps["F"], costo)
    m8.index = ps["lunedi"]
    RIS.mkdir(exist_ok=True)
    m8.to_csv(RIS / "settimane_M8.csv.gz")
    jb = ps["simboli"].index("BTCUSDT")
    btc = pd.Series(ps["R"][:, jb], index=ps["lunedi"])
    e = te.esame(m8, btc, inizio=q.INIZIO, anni_pieni=q.ANNI_PIENI)
    sr = v25.prove_fino_alla_ventiquattresima()
    e25 = json.loads((QUI / "risultati_venticinquesima" / "esame.json").read_text())
    e28 = json.loads((QUI / "risultati_ventottesima" / "esame.json").read_text())
    sr += [e25["M7"]["intero"]["sharpe"], e25["F5 + M7"]["intero"]["sharpe"], e28["K2"]["intero"]["sharpe"],
           e28["F5 + M7 + K2"]["intero"]["sharpe"], e["intero"]["sharpe"]]
    i = e["intero"]
    e["sharpe_corretto"] = te.sharpe_corretto(i["sharpe"], i["settimane"], i["asimmetria"], i["curtosi"], sr, 52)
    e["prove_nel_conto"] = len(sr)
    e["esito"] = te.esito(e, e["sharpe_corretto"])
    m7 = pd.read_csv(QUI / "risultati_venticinquesima" / "settimane_M7.csv.gz", index_col=0)
    d8, d7 = m8[m8.index >= q.INIZIO]["netto"], m7[m7.index >= q.INIZIO]["netto"]
    c = d8.index.intersection(d7.index)
    e["M7_stessi_anni"] = te.numeri_settimana(d7)
    e["correlazione_M7"] = float(np.corrcoef(d8.loc[c], d7.loc[c])[0, 1])
    (RIS / "esame.json").write_text(json.dumps(e, ensure_ascii=False, indent=1), encoding="utf-8")
    pa = e["per_anno"]
    testo = "\n".join([
        "# Programma 6 — risultati della ventinovesima prova (M8: il modello con l'obiettivo del rendimento in più)", "",
        "Regole in `VENTINOVESIMA.md` (scritte prima). Le 100 monete più scambiate, dal 3 gennaio 2022, dati corretti.", "",
        f"* {100 * i['annuo']:+.1f}% l'anno, volatilità {100 * i['volatilita']:.1f}%, **Sharpe {i['sharpe']:.2f}**, discesa massima "
        f"{100 * i['discesa_max']:.1f}%; media settimanale {100 * e['boot']['media']:+.3f}% (intervallo "
        f"{100 * e['boot']['basso']:+.3f}; {100 * e['boot']['alto']:+.3f}).",
        "* Per anno: " + ", ".join(f"{a} {100 * v:+.1f}%" for a, v in pa.items()) + f"; ultimo anno {100 * e['ultimo_anno']:+.1f}%.",
        f"* M7 sugli stessi anni: Sharpe {e['M7_stessi_anni']['sharpe']:.2f}; correlazione con M7 {e['correlazione_M7']:.2f}.",
        f"* Sharpe corretto {e['sharpe_corretto']:.2f} con {e['prove_nel_conto']} prove.", "",
        f"**Esito: {e['esito']}**"]) + "\n"
    (QUI / "RISULTATI_VENTINOVESIMA.md").write_text(testo, encoding="utf-8")
    log(testo)
    return e


if __name__ == "__main__":
    esegui(log=lambda x: print(x, flush=True))
    print("VENTINOVESIMA FINITA", flush=True)
