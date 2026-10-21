"""Programma 6: quando ogni moneta e' entrata su Coinbase (la borsa americana), dalle candele pubbliche
(api.exchange.coinbase.com): il primo giorno e la prima ora di scambi di ogni mercato <moneta>-USD di oggi, se e' dopo il
1 dicembre 2020. I mercati tolti da Coinbase non sono nell'elenco di oggi.

Scrive in ``research/data/coinbase/quotazioni.json`` (fuori da git) e in ``scarico_coinbase.json`` quante monete e
l'impronta. Uso: python3 -m research.programma6.scarico_coinbase
"""
from __future__ import annotations

import hashlib
import json
import time
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

RADICE = Path(__file__).resolve().parents[2]
DATI = RADICE / "research" / "data" / "coinbase"
QUI = Path(__file__).parent
API = "https://api.exchange.coinbase.com"
DA = datetime(2020, 12, 1, tzinfo=timezone.utc)


def chiedi(percorso: str):
    for prova in range(5):
        try:
            req = urllib.request.Request(f"{API}/{percorso}", headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=30) as r:
                out = json.loads(r.read())
            time.sleep(0.12)
            return out
        except Exception:
            time.sleep(2 ** (prova + 1))
    raise RuntimeError(f"{percorso} non scaricato")


def _iso(t: datetime) -> str:
    return t.strftime("%Y-%m-%dT%H:%M:%SZ")


def primo_giorno(prodotto: str) -> dict:
    """La prima candela giornaliera dal 1 dicembre 2020 (finestre di 300 giorni); prima del 2020-12: solo il segno."""
    t = DA
    adesso = datetime.now(timezone.utc)
    while t < adesso:
        fine = t + timedelta(days=299)
        c = chiedi(f"products/{prodotto}/candles?granularity=86400&start={_iso(t)}&end={_iso(fine)}")
        if c:
            g0 = min(x[0] for x in c)
            if t == DA and g0 <= int(DA.timestamp()) + 86400:
                return {"prodotto": prodotto, "prima": True}
            ore = chiedi(f"products/{prodotto}/candles?granularity=3600&start={_iso(datetime.fromtimestamp(g0, timezone.utc))}"
                         f"&end={_iso(datetime.fromtimestamp(g0, timezone.utc) + timedelta(hours=299))}")
            h0 = min(x[0] for x in ore) if ore else None
            primo = min(c, key=lambda x: x[0])
            return {"prodotto": prodotto, "primo_giorno": datetime.fromtimestamp(g0, timezone.utc).strftime("%Y-%m-%d"),
                    "prima_ora": datetime.fromtimestamp(h0, timezone.utc).strftime("%Y-%m-%dT%H:%M:%S") if h0 else None,
                    "prezzo_primo_giorno": float(primo[4])}
        t = fine
    return {"prodotto": prodotto, "vuoto": True}


def main() -> int:
    DATI.mkdir(parents=True, exist_ok=True)
    prodotti = sorted(x["id"] for x in chiedi("products") if x["quote_currency"] == "USD")
    out = []
    for k, p in enumerate(prodotti):
        try:
            out.append(primo_giorno(p))
        except Exception as err:
            out.append({"prodotto": p, "errore": repr(err)[:200]})
        if k % 25 == 0:
            print(f"[coinbase] {k}/{len(prodotti)}", flush=True)
    (DATI / "quotazioni.json").write_text(json.dumps(out, ensure_ascii=False, indent=0), encoding="utf-8")
    righe = "\n".join(f"{x['prodotto']} {x.get('prima_ora')} {x.get('prezzo_primo_giorno')}" for x in out)
    imp = {"prodotti": len(out), "dal_2020_12": sum(1 for x in out if "primo_giorno" in x),
           "errori": sum(1 for x in out if "errore" in x), "sha256": hashlib.sha256(righe.encode()).hexdigest(),
           "scaricato": datetime.now(timezone.utc).strftime("%Y-%m-%d")}
    (QUI / "scarico_coinbase.json").write_text(json.dumps(imp, indent=1), encoding="utf-8")
    print(f"[coinbase] {len(out)} prodotti", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
