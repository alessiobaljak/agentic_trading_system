"""Le varianti delle idee di ipotesi.md (I-01 ... I-14), una classe per idea.

Ogni classe implementa le regole ESATTE scritte in ipotesi.md, con le convenzioni comuni
del file: segnale alla chiusura, ingresso all'apertura dopo, stop dalla chiusura del
segnale, "esce dopo N barre" = "chiudi" alla chiusura della N-esima barra in posizione.
``VARIANTI`` mappa il nome della variante in ipotesi.md su (classe, parametri, timeframe).
"""

import math
from bisect import bisect_right
from collections import deque
from datetime import datetime, timezone

from comune import Variante
from indicatori import ATR, Estremo, Media, RSI, Ritardo
from research.src.motore import Segnale

GIORNO_MS = 86_400_000
TETTO_STOP = 0.06


def segnale_da_distanza(direzione, close, distanza):
    """Segnale con stop a ``distanza`` dalla chiusura, al massimo il 6% (tetto del bot)."""
    d = min(distanza, TETTO_STOP * close)
    if direzione == "long":
        return Segnale("long", close - d)
    return Segnale("short", close + d)


def segnale_da_livello(direzione, close, livello):
    """Segnale con stop a un livello di prezzo, con distanza al massimo il 6%."""
    if direzione == "long":
        return Segnale("long", max(livello, close * (1 - TETTO_STOP)))
    return Segnale("short", min(livello, close * (1 + TETTO_STOP)))


# --------------------------------------------------------------------------- #
# I-01 momentum di una settimana (1d)
# --------------------------------------------------------------------------- #
class MomentumSettimana(Variante):
    def __init__(self, serie, direzione, lookback=7, uscita=7, stop_pct=0.06):
        super().__init__(serie)
        self.direzione = direzione
        self.uscita = uscita
        self.stop_pct = stop_pct
        self.rit = Ritardo(lookback)

    def aggiorna(self, barra, i):
        self.rit.aggiorna(barra.close)

    def pronta(self):
        return self.rit.valore is not None

    def calcola_segnale(self, storia):
        c = storia[-1].close
        return segnale_da_distanza(self.direzione, c, self.stop_pct * c)

    def condizione(self, storia):
        r = storia[-1].close / self.rit.valore - 1.0
        return r > 0 if self.direzione == "long" else r < 0

    def esci(self, storia, pos):
        return self.barre_in_posizione(storia, pos) >= self.uscita


# --------------------------------------------------------------------------- #
# I-02 rottura del canale di Donchian (4h)
# --------------------------------------------------------------------------- #
class Donchian(Variante):
    def __init__(self, serie, direzione, n_ingresso=20, n_uscita=10, k_stop=2.0, n_atr=20):
        super().__init__(serie)
        self.direzione = direzione
        self.k = k_stop
        self.max_in = Estremo(n_ingresso, massimo=True)
        self.min_in = Estremo(n_ingresso, massimo=False)
        self.max_out = Estremo(n_uscita, massimo=True)
        self.min_out = Estremo(n_uscita, massimo=False)
        self.atr = ATR(n_atr)
        self.prec = {}

    def aggiorna(self, barra, i):
        # gli estremi delle barre PRECEDENTI (esclusa la corrente)
        self.prec = {"max_in": self.max_in.valore, "min_in": self.min_in.valore,
                     "max_out": self.max_out.valore, "min_out": self.min_out.valore}
        self.max_in.aggiorna(barra.high)
        self.min_in.aggiorna(barra.low)
        self.max_out.aggiorna(barra.high)
        self.min_out.aggiorna(barra.low)
        self.atr.aggiorna(barra.high, barra.low, barra.close)

    def pronta(self):
        return self.atr.valore is not None and all(v is not None for v in self.prec.values()) and bool(self.prec)

    def calcola_segnale(self, storia):
        return segnale_da_distanza(self.direzione, storia[-1].close, self.k * self.atr.valore)

    def condizione(self, storia):
        c = storia[-1].close
        return c > self.prec["max_in"] if self.direzione == "long" else c < self.prec["min_in"]

    def esci(self, storia, pos):
        c = storia[-1].close
        if self.prec.get("min_out") is None:
            return False
        return c < self.prec["min_out"] if self.direzione == "long" else c > self.prec["max_out"]


