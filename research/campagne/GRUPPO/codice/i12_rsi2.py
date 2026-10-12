"""Idea I-12, ritracciamento breve dentro il trend lungo (ipotesi.md): una regola per tutte le monete del gruppo.

RSI di Wilder su ``periodo_rsi`` barre; media semplice delle chiusure su ``media_lunga`` e su ``media_corta`` barre.
Ingresso (variante), alla chiusura della barra k: long se chiusura > media lunga e RSI < ``rsi_soglia``; short se
chiusura < media lunga e RSI > 100 - ``rsi_soglia``.
Uscita (uguale per variante, (a), casuale): stop a ``stop_atr`` ATR di Wilder dalla chiusura del segnale, nessun
target; chiusura all'apertura della barra dopo la prima chiusura oltre la media corta (sopra per il long, sotto
per lo short).
Contratto: docstring di research/src/gruppo.py.
"""
from research.src.motore import Segnale


class _Barre:
    """Barre chiuse, ATR e RSI di Wilder, medie semplici delle chiusure, barra per barra (niente sguardo avanti)."""

    def __init__(self, p):
        self.n = 0
        self.c = []
        self.atr, self.rsi = [], []
        self._p = p
        self._somma_tr = 0.0
        self._su = self._giu = 0.0
        self._somme = {}

    def media(self, k, q):
        if k < q - 1:
            return None
        return sum(self.c[k - q + 1:k + 1]) / q

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
            self.c.append(b.close)
            pa = p["atr"]
            if k < pa:
                self._somma_tr += tr
                self.atr.append(self._somma_tr / pa if k == pa - 1 else None)
            else:
                self.atr.append((self.atr[k - 1] * (pa - 1) + tr) / pa)
            q = p["periodo_rsi"]
            if k == 0:
                self.rsi.append(None)
                continue
            d = self.c[k] - self.c[k - 1]
            su, giu = max(d, 0.0), max(-d, 0.0)
            if k <= q:
                self._su += su / q
                self._giu += giu / q
                pronto = k == q
            else:
                self._su = (self._su * (q - 1) + su) / q
                self._giu = (self._giu * (q - 1) + giu) / q
                pronto = True
            if not pronto:
                self.rsi.append(None)
            elif self._giu == 0:
                self.rsi.append(100.0)
            else:
                self.rsi.append(100.0 - 100.0 / (1.0 + self._su / self._giu))
        self.n = n


def _riscaldamento(p):
    return max(p["atr"] - 1, p["periodo_rsi"], p["media_lunga"] - 1, p["media_corta"] - 1)


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
    lunga = B.media(k, p["media_lunga"])
    if p["direzione"] == "long":
        return B.c[k] > lunga and B.rsi[k] < p["rsi_soglia"]
    return B.c[k] < lunga and B.rsi[k] > 100 - p["rsi_soglia"]


def _esce(B, p):
    k = B.n - 1
    corta = B.media(k, p["media_corta"])
    if corta is None:
        return False
    return B.c[k] > corta if p["direzione"] == "long" else B.c[k] < corta


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
