"""Programma 7, ventiduesima prova (VENTIDUESIMA.md): G20, il modello ad alberi deciso ogni giorno (M3, `programma6/sedicesima`)
con la media dei ranghi di cinque semi (come M6) e gli ordini limite sulle variazioni di peso (come G1). Dal 3 gennaio 2022.

Uso: python3 -m research.programma7.ventiduesima
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from research.programma6 import asticella as ast
from research.programma6 import cinquantaseiesima as cs
from research.programma6 import quattordicesima as q
from research.programma6 import seconda as sc
from research.programma6 import sedicesima as m3
from research.programma6 import terza as te
from research.programma6 import ventitreesima as vt
from research.programma7 import prima as pr

QUI = Path(__file__).parent
RIS = QUI / "risultati_ventiduesima"
P6 = QUI.parent / "programma6"
INIZIO, FINE = q.INIZIO, pr.FINE
SEMI = vt.SEMI
M3_SHARPE, M3_SPESE = 0.95, 0.238                      # RISULTATI_SEDICESIMA.md, per il confronto


def previsioni_seme(seme: int, X, Y, U, giorni, log=print) -> np.ndarray:
    """Le previsioni giornaliere di M3 con il seme dato (lo stesso trucco di `ventitreesima.previsioni_seme`)."""
    from sklearn.ensemble import HistGradientBoostingRegressor
    originale = q._modello
    q._modello = lambda tipo: HistGradientBoostingRegressor(
        max_iter=300, learning_rate=0.05, max_leaf_nodes=15, min_samples_leaf=200, l2_regularization=1.0, random_state=seme)
    try:
        return m3.previsioni(X, Y, U, giorni, log)
    finally:
        q._modello = originale


def pesi_operativi(Pm: np.ndarray, U: np.ndarray, sig: np.ndarray, pan: dict, colonne: np.ndarray) -> np.ndarray:
    """I pesi della banda su tutte le colonne del pannello, spostati di un giorno (la decisione di t vale per t + 1), senza
    posizioni dove manca la candela del giorno dopo."""
    W = np.zeros(pan["close"].shape)
    W[:, colonne] = m3.pesi_isteresi(Pm, U, sig)
    domani = np.vstack([np.isfinite(pan["open"][1:]), np.zeros((1, W.shape[1]), bool)])
    W = np.where(domani, W, 0.0)
    return np.vstack([np.zeros((1, W.shape[1])), W[:-1]])


def esegui(log=print) -> dict:
    pan = sc.pannello()
    ps = te.pannello_settimane(pan, log=lambda x: None, indicatori_si=False)
    Ud = m3.universo_giornaliero(pan, ps)
    colonne = np.flatnonzero(Ud.any(axis=0))
    log(f"[ventiduesima] {len(colonne)} monete passate dall'universo")
    X, nomi, Y, U = m3.tabella(pan, Ud, colonne)
    giorni_tutti = np.arange(X.shape[0]) + pan["t0"]
    Ps = []
    for s in SEMI:
        Ps.append(previsioni_seme(s, X, Y, U, giorni_tutti, log))
        log(f"[ventiduesima] seme {s} fatto")
    with np.errstate(all="ignore"):
        Pm = np.where(U, vt.media_ranghi(Ps, U), np.nan)
    Wop = pesi_operativi(Pm, U, m3.sigma_giornaliera(pan, colonne), pan, colonne)
    giorni = np.arange(INIZIO, FINE, dtype=np.int64)
    idx = giorni - pan["t0"]
    W = Wop[idx]
    R = sc.rendimenti(pan)[idx]
    F = np.nan_to_num(pan["funding"][idx])
    costo = sc.costi_moneta(pan["simboli"])
    mercato = te.conto(W, R, F, costo)
    spese, n_tot, n_lim, n_senza = cs.spese_a_limite(W, R, giorni, pan["simboli"], costo)
    limite = mercato.copy()
    limite["spese"] = spese
    limite["netto"] = limite["lordo"] - limite["spese"] - limite["funding"]
    limite["netto_doppio"] = limite["lordo"] - 2 * limite["spese"] - limite["funding"]
    sett_lim, sett_mer = pr.per_settimana(limite, giorni), pr.per_settimana(mercato, giorni)
    RIS.mkdir(exist_ok=True)
    sett_lim.to_csv(RIS / "settimane_G20.csv.gz")
    sett_mer.to_csv(RIS / "settimane_G20_mercato.csv.gz")
    limite.assign(giorno=giorni).to_csv(RIS / "giorni_G20.csv.gz", index=False)
    btc = pd.Series(ps["R"][:, ps["simboli"].index("BTCUSDT")], index=ps["lunedi"])
    anni = (2022, 2023, 2024, 2025)
    e = te.esame(sett_lim, btc, inizio=INIZIO, anni_pieni=anni)
    em = te.esame(sett_mer, btc, inizio=INIZIO, anni_pieni=anni)
    e["a_mercato"] = {k: em["intero"][k] for k in ("sharpe", "annuo", "discesa_max")} | {"spese_annue": em["spese_annue"]}
    e["ordini"] = {"variazioni": n_tot, "eseguite_con_il_limite": n_lim, "senza_candele_a_1_ora": n_senza}
    e["movimenti"] = pr.movimenti(W)
    confronti = {}
    for nome, f in (("G1", QUI / "risultati_prima" / "settimane_G1.csv.gz"), ("M7", P6 / "risultati_venticinquesima" / "settimane_M7.csv.gz")):
        if f.exists():
            s = pd.read_csv(f, index_col=0)
            c = sett_lim.index.intersection(s.index)
            ex = te.esame(s.loc[c], btc, inizio=INIZIO, anni_pieni=anni)
            confronti[nome] = {"sharpe": ex["intero"]["sharpe"], "annuo": ex["intero"]["annuo"],
                               "correlazione": float(np.corrcoef(sett_lim.loc[c, "netto"], s.loc[c, "netto"])[0, 1])}
    e["confronti"] = confronti
    rivisto = ast.corretto_rivisto({**ast.serie_nuove(), "84 G20": sett_lim["netto"]}, {"84 G20": e["intero"]})
    r = rivisto["candidate"]["84 G20"]
    e["sharpe_corretto"], e["t"], e["gruppi"] = r["corretto_con_aggiunta"], r["t"], rivisto["gruppi"]
    e["esito"] = te.esito(e, e["sharpe_corretto"])
    e["regola_del_proprietario"] = bool(e["sharpe_corretto"] >= 0.90 and all(v > 0 for v in e["per_anno"].values()) and e["t"] > 3)
    (RIS / "esame.json").write_text(json.dumps(e, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    i, o, mv, m = e["intero"], e["ordini"], e["movimenti"], e["a_mercato"]
    testo = "\n".join([
        "# Programma 7 — risultati della ventiduesima prova (G20: il modello ad alberi deciso ogni giorno, cinque semi, ordini limite)", "",
        "Regole in `VENTIDUESIMA.md` (scritte prima). Dal 3 gennaio 2022 al 5 ottobre 2026; riallenato ogni 28 giorni solo sul passato.", "",
        f"* Operazioni: {mv['entrate_al_giorno']:.1f} entrate e {mv['uscite_al_giorno']:.1f} uscite al giorno in media; una posizione dura "
        f"in media {mv['durata_media_giorni']:.1f} giorni.",
        f"* Variazioni di peso {o['variazioni']}: eseguite con il limite {o['eseguite_con_il_limite']} "
        f"({100 * o['eseguite_con_il_limite'] / max(1, o['variazioni'] - o['senza_candele_a_1_ora']):.0f}% di quelle con le candele).",
        f"* **G20 con gli ordini limite: Sharpe {i['sharpe']:.2f}**, {100 * i['annuo']:+.1f}% l'anno, volatilità {100 * i['volatilita']:.1f}%, "
        f"discesa {100 * i['discesa_max']:.1f}%; spese {100 * e['spese_annue']:.1f}% l'anno.",
        f"* Tutto a mercato: Sharpe {m['sharpe']:.2f}, {100 * m['annuo']:+.1f}% l'anno, spese {100 * m['spese_annue']:.1f}% "
        f"(M3 nella prova 16: Sharpe {M3_SHARPE:.2f}, spese {100 * M3_SPESE:.1f}%).",
        "* Per anno: " + ", ".join(f"{a} {100 * v:+.1f}%" for a, v in e["per_anno"].items()) + ".",
        "* Confronti sulle stesse settimane: " + "; ".join(f"{n} Sharpe {c['sharpe']:.2f} ({100 * c['annuo']:+.1f}% l'anno), correlazione "
                                                            f"{c['correlazione']:.2f}" for n, c in confronti.items()) + ".",
        f"* Sharpe corretto con l'aggiunta {e['sharpe_corretto']:.2f} ({e['gruppi']} gruppi); t dello Sharpe {e['t']:.2f}; regola del "
        f"proprietario del 24 ottobre: {'sì' if e['regola_del_proprietario'] else 'no'}.", "",
        f"**Esito: {e['esito']}**"]) + "\n"
    (QUI / "RISULTATI_VENTIDUESIMA.md").write_text(testo, encoding="utf-8")
    log(testo)
    return e


if __name__ == "__main__":
    esegui(log=lambda x: print(x, flush=True))
    print("VENTIDUESIMA FINITA", flush=True)
