"""Programma 7, settantaseiesima prova (SETTANTASEIESIMA.md): GA, quanto i giornali crypto parlano di una moneta, a settimana come F5.
Short il quinto con l'attenzione piu' alta, long il piu' basso. GA1: la quota degli articoli dei 28 giorni rispetto agli 84 prima; GA2: gli
articoli per dollaro scambiato.

Uso: python3 -m research.programma7.settantaseiesima
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from research.programma6 import annunci as an
from research.programma6 import asticella as ast
from research.programma6 import ottava as ot
from research.programma6 import seconda as sc
from research.programma6 import sesta as se
from research.programma6 import terza as te
from research.programma6 import ventiquattresima as vq

QUI = Path(__file__).parent
RIS = QUI / "risultati_settantaseiesima"
FILE = QUI.parent / "data" / "notizie_coindesk" / "coindesk.csv"
FINE = sc.giorno(2025, 1, 27)
RITARDO, RECENTE, PRIMA, MINIMO, MESCOLATE, SEME = 2, 28, 84, 3, 20, 2026


def articoli(pan: dict) -> tuple:
    """Gli articoli per giorno e per moneta (giorni del pannello × monete) e il totale degli articoli per giorno."""
    d = pd.read_csv(FILE, usecols=["published_on", "categories"])
    d["giorno"] = (pd.to_datetime(d["published_on"]).astype("int64") // 86_400_000_000_000).astype(int)
    T, S = pan["close"].shape
    t0 = pan["t0"]
    A = np.zeros((T, S))
    N = np.zeros(T)
    simboli = list(pan["simboli"])
    mappa: dict = {}
    for g, c in zip(d["giorno"].to_numpy(), d["categories"].fillna("").to_numpy()):
        k = g - t0
        if not 0 <= k < T:
            continue
        N[k] += 1
        for x in set(str(c).split("|")):
            if x not in mappa:
                mappa[x] = an.perpetuo(x, simboli) if x.isupper() else ""
            s = mappa[x]
            if s:
                A[k, simboli.index(s)] += 1
    return A, N, {k: v for k, v in mappa.items() if v}


def segnali(pan: dict, A: np.ndarray, N: np.ndarray, lun_idx: np.ndarray) -> tuple:
    Ac = np.vstack([np.zeros((1, A.shape[1])), np.cumsum(A, axis=0)])
    Nc = np.r_[0.0, np.cumsum(N)]
    V = np.nan_to_num(pan["quote_volume"])
    Vc = np.vstack([np.zeros((1, V.shape[1])), np.cumsum(V, axis=0)])
    fine = lun_idx - RITARDO + 1                       # finestre che finiscono alla fine del giorno l - 2
    a_rec = Ac[fine] - Ac[fine - RECENTE]
    a_pri = Ac[fine - RECENTE] - Ac[fine - RECENTE - PRIMA]
    n_rec = (Nc[fine] - Nc[fine - RECENTE])[:, None]
    n_pri = (Nc[fine - RECENTE] - Nc[fine - RECENTE - PRIMA])[:, None]
    v_rec = Vc[fine] - Vc[fine - RECENTE]
    with np.errstate(all="ignore"):
        ga1 = np.log((a_rec + 1) / n_rec) - np.log((a_pri + 1) / n_pri)
        ga2 = np.log((a_rec + 1) / v_rec)
    ok = (a_rec + a_pri >= MINIMO) & (n_rec > 0) & (n_pri > 0)
    ga1 = np.where(ok & np.isfinite(ga1), ga1, np.nan)
    ga2 = np.where(ok & (v_rec > 0) & np.isfinite(ga2), ga2, np.nan)
    return ga1, ga2


def esegui(log=print) -> dict:
    # l'archivio finisce a gennaio 2025: l'«ultimo anno» dell'esame e' l'ultimo anno dei dati (27 gennaio 2024 - 27 gennaio 2025),
    # e il tratto «dopo aprile 2025» (solo descrittivo) non esiste; si spostano le due date al 27 gennaio 2024
    sc.ULTIMO_ANNO = sc.PUBBLICAZIONE = FINE - 364
    pan = sc.pannello()
    ps = te.pannello_settimane(pan, log=lambda x: None, indicatori_si=False)
    A, N, mappa = articoli(pan)
    log(f"[settantaseiesima] {int(N.sum())} articoli nel periodo del pannello, {len(mappa)} sigle abbinate a un perpetuo")
    lun = ps["lunedi"]
    idx = lun - pan["t0"]
    ga1, ga2 = segnali(pan, A, N, idx)
    sig = ot.sigma_30(pan, idx)
    costo = sc.costi_moneta(pan["simboli"])
    btc = pd.Series(ps["R"][:, ps["simboli"].index("BTCUSDT")], index=lun)
    tieni = (lun >= se.INIZIO) & (lun <= FINE)
    U = ps["U"] & (lun <= FINE)[:, None]
    f5 = pd.read_csv(QUI.parent / "programma6" / "risultati_controllo_parita" / "settimane_F5.csv.gz", index_col=0)
    rng = np.random.default_rng(SEME)
    out, serie = {}, {}
    RIS.mkdir(exist_ok=True)

    def conto(D, verso=-1.0):
        W = vq.pesi_banda(np.where(np.isfinite(sig) & U, verso * D, np.nan), U, sig)
        df = te.conto(W, ps["R"], ps["F"], costo)
        df.index = lun
        return df[df.index <= FINE], W
    for nome, D in (("GA1", ga1), ("GA2", ga2)):
        df, W = conto(D)
        df.to_csv(RIS / f"settimane_{nome}.csv.gz")
        e = te.esame(df, btc, inizio=se.INIZIO, anni_pieni=(2021, 2022, 2023, 2024))
        valide = (np.isfinite(D) & U)[tieni]
        e["monete_con_segnale_mediana"] = float(np.median(valide.sum(axis=1)))
        e["settimane_con_posizioni"] = int((np.abs(W[tieni]).sum(axis=1) > 0).sum())
        e["settimane"] = int(tieni.sum())
        c = df.index.intersection(f5.index)
        c = c[c >= se.INIZIO]
        e["correlazione_F5"] = float(np.corrcoef(df.loc[c, "netto"], f5.loc[c, "netto"])[0, 1])
        op, _ = conto(D, +1.0)
        e["opposto_sharpe"] = te.numeri_settimana(op[op.index >= se.INIZIO]["netto"])["sharpe"]
        sh = []
        for _ in range(MESCOLATE):
            M = np.full_like(D, np.nan)
            for k in range(D.shape[0]):
                jj = np.flatnonzero(np.isfinite(D[k]) & U[k])
                if len(jj):
                    M[k, jj] = rng.permutation(D[k, jj])
            dm, _ = conto(M)
            sh.append(te.numeri_settimana(dm[dm.index >= se.INIZIO]["netto"])["sharpe"])
        e["mescolato_sharpe_medio"], e["mescolato_sopra"] = float(np.mean(sh)), int(sum(1 for v in sh if v >= e["intero"]["sharpe"]))
        out[nome], serie[nome] = e, df
    rivisto = ast.corretto_rivisto({**ast.serie_nuove(), "138 GA1": serie["GA1"]["netto"], "138 GA2": serie["GA2"]["netto"]},
                                   {"138 GA1": out["GA1"]["intero"], "138 GA2": out["GA2"]["intero"]})
    for nome in ("GA1", "GA2"):
        e = out[nome]
        r = rivisto["candidate"][f"138 {nome}"]
        e["sharpe_corretto"], e["t"], e["gruppi"] = r["corretto_con_aggiunta"], r["t"], rivisto["gruppi"]
        e["esito"] = te.esito(e, e["sharpe_corretto"])
        anni = e.get("per_anno", {})
        e["regola_proprietario"] = bool(e["sharpe_corretto"] >= 0.90 and e["t"] > 3 and anni and all(v > 0 for v in anni.values()))
    (RIS / "esame.json").write_text(json.dumps({"sigle": mappa, **out}, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    pc = lambda v: f"{100 * v:+.1f}%"  # noqa: E731
    righe = ["# Programma 7 — risultati della settantaseiesima prova (GA: quanto i giornali crypto parlano di una moneta)", "",
             "Regole in `SETTANTASEIESIMA.md` (scritte prima). Dal 4 gennaio 2021 al 27 gennaio 2025, 229.172 articoli raccolti da CoinDesk "
             f"Data, {len(mappa)} sigle abbinate a un perpetuo; short il quinto con l'attenzione più alta, long il più basso, come F5.", ""]
    for nome, titolo in (("GA1", "l'attenzione che sale"), ("GA2", "gli articoli per dollaro scambiato")):
        e = out[nome]
        i = e["intero"]
        righe += [
            f"* **{nome} ({titolo}): Sharpe {i['sharpe']:.2f}**, {pc(i['annuo'])} l'anno, volatilità {100 * i['volatilita']:.1f}%, discesa "
            f"{100 * i['discesa_max']:.1f}%; spese {100 * e['spese_annue']:.1f}% l'anno; lato long {pc(e['long_annuo'])}, short "
            f"{pc(e['short_annuo'])} l'anno.",
            "  * Per anno: " + ", ".join(f"{a} {pc(x)}" for a, x in e["per_anno"].items()) + ".",
            f"  * Monete con il segnale, mediana {e['monete_con_segnale_mediana']:.0f} a settimana; settimane con le posizioni "
            f"{e['settimane_con_posizioni']} su {e['settimane']}.",
            f"  * Il segnale mescolato: Sharpe medio {e['mescolato_sharpe_medio']:.2f}, {e['mescolato_sopra']} su {MESCOLATE} sopra quello "
            f"vero; il verso opposto {e['opposto_sharpe']:.2f}; correlazione con F5 {e['correlazione_F5']:.2f}.",
            f"  * Sharpe corretto con l'aggiunta {e['sharpe_corretto']:.2f} ({e['gruppi']} gruppi); t {e['t']:.2f}; regola del proprietario: "
            f"{'sì' if e['regola_proprietario'] else 'no'}. **Esito: {e['esito']}**."]
    testo = "\n".join(righe) + "\n"
    (QUI / "RISULTATI_SETTANTASEIESIMA.md").write_text(testo, encoding="utf-8")
    log(testo)
    return out


if __name__ == "__main__":
    esegui(log=lambda x: print(x, flush=True))
    print("SETTANTASEIESIMA FINITA", flush=True)
