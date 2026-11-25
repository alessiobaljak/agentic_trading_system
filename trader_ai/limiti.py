"""I limiti nel codice (REGOLE.md, versione 3, sezione 6): pochi, per scelta del proprietario («non ci sono limiti nella demo»).

Restano: leva fino a 10, margine non oltre il disponibile, una sola operazione alla volta, stop obbligatorio dalla parte giusta e
prima della liquidazione, obiettivo del giorno del 3% del conto di mezzanotte (il proprietario, 25 novembre 2026: «il profitto
giornaliero mettilo al 3%»; prima 50 USDT) dopo il quale ci si ferma fino a mezzanotte UTC.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from trader_ai.schema import Risposta

OBIETTIVO_GIORNO_QUOTA = 0.03      # 3% del conto a mezzanotte UTC (30 USDT su 1.000)
LEVA_MAX = 10.0
#: Valore minimo di un ordine; per BTCUSDT Binance chiede 100 USDT (da confermare sul conto demo con le regole del simbolo).
ORDINE_MIN_VALORE = 100.0
#: Lo stop deve stare prima della liquidazione: con leva L la liquidazione arriva poco prima di un movimento di 1/L contro;
#: si tiene un margine del 10% (stop entro 0,9/L dal prezzo) se il conto non dà il prezzo di liquidazione.
MARGINE_LIQUIDAZIONE = 0.9


@dataclass
class Posizione:
    lato: str                        # «lungo» o «corto»
    quantita: float
    entrata: float
    leva: float
    stop: float
    obiettivo: Optional[float] = None
    liquidazione: Optional[float] = None


@dataclass
class Conto:
    conto: float                     # saldo più risultato aperto, USDT
    disponibile: float               # margine libero, USDT
    conto_mezzanotte: float
    posizione: Optional[Posizione] = None


def obiettivo_raggiunto(c: Conto) -> bool:
    return c.conto >= c.conto_mezzanotte + obiettivo_usdt(c)


def obiettivo_usdt(c: Conto) -> float:
    return c.conto_mezzanotte * OBIETTIVO_GIORNO_QUOTA


def _stop_ok(lato: str, prezzo: float, stop: Optional[float], leva: float, liquidazione: Optional[float]) -> Optional[str]:
    if stop is None or stop <= 0:
        return "manca lo stop"
    if lato == "lungo" and stop >= prezzo or lato == "corto" and stop <= prezzo:
        return "stop dalla parte sbagliata del prezzo"
    if liquidazione:
        oltre = stop <= liquidazione if lato == "lungo" else stop >= liquidazione
        if oltre:
            return f"stop oltre il prezzo di liquidazione {liquidazione:g}"
    elif abs(prezzo - stop) / prezzo > MARGINE_LIQUIDAZIONE / leva:
        return f"stop troppo lontano per la leva {leva:g}: arriverebbe prima la liquidazione"
    return None


def _obiettivo_ok(lato: str, prezzo: float, obiettivo: Optional[float]) -> Optional[str]:
    if obiettivo is not None and (lato == "lungo" and obiettivo <= prezzo or lato == "corto" and obiettivo >= prezzo):
        return "obiettivo dalla parte sbagliata del prezzo"
    return None


def controlla(r: Risposta, c: Conto, prezzo: float) -> Optional[str]:
    """None se la decisione si può eseguire, altrimenti il motivo dello scarto."""
    if r.azione == "aspetta":
        return None
    if r.azione in ("apri_lungo", "apri_corto"):
        if c.posizione is not None:
            return "c'è già un'operazione aperta: prima chiudi"
        if r.leva is None or not 1 <= r.leva <= LEVA_MAX:
            return f"leva {r.leva} fuori da 1-{LEVA_MAX:g}"
        if r.margine_usdt is None or r.margine_usdt <= 0:
            return "manca il margine"
        if r.margine_usdt > c.disponibile:
            return f"margine {r.margine_usdt:.2f} oltre il disponibile {c.disponibile:.2f}"
        if r.margine_usdt * r.leva < ORDINE_MIN_VALORE:
            return f"valore {r.margine_usdt * r.leva:.2f} USDT sotto il minimo di {ORDINE_MIN_VALORE:g}"
        lato = "lungo" if r.azione == "apri_lungo" else "corto"
        rif = r.prezzo_limite if r.tipo_ordine == "limite" else prezzo
        if r.tipo_ordine == "limite" and (rif is None or rif <= 0):
            return "ordine limite senza prezzo"
        return _stop_ok(lato, rif, r.stop_prezzo, r.leva, None) or _obiettivo_ok(lato, rif, r.obiettivo_prezzo)
    p = c.posizione
    if p is None:
        return "nessuna operazione aperta"
    if r.azione == "chiudi":
        return None
    if r.azione == "modifica":
        if r.stop_prezzo is None and r.obiettivo_prezzo is None:
            return "modifica senza stop né obiettivo"
        if r.stop_prezzo is not None:
            motivo = _stop_ok(p.lato, prezzo, r.stop_prezzo, p.leva, p.liquidazione)
            if motivo:
                return motivo
        return _obiettivo_ok(p.lato, prezzo, r.obiettivo_prezzo)
    return "azione sconosciuta"
