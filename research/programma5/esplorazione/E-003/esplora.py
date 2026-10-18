"""E-003 — valore relativo fra le monete, periodo C (piano.md).
Uso: PYTHONPATH=. python3 research/programma5/esplorazione/E-003/esplora.py"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

from research.programma5.strumenti.esplorazione import riassumi, t_giorni, tabella_md
from research.programma5.strumenti.ore import barre

QUI = Path(__file__).parent
MONETE = ("BTCUSDT", "ETHUSDT", "SOLUSDT", "XRPUSDT", "BNBUSDT", "DOGEUSDT",
          "ADAUSDT", "LINKUSDT", "AVAXUSDT", "LTCUSDT", "DOTUSDT", "TRXUSDT")
ALTRE = MONETE[1:]
HH = (1, 4, 12, 24, 72, 168)


def avanti(b: pd.DataFrame, h: int) -> np.ndarray:
    """Long da apertura di t+1 a chiusura di t+h, meno il funding pagato da long (come E-001)."""
    o, c, f = (b[k].to_numpy(float) for k in ("open", "close", "funding_cum"))
    n = len(c)
    out = np.full(n, np.nan)
    if h < n:
        out[: n - h] = (c[h:] / o[1: n - h + 1] - 1 - (f[h - 1: n - 1] - f[: n - h]))
    return out


def pannello():
    grezze = {s: barre(s, "C") for s in MONETE}
    ore = np.arange(min(b.index.min() for b in grezze.values()), max(b.index.max() for b in grezze.values()) + 1)
    P = {}
    for s, b in grezze.items():
        b = b.reindex(ore)
        b["periodo"] = b["periodo"].eq(True)
        b["funding_cum"] = b["funding_cum"].ffill().fillna(0.0)
        b["lc"] = np.log(b["close"])
        b["r1"] = b["lc"].diff()
        P[s] = b
    A = {h: {s: avanti(P[s], h) for s in MONETE} for h in HH}
    return ore, P, A


def sfoltisci(cond: np.ndarray, pausa: int) -> np.ndarray:
    scelti, ultimo = [], -10 ** 12
    for t in np.flatnonzero(cond):
        if t - ultimo >= pausa:
            scelti.append(t)
            ultimo = t
    return np.asarray(scelti, dtype=np.int64)


def mesi(ore: np.ndarray) -> np.ndarray:
    return pd.to_datetime(ore * 3600, unit="s").to_period("M").astype(str).to_numpy()


# ---------------------------------------------------------------------------
# G1: scossa propria coperta con BTC
# ---------------------------------------------------------------------------

def g1(ore, P, A, ris):
    btc = P["BTCUSDT"]
    mese = mesi(ore)
    for s in ALTRE:
        b = P[s]
        rb = btc["r1"]
        m = 720, 500
        cov = (b["r1"] * rb).rolling(*m).mean() - b["r1"].rolling(*m).mean() * rb.rolling(*m).mean()
        beta = cov / rb.rolling(*m).var(ddof=0)
        e1 = b["r1"] - beta.shift(1) * rb
        sig_e = e1.rolling(*m).std()
        nel = b["periodo"].to_numpy()
        for w in (1, 4, 24):
            ew = (b["lc"] - b["lc"].shift(w)) - beta.shift(w) * (btc["lc"] - btc["lc"].shift(w))
            z = (ew / (sig_e.shift(w) * np.sqrt(w))).to_numpy()
            bt = beta.shift(w).to_numpy()
            for h in (1, 4, 12, 24, 72):
                cop = A[h][s] - bt * A[h]["BTCUSDT"]
                ok = nel & np.isfinite(cop)
                base = pd.Series(mese).map(pd.Series(cop[ok]).groupby(mese[ok]).mean()).to_numpy(float)
                for k in (2, 3, 4):
                    for lato, cond, d in (("su", z >= k, 1), ("giu", z <= -k, -1)):
                        ev = sfoltisci(cond & ok, max(w, h))
                        ris.setdefault(f"G1 w{w} k{k} {lato} h{h}", {"fam": "G1", "righe": []})["righe"].append(
                            pd.DataFrame({"s": s, "minuto": ore[ev] * 60, "v": d * cop[ev],
                                          "x": d * (cop[ev] - base[ev])}))


# ---------------------------------------------------------------------------
# G2-G5: classifiche (portafoglio long le 3 prime, short le 3 ultime)
# ---------------------------------------------------------------------------

def decisioni(ore: np.ndarray, nel: np.ndarray, h: int) -> np.ndarray:
    fine = ore + 1
    if h <= 24:
        ok = (fine % h) == 0
    else:
        giorno0 = (fine[nel][0] // 24) if nel.any() else 0
        ok = ((fine % 24) == 0) & (((fine // 24 - giorno0) % (h // 24)) == 0)
    return np.flatnonzero(ok & nel)


def classifica(nome, fam, ore, punteggio: dict, A_h: dict, dec: np.ndarray, ris, minimo: int = 8):
    monete = list(punteggio)
    S = np.vstack([punteggio[s] for s in monete])          # monete x ore
    R = np.vstack([A_h[s] for s in monete])
    righe, contributi = [], []
    for t in dec:
        p, r = S[:, t], R[:, t]
        ok = np.isfinite(p) & np.isfinite(r)
        if ok.sum() < minimo:
            continue
        idx = np.flatnonzero(ok)
        ordine = idx[np.argsort(p[idx], kind="stable")]
        basse, alte = ordine[:3], ordine[-3:]
        v = (r[alte].mean() - r[basse].mean()) / 2
        media = r[idx].mean()
        righe.append(("PORTAFOGLIO", int(ore[t] * 60), v, v))
        for i in alte:
            contributi.append((monete[i], r[i] - media))
        for i in basse:
            contributi.append((monete[i], -(r[i] - media)))
    cella = ris.setdefault(nome, {"fam": fam, "righe": []})
    cella["righe"].append(pd.DataFrame(righe, columns=["s", "minuto", "v", "x"]))
    cella["contributi"] = contributi


def g2_g5(ore, P, A, ris):
    nel = P["BTCUSDT"]["periodo"].to_numpy()
    btc = P["BTCUSDT"]
    # beta di ogni moneta con BTC per il residuo
    beta = {}
    for s in ALTRE:
        b, rb = P[s], btc["r1"]
        cov = (b["r1"] * rb).rolling(720, min_periods=500).mean() - \
            b["r1"].rolling(720, min_periods=500).mean() * rb.rolling(720, min_periods=500).mean()
        beta[s] = cov / rb.rolling(720, min_periods=500).var(ddof=0)
    for w in (1, 4, 24, 72, 168):
        grezzo = {s: (P[s]["lc"] - P[s]["lc"].shift(w)).to_numpy() for s in MONETE}
        residuo = {s: ((P[s]["lc"] - P[s]["lc"].shift(w)) - beta[s].shift(w) *
                       (btc["lc"] - btc["lc"].shift(w))).to_numpy() for s in ALTRE}
        for h in (1, 4, 24, 72, 168):
            dec = decisioni(ore, nel, h)
            classifica(f"G2 rendimento w{w} h{h}", "G2", ore, grezzo, A[h], dec, ris)
            classifica(f"G2 residuo w{w} h{h}", "G2", ore, residuo, {s: A[h][s] for s in ALTRE}, dec, ris)
    for h in (24, 72, 168):
        f8 = {s: P[s]["funding_8h"].to_numpy(float) for s in MONETE}
        classifica(f"G3 funding h{h}", "G3", ore, f8, A[h], decisioni(ore, nel, h), ris)
    for w in (24, 72):
        doi = {s: (np.log(P[s]["oi"].where(P[s]["oi"] > 0)) - np.log(P[s]["oi"].where(P[s]["oi"] > 0)).shift(w))
               .to_numpy() for s in MONETE}
        for h in (24, 72):
            classifica(f"G4 oi w{w} h{h}", "G4", ore, doi, A[h], decisioni(ore, nel, h), ris)
    vol = {}
    for s in MONETE:
        v24 = P[s]["volume"].rolling(24).sum()
        vol[s] = (v24 / v24.rolling(720, min_periods=500).median().shift(24)).to_numpy()
    for h in (24, 72):
        classifica(f"G5 volume h{h}", "G5", ore, vol, A[h], decisioni(ore, nel, h), ris)


# ---------------------------------------------------------------------------
# G6: le altre insieme contro BTC
# ---------------------------------------------------------------------------

def g6(ore, P, A, ris):
    btc = P["BTCUSDT"]
    nel = btc["periodo"].to_numpy()
    r1 = pd.DataFrame({s: P[s]["r1"] for s in ALTRE})
    s1 = r1.mean(axis=1) - btc["r1"]
    sig = s1.rolling(720, min_periods=500).std()
    lc = pd.DataFrame({s: P[s]["lc"] for s in ALTRE})
    for w in (4, 24, 72):
        sw = (lc - lc.shift(w)).mean(axis=1) - (btc["lc"] - btc["lc"].shift(w))
        z = (sw / (sig.shift(w) * np.sqrt(w))).to_numpy()
        for h in (4, 24, 72):
            paniere = np.nanmean(np.vstack([A[h][s] for s in ALTRE]), axis=0)
            v_lungo = (paniere - A[h]["BTCUSDT"]) / 2
            ok = nel & np.isfinite(v_lungo)
            for k in (2, 3):
                for lato, cond, d in (("su", z >= k, 1), ("giu", z <= -k, -1)):
                    ev = sfoltisci(cond & ok, max(w, h))
                    ris.setdefault(f"G6 w{w} k{k} {lato} h{h}", {"fam": "G6", "righe": []})["righe"].append(
                        pd.DataFrame({"s": "PANIERE", "minuto": ore[ev] * 60, "v": d * v_lungo[ev],
                                      "x": d * v_lungo[ev]}))


# ---------------------------------------------------------------------------

def promossa(fam: str, r: dict) -> bool:
    if r.get("trade", 0) < 100 or not np.isfinite(r.get("t", np.nan)):
        return False
    segno = np.sign(r["lordo"])
    soglia, caso, t_min = (0.005, 0.004, 3.0) if fam == "G1" else (0.003, 0.003, 3.5 if fam == "G6" else 3.0)
    if segno * r["lordo"] < soglia or segno * r["contro_caso"] < caso or segno * r["t"] < t_min:
        return False
    if any(segno * m <= 0 for n, m in r["per_anno"].values() if n >= 20):
        return False
    if fam == "G6":
        return True
    monete = [m for n, m in r["per_moneta"].values() if n >= 10]
    giuste = sum(1 for m in monete if segno * m > 0)
    return len(monete) >= 6 and giuste >= 0.7 * len(monete)


def main() -> int:
    ore, P, A = pannello()
    print("[E-003] pannello pronto", flush=True)
    ris: dict = {}
    g1(ore, P, A, ris)
    print("[E-003] G1 fatto", flush=True)
    g2_g5(ore, P, A, ris)
    print("[E-003] G2-G5 fatti", flush=True)
    g6(ore, P, A, ris)
    risultati = {}
    for nome, cella in ris.items():
        parti = [p for p in cella["righe"] if len(p)]
        righe = pd.concat(parti, ignore_index=True) if parti else pd.DataFrame(columns=["s", "minuto", "v", "x"])
        r = riassumi(righe)
        if "contributi" in cella and r["trade"]:
            c = pd.DataFrame(cella["contributi"], columns=["s", "v"])
            r["per_moneta"] = {m: [int(len(g)), float(g["v"].mean())] for m, g in c.groupby("s")}
        r["famiglia"] = cella["fam"]
        r["promossa"] = promossa(cella["fam"], r) if r["trade"] else False
        risultati[nome] = r
    (QUI / "risultati.json").write_text(json.dumps(risultati, ensure_ascii=False, indent=0), encoding="utf-8")
    intro = ["Calcolo di `esplora.py` sul periodo C (piano: `piano.md`). Lordo a trade in % (G1: del valore della "
             "moneta, coperta con BTC; G2-G6: del capitale, metà long e metà short), funding compreso, senza "
             "commissioni e scarto (un giro: G1 circa 0,26%, G2-G6 circa 0,13%). Il segno dice il verso: negativo = "
             "conviene «contro». Per G2-G5 la colonna delle monete conta il contributo di ogni moneta nel portafoglio."]
    (QUI / "risultati.md").write_text(tabella_md("E-003 — risultati", intro, risultati), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
