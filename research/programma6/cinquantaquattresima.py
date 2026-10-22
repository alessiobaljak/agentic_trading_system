"""Programma 6, cinquantaquattresima prova (CINQUANTAQUATTRESIMA.md): lo scalping sul serio. Cinque schemi sulle candele a
1 minuto delle 30 monete piu' scambiate del mese (fra le 100 di research/data/p5), dal 2024-01-01 al 2026-10-15: Z1 lo stile
del canale (15 minuti, tendenza + ritracciamento, tre obiettivi, stop all'entrata dopo il primo, 5 al giorno), Z1b uguale
senza il limite di 5 al giorno, Z2 il ritorno alla VWAP (5 minuti), Z3 la rottura della prima ora americana, Z4 la spinta
del volume (1 minuto). Entrate e obiettivi a ordine limite dove scritto.

Scelte di calcolo non scritte nelle regole (fissate prima di guardare i risultati):
* Ogni moneta si simula da sola, una operazione alla volta (un ordine in attesa tiene occupata la moneta fino alla scadenza);
  i limiti del portafoglio (5 aperte insieme; per Z1 le prime 5 operazioni eseguite del giorno per ora d'entrata, gli ordini
  non eseguiti non contano) si applicano dopo, su tutte le operazioni in ordine d'entrata. Una operazione tolta dal limite non
  libera la moneta per un segnale successivo (approssimazione: le operazioni contate possono essere un po' meno).
* Nel minuto in cui un limite d'entrata si esegue si guarda solo lo stop (non gli obiettivi); lo stop all'entrata dopo il TP1
  vale dal minuto dopo quello in cui il TP1 si esegue.
* Z1: «la chiusura torna sotto la media 20» = la chiusura a 15 minuti passa da sopra (o uguale) a sotto la EMA 20 (al
  contrario per lo short). Z2: l'obiettivo e' la VWAP alla chiusura della candela del segnale; la deviazione e' quella dello
  scarto chiusura − VWAP dalle candele a 5 minuti del giorno, compresa quella del segnale. Z3: il range vale con almeno 50
  minuti con il dato su 60. Z4: il rendimento della candela e' chiusura su chiusura del minuto prima.
* Il funding: i regolamenti dei file mensili dell'archivio; dove il file del mese non c'e' (settembre-ottobre 2026) vale zero.
* L'esame del portafoglio e' `terza.esito` con una sola differenza: «positiva in almeno 4 anni» (pensata per 6 anni) diventa
  «positiva in almeno due terzi degli anni» (2 su 3: 2024, 2025, 2026); i trimestri sugli anni pieni 2024 e 2025.

Uso: python3 -m research.programma6.cinquantaquattresima
"""
from __future__ import annotations

import json
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd
from numba import njit

from research.programma5.strumenti import motore5 as m5
from research.programma6 import asticella as ast
from research.programma6 import seconda as sc
from research.programma6 import terza as te
from research.programma6 import ventunesima as vu
from research.src.dati import funding_da_zip

QUI = Path(__file__).parent
RIS = QUI / "risultati_cinquantaquattresima"
DATI = QUI.parents[1] / "research" / "data" / "p5"
DA, A = sc.giorno(2024, 1, 1), sc.giorno(2026, 10, 15)
N_MONETE, RISCHIO, MAX_APERTE, MAX_GIORNO = 30, 0.01, 5, 5
SCHEMI = ("Z1", "Z1b", "Z2", "Z3", "Z4")
P_SOGLIA = 0.01 / len(SCHEMI)
MOTIVI = {1: "stop", 2: "pareggio dopo il TP1", 3: "obiettivi", 4: "tempo"}


# ---------------------------------------------------------------------------
# dati
# ---------------------------------------------------------------------------

