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
from bot.core.costs import funding_fraction
from bot.core.indicators import compute_indicator_frame, snapshot_from_row
from bot.core.models import AssetSnapshot, Candle, Direction, Regime
from bot.config import settings
from bot.execution.exit_logic import (
    locked_stop, scale_ladder, scale_fills, ladder_multiples, mfe_in_r,
    breakeven_after_tp1,
)
from bot.strategies import get_all_strategies
from bot.strategies.base import StrategyContext

LEVERAGE_LEVELS = (2, 3, 5, 10, 20)


def pf_by_regime(trades) -> dict:
    """PF e numero di trade PER REGIME dai trade simulati. E' il dato che permette
    al bot di NON operare una coppia nel regime in cui il gate stesso l'ha vista
    perdere — e al learning di partire con un prior invece che da zero."""
    from collections import defaultdict
    acc: dict[str, list[float]] = defaultdict(list)
    for t in trades:
        acc[str(getattr(t, "regime_at_entry", "") or t.regime)].append(t.pnl_pct)
    out: dict[str, dict] = {}
    for regime, pnls in acc.items():
        gains = sum(x for x in pnls if x > 0)
        losses = -sum(x for x in pnls if x < 0)
        pf = (gains / losses) if losses > 0 else (99.0 if gains > 0 else 0.0)
        out[regime] = {"pf": round(pf, 3), "trades": len(pnls)}
    return out


def max_drawdown(trades) -> float:
    """Max drawdown della curva di equity dei trade IN SEQUENZA (cumulata dei
    pnl_pct). E' la misura della continuita': due strategie con lo stesso ritorno
    possono scavare buche molto diverse per arrivarci, e la buca e' cio' che in
    live diventa drawdown reale."""
    peak = equity = dd = 0.0
    for t in trades:
        equity += t.pnl_pct
        peak = max(peak, equity)
        dd = max(dd, peak - equity)
    return dd


def recency_weights(trades, half_life_days: float | None = None) -> list[float]:
    """Peso di ogni trade nella SCELTA DEI PARAMETRI: 1.0 per il piu' recente,
    dimezzato ogni `half_life_days`. Emivita <= 0 (o timestamp assenti) -> pesi
    uniformi, cioe' esattamente il comportamento storico."""
    hl = settings.GATE_RECENCY_HALFLIFE_DAYS if half_life_days is None else half_life_days
    ts = [float(getattr(t, "entry_ts", 0) or 0) for t in trades]
    if hl <= 0 or not ts or max(ts) <= 0:
        return [1.0] * len(ts)
    newest = max(ts)
    return [0.5 ** (max(0.0, newest - t) / 86400.0 / hl) if t > 0 else 0.0 for t in ts]


def weighted_score_parts(trades) -> tuple[float, float]:
    """(ritorno pesato, profit factor pesato) coi pesi di recency.

    Il ritorno e' RINORMALIZZATO sul numero di trade: senza, pesare abbasserebbe
    ogni somma e il punteggio finirebbe per premiare semplicemente chi ha piu'
    trade invece di chi va meglio ADESSO."""
    w = recency_weights(trades)
    tot_w = sum(w)
    if tot_w <= 0:
        return 0.0, 0.0
    n = len(trades)
    pnl = sum(wi * t.pnl_pct for wi, t in zip(w, trades)) * n / tot_w
    gains = sum(wi * t.pnl_pct for wi, t in zip(w, trades) if t.pnl_pct > 0)
    losses = -sum(wi * t.pnl_pct for wi, t in zip(w, trades) if t.pnl_pct < 0)
    pf = (gains / losses) if losses > 0 else (99.0 if gains > 0 else 0.0)
    return pnl, pf


def regime_ok(regime_pf: dict | None) -> bool:
    """False se ESISTE un regime, con campione sufficiente, in perdita marcata.

    Senza questo una coppia poteva validarsi vivendo di un solo regime: profitto
    enorme in trend, perdite in laterale, totale positivo -> promossa. Poi il paper
    la incontrava in laterale e perdeva. Non si pretende profitto ovunque (sarebbe
    troppo), si esige che nessun regime sia un buco conclamato."""
    if not regime_pf or settings.GATE_REGIME_MIN_PF <= 0:
        return True
    for rec in regime_pf.values():
        if not isinstance(rec, dict):
            continue
        try:
            n, pf = int(rec.get("trades", 0)), float(rec.get("pf", 99))
        except (TypeError, ValueError):
            continue
        if n >= settings.GATE_REGIME_MIN_TRADES and pf < settings.GATE_REGIME_MIN_PF:
            return False
    return True


