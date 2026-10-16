"""Implementazione di riferimento degli indicatori e delle condizioni del catalogo 3.

Scritta direttamente dalle formule di ``research/PROTOCOLLO_3.md`` (sezioni 7.2-7.5 e 7.8),
SENZA guardare il codice di ``research/src/catalogo3.py``: serve al Passo 0, punto 6
(«EMA, SMA, RSI, ATR, ADX, MACD, stocastico, Bollinger e Donchian coincidono con
un'implementazione di riferimento»). Solo cicli Python semplici, un valore alla volta;
numpy compare solo per restituire gli array.

Convenzioni (le stesse ``SCELTA`` documentate nel modulo, nessuna in piu'):

* NaN dove l'indicatore non e' ancora definito;
* medie di Wilder (alfa = 1/n): primo valore = media semplice dei primi n valori, poi
  media = (media precedente x (n - 1) + valore) / n;
* vero range e variazioni di chiusura partono dalla seconda candela (la prima non ha
  chiusura precedente);
* RSI = 100 se la media dei ribassi e' 0, 50 se sono 0 entrambe;
* stocastico: %K grezzo = 50 se massimo = minimo;
* ATR percentile: percentuale dei 500 valori PRECEDENTI di ATR/chiusura strettamente minori
  del valore corrente, definita solo se tutti i 500 sono definiti;
* Donchian e volume relativo escludono la candela corrente;
* VWAP e range asiatico per giorno UTC.
"""

from __future__ import annotations

import math
from datetime import datetime, timezone
from typing import List, Optional, Sequence, Tuple

import numpy as np

NAN = math.nan
MINUTO_MS = 60_000
GIORNO_MS = 24 * 60 * MINUTO_MS


def _lista(x) -> List[float]:
    return [float(v) for v in x]


def _def(v: float) -> bool:
    return not math.isnan(v)


def _arr(x: Sequence[float]) -> np.ndarray:
    return np.array(x, dtype=np.float64)


# ---------------------------------------------------------------------------
# medie
# ---------------------------------------------------------------------------


def ema(x, n: int) -> np.ndarray:
    """EMA = a x valore + (1 - a) x EMA precedente, a = 2/(n+1); primo valore = media dei
    primi n valori definiti (7.2). Se x comincia con NaN si parte dal primo definito."""
    x = _lista(x)
    out = [NAN] * len(x)
    inizio = next((i for i, v in enumerate(x) if _def(v)), None)
    if inizio is None or inizio + n > len(x):
        return _arr(out)
    a = 2.0 / (n + 1)
    somma = 0.0
    for i in range(inizio, inizio + n):
        somma += x[i]
    prec = somma / n
    out[inizio + n - 1] = prec
    for i in range(inizio + n, len(x)):
        prec = a * x[i] + (1 - a) * prec
        out[i] = prec
    return _arr(out)


def sma(x, n: int) -> np.ndarray:
    """Media semplice degli ultimi n valori, quello corrente compreso; NaN se uno manca."""
    x = _lista(x)
    out = [NAN] * len(x)
    for i in range(n - 1, len(x)):
        somma = 0.0
        ok = True
        for j in range(i - n + 1, i + 1):
            if not _def(x[j]):
                ok = False
                break
            somma += x[j]
        if ok:
            out[i] = somma / n
    return _arr(out)


def deviazione_popolazione(x, n: int) -> np.ndarray:
    """Deviazione standard di popolazione (divisore n) degli ultimi n valori."""
    x = _lista(x)
    out = [NAN] * len(x)
    for i in range(n - 1, len(x)):
        finestra = x[i - n + 1:i + 1]
        media = sum(finestra) / n
        var = 0.0
        for v in finestra:
            var += (v - media) ** 2
        out[i] = math.sqrt(var / n)
    return _arr(out)


def wilder(x: List[float], n: int, primo: int) -> List[float]:
    """Media di Wilder dei valori x[primo:]: primo valore (all'indice primo + n - 1) =
    media semplice dei primi n; poi (prec x (n - 1) + valore) / n."""
    out = [NAN] * len(x)
    if primo + n > len(x):
        return out
    somma = 0.0
    for i in range(primo, primo + n):
        somma += x[i]
    prec = somma / n
    out[primo + n - 1] = prec
    for i in range(primo + n, len(x)):
        prec = (prec * (n - 1) + x[i]) / n
        out[i] = prec
    return out