def minuti(simbolo: str, da: int, a: int) -> pd.DataFrame:
    """Le candele a 1 minuto dal giorno `da` al giorno `a` (giorni dall'epoca), griglia senza buchi (NaN dove mancano)."""
    d0, d1 = date.fromordinal(date(1970, 1, 1).toordinal() + da), date.fromordinal(date(1970, 1, 1).toordinal() + a)
    file = [p for p in sorted((DATI / simbolo / "klines").glob("*.zip")) if p.with_suffix(".zip.ok").exists()
            and m5._dentro(p.name, d0, d1)]
    if not file:
        return pd.DataFrame()
    df = pd.concat([m5._csv_da_zip(p, m5.KLINE) for p in file], ignore_index=True)
    df["minuto"] = m5._ms(df["open_time"]) // 60_000
    df = df[(df["minuto"] >= da * 1440) & (df["minuto"] < (a + 1) * 1440)]
    df = df.drop_duplicates("minuto").set_index("minuto").sort_index()
    df = df[["open", "high", "low", "close", "volume", "taker_buy_volume"]].astype(float)
    return df.reindex(np.arange(df.index.min(), df.index.max() + 1))


def funding_minuti(simbolo: str, indice: np.ndarray) -> np.ndarray:
    """Il tasso di funding nel minuto del regolamento (0 altrove), sulla griglia dei minuti."""
    out = np.zeros(len(indice))
    righe = []
    for p in sorted((DATI / simbolo / "funding").glob("*.zip")):
        try:
            righe += funding_da_zip(p)
        except Exception:  # noqa: BLE001
            continue
    m0 = int(indice[0])
    for ts, _ore, tasso in righe:
        k = int(ts) // 60_000 - m0
        if 0 <= k < len(out):
            out[k] = tasso
    return out


def universo_mensile(pan: dict, simboli: list) -> dict:
    """{(anno, mese): insieme delle 30 monete piu' scambiate} fra `simboli`, mediana del volume dei 30 giorni prima."""
    V = pan["quote_volume"]
    col = {s: pan["simboli"].index(s) for s in simboli if s in pan["simboli"]}
    out = {}
    g = DA
    while g <= A:
        y, m = map(int, sc.data(g)[:7].split("-"))
        primo = sc.giorno(y, m, 1)
        k = primo - pan["t0"]
        med = {s: float(np.nanmedian(V[max(0, k - 30): k, j])) for s, j in col.items()}
        med = {s: v for s, v in med.items() if np.isfinite(v) and v > 0}
        out[(y, m)] = set(sorted(med, key=lambda s: -med[s])[:N_MONETE])
        g = sc.giorno(y + (m == 12), m % 12 + 1, 1)
    return out


# ---------------------------------------------------------------------------
# il simulatore al minuto
# ---------------------------------------------------------------------------

@njit(cache=True)
def simula(o, h, l, c, fund, s_min, tipo, verso, livello, valido, sl, tp1, tp2, tp3, f1, f2, f3, be, max_hold, max_abs,
           costo_mercato, maker):
    """Per ogni segnale (minuti relativi alla griglia, in ordine): l'operazione. Una alla volta per moneta.
    tipo 0 = a mercato all'apertura del minuto s, 1 = limite al livello valido `valido` minuti.
    Ritorna righe (segnale, entrata, uscita, verso, prezzo, R netto, R lordo, costo in R, tp1 preso, motivo)."""
    n = len(o)
    out = []
    occupata = -1
    for i in range(len(s_min)):
        s = s_min[i]
        if s <= occupata or s >= n:
            continue
        v = verso[i]
        # --- l'entrata
        e = -1
        p0 = 0.0
        costo = 0.0
        if tipo[i] == 0:
            if np.isfinite(o[s]):
                e = s
                p0 = o[s]
                costo = costo_mercato
        else:
            fine = min(n, s + valido[i])
            for m in range(s, fine):
                if not np.isfinite(l[m]):
                    continue
                if (v > 0 and l[m] < livello[i]) or (v < 0 and h[m] > livello[i]):
                    e = m
                    break
            if e < 0:
                occupata = fine - 1
                continue
            p0 = livello[i]
            costo = maker
        if e < 0:
            continue
        stop = sl[i]
        rischio = abs(p0 - stop) / p0
        if not rischio > 0:
            continue
        tps = (tp1[i], tp2[i], tp3[i])
        frs = (f1[i], f2[i], f3[i])
        fatto = [False, False, False]
        resto = 1.0
        pnl = 0.0
        tp1_preso = False
        nuovo_stop = np.nan
        fine_t = n - 1
        if max_hold[i] > 0:
            fine_t = min(fine_t, e + max_hold[i])
        if max_abs[i] > 0:
            fine_t = min(fine_t, max_abs[i])
        uscita, motivo = -1, 0
        m = e
        while m <= fine_t:
            if m > e and fund[m] != 0.0:
                pnl -= v * fund[m] * resto
            if not np.isfinite(o[m]):
                m += 1
                continue
            if m == fine_t and m > e:
                pnl += resto * v * (o[m] / p0 - 1)
                costo += resto * costo_mercato
                uscita, motivo = m, 4
                break
            if np.isfinite(nuovo_stop):
                stop = nuovo_stop
                nuovo_stop = np.nan
            colpito = (l[m] <= stop) if v > 0 else (h[m] >= stop)
            if colpito:
                px = stop
                if m > e and ((v > 0 and o[m] < stop) or (v < 0 and o[m] > stop)):
                    px = o[m]
                pnl += resto * v * (px / p0 - 1)
                costo += resto * costo_mercato
                uscita = m
                motivo = 2 if tp1_preso and abs(stop - p0) < 1e-12 else 1
                break
            if m > e:
                for k in range(3):
                    if fatto[k] or not np.isfinite(tps[k]) or frs[k] <= 0:
                        continue
                    preso = (h[m] > tps[k]) if v > 0 else (l[m] < tps[k])
                    if preso:
                        fatto[k] = True
                        pnl += frs[k] * v * (tps[k] / p0 - 1)
                        costo += frs[k] * maker
                        resto -= frs[k]
                        if k == 0:
                            tp1_preso = True
                            if be[i]:
                                nuovo_stop = p0
                if resto <= 1e-9:
                    uscita, motivo = m, 3
                    break
            m += 1
        if uscita < 0:
            break
        out.append((s, e, uscita, v, p0, (pnl - costo) / rischio, pnl / rischio, costo / rischio, 1.0 if tp1_preso else 0.0,
                    motivo))
        occupata = uscita
    return out


