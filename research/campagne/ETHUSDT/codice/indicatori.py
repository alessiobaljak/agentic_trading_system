"""Indicatori incrementali per le strategie della campagna ETHUSDT.

Ogni indicatore riceve UNA barra chiusa alla volta (``aggiorna``) e conserva solo
cio' che serve: non vede mai barre future, per costruzione. ``valore`` e' None
finche' l'indicatore non e' caldo (riscaldamento).
"""

from collections import deque
from typing import Deque, Optional


class Media:
    """Media semplice degli ultimi ``n`` valori."""

    def __init__(self, n: int) -> None:
        self.n = int(n)
        self.finestra: Deque[float] = deque()
        self.somma = 0.0

    def aggiorna(self, x: float) -> None:
        self.finestra.append(x)
        self.somma += x
        if len(self.finestra) > self.n:
            self.somma -= self.finestra.popleft()

    @property
    def valore(self) -> Optional[float]:
        return self.somma / self.n if len(self.finestra) == self.n else None


class MediaEsponenziale:
    """Media esponenziale con alfa = 2 / (n + 1), inizializzata con la media dei primi n valori."""

    def __init__(self, n: int) -> None:
        self.n = int(n)
        self.alfa = 2.0 / (self.n + 1)
        self.primi = []
        self._valore: Optional[float] = None

    def aggiorna(self, x: float) -> None:
        if self._valore is None:
            self.primi.append(x)
            if len(self.primi) == self.n:
                self._valore = sum(self.primi) / self.n
            return
        self._valore += self.alfa * (x - self._valore)

    @property
    def valore(self) -> Optional[float]:
        return self._valore


class ATR:
    """Average true range alla Wilder (n barre), sulle barre chiuse."""

    def __init__(self, n: int) -> None:
        self.n = int(n)
        self.close_prec: Optional[float] = None
        self.primi = []
        self._valore: Optional[float] = None

    def aggiorna(self, high: float, low: float, close: float) -> None:
        if self.close_prec is None:
            tr = high - low
        else:
            tr = max(high - low, abs(high - self.close_prec), abs(low - self.close_prec))
        self.close_prec = close
        if self._valore is None:
            self.primi.append(tr)
            if len(self.primi) == self.n:
                self._valore = sum(self.primi) / self.n
            return
        self._valore = (self._valore * (self.n - 1) + tr) / self.n

    @property
    def valore(self) -> Optional[float]:
        return self._valore


class RSI:
    """Relative strength index alla Wilder su ``n`` barre."""

    def __init__(self, n: int) -> None:
        self.n = int(n)
        self.prec: Optional[float] = None
        self.su = []
        self.giu = []
        self.media_su: Optional[float] = None
        self.media_giu: Optional[float] = None

    def aggiorna(self, close: float) -> None:
        if self.prec is None:
            self.prec = close
            return
        d = close - self.prec
        self.prec = close
        s, g = max(d, 0.0), max(-d, 0.0)
        if self.media_su is None:
            self.su.append(s)
            self.giu.append(g)
            if len(self.su) == self.n:
                self.media_su = sum(self.su) / self.n
                self.media_giu = sum(self.giu) / self.n
            return
        self.media_su = (self.media_su * (self.n - 1) + s) / self.n
        self.media_giu = (self.media_giu * (self.n - 1) + g) / self.n

    @property
    def valore(self) -> Optional[float]:
        if self.media_su is None:
            return None
        if self.media_giu == 0:
            return 100.0
        rs = self.media_su / self.media_giu
        return 100.0 - 100.0 / (1.0 + rs)


class Estremo:
    """Massimo (o minimo) degli ultimi ``n`` valori, con una coda monotona."""

    def __init__(self, n: int, massimo: bool = True) -> None:
        self.n = int(n)
        self.massimo = massimo
        self.coda: Deque = deque()  # (indice, valore)
        self.i = -1

    def aggiorna(self, x: float) -> None:
        self.i += 1
        if self.massimo:
            while self.coda and self.coda[-1][1] <= x:
                self.coda.pop()
        else:
            while self.coda and self.coda[-1][1] >= x:
                self.coda.pop()
        self.coda.append((self.i, x))
        while self.coda[0][0] <= self.i - self.n:
            self.coda.popleft()

    @property
    def valore(self) -> Optional[float]:
        return self.coda[0][1] if self.i + 1 >= self.n else None


class Ritardo:
    """Il valore di ``n`` barre fa (n=1: la barra prima dell'ultima aggiornata)."""

    def __init__(self, n: int) -> None:
        self.n = int(n)
        self.finestra: Deque[float] = deque(maxlen=self.n + 1)

    def aggiorna(self, x: float) -> None:
        self.finestra.append(x)

    @property
    def valore(self) -> Optional[float]:
        return self.finestra[0] if len(self.finestra) == self.n + 1 else None


class DeviazioneStandard:
    """Deviazione standard (ddof=0) degli ultimi ``n`` valori."""

    def __init__(self, n: int) -> None:
        self.n = int(n)
        self.finestra: Deque[float] = deque()
        self.s = 0.0
        self.s2 = 0.0

    def aggiorna(self, x: float) -> None:
        self.finestra.append(x)
        self.s += x
        self.s2 += x * x
        if len(self.finestra) > self.n:
            v = self.finestra.popleft()
            self.s -= v
            self.s2 -= v * v

    @property
    def valore(self) -> Optional[float]:
        if len(self.finestra) < self.n:
            return None
        m = self.s / self.n
        return max(0.0, self.s2 / self.n - m * m) ** 0.5
