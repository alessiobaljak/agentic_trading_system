"""Programma 7, cinquantaseiesima prova (CINQUANTASEIESIMA.md): MV, il momento dei vicini deciso ogni giorno come G1. Il segnale e' la
media dei rendimenti di ieri delle 10 monete piu' correlate (90 giorni prima, almeno 60 in comune); long il quinto piu' alto, short il
piu' basso, banda 20/40, ordini limite.

Uso: python3 -m research.programma7.cinquantaseiesima
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
RIS = QUI / "risultati_cinquantaseiesima"
FINE = sc.giorno(2026, 10, 19)
GIORNI, MINIMO, VICINI = 90, 60, 10


def rendimenti_con_buchi(pan: dict) -> np.ndarray:
    """Il rendimento del giorno t (apertura → apertura dopo), NaN dove manca."""
    O = pan["open"]
    r = np.full(O.shape, np.nan)
    with np.errstate(all="ignore"):
        r[:-1] = O[1:] / O[:-1] - 1
    return r


def segnale(pan: dict, idx: np.ndarray, Ud: np.ndarray) -> np.ndarray:
    r = rendimenti_con_buchi(pan)
    S = np.full((len(idx), r.shape[1]), np.nan)
    for k, i in enumerate(idx):
        js = np.flatnonzero(Ud[k])
        if len(js) < VICINI + 1 or i - GIORNI < 0:
            continue
        blocco = pd.DataFrame(r[i - GIORNI:i][:, js])
        C = blocco.corr(min_periods=MINIMO).to_numpy()
        np.fill_diagonal(C, np.nan)
        ieri = r[i - 1, js]
        for a, j in enumerate(js):
            c = C[a]
            ok = np.flatnonzero(np.isfinite(c) & np.isfinite(ieri))
            if len(ok) < VICINI:
                continue
            vicini = ok[np.argsort(-c[ok])[:VICINI]]
            S[k, j] = float(np.mean(ieri[vicini]))
    return S


def senza_banda(ct: np.ndarray, U: np.ndarray, sig: np.ndarray) -> np.ndarray:
    W = np.zeros(ct.shape)
    for k in range(ct.shape[0]):
        js = np.flatnonzero(U[k] & np.isfinite(ct[k]) & np.isfinite(sig[k]) & (sig[k] > 0))
        if len(js) < te.MIN_MONETE:
            continue
        p = pd.Series(ct[k, js]).rank(pct=True).to_numpy()
        for lato, segno in ((js[p > 0.8], 1.0), (js[p <= 0.2], -1.0)):
            if len(lato):
                inv = 1.0 / sig[k, lato]
                W[k, lato] = segno * inv / inv.sum()
    return W


def esegui(log=print) -> dict:
    pan = sc.pannello()
    ps = te.pannello_settimane(pan, log=lambda x: None, indicatori_si=False)
    giorni = np.arange(se.INIZIO, FINE, dtype=np.int64)
    idx = giorni - pan["t0"]
    Ud = g1.universo_del_giorno(giorni, ps["lunedi"], ps["U"])
    sig = ot.sigma_30(pan, idx)
    log("[cinquantaseiesima] calcolo i vicini di ogni giorno")
    S = segnale(pan, idx, Ud)
    R = sc.rendimenti(pan)[idx]
    F = np.nan_to_num(pan["funding"][idx])
    costo = sc.costi_moneta(pan["simboli"])
    btc = pd.Series(ps["R"][:, ps["simboli"].index("BTCUSDT")], index=ps["lunedi"])
    out = {}
    RIS.mkdir(exist_ok=True)
    for nome, verso in (("MV", 1.0), ("MV opposto", -1.0)):
        W = vq.pesi_banda(np.where(np.isfinite(sig), verso * S, np.nan), Ud, sig)
        lim, ordini = kp.conto(W, R, F, costo, giorni, pan["simboli"])
        sett = g1.per_settimana(lim, giorni)
        sett.to_csv(RIS / f"settimane_{nome.replace(' ', '_')}.csv.gz")
        e = te.esame(sett, btc, inizio=se.INIZIO, anni_pieni=se.ANNI_PIENI)
        e["ordini"], e["movimenti"] = ordini, g1.movimenti(W)
        out[nome] = e
        if nome == "MV":
            sett_mv = sett
    Wn = senza_banda(np.where(np.isfinite(sig), S, np.nan), Ud, sig)
    sett_n = g1.per_settimana(te.conto(Wn, R, F, costo), giorni)
    en = te.esame(sett_n, btc, inizio=se.INIZIO, anni_pieni=se.ANNI_PIENI)
    e = out["MV"]
    e["senza_banda_a_mercato"] = {k: en["intero"][k] for k in ("sharpe", "annuo", "discesa_max")} | {"spese_annue": en["spese_annue"],
                                                                                                     "lordo_annuo": float(sett_n["lordo"].sum() / max(1, len(sett_n)) * 52)}
    rivisto = ast.corretto_rivisto({**ast.serie_nuove(), "118 MV": sett_mv["netto"]}, {"118 MV": e["intero"]})
    r = rivisto["candidate"]["118 MV"]
    e["sharpe_corretto"], e["t"], e["gruppi"] = r["corretto_con_aggiunta"], r["t"], rivisto["gruppi"]
    e["esito"] = te.esito(e, e["sharpe_corretto"])
    g1s = pd.read_csv(QUI / "risultati_prima" / "settimane_G1.csv.gz", index_col=0)
    c = sett_mv.index.intersection(g1s.index)
    e["correlazione_G1"] = float(np.corrcoef(sett_mv.loc[c, "netto"], g1s.loc[c, "netto"])[0, 1])
    anni = e.get("per_anno", {})
    e["regola_proprietario"] = bool(e["sharpe_corretto"] >= 0.90 and e["t"] > 3 and anni and all(x > 0 for x in anni.values()))
    (RIS / "esame.json").write_text(json.dumps(out, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    i, mv, op, nb = e["intero"], e["movimenti"], out["MV opposto"]["intero"], e["senza_banda_a_mercato"]
    testo = "\n".join([
        "# Programma 7 — risultati della cinquantaseiesima prova (MV: il momento dei vicini, ogni giorno)", "",
        "Regole in `CINQUANTASEIESIMA.md` (scritte prima). Dal 4 gennaio 2021 al 19 ottobre 2026, le 100 monete più scambiate.", "",
        f"* Operazioni: {mv['entrate_al_giorno']:.1f} entrate e {mv['uscite_al_giorno']:.1f} uscite al giorno; una posizione dura in media "
        f"{mv['durata_media_giorni']:.1f} giorni.",
        f"* **MV: Sharpe {i['sharpe']:.2f}**, {100 * i['annuo']:+.1f}% l'anno, volatilità {100 * i['volatilita']:.1f}%, discesa "
        f"{100 * i['discesa_max']:.1f}%; spese {100 * e['spese_annue']:.1f}% l'anno.",
        "* Per anno: " + ", ".join(f"{a} {100 * x:+.1f}%" for a, x in e["per_anno"].items()) + ".",
        f"* Il verso opposto: Sharpe {op['sharpe']:.2f}, {100 * op['annuo']:+.1f}% l'anno.",
        f"* Senza banda, rifatte ogni giorno e a mercato: Sharpe {nb['sharpe']:.2f}, {100 * nb['annuo']:+.1f}% l'anno, spese "
        f"{100 * nb['spese_annue']:.1f}%, lordo {100 * nb['lordo_annuo']:+.1f}% l'anno.",
        f"* Correlazione con G1: {e['correlazione_G1']:.2f}.",
        f"* Sharpe corretto con l'aggiunta {e['sharpe_corretto']:.2f} ({e['gruppi']} gruppi); t {e['t']:.2f}; regola del proprietario: "
        f"{'sì' if e['regola_proprietario'] else 'no'}.", "",
        f"**Esito: {e['esito']}**"]) + "\n"
    (QUI / "RISULTATI_CINQUANTASEIESIMA.md").write_text(testo, encoding="utf-8")
    log(testo)
    return out


if __name__ == "__main__":
    esegui(log=lambda x: print(x, flush=True))
    print("CINQUANTASEIESIMA FINITA", flush=True)
