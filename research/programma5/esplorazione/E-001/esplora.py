"""E-001 — esplorazione a ore sul periodo C (piano.md). Uso: PYTHONPATH=. python3 research/programma5/esplorazione/E-001/esplora.py

Scrive risultati.json (tutte le celle) e risultati.md (le celle promosse, le migliori, il riassunto per famiglia).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

from research.programma5.strumenti.ore import barre

QUI = Path(__file__).parent
MONETE = ("BTCUSDT", "ETHUSDT", "SOLUSDT", "XRPUSDT", "BNBUSDT", "DOGEUSDT",
          "ADAUSDT", "LINKUSDT", "AVAXUSDT", "LTCUSDT", "DOTUSDT", "TRXUSDT")
H5 = (1, 4, 12, 24, 72)


# ---------------------------------------------------------------------------
# preparazione per moneta
# ---------------------------------------------------------------------------

def prepara(s: str, btc: pd.DataFrame | None) -> pd.DataFrame:
    b = barre(s, "C").copy()
    b["lc"] = np.log(b["close"])
    b["r1"] = b["lc"].diff()
    b["sigma"] = b["r1"].rolling(720, min_periods=500).std()
    if btc is not None:
        rb = btc["r1"].reindex(b.index)
        b["rb"] = rb
        b["lcb"] = btc["lc"].reindex(b.index)
        cov = (b["r1"] * rb).rolling(720, min_periods=500).mean() - \
            b["r1"].rolling(720, min_periods=500).mean() * rb.rolling(720, min_periods=500).mean()
        b["beta"] = cov / rb.rolling(720, min_periods=500).var(ddof=0)
        e1 = b["r1"] - b["beta"].shift(1) * rb
        b["sigma_e"] = e1.rolling(720, min_periods=500).std()
        b["zb1"] = btc["z1"].reindex(b.index)
        b["zb4"] = btc["z4"].reindex(b.index)
    for w in (1, 4, 24):
        b[f"z{w}"] = (b["lc"] - b["lc"].shift(w)) / (b["sigma"].shift(w) * np.sqrt(w))
    return b


def avanti(b: pd.DataFrame, h: int) -> np.ndarray:
    """Rendimento long da apertura di t+1 a chiusura di t+h, meno il funding pagato da long nel frattempo."""
    o = b["open"].to_numpy(float)
    c = b["close"].to_numpy(float)
    f = b["funding_cum"].to_numpy(float)
    n = len(c)
    out = np.full(n, np.nan)
    if h >= n:
        return out
    ent = np.roll(o, -1)
    usc = np.roll(c, -h)
    fu = np.roll(f, -(h - 1)) - f
    out[: n - h] = (usc / ent - 1 - fu)[: n - h]
    return out


def sfoltisci(cond: np.ndarray, pausa: int) -> np.ndarray:
    scelti, ultimo = [], -10 ** 12
    for t in np.flatnonzero(cond):
        if t - ultimo >= pausa:
            scelti.append(t)
            ultimo = t
    return np.asarray(scelti, dtype=np.int64)


# ---------------------------------------------------------------------------
# le famiglie: ognuna da' (nome_cella, h, pausa, condizione, direzione) per moneta
# ---------------------------------------------------------------------------

def pct_mobile(x: pd.Series, finestra: int, minimo: int) -> pd.Series:
    return x.rolling(finestra, min_periods=minimo).rank(pct=True)


def celle(s: str, b: pd.DataFrame):
    ora = b.index.to_numpy()
    mezzanotte = ((ora + 1) % 24) == 0
    r1 = b["r1"].to_numpy()
    uno = np.ones(len(b))
    # F1 scossa
    for w in (1, 4, 24):
        z = b[f"z{w}"].to_numpy()
        for k in (3, 4, 5):
            for h in H5:
                yield f"F1 w{w} k{k} su h{h}", "F1", h, max(w, h), z >= k, uno
                yield f"F1 w{w} k{k} giu h{h}", "F1", h, max(w, h), z <= -k, -uno
    # F2 scossa + interesse aperto
    loi = np.log(b["oi"].where(b["oi"] > 0))
    for w in (1, 4):
        z = b[f"z{w}"].to_numpy()
        doi = loi - loi.shift(w)
        p = pct_mobile(doi, 720, 240).to_numpy()
        for lato, cz, d in (("su", z >= 3, uno), ("giu", z <= -3, -uno)):
            for oi_nome, co in (("oi su", p >= 0.8), ("oi giu", p <= 0.2)):
                for h in H5:
                    yield f"F2 w{w} {lato} {oi_nome} h{h}", "F2", h, max(w, h), cz & co, d
    # F3 scossa propria e F4 scossa di BTC (solo le altre monete)
    if s != "BTCUSDT":
        for w in (1, 4, 24):
            ew = (b["lc"] - b["lc"].shift(w)) - b["beta"].shift(w) * (b["lcb"] - b["lcb"].shift(w))
            ze = (ew / (b["sigma_e"].shift(w) * np.sqrt(w))).to_numpy()
            for k in (3, 4):
                for h in H5:
                    yield f"F3 w{w} k{k} su h{h}", "F3", h, max(w, h), ze >= k, uno
                    yield f"F3 w{w} k{k} giu h{h}", "F3", h, max(w, h), ze <= -k, -uno
        for w in (1, 4):
            zb = b[f"zb{w}"].to_numpy()
            for k in (3, 4):
                for h in H5:
                    yield f"F4 w{w} k{k} su h{h}", "F4", h, max(w, h), zb >= k, uno
                    yield f"F4 w{w} k{k} giu h{h}", "F4", h, max(w, h), zb <= -k, -uno
    # F5 rottura
    c = b["close"]
    for N in (5, 20, 60):
        mx = b["high"].rolling(N * 24, min_periods=N * 24 - 12).max().shift(1).to_numpy()
        mn = b["low"].rolling(N * 24, min_periods=N * 24 - 12).min().shift(1).to_numpy()
        for h in (24, 72, 168):
            yield f"F5 N{N} su h{h}", "F5", h, h, c.to_numpy() > mx, uno
            yield f"F5 N{N} giu h{h}", "F5", h, h, c.to_numpy() < mn, -uno
    # F6 funding (deciso alla chiusura dell'ora che finisce al regolamento)
    reg = b["regolamento"].to_numpy(bool)
    f8 = b["funding_8h"].where(b["regolamento"])
    pf = pd.Series(np.nan, index=b.index)
    sett = f8.dropna()
    pf.loc[sett.index] = pct_mobile(sett, 270, 90).to_numpy()
    pf = pf.to_numpy()
    for h in (24, 72, 168):
        yield f"F6 alto h{h}", "F6", h, h, reg & (pf >= 0.9), uno
        yield f"F6 basso h{h}", "F6", h, h, reg & (pf <= 0.1), -uno
    # F7 rapporti long/short a mezzanotte
    for col in ("ls_tutti", "ls_grandi_pos", "ls_grandi_conti"):
        x = b[col].where(mezzanotte)
        px = pd.Series(np.nan, index=b.index)
        giorni = x.dropna()
        px.loc[giorni.index] = pct_mobile(giorni, 31, 20).to_numpy()
        px = px.to_numpy()
        for h in (24, 72):
            yield f"F7 {col} alto h{h}", "F7", h, h, mezzanotte & (px >= 0.9), uno
            yield f"F7 {col} basso h{h}", "F7", h, h, mezzanotte & (px <= 0.1), -uno
    # F8 acquisti aggressivi
    for w in (1, 4, 24):
        q = b["buy"].rolling(w).sum() / b["volume"].rolling(w).sum()
        pq = pct_mobile(q, 720, 500).to_numpy()
        for h in (1, 4, 24):
            yield f"F8 w{w} alta h{h}", "F8", h, max(w, h), pq >= 0.95, uno
            yield f"F8 w{w} bassa h{h}", "F8", h, max(w, h), pq <= 0.05, -uno
    # F9 volume
    vr = (b["volume"] / b["volume"].rolling(720, min_periods=500).median().shift(1)).to_numpy()
    for k in (5, 10):
        for h in (1, 4, 24):
            yield f"F9 k{k} su h{h}", "F9", h, h, (vr >= k) & (r1 > 0), uno
            yield f"F9 k{k} giu h{h}", "F9", h, h, (vr >= k) & (r1 < 0), -uno
    # F10 calma poi rottura
    mx24 = b["high"].rolling(24).max()
    mn24 = b["low"].rolling(24).min()
    ampiezza = (mx24 - mn24) / b["close"]
    calma = (ampiezza / ampiezza.rolling(720, min_periods=500).median()).shift(1).to_numpy() < 0.5
    for h in (4, 24, 72):
        yield f"F10 su h{h}", "F10", h, h, calma & (c.to_numpy() > mx24.shift(1).to_numpy()), uno
        yield f"F10 giu h{h}", "F10", h, h, calma & (c.to_numpy() < mn24.shift(1).to_numpy()), -uno
    # F11 calendario
    for X in range(24):
        yield f"F11 ora {X:02d}", "F11", 1, 1, (ora % 24) == ((X - 1) % 24), uno
    giorno = pd.to_datetime((ora + 1) * 3600, unit="s").dayofweek.to_numpy()   # giorno in cui si entra
    for g, nome in enumerate(("lun", "mar", "mer", "gio", "ven", "sab", "dom")):
        yield f"F11 {nome}", "F11", 24, 24, mezzanotte & (giorno == g), uno
    # F12 tendenza
    lc = b["lc"]
    for N in (3, 7, 30):
        r = (lc - lc.shift(24 * N)).to_numpy()
        for h in (24, 168):
            yield f"F12 N{N} su h{h}", "F12", h, h, mezzanotte & (r > 0), uno
            yield f"F12 N{N} giu h{h}", "F12", h, h, mezzanotte & (r < 0), -uno
    # F13 prezzo e interesse aperto
    z24 = b["z24"].to_numpy()
    doi24 = (loi - loi.shift(24)).to_numpy()
    for lp, cp, d in (("su", z24 >= 1, uno), ("giu", z24 <= -1, -uno)):
        for lo, co in (("oi su", doi24 > 0), ("oi giu", doi24 < 0)):
            for h in (24, 72):
                yield f"F13 prezzo {lp} {lo} h{h}", "F13", h, h, mezzanotte & cp & co, d


# ---------------------------------------------------------------------------
# statistica
# ---------------------------------------------------------------------------

def t_giorni(v: np.ndarray, giorno: np.ndarray) -> float:
    if len(v) < 5:
        return float("nan")
    unici, inv = np.unique(giorno, return_inverse=True)
    S, N = np.bincount(inv, weights=v), np.bincount(inv)
    m = S.sum() / N.sum()
    G = len(unici)
    if G < 3:
        return float("nan")
    se = np.sqrt(np.sum((S - m * N) ** 2) * G / (G - 1)) / N.sum()
    return float(m / se) if se > 0 else float("nan")


def riassumi(righe: pd.DataFrame) -> dict:
    v = righe["v"].to_numpy()
    out = {"trade": int(len(v))}
    if len(v) == 0:
        return out
    out["lordo"] = float(v.mean())
    out["contro_caso"] = float(righe["x"].mean())
    out["t"] = t_giorni(v, righe["ora"].to_numpy() // 24)
    anni = pd.to_datetime(righe["ora"].to_numpy() * 3600, unit="s").year
    out["per_anno"] = {int(a): [int((anni == a).sum()), float(v[anni == a].mean())] for a in sorted(set(anni))}
    out["per_moneta"] = {m: [int(len(g)), float(g["v"].mean())] for m, g in righe.groupby("s")}
    return out


def promossa(r: dict) -> bool:
    if r.get("trade", 0) < 100 or not np.isfinite(r.get("t", np.nan)):
        return False
    segno = np.sign(r["lordo"])
    if abs(r["lordo"]) < 0.003 or segno * r["contro_caso"] < 0.0025 or abs(r["t"]) < 3:
        return False
    if any(segno * m <= 0 for n, m in r["per_anno"].values() if n >= 20):
        return False
    monete = [m for n, m in r["per_moneta"].values() if n >= 10]
    giuste = sum(1 for m in monete if segno * m > 0)
    return len(monete) >= 6 and giuste >= 0.7 * len(monete)


def main() -> int:
    raccolte: dict = {}
    btc = prepara("BTCUSDT", None)
    for s in MONETE:
        b = btc if s == "BTCUSDT" else prepara(s, btc)
        nel = b["periodo"].to_numpy(bool)
        mese = pd.to_datetime(b.index.to_numpy() * 3600, unit="s").to_period("M").astype(str).to_numpy()
        fwd = {}
        base = {}
        for h in (1, 4, 12, 24, 72, 168):
            a = avanti(b, h)
            fwd[h] = a
            ok = nel & np.isfinite(a)
            medie = pd.Series(a[ok]).groupby(mese[ok]).mean()
            base[h] = pd.Series(mese).map(medie).to_numpy(float)
        conte = 0
        for nome, fam, h, pausa, cond, d in celle(s, b):
            a = fwd[h]
            cond = np.asarray(cond, bool) & nel & np.isfinite(a)
            ev = sfoltisci(cond, pausa)
            if len(ev) == 0:
                raccolte.setdefault(nome, (fam, h, []))
                continue
            dd = d[ev]
            raccolte.setdefault(nome, (fam, h, []))[2].append(pd.DataFrame(
                {"s": s, "ora": b.index.to_numpy()[ev], "v": dd * a[ev], "x": dd * (a[ev] - base[h][ev])}))
            conte += len(ev)
        print(f"[E-001] {s}: {conte} eventi", flush=True)
    risultati = {}
    for nome, (fam, h, parti) in raccolte.items():
        righe = pd.concat(parti, ignore_index=True) if parti else pd.DataFrame(columns=["s", "ora", "v", "x"])
        r = riassumi(righe)
        r.update({"famiglia": fam, "h": h, "promossa": promossa(r)})
        risultati[nome] = r
    (QUI / "risultati.json").write_text(json.dumps(risultati, ensure_ascii=False, indent=0), encoding="utf-8")
    scrivi_md(risultati)
    return 0


def _riga(n: str, r: dict) -> str:
    anni = " ".join(f"{a}:{100 * m:+.2f}({k})" for a, (k, m) in r.get("per_anno", {}).items())
    monete = [m for k, m in r.get("per_moneta", {}).values() if k >= 10]
    segno = np.sign(r.get("lordo", 0))
    giuste = sum(1 for m in monete if segno * m > 0)
    return (f"| {n} | {r['trade']} | {100 * r['lordo']:+.3f}% | {100 * r['contro_caso']:+.3f}% | {r['t']:+.2f} | "
            f"{anni} | {giuste}/{len(monete)} | {'**sì**' if r['promossa'] else ''} |")


def scrivi_md(ris: dict) -> None:
    validi = {n: r for n, r in ris.items() if r.get("trade", 0) > 0 and np.isfinite(r.get("t", np.nan))}
    promosse = {n: r for n, r in validi.items() if r["promossa"]}
    testa = ["| Cella | Trade | Lordo «segue» | Contro il caso | t | Per anno (lordo %, trade) | Monete col segno giusto "
             "(≥10 trade) | Promossa |", "|---|---|---|---|---|---|---|---|"]
    righe = ["# E-001 — risultati", "",
             f"Calcolo di `esplora.py` sul periodo C (piano: `piano.md`). Celle calcolate: **{len(ris)}** "
             f"({len(validi)} con trade), cioè {2 * len(ris)} contando i due versi. Promosse: **{len(promosse)}**.",
             "Lordo in % del valore della posizione, a trade, funding compreso, senza commissioni e scarto (0,12-0,14% "
             "a giro). Il segno dice il verso: negativo = conviene «contro».", "", "## Celle promosse", ""]
    if promosse:
        righe += testa + [_riga(n, r) for n, r in sorted(promosse.items(), key=lambda x: -abs(x[1]["t"]))]
    else:
        righe.append("Nessuna.")
    righe += ["", "## Le 40 celle con |t| più alto", ""] + testa
    righe += [_riga(n, r) for n, r in sorted(validi.items(), key=lambda x: -abs(x[1]["t"]))[:40]]
    righe += ["", "## Le 30 celle con |lordo| più alto (almeno 100 trade)", ""] + testa
    grandi = {n: r for n, r in validi.items() if r["trade"] >= 100}
    righe += [_riga(n, r) for n, r in sorted(grandi.items(), key=lambda x: -abs(x[1]["lordo"]))[:30]]
    righe += ["", "Tutte le celle, con i numeri per moneta, sono in `risultati.json`."]
    (QUI / "risultati.md").write_text("\n".join(righe) + "\n", encoding="utf-8")


if __name__ == "__main__":
    sys.exit(main())
