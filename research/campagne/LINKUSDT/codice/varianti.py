"""Le varianti della campagna LINKUSDT, scritte come in ipotesi.md PRIMA dei test.

Ogni variante: ``VARIANTI[id]`` con idea, fonte, meccanismo, timeframe, direzione, parametri,
previsione, e la funzione ``prepara(candele, extra) -> comune.Prep``. Gli indicatori usano solo
barre chiuse (``indicatori.py``). L'uscita "dopo H barre" chiude all'apertura della barra H dopo
l'ingresso: la posizione resta aperta H barre.
"""
from __future__ import annotations

import bisect
import math
from typing import Callable, Dict

import numpy as np

import comune as C
import indicatori as I
from research.src.motore import Segnale

CRITERIO = ("batte nettamente la (a) e la (b) in costruzione (contro_baseline) con R medio dopo i costi "
            "positivo: allora e' un candidato (sezione 8)")


def extra_per(tf: str) -> Dict[str, object]:
    s = C.serie(tf)
    return {"funding": C.funding(), "taker": C.taker_buy_quote(tf), "volume": s["volume_usdt"]}


def _stop_atr(direzione: str, k: float, c: np.ndarray, a: np.ndarray):
    def segnale(i):
        if i >= len(c) or not I.ok(a[i]) or a[i] <= 0:
            return None
        if direzione == "long":
            return Segnale("long", c[i] - k * a[i])
        return Segnale("short", c[i] + k * a[i])
    return segnale


def _dopo(h: int):
    return lambda i, ie: i - ie + 1 >= h


def costruttore(direzione: str, k_atr: float, h: int, condizione: Callable):
    """Variante standard: condizione(candele, extra) -> funzione entra(i); stop k ATR(14); uscita dopo h barre."""
    def prepara(candele, extra):
        c = I.arr(candele, "close")
        a = I.atr(candele, 14)
        return C.Prep(condizione(candele, extra), _stop_atr(direzione, k_atr, c, a), _dopo(h))
    return prepara


# ---------------------------------------------------------------------------
# Condizioni d'ingresso
# ---------------------------------------------------------------------------


def cond_rend_k(k: int, segno: int):
    def f(candele, extra):
        r = I.rendimenti(I.arr(candele, "close"), k)
        return lambda i: I.ok(r[i]) and (r[i] > 0 if segno > 0 else r[i] < 0)
    return f


def cond_rottura(n: int, segno: int):
    def f(candele, extra):
        c = I.arr(candele, "close")
        if segno > 0:
            liv = I.max_precedente(I.arr(candele, "high"), n)
            return lambda i: I.ok(liv[i]) and c[i] > liv[i]
        liv = I.min_precedente(I.arr(candele, "low"), n)
        return lambda i: I.ok(liv[i]) and c[i] < liv[i]
    return f


def cond_z_estremo(n: int, z: float, segno: int):
    def f(candele, extra):
        r = I.rendimenti(I.arr(candele, "close"), 1)
        s = I.std_precedente(r, n)
        if segno < 0:
            return lambda i: I.ok(r[i], s[i]) and s[i] > 0 and r[i] < -z * s[i]
        return lambda i: I.ok(r[i], s[i]) and s[i] > 0 and r[i] > z * s[i]
    return f


def cond_prima_mezzora(segno: int):
    """Alla chiusura della barra 23:00-23:30 UTC: segno della mezz'ora 00:00-00:30 dello stesso giorno."""
    def f(candele, extra):
        prima: Dict[str, float] = {}
        for c in candele:
            d = I.utc(c.ts)
            if d.hour == 0 and d.minute == 0:
                prima[d.strftime("%Y-%m-%d")] = c.close - c.open

        def entra(i):
            d = I.utc(candele[i].ts)
            if not (d.hour == 23 and d.minute == 0):
                return False
            v = prima.get(d.strftime("%Y-%m-%d"))
            return v is not None and (v > 0 if segno > 0 else v < 0)
        return entra
    return f


def cond_domenica():
    def f(candele, extra):
        return lambda i: I.utc(candele[i].ts).weekday() == 6
    return f


