"""Programma 6, cinquantacinquesima prova (CINQUANTACINQUESIMA.md): C3, un solo punteggio per moneta dalla media dei ranghi
di F5 (−funding dei 7 giorni), K1 e M7 (5 semi), con la banda di F5. Dal 2022.

Uso: python3 -m research.programma6.cinquantacinquesima
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from research.programma6 import asticella as ast
from research.programma6 import dodicesima as do
from research.programma6 import ottava as ot
from research.programma6 import quattordicesima as q
from research.programma6 import seconda as sc
from research.programma6 import sesta as se
from research.programma6 import terza as te
from research.programma6 import undicesima as un
from research.programma6 import ventiquattresima as vq
from research.programma6 import ventitreesima as vt

QUI = Path(__file__).parent
RIS = QUI / "risultati_cinquantacinquesima"


def punteggio(f: np.ndarray, k: np.ndarray, m: np.ndarray, U: np.ndarray) -> np.ndarray:
    """La media dei ranghi disponibili (fra −0,5 e +0,5), con il funding sempre presente e almeno 2 su 3."""
    Z = np.stack([f, k, m], axis=2)
    ok = np.isfinite(Z)
    R = te.ranghi(np.where(ok, Z, np.nan), U)
    n = ok.sum(axis=2)
    with np.errstate(all="ignore"):
        s = np.where(ok, R, 0.0).sum(axis=2) / n
    return np.where(ok[:, :, 0] & (n >= 2) & U, s, np.nan)


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
        log(f"[cinquantacinquesima] seme {s} fatto")
    with np.errstate(all="ignore"):
        Pm = np.where(ps["U"], vt.media_ranghi(Ps, ps["U"]), np.nan)
    k = do.segnale_k1(pan, ps, un.pannello_metrics(pan))
    c = punteggio(-se.funding_7(pan, lun), k, Pm, ps["U"])
    W = vq.pesi_banda(np.where(np.isfinite(sig), c, np.nan), ps["U"], sig)
    df = te.conto(W, ps["R"], ps["F"], costo)
    df.index = ps["lunedi"]
    RIS.mkdir(exist_ok=True)
    df.to_csv(RIS / "settimane_C3.csv.gz")
    btc = pd.Series(ps["R"][:, ps["simboli"].index("BTCUSDT")], index=ps["lunedi"])
    e = te.esame(df, btc, inizio=q.INIZIO, anni_pieni=q.ANNI_PIENI)
    tre = pd.read_csv(QUI / "risultati_ventottesima" / "settimane_F5_M7_K2.csv.gz", index_col=0)
    e3 = te.esame(tre, btc, inizio=q.INIZIO, anni_pieni=q.ANNI_PIENI)
    e["tre_portafogli"] = {x: e3["intero"][x] for x in ("sharpe", "annuo", "volatilita", "discesa_max")}
    f5 = pd.read_csv(QUI / "risultati_ventiquattresima" / "settimane_F5.csv.gz", index_col=0)["netto"]
    comuni = df.index[df.index >= q.INIZIO].intersection(f5.index)
    e["correlazione_F5"] = float(np.corrcoef(df.loc[comuni, "netto"], f5.loc[comuni])[0, 1])
    nuove = {f"49 {x}": pd.read_csv(QUI / "risultati_quarantanovesima" / f"settimane_{x}.csv.gz", index_col=0)["netto"] for x in ("X1", "X2")}
    for n_, f_ in (("51 F7", "risultati_cinquantunesima/settimane_F7.csv.gz"), ("52 B1", "risultati_cinquantaduesima/settimane_B1.csv.gz"),
                   ("53 F8", "risultati_cinquantatreesima/settimane_F8.csv.gz")):
        nuove[n_] = pd.read_csv(QUI / f_, index_col=0)["netto"]
    z = QUI / "risultati_cinquantaquattresima"
    for f_ in sorted(z.glob("settimane_*.csv.gz")) if z.exists() else []:
        nuove[f"54 {f_.name[len('settimane_'):-len('.csv.gz')]}"] = pd.read_csv(f_, index_col=0).iloc[:, 0]
    nuove["55 C3"] = df["netto"]
    r = ast.corretto_rivisto(nuove, {"55 C3": e["intero"]})
    cc = r["candidate"]["55 C3"]
    e["sharpe_corretto"], e["t"], e["gruppo"], e["gruppi"] = cc["corretto"], cc["t"], cc["gruppo"], r["gruppi"]
    e["esito"] = te.esito(e, e["sharpe_corretto"])
    (RIS / "esame.json").write_text(json.dumps(e, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    i, t3 = e["intero"], e["tre_portafogli"]
    testo = "\n".join([
        "# Programma 6 — risultati della cinquantacinquesima prova (C3: un solo punteggio da F5, K2 e M7)", "",
        "Regole in `CINQUANTACINQUESIMA.md` (scritte prima).", "",
        f"* C3 dal 2022: Sharpe {i['sharpe']:.2f}, {100 * i['annuo']:+.1f}% l'anno, volatilità {100 * i['volatilita']:.1f}%, discesa "
        f"{100 * i['discesa_max']:.1f}%; spese {100 * e['spese_annue']:.1f}% l'anno (giro medio {e['giro_medio']:.2f}); correlazione con "
        f"F5 {e['correlazione_F5']:.2f}.",
        f"* F5 + M7 + K2 a portafogli sulle stesse settimane: Sharpe {t3['sharpe']:.2f}, {100 * t3['annuo']:+.1f}% l'anno, discesa "
        f"{100 * t3['discesa_max']:.1f}%.",
        "* Per anno: " + ", ".join(f"{a} {100 * v:+.1f}%" for a, v in e["per_anno"].items()) + ".",
        f"* Sharpe corretto rivisto {e['sharpe_corretto']:.2f} ({e['gruppi']} gruppi); t dello Sharpe {e['t']:.2f}; gruppo: "
        + ", ".join(e["gruppo"]) + ".", "", f"**Esito: {e['esito']}**"]) + "\n"
    (QUI / "RISULTATI_CINQUANTACINQUESIMA.md").write_text(testo, encoding="utf-8")
    log(testo)
    return e


if __name__ == "__main__":
    esegui(log=lambda x: print(x, flush=True))
    print("CINQUANTACINQUESIMA FINITA", flush=True)
