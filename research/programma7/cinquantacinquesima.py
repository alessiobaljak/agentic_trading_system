"""Programma 7, cinquantacinquesima prova (CINQUANTACINQUESIMA.md): EMI ed EWIL, le monete «inelastiche» di Li, Liao, Yang e Zhang
(bozza 2026). InRank = media dei ranghi della salita dal minimo e del crollo dal massimo delle 12 settimane, annualizzati; EMI long il
quinto elastico e short l'inelastico; EWIL long le vincenti elastiche e short le perdenti inelastiche (30/40/30). A settimana, senza banda.

Uso: python3 -m research.programma7.cinquantacinquesima
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

QUI = Path(__file__).parent
RIS = QUI / "risultati_cinquantacinquesima"
FINESTRA, DUE_SETTIMANE = 84, 14
DOPO_ARTICOLO = sc.giorno(2024, 6, 3)


def inelasticita(c: np.ndarray) -> tuple[float, float]:
    """(salita, crollo) annualizzati sulle chiusure c (l'ultima e' la domenica); 0 se l'estremo e' l'ultimo giorno."""
    n = len(c)
    p = c[-1]
    i_min = n - 1 - int(np.argmin(c[::-1]))          # a parita' l'ultimo giorno
    i_max = n - 1 - int(np.argmax(c[::-1]))
    g_min, g_max = n - 1 - i_min, n - 1 - i_max
    salita = (p / c[i_min] - 1) * 365 / g_min if g_min > 0 else 0.0
    crollo = (p / c[i_max] - 1) * 365 / g_max if g_max > 0 else 0.0
    return salita, crollo


def ranghi(v: np.ndarray) -> np.ndarray:
    return pd.Series(v).rank(pct=True).to_numpy()


def pesi(pan: dict, ps: dict, sig: np.ndarray, variante: str) -> tuple[np.ndarray, list]:
    C = pan["close"]
    t0 = pan["t0"]
    lun = ps["lunedi"]
    W = np.zeros((len(lun), C.shape[1]))
    lati = []
    for k, l in enumerate(lun):
        i = l - t0
        if i - FINESTRA < 0:
            lati.append((0, 0))
            continue
        blocco = C[i - FINESTRA:i]
        ok = ps["U"][k] & np.isfinite(blocco).all(axis=0) & np.isfinite(sig[k]) & (sig[k] > 0)
        js = np.flatnonzero(ok)
        if len(js) < te.MIN_MONETE:
            lati.append((0, 0))
            continue
        sc_, cr = zip(*(inelasticita(blocco[:, j]) for j in js))
        inr = ranghi((ranghi(np.array(sc_)) + ranghi(np.abs(np.array(cr)))) / 2)
        if variante == "EMI":
            lunghi, corti = js[inr <= 0.2], js[inr > 0.8]
        else:
            r2 = ranghi(blocco[-1, js] / blocco[-1 - DUE_SETTIMANE, js] - 1)
            lunghi, corti = js[(r2 > 0.7) & (inr <= 0.3)], js[(r2 <= 0.3) & (inr > 0.7)]
            if len(lunghi) < 2 or len(corti) < 2:
                lati.append((len(lunghi), len(corti)))
                continue
        for lato, segno in ((lunghi, 1.0), (corti, -1.0)):
            inv = 1.0 / sig[k, lato]
            W[k, lato] = segno * inv / inv.sum()
        lati.append((len(lunghi), len(corti)))
    return W, lati


