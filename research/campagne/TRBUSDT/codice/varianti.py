"""Le varianti delle idee di ipotesi.md, scritte prima di qualunque test.

Ogni funzione ``v_<id>()`` restituisce la ``banco.Variante``. ``REGISTRO`` contiene per ogni id
idea, fonte, meccanismo, parametri, previsione (intervallo dell'R medio dopo i costi in
costruzione, deciso prima del test) e criterio di successo.
"""

from __future__ import annotations

from datetime import datetime, timezone

import numpy as np

from research.src.motore import Segnale
from research.campagne.TRBUSDT.codice import banco
from research.campagne.TRBUSDT.codice import indicatori as ind

CRITERIO = ("candidato se batte nettamente la (a) e la (b) in costruzione (contro_baseline) e ha R medio "
            "dopo i costi positivo, con almeno 70 trade")


def _ms(tf):
    return banco.ms_per_barra(tf)


def _uscita_tempo(h, tf):
    """'chiudi' alla chiusura della h-esima barra dalla barra d'ingresso compresa."""
    durata = _ms(tf)

    def uscita(ctx, i, pos):
        barre = (int(ctx["ts"][i]) - pos.ts_entrata) // durata + 1
        return "chiudi" if barre >= h else None

    return uscita


def _stop_atr(direzione, k):
    def segnale(ctx, i):
        a = ctx["atr"][i]
        c = ctx["c"][i]
        if not np.isfinite(a) or a <= 0 or not ctx["pronto"][i]:
            return None
        return Segnale(direzione, c - k * a if direzione == "long" else c + k * a, None)

    return segnale


def _base(candele, riscaldamento):
    o, h, l, c, v, ts = ind.colonne(candele)
    pronto = np.zeros(len(c), dtype=bool)
    pronto[riscaldamento:] = True
    return {"o": o, "h": h, "l": l, "c": c, "v": v, "ts": ts, "atr": ind.atr(h, l, c, 14), "pronto": pronto}


# --------------------------------------------------------------------------- I-01
def _i01(direzione):
    tf = "4h"

    def prepara(candele):
        ctx = _base(candele, 120)
        ctx["r120"] = ind.rendimento(ctx["c"], 120)
        return ctx

    def condizione(ctx, i):
        r = ctx["r120"][i]
        return np.isfinite(r) and (r > 0 if direzione == "long" else r < 0)

    return banco.Variante(f"I-01-{direzione[0].upper()}", tf, direzione, prepara, condizione,
                          _stop_atr(direzione, 2.0), _uscita_tempo(30, tf))


# --------------------------------------------------------------------------- I-02
def _i02(direzione, canale=50, tenere=60, suffisso=""):
    tf = "4h"

    def prepara(candele):
        ctx = _base(candele, canale)
        h, l = ctx["h"], ctx["l"]
        mx = np.full(len(h), np.nan)
        mn = np.full(len(h), np.nan)
        mx[1:] = ind.rolling_max(h, canale)[:-1]
        mn[1:] = ind.rolling_min(l, canale)[:-1]
        ctx["max_prec"], ctx["min_prec"] = mx, mn
        return ctx

    def condizione(ctx, i):
        if direzione == "long":
            return np.isfinite(ctx["max_prec"][i]) and ctx["c"][i] > ctx["max_prec"][i]
        return np.isfinite(ctx["min_prec"][i]) and ctx["c"][i] < ctx["min_prec"][i]

    return banco.Variante(f"I-02-{direzione[0].upper()}{suffisso}", tf, direzione, prepara, condizione,
                          _stop_atr(direzione, 2.0), _uscita_tempo(tenere, tf))


# --------------------------------------------------------------------------- I-03
def _i03(direzione):
    tf = "1h"

    def prepara(candele):
        ctx = _base(candele, 726)
        r6 = ind.rendimento(ctx["c"], 6)
        sd = np.full(len(r6), np.nan)
        r6z = np.where(np.isfinite(r6), r6, 0.0)
        sd_tmp = ind.rolling_std(r6z, 720)
        sd[726:] = sd_tmp[726:]
        ctx["z"] = r6 / sd
        return ctx

    def condizione(ctx, i):
        z = ctx["z"][i]
        return np.isfinite(z) and (z < -2.5 if direzione == "long" else z > 2.5)

    return banco.Variante(f"I-03-{direzione[0].upper()}", tf, direzione, prepara, condizione,
                          _stop_atr(direzione, 2.0), _uscita_tempo(12, tf))


