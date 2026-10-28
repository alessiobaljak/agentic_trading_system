"""Programma 7, cinquantasettesima prova (CINQUANTASETTESIMA.md): CU, la crescita degli utenti a settimana come F5. Il segnale del
lunedi' l e' la crescita degli indirizzi con saldo (CoinMetrics community, AdrBalCnt) dal giorno l-9 al giorno l-2; scartata se oltre il
50%. Long il quinto con la crescita piu' alta, short il piu' basso, banda 20/40.

Uso: python3 -m research.programma7.cinquantasettesima
"""
from __future__ import annotations

import json
import time
import urllib.parse
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
from research.programma7 import cinquantaquattresima as vu

QUI = Path(__file__).parent
RIS = QUI / "risultati_cinquantasettesima"
METRICA, TETTO = "AdrBalCnt", 0.50


def attivi(simboli) -> dict:
    d = vu._get(f"{vu.API}/catalog/asset-metrics?metrics={METRICA}")["data"]
    out = {}
    for a in sorted(next(f for f in d[0]["frequencies"] if f["frequency"] == "1d")["assets"]):
        if "_" in a:
            continue
        p = an.perpetuo(a.upper(), simboli)
        if p:
            out[p] = a
    return out


def serie(asset: str) -> pd.Series:
    f = vu.DATI / f"{asset}_saldo.csv.gz"
    if f.exists():
        return pd.read_csv(f, index_col=0).iloc[:, 0]
    q = urllib.parse.urlencode({"assets": asset, "metrics": METRICA, "frequency": "1d", "start_time": "2020-12-01", "page_size": 10000})
    url, righe = f"{vu.API}/timeseries/asset-metrics?{q}", []
    while url:
        d = vu._get(url)
        if not d:
            break
        righe += d.get("data", [])
        url = d.get("next_page_url")
        time.sleep(0.3)
    df = pd.DataFrame(righe)
    if df.empty or METRICA not in df:
        s = pd.Series(dtype=float, name=METRICA)
    else:
        df["giorno"] = pd.to_datetime(df["time"]).dt.tz_localize(None).astype("int64") // 86_400_000_000_000
        s = pd.to_numeric(df.set_index("giorno")[METRICA], errors="coerce")
    vu.DATI.mkdir(parents=True, exist_ok=True)
    s.to_frame(METRICA).to_csv(f)
    return s


def segnale(pan: dict, mappa: dict, lun: np.ndarray) -> np.ndarray:
    T, S = pan["close"].shape
    t0 = pan["t0"]
    ct = np.full((len(lun), S), np.nan)
    for s, a in mappa.items():
        x = serie(a)
        if x.empty:
            continue
        j = pan["simboli"].index(s)
        v = x.reindex(np.arange(t0, t0 + T)).to_numpy()
        for k, l in enumerate(lun):
            i = l - t0
            if i - 9 < 0 or i - 2 >= T:
                continue
            a2, a9 = v[i - 2], v[i - 9]
            if np.isfinite(a2) and np.isfinite(a9) and a9 > 0:
                g = a2 / a9 - 1
                if abs(g) <= TETTO:
                    ct[k, j] = g
    return ct


