"""Le varianti della campagna 1000SHIBUSDT, scritte da ipotesi.md (un nome per variante).

Ogni variante e' una ``quadro.Variante``. Gli indicatori sono causali (``quadro``); la
condizione d'ingresso e' separata dal calcolo del segnale (stop e target), cosi' la (a)
e la (b) usano lo stesso segnale e la stessa uscita senza la condizione.
"""
from __future__ import annotations

import numpy as np

import quadro as q
from research.src import dati
from research.src.motore import Segnale

VARIANTI = {}


def registra(v):
    VARIANTI[v.id] = v
    return v


# --------------------------------------------------------------------------- #
# Pezzi comuni
# --------------------------------------------------------------------------- #


TETTO_STOP = 0.06  # stop_massimo_bot di parametri.yaml (ipotesi.md, regole comuni)


def segnale_atr(direzione, k, chiave="atr"):
    def f(i, ind, candele):
        a = ind[chiave][i]
        if np.isnan(a) or a <= 0:
            return None
        c = candele[i].close
        distanza = min(k * a, TETTO_STOP * c)
        stop = c - distanza if direzione == "long" else c + distanza
        if stop <= 0:
            return None
        return Segnale(direzione, stop)
    return f


def esci_dopo(n):
    def f(i, ind, candele, pos, barre):
        return barre >= n
    return f


def rendimenti(close):
    r = np.full(len(close), np.nan)
    r[1:] = close[1:] / close[:-1] - 1
    return r


def sigma_precedente(r, n):
    """Deviazione standard dei rendimenti delle n barre PRIMA di i (esclusa la barra i)."""
    return q.ritardato(q.deviazione_mobile(r, n), 1)


# --------------------------------------------------------------------------- #
# Controllo positivo (lookahead dichiarato): NON e' una variante
# --------------------------------------------------------------------------- #


def _prep_lookahead(candele, serie):
    o, c = q.arr(candele, "open"), q.arr(candele, "close")
    prossima_su = np.zeros(len(c))
    # lookahead DI PROPOSITO: legge la barra i+1 dalla lista intera
    prossima_su[:-1] = (c[1:] > o[1:]).astype(float)
    return {"atr": q.atr(candele, 14), "su": prossima_su}


registra(q.Variante(
    id="CONTROLLO", tf="4h", direzione="long", prepara=_prep_lookahead,
    ingresso=lambda i, ind: ind["su"][i] > 0.5,
    segnale=segnale_atr("long", 2.0), esci=esci_dopo(1), riscaldamento=15,
    descrizione={"nota": "controllo positivo con lookahead dichiarato"}))


# --------------------------------------------------------------------------- #
# I-01 Momento della serie (4h)
# --------------------------------------------------------------------------- #


def _prep_i01(candele, serie):
    c = q.arr(candele, "close")
    r42 = np.full(len(c), np.nan)
    r42[42:] = c[42:] / c[:-42] - 1
    return {"atr": q.atr(candele, 14), "r42": r42}


for nome, dirz, segno in (("I-01a", "long", 1), ("I-01b", "short", -1)):
    registra(q.Variante(
        id=nome, tf="4h", direzione=dirz, prepara=_prep_i01,
        ingresso=(lambda s: lambda i, ind: s * ind["r42"][i] > 0)(segno),
        segnale=segnale_atr(dirz, 3.0), esci=esci_dopo(18), riscaldamento=42,
        descrizione={"condizione": f"rendimento a 42 barre {'>' if segno > 0 else '<'} 0",
                     "uscita": "dopo 18 barre", "stop": "3 ATR(14)"}))


# --------------------------------------------------------------------------- #
# I-02 Inversione dopo barre estreme (1h)
# --------------------------------------------------------------------------- #


def _prep_i02(candele, serie):
    c = q.arr(candele, "close")
    r = rendimenti(c)
    return {"atr": q.atr(candele, 14), "r": r, "sig": sigma_precedente(r, 168)}


registra(q.Variante(
    id="I-02a", tf="1h", direzione="long", prepara=_prep_i02,
    ingresso=lambda i, ind: ind["r"][i] < -3 * ind["sig"][i],
    segnale=segnale_atr("long", 2.5), esci=esci_dopo(6), riscaldamento=169,
    descrizione={"condizione": "rendimento della barra < -3 sigma a 168", "uscita": "dopo 6 barre",
                 "stop": "2,5 ATR(14)"}))
registra(q.Variante(
    id="I-02b", tf="1h", direzione="short", prepara=_prep_i02,
    ingresso=lambda i, ind: ind["r"][i] > 3 * ind["sig"][i],
    segnale=segnale_atr("short", 2.5), esci=esci_dopo(6), riscaldamento=169,
    descrizione={"condizione": "rendimento della barra > +3 sigma a 168", "uscita": "dopo 6 barre",
                 "stop": "2,5 ATR(14)"}))


