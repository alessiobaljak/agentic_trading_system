"""Fase 0, punto 3: buchi, barre tolte dall'allineamento, funding, volume per anno e per mese.

Scrive ``fase0_calcoli.json`` nella cartella della campagna e ``mesi_esclusi.json`` (i mesi con
volume medio giornaliero in USDT sotto 20 milioni, letto dalle candele giornaliere del last con
``volume_usdt_da_zip``, su tutti i giorni).
"""
from __future__ import annotations

import json
from datetime import date, datetime, timezone
from pathlib import Path

import numpy as np

import comune
from research.src import dati

SOGLIA = 20_000_000
FINE = date(2023, 12, 31)


def giorno(ts: int) -> str:
    return datetime.fromtimestamp(ts / 1000, tz=timezone.utc).strftime("%Y-%m-%d %H:%M")


def intervalli_di_ts(lista, passo):
    """Raggruppa ts consecutivi (a distanza ``passo``) in intervalli [da, a]."""
    out = []
    for t in lista:
        if out and t - out[-1][1] == passo:
            out[-1][1] = t
        else:
            out.append([t, t])
    return [[giorno(a), giorno(b), (b - a) // passo + 1] for a, b in out]


def buchi(candele, passo):
    out = []
    for p, d in zip(candele, candele[1:]):
        if d.ts != p.ts + passo:
            out.append([giorno(p.ts + passo), giorno(d.ts - passo), (d.ts - p.ts) // passo - 1])
    return out


def main():
    ms = {"15m": 900_000, "30m": 1_800_000, "1h": 3_600_000, "2h": 7_200_000, "4h": 14_400_000,
          "6h": 21_600_000, "8h": 28_800_000, "12h": 43_200_000, "1d": 86_400_000}
    esito = {"allineamento": {}, "buchi_last": {}, "buchi_mark": {}, "btc_buchi": {}}
    inizio = comune.PRIMO_GIORNO
    for tf in comune.TIMEFRAME:
        ris = dati.carica_serie_allineate(comune.SIMBOLO, tf, inizio, FINE)
        last = dati.carica_candele(comune.SIMBOLO, tf, inizio, FINE)
        mark = dati.carica_candele(comune.SIMBOLO, tf, inizio, FINE, tipo="markPriceKlines")
        btc = dati.carica_candele("BTCUSDT", tf, inizio, FINE)
        esito["allineamento"][tf] = {
            "barre_last": len(last), "barre_mark": len(mark), "barre_tenute": len(ris["candele"]),
            "prima_barra": giorno(ris["candele"][0].ts), "ultima_barra": giorno(ris["candele"][-1].ts),
            "n_tolte_last": ris["n_tolte_last"], "n_tolte_mark": ris["n_tolte_mark"],
            "intervalli_tolte_last": intervalli_di_ts(ris["tolte_last"], ms[tf]),
            "intervalli_tolte_mark": intervalli_di_ts(ris["tolte_mark"], ms[tf]),
            "n_volume_mancante": ris["n_volume_mancante"],
        }
        esito["buchi_last"][tf] = buchi(last, ms[tf])
        esito["buchi_mark"][tf] = buchi(mark, ms[tf])
        esito["btc_buchi"][tf] = {"barre": len(btc), "buchi": buchi(btc, ms[tf])[:20],
                                  "prima": giorno(btc[0].ts) if btc else None}

    # Volume in USDT dalle candele giornaliere del last, tutti i giorni.
    volumi = {}
    for p in sorted((comune.CARTELLA_DATI / "klines" / "1d").glob("*.zip")):
        for ts, v in dati.volume_usdt_da_zip(p).items():
            if dati.ms_da_data(inizio) <= ts < dati.ms_da_data(date(2024, 1, 1)):
                volumi.setdefault(ts, v)
    per_mese, per_anno = {}, {}
    for ts, v in volumi.items():
        d = datetime.fromtimestamp(ts / 1000, tz=timezone.utc)
        per_mese.setdefault(d.strftime("%Y-%m"), []).append(v)
        per_anno.setdefault(str(d.year), []).append(v)
    media_mese = {m: float(np.mean(v)) for m, v in sorted(per_mese.items())}
    esito["volume_medio_giornaliero_usdt_per_anno"] = {a: float(np.mean(v)) for a, v in sorted(per_anno.items())}
    esito["volume_medio_giornaliero_usdt_per_mese"] = media_mese
    esito["giorni_per_mese"] = {m: len(v) for m, v in sorted(per_mese.items())}
    esclusi = [m for m, v in media_mese.items() if v < SOGLIA]
    esito["mesi_sotto_soglia"] = esclusi

    # Funding: disponibilita' e intervallo nel tempo.
    righe = dati.carica_funding_dettaglio(comune.SIMBOLO, inizio, FINE)
    esito["funding"] = {
        "n_settlement": len(righe), "primo": giorno(righe[0][0]), "ultimo": giorno(righe[-1][0]),
        "intervalli_dichiarati": [[giorno(t), o] for t, o in dati.intervallo_funding(righe)],
        "intervalli_da_distanza": [[giorno(t), o] for t, o in dati.intervallo_funding([(t, r) for t, _, r in righe])],
        "tasso_medio": float(np.mean([r for _, _, r in righe])),
        "tasso_mediano": float(np.median([r for _, _, r in righe])),
        "quota_positivi": float(np.mean([r > 0 for _, _, r in righe])),
        "per_anno_medio": {a: float(np.mean([r for t, _, r in righe if giorno(t).startswith(a)]))
                           for a in ("2020", "2021", "2022", "2023")},
    }
    out = comune.CARTELLA_CAMPAGNA / "fase0_calcoli.json"
    out.write_text(json.dumps(esito, indent=1, ensure_ascii=False))
    (comune.CARTELLA_CAMPAGNA / "mesi_esclusi.json").write_text(json.dumps(
        {"soglia_usdt_giorno": SOGLIA, "fonte": "candele 1d del last, colonna quote_volume (volume_usdt_da_zip), tutti i giorni",
         "mesi_esclusi": esclusi}, indent=1))
    print("fatto")


if __name__ == "__main__":
    main()
