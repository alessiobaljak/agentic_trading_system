"""Modello di costo CONDIVISO tra backtest (GATE 1) e live — per la parita'.

Il costo round-trip di un trade = fee fisse + uno SPREAD stimato che si allarga
sulle coin sottili. Cosi' il gate valida ogni coppia coi SUOI costi reali e
l'INTERO universo e' tradabile: chi non batte il proprio spread non passa (invece
di tagliarlo con un filtro netto sul volume). Con size piccole lo slippage e'
trascurabile -> il termine variabile e' lo spread bid-ask, approssimato dalla
liquidita' (volume 24h in USDT). Stesse soglie qui = stesso costo su gate e live.
"""
from __future__ import annotations


def liquidity_spread(daily_quote_vol: float | None) -> float:
    """Spread round-trip per fascia di volume 24h (USDT). Valori MISURATI dagli
    spread bid/ask reali di Binance Futures (scripts/measure_spreads.py), con un
    piccolo margine per depth/volatilita' (lo snapshot e' a mercato calmo)."""
    v = daily_quote_vol or 0.0
    if v >= 200_000_000:
        return 0.00012       # misurato 0.0103% -> ~0.012% col buffer
    if v >= 50_000_000:
        return 0.00025       # misurato 0.0213%
    if v >= 10_000_000:
        return 0.00045       # misurato 0.0385%
    return 0.00080           # misurato 0.0677% (sottile): buffer maggiore


def funding_fraction(rate_per_8h: float | None, held_hours: float, long: bool,
                     default_rate: float = 0.0001) -> float:
    """Funding sui perpetual come FRAZIONE (con segno) del notional — CONDIVISO
    tra backtest e live per la parita'.

    Binance regola il funding ogni 8h: chi e' LONG PAGA quando il tasso e' positivo,
    chi e' SHORT INCASSA (e viceversa a tasso negativo). Lo approssimiamo in modo
    continuo (proporzionale alle ore) col tasso REALE della coin. Ritorna un COSTO
    da SOTTRARRE al PnL: > 0 = paghi, < 0 = incassi. `rate_per_8h` None -> default.
    """
    rate = default_rate if rate_per_8h is None else rate_per_8h
    sign = 1.0 if long else -1.0
    return (held_hours / 8.0) * rate * sign
