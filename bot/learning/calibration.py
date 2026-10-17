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

DUE MISURE IN PIU', SOLO MISURE (26 set 2026, backlog J8)
Ogni trade porta anche `regime_confidence_at_entry` (quanto era netta la
classificazione di regime, 0..1) e `fear_greed_at_entry` (l'indice 0..100).
Nessuno dei due entra in `allocation()`; il modello (bot/core/models.py) lo
diceva gia': «registrato per poter misurare se predice l'esito: solo dopo
quella verifica ha senso legarlo a size o leva». Qui si fa quella verifica:
terzili di confidenza del regime (`regime_confidence`, con un verdetto «cresce»
/ «piatta» / «campione insufficiente» sotto MIN_PER_FASCIA trade per fascia) e
tre fasce fisse di F&G (<= 25 paura, 26-74, >= 75 avidita': i confini del
sito che lo pubblica, non tarati). `trust` NON li guarda: il verdetto sulla
confidenza del segnale resta l'unico che tocca la size.
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

# le fasce del regime e del F&G (26 set 2026): sotto 10 trade per fascia il
# confronto fra fasce e' rumore (dichiarato prima di vedere i numeri). Le
# fasce del F&G sono quelle del sito che lo pubblica (paura <= 25, avidita' >= 75).
MIN_PER_FASCIA = 10
FG_PAURA, FG_AVIDITA = 25, 75
CRESCE, PIATTA, INSUFFICIENTE_FASCE = "cresce", "piatta", "campione insufficiente"


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


def _fascia(etichetta: str, pnls: list[float]) -> dict:
    return {"fascia": etichetta, "n": len(pnls),
            "win_rate": round(sum(1 for x in pnls if x > 0) / len(pnls), 3) if pnls else None,
            "pnl_medio": round(mean(pnls), 5) if pnls else None}


def fasce_regime(pairs: list[tuple[float, float]], n_fasce: int = 3) -> list[dict]:
    """Terzili della confidenza del REGIME con n, win rate e pnl medio (26 set
    2026). Stessa forma di `confidence_buckets`, con le etichette del range."""
    if len(pairs) < n_fasce:
        return []
    ordered = sorted(pairs, key=lambda p: p[0])
    size = len(ordered) // n_fasce
    out = []
    for i in range(n_fasce):
        lo = i * size
        hi = len(ordered) if i == n_fasce - 1 else (i + 1) * size
        chunk = ordered[lo:hi]
        if not chunk:
            continue
        f = _fascia(f"{min(p[0] for p in chunk):.2f}-{max(p[0] for p in chunk):.2f}",
                    [p[1] for p in chunk])
        f["min"], f["max"] = round(min(p[0] for p in chunk), 3), round(max(p[0] for p in chunk), 3)
        out.append(f)
    return out


def verdetto_fasce(fasce: list[dict], minimo: int = MIN_PER_FASCIA) -> str:
    """«cresce» se il pnl medio della fascia ALTA supera quello della BASSA,
    «piatta» altrimenti; «campione insufficiente» se una fascia ha meno di
    `minimo` trade o le fasce sono meno di due. Nessuna regola sulla size ne
    discende: e' una misura."""
    if len(fasce) < 2 or any(int(f.get("n", 0) or 0) < minimo for f in fasce):
        return INSUFFICIENTE_FASCE
    lo, hi = fasce[0].get("pnl_medio"), fasce[-1].get("pnl_medio")
    if lo is None or hi is None:
        return INSUFFICIENTE_FASCE
    return CRESCE if hi > lo else PIATTA


def fasce_fear_greed(pairs: list[tuple[float, float]]) -> list[dict]:
    """Tre fasce fisse del Fear & Greed all'apertura: paura (<= 25), mezzo
    (26-74), avidita' (>= 75). Fasce vuote comprese, con n = 0: chi legge deve
    vedere che manca il dato, non che manca la riga."""
    gruppi = {f"<={FG_PAURA}": [], f"{FG_PAURA + 1}-{FG_AVIDITA - 1}": [], f">={FG_AVIDITA}": []}
    for fg, pnl in pairs:
        if fg <= FG_PAURA:
            gruppi[f"<={FG_PAURA}"].append(pnl)
        elif fg >= FG_AVIDITA:
            gruppi[f">={FG_AVIDITA}"].append(pnl)
        else:
            gruppi[f"{FG_PAURA + 1}-{FG_AVIDITA - 1}"].append(pnl)
    return [_fascia(k, v) for k, v in gruppi.items()]


def _coppie(trades: list[dict], campo: str) -> list[tuple[float, float]]:
    out = []
    for t in trades:
        if (str(t.get("exit_reason", "")) in _EXTERNAL or t.get("esplorativa")
                or t.get(campo) is None or t.get("pnl_pct") is None):
            continue
        try:
            out.append((float(t[campo]), float(t["pnl_pct"])))
        except (TypeError, ValueError):
            continue
    return out


def misure_contesto(trades: list[dict]) -> dict:
    """Le due misure del 26 set 2026 (regime, F&G): sono la stessa popolazione
    della calibrazione (fuori esiti esterni ed esplorativi), ma ognuna con i
    SUOI trade noti, perche' un trade senza F&G puo' avere il regime. Non
    toccano `trust`."""
    reg = _coppie(trades, "regime_confidence_at_entry")
    fr = fasce_regime(reg)
    fg = _coppie(trades, "fear_greed_at_entry")
    return {"regime_confidence": {"trades": len(reg), "fasce": fr,
                                  "verdetto_regime": verdetto_fasce(fr)},
            "fear_greed": {"trades": len(fg), "fasce": fasce_fear_greed(fg)}}


def calibrate(trades: Iterable[dict]) -> dict:
    """Verdetto sulla calibrazione + `trust` da applicare in allocation.

    trust 1.0 = la confidenza conta come oggi; 0.0 = non influenza piu' la size.
    Dal 26 set 2026 porta anche `regime_confidence` e `fear_greed` (vedi
    `misure_contesto`): misure, che `trust` non legge."""
    trades = list(trades)
    contesto = misure_contesto(trades)
    # i trade del paper esplorativo (25 set 2026, F1bis) restano fuori: la
    # calibrazione tara la fiducia nella confidenza delle VALIDATE, e un
    # quasi-passaggio a size ridotta e' un'altra popolazione
    pairs = [(float(t["confidence_at_entry"]), float(t["pnl_pct"]))
             for t in trades
             if str(t.get("exit_reason", "")) not in _EXTERNAL
             and not t.get("esplorativa")
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
                    "note": _constant_note(lo, hi, n), **contesto}

    if n < settings.CALIBRATION_MIN_TRADES:
        return {"verdict": INSUFFICIENT, "trades": n, "correlation": corr,
                "buckets": buckets, "trust": 1.0,
                "note": f"servono {settings.CALIBRATION_MIN_TRADES} trade, ce ne sono {n}",
                **contesto}

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
            "buckets": buckets, "monotonic": rising, "trust": trust, "note": note,
            **contesto}


def confidence_trust(cal_doc: dict | None) -> float:
    """Quanto fidarsi della confidenza (0..1). 1.0 se disattivata o senza dati:
    senza evidenza NON si devia dal comportamento validato dal gate."""
    if not settings.CALIBRATION_ENABLED or not cal_doc:
        return 1.0
    try:
        return max(0.0, min(1.0, float(cal_doc.get("trust", 1.0))))
    except (TypeError, ValueError):
        return 1.0