# ---------------------------------------------------------------------------
# oscillatori e volatilita'
# ---------------------------------------------------------------------------


def rsi(close, n: int) -> np.ndarray:
    """RSI di Wilder: medie di Wilder di rialzi e ribassi di chiusura (dalla seconda
    candela); RSI = 100 - 100 / (1 + rialzi / ribassi)."""
    c = _lista(close)
    rialzi = [NAN] * len(c)
    ribassi = [NAN] * len(c)
    for i in range(1, len(c)):
        d = c[i] - c[i - 1]
        rialzi[i] = d if d > 0 else 0.0
        ribassi[i] = -d if d < 0 else 0.0
    mr = wilder(rialzi, n, 1)
    mb = wilder(ribassi, n, 1)
    out = [NAN] * len(c)
    for i in range(len(c)):
        if not _def(mr[i]):
            continue
        if mb[i] == 0.0:
            out[i] = 50.0 if mr[i] == 0.0 else 100.0
        else:
            out[i] = 100.0 - 100.0 / (1.0 + mr[i] / mb[i])
    return _arr(out)


def vero_range(high, low, close) -> List[float]:
    """Massimo fra (massimo - minimo), (massimo - chiusura precedente), (chiusura precedente
    - minimo), come scritto in 7.2; la prima candela non ha chiusura precedente: NaN."""
    h, l, c = _lista(high), _lista(low), _lista(close)
    out = [NAN] * len(h)
    for i in range(1, len(h)):
        out[i] = max(h[i] - l[i], h[i] - c[i - 1], c[i - 1] - l[i])
    return out


def atr(high, low, close, n: int = 14) -> np.ndarray:
    return _arr(wilder(vero_range(high, low, close), n, 1))


def adx(high, low, close, n: int = 14) -> np.ndarray:
    """ADX di Wilder: +DM / -DM (movimento direzionale), vero range, tutti lisciati con
    Wilder dalla seconda candela; DI = 100 x DM / TR; DX = 100 x |+DI - -DI| / (+DI + -DI)
    (0 se la somma e' 0); ADX = media di Wilder del DX (dal primo DX definito)."""
    h, l = _lista(high), _lista(low)
    m = len(h)
    piu = [NAN] * m
    meno = [NAN] * m
    for i in range(1, m):
        su = h[i] - h[i - 1]
        giu = l[i - 1] - l[i]
        piu[i] = su if (su > giu and su > 0) else 0.0
        meno[i] = giu if (giu > su and giu > 0) else 0.0
    tr = vero_range(high, low, close)
    s_tr = wilder(tr, n, 1)
    s_piu = wilder(piu, n, 1)
    s_meno = wilder(meno, n, 1)
    dx = [NAN] * m
    for i in range(m):
        if not _def(s_tr[i]):
            continue
        di_p = 100.0 * s_piu[i] / s_tr[i]
        di_m = 100.0 * s_meno[i] / s_tr[i]
        somma = di_p + di_m
        dx[i] = 0.0 if somma == 0 else 100.0 * abs(di_p - di_m) / somma
    primo_dx = next((i for i, v in enumerate(dx) if _def(v)), None)
    if primo_dx is None:
        return _arr([NAN] * m)
    return _arr(wilder(dx, n, primo_dx))


def stocastico(high, low, close, k: int = 14, lk: int = 3, ld: int = 3) -> Tuple[np.ndarray, np.ndarray]:
    """%K grezzo = 100 x (chiusura - minimo dei minimi) / (massimo dei massimi - minimo dei
    minimi) sulle ultime k candele (corrente compresa), 50 se massimo = minimo;
    %K = SMA(lk) del grezzo; %D = SMA(ld) del %K."""
    h, l, c = _lista(high), _lista(low), _lista(close)
    grezzo = [NAN] * len(c)
    for i in range(k - 1, len(c)):
        mx = max(h[i - k + 1:i + 1])
        mn = min(l[i - k + 1:i + 1])
        grezzo[i] = 50.0 if mx == mn else 100.0 * (c[i] - mn) / (mx - mn)
    pk = sma(grezzo, lk)
    pd = sma(pk, ld)
    return pk, pd