# --------------------------------------------------------------------------- I-04
def _i04(soglia_volume, soglia_rialzo, nome):
    tf = "1h"

    def prepara(candele):
        ctx = _base(candele, 168)
        med = np.full(len(ctx["v"]), np.nan)
        med[1:] = ind.rolling_median(ctx["v"], 168)[:-1]
        ctx["med"] = med
        return ctx

    def condizione(ctx, i):
        m = ctx["med"][i]
        return (np.isfinite(m) and m > 0 and ctx["v"][i] > soglia_volume * m
                and ctx["c"][i] / ctx["o"][i] - 1 > soglia_rialzo)

    def segnale(ctx, i):
        a = ctx["atr"][i]
        if not np.isfinite(a) or not ctx["pronto"][i]:
            return None
        return Segnale("short", ctx["h"][i] + a, None)

    return banco.Variante(nome, tf, "short", prepara, condizione, segnale, _uscita_tempo(24, tf))


# --------------------------------------------------------------------------- I-05
def _i05(direzione, alto=90, basso=10, suffisso=""):
    tf = "8h"

    def prepara(candele):
        ctx = _base(candele, 0)
        # il funding della stessa serie usata dal test: costruzione o costruzione+validazione
        periodo = "costruzione" if candele[-1].close_ts <= banco.FINE_COSTRUZIONE_TS else "validazione"
        funding = banco.carica(tf, periodo)["funding"]
        ts_f = np.array([t for t, _ in funding], dtype=np.int64)
        r_f = np.array([r for _, r in funding], dtype=float)
        n = len(candele)
        f = np.full(n, np.nan)
        for i, cnd in enumerate(candele):
            k = np.searchsorted(ts_f, cnd.close_ts, side="right")  # settlement con istante <= chiusura
            if k >= 3:
                f[i] = r_f[k - 3:k].mean()
        p90 = np.full(n, np.nan)
        p10 = np.full(n, np.nan)
        for i in range(270, n):
            fin = f[i - 270:i]
            fin = fin[np.isfinite(fin)]
            if len(fin) >= 200:
                p90[i] = np.percentile(fin, alto)
                p10[i] = np.percentile(fin, basso)
        ctx.update({"f": f, "p90": p90, "p10": p10})
        ctx["pronto"] = np.isfinite(p90) & np.isfinite(f)
        return ctx

    def condizione(ctx, i):
        f = ctx["f"][i]
        if not ctx["pronto"][i]:
            return False
        if direzione == "short":
            return f >= ctx["p90"][i] and f > 0.0001
        return f <= ctx["p10"][i] and f < 0

    return banco.Variante(f"I-05-{direzione[0].upper()}{suffisso}", tf, direzione, prepara, condizione,
                          _stop_atr(direzione, 2.0), _uscita_tempo(9, tf))


# --------------------------------------------------------------------------- I-06
def _giorno(ts):
    return datetime.fromtimestamp(int(ts) / 1000, tz=timezone.utc)


def _i06():
    tf = "1d"

    def prepara(candele):
        ctx = _base(candele, 0)
        ctx["domenica"] = np.array([_giorno(t).weekday() == 6 for t in ctx["ts"]], dtype=bool)
        return ctx

    def segnale(ctx, i):
        return Segnale("long", ctx["c"][i] * 0.94, None)

    return banco.Variante("I-06-L", tf, "long", prepara, lambda ctx, i: bool(ctx["domenica"][i]), segnale,
                          _uscita_tempo(1, tf))


