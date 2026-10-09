"""Le varianti della campagna BNBUSDT, una funzione per variante (regole come in ipotesi.md).

Ogni funzione restituisce una ``comune.Variante``. Gli indicatori in ``prepara`` sono causali
(il valore all'indice i usa barre fino a i), salvo il controllo positivo, che legge la barra
futura di proposito.
"""
from __future__ import annotations

import math
from typing import Dict

import numpy as np

import comune as C
from comune import Segnale, Variante


def _stop_atr(direzione: str, k: float, chiave_atr: str = "atr"):
    """Segnale con stop a k ATR dalla chiusura della barra di segnale, senza target."""
    def segnale(ind, i, candele):
        a = ind[chiave_atr][i]
        if not np.isfinite(a) or a <= 0:
            return None
        c = ind["close"][i]
        stop = c - k * a if direzione == "long" else c + k * a
        if stop <= 0:
            return None
        return Segnale(direzione, stop)
    return segnale


def _uscita_tempo(n_barre: int):
    def uscita(ind, i, barre, pos, candele):
        return barre >= n_barre
    return uscita


# ---------------------------------------------------------------------------
# Controllo positivo degli strumenti (nota, non e' una variante)
# ---------------------------------------------------------------------------

def controllo_positivo() -> Variante:
    def prepara(candele):
        o = C.array_ohlcv(candele)
        o["atr"] = C.atr(o, 14)
        fut = np.zeros(len(candele), dtype=bool)
        fut[:-1] = o["close"][1:] > o["open"][1:]  # LOOKAHEAD DICHIARATO: la barra dopo
        o["futuro_su"] = fut
        return o
    return Variante("CONTROLLO", "1h", "long", prepara,
                    condizione=lambda ind, i: bool(ind["futuro_su"][i]),
                    segnale=_stop_atr("long", 2.0), uscita=_uscita_tempo(1))


# ---------------------------------------------------------------------------
# Strumenti per gli indicatori
# ---------------------------------------------------------------------------

from datetime import datetime, timezone  # noqa: E402


def _giorno_settimana(ts) -> np.ndarray:
    """0 = lunedi' ... 6 = domenica, per l'apertura di ogni barra (UTC)."""
    return np.array([datetime.fromtimestamp(t / 1000, tz=timezone.utc).weekday() for t in ts])


def _quantile_mobile(x: np.ndarray, n: int, q: float) -> np.ndarray:
    """Quantile q della finestra x[i-n+1..i] (finestra che comprende la barra i), causale."""
    from numpy.lib.stride_tricks import sliding_window_view
    out = np.full(len(x), np.nan)
    if len(x) >= n:
        w = sliding_window_view(x, n)
        out[n - 1:] = np.quantile(w, q, axis=1)
    return out


def _funding_noto(candele) -> np.ndarray:
    """Per ogni barra, l'ultimo tasso di funding con settlement entro la chiusura della barra."""
    fine = datetime.fromtimestamp(candele[-1].close_ts / 1000, tz=timezone.utc).date()
    f = C.dati.carica_funding(C.SIMBOLO, C.INIZIO, fine)
    ts_f = np.array([t for t, _ in f], dtype=np.int64)
    val = np.array([r for _, r in f], dtype=float)
    chiusure = np.array([c.close_ts for c in candele], dtype=np.int64)
    k = np.searchsorted(ts_f, chiusure, side="right") - 1
    out = np.where(k >= 0, val[np.clip(k, 0, None)], np.nan)
    return out, k


def _taker(candele, tf: str):
    """Volume e volume dei compratori aggressivi (taker buy) dai CSV klines, per ts."""
    fine = datetime.fromtimestamp(candele[-1].close_ts / 1000, tz=timezone.utc).date()
    per_ts = {}
    for p in C.dati._percorsi_presenti(C.SIMBOLO, "klines", tf, C.INIZIO, fine, C.dati.RADICE_DEFAULT):
        for r in C.dati.righe_csv_da_zip(p):
            ts = C.dati.normalizza_ts(r[0])
            if ts not in per_ts:
                per_ts[ts] = (float(r[5]), float(r[9]))
    v = np.array([per_ts[c.ts][0] for c in candele])
    tb = np.array([per_ts[c.ts][1] for c in candele])
    return v, tb


