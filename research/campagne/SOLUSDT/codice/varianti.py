"""Le varianti della campagna SOLUSDT: una costruttrice per id (regole in ipotesi.md).

Ogni costruttrice prende la Serie e restituisce le Regole (segnale, condizione, esci),
tutte CAUSALI salvo il controllo positivo, che legge la barra dopo di proposito.
``segnale(i)`` e' None finche' TUTTI gli indicatori della variante (anche quelli della
condizione) non sono calcolabili: e' il riscaldamento, che la (a) e la (b) rispettano.
"""
from __future__ import annotations

import math
from typing import Callable, Dict, Optional

import numpy as np

from comune import Regole, Segnale, Serie, arr, atr, ema, ms_tf, rolling_max, rolling_min, rolling_std, rsi, sma, ritardato


def _ok(*valori) -> bool:
    return all(v is not None and not (isinstance(v, float) and math.isnan(v)) for v in valori)


def segnale_atr(direzione: str, close: np.ndarray, a: np.ndarray, k_stop: float, k_target: Optional[float],
                pronto: np.ndarray) -> Callable[[int], Optional[Segnale]]:
    """Stop (e target) a k volte l'ATR dal close della barra di segnale."""
    lato = 1 if direzione == "long" else -1

    def segnale(i: int) -> Optional[Segnale]:
        if not pronto[i] or not _ok(a[i]) or a[i] <= 0:
            return None
        stop = close[i] - lato * k_stop * a[i]
        if stop <= 0:
            return None
        target = close[i] + lato * k_target * a[i] if k_target is not None else None
        return Segnale(direzione, stop, target)
    return segnale


def esci_dopo(n_barre: int) -> Callable[[int, int], bool]:
    """Chiude all'apertura della barra dopo la n-esima barra tenuta."""
    return lambda i, i_ing: i - i_ing + 1 >= n_barre


def pronto_da(n: int, *serie: np.ndarray) -> np.ndarray:
    ok = np.ones(n, dtype=bool)
    for s in serie:
        ok &= ~np.isnan(s)
    return ok


# --------------------------------------------------------------------------- #
# Controllo positivo degli strumenti (nota, non variante): legge la barra dopo
# --------------------------------------------------------------------------- #

def controllo_positivo(s: Serie) -> Regole:
    c = s.last
    close = arr(c, "close")
    a = atr(c, 14)
    n = len(c)
    pronto = pronto_da(n, a)
    pronto[-1] = False
    futuro = np.append(close[1:], np.nan)  # LOOKAHEAD DICHIARATO: il close della barra dopo
    cond = lambda i: i + 1 < n and futuro[i] > c[i + 1].open  # la barra dopo chiude sopra la sua apertura
    return Regole(segnale_atr("long", close, a, 2.0, None, pronto), cond, esci_dopo(1))


def rendimenti(close: np.ndarray) -> np.ndarray:
    r = np.full(len(close), np.nan)
    r[1:] = close[1:] / close[:-1] - 1
    return r


def sigma_precedente(r: np.ndarray, n: int) -> np.ndarray:
    """sigma dei rendimenti delle n barre PRECEDENTI (barra i esclusa)."""
    return ritardato(rolling_std(r, n), 1)


def base(s: Serie):
    c = s.last
    return c, arr(c, "close"), arr(c, "high"), arr(c, "low"), arr(c, "open"), len(c)


# --------------------------------------------------------------------------- #
# I-01 momentum della serie (1d)
# --------------------------------------------------------------------------- #

def _i01(direzione: str, tenuta: int):
    def costr(s: Serie) -> Regole:
        c, close, h, l, o, n = base(s)
        a = atr(c, 14)
        r7 = np.full(n, np.nan)
        r7[7:] = close[7:] / close[:-7] - 1
        pronto = pronto_da(n, a, r7)
        cond = (lambda i: r7[i] > 0) if direzione == "long" else (lambda i: r7[i] < 0)
        return Regole(segnale_atr(direzione, close, a, 2.0, None, pronto), cond, esci_dopo(tenuta))
    return costr


# --------------------------------------------------------------------------- #
# I-02 rottura del canale, tartarughe (4h)
# --------------------------------------------------------------------------- #

