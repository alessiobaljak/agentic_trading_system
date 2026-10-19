"""Programma 6, seconda prova (SECONDA.md): le candele giornaliere di tutti i perpetui USDT-M, l'universo mese per mese
con i soli dati di allora, la regola pubblicata (parte A: varianti A1, A2, A3), le famiglie della prima prova a 1 giorno
(parte B) e l'esame.

Convenzioni (SECONDA.md, sezioni 4-5): il giorno ``t`` e' la candela che apre alle 00:00 UTC; il peso deciso alla
chiusura di ``t`` si tiene sul giorno ``t+1``, dall'apertura di ``t+1`` all'apertura di ``t+2`` (o alla chiusura di
``t+1`` se la moneta non ha la candela dopo: tolta dal listino). Il funding regolato al minuto ``m`` tocca chi tiene il
giorno ``(m-1)//1440`` (il regolamento delle 00:00 lo paga chi ha tenuto il giorno prima).

Uso: python3 -m research.programma6.seconda [pannello|A|B|rapporto]
"""
from __future__ import annotations

import json
import math
import sys
import warnings
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
from numba import njit

from research.programma5.strumenti import motore5 as m5
from research.programma6.motore import TAKER
from research.src.dati import funding_da_zip

RADICE = Path(__file__).resolve().parents[2]
DATI = RADICE / "research" / "data" / "p6g"
PANNELLO = RADICE / "research" / "data" / "p6g_pannello.pkl"
QUI = Path(__file__).parent
RIS = QUI / "risultati_seconda"

PERIODI = (5, 10, 20, 30, 60, 90, 150, 250, 360)
VOL_OBIETTIVO, MOLT_MAX = 0.25, 2.0
N_A, N_B = 20, 50
VOLUME_MIN, STORIA_MIN, GIORNI_VOLUME, GIORNI_VOL = 2e6, 365, 30, 90
PROVE_PROGRAMMA = 21          # SECONDA.md, sezione 7: 9 + 3 + 9

# SECONDA.md, sezione 9: i contratti che non sono una moneta
ESCLUSI = (
    # indici
    "BTCDOMUSDT", "DEFIUSDT", "FOOTBALLUSDT", "BLUEBIRDUSDT",
    # metalli, materie prime, oro in gettoni, valute
    "XAUUSDT", "XAGUSDT", "XPTUSDT", "XPDUSDT", "COPPERUSDT", "NATGASUSDT", "PAXGUSDT", "XAUTUSDT", "USDBRLUSDT",
    # azioni e fondi
    "AAOIUSDT", "AAPLUSDT", "ACNUSDT", "ADBEUSDT", "ALABUSDT", "AMATUSDT", "AMDUSDT", "AMZNUSDT", "ANETUSDT",
    "ANTHROPICUSDT", "APLDUSDT", "APPUSDT", "ASMLUSDT", "ASTSUSDT", "AVGOUSDT", "AXTIUSDT", "BABAUSDT", "BITOUSDT",
    "BMNRUSDT", "BRKBUSDT", "BYDUSDT", "CIENUSDT", "COHRUSDT", "COINUSDT", "COSTUSDT", "CRCLUSDT", "CRDOUSDT",
    "CRMUSDT", "CRWDUSDT", "CRWVUSDT", "CSCOUSDT", "CSOPSAMSUNG2LUSDT", "CSOPSKHYNIX2LUSDT", "CVNAUSDT", "CXMTUSDT",
    "DDOGUSDT", "DELLUSDT", "DISUSDT", "DJTUSDT", "DKNGUSDT", "EBAYUSDT", "EWJUSDT", "EWYUSDT", "EWZUSDT",
    "FLNCUSDT", "GDXUSDT", "GEVUSDT", "GIGADEVUSDT", "GLWUSDT", "GMEUSDT", "GOOGLUSDT", "GTLBUSDT", "HANMIUSDT",
    "HIMSUSDT", "HK0625USDT", "HK0700USDT", "HK0992USDT", "HK1810USDT", "HOODUSDT", "HPEUSDT", "HUTUSDT",
    "HYUNDAIUSDT", "IBMUSDT", "INTCUSDT", "IONQUSDT", "IRENUSDT", "IWMUSDT", "JPMUSDT", "KLACUSDT", "KODEX200USDT",
    "KUAISHOUUSDT", "LGELECTRONICSUSDT", "LLYUSDT", "LRCXUSDT", "MARAUSDT", "MDBUSDT", "MEITUANUSDT", "METAUSDT",
    "MINIMAXUSDT", "MRKUSDT", "MRNAUSDT", "MRVLUSDT", "MSFTUSDT", "MSTRUSDT", "NAVERUSDT", "NBISUSDT", "NFLXUSDT",
    "NKEUSDT", "NOWUSDT", "NVDAUSDT", "NVDLUSDT", "NVOUSDT", "OKLOUSDT", "ONDSUSDT", "OPENAIUSDT", "ORCLUSDT",
    "PANWUSDT", "PDDUSDT", "PLTRUSDT", "POPMARTUSDT", "PYPLUSDT", "QCOMUSDT", "QQQUSDT", "RDDTUSDT", "RIVNUSDT",
    "RKLBUSDT", "SAMSUNGEMUSDT", "SAMSUNGUSDT", "SHOPUSDT", "SKHYNIXUSDT", "SMCIUSDT", "SMHUSDT", "SNDKUSDT",
    "SNOWUSDT", "SOFIUSDT", "SONYUSDT", "SOXLUSDT", "SOXSUSDT", "SPCXUSDT", "SPYUSDT", "SQQQUSDT", "TEMUSDT",
    "TENCENTUSDT", "TMFUSDT", "TQQQUSDT", "TSLAUSDT", "TSLLUSDT", "TSMUSDT", "TTWOUSDT", "TXNUSDT", "TZAUSDT",
    "UBERUSDT", "UNHUSDT", "UNITREEUSDT", "URNMUSDT", "UVXYUSDT", "WDCUSDT", "WMTUSDT", "XBIUSDT", "XLEUSDT",
    "XOMUSDT", "ZHIPUUSDT",
    # aggiunti il 19 ottobre 2026 sera (SECONDA.md, sezione 9): materie prime e azioni nate dal 2026-04, mai entrate
    # nell'universo delle prove; BZUSDT e CLUSDT (petrolio) sarebbero entrate nel paper dalla settimana del 2026-10-19
    "BZUSDT", "CLUSDT", "SKHYUSDT", "NOKUSDT", "MUUSDT", "ARMUSDT", "LITEUSDT", "NETUSDT", "TERUSDT", "TWSTUSDT",
    "KORUUSDT", "CRMLUSDT", "CBRSUSDT", "DRAMUSDT", "INTWUSDT", "AGPUUSDT",
)