# --------------------------------------------------------------------------- #
# I-03 Donchian (4h)
# --------------------------------------------------------------------------- #


def _prep_i03(candele, serie):
    h, l = q.arr(candele, "high"), q.arr(candele, "low")
    return {"atr": q.atr(candele, 20), "c": q.arr(candele, "close"),
            "max20": q.ritardato(q.massimo_mobile(h, 20), 1), "min20": q.ritardato(q.minimo_mobile(l, 20), 1),
            "max10": q.ritardato(q.massimo_mobile(h, 10), 1), "min10": q.ritardato(q.minimo_mobile(l, 10), 1)}


registra(q.Variante(
    id="I-03a", tf="4h", direzione="long", prepara=_prep_i03,
    ingresso=lambda i, ind: ind["c"][i] > ind["max20"][i],
    segnale=segnale_atr("long", 2.0), esci=lambda i, ind, c, p, b: ind["c"][i] < ind["min10"][i],
    riscaldamento=21, descrizione={"condizione": "chiusura > massimo 20 barre precedenti",
                                    "uscita": "chiusura < minimo 10 barre precedenti", "stop": "2 ATR(20)"}))
registra(q.Variante(
    id="I-03b", tf="4h", direzione="short", prepara=_prep_i03,
    ingresso=lambda i, ind: ind["c"][i] < ind["min20"][i],
    segnale=segnale_atr("short", 2.0), esci=lambda i, ind, c, p, b: ind["c"][i] > ind["max10"][i],
    riscaldamento=21, descrizione={"condizione": "chiusura < minimo 20 barre precedenti",
                                    "uscita": "chiusura > massimo 10 barre precedenti", "stop": "2 ATR(20)"}))


# --------------------------------------------------------------------------- #
# I-04 Funding (4h)
# --------------------------------------------------------------------------- #


def _prep_i04(candele, serie):
    return {"atr": q.atr(candele, 14), "f": q.funding_ultimo(candele, serie.funding)}


registra(q.Variante(
    id="I-04a", tf="4h", direzione="short", prepara=_prep_i04,
    ingresso=lambda i, ind: ind["f"][i] >= 0.0003,
    segnale=segnale_atr("short", 3.0), esci=esci_dopo(18), riscaldamento=15,
    descrizione={"condizione": "ultimo funding >= 0,0003", "uscita": "dopo 18 barre", "stop": "3 ATR(14)"}))
registra(q.Variante(
    id="I-04b", tf="4h", direzione="long", prepara=_prep_i04,
    ingresso=lambda i, ind: ind["f"][i] < 0,
    segnale=segnale_atr("long", 3.0), esci=esci_dopo(18), riscaldamento=15,
    descrizione={"condizione": "ultimo funding < 0", "uscita": "dopo 18 barre", "stop": "3 ATR(14)"}))


# --------------------------------------------------------------------------- #
# I-05 Volume alto (4h)
# --------------------------------------------------------------------------- #


def _volume_usdt(candele, serie):
    vol = serie.info["volume_usdt"]
    return np.array([np.nan if vol.get(c.ts) is None else vol[c.ts] for c in candele])


def _prep_i05(candele, serie):
    v = _volume_usdt(candele, serie)
    s6 = np.full(len(v), np.nan)
    s300 = np.full(len(v), np.nan)
    cs = np.cumsum(np.insert(np.nan_to_num(v), 0, 0.0))
    for i in range(305, len(v)):
        s6[i] = cs[i + 1] - cs[i - 5]
        s300[i] = cs[i - 5] - cs[i - 305]  # le 300 barre prima delle ultime 6
    return {"atr": q.atr(candele, 14), "s6": s6, "media_giorno": s300 / 50}


registra(q.Variante(
    id="I-05a", tf="4h", direzione="long", prepara=_prep_i05,
    ingresso=lambda i, ind: ind["s6"][i] >= 2 * ind["media_giorno"][i],
    segnale=segnale_atr("long", 3.0), esci=esci_dopo(18), riscaldamento=306,
    descrizione={"condizione": "volume USDT 24h >= 2 x media giornaliera dei 50 giorni prima",
                 "uscita": "dopo 18 barre", "stop": "3 ATR(14)"}))


# --------------------------------------------------------------------------- #
# I-06 Gonfia e sgonfia (15m)
# --------------------------------------------------------------------------- #


def _prep_i06(candele, serie):
    c = q.arr(candele, "close")
    v = _volume_usdt(candele, serie)
    media96 = q.ritardato(q.media_mobile(np.nan_to_num(v), 96), 1)
    return {"atr": q.atr(candele, 14), "r": rendimenti(c), "v": v, "m96": media96}


registra(q.Variante(
    id="I-06a", tf="15m", direzione="short", prepara=_prep_i06,
    ingresso=lambda i, ind: ind["r"][i] >= 0.04 and ind["v"][i] >= 5 * ind["m96"][i],
    segnale=segnale_atr("short", 2.0), esci=esci_dopo(16), riscaldamento=97,
    descrizione={"condizione": "rendimento barra >= 4% e volume USDT >= 5 x media 96 barre precedenti",
                 "uscita": "dopo 16 barre", "stop": "2 ATR(14)"}))


