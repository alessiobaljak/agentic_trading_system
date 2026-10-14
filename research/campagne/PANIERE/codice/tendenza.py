"""Idea A, tendenza: le sei varianti A1-20, A1-55 (rottura del canale) e A2 (segno del rendimento), long e short.

Modulo della variante per research/src/gruppo.py (contratto nella sua docstring): le quattro funzioni
crea_variante, crea_a, crea_casuale e crea_segnale, al livello del modulo. Regole in ipotesi.md, idea A, punto 6.

Parametri ``p`` (il dizionario della registrazione):
* ``regola``: "A1" (rottura) o "A2" (segno del rendimento);
* ``direzione``: "long" o "short";
* per A1 ``n``: barre del canale d'ingresso (20 o 55); l'uscita usa ``n // 2`` barre;
* per A2 ``giorni_rendimento`` (60) e ``giorni_media`` (100);
* per tutte ``multiplo_atr`` (2,5), ``barre_atr`` (20), ``barre_massime`` (60).

Scelte scritte prima di ogni dato (ipotesi.md):
* «giorni» = barre della serie della moneta (le barre tolte dall'allineamento sono buchi e le finestre li
  attraversano);
* canale di A1 su high e low delle barre PRECEDENTI al giorno di segnale; l'uscita a segnale usa le
  ``n // 2`` barre precedenti al giorno in cui si decide;
* ATR(20) = media semplice dei true range delle ultime 20 barre, giorno di segnale compreso (servono 21
  barre); stop = chiusura del giorno di segnale -/+ 2,5 ATR;
* uscita a tempo: alla chiusura della 60a barra in posizione (la barra d'ingresso conta 1) la strategia
  chiede «chiudi», che il motore esegue all'apertura della barra dopo;
* la variante non tiene stato fra un'esecuzione e l'altra: ogni ``crea()`` restituisce una funzione nuova
  che legge solo la storia chiusa che il motore le passa.
"""

from research.src.motore import Segnale


def _atr(storia, barre):
    """Media semplice dei true range delle ultime ``barre`` barre (serve una barra in più); None se mancano."""
    if len(storia) < barre + 1:
        return None
    somma = 0.0
    for k in range(len(storia) - barre, len(storia)):
        c, prima = storia[k], storia[k - 1]
        somma += max(c.high - c.low, abs(c.high - prima.close), abs(c.low - prima.close))
    return somma / barre


def _riscaldamento(p):
    """Barre che servono per calcolare il segnale della variante alla barra corrente."""
    atr = p["barre_atr"] + 1
    if p["regola"] == "A1":
        return max(p["n"] + 1, atr)
    return max(p["giorni_rendimento"] + 1, p["giorni_media"], atr)


def _segnale(storia, p):
    """Il segnale senza la condizione d'ingresso: la direzione e lo stop a 2,5 ATR(20); None nel riscaldamento."""
    if len(storia) < _riscaldamento(p):
        return None
    atr = _atr(storia, p["barre_atr"])
    if atr is None or atr <= 0:
        return None
    chiusura = storia[-1].close
    if p["direzione"] == "long":
        return Segnale("long", chiusura - p["multiplo_atr"] * atr)
    return Segnale("short", chiusura + p["multiplo_atr"] * atr)


def _condizione_ingresso(storia, p):
    """True se alla chiusura della barra corrente vale la condizione d'ingresso dell'ipotesi."""
    c = storia[-1]
    if p["regola"] == "A1":
        n = p["n"]
        precedenti = storia[len(storia) - 1 - n:len(storia) - 1]
        if p["direzione"] == "long":
            return c.close > max(b.high for b in precedenti)
        return c.close < min(b.low for b in precedenti)
    rendimento = c.close / storia[len(storia) - 1 - p["giorni_rendimento"]].close - 1.0
    media = sum(b.close for b in storia[len(storia) - p["giorni_media"]:]) / p["giorni_media"]
    if p["direzione"] == "long":
        return rendimento > 0 and c.close > media
    return rendimento < 0 and c.close < media


def _barre_in_posizione(storia, posizione):
    """Barre della storia dalla barra d'ingresso (compresa) alla corrente."""
    n = 0
    for k in range(len(storia) - 1, -1, -1):
        if storia[k].ts < posizione.ts_entrata:
            break
        n += 1
    return n


def _uscita(storia, posizione, p):
    """True se la posizione aperta deve uscire alla chiusura della barra corrente (a segnale o a tempo)."""
    if _barre_in_posizione(storia, posizione) >= p["barre_massime"]:
        return True
    c = storia[-1]
    if p["regola"] == "A1":
        k = p["n"] // 2
        if len(storia) < k + 1:
            return False
        precedenti = storia[len(storia) - 1 - k:len(storia) - 1]
        if posizione.direzione == "long":
            return c.close < min(b.low for b in precedenti)
        return c.close > max(b.high for b in precedenti)
    if len(storia) < max(p["giorni_rendimento"] + 1, p["giorni_media"]):
        return False
    rendimento = c.close / storia[len(storia) - 1 - p["giorni_rendimento"]].close - 1.0
    media = sum(b.close for b in storia[len(storia) - p["giorni_media"]:]) / p["giorni_media"]
    if posizione.direzione == "long":
        return not (rendimento > 0 and c.close > media)
    return not (rendimento < 0 and c.close < media)


def _strategia(p, entra):
    """Una strategia nuova: ``entra(storia)`` dice se alla barra corrente si chiede l'ingresso."""

    def strategia(storia, posizione):
        if posizione is not None:
            return "chiudi" if _uscita(storia, posizione, p) else None
        segnale = _segnale(storia, p)
        if segnale is None or not entra(storia):
            return None
        return segnale

    return strategia


def crea_variante(ctx, p):
    def crea():
        return _strategia(p, lambda storia: _condizione_ingresso(storia, p))
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
