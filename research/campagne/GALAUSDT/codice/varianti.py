"""Le varianti della campagna GALAUSDT (regole complete, regola 6 del protocollo).

Ogni classe e' un'idea di ipotesi.md; ogni variante e' un'istanza con id, timeframe,
direzione e parametri scritti in ipotesi.md PRIMA del test. Gli array di ``prepara`` sono
causali (valore all'indice i calcolato con le barre 0..i). ``segnale`` calcola stop e target
SENZA la condizione d'ingresso (serve alle baseline (a) e (b)); ``condizione`` e' la
condizione d'ingresso dell'ipotesi; ``esci`` l'uscita a segnale o a tempo.

Stop: k ATR dal close della barra di segnale, al massimo il 6% del prezzo (``stop_massimo_bot``
di parametri.yaml: oltre, il bot non apre il trade). Target: multiplo della distanza dello stop.
"""

from __future__ import annotations

import math
from typing import Optional

import numpy as np
import pandas as pd

from research.src.motore import Segnale
from research.campagne.GALAUSDT.codice.comune import (Variante, atr, ema, rolling_max, rolling_min, rolling_std,
                                                      rsi, sma, valido)

STOP_MASSIMO = 0.06


def segnale_stop(direzione: str, close: float, distanza: float, k_target: Optional[float]) -> Optional[Segnale]:
    if not valido(close, distanza) or distanza <= 0 or close <= 0:
        return None
    d = min(distanza, STOP_MASSIMO * close)
    if direzione == "long":
        return Segnale("long", close - d, close + k_target * d if k_target else None)
    t = close - k_target * d if k_target else None
    if t is not None and t <= 0:
        return None
    return Segnale("short", close + d, t)


class ConStopATR(Variante):
    """Base: stop a k_stop ATR(n_atr), target opzionale a k_target R, uscita a tempo opzionale."""

    parametri_numerici = {"n_atr_barre": 14, "k_stop": 2.0, "k_target": 0.0, "uscita_tempo_barre": 0}

    def _base(self, df):
        return {"atr": atr(df, int(self.p["n_atr_barre"])), "close": df["close"].to_numpy()}

    def segnale(self, a, i, df):
        kt = self.p.get("k_target") or None
        return segnale_stop(self.direzione, a["close"][i], self.p["k_stop"] * a["atr"][i], kt)

    def esci_tempo(self, tenute):
        n = int(self.p.get("uscita_tempo_barre") or 0)
        return n > 0 and tenute >= n

    def esci(self, a, i, df, tenute, pos):
        return self.esci_tempo(tenute)


# ---------------------------------------------------------------------------
# Controllo positivo degli strumenti (lezioni/metodo.md): legge la barra DOPO
# ---------------------------------------------------------------------------


class ControlloLookahead(ConStopATR):
    parametri_numerici = {"n_atr_barre": 14, "k_stop": 2.0, "k_target": 0.0, "uscita_tempo_barre": 1}

    def prepara(self, df):
        a = self._base(df)
        c = df["close"].to_numpy()
        o = df["open"].to_numpy()
        futuro = np.full(len(c), np.nan)
        futuro[:-1] = c[1:] / o[1:] - 1  # rendimento della barra SUCCESSIVA: lookahead voluto
        a["futuro"] = futuro
        return a

    def condizione(self, a, i, df):
        f = a["futuro"][i]
        return valido(f) and (f > 0 if self.direzione == "long" else f < 0)


# ---------------------------------------------------------------------------
# I-01 Momentum di serie temporale: il rendimento delle ultime N barre cambia segno
# ---------------------------------------------------------------------------


class MomentumSerie(ConStopATR):
    parametri_numerici = {"lookback_barre": 42, "n_atr_barre": 14, "k_stop": 2.0, "k_target": 0.0,
                          "uscita_tempo_barre": 0}

    def prepara(self, df):
        a = self._base(df)
        n = int(self.p["lookback_barre"])
        a["r"] = (df["close"] / df["close"].shift(n) - 1).to_numpy()
        return a

    def condizione(self, a, i, df):
        if i < 1 or not valido(a["r"][i], a["r"][i - 1]):
            return False
        if self.direzione == "long":
            return a["r"][i] > 0 >= a["r"][i - 1]
        return a["r"][i] < 0 <= a["r"][i - 1]

    def esci(self, a, i, df, tenute, pos):
        r = a["r"][i]
        if not valido(r):
            return False
        return r <= 0 if self.direzione == "long" else r >= 0