def giorno(a: int, m: int, g: int) -> int:
    return int(datetime(a, m, g, tzinfo=timezone.utc).timestamp() // 86400)


def data(t: int) -> str:
    return datetime.fromtimestamp(int(t) * 86400, tz=timezone.utc).strftime("%Y-%m-%d")


INIZIO = giorno(2021, 1, 1)
PUBBLICAZIONE = giorno(2025, 4, 9)
ULTIMO_ANNO = giorno(2025, 10, 1)


# ---------------------------------------------------------------------------
# dati
# ---------------------------------------------------------------------------

def candele(simbolo: str) -> pd.DataFrame:
    """Le candele giornaliere (indice = giorno dall'epoca): open, high, low, close, volume, quote_volume."""
    file = sorted((DATI / simbolo / "giorni").glob("*.zip"))
    if not file:
        return pd.DataFrame()
    df = pd.concat([m5._csv_da_zip(p, m5.KLINE) for p in file], ignore_index=True)
    df["giorno"] = m5._ms(df["open_time"]) // 86_400_000
    df = df.drop_duplicates("giorno", keep="last").set_index("giorno").sort_index()
    return df[["open", "high", "low", "close", "volume", "quote_volume", "taker_buy_quote_volume"]].astype(float)


def funding_giorni(simbolo: str) -> pd.Series:
    """La somma dei tassi di funding per giorno di tenuta (sezione 3 di SECONDA.md)."""
    righe = []
    for p in sorted((DATI / simbolo / "funding").glob("*.zip")):
        righe += funding_da_zip(p)
    if not righe:
        return pd.Series(dtype=float)
    df = pd.DataFrame(righe, columns=["ts", "ore", "tasso"]).drop_duplicates("ts")
    tenuta = (df["ts"].to_numpy() // 60_000 - 1) // 1440
    return pd.Series(df["tasso"].to_numpy(float), index=tenuta).groupby(level=0).sum()


def riempi_funding(f: np.ndarray, c_ok: np.ndarray, coperti: np.ndarray) -> np.ndarray:
    """Dove la moneta ha la candela ma non il dato di funding (dopo il primo regolamento), la media giornaliera dei 90
    giorni coperti prima (SECONDA.md, sezione 3)."""
    out = f.copy()
    idx = np.flatnonzero(coperti)
    if not len(idx):
        return out
    for t in np.flatnonzero(c_ok & ~coperti):
        if t < idx[0]:
            continue
        prima = idx[idx < t][-GIORNI_VOL:]
        out[t] = f[prima].mean() if len(prima) else 0.0
    return out


def costruisci_pannello(simboli=None, log=print) -> dict:
    if simboli is None:
        simboli = sorted(p.name for p in DATI.iterdir() if p.is_dir() and p.name not in ESCLUSI)
    serie, fund = {}, {}
    for s in simboli:
        c = candele(s)
        if len(c):
            serie[s], fund[s] = c, funding_giorni(s)
    t0 = min(int(c.index.min()) for c in serie.values())
    t1 = max(int(c.index.max()) for c in serie.values())
    T, nomi = t1 - t0 + 1, sorted(serie)
    P = {k: np.full((T, len(nomi)), np.nan)
         for k in ("open", "high", "low", "close", "quote_volume", "taker_buy_quote_volume")}
    F = np.zeros((T, len(nomi)))
    for j, s in enumerate(nomi):
        c = serie[s]
        r = c.index.to_numpy() - t0
        for k in P:
            P[k][r, j] = c[k].to_numpy()
        f = fund[s]
        f = f[(f.index >= t0) & (f.index <= t1)]
        col = np.zeros(T)
        col[f.index.to_numpy() - t0] = f.to_numpy()
        # giorni coperti: quelli di un mese che ha almeno un regolamento
        coperti = np.zeros(T, bool)
        if len(f):
            mesi = pd.to_datetime((np.arange(T) + t0) * 86400, unit="s").to_period("M")
            mesi_f = set(pd.to_datetime((f.index.to_numpy()) * 86400, unit="s").to_period("M"))
            coperti = np.array([m in mesi_f for m in mesi]) & (np.arange(T) <= f.index.max() - t0)
        F[:, j] = riempi_funding(col, np.isfinite(P["close"][:, j]), coperti)
        log(f"[pannello] {s}")
    pan = {"t0": t0, "simboli": nomi, **P, "funding": F}
    pd.to_pickle(pan, PANNELLO)
    return pan


def pannello() -> dict:
    return pd.read_pickle(PANNELLO)


# ---------------------------------------------------------------------------
# universo (SECONDA.md, sezione 4)
# ---------------------------------------------------------------------------

def universo(pan: dict, n: int) -> np.ndarray:
    """Maschera (giorni × monete): vero se la moneta e' nell'universo del mese del giorno di tenuta."""
    C, V, t0 = pan["close"], pan["quote_volume"], pan["t0"]
    T, S = C.shape
    ok = np.isfinite(C)
    primo = np.where(ok.any(axis=0), ok.argmax(axis=0), T)
    U = np.zeros((T, S), bool)
    giorni = np.arange(T) + t0
    mesi = pd.to_datetime(giorni * 86400, unit="s").to_period("M")
    for m in pd.unique(mesi):
        righe = np.flatnonzero(mesi == m)
        r0 = righe[0]                       # primo giorno del mese (indice)
        if r0 < 1:
            continue
        ieri = r0 - 1
        finestra = V[max(0, r0 - GIORNI_VOLUME): r0]
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", RuntimeWarning)
            med = np.nanmedian(finestra, axis=0)
        ammesse = ok[ieri] & (r0 - primo >= STORIA_MIN) & (np.nan_to_num(med, nan=0.0) >= VOLUME_MIN)
        cand = np.flatnonzero(ammesse)
        scelte = cand[np.argsort(-med[cand], kind="stable")][:n]
        U[np.ix_(righe, scelte)] = True
    return U


# ---------------------------------------------------------------------------
# la regola pubblicata (SECONDA.md, sezione 5)
# ---------------------------------------------------------------------------

@njit(cache=True)
def _stato(c, entra, mid, verso):
    """Lo stato (0/1) di un modello di Donchian sulle chiusure: ingresso quando ``entra``; lo stop parte dal punto medio
    e segue (sale per i long, scende per gli short); uscita quando la chiusura passa lo stop del giorno prima."""
    n = len(c)
    out = np.zeros(n, np.int8)
    on = False
    stop = 0.0
    for t in range(n):
        uscito = False
        if on:
            if (verso > 0 and c[t] < stop) or (verso < 0 and c[t] > stop):
                on = False
                uscito = True
            elif mid[t] == mid[t]:
                stop = max(stop, mid[t]) if verso > 0 else min(stop, mid[t])
        if not on and not uscito and entra[t] and mid[t] == mid[t]:
            on = True
            stop = mid[t]
        out[t] = 1 if on else 0
    return out


def segnale_moneta(c: np.ndarray, short: bool = False) -> np.ndarray:
    """Il segnale (media dei nove modelli) su una serie di chiusure senza buchi: da 0 a 1 (solo long) o da -1 a 1."""
    s = pd.Series(c)
    tot = np.zeros(len(c))
    for L in PERIODI:
        mx, mn = s.rolling(L).max(), s.rolling(L).min()
        mid = ((mx + mn) / 2).to_numpy()
        sopra = (s > mx.shift(1)).to_numpy()
        tot += _stato(c, sopra, mid, 1)
        if short:
            sotto = (s < mn.shift(1)).to_numpy()
            tot -= _stato(c, sotto, mid, -1)
    return tot / len(PERIODI)


def moltiplicatore(c: np.ndarray) -> np.ndarray:
    r = pd.Series(c).pct_change()
    vol = r.rolling(GIORNI_VOL).std().to_numpy() * math.sqrt(365)
    with np.errstate(divide="ignore", invalid="ignore"):
        return np.where(vol > 0, np.minimum(VOL_OBIETTIVO / vol, MOLT_MAX), np.nan)


def _per_moneta(C: np.ndarray, funz) -> np.ndarray:
    """Applica ``funz`` alla serie di ogni moneta senza i giorni mancanti e rimette i valori al loro posto."""
    out = np.full(C.shape, np.nan)
    for j in range(C.shape[1]):
        ok = np.isfinite(C[:, j])
        if ok.sum() > 1:
            out[ok, j] = funz(C[ok, j])
    return out


def rendimenti(pan: dict) -> np.ndarray:
    """Rendimento del giorno di tenuta: apertura → apertura dopo (o chiusura se manca la candela dopo)."""
    O, C = pan["open"], pan["close"]
    uscita = np.vstack([O[1:], np.full((1, O.shape[1]), np.nan)])
    uscita = np.where(np.isfinite(uscita), uscita, C)
    with np.errstate(all="ignore"):
        r = uscita / O - 1
    return np.where(np.isfinite(r), r, 0.0)


def pesi_regola(pan: dict, variante: str, U: np.ndarray) -> np.ndarray:
    """I pesi decisi alla chiusura di ogni giorno (per il giorno dopo)."""
    C = pan["close"]
    short = variante == "A2"
    if variante == "A3":
        j = pan["simboli"].index("BTCUSDT")
        s = np.zeros(C.shape)
        m = np.zeros(C.shape)
        ok = np.isfinite(C[:, j])
        s[ok, j] = segnale_moneta(C[ok, j])
        m[ok, j] = moltiplicatore(C[ok, j])
        W = s * np.nan_to_num(m)
        domani = np.vstack([np.isfinite(C[1:]), np.zeros((1, C.shape[1]), bool)])
        return np.where(domani, W, 0.0)
    if variante == "sempre":
        s = np.where(np.isfinite(C), 1.0, np.nan)
    else:
        s = _per_moneta(C, lambda c: segnale_moneta(c, short))
    m = _per_moneta(C, moltiplicatore)
    W = np.nan_to_num(s) * np.nan_to_num(m) / N_A
    domani_u = np.vstack([U[1:], np.zeros((1, C.shape[1]), bool)])
    domani = np.vstack([np.isfinite(pan["open"][1:]), np.zeros((1, C.shape[1]), bool)])
    return np.where(domani_u & domani, W, 0.0)


def costi_moneta(simboli) -> np.ndarray:
    """Il costo di un giro di peso: commissione a mercato piu' lo scarto (SECONDA.md, sezione 5)."""
    return np.array([TAKER + m5.scarto(s) for s in simboli])


@njit(cache=True)
def _portafoglio(W, r, F, costo):
    T, S = W.shape
    lordo = np.zeros(T)
    spese = np.zeros(T)
    fund = np.zeros(T)
    giro = np.zeros(T)
    deriva = np.zeros(S)
    for h in range(1, T):
        g = 0.0
        sp = 0.0
        lo = 0.0
        fu = 0.0
        for i in range(S):
            w = W[h - 1, i]
            d = abs(w - deriva[i])
            g += d
            sp += d * costo[i]
            lo += w * r[h, i]
            fu += w * F[h, i]
        lordo[h] = lo
        spese[h] = sp
        fund[h] = fu
        giro[h] = g
        netto = lo - sp - fu
        for i in range(S):
            deriva[i] = W[h - 1, i] * (1 + r[h, i]) / (1 + netto) if 1 + netto > 0 else 0.0
    return lordo, spese, fund, giro


def portafoglio(pan: dict, W: np.ndarray) -> pd.DataFrame:
    """Il conto giornaliero: lordo, spese (commissioni e scarto sul giro), funding, netto, netto a costi doppi."""
    r = rendimenti(pan)
    lordo, spese, fund, giro = _portafoglio(np.ascontiguousarray(W), np.ascontiguousarray(r),
                                            np.ascontiguousarray(pan["funding"]), costi_moneta(pan["simboli"]))
    giorni = np.arange(W.shape[0]) + pan["t0"]
    esp = np.vstack([np.zeros((1, W.shape[1])), W[:-1]])
    df = pd.DataFrame({"lordo": lordo, "spese": spese, "funding": fund, "giro": giro,
                       "esposizione": np.abs(esp).sum(axis=1), "netta": esp.sum(axis=1)}, index=giorni)
    df["netto"] = df["lordo"] - df["spese"] - df["funding"]
    df["netto_doppio"] = df["lordo"] - 2 * df["spese"] - df["funding"]
    return df


# ---------------------------------------------------------------------------
# esame (SECONDA.md, sezione 7)
# ---------------------------------------------------------------------------

def bootstrap_blocchi(x: np.ndarray, blocco: int = 20, n: int = 10000, seme: int = 2026) -> dict:
    """Media e intervallo al 95% con il bootstrap a blocchi circolari."""
    x = np.asarray(x, float)
    T = len(x)
    rng = np.random.default_rng(seme)
    k = int(math.ceil(T / blocco))
    est = np.concatenate([x, x[:blocco]])
    medie = np.empty(n)
    for b in range(n):
        inizi = rng.integers(0, T, k)
        idx = (inizi[:, None] + np.arange(blocco)[None, :]).ravel()[:T]
        medie[b] = est[idx].mean()
    return {"media": float(x.mean()), "basso": float(np.percentile(medie, 2.5)),
            "alto": float(np.percentile(medie, 97.5)), "p": float((np.sum(medie <= 0) + 1) / (n + 1))}


def numeri(netto: pd.Series) -> dict:
    x = netto.to_numpy()
    sd = x.std(ddof=1)
    eq = np.cumprod(1 + x)
    return {"giorni": int(len(x)), "annuo": float(x.mean() * 365), "volatilita": float(sd * math.sqrt(365)),
            "sharpe": float(x.mean() / sd * math.sqrt(365)) if sd > 0 else 0.0,
            "discesa_max": float((eq / np.maximum.accumulate(eq) - 1).min()),
            "totale": float(eq[-1] - 1), "asimmetria": float(pd.Series(x).skew()),
            "curtosi": float(pd.Series(x).kurt() + 3)}


def esame_a(df: pd.DataFrame, btc: pd.Series) -> dict:
    d = df[df.index >= INIZIO]
    e = {"intero": numeri(d["netto"]), "boot": bootstrap_blocchi(d["netto"].to_numpy()),
         "costi_doppi": float(d["netto_doppio"].mean()), "esposizione_media": float(d["esposizione"].mean()),
         "giro_annuo": float(d["giro"].mean() * 365), "spese_annue": float(d["spese"].mean() * 365),
         "funding_annuo": float(d["funding"].mean() * 365)}
    anni = pd.to_datetime(d.index.to_numpy() * 86400, unit="s").year
    e["per_anno"] = {int(a): float(d["netto"][anni == a].mean() * 365) for a in sorted(set(anni))}
    e["ultimo_anno"] = float(d["netto"][d.index >= ULTIMO_ANNO].mean() * 365)
    e["dopo_articolo"] = numeri(d["netto"][d.index >= PUBBLICAZIONE])
    b = btc.reindex(d.index).fillna(0.0).to_numpy()
    X = np.vstack([np.ones(len(b)), b]).T
    coef, *_ = np.linalg.lstsq(X, d["netto"].to_numpy(), rcond=None)
    e["extra_btc_annuo"], e["beta_btc"] = float(coef[0] * 365), float(coef[1])
    return e


def esito_a(e: dict, dsr: float) -> str:
    if not e["boot"]["basso"] > 0:
        return "netto con l'intervallo non sopra zero"
    if not dsr >= 0.95:
        return f"Sharpe corretto {dsr:.2f} sotto 0,95"
    if sum(1 for v in e["per_anno"].values() if v > 0) < 4:
        return "positiva in meno di 4 anni"
    if not e["ultimo_anno"] > 0:
        return "non positiva nell'ultimo anno"
    if not e["dopo_articolo"]["annuo"] > 0:
        return "non positiva dopo l'articolo"
    if not e["costi_doppi"] > 0:
        return "non positiva a costi doppi"
    if not e["extra_btc_annuo"] > 0:
        return "niente in più del Bitcoin"
    return "VALIDA"


def parte_a(pan: dict) -> dict:
    U = universo(pan, N_A)
    r = rendimenti(pan)
    btc = pd.Series(r[:, pan["simboli"].index("BTCUSDT")], index=np.arange(r.shape[0]) + pan["t0"])
    RIS.mkdir(exist_ok=True)
    out = {}
    for v in ("A1", "A2", "A3", "sempre"):
        df = portafoglio(pan, pesi_regola(pan, v, U))
        df.to_csv(RIS / f"giorni_{v}.csv.gz")
        out[v] = esame_a(df, btc)
    out["btc"] = {"intero": numeri(btc[btc.index >= INIZIO]),
                  "dopo_articolo": numeri(btc[btc.index >= PUBBLICAZIONE])}
    # chi c'era nell'universo, mese per mese (per il controllo)
    mesi = {}
    for t in range(0, U.shape[0]):
        g = data(t + pan["t0"])
        if g.endswith("-01") and U[t].any():
            mesi[g[:7]] = [pan["simboli"][j] for j in np.flatnonzero(U[t])]
    out["universo"] = mesi
    (RIS / "A.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    return out


# ---------------------------------------------------------------------------
# parte B: le famiglie della prima prova a 1 giorno (SECONDA.md, sezione 6)
# ---------------------------------------------------------------------------

def barre_giorno(pan: dict, j: int) -> pd.DataFrame:
    """Le candele di una moneta nel formato del motore della prima prova (funding cumulato alla chiusura)."""
    C = pan["close"][:, j]
    ok = np.flatnonzero(np.isfinite(C))
    if not len(ok):
        return pd.DataFrame()
    a, z = ok[0], ok[-1] + 1
    b = pd.DataFrame({k: pan[k][a:z, j] for k in ("open", "high", "low", "close", "quote_volume")})
    b["funding_cum"] = np.cumsum(pan["funding"][a:z, j])
    b["minuto"] = (np.arange(a, z) + pan["t0"]) * 1440
    return b


def trade_famiglia_giorni(famiglia: str, pan: dict, U: np.ndarray) -> tuple:
    from research.programma6 import motore as mo
    from research.programma6.famiglie import FAMIGLIE, combinazioni
    funz = FAMIGLIE[famiglia][0]
    combo = combinazioni(famiglia, tempi=["1d"])
    parti = []
    usate = np.flatnonzero(U.any(axis=0))
    for j in usate:
        s = pan["simboli"][j]
        b = barre_giorno(pan, j)
        if len(b) < 250:
            continue
        a = mo.atr(b)
        cache = {}
        slip = m5.scarto(s)
        for k, cmb in enumerate(combo):
            chiave = tuple(sorted(cmb["segnali"].items()))
            if chiave not in cache:
                cache[chiave] = funz(b, **cmb["segnali"])
            u, ing = cmb["uscita"], cmb["ingresso"]
            t = mo.simula(b, a, cache[chiave], u["stop_k"], u["tp_k"], u["trail_k"], u["max_barre"],
                          ing["limite_k"], ing["validita"], slip)
            if not len(t["R"]):
                continue
            g = t["minuto_in"] // 1440 - pan["t0"]
            dentro = U[g, j]
            if not dentro.any():
                continue
            parti.append(pd.DataFrame({"k": k, "simbolo": s, "minuto": t["minuto_in"][dentro],
                                       "uscita": t["minuto_out"][dentro], "direzione": t["direzione"][dentro],
                                       "R": t["R"][dentro], "netto": t["netto"][dentro],
                                       "netto_doppio": t["netto_doppio"][dentro],
                                       "frazione_stop": t["frazione_stop"][dentro], "motivo": t["motivo"][dentro]}))
    tutti = pd.concat(parti, ignore_index=True) if parti else pd.DataFrame()
    if len(tutti):
        tutti = tutti[np.isfinite(tutti["R"])]
    return combo, tutti


def capitale_tetto(t: pd.DataFrame, rischio: float = 0.01, tetto: float = 5.0) -> dict:
    """Il capitale con il tetto: un trade nuovo non si apre se il valore delle posizioni aperte supererebbe ``tetto``
    volte il capitale (SECONDA.md, sezione 6). Rendimento giornaliero = somma dei trade chiusi nel giorno."""
    t = t.sort_values("minuto")
    leva = np.minimum(tetto, rischio / t["frazione_stop"].to_numpy())
    presi = np.zeros(len(t), bool)
    aperti = []          # (uscita, leva)
    for i, (m, u, lv) in enumerate(zip(t["minuto"].to_numpy(), t["uscita"].to_numpy(), leva)):
        aperti = [(x, y) for x, y in aperti if x > m]
        if sum(y for _, y in aperti) + lv <= tetto + 1e-12:
            aperti.append((u, lv))
            presi[i] = True
    p = t[presi]
    r = pd.Series(leva[presi] * p["netto"].to_numpy(), index=p["uscita"].to_numpy() // 1440).groupby(level=0).sum()
    tutti = pd.Series(0.0, index=np.arange(r.index.min(), r.index.max() + 1))
    tutti.loc[r.index] = r.to_numpy()
    out = numeri(tutti)
    out["trade_presi"] = int(presi.sum())
    return out


def una_b(famiglia: str, pan: dict, U: np.ndarray) -> dict:
    from research.programma6 import finestre as fi
    combo, tr = trade_famiglia_giorni(famiglia, pan, U)
    if tr.empty:
        return {"trade": 0}
    t, scelte = fi.avanza(tr, combo, tempi=["1d"])
    e = fi.esame(t)
    e["pbo"] = fi.pbo(tr, len(combo))
    e["combinazioni"] = len(combo)
    e["scelte"] = [{"trimestre": datetime.fromtimestamp(s["da"] * 60, tz=timezone.utc).strftime("%Y-%m"),
                    "combinazione": combo[s["combinazione"]] if s["combinazione"] >= 0 else None} for s in scelte]
    if e.get("trade"):
        e["capitale_tetto"] = capitale_tetto(t)
        t.to_csv(RIS / f"trade_B_{famiglia}.csv.gz", index=False)
    (RIS / f"B_{famiglia}.json").write_text(json.dumps(e, ensure_ascii=False, indent=1, default=float),
                                            encoding="utf-8")
    return e


def parte_b(pan: dict, famiglie=None, log=print) -> None:
    from research.programma6.famiglie import FAMIGLIE
    U = universo(pan, N_B)
    RIS.mkdir(exist_ok=True)
    for f in (famiglie or list(FAMIGLIE)):
        e = una_b(f, pan, U)
        log(f"[B] {f} {e.get('trade')}")


# ---------------------------------------------------------------------------
# rapporto
# ---------------------------------------------------------------------------

def sharpe_prove() -> list:
    """Gli Sharpe annui di tutte le prove del programma 6 (prima prova, A1-A3, B)."""
    sr = []
    for f in sorted((QUI / "risultati").glob("*.json")):
        e = json.loads(f.read_text())
        if e.get("trade"):
            sr.append(e["capitale"]["sharpe_annuo"])
    a = json.loads((RIS / "A.json").read_text()) if (RIS / "A.json").exists() else {}
    sr += [a[v]["intero"]["sharpe"] for v in ("A1", "A2", "A3") if v in a]
    for f in sorted(RIS.glob("B_*.json")):
        e = json.loads(f.read_text())
        if e.get("trade"):
            sr.append(e["capitale"]["sharpe_annuo"])
    return sr


def rapporto() -> str:
    from research.programma6 import finestre as fi
    from research.programma6.esegui import esito
    sr = sharpe_prove()
    while len(sr) < PROVE_PROGRAMMA:
        sr.append(0.0)       # le prove non ancora fatte contano nel numero (SECONDA.md, sezione 7)
    a = json.loads((RIS / "A.json").read_text())
    righe = ["# Programma 6 — risultati della seconda prova", "",
             "Regole in `SECONDA.md` (scritte prima). Dal 2021-01-01 all'ultimo giorno scaricato; universo mese per mese "
             "con i soli dati di allora, fra tutte le monete dell'archivio.", "",
             "## Parte A — la regola pubblicata (Zarattini, Pagani e Barbon 2025)", "",
             "| Variante | Rendimento/anno | Intervallo (giorno) | Volatilità | Sharpe | Sharpe corretto | Discesa massima | "
             "Anni positivi | Ultimo anno | Dopo l'articolo (anno; Sharpe) | Costi doppi (giorno) | In più del BTC/anno | "
             "Esposizione media | Esito |", "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for v in ("A1", "A2", "A3", "sempre"):
        e = a[v]
        i = e["intero"]
        dsr = fi.sharpe_corretto(i["sharpe"], i["giorni"], i["asimmetria"], i["curtosi"], sr)
        anni = sum(1 for x in e["per_anno"].values() if x > 0)
        es = esito_a(e, dsr) if v != "sempre" else "confronto"
        righe.append(f"| {v} | {100 * i['annuo']:+.1f}% | {100 * e['boot']['basso']:+.3f}%; {100 * e['boot']['alto']:+.3f}% | "
                     f"{100 * i['volatilita']:.1f}% | {i['sharpe']:.2f} | {dsr:.2f} | {100 * i['discesa_max']:.1f}% | "
                     f"{anni}/{len(e['per_anno'])} | {100 * e['ultimo_anno']:+.1f}% | "
                     f"{100 * e['dopo_articolo']['annuo']:+.1f}%; {e['dopo_articolo']['sharpe']:.2f} | "
                     f"{100 * e['costi_doppi']:+.4f}% | {100 * e['extra_btc_annuo']:+.1f}% | "
                     f"{e['esposizione_media']:.2f} | {es} |")
    b = a["btc"]
    righe += ["", f"Bitcoin sempre comprato: {100 * b['intero']['annuo']:+.1f}% l'anno, Sharpe {b['intero']['sharpe']:.2f}, "
                  f"discesa massima {100 * b['intero']['discesa_max']:.1f}%; dopo l'articolo {100 * b['dopo_articolo']['annuo']:+.1f}% "
                  f"l'anno, Sharpe {b['dopo_articolo']['sharpe']:.2f}.", ""]
    righe += ["### Per anno (rendimento netto annualizzato)", "", "| Variante | " +
              " | ".join(str(x) for x in a["A1"]["per_anno"]) + " |", "|---|" + "---|" * len(a["A1"]["per_anno"])]
    for v in ("A1", "A2", "A3", "sempre"):
        righe.append(f"| {v} | " + " | ".join(f"{100 * x:+.1f}%" for x in a[v]["per_anno"].values()) + " |")
    fb = sorted(RIS.glob("B_*.json"))
    if fb:
        righe += ["", "## Parte B — le famiglie della prima prova a 1 giorno, con le finestre che avanzano", "",
                  "| Famiglia | Trade | R a trade | Intervallo | Netto a trade | Sharpe (con tetto) | Rendimento/anno (con tetto) | "
                  "Sharpe corretto | PBO | Anni positivi | Ultimo anno (R) | Esito |",
                  "|---|---|---|---|---|---|---|---|---|---|---|---|"]
        for f in fb:
            e = json.loads(f.read_text())
            nome = f.stem[2:]
            if not e.get("trade"):
                righe.append(f"| {nome} | 0 | | | | | | | | | | non opera |")
                continue
            cap = e["capitale"]
            dsr = fi.sharpe_corretto(cap["sharpe_annuo"], cap["giorni"], cap["asimmetria"], cap["curtosi"], sr)
            anni = sum(1 for x in e["per_anno"].values() if x["trade"] > 0 and x["R"] > 0)
            ct = e.get("capitale_tetto", {})
            righe.append(f"| {nome} | {e['trade']} | {e['R']['media']:+.3f} | {e['R']['basso']:+.3f}; {e['R']['alto']:+.3f} | "
                         f"{100 * e['netto']['media']:+.3f}% | {ct.get('sharpe', float('nan')):.2f} | "
                         f"{100 * ct.get('annuo', float('nan')):+.1f}% | {dsr:.2f} | {e['pbo']:.2f} | "
                         f"{anni}/{len(e['per_anno'])} | {e['ultimo_anno']['R']:+.3f} | {esito(e, dsr)} |")
    testo = "\n".join(righe) + "\n"
    (QUI / "RISULTATI_SECONDA.md").write_text(testo, encoding="utf-8")
    return testo


if __name__ == "__main__":
    cosa = sys.argv[1] if len(sys.argv) > 1 else "tutto"
    if cosa in ("pannello", "tutto"):
        costruisci_pannello(log=lambda x: None)
        print("PANNELLO PRONTO", flush=True)
    if cosa in ("A", "tutto"):
        parte_a(pannello())
        print("A FINITA", flush=True)
    if cosa in ("B", "tutto"):
        parte_b(pannello(), sys.argv[2:] or None, log=lambda x: print(x, flush=True))
        print("B FINITA", flush=True)
    if cosa in ("rapporto", "tutto", "A", "B"):
        print(rapporto())