def macd(close, veloce: int = 12, lenta: int = 26, segnale: int = 9) -> Tuple[np.ndarray, np.ndarray]:
    """Linea = EMA(12) - EMA(26); segnale = EMA(9) della linea (dal primo valore definito)."""
    ev = ema(close, veloce)
    el = ema(close, lenta)
    linea = [float(a) - float(b) for a, b in zip(ev, el)]  # NaN dove una delle due manca
    return _arr(linea), ema(linea, segnale)


def bollinger(close, n: int, k: float) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """(inferiore, media, superiore) = SMA(n) -/+ k x deviazione di popolazione."""
    media = sma(close, n)
    dev = deviazione_popolazione(close, n)
    inf = [NAN] * len(media)
    sup = [NAN] * len(media)
    for i in range(len(media)):
        if _def(media[i]):
            inf[i] = media[i] - k * dev[i]
            sup[i] = media[i] + k * dev[i]
    return _arr(inf), media, _arr(sup)


def donchian(high, low, n: int) -> Tuple[np.ndarray, np.ndarray]:
    """Massimo dei massimi e minimo dei minimi delle n candele PRECEDENTI (esclusa la corrente)."""
    h, l = _lista(high), _lista(low)
    su = [NAN] * len(h)
    giu = [NAN] * len(h)
    for i in range(n, len(h)):
        su[i] = max(h[i - n:i])
        giu[i] = min(l[i - n:i])
    return _arr(su), _arr(giu)


def volume_relativo(volume, n: int = 20) -> np.ndarray:
    """Volume della candela / media dei volumi delle n candele PRECEDENTI."""
    v = _lista(volume)
    out = [NAN] * len(v)
    for i in range(n, len(v)):
        media = sum(v[i - n:i]) / n
        out[i] = v[i] / media
    return _arr(out)


def atr_percentile(atr_, close, finestra: int = 500) -> np.ndarray:
    """Percentuale dei ``finestra`` valori precedenti di ATR/chiusura strettamente minori del
    valore corrente; NaN se il corrente o uno dei precedenti non e' definito."""
    a, c = _lista(atr_), _lista(close)
    x = [a[i] / c[i] for i in range(len(a))]
    out = [NAN] * len(x)
    for i in range(finestra, len(x)):
        if not _def(x[i]):
            continue
        prec = x[i - finestra:i]
        if any(not _def(v) for v in prec):
            continue
        minori = 0
        for v in prec:
            if v < x[i]:
                minori += 1
        out[i] = 100.0 * minori / finestra
    return _arr(out)


# ---------------------------------------------------------------------------
# calendario (UTC), VWAP, range asiatico, funding
# ---------------------------------------------------------------------------


def giorno(ts: int) -> int:
    return int(ts) // GIORNO_MS


def minuto_del_giorno(ts: int) -> int:
    return (int(ts) % GIORNO_MS) // MINUTO_MS


def giorno_della_settimana(ts: int) -> int:
    """0 = lunedi' ... 6 = domenica, in UTC."""
    return datetime.fromtimestamp(int(ts) / 1000, tz=timezone.utc).weekday()


def vwap_giornaliero(ts, high, low, close, volume) -> np.ndarray:
    """Dall'inizio del giorno UTC: somma(prezzo tipico x volume) / somma(volumi), con la
    candela corrente; prezzo tipico = (massimo + minimo + chiusura) / 3."""
    ts = [int(t) for t in ts]
    h, l, c, v = _lista(high), _lista(low), _lista(close), _lista(volume)
    out = [NAN] * len(ts)
    num = den = 0.0
    for i in range(len(ts)):
        if i == 0 or giorno(ts[i]) != giorno(ts[i - 1]):
            num = den = 0.0
        tipico = (h[i] + l[i] + c[i]) / 3.0
        num += tipico * v[i]
        den += v[i]
        out[i] = num / den if den > 0 else NAN
    return _arr(out)


def range_asiatico(ts, high, low) -> Tuple[np.ndarray, np.ndarray]:
    """Massimo e minimo delle candele che aprono fra 00:00 (compreso) e 08:00 (escluso) UTC
    dello stesso giorno, per le candele che aprono alle 08:00 o dopo; prima NaN."""
    ts = [int(t) for t in ts]
    h, l = _lista(high), _lista(low)
    su = [NAN] * len(ts)
    giu = [NAN] * len(ts)
    for i in range(len(ts)):
        if minuto_del_giorno(ts[i]) < 8 * 60:
            continue
        hs = [h[j] for j in range(len(ts)) if giorno(ts[j]) == giorno(ts[i]) and minuto_del_giorno(ts[j]) < 480]
        ls = [l[j] for j in range(len(ts)) if giorno(ts[j]) == giorno(ts[i]) and minuto_del_giorno(ts[j]) < 480]
        if hs:
            su[i] = max(hs)
            giu[i] = min(ls)
    return _arr(su), _arr(giu)


