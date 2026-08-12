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

from backtesting.engine import (Backtester, StrategyStats, max_drawdown, passes_gate,
                                pf_by_regime, pf_without_top, weighted_score_parts)
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
    # verifica finale sull'HOLDOUT (dati MAI visti dalla selezione), coi parametri
    # che verrebbero spediti: {"pf", "pnl_pct", "trades", "ok"}. Vuoto se holdout off.
    holdout: dict = field(default_factory=dict)
    # PF/trades per regime dai trade OOS: esportato nel registro per il filtro di
    # regime live e come prior per il learning.
    regime_pf: dict = field(default_factory=dict)
    # timestamp dell'ultima candela usata: serve alla regola "pass solo con dati nuovi"
    data_end: float = 0.0
    # max drawdown OOS della coppia da SOLA. Va salvato, non solo usato per il
    # verdetto: senza, non si puo' confrontare la buca PROMESSA dal gate con quella
    # che il portafoglio scava davvero tenendo aperte 9-12 coppie insieme.
    oos_max_dd: float = 0.0


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
        interval: str = "1h",
    ) -> None:
        self.n_windows = n_windows
        self.min_trades_train = min_trades_train
        self.min_trades_oos = min_trades_oos
        self.pf_threshold = pf_threshold
        from backtesting.data_loader import funding_rate_for
        from bot.config import timeframe_hours
        # durata di UNA candela in ore: guida i calcoli tempo-dipendenti del backtest
        # (funding sulle ore aperte). DEVE combaciare col --interval dei dati caricati.
        self.bt = Backtester(window=warmup, capital=capital,
                             interval_hours=timeframe_hours(interval),
                             funding_rate_provider=funding_rate_for)
        # se >0, campiona al massimo questo numero di combinazioni per strategia
        # (per tenere i tempi gestibili quando si ottimizzano molti coin)
        self.max_combos = max_combos
        self._rng = random.Random(seed)
        # HOLDOUT anti data-snooping: ultimi N giorni esclusi da train e finestre.
        # La selezione non li vede mai; ci si valuta UNA volta, a valle, coi
        # parametri che verrebbero spediti. In barre del timeframe corrente.
        from bot.config import settings as _st
        self.holdout_bars = int(_st.GATE_HOLDOUT_DAYS * 24.0 / timeframe_hours(interval))

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
        # obiettivo: PROFITTO CONTINUO, non profitto e basta. Il drawdown della
        # curva entra nel punteggio con lo stesso peso del ritorno: tra due
        # parametri con lo stesso guadagno vince quello che scava la buca minore.
        # Piccolo bonus PF come tie-break di qualita'.
        # RECENCY: ritorno e PF sono PESATI (i trade recenti contano di piu'), cosi'
        # i parametri si ritarano sul carattere ATTUALE del mercato invece che sulla
        # media di anni. Il drawdown NON si pesa: e' una proprieta' del PERCORSO,
        # riponderarla non avrebbe significato.
        pnl_w, pf_w = weighted_score_parts(stats.trades)
        return pnl_w - max_drawdown(stats.trades) + 0.1 * (pf_w - 1.0)

    def split_holdout(self, candles: list) -> tuple[list, int]:
        """(corpo per la selezione, indice di inizio holdout). La selezione (train,
        finestre OOS, pass) lavora SOLO sul corpo; l'holdout resta invisibile fino
        alla verifica finale. holdout_bars<=0 -> nessun holdout (corpo = tutto)."""
        if self.holdout_bars <= 0 or len(candles) <= self.holdout_bars:
            return candles, len(candles)
        cut = len(candles) - self.holdout_bars
        return candles[:cut], cut

    def _holdout_check(self, strategy, symbol: str, candles: list, frame,
                       cut: int, context_by_ts=None) -> dict:
        """Valuta i parametri SPEDIBILI sull'holdout. Include il warmup degli
        indicatori PRIMA del taglio, ma i trade contati partono dall'holdout."""
        from bot.config import settings as _st
        if cut >= len(candles):
            return {}
        start = max(0, cut - self.bt.window)
        seg = candles[start:]
        seg_f = frame.iloc[start:].reset_index(drop=True)
        st = self.bt.run_strategy(strategy, symbol, seg, frame=seg_f,
                                  context_by_ts=context_by_ts)
        pf = st.profit_factor()
        pnl = st.total_pnl_pct()
        n = len(st.trades)
        # ROBUSTEZZA sull'unico campione mai usato per selezionare: se l'holdout e'
        # positivo SOLO grazie ai suoi colpi migliori, non ha verificato un edge.
        # Misurato su BIRBUSDT|gen_472f85b8: 94 trade, +29.5%, ma togliendo i 7
        # migliori diventava -22.6%. Passava lo stesso.
        pf_ex = pf_without_top(st.trades)
        ok = (n >= _st.GATE_HOLDOUT_MIN_TRADES and pf >= _st.GATE_HOLDOUT_PF and pnl > 0
              and pf_ex >= _st.GATE_MIN_PF_EX_TOP)
        return {"pf": round(pf, 3), "pnl_pct": round(pnl, 4), "trades": n, "ok": ok,
                "pf_ex_top": round(pf_ex, 3)}

    def optimize_symbol(self, symbol: str, candles: list[Candle],
                        context_by_ts: dict | None = None) -> list[OptResult]:
        results: list[OptResult] = []
        frame = compute_indicator_frame(candles)
        # la SELEZIONE vede solo il corpo: l'holdout resta fuori da train e finestre
        body, cut = self.split_holdout(candles)
        windows = self._windows(len(body))
        if not windows:
            print(f"[optimizer] {symbol}: dati insufficienti per il walk-forward")
            return results

        for name, cls in STRATEGY_REGISTRY.items():
            # griglia EFFETTIVA: sotto scale-out `rr` (morto) viene sostituito dalla
            # scala dei TP, cosi' la ricerca taratura cio' che decide le uscite
            from bot.execution.exit_logic import effective_param_grid
            combos = _param_combos(effective_param_grid(getattr(cls, "param_grid", {})))
            if not combos:
                continue  # strategia non ottimizzabile (nessuna griglia)
            if self.max_combos and len(combos) > self.max_combos:
                combos = self._rng.sample(combos, self.max_combos)

            oos = StrategyStats(strategy=name)
            history: list[dict] = []
            window_pnls: list[float] = []   # ritorno OOS per finestra (consistenza)
            for (ta, tb, sa, sb) in windows:
                train_c = body[ta:tb]
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
                test_c = body[sa:sb]
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
            reg_pf = pf_by_regime(oos.trades)
            passed = passes_gate(window_pnls, len(oos.trades), pf, oos.win_rate(), pnl,
                                 max_dd=max_drawdown(oos.trades), regime_pf=reg_pf,
                                 pf_ex_top=pf_without_top(oos.trades))
            # VERIFICA FINALE sull'holdout, solo se le finestre sono superate e coi
            # parametri che verrebbero spediti (l'ultimo best del walk-forward).
            hold: dict = {}
            if passed and history and self.holdout_bars > 0:
                hold = self._holdout_check(cls(history[-1]), symbol, candles, frame,
                                           cut, context_by_ts=context_by_ts)
                passed = bool(hold.get("ok"))
            results.append(OptResult(
                symbol=symbol, strategy=name,
                best_params=history[-1] if history else {},
                oos_pf=round(pf, 3), oos_pnl_pct=round(pnl, 4),
                oos_trades=len(oos.trades), oos_win_rate=round(oos.win_rate(), 3),
                passed=passed, trailing=oos.trailing_counts(), params_history=history,
                holdout=hold, regime_pf=reg_pf,
                oos_max_dd=round(max_drawdown(oos.trades), 4),
                data_end=(candles[-1].open_time.timestamp() if candles else 0.0),
            ))
        return results