def _i02(direzione: str):
    def costr(s: Serie) -> Regole:
        c, close, h, l, o, n = base(s)
        a = atr(c, 20)
        max20 = ritardato(rolling_max(h, 20), 1)
        min20 = ritardato(rolling_min(l, 20), 1)
        max10 = ritardato(rolling_max(h, 10), 1)
        min10 = ritardato(rolling_min(l, 10), 1)
        pronto = pronto_da(n, a, max20, min20, max10, min10)
        if direzione == "long":
            cond = lambda i: close[i] > max20[i]
            esci = lambda i, i_ing: close[i] < min10[i]
        else:
            cond = lambda i: close[i] < min20[i]
            esci = lambda i, i_ing: close[i] > max10[i]
        return Regole(segnale_atr(direzione, close, a, 2.0, None, pronto), cond, esci)
    return costr


# --------------------------------------------------------------------------- #
# I-03 incrocio sopra la media di 50 con banda 1% (4h, long)
# --------------------------------------------------------------------------- #

def _i03_gen(tenuta: int):
    def costr(s: Serie) -> Regole:
        c, close, h, l, o, n = base(s)
        a = atr(c, 14)
        m = sma(close, 50)
        m1 = ritardato(m, 1)
        c1 = ritardato(close, 1)
        pronto = pronto_da(n, a, m1)
        cond = lambda i: c1[i] <= 1.01 * m1[i] and close[i] > 1.01 * m[i]
        return Regole(segnale_atr("long", close, a, 3.0, None, pronto), cond, esci_dopo(tenuta))
    return costr


_i03 = _i03_gen(60)
_i03b = _i03_gen(120)


# --------------------------------------------------------------------------- #
# I-04 RSI(2) di Connors (4h)
# --------------------------------------------------------------------------- #

def _i04(direzione: str, soglia: Optional[float] = None):
    soglia = soglia if soglia is not None else (5 if direzione == "long" else 95)

    def costr(s: Serie) -> Regole:
        c, close, h, l, o, n = base(s)
        a = atr(c, 14)
        m200 = sma(close, 200)
        m5 = sma(close, 5)
        r2 = rsi(close, 2)
        pronto = pronto_da(n, a, m200, m5, r2)
        if direzione == "long":
            cond = lambda i: close[i] > m200[i] and r2[i] < soglia
            esci = lambda i, i_ing: close[i] > m5[i]
        else:
            cond = lambda i: close[i] < m200[i] and r2[i] > soglia
            esci = lambda i, i_ing: close[i] < m5[i]
        return Regole(segnale_atr(direzione, close, a, 3.0, None, pronto), cond, esci)
    return costr


# --------------------------------------------------------------------------- #
# I-05 inversione dopo movimento estremo (1h)
# --------------------------------------------------------------------------- #

def _i05(direzione: str):
    def costr(s: Serie) -> Regole:
        c, close, h, l, o, n = base(s)
        a = atr(c, 14)
        r = rendimenti(close)
        sg = sigma_precedente(r, 168)
        pronto = pronto_da(n, a, sg, r)
        cond = (lambda i: r[i] < -3 * sg[i]) if direzione == "long" else (lambda i: r[i] > 3 * sg[i])
        return Regole(segnale_atr(direzione, close, a, 2.0, None, pronto), cond, esci_dopo(6))
    return costr


# --------------------------------------------------------------------------- #
# I-06 inversione dei cali con volume alto (4h, long)
# --------------------------------------------------------------------------- #

def _i06_gen(mult: float):
    def costr(s: Serie) -> Regole:
        c, close, h, l, o, n = base(s)
        a = atr(c, 14)
        r = rendimenti(close)
        sg = sigma_precedente(r, 90)
        v = arr(c, "volume")
        vm = ritardato(sma(v, 42), 1)
        pronto = pronto_da(n, a, sg, vm, r)
        cond = lambda i: r[i] < -2 * sg[i] and v[i] > mult * vm[i]
        return Regole(segnale_atr("long", close, a, 2.0, None, pronto), cond, esci_dopo(6))
    return costr


_i06 = _i06_gen(2.0)
_i06b = _i06_gen(1.5)


# --------------------------------------------------------------------------- #
# I-07 NR7 e rottura (4h)
# --------------------------------------------------------------------------- #

