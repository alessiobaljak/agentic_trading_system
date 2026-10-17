"""LE FUNZIONI SERVONO? (1 ott 2026, richiesta del proprietario: «per le varie
features che abbiamo implementato stiamo tracciando il progress, stanno davvero
contribuendo a migliorare il sistema?»).

La verifica del 1 ott (diario) ha trovato che quasi ogni funzione ha un
CONTATORE (quante volte scatta) ma poche hanno un confronto d'ESITO. Qui, per
le funzioni che agiscono sui trade del paper, il confronto minimo coi dati che
ogni trade porta gia' (`size_factors_at_entry`, `declassata`, `esplorativa`,
`orig_stop`, `leverage`, `pnl`): R medio del gruppo toccato dalla funzione
contro quello non toccato, con margine, e un verdetto in parole.

Regole del verdetto (scritte qui PRIMA di leggere i numeri, 1 ott 2026):
  * meno di MIN_GRUPPO trade con R in uno dei due gruppi -> «campione piccolo»;
  * differenza nel verso atteso oltre il margine (2 errori standard trade per
    trade) -> «contribuisce»; nel verso opposto oltre il margine -> «va contro»;
  * altrimenti -> «non si vede ancora».
Il verso atteso e' scritto per ogni funzione (`atteso`): per un freno che
riduce la size il gruppo frenato dovrebbe essere quello PEGGIORE (la funzione
ha senso se frena chi poi perde); per i pesi che alzano la size il gruppo
alzato dovrebbe essere il MIGLIORE. Le funzioni che in R non cambiano niente
per costruzione (riducono solo la size) si misurano anche in USDT risparmiati
o persi rispetto al trade a size piena.

Tutto e' puro: le letture (trade, documenti dell'ombra, spec) le fa chi chiama.
"""
from __future__ import annotations

import math
import re

#: sotto questo numero di trade con R per gruppo non si giudica
MIN_GRUPPO = 10

_LEARN = re.compile(r"learning x([0-9.]+)")
_FRENO = re.compile(r"FRENO x([0-9.]+)")


def _r(t: dict) -> float | None:
    from bot.learning.drift import r_multiplo
    try:
        return r_multiplo(t)
    except Exception:  # noqa: BLE001
        return None


def _sf(t: dict) -> dict:
    v = t.get("size_factors_at_entry")
    return v if isinstance(v, dict) else {}


def _num(v) -> float | None:
    try:
        f = float(v)
    except (TypeError, ValueError):
        return None
    return None if (f != f or f in (float("inf"), float("-inf"))) else f


def _stat(valori: list[float]) -> dict:
    n = len(valori)
    if not n:
        return {"n": 0, "r_medio": None, "es": None}
    m = sum(valori) / n
    var = sum((x - m) ** 2 for x in valori) / (n - 1) if n > 1 else 0.0
    return {"n": n, "r_medio": round(m, 3), "es": math.sqrt(var / n) if n > 1 else None}


def confronto(toccati: list[float], altri: list[float], atteso: str) -> dict:
    """Il confronto d'esito fra il gruppo toccato dalla funzione e gli altri.
    `atteso`: "meglio" (i toccati dovrebbero rendere di piu') o "peggio" (la
    funzione ha senso se tocca chi poi rende di meno). Pura."""
    a, b = _stat(toccati), _stat(altri)
    out = {"toccati": {"n": a["n"], "r_medio": a["r_medio"]},
           "altri": {"n": b["n"], "r_medio": b["r_medio"]},
           "differenza": None, "margine": None, "atteso": atteso}
    if a["n"] < MIN_GRUPPO or b["n"] < MIN_GRUPPO:
        out["verdetto"] = "campione piccolo"
        return out
    diff = a["r_medio"] - b["r_medio"]
    es = math.sqrt((a["es"] or 0.0) ** 2 + (b["es"] or 0.0) ** 2)
    margine = 2.0 * es
    out.update({"differenza": round(diff, 3), "margine": round(margine, 3)})
    verso = diff if atteso == "meglio" else -diff
    if verso > margine:
        out["verdetto"] = "contribuisce"
    elif verso < -margine:
        out["verdetto"] = "va contro"
    else:
        out["verdetto"] = "non si vede ancora"
    return out