def _somma_mobile(x: np.ndarray, n: int) -> np.ndarray:
    return C.sma(x, n) * n


def _uscita_su_indicatore(chiave: str):
    """Chiude quando l'array booleano ``chiave`` e' vero alla chiusura della barra."""
    def uscita(ind, i, barre, pos, candele):
        return bool(ind[chiave][i])
    return uscita


# ---------------------------------------------------------------------------
# I-01 Momentum a serie temporale (Moskowitz, Ooi, Pedersen 2012; Liu, Tsyvinski 2021)
# ---------------------------------------------------------------------------

def i01(direzione: str, vid: str) -> Variante:
    def prepara(candele):
        o = C.array_ohlcv(candele)
        o["atr"] = C.atr(o, 14)
        o["ret7"] = o["close"] / C.ritardo(o["close"], 7) - 1
        return o
    if direzione == "long":
        cond = lambda ind, i: bool(ind["ret7"][i] > 0)  # noqa: E731
    else:
        cond = lambda ind, i: bool(ind["ret7"][i] < 0)  # noqa: E731
    return Variante(vid, "1d", direzione, prepara, cond, _stop_atr(direzione, 2.0), _uscita_tempo(7))


# ---------------------------------------------------------------------------
# I-02 Rottura del canale di Donchian (Faith 2007, sistema 1 delle tartarughe)
# ---------------------------------------------------------------------------

def i02(direzione: str, vid: str) -> Variante:
    def prepara(candele):
        o = C.array_ohlcv(candele)
        o["atr"] = C.atr(o, 20)
        o["max20"] = C.ritardo(C.rolling_max(o["high"], 20), 1)
        o["min20"] = C.ritardo(C.rolling_min(o["low"], 20), 1)
        o["min10"] = C.ritardo(C.rolling_min(o["low"], 10), 1)
        o["max10"] = C.ritardo(C.rolling_max(o["high"], 10), 1)
        with np.errstate(invalid="ignore"):
            o["esci_long"] = o["close"] < o["min10"]
            o["esci_short"] = o["close"] > o["max10"]
        return o
    if direzione == "long":
        cond = lambda ind, i: bool(ind["close"][i] > ind["max20"][i])  # noqa: E731
        usc = _uscita_su_indicatore("esci_long")
    else:
        cond = lambda ind, i: bool(ind["close"][i] < ind["min20"][i])  # noqa: E731
        usc = _uscita_su_indicatore("esci_short")
    return Variante(vid, "4h", direzione, prepara, cond, _stop_atr(direzione, 2.0), usc)


# ---------------------------------------------------------------------------
# I-03 RSI a 2 periodi sopra la media a 200 (Connors, Alvarez 2008)
# ---------------------------------------------------------------------------

def i03(tf: str, vid: str) -> Variante:
    def prepara(candele):
        o = C.array_ohlcv(candele)
        o["atr"] = C.atr(o, 14)
        o["rsi2"] = C.rsi(o["close"], 2)
        o["sma200"] = C.sma(o["close"], 200)
        o["sma5"] = C.sma(o["close"], 5)
        with np.errstate(invalid="ignore"):
            o["esci"] = o["close"] > o["sma5"]
        return o
    cond = lambda ind, i: bool(ind["close"][i] > ind["sma200"][i] and ind["rsi2"][i] < 5)  # noqa: E731
    return Variante(vid, tf, "long", prepara, cond, _stop_atr("long", 2.5), _uscita_su_indicatore("esci"))


# ---------------------------------------------------------------------------
# I-04 Effetto del lunedi' (Caporale, Plastun 2019)
# ---------------------------------------------------------------------------

def i04(vid: str) -> Variante:
    def prepara(candele):
        o = C.array_ohlcv(candele)
        o["atr"] = C.atr(o, 14)
        o["gs"] = _giorno_settimana(o["ts"])
        return o
    cond = lambda ind, i: bool(ind["gs"][i] == 6)  # noqa: E731  barra della domenica: si entra lunedi'
    return Variante(vid, "1d", "long", prepara, cond, _stop_atr("long", 2.0), _uscita_tempo(1))


