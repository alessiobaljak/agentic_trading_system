"""Le varianti della campagna BTCUSDT: una per combinazione idea/timeframe/direzione.

Ogni variante e' un dizionario con: ``idea``, ``fonte``, ``meccanismo``, ``tf``,
``direzione``, ``parametri`` (dichiarati), ``uscita`` (regole per la fabbrica),
``occupazione`` (barre per trade, per la stima), ``previsione`` (testo) e
``previsione_pf`` (intervallo [min, max] del profit factor, giudicato
meccanicamente), ``criterio_successo``. ``entra(serie)`` costruisce la
funzione di ingresso; ``direzione_di`` e ``ammessa`` servono alla baseline (a).
Le descrizioni complete sono in ipotesi.md.
"""
from __future__ import annotations

from typing import Callable, Dict, Optional

import numpy as np

import strumenti as s

CRITERIO = ("R medio > 0 dopo costi; R medio sopra il 90° percentile delle entrate casuali con la stessa uscita; "
            "differenza netta (> 2 errori standard, bootstrap a blocchi) dalla simulazione mediana e dalla baseline incondizionata; "
            "almeno 100 trade in costruzione")

VARIANTI: Dict[str, Dict[str, object]] = {}


def _reg(id_: str, **kw):
    kw["id"] = id_
    VARIANTI[id_] = kw


# --------------------------------------------------------------------------- I-01
def _entra_canale(serie: s.Serie, n: int, direzione: str):
    mx, mn = serie.max_precedente(n), serie.min_precedente(n)
    c = serie.c
    if direzione == "long":
        return lambda i: "long" if (np.isfinite(mx[i]) and c[i] > mx[i]) else None
    return lambda i: "short" if (np.isfinite(mn[i]) and c[i] < mn[i]) else None


def _chiudi_canale(serie: s.Serie, m: int):
    mx, mn = serie.max_precedente(m), serie.min_precedente(m)
    c = serie.c

    def chiudi(i: int, pos) -> bool:
        if pos.direzione == "long":
            return bool(np.isfinite(mn[i]) and c[i] < mn[i])
        return bool(np.isfinite(mx[i]) and c[i] > mx[i])
    return chiudi


for _dir in ("long", "short"):
    _reg(f"BTCUSDT-V01-{_dir}" if _dir == "long" else "BTCUSDT-V02-short",
         idea="I-01", tf="4h", direzione=_dir,
         fonte="Gerritsen, Bouri, Ramezanifar, Roubaud, 'The profitability of technical trading rules in the Bitcoin market', Finance Research Letters 34, 2020; Brock, Lakonishok, LeBaron, 'Simple Technical Trading Rules and the Stochastic Properties of Stock Returns', Journal of Finance 47(5), 1992",
         meccanismo="continuazione dopo la rottura del canale di 30 barre (seguaci del trend e stop di chi era contro)",
         parametri={"canale_ingresso_barre": 30, "canale_uscita_barre": 15, "stop_atr": 2.0, "atr_n": 14, "max_barre": 60},
         entra=(lambda serie, d=_dir: _entra_canale(serie, 30, d)),
         uscita=(lambda serie: {"stop_atr": 2.0, "atr_n": 14, "max_barre": 60, "chiudi": _chiudi_canale(serie, 15)}),
         direzione_di=(lambda serie, d=_dir: (lambda i: d)),
         occupazione=15,
         previsione=("long: PF 0,95-1,20, R medio 0/+0,10, 120-180 trade, non netto sul caso long" if _dir == "long" else "short: PF 0,80-1,00, R medio negativo"),
         previsione_pf=([0.95, 1.20] if _dir == "long" else [0.80, 1.00]),
         criterio_successo=CRITERIO)

# --------------------------------------------------------------------------- I-02
def _entra_momentum(serie: s.Serie, n: int, direzione: str):
    r = serie.rendimento(n)
    if direzione == "long":
        return lambda i: "long" if (np.isfinite(r[i]) and r[i] > 0) else None
    return lambda i: "short" if (np.isfinite(r[i]) and r[i] < 0) else None


