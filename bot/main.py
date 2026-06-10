"""
Entry point del bot — processo persistente 24/7 (VPS Hetzner).

Loop principale:
  * ogni 4h     : market scan (tutto l'universo futures) + asset selection
  * ogni 1h     : regime detection
  * ogni 15m    : orchestratore -> decisione -> RISK GATE -> execution
  * ogni tick   : update posizioni (trailing/scale-out/SL/TP), kill switch, breaker
  * stato live  : scritto su Firebase RTDB (/bot_status, /positions)

DRY_RUN=True (default) => paper trading: nessun ordine reale, ma il learning gira.

Avvio:  python -m bot.main
"""
from __future__ import annotations

import time
from datetime import datetime, timezone

from bot.config import settings
from bot.core.firebase_client import get_firebase
from bot.core.models import ExitReason, RiskSettings
from bot.agents.market_scanner import MarketScanner
from bot.agents.onchain_agent import OnChainAgent
from bot.agents.price_agent import PriceAgent
from bot.agents.regime_detector import RegimeDetector
from bot.execution.executor import ExecutionEngine
from bot.execution.notifier import TelegramNotifier
from bot.learning.adaptation import AdaptationEngine
from bot.learning.trade_logger import TradeLogger
from bot.orchestrator import Orchestrator
from bot.risk.circuit_breakers import CircuitBreakers
from bot.risk.risk_manager import RiskManager


