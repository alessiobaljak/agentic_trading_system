"""Le varianti di FTMUSDT, scritte come in ipotesi.md. Ogni funzione restituisce una ``Variante``."""
from __future__ import annotations

import bisect
import math
from datetime import datetime, timezone

import numpy as np

import indicatori as ind
from comune import motore
from quadro import Variante, barre_tenute

Segnale = motore.Segnale


def _ok(*xs) -> bool:
    return all(x is not None and not (isinstance(x, float) and math.isnan(x)) for x in xs)


def _segnale_atr(direzione: str, k: float):
    def segnale(ctx, i):
        a = ctx["atr"][i]
        c = ctx["serie"].c[i]
        if not _ok(a) or a <= 0:
            return None
        stop = c - k * a if direzione == "long" else c + k * a
        if stop <= 0:
            return None
        return Segnale(direzione, stop)
    return segnale


def _uscita_tempo(n: int):
    def uscita(ctx, i, pos):
        return "chiudi" if barre_tenute(ctx, i, pos) >= n else None
    return uscita


# ---------------------------------------------------------------------------
# Controllo positivo degli strumenti (lezioni/metodo.md): guarda di proposito la barra dopo
# ---------------------------------------------------------------------------

def controllo_positivo():
    def prepara(s):
        return {"atr": ind.atr(s, 24)}

    def condizione(ctx, i):
        s = ctx["serie"]
        return i + 1 < len(s.c) and s.c[i + 1] > s.o[i + 1]  # SGUARDO AL FUTURO, voluto

    return Variante("CONTROLLO", "1h", "long", prepara, condizione, _segnale_atr("long", 2.0), _uscita_tempo(1))


# ---------------------------------------------------------------------------
# I-01 momento della serie temporale (1d)
# ---------------------------------------------------------------------------

def i01(id_, direzione):
    def prepara(s):
        return {"atr": ind.atr(s, 14), "r14": ind.rendimento(s.c, 14)}

    def condizione(ctx, i):
        r = ctx["r14"][i]
        if not _ok(r):
            return False
        return r > 0 if direzione == "long" else r < 0

    return Variante(id_, "1d", direzione, prepara, condizione, _segnale_atr(direzione, 2.5), _uscita_tempo(5))


# ---------------------------------------------------------------------------
# I-02 rottura del canale di Donchian (4h)
# ---------------------------------------------------------------------------

def i02(id_, direzione, tf="4h"):
    def prepara(s):
        return {"atr": ind.atr(s, 20), "max20": ind.massimo_precedente(s.h, 20), "min20": ind.minimo_precedente(s.l, 20),
                "max10": ind.massimo_precedente(s.h, 10), "min10": ind.minimo_precedente(s.l, 10)}

    def condizione(ctx, i):
        c = ctx["serie"].c[i]
        if direzione == "long":
            return _ok(ctx["max20"][i]) and c > ctx["max20"][i]
        return _ok(ctx["min20"][i]) and c < ctx["min20"][i]

    def uscita(ctx, i, pos):
        c = ctx["serie"].c[i]
        if direzione == "long":
            return "chiudi" if _ok(ctx["min10"][i]) and c < ctx["min10"][i] else None
        return "chiudi" if _ok(ctx["max10"][i]) and c > ctx["max10"][i] else None

    return Variante(id_, tf, direzione, prepara, condizione, _segnale_atr(direzione, 2.0), uscita)


# ---------------------------------------------------------------------------
# I-03 ritorno dopo un movimento estremo (1h)
# ---------------------------------------------------------------------------

def i03(id_, direzione):
    def prepara(s):
        lr = ind.log_rend(s.c)
        sd = ind.dev_std_mobile(lr, 720)
        r3 = np.full(len(s.c), np.nan)
        r3[3:] = np.log(s.c[3:] / s.c[:-3])
        return {"atr": ind.atr(s, 24), "z": r3 / (sd * math.sqrt(3))}

    def condizione(ctx, i):
        z = ctx["z"][i]
        if not _ok(z):
            return False
        return z < -3 if direzione == "long" else z > 3

    return Variante(id_, "1h", direzione, prepara, condizione, _segnale_atr(direzione, 2.0), _uscita_tempo(6))


# ---------------------------------------------------------------------------
# I-04 funding estremo (8h)
# ---------------------------------------------------------------------------

