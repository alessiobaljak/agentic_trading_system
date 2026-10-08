"""Le varianti della campagna BTCUSDT, scritte da ipotesi.md (stessi identificativi).

Ogni funzione ``vNN()`` restituisce una ``quadro.Variante``. Gli indicatori sono causali:
il valore alla barra i usa solo le barre 0..i. Le condizioni restituiscono None durante il
riscaldamento.
"""
from __future__ import annotations

import math
from datetime import datetime, timezone

import numpy as np

import quadro
from quadro import Variante, arr, atr, barre_tenute, massimo_precedente, minimo_precedente, nan, per_ts, rsi, sma
from comune import PERIODI
from research.src.motore import Segnale


def _uscita_tempo(n_barre, tf):
    ms = quadro.MS[tf]

    def uscita(stato, storia, pos):
        return "chiudi" if barre_tenute(storia, pos, ms) >= n_barre else None
    return uscita


def _stop_pct(direzione, pct):
    def segnale(stato, storia):
        c = storia[-1].close
        return Segnale(direzione, stop=c * (1 - pct) if direzione == "long" else c * (1 + pct))
    return segnale


# ---------------------------------------------------------------------------
# I-01 momentum a serie storica, 1d
# ---------------------------------------------------------------------------

def _i01(direzione, vid):
    tf = "1d"

    def prepara(candele):
        c = arr(candele, "close")
        r7 = np.full(c.size, np.nan)
        r7[7:] = c[7:] / c[:-7] - 1
        return per_ts(candele, r7=r7)

    def condizione(stato, storia):
        x = stato[storia[-1].ts]["r7"]
        if nan(x):
            return None
        return x > 0 if direzione == "long" else x < 0

    return Variante(vid, tf, direzione, prepara, condizione, _stop_pct(direzione, 0.06), _uscita_tempo(7, tf))


def v01():
    return _i01("long", "V01")


def v02():
    return _i01("short", "V02")


# ---------------------------------------------------------------------------
# I-02 rottura del canale di 20 barre, 4h
# ---------------------------------------------------------------------------

def _i02(direzione, vid):
    tf = "4h"

    def prepara(candele):
        h, l = arr(candele, "high"), arr(candele, "low")
        return per_ts(candele, max20=massimo_precedente(h, 20), min20=minimo_precedente(l, 20),
                      max10=massimo_precedente(h, 10), min10=minimo_precedente(l, 10), atr20=atr(candele, 20))

    def condizione(stato, storia):
        s = stato[storia[-1].ts]
        if nan(s["max20"]) or nan(s["atr20"]):
            return None
        c = storia[-1].close
        return c > s["max20"] if direzione == "long" else c < s["min20"]

    def segnale(stato, storia):
        s = stato[storia[-1].ts]
        if nan(s["atr20"]):
            return None
        c = storia[-1].close
        return Segnale(direzione, stop=c - 2 * s["atr20"] if direzione == "long" else c + 2 * s["atr20"])

    def uscita(stato, storia, pos):
        s = stato[storia[-1].ts]
        c = storia[-1].close
        if direzione == "long":
            return "chiudi" if not nan(s["min10"]) and c < s["min10"] else None
        return "chiudi" if not nan(s["max10"]) and c > s["max10"] else None

    return Variante(vid, tf, direzione, prepara, condizione, segnale, uscita)


def v03():
    return _i02("long", "V03")


def v04():
    return _i02("short", "V04")


# ---------------------------------------------------------------------------
# I-03 barre anomale, 4h
# ---------------------------------------------------------------------------

def _i03(verso_barra, vid):
    tf = "4h"

    def prepara(candele):
        c = arr(candele, "close")
        r = np.full(c.size, np.nan)
        r[1:] = c[1:] / c[:-1] - 1
        sd = np.full(c.size, np.nan)
        for i in range(181, c.size):
            sd[i] = np.std(r[i - 180:i], ddof=1)
        return per_ts(candele, r=r, sd=sd)

    def condizione(stato, storia):
        s = stato[storia[-1].ts]
        if nan(s["sd"]) or nan(s["r"]):
            return None
        return s["r"] > 2 * s["sd"] if verso_barra == "su" else s["r"] < -2 * s["sd"]

    return Variante(vid, tf, "long", prepara, condizione, _stop_pct("long", 0.05), _uscita_tempo(6, tf))


