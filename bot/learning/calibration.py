"""
CALIBRAZIONE DELLA CONFIDENZA — la confidenza predice davvero l'esito?

PERCHE' SERVE
`allocation()` modula size e leva sulla confidenza del segnale (30 -> x0.75,
85+ -> x1.25). Ma nessuno aveva mai verificato che quel numero predicesse
qualcosa: se la confidenza fosse rumore, staremmo dimensionando le posizioni su
una cifra senza significato — e con convinzione, che e' la parte peggiore.
La correlazione esisteva gia' (`metrics.confidence_outcome_correlation`) ma
finiva in un report notturno che nessuno legge e non alimentava nulla.

COSA MISURA
Due segnali, perche' uno solo inganna:
  * CORRELAZIONE (Pearson) tra confidenza ed esito: cattura la relazione lineare
    ma e' sensibile a pochi trade estremi.
  * MONOTONIA A FASCE: divide i trade in terzili di confidenza e guarda se
    l'expectancy CRESCE. E' piu' robusta: non le importa di quanto, le importa
    che l'ordine sia giusto.

COSA FA COL RISULTATO
Non inverte e non spegne: RIDUCE l'influenza della confidenza verso il neutro.
Se la confidenza anti-predice, la risposta onesta e' smettere di usarla — non
scommetterci contro, che sarebbe adattarsi al rumore con un altro nome.
Sotto il campione minimo non tocca niente: agire su 10 trade sarebbe l'errore
che stiamo cercando di evitare.

QUANDO NON PUO' MISURARE NULLA (25 set 2026)
Tutte le strategie generate escono a confidenza fissa 60
(`bot/strategies/generated.py`). Con un solo valore le «fasce» non sono fasce
di confidenza: `sorted` e' stabile, quindi i terzili sono l'ORDINE CRONOLOGICO
dei trade, e «la fascia alta rende piu' della bassa» significa solo «gli ultimi
trade sono andati meglio dei primi». Il verdetto oscillava fra «flat» (23 set)
e «ok» (25 set) senza che nulla fosse cambiato: era un artefatto. In quel caso
il verdetto e' «costante», con trust 1.0 (niente da correggere, niente da
ridurre) e una nota che dice perche' non si misura.
"""
from __future__ import annotations

from statistics import mean
from typing import Iterable

from bot.config import settings

# esiti non decisi dalla strategia: non dicono nulla sulla qualita' del segnale
_EXTERNAL = {"manual", "kill_switch", "circuit_breaker"}

OK, FLAT, INVERTED, INSUFFICIENT = "ok", "flat", "inverted", "insufficient"
# la confidenza non varia: non c'e' niente da calibrare (vedi in cima, 25 set 2026)
CONSTANT = "costante"

# sotto questo range (in punti di confidenza) le fasce non separano nulla: un
# punto e' meno di qualunque differenza che allocation() possa tradurre in size
CONSTANT_RANGE = 1.0


def _constant_note(lo: float, hi: float, n: int) -> str:
    """Perche' non si misura, detto a chi legge il verdetto al mattino.

    Il caso reale (25 set 2026) e' «tutte a 60»: e' il valore fisso delle
    strategie generate, e va detto. Se un giorno il valore costante fosse un
    altro, la frase sulle generate sarebbe falsa: si scrive solo la costanza."""
    coda = ("la calibrazione non puo' misurare nulla finche' la confidenza non "
            f"varia ({n} trade, confidenza {lo:.0f}-{hi:.0f})")
    if abs(lo - 60.0) < CONSTANT_RANGE:
        return f"tutte le strategie generate escono a confidenza 60: {coda}"
    return f"la confidenza e' costante ({lo:.0f}) su tutti i trade: {coda}"


def _pearson(pairs: list[tuple[float, float]]) -> float | None:
    if len(pairs) < 5:
        return None
    xs = [p[0] for p in pairs]
    ys = [p[1] for p in pairs]
    mx, my = mean(xs), mean(ys)
    num = sum((x - mx) * (y - my) for x, y in pairs)
    dx = sum((x - mx) ** 2 for x in xs) ** 0.5
    dy = sum((y - my) ** 2 for y in ys) ** 0.5
    if dx == 0 or dy == 0:
        return None
    return num / (dx * dy)