def cond_funding(n: int, q: float, segno: int):
    def f(candele, extra):
        fund = extra["funding"]
        ts = [t for t, _ in fund]
        tassi = np.array([r for _, r in fund], dtype=float)
        soglia = I.quantile_precedente(tassi, n, q)

        def entra(i):
            k = bisect.bisect_right(ts, candele[i].close_ts) - 1
            if k < 0 or not I.ok(soglia[k]):
                return False
            return tassi[k] > soglia[k] if segno > 0 else tassi[k] < soglia[k]
        return entra
    return f


def cond_volume_alto(n: int, primi: int):
    def f(candele, extra):
        vol = np.array([extra["volume"].get(c.ts) or math.nan for c in candele], dtype=float)

        def entra(i):
            if i < n - 1:
                return False
            finestra = vol[i - n + 1:i + 1]
            if np.isnan(finestra).any():
                return False
            return int((finestra > vol[i]).sum()) < primi
        return entra
    return f


def cond_squilibrio(n: int, q: float, segno: int):
    def f(candele, extra):
        tk = extra["taker"]
        vol = extra["volume"]
        quota = np.array([(tk.get(c.ts) / vol[c.ts]) if (tk.get(c.ts) is not None and vol.get(c.ts)) else math.nan
                          for c in candele], dtype=float)
        soglia = I.quantile_precedente(quota, n, q)
        if segno > 0:
            return lambda i: I.ok(quota[i], soglia[i]) and quota[i] > soglia[i]
        return lambda i: I.ok(quota[i], soglia[i]) and quota[i] < soglia[i]
    return f


def prepara_williams(segno: int, k: float, k_atr: float):
    """Prima ora del giorno UTC oltre apertura +- k x escursione di ieri; uscita a fine giorno UTC."""
    def prepara(candele, extra):
        c = I.arr(candele, "close")
        a = I.atr(candele, 14)
        giorno = [I.utc(x.ts).strftime("%Y-%m-%d") for x in candele]
        ora = [I.utc(x.ts).hour for x in candele]
        apertura: Dict[str, float] = {}
        alto: Dict[str, float] = {}
        basso: Dict[str, float] = {}
        n_barre: Dict[str, int] = {}
        for x, g in zip(candele, giorno):
            if g not in apertura and I.utc(x.ts).hour == 0:
                apertura[g] = x.open
            alto[g] = max(alto.get(g, -math.inf), x.high)
            basso[g] = min(basso.get(g, math.inf), x.low)
            n_barre[g] = n_barre.get(g, 0) + 1
        giorni = sorted(n_barre)
        ieri = {g: giorni[k_] for k_, g in enumerate(giorni[1:], start=0)}
        # escursione di ieri solo se ieri e' completo (24 barre) e precede davvero di un giorno
        from datetime import date, timedelta
        primo_trigger: Dict[str, int] = {}
        for i in range(len(candele)):
            g = giorno[i]
            if g in primo_trigger or g not in apertura or ora[i] == 23:
                continue
            y = ieri.get(g)
            if y is None or n_barre.get(y) != 24 or date.fromisoformat(g) - date.fromisoformat(y) != timedelta(days=1):
                continue
            esc = alto[y] - basso[y]
            soglia = apertura[g] + segno * k * esc
            if (segno > 0 and c[i] > soglia) or (segno < 0 and c[i] < soglia):
                primo_trigger[g] = i
        # nota: alto/basso del giorno g contengono barre future di g, ma qui si usano solo per IERI
        trigger = set(primo_trigger.values())

        def esci(i, ie):
            return ora[i] == 23 or giorno[i] != giorno[ie]
        return C.Prep(lambda i: i in trigger, _stop_atr("long" if segno > 0 else "short", k_atr, c, a), esci)
    return prepara


def prepara_connors(rsi_soglia: float, n_lunga: int, n_corta: int, k_atr: float, h_max: int):
    def prepara(candele, extra):
        c = I.arr(candele, "close")
        a = I.atr(candele, 14)
        s200 = I.sma(c, n_lunga)
        s5 = I.sma(c, n_corta)
        r2 = I.rsi(c, 2)

        def entra(i):
            return I.ok(s200[i], r2[i]) and c[i] > s200[i] and r2[i] < rsi_soglia

        def esci(i, ie):
            return (I.ok(s5[i]) and c[i] > s5[i]) or (i - ie + 1 >= h_max)
        return C.Prep(entra, _stop_atr("long", k_atr, c, a), esci)
    return prepara


