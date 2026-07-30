"""
Logica di uscita CONDIVISA tra backtest (GATE 1) e live executor.

Tenerla in un solo posto garantisce che il paper trading si comporti ESATTAMENTE
come la validazione: stesso stop, stesso profit-lock, stessi parametri.

profit-lock (protezione del profitto):
  Quando una posizione va in profitto ma non tocca il take-profit, invece di
  restituire tutto il guadagno blocchiamo una parte del MIGLIOR profitto visto.
  - si "arma" quando il prezzo ha coperto PROFIT_LOCK_TRIGGER della distanza
    entry->TP (es. metà strada);
  - una volta armato, lo stop sale (long) / scende (short) a
    entry +/- PROFIT_LOCK_KEEP * (miglior_escursione_favorevole),
    e può solo MIGLIORARE (ratchet), mai peggiorare.
"""
from __future__ import annotations

from bot.config import settings


def locked_stop(entry: float, target: float, long: bool,
                best_favorable_price: float, base_stop: float,
                keep: float | None = None) -> float:
    """
    Ritorna lo stop EFFETTIVO data la migliore escursione favorevole vista finora.
    Se il profit-lock non è armato (o disattivato) ritorna lo stop base invariato.

    `best_favorable_price` è il prezzo più favorevole raggiunto FINORA (il massimo
    per un long, il minimo per uno short), escludendo la barra corrente per evitare
    look-ahead nel backtest.

    `keep`: frazione del miglior guadagno da bloccare. None -> default globale
    (PROFIT_LOCK_KEEP, il valore VALIDATO dal gate). Il bot live puo' passare il
    valore IMPARATO per-strategia dai verdetti trailing (metrics.compute_trailing_keep).
    """
    if not settings.PROFIT_LOCK_ENABLED:
        return base_stop
    tp_dist = abs(target - entry)
    if tp_dist <= 0:
        return base_stop
    fav_move = (best_favorable_price - entry) if long else (entry - best_favorable_price)
    if fav_move <= 0 or fav_move < settings.PROFIT_LOCK_TRIGGER * tp_dist:
        return base_stop  # non ancora armato
    lock = (settings.PROFIT_LOCK_KEEP if keep is None else keep) * fav_move
    locked = entry + lock if long else entry - lock
    # lo stop può solo migliorare: sale per i long, scende per gli short
    return max(base_stop, locked) if long else min(base_stop, locked)


# ---- SCALE DI TP CANDIDATE (per la taratura per-coppia dal GATE) ------------ #
# La scala giusta NON e' la stessa per tutte le coppie: R e' gia' normalizzato sulla
# volatilita' (R = atr_mult x ATR), quindi la domanda non e' "quanto e' volatile la
# coin" ma "quanto TENDE, in unita' della sua volatilita'". Una coin che ritraccia
# subito non vedra' mai 5R; una che tende lo supera. Per questo la scala e' un
# PARAMETRO da validare per coppia, non una costante globale.
# Le quote (30/30/40) restano fisse: sono il risultato VALIDATO dall'A/B, e farle
# variare qui allargherebbe lo spazio di ricerca senza una domanda aperta a cui
# rispondere. Questo elenco e' un punto di partenza da rivedere sui dati misurati
# (mfe_r: dove arriva davvero il prezzo, in unita' di R).
SCALE_LADDER_CANDIDATES: tuple[tuple[float, ...], ...] = (
    (1.0, 1.5, 2.5),    # molto corta: incassa presto, per coppie che ritracciano
    (1.0, 2.0, 3.0),    # corta
    (1.5, 3.0, 5.0),    # attuale (default globale dall'A/B)
    (2.0, 4.0, 6.0),    # lunga: per coppie che tendono davvero
)


def scale_ladder(entry: float, base_stop: float, long: bool,
                 r_mults=None, fracs=None) -> list[tuple[float, float]]:
    """Scala di take-profit a MULTIPLI di R (R = |entry - base_stop|).

    Ritorna [(price, fraction), ...] in ordine di R crescente. L'ultimo livello è
    il TP FINALE. Vuota se R<=0 o scale-out disattivo. CONDIVISA tra backtest e
    live per garantire la parità GATE 1 <-> paper.
    """
    r_mults = settings.SCALE_OUT_R_MULTIPLES if r_mults is None else r_mults
    fracs = settings.SCALE_OUT_FRACTIONS if fracs is None else fracs
    R = abs(entry - base_stop)
    if R <= 0 or not r_mults:
        return []
    out: list[tuple[float, float]] = []
    for m, f in zip(r_mults, fracs):
        price = entry + m * R if long else entry - m * R
        out.append((price, f))
    return out


def effective_param_grid(grid: dict) -> dict:
    """Griglia di ricerca EFFETTIVA per una strategia, in base al modello di uscita.

    Sotto scale-out il take-profit non e' piu' `rr` x R: e' la SCALA di gradini. `rr`
    resta nella griglia ma non ha NESSUN effetto sulle uscite (il ramo scale-out non
    usa `target`), quindi con `--max-combos` che campiona a caso finirebbe per diluire
    la ricerca su un parametro morto — misurato: 67-75% delle combinazioni campionate
    sarebbero cloni. Qui `rr` viene SOSTITUITO dalla scala: stesso numero di
    combinazioni, ma tarate su cio' che decide davvero le uscite.
    Senza scale-out la griglia resta identica a prima."""
    if not settings.SCALE_OUT_ENABLED or "rr" not in grid:
        return grid
    out = {k: v for k, v in grid.items() if k != "rr"}
    out["scale_r_mults"] = list(SCALE_LADDER_CANDIDATES)
    return out


