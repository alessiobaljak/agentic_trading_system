"""Strategia BTCORA: tendenza del giorno applicata alle ore (regole in REGOLE.md accanto a questo file).

Uso: python3 -m research.collaudo_agenti.btcora.strategia
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from research.programma6 import esecuzione as es
from research.programma6 import seconda as sc

QUI = Path(__file__).parent
COSTO = 0.0005            # taker per lato
LEVA = 1.0


def dati():
    pan = sc.pannello()
    j = pan["simboli"].index("BTCUSDT")
    g = np.arange(sc.giorno(2023, 1, 1), sc.giorno(2024, 1, 1))
    idx = g - pan["t0"]
    giorni = pd.DataFrame({"close": pan["close"][idx, j], "funding": pan["funding"][idx, j]}, index=g)
    ore = es.ore_di("BTCUSDT")
    ore = ore[(ore.index >= g[0] * 24) & (ore.index < (g[-1] + 1) * 24)].copy()
    return giorni, ore


def segnali(giorni, ore):
    giorni = giorni.copy()
    giorni["media20"] = giorni["close"].rolling(20).mean()
    giorni["su"] = (giorni["close"] > giorni["media20"]).astype(float)
    ore = ore.copy()
    ore["giorno"] = ore.index // 24
    ore = ore.join(giorni[["su"]], on="giorno")          # il segnale del giorno per ogni ora del giorno
    ore["pos"] = np.where(ore["su"] == 1.0, 1.0, -1.0) * LEVA
    return ore


def conto(ore, giorni):
    r = ore["close"].pct_change().fillna(0.0)
    pos = ore["pos"].shift(1).fillna(0.0)
    cambi = pos.diff().abs().fillna(0.0)
    netto = pos * r - cambi * COSTO
    per_giorno = netto.groupby(ore.index // 24).sum()
    sharpe = per_giorno.mean() / per_giorno.std() * np.sqrt(252)
    return per_giorno, float(sharpe)


def main():
    giorni, ore = dati()
    ore = segnali(giorni, ore)
    per_giorno, sharpe = conto(ore, giorni)
    out = {"periodo": "2023-01-01 / 2023-12-31", "scala": "1h con filtro giornaliero", "sharpe": round(sharpe, 2),
           "rendimento": round(float(per_giorno.sum()), 4), "giorni": int(len(per_giorno))}
    (QUI / "risultati.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps(out))


if __name__ == "__main__":
    main()
