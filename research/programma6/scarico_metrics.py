"""Programma 6: i dati giornalieri sulle posizioni (``metrics`` dell'archivio pubblico di Binance: interesse aperto,
rapporti long/short dei conti grandi e di tutti, rapporto fra acquisti e vendite a mercato) per le monete e i giorni che
servono alle prove settimanali fra le 100 monete più scambiate (ogni settimana dell'universo e i 30 giorni prima), dal
2021-12. Ogni file si scarica, si verifica col CHECKSUM, si **riassume nel suo giorno** e si butta: resta solo il
riassunto (``research/data/p6m/<SIMBOLO>.pkl``) e l'impronta (``scarico_metrics.json``: numero di file e SHA-256
dell'elenco ordinato «nome impronta»). Per le monete del programma 5 si usano i file già scaricati.

Uso: python3 -m research.programma6.scarico_metrics
"""
from __future__ import annotations

import hashlib
import io
import json
import os
import zipfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import numpy as np
import pandas as pd

from research.programma5.strumenti.scarico import BASE, _prendi
from research.programma6 import seconda as sc
from research.programma6 import terza as te
from research.src.dati import leggi_checksum

RADICE = Path(__file__).resolve().parents[2]
DATI = RADICE / "research" / "data" / "p6m"
P5 = RADICE / "research" / "data" / "p5"
QUI = Path(__file__).parent
DAL = sc.giorno(2021, 12, 1)
COLONNE = ["sum_open_interest_value", "count_toptrader_long_short_ratio", "sum_toptrader_long_short_ratio",
           "count_long_short_ratio", "sum_taker_long_short_vol_ratio"]


def giorni_che_servono(pan: dict) -> dict:
    ps = te.pannello_settimane(pan, log=lambda x: None, indicatori_si=False)
    lun = ps["lunedi"] - pan["t0"]
    out = {}
    for k in np.flatnonzero(ps["lunedi"] >= DAL + 30):
        for j in np.flatnonzero(ps["U"][k]):
            out.setdefault(ps["simboli"][j], set()).update(range(lun[k] - 30 + pan["t0"], lun[k] + pan["t0"]))
    # anche gli ultimi 31 giorni delle monete dell'universo dell'ultima settimana (per le posizioni di adesso nel paper)
    T = pan["close"].shape[0]
    if len(ps["U"]):
        for j in np.flatnonzero(ps["U"][-1]):
            out.setdefault(ps["simboli"][j], set()).update(range(T - 31 + pan["t0"], T + pan["t0"]))
    return out


def riassunto(grezzo: bytes) -> dict:
    with zipfile.ZipFile(io.BytesIO(grezzo)) as z:
        df = pd.read_csv(io.BytesIO(z.read(z.namelist()[0])))
    df = df[[c for c in COLONNE if c in df.columns]].apply(pd.to_numeric, errors="coerce")
    out = {"oi_valore_fine": float(df["sum_open_interest_value"].dropna().iloc[-1]) if df["sum_open_interest_value"].notna().any() else np.nan}
    for c in COLONNE[1:]:
        out[c] = float(df[c].mean()) if c in df else np.nan
    return out


def un_giorno(s: str, g: int):
    data = sc.data(g)
    nome = f"{s}-metrics-{data}.zip"
    locale = P5 / s / "metrics" / nome
    if locale.exists() and locale.with_suffix(".zip.ok").exists():
        grezzo = locale.read_bytes()
        impronta = locale.with_suffix(".zip.ok").read_text().strip().split()[0]
    else:
        chiave = f"data/futures/um/daily/metrics/{s}/{nome}"
        grezzo = _prendi(BASE + chiave)
        if grezzo is None:
            return g, None, None
        somma = _prendi(BASE + chiave + ".CHECKSUM")
        impronta = hashlib.sha256(grezzo).hexdigest()
        if somma is not None and leggi_checksum(somma, chiave) != impronta:
            raise RuntimeError(f"CHECKSUM diverso per {chiave}")
    try:
        return g, riassunto(grezzo), f"{nome} {impronta}"
    except Exception:                                   # file vuoto o senza colonne: si conta ma non si usa
        return g, None, f"{nome} {impronta}"


def una_moneta(s: str, giorni: set) -> dict:
    dest = DATI / f"{s}.pkl"
    fatto = pd.read_pickle(dest) if dest.exists() else pd.DataFrame()
    da_fare = sorted(g for g in giorni if g >= DAL and g not in set(fatto.index))
    with ThreadPoolExecutor(max_workers=8) as ex:
        esiti = list(ex.map(lambda g: un_giorno(s, g), da_fare))
    righe = {g: r for g, r, _ in esiti if r}
    nuovi = pd.DataFrame.from_dict(righe, orient="index") if righe else pd.DataFrame()
    tutto = pd.concat([fatto, nuovi]).sort_index() if len(nuovi) else fatto
    DATI.mkdir(parents=True, exist_ok=True)
    tutto.to_pickle(dest)
    return {"giorni": int(len(tutto)), "impronte": sorted(x for _, _, x in esiti if x)}


def main() -> int:
    pan = sc.pannello()
    servono = giorni_che_servono(pan)
    cartella = Path(os.environ["P6_IMPRONTE"]) if os.environ.get("P6_IMPRONTE") else QUI
    dest = cartella / "scarico_metrics.json"
    pieno = cartella / "scarico_metrics_elenco.json"
    imp = json.loads(pieno.read_text()) if pieno.exists() else {}
    simboli = sorted(servono)
    print(f"[metrics] {len(simboli)} monete, {sum(len(v) for v in servono.values())} giorni", flush=True)
    with ThreadPoolExecutor(max_workers=int(os.environ.get("P6_FILI", "8"))) as ex:
        for s, r in zip(simboli, ex.map(lambda x: una_moneta(x, servono[x]), simboli)):
            vecchie = imp.get(s, {}).get("elenco", [])
            elenco = sorted(set(vecchie) | set(r["impronte"]))
            imp[s] = {"giorni": r["giorni"], "file": len(elenco),
                      "sha256": hashlib.sha256("\n".join(elenco).encode()).hexdigest(), "elenco": elenco}
            print(f"[metrics] {s}: {r['giorni']} giorni", flush=True)
            leggero = {k: {kk: vv for kk, vv in v.items() if kk != "elenco"} for k, v in imp.items()}
            pieno.write_text(json.dumps(imp, indent=0, sort_keys=True))
            dest.write_text(json.dumps(leggero, indent=0, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
