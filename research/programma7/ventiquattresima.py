"""Programma 7, ventiquattresima prova (VENTIQUATTRESIMA.md): F5N, F5 neutra al mercato: i due lati scalati perche' la somma dei
beta (stimati sui 90 giorni prima del lunedi' verso la media dell'universo) sia zero; con il controllo del peso fisso 120/80.

Uso: python3 -m research.programma7.ventiquattresima
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from research.programma6 import asticella as ast
from research.programma6 import ottava as ot
from research.programma6 import seconda as sc
from research.programma6 import sesta as se
from research.programma6 import terza as te
from research.programma6 import ventiquattresima as vq

QUI = Path(__file__).parent
RIS = QUI / "risultati_ventiquattresima"
P6 = QUI.parent / "programma6"
GIORNI_BETA, MIN_BETA = 90, 45
LIMITI = (0.5, 1.5)
FISSO = (1.2, 0.8)


def beta_delle_monete(pan: dict, U: np.ndarray, lun_idx: np.ndarray) -> np.ndarray:
    """(settimane × monete) la pendenza dei rendimenti giornalieri della moneta sulla media giornaliera dell'universo della
    settimana, sui 90 giorni prima del lunedi' (almeno 45 con tutti e due i dati); 1 dove manca."""
    C = pan["close"]
    with np.errstate(all="ignore"):
        r = np.vstack([np.full((1, C.shape[1]), np.nan), C[1:] / C[:-1] - 1])
    out = np.ones((len(lun_idx), C.shape[1]))
    for k, m in enumerate(lun_idx):
        a, b = max(0, m - GIORNI_BETA), m
        if b - a < MIN_BETA:
            continue
        blocco = r[a:b]
        with np.errstate(all="ignore"):
            mercato = np.nanmean(np.where(U[k][None, :], blocco, np.nan), axis=1)
        ok_m = np.isfinite(mercato)
        for j in np.flatnonzero(U[k]):
            ok = ok_m & np.isfinite(blocco[:, j])
            if ok.sum() < MIN_BETA:
                continue
            x, y = mercato[ok], blocco[ok, j]
            vx = x.var()
            if vx > 0:
                out[k, j] = float(np.cov(x, y, ddof=0)[0, 1] / vx)
    return out


def scala_neutra(W: np.ndarray, beta: np.ndarray) -> tuple:
    """I pesi di F5 con i due lati scalati (long × a, short × b) perche' la somma dei beta pesati sia zero, con l'esposizione
    lorda al 200%; a e b entro LIMITI. Restituisce (pesi, a, b, βL, βS) per settimana."""
    WN = W.copy()
    n = W.shape[0]
    a_, b_, bl_, bs_ = np.ones(n), np.ones(n), np.full(n, np.nan), np.full(n, np.nan)
    for k in range(n):
        lato_l, lato_s = W[k] > 0, W[k] < 0
        if not lato_l.any() or not lato_s.any():
            continue
        bl = float((W[k, lato_l] * beta[k, lato_l]).sum() / W[k, lato_l].sum())
        bs = float((-W[k, lato_s] * beta[k, lato_s]).sum() / (-W[k, lato_s]).sum())
        bl_[k], bs_[k] = bl, bs
        if bl + bs <= 0:
            continue
        a = float(np.clip(2 * bs / (bl + bs), *LIMITI))
        b = float(np.clip(2 * bl / (bl + bs), *LIMITI))
        a_[k], b_[k] = a, b
        WN[k, lato_l] *= a
        WN[k, lato_s] *= b
    return WN, a_, b_, bl_, bs_


