"""Le varianti della campagna LTCUSDT. Ogni variante e' scritta qui e in ipotesi.md PRIMA del test.

REGISTRO: id -> (funzione che crea la variante, metadati della registrazione).

Convenzioni (vedi quadro.py): ``prepara`` calcola indicatori causali (indice i = barre 0..i);
``entra`` e' la condizione d'ingresso; ``segnale`` il Segnale senza condizione d'ingresso, None
nel riscaldamento (prima barra in cui la variante puo' entrare: ``riscaldamento``); ``esci`` la
chiusura all'apertura della barra dopo.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))

import indicatori as I  # noqa: E402
import quadro  # noqa: E402
from research.src.motore import Segnale  # noqa: E402

STOP_MAX = 0.06  # stop_massimo_bot di parametri.yaml


def _ok(*valori) -> bool:
    return all(v is not None and not (isinstance(v, float) and math.isnan(v)) for v in valori)


class Base(quadro.Variante):
    riscaldamento = 0

    def stop_distanza(self, i, ind):
        """Distanza dello stop in frazione del close di segnale."""
        raise NotImplementedError

    def segnale(self, i, ind):
        if i < self.riscaldamento:
            return None
        c = float(ind["close"][i])
        d = self.stop_distanza(i, ind)
        if not _ok(c, d) or d <= 0:
            return None
        if self.direzione == "long":
            return Segnale("long", stop=c * (1 - d))
        return Segnale("short", stop=c * (1 + d))


# ---------------------------------------------------------------------------
# I-01 momentum di serie temporale settimanale (LTCUSDT-001, -002)
# ---------------------------------------------------------------------------


class MomentumSettimanale(Base):
    tf = "1d"
    riscaldamento = 7

    def __init__(self, direzione):
        self.direzione = direzione

    def prepara(self, candele):
        s = I.serie(candele)
        return {"close": s["close"], "r7": I.rendimento(s["close"], 7)}

    def entra(self, i, ind):
        r = ind["r7"][i]
        if math.isnan(r):
            return False
        return r > 0 if self.direzione == "long" else r < 0

    def stop_distanza(self, i, ind):
        return STOP_MAX

    def esci(self, i, ind, pos):
        return quadro.tempo_in_barre(i, ind, pos) >= 7


# ---------------------------------------------------------------------------
# I-02 breakout di canale (LTCUSDT-003, -004)
# ---------------------------------------------------------------------------


class BreakoutCanale(Base):
    tf = "4h"
    riscaldamento = 20

    def __init__(self, direzione):
        self.direzione = direzione

    def prepara(self, candele):
        s = I.serie(candele)
        return {
            "close": s["close"],
            "max20": I.ritardo(I.rolling_max(s["high"], 20), 1),
            "min20": I.ritardo(I.rolling_min(s["low"], 20), 1),
            "max10": I.ritardo(I.rolling_max(s["high"], 10), 1),
            "min10": I.ritardo(I.rolling_min(s["low"], 10), 1),
            "atr20": I.atr(s["high"], s["low"], s["close"], 20),
        }

    def entra(self, i, ind):
        c = ind["close"][i]
        if self.direzione == "long":
            return bool(c > ind["max20"][i])
        return bool(c < ind["min20"][i])

    def stop_distanza(self, i, ind):
        a = ind["atr20"][i]
        if math.isnan(a):
            return None
        return min(2 * a / ind["close"][i], STOP_MAX)

    def esci(self, i, ind, pos):
        c = ind["close"][i]
        if self.direzione == "long":
            return bool(c < ind["min10"][i])
        return bool(c > ind["max10"][i])


# ---------------------------------------------------------------------------
# I-03 RSI a 2 periodi dentro la tendenza (LTCUSDT-005, -006)
# ---------------------------------------------------------------------------


class RSI2(Base):
    tf = "4h"
    riscaldamento = 199  # la media a 200 barre esiste dalla barra 199

    def __init__(self, direzione):
        self.direzione = direzione

    def prepara(self, candele):
        s = I.serie(candele)
        return {"close": s["close"], "sma200": I.sma(s["close"], 200), "sma5": I.sma(s["close"], 5),
                "rsi2": I.rsi(s["close"], 2)}

    def entra(self, i, ind):
        c, m, r = ind["close"][i], ind["sma200"][i], ind["rsi2"][i]
        if math.isnan(m) or math.isnan(r):
            return False
        if self.direzione == "long":
            return bool(c > m and r < 10)
        return bool(c < m and r > 90)

    def stop_distanza(self, i, ind):
        return STOP_MAX

    def esci(self, i, ind, pos):
        c, m5 = ind["close"][i], ind["sma5"][i]
        if math.isnan(m5):
            return False
        return bool(c > m5) if self.direzione == "long" else bool(c < m5)


# ---------------------------------------------------------------------------
# I-04 inversione dopo shock con volume alto (LTCUSDT-007, -008)
# ---------------------------------------------------------------------------


class ShockVolume(Base):
    tf = "1h"
    riscaldamento = 169

    def __init__(self, direzione):
        self.direzione = direzione

    def prepara(self, candele):
        s = I.serie(candele)
        r1 = I.rendimento(s["close"], 1)
        sd = I.ritardo(I.rolling_std(r1, 168), 1)
        import pandas as pd
        med = I.ritardo(pd.Series(s["volume"]).rolling(168, min_periods=168).median().to_numpy(), 1)
        return {"close": s["close"], "r1": r1, "sd": sd, "vol": s["volume"], "med_vol": med,
                "atr24": I.atr(s["high"], s["low"], s["close"], 24)}

    def entra(self, i, ind):
        r, sd, v, m = ind["r1"][i], ind["sd"][i], ind["vol"][i], ind["med_vol"][i]
        if math.isnan(r) or math.isnan(sd) or math.isnan(m) or sd <= 0:
            return False
        if v <= 3 * m:
            return False
        return bool(r < -2.5 * sd) if self.direzione == "long" else bool(r > 2.5 * sd)

    def stop_distanza(self, i, ind):
        a = ind["atr24"][i]
        if math.isnan(a):
            return None
        return min(2 * a / ind["close"][i], STOP_MAX)

    def esci(self, i, ind, pos):
        return quadro.tempo_in_barre(i, ind, pos) >= 12


# ---------------------------------------------------------------------------
# I-05 affollamento della leva misurato dal funding (LTCUSDT-009, -009b, -010)
# ---------------------------------------------------------------------------


def funding_noto(candele, n_ultimi: int) -> np.ndarray:
    """Media degli ultimi ``n_ultimi`` settlement con istante <= chiusura della barra (NaN se meno)."""
    from datetime import datetime, timezone
    from research.src import dati
    ultimo = datetime.fromtimestamp(candele[-1].close_ts / 1000, tz=timezone.utc).date()
    righe = dati.carica_funding(quadro.SIMBOLO, quadro.PRIMO_GIORNO, ultimo)
    ts = np.array([t for t, _ in righe], dtype=np.int64)
    tassi = np.array([r for _, r in righe], dtype=float)
    out = np.full(len(candele), np.nan)
    for i, c in enumerate(candele):
        k = int(np.searchsorted(ts, c.close_ts, side="right"))  # settlement con ts <= close_ts
        if k >= n_ultimi:
            out[i] = tassi[k - n_ultimi:k].mean()
    return out


class FundingAffollato(Base):
    tf = "8h"

    def __init__(self, direzione, soglia):
        self.direzione = direzione
        self.soglia = soglia

    def prepara(self, candele):
        s = I.serie(candele)
        f = funding_noto(candele, 3)
        primo = int(np.argmax(~np.isnan(f))) if (~np.isnan(f)).any() else len(candele)
        self.riscaldamento = primo
        return {"close": s["close"], "funding3": f}

    def entra(self, i, ind):
        f = ind["funding3"][i]
        if math.isnan(f):
            return False
        if self.direzione == "long":
            return bool(f < 0)  # soglia "negativo": short affollati
        return bool(f >= self.soglia)

    def stop_distanza(self, i, ind):
        return STOP_MAX

    def esci(self, i, ind, pos):
        return quadro.tempo_in_barre(i, ind, pos) >= 9


# ---------------------------------------------------------------------------
# I-06 numeri tondi (LTCUSDT-011, -012)
# ---------------------------------------------------------------------------

LIVELLI_TONDI = np.array(sorted(set(list(range(5, 100, 5)) + list(range(100, 2001, 10)))), dtype=float)


class NumeriTondi(Base):
    tf = "1h"
    riscaldamento = 24

    def __init__(self, direzione):
        self.direzione = direzione

    def prepara(self, candele):
        s = I.serie(candele)
        c = s["close"]
        prec = I.ritardo(c, 1)
        su = np.zeros(len(c), dtype=bool)
        giu = np.zeros(len(c), dtype=bool)
        for i in range(1, len(c)):
            a, b = prec[i], c[i]
            if b > a:  # c'e' un livello L con a < L <= b ?
                k = np.searchsorted(LIVELLI_TONDI, a, side="right")
                su[i] = k < len(LIVELLI_TONDI) and LIVELLI_TONDI[k] <= b
            elif b < a:  # c'e' un livello L con b <= L < a ?
                k = np.searchsorted(LIVELLI_TONDI, b, side="left")
                giu[i] = k < len(LIVELLI_TONDI) and LIVELLI_TONDI[k] < a
        return {"close": c, "su": su, "giu": giu, "atr24": I.atr(s["high"], s["low"], c, 24)}

    def entra(self, i, ind):
        return bool(ind["su"][i]) if self.direzione == "long" else bool(ind["giu"][i])

    def stop_distanza(self, i, ind):
        a = ind["atr24"][i]
        if math.isnan(a):
            return None
        return min(2 * a / ind["close"][i], STOP_MAX)

    def esci(self, i, ind, pos):
        return quadro.tempo_in_barre(i, ind, pos) >= 6


# ---------------------------------------------------------------------------
# I-07 breakout del range d'apertura (LTCUSDT-013, -014)
# ---------------------------------------------------------------------------


class RangeApertura(Base):
    tf = "1h"

    def __init__(self, direzione):
        self.direzione = direzione

    def prepara(self, candele):
        s = I.serie(candele)
        n = len(candele)
        giorno = s["ts"] // 86_400_000
        ora = I.ora_utc(s["ts"])
        r_alto = np.full(n, np.nan)
        r_basso = np.full(n, np.nan)
        primo_sopra = np.zeros(n, dtype=bool)
        primo_sotto = np.zeros(n, dtype=bool)
        # range delle barre 00-03 della giornata, solo se tutte e quattro presenti
        per_giorno = {}
        for i in range(n):
            if ora[i] <= 3:
                per_giorno.setdefault(int(giorno[i]), []).append(i)
        visto_sopra = {}
        visto_sotto = {}
        for i in range(n):
            g = int(giorno[i])
            idx = per_giorno.get(g, [])
            if 4 <= ora[i] <= 20 and len(idx) == 4:
                alto = max(s["high"][j] for j in idx)
                basso = min(s["low"][j] for j in idx)
                r_alto[i], r_basso[i] = alto, basso
                if s["close"][i] > alto and not visto_sopra.get(g):
                    primo_sopra[i] = True
                    visto_sopra[g] = True
                if s["close"][i] < basso and not visto_sotto.get(g):
                    primo_sotto[i] = True
                    visto_sotto[g] = True
        # altezza relativa del range di ogni giorno completo e mediana dei 20 giorni completi precedenti
        altezza_giorno = {}
        for g, idx in per_giorno.items():
            if len(idx) == 4:
                alto = max(s["high"][j] for j in idx)
                basso = min(s["low"][j] for j in idx)
                altezza_giorno[g] = (alto - basso) / basso
        giorni = sorted(altezza_giorno)
        mediana_prec = {}
        for k, g in enumerate(giorni):
            if k >= 20:
                mediana_prec[g] = float(np.median([altezza_giorno[x] for x in giorni[k - 20:k]]))
        stretto = np.zeros(n, dtype=bool)
        primo = n
        for i in range(n):
            g = int(giorno[i])
            if g in mediana_prec:
                primo = min(primo, i)
                stretto[i] = altezza_giorno[g] < mediana_prec[g]
        if getattr(self, "solo_stretto", False):
            self.riscaldamento = primo  # la variante col filtro puo' entrare solo da qui
        return {"close": s["close"], "ora": ora, "r_alto": r_alto, "r_basso": r_basso,
                "primo_sopra": primo_sopra, "primo_sotto": primo_sotto, "stretto": stretto}

    def entra(self, i, ind):
        if getattr(self, "solo_stretto", False) and not ind["stretto"][i]:
            return False
        return bool(ind["primo_sopra"][i]) if self.direzione == "long" else bool(ind["primo_sotto"][i])

    def stop_distanza(self, i, ind):
        c = ind["close"][i]
        fisso = getattr(self, "stop_fisso", None)
        if fisso is not None:
            # stesso campo di validita' del segnale originale (range definito, close dalla parte giusta)
            riferimento = ind["r_basso"][i] if self.direzione == "long" else ind["r_alto"][i]
            if math.isnan(riferimento):
                return None
            return fisso
        if self.direzione == "long":
            b = ind["r_basso"][i]
            if math.isnan(b) or b >= c:
                return None
            return min((c - b) / c, STOP_MAX)
        a = ind["r_alto"][i]
        if math.isnan(a) or a <= c:
            return None
        return min((a - c) / c, STOP_MAX)

    def esci(self, i, ind, pos):
        return int(ind["ora"][i]) == 23


# ---------------------------------------------------------------------------
# I-08 lunedi' (LTCUSDT-015)
# ---------------------------------------------------------------------------


class Lunedi(Base):
    tf = "1d"
    direzione = "long"

    def prepara(self, candele):
        s = I.serie(candele)
        return {"close": s["close"], "dow": I.giorno_settimana(s["ts"])}

    def entra(self, i, ind):
        return int(ind["dow"][i]) == 6  # chiusura della domenica: si entra il lunedi'

    def stop_distanza(self, i, ind):
        return STOP_MAX

    def esci(self, i, ind, pos):
        return quadro.tempo_in_barre(i, ind, pos) >= 1


# ---------------------------------------------------------------------------
# I-09 squeeze delle bande (LTCUSDT-016, -017)
# ---------------------------------------------------------------------------


class Squeeze(Base):
    tf = "4h"
    riscaldamento = 141

    def __init__(self, direzione, percentile=0.1):
        self.direzione = direzione
        self.percentile = percentile

    def prepara(self, candele):
        import pandas as pd
        s = I.serie(candele)
        c = s["close"]
        m = I.sma(c, 20)
        sd = I.rolling_std(c, 20)
        su, giu = m + 2 * sd, m - 2 * sd
        bw = (su - giu) / m
        q = pd.Series(bw).rolling(120, min_periods=120).quantile(self.percentile).to_numpy()
        squeeze_prec = I.ritardo(bw, 1) <= I.ritardo(q, 2)  # bw[i-1] <= 10° percentile di bw[i-121..i-2]
        return {"close": c, "media": m, "su": su, "giu": giu, "squeeze_prec": squeeze_prec}

    def entra(self, i, ind):
        if not ind["squeeze_prec"][i]:
            return False
        c = ind["close"][i]
        return bool(c > ind["su"][i]) if self.direzione == "long" else bool(c < ind["giu"][i])

    def stop_distanza(self, i, ind):
        c, m = ind["close"][i], ind["media"][i]
        if math.isnan(m):
            return None
        d = (c - m) / c if self.direzione == "long" else (m - c) / c
        if d <= 0:
            return None
        return min(d, STOP_MAX)

    def esci(self, i, ind, pos):
        c, m = ind["close"][i], ind["media"][i]
        if quadro.tempo_in_barre(i, ind, pos) >= 30:
            return True
        return bool(c < m) if self.direzione == "long" else bool(c > m)


class Squeeze2h(Squeeze):
    tf = "2h"


# ---------------------------------------------------------------------------
# I-10 inerzia dopo un giorno anomalo (LTCUSDT-018, -019 e le condizionali b)
# ---------------------------------------------------------------------------


class GiornoAnomalo(Base):
    tf = "1d"
    riscaldamento = 31

    def __init__(self, direzione, k):
        self.direzione = direzione
        self.k = k

    def prepara(self, candele):
        s = I.serie(candele)
        r = I.rendimento(s["close"], 1)
        return {"close": s["close"], "r": r, "m": I.ritardo(I.sma(r, 30), 1), "s": I.ritardo(I.rolling_std(r, 30), 1)}

    def entra(self, i, ind):
        r, m, s = ind["r"][i], ind["m"][i], ind["s"][i]
        if math.isnan(r) or math.isnan(m) or math.isnan(s):
            return False
        return bool(r > m + self.k * s) if self.direzione == "long" else bool(r < m - self.k * s)

    def stop_distanza(self, i, ind):
        return STOP_MAX

    def esci(self, i, ind, pos):
        return quadro.tempo_in_barre(i, ind, pos) >= 1


# ---------------------------------------------------------------------------
# I-11 continuazione dopo shock con volume alto (LTCUSDT-020, -021)
# ---------------------------------------------------------------------------


class ContinuazioneVolume(ShockVolume):
    def entra(self, i, ind):
        r, sd, v, m = ind["r1"][i], ind["sd"][i], ind["vol"][i], ind["med_vol"][i]
        if math.isnan(r) or math.isnan(sd) or math.isnan(m) or sd <= 0:
            return False
        if v <= 3 * m:
            return False
        return bool(r > 2.5 * sd) if self.direzione == "long" else bool(r < -2.5 * sd)


# ---------------------------------------------------------------------------
# I-12 premio del perpetuo sul mark (LTCUSDT-022, -023)
# ---------------------------------------------------------------------------


class PremioMark(Base):
    tf = "1h"
    riscaldamento = 169

    def __init__(self, direzione):
        self.direzione = direzione

    def prepara(self, candele):
        from datetime import datetime, timezone
        from research.src import dati
        s = I.serie(candele)
        fine = datetime.fromtimestamp(candele[-1].close_ts / 1000, tz=timezone.utc).date()
        al = dati.carica_serie_allineate(quadro.SIMBOLO, self.tf, quadro.PRIMO_GIORNO, fine)
        mark = {m.ts: m.close for m in al["candele_mark"]}
        mc = np.array([mark[c.ts] for c in candele], dtype=float)  # stesse barre: la serie e' gia' allineata
        p = s["close"] / mc - 1
        return {"close": s["close"], "p": p, "m": I.ritardo(I.sma(p, 168), 1),
                "sd": I.ritardo(I.rolling_std(p, 168), 1), "atr24": I.atr(s["high"], s["low"], s["close"], 24)}

    def entra(self, i, ind):
        p, m, sd = ind["p"][i], ind["m"][i], ind["sd"][i]
        if math.isnan(m) or math.isnan(sd) or sd <= 0:
            return False
        return bool(p > m + 3 * sd) if self.direzione == "short" else bool(p < m - 3 * sd)

    def stop_distanza(self, i, ind):
        a = ind["atr24"][i]
        if math.isnan(a):
            return None
        return min(2 * a / ind["close"][i], STOP_MAX)

    def esci(self, i, ind, pos):
        return quadro.tempo_in_barre(i, ind, pos) >= 4


# ---------------------------------------------------------------------------
# I-13 incrocio della media mobile con banda e tenuta fissa (LTCUSDT-024, -025)
# ---------------------------------------------------------------------------


class IncrocioMedia(Base):
    tf = "4h"
    riscaldamento = 50

    def __init__(self, direzione):
        self.direzione = direzione

    def prepara(self, candele):
        s = I.serie(candele)
        c = s["close"]
        m = I.sma(c, 50)
        return {"close": c, "c_prec": I.ritardo(c, 1), "m": m, "m_prec": I.ritardo(m, 1)}

    def entra(self, i, ind):
        c, cp, m, mp = ind["close"][i], ind["c_prec"][i], ind["m"][i], ind["m_prec"][i]
        if math.isnan(m) or math.isnan(mp):
            return False
        if self.direzione == "long":
            return bool(c > 1.01 * m and cp <= 1.01 * mp)
        return bool(c < 0.99 * m and cp >= 0.99 * mp)

    def stop_distanza(self, i, ind):
        return STOP_MAX

    def esci(self, i, ind, pos):
        return quadro.tempo_in_barre(i, ind, pos) >= 10


# ---------------------------------------------------------------------------
# Registro
# ---------------------------------------------------------------------------

FONTE_I01 = ("Yukun Liu, Aleh Tsyvinski, «Risks and Returns of Cryptocurrency», NBER Working Paper 24877, "
             "agosto 2018 (Review of Financial Studies 34(6), 2021); base: Moskowitz, Ooi, Pedersen, «Time Series "
             "Momentum», Journal of Financial Economics 104(2), 2012")
FONTE_I02 = "Curtis Faith, «Way of the Turtle», McGraw-Hill, 2007 (Sistema 1: breakout a 20, uscita a 10, stop 2 N)"
FONTE_I03 = "Larry Connors, Cesar Alvarez, «Short Term Trading Strategies That Work», TradingMarkets Publishing, 2008"
FONTE_I04 = ("John Y. Campbell, Sanford J. Grossman, Jiang Wang, «Trading Volume and Serial Correlation in Stock "
             "Returns», Quarterly Journal of Economics 108(4), novembre 1993")

FONTE_I05 = ("Maik Schmeling, Andreas Schrimpf, Karamfil Todorov, «Crypto Carry», BIS Working Papers n. 1087, "
             "marzo 2023")
FONTE_I06 = ("Carol L. Osler, «Currency Orders and Exchange Rate Dynamics: An Explanation for the Predictive Success "
             "of Technical Analysis», Journal of Finance 58(5), ottobre 2003")
FONTE_I07 = ("Toby Crabel, «Day Trading with Short Term Price Patterns and Opening Range Breakout», Traders Press, "
             "1990")
FONTE_I08 = ("Guglielmo Maria Caporale, Alex Plastun, «The day of the week effect in the cryptocurrency market», "
             "Finance Research Letters 31, dicembre 2019")

FONTE_I09 = "John Bollinger, «Bollinger on Bollinger Bands», McGraw-Hill, 2001 (lo squeeze)"
FONTE_I10 = ("Guglielmo Maria Caporale, Alex Plastun, «Price overreactions in the cryptocurrency market», Journal of "
             "Economic Studies 46(5), 2019 (CESifo Working Paper 7280, 2018)")

FONTE_I11 = ("Guillermo Llorente, Roni Michaely, Gideon Saar, Jiang Wang, «Dynamic Volume-Return Relation of "
             "Individual Stocks», Review of Financial Studies 15(4), 2002")
FONTE_I12 = ("Songrun He, Asaf Manela, Omri Ross, Victor von Wachter, «Fundamentals of Perpetual Futures», arXiv "
             "2212.06888, prima versione dicembre 2022")

def _stretto(v):
    v.solo_stretto = True
    return v


def _stop_fisso(v, d):
    v.stop_fisso = d
    return v


FONTE_I13 = ("William Brock, Josef Lakonishok, Blake LeBaron, «Simple Technical Trading Rules and the Stochastic "
             "Properties of Stock Returns», Journal of Finance 47(5), dicembre 1992; Robert Hudson, Andrew Urquhart, "
             "«Technical trading and cryptocurrencies», Annals of Operations Research 297(1), 2021 (online 2019)")

REGISTRO = {
    "LTCUSDT-001": (lambda: MomentumSettimanale("long"), {
        "idea": "I-01", "fonte": FONTE_I01,
        "meccanismo": "momentum di serie temporale: una settimana positiva prevede la settimana successiva",
        "parametri": {"lookback_giorni": 7, "soglia_rendimento": 0.0, "tenuta_barre": 7, "stop": 0.06, "target": None},
        "previsione": "profit factor fra 0,9 e 1,3; R medio fra -0,05 e +0,15; non batte nettamente la (b)"}),
    "LTCUSDT-002": (lambda: MomentumSettimanale("short"), {
        "idea": "I-01", "fonte": FONTE_I01,
        "meccanismo": "momentum di serie temporale: una settimana negativa prevede la settimana successiva",
        "parametri": {"lookback_giorni": 7, "soglia_rendimento": 0.0, "tenuta_barre": 7, "stop": 0.06, "target": None},
        "previsione": "profit factor fra 0,8 e 1,2; R medio fra -0,1 e +0,1; non batte nettamente la (b)"}),
    "LTCUSDT-003": (lambda: BreakoutCanale("long"), {
        "idea": "I-02", "fonte": FONTE_I02,
        "meccanismo": "breakout del massimo a 20 barre, uscita sul minimo a 10 barre",
        "parametri": {"canale_ingresso": 20, "canale_uscita": 10, "stop_atr": 2.0, "atr": 20, "stop_massimo": 0.06},
        "previsione": "profit factor fra 0,9 e 1,3; non batte nettamente la (b)"}),
    "LTCUSDT-004": (lambda: BreakoutCanale("short"), {
        "idea": "I-02", "fonte": FONTE_I02,
        "meccanismo": "breakout del minimo a 20 barre, uscita sul massimo a 10 barre",
        "parametri": {"canale_ingresso": 20, "canale_uscita": 10, "stop_atr": 2.0, "atr": 20, "stop_massimo": 0.06},
        "previsione": "profit factor fra 0,8 e 1,2; non batte nettamente la (b)"}),
    "LTCUSDT-005": (lambda: RSI2("long"), {
        "idea": "I-03", "fonte": FONTE_I03,
        "meccanismo": "ritorno verso la media dopo due barre di eccesso al ribasso, dentro una tendenza positiva",
        "parametri": {"media_tendenza": 200, "rsi": 2, "soglia_rsi": 10, "media_uscita": 5, "stop": 0.06},
        "previsione": "profit factor fra 0,9 e 1,4; R medio fra -0,05 e +0,1; non batte nettamente la (b)"}),
    "LTCUSDT-006": (lambda: RSI2("short"), {
        "idea": "I-03", "fonte": FONTE_I03,
        "meccanismo": "ritorno verso la media dopo due barre di eccesso al rialzo, dentro una tendenza negativa",
        "parametri": {"media_tendenza": 200, "rsi": 2, "soglia_rsi": 90, "media_uscita": 5, "stop": 0.06},
        "previsione": "profit factor fra 0,8 e 1,2; non batte nettamente la (b)"}),
    "LTCUSDT-007": (lambda: ShockVolume("long"), {
        "idea": "I-04", "fonte": FONTE_I04,
        "meccanismo": "inversione dopo un calo orario estremo con volume alto (domanda di liquidita' assorbita)",
        "parametri": {"finestra": 168, "soglia_sd": 2.5, "soglia_volume_mediana": 3.0, "tenuta_barre": 12,
                      "stop_atr": 2.0, "atr": 24, "stop_massimo": 0.06},
        "previsione": "profit factor fra 0,9 e 1,4; R medio fra -0,1 e +0,15; non batte nettamente la (b)"}),
    "LTCUSDT-008": (lambda: ShockVolume("short"), {
        "idea": "I-04", "fonte": FONTE_I04,
        "meccanismo": "inversione dopo un rialzo orario estremo con volume alto (domanda di liquidita' assorbita)",
        "parametri": {"finestra": 168, "soglia_sd": 2.5, "soglia_volume_mediana": 3.0, "tenuta_barre": 12,
                      "stop_atr": 2.0, "atr": 24, "stop_massimo": 0.06},
        "previsione": "profit factor fra 0,8 e 1,2; non batte nettamente la (b)"}),
    "LTCUSDT-009": (lambda: FundingAffollato("short", 0.0005), {
        "idea": "I-05", "fonte": FONTE_I05,
        "meccanismo": "short quando il funding resta alto per un giorno (long a leva affollati)",
        "parametri": {"settlement_media": 3, "soglia_funding": 0.0005, "tenuta_barre": 9, "stop": 0.06},
        "previsione": "profit factor fra 0,8 e 1,3; R medio fra -0,15 e +0,15; non batte nettamente la (b)"}),
    "LTCUSDT-009b": (lambda: FundingAffollato("short", 0.0003), {
        "idea": "I-05", "fonte": FONTE_I05,
        "meccanismo": "short quando il funding resta alto per un giorno (long a leva affollati); soglia allentata, scritta prima di ogni test",
        "parametri": {"settlement_media": 3, "soglia_funding": 0.0003, "tenuta_barre": 9, "stop": 0.06},
        "previsione": "profit factor fra 0,8 e 1,3; R medio fra -0,15 e +0,15; non batte nettamente la (b)"}),
    "LTCUSDT-010": (lambda: FundingAffollato("long", "negativo"), {
        "idea": "I-05", "fonte": FONTE_I05,
        "meccanismo": "long quando il funding resta negativo per un giorno (short affollati)",
        "parametri": {"settlement_media": 3, "soglia_funding": "< 0", "tenuta_barre": 9, "stop": 0.06},
        "previsione": "profit factor fra 0,8 e 1,3; non batte nettamente la (b)"}),
    "LTCUSDT-011": (lambda: NumeriTondi("long"), {
        "idea": "I-06", "fonte": FONTE_I06,
        "meccanismo": "continuazione dopo l'attraversamento verso l'alto di un numero tondo (stop di acquisto a catena)",
        "parametri": {"livelli": "multipli di 5 sotto 100, di 10 da 100", "tenuta_barre": 6, "stop_atr": 2.0, "atr": 24,
                      "stop_massimo": 0.06},
        "previsione": "profit factor fra 0,8 e 1,2; R medio fra -0,15 e +0,1; non batte nettamente la (b)"}),
    "LTCUSDT-012": (lambda: NumeriTondi("short"), {
        "idea": "I-06", "fonte": FONTE_I06,
        "meccanismo": "continuazione dopo l'attraversamento verso il basso di un numero tondo (stop di vendita a catena)",
        "parametri": {"livelli": "multipli di 5 sotto 100, di 10 da 100", "tenuta_barre": 6, "stop_atr": 2.0, "atr": 24,
                      "stop_massimo": 0.06},
        "previsione": "profit factor fra 0,8 e 1,2; R medio fra -0,15 e +0,1; non batte nettamente la (b)"}),
    "LTCUSDT-013": (lambda: RangeApertura("long"), {
        "idea": "I-07", "fonte": FONTE_I07,
        "meccanismo": "breakout al rialzo del range delle prime 4 ore UTC, chiusura a fine giornata",
        "parametri": {"range_ore": "00-03 UTC", "finestra_ingresso": "04-20 UTC", "uscita": "chiusura della barra delle 23",
                      "stop": "minimo del range, al massimo 6%"},
        "previsione": "profit factor fra 0,8 e 1,2; non batte nettamente la (b)"}),
    "LTCUSDT-014": (lambda: RangeApertura("short"), {
        "idea": "I-07", "fonte": FONTE_I07,
        "meccanismo": "breakout al ribasso del range delle prime 4 ore UTC, chiusura a fine giornata",
        "parametri": {"range_ore": "00-03 UTC", "finestra_ingresso": "04-20 UTC", "uscita": "chiusura della barra delle 23",
                      "stop": "massimo del range, al massimo 6%"},
        "previsione": "profit factor fra 0,8 e 1,2; non batte nettamente la (b)"}),
    "LTCUSDT-015": (lambda: Lunedi(), {
        "idea": "I-08", "fonte": FONTE_I08,
        "meccanismo": "rendimento anomalo del lunedi'",
        "parametri": {"giorno": "lunedi' (UTC)", "tenuta_barre": 1, "stop": 0.06},
        "previsione": "profit factor fra 0,8 e 1,3; R medio fra -0,05 e +0,1; non batte nettamente la (b)"}),
    "LTCUSDT-016": (lambda: Squeeze("long"), {
        "idea": "I-09", "fonte": FONTE_I09,
        "meccanismo": "breakout sopra la banda superiore dopo una compressione della volatilita'",
        "parametri": {"bande": 20, "deviazioni": 2, "finestra_squeeze": 120, "percentile_squeeze": 10,
                      "stop": "media a 20 barre, al massimo 6%", "uscita": "close sotto la media o 30 barre"},
        "previsione": "profit factor fra 0,8 e 1,3; non batte nettamente la (b)"}),
    "LTCUSDT-017": (lambda: Squeeze("short"), {
        "idea": "I-09", "fonte": FONTE_I09,
        "meccanismo": "breakout sotto la banda inferiore dopo una compressione della volatilita'",
        "parametri": {"bande": 20, "deviazioni": 2, "finestra_squeeze": 120, "percentile_squeeze": 10,
                      "stop": "media a 20 barre, al massimo 6%", "uscita": "close sopra la media o 30 barre"},
        "previsione": "profit factor fra 0,8 e 1,3; non batte nettamente la (b)"}),
    "LTCUSDT-016b": (lambda: Squeeze("long", 0.2), {
        "idea": "I-09", "fonte": FONTE_I09,
        "meccanismo": "breakout sopra la banda superiore dopo una compressione della volatilita'; squeeze allentato al 20° percentile dopo lo scarto della 016",
        "parametri": {"bande": 20, "deviazioni": 2, "finestra_squeeze": 120, "percentile_squeeze": 20,
                      "stop": "media a 20 barre, al massimo 6%", "uscita": "close sotto la media o 30 barre"},
        "previsione": "profit factor fra 0,8 e 1,3; non batte nettamente la (b)"}),
    "LTCUSDT-017b": (lambda: Squeeze("short", 0.2), {
        "idea": "I-09", "fonte": FONTE_I09,
        "meccanismo": "breakout sotto la banda inferiore dopo una compressione della volatilita'; squeeze allentato al 20° percentile",
        "parametri": {"bande": 20, "deviazioni": 2, "finestra_squeeze": 120, "percentile_squeeze": 20,
                      "stop": "media a 20 barre, al massimo 6%", "uscita": "close sopra la media o 30 barre"},
        "previsione": "profit factor fra 0,8 e 1,3; non batte nettamente la (b)"}),
    "LTCUSDT-016c": (lambda: Squeeze2h("long", 0.2), {
        "idea": "I-09", "fonte": FONTE_I09,
        "meccanismo": "breakout sopra la banda superiore dopo una compressione della volatilita'; 2h, squeeze al 20° percentile dopo gli scarti",
        "parametri": {"bande": 20, "deviazioni": 2, "finestra_squeeze": 120, "percentile_squeeze": 20,
                      "stop": "media a 20 barre, al massimo 6%", "uscita": "close sotto la media o 30 barre"},
        "previsione": "profit factor fra 0,8 e 1,3; non batte nettamente la (b)"}),
    "LTCUSDT-017c": (lambda: Squeeze2h("short", 0.2), {
        "idea": "I-09", "fonte": FONTE_I09,
        "meccanismo": "breakout sotto la banda inferiore dopo una compressione della volatilita'; 2h, squeeze al 20° percentile dopo gli scarti",
        "parametri": {"bande": 20, "deviazioni": 2, "finestra_squeeze": 120, "percentile_squeeze": 20,
                      "stop": "media a 20 barre, al massimo 6%", "uscita": "close sopra la media o 30 barre"},
        "previsione": "profit factor fra 0,8 e 1,3; non batte nettamente la (b)"}),
    "LTCUSDT-020": (lambda: ContinuazioneVolume("long"), {
        "idea": "I-11", "fonte": FONTE_I11,
        "meccanismo": "continuazione dopo un balzo orario con volume alto (scambi informati); idea nata dallo studio del fallimento della 008, dichiarato",
        "parametri": {"finestra": 168, "soglia_sd": 2.5, "soglia_volume_mediana": 3.0, "tenuta_barre": 12,
                      "stop_atr": 2.0, "atr": 24, "stop_massimo": 0.06},
        "previsione": "profit factor fra 1,0 e 1,4; R medio fra 0 e +0,15; non batte nettamente la (b)"}),
    "LTCUSDT-021": (lambda: ContinuazioneVolume("short"), {
        "idea": "I-11", "fonte": FONTE_I11,
        "meccanismo": "continuazione dopo un crollo orario con volume alto (scambi informati); idea nata dallo studio dei fallimenti della 007, dichiarato",
        "parametri": {"finestra": 168, "soglia_sd": 2.5, "soglia_volume_mediana": 3.0, "tenuta_barre": 12,
                      "stop_atr": 2.0, "atr": 24, "stop_massimo": 0.06},
        "previsione": "profit factor fra 0,8 e 1,2; R medio fra -0,1 e +0,05; non batte nettamente la (b)"}),
    "LTCUSDT-022": (lambda: PremioMark("short"), {
        "idea": "I-12", "fonte": FONTE_I12,
        "meccanismo": "convergenza dell'ultimo prezzo verso il mark quando il premio e' anomalo verso l'alto",
        "parametri": {"finestra": 168, "soglia_sd": 3.0, "tenuta_barre": 4, "stop_atr": 2.0, "atr": 24, "stop_massimo": 0.06},
        "previsione": "profit factor fra 0,8 e 1,2; non batte nettamente la (b)"}),
    "LTCUSDT-023": (lambda: PremioMark("long"), {
        "idea": "I-12", "fonte": FONTE_I12,
        "meccanismo": "convergenza dell'ultimo prezzo verso il mark quando il premio e' anomalo verso il basso",
        "parametri": {"finestra": 168, "soglia_sd": 3.0, "tenuta_barre": 4, "stop_atr": 2.0, "atr": 24, "stop_massimo": 0.06},
        "previsione": "profit factor fra 0,8 e 1,2; non batte nettamente la (b)"}),
    "LTCUSDT-024": (lambda: IncrocioMedia("long"), {
        "idea": "I-13", "fonte": FONTE_I13,
        "meccanismo": "attraversamento verso l'alto della media a 50 barre oltre la banda dell'1%, tenuta fissa",
        "parametri": {"media": 50, "banda": 0.01, "tenuta_barre": 10, "stop": 0.06},
        "previsione": "profit factor fra 0,8 e 1,3; non batte nettamente la (b)"}),
    "LTCUSDT-025": (lambda: IncrocioMedia("short"), {
        "idea": "I-13", "fonte": FONTE_I13,
        "meccanismo": "attraversamento verso il basso della media a 50 barre oltre la banda dell'1%, tenuta fissa",
        "parametri": {"media": 50, "banda": 0.01, "tenuta_barre": 10, "stop": 0.06},
        "previsione": "profit factor fra 0,8 e 1,3; non batte nettamente la (b)"}),
    "LTCUSDT-026": (lambda: _stretto(RangeApertura("short")), {
        "idea": "I-07", "fonte": FONTE_I07, "famiglia": "LTCUSDT-014", "ritocco_di": "LTCUSDT-014",
        "meccanismo": "breakout al ribasso del range delle prime 4 ore UTC, solo nei giorni con range stretto",
        "parametri": {"range_ore": "00-03 UTC", "finestra_ingresso": "04-20 UTC", "uscita": "chiusura della barra delle 23",
                      "stop": "massimo del range, al massimo 6%",
                      "filtro": "altezza del range < mediana delle altezze dei 20 giorni precedenti"},
        "cosa_cambia": "aggiunge il filtro del range stretto alla 014",
        "perche": "Crabel lega i breakout migliori ai range d'apertura stretti (contrazione prima dell'espansione); lo studio dei fallimenti della 014 non mostra un fallimento sistematico (nota LTCUSDT-N011)",
        "previsione": "meno trade (circa la meta'), profit factor fra 0,8 e 1,3, R medio fra -0,1 e +0,1; non batte nettamente la (b)"}),
    "LTCUSDT-027": (lambda: _stop_fisso(RangeApertura("short"), 0.03), {
        "idea": "I-07", "fonte": FONTE_I07, "famiglia": "LTCUSDT-014", "ritocco_di": "LTCUSDT-014",
        "meccanismo": "breakout al ribasso del range delle prime 4 ore UTC con stop fisso al 3%",
        "parametri": {"range_ore": "00-03 UTC", "finestra_ingresso": "04-20 UTC", "uscita": "chiusura della barra delle 23",
                      "stop": 0.03},
        "cosa_cambia": "stop fisso al 3% sopra il close di segnale invece del massimo del range",
        "perche": "separare la direzione del breakout dal rumore della posizione dello stop (nota LTCUSDT-N012)",
        "previsione": "circa gli stessi 554 trade; profit factor fra 0,8 e 1,2; R medio fra -0,1 e +0,05; non batte nettamente la (b)"}),
    "LTCUSDT-018": (lambda: GiornoAnomalo("long", 1.5), {
        "idea": "I-10", "fonte": FONTE_I10,
        "meccanismo": "inerzia il giorno dopo un giorno anomalo al rialzo",
        "parametri": {"finestra": 30, "soglia_sd": 1.5, "tenuta_barre": 1, "stop": 0.06},
        "previsione": "profit factor fra 0,8 e 1,3; R medio fra -0,1 e +0,1; non batte nettamente la (b)"}),
    "LTCUSDT-018b": (lambda: GiornoAnomalo("long", 1.0), {
        "idea": "I-10", "fonte": FONTE_I10,
        "meccanismo": "inerzia il giorno dopo un giorno anomalo al rialzo; soglia allentata scritta prima di ogni test",
        "parametri": {"finestra": 30, "soglia_sd": 1.0, "tenuta_barre": 1, "stop": 0.06},
        "previsione": "profit factor fra 0,8 e 1,3; R medio fra -0,1 e +0,1; non batte nettamente la (b)"}),
    "LTCUSDT-019": (lambda: GiornoAnomalo("short", 1.5), {
        "idea": "I-10", "fonte": FONTE_I10,
        "meccanismo": "inerzia il giorno dopo un giorno anomalo al ribasso",
        "parametri": {"finestra": 30, "soglia_sd": 1.5, "tenuta_barre": 1, "stop": 0.06},
        "previsione": "profit factor fra 0,8 e 1,3; R medio fra -0,1 e +0,1; non batte nettamente la (b)"}),
    "LTCUSDT-019b": (lambda: GiornoAnomalo("short", 1.0), {
        "idea": "I-10", "fonte": FONTE_I10,
        "meccanismo": "inerzia il giorno dopo un giorno anomalo al ribasso; soglia allentata scritta prima di ogni test",
        "parametri": {"finestra": 30, "soglia_sd": 1.0, "tenuta_barre": 1, "stop": 0.06},
        "previsione": "profit factor fra 0,8 e 1,3; R medio fra -0,1 e +0,1; non batte nettamente la (b)"}),
}
