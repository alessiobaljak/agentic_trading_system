"""Programma 6, cinquantatreesima prova (CINQUANTATREESIMA.md): F8, il funding dei 7 giorni di ogni moneta rispetto alle
sue 26 settimane prima (z): short sopra 1, long sotto −1; pesi 2 × (1/vol) / Σ(1/vol) dell'universo.

Uso: python3 -m research.programma6.cinquantatreesima
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
RIS = QUI / "risultati_cinquantatreesima"
SETTIMANE, MINIMO, SOGLIA = 26, 13, 1.0


def zeta(S7: np.ndarray) -> np.ndarray:
    """Settimane × monete: (S7 − media delle 26 settimane prima) / deviazione (almeno 13)."""
    df = pd.DataFrame(S7)
    prima = df.shift(1).rolling(SETTIMANE, min_periods=MINIMO)
    sd = prima.std()
    return ((df - prima.mean()) / sd.where(sd > 0)).to_numpy()


def pesi(Z: np.ndarray, U: np.ndarray, sig: np.ndarray) -> np.ndarray:
    W = np.zeros_like(Z)
    for k in range(Z.shape[0]):
        idx = np.flatnonzero(U[k] & np.isfinite(sig[k]) & (sig[k] > 0))
        if len(idx) < te.MIN_MONETE:
            continue
        inv = 1.0 / sig[k, idx]
        base = 2.0 * inv / inv.sum()
        z = Z[k, idx]
        W[k, idx] = np.where(z > SOGLIA, -base, np.where(z < -SOGLIA, base, 0.0))
    return W


def esegui(log=print) -> dict:
    pan = sc.pannello()
    ps = te.pannello_settimane(pan, log=lambda x: None, indicatori_si=False)
    lun = ps["lunedi"] - pan["t0"]
    sig = ot.sigma_30(pan, lun)
    W = pesi(zeta(se.funding_7(pan, lun)), ps["U"], sig)
    df = te.conto(W, ps["R"], ps["F"], sc.costi_moneta(ps["simboli"]))
    df.index = ps["lunedi"]
    RIS.mkdir(exist_ok=True)
    df.to_csv(RIS / "settimane_F8.csv.gz")
    btc = pd.Series(ps["R"][:, ps["simboli"].index("BTCUSDT")], index=ps["lunedi"])
    e = te.esame(df, btc, inizio=se.INIZIO, anni_pieni=se.ANNI_PIENI)
    dentro = ps["lunedi"] >= se.INIZIO
    e["long_medi"] = float((W[dentro] > 0).sum(axis=1).mean())
    e["short_medi"] = float((W[dentro] < 0).sum(axis=1).mean())
    e["netta_media"] = float(W[dentro].sum(axis=1).mean())
    f5 = pd.read_csv(QUI / "risultati_ventiquattresima" / "settimane_F5.csv.gz", index_col=0)["netto"]
    comuni = df.index[df.index >= se.INIZIO].intersection(f5.index)
    e["correlazione_F5"] = float(np.corrcoef(df.loc[comuni, "netto"], f5.loc[comuni])[0, 1])
    nuove = {f"49 {k}": pd.read_csv(QUI / "risultati_quarantanovesima" / f"settimane_{k}.csv.gz", index_col=0)["netto"] for k in ("X1", "X2")}
    nuove["51 F7"] = pd.read_csv(QUI / "risultati_cinquantunesima" / "settimane_F7.csv.gz", index_col=0)["netto"]
    nuove["52 B1"] = pd.read_csv(QUI / "risultati_cinquantaduesima" / "settimane_B1.csv.gz", index_col=0)["netto"]
    nuove["53 F8"] = df["netto"]
    r = ast.corretto_rivisto(nuove, {"53 F8": e["intero"]})
    c = r["candidate"]["53 F8"]
    e["sharpe_corretto"], e["t"], e["gruppo"], e["gruppi"] = c["corretto"], c["t"], c["gruppo"], r["gruppi"]
    e["esito"] = te.esito(e, e["sharpe_corretto"])
    (RIS / "esame.json").write_text(json.dumps(e, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    i = e["intero"]
    testo = "\n".join([
        "# Programma 6 — risultati della cinquantatreesima prova (F8: il funding di ogni moneta rispetto alla sua storia)", "",
        "Regole in `CINQUANTATREESIMA.md` (scritte prima).", "",
        f"* In media {e['long_medi']:.1f} long e {e['short_medi']:.1f} short; esposizione netta media {e['netta_media']:+.2f}; beta verso "
        f"il Bitcoin {e['beta_btc']:.2f}; correlazione con F5 {e['correlazione_F5']:.2f}.",
        f"* Sharpe {i['sharpe']:.2f}, {100 * i['annuo']:+.1f}% l'anno, volatilità {100 * i['volatilita']:.1f}%, discesa "
        f"{100 * i['discesa_max']:.1f}%; spese {100 * e['spese_annue']:.1f}% l'anno.",
        "* Per anno: " + ", ".join(f"{a} {100 * v:+.1f}%" for a, v in e["per_anno"].items()) + ".",
        f"* Sharpe corretto rivisto {e['sharpe_corretto']:.2f} ({e['gruppi']} gruppi); t dello Sharpe {e['t']:.2f}; gruppo: "
        + ", ".join(e["gruppo"]) + ".", "", f"**Esito: {e['esito']}**"]) + "\n"
    (QUI / "RISULTATI_CINQUANTATREESIMA.md").write_text(testo, encoding="utf-8")
    log(testo)
    return e


if __name__ == "__main__":
    esegui(log=lambda x: print(x, flush=True))
    print("CINQUANTATREESIMA FINITA", flush=True)