# ---------------------------------------------------------------------------
# I-05 Funding estremo (Schmeling, Schrimpf, Todorov 2023)
# ---------------------------------------------------------------------------

def i05(direzione: str, vid: str) -> Variante:
    def prepara(candele):
        o = C.array_ohlcv(candele)
        o["atr"] = C.atr(o, 14)
        f, k = _funding_noto(candele)
        # soglie sulla finestra degli ultimi 90 settlement PRIMA di quello corrente
        fd = C.dati.carica_funding(C.SIMBOLO, C.INIZIO, datetime.fromtimestamp(candele[-1].close_ts / 1000, tz=timezone.utc).date())
        vals = np.array([r for _, r in fd])
        q90 = np.full(len(vals), np.nan)
        q10 = np.full(len(vals), np.nan)
        for j in range(90, len(vals)):
            w = vals[j - 90:j]
            q90[j] = np.quantile(w, 0.9)
            q10[j] = np.quantile(w, 0.1)
        kk = np.clip(k, 0, None)
        o["f"] = f
        o["f_q90"] = np.where(k >= 0, q90[kk], np.nan)
        o["f_q10"] = np.where(k >= 0, q10[kk], np.nan)
        return o
    if direzione == "short":
        cond = lambda ind, i: bool(ind["f"][i] > ind["f_q90"][i])  # noqa: E731
    else:
        cond = lambda ind, i: bool(ind["f"][i] < ind["f_q10"][i])  # noqa: E731
    return Variante(vid, "8h", direzione, prepara, cond, _stop_atr(direzione, 2.0), _uscita_tempo(3))


# ---------------------------------------------------------------------------
# I-06 Compressione delle bande di Bollinger (Bollinger 2001)
# ---------------------------------------------------------------------------

def i06(direzione: str, vid: str, tf: str = "4h") -> Variante:
    def prepara(candele):
        o = C.array_ohlcv(candele)
        o["atr"] = C.atr(o, 14)
        m = C.sma(o["close"], 20)
        s = C.rolling_std(o["close"], 20)
        o["sma20"] = m
        o["sup"] = m + 2 * s
        o["inf"] = m - 2 * s
        bw = 4 * s / m
        o["squeeze"] = C.rolling_min(bw, 6) <= C.rolling_min(bw, 120)
        with np.errstate(invalid="ignore"):
            o["esci_long"] = o["close"] < m
            o["esci_short"] = o["close"] > m
        return o
    if direzione == "long":
        cond = lambda ind, i: bool(ind["squeeze"][i] and ind["close"][i] > ind["sup"][i])  # noqa: E731
        usc = _uscita_su_indicatore("esci_long")
    else:
        cond = lambda ind, i: bool(ind["squeeze"][i] and ind["close"][i] < ind["inf"][i])  # noqa: E731
        usc = _uscita_su_indicatore("esci_short")
    return Variante(vid, tf, direzione, prepara, cond, _stop_atr(direzione, 2.0), usc)


# ---------------------------------------------------------------------------
# I-07 Premio del volume alto (Gervais, Kaniel, Mingelgrin 2001)
# ---------------------------------------------------------------------------

def i07(vid: str, q: float = 0.9) -> Variante:
    def prepara(candele):
        o = C.array_ohlcv(candele)
        o["atr"] = C.atr(o, 14)
        o["vq90"] = _quantile_mobile(o["volume"], 50, q)
        return o
    cond = lambda ind, i: bool(ind["volume"][i] >= ind["vq90"][i])  # noqa: E731
    return Variante(vid, "1d", "long", prepara, cond, _stop_atr("long", 2.0), _uscita_tempo(5))


# ---------------------------------------------------------------------------
# I-08 Sovrareazione seguita da continuazione (Caporale, Plastun 2019, J. Econ. Studies)
# ---------------------------------------------------------------------------