def _passo_tondo(p: float) -> float:
    return 10 ** math.floor(math.log10(p)) / 2


def cond_numero_tondo(segno: int):
    def f(candele, extra):
        c = I.arr(candele, "close")

        def entra(i):
            if i < 1:
                return False
            p0, p1 = c[i - 1], c[i]
            passo = _passo_tondo(p0)
            if segno > 0:
                livello = math.floor(p0 / passo + 1) * passo  # primo tondo sopra p0 (strettamente)
                return p0 < livello <= p1
            livello = math.ceil(p0 / passo - 1) * passo  # primo tondo sotto p0
            return p1 <= livello < p0
        return entra
    return f


# ---------------------------------------------------------------------------
# Registro delle varianti (come in ipotesi.md)
# ---------------------------------------------------------------------------

FONTI = {
    "I-01": "Liu e Tsyvinski, Risks and Returns of Cryptocurrency, NBER Working Paper 24877, agosto 2018; Moskowitz, Ooi e Pedersen, Time Series Momentum, Journal of Financial Economics 104(2), 2012",
    "I-02": "Brock, Lakonishok e LeBaron, Simple Technical Trading Rules and the Stochastic Properties of Stock Returns, Journal of Finance 47(5), 1992",
    "I-03": "Nagel, Evaporating Liquidity, Review of Financial Studies 25(7), 2012; Lehmann, Fads, Martingales, and Market Efficiency, Quarterly Journal of Economics 105(1), 1990",
    "I-04": "Shen, Urquhart e Wang, Bitcoin intraday time-series momentum, Financial Review 57(2), 2022; Gao, Han, Li e Zhou, Market intraday momentum, Journal of Financial Economics 129(2), 2018",
    "I-05": "Caporale e Plastun, The day of the week effect in the cryptocurrency market, Finance Research Letters 31, 2019",
    "I-06": "Schmeling, Schrimpf e Todorov, Crypto carry, BIS Working Paper 1087, aprile 2023",
    "I-07": "Gervais, Kaniel e Mingelgrin, The High-Volume Return Premium, Journal of Finance 56(3), 2001",
    "I-08": "Chordia e Subrahmanyam, Order imbalance and individual stock returns: Theory and evidence, Journal of Financial Economics 72(3), 2004",
    "I-09": "Williams, Long-Term Secrets to Short-Term Trading, Wiley, 1999; Crabel, Day Trading with Short Term Price Patterns and Opening Range Breakout, 1990",
    "I-10": "Connors e Alvarez, Short Term Trading Strategies That Work, TradingMarkets, 2008",
    "I-11": "Osler, Currency Orders and Exchange Rate Dynamics: An Explanation for the Predictive Success of Technical Analysis, Journal of Finance 58(5), 2003",
    "I-12": "George e Hwang, The 52-Week High and Momentum Investing, Journal of Finance 59(5), 2004",
    "I-13": "Zaremba, Bilgin, Long, Mercik e Szczygielski, Up or down? Short-term reversal, momentum, and liquidity effects in cryptocurrency markets, International Review of Financial Analysis 78, 2021",
}

PREV_NULLA = "R medio fra -0,10 e +0,05, t contro la (b) fra -1,5 e +1,5: non candidato"

