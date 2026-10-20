"""Programma 6, ventiquattresima prova (VENTIQUATTRESIMA.md): F5, il segnale di F3 (−funding dei 7 giorni) con la banda:
si entra fra il 20% piu' alto (long) o piu' basso (short) e si esce solo sotto il 40%. Pesi secondo la volatilita'.

Uso: python3 -m research.programma6.ventiquattresima
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from research.programma6 import diciottesima as di
from research.programma6 import ottava as ot
from research.programma6 import seconda as sc
from research.programma6 import sesta as se
from research.programma6 import terza as te

QUI = Path(__file__).parent
RIS = QUI / "risultati_ventiquattresima"
ENTRA, RESTA = 0.20, 0.40


def pesi_banda(ct: np.ndarray, U: np.ndarray, sig: np.ndarray) -> np.ndarray:
    W, S = ct.shape
    out = np.zeros((W, S))
    lunghi, corti = set(), set()
    for k in range(W):
        idx = np.flatnonzero(U[k] & np.isfinite(ct[k]) & np.isfinite(sig[k]) & (sig[k] > 0))
        if len(idx) < te.MIN_MONETE:
            lunghi, corti = set(), set()
            continue
        pr = pd.Series(ct[k, idx]).rank(pct=True).to_numpy()
        rango = dict(zip(idx.tolist(), pr))
        lunghi = {j for j in lunghi if rango.get(j, 0) >= 1 - RESTA} | {j for j, p in rango.items() if p > 1 - ENTRA}
        corti = {j for j in corti if rango.get(j, 1) <= RESTA} | {j for j, p in rango.items() if p <= ENTRA}
        for lato, segno in ((sorted(lunghi), 1.0), (sorted(corti), -1.0)):
            if lato:
                inv = 1.0 / sig[k, lato]
                out[k, lato] = segno * inv / inv.sum()
    return out


def esegui(log=print) -> dict:
    pan = sc.pannello()
    ps = te.pannello_settimane(pan, log=lambda x: None, indicatori_si=False)
    lun = ps["lunedi"] - pan["t0"]
    sig = ot.sigma_30(pan, lun)
    ct = np.where(np.isfinite(sig), -se.funding_7(pan, lun), np.nan)
    costo = sc.costi_moneta(ps["simboli"])
    Wt = pesi_banda(ct, ps["U"], sig)
    df = te.conto(Wt, ps["R"], ps["F"], costo)
    df.index = ps["lunedi"]
    RIS.mkdir(exist_ok=True)
    df.to_csv(RIS / "settimane_F5.csv.gz")
    jb = ps["simboli"].index("BTCUSDT")
    btc = pd.Series(ps["R"][:, jb], index=ps["lunedi"])
    e = te.esame(df, btc, inizio=se.INIZIO, anni_pieni=se.ANNI_PIENI)
    d = df[df.index >= se.INIZIO]
    e["dal_funding_annuo"] = float(-d["funding"].mean() * 52)
    e["dal_prezzo_annuo"] = float(d["lordo"].mean() * 52)
    lati = Wt[ps["lunedi"] >= se.INIZIO]
    e["monete_per_lato"] = {"long": float((lati > 0).sum(axis=1).mean()), "short": float((lati < 0).sum(axis=1).mean())}
    f3 = ot.portafoglio_f3(pan, ps, costo)
    e3 = te.esame(f3, btc, inizio=se.INIZIO, anni_pieni=se.ANNI_PIENI)
    e["F3_stessi_dati"] = {"sharpe": e3["intero"]["sharpe"], "annuo": e3["intero"]["annuo"], "giro_medio": e3["giro_medio"],
                           "spese_annue": e3["spese_annue"]}
    c = d.index.intersection(f3.index)
    e["correlazione_F3"] = float(np.corrcoef(d.loc[c, "netto"], f3.loc[c, "netto"])[0, 1])
    sr = di.prove_fino_alla_diciassettesima()
    for n, f in (("N1", "risultati_diciottesima"), ("N2", "risultati_diciottesima"), ("P1", "risultati_diciannovesima"),
                 ("P2", "risultati_diciannovesima"), ("S1", "risultati_ventesima"), ("S2", "risultati_ventesima")):
        sr.append(json.loads((QUI / f / "esame.json").read_text())[n]["intero"]["sharpe"])
    f23 = QUI / "risultati_ventitreesima" / "esame.json"
    if f23.exists():
        sr.append(json.loads(f23.read_text())["intero"]["sharpe"])
    sr.append(e["intero"]["sharpe"])
    i = e["intero"]
    e["sharpe_corretto"] = te.sharpe_corretto(i["sharpe"], i["settimane"], i["asimmetria"], i["curtosi"], sr, 52)
    e["prove_nel_conto"] = len(sr)
    e["esito"] = te.esito(e, e["sharpe_corretto"])
    (RIS / "esame.json").write_text(json.dumps(e, ensure_ascii=False, indent=1), encoding="utf-8")
    pa, g3 = e["per_anno"], e["F3_stessi_dati"]
    testo = "\n".join([
        "# Programma 6 — risultati della ventiquattresima prova (F5: F3 con la banda, entrata al 20% e uscita al 40%)", "",
        "Regole in `VENTIQUATTRESIMA.md` (scritte prima). Le 100 monete più scambiate, dal 4 gennaio 2021, dati corretti del "
        "20 ottobre.", "",
        f"* {100 * i['annuo']:+.1f}% l'anno, volatilità {100 * i['volatilita']:.1f}%, **Sharpe {i['sharpe']:.2f}**, discesa massima "
        f"{100 * i['discesa_max']:.1f}%; media settimanale {100 * e['boot']['media']:+.3f}% (intervallo "
        f"{100 * e['boot']['basso']:+.3f}; {100 * e['boot']['alto']:+.3f}).",
        "* Per anno: " + ", ".join(f"{a} {100 * v:+.1f}%" for a, v in pa.items()) + f"; ultimo anno {100 * e['ultimo_anno']:+.1f}%.",
        f"* Giro medio {e['giro_medio']:.2f} a settimana, spese {100 * e['spese_annue']:.1f}% l'anno; monete per lato "
        f"{e['monete_per_lato']['long']:.1f} long, {e['monete_per_lato']['short']:.1f} short; dal funding "
        f"{100 * e['dal_funding_annuo']:+.1f}%, dal prezzo {100 * e['dal_prezzo_annuo']:+.1f}%.",
        f"* F3 sugli stessi dati: Sharpe {g3['sharpe']:.2f}, {100 * g3['annuo']:+.1f}% l'anno, giro {g3['giro_medio']:.2f}, spese "
        f"{100 * g3['spese_annue']:.1f}%; correlazione con F3 {e['correlazione_F3']:.2f}.",
        f"* Sharpe corretto {e['sharpe_corretto']:.2f} con {e['prove_nel_conto']} prove.", "",
        f"**Esito: {e['esito']}**"]) + "\n"
    (QUI / "RISULTATI_VENTIQUATTRESIMA.md").write_text(testo, encoding="utf-8")
    log(testo)
    return e


if __name__ == "__main__":
    esegui(log=lambda x: print(x, flush=True))
    print("VENTIQUATTRESIMA FINITA", flush=True)