def funding_regolato(ts_candele, durata: int, ts_funding, tassi) -> np.ndarray:
    """Ultimo tasso regolato alla chiusura della candela: ultimo T <= apertura + durata - 1 ms."""
    out = [NAN] * len(ts_candele)
    for i, t in enumerate(ts_candele):
        chiusura = int(t) + durata - 1
        ultimo = NAN
        for tf, r in zip(ts_funding, tassi):
            if int(tf) <= chiusura:
                ultimo = float(r)
        out[i] = ultimo
    return _arr(out)


def prima_candela_dopo_regolamento(ts_candele, ts_funding) -> np.ndarray:
    """Vero se un regolamento T cade in (apertura della candela precedente, apertura della
    candela]: la candela e' la prima che inizia a T o dopo. La prima candela della serie:
    vero solo se un regolamento cade esattamente alla sua apertura."""
    out = [False] * len(ts_candele)
    for i, t in enumerate(ts_candele):
        prec = int(ts_candele[i - 1]) if i > 0 else int(t) - 1
        out[i] = any(prec < int(tf) <= int(t) for tf in ts_funding)
    return np.array(out, dtype=bool)


# ---------------------------------------------------------------------------
# incroci (7.2)
# ---------------------------------------------------------------------------


def _valore(b, i):
    return float(b) if np.isscalar(b) else float(b[i])


def incrocio_su(a, b) -> np.ndarray:
    """Alla chiusura precedente a <= b, a quella attuale a > b (NaN: falso)."""
    a = _lista(a)
    out = [False] * len(a)
    for i in range(1, len(a)):
        p, q = a[i - 1], a[i]
        bp, bq = _valore(b, i - 1), _valore(b, i)
        if all(_def(v) for v in (p, q, bp, bq)):
            out[i] = (p <= bp) and (q > bq)
    return np.array(out, dtype=bool)


def incrocio_giu(a, b) -> np.ndarray:
    """Alla chiusura precedente a >= b, a quella attuale a < b (NaN: falso)."""
    a = _lista(a)
    out = [False] * len(a)
    for i in range(1, len(a)):
        p, q = a[i - 1], a[i]
        bp, bq = _valore(b, i - 1), _valore(b, i)
        if all(_def(v) for v in (p, q, bp, bq)):
            out[i] = (p >= bp) and (q < bq)
    return np.array(out, dtype=bool)


# ---------------------------------------------------------------------------
# condizioni di ingresso, filtro e conferma (7.3-7.5), su una variante normalizzata
# ---------------------------------------------------------------------------


def _maggiore(a, b) -> np.ndarray:
    """a > b elemento per elemento; NaN: falso."""
    out = []
    for i in range(len(a)):
        x, y = float(a[i]), _valore(b, i)
        out.append(_def(x) and _def(y) and x > y)
    return np.array(out, dtype=bool)


def _minore(a, b) -> np.ndarray:
    out = []
    for i in range(len(a)):
        x, y = float(a[i]), _valore(b, i)
        out.append(_def(x) and _def(y) and x < y)
    return np.array(out, dtype=bool)


def _media(tipo: str, close, n: int) -> np.ndarray:
    return ema(close, n) if tipo == "EMA" else sma(close, n)


