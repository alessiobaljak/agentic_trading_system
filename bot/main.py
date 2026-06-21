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
from bot.agents.sentiment_agent import SentimentAgent
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
        self.sentiment = SentimentAgent()
        self.scanner = MarketScanner(self.price, self.sentiment)
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
        self.last_adapt_reload = 0.0

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

    def reconcile_equity(self) -> float:
        """All'avvio ricalcola l'equity dalla fonte di verità (i trade chiusi):
        equity = capitale iniziale + somma di TUTTI i PnL realizzati. Così è
        sempre coerente coi trade chiusi (anche quelli chiusi prima di questa
        logica) e si auto-corregge dopo ogni riavvio."""
        base = self.fb.get_rtdb("/account/starting_equity")
        base = float(base) if base else 10_000.0
        realized = sum(float(t.get("pnl", 0.0)) for t in self.logger.all_since(0.0))
        eq = base + realized
        self.fb.set_rtdb("/account/equity", eq)
        print(f"[main] equity riconciliata: {eq:.2f} (base {base:.2f} + realizzato {realized:+.2f})")
        return eq

    def apply_realized_pnl(self, pnl: float) -> float:
        """Aggiorna l'equity col PnL realizzato di un trade chiuso e la persiste.
        Così il sizing dei trade successivi compone (equity sale -> rischio in $
        sale, e viceversa) e la dashboard mostra l'equity vera."""
        new_eq = self.account_equity() + float(pnl)
        self.fb.set_rtdb("/account/equity", new_eq)
        return new_eq

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
                # NB: niente sentiment per-coin qui. Le strategie usano SOLO indicatori
                # tecnici (RSI/Bollinger/MACD/…), non il sentiment: evitarlo permette di
                # valutare l'INTERO mercato liquido a ogni ciclo senza saturare CoinGecko.
                self.selected[sym] = snap

    # ------------------------------------------------------------------ #
    def trading_cycle(self, now: float) -> None:
        # 1) gestione posizioni aperte (trailing/scale-out/SL/TP)
        # Usa il MARK PRICE FRESCO a ogni tick (1 richiesta): le posizioni vanno
        # gestite sul prezzo vivo, non sullo snapshot che si aggiorna ogni 15m.
        for sym, pos in list(self.executor.open_positions.items()):
            price = self.price.get_mark_price(sym)
            if price is None:
                snap = self.selected.get(sym) or self.price.build_snapshot(sym)
                price = snap.price if snap else None
            if price is None:
                continue
            closed = self.executor.update_position(sym, price)
            if closed:
                self.logger.log(closed)
                eq = self.account_equity()
                self.apply_realized_pnl(closed.pnl)
                self.notifier.trade_closed(
                    closed.symbol, closed.strategy, closed.direction.value,
                    closed.exit_price, closed.pnl, closed.pnl_pct,
                    closed.exit_reason.value, dry_run=settings.DRY_RUN)
                was_sl = closed.exit_reason in (ExitReason.STOP_LOSS,)
                # perdita giornaliera come % del CAPITALE (USDT/equity), NON come
                # somma dei rendimenti-su-margine (che la leva amplifica ~Nx e
                # faceva scattare il breaker troppo presto).
                self.circuit_breakers.register_trade_result(closed.pnl / eq if eq else 0.0, was_sl)
                self._persist_risk_state()
                if self.circuit_breakers.state.daily_pnl_pct <= -0.03:
                    self.notifier.daily_loss(abs(self.circuit_breakers.state.daily_pnl_pct))

        # 2) kill switch
        if self.kill_switch_active():
            prices = {s: self.selected[s].price for s in self.selected if s in self.selected}
            closed = self.executor.force_close_all(prices, ExitReason.KILL_SWITCH)
            for t in closed:
                self.logger.log(t)
                self.apply_realized_pnl(t.pnl)
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
            self._publish_decision_status()  # flat: motivo già in last_status
            return
        if decision.asset in self.executor.open_positions:
            self._publish_decision_status(
                {"outcome": "flat", "reason": f"{decision.asset} già aperto"})
            return
        if len(self.executor.open_positions) >= settings.MAX_OPEN_POSITIONS:
            self._publish_decision_status(
                {"outcome": "flat",
                 "reason": f"raggiunto il max di posizioni ({settings.MAX_OPEN_POSITIONS})"})
            return

        asset = self.selected.get(decision.asset)
        if not asset:
            self._publish_decision_status({"outcome": "flat", "reason": "snapshot asset mancante"})
            return

        # sentiment/social SOLO per la coin che sta per essere tradata (1 chiamata,
        # non 100): arricchisce il contesto del trade (sentiment_at_entry) ed è il
        # segnale che il layer LLM usa quando attivo. I dati tecnici restano la base.
        try:
            sent = self.sentiment.get_sentiment(decision.asset)
            asset.sentiment_score = sent.get("sentiment_score")
            asset.social_volume = sent.get("social_volume")
        except Exception:  # noqa: BLE001
            pass

        # 4) RISK GATE — ultimo controllo prima dell'ordine
        user = self.read_user_risk()
        params = self.risk.evaluate(decision, user, asset, self.account_equity(),
                                    volatility_sigma=self._volatility_sigma(asset))
        if not params.approved:
            print(f"[main] trade bloccato dal gate: {params.reject_reason}")
            self._publish_decision_status(
                {"outcome": "flat", "reason": f"bloccato dal risk gate: {params.reject_reason}"})
            return

        pos = self.executor.open_position(asset, decision.strategy, decision.direction,
                                          params, confidence=decision.confidence)
        if pos is not None:
            self._publish_decision_status(
                {"outcome": "opened",
                 "reason": f"aperta {pos.symbol} {pos.direction.value} ({pos.strategy})"})
            self.notifier.trade_opened(
                pos.symbol, pos.strategy, pos.direction.value,
                pos.entry_price, pos.quantity, pos.leverage,
                pos.stop_price, pos.take_profit_price, dry_run=settings.DRY_RUN)

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

    def _publish_decision_status(self, extra: dict | None = None) -> None:
        """Pubblica su Firebase l'esito dell'ultima decisione (perché flat/aperto),
        così è leggibile dalla dashboard senza SSH."""
        status = dict(self.orchestrator.last_status)
        if extra:
            status.update(extra)
        if status:
            self.fb.set_rtdb("/decision_status", status)

    # ------------------------------------------------------------------ #
    def run(self, max_iterations: int | None = None, sleep_s: float = 30.0) -> None:
        print(f"[main] avvio bot @ {datetime.now(timezone.utc).isoformat()} "
              f"DRY_RUN={settings.DRY_RUN}")
        self.reconcile_equity()
        self.notifier.send(f"🟢 Bot avviato (DRY_RUN={settings.DRY_RUN})")
        it = 0
        while max_iterations is None or it < max_iterations:
            now = time.time()
            try:
                # ricarica pesi + parametri ottimizzati (dal job notturno) ogni 6h
                if now - self.last_adapt_reload >= 6 * 3600:
                    self.adaptation.load_weights()
                    self.adaptation.load_params()
                    self.adaptation.load_generated()
                    self.last_adapt_reload = now
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