for _id, _dir in (("BTCUSDT-V03-long", "long"), ("BTCUSDT-V04-short", "short")):
    _reg(_id, idea="I-02", tf="1d", direzione=_dir,
         fonte="Moskowitz, Ooi, Pedersen, 'Time Series Momentum', Journal of Financial Economics 104(2), 2012; Liu, Tsyvinski, 'Risks and Returns of Cryptocurrency', Review of Financial Studies 34(6), 2021",
         meccanismo="continuazione del rendimento a 7 giorni (diffusione lenta, herding)",
         parametri={"finestra_giorni": 7, "stop_atr": 2.0, "atr_n": 14, "max_barre": 7},
         entra=(lambda serie, d=_dir: _entra_momentum(serie, 7, d)),
         uscita=(lambda serie: {"stop_atr": 2.0, "atr_n": 14, "max_barre": 7}),
         direzione_di=(lambda serie, d=_dir: (lambda i: d)),
         occupazione=7,
         previsione=("long: PF 1,00-1,25, 110-130 trade, R medio 0/+0,15, non netto sul caso long" if _dir == "long" else "short: PF 0,85-1,05"),
         previsione_pf=([1.00, 1.25] if _dir == "long" else [0.85, 1.05]),
         criterio_successo=CRITERIO)

# --------------------------------------------------------------------------- I-03
def _entra_intraday(serie: s.Serie, direzione: str, soglia: float = 0.0):
    o, c, ora, minuto, giorno = serie.o, serie.c, serie.ora, serie.minuto, serie.giorno

    def entra(i: int):
        if ora[i] != 23 or minuto[i] != 0 or i < 46:
            return None
        j = i - 46
        if ora[j] != 0 or minuto[j] != 0 or giorno[j] != giorno[i]:
            return None
        r0 = c[j] / o[j] - 1
        if direzione == "long" and r0 > soglia:
            return "long"
        if direzione == "short" and r0 < -soglia:
            return "short"
        return None
    return entra


def _ammessa_2300(serie: s.Serie):
    ora, minuto = serie.ora, serie.minuto
    return lambda i: bool(ora[i] == 23 and minuto[i] == 0)


for _id, _dir in (("BTCUSDT-V05-long", "long"), ("BTCUSDT-V06-short", "short")):
    _reg(_id, idea="I-03", tf="30m", direzione=_dir,
         fonte="Shen, Urquhart, Wang, 'Bitcoin intraday time series momentum', Financial Review 57(2), 2022; Gao, Han, Li, Zhou, 'Intraday momentum', Journal of Financial Economics 129(2), 2018",
         meccanismo="ribilanciamento di fine giornata UTC nella direzione della prima mezz'ora",
         parametri={"barra_segnale": "23:00-23:30 UTC", "barra_predittiva": "00:00-00:30 UTC", "stop_atr": 2.0, "atr_n": 14, "max_barre": 1},
         entra=(lambda serie, d=_dir: _entra_intraday(serie, d)),
         uscita=(lambda serie: {"stop_atr": 2.0, "atr_n": 14, "max_barre": 1}),
         direzione_di=(lambda serie, d=_dir: (lambda i: d)),
         ammessa=_ammessa_2300,
         occupazione=1,
         previsione=f"{_dir}: ~500 trade, PF 0,85-1,00 dopo costi, R medio negativo: effetto lordo piccolo mangiato dai costi",
         previsione_pf=[0.85, 1.00],
         criterio_successo=CRITERIO)

# --------------------------------------------------------------------------- I-04
def _percentile_precedente(arr: np.ndarray, n: int, q: float) -> np.ndarray:
    """q-esimo percentile delle n osservazioni PRIMA di i (esclusa i)."""
    out = np.full(arr.shape, np.nan)
    for i in range(n, arr.size):
        w = arr[i - n:i]
        if np.all(np.isfinite(w)):
            out[i] = np.percentile(w, q)
    return out


def _entra_funding(serie: s.Serie, direzione: str, q: float = 90.0, n: int = 270):
    f = serie.funding_ultimo()
    if direzione == "short":
        soglia = _percentile_precedente(f, n, q)
        return lambda i: "short" if (np.isfinite(soglia[i]) and np.isfinite(f[i]) and f[i] > soglia[i]) else None
    soglia = _percentile_precedente(f, n, 100.0 - q)
    return lambda i: "long" if (np.isfinite(soglia[i]) and np.isfinite(f[i]) and f[i] < soglia[i]) else None


