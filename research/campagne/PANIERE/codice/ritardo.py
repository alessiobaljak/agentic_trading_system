"""Idea C, il ritardo delle monete dopo un giorno forte di Bitcoin: C1-1,5, C1-2 e C2-1,5, long e short.

Modulo della variante per research/src/gruppo.py (contratto nella sua docstring, con la correzione 1 di
regole.md, sezione 8). Regole in ipotesi.md, idea C, punto 6.

Parametri ``p``:
* ``direzione``: "long" (dopo un giorno forte al rialzo) o "short" (dopo un giorno forte al ribasso);
* ``k``: 1,5 o 2 (deviazioni standard dei 60 rendimenti precedenti di Bitcoin, almeno 40 finiti);
* ``monete_in_ritardo``: 0 per C1 (tutte le monete in ritardo), 20 per C2 (solo le 20 più in ritardo);
* ``giorni_deviazione`` (60), ``giorni_minimi_deviazione`` (40), ``barre_uscita`` (5);
* ``multiplo_atr`` (2,5), ``barre_atr`` (20), ``barre_massime`` (60).

Scelte scritte prima di ogni dato:
* tutto si legge dalle righe del paniere (``ctx.paniere_chiuse_entro``), che seguono il calendario UTC: il giorno
  forte con ``paniere.giorno_forte_ultimo`` sulle chiusure di BTCUSDT delle ultime 62 righe (se ne manca una,
  nessun segnale); il rendimento del giorno di ogni moneta con ``paniere.rendimenti_ultimo_giorno(righe, 1)``
  (fuori BTCUSDT e le monete sotto la liquidità quel giorno);
* «in ritardo» dopo un giorno forte al rialzo: rendimento del giorno della moneta strettamente sotto quello di
  Bitcoin (long); dopo un giorno forte al ribasso: strettamente sopra (short);
* C2: le monete in ritardo si ordinano per distanza dal rendimento di Bitcoin, dalla più lontana (parità
  alfabetica), e si tengono le prime 20;
* uscita a segnale: alla chiusura della quinta barra in posizione (la barra d'ingresso conta 1, quindi il quinto
  giorno dopo quello del segnale) la strategia chiede «chiudi», eseguito all'apertura del giorno dopo; uscita a
  tempo 60 barre (non scatta mai prima);
* la riga del paniere letta è quella dello stesso giorno della barra (``ts`` uguale); se manca, nessun segnale.
"""

from research.src.motore import Segnale
from research.src import paniere

RIFERIMENTO = "BTCUSDT"


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


def _in_ritardo(ctx, storia, p):
    """True se alla chiusura della barra corrente c'è un giorno forte di Bitcoin nella direzione e la moneta è in ritardo."""
    barra = storia[-1]
    n = p["giorni_deviazione"]
    righe = ctx.paniere_chiuse_entro(barra.close_ts)
    if len(righe) < n + 2 or righe[-1].ts != barra.ts:
        return False
    chiusure_btc = [r.chiusure.get(RIFERIMENTO) for r in righe[len(righe) - (n + 2):]]
    if any(c is None for c in chiusure_btc):
        return False
    forte = paniere.giorno_forte_ultimo(chiusure_btc, p["k"], n, p["giorni_minimi_deviazione"])
    verso = 1 if p["direzione"] == "long" else -1
    if forte != verso:
        return False
    r_btc = chiusure_btc[-1] / chiusure_btc[-2] - 1.0
    rendimenti = paniere.rendimenti_ultimo_giorno(righe, 1)
    if ctx.simbolo not in rendimenti:
        return False
    # distanza nella direzione del ritardo: positiva = in ritardo
    distanze = {s: verso * (r_btc - r) for s, r in rendimenti.items()}
    if distanze[ctx.simbolo] <= 0:
        return False
    if not p["monete_in_ritardo"]:
        return True
    in_ritardo = sorted((s for s, d in distanze.items() if d > 0), key=lambda s: (-distanze[s], s))
    return ctx.simbolo in in_ritardo[:p["monete_in_ritardo"]]


def _barre_in_posizione(storia, posizione):
    n = 0
    for k in range(len(storia) - 1, -1, -1):
        if storia[k].ts < posizione.ts_entrata:
            break
        n += 1
    return n


def _strategia(p, entra):
    def strategia(storia, posizione):
        if posizione is not None:
            tenute = _barre_in_posizione(storia, posizione)
            return "chiudi" if tenute >= p["barre_uscita"] or tenute >= p["barre_massime"] else None
        segnale = _segnale(storia, p)
        if segnale is None or not entra(storia):
            return None
        return segnale

    return strategia


def crea_variante(ctx, p):
    def crea():
        return _strategia(p, lambda storia: _in_ritardo(ctx, storia, p))
    return crea


def crea_a(ctx, p):
    def crea():
        return _strategia(p, lambda storia: True)
    return crea


def crea_casuale(ctx, p):
    def crea_casuale_(ingressi):
        ingressi = frozenset(ingressi)
        return _strategia(p, lambda storia: (len(storia) - 1) in ingressi)
    return crea_casuale_


def crea_segnale(ctx, p):
    def crea_segnale_():
        return lambda storia: _segnale(storia, p)
    return crea_segnale_
