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
                best_favorable_price: float, base_stop: float) -> float:
    """
    Ritorna lo stop EFFETTIVO data la migliore escursione favorevole vista finora.
    Se il profit-lock non è armato (o disattivato) ritorna lo stop base invariato.

    `best_favorable_price` è il prezzo più favorevole raggiunto FINORA (il massimo
    per un long, il minimo per uno short), escludendo la barra corrente per evitare
    look-ahead nel backtest.
    """
    if not settings.PROFIT_LOCK_ENABLED:
        return base_stop
    tp_dist = abs(target - entry)
    if tp_dist <= 0:
        return base_stop
    fav_move = (best_favorable_price - entry) if long else (entry - best_favorable_price)
    if fav_move <= 0 or fav_move < settings.PROFIT_LOCK_TRIGGER * tp_dist:
        return base_stop  # non ancora armato
    lock = settings.PROFIT_LOCK_KEEP * fav_move
    locked = entry + lock if long else entry - lock
    # lo stop può solo migliorare: sale per i long, scende per gli short
    return max(base_stop, locked) if long else min(base_stop, locked)


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
