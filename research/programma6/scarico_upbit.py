"""Programma 6: quando ogni moneta e' entrata nel mercato in won di Upbit (la borsa coreana), dalle candele pubbliche
(api.upbit.com): il primo mese, il primo giorno e la prima ora di scambi di ogni mercato KRW-<moneta> di oggi. Gli annunci
di Upbit non sono raggiungibili da qui (Cloudflare): la prima candela e' l'inizio degli scambi. I mercati tolti da Upbit non
sono nell'elenco di oggi.

Scrive in ``research/data/upbit/quotazioni.json`` (fuori da git) e in ``scarico_upbit.json`` quante monete e l'impronta.
Uso: python3 -m research.programma6.scarico_upbit
"""
from __future__ import annotations

import hashlib
import json
import time
import urllib.request
from datetime import datetime, timedelta
from pathlib import Path

RADICE = Path(__file__).resolve().parents[2]
DATI = RADICE / "research" / "data" / "upbit"
QUI = Path(__file__).parent
API = "https://api.upbit.com/v1"
PRIMO_MESE_UTILE = "2020-12"      # i mercati aperti prima non servono alle prove (dal 2021): solo il primo mese


def chiedi(percorso: str):
    for prova in range(5):
        try:
            req = urllib.request.Request(f"{API}/{percorso}", headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=30) as r:
                out = json.loads(r.read())
            time.sleep(0.15)
            return out
        except Exception:
            time.sleep(2 ** (prova + 1))
    raise RuntimeError(f"{percorso} non scaricato")


def prima_ora(mercato: str) -> dict:
    mesi = chiedi(f"candles/months?market={mercato}&count=200")
    if not mesi:
        return {}
    m0 = min(x["candle_date_time_utc"] for x in mesi)
    if m0[:7] < PRIMO_MESE_UTILE:
        return {"mercato": mercato, "primo_mese": m0[:10]}
    fine_mese = (datetime.fromisoformat(m0) + timedelta(days=40)).strftime("%Y-%m-%dT00:00:00")
    giorni = chiedi(f"candles/days?market={mercato}&count=60&to={fine_mese}")
    g0 = min(x["candle_date_time_utc"] for x in giorni)
    a = (datetime.fromisoformat(g0) + timedelta(days=3)).strftime("%Y-%m-%dT00:00:00")
    ore = chiedi(f"candles/minutes/60?market={mercato}&count=200&to={a}")
    h0 = min(ore, key=lambda x: x["candle_date_time_utc"])["candle_date_time_utc"] if ore else None
    return {"mercato": mercato, "primo_mese": m0[:10], "primo_giorno": g0[:10], "prima_ora": h0,
            "prezzo_primo_giorno": float(min(giorni, key=lambda x: x["candle_date_time_utc"])["trade_price"])}


def main() -> int:
    DATI.mkdir(parents=True, exist_ok=True)
    mercati = sorted(x["market"] for x in chiedi("market/all") if x["market"].startswith("KRW-"))
    out = []
    for k, m in enumerate(mercati):
        try:
            x = prima_ora(m)
        except Exception as err:
            x = {"mercato": m, "errore": repr(err)[:200]}
        if x:
            out.append(x)
        if k % 10 == 0:
            print(f"[upbit] {k}/{len(mercati)}", flush=True)
    (DATI / "quotazioni.json").write_text(json.dumps(out, ensure_ascii=False, indent=0), encoding="utf-8")
    righe = "\n".join(f"{x['mercato']} {x.get('prima_ora')} {x.get('prezzo_primo_giorno')}" for x in out)
    imp = {"mercati": len(out), "dal_2020_12": sum(1 for x in out if "prima_ora" in x),
           "senza_ora": sum(1 for x in out if "prima_ora" in x and not x["prima_ora"]),
           "errori": sum(1 for x in out if "errore" in x), "sha256": hashlib.sha256(righe.encode()).hexdigest(), "scaricato": datetime.utcnow().strftime("%Y-%m-%d")}
    (QUI / "scarico_upbit.json").write_text(json.dumps(imp, indent=1), encoding="utf-8")
    print(f"[upbit] {len(out)} mercati", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
