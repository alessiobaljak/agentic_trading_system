"""Programma 7, cinquantaquattresima prova (CINQUANTAQUATTRESIMA.md): VU, il valore misurato con gli utenti a settimana come F5.
Long il quinto con piu' indirizzi attivi (media dei giorni l-8..l-2) per dollaro di valore (giorno l-2), short il quinto con meno,
banda 20/40, pesi secondo l'inverso della volatilita'. Dati: CoinMetrics community.

Uso: python3 -m research.programma7.cinquantaquattresima
"""
from __future__ import annotations

import json
import time
import urllib.parse
import urllib.request
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
RADICE = QUI.parents[1]
RIS = QUI / "risultati_cinquantaquattresima"
DATI = RADICE / "research" / "data" / "coinmetrics"
API = "https://community-api.coinmetrics.io/v4"
METRICHE = ("AdrActCnt", "CapMrktCurUSD")


def _get(url: str):
    for k in range(6):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "ricerca/1.0"}), timeout=120) as r:
                return json.load(r)
        except Exception:  # noqa: BLE001
            time.sleep(2 * (k + 1))
    return None


def attivi(simboli) -> dict:
    """Perpetuo → sigla di CoinMetrics, per le monete con tutte e due le metriche gratis (senza le copie con il trattino basso)."""
    d = _get(f"{API}/catalog/asset-metrics?metrics={','.join(METRICHE)}")["data"]
    insiemi = [set(next(f for f in m["frequencies"] if f["frequency"] == "1d")["assets"]) for m in d]
    out = {}
    for a in sorted(set.intersection(*insiemi)):
        if "_" in a:
            continue
        p = an.perpetuo(a.upper(), simboli)
        if p:
            out[p] = a
    return out


def serie(asset: str) -> pd.DataFrame:
    """Le due metriche giornaliere di una moneta (indice = giorno dall'epoca), salvate in ``DATI``."""
    f = DATI / f"{asset}.csv.gz"
    if f.exists():
        return pd.read_csv(f, index_col=0)
    q = urllib.parse.urlencode({"assets": asset, "metrics": ",".join(METRICHE), "frequency": "1d",
                                "start_time": "2020-12-01", "page_size": 10000})
    url, righe = f"{API}/timeseries/asset-metrics?{q}", []
    while url:
        d = _get(url)
        if not d:
            break
        righe += d.get("data", [])
        url = d.get("next_page_url")
        time.sleep(0.3)
    df = pd.DataFrame(righe)
    if df.empty:
        out = pd.DataFrame(columns=list(METRICHE))
    else:
        df["giorno"] = pd.to_datetime(df["time"]).dt.tz_localize(None).astype("int64") // 86_400_000_000_000
        out = df.set_index("giorno")[[m for m in METRICHE if m in df]].apply(pd.to_numeric, errors="coerce")
    DATI.mkdir(parents=True, exist_ok=True)
    out.to_csv(f)
    return out


def segnale(pan: dict, mappa: dict, lun: np.ndarray) -> np.ndarray:
    """ct[k, j]: media degli indirizzi attivi dei giorni l-8..l-2 divisa per il valore del giorno l-2 (NaN se manca)."""
    T, S = pan["close"].shape
    t0 = pan["t0"]
    ct = np.full((len(lun), S), np.nan)
    for s, a in mappa.items():
        x = serie(a)
        if x.empty or "AdrActCnt" not in x or "CapMrktCurUSD" not in x:
            continue
        j = pan["simboli"].index(s)
        ad = x["AdrActCnt"].reindex(np.arange(t0, t0 + T)).to_numpy()
        cap = x["CapMrktCurUSD"].reindex(np.arange(t0, t0 + T)).to_numpy()
        for k, l in enumerate(lun):
            i = l - t0
            if i - 8 < 0 or i - 2 >= T:
                continue
            blocco = ad[i - 8:i - 1]
            c = cap[i - 2]
            if np.isfinite(blocco).sum() >= 5 and np.isfinite(c) and c > 0:
                ct[k, j] = np.nanmean(blocco) / c
    return ct


