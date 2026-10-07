"""I segnali delle 12 idee di ipotesi.md, scritti come dichiarati li', prima di ogni test.

Ogni funzione ``segnali_<idea>(s)`` restituisce un array (+1 long, -1 short, 0 niente)
allineato alle barre di ``s`` e calcolato in modo causale, piu' l'oggetto ``Uscita``
dell'idea. Le varianti long e short di una stessa idea usano lo stesso array
filtrato per segno (``solo(segnali, +1)``). I numeri sono quelli di ipotesi.md: non
si toccano dopo aver visto un risultato (una modifica e' una nuova variante).
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Dict, Optional

import numpy as np

import comune
from comune import Serie, Uscita


@dataclass
class Idea:
    codice: str
    nome: str
    timeframe: str
    con_btc: bool
    costruisci: Callable[[Serie], tuple]  # -> (segnali, Uscita, riscaldamento_barre)
    direzioni: tuple = (1, -1)


def solo(segnali: np.ndarray, direzione: int) -> np.ndarray:
    return np.where(segnali == direzione, direzione, 0)


# --- I-01 momento di serie temporale, 4h ---------------------------------------------
def i01(s: Serie):
    r42 = comune.rendimento_a(s.close, 42)
    segn = np.where(r42 > 0, 1, np.where(r42 < 0, -1, 0))
    segn[~np.isfinite(r42)] = 0

    def chiusura(i, pos):  # il segno del rendimento a 42 barre cambia
        return (pos.direzione == "long" and segn[i] < 0) or (pos.direzione == "short" and segn[i] > 0)

    return segn, Uscita(k_atr=2.0, h_barre=42, chiusura_segnale=chiusura), 42


# --- I-02 rottura del canale, 4h -----------------------------------------------------
def i02(s: Serie):
    hi30, lo30 = comune.massimo_precedente(s.high, 30), comune.minimo_precedente(s.low, 30)
    hi15, lo15 = comune.massimo_precedente(s.high, 15), comune.minimo_precedente(s.low, 15)
    segn = np.where(s.close > hi30, 1, np.where(s.close < lo30, -1, 0))
    segn[~np.isfinite(hi30)] = 0

    def chiusura(i, pos):
        return (pos.direzione == "long" and s.close[i] < lo15[i]) or (pos.direzione == "short" and s.close[i] > hi15[i])

    return segn, Uscita(k_atr=2.0, h_barre=60, chiusura_segnale=chiusura), 30


# --- I-03 RSI a 2 periodi, 1h ---------------------------------------------------------
def i03(s: Serie):
    r = comune.rsi(s.close, 2)
    segn = np.where(r < 10, 1, np.where(r > 90, -1, 0))
    segn[~np.isfinite(r)] = 0

    def chiusura(i, pos):
        return (pos.direzione == "long" and r[i] > 50) or (pos.direzione == "short" and r[i] < 50)

    return segn, Uscita(k_atr=2.0, h_barre=12, chiusura_segnale=chiusura), 20


# --- I-04 reazione eccessiva dopo candela anomala, 4h ----------------------------------
def i04(s: Serie):
    r = comune.rendimenti(s.close)
    sigma = np.full(len(r), np.nan)
    # deviazione standard dei 180 rendimenti PRECEDENTI (esclusa la barra corrente)
    ds = comune.dev_standard_mobile(np.nan_to_num(r, nan=0.0), 180)
    sigma[1:] = ds[:-1]
    segn = np.where(r > 2.5 * sigma, -1, np.where(r < -2.5 * sigma, 1, 0))
    segn[~np.isfinite(sigma) | ~np.isfinite(r)] = 0
    return segn, Uscita(k_atr=2.0, h_barre=3), 182


# --- I-05 ritardo di ETH su BTC, 1h --------------------------------------------------
def i05(s: Serie):
    r_eth = comune.rendimenti(s.close)
    r_btc = comune.rendimenti(s.btc_close)
    segn = np.where((r_btc > 0.0075) & (r_eth < r_btc - 0.0025), 1,
                    np.where((r_btc < -0.0075) & (r_eth > r_btc + 0.0025), -1, 0))
    segn[~np.isfinite(r_eth) | ~np.isfinite(r_btc)] = 0
    return segn, Uscita(k_atr=2.0, h_barre=4), 20


# --- I-06 ritorno alla media del rapporto ETH/BTC, 4h ------------------------------------
def i06(s: Serie):
    rapporto = np.log(s.close / s.btc_close)
    m, d = comune.media_mobile(rapporto, 120), comune.dev_standard_mobile(rapporto, 120)
    z = (rapporto - m) / np.where(d > 0, d, np.nan)
    segn = np.where(z > 2, -1, np.where(z < -2, 1, 0))
    segn[~np.isfinite(z)] = 0

    def chiusura(i, pos):
        return (pos.direzione == "short" and z[i] <= 0) or (pos.direzione == "long" and z[i] >= 0)

    return segn, Uscita(k_atr=2.0, h_barre=60, chiusura_segnale=chiusura), 120


# --- I-07 momento relativo ETH contro BTC, 1d, ogni lunedi' ---------------------------------
def i07(s: Serie):
    rel = comune.rendimento_a(s.close, 14) - comune.rendimento_a(s.btc_close, 14)
    domenica = np.array([comune.giorno_settimana(int(t)) == 6 for t in s.ts])
    segn = np.where(domenica & (rel > 0), 1, np.where(domenica & (rel < 0), -1, 0))
    segn[~np.isfinite(rel)] = 0
    return segn, Uscita(k_atr=2.0, h_barre=7), 14


# --- I-08 inversione del fine settimana, 1d ----------------------------------------------
def i08(s: Serie):
    r2 = comune.rendimento_a(s.close, 2)  # sabato + domenica, letto alla chiusura della domenica
    domenica = np.array([comune.giorno_settimana(int(t)) == 6 for t in s.ts])
    segn = np.where(domenica & (r2 > 0.01), -1, np.where(domenica & (r2 < -0.01), 1, 0))
    segn[~np.isfinite(r2)] = 0
    return segn, Uscita(k_atr=2.0, h_barre=1), 14


# --- I-09 momento intragiornaliero, 1h -------------------------------------------------
def i09(s: Serie):
    r = comune.rendimenti(s.close)
    ore = np.array([comune.ora_utc(int(t)) for t in s.ts])
    segn = np.zeros(len(s.ts), dtype=int)
    # alla chiusura della barra 22:00-23:00 (ts con ora 22) si legge la barra con ora 0 dello stesso giorno UTC
    giorno = (s.ts // comune.MS_GIORNO)
    prima_ora: Dict[int, float] = {}
    for i in range(len(s.ts)):
        if ore[i] == 0 and np.isfinite(r[i]):
            prima_ora[int(giorno[i])] = r[i]
        if ore[i] == 22:
            r0 = prima_ora.get(int(giorno[i]))
            if r0 is not None:
                segn[i] = 1 if r0 > 0.003 else (-1 if r0 < -0.003 else 0)
    return segn, Uscita(k_atr=2.0, h_barre=1), 20


# --- I-10 funding estremo come segnale contrario, 8h ----------------------------------------
def i10(s: Serie):
    # tasso del settlement che cade all'apertura della barra 8h (00, 08, 16 UTC)
    per_ts = {ts: tasso for ts, tasso in s.funding}
    tasso = np.array([per_ts.get(int(t), np.nan) for t in s.ts])
    alto = comune.percentile_mobile(np.nan_to_num(tasso, nan=0.0), 90, 90)
    basso = comune.percentile_mobile(np.nan_to_num(tasso, nan=0.0), 90, 10)
    segn = np.where(tasso > alto, -1, np.where(tasso < basso, 1, 0))
    segn[~np.isfinite(tasso) | ~np.isfinite(alto)] = 0
    return segn, Uscita(k_atr=2.0, h_barre=1), 92


# --- I-11 compressione della volatilita' e rottura, 4h ---------------------------------------
def i11(s: Serie):
    r = np.nan_to_num(comune.rendimenti(s.close), nan=0.0)
    rapporto = comune.dev_standard_mobile(r, 30) / comune.dev_standard_mobile(r, 180)
    compresso_prima = np.concatenate(([False], (rapporto[:-1] < 0.5)))
    hi30, lo30 = comune.massimo_precedente(s.high, 30), comune.minimo_precedente(s.low, 30)
    segn = np.where(compresso_prima & (s.close > hi30), 1, np.where(compresso_prima & (s.close < lo30), -1, 0))
    segn[~np.isfinite(rapporto) | ~np.isfinite(hi30)] = 0
    return segn, Uscita(k_atr=2.0, h_barre=30, rr_target=2.0), 182


# --- I-12 premio del volume alto, 12h -------------------------------------------------------
def i12(s: Serie):
    volume_usdt = s.volume * s.close  # volume base x close: approssimazione del volume in USDT della barra
    soglia = comune.percentile_mobile(volume_usdt, 100, 90)
    segn = np.where(volume_usdt > soglia, 1, 0)
    segn[~np.isfinite(soglia)] = 0
    return segn, Uscita(k_atr=2.0, h_barre=6), 100


# =====================================================================================
# Secondo lotto (ipotesi.md, «Secondo lotto di idee»), scritto prima dei risultati del primo
# =====================================================================================


# --- I-13 squilibrio degli ordini a mercato, 1h ----------------------------------------------
def i13(s: Serie):
    q, tb = comune.flusso_taker(s, comune.INIZIO_DATI, comune.FINE_IN_SAMPLE)
    q4 = comune.media_mobile(np.nan_to_num(q, nan=0.0), 4) * 4
    tb4 = comune.media_mobile(np.nan_to_num(tb, nan=0.0), 4) * 4
    quota = np.where(q4 > 0, tb4 / np.where(q4 > 0, q4, 1.0), np.nan)
    segn = np.where(quota > 0.58, 1, np.where(quota < 0.42, -1, 0))
    segn[~np.isfinite(quota)] = 0
    return segn, Uscita(k_atr=2.0, h_barre=2), 20


# --- I-14 premio del perpetuo sul mark, 1h -----------------------------------------------------
def i14(s: Serie):
    premio = comune.premio_sul_mark(s)
    p = np.nan_to_num(premio, nan=0.0)
    alto, basso = comune.percentile_mobile(p, 720, 90), comune.percentile_mobile(p, 720, 10)
    segn = np.where(premio > alto, -1, np.where(premio < basso, 1, 0))
    segn[~np.isfinite(premio) | ~np.isfinite(alto)] = 0
    return segn, Uscita(k_atr=2.0, h_barre=4), 722


# --- I-15 rottura del range d'apertura del giorno UTC, 1h ------------------------------------------
def i15(s: Serie):
    ore = np.array([comune.ora_utc(int(t)) for t in s.ts])
    giorno = s.ts // comune.MS_GIORNO
    # ATR giornaliero dei 14 giorni PRECEDENTI, dalle candele giornaliere aggregate
    giorni = comune.candele("1d", comune.INIZIO_DATI, comune.FINE_IN_SAMPLE)
    chiusure = np.array([c.close for c in giorni])
    alti, bassi = np.array([c.high for c in giorni]), np.array([c.low for c in giorni])
    prev = np.concatenate(([chiusure[0]], chiusure[:-1]))
    tr = np.maximum(alti - bassi, np.maximum(np.abs(alti - prev), np.abs(bassi - prev)))
    atr_g = comune.media_mobile(tr, 14)
    atr_del_giorno = {int(c.ts // comune.MS_GIORNO) + 1: atr_g[i] for i, c in enumerate(giorni)}  # vale dal giorno DOPO
    segn = np.zeros(len(s.ts), dtype=int)
    apertura: Dict[int, float] = {}
    gia_entrato: Dict[int, bool] = {}
    for i in range(len(s.ts)):
        g = int(giorno[i])
        if ore[i] == 0:
            apertura[g] = s.open[i]
        a, atrg = apertura.get(g), atr_del_giorno.get(g, np.nan)
        if a is None or not np.isfinite(atrg) or gia_entrato.get(g) or ore[i] >= 22:
            continue
        if s.close[i] > a + 0.5 * atrg:
            segn[i], gia_entrato[g] = 1, True
        elif s.close[i] < a - 0.5 * atrg:
            segn[i], gia_entrato[g] = -1, True

    def chiusura(i, pos):
        return ore[i] == 23  # chiude all'apertura delle 00:00

    return segn, Uscita(k_atr=2.0, h_barre=24, chiusura_segnale=chiusura), 24 * 15


# --- I-16 ore americane (long) e ore asiatiche (short), 1h ------------------------------------------
def i16(s: Serie):
    ore = np.array([comune.ora_utc(int(t)) for t in s.ts])
    segn = np.where(ore == 12, 1, np.where(ore == 23, -1, 0))
    return segn, Uscita(k_atr=2.0, h_barre=8), 20


# =====================================================================================
# Terzo lotto (ipotesi.md, «Terzo lotto di idee»), scritto prima dei risultati del secondo
# =====================================================================================


# --- I-17 autocorrelazione dei rendimenti giornalieri, 1d ------------------------------------------
def i17(s: Serie):
    r = comune.rendimenti(s.close)
    segn = np.where(r > 0, 1, np.where(r < 0, -1, 0))
    segn[~np.isfinite(r)] = 0
    return segn, Uscita(k_atr=2.0, h_barre=1), 15


# --- I-18 attraversamento di un livello tondo, 1h ------------------------------------------------------
def i18(s: Serie):
    prev = np.concatenate(([np.nan], s.close[:-1]))
    passo = np.where(s.close < 1000.0, 10.0, 100.0)
    # livello tondo attraversato verso l'alto: esiste L = k*passo con prev < L <= close
    su = np.floor(s.close / passo) * passo
    giu = np.ceil(s.close / passo) * passo
    segn = np.where((prev < su) & (su <= s.close), 1, np.where((prev > giu) & (giu >= s.close), -1, 0))
    segn[~np.isfinite(prev)] = 0
    return segn, Uscita(k_atr=2.0, h_barre=2), 20


# --- I-19 vicinanza al massimo e al minimo a 30 giorni, 4h -------------------------------------------
def i19(s: Serie):
    hi, lo = comune.massimo_precedente(s.high, 180), comune.minimo_precedente(s.low, 180)
    segn = np.where(s.close >= 0.98 * hi, 1, np.where(s.close <= 1.02 * lo, -1, 0))
    segn[~np.isfinite(hi)] = 0
    return segn, Uscita(k_atr=2.0, h_barre=24), 180


IDEE: Dict[str, Idea] = {
    "I-17": Idea("I-17", "autocorrelazione dei rendimenti giornalieri", "1d", False, i17),
    "I-18": Idea("I-18", "attraversamento di un livello tondo", "1h", False, i18),
    "I-19": Idea("I-19", "vicinanza al massimo e al minimo a 30 giorni", "4h", False, i19),
    "I-13": Idea("I-13", "squilibrio degli ordini a mercato (compratori aggressivi)", "1h", False, i13),
    "I-14": Idea("I-14", "premio del perpetuo sul prezzo mark", "1h", False, i14),
    "I-15": Idea("I-15", "rottura del range d'apertura del giorno UTC", "1h", False, i15),
    "I-16": Idea("I-16", "ore americane (long) e ore asiatiche (short)", "1h", False, i16),
    "I-01": Idea("I-01", "momento di serie temporale a 7 giorni", "4h", False, i01),
    "I-02": Idea("I-02", "rottura del canale a 30 barre", "4h", False, i02),
    "I-03": Idea("I-03", "inversione RSI a 2 periodi", "1h", False, i03),
    "I-04": Idea("I-04", "reazione eccessiva dopo candela anomala", "4h", False, i04),
    "I-05": Idea("I-05", "ritardo di ETH su BTC", "1h", True, i05),
    "I-06": Idea("I-06", "ritorno alla media del rapporto ETH/BTC", "4h", True, i06),
    "I-07": Idea("I-07", "momento relativo ETH contro BTC", "1d", True, i07),
    "I-08": Idea("I-08", "inversione del fine settimana", "1d", False, i08),
    "I-09": Idea("I-09", "momento intragiornaliero", "1h", False, i09),
    "I-10": Idea("I-10", "funding estremo come segnale contrario", "8h", False, i10),
    "I-11": Idea("I-11", "compressione della volatilita' e rottura", "4h", False, i11),
    "I-12": Idea("I-12", "premio del volume alto", "12h", False, i12, direzioni=(1,)),
}

FONTI = {
    "I-01": "Moskowitz, Ooi, Pedersen, «Time Series Momentum», J. Financial Economics 2012; Liu e Tsyvinski, «Risks and Returns of Cryptocurrency», Rev. Financial Studies 2021",
    "I-02": "Brock, Lakonishok, LeBaron, «Simple Technical Trading Rules...», J. Finance 1992; Grobys, Ahmed, Sapkota, Finance Research Letters 2020",
    "I-03": "Lehmann, «Fads, Martingales, and Market Efficiency», QJE 1990; Connors e Alvarez, «Short Term Trading Strategies That Work», 2008",
    "I-04": "De Bondt e Thaler, «Does the Stock Market Overreact?», J. Finance 1985; Caporale e Plastun, «Price overreactions in the cryptocurrency market», J. Economic Studies 2019",
    "I-05": "Koutmos, «Return and volatility spillovers among cryptocurrencies», Economics Letters 2018; Ciaian, Rajcaniova, Kancs, JIFMIM 2018",
    "I-06": "Gatev, Goetzmann, Rouwenhorst, «Pairs Trading», Rev. Financial Studies 2006",
    "I-07": "Liu, Tsyvinski, Wu, «Common Risk Factors in Cryptocurrency», J. Finance 2022; Jegadeesh e Titman, J. Finance 1993",
    "I-08": "Baur, Cahill, Godfrey, Liu, Finance Research Letters 2019; Kaiser, «Seasonality in cryptocurrencies», Finance Research Letters 2019; Lehmann 1990",
    "I-09": "Gao, Han, Li, Zhou, «Market intraday momentum», J. Financial Economics 2018",
    "I-10": "He, Manela, Ross, von Wachter, «Fundamentals of Perpetual Futures», 2022 (arXiv 2212.06888); Schmeling, Schrimpf, Todorov, «Crypto carry», BIS WP 1087, 2023",
    "I-11": "Bollinger, «Bollinger on Bollinger Bands», 2001; Connors e Raschke, «Street Smarts», 1995",
    "I-12": "Gervais, Kaniel, Mingelgrin, «The High-Volume Return Premium», J. Finance 2001; Blume, Easley, O'Hara, J. Finance 1994",
    "I-13": "Chordia, Roll, Subrahmanyam, «Order imbalance, liquidity, and market returns», J. Financial Economics 2002",
    "I-14": "Alexander, Choi, Park, Park, «BitMEX bitcoin derivatives: Price discovery, informational efficiency, and hedging effectiveness», J. Futures Markets 2020; He, Manela, Ross, von Wachter 2022",
    "I-15": "Crabel, «Day Trading with Short Term Price Patterns and Opening Range Breakout», 1990",
    "I-16": "Baur, Cahill, Godfrey, Liu, «Bitcoin time-of-day, day-of-week and month-of-year effects in returns and trading volume», Finance Research Letters 2019",
    "I-17": "Lo e MacKinlay, «Stock Market Prices Do Not Follow Random Walks», Rev. Financial Studies 1988; Urquhart, «The inefficiency of Bitcoin», Economics Letters 2016",
    "I-18": "Osler, «Currency Orders and Exchange Rate Dynamics: An Explanation for the Predictive Success of Technical Analysis», J. Finance 2003",
    "I-19": "George e Hwang, «The 52-Week High and Momentum Investing», J. Finance 2004",
}

MECCANISMI = {
    "I-01": "flussi lenti di investitori che seguono le notizie con ritardo: il segno del rendimento a 7 giorni continua",
    "I-02": "una chiusura fuori dal range di 5 giorni segnala nuova informazione o stop forzati nel verso della rottura",
    "I-03": "dopo un eccesso di vendite (RSI2<10) o di acquisti (>90) in poche ore, il prezzo rimbalza per il ritorno della liquidita'",
    "I-04": "una candela da 4h oltre 2,5 deviazioni standard e' una reazione eccessiva che la barra dopo corregge",
    "I-05": "BTC guida e ETH la segue con ritardo di qualche ora quando il divario di rendimento e' ampio",
    "I-06": "il rapporto ETH/BTC oscilla attorno a una media mobile di 20 giorni: oltre 2 deviazioni standard rientra",
    "I-07": "il rendimento relativo a 2 settimane di ETH contro BTC continua nella settimana dopo (momento fra monete)",
    "I-08": "mercati sottili nel fine settimana esagerano il movimento e il lunedi', con la liquidita', corregge",
    "I-09": "la prima ora UTC del giorno predice l'ultima per i flussi di chi aggiusta le posizioni prima del settlement",
    "I-10": "un funding estremo segnala leva affollata da un lato, che si sgonfia fino al settlement dopo",
    "I-11": "dopo una compressione della volatilita' (30 barre sotto meta' di 180) la rottura del range avvia un movimento ampio nello stesso verso",
    "I-12": "una candela con volume nel 10 % piu' alto attira attenzione e precede rendimenti positivi (premio del volume alto)",
    "I-13": "la pressione degli ordini aggressivi delle ultime 4 ore (quota compratori sopra 58 % o sotto 42 %) continua per 2 ore per l'inventario dei market maker",
    "I-14": "un premio estremo del perpetuo sul mark (oltre il 90° o sotto il 10° percentile a 30 giorni) rientra nelle ore successive",
    "I-15": "la prima chiusura oraria oltre mezzo ATR giornaliero dall'apertura del giorno UTC continua fino a fine giornata",
    "I-16": "le ore della sessione americana rendono di piu' e quelle asiatiche di meno, per i flussi legati ai mercati tradizionali",
    "I-17": "il segno del rendimento giornaliero continua il giorno dopo (autocorrelazione positiva a breve)",
    "I-18": "gli ordini di stop si raggruppano oltre i numeri tondi: attraversato il livello, il movimento accelera per 2 ore",
    "I-19": "vicino al massimo (minimo) a 30 giorni gli operatori ancorati vendono (comprano) troppo presto e poi rincorrono: continuazione per 4 giorni",
}