# --------------------------------------------------------------------------- #
# I-07 Lunedi' (1d)
# --------------------------------------------------------------------------- #


def _prep_i07(candele, serie):
    return {"atr": q.atr(candele, 14), "gs": q.giorno_settimana(candele).astype(float)}


registra(q.Variante(
    id="I-07a", tf="1d", direzione="long", prepara=_prep_i07,
    ingresso=lambda i, ind: ind["gs"][i] == 6,
    segnale=segnale_atr("long", 2.0), esci=esci_dopo(1), riscaldamento=15,
    descrizione={"condizione": "barra di segnale = domenica UTC (ingresso lunedi' 00:00)",
                 "uscita": "dopo 1 barra", "stop": "2 ATR(14) giornaliero"}))


# --------------------------------------------------------------------------- #
# I-08 Momento interno al giorno (30m)
# --------------------------------------------------------------------------- #


def _prep_i08(candele, serie):
    o, c = q.arr(candele, "open"), q.arr(candele, "close")
    ts = np.array([x.ts for x in candele])
    giorno = ts // dati.MS_GIORNO
    minuto = (ts % dati.MS_GIORNO) // 60000
    prima = {}
    for k in range(len(candele)):
        if minuto[k] == 0:
            prima[giorno[k]] = c[k] / o[k] - 1
    r_prima = np.full(len(c), np.nan)
    for k in range(len(candele)):
        if minuto[k] == 23 * 60 and giorno[k] in prima:
            r_prima[k] = prima[giorno[k]]
    return {"atr": q.atr(candele, 14), "r_prima": r_prima}


registra(q.Variante(
    id="I-08a", tf="30m", direzione="long", prepara=_prep_i08,
    ingresso=lambda i, ind: ind["r_prima"][i] > 0,
    segnale=segnale_atr("long", 2.0), esci=esci_dopo(1), riscaldamento=48,
    descrizione={"condizione": "barra 23:00 UTC e rendimento della barra 00:00 dello stesso giorno > 0",
                 "uscita": "dopo 1 barra", "stop": "2 ATR(14)"}))
registra(q.Variante(
    id="I-08b", tf="30m", direzione="short", prepara=_prep_i08,
    ingresso=lambda i, ind: ind["r_prima"][i] < 0,
    segnale=segnale_atr("short", 2.0), esci=esci_dopo(1), riscaldamento=48,
    descrizione={"condizione": "barra 23:00 UTC e rendimento della barra 00:00 dello stesso giorno < 0",
                 "uscita": "dopo 1 barra", "stop": "2 ATR(14)"}))


# --------------------------------------------------------------------------- #
# I-09 Bitcoin guida (1h)
# --------------------------------------------------------------------------- #


def _prep_i09(candele, serie):
    c = q.arr(candele, "close")
    r = rendimenti(c)
    rb = np.full(len(c), np.nan)
    for k, x in enumerate(candele):
        b = serie.btc.get(x.ts)
        if b is not None:
            rb[k] = b.close / b.open - 1
    # sigma di BTC sulle 168 barre prima (ignora i buchi)
    sb = np.full(len(c), np.nan)
    for k in range(169, len(c)):
        fin = rb[k - 168:k]
        fin = fin[~np.isnan(fin)]
        if len(fin) > 100:
            sb[k] = np.std(fin, ddof=1)
    return {"atr": q.atr(candele, 14), "r": r, "rb": rb, "sb": sb}


registra(q.Variante(
    id="I-09a", tf="1h", direzione="long", prepara=_prep_i09, con_btc=True,
    ingresso=lambda i, ind: ind["rb"][i] > 2 * ind["sb"][i] and ind["r"][i] < ind["rb"][i],
    segnale=segnale_atr("long", 2.5), esci=esci_dopo(3), riscaldamento=169,
    descrizione={"condizione": "rendimento BTC > 2 sigma_BTC(168) e rendimento SHIB < rendimento BTC",
                 "uscita": "dopo 3 barre", "stop": "2,5 ATR(14)"}))
registra(q.Variante(
    id="I-09b", tf="1h", direzione="short", prepara=_prep_i09, con_btc=True,
    ingresso=lambda i, ind: ind["rb"][i] < -2 * ind["sb"][i] and ind["r"][i] > ind["rb"][i],
    segnale=segnale_atr("short", 2.5), esci=esci_dopo(3), riscaldamento=169,
    descrizione={"condizione": "rendimento BTC < -2 sigma_BTC(168) e rendimento SHIB > rendimento BTC",
                 "uscita": "dopo 3 barre", "stop": "2,5 ATR(14)"}))


