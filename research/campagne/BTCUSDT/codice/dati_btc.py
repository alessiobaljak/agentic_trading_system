"""Dati e parametri della campagna BTCUSDT, in un posto solo.

* ``carica(intervallo)``: candele last (segnali e stop) e mark (liquidazioni)
  sul timeframe richiesto, aggregate dalle 15m scaricate in Fase 0, piu' il
  funding. Le barre MARK mancanti (770 barre a 15m in 7 buchi, vedi
  fase0_dati.md) si riempiono con la barra LAST dello stesso istante, PRIMA
  dell'aggregazione; il numero di barre riempite si ritorna e si dichiara.
* ``parametri(...)``: i ``Parametri`` del motore con i valori congelati di
  config/parametri.yaml e la fascia di slippage della scheda (0,01% per lato).
* ``fetta(candele, inizio, fine)``: le candele di un periodo (giorni inclusi).
* ``COSTRUZIONE`` e ``VALIDAZIONE``: le date registrate nel log (BTCUSDT-F0-01).
"""
from __future__ import annotations

import sys
from datetime import date, timedelta
from functools import lru_cache
from pathlib import Path
from typing import Dict, List, Sequence, Tuple

RADICE_REPO = Path(__file__).resolve().parents[4]
if str(RADICE_REPO) not in sys.path:
    sys.path.insert(0, str(RADICE_REPO))

from research.src import dati  # noqa: E402
from research.src.motore import Candela, Parametri  # noqa: E402

SIMBOLO = "BTCUSDT"
INIZIO_DATI, FINE_DATI = date(2020, 1, 1), date(2023, 12, 31)
COSTRUZIONE = (date(2020, 1, 1), date(2022, 10, 19))
VALIDAZIONE = (date(2022, 10, 20), date(2023, 12, 31))

# Valori congelati (research/config/parametri.yaml, scheda_moneta.md)
COMMISSIONE = 0.0005
SLIPPAGE = 0.0001
RISCHIO = 0.01
LEVA_MAX = 2.0
MMR = 0.025
CAPITALE = 1000.0


def parametri(moltiplicatore_costi: float = 1.0, ritardo_barre: int = 0, intrabarra: str = "stop_prima") -> Parametri:
    return Parametri(
        commissione_per_lato=COMMISSIONE,
        slippage_per_lato=SLIPPAGE,
        rischio_per_trade=RISCHIO,
        leva_max=LEVA_MAX,
        modalita_margine="isolated",
        tasso_margine_mantenimento=MMR,
        margine_minimo_da_liquidazione=0.8,
        capitale_iniziale=CAPITALE,
        riempimento_intrabarra=intrabarra,  # type: ignore[arg-type]
        moltiplicatore_costi=moltiplicatore_costi,
        ritardo_barre=ritardo_barre,
    )


def riempi_mark_con_last(last: Sequence[Candela], mark: Sequence[Candela]) -> Tuple[List[Candela], int]:
    """Serie mark allineata ai ts di ``last``; le barre assenti prendono la barra last."""
    per_ts = {c.ts: c for c in mark}
    out: List[Candela] = []
    riempite = 0
    for c in last:
        m = per_ts.get(c.ts)
        if m is None:
            m = c
            riempite += 1
        out.append(m)
    return out, riempite


@lru_cache(maxsize=None)
def _base15() -> Tuple[Tuple[Candela, ...], Tuple[Candela, ...], int, Tuple[Tuple[int, float], ...]]:
    last = dati.carica_candele(SIMBOLO, "15m", INIZIO_DATI, FINE_DATI)
    mark = dati.carica_candele(SIMBOLO, "15m", INIZIO_DATI, FINE_DATI, tipo="markPriceKlines")
    mark_pieno, riempite = riempi_mark_con_last(last, mark)
    funding = dati.carica_funding(SIMBOLO, INIZIO_DATI, FINE_DATI)
    return tuple(last), tuple(mark_pieno), riempite, tuple(funding)


@lru_cache(maxsize=None)
def carica(intervallo: str) -> Dict[str, object]:
    """{'last': [...], 'mark': [...], 'funding': [...], 'mark_riempite_15m': n} sul timeframe."""
    last, mark, riempite, funding = _base15()
    if intervallo == "15m":
        l, m = list(last), list(mark)
    else:
        l = dati.aggrega_candele(last, intervallo)
        m = dati.aggrega_candele(mark, intervallo)
    return {"last": l, "mark": m, "funding": list(funding), "mark_riempite_15m": riempite}


def fetta(candele: Sequence[Candela], inizio: date, fine: date) -> List[Candela]:
    da, a = dati.ms_da_data(inizio), dati.ms_da_data(fine + timedelta(days=1))
    return [c for c in candele if da <= c.ts and c.close_ts < a]


def fetta_funding(funding: Sequence[Tuple[int, float]], inizio: date, fine: date) -> List[Tuple[int, float]]:
    da, a = dati.ms_da_data(inizio), dati.ms_da_data(fine + timedelta(days=1))
    return [(ts, r) for ts, r in funding if da <= ts < a]
