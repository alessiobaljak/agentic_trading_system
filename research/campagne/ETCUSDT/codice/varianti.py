"""Le varianti della campagna ETCUSDT, scritte come in ipotesi.md (Fase 1), prima dei test.

Ogni voce di CATALOGO e' una funzione senza argomenti che restituisce (Variante, meta): meta va nella
registrazione del log. Il controllo positivo (CONTROLLO) legge di proposito la barra dopo.
"""
from __future__ import annotations

import bisect
import math
from datetime import datetime, timezone
from typing import Dict, Optional

import numpy as np

import comune as C
from comune import Variante


def _nan(x) -> bool:
    return x is None or (isinstance(x, float) and math.isnan(x))


def _riscaldamento(*liste) -> int:
    """Prima barra da cui TUTTI gli indicatori sono definiti."""
    n = len(liste[0])
    for i in range(n):
        if all(not _nan(l[i]) for l in liste):
            return i
    return n


def _base(serie: C.Serie, n_atr: int = 14) -> dict:
    c = C.arr(serie.candele, "close")
    h = C.arr(serie.candele, "high")
    l = C.arr(serie.candele, "low")
    o = C.arr(serie.candele, "open")
    return {"c_np": c, "h_np": h, "l_np": l, "o_np": o, "c": c.tolist(), "atr": C.a_lista(C.atr(h, l, c, n_atr))}


def _stop(k: float, direzione: str):
    if direzione == "long":
        def segnale(ind, i):
            a = ind["atr"][i]
            return None if a is None else (ind["c"][i] - k * a, None)
    else:
        def segnale(ind, i):
            a = ind["atr"][i]
            return None if a is None else (ind["c"][i] + k * a, None)
    return segnale


def _rendimenti_1(c: np.ndarray) -> np.ndarray:
    r = np.full(len(c), np.nan)
    r[1:] = c[1:] / c[:-1] - 1
    return r


def _std_precedente(x: np.ndarray, n: int, ddof: int = 1) -> np.ndarray:
    """Deviazione standard delle n osservazioni PRIMA di i (i escluso)."""
    out = np.full(len(x), np.nan)
    for i in range(n, len(x)):
        w = x[i - n:i]
        if not np.isnan(w).any():
            out[i] = np.std(w, ddof=ddof)
    return out


def _media_precedente(x: np.ndarray, n: int) -> np.ndarray:
    out = np.full(len(x), np.nan)
    for i in range(n, len(x)):
        w = x[i - n:i]
        if not np.isnan(w).any():
            out[i] = np.mean(w)
    return out


def _percentile_precedente(x: np.ndarray, n: int, q: float) -> np.ndarray:
    out = np.full(len(x), np.nan)
    for i in range(n, len(x)):
        w = x[i - n:i]
        if not np.isnan(w).any():
            out[i] = np.percentile(w, q, method="linear")
    return out


def _meta(idea, nome, fonte, meccanismo, parametri, previsione, criterio=None):
    return {
        "idea": idea,
        "nome": nome,
        "fonte": fonte,
        "meccanismo": meccanismo,
        "parametri": parametri,
        "previsione": previsione,
        "criterio_successo": criterio or ("batte nettamente la (a) e la (b) (contro_baseline, sezione 8) con R medio dopo i "
                                          "costi positivo: diventa candidato"),
    }


# ---------------------------------------------------------------------------
# I-01 momento a 7 giorni (4h)
# ---------------------------------------------------------------------------
F01 = ("T. J. Moskowitz, Y. H. Ooi, L. H. Pedersen, 'Time Series Momentum', Journal of Financial Economics 104(2), 2012; "
       "Y. Liu, A. Tsyvinski, 'Risks and Returns of Cryptocurrency', NBER Working Paper 24877, agosto 2018")


