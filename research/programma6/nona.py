"""Programma 6, nona prova (NONA.md): G1 (la quota di acquisti aggressivi dei 7 giorni prima) e G2 (il rendimento
giornaliero piu' alto dei 30 giorni prima) fra monete, long il quinto piu' basso e short il piu' alto, pesi secondo la
volatilita'; esame sulle 100 monete e conferma sulle 101-200 come l'ottava prova.

Uso: python3 -m research.programma6.nona
"""
from __future__ import annotations

import json
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

from research.programma6 import ottava as ot
from research.programma6 import seconda as sc
from research.programma6 import sesta as se
from research.programma6 import settima as st
from research.programma6 import terza as te
from research.programma6.motore import TAKER

QUI = Path(__file__).parent
RIS = QUI / "risultati_nona"
PROVE_PROGRAMMA = 29


def g1(pan: dict, lun_idx: np.ndarray) -> np.ndarray:
    """Quota del volume in USDT dei 7 giorni prima comprata a mercato (almeno 5 giorni con volume)."""
    V, B = pan["quote_volume"], pan["taker_buy_quote_volume"]
    out = np.full((len(lun_idx), V.shape[1]), np.nan)
    for k, m in enumerate(lun_idx):
        v, b = V[max(0, m - 7): m], B[max(0, m - 7): m]
        ok = np.isfinite(v) & np.isfinite(b) & (v > 0)
        sv, sb = np.where(ok, v, 0).sum(axis=0), np.where(ok, b, 0).sum(axis=0)
        with np.errstate(all="ignore"):
            out[k] = np.where((ok.sum(axis=0) >= 5) & (sv > 0), sb / sv, np.nan)
    return out


def g2(pan: dict, lun_idx: np.ndarray) -> np.ndarray:
    """Il rendimento giornaliero (chiusura su chiusura) piu' alto dei 30 giorni prima (almeno 20 giorni)."""
    C = pan["close"]
    with np.errstate(all="ignore"):
        r = np.vstack([np.full((1, C.shape[1]), np.nan), C[1:] / C[:-1] - 1])
    out = np.full((len(lun_idx), C.shape[1]), np.nan)
    for k, m in enumerate(lun_idx):
        f = r[max(0, m - 30): m]
        n = np.isfinite(f).sum(axis=0)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", RuntimeWarning)
            mx = np.nanmax(f, axis=0)
        out[k] = np.where(n >= 20, mx, np.nan)
    return out


def portafoglio(pan: dict, ps: dict, costo: np.ndarray, segnale) -> pd.DataFrame:
    lun_idx = ps["lunedi"] - pan["t0"]
    s = segnale(pan, lun_idx)
    sig = ot.sigma_30(pan, lun_idx)
    ct = np.where(np.isfinite(sig) & np.isfinite(s), -s, np.nan)
    Wt = te.pesi_portafoglio(ct, ps["U"], np.nan_to_num(1.0 / sig), True)
    df = te.conto(Wt, ps["R"], ps["F"], costo)
    df.index = ps["lunedi"]
    df["dal_funding"] = -df["funding"]
    return df


def _conferma(df2: pd.DataFrame) -> dict:
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
    return c