def v05():
    return _i03("su", "V05")


def v06():
    return _i03("giu", "V06")


# ---------------------------------------------------------------------------
# I-04 RSI(2) con filtro di trend, 4h
# ---------------------------------------------------------------------------

def _i04(direzione, vid):
    tf = "4h"

    def prepara(candele):
        c = arr(candele, "close")
        return per_ts(candele, sma200=sma(c, 200), sma5=sma(c, 5), rsi2=rsi(c, 2), atr14=atr(candele, 14))

    def condizione(stato, storia):
        s = stato[storia[-1].ts]
        if nan(s["sma200"]) or nan(s["rsi2"]) or nan(s["atr14"]):
            return None
        c = storia[-1].close
        if direzione == "long":
            return c > s["sma200"] and s["rsi2"] < 10
        return c < s["sma200"] and s["rsi2"] > 90

    def segnale(stato, storia):
        s = stato[storia[-1].ts]
        if nan(s["atr14"]):
            return None
        c = storia[-1].close
        return Segnale(direzione, stop=c - 3 * s["atr14"] if direzione == "long" else c + 3 * s["atr14"])

    def uscita(stato, storia, pos):
        s = stato[storia[-1].ts]
        c = storia[-1].close
        if nan(s["sma5"]):
            return None
        if direzione == "long":
            return "chiudi" if c > s["sma5"] else None
        return "chiudi" if c < s["sma5"] else None

    return Variante(vid, tf, direzione, prepara, condizione, segnale, uscita)


def v07():
    return _i04("long", "V07")


def v08():
    return _i04("short", "V08")


# ---------------------------------------------------------------------------
# I-05 lunedi', 1d
# ---------------------------------------------------------------------------

def v09():
    tf = "1d"

    def prepara(candele):
        return {}

    def condizione(stato, storia):
        # barra di domenica (weekday 6): l'ingresso e' all'apertura del lunedi'
        return datetime.fromtimestamp(storia[-1].ts / 1000, tz=timezone.utc).weekday() == 6

    return Variante("V09", tf, "long", prepara, condizione, _stop_pct("long", 0.05), _uscita_tempo(1, tf))


# ---------------------------------------------------------------------------
# I-06 rottura di volatilita' dall'apertura del giorno, 1h
# ---------------------------------------------------------------------------

def _i06(direzione, vid):
    tf = "1h"
    GIORNO = 86_400_000

    def prepara(candele):
        # per ogni giorno UTC: apertura (barra delle 00:00), high, low e numero di barre
        giorni = {}
        for c in candele:
            g = c.ts // GIORNO
            d = giorni.setdefault(g, {"open": None, "high": -math.inf, "low": math.inf, "n": 0})
            if c.ts % GIORNO == 0:
                d["open"] = c.open
            d["high"] = max(d["high"], c.high)
            d["low"] = min(d["low"], c.low)
            d["n"] += 1
        return giorni

    def _livelli(stato, storia):
        ts = storia[-1].ts
        g = ts // GIORNO
        oggi, ieri = stato.get(g), stato.get(g - 1)
        if oggi is None or ieri is None or oggi["open"] is None or ieri["n"] != 24:
            return None
        return oggi["open"], ieri["high"] - ieri["low"]

    def condizione(stato, storia):
        liv = _livelli(stato, storia)
        if liv is None:
            return None
        ts = storia[-1].ts
        if (ts % GIORNO) // 3_600_000 == 23:
            return False
        o, rng = liv
        # un solo ingresso per giorno: la prima chiusura oltre la soglia
        inizio_giorno = ts - ts % GIORNO
        soglia_su, soglia_giu = o + 0.5 * rng, o - 0.5 * rng
        oltre = (lambda x: x > soglia_su) if direzione == "long" else (lambda x: x < soglia_giu)
        if not oltre(storia[-1].close):
            return False
        k = len(storia) - 2
        while k >= 0 and storia[k].ts >= inizio_giorno:
            if oltre(storia[k].close):
                return False
            k -= 1
        return True

    def segnale(stato, storia):
        liv = _livelli(stato, storia)
        if liv is None:
            return None
        return Segnale(direzione, stop=liv[0])

    def uscita(stato, storia, pos):
        return "chiudi" if (storia[-1].ts % GIORNO) // 3_600_000 == 23 else None

    return Variante(vid, tf, direzione, prepara, condizione, segnale, uscita)