# --------------------------------------------------------------------------- #
# I-03 sopra / sotto la media di 50 giorni (1d)
# --------------------------------------------------------------------------- #
class SopraMedia(Variante):
    def __init__(self, serie, direzione, n=50, stop_pct=0.06):
        super().__init__(serie)
        self.direzione = direzione
        self.stop_pct = stop_pct
        self.media = Media(n)

    def aggiorna(self, barra, i):
        self.media.aggiorna(barra.close)

    def pronta(self):
        return self.media.valore is not None

    def calcola_segnale(self, storia):
        c = storia[-1].close
        return segnale_da_distanza(self.direzione, c, self.stop_pct * c)

    def condizione(self, storia):
        c = storia[-1].close
        return c > self.media.valore if self.direzione == "long" else c < self.media.valore

    def esci(self, storia, pos):
        if self.media.valore is None:
            return False
        c = storia[-1].close
        return c < self.media.valore if self.direzione == "long" else c > self.media.valore


# --------------------------------------------------------------------------- #
# I-04 RSI a 2 barre con la media di 200 (4h)
# --------------------------------------------------------------------------- #
class RSI2(Variante):
    def __init__(self, serie, direzione, n_lunga=200, n_uscita=5, soglia=10.0, k_stop=3.0):
        super().__init__(serie)
        self.direzione = direzione
        self.soglia = soglia
        self.k = k_stop
        self.lunga = Media(n_lunga)
        self.corta = Media(n_uscita)
        self.rsi = RSI(2)
        self.atr = ATR(14)

    def aggiorna(self, barra, i):
        self.lunga.aggiorna(barra.close)
        self.corta.aggiorna(barra.close)
        self.rsi.aggiorna(barra.close)
        self.atr.aggiorna(barra.high, barra.low, barra.close)

    def pronta(self):
        return None not in (self.lunga.valore, self.corta.valore, self.rsi.valore, self.atr.valore)

    def calcola_segnale(self, storia):
        return segnale_da_distanza(self.direzione, storia[-1].close, self.k * self.atr.valore)

    def condizione(self, storia):
        c = storia[-1].close
        if self.direzione == "long":
            return c > self.lunga.valore and self.rsi.valore < self.soglia
        return c < self.lunga.valore and self.rsi.valore > 100.0 - self.soglia

    def esci(self, storia, pos):
        if self.corta.valore is None:
            return False
        c = storia[-1].close
        return c > self.corta.valore if self.direzione == "long" else c < self.corta.valore


# --------------------------------------------------------------------------- #
# I-05 barra piu' stretta delle ultime 7 (4h)
# --------------------------------------------------------------------------- #
class NR7(Variante):
    def __init__(self, serie, direzione, n=7, uscita=6):
        super().__init__(serie)
        self.direzione = direzione
        self.n = n
        self.uscita = uscita
        self.escursioni = deque(maxlen=n + 1)
        self.barre = deque(maxlen=2)

    def aggiorna(self, barra, i):
        self.escursioni.append(barra.high - barra.low)
        self.barre.append(barra)

    def pronta(self):
        return len(self.escursioni) == self.n + 1

    def _precedente_nr7(self):
        ultime = list(self.escursioni)[:-1]  # le n barre che finiscono con la precedente
        return ultime[-1] <= min(ultime)

    def calcola_segnale(self, storia):
        prec = self.barre[0]
        c = storia[-1].close
        return segnale_da_livello(self.direzione, c, prec.low if self.direzione == "long" else prec.high)

    def condizione(self, storia):
        if not self._precedente_nr7():
            return False
        prec = self.barre[0]
        c = storia[-1].close
        return c > prec.high if self.direzione == "long" else c < prec.low

    def esci(self, storia, pos):
        return self.barre_in_posizione(storia, pos) >= self.uscita


