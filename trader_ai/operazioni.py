"""I conti delle operazioni, per il modello e per il resoconto (controllo del 26 novembre 2026, punti 3.1, 3.2, 3.3 e 3.6): spese,
pareggio, netto allo stop e all'obiettivo, 1 R, quanto il prezzo è andato a favore e contro, il bilancio delle operazioni chiuse.

Solo calcoli sui numeri del conto e sulle candele: nessun consiglio di strategia. Le spese sono quelle del conto simulato (le stesse
del conto demo: decisione del 7 novembre 2026), lette dalle sue costanti e mai riscritte a mano.

«1 R» è la perdita netta prevista allo stop in vigore quando l'ordine si è eseguito (spese d'entrata e d'uscita comprese): un'uscita
a quello stop vale circa −1 R.
"""
from __future__ import annotations

from datetime import datetime, timezone
from statistics import median
from typing import Dict, List, Optional, Tuple

from trader_ai.conto_simulato import COMMISSIONE_LIMITE, COMMISSIONE_MERCATO, scarto

MIN_MS = 60_000


def spese_entrata(valore: float, limite: bool) -> float:
    """La commissione d'entrata (lo scarto di prezzo di un ordine a mercato è già dentro il prezzo d'entrata)."""
    return valore * (COMMISSIONE_LIMITE if limite else COMMISSIONE_MERCATO)


def uscita_effettiva(lato: str, livello: float, simbolo: str) -> float:
    """Il prezzo a cui si esce a mercato quando scatta un livello (stop, obiettivo o «chiudi»): lo scarto è sempre contro."""
    return livello * (1 - scarto(simbolo)) if lato == "lungo" else livello * (1 + scarto(simbolo))


def netto_a(lato: str, entrata: float, quantita: float, livello: float, spese_pagate: float, funding: float,
            simbolo: str) -> float:
    """Il risultato netto se l'operazione esce a mercato al livello dato: prezzo, commissione e scarto d'uscita, spese già pagate
    e funding già ricevuto (positivo) o pagato (negativo)."""
    u = uscita_effettiva(lato, livello, simbolo)
    lordo = (u - entrata) * quantita if lato == "lungo" else (entrata - u) * quantita
    return lordo - u * quantita * COMMISSIONE_MERCATO - spese_pagate + funding


def pareggio(lato: str, entrata: float, quantita: float, spese_pagate: float, funding: float, simbolo: str) -> float:
    """Il prezzo a cui un'uscita a mercato chiude a zero netto."""
    sc, f, a = scarto(simbolo), COMMISSIONE_MERCATO, (spese_pagate - funding) / quantita
    if lato == "lungo":
        return (entrata + a) / ((1 - sc) * (1 - f))
    return (entrata - a) / ((1 + sc) * (1 + f))


def un_r(lato: str, entrata: float, quantita: float, stop: Optional[float], spese_pagate: float,
         simbolo: str) -> Optional[float]:
    """1 R in USDT: la perdita netta allo stop (spese comprese, funding escluso). None se lo stop manca o non è una perdita."""
    if not stop:
        return None
    r = -netto_a(lato, entrata, quantita, stop, spese_pagate, 0.0, simbolo)
    return r if r > 0 else None


def escursione(candele_1m: List[dict], lato: str, entrata: float, eseguita_ms: int, chiusa_ms: Optional[int] = None,
               da_limite: bool = False) -> Tuple[float, float]:
    """Quanto il prezzo degli scambi è andato al massimo a favore e al massimo contro (in prezzo, ≥ 0) fra l'esecuzione e la chiusura
    (o adesso), dalle candele da 1 minuto. Il minuto dell'esecuzione: per un ordine limite conta solo il lato contrario (il lato a
    favore può essere venuto prima dell'esecuzione); per un ordine a mercato non conta (non si sa a che secondo è partito). Il minuto
    della chiusura conta intero."""
    lungo = lato == "lungo"
    m_es = eseguita_ms - eseguita_ms % MIN_MS
    favore = contro = 0.0
    for c in candele_1m:
        t = int(c["aperta"].timestamp() * 1000)
        if t < m_es:
            continue
        if chiusa_ms is not None and t > chiusa_ms:
            break
        alto, basso = c["massimo"], c["minimo"]
        if t == m_es:
            if da_limite:
                contro = max(contro, entrata - basso if lungo else alto - entrata)
            continue
        favore = max(favore, alto - entrata if lungo else entrata - basso)
        contro = max(contro, entrata - basso if lungo else alto - entrata)
    return favore, contro


