"""
AdaptationEngine — applica i pesi appresi alle decisioni dell'orchestratore.

Meccanismo concreto (come da specifica):
  * I pesi strategia×regime sono su Firebase (strategy_weights/current),
    aggiornati ogni notte dal learning loop.
  * L'orchestratore moltiplica la propria confidenza per il peso della strategia
    nel regime corrente.
  * Strategie che performano male -> peso -> 0 (progressivamente disattivate).
  * Strategie che performano bene -> peso alto -> più capitale.

ANTI-OVERFITTING (baseline non adattata):
  * Una frazione fissa del capitale (config.BASELINE_CAPITAL_FRACTION, 20%) usa
    SEMPRE peso 1.0 per ogni strategia (configurazione baseline). Questo evita il
    collasso su pattern passati. Il metodo `is_baseline_cycle()` indica quando un
    ciclo va trattato come baseline.
"""
from __future__ import annotations

import random
from typing import Optional

from bot.config import settings
from bot.core.firebase_client import get_firebase
from bot.core.models import Regime, StrategyRegimeWeight


class AdaptationEngine:
    def __init__(self, firebase=None) -> None:
        self.fb = firebase or get_firebase()
        self._weights: dict[str, float] = {}   # chiave "strategy|regime" -> peso
        self.load_weights()

    # ------------------------------------------------------------------ #
    def load_weights(self) -> None:
        doc = self.fb.get_doc("strategy_weights", "current") or {}
        self._weights = {}
        for w in doc.get("weights", []):
            key = f"{w['strategy']}|{w['regime']}"
            self._weights[key] = float(w.get("weight", 1.0))

    def save_weights(self, weights: list[StrategyRegimeWeight]) -> None:
        self.fb.set_doc("strategy_weights", "current", {
            "weights": [w.model_dump(mode="json") for w in weights],
        })
        self.load_weights()

    # ------------------------------------------------------------------ #
    def weight_for(self, strategy: str, regime: Regime, baseline: bool = False) -> float:
        """
        Peso della strategia nel regime. Se `baseline` True (sleeve baseline),
        ritorna sempre 1.0 (configurazione non adattata).
        Default 1.0 quando non ci sono ancora dati di apprendimento.
        """
        if baseline:
            return 1.0
        return self._weights.get(f"{strategy}|{regime.value}", 1.0)

    def is_baseline_cycle(self, rng: Optional[random.Random] = None) -> bool:
        """
        True con probabilità pari a BASELINE_CAPITAL_FRACTION: in tal caso il ciclo
        usa la configurazione baseline non adattata (riferimento anti-overfitting).
        """
        r = rng or random
        return r.random() < settings.BASELINE_CAPITAL_FRACTION
