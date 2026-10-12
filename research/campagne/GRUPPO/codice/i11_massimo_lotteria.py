"""Idea I-11, moneta «lotteria» dopo un rialzo estremo di un giorno (ipotesi.md): una regola per tutte le monete.

r_i = chiusura_i / chiusura_{i-1} - 1. MAX = il rendimento piu' alto delle ``finestra`` barre fino a k compresa;
riferimento = la mediana di |r_i| sulle ``finestra_rif`` barre fino a k compresa.
Ingresso (variante), alla chiusura della barra k: short se MAX > ``multiplo`` x riferimento.
Uscita (uguale per variante, (a), casuale): stop a ``stop_atr`` ATR di Wilder dalla chiusura del segnale, nessun
target, chiusura all'apertura dopo ``tenuta`` barre tenute.
Contratto: docstring di research/src/gruppo.py.
"""
from bisect import bisect_left

from research.src.motore import Segnale


class _Barre:
    """Le barre chiuse ricevute fin qui, con l'ATR di Wilder e i rendimenti, barra per barra."""

    def __init__(self, periodo_atr):
        self.n = 0
        self.ts, self.c, self.r = [], [], []
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
                self.r.append(None)
            else:
                pc = self.c[k - 1]
                tr = max(b.high - b.low, abs(b.high - pc), abs(b.low - pc))
                self.r.append(b.close / pc - 1.0)
            self.ts.append(b.ts)
            self.c.append(b.close)
            if k < self._p:
                self._somma += tr
                self.atr.append(self._somma / self._p if k == self._p - 1 else None)
            else:
                self.atr.append((self.atr[k - 1] * (self._p - 1) + tr) / self._p)
        self.n = n


def _riscaldamento(p):
    return max(p["atr"] - 1, p["finestra"], p["finestra_rif"])


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
    massimo = max(B.r[k - p["finestra"] + 1:k + 1])
    assoluti = sorted(abs(x) for x in B.r[k - p["finestra_rif"] + 1:k + 1])
    m = len(assoluti)
    mediana = assoluti[m // 2] if m % 2 else (assoluti[m // 2 - 1] + assoluti[m // 2]) / 2
    return mediana > 0 and massimo > p["multiplo"] * mediana


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
