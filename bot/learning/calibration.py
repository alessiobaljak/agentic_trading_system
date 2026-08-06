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
"""
from __future__ import annotations

from statistics import mean
from typing import Iterable

from bot.config import settings

# esiti non decisi dalla strategia: non dicono nulla sulla qualita' del segnale
_EXTERNAL = {"manual", "kill_switch", "circuit_breaker"}

OK, FLAT, INVERTED, INSUFFICIENT = "ok", "flat", "inverted", "insufficient"


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
