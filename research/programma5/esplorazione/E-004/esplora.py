"""E-004 — premio sullo spot e liquidazioni a ore, periodo C (piano.md).
Uso: PYTHONPATH=. python3 research/programma5/esplorazione/E-004/esplora.py"""
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


def avanti(b: pd.DataFrame, h: int) -> np.ndarray:
    o, c, f = (b[k].to_numpy(float) for k in ("open", "close", "funding_cum"))
    n = len(c)
    out = np.full(n, np.nan)
    if h < n:
        out[: n - h] = (c[h:] / o[1: n - h + 1] - 1 - (f[h - 1: n - 1] - f[: n - h]))
    return out


def sfoltisci(cond: np.ndarray, pausa: int) -> np.ndarray:
    scelti, ultimo = [], -10 ** 12
    for t in np.flatnonzero(cond):
        if t - ultimo >= pausa:
            scelti.append(t)
            ultimo = t
    return np.asarray(scelti, dtype=np.int64)


def pct(x: pd.Series) -> np.ndarray:
    return x.rolling(720, min_periods=500).rank(pct=True).to_numpy()


def celle(b: pd.DataFrame):
    uno = np.ones(len(b))
    lc = np.log(b["close"])
    sig = lc.diff().rolling(720, min_periods=500).std()
    zz = {w: ((lc - lc.shift(w)) / (sig.shift(w) * np.sqrt(w))).to_numpy() for w in (1, 4)}
    pr = b["premio"]
    ppr = pct(pr)
    for q in (0.05, 0.01):
        for h in (1, 4, 24, 72):
            yield f"P1 q{int(q * 100)} alto h{h}", "P1", h, h, ppr >= 1 - q, uno
            yield f"P1 q{int(q * 100)} basso h{h}", "P1", h, h, ppr <= q, -uno
    for w in (1, 4):
        pd_ = pct(pr - pr.shift(w))
        for h in (1, 4, 24):
            yield f"P2 w{w} sale h{h}", "P2", h, max(w, h), pd_ >= 0.95, uno
            yield f"P2 w{w} scende h{h}", "P2", h, max(w, h), pd_ <= 0.05, -uno
    for w in (1, 4):
        z = zz[w]
        for h in (4, 12, 24):
            yield f"P3 w{w} giu sconto h{h}", "P3", h, max(w, h), (z <= -3) & (ppr <= 0.10), -uno
            yield f"P3 w{w} giu senza sconto h{h}", "P3", h, max(w, h), (z <= -3) & (ppr > 0.10), -uno
            yield f"P3 w{w} su premio h{h}", "P3", h, max(w, h), (z >= 3) & (ppr >= 0.90), uno
            yield f"P3 w{w} su senza premio h{h}", "P3", h, max(w, h), (z >= 3) & (ppr < 0.90), uno
    loi = np.log(b["oi"].where(b["oi"] > 0))
    poi = pct(loi - loi.shift(1))
    z1 = zz[1]
    for h in (4, 12, 24):
        yield f"L0 giu h{h}", "L0", h, h, z1 <= -2, -uno
        yield f"L0 su h{h}", "L0", h, h, z1 >= 2, uno
        yield f"L1 giu h{h}", "L1", h, h, (poi <= 0.02) & (z1 <= -2), -uno
        yield f"L1 su h{h}", "L1", h, h, (poi <= 0.02) & (z1 >= 2), uno
        yield f"L2 giu h{h}", "L2", h, h, (poi >= 0.98) & (z1 <= -2), -uno
        yield f"L2 su h{h}", "L2", h, h, (poi >= 0.98) & (z1 >= 2), uno


def gemella(nome: str) -> str | None:
    if nome.startswith("P3"):
        return (nome.replace("giu sconto", "giu senza sconto") if "giu sconto" in nome
                else nome.replace("su premio", "su senza premio") if "su premio" in nome else None)
    if nome.startswith(("L1", "L2")):
        return "L0" + nome[2:]
    return None


def main() -> int:
    raccolte: dict = {}
    for s in MONETE:
        b = barre(s, "C").copy()
        b["premio"] = m5.premio(s, "C").reindex(b.index)
        nel = b["periodo"].to_numpy(bool)
        mese = pd.to_datetime(b.index.to_numpy() * 3600, unit="s").to_period("M").astype(str).to_numpy()
        fwd, base = {}, {}
        for h in (1, 4, 12, 24, 72):
            a = avanti(b, h)
            ok = nel & np.isfinite(a)
            fwd[h] = a
            base[h] = pd.Series(mese).map(pd.Series(a[ok]).groupby(mese[ok]).mean()).to_numpy(float)
        conta = 0
        for nome, fam, h, pausa, cond, d in celle(b):
            a = fwd[h]
            ev = sfoltisci(np.asarray(cond, bool) & nel & np.isfinite(a), pausa)
            raccolte.setdefault(nome, (fam, []))[1].append(pd.DataFrame(
                {"s": s, "minuto": b.index.to_numpy()[ev] * 60, "v": d[ev] * a[ev],
                 "x": d[ev] * (a[ev] - base[h][ev])}))
            conta += len(ev)
        print(f"[E-004] {s}: {conta} eventi", flush=True)
    risultati = {}
    for nome, (fam, parti) in raccolte.items():
        righe = pd.concat([p for p in parti if len(p)] or [pd.DataFrame(columns=["s", "minuto", "v", "x"])],
                          ignore_index=True)
        r = riassumi(righe)
        r["famiglia"] = fam
        r["promossa"] = bool(r["trade"]) and fam != "L0" and promossa(r, 0.003, 0.0025)
        risultati[nome] = r
    for nome, r in risultati.items():
        g = gemella(nome)
        if r["promossa"] and g and risultati.get(g, {}).get("trade"):
            segno = np.sign(r["lordo"])
            r["contro_gemella"] = float(segno * (r["lordo"] - risultati[g]["lordo"]))
            if r["contro_gemella"] < 0.003:
                r["promossa"] = False
    (QUI / "risultati.json").write_text(json.dumps(risultati, ensure_ascii=False, indent=0), encoding="utf-8")
    intro = ["Calcolo di `esplora.py` sul periodo C (piano: `piano.md`). Lordo in % a trade, funding compreso, senza "
             "commissioni e scarto (0,12-0,14% a giro). Il segno dice il verso: negativo = conviene «contro». Le celle L0 "
             "sono di riferimento e non si promuovono; per P3, L1 e L2 il confronto con la gemella è in `risultati.json` "
             "(«contro_gemella»)."]
    (QUI / "risultati.md").write_text(tabella_md("E-004 — risultati", intro, risultati), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
