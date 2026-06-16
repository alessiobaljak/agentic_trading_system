"""
Execution Engine — Binance Futures.

Caratteristiche:
  * limit order per minimizzare slippage
  * TP + SL piazzati immediatamente come ordini separati appena il fill è confermato
  * trailing stop attivato a +1 ATR di profitto
  * scale-out parziale: 50% al primo target, resto con trailing
  * scrive lo stato posizione su Firebase Realtime DB immediatamente

DRY_RUN:
  Lo STESSO codice gira in modalità simulata (settings.DRY_RUN=True): non invia
  ordini reali a Binance ma simula fill/PnL su dati live, e scrive comunque lo
  stato su Firebase. È il GATE 2 (paper trading). Per andare live: DRY_RUN=False.

NB: l'ExecutionEngine NON decide la size/leva — riceve EffectiveRiskParams già
passati dal RiskManager (final gate). Non c'è percorso che bypassi il gate.
"""
from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional

from bot.config import settings
from bot.core.firebase_client import get_firebase
from bot.core.models import (
    AssetSnapshot, ClosedTrade, Direction, EffectiveRiskParams, ExitReason, Regime,
)


@dataclass
class Position:
    position_id: str
    symbol: str
    strategy: str
    direction: Direction
    entry_price: float
    quantity: float
    leverage: float
    stop_price: float
    take_profit_price: float
    entry_time: datetime
    regime_at_entry: Regime
    # contesto per il trade logger
    indicators_at_entry: dict = field(default_factory=dict)
    sentiment_at_entry: Optional[float] = None
    fear_greed_at_entry: Optional[int] = None
    funding_at_entry: Optional[float] = None
    confidence_at_entry: Optional[float] = None
    # gestione trailing / scale-out
    scaled_out: bool = False
    trailing_active: bool = False
    high_water: float = 0.0          # miglior prezzo a favore visto
    atr: float = 0.0
    remaining_qty: float = 0.0

    def __post_init__(self):
        self.remaining_qty = self.quantity
        self.high_water = self.entry_price


