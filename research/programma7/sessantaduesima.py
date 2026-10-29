"""Programma 7, sessantaduesima prova (SESSANTADUESIMA.md): G1M, G1 con un minimo di monete per lato. Se un lato di G1 ha meno di 10
monete, tutti i pesi del giorno si moltiplicano per min(n_L, n_S)/10. Si giudica sui rischi contro G1 calcolata con lo stesso codice.

Uso: python3 -m research.programma7.sessantaduesima
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
from research.programma7 import cinquantaduesima as kp
from research.programma7 import prima as g1

QUI = Path(__file__).parent
RIS = QUI / "risultati_sessantaduesima"
MINIMO = 10


def fattore(W: np.ndarray) -> np.ndarray:
    nl, ns = (W > 0).sum(axis=1), (W < 0).sum(axis=1)
    m = np.minimum(nl, ns)
    return np.where((m > 0) & (m < MINIMO), m / MINIMO, 1.0)


def discesa(x: pd.Series) -> float:
    eq = (1 + x).cumprod()
    return float((eq / eq.cummax() - 1).min())


def esegui(log=print) -> dict:
    pan = sc.pannello()
    ps = te.pannello_settimane(pan, log=lambda x: None, indicatori_si=False)
    giorni = np.arange(se.INIZIO, g1.FINE, dtype=np.int64)
    idx = giorni - pan["t0"]
    Ud = g1.universo_del_giorno(giorni, ps["lunedi"], ps["U"])
    sig = ot.sigma_30(pan, idx)
    W = vq.pesi_banda(np.where(np.isfinite(sig), -se.funding_7(pan, idx), np.nan), Ud, sig)
    f = fattore(W)
    R = sc.rendimenti(pan)[idx]
    F = np.nan_to_num(pan["funding"][idx])
    costo = sc.costi_moneta(pan["simboli"])
    btc = pd.Series(ps["R"][:, ps["simboli"].index("BTCUSDT")], index=ps["lunedi"])
    out, giornaliere, sett = {}, {}, {}
    RIS.mkdir(exist_ok=True)
    for nome, Wx in (("G1", W), ("G1M", W * f[:, None])):
        lim, ordini = kp.conto(Wx, R, F, costo, giorni, pan["simboli"])
        s = g1.per_settimana(lim, giorni)
        s.to_csv(RIS / f"settimane_{nome}.csv.gz")
        e = te.esame(s, btc, inizio=se.INIZIO, anni_pieni=se.ANNI_PIENI)
        d = pd.Series(lim["netto"].to_numpy(), index=giorni)
        e["giorno_peggiore"], e["giorno_peggiore_data"] = float(d.min()), sc.data(int(d.idxmin()))
        e["settimana_peggiore"] = float(s["netto"].min())
        e["discesa_giorni"] = discesa(d)
        out[nome], giornaliere[nome], sett[nome] = e, d, s["netto"]
    a, b = out["G1"], out["G1M"]
    b["giorni_ridotti"] = int((f < 1).sum())
    b["fattore_medio_nei_giorni_ridotti"] = float(f[f < 1].mean()) if (f < 1).any() else None
    rng = np.random.default_rng(2026)
    sa, sb = sett["G1"].to_numpy(), sett["G1M"].to_numpy()
    n, blocco, meglio = len(sa), 8, 0
    for _ in range(2000):
        ii = np.concatenate([np.arange(k, k + blocco) for k in rng.integers(0, n - blocco, n // blocco)])
        meglio += discesa(pd.Series(sb[ii])) > discesa(pd.Series(sa[ii]))
    b["ricampionamento_discesa_meglio"] = meglio / 2000
    rivisto = ast.corretto_rivisto({**ast.serie_nuove(), "124 G1M": sett["G1M"]}, {"124 G1M": b["intero"]})
    r = rivisto["candidate"]["124 G1M"]
    b["sharpe_corretto"], b["t"], b["gruppi"] = r["corretto_con_aggiunta"], r["t"], rivisto["gruppi"]
    passa = (b["intero"]["discesa_max"] > a["intero"]["discesa_max"] and b["giorno_peggiore"] > a["giorno_peggiore"]
             and b["intero"]["sharpe"] >= a["intero"]["sharpe"] - 0.10)
    b["esito"] = "PASSA (protezione)" if passa else "non passa"
    (RIS / "esame.json").write_text(json.dumps(out, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    ia, ib = a["intero"], b["intero"]
    testo = "\n".join([
        "# Programma 7 — risultati della sessantaduesima prova (G1M: G1 con un minimo di monete per lato)", "",
        "Regole in `SESSANTADUESIMA.md` (scritte prima). Dal 4 gennaio 2021 al 5 ottobre 2026, stesso codice e stessi dati per tutte e due.", "",
        "| | Sharpe | l'anno | discesa (settimane) | discesa (giorni) | giorno peggiore | settimana peggiore |", "|---|---|---|---|---|---|---|",
        f"| G1 | {ia['sharpe']:.2f} | {100 * ia['annuo']:+.1f}% | {100 * ia['discesa_max']:.1f}% | {100 * a['discesa_giorni']:.1f}% | "
        f"{100 * a['giorno_peggiore']:.2f}% ({a['giorno_peggiore_data']}) | {100 * a['settimana_peggiore']:.2f}% |",
        f"| G1M | {ib['sharpe']:.2f} | {100 * ib['annuo']:+.1f}% | {100 * ib['discesa_max']:.1f}% | {100 * b['discesa_giorni']:.1f}% | "
        f"{100 * b['giorno_peggiore']:.2f}% ({b['giorno_peggiore_data']}) | {100 * b['settimana_peggiore']:.2f}% |", "",
        f"* Giorni con l'esposizione ridotta: {b['giorni_ridotti']}, fattore medio {b['fattore_medio_nei_giorni_ridotti'] or 0:.2f}.",
        "* Per anno G1M: " + ", ".join(f"{k} {100 * v:+.1f}%" for k, v in b["per_anno"].items()) + "; G1: " +
        ", ".join(f"{k} {100 * v:+.1f}%" for k, v in a["per_anno"].items()) + ".",
        f"* Ricampionamento a blocchi di 8 settimane: G1M scende meno di G1 nel {100 * b['ricampionamento_discesa_meglio']:.0f}% dei casi.",
        f"* Sharpe corretto di G1M {b['sharpe_corretto']:.2f} ({b['gruppi']} gruppi), t {b['t']:.2f}.", "",
        f"**Esito: {b['esito']}** (discesa e giorno peggiore più bassi di G1, Sharpe non più di 0,10 sotto)."]) + "\n"
    (QUI / "RISULTATI_SESSANTADUESIMA.md").write_text(testo, encoding="utf-8")
    log(testo)
    return out


if __name__ == "__main__":
    esegui(log=lambda x: print(x, flush=True))
    print("SESSANTADUESIMA FINITA", flush=True)
