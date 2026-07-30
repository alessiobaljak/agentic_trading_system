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

import os
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional

from bot.config import settings
from bot.core.costs import funding_fraction, liquidity_spread
from bot.core.firebase_client import get_firebase
from bot.core.models import (
    AssetSnapshot, ClosedTrade, Direction, EffectiveRiskParams, ExitReason, Regime,
)
from bot.execution.exit_logic import (
    locked_stop, scale_ladder, scale_fills, mfe_in_r,
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
    # spread liquidità-dipendente (== backtest): fissato all'apertura dal volume 24h
    spread_cost: float = 0.0
    # gestione trailing / scale-out
    scaled_out: bool = False
    trailing_active: bool = False
    high_water: float = 0.0          # miglior prezzo a favore visto
    atr: float = 0.0
    remaining_qty: float = 0.0
    # scale-out (TP scaglionati su R): livello raggiunto, PnL lordo gia' realizzato
    # dalle fette chiuse, e stop base ORIGINALE (per calcolare R anche dopo il BE)
    scale_stage: int = 0
    realized_gross: float = 0.0
    realized_net: float = 0.0    # PnL NETTO gia' realizzato dalle fette (fee/spread dedotti), gia' accreditato all'equity
    orig_stop: float = 0.0
    # --- solo LIVE (DRY_RUN=False): ordini di protezione REALI sull'exchange ---
    # id dello STOP appoggiato sul book e prezzo a cui e' appoggiato: servono per
    # SOSTITUIRLO quando lo stop si muove (break-even dopo TP1, profit-lock).
    sl_order_id: Optional[int] = None
    exchange_stop: Optional[float] = None
    # scala di TP CONGELATA all'ingresso (multipli di R validati per questa coppia).
    # Congelarla e' essenziale: se venisse riletta dal registro a ogni tick, una
    # passata dell'ottimizzatore cambierebbe i TP di un trade GIA' APERTO — si
    # eseguirebbe un piano diverso da quello di ingresso, la dashboard mostrerebbe
    # altri numeri e in live gli ordini sul book non corrisponderebbero piu'.
    # None -> default globale (SCALE_OUT_R_MULTIPLES).
    scale_r_mults: Optional[tuple] = None

    def __post_init__(self):
        self.remaining_qty = self.quantity
        self.high_water = self.entry_price
        self.orig_stop = self.stop_price


class ExecutionEngine:
    def __init__(self, firebase=None, dry_run: Optional[bool] = None) -> None:
        self.fb = firebase or get_firebase()
        self.dry_run = settings.DRY_RUN if dry_run is None else dry_run
        self.open_positions: dict[str, Position] = {}
        self._client = None
        # STESSI costi del backtester (GATE 1): fee+slippage round-trip come
        # frazione del notional + funding sui perpetual proporzionale alle ore.
        # Così il PnL del paper è NETTO e coerente con la validazione.
        self.cost_per_trade = float(os.getenv("BACKTEST_COST_PER_TRADE", "0.0008"))
        self.funding_per_8h = float(os.getenv("BACKTEST_FUNDING_PER_8H", "0.0001"))
        # max holding: come l'orizzonte del backtest = 96 BARRE del timeframe
        # (24h a 15m, 96h a 1h). In ORE fisse divergerebbe dal gate al cambio
        # timeframe. EXEC_MAX_HOLD_HOURS (in ore) vince se impostato.
        from bot.config import timeframe_hours
        _tf_h = timeframe_hours(settings.ORCHESTRATOR_TIMEFRAME)
        self.max_hold_hours = float(os.getenv("EXEC_MAX_HOLD_HOURS", str(96 * _tf_h)))
        if not self.dry_run:
            self._init_binance()
        # CRITICO: ricarica le posizioni aperte da Firebase. Senza questo, ogni
        # riavvio del processo (anche un auto-restart di systemd dopo un crash)
        # parte con open_positions VUOTO -> le posizioni aperte prima diventano
        # orfane: ri-aperte con un nuovo entry e mai chiuse/loggate.
        # keep del profit-lock IMPARATO per-strategia (B2): aggiornato ogni ora dal
        # refresh del learning in main; vuoto = default globale per tutte.
        self.trailing_keep: dict[str, float] = {}
        # coda dei PnL NETTI realizzati (fette scale-out + residuo alla chiusura) che
        # il loop principale accredita all'equity: come Binance, ogni fill realizza
        # subito sul saldo. Svuotata da TradingBot dopo ogni update.
        self.realized_events: list[float] = []
        self.restore_open_positions()

    def pop_realized(self) -> list[float]:
        """Restituisce e AZZERA gli eventi di realizzo (da accreditare all'equity)."""
        ev = self.realized_events
        self.realized_events = []
        return ev

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
        scale_r_mults: Optional[tuple] = None,
    ) -> Optional[Position]:
        """Apre una posizione. `params` DEVE provenire dal final gate (approved)."""
        if not params.approved or params.quantity <= 0:
            print(f"[execution] ordine rifiutato dal gate: {params.reject_reason}")
            return None

        ind15 = asset.ind(settings.ORCHESTRATOR_TIMEFRAME)
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
            spread_cost=liquidity_spread(asset.volume_24h),   # == costo backtest
            scale_r_mults=tuple(scale_r_mults) if scale_r_mults else None,
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

    @staticmethod
    def _opposite(pos: Position) -> str:
        """Lato che CHIUDE la posizione (per gli ordini reduce-only SL/TP)."""
        return "SELL" if pos.direction == Direction.LONG else "BUY"

    def _submit_live_entry(self, pos: Position) -> None:
        """Ordini reali: limit entry + ordini di protezione (SL + scala TP)."""
        side = "BUY" if pos.direction == Direction.LONG else "SELL"
        try:
            self._client.futures_change_leverage(symbol=pos.symbol, leverage=int(pos.leverage))
            self._client.futures_create_order(
                symbol=pos.symbol, side=side, type="LIMIT", timeInForce="GTC",
                quantity=round(pos.quantity, 6), price=round(pos.entry_price, 6),
            )
        except Exception as exc:  # noqa: BLE001
            print(f"[execution] errore ordine live {pos.symbol}: {exc}")
            return
        self._place_protective_orders(pos)

    def _place_protective_orders(self, pos: Position) -> None:
        """Appoggia sul book TUTTO il piano di uscita, non solo un TP unico.

        Con lo SCALE-OUT attivo il piano e' una SCALA (30% a 1.5R, 30% a 3R, 40% a 5R):
        se piazzassimo un solo TP, gli ordini reali sull'exchange direbbero una cosa e la
        logica del bot un'altra. Ogni livello diventa quindi un TAKE_PROFIT_MARKET
        reduce-only con la SUA frazione di quantita'; l'ultima fetta prende il RESTO
        (evita che gli arrotondamenti lascino polvere non protetta).

        Lo STOP copre la quantita' piena: essendo reduce-only, Binance lo limita da solo
        alla size effettivamente aperta man mano che le fette si chiudono."""
        opp = self._opposite(pos)
        long = pos.direction == Direction.LONG
        ladder = scale_ladder(pos.entry_price, pos.orig_stop, long, r_mults=pos.scale_r_mults) if settings.SCALE_OUT_ENABLED else []
        try:
            resp = self._client.futures_create_order(
                symbol=pos.symbol, side=opp, type="STOP_MARKET", reduceOnly=True,
                stopPrice=round(pos.stop_price, 6), quantity=round(pos.quantity, 6),
            )
            pos.sl_order_id = (resp or {}).get("orderId") if isinstance(resp, dict) else None
            pos.exchange_stop = pos.stop_price
        except Exception as exc:  # noqa: BLE001
            print(f"[execution] errore STOP live {pos.symbol}: {exc}")

        targets = ladder or [(pos.take_profit_price, 1.0)]
        qty_left = pos.quantity
        for i, (price, frac) in enumerate(targets):
            last = i == len(targets) - 1
            qty = qty_left if last else round(pos.quantity * frac, 6)
            qty = min(qty, qty_left)
            if qty <= 0:
                continue
            try:
                self._client.futures_create_order(
                    symbol=pos.symbol, side=opp, type="TAKE_PROFIT_MARKET", reduceOnly=True,
                    stopPrice=round(price, 6), quantity=round(qty, 6),
                )
            except Exception as exc:  # noqa: BLE001
                print(f"[execution] errore TP live {pos.symbol} @ {price}: {exc}")
            qty_left -= qty

    def _sync_exchange_stop(self, pos: Position, new_stop: float) -> None:
        """Allinea lo STOP appoggiato sul book al nuovo stop deciso dalla logica
        (break-even dopo il primo TP, o profit-lock che lo alza). Senza questo
        l'exchange terrebbe lo stop ORIGINALE: la protezione esisterebbe solo nella
        memoria del bot, e un suo crash lascerebbe la posizione scoperta.
        Cancella-e-ripiazza (Binance non modifica in place gli stop)."""
        if self.dry_run or self._client is None:
            return
        if pos.exchange_stop is not None and abs(new_stop - pos.exchange_stop) < 1e-12:
            return
        if pos.sl_order_id is not None:
            try:
                self._client.futures_cancel_order(symbol=pos.symbol, orderId=pos.sl_order_id)
            except Exception as exc:  # noqa: BLE001
                print(f"[execution] cancel STOP {pos.symbol} fallito: {exc}")
        try:
            resp = self._client.futures_create_order(
                symbol=pos.symbol, side=self._opposite(pos), type="STOP_MARKET",
                reduceOnly=True, stopPrice=round(new_stop, 6),
                quantity=round(pos.remaining_qty, 6),
            )
            pos.sl_order_id = (resp or {}).get("orderId") if isinstance(resp, dict) else None
            pos.exchange_stop = new_stop
        except Exception as exc:  # noqa: BLE001
            # lo stop vecchio e' stato cancellato ma il nuovo non e' passato: la
            # posizione e' SCOPERTA sull'exchange -> segnalalo forte, il bot continua
            # a proteggerla via update_position (stop "software") fino al prossimo giro.
            pos.sl_order_id = None
            pos.exchange_stop = None
            print(f"[execution] ATTENZIONE: STOP non ripiazzato su {pos.symbol}: {exc}")

    # ------------------------------------------------------------------ #
    # Gestione posizione — ALLINEATA AL BACKTEST (GATE 1)                 #
    # ------------------------------------------------------------------ #
    def update_position(self, symbol: str, mark_price: float,
                        high: float | None = None,
                        low: float | None = None,
                        publish: bool = True) -> Optional[ClosedTrade]:
        """
        Esce TUTTA la posizione allo stop o al take-profit PIENO, esattamente come
        il backtest che valida le strategie. Lo stop può essere ALZATO dal
        profit-lock (stessa logica del backtest, bot/execution/exit_logic.py): se la
        posizione è andata in profitto blocca parte del guadagno invece di restituirlo.
        Uscita anche a fine orizzonte (max holding), come le 96 barre del backtester.

        `high`/`low`: estremi (OMBRE) del prezzo dall'ultima lettura. Il gate valuta i
        trigger sul range high/low della candela; il live campiona ogni ~30s e senza
        questi si perderebbe i movimenti tra due letture. Passandoli si ottiene la
        PARITA' col gate — e col Binance reale, dove gli ordini TP/SL sul book vengono
        eseguiti dall'ombra. Omessi -> si ricade sul solo `mark_price` (vecchio
        comportamento). Vengono sempre ALLARGATI al mark osservato, così nessun
        trigger che scattava prima puo' sparire.

        `publish=False`: non scrive lo stato su Firebase e non tocca gli ordini reali.
        Usato durante il REPLAY del percorso (update_position_path), dove i passi
        intermedi sono valutazioni, non fotografie da pubblicare.
        """
        pos = self.open_positions.get(symbol)
        if pos is None:
            return None
        long = pos.direction == Direction.LONG

        # range effettivo del tick: le ombre, mai piu' strette del mark osservato
        hi = mark_price if high is None else max(high, mark_price)
        lo = mark_price if low is None else min(low, mark_price)

        # `keep` per-strategia: IMPARATO dai verdetti trailing del paper (B1/B2);
        # assente dalla mappa (pochi dati) -> default globale validato dal gate.
        keep = self.trailing_keep.get(pos.strategy)
        # ORDINE (identico al motore del gate): lo stop effettivo si calcola sul
        # high_water dei tick PRECEDENTI; i trigger si valutano su questo range; il
        # high_water si aggiorna SOLO a fine tick (come best_fav a fine barra).
        # Perche': il range di un tick e' un insieme NON ORDINATO. Se l'estremo
        # favorevole armasse il profit-lock e l'estremo avverso dello stesso range lo
        # facesse scattare, ci regaleremmo un'uscita in profitto senza sapere quale dei
        # due sia arrivato prima. Il costo e' che il lock si arma un tick dopo (~30s).

        # SCALE-OUT su multipli di R (se attivo): scala di TP + break-even dopo il
        # primo TP. Vuota -> percorso classico a TP unico (sotto). R usa lo stop
        # ORIGINALE (orig_stop), non quello spostato a break-even.
        ladder = scale_ladder(pos.entry_price, pos.orig_stop, long, r_mults=pos.scale_r_mults) if settings.SCALE_OUT_ENABLED else []
        if ladder:
            final_target = ladder[-1][0]
            eff_stop = locked_stop(pos.entry_price, final_target, long, pos.high_water,
                                   pos.stop_price, keep=keep)
            pos.trailing_active = eff_stop != pos.orig_stop

            # 1) stop del RESIDUO (dopo il primo TP pos.stop_price = entry = break-even).
            #    PRIMA dei TP: se nello stesso range si toccano entrambi, l'ordine
            #    intra-candela e' ignoto -> si assume il caso PEGGIORE (come il gate).
            hit_sl = (lo <= eff_stop) if long else (hi >= eff_stop)
            if hit_sl:
                # tre esiti distinti (l'etichetta descrive COSA e' successo davvero):
                #  - SCALE_OUT: ha gia' bancato >=1 fetta (TP1/TP2) e il residuo esce
                #    sullo stop rialzato a break-even/profit-lock -> esito NETTO positivo
                #  - TRAILING_STOP: profit-lock armato senza aver bancato fette (raro)
                #  - STOP_LOSS: stoppato prima di qualsiasi TP -> perdita piena
                if pos.scaled_out:
                    reason = ExitReason.SCALE_OUT
                elif pos.trailing_active:
                    reason = ExitReason.TRAILING_STOP
                else:
                    reason = ExitReason.STOP_LOSS
                return self._close(pos, eff_stop, reason)

            # 2) fette di TP raggiunte (idempotente: `scale_stage` avanza e non torna,
            #    quindi rileggere la stessa ombra non riempie due volte lo stesso livello)
            new_stage, fills = scale_fills(ladder, pos.scale_stage, long, hi, lo)
            if fills:
                reached_final = new_stage >= len(ladder)
                partials = fills[:-1] if reached_final else fills
                for price, frac in partials:
                    self._partial_close(pos, price, pos.quantity * frac)
                pos.scale_stage = new_stage
                if settings.SCALE_OUT_SL_TO_BREAKEVEN:
                    pos.stop_price = pos.entry_price   # break-even sul residuo
                if reached_final:
                    last_price = fills[-1][0]
                    return self._close(pos, last_price, ExitReason.TAKE_PROFIT)

            # 3) uscita a fine orizzonte
            held_h = (datetime.now(timezone.utc) - pos.entry_time).total_seconds() / 3600.0
            if held_h >= self.max_hold_hours:
                return self._close(pos, mark_price, ExitReason.TIME_EXIT)

            # ombre nel high_water solo ORA (dopo i trigger): valgono per i tick
            # FUTURI, come il gate che aggiorna best_fav a fine barra
            pos.high_water = max(pos.high_water, hi) if long else min(pos.high_water, lo)
            # LIVE: lo stop sul book deve seguire quello deciso qui (break-even/profit-lock)
            if publish:
                intended = max(eff_stop, pos.stop_price) if long else min(eff_stop, pos.stop_price)
                self._sync_exchange_stop(pos, intended)
                self._write_position_state(pos, mark_price)
            return None

        # --- percorso classico: TP unico pieno (identico al backtest) ---
        eff_stop = locked_stop(pos.entry_price, pos.take_profit_price, long,
                               pos.high_water, pos.stop_price, keep=keep)
        pos.trailing_active = eff_stop != pos.stop_price

        # stop (base o alzato dal profit-lock). Se è stato alzato, l'uscita è in
        # profitto -> TRAILING_STOP; altrimenti è lo stop-loss vero e proprio.
        # Anche qui lo stop viene PRIMA del TP: caso peggiore se il range tocca entrambi.
        hit_sl = (lo <= eff_stop) if long else (hi >= eff_stop)
        if hit_sl:
            reason = ExitReason.TRAILING_STOP if pos.trailing_active else ExitReason.STOP_LOSS
            return self._close(pos, eff_stop, reason)

        # take profit PIENO (tutta la posizione al target, RR pieno)
        hit_tp = (hi >= pos.take_profit_price) if long else (lo <= pos.take_profit_price)
        if hit_tp:
            return self._close(pos, pos.take_profit_price, ExitReason.TAKE_PROFIT)

        # uscita a fine orizzonte (come l'orizzonte del backtester)
        held_h = (datetime.now(timezone.utc) - pos.entry_time).total_seconds() / 3600.0
        if held_h >= self.max_hold_hours:
            return self._close(pos, mark_price, ExitReason.TIME_EXIT)

        pos.high_water = max(pos.high_water, hi) if long else min(pos.high_water, lo)
        if publish:
            self._sync_exchange_stop(pos, eff_stop)   # LIVE: stop sul book = stop deciso qui
            self._write_position_state(pos, mark_price)
        return None

    def update_position_path(self, symbol: str, path: list[float],
                             mark_price: float) -> Optional[ClosedTrade]:
        """Rigioca il percorso dei prezzi UNO PER UNO, nell'ordine reale.

        E' la differenza tra "so che il prezzo e' passato da 103 e da 97" e "so che
        e' passato PRIMA da 103 e POI da 97": nel primo caso bisogna assumere il
        peggio, nel secondo si sa che il TP1 e' stato incassato prima dello stop.
        Ogni punto viene valutato con high=low=punto, quindi non c'e' nessun range
        ambiguo: e' la stessa cosa che farebbe la matching engine di Binance.

        La prima uscita interrompe il replay (il resto del percorso e' successo quando
        la posizione era gia' chiusa). Se nessun punto la chiude, si valuta il mark
        finale — che pubblica lo stato e allinea gli ordini reali."""
        for point in path:
            closed = self.update_position(symbol, point, high=point, low=point,
                                          publish=False)
            if closed is not None:
                return closed
        return self.update_position(symbol, mark_price)

    def _partial_close(self, pos: Position, price: float, qty: float) -> None:
        """Chiude una FETTA (qty assoluta) della posizione al prezzo dato e accumula
        il PnL lordo realizzato. Il residuo continua a correre. La contabilita' del
        PnL finale (fette + residuo, netto costi) e' in _build_closed_trade."""
        qty = min(qty, pos.remaining_qty)
        if qty <= 0:
            return
        long = pos.direction == Direction.LONG
        gross_unit = (price - pos.entry_price) if long else (pos.entry_price - price)
        pos.realized_gross += gross_unit * qty
        # PnL NETTO della fetta (fee+slippage round-trip sulla sua quota di notional;
        # il funding e' regolato in blocco alla chiusura finale in _build_closed_trade,
        # cosi' il PnL LOGGATO resta col modello di costo del backtest -> parita' GATE 1).
        # Come Binance: questo netto viene ACCREDITATO SUBITO all'equity.
        net = gross_unit * qty - (self.cost_per_trade + pos.spread_cost) * (pos.entry_price * qty)
        pos.realized_net += net
        self.realized_events.append(net)
        pos.remaining_qty -= qty
        pos.scaled_out = True
        if self.dry_run:
            print(f"[DRY_RUN] SCALE-OUT {qty:.4f} {pos.symbol} @ {price} "
                  f"(netto {net:+.4f}, residuo {pos.remaining_qty:.4f})")
        elif self._client:
            side = "SELL" if long else "BUY"
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
            # CANCELLA gli ordini condizionali rimasti (SL/TP piazzati all'apertura):
            # senza, restano ORFANI su Binance e possono chiudere a prezzi arbitrari
            # una posizione FUTURA sullo stesso simbolo. Il bot tiene al massimo una
            # posizione per simbolo, quindi cancel-all sul simbolo e' sicuro.
            try:
                self._client.futures_cancel_all_open_orders(symbol=pos.symbol)
            except Exception as exc:  # noqa: BLE001
                print(f"[execution] cancel ordini {pos.symbol} fallita: {exc} "
                      f"(POSSIBILI ORDINI ORFANI: verificare su Binance)")

        trade = self._build_closed_trade(pos, price, reason)
        # Accredita all'equity SOLO la parte non ancora realizzata dalle fette:
        # trade.pnl e' il TOTALE (fette + residuo, netto costi pieni); realized_net
        # e' gia' stato accreditato ai TP parziali. Cosi' la somma degli eventi ==
        # trade.pnl loggato (nessun doppio conteggio) e reconcile resta coerente.
        self.realized_events.append(trade.pnl - pos.realized_net)
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
        # PnL lordo = fette gia' realizzate (scale-out) + residuo al prezzo d'uscita.
        # Senza scale-out realized_gross=0 e remaining_qty=quantity -> identico a prima.
        gross_final = (exit_price - pos.entry_price) if long else (pos.entry_price - exit_price)
        gross_pnl = pos.realized_gross + gross_final * pos.remaining_qty
        # --- costi reali (come il backtester): fee+slippage round-trip + funding ---
        # sul notional PIENO (entry una volta + uscite che sommano all'intera size)
        notional = pos.entry_price * pos.quantity
        held_hours = max(0.0, (datetime.now(timezone.utc) - pos.entry_time).total_seconds() / 3600.0)
        # funding REALE con segno: usa il tasso della coin all'entrata; long paga /
        # short incassa quando il tasso e' positivo (viceversa se negativo).
        funding = funding_fraction(pos.funding_at_entry, held_hours, long,
                                   default_rate=self.funding_per_8h)
        cost = (self.cost_per_trade + pos.spread_cost + funding) * notional
        pnl = gross_pnl - cost                       # PnL NETTO in USDT
        # PnL% sul margine impegnato (notional/leverage)
        margin = notional / max(pos.leverage, 1)
        pnl_pct = pnl / margin if margin else 0.0
        from bot.core.models import IndicatorSnapshot
        ind = {k: IndicatorSnapshot(**v) for k, v in pos.indicators_at_entry.items()}
        return ClosedTrade(
            trade_id=pos.position_id, symbol=pos.symbol, strategy=pos.strategy,
            direction=pos.direction, timeframe=settings.ORCHESTRATOR_TIMEFRAME,
            entry_time=pos.entry_time,
            exit_time=datetime.now(timezone.utc), entry_price=pos.entry_price,
            exit_price=exit_price, size=pos.quantity,
            notional=pos.entry_price * pos.quantity, leverage=pos.leverage,
            pnl=pnl, pnl_pct=pnl_pct, exit_reason=reason,
            take_profit_price=pos.take_profit_price, stop_price=pos.stop_price,
            regime_at_entry=pos.regime_at_entry, indicators_at_entry=ind,
            sentiment_at_entry=pos.sentiment_at_entry,
            fear_greed_at_entry=pos.fear_greed_at_entry,
            funding_at_entry=pos.funding_at_entry,
            confidence_at_entry=pos.confidence_at_entry,
            scale_stage_reached=pos.scale_stage,
            realized_partial=round(pos.realized_net, 6),
            mfe_r=round(mfe_in_r(pos.entry_price, pos.high_water, pos.orig_stop), 3),
        )

    def _write_position_state(self, pos: Position, mark_price: float) -> None:
        long = pos.direction == Direction.LONG
        gross = (mark_price - pos.entry_price) if long else (pos.entry_price - mark_price)
        # UPNL NETTO = quanto incasseresti chiudendo ORA. Sottrae fee round-trip +
        # spread + funding MATURATO finora (i "mini charge" di Binance sulle perpetual,
        # proporzionali alle ore aperte). Stessa formula di _build_closed_trade, cosi'
        # l'UPNL mostrato coincide col PnL reale se chiudi adesso.
        notional = pos.entry_price * pos.remaining_qty
        held_hours = max(0.0, (datetime.now(timezone.utc) - pos.entry_time).total_seconds() / 3600.0)
        funding = funding_fraction(pos.funding_at_entry, held_hours, long,
                                   default_rate=self.funding_per_8h)
        accrued_funding = funding * notional
        costs = (self.cost_per_trade + pos.spread_cost) * notional + accrued_funding
        unreal = gross * pos.remaining_qty - costs
        # TP scaglionati (scale-out): livelli, quota, R e quali gia' raggiunti (per la
        # dashboard). Solo osservabilita'. Vuoto se scale-out disattivo (TP unico).
        tp_ladder = []
        if settings.SCALE_OUT_ENABLED:
            _mults = settings.SCALE_OUT_R_MULTIPLES
            tp_ladder = [
                {"price": round(pr, 6), "fraction": fr,
                 "r": (_mults[i] if i < len(_mults) else None),
                 "hit": i < pos.scale_stage}
                for i, (pr, fr) in enumerate(scale_ladder(pos.entry_price, pos.orig_stop, long, r_mults=pos.scale_r_mults))
            ]
        self.fb.set_rtdb(f"/positions/{pos.symbol}", {
            "position_id": pos.position_id, "symbol": pos.symbol,
            "strategy": pos.strategy, "direction": pos.direction.value,
            "entry_price": pos.entry_price, "mark_price": mark_price,
            "quantity": pos.remaining_qty, "leverage": pos.leverage,
            "stop_price": pos.stop_price, "take_profit_price": pos.take_profit_price,
            "tp_ladder": tp_ladder,
            # PnL gia' incassato dalle fette (TP parziali), gia' accreditato in equity
            "realized_partial": round(pos.realized_net, 4),
            "unrealized_pnl": unreal, "trailing_active": pos.trailing_active,
            "scaled_out": pos.scaled_out, "dry_run": self.dry_run,
            "updated_at": time.time(),
            # trasparenza costi sulla posizione aperta (funding maturato + ore)
            "accrued_funding": round(accrued_funding, 4), "held_hours": round(held_hours, 2),
            # senza questo, dopo un RESTART lo spread sparirebbe dai costi di
            # chiusura (PnL sovrastimato che avvelena il learning)
            "spread_cost": pos.spread_cost,
            # --- campi extra per ricostruire la posizione dopo un restart ---
            "original_quantity": pos.quantity, "remaining_qty": pos.remaining_qty,
            # stato scale-out (per non perdere fette/BE dopo un riavvio)
            "sl_order_id": pos.sl_order_id, "exchange_stop": pos.exchange_stop,
            "scale_r_mults": list(pos.scale_r_mults) if pos.scale_r_mults else None,
            "scale_stage": pos.scale_stage, "realized_gross": pos.realized_gross,
            "realized_net": pos.realized_net,
            "orig_stop": pos.orig_stop,
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
            spread_cost=float(p.get("spread_cost", 0.0) or 0.0),
        )
        # __post_init__ azzera remaining_qty/high_water: ripristino lo stato vivo
        pos.remaining_qty = float(p.get("remaining_qty", original_qty))
        pos.high_water = float(p.get("high_water", pos.entry_price) or pos.entry_price)
        pos.scaled_out = bool(p.get("scaled_out", False))
        pos.trailing_active = bool(p.get("trailing_active", False))
        pos.scale_stage = int(p.get("scale_stage", 0) or 0)
        pos.realized_gross = float(p.get("realized_gross", 0.0) or 0.0)
        pos.realized_net = float(p.get("realized_net", 0.0) or 0.0)
        # ordini di protezione LIVE: senza questi, dopo un restart il bot non saprebbe
        # QUALE stop cancellare e ne accumulerebbe uno nuovo a ogni spostamento
        _sid = p.get("sl_order_id")
        pos.sl_order_id = int(_sid) if _sid is not None else None
        _xs = p.get("exchange_stop")
        pos.exchange_stop = float(_xs) if _xs is not None else None
        # la scala congelata deve sopravvivere al restart, altrimenti la posizione
        # ripartirebbe con TP diversi da quelli con cui e' stata aperta
        _sm = p.get("scale_r_mults")
        pos.scale_r_mults = tuple(float(x) for x in _sm) if _sm else None
        pos.orig_stop = float(p.get("orig_stop", pos.stop_price) or pos.stop_price)
        return pos

    @staticmethod
    def _parse_dt(v) -> datetime:
        if isinstance(v, str):
            try:
                return datetime.fromisoformat(v)
            except ValueError:
                pass
        return datetime.now(timezone.utc)