class ExecutionEngine:
    def __init__(self, firebase=None, dry_run: Optional[bool] = None) -> None:
        self.fb = firebase or get_firebase()
        self.dry_run = settings.DRY_RUN if dry_run is None else dry_run
        self.open_positions: dict[str, Position] = {}
        self._client = None
        if not self.dry_run:
            self._init_binance()
        # CRITICO: ricarica le posizioni aperte da Firebase. Senza questo, ogni
        # riavvio del processo (anche un auto-restart di systemd dopo un crash)
        # parte con open_positions VUOTO -> le posizioni aperte prima diventano
        # orfane: ri-aperte con un nuovo entry e mai chiuse/loggate.
        self.restore_open_positions()

    def _init_binance(self) -> None:
        try:
            from binance.client import Client

            self._client = Client(
                settings.BINANCE_API_KEY, settings.BINANCE_API_SECRET,
                testnet=settings.BINANCE_TESTNET,
            )
            print("[execution] Binance client LIVE inizializzato"
                  f" ({'testnet' if settings.BINANCE_TESTNET else 'mainnet'})")
        except Exception as exc:  # noqa: BLE001
            print(f"[execution] init Binance fallito: {exc} -> forzo DRY_RUN")
            self.dry_run = True

    # ------------------------------------------------------------------ #
    # Apertura                                                           #
    # ------------------------------------------------------------------ #
    def open_position(
        self,
        asset: AssetSnapshot,
        strategy: str,
        direction: Direction,
        params: EffectiveRiskParams,
        confidence: Optional[float] = None,
    ) -> Optional[Position]:
        """Apre una posizione. `params` DEVE provenire dal final gate (approved)."""
        if not params.approved or params.quantity <= 0:
            print(f"[execution] ordine rifiutato dal gate: {params.reject_reason}")
            return None

        ind15 = asset.ind("15m")
        pos = Position(
            position_id=str(uuid.uuid4()),
            symbol=asset.symbol, strategy=strategy, direction=direction,
            entry_price=asset.price, quantity=params.quantity, leverage=params.leverage,
            stop_price=params.stop_price, take_profit_price=params.take_profit_price,
            entry_time=datetime.now(timezone.utc), regime_at_entry=asset.regime or Regime.SIDEWAYS,
            indicators_at_entry={k: v.model_dump() for k, v in asset.indicators.items()},
            sentiment_at_entry=asset.sentiment_score, fear_greed_at_entry=asset.fear_greed,
            funding_at_entry=asset.funding_rate, confidence_at_entry=confidence,
            atr=(ind15.atr if ind15 and ind15.atr else 0.0),
        )

        if self.dry_run:
            print(f"[DRY_RUN] OPEN {direction.value} {pos.symbol} qty={pos.quantity:.4f} "
                  f"@ {pos.entry_price} lev={pos.leverage}x SL={pos.stop_price:.4f} "
                  f"TP={pos.take_profit_price:.4f}")
        else:
            self._submit_live_entry(pos)

        self.open_positions[pos.symbol] = pos
        self._write_position_state(pos, mark_price=pos.entry_price)
        return pos

    def _submit_live_entry(self, pos: Position) -> None:
        """Ordini reali: limit entry + SL e TP separati (riduce slippage)."""
        side = "BUY" if pos.direction == Direction.LONG else "SELL"
        opp = "SELL" if side == "BUY" else "BUY"
        try:
            self._client.futures_change_leverage(symbol=pos.symbol, leverage=int(pos.leverage))
            self._client.futures_create_order(
                symbol=pos.symbol, side=side, type="LIMIT", timeInForce="GTC",
                quantity=round(pos.quantity, 6), price=round(pos.entry_price, 6),
            )
            # SL e TP come ordini reduce-only separati
            self._client.futures_create_order(
                symbol=pos.symbol, side=opp, type="STOP_MARKET", reduceOnly=True,
                stopPrice=round(pos.stop_price, 6), quantity=round(pos.quantity, 6),
            )
            self._client.futures_create_order(
                symbol=pos.symbol, side=opp, type="TAKE_PROFIT_MARKET", reduceOnly=True,
                stopPrice=round(pos.take_profit_price, 6), quantity=round(pos.quantity / 2, 6),
            )
        except Exception as exc:  # noqa: BLE001
            print(f"[execution] errore ordine live {pos.symbol}: {exc}")

    # ------------------------------------------------------------------ #
    # Gestione posizione (trailing, scale-out, exit)                     #
    # ------------------------------------------------------------------ #
    def update_position(self, symbol: str, mark_price: float) -> Optional[ClosedTrade]:
        """
        Aggiorna una posizione col prezzo corrente. Gestisce SL/TP/trailing/scale-out.
        Ritorna un ClosedTrade se la posizione si chiude del tutto.
        """
        pos = self.open_positions.get(symbol)
        if pos is None:
            return None
        long = pos.direction == Direction.LONG
        favorable = (mark_price - pos.entry_price) if long else (pos.entry_price - mark_price)

        # aggiorna high water mark
        if long:
            pos.high_water = max(pos.high_water, mark_price)
        else:
            pos.high_water = min(pos.high_water, mark_price)

        # attivazione trailing a +1 ATR di profitto
        if not pos.trailing_active and pos.atr > 0 and favorable >= pos.atr:
            pos.trailing_active = True

        # scale-out parziale 50% al primo target (TP)
        if not pos.scaled_out:
            hit_tp = (mark_price >= pos.take_profit_price) if long else (mark_price <= pos.take_profit_price)
            if hit_tp:
                self._partial_close(pos, mark_price, 0.5)
                pos.scaled_out = True
                self._write_position_state(pos, mark_price)
                # il resto continua con trailing
                return None

        # stop loss
        hit_sl = (mark_price <= pos.stop_price) if long else (mark_price >= pos.stop_price)
        if hit_sl:
            return self._close(pos, mark_price, ExitReason.STOP_LOSS)

        # trailing stop: chiude se ritraccia di 1 ATR dal high water
        if pos.trailing_active and pos.atr > 0:
            give_back = (pos.high_water - mark_price) if long else (mark_price - pos.high_water)
            if give_back >= pos.atr:
                reason = ExitReason.TRAILING_STOP if pos.scaled_out else ExitReason.TRAILING_STOP
                return self._close(pos, mark_price, reason)

        self._write_position_state(pos, mark_price)
        return None

    def _partial_close(self, pos: Position, price: float, fraction: float) -> None:
        qty = pos.remaining_qty * fraction
        pos.remaining_qty -= qty
        if self.dry_run:
            print(f"[DRY_RUN] SCALE-OUT {fraction:.0%} {pos.symbol} @ {price}")
        elif self._client:
            side = "SELL" if pos.direction == Direction.LONG else "BUY"
            try:
                self._client.futures_create_order(
                    symbol=pos.symbol, side=side, type="MARKET",
                    reduceOnly=True, quantity=round(qty, 6))
            except Exception as exc:  # noqa: BLE001
                print(f"[execution] scale-out errore: {exc}")

    def _close(self, pos: Position, price: float, reason: ExitReason) -> ClosedTrade:
        if self.dry_run:
            print(f"[DRY_RUN] CLOSE {pos.symbol} @ {price} ({reason.value})")
        elif self._client:
            side = "SELL" if pos.direction == Direction.LONG else "BUY"
            try:
                self._client.futures_create_order(
                    symbol=pos.symbol, side=side, type="MARKET",
                    reduceOnly=True, quantity=round(pos.remaining_qty, 6))
            except Exception as exc:  # noqa: BLE001
                print(f"[execution] close errore: {exc}")

        trade = self._build_closed_trade(pos, price, reason)
        self.open_positions.pop(pos.symbol, None)
        # la rimozione del nodo non deve MAI impedire il logging del trade
        try:
            self.fb.set_rtdb(f"/positions/{pos.symbol}", None)
        except Exception as exc:  # noqa: BLE001
            print(f"[execution] pulizia nodo posizione {pos.symbol} fallita: {exc}")
        return trade

    def force_close_all(self, prices: dict[str, float], reason: ExitReason) -> list[ClosedTrade]:
        """Usato dal KILL SWITCH e dai circuit breaker per andare flat."""
        closed = []
        for sym in list(self.open_positions.keys()):
            price = prices.get(sym, self.open_positions[sym].entry_price)
            closed.append(self._close(self.open_positions[sym], price, reason))
        return closed

    # ------------------------------------------------------------------ #
    def _build_closed_trade(self, pos: Position, exit_price: float, reason: ExitReason) -> ClosedTrade:
        long = pos.direction == Direction.LONG
        gross = (exit_price - pos.entry_price) if long else (pos.entry_price - exit_price)
        pnl = gross * pos.quantity
        # PnL% sul margine impegnato (notional/leverage)
        margin = (pos.entry_price * pos.quantity) / max(pos.leverage, 1)
        pnl_pct = pnl / margin if margin else 0.0
        from bot.core.models import IndicatorSnapshot
        ind = {k: IndicatorSnapshot(**v) for k, v in pos.indicators_at_entry.items()}
        return ClosedTrade(
            trade_id=pos.position_id, symbol=pos.symbol, strategy=pos.strategy,
            direction=pos.direction, entry_time=pos.entry_time,
            exit_time=datetime.now(timezone.utc), entry_price=pos.entry_price,
            exit_price=exit_price, size=pos.quantity,
            notional=pos.entry_price * pos.quantity, leverage=pos.leverage,
            pnl=pnl, pnl_pct=pnl_pct, exit_reason=reason,
            regime_at_entry=pos.regime_at_entry, indicators_at_entry=ind,
            sentiment_at_entry=pos.sentiment_at_entry,
            fear_greed_at_entry=pos.fear_greed_at_entry,
            funding_at_entry=pos.funding_at_entry,
            confidence_at_entry=pos.confidence_at_entry,
        )

    def _write_position_state(self, pos: Position, mark_price: float) -> None:
        long = pos.direction == Direction.LONG
        gross = (mark_price - pos.entry_price) if long else (pos.entry_price - mark_price)
        unreal = gross * pos.remaining_qty
        self.fb.set_rtdb(f"/positions/{pos.symbol}", {
            "position_id": pos.position_id, "symbol": pos.symbol,
            "strategy": pos.strategy, "direction": pos.direction.value,
            "entry_price": pos.entry_price, "mark_price": mark_price,
            "quantity": pos.remaining_qty, "leverage": pos.leverage,
            "stop_price": pos.stop_price, "take_profit_price": pos.take_profit_price,
            "unrealized_pnl": unreal, "trailing_active": pos.trailing_active,
            "scaled_out": pos.scaled_out, "dry_run": self.dry_run,
            "updated_at": time.time(),
            # --- campi extra per ricostruire la posizione dopo un restart ---
            "original_quantity": pos.quantity, "remaining_qty": pos.remaining_qty,
            "entry_time": pos.entry_time.isoformat(),
            "regime_at_entry": pos.regime_at_entry.value,
            "atr": pos.atr, "high_water": pos.high_water,
            "indicators_at_entry": pos.indicators_at_entry,
            "sentiment_at_entry": pos.sentiment_at_entry,
            "fear_greed_at_entry": pos.fear_greed_at_entry,
            "funding_at_entry": pos.funding_at_entry,
            "confidence_at_entry": pos.confidence_at_entry,
        })

    # ------------------------------------------------------------------ #
    # Ripristino stato dopo un riavvio                                   #
    # ------------------------------------------------------------------ #
    def restore_open_positions(self) -> int:
        """Ricarica le posizioni aperte da Firebase (/positions) in memoria.
        Idempotente: salta i simboli già presenti. Ritorna quante ne ha caricate."""
        data = self.fb.get_rtdb("/positions")
        if not isinstance(data, dict) or not data:
            return 0
        restored = 0
        for sym, p in data.items():
            if not isinstance(p, dict) or sym in self.open_positions:
                continue
            try:
                self.open_positions[sym] = self._position_from_state(p)
                restored += 1
            except Exception as exc:  # noqa: BLE001
                print(f"[execution] impossibile ricaricare la posizione {sym}: {exc}")
        if restored:
            print(f"[execution] ricaricate {restored} posizioni aperte da Firebase "
                  f"(no orfani al riavvio): {list(self.open_positions.keys())}")
        return restored

    def _position_from_state(self, p: dict) -> Position:
        original_qty = float(p.get("original_quantity", p.get("quantity", 0.0)))
        pos = Position(
            position_id=p.get("position_id") or str(uuid.uuid4()),
            symbol=p["symbol"], strategy=p.get("strategy", "unknown"),
            direction=Direction(p["direction"]),
            entry_price=float(p["entry_price"]), quantity=original_qty,
            leverage=float(p.get("leverage", 1) or 1),
            stop_price=float(p.get("stop_price", 0.0) or 0.0),
            take_profit_price=float(p.get("take_profit_price", 0.0) or 0.0),
            entry_time=self._parse_dt(p.get("entry_time")),
            regime_at_entry=Regime(p.get("regime_at_entry", Regime.SIDEWAYS.value)),
            indicators_at_entry=p.get("indicators_at_entry") or {},
            sentiment_at_entry=p.get("sentiment_at_entry"),
            fear_greed_at_entry=p.get("fear_greed_at_entry"),
            funding_at_entry=p.get("funding_at_entry"),
            confidence_at_entry=p.get("confidence_at_entry"),
            atr=float(p.get("atr", 0.0) or 0.0),
        )
        # __post_init__ azzera remaining_qty/high_water: ripristino lo stato vivo
        pos.remaining_qty = float(p.get("remaining_qty", original_qty))
        pos.high_water = float(p.get("high_water", pos.entry_price) or pos.entry_price)
        pos.scaled_out = bool(p.get("scaled_out", False))
        pos.trailing_active = bool(p.get("trailing_active", False))
        return pos

    @staticmethod
    def _parse_dt(v) -> datetime:
        if isinstance(v, str):
            try:
                return datetime.fromisoformat(v)
            except ValueError:
                pass
        return datetime.now(timezone.utc)
