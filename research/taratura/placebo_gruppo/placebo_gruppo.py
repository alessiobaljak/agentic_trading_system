"""Il modulo della placebo per il contratto di ``research/src/gruppo.py`` (regole in ``regole.md`` di questa cartella).

E' un modulo «della variante» come quelli della sessione di gruppo: ``gruppo.py`` lo esegue per percorso dai suoi
byte, da capo per ogni moneta, e chiama le quattro funzioni del contratto (docstring di ``gruppo.py``, punti 1-2).
Importa solo la libreria standard, numpy e ``research.src.motore`` (il controllo degli import e' sul testo), non
legge file, non tiene stato fuori dalle sue istanze. ``p`` e' ``{"regola": <una di REGOLE>, "direzione": "long" |
"short"}``; il timeframe (``"1h"`` o ``"4h"``) arriva da ``ctx.timeframe``.

Le regole d'ingresso da manuale e le uscite sono quelle della prova del 9 ottobre (``taratura/placebo/regole.md``,
punti 3.1 e 3.3; ``taratura/placebo/placebo.py``), adattate al contratto di gruppo:

* **ingresso** (solo in ``crea_variante``): la regola calcolata alla chiusura della barra i con le barre 0..i;
  ``segnali_regola`` e' il calcolo vettoriale (lo stesso della prova del 9 ottobre, usato da ``esegui.py`` per gli
  istanti di segnale), ``_Regola`` lo stesso calcolo una barra alla volta, con la stessa aritmetica (stessi
  risultati bit per bit: lo prova ``test_placebo_gruppo.py``). Nessun segnale nelle prime ``RISCALDAMENTO`` (60)
  barre della serie (regole.md, punto 3.4);
* **segnale** (stop e target): ATR(14) alla barra di segnale, media semplice degli ultimi 14 true range (barre
  i - 13 .. i; il true range della barra k usa la chiusura di k - 1). Per incrocio delle medie, rottura e MACD stop
  a 1,5 ATR e target a 2,5 ATR; per RSI, Bollinger e momento stop a 2 ATR e nessun target. None (segnale non
  calcolabile) nel riscaldamento e dove l'ATR non e' un numero positivo;
* **uscita**: per RSI, Bollinger e momento «chiudi» alla chiusura della barra in cui la posizione e' tenuta da
  ``BARRE_USCITA_TEMPO`` barre (24 a 1 ora, 12 a 4 ore), contate nella serie (un buco nei dati non allunga la
  posizione), quindi l'uscita e' all'apertura della barra dopo, come il 9 ottobre; per le altre tre solo stop e
  target.

Scelta numerica documentata: l'ATR qui e' ``math.fsum`` dei 14 true range diviso 14, calcolato alla barra; la prova
del 9 ottobre lo calcolava con le somme cumulate dell'intera serie (``_sma``), che differiscono nelle ultime cifre
(sulle serie sintetiche dei test l'errore relativo e' dell'ordine di 1e-13; il test lo tiene sotto 1e-10). Per i segnali d'ingresso invece si usa la stessa aritmetica
del 9 ottobre, perche' un segnale e' un confronto e deve coincidere.

Le quattro funzioni del contratto: ``crea_variante`` (la regola completa: serve al controllo del contratto e al test
che confronta la regola come variante con la stessa data come ``ingressi_placebo``; nella prova la placebo passa
sempre da ``ingressi_placebo``), ``crea_a`` (entra a ogni barra libera dalla barra 60), ``crea_casuale`` (entra alle
barre di ``ingressi``) e ``crea_segnale`` (il segnale senza la condizione d'ingresso).
"""

from __future__ import annotations

import math

import numpy as np

from research.src.motore import Segnale