# --------------------------------------------------------------------------- #
# I-06 la prima mezz'ora prevede l'ultima (30m)
# --------------------------------------------------------------------------- #
class PrimaMezzora(Variante):
    def __init__(self, serie, direzione, k_stop=2.0):
        super().__init__(serie)
        self.direzione = direzione
        self.k = k_stop
        self.atr = ATR(14)
        self.giorno = None
        self.r_prima = None

    def aggiorna(self, barra, i):
        self.atr.aggiorna(barra.high, barra.low, barra.close)
        giorno = barra.ts // GIORNO_MS
        if barra.ts % GIORNO_MS == 0:
            self.giorno = giorno
            self.r_prima = barra.close / barra.open - 1.0
        elif giorno != self.giorno:
            # giorno senza la barra delle 00:00 (buco nei dati): nessun segnale quel giorno
            self.giorno = giorno
            self.r_prima = None

    def pronta(self):
        return self.atr.valore is not None

    def calcola_segnale(self, storia):
        return segnale_da_distanza(self.direzione, storia[-1].close, self.k * self.atr.valore)

    def condizione(self, storia):
        b = storia[-1]
        if b.ts % GIORNO_MS != 23 * 3_600_000 or self.r_prima is None:
            return False
        return self.r_prima > 0 if self.direzione == "long" else self.r_prima < 0

    def esci(self, storia, pos):
        return self.barre_in_posizione(storia, pos) >= 1


# --------------------------------------------------------------------------- #
# I-07 BTC si muove prima di ETH (1h)
# --------------------------------------------------------------------------- #
class RitardoBTC(Variante):
    def __init__(self, serie, direzione, soglia_btc=0.01, quota=0.5, uscita=2, k_stop=2.0):
        super().__init__(serie)
        self.direzione = direzione
        self.soglia = soglia_btc
        self.quota = quota
        self.uscita = uscita
        self.k = k_stop
        self.atr = ATR(14)

    def aggiorna(self, barra, i):
        self.atr.aggiorna(barra.high, barra.low, barra.close)

    def pronta(self):
        return self.atr.valore is not None

    def calcola_segnale(self, storia):
        return segnale_da_distanza(self.direzione, storia[-1].close, self.k * self.atr.valore)

    def condizione(self, storia):
        b = storia[-1]
        btc = self.serie.btc.get(b.ts)  # la barra di BTC chiusa nello stesso istante
        if btc is None:
            return False
        r_btc = btc.close / btc.open - 1.0
        r_eth = b.close / b.open - 1.0
        if self.direzione == "long":
            return r_btc > self.soglia and r_eth < self.quota * r_btc
        return r_btc < -self.soglia and r_eth > self.quota * r_btc

    def esci(self, storia, pos):
        return self.barre_in_posizione(storia, pos) >= self.uscita


# --------------------------------------------------------------------------- #
# I-08 funding alto / negativo (8h)
# --------------------------------------------------------------------------- #
class Funding(Variante):
    def __init__(self, serie, direzione, soglia=0.0005, uscita=9, k_stop=2.0):
        super().__init__(serie)
        self.direzione = direzione
        self.soglia = soglia
        self.uscita = uscita
        self.k = k_stop
        self.atr = ATR(14)
        self.ts_funding = [t for t, _ in serie.funding]
        self.tassi = [r for _, r in serie.funding]
        self.tasso = None

    def aggiorna(self, barra, i):
        self.atr.aggiorna(barra.high, barra.low, barra.close)
        k = bisect_right(self.ts_funding, barra.close_ts)  # settlement gia' avvenuti
        self.tasso = self.tassi[k - 1] if k > 0 else None

    def pronta(self):
        return self.atr.valore is not None and self.tasso is not None

    def calcola_segnale(self, storia):
        return segnale_da_distanza(self.direzione, storia[-1].close, self.k * self.atr.valore)

    def condizione(self, storia):
        if self.direzione == "short":
            return self.tasso >= self.soglia
        return self.tasso < 0

    def esci(self, storia, pos):
        return self.barre_in_posizione(storia, pos) >= self.uscita


# --------------------------------------------------------------------------- #
# I-09 il lunedi' (1d)
# --------------------------------------------------------------------------- #
class Lunedi(Variante):
    def __init__(self, serie, direzione="long", stop_pct=0.06):
        super().__init__(serie)
        self.direzione = direzione
        self.stop_pct = stop_pct

    def aggiorna(self, barra, i):
        pass

    def pronta(self):
        return True

    def calcola_segnale(self, storia):
        c = storia[-1].close
        return segnale_da_distanza(self.direzione, c, self.stop_pct * c)

    def condizione(self, storia):
        giorno = datetime.fromtimestamp(storia[-1].ts / 1000, tz=timezone.utc).weekday()
        return giorno == 6  # la barra chiusa e' la domenica: si entra il lunedi'

    def esci(self, storia, pos):
        return self.barre_in_posizione(storia, pos) >= 1


