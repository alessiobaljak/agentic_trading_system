"""Programma 7, ventitreesima prova (VENTITREESIMA.md): G21, l'inversione di un giorno fra le monete 101-200 con meno giro: solo
il 10% per lato, tre fette da un terzo del capitale tenute tre giorni, ordini limite (come la prova 67, `undicesima`).

Uso: python3 -m research.programma7.ventitreesima
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
RIS = QUI / "risultati_ventitreesima"
QUOTA, FETTE = 0.10, 3
G9 = {"lordo": 0.291, "spese": 0.612, "netto": -0.384}            # RISULTATI_UNDICESIMA.md, per il confronto


def pesi_estremi(ieri: np.ndarray, U: np.ndarray, sig: np.ndarray, quota: float = QUOTA) -> np.ndarray:
    """(giorni × monete) la fetta del giorno: long il ``quota`` sceso di piu' ieri, short il ``quota`` salito di piu', pesi
    1/volatilita', ogni lato al 100%."""
    W = np.zeros_like(ieri)
    for d in range(ieri.shape[0]):
        idx = np.flatnonzero(U[d] & np.isfinite(ieri[d]) & np.isfinite(sig[d]) & (sig[d] > 0))
        if len(idx) < te.MIN_MONETE:
            continue
        p = pd.Series(ieri[d, idx]).rank(pct=True).to_numpy()
        for lato, segno in ((idx[p <= quota], 1.0), (idx[p > 1 - quota], -1.0)):
            if len(lato):
                inv = 1.0 / sig[d, lato]
                W[d, lato] = segno * inv / inv.sum()
    return W


def pesi_a_fette(Wf: np.ndarray, fette: int = FETTE) -> np.ndarray:
    """Il peso operativo del giorno d: la media delle fette aperte nei giorni d, d-1, ..., d-fette+1 (ognuna vale 1/fette)."""
    W = np.zeros_like(Wf)
    for k in range(fette):
        W[k:] += Wf[: Wf.shape[0] - k] if k else Wf
    return W / fette


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
    Wf = pesi_estremi(ieri, Ud, sig)
    # una fetta aperta su una moneta uscita dall'universo o senza candela resta ferma fino alla sua chiusura naturale, salvo che
    # manchi la candela: allora si azzera (la moneta e' stata tolta dal listino)
    W = pesi_a_fette(Wf)
    W = np.where(np.isfinite(pan["open"][idx]), W, 0.0)
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
    sett.to_csv(RIS / "settimane_G21.csv.gz")
    pb = te.pannello_settimane(pan, log=lambda x: None, indicatori_si=False)
    btc = pd.Series(pb["R"][:, pb["simboli"].index("BTCUSDT")], index=pb["lunedi"])
    e = te.esame(sett, btc, inizio=se.INIZIO, anni_pieni=se.ANNI_PIENI)
    em = te.esame(sett_m, btc, inizio=se.INIZIO, anni_pieni=se.ANNI_PIENI)
    e["a_mercato"] = {k: em["intero"][k] for k in ("sharpe", "annuo")} | {"spese_annue": em["spese_annue"]}
    e["lordo_annuo"] = float(sett["lordo"].mean() * 52)
    e["ordini"] = {"variazioni": n_tot, "eseguite_con_il_limite": n_lim, "senza_candele_a_1_ora": n_senza}
    e["movimenti"] = pr.movimenti(W)
    rivisto = ast.corretto_rivisto({**ast.serie_nuove(), "85 G21": sett["netto"]}, {"85 G21": e["intero"]})
    rr = rivisto["candidate"]["85 G21"]
    e["sharpe_corretto"], e["t"], e["gruppi"] = rr["corretto_con_aggiunta"], rr["t"], rivisto["gruppi"]
    e["esito"] = te.esito(e, e["sharpe_corretto"])
    e["regola_del_proprietario"] = bool(e["sharpe_corretto"] >= 0.90 and all(v > 0 for v in e["per_anno"].values()) and e["t"] > 3)
    (RIS / "esame.json").write_text(json.dumps(e, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    i, o, m, mv = e["intero"], e["ordini"], e["a_mercato"], e["movimenti"]
    testo = "\n".join([
        "# Programma 7 — risultati della ventitreesima prova (G21: l'inversione fra le 101-200 con meno giro)", "",
        "Regole in `VENTITREESIMA.md` (scritte prima). Dal 4 gennaio 2021 al 4 ottobre 2026.", "",
        f"* Variazioni {o['variazioni']}: eseguite a limite {o['eseguite_con_il_limite']} "
        f"({100 * o['eseguite_con_il_limite'] / max(1, o['variazioni'] - o['senza_candele_a_1_ora']):.0f}% di quelle con le candele); "
        f"giro medio a settimana {e['giro_medio']:.1f} (la prova 67: 17,5); {mv['entrate_al_giorno']:.1f} entrate al giorno, una posizione "
        f"dura {mv['durata_media_giorni']:.1f} giorni.",
        f"* Prima dei costi: {100 * e['lordo_annuo']:+.1f}% l'anno (la prova 67: {100 * G9['lordo']:+.1f}%).",
        f"* **G21 a limite: Sharpe {i['sharpe']:.2f}**, {100 * i['annuo']:+.1f}% l'anno, volatilità {100 * i['volatilita']:.1f}%, discesa "
        f"{100 * i['discesa_max']:.1f}%; spese {100 * e['spese_annue']:.1f}% l'anno (la prova 67: {100 * G9['spese']:.1f}%, netto "
        f"{100 * G9['netto']:+.1f}%).",
        f"* Tutto a mercato: Sharpe {m['sharpe']:.2f}, {100 * m['annuo']:+.1f}% l'anno, spese {100 * m['spese_annue']:.1f}%.",
        "* Per anno: " + ", ".join(f"{a} {100 * v:+.1f}%" for a, v in e["per_anno"].items()) + ".",
        f"* Sharpe corretto {e['sharpe_corretto']:.2f} ({e['gruppi']} gruppi); t {e['t']:.2f}; regola del proprietario del 24 ottobre: "
        f"{'sì' if e['regola_del_proprietario'] else 'no'}.", "",
        f"**Esito: {e['esito']}**"]) + "\n"
    (QUI / "RISULTATI_VENTITREESIMA.md").write_text(testo, encoding="utf-8")
    log(testo)
    return e


if __name__ == "__main__":
    esegui(log=lambda x: print(x, flush=True))
    print("VENTITREESIMA FINITA", flush=True)