#: Come si è chiusa un'operazione, per gruppi (la scheda e il bilancio li contano). «stop spostato da te prima dell'esecuzione»:
#: lo stop in vigore all'esecuzione l'aveva già spostato il modello mentre l'ordine limite aspettava (revisione del 26 novembre
#: 2026, punto B2: su 7 «stop iniziale» del 25-26 novembre, 5 erano così).
CATEGORIE = ("obiettivo", "stop iniziale", "stop spostato da te prima dell'esecuzione", "stop spostato da te", "chiusa da te",
             "liquidazione", "altro")


def tipo_di_stop(spostamenti: List[dict]) -> str:
    """Come chiamare un'uscita allo stop, dagli spostamenti dello stop."""
    stop = [s for s in spostamenti if s.get("campo") == "stop"]
    if any(not s.get("prima_dell_esecuzione") for s in stop):
        return "stop spostato da te"
    if stop:
        return "stop spostato da te prima dell'esecuzione"
    return "stop iniziale"


def categoria(come: str) -> str:
    come = come or ""
    if come in CATEGORIE[:-1] and come != "chiusa da te":
        return come
    if come in ("chiusa da te", "chiusa dal modello"):
        return "chiusa da te"
    if come == "stop":
        return "stop iniziale"          # memoria vecchia senza il diario per distinguerlo: il caso più comune
    return "altro"


def ms(iso: Optional[str]) -> Optional[int]:
    return int(datetime.fromisoformat(iso).timestamp() * 1000) if iso else None


def iso_da_ms(t: Optional[int]) -> Optional[str]:
    return datetime.fromtimestamp(t / 1000, timezone.utc).isoformat() if t else None


def durata_min(op: dict) -> Optional[float]:
    a, b = ms(op.get("eseguita") or op.get("aperta")), ms(op.get("chiusa"))
    return (b - a) / MIN_MS if a and b else None


def bilancio(ops: List[dict]) -> Dict[str, object]:
    """Somme e conteggi di un gruppo di operazioni chiuse."""
    uscite = {k: 0 for k in CATEGORIE}
    for o in ops:
        uscite[categoria(o.get("come", ""))] += 1
    durate = [d for d in (durata_min(o) for o in ops) if d is not None]
    prezzo = sum(o["risultato_prezzo"] for o in ops if o.get("risultato_prezzo") is not None)
    spese, funding = sum(o.get("spese") or 0.0 for o in ops), sum(o.get("funding") or 0.0 for o in ops)
    con_dettaglio = all(o.get("risultato_prezzo") is not None for o in ops)
    # con il dettaglio il netto è la somma delle parti (non dei risultati già arrotondati: punto B1 della revisione)
    netto = prezzo - spese + funding if con_dettaglio and ops else sum(o["risultato"] for o in ops)
    return {"n": len(ops), "netto": netto, "prezzo": prezzo, "spese": spese, "funding": funding, "con_dettaglio": con_dettaglio,
            "vinte": sum(o["risultato"] > 0 for o in ops), "perse": sum(o["risultato"] < 0 for o in ops),
            "uscite": uscite, "durata_mediana": median(durate) if durate else None}


def serie_perdente(ops: List[dict]) -> List[dict]:
    """Le operazioni perse di fila, dall'ultima indietro (vuota se l'ultima non è una perdita)."""
    out = []
    for o in reversed(ops):
        if o["risultato"] >= 0:
            break
        out.append(o)
    return list(reversed(out))