def ladder_multiples(params: dict | None) -> tuple | None:
    """Multipli di R da usare per QUESTA coppia, letti dai params validati dal gate.

    None -> `scale_ladder` usa il default globale (SCALE_OUT_R_MULTIPLES). E' il caso
    delle coppie non ancora ri-validate col nuovo spazio di ricerca: continuano a
    operare con la scala CON CUI SONO STATE VALIDATE, quindi la parita' gate<->paper
    regge anche a registro misto durante la migrazione."""
    if not params:
        return None
    v = params.get("scale_r_mults")
    if not v:
        return None
    try:
        out = tuple(float(x) for x in v)
    except (TypeError, ValueError):
        return None
    return out or None


def mfe_in_r(entry: float, best_favorable: float, base_stop: float) -> float:
    """Massima escursione FAVOREVOLE in unita' di R (R = |entry - stop base|).

    E' la misura che rende decidibile la scala: da questo unico numero si sa quali
    gradini AVREBBE colpito QUALUNQUE scala, senza doverle provare una per una ne'
    sacrificare trade per esplorare. 0 se R non e' calcolabile."""
    R = abs(entry - base_stop)
    if R <= 0:
        return 0.0
    return abs(best_favorable - entry) / R


def scale_fills(ladder, stage: int, long: bool, hi: float, lo: float):
    """Quante fette della scala si riempiono nel range [lo, hi] a partire da `stage`.

    Ritorna (new_stage, fills) con fills = [(price, fraction), ...] nell'ordine.
    Per il live basta passare hi=lo=mark. I livelli si riempiono in sequenza: un
    livello superiore non può riempirsi prima di quello inferiore.
    """
    fills: list[tuple[float, float]] = []
    while stage < len(ladder):
        price, frac = ladder[stage]
        reached = (hi >= price) if long else (lo <= price)
        if not reached:
            break
        fills.append((price, frac))
        stage += 1
    return stage, fills


def trailing_verdict(candles, stop: float, target: float, long: bool) -> str:
    """Controfattuale su un'uscita TRAILING: se avessimo TENUTO (stop base + TP),
    cosa sarebbe arrivato PRIMA scorrendo le candele DALL'uscita in avanti?
      - TP per primo   -> 'premature' (tagliato un vincitore)
      - stop base primo-> 'protected' (evitata una perdita)
      - nessuno / stessa candela -> 'neutral'
    Condivisa tra backtest (GATE 1) e bot (learning dal paper). `candles`: sequenza
    con attributi .high e .low."""
    for c in candles:
        tp_hit = (c.high >= target) if long else (c.low <= target)
        sl_hit = (c.low <= stop) if long else (c.high >= stop)
        if tp_hit and sl_hit:
            return "neutral"          # stessa candela: ordine intra-candela ignoto
        if tp_hit:
            return "premature"
        if sl_hit:
            return "protected"
    return "neutral"


def _atr(candles, period: int = 14) -> float:
    """ATR semplice (media dei true range) sulle candele date. 0 se dati insufficienti."""
    if len(candles) < 2:
        return 0.0
    trs, prev = [], candles[0].close
    for c in candles[1:]:
        trs.append(max(c.high - c.low, abs(c.high - prev), abs(c.low - prev)))
        prev = c.close
    window = trs[-period:] if len(trs) >= period else trs
    return sum(window) / len(window) if window else 0.0


def trailing_reason(during, after, entry: float, exit_price: float,
                    stop: float, target: float, long: bool) -> dict:
    """Verdetto trailing + il PERCHE', per capire come ridurre i 'premature'.

    - verdict: 'premature' | 'protected' | 'neutral' (dal prezzo DOPO l'uscita).
    - miss_to_tp: frazione del tragitto entry->TP lasciata sul tavolo all'uscita
      (0 = uscito al TP, 1 = uscito all'entrata). Premature con miss piccola = per un
      soffio, un trail piu' largo lo prende.
    - knockout_atr: profondita' del ritracciamento che ha fatto scattare il trail
      (dal massimo/minimo raggiunto fino all'uscita) in MULTIPLI di ATR. < ~1 = rumore
      (un trail consapevole dell'ATR lo eviterebbe); grande = inversione reale.

    `during` = candele TRA entrata e uscita (per max/min e ATR); `after` = candele
    DALL'uscita in avanti (per il controfattuale)."""
    verdict = trailing_verdict(after, stop, target, long)
    tp_dist = abs(target - entry) or 1e-9
    miss = min(1.0, abs(target - exit_price) / tp_dist)
    hw = (max((c.high for c in during), default=exit_price) if long
          else min((c.low for c in during), default=exit_price))
    dip = (hw - exit_price) if long else (exit_price - hw)
    atr = _atr(during)
    return {
        "verdict": verdict,
        "miss_to_tp": round(miss, 3),
        "knockout_atr": round(dip / atr, 2) if atr > 0 else None,
    }