def v10():
    return _i06("long", "V10")


def v11():
    return _i06("short", "V11")


# ---------------------------------------------------------------------------
# I-07 compressione delle bande di Bollinger, 4h
# ---------------------------------------------------------------------------

def _i07(direzione, vid):
    tf = "4h"

    def prepara(candele):
        c = arr(candele, "close")
        m = sma(c, 20)
        sd = np.full(c.size, np.nan)
        for i in range(19, c.size):
            sd[i] = np.std(c[i - 19:i + 1])  # deviazione standard della popolazione, come Bollinger
        su, giu = m + 2 * sd, m - 2 * sd
        larg = (su - giu) / m
        compr = np.zeros(c.size, dtype=bool)
        ok = np.zeros(c.size, dtype=bool)
        for i in range(19 + 124, c.size):
            finestra = larg[i - 124:i + 1]
            compr[i] = larg[i] <= finestra.min()
            ok[i] = True
        recente = np.full(c.size, np.nan)
        for i in range(c.size):
            if i >= 19 + 124 + 9:
                recente[i] = float(compr[i - 9:i + 1].any())
        return per_ts(candele, m=m, su=su, giu=giu, recente=recente, atr20=atr(candele, 20))

    def condizione(stato, storia):
        s = stato[storia[-1].ts]
        if nan(s["recente"]) or nan(s["atr20"]):
            return None
        c = storia[-1].close
        if s["recente"] < 0.5:
            return False
        return c > s["su"] if direzione == "long" else c < s["giu"]

    def segnale(stato, storia):
        s = stato[storia[-1].ts]
        if nan(s["atr20"]):
            return None
        c = storia[-1].close
        return Segnale(direzione, stop=c - 2 * s["atr20"] if direzione == "long" else c + 2 * s["atr20"])

    def uscita(stato, storia, pos):
        s = stato[storia[-1].ts]
        c = storia[-1].close
        if nan(s["m"]):
            return None
        if direzione == "long":
            return "chiudi" if c < s["m"] else None
        return "chiudi" if c > s["m"] else None

    return Variante(vid, tf, direzione, prepara, condizione, segnale, uscita)


def v12():
    return _i07("long", "V12")


def v13():
    return _i07("short", "V13")


# ---------------------------------------------------------------------------
# I-08 funding, 8h
# ---------------------------------------------------------------------------

def _i08(direzione, vid):
    tf = "8h"

    def prepara(candele):
        _, _, funding = quadro.tutto_insample(tf)
        funding = [(t, r) for t, r in funding if t <= candele[-1].close_ts]
        ts_f = [t for t, _ in funding]
        tassi = [r for _, r in funding]
        import bisect
        out = {}
        for c in candele:
            k = bisect.bisect_right(ts_f, c.close_ts) - 1
            out[c.ts] = tassi[k] if k >= 0 else float("nan")
        return out

    def condizione(stato, storia):
        f = stato.get(storia[-1].ts)
        if nan(f):
            return None
        return f >= 0.0005 if direzione == "short" else f < 0

    return Variante(vid, tf, direzione, prepara, condizione, _stop_pct(direzione, 0.05), _uscita_tempo(3, tf))


def v14():
    return _i08("short", "V14")


def v15():
    return _i08("long", "V15")


# ---------------------------------------------------------------------------
# I-09 squilibrio degli ordini aggressivi, 4h
# ---------------------------------------------------------------------------

