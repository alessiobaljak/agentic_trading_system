"""Le varianti di XRPUSDT, esattamente come scritte in ipotesi.md (regole comuni comprese).

Ogni funzione ``prepara`` usa solo barre chiuse: il valore alla barra i dipende dalle barre 0..i.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Dict

import numpy as np

from research.src import dati
from research.campagne.XRPUSDT.codice import quadro as q
from research.campagne.XRPUSDT.codice.quadro import Variante

TETTO_STOP = 0.06


def stop_da(s: Dict, k: float, direzione: str, n_atr: int = 14) -> np.ndarray:
    """Stop = chiusura -/+ min(k x ATR(n_atr), 6% della chiusura)."""
    c = s["close"]
    dist = np.minimum(k * q.atr(s, n_atr), TETTO_STOP * c)
    return c - dist if direzione == "long" else c + dist


def rendimento(c: np.ndarray, k: int = 1) -> np.ndarray:
    out = np.full(len(c), np.nan)
    out[k:] = c[k:] / c[:-k] - 1
    return out


def _nan_falso(x):
    return np.where(np.isnan(x), False, x).astype(bool)


# ---------------------------------------------------------------------------
# Dati in piu': taker buy volume e funding alla barra
# ---------------------------------------------------------------------------


def taker_buy(s: Dict) -> np.ndarray:
    """Volume taker buy (colonna 9 dei CSV klines, moneta base) sugli stessi ts della serie."""
    if "taker_buy" in s:
        return s["taker_buy"]
    tb = {}
    fine = datetime.fromtimestamp(int(s["ts"][-1]) / 1000, tz=timezone.utc).date()
    for p in dati._percorsi_presenti(q.SIMBOLO, "klines", s["tf"], q.INIZIO, fine, dati.RADICE_DEFAULT):
        for r in dati.righe_csv_da_zip(p):
            ts = dati.normalizza_ts(r[0])
            if ts not in tb and len(r) > 9 and r[9].strip():
                tb[ts] = float(r[9])
    s["taker_buy"] = np.array([tb.get(int(t), np.nan) for t in s["ts"]])
    return s["taker_buy"]


def funding_alla_barra(s: Dict) -> np.ndarray:
    """Tasso dell'ultimo settlement con istante entro la chiusura della barra i (noto a quel momento)."""
    f = s["funding"]
    ts_f = np.array([t for t, _ in f], dtype=np.int64)
    r_f = np.array([r for _, r in f])
    close_ts = np.array([c.close_ts for c in s["candele"]], dtype=np.int64)
    k = np.searchsorted(ts_f, close_ts, side="right") - 1
    out = np.where(k >= 0, r_f[np.clip(k, 0, None)], np.nan)
    return out


# ---------------------------------------------------------------------------
# I-01 momentum a una settimana (1d)
# ---------------------------------------------------------------------------


def _i01(direzione):
    def prepara(s):
        r7 = rendimento(s["close"], 7)
        cond = (r7 > 0) if direzione == "long" else (r7 < 0)
        return {"cond": _nan_falso(cond), "stop": stop_da(s, 2.0, direzione), "target": None, "warmup": 14}
    return prepara


# ---------------------------------------------------------------------------
# I-02 movimento orario estremo con volume alto (1h)
# ---------------------------------------------------------------------------


def _i02(direzione):
    def prepara(s):
        r = rendimento(s["close"], 1)
        sig = q.ritardato(q.rolling_std(r, 168), 1)
        vrel = s["volume"] / q.ritardato(q.sma(s["volume"], 168), 1)
        if direzione == "long":
            cond = (r < -2.5 * sig) & (vrel > 2)
        else:
            cond = (r > 2.5 * sig) & (vrel > 2)
        return {"cond": _nan_falso(cond), "stop": stop_da(s, 1.5, direzione), "target": None, "warmup": 170}
    return prepara


# ---------------------------------------------------------------------------
# I-03 sovrareazione giornaliera (1d)
# ---------------------------------------------------------------------------