# --------------------------------------------------------------------------- #
# I-10 Compressione e rottura delle bande (4h)
# --------------------------------------------------------------------------- #


def _prep_i10(candele, serie):
    c = q.arr(candele, "close")
    m = q.media_mobile(c, 20)
    s = q.deviazione_mobile(c, 20)
    amp = 4 * s / m
    min120 = q.ritardato(q.minimo_mobile(amp, 120), 1)
    alla_minima = (amp <= min120).astype(float)
    alla_minima[np.isnan(min120)] = np.nan
    recente = np.full(len(c), np.nan)
    for k in range(140, len(c)):
        recente[k] = np.nanmax(alla_minima[k - 5:k + 1])
    return {"atr": q.atr(candele, 14), "c": c, "m": m, "su": m + 2 * s, "giu": m - 2 * s, "sq": recente}


registra(q.Variante(
    id="I-10a", tf="4h", direzione="long", prepara=_prep_i10,
    ingresso=lambda i, ind: ind["sq"][i] > 0.5 and ind["c"][i] > ind["su"][i],
    segnale=segnale_atr("long", 2.0), esci=lambda i, ind, c, p, b: ind["c"][i] < ind["m"][i],
    riscaldamento=140, descrizione={"condizione": "ampiezza bande al minimo di 120 barre nelle ultime 6 e chiusura > banda alta",
                                     "uscita": "chiusura < media 20", "stop": "2 ATR(14)"}))
registra(q.Variante(
    id="I-10b", tf="4h", direzione="short", prepara=_prep_i10,
    ingresso=lambda i, ind: ind["sq"][i] > 0.5 and ind["c"][i] < ind["giu"][i],
    segnale=segnale_atr("short", 2.0), esci=lambda i, ind, c, p, b: ind["c"][i] > ind["m"][i],
    riscaldamento=140, descrizione={"condizione": "ampiezza bande al minimo di 120 barre nelle ultime 6 e chiusura < banda bassa",
                                     "uscita": "chiusura > media 20", "stop": "2 ATR(14)"}))


# --------------------------------------------------------------------------- #
# I-11 RSI a 2 in tendenza (4h)
# --------------------------------------------------------------------------- #


def _prep_i11(candele, serie):
    c = q.arr(candele, "close")
    return {"atr": q.atr(candele, 14), "c": c, "m200": q.media_mobile(c, 200), "m5": q.media_mobile(c, 5),
            "rsi2": q.rsi(c, 2)}


registra(q.Variante(
    id="I-11a", tf="4h", direzione="long", prepara=_prep_i11,
    ingresso=lambda i, ind: ind["c"][i] > ind["m200"][i] and ind["rsi2"][i] < 10,
    segnale=segnale_atr("long", 3.0), esci=lambda i, ind, c, p, b: ind["c"][i] > ind["m5"][i],
    riscaldamento=200, descrizione={"condizione": "chiusura > media 200 e RSI(2) < 10",
                                     "uscita": "chiusura > media 5", "stop": "3 ATR(14)"}))
registra(q.Variante(
    id="I-11b", tf="4h", direzione="short", prepara=_prep_i11,
    ingresso=lambda i, ind: ind["c"][i] < ind["m200"][i] and ind["rsi2"][i] > 90,
    segnale=segnale_atr("short", 3.0), esci=lambda i, ind, c, p, b: ind["c"][i] < ind["m5"][i],
    riscaldamento=200, descrizione={"condizione": "chiusura < media 200 e RSI(2) > 90",
                                     "uscita": "chiusura < media 5", "stop": "3 ATR(14)"}))


# --------------------------------------------------------------------------- #
# I-12 Squilibrio degli aggressori (1h)
# --------------------------------------------------------------------------- #

_TAKER = {}


def quota_aggressiva_per_ts(tf):
    """{ts: (quote_volume, taker_buy_quote_volume)} dai file klines del timeframe."""
    if tf not in _TAKER:
        out = {}
        for p in sorted((q.CARTELLA_DATI / "klines" / tf).glob("*.zip")):
            for riga in dati.righe_csv_da_zip(p):
                ts = dati.normalizza_ts(riga[0])
                if ts in out or len(riga) < 11:
                    continue
                out[ts] = (float(riga[7]), float(riga[10]))
        _TAKER[tf] = out
    return _TAKER[tf]


def _prep_i12(candele, serie):
    tab = quota_aggressiva_per_ts("1h")
    qv = np.array([tab.get(c.ts, (np.nan, np.nan))[0] for c in candele])
    tb = np.array([tab.get(c.ts, (np.nan, np.nan))[1] for c in candele])
    quota = np.full(len(candele), np.nan)
    for k in range(23, len(candele)):
        a, b = np.nansum(qv[k - 23:k + 1]), np.nansum(tb[k - 23:k + 1])
        if a > 0:
            quota[k] = b / a
    p90 = np.full(len(candele), np.nan)
    p10 = np.full(len(candele), np.nan)
    for k in range(744, len(candele)):
        fin = quota[k - 720:k]
        fin = fin[~np.isnan(fin)]
        if len(fin) > 500:
            p90[k] = np.percentile(fin, 90)
            p10[k] = np.percentile(fin, 10)
    return {"atr": q.atr(candele, 14), "quota": quota, "p90": p90, "p10": p10}