# --------------------------------------------------------------------------- #
# I-10 continuazione dopo un giorno anomalo (1d)
# --------------------------------------------------------------------------- #
class GiornoAnomalo(Variante):
    def __init__(self, serie, direzione, n=30, k=1.0, stop_pct=0.06):
        super().__init__(serie)
        self.direzione = direzione
        self.k = k
        self.stop_pct = stop_pct
        self.finestra = deque(maxlen=n)
        self.n = n
        self.statistiche = None
        self.r = None

    def aggiorna(self, barra, i):
        self.r = barra.close / barra.open - 1.0
        if len(self.finestra) == self.n:
            vals = list(self.finestra)
            media = sum(vals) / self.n
            sd = math.sqrt(sum((x - media) ** 2 for x in vals) / (self.n - 1))
            self.statistiche = (media, sd)
        self.finestra.append(self.r)

    def pronta(self):
        return self.statistiche is not None

    def calcola_segnale(self, storia):
        c = storia[-1].close
        return segnale_da_distanza(self.direzione, c, self.stop_pct * c)

    def condizione(self, storia):
        media, sd = self.statistiche
        if self.direzione == "long":
            return self.r > 0 and self.r > media + self.k * sd
        return self.r < 0 and self.r < media - self.k * sd

    def esci(self, storia, pos):
        return self.barre_in_posizione(storia, pos) >= 1


# --------------------------------------------------------------------------- #
# I-11 passaggio di un numero tondo (1h)
# --------------------------------------------------------------------------- #
def livello_tondo_in(a, b):
    """True se c'e' un livello tondo L con a < L <= b (multipli di 10 sotto 1000, di 100 da 1000)."""
    if b <= a:
        return False
    if a < 1000:
        primo = math.floor(a / 10.0) * 10.0 + 10.0
    else:
        primo = math.floor(a / 100.0) * 100.0 + 100.0
    return primo <= b


class NumeroTondo(Variante):
    def __init__(self, serie, direzione, uscita=4, k_stop=1.5):
        super().__init__(serie)
        self.direzione = direzione
        self.uscita = uscita
        self.k = k_stop
        self.atr = ATR(14)
        self.close_prec = None
        self.close_corr = None

    def aggiorna(self, barra, i):
        self.atr.aggiorna(barra.high, barra.low, barra.close)
        self.close_prec = self.close_corr
        self.close_corr = barra.close

    def pronta(self):
        return self.atr.valore is not None and self.close_prec is not None

    def calcola_segnale(self, storia):
        return segnale_da_distanza(self.direzione, storia[-1].close, self.k * self.atr.valore)

    def condizione(self, storia):
        if self.direzione == "long":
            return livello_tondo_in(self.close_prec, self.close_corr)
        return livello_tondo_in(self.close_corr, self.close_prec)

    def esci(self, storia, pos):
        return self.barre_in_posizione(storia, pos) >= self.uscita


# --------------------------------------------------------------------------- #
# I-12 volume insolito (1d)
# --------------------------------------------------------------------------- #
class VolumeInsolito(Variante):
    def __init__(self, serie, direzione, n=50, posti=5, uscita=10, stop_pct=0.06):
        super().__init__(serie)
        self.direzione = direzione
        self.n = n
        self.posti = posti
        self.uscita = uscita
        self.stop_pct = stop_pct
        self.finestra = deque(maxlen=n)

    def aggiorna(self, barra, i):
        self.finestra.append(barra.volume * barra.close)

    def pronta(self):
        return len(self.finestra) == self.n

    def calcola_segnale(self, storia):
        c = storia[-1].close
        return segnale_da_distanza(self.direzione, c, self.stop_pct * c)

    def condizione(self, storia):
        v = self.finestra[-1]
        if self.direzione == "long":
            return sum(1 for x in self.finestra if x > v) < self.posti
        return sum(1 for x in self.finestra if x < v) < self.posti

    def esci(self, storia, pos):
        return self.barre_in_posizione(storia, pos) >= self.uscita