def _i09(direzione, vid):
    tf = "4h"

    def prepara(candele):
        ultimo = datetime.fromtimestamp(candele[-1].ts / 1000, tz=timezone.utc).date()
        extra = quadro.extra_csv(tf, ultimo)
        vol = arr(candele, "volume")
        buy = np.array([extra[c.ts][1] if c.ts in extra else np.nan for c in candele])
        s_buy = np.full(vol.size, np.nan)
        s_vol = np.full(vol.size, np.nan)
        for i in range(5, vol.size):
            s_buy[i] = buy[i - 5:i + 1].sum()
            s_vol[i] = vol[i - 5:i + 1].sum()
        imb = (2 * s_buy - s_vol) / s_vol
        p90 = np.full(vol.size, np.nan)
        p10 = np.full(vol.size, np.nan)
        for i in range(5 + 180, vol.size):
            fin = imb[i - 180:i]
            if np.isnan(fin).any() or np.isnan(imb[i]):
                continue
            p90[i] = np.percentile(fin, 90)
            p10[i] = np.percentile(fin, 10)
        return per_ts(candele, imb=imb, p90=p90, p10=p10, atr14=atr(candele, 14))

    def condizione(stato, storia):
        s = stato[storia[-1].ts]
        if nan(s["p90"]) or nan(s["atr14"]):
            return None
        return s["imb"] > s["p90"] if direzione == "long" else s["imb"] < s["p10"]

    def segnale(stato, storia):
        s = stato[storia[-1].ts]
        if nan(s["atr14"]):
            return None
        c = storia[-1].close
        return Segnale(direzione, stop=c - 2 * s["atr14"] if direzione == "long" else c + 2 * s["atr14"])

    return Variante(vid, tf, direzione, prepara, condizione, segnale, _uscita_tempo(6, tf))


def v16():
    return _i09("long", "V16")


def v17():
    return _i09("short", "V17")


# ---------------------------------------------------------------------------
# I-10 momentum di giornata, 30m
# ---------------------------------------------------------------------------