registra(q.Variante(
    id="I-12a", tf="1h", direzione="long", prepara=_prep_i12,
    ingresso=lambda i, ind: ind["quota"][i] > ind["p90"][i],
    segnale=segnale_atr("long", 3.0), esci=esci_dopo(24), riscaldamento=744,
    descrizione={"condizione": "quota aggressiva in acquisto a 24 barre > 90 percentile delle 720 barre precedenti",
                 "uscita": "dopo 24 barre", "stop": "3 ATR(14)"}))
registra(q.Variante(
    id="I-12b", tf="1h", direzione="short", prepara=_prep_i12,
    ingresso=lambda i, ind: ind["quota"][i] < ind["p10"][i],
    segnale=segnale_atr("short", 3.0), esci=esci_dopo(24), riscaldamento=744,
    descrizione={"condizione": "quota aggressiva in acquisto a 24 barre < 10 percentile delle 720 barre precedenti",
                 "uscita": "dopo 24 barre", "stop": "3 ATR(14)"}))


# --------------------------------------------------------------------------- #
# Varianti allentate delle idee scartate per pochi trade (ipotesi.md)
# --------------------------------------------------------------------------- #

for nome, base in (("I-03c", "I-03a"), ("I-03d", "I-03b")):
    b = VARIANTI[base]
    registra(q.Variante(id=nome, tf="2h", direzione=b.direzione, prepara=b.prepara, ingresso=b.ingresso,
                        segnale=b.segnale, esci=b.esci, riscaldamento=b.riscaldamento,
                        descrizione=dict(b.descrizione, timeframe="2h")))

registra(q.Variante(
    id="I-04c", tf="4h", direzione="short", prepara=_prep_i04,
    ingresso=lambda i, ind: ind["f"][i] >= 0.0002,
    segnale=segnale_atr("short", 3.0), esci=esci_dopo(18), riscaldamento=15,
    descrizione={"condizione": "ultimo funding >= 0,0002", "uscita": "dopo 18 barre", "stop": "3 ATR(14)"}))

registra(q.Variante(
    id="I-05b", tf="4h", direzione="long", prepara=_prep_i05,
    ingresso=lambda i, ind: ind["s6"][i] >= 1.5 * ind["media_giorno"][i],
    segnale=segnale_atr("long", 3.0), esci=esci_dopo(18), riscaldamento=306,
    descrizione={"condizione": "volume USDT 24h >= 1,5 x media giornaliera dei 50 giorni prima",
                 "uscita": "dopo 18 barre", "stop": "3 ATR(14)"}))

registra(q.Variante(
    id="I-06b", tf="15m", direzione="short", prepara=_prep_i06,
    ingresso=lambda i, ind: ind["r"][i] >= 0.03 and ind["v"][i] >= 5 * ind["m96"][i],
    segnale=segnale_atr("short", 2.0), esci=esci_dopo(16), riscaldamento=97,
    descrizione={"condizione": "rendimento barra >= 3% e volume USDT >= 5 x media 96 barre precedenti",
                 "uscita": "dopo 16 barre", "stop": "2 ATR(14)"}))


def _prep_i10_1h(candele, serie):
    c = q.arr(candele, "close")
    m = q.media_mobile(c, 20)
    s = q.deviazione_mobile(c, 20)
    amp = 4 * s / m
    min120 = q.ritardato(q.minimo_mobile(amp, 120), 1)
    alla_minima = (amp <= min120).astype(float)
    alla_minima[np.isnan(min120)] = np.nan
    recente = np.full(len(c), np.nan)
    for k in range(152, len(c)):
        recente[k] = np.nanmax(alla_minima[k - 11:k + 1])
    return {"atr": q.atr(candele, 14), "c": c, "m": m, "su": m + 2 * s, "giu": m - 2 * s, "sq": recente}


registra(q.Variante(
    id="I-10c", tf="1h", direzione="long", prepara=_prep_i10_1h,
    ingresso=lambda i, ind: ind["sq"][i] > 0.5 and ind["c"][i] > ind["su"][i],
    segnale=segnale_atr("long", 2.0), esci=lambda i, ind, c, p, b: ind["c"][i] < ind["m"][i],
    riscaldamento=152, descrizione={"condizione": "ampiezza bande al minimo di 120 barre nelle ultime 12 e chiusura > banda alta",
                                     "uscita": "chiusura < media 20", "stop": "2 ATR(14)"}))