# ---------------------------------------------------------------------------
# I-02 Rottura del canale di Donchian (regole delle tartarughe)
# ---------------------------------------------------------------------------


class Donchian(ConStopATR):
    parametri_numerici = {"entrata_barre": 20, "uscita_barre": 10, "n_atr_barre": 20, "k_stop": 2.0,
                          "k_target": 0.0, "uscita_tempo_barre": 0}

    def prepara(self, df):
        a = self._base(df)
        ne, nu = int(self.p["entrata_barre"]), int(self.p["uscita_barre"])
        a["max_e"] = rolling_max(df["high"], ne)
        a["min_e"] = rolling_min(df["low"], ne)
        a["max_u"] = rolling_max(df["high"], nu)
        a["min_u"] = rolling_min(df["low"], nu)
        return a

    def condizione(self, a, i, df):
        if i < 1:
            return False
        c = a["close"][i]
        if self.direzione == "long":
            m = a["max_e"][i - 1]  # massimo delle N barre PRIMA della barra corrente
            return valido(m) and c > m
        m = a["min_e"][i - 1]
        return valido(m) and c < m

    def esci(self, a, i, df, tenute, pos):
        if i < 1:
            return False
        c = a["close"][i]
        if self.direzione == "long":
            m = a["min_u"][i - 1]
            return valido(m) and c < m
        m = a["max_u"][i - 1]
        return valido(m) and c > m


# ---------------------------------------------------------------------------
# I-03 RSI a 2 periodi con filtro di tendenza (Connors e Alvarez)
# ---------------------------------------------------------------------------


class ConnorsRSI2(ConStopATR):
    parametri_numerici = {"rsi_barre": 2, "soglia": 10.0, "tendenza_barre": 200, "uscita_media_barre": 5,
                          "n_atr_barre": 14, "k_stop": 3.0, "k_target": 0.0, "uscita_tempo_barre": 0}

    def prepara(self, df):
        a = self._base(df)
        a["rsi"] = rsi(df["close"], int(self.p["rsi_barre"]))
        a["tend"] = sma(df["close"], int(self.p["tendenza_barre"]))
        a["usc"] = sma(df["close"], int(self.p["uscita_media_barre"]))
        return a

    def condizione(self, a, i, df):
        r, t, c = a["rsi"][i], a["tend"][i], a["close"][i]
        if not valido(r, t):
            return False
        if self.direzione == "long":
            return c > t and r < self.p["soglia"]
        return c < t and r > 100 - self.p["soglia"]

    def esci(self, a, i, df, tenute, pos):
        u, c = a["usc"][i], a["close"][i]
        if not valido(u):
            return False
        return c > u if self.direzione == "long" else c < u


# ---------------------------------------------------------------------------
# I-04 Falsa rottura: spazzata degli stop oltre il minimo/massimo recente e rientro
# ---------------------------------------------------------------------------


class FalsaRottura(Variante):
    parametri_numerici = {"finestra_barre": 48, "n_atr_barre": 24, "margine_stop_atr": 0.5, "k_target": 2.0,
                          "uscita_tempo_barre": 24}

    def prepara(self, df):
        n = int(self.p["finestra_barre"])
        return {"atr": atr(df, int(self.p["n_atr_barre"])), "close": df["close"].to_numpy(),
                "high": df["high"].to_numpy(), "low": df["low"].to_numpy(),
                "min_prec": rolling_min(df["low"], n), "max_prec": rolling_max(df["high"], n)}

    def segnale(self, a, i, df):
        # stop oltre l'estremo della barra di segnale, di un margine in ATR
        c, at = a["close"][i], a["atr"][i]
        if not valido(c, at):
            return None
        if self.direzione == "long":
            dist = c - (a["low"][i] - self.p["margine_stop_atr"] * at)
        else:
            dist = (a["high"][i] + self.p["margine_stop_atr"] * at) - c
        return segnale_stop(self.direzione, c, dist, self.p["k_target"])

    def condizione(self, a, i, df):
        if i < 1:
            return False
        c = a["close"][i]
        if self.direzione == "long":
            m = a["min_prec"][i - 1]
            return valido(m) and a["low"][i] < m and c > m
        m = a["max_prec"][i - 1]
        return valido(m) and a["high"][i] > m and c < m

    def esci(self, a, i, df, tenute, pos):
        n = int(self.p["uscita_tempo_barre"])
        return n > 0 and tenute >= n


