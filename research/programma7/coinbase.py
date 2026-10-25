"""Le candele a 1 ora dei mercati in dollari di Coinbase, per moneta (prova 87, VENTICINQUESIMA.md): la stessa richiesta della
prova 72 (`sedicesima.scarica`, solo BTC-USD) resa generale, con la cache in research/data/coinbase/ore_<PRODOTTO>.csv.gz.

Uso: python3 -m research.programma7.coinbase   (scarica le monete in comune con i perpetui di Binance, dal 2023)
"""
from __future__ import annotations

import hashlib
import json
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import requests

from research.programma6 import seconda as sc

DATI = Path(__file__).resolve().parents[2] / "research" / "data" / "coinbase"
URL = "https://api.exchange.coinbase.com/products/{p}/candles"
DA, A = datetime(2022, 12, 20, tzinfo=timezone.utc), datetime(2026, 10, 6, tzinfo=timezone.utc)
IMPRONTA = Path(__file__).parent / "coinbase_impronte.json"


def scarica(prodotto: str, da: datetime = DA, a: datetime = A, log=print) -> pd.DataFrame:
    """Le candele da 1 ora di un mercato di Coinbase (indice: l'ora dall'epoca), in cache."""
    f = DATI / f"ore_{prodotto}.csv.gz"
    if f.exists():
        return pd.read_csv(f, index_col=0)
    righe, t, vuote = [], da, 0
    while t < a:
        u = min(t + timedelta(hours=300), a)
        for prova in range(5):
            try:
                r = requests.get(URL.format(p=prodotto), params={"granularity": 3600, "start": t.isoformat(), "end": u.isoformat()},
                                 timeout=30)
                if r.status_code == 404:
                    righe = []
                    t = a
                    break
                if r.status_code == 429:
                    time.sleep(2 + 2 * prova)
                    continue
                r.raise_for_status()
                blocco = r.json()
                righe += blocco
                vuote += not blocco
                break
            except requests.RequestException as exc:
                if prova == 4:
                    log(f"[coinbase] {prodotto} {t:%Y-%m-%d}: {exc}")
                time.sleep(1 + prova)
        t = u
        time.sleep(0.2)
    if not righe:
        d = pd.DataFrame(columns=["open", "high", "low", "close", "volume"])
    else:
        d = pd.DataFrame(righe, columns=["t", "low", "high", "open", "close", "volume"]).drop_duplicates("t").sort_values("t")
        d.index = (d["t"] // 3600).astype(np.int64)
        d = d[["open", "high", "low", "close", "volume"]]
    DATI.mkdir(parents=True, exist_ok=True)
    d.to_csv(f)
    return d


def monete_in_comune(pan: dict, prima_del: str = "2024-01-01") -> list:
    """Le basi (per esempio «SOL») con il mercato -USD su Coinbase quotato prima di ``prima_del`` e il perpetuo USDT su Binance,
    anche con il prefisso dei multipli."""
    q = json.load(open(DATI / "quotazioni.json", encoding="utf-8"))
    usd = {p["prodotto"][:-4]: p.get("primo_giorno") for p in q if p.get("prodotto", "").endswith("-USD")}
    basi = set()
    for s in pan["simboli"]:
        if not s.endswith("USDT"):
            continue
        b = s[:-4]
        for pre in ("1000000", "1000", "1M"):
            if b.startswith(pre) and b[len(pre):] in usd:
                b = b[len(pre):]
        basi.add(b)
    return sorted(b for b in basi if usd.get(b) and usd[b] <= prima_del)


def main(log=print) -> dict:
    pan = sc.pannello()
    basi = monete_in_comune(pan)
    log(f"[coinbase] {len(basi)} monete in comune da scaricare")
    with ThreadPoolExecutor(max_workers=3) as ex:
        esiti = list(ex.map(lambda b: (b, len(scarica(f"{b}-USD", log=log))), basi))
    impronte = {}
    for b, n in esiti:
        f = DATI / f"ore_{b}-USD.csv.gz"
        impronte[b] = {"ore": n, "sha256": hashlib.sha256(f.read_bytes()).hexdigest()[:16]}
    IMPRONTA.write_text(json.dumps({"scaricato": datetime.now(timezone.utc).isoformat(timespec="minutes"), "monete": impronte},
                                   ensure_ascii=False, indent=1), encoding="utf-8")
    log(f"[coinbase] fatto: {sum(1 for _, n in esiti if n)} monete con candele, {sum(n for _, n in esiti)} ore in tutto")
    return impronte


if __name__ == "__main__":
    main(log=lambda x: print(x, flush=True))
    print("COINBASE FINITO", flush=True)
