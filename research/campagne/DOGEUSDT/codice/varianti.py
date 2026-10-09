"""Le varianti della campagna DOGEUSDT, come scritte in ipotesi.md (regole esatte del registro)."""
from __future__ import annotations

from datetime import datetime, timezone

import numpy as np

import quadro as q
from quadro import Base


def _ora_e_giorno(ts):
    """Ora UTC e giorno della settimana (lunedi' = 0) di ogni barra."""
    ore = np.array([datetime.fromtimestamp(t / 1000, tz=timezone.utc).hour for t in ts])
    minuti = np.array([datetime.fromtimestamp(t / 1000, tz=timezone.utc).minute for t in ts])
    wd = np.array([datetime.fromtimestamp(t / 1000, tz=timezone.utc).weekday() for t in ts])
    giorno = (ts // q.dati.MS_GIORNO).astype(np.int64)
    return ore, minuti, wd, giorno


def rendimenti(c):
    r = np.full(len(c), np.nan)
    r[1:] = c[1:] / c[:-1] - 1
    return r


class Controllo(Base):
    """Controllo positivo (lookahead dichiarato): legge la barra successiva."""
    tf, direzione, barre, stop_atr = "1h", "long", 1, 2.0

    def prepara(self, d):
        super().prepara(d)
        o, c = d["open"], d["close"]
        futura = np.full(len(c), False)
        futura[:-1] = c[1:] > o[1:] * 1.003
        self.futura = futura

    def condizione(self, i):
        return bool(self.futura[i])


class Momento7(Base):
    """I-01: rendimento a 7 barre (1d) col segno della direzione; uscita dopo 3 barre."""
    tf, barre, stop_atr = "1d", 3, 2.5
    lookback = 7

    def __init__(self, direzione):
        self.direzione = direzione

    def prepara(self, d):
        super().prepara(d)
        c = self.c
        self.ret = np.full(len(c), np.nan)
        L = self.lookback
        self.ret[L:] = c[L:] / c[:-L] - 1
        self.primo_indice = q.primo_finito(self.a, self.ret)

    def condizione(self, i):
        return self.ret[i] > 0 if self.direzione == "long" else self.ret[i] < 0


class PrimaMezzora(Base):
    """I-02: segno della barra 00:00-00:30 UTC; ingresso alle 23:30, uscita dopo 1 barra."""
    tf, barre, stop_atr = "30m", 1, 2.0

    def __init__(self, direzione):
        self.direzione = direzione

    def prepara(self, d):
        super().prepara(d)
        ore, minuti, _, giorno = _ora_e_giorno(d["ts"])
        segno_prima = {}
        for k in range(len(d["ts"])):
            if ore[k] == 0 and minuti[k] == 0:
                segno_prima[giorno[k]] = np.sign(d["close"][k] - d["open"][k])
        self.cond = np.zeros(len(d["ts"]), dtype=bool)
        voluto = 1 if self.direzione == "long" else -1
        for k in range(len(d["ts"])):
            if ore[k] == 23 and minuti[k] == 0 and segno_prima.get(giorno[k], 0) == voluto:
                self.cond[k] = True

    def condizione(self, i):
        return bool(self.cond[i])


class RotturaCanale(Base):
    """I-03: close oltre il massimo (minimo) delle 50 barre precedenti; 4h; uscita dopo 30 barre."""
    tf, barre, stop_atr = "4h", 30, 2.0
    n = 50

    def __init__(self, direzione):
        self.direzione = direzione

    def prepara(self, d):
        super().prepara(d)
        n = self.n
        hh = q.rolling_max(d["high"], n)
        ll = q.rolling_min(d["low"], n)
        self.prev_hh = np.concatenate([[np.nan], hh[:-1]])
        self.prev_ll = np.concatenate([[np.nan], ll[:-1]])
        self.primo_indice = q.primo_finito(self.a, self.prev_hh)

    def condizione(self, i):
        if self.direzione == "long":
            return self.c[i] > self.prev_hh[i]
        return self.c[i] < self.prev_ll[i]


class RotturaVolatilita(Base):
    """I-04: apertura del giorno UTC +- 0,5 x escursione del giorno prima; 1h; uscita a fine giorno."""
    tf, stop_atr = "1h", 2.0
    k = 0.5

    def __init__(self, direzione):
        self.direzione = direzione

    def prepara(self, d):
        super().prepara(d)
        ore, _, _, giorno = _ora_e_giorno(d["ts"])
        self.ore = ore
        n = len(d["ts"])
        # massimo e minimo per giorno, e apertura (barra delle 00:00) per giorno
        hi, lo, ap = {}, {}, {}
        for k in range(n):
            g = giorno[k]
            hi[g] = max(hi.get(g, -np.inf), d["high"][k])
            lo[g] = min(lo.get(g, np.inf), d["low"][k])
            if ore[k] == 0:
                ap[g] = d["open"][k]
        self.cond = np.zeros(n, dtype=bool)
        s = 1 if self.direzione == "long" else -1
        gia = set()
        for k in range(n):
            g = giorno[k]
            if g not in ap or (g - 1) not in hi or ore[k] >= 23:
                continue
            livello = ap[g] + s * self.k * (hi[g - 1] - lo[g - 1])
            if g in gia:
                continue
            if s * (d["close"][k] - livello) > 0:
                gia.add(g)
                self.cond[k] = True
        # il giorno precedente e' completo solo alla fine di quel giorno: il livello di oggi usa
        # solo massimo e minimo di ieri (barre chiuse) e l'apertura di oggi (gia' nota).
        self.primo_indice = q.primo_finito(self.a)

    def condizione(self, i):
        return bool(self.cond[i])

    def esci(self, i, barre_tenute):
        return self.ore[i] == 23


class RSI2(Base):
    """I-05: Connors, RSI(2) con filtro SMA200 e uscita sulla SMA5; 4h; stop 3 ATR."""
    tf, stop_atr = "4h", 3.0

    def __init__(self, direzione):
        self.direzione = direzione

    def prepara(self, d):
        super().prepara(d)
        c = self.c
        self.s200 = q.sma(c, 200)
        self.s5 = q.sma(c, 5)
        self.r2 = q.rsi(c, 2)
        self.primo_indice = q.primo_finito(self.a, self.s200, self.r2)

    def condizione(self, i):
        if self.direzione == "long":
            return self.c[i] > self.s200[i] and self.r2[i] < 10
        return self.c[i] < self.s200[i] and self.r2[i] > 90

    def esci(self, i, barre_tenute):
        if self.direzione == "long":
            return self.c[i] > self.s5[i]
        return self.c[i] < self.s5[i]


class VolumeAnomalo(Base):
    """I-06: volume in USDT del giorno contro la media dei 20 giorni prima; uscita dopo 5 barre."""
    tf, barre, stop_atr = "1d", 5, 2.5

    def __init__(self, direzione, soglia):
        self.direzione = direzione
        self.soglia = soglia

    def prepara(self, d):
        super().prepara(d)
        v = d["vol_usdt"]
        m = q.sma(v, 20)
        self.media_prima = np.concatenate([[np.nan], m[:-1]])
        self.v = v
        self.primo_indice = q.primo_finito(self.a, self.media_prima)

    def condizione(self, i):
        if not np.isfinite(self.v[i]) or not np.isfinite(self.media_prima[i]):
            return False
        if self.direzione == "long":
            return self.v[i] > self.soglia * self.media_prima[i]
        return self.v[i] < self.soglia * self.media_prima[i]


class Lotteria(Base):
    """I-07: massimo dei rendimenti giornalieri delle ultime 7 barre; uscita dopo 3 barre."""
    tf, barre, stop_atr = "1d", 3, 2.5

    def __init__(self, direzione, soglia):
        self.direzione = direzione
        self.soglia = soglia

    def prepara(self, d):
        super().prepara(d)
        r = rendimenti(self.c)
        self.mx = q.rolling_max(np.nan_to_num(r, nan=-np.inf), 7)
        self.mx[:7] = np.nan
        self.primo_indice = q.primo_finito(self.a, self.mx)

    def condizione(self, i):
        if self.direzione == "short":
            return self.mx[i] >= self.soglia
        return self.mx[i] < self.soglia


class Funding(Base):
    """I-08: ultimo funding con istante <= chiusura della barra; 8h; uscita dopo 3 barre."""
    tf, barre, stop_atr = "8h", 3, 2.0

    def __init__(self, direzione):
        self.direzione = direzione

    def prepara(self, d):
        super().prepara(d)
        f = q.funding()
        fts = np.array([t for t, _ in f], dtype=np.int64)
        fr = np.array([r for _, r in f])
        chiusure = np.array([c.close_ts for c in d["candele"]], dtype=np.int64)
        idx = np.searchsorted(fts, chiusure, side="right") - 1
        self.ultimo = np.where(idx >= 0, fr[np.clip(idx, 0, None)], np.nan)
        self.primo_indice = q.primo_finito(self.a, self.ultimo)

    def condizione(self, i):
        if self.direzione == "short":
            return self.ultimo[i] >= 0.0005
        return self.ultimo[i] < 0


class Lunedi(Base):
    """I-09: segnale alla chiusura della domenica UTC, long il lunedi', uscita dopo 1 barra."""
    tf, barre, stop_atr, direzione = "1d", 1, 2.0, "long"

    def prepara(self, d):
        super().prepara(d)
        _, _, wd, _ = _ora_e_giorno(d["ts"])
        self.wd = wd

    def condizione(self, i):
        return self.wd[i] == 6


class Strettoia(Base):
    """I-10: Bollinger 20/2 con ampiezza nel quinto piu' basso delle ultime 120; 4h; uscita dopo 12."""
    tf, barre, stop_atr = "4h", 12, 2.0
    finestra = 120
    percentile = 20
    nb = 20     # barre delle bande
    kb = 2.0    # deviazioni standard della banda d'ingresso

    def __init__(self, direzione):
        self.direzione = direzione

    def prepara(self, d):
        super().prepara(d)
        c = self.c
        m = q.sma(c, self.nb)
        sd = q.rolling_std(c, self.nb)
        amp = 4 * sd / m
        p20 = np.full(len(c), np.nan)
        F = self.finestra
        for i in range(F - 1, len(c)):
            w = amp[i - F + 1:i + 1]
            if np.isfinite(w).all():
                p20[i] = np.percentile(w, self.percentile)
        self.m, self.sd, self.amp, self.p20 = m, sd, amp, p20
        self.primo_indice = q.primo_finito(self.a, self.p20)

    def condizione(self, i):
        if not (self.amp[i] <= self.p20[i]):
            return False
        if self.direzione == "long":
            return self.c[i] > self.m[i] + self.kb * self.sd[i]
        return self.c[i] < self.m[i] - self.kb * self.sd[i]


class BarraEstrema(Base):
    """I-11: rendimento della barra oltre 3 deviazioni delle 168 precedenti, contro; 1h; uscita dopo 6."""
    tf, barre, stop_atr = "1h", 6, 2.0

    def __init__(self, direzione):
        self.direzione = direzione

    def prepara(self, d):
        super().prepara(d)
        r = rendimenti(self.c)
        sd = q.rolling_std(np.nan_to_num(r), 168)
        self.sd_prima = np.concatenate([[np.nan], sd[:-1]])
        self.sd_prima[:169] = np.nan
        self.r = r
        self.primo_indice = q.primo_finito(self.a, self.sd_prima)

    def condizione(self, i):
        if self.direzione == "long":
            return self.r[i] < -3 * self.sd_prima[i]
        return self.r[i] > 3 * self.sd_prima[i]


class GiornoAnomalo(Base):
    """I-12: rendimento del giorno oltre media +- 1,5 deviazioni dei 30 precedenti; inerzia; 1 barra."""
    tf, barre, stop_atr = "1d", 1, 2.0

    def __init__(self, direzione):
        self.direzione = direzione

    def prepara(self, d):
        super().prepara(d)
        r = rendimenti(self.c)
        m = q.sma(np.nan_to_num(r), 30)
        sd = q.rolling_std(np.nan_to_num(r), 30)
        self.m_prima = np.concatenate([[np.nan], m[:-1]])
        self.sd_prima = np.concatenate([[np.nan], sd[:-1]])
        self.m_prima[:31] = np.nan
        self.sd_prima[:31] = np.nan
        self.r = r
        self.primo_indice = q.primo_finito(self.a, self.sd_prima)

    def condizione(self, i):
        if self.direzione == "long":
            return self.r[i] > self.m_prima[i] + 1.5 * self.sd_prima[i]
        return self.r[i] < self.m_prima[i] - 1.5 * self.sd_prima[i]


def quota_aggressivi_1d():
    """{ts: taker_buy_quote_volume / quote_volume} dalle candele 1d del last (colonne 10 e 7 del CSV)."""
    out = {}
    for anno, mese in q.dati.mesi_del_periodo(q.INIZIO, q.FINE):
        p = q.dati.percorso_mese(q.SIMBOLO, "klines", "1d", anno, mese, q.dati.RADICE_DEFAULT)
        if not p.is_file():
            continue
        for riga in q.dati.righe_csv_da_zip(p):
            ts = q.dati.normalizza_ts(riga[0])
            if ts in out or len(riga) < 11:
                continue
            qv, tb = float(riga[7]), float(riga[10])
            out[ts] = tb / qv if qv > 0 else np.nan
    return out


class Squilibrio(Base):
    """I-13: quota del volume degli acquirenti aggressivi del giorno contro 0,5; 1d; uscita dopo 1 barra."""
    tf, barre, stop_atr = "1d", 1, 2.0

    def __init__(self, direzione):
        self.direzione = direzione

    def prepara(self, d):
        super().prepara(d)
        qa = quota_aggressivi_1d()
        self.quota = np.array([qa.get(int(t), np.nan) for t in d["ts"]])

    def condizione(self, i):
        x = self.quota[i]
        if not np.isfinite(x):
            return False
        return x > 0.5 if self.direzione == "long" else x < 0.5


class NumeroTondo(Base):
    """I-14: chiusura oraria che attraversa un multiplo di 0,01; uscita dopo 6 barre."""
    tf, barre, stop_atr = "1h", 6, 2.0

    def __init__(self, direzione):
        self.direzione = direzione

    def prepara(self, d):
        super().prepara(d)
        c = self.c
        livello_prima = np.floor(np.concatenate([[np.nan], c[:-1]]) / 0.01)
        livello_ora = np.floor(c / 0.01)
        self.su = livello_ora > livello_prima
        self.giu = livello_ora < livello_prima

    def condizione(self, i):
        return bool(self.su[i]) if self.direzione == "long" else bool(self.giu[i])


class NR4(Base):
    """I-15: giorno UTC precedente con escursione minima delle ultime 4; rottura oraria; uscita a fine giorno."""
    tf, stop_atr = "1h", 2.0

    def __init__(self, direzione):
        self.direzione = direzione

    def prepara(self, d):
        super().prepara(d)
        ore, _, _, giorno = _ora_e_giorno(d["ts"])
        self.ore = ore
        n = len(d["ts"])
        hi, lo = {}, {}
        for k in range(n):
            g = giorno[k]
            hi[g] = max(hi.get(g, -np.inf), d["high"][k])
            lo[g] = min(lo.get(g, np.inf), d["low"][k])

        def nr4(g):
            if not all((g - j) in hi for j in range(4)):
                return False
            r = [hi[g - j] - lo[g - j] for j in range(4)]
            return r[0] < min(r[1:])

        self.cond = np.zeros(n, dtype=bool)
        s = 1 if self.direzione == "long" else -1
        gia = set()
        for k in range(n):
            g = giorno[k]
            if ore[k] >= 23 or g in gia or not nr4(g - 1):
                continue
            livello = hi[g - 1] if s == 1 else lo[g - 1]
            if s * (d["close"][k] - livello) > 0:
                gia.add(g)
                self.cond[k] = True

    def condizione(self, i):
        return bool(self.cond[i])

    def esci(self, i, barre_tenute):
        return self.ore[i] == 23


def dmi(d, n=14):
    """+DI, -DI e ADX di Wilder (medie di Wilder, causali)."""
    h, l, c = d["high"], d["low"], d["close"]
    N = len(c)
    up = np.zeros(N)
    dn = np.zeros(N)
    tr = np.zeros(N)
    for i in range(1, N):
        u, w = h[i] - h[i - 1], l[i - 1] - l[i]
        up[i] = u if (u > w and u > 0) else 0.0
        dn[i] = w if (w > u and w > 0) else 0.0
        tr[i] = max(h[i] - l[i], abs(h[i] - c[i - 1]), abs(l[i] - c[i - 1]))
    pdi = np.full(N, np.nan)
    mdi = np.full(N, np.nan)
    adx = np.full(N, np.nan)
    if N <= 2 * n:
        return pdi, mdi, adx
    s_tr, s_up, s_dn = tr[1:n + 1].sum(), up[1:n + 1].sum(), dn[1:n + 1].sum()
    dx = np.full(N, np.nan)
    for i in range(n, N):
        if i > n:
            s_tr = s_tr - s_tr / n + tr[i]
            s_up = s_up - s_up / n + up[i]
            s_dn = s_dn - s_dn / n + dn[i]
        if s_tr > 0:
            pdi[i] = 100 * s_up / s_tr
            mdi[i] = 100 * s_dn / s_tr
            somma = pdi[i] + mdi[i]
            dx[i] = 100 * abs(pdi[i] - mdi[i]) / somma if somma > 0 else 0.0
    adx[2 * n - 1] = np.nanmean(dx[n:2 * n])
    for i in range(2 * n, N):
        adx[i] = (adx[i - 1] * (n - 1) + dx[i]) / n
    return pdi, mdi, adx


class Direzionale(Base):
    """I-16: incrocio +DI/-DI con ADX > 25; uscita all'incrocio opposto; 4h; stop 2,5 ATR."""
    tf, stop_atr = "4h", 2.5

    def __init__(self, direzione):
        self.direzione = direzione

    def prepara(self, d):
        super().prepara(d)
        self.p, self.m, self.adx = dmi(d)
        self.primo_indice = q.primo_finito(self.a, self.adx) + 1

    def condizione(self, i):
        p, m = self.p, self.m
        if self.direzione == "long":
            return p[i] > m[i] and p[i - 1] <= m[i - 1] and self.adx[i] > 25
        return m[i] > p[i] and m[i - 1] <= p[i - 1] and self.adx[i] > 25

    def esci(self, i, barre_tenute):
        if self.direzione == "long":
            return self.m[i] > self.p[i]
        return self.p[i] > self.m[i]


def allentata(classe, direzione, **attributi):
    """Variante allentata di un'idea: stessa classe con attributi di classe diversi (tf, n, barre, k)."""
    v = classe(direzione)
    for k, val in attributi.items():
        setattr(v, k, val)
    return v


class GiornoAnomaloK(GiornoAnomalo):
    k = 1.5

    def condizione(self, i):
        if self.direzione == "long":
            return self.r[i] > self.m_prima[i] + self.k * self.sd_prima[i]
        return self.r[i] < self.m_prima[i] - self.k * self.sd_prima[i]


VARIANTI = {
    "DOGEUSDT-040": lambda: allentata(Strettoia, "short", tf="1h", barre=24),
    "DOGEUSDT-041": lambda: allentata(Strettoia, "short", tf="1h", stop_atr=3.0),
    "DOGEUSDT-042": lambda: allentata(Strettoia, "short", tf="1h", stop_atr=3.0, finestra=480),
    "DOGEUSDT-043": lambda: allentata(Strettoia, "short", tf="1h", stop_atr=3.0, percentile=10),
    "DOGEUSDT-044": lambda: allentata(Strettoia, "short", tf="1h", stop_atr=4.0),
    "DOGEUSDT-032": lambda: allentata(RotturaCanale, "long", n=20, barre=12),
    "DOGEUSDT-033": lambda: allentata(RotturaCanale, "short", n=20, barre=12),
    "DOGEUSDT-034": lambda: allentata(Strettoia, "long", tf="1h"),
    "DOGEUSDT-035": lambda: allentata(Strettoia, "short", tf="1h"),
    "DOGEUSDT-036": lambda: allentata(GiornoAnomaloK, "long", k=1.0),
    "DOGEUSDT-037": lambda: allentata(GiornoAnomaloK, "short", k=1.0),
    "DOGEUSDT-038": lambda: allentata(Direzionale, "long", tf="1h"),
    "DOGEUSDT-039": lambda: allentata(Direzionale, "short", tf="1h"),
    "DOGEUSDT-030": lambda: Direzionale("long"),
    "DOGEUSDT-031": lambda: Direzionale("short"),
    "DOGEUSDT-024": lambda: Squilibrio("long"),
    "DOGEUSDT-025": lambda: Squilibrio("short"),
    "DOGEUSDT-026": lambda: NumeroTondo("long"),
    "DOGEUSDT-027": lambda: NumeroTondo("short"),
    "DOGEUSDT-028": lambda: NR4("long"),
    "DOGEUSDT-029": lambda: NR4("short"),
    "DOGEUSDT-001": lambda: Momento7("long"),
    "DOGEUSDT-002": lambda: Momento7("short"),
    "DOGEUSDT-003": lambda: PrimaMezzora("long"),
    "DOGEUSDT-004": lambda: PrimaMezzora("short"),
    "DOGEUSDT-005": lambda: RotturaCanale("long"),
    "DOGEUSDT-006": lambda: RotturaCanale("short"),
    "DOGEUSDT-007": lambda: RotturaVolatilita("long"),
    "DOGEUSDT-008": lambda: RotturaVolatilita("short"),
    "DOGEUSDT-009": lambda: RSI2("long"),
    "DOGEUSDT-010": lambda: RSI2("short"),
    "DOGEUSDT-011": lambda: VolumeAnomalo("long", 1.5),
    "DOGEUSDT-012": lambda: VolumeAnomalo("short", 0.6),
    "DOGEUSDT-013": lambda: Lotteria("short", 0.10),
    "DOGEUSDT-014": lambda: Lotteria("long", 0.03),
    "DOGEUSDT-015": lambda: Funding("short"),
    "DOGEUSDT-016": lambda: Funding("long"),
    "DOGEUSDT-017": lambda: Lunedi(),
    "DOGEUSDT-018": lambda: Strettoia("long"),
    "DOGEUSDT-019": lambda: Strettoia("short"),
    "DOGEUSDT-020": lambda: BarraEstrema("long"),
    "DOGEUSDT-021": lambda: BarraEstrema("short"),
    "DOGEUSDT-022": lambda: GiornoAnomalo("long"),
    "DOGEUSDT-023": lambda: GiornoAnomalo("short"),
}