def i08(direzione: str, vid: str) -> Variante:
    def prepara(candele):
        o = C.array_ohlcv(candele)
        o["atr"] = C.atr(o, 14)
        r24 = o["close"] / C.ritardo(o["close"], 6) - 1
        o["r24"] = r24
        o["m"] = C.sma(r24, 180)
        o["s"] = C.rolling_std(r24, 180)
        return o
    if direzione == "long":
        cond = lambda ind, i: bool(ind["r24"][i] > ind["m"][i] + 2 * ind["s"][i])  # noqa: E731
    else:
        cond = lambda ind, i: bool(ind["r24"][i] < ind["m"][i] - 2 * ind["s"][i])  # noqa: E731
    return Variante(vid, "4h", direzione, prepara, cond, _stop_atr(direzione, 2.0), _uscita_tempo(6))


# ---------------------------------------------------------------------------
# I-09 Squilibrio degli ordini aggressivi (Chordia, Subrahmanyam 2004)
# ---------------------------------------------------------------------------

def i09(direzione: str, vid: str) -> Variante:
    def prepara(candele):
        o = C.array_ohlcv(candele)
        o["atr"] = C.atr(o, 14)
        v, tb = _taker(candele, "4h")
        sv = _somma_mobile(v, 6)
        imb = (2 * _somma_mobile(tb, 6) - sv) / sv
        o["imb"] = imb
        o["q90"] = _quantile_mobile(np.nan_to_num(imb, nan=0.0), 180, 0.9)
        o["q10"] = _quantile_mobile(np.nan_to_num(imb, nan=0.0), 180, 0.1)
        o["q90"][:185] = np.nan
        o["q10"][:185] = np.nan
        return o
    if direzione == "long":
        cond = lambda ind, i: bool(ind["imb"][i] >= ind["q90"][i])  # noqa: E731
    else:
        cond = lambda ind, i: bool(ind["imb"][i] <= ind["q10"][i])  # noqa: E731
    return Variante(vid, "4h", direzione, prepara, cond, _stop_atr(direzione, 2.0), _uscita_tempo(6))


# ---------------------------------------------------------------------------
# I-10 Incrocio della media mobile a 50 (Brock, Lakonishok, LeBaron 1992)
# ---------------------------------------------------------------------------

def i10(direzione: str, vid: str) -> Variante:
    def prepara(candele):
        o = C.array_ohlcv(candele)
        o["atr"] = C.atr(o, 14)
        m = C.sma(o["close"], 50)
        o["sma50"] = m
        pc = C.ritardo(o["close"], 1)
        pm = C.ritardo(m, 1)
        with np.errstate(invalid="ignore"):
            o["su"] = (o["close"] > m) & (pc <= pm)
            o["giu"] = (o["close"] < m) & (pc >= pm)
            o["sotto"] = o["close"] < m
            o["sopra"] = o["close"] > m
        return o
    if direzione == "long":
        cond = lambda ind, i: bool(ind["su"][i])  # noqa: E731
        usc = _uscita_su_indicatore("sotto")
    else:
        cond = lambda ind, i: bool(ind["giu"][i])  # noqa: E731
        usc = _uscita_su_indicatore("sopra")
    return Variante(vid, "4h", direzione, prepara, cond, _stop_atr(direzione, 2.0), usc)


# ---------------------------------------------------------------------------
# I-11 Momento infragiornaliero: prima mezz'ora -> ultima mezz'ora (Shen, Urquhart, Wang 2022)
# ---------------------------------------------------------------------------

def i11(direzione: str, vid: str) -> Variante:
    def prepara(candele):
        o = C.array_ohlcv(candele)
        o["atr"] = C.atr(o, 14)
        giorno = o["ts"] // 86_400_000
        minuto = (o["ts"] % 86_400_000) // 60_000
        prima = {}
        for i in range(len(candele)):
            if minuto[i] == 0:
                prima[giorno[i]] = o["close"][i] / o["open"][i] - 1
        r = np.full(len(candele), np.nan)
        for i in range(len(candele)):
            if minuto[i] == 23 * 60 and giorno[i] in prima:  # chiusura della barra delle 23:00: si entra alle 23:30
                r[i] = prima[giorno[i]]
        o["prima_mezzora"] = r
        return o
    if direzione == "long":
        cond = lambda ind, i: bool(ind["prima_mezzora"][i] > 0)  # noqa: E731
    else:
        cond = lambda ind, i: bool(ind["prima_mezzora"][i] < 0)  # noqa: E731
    return Variante(vid, "30m", direzione, prepara, cond, _stop_atr(direzione, 2.0), _uscita_tempo(1))


