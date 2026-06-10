"""
Motore di backtesting (GATE 1).

Per ogni strategia simula i trade sui dati storici:
  * costruisce indicatori su una finestra rolling
  * classifica il regime ad ogni barra (RegimeDetector)
  * genera segnali ed esegue entry/exit con SL/TP (e trailing semplificato)
  * traccia la MAX ADVERSE EXCURSION per simulare le LIQUIDAZIONI a vari leverage
  * segmenta i risultati per strategia × regime

Poi VALIDA IL LEARNING LOOP: dà in pasto i trade simulati a
`bot.learning.metrics.compute_weights` e verifica che produca pesi coerenti.

È un GATE: se le strategie non sono profittevoli, `verdict()` segnala lo stop.
"""
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from typing import Optional

from bot.agents.regime_detector import RegimeDetector
from bot.core.indicators import compute_indicator_frame, snapshot_from_row
from bot.core.models import AssetSnapshot, Candle, Direction, Regime
from bot.strategies import get_all_strategies
from bot.strategies.base import StrategyContext

LEVERAGE_LEVELS = (2, 3, 5, 10, 20)
# soglia di liquidazione approssimata: ~ (1/leva) meno un buffer di mantenimento
MAINTENANCE_BUFFER = 0.005


@dataclass
class SimTrade:
    strategy: str
    regime: str
    direction: str
    entry_price: float
    exit_price: float
    pnl_pct: float                 # sul margine (pre-leva: variazione prezzo)
    max_adverse_pct: float         # escursione avversa massima (per liquidazioni)
    confidence: float
    is_win: bool
    pnl: float
    symbol: str
    hour_bucket: int = 0
    confidence_at_entry: Optional[float] = None
    regime_at_entry: str = ""

    def as_trade_dict(self) -> dict:
        """Formato compatibile con bot.learning.metrics."""
        return {
            "strategy": self.strategy, "regime_at_entry": self.regime,
            "symbol": self.symbol, "direction": self.direction,
            "pnl": self.pnl, "pnl_pct": self.pnl_pct, "is_win": self.is_win,
            "hour_bucket": self.hour_bucket,
            "confidence_at_entry": self.confidence_at_entry,
        }


@dataclass
class StrategyStats:
    strategy: str
    trades: list[SimTrade] = field(default_factory=list)

    def by_regime(self) -> dict[str, list[SimTrade]]:
        out = defaultdict(list)
        for t in self.trades:
            out[t.regime].append(t)
        return out

    def total_pnl_pct(self) -> float:
        return sum(t.pnl_pct for t in self.trades)

    def win_rate(self) -> float:
        return (sum(t.is_win for t in self.trades) / len(self.trades)) if self.trades else 0.0

    def profit_factor(self) -> float:
        gains = sum(t.pnl_pct for t in self.trades if t.pnl_pct > 0)
        losses = -sum(t.pnl_pct for t in self.trades if t.pnl_pct < 0)
        return gains / losses if losses > 0 else (gains if gains else 0.0)

    def liquidations_at_leverage(self) -> dict[int, int]:
        """Quante volte saresti stato liquidato a ciascun livello di leva."""
        out = {}
        for lev in LEVERAGE_LEVELS:
            threshold = (1.0 / lev) - MAINTENANCE_BUFFER
            out[lev] = sum(1 for t in self.trades if t.max_adverse_pct >= threshold)
        return out


class Backtester:
    def __init__(self, window: int = 200, capital: float = 10_000.0) -> None:
        self.window = window
        self.capital = capital
        self.regime_detector = RegimeDetector()
        self.strategies = get_all_strategies()

    def _snapshot_from_frame(self, symbol: str, frame, idx: int) -> AssetSnapshot:
        row = frame.iloc[idx]
        snap = AssetSnapshot(symbol=symbol, price=float(row["close"]))
        ind15 = snapshot_from_row(row, "15m")
        ind1h = snapshot_from_row(row, "1h")
        snap.indicators["15m"] = ind15
        snap.indicators["1h"] = ind1h
        snap.indicators["5m"] = ind15
        return snap

    def run_strategy(self, strategy, symbol: str, candles: list[Candle], frame=None) -> StrategyStats:
        stats = StrategyStats(strategy=strategy.name)
        if frame is None:
            frame = compute_indicator_frame(candles)
        i = self.window
        n = len(candles)
        while i < n - 1:
            snap = self._snapshot_from_frame(symbol, frame, i)
            regime = self.regime_detector.detect(snap)
            snap.regime = regime
            if not strategy.is_active_in(regime):
                i += 1
                continue
            sig = strategy.generate_signal(snap, StrategyContext({symbol: snap}, regime))
            if sig is None:
                i += 1
                continue

            entry = snap.price
            stop = sig.suggested_stop or (entry * (0.98 if sig.direction == Direction.LONG else 1.02))
            target = sig.suggested_target or (entry * (1.04 if sig.direction == Direction.LONG else 0.96))
            long = sig.direction == Direction.LONG

            # simula l'evoluzione fino a SL/TP o fine finestra (max 96 barre)
            max_adverse = 0.0
            exit_price = entry
            j = i + 1
            horizon = min(n - 1, i + 96)
            while j <= horizon:
                c = candles[j]
                adverse = (entry - c.low) / entry if long else (c.high - entry) / entry
                max_adverse = max(max_adverse, adverse)
                if long and c.low <= stop:
                    exit_price = stop; break
                if long and c.high >= target:
                    exit_price = target; break
                if (not long) and c.high >= stop:
                    exit_price = stop; break
                if (not long) and c.low <= target:
                    exit_price = target; break
                exit_price = c.close
                j += 1

            pnl_pct = (exit_price - entry) / entry if long else (entry - exit_price) / entry
            stats.trades.append(SimTrade(
                strategy=strategy.name, regime=regime.value, direction=sig.direction.value,
                entry_price=entry, exit_price=exit_price, pnl_pct=pnl_pct,
                max_adverse_pct=max_adverse, confidence=sig.confidence,
                is_win=pnl_pct > 0, pnl=pnl_pct * self.capital, symbol=symbol,
                hour_bucket=candles[i].open_time.hour,
                confidence_at_entry=sig.confidence, regime_at_entry=regime.value,
            ))
            i = j + 1   # niente posizioni sovrapposte
        return stats

    def run(self, symbol: str, candles: list[Candle]) -> dict[str, StrategyStats]:
        # indicatori calcolati UNA volta sull'intera serie (riuso per tutte le strategie)
        frame = compute_indicator_frame(candles)
        results = {}
        for strat in self.strategies:
            results[strat.name] = self.run_strategy(strat, symbol, candles, frame=frame)
        return results

    # ---- validazione del learning loop sui dati storici ----
    @staticmethod
    def validate_learning(all_stats: dict[str, StrategyStats]) -> list:
        from bot.learning.metrics import compute_weights
        trades = [t.as_trade_dict() for s in all_stats.values() for t in s.trades]
        return compute_weights(trades)

    # ---- verdetto del GATE ----
    @staticmethod
    def verdict(all_stats: dict[str, StrategyStats]) -> dict:
        profitable = {k: s for k, s in all_stats.items() if s.total_pnl_pct() > 0}
        total = sum(s.total_pnl_pct() for s in all_stats.values())
        passed = total > 0 and len(profitable) >= 1
        return {
            "passed": passed,
            "total_pnl_pct": total,
            "profitable_strategies": list(profitable.keys()),
            "message": ("GATE 1 superato: almeno una strategia profittevole, edge positivo."
                        if passed else
                        "GATE 1 NON superato: rivedere le strategie prima di procedere all'execution."),
        }