def _i01(direzione):
    def prepara(serie):
        ind = _base(serie)
        ind["r42"] = C.a_lista(C.rendimento(ind["c_np"], 42))
        ind["riscaldamento"] = _riscaldamento(ind["r42"], ind["atr"])
        return ind

    if direzione == "long":
        ingresso = lambda ind, i: ind["r42"][i] > 0
    else:
        ingresso = lambda ind, i: ind["r42"][i] < 0
    nome = "I-01-L" if direzione == "long" else "I-01-S"
    var = Variante(nome, "4h", direzione, prepara, ingresso, _stop(2.0, direzione), max_barre=42)
    meta = _meta("I-01", nome, F01, "momento della serie storica a una settimana (sottoreazione, inseguimento)",
                 {"rendimento_barre": 42, "soglia": 0, "stop_atr": 2.0, "atr_barre": 14, "uscita_barre": 42, "target": None},
                 "R medio fra -0,05 e +0,10 (long) / fra -0,10 e +0,05 (short); non netto contro la (b)")
    return var, meta


# ---------------------------------------------------------------------------
# I-02 rottura del canale di 50 barre (4h)
# ---------------------------------------------------------------------------
F02 = ("W. Brock, J. Lakonishok, B. LeBaron, 'Simple Technical Trading Rules and the Stochastic Properties of Stock Returns', "
       "Journal of Finance 47(5), 1992")


def _i02(direzione):
    def prepara(serie):
        ind = _base(serie)
        ind["max50"] = C.a_lista(C.massimo_precedente(ind["h_np"], 50))
        ind["min50"] = C.a_lista(C.minimo_precedente(ind["l_np"], 50))
        ind["riscaldamento"] = _riscaldamento(ind["max50"], ind["atr"])
        return ind

    if direzione == "long":
        ingresso = lambda ind, i: ind["c"][i] > ind["max50"][i]
    else:
        ingresso = lambda ind, i: ind["c"][i] < ind["min50"][i]
    nome = "I-02-L" if direzione == "long" else "I-02-S"
    var = Variante(nome, "4h", direzione, prepara, ingresso, _stop(2.0, direzione), max_barre=60)
    meta = _meta("I-02", nome, F02, "rottura del massimo/minimo del canale (stop degli avversari, ancoraggio, seguaci del trend)",
                 {"canale_barre": 50, "stop_atr": 2.0, "atr_barre": 14, "uscita_barre": 60, "target": None},
                 "R medio fra -0,10 e +0,10; non netto")
    return var, meta


# ---------------------------------------------------------------------------
# I-03 inversione dopo shock orario (1h)
# ---------------------------------------------------------------------------
F03 = ("S. Nagel, 'Evaporating Liquidity', Review of Financial Studies 25(7), 2012; N. Jegadeesh, 'Evidence of Predictable "
       "Behavior of Security Returns', Journal of Finance 45(3), 1990")


def _i03(direzione):
    def prepara(serie):
        ind = _base(serie)
        r = _rendimenti_1(ind["c_np"])
        s = _std_precedente(r, 168)
        ind["r"] = C.a_lista(r)
        ind["s"] = C.a_lista(s)
        ind["riscaldamento"] = _riscaldamento(ind["r"], ind["s"], ind["atr"])
        return ind

    if direzione == "long":
        ingresso = lambda ind, i: ind["r"][i] < -3.0 * ind["s"][i]
    else:
        ingresso = lambda ind, i: ind["r"][i] > 3.0 * ind["s"][i]
    nome = "I-03-L" if direzione == "long" else "I-03-S"
    var = Variante(nome, "1h", direzione, prepara, ingresso, _stop(2.0, direzione), max_barre=12)
    meta = _meta("I-03", nome, F03, "inversione dopo uno shock orario: compenso di chi fornisce liquidita' a vendite/acquisti forzati",
                 {"soglia_deviazioni": 3.0, "finestra_deviazione_barre": 168, "stop_atr": 2.0, "atr_barre": 14,
                  "uscita_barre": 12, "target": None},
                 "long: R medio fra -0,10 e +0,10; short: fra -0,15 e +0,05; non netto")
    return var, meta


# ---------------------------------------------------------------------------
# I-04 continuazione dopo giornata anomala (1d)
# ---------------------------------------------------------------------------
F04 = "G. M. Caporale, A. Plastun, 'Price overreactions in the cryptocurrency market', Journal of Economic Studies 46(5), 2019"


