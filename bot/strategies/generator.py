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
    # --- il MERCATO. Aggiunti il 21 set dopo due short consecutivi su una coin
    # che saliva dentro una giornata di rialzo: le altre feature guardano solo
    # quella coin, quindi la strategia non poteva distinguere «sto vendendo un
    # ritracciamento» da «sto davanti a un treno». Sono mattoncini, NON un veto:
    # il gate misura se servono, come per tutto il resto.
    "market_trend", "market_fade", "relative_strength",
    # --- la CONFERMA A 1 ORA della stessa coin (22 set): long solo con le medie
    # orarie in salita, short solo in discesa. Il gate misura se serve.
    "htf_confirm",
    # e l'ipotesi opposta: vendere l'eccesso rispetto alla media oraria (lo
    # short sul calo momentaneo dentro un trend in salita). Sceglie il gate.
    "htf_fade",
]
# combinazioni incoerenti da evitare (mean-reversion + breakout sullo stesso segnale)
_INCOMPATIBLE = {
    frozenset({"bb_touch", "bb_break"}),
    frozenset({"vwap_momentum", "vwap_reversion"}),
    frozenset({"rsi_extreme", "rsi_momentum"}),
    frozenset({"stoch_extreme", "stoch_momentum"}),
    # andare col mercato e contro il mercato insieme non lascia passare niente
    frozenset({"market_trend", "market_fade"}),
    frozenset({"htf_confirm", "htf_fade"}),
}

# feature di CONDIZIONE (non danno la direzione: dicono quando operare). Erano
# assenti: il generatore combinava solo oscillatori sullo stesso timeframe, quindi
# sapeva dove sta il prezzo ma mai in che condizione e' il mercato.
_CONDITIONAL = ["volatility_regime", "trend_strength", "volume_surge", "session",
                # dal 21 set 2026: «non sovraesteso» e «trend debole», le due
                # condizioni con cui una mean-reversion puo' rifiutarsi di
                # vendere una salita verticale
                "not_stretched", "adx_below"]
_VOL_PCT = [0.01, 0.02, 0.03]
_ADX_LO = [18.0, 22.0, 28.0]
_RS_GAP = [0.0, 0.005, 0.02]
_STRETCH_MAX = [2.0, 3.0, 4.5]   # in ATR dalla media lenta
_HTF_GAP = [0.0, 0.01, 0.02]     # distanza minima dalla media oraria, frazione del prezzo
_ADX_HI = [20.0, 28.0, 35.0]
_VOL_MULT_FEAT = [1.2, 1.5, 2.0]
_SESSIONS = [(0, 8), (8, 16), (12, 21), (16, 24)]

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
    elif kind == "volatility_regime":
        f["vol_pct"] = rng.choice(_VOL_PCT)
    elif kind == "trend_strength":
        f["adx_lo"] = rng.choice(_ADX_LO)
    elif kind == "volume_surge":
        f["vol_mult_feat"] = rng.choice(_VOL_MULT_FEAT)
    elif kind == "session":
        f["hour_from"], f["hour_to"] = rng.choice(_SESSIONS)
    elif kind == "not_stretched":
        f["stretch_max"] = rng.choice(_STRETCH_MAX)
    elif kind == "adx_below":
        f["adx_hi"] = rng.choice(_ADX_HI)
    elif kind == "htf_fade":
        f["htf_gap"] = rng.choice(_HTF_GAP)
    elif kind == "relative_strength":
        # 0 = basta essere piu' forte del mercato; 0.02 = almeno due punti
        # percentuali in piu'. Senza questa riga il generatore proporrebbe la
        # feature senza il suo parametro e il validatore la scarterebbe: e'
        # esattamente lo scarto che il 20 settembre ha bruciato il 74% delle
        # proposte AI.
        f["rs_gap"] = rng.choice(_RS_GAP)
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
        # con probabilita' 1/2 la spec include una feature di CONDIZIONE (volatilita',
        # forza del trend, volume, sessione). Non da' la direzione: dice QUANDO la
        # direzione vale. Meta' delle spec resta puramente direzionale, cosi' il
        # confronto tra i due stili lo fa il gate, non una scelta a priori.
        # La condizione occupa uno degli slot: il tetto max_features resta invariato.
        add_cond = rng.random() < 0.5
        k = rng.randint(1, max(1, max_features - (1 if add_cond else 0)))
        kinds = rng.sample(_DIRECTIONAL, k)
        if add_cond:
            kinds.append(rng.choice(_CONDITIONAL))
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
    # il lato operato (variante dai referti, 23 set 2026) e' parte dell'idea:
    # mutare «attorno a» una spec solo-long deve restare solo-long, altrimenti
    # la figlia riapre il lato che il paper aveva visto perdere sempre
    if spec.get("solo") in ("long", "short"):
        child["solo"] = spec["solo"]
        child["id"] = spec_id(child)
    return child