def passes_gate(window_pnls: list[float], n_trades: int, pf: float,
                win_rate: float, total_return: float,
                max_dd: float | None = None,
                regime_pf: dict | None = None) -> bool:
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
    # CONTINUITA' trade-per-trade: le finestre la misurano ad anni, questo a ogni
    # trade — niente curve che scavano buche profonde per poi risalire.
    if max_dd is not None and max_dd > 0:
        if total_return / max_dd < settings.GATE_MIN_RECOVERY:
            return False
    if not regime_ok(regime_pf):
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
    # massima escursione FAVOREVOLE in unita' di R: dice DOVE arriva davvero il prezzo
    # prima di tornare. E' la misura che rende decidibile la scala dei TP (da questo
    # numero si sa quali gradini avrebbe colpito qualunque scala).
    mfe_r: float = 0.0
    # istante d'ingresso (epoch): permette di pesare i trade RECENTI piu' dei vecchi
    # nella scelta dei parametri. 0 = sconosciuto -> peso uniforme.
    entry_ts: float = 0.0
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
                 interval_hours: float = 1.0, funding_rate_provider=None) -> None:
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
        # provider OPZIONALE del tasso funding REALE per-coin (data_loader.funding_rate_for
        # nei run veri; None nei test/offline -> usa il default flat). Cache per simbolo.
        self._funding_provider = funding_rate_provider
        self._funding_rate_cache: dict[str, float] = {}
        self._htf_cache: dict = {}    # slice -> (frame_1h, h_idx) per la 1h reale
        self._prep_cache: dict = {}   # slice -> (snaps, regimes) per barra (riuso tra combo)
        self.regime_detector = RegimeDetector()
        self.strategies = get_all_strategies()

    def _symbol_funding(self, symbol: str) -> float:
        """Tasso funding per-8h da usare per QUESTA coin: reale (dal provider) se
        disponibile, altrimenti il default flat. Mai None."""
        if symbol not in self._funding_rate_cache:
            rate = None
            if self._funding_provider is not None:
                try:
                    rate = self._funding_provider(symbol)
                except Exception:  # noqa: BLE001
                    rate = None
            self._funding_rate_cache[symbol] = self.funding_per_8h if rate is None else rate
        return self._funding_rate_cache[symbol]

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

    # ------------------------------------------------------------------ #
    # 1H REALE nel backtest.
    # Regime detector e trend_following leggono ind("1h"): live e' la 1h VERA di
    # Binance, quindi anche il gate deve fornirla VERA (aggregata dalle candele del
    # timeframe base), non un alias della riga 15m — altrimenti si valida sotto
    # regimi sbagliati e la conferma dual-timeframe diventa una tautologia.
    # ------------------------------------------------------------------ #
    def _resample_1h(self, candles: list[Candle]) -> list[Candle]:
        """Aggrega le candele del timeframe base in candele 1h (OHLCV standard)."""
        buckets: dict = {}
        order: list = []
        for c in candles:
            ts = c.open_time.replace(minute=0, second=0, microsecond=0)
            b = buckets.get(ts)
            if b is None:
                buckets[ts] = [c.open, c.high, c.low, c.close, c.volume]
                order.append(ts)
            else:
                b[1] = max(b[1], c.high)
                b[2] = min(b[2], c.low)
                b[3] = c.close
                b[4] += c.volume
        return [Candle(open_time=ts, open=buckets[ts][0], high=buckets[ts][1],
                       low=buckets[ts][2], close=buckets[ts][3], volume=buckets[ts][4])
                for ts in order]

    def _htf_for(self, candles: list[Candle]):
        """(frame_1h, h_idx) per la serie data: h_idx[i] = indice dell'ULTIMA candela
        1h CHIUSA alla chiusura della barra i (-1 se nessuna: niente look-ahead sulla
        1h in formazione — il live, dopo il fix della candela parziale, fa lo stesso).
        None se il timeframe base e' gia' >= 1h (la riga e' gia' la 1h). Memoizzata
        per slice: l'optimizer richiama run_strategy molte volte sugli stessi dati."""
        if self.interval_hours >= 1.0 or not candles:
            return None
        key = (candles[0].open_time, candles[-1].open_time, len(candles))
        hit = self._htf_cache.get(key)
        if hit is not None:
            return hit
        from datetime import timedelta
        hc = self._resample_1h(candles)
        frame_1h = compute_indicator_frame(hc)
        bar = timedelta(hours=self.interval_hours)
        hour = timedelta(hours=1)
        h_idx, j = [], -1
        for c in candles:
            bar_close = c.open_time + bar
            while j + 1 < len(hc) and hc[j + 1].open_time + hour <= bar_close:
                j += 1
            h_idx.append(j)
        if len(self._htf_cache) > 8:      # slice diverse (finestre walk-forward)
            self._htf_cache.clear()
        self._htf_cache[key] = (frame_1h, h_idx)
        return self._htf_cache[key]

    def _snapshot_from_frame(self, symbol: str, frame, idx: int,
                             htf=None) -> AssetSnapshot:
        row = frame.iloc[idx]
        snap = AssetSnapshot(symbol=symbol, price=float(row["close"]))
        tf = settings.ORCHESTRATOR_TIMEFRAME
        ind = snapshot_from_row(row, tf)
        snap.indicators[tf] = ind
        # 1h REALE quando disponibile (timeframe base < 1h e storia sufficiente);
        # fallback: alias della riga base (comportamento storico, es. tf gia' 1h).
        ind1h = None
        if htf is not None:
            frame_1h, h_idx = htf
            if 0 <= idx < len(h_idx) and h_idx[idx] >= 0:
                ind1h = snapshot_from_row(frame_1h.iloc[h_idx[idx]], "1h")
        snap.indicators["1h"] = ind1h if ind1h is not None else snapshot_from_row(row, "1h")
        # alias di compatibilita' per consumatori legacy con chiavi fisse
        snap.indicators.setdefault("15m", ind)
        snap.indicators.setdefault("5m", ind)
        return snap

    def build_context(self, symbol: str, candles: list[Candle], frame=None) -> dict:
        """Mappa open_time -> AssetSnapshot per un asset di CONTESTO (es. BTC), così
        strategie cross-asset (momentum_cross_asset) sono validabili nel backtest."""
        if frame is None:
            frame = compute_indicator_frame(candles)
        htf = self._htf_for(candles)
        out: dict = {}
        for idx in range(len(frame)):
            snap = self._snapshot_from_frame(symbol, frame, idx, htf=htf)
            out[frame.iloc[idx]["open_time"]] = snap
        return out

    def _prepared(self, symbol: str, frame, candles: list[Candle]):
        """(snaps, regimes) per barra, MEMOIZZATO per slice. Snapshot e regime NON
        dipendono dalla strategia/combo: nell'optimizer run_strategy e' chiamata ~108
        volte per coin sugli STESSI dati -> calcolarli una volta sola e riusarli
        elimina il costo dominante a 15m (ricostruzione Pydantic barra-per-barra)."""
        key = (symbol, len(frame), frame.iloc[0]["open_time"], frame.iloc[-1]["open_time"])
        hit = self._prep_cache.get(key)
        if hit is not None:
            return hit
        htf = self._htf_for(candles)           # 1h REALE per regime/dual-timeframe
        snaps, regimes = [], []
        for idx in range(len(frame)):
            snap = self._snapshot_from_frame(symbol, frame, idx, htf=htf)
            regime = self.regime_detector.detect(snap)
            snap.regime = regime
            snaps.append(snap)
            regimes.append(regime)
        if len(self._prep_cache) > 4:          # tiene train+test della coin corrente
            self._prep_cache.clear()
        self._prep_cache[key] = (snaps, regimes)
        return snaps, regimes

    def run_strategy(self, strategy, symbol: str, candles: list[Candle], frame=None,
                     context_by_ts: dict | None = None) -> StrategyStats:
        stats = StrategyStats(strategy=strategy.name)
        if frame is None:
            frame = compute_indicator_frame(candles)
        cost = self._liquidity_cost(candles)   # costo reale di QUESTA coin (liquidita')
        snaps, regimes = self._prepared(symbol, frame, candles)
        i = self.window
        n = len(candles)
        while i < n - 1:
            snap = snaps[i]
            regime = regimes[i]
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

            # SCALE-OUT su multipli di R (se attivo): scala di TP + break-even dopo
            # il primo TP. Vuota -> percorso classico a TP unico (sotto).
            # I multipli vengono dai params della STRATEGIA se li porta (scala tarata
            # per questa coppia), altrimenti dal default globale: cosi' una coppia non
            # ancora ri-validata resta identica a come e' stata validata.
            _mults = ladder_multiples(getattr(strategy, "params", None))
            ladder = (scale_ladder(entry, stop, long, r_mults=_mults)
                      if settings.SCALE_OUT_ENABLED else [])

            mfe = entry          # miglior prezzo a favore, per la MISURA (non decide nulla)
            max_adverse = 0.0
            exit_price = entry
            j = i + 1
            horizon = min(n - 1, i + 96)
            best_fav = entry
            trailing_verdict = None

            if ladder:
                # --- percorso SCALE-OUT (parità con l'executor live) ---
                final_target = ladder[-1][0]
                stage = 0
                taken = 0.0
                realized_pct = 0.0
                stop_base = stop
                done = False
                while j <= horizon:
                    c = candles[j]
                    eff_stop = locked_stop(entry, final_target, long, best_fav, stop_base)
                    trailing = eff_stop != stop_base
                    adverse = (entry - c.low) / entry if long else (c.high - entry) / entry
                    max_adverse = max(max_adverse, adverse)
                    mfe = max(mfe, c.high) if long else min(mfe, c.low)
                    # 1) stop del RESIDUO (stop_base = entry dopo il primo TP)
                    stop_hit = (c.low <= eff_stop) if long else (c.high >= eff_stop)
                    if stop_hit:
                        ret = (eff_stop - entry) / entry if long else (entry - eff_stop) / entry
                        realized_pct += (1.0 - taken) * ret
                        exit_price = eff_stop
                        if trailing:
                            trailing_verdict = self._trailing_verdict(candles, j, horizon, stop, final_target, long)
                        done = True
                        break
                    # 2) fette di TP raggiunte in questa barra
                    stage, fills = scale_fills(ladder, stage, long, c.high, c.low)
                    for price, frac in fills:
                        ret = (price - entry) / entry if long else (entry - price) / entry
                        realized_pct += frac * ret
                        taken += frac
                        exit_price = price
                    if fills and breakeven_after_tp1(getattr(strategy, "params", None)):
                        stop_base = entry   # break-even sul residuo dopo il primo TP
                    if stage >= len(ladder):
                        done = True
                        break
                    best_fav = max(best_fav, c.high) if long else min(best_fav, c.low)
                    j += 1
                if not done:
                    c = candles[min(j, horizon)]
                    ret = (c.close - entry) / entry if long else (entry - c.close) / entry
                    realized_pct += (1.0 - taken) * ret
                    exit_price = c.close
                pnl_pct = realized_pct
            else:
                # --- percorso classico: TP unico pieno ---
                # simula l'evoluzione fino a SL/TP o fine finestra (max 96 barre)
                while j <= horizon:
                    c = candles[j]
                    # stop effettivo: base o alzato dal profit-lock (sui massimi passati)
                    eff_stop = locked_stop(entry, target, long, best_fav, stop)
                    trailing = eff_stop != stop   # il profit-lock ha alzato lo stop?
                    adverse = (entry - c.low) / entry if long else (c.high - entry) / entry
                    max_adverse = max(max_adverse, adverse)
                    mfe = max(mfe, c.high) if long else min(mfe, c.low)
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
            # uscite reali: fee+slippage (round-trip) + funding sui perpetual con SEGNO
            # per direzione e tasso REALE della coin (long paga / short incassa a tasso>0).
            held_hours = max(0, (min(j, horizon) - i)) * self.interval_hours
            funding = funding_fraction(self._symbol_funding(symbol), held_hours, long,
                                       default_rate=self.funding_per_8h)
            pnl_pct -= (cost + funding)
            stats.trades.append(SimTrade(
                strategy=strategy.name, regime=regime.value, direction=sig.direction.value,
                entry_price=entry, exit_price=exit_price, pnl_pct=pnl_pct,
                max_adverse_pct=max_adverse, confidence=sig.confidence,
                is_win=pnl_pct > 0, pnl=pnl_pct * self.capital, symbol=symbol,
                hour_bucket=candles[i].open_time.hour,
                confidence_at_entry=sig.confidence, regime_at_entry=regime.value,
                trailing_verdict=trailing_verdict,
                mfe_r=round(mfe_in_r(entry, mfe, stop), 3),
                entry_ts=candles[i].open_time.timestamp(),
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