# --------------------------------------------------------------------------- #
# I-13 vendite (acquisti) forzati e rimbalzo (1h)
# --------------------------------------------------------------------------- #
class VenditeForzate(Variante):
    def __init__(self, serie, direzione, n=24, k_corpo=2.0, k_volume=3.0, uscita=6, k_stop=0.5):
        super().__init__(serie)
        self.direzione = direzione
        self.k_corpo = k_corpo
        self.k_volume = k_volume
        self.uscita = uscita
        self.k_stop = k_stop
        self.atr = ATR(n)
        self.vol = Media(n)
        self.atr_prec = None
        self.vol_prec = None

    def aggiorna(self, barra, i):
        self.atr_prec = self.atr.valore
        self.vol_prec = self.vol.valore
        self.atr.aggiorna(barra.high, barra.low, barra.close)
        self.vol.aggiorna(barra.volume)

    def pronta(self):
        return self.atr_prec is not None and self.vol_prec is not None

    def calcola_segnale(self, storia):
        b = storia[-1]
        if self.direzione == "long":
            return segnale_da_livello("long", b.close, b.low - self.k_stop * self.atr_prec)
        return segnale_da_livello("short", b.close, b.high + self.k_stop * self.atr_prec)

    def condizione(self, storia):
        b = storia[-1]
        if b.volume <= self.k_volume * self.vol_prec:
            return False
        corpo = b.close - b.open
        return corpo < -self.k_corpo * self.atr_prec if self.direzione == "long" else corpo > self.k_corpo * self.atr_prec

    def esci(self, storia, pos):
        return self.barre_in_posizione(storia, pos) >= self.uscita


# --------------------------------------------------------------------------- #
# I-18 continuazione dopo una barra di vendite forzate (1h)
# --------------------------------------------------------------------------- #
class Cascata(VenditeForzate):
    """Stessa condizione di I-13a (caduta oltre 2 ATR con volume oltre 3 volte), ma short."""

    PARAMETRI_IN_BARRE = ("n", "uscita")

    def __init__(self, serie, direzione="short", n=24, k_corpo=2.0, k_volume=3.0, uscita=6, k_stop=0.5):
        super().__init__(serie, direzione, n=n, k_corpo=k_corpo, k_volume=k_volume, uscita=uscita, k_stop=k_stop)

    def calcola_segnale(self, storia):
        b = storia[-1]
        return segnale_da_livello("short", b.close, b.high + self.k_stop * self.atr_prec)

    def condizione(self, storia):
        b = storia[-1]
        if b.volume <= self.k_volume * self.vol_prec:
            return False
        return b.close - b.open < -self.k_corpo * self.atr_prec


# --------------------------------------------------------------------------- #
# I-14 rifiuto al massimo / minimo del giorno prima (1h)
# --------------------------------------------------------------------------- #
class GiornoPrima(Variante):
    #: parametri espressi in barre (si convertono nella verifica dei timeframe adiacenti)
    PARAMETRI_IN_BARRE = ("uscita", "n_atr")

    def __init__(self, serie, direzione, uscita=6, k_stop=0.25, n_atr=14):
        super().__init__(serie)
        self.direzione = direzione
        self.uscita = uscita
        self.k_stop = k_stop
        self.atr = ATR(n_atr)
        self.giorno = None
        self.max_oggi = None
        self.min_oggi = None
        self.max_ieri = None
        self.min_ieri = None

    def aggiorna(self, barra, i):
        self.atr.aggiorna(barra.high, barra.low, barra.close)
        giorno = barra.ts // GIORNO_MS
        if giorno != self.giorno:
            if self.giorno is not None and giorno == self.giorno + 1:
                self.max_ieri, self.min_ieri = self.max_oggi, self.min_oggi
            else:
                self.max_ieri = self.min_ieri = None  # primo giorno o giorno saltato (buco)
            self.giorno = giorno
            self.max_oggi, self.min_oggi = barra.high, barra.low
        else:
            self.max_oggi = max(self.max_oggi, barra.high)
            self.min_oggi = min(self.min_oggi, barra.low)

    def pronta(self):
        return self.atr.valore is not None and self.max_ieri is not None

    def calcola_segnale(self, storia):
        b = storia[-1]
        if self.direzione == "short":
            return segnale_da_livello("short", b.close, b.high + self.k_stop * self.atr.valore)
        return segnale_da_livello("long", b.close, b.low - self.k_stop * self.atr.valore)

    def condizione(self, storia):
        b = storia[-1]
        if self.direzione == "short":
            return b.high > self.max_ieri and b.close < self.max_ieri
        return b.low < self.min_ieri and b.close > self.min_ieri

    def esci(self, storia, pos):
        return self.barre_in_posizione(storia, pos) >= self.uscita