def confidence_buckets(pairs: list[tuple[float, float]], n_buckets: int = 3) -> list[dict]:
    """Terzili di confidenza con l'esito medio di ciascuno.

    Piu' robusta della sola correlazione: se l'expectancy cresce passando dalla
    fascia bassa all'alta, la confidenza ORDINA correttamente i trade — che e'
    tutto cio' che serve per modulare la size."""
    if len(pairs) < n_buckets:
        return []
    ordered = sorted(pairs, key=lambda p: p[0])
    size = len(ordered) // n_buckets
    out = []
    for i in range(n_buckets):
        lo = i * size
        hi = len(ordered) if i == n_buckets - 1 else (i + 1) * size
        chunk = ordered[lo:hi]
        if not chunk:
            continue
        pnls = [p[1] for p in chunk]
        out.append({
            "conf_min": round(min(p[0] for p in chunk), 1),
            "conf_max": round(max(p[0] for p in chunk), 1),
            "trades": len(chunk),
            "win_rate": round(sum(1 for x in pnls if x > 0) / len(pnls), 3),
            "expectancy": round(mean(pnls), 5),
        })
    return out


def calibrate(trades: Iterable[dict]) -> dict:
    """Verdetto sulla calibrazione + `trust` da applicare in allocation.

    trust 1.0 = la confidenza conta come oggi; 0.0 = non influenza piu' la size."""
    pairs = [(float(t["confidence_at_entry"]), float(t["pnl_pct"]))
             for t in trades
             if str(t.get("exit_reason", "")) not in _EXTERNAL
             and t.get("confidence_at_entry") is not None
             and t.get("pnl_pct") is not None]
    n = len(pairs)
    buckets = confidence_buckets(pairs)
    corr = _pearson(pairs)

    # CONFIDENZA CHE NON VARIA: viene PRIMA del campione minimo, di proposito.
    # «insufficient: servono 30 trade» promette che con piu' trade si misurera'
    # qualcosa; con la confidenza fissa a 60 non e' vero, e la promessa falsa e'
    # peggio del numero mancante. Sotto i 2 trade il range non e' definito e vale
    # il verdetto di sempre. (25 set 2026)
    if n >= 2:
        lo = min(p[0] for p in pairs)
        hi = max(p[0] for p in pairs)
        # «tutte le fasce hanno lo stesso valore» e «varianza nulla» sono casi
        # particolari di «range sotto un punto»: basta questo controllo.
        if hi - lo < CONSTANT_RANGE:
            return {"verdict": CONSTANT, "trades": n, "correlation": None,
                    "buckets": buckets, "monotonic": None, "trust": 1.0,
                    "note": _constant_note(lo, hi, n)}

    if n < settings.CALIBRATION_MIN_TRADES:
        return {"verdict": INSUFFICIENT, "trades": n, "correlation": corr,
                "buckets": buckets, "trust": 1.0,
                "note": f"servono {settings.CALIBRATION_MIN_TRADES} trade, ce ne sono {n}"}

    # monotonia: l'expectancy della fascia ALTA supera quella della fascia BASSA?
    rising = bool(buckets) and buckets[-1]["expectancy"] > buckets[0]["expectancy"]
    c = corr if corr is not None else 0.0

    if c <= -settings.CALIBRATION_FLAT_ABS and not rising:
        verdict, trust = INVERTED, 0.0
        note = "la confidenza ANTI-predice: smette di influenzare la size"
    elif abs(c) < settings.CALIBRATION_FLAT_ABS and not rising:
        verdict, trust = FLAT, settings.CALIBRATION_FLAT_TRUST
        note = "nessuna relazione tra confidenza ed esito: influenza ridotta"
    else:
        verdict, trust = OK, 1.0
        note = "la confidenza ordina correttamente gli esiti"
    return {"verdict": verdict, "trades": n, "correlation": round(c, 3),
            "buckets": buckets, "monotonic": rising, "trust": trust, "note": note}


def confidence_trust(cal_doc: dict | None) -> float:
    """Quanto fidarsi della confidenza (0..1). 1.0 se disattivata o senza dati:
    senza evidenza NON si devia dal comportamento validato dal gate."""
    if not settings.CALIBRATION_ENABLED or not cal_doc:
        return 1.0
    try:
        return max(0.0, min(1.0, float(cal_doc.get("trust", 1.0))))
    except (TypeError, ValueError):
        return 1.0