#: barre iniziali di ogni serie senza segnali (regole.md, punto 3.4; SMA50 e MACD 26 + 9 sono pronti prima)
RISCALDAMENTO = 60
#: le sei regole d'ingresso da manuale (regole.md, punto 3.1) e la loro uscita (punto 3.3)
REGOLE = ("incrocio_medie", "rsi", "rottura_20", "bollinger", "macd", "momento_10")
USCITA_DELLA_REGOLA = {
    "incrocio_medie": "atr", "rottura_20": "atr", "macd": "atr",
    "rsi": "tempo", "bollinger": "tempo", "momento_10": "tempo",
}
USCITE = ("atr", "tempo")
DIREZIONI = ("long", "short")
TIMEFRAME = ("1h", "4h")
MS_BARRA = {"1h": 3_600_000, "4h": 14_400_000}
#: uscita a tempo: barre tenute (un giorno a 1 ora, due giorni a 4 ore)
BARRE_USCITA_TEMPO = {"1h": 24, "4h": 12}
#: barre dell'ATR (media semplice dei true range)
BARRE_ATR = 14
#: stop e target in ATR per tipo di uscita: (stop, target o None)
MULTIPLI_ATR = {"atr": (1.5, 2.5), "tempo": (2.0, None)}


# ---------------------------------------------------------------------------
# Il calcolo vettoriale delle regole (lo stesso di taratura/placebo/placebo.py)
# ---------------------------------------------------------------------------


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


def _rsi(close: np.ndarray, n: int = 14) -> np.ndarray:
    out = np.full(close.size, np.nan)
    if close.size <= n:
        return out
    d = np.diff(close)
    su, giu = np.clip(d, 0, None), np.clip(-d, 0, None)
    m_su, m_giu = su[:n].mean(), giu[:n].mean()
    for i in range(n, close.size):
        if i > n:
            m_su = (m_su * (n - 1) + su[i - 1]) / n
            m_giu = (m_giu * (n - 1) + giu[i - 1]) / n
        out[i] = 100.0 if m_giu == 0 else 100.0 - 100.0 / (1.0 + m_su / m_giu)
    return out


def segnali_regola(candele, regola: str, direzione: str) -> np.ndarray:
    """Maschera booleana delle barre in cui la regola da manuale scatta, alla chiusura della barra.

    Copia del calcolo di ``taratura/placebo/placebo.py`` (prova del 9 ottobre), CAUSALE: il valore alla barra i usa
    solo le barre 0..i. Il riscaldamento (prime ``RISCALDAMENTO`` barre) NON e' tolto qui: lo toglie chi usa la
    maschera, come il 9 ottobre.
    """
    if regola not in REGOLE or direzione not in DIREZIONI:
        raise ValueError(f"regola o direzione sconosciuta: {regola!r}, {direzione!r}")
    close = np.array([c.close for c in candele], dtype=float)
    high = np.array([c.high for c in candele], dtype=float)
    low = np.array([c.low for c in candele], dtype=float)
    n = close.size
    s = np.zeros(n, dtype=bool)
    lungo = direzione == "long"
    with np.errstate(invalid="ignore"):
        if regola == "incrocio_medie":
            a, b = _sma(close, 20), _sma(close, 50)
            sopra = a > b
            s[1:] = (sopra[1:] & ~sopra[:-1]) if lungo else (~sopra[1:] & sopra[:-1])
            s &= ~np.isnan(b)
            s[1:] &= ~np.isnan(b[:-1])
        elif regola == "rsi":
            r = _rsi(close, 14)
            if lungo:
                s[1:] = (r[:-1] < 30) & (r[1:] >= 30)
            else:
                s[1:] = (r[:-1] > 70) & (r[1:] <= 70)
        elif regola == "rottura_20":
            for i in range(20, n):
                if lungo:
                    s[i] = close[i] > high[i - 20:i].max()
                else:
                    s[i] = close[i] < low[i - 20:i].min()
        elif regola == "bollinger":
            m = _sma(close, 20)
            sd = np.full(n, np.nan)
            for i in range(19, n):
                sd[i] = close[i - 19:i + 1].std()
            s = (close < m - 2 * sd) if lungo else (close > m + 2 * sd)
        elif regola == "macd":
            linea = _ema(close, 12) - _ema(close, 26)
            valida = ~np.isnan(linea)
            seg = np.full(n, np.nan)
            if valida.sum() >= 9:
                primo = int(np.argmax(valida))
                seg[primo:] = _ema(linea[primo:], 9)
            sopra = linea > seg
            pronto = ~np.isnan(seg)
            s[1:] = ((sopra[1:] & ~sopra[:-1]) if lungo else (~sopra[1:] & sopra[:-1])) & pronto[1:] & pronto[:-1]
        elif regola == "momento_10":
            roc = np.full(n, np.nan)
            roc[10:] = close[10:] / close[:-10] - 1.0
            pos = roc > 0
            neg = roc < 0
            pronto = ~np.isnan(roc)
            if lungo:
                s[1:] = pos[1:] & ~pos[:-1] & pronto[:-1]
            else:
                s[1:] = neg[1:] & ~neg[:-1] & pronto[:-1]
    return np.asarray(s, dtype=bool)


