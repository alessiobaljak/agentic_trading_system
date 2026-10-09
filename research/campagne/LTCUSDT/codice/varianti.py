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
# Registro
# ---------------------------------------------------------------------------

FONTE_I01 = ("Yukun Liu, Aleh Tsyvinski, «Risks and Returns of Cryptocurrency», NBER Working Paper 24877, "
             "agosto 2018 (Review of Financial Studies 34(6), 2021); base: Moskowitz, Ooi, Pedersen, «Time Series "
             "Momentum», Journal of Financial Economics 104(2), 2012")
FONTE_I02 = "Curtis Faith, «Way of the Turtle», McGraw-Hill, 2007 (Sistema 1: breakout a 20, uscita a 10, stop 2 N)"
FONTE_I03 = "Larry Connors, Cesar Alvarez, «Short Term Trading Strategies That Work», TradingMarkets Publishing, 2008"
FONTE_I04 = ("John Y. Campbell, Sanford J. Grossman, Jiang Wang, «Trading Volume and Serial Correlation in Stock "
             "Returns», Quarterly Journal of Economics 108(4), novembre 1993")

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
}
