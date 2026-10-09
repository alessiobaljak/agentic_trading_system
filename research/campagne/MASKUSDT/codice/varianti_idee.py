"""Le varianti delle idee nuove (ipotesi.md, I-01 ... I-14), con le regole esatte registrate.

Ogni classe implementa la condizione d'ingresso dell'ipotesi; stop, target e uscita a
tempo vengono da ``VarianteATR``. Gli indicatori si calcolano una volta su tutte le
barre del periodo e sono causali (il valore alla barra i usa solo barre <= i).
"""
from __future__ import annotations

import math
from datetime import datetime, timezone

import numpy as np

import quadro
from indicatori import (deviazione_precedente, massimo_precedente, minimo_precedente, percentile_precedente,
                        rendimento, rsi, sma, somma_mobile)
from varianti_base import VarianteATR


def _ok(*valori):
    return all(not (isinstance(v, float) and math.isnan(v)) and v is not None for v in valori)


# ---------------------------------------------------------------------------
# I-01 momento nel tempo, 4h
# ---------------------------------------------------------------------------
class I01(VarianteATR):
    tf = "4h"
    k_stop = 2.0
    rr = None
    barre_max = 18

    def prepara_condizione(self, st):
        st["ret42"] = rendimento(st["c"], 42)

    def pronta(self, st, i):
        return super().pronta(st, i) and _ok(st["ret42"][i])


class I01L(I01):
    direzione = "long"

    def condizione(self, st, i):
        return st["ret42"][i] > 0


class I01S(I01):
    direzione = "short"

    def condizione(self, st, i):
        return st["ret42"][i] < 0


# ---------------------------------------------------------------------------
# I-02 rottura del canale di 48 barre, 1h
# ---------------------------------------------------------------------------
class I02(VarianteATR):
    tf = "1h"
    k_stop = 2.0
    rr = None
    barre_max = 24

    def prepara_condizione(self, st):
        st["hh"] = massimo_precedente(st["h"], 48)
        st["ll"] = minimo_precedente(st["l"], 48)

    def pronta(self, st, i):
        return super().pronta(st, i) and _ok(st["hh"][i], st["ll"][i])


class I02L(I02):
    direzione = "long"

    def condizione(self, st, i):
        return st["c"][i] > st["hh"][i]


class I02S(I02):
    direzione = "short"

    def condizione(self, st, i):
        return st["c"][i] < st["ll"][i]


# ---------------------------------------------------------------------------
# I-03 ritorno dopo una barra estrema, 1h
# ---------------------------------------------------------------------------
class I03(VarianteATR):
    tf = "1h"
    k_stop = 2.0
    rr = 1.0
    barre_max = 6

    def prepara_condizione(self, st):
        r1 = rendimento(st["c"], 1)
        st["r1"] = r1
        st["sd168"] = deviazione_precedente(r1, 168)

    def pronta(self, st, i):
        return super().pronta(st, i) and _ok(st["r1"][i], st["sd168"][i])


class I03L(I03):
    direzione = "long"

    def condizione(self, st, i):
        return st["r1"][i] < -3.0 * st["sd168"][i]


class I03S(I03):
    direzione = "short"

    def condizione(self, st, i):
        return st["r1"][i] > 3.0 * st["sd168"][i]


# ---------------------------------------------------------------------------
# I-04 ritracciamento a 2 periodi nel trend, 1h
# ---------------------------------------------------------------------------
class I04(VarianteATR):
    tf = "1h"
    k_stop = 3.0
    rr = None
    barre_max = 48

    def prepara_condizione(self, st):
        st["sma200"] = sma(st["c"], 200)
        st["sma5"] = sma(st["c"], 5)
        st["rsi2"] = rsi(st["c"], 2)

    def pronta(self, st, i):
        return super().pronta(st, i) and _ok(st["sma200"][i], st["sma5"][i], st["rsi2"][i])


