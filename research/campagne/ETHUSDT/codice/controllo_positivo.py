"""Controllo positivo degli strumenti (lezioni/metodo.md): una strategia che BARA di proposito.

Lookahead dichiarato: alla chiusura della barra i la strategia guarda la barra i+1
(che non e' ancora chiusa) leggendola dalla serie completa, ed entra long solo se
quella barra salira' di oltre l'1% dall'apertura alla chiusura. Esce con "chiudi" alla
chiusura della barra d'ingresso (cioe' all'apertura della barra dopo, quasi alla
chiusura della barra che ha "visto"). Stop a 2 ATR(14) sotto la chiusura del segnale.

Deve battere nettamente il caso e crollare con il ritardo di una barra: se non lo fa,
gli strumenti non vedono un vantaggio che c'e' per costruzione, e nessun risultato
della campagna vale. Non e' una variante: non consuma budget.
"""

from comune import Variante
from indicatori import ATR
from research.src.motore import Segnale


class Barante(Variante):
    direzione = "long"

    def __init__(self, serie, **p):
        super().__init__(serie, **p)
        self.atr = ATR(14)
        self.indice = {c.ts: k for k, c in enumerate(serie.last)}

    def aggiorna(self, barra, i):
        self.atr.aggiorna(barra.high, barra.low, barra.close)

    def pronta(self):
        return self.atr.valore is not None

    def calcola_segnale(self, storia):
        c = storia[-1].close
        return Segnale("long", c - 2.0 * self.atr.valore)

    def condizione(self, storia):
        k = self.indice[storia[-1].ts] + 1
        if k >= len(self.serie.last):
            return False
        dopo = self.serie.last[k]  # BARA: la barra successiva
        return dopo.close / dopo.open - 1.0 > 0.01

    def esci(self, storia, pos):
        return self.barre_in_posizione(storia, pos) >= 1


VARIANTI = {
    "ETHUSDT-C01": (Barante, {}, "4h"),
}