# ---------------------------------------------------------------------------
# I-12 Rimbalzo dopo una caduta forzata (Brunnermeier, Pedersen 2009)
# ---------------------------------------------------------------------------

def i12(soglia_atr: float, vid: str) -> Variante:
    def prepara(candele):
        o = C.array_ohlcv(candele)
        o["atr"] = C.atr(o, 14)
        o["atr_prima"] = C.ritardo(o["atr"], 1)
        return o
    cond = lambda ind, i: bool(ind["close"][i] - ind["open"][i] < -soglia_atr * ind["atr_prima"][i])  # noqa: E731
    return Variante(vid, "1h", "long", prepara, cond, _stop_atr("long", 2.0), _uscita_tempo(12))


# ---------------------------------------------------------------------------
# I-13 Cambio del mese (Lakonishok, Smidt 1988)
# ---------------------------------------------------------------------------

def i13(vid: str) -> Variante:
    def prepara(candele):
        o = C.array_ohlcv(candele)
        o["atr"] = C.atr(o, 14)
        dopo = np.zeros(len(candele), dtype=bool)
        for i in range(len(candele)):
            d = datetime.fromtimestamp((o["ts"][i] + 86_400_000) / 1000, tz=timezone.utc)
            d2 = datetime.fromtimestamp((o["ts"][i] + 2 * 86_400_000) / 1000, tz=timezone.utc)
            dopo[i] = d.month != d2.month  # la barra dopo e' l'ultimo giorno del mese
        o["vigilia"] = dopo
        return o
    cond = lambda ind, i: bool(ind["vigilia"][i])  # noqa: E731
    return Variante(vid, "1d", "long", prepara, cond, _stop_atr("long", 2.0), _uscita_tempo(4))


# ---------------------------------------------------------------------------
# I-14 Volatilita' bassa (Moreira, Muir 2017)
# ---------------------------------------------------------------------------

def i14(vid: str) -> Variante:
    def prepara(candele):
        o = C.array_ohlcv(candele)
        o["atr"] = C.atr(o, 14)
        lr = np.diff(np.log(o["close"]), prepend=np.nan)
        rv = C.rolling_std(lr, 42)
        o["rv"] = rv
        o["rv_q33"] = _quantile_mobile(np.nan_to_num(rv, nan=np.inf), 540, 1 / 3)
        o["rv_q33"][:582] = np.nan
        return o
    cond = lambda ind, i: bool(ind["rv"][i] <= ind["rv_q33"][i])  # noqa: E731
    return Variante(vid, "4h", "long", prepara, cond, _stop_atr("long", 2.0), _uscita_tempo(6))


# ---------------------------------------------------------------------------
# I-15 Forza della tendenza con l'ADX (Wilder 1978)
# ---------------------------------------------------------------------------

def _dmi(o, n: int = 14):
    """+DI, -DI e ADX di Wilder, causali."""
    h, l = o["high"], o["low"]
    su = np.diff(h, prepend=h[0])
    giu = -np.diff(l, prepend=l[0])
    pdm = np.where((su > giu) & (su > 0), su, 0.0)
    mdm = np.where((giu > su) & (giu > 0), giu, 0.0)
    tr = C.true_range(o)
    N = len(h)

    def wilder(x):
        out = np.full(N, np.nan)
        if N <= n:
            return out
        m = x[1:n + 1].sum()
        out[n] = m
        for i in range(n + 1, N):
            m = m - m / n + x[i]
            out[i] = m
        return out
    atr_w, p, m = wilder(tr), wilder(pdm), wilder(mdm)
    with np.errstate(invalid="ignore", divide="ignore"):
        pdi = 100 * p / atr_w
        mdi = 100 * m / atr_w
        dx = 100 * np.abs(pdi - mdi) / (pdi + mdi)
    adx = np.full(N, np.nan)
    inizio = 2 * n
    if N > inizio:
        a = np.nanmean(dx[n + 1:inizio + 1])
        adx[inizio] = a
        for i in range(inizio + 1, N):
            a = (a * (n - 1) + dx[i]) / n
            adx[i] = a
    return pdi, mdi, adx