def _i04(direzione):
    def prepara(serie):
        ind = _base(serie)
        r = _rendimenti_1(ind["c_np"])
        ind["r"] = C.a_lista(r)
        ind["m"] = C.a_lista(_media_precedente(r, 30))
        ind["s"] = C.a_lista(_std_precedente(r, 30))
        ind["riscaldamento"] = _riscaldamento(ind["r"], ind["m"], ind["s"], ind["atr"])
        return ind

    if direzione == "long":
        ingresso = lambda ind, i: ind["r"][i] > ind["m"][i] + ind["s"][i]
    else:
        ingresso = lambda ind, i: ind["r"][i] < ind["m"][i] - ind["s"][i]
    nome = "I-04-L" if direzione == "long" else "I-04-S"
    var = Variante(nome, "1d", direzione, prepara, ingresso, _stop(1.0, direzione), max_barre=1)
    meta = _meta("I-04", nome, F04, "continuazione il giorno dopo una giornata di reazione eccessiva",
                 {"soglia_deviazioni": 1.0, "finestra_giorni": 30, "stop_atr": 1.0, "atr_barre": 14, "uscita_barre": 1,
                  "target": None},
                 "R medio fra -0,10 e +0,10; non netto")
    return var, meta


# ---------------------------------------------------------------------------
# I-05 funding affollato (8h)
# ---------------------------------------------------------------------------
F05 = "S. He, A. Manela, O. Ross, V. von Wachter, 'Fundamentals of Perpetual Futures', arXiv 2212.06888, dicembre 2022"


def _i05(direzione):
    def prepara(serie):
        ind = _base(serie)
        f = sorted(serie.funding)
        ts_f = [t for t, _ in f]
        tassi = np.array([r for _, r in f], dtype=float)
        p90 = _percentile_precedente(tassi, 90, 90)
        p10 = _percentile_precedente(tassi, 90, 10)
        ultimo, q90, q10 = [], [], []
        for cnd in serie.candele:
            k = bisect.bisect_right(ts_f, cnd.close_ts) - 1  # ultimo settlement regolato entro la chiusura
            if k < 0:
                ultimo.append(None); q90.append(None); q10.append(None)
            else:
                ultimo.append(float(tassi[k]))
                q90.append(None if math.isnan(p90[k]) else float(p90[k]))
                q10.append(None if math.isnan(p10[k]) else float(p10[k]))
        ind["f"], ind["q90"], ind["q10"] = ultimo, q90, q10
        ind["riscaldamento"] = _riscaldamento(ind["f"], ind["q90"], ind["atr"])
        return ind

    if direzione == "short":
        ingresso = lambda ind, i: ind["f"][i] > 0.0001 and ind["f"][i] >= ind["q90"][i]
    else:
        ingresso = lambda ind, i: ind["f"][i] < 0 and ind["f"][i] <= ind["q10"][i]
    nome = "I-05-S" if direzione == "short" else "I-05-L"
    var = Variante(nome, "8h", direzione, prepara, ingresso, _stop(2.0, direzione), max_barre=9)
    meta = _meta("I-05", nome, F05, "funding estremo = leva affollata da una parte; il premio torna verso zero",
                 {"funding_finestra_settlement": 90, "percentile": 90 if direzione == "short" else 10,
                  "soglia_assoluta": 0.0001 if direzione == "short" else 0.0, "stop_atr": 2.0, "atr_barre": 14,
                  "uscita_barre": 9, "target": None},
                 "R medio fra -0,10 e +0,10; il long probabilmente sotto i trade minimi")
    return var, meta


# ---------------------------------------------------------------------------
# I-06 premio del volume alto (4h)
# ---------------------------------------------------------------------------
F06 = "S. Gervais, R. Kaniel, D. H. Mingelgrin, 'The High-Volume Return Premium', Journal of Finance 56(3), 2001"


