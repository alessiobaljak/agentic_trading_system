"""Le varianti della campagna DYDXUSDT, scritte come in ipotesi.md PRIMA del loro test.

Ogni variante e' una funzione ``crea_spec(ctx) -> Spec`` (vedi comune.py): calcolo del segnale
(direzione, stop, target) senza la condizione d'ingresso, condizione d'ingresso, uscita.
Il registro ``VARIANTI`` porta per ognuna: timeframe, direzione, idea, parametri, previsione e
criterio di successo, cosi' come vanno nel log.
"""
from __future__ import annotations

import math
from datetime import datetime, timezone
from typing import Callable, Dict

import numpy as np

from comune import (Contesto, Segnale, Spec, atr, barre_in_posizione, funding_ultimo, massimo_precedente,
                    minimo_precedente, quota_acquisti_taker, rendimento, rsi, sma)


# ---------------------------------------------------------------------------
# Mattoni
# ---------------------------------------------------------------------------

def segnale_atr(ctx: Contesto, direzione: str, k: float, riscaldamento: int, n_atr: int = 14):
    """Stop a k volte l'ATR di Wilder dal close della barra del segnale; nessun target."""
    a = atr(ctx, n_atr)

    def s(i: int):
        if i < riscaldamento or not np.isfinite(a[i]) or a[i] <= 0:
            return None
        stop = ctx.c[i] - k * a[i] if direzione == "long" else ctx.c[i] + k * a[i]
        if stop <= 0:
            return None
        return Segnale(direzione, float(stop))
    return s


def uscita_tempo(ctx: Contesto, barre: int):
    def e(i, pos):
        return barre_in_posizione(ctx, i, pos) >= barre
    return e


def _ora(ts: int) -> datetime:
    return datetime.fromtimestamp(ts / 1000, tz=timezone.utc)


# ---------------------------------------------------------------------------
# Controllo positivo (nota, non variante): legge di proposito la barra successiva
# ---------------------------------------------------------------------------

def controllo_positivo(ctx: Contesto) -> Spec:
    sig = segnale_atr(ctx, "long", 2.0, 14)

    def cond(i):
        return i + 1 < ctx.n and ctx.c[i + 1] > ctx.o[i + 1]  # LOOKAHEAD DICHIARATO

    return Spec(sig, cond, uscita_tempo(ctx, 1))


# ---------------------------------------------------------------------------
# I-01 Momento della serie (1d)
# ---------------------------------------------------------------------------

def _i01(direzione):
    def crea(ctx: Contesto) -> Spec:
        r7 = rendimento(ctx.c, 7)
        sig = segnale_atr(ctx, direzione, 2.0, 14)

        def cond(i):
            return np.isfinite(r7[i]) and (r7[i] > 0 if direzione == "long" else r7[i] < 0)
        return Spec(sig, cond, uscita_tempo(ctx, 3))
    return crea


# ---------------------------------------------------------------------------
# I-02 Rottura del canale di 50 barre (4h)
# ---------------------------------------------------------------------------

def _i02(direzione):
    def crea(ctx: Contesto) -> Spec:
        hi = massimo_precedente(ctx.h, 50)
        lo = minimo_precedente(ctx.l, 50)
        sig = segnale_atr(ctx, direzione, 2.0, 50)

        def cond(i):
            if direzione == "long":
                return np.isfinite(hi[i]) and ctx.c[i] > hi[i]
            return np.isfinite(lo[i]) and ctx.c[i] < lo[i]
        return Spec(sig, cond, uscita_tempo(ctx, 10))
    return crea


# ---------------------------------------------------------------------------
# I-03 RSI a 2 barre con filtro della media a 200 (1h)
# ---------------------------------------------------------------------------

