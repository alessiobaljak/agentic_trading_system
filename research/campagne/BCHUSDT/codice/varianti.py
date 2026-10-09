"""Le varianti della campagna BCHUSDT. Ognuna e' descritta in ipotesi.md prima del test.

Ogni classe e' una regola completa (timeframe, direzione, ingresso, uscita, stop,
target). Gli indicatori sono causali (``comune.verifica_causalita``). Il registro
``VARIANTI`` collega l'id del log alla fabbrica della variante.
"""
from datetime import datetime, timezone

import numpy as np

from research.campagne.BCHUSDT.codice import comune, indicatori as ind

ORA = 3_600_000
GIORNO = 24 * ORA


def _ok(*xs):
    return all(x is not None and np.isfinite(x) for x in xs)


# ---------------------------------------------------------------------------
# I-01 Momento della serie (rendimento degli ultimi 7 giorni), 1d
# ---------------------------------------------------------------------------
class MomentoSerie(comune.Variante):
    tf = "1d"
    riscaldamento = 14

    def __init__(self, id, direzione, giorni=7, tenuta=7, atr_stop=2.5):
        self.id, self.direzione = id, direzione
        self.giorni, self.tenuta, self.atr_stop = giorni, tenuta, atr_stop
        self.riscaldamento = max(14, giorni)

    def prepara(self, s):
        return {"r": ind.rendimento(s["close"], self.giorni), "atr": ind.atr(s["high"], s["low"], s["close"], 14)}

    def stop_target(self, x, s, i):
        a = x["atr"][i]
        if not _ok(a):
            return None
        c = s["close"][i]
        return (c - self.atr_stop * a, None) if self.direzione == "long" else (c + self.atr_stop * a, None)

    def condizione(self, x, s, i):
        r = x["r"][i]
        return _ok(r) and (r > 0 if self.direzione == "long" else r < 0)

    def esci(self, x, s, i, tenute, pos):
        return tenute >= self.tenuta


# ---------------------------------------------------------------------------
# I-02 Rottura del canale (Donchian / rottura del range), 4h
# ---------------------------------------------------------------------------
class RotturaCanale(comune.Variante):
    tf = "4h"

    def __init__(self, id, direzione, n_ingresso=20, n_uscita=10, atr_n=20, atr_stop=2.0):
        self.id, self.direzione = id, direzione
        self.n_in, self.n_out, self.atr_n, self.atr_stop = n_ingresso, n_uscita, atr_n, atr_stop
        self.riscaldamento = max(n_ingresso, n_uscita, atr_n) + 1

    def prepara(self, s):
        h, l = s["high"], s["low"]
        return {
            "max_in": ind.precedente(ind.massimo(h, self.n_in), 1),
            "min_in": ind.precedente(ind.minimo(l, self.n_in), 1),
            "max_out": ind.precedente(ind.massimo(h, self.n_out), 1),
            "min_out": ind.precedente(ind.minimo(l, self.n_out), 1),
            "atr": ind.atr(h, l, s["close"], self.atr_n),
        }

    def stop_target(self, x, s, i):
        a = x["atr"][i]
        if not _ok(a):
            return None
        c = s["close"][i]
        return (c - self.atr_stop * a, None) if self.direzione == "long" else (c + self.atr_stop * a, None)

    def condizione(self, x, s, i):
        c = s["close"][i]
        if self.direzione == "long":
            return _ok(x["max_in"][i]) and c > x["max_in"][i]
        return _ok(x["min_in"][i]) and c < x["min_in"][i]

    def esci(self, x, s, i, tenute, pos):
        c = s["close"][i]
        if self.direzione == "long":
            return _ok(x["min_out"][i]) and c < x["min_out"][i]
        return _ok(x["max_out"][i]) and c > x["max_out"][i]


# ---------------------------------------------------------------------------
# I-03 RSI a 2 periodi nel verso della media a 200 (Connors e Alvarez), 4h
# ---------------------------------------------------------------------------
class RsiBreve(comune.Variante):
    tf = "4h"

    def __init__(self, id, direzione, soglia_long=10, soglia_short=90, n_media=200, n_uscita=5, atr_stop=3.0):
        self.id, self.direzione = id, direzione
        self.s_long, self.s_short, self.n_media, self.n_out, self.atr_stop = (
            soglia_long, soglia_short, n_media, n_uscita, atr_stop)
        self.riscaldamento = n_media

    def prepara(self, s):
        c = s["close"]
        return {"rsi": ind.rsi(c, 2), "media": ind.sma(c, self.n_media), "media_out": ind.sma(c, self.n_out),
                "atr": ind.atr(s["high"], s["low"], c, 14)}

    def stop_target(self, x, s, i):
        a = x["atr"][i]
        if not _ok(a):
            return None
        c = s["close"][i]
        return (c - self.atr_stop * a, None) if self.direzione == "long" else (c + self.atr_stop * a, None)

    def condizione(self, x, s, i):
        r, m, c = x["rsi"][i], x["media"][i], s["close"][i]
        if not _ok(r, m):
            return False
        if self.direzione == "long":
            return r < self.s_long and c > m
        return r > self.s_short and c < m

    def esci(self, x, s, i, tenute, pos):
        m, c = x["media_out"][i], s["close"][i]
        if not _ok(m):
            return False
        return c > m if self.direzione == "long" else c < m