for _id, _dir in (("BTCUSDT-V07-short", "short"), ("BTCUSDT-V08-long", "long")):
    _reg(_id, idea="I-04", tf="8h", direzione=_dir,
         fonte="Schmeling, Schrimpf, Todorov, 'Crypto Carry', BIS Working Papers 1087, aprile 2023; He, Manela, Ross, von Wachter, 'Fundamentals of Perpetual Futures', arXiv 2212.06888, dicembre 2022",
         meccanismo="rientro di un posizionamento affollato segnalato dal funding estremo (decile su 90 giorni)",
         parametri={"percentile": 90 if _dir == "short" else 10, "finestra_settlement": 270, "stop_atr": 2.0, "atr_n": 14, "max_barre": 3, "funding_usato": "ultimo settlement avvenuto entro la chiusura della barra"},
         entra=(lambda serie, d=_dir: _entra_funding(serie, d)),
         uscita=(lambda serie: {"stop_atr": 2.0, "atr_n": 14, "max_barre": 3}),
         direzione_di=(lambda serie, d=_dir: (lambda i: d)),
         occupazione=3,
         previsione=("short: 80-150 trade, PF 0,90-1,15, R medio -0,05/+0,10, funding incassato ~0,03-0,05 R a trade" if _dir == "short" else "long: 40-90 trade (forse sotto il minimo), PF 0,9-1,1"),
         previsione_pf=([0.90, 1.15] if _dir == "short" else [0.90, 1.10]),
         criterio_successo=CRITERIO)

# --------------------------------------------------------------------------- I-05
def _entra_lunedi(serie: s.Serie):
    gs = serie.giorno_settimana
    return lambda i: "long" if gs[i] == 6 else None  # chiusura della domenica -> ingresso apertura lunedi'


_reg("BTCUSDT-V09-long", idea="I-05", tf="1d", direzione="long",
     fonte="Aharon, Qadan, 'Bitcoin and the day-of-the-week effect', Economic Modelling 82, 2019; Baur, Cahill, Godfrey, Liu, 'Bitcoin time-of-day, day-of-week and month-of-year effects in returns and trading volume', Finance Research Letters 31, 2019; Kaiser, 'Seasonality in cryptocurrencies', Finance Research Letters 31, 2019",
     meccanismo="flussi di inizio settimana (riapertura dei mercati tradizionali, notizie del fine settimana)",
     parametri={"giorno": "lunedi' UTC", "stop_atr": 2.0, "atr_n": 14, "max_barre": 1},
     entra=_entra_lunedi,
     uscita=(lambda serie: {"stop_atr": 2.0, "atr_n": 14, "max_barre": 1}),
     direzione_di=(lambda serie: (lambda i: "long")),
     occupazione=1,
     previsione="~145 trade, PF 0,90-1,20, R medio -0,05/+0,10, non netto sul caso",
     previsione_pf=[0.90, 1.20],
     criterio_successo=CRITERIO)

# --------------------------------------------------------------------------- I-06
def _entra_anomalo(serie: s.Serie, direzione: str, k: float = 1.0, n: int = 30):
    r = serie.rendimento(1)
    ar = np.abs(r)
    media = s.shift(s.sma(ar, n), 1)
    std = s.shift(s.rolling_std(ar, n), 1)
    soglia = media + k * std

    def entra(i: int):
        if not (np.isfinite(soglia[i]) and np.isfinite(r[i])) or ar[i] <= soglia[i]:
            return None
        if direzione == "long" and r[i] > 0:
            return "long"
        if direzione == "short" and r[i] < 0:
            return "short"
        return None
    return entra


for _id, _dir in (("BTCUSDT-V10-long", "long"), ("BTCUSDT-V11-short", "short")):
    _reg(_id, idea="I-06", tf="1d", direzione=_dir,
         fonte="Caporale, Plastun, 'Price overreactions in the cryptocurrency market', Journal of Economic Studies 46(5), 2019",
         meccanismo="continuazione il giorno dopo un movimento anomalo (reazione in ritardo, liquidazioni a catena)",
         parametri={"soglia": "media + 1 deviazione standard dei |rendimenti| dei 30 giorni precedenti", "stop_atr": 2.0, "atr_n": 14, "max_barre": 1},
         entra=(lambda serie, d=_dir: _entra_anomalo(serie, d)),
         uscita=(lambda serie: {"stop_atr": 2.0, "atr_n": 14, "max_barre": 1}),
         direzione_di=(lambda serie, d=_dir: (lambda i: d)),
         occupazione=1,
         previsione=f"{_dir}: 50-90 trade (forse sotto il minimo), PF 0,9-1,1",
         previsione_pf=[0.90, 1.10],
         criterio_successo=CRITERIO)


