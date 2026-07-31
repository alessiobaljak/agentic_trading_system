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

from bot.agents.regime_detector import RegimeDetector
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
        # per il regime PER-COIN in parita' col backtest (stesso detector del bt)
        self.regime_detector = RegimeDetector()
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
        self, assets: dict[str, AssetSnapshot], regime: Regime,
        disabled: Optional[set] = None,
    ) -> list[dict]:
        """
        Raccoglie i segnali delle strategie attive nel regime corrente.
        Per OGNI asset istanzia le strategie con i PARAMETRI OTTIMIZZATI per quel
        coin (walk-forward) e opera solo le coppie (asset, strategia) che hanno
        passato la validazione out-of-sample. Le strategie in `disabled` (messe in
        panchina dall'adattamento real-time dopo perdite consecutive) sono saltate.
        """
        disabled = disabled or set()
        ctx_global = StrategyContext(all_assets=assets, regime=regime)
        signals = []
        for sym, asset in assets.items():
            # PARITA' COL BACKTEST: il regime e' rilevato PER-COIN dai dati di quella
            # coin (come engine.run_strategy), non l'unico macro-BTC. Cosi' su ogni
            # coin scattano le stesse strategie del GATE 1. Fuori parita': macro unico.
            if settings.BACKTEST_PARITY:
                coin_regime = self.regime_detector.detect(asset)
                asset.regime = coin_regime
                ctx = StrategyContext(all_assets=assets, regime=coin_regime)
            else:
                coin_regime = regime
                ctx = ctx_global
            params_by_strat = self.adaptation.params_for(sym)
            # strategie base (6) + strategie GENERATE validate per questo asset
            strategies = get_all_strategies(params_by_strat)
            strategies += self.adaptation.generated_strategies_for(sym)
            for strat in strategies:
                if strat.name in disabled:
                    continue
                if not strat.is_active_in(coin_regime):
                    continue
                if not self.adaptation.is_enabled(sym, strat.name):
                    continue
                # filtro di regime informato dal gate: non si opera una coppia nel
                # regime in cui il gate l'ha vista perdere (fail-open senza dati)
                if not self.adaptation.regime_ok(sym, strat.name, coin_regime):
                    continue
                sig = strat.generate_signal(asset, ctx)
                if sig is None:
                    continue
                weight = self.adaptation.weight_for(strat.name, coin_regime)
                signals.append({
                    "strategy": sig.strategy, "symbol": sig.symbol,
                    "direction": sig.direction.value, "confidence": sig.confidence,
                    "adjusted_confidence": sig.confidence * weight,
                    "weight": weight, "reasoning": sig.reasoning,
                    "coin_regime": coin_regime,   # per il tilt di trend (decide_all)
                    # SL/TP della STRATEGIA: stessi del backtest -> il risk manager
                    # li usa invece dei default fissi (parità GATE 1 <-> paper).
                    "suggested_stop": sig.suggested_stop,
                    "suggested_target": sig.suggested_target,
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
        disabled: Optional[set] = None,
    ) -> Optional[OrchestratorDecision]:
        signals = self.collect_signals(assets, regime, disabled=disabled)
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
    @staticmethod
    def _trend_align(regime: Optional[Regime], direction: str) -> float:
        """+1 se la direzione e' IN TREND, -1 se CONTROtrend, 0 se regime neutro
        (sideways/incertezza). Usato per il tilt di size sul trend."""
        if regime == Regime.BULL_TRENDING:
            return 1.0 if direction == Direction.LONG.value else -1.0
        if regime == Regime.BEAR_TRENDING:
            return 1.0 if direction == Direction.SHORT.value else -1.0
        return 0.0

    # ------------------------------------------------------------------ #
    def decide_all(
        self, assets: dict[str, AssetSnapshot], regime: Regime,
        disabled: Optional[set] = None,
    ) -> list[OrchestratorDecision]:
        """PARITA' COL BACKTEST: ritorna UNA decisione per OGNI coin con un segnale
        valido (sopra soglia, peso>0), prendendo la strategia migliore per quella
        coin. Niente LLM, niente 'scegli il migliore globale': come il backtest che
        apre ogni segnale indipendentemente. Vincolo conto reale: 1 posizione/coin."""
        signals = self.collect_signals(assets, regime, disabled=disabled)
        decisions: list[OrchestratorDecision] = []
        seen: set = set()
        for s in signals:  # ordinati per adjusted_confidence desc
            if s["adjusted_confidence"] < self.DECISION_THRESHOLD or s["weight"] <= 0.0:
                continue
            if s["symbol"] in seen:
                continue
            seen.add(s["symbol"])
            # TREND come contesto: modula la SIZE (non un veto). Il controtrend
            # (rispetto a trend della coin 60% + mercato 40%) apre piu' piccolo;
            # in-trend resta pieno. size_multiplier<=1 -> puo' solo ridurre.
            size_mult = 1.0
            if settings.TREND_TILT_ENABLED:
                align = (0.6 * self._trend_align(s.get("coin_regime"), s["direction"])
                         + 0.4 * self._trend_align(regime, s["direction"]))
                size_mult = max(0.5, 1.0 + settings.TREND_TILT_STRENGTH * min(0.0, align))
            d = OrchestratorDecision(
                asset=s["symbol"], strategy=s["strategy"],
                direction=Direction(s["direction"]), size_multiplier=size_mult,
                confidence=s["confidence"], reasoning=s.get("reasoning", ""),
                suggested_stop=s.get("suggested_stop"),
                suggested_target=s.get("suggested_target"))
            d.adjusted_confidence = s["adjusted_confidence"]
            decisions.append(d)
        self._record_status(
            regime, len(assets), signals, "decided" if decisions else "flat",
            f"parita' backtest: {len(decisions)} segnali validi aperti" if decisions
            else "nessun segnale valido sopra soglia",
            decisions[0] if decisions else None)
        return decisions

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
            suggested_stop=best.get("suggested_stop"),
            suggested_target=best.get("suggested_target"),
        )