def _i03(direzione, k):
    def prepara(s):
        r = rendimento(s["close"], 1)
        m = q.ritardato(q.sma(r, 30), 1)
        sd = q.ritardato(q.rolling_std(r, 30), 1)
        cond = (r > m + k * sd) if direzione == "long" else (r < m - k * sd)
        return {"cond": _nan_falso(cond), "stop": stop_da(s, 1.5, direzione), "target": None, "warmup": 32}
    return prepara


# ---------------------------------------------------------------------------
# I-04 funding estremo (8h)
# ---------------------------------------------------------------------------


def _i04(direzione, soglia):
    def prepara(s):
        f = funding_alla_barra(s)
        cond = (f >= soglia) if direzione == "short" else (f <= soglia)
        return {"cond": _nan_falso(cond), "stop": stop_da(s, 2.0, direzione), "target": None, "warmup": 14}
    return prepara


# ---------------------------------------------------------------------------
# I-05 lunedi' (1d)
# ---------------------------------------------------------------------------


def _i05(s):
    dom = np.array([datetime.fromtimestamp(int(t) / 1000, tz=timezone.utc).weekday() == 6 for t in s["ts"]])
    return {"cond": dom, "stop": stop_da(s, 1.5, "long"), "target": None, "warmup": 14}


# ---------------------------------------------------------------------------
# I-06 BTC guida (1h)
# ---------------------------------------------------------------------------


def _i06(direzione):
    def prepara(s):
        rb = rendimento(s["btc_close"], 1)
        rx = rendimento(s["close"], 1)
        if direzione == "long":
            cond = (rb > 0.01) & (rx < 0.5 * rb)
        else:
            cond = (rb < -0.01) & (rx > 0.5 * rb)
        return {"cond": _nan_falso(cond), "stop": stop_da(s, 1.5, direzione), "target": None, "warmup": 14}
    return prepara


# ---------------------------------------------------------------------------
# I-07 rottura del canale di 20 barre (4h)
# ---------------------------------------------------------------------------


def _i07(direzione):
    def prepara(s):
        c = s["close"]
        hh = q.ritardato(q.rolling_max(s["high"], 20), 1)
        ll = q.ritardato(q.rolling_min(s["low"], 20), 1)
        h10 = q.ritardato(q.rolling_max(s["high"], 10), 1)
        l10 = q.ritardato(q.rolling_min(s["low"], 10), 1)
        if direzione == "long":
            cond, usc = c > hh, c < l10
        else:
            cond, usc = c < ll, c > h10
        return {"cond": _nan_falso(cond), "uscita": _nan_falso(usc), "stop": stop_da(s, 2.0, direzione),
                "target": None, "warmup": 21}
    return prepara


# ---------------------------------------------------------------------------
# I-08 RSI a 2 periodi nel trend (4h)
# ---------------------------------------------------------------------------


def _i08(direzione):
    def prepara(s):
        c = s["close"]
        m200, m5, r2 = q.sma(c, 200), q.sma(c, 5), q.rsi(c, 2)
        if direzione == "long":
            cond, usc = (c > m200) & (r2 < 10), c > m5
        else:
            cond, usc = (c < m200) & (r2 > 90), c < m5
        return {"cond": _nan_falso(cond), "uscita": _nan_falso(usc), "stop": stop_da(s, 2.5, direzione),
                "target": None, "warmup": 200}
    return prepara


# ---------------------------------------------------------------------------
# I-09 compressione delle bande (1h)
# ---------------------------------------------------------------------------