def i15(direzione: str, vid: str) -> Variante:
    def prepara(candele):
        o = C.array_ohlcv(candele)
        o["atr"] = C.atr(o, 14)
        pdi, mdi, adx = _dmi(o, 14)
        prec = C.ritardo(adx, 1)
        with np.errstate(invalid="ignore"):
            o["adx_su"] = (adx > 25) & (prec <= 25)
            o["pdi_mag"] = pdi > mdi
            o["mdi_mag"] = mdi > pdi
        return o
    if direzione == "long":
        cond = lambda ind, i: bool(ind["adx_su"][i] and ind["pdi_mag"][i])  # noqa: E731
        usc = _uscita_su_indicatore("mdi_mag")
    else:
        cond = lambda ind, i: bool(ind["adx_su"][i] and ind["mdi_mag"][i])  # noqa: E731
        usc = _uscita_su_indicatore("pdi_mag")
    return Variante(vid, "4h", direzione, prepara, cond, _stop_atr(direzione, 2.0), usc)


# ---------------------------------------------------------------------------
# I-16 Shock di illiquidita' (Amihud 2002)
# ---------------------------------------------------------------------------

def _volume_usdt(candele, tf: str) -> np.ndarray:
    fine = datetime.fromtimestamp(candele[-1].close_ts / 1000, tz=timezone.utc).date()
    per_ts = {}
    for p in C.dati._percorsi_presenti(C.SIMBOLO, "klines", tf, C.INIZIO, fine, C.dati.RADICE_DEFAULT):
        for ts, v in C.dati.volume_usdt_da_zip(p).items():
            per_ts.setdefault(ts, v)
    return np.array([per_ts.get(c.ts, np.nan) for c in candele])


def i16(vid: str) -> Variante:
    def prepara(candele):
        o = C.array_ohlcv(candele)
        o["atr"] = C.atr(o, 14)
        qv = _volume_usdt(candele, "4h")
        r = np.abs(np.diff(np.log(o["close"]), prepend=np.nan))
        with np.errstate(invalid="ignore", divide="ignore"):
            ill = C.sma(r / qv * 1e9, 6)
        o["ill"] = ill
        o["ill_q90"] = _quantile_mobile(np.nan_to_num(ill, nan=np.inf), 180, 0.9)
        o["ill_q90"][:190] = np.nan
        return o
    cond = lambda ind, i: bool(ind["ill"][i] >= ind["ill_q90"][i])  # noqa: E731
    return Variante(vid, "4h", "long", prepara, cond, _stop_atr("long", 2.0), _uscita_tempo(6))


# ---------------------------------------------------------------------------
# I-17 Asimmetria realizzata negativa (Amaya, Christoffersen, Jacobs, Vasquez 2015)
# ---------------------------------------------------------------------------

def i17(vid: str) -> Variante:
    def prepara(candele):
        from numpy.lib.stride_tricks import sliding_window_view
        o = C.array_ohlcv(candele)
        o["atr"] = C.atr(o, 14)
        lr = np.diff(np.log(o["close"]), prepend=0.0)
        sk = np.full(len(lr), np.nan)
        n = 42
        if len(lr) > n:
            w = sliding_window_view(lr[1:], n)  # finestra che termina alla barra i (indice i = j + n)
            m = w.mean(axis=1, keepdims=True)
            d = w - m
            s2 = (d ** 2).mean(axis=1)
            s3 = (d ** 3).mean(axis=1)
            with np.errstate(invalid="ignore", divide="ignore"):
                sk[n:] = s3 / s2 ** 1.5
        o["sk"] = sk
        o["sk_q10"] = _quantile_mobile(np.nan_to_num(sk, nan=-np.inf), 540, 0.1)
        o["sk_q10"][:600] = np.nan
        return o
    cond = lambda ind, i: bool(ind["sk"][i] <= ind["sk_q10"][i])  # noqa: E731
    return Variante(vid, "4h", "long", prepara, cond, _stop_atr("long", 2.0), _uscita_tempo(42))