def _i06(direzione):
    def prepara(serie):
        ind = _base(serie)
        v = np.array([np.nan if serie.volume_usdt.get(c.ts) is None else serie.volume_usdt[c.ts] for c in serie.candele])
        v24 = np.full(len(v), np.nan)
        for i in range(5, len(v)):
            v24[i] = np.sum(v[i - 5:i + 1])
        ind["v24"] = C.a_lista(v24)
        ind["q"] = C.a_lista(_percentile_precedente(v24, 300, 90 if direzione == "long" else 10))
        ind["riscaldamento"] = _riscaldamento(ind["v24"], ind["q"], ind["atr"])
        return ind

    if direzione == "long":
        ingresso = lambda ind, i: ind["v24"][i] is not None and ind["q"][i] is not None and ind["v24"][i] >= ind["q"][i]
    else:
        ingresso = lambda ind, i: ind["v24"][i] is not None and ind["q"][i] is not None and ind["v24"][i] <= ind["q"][i]
    nome = "I-06-L" if direzione == "long" else "I-06-S"
    var = Variante(nome, "4h", direzione, prepara, ingresso, _stop(2.0, direzione), max_barre=30)
    meta = _meta("I-06", nome, F06, "volume anomalo alto (basso) attira (perde) attenzione e compratori nei giorni dopo",
                 {"volume_barre": 6, "finestra_percentile_barre": 300, "percentile": 90 if direzione == "long" else 10,
                  "stop_atr": 2.0, "atr_barre": 14, "uscita_barre": 30, "target": None},
                 "R medio fra -0,10 e +0,10; non netto")
    return var, meta


# ---------------------------------------------------------------------------
# I-07 squilibrio dei taker (1h)
# ---------------------------------------------------------------------------
F07 = ("T. Chordia, A. Subrahmanyam, 'Order imbalance and individual stock returns: Theory and evidence', Journal of "
       "Financial Economics 72(3), 2004")


def _i07(direzione):
    def prepara(serie):
        ind = _base(serie)
        tbq = C.colonne_klines(serie.tf, serie.periodo, 10)  # taker_buy_quote_volume
        imb = np.full(serie.n, np.nan)
        for i, c in enumerate(serie.candele):
            qv = serie.volume_usdt.get(c.ts)
            b = tbq.get(c.ts)
            if qv is not None and b is not None and qv > 0:
                imb[i] = (2 * b - qv) / qv
        ind["imb"] = C.a_lista(imb)
        ind["q"] = C.a_lista(_percentile_precedente(imb, 168, 95 if direzione == "long" else 5))
        ind["riscaldamento"] = _riscaldamento(ind["imb"], ind["q"], ind["atr"])
        return ind

    if direzione == "long":
        ingresso = lambda ind, i: ind["imb"][i] is not None and ind["q"][i] is not None and ind["imb"][i] >= ind["q"][i]
    else:
        ingresso = lambda ind, i: ind["imb"][i] is not None and ind["q"][i] is not None and ind["imb"][i] <= ind["q"][i]
    nome = "I-07-L" if direzione == "long" else "I-07-S"
    var = Variante(nome, "1h", direzione, prepara, ingresso, _stop(2.0, direzione), max_barre=6)
    meta = _meta("I-07", nome, F07, "lo squilibrio degli ordini aggressivi persiste (ordini spezzati) e porta il prezzo",
                 {"finestra_percentile_barre": 168, "percentile": 95 if direzione == "long" else 5, "stop_atr": 2.0,
                  "atr_barre": 14, "uscita_barre": 6, "target": None},
                 "R medio fra -0,15 e +0,05; non netto")
    return var, meta


# ---------------------------------------------------------------------------
# I-08 lunedi' (1d)
# ---------------------------------------------------------------------------
F08 = "G. M. Caporale, A. Plastun, 'The day of the week effect in the cryptocurrency market', Finance Research Letters 31, 2019"


def _i08():
    def prepara(serie):
        ind = _base(serie)
        ind["domenica"] = [datetime.fromtimestamp(c.ts / 1000, tz=timezone.utc).weekday() == 6 for c in serie.candele]
        ind["riscaldamento"] = _riscaldamento(ind["atr"])
        return ind

    ingresso = lambda ind, i: ind["domenica"][i]
    var = Variante("I-08-L", "1d", "long", prepara, ingresso, _stop(1.0, "long"), max_barre=1)
    meta = _meta("I-08", "I-08-L", F08, "rendimenti anomali positivi il lunedi' (flussi alla riapertura dei mercati tradizionali)",
                 {"giorno": "lunedi' (segnale alla chiusura della domenica UTC)", "stop_atr": 1.0, "atr_barre": 14,
                  "uscita_barre": 1, "target": None},
                 "R medio fra -0,10 e +0,05; non netto")
    return var, meta


