"""I limiti fissi del trader AI (REGOLE.md, sezione 6): il modello propone, questo codice decide.

Ogni decisione fuori limite si scarta con il suo motivo; le altre dello stesso giro vanno avanti. I numeri sono una proposta
della sessione «trading AI» (23 novembre 2026): li cambia solo il proprietario.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Tuple

from trader_ai.schema import Decisione

MARGINE_MAX_QUOTA = 0.20        # margine di una posizione, come frazione del conto
LEVA_MAX = 3.0
ESPOSIZIONE_MAX_VOLTE = 2.0     # valore di tutte le posizioni / conto
POSIZIONI_MAX = 8
VOLUME_MIN_24H = 20_000_000     # USDT scambiati nelle 24 ore
STOP_MIN, STOP_MAX = 0.005, 0.25  # distanza dello stop dal prezzo
ORDINE_MIN_USDT = 20.0
PERDITA_GIORNO_MAX = 0.10       # dalla mezzanotte UTC: chiude tutto, niente aperture fino a mezzanotte
PERDITA_MAX = 0.35              # dal massimo del conto: chiude tutto e si ferma


@dataclass
class Posizione:
    moneta: str
    lato: str            # "lungo" o "corto"
    quantita: float      # sempre positiva
    entrata: float
    stop: float
    obiettivo: Optional[float] = None


@dataclass
class Portafoglio:
    conto: float                      # saldo più guadagni e perdite aperti, in USDT
    conto_mezzanotte: float
    massimo_conto: float
    posizioni: Dict[str, Posizione] = field(default_factory=dict)
    fermo: bool = False               # perdita massima raggiunta: riparte solo con l'ok del proprietario


def stato_rischio(p: Portafoglio) -> Optional[str]:
    """«fermo» (perdita massima dal massimo), «blocco_giorno» (perdita del giorno) o None."""
    if p.fermo or (p.massimo_conto > 0 and p.conto <= p.massimo_conto * (1 - PERDITA_MAX)):
        return "fermo"
    if p.conto_mezzanotte > 0 and p.conto <= p.conto_mezzanotte * (1 - PERDITA_GIORNO_MAX):
        return "blocco_giorno"
    return None


def _esposizione(posizioni: Dict[str, Posizione], prezzi: Dict[str, float]) -> float:
    return sum(abs(x.quantita) * prezzi.get(m, x.entrata) for m, x in posizioni.items())


def controlla(decisioni: List[Decisione], p: Portafoglio, prezzi: Dict[str, float],
              volumi_24h: Dict[str, float]) -> Tuple[List[Decisione], List[Tuple[Decisione, str]]]:
    """Divide le decisioni in accettate e scartate (con il motivo). Le aperture accettate contano subito per i limiti
    delle decisioni che seguono nello stesso giro."""
    accettate: List[Decisione] = []
    scartate: List[Tuple[Decisione, str]] = []
    rischio = stato_rischio(p)
    posizioni = dict(p.posizioni)
    gia_toccate: set = set()

    for d in decisioni:
        m = d.moneta.strip().upper()
        d = d.model_copy(update={"moneta": m})
        prezzo = prezzi.get(m)
        motivo = None
        if prezzo is None or prezzo <= 0:
            motivo = "moneta non quotata"
        elif m in gia_toccate:
            motivo = "seconda decisione sulla stessa moneta nello stesso giro"
        elif d.azione in ("apri_lungo", "apri_corto"):
            motivo = _controlla_apertura(d, prezzo, p.conto, posizioni, prezzi, volumi_24h.get(m, 0.0), rischio)
            if motivo is None:
                q = d.quota_conto * d.leva * p.conto / prezzo
                posizioni[m] = Posizione(m, "lungo" if d.azione == "apri_lungo" else "corto", q, prezzo, d.stop_prezzo)
        else:
            motivo = _controlla_su_posizione(d, posizioni.get(m), prezzo)
        if motivo:
            scartate.append((d, motivo))
        else:
            accettate.append(d)
            gia_toccate.add(m)
    return accettate, scartate


def _distanza_stop_ok(lato: str, prezzo: float, stop: Optional[float]) -> Optional[str]:
    if stop is None or stop <= 0:
        return "manca lo stop"
    if lato == "lungo" and stop >= prezzo or lato == "corto" and stop <= prezzo:
        return "stop dalla parte sbagliata del prezzo"
    dist = abs(prezzo - stop) / prezzo
    if dist < STOP_MIN or dist > STOP_MAX:
        return f"stop a {dist:.2%} dal prezzo, fuori da {STOP_MIN:.1%}-{STOP_MAX:.0%}"
    return None


def _controlla_apertura(d: Decisione, prezzo: float, conto: float, posizioni: Dict[str, Posizione],
                        prezzi: Dict[str, float], volume: float, rischio: Optional[str]) -> Optional[str]:
    if rischio:
        return f"aperture bloccate ({rischio})"
    if d.moneta in posizioni:
        return "c'è già una posizione su questa moneta"
    if len(posizioni) >= POSIZIONI_MAX:
        return f"già {POSIZIONI_MAX} posizioni aperte"
    if volume < VOLUME_MIN_24H:
        return f"volume delle 24 ore {volume / 1e6:.1f} milioni, sotto {VOLUME_MIN_24H / 1e6:.0f}"
    if d.quota_conto is None or not 0 < d.quota_conto <= MARGINE_MAX_QUOTA:
        return f"quota del conto {d.quota_conto} fuori da 0-{MARGINE_MAX_QUOTA}"
    if d.leva is None or not 1 <= d.leva <= LEVA_MAX:
        return f"leva {d.leva} fuori da 1-{LEVA_MAX:g}"
    valore = d.quota_conto * d.leva * conto
    if valore < ORDINE_MIN_USDT:
        return f"ordine da {valore:.2f} USDT, sotto il minimo di {ORDINE_MIN_USDT:g}"
    if _esposizione(posizioni, prezzi) + valore > ESPOSIZIONE_MAX_VOLTE * conto:
        return f"l'esposizione totale supererebbe {ESPOSIZIONE_MAX_VOLTE:g} volte il conto"
    lato = "lungo" if d.azione == "apri_lungo" else "corto"
    motivo = _distanza_stop_ok(lato, prezzo, d.stop_prezzo)
    if motivo:
        return motivo
    if d.obiettivo_prezzo is not None and (
            lato == "lungo" and d.obiettivo_prezzo <= prezzo or lato == "corto" and d.obiettivo_prezzo >= prezzo):
        return "obiettivo dalla parte sbagliata del prezzo"
    if d.tipo_ordine == "limite" and (d.prezzo_limite is None or d.prezzo_limite <= 0):
        return "ordine limite senza prezzo"
    return None


def _controlla_su_posizione(d: Decisione, pos: Optional[Posizione], prezzo: float) -> Optional[str]:
    if pos is None:
        return "nessuna posizione su questa moneta"
    if d.azione == "chiudi":
        return None
    if d.azione == "riduci":
        if d.quota_conto is None or not 0 < d.quota_conto < 1:
            return "riduci vuole una frazione fra 0 e 1 (esclusi)"
        return None
    if d.azione == "sposta_stop":
        motivo = _distanza_stop_ok(pos.lato, prezzo, d.stop_prezzo)
        if motivo:
            return motivo
        piu_stretto = d.stop_prezzo > pos.stop if pos.lato == "lungo" else d.stop_prezzo < pos.stop
        return None if piu_stretto else "lo stop si può solo stringere, mai allargare"
    if d.azione == "metti_obiettivo":
        o = d.obiettivo_prezzo
        if o is None or pos.lato == "lungo" and o <= prezzo or pos.lato == "corto" and o >= prezzo:
            return "obiettivo mancante o dalla parte sbagliata del prezzo"
        return None
    return "azione sconosciuta"