def _i10(direzione, vid):
    tf = "30m"
    GIORNO = 86_400_000

    def prepara(candele):
        prima = {}
        for c in candele:
            if c.ts % GIORNO == 0:
                prima[c.ts // GIORNO] = (c.open, c.close)
        return prima

    def condizione(stato, storia):
        ts = storia[-1].ts
        if ts % GIORNO != 23 * 3_600_000:  # barra 23:00-23:30
            return False
        p = stato.get(ts // GIORNO)
        if p is None:
            return None
        o, c = p
        return c > o if direzione == "long" else c < o

    return Variante(vid, tf, direzione, prepara, condizione, _stop_pct(direzione, 0.01), _uscita_tempo(1, tf))


def v18():
    return _i10("long", "V18")


def v19():
    return _i10("short", "V19")


# ---------------------------------------------------------------------------
# I-11 numeri tondi, 1h
# ---------------------------------------------------------------------------

def _i11(direzione, vid):
    tf = "1h"
    PASSO = 1000.0

    def _livello(storia):
        if len(storia) < 2:
            return None
        p, c = storia[-2].close, storia[-1].close
        if direzione == "long":
            # K multiplo di 1000 con p < K <= c: il piu' lontano da p e' il piu' alto
            k = math.floor(c / PASSO) * PASSO
            return k if p < k <= c else None
        k = math.ceil(c / PASSO) * PASSO
        if k == c:
            k = c + PASSO  # close esattamente su K: K > close non vale per K = close
        # K con c < K <= p: il piu' lontano da p e' il piu' basso, cioe' il primo sopra c
        return k if c < k <= p else None

    def prepara(candele):
        return {}

    def condizione(stato, storia):
        if len(storia) < 2:
            return None
        return _livello(storia) is not None

    def segnale(stato, storia):
        # senza condizione: il numero tondo di riferimento e' quello piu' vicino al close
        k = _livello(storia)
        c = storia[-1].close
        if k is None:
            k = math.floor(c / PASSO) * PASSO if direzione == "long" else math.ceil(c / PASSO) * PASSO
            if direzione == "short" and k == c:
                k = c + PASSO
            if direzione == "long" and k <= 0:
                return None
        return Segnale(direzione, stop=k * 0.99 if direzione == "long" else k * 1.01)

    return Variante(vid, tf, direzione, prepara, condizione, segnale, _uscita_tempo(4, tf))


def v20():
    return _i11("long", "V20")


def v21():
    return _i11("short", "V21")


# ---------------------------------------------------------------------------
# I-12 martello e stella cadente, 4h
# ---------------------------------------------------------------------------

def _i12(direzione, vid):
    tf = "4h"

    def prepara(candele):
        return {}

    def condizione(stato, storia):
        if len(storia) < 7:
            return None
        b = storia[-1]
        rng = b.high - b.low
        corpo = abs(b.close - b.open)
        if rng <= 0 or corpo <= 0:
            return False
        inf = min(b.open, b.close) - b.low
        sup = b.high - max(b.open, b.close)
        if direzione == "long":
            return inf >= 2 * corpo and sup <= 0.1 * rng and b.close < storia[-7].close
        return sup >= 2 * corpo and inf <= 0.1 * rng and b.close > storia[-7].close

    def segnale(stato, storia):
        b = storia[-1]
        if direzione == "long":
            return Segnale("long", stop=b.low) if b.low < b.close else None
        return Segnale("short", stop=b.high) if b.high > b.close else None

    return Variante(vid, tf, direzione, prepara, condizione, segnale, _uscita_tempo(6, tf))


def v22():
    return _i12("long", "V22")


def v23():
    return _i12("short", "V23")


# ---------------------------------------------------------------------------
# I-13 vicino al massimo di un anno, 1d
# ---------------------------------------------------------------------------

def v24():
    tf = "1d"

    def prepara(candele):
        return per_ts(candele, max365=massimo_precedente(arr(candele, "high"), 365))

    def condizione(stato, storia):
        m = stato[storia[-1].ts]["max365"]
        if nan(m):
            return None
        return storia[-1].close >= 0.95 * m

    return Variante("V24", tf, "long", prepara, condizione, _stop_pct("long", 0.06), _uscita_tempo(5, tf))


# ---------------------------------------------------------------------------
# I-14 NR7, 1h
# ---------------------------------------------------------------------------

def _i14(direzione, vid):
    tf = "1h"
    GIORNO = 86_400_000

    def prepara(candele):
        giorni = {}
        for c in candele:
            d = giorni.setdefault(c.ts // GIORNO, {"high": -math.inf, "low": math.inf, "n": 0})
            d["high"] = max(d["high"], c.high)
            d["low"] = min(d["low"], c.low)
            d["n"] += 1
        return giorni

    def _ieri(stato, storia):
        g = storia[-1].ts // GIORNO
        dd = [stato.get(g - k) for k in range(1, 8)]
        if any(d is None or d["n"] != 24 for d in dd):
            return None
        rng = [d["high"] - d["low"] for d in dd]
        return dd[0], all(rng[0] < r for r in rng[1:])

    def condizione(stato, storia):
        x = _ieri(stato, storia)
        if x is None:
            return None
        ieri, nr7 = x
        ts = storia[-1].ts
        if not nr7 or (ts % GIORNO) // 3_600_000 == 23:
            return False
        oltre = (lambda c: c > ieri["high"]) if direzione == "long" else (lambda c: c < ieri["low"])
        if not oltre(storia[-1].close):
            return False
        inizio = ts - ts % GIORNO
        k = len(storia) - 2
        while k >= 0 and storia[k].ts >= inizio:
            if oltre(storia[k].close):
                return False
            k -= 1
        return True

    def segnale(stato, storia):
        x = _ieri(stato, storia)
        if x is None:
            return None
        ieri = x[0]
        return Segnale(direzione, stop=ieri["low"] if direzione == "long" else ieri["high"])

    def uscita(stato, storia, pos):
        return "chiudi" if (storia[-1].ts % GIORNO) // 3_600_000 == 23 else None

    return Variante(vid, tf, direzione, prepara, condizione, segnale, uscita)


def v25():
    return _i14("long", "V25")


def v26():
    return _i14("short", "V26")


# ---------------------------------------------------------------------------
# I-15 molla e spinta, 4h
# ---------------------------------------------------------------------------

def _i15(direzione, vid):
    tf = "4h"

    def prepara(candele):
        h, l = arr(candele, "high"), arr(candele, "low")
        return per_ts(candele, max20=massimo_precedente(h, 20), min20=minimo_precedente(l, 20))

    def condizione(stato, storia):
        s = stato[storia[-1].ts]
        if nan(s["min20"]):
            return None
        b = storia[-1]
        if direzione == "long":
            return b.low < s["min20"] and b.close > s["min20"]
        return b.high > s["max20"] and b.close < s["max20"]

    def segnale(stato, storia):
        b = storia[-1]
        return Segnale(direzione, stop=b.low * 0.999 if direzione == "long" else b.high * 1.001)

    return Variante(vid, tf, direzione, prepara, condizione, segnale, _uscita_tempo(6, tf))


def v27():
    return _i15("long", "V27")


def v28():
    return _i15("short", "V28")


# ---------------------------------------------------------------------------
# I-16 media mobile di 50 con banda dell'1%, 4h
# ---------------------------------------------------------------------------

def v29():
    tf = "4h"

    def prepara(candele):
        c = arr(candele, "close")
        m = sma(c, 50)
        prec = np.full(c.size, np.nan)
        prec_m = np.full(c.size, np.nan)
        prec[1:] = c[:-1]
        prec_m[1:] = m[:-1]
        return per_ts(candele, m=m, prec=prec, prec_m=prec_m, atr14=atr(candele, 14))

    def condizione(stato, storia):
        s = stato[storia[-1].ts]
        if nan(s["prec_m"]) or nan(s["atr14"]):
            return None
        return storia[-1].close > 1.01 * s["m"] and s["prec"] <= 1.01 * s["prec_m"]

    def segnale(stato, storia):
        s = stato[storia[-1].ts]
        if nan(s["atr14"]):
            return None
        return Segnale("long", stop=storia[-1].close - 3 * s["atr14"])

    def uscita(stato, storia, pos):
        s = stato[storia[-1].ts]
        return "chiudi" if not nan(s["m"]) and storia[-1].close < 0.99 * s["m"] else None

    return Variante("V29", tf, "long", prepara, condizione, segnale, uscita)


# ---------------------------------------------------------------------------
# I-17 volume alto, 4h
# ---------------------------------------------------------------------------

def v30():
    tf = "4h"

    def prepara(candele):
        v = arr(candele, "volume")
        return per_ts(candele, vol=v, max49=massimo_precedente(v, 49), atr14=atr(candele, 14))

    def condizione(stato, storia):
        s = stato[storia[-1].ts]
        if nan(s["max49"]) or nan(s["atr14"]):
            return None
        return s["vol"] > s["max49"]

    def segnale(stato, storia):
        s = stato[storia[-1].ts]
        if nan(s["atr14"]):
            return None
        return Segnale("long", stop=storia[-1].close - 2 * s["atr14"])

    return Variante("V30", tf, "long", prepara, condizione, segnale, _uscita_tempo(6, tf))


# ---------------------------------------------------------------------------
# Ritocchi (regola 6)
# ---------------------------------------------------------------------------

def v31():
    """Ritocco di V19: in piu' il filtro «giornata in calo alla chiusura delle 23:30»."""
    base = v19()
    GIORNO = 86_400_000
    cond_base = base.condizione

    def condizione(stato, storia):
        c = cond_base(stato, storia)
        if not c:
            return c
        ts = storia[-1].ts
        p = stato.get(ts // GIORNO)
        return storia[-1].close < p[0]  # p[0] = apertura del giorno (barra 00:00)

    return Variante("V31", base.tf, base.direzione, base.prepara, condizione, base.segnale, base.uscita)


def v32(quantile=0.5, vid="V32"):
    """Ritocco di V31: in piu' il filtro di volatilita' bassa.

    Volatilita' = deviazione standard dei rendimenti logaritmici a 30 minuti delle ultime
    960 barre (20 giorni), barra del segnale compresa. Filtro: alla barra delle 23:00 la
    volatilita' e' <= alla mediana dei valori alle barre delle 23:00 dei 365 giorni prima.
    """
    base = v31()
    GIORNO = 86_400_000

    def prepara(candele):
        stato = base.prepara(candele)
        c = arr(candele, "close")
        lr = np.zeros(c.size)
        lr[1:] = np.diff(np.log(c))
        s1 = np.cumsum(np.insert(lr, 0, 0.0))
        s2 = np.cumsum(np.insert(lr * lr, 0, 0.0))
        n = 960
        vol = {}
        storico = []  # (ts, vol) alle barre delle 23:00
        mediana = {}
        for i, x in enumerate(candele):
            if x.ts % GIORNO != 23 * 3_600_000 or i < n:
                continue
            m = (s1[i + 1] - s1[i + 1 - n]) / n
            var = (s2[i + 1] - s2[i + 1 - n]) / n - m * m
            v = math.sqrt(max(var, 0.0) * n / (n - 1))
            prec = [w for t, w in storico if t >= x.ts - 365 * GIORNO]
            if len(prec) >= 300:
                mediana[x.ts] = float(np.quantile(prec, quantile))
            vol[x.ts] = v
            storico.append((x.ts, v))
        stato = dict(stato)
        stato["_vol"] = vol
        stato["_mediana"] = mediana
        return stato

    def condizione(stato, storia):
        ts = storia[-1].ts
        if not stato["_mediana"] or ts < min(stato["_mediana"]):
            return None  # riscaldamento: la variante non puo' ancora entrare
        c = base.condizione(stato, storia)
        if not c:
            return c
        if ts not in stato["_mediana"]:
            return None
        return stato["_vol"][ts] <= stato["_mediana"][ts]

    return Variante(vid, base.tf, base.direzione, prepara, condizione, base.segnale, base.uscita)


def v33():
    """Ritocco di V31: in piu' il filtro «solo sabato e domenica» (giorno UTC del segnale)."""
    base = v31()

    def condizione(stato, storia):
        c = base.condizione(stato, storia)
        if not c:
            return c
        return datetime.fromtimestamp(storia[-1].ts / 1000, tz=timezone.utc).weekday() >= 5

    return Variante("V33", base.tf, base.direzione, base.prepara, condizione, base.segnale, base.uscita)


def v34():
    """Ritocco di V31: in piu' i due filtri di V32 (volatilita' bassa) e V33 (fine settimana)."""
    a, b = v32(), v33()

    def condizione(stato, storia):
        c = a.condizione(stato, storia)
        if not c:
            return c
        return b.condizione(stato, storia)

    return Variante("V34", a.tf, a.direzione, a.prepara, condizione, a.segnale, a.uscita)


def v35():
    """Ritocco di V31: filtro di volatilita' come V32 ma con soglia al 75° percentile."""
    return v32(quantile=0.75, vid="V35")


def v36(M=2190, vid="V36"):
    """Ritocco di V28: in piu' il filtro di volatilita' alta.

    Volatilita' = deviazione standard dei rendimenti logaritmici a 4 ore delle ultime 960
    barre, barra del segnale compresa (la misura dello studio dei fallimenti). Filtro: sopra
    la mediana dei suoi valori nelle 2.190 barre precedenti (365 giorni).
    """
    base = v28()
    N = 960

    def prepara(candele):
        stato = base.prepara(candele)
        c = arr(candele, "close")
        lr = np.zeros(c.size)
        lr[1:] = np.diff(np.log(c))
        s1 = np.cumsum(np.insert(lr, 0, 0.0))
        s2 = np.cumsum(np.insert(lr * lr, 0, 0.0))
        vol = np.full(c.size, np.nan)
        for i in range(N, c.size):
            m = (s1[i + 1] - s1[i + 1 - N]) / N
            vol[i] = math.sqrt(max((s2[i + 1] - s2[i + 1 - N]) / N - m * m, 0.0) * N / (N - 1))
        med = np.full(c.size, np.nan)
        for i in range(N + M, c.size):
            med[i] = np.median(vol[i - M:i])
        for x, v, mm in zip(candele, vol, med):
            stato[x.ts] = dict(stato[x.ts], vol=float(v), med=float(mm))
        return stato

    def condizione(stato, storia):
        s = stato[storia[-1].ts]
        if nan(s["med"]):
            return None
        c = base.condizione(stato, storia)
        if not c:
            return c
        return s["vol"] > s["med"]

    return Variante(vid, base.tf, base.direzione, prepara, condizione, base.segnale, base.uscita)


def v37():
    """Ritocco di V28: come V36 ma la mediana si calcola sulle 1.095 barre precedenti (182 giorni)."""
    return v36(M=1095, vid="V37")


TUTTE = {f"V{n:02d}": globals()[f"v{n:02d}"] for n in range(1, 38)}
