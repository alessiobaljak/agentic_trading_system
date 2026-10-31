"""Programma 7, ottantaduesima prova (OTTANTADUESIMA.md): FP, il momento delle salite continue («la rana nella pentola»), deciso ogni
giorno come G1. Fra le monete con la discontinuità dei 14 giorni fino alla mediana, long chi è salito di più e short chi è sceso di più;
deve battere anche il momento semplice sulle stesse regole.

Uso: python3 -m research.programma7.ottantaduesima
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
RIS = QUI / "risultati_ottantaduesima"
GIORNI = 14
NOME = "144 FP"


def numeri(pan: dict, idx: np.ndarray) -> tuple:
    """R14 e la discontinuità ID per ogni giorno di ``idx`` (chiusure da g − 15 a g − 1)."""
    c = pan["close"]
    with np.errstate(all="ignore"):
        r14 = c[idx - 1] / c[idx - 1 - GIORNI] - 1
        su = np.zeros(r14.shape)
        giu = np.zeros(r14.shape)
        tutti = np.ones(r14.shape, dtype=bool)
        for k in range(1, GIORNI + 1):
            d = c[idx - k] / c[idx - k - 1] - 1
            tutti &= np.isfinite(d)
            su += d > 0
            giu += d < 0
        idd = np.sign(r14) * (giu - su) / GIORNI
    ok = tutti & np.isfinite(r14) & (c[idx - 1 - GIORNI] > 0)
    return np.where(ok, r14, np.nan), np.where(ok, idd, np.nan)


def filtro(r14: np.ndarray, idd: np.ndarray, U: np.ndarray, meta: str) -> np.ndarray:
    """Il segnale R14 sulla metà continua (ID fino alla mediana del giorno) o sulla metà a salti."""
    out = np.full(r14.shape, np.nan)
    for k in range(r14.shape[0]):
        ok = U[k] & np.isfinite(r14[k]) & np.isfinite(idd[k])
        if not ok.any():
            continue
        m = np.median(idd[k, ok])
        sel = ok & ((idd[k] <= m) if meta == "continua" else (idd[k] > m))
        out[k, sel] = r14[k, sel]
    return out


def esegui(log=print) -> dict:
    pan = sc.pannello()
    ps = te.pannello_settimane(pan, log=lambda x: None, indicatori_si=False)
    giorni = np.arange(se.INIZIO, g1.FINE, dtype=np.int64)
    idx = giorni - pan["t0"]
    Ud = g1.universo_del_giorno(giorni, ps["lunedi"], ps["U"])
    sig = ot.sigma_30(pan, idx)
    r14, idd = numeri(pan, idx)
    R = sc.rendimenti(pan)[idx]
    F = np.nan_to_num(pan["funding"][idx])
    costo = sc.costi_moneta(pan["simboli"])
    btc = pd.Series(ps["R"][:, ps["simboli"].index("BTCUSDT")], index=ps["lunedi"])
    RIS.mkdir(exist_ok=True)
    out, serie = {}, {}
    varianti = (("FP", filtro(r14, idd, Ud, "continua")), ("momento semplice", r14), ("metà a salti", filtro(r14, idd, Ud, "salti")))
    for nome, ct in varianti:
        ct = np.where(np.isfinite(sig), ct, np.nan)
        W = vq.pesi_banda(ct, Ud, sig)
        lim, ordini = kp.conto(W, R, F, costo, giorni, pan["simboli"])
        s = g1.per_settimana(lim, giorni)
        s.to_csv(RIS / f"settimane_{nome.replace(' ', '_')}.csv.gz")
        e = te.esame(s, btc, inizio=se.INIZIO, anni_pieni=se.ANNI_PIENI)
        e["movimenti"] = g1.movimenti(W)
        e["monete_per_lato"] = {"long": float((W > 0).sum(axis=1).mean()), "short": float((W < 0).sum(axis=1).mean())}
        e["giorno_peggiore"] = float(lim["netto"].min())
        out[nome], serie[nome] = e, s
    e = out["FP"]
    rivisto = ast.corretto_rivisto({**ast.serie_nuove(), NOME: serie["FP"]["netto"]}, {NOME: e["intero"]})
    r = rivisto["candidate"][NOME]
    e["sharpe_corretto"], e["t"], e["gruppi"] = r["corretto_con_aggiunta"], r["t"], rivisto["gruppi"]
    e["esito_esame"] = te.esito(e, e["sharpe_corretto"])
    anni = e.get("per_anno", {})
    e["regola_proprietario"] = bool(e["sharpe_corretto"] >= 0.90 and e["t"] > 3 and anni and all(v > 0 for v in anni.values()))
    sopra = e["intero"]["sharpe"] > out["momento semplice"]["intero"]["sharpe"]
    e["esito"] = e["esito_esame"] if sopra else f"no: non sta sopra il momento semplice ({e['esito_esame']})"
    g1s = pd.read_csv(QUI / "risultati_ottantesima" / "settimane_G1.csv.gz", index_col=0)
    c = serie["FP"].index.intersection(g1s.index)
    e["correlazione_G1"] = float(np.corrcoef(serie["FP"].loc[c, "netto"], g1s.loc[c, "netto"])[0, 1]) if len(c) > 10 else None
    (RIS / "esame.json").write_text(json.dumps(out, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    pc = lambda v: "—" if v is None or v != v else f"{100 * v:+.1f}%"  # noqa: E731
    righe = ["# Programma 7 — risultati dell'ottantaduesima prova (FP: il momento delle salite continue)", "",
             "Regole in `OTTANTADUESIMA.md` (scritte prima). Dal 4 gennaio 2021 al 5 ottobre 2026, deciso ogni giorno come G1, stesso codice "
             "per le tre versioni.", ""]
    for nome, _ct in varianti:
        x = out[nome]
        i = x["intero"]
        mv = x["movimenti"]
        righe += [f"* **{nome}: Sharpe {i['sharpe']:.2f}**, {pc(i['annuo'])} l'anno, volatilità {100 * i['volatilita']:.1f}%, discesa "
                  f"{100 * i['discesa_max']:.1f}%, giorno peggiore {pc(x['giorno_peggiore'])}; spese {100 * x['spese_annue']:.1f}% l'anno; "
                  f"monete per lato {x['monete_per_lato']['long']:.1f} e {x['monete_per_lato']['short']:.1f}; movimenti {mv}.",
                  "  * Per anno: " + ", ".join(f"{a} {pc(v)}" for a, v in x["per_anno"].items()) + "."]
    righe += [f"* Correlazione di FP con G1: {'—' if e['correlazione_G1'] is None else format(e['correlazione_G1'], '.2f')}.",
              f"* Sharpe corretto con l'aggiunta {e['sharpe_corretto']:.2f} ({e['gruppi']} gruppi); t {e['t']:.2f}; regola del proprietario: "
              f"{'sì' if e['regola_proprietario'] else 'no'}.", "",
              f"**Esito: {e['esito']}**."]
    testo = "\n".join(righe) + "\n"
    (QUI / "RISULTATI_OTTANTADUESIMA.md").write_text(testo, encoding="utf-8")
    log(testo)
    return out


if __name__ == "__main__":
    esegui(log=lambda x: print(x, flush=True))
    print("OTTANTADUESIMA FINITA", flush=True)
