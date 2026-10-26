"""Programma 7, quarantaseiesima prova (QUARANTASEIESIMA.md): SK, lo scalping con gli indicatori classici a 1 e 5 minuti del documento
del proprietario (26 ottobre 2026): 9 regole × 2 tempi su 6 monete grandi, 2024-2026, stop 1 ATR e obiettivo 2 ATR dove il documento
non dice l'uscita.

Uso: python3 -m research.programma7.quarantaseiesima
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from numba import njit

from research.programma6 import dati as d6
from research.programma6 import seconda as sc

QUI = Path(__file__).parent
RIS = QUI / "risultati_quarantaseiesima"
MONETE = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "XRPUSDT", "DOGEUSDT", "BNBUSDT"]
SCARTO = {"BTCUSDT": 0.0001, "ETHUSDT": 0.0001, "SOLUSDT": 0.0001}
SCARTO_ALTRE, TAKER, MAKER = 0.0002, 0.0005, 0.0002
DA_MIN = sc.giorno(2024, 1, 1) * 1440
A_MIN = sc.giorno(2026, 10, 1) * 1440
MAX_CANDELE = 60
REGOLE = ["ema_9_21_rsi", "ema5", "rsi7_80_20", "bollinger", "macd", "stocastico_533", "vwap", "ritracciamento", "rottura_volume"]
VARIANTI = 18


def candele(simbolo: str, minuti: int) -> pd.DataFrame:
    df = d6.minuti_tutti(simbolo)
    df = df[(df.index >= DA_MIN) & (df.index < A_MIN)]
    if minuti == 1:
        return df[["open", "high", "low", "close", "volume"]].copy()
    g = df.assign(b=df.index // minuti)
    b = g.groupby("b").agg(open=("open", "first"), high=("high", "max"), low=("low", "min"), close=("close", "last"),
                           volume=("volume", "sum"), n=("close", "size"))
    b = b[b["n"] == minuti].drop(columns="n")
    b.index = b.index * minuti
    return b


def _ema(x: pd.Series, n: int) -> pd.Series:
    return x.ewm(span=n, adjust=False).mean()


def _rsi(c: pd.Series, n: int) -> pd.Series:
    d = c.diff()
    su = d.clip(lower=0).ewm(alpha=1 / n, adjust=False).mean()
    giu = (-d.clip(upper=0)).ewm(alpha=1 / n, adjust=False).mean()
    return 100 - 100 / (1 + su / giu.replace(0, np.nan))


def _atr(df: pd.DataFrame, n: int = 14) -> pd.Series:
    pc = df["close"].shift()
    tr = pd.concat([df["high"] - df["low"], (df["high"] - pc).abs(), (df["low"] - pc).abs()], axis=1).max(axis=1)
    return tr.ewm(alpha=1 / n, adjust=False).mean()


def segnali(df: pd.DataFrame, regola: str) -> tuple:
    """(direzione al segnale: +1, -1, 0; stop; obiettivo; prezzo d'entrata o NaN per «apertura della candela dopo»; candela d'entrata
    = segnale + 1). Stop e obiettivo come livelli assoluti calcolati sulla candela del segnale (per le regole a ATR rispetto alla
    chiusura del segnale; si ricalcolano sull'entrata vera in `_simula` con la stessa distanza)."""
    o, h, l, c, v = (df[k] for k in ("open", "high", "low", "close", "volume"))
    atr = _atr(df)
    n = len(df)
    dirz = np.zeros(n, dtype=np.int64)
    dist_stop = atr.to_numpy().copy()
    dist_ob = 2 * atr.to_numpy()
    prezzo = np.full(n, np.nan)
    livello_ob = np.full(n, np.nan)            # obiettivo a livello fisso (Bollinger)
    if regola == "ema_9_21_rsi":
        e9, e21, r = _ema(c, 9), _ema(c, 21), _rsi(c, 14)
        su = (e9 > e21) & (e9.shift() <= e21.shift())
        giu = (e9 < e21) & (e9.shift() >= e21.shift())
        dirz[(su & (r > 50)).to_numpy()] = 1
        dirz[(giu & (r < 50)).to_numpy()] = -1
    elif regola == "ema5":
        e5 = _ema(c, 5)
        sopra = (l > e5).to_numpy()            # candela tutta sopra la EMA 5: short se la dopo rompe il minimo
        sotto = (h < e5).to_numpy()
        hh, ll, oo = h.to_numpy(), l.to_numpy(), o.to_numpy()
        for i in range(n - 1):
            if sopra[i] and ll[i + 1] < ll[i]:
                dirz[i] = -1
                prezzo[i] = min(ll[i], oo[i + 1])
                dist_stop[i] = hh[i] - prezzo[i]
                dist_ob[i] = 3 * dist_stop[i]
            elif sotto[i] and hh[i + 1] > hh[i]:
                dirz[i] = 1
                prezzo[i] = max(hh[i], oo[i + 1])
                dist_stop[i] = prezzo[i] - ll[i]
                dist_ob[i] = 3 * dist_stop[i]
    elif regola == "rsi7_80_20":
        r = _rsi(c, 7)
        dirz[((r < 80) & (r.shift() >= 80)).to_numpy()] = -1
        dirz[((r > 20) & (r.shift() <= 20)).to_numpy()] = 1
    elif regola == "bollinger":
        m, s = c.rolling(20).mean(), c.rolling(20).std(ddof=0)
        dirz[(c < m - 2 * s).to_numpy()] = 1
        dirz[(c > m + 2 * s).to_numpy()] = -1
        livello_ob = m.to_numpy()
    elif regola == "macd":
        mc = _ema(c, 12) - _ema(c, 26)
        sg = _ema(mc, 9)
        dirz[((mc > sg) & (mc.shift() <= sg.shift())).to_numpy()] = 1
        dirz[((mc < sg) & (mc.shift() >= sg.shift())).to_numpy()] = -1
    elif regola == "stocastico_533":
        lo5, hi5 = l.rolling(5).min(), h.rolling(5).max()
        k = (100 * (c - lo5) / (hi5 - lo5).replace(0, np.nan)).rolling(3).mean()
        dd = k.rolling(3).mean()
        dirz[((k > dd) & (k.shift() <= dd.shift()) & (k < 20)).to_numpy()] = 1
        dirz[((k < dd) & (k.shift() >= dd.shift()) & (k > 80)).to_numpy()] = -1
    elif regola == "vwap":
        giorno = df.index.to_numpy() // 1440
        tp = (h + l + c) / 3
        pv = (tp * v).groupby(giorno).cumsum()
        vv = v.groupby(giorno).cumsum()
        vw = pv / vv.replace(0, np.nan)
        dirz[((l <= vw) & (c > vw) & (c.shift() > vw.shift())).to_numpy()] = 1
        dirz[((h >= vw) & (c < vw) & (c.shift() < vw.shift())).to_numpy()] = -1
        dist_stop = 0.0025 * c.to_numpy()
        dist_ob = 0.005 * c.to_numpy()
    elif regola == "ritracciamento":
        e9, e14, e20 = _ema(c, 9), _ema(c, 14), _ema(c, 20)
        r = _rsi(c, 14)
        st = 100 * (r - r.rolling(14).min()) / (r.rolling(14).max() - r.rolling(14).min()).replace(0, np.nan)
        kk = st.rolling(3).mean()
        su = (e9 > e14) & (e14 > e20) & (c < e9) & (c > e20) & (kk < 20)
        giu = (e9 < e14) & (e14 < e20) & (c > e9) & (c < e20) & (kk > 80)
        dirz[su.to_numpy()] = 1
        dirz[giu.to_numpy()] = -1
    elif regola == "rottura_volume":
        hi20, lo20 = h.shift().rolling(20).max(), l.shift().rolling(20).min()
        vm = v.shift().rolling(20).mean()
        dirz[((c > hi20) & (v > 1.5 * vm)).to_numpy()] = 1
        dirz[((c < lo20) & (v > 1.5 * vm)).to_numpy()] = -1
    ok = np.isfinite(dist_stop) & (dist_stop > 0) & np.isfinite(dist_ob) & (dist_ob > 0)
    dirz[~ok] = 0
    return dirz, dist_stop, dist_ob, prezzo, livello_ob


@njit(cache=True)
def _simula(o, h, l, c, dirz, dist_stop, dist_ob, prezzo, livello_ob, costo_m, max_c):
    n = len(o)
    out_i = np.empty(n, dtype=np.int64)
    out_d = np.empty(n, dtype=np.int64)
    out_lordo = np.empty(n)
    out_motivo = np.empty(n, dtype=np.int64)       # 0 stop, 1 obiettivo, 2 tempo
    k = 0
    libero = 0
    for i in range(n - 1):
        if dirz[i] == 0 or i < libero:
            continue
        e = i + 1
        p0 = prezzo[i] if not np.isnan(prezzo[i]) else o[e]
        d = dirz[i]
        stop = p0 - d * dist_stop[i]
        if not np.isnan(livello_ob[i]):
            ob = livello_ob[i]
            if (ob - p0) * d <= 0:                 # la media e' gia' dietro l'entrata: niente operazione
                continue
        else:
            ob = p0 + d * dist_ob[i]
        uscita, px, motivo = -1, 0.0, 2
        for j in range(e, min(n, e + max_c)):
            if d == 1:
                if l[j] <= stop:
                    px = stop if o[j] >= stop else o[j]
                    uscita, motivo = j, 0
                    break
                if h[j] >= ob:
                    px = ob if o[j] <= ob else o[j]
                    uscita, motivo = j, 1
                    break
            else:
                if h[j] >= stop:
                    px = stop if o[j] <= stop else o[j]
                    uscita, motivo = j, 0
                    break
                if l[j] <= ob:
                    px = ob if o[j] >= ob else o[j]
                    uscita, motivo = j, 1
                    break
        if uscita < 0:
            uscita = min(n, e + max_c) - 1
            px = c[uscita]
            motivo = 2
        out_i[k] = e
        out_d[k] = d
        out_lordo[k] = d * (px / p0 - 1)
        out_motivo[k] = motivo
        k += 1
        libero = uscita + 1
    return out_i[:k], out_d[:k], out_lordo[:k], out_motivo[:k]


def operazioni(df: pd.DataFrame, regola: str, simbolo: str) -> pd.DataFrame:
    dirz, ds, dob, pz, lob = segnali(df, regola)
    a = [x.to_numpy(np.float64) for x in (df["open"], df["high"], df["low"], df["close"])]
    sp = SCARTO.get(simbolo, SCARTO_ALTRE)
    costo_m = TAKER + sp
    ei, dd, lordo, mot = _simula(a[0], a[1], a[2], a[3], dirz, ds.astype(np.float64), dob.astype(np.float64),
                                 pz.astype(np.float64), lob.astype(np.float64), costo_m, MAX_CANDELE)
    costi = costo_m + np.where(mot == 1, MAKER, costo_m)
    minuto = df.index.to_numpy()[ei]
    return pd.DataFrame({"minuto": minuto, "giorno": minuto // 1440, "lato": dd, "lordo": lordo, "netto": lordo - costi, "motivo": mot})


def bootstrap_giorni(x: pd.DataFrame, n: int = 5000, seme: int = 2026) -> dict:
    g = x.groupby("giorno")["netto"]
    somme, conte = g.sum().to_numpy(), g.count().to_numpy()
    rng = np.random.default_rng(seme)
    idx = rng.integers(0, len(somme), size=(n, len(somme)))
    medie = somme[idx].sum(axis=1) / conte[idx].sum(axis=1)
    return {"media": float(somme.sum() / conte.sum()), "basso": float(np.quantile(medie, 0.025)), "alto": float(np.quantile(medie, 0.975)),
            "p": float((np.sum(medie <= 0) + 1) / (n + 1))}


def esegui(log=print) -> dict:
    RIS.mkdir(exist_ok=True)
    tutte = []
    for s in MONETE:
        for tf in (1, 5):
            df = candele(s, tf)
            for r in REGOLE:
                op = operazioni(df, r, s)
                op["simbolo"], op["tempo"], op["regola"] = s, tf, r
                tutte.append(op)
            log(f"[quarantaseiesima] {s} a {tf} minuti: fatto")
    tutte = pd.concat(tutte, ignore_index=True)
    tutte.to_csv(RIS / "operazioni_SK.csv.gz", index=False)
    soglia = 0.01 / VARIANTI
    tab, out = [], {}
    giorni_tot = (A_MIN - DA_MIN) / 1440
    for (r, tf), x in tutte.groupby(["regola", "tempo"]):
        b = bootstrap_giorni(x)
        anno = pd.to_datetime(x["giorno"] * 86400, unit="s").dt.year
        per_anno = {int(a): float(y["netto"].mean()) for a, y in x.groupby(anno)}
        per_moneta = {m: float(y["netto"].mean()) for m, y in x.groupby("simbolo")}
        positive = sum(1 for v in per_moneta.values() if v > 0)
        valida = b["p"] <= soglia and b["media"] > 0 and all(v > 0 for v in per_anno.values()) and positive >= 4
        chiave = f"{r} {tf}m"
        out[chiave] = {"operazioni": int(len(x)), "al_giorno": float(len(x) / giorni_tot / len(MONETE)), "lordo": float(x["lordo"].mean()),
                       "netto": b, "vinte": float((x["netto"] > 0).mean()), "obiettivi": float((x["motivo"] == 1).mean()),
                       "per_anno": per_anno, "per_moneta": per_moneta, "monete_positive": positive, "valida": bool(valida)}
        tab.append((chiave, out[chiave]))
    (RIS / "esame.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    pc = lambda v: f"{100 * v:+.3f}%"  # noqa: E731
    righe = ["# Programma 7 — risultati della quarantaseiesima prova (SK: gli indicatori classici a 1 e 5 minuti)", "",
             "Regole in `QUARANTASEIESIMA.md` (scritte prima). BTC, ETH, SOL, XRP, DOGE, BNB; dal 1° gennaio 2024 al 30 settembre 2026.", "",
             "| Regola e tempo | Operazioni (al giorno per moneta) | Lordo a operazione | Netto a operazione | p | Vinte | Obiettivi | Per anno (netto) | Monete positive |",
             "|---|---|---|---|---|---|---|---|---|"]
    for chiave, v in sorted(tab, key=lambda t: -t[1]["netto"]["media"]):
        righe.append(f"| {chiave} | {v['operazioni']} ({v['al_giorno']:.1f}) | {pc(v['lordo'])} | {pc(v['netto']['media'])} | {v['netto']['p']:.3f} | "
                     f"{100 * v['vinte']:.0f}% | {100 * v['obiettivi']:.0f}% | " + ", ".join(f"{a} {pc(m)}" for a, m in v["per_anno"].items())
                     + f" | {v['monete_positive']} su 6 |")
    valide = [k for k, v in out.items() if v["valida"]]
    righe += ["", f"**Esito: {len(valide)} valide su {VARIANTI}** (soglia per ciascuna p ≤ {soglia:.5f}, positiva in ogni anno, su almeno 4 monete)"
              + (": " + ", ".join(valide) if valide else "") + "."]
    testo = "\n".join(righe) + "\n"
    (QUI / "RISULTATI_QUARANTASEIESIMA.md").write_text(testo, encoding="utf-8")
    log(testo)
    return out


if __name__ == "__main__":
    esegui(log=lambda x: print(x, flush=True))
    print("QUARANTASEIESIMA FINITA", flush=True)
