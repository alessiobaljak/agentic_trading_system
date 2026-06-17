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
        self._params: dict[str, dict] = {}     # chiave "SYMBOL|strategy" -> params ottimizzati
        self._passed: set[str] = set()         # coppie "SYMBOL|strategy" che hanno passato OOS
        self._has_opt_data: bool = False
        self._generated_specs: dict[str, dict] = {}  # gen_id -> spec (strategie scoperte)
        self.load_weights()
        self.load_params()
        self.load_generated()

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

    # ------------------------------------------------------------------ #
    # Parametri ottimizzati per-asset (walk-forward, job autonomo)        #
    # ------------------------------------------------------------------ #
    def load_params(self) -> None:
        # preferisci il REGISTRO validato (coppie robuste, passate piu' volte);
        # se assente, ricadi sull'ultimo run (strategy_params/current).
        reg = self.fb.get_doc("strategy_registry", "validated") or {}
        validated = reg.get("validated") or []
        pairs = reg.get("pairs", {}) or {}
        if validated:
            self._passed = set(validated)
            self._params = {k: (pairs.get(k, {}).get("last_params", {}) or {}) for k in validated}
            self._has_opt_data = True
            return
        doc = self.fb.get_doc("strategy_params", "current") or {}
        entries = doc.get("entries", {}) or {}
        self._params = {}
        self._passed = set(doc.get("passed", []) or [])
        for key, e in entries.items():
            self._params[key] = e.get("params", {}) or {}
        self._has_opt_data = bool(entries)

    def params_for(self, symbol: str) -> dict[str, dict]:
        """{strategy: params} per l'asset (solo coppie ottimizzate)."""
        out: dict[str, dict] = {}
        prefix = f"{symbol}|"
        for key, params in self._params.items():
            if key.startswith(prefix):
                out[key[len(prefix):]] = params
        return out

    # ------------------------------------------------------------------ #
    # Strategie GENERATE (scoperte dal motore di discovery)              #
    # ------------------------------------------------------------------ #
    def load_generated(self) -> None:
        doc = self.fb.get_doc("discovered_strategies", "specs") or {}
        self._generated_specs = doc.get("specs", {}) or {}

    def generated_strategies_for(self, symbol: str) -> list:
        """Istanzia le strategie GENERATE che sono validate e abilitate per questo
        asset. Vengono trattate come tutte le altre (gate + pesi del learning)."""
        from bot.strategies.generated import GeneratedStrategy
        out = []
        for gen_id, spec in self._generated_specs.items():
            if self.is_enabled(symbol, gen_id):
                out.append(GeneratedStrategy(spec))
        return out

    def is_enabled(self, symbol: str, strategy: str) -> bool:
        """
        True se la coppia (asset, strategia) è abilitata a operare.
        Finché non esistono dati di ottimizzazione, TUTTO è abilitato (il bot
        funziona coi default). Quando l'ottimizzazione ha girato, opera SOLO le
        coppie che hanno passato la validazione out-of-sample.
        """
        if not self._has_opt_data:
            return True
        return f"{symbol}|{strategy}" in self._passed

    def is_baseline_cycle(self, rng: Optional[random.Random] = None) -> bool:
        """
        True con probabilità pari a BASELINE_CAPITAL_FRACTION: in tal caso il ciclo
        usa la configurazione baseline non adattata (riferimento anti-overfitting).
        """
        r = rng or random
        return r.random() < settings.BASELINE_CAPITAL_FRACTION
