"""Le varianti di MATICUSDT, una funzione per variante (regole in ipotesi.md).

Ogni funzione riceve la ``Serie`` del suo timeframe e restituisce le ``Regole``. Tutti gli
array sono causali (all'indice i solo le barre 0..i). Stop comune: distanza = min(2 ATR(14),
6% della chiusura).
"""
from __future__ import annotations

import bisect
import math

import numpy as np

import quadro
from quadro import Regole, Serie

TIMEFRAME = {}


def tf(nome):
    def dec(f):
        TIMEFRAME[f.__name__] = nome
        return f
    return dec


def distanza_stop(s: Serie) -> np.ndarray:
    a = quadro.atr(s, 14)
    return np.minimum(2 * a, 0.06 * s.c)


def stop_long(s: Serie, pronto: np.ndarray) -> np.ndarray:
    st = s.c - distanza_stop(s)
    return np.where(pronto, st, np.nan)


def stop_short(s: Serie, pronto: np.ndarray) -> np.ndarray:
    st = s.c + distanza_stop(s)
    return np.where(pronto, st, np.nan)


def _ok(*arrays) -> np.ndarray:
    m = np.ones(len(arrays[0]), dtype=bool)
    for a in arrays:
        m &= ~np.isnan(a)
    return m


# ------------------------------------------------------------------ I-01
@tf("4h")
def V01(s):
    r = quadro.rendimento(s.c, 42)
    pronto = _ok(r, quadro.atr(s, 14))
    return Regole(s, "long", pronto & (r > 0), stop_long(s, pronto), tenuta=42)


@tf("4h")
def V02(s):
    r = quadro.rendimento(s.c, 42)
    pronto = _ok(r, quadro.atr(s, 14))
    return Regole(s, "short", pronto & (r < 0), stop_short(s, pronto), tenuta=42)


# ------------------------------------------------------------------ I-02
@tf("4h")
def V03(s):
    hh = quadro.massimo_precedente(s.h, 120)
    ll = quadro.minimo_precedente(s.l, 60)
    pronto = _ok(hh, ll, quadro.atr(s, 14))
    return Regole(s, "long", pronto & (s.c > hh), stop_long(s, pronto),
                  uscita=np.nan_to_num(s.c < ll, nan=0).astype(bool) & pronto)


@tf("4h")
def V04(s):
    ll = quadro.minimo_precedente(s.l, 120)
    hh = quadro.massimo_precedente(s.h, 60)
    pronto = _ok(hh, ll, quadro.atr(s, 14))
    return Regole(s, "short", pronto & (s.c < ll), stop_short(s, pronto),
                  uscita=(s.c > hh) & pronto)


# ------------------------------------------------------------------ I-03
def _anomalia_giornaliera(s: Serie, verso: int):
    """Primo superamento nel giorno della soglia media +/- 1 dev. std. dei 30 rendimenti giornalieri precedenti."""
    giorno = s.ts // 86_400_000
    ora = quadro.ora_utc(s)
    # chiusura di ogni giorno = close dell'ultima barra del giorno con ora 23
    chiusure = {}
    for i in range(s.n):
        if ora[i] == 23:
            chiusure[int(giorno[i])] = s.c[i]
    giorni = sorted(chiusure)
    rend = {}
    for a, b in zip(giorni, giorni[1:]):
        if b == a + 1:
            rend[b] = chiusure[b] / chiusure[a] - 1
    soglia = {}
    for g in set(int(x) for x in giorno):
        prec = [rend[d] for d in range(g - 30, g) if d in rend]
        if len(prec) == 30:
            m, sd = float(np.mean(prec)), float(np.std(prec, ddof=1))
            soglia[g] = m + verso * sd
    apertura = {}
    for i in range(s.n):
        g = int(giorno[i])
        if g not in apertura:
            apertura[g] = s.o[i]
    ingresso = np.zeros(s.n, dtype=bool)
    pronto = np.zeros(s.n, dtype=bool)
    gia = set()
    for i in range(s.n):
        g = int(giorno[i])
        if g not in soglia or ora[i] > 21:
            continue
        pronto[i] = True
        r = s.c[i] / apertura[g] - 1
        if g not in gia and verso * (r - soglia[g]) > 0:
            ingresso[i] = True
            gia.add(g)
    pronto &= _ok(quadro.atr(s, 14))
    return ingresso & pronto, pronto, ora == 23


