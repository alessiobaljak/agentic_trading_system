"""Programma 6, quarantaseiesima prova (QUARANTASEIESIMA.md): le 17 strategie gia' pronte di TradingView con i valori di
serie, su candele a 4 ore e a 1 giorno, fra le monete dell'universo settimanale, con i costi veri di Binance (e senza, per
confronto). Ogni strategia gira la posizione come nello Strategy Tester.

Uso: python3 -m research.programma6.quarantaseiesima
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from numba import njit

from research.programma5.strumenti import motore5 as m5
from research.programma6 import esecuzione as es
from research.programma6 import quarantacinquesima as qc
from research.programma6 import seconda as sc
from research.programma6 import sesta as se
from research.programma6 import terza as te
from research.programma6 import trentaquattresima as tq
from research.programma6.motore import TAKER

QUI = Path(__file__).parent
RIS = QUI / "risultati_quarantaseiesima"
DA, A = tq.DA, tq.A
TEMPI = ("4h", "1d")


# ---------------------------------------------------------------------------
# indicatori come in Pine (ta.*)
# ---------------------------------------------------------------------------

def _rma(x: pd.Series, n: int) -> pd.Series:
    return x.ewm(alpha=1.0 / n, adjust=False, min_periods=n).mean()


def _tr(h, l, c) -> pd.Series:
    pc = c.shift(1)
    return pd.concat([h - l, (h - pc).abs(), (l - pc).abs()], axis=1).max(axis=1)


def _sopra(a: pd.Series, b) -> np.ndarray:
    """ta.crossover: a > b ora e a <= b alla candela prima."""
    b = b if isinstance(b, pd.Series) else pd.Series(float(b), index=a.index)
    return ((a > b) & (a.shift(1) <= b.shift(1))).to_numpy()


def _sotto(a: pd.Series, b) -> np.ndarray:
    b = b if isinstance(b, pd.Series) else pd.Series(float(b), index=a.index)
    return ((a < b) & (a.shift(1) >= b.shift(1))).to_numpy()


def _rsi(c: pd.Series, n: int) -> pd.Series:
    d = c.diff()
    su, giu = _rma(d.clip(lower=0), n), _rma(-d.clip(upper=0), n)
    return 100 - 100 / (1 + su / giu.replace(0, np.nan))


def _pivot(x: np.ndarray, sinistra: int, destra: int, alto: bool) -> np.ndarray:
    """ta.pivothigh/pivotlow: alla candela t il valore della candela t − destra se e' il piu' alto (basso) della finestra."""
    s = pd.Series(x)
    if alto:
        sx, dx = s.rolling(sinistra).max().shift(1), s.rolling(destra).max().shift(-destra)
        perno = (s > sx) & (s > dx)
    else:
        sx, dx = s.rolling(sinistra).min().shift(1), s.rolling(destra).min().shift(-destra)
        perno = (s < sx) & (s < dx)
    return np.where(perno.shift(destra, fill_value=False).to_numpy(bool), s.shift(destra).to_numpy(), np.nan)


@njit(cache=True)
def _supertrend(h, l, c, atr, fattore):
    n = len(c)
    direzione = np.zeros(n)
    su_prima, giu_prima, dir_prima = np.nan, np.nan, 1.0
    for i in range(n):
        if not np.isfinite(atr[i]):
            continue
        m = (h[i] + l[i]) / 2
        su, giu = m + fattore * atr[i], m - fattore * atr[i]
        if np.isfinite(giu_prima) and not (giu > giu_prima or c[i - 1] < giu_prima):
            giu = giu_prima
        if np.isfinite(su_prima) and not (su < su_prima or c[i - 1] > su_prima):
            su = su_prima
        if not np.isfinite(su_prima):
            d = 1.0
        elif dir_prima == -1.0:
            d = 1.0 if c[i] < giu else -1.0
        else:
            d = -1.0 if c[i] > su else 1.0
        direzione[i] = d
        su_prima, giu_prima, dir_prima = su, giu, d
    return direzione


@njit(cache=True)
def _sar(h, l, inizio, passo, massimo):
    """Il SAR di Wilder: per ogni candela il livello valido in quella candela (noto alla chiusura di quella prima) e se la
    tendenza entrando era in salita."""
    n = len(h)
    sar, su = np.full(n, np.nan), np.zeros(n, np.bool_)
    if n < 3:
        return sar, su
    salita, ep, s, af = True, h[0], l[0], inizio
    for i in range(1, n):
        s = s + af * (ep - s)
        if salita:
            s = min(s, l[i - 1], l[i - 2] if i >= 2 else l[i - 1])
        else:
            s = max(s, h[i - 1], h[i - 2] if i >= 2 else h[i - 1])
        sar[i], su[i] = s, salita
        if salita and l[i] <= s:
            salita, s, ep, af = False, ep, l[i], inizio
        elif (not salita) and h[i] >= s:
            salita, s, ep, af = True, ep, h[i], inizio
        elif salita and h[i] > ep:
            ep, af = h[i], min(af + passo, massimo)
        elif (not salita) and l[i] < ep:
            ep, af = l[i], min(af + passo, massimo)
    return sar, su


# ---------------------------------------------------------------------------
# le 17 strategie (valori di serie); ognuna da' ordini per la candela dopo:
# ml/ms entrate a mercato, sl/ss livelli degli stop (NaN = nessun ordine)
# ---------------------------------------------------------------------------

def _vuoto(n):
    return {"ml": np.zeros(n, bool), "ms": np.zeros(n, bool), "sl": np.full(n, np.nan), "ss": np.full(n, np.nan)}


def segnali(nome: str, b: pd.DataFrame) -> dict:
    o, h, l, c = b["open"], b["high"], b["low"], b["close"]
    n = len(c)
    x = _vuoto(n)
    if nome == "BarUpDn":
        x["ml"] = ((c > o) & (o > c.shift(1))).to_numpy()
        x["ms"] = ((c < o) & (o < c.shift(1))).to_numpy()
    elif nome == "Bollinger Bands":
        base = c.rolling(20).mean()
        dev = 2.0 * c.rolling(20).std(ddof=0)
        alto, basso = base + dev, base - dev
        x["sl"] = np.where(_sopra(c, basso), basso.to_numpy(), np.nan)
        x["ss"] = np.where(_sotto(c, alto), alto.to_numpy(), np.nan)
    elif nome == "Channel BreakOut":
        ok = c.shift(5).notna().to_numpy()
        x["sl"] = np.where(ok, h.rolling(5).max().to_numpy(), np.nan)
        x["ss"] = np.where(ok, l.rolling(5).min().to_numpy(), np.nan)
    elif nome == "Consecutive Up/Down":
        cv = c.to_numpy()
        su = giu = 0
        for i in range(1, n):
            su = su + 1 if cv[i] > cv[i - 1] else 0
            giu = giu + 1 if cv[i] < cv[i - 1] else 0
            x["ml"][i], x["ms"][i] = su >= 3, giu >= 3
    elif nome in ("InSide Bar", "OutSide Bar"):
        dentro = (h < h.shift(1)) & (l > l.shift(1)) if nome == "InSide Bar" else (h > h.shift(1)) & (l < l.shift(1))
        x["ml"] = (dentro & (c > o)).to_numpy()
        x["ms"] = (dentro & (c < o)).to_numpy()
    elif nome == "Keltner Channels":
        ma = c.ewm(span=20, adjust=False, min_periods=20).mean()
        r = _rma(_tr(h, l, c), 10)
        alto, basso = ma + 2.0 * r, ma - 2.0 * r
        cu, cd = _sopra(c, alto), _sotto(c, basso)
        hv, lv, cv, mv = h.to_numpy(), l.to_numpy(), c.to_numpy(), ma.to_numpy()
        att_b = att_s = False
        lb = ls = np.nan
        for i in range(n):
            if att_b and (cv[i] < mv[i] or hv[i] >= lb):
                att_b = False
            if cu[i]:
                att_b, lb = True, hv[i]
            if att_s and (cv[i] > mv[i] or lv[i] <= ls):
                att_s = False
            if cd[i]:
                att_s, ls = True, lv[i]
            x["sl"][i] = lb if att_b else np.nan
            x["ss"][i] = ls if att_s else np.nan
    elif nome == "MACD":
        macd = c.ewm(span=12, adjust=False).mean() - c.ewm(span=26, adjust=False).mean()
        delta = macd - macd.ewm(span=9, adjust=False).mean()
        delta[c.index[:26]] = np.nan
        x["ml"], x["ms"] = _sopra(delta, 0.0), _sotto(delta, 0.0)
    elif nome == "Momentum":
        m0 = c - c.shift(12)
        m1 = m0 - m0.shift(1)
        x["sl"] = np.where((m0 > 0) & (m1 > 0), h.to_numpy(), np.nan)
        x["ss"] = np.where((m0 < 0) & (m1 < 0), l.to_numpy(), np.nan)
    elif nome == "Parabolic SAR":
        sar, su = _sar(h.to_numpy(float), l.to_numpy(float), 0.02, 0.02, 0.2)
        # l'ordine per la candela i e' noto alla chiusura di i − 1: se si sale, short allo stop del SAR, se no long
        x["ss"][:-1] = np.where(su[1:], sar[1:], np.nan)
        x["sl"][:-1] = np.where(~su[1:] & np.isfinite(sar[1:]), sar[1:], np.nan)
    elif nome == "Pivot Extension":
        x["ml"] = np.isfinite(_pivot(l.to_numpy(float), 4, 2, alto=False))
        x["ms"] = np.isfinite(_pivot(h.to_numpy(float), 4, 2, alto=True))
    elif nome == "Pivot Reversal":
        ph, pl = _pivot(h.to_numpy(float), 4, 2, True), _pivot(l.to_numpy(float), 4, 2, False)
        hv, lv = h.to_numpy(), l.to_numpy()
        le = se_ = False
        hp = lp = np.nan
        for i in range(n):
            if np.isfinite(ph[i]):
                hp, le = ph[i], True
            elif le and hv[i] > hp:
                le = False
            if np.isfinite(pl[i]):
                lp, se_ = pl[i], True
            elif se_ and lv[i] < lp:
                se_ = False
            x["sl"][i] = hp if le else np.nan
            x["ss"][i] = lp if se_ else np.nan
    elif nome == "Price Channel":
        ok = c.shift(20).notna().to_numpy()
        x["sl"] = np.where(ok, h.rolling(20).max().to_numpy(), np.nan)
        x["ss"] = np.where(ok, l.rolling(20).min().to_numpy(), np.nan)
    elif nome == "RSI":
        r = _rsi(c, 14)
        x["ml"], x["ms"] = _sopra(r, 30.0), _sotto(r, 70.0)
    elif nome == "Stochastic Slow":
        st = 100 * (c - l.rolling(14).min()) / (h.rolling(14).max() - l.rolling(14).min())
        k = st.rolling(3).mean()
        d = k.rolling(3).mean()
        x["ml"] = _sopra(k, d) & (k < 20).to_numpy()
        x["ms"] = _sotto(k, d) & (k > 80).to_numpy()
    elif nome == "Supertrend":
        dr = _supertrend(h.to_numpy(float), l.to_numpy(float), c.to_numpy(float), _rma(_tr(h, l, c), 10).to_numpy(float), 3.0)
        cambio = np.r_[0.0, np.diff(dr)]
        prima = np.r_[0.0, dr[:-1]]
        x["ml"] = (cambio < 0) & (prima != 0)
        x["ms"] = (cambio > 0) & (prima != 0)
    elif nome == "Volty Expan Close":
        atrs = _tr(h, l, c).rolling(5).mean() * 0.75
        ok = c.shift(5).notna().to_numpy()
        x["sl"] = np.where(ok, (c + atrs).to_numpy(), np.nan)
        x["ss"] = np.where(ok, (c - atrs).to_numpy(), np.nan)
    else:
        raise ValueError(nome)
    return x


STRATEGIE = ("BarUpDn", "Bollinger Bands", "Channel BreakOut", "Consecutive Up/Down", "InSide Bar", "Keltner Channels",
             "MACD", "Momentum", "OutSide Bar", "Parabolic SAR", "Pivot Extension", "Pivot Reversal", "Price Channel",
             "RSI", "Stochastic Slow", "Supertrend", "Volty Expan Close")


# ---------------------------------------------------------------------------
# lo Strategy Tester: una posizione da −1 a +1 per moneta
# ---------------------------------------------------------------------------

@njit(cache=True)
def simula(o, h, l, c, ml, ms, sl, ss, dentro, fund):
    """Per candela: (rendimento lordo, giro della posizione, funding pagato); e le operazioni chiuse (rendimento)."""
    n = len(c)
    lordo, giro, fu = np.zeros(n), np.zeros(n), np.zeros(n)
    chiuse = []
    p, prezzo_in = 0.0, 0.0
    for i in range(1, n):
        t = i - 1
        if not dentro[i]:
            if p != 0.0:
                lordo[i] = p * (o[i] / c[t] - 1)
                giro[i] = abs(p)
                chiuse.append(p * (o[i] / prezzo_in - 1))
                p = 0.0
            continue
        nuova, fill = p, np.nan
        if ml[t] and not ms[t] and p <= 0.0:
            nuova, fill = 1.0, o[i]
        elif ms[t] and not ml[t] and p >= 0.0:
            nuova, fill = -1.0, o[i]
        else:
            fl, fs = np.nan, np.nan
            if p <= 0.0 and np.isfinite(sl[t]):
                if o[i] >= sl[t]:
                    fl = o[i]
                elif h[i] >= sl[t]:
                    fl = sl[t]
            if p >= 0.0 and np.isfinite(ss[t]):
                if o[i] <= ss[t]:
                    fs = o[i]
                elif l[i] <= ss[t]:
                    fs = ss[t]
            if np.isfinite(fl) and np.isfinite(fs):
                if abs(fl - o[i]) <= abs(fs - o[i]):
                    fs = np.nan
                else:
                    fl = np.nan
            if np.isfinite(fl):
                nuova, fill = 1.0, fl
            elif np.isfinite(fs):
                nuova, fill = -1.0, fs
        if np.isfinite(fill) and nuova != p:
            lordo[i] = p * (fill / c[t] - 1) + nuova * (c[i] / fill - 1)
            giro[i] = abs(nuova - p)
            if p != 0.0:
                chiuse.append(p * (fill / prezzo_in - 1))
            p, prezzo_in = nuova, fill
        else:
            lordo[i] = p * (c[i] / c[t] - 1)
        fu[i] = p * fund[i]
    return lordo, giro, fu, chiuse


def barre(pan: dict, j: int, tempo: str) -> tuple:
    """(candele, giorno di ogni candela dall'inizio del pannello, frazione del giorno di ogni candela)."""
    if tempo == "1d":
        b = pd.DataFrame({k: pan[k][:, j] for k in ("open", "high", "low", "close")}).dropna()
        return b, b.index.to_numpy(), 1.0
    b = tq.quattro_ore(es.ore_di(pan["simboli"][j]))
    return b.reset_index(drop=True), b.index.to_numpy() * 4 // 24 - pan["t0"], 4 / 24


def esegui(log=print) -> dict:
    pan = sc.pannello()
    ps = te.pannello_settimane(pan, log=lambda x: None, indicatori_si=False)
    _, Ud = tq.rango_funding(pan, ps)
    T = Ud.shape[0]
    giorni = np.arange(T) + pan["t0"]
    periodo = (giorni >= DA) & (giorni <= A)
    N = np.maximum(1, (Ud & periodo[:, None]).sum(axis=1))
    btc = pd.Series(ps["R"][:, ps["simboli"].index("BTCUSDT")], index=ps["lunedi"])
    sr = qc.prove_fino_alla_quarantaquattresima()
    e45 = json.loads((QUI / "risultati_quarantacinquesima" / "esame.json").read_text())
    sr += [e45["I1"]["intero"]["sharpe"], e45["I2"]["portafoglio"]["intero"]["sharpe"]]
    monete = np.flatnonzero((Ud & periodo[:, None]).any(axis=0))
    acc = {(s, tf): {"lordo": np.zeros(T), "spese": np.zeros(T), "funding": np.zeros(T), "giro": np.zeros(T), "chiuse": []}
           for s in STRATEGIE for tf in TEMPI}
    for k, j in enumerate(monete):
        costo = TAKER + m5.scarto(pan["simboli"][j])
        for tf in TEMPI:
            b, g, quota = barre(pan, j, tf)
            if len(b) < 60:
                continue
            gc = np.clip(g, 0, T - 1)
            dentro = (g >= 0) & (g < T) & Ud[gc, j] & periodo[gc]
            fund = pan["funding"][gc, j] * quota
            arr = [b[x].to_numpy(float) for x in ("open", "high", "low", "close")]
            for s in STRATEGIE:
                x = segnali(s, b)
                lordo, giro, fu, chiuse = simula(*arr, x["ml"], x["ms"], x["sl"], x["ss"], dentro, fund)
                a = acc[(s, tf)]
                np.add.at(a["lordo"], gc, lordo)
                np.add.at(a["spese"], gc, giro * costo)
                np.add.at(a["funding"], gc, fu)
                np.add.at(a["giro"], gc, giro)
                a["chiuse"] += list(chiuse)
        if k % 50 == 0:
            log(f"[quarantaseiesima] {k}/{len(monete)} monete")
    RIS.mkdir(exist_ok=True)
    esami, settimane = {}, {}
    lun = ((giorni + 3) // 7) * 7 - 3
    for (s, tf), a in acc.items():
        d = pd.DataFrame({k: a[k] / N for k in ("lordo", "spese", "funding", "giro")}, index=giorni)[periodo]
        w = d.groupby(lun[periodo]).sum()
        w["netto"] = w["lordo"] - w["spese"] - w["funding"]
        w["netto_doppio"] = w["netto"] - w["spese"]
        w["long"] = w["short"] = 0.0
        w["monete"] = 1
        w = w[(w.index >= DA) & (w.index + 6 <= A)]
        settimane[f"{s} {tf}"] = w
        e = te.esame(w, btc, inizio=DA, anni_pieni=se.ANNI_PIENI)
        senza = w.assign(netto=w["lordo"], netto_doppio=w["lordo"])
        e["senza_costi"] = te.numeri_settimana(senza["netto"])
        ch = np.asarray(a["chiuse"])
        e["operazioni"] = int(len(ch))
        e["vinte"] = float((ch > 0).mean()) if len(ch) else float("nan")
        esami[f"{s} {tf}"] = e
        sr.append(e["intero"]["sharpe"])
    for e in esami.values():
        i = e["intero"]
        e["sharpe_corretto"] = te.sharpe_corretto(i["sharpe"], i["settimane"], i["asimmetria"], i["curtosi"], sr, 52)
        e["prove_nel_conto"] = len(sr)
        e["esito"] = te.esito(e, e["sharpe_corretto"])
    pd.concat({k: v["netto"] for k, v in settimane.items()}, axis=1).to_csv(RIS / "settimane_nette.csv.gz")
    (RIS / "esame.json").write_text(json.dumps(esami, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    righe = ["# Programma 6 — risultati della quarantaseiesima prova (le strategie già pronte di TradingView)", "",
             "Regole in `QUARANTASEIESIMA.md` (scritte prima). 17 strategie con i valori di serie, candele a 4 ore e a 1 giorno, "
             "le 100 monete più scambiate di ogni settimana, capitale in parti uguali, dal 4 gennaio 2021 al 10 ottobre 2026.", "",
             "| Strategia | Candele | Operazioni | Vinte | Senza costi: l'anno, Sharpe | Con i costi: l'anno, Sharpe, discesa | "
             "Spese l'anno | Sharpe corretto | Esito |", "|---|---|---|---|---|---|---|---|---|"]
    for nome, e in sorted(esami.items(), key=lambda kv: -kv[1]["intero"]["sharpe"]):
        s_, tf = nome.rsplit(" ", 1)
        i, z = e["intero"], e["senza_costi"]
        righe.append(f"| {s_} | {tf} | {e['operazioni']} | {100 * e['vinte']:.0f}% | {100 * z['annuo']:+.1f}%, {z['sharpe']:.2f} | "
                     f"{100 * i['annuo']:+.1f}%, {i['sharpe']:.2f}, {100 * i['discesa_max']:.0f}% | {100 * e['spese_annue']:.1f}% | "
                     f"{e['sharpe_corretto']:.2f} | {e['esito']} |")
    righe += ["", f"Sharpe corretto con {len(sr)} prove nel conto.", ""]
    valide = [k for k, e in esami.items() if e["esito"] == "VALIDA"]
    righe.append(f"**Valide: {', '.join(valide) if valide else 'nessuna'}**")
    testo = "\n".join(righe) + "\n"
    (QUI / "RISULTATI_QUARANTASEIESIMA.md").write_text(testo, encoding="utf-8")
    log(testo)
    return esami


if __name__ == "__main__":
    esegui(log=lambda x: print(x, flush=True))
    print("QUARANTASEIESIMA FINITA", flush=True)
