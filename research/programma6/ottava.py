"""Programma 6, ottava prova (OTTAVA.md): F3, il funding fra monete con i pesi inversamente proporzionali alla volatilita'
dei 30 giorni prima; esame sulle 100 monete piu' scambiate e conferma sulle monete 101-200.

Uso: python3 -m research.programma6.ottava
"""
from __future__ import annotations

import json
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

from research.programma6 import seconda as sc
from research.programma6 import sesta as se
from research.programma6 import settima as st
from research.programma6 import terza as te
from research.programma6.motore import TAKER

QUI = Path(__file__).parent
RIS = QUI / "risultati_ottava"
PROVE_PROGRAMMA = 27


def sigma_30(pan: dict, lun_idx: np.ndarray) -> np.ndarray:
    """Deviazione standard dei rendimenti giornalieri (chiusura su chiusura) dei 30 giorni prima di ogni lunedi'; NaN con
    meno di 20 giorni."""
    C = pan["close"]
    with np.errstate(all="ignore"):
        r = C[1:] / C[:-1] - 1
    r = np.vstack([np.full((1, C.shape[1]), np.nan), r])
    out = np.full((len(lun_idx), C.shape[1]), np.nan)
    for k, m in enumerate(lun_idx):
        f = r[max(0, m - 30): m]
        n = np.isfinite(f).sum(axis=0)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", RuntimeWarning)
            sd = np.nanstd(f, axis=0, ddof=1)
        out[k] = np.where((n >= 20) & (sd > 0), sd, np.nan)
    return out


def portafoglio_f3(pan: dict, ps: dict, costo: np.ndarray) -> pd.DataFrame:
    lun_idx = ps["lunedi"] - pan["t0"]
    S7 = se.funding_7(pan, lun_idx)
    sig = sigma_30(pan, lun_idx)
    ct = np.where(np.isfinite(sig), -S7, np.nan)
    Wt = te.pesi_portafoglio(ct, ps["U"], np.nan_to_num(1.0 / sig), True)
    df = te.conto(Wt, ps["R"], ps["F"], costo)
    df.index = ps["lunedi"]
    df["dal_funding"] = -df["funding"]
    return df


