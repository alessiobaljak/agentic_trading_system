"""Programma 5: il calcolo delle idee a 1 minuto senza interesse aperto (I-005, I-006, I-007), e l'aggregatore comune."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Callable

import numpy as np
import pandas as pd

from research.programma5.strumenti import motore5 as m5
from research.programma5.strumenti.eventi import eventi, metro24, ritorno5

MONETE = ("BTCUSDT", "ETHUSDT", "SOLUSDT", "XRPUSDT", "BNBUSDT", "DOGEUSDT",
          "ADAUSDT", "LINKUSDT", "AVAXUSDT", "LTCUSDT", "DOTUSDT", "TRXUSDT")


def aggrega(idea: str, varianti: dict, periodo: str, cartella: Path, per_moneta: Callable, monete=MONETE) -> dict:
    raccolti = {n: ([], []) for n in varianti}
    for s in monete:
        ris = per_moneta(idea, varianti, s, periodo)
        for n, (t, c) in ris.items():
            raccolti[n][0].append(t)
            raccolti[n][1].append(c)
        print(f"[{idea} {periodo}] {s}: " + ", ".join(f"{n} {len(t)}" for n, (t, _) in ris.items()), flush=True)
    esito = {}
    for n, (tt, cc) in raccolti.items():
        pt, pc = [x for x in tt if not x.empty], [x for x in cc if not x.empty]
        t = pd.concat(pt, ignore_index=True) if pt else pd.DataFrame()
        c = pd.concat(pc, ignore_index=True) if pc else pd.DataFrame()
        esito[n] = m5.esame(t, c, n_boot=10000 if periodo != "C" else 2000)
        if not t.empty:
            t.to_csv(cartella / f"trade_{periodo}_{n}.csv.gz", index=False)
    (cartella / f"{periodo}.json").write_text(json.dumps(esito, ensure_ascii=False, indent=1, default=float),
                                              encoding="utf-8")
    return esito


# ---------------------------------------------------------------------------
# I-005: squilibrio degli acquisti aggressivi durante un'esplosione
# ---------------------------------------------------------------------------

def per_moneta_i005(idea: str, varianti: dict, simbolo: str, periodo: str) -> dict:
    df = m5.minuti(simbolo, periodo, idea)
    if df.empty:
        return {}
    fund = m5.funding(simbolo)
    r5 = ritorno5(df)
    metro = metro24(r5)
    vol5 = df["volume"].rolling(5).sum().to_numpy()
    buy5 = df["taker_buy_volume"].rolling(5).sum().to_numpy()
    quota = np.where(vol5 > 0, buy5 / np.where(vol5 > 0, vol5, 1), np.nan)
    base = df["periodo"].to_numpy() & np.isfinite(r5) & np.isfinite(metro) & (metro > 0) & np.isfinite(quota)
    out = {}
    for nome, v in varianti.items():
        su = base & (r5 > 8 * metro) & (quota >= v["soglia"])
        giu = base & (r5 < -8 * metro) & (quota <= 1 - v["soglia"])
        ev = eventi(su | giu, max(60, v["minuti"]))
        direz = np.sign(r5[ev]).astype(int)
        uscita = m5.Uscita(minuti=v["minuti"])
        t = m5.simula(df, simbolo, ev, direz, uscita, fund, esplosione=np.ones(len(ev), bool))
        out[nome] = (t, m5.caso(df, simbolo, t, uscita, fund) if not t.empty else t)
    return out


# ---------------------------------------------------------------------------
# I-006: il prezzo intorno al regolamento del funding
# ---------------------------------------------------------------------------

def per_moneta_i006(idea: str, varianti: dict, simbolo: str, periodo: str) -> dict:
    df = m5.minuti(simbolo, periodo, idea)
    if df.empty:
        return {}
    fund = m5.funding(simbolo)
    minuti = df.index.to_numpy()
    periodo_ok = df["periodo"].to_numpy()
    f_min = fund.index.to_numpy()
    f_8h = (fund["tasso"] * 8.0 / fund["ore"].clip(lower=1)).to_numpy(float)
    out = {}
    for nome, v in varianti.items():
        dec, direz = [], []
        for k in range(1, len(f_min)):
            T = f_min[k]
            noto = f_8h[k - 1]                      # l'ultimo regolamento prima dell'ingresso
            if abs(noto) < v["soglia"]:
                continue
            ingresso_min = T - v["anticipo"]
            if f_min[k - 1] >= ingresso_min:          # il regolamento prima deve essere gia' avvenuto
                continue
            pos = np.searchsorted(minuti, ingresso_min - 1)   # si decide alla chiusura del minuto prima
            if pos >= len(minuti) or minuti[pos] != ingresso_min - 1 or not periodo_ok[pos]:
                continue
            dec.append(pos)
            direz.append(-1 if noto > 0 else 1)
        dec = np.asarray(dec, dtype=np.int64)
        uscita = m5.Uscita(minuti=v["anticipo"] + 5)
        t = m5.simula(df, simbolo, dec, np.asarray(direz, dtype=int), uscita, fund)
        out[nome] = (t, m5.caso(df, simbolo, t, uscita, fund) if not t.empty else t)
    return out


# ---------------------------------------------------------------------------
# I-007: le altre monete dopo BTC
# ---------------------------------------------------------------------------

_BTC: dict = {}


def _btc(periodo: str, idea: str):
    if periodo not in _BTC:
        b = m5.minuti("BTCUSDT", periodo, idea)
        r5 = ritorno5(b)
        _BTC[periodo] = pd.DataFrame({"r5": r5, "metro": metro24(r5)}, index=b.index)
    return _BTC[periodo]


def per_moneta_i007(idea: str, varianti: dict, simbolo: str, periodo: str) -> dict:
    if simbolo == "BTCUSDT":
        return {}
    df = m5.minuti(simbolo, periodo, idea)
    if df.empty:
        return {}
    fund = m5.funding(simbolo)
    b = _btc(periodo, idea).reindex(df.index)
    r5, metro = ritorno5(df), metro24(ritorno5(df))
    br5, bmetro = b["r5"].to_numpy(), b["metro"].to_numpy()
    base = (df["periodo"].to_numpy() & np.isfinite(r5) & np.isfinite(metro) & (metro > 0)
            & np.isfinite(br5) & np.isfinite(bmetro) & (bmetro > 0))
    esplode = base & (np.abs(br5) > 8 * bmetro)
    atteso = np.abs(br5) * np.where(bmetro > 0, metro / np.where(bmetro > 0, bmetro, 1), np.nan)
    mosso = np.sign(br5) * r5                     # quanto si e' mossa la moneta nella direzione di BTC
    out = {}
    for nome, v in varianti.items():
        cond = esplode & (mosso < v["indietro"] * atteso)
        ev = eventi(cond, 60)
        direz = np.sign(br5[ev]).astype(int)
        uscita = m5.Uscita(minuti=v["minuti"])
        t = m5.simula(df, simbolo, ev, direz, uscita, fund, esplosione=np.ones(len(ev), bool))
        out[nome] = (t, m5.caso(df, simbolo, t, uscita, fund) if not t.empty else t)
    return out