# --------------------------------------------------------------------------- I-07
def _i07(direzione, tf="4h", suffisso=""):

    def prepara(candele):
        ctx = _base(candele, 140)
        c = ctx["c"]
        m = ind.sma(c, 20)
        s = ind.rolling_std(c, 20)
        alta, bassa = m + 2 * s, m - 2 * s
        amp = 4 * s / m
        perc = np.full(len(c), np.nan)
        for i in range(139, len(c)):
            fin = amp[i - 119:i + 1]
            if np.isfinite(fin).all():
                perc[i] = np.percentile(fin, 20)
        compr = np.zeros(len(c), dtype=bool)
        compr[1:] = (amp[:-1] <= perc[:-1]) & np.isfinite(perc[:-1])
        ctx.update({"m": m, "alta": alta, "bassa": bassa, "compr": compr})
        return ctx

    def condizione(ctx, i):
        if not ctx["compr"][i]:
            return False
        return ctx["c"][i] > ctx["alta"][i] if direzione == "long" else ctx["c"][i] < ctx["bassa"][i]

    def segnale(ctx, i):
        m = ctx["m"][i]
        if not np.isfinite(m) or not ctx["pronto"][i]:
            return None
        return Segnale(direzione, m, None)

    return banco.Variante(f"I-07-{direzione[0].upper()}{suffisso}", tf, direzione, prepara, condizione, segnale,
                          _uscita_tempo(30, tf))


# --------------------------------------------------------------------------- I-08
def _i08(direzione):
    tf = "4h"

    def prepara(candele):
        ctx = _base(candele, 200)
        ctx["m200"] = ind.sma(ctx["c"], 200)
        ctx["m5"] = ind.sma(ctx["c"], 5)
        ctx["rsi2"] = ind.rsi(ctx["c"], 2)
        return ctx

    def condizione(ctx, i):
        m, r = ctx["m200"][i], ctx["rsi2"][i]
        if not (np.isfinite(m) and np.isfinite(r)):
            return False
        if direzione == "long":
            return ctx["c"][i] > m and r < 10
        return ctx["c"][i] < m and r > 90

    def uscita(ctx, i, pos):
        m5 = ctx["m5"][i]
        if int(ctx["ts"][i]) < pos.ts_entrata or not np.isfinite(m5):
            return None
        if direzione == "long":
            return "chiudi" if ctx["c"][i] > m5 else None
        return "chiudi" if ctx["c"][i] < m5 else None

    return banco.Variante(f"I-08-{direzione[0].upper()}", tf, direzione, prepara, condizione,
                          _stop_atr(direzione, 3.0), uscita)


# --------------------------------------------------------------------------- I-09
def _i09(tf="1d", finestra=20, tenere=5, nome="I-09-L"):

    def prepara(candele):
        ctx = _base(candele, finestra)
        mv = np.full(len(ctx["v"]), np.nan)
        mv[1:] = ind.sma(ctx["v"], finestra)[:-1]
        ctx["mv"] = mv
        return ctx

    def condizione(ctx, i):
        m = ctx["mv"][i]
        return np.isfinite(m) and m > 0 and ctx["v"][i] > 2 * m

    return banco.Variante(nome, tf, "long", prepara, condizione, _stop_atr("long", 2.0), _uscita_tempo(tenere, tf))


# --------------------------------------------------------------------------- I-14
def _i14():
    tf = "4h"

    def prepara(candele):
        ctx = _base(candele, 42 + 540)
        c, v = ctx["c"], ctx["v"]
        r = np.full(len(c), np.nan)
        r[1:] = np.abs(c[1:] / c[:-1] - 1)
        usdt = v * c
        x = np.where(usdt > 0, r / np.where(usdt > 0, usdt, 1), np.nan)
        a = np.full(len(c), np.nan)
        for i in range(42, len(c)):
            fin = x[i - 41:i + 1]
            if np.isfinite(fin).all():
                a[i] = fin.mean()
        soglia = np.full(len(c), np.nan)
        for i in range(42 + 540, len(c)):
            fin = a[i - 540:i]
            fin = fin[np.isfinite(fin)]
            if len(fin) >= 400:
                soglia[i] = np.percentile(fin, 90)
        ctx["a"], ctx["soglia"] = a, soglia
        return ctx

    def condizione(ctx, i):
        return np.isfinite(ctx["a"][i]) and np.isfinite(ctx["soglia"][i]) and ctx["a"][i] >= ctx["soglia"][i]

    return banco.Variante("I-14-L", tf, "long", prepara, condizione, _stop_atr("long", 2.0), _uscita_tempo(42, tf))


