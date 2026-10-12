"""Idea I-10, vicinanza al massimo dell'ultimo anno (ipotesi.md): una regola per tutte le monete del gruppo.

Ingresso (variante), alla chiusura della barra k: long se la chiusura di k e' almeno ``quota`` x il massimo dei
massimi delle ``finestra`` barre fino a k compresa.
Uscita (uguale per variante, (a), casuale): stop a ``stop_atr`` ATR di Wilder dalla chiusura del segnale, nessun
target, chiusura all'apertura dopo ``tenuta`` barre tenute.
Contratto: docstring di research/src/gruppo.py.
"""
from bisect import bisect_left
from collections import deque

from research.src.motore import Segnale


class _Barre:
    """Barre chiuse, ATR di Wilder e massimo mobile dei massimi (coda monotona), barra per barra."""

    def __init__(self, p):
        self.n = 0
        self.ts, self.c, self.h = [], [], []
        self.atr, self.massimo = [], []
        self._p = p
        self._somma = 0.0
        self._coda = deque()

    def aggiorna(self, storia):
        p = self._p
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
            self.c.append(b.close)
            self.h.append(b.high)
            pa = p["atr"]
            if k < pa:
                self._somma += tr
                self.atr.append(self._somma / pa if k == pa - 1 else None)
            else:
                self.atr.append((self.atr[k - 1] * (pa - 1) + tr) / pa)
            f = p["finestra"]
            while self._coda and self.h[self._coda[-1]] <= b.high:
                self._coda.pop()
            self._coda.append(k)
            while self._coda[0] <= k - f:
                self._coda.popleft()
            self.massimo.append(self.h[self._coda[0]] if k >= f - 1 else None)
        self.n = n


def _riscaldamento(p):
    return max(p["atr"] - 1, p["finestra"] - 1)


def _segnale_base(B, p):
    k = B.n - 1
    if k < _riscaldamento(p) or B.atr[k] is None:
        return None
    distanza = p["stop_atr"] * B.atr[k]
    if p["direzione"] == "long":
        return Segnale("long", B.c[k] - distanza, None)
    return Segnale("short", B.c[k] + distanza, None)


def _condizione(B, p):
    k = B.n - 1
    return B.c[k] >= p["quota"] * B.massimo[k]


def _strategia(p, modo, ingressi=None):
    B = _Barre(p)

    def strategia(storia, posizione):
        B.aggiorna(storia)
        if posizione is not None:
            tenute = B.n - bisect_left(B.ts, posizione.ts_entrata)
            return "chiudi" if tenute >= p["tenuta"] else None
        s = _segnale_base(B, p)
        if s is None:
            return None
        if modo == "variante" and not _condizione(B, p):
            return None
        if modo == "casuale" and (B.n - 1) not in ingressi:
            return None
        return s

    return strategia


def crea_variante(ctx, p):
    return lambda: _strategia(p, "variante")


def crea_a(ctx, p):
    return lambda: _strategia(p, "a")


def crea_casuale(ctx, p):
    return lambda ingressi: _strategia(p, "casuale", frozenset(ingressi))


def crea_segnale(ctx, p):
    def crea():
        B = _Barre(p)

        def segnale(storia):
            B.aggiorna(storia)
            return _segnale_base(B, p)

        return segnale

    return crea