def _gruppi(trades, toccato) -> tuple[list[float], list[float]]:
    si, no = [], []
    for t in trades or []:
        r = _r(t)
        if r is None:
            continue
        k = toccato(t)
        if k is None:
            continue
        (si if k else no).append(r)
    return si, no


def _usdt_risparmiati(trades, fattore) -> tuple[float, int]:
    """Quanto avrebbe fatto la differenza la size piena: Σ pnl x (1/f - 1) sui
    trade con fattore f < 1 che non erano gia' tagliati dal tetto per
    posizione (li' il fattore non ha agito). Positivo = la riduzione ha
    risparmiato perdite; negativo = ha tolto guadagni."""
    tot, n = 0.0, 0
    for t in trades or []:
        f = fattore(t)
        if f is None or not (0 < f < 1) or _sf(t).get("capped_by_position_limit"):
            continue
        pnl = _num(t.get("pnl"))
        if pnl is None:
            continue
        tot += -pnl * (1.0 / f - 1.0)
        n += 1
    return round(tot, 2), n


def _freno(t: dict) -> float | None:
    m = _FRENO.search(str(_sf(t).get("alloc_note") or ""))
    return _num(m.group(1)) if m else None


def _peso(t: dict) -> float | None:
    """Il peso strategia x regime all'ingresso, dalla nota dell'allocazione:
    learn_mult = 0,5 + 0,75 w (`adaptation.allocation`). None = nessun dato."""
    m = _LEARN.search(str(_sf(t).get("alloc_note") or ""))
    if not m:
        return None
    lm = _num(m.group(1))
    return None if lm is None else (lm - 0.5) / 0.75


def contributi(trades: list[dict]) -> list[dict]:
    """Le funzioni del bot misurate sui trade del paper (validate ed
    esplorative insieme dove ha senso). Ogni voce: nome, cosa fa, il confronto
    (`confronto`) e, per chi riduce la size, i USDT risparmiati. Pura."""
    validate = [t for t in trades or [] if not t.get("esplorativa")]
    out: list[dict] = []

    # 1) il freno globale da deriva: riduce la size quando il paper smentisce il gate
    si, no = _gruppi(validate, lambda t: (_freno(t) or 1.0) < 1.0)
    usdt, n_usdt = _usdt_risparmiati(validate, _freno)
    out.append({"nome": "freno globale da deriva",
                "cosa": "dimezza circa la size quando il paper rende meno del promesso",
                "confronto": confronto(si, no, "peggio"),
                "usdt_risparmiati": usdt, "n_usdt": n_usdt,
                "nota": "in R una riduzione di size non cambia l'esito: conta in USDT"})

    # 2) la panchina dei pesi (pavimento `peso_size`)
    def _panchina(t):
        v = _num(_sf(t).get("peso_size"))
        return v is not None and v < 1.0
    si, no = _gruppi(validate, _panchina)
    usdt, n_usdt = _usdt_risparmiati(validate, lambda t: _num(_sf(t).get("peso_size")))
    out.append({"nome": "panchina dei pesi",
                "cosa": "size ridotta alle strategia x regime che perdono nel paper",
                "confronto": confronto(si, no, "peggio"),
                "usdt_risparmiati": usdt, "n_usdt": n_usdt})

    # 3) i pesi che ALZANO size e leva (K9): peso > 0,8 contro il resto con dati
    def _alto(t):
        w = _peso(t)
        return None if w is None else w > 0.8
    si, no = _gruppi(validate, _alto)
    out.append({"nome": "pesi alti (size e leva in su)",
                "cosa": "peso > 0,8: piu' size e leva a chi ha vinto di recente",
                "confronto": confronto(si, no, "meglio")})

    # 4) la leva sopra 1x
    def _leva(t):
        lv = _num(t.get("leverage"))
        return None if lv is None else lv > 1.05
    si, no = _gruppi(validate, _leva)
    out.append({"nome": "leva sopra 1x",
                "cosa": "trade aperti con leva > 1 (pesi e convinzione)",
                "confronto": confronto(si, no, "meglio")})

    # 5) il tilt di trend e sentiment (size_multiplier della decisione < 1)
    def _tilt(t):
        v = _num(_sf(t).get("size_multiplier"))
        return None if v is None else v < 0.999
    si, no = _gruppi(validate, _tilt)
    usdt, n_usdt = _usdt_risparmiati(validate, lambda t: _num(_sf(t).get("size_multiplier")))
    out.append({"nome": "tilt di trend e sentiment",
                "cosa": "size ridotta ai trade contro il trend o col sentiment sfavorevole",
                "confronto": confronto(si, no, "peggio"),
                "usdt_risparmiati": usdt, "n_usdt": n_usdt})

    # 6) le declassate a un quarto di size
    si, no = _gruppi(validate, lambda t: bool(t.get("declassata")))
    usdt, n_usdt = _usdt_risparmiati(validate, lambda t: (_num(_sf(t).get("declassata"))
                                                          if t.get("declassata") else None))
    rischi = {k: [x for x in (_num(t.get("risk_effective_pct")) for t in validate
                              if bool(t.get("declassata")) is v) if x is not None]
              for k, v in (("declassate", True), ("attive", False))}
    out.append({"nome": "declassate a un quarto",
                "cosa": "validate bocciate due notti di fila, operate a size ridotta",
                "confronto": confronto(si, no, "peggio"),
                "usdt_risparmiati": usdt, "n_usdt": n_usdt,
                "rischio_medio_pct": {k: (round(sum(v) / len(v), 4) if v else None)
                                      for k, v in rischi.items()}})

    # 7) il paper esplorativo: R delle esplorative contro le validate
    esp = [r for r in (_r(t) for t in trades or [] if t.get("esplorativa")) if r is not None]
    val = [r for r in (_r(t) for t in validate) if r is not None]
    out.append({"nome": "paper esplorativo",
                "cosa": "quasi-passaggi operati a un quarto: rendono come le validate?",
                "confronto": confronto(esp, val, "meglio"),
                "nota": "«contribuisce» qui vuol dire: i quasi-passaggi rendono piu' delle validate"})
    return out