class TradingBot:
    def __init__(self) -> None:
        self.fb = get_firebase()
        self.price = PriceAgent()
        self.onchain = OnChainAgent()
        self.scanner = MarketScanner(self.price)
        self.regime_detector = RegimeDetector()
        self.adaptation = AdaptationEngine(self.fb)
        self.orchestrator = Orchestrator(self.adaptation)
        self.circuit_breakers = CircuitBreakers.from_dict(self.fb.get_rtdb("/risk_state"))
        self.risk = RiskManager(self.circuit_breakers)
        self.executor = ExecutionEngine(self.fb)
        self.logger = TradeLogger(self.fb)
        self.notifier = TelegramNotifier()

        self.selected: dict = {}        # symbol -> AssetSnapshot
        self.regime = None
        self.last_scan = 0.0
        self.last_regime = 0.0
        self.last_decision = 0.0

    # ------------------------------------------------------------------ #
    def read_user_risk(self) -> RiskSettings:
        """Rilegge i parametri regolabili da Firebase PRIMA di ogni nuovo trade."""
        doc = self.fb.get_doc("user_risk_settings", "current")
        if not doc:
            return RiskSettings(leverage=settings.DEFAULT_LEVERAGE,
                                risk_per_trade=settings.DEFAULT_RISK_PER_TRADE)
        try:
            return RiskSettings(**doc)
        except Exception:  # noqa: BLE001
            return RiskSettings()

    def account_equity(self) -> float:
        """Equity corrente. In DRY_RUN usa un valore di paper (o da Firebase)."""
        eq = self.fb.get_rtdb("/account/equity")
        return float(eq) if eq else 10_000.0

    def kill_switch_active(self) -> bool:
        return bool(self.fb.get_rtdb("/commands/kill_switch"))

    # ------------------------------------------------------------------ #
    def maybe_scan(self, now: float) -> None:
        if now - self.last_scan < settings.SCAN_INTERVAL_HOURS * 3600 and self.selected:
            return
        print("[main] market scan...")
        results = self.scanner.scan()
        regime = self.regime or self.refresh_regime(now)
        selected = self.scanner.select_assets(results, regime)
        self.selected = {r.symbol: r.snapshot for r in selected}
        self.last_scan = now
        print(f"[main] selezionati: {list(self.selected.keys())}")

    def refresh_regime(self, now: float):
        btc = self.price.build_snapshot("BTCUSDT")
        fng = self.onchain.fear_greed()
        if btc:
            self.regime = self.regime_detector.detect(btc, fng)
        self.last_regime = now
        self.fb.set_rtdb("/bot_status", {
            "state": "running", "regime": self.regime.value if self.regime else None,
            "dry_run": settings.DRY_RUN, "updated_at": now,
        })
        return self.regime

    def refresh_selected_snapshots(self) -> None:
        fng = self.onchain.fear_greed()
        for sym in list(self.selected.keys()):
            snap = self.price.build_snapshot(sym)
            if snap:
                snap.regime = self.regime
                snap.fear_greed = fng
                self.selected[sym] = snap

    # ------------------------------------------------------------------ #
    def trading_cycle(self, now: float) -> None:
        # 1) gestione posizioni aperte (trailing/scale-out/SL/TP)
        for sym, pos in list(self.executor.open_positions.items()):
            snap = self.selected.get(sym) or self.price.build_snapshot(sym)
            if not snap:
                continue
            closed = self.executor.update_position(sym, snap.price)
            if closed:
                self.logger.log(closed)
                was_sl = closed.exit_reason in (ExitReason.STOP_LOSS,)
                self.circuit_breakers.register_trade_result(closed.pnl_pct, was_sl)
                self._persist_risk_state()
                if self.circuit_breakers.state.daily_pnl_pct <= -0.03:
                    self.notifier.daily_loss(abs(self.circuit_breakers.state.daily_pnl_pct))

        # 2) kill switch
        if self.kill_switch_active():
            prices = {s: self.selected[s].price for s in self.selected if s in self.selected}
            closed = self.executor.force_close_all(prices, ExitReason.KILL_SWITCH)
            for t in closed:
                self.logger.log(t)
            self.notifier.kill_switch()
            self.fb.set_rtdb("/commands/kill_switch", False)
            return

        # 3) nuova decisione ogni 15m
        if now - self.last_decision < 15 * 60:
            return
        self.last_decision = now
        if not self.regime or not self.selected:
            return

        self.refresh_selected_snapshots()
        memory = self._load_memory()
        recent = self.logger.recent(20)
        decision = self.orchestrator.decide(self.selected, self.regime, memory, recent)
        if decision is None:
            return
        if decision.asset in self.executor.open_positions:
            return
        if len(self.executor.open_positions) >= settings.MAX_OPEN_POSITIONS:
            return

        asset = self.selected.get(decision.asset)
        if not asset:
            return

        # 4) RISK GATE — ultimo controllo prima dell'ordine
        user = self.read_user_risk()
        params = self.risk.evaluate(decision, user, asset, self.account_equity(),
                                    volatility_sigma=self._volatility_sigma(asset))
        if not params.approved:
            print(f"[main] trade bloccato dal gate: {params.reject_reason}")
            return

        self.executor.open_position(asset, decision.strategy, decision.direction,
                                    params, confidence=decision.confidence)

    # ------------------------------------------------------------------ #
    def _load_memory(self):
        from bot.core.models import MemoryReport
        doc = self.fb.get_doc("memory", "30")
        if not doc:
            return None
        try:
            return MemoryReport(**doc)
        except Exception:  # noqa: BLE001
            return None

    @staticmethod
    def _volatility_sigma(asset) -> float:
        """Stima grezza della volatilità in sigma da ATR/prezzo su 1h."""
        i = asset.ind("1h")
        if not i or not i.atr or not asset.price:
            return 0.0
        atr_pct = i.atr / asset.price
        # mappa atr_pct in "sigma": 1% ~ 1σ, 3% ~ 3σ (euristica documentata)
        return atr_pct / 0.01

    def _persist_risk_state(self) -> None:
        self.fb.set_rtdb("/risk_state", self.circuit_breakers.to_dict())

    # ------------------------------------------------------------------ #
    def run(self, max_iterations: int | None = None, sleep_s: float = 30.0) -> None:
        print(f"[main] avvio bot @ {datetime.now(timezone.utc).isoformat()} "
              f"DRY_RUN={settings.DRY_RUN}")
        self.notifier.send(f"🟢 Bot avviato (DRY_RUN={settings.DRY_RUN})")
        it = 0
        while max_iterations is None or it < max_iterations:
            now = time.time()
            try:
                if now - self.last_regime >= settings.REGIME_INTERVAL_MINUTES * 60 or not self.regime:
                    self.refresh_regime(now)
                self.maybe_scan(now)
                self.trading_cycle(now)
                self.fb.set_rtdb("/bot_status/heartbeat", now)
            except Exception as exc:  # noqa: BLE001
                print(f"[main] errore nel ciclo: {exc}")
            it += 1
            if max_iterations is not None and it >= max_iterations:
                break
            time.sleep(sleep_s)


def main() -> None:
    TradingBot().run()


if __name__ == "__main__":
    main()
