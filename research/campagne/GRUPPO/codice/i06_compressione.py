"""Idea I-06, rottura dopo una compressione della volatilita' (ipotesi.md): una regola per tutte le monete.

Bande di Bollinger su ``periodo_bb`` chiusure: media semplice M, deviazione standard di popolazione S, bande
M +/- ``k_bb`` x S, larghezza W = 2 x k_bb x S / M. La barra j e' «compressa» se W_j e' il minimo di W sulle
``finestra_compressione`` barre fino a j compresa.
Ingresso (variante), alla chiusura della barra k: c'e' una barra compressa fra k - ``recenti`` e k - 1, e la
chiusura di k e' sopra la banda alta (long) o sotto la banda bassa (short).
Uscita (uguale per variante, (a), casuale): stop a ``stop_atr`` ATR di Wilder dalla chiusura del segnale, nessun
target; chiusura all'apertura della barra dopo la prima chiusura che torna dall'altra parte della media M
(sotto M per il long, sopra M per lo short).
Contratto: docstring di research/src/gruppo.py.
"""
import math

from research.src.motore import Segnale


class _Barre:
    """Barre chiuse, ATR di Wilder, media e deviazione delle chiusure e larghezza delle bande, barra per barra."""

    def __init__(self, p):
        self.n = 0
        self.ts, self.c = [], []
        self.atr, self.media, self.dev, self.larghezza, self.compressa = [], [], [], [], []
        self._p = p
        self._somma = 0.0

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
            pa = p["atr"]
            if k < pa:
                self._somma += tr
                self.atr.append(self._somma / pa if k == pa - 1 else None)
            else:
                self.atr.append((self.atr[k - 1] * (pa - 1) + tr) / pa)
            q = p["periodo_bb"]
            if k >= q - 1:
                finestra = self.c[k - q + 1:k + 1]
                m = sum(finestra) / q
                s = math.sqrt(sum((x - m) ** 2 for x in finestra) / q)
                self.media.append(m)
                self.dev.append(s)
                self.larghezza.append(2 * p["k_bb"] * s / m)
            else:
                self.media.append(None)
                self.dev.append(None)
                self.larghezza.append(None)
            f = p["finestra_compressione"]
            if k >= q - 1 + f - 1:
                ultime = self.larghezza[k - f + 1:k + 1]
                self.compressa.append(self.larghezza[k] <= min(ultime))
            else:
                self.compressa.append(False)
        self.n = n


def _riscaldamento(p):
    return max(p["atr"] - 1, p["periodo_bb"] - 1 + p["finestra_compressione"] - 1 + p["recenti"])


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
    if not any(B.compressa[k - p["recenti"]:k]):
        return False
    banda = p["k_bb"] * B.dev[k]
    if p["direzione"] == "long":
        return B.c[k] > B.media[k] + banda
    return B.c[k] < B.media[k] - banda


def _esce(B, p):
    k = B.n - 1
    if B.media[k] is None:
        return False
    return B.c[k] < B.media[k] if p["direzione"] == "long" else B.c[k] > B.media[k]


def _strategia(p, modo, ingressi=None):
    B = _Barre(p)

    def strategia(storia, posizione):
        B.aggiorna(storia)
        if posizione is not None:
            return "chiudi" if _esce(B, p) else None
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
