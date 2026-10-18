"""E-002 — reti di ordini limite sulla volatilita', periodo C (piano.md).
Uso: PYTHONPATH=. python3 research/programma5/esplorazione/E-002/esplora.py"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

from research.programma5.strumenti import motore5 as m5
from research.programma5.strumenti.esplorazione import promossa, riassumi, tabella_md
from research.programma5.strumenti.ore import barre

QUI = Path(__file__).parent
MONETE = ("BTCUSDT", "ETHUSDT", "SOLUSDT", "XRPUSDT", "BNBUSDT", "DOGEUSDT",
          "ADAUSDT", "LINKUSDT", "AVAXUSDT", "LTCUSDT", "DOTUSDT", "TRXUSDT")
K = (2, 3, 4, 6)
H = (15, 60, 240, 1440)
OI = ("tutti", "oi giu", "oi su")


def pct_oi_60(df: pd.DataFrame, met: pd.DataFrame) -> np.ndarray:
    """Per ogni minuto: percentile (fra i 30 giorni prima) della variazione dell'interesse aperto nei 60 minuti prima,
    con le ultime rilevazioni note (orario <= minuto, al massimo 10 minuti prima)."""
    n = len(df)
    if met.empty or "sum_open_interest" not in met:
        return np.full(n, np.nan)
    oi = met["sum_open_interest"].astype(float)
    oi = oi.where(oi > 0).dropna()
    griglia = oi.reindex(np.arange(oi.index.min() // 5 * 5, oi.index.max() + 1, 5))
    chg = np.log(griglia) - np.log(griglia.shift(12))
    pct = chg.rolling(30 * 288, min_periods=10 * 288).rank(pct=True).dropna()
    if pct.empty:
        return np.full(n, np.nan)
    idx = df.index.to_numpy()
    pi = pct.index.to_numpy()
    pos = np.searchsorted(pi, idx, "right") - 1
    ok = (pos >= 0) & ((idx - pi[np.clip(pos, 0, None)]) <= 10)
    return np.where(ok, pct.to_numpy()[np.clip(pos, 0, None)], np.nan)


def per_moneta(s: str) -> dict:
    df = m5.minuti(s, "C", storia_giorni=35)
    met = m5.metrics(s, "C", storia_giorni=35)
    fund = m5.funding(s)
    b = barre(s, "C")
    minuto = df.index.to_numpy()
    o, h, l, c = (df[k].to_numpy(float) for k in ("open", "high", "low", "close"))
    nel = df["periodo"].to_numpy(bool)
    n = len(c)
    # funding cumulato al minuto (regolamenti con minuto <= m)
    F = np.zeros(n)
    if len(fund):
        cum = np.concatenate([[0.0], np.cumsum(fund["tasso"].to_numpy(float))])
        F = cum[np.searchsorted(fund.index.to_numpy(), minuto, "right")]
    # livelli per ora: P = chiusura dell'ora prima, sigma delle 720 ore fino all'ora prima
    r1 = np.log(b["close"]).diff()
    sig = r1.rolling(720, min_periods=500).std()
    P_ora = b["close"].shift(1)
    S_ora = sig.shift(1)
    off = int((60 - minuto[0] % 60) % 60)
    nh = (n - off) // 60
    ore = (minuto[off] // 60) + np.arange(nh)
    P = P_ora.reindex(ore).to_numpy(float)
    S = S_ora.reindex(ore).to_numpy(float)
    L2 = l[off: off + nh * 60].reshape(nh, 60)
    H2 = h[off: off + nh * 60].reshape(nh, 60)
    ora_nel = nel[off: off + nh * 60].reshape(nh, 60)[:, 0]
    pct = pct_oi_60(df, met)
    mese = pd.to_datetime(minuto * 60, unit="s").to_period("M").astype(str).to_numpy()
    out = {}
    for HH in H:
        # rendimento long a caso: apertura del minuto -> chiusura del minuto HH dopo, meno funding; media mese
        fwd = np.full(n, np.nan)
        fwd[: n - HH] = c[HH:] / o[: n - HH] - 1 - (F[HH:] - F[: n - HH])
        ok = nel & np.isfinite(fwd)
        base = pd.Series(mese).map(pd.Series(fwd[ok]).groupby(mese[ok]).mean()).to_numpy(float)
        for k in K:
            for lato, d in (("acquisto", 1), ("vendita", -1)):
                livello = P * np.exp(-d * k * S)
                if d > 0:
                    tocca = L2 < livello[:, None]
                else:
                    tocca = H2 > livello[:, None]
                valida = np.isfinite(livello) & ora_nel
                riga_ok = tocca.any(axis=1) & valida
                col = tocca.argmax(axis=1)
                for oi_nome in OI:
                    righe, libero_da = [], -1
                    for r in np.flatnonzero(riga_ok):
                        if ore[r] < libero_da:
                            continue
                        j = off + r * 60 + col[r]
                        e = j + HH
                        if e >= n or not np.isfinite(c[e]):
                            continue
                        if oi_nome == "oi giu" and not (pct[j] <= 0.2):
                            continue
                        if oi_nome == "oi su" and not (pct[j] >= 0.8):
                            continue
                        v = d * (c[e] / livello[r] - 1) - d * (F[e] - F[j])
                        righe.append((s, int(minuto[j]), v, v - d * base[j]))
                        libero_da = minuto[e] // 60 + 1
                    out[f"{lato} k{k} H{HH} {oi_nome}"] = righe
    return out


def main() -> int:
    raccolte: dict = {}
    for s in MONETE:
        ris = per_moneta(s)
        for nome, righe in ris.items():
            raccolte.setdefault(nome, []).extend(righe)
        print(f"[E-002] {s}: {sum(len(r) for r in ris.values())} trade", flush=True)
    risultati = {}
    for nome, righe in raccolte.items():
        df = pd.DataFrame(righe, columns=["s", "minuto", "v", "x"])
        r = riassumi(df)
        r["promossa"] = promossa(r, 0.0025, 0.0020, solo_positivo=True) if r["trade"] else False
        risultati[nome] = r
    (QUI / "risultati.json").write_text(json.dumps(risultati, ensure_ascii=False, indent=0), encoding="utf-8")
    intro = ["Calcolo di `esplora.py` sul periodo C (piano: `piano.md`). Lordo in % del valore della posizione, a trade, "
             "dall'esecuzione al livello all'uscita a mercato, funding compreso, senza commissioni e scarto (un giro "
             "0,09-0,11%). Qui conta solo il lordo positivo: un ordine limite non ha un «contro»."]
    (QUI / "risultati.md").write_text(tabella_md("E-002 — risultati", intro, risultati), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