VARIANTI: Dict[str, Dict[str, object]] = {
    "V01": dict(idea="I-01", tf="1d", direzione="long", meccanismo="momentum nel tempo a una settimana",
                parametri={"rendimento_barre": 7, "soglia": "> 0", "uscita_barre": 7, "stop_atr": 3},
                prepara=costruttore("long", 3, 7, cond_rend_k(7, +1)),
                previsione="R medio fra -0,05 e +0,10, t contro la (b) fra -1 e +2: probabilmente non candidato (il rialzo del 2021 lo prende anche la (b))"),
    "V02": dict(idea="I-01", tf="1d", direzione="short", meccanismo="momentum nel tempo a una settimana",
                parametri={"rendimento_barre": 7, "soglia": "< 0", "uscita_barre": 7, "stop_atr": 3},
                prepara=costruttore("short", 3, 7, cond_rend_k(7, -1)),
                previsione="R medio fra -0,10 e +0,05, t contro la (b) fra -1 e +1,5: non candidato"),
    "V03": dict(idea="I-02", tf="4h", direzione="long", meccanismo="rottura del massimo delle 50 barre",
                parametri={"finestra": 50, "uscita_barre": 10, "stop_atr": 2},
                prepara=costruttore("long", 2, 10, cond_rottura(50, +1)),
                previsione="R medio fra -0,05 e +0,10, t contro la (b) fra -1 e +2: non candidato"),
    "V04": dict(idea="I-02", tf="4h", direzione="short", meccanismo="rottura del minimo delle 50 barre",
                parametri={"finestra": 50, "uscita_barre": 10, "stop_atr": 2},
                prepara=costruttore("short", 2, 10, cond_rottura(50, -1)),
                previsione=PREV_NULLA),
    "V05": dict(idea="I-03", tf="1h", direzione="long", meccanismo="inversione dopo un'ora estrema al ribasso",
                parametri={"finestra_std": 168, "z": 3, "uscita_barre": 6, "stop_atr": 2},
                prepara=costruttore("long", 2, 6, cond_z_estremo(168, 3, -1)),
                previsione="R medio fra -0,05 e +0,10, t contro la (b) fra -1 e +2: non candidato, segno incerto"),
    "V06": dict(idea="I-03", tf="1h", direzione="short", meccanismo="inversione dopo un'ora estrema al rialzo",
                parametri={"finestra_std": 168, "z": 3, "uscita_barre": 6, "stop_atr": 2},
                prepara=costruttore("short", 2, 6, cond_z_estremo(168, 3, +1)),
                previsione=PREV_NULLA),
    "V07": dict(idea="I-04", tf="30m", direzione="long", meccanismo="la prima mezz'ora del giorno UTC prevede l'ultima",
                parametri={"barra_segnale": "23:00-23:30 UTC", "condizione": "mezz'ora 00:00-00:30 chiusa sopra l'apertura", "uscita_barre": 1, "stop_atr": 2},
                prepara=costruttore("long", 2, 1, cond_prima_mezzora(+1)),
                previsione="R medio fra -0,12 e 0 (costo del giro 0,058 R), t contro la (b) fra -1,5 e +1,5: non candidato"),
    "V08": dict(idea="I-04", tf="30m", direzione="short", meccanismo="la prima mezz'ora del giorno UTC prevede l'ultima",
                parametri={"barra_segnale": "23:00-23:30 UTC", "condizione": "mezz'ora 00:00-00:30 chiusa sotto l'apertura", "uscita_barre": 1, "stop_atr": 2},
                prepara=costruttore("short", 2, 1, cond_prima_mezzora(-1)),
                previsione="R medio fra -0,12 e 0 (costo del giro 0,058 R), t contro la (b) fra -1,5 e +1,5: non candidato"),
    "V09": dict(idea="I-05", tf="1d", direzione="long", meccanismo="rendimento del lunedi'",
                parametri={"barra_segnale": "domenica UTC", "uscita_barre": 1, "stop_atr": 2},
                prepara=costruttore("long", 2, 1, cond_domenica()),
                previsione="R medio fra -0,05 e +0,08, t contro la (b) fra -1 e +1,5: non candidato"),
    "V10": dict(idea="I-06", tf="8h", direzione="short", meccanismo="funding estremo alto: long affollati",
                parametri={"finestra_settlement": 270, "quantile": 0.90, "uscita_barre": 3, "stop_atr": 2},
                prepara=costruttore("short", 2, 3, cond_funding(270, 0.90, +1)),
                previsione="R medio fra -0,10 e +0,05, t contro la (b) fra -1 e +1,5: non candidato (il funding alto coincide col trend)"),
    "V11": dict(idea="I-06", tf="8h", direzione="long", meccanismo="funding estremo basso: short affollati",
                parametri={"finestra_settlement": 270, "quantile": 0.10, "uscita_barre": 3, "stop_atr": 2},
                prepara=costruttore("long", 2, 3, cond_funding(270, 0.10, -1)),
                previsione="R medio fra -0,05 e +0,10, t contro la (b) fra -1 e +2: non candidato"),
    "V12": dict(idea="I-07", tf="1d", direzione="long", meccanismo="premio dei volumi alti",
                parametri={"finestra": 50, "primi": 5, "uscita_barre": 10, "stop_atr": 3},
                prepara=costruttore("long", 3, 10, cond_volume_alto(50, 5)),
                previsione="R medio fra -0,05 e +0,10, t contro la (b) fra -1 e +1,5: non candidato"),
    "V13": dict(idea="I-08", tf="1h", direzione="long", meccanismo="squilibrio di acquisti aggressivi",
                parametri={"finestra": 720, "quantile": 0.95, "uscita_barre": 4, "stop_atr": 2},
                prepara=costruttore("long", 2, 4, cond_squilibrio(720, 0.95, +1)),
                previsione=PREV_NULLA),
    "V14": dict(idea="I-08", tf="1h", direzione="short", meccanismo="squilibrio di vendite aggressive",
                parametri={"finestra": 720, "quantile": 0.05, "uscita_barre": 4, "stop_atr": 2},
                prepara=costruttore("short", 2, 4, cond_squilibrio(720, 0.05, -1)),
                previsione=PREV_NULLA),
    "V15": dict(idea="I-09", tf="1h", direzione="long", meccanismo="rottura di volatilita' dall'apertura del giorno",
                parametri={"k_escursione_ieri": 0.5, "uscita": "fine del giorno UTC", "stop_atr": 2},
                prepara=prepara_williams(+1, 0.5, 2),
                previsione=PREV_NULLA),
    "V16": dict(idea="I-09", tf="1h", direzione="short", meccanismo="rottura di volatilita' dall'apertura del giorno",
                parametri={"k_escursione_ieri": 0.5, "uscita": "fine del giorno UTC", "stop_atr": 2},
                prepara=prepara_williams(-1, 0.5, 2),
                previsione=PREV_NULLA),
    "V17": dict(idea="I-10", tf="1d", direzione="long", meccanismo="ritracciamento nel trend (RSI a 2)",
                parametri={"media_lunga": 200, "rsi_2_sotto": 10, "uscita": "chiusura sopra media a 5 o 20 barre", "stop_atr": 3},
                prepara=prepara_connors(10, 200, 5, 3, 20),
                previsione="probabile scarto per pochi trade; se testata: R medio fra -0,05 e +0,10, non candidato"),
    "V18": dict(idea="I-10", tf="4h", direzione="long", meccanismo="ritracciamento nel trend (RSI a 2)",
                parametri={"media_lunga": 200, "rsi_2_sotto": 10, "uscita": "chiusura sopra media a 5 o 20 barre", "stop_atr": 3},
                prepara=prepara_connors(10, 200, 5, 3, 20),
                previsione="R medio fra -0,05 e +0,10, t contro la (b) fra -1 e +2: non candidato"),
    "V19": dict(idea="I-11", tf="1h", direzione="long", meccanismo="attraversamento al rialzo di un numero tondo",
                parametri={"passo": "meta' della potenza di 10 sotto il prezzo", "uscita_barre": 4, "stop_atr": 2},
                prepara=costruttore("long", 2, 4, cond_numero_tondo(+1)),
                previsione=PREV_NULLA),
    "V20": dict(idea="I-11", tf="1h", direzione="short", meccanismo="attraversamento al ribasso di un numero tondo",
                parametri={"passo": "meta' della potenza di 10 sotto il prezzo", "uscita_barre": 4, "stop_atr": 2},
                prepara=costruttore("short", 2, 4, cond_numero_tondo(-1)),
                previsione=PREV_NULLA),
    "V21": dict(idea="I-12", tf="1d", direzione="long", meccanismo="nuovo massimo dell'anno",
                parametri={"finestra": 365, "uscita_barre": 20, "stop_atr": 3},
                prepara=costruttore("long", 3, 20, cond_rottura(365, +1)),
                previsione="probabile scarto per pochi trade"),
    "V22": dict(idea="I-13", tf="1d", direzione="long", meccanismo="momentum giornaliero",
                parametri={"rendimento_barre": 1, "soglia": "> 0", "uscita_barre": 1, "stop_atr": 2},
                prepara=costruttore("long", 2, 1, cond_rend_k(1, +1)),
                previsione=PREV_NULLA),
    "V23": dict(idea="I-13", tf="1d", direzione="short", meccanismo="momentum giornaliero",
                parametri={"rendimento_barre": 1, "soglia": "< 0", "uscita_barre": 1, "stop_atr": 2},
                prepara=costruttore("short", 2, 1, cond_rend_k(1, -1)),
                previsione=PREV_NULLA),
}