def condizione_ingresso(e: dict, long: bool, s) -> np.ndarray:
    """Il segnale di ingresso (7.3) alla chiusura di ogni candela, per la serie ``s``
    (oggetto con ts, open, high, low, close, volume, funding_ts, funding_tasso, durata)."""
    c = e["codice"]
    cl = s.close
    if c == "E1":
        v = _media(e["media"], cl, e["veloce"])
        l = _media(e["media"], cl, e["lenta"])
        return incrocio_su(v, l) if long else incrocio_giu(v, l)
    if c == "E2":
        m = _media(e["media"], cl, e["n"])
        return incrocio_su(cl, m) if long else incrocio_giu(cl, m)
    if c == "E3":
        su, giu = donchian(s.high, s.low, e["n"])
        return _maggiore(cl, su) if long else _minore(cl, giu)
    if c == "E4":
        inf, _, sup = bollinger(cl, 20, e["k"])
        return _maggiore(cl, sup) if long else _minore(cl, inf)
    if c == "E5":
        inf, _, sup = bollinger(cl, 20, e["k"])
        out = [False] * len(cl)
        for i in range(1, len(cl)):
            if not all(_def(float(x)) for x in (inf[i - 1], sup[i - 1], inf[i], sup[i])):
                continue
            dentro = inf[i] <= cl[i] <= sup[i]
            if long:
                out[i] = bool(cl[i - 1] < inf[i - 1] and dentro)
            else:
                out[i] = bool(cl[i - 1] > sup[i - 1] and dentro)
        return np.array(out, dtype=bool)
    if c == "E6":
        r = rsi(cl, e["n"])
        bassa, alta = e["soglie"]
        return incrocio_su(r, bassa) if long else incrocio_giu(r, alta)
    if c == "E7":
        r = rsi(cl, e["n"])
        return incrocio_su(r, 50.0) if long else incrocio_giu(r, 50.0)
    if c == "E8":
        pk, pd = stocastico(s.high, s.low, cl)
        if long:
            return incrocio_su(pk, pd) & _minore(pk, 20.0)
        return incrocio_giu(pk, pd) & _maggiore(pk, 80.0)
    if c == "E9":
        linea, seg = macd(cl)
        return incrocio_su(linea, seg) if long else incrocio_giu(linea, seg)
    if c == "E10":
        return e10(s, long)
    if c == "E11":
        prima = prima_candela_dopo_regolamento(s.ts, s.funding_ts)
        f = funding_regolato(s.ts, s.durata, s.funding_ts, s.funding_tasso)
        livello = _maggiore(f, e["soglia"]) if e["soglia"] >= 0.0003 - 1e-12 else _minore(f, e["soglia"])
        return prima & livello
    if c == "E12":
        rv = volume_relativo(s.volume, 20)
        dir_ = _maggiore(cl, s.open) if long else _minore(cl, s.open)
        return _maggiore(rv, e["soglia"]) & dir_
    raise ValueError(c)


def e10(s, long: bool, inizio_min: int = 8 * 60, fine_min: int = 16 * 60) -> np.ndarray:
    """Prima chiusura del giorno, fra le 08:00 e le 16:00 UTC, sopra il massimo (long) o sotto
    il minimo (short) del range asiatico: al massimo un segnale al giorno. La finestra e'
    sull'ora di APERTURA della candela, [08:00, 16:00)."""
    su, giu = range_asiatico(s.ts, s.high, s.low)
    out = [False] * len(s.ts)
    giorni_con_segnale = set()
    for i in range(len(s.ts)):
        mm = minuto_del_giorno(s.ts[i])
        if not (inizio_min <= mm < fine_min):
            continue
        d = giorno(s.ts[i])
        if d in giorni_con_segnale:
            continue
        livello = su[i] if long else giu[i]
        if not _def(float(livello)):
            continue
        if (long and s.close[i] > livello) or (not long and s.close[i] < livello):
            out[i] = True
            giorni_con_segnale.add(d)
    return np.array(out, dtype=bool)


def condizione_filtro(f: Optional[dict], s) -> np.ndarray:
    """Il filtro di regime (7.4) alla chiusura di ogni candela; non dipende dalla direzione."""
    m = len(s.ts)
    if f is None:
        return np.ones(m, dtype=bool)
    c = f["codice"]
    cl = s.close
    if c == "F1":
        e = ema(cl, f["n"])
        return _maggiore(cl, e) if f["lato"] == "sopra" else _minore(cl, e)
    if c == "F2":
        a = adx(s.high, s.low, cl, 14)
        return _maggiore(a, 25.0) if f["regime"] == "tendenza" else _minore(a, 20.0)
    if c == "F3":
        p = atr_percentile(atr(s.high, s.low, cl, 14), cl, 500)
        return _maggiore(p, 70.0) if f["regime"] == "alta" else _minore(p, 30.0)
    if c == "F4":
        fr = funding_regolato(s.ts, s.durata, s.funding_ts, s.funding_tasso)
        return _maggiore(fr, 0.0003) if f["lato"] == "sopra" else _minore(fr, 0.0)
    if c == "F5":
        a, b = {"asia": (0, 480), "europa": (420, 960), "usa": (780, 1260)}[f["sessione"]]
        return np.array([a <= minuto_del_giorno(t) < b for t in s.ts], dtype=bool)
    if c == "F6":
        fer = f["giorni"] == "feriali"
        return np.array([(giorno_della_settimana(t) < 5) == fer for t in s.ts], dtype=bool)
    if c == "F7":
        vw = vwap_giornaliero(s.ts, s.high, s.low, cl, s.volume)
        return _maggiore(cl, vw) if f["lato"] == "sopra" else _minore(cl, vw)
    raise ValueError(c)