# =========================================================================== secondo blocco
# --------------------------------------------------------------------------- I-04b
def _entra_funding_negativo(serie: s.Serie):
    f = serie.funding_ultimo()
    return lambda i: "long" if (np.isfinite(f[i]) and f[i] < 0) else None


_reg("BTCUSDT-V12-long", idea="I-04b", tf="8h", direzione="long",
     fonte="come I-04: Schmeling, Schrimpf, Todorov, 'Crypto Carry', BIS WP 1087, 2023; He, Manela, Ross, von Wachter, 'Fundamentals of Perpetual Futures', arXiv 2212.06888, 2022. Variante nata dalla Fase 3 di V08",
     meccanismo="posizionamento netto corto (gli short pagano i long) seguito da rimbalzo",
     parametri={"condizione": "ultimo settlement entro la chiusura con tasso < 0", "stop_atr": 2.0, "atr_n": 14, "max_barre": 3},
     entra=_entra_funding_negativo,
     uscita=(lambda serie: {"stop_atr": 2.0, "atr_n": 14, "max_barre": 3}),
     direzione_di=(lambda serie: (lambda i: "long")),
     occupazione=3,
     previsione="100-140 trade, PF 1,2-1,6, R medio +0,05/+0,12; percentile > 90 ma differenza forse non netta",
     previsione_pf=[1.2, 1.6], criterio_successo=CRITERIO)

# --------------------------------------------------------------------------- I-04 short 85°
_reg("BTCUSDT-V13-short", idea="I-04", tf="8h", direzione="short",
     fonte="Schmeling, Schrimpf, Todorov, 'Crypto Carry', BIS Working Papers 1087, aprile 2023; He, Manela, Ross, von Wachter, 'Fundamentals of Perpetual Futures', arXiv 2212.06888, dicembre 2022",
     meccanismo="rientro di un posizionamento affollato segnalato dal funding alto (85° percentile su 90 giorni)",
     parametri={"percentile": 85, "finestra_settlement": 270, "stop_atr": 2.0, "atr_n": 14, "max_barre": 3},
     entra=(lambda serie: _entra_funding(serie, "short", q=85.0)),
     uscita=(lambda serie: {"stop_atr": 2.0, "atr_n": 14, "max_barre": 3}),
     direzione_di=(lambda serie: (lambda i: "short")),
     occupazione=3,
     previsione="100-130 trade, PF 0,9-1,1, R medio ~0",
     previsione_pf=[0.9, 1.1], criterio_successo=CRITERIO)

# --------------------------------------------------------------------------- I-07
def _prima_barra_del_giorno(serie: s.Serie, ora_inizio: int = 0):
    """Per ogni barra i, l'indice j della barra ``ora_inizio`` del suo giorno (UTC); -1 se manca."""
    ora, giorno = serie.ora, serie.giorno
    primo = {}
    for i in range(serie.n):
        if ora[i] == ora_inizio:
            primo[int(giorno[i])] = i
    out = np.full(serie.n, -1, dtype=np.int64)
    for i in range(serie.n):
        g = int(giorno[i]) if ora[i] >= ora_inizio else int(giorno[i]) - 1
        out[i] = primo.get(g, -1)
    return out


def _prima_rottura(serie: s.Serie, ora_inizio: int = 0):
    """lato[i] = +1/-1 se i e' la PRIMA barra del giorno (dopo la prima ora) con close fuori dall'intervallo della prima ora; 0 altrimenti."""
    j_di = _prima_barra_del_giorno(serie, ora_inizio)
    h, l, c = serie.h, serie.l, serie.c
    lato = np.zeros(serie.n, dtype=np.int64)
    gia = set()
    for i in range(serie.n):
        j = j_di[i]
        if j < 0 or j >= i or (i - j) > 22 or j in gia:
            continue
        if c[i] > h[j]:
            lato[i] = 1; gia.add(j)
        elif c[i] < l[j]:
            lato[i] = -1; gia.add(j)
    return lato, j_di