# --------------------------------------------------------------------------- #
# I-15 squilibrio degli ordini (1d)
# --------------------------------------------------------------------------- #
class Squilibrio(Variante):
    def __init__(self, serie, direzione, n=30, uscita=1, stop_pct=0.06):
        super().__init__(serie)
        self.direzione = direzione
        self.n = n
        self.uscita = uscita
        self.stop_pct = stop_pct
        self.quote = serie.taker
        self.finestra = deque(maxlen=n)
        self.media_prec = None
        self.q = None

    def aggiorna(self, barra, i):
        self.q = self.quote.get(barra.ts)
        self.media_prec = sum(self.finestra) / self.n if len(self.finestra) == self.n else None
        if self.q is not None:
            self.finestra.append(self.q)

    def pronta(self):
        return self.media_prec is not None

    def calcola_segnale(self, storia):
        c = storia[-1].close
        return segnale_da_distanza(self.direzione, c, self.stop_pct * c)

    def condizione(self, storia):
        if self.q is None:
            return False
        return self.q > self.media_prec if self.direzione == "long" else self.q < self.media_prec

    def esci(self, storia, pos):
        return self.barre_in_posizione(storia, pos) >= self.uscita


# --------------------------------------------------------------------------- #
# I-16 periodicita' oraria (1h)
# --------------------------------------------------------------------------- #
class StessaOra(Variante):
    def __init__(self, serie, direzione, n_giorni=20, uscita=1, k_stop=2.0):
        super().__init__(serie)
        self.direzione = direzione
        self.n = n_giorni
        self.uscita = uscita
        self.k = k_stop
        self.atr = ATR(14)
        self.per_ora = [deque(maxlen=n_giorni) for _ in range(24)]

    def aggiorna(self, barra, i):
        self.atr.aggiorna(barra.high, barra.low, barra.close)
        ora = (barra.ts % GIORNO_MS) // 3_600_000
        self.per_ora[ora].append(barra.close / barra.open - 1.0)

    def pronta(self):
        return self.atr.valore is not None and all(len(d) == self.n for d in self.per_ora)

    def calcola_segnale(self, storia):
        return segnale_da_distanza(self.direzione, storia[-1].close, self.k * self.atr.valore)

    def condizione(self, storia):
        prossima = ((storia[-1].ts % GIORNO_MS) // 3_600_000 + 1) % 24
        medie = [sum(d) / len(d) for d in self.per_ora]
        if self.direzione == "long":
            migliore = max(range(24), key=lambda h: medie[h])
            return prossima == migliore and medie[migliore] > 0
        peggiore = min(range(24), key=lambda h: medie[h])
        return prossima == peggiore and medie[peggiore] < 0

    def esci(self, storia, pos):
        return self.barre_in_posizione(storia, pos) >= self.uscita


# --------------------------------------------------------------------------- #
# I-17 rottura di volatilita' dall'apertura del giorno (1h)
# --------------------------------------------------------------------------- #
class RotturaVolatilita(Variante):
    def __init__(self, serie, direzione, k=0.5):
        super().__init__(serie)
        self.direzione = direzione
        self.k = k
        self.giorno = None
        self.apertura = None
        self.max_oggi = None
        self.min_oggi = None
        self.escursione_ieri = None
        self.segnalato_oggi = False
        self.prima_rottura = False

    def aggiorna(self, barra, i):
        giorno = barra.ts // GIORNO_MS
        if giorno != self.giorno:
            if self.giorno is not None and giorno == self.giorno + 1 and self.max_oggi is not None:
                self.escursione_ieri = self.max_oggi - self.min_oggi
            else:
                self.escursione_ieri = None  # primo giorno o giorno saltato (buco)
            self.giorno = giorno
            self.apertura = barra.open if barra.ts % GIORNO_MS == 0 else None  # serve la barra delle 00:00
            self.max_oggi, self.min_oggi = barra.high, barra.low
            self.segnalato_oggi = False
        else:
            self.max_oggi = max(self.max_oggi, barra.high)
            self.min_oggi = min(self.min_oggi, barra.low)
        # la prima barra del giorno che chiude oltre la soglia (indipendente da chi chiama)
        self.prima_rottura = False
        if self.escursione_ieri is not None and self.apertura is not None and not self.segnalato_oggi:
            soglia = self.k * self.escursione_ieri
            if self.direzione == "long":
                rottura = barra.close > self.apertura + soglia
            else:
                rottura = barra.close < self.apertura - soglia
            if rottura:
                self.segnalato_oggi = True
                self.prima_rottura = True

    def pronta(self):
        return self.escursione_ieri is not None and self.apertura is not None

    def calcola_segnale(self, storia):
        return segnale_da_livello(self.direzione, storia[-1].close, self.apertura)

    def condizione(self, storia):
        b = storia[-1]
        if (b.ts % GIORNO_MS) // 3_600_000 > 22:
            return False
        return self.prima_rottura

    def esci(self, storia, pos):
        return (storia[-1].ts % GIORNO_MS) // 3_600_000 == 23


VARIANTI = {
    "I-01a": (MomentumSettimana, {"direzione": "long"}, "1d"),
    "I-01b": (MomentumSettimana, {"direzione": "short"}, "1d"),
    "I-02a": (Donchian, {"direzione": "long"}, "4h"),
    "I-02b": (Donchian, {"direzione": "short"}, "4h"),
    "I-03a": (SopraMedia, {"direzione": "long"}, "1d"),
    "I-03b": (SopraMedia, {"direzione": "short"}, "1d"),
    "I-04a": (RSI2, {"direzione": "long"}, "4h"),
    "I-04b": (RSI2, {"direzione": "short"}, "4h"),
    "I-05a": (NR7, {"direzione": "long"}, "4h"),
    "I-05b": (NR7, {"direzione": "short"}, "4h"),
    "I-06a": (PrimaMezzora, {"direzione": "long"}, "30m"),
    "I-06b": (PrimaMezzora, {"direzione": "short"}, "30m"),
    "I-07a": (RitardoBTC, {"direzione": "long"}, "1h"),
    "I-07b": (RitardoBTC, {"direzione": "short"}, "1h"),
    "I-08a": (Funding, {"direzione": "short"}, "8h"),
    "I-08b": (Funding, {"direzione": "long"}, "8h"),
    "I-09a": (Lunedi, {"direzione": "long"}, "1d"),
    "I-10a": (GiornoAnomalo, {"direzione": "long"}, "1d"),
    "I-10b": (GiornoAnomalo, {"direzione": "short"}, "1d"),
    "I-11a": (NumeroTondo, {"direzione": "long"}, "1h"),
    "I-11b": (NumeroTondo, {"direzione": "short"}, "1h"),
    "I-12a": (VolumeInsolito, {"direzione": "long"}, "1d"),
    "I-12b": (VolumeInsolito, {"direzione": "short"}, "1d"),
    "I-13a": (VenditeForzate, {"direzione": "long"}, "1h"),
    "I-13b": (VenditeForzate, {"direzione": "short"}, "1h"),
    "I-14a": (GiornoPrima, {"direzione": "short"}, "1h"),
    "I-14b": (GiornoPrima, {"direzione": "long"}, "1h"),
    "I-15a": (Squilibrio, {"direzione": "long"}, "1d"),
    "I-15b": (Squilibrio, {"direzione": "short"}, "1d"),
    "I-16a": (StessaOra, {"direzione": "long"}, "1h"),
    "I-16b": (StessaOra, {"direzione": "short"}, "1h"),
    "I-17a": (RotturaVolatilita, {"direzione": "long"}, "1h"),
    "I-17b": (RotturaVolatilita, {"direzione": "short"}, "1h"),
    "I-18a": (Cascata, {"direzione": "short"}, "1h"),
}