def _i07(direzione: str):
    def costr(s: Serie) -> Regole:
        c, close, h, l, o, n = base(s)
        rng = h - l
        minimo7 = rolling_min(rng, 7)
        nr7 = (rng <= minimo7) & ~np.isnan(minimo7)  # la barra ha l'escursione minima delle ultime 7
        pronto = np.zeros(n, dtype=bool)
        pronto[1:] = ~np.isnan(minimo7[:-1])
        lato = 1 if direzione == "long" else -1

        def segnale(i):
            if i < 1 or not pronto[i]:
                return None
            stop = l[i - 1] if lato == 1 else h[i - 1]
            if stop <= 0:
                return None
            return Segnale(direzione, stop, None)
        if direzione == "long":
            cond = lambda i: i >= 1 and nr7[i - 1] and close[i] > h[i - 1]
        else:
            cond = lambda i: i >= 1 and nr7[i - 1] and close[i] < l[i - 1]
        return Regole(segnale, cond, esci_dopo(6))
    return costr


# --------------------------------------------------------------------------- #
# I-08 lunedi' (1d, long)
# --------------------------------------------------------------------------- #

def _i08(s: Serie) -> Regole:
    from datetime import datetime, timezone
    c, close, h, l, o, n = base(s)
    a = atr(c, 14)
    domenica = np.array([datetime.fromtimestamp(x.ts / 1000, tz=timezone.utc).weekday() == 6 for x in c])
    pronto = pronto_da(n, a)
    return Regole(segnale_atr("long", close, a, 2.0, None, pronto), lambda i: bool(domenica[i]), esci_dopo(1))


# --------------------------------------------------------------------------- #
# I-09 prima mezz'ora -> ultima mezz'ora (30m)
# --------------------------------------------------------------------------- #

def _i09(direzione: str):
    def costr(s: Serie) -> Regole:
        c, close, h, l, o, n = base(s)
        a = atr(c, 14)
        per_ts = {x.ts: k for k, x in enumerate(c)}
        ora = 3_600_000
        prima = np.full(n, np.nan)  # alla barra delle 23:00: rendimento della prima mezz'ora del giorno
        for k, x in enumerate(c):
            if x.ts % (24 * ora) == 23 * ora:
                j = per_ts.get(x.ts - 23 * ora)
                if j is not None:
                    prima[k] = c[j].close / c[j].open - 1
        pronto = pronto_da(n, a)
        if direzione == "long":
            cond = lambda i: not math.isnan(prima[i]) and prima[i] > 0
        else:
            cond = lambda i: not math.isnan(prima[i]) and prima[i] < 0
        return Regole(segnale_atr(direzione, close, a, 2.0, None, pronto), cond, esci_dopo(1))
    return costr


# --------------------------------------------------------------------------- #
# I-10 funding estremo (8h)
# --------------------------------------------------------------------------- #

def _i10(direzione: str, soglia: float = 0.0005):
    def costr(s: Serie) -> Regole:
        from bisect import bisect_right
        c, close, h, l, o, n = base(s)
        a = atr(c, 14)
        ts_f = [t for t, _ in s.funding]
        tassi = [r for _, r in s.funding]
        media3 = np.full(n, np.nan)
        for k, x in enumerate(c):
            j = bisect_right(ts_f, x.close_ts)
            if j >= 3:
                media3[k] = sum(tassi[j - 3:j]) / 3
        pronto = pronto_da(n, a, media3)
        cond = (lambda i: media3[i] > soglia) if direzione == "short" else (lambda i: media3[i] < -soglia)
        return Regole(segnale_atr(direzione, close, a, 2.0, None, pronto), cond, esci_dopo(3))
    return costr


# --------------------------------------------------------------------------- #
# I-11 BTC guida, SOL segue (1h)
# --------------------------------------------------------------------------- #

def _i11(direzione: str):
    def costr(s: Serie) -> Regole:
        c, close, h, l, o, n = base(s)
        a = atr(c, 14)
        passo = ms_tf(s.tf)
        rb = np.full(n, np.nan)
        for k, x in enumerate(c):
            b, b0 = s.btc.get(x.ts), s.btc.get(x.ts - passo)
            if b is not None and b0 is not None:
                rb[k] = b.close / b0.close - 1
        # sigma di BTC: dai rendimenti di BTC sulla sua serie completa, 168 barre precedenti
        ts_btc = sorted(s.btc)
        cb = np.array([s.btc[t].close for t in ts_btc])
        rbt = rendimenti(cb)
        sgb_tutte = sigma_precedente(rbt, 168)
        pos_btc = {t: k for k, t in enumerate(ts_btc)}
        sgb = np.array([sgb_tutte[pos_btc[x.ts]] if x.ts in pos_btc else np.nan for x in c])
        rs = np.full(n, np.nan)
        for k in range(1, n):
            if c[k].ts - c[k - 1].ts == passo:
                rs[k] = close[k] / close[k - 1] - 1
        pronto = pronto_da(n, a, sgb)
        if direzione == "long":
            cond = lambda i: not (math.isnan(rb[i]) or math.isnan(rs[i])) and rb[i] > 2 * sgb[i] and rs[i] < rb[i]
        else:
            cond = lambda i: not (math.isnan(rb[i]) or math.isnan(rs[i])) and rb[i] < -2 * sgb[i] and rs[i] > rb[i]
        return Regole(segnale_atr(direzione, close, a, 2.0, None, pronto), cond, esci_dopo(3))
    return costr