# --------------------------------------------------------------------------- I-15
def _i15(direzione):
    tf = "4h"

    def prepara(candele):
        ctx = _base(candele, 43 + 540)
        c = ctx["c"]
        r = np.full(len(c), np.nan)
        r[1:] = c[1:] / c[:-1] - 1
        s = np.full(len(c), np.nan)
        for i in range(42, len(c)):
            fin = r[i - 41:i + 1]
            if np.isfinite(fin).all():
                d = fin - fin.mean()
                sd = np.sqrt((d ** 2).mean())
                if sd > 0:
                    s[i] = (d ** 3).mean() / sd ** 3
        alto = np.full(len(c), np.nan)
        basso = np.full(len(c), np.nan)
        for i in range(43 + 540, len(c)):
            fin = s[i - 540:i]
            fin = fin[np.isfinite(fin)]
            if len(fin) >= 400:
                alto[i] = np.percentile(fin, 90)
                basso[i] = np.percentile(fin, 10)
        ctx.update({"s": s, "alto": alto, "basso": basso})
        return ctx

    def condizione(ctx, i):
        s = ctx["s"][i]
        if direzione == "short":
            return np.isfinite(s) and np.isfinite(ctx["alto"][i]) and s >= ctx["alto"][i]
        return np.isfinite(s) and np.isfinite(ctx["basso"][i]) and s <= ctx["basso"][i]

    return banco.Variante(f"I-15-{direzione[0].upper()}", tf, direzione, prepara, condizione,
                          _stop_atr(direzione, 2.0), _uscita_tempo(18, tf))


# --------------------------------------------------------------------------- I-10
def _i10(direzione):
    tf = "30m"

    def prepara(candele):
        ctx = _base(candele, 14)
        n = len(candele)
        r1 = np.full(n, np.nan)
        prima = {}
        for k, t in enumerate(ctx["ts"]):
            g = _giorno(t)
            if g.hour == 0 and g.minute == 0:
                prima[g.date()] = ctx["c"][k] / ctx["o"][k] - 1
            if g.hour == 23 and g.minute == 0 and g.date() in prima:
                r1[k] = prima[g.date()]
        ctx["r1"] = r1
        return ctx

    def condizione(ctx, i):
        r = ctx["r1"][i]
        return np.isfinite(r) and (r > 0 if direzione == "long" else r < 0)

    return banco.Variante(f"I-10-{direzione[0].upper()}", tf, direzione, prepara, condizione,
                          _stop_atr(direzione, 1.0), _uscita_tempo(1, tf))


# --------------------------------------------------------------------------- I-11
def _passo(p):
    if p < 10:
        return 0.5
    if p < 100:
        return 5.0
    return 50.0


def _i11(direzione):
    tf = "1h"

    def prepara(candele):
        ctx = _base(candele, 14)
        c = ctx["c"]
        su = np.zeros(len(c), dtype=bool)
        giu = np.zeros(len(c), dtype=bool)
        for i in range(1, len(c)):
            p = _passo(c[i - 1])
            a, b = np.floor(c[i - 1] / p), np.floor(c[i] / p)
            su[i] = b > a
            giu[i] = b < a
        ctx["su"], ctx["giu"] = su, giu
        return ctx

    def condizione(ctx, i):
        return bool(ctx["su"][i] if direzione == "long" else ctx["giu"][i])

    return banco.Variante(f"I-11-{direzione[0].upper()}", tf, direzione, prepara, condizione,
                          _stop_atr(direzione, 1.5), _uscita_tempo(12, tf))


# --------------------------------------------------------------------------- I-12
def _i12(direzione):
    tf = "1d"

    def prepara(candele):
        ctx = _base(candele, 0)
        h, l, c = ctx["h"], ctx["l"], ctx["c"]
        rng = h - l
        ctx["ibs"] = np.where(rng > 0, (c - l) / np.where(rng > 0, rng, 1), np.nan)
        return ctx

    def condizione(ctx, i):
        x = ctx["ibs"][i]
        return np.isfinite(x) and (x < 0.2 if direzione == "long" else x > 0.8)

    def segnale(ctx, i):
        c = ctx["c"][i]
        return Segnale(direzione, c * 0.94 if direzione == "long" else c * 1.06, None)

    return banco.Variante(f"I-12-{direzione[0].upper()}", tf, direzione, prepara, condizione, segnale,
                          _uscita_tempo(1, tf))