def esegui(log=print) -> dict:
    pan = sc.pannello()
    RIS.mkdir(exist_ok=True)
    jb = pan["simboli"].index("BTCUSDT")
    ps = te.pannello_settimane(pan, log=lambda x: None, indicatori_si=False)
    ps2 = te.pannello_settimane(pan, log=lambda x: None, da=100, a=200, indicatori_si=False)
    btc = pd.Series(ps["R"][:, jb], index=ps["lunedi"])
    f3 = pd.read_csv(QUI / "risultati_ottava" / "settimane_F3.csv.gz", index_col=0)["netto"]
    sr = sc.sharpe_prove()
    for v in ("C1", "C2", "C3"):
        sr.append(json.loads((te.RIS / f"{v}.json").read_text())["intero"]["sharpe"])
    for v in ("F1", "F2"):
        sr.append(json.loads((se.RIS / f"{v}.json").read_text())["intero"]["sharpe"])
    sr.append(json.loads((ot.RIS / "esame.json").read_text())["cento"]["intero"]["sharpe"])
    risultati = {}
    for nome, segnale in (("G1", g1), ("G2", g2)):
        df = portafoglio(pan, ps, sc.costi_moneta(ps["simboli"]), segnale)
        df.to_csv(RIS / f"settimane_{nome}.csv.gz")
        e = te.esame(df, btc, inizio=se.INIZIO, anni_pieni=se.ANNI_PIENI)
        d = df[df.index >= se.INIZIO]
        e["dal_funding_annuo"] = float(d["dal_funding"].mean() * 52)
        e["dal_prezzo_annuo"] = float(d["lordo"].mean() * 52)
        comuni = d.index.intersection(f3.index)
        e["correlazione_F3"] = float(np.corrcoef(d.loc[comuni, "netto"], f3.loc[comuni])[0, 1])
        risultati[nome] = e
        sr.append(e["intero"]["sharpe"])
    out = {}
    for nome, segnale in (("G1", g1), ("G2", g2)):
        e = risultati[nome]
        i = e["intero"]
        e["sharpe_corretto"] = te.sharpe_corretto(i["sharpe"], i["settimane"], i["asimmetria"], i["curtosi"], sr, 52)
        e["prove_nel_conto"] = len(sr)
        e["esito"] = te.esito(e, e["sharpe_corretto"])
        df2 = portafoglio(pan, ps2, np.full(len(ps2["simboli"]), TAKER + st.SCARTO), segnale)
        df2.to_csv(RIS / f"settimane_{nome}_101_200.csv.gz")
        c = _conferma(df2)
        out[nome] = {"cento": e, "conferma_101_200": c,
                     "esito": "VALIDA" if e["esito"] == "VALIDA" and c["esito"] == "CONFERMATA" else "non valida"}
        log(f"[nona] {nome}: cento {e['esito']}; 101-200 {c['esito']}")
    (RIS / "esame.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    return out


def rapporto() -> str:
    r = json.loads((RIS / "esame.json").read_text())
    righe = ["# Programma 6 — risultati della nona prova (acquisti aggressivi e biglietto della lotteria)", "",
             "Regole in `NONA.md` (scritte prima). Long il quinto meno affollato, short il più affollato, pesi secondo la "
             "volatilità, ogni lunedì; sulle 100 monete più scambiate dal 4 gennaio 2021 e, come conferma, sulle 101-200.", "",
             "| Segnale | Rendimento/anno | Sharpe | Intervallo (settimana) | Sharpe corretto | Anni positivi | Ultimo anno | "
             "Dal prezzo | Dal funding | Correlazione con F3 | 101-200: Sharpe, p | Esito |",
             "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for nome in ("G1", "G2"):
        e, c = r[nome]["cento"], r[nome]["conferma_101_200"]
        i = e["intero"]
        anni = sum(1 for x in e["per_anno"].values() if x > 0)
        righe.append(f"| {nome} | {100 * i['annuo']:+.1f}% | {i['sharpe']:.2f} | {100 * e['boot']['basso']:+.2f}%; "
                     f"{100 * e['boot']['alto']:+.2f}% | {e['sharpe_corretto']:.2f} | {anni}/{len(e['per_anno'])} | "
                     f"{100 * e['ultimo_anno']:+.1f}% | {100 * e['dal_prezzo_annuo']:+.1f}% | {100 * e['dal_funding_annuo']:+.1f}% | "
                     f"{e['correlazione_F3']:.2f} | {c['intero']['sharpe']:.2f}, {c['boot']['p']:.3f} | {e['esito']}; {c['esito']} |")
    testo = "\n".join(righe) + "\n"
    (QUI / "RISULTATI_NONA.md").write_text(testo, encoding="utf-8")
    return testo


if __name__ == "__main__":
    esegui(log=lambda x: print(x, flush=True))
    print(rapporto())
    print("NONA FINITA", flush=True)
