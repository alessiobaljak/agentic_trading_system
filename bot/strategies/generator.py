"""
Generatore di strategie — il motore che "inventa" nuove strategie come spec
dichiarative (vedi generated.py). Combina le feature della libreria con soglie
diverse: lo spazio è enorme (decine/centinaia di strategie sensate).

Due modalità:
  * generate_specs(n): campiona n strategie nuove (combinazioni di 1-3 feature).
  * mutate(spec): variazione di una strategia che funziona (evoluzione genetica),
    così il sistema esplora "intorno" alle vincenti senza perderle.

Tutto è deterministico dato il seed: run ripetibili e validabili.
"""
from __future__ import annotations

import random
from typing import Optional

from bot.strategies.generated import FEATURE_LIBRARY, spec_id

# feature direzionali "portanti" (danno la direzione del trade)
_DIRECTIONAL = [
    "rsi_extreme", "rsi_momentum", "bb_touch", "bb_break",
    "vwap_momentum", "vwap_reversion", "ema_cross", "macd_cross",
    "macd_hist", "price_ema", "macd_zero", "price_bb_mid",
    "stoch_extreme", "stoch_momentum",
]
# combinazioni incoerenti da evitare (mean-reversion + breakout sullo stesso segnale)
_INCOMPATIBLE = {
    frozenset({"bb_touch", "bb_break"}),
    frozenset({"vwap_momentum", "vwap_reversion"}),
    frozenset({"rsi_extreme", "rsi_momentum"}),
    frozenset({"stoch_extreme", "stoch_momentum"}),
}

_RSI_LOW = [20.0, 25.0, 30.0, 35.0]
_RSI_HIGH = [65.0, 70.0, 75.0, 80.0]
_RSI_MID = [45.0, 50.0, 55.0]
_STOCH_LOW = [10.0, 15.0, 20.0, 25.0]
_STOCH_HIGH = [75.0, 80.0, 85.0, 90.0]
_ATR_STOP = [1.0, 1.5, 2.0, 2.5]
_RR = [1.5, 2.0, 2.5, 3.0]
_VOL = [0.0, 0.0, 1.5, 2.0]      # spesso nessun filtro volume, a volte sì
_ADX = [0.0, 0.0, 0.0, 20.0, 25.0]  # spesso off; a volte richiede trend forte


def _feature_with_params(kind: str, rng: random.Random) -> dict:
    f = {"kind": kind}
    if kind == "rsi_extreme":
        f["low"] = rng.choice(_RSI_LOW)
        f["high"] = rng.choice(_RSI_HIGH)
    elif kind == "rsi_momentum":
        f["mid"] = rng.choice(_RSI_MID)
    elif kind == "stoch_extreme":
        f["low"] = rng.choice(_STOCH_LOW)
        f["high"] = rng.choice(_STOCH_HIGH)
    return f


def _coherent(kinds: list[str]) -> bool:
    s = set(kinds)
    if len(s) != len(kinds):
        return False
    return not any(pair <= s for pair in _INCOMPATIBLE)


def _build_spec(kinds: list[str], rng: random.Random) -> dict:
    spec = {
        "features": [_feature_with_params(k, rng) for k in kinds],
        "volume_mult": rng.choice(_VOL),
        "min_adx": rng.choice(_ADX),
        "atr_mult_stop": rng.choice(_ATR_STOP),
        "rr": rng.choice(_RR),
    }
    spec["id"] = spec_id(spec)
    return spec


def generate_specs(n: int, seed: int = 0, max_features: int = 3) -> list[dict]:
    """Genera fino a n strategie UNICHE (per id). Combinazioni di 1..max_features."""
    rng = random.Random(seed)
    seen: set[str] = set()
    out: list[dict] = []
    attempts = 0
    while len(out) < n and attempts < n * 40:
        attempts += 1
        k = rng.randint(1, max_features)
        kinds = rng.sample(_DIRECTIONAL, k)
        if not _coherent(kinds):
            continue
        spec = _build_spec(kinds, rng)
        if spec["id"] in seen:
            continue
        seen.add(spec["id"])
        out.append(spec)
    return out


def mutate(spec: dict, seed: int = 0) -> dict:
    """Variazione di una strategia vincente: cambia una soglia, o aggiunge/toglie
    una feature. Mantiene la coerenza. Per l'evoluzione attorno alle vincenti."""
    rng = random.Random(seed)
    kinds = [f["kind"] for f in spec.get("features", [])]
    choice = rng.random()
    if choice < 0.4 and len(kinds) < 3:
        candidates = [k for k in _DIRECTIONAL if _coherent(kinds + [k])]
        if candidates:
            kinds = kinds + [rng.choice(candidates)]
    elif choice < 0.7 and len(kinds) > 1:
        kinds.pop(rng.randrange(len(kinds)))
    child = _build_spec(kinds, rng)
    return child