def _i03(direzione):
    def crea(ctx: Contesto) -> Spec:
        m200 = sma(ctx.c, 200)
        m5 = sma(ctx.c, 5)
        r2 = rsi(ctx.c, 2)
        sig = segnale_atr(ctx, direzione, 3.0, 200)

        def cond(i):
            if not (np.isfinite(m200[i]) and np.isfinite(r2[i])):
                return False
            if direzione == "long":
                return ctx.c[i] > m200[i] and r2[i] < 10
            return ctx.c[i] < m200[i] and r2[i] > 90

        def esci(i, pos):
            if direzione == "long":
                return ctx.c[i] > m5[i]
            return ctx.c[i] < m5[i]
        return Spec(sig, cond, esci)
    return crea


# ---------------------------------------------------------------------------
# I-04 Momento intragiornaliero: prima mezz'ora UTC -> ultima mezz'ora (30m)
# ---------------------------------------------------------------------------

def _i04(direzione):
    def crea(ctx: Contesto) -> Spec:
        sig = segnale_atr(ctx, direzione, 2.0, 14)
        indice_ts = {int(t): k for k, t in enumerate(ctx.ts)}

        def cond(i):
            g = _ora(int(ctx.ts[i]))
            if not (g.hour == 23 and g.minute == 0):
                return False
            mezzanotte = int(ctx.ts[i]) - 23 * 3_600_000
            j = indice_ts.get(mezzanotte)
            if j is None:
                return False
            r = ctx.c[j] / ctx.o[j] - 1.0
            return r > 0 if direzione == "long" else r < 0
        return Spec(sig, cond, uscita_tempo(ctx, 1))
    return crea


# ---------------------------------------------------------------------------
# I-05 Ritorno dopo un movimento forte con volume alto (1h)
# ---------------------------------------------------------------------------

def _i05(direzione):
    def crea(ctx: Contesto) -> Spec:
        a = atr(ctx, 14)
        sig = segnale_atr(ctx, direzione, 2.0, 25)
        v = ctx.volume_usdt

        def cond(i):
            if i < 25 or not np.isfinite(a[i - 1]):
                return False
            media_v = np.nanmean(v[i - 24:i])
            if not (np.isfinite(v[i]) and np.isfinite(media_v) and media_v > 0):
                return False
            r1 = ctx.c[i] / ctx.c[i - 1] - 1.0
            soglia = 2.0 * a[i - 1] / ctx.c[i - 1]
            volume_alto = v[i] > 3.0 * media_v
            if direzione == "long":
                return volume_alto and r1 < -soglia
            return volume_alto and r1 > soglia
        return Spec(sig, cond, uscita_tempo(ctx, 12))
    return crea


# ---------------------------------------------------------------------------
# I-06 Funding affollato (8h)
# ---------------------------------------------------------------------------

def _i06(direzione):
    def crea(ctx: Contesto) -> Spec:
        f = funding_ultimo(ctx)
        sig = segnale_atr(ctx, direzione, 2.0, 14)

        def cond(i):
            if not np.isfinite(f[i]):
                return False
            return f[i] >= 0.0003 if direzione == "short" else f[i] <= -0.0003
        return Spec(sig, cond, uscita_tempo(ctx, 3))
    return crea


# ---------------------------------------------------------------------------
# I-07 Lunedi' (1d)
# ---------------------------------------------------------------------------

def _i07(ctx: Contesto) -> Spec:
    sig = segnale_atr(ctx, "long", 2.0, 14)

    def cond(i):
        return _ora(int(ctx.ts[i])).weekday() == 6  # barra della domenica: si entra all'apertura del lunedi'
    return Spec(sig, cond, uscita_tempo(ctx, 1))


# ---------------------------------------------------------------------------
# I-08 BTC guida, DYDX segue (1h)
# ---------------------------------------------------------------------------