class I04L(I04):
    direzione = "long"

    def condizione(self, st, i):
        return st["c"][i] > st["sma200"][i] and st["rsi2"][i] < 10

    def uscita(self, st, i, pos, k):
        if st["c"][i] > st["sma5"][i]:
            return "chiudi"
        return super().uscita(st, i, pos, k)


class I04S(I04):
    direzione = "short"

    def condizione(self, st, i):
        return st["c"][i] < st["sma200"][i] and st["rsi2"][i] > 90

    def uscita(self, st, i, pos, k):
        if st["c"][i] < st["sma5"][i]:
            return "chiudi"
        return super().uscita(st, i, pos, k)


# ---------------------------------------------------------------------------
# I-05 funding estremo, 8h
# ---------------------------------------------------------------------------
class I05(VarianteATR):
    tf = "8h"
    k_stop = 2.0
    rr = None
    barre_max = 3

    def prepara_condizione(self, st):
        fund = st["per"].funding  # (ts, tasso) ordinati, solo fino alla fine del periodo
        ts_f = np.array([t for t, _ in fund], dtype=np.int64)
        tassi = np.array([r for _, r in fund], dtype=float)
        p90 = percentile_precedente(tassi, 270, 90)
        p10 = percentile_precedente(tassi, 270, 10)
        n = len(st["c"])
        f = np.full(n, np.nan)
        a90 = np.full(n, np.nan)
        a10 = np.full(n, np.nan)
        for i, cand in enumerate(st["candele"]):
            j = int(np.searchsorted(ts_f, cand.close_ts, side="right")) - 1  # ultimo settlement entro la chiusura
            if j >= 0:
                f[i], a90[i], a10[i] = tassi[j], p90[j], p10[j]
        st["f"], st["f90"], st["f10"] = f, a90, a10

    def pronta(self, st, i):
        return super().pronta(st, i) and _ok(st["f"][i], st["f90"][i], st["f10"][i])


class I05S(I05):
    direzione = "short"

    def condizione(self, st, i):
        return st["f"][i] > st["f90"][i] and st["f"][i] > 0


class I05L(I05):
    direzione = "long"

    def condizione(self, st, i):
        return st["f"][i] < st["f10"][i] and st["f"][i] < 0.0001


# ---------------------------------------------------------------------------
# I-06 volume alto, 4h
# ---------------------------------------------------------------------------
class I06L(VarianteATR):
    tf = "4h"
    direzione = "long"
    k_stop = 3.0
    rr = None
    barre_max = 30

    def prepara_condizione(self, st):
        v = np.array([np.nan if x is None else x for x in st["per"].volume_usdt], dtype=float)
        v6 = somma_mobile(v, 6)
        n = len(v)
        rif = np.full(n, np.nan)
        # media per barra delle 294 barre prima della finestra di 6 (i-299 .. i-6), per 6
        for i in range(299, n):
            w = v[i - 299:i - 5]
            if not np.isnan(w).any():
                rif[i] = 6.0 * np.mean(w)
        st["v6"], st["rif6"] = v6, rif

    def pronta(self, st, i):
        return super().pronta(st, i) and _ok(st["v6"][i], st["rif6"][i])

    multiplo = 2.5

    def condizione(self, st, i):
        return st["v6"][i] > self.multiplo * st["rif6"][i]


class I06Lb(I06L):
    multiplo = 1.5
    barre_max = 12