# ---------------------------------------------------------------------------
# I-05 Funding estremo: posizionamento affollato a leva
# ---------------------------------------------------------------------------


class FundingEstremo(ConStopATR):
    parametri_numerici = {"finestra_barre": 90, "quantile": 0.85, "n_atr_barre": 14, "k_stop": 2.0,
                          "k_target": 0.0, "uscita_tempo_barre": 3}

    def prepara(self, df):
        a = self._base(df)
        f = df["funding_ultimo"]
        n = int(self.p["finestra_barre"])
        q = float(self.p["quantile"])
        a["f"] = f.to_numpy()
        # quantile delle N barre PRECEDENTI (la barra corrente esclusa)
        a["alto"] = f.shift(1).rolling(n, min_periods=n).quantile(q).to_numpy()
        a["basso"] = f.shift(1).rolling(n, min_periods=n).quantile(1 - q).to_numpy()
        return a

    def condizione(self, a, i, df):
        f = a["f"][i]
        if self.direzione == "short":
            return valido(f, a["alto"][i]) and f > a["alto"][i] and f > 0
        return valido(f, a["basso"][i]) and f < a["basso"][i] and f < 0


# ---------------------------------------------------------------------------
# I-06 Ritardo rispetto a BTC (le monete piccole seguono le grandi in ritardo)
# ---------------------------------------------------------------------------