def _entra_orb(serie: s.Serie, direzione: str, ora_inizio: int = 0):
    lato, _ = _prima_rottura(serie, ora_inizio)
    voluto = 1 if direzione == "long" else -1
    return lambda i: direzione if lato[i] == voluto else None


def _uscita_orb(serie: s.Serie, ora_inizio: int = 0):
    """Stop all'estremo opposto della prima ora (almeno 1 ATR dal close); «chiudi» alla chiusura della barra prima dell'ora di inizio."""
    _, j_di = _prima_rottura(serie, ora_inizio)
    atr = serie.atr(14)
    h, l, c, ora = serie.h, serie.l, serie.c, serie.ora

    def stop_fn(i: int, direzione: str):
        j = j_di[i]
        a = atr[i]
        if j < 0 or not np.isfinite(a):
            return None
        return min(l[j], c[i] - a) if direzione == "long" else max(h[j], c[i] + a)

    def chiudi(i: int, pos) -> bool:
        return bool(ora[i] == (ora_inizio - 1) % 24)
    return {"stop_fn": stop_fn, "atr_n": 14, "chiudi": chiudi}


for _id, _dir in (("BTCUSDT-V14-long", "long"), ("BTCUSDT-V15-short", "short")):
    _reg(_id, idea="I-07", tf="1h", direzione=_dir,
         fonte="Crabel, 'Day Trading with Short Term Price Patterns and Opening Range Breakout', 1990",
         meccanismo="la rottura dell'intervallo della prima ora del giorno UTC anticipa la direzione del giorno",
         parametri={"prima_ora": "00:00-01:00 UTC", "stop": "estremo opposto della prima ora, almeno 1 ATR(14) dal close del segnale", "uscita": "chiusura della barra 23:00 (apertura 00:00)", "un_trade_al_giorno": True},
         entra=(lambda serie, d=_dir: _entra_orb(serie, d)),
         uscita=(lambda serie: _uscita_orb(serie)),
         direzione_di=(lambda serie, d=_dir: (lambda i: d)),
         occupazione=12,
         previsione=f"{_dir}: 400-600 trade, PF 0,85-1,05, R medio <= 0",
         previsione_pf=[0.85, 1.05], criterio_successo=CRITERIO)

# --------------------------------------------------------------------------- I-08
def _entra_rsi2(serie: s.Serie, direzione: str, soglia: float = 10.0, n_sma: int = 200):
    rsi, sma200, c = serie.rsi(2), s.sma(serie.c, n_sma), serie.c
    if direzione == "long":
        return lambda i: "long" if (np.isfinite(rsi[i]) and np.isfinite(sma200[i]) and c[i] > sma200[i] and rsi[i] < soglia) else None
    return lambda i: "short" if (np.isfinite(rsi[i]) and np.isfinite(sma200[i]) and c[i] < sma200[i] and rsi[i] > 100 - soglia) else None


def _chiudi_rsi2(serie: s.Serie, uscita_long: float = 60.0):
    rsi = serie.rsi(2)

    def chiudi(i: int, pos) -> bool:
        if pos.direzione == "long":
            return bool(np.isfinite(rsi[i]) and rsi[i] > uscita_long)
        return bool(np.isfinite(rsi[i]) and rsi[i] < 100 - uscita_long)
    return chiudi