def _i09(direzione, finestra=480, recenti=10):
    def prepara(s):
        c = s["close"]
        m, sd = q.sma(c, 20), q.rolling_std(c, 20)
        su, giu = m + 2 * sd, m - 2 * sd
        larg = 4 * sd / m
        minimo = q.rolling_min(larg, finestra)
        al_minimo = (larg <= minimo + 1e-15).astype(float)  # la barra j e' il minimo delle 480 fino a j
        recente = q.ritardato(q.rolling_max(al_minimo, recenti), 1)  # una delle barre i-recenti..i-1
        recente = _nan_falso(recente > 0)
        cond = recente & ((c > su) if direzione == "long" else (c < giu))
        return {"cond": _nan_falso(cond), "stop": stop_da(s, 2.0, direzione), "target": None, "warmup": 500}
    return prepara


# ---------------------------------------------------------------------------
# I-10 squilibrio degli ordini aggressivi (1h)
# ---------------------------------------------------------------------------


def _i10(direzione, soglia):
    def prepara(s):
        tb = taker_buy(s)
        v = s["volume"]
        sq = 2 * (q.sma(tb, 4) * 4) / (q.sma(v, 4) * 4) - 1
        cond = (sq > soglia) if direzione == "long" else (sq < -soglia)
        return {"cond": _nan_falso(cond), "stop": stop_da(s, 1.5, direzione), "target": None, "warmup": 14}
    return prepara


# ---------------------------------------------------------------------------
# I-11 premio del perpetuo sul mark (1h)
# ---------------------------------------------------------------------------


def _i11(direzione, soglia, caduta_massima=None, k=1.5, n_atr=14):
    def prepara(s):
        mark = np.array([c.close for c in s["mark"]])
        p = s["close"] / mark - 1
        cond = (p > soglia) if direzione == "short" else (p < -soglia)
        if caduta_massima is not None:  # ritocco: niente ingressi dopo una barra crollata oltre la soglia
            cond = cond & (rendimento(s["close"], 1) >= -caduta_massima)
        return {"cond": _nan_falso(cond), "stop": stop_da(s, k, direzione, n_atr), "target": None,
                "warmup": max(14, n_atr)}
    return prepara


# ---------------------------------------------------------------------------
# I-12 numeri tondi (1h)
# ---------------------------------------------------------------------------


def _i12(direzione):
    def prepara(s):
        c = s["close"]
        prev = q.ritardato(c, 1)
        passo = 10.0 ** (np.floor(np.log10(prev)) - 1)
        # il multiplo del passo appena sopra prev (strettamente) e appena sotto (strettamente)
        sopra = (np.floor(prev / passo + 1e-9) + 1) * passo
        sotto = (np.ceil(prev / passo - 1e-9) - 1) * passo
        if direzione == "long":
            cond = c >= sopra - 1e-12
        else:
            cond = c <= sotto + 1e-12
        return {"cond": _nan_falso(cond), "stop": stop_da(s, 1.5, direzione), "target": None, "warmup": 14}
    return prepara


# ---------------------------------------------------------------------------
# I-13 prima mezz'ora e ultima mezz'ora (30m)
# ---------------------------------------------------------------------------


def _i13(direzione):
    def prepara(s):
        ts = s["ts"]
        o, c = s["open"], s["close"]
        indice = {int(t): k for k, t in enumerate(ts)}
        giorno_ms = 86_400_000
        cond = np.zeros(len(ts), dtype=bool)
        for k, t in enumerate(ts):
            t = int(t)
            if t % giorno_ms != 23 * 3_600_000:
                continue
            j = indice.get(t - t % giorno_ms)
            if j is None:
                continue
            r = c[j] / o[j] - 1
            cond[k] = (r > 0) if direzione == "long" else (r < 0)
        return {"cond": cond, "stop": stop_da(s, 1.5, direzione), "target": None, "warmup": 14}
    return prepara


# ---------------------------------------------------------------------------
# I-14 momentum relativo XRP contro BTC (1d)
# ---------------------------------------------------------------------------


def _i14(direzione):
    def prepara(s):
        rel = rendimento(s["close"], 7) - rendimento(s["btc_close"], 7)
        cond = (rel > 0) if direzione == "long" else (rel < 0)
        return {"cond": _nan_falso(cond), "stop": stop_da(s, 2.0, direzione), "target": None, "warmup": 14}
    return prepara


