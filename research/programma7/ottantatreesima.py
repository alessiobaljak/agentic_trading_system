"""Programma 7, ottantatreesima prova (OTTANTATREESIMA.md): NV, le notizie nuove contro quelle ripetute, a settimana come F5. La novità di
ogni articolo su una moneta è 1 meno la somiglianza più alta con i 20 articoli precedenti sulla stessa moneta dei giorni prima; long il
quinto con le notizie più nuove dei 28 giorni, short il quinto con le più ripetute. Archivio della prova 138, 2021 – gennaio 2025.

Uso: python3 -m research.programma7.ottantatreesima
"""
from __future__ import annotations

import html
import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import HashingVectorizer

from research.programma6 import annunci as an
from research.programma6 import asticella as ast
from research.programma6 import ottava as ot
from research.programma6 import seconda as sc
from research.programma6 import sesta as se
from research.programma6 import terza as te
from research.programma6 import ventiquattresima as vq
from research.programma7 import settantaseiesima as ga

QUI = Path(__file__).parent
RIS = QUI / "risultati_ottantatreesima"
FINE = ga.FINE
RITARDO, RECENTE, PRECEDENTI, MIN_PRECEDENTI, FINESTRA_PRECEDENTI, MINIMO, MESCOLATE, SEME = 2, 28, 20, 5, 90, 3, 20, 2026
NOME = "145 NV"


