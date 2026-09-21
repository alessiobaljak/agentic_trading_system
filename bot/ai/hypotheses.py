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

import time
from collections import Counter
from typing import Optional

from bot.ai.client import ask_json, available
from bot.strategies.generated import (FEATURE_LIBRARY, MARKET_FEATURES,
                                      feature_esiste, spec_id)
from bot.strategies.generator import _ATR_STOP, _DIRECTIONAL, _INCOMPATIBLE, _RR

#: esito dell'ULTIMA chiamata a `propose` in questo processo: quante proposte, quante
#: accettate, e il conteggio dei motivi di scarto. Lo legge la discovery per salvarlo
#: su Firebase — vedi il commento dentro `propose`.
ULTIMO_ESITO: dict = {}

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
    # scarto minimo fra la distanza della coin dalla sua media e quella del
    # mercato dalla sua: 0 = basta essere piu' forte, 0.02 = almeno due punti
    # percentuali di forza in piu'.
    "relative_strength": {"rs_gap": (0.0, 0.05)},
}

#: fasce dei numeri di una spec. UNA SOLA definizione, usata sia da `_esamina_spec`
#: per validare sia dal prompt per dichiararle. Prima le fasce esistevano solo nel
#: validatore e il prompt non le nominava: il 20 settembre il modello ha proposto
#: rr fra 0.9 e 1.3 — sensato per una strategia di ritorno alla media, e coerente
#: con le prove del paper che gli passiamo (mfe mediana 0.85R) — e QUATTORDICI
#: proposte su diciannove sono state scartate per quello. Una regola che il
#: validatore conosce e il richiedente no non e' una regola: e' una trappola.
_NUMERI = {
    "atr_mult_stop": (min(_ATR_STOP), max(_ATR_STOP)),
    "rr": (min(_RR), max(_RR)),
    "min_adx": (0.0, 40.0),
    "volume_mult": (0.0, 5.0),
}


def _fasce_testo() -> str:
    """Le fasce ammesse, scritte per chi propone. Generate dalle stesse costanti
    che validano: un elenco copiato a mano si stacca al primo cambio di soglia."""
    righe = [f"  - {k}: da {lo:g} a {hi:g}" for k, (lo, hi) in _NUMERI.items()]
    for kind, params in sorted(_FEATURE_PARAMS.items()):
        dettaglio = ", ".join(f"{n} da {lo:g} a {hi:g}" for n, (lo, hi) in params.items())
        righe.append(f"  - feature {kind}: richiede {dettaglio}")
    return "\n".join(righe)


_SYSTEM_TEMPLATE = """\
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
- niente coppie contraddittorie (mean-reversion + breakout sullo stesso segnale);
- OGNI feature che richiede parametri deve averli TUTTI, dentro la sua fascia;
- i numeri devono stare nelle fasce qui sotto. Fuori fascia la spec viene
  scartata INTERA: non viene corretta ne' avvicinata al limite.

FASCE AMMESSE:
{FASCE}

Rispondi ESCLUSIVAMENTE con JSON:
{"specs": [
  {"mechanism": "perche' dovrebbe funzionare, 1-2 frasi",
   "features": [{"kind": "volume_surge", "vol_mult_feat": 2.0},
                {"kind": "stoch_momentum"}],
   "atr_mult_stop": 2.0, "rr": 2.5, "min_adx": 20.0, "volume_mult": 1.5}
]}"""

# riempito UNA volta all'import: le fasce non cambiano a runtime, e generarle
# a ogni chiamata nasconderebbe un errore di formato fino alla prima proposta
SYSTEM = _SYSTEM_TEMPLATE.replace("{FASCE}", _fasce_testo())


def _esamina_feature(raw: dict) -> tuple[Optional[dict], str]:
    """(feature ripulita, motivo dello scarto). Uno dei due e' sempre vuoto."""
    if not isinstance(raw, dict):
        return None, "feature non e' un oggetto"
    kind = raw.get("kind")
    if not feature_esiste(kind):
        return None, f"feature inesistente: {str(kind)[:30]}"
    out = {"kind": kind}
    for name, (lo, hi) in _FEATURE_PARAMS.get(kind, {}).items():
        if name not in raw:
            return None, f"{kind}: manca il parametro {name}"
        try:
            v = float(raw[name])
        except (TypeError, ValueError):
            return None, f"{kind}: {name} non e' un numero"
        if not (lo <= v <= hi):
            return None, f"{kind}: {name}={v:g} fuori dalla fascia {lo:g}-{hi:g}"
        out[name] = v
    if kind == "session":        # le ore restano interi, e devono essere ordinate
        out["hour_from"], out["hour_to"] = int(out["hour_from"]), int(out["hour_to"])
        if out["hour_from"] >= out["hour_to"]:
            return None, "session: ora di inizio non precedente a quella di fine"
    return out, ""


