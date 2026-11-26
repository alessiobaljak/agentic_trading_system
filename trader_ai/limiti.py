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
#: La commissione d'entrata a mercato con lo scarto di prezzo (0,05% + 0,01%): il conto la vuole dentro il disponibile.
SPESE_ENTRATA_MAX = 0.0006


@dataclass
class Posizione:
    lato: str                        # «lungo» o «corto»
    quantita: float
    entrata: float
    leva: float
    stop: float
    obiettivo: Optional[float] = None
    liquidazione: Optional[float] = None
    #: un ordine limite non ancora eseguito: nessuna posizione e nessun risultato; `entrata` è il prezzo limite (controllo del 26
    #: novembre 2026, punto 2.1: il modello lo prendeva per un'operazione aperta in guadagno)
    in_attesa: bool = False


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


def _stop_ok(lato: str, prezzo: float, stop: Optional[float], leva: float, liquidazione: Optional[float],
             nome: str = "del prezzo") -> Optional[str]:
    """`nome`: di quale prezzo si parla nel motivo dello scarto («del prezzo» di adesso o «del prezzo limite»)."""
    if stop is None or stop <= 0:
        return "manca lo stop"
    if lato == "lungo" and stop >= prezzo or lato == "corto" and stop <= prezzo:
        verso = "sotto" if lato == "lungo" else "sopra"
        return f"stop {stop:.10g} dalla parte sbagliata {nome} {prezzo:.10g} (per un {lato} va {verso})"
    if liquidazione:
        oltre = stop <= liquidazione if lato == "lungo" else stop >= liquidazione
        if oltre:
            return f"stop oltre il prezzo di liquidazione {liquidazione:.10g}"
    elif abs(prezzo - stop) / prezzo > MARGINE_LIQUIDAZIONE / leva:
        return f"stop {stop:.10g} troppo lontano {nome} {prezzo:.10g} per la leva {leva:g}: arriverebbe prima la liquidazione"
    return None


def _obiettivo_ok(lato: str, prezzo: float, obiettivo: Optional[float], nome: str = "del prezzo") -> Optional[str]:
    if obiettivo is not None and (lato == "lungo" and obiettivo <= prezzo or lato == "corto" and obiettivo >= prezzo):
        verso = "sopra" if lato == "lungo" else "sotto"
        return f"obiettivo {obiettivo:.10g} dalla parte sbagliata {nome} {prezzo:.10g} (per un {lato} va {verso})"
    return None


def controlla(r: Risposta, c: Conto, prezzo: float) -> Optional[str]:
    """None se la decisione si può eseguire, altrimenti il motivo dello scarto."""
    if r.azione == "aspetta":
        return None
    if r.azione in ("apri_lungo", "apri_corto"):
        if c.posizione is not None and c.posizione.in_attesa:
            return "c'è un ordine limite in attesa: per aprire altro prima annullalo con «chiudi»"
        if c.posizione is not None:
            return "c'è già un'operazione aperta: prima chiudi"
        if r.leva is None or not 1 <= r.leva <= LEVA_MAX:
            return f"leva {r.leva} fuori da 1-{LEVA_MAX:g}"
        if r.tipo_ordine != "limite" and r.prezzo_limite is not None:
            return "prezzo_limite con tipo_ordine «mercato»: per un ordine limite serve tipo_ordine «limite»"
        if r.margine_usdt is None or r.margine_usdt <= 0:
            return "manca il margine"
        if r.margine_usdt > c.disponibile:
            return f"margine {r.margine_usdt:.2f} oltre il disponibile {c.disponibile:.2f}"
        if r.leva and r.margine_usdt * (1 + r.leva * SPESE_ENTRATA_MAX) > c.disponibile:
            # il conto vuole anche la commissione d'entrata (con lo scarto) dentro il disponibile (revisione del 26 novembre, R7-04)
            return (f"margine {r.margine_usdt:.2f} più la commissione d'entrata ({r.margine_usdt * r.leva * SPESE_ENTRATA_MAX:.2f}) "
                    f"oltre il disponibile {c.disponibile:.2f}")
        if r.margine_usdt * r.leva < ORDINE_MIN_VALORE:
            return f"valore {r.margine_usdt * r.leva:.2f} USDT sotto il minimo di {ORDINE_MIN_VALORE:g}"
        lato = "lungo" if r.azione == "apri_lungo" else "corto"
        limite = r.tipo_ordine == "limite"
        rif = r.prezzo_limite if limite else prezzo
        if limite and (rif is None or rif <= 0):
            return "ordine limite senza prezzo"
        nome = "del prezzo limite" if limite else "del prezzo"
        motivo = _stop_ok(lato, rif, r.stop_prezzo, r.leva, None, nome) or _obiettivo_ok(lato, rif, r.obiettivo_prezzo, nome)
        if not motivo and limite and (rif >= prezzo if lato == "lungo" else rif <= prezzo):
            # un limite già oltre il prezzo si esegue subito a mercato: stop e obiettivo valgono anche sul prezzo di adesso
            # (revisione del 26 novembre 2026, problema 193)
            motivo = (_stop_ok(lato, prezzo, r.stop_prezzo, r.leva, None, "del prezzo di adesso")
                      or _obiettivo_ok(lato, prezzo, r.obiettivo_prezzo, "del prezzo di adesso"))
        return motivo
    p = c.posizione
    if p is None:
        return "nessuna operazione aperta"
    if r.azione == "chiudi":
        return None
    if r.azione == "modifica":
        if r.stop_prezzo is None and r.obiettivo_prezzo is None:
            return "modifica senza stop né obiettivo"
        if p.in_attesa:
            # l'ordine non è eseguito: stop e obiettivo si misurano dal prezzo limite, dove l'operazione comincerà (controllo del 26
            # novembre 2026, punto 2.1: sei modifiche accettate con lo stop dalla parte sbagliata del limite); lo stop non deve
            # nemmeno scattare subito al prezzo di adesso
            if r.stop_prezzo is not None:
                motivo = _stop_ok(p.lato, p.entrata, r.stop_prezzo, p.leva, None, "del prezzo limite")
                if not motivo and (r.stop_prezzo >= prezzo if p.lato == "lungo" else r.stop_prezzo <= prezzo):
                    motivo = f"stop {r.stop_prezzo:.10g} scatterebbe subito: è dalla parte sbagliata del prezzo di adesso {prezzo:.10g}"
                if motivo:
                    return motivo
            return _obiettivo_ok(p.lato, p.entrata, r.obiettivo_prezzo, "del prezzo limite")
        if r.stop_prezzo is not None:
            motivo = _stop_ok(p.lato, prezzo, r.stop_prezzo, p.leva, p.liquidazione)
            if motivo:
                return motivo
        return _obiettivo_ok(p.lato, prezzo, r.obiettivo_prezzo)
    return "azione sconosciuta"