# ---------------------------------------------------------------------------
# I-07 scarico dopo il pump, 1h
# ---------------------------------------------------------------------------
class I07(VarianteATR):
    tf = "1h"
    direzione = "short"
    k_stop = 2.0
    rr = None
    barre_max = 24
    soglia_dev = 3.0
    soglia_vol = 3.0

    def prepara_condizione(self, st):
        r3 = rendimento(st["c"], 3)
        v = np.array([np.nan if x is None else x for x in st["per"].volume_usdt], dtype=float)
        v3 = somma_mobile(v, 3)
        n = len(v)
        rif = np.full(n, np.nan)
        for i in range(171, n):
            w = v[i - 171:i - 3]  # le 168 barre prima della finestra di 3
            if not np.isnan(w).any():
                rif[i] = 3.0 * np.mean(w)
        st["r3"], st["sd3"], st["v3"], st["rif3"] = r3, deviazione_precedente(r3, 168), v3, rif

    def pronta(self, st, i):
        return super().pronta(st, i) and _ok(st["r3"][i], st["sd3"][i], st["v3"][i], st["rif3"][i])

    def condizione(self, st, i):
        return st["r3"][i] > self.soglia_dev * st["sd3"][i] and st["v3"][i] > self.soglia_vol * st["rif3"][i]


class I07S(I07):
    pass


class I07Sb(I07):
    soglia_dev = 2.5
    soglia_vol = 2.0


# ---------------------------------------------------------------------------
# I-08 MASK in ritardo su BTC, 1h
# ---------------------------------------------------------------------------
class I08(VarianteATR):
    tf = "1h"
    k_stop = 2.0
    rr = None
    barre_max = 4

    def prepara_condizione(self, st):
        per = st["per"]
        ms = per.ms_barra
        n = len(st["c"])
        rb = np.full(n, np.nan)
        rm = np.full(n, np.nan)
        cs = st["candele"]
        for i in range(1, n):
            contigue = cs[i].ts - cs[i - 1].ts == ms
            b0, b1 = per.btc[i - 1], per.btc[i]
            if contigue and b0 is not None and b1 is not None:
                rb[i] = math.log(b1.close / b0.close)
                rm[i] = math.log(cs[i].close / cs[i - 1].close)
        st["rb"], st["rm"], st["sdb"] = rb, rm, deviazione_precedente(rb, 168)

    def pronta(self, st, i):
        return super().pronta(st, i) and _ok(st["rb"][i], st["rm"][i], st["sdb"][i])


class I08L(I08):
    direzione = "long"
    dev = 2.0

    def condizione(self, st, i):
        return st["rb"][i] > self.dev * st["sdb"][i] and st["rm"][i] < 0.5 * st["rb"][i]


class I08S(I08):
    direzione = "short"
    dev = 2.0

    def condizione(self, st, i):
        return st["rb"][i] < -self.dev * st["sdb"][i] and st["rm"][i] > 0.5 * st["rb"][i]


class I08Lb(I08L):
    dev = 1.5


class I08Sb(I08S):
    dev = 1.5


# ---------------------------------------------------------------------------
# I-15 momento intraday, 30m
# ---------------------------------------------------------------------------
class I15(VarianteATR):
    tf = "30m"
    k_stop = 2.0
    rr = None
    barre_max = 1

    def prepara_condizione(self, st):
        cs = st["candele"]
        n = len(cs)
        primo = {}  # giorno -> segno della barra 00:00
        for c in cs:
            d = datetime.fromtimestamp(c.ts / 1000, tz=timezone.utc)
            if d.hour == 0 and d.minute == 0:
                primo[_giorno(c.ts)] = 1 if c.close > c.open else (-1 if c.close < c.open else 0)
        seg = np.zeros(n, dtype=int)
        for i, c in enumerate(cs):
            d = datetime.fromtimestamp(c.ts / 1000, tz=timezone.utc)
            if d.hour == 23 and d.minute == 0:
                seg[i] = primo.get(_giorno(c.ts), 0)
        st["seg"] = seg


class I15L(I15):
    direzione = "long"

    def condizione(self, st, i):
        return st["seg"][i] == 1


class I15S(I15):
    direzione = "short"

    def condizione(self, st, i):
        return st["seg"][i] == -1


