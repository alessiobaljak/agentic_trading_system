"""Programma 6, cinquantunesima prova (CINQUANTUNESIMA.md): F7, F5 sulle monete 101-150 con le variazioni del lunedi' a
ordine limite all'apertura per un'ora (0,02%), poi a mercato (0,05% + 0,10% + il movimento dell'ora contro).

Uso: python3 -m research.programma6.cinquantunesima
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from research.programma6 import asticella as ast
from research.programma6 import esecuzione as es
from research.programma6 import ottava as ot
from research.programma6 import seconda as sc
from research.programma6 import sesta as se
from research.programma6 import settima as st
from research.programma6 import terza as te
from research.programma6 import ventiquattresima as vq
from research.programma6.motore import MAKER, TAKER

QUI = Path(__file__).parent
RIS = QUI / "risultati_cinquantunesima"
A_MERCATO = TAKER + st.SCARTO


def variazioni(W: np.ndarray, R: np.ndarray) -> np.ndarray:
    """Le variazioni di peso di ogni lunedi', con i pesi che derivano col prezzo durante la settimana (come `terza.conto`)."""
    R0 = np.nan_to_num(R)
    out = np.zeros_like(W)
    deriva = np.zeros(W.shape[1])
    for w in range(W.shape[0]):
        out[w] = W[w] - deriva
        lordo = float((W[w] * R0[w]).sum())
        deriva = W[w] * (1 + R0[w]) / (1 + lordo) if 1 + lordo > 0 else np.zeros(W.shape[1])
    return out


def costo_limite(o: float, h: float, l: float, p1: float, compra: bool) -> tuple:
    """(costo per unita', eseguito con il limite?) per una variazione al lunedi'."""
    if (l < o) if compra else (h > o):
        return MAKER, True
    contro = (p1 / o - 1) if compra else (1 - p1 / o)
    return A_MERCATO + contro, False