registra(q.Variante(
    id="I-10d", tf="1h", direzione="short", prepara=_prep_i10_1h,
    ingresso=lambda i, ind: ind["sq"][i] > 0.5 and ind["c"][i] < ind["giu"][i],
    segnale=segnale_atr("short", 2.0), esci=lambda i, ind, c, p, b: ind["c"][i] > ind["m"][i],
    riscaldamento=152, descrizione={"condizione": "ampiezza bande al minimo di 120 barre nelle ultime 12 e chiusura < banda bassa",
                                     "uscita": "chiusura > media 20", "stop": "2 ATR(14)"}))


# --------------------------------------------------------------------------- #
# I-13 Momento dopo un rendimento anomalo (4h)
# --------------------------------------------------------------------------- #


def _prep_i13(candele, serie):
    c = q.arr(candele, "close")
    r = rendimenti(c)
    return {"atr": q.atr(candele, 14), "r": r, "sig": sigma_precedente(r, 120)}


registra(q.Variante(
    id="I-13a", tf="4h", direzione="long", prepara=_prep_i13,
    ingresso=lambda i, ind: ind["r"][i] > 2 * ind["sig"][i],
    segnale=segnale_atr("long", 2.0), esci=esci_dopo(6), riscaldamento=121,
    descrizione={"condizione": "rendimento della barra > 2 sigma a 120", "uscita": "dopo 6 barre", "stop": "2 ATR(14)"}))
registra(q.Variante(
    id="I-13b", tf="4h", direzione="short", prepara=_prep_i13,
    ingresso=lambda i, ind: ind["r"][i] < -2 * ind["sig"][i],
    segnale=segnale_atr("short", 2.0), esci=esci_dopo(6), riscaldamento=121,
    descrizione={"condizione": "rendimento della barra < -2 sigma a 120", "uscita": "dopo 6 barre", "stop": "2 ATR(14)"}))


# --------------------------------------------------------------------------- #
# I-14 Incrocio con la media a 50 (4h)
# --------------------------------------------------------------------------- #


def _prep_i14(candele, serie):
    c = q.arr(candele, "close")
    m = q.media_mobile(c, 50)
    return {"atr": q.atr(candele, 14), "c": c, "m": m, "c1": q.ritardato(c, 1), "m1": q.ritardato(m, 1)}


registra(q.Variante(
    id="I-14a", tf="4h", direzione="long", prepara=_prep_i14,
    ingresso=lambda i, ind: ind["c"][i] > ind["m"][i] and ind["c1"][i] <= ind["m1"][i],
    segnale=segnale_atr("long", 2.0), esci=esci_dopo(10), riscaldamento=51,
    descrizione={"condizione": "chiusura incrocia dal basso la media 50", "uscita": "dopo 10 barre", "stop": "2 ATR(14)"}))
# --------------------------------------------------------------------------- #
# Ritocchi (regola 6), nell'ordine del log
# --------------------------------------------------------------------------- #

registra(q.Variante(
    id="R1-I-08b", tf="30m", direzione="short", prepara=_prep_i08,
    ingresso=lambda i, ind: ind["r_prima"][i] <= -0.009,
    segnale=segnale_atr("short", 2.0), esci=esci_dopo(1), riscaldamento=48,
    descrizione={"ritocco_di": "I-08b", "condizione": "barra 23:00 UTC e rendimento della barra 00:00 <= -0,9%",
                 "uscita": "dopo 1 barra", "stop": "2 ATR(14)"}))


def _prep_r2_i08b(candele, serie):
    ind = _prep_i08(candele, serie)
    o, c = q.arr(candele, "open"), q.arr(candele, "close")
    ind["r_penultima"] = c / o - 1  # rendimento della barra di segnale (23:00-23:30)
    return ind


registra(q.Variante(
    id="R2-I-08b", tf="30m", direzione="short", prepara=_prep_r2_i08b,
    ingresso=lambda i, ind: ind["r_prima"][i] <= -0.009 and ind["r_penultima"][i] < 0,
    segnale=segnale_atr("short", 2.0), esci=esci_dopo(1), riscaldamento=48,
    descrizione={"ritocco_di": "I-08b", "condizione": "barra 23:00 UTC, rendimento della barra 00:00 <= -0,9% "
                 "e rendimento della barra 23:00 < 0", "uscita": "dopo 1 barra", "stop": "2 ATR(14)"}))


def _prep_r3_i08b(candele, serie):
    ind = _prep_i08(candele, serie)
    o, c = q.arr(candele, "open"), q.arr(candele, "close")
    ts = np.array([x.ts for x in candele])
    giorno = ts // dati.MS_GIORNO
    minuto = (ts % dati.MS_GIORNO) // 60000
    apertura = {}
    for j in range(len(candele)):
        if minuto[j] == 0:
            apertura[giorno[j]] = o[j]
    r_giorno = np.full(len(c), np.nan)
    for j in range(len(candele)):
        if minuto[j] == 23 * 60 and giorno[j] in apertura:
            r_giorno[j] = c[j] / apertura[giorno[j]] - 1  # dalle 00:00 alla chiusura delle 23:30
    ind["r_giorno"] = r_giorno
    return ind