for _id, _dir in (("BTCUSDT-V16-long", "long"), ("BTCUSDT-V17-short", "short")):
    _reg(_id, idea="I-08", tf="4h", direzione=_dir,
         fonte="Connors, Alvarez, 'Short Term Trading Strategies That Work', TradingMarkets Publishing, 2009; Wilder, 'New Concepts in Technical Trading Systems', 1978",
         meccanismo="fornitura di liquidita' dopo un ritracciamento di 2 barre dentro il trend (media a 200 barre)",
         parametri={"rsi_periodi": 2, "soglia_ingresso": 10 if _dir == "long" else 90, "soglia_uscita": 60 if _dir == "long" else 40, "sma": 200, "stop_atr": 2.0, "atr_n": 14, "max_barre": 10},
         entra=(lambda serie, d=_dir: _entra_rsi2(serie, d)),
         uscita=(lambda serie: {"stop_atr": 2.0, "atr_n": 14, "max_barre": 10, "chiudi": _chiudi_rsi2(serie)}),
         direzione_di=(lambda serie, d=_dir: (lambda i: d)),
         occupazione=10,
         previsione=("long: 150-250 trade, PF 1,0-1,3, R medio 0/+0,10, non netto sul caso long" if _dir == "long" else "short: 100-200 trade, PF 0,8-1,0"),
         previsione_pf=([1.0, 1.3] if _dir == "long" else [0.8, 1.0]), criterio_successo=CRITERIO)

# --------------------------------------------------------------------------- I-09
def _entra_volume(serie: s.Serie, q: float = 90.0, n: int = 50):
    soglia = _percentile_precedente(serie.v, n, q)
    v = serie.v
    return lambda i: "long" if (np.isfinite(soglia[i]) and v[i] > soglia[i]) else None


_reg("BTCUSDT-V18-long", idea="I-09", tf="1d", direzione="long",
     fonte="Gervais, Kaniel, Mingelgrin, 'The High-Volume Return Premium', Journal of Finance 56(3), 2001",
     meccanismo="attenzione attirata dal volume anomalo, seguita da acquisti",
     parametri={"percentile_volume": 90, "finestra_giorni": 50, "stop_atr": 2.0, "atr_n": 14, "max_barre": 5},
     entra=_entra_volume,
     uscita=(lambda serie: {"stop_atr": 2.0, "atr_n": 14, "max_barre": 5}),
     direzione_di=(lambda serie: (lambda i: "long")),
     occupazione=5,
     previsione="60-80 trade stimati: probabile scarto; se si testa PF 0,9-1,2",
     previsione_pf=[0.9, 1.2], criterio_successo=CRITERIO)

# --------------------------------------------------------------------------- I-10
def _entra_squeeze(serie: s.Serie, direzione: str, n: int = 20, k: float = 2.0, finestra: int = 120):
    m, sd = s.sma(serie.c, n), s.rolling_std(serie.c, n)
    alta, bassa = m + k * sd, m - k * sd
    ampiezza = (alta - bassa) / m
    minimo_prec = s.shift(s.rolling_min(ampiezza, finestra), 1)
    amp_prec = s.shift(ampiezza, 1)
    c = serie.c

    def entra(i: int):
        if not (np.isfinite(minimo_prec[i]) and np.isfinite(amp_prec[i])) or amp_prec[i] > minimo_prec[i]:
            return None
        if direzione == "long" and c[i] > alta[i]:
            return "long"
        if direzione == "short" and c[i] < bassa[i]:
            return "short"
        return None
    return entra


for _id, _dir in (("BTCUSDT-V19-long", "long"), ("BTCUSDT-V20-short", "short")):
    _reg(_id, idea="I-10", tf="4h", direzione=_dir,
         fonte="Bollinger, 'Bollinger on Bollinger Bands', McGraw-Hill, 2001",
         meccanismo="espansione della volatilita' dopo la compressione, nella direzione della prima rottura",
         parametri={"bande": "SMA 20, 2 deviazioni standard", "finestra_minimo_ampiezza": 120, "stop_atr": 2.0, "atr_n": 14, "max_barre": 20},
         entra=(lambda serie, d=_dir: _entra_squeeze(serie, d)),
         uscita=(lambda serie: {"stop_atr": 2.0, "atr_n": 14, "max_barre": 20}),
         direzione_di=(lambda serie, d=_dir: (lambda i: d)),
         occupazione=20,
         previsione=f"{_dir}: 20-50 trade stimati: probabile scarto",
         previsione_pf=[0.8, 1.2], criterio_successo=CRITERIO)


# =========================================================================== terzo blocco
# --------------------------------------------------------------------------- I-11
def _entra_bassa_vol(serie: s.Serie, n_vol: int = 20, n_med: int = 120):
    r = serie.rendimento(1)
    vol = s.rolling_std(r, n_vol)
    mediana_prec = s.shift(_rolling_mediana(vol, n_med), 1)
    return lambda i: "long" if (np.isfinite(vol[i]) and np.isfinite(mediana_prec[i]) and vol[i] < mediana_prec[i]) else None


