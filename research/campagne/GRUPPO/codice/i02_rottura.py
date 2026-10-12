"""Idea I-02, rottura dell'intervallo di prezzo (ipotesi.md): una regola per tutte le monete del gruppo.

Ingresso (variante), alla chiusura della barra k: long se la chiusura di k e' sopra il massimo delle chiusure
delle ``finestra`` barre prima di k; short se e' sotto il minimo.
Uscita (uguale per variante, (a), casuale): stop a ``stop_atr`` ATR di Wilder (``atr`` barre) dalla chiusura
della barra del segnale, nessun target, chiusura all'apertura dopo ``tenuta`` barre tenute.
Contratto: docstring di research/src/gruppo.py.
"""
from bisect import bisect_left

from research.src.motore import Segnale


class _Barre:
    """Le barre chiuse ricevute fin qui, con l'ATR di Wilder aggiornato barra per barra (niente sguardo avanti)."""

    def __init__(self, periodo_atr):
        self.n = 0
        self.ts, self.c, self.h, self.l = [], [], [], []
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
            if k < self._p:
                self._somma += tr
                self.atr.append(self._somma / self._p if k == self._p - 1 else None)
            else:
                self.atr.append((self.atr[k - 1] * (self._p - 1) + tr) / self._p)
        self.n = n


def _riscaldamento(p):
    return max(p["atr"] - 1, p["finestra"])


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
    prima = B.c[k - p["finestra"]:k]
    return B.c[k] > max(prima) if p["direzione"] == "long" else B.c[k] < min(prima)


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
