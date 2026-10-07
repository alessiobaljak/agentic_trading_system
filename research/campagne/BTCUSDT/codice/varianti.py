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