registra(q.Variante(
    id="R3-I-08b", tf="30m", direzione="short", prepara=_prep_r3_i08b,
    ingresso=lambda i, ind: ind["r_prima"][i] <= -0.009 and ind["r_giorno"][i] < 0,
    segnale=segnale_atr("short", 2.0), esci=esci_dopo(1), riscaldamento=48,
    descrizione={"ritocco_di": "I-08b", "condizione": "barra 23:00 UTC, rendimento della barra 00:00 <= -0,9% "
                 "e rendimento del giorno fino alle 23:30 < 0", "uscita": "dopo 1 barra", "stop": "2 ATR(14)"}))


registra(q.Variante(
    id="R4-I-08b", tf="30m", direzione="short", prepara=_prep_r3_i08b,
    ingresso=lambda i, ind: ind["r_prima"][i] < 0 and ind["r_giorno"][i] < 0,
    segnale=segnale_atr("short", 2.0), esci=esci_dopo(1), riscaldamento=48,
    descrizione={"ritocco_di": "I-08b", "condizione": "barra 23:00 UTC, rendimento della barra 00:00 < 0 "
                 "e rendimento del giorno fino alle 23:30 < 0", "uscita": "dopo 1 barra", "stop": "2 ATR(14)"}))


registra(q.Variante(
    id="R5-I-08b", tf="30m", direzione="short", prepara=_prep_r3_i08b,
    ingresso=lambda i, ind: ind["r_prima"][i] <= -0.005 and ind["r_giorno"][i] < 0,
    segnale=segnale_atr("short", 2.0), esci=esci_dopo(1), riscaldamento=48,
    descrizione={"ritocco_di": "R4-I-08b", "condizione": "barra 23:00 UTC, rendimento della barra 00:00 <= -0,5% "
                 "e rendimento del giorno fino alle 23:30 < 0", "uscita": "dopo 1 barra", "stop": "2 ATR(14)"}))


def fai_r1_i08b(nome, tf="30m", soglia=-0.009, k=2.0, n_atr=14, uscita=1, minuto_segnale=None,
                barre_prima=1, filtro_giorno=False):
    """Le regole di R1-I-08b con parametri spostati (verifiche di Fase 4).

    ``barre_prima``: quante barre del timeframe formano la prima mezz'ora (2 a 15m, 1 a 30m e,
    per definizione, la prima ora a 1h); ``minuto_segnale``: il minuto del giorno della barra
    di segnale (la barra che chiude quando inizia l'ultima mezz'ora, o l'ultima ora a 1h).
    """
    ms = q.MS[tf]
    if minuto_segnale is None:
        minuto_segnale = 24 * 60 - 30 - ms // 60000

    def prep(candele, serie):
        o, c = q.arr(candele, "open"), q.arr(candele, "close")
        ts = np.array([x.ts for x in candele])
        giorno = ts // dati.MS_GIORNO
        minuto = (ts % dati.MS_GIORNO) // 60000
        apertura, chiusura = {}, {}
        for j in range(len(candele)):
            if minuto[j] == 0:
                apertura[giorno[j]] = o[j]
            if minuto[j] == (barre_prima - 1) * ms // 60000:
                chiusura[giorno[j]] = c[j]
        r_prima = np.full(len(c), np.nan)
        r_giorno = np.full(len(c), np.nan)
        for j in range(len(candele)):
            g = giorno[j]
            if minuto[j] == minuto_segnale and g in apertura and g in chiusura:
                r_prima[j] = chiusura[g] / apertura[g] - 1
                r_giorno[j] = c[j] / apertura[g] - 1
        return {"atr": q.atr(candele, n_atr), "r_prima": r_prima, "r_giorno": r_giorno}

    if filtro_giorno:
        ingresso = lambda i, ind: ind["r_prima"][i] <= soglia and ind["r_giorno"][i] < 0  # noqa: E731
    else:
        ingresso = lambda i, ind: ind["r_prima"][i] <= soglia  # noqa: E731
    return q.Variante(
        id=nome, tf=tf, direzione="short", prepara=prep,
        ingresso=ingresso,
        segnale=segnale_atr("short", k), esci=esci_dopo(uscita), riscaldamento=max(48, n_atr + 1),
        descrizione={"base": "R1-I-08b", "tf": tf, "soglia": soglia, "k": k, "n_atr": n_atr, "uscita": uscita})