# --------------------------------------------------------------------------- #
# I-12 volume giornaliero alto (1d, long)
# --------------------------------------------------------------------------- #

def _i12_gen(q: float, tenuta: int):
    def costr(s: Serie) -> Regole:
        c, close, h, l, o, n = base(s)
        a = atr(c, 14)
        v = arr(c, "volume")
        pq = ritardato(pd_quantile(v, 49, q), 1)
        pronto = pronto_da(n, a, pq)
        return Regole(segnale_atr("long", close, a, 2.0, None, pronto), lambda i: v[i] > pq[i], esci_dopo(tenuta))
    return costr


_i12 = _i12_gen(0.9, 5)
_i12b = _i12_gen(0.8, 3)


def pd_quantile(x: np.ndarray, n: int, q: float) -> np.ndarray:
    import pandas as pd
    return pd.Series(x).rolling(n, min_periods=n).quantile(q, interpolation="linear").to_numpy()


# --------------------------------------------------------------------------- #
# I-13 numeri tondi (1h)
# --------------------------------------------------------------------------- #

def _i13(direzione: str):
    def costr(s: Serie) -> Regole:
        c, close, h, l, o, n = base(s)
        a = atr(c, 14)
        pronto = pronto_da(n, a)

        def cond(i):
            if i < 1:
                return False
            p, x = close[i - 1], close[i]
            passo = 5 * 10 ** (math.floor(math.log10(p)) - 1)
            if direzione == "long":
                livello = (math.floor(p / passo) + 1) * passo
                return p < livello <= x
            livello = (math.ceil(p / passo) - 1) * passo
            return x <= livello < p
        return Regole(segnale_atr(direzione, close, a, 2.0, None, pronto), cond, esci_dopo(4))
    return costr


VARIANTI: Dict[str, tuple] = {
    "CONTROLLO": ("1h", controllo_positivo),
    "SOLUSDT-001": ("1d", _i01("long", 7)),
    "SOLUSDT-002": ("1d", _i01("short", 7)),
    "SOLUSDT-001b": ("1d", _i01("long", 3)),
    "SOLUSDT-002b": ("1d", _i01("short", 3)),
    "SOLUSDT-003": ("4h", _i02("long")),
    "SOLUSDT-004": ("4h", _i02("short")),
    "SOLUSDT-005": ("4h", _i03),
    "SOLUSDT-006": ("4h", _i04("long")),
    "SOLUSDT-007": ("4h", _i04("short")),
    "SOLUSDT-008": ("1h", _i05("long")),
    "SOLUSDT-009": ("1h", _i05("short")),
    "SOLUSDT-010": ("4h", _i06),
    "SOLUSDT-011": ("4h", _i07("long")),
    "SOLUSDT-012": ("4h", _i07("short")),
    "SOLUSDT-013": ("1d", _i08),
    "SOLUSDT-014": ("30m", _i09("long")),
    "SOLUSDT-015": ("30m", _i09("short")),
    "SOLUSDT-016": ("8h", _i10("short")),
    "SOLUSDT-017": ("8h", _i10("long")),
    "SOLUSDT-018": ("1h", _i11("long")),
    "SOLUSDT-019": ("1h", _i11("short")),
    "SOLUSDT-020": ("1d", _i12),
    "SOLUSDT-004b": ("2h", _i02("short")),
    "SOLUSDT-005b": ("2h", _i03b),
    "SOLUSDT-006b": ("4h", _i04("long", 10)),
    "SOLUSDT-007b": ("4h", _i04("short", 90)),
    "SOLUSDT-010b": ("4h", _i06b),
    "SOLUSDT-017b": ("8h", _i10("long", 0.0001)),
    "SOLUSDT-020b": ("1d", _i12b),
    "SOLUSDT-021": ("1h", _i13("long")),
    "SOLUSDT-022": ("1h", _i13("short")),
}