def novita(pan: dict, log=print) -> tuple:
    """Somma della novità e numero degli articoli che contano, per giorno del pannello e per moneta."""
    d = pd.read_csv(ga.FILE, usecols=["published_on", "title", "body", "categories"])
    d["giorno"] = (pd.to_datetime(d["published_on"]).astype("int64") // 86_400_000_000_000).astype(int)
    d = d.sort_values("published_on", kind="stable").reset_index(drop=True)
    simboli = list(pan["simboli"])
    mappa: dict = {}
    per_moneta: dict = {}
    for i, c in enumerate(d["categories"].fillna("").to_numpy()):
        for x in set(str(c).split("|")):
            if x not in mappa:
                mappa[x] = an.perpetuo(x, simboli) if x.isupper() else ""
            s = mappa[x]
            if s:
                per_moneta.setdefault(s, []).append(i)
    testi = [html.unescape(f"{a} {b}").lower() for a, b in zip(d["title"].fillna("").to_numpy(), d["body"].fillna("").to_numpy())]
    X = HashingVectorizer(n_features=2 ** 20, ngram_range=(1, 2), stop_words="english", alternate_sign=False, norm="l2").transform(testi)
    log(f"[ottantatreesima] {len(d)} articoli, {len(per_moneta)} monete con il perpetuo citate")
    T, S = pan["close"].shape
    t0 = pan["t0"]
    somma, conta = np.zeros((T, S)), np.zeros((T, S))
    giorni = d["giorno"].to_numpy()
    tutte = []
    for s, ii in per_moneta.items():
        j = simboli.index(s)
        ii = np.array(ii)
        ds = giorni[ii]
        Xs = X[ii]
        for k in range(len(ii)):
            fine = int(np.searchsorted(ds, ds[k], side="left"))          # solo gli articoli dei giorni prima
            inizio = max(fine - PRECEDENTI, int(np.searchsorted(ds, ds[k] - FINESTRA_PRECEDENTI, side="left")))
            if fine - inizio < MIN_PRECEDENTI:
                continue
            sim = (Xs[k] @ Xs[inizio:fine].T).toarray().ravel()
            nv = 1.0 - float(sim.max())
            g = ds[k] - t0
            if 0 <= g < T:
                somma[g, j] += nv
                conta[g, j] += 1
                tutte.append(nv)
    log(f"[ottantatreesima] {len(tutte)} coppie articolo-moneta con la novità; mediana {np.median(tutte):.3f}")
    return somma, conta, {k: v for k, v in mappa.items() if v}, len(tutte), float(np.median(tutte))


def segnale(somma: np.ndarray, conta: np.ndarray, lun_idx: np.ndarray) -> np.ndarray:
    Sc = np.vstack([np.zeros((1, somma.shape[1])), np.cumsum(somma, axis=0)])
    Cc = np.vstack([np.zeros((1, conta.shape[1])), np.cumsum(conta, axis=0)])
    fine = lun_idx - RITARDO + 1
    s, c = Sc[fine] - Sc[fine - RECENTE], Cc[fine] - Cc[fine - RECENTE]
    with np.errstate(all="ignore"):
        return np.where(c >= MINIMO, s / c, np.nan)


def esegui(log=print) -> dict:
    sc.ULTIMO_ANNO = sc.PUBBLICAZIONE = FINE - 364        # come la prova 138: l'archivio finisce a gennaio 2025
    pan = sc.pannello()
    ps = te.pannello_settimane(pan, log=lambda x: None, indicatori_si=False)
    somma, conta, mappa, coppie, mediana = novita(pan, log)
    lun = ps["lunedi"]
    idx = lun - pan["t0"]
    NV = segnale(somma, conta, idx)
    sig = ot.sigma_30(pan, idx)
    costo = sc.costi_moneta(pan["simboli"])
    btc = pd.Series(ps["R"][:, ps["simboli"].index("BTCUSDT")], index=lun)
    tieni = (lun >= se.INIZIO) & (lun <= FINE)
    U = ps["U"] & (lun <= FINE)[:, None]
    f5 = pd.read_csv(QUI.parent / "programma6" / "risultati_controllo_parita" / "settimane_F5.csv.gz", index_col=0)
    RIS.mkdir(exist_ok=True)

    def conto(D, verso=1.0):
        W = vq.pesi_banda(np.where(np.isfinite(sig) & U, verso * D, np.nan), U, sig)
        df = te.conto(W, ps["R"], ps["F"], costo)
        df.index = lun
        return df[df.index <= FINE], W
    df, W = conto(NV)
    df.to_csv(RIS / "settimane_NV.csv.gz")
    e = te.esame(df, btc, inizio=se.INIZIO, anni_pieni=(2021, 2022, 2023, 2024))
    valide = (np.isfinite(NV) & U)[tieni]
    e["monete_con_segnale_mediana"] = float(np.median(valide.sum(axis=1)))
    e["settimane_con_posizioni"] = int((np.abs(W[tieni]).sum(axis=1) > 0).sum())
    e["settimane"] = int(tieni.sum())
    c = df.index.intersection(f5.index)
    c = c[c >= se.INIZIO]
    e["correlazione_F5"] = float(np.corrcoef(df.loc[c, "netto"], f5.loc[c, "netto"])[0, 1])
    op, _ = conto(NV, -1.0)
    e["opposto_sharpe"] = te.numeri_settimana(op[op.index >= se.INIZIO]["netto"])["sharpe"]
    rng = np.random.default_rng(SEME)
    sh = []
    for _ in range(MESCOLATE):
        M = np.full_like(NV, np.nan)
        for k in range(NV.shape[0]):
            jj = np.flatnonzero(np.isfinite(NV[k]) & U[k])
            if len(jj):
                M[k, jj] = rng.permutation(NV[k, jj])
        dm, _ = conto(M)
        sh.append(te.numeri_settimana(dm[dm.index >= se.INIZIO]["netto"])["sharpe"])
    e["mescolato_sharpe_medio"], e["mescolato_sopra"] = float(np.mean(sh)), int(sum(1 for v in sh if v >= e["intero"]["sharpe"]))
    # la correlazione di rango fra il segnale e il volume dei 28 giorni prima
    V = np.nan_to_num(pan["quote_volume"])
    Vc = np.vstack([np.zeros((1, V.shape[1])), np.cumsum(V, axis=0)])
    fine = idx - RITARDO + 1
    vol = Vc[fine] - Vc[fine - RECENTE]
    cr = []
    for k in np.flatnonzero(tieni):
        jj = np.flatnonzero(np.isfinite(NV[k]) & U[k] & (vol[k] > 0))
        if len(jj) >= 10:
            cr.append(pd.Series(NV[k, jj]).rank().corr(pd.Series(np.log(vol[k, jj])).rank()))
    e["correlazione_volume"] = float(np.nanmean(cr)) if cr else None
    rivisto = ast.corretto_rivisto({**ast.serie_nuove(), NOME: df["netto"]}, {NOME: e["intero"]})
    r = rivisto["candidate"][NOME]
    e["sharpe_corretto"], e["t"], e["gruppi"] = r["corretto_con_aggiunta"], r["t"], rivisto["gruppi"]
    e["esito_esame"] = te.esito(e, e["sharpe_corretto"])
    anni = e.get("per_anno", {})
    e["regola_proprietario"] = bool(e["sharpe_corretto"] >= 0.90 and e["t"] > 3 and anni and all(v > 0 for v in anni.values()))
    regge = e["mescolato_sopra"] <= 1
    e["esito"] = e["esito_esame"] if regge else f"no: il segnale mescolato fa come quello vero ({e['esito_esame']})"
    (RIS / "esame.json").write_text(json.dumps({"coppie": coppie, "mediana_novita": mediana, "NV": e}, ensure_ascii=False, indent=1,
                                               default=str), encoding="utf-8")
    pc = lambda v: "—" if v is None or v != v else f"{100 * v:+.1f}%"  # noqa: E731
    i = e["intero"]
    righe = ["# Programma 7 — risultati dell'ottantatreesima prova (NV: le notizie nuove contro quelle ripetute)", "",
             "Regole in `OTTANTATREESIMA.md` (scritte prima). Dal 4 gennaio 2021 al 27 gennaio 2025, archivio della prova 138; long il quinto "
             "con le notizie più nuove, short il quinto con le più ripetute, come F5.", "",
             f"* Coppie articolo-moneta con la novità: {coppie}; novità mediana {mediana:.3f}; monete con il segnale, mediana "
             f"{e['monete_con_segnale_mediana']:.0f} a settimana; settimane con le posizioni {e['settimane_con_posizioni']} su {e['settimane']}.",
             f"* **NV: Sharpe {i['sharpe']:.2f}**, {pc(i['annuo'])} l'anno, volatilità {100 * i['volatilita']:.1f}%, discesa "
             f"{100 * i['discesa_max']:.1f}%; spese {100 * e['spese_annue']:.1f}% l'anno; lato long {pc(e['long_annuo'])}, short "
             f"{pc(e['short_annuo'])} l'anno.",
             "  * Per anno: " + ", ".join(f"{a} {pc(x)}" for a, x in e["per_anno"].items()) + ".",
             f"* Il segnale mescolato: Sharpe medio {e['mescolato_sharpe_medio']:.2f}, {e['mescolato_sopra']} su {MESCOLATE} sopra o pari a "
             f"quello vero; il verso opposto {e['opposto_sharpe']:.2f}.",
             f"* Per capire: correlazione di rango media fra la novità e il volume dei 28 giorni "
             f"{'—' if e['correlazione_volume'] is None else format(e['correlazione_volume'], '.2f')}; correlazione con F5 "
             f"{e['correlazione_F5']:.2f}.",
             f"* Sharpe corretto con l'aggiunta {e['sharpe_corretto']:.2f} ({e['gruppi']} gruppi); t {e['t']:.2f}; regola del proprietario: "
             f"{'sì' if e['regola_proprietario'] else 'no'}.", "",
             f"**Esito: {e['esito']}**."]
    testo = "\n".join(righe) + "\n"
    (QUI / "RISULTATI_OTTANTATREESIMA.md").write_text(testo, encoding="utf-8")
    log(testo)
    return {"NV": e}


if __name__ == "__main__":
    esegui(log=lambda x: print(x, flush=True))
    print("OTTANTATREESIMA FINITA", flush=True)