# ---------------------------------------------------------------------------
# I-09 compressione delle bande e rottura, 1h
# ---------------------------------------------------------------------------
class I09(VarianteATR):
    tf = "1h"
    k_stop = 2.0
    rr = 2.0
    barre_max = 48

    def prepara_condizione(self, st):
        c = st["c"]
        n = len(c)
        m20 = sma(c, 20)
        sd20 = np.full(n, np.nan)
        for i in range(19, n):
            sd20[i] = np.std(c[i - 19:i + 1])  # deviazione della popolazione, come le bande di Bollinger
        bw = 4.0 * sd20 / m20
        p20 = percentile_precedente(bw, 500, 20)
        compressa = np.zeros(n, dtype=bool)
        valida = np.zeros(n, dtype=bool)
        for i in range(9, n):
            w = bw[i - 9:i + 1]
            if not np.isnan(p20[i]) and not np.isnan(w).any():
                valida[i] = True
                compressa[i] = w.min() <= p20[i]
        st["m20"], st["sd20"], st["compressa"], st["valida"] = m20, sd20, compressa, valida

    def pronta(self, st, i):
        return super().pronta(st, i) and bool(st["valida"][i])


class I09L(I09):
    direzione = "long"

    def condizione(self, st, i):
        return st["compressa"][i] and st["c"][i] > st["m20"][i] + 2.0 * st["sd20"][i]


class I09S(I09):
    direzione = "short"

    def condizione(self, st, i):
        return st["compressa"][i] and st["c"][i] < st["m20"][i] - 2.0 * st["sd20"][i]


# ---------------------------------------------------------------------------
# I-10 martello e stella cadente, 1h
# ---------------------------------------------------------------------------
class I10(VarianteATR):
    tf = "1h"
    k_stop = 2.0
    rr = 1.0
    barre_max = 12
    riscaldamento = 23

    def prepara_condizione(self, st):
        o, h, l, c = st["o"], st["h"], st["l"], st["c"]
        st["corpo"] = np.abs(c - o)
        st["escursione"] = h - l
        st["ombra_inf"] = np.minimum(o, c) - l
        st["ombra_sup"] = h - np.maximum(o, c)


class I10L(I10):
    direzione = "long"

    def condizione(self, st, i):
        if st["escursione"][i] <= 0:
            return False
        return (st["ombra_inf"][i] >= 2.0 * st["corpo"][i] and st["ombra_sup"][i] <= 0.25 * st["escursione"][i]
                and st["l"][i] <= np.min(st["l"][i - 23:i + 1]))


class I10S(I10):
    direzione = "short"

    def condizione(self, st, i):
        if st["escursione"][i] <= 0:
            return False
        return (st["ombra_sup"][i] >= 2.0 * st["corpo"][i] and st["ombra_inf"][i] <= 0.25 * st["escursione"][i]
                and st["h"][i] >= np.max(st["h"][i - 23:i + 1]))


# ---------------------------------------------------------------------------
# I-11 rottura dell'intervallo d'apertura della giornata UTC, 1h
# ---------------------------------------------------------------------------
def _ora(ts):
    return datetime.fromtimestamp(ts / 1000, tz=timezone.utc).hour


def _giorno(ts):
    return ts // 86_400_000


class I11(VarianteATR):
    tf = "1h"
    k_stop = 1.5
    rr = None
    barre_max = None

    def prepara_condizione(self, st):
        cs = st["candele"]
        n = len(cs)
        rottura = np.zeros(n, dtype=int)  # +1 primo close sopra, -1 primo close sotto, 0 altrimenti
        ore = np.array([_ora(c.ts) for c in cs])
        per_giorno = {}
        for i, c in enumerate(cs):
            per_giorno.setdefault(_giorno(c.ts), {})[ore[i]] = i
        for g, mappa in per_giorno.items():
            if 0 not in mappa or 1 not in mappa:
                continue
            hi = max(cs[mappa[0]].high, cs[mappa[1]].high)
            lo = min(cs[mappa[0]].low, cs[mappa[1]].low)
            for ora in range(2, 12):
                if ora not in mappa:
                    continue
                i = mappa[ora]
                if cs[i].close > hi:
                    rottura[i] = 1
                    break
                if cs[i].close < lo:
                    rottura[i] = -1
                    break
        st["rottura"], st["ore"] = rottura, ore

    def uscita(self, st, i, pos, k):
        if st["ore"][i] == 23:
            return "chiudi"
        return None


