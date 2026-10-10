"""Idea I-19, inversione del rendimento proprio della moneta, al netto di BTC (ipotesi.md): una regola per tutte.

Coppie di rendimenti di una barra (moneta, BTCUSDT) sulle barre contigue in cui BTC ha la barra che chiude nello
stesso istante. Sulle ``finestra_beta`` coppie che finiscono alla barra k - ``orizzonte`` (quindi PRIMA del
movimento che si giudica): alfa e beta dei minimi quadrati, deviazione standard (ddof 2) dei residui s_e.
Residuo delle ultime ``orizzonte`` barre fino a k: somma di (r - alfa - beta x r_btc); z = residuo / (s_e x
radice(orizzonte)). Servono tutte le coppie: altrimenti nessun segnale.
Ingresso (variante): long se z < -``soglia_z`` (la moneta e' scesa piu' di quanto spiega BTC); short se z > soglia.
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
    """Le chiusure delle barre chiuse di BTCUSDT lette dal contesto, per istante di chiusura."""

    def __init__(self, ctx):
        self.ctx = ctx
        self.n = 0
        self.chiusura = {}

    def aggiorna(self, adesso):
        vista = self.ctx.btc_chiuse_entro(adesso)
        for i in range(self.n, len(vista)):
            self.chiusura[vista[i].close_ts] = vista[i].close
        self.n = len(vista)


def _riscaldamento(p):
    return max(p["atr"] - 1, p["orizzonte"] + p["finestra_beta"])


def _segnale_base(B, p):
    k = B.n - 1
    if k < _riscaldamento(p) or B.atr[k] is None:
        return None
    distanza = p["stop_atr"] * B.atr[k]
    if p["direzione"] == "long":
        return Segnale("long", B.c[k] - distanza, None)
    return Segnale("short", B.c[k] + distanza, None)


def _coppia(B, T, i, ms):
    """(r della moneta, r di BTC) della barra i, o None se manca qualcosa."""
    if i < 1 or B.cts[i] - B.cts[i - 1] != ms:
        return None
    b1, b0 = T.chiusura.get(B.cts[i]), T.chiusura.get(B.cts[i] - ms)
    if b1 is None or b0 is None:
        return None
    return B.c[i] / B.c[i - 1] - 1.0, b1 / b0 - 1.0


def _z(B, T, p, ms):
    k = B.n - 1
    h, f = p["orizzonte"], p["finestra_beta"]
    if k < h + f:
        return None
    T.aggiorna(B.cts[k])
    coppie = []
    for i in range(k - h - f + 1, k + 1):
        c = _coppia(B, T, i, ms)
        if c is None:
            return None
        coppie.append(c)
    stima, recenti = coppie[:f], coppie[f:]
    mx = sum(b for _, b in stima) / f
    my = sum(a for a, _ in stima) / f
    sxx = sum((b - mx) ** 2 for _, b in stima)
    if sxx <= 0:
        return None
    beta = sum((b - mx) * (a - my) for a, b in stima) / sxx
    alfa = my - beta * mx
    se = math.sqrt(sum((a - alfa - beta * b) ** 2 for a, b in stima) / (f - 2))
    if se <= 0:
        return None
    residuo = sum(a - alfa - beta * b for a, b in recenti)
    return residuo / (se * math.sqrt(h))


def _condizione(B, T, p, ms):
    z = _z(B, T, p, ms)
    if z is None:
        return False
    return z < -p["soglia_z"] if p["direzione"] == "long" else z > p["soglia_z"]


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
        if modo == "variante" and not _condizione(B, T, p, ms):
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