# ---------------------------------------------------------------------------
# I-15 rottura dell'intervallo d'apertura della giornata UTC (1h)
# ---------------------------------------------------------------------------


def _i15(direzione):
    def prepara(s):
        ts, h, l, c = s["ts"], s["high"], s["low"], s["close"]
        indice = {int(t): k for k, t in enumerate(ts)}
        G, H = 86_400_000, 3_600_000
        n = len(ts)
        cond = np.zeros(n, dtype=bool)
        usc = np.zeros(n, dtype=bool)
        gia = {}
        for k in range(n):
            t = int(ts[k])
            g0 = t - t % G
            ora = (t - g0) // H
            if ora == 23:
                usc[k] = True
            if ora < 2 or ora > 22:
                continue
            a, b = indice.get(g0), indice.get(g0 + H)
            if a is None or b is None:
                continue
            if gia.get(g0):
                continue
            if direzione == "long" and c[k] > max(h[a], h[b]):
                cond[k] = True
                gia[g0] = True
            elif direzione == "short" and c[k] < min(l[a], l[b]):
                cond[k] = True
                gia[g0] = True
        return {"cond": cond, "uscita": usc, "stop": stop_da(s, 1.5, direzione), "target": None, "warmup": 14}
    return prepara


VARIANTI = {
    "XRPUSDT-V26": Variante("XRPUSDT-V26", "1d", "long", _i14("long"), 7, {"idea": "I-14"}),
    "XRPUSDT-V27": Variante("XRPUSDT-V27", "1d", "short", _i14("short"), 7, {"idea": "I-14"}),
    "XRPUSDT-V28": Variante("XRPUSDT-V28", "1h", "long", _i15("long"), 22, {"idea": "I-15"}),
    "XRPUSDT-V29": Variante("XRPUSDT-V29", "1h", "short", _i15("short"), 22, {"idea": "I-15"}),
    "XRPUSDT-V01": Variante("XRPUSDT-V01", "1d", "long", _i01("long"), 7, {"idea": "I-01"}),
    "XRPUSDT-V02": Variante("XRPUSDT-V02", "1d", "short", _i01("short"), 7, {"idea": "I-01"}),
    "XRPUSDT-V03": Variante("XRPUSDT-V03", "1h", "long", _i02("long"), 12, {"idea": "I-02"}),
    "XRPUSDT-V04": Variante("XRPUSDT-V04", "1h", "short", _i02("short"), 12, {"idea": "I-02"}),
    "XRPUSDT-V05": Variante("XRPUSDT-V05", "1d", "long", _i03("long", 1.5), 1, {"idea": "I-03"}),
    "XRPUSDT-V06": Variante("XRPUSDT-V06", "1d", "short", _i03("short", 1.5), 1, {"idea": "I-03"}),
    "XRPUSDT-V05b": Variante("XRPUSDT-V05b", "1d", "long", _i03("long", 1.0), 1, {"idea": "I-03"}),
    "XRPUSDT-V06b": Variante("XRPUSDT-V06b", "1d", "short", _i03("short", 1.0), 1, {"idea": "I-03"}),
    "XRPUSDT-V07": Variante("XRPUSDT-V07", "8h", "short", _i04("short", 0.0005), 9, {"idea": "I-04"}),
    "XRPUSDT-V08": Variante("XRPUSDT-V08", "8h", "long", _i04("long", -0.0002), 9, {"idea": "I-04"}),
    "XRPUSDT-V07b": Variante("XRPUSDT-V07b", "8h", "short", _i04("short", 0.0003), 9, {"idea": "I-04"}),
    "XRPUSDT-V08b": Variante("XRPUSDT-V08b", "8h", "long", _i04("long", -0.0001), 9, {"idea": "I-04"}),
    "XRPUSDT-V09": Variante("XRPUSDT-V09", "1d", "long", _i05, 1, {"idea": "I-05"}),
    "XRPUSDT-V10": Variante("XRPUSDT-V10", "1h", "long", _i06("long"), 4, {"idea": "I-06"}),
    "XRPUSDT-V11": Variante("XRPUSDT-V11", "1h", "short", _i06("short"), 4, {"idea": "I-06"}),
    "XRPUSDT-V12": Variante("XRPUSDT-V12", "4h", "long", _i07("long"), 30, {"idea": "I-07"}),
    "XRPUSDT-V13": Variante("XRPUSDT-V13", "4h", "short", _i07("short"), 30, {"idea": "I-07"}),
    "XRPUSDT-V14": Variante("XRPUSDT-V14", "4h", "long", _i08("long"), 30, {"idea": "I-08"}),
    "XRPUSDT-V15": Variante("XRPUSDT-V15", "4h", "short", _i08("short"), 30, {"idea": "I-08"}),
    "XRPUSDT-V16": Variante("XRPUSDT-V16", "1h", "long", _i09("long"), 24, {"idea": "I-09"}),
    "XRPUSDT-V17": Variante("XRPUSDT-V17", "1h", "short", _i09("short"), 24, {"idea": "I-09"}),
    "XRPUSDT-V16b": Variante("XRPUSDT-V16b", "1h", "long", _i09("long", 240, 24), 24, {"idea": "I-09"}),
    "XRPUSDT-V17b": Variante("XRPUSDT-V17b", "1h", "short", _i09("short", 240, 24), 24, {"idea": "I-09"}),
    "XRPUSDT-V18": Variante("XRPUSDT-V18", "1h", "long", _i10("long", 0.10), 4, {"idea": "I-10"}),
    "XRPUSDT-V19": Variante("XRPUSDT-V19", "1h", "short", _i10("short", 0.10), 4, {"idea": "I-10"}),
    "XRPUSDT-V18b": Variante("XRPUSDT-V18b", "1h", "long", _i10("long", 0.06), 4, {"idea": "I-10"}),
    "XRPUSDT-V19b": Variante("XRPUSDT-V19b", "1h", "short", _i10("short", 0.06), 4, {"idea": "I-10"}),
    "XRPUSDT-V20": Variante("XRPUSDT-V20", "1h", "short", _i11("short", 0.0015), 4, {"idea": "I-11"}),
    "XRPUSDT-V21": Variante("XRPUSDT-V21", "1h", "long", _i11("long", 0.0015), 4, {"idea": "I-11"}),
    "XRPUSDT-V20b": Variante("XRPUSDT-V20b", "1h", "short", _i11("short", 0.0010), 4, {"idea": "I-11"}),
    "XRPUSDT-V21b": Variante("XRPUSDT-V21b", "1h", "long", _i11("long", 0.0010), 4, {"idea": "I-11"}),
    "XRPUSDT-V21r1": Variante("XRPUSDT-V21r1", "1h", "long", _i11("long", 0.0015, 0.10), 4, {"idea": "I-11"}),
    "XRPUSDT-V21r2": Variante("XRPUSDT-V21r2", "1h", "long", _i11("long", 0.0015, 0.10), 8, {"idea": "I-11"}),
    "XRPUSDT-V21r3": Variante("XRPUSDT-V21r3", "1h", "long", _i11("long", 0.0020, 0.10), 4, {"idea": "I-11"}),
    "XRPUSDT-V22": Variante("XRPUSDT-V22", "1h", "long", _i12("long"), 6, {"idea": "I-12"}),
    "XRPUSDT-V23": Variante("XRPUSDT-V23", "1h", "short", _i12("short"), 6, {"idea": "I-12"}),
    "XRPUSDT-V24": Variante("XRPUSDT-V24", "30m", "long", _i13("long"), 1, {"idea": "I-13"}),
    "XRPUSDT-V25": Variante("XRPUSDT-V25", "30m", "short", _i13("short"), 1, {"idea": "I-13"}),
}