@tf("1h")
def V05(s):
    ing, pronto, fine = _anomalia_giornaliera(s, +1)
    return Regole(s, "long", ing, stop_long(s, pronto), uscita=fine)


@tf("1h")
def V06(s):
    ing, pronto, fine = _anomalia_giornaliera(s, -1)
    return Regole(s, "short", ing, stop_short(s, pronto), uscita=fine)


# ------------------------------------------------------------------ I-04
def _prima_mezzora(s: Serie):
    minuto = quadro.minuto_del_giorno(s)
    giorno = s.ts // 86_400_000
    prima = {}
    for i in range(s.n):
        if minuto[i] == 0:
            prima[int(giorno[i])] = s.c[i] / s.o[i] - 1
    segno = np.full(s.n, np.nan)
    for i in range(s.n):
        if minuto[i] == 1380 and int(giorno[i]) in prima:
            segno[i] = prima[int(giorno[i])]
    pronto = _ok(segno, quadro.atr(s, 14))
    return segno, pronto


@tf("30m")
def V07(s):
    segno, pronto = _prima_mezzora(s)
    return Regole(s, "long", pronto & (np.nan_to_num(segno) > 0), stop_long(s, pronto), tenuta=1)


@tf("30m")
def V08(s):
    segno, pronto = _prima_mezzora(s)
    return Regole(s, "short", pronto & (np.nan_to_num(segno) < 0), stop_short(s, pronto), tenuta=1)


# ------------------------------------------------------------------ I-05
@tf("4h")
def V09(s):
    m200, m5, r2 = quadro.sma(s.c, 200), quadro.sma(s.c, 5), quadro.rsi(s.c, 2)
    pronto = _ok(m200, m5, r2, quadro.atr(s, 14))
    return Regole(s, "long", pronto & (s.c > m200) & (r2 < 5), stop_long(s, pronto),
                  uscita=pronto & (s.c > m5))


@tf("4h")
def V10(s):
    m200, m5, r2 = quadro.sma(s.c, 200), quadro.sma(s.c, 5), quadro.rsi(s.c, 2)
    pronto = _ok(m200, m5, r2, quadro.atr(s, 14))
    return Regole(s, "short", pronto & (s.c < m200) & (r2 > 95), stop_short(s, pronto),
                  uscita=pronto & (s.c < m5))


# ------------------------------------------------------------------ I-06
@tf("1d")
def V11(s):
    pronto = _ok(quadro.atr(s, 14))
    domenica = quadro.giorno_settimana(s) == 6
    return Regole(s, "long", pronto & domenica, stop_long(s, pronto), tenuta=1)


# ------------------------------------------------------------------ I-07
def _ultimo_funding(s: Serie) -> np.ndarray:
    tempi = [t for t, _ in s.funding]
    tassi = [r for _, r in s.funding]
    out = np.full(s.n, np.nan)
    for i, c in enumerate(s.candele):
        k = bisect.bisect_right(tempi, c.close_ts) - 1
        if k >= 0:
            out[i] = tassi[k]
    return out


@tf("8h")
def V12(s):
    f = _ultimo_funding(s)
    pronto = _ok(f, quadro.atr(s, 14))
    return Regole(s, "short", pronto & (np.nan_to_num(f) >= 0.0005), stop_short(s, pronto), tenuta=3)


@tf("8h")
def V13(s):
    f = _ultimo_funding(s)
    pronto = _ok(f, quadro.atr(s, 14))
    return Regole(s, "long", pronto & (np.nan_to_num(f) <= -0.0001), stop_long(s, pronto), tenuta=3)