class I11L(I11):
    direzione = "long"

    def condizione(self, st, i):
        return st["rottura"][i] == 1


class I11S(I11):
    direzione = "short"

    def condizione(self, st, i):
        return st["rottura"][i] == -1


# ---------------------------------------------------------------------------
# I-12 squilibrio degli ordini aggressivi, 1h
# ---------------------------------------------------------------------------
class I12(VarianteATR):
    tf = "1h"
    k_stop = 2.0
    rr = None
    barre_max = 6

    def prepara_condizione(self, st):
        dati_v = quadro.volume_aggressivo(self.tf)
        qv = np.array([dati_v.get(c.ts, (np.nan, np.nan))[0] for c in st["candele"]], dtype=float)
        tb = np.array([dati_v.get(c.ts, (np.nan, np.nan))[1] for c in st["candele"]], dtype=float)
        q3 = somma_mobile(qv, 3)
        t3 = somma_mobile(tb, 3)
        quota = np.where(q3 > 0, t3 / np.where(q3 > 0, q3, 1.0), np.nan)
        st["quota"] = quota
        st["q90"] = percentile_precedente(quota, 500, 90)
        st["q10"] = percentile_precedente(quota, 500, 10)

    def pronta(self, st, i):
        return super().pronta(st, i) and _ok(st["quota"][i], st["q90"][i], st["q10"][i])


class I12L(I12):
    direzione = "long"

    def condizione(self, st, i):
        return st["quota"][i] > st["q90"][i]


class I12S(I12):
    direzione = "short"

    def condizione(self, st, i):
        return st["quota"][i] < st["q10"][i]


# ---------------------------------------------------------------------------
# I-13 trend del mercato (BTC), 4h
# ---------------------------------------------------------------------------
class I13L(VarianteATR):
    tf = "4h"
    direzione = "long"
    k_stop = 2.0
    rr = None
    barre_max = 18

    def prepara_condizione(self, st):
        bc = np.array([np.nan if b is None else b.close for b in st["per"].btc], dtype=float)
        st["bc"], st["bm42"] = bc, sma(bc, 42)  # un NaN nella finestra rende NaN la media

    def pronta(self, st, i):
        return super().pronta(st, i) and i >= 6 and _ok(st["bc"][i], st["bm42"][i], st["bm42"][i - 6])

    def condizione(self, st, i):
        return st["bc"][i] > st["bm42"][i] and st["bm42"][i] > st["bm42"][i - 6]


# ---------------------------------------------------------------------------
# I-14 scarto last-mark, 1h
# ---------------------------------------------------------------------------
class I14(VarianteATR):
    tf = "1h"
    k_stop = 2.0
    rr = None
    barre_max = 8

    def prepara_condizione(self, st):
        mc = np.array([m.close for m in st["per"].mark], dtype=float)
        prem = (st["c"] - mc) / mc
        st["prem"] = prem
        st["p95"] = percentile_precedente(prem, 720, 95)
        st["p5"] = percentile_precedente(prem, 720, 5)

    def pronta(self, st, i):
        return super().pronta(st, i) and _ok(st["prem"][i], st["p95"][i], st["p5"][i])


class I14S(I14):
    direzione = "short"

    def condizione(self, st, i):
        return st["prem"][i] > st["p95"][i] and st["prem"][i] > 0


class I14L(I14):
    direzione = "long"

    def condizione(self, st, i):
        return st["prem"][i] < st["p5"][i] and st["prem"][i] < 0
