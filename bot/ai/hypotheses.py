"""GENERATORE DI IPOTESI — strategie con un meccanismo, non combinazioni a caso.

Il generatore casuale (`bot/strategies/generator.py`) estrae feature e soglie col
dado. Nessuna candidata ha una RAGIONE per funzionare, quindi fra le migliaia
testate sopravvivono quelle fortunate — che poi in produzione regrediscono. E'
il difetto misurato: 1464 coppie valutate per passata, PF 1.5 nel gate e 0.5 nel
paper.

Qui il modello propone poche spec ognuna con un `mechanism` dichiarato: perche'
quella combinazione dovrebbe catturare un comportamento reale di QUELLA coin.
Serve a due cose concrete:
  * un'ipotesi con un perche' e' falsificabile, una combinazione casuale no;
  * meno candidate = meno confronto multiplo = meno fortunati promossi.

COSA NON CAMBIA: le spec prodotte qui passano dallo STESSO gate delle altre,
senza sconti. Il modello sceglie cosa provare, non cosa e' valido.

SICUREZZA: l'output del modello e' testo. Ogni spec viene ricostruita campo per
campo contro il vocabolario chiuso del generatore (`FEATURE_LIBRARY`,
`_DIRECTIONAL`, `_INCOMPATIBLE`); quello che non combacia viene scartato, non
corretto. Cosi' una risposta storta produce meno candidate, mai una spec che il
motore non sa eseguire.
"""
from __future__ import annotations

from typing import Optional

from bot.ai.client import ask_json, available
from bot.strategies.generated import FEATURE_LIBRARY, spec_id
from bot.strategies.generator import _ATR_STOP, _DIRECTIONAL, _INCOMPATIBLE, _RR

# parametri numerici ammessi per feature, con intervallo. Fuori intervallo ->
# spec scartata: non si "corregge" l'output del modello, lo si rifiuta.
_FEATURE_PARAMS = {
    "rsi_extreme": {"low": (5.0, 45.0), "high": (55.0, 95.0)},
    "rsi_momentum": {"mid": (35.0, 65.0)},
    "stoch_extreme": {"low": (5.0, 40.0), "high": (60.0, 95.0)},
    "volatility_regime": {"vol_pct": (0.002, 0.10)},
    "trend_strength": {"adx_lo": (10.0, 40.0)},
    "volume_surge": {"vol_mult_feat": (1.05, 5.0)},
    "session": {"hour_from": (0, 23), "hour_to": (1, 24)},
}

SYSTEM = """\
Proponi strategie di trading per crypto futures come specifiche dichiarative.

Ogni proposta deve avere un MECCANISMO: perche' quella combinazione dovrebbe
catturare un comportamento reale del mercato su quella coin. Non "questi
indicatori insieme funzionano", ma "su una coin illiquida un picco di volume
precede il movimento perche' gli ordini grossi muovono il book".

Una proposta senza meccanismo plausibile e' inutile: e' quello che gia' fa un
generatore casuale, e la selezione poi premia la fortuna. Meglio 5 ipotesi
motivate che 50 combinazioni.

Vincoli (una spec che li viola viene scartata):
- almeno una feature DIREZIONALE;
- da 1 a 3 feature in tutto, senza ripetizioni;
- niente coppie contraddittorie (mean-reversion + breakout sullo stesso segnale).

Rispondi ESCLUSIVAMENTE con JSON:
{"specs": [
  {"mechanism": "perche' dovrebbe funzionare, 1-2 frasi",
   "features": [{"kind": "volume_surge", "vol_mult_feat": 2.0},
                {"kind": "stoch_momentum"}],
   "atr_mult_stop": 2.0, "rr": 2.5, "min_adx": 20.0, "volume_mult": 1.5}
]}"""


def _clean_feature(raw: dict) -> Optional[dict]:
    if not isinstance(raw, dict):
        return None
    kind = raw.get("kind")
    if kind not in FEATURE_LIBRARY:
        return None
    out = {"kind": kind}
    for name, (lo, hi) in _FEATURE_PARAMS.get(kind, {}).items():
        if name not in raw:
            return None          # parametro obbligatorio mancante -> scarta
        try:
            v = float(raw[name])
        except (TypeError, ValueError):
            return None
        if not (lo <= v <= hi):
            return None
        out[name] = v
    if kind == "session":        # le ore restano interi, e devono essere ordinate
        out["hour_from"], out["hour_to"] = int(out["hour_from"]), int(out["hour_to"])
        if out["hour_from"] >= out["hour_to"]:
            return None
    return out


def _clean_spec(raw: dict) -> Optional[dict]:
    """Ricostruisce una spec valida dai campi proposti, o None."""
    if not isinstance(raw, dict):
        return None
    feats = [f for f in (_clean_feature(x) for x in (raw.get("features") or [])) if f]
    kinds = [f["kind"] for f in feats]
    if not 1 <= len(feats) <= 3 or len(set(kinds)) != len(kinds):
        return None
    if not any(k in _DIRECTIONAL for k in kinds):
        return None              # senza direzionale la spec non sa dove andare
    if any(pair <= set(kinds) for pair in _INCOMPATIBLE):
        return None
    def _num(key, lo, hi, default):
        try:
            v = float(raw.get(key, default))
        except (TypeError, ValueError):
            return None
        return v if lo <= v <= hi else None
    atr = _num("atr_mult_stop", min(_ATR_STOP), max(_ATR_STOP), 1.5)
    rr = _num("rr", min(_RR), max(_RR), 2.0)
    adx = _num("min_adx", 0.0, 40.0, 0.0)
    vol = _num("volume_mult", 0.0, 5.0, 0.0)
    if None in (atr, rr, adx, vol):
        return None
    spec = {"features": feats, "volume_mult": vol, "min_adx": adx,
            "atr_mult_stop": atr, "rr": rr}
    spec["id"] = spec_id(spec)   # STESSA identita' delle spec casuali: niente corsie
    mech = str(raw.get("mechanism") or "").strip()
    if mech:
        # tracciabile: dopo la validazione si potra' chiedere se il meccanismo
        # dichiarato regge, non solo se i numeri tornano.
        spec["mechanism"] = mech[:400]
    return spec


def propose(n: int, market_context: str = "") -> list[dict]:
    """Fino a `n` spec valide e motivate. Lista vuota se l'AI non e' disponibile."""
    if not available() or n <= 0:
        return []
    kinds = ", ".join(sorted(FEATURE_LIBRARY))
    user = (f"Feature disponibili (usa SOLO questi nomi): {kinds}\n"
            f"Direzionali: {', '.join(_DIRECTIONAL)}\n\n"
            f"{market_context}\n\n"
            f"Proponi {n} strategie, ciascuna con il suo meccanismo.")
    out = ask_json(SYSTEM, user, max_tokens=4000, label="ai-hypotheses")
    raw = (out or {}).get("specs") if isinstance(out, dict) else out
    if not isinstance(raw, list):
        return []
    seen: set = set()
    specs: list[dict] = []
    for item in raw:
        spec = _clean_spec(item)
        if spec and spec["id"] not in seen:
            seen.add(spec["id"])
            specs.append(spec)
    kept, tot = len(specs), len(raw)
    if kept < tot:
        print(f"[ai-hypotheses] {tot - kept}/{tot} proposte scartate (fuori vocabolario)")
    return specs[:n]