def _i08(direzione):
    def crea(ctx: Contesto) -> Spec:
        b = ctx.btc
        rb = np.full(ctx.n, np.nan)
        rb[1:] = b[1:] / b[:-1] - 1.0
        sd = np.full(ctx.n, np.nan)
        for i in range(169, ctx.n):
            finestra = rb[i - 168:i]
            if np.isfinite(finestra).sum() >= 100:
                sd[i] = np.nanstd(finestra)
        sig = segnale_atr(ctx, direzione, 2.0, 170)

        def cond(i):
            if i < 170 or not (np.isfinite(rb[i]) and np.isfinite(sd[i]) and sd[i] > 0):
                return False
            rd = ctx.c[i] / ctx.c[i - 1] - 1.0
            if direzione == "long":
                return rb[i] > 2.0 * sd[i] and rd < rb[i]
            return rb[i] < -2.0 * sd[i] and rd > rb[i]
        return Spec(sig, cond, uscita_tempo(ctx, 3))
    return crea


# ---------------------------------------------------------------------------
# I-09 Numeri tondi (1h)
# ---------------------------------------------------------------------------

def livelli_attraversati(p0: float, p1: float):
    """Livelli tondi L con min(p0,p1) < L <= max(p0,p1): multipli di 0,5 sotto 10, multipli di 5 da 10 in su."""
    basso, alto = min(p0, p1), max(p0, p1)
    out = []
    k = math.floor(basso / 0.5) + 1
    while k * 0.5 <= alto and k * 0.5 < 10:
        out.append(k * 0.5)
        k += 1
    k = max(2, math.floor(basso / 5) + 1)
    while k * 5 <= alto:
        if k * 5 > basso:
            out.append(k * 5.0)
        k += 1
    return out


def _i09(direzione):
    def crea(ctx: Contesto) -> Spec:
        sig = segnale_atr(ctx, direzione, 2.0, 14)

        def cond(i):
            if i < 1:
                return False
            p0, p1 = ctx.c[i - 1], ctx.c[i]
            if direzione == "long":
                return p1 > p0 and any(p0 < L <= p1 for L in livelli_attraversati(p0, p1))
            return p1 < p0 and any(p1 <= L < p0 for L in livelli_attraversati(p1 - 1e-12, p0 - 1e-12))
        return Spec(sig, cond, uscita_tempo(ctx, 4))
    return crea


# ---------------------------------------------------------------------------
# I-10 Barra stretta (la piu' stretta di 7) e rottura (4h)
# ---------------------------------------------------------------------------

def _i10(direzione):
    def crea(ctx: Contesto) -> Spec:
        rng = ctx.h - ctx.l
        nr7 = np.zeros(ctx.n, dtype=bool)
        for j in range(6, ctx.n):
            nr7[j] = rng[j] < rng[j - 6:j].min()

        def sig(i):
            if i < 7:
                return None
            stop = ctx.l[i - 1] if direzione == "long" else ctx.h[i - 1]
            if stop <= 0:
                return None
            return Segnale(direzione, float(stop))

        def cond(i):
            if i < 7 or not nr7[i - 1]:
                return False
            return ctx.c[i] > ctx.h[i - 1] if direzione == "long" else ctx.c[i] < ctx.l[i - 1]
        return Spec(sig, cond, uscita_tempo(ctx, 6))
    return crea


# ---------------------------------------------------------------------------
# I-11 Squilibrio degli ordini dei taker (1d)
# ---------------------------------------------------------------------------

def _i11(direzione):
    def crea(ctx: Contesto) -> Spec:
        q = quota_acquisti_taker(ctx)
        sig = segnale_atr(ctx, direzione, 2.0, 14)

        def cond(i):
            if not np.isfinite(q[i]):
                return False
            sq = 2.0 * q[i] - 1.0
            return sq > 0 if direzione == "long" else sq < 0
        return Spec(sig, cond, uscita_tempo(ctx, 1))
    return crea


# ---------------------------------------------------------------------------
# Varianti aggiunte dopo gli scarti (ipotesi.md, 2026-10-09 17:47 UTC)
# ---------------------------------------------------------------------------