# --------------------------------------------------------------------------- I-13
def _i13(direzione):
    tf = "15m"

    def prepara(candele):
        ctx = _base(candele, 0)
        n = len(candele)
        alto = np.full(n, np.nan)
        basso = np.full(n, np.nan)
        primo = np.zeros(n, dtype=bool)
        fine_giorno = np.zeros(n, dtype=bool)
        range_giorno = {}
        barre_prima_ora = {}
        gia = set()
        for k, t in enumerate(ctx["ts"]):
            g = _giorno(t)
            d = g.date()
            if g.hour == 0:
                barre_prima_ora.setdefault(d, []).append(k)
                if len(barre_prima_ora[d]) == 4:
                    ks = barre_prima_ora[d]
                    range_giorno[d] = (ctx["h"][ks].max(), ctx["l"][ks].min())
                continue
            if g.hour == 23 and g.minute == 45:
                fine_giorno[k] = True
            if d in range_giorno and g.hour < 22:
                hi, lo = range_giorno[d]
                alto[k], basso[k] = hi, lo
                rotto = ctx["c"][k] > hi if direzione == "long" else ctx["c"][k] < lo
                if rotto and d not in gia:
                    primo[k] = True
                    gia.add(d)
        ctx.update({"alto": alto, "basso": basso, "primo": primo, "fine_giorno": fine_giorno})
        return ctx

    def segnale(ctx, i):
        hi, lo = ctx["alto"][i], ctx["basso"][i]
        if not (np.isfinite(hi) and np.isfinite(lo)):
            return None
        return Segnale(direzione, lo if direzione == "long" else hi, None)

    def uscita(ctx, i, pos):
        return "chiudi" if ctx["fine_giorno"][i] and int(ctx["ts"][i]) >= pos.ts_entrata else None

    return banco.Variante(f"I-13-{direzione[0].upper()}", tf, direzione, prepara,
                          lambda ctx, i: bool(ctx["primo"][i]), segnale, uscita)


# --------------------------------------------------------------------------- registro
VARIANTI = {
    "I-01-L": lambda: _i01("long"), "I-01-S": lambda: _i01("short"),
    "I-02-L": lambda: _i02("long"), "I-02-S": lambda: _i02("short"),
    "I-03-L": lambda: _i03("long"), "I-03-S": lambda: _i03("short"),
    "I-04-A": lambda: _i04(5.0, 0.03, "I-04-A"), "I-04-B": lambda: _i04(3.0, 0.02, "I-04-B"),
    "I-05-S": lambda: _i05("short"), "I-05-L": lambda: _i05("long"),
    "I-06-L": _i06,
    "I-07-L": lambda: _i07("long"), "I-07-S": lambda: _i07("short"),
    "I-08-L": lambda: _i08("long"), "I-08-S": lambda: _i08("short"),
    "I-09-L": _i09,
    "I-10-L": lambda: _i10("long"), "I-10-S": lambda: _i10("short"),
    "I-11-L": lambda: _i11("long"), "I-11-S": lambda: _i11("short"),
    "I-12-L": lambda: _i12("long"), "I-12-S": lambda: _i12("short"),
    "I-13-L": lambda: _i13("long"), "I-13-S": lambda: _i13("short"),
    # aggiunte dopo gli scarti per trade stimati (ipotesi.md, 2026-10-09)
    "I-02-L2": lambda: _i02("long", 20, 30, "2"), "I-02-S2": lambda: _i02("short", 20, 30, "2"),
    "I-05-S2": lambda: _i05("short", 75, 25, "2"), "I-05-L2": lambda: _i05("long", 75, 25, "2"),
    "I-07-L2": lambda: _i07("long", "1h", "2"), "I-07-S2": lambda: _i07("short", "1h", "2"),
    "I-09-L2": lambda: _i09("12h", 40, 10, "I-09-L2"),
    "I-14-L": _i14,
    "I-15-S": lambda: _i15("short"), "I-15-L": lambda: _i15("long"),
}