# --------------------------------------------------------------------------- #
# LE VARIANTI DAI REFERTI DEL PAPER (23 set 2026, backlog B8)                  #
#                                                                              #
# «Una strategia generata non puo' essere ritarata: puo' solo morire.» Il      #
# proprietario ha chiesto che il sistema impari da ogni trade; la strada       #
# onesta NON e' spostare una soglia guardando i risultati del paper (il paper  #
# e' la prova, non il training set: BIRBUSDT, PF 1,51 promesso e 0,16 vissuto).#
# La strada e': il paper PROPONE una variante della stessa idea, e il GATE la  #
# prova sulla storia come qualunque candidata, tre conferme piu' holdout.      #
#                                                                              #
# Il documento `learning/referti` raccoglie i post-mortem dei trade chiusi e   #
# formula ipotesi con regole dichiarate PRIMA (solo_long, solo_short,          #
# conferma_trend, stop_stretto). Qui ogni ipotesi diventa una spec figlia:     #
# stessa logica, un solo cambiamento, nuovo id. Il gate decide se vale.        #
# --------------------------------------------------------------------------- #
#: i tipi di ipotesi che il referto puo' formulare e che qui sanno diventare spec
TIPI_VARIANTE = ("solo_long", "solo_short", "conferma_trend", "stop_stretto")


def varianti_da_referto(spec: dict, tipo: str) -> Optional[dict]:
    """La spec FIGLIA di `spec` per l'ipotesi `tipo`, o None se non ha senso.

    Funzione pura: non legge Firebase, non tira a caso. Cambia UNA cosa sola,
    cosi' se la figlia passa il gate e il genitore no, si sa esattamente cosa
    ha fatto la differenza.

      * solo_long / solo_short: la stessa spec che opera un lato solo. None se
        gia' lo fa.
      * conferma_trend: aggiunge la conferma a 1 ora (`htf_confirm`). None se
        la spec guarda gia' l'ora (conferma o fade: sarebbe incoerente). Puo'
        arrivare a 4 feature: la conferma e' un filtro, non un segnale nuovo.
      * stop_stretto: lo stop al gradino sotto nella lista `_ATR_STOP`. None se
        e' gia' al minimo; un valore fuori lista scende al gradino piu' grande
        sotto di lui.

    La figlia perde l'id del genitore e ne riceve uno suo (`spec_id`, che
    include `solo`), conserva il timeframe, e porta scritto da dove viene:
    origine/genitore/ipotesi. Sono etichette, non logica: non entrano nell'id.
    """
    if not isinstance(spec, dict) or tipo not in TIPI_VARIANTE:
        return None
    figlia = {k: v for k, v in spec.items() if k != "id"}
    figlia["features"] = [dict(f) for f in spec.get("features", []) if isinstance(f, dict)]

    if tipo in ("solo_long", "solo_short"):
        lato = tipo.split("_", 1)[1]
        if str(spec.get("solo") or "").lower() == lato:
            return None
        figlia["solo"] = lato
    elif tipo == "conferma_trend":
        kinds = [f.get("kind") for f in figlia["features"]]
        if "htf_confirm" in kinds or "htf_fade" in kinds:
            return None
        if not _coherent(kinds + ["htf_confirm"]):
            return None
        figlia["features"].append({"kind": "htf_confirm"})
    elif tipo == "stop_stretto":
        try:
            attuale = float(spec.get("atr_mult_stop"))
        except (TypeError, ValueError):
            return None
        sotto = [g for g in _ATR_STOP if g < attuale]
        if not sotto:
            return None
        figlia["atr_mult_stop"] = max(sotto)

    figlia["origine"] = "referto"
    figlia["genitore"] = spec.get("id")
    figlia["ipotesi"] = tipo
    figlia["id"] = spec_id(figlia)
    return figlia
