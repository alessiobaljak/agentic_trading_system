"""Programma 6, cinquantaseiesima prova (CINQUANTASEIESIMA.md): F9, F5 fra le 100 con le variazioni del lunedi' a ordine
limite all'apertura per un'ora (0,02%), poi a mercato (il costo della moneta come in F5 piu' il movimento dell'ora contro).

Uso: python3 -m research.programma6.cinquantaseiesima
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from research.programma6 import asticella as ast
from research.programma6 import cinquantunesima as cu
from research.programma6 import esecuzione as es
from research.programma6 import ottava as ot
from research.programma6 import seconda as sc
from research.programma6 import sesta as se
from research.programma6 import terza as te
from research.programma6 import ventiquattresima as vq
from research.programma6.motore import MAKER

QUI = Path(__file__).parent
RIS = QUI / "risultati_cinquantaseiesima"


def costo_limite(o: float, h: float, l: float, p1: float, compra: bool, a_mercato: float) -> tuple:
    """(costo per unita', eseguito con il limite?): come `cinquantunesima.costo_limite` con il costo a mercato della moneta."""
    if (l < o) if compra else (h > o):
        return MAKER, True
    contro = (p1 / o - 1) if compra else (1 - p1 / o)
    return a_mercato + contro, False


def spese_a_limite(W: np.ndarray, R: np.ndarray, lunedi: np.ndarray, simboli: list, costo: np.ndarray, ore_di=es.ore_di) -> tuple:
    """Le spese di ogni settimana con le variazioni a limite e i conteggi (variazioni, eseguite con il limite, senza candele)."""
    D = cu.variazioni(W, R)
    spese = np.zeros(W.shape[0])
    n_tot = n_lim = n_senza = 0
    for j in np.flatnonzero(np.abs(D).sum(axis=0) > 0):
        b = ore_di(simboli[j])
        for w in np.flatnonzero(np.abs(D[:, j]) > 1e-9):
            dw = float(D[w, j])
            ora = int(lunedi[w]) * 24
            n_tot += 1
            if b.empty or ora not in b.index or ora + 1 not in b.index or not np.isfinite(b.loc[[ora, ora + 1]].to_numpy()).all():
                spese[w] += abs(dw) * costo[j]
                n_senza += 1
                continue
            c, preso = costo_limite(b.loc[ora, "open"], b.loc[ora, "high"], b.loc[ora, "low"], b.loc[ora + 1, "open"], dw > 0, costo[j])
            spese[w] += abs(dw) * c
            n_lim += preso
    return spese, n_tot, n_lim, n_senza


def esegui(log=print) -> dict:
    pan = sc.pannello()
    ps = te.pannello_settimane(pan, log=lambda x: None, indicatori_si=False)
    lun = ps["lunedi"] - pan["t0"]
    sig = ot.sigma_30(pan, lun)
    costo = sc.costi_moneta(ps["simboli"])
    W = vq.pesi_banda(np.where(np.isfinite(sig), -se.funding_7(pan, lun), np.nan), ps["U"], sig)
    a_mercato = te.conto(W, ps["R"], ps["F"], costo)
    a_mercato.index = ps["lunedi"]
    spese, n_tot, n_lim, n_senza = spese_a_limite(W, ps["R"], ps["lunedi"], ps["simboli"], costo)
    df = a_mercato.copy()
    df["spese"] = spese
    df["netto"] = df["lordo"] - df["spese"] - df["funding"]
    df["netto_doppio"] = df["lordo"] - 2 * df["spese"] - df["funding"]
    RIS.mkdir(exist_ok=True)
    df.to_csv(RIS / "settimane_F9.csv.gz")
    btc = pd.Series(ps["R"][:, ps["simboli"].index("BTCUSDT")], index=ps["lunedi"])
    e = te.esame(df, btc, inizio=se.INIZIO, anni_pieni=se.ANNI_PIENI)
    e5 = te.esame(a_mercato, btc, inizio=se.INIZIO, anni_pieni=se.ANNI_PIENI)
    d = df[df.index >= se.INIZIO]
    m = a_mercato[a_mercato.index >= se.INIZIO]
    scambiato = float(np.abs(cu.variazioni(W, ps["R"])[ps["lunedi"] >= se.INIZIO]).sum())
    e["costo_per_unita"] = {"limite": float(d["spese"].sum() / scambiato), "mercato": float(m["spese"].sum() / scambiato)}
    e["F5_a_mercato"] = {k: e5["intero"][k] for k in ("sharpe", "annuo", "discesa_max")} | {"spese_annue": e5["spese_annue"]}
    e["ordini"] = {"variazioni": n_tot, "eseguite_con_il_limite": n_lim, "senza_candele_a_1_ora": n_senza}
    rivisto = ast.corretto_rivisto({**ast.serie_nuove(), "56 F9": df["netto"]}, {"56 F9": e["intero"]})
    r = rivisto["candidate"]["56 F9"]
    e["sharpe_corretto"], e["sharpe_corretto_sezione_3"] = r["corretto_con_aggiunta"], r["corretto"]
    e["t"], e["gruppo"], e["gruppi"] = r["t"], r["gruppo"], rivisto["gruppi"]
    e["esito"] = te.esito(e, e["sharpe_corretto"])
    e["p17"] = bool(e["spese_annue"] < e5["spese_annue"] and e["intero"]["sharpe"] >= e5["intero"]["sharpe"])
    (RIS / "esame.json").write_text(json.dumps(e, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    i, o, q, c = e["intero"], e["ordini"], e["F5_a_mercato"], e["costo_per_unita"]
    testo = "\n".join([
        "# Programma 6 — risultati della cinquantaseiesima prova (F9: F5 fra le 100 con gli ordini limite)", "",
        "Regole in `CINQUANTASEIESIMA.md` (scritte prima).", "",
        f"* Variazioni di peso {o['variazioni']}: eseguite con il limite {o['eseguite_con_il_limite']} "
        f"({100 * o['eseguite_con_il_limite'] / max(1, o['variazioni']):.0f}%), senza le candele a 1 ora {o['senza_candele_a_1_ora']}.",
        f"* Costo per unità scambiata: a limite {100 * c['limite']:.3f}%, a mercato {100 * c['mercato']:.3f}%.",
        f"* F9: Sharpe {i['sharpe']:.2f}, {100 * i['annuo']:+.1f}% l'anno, volatilità {100 * i['volatilita']:.1f}%, discesa "
        f"{100 * i['discesa_max']:.1f}%; spese {100 * e['spese_annue']:.1f}% l'anno.",
        f"* F5 a mercato sulle stesse settimane: Sharpe {q['sharpe']:.2f}, {100 * q['annuo']:+.1f}% l'anno, discesa "
        f"{100 * q['discesa_max']:.1f}%, spese {100 * q['spese_annue']:.1f}%.",
        "* Per anno: " + ", ".join(f"{a} {100 * v:+.1f}%" for a, v in e["per_anno"].items()) + ".",
        f"* Sharpe corretto rivisto con l'aggiunta {e['sharpe_corretto']:.2f} (sezione 3: {e['sharpe_corretto_sezione_3']:.2f}; "
        f"{e['gruppi']} gruppi); t dello Sharpe {e['t']:.2f}; gruppo: " + ", ".join(e["gruppo"]) + ".", "",
        f"**Esito: {e['esito']}** (per la riserva di `CINQUANTASEIESIMA.md` F9 non diventa comunque validata).", "",
        f"**Voce P17: {'il bot passa F5 agli ordini limite' if e['p17'] else 'F5 nel bot resta a mercato'}** (regola fissata prima)."]) + "\n"
    (QUI / "RISULTATI_CINQUANTASEIESIMA.md").write_text(testo, encoding="utf-8")
    log(testo)
    return e


if __name__ == "__main__":
    esegui(log=lambda x: print(x, flush=True))
    print("CINQUANTASEIESIMA FINITA", flush=True)