def esegui(log=print) -> dict:
    pan = sc.pannello()
    RIS.mkdir(exist_ok=True)
    jb = pan["simboli"].index("BTCUSDT")
    # 1. le 100 monete piu' scambiate
    ps = te.pannello_settimane(pan, log=lambda x: None, indicatori_si=False)
    df = portafoglio_f3(pan, ps, sc.costi_moneta(ps["simboli"]))
    df.to_csv(RIS / "settimane_F3.csv.gz")
    btc = pd.Series(ps["R"][:, jb], index=ps["lunedi"])
    e = te.esame(df, btc, inizio=se.INIZIO, anni_pieni=se.ANNI_PIENI)
    d = df[df.index >= se.INIZIO]
    e["dal_funding_annuo"] = float(d["dal_funding"].mean() * 52)
    e["dal_prezzo_annuo"] = float(d["lordo"].mean() * 52)
    d20 = df[(df.index < se.INIZIO) & (df["monete"] > 0)]
    e["settimane_2020"] = {"settimane": int(len(d20)), "media": float(d20["netto"].mean()) if len(d20) else float("nan"),
                           "funding": float(-d20["funding"].mean()) if len(d20) else float("nan"),
                           "prezzo": float(d20["lordo"].mean()) if len(d20) else float("nan")}
    sr = sc.sharpe_prove()
    for v in ("C1", "C2", "C3"):
        sr.append(json.loads((te.RIS / f"{v}.json").read_text())["intero"]["sharpe"])
    for v in ("F1", "F2"):
        sr.append(json.loads((se.RIS / f"{v}.json").read_text())["intero"]["sharpe"])
    sr.append(e["intero"]["sharpe"])
    i = e["intero"]
    e["sharpe_corretto"] = te.sharpe_corretto(i["sharpe"], i["settimane"], i["asimmetria"], i["curtosi"], sr, 52)
    e["prove_nel_conto"] = len(sr)
    e["esito"] = te.esito(e, e["sharpe_corretto"])
    # 2. conferma sulle monete 101-200, scarto 0,10%
    ps2 = te.pannello_settimane(pan, log=lambda x: None, da=100, a=200, indicatori_si=False)
    df2 = portafoglio_f3(pan, ps2, np.full(len(ps2["simboli"]), TAKER + st.SCARTO))
    df2.to_csv(RIS / "settimane_F3_101_200.csv.gz")
    d2 = df2[(df2.index >= se.INIZIO) & (df2["monete"] > 0)]
    date = pd.to_datetime(d2.index.to_numpy() * 86400, unit="s")
    c = {"settimane_operate": int(len(d2)), "dal": sc.data(int(d2.index.min())) if len(d2) else "",
         "intero": te.numeri_settimana(d2["netto"]), "boot": sc.bootstrap_blocchi(d2["netto"].to_numpy(), blocco=4),
         "costi_doppi": float(d2["netto_doppio"].mean()), "dal_funding_annuo": float(d2["dal_funding"].mean() * 52),
         "dal_prezzo_annuo": float(d2["lordo"].mean() * 52), "spese_annue": float(d2["spese"].mean() * 52),
         "per_anno": {int(a): {"settimane": int((date.year == a).sum()), "annuo": float(d2["netto"][date.year == a].mean() * 52)}
                      for a in sorted(set(date.year))}}
    u = d2[d2.index >= sc.ULTIMO_ANNO]
    c["ultimo_anno"] = float(u["netto"].mean() * 52) if len(u) else float("nan")
    c["senza_5_migliori"] = float(d2["netto"].sort_values(ascending=False).iloc[5:].mean())
    c["esito"] = st.esito(c)
    out = {"cento": e, "conferma_101_200": c,
           "esito": "VALIDA" if e["esito"] == "VALIDA" and c["esito"] == "CONFERMATA" else "non valida"}
    (RIS / "esame.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    log(f"[ottava] cento: {e['esito']}; 101-200: {c['esito']}")
    return out


def rapporto() -> str:
    r = json.loads((RIS / "esame.json").read_text())
    e, c = r["cento"], r["conferma_101_200"]
    i, i2 = e["intero"], c["intero"]
    pa = e["per_anno"]
    righe = ["# Programma 6 — risultati dell'ottava prova (F3: il funding fra monete con i pesi secondo la volatilità)", "",
             "Regole in `OTTAVA.md` (scritte prima).", "", "## 1. Le 100 monete più scambiate (dal 4 gennaio 2021)", "",
             f"* {100 * i['annuo']:+.1f}% l'anno, volatilità {100 * i['volatilita']:.1f}%, **Sharpe {i['sharpe']:.2f}**, discesa "
             f"massima {100 * i['discesa_max']:.1f}%; media settimanale {100 * e['boot']['media']:+.3f}% (intervallo "
             f"{100 * e['boot']['basso']:+.3f}; {100 * e['boot']['alto']:+.3f}).",
             f"* Sharpe corretto **{e['sharpe_corretto']:.2f}** con {e['prove_nel_conto']} prove; dal funding "
             f"{100 * e['dal_funding_annuo']:+.1f}% l'anno, dal prezzo {100 * e['dal_prezzo_annuo']:+.1f}%; a costi doppi "
             f"{100 * e['costi_doppi']:+.3f}% a settimana; in più del Bitcoin {100 * e['extra_btc_annuo']:+.1f}% l'anno.",
             "* Per anno: " + ", ".join(f"{a} {100 * v:+.1f}%" for a, v in pa.items()) + f"; ultimo anno {100 * e['ultimo_anno']:+.1f}%.",
             f"* Settimane del 2020 (senza condizione): {e['settimane_2020']['settimane']}, media "
             f"{100 * e['settimane_2020']['media']:+.3f}% a settimana (funding {100 * e['settimane_2020']['funding']:+.3f}%, prezzo "
             f"{100 * e['settimane_2020']['prezzo']:+.3f}%).",
             f"* **Esito: {e['esito']}**", "", "## 2. Conferma sulle monete 101-200 (scarto 0,10%)", "",
             f"* {c['settimane_operate']} settimane dal {c['dal']}: {100 * i2['annuo']:+.1f}% l'anno, Sharpe {i2['sharpe']:.2f}; "
             f"media settimanale {100 * c['boot']['media']:+.3f}% (intervallo {100 * c['boot']['basso']:+.3f}; "
             f"{100 * c['boot']['alto']:+.3f}, p {c['boot']['p']:.4f}).",
             f"* Dal funding {100 * c['dal_funding_annuo']:+.1f}% l'anno, dal prezzo {100 * c['dal_prezzo_annuo']:+.1f}%, spese "
             f"{100 * c['spese_annue']:.1f}%; ultimo anno {100 * c['ultimo_anno']:+.1f}%.",
             "* Per anno: " + ", ".join(f"{a} {100 * v['annuo']:+.1f}% ({v['settimane']})" for a, v in c["per_anno"].items()) + ".",
             f"* **Esito: {c['esito']}**", "", f"**F3: {r['esito']}**"]
    testo = "\n".join(righe) + "\n"
    (QUI / "RISULTATI_OTTAVA.md").write_text(testo, encoding="utf-8")
    return testo


if __name__ == "__main__":
    esegui(log=lambda x: print(x, flush=True))
    print(rapporto())
    print("OTTAVA FINITA", flush=True)