# ---------------------------------------------------------------------------
# i segnali dei cinque schemi (minuti assoluti; i livelli in prezzo)
# ---------------------------------------------------------------------------

def _barre(df: pd.DataFrame, passo: int) -> pd.DataFrame:
    g = df.groupby(df.index.to_numpy() // passo)
    b = pd.DataFrame({"open": g["open"].first(), "high": g["high"].max(), "low": g["low"].min(), "close": g["close"].last(),
                      "volume": g["volume"].sum()})
    b["tp_v"] = (((df["high"] + df["low"] + df["close"]) / 3) * df["volume"]).groupby(df.index.to_numpy() // passo).sum()
    return b.dropna(subset=["close"])


def _vuoti(n):
    return {k: [] for k in ("s", "tipo", "verso", "livello", "valido", "sl", "tp1", "tp2", "tp3", "f1", "f2", "f3", "be",
                            "max_hold", "max_abs")}


def _aggiungi(d, **kw):
    for k, v in kw.items():
        d[k].append(v)


def segnali_z1(df: pd.DataFrame) -> dict:
    b = _barre(df, 15)
    c = b["close"]
    e20, e50, e200 = (c.ewm(span=n, adjust=False, min_periods=n).mean() for n in (20, 50, 200))
    sotto = (c < e20) & (c.shift(1) >= e20.shift(1))
    sopra = (c > e20) & (c.shift(1) <= e20.shift(1))
    lungo = sotto & (e50 > e200)
    corto = sopra & (e50 < e200)
    d = _vuoti(0)
    for k in b.index[lungo.to_numpy() | corto.to_numpy()]:
        v = 1 if lungo[k] else -1
        p = float(c[k])
        _aggiungi(d, s=int((k + 1) * 15), tipo=1, verso=v, livello=p, valido=60, sl=p * (1 - v * 0.015),
                  tp1=p * (1 + v * 0.006), tp2=p * (1 + v * 0.012), tp3=p * (1 + v * 0.02), f1=1 / 3, f2=1 / 3, f3=1 / 3,
                  be=True, max_hold=1440, max_abs=-1)
    return d


def segnali_z2(df: pd.DataFrame) -> dict:
    b = _barre(df, 5)
    giorno = (b.index.to_numpy() * 5) // 1440
    vwap = b["tp_v"].groupby(giorno).cumsum() / b["volume"].groupby(giorno).cumsum()
    scarto = b["close"] - vwap
    dev = scarto.groupby(giorno).expanding().std().reset_index(level=0, drop=True)
    n = scarto.groupby(giorno).cumcount() + 1
    ok = (n >= 24) & (dev > 0) & np.isfinite(vwap)
    lungo = ok & (b["close"] < vwap - 2 * dev)
    corto = ok & (b["close"] > vwap + 2 * dev)
    d = _vuoti(0)
    for k in b.index[lungo.to_numpy() | corto.to_numpy()]:
        v = 1 if lungo[k] else -1
        p, w = float(b.at[k, "close"]), float(vwap[k])
        _aggiungi(d, s=int((k + 1) * 5), tipo=1, verso=v, livello=p, valido=15, sl=p - (w - p), tp1=w, tp2=np.nan,
                  tp3=np.nan, f1=1.0, f2=0.0, f3=0.0, be=False, max_hold=120, max_abs=-1)
    return d


def segnali_z3(df: pd.DataFrame) -> dict:
    d = _vuoti(0)
    o = df["open"]
    for g in np.unique(df.index.to_numpy() // 1440):
        r = df.loc[g * 1440 + 810: g * 1440 + 869]
        if r["close"].notna().sum() < 50:
            continue
        hi, lo = float(r["high"].max()), float(r["low"].min())
        alto = hi - lo
        if not alto > 0:
            continue
        mezzo = (hi + lo) / 2
        dopo = df.loc[g * 1440 + 870: g * 1440 + 1199]
        if dopo.empty:
            continue
        b5 = dopo["close"].groupby(dopo.index.to_numpy() // 5).last().dropna()
        for k, cl in b5.items():
            v = 1 if cl > hi else (-1 if cl < lo else 0)
            if v == 0:
                continue
            s = int((k + 1) * 5)
            if s not in o.index or not np.isfinite(o[s]):
                break
            p0 = float(o[s])
            if (v > 0 and p0 <= mezzo) or (v < 0 and p0 >= mezzo):
                break
            _aggiungi(d, s=s, tipo=0, verso=v, livello=p0, valido=0, sl=mezzo, tp1=p0 + v * alto, tp2=p0 + 2 * v * alto,
                      tp3=np.nan, f1=0.5, f2=0.5, f3=0.0, be=True, max_hold=-1, max_abs=int(g * 1440 + 1200))
            break
    return d


def segnali_z4(df: pd.DataFrame) -> dict:
    vol = df["volume"]
    med = vol.rolling(60, min_periods=60).median().shift(1)
    ret = df["close"] / df["close"].shift(1) - 1
    quota = df["taker_buy_volume"] / vol.where(vol > 0)
    spinta = vol > 10 * med
    lungo = spinta & (ret > 0.005) & (quota > 0.7)
    corto = spinta & (ret < -0.005) & (quota < 0.3)
    o = df["open"]
    d = _vuoti(0)
    for t in df.index[(lungo | corto).to_numpy()]:
        s = int(t + 1)
        if s not in o.index or not np.isfinite(o[s]):
            continue
        v = 1 if lungo[t] else -1
        p0 = float(o[s])
        _aggiungi(d, s=s, tipo=0, verso=v, livello=p0, valido=0, sl=p0 * (1 - v * 0.005), tp1=p0 * (1 + v * 0.01),
                  tp2=np.nan, tp3=np.nan, f1=1.0, f2=0.0, f3=0.0, be=False, max_hold=30, max_abs=-1)
    return d


GENERATORI = {"Z1": segnali_z1, "Z2": segnali_z2, "Z3": segnali_z3, "Z4": segnali_z4}


def operazioni_moneta(simbolo: str, df: pd.DataFrame, fund: np.ndarray, dentro) -> dict:
    """Le operazioni di una moneta per schema (Z1b ha le stesse operazioni di Z1: cambia solo il limite del giorno)."""
    m0 = int(df.index[0])
    o, h, l, c = (df[k].to_numpy(float) for k in ("open", "high", "low", "close"))
    costo_mercato = m5.TAKER + m5.scarto(simbolo)
    out = {}
    for nome, gen in GENERATORI.items():
        d = gen(df)
        if not d["s"]:
            out[nome] = []
            continue
        tieni = [i for i, s in enumerate(d["s"]) if dentro(s)]
        if not tieni:
            out[nome] = []
            continue
        a = {k: np.asarray([d[k][i] for i in tieni]) for k in d}
        ordine = np.argsort(a["s"], kind="stable")
        a = {k: v[ordine] for k, v in a.items()}
        righe = simula(o, h, l, c, fund, (a["s"] - m0).astype(np.int64), a["tipo"].astype(np.int64),
                       a["verso"].astype(np.int64), a["livello"].astype(float), a["valido"].astype(np.int64),
                       a["sl"].astype(float), a["tp1"].astype(float), a["tp2"].astype(float), a["tp3"].astype(float),
                       a["f1"].astype(float), a["f2"].astype(float), a["f3"].astype(float), a["be"].astype(np.bool_),
                       a["max_hold"].astype(np.int64), a["max_abs"].astype(np.int64), costo_mercato, m5.MAKER)
        out[nome] = [{"simbolo": simbolo, "segnale": int(r[0]) + m0, "entrata": int(r[1]) + m0, "uscita": int(r[2]) + m0,
                      "verso": int(r[3]), "prezzo": float(r[4]), "R": float(r[5]), "R_lordo": float(r[6]),
                      "costo_R": float(r[7]), "tp1": bool(r[8]), "motivo": MOTIVI[int(r[9])]} for r in righe]
    return out


# ---------------------------------------------------------------------------
# il portafoglio e l'esame
# ---------------------------------------------------------------------------

def portafoglio(ops: pd.DataFrame, max_giorno: int | None) -> pd.DataFrame:
    """Le operazioni tenute: al massimo 5 aperte insieme e, se `max_giorno`, le prime `max_giorno` del giorno per entrata."""
    if ops.empty:
        return ops
    d = ops.sort_values(["entrata", "simbolo"]).reset_index(drop=True)
    aperte, tenute, per_giorno = [], [], {}
    for k, x in d.iterrows():
        aperte = [u for u in aperte if u > x["entrata"]]
        g = int(x["entrata"]) // 1440
        if len(aperte) >= MAX_APERTE or (max_giorno and per_giorno.get(g, 0) >= max_giorno):
            continue
        aperte.append(int(x["uscita"]))
        per_giorno[g] = per_giorno.get(g, 0) + 1
        tenute.append(k)
    return d.loc[tenute].reset_index(drop=True)


def settimane(t: pd.DataFrame) -> pd.DataFrame:
    giorno = t["uscita"].to_numpy() // 1440
    lun = ((giorno + 3) // 7) * 7 - 3
    tutte = np.arange(DA, A + 1, 7)
    netto = pd.Series(RISCHIO * t["R"].to_numpy(), index=lun).groupby(level=0).sum().reindex(tutte).fillna(0.0)
    doppio = pd.Series(RISCHIO * (t["R"] - t["costo_R"]).to_numpy(), index=lun).groupby(level=0).sum().reindex(tutte).fillna(0.0)
    out = pd.DataFrame({"netto": netto, "netto_doppio": doppio})
    for k in ("lordo", "spese", "funding", "giro", "long", "short"):
        out[k] = 0.0
    out["monete"] = 1
    return out


def esito_portafoglio(e: dict, dsr: float) -> str:
    """`terza.esito` con gli anni positivi in almeno due terzi (vedi in testa al file)."""
    if not e["boot"]["basso"] > 0:
        return "netto con l'intervallo non sopra zero"
    if not dsr >= 0.95:
        return f"Sharpe corretto {dsr:.2f} sotto 0,95"
    anni = list(e["per_anno"].values())
    if sum(1 for v in anni if v > 0) < (2 / 3) * len(anni):
        return f"positiva in meno di due terzi degli anni ({len(anni)})"
    if not e["ultimo_anno"] > 0:
        return "non positiva nell'ultimo anno"
    if not e["costi_doppi"] > 0:
        return "non positiva a costi doppi"
    for a in sorted({k[:4] for k in e["per_trimestre"]}):
        if sum(1 for q in range(1, 5) if e["per_trimestre"][f"{a}T{q}"] > 0) < 2:
            return f"positiva in meno di 2 trimestri nel {a}"
    if not e["extra_btc_annuo"] > 0:
        return "niente in più del Bitcoin"
    return "VALIDA"


def esame_operazioni(t: pd.DataFrame) -> dict:
    d = t.sort_values("entrata").reset_index(drop=True)
    d["annuncio"] = d["entrata"] // 1440
    e = {"boot": vu.bootstrap_annunci(d, "R")}
    meta = len(d) // 2
    e["prima_meta"], e["seconda_meta"] = float(d["R"].iloc[:meta].mean()), float(d["R"].iloc[meta:].mean())
    migliori = d.groupby("annuncio")["R"].sum().sort_values(ascending=False).index[:5]
    e["senza_5_giorni_migliori"] = float(d.loc[~d["annuncio"].isin(migliori), "R"].mean())
    vinte, perse = d["R"] > 0, d["R"] <= 0
    e.update({"operazioni": int(len(d)), "vinte": float(vinte.mean()), "tp1": float(d["tp1"].mean()),
              "R_vinte": float(d.loc[vinte, "R"].mean()) if vinte.any() else float("nan"),
              "R_perse": float(d.loc[perse, "R"].mean()) if perse.any() else float("nan"),
              "costo_R": float(d["costo_R"].mean()), "R_lordo": float(d["R_lordo"].mean()),
              "motivi": d["motivo"].value_counts(normalize=True).round(3).to_dict(),
              "per_anno": {a: {"operazioni": int(len(g)), "R": float(g["R"].mean())}
                           for a, g in d.groupby(pd.to_datetime(d["entrata"] * 60, unit="s").dt.year)},
              "long_short": {int(v): float(g["R"].mean()) for v, g in d.groupby("verso")}})
    e["passa"] = bool(e["boot"]["p"] <= P_SOGLIA and e["prima_meta"] > 0 and e["seconda_meta"] > 0
                      and e["senza_5_giorni_migliori"] > 0)
    return e


def esegui(log=print) -> dict:
    pan = sc.pannello()
    simboli = sorted(p.name for p in DATI.iterdir() if (p / "klines").is_dir())
    uni = universo_mensile(pan, simboli)
    usate = sorted(set().union(*uni.values()))
    log(f"[cinquantaquattresima] {len(usate)} monete entrano almeno un mese fra le 30")
    tutte = {k: [] for k in GENERATORI}
    for n, s in enumerate(usate):
        df = minuti(s, DA - 10, A)
        if df.empty:
            continue
        fund = funding_minuti(s, df.index.to_numpy())

        def dentro(minuto, s=s):
            g = int(minuto) // 1440
            if not (DA <= g <= A):
                return False
            y, m = map(int, sc.data(g)[:7].split("-"))
            return s in uni.get((y, m), set())

        for k, v in operazioni_moneta(s, df, fund, dentro).items():
            tutte[k] += v
        log(f"[cinquantaquattresima] {n + 1}/{len(usate)} {s}: " + ", ".join(f"{k} {len(v)}" for k, v in tutte.items()))
        del df, fund
    RIS.mkdir(exist_ok=True)
    pr = te.pannello_settimane(pan, log=lambda x: None, indicatori_si=False)
    btc = pd.Series(pr["R"][:, pr["simboli"].index("BTCUSDT")], index=pr["lunedi"])
    esami, serie = {}, {}
    for nome in SCHEMI:
        base = pd.DataFrame(tutte["Z1" if nome == "Z1b" else nome])
        t = portafoglio(base, MAX_GIORNO if nome == "Z1" else None)
        if len(t) < 30:
            esami[nome] = {"operazioni": int(len(t)), "esito": "troppo poche operazioni"}
            continue
        sett = settimane(t)
        sett.to_csv(RIS / f"settimane_{nome}.csv.gz")
        t.to_csv(RIS / f"operazioni_{nome}.csv.gz", index=False)
        e = {"operazioni": esame_operazioni(t), "segnali_eseguiti_prima_dei_limiti": int(len(base))}
        e["portafoglio"] = te.esame(sett, btc, inizio=DA, anni_pieni=(2024, 2025))
        serie[f"54 {nome}"] = sett["netto"]
        esami[nome] = e
    nuove = {f"49 {k}": pd.read_csv(QUI / "risultati_quarantanovesima" / f"settimane_{k}.csv.gz", index_col=0)["netto"]
             for k in ("X1", "X2")}
    nuove["51 F7"] = pd.read_csv(QUI / "risultati_cinquantunesima" / "settimane_F7.csv.gz", index_col=0)["netto"]
    nuove["52 B1"] = pd.read_csv(QUI / "risultati_cinquantaduesima" / "settimane_B1.csv.gz", index_col=0)["netto"]
    nuove["53 F8"] = pd.read_csv(QUI / "risultati_cinquantatreesima" / "settimane_F8.csv.gz", index_col=0)["netto"]
    nuove.update(serie)
    candidate = {f"54 {n}": e["portafoglio"]["intero"] for n, e in esami.items() if "portafoglio" in e}
    rivisto = ast.corretto_rivisto(nuove, candidate)
    for nome, e in esami.items():
        if "portafoglio" not in e:
            continue
        p = e["portafoglio"]
        r = rivisto["candidate"][f"54 {nome}"]
        p["sharpe_corretto"], p["t"], p["gruppo"], p["gruppi"] = r["corretto"], r["t"], r["gruppo"], rivisto["gruppi"]
        p["esito"] = esito_portafoglio(p, p["sharpe_corretto"])
        e["esito"] = "VALIDA" if e["operazioni"]["passa"] and p["esito"] == "VALIDA" else "non valida"
    (RIS / "esame.json").write_text(json.dumps(esami, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    righe = ["# Programma 6 — risultati della cinquantaquattresima prova (lo scalping sul serio)", "",
             "Regole in `CINQUANTAQUATTRESIMA.md` (scritte prima; Z1b aggiunto prima dei risultati, sezione 3bis); le scelte "
             "di calcolo non scritte nelle regole sono in testa a `cinquantaquattresima.py`. Le 30 monete più scambiate di ogni "
             f"mese fra le 100 con le candele a 1 minuto, dal 2024-01-01 al 2026-10-15; {len(usate)} monete in tutto.", "",
             "| Schema | Operazioni | Vinte | Almeno il TP1 | R medio netto (lordo) | Vinte, perse (R medio) | Costi (R) | p | "
             "Portafoglio: l'anno, Sharpe, discesa | Esito |", "|---|---|---|---|---|---|---|---|---|---|"]
    for nome, e in esami.items():
        if "portafoglio" not in e:
            righe.append(f"| {nome} | {e['operazioni']} | | | | | | | | {e['esito']} |")
            continue
        o, p = e["operazioni"], e["portafoglio"]
        i = p["intero"]
        righe.append(f"| {nome} | {o['operazioni']} | {100 * o['vinte']:.0f}% | {100 * o['tp1']:.0f}% | {o['boot']['media']:+.3f} "
                     f"({o['R_lordo']:+.3f}) | {o['R_vinte']:+.2f}, {o['R_perse']:+.2f} | {o['costo_R']:.3f} | {o['boot']['p']:.4f} | "
                     f"{100 * i['annuo']:+.1f}%, {i['sharpe']:.2f}, {100 * i['discesa_max']:.1f}% | {e['esito']} |")
    righe += [""]
    for nome, e in esami.items():
        if "portafoglio" not in e:
            continue
        o, p = e["operazioni"], e["portafoglio"]
        righe.append(f"* **{nome}**: per anno " + ", ".join(f"{a} {x['R']:+.3f} R ({x['operazioni']})" for a, x in o["per_anno"].items())
                     + "; uscite " + ", ".join(f"{k} {100 * v:.0f}%" for k, v in o["motivi"].items())
                     + f"; metà {o['prima_meta']:+.3f} e {o['seconda_meta']:+.3f}; senza i 5 giorni migliori {o['senza_5_giorni_migliori']:+.3f}; "
                     f"Sharpe corretto rivisto {p['sharpe_corretto']:.2f} ({p['gruppi']} gruppi), t {p['t']:.2f}; portafoglio: {p['esito']}.")
    righe += ["", f"Soglia per operazione p ≤ {P_SOGLIA:.4f} (0,01 diviso i 5 schemi). R = guadagno in multipli del rischio "
              "fra entrata e stop (1% del capitale a operazione)."]
    testo = "\n".join(righe) + "\n"
    (QUI / "RISULTATI_CINQUANTAQUATTRESIMA.md").write_text(testo, encoding="utf-8")
    log(testo)
    return esami


if __name__ == "__main__":
    esegui(log=lambda x: print(x, flush=True))
    print("CINQUANTAQUATTRESIMA FINITA", flush=True)
