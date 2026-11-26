"""Il messaggio al modello (REGOLE.md, versione 3, sezione 4). Istruzioni fisse nel `system` (in cache); dati della moneta, conto
e memoria nel messaggio. Solo candele chiuse entro l'ora della chiamata. Nessun dato dell'altra sessione."""
from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from trader_ai.indicatori import riassunto
from trader_ai.limiti import OBIETTIVO_GIORNO_QUOTA, Conto, obiettivo_usdt

ISTRUZIONI = Path(__file__).with_name("istruzioni.md")
#: Quante candele si mostrano per intervallo (gli indicatori si calcolano su tutte quelle ricevute, di solito 200).
MOSTRATE = {"5m": 48, "15m": 48, "30m": 48}


def taglia(candele: List[dict], ora: datetime) -> List[dict]:
    """Solo le candele chiuse entro l'ora della chiamata."""
    return [c for c in candele if c["chiusa"] <= ora]


def _n(x: Optional[float], cifre: int = 6) -> str:
    return "-" if x is None else f"{x:.{cifre}g}"


def blocco_intervallo(nome: str, candele: List[dict]) -> str:
    if not candele:
        return f"## candele {nome}: nessuna"
    ind = riassunto(candele)
    righe = [f"## candele {nome} (chiusa UTC, apertura, massimo, minimo, chiusura, volume)"]
    for c in candele[-MOSTRATE.get(nome, 48):]:
        righe.append(f"{c['chiusa'].strftime('%m-%d %H:%M')} {_n(c['apertura'])} {_n(c['massimo'])} {_n(c['minimo'])} "
                     f"{_n(c['chiusura'])} {_n(c['volume'], 5)}")
    righe.append("indicatori sull'ultima candela: " + ", ".join(f"{k} {_n(v)}" for k, v in ind.items()))
    return "\n".join(righe)


def blocco_conto(c: Conto, prezzo: float) -> str:
    guadagno = c.conto - c.conto_mezzanotte
    righe = [f"conto {c.conto:.2f} USDT, disponibile {c.disponibile:.2f}; guadagno da mezzanotte UTC {guadagno:+.2f}; "
             f"mancano {max(0.0, obiettivo_usdt(c) - guadagno):.2f} all'obiettivo di {obiettivo_usdt(c):.2f} "
             f"({OBIETTIVO_GIORNO_QUOTA:.0%} del conto a mezzanotte)"]
    p = c.posizione
    if p is None:
        righe.append("nessuna operazione aperta")
    else:
        segno = 1 if p.lato == "lungo" else -1
        righe.append(f"operazione aperta: {p.lato}, quantità {p.quantita:g}, entrata {_n(p.entrata)}, leva {p.leva:g}, "
                     f"stop {_n(p.stop)}, obiettivo {_n(p.obiettivo)}, liquidazione {_n(p.liquidazione)}, "
                     f"risultato {segno * (prezzo - p.entrata) * p.quantita:+.2f} USDT")
    return "\n".join(righe)


def bilancio_di_oggi(operazioni: List[dict], giorno: str, prezzo_mezzanotte: Optional[float], prezzo: float) -> str:
    """Il bilancio del giorno in chiaro (il proprietario, 26 novembre 2026: «è ovvio che l'AI deve sapere se il primo trade è
    fallito [...] altrimenti come impara»)."""
    oggi = [o for o in operazioni if str(o.get("chiusa", "")).startswith(giorno)]
    righe = [f"bilancio di oggi ({giorno}): {len(oggi)} operazioni chiuse, risultato {sum(o['risultato'] for o in oggi):+.2f} USDT"]
    for lato in ("lungo", "corto"):
        x = [o for o in oggi if o["lato"] == lato]
        if x:
            righe.append(f"- {lato}: {len(x)} operazioni, {sum(o['risultato'] > 0 for o in x)} vinte e "
                         f"{sum(o['risultato'] <= 0 for o in x)} perse, risultato {sum(o['risultato'] for o in x):+.2f} USDT")
    if prezzo_mezzanotte:
        righe.append(f"- il prezzo da mezzanotte: da {prezzo_mezzanotte:g} a {prezzo:g} ({(prezzo / prezzo_mezzanotte - 1) * 100:+.2f}%)")
    return "\n".join(righe)


def blocco_memoria(operazioni: List[dict], approccio: Optional[str], note: List[str], scarto: Optional[str],
                   bilancio: str = "") -> str:
    righe = ([bilancio] if bilancio else []) + [f"approccio attuale: {approccio or 'nessuno ancora'}"]
    if scarto:
        righe.append(f"la tua decisione precedente è stata SCARTATA dal codice: {scarto}")
    if operazioni:
        righe.append("ultime operazioni chiuse (apertura, lato, leva, entrata, uscita, come, risultato USDT, approccio):")
        for o in operazioni[-30:]:
            righe.append(f"{o['aperta']} {o['lato']} x{o['leva']:g} {_n(o['entrata'])} -> {_n(o['uscita'])} {o['come']} "
                         f"{o['risultato']:+.2f} [{o['approccio']}]")
    else:
        righe.append("nessuna operazione chiusa finora")
    if note:
        righe.append("tue ultime note:")
        righe += [f"- {x}" for x in note[-10:]]
    return "\n".join(righe)


def costruisci(ora: datetime, motivo: str, budget_rimasto: float, moneta: str, candele: Dict[str, List[dict]],
               mercato: Dict[str, Optional[float]], conto: Conto, memoria: str) -> tuple[str, str]:
    """Ritorna (system, utente). `candele`: intervallo («5m», «15m», «30m») -> candele; `mercato`: prezzo, funding, ecc."""
    prezzo = mercato["prezzo"]
    utente = "\n\n".join([
        f"ora {ora.strftime('%Y-%m-%d %H:%M')} UTC; motivo della chiamata: {motivo}; budget di chiamate rimasto oggi "
        f"{budget_rimasto:.2f} dollari",
        f"# {moneta}\n" + ", ".join(f"{k} {_n(v)}" for k, v in mercato.items()),
        "# Conto\n" + blocco_conto(conto, prezzo),
        "# La tua memoria\n" + memoria,
        *[blocco_intervallo(nome, taglia(c, ora)) for nome, c in candele.items()],
    ])
    return ISTRUZIONI.read_text(), utente