# ---------------------------------------------------------------------------
# La stessa regola una barra alla volta (per crea_variante)
# ---------------------------------------------------------------------------


def _maggiore(a: float, b: float) -> bool:
    """``a > b`` con la lettura di numpy: un NaN da' False."""
    return (not math.isnan(a)) and (not math.isnan(b)) and a > b


class _Regola:
    """La regola da manuale aggiornata barra per barra, con la stessa aritmetica di ``segnali_regola``.

    ``aggiungi(barra)`` riceve la barra i (le barre arrivano in ordine, una volta sola) e dice se la regola scatta
    alla sua chiusura. Le somme cumulate, le medie iniziali (``np.mean`` sugli stessi valori), le ricorsioni e
    ``np.std`` sono quelle del calcolo vettoriale: i confronti escono uguali.
    """

    def __init__(self, regola: str, direzione: str) -> None:
        if regola not in REGOLE or direzione not in DIREZIONI:
            raise ValueError(f"regola o direzione sconosciuta: {regola!r}, {direzione!r}")
        self.regola = regola
        self.lungo = direzione == "long"
        self.close: list = []
        self.high: list = []
        self.low: list = []
        self.cumulata = [0.0]  # come np.cumsum(np.insert(close, 0, 0.0))
        self.prec_sopra = False
        self.prec_b_valida = False
        self.prec_pronto = False
        self.prec_r = math.nan
        self.m_su = self.m_giu = math.nan
        self.e12 = self.e26 = self.segnale = math.nan
        self.linee: list = []  # la linea del MACD dalla prima barra in cui esiste
        self.calcolo = getattr(self, "_" + regola)

    def _media_mobile(self, i: int, n: int) -> float:
        if i < n - 1:
            return math.nan
        return (self.cumulata[i + 1] - self.cumulata[i + 1 - n]) / n

    def aggiungi(self, barra) -> bool:
        i = len(self.close)
        self.close.append(float(barra.close))
        self.high.append(float(barra.high))
        self.low.append(float(barra.low))
        self.cumulata.append(self.cumulata[-1] + self.close[-1])
        return bool(self.calcolo(i))

    def _incrocio_medie(self, i: int) -> bool:
        a, b = self._media_mobile(i, 20), self._media_mobile(i, 50)
        sopra = _maggiore(a, b)
        b_valida = not math.isnan(b)
        scatta = False
        if i >= 1 and b_valida and self.prec_b_valida:
            scatta = (sopra and not self.prec_sopra) if self.lungo else ((not sopra) and self.prec_sopra)
        self.prec_sopra, self.prec_b_valida = sopra, b_valida
        return scatta

    def _rsi(self, i: int, n: int = 14) -> bool:
        r = math.nan
        if i == n:
            d = np.diff(np.array(self.close[:n + 1], dtype=float))
            self.m_su = np.clip(d, 0, None)[:n].mean()
            self.m_giu = np.clip(-d, 0, None)[:n].mean()
        elif i > n:
            d = self.close[i] - self.close[i - 1]
            self.m_su = (self.m_su * (n - 1) + max(d, 0.0)) / n
            self.m_giu = (self.m_giu * (n - 1) + max(-d, 0.0)) / n
        if i >= n:
            r = 100.0 if self.m_giu == 0 else 100.0 - 100.0 / (1.0 + self.m_su / self.m_giu)
        prec, self.prec_r = self.prec_r, r
        if i < 1 or math.isnan(r) or math.isnan(prec):
            return False
        return (prec < 30 and r >= 30) if self.lungo else (prec > 70 and r <= 70)

    def _rottura_20(self, i: int) -> bool:
        if i < 20:
            return False
        if self.lungo:
            return self.close[i] > max(self.high[i - 20:i])
        return self.close[i] < min(self.low[i - 20:i])

    def _bollinger(self, i: int) -> bool:
        if i < 19:
            return False
        m = self._media_mobile(i, 20)
        sd = np.array(self.close[i - 19:i + 1], dtype=float).std()
        if self.lungo:
            return bool(self.close[i] < m - 2 * sd)
        return bool(self.close[i] > m + 2 * sd)

    @staticmethod
    def _ema_passo(n: int, x: float, prima: float) -> float:
        a = 2.0 / (n + 1)
        return a * x + (1 - a) * prima

    def _macd(self, i: int) -> bool:
        if i == 11:
            self.e12 = np.array(self.close[:12], dtype=float).mean()
        elif i > 11:
            self.e12 = self._ema_passo(12, self.close[i], self.e12)
        if i == 25:
            self.e26 = np.array(self.close[:26], dtype=float).mean()
        elif i > 25:
            self.e26 = self._ema_passo(26, self.close[i], self.e26)
        linea = self.e12 - self.e26 if i >= 25 else math.nan
        if i >= 25:
            self.linee.append(linea)
        if len(self.linee) == 9 and i >= 25:
            self.segnale = np.array(self.linee[:9], dtype=float).mean()
        elif len(self.linee) > 9:
            self.segnale = self._ema_passo(9, linea, self.segnale)
        pronto = len(self.linee) >= 9
        sopra = _maggiore(linea, self.segnale) if pronto else False
        scatta = False
        if i >= 1 and pronto and self.prec_pronto:
            scatta = (sopra and not self.prec_sopra) if self.lungo else ((not sopra) and self.prec_sopra)
        self.prec_sopra, self.prec_pronto = sopra, pronto
        return scatta

    def _momento_10(self, i: int) -> bool:
        pronto = i >= 10
        roc = self.close[i] / self.close[i - 10] - 1.0 if pronto else math.nan
        sopra = (roc > 0) if self.lungo else (roc < 0)  # un NaN da' False
        scatta = bool(i >= 1 and sopra and not self.prec_sopra and self.prec_pronto)
        self.prec_sopra, self.prec_pronto = bool(sopra), pronto
        return scatta


