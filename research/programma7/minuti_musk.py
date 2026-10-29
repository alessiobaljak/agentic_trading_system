"""Misura descrittiva per l'idea 98 (non una prova, non entra nel conto): come si muove il prezzo dopo i messaggi originali di Musk su
Dogecoin e sul Bitcoin. Eventi: i messaggi «X Update» (non risposte, non ripubblicazioni) della raccolta pubblica fdaudens/musk-tweets
(Hugging Face) che nominano Dogecoin («doge», «dogecoin») o il Bitcoin («bitcoin», «btc»). Per ognuno il perpetuo di Binance
(DOGEUSDT, BTCUSDT) a 1 minuto: il rendimento dall'apertura del minuto del messaggio a +1, +5, +15, +60 e +240 minuti, e lo stesso in 5
minuti presi a caso nei 30 giorni prima (il controllo).

Uso: python3 -m research.programma7.minuti_musk FILE_CSV
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

from research.programma6 import seconda as sc
from research.trader_copiati.analisi_trader2 import minuti

QUI = Path(__file__).parent
DOPO = (1, 5, 15, 60, 240)
PAROLE = {"DOGEUSDT": r"\bdoge\b|dogecoin", "BTCUSDT": r"bitcoin|\bbtc\b"}


def percorso(simbolo: str, m: int) -> dict | None:
    giorni = range(m // 1440, (m + max(DOPO)) // 1440 + 1)
    w = pd.concat([x for x in (minuti(simbolo, sc.data(g)) for g in giorni) if not x.empty]) if giorni else pd.DataFrame()
    if w.empty or m not in w.index:
        return None
    p0 = float(w.loc[m, "open"])
    out = {}
    for d in DOPO:
        out[f"m{d}"] = float(w.loc[m + d, "open"] / p0 - 1) if (m + d) in w.index else np.nan
    return out


def main(file: str) -> None:
    df = pd.read_csv(file, low_memory=False)
    df = df[df["MessageType"] == "X Update"].copy()
    df["t"] = pd.to_datetime(df["CreatedTime"], errors="coerce", utc=True)
    df = df[df["t"] >= pd.Timestamp("2020-01-01", tz="UTC")]
    righe, caso = [], []
    rng = np.random.default_rng(2026)
    for simbolo, reg in PAROLE.items():
        ev = df[df["Message"].astype(str).str.contains(reg, case=False, regex=True)]
        visti = set()
        for _, x in ev.iterrows():
            m = int(x["t"].timestamp() // 60)
            if any(abs(m - v) < 240 for v in visti):          # un messaggio ogni 4 ore per moneta: niente sovrapposizioni
                continue
            visti.add(m)
            p = percorso(simbolo, m)
            if p:
                righe.append({"moneta": simbolo, "data": x["t"].strftime("%Y-%m-%d %H:%M"), "testo": str(x["Message"])[:80], **p})
            for t in rng.integers(m - 30 * 1440, m - 1440, 5):
                q = percorso(simbolo, int(t))
                if q:
                    caso.append({"moneta": simbolo, **q})
    d, c = pd.DataFrame(righe), pd.DataFrame(caso)
    d.to_csv(QUI / "risultati_minuti_musk.csv", index=False)
    righe_md = ["# Come si muove il prezzo dopo i messaggi di Musk (misura descrittiva, idea 98)", "",
                "Script `minuti_musk.py`. Messaggi originali (non risposte) della raccolta pubblica fdaudens/musk-tweets (Hugging Face), dal "
                "2020 al maggio 2025, un messaggio ogni 4 ore per moneta; perpetui di Binance a 1 minuto. Il controllo: 5 minuti a caso nei 30 "
                "giorni prima di ogni messaggio. Non è una prova: non entra nel conto.", ""]
    for simbolo in PAROLE:
        x, y = d[d["moneta"] == simbolo], c[c["moneta"] == simbolo]
        righe_md += [f"## {simbolo}: {len(x)} messaggi", "", "| Minuti dopo | Media | Mediana | Il controllo (media) |", "|---|---|---|---|"]
        for k in DOPO:
            righe_md.append(f"| +{k} | {100 * x[f'm{k}'].mean():+.3f}% | {100 * x[f'm{k}'].median():+.3f}% | {100 * y[f'm{k}'].mean():+.3f}% |")
        if len(x):
            top = x.reindex(x["m5"].abs().sort_values(ascending=False).index).head(5)
            righe_md += ["", "I 5 messaggi con il movimento più grande in 5 minuti: " + "; ".join(
                f"{r['data']} {100 * r['m5']:+.1f}% («{r['testo'][:40]}»)" for _, r in top.iterrows()), ""]
    testo = "\n".join(righe_md) + "\n"
    (QUI / "MINUTI_MUSK.md").write_text(testo, encoding="utf-8")
    print(testo, flush=True)


if __name__ == "__main__":
    main(sys.argv[1])
    print("MUSK FINITA", flush=True)