def condizione_conferma(cf: Optional[dict], long: bool, s) -> np.ndarray:
    """La conferma (7.5) alla chiusura della candela del segnale."""
    m = len(s.ts)
    if cf is None:
        return np.ones(m, dtype=bool)
    c = cf["codice"]
    if c == "C1":
        return _maggiore(volume_relativo(s.volume, 20), cf["soglia"])
    if c == "C2":
        return _maggiore(s.close, s.open) if long else _minore(s.close, s.open)
    if c == "C3":
        r = rsi(s.close, 14)
        return _maggiore(r, 50.0) if long else _minore(r, 50.0)
    raise ValueError(c)


# ---------------------------------------------------------------------------
# riscaldamento (7.8)
# ---------------------------------------------------------------------------


def riscaldamento(v: dict) -> int:
    """Candele che devono PRECEDERE, nel tratto senza buchi, la prima candela che puo' dare un
    segnale (la candela t e' ammessa se t - inizio del tratto >= w).

    7.8: 3 volte il periodo piu' lungo dei ricorsivi (EMA, RSI, ATR, ADX, MACD); almeno il
    periodo pieno per gli altri (SMA, Bollinger, Donchian, volume relativo); per l'ATR
    percentile i 3 x 14 dell'ATR piu' le 500 candele della finestra. MACD: 3 x 26.
    "Della variante": contano anche l'ATR(14) dello stop S1, dell'ingresso limit e del
    trailing U3 (ricorsivo) e le n candele dello stop S2 (periodo pieno).
    """
    ricorsivi: List[int] = []
    pieni: List[int] = [1]  # un incrocio guarda anche la candela precedente
    if v["stop"]["codice"] == "S1" or v["tipo_ingresso"]["codice"] == "L" or any(
            u["codice"] == "U3" for u in v["uscite"]):
        ricorsivi.append(14)
    if v["stop"]["codice"] == "S2":
        # il protocollo non nomina lo stop S2 in 7.8; qui la SCELTA del modulo: il minimo /
        # massimo delle ultime n candele, segnale compreso, e' definito dalla candela n - 1
        pieni.append(v["stop"]["n"] - 1)
    for parte in (v.get("filtro"), v["ingresso"], v.get("conferma")):
        if not parte:
            continue
        c = parte["codice"]
        if c == "E1":
            (ricorsivi if parte["media"] == "EMA" else pieni).extend([parte["veloce"], parte["lenta"]])
        elif c == "E2":
            (ricorsivi if parte["media"] == "EMA" else pieni).append(parte["n"])
        elif c == "E3":
            pieni.append(parte["n"])
        elif c in ("E4", "E5"):
            pieni.append(20)
        elif c in ("E6", "E7"):
            ricorsivi.append(parte["n"])
        elif c == "E8":
            # stocastico (non nominato in 7.8): %D definito dalla candela 17 (14 + 3 + 3 - 3),
            # l'incrocio guarda anche la precedente -> 18
            pieni.append(18)
        elif c == "E9":
            ricorsivi.append(26)
        elif c in ("E12", "C1"):
            pieni.append(20)
        elif c == "C3":
            ricorsivi.append(14)
        elif c == "F1":
            ricorsivi.append(parte["n"])
        elif c == "F2":
            ricorsivi.append(14)
        elif c == "F3":
            pieni.append(3 * 14 + 500)
    return max([3 * r for r in ricorsivi] + pieni)


def ammessa(ts, durata: int, w: int) -> np.ndarray:
    """Vero dove nel tratto senza buchi (candele consecutive) almeno w candele precedono t."""
    out = [False] * len(ts)
    inizio = 0
    for i in range(len(ts)):
        if i > 0 and int(ts[i]) - int(ts[i - 1]) != durata:
            inizio = i
        out[i] = (i - inizio) >= w
    return np.array(out, dtype=bool)