# ------------------------------------------------------------------ I-08
@tf("1d")
def V14(s):
    mx = quadro.massimo_precedente(s.qv, 49)
    pronto = _ok(mx, quadro.atr(s, 14))
    return Regole(s, "long", pronto & (s.qv > np.nan_to_num(mx, nan=np.inf)), stop_long(s, pronto), tenuta=10)


@tf("1d")
def V15(s):
    media = np.full(s.n, np.nan)
    for i in range(50, s.n):
        media[i] = s.qv[i - 50:i].mean()
    pronto = _ok(media, quadro.atr(s, 14))
    return Regole(s, "long", pronto & (s.qv > 2 * np.nan_to_num(media, nan=np.inf)), stop_long(s, pronto), tenuta=5)


# ------------------------------------------------------------------ I-09
def _salto(s: Serie):
    r = quadro.rendimento(s.c, 1)
    sd = np.full(s.n, np.nan)
    for i in range(169, s.n):
        sd[i] = r[i - 168:i].std(ddof=1)
    pronto = _ok(sd, r, quadro.atr(s, 14))
    return r, sd, pronto


@tf("1h")
def V16(s):
    r, sd, pronto = _salto(s)
    return Regole(s, "long", pronto & (np.nan_to_num(r) < -3 * np.nan_to_num(sd, nan=np.inf)), stop_long(s, pronto), tenuta=6)


@tf("1h")
def V17(s):
    r, sd, pronto = _salto(s)
    return Regole(s, "short", pronto & (np.nan_to_num(r) > 3 * np.nan_to_num(sd, nan=np.inf)), stop_short(s, pronto), tenuta=6)


# ------------------------------------------------------------------ I-10
@tf("1d")
def V18(s):
    mx = quadro.massimo_precedente(s.h, 365)
    pronto = _ok(mx, quadro.atr(s, 14))
    return Regole(s, "long", pronto & (s.c >= 0.95 * np.nan_to_num(mx, nan=np.inf)), stop_long(s, pronto), tenuta=10)


# ------------------------------------------------------------------ I-11
def _media300(s):
    m = quadro.sma(s.c, 300)
    prima = np.concatenate([[np.nan], s.c[:-1] - m[:-1]])
    pronto = _ok(m, prima, quadro.atr(s, 14))
    return m, prima, pronto


@tf("4h")
def V19(s):
    m, prima, pronto = _media300(s)
    return Regole(s, "long", pronto & (s.c > m) & (np.nan_to_num(prima) <= 0), stop_long(s, pronto),
                  uscita=pronto & (s.c < m))


@tf("4h")
def V20(s):
    m, prima, pronto = _media300(s)
    return Regole(s, "short", pronto & (s.c < m) & (np.nan_to_num(prima) >= 0), stop_short(s, pronto),
                  uscita=pronto & (s.c > m))


# ------------------------------------------------------------------ I-12
def _stretta(s):
    m = quadro.sma(s.c, 20)
    sd = quadro.dev_std_mobile(s.c, 20)
    larg = 4 * sd / m
    min20 = np.full(s.n, np.nan)
    min1080 = np.full(s.n, np.nan)
    for i in range(s.n):
        if i >= 19 and not np.isnan(larg[i - 19:i + 1]).any():
            min20[i] = larg[i - 19:i + 1].min()
        if i >= 1080 + 19 and not np.isnan(larg[i - 1080:i]).any():
            min1080[i] = larg[i - 1080:i].min()
    pronto = _ok(m, sd, min20, min1080, quadro.atr(s, 14))
    stretta = pronto & (np.nan_to_num(min20, nan=np.inf) <= 1.1 * np.nan_to_num(min1080))
    return m, sd, stretta, pronto


@tf("4h")
def V21(s):
    m, sd, stretta, pronto = _stretta(s)
    return Regole(s, "long", stretta & (s.c > m + 2 * sd), stop_long(s, pronto), tenuta=30,
                  uscita=pronto & (s.c < m))


@tf("4h")
def V22(s):
    m, sd, stretta, pronto = _stretta(s)
    return Regole(s, "short", stretta & (s.c < m - 2 * sd), stop_short(s, pronto), tenuta=30,
                  uscita=pronto & (s.c > m))
