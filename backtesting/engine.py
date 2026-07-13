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
from bot.config import settings
from bot.execution.exit_logic import locked_stop
from bot.strategies import get_all_strategies
from bot.strategies.base import StrategyContext

LEVERAGE_LEVELS = (2, 3, 5, 10, 20)


def passes_gate(window_pnls: list[float], n_trades: int, pf: float,
                win_rate: float, total_return: float) -> bool:
    """
    Verdetto GATE 1 per una coppia (coin, strategia), fuori campione (OOS).
    Tutte le condizioni (soglie in config) devono valere:
      * almeno GATE_MIN_TRADES trade;
      * profit factor >= GATE_PF_THRESHOLD;
      * win-rate >= GATE_WIN_RATE_FLOOR;
      * ritorno OOS totale >= GATE_MIN_TOTAL_RETURN ("profittevole, e di tanto");
      * profittevole in OGNI (o quasi) finestra OOS — almeno
        GATE_CONSISTENCY_FRACTION delle finestre > 0: niente "in perdita un anno e
        recupero il dopo".
    """
    if n_trades < settings.GATE_MIN_TRADES:
        return False
    if pf < settings.GATE_PF_THRESHOLD:
        return False
    if win_rate < settings.GATE_WIN_RATE_FLOOR:
        return False
    if total_return < settings.GATE_MIN_TOTAL_RETURN:
        return False
    if window_pnls:
        positive = sum(1 for w in window_pnls if w > 0)
        if positive < len(window_pnls) * settings.GATE_CONSISTENCY_FRACTION - 1e-9:
            return False
    return True
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
    # verdetto controfattuale sull'uscita TRAILING (None se non trailing):
    # 'premature' = avremmo raggiunto il TP tenendo; 'protected' = avremmo preso lo
    # stop base; 'neutral' = nessuno dei due entro l'orizzonte.
    trailing_verdict: Optional[str] = None

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

    def trailing_counts(self) -> dict:
        """Conteggi del verdetto sulle uscite trailing: prematuro/protetto/neutro.
        Serve al bot per capire se il profit-lock su questa strategia taglia i
        vincitori (tanti 'premature' -> andrebbe allentato) o protegge davvero."""
        out = {"premature": 0, "protected": 0, "neutral": 0, "trailing_total": 0}
        for t in self.trades:
            if t.trailing_verdict:
                out[t.trailing_verdict] += 1
                out["trailing_total"] += 1
        return out

    def profit_factor(self) -> float:
        gains = sum(t.pnl_pct for t in self.trades if t.pnl_pct > 0)
        losses = -sum(t.pnl_pct for t in self.trades if t.pnl_pct < 0)
        if losses > 0:
            return gains / losses
        # nessuna perdita: PF "infinito" -> cap alto (JSON-safe), cosi' una strategia
        # senza perdite NON viene bocciata dal gate (prima ritornava 'gains', spesso
        # < soglia -> bocciata pur essendo perfetta).
        return 999.0 if gains > 0 else 0.0

    def liquidations_at_leverage(self) -> dict[int, int]:
        """Quante volte saresti stato liquidato a ciascun livello di leva."""
        out = {}
        for lev in LEVERAGE_LEVELS:
            threshold = (1.0 / lev) - MAINTENANCE_BUFFER
            out[lev] = sum(1 for t in self.trades if t.max_adverse_pct >= threshold)
        return out