for _nome, _kw in {
    "R1-I-08b_soglia_-0.0072": {"soglia": -0.0072}, "R1-I-08b_soglia_-0.0108": {"soglia": -0.0108},
    "R1-I-08b_k_1.6": {"k": 1.6}, "R1-I-08b_k_2.4": {"k": 2.4},
    "R1-I-08b_atr_11": {"n_atr": 11}, "R1-I-08b_atr_17": {"n_atr": 17},
    "R1-I-08b_uscita_2": {"uscita": 2},
    "R1-I-08b_tf_15m": {"tf": "15m", "n_atr": 28, "uscita": 2, "barre_prima": 2},
    "R1-I-08b_tf_1h": {"tf": "1h", "n_atr": 7, "uscita": 1, "barre_prima": 1, "minuto_segnale": 22 * 60},
    "R1-I-08b_copia": {},
}.items():
    registra(fai_r1_i08b(_nome, **_kw))

for _nome, _kw in {
    "R5-I-08b_soglia_-0.004": {"soglia": -0.004}, "R5-I-08b_soglia_-0.006": {"soglia": -0.006},
    "R5-I-08b_k_1.6": {"k": 1.6}, "R5-I-08b_k_2.4": {"k": 2.4},
    "R5-I-08b_atr_11": {"n_atr": 11}, "R5-I-08b_atr_17": {"n_atr": 17},
    "R5-I-08b_uscita_2": {"uscita": 2},
    "R5-I-08b_tf_15m": {"tf": "15m", "n_atr": 28, "uscita": 2, "barre_prima": 2},
    "R5-I-08b_tf_1h": {"tf": "1h", "n_atr": 7, "uscita": 1, "barre_prima": 1, "minuto_segnale": 22 * 60},
    "R5-I-08b_copia": {},
    # Fase 5, prova dello scettico: le stesse regole a un'ora diversa (non l'ultima mezz'ora)
    "R5-I-08b_ora_11": {"minuto_segnale": 11 * 60},
    "R5-I-08b_ora_17": {"minuto_segnale": 17 * 60},
}.items():
    registra(fai_r1_i08b(_nome, **dict({"soglia": -0.005, "filtro_giorno": True}, **_kw)))


def _prep_i15(candele, serie):
    c = q.arr(candele, "close")
    c1 = q.ritardato(c, 1)
    su = np.zeros(len(c))
    giu = np.zeros(len(c))
    for k in range(1, len(c)):
        a, b = c1[k], c[k]
        passo = 10.0 ** (np.floor(np.log10(b)) - 1)
        if a < b:
            # esiste L = n*passo con a < L <= b ?
            if np.floor(b / passo + 1e-9) * passo > a + 1e-15:
                su[k] = 1
        elif a > b:
            passo_a = 10.0 ** (np.floor(np.log10(a)) - 1)
            p = min(passo, passo_a)
            if np.ceil(b / p - 1e-9) * p < a - 1e-15:
                giu[k] = 1
    return {"atr": q.atr(candele, 14), "su": su, "giu": giu}


registra(q.Variante(
    id="I-15a", tf="1h", direzione="long", prepara=_prep_i15,
    ingresso=lambda i, ind: ind["su"][i] > 0.5,
    segnale=segnale_atr("long", 2.5), esci=esci_dopo(6), riscaldamento=15,
    descrizione={"condizione": "la chiusura attraversa verso l'alto un prezzo con due cifre significative",
                 "uscita": "dopo 6 barre", "stop": "2,5 ATR(14)"}))
registra(q.Variante(
    id="I-15b", tf="1h", direzione="short", prepara=_prep_i15,
    ingresso=lambda i, ind: ind["giu"][i] > 0.5,
    segnale=segnale_atr("short", 2.5), esci=esci_dopo(6), riscaldamento=15,
    descrizione={"condizione": "la chiusura attraversa verso il basso un prezzo con due cifre significative",
                 "uscita": "dopo 6 barre", "stop": "2,5 ATR(14)"}))


def _prep_i16(candele, serie):
    c = q.arr(candele, "close")
    r6 = np.full(len(c), np.nan)
    r6[6:] = c[6:] / c[:-6] - 1
    return {"atr": q.atr(candele, 14), "max30": q.massimo_mobile(np.nan_to_num(r6, nan=-1.0), 180)}


registra(q.Variante(
    id="I-16a", tf="4h", direzione="short", prepara=_prep_i16,
    ingresso=lambda i, ind: ind["max30"][i] >= 0.25,
    segnale=segnale_atr("short", 3.0), esci=esci_dopo(18), riscaldamento=186,
    descrizione={"condizione": "massimo dei rendimenti a 24 ore delle ultime 180 barre >= 25%",
                 "uscita": "dopo 18 barre", "stop": "3 ATR(14)"}))


registra(q.Variante(
    id="I-14b", tf="4h", direzione="short", prepara=_prep_i14,
    ingresso=lambda i, ind: ind["c"][i] < ind["m"][i] and ind["c1"][i] >= ind["m1"][i],
    segnale=segnale_atr("short", 2.0), esci=esci_dopo(10), riscaldamento=51,
    descrizione={"condizione": "chiusura incrocia dall'alto la media 50", "uscita": "dopo 10 barre", "stop": "2 ATR(14)"}))