# ---------------------------------------------------------------------------
# I-04 Rottura di volatilita' dall'apertura del giorno (Larry Williams), 1h
# ---------------------------------------------------------------------------
def _giornaliere(s):
    """Per ogni barra oraria: apertura del giorno UTC, range del giorno UTC precedente (se completo),
    indice dell'ora nel giorno. Causale: il range e' quello di un giorno gia' chiuso."""
    ts = s["ts"]
    giorno = ts // GIORNO
    n = len(ts)
    apertura = np.full(n, np.nan)
    range_prec = np.full(n, np.nan)
    ora = ((ts % GIORNO) // ORA).astype(int)
    hi_g, lo_g, cnt_g, open_g = {}, {}, {}, {}
    for k in range(n):
        g = int(giorno[k])
        if g not in open_g:
            open_g[g] = s["open"][k]
            hi_g[g], lo_g[g], cnt_g[g] = s["high"][k], s["low"][k], 0
        hi_g[g] = max(hi_g[g], s["high"][k])
        lo_g[g] = min(lo_g[g], s["low"][k])
        cnt_g[g] += 1
        apertura[k] = open_g[g]
        if (g - 1) in cnt_g and cnt_g[g - 1] == 24:
            range_prec[k] = hi_g[g - 1] - lo_g[g - 1]
    return apertura, range_prec, ora


class RotturaVolatilita(comune.Variante):
    tf = "1h"
    riscaldamento = 48

    def __init__(self, id, direzione, k=0.5):
        self.id, self.direzione, self.k = id, direzione, k

    def prepara(self, s):
        apertura, rng, ora = _giornaliere(s)
        # la prima barra del giorno deve essere l'ora 0: altrimenti l'apertura del giorno non e' nota
        prima = np.full(len(ora), False)
        g = s["ts"] // GIORNO
        primo_ora0 = {}
        for k in range(len(ora)):
            gg = int(g[k])
            if gg not in primo_ora0:
                primo_ora0[gg] = ora[k] == 0
            prima[k] = primo_ora0[gg]
        apertura = np.where(prima, apertura, np.nan)
        livello_su = apertura + self.k * rng
        livello_giu = apertura - self.k * rng
        c = s["close"]
        # primo attraversamento del giorno: nessuna chiusura oltre il livello prima, nello stesso giorno
        primo = np.full(len(c), False)
        gia = {}
        for k in range(len(c)):
            gg = int(g[k])
            lv = livello_su[k] if self.direzione == "long" else livello_giu[k]
            oltre = np.isfinite(lv) and (c[k] > lv if self.direzione == "long" else c[k] < lv)
            if oltre and not gia.get(gg, False):
                primo[k] = True
            if oltre:
                gia[gg] = True
        return {"apertura": apertura, "su": livello_su, "giu": livello_giu, "primo": primo.astype(float),
                "ora": ora.astype(float)}

    def stop_target(self, x, s, i):
        a = x["apertura"][i]
        if not _ok(a) or x["ora"][i] >= 23:
            return None
        return a, None

    def condizione(self, x, s, i):
        return bool(x["primo"][i] > 0)

    def esci(self, x, s, i, tenute, pos):
        return x["ora"][i] >= 23  # chiusura all'apertura del giorno dopo


VARIANTI = {
    "BCHUSDT-001": lambda: MomentoSerie("BCHUSDT-001", "long"),
    "BCHUSDT-002": lambda: MomentoSerie("BCHUSDT-002", "short"),
    "BCHUSDT-003": lambda: RotturaCanale("BCHUSDT-003", "long"),
    "BCHUSDT-004": lambda: RotturaCanale("BCHUSDT-004", "short"),
    "BCHUSDT-005": lambda: RsiBreve("BCHUSDT-005", "long"),
    "BCHUSDT-006": lambda: RsiBreve("BCHUSDT-006", "short"),
    "BCHUSDT-007": lambda: RotturaVolatilita("BCHUSDT-007", "long"),
    "BCHUSDT-008": lambda: RotturaVolatilita("BCHUSDT-008", "short"),
}
