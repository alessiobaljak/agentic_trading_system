"""Le sei regole da manuale della prova a placebo A BARRE GIORNALIERE (seconda edizione; regole in ``regole.md``).

E' il modulo delle regole della prova a 1 ora (``taratura/placebo_gruppo/placebo_gruppo.py``) con i parametri
scritti per il giorno (correzione 1 di ``regole.md``): con i parametri a 1 ora (medie 20/50, RSI 14, rottura 20,
Bollinger 20, MACD 12/26/9, momento 10, uscita a tempo 10 barre) le placebo davano 250-420 trade sommati in
costruzione sulle 80 monete, sotto il minimo di 700 dell'esame: scarti, non giudizi. I parametri qui sotto sono
scelti SOLO contando i trade (``conta_trade_di_gruppo``, mai guardando rendimenti): devono dare almeno 700 trade
sommati in costruzione per quasi tutte le regole. Il contratto con ``research/src/gruppo.py`` e' quello della
docstring di ``gruppo.py`` (punto 2): ``crea_variante``, ``crea_a``, ``crea_casuale``, ``crea_segnale``; solo
libreria standard, numpy e ``research.src.motore``.
"""
from __future__ import annotations

import math

import numpy as np

from research.src.motore import Segnale

#: barre iniziali di ogni serie senza segnali
RISCALDAMENTO = 60
#: le sei regole d'ingresso da manuale e la loro uscita
REGOLE = ("incrocio_medie", "rsi", "rottura", "bollinger", "macd", "momento")
USCITA_DELLA_REGOLA = {
    "incrocio_medie": "atr", "rottura": "atr", "macd": "atr",
    "rsi": "tempo", "bollinger": "tempo", "momento": "tempo",
}
USCITE = ("atr", "tempo")
DIREZIONI = ("long", "short")
TIMEFRAME = ("1d",)
MS_BARRA = {"1d": 86_400_000}
#: i parametri per il giorno (correzione 1 di regole.md; scelti contando i trade, mai i rendimenti)
PARAMETRI = {
    "incrocio_medie": {"corta": 5, "lunga": 20},
    "rsi": {"n": 7, "basso": 30, "alto": 70},
    "rottura": {"n": 10},
    "bollinger": {"n": 10, "k": 1.5},
    "macd": {"corta": 5, "lunga": 13, "segnale": 4},
    "momento": {"n": 5},
}
#: uscita a tempo: barre tenute (5 giorni)
BARRE_USCITA_TEMPO = {"1d": 5}
#: durata massima di OGNI posizione, anche con l'uscita ATR (correzione 2 di regole.md): le 60 barre dell'uscita a
#: tempo delle idee della seconda edizione (PROTOCOLLO_2, sezione 3.1). Senza, una posizione a stop/target in ATR
#: giornalieri dura centinaia di giorni, il blocco del bootstrap diventa l'intera serie e l'esame non e' valutabile.
BARRE_MASSIME = 60
#: barre dell'ATR (media semplice dei true range)
BARRE_ATR = 14
#: stop e target in ATR per tipo di uscita: (stop, target o None)
MULTIPLI_ATR = {"atr": (1.5, 2.5), "tempo": (2.0, None)}


def _sma(x: np.ndarray, n: int) -> np.ndarray:
    out = np.full(x.size, np.nan)
    if x.size >= n:
        c = np.cumsum(np.insert(x, 0, 0.0))
        out[n - 1:] = (c[n:] - c[:-n]) / n
    return out


def _ema(x: np.ndarray, n: int) -> np.ndarray:
    out = np.full(x.size, np.nan)
    if x.size < n:
        return out
    a = 2.0 / (n + 1)
    out[n - 1] = x[:n].mean()
    for i in range(n, x.size):
        out[i] = a * x[i] + (1 - a) * out[i - 1]
    return out


