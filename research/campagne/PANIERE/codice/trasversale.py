"""Idea B, momentum trasversale fra monete: le sei varianti B1, B2, B3, long e short.

Modulo della variante per research/src/gruppo.py (contratto nella sua docstring, con la correzione 1 di
regole.md, sezione 8). Regole in ipotesi.md, idea B, punto 6.

Parametri ``p``:
* ``direzione``: "long" o "short";
* ``giorni_rendimento``: 28 (B1, B3) o 14 (B2);
* ``monete_per_lato``: 10 (B1, B2) o 20 (B3);
* ``storia_minima``: 90 (giorni di storia per entrare in classifica);
* ``multiplo_atr`` (2,5), ``barre_atr`` (20), ``barre_massime`` (60).

Scelte scritte prima di ogni dato:
* il ribilanciamento «lunedì alle 00:00 UTC» è la chiusura della barra della DOMENICA (regole.md, sezione 8,
  correzione 1): la classifica si legge sulle righe del paniere fino alla domenica e l'ordine limite vale per il
  lunedì;
* classifica con ``paniere.classifica_ultimo_giorno(righe, giorni_rendimento, storia_minima)``: BTCUSDT escluso,
  fuori le monete sotto la liquidità quel giorno e quelle senza una chiusura 90 giorni prima, parità alfabetica;
* long: la moneta è fra le prime ``monete_per_lato``; short: fra le ultime ``monete_per_lato``
  (rango > n_monete - monete_per_lato); se le monete classificate sono meno di 2 × monete_per_lato, nessun segnale
  (le prime e le ultime si sovrapporrebbero);
* una posizione aperta, alla domenica successiva, resta se la moneta è ancora nelle sue ``monete_per_lato``,
  altrimenti esce («chiudi», eseguito all'apertura del lunedì); uscita a tempo dopo 60 barre in posizione; dopo uno
  stop si rientra solo a un ribilanciamento;
* la riga del paniere letta è quella dello stesso giorno della barra (``ts`` uguale); se manca, nessun segnale e
  nessuna uscita a segnale quel giorno.
"""

from research.src.motore import Segnale
from research.src import paniere

GIORNO_MS = 86_400_000
DOMENICA = 6  # lunedì = 0; il 1970-01-01 era un giovedì (3)


def _domenica(ts):
    return (ts // GIORNO_MS + 3) % 7 == DOMENICA


def _atr(storia, barre):
    if len(storia) < barre + 1:
        return None
    somma = 0.0
    for k in range(len(storia) - barre, len(storia)):
        c, prima = storia[k], storia[k - 1]
        somma += max(c.high - c.low, abs(c.high - prima.close), abs(c.low - prima.close))
    return somma / barre


def _segnale(storia, p):
    if len(storia) < p["barre_atr"] + 1:
        return None
    atr = _atr(storia, p["barre_atr"])
    if atr is None or atr <= 0:
        return None
    chiusura = storia[-1].close
    if p["direzione"] == "long":
        return Segnale("long", chiusura - p["multiplo_atr"] * atr)
    return Segnale("short", chiusura + p["multiplo_atr"] * atr)


def _nel_proprio_lato(ctx, storia, p):
    """True / False alla domenica se la moneta è nelle sue ``monete_per_lato``; None se non si può dire."""
    barra = storia[-1]
    if not _domenica(barra.ts):
        return None
    righe = ctx.paniere_chiuse_entro(barra.close_ts)
    if not len(righe) or righe[-1].ts != barra.ts:
        return None
    ranghi, n_monete = paniere.classifica_ultimo_giorno(righe, p["giorni_rendimento"], p["storia_minima"])
    k = p["monete_per_lato"]
    if n_monete < 2 * k:
        return None
    rango = ranghi.get(ctx.simbolo)
    if rango is None:
        return False
    if p["direzione"] == "long":
        return rango <= k
    return rango > n_monete - k


def _barre_in_posizione(storia, posizione):
    n = 0
    for k in range(len(storia) - 1, -1, -1):
        if storia[k].ts < posizione.ts_entrata:
            break
        n += 1
    return n


def _uscita(ctx, storia, posizione, p):
    if _barre_in_posizione(storia, posizione) >= p["barre_massime"]:
        return True
    return _nel_proprio_lato(ctx, storia, p) is False


def _strategia(ctx, p, entra):
    def strategia(storia, posizione):
        if posizione is not None:
            return "chiudi" if _uscita(ctx, storia, posizione, p) else None
        segnale = _segnale(storia, p)
        if segnale is None or not entra(storia):
            return None
        return segnale

    return strategia


def crea_variante(ctx, p):
    def crea():
        return _strategia(ctx, p, lambda storia: _nel_proprio_lato(ctx, storia, p) is True)
    return crea


def crea_a(ctx, p):
    def crea():
        return _strategia(ctx, p, lambda storia: True)
    return crea


def crea_casuale(ctx, p):
    def crea_casuale_(ingressi):
        ingressi = frozenset(ingressi)
        return _strategia(ctx, p, lambda storia: (len(storia) - 1) in ingressi)
    return crea_casuale_


def crea_segnale(ctx, p):
    def crea_segnale_():
        return lambda storia: _segnale(storia, p)
    return crea_segnale_