def _esamina_spec(raw: dict) -> tuple[Optional[dict], str]:
    """(spec valida, motivo dello scarto) — la LOGICA sta qui, una volta sola.

    PERCHE' UN MOTIVO E NON UN SI'/NO. Il 19 settembre, primo giro col livello AI
    riacceso, il log ha detto: «19/20 proposte scartate (fuori vocabolario)». Il
    95% buttato, e nessun modo di sapere QUALE regola le fermasse — feature
    inventate? troppe? parametri fuori scala? combinazioni vietate? Senza quella
    risposta l'unica mossa possibile era correggere il prompt a tentoni, cioe'
    cambiare qualcosa e sperare. E' lo stesso buco che il gate aveva prima
    dell'autopsia: si contavano i morti senza sapere di cosa.

    `_clean_spec` resta la porta di prima (solo la spec) per chi non vuole il
    motivo; entrambe passano di qui, quindi non possono divergere.
    """
    if not isinstance(raw, dict):
        return None, "proposta non e' un oggetto"

    grezze = raw.get("features") or []
    feats, motivi_feat = [], []
    for x in grezze:
        f, perche = _esamina_feature(x)
        if f:
            feats.append(f)
        else:
            motivi_feat.append(perche)
    # QUANDO TUTTE le feature cadono, la spec cade con loro — ed e' il caso in cui
    # il motivo serve davvero: «nessuna feature valida» non direbbe niente, mentre
    # «rsi_extreme: manca il parametro low» dice cosa correggere nel prompt. Si
    # riporta il PRIMO motivo: con tre feature al massimo, l'elenco completo
    # sarebbe rumore e il primo basta a riconoscere lo schema.
    #
    # Se invece ne cade solo QUALCUNA, la spec prosegue con le rimaste: e' il
    # comportamento di sempre e non lo cambio mentre sto diagnosticando — una
    # modifica alla severita' in mezzo a una misura renderebbe illeggibile il
    # confronto col giro precedente.
    if not feats:
        return None, motivi_feat[0] if motivi_feat else "nessuna feature proposta"
    kinds = [f["kind"] for f in feats]
    if len(feats) > 3:
        return None, f"troppe feature ({len(feats)}, il massimo e' 3)"
    if len(set(kinds)) != len(kinds):
        return None, "stessa feature ripetuta"
    if not any(k in _DIRECTIONAL for k in kinds):
        # senza direzionale la spec non sa dove andare
        return None, "nessuna feature direzionale"
    for pair in _INCOMPATIBLE:
        if pair <= set(kinds):
            return None, f"coppia incompatibile: {' + '.join(sorted(pair))}"

    # le fasce vengono da `_NUMERI`, le STESSE che il prompt dichiara: una copia
    # scritta qui si staccherebbe dal prompt al primo cambio di soglia, e il
    # modello proporrebbe valori legali secondo le istruzioni e illegali per il
    # validatore — il difetto che il 20 settembre ha scartato 14 proposte su 19.
    for key, default in (("atr_mult_stop", 1.5), ("rr", 2.0),
                         ("min_adx", 0.0), ("volume_mult", 0.0)):
        lo, hi = _NUMERI[key]
        try:
            v = float(raw.get(key, default))
        except (TypeError, ValueError):
            return None, f"{key} non e' un numero"
        if not (lo <= v <= hi):
            return None, f"{key}={v:g} fuori dalla fascia {lo:g}-{hi:g}"
        raw = {**raw, key: v}

    spec = {"features": feats, "volume_mult": raw["volume_mult"],
            "min_adx": raw["min_adx"], "atr_mult_stop": raw["atr_mult_stop"],
            "rr": raw["rr"]}
    spec["id"] = spec_id(spec)   # STESSA identita' delle spec casuali: niente corsie
    mech = str(raw.get("mechanism") or "").strip()
    if mech:
        # tracciabile: dopo la validazione si potra' chiedere se il meccanismo
        # dichiarato regge, non solo se i numeri tornano.
        spec["mechanism"] = mech[:400]
    return spec, ""


def _clean_feature(raw: dict) -> Optional[dict]:
    return _esamina_feature(raw)[0]


def _clean_spec(raw: dict) -> Optional[dict]:
    """Ricostruisce una spec valida dai campi proposti, o None."""
    return _esamina_spec(raw)[0]


def propose(n: int, market_context: str = "") -> list[dict]:
    """Fino a `n` spec valide e motivate. Lista vuota se l'AI non e' disponibile."""
    if not available() or n <= 0:
        return []
    kinds = ", ".join(sorted(set(FEATURE_LIBRARY) | set(MARKET_FEATURES)))
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
    motivi: Counter = Counter()
    for item in raw:
        spec, perche = _esamina_spec(item)
        if not spec:
            motivi[perche] += 1
            continue
        if spec["id"] in seen:
            motivi["duplicata di un'altra proposta dello stesso giro"] += 1
            continue
        seen.add(spec["id"])
        specs.append(spec)
    kept, tot = len(specs), len(raw)
    # L'ESITO SOPRAVVIVE AL LOG. Il 20 settembre la diagnosi dei motivi c'era gia'
    # e non e' stata leggibile lo stesso: il canale ops mostra le ultime 80 righe
    # del journal, la discovery gira una volta ogni tre ore e in mezzo l'ottimizzo
    # ne scrive migliaia. Sei ore dopo, il motivo per cui il 95% delle proposte
    # viene buttato era gia' scorso via. Una diagnosi che vive solo in una
    # finestra che scorre non e' una diagnosi — e' la terza volta in due giorni
    # che un'informazione esiste e non si riesce a raggiungerla.
    ULTIMO_ESITO.clear()
    ULTIMO_ESITO.update({"proposte": tot, "accettate": kept,
                         "motivi": dict(motivi.most_common()), "at": time.time()})
    if kept < tot:
        # I MOTIVI, non solo il conteggio. La prima versione stampava «N/M proposte
        # scartate (fuori vocabolario)» e basta: il 19 settembre ha detto 19 su 20
        # senza dire quale regola, e per correggere il prompt restava solo provare
        # a caso. Con l'elenco davanti si vede subito se il modello inventa nomi,
        # sfora le fasce o dimentica un parametro — tre correzioni diverse.
        dettaglio = " · ".join(f"{m} ×{k}" for m, k in motivi.most_common(6))
        print(f"[ai-hypotheses] {tot - kept}/{tot} proposte scartate: {dettaglio}")
    return specs[:n]
