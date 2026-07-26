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