def funding_per_barra(s):
    """Ultimo funding con settlement <= chiusura della barra, e i suoi percentili sulle ultime 270 settlement."""
    f_ts = [t for t, _ in s.funding]
    f_val = np.array([r for _, r in s.funding])
    p90 = ind.percentile_mobile(f_val, 270, 0.90)
    p10 = ind.percentile_mobile(f_val, 270, 0.10)
    n = len(s.c)
    f, q90, q10 = np.full(n, np.nan), np.full(n, np.nan), np.full(n, np.nan)
    for i in range(n):
        chiusura = int(s.ts[i]) + {"8h": 28_800_000}.get(s.tf, 0) - 1
        k = bisect.bisect_right(f_ts, chiusura) - 1
        if k >= 0:
            f[i], q90[i], q10[i] = f_val[k], p90[k], p10[k]
    return f, q90, q10


def i04(id_, direzione):
    def prepara(s):
        f, q90, q10 = funding_per_barra(s)
        return {"atr": ind.atr(s, 21), "f": f, "q90": q90, "q10": q10}

    def condizione(ctx, i):
        f = ctx["f"][i]
        if direzione == "short":
            return _ok(f, ctx["q90"][i]) and f > 0.0001 and f >= ctx["q90"][i]
        return _ok(f, ctx["q10"][i]) and f < 0 and f <= ctx["q10"][i]

    return Variante(id_, "8h", direzione, prepara, condizione, _segnale_atr(direzione, 2.0), _uscita_tempo(3))


# ---------------------------------------------------------------------------
# I-05 lunedi' (1d)
# ---------------------------------------------------------------------------

def i05(id_):
    def prepara(s):
        dom = np.array([datetime.fromtimestamp(int(t) / 1000, tz=timezone.utc).weekday() == 6 for t in s.ts])
        return {"atr": ind.atr(s, 14), "domenica": dom}

    def condizione(ctx, i):
        return bool(ctx["domenica"][i])

    return Variante(id_, "1d", "long", prepara, condizione, _segnale_atr("long", 2.0), _uscita_tempo(1))


# ---------------------------------------------------------------------------
# I-06 rottura di volatilita' della giornata (1h)
# ---------------------------------------------------------------------------