class RitardoBTC(ConStopATR):
    parametri_numerici = {"finestra_barre": 168, "k_sigma": 2.0, "n_atr_barre": 24, "k_stop": 2.0,
                          "k_target": 0.0, "uscita_tempo_barre": 3}

    def prepara(self, df):
        a = self._base(df)
        rb = df["btc_close"] / df["btc_close"].shift(1) - 1
        rg = df["close"] / df["close"].shift(1) - 1
        a["rb"] = rb.to_numpy()
        a["rg"] = rg.to_numpy()
        a["sb"] = rb.shift(1).rolling(int(self.p["finestra_barre"]), min_periods=int(self.p["finestra_barre"]) // 2).std().to_numpy()
        return a

    def condizione(self, a, i, df):
        rb, rg, sb = a["rb"][i], a["rg"][i], a["sb"][i]
        if not valido(rb, rg, sb) or sb <= 0:
            return False
        minimo = float(self.p.get("atr_min_rel", 0.0) or 0.0)
        if minimo > 0 and not (valido(a["atr"][i]) and a["atr"][i] / a["close"][i] > minimo):
            return False  # filtro del ritocco: volatilita' relativa sotto la soglia
        k = self.p["k_sigma"]
        if self.direzione == "long":
            return rb > k * sb and rg < rb
        return rb < -k * sb and rg > rb


# ---------------------------------------------------------------------------
# I-07 Barra piu' stretta delle ultime 7 (NR7) e rottura
# ---------------------------------------------------------------------------


class NR7(Variante):
    parametri_numerici = {"strette_barre": 7, "n_atr_barre": 14, "k_target": 2.0, "uscita_tempo_barre": 12}

    def prepara(self, df):
        rng = df["high"] - df["low"]
        n = int(self.p["strette_barre"])
        return {"atr": atr(df, int(self.p["n_atr_barre"])), "close": df["close"].to_numpy(),
                "high": df["high"].to_numpy(), "low": df["low"].to_numpy(),
                "nr": (rng <= rng.rolling(n, min_periods=n).min()).to_numpy()}

    def segnale(self, a, i, df):
        # stop all'estremo opposto della barra stretta precedente; senza barra precedente, nessun segnale
        if i < 1:
            return None
        c = a["close"][i]
        if self.direzione == "long":
            dist = c - a["low"][i - 1]
        else:
            dist = a["high"][i - 1] - c
        if not valido(dist) or dist <= 0:
            return None
        return segnale_stop(self.direzione, c, dist, self.p["k_target"])

    def condizione(self, a, i, df):
        if i < 1 or not a["nr"][i - 1]:
            return False
        if self.direzione == "long":
            return a["close"][i] > a["high"][i - 1]
        return a["close"][i] < a["low"][i - 1]

    def esci(self, a, i, df, tenute, pos):
        n = int(self.p["uscita_tempo_barre"])
        return n > 0 and tenute >= n


# ---------------------------------------------------------------------------
# I-08 Movimento grande con volume alto: continuazione
# ---------------------------------------------------------------------------


class VolumeContinuazione(ConStopATR):
    parametri_numerici = {"finestra_barre": 168, "k_sigma": 2.0, "k_volume": 2.0, "n_atr_barre": 24,
                          "k_stop": 2.0, "k_target": 0.0, "uscita_tempo_barre": 6}

    def prepara(self, df):
        a = self._base(df)
        n = int(self.p["finestra_barre"])
        r = df["close"] / df["close"].shift(1) - 1
        a["r"] = r.to_numpy()
        a["s"] = r.shift(1).rolling(n, min_periods=n).std().to_numpy()
        a["v"] = df["quote_volume"].to_numpy()
        a["vm"] = df["quote_volume"].shift(1).rolling(n, min_periods=n).mean().to_numpy()
        return a

    def condizione(self, a, i, df):
        r, s, v, vm = a["r"][i], a["s"][i], a["v"][i], a["vm"][i]
        if not valido(r, s, v, vm) or s <= 0:
            return False
        if v <= self.p["k_volume"] * vm:
            return False
        k = self.p["k_sigma"]
        return r > k * s if self.direzione == "long" else r < -k * s


# ---------------------------------------------------------------------------
# I-09 Rottura di volatilita' dall'apertura del giorno (Larry Williams)
# ---------------------------------------------------------------------------


class RotturaWilliams(Variante):
    parametri_numerici = {"k_range": 0.5}

    def prepara(self, df):
        g = df["giorno"]
        apertura = df.groupby(g)["open"].transform("first")
        hi_g = df.groupby(g)["high"].max()
        lo_g = df.groupby(g)["low"].min()
        n_g = df.groupby(g)["high"].size()
        rng = (hi_g - lo_g).where(n_g == 24)  # solo giorni completi a 1h
        rng_prec = g.map(rng.shift(1).where(rng.index.to_series().diff() == 1))
        a = {"close": df["close"].to_numpy(), "ap": apertura.to_numpy(), "rp": rng_prec.to_numpy(),
             "ora": df["ora"].to_numpy(), "giorno": g.to_numpy()}
        # prima apertura della barra 00:00 del giorno: senza la barra delle 00, apertura non valida
        prima_ora = df.groupby(g)["ora"].transform("first").to_numpy()
        a["ap"] = np.where(prima_ora == 0, a["ap"], np.nan)
        # gia' scattato oggi? (contatore causale: scatti fino alla barra precedente)
        return a

    def segnale(self, a, i, df):
        ap, rp, c = a["ap"][i], a["rp"][i], a["close"][i]
        if not valido(ap, rp, c) or rp <= 0 or a["ora"][i] >= 23:
            return None
        # stop a k x range del giorno prima dal close (al primo attraversamento e' circa l'apertura del giorno)
        return segnale_stop(self.direzione, c, self.p["k_range"] * rp, None)

    def condizione(self, a, i, df):
        ap, rp, c = a["ap"][i], a["rp"][i], a["close"][i]
        if not valido(ap, rp) or a["ora"][i] >= 23:
            return False
        livello = ap + self.p["k_range"] * rp if self.direzione == "long" else ap - self.p["k_range"] * rp
        sopra = c > livello if self.direzione == "long" else c < livello
        if not sopra:
            return False
        # solo il primo attraversamento del giorno: la barra precedente dello stesso giorno era sotto
        if i >= 1 and a["giorno"][i - 1] == a["giorno"][i]:
            cp = a["close"][i - 1]
            prima = cp > livello if self.direzione == "long" else cp < livello
            return not prima
        return True

    def esci(self, a, i, df, tenute, pos):
        return a["ora"][i] == 23  # chiusura all'apertura delle 00:00, fine del giorno UTC


# ---------------------------------------------------------------------------
# I-10 Effetto del lunedi'
# ---------------------------------------------------------------------------


class Lunedi(ConStopATR):
    parametri_numerici = {"n_atr_barre": 14, "k_stop": 2.0, "k_target": 0.0, "uscita_tempo_barre": 1}

    def prepara(self, df):
        a = self._base(df)
        a["gs"] = df["giorno_settimana"].to_numpy()
        return a

    def condizione(self, a, i, df):
        return a["gs"][i] == 6  # barra della domenica chiusa: ingresso all'apertura del lunedi'


# ---------------------------------------------------------------------------
# I-11 Valore relativo rispetto a BTC: lo scarto si richiude
# ---------------------------------------------------------------------------


class ValoreRelativo(ConStopATR):
    parametri_numerici = {"finestra_barre": 42, "z_ingresso": 2.0, "n_atr_barre": 14, "k_stop": 2.0,
                          "k_target": 0.0, "uscita_tempo_barre": 18}

    def prepara(self, df):
        a = self._base(df)
        s = np.log(df["close"]) - np.log(df["btc_close"])
        n = int(self.p["finestra_barre"])
        m = s.rolling(n, min_periods=n).mean()
        sd = s.rolling(n, min_periods=n).std(ddof=0)
        a["z"] = ((s - m) / sd).to_numpy()
        return a

    def condizione(self, a, i, df):
        z = a["z"][i]
        if not valido(z):
            return False
        return z < -self.p["z_ingresso"] if self.direzione == "long" else z > self.p["z_ingresso"]

    def esci(self, a, i, df, tenute, pos):
        if self.esci_tempo(tenute):
            return True
        z = a["z"][i]
        if not valido(z):
            return False
        return z >= 0 if self.direzione == "long" else z <= 0


# ---------------------------------------------------------------------------
# I-12 Reazione eccessiva giornaliera: il giorno dopo continua
# ---------------------------------------------------------------------------


class GiornoAnomalo(ConStopATR):
    parametri_numerici = {"finestra_barre": 30, "k_sigma": 2.0, "n_atr_barre": 14, "k_stop": 2.0,
                          "k_target": 0.0, "uscita_tempo_barre": 1}

    def prepara(self, df):
        a = self._base(df)
        n = int(self.p["finestra_barre"])
        r = df["close"] / df["open"] - 1
        a["r"] = r.to_numpy()
        a["m"] = r.shift(1).rolling(n, min_periods=n).mean().to_numpy()
        a["s"] = r.shift(1).rolling(n, min_periods=n).std().to_numpy()
        return a

    def condizione(self, a, i, df):
        r, m, s = a["r"][i], a["m"][i], a["s"][i]
        if not valido(r, m, s) or s <= 0:
            return False
        k = self.p["k_sigma"]
        return r > m + k * s if self.direzione == "long" else r < m - k * s


# ---------------------------------------------------------------------------
# I-13 Pompa e scarico: dopo un'impennata con volume enorme il prezzo ricade
# ---------------------------------------------------------------------------


class PompaScarico(ConStopATR):
    parametri_numerici = {"finestra_barre": 168, "k_sigma": 3.0, "k_volume": 3.0, "n_atr_barre": 24,
                          "k_stop": 2.0, "k_target": 0.0, "uscita_tempo_barre": 24}

    def prepara(self, df):
        return VolumeContinuazione.prepara(self, df)

    def condizione(self, a, i, df):
        r, s, v, vm = a["r"][i], a["s"][i], a["v"][i], a["vm"][i]
        if not valido(r, s, v, vm) or s <= 0:
            return False
        return v > self.p["k_volume"] * vm and r > self.p["k_sigma"] * s


# ---------------------------------------------------------------------------
# I-14 Periodicita' oraria (Heston, Korajczyk, Sadka)
# ---------------------------------------------------------------------------


class PeriodicitaOraria(ConStopATR):
    parametri_numerici = {"giorni": 20, "z_ingresso": 1.5, "n_atr_barre": 24, "k_stop": 2.0, "k_target": 0.0,
                          "uscita_tempo_barre": 1}

    def prepara(self, df):
        a = self._base(df)
        n = len(df)
        g = int(self.p["giorni"])
        r = df["close"] / df["open"] - 1
        ora = df["ora"].to_numpy()
        # z dell'ora h aggiornato all'ultima barra di quell'ora (compresa), poi portato in avanti
        z_per_ora = np.full((24, n), np.nan)
        for h in range(24):
            idx = np.where(ora == h)[0]
            if len(idx) == 0:
                continue
            rh = r.iloc[idx]
            m = rh.rolling(g, min_periods=g).mean()
            s = rh.rolling(g, min_periods=g).std()
            z = (m / (s / np.sqrt(g))).to_numpy()
            col = pd.Series(np.nan, index=range(n))
            col.iloc[idx] = z
            z_per_ora[h] = col.ffill().to_numpy()
        a["z_per_ora"] = z_per_ora
        a["ora"] = ora
        return a

    def condizione(self, a, i, df):
        prossima = (int(a["ora"][i]) + 1) % 24
        z = a["z_per_ora"][prossima][i]
        if not valido(z):
            return False
        return z > self.p["z_ingresso"] if self.direzione == "long" else z < -self.p["z_ingresso"]


# ---------------------------------------------------------------------------
# I-15 Scarto fra last e mark
# ---------------------------------------------------------------------------


class ScartoMark(ConStopATR):
    parametri_numerici = {"finestra_barre": 168, "z_ingresso": 2.0, "n_atr_barre": 24, "k_stop": 2.0,
                          "k_target": 0.0, "uscita_tempo_barre": 2}

    def prepara(self, df):
        a = self._base(df)
        n = int(self.p["finestra_barre"])
        b = (df["close"] - df["mark_close"]) / df["mark_close"]
        m = b.shift(1).rolling(n, min_periods=n).mean()
        s = b.shift(1).rolling(n, min_periods=n).std()
        a["z"] = ((b - m) / s).to_numpy()
        return a

    def condizione(self, a, i, df):
        z = a["z"][i]
        if not valido(z):
            return False
        return z < -self.p["z_ingresso"] if self.direzione == "long" else z > self.p["z_ingresso"]


# ---------------------------------------------------------------------------
# I-16 Numeri tondi (Osler 2003)
# ---------------------------------------------------------------------------


class NumeriTondi(Variante):
    parametri_numerici = {"n_atr_barre": 24, "margine_stop_atr": 0.5, "k_target": 2.0, "uscita_tempo_barre": 24}

    def prepara(self, df):
        c = df["close"].to_numpy()
        cp = np.concatenate([[np.nan], c[:-1]])
        with np.errstate(invalid="ignore", divide="ignore"):
            u = np.power(10.0, np.floor(np.log10(cp))) / 2
            sopra = np.ceil(cp / u * (1 + 1e-12)) * u  # primo multiplo strettamente sopra
            sotto = np.floor(cp / u * (1 - 1e-12)) * u  # primo multiplo strettamente sotto
        return {"atr": atr(df, int(self.p["n_atr_barre"])), "close": c, "high": df["high"].to_numpy(),
                "low": df["low"].to_numpy(), "sopra": sopra, "sotto": sotto}

    def segnale(self, a, i, df):
        c, at = a["close"][i], a["atr"][i]
        if self.direzione == "short":
            livello = a["sopra"][i]
            if not valido(c, at, livello):
                return None
            dist = max(livello - c, 0.0) + self.p["margine_stop_atr"] * at
        else:
            livello = a["sotto"][i]
            if not valido(c, at, livello):
                return None
            dist = max(c - livello, 0.0) + self.p["margine_stop_atr"] * at
        return segnale_stop(self.direzione, c, dist, self.p["k_target"])

    def condizione(self, a, i, df):
        c = a["close"][i]
        if self.direzione == "short":
            livello = a["sopra"][i]
            return valido(livello) and a["high"][i] >= livello and c < livello
        livello = a["sotto"][i]
        return valido(livello) and a["low"][i] <= livello and c > livello

    def esci(self, a, i, df, tenute, pos):
        n = int(self.p["uscita_tempo_barre"])
        return n > 0 and tenute >= n


# ---------------------------------------------------------------------------
# I-17 Momentum dentro la giornata (Gao, Han, Li, Zhou)
# ---------------------------------------------------------------------------


class MomentumGiornata(ConStopATR):
    parametri_numerici = {"n_atr_barre": 48, "k_stop": 2.0, "k_target": 0.0, "uscita_tempo_barre": 1}

    def prepara(self, df):
        a = self._base(df)
        prima = (df["ora"] == 0) & (df["minuto"] == 0)
        r = (df["close"] / df["open"] - 1).where(prima)
        a["r_prima"] = r.groupby(df["giorno"]).transform("max").to_numpy()  # una sola barra per giorno
        a["ultima"] = ((df["ora"] == 23) & (df["minuto"] == 0)).to_numpy()
        return a

    def condizione(self, a, i, df):
        if not a["ultima"][i]:
            return False
        r = a["r_prima"][i]
        if not valido(r):
            return False
        return r > 0 if self.direzione == "long" else r < 0