def esegui(log=print) -> dict:
    pan = sc.pannello()
    ps = te.pannello_settimane(pan, log=lambda x: None, indicatori_si=False)
    assert ps["simboli"] == pan["simboli"]
    mappa = attivi(pan["simboli"])
    log(f"[cinquantasettesima] {len(mappa)} monete con il dato e il perpetuo; scarico")
    lun = ps["lunedi"]
    ct = segnale(pan, mappa, lun)
    sig = ot.sigma_30(pan, lun - pan["t0"])
    costo = sc.costi_moneta(pan["simboli"])
    btc = pd.Series(ps["R"][:, ps["simboli"].index("BTCUSDT")], index=lun)
    out = {}
    RIS.mkdir(exist_ok=True)
    for nome, verso in (("CU", 1.0), ("CU opposto", -1.0)):
        W = vq.pesi_banda(np.where(np.isfinite(sig), verso * ct, np.nan), ps["U"], sig)
        df = te.conto(W, ps["R"], ps["F"], costo)
        df.index = lun
        df.to_csv(RIS / f"settimane_{nome.replace(' ', '_')}.csv.gz")
        out[nome] = te.esame(df, btc, inizio=se.INIZIO, anni_pieni=se.ANNI_PIENI)
        if nome == "CU":
            df_cu, W_cu = df, W
    e = out["CU"]
    rivisto = ast.corretto_rivisto({**ast.serie_nuove(), "119 CU": df_cu["netto"]}, {"119 CU": e["intero"]})
    r = rivisto["candidate"]["119 CU"]
    e["sharpe_corretto"], e["t"], e["gruppi"] = r["corretto_con_aggiunta"], r["t"], rivisto["gruppi"]
    e["esito"] = te.esito(e, e["sharpe_corretto"])
    dal = lun >= se.INIZIO
    for nome, f in (("F5", QUI.parent / "programma6" / "risultati_controllo_parita" / "settimane_F5.csv.gz"),
                    ("VU", QUI / "risultati_cinquantaquattresima" / "settimane_VU.csv.gz")):
        x = pd.read_csv(f, index_col=0)["netto"]
        c = df_cu.index.intersection(x.index)
        c = c[c >= se.INIZIO]
        e[f"correlazione_{nome}"] = float(np.corrcoef(df_cu.loc[c, "netto"], x.loc[c])[0, 1])
    e["monete_con_segnale_mediana"] = float(np.median((np.isfinite(ct) & ps["U"])[dal].sum(axis=1)))
    e["settimane_con_posizioni"], e["settimane"] = int((np.abs(W_cu[dal]).sum(axis=1) > 0).sum()), int(dal.sum())
    anni = e.get("per_anno", {})
    e["regola_proprietario"] = bool(e["sharpe_corretto"] >= 0.90 and e["t"] > 3 and anni and all(v > 0 for v in anni.values()))
    (RIS / "esame.json").write_text(json.dumps(out, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    i, op = e["intero"], out["CU opposto"]["intero"]
    testo = "\n".join([
        "# Programma 7 — risultati della cinquantasettesima prova (CU: la crescita degli utenti, a settimana)", "",
        "Regole in `CINQUANTASETTESIMA.md` (scritte prima). Dal 4 gennaio 2021, dati di CoinMetrics community e di Binance.", "",
        f"* {len(mappa)} monete con il dato e il perpetuo; con il segnale nell'universo, mediana {e['monete_con_segnale_mediana']:.0f} a "
        f"settimana; settimane con le posizioni {e['settimane_con_posizioni']} su {e['settimane']}.",
        f"* **CU: Sharpe {i['sharpe']:.2f}**, {100 * i['annuo']:+.1f}% l'anno, volatilità {100 * i['volatilita']:.1f}%, discesa "
        f"{100 * i['discesa_max']:.1f}%; spese {100 * e['spese_annue']:.1f}% l'anno.",
        "* Per anno: " + ", ".join(f"{a} {100 * v:+.1f}%" for a, v in e["per_anno"].items()) + ".",
        f"* Il verso opposto: Sharpe {op['sharpe']:.2f}, {100 * op['annuo']:+.1f}% l'anno.",
        f"* Correlazione con F5 {e['correlazione_F5']:.2f}, con la prova 116 {e['correlazione_VU']:.2f}.",
        f"* Sharpe corretto con l'aggiunta {e['sharpe_corretto']:.2f} ({e['gruppi']} gruppi); t {e['t']:.2f}; regola del proprietario: "
        f"{'sì' if e['regola_proprietario'] else 'no'}.", "",
        f"**Esito: {e['esito']}**"]) + "\n"
    (QUI / "RISULTATI_CINQUANTASETTESIMA.md").write_text(testo, encoding="utf-8")
    log(testo)
    return out


if __name__ == "__main__":
    esegui(log=lambda x: print(x, flush=True))
    print("CINQUANTASETTESIMA FINITA", flush=True)