# ---------------------------------------------------------------------------
# I-09 BTC guida (1h)
# ---------------------------------------------------------------------------
F09 = ("K. Hou, 'Industry Information Diffusion and the Lead-lag Effect in Stock Returns', Review of Financial Studies 20(4), "
       "2007; D. Koutmos, 'Return and volatility spillovers among cryptocurrencies', Economics Letters 173, 2018")


def _i09(direzione):
    def prepara(serie):
        ind = _base(serie)
        btc = C.btc_allineato(serie)
        cb = np.array([np.nan if b is None else b.close for b in btc])
        rb = np.full(serie.n, np.nan)
        re = np.full(serie.n, np.nan)
        ms = C.MS[serie.tf]
        for i in range(1, serie.n):
            if serie.candele[i].ts - serie.candele[i - 1].ts == ms:  # barre contigue
                re[i] = serie.candele[i].close / serie.candele[i - 1].close - 1
                if not (math.isnan(cb[i]) or math.isnan(cb[i - 1])):
                    rb[i] = cb[i] / cb[i - 1] - 1
        sb = np.full(serie.n, np.nan)
        for i in range(168, serie.n):
            w = rb[i - 168:i]
            w = w[~np.isnan(w)]
            if len(w) >= 120:
                sb[i] = np.std(w, ddof=1)
        ind["rb"], ind["re"], ind["sb"] = C.a_lista(rb), C.a_lista(re), C.a_lista(sb)
        ind["riscaldamento"] = _riscaldamento(ind["sb"], ind["atr"])
        return ind

    def ingresso(ind, i):
        rb, re, sb = ind["rb"][i], ind["re"][i], ind["sb"][i]
        if rb is None or re is None or sb is None:
            return False
        if direzione == "long":
            return rb > 2.0 * sb and re < 0.5 * rb
        return rb < -2.0 * sb and re > 0.5 * rb

    nome = "I-09-L" if direzione == "long" else "I-09-S"
    var = Variante(nome, "1h", direzione, prepara, ingresso, _stop(2.0, direzione), max_barre=4)
    meta = _meta("I-09", nome, F09, "BTC guida, ETC segue in ritardo (diffusione lenta dell'informazione comune)",
                 {"soglia_deviazioni_btc": 2.0, "finestra_barre": 168, "quota_di_btc": 0.5, "stop_atr": 2.0, "atr_barre": 14,
                  "uscita_barre": 4, "target": None},
                 "R medio fra -0,15 e +0,05; non netto")
    return var, meta


# ---------------------------------------------------------------------------
# I-10 squeeze di Bollinger e rottura (4h)
# ---------------------------------------------------------------------------
F10 = "J. Bollinger, 'Bollinger on Bollinger Bands', McGraw-Hill, 2001"


def _i10(direzione):
    def prepara(serie):
        ind = _base(serie)
        c = ind["c_np"]
        m = C.sma(c, 20)
        sd = np.full(len(c), np.nan)
        for i in range(19, len(c)):
            sd[i] = np.std(c[i - 19:i + 1], ddof=0)
        bw = 4 * sd / m
        sq = np.full(len(c), np.nan)
        for i in range(19 + 124, len(c)):
            sq[i] = 1.0 if np.min(bw[i - 4:i + 1]) <= np.min(bw[i - 124:i - 4]) else 0.0
        ind["su"] = C.a_lista(m + 2 * sd)
        ind["giu"] = C.a_lista(m - 2 * sd)
        ind["sq"] = C.a_lista(sq)
        ind["riscaldamento"] = _riscaldamento(ind["sq"], ind["atr"])
        return ind

    if direzione == "long":
        ingresso = lambda ind, i: ind["sq"][i] == 1.0 and ind["c"][i] > ind["su"][i]
    else:
        ingresso = lambda ind, i: ind["sq"][i] == 1.0 and ind["c"][i] < ind["giu"][i]
    nome = "I-10-L" if direzione == "long" else "I-10-S"
    var = Variante(nome, "4h", direzione, prepara, ingresso, _stop(2.0, direzione), max_barre=30)
    meta = _meta("I-10", nome, F10, "compressione della volatilita' seguita da espansione nella direzione dell'uscita dalle bande",
                 {"bande_barre": 20, "bande_deviazioni": 2, "squeeze_ultime_barre": 5, "squeeze_confronto_barre": 120,
                  "stop_atr": 2.0, "atr_barre": 14, "uscita_barre": 30, "target": None},
                 "R medio fra -0,10 e +0,10; probabile sotto i trade minimi")
    return var, meta


