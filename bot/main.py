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
from bot.core.models import Direction, ExitReason, Regime, RiskSettings
from bot.agents.market_scanner import MarketScanner
from bot.agents.onchain_agent import OnChainAgent
from bot.agents.price_agent import PriceAgent
from bot.agents.price_stream import PriceStream
from bot.agents.regime_detector import RegimeDetector
from bot.agents.sentiment_agent import SentimentAgent
from bot.execution.executor import ExecutionEngine
from bot.execution.exit_logic import (breakeven_after_tp1, ladder_multiples,
                                      trailing_reason)
from bot.execution.notifier import TelegramNotifier
from bot.learning.adaptation import AdaptationEngine
from bot.learning.trade_logger import TradeLogger
from bot.orchestrator import Orchestrator
from bot.risk.circuit_breakers import CircuitBreakers
from bot.risk.correlation_guard import CorrelationGuard
from bot.risk.risk_manager import RiskManager


class TradingBot:
    def __init__(self) -> None:
        self.fb = get_firebase()
        self.price = PriceAgent()
        # stream dei trade in tempo reale: da' al paper la SEQUENZA dei prezzi, non
        # solo gli estremi aggregati di una candela. Degradazione automatica su REST.
        self.stream = PriceStream() if settings.EXEC_PRICE_STREAM_ENABLED else None
        # range della finestra rigiocata per ultima (rete di sicurezza post-replay)
        self._last_path_range: tuple[float | None, float | None] = (None, None)
        self.onchain = OnChainAgent()
        self.sentiment = SentimentAgent()
        self.scanner = MarketScanner(self.price, self.sentiment)
        self.regime_detector = RegimeDetector()
        self.adaptation = AdaptationEngine(self.fb)
        self.orchestrator = Orchestrator(self.adaptation)
        self.circuit_breakers = CircuitBreakers.from_dict(self.fb.get_rtdb("/risk_state"))
        self.risk = RiskManager(self.circuit_breakers)
        # guard di correlazione: era codice MORTO (0 import) fino all'audit del 04/08
        self.corr_guard = CorrelationGuard()
        self._price_cache: dict[str, tuple[float, list]] = {}   # symbol -> (ts, closes)
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
        # True se in QUESTO ciclo si e' chiuso un trade DETERMINATO dalla strategia
        # (SL/TP/trailing/time): fa ricalcolare i pesi SUBITO (learning event-driven).
        self._closed_this_cycle = False
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
        return float(eq) if eq else 1000.0

    def _used_margin(self) -> float:
        """Margine bloccato dalle posizioni aperte = somma(notional_RESIDUO/leva).
        Usa la quantita' RESIDUA: come Binance, quando una fetta (TP parziale) si
        chiude il suo margine si LIBERA subito e torna disponibile per nuovi trade."""
        return sum(p.remaining_qty * p.entry_price / max(p.leverage, 1.0)
                   for p in self.executor.open_positions.values())

    def _price_series(self, symbol: str, max_age_s: float = 1800.0) -> list:
        """Chiusure orarie recenti per la correlazione, con cache breve.

        Senza cache servirebbero N+1 chiamate a ogni decisione; con le posizioni
        aperte che cambiano di rado, mezz'ora di validita' e' abbondante."""
        now = time.time()
        hit = self._price_cache.get(symbol)
        if hit and now - hit[0] < max_age_s:
            return hit[1]
        try:
            candles = self.price.get_candles(symbol, "1h",
                                             limit=settings.CORRELATION_LOOKBACK_BARS)
        except Exception:  # noqa: BLE001
            return []
        closes = [c.close for c in candles]
        self._price_cache[symbol] = (now, closes)
        return closes

    def _correlation_blocks(self, symbol: str) -> str | None:
        """Motivo del blocco se aprire `symbol` creerebbe un grappolo di posizioni
        correlate, altrimenti None. FAIL-OPEN: senza storico non blocca nulla."""
        if not settings.CORRELATION_GUARD_ENABLED or not self.executor.open_positions:
            return None
        cand = self._price_series(symbol)
        if len(cand) < 3:
            return None
        opens = {sym: self._price_series(sym)
                 for sym in self.executor.open_positions if sym != symbol}
        opens = {k: v for k, v in opens.items() if len(v) >= 3}
        if not opens:
            return None
        ok, reason = self.corr_guard.can_open(symbol, cand, opens)
        return None if ok else reason

    def _directional_risk_blocks(self, direction, add_risk: float) -> str | None:
        """Motivo del blocco se il rischio nello STESSO verso supererebbe il tetto.

        Il cap sul NUMERO di posizioni non protegge: 5 long correlati rischiano
        quanto un unico trade con size 5x. Qui si somma il rischio vero di ognuna
        (distanza dallo stop ORIGINALE x quantita' residua)."""
        cap = settings.MAX_DIRECTIONAL_RISK_PCT
        if cap <= 0:
            return None
        eq = self.account_equity()
        if eq <= 0:
            return None
        same = sum(abs(p.entry_price - (p.orig_stop or p.stop_price)) * p.remaining_qty
                   for p in self.executor.open_positions.values()
                   if p.direction == direction)
        total = (same + max(0.0, add_risk)) / eq
        if total > cap:
            return (f"rischio direzionale {total*100:.1f}% > tetto {cap*100:.1f}% "
                    f"({direction.value}: gia' {same/eq*100:.1f}% impegnato)")
        return None

    def _sync_stream_symbols(self) -> None:
        """Tiene lo stream iscritto ESATTAMENTE ai simboli con posizioni aperte."""
        if self.stream is None:
            return
        try:
            self.stream.set_symbols(self.executor.open_positions.keys())
        except Exception as exc:  # noqa: BLE001
            print(f"[main] sync stream simboli fallito: {exc}")

    def _price_path(self, symbol: str, pos) -> list[float]:
        """Sequenza ORDINATA dei prezzi dall'ultima lettura, dallo stream.

        E' cio' che permette al paper di cogliere OGNI variazione nell'ordine in cui e'
        avvenuta, invece di schiacciarla in un massimo/minimo. Vuota se lo stream non
        c'e'/non e' sano o se il replay e' disattivato -> il chiamante usa il range
        aggregato delle candele. Memorizza anche il range della stessa finestra
        (`_last_path_range`) da usare come rete di sicurezza dopo il replay."""
        self._last_path_range = (None, None)
        if not (settings.EXEC_WICK_FILLS_ENABLED and settings.EXEC_PATH_REPLAY_ENABLED):
            return []
        if self.stream is None or not self.stream.is_healthy():
            return []
        path, hi, lo, truncated = self.stream.take(symbol)
        if hi is None:
            return []
        self._last_path_range = (hi, lo)
        if truncated:
            print(f"[main] percorso {symbol} troncato al tetto di punti: "
                  f"la coda e' coperta solo dagli estremi")
        return path

    def _wick_range(self, symbol: str, pos) -> tuple[float | None, float | None]:
        """Estremi (high/low) toccati dal prezzo da quando l'abbiamo guardato l'ultima volta.

        Serve per la PARITA' con il GATE, che riempie TP/SL quando l'OMBRA tocca il
        livello: il bot campiona ogni ~30s e da solo non vedrebbe i movimenti tra due
        letture. E' anche il comportamento del Binance REALE, dove gli ordini TP/SL
        restano appoggiati sul book ed è l'ombra a eseguirli.

        Due fonti, in ordine di qualita':
          1. STREAM WebSocket — vede ogni singolo trade, e il range e' esattamente la
             finestra [tick precedente, ora]. E' la fonte che risolve anche l'ORDINE
             dei prezzi dentro il minuto.
          2. candele 1m via REST — vede gli estremi ma non il loro ordine. Ripiego se
             lo stream non e' sano. Scarta le candele APERTE PRIMA dell'ingresso: il
             prezzo di prima che entrassimo non puo' riempire i nostri TP.

        (None, None) se non ci sono dati -> l'executor ricade sul solo mark price."""
        if not settings.EXEC_WICK_FILLS_ENABLED:
            return None, None
        # 1) stream in tempo reale: e' la fonte MIGLIORE (vede ogni trade, e il range
        # e' esattamente la finestra dal tick precedente a ora). take_range azzera,
        # quindi nessuna sovrapposizione tra tick.
        if self.stream is not None and self.stream.is_healthy():
            hi, lo = self.stream.take_range(symbol)
            if hi is not None:
                return hi, lo
        # 2) ripiego: candele 1m via REST (vede gli estremi, non il loro ordine)
        try:
            candles = self.price.get_candles(
                symbol, "1m", limit=max(2, settings.EXEC_WICK_LOOKBACK_1M))
        except Exception:  # noqa: BLE001
            return None, None
        fresh = [c for c in candles if c.open_time >= pos.entry_time]
        if not fresh:
            return None, None
        return max(c.high for c in fresh), min(c.low for c in fresh)

    def _settle_realized(self) -> None:
        """Accredita all'equity i PnL realizzati (fette scale-out + chiusure) accumulati
        dall'executor in questo tick — come Binance, ogni fill realizza sul saldo."""
        for delta in self.executor.pop_realized():
            self.apply_realized_pnl(delta)

    def reconcile_equity(self) -> float:
        """All'avvio ricalcola l'equity dalla fonte di verità (i trade chiusi):
        equity = capitale iniziale + somma di TUTTI i PnL realizzati. Così è
        sempre coerente coi trade chiusi (anche quelli chiusi prima di questa
        logica) e si auto-corregge dopo ogni riavvio."""
        base = self.fb.get_rtdb("/account/starting_equity")
        base = float(base) if base else 1000.0
        realized = sum(float(t.get("pnl", 0.0)) for t in self.logger.all_since(0.0))
        # + PnL delle FETTE gia' realizzate su posizioni ANCORA aperte (scale-out):
        # il loro trade non e' ancora loggato, ma il netto e' gia' in equity. Cosi'
        # dopo un restart a meta' trade l'equity resta coerente (nessun salto).
        open_realized = sum(p.realized_net for p in self.executor.open_positions.values())
        eq = base + realized + open_realized
        self.fb.set_rtdb("/account/equity", eq)
        print(f"[main] equity riconciliata: {eq:.2f} (base {base:.2f} + realizzato "
              f"{realized:+.2f} + fette aperte {open_realized:+.2f})")
        return eq

    def _log_closed(self, closed) -> None:
        """Registra un trade CHIUSO in modo non perdibile (WAL). Quando arriviamo
        qui la posizione e' gia' stata rimossa da memoria e da /positions: se
        logger.log fallisse (Firestore transitorio) il trade sparirebbe per sempre
        (equity mai piu' riconciliabile). Quindi: 1) record su RTDB /unlogged_trades,
        2) Firestore + equity, 3) cancella il WAL. I resti vengono recuperati da
        _replay_unlogged() all'avvio."""
        wal_path = f"/unlogged_trades/{closed.trade_id}"
        data = closed.model_dump(mode="json")
        try:
            self.fb.set_rtdb(wal_path, data)
        except Exception:  # noqa: BLE001
            pass          # WAL best-effort: senza, si procede come prima
        self.logger.log(closed)
        # NB: l'equity NON viene aggiornata qui: il PnL (fette + residuo) e' gia'
        # accreditato via _settle_realized() dagli eventi di realizzo dell'executor,
        # evitando il doppio conteggio con le fette parziali dello scale-out.
        try:
            self.fb.set_rtdb(wal_path, None)
        except Exception:  # noqa: BLE001
            pass

    def _replay_unlogged(self) -> None:
        """Completa i log rimasti a meta' (crash/errore tra chiusura e Firestore).
        Va chiamato PRIMA di reconcile_equity: cosi' l'equity ricalcolata include
        anche i trade recuperati (niente doppio conteggio del PnL)."""
        try:
            pending = self.fb.get_rtdb("/unlogged_trades") or {}
        except Exception:  # noqa: BLE001
            return
        if not isinstance(pending, dict):
            return
        from bot.core.models import ClosedTrade
        for tid, data in list(pending.items()):
            try:
                self.logger.log(ClosedTrade(**data))
                self.fb.set_rtdb(f"/unlogged_trades/{tid}", None)
                print(f"[main] trade {tid} recuperato dal WAL")
            except Exception as exc:  # noqa: BLE001
                print(f"[main] replay WAL {tid} fallito: {exc}")

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
            # SOLO osservabilita' (dashboard Sentiment): il Fear & Greed corrente.
            # Gia' calcolato sopra per il regime; qui e' un semplice output, non
            # influenza alcuna decisione/learning.
            "fear_greed": fng,
            # osservabilita': lo stream prezzi e' vivo? Se False il bot sta usando le
            # candele REST (funziona, ma non risolve l'ORDINE dei prezzi nel minuto).
            "price_stream": (self.stream.is_healthy() if self.stream is not None else False),
        })
        return self.regime

    def refresh_selected_snapshots(self) -> None:
        fng = self.onchain.fear_greed()
        for sym in list(self.selected.keys()):
            # pacing leggero: ~7 richieste/coin x 200 coin per ciclo e' vicino al
            # weight limit Binance (2400/min); 50ms/coin spalma il burst senza
            # allungare il ciclo in modo percettibile (10s su 200 coin).
            time.sleep(0.05)
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
        self._closed_this_cycle = False   # reset: settato se chiude un trade di strategia
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
            # PERCORSO dei prezzi dall'ultima lettura. Se lo stream lo fornisce, si
            # rigioca punto per punto (ordine reale, come Binance); altrimenti si usa
            # il range aggregato delle candele 1m (estremi senza ordine -> il peggio).
            path = self._price_path(sym, pos)
            if path:
                closed = self.executor.update_position_path(sym, path, price)
                # rete di sicurezza: un estremo filtrato dallo zigzag (o la coda di un
                # percorso troncato) verrebbe comunque colto dal range aggregato
                if closed is None and self._last_path_range != (None, None):
                    hi, lo = self._last_path_range
                    closed = self.executor.update_position(sym, price, high=hi, low=lo)
            else:
                hi, lo = self._wick_range(sym, pos)
                closed = self.executor.update_position(sym, price, high=hi, low=lo)
            if closed is not None:
                self._sync_stream_symbols()   # posizione chiusa -> disiscrivi il simbolo
            # accredita subito all'equity le fette realizzate (TP parziali) e/o la
            # chiusura finale — come Binance, ogni fill va sul saldo all'istante.
            self._settle_realized()
            if closed:
                eq = self.account_equity()
                # uscita DETERMINATA dalla strategia -> il learning va ricalcolato ora
                self._closed_this_cycle = True
                self._log_closed(closed)
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
                self._settle_realized()
                self._log_closed(closed)
                self.notifier.trade_closed(
                    closed.symbol, closed.strategy, closed.direction.value,
                    closed.exit_price, closed.pnl, closed.pnl_pct,
                    closed.exit_reason.value, dry_run=settings.DRY_RUN)
                self.circuit_breakers.register_trade_result(
                    closed.pnl / eq if eq else 0.0, False)
                self._persist_risk_state()
            self.fb.set_rtdb("/commands/close_position", None)

        # 2) kill switch — prezzi FRESCHI per ogni posizione aperta: gli snapshot
        # possono essere vecchi di 15m/4h e il fallback all'entry price registrerebbe
        # un PnL finto proprio nel percorso di emergenza.
        if self.kill_switch_active():
            prices: dict[str, float] = {}
            for s in list(self.executor.open_positions.keys()):
                p = self.price.get_mark_price(s)
                if p is None:
                    snap = self.selected.get(s)
                    p = snap.price if snap else None
                if p is not None:
                    prices[s] = p
            closed = self.executor.force_close_all(prices, ExitReason.KILL_SWITCH)
            self._settle_realized()
            for t in closed:
                self._log_closed(t)
            self.notifier.kill_switch()
            self.fb.set_rtdb("/commands/kill_switch", False)
            return

        # 3) nuova decisione a OGNI CANDELA CHIUSA del timeframe, ALLINEATA al
        # confine dell'orologio (xx:00/15/30/45), non a "N secondi dall'avvio del
        # processo": gli indicatori sono su barre chiuse (parita' col backtest),
        # quindi si decide subito dopo la chiusura della barra, come nel gate.
        itv = self._decision_interval_s
        boundary = (now // itv) * itv          # apertura della candela corrente
        if boundary <= self.last_decision or now - boundary < 5.0:
            return                             # barra non ancora chiusa/gia' decisa
        self.last_decision = boundary
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
        # short-circuit: conto gia' pienamente investito -> inutile valutare oltre.
        if settings.BACKTEST_PARITY and self._used_margin() >= self.account_equity():
            return

        asset = self.selected.get(decision.asset)
        if not asset:
            self._publish_decision_status({"outcome": "flat", "reason": "snapshot asset mancante"})
            return

        # DIVERSIFICAZIONE: aprire la 5a posizione correlata alle altre 4 non e'
        # diversificare, e' quintuplicare la stessa scommessa. Guard collegato
        # all'audit del 04/08 (prima era codice morto).
        corr_reason = self._correlation_blocks(decision.asset)
        if corr_reason:
            self._publish_decision_status({"outcome": "flat", "reason": corr_reason})
            return

        # sentiment/social SOLO per la coin che sta per essere tradata.
        try:
            sent = self.sentiment.get_sentiment(decision.asset)
            asset.sentiment_score = sent.get("sentiment_score")
            asset.social_volume = sent.get("social_volume")
        except Exception:  # noqa: BLE001
            pass

        # SENTIMENT TILT (live-only, come il trend tilt): se il sentiment della coin
        # e' CONTRO la direzione del trade, apri piu' piccolo (solo riduzione, mai
        # aumento). Niente dato -> nessuna penalita'. Non nel backtest -> parita' GATE1.
        if settings.SENTIMENT_TILT_ENABLED and asset.sentiment_score is not None:
            f = self._sentiment_size_factor(asset.sentiment_score, decision.direction)
            if f < 1.0:
                decision.size_multiplier = max(0.0, min(1.0, decision.size_multiplier * f))

        # RISK GATE — ultimo controllo prima dell'ordine.
        # Size e leva GUIDATE DAI DATI: convinzione del segnale × peso appreso della
        # strategia nel regime (adaptation.allocation). I cap di sicurezza (volatilita',
        # hard cap, 10%/posizione) restano tetto invalicabile dentro il risk manager.
        user = self.read_user_risk()
        rmult, lmult, alloc_note = self.adaptation.allocation(
            decision.strategy, asset.regime or self.regime or Regime.SIDEWAYS,
            decision.confidence, drift_key=(asset.symbol, decision.strategy))
        params = self.risk.evaluate(decision, user, asset, self.account_equity(),
                                    volatility_sigma=self._volatility_sigma(asset),
                                    risk_mult=rmult, lev_mult=lmult, alloc_note=alloc_note)
        if not params.approved:
            print(f"[main] trade bloccato dal gate: {params.reject_reason}")
            self._publish_decision_status(
                {"outcome": "flat", "reason": f"bloccato dal risk gate: {params.reject_reason}"})
            return

        # ESPOSIZIONE DIREZIONALE: qui il rischio del trade e' noto (distanza dallo
        # stop x quantita'), quindi si puo' sommare a quello gia' impegnato nello
        # stesso verso. Il cap sul NUMERO di posizioni non protegge da 5 scommesse
        # identiche; questo si'.
        trade_risk = abs(asset.price - params.stop_price) * params.quantity
        dir_reason = self._directional_risk_blocks(decision.direction, trade_risk)
        if dir_reason:
            print(f"[main] trade bloccato: {dir_reason}")
            self._publish_decision_status({"outcome": "flat", "reason": dir_reason})
            return

        # REALISMO PRODUZIONE: Binance rifiuta l'ordine se il margine libero non copre
        # il margine iniziale richiesto. Il paper fa lo stesso -> nessuna apertura che
        # in reale verrebbe respinta, niente over-allocazione oltre l'equity.
        new_margin = params.quantity * asset.price / max(params.leverage, 1.0)
        used = self._used_margin()
        eq = self.account_equity()
        if used + new_margin > eq:
            self._publish_decision_status(
                {"outcome": "flat",
                 "reason": (f"margine insufficiente (Binance rifiuterebbe): usato {used:.0f} + "
                            f"nuovo {new_margin:.0f} > equity {eq:.0f}")})
            return

        # scala di TP tarata per QUESTA coppia dal GATE (se l'ha gia' ri-validata).
        # Assente -> None -> l'executor usa il default globale, cioe' esattamente la
        # scala con cui quella coppia e' stata validata: registro misto ma coerente.
        _sparams = self.adaptation.params_for(asset.symbol).get(decision.strategy, {})
        pos = self.executor.open_position(asset, decision.strategy, decision.direction,
                                          params, confidence=decision.confidence,
                                          scale_r_mults=ladder_multiples(_sparams),
                                          sl_to_breakeven=breakeven_after_tp1(_sparams))
        if pos is not None:
            self._sync_stream_symbols()
            # i prezzi accumulati PRIMA dell'ingresso non possono riempire i suoi TP
            if self.stream is not None:
                self.stream.reset(pos.symbol)
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

    @staticmethod
    def _sentiment_size_factor(sentiment: float, direction: Direction) -> float:
        """Fattore di size in [SENTIMENT_TILT_FLOOR, 1.0] dal sentiment (0..1, 0.5
        neutro). Sentiment allineato alla direzione -> 1.0; contrario -> riduce fino
        al floor. Come il trend tilt: usa solo la parte CONTRARIA (min(0, align)),
        quindi puo' solo RIDURRE la size, mai aumentarla."""
        s = max(0.0, min(1.0, sentiment))
        align = (s - 0.5) * 2.0 if direction == Direction.LONG else (0.5 - s) * 2.0  # [-1,1]
        return max(settings.SENTIMENT_TILT_FLOOR,
                   1.0 + settings.SENTIMENT_TILT_STRENGTH * min(0.0, align))

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
            # trailing_stop E scale_out: entrambi tagliano il "runner" prima del TP
            # finale -> il controfattuale (tenere fino a TP3?) allena il keep trailing.
            if t.get("exit_reason") not in ("trailing_stop", "scale_out") \
                    or t.get("trailing_verdict") is not None:
                continue
            tp, sl, ex = t.get("take_profit_price"), t.get("stop_price"), t.get("exit_ts")
            if tp is None or sl is None or ex is None:
                continue   # dati mancanti
            try:
                candles = self.price.get_candles(
                    t.get("symbol", ""), settings.ORCHESTRATOR_TIMEFRAME, limit=300)
            except Exception:  # noqa: BLE001
                continue
            entry_ts = ex - float(t.get("duration_seconds", 0) or 0)
            during = [c for c in candles if entry_ts <= c.open_time.timestamp() <= ex]
            after = [c for c in candles if ex <= c.open_time.timestamp() <= ex + window_s]
            if len(after) < 2:
                continue   # servono un paio di candele DOPO l'uscita per il controfattuale
            long = str(t.get("direction", "")).lower() == "long"
            res = trailing_reason(during, after, float(t.get("entry_price", 0.0)),
                                  float(t.get("exit_price", 0.0)), float(sl), float(tp), long)
            # 'premature'/'protected' sono DEFINITIVI (TP o SL scattato dopo l'uscita)
            # -> si scrivono SUBITO, niente attesa di 24h. 'neutral' (ne' TP ne' SL)
            # e' valido solo a finestra piena; altrimenti aspetta piu' candele.
            if res["verdict"] == "neutral" and now - ex < window_s:
                continue
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
    def _publish_drift(self, trades: list[dict]) -> None:
        """Confronta il vissuto del paper con la promessa del gate e pubblica i
        verdetti su `drift/current`. Da li' due strade:
          * SUBITO: adaptation frena size/leva delle coppie in deriva (allocation);
          * alla passata successiva: optimize/discover leggono le derive CONFERMATE
            e le contano come fallimento -> auto-purge se anche la storia le boccia.
        E' l'anello che mancava: il paper non tara i parametri (li consumerebbe come
        training set) ma FALSIFICA cio' che il gate aveva promesso."""
        if not settings.DRIFT_ENABLED:
            return
        try:
            from bot.core.firebase_client import decode_pairs
            from bot.learning.drift import compute_drift, drifted_keys
            reg = self.fb.get_doc("strategy_registry", "validated") or {}
            doc = compute_drift(trades, decode_pairs(reg.get("pairs")))
            doc["updated_at"] = time.time()
            self.fb.set_doc("drift", "current", doc)
            self.adaptation._drift = doc          # effetto immediato, senza reload
            n = len(drifted_keys(doc))
            if n:
                print(f"[drift] {n} coppie in deriva confermata -> size/leva frenate, "
                      f"evidenza al gate alla prossima passata")
        except Exception as exc:  # noqa: BLE001
            print(f"[drift] calcolo saltato: {exc}")

    def _publish_calibration(self, trades: list[dict]) -> None:
        """Verifica che la confidenza dei segnali predica l'esito e pubblica il
        verdetto su `calibration/current`.

        La usiamo per modulare size e leva: se non predicesse nulla staremmo
        dimensionando le posizioni su un numero senza significato. Il verdetto
        RESTRINGE la sua influenza verso il neutro — mai la inverte."""
        if not settings.CALIBRATION_ENABLED:
            return
        from bot.learning.calibration import calibrate
        doc = calibrate(trades)
        doc["updated_at"] = time.time()
        self.fb.set_doc("calibration", "current", doc)
        self.adaptation._calibration = doc          # effetto immediato
        if doc.get("trust", 1.0) < 1.0:
            print(f"[calibrazione] {doc['verdict']}: {doc.get('note', '')} "
                  f"-> influenza confidenza x{doc['trust']:.2f}")

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
            # DERIVA dopo i pesi e in un try SUO: e' diagnostica, un suo errore non
            # deve mai impedire il ricalcolo dei pesi (che e' il learning primario).
            try:
                self._publish_drift(trades)
            except Exception as exc:  # noqa: BLE001
                print(f"[drift] pubblicazione saltata: {exc}")
            # anche questa e' diagnostica: in un try suo, non deve fermare i pesi
            try:
                self._publish_calibration(trades)
            except Exception as exc:  # noqa: BLE001
                print(f"[calibrazione] pubblicazione saltata: {exc}")
            # B2 — il TRAILING impara: keep del profit-lock per-strategia dai verdetti
            # (premature/protected + rumore vs inversione). Campione insufficiente ->
            # mappa senza quella strategia -> default globale validato dal gate.
            keep = metrics.compute_trailing_keep(trades)
            self.executor.trailing_keep = keep
            if keep:
                self.fb.set_rtdb("/trailing_keep", keep)   # visibilita' dashboard/debug
                print(f"[main] trailing keep adattato per {len(keep)} strategie: {keep}")
        except Exception as exc:  # noqa: BLE001
            print(f"[main] refresh_weights fallito: {exc}")

    # ------------------------------------------------------------------ #
    def run(self, max_iterations: int | None = None, sleep_s: float = 30.0) -> None:
        print(f"[main] avvio bot @ {datetime.now(timezone.utc).isoformat()} "
              f"DRY_RUN={settings.DRY_RUN}")
        self._replay_unlogged()   # recupera log a meta' PRIMA di riconciliare
        self.reconcile_equity()
        self._load_adapt_state()
        # esce dalla manutenzione: il bot e' di nuovo su -> il monitoraggio "offline"
        # torna attivo da solo (vedi scripts/monitor.py).
        self.fb.set_rtdb("/commands/maintenance", False)
        # stream prezzi: iscritto alle posizioni RIPRISTINATE dal restart
        if self.stream is not None:
            self.stream.start()
            self._sync_stream_symbols()
        self.notifier.send(f"🟢 Bot avviato (DRY_RUN={settings.DRY_RUN})")
        it = 0
        while max_iterations is None or it < max_iterations:
            now = time.time()
            try:
                # ricarica pesi + parametri ottimizzati (dal job notturno) ogni 6h
                # rete di sicurezza: verdetto trailing (B1) ~ogni barra, cosi' i verdetti
                # disponibili vengono scritti in fretta anche senza nuove chiusure.
                if now - self.last_trailing_eval >= self._decision_interval_s:
                    self.evaluate_pending_trailing(now)
                    self.last_trailing_eval = now
                # RETE DI SICUREZZA tempo-based: ricalcolo orario cosi' il recupero
                # in prova (probation, tempo-dipendente) avanza anche senza chiusure.
                # Il ricalcolo PRINCIPALE e' event-driven: subito dopo ogni trade
                # chiuso (vedi dopo trading_cycle).
                if now - self.last_weight_refresh >= 3600:
                    self.refresh_weights(now)
                    self.last_weight_refresh = now
                # ricarica il REGISTRO validato (coppie GATE 1 + specs generate +
                # params) OGNI ORA: cosi' il bot aggancia in fretta le nuove coppie
                # validate e il flag "ready" appena la copertura cresce, senza
                # aspettare 6h. Costo trascurabile (pochi doc). L'orario override.
                if now - self.last_adapt_reload >= settings.ADAPT_RELOAD_SECONDS:
                    self.adaptation.load_weights()
                    self.adaptation.load_params()
                    self.adaptation.load_generated()
                    self.last_adapt_reload = now
                if now - self.last_regime >= settings.REGIME_INTERVAL_MINUTES * 60 or not self.regime:
                    self.refresh_regime(now)
                self.maybe_scan(now)
                self.trading_cycle(now)
                # LEARNING EVENT-DRIVEN: se in questo ciclo si e' chiuso un trade
                # (determinato dalla strategia), ricalcola i pesi SUBITO invece di
                # aspettare la finestra oraria -> adattamento immediato ad ogni esito.
                if self._closed_this_cycle:
                    # 1) assegna i verdetti trailing ora disponibili (premature/protected
                    #    definitivi appena ci sono 2 candele dopo l'uscita), poi
                    # 2) ricalcola i pesi + il trailing-keep con i dati freschi.
                    self.evaluate_pending_trailing(time.time())
                    self.last_trailing_eval = time.time()
                    self.refresh_weights(time.time())
                    self.last_weight_refresh = time.time()
                    self._closed_this_cycle = False
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
