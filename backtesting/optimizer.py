"""
Walk-Forward Optimizer — il motore di "test -> learn -> iterate" autonomo.

Per OGNI asset e OGNI strategia (con param_grid):
  1. divide lo storico in finestre sequenziali train/test;
  2. su ogni TRAIN cerca i parametri migliori (grid search);
  3. li applica sulla finestra TEST successiva, MAI vista (out-of-sample);
  4. aggrega le performance OOS su tutte le finestre.

Il risultato per (asset, strategia) è: parametri più recenti che hanno vinto +
metriche OOS (pf, pnl, n. trade, win rate). Questo evita l'overfitting (si misura
solo fuori campione) e cattura il fatto che i parametri migliori cambiano nel tempo.

Output pensato per essere scritto su Firebase e letto dal bot:
  strategy_params/current -> { "BTCUSDT|breakout": {params...}, ... }
"""
from __future__ import annotations

import itertools
import random
from dataclasses import dataclass, field
from typing import Optional

from backtesting.engine import Backtester, StrategyStats, passes_gate
from bot.core.indicators import compute_indicator_frame
from bot.core.models import Candle
from bot.strategies.base import STRATEGY_REGISTRY


def _param_combos(grid: dict[str, list]) -> list[dict]:
    if not grid:
        return []
    keys = list(grid.keys())
    return [dict(zip(keys, vals)) for vals in itertools.product(*[grid[k] for k in keys])]


@dataclass
class OptResult:
    symbol: str
    strategy: str
    best_params: dict
    oos_pf: float
    oos_pnl_pct: float
    oos_trades: int
    oos_win_rate: float
    passed: bool
    trailing: dict = field(default_factory=dict)   # conteggi verdetto trailing OOS
    params_history: list = field(default_factory=list)


class WalkForwardOptimizer:
    def __init__(
        self,
        n_windows: int = 3,
        min_trades_train: int = 10,
        min_trades_oos: int = 10,
        pf_threshold: float = 1.10,
        capital: float = 10_000.0,
        warmup: int = 200,
        max_combos: int = 0,
        seed: int = 7,
    ) -> None:
        self.n_windows = n_windows
        self.min_trades_train = min_trades_train
        self.min_trades_oos = min_trades_oos
        self.pf_threshold = pf_threshold
        self.bt = Backtester(window=warmup, capital=capital)
        # se >0, campiona al massimo questo numero di combinazioni per strategia
        # (per tenere i tempi gestibili quando si ottimizzano molti coin)
        self.max_combos = max_combos
        self._rng = random.Random(seed)

    # ------------------------------------------------------------------ #
    def _windows(self, n: int) -> list[tuple[int, int, int, int]]:
        """Ritorna [(train_a, train_b, test_a, test_b), ...] su indici candele."""
        blocks = self.n_windows + 1
        size = n // blocks
        if size <= self.bt.window + 50:
            return []
        out = []
        for w in range(self.n_windows):
            ta, tb = w * size, (w + 1) * size
            sa, sb = (w + 1) * size, (w + 2) * size
            out.append((ta, tb, sa, min(sb, n)))
        return out

    @staticmethod
    def _score(stats: StrategyStats, min_trades: int) -> float:
        if len(stats.trades) < min_trades:
            return -1e9
        # obiettivo: ritorno netto OOS, con piccolo bonus per profit factor
        return stats.total_pnl_pct() + 0.1 * (stats.profit_factor() - 1.0)

    def optimize_symbol(self, symbol: str, candles: list[Candle],
                        context_by_ts: dict | None = None) -> list[OptResult]:
        results: list[OptResult] = []
        frame = compute_indicator_frame(candles)
        windows = self._windows(len(candles))
        if not windows:
            print(f"[optimizer] {symbol}: dati insufficienti per il walk-forward")
            return results

        for name, cls in STRATEGY_REGISTRY.items():
            combos = _param_combos(getattr(cls, "param_grid", {}))
            if not combos:
                continue  # strategia non ottimizzabile (nessuna griglia)
            if self.max_combos and len(combos) > self.max_combos:
                combos = self._rng.sample(combos, self.max_combos)

            oos = StrategyStats(strategy=name)
            history: list[dict] = []
            window_pnls: list[float] = []   # ritorno OOS per finestra (consistenza)
            for (ta, tb, sa, sb) in windows:
                train_c = candles[ta:tb]
                train_f = frame.iloc[ta:tb].reset_index(drop=True)
                # grid search sul train
                best_combo, best_score = combos[0], -1e18
                for combo in combos:
                    st = self.bt.run_strategy(cls(combo), symbol, train_c, frame=train_f,
                                              context_by_ts=context_by_ts)
                    sc = self._score(st, self.min_trades_train)
                    if sc > best_score:
                        best_score, best_combo = sc, combo
                # se NESSUNA combo ha abbastanza trade sul train (score sentinella),
                # salta la finestra: non applichiamo parametri non validati all'OOS.
                if best_score < -1e8:
                    continue
                # applica i migliori sul TEST (out-of-sample)
                test_c = candles[sa:sb]
                test_f = frame.iloc[sa:sb].reset_index(drop=True)
                st_oos = self.bt.run_strategy(cls(best_combo), symbol, test_c, frame=test_f,
                                              context_by_ts=context_by_ts)
                oos.trades.extend(st_oos.trades)
                # consistenza: conta SOLO le finestre che hanno prodotto trade. Una
                # finestra senza segnali non e' "una perdita", e' "nessun dato".
                if st_oos.trades:
                    window_pnls.append(sum(t.pnl_pct for t in st_oos.trades))
                history.append(best_combo)

            pf = oos.profit_factor()
            pnl = oos.total_pnl_pct()
            passed = passes_gate(window_pnls, len(oos.trades), pf, oos.win_rate(), pnl)
            results.append(OptResult(
                symbol=symbol, strategy=name,
                best_params=history[-1] if history else {},
                oos_pf=round(pf, 3), oos_pnl_pct=round(pnl, 4),
                oos_trades=len(oos.trades), oos_win_rate=round(oos.win_rate(), 3),
                passed=passed, trailing=oos.trailing_counts(), params_history=history,
            ))
        return results