def _giorni(s):
    return (s.ts // 86_400_000).astype(np.int64)


def i06(id_, direzione):
    def prepara(s):
        g = _giorni(s)
        n = len(s.c)
        apertura = np.full(n, np.nan)
        range_prec = np.full(n, np.nan)
        soglia_gia = np.zeros(n, dtype=bool)  # una barra precedente della stessa giornata ha gia' chiuso oltre la soglia
        ultima = np.zeros(n, dtype=bool)
        # high e low di ogni giornata; si usano solo dal giorno DOPO (giornata gia' chiusa)
        alto, basso = {}, {}
        for i in range(n):
            alto[g[i]] = max(alto.get(g[i], -np.inf), s.h[i])
            basso[g[i]] = min(basso.get(g[i], np.inf), s.l[i])
        primo_ts, primo_open = {}, {}
        for i in range(n):
            primo_ts.setdefault(g[i], int(s.ts[i]))
            primo_open.setdefault(g[i], s.o[i])
            ultima[i] = (int(s.ts[i]) // 3_600_000) % 24 == 23
            # l'apertura della giornata e' nota solo se c'e' la barra delle 00:00
            apertura[i] = primo_open[g[i]] if primo_ts[g[i]] % 86_400_000 == 0 else np.nan
            if g[i] - 1 in alto:
                range_prec[i] = alto[g[i] - 1] - basso[g[i] - 1]
        segno = 1 if direzione == "long" else -1
        soglia = apertura + segno * 0.5 * range_prec
        oltre = segno * (s.c - soglia) > 0
        visto = {}
        for i in range(n):
            soglia_gia[i] = visto.get(g[i], False)
            if oltre[i] and not np.isnan(soglia[i]):
                visto[g[i]] = True
        return {"atr": ind.atr(s, 24), "oltre": oltre & ~np.isnan(soglia), "gia": soglia_gia, "ultima": ultima}

    def condizione(ctx, i):
        return bool(ctx["oltre"][i] and not ctx["gia"][i] and not ctx["ultima"][i])

    def uscita(ctx, i, pos):
        return "chiudi" if ctx["ultima"][i] else None

    return Variante(id_, "1h", direzione, prepara, condizione, _segnale_atr(direzione, 2.0), uscita)


# ---------------------------------------------------------------------------
# I-07 RSI a 2 dentro il trend (4h)
# ---------------------------------------------------------------------------

def i07(id_, direzione):
    def prepara(s):
        return {"atr": ind.atr(s, 20), "m200": ind.media_mobile(s.c, 200), "m5": ind.media_mobile(s.c, 5),
                "rsi": ind.rsi_semplice(s.c, 2)}

    def condizione(ctx, i):
        c, m, r = ctx["serie"].c[i], ctx["m200"][i], ctx["rsi"][i]
        if not _ok(m, r):
            return False
        return (c > m and r < 10) if direzione == "long" else (c < m and r > 90)

    def uscita(ctx, i, pos):
        c, m5 = ctx["serie"].c[i], ctx["m5"][i]
        if not _ok(m5):
            return None
        return "chiudi" if ((c > m5) if direzione == "long" else (c < m5)) else None

    return Variante(id_, "4h", direzione, prepara, condizione, _segnale_atr(direzione, 3.0), uscita)


# ---------------------------------------------------------------------------
# I-08 BTC prima di FTM (1h)
# ---------------------------------------------------------------------------

def i08(id_, direzione):
    def prepara(s):
        from quadro import carica_btc
        btc = carica_btc("1h")
        n = len(s.c)
        rb = np.full(n, np.nan)
        for i in range(1, n):
            a, b = btc.get(int(s.ts[i - 1])), btc.get(int(s.ts[i]))
            if a and b and s.ts[i] - s.ts[i - 1] == 3_600_000:
                rb[i] = math.log(b / a)
        # dev. std dei rendimenti di BTC sulle ultime 720 barre (della serie di BTC, non di quella di FTM)
        ts_btc = sorted(btc)
        lr_btc = np.full(len(ts_btc), np.nan)
        for k in range(1, len(ts_btc)):
            if ts_btc[k] - ts_btc[k - 1] == 3_600_000:
                lr_btc[k] = math.log(btc[ts_btc[k]] / btc[ts_btc[k - 1]])
        sd_btc_ser = ind.dev_std_mobile(np.nan_to_num(lr_btc, nan=0.0), 720)
        pos_btc = {t: k for k, t in enumerate(ts_btc)}
        sb = np.array([sd_btc_ser[pos_btc[int(t)]] if int(t) in pos_btc else np.nan for t in s.ts])
        rf = ind.log_rend(s.c)
        rf[1:][np.diff(s.ts) != 3_600_000] = np.nan
        return {"atr": ind.atr(s, 24), "rb": rb, "sb": sb, "rf": rf}

    def condizione(ctx, i):
        rb, sb, rf = ctx["rb"][i], ctx["sb"][i], ctx["rf"][i]
        if not _ok(rb, sb, rf):
            return False
        return (rb > 2 * sb and rf < rb) if direzione == "long" else (rb < -2 * sb and rf > rb)

    return Variante(id_, "1h", direzione, prepara, condizione, _segnale_atr(direzione, 2.0), _uscita_tempo(3))


# ---------------------------------------------------------------------------
# I-09 compressione delle bande e rottura (4h)
# ---------------------------------------------------------------------------

def i09(id_, direzione, tf="4h"):
    def prepara(s):
        m = ind.media_mobile(s.c, 20)
        sd = ind.dev_std_mobile(s.c, 20) * math.sqrt(19 / 20)  # dev. std della popolazione, come Bollinger
        bw = 4 * sd / m
        p20 = ind.percentile_mobile(bw, 120, 0.20)
        return {"atr": ind.atr(s, 20), "m": m, "sd": sd, "bw": bw, "p20": p20}

    def condizione(ctx, i):
        if i < 1:
            return False
        bw1, p1, m, sd = ctx["bw"][i - 1], ctx["p20"][i - 1], ctx["m"][i], ctx["sd"][i]
        if not _ok(bw1, p1, m, sd):
            return False
        c = ctx["serie"].c[i]
        compressa = bw1 <= p1
        return compressa and (c > m + 2 * sd if direzione == "long" else c < m - 2 * sd)

    def uscita(ctx, i, pos):
        c, m = ctx["serie"].c[i], ctx["m"][i]
        if not _ok(m):
            return None
        return "chiudi" if ((c < m) if direzione == "long" else (c > m)) else None

    return Variante(id_, tf, direzione, prepara, condizione, _segnale_atr(direzione, 2.0), uscita)


# ---------------------------------------------------------------------------
# I-10 premio del last sul mark (1h)
# ---------------------------------------------------------------------------

def i10(id_, direzione):
    def prepara(s):
        cm = np.array([x.close for x in s.mark])
        p = s.c / cm - 1
        return {"atr": ind.atr(s, 24), "p": p, "p99": ind.percentile_mobile(p, 720, 0.99),
                "p01": ind.percentile_mobile(p, 720, 0.01)}

    def condizione(ctx, i):
        p = ctx["p"][i]
        if direzione == "short":
            return _ok(p, ctx["p99"][i]) and p > 0 and p >= ctx["p99"][i]
        return _ok(p, ctx["p01"][i]) and p < 0 and p <= ctx["p01"][i]

    return Variante(id_, "1h", direzione, prepara, condizione, _segnale_atr(direzione, 2.0), _uscita_tempo(4))


# ---------------------------------------------------------------------------
# I-11 prima mezz'ora -> ultima mezz'ora (30m)
# ---------------------------------------------------------------------------

def i11(id_, direzione):
    def prepara(s):
        n = len(s.c)
        r_prima = np.full(n, np.nan)
        prima = {}
        for i in range(n):
            g, resto = divmod(int(s.ts[i]), 86_400_000)
            if resto == 0:
                prima[g] = s.c[i] / s.o[i] - 1
            if resto == 23 * 3_600_000 and g in prima:  # barra delle 23:00: si entra alle 23:30
                r_prima[i] = prima[g]
        return {"atr": ind.atr(s, 48), "r_prima": r_prima}

    def condizione(ctx, i):
        r = ctx["r_prima"][i]
        if not _ok(r):
            return False
        return r > 0 if direzione == "long" else r < 0

    return Variante(id_, "30m", direzione, prepara, condizione, _segnale_atr(direzione, 2.0), _uscita_tempo(1))


# ---------------------------------------------------------------------------
# I-12 volatilita' bassa (1d)
# ---------------------------------------------------------------------------

def i12(id_):
    def prepara(s):
        vol30 = ind.dev_std_mobile(ind.log_rend(s.c), 30)
        med = pd_median(vol30, 180)
        return {"atr": ind.atr(s, 14), "vol30": vol30, "med": med}

    def condizione(ctx, i):
        v, m = ctx["vol30"][i], ctx["med"][i]
        return _ok(v, m) and v < m

    return Variante(id_, "1d", "long", prepara, condizione, _segnale_atr("long", 2.5), _uscita_tempo(5))


def pd_median(x, n):
    return ind.percentile_mobile(x, n, 0.5)


# ---------------------------------------------------------------------------
# I-13 incrocio di medie 10/50 (4h)
# ---------------------------------------------------------------------------

def i13(id_, direzione, tf="4h"):
    def prepara(s):
        return {"atr": ind.atr(s, 20), "m10": ind.media_mobile(s.c, 10), "m50": ind.media_mobile(s.c, 50)}

    def condizione(ctx, i):
        if i < 1:
            return False
        a, b, a1, b1 = ctx["m10"][i], ctx["m50"][i], ctx["m10"][i - 1], ctx["m50"][i - 1]
        if not _ok(a, b, a1, b1):
            return False
        return (a > b and a1 <= b1) if direzione == "long" else (a < b and a1 >= b1)

    def uscita(ctx, i, pos):
        a, b = ctx["m10"][i], ctx["m50"][i]
        if not _ok(a, b):
            return None
        return "chiudi" if ((a < b) if direzione == "long" else (a > b)) else None

    return Variante(id_, tf, direzione, prepara, condizione, _segnale_atr(direzione, 3.0), uscita)


# ---------------------------------------------------------------------------
# I-14 calo con volume alto che torna indietro (1d)
# ---------------------------------------------------------------------------

def i14(id_, tf="1d"):
    def prepara(s):
        r = ind.log_rend(s.c)
        sd60 = ind.dev_std_mobile(r, 60)
        vm30 = ind.media_mobile(np.concatenate([[np.nan], s.v[:-1]]), 30)  # 30 giorni PRECEDENTI
        return {"atr": ind.atr(s, 14), "r": r, "sd60": sd60, "vm30": vm30}

    def condizione(ctx, i):
        r, sd, vm = ctx["r"][i], ctx["sd60"][i], ctx["vm30"][i]
        if not _ok(r, sd, vm):
            return False
        return r < -sd and ctx["serie"].v[i] > 1.5 * vm

    return Variante(id_, tf, "long", prepara, condizione, _segnale_atr("long", 2.0), _uscita_tempo(2))


# ---------------------------------------------------------------------------
# I-15 attraversamento dei numeri tondi (1h)
# ---------------------------------------------------------------------------

def i15(id_, direzione):
    def prepara(s):
        n = len(s.c)
        attraversa = np.zeros(n, dtype=bool)
        for i in range(1, n):
            p = s.c[i - 1]
            passo = 10.0 ** (math.floor(math.log10(p)) - 1)
            k = p / passo
            if direzione == "long":
                livello = (math.floor(k + 1e-9) + 1) * passo
                attraversa[i] = s.c[i] >= livello - 1e-12
            else:
                livello = (math.ceil(k - 1e-9) - 1) * passo
                attraversa[i] = s.c[i] <= livello + 1e-12
        return {"atr": ind.atr(s, 24), "att": attraversa}

    def condizione(ctx, i):
        return bool(ctx["att"][i])

    return Variante(id_, "1h", direzione, prepara, condizione, _segnale_atr(direzione, 2.0), _uscita_tempo(3))