def ombra_ai(trades: list[dict], decisioni: list[dict]) -> dict:
    """L'OMBRA AI (spenta dal 30 set): i trade che l'AI avrebbe EVITATO
    (`shadow_veto`) contro quelli su cui era d'accordo (`agree`), in R, legando
    `trade_ids` dei documenti `ai_shadow` al `trade_id` dei trade chiusi.
    Risponde una volta per sempre a «il veto dell'AI sarebbe servito?»: se i
    vetati rendono MENO degli accordi oltre il margine, si'. Pura."""
    r_per_id = {}
    for t in trades or []:
        r = _r(t)
        tid = str(t.get("trade_id") or "")
        if r is not None and tid:
            r_per_id[tid] = r
    vetati, accordo = [], []
    visti: set[str] = set()
    for d in decisioni or []:
        if not isinstance(d, dict):
            continue
        dove = {"shadow_veto": vetati, "agree": accordo}.get(str(d.get("verdict")))
        if dove is None:
            continue
        for tid in d.get("trade_ids") or []:
            tid = str(tid)
            if tid in r_per_id and tid not in visti:
                visti.add(tid)
                dove.append(r_per_id[tid])
    return {"nome": "ombra AI (spenta)",
            "cosa": "i trade che l'AI avrebbe evitato rendono meno di quelli che approvava?",
            "confronto": confronto(vetati, accordo, "peggio")}


def per_origine(trades: list[dict], specs: dict | None) -> dict:
    """R del paper per ORIGINE della strategia (AI, casuali, varianti dai
    referti, intorno), con `registry.origine_spec` sulla spec della strategia
    del trade. Pura."""
    from bot.core.registry import origine_spec
    specs = specs if isinstance(specs, dict) else {}
    gruppi: dict[str, list[float]] = {}
    for t in trades or []:
        if t.get("esplorativa"):
            continue
        r = _r(t)
        if r is None:
            continue
        gid = str(t.get("strategy") or "")
        o = origine_spec(specs.get(gid), generata=gid.startswith("gen_"))
        gruppi.setdefault(o, []).append(r)
    return {o: _stat(v) | {"es": None} for o, v in sorted(gruppi.items())}


def riga_verdetto(c: dict) -> str:
    """Una riga leggibile del confronto."""
    a, b = c["toccati"], c["altri"]
    fr = lambda v: "—" if v is None else f"{v:+.3f}R"  # noqa: E731
    base = f"toccati {a['n']} a {fr(a['r_medio'])} · altri {b['n']} a {fr(b['r_medio'])}"
    if c.get("differenza") is not None:
        base += f" · diff {c['differenza']:+.3f} ±{c['margine']:.3f}"
    return f"{base} -> {c['verdetto'].upper()}"
