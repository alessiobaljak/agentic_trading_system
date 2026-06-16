"""
Orchestratore — chiamato ad ogni candela 15m chiusa.

Flusso:
  1. Raccoglie i segnali delle strategie ATTIVE nel regime corrente.
  2. Costruisce l'input strutturato (prompt.py) con il memory_report.
  3. Chiama Claude e valida l'output con Pydantic (OrchestratorDecision).
  4. ADATTAMENTO: moltiplica la confidenza per il peso strategia×regime
     (dal learning loop). Strategie con peso 0 vengono di fatto disattivate.

Fallback senza API: se ANTHROPIC_API_KEY non è impostata, usa un ensemble
deterministico dei segnali pesati dal learning (così il paper trading gira
senza spesa LLM). Il comportamento è documentato in docs/orchestrator.md.
"""
from __future__ import annotations

import json
import time
from typing import Optional

from bot.config import settings
from bot.core.models import (
    AssetSnapshot, Direction, MemoryReport, OrchestratorDecision, Regime,
)
from bot.learning.adaptation import AdaptationEngine
from bot.orchestrator.prompt import SYSTEM_PROMPT, build_user_message
from bot.strategies import get_all_strategies
from bot.strategies.base import StrategyContext


class Orchestrator:
    DECISION_THRESHOLD = 30  # confidenza aggiustata minima per agire (fallback)

    def __init__(self, adaptation: Optional[AdaptationEngine] = None) -> None:
        self.adaptation = adaptation or AdaptationEngine()
        self.strategies = get_all_strategies()
        # esito dell'ULTIMA decisione (osservabilità): pubblicato su Firebase da main
        self.last_status: dict = {}

    def _record_status(self, regime: Regime, n_assets: int, signals: list[dict],
                       outcome: str, reason: str,
                       decision: Optional[OrchestratorDecision] = None) -> None:
        best = signals[0] if signals else None
        self.last_status = {
            "ts": time.time(),
            "regime": regime.value,
            "assets_evaluated": n_assets,
            "signals_found": len(signals),
            "best_symbol": best["symbol"] if best else None,
            "best_strategy": best["strategy"] if best else None,
            "best_confidence": round(float(best["confidence"]), 1) if best else None,
            "best_adjusted": round(float(best["adjusted_confidence"]), 1) if best else None,
            "threshold": self.DECISION_THRESHOLD,
            "outcome": outcome,            # "flat" | "decided"
            "reason": reason,
            "chosen_asset": decision.asset if decision else None,
            "chosen_strategy": decision.strategy if decision else None,
        }

    # ------------------------------------------------------------------ #
    def collect_signals(
        self, assets: dict[str, AssetSnapshot], regime: Regime
    ) -> list[dict]:
        """
        Raccoglie i segnali delle strategie attive nel regime corrente.
        Per OGNI asset istanzia le strategie con i PARAMETRI OTTIMIZZATI per quel
        coin (walk-forward) e opera solo le coppie (asset, strategia) che hanno
        passato la validazione out-of-sample.
        """
        ctx = StrategyContext(all_assets=assets, regime=regime)
        signals = []
        for sym, asset in assets.items():
            params_by_strat = self.adaptation.params_for(sym)
            for strat in get_all_strategies(params_by_strat):
                if not strat.is_active_in(regime):
                    continue
                if not self.adaptation.is_enabled(sym, strat.name):
                    continue
                sig = strat.generate_signal(asset, ctx)
                if sig is None:
                    continue
                weight = self.adaptation.weight_for(strat.name, regime)
                signals.append({
                    "strategy": sig.strategy, "symbol": sig.symbol,
                    "direction": sig.direction.value, "confidence": sig.confidence,
                    "adjusted_confidence": sig.confidence * weight,
                    "weight": weight, "reasoning": sig.reasoning,
                })
        signals.sort(key=lambda s: s["adjusted_confidence"], reverse=True)
        return signals

    # ------------------------------------------------------------------ #
    def decide(
        self,
        assets: dict[str, AssetSnapshot],
        regime: Regime,
        memory_report: Optional[MemoryReport] = None,
        recent_trades: Optional[list[dict]] = None,
        macro_events: Optional[list[dict]] = None,
    ) -> Optional[OrchestratorDecision]:
        signals = self.collect_signals(assets, regime)
        if not signals:
            self._record_status(regime, len(assets), signals, "flat",
                                "nessun segnale dalle strategie attive in questo regime")
            return None

        if settings.ANTHROPIC_API_KEY:
            decision = self._decide_llm(
                list(assets.values()), signals, regime, memory_report,
                recent_trades or [], macro_events,
            )
        else:
            decision = self._decide_fallback(signals)

        if decision is None:
            best_adj = signals[0]["adjusted_confidence"]
            self._record_status(
                regime, len(assets), signals, "flat",
                f"miglior segnale {best_adj:.0f} sotto soglia {self.DECISION_THRESHOLD} "
                "(o LLM ha scelto flat)")
            return None

        # --- adattamento: aggiusta la confidenza col peso del learning ---
        weight = self.adaptation.weight_for(decision.strategy, regime)
        decision.adjusted_confidence = decision.confidence * weight
        # strategia di fatto disattivata in questo regime
        if weight <= 0.0:
            self._record_status(regime, len(assets), signals, "flat",
                                f"{decision.strategy} disattivata dal learning (peso 0)")
            return None
        self._record_status(regime, len(assets), signals, "decided",
                            "segnale valido sopra soglia", decision)
        return decision

    # ------------------------------------------------------------------ #
    def _decide_llm(
        self, assets, signals, regime, memory_report, recent_trades, macro_events
    ) -> Optional[OrchestratorDecision]:
        try:
            import anthropic

            client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
            user_msg = build_user_message(
                assets, signals, regime, memory_report, recent_trades, macro_events
            )
            resp = client.messages.create(
                model=settings.ANTHROPIC_MODEL,
                max_tokens=600,
                system=SYSTEM_PROMPT,
                messages=[{"role": "user", "content": user_msg}],
            )
            text = resp.content[0].text.strip()
            start, end = text.find("{"), text.rfind("}")
            data = json.loads(text[start:end + 1])
            if float(data.get("size_multiplier", 0)) <= 0:
                return None  # l'LLM ha scelto di stare flat
            return OrchestratorDecision(**{
                "asset": data["asset"], "strategy": data["strategy"],
                "direction": Direction(data["direction"]),
                "size_multiplier": float(data["size_multiplier"]),
                "confidence": float(data["confidence"]),
                "reasoning": data.get("reasoning", ""),
            })
        except Exception as exc:  # noqa: BLE001
            print(f"[orchestrator] LLM fallito ({exc}) -> fallback deterministico")
            return self._decide_fallback(signals)

    def _decide_fallback(self, signals: list[dict]) -> Optional[OrchestratorDecision]:
        """Ensemble deterministico: prende il segnale con confidenza aggiustata massima."""
        best = signals[0]
        if best["adjusted_confidence"] < 30:   # soglia minima per agire
            return None
        # size proporzionale alla confidenza aggiustata (0..1)
        size_mult = max(0.0, min(1.0, best["adjusted_confidence"] / 100.0))
        return OrchestratorDecision(
            asset=best["symbol"], strategy=best["strategy"],
            direction=Direction(best["direction"]),
            size_multiplier=size_mult, confidence=best["confidence"],
            reasoning=f"[fallback] {best['reasoning']} (peso={best['weight']:.2f})",
        )