# ---------------------------------------------------------------------------
# Segnale e uscita (regole.md, punto 3.3)
# ---------------------------------------------------------------------------


def atr_alla_barra(storia, i: int) -> float:
    """ATR(14) alla barra i: media semplice dei true range delle barre i - 13 .. i (NaN se i < 14).

    True range della barra k: il piu' alto fra high - low, |high - chiusura di k - 1| e |low - chiusura di k - 1|.
    Usa solo le barre i - 14 .. i, gia' chiuse.
    """
    if i < BARRE_ATR:
        return math.nan
    barre = storia[i - BARRE_ATR:i + 1]
    tr = []
    for prima, barra in zip(barre[:-1], barre[1:]):
        tr.append(max(barra.high - barra.low, max(abs(barra.high - prima.close), abs(barra.low - prima.close))))
    return math.fsum(tr) / BARRE_ATR


def _segnale_alla_barra(storia, direzione: str, uscita: str):
    """Il segnale della variante SENZA la condizione d'ingresso alla chiusura dell'ultima barra di ``storia``.

    None nel riscaldamento (prime ``RISCALDAMENTO`` barre) e dove l'ATR non e' un numero positivo.
    """
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
    """L'uscita a tempo: «chiudi» quando la posizione e' tenuta da ``barre`` barre, contate nella serie.

    La barra d'ingresso conta come la prima (alla sua chiusura la posizione e' tenuta da una barra): «chiudi» alla
    chiusura della barra numero ``barre`` e uscita all'apertura della successiva. L'indice della barra d'ingresso si
    cerca una volta per posizione, a ritroso nella storia (al piu' ``barre`` + 1 barre).
    """
    stato = {"ts": None, "indice": None}

    def esci(storia, posizione):
        i = len(storia) - 1
        if stato["ts"] != posizione.ts_entrata:
            stato["ts"], stato["indice"] = posizione.ts_entrata, None
            for k in range(i, max(-1, i - barre - 1), -1):
                if storia[k].ts == posizione.ts_entrata:
                    stato["indice"] = k
                    break
        if stato["indice"] is None:  # piu' di ``barre`` + 1 barre fa: gia' oltre il tempo
            return "chiudi"
        return "chiudi" if i - stato["indice"] + 1 >= barre else None

    return esci


