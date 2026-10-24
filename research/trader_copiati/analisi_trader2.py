"""Trader da copiare n. 2: le posizioni chiuse trascritte dalle schermate, rimesse sui prezzi veri a 1 minuto di Binance.

Per ogni posizione: l'ora in UTC (le schermate mostrano l'ora italiana: UTC+2 fino al 25 ottobre 2026, UTC+1 prima del 29 marzo),
il controllo che il prezzo d'entrata e quello d'uscita stiano nelle candele di quei minuti, quanto si era mossa la moneta prima
dell'entrata (5, 15, 60 minuti), il volume rispetto al giorno prima, l'eta' del contratto, la durata e il rendimento sul prezzo.
Descrittivo: non e' una prova e non entra nel conto.

Uso: python3 -m research.trader_copiati.analisi_trader2 <cartella con i csv delle trascrizioni>
"""
from __future__ import annotations

import csv
import io
import json
import sys
import time
import zipfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import requests

QUI = Path(__file__).parent
DATI = QUI.parents[1] / "research" / "data" / "minuti_trader"
URL = "https://data.binance.vision/data/futures/um/daily/klines/{s}/1m/{s}-1m-{d}.zip"
ORA_LEGALE = (datetime(2026, 3, 29, 1, tzinfo=timezone.utc), datetime(2026, 10, 25, 1, tzinfo=timezone.utc))


def utc(testo: str) -> datetime:
    """L'ora delle schermate (ora italiana) in UTC."""
    t = datetime.strptime(testo.strip(), "%Y-%m-%d %H:%M:%S")
    for scarto in (2, 1):
        u = (t - timedelta(hours=scarto)).replace(tzinfo=timezone.utc)
        if (scarto == 2) == (ORA_LEGALE[0] <= u < ORA_LEGALE[1]):
            return u
    return (t - timedelta(hours=1)).replace(tzinfo=timezone.utc)


def minuti(simbolo: str, giorno: str) -> pd.DataFrame:
    """Le candele da 1 minuto di un giorno (UTC), dall'archivio pubblico di Binance, in cache."""
    f = DATI / simbolo / f"{giorno}.csv.gz"
    if f.exists():
        return pd.read_csv(f, index_col=0)
    for k in range(3):
        r = requests.get(URL.format(s=simbolo, d=giorno), timeout=30)
        if r.status_code == 404:
            return pd.DataFrame()
        if r.ok:
            break
        time.sleep(2 ** k)
    else:
        return pd.DataFrame()
    z = zipfile.ZipFile(io.BytesIO(r.content))
    righe = list(csv.reader(io.TextIOWrapper(z.open(z.namelist()[0]))))
    if righe and not righe[0][0].isdigit():
        righe = righe[1:]
    d = pd.DataFrame([[int(x[0]) // 60000, *map(float, x[1:6]), float(x[7])] for x in righe],
                     columns=["minuto", "open", "high", "low", "close", "volume", "dollari"]).set_index("minuto")
    f.parent.mkdir(parents=True, exist_ok=True)
    d.to_csv(f)
    return d


def finestra(simbolo: str, da: datetime, a: datetime) -> pd.DataFrame:
    giorni = sorted({(da + timedelta(days=k)).strftime("%Y-%m-%d") for k in range((a.date() - da.date()).days + 1)})
    parti = [minuti(simbolo, g) for g in giorni]
    parti = [p for p in parti if not p.empty]
    return pd.concat(parti).sort_index() if parti else pd.DataFrame()


def analizza(r: dict) -> dict:
    s, lato = r["simbolo"], r["lato"]
    a, c = utc(r["aperta"]), utc(r["chiusa"])
    m_a, m_c = int(a.timestamp()) // 60, int(c.timestamp()) // 60
    w = finestra(s, a - timedelta(days=1, hours=1), c + timedelta(minutes=5))
    out = {**r, "aperta_utc": a.strftime("%Y-%m-%d %H:%M:%S"), "chiusa_utc": c.strftime("%Y-%m-%d %H:%M:%S"),
           "durata_min": (m_c - m_a)}
    e, x = float(r["entrata"] or "nan"), float(r["prezzo_chiusura"] or "nan")
    segno = -1 if lato == "short" else 1
    out["rend_prezzo"] = segno * (x / e - 1) if e > 0 else np.nan
    if w.empty or m_a not in w.index:
        out["controllo"] = "candele mancanti"
        return out
    # i prezzi d'entrata e d'uscita sono medie (piu' ordini): si controlla che stiano fra il minimo e il massimo del tratto tenuto
    tratto = w.loc[m_a:m_c]
    out["controllo"] = "ok" if tratto["low"].min() * 0.995 <= e <= tratto["high"].max() * 1.005 and \
        tratto["low"].min() * 0.995 <= x <= tratto["high"].max() * 1.005 else "prezzi fuori dalle candele"
    p0 = w.loc[m_a, "open"]
    for n in (5, 15, 60):
        if m_a - n in w.index:
            out[f"prima_{n}m"] = p0 / w.loc[m_a - n, "open"] - 1
            out[f"max_{n}m"] = w.loc[m_a - n:m_a - 1, "high"].max() / w.loc[m_a - n, "open"] - 1
            out[f"min_{n}m"] = w.loc[m_a - n:m_a - 1, "low"].min() / w.loc[m_a - n, "open"] - 1
    giorno_prima = w.loc[m_a - 1440:m_a - 1]
    if len(giorno_prima) > 60:
        med = giorno_prima["dollari"].median()
        out["volume_15m_su_mediana"] = w.loc[m_a - 15:m_a - 1, "dollari"].mean() / med if med > 0 else np.nan
        out["salita_24h"] = p0 / giorno_prima["open"].iloc[0] - 1
    # dopo l'uscita: cosa avrebbe fatto tenendo 60 minuti in piu' (per capire se esce presto o tardi)
    if m_c + 60 in w.index:
        out["dopo_60m"] = segno * (w.loc[m_c + 60, "close"] / x - 1)
    out["massimo_contro"] = (tratto["high"].max() / e - 1) if lato == "short" else (1 - tratto["low"].min() / e)
    return out


def esegui(cartella: str) -> pd.DataFrame:
    righe = []
    for f in sorted(Path(cartella).glob("*.csv")):
        righe += list(csv.DictReader(open(f, encoding="utf-8")))
    righe = [r for r in righe if r.get("simbolo") and r.get("aperta") and r.get("chiusa")]
    chiavi = set()
    uniche = []
    for r in righe:                       # la stessa posizione puo' stare in due schermate di fila
        k = (r["simbolo"], r["aperta"], r["chiusa"])
        if k not in chiavi:
            chiavi.add(k)
            uniche.append(r)
    out = pd.DataFrame([analizza(r) for r in uniche])
    out.to_csv(QUI / "trader2_posizioni.csv", index=False)
    return out


if __name__ == "__main__":
    d = esegui(sys.argv[1])
    print(json.dumps({"posizioni": len(d), "controllo": d["controllo"].value_counts().to_dict()}, ensure_ascii=False))
