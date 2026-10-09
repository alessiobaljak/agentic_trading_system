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


# ---------------------------------------------------------------------------
# I-05 Attraversamento dei livelli tondi (Osler), 1h
# ---------------------------------------------------------------------------
def _passo_tondo(p):
    """Il passo dei livelli tondi: 10 per prezzi fra 100 e 1000, 100 fra 1000 e 10000, ecc."""
    return 10.0 ** (np.floor(np.log10(p)) - 1)


class LivelliTondi(comune.Variante):
    tf = "1h"
    riscaldamento = 25

    def __init__(self, id, direzione, tenuta=12, atr_stop=1.0):
        self.id, self.direzione, self.tenuta, self.atr_stop = id, direzione, tenuta, atr_stop

    def prepara(self, s):
        c = s["close"]
        cp = ind.precedente(c, 1)
        passo = _passo_tondo(np.where(np.isfinite(cp), cp, c))
        if self.direzione == "long":
            livello = np.floor(c / passo) * passo          # il livello tondo piu' alto sotto il close
            attraversa = (cp <= livello) & (c > livello)
        else:
            livello = np.ceil(c / passo) * passo           # il livello tondo piu' basso sopra il close
            attraversa = (cp >= livello) & (c < livello)
        return {"livello": livello, "attraversa": attraversa.astype(float),
                "atr": ind.atr(s["high"], s["low"], c, 24)}

    def stop_target(self, x, s, i):
        a, lv = x["atr"][i], x["livello"][i]
        if not _ok(a, lv):
            return None
        return (lv - self.atr_stop * a, None) if self.direzione == "long" else (lv + self.atr_stop * a, None)

    def condizione(self, x, s, i):
        return bool(x["attraversa"][i] > 0)

    def esci(self, x, s, i, tenute, pos):
        return tenute >= self.tenuta


# ---------------------------------------------------------------------------
# I-06 Inerzia dopo le giornate di sovra-reazione (Caporale e Plastun), 1d
# ---------------------------------------------------------------------------
class SovraReazione(comune.Variante):
    tf = "1d"

    def __init__(self, id, direzione, finestra=30, k=1.0, atr_stop=2.0):
        self.id, self.direzione, self.finestra, self.k, self.atr_stop = id, direzione, finestra, k, atr_stop
        self.riscaldamento = finestra + 1

    def prepara(self, s):
        r = s["close"] / s["open"] - 1
        ar = np.abs(r)
        soglia = ind.precedente(ind.sma(ar, self.finestra) + self.k * ind.dev_std(ar, self.finestra), 1)
        return {"r": r, "soglia": soglia, "atr": ind.atr(s["high"], s["low"], s["close"], 14)}

    def stop_target(self, x, s, i):
        a = x["atr"][i]
        if not _ok(a):
            return None
        c = s["close"][i]
        return (c - self.atr_stop * a, None) if self.direzione == "long" else (c + self.atr_stop * a, None)

    def condizione(self, x, s, i):
        r, sg = x["r"][i], x["soglia"][i]
        if not _ok(r, sg):
            return False
        return r > sg if self.direzione == "long" else r < -sg

    def esci(self, x, s, i, tenute, pos):
        return tenute >= 1