def _rsi(close: np.ndarray, n: int) -> np.ndarray:
    out = np.full(close.size, np.nan)
    if close.size <= n:
        return out
    d = np.diff(close)
    su = np.where(d > 0, d, 0.0)
    giu = np.where(d < 0, -d, 0.0)
    m_su, m_giu = su[:n].mean(), giu[:n].mean()
    out[n] = 100.0 if m_giu == 0 else 100.0 - 100.0 / (1.0 + m_su / m_giu)
    for i in range(n + 1, close.size):
        m_su = (m_su * (n - 1) + su[i - 1]) / n
        m_giu = (m_giu * (n - 1) + giu[i - 1]) / n
        out[i] = 100.0 if m_giu == 0 else 100.0 - 100.0 / (1.0 + m_su / m_giu)
    return out


def segnali_regola(candele, regola: str, direzione: str) -> np.ndarray:
    """Maschera booleana delle barre in cui la regola scatta, alla chiusura della barra. CAUSALE: il valore alla
    barra i usa solo le barre 0..i. Il riscaldamento NON e' tolto qui: lo toglie chi usa la maschera."""
    if regola not in REGOLE or direzione not in DIREZIONI:
        raise ValueError(f"regola o direzione sconosciuta: {regola!r}, {direzione!r}")
    p = PARAMETRI[regola]
    close = np.array([c.close for c in candele], dtype=float)
    high = np.array([c.high for c in candele], dtype=float)
    low = np.array([c.low for c in candele], dtype=float)
    n = close.size
    s = np.zeros(n, dtype=bool)
    lungo = direzione == "long"
    with np.errstate(invalid="ignore"):
        if regola == "incrocio_medie":
            a, b = _sma(close, p["corta"]), _sma(close, p["lunga"])
            sopra = a > b
            s[1:] = (sopra[1:] & ~sopra[:-1]) if lungo else (~sopra[1:] & sopra[:-1])
            s &= ~np.isnan(b)
            s[1:] &= ~np.isnan(b[:-1])
        elif regola == "rsi":
            r = _rsi(close, p["n"])
            if lungo:
                s[1:] = (r[:-1] < p["basso"]) & (r[1:] >= p["basso"])
            else:
                s[1:] = (r[:-1] > p["alto"]) & (r[1:] <= p["alto"])
        elif regola == "rottura":
            k = p["n"]
            for i in range(k, n):
                s[i] = close[i] > high[i - k:i].max() if lungo else close[i] < low[i - k:i].min()
        elif regola == "bollinger":
            k = p["n"]
            m = _sma(close, k)
            sd = np.full(n, np.nan)
            for i in range(k - 1, n):
                sd[i] = close[i - k + 1:i + 1].std()
            s = (close < m - p["k"] * sd) if lungo else (close > m + p["k"] * sd)
        elif regola == "macd":
            linea = _ema(close, p["corta"]) - _ema(close, p["lunga"])
            valida = ~np.isnan(linea)
            seg = np.full(n, np.nan)
            if valida.sum() >= p["segnale"]:
                primo = int(np.argmax(valida))
                seg[primo:] = _ema(linea[primo:], p["segnale"])
            sopra = linea > seg
            pronto = ~np.isnan(seg)
            s[1:] = ((sopra[1:] & ~sopra[:-1]) if lungo else (~sopra[1:] & sopra[:-1])) & pronto[1:] & pronto[:-1]
        elif regola == "momento":
            k = p["n"]
            roc = np.full(n, np.nan)
            roc[k:] = close[k:] / close[:-k] - 1.0
            pos = roc > 0
            neg = roc < 0
            pronto = ~np.isnan(roc)
            s[1:] = (pos[1:] & ~pos[:-1] & pronto[:-1]) if lungo else (neg[1:] & ~neg[:-1] & pronto[:-1])
    return np.asarray(s, dtype=bool)


def atr_alla_barra(storia, i: int) -> float:
    """ATR(14) alla barra i: media semplice dei true range delle barre i - 13 .. i (NaN se i < 14)."""
    if i < BARRE_ATR:
        return math.nan
    barre = storia[i - BARRE_ATR:i + 1]
    tr = []
    for prima, barra in zip(barre[:-1], barre[1:]):
        tr.append(max(barra.high - barra.low, max(abs(barra.high - prima.close), abs(barra.low - prima.close))))
    return math.fsum(tr) / BARRE_ATR


