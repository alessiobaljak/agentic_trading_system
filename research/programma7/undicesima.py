"""Programma 7, undicesima prova (UNDICESIMA.md): G9, l'inversione di un giorno fra le monete 101-200 con gli ordini limite.

Uso: python3 -m research.programma7.undicesima
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from research.programma6 import asticella as ast
from research.programma6 import cinquantaseiesima as cs
from research.programma6 import ottava as ot
from research.programma6 import seconda as sc
from research.programma6 import sesta as se
from research.programma6 import settima as st
from research.programma6 import terza as te
from research.programma6.motore import TAKER
from research.programma7 import prima as pr

QUI = Path(__file__).parent
RIS = QUI / "risultati_undicesima"
QUOTA = 0.20


def pesi_inversione(ieri: np.ndarray, U: np.ndarray, sig: np.ndarray) -> np.ndarray:
    """(giorni × monete) long il 20% sceso di piu' ieri, short il 20% salito di piu', pesi 1/volatilita', ogni lato al 100%."""
    W = np.zeros_like(ieri)
    for d in range(ieri.shape[0]):
        idx = np.flatnonzero(U[d] & np.isfinite(ieri[d]) & np.isfinite(sig[d]) & (sig[d] > 0))
        if len(idx) < te.MIN_MONETE:
            continue
        p = pd.Series(ieri[d, idx]).rank(pct=True).to_numpy()
        for lato, segno in ((idx[p <= QUOTA], 1.0), (idx[p > 1 - QUOTA], -1.0)):
            if len(lato):
                inv = 1.0 / sig[d, lato]
                W[d, lato] = segno * inv / inv.sum()
    return W


def esegui(log=print) -> dict:
    pan = sc.pannello()
    ps = te.pannello_settimane(pan, log=lambda x: None, da=100, a=200, indicatori_si=False)
    giorni = np.arange(se.INIZIO, pr.FINE, dtype=np.int64)
    idx = giorni - pan["t0"]
    Ud = pr.universo_del_giorno(giorni, ps["lunedi"], ps["U"])
    sig = ot.sigma_30(pan, idx)
    r_tutti = sc.rendimenti(pan).astype(float)
    r_tutti[~np.isfinite(pan["close"])] = np.nan
    ieri = r_tutti[idx - 1]
    W = pesi_inversione(ieri, Ud, sig)
    R, F = sc.rendimenti(pan)[idx], np.nan_to_num(pan["funding"][idx])
    costo = np.full(len(pan["simboli"]), TAKER + st.SCARTO)
    mercato = te.conto(W, R, F, costo)
    limite = mercato.copy()
    spese, n_tot, n_lim, n_senza = cs.spese_a_limite(W, R, giorni, pan["simboli"], costo)
    limite["spese"] = spese
    limite["netto"] = limite["lordo"] - limite["spese"] - limite["funding"]
    limite["netto_doppio"] = limite["lordo"] - 2 * limite["spese"] - limite["funding"]
    sett, sett_m = pr.per_settimana(limite, giorni), pr.per_settimana(mercato, giorni)
    RIS.mkdir(exist_ok=True)
    sett.to_csv(RIS / "settimane_G9.csv.gz")
    pb = te.pannello_settimane(pan, log=lambda x: None, indicatori_si=False)
    btc = pd.Series(pb["R"][:, pb["simboli"].index("BTCUSDT")], index=pb["lunedi"])
    e = te.esame(sett, btc, inizio=se.INIZIO, anni_pieni=se.ANNI_PIENI)
    em = te.esame(sett_m, btc, inizio=se.INIZIO, anni_pieni=se.ANNI_PIENI)
    e["a_mercato"] = {k: em["intero"][k] for k in ("sharpe", "annuo")} | {"spese_annue": em["spese_annue"]}
    e["lordo_annuo"] = float(sett["lordo"].mean() * 52)
    e["ordini"] = {"variazioni": n_tot, "eseguite_con_il_limite": n_lim, "senza_candele_a_1_ora": n_senza}
    rivisto = ast.corretto_rivisto({**ast.serie_nuove(), "67 G9": sett["netto"]}, {"67 G9": e["intero"]})
    rr = rivisto["candidate"]["67 G9"]
    e["sharpe_corretto"], e["t"], e["gruppi"] = rr["corretto_con_aggiunta"], rr["t"], rivisto["gruppi"]
    e["esito"] = te.esito(e, e["sharpe_corretto"])
    (RIS / "esame.json").write_text(json.dumps(e, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    i, o, m = e["intero"], e["ordini"], e["a_mercato"]
    testo = "\n".join([
        "# Programma 7 — risultati dell'undicesima prova (G9: l'inversione di un giorno fra le 101-200, a limite)", "",
        "Regole in `UNDICESIMA.md` (scritte prima).", "",
        f"* Variazioni {o['variazioni']}: eseguite a limite {o['eseguite_con_il_limite']} "
        f"({100 * o['eseguite_con_il_limite'] / max(1, o['variazioni'] - o['senza_candele_a_1_ora']):.0f}% di quelle con le candele).",
        f"* Prima dei costi: {100 * e['lordo_annuo']:+.1f}% l'anno.",
        f"* G9 a limite: Sharpe {i['sharpe']:.2f}, {100 * i['annuo']:+.1f}% l'anno, volatilità {100 * i['volatilita']:.1f}%, discesa "
        f"{100 * i['discesa_max']:.1f}%; spese {100 * e['spese_annue']:.1f}% l'anno (giro medio a settimana {e['giro_medio']:.1f}).",
        f"* Tutto a mercato: Sharpe {m['sharpe']:.2f}, {100 * m['annuo']:+.1f}% l'anno, spese {100 * m['spese_annue']:.1f}%.",
        "* Per anno: " + ", ".join(f"{a} {100 * v:+.1f}%" for a, v in e["per_anno"].items()) + ".",
        f"* Sharpe corretto {e['sharpe_corretto']:.2f} ({e['gruppi']} gruppi); t {e['t']:.2f}.", "",
        f"**Esito: {e['esito']}**"]) + "\n"
    (QUI / "RISULTATI_UNDICESIMA.md").write_text(testo, encoding="utf-8")
    log(testo)
    return e


if __name__ == "__main__":
    esegui(log=lambda x: print(x, flush=True))
    print("UNDICESIMA FINITA", flush=True)
