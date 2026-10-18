"""E-005 — scalping con ordini limite in entrata e in uscita, periodo C (piano.md).
Uso: PYTHONPATH=. python3 research/programma5/esplorazione/E-005/esplora.py"""
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
K = (1, 2, 3)
M = (0.5, 1, 2)
H = (15, 60, 240)


def per_moneta(s: str) -> dict:
    df = m5.minuti(s, "C", storia_giorni=35)
    fund = m5.funding(s)
    b = barre(s, "C")
    minuto = df.index.to_numpy()
    o, h, l, c = (df[k].to_numpy(float) for k in ("open", "high", "low", "close"))
    nel = df["periodo"].to_numpy(bool)
    n = len(c)
    F = np.zeros(n)
    if len(fund):
        cum = np.concatenate([[0.0], np.cumsum(fund["tasso"].to_numpy(float))])
        F = cum[np.searchsorted(fund.index.to_numpy(), minuto, "right")]
    sc = m5.scarto(s)
    r1 = np.log(b["close"]).diff()
    sig = r1.rolling(720, min_periods=500).std()
    off = int((60 - minuto[0] % 60) % 60)
    nh = (n - off) // 60
    ore = (minuto[off] // 60) + np.arange(nh)
    P = b["close"].shift(1).reindex(ore).to_numpy(float)
    S = sig.shift(1).reindex(ore).to_numpy(float)
    L2 = l[off: off + nh * 60].reshape(nh, 60)
    H2 = h[off: off + nh * 60].reshape(nh, 60)
    ora_nel = nel[off: off + nh * 60].reshape(nh, 60)[:, 0]
    mese = pd.to_datetime(minuto * 60, unit="s").to_period("M").astype(str).to_numpy()
    out = {}
    for HH in H:
        fwd = np.full(n, np.nan)
        fwd[: n - HH] = c[HH:] / o[: n - HH] - 1
        ok = nel & np.isfinite(fwd)
        base = pd.Series(mese).map(pd.Series(fwd[ok]).groupby(mese[ok]).mean()).to_numpy(float)
        for k in K:
            for lato, d in (("acquisto", 1), ("vendita", -1)):
                livello = P * np.exp(-d * k * S)
                tocca = (L2 < livello[:, None]) if d > 0 else (H2 > livello[:, None])
                riga_ok = tocca.any(axis=1) & np.isfinite(livello) & ora_nel
                col = tocca.argmax(axis=1)
                for mm in M:
                    righe, libero = [], -1
                    for r in np.flatnonzero(riga_ok):
                        if ore[r] < libero:
                            continue
                        j = off + r * 60 + col[r]
                        e = j + HH
                        if e >= n or not np.isfinite(c[e]):
                            continue
                        L = livello[r]
                        T = L * np.exp(d * mm * S[r])
                        finestra = (h[j + 1: e + 1] > T) if d > 0 else (l[j + 1: e + 1] < T)
                        if finestra.any():
                            i = j + 1 + int(np.argmax(finestra))
                            prezzo, costo = T, 2 * m5.MAKER
                        else:
                            i = e
                            prezzo, costo = c[e], m5.MAKER + m5.TAKER + 2 * sc
                        lordo = d * (prezzo / L - 1) - d * (F[i] - F[j])
                        v = lordo - costo
                        righe.append((s, int(minuto[j]), v, v - d * base[j], v - costo))
                        libero = minuto[i] // 60 + 1
                    out[f"{lato} k{k} m{mm} H{HH}"] = righe
    return out


def main() -> int:
    raccolte: dict = {}
    for s in MONETE:
        ris = per_moneta(s)
        for nome, righe in ris.items():
            raccolte.setdefault(nome, []).extend(righe)
        print(f"[E-005] {s}: {sum(len(r) for r in ris.values())} trade", flush=True)
    risultati = {}
    for nome, righe in raccolte.items():
        df = pd.DataFrame(righe, columns=["s", "minuto", "v", "x", "doppio"])
        r = riassumi(df)
        r["doppio"] = float(df["doppio"].mean()) if len(df) else float("nan")
        r["promossa"] = bool(r["trade"]) and promossa(r, 0.0005, -1.0, solo_positivo=True) and r["doppio"] > 0
        risultati[nome] = r
    (QUI / "risultati.json").write_text(json.dumps(risultati, ensure_ascii=False, indent=0), encoding="utf-8")
    intro = ["Calcolo di `esplora.py` sul periodo C (piano: `piano.md`). Qui la colonna «Lordo» è il **netto** a trade "
             "(commissioni, scarto e funding compresi); il netto a costi doppi è in `risultati.json` («doppio»)."]
    (QUI / "risultati.md").write_text(tabella_md("E-005 — risultati", intro, risultati), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