def _i05b(direzione, k_mov=1.5, k_vol=2.0):
    def crea(ctx: Contesto) -> Spec:
        a = atr(ctx, 14)
        sig = segnale_atr(ctx, direzione, 2.0, 25)
        v = ctx.volume_usdt

        def cond(i):
            if i < 25 or not np.isfinite(a[i - 1]):
                return False
            media_v = np.nanmean(v[i - 24:i])
            if not (np.isfinite(v[i]) and np.isfinite(media_v) and media_v > 0):
                return False
            r1 = ctx.c[i] / ctx.c[i - 1] - 1.0
            soglia = k_mov * a[i - 1] / ctx.c[i - 1]
            volume_alto = v[i] > k_vol * media_v
            if direzione == "long":
                return volume_alto and r1 < -soglia
            return volume_alto and r1 > soglia
        return Spec(sig, cond, uscita_tempo(ctx, 12))
    return crea


def _i06b(direzione):
    def crea(ctx: Contesto) -> Spec:
        f = funding_ultimo(ctx)
        sig = segnale_atr(ctx, direzione, 2.0, 14)

        def cond(i):
            if not np.isfinite(f[i]):
                return False
            return f[i] > 0.0001 if direzione == "short" else f[i] < 0.0
        return Spec(sig, cond, uscita_tempo(ctx, 3))
    return crea


def _i12(direzione, finestra=168, z_soglia=2.0, uscita=4):
    def crea(ctx: Contesto) -> Spec:
        mark = np.array([m.close for m in ctx.candele_mark])
        sc = ctx.c / mark - 1.0
        z = np.full(ctx.n, np.nan)
        for i in range(finestra, ctx.n):
            w = sc[i - finestra:i]
            sd = w.std()
            if sd > 0:
                z[i] = (sc[i] - w.mean()) / sd
        sig = segnale_atr(ctx, direzione, 2.0, finestra)

        def cond(i):
            if not np.isfinite(z[i]):
                return False
            return z[i] > z_soglia if direzione == "short" else z[i] < -z_soglia
        return Spec(sig, cond, uscita_tempo(ctx, uscita))
    return crea


def _i10_stop_atr(direzione, k_stop=2.0, uscita=6):
    """Ritocco di I-10: stessa condizione, stop a k ATR(14) dal close invece del lato della barra stretta."""
    def crea(ctx: Contesto) -> Spec:
        rng = ctx.h - ctx.l
        nr7 = np.zeros(ctx.n, dtype=bool)
        for j in range(6, ctx.n):
            nr7[j] = rng[j] < rng[j - 6:j].min()
        sig = segnale_atr(ctx, direzione, k_stop, 14)

        def cond(i):
            if i < 7 or not nr7[i - 1]:
                return False
            return ctx.c[i] > ctx.h[i - 1] if direzione == "long" else ctx.c[i] < ctx.l[i - 1]
        return Spec(sig, cond, uscita_tempo(ctx, uscita))
    return crea


def _i10_uscita(direzione, uscita):
    """Ritocco di I-10: stop originale (lato della barra stretta), tenuta diversa."""
    def crea(ctx: Contesto) -> Spec:
        base = _i10(direzione)(ctx)
        return Spec(base.segnale, base.condizione, uscita_tempo(ctx, uscita))
    return crea


def _i10_volume_basso(direzione, uscita=6, finestra=20):
    """Ritocco di I-10: come 013, solo se il volume in USDT della barra del segnale non supera la media delle 20 prima."""
    def crea(ctx: Contesto) -> Spec:
        base = _i10(direzione)(ctx)
        v = ctx.volume_usdt

        def cond(i):
            if i < finestra or not base.condizione(i):
                return False
            media = v[i - finestra:i].mean()
            return bool(np.isfinite(v[i]) and np.isfinite(media) and v[i] <= media)

        def sig(i):
            return base.segnale(i) if i >= finestra else None
        return Spec(sig, cond, uscita_tempo(ctx, uscita))
    return crea