FONTI = {
    "I-01": "Moskowitz, Ooi, Pedersen, «Time series momentum», Journal of Financial Economics 104(2), 2012; Liu, Tsyvinski, «Risks and Returns of Cryptocurrency», NBER WP 24877, agosto 2018",
    "I-02": "Brock, Lakonishok, LeBaron, «Simple Technical Trading Rules and the Stochastic Properties of Stock Returns», Journal of Finance 47(5), dicembre 1992",
    "I-03": "De Bondt, Thaler, «Does the Stock Market Overreact?», Journal of Finance 40(3), luglio 1985; Lehmann, «Fads, Martingales, and Market Efficiency», QJE 105(1), febbraio 1990",
    "I-04": "Kamps, Kleinberg, «To the moon: defining and detecting cryptocurrency pump-and-dumps», Crime Science 7:18, novembre 2018",
    "I-05": "Schmeling, Schrimpf, Todorov, «Crypto carry», BIS Working Papers 1087, marzo 2023; He, Manela, Ross, von Wachter, «Fundamentals of Perpetual Futures», arXiv 2212.06888, dicembre 2022",
    "I-06": "Caporale, Plastun, «The day of the week effect in the cryptocurrency market», Finance Research Letters 31, dicembre 2019",
    "I-07": "Bollinger, «Bollinger on Bollinger Bands», McGraw-Hill, 2001",
    "I-08": "Connors, Alvarez, «Short Term Trading Strategies That Work», TradingMarkets, 2008; Wilder, «New Concepts in Technical Trading Systems», 1978",
    "I-09": "Gervais, Kaniel, Mingelgrin, «The High-Volume Return Premium», Journal of Finance 56(3), giugno 2001",
    "I-10": "Gao, Han, Li, Zhou, «Market intraday momentum», Journal of Financial Economics 129(2), agosto 2018; «Intraday return predictability in the cryptocurrency markets: Momentum, reversal, or both», North American Journal of Economics and Finance 62, 2022 (DOI 10.1016/j.najef.2022.101733)",
    "I-11": "Osler, «Currency Orders and Exchange Rate Dynamics: An Explanation for the Predictive Success of Technical Analysis», Journal of Finance 58(5), ottobre 2003",
    "I-12": "Pagonidis, «The IBS Effect: Mean Reversion in Equity ETFs», articolo NAAIM, 2013",
    "I-13": "Crabel, «Day Trading with Short Term Price Patterns and Opening Range Breakout», Traders Press, 1990",
    "I-14": "Amihud, «Illiquidity and stock returns: cross-section and time-series effects», Journal of Financial Markets 5(1), gennaio 2002",
    "I-15": "Boyer, Mitton, Vorkink, «Expected Idiosyncratic Skewness», Review of Financial Studies 23(1), gennaio 2010; Barberis, Huang, «Stocks as Lotteries», American Economic Review 98(5), dicembre 2008",
}

MECCANISMI = {
    "I-01": "momentum della serie: il rendimento a 20 giorni predice i 5 giorni dopo con lo stesso segno",
    "I-02": "rottura del canale: la chiusura oltre il massimo/minimo di 50 barre continua per 10 giorni",
    "I-03": "reazione eccessiva: dopo un movimento di 6 ore oltre 2,5 deviazioni standard il prezzo torna indietro in 12 ore",
    "I-04": "sgonfiamento dopo un gonfiamento di prezzo e volume in un'ora",
    "I-05": "funding affollato: chi paga un funding estremo viene liquidato, il prezzo va contro di lui in 3 giorni",
    "I-06": "effetto del lunedi': il lunedi' rende piu' di un giorno qualunque",
    "I-07": "compressione della volatilita' seguita da rottura della banda nella stessa direzione",
    "I-08": "ritorno di brevissimo periodo nel verso del trend (RSI a 2 barre sotto 10 / sopra 90)",
    "I-09": "premio del volume alto: dopo un giorno di volume doppio il prezzo sale nei 5 giorni dopo",
    "I-10": "momentum dentro la giornata: la prima mezz'ora UTC predice l'ultima",
    "I-11": "numeri tondi: dopo l'attraversamento di un numero tondo il movimento continua per 12 ore",
    "I-12": "posizione della chiusura nella barra: chiusura vicina al minimo/massimo del giorno, ritorno il giorno dopo",
    "I-13": "rottura del range della prima ora UTC: la giornata continua nel verso della rottura",
    "I-14": "premio dell'illiquidita': dopo un'illiquidita' di Amihud a 7 giorni ai massimi di 90 giorni il prezzo sale",
    "I-15": "preferenza per le lotterie: dopo un'asimmetria dei rendimenti estrema il prezzo va nel verso opposto",
}

