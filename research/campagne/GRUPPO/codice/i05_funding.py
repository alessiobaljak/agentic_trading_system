"""Idea I-05, affollamento misurato dal funding (ipotesi.md): una regola per tutte le monete del gruppo.

Funding delle ultime ``finestra_ore`` ore: la somma dei tassi dei regolamenti della moneta con istante nella
finestra (close_ts - finestra_ore, close_ts] della barra del segnale, letti con ctx.funding_regolato_entro (solo
regolamenti gia' avvenuti). La somma non dipende dall'intervallo del funding (8 o 4 ore): e' il costo di un giorno.
Ingresso (variante): short se la somma e' sopra ``soglia`` (long affollati); long se e' sotto -``soglia`` (short
affollati).
Uscita (uguale per variante, (a), casuale): stop a ``stop_atr`` ATR di Wilder dalla chiusura del segnale, nessun
target, chiusura all'apertura dopo ``tenuta`` barre tenute.
Contratto: docstring di research/src/gruppo.py.
"""
from bisect import bisect_left

from research.src.motore import Segnale

MS_ORA = 3_600_000


class _Barre:
    """Le barre chiuse ricevute fin qui, con l'ATR di Wilder aggiornato barra per barra (niente sguardo avanti)."""

    def __init__(self, periodo_atr):
        self.n = 0
        self.ts, self.cts, self.c, self.h, self.l = [], [], [], [], []
        self.atr = []
        self._p = periodo_atr
        self._somma = 0.0

    def aggiorna(self, storia):
        n = len(storia)
        if n < self.n:
            raise ValueError("la storia si e' accorciata: istanza riusata")
        for k in range(self.n, n):
            b = storia[k]
            if k == 0:
                tr = b.high - b.low
            else:
                pc = self.c[k - 1]
                tr = max(b.high - b.low, abs(b.high - pc), abs(b.low - pc))
            self.ts.append(b.ts)
            self.cts.append(b.close_ts)
            self.c.append(b.close)
            self.h.append(b.high)
            self.l.append(b.low)
            if k < self._p:
                self._somma += tr
                self.atr.append(self._somma / self._p if k == self._p - 1 else None)
            else:
                self.atr.append((self.atr[k - 1] * (self._p - 1) + tr) / self._p)
        self.n = n


def _riscaldamento(p):
    return p["atr"] - 1


def _segnale_base(B, p):
    k = B.n - 1
    if k < _riscaldamento(p) or B.atr[k] is None:
        return None
    distanza = p["stop_atr"] * B.atr[k]
    if p["direzione"] == "long":
        return Segnale("long", B.c[k] - distanza, None)
    return Segnale("short", B.c[k] + distanza, None)


def _funding_finestra(ctx, B, p):
    adesso = B.cts[B.n - 1]
    inizio = adesso - p["finestra_ore"] * MS_ORA
    regolati = ctx.funding_regolato_entro(adesso)
    somma = 0.0
    i = len(regolati) - 1
    while i >= 0 and regolati[i][0] > inizio:
        somma += regolati[i][1]
        i -= 1
    return somma


def _condizione(ctx, B, p):
    f = _funding_finestra(ctx, B, p)
    return f < -p["soglia"] if p["direzione"] == "long" else f > p["soglia"]


def _strategia(ctx, p, modo, ingressi=None):
    B = _Barre(p["atr"])

    def strategia(storia, posizione):
        B.aggiorna(storia)
        if posizione is not None:
            tenute = B.n - bisect_left(B.ts, posizione.ts_entrata)
            return "chiudi" if tenute >= p["tenuta"] else None
        s = _segnale_base(B, p)
        if s is None:
            return None
        if modo == "variante" and not _condizione(ctx, B, p):
            return None
        if modo == "casuale" and (B.n - 1) not in ingressi:
            return None
        return s

    return strategia


def crea_variante(ctx, p):
    return lambda: _strategia(ctx, p, "variante")


def crea_a(ctx, p):
    return lambda: _strategia(ctx, p, "a")


def crea_casuale(ctx, p):
    return lambda ingressi: _strategia(ctx, p, "casuale", frozenset(ingressi))


def crea_segnale(ctx, p):
    def crea():
        B = _Barre(p["atr"])

        def segnale(storia):
            B.aggiorna(storia)
            return _segnale_base(B, p)

        return segnale

    return crea