class Backtester:
    def __init__(self, window: int = 200, capital: float = 10_000.0,
                 cost_per_trade: float = None, funding_per_8h: float = None,
                 interval_hours: float = 1.0) -> None:
        import os
        self.window = window
        self.capital = capital
        # costo round-trip (fee + slippage) come frazione del nozionale, per trade.
        # default 0.08% (taker ~0.04%/lato + slippage). Configurabile via env.
        self.cost_per_trade = (cost_per_trade if cost_per_trade is not None
                               else float(os.getenv("BACKTEST_COST_PER_TRADE", "0.0008")))
        # funding sui perpetual: costo ricorrente ogni 8h sulle posizioni aperte.
        # default 0.01%/8h (stima conservativa). Configurabile via env.
        self.funding_per_8h = (funding_per_8h if funding_per_8h is not None
                               else float(os.getenv("BACKTEST_FUNDING_PER_8H", "0.0001")))
        self.interval_hours = interval_hours
        self.regime_detector = RegimeDetector()
        self.strategies = get_all_strategies()

    def _liquidity_cost(self, candles: list[Candle]) -> float:
        """Costo round-trip LIQUIDITA'-DIPENDENTE: fee fisse + spread stimato che si
        allarga sulle coin sottili. Cosi' il gate valida ogni coppia coi SUOI costi
        reali e l'INTERO universo e' tradabile: una coppia passa solo se l'edge batte
        il proprio costo (niente piu' taglio netto sul volume). Con size piccole lo
        slippage e' trascurabile: il termine variabile e' lo SPREAD, stimato dal
        volume 24h in USDT (close*volume medio * candele/giorno)."""
        if not candles:
            return self.cost_per_trade
        from bot.core.costs import liquidity_spread
        recent = candles[-min(len(candles), 720):]        # ~ultimi 30g su 1h
        avg_quote = sum(c.close * c.volume for c in recent) / len(recent)
        daily_vol = avg_quote * (24.0 / max(self.interval_hours, 1e-9))
        return self.cost_per_trade + liquidity_spread(daily_vol)

    @staticmethod
    def _trailing_verdict(candles, j: int, horizon: int, stop: float, target: float,
                          long: bool) -> str:
        """Verdetto controfattuale sul trailing dalla barra j all'orizzonte.
        Usa la funzione CONDIVISA (bot/execution/exit_logic) = stessa logica del bot."""
        from bot.execution.exit_logic import trailing_verdict
        return trailing_verdict(candles[j:horizon + 1], stop, target, long)

    def _snapshot_from_frame(self, symbol: str, frame, idx: int) -> AssetSnapshot:
        row = frame.iloc[idx]
        snap = AssetSnapshot(symbol=symbol, price=float(row["close"]))
        ind15 = snapshot_from_row(row, "15m")
        ind1h = snapshot_from_row(row, "1h")
        snap.indicators["15m"] = ind15
        snap.indicators["1h"] = ind1h
        snap.indicators["5m"] = ind15
        return snap

    def build_context(self, symbol: str, candles: list[Candle], frame=None) -> dict:
        """Mappa open_time -> AssetSnapshot per un asset di CONTESTO (es. BTC), così
        strategie cross-asset (momentum_cross_asset) sono validabili nel backtest."""
        if frame is None:
            frame = compute_indicator_frame(candles)
        out: dict = {}
        for idx in range(len(frame)):
            snap = self._snapshot_from_frame(symbol, frame, idx)
            out[frame.iloc[idx]["open_time"]] = snap
        return out

    def run_strategy(self, strategy, symbol: str, candles: list[Candle], frame=None,
                     context_by_ts: dict | None = None) -> StrategyStats:
        stats = StrategyStats(strategy=strategy.name)
        if frame is None:
            frame = compute_indicator_frame(candles)
        cost = self._liquidity_cost(candles)   # costo reale di QUESTA coin (liquidita')
        i = self.window
        n = len(candles)
        while i < n - 1:
            snap = self._snapshot_from_frame(symbol, frame, i)
            regime = self.regime_detector.detect(snap)
            snap.regime = regime
            if not strategy.is_active_in(regime):
                i += 1
                continue
            ctx_assets = {symbol: snap}
            if context_by_ts:
                ctx_snap = context_by_ts.get(candles[i].open_time)
                if ctx_snap is not None:
                    ctx_assets[ctx_snap.symbol] = ctx_snap
            sig = strategy.generate_signal(snap, StrategyContext(ctx_assets, regime))
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
            # miglior prezzo a favore visto FINORA (per il profit-lock). Usa solo le
            # barre PRECEDENTI quando calcola lo stop, così niente look-ahead.
            best_fav = entry
            trailing_verdict = None
            while j <= horizon:
                c = candles[j]
                # stop effettivo: base o alzato dal profit-lock (sui massimi passati)
                eff_stop = locked_stop(entry, target, long, best_fav, stop)
                trailing = eff_stop != stop   # il profit-lock ha alzato lo stop?
                adverse = (entry - c.low) / entry if long else (c.high - entry) / entry
                max_adverse = max(max_adverse, adverse)
                if long and c.low <= eff_stop:
                    exit_price = eff_stop
                    if trailing:
                        trailing_verdict = self._trailing_verdict(candles, j, horizon, stop, target, long)
                    break
                if long and c.high >= target:
                    exit_price = target; break
                if (not long) and c.high >= eff_stop:
                    exit_price = eff_stop
                    if trailing:
                        trailing_verdict = self._trailing_verdict(candles, j, horizon, stop, target, long)
                    break
                if (not long) and c.low <= target:
                    exit_price = target; break
                # aggiorna il miglior prezzo a favore DOPO i controlli di uscita
                best_fav = max(best_fav, c.high) if long else min(best_fav, c.low)
                exit_price = c.close
                j += 1

            pnl_pct = (exit_price - entry) / entry if long else (entry - exit_price) / entry
            # uscite reali: fee+slippage (round-trip) + funding sui perpetual.
            held_hours = max(0, (min(j, horizon) - i)) * self.interval_hours
            funding = (held_hours / 8.0) * self.funding_per_8h
            pnl_pct -= (cost + funding)
            stats.trades.append(SimTrade(
                strategy=strategy.name, regime=regime.value, direction=sig.direction.value,
                entry_price=entry, exit_price=exit_price, pnl_pct=pnl_pct,
                max_adverse_pct=max_adverse, confidence=sig.confidence,
                is_win=pnl_pct > 0, pnl=pnl_pct * self.capital, symbol=symbol,
                hour_bucket=candles[i].open_time.hour,
                confidence_at_entry=sig.confidence, regime_at_entry=regime.value,
                trailing_verdict=trailing_verdict,
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