def esegui(log=print) -> dict:
    pan = sc.pannello()
    ps = te.pannello_settimane(pan, log=lambda x: None, indicatori_si=False)
    assert ps["simboli"] == pan["simboli"]
    lun = ps["lunedi"]
    sig = ot.sigma_30(pan, lun - pan["t0"])
    costo = sc.costi_moneta(pan["simboli"])
    btc = pd.Series(ps["R"][:, ps["simboli"].index("BTCUSDT")], index=lun)
    f5 = pd.read_csv(QUI.parent / "programma6" / "risultati_controllo_parita" / "settimane_F5.csv.gz", index_col=0)
    out, serie = {}, {}
    RIS.mkdir(exist_ok=True)
    for v in ("EMI", "EWIL"):
        W, lati = pesi(pan, ps, sig, v)
        for nome, segno in ((v, 1.0), (f"{v} opposto", -1.0)):
            df = te.conto(segno * W, ps["R"], ps["F"], costo)
            df.index = lun
            df.to_csv(RIS / f"settimane_{nome.replace(' ', '_')}.csv.gz")
            e = te.esame(df, btc, inizio=se.INIZIO, anni_pieni=se.ANNI_PIENI)
            if segno > 0:
                dopo = te.esame(df, btc, inizio=DOPO_ARTICOLO, anni_pieni=(2025,))
                e["dopo_l_articolo"] = {k: dopo["intero"][k] for k in ("sharpe", "annuo", "discesa_max")}
                c = df.index.intersection(f5.index)
                c = c[c >= se.INIZIO]
                e["correlazione_F5"] = float(np.corrcoef(df.loc[c, "netto"], f5.loc[c, "netto"])[0, 1])
                dal = lun >= se.INIZIO
                L = np.array(lati)[dal]
                e["monete_per_lato_mediana"] = [float(np.median(L[:, 0])), float(np.median(L[:, 1]))]
                e["settimane_con_posizioni"] = int((np.abs(W[dal]).sum(axis=1) > 0).sum())
                serie[f"117 {v}"] = df["netto"]
            out[nome] = e
    rivisto = ast.corretto_rivisto({**ast.serie_nuove(), **serie}, {k: out[k[4:]]["intero"] for k in serie})
    for k in serie:
        e = out[k[4:]]
        r = rivisto["candidate"][k]
        e["sharpe_corretto"], e["t"], e["gruppi"] = r["corretto_con_aggiunta"], r["t"], rivisto["gruppi"]
        e["esito"] = te.esito(e, e["sharpe_corretto"])
        anni = e.get("per_anno", {})
        e["regola_proprietario"] = bool(e["sharpe_corretto"] >= 0.90 and e["t"] > 3 and anni and all(x > 0 for x in anni.values()))
    (RIS / "esame.json").write_text(json.dumps(out, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    righe = ["# Programma 7 — risultati della cinquantacinquesima prova (EMI ed EWIL: le monete inelastiche, a settimana)", "",
             "Regole in `CINQUANTACINQUESIMA.md` (scritte prima). Dal 4 gennaio 2021, chiusure giornaliere di Binance, le 100 monete più "
             "scambiate di ogni settimana.", ""]
    for v in ("EMI", "EWIL"):
        e, op = out[v], out[f"{v} opposto"]["intero"]
        i, d = e["intero"], e["dopo_l_articolo"]
        righe += [f"* **{v}: Sharpe {i['sharpe']:.2f}**, {100 * i['annuo']:+.1f}% l'anno, volatilità {100 * i['volatilita']:.1f}%, discesa "
                  f"{100 * i['discesa_max']:.1f}%, spese {100 * e['spese_annue']:.1f}% l'anno; monete per lato (mediana) "
                  f"{e['monete_per_lato_mediana'][0]:.0f} e {e['monete_per_lato_mediana'][1]:.0f}, settimane con le posizioni "
                  f"{e['settimane_con_posizioni']}.",
                  "  Per anno: " + ", ".join(f"{a} {100 * x:+.1f}%" for a, x in e["per_anno"].items()) + "; dal giugno 2024 (fuori dal campione "
                  f"dell'articolo) Sharpe {d['sharpe']:.2f}, {100 * d['annuo']:+.1f}% l'anno; il verso opposto Sharpe {op['sharpe']:.2f}; "
                  f"correlazione con F5 {e['correlazione_F5']:.2f}; Sharpe corretto {e['sharpe_corretto']:.2f} ({e['gruppi']} gruppi), "
                  f"t {e['t']:.2f}; regola del proprietario: {'sì' if e['regola_proprietario'] else 'no'}. **Esito: {e['esito']}**."]
    testo = "\n".join(righe) + "\n"
    (QUI / "RISULTATI_CINQUANTACINQUESIMA.md").write_text(testo, encoding="utf-8")
    log(testo)
    return out


if __name__ == "__main__":
    esegui(log=lambda x: print(x, flush=True))
    print("CINQUANTACINQUESIMA FINITA", flush=True)
