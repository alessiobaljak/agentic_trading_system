"""Idea I-03, continuazione dopo un rendimento anomalo di una barra (ipotesi.md): una regola per tutte le monete.

Rendimento della barra k: r_k = chiusura_k / chiusura_{k-1} - 1. Anomalo in su se r_k > media + ``soglia_dev`` x
deviazione standard (ddof 1) dei ``finestra`` rendimenti PRIMA di k; anomalo in giu' se r_k < media - soglia x dev.
Ingresso (variante): long dopo un anomalo in su, short dopo un anomalo in giu' (stessa direzione: continuazione).
Uscita (uguale per variante, (a), casuale): stop a ``stop_atr`` ATR di Wilder dalla chiusura del segnale, nessun
target, chiusura all'apertura dopo ``tenuta`` barre tenute.
Contratto: docstring di research/src/gruppo.py.
"""
import math
from bisect import bisect_left

from research.src.motore import Segnale


class _Barre:
    """Le barre chiuse ricevute fin qui, con l'ATR di Wilder aggiornato barra per barra (niente sguardo avanti)."""

    def __init__(self, periodo_atr):
        self.n = 0
        self.ts, self.c, self.h, self.l, self.v = [], [], [], [], []
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
            self.c.append(b.close)
            self.h.append(b.high)
            self.l.append(b.low)
            self.v.append(b.volume)
            if k < self._p:
                self._somma += tr
                self.atr.append(self._somma / self._p if k == self._p - 1 else None)
            else:
                self.atr.append((self.atr[k - 1] * (self._p - 1) + tr) / self._p)
        self.n = n


def _riscaldamento(p):
    # servono finestra rendimenti prima di k (cioe' chiusure da k - finestra - 1) e l'ATR
    return max(p["atr"] - 1, p["finestra"] + 1)


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
    f = p["finestra"]
    rend = [B.c[i] / B.c[i - 1] - 1.0 for i in range(k - f, k)]
    media = sum(rend) / f
    dev = math.sqrt(sum((x - media) ** 2 for x in rend) / (f - 1))
    r = B.c[k] / B.c[k - 1] - 1.0
    if p["direzione"] == "long":
        return r > media + p["soglia_dev"] * dev
    return r < media - p["soglia_dev"] * dev


def _strategia(p, modo, ingressi=None):
    B = _Barre(p["atr"])

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
        B = _Barre(p["atr"])

        def segnale(storia):
            B.aggiorna(storia)
            return _segnale_base(B, p)

        return segnale

    return crea
