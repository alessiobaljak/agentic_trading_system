"""Programma 7, quinta prova (QUINTA.md): F5T e G1T, F5 e G1 con il tetto del 10% per moneta in ogni lato.

Uso: python3 -m research.programma7.quinta
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from research.programma6 import asticella as ast
from research.programma6 import cinquantaseiesima as cs
from research.programma6 import ottava as ot
from research.programma6 import seconda as sc
from research.programma6 import sesta as se
from research.programma6 import terza as te
from research.programma6 import ventiquattresima as vq
from research.programma7 import prima as pr

QUI = Path(__file__).parent
RIS = QUI / "risultati_quinta"
TETTO = 0.10


def con_tetto(pesi: np.ndarray, tetto: float = TETTO) -> np.ndarray:
    """I pesi di un lato (positivi, somma 1) con nessuno sopra ``tetto``: l'eccesso va agli altri in proporzione, finche'
    nessuno supera; con meno di 1/tetto monete, pesi uguali."""
    w = np.asarray(pesi, float).copy()
    n = len(w)
    if n == 0:
        return w
    if n * tetto < 1:
        return np.full(n, 1.0 / n)
    fermi = np.zeros(n, dtype=bool)
    for _ in range(n):
        sopra = (w > tetto + 1e-12) & ~fermi
        if not sopra.any():
            break
        fermi |= sopra
        resto = 1.0 - tetto * fermi.sum()
        liberi = ~fermi
        w[fermi] = tetto
        w[liberi] = w[liberi] / w[liberi].sum() * resto
    return w


def applica_tetto(W: np.ndarray, tetto: float = TETTO) -> np.ndarray:
    out = W.copy()
    for k in range(W.shape[0]):
        for segno in (1.0, -1.0):
            lato = np.flatnonzero(np.sign(W[k]) == segno)
            if len(lato):
                out[k, lato] = segno * con_tetto(np.abs(W[k, lato]) / np.abs(W[k, lato]).sum(), tetto)
    return out


def esegui(log=print) -> dict:
    pan = sc.pannello()
    ps = te.pannello_settimane(pan, log=lambda x: None, indicatori_si=False)
    costo = sc.costi_moneta(pan["simboli"])
    btc = pd.Series(ps["R"][:, ps["simboli"].index("BTCUSDT")], index=ps["lunedi"])
    # F5T, settimanale a mercato
    lun = ps["lunedi"] - pan["t0"]
    sig = ot.sigma_30(pan, lun)
    W5 = vq.pesi_banda(np.where(np.isfinite(sig), -se.funding_7(pan, lun), np.nan), ps["U"], sig)
    W5t = applica_tetto(W5)
    f5 = te.conto(W5, ps["R"], ps["F"], costo)
    f5t = te.conto(W5t, ps["R"], ps["F"], costo)
    f5.index = f5t.index = ps["lunedi"]
    # G1T, giornaliera con gli ordini limite
    giorni = np.arange(se.INIZIO, pr.FINE, dtype=np.int64)
    idx = giorni - pan["t0"]
    Ud = pr.universo_del_giorno(giorni, ps["lunedi"], ps["U"])
    sigd = ot.sigma_30(pan, idx)
    Wg = applica_tetto(vq.pesi_banda(np.where(np.isfinite(sigd), -se.funding_7(pan, idx), np.nan), Ud, sigd))
    R, F = sc.rendimenti(pan)[idx], np.nan_to_num(pan["funding"][idx])
    g = te.conto(Wg, R, F, costo)
    g["spese"] = cs.spese_a_limite(Wg, R, giorni, pan["simboli"], costo)[0]
    g["netto"] = g["lordo"] - g["spese"] - g["funding"]
    g["netto_doppio"] = g["lordo"] - 2 * g["spese"] - g["funding"]
    g1t = pr.per_settimana(g, giorni)
    g1 = pd.read_csv(QUI / "risultati_prima" / "settimane_G1.csv.gz", index_col=0)
    RIS.mkdir(exist_ok=True)
    f5t.to_csv(RIS / "settimane_F5T.csv.gz")
    g1t.to_csv(RIS / "settimane_G1T.csv.gz")
    out = {}
    for nome, df, base, inizio in (("F5T", f5t, f5, se.INIZIO), ("G1T", g1t, g1, se.INIZIO)):
        fine = df.index < pr.FINE
        e = te.esame(df[fine], btc, inizio=inizio, anni_pieni=se.ANNI_PIENI)
        eb = te.esame(base[base.index < pr.FINE], btc, inizio=inizio, anni_pieni=se.ANNI_PIENI)
        e["senza_tetto"] = {k: eb["intero"][k] for k in ("sharpe", "annuo", "discesa_max")}
        out[nome] = e
    Wmax = {"F5": float(np.abs(W5).max()), "F5T": float(np.abs(W5t).max()), "G1T": float(np.abs(Wg).max())}
    chiavi = {"F5T": "61 F5T", "G1T": "61 G1T"}
    nuove = {**ast.serie_nuove(), "57 G1": g1["netto"], "61 F5T": f5t["netto"], "61 G1T": g1t["netto"]}
    rivisto = ast.corretto_rivisto(nuove, {chiavi[n]: out[n]["intero"] for n in out})
    for n in out:
        r = rivisto["candidate"][chiavi[n]]
        out[n]["sharpe_corretto"], out[n]["t"] = r["corretto_con_aggiunta"], r["t"]
        out[n]["esito"] = te.esito(out[n], out[n]["sharpe_corretto"])
        st = out[n]["senza_tetto"]
        out[n]["il_bot_prende_il_tetto"] = bool(out[n]["intero"]["sharpe"] >= st["sharpe"] - 0.05
                                                and out[n]["intero"]["discesa_max"] >= st["discesa_max"])
    out["peso_massimo"] = Wmax
    (RIS / "esame.json").write_text(json.dumps(out, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    righe = ["# Programma 7 — risultati della quinta prova (il tetto del 10% per moneta: F5T, G1T)", "",
             "Regole in `QUINTA.md` (scritte prima).", "",
             f"Peso massimo di una moneta sul capitale di un lato: F5 {100 * Wmax['F5']:.1f}%, F5T {100 * Wmax['F5T']:.1f}%, "
             f"G1T {100 * Wmax['G1T']:.1f}%.", "",
             "| Strategia | Sharpe | l'anno | discesa | senza il tetto: Sharpe, l'anno, discesa | Sharpe corretto | t | il bot prende il tetto |",
             "|---|---|---|---|---|---|---|---|"]
    for n in ("F5T", "G1T"):
        i, st = out[n]["intero"], out[n]["senza_tetto"]
        righe.append(f"| {n} | {i['sharpe']:.2f} | {100 * i['annuo']:+.1f}% | {100 * i['discesa_max']:.1f}% | {st['sharpe']:.2f}, "
                     f"{100 * st['annuo']:+.1f}%, {100 * st['discesa_max']:.1f}% | {out[n]['sharpe_corretto']:.2f} | {out[n]['t']:.2f} | "
                     f"{'sì' if out[n]['il_bot_prende_il_tetto'] else 'no'} |")
    righe += [""] + [f"* {n} per anno: " + ", ".join(f"{a} {100 * v:+.1f}%" for a, v in out[n]["per_anno"].items()) for n in ("F5T", "G1T")]
    righe += ["", f"**Esito**: F5T {out['F5T']['esito']}; G1T {out['G1T']['esito']}."]
    testo = "\n".join(righe) + "\n"
    (QUI / "RISULTATI_QUINTA.md").write_text(testo, encoding="utf-8")
    log(testo)
    return out


if __name__ == "__main__":
    esegui(log=lambda x: print(x, flush=True))
    print("QUINTA FINITA", flush=True)