def _leggi_p(ctx, p):
    """Regola, direzione, uscita e barre dell'uscita a tempo da ``p`` e da ``ctx.timeframe`` (ValueError se no)."""
    regola, direzione = p.get("regola"), p.get("direzione")
    if regola not in REGOLE or direzione not in DIREZIONI:
        raise ValueError(f"p deve avere regola in {REGOLE} e direzione in {DIREZIONI}: {p!r}")
    if ctx.timeframe not in BARRE_USCITA_TEMPO:
        raise ValueError(f"timeframe {ctx.timeframe!r} non previsto dalla prova: {TIMEFRAME}")
    return regola, direzione, USCITA_DELLA_REGOLA[regola], BARRE_USCITA_TEMPO[ctx.timeframe]


def _strategia(direzione: str, uscita: str, barre: int, entra):
    """La strategia: con una posizione l'uscita della regola, senza il segnale dove ``entra(storia)`` e' vero."""
    esci = _uscita_a_tempo(barre) if uscita == "tempo" else None

    def strategia(storia, posizione):
        if posizione is not None:
            return esci(storia, posizione) if esci is not None else None
        if entra(storia):
            return _segnale_alla_barra(storia, direzione, uscita)
        return None

    return strategia


# ---------------------------------------------------------------------------
# Le quattro funzioni del contratto (docstring di research/src/gruppo.py, punto 2)
# ---------------------------------------------------------------------------


def crea_variante(ctx, p):
    """La regola da manuale completa: segnale alla chiusura della barra i >= 60 in cui la regola scatta."""
    regola, direzione, uscita, barre = _leggi_p(ctx, p)

    def crea():
        calcolo = _Regola(regola, direzione)
        scatta: list = []

        def entra(storia):
            for k in range(len(scatta), len(storia)):
                scatta.append(calcolo.aggiungi(storia[k]))
            i = len(storia) - 1
            return i >= RISCALDAMENTO and scatta[i]

        return _strategia(direzione, uscita, barre, entra)

    return crea


def crea_a(ctx, p):
    """La (a): stessa direzione, stop, target e uscita, entra a ogni barra libera dalla barra 60."""
    _, direzione, uscita, barre = _leggi_p(ctx, p)

    def crea():
        return _strategia(direzione, uscita, barre, lambda storia: len(storia) - 1 >= RISCALDAMENTO)

    return crea


def crea_casuale(ctx, p):
    """La strategia casuale: alla chiusura delle barre di ``ingressi`` (indici), se libera, il segnale della variante."""
    _, direzione, uscita, barre = _leggi_p(ctx, p)

    def crea(ingressi):
        ingressi = frozenset(ingressi)
        return _strategia(direzione, uscita, barre, lambda storia: (len(storia) - 1) in ingressi)

    return crea


def crea_segnale(ctx, p):
    """Il segnale senza la condizione d'ingresso (None nel riscaldamento e con l'ATR non positivo)."""
    _, direzione, uscita, _ = _leggi_p(ctx, p)

    def crea():
        def segnale(storia):
            return _segnale_alla_barra(storia, direzione, uscita)

        return segnale

    return crea