PARAMETRI = {
    "I-01-L": {"rendimento_barre": 120, "soglia": 0, "stop_atr": 2.0, "tenere_barre": 30},
    "I-01-S": {"rendimento_barre": 120, "soglia": 0, "stop_atr": 2.0, "tenere_barre": 30},
    "I-02-L": {"canale_barre": 50, "stop_atr": 2.0, "tenere_barre": 60},
    "I-02-S": {"canale_barre": 50, "stop_atr": 2.0, "tenere_barre": 60},
    "I-03-L": {"rendimento_barre": 6, "finestra_deviazione": 720, "soglia_z": -2.5, "stop_atr": 2.0, "tenere_barre": 12},
    "I-03-S": {"rendimento_barre": 6, "finestra_deviazione": 720, "soglia_z": 2.5, "stop_atr": 2.0, "tenere_barre": 12},
    "I-04-A": {"volume_su_mediana": 5.0, "finestra_mediana": 168, "rialzo_barra": 0.03, "stop": "high + 1 ATR", "tenere_barre": 24},
    "I-04-B": {"volume_su_mediana": 3.0, "finestra_mediana": 168, "rialzo_barra": 0.02, "stop": "high + 1 ATR", "tenere_barre": 24},
    "I-05-S": {"media_settlement": 3, "finestra_percentile": 270, "percentile": 90, "funding_minimo": 0.0001, "stop_atr": 2.0, "tenere_barre": 9},
    "I-05-L": {"media_settlement": 3, "finestra_percentile": 270, "percentile": 10, "funding_massimo": 0.0, "stop_atr": 2.0, "tenere_barre": 9},
    "I-06-L": {"giorno_segnale": "domenica", "stop_pct": 0.06, "tenere_barre": 1},
    "I-07-L": {"bande_barre": 20, "bande_deviazioni": 2, "finestra_percentile": 120, "percentile": 20, "stop": "media20", "tenere_barre": 30},
    "I-07-S": {"bande_barre": 20, "bande_deviazioni": 2, "finestra_percentile": 120, "percentile": 20, "stop": "media20", "tenere_barre": 30},
    "I-08-L": {"media_lunga": 200, "rsi_barre": 2, "rsi_soglia": 10, "media_uscita": 5, "stop_atr": 3.0},
    "I-08-S": {"media_lunga": 200, "rsi_barre": 2, "rsi_soglia": 90, "media_uscita": 5, "stop_atr": 3.0},
    "I-09-L": {"volume_su_media": 2.0, "finestra_media": 20, "stop_atr": 2.0, "tenere_barre": 5},
    "I-10-L": {"barra_predittiva": "00:00-00:30 UTC", "barra_segnale": "23:00-23:30 UTC", "stop_atr": 1.0, "tenere_barre": 1},
    "I-10-S": {"barra_predittiva": "00:00-00:30 UTC", "barra_segnale": "23:00-23:30 UTC", "stop_atr": 1.0, "tenere_barre": 1},
    "I-11-L": {"passi": {"<10": 0.5, "10-100": 5, "100-1000": 50}, "stop_atr": 1.5, "tenere_barre": 12},
    "I-11-S": {"passi": {"<10": 0.5, "10-100": 5, "100-1000": 50}, "stop_atr": 1.5, "tenere_barre": 12},
    "I-12-L": {"ibs_soglia": 0.2, "stop_pct": 0.06, "tenere_barre": 1},
    "I-12-S": {"ibs_soglia": 0.8, "stop_pct": 0.06, "tenere_barre": 1},
    "I-13-L": {"range": "00:00-01:00 UTC", "ultima_ora_segnale": 22, "stop": "minimo del range", "uscita": "chiusura 23:45-24:00"},
    "I-13-S": {"range": "00:00-01:00 UTC", "ultima_ora_segnale": 22, "stop": "massimo del range", "uscita": "chiusura 23:45-24:00"},
    "I-02-L2": {"canale_barre": 20, "stop_atr": 2.0, "tenere_barre": 30},
    "I-02-S2": {"canale_barre": 20, "stop_atr": 2.0, "tenere_barre": 30},
    "I-05-S2": {"media_settlement": 3, "finestra_percentile": 270, "percentile": 75, "funding_minimo": 0.0001, "stop_atr": 2.0, "tenere_barre": 9},
    "I-05-L2": {"media_settlement": 3, "finestra_percentile": 270, "percentile": 25, "funding_massimo": 0.0, "stop_atr": 2.0, "tenere_barre": 9},
    "I-07-L2": {"bande_barre": 20, "bande_deviazioni": 2, "finestra_percentile": 120, "percentile": 20, "stop": "media20", "tenere_barre": 30},
    "I-07-S2": {"bande_barre": 20, "bande_deviazioni": 2, "finestra_percentile": 120, "percentile": 20, "stop": "media20", "tenere_barre": 30},
    "I-09-L2": {"volume_su_media": 2.0, "finestra_media": 40, "stop_atr": 2.0, "tenere_barre": 10},
    "I-14-L": {"finestra_illiquidita": 42, "finestra_percentile": 540, "percentile": 90, "stop_atr": 2.0, "tenere_barre": 42},
    "I-15-S": {"finestra_asimmetria": 42, "finestra_percentile": 540, "percentile": 90, "stop_atr": 2.0, "tenere_barre": 18},
    "I-15-L": {"finestra_asimmetria": 42, "finestra_percentile": 540, "percentile": 10, "stop_atr": 2.0, "tenere_barre": 18},
}