def esegui(log=print) -> dict:
    pan = sc.pannello()
    ps = te.pannello_settimane(pan, log=lambda x: None, da=100, a=150, indicatori_si=False)
    lun = ps["lunedi"] - pan["t0"]
    sig = ot.sigma_30(pan, lun)
    W = vq.pesi_banda(np.where(np.isfinite(sig), -se.funding_7(pan, lun), np.nan), ps["U"], sig)
    base = te.conto(W, ps["R"], ps["F"], np.zeros(len(ps["simboli"])))
    base.index = ps["lunedi"]
    D = variazioni(W, ps["R"])
    spese = np.zeros(W.shape[0])
    n_tot = n_lim = n_senza = 0
    for j in np.flatnonzero(np.abs(D).sum(axis=0) > 0):
        b = es.ore_di(ps["simboli"][j])
        for w in np.flatnonzero(np.abs(D[:, j]) > 1e-9):
            dw = float(D[w, j])
            ora = int(ps["lunedi"][w]) * 24
            n_tot += 1
            if b.empty or ora not in b.index or ora + 1 not in b.index or not np.isfinite(b.loc[[ora, ora + 1]].to_numpy()).all():
                spese[w] += abs(dw) * A_MERCATO
                n_senza += 1
                continue
            c, preso = costo_limite(b.loc[ora, "open"], b.loc[ora, "high"], b.loc[ora, "low"], b.loc[ora + 1, "open"], dw > 0)
            spese[w] += abs(dw) * c
            n_lim += preso
    df = base.copy()
    df["spese"] = spese
    df["netto"] = df["lordo"] - df["spese"] - df["funding"]
    df["netto_doppio"] = df["lordo"] - 2 * df["spese"] - df["funding"]
    RIS.mkdir(exist_ok=True)
    df.to_csv(RIS / "settimane_F7.csv.gz")
    pan_btc = te.pannello_settimane(pan, log=lambda x: None, indicatori_si=False)
    btc = pd.Series(pan_btc["R"][:, pan_btc["simboli"].index("BTCUSDT")], index=pan_btc["lunedi"])
    e = te.esame(df, btc, inizio=se.INIZIO, anni_pieni=se.ANNI_PIENI)
    p50 = pd.read_csv(QUI / "risultati_cinquantesima" / "settimane_F5_101_150.csv.gz", index_col=0)
    e50 = te.esame(p50, btc, inizio=se.INIZIO, anni_pieni=se.ANNI_PIENI)
    prima = ast.conto_di_prima() + [json.loads((QUI / "risultati_quarantanovesima" / "esame.json").read_text())[k]["intero"]["sharpe"]
                                    for k in ("X1", "X2")] + [e["intero"]["sharpe"]]
    x49 = {f"49 {k}": pd.read_csv(QUI / "risultati_quarantanovesima" / f"settimane_{k}.csv.gz", index_col=0)["netto"]
           for k in ("X1", "X2")}
    rivisto = ast.corretto_rivisto({**x49, "51 F7": df["netto"]}, {"51 F7": e["intero"]})
    r = rivisto["candidate"]["51 F7"]
    i = e["intero"]
    e["sharpe_corretto"], e["t"], e["gruppo"], e["gruppi"] = r["corretto"], r["t"], r["gruppo"], rivisto["gruppi"]
    e["sharpe_corretto_prima"] = te.sharpe_corretto(i["sharpe"], i["settimane"], i["asimmetria"], i["curtosi"], prima, 52)
    e["prove_nel_conto"] = len(prima)
    e["esito"] = te.esito(e, e["sharpe_corretto"])
    e["ordini"] = {"variazioni": n_tot, "eseguite_con_il_limite": n_lim, "senza_candele_a_1_ora": n_senza}
    e["prova_50"] = {k: e50["intero"][k] for k in ("sharpe", "annuo", "discesa_max")} | {"spese_annue": e50["spese_annue"]}
    (RIS / "esame.json").write_text(json.dumps(e, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    o, q = e["ordini"], e["prova_50"]
    testo = "\n".join([
        "# Programma 6 — risultati della cinquantunesima prova (F7: F5 sulle 101-150 con gli ordini limite)", "",
        "Regole in `CINQUANTUNESIMA.md` (scritte prima).", "",
        f"* Variazioni di peso {o['variazioni']}: eseguite con il limite {o['eseguite_con_il_limite']} "
        f"({100 * o['eseguite_con_il_limite'] / max(1, o['variazioni']):.0f}%), senza le candele a 1 ora {o['senza_candele_a_1_ora']}.",
        f"* F7: Sharpe {i['sharpe']:.2f}, {100 * i['annuo']:+.1f}% l'anno, volatilità {100 * i['volatilita']:.1f}%, discesa "
        f"{100 * i['discesa_max']:.1f}%; spese {100 * e['spese_annue']:.1f}% l'anno.",
        f"* La prova 50 (a mercato) sulle stesse settimane: Sharpe {q['sharpe']:.2f}, {100 * q['annuo']:+.1f}% l'anno, spese "
        f"{100 * q['spese_annue']:.1f}%.",
        "* Per anno: " + ", ".join(f"{a} {100 * v:+.1f}%" for a, v in e["per_anno"].items()) + ".",
        f"* Sharpe corretto rivisto {e['sharpe_corretto']:.2f} ({e['gruppi']} gruppi; prima {e['sharpe_corretto_prima']:.2f} con "
        f"{e['prove_nel_conto']} prove); t dello Sharpe {e['t']:.2f}.", "",
        f"**Esito: {e['esito']}**"]) + "\n"
    (QUI / "RISULTATI_CINQUANTUNESIMA.md").write_text(testo, encoding="utf-8")
    log(testo)
    return e


if __name__ == "__main__":
    esegui(log=lambda x: print(x, flush=True))
    print("CINQUANTUNESIMA FINITA", flush=True)