# ---------------------------------------------------------------------------
# I-07 Lunedi' (Caporale e Plastun), 1d
# ---------------------------------------------------------------------------
class Lunedi(comune.Variante):
    tf = "1d"
    riscaldamento = 14

    def __init__(self, id, direzione="long", atr_stop=2.0):
        self.id, self.direzione, self.atr_stop = id, direzione, atr_stop

    def prepara(self, s):
        # 1970-01-01 era giovedi': (giorni + 3) % 7 == 0 e' lunedi', == 6 e' domenica
        giorno_sett = ((s["ts"] // GIORNO) + 3) % 7
        return {"gs": giorno_sett.astype(float), "atr": ind.atr(s["high"], s["low"], s["close"], 14)}

    def stop_target(self, x, s, i):
        a = x["atr"][i]
        if not _ok(a):
            return None
        c = s["close"][i]
        return (c - self.atr_stop * a, None) if self.direzione == "long" else (c + self.atr_stop * a, None)

    def condizione(self, x, s, i):
        return x["gs"][i] == 6  # chiusura della domenica: ingresso all'apertura del lunedi'

    def esci(self, x, s, i, tenute, pos):
        return tenute >= 1


# ---------------------------------------------------------------------------
# I-08 Premio del volume alto (Gervais, Kaniel, Mingelgrin), 1d
# ---------------------------------------------------------------------------
class VolumeAlto(comune.Variante):
    tf = "1d"

    def __init__(self, id, direzione="long", finestra=49, quantile=0.9, tenuta=10, atr_stop=3.0):
        self.id, self.direzione, self.finestra, self.q, self.tenuta, self.atr_stop = (
            id, direzione, finestra, quantile, tenuta, atr_stop)
        self.riscaldamento = finestra + 1

    def prepara(self, s):
        import pandas as pd
        v = s["volume_usdt"]
        soglia = pd.Series(v).rolling(self.finestra, min_periods=self.finestra).quantile(self.q).to_numpy()
        return {"v": v, "soglia": ind.precedente(soglia, 1), "atr": ind.atr(s["high"], s["low"], s["close"], 14)}

    def stop_target(self, x, s, i):
        a = x["atr"][i]
        if not _ok(a):
            return None
        c = s["close"][i]
        return (c - self.atr_stop * a, None) if self.direzione == "long" else (c + self.atr_stop * a, None)

    def condizione(self, x, s, i):
        v, sg = x["v"][i], x["soglia"][i]
        return _ok(v, sg) and v > sg

    def esci(self, x, s, i, tenute, pos):
        return tenute >= self.tenuta


# ---------------------------------------------------------------------------
# I-09 Inversione dei movimenti grandi con volume alto (Campbell, Grossman, Wang), 4h
# ---------------------------------------------------------------------------
class InversioneVolume(comune.Variante):
    tf = "4h"

    def __init__(self, id, direzione, finestra=100, z=2.0, vol_rapporto=2.0, tenuta=6, atr_stop=2.5):
        self.id, self.direzione, self.finestra, self.z, self.vr, self.tenuta, self.atr_stop = (
            id, direzione, finestra, z, vol_rapporto, tenuta, atr_stop)
        self.riscaldamento = finestra + 1

    def prepara(self, s):
        c = s["close"]
        r = c / ind.precedente(c, 1) - 1
        sd = ind.precedente(ind.dev_std(r, self.finestra), 1)
        vm = ind.precedente(ind.sma(s["volume_usdt"], self.finestra), 1)
        return {"z": r / sd, "vr": s["volume_usdt"] / vm, "atr": ind.atr(s["high"], s["low"], c, 14)}

    def stop_target(self, x, s, i):
        a = x["atr"][i]
        if not _ok(a):
            return None
        c = s["close"][i]
        return (c - self.atr_stop * a, None) if self.direzione == "long" else (c + self.atr_stop * a, None)

    def condizione(self, x, s, i):
        z, vr = x["z"][i], x["vr"][i]
        if not _ok(z, vr) or vr <= self.vr:
            return False
        return z < -self.z if self.direzione == "long" else z > self.z

    def esci(self, x, s, i, tenute, pos):
        return tenute >= self.tenuta


# ---------------------------------------------------------------------------
# I-10 Funding estremo: la parte affollata paga (He, Manela, Ross, von Wachter), 8h
# ---------------------------------------------------------------------------
class FundingEstremo(comune.Variante):
    tf = "8h"

    def __init__(self, id, direzione, finestra=90, quantile=0.9, tenuta=3, atr_stop=2.0):
        self.id, self.direzione, self.finestra, self.q, self.tenuta, self.atr_stop = (
            id, direzione, finestra, quantile, tenuta, atr_stop)
        self.riscaldamento = finestra + 1

    def prepara(self, s):
        import bisect
        import pandas as pd
        f_ts = [t for t, _ in s["funding"]]
        f_r = [r for _, r in s["funding"]]
        chiusure = s["ts"] + s["ms_barra"] - 1
        f = np.full(len(chiusure), np.nan)
        for k, t in enumerate(chiusure):
            j = bisect.bisect_right(f_ts, int(t)) - 1
            if j >= 0 and int(t) - f_ts[j] < s["ms_barra"]:
                f[k] = f_r[j]
        serie_f = pd.Series(f)
        alto = serie_f.rolling(self.finestra, min_periods=self.finestra).quantile(self.q).to_numpy()
        basso = serie_f.rolling(self.finestra, min_periods=self.finestra).quantile(1 - self.q).to_numpy()
        return {"f": f, "alto": ind.precedente(alto, 1), "basso": ind.precedente(basso, 1),
                "atr": ind.atr(s["high"], s["low"], s["close"], 14)}

    def stop_target(self, x, s, i):
        a = x["atr"][i]
        if not _ok(a):
            return None
        c = s["close"][i]
        return (c - self.atr_stop * a, None) if self.direzione == "long" else (c + self.atr_stop * a, None)

    def condizione(self, x, s, i):
        f, hi, lo = x["f"][i], x["alto"][i], x["basso"][i]
        if not _ok(f, hi, lo):
            return False
        # short quando i long sono affollati (funding nel decile alto), long nello specchio
        return f > hi if self.direzione == "short" else f < lo

    def esci(self, x, s, i, tenute, pos):
        return tenute >= self.tenuta


# ---------------------------------------------------------------------------
# I-11 Flusso degli ordini aggressivi (Evans e Lyons), 1h
# ---------------------------------------------------------------------------
_TAKER = {}


def quota_acquisti_aggressivi(tf):
    """{ts: (taker_buy_quote_volume, quote_volume)} dai file klines di BCHUSDT (colonne 10 e 7)."""
    if tf in _TAKER:
        return _TAKER[tf]
    from research.src import dati
    out = {}
    for p in sorted((comune.CARTELLA_DATI / "klines" / tf).glob("*.zip")):
        for riga in dati.righe_csv_da_zip(p):
            ts = dati.normalizza_ts(riga[0])
            if ts not in out and len(riga) > 10 and riga[10].strip() and riga[7].strip():
                out[ts] = (float(riga[10]), float(riga[7]))
    _TAKER[tf] = out
    return out


class FlussoAggressivo(comune.Variante):
    tf = "1h"

    def __init__(self, id, direzione, barre=4, finestra=720, z=2.0, tenuta=4, atr_stop=2.0):
        self.id, self.direzione, self.barre, self.finestra, self.z, self.tenuta, self.atr_stop = (
            id, direzione, barre, finestra, z, tenuta, atr_stop)
        self.riscaldamento = finestra + barre + 1

    def prepara(self, s):
        tk = quota_acquisti_aggressivi(self.tf)
        compra = np.array([tk.get(int(t), (np.nan, np.nan))[0] for t in s["ts"]])
        tutto = np.array([tk.get(int(t), (np.nan, np.nan))[1] for t in s["ts"]])
        quota = ind.somma(compra, self.barre) / ind.somma(tutto, self.barre)
        m = ind.precedente(ind.sma(quota, self.finestra), 1)
        sd = ind.precedente(ind.dev_std(quota, self.finestra), 1)
        return {"z": (quota - m) / sd, "atr": ind.atr(s["high"], s["low"], s["close"], 24)}

    def stop_target(self, x, s, i):
        a = x["atr"][i]
        if not _ok(a):
            return None
        c = s["close"][i]
        return (c - self.atr_stop * a, None) if self.direzione == "long" else (c + self.atr_stop * a, None)

    def condizione(self, x, s, i):
        z = x["z"][i]
        if not _ok(z):
            return False
        return z > self.z if self.direzione == "long" else z < -self.z

    def esci(self, x, s, i, tenute, pos):
        return tenute >= self.tenuta


# ---------------------------------------------------------------------------
# I-12 Compressione delle bande di Bollinger e rottura (Bollinger), 4h
# ---------------------------------------------------------------------------
class CompressioneBande(comune.Variante):
    tf = "4h"

    def __init__(self, id, direzione, n=20, k=2.0, n_minimo=125, recente=10, atr_stop=2.0):
        self.id, self.direzione, self.n, self.k, self.n_min, self.recente, self.atr_stop = (
            id, direzione, n, k, n_minimo, recente, atr_stop)
        self.riscaldamento = n + n_minimo

    def prepara(self, s):
        c = s["close"]
        m = ind.sma(c, self.n)
        sd = ind.dev_std(c, self.n)
        larghezza = 2 * self.k * sd / m
        compresso = ind.minimo(larghezza, self.recente) <= ind.minimo(larghezza, self.n_min)
        return {"media": m, "su": m + self.k * sd, "giu": m - self.k * sd, "compresso": compresso.astype(float),
                "atr": ind.atr(s["high"], s["low"], c, 14)}

    def stop_target(self, x, s, i):
        a = x["atr"][i]
        if not _ok(a):
            return None
        c = s["close"][i]
        return (c - self.atr_stop * a, None) if self.direzione == "long" else (c + self.atr_stop * a, None)

    def condizione(self, x, s, i):
        if not x["compresso"][i] > 0:
            return False
        c = s["close"][i]
        if self.direzione == "long":
            return _ok(x["su"][i]) and c > x["su"][i]
        return _ok(x["giu"][i]) and c < x["giu"][i]

    def esci(self, x, s, i, tenute, pos):
        m, c = x["media"][i], s["close"][i]
        if not _ok(m):
            return False
        return c < m if self.direzione == "long" else c > m


# ---------------------------------------------------------------------------
# I-13 Prezzo sopra la media mobile (Detzel, Liu, Strauss, Zhou, Zhu), 1d
# ---------------------------------------------------------------------------
class SopraMedia(comune.Variante):
    tf = "1d"

    def __init__(self, id, direzione, n=20, atr_stop=3.0):
        self.id, self.direzione, self.n, self.atr_stop = id, direzione, n, atr_stop
        self.riscaldamento = max(n, 14) + 1

    def prepara(self, s):
        c = s["close"]
        m = ind.sma(c, self.n)
        return {"m": m, "mp": ind.precedente(m, 1), "cp": ind.precedente(c, 1),
                "atr": ind.atr(s["high"], s["low"], c, 14)}

    def stop_target(self, x, s, i):
        a = x["atr"][i]
        if not _ok(a):
            return None
        c = s["close"][i]
        return (c - self.atr_stop * a, None) if self.direzione == "long" else (c + self.atr_stop * a, None)

    def condizione(self, x, s, i):
        c, m, cp, mp = s["close"][i], x["m"][i], x["cp"][i], x["mp"][i]
        if not _ok(m, cp, mp):
            return False
        if self.direzione == "long":
            return c > m and cp <= mp
        return c < m and cp >= mp

    def esci(self, x, s, i, tenute, pos):
        m, c = x["m"][i], s["close"][i]
        if not _ok(m):
            return False
        return c < m if self.direzione == "long" else c > m


# ---------------------------------------------------------------------------
# I-14 Volatilita' bassa: rendimento per rischio piu' alto (Moreira e Muir), 1d
# ---------------------------------------------------------------------------
class VolatilitaBassa(comune.Variante):
    tf = "1d"

    def __init__(self, id, direzione="long", n_vol=7, finestra=90, tenuta=5, atr_stop=2.5):
        self.id, self.direzione, self.n_vol, self.finestra, self.tenuta, self.atr_stop = (
            id, direzione, n_vol, finestra, tenuta, atr_stop)
        self.riscaldamento = n_vol + finestra + 1

    def prepara(self, s):
        import pandas as pd
        c = s["close"]
        r = c / ind.precedente(c, 1) - 1
        vol = ind.dev_std(r, self.n_vol)
        mediana = ind.precedente(pd.Series(vol).rolling(self.finestra, min_periods=self.finestra).median().to_numpy(), 1)
        return {"vol": vol, "mediana": mediana, "atr": ind.atr(s["high"], s["low"], c, 14)}

    def stop_target(self, x, s, i):
        a = x["atr"][i]
        if not _ok(a):
            return None
        c = s["close"][i]
        return (c - self.atr_stop * a, None) if self.direzione == "long" else (c + self.atr_stop * a, None)

    def condizione(self, x, s, i):
        v, m = x["vol"][i], x["mediana"][i]
        return _ok(v, m) and v < m

    def esci(self, x, s, i, tenute, pos):
        return tenute >= self.tenuta


class _Bande1h(CompressioneBande):
    """Stessa regola di I-12 su 1h, stessi parametri in barre (20, 2, 125, 10)."""
    tf = "1h"


def _bande_1h(id, direzione):
    return _Bande1h(id, direzione)


# ---------------------------------------------------------------------------
# Ritocchi (regola 6): stessa idea, timeframe, direzione e meccanismo
# ---------------------------------------------------------------------------
class MomentoSerieFiltro(MomentoSerie):
    """I-01 con un filtro nato dallo studio dei fallimenti: anche il rendimento a ``giorni_lunghi``
    giorni deve essere dalla stessa parte (negativo per lo short, positivo per il long)."""

    def __init__(self, id, direzione, giorni_lunghi=30, **kw):
        super().__init__(id, direzione, **kw)
        self.giorni_lunghi = giorni_lunghi
        self.riscaldamento = max(self.riscaldamento, giorni_lunghi)

    def prepara(self, s):
        x = super().prepara(s)
        x["r_lungo"] = ind.rendimento(s["close"], self.giorni_lunghi)
        return x

    def condizione(self, x, s, i):
        rl = x["r_lungo"][i]
        if not _ok(rl):
            return False
        return super().condizione(x, s, i) and (rl < 0 if self.direzione == "short" else rl > 0)


VARIANTI = {
    "BCHUSDT-001": lambda: MomentoSerie("BCHUSDT-001", "long"),
    "BCHUSDT-002": lambda: MomentoSerie("BCHUSDT-002", "short"),
    "BCHUSDT-003": lambda: RotturaCanale("BCHUSDT-003", "long"),
    "BCHUSDT-004": lambda: RotturaCanale("BCHUSDT-004", "short"),
    "BCHUSDT-005": lambda: RsiBreve("BCHUSDT-005", "long"),
    "BCHUSDT-006": lambda: RsiBreve("BCHUSDT-006", "short"),
    "BCHUSDT-007": lambda: RotturaVolatilita("BCHUSDT-007", "long"),
    "BCHUSDT-008": lambda: RotturaVolatilita("BCHUSDT-008", "short"),
    "BCHUSDT-009": lambda: LivelliTondi("BCHUSDT-009", "long"),
    "BCHUSDT-010": lambda: LivelliTondi("BCHUSDT-010", "short"),
    "BCHUSDT-011": lambda: SovraReazione("BCHUSDT-011", "long"),
    "BCHUSDT-012": lambda: SovraReazione("BCHUSDT-012", "short"),
    "BCHUSDT-013": lambda: Lunedi("BCHUSDT-013", "long"),
    "BCHUSDT-014": lambda: VolumeAlto("BCHUSDT-014", "long"),
    "BCHUSDT-015": lambda: InversioneVolume("BCHUSDT-015", "long"),
    "BCHUSDT-016": lambda: InversioneVolume("BCHUSDT-016", "short"),
    "BCHUSDT-017": lambda: FundingEstremo("BCHUSDT-017", "short"),
    "BCHUSDT-018": lambda: FundingEstremo("BCHUSDT-018", "long"),
    "BCHUSDT-019": lambda: FlussoAggressivo("BCHUSDT-019", "long"),
    "BCHUSDT-020": lambda: FlussoAggressivo("BCHUSDT-020", "short"),
    "BCHUSDT-021": lambda: CompressioneBande("BCHUSDT-021", "long"),
    "BCHUSDT-022": lambda: CompressioneBande("BCHUSDT-022", "short"),
    "BCHUSDT-023": lambda: SopraMedia("BCHUSDT-023", "long"),
    "BCHUSDT-024": lambda: SopraMedia("BCHUSDT-024", "short"),
    # varianti delle idee nuove con le soglie allentate dopo lo scarto (senza risultati visti)
    "BCHUSDT-025": lambda: SovraReazione("BCHUSDT-025", "long", k=0.5),
    "BCHUSDT-026": lambda: SovraReazione("BCHUSDT-026", "short", k=0.5),
    "BCHUSDT-027": lambda: VolumeAlto("BCHUSDT-027", "long", quantile=0.8, tenuta=5),
    "BCHUSDT-028": lambda: _bande_1h("BCHUSDT-028", "long"),
    "BCHUSDT-029": lambda: _bande_1h("BCHUSDT-029", "short"),
    "BCHUSDT-030": lambda: SopraMedia("BCHUSDT-030", "long", n=10),
    "BCHUSDT-031": lambda: SopraMedia("BCHUSDT-031", "short", n=10),
    "BCHUSDT-032": lambda: VolatilitaBassa("BCHUSDT-032", "long"),
    "BCHUSDT-033": lambda: MomentoSerieFiltro("BCHUSDT-033", "short", giorni_lunghi=30),
}