def _rolling_mediana(arr: np.ndarray, n: int) -> np.ndarray:
    return s._rolling_apply(arr, n, lambda w, axis: np.nanmedian(w, axis=axis))


_reg("BTCUSDT-V21-long", idea="I-11", tf="1d", direzione="long",
     fonte="Moreira, Muir, 'Volatility-Managed Portfolios', Journal of Finance 72(4), 2017",
     meccanismo="rendimento per unita' di rischio piu' alto quando la volatilita' recente e' bassa",
     parametri={"volatilita": "deviazione standard dei rendimenti giornalieri a 20 giorni", "soglia": "sotto la mediana dei 120 giorni precedenti", "stop_atr": 2.0, "atr_n": 14, "max_barre": 3},
     entra=_entra_bassa_vol,
     uscita=(lambda serie: {"stop_atr": 2.0, "atr_n": 14, "max_barre": 3}),
     direzione_di=(lambda serie: (lambda i: "long")),
     occupazione=3,
     previsione="100-140 trade, PF 1,0-1,3, R medio 0/+0,08, non netta",
     previsione_pf=[1.0, 1.3], criterio_successo=CRITERIO)

# --------------------------------------------------------------------------- I-02b
for _id, _dir in (("BTCUSDT-V22-long", "long"), ("BTCUSDT-V23-short", "short")):
    _reg(_id, idea="I-02b", tf="1d", direzione=_dir,
         fonte="Moskowitz, Ooi, Pedersen, 'Time Series Momentum', Journal of Financial Economics 104(2), 2012; Liu, Tsyvinski, 'Risks and Returns of Cryptocurrency', Review of Financial Studies 34(6), 2021",
         meccanismo="continuazione del rendimento a 5 giorni",
         parametri={"finestra_giorni": 5, "stop_atr": 2.0, "atr_n": 14, "max_barre": 5},
         entra=(lambda serie, d=_dir: _entra_momentum(serie, 5, d)),
         uscita=(lambda serie: {"stop_atr": 2.0, "atr_n": 14, "max_barre": 5}),
         direzione_di=(lambda serie, d=_dir: (lambda i: d)),
         occupazione=5,
         previsione=("long: 120-150 trade, PF 1,0-1,25, non netto sul caso long" if _dir == "long" else "short: PF 0,85-1,05"),
         previsione_pf=([1.0, 1.25] if _dir == "long" else [0.85, 1.05]), criterio_successo=CRITERIO)

# --------------------------------------------------------------------------- I-12
def _giorni_nr7(serie_1d: s.Serie, n: int = 7):
    """{ordinale del giorno: (high, low)} dei giorni il cui range e' il piu' stretto degli ultimi n."""
    rng = serie_1d.h - serie_1d.l
    minimo_prec = s.shift(s.rolling_min(rng, n - 1), 1)
    out = {}
    for i in range(serie_1d.n):
        if np.isfinite(minimo_prec[i]) and rng[i] < minimo_prec[i]:
            out[int(serie_1d.giorno[i])] = (float(serie_1d.h[i]), float(serie_1d.l[i]))
    return out


def _prima_rottura_nr7(serie: s.Serie):
    """lato[i] = +1/-1 se i e' la prima barra oraria del giorno dopo un NR7 con close fuori dal range NR7."""
    nr7 = _giorni_nr7(s.Serie("1d"))
    c, ora, giorno = serie.c, serie.ora, serie.giorno
    lato = np.zeros(serie.n, dtype=np.int64)
    livelli = np.full((serie.n, 2), np.nan)
    gia = set()
    for i in range(serie.n):
        g = int(giorno[i])
        hl = nr7.get(g - 1)
        if hl is None or g in gia or ora[i] == 23:
            continue
        livelli[i] = hl
        if c[i] > hl[0]:
            lato[i] = 1; gia.add(g)
        elif c[i] < hl[1]:
            lato[i] = -1; gia.add(g)
    return lato, livelli