# ---------------------------------------------------------------------------
# I-11 RSI(2) nel trend (4h)
# ---------------------------------------------------------------------------
F11 = "L. Connors, C. Alvarez, 'Short Term Trading Strategies That Work', TradingMarkets, 2009"


def _i11(direzione):
    def prepara(serie):
        ind = _base(serie)
        c = ind["c_np"]
        ind["m200"] = C.a_lista(C.sma(c, 200))
        ind["m5"] = C.a_lista(C.sma(c, 5))
        ind["rsi2"] = C.a_lista(C.rsi(c, 2))
        ind["riscaldamento"] = _riscaldamento(ind["m200"], ind["m5"], ind["rsi2"], ind["atr"])
        return ind

    if direzione == "long":
        ingresso = lambda ind, i: ind["c"][i] > ind["m200"][i] and ind["rsi2"][i] < 10
        uscita = lambda ind, i, pos: ind["m5"][i] is not None and ind["c"][i] > ind["m5"][i]
    else:
        ingresso = lambda ind, i: ind["c"][i] < ind["m200"][i] and ind["rsi2"][i] > 90
        uscita = lambda ind, i, pos: ind["m5"][i] is not None and ind["c"][i] < ind["m5"][i]
    nome = "I-11-L" if direzione == "long" else "I-11-S"
    var = Variante(nome, "4h", direzione, prepara, ingresso, _stop(3.0, direzione), max_barre=20, uscita=uscita)
    meta = _meta("I-11", nome, F11, "ritorno dopo un ipervenduto (ipercomprato) brevissimo dentro il trend",
                 {"media_trend": 200, "rsi_barre": 2, "rsi_soglia": 10 if direzione == "long" else 90, "media_uscita": 5,
                  "uscita_barre_massime": 20, "stop_atr": 3.0, "atr_barre": 14, "target": None},
                 "R medio fra -0,10 e +0,10; non netto")
    return var, meta


CATALOGO = {
    "I-01-L": lambda: _i01("long"), "I-01-S": lambda: _i01("short"),
    "I-02-L": lambda: _i02("long"), "I-02-S": lambda: _i02("short"),
    "I-03-L": lambda: _i03("long"), "I-03-S": lambda: _i03("short"),
    "I-04-L": lambda: _i04("long"), "I-04-S": lambda: _i04("short"),
    "I-05-S": lambda: _i05("short"), "I-05-L": lambda: _i05("long"),
    "I-06-L": lambda: _i06("long"), "I-06-S": lambda: _i06("short"),
    "I-07-L": lambda: _i07("long"), "I-07-S": lambda: _i07("short"),
    "I-08-L": _i08,
    "I-09-L": lambda: _i09("long"), "I-09-S": lambda: _i09("short"),
    "I-10-L": lambda: _i10("long"), "I-10-S": lambda: _i10("short"),
    "I-11-L": lambda: _i11("long"), "I-11-S": lambda: _i11("short"),
}


# ---------------------------------------------------------------------------
# Controllo positivo degli strumenti (lezioni/metodo.md): lookahead DICHIARATO
# ---------------------------------------------------------------------------


def controllo_positivo():
    def prepara(serie):
        ind = _base(serie)
        o, c = ind["o_np"], ind["c_np"]
        fut = [None] * serie.n
        for i in range(serie.n - 1):
            fut[i] = bool(c[i + 1] > o[i + 1])  # legge la barra DOPO: vietato in una variante vera
        ind["fut"] = fut
        ind["riscaldamento"] = _riscaldamento(ind["atr"])
        return ind

    ingresso = lambda ind, i: bool(ind["fut"][i])
    return Variante("CONTROLLO", "1h", "long", prepara, ingresso, _stop(2.0, "long"), max_barre=1)