def esegui(log=print) -> dict:
    pan = sc.pannello()
    ps = te.pannello_settimane(pan, log=lambda x: None, indicatori_si=False)
    lun = ps["lunedi"] - pan["t0"]
    sig = ot.sigma_30(pan, lun)
    costo = sc.costi_moneta(ps["simboli"])
    W = vq.pesi_banda(np.where(np.isfinite(sig), -se.funding_7(pan, lun), np.nan), ps["U"], sig)
    beta = beta_delle_monete(pan, ps["U"], lun)
    WN, a, b, bl, bs = scala_neutra(W, beta)
    WF = np.where(W > 0, W * FISSO[0], W * FISSO[1])
    conti = {}
    for nome, Wx in (("F5", W), ("F5N", WN), ("F5 120/80", WF)):
        d = te.conto(Wx, ps["R"], ps["F"], costo)
        d.index = ps["lunedi"]
        conti[nome] = d
    RIS.mkdir(exist_ok=True)
    for nome, d in conti.items():
        d.to_csv(RIS / f"settimane_{nome.replace(' ', '_').replace('/', '-')}.csv.gz")
    btc = pd.Series(ps["R"][:, ps["simboli"].index("BTCUSDT")], index=ps["lunedi"])
    out = {n: te.esame(d, btc, inizio=se.INIZIO, anni_pieni=se.ANNI_PIENI) for n, d in conti.items()}
    dentro = ps["lunedi"] >= se.INIZIO
    out["beta"] = {"long_medio": float(np.nanmean(bl[dentro])), "short_medio": float(np.nanmean(bs[dentro])),
                   "a_medio": float(a[dentro].mean()), "b_medio": float(b[dentro].mean()),
                   "settimane_al_limite": int(((a[dentro] <= LIMITI[0]) | (a[dentro] >= LIMITI[1])).sum())}
    f5 = conti["F5"][conti["F5"].index >= se.INIZIO]
    peggiori = f5.nsmallest(15, "netto").index
    out["quindici_peggiori"] = {n: float(conti[n].loc[peggiori, "netto"].mean()) for n in conti}
    c = conti["F5"].index
    out["correlazione_F5N_F5"] = float(np.corrcoef(conti["F5N"].loc[c, "netto"], conti["F5"].loc[c, "netto"])[0, 1])
    serie = {**ast.serie_nuove(), "86 F5N": conti["F5N"]["netto"], "86 F5 120/80": conti["F5 120/80"]["netto"]}
    rivisto = ast.corretto_rivisto(serie, {"86 F5N": out["F5N"]["intero"], "86 F5 120/80": out["F5 120/80"]["intero"]})
    for n in ("F5N", "F5 120/80"):
        r = rivisto["candidate"][f"86 {n}"]
        out[n]["sharpe_corretto"], out[n]["t"], out[n]["gruppi"] = r["corretto_con_aggiunta"], r["t"], rivisto["gruppi"]
        out[n]["esito"] = te.esito(out[n], out[n]["sharpe_corretto"])
        out[n]["regola_del_proprietario"] = bool(out[n]["sharpe_corretto"] >= 0.90 and all(v > 0 for v in out[n]["per_anno"].values())
                                                 and out[n]["t"] > 3)
    (RIS / "esame.json").write_text(json.dumps(out, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    bb = out["beta"]
    righe = ["# Programma 7 — risultati della ventiquattresima prova (F5N: F5 neutra al mercato)", "",
             "Regole in `VENTIQUATTRESIMA.md` (scritte prima). Dal 4 gennaio 2021.", "",
             "| | Sharpe | l'anno | volatilità | discesa | per anno |", "|---|---|---|---|---|---|"]
    for n in ("F5", "F5N", "F5 120/80"):
        i = out[n]["intero"]
        righe.append(f"| {n} | {i['sharpe']:.2f} | {100 * i['annuo']:+.1f}% | {100 * i['volatilita']:.1f}% | {100 * i['discesa_max']:.1f}% | "
                     + ", ".join(f"{y} {100 * v:+.1f}%" for y, v in out[n]["per_anno"].items()) + " |")
    righe += ["",
              f"* Beta medio del lato long {bb['long_medio']:.2f}, del lato short {bb['short_medio']:.2f}; scalatura media long "
              f"{bb['a_medio']:.2f}, short {bb['b_medio']:.2f}; settimane al limite {bb['settimane_al_limite']}.",
              "* Le 15 settimane peggiori di F5, rifatte: " + ", ".join(f"{n} {100 * v:+.2f}%" for n, v in out["quindici_peggiori"].items())
              + f". Correlazione F5N-F5 {out['correlazione_F5N_F5']:.2f}.",
              *(f"* **{n}**: Sharpe corretto {out[n]['sharpe_corretto']:.2f} ({out[n]['gruppi']} gruppi), t {out[n]['t']:.2f}; esito "
                f"{out[n]['esito']}; regola del proprietario: {'sì' if out[n]['regola_del_proprietario'] else 'no'}." for n in ("F5N", "F5 120/80"))]
    testo = "\n".join(righe) + "\n"
    (QUI / "RISULTATI_VENTIQUATTRESIMA.md").write_text(testo, encoding="utf-8")
    log(testo)
    return out


if __name__ == "__main__":
    esegui(log=lambda x: print(x, flush=True))
    print("VENTIQUATTRESIMA FINITA", flush=True)
