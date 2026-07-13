"""
Metriche di performance SEGMENTATE + calcolo dei PESI DINAMICI.

Tutto opera su liste di dict (trade serializzati da Firestore) per evitare
dipendenze forti dai modelli durante il job notturno.
"""
from __future__ import annotations

from collections import defaultdict
from statistics import mean
from typing import Iterable

from bot.config import settings
from bot.core.models import Regime, StrategyRegimeWeight

# Mappa win_rate -> peso: <=LOW => 0 (disattivata), >=HIGH => 1 (piena).
WEIGHT_WINRATE_LOW = 0.35
WEIGHT_WINRATE_HIGH = 0.60


def _is_win(t: dict) -> bool:
    return bool(t.get("is_win", t.get("pnl", 0) > 0))


def win_rate(trades: Iterable[dict]) -> float:
    trades = list(trades)
    if not trades:
        return 0.0
    return sum(_is_win(t) for t in trades) / len(trades)


def win_rate_by_strategy(trades: list[dict]) -> dict[str, float]:
    groups = defaultdict(list)
    for t in trades:
        groups[t.get("strategy", "?")].append(t)
    return {k: win_rate(v) for k, v in groups.items()}


def win_rate_by_strategy_regime(trades: list[dict]) -> dict[str, float]:
    groups = defaultdict(list)
    for t in trades:
        key = f"{t.get('strategy','?')}|{t.get('regime_at_entry','?')}"
        groups[key].append(t)
    return {k: win_rate(v) for k, v in groups.items()}


def avg_rr_by_strategy(trades: list[dict]) -> dict[str, float]:
    """R:R realizzato medio = |avg win pnl_pct| / |avg loss pnl_pct| per strategia."""
    groups = defaultdict(list)
    for t in trades:
        groups[t.get("strategy", "?")].append(t)
    out = {}
    for strat, ts in groups.items():
        wins = [abs(t.get("pnl_pct", 0)) for t in ts if _is_win(t)]
        losses = [abs(t.get("pnl_pct", 0)) for t in ts if not _is_win(t)]
        if wins and losses and mean(losses) > 0:
            out[strat] = mean(wins) / mean(losses)
        elif wins and not losses:
            out[strat] = float(len(wins))  # nessuna perdita
    return out


def pnl_by_asset(trades: list[dict]) -> dict[str, float]:
    out = defaultdict(float)
    for t in trades:
        out[t.get("symbol", "?")] += float(t.get("pnl", 0))
    return dict(out)


def win_rate_by_hour(trades: list[dict]) -> dict[str, float]:
    groups = defaultdict(list)
    for t in trades:
        groups[str(t.get("hour_bucket", -1))].append(t)
    return {k: win_rate(v) for k, v in groups.items()}


def worst_drawdown_conditions(trades: list[dict], n: int = 10) -> list[str]:
    """Cosa avevano in comune i trade più perdenti (insight testuali)."""
    losers = sorted([t for t in trades if t.get("pnl", 0) < 0],
                    key=lambda t: t.get("pnl", 0))[:n]
    if not losers:
        return []
    insights = []
    # regime più frequente tra i peggiori
    regimes = defaultdict(int)
    strategies = defaultdict(int)
    hours = defaultdict(int)
    for t in losers:
        regimes[t.get("regime_at_entry", "?")] += 1
        strategies[t.get("strategy", "?")] += 1
        hours[t.get("hour_bucket", -1)] += 1
    top_regime = max(regimes, key=regimes.get)
    top_strat = max(strategies, key=strategies.get)
    top_hour = max(hours, key=hours.get)
    insights.append(f"{regimes[top_regime]}/{len(losers)} dei peggiori trade in regime '{top_regime}'")
    insights.append(f"{strategies[top_strat]}/{len(losers)} dalla strategia '{top_strat}'")
    insights.append(f"fascia oraria UTC {top_hour} ricorrente tra i peggiori")
    return insights


def confidence_outcome_correlation(trades: list[dict]) -> float | None:
    """Pearson tra confidenza dichiarata all'entrata e PnL% reale."""
    pairs = [(t.get("confidence_at_entry"), t.get("pnl_pct"))
             for t in trades
             if t.get("confidence_at_entry") is not None and t.get("pnl_pct") is not None]
    if len(pairs) < 5:
        return None
    xs = [p[0] for p in pairs]
    ys = [p[1] for p in pairs]
    mx, my = mean(xs), mean(ys)
    num = sum((x - mx) * (y - my) for x, y in pairs)
    dx = sum((x - mx) ** 2 for x in xs) ** 0.5
    dy = sum((y - my) ** 2 for y in ys) ** 0.5
    if dx == 0 or dy == 0:
        return None
    return num / (dx * dy)


def _winrate_to_weight(wr: float) -> float:
    if wr <= WEIGHT_WINRATE_LOW:
        return 0.0
    if wr >= WEIGHT_WINRATE_HIGH:
        return 1.0
    return (wr - WEIGHT_WINRATE_LOW) / (WEIGHT_WINRATE_HIGH - WEIGHT_WINRATE_LOW)


def compute_weights(trades: list[dict]) -> list[StrategyRegimeWeight]:
    """
    Pesi dinamici per strategia × regime, con SHRINKAGE graduale (niente cliff).

    Il win-rate stimato parte dal PRIOR neutro (0.60 -> peso 1.0, "tradala") e si
    muove verso l'osservato in proporzione al campione: pochi trade -> resta vicino
    al neutro; molti -> si avvicina all'osservato. Cosi' il learning inizia SUBITO
    (anche con 1-2 trade sposta un po') senza reagire al rumore di un campione
    minuscolo. MIN_TRADES_PER_WEIGHT ora e' la FORZA dello shrinkage (pseudo-conteggio),
    non piu' una soglia netta.
    """
    prior_wr = WEIGHT_WINRATE_HIGH          # 0.60 -> peso 1.0 (prior "tradala")
    k = max(1, settings.MIN_TRADES_PER_WEIGHT)   # forza dello shrinkage

    groups: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for t in trades:
        groups[(t.get("strategy", "?"), t.get("regime_at_entry", "?"))].append(t)

    weights: list[StrategyRegimeWeight] = []
    rr_map = avg_rr_by_strategy(trades)
    for (strat, regime), ts in groups.items():
        try:
            regime_enum = Regime(regime)
        except ValueError:
            continue
        n = len(ts)
        wr = win_rate(ts)
        # win-rate "regolarizzato": media pesata tra osservato (n) e prior (k)
        shrunk = (n * wr + k * prior_wr) / (n + k)
        weight = _winrate_to_weight(shrunk)
        # bonus/malus lieve dal R:R realizzato (solo con un minimo di campione)
        rr = rr_map.get(strat)
        if rr is not None and n >= 3:
            weight = max(0.0, min(1.0, weight * (0.75 + min(rr, 3.0) / 6.0)))
        weights.append(StrategyRegimeWeight(
            strategy=strat, regime=regime_enum, weight=round(weight, 4),
            win_rate=round(wr, 4), avg_rr=rr_map.get(strat), sample_size=n,
        ))
    return weights