# Previsioni scritte prima dei test: intervallo dell'R medio dopo i costi in costruzione e attesa su «nettamente».
PREVISIONI = {
    "I-01-L": ((-0.15, 0.10), "non batte nettamente la (b): momentum debole su una sola altcoin, costruzione con il ribasso del 2022"),
    "I-01-S": ((-0.10, 0.15), "non batte nettamente la (b)"),
    "I-02-L": ((-0.20, 0.10), "non batte nettamente la (b): molte false rotture"),
    "I-02-S": ((-0.10, 0.15), "non batte nettamente la (b)"),
    "I-03-L": ((-0.15, 0.10), "non batte nettamente la (b)"),
    "I-03-S": ((-0.15, 0.10), "non batte nettamente la (b)"),
    "I-04-A": ((-0.20, 0.20), "probabilmente sotto i 70 trade; se testata non batte nettamente la (b)"),
    "I-04-B": ((-0.20, 0.15), "non batte nettamente la (b)"),
    "I-05-S": ((-0.15, 0.15), "non batte nettamente la (b)"),
    "I-05-L": ((-0.15, 0.15), "non batte nettamente la (b)"),
    "I-06-L": ((-0.10, 0.10), "non batte nettamente la (b): l'effetto della fonte e' su Bitcoin"),
    "I-07-L": ((-0.20, 0.10), "non batte nettamente la (b)"),
    "I-07-S": ((-0.15, 0.15), "non batte nettamente la (b)"),
    "I-08-L": ((-0.15, 0.10), "non batte nettamente la (b)"),
    "I-08-S": ((-0.15, 0.10), "non batte nettamente la (b)"),
    "I-09-L": ((-0.15, 0.10), "non batte nettamente la (b)"),
    "I-10-L": ((-0.25, 0.00), "R medio negativo: i costi di una mezz'ora pesano circa 0,2 R"),
    "I-10-S": ((-0.25, 0.00), "R medio negativo: costi"),
    "I-11-L": ((-0.20, 0.05), "non batte nettamente la (b)"),
    "I-11-S": ((-0.20, 0.05), "non batte nettamente la (b)"),
    "I-12-L": ((-0.10, 0.10), "non batte nettamente la (b)"),
    "I-12-S": ((-0.10, 0.10), "non batte nettamente la (b)"),
    "I-13-L": ((-0.20, 0.05), "non batte nettamente la (b): costi alti in R"),
    "I-13-S": ((-0.20, 0.05), "non batte nettamente la (b)"),
    "I-02-L2": ((-0.20, 0.10), "non batte nettamente la (b)"),
    "I-02-S2": ((-0.25, 0.10), "non batte nettamente la (b)"),
    "I-05-S2": ((-0.20, 0.15), "non batte nettamente la (b); se sotto 70 trade, scarto"),
    "I-05-L2": ((-0.15, 0.20), "non batte nettamente la (b); se sotto 70 trade, scarto"),
    "I-07-L2": ((-0.20, 0.05), "non batte nettamente la (b)"),
    "I-07-S2": ((-0.20, 0.05), "non batte nettamente la (b)"),
    "I-09-L2": ((-0.15, 0.10), "non batte nettamente la (b)"),
    "I-14-L": ((-0.15, 0.15), "non batte nettamente la (b)"),
    "I-15-S": ((-0.25, 0.10), "non batte nettamente la (b)"),
    "I-15-L": ((-0.10, 0.15), "non batte nettamente la (b)"),
}
