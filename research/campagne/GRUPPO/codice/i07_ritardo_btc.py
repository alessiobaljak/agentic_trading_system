"""Idea I-07, la moneta che resta indietro rispetto a un movimento forte di BTC (ipotesi.md): una regola per tutte.

Alla chiusura della barra k della moneta: r_btc = rendimento della barra di BTCUSDT che chiude nello stesso istante
(serve anche la barra BTC precedente, contigua); dev_btc = deviazione standard (ddof 1) dei rendimenti delle
``finestra`` barre BTC prima di quella; r = rendimento della barra k della moneta (barra precedente contigua).
Ingresso (variante): long se r_btc > ``soglia_dev`` x dev_btc e r < ``frazione`` x r_btc (la moneta non ha seguito);
short se r_btc < -soglia x dev_btc e r > frazione x r_btc.
Uscita (uguale per variante, (a), casuale): stop a ``stop_atr`` ATR di Wilder dalla chiusura del segnale, nessun
target, chiusura all'apertura dopo ``tenuta`` barre tenute.
Contratto: docstring di research/src/gruppo.py. BTCUSDT si legge solo con ctx.btc_chiuse_entro (barre chiuse).
"""
import math
from bisect import bisect_left

from research.src.motore import Segnale


class _Barre:
    """Le barre chiuse ricevute fin qui, con l'ATR di Wilder aggiornato barra per barra (niente sguardo avanti)."""

    def __init__(self, periodo_atr):
        self.n = 0
        self.ts, self.cts, self.c = [], [], []
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
            if k < self._p:
                self._somma += tr
                self.atr.append(self._somma / self._p if k == self._p - 1 else None)
            else:
                self.atr.append((self.atr[k - 1] * (self._p - 1) + tr) / self._p)
        self.n = n


class _Btc:
    """Le barre chiuse di BTCUSDT lette dal contesto, in ordine, con indice per istante di chiusura."""

    def __init__(self, ctx):
        self.ctx = ctx
        self.cts, self.c = [], []
        self.indice = {}

    def aggiorna(self, adesso):
        vista = self.ctx.btc_chiuse_entro(adesso)
        for i in range(len(self.c), len(vista)):
            b = vista[i]
            self.indice[b.close_ts] = len(self.c)
            self.cts.append(b.close_ts)
            self.c.append(b.close)


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


def _condizione(ctx, B, T, p, ms):
    k = B.n - 1
    if k < 1 or B.cts[k] - B.cts[k - 1] != ms:
        return False
    T.aggiorna(B.cts[k])
    j = T.indice.get(B.cts[k])
    f = p["finestra"]
    if j is None or j < f + 1:
        return False
    if any(T.cts[i] - T.cts[i - 1] != ms for i in range(j - f, j + 1)):
        return False
    rend = [T.c[i] / T.c[i - 1] - 1.0 for i in range(j - f, j)]
    media = sum(rend) / f
    dev = math.sqrt(sum((x - media) ** 2 for x in rend) / (f - 1))
    r_btc = T.c[j] / T.c[j - 1] - 1.0
    r = B.c[k] / B.c[k - 1] - 1.0
    if p["direzione"] == "long":
        return r_btc > p["soglia_dev"] * dev and r < p["frazione"] * r_btc
    return r_btc < -p["soglia_dev"] * dev and r > p["frazione"] * r_btc


def _strategia(ctx, p, modo, ingressi=None):
    B = _Barre(p["atr"])
    T = _Btc(ctx)
    ms = ctx.ms_per_barra

    def strategia(storia, posizione):
        B.aggiorna(storia)
        if posizione is not None:
            tenute = B.n - bisect_left(B.ts, posizione.ts_entrata)
            return "chiudi" if tenute >= p["tenuta"] else None
        s = _segnale_base(B, p)
        if s is None:
            return None
        if modo == "variante" and not _condizione(ctx, B, T, p, ms):
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
