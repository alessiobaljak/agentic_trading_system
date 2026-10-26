"""Programma 7, quarantanovesima prova (QUARANTANOVESIMA.md): SK2, il resto dello scalping del documento del proprietario: divergenze
dell'RSI, engulfing, pin bar e trading nell'intervallo, a 1 e 5 minuti; stesso simulatore, monete, periodo, costi ed esame della prova 108.

Uso: python3 -m research.programma7.quarantanovesima
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from numba import njit

from research.programma7 import quarantaseiesima as sk

QUI = Path(__file__).parent
RIS = QUI / "risultati_quarantanovesima"
REGOLE = ["divergenza_rsi", "engulfing", "pin_bar", "intervallo"]
VARIANTI = 8


@njit(cache=True)
def _divergenze(l, h, rsi):
    n = len(l)
    out = np.zeros(n, dtype=np.int64)
    for i in range(20, n):
        # minimo: la candela i e' la piu' bassa delle ultime 5 e sotto il minimo delle candele da i-20 a i-5
        m5 = l[i]
        ok = True
        for k in range(i - 4, i):
            if l[k] < m5:
                ok = False
                break
        if ok:
            jm, vm = -1, 1e300
            for k in range(i - 20, i - 4):
                if l[k] < vm:
                    vm, jm = l[k], k
            if jm >= 0 and l[i] < vm and rsi[i] == rsi[i] and rsi[jm] == rsi[jm] and rsi[i] > rsi[jm]:
                out[i] = 1
                continue
        M5 = h[i]
        ok = True
        for k in range(i - 4, i):
            if h[k] > M5:
                ok = False
                break
        if ok:
            jM, vM = -1, -1e300
            for k in range(i - 20, i - 4):
                if h[k] > vM:
                    vM, jM = h[k], k
            if jM >= 0 and h[i] > vM and rsi[i] == rsi[i] and rsi[jM] == rsi[jM] and rsi[i] < rsi[jM]:
                out[i] = -1
    return out


def segnali(df: pd.DataFrame, regola: str) -> tuple:
    o, h, l, c = (df[k] for k in ("open", "high", "low", "close"))
    atr = sk._atr(df)
    n = len(df)
    dirz = np.zeros(n, dtype=np.int64)
    dist_stop = atr.to_numpy().copy()
    dist_ob = 2 * atr.to_numpy()
    prezzo = np.full(n, np.nan)
    livello_ob = np.full(n, np.nan)
    if regola == "divergenza_rsi":
        dirz = _divergenze(l.to_numpy(np.float64), h.to_numpy(np.float64), sk._rsi(c, 14).to_numpy(np.float64))
    elif regola == "engulfing":
        giu3 = (c.shift(1) < c.shift(2)) & (c.shift(2) < c.shift(3)) & (c.shift(3) < c.shift(4))
        su3 = (c.shift(1) > c.shift(2)) & (c.shift(2) > c.shift(3)) & (c.shift(3) > c.shift(4))
        rossa, verde = c.shift(1) < o.shift(1), c > o
        dirz[(giu3 & rossa & verde & (o <= c.shift(1)) & (c >= o.shift(1))).to_numpy()] = 1
        dirz[(su3 & (c.shift(1) > o.shift(1)) & (c < o) & (o >= c.shift(1)) & (c <= o.shift(1))).to_numpy()] = -1
    elif regola == "pin_bar":
        corpo = (c - o).abs()
        bassa, alta, ampiezza = np.minimum(o, c) - l, h - np.maximum(o, c), h - l
        dirz[((bassa >= 2 * corpo) & (c >= l + 2 * ampiezza / 3) & (l <= l.rolling(20).min()) & (ampiezza > 0)).to_numpy()] = 1
        dirz[((alta >= 2 * corpo) & (c <= h - 2 * ampiezza / 3) & (h >= h.rolling(20).max()) & (ampiezza > 0)).to_numpy()] = -1
    elif regola == "intervallo":
        hi, lo = h.shift().rolling(60).max(), l.shift().rolling(60).min()
        largo = (hi - lo) / c
        laterale = largo < 0.015
        su = laterale & (l <= lo) & (c > lo)
        giu = laterale & (h >= hi) & (c < hi)
        w = (hi - lo).to_numpy()
        cc, lo_, hi_ = c.to_numpy(), lo.to_numpy(), hi.to_numpy()
        ds_su = cc - (lo_ - 0.25 * w)
        ds_giu = (hi_ + 0.25 * w) - cc
        dirz[su.to_numpy()] = 1
        dirz[giu.to_numpy()] = -1
        dist_stop = np.where(dirz == 1, ds_su, np.where(dirz == -1, ds_giu, dist_stop))
        livello_ob = np.where(dirz == 1, hi_, np.where(dirz == -1, lo_, np.nan))
    ok = np.isfinite(dist_stop) & (dist_stop > 0) & np.isfinite(dist_ob) & (dist_ob > 0)
    dirz = np.where(ok, dirz, 0)
    return dirz, dist_stop, dist_ob, prezzo, livello_ob


def operazioni(df: pd.DataFrame, regola: str, simbolo: str) -> pd.DataFrame:
    dirz, ds, dob, pz, lob = segnali(df, regola)
    a = [x.to_numpy(np.float64) for x in (df["open"], df["high"], df["low"], df["close"])]
    costo_m = sk.TAKER + sk.SCARTO.get(simbolo, sk.SCARTO_ALTRE)
    ei, dd, lordo, mot = sk._simula(a[0], a[1], a[2], a[3], dirz.astype(np.int64), np.asarray(ds, np.float64), np.asarray(dob, np.float64),
                                    np.asarray(pz, np.float64), np.asarray(lob, np.float64), costo_m, sk.MAX_CANDELE)
    costi = costo_m + np.where(mot == 1, sk.MAKER, costo_m)
    minuto = df.index.to_numpy()[ei]
    return pd.DataFrame({"minuto": minuto, "giorno": minuto // 1440, "lato": dd, "lordo": lordo, "netto": lordo - costi, "motivo": mot})


def esegui(log=print) -> dict:
    RIS.mkdir(exist_ok=True)
    tutte = []
    for s in sk.MONETE:
        for tf in (1, 5):
            df = sk.candele(s, tf)
            for r in REGOLE:
                op = operazioni(df, r, s)
                op["simbolo"], op["tempo"], op["regola"] = s, tf, r
                tutte.append(op)
            log(f"[quarantanovesima] {s} a {tf} minuti: fatto")
    tutte = pd.concat(tutte, ignore_index=True)
    soglia = 0.01 / VARIANTI
    giorni_tot = (sk.A_MIN - sk.DA_MIN) / 1440
    out, tab = {}, []
    for (r, tf), x in tutte.groupby(["regola", "tempo"]):
        b = sk.bootstrap_giorni(x)
        anno = pd.to_datetime(x["giorno"] * 86400, unit="s").dt.year
        per_anno = {int(a): float(y["netto"].mean()) for a, y in x.groupby(anno)}
        per_moneta = {m: float(y["netto"].mean()) for m, y in x.groupby("simbolo")}
        positive = sum(1 for v in per_moneta.values() if v > 0)
        k = f"{r} {tf}m"
        out[k] = {"operazioni": int(len(x)), "al_giorno": float(len(x) / giorni_tot / len(sk.MONETE)), "lordo": float(x["lordo"].mean()), "netto": b,
                  "vinte": float((x["netto"] > 0).mean()), "per_anno": per_anno, "monete_positive": positive,
                  "valida": bool(b["p"] <= soglia and b["media"] > 0 and all(v > 0 for v in per_anno.values()) and positive >= 4)}
        tab.append((k, out[k]))
    (RIS / "esame.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    pc = lambda v: f"{100 * v:+.3f}%"  # noqa: E731
    righe = ["# Programma 7 — risultati della quarantanovesima prova (SK2: divergenze, candele e intervallo a 1 e 5 minuti)", "",
             "Regole in `QUARANTANOVESIMA.md` (scritte prima). Stesse monete, periodo, costi ed esame della prova 108.", "",
             "| Regola e tempo | Operazioni (al giorno per moneta) | Lordo a operazione | Netto a operazione | p | Vinte | Per anno (netto) | Monete positive |",
             "|---|---|---|---|---|---|---|---|"]
    for k, v in sorted(tab, key=lambda t: -t[1]["netto"]["media"]):
        righe.append(f"| {k} | {v['operazioni']} ({v['al_giorno']:.1f}) | {pc(v['lordo'])} | {pc(v['netto']['media'])} | {v['netto']['p']:.3f} | "
                     f"{100 * v['vinte']:.0f}% | " + ", ".join(f"{a} {pc(m)}" for a, m in v["per_anno"].items()) + f" | {v['monete_positive']} su 6 |")
    valide = [k for k, v in out.items() if v["valida"]]
    righe += ["", f"**Esito: {len(valide)} valide su {VARIANTI}** (soglia p ≤ {soglia:.5f}, positiva in ogni anno, su almeno 4 monete)."]
    testo = "\n".join(righe) + "\n"
    (QUI / "RISULTATI_QUARANTANOVESIMA.md").write_text(testo, encoding="utf-8")
    log(testo)
    return out


if __name__ == "__main__":
    esegui(log=lambda x: print(x, flush=True))
    print("QUARANTANOVESIMA FINITA", flush=True)
