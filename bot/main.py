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
from bot.execution.exit_logic import trailing_reason
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
        self.last_trailing_eval = 0.0
        self.last_weight_refresh = 0.0
        # intervallo tra decisioni = durata del timeframe unico (es. 1h -> 3600s).
        # Cosi' l'orchestratore agisce a OGNI candela chiusa del timeframe validato.
        _tf_secs = {"1m": 60, "5m": 300, "15m": 900, "30m": 1800, "1h": 3600, "4h": 14400}
        self._decision_interval_s = _tf_secs.get(settings.ORCHESTRATOR_TIMEFRAME, 3600)
        self._coin_cooldown: dict[str, float] = {}    # symbol -> epoch in cooldown
        self._strat_streak: dict[str, int] = {}       # strategia -> stop consecutivi
        self._strat_cooldown: dict[str, float] = {}   # strategia -> epoch in panchina

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
        # UNIVERSO LIVE = le coin VALIDATE in GATE 1 (le uniche tradabili), non un
        # top-N per volume. Cosi' ogni coppia validata ha la possibilita' di generare
        # un segnale a ogni ciclo, invece di restare invisibile perche' fuori dai piu'
        # liquidi. Il filtro liquidita' dello scanner resta (scarta le illiquide).
        # In bootstrap (registro non ancora caricato) si ricade sullo scan per volume.
        coins = sorted(self.adaptation.validated_coins())
        if coins:
            results = self.scanner.scan(symbols=coins)
            regime = self.regime or self.refresh_regime(now)
            selected = self.scanner.select_assets(results, regime, top_n=len(results))
        else:
            results = self.scanner.scan()
            regime = self.regime or self.refresh_regime(now)
            selected = self.scanner.select_assets(results, regime)
        self.selected = {r.symbol: r.snapshot for r in selected}
        self.last_scan = now
        print(f"[main] valutate {len(self.selected)} coin validate "
              f"({len(coins)} nel registro): {list(self.selected.keys())}")

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
                # cooldown anti-whipsaw: dopo uno STOP, la coin è "calda"/choppy →
                # non rientrare su quella coin per qualche ora (evita il tritacarne).
                if was_sl:
                    self._coin_cooldown[closed.symbol] = now + settings.COOLDOWN_HOURS * 3600
                # adattamento real-time: una STRATEGIA che perde N volte di fila va
                # in panchina (il bot NON si ferma, continua con le altre strategie).
                st = closed.strategy
                if was_sl:
                    self._strat_streak[st] = self._strat_streak.get(st, 0) + 1
                    if self._strat_streak[st] >= settings.STRATEGY_LOSS_STREAK:
                        self._strat_cooldown[st] = now + settings.STRATEGY_COOLDOWN_HOURS * 3600
                        self._strat_streak[st] = 0
                        print(f"[main] strategia {st} in panchina dopo "
                              f"{settings.STRATEGY_LOSS_STREAK} stop consecutivi")
                else:  # vincita -> la strategia funziona di nuovo
                    self._strat_streak[st] = 0
                    self._strat_cooldown.pop(st, None)
                self._save_adapt_state()  # persiste i cooldown (sopravvivono ai riavvii)
                # perdita giornaliera come % del CAPITALE (USDT/equity), NON come
                # somma dei rendimenti-su-margine (che la leva amplifica ~Nx e
                # faceva scattare il breaker troppo presto).
                self.circuit_breakers.register_trade_result(closed.pnl / eq if eq else 0.0, was_sl)
                self._persist_risk_state()
                if self.circuit_breakers.state.daily_pnl_pct <= -0.03:
                    self.notifier.daily_loss(abs(self.circuit_breakers.state.daily_pnl_pct))

        # 1b) chiusura MANUALE di singole posizioni (richiesta dalla dashboard).
        # La dashboard scrive /commands/close_position/{symbol}=true; qui chiudiamo
        # quelle posizioni al mark price con PnL corretto (come un TP/SL), poi
        # azzeriamo il comando. Non tocca la logica di trading: agisce SOLO su
        # richiesta esplicita dell'utente.
        close_req = self.fb.get_rtdb("/commands/close_position") or {}
        if isinstance(close_req, dict) and close_req:
            for sym in list(close_req.keys()):
                pos = self.executor.open_positions.get(sym)
                if pos is None:
                    continue
                price = self.price.get_mark_price(sym)
                if price is None:
                    snap = self.selected.get(sym) or self.price.build_snapshot(sym)
                    price = snap.price if snap else pos.entry_price
                eq = self.account_equity()
                closed = self.executor._close(pos, price, ExitReason.MANUAL)
                self.logger.log(closed)
                self.apply_realized_pnl(closed.pnl)
                self.notifier.trade_closed(
                    closed.symbol, closed.strategy, closed.direction.value,
                    closed.exit_price, closed.pnl, closed.pnl_pct,
                    closed.exit_reason.value, dry_run=settings.DRY_RUN)
                self.circuit_breakers.register_trade_result(
                    closed.pnl / eq if eq else 0.0, False)
                self._persist_risk_state()
            self.fb.set_rtdb("/commands/close_position", None)

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
        if now - self.last_decision < self._decision_interval_s:
            return
        self.last_decision = now
        if not self.regime or not self.selected:
            return

        self.refresh_selected_snapshots()
        memory = self._load_memory()
        recent = self.logger.recent(20)
        # strategie temporaneamente in panchina (adattamento real-time).
        # In parita' col backtest il bench e' disattivato (il bt non lo ha).
        disabled = set() if settings.BACKTEST_PARITY else {
            s for s, until in self._strat_cooldown.items() if now < until}
        # PARITA' COL BACKTEST: il backtest apre OGNI segnale di ogni coppia (non
        # "il migliore del ciclo"). In parita' apriamo TUTTI i segnali validi del
        # ciclo (uno per coin); altrimenti la singola decisione migliore (LLM/fallback).
        if settings.BACKTEST_PARITY:
            for d in self.orchestrator.decide_all(self.selected, self.regime, disabled=disabled):
                self._try_open(d, now)
            self._publish_decision_status()
            return
        decision = self.orchestrator.decide(self.selected, self.regime, memory, recent,
                                            disabled=disabled)
        if decision is None:
            self._publish_decision_status()  # flat: motivo già in last_status
            return
        self._try_open(decision, now)

    # ------------------------------------------------------------------ #
    def _try_open(self, decision, now: float) -> None:
        """Apre UNA posizione dalla decisione (controlli + risk gate + executor).
        Se un controllo fallisce fa 'return' (salta questa decisione; in parita' il
        loop continua con le altre)."""
        if decision.asset in self.executor.open_positions:
            self._publish_decision_status(
                {"outcome": "flat", "reason": f"{decision.asset} già aperto"})
            return
        cd_until = self._coin_cooldown.get(decision.asset, 0.0)
        if not settings.BACKTEST_PARITY and now < cd_until:
            self._publish_decision_status(
                {"outcome": "flat",
                 "reason": f"cooldown su {decision.asset} dopo stop ({int((cd_until - now) / 60)}m)"})
            return
        # cap sul NUMERO di posizioni: in parita' disattivato (il bt non lo ha).
        if not settings.BACKTEST_PARITY and len(self.executor.open_positions) >= settings.MAX_OPEN_POSITIONS:
            self._publish_decision_status(
                {"outcome": "flat",
                 "reason": f"raggiunto il max di posizioni ({settings.MAX_OPEN_POSITIONS})"})
            return
        # in parita' niente over-leverage: stop alle aperture quando il margine usato
        # raggiunge l'equity (conto pienamente investito).
        if settings.BACKTEST_PARITY:
            used = sum(p.quantity * p.entry_price / max(p.leverage, 1.0)
                       for p in self.executor.open_positions.values())
            if used >= self.account_equity():
                return

        asset = self.selected.get(decision.asset)
        if not asset:
            self._publish_decision_status({"outcome": "flat", "reason": "snapshot asset mancante"})
            return

        # sentiment/social SOLO per la coin che sta per essere tradata.
        try:
            sent = self.sentiment.get_sentiment(decision.asset)
            asset.sentiment_score = sent.get("sentiment_score")
            asset.social_volume = sent.get("social_volume")
        except Exception:  # noqa: BLE001
            pass

        # RISK GATE — ultimo controllo prima dell'ordine
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
    def _load_adapt_state(self) -> None:
        """Ricarica cooldown coin/strategia da Firebase: così SOPRAVVIVONO ai
        riavvii del bot (prima erano solo in memoria e si azzeravano a ogni restart)."""
        d = self.fb.get_rtdb("/adapt_state") or {}
        try:
            self._coin_cooldown = {k: float(v) for k, v in (d.get("coin_cooldown") or {}).items()}
            self._strat_streak = {k: int(v) for k, v in (d.get("strat_streak") or {}).items()}
            self._strat_cooldown = {k: float(v) for k, v in (d.get("strat_cooldown") or {}).items()}
            n = sum(1 for v in self._coin_cooldown.values() if v > time.time())
            m = sum(1 for v in self._strat_cooldown.values() if v > time.time())
            print(f"[main] cooldown ricaricati: {n} coin, {m} strategie in panchina")
        except Exception as exc:  # noqa: BLE001
            print(f"[main] cooldown non ricaricati: {exc}")

    def _save_adapt_state(self) -> None:
        now = time.time()
        # tieni solo i cooldown ancora attivi (pulizia)
        self._coin_cooldown = {k: v for k, v in self._coin_cooldown.items() if v > now}
        self._strat_cooldown = {k: v for k, v in self._strat_cooldown.items() if v > now}
        self.fb.set_rtdb("/adapt_state", {
            "coin_cooldown": self._coin_cooldown,
            "strat_streak": self._strat_streak,
            "strat_cooldown": self._strat_cooldown,
            "updated_at": now,
        })

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
    def evaluate_pending_trailing(self, now: float, window_h: float = 24.0,
                                  max_eval: int = 15) -> None:
        """B1 (learning dal paper): assegna il verdetto trailing (prematuro/protetto)
        alle uscite TRAILING recenti che non ce l'hanno ancora, dal prezzo SUCCESSIVO
        reale (Binance). Il dato si accumula sui trade -> il learning potra' usarlo.
        Gira sul VPS (ha Binance), non nel learning notturno su GitHub (geo-bloccato)."""
        window_s = window_h * 3600
        try:
            trades = self.logger.recent(limit=100)
        except Exception:  # noqa: BLE001
            return
        done = 0
        for t in trades:
            if done >= max_eval:
                break
            if t.get("exit_reason") != "trailing_stop" or t.get("trailing_verdict") is not None:
                continue
            tp, sl, ex = t.get("take_profit_price"), t.get("stop_price"), t.get("exit_ts")
            if tp is None or sl is None or ex is None or now - ex < window_s:
                continue   # dati mancanti o finestra di 24h non ancora completa
            try:
                candles = self.price.get_candles(t.get("symbol", ""), "15m", limit=300)
            except Exception:  # noqa: BLE001
                continue
            entry_ts = ex - float(t.get("duration_seconds", 0) or 0)
            during = [c for c in candles if entry_ts <= c.open_time.timestamp() <= ex]
            after = [c for c in candles if ex <= c.open_time.timestamp() <= ex + window_s]
            if not after:
                continue
            long = str(t.get("direction", "")).lower() == "long"
            res = trailing_reason(during, after, float(t.get("entry_price", 0.0)),
                                  float(t.get("exit_price", 0.0)), float(sl), float(tp), long)
            t["trailing_verdict"] = res["verdict"]
            t["trailing_miss_to_tp"] = res["miss_to_tp"]      # quanto tragitto lasciato sul tavolo
            t["trailing_knockout_atr"] = res["knockout_atr"]  # rumore (<1) vs inversione reale
            try:
                self.fb.set_doc("trades", t["trade_id"], t)   # riscrive il doc + i campi
                done += 1
            except Exception:  # noqa: BLE001
                pass
        if done:
            print(f"[main] verdetto trailing assegnato a {done} trade paper")

    # ------------------------------------------------------------------ #
    def refresh_weights(self, now: float) -> None:
        """Ricalcola i pesi strategia×regime dai TRADE su Firestore (nessun Binance)
        e li salva. Stessa identica logica del job notturno (finestra 30g,
        metrics.compute_weights), ma ogni ora: cosi' le perdite recenti frenano una
        strategia in poche ore invece di aspettare la notte. E' aritmetica sul nostro
        registro (win/loss gia' scritti), quindi giralo pure sul VPS nel loop."""
        from bot.learning import metrics
        try:
            trades = self.logger.all_since(now - 30 * 86400)
            weights = metrics.compute_weights(trades)
            if weights:
                self.adaptation.save_weights(weights)   # save_weights ricarica anche in RAM
                print(f"[main] pesi ricalcolati: {len(weights)} coppie strat×regime "
                      f"da {len(trades)} trade (30g)")
        except Exception as exc:  # noqa: BLE001
            print(f"[main] refresh_weights fallito: {exc}")

    # ------------------------------------------------------------------ #
    def run(self, max_iterations: int | None = None, sleep_s: float = 30.0) -> None:
        print(f"[main] avvio bot @ {datetime.now(timezone.utc).isoformat()} "
              f"DRY_RUN={settings.DRY_RUN}")
        self.reconcile_equity()
        self._load_adapt_state()
        # esce dalla manutenzione: il bot e' di nuovo su -> il monitoraggio "offline"
        # torna attivo da solo (vedi scripts/monitor.py).
        self.fb.set_rtdb("/commands/maintenance", False)
        self.notifier.send(f"🟢 Bot avviato (DRY_RUN={settings.DRY_RUN})")
        it = 0
        while max_iterations is None or it < max_iterations:
            now = time.time()
            try:
                # ricarica pesi + parametri ottimizzati (dal job notturno) ogni 6h
                if now - self.last_trailing_eval >= 3600:   # verdetto trailing paper (B1)
                    self.evaluate_pending_trailing(now)
                    self.last_trailing_eval = now
                if now - self.last_weight_refresh >= 3600:   # ricalcolo pesi ogni ora (opzione A)
                    self.refresh_weights(now)
                    self.last_weight_refresh = now
                if now - self.last_adapt_reload >= 6 * 3600:
                    self.adaptation.load_weights()
                    self.adaptation.load_params()
                    self.adaptation.load_generated()
                    self.last_adapt_reload = now
                if now - self.last_regime >= settings.REGIME_INTERVAL_MINUTES * 60 or not self.regime:
                    self.refresh_regime(now)
                self.maybe_scan(now)
                self.trading_cycle(now)
            except Exception as exc:  # noqa: BLE001
                print(f"[main] errore nel ciclo: {exc}")
            finally:
                # heartbeat SEMPRE aggiornato a ogni iterazione, anche se il ciclo
                # ha lanciato un'eccezione o lo scan ha bloccato a lungo: indica
                # "il loop è vivo", non "il ciclo è andato a buon fine".
                self.fb.set_rtdb("/bot_status/heartbeat", time.time())
            it += 1
            if max_iterations is not None and it >= max_iterations:
                break
            time.sleep(sleep_s)


def main() -> None:
    TradingBot().run()


if __name__ == "__main__":
    main()