def esegui(log=print) -> dict:
    pan = sc.pannello()
    ps = te.pannello_settimane(pan, log=lambda x: None, indicatori_si=False)
    assert ps["simboli"] == pan["simboli"]
    mappa = attivi(pan["simboli"])
    log(f"[cinquantaquattresima] {len(mappa)} monete con i dati di CoinMetrics e il perpetuo; scarico")
    lun = ps["lunedi"]
    idx = lun - pan["t0"]
    ct = segnale(pan, mappa, lun)
    sig = ot.sigma_30(pan, idx)
    costo = sc.costi_moneta(pan["simboli"])
    btc = pd.Series(ps["R"][:, ps["simboli"].index("BTCUSDT")], index=lun)
    out = {}
    for nome, verso in (("VU", 1.0), ("VU opposto", -1.0)):
        W = vq.pesi_banda(np.where(np.isfinite(sig), verso * ct, np.nan), ps["U"], sig)
        df = te.conto(W, ps["R"], ps["F"], costo)
        df.index = lun
        RIS.mkdir(exist_ok=True)
        df.to_csv(RIS / f"settimane_{nome.replace(' ', '_')}.csv.gz")
        out[nome] = te.esame(df, btc, inizio=se.INIZIO, anni_pieni=se.ANNI_PIENI)
        if nome == "VU":
            df_vu, W_vu = df, W
    e = out["VU"]
    rivisto = ast.corretto_rivisto({**ast.serie_nuove(), "116 VU": df_vu["netto"]}, {"116 VU": e["intero"]})
    r = rivisto["candidate"]["116 VU"]
    e["sharpe_corretto"], e["t"], e["gruppi"] = r["corretto_con_aggiunta"], r["t"], rivisto["gruppi"]
    e["esito"] = te.esito(e, e["sharpe_corretto"])
    f5 = pd.read_csv(QUI.parent / "programma6" / "risultati_controllo_parita" / "settimane_F5.csv.gz", index_col=0)
    c = df_vu.index.intersection(f5.index)
    c = c[c >= se.INIZIO]
    e["correlazione_F5"] = float(np.corrcoef(df_vu.loc[c, "netto"], f5.loc[c, "netto"])[0, 1])
    dal = lun >= se.INIZIO
    n = (np.isfinite(ct) & ps["U"])[dal].sum(axis=1)
    e["monete_con_segnale_mediana"] = float(np.median(n))
    e["settimane_con_posizioni"] = int((np.abs(W_vu[dal]).sum(axis=1) > 0).sum())
    e["settimane"] = int(dal.sum())
    anni = e.get("per_anno", {})
    e["regola_proprietario"] = bool(e["sharpe_corretto"] >= 0.90 and e["t"] > 3 and anni and all(v > 0 for v in anni.values()))
    (RIS / "esame.json").write_text(json.dumps(out, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    i, op = e["intero"], out["VU opposto"]["intero"]
    testo = "\n".join([
        "# Programma 7 — risultati della cinquantaquattresima prova (VU: il valore misurato con gli utenti, a settimana)", "",
        "Regole in `CINQUANTAQUATTRESIMA.md` (scritte prima). Dal 4 gennaio 2021, dati di CoinMetrics community e di Binance.", "",
        f"* {len(mappa)} monete con i dati e il perpetuo; monete con il segnale nell'universo, mediana {e['monete_con_segnale_mediana']:.0f} "
        f"a settimana; settimane con le posizioni {e['settimane_con_posizioni']} su {e['settimane']} (almeno 20 monete).",
        f"* **VU: Sharpe {i['sharpe']:.2f}**, {100 * i['annuo']:+.1f}% l'anno, volatilità {100 * i['volatilita']:.1f}%, discesa "
        f"{100 * i['discesa_max']:.1f}%; spese {100 * e['spese_annue']:.1f}% l'anno.",
        "* Per anno: " + ", ".join(f"{a} {100 * v:+.1f}%" for a, v in e["per_anno"].items()) + ".",
        f"* Il verso opposto (long le monete «care»): Sharpe {op['sharpe']:.2f}, {100 * op['annuo']:+.1f}% l'anno.",
        f"* Correlazione con F5: {e['correlazione_F5']:.2f}.",
        f"* Sharpe corretto con l'aggiunta {e['sharpe_corretto']:.2f} ({e['gruppi']} gruppi); t dello Sharpe {e['t']:.2f}; regola del "
        f"proprietario (corretto ≥ 0,90, ogni anno positivo, t > 3): {'sì' if e['regola_proprietario'] else 'no'}.", "",
        f"**Esito: {e['esito']}**"]) + "\n"
    (QUI / "RISULTATI_CINQUANTAQUATTRESIMA.md").write_text(testo, encoding="utf-8")
    log(testo)
    return out


if __name__ == "__main__":
    esegui(log=lambda x: print(x, flush=True))
    print("CINQUANTAQUATTRESIMA FINITA", flush=True)