def _i10_volume_basso_trend(direzione, uscita=6, finestra=20, media=50):
    """Ritocco di 024: in piu' il close della barra del segnale sotto (short) o sopra (long) la media a 50."""
    def crea(ctx: Contesto) -> Spec:
        base = _i10_volume_basso(direzione, uscita, finestra)(ctx)
        m = sma(ctx.c, media)

        def cond(i):
            if i < media or not np.isfinite(m[i]) or not base.condizione(i):
                return False
            return ctx.c[i] < m[i] if direzione == "short" else ctx.c[i] > m[i]

        def sig(i):
            return base.segnale(i) if i >= media else None
        return Spec(sig, cond, base.esci)
    return crea


def segnale_pct(ctx: Contesto, direzione: str, pct: float, riscaldamento: int):
    """Stop a una percentuale fissa dal close della barra del segnale; nessun target."""
    def s(i: int):
        if i < riscaldamento:
            return None
        stop = ctx.c[i] * (1 - pct) if direzione == "long" else ctx.c[i] * (1 + pct)
        return Segnale(direzione, float(stop))
    return s


def _con_stop_pct(crea_base, direzione, pct, riscaldamento=14):
    """Ritocco dello stop: stessa condizione e uscita, stop a pct dal close."""
    def crea(ctx: Contesto) -> Spec:
        base = crea_base(ctx)
        return Spec(segnale_pct(ctx, direzione, pct, riscaldamento), base.condizione, base.esci)
    return crea


def _con_uscita(crea_base, barre):
    """Ritocco della tenuta: stessa condizione e stesso stop, uscita dopo ``barre`` barre."""
    def crea(ctx: Contesto) -> Spec:
        base = crea_base(ctx)
        return Spec(base.segnale, base.condizione, uscita_tempo(ctx, barre))
    return crea


def _i11_soglia(direzione, soglia):
    """Ritocco di I-11: soglia diversa sulla quota degli acquisti dei taker."""
    def crea(ctx: Contesto) -> Spec:
        base = _i11(direzione)(ctx)
        q = quota_acquisti_taker(ctx)

        def cond(i):
            if not np.isfinite(q[i]):
                return False
            return q[i] < soglia if direzione == "short" else q[i] > soglia
        return Spec(base.segnale, cond, base.esci)
    return crea


CREA: Dict[str, Callable] = {
    "I11_short_soglia049": _i11_soglia("short", 0.49),
    "I11_short_soglia048": _i11_soglia("short", 0.48),
    "I11_short_soglia049_uscita2": _con_uscita(_i11_soglia("short", 0.49), 2),
    "I11_short_uscita2": _con_uscita(_i11("short"), 2),
    "I11_short_stop6": _con_stop_pct(_i11("short"), "short", 0.06),
    "I10_short_volume_basso_uscita12": _i10_volume_basso("short", uscita=12),
    "I10_short_volume_basso_trend": _i10_volume_basso_trend("short"),
    "I10_short_volume_basso": _i10_volume_basso("short"),
    "I10_short_stop2atr": _i10_stop_atr("short"),
    "I10_short_uscita12": _i10_uscita("short", 12),
    "I02h_long": _i02("long"), "I02h_short": _i02("short"),
    "I05b_long": _i05b("long"), "I05b_short": _i05b("short"),
    "I06b_short": _i06b("short"), "I06b_long": _i06b("long"),
    "I12_short": _i12("short"), "I12_long": _i12("long"),
    "controllo_positivo": controllo_positivo,
    "I01_long": _i01("long"), "I01_short": _i01("short"),
    "I02_long": _i02("long"), "I02_short": _i02("short"),
    "I03_long": _i03("long"), "I03_short": _i03("short"),
    "I04_long": _i04("long"), "I04_short": _i04("short"),
    "I05_long": _i05("long"), "I05_short": _i05("short"),
    "I06_short": _i06("short"), "I06_long": _i06("long"),
    "I07_long": _i07,
    "I08_long": _i08("long"), "I08_short": _i08("short"),
    "I09_long": _i09("long"), "I09_short": _i09("short"),
    "I10_long": _i10("long"), "I10_short": _i10("short"),
    "I11_long": _i11("long"), "I11_short": _i11("short"),
}