def _entra_nr7(serie: s.Serie, direzione: str):
    lato, _ = _prima_rottura_nr7(serie)
    voluto = 1 if direzione == "long" else -1
    return lambda i: direzione if lato[i] == voluto else None


def _uscita_nr7(serie: s.Serie):
    _, livelli = _prima_rottura_nr7(serie)
    nr7 = _giorni_nr7(s.Serie("1d"))
    atr = serie.atr(14)
    c, ora, giorno = serie.c, serie.ora, serie.giorno

    def stop_fn(i: int, direzione: str):
        hl = nr7.get(int(giorno[i]) - 1)
        a = atr[i]
        if hl is None or not np.isfinite(a):
            return None
        return min(hl[1], c[i] - a) if direzione == "long" else max(hl[0], c[i] + a)

    def chiudi(i: int, pos) -> bool:
        return bool(ora[i] == 23)
    return {"stop_fn": stop_fn, "atr_n": 14, "chiudi": chiudi}


for _id, _dir in (("BTCUSDT-V24-long", "long"), ("BTCUSDT-V25-short", "short")):
    _reg(_id, idea="I-12", tf="1h", direzione=_dir,
         fonte="Crabel, 'Day Trading with Short Term Price Patterns and Opening Range Breakout', 1990",
         meccanismo="espansione dopo la contrazione dell'intervallo giornaliero (NR7), nella direzione della prima rottura",
         parametri={"nr": 7, "stop": "estremo opposto del giorno NR7, almeno 1 ATR(14) orario", "uscita": "chiusura della barra 23:00", "un_trade_al_giorno": True},
         entra=(lambda serie, d=_dir: _entra_nr7(serie, d)),
         uscita=(lambda serie: _uscita_nr7(serie)),
         direzione_di=(lambda serie, d=_dir: (lambda i: d)),
         occupazione=12,
         previsione=f"{_dir}: 60-100 trade stimati, probabile scarto; se si testa PF 0,9-1,1",
         previsione_pf=[0.9, 1.1], criterio_successo=CRITERIO)


# =========================================================================== quarto blocco (Fase 5)
# --------------------------------------------------------------------------- I-13
def _bande(serie: s.Serie, n: int = 20, k: float = 2.0):
    m, sd = s.sma(serie.c, n), s.rolling_std(serie.c, n)
    return m, m + k * sd, m - k * sd


def _entra_bollinger(serie: s.Serie, direzione: str):
    m, alta, bassa = _bande(serie)
    c = serie.c
    if direzione == "long":
        return lambda i: "long" if (np.isfinite(bassa[i]) and c[i] < bassa[i]) else None
    return lambda i: "short" if (np.isfinite(alta[i]) and c[i] > alta[i]) else None


def _chiudi_bollinger(serie: s.Serie):
    m, _, _ = _bande(serie)
    c = serie.c

    def chiudi(i: int, pos) -> bool:
        if not np.isfinite(m[i]):
            return False
        return bool(c[i] > m[i]) if pos.direzione == "long" else bool(c[i] < m[i])
    return chiudi


for _id, _dir in (("BTCUSDT-V26-long", "long"), ("BTCUSDT-V27-short", "short")):
    _reg(_id, idea="I-13", tf="4h", direzione=_dir,
         fonte="Bollinger, 'Bollinger on Bollinger Bands', McGraw-Hill, 2001; Lento, Gradojevic, Wright, 'Investment information content in Bollinger Bands', Applied Financial Economics Letters 3(4), 2007",
         meccanismo="fornitura di liquidita' dopo un eccesso di 2 deviazioni standard dalla media a 20 barre",
         parametri={"bande": "SMA 20, 2 deviazioni standard", "uscita": "rientro oltre la media o 10 barre", "stop_atr": 2.0, "atr_n": 14, "max_barre": 10},
         entra=(lambda serie, d=_dir: _entra_bollinger(serie, d)),
         uscita=(lambda serie: {"stop_atr": 2.0, "atr_n": 14, "max_barre": 10, "chiudi": _chiudi_bollinger(serie)}),
         direzione_di=(lambda serie, d=_dir: (lambda i: d)),
         occupazione=10,
         previsione=f"{_dir}: 100-160 trade, PF 0,85-1,05, R medio <= 0",
         previsione_pf=[0.85, 1.05], criterio_successo=CRITERIO)
