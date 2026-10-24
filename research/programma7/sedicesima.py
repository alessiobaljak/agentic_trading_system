"""Programma 7, sedicesima prova (SEDICESIMA.md): G14, il premio di Coinbase sul Bitcoin: long (short) il Bitcoin per il giorno
dopo se la media del premio delle 24 ore prima e' positiva (negativa).

Uso: python3 -m research.programma7.sedicesima
"""
from __future__ import annotations

import gzip
import hashlib
import json
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import requests

from research.programma6 import asticella as ast
from research.programma6 import esecuzione as es
from research.programma6 import seconda as sc
from research.programma6 import sesta as se
from research.programma6 import terza as te
from research.programma6.motore import TAKER
from research.programma7 import prima as pr

QUI = Path(__file__).parent
RIS = QUI / "risultati_sedicesima"
DATI = QUI.parents[1] / "research" / "data" / "coinbase"
FILE_ORE = DATI / "ore_BTC-USD.csv.gz"
DA, A = datetime(2020, 12, 30, tzinfo=timezone.utc), datetime(2026, 10, 5, tzinfo=timezone.utc)
COSTO = TAKER + 0.0001
URL = "https://api.exchange.coinbase.com/products/BTC-USD/candles"


def scarica(log=print) -> pd.DataFrame:
    """Le candele da 1 ora del BTC-USD di Coinbase (300 per richiesta), in cache in research/data/coinbase."""
    if FILE_ORE.exists():
        return pd.read_csv(FILE_ORE, index_col=0)
    righe, t = [], DA
    while t < A:
        u = min(t + timedelta(hours=300), A)
        for prova in range(4):
            try:
                r = requests.get(URL, params={"granularity": 3600, "start": t.isoformat(), "end": u.isoformat()}, timeout=20)
                r.raise_for_status()
                righe += r.json()
                break
            except Exception as exc:  # noqa: BLE001
                if prova == 3:
                    log(f"[sedicesima] scarico fallito {t}: {exc}")
                time.sleep(2 ** prova)
        t = u
        time.sleep(0.15)
    d = pd.DataFrame(righe, columns=["t", "low", "high", "open", "close", "volume"]).drop_duplicates("t").sort_values("t")
    d.index = (d["t"] // 3600).astype(np.int64)
    d = d[["open", "high", "low", "close", "volume"]]
    DATI.mkdir(parents=True, exist_ok=True)
    d.to_csv(FILE_ORE)
    return d


def segnale_giornaliero(cb: pd.Series, bn: pd.Series, giorni: np.ndarray, minimo: int = 20) -> np.ndarray:
    """La media del premio (Coinbase / Binance − 1, chiusure orarie) delle 24 ore prima delle 00:00 di ogni giorno; NaN con meno
    di ``minimo`` ore con tutti e due i dati."""
    premio = (cb / bn - 1).dropna()
    out = np.full(len(giorni), np.nan)
    for k, g in enumerate(giorni):
        x = premio[(premio.index >= g * 24 - 24) & (premio.index < g * 24)]
        if len(x) >= minimo:
            out[k] = float(x.mean())
    return out


def conto(pos: np.ndarray, r: np.ndarray, f: np.ndarray) -> pd.DataFrame:
    """Il conto giornaliero di una posizione sul Bitcoin (+1 long, −1 short, 0 fuori): lordo, spese ai cambi, funding (il long paga)."""
    prima = np.concatenate([[0.0], pos[:-1]])
    spese = np.abs(pos - prima) * COSTO
    lordo = pos * r
    fund = pos * f
    df = pd.DataFrame({"lordo": lordo, "spese": spese, "funding": fund, "netto": lordo - spese - fund,
                       "netto_doppio": lordo - 2 * spese - fund, "giro": np.abs(pos - prima),
                       "long": np.where(pos > 0, lordo - spese - fund, 0.0), "short": np.where(pos < 0, lordo - spese - fund, 0.0),
                       "monete": (pos != 0).astype(int)})
    return df


def esegui(log=print) -> dict:
    cb = scarica(log)
    impronta = hashlib.sha256(gzip.compress(cb.to_csv().encode(), mtime=0)).hexdigest()[:16]
    bn = es.ore_di("BTCUSDT")
    pan = sc.pannello()
    giorni = np.arange(se.INIZIO, pr.FINE, dtype=np.int64)
    idx = giorni - pan["t0"]
    jb = pan["simboli"].index("BTCUSDT")
    s = segnale_giornaliero(cb["close"], bn["close"], giorni)
    pos = np.where(np.isfinite(s), np.sign(s), 0.0)
    r = sc.rendimenti(pan)[idx, jb]
    f = np.nan_to_num(pan["funding"][idx, jb])
    d = conto(pos, r, f)
    sett = pr.per_settimana(d, giorni)
    RIS.mkdir(exist_ok=True)
    sett.to_csv(RIS / "settimane_G14.csv.gz")
    ps = te.pannello_settimane(pan, log=lambda x: None, indicatori_si=False)
    btc = pd.Series(ps["R"][:, ps["simboli"].index("BTCUSDT")], index=ps["lunedi"])
    e = te.esame(sett, btc, inizio=se.INIZIO, anni_pieni=se.ANNI_PIENI)
    tenuto = btc[(btc.index >= se.INIZIO) & (btc.index < pr.FINE)]
    e["btc_tenuto"] = {"sharpe": float(tenuto.mean() / tenuto.std() * np.sqrt(52)), "annuo": float(tenuto.mean() * 52)}
    e["giorni_long"] = float((pos > 0).mean())
    e["giorni_fuori"] = float((pos == 0).mean())
    e["cambi_anno"] = float((np.abs(np.diff(pos)) > 0).sum() / (len(pos) / 365))
    e["premio_medio"] = float(np.nanmean(s))
    e["giorni_long_rendimento"] = float(r[pos > 0].mean()) if (pos > 0).any() else None
    e["giorni_short_rendimento_btc"] = float(r[pos < 0].mean()) if (pos < 0).any() else None
    e["impronta_dati"] = {"ore_coinbase": int(len(cb)), "sha256": impronta}
    rivisto = ast.corretto_rivisto({**ast.serie_nuove(), "72 G14": sett["netto"]}, {"72 G14": e["intero"]})
    rr = rivisto["candidate"]["72 G14"]
    e["sharpe_corretto"], e["t"], e["gruppi"] = rr["corretto_con_aggiunta"], rr["t"], rivisto["gruppi"]
    e["esito"] = te.esito(e, e["sharpe_corretto"])
    (RIS / "esame.json").write_text(json.dumps(e, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    i, b = e["intero"], e["btc_tenuto"]
    testo = "\n".join([
        "# Programma 7 — risultati della sedicesima prova (G14: il premio di Coinbase sul Bitcoin)", "",
        "Regole in `SEDICESIMA.md` (scritte prima).", "",
        f"* Dati: {e['impronta_dati']['ore_coinbase']} ore di Coinbase (impronta {impronta}); premio medio {100 * e['premio_medio']:+.3f}%.",
        f"* Giorni long {100 * e['giorni_long']:.0f}%, fuori {100 * e['giorni_fuori']:.0f}%; cambi di posizione {e['cambi_anno']:.0f} l'anno.",
        f"* Il Bitcoin nei giorni long: {100 * (e['giorni_long_rendimento'] or 0):+.3f}% al giorno; nei giorni short: "
        f"{100 * (e['giorni_short_rendimento_btc'] or 0):+.3f}% al giorno.",
        f"* G14: Sharpe {i['sharpe']:.2f}, {100 * i['annuo']:+.1f}% l'anno, volatilità {100 * i['volatilita']:.1f}%, discesa "
        f"{100 * i['discesa_max']:.1f}%; spese {100 * e['spese_annue']:.1f}% l'anno.",
        f"* Il Bitcoin tenuto sulle stesse settimane: Sharpe {b['sharpe']:.2f}, {100 * b['annuo']:+.1f}% l'anno.",
        "* Per anno: " + ", ".join(f"{a} {100 * v:+.1f}%" for a, v in e["per_anno"].items()) + ".",
        f"* Sharpe corretto {e['sharpe_corretto']:.2f} ({e['gruppi']} gruppi); t {e['t']:.2f}.", "",
        f"**Esito: {e['esito']}**"]) + "\n"
    (QUI / "RISULTATI_SEDICESIMA.md").write_text(testo, encoding="utf-8")
    log(testo)
    return e


if __name__ == "__main__":
    esegui(log=lambda x: print(x, flush=True))
    print("SEDICESIMA FINITA", flush=True)
