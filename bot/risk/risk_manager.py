"""
RiskManager — orchestrazione della sicurezza.

Implementa esplicitamente:
  1. LOGICA DI PRECEDENZA (resolve_effective_params): per ogni trade i valori
     effettivi di leverage e size sono il MINIMO tra:
        a) valore richiesto dall'utente (Firebase user_risk_settings)
        b) cap di sicurezza calcolato dal sistema (alta volatilità -> riduce)
        c) hard cap assoluto hardcoded (5x / 3%)
     => effective = min(user, system_safety, HARD_CAP)

  2. FINAL GATE (final_gate): l'ULTIMO controllo prima dell'invio dell'ordine.
     Qualsiasi richiesta (utente, LLM, strategia) lo attraversa. Riapplica i cap
     (difesa in profondità) e verifica i circuit breaker. Nessun ordine parte
     senza passare di qui.
"""
from __future__ import annotations

from typing import Optional

from bot.core.models import (
    AssetSnapshot,
    Direction,
    EffectiveRiskParams,
    OrchestratorDecision,
    RiskSettings,
)
from bot.config import settings
from bot.risk import hard_limits
from bot.risk.circuit_breakers import CircuitBreakers


class RiskManager:
    def __init__(self, circuit_breakers: Optional[CircuitBreakers] = None) -> None:
        self.circuit_breakers = circuit_breakers or CircuitBreakers()

    # ------------------------------------------------------------------ #
    # 1) Logica di precedenza                                            #
    # ------------------------------------------------------------------ #
    def resolve_effective_params(
        self,
        decision: OrchestratorDecision,
        user_settings: RiskSettings,
        asset: AssetSnapshot,
        account_equity: float,
        volatility_sigma: float = 0.0,
        risk_mult: float = 1.0,
        lev_mult: float = 1.0,
        alloc_note: str = "",
    ) -> EffectiveRiskParams:
        """
        Calcola leverage/size effettivi e i prezzi di SL/TP.
        `risk_mult`/`lev_mult` vengono dall'ALLOCAZIONE data-driven (convinzione del
        segnale × apprendimento, adaptation.allocation): scalano la base utente PRIMA
        dei cap, che restano tetto invalicabile (possono solo ridurre).
        Documenta nei `notes` cosa ha clampato cosa (tracciabilità).
        """
        notes: list[str] = []
        if alloc_note:
            notes.append(alloc_note)

        # (a) base utente, SCALATA dall'allocazione data-driven
        user_lev = float(user_settings.leverage)
        user_risk = float(user_settings.risk_per_trade)
        alloc_lev = max(1.0, user_lev * max(0.0, lev_mult))
        alloc_risk = user_risk * max(0.0, risk_mult)

        # (b) cap di sicurezza calcolati dal sistema (volatilità)
        sys_lev_cap = hard_limits.safety_leverage_cap(volatility_sigma)
        sys_risk_cap = hard_limits.safety_risk_cap(volatility_sigma)
        if sys_lev_cap < alloc_lev:
            notes.append(f"Leva ridotta da {alloc_lev:.1f}x a {sys_lev_cap}x per volatilità {volatility_sigma:.1f}σ")
        if sys_risk_cap < alloc_risk:
            notes.append(f"Size ridotta per alta volatilità ({volatility_sigma:.1f}σ)")

        # (c) hard cap assoluti (ultima difesa, possono solo ridurre)
        if alloc_lev > hard_limits.MAX_LEVERAGE:
            notes.append(f"Leva {alloc_lev:.1f}x oltre l'hard cap: limitata a {hard_limits.MAX_LEVERAGE}x")
        if alloc_risk > hard_limits.MAX_RISK_PER_TRADE:
            notes.append(f"Rischio {alloc_risk*100:.1f}% oltre l'hard cap: limitato a {hard_limits.MAX_RISK_PER_TRADE*100:.0f}%")

        # === precedenza: il valore più conservativo (minimo) ===
        eff_lev = min(alloc_lev, sys_lev_cap, hard_limits.MAX_LEVERAGE)
        # la leva sui futures e' un INTERO: Binance non accetta 2.02x. Arrotondo
        # (>=1) -> la leva dinamica si muove a gradini puliti (1x/2x/3x per
        # convinzione+learning), niente code decimali, e resta valida per l'ordine reale.
        eff_lev = float(max(1, min(round(eff_lev), int(hard_limits.MAX_LEVERAGE))))
        eff_risk = min(alloc_risk, sys_risk_cap, hard_limits.MAX_RISK_PER_TRADE)

        # il size_multiplier dell'orchestratore scala ulteriormente (<=1)
        eff_risk *= max(0.0, min(1.0, decision.size_multiplier))

        # --- SL/TP: prima scelta = quelli della STRATEGIA (== backtest GATE 1) ---
        # Se la decisione porta suggested_stop/target (dagli stessi atr_mult_stop/rr
        # validati out-of-sample), li usiamo TALI E QUALI: così il paper replica lo
        # stop/target del gate. Solo se assenti si ricade sui default fissi 1.5ATR/2RR.
        if decision.suggested_stop and decision.suggested_target:
            stop_price, take_profit = decision.suggested_stop, decision.suggested_target
        else:
            stop_price, take_profit = self._stop_target(asset, decision.direction)
            notes.append("SL/TP dai default risk manager (strategia senza suggested_stop/target)")
        price = asset.price
        risk_amount = account_equity * eff_risk         # $ a rischio
        per_unit_risk = abs(price - stop_price) if stop_price else None

        if not per_unit_risk or per_unit_risk <= 0:
            return EffectiveRiskParams(
                leverage=eff_lev, risk_per_trade=eff_risk, notional=0, quantity=0,
                stop_price=stop_price or 0, take_profit_price=take_profit or 0,
                user_leverage=user_lev, user_risk_per_trade=user_risk,
                safety_leverage_cap=sys_lev_cap, safety_risk_cap=sys_risk_cap,
                notes=notes, approved=False,
                reject_reason="Stop loss non calcolabile (ATR mancante)",
            )

        quantity = risk_amount / per_unit_risk           # size derivata dal rischio
        notional = quantity * price

        # vincolo da leva: il nozionale non può eccedere equity * leva
        max_notional = account_equity * eff_lev
        # cap PER-POSIZIONE: una singola posizione non usa piu' di una frazione
        # dell'equity come margine -> cosi' piu' strategie operano simultaneamente
        # e nessuna prende tutta la liquidita'. In parita' col backtest, default 10%.
        frac = settings.MAX_POSITION_EQUITY_FRACTION
        if settings.BACKTEST_PARITY and frac >= 1.0:
            frac = 0.10
        if frac < 1.0:
            max_notional = min(max_notional, account_equity * eff_lev * frac)
        if notional > max_notional:
            notes.append(f"Nozionale limitato (cap posizione {frac:.0%} equity)")
            notional = max_notional
            quantity = notional / price

        return EffectiveRiskParams(
            leverage=eff_lev,
            risk_per_trade=eff_risk,
            notional=notional,
            quantity=quantity,
            stop_price=stop_price,
            take_profit_price=take_profit,
            user_leverage=user_lev,
            user_risk_per_trade=user_risk,
            safety_leverage_cap=sys_lev_cap,
            safety_risk_cap=sys_risk_cap,
            notes=notes,
            approved=True,
        )

    @staticmethod
    def _stop_target(
        asset: AssetSnapshot, direction: Direction,
        atr_mult: float = 1.5, rr: float = 2.0,
    ) -> tuple[Optional[float], Optional[float]]:
        ind = asset.ind(settings.ORCHESTRATOR_TIMEFRAME)
        if not ind or not ind.atr:
            return None, None
        price = asset.price
        risk = atr_mult * ind.atr
        if direction == Direction.LONG:
            return price - risk, price + rr * risk
        return price + risk, price - rr * risk

    # ------------------------------------------------------------------ #
    # 2) Final gate — ultimo controllo prima dell'ordine                 #
    # ------------------------------------------------------------------ #
    def final_gate(self, params: EffectiveRiskParams) -> EffectiveRiskParams:
        """
        Ultimo cancello prima dell'invio dell'ordine. Idempotente e difensivo:
        riapplica gli hard cap (anche se già applicati) e blocca se un circuit
        breaker è attivo. Restituisce params eventualmente modificato con
        approved/reject_reason aggiornati.
        """
        # --- difesa in profondità: riapplica gli hard cap ---
        if params.leverage > hard_limits.MAX_LEVERAGE:
            params.leverage = hard_limits.MAX_LEVERAGE
            params.notes.append("[final_gate] leva ri-clampata all'hard cap 5x")
        if params.risk_per_trade > hard_limits.MAX_RISK_PER_TRADE:
            params.risk_per_trade = hard_limits.MAX_RISK_PER_TRADE
            params.notes.append("[final_gate] rischio ri-clampato all'hard cap 3%")

        # --- circuit breakers ---
        reason = self.circuit_breakers.blocking_reason()
        if reason is not None:
            params.approved = False
            params.reject_reason = f"[circuit_breaker] {reason}"
            return params

        if params.quantity <= 0 or params.notional <= 0:
            params.approved = False
            params.reject_reason = params.reject_reason or "Quantità/nozionale nullo"
            return params

        params.approved = True
        return params

    # ------------------------------------------------------------------ #
    # Helper end-to-end                                                  #
    # ------------------------------------------------------------------ #
    def evaluate(
        self,
        decision: OrchestratorDecision,
        user_settings: RiskSettings,
        asset: AssetSnapshot,
        account_equity: float,
        volatility_sigma: float = 0.0,
        risk_mult: float = 1.0,
        lev_mult: float = 1.0,
        alloc_note: str = "",
    ) -> EffectiveRiskParams:
        """resolve_effective_params + final_gate in un solo passaggio."""
        params = self.resolve_effective_params(
            decision, user_settings, asset, account_equity, volatility_sigma,
            risk_mult=risk_mult, lev_mult=lev_mult, alloc_note=alloc_note,
        )
        if not params.approved:
            return params
        return self.final_gate(params)