def _segnale_alla_barra(storia, direzione: str, uscita: str):
    """Il segnale SENZA la condizione d'ingresso alla chiusura dell'ultima barra di ``storia``: None nel
    riscaldamento e dove l'ATR non e' un numero positivo."""
    i = len(storia) - 1
    if i < RISCALDAMENTO:
        return None
    a = atr_alla_barra(storia, i)
    if not math.isfinite(a) or a <= 0:
        return None
    lato = 1.0 if direzione == "long" else -1.0
    prezzo = storia[-1].close
    multiplo_stop, multiplo_target = MULTIPLI_ATR[uscita]
    target = None if multiplo_target is None else prezzo + lato * multiplo_target * a
    return Segnale(direzione, prezzo - lato * multiplo_stop * a, target)


def _uscita_a_tempo(barre: int):
    """«chiudi» quando la posizione e' tenuta da ``barre`` barre (la barra d'ingresso e' la prima)."""
    stato = {"ts": None, "indice": None}

    def esci(storia, posizione):
        i = len(storia) - 1
        if stato["ts"] != posizione.ts_entrata:
            stato["ts"], stato["indice"] = posizione.ts_entrata, None
            for k in range(i, max(-1, i - barre - 1), -1):
                if storia[k].ts == posizione.ts_entrata:
                    stato["indice"] = k
                    break
        if stato["indice"] is None:
            return "chiudi"
        return "chiudi" if i - stato["indice"] + 1 >= barre else None

    return esci


def _leggi_p(ctx, p):
    regola, direzione = p.get("regola"), p.get("direzione")
    if regola not in REGOLE or direzione not in DIREZIONI:
        raise ValueError(f"p deve avere regola in {REGOLE} e direzione in {DIREZIONI}: {p!r}")
    if ctx.timeframe not in BARRE_USCITA_TEMPO:
        raise ValueError(f"timeframe {ctx.timeframe!r} non previsto dalla prova: {TIMEFRAME}")
    return regola, direzione, USCITA_DELLA_REGOLA[regola], BARRE_USCITA_TEMPO[ctx.timeframe]


def _strategia(direzione: str, uscita: str, barre: int, entra):
    # «tempo»: le barre della regola; «atr»: stop e target in ATR, ma mai oltre BARRE_MASSIME (correzione 2)
    esci = _uscita_a_tempo(barre if uscita == "tempo" else BARRE_MASSIME)

    def strategia(storia, posizione):
        if posizione is not None:
            return esci(storia, posizione)
        if entra(storia):
            return _segnale_alla_barra(storia, direzione, uscita)
        return None

    return strategia


def crea_variante(ctx, p):
    """La regola completa: segnale alla chiusura della barra i >= 60 in cui la regola scatta (calcolo vettoriale
    sulla storia chiusa, causale: la maschera alla barra i usa solo le barre fino a i)."""
    regola, direzione, uscita, barre = _leggi_p(ctx, p)

    def crea():
        def entra(storia):
            i = len(storia) - 1
            if i < RISCALDAMENTO:
                return False
            return bool(segnali_regola(storia, regola, direzione)[i])

        return _strategia(direzione, uscita, barre, entra)

    return crea


def crea_a(ctx, p):
    _, direzione, uscita, barre = _leggi_p(ctx, p)

    def crea():
        return _strategia(direzione, uscita, barre, lambda storia: len(storia) - 1 >= RISCALDAMENTO)

    return crea


def crea_casuale(ctx, p):
    _, direzione, uscita, barre = _leggi_p(ctx, p)

    def crea(ingressi):
        ingressi = frozenset(ingressi)
        return _strategia(direzione, uscita, barre, lambda storia: (len(storia) - 1) in ingressi)

    return crea


def crea_segnale(ctx, p):
    _, direzione, uscita, _ = _leggi_p(ctx, p)

    def crea():
        def segnale(storia):
            return _segnale_alla_barra(storia, direzione, uscita)

        return segnale

    return crea
