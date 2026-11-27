"""Audit di F5 nella configurazione del conto vero (27 novembre 2026, backtest-auditor).

F5 = prova 24 (`research/programma6/VENTIQUATTRESIMA.md`), con la correzione delle parita' del 23 ottobre (`sesta.funding_7`
arrotondato, `CONTROLLO_PARITA.md`). Il conto vero (`bot/portafoglio/conto_vero.py`, spento) legge i pesi del paper di F5
(`bot/portafoglio/f5.py`, `data/paper_f5.json`) e li esegue con ordini limite al prezzo mark per un'ora, poi a mercato, con i
filtri veri di Binance (`bot/portafoglio/filtri_conto_vero.json`) e un capitale fino a 300 USDT.

Uso (dalla radice del repository):
  python3 -I audits/repro/f5_conto_vero_2026-11-27.py <parte> --codice <cartella del codice> --pannello <pickle> --cache <cartella>
  --codice   cartella con `research/` e `bot/` del commit da provare (copia fatta con `git archive`; di serie la radice)
  --pannello il pannello giornaliero salvato (`seconda.pannello()` copiato; di serie quello di `seconda.pannello()`)
  --cache    cartella temporanea per le cache (mai `research/data/`)
Parti: base ore dati taglio parita tempi costi conto rischio misure sensi corretto
Ogni parte scrive solo `audits/repro/f5_conto_vero_2026-11-27_esito_<parte>.json`. Non scrive mai fuori da `audits/` e dalla cache.
"""
from __future__ import annotations

import argparse
import json
import math
import pickle
import sys
import time
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

QUI = Path(__file__).resolve().parent
RADICE = QUI.parents[1]
ARG = argparse.ArgumentParser()
ARG.add_argument("parte")
ARG.add_argument("--codice", default=str(RADICE))
ARG.add_argument("--pannello", default="")
ARG.add_argument("--cache", default="/tmp/f5_audit_cache")
A = ARG.parse_args()
CODICE = Path(A.codice)
sys.path.insert(0, str(CODICE))
CACHE = Path(A.cache)
CACHE.mkdir(parents=True, exist_ok=True)

from research.programma6 import ottava as ot  # noqa: E402
from research.programma6 import seconda as sc  # noqa: E402
from research.programma6 import sesta as se  # noqa: E402
from research.programma6 import terza as te  # noqa: E402
from research.programma6 import ventiquattresima as vq  # noqa: E402
from research.programma6.motore import MAKER, TAKER  # noqa: E402

INIZIO = sc.giorno(2021, 1, 4)              # VENTIQUATTRESIMA.md, sezione 3: «dal 4 gennaio 2021»
FINE_MAZZO = sc.giorno(2026, 10, 5)         # asticella.periodo: «dal 4 gennaio 2021 al 5 ottobre 2026» (301 lunedi')
FINE_300 = sc.giorno(2026, 9, 28)           # le 300 settimane citate il 25 novembre («al 4 ottobre»)
FILTRI = CODICE / "bot" / "portafoglio" / "filtri_conto_vero.json"
TICK = 1e-12


def log(*a):
    print(time.strftime("%H:%M:%S"), *a, flush=True)


def salva(parte: str, out: dict) -> None:
    f = QUI / f"f5_conto_vero_2026-11-27_esito_{parte}.json"
    f.write_text(json.dumps(out, ensure_ascii=False, indent=1, default=float), encoding="utf-8")
    log("scritto", f.name)


def pannello() -> dict:
    return pd.read_pickle(A.pannello) if A.pannello else sc.pannello()


def numeri(x: pd.Series) -> dict:
    x = x.astype(float)
    v = x.to_numpy()
    sd = v.std(ddof=1)
    eq = np.cumprod(1 + v)
    picco = np.maximum.accumulate(eq)
    dd = eq / picco - 1
    # durata della discesa piu' lunga sotto il massimo (settimane)
    sotto, lungo, cur = dd < -1e-12, 0, 0
    for s_ in sotto:
        cur = cur + 1 if s_ else 0
        lungo = max(lungo, cur)
    neg = v[v < 0]
    dsd = math.sqrt((np.minimum(v, 0) ** 2).mean()) if len(v) else 0.0
    anni = len(v) / 52
    return {"settimane": int(len(v)), "annuo": float(v.mean() * 52), "composto_annuo": float(eq[-1] ** (1 / anni) - 1) if anni > 0 else 0.0,
            "volatilita": float(sd * math.sqrt(52)), "sharpe": float(v.mean() / sd * math.sqrt(52)) if sd > 0 else 0.0,
            "sortino": float(v.mean() * 52 / (dsd * math.sqrt(52))) if dsd > 0 else 0.0,
            "discesa_max": float(dd.min()), "discesa_settimane_piu_lunga": int(lungo),
            "asimmetria": float(pd.Series(v).skew()), "curtosi": float(pd.Series(v).kurt() + 3),
            "t": float(v.mean() / sd * math.sqrt(len(v))) if sd > 0 else 0.0,
            "settimane_negative": int((v < 0).sum()), "peggiore": float(v.min()), "migliore": float(v.max())}


def per_anno(x: pd.Series) -> dict:
    anni = pd.to_datetime(x.index.to_numpy() * 86400, unit="s").year
    return {int(a): float(x[anni == a].mean() * 52) for a in sorted(set(anni))}


def per_anno_composto(x: pd.Series) -> dict:
    anni = pd.to_datetime(x.index.to_numpy() * 86400, unit="s").year
    return {int(a): float(np.prod(1 + x[anni == a].to_numpy()) - 1) for a in sorted(set(anni))}


# ---------------------------------------------------------------------------
# F5 come la ricerca (ventiquattresima con la correzione delle parita')
# ---------------------------------------------------------------------------

def f5(pan, entra=vq.ENTRA, resta=vq.RESTA, giorni_f=7, giorni_s=30, n_uni=te.N_UNIVERSO, ps=None):
    if ps is None or n_uni != te.N_UNIVERSO:
        ps = te.pannello_settimane(pan, log=lambda x: None, indicatori_si=False, a=n_uni)
    lun = ps["lunedi"] - pan["t0"]
    sig = ot.sigma_30(pan, lun) if giorni_s == 30 else sigma_n(pan, lun, giorni_s)
    if giorni_f == 7:
        S = se.funding_7(pan, lun)
    else:
        Fc = np.vstack([np.zeros((1, pan["funding"].shape[1])), np.cumsum(pan["funding"], axis=0)])
        S = np.round(Fc[lun] - Fc[lun - giorni_f], 12)
    vecchi = (vq.ENTRA, vq.RESTA)
    vq.ENTRA, vq.RESTA = entra, resta
    try:
        W = vq.pesi_banda(np.where(np.isfinite(sig), -S, np.nan), ps["U"], sig)
    finally:
        vq.ENTRA, vq.RESTA = vecchi
    return W, ps


def sigma_n(pan, lun_idx, n):
    C = pan["close"]
    with np.errstate(all="ignore"):
        r = C[1:] / C[:-1] - 1
    r = np.vstack([np.full((1, C.shape[1]), np.nan), r])
    out = np.full((len(lun_idx), C.shape[1]), np.nan)
    minimo = int(round(20 * n / 30))
    for k, m in enumerate(lun_idx):
        f = r[max(0, m - n): m]
        cnt = np.isfinite(f).sum(axis=0)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", RuntimeWarning)
            sd = np.nanstd(f, axis=0, ddof=1)
        out[k] = np.where((cnt >= minimo) & (sd > 0), sd, np.nan)
    return out


def carica_base():
    f = CACHE / "base.pkl"
    if f.exists():
        with open(f, "rb") as h:
            return pickle.load(h)
    pan = pannello()
    W, ps = f5(pan)
    costo = sc.costi_moneta(ps["simboli"])
    df = te.conto(W, ps["R"], ps["F"], costo)
    df.index = ps["lunedi"]
    b = {"pan": pan, "ps": ps, "W": W, "costo": costo, "df": df}
    with open(f, "wb") as h:
        pickle.dump(b, h)
    return b


def nel_periodo(s: pd.Series, fine=FINE_MAZZO) -> pd.Series:
    return s[(s.index >= INIZIO) & (s.index <= fine)]


def parte_base():
    b = carica_base()
    pan, ps, W, df = b["pan"], b["ps"], b["W"], b["df"]
    out = {"pannello": {"primo": sc.data(pan["t0"]), "ultimo": sc.data(pan["t0"] + pan["close"].shape[0] - 1),
                        "monete": len(pan["simboli"])},
           "settimane_nel_pannello": [sc.data(int(df.index[0])), sc.data(int(df.index[-1]))]}
    for nome, fine in (("al_28_settembre_300", FINE_300), ("al_5_ottobre_mazzo", FINE_MAZZO), ("al_12_ottobre", sc.giorno(2026, 10, 12)),
                       ("al_19_ottobre", sc.giorno(2026, 10, 19)), ("tutto", int(df.index[-1]))):
        x = nel_periodo(df["netto"], fine)
        out[nome] = numeri(x) | {"per_anno": per_anno(x)}
    salvate = {"controllo_parita": RADICE / "research/programma6/risultati_controllo_parita/settimane_F5.csv.gz",
               "ventiquattresima_originale": RADICE / "research/programma6/risultati_ventiquattresima/settimane_F5.csv.gz"}
    for nome, f in salvate.items():
        old = pd.read_csv(f, index_col=0)
        c = old.index.intersection(df.index)
        c = c[c >= INIZIO]
        diff = (old.loc[c, "netto"] - df.loc[c, "netto"]).abs()
        out[f"confronto_{nome}"] = {"settimane_comuni": int(len(c)), "ultima": sc.data(int(c[-1])),
                                    "diverse_oltre_1e-9": int((diff > 1e-9).sum()),
                                    "diverse": {sc.data(int(i)): [round(float(old.loc[i, "netto"]), 6), round(float(df.loc[i, "netto"]), 6)]
                                                for i in diff[diff > 1e-9].index[:20]},
                                    "sharpe_salvata_al_5_ottobre": numeri(nel_periodo(old["netto"]))["sharpe"]}
    # esame della ricerca (terza.esame) sullo stesso periodo, per i numeri della regola
    btc = pd.Series(ps["R"][:, ps["simboli"].index("BTCUSDT")], index=ps["lunedi"])
    e = te.esame(df[df.index <= FINE_MAZZO], btc, inizio=INIZIO, anni_pieni=se.ANNI_PIENI)
    out["esame_terza_al_5_ottobre"] = {k: e[k] for k in ("giro_medio", "spese_annue", "funding_annuo", "long_annuo", "short_annuo",
                                                          "settimane_ferme", "per_anno", "ultimo_anno", "costi_doppi",
                                                          "extra_btc_annuo", "beta_btc", "boot")}
    lati = W[(ps["lunedi"] >= INIZIO) & (ps["lunedi"] <= FINE_MAZZO)]
    out["monete_per_lato"] = {"long": float((lati > 0).sum(axis=1).mean()), "short": float((lati < 0).sum(axis=1).mean()),
                              "long_min": int((lati > 0).sum(axis=1).min()), "short_min": int((lati < 0).sum(axis=1).min())}
    salva("base", out)


# ---------------------------------------------------------------------------
# le candele orarie del lunedi' (archivio mensile da 1 ora della copia locale, `quarta.ore`)
# ---------------------------------------------------------------------------

def carica_ore():
    f = CACHE / "ore.pkl"
    if f.exists():
        with open(f, "rb") as h:
            return pickle.load(h)
    from research.programma6 import quarta as qa
    b = carica_base()
    pan, ps, W = b["pan"], b["ps"], b["W"]
    lun = ps["lunedi"]                         # giorni dall'epoca
    S = W.shape[1]
    nomi = ("O00", "H00", "L00", "C00", "O01", "H01", "L01", "O02", "O04")
    H = {k: np.full((len(lun), S), np.nan) for k in nomi}
    usati = np.flatnonzero(np.abs(W).sum(axis=0) > 0)
    for j in usati:
        z = qa.ore(ps["simboli"][j])
        if z.empty:
            continue
        for k, nome in enumerate(nomi):
            ora = int(nome[1:])
            col = {"O": "open", "H": "high", "L": "low", "C": "close"}[nome[0]]
            idx = lun * 24 + ora
            ok = (idx >= z.index.min()) & (idx <= z.index.max())
            v = np.full(len(lun), np.nan)
            v[ok] = z[col].reindex(idx[ok]).to_numpy()
            H[nome][:, j] = v
    with open(f, "wb") as h:
        pickle.dump(H, h)
    return H


def parte_ore():
    H = carica_ore()
    b = carica_base()
    W, ps = b["W"], b["ps"]
    sett = (ps["lunedi"] >= INIZIO) & (ps["lunedi"] <= FINE_MAZZO)
    tenute = (np.abs(W) > 0) & sett[:, None]
    out = {k: {"coppie_tenute_senza": int((tenute & ~np.isfinite(v)).sum()), "coppie_tenute": int(tenute.sum())} for k, v in H.items()}
    # le candele orarie contro le giornaliere all'apertura del lunedi'
    O = b["pan"]["open"][ps["lunedi"] - b["pan"]["t0"]]
    ok = tenute & np.isfinite(H["O00"]) & np.isfinite(O)
    rel = np.abs(H["O00"][ok] / O[ok] - 1)
    out["apertura_ora_contro_giorno"] = {"coppie": int(ok.sum()), "oltre_0,1%": int((rel > 0.001).sum()), "massimo": float(rel.max())}
    salva("ore", out)


# ---------------------------------------------------------------------------
# A. dati
# ---------------------------------------------------------------------------

def parte_dati():
    from research.programma5.strumenti import motore5 as m5
    from research.src.dati import funding_da_zip
    b = carica_base()
    pan, ps, W = b["pan"], b["ps"], b["W"]
    t0 = pan["t0"]
    lun = ps["lunedi"]
    sett = np.flatnonzero((lun >= INIZIO) & (lun <= FINE_MAZZO))
    # tenute per giorno: la moneta j e' tenuta nei 7 giorni della settimana w
    T, S = pan["close"].shape
    tenuta = np.zeros((T, S), bool)
    for w in sett:
        m = lun[w] - t0
        tenuta[m:m + 7] |= (W[w] != 0)[None, :]
    usati = np.flatnonzero(tenuta.any(axis=0))
    C, O, V = pan["close"], pan["open"], pan["quote_volume"]
    out = {"monete_tenute": int(len(usati)), "giorni_moneta_tenuti": int(tenuta.sum())}
    # buchi: giorno tenuto senza candela fra la prima e l'ultima candela della moneta
    buchi = {}
    for j in usati:
        ok = np.isfinite(C[:, j])
        idx = np.flatnonzero(ok)
        dentro = np.zeros(T, bool)
        dentro[idx[0]: idx[-1] + 1] = True
        man = tenuta[:, j] & dentro & ~ok
        if man.any():
            buchi[pan["simboli"][j]] = [sc.data(t0 + int(t)) for t in np.flatnonzero(man)]
    giorni_buchi = {}
    for s, gg in buchi.items():
        for g in gg:
            giorni_buchi[g] = giorni_buchi.get(g, 0) + 1
    out["buchi_tenuti"] = {"monete": len(buchi), "giorni_moneta": int(sum(len(v) for v in buchi.values())),
                           "per_giorno": dict(sorted(giorni_buchi.items()))}
    # giorni fermi (volume zero) tenuti
    fermi = tenuta & np.isfinite(C) & (np.nan_to_num(V) == 0)
    out["giorni_fermi_tenuti"] = {"giorni_moneta": int(fermi.sum()),
                                  "monete": sorted({pan["simboli"][j] for j in np.flatnonzero(fermi.any(axis=0))})[:30]}
    # valori anomali: rendimento del giorno oltre +100% o sotto -60% su giorni tenuti; alto < basso; apertura fuori dal giorno
    r = sc.rendimenti(pan)
    ano = tenuta & ((r > 1.0) | (r < -0.6))
    out["rendimenti_anomali_tenuti"] = [(pan["simboli"][j], sc.data(t0 + int(t)), round(float(r[t, j]), 4))
                                        for t, j in zip(*np.nonzero(ano))][:40]
    Hh, Ll = pan["high"], pan["low"]
    with np.errstate(invalid="ignore"):
        storti = tenuta & np.isfinite(C) & ((Hh < Ll) | (O > Hh * (1 + 1e-9)) | (O < Ll * (1 - 1e-9)) | (C > Hh * (1 + 1e-9))
                                            | (C < Ll * (1 - 1e-9)) | (O <= 0))
    out["candele_incoerenti_tenute"] = int(storti.sum())
    # file grezzi: doppioni, ordine, ore non a mezzanotte UTC (solo le monete tenute)
    dop = fuori_ordine = non_utc = 0
    per_moneta = {}
    for j in usati:
        s = pan["simboli"][j]
        file = sorted((sc.DATI / s / "giorni").glob("*.zip"))
        if not file:
            continue
        d = pd.concat([m5._csv_da_zip(p, m5.KLINE) for p in file], ignore_index=True)
        ms = m5._ms(d["open_time"]).to_numpy()
        nd = int(pd.Series(ms).duplicated().sum())
        fo = int((np.diff(ms) <= 0).sum()) - nd
        nu = int((ms % 86_400_000 != 0).sum())
        dop, fuori_ordine, non_utc = dop + nd, fuori_ordine + max(fo, 0), non_utc + nu
        if nd or nu:
            per_moneta[s] = {"doppioni": nd, "non_mezzanotte": nu}
    out["file_grezzi"] = {"doppioni": dop, "fuori_ordine_fra_file": fuori_ordine, "non_mezzanotte_utc": non_utc,
                          "monete_con_doppioni_o_ore": dict(list(per_moneta.items())[:20])}
    # funding: vero contro stimato nei giorni tenuti; orari dei regolamenti letti dai dati
    F = pan["funding"]
    stimati, diversi, fuori_ora, intervalli = {}, 0, 0, {}
    ultimo_vero = {}
    for j in usati:
        s = pan["simboli"][j]
        righe = []
        for p in sorted((sc.DATI / s / "funding").glob("*.zip")):
            righe += funding_da_zip(p)
        if not righe:
            stimati[s] = int(tenuta[:, j].sum())
            continue
        df = pd.DataFrame(righe, columns=["ts", "ore", "tasso"]).drop_duplicates("ts").sort_values("ts")
        minuti = df["ts"].to_numpy() // 60_000
        fuori_ora += int(((df["ts"].to_numpy() % 3_600_000) > 60_000).sum())
        gap = np.diff(df["ts"].to_numpy()) / 3_600_000
        for g in np.round(gap).astype(int):
            intervalli[int(g)] = intervalli.get(int(g), 0) + 1
        ten = (minuti - 1) // 1440
        vero = pd.Series(df["tasso"].to_numpy(float), index=ten).groupby(level=0).sum()
        giorni_ten = np.flatnonzero(tenuta[:, j]) + t0
        ultimo_vero[s] = int(ten.max())
        senza = [g for g in giorni_ten if g not in vero.index and g > ten.min()]
        if senza:
            stimati[s] = len(senza)
        cc = [g for g in giorni_ten if g in vero.index]
        if cc:
            a = np.array([F[g - t0, j] for g in cc])
            v = vero.reindex(cc).to_numpy()
            diversi += int((np.abs(a - v) > 1e-12).sum())
    ultimo = max(ultimo_vero.values()) if ultimo_vero else None
    out["funding"] = {"giorni_moneta_tenuti_senza_dato_vero": int(sum(stimati.values())),
                      "monete_con_giorni_stimati": len(stimati), "esempi": dict(list(sorted(stimati.items(), key=lambda kv: -kv[1]))[:15]),
                      "giorni_veri_diversi_dal_pannello": diversi, "regolamenti_oltre_un_minuto_dall_ora": fuori_ora,
                      "intervalli_fra_regolamenti_ore": dict(sorted(intervalli.items())),
                      "ultimo_giorno_di_tenuta_con_dato_vero": sc.data(ultimo) if ultimo else None}
    # settimane del periodo con funding stimato (giorni tenuti senza dato vero, per settimana)
    out["periodo_dichiarato"] = {"regole": "VENTIQUATTRESIMA.md sezione 3: dal 4 gennaio 2021, nessuna fine scritta",
                                 "mazzo": "asticella.periodo: dal 4 gennaio 2021 al 5 ottobre 2026",
                                 "decisione_25_novembre": "300 settimane al 4 ottobre (ultimo lunedi' 28 settembre)"}
    salva("dati", out)


# ---------------------------------------------------------------------------
# B. prova del taglio: i pesi di un lunedi' con il pannello fermo alla domenica piu' l'apertura del lunedi'
# ---------------------------------------------------------------------------

def tagliato(pan, m):
    T2 = m + 8
    out = {"t0": pan["t0"], "simboli": pan["simboli"]}
    for k in ("open", "high", "low", "close", "quote_volume", "taker_buy_quote_volume"):
        a = np.full((T2, pan[k].shape[1]), np.nan)
        a[:m] = pan[k][:m]
        if k == "open":
            a[m] = pan[k][m]
        out[k] = a
    f = np.zeros((T2, pan["funding"].shape[1]))
    f[:m] = pan["funding"][:m]
    out["funding"] = f
    return out


def parte_taglio():
    b = carica_base()
    pan, ps, W = b["pan"], b["ps"], b["W"]
    rng = np.random.default_rng(20261127)
    sett = np.flatnonzero((ps["lunedi"] >= INIZIO) & (ps["lunedi"] <= int(ps["lunedi"][-1])))
    scelte = sorted(set(rng.choice(sett, 14, replace=False).tolist()) | {int(sett[0]), int(sett[-1]), int(sett[-2])})
    esiti = {}
    for w in scelte:
        g = int(ps["lunedi"][w])
        p2 = tagliato(pan, g - pan["t0"])
        W2, ps2 = f5(p2)
        w2 = int(np.flatnonzero(ps2["lunedi"] == g)[0])
        esiti[sc.data(g)] = float(np.abs(W2[w2] - W[w]).max())
        log("taglio", sc.data(g), esiti[sc.data(g)])
    salva("taglio", {"differenza_massima_dei_pesi": esiti, "tutti_uguali": all(v < 1e-12 for v in esiti.values())})


# ---------------------------------------------------------------------------
# F. parita': le funzioni pure del bot (`bot/portafoglio/f5.py`) contro la ricerca, sugli stessi dati, ogni lunedi'
# ---------------------------------------------------------------------------

def parte_parita():
    from bot.portafoglio import f5 as bf
    b = carica_base()
    pan, ps, W = b["pan"], b["ps"], b["W"]
    t0 = pan["t0"]
    O, C, V, F = pan["open"], pan["close"], pan["quote_volume"], pan["funding"]
    T, S = C.shape
    ok = np.isfinite(C)
    primo_idx = np.where(ok.any(axis=0), ok.argmax(axis=0), T)
    sett = np.flatnonzero(ps["lunedi"] >= INIZIO)
    lunghi, corti = set(), set()
    # la banda del bot parte dalle posizioni della ricerca della settimana prima (come `banda_di_partenza`)
    w0 = sett[0] - 1
    simb = pan["simboli"]
    lunghi = {simb[j] for j in np.flatnonzero(W[w0] > 0)}
    corti = {simb[j] for j in np.flatnonzero(W[w0] < 0)}
    diverse, universi_diversi, max_diff, esempi = 0, 0, 0.0, []
    for w in sett:
        g = int(ps["lunedi"][w])
        m = g - t0
        giornaliere, primo, fund = {}, {}, {}
        for j in range(S):
            if not (np.isfinite(O[m, j]) or np.isfinite(C[m - 1, j])):
                continue
            gg = {}
            for d in range(m - 40, m + 1):
                if 0 <= d < T and (np.isfinite(C[d, j]) or (d == m and np.isfinite(O[d, j]))):
                    gg[d + t0] = (float(O[d, j]), float(C[d, j]) if d < m else float("nan"),
                                  float(V[d, j]) if d < m else float("nan"))
            if not gg:
                continue
            giornaliere[simb[j]] = gg
            primo[simb[j]] = int(primo_idx[j]) + t0
            fund[simb[j]] = {d + t0: float(F[d, j]) for d in range(m - 8, m)}
        uni = bf.universo(giornaliere, primo, g)
        uni_r = sorted(simb[j] for j in np.flatnonzero(ps["U"][w]))
        if sorted(uni) != uni_r:
            universi_diversi += 1
        sigma, seg = {}, {}
        for s in uni:
            sg = bf.sigma_30({d: v[1] for d, v in giornaliere[s].items()}, g)
            sigma[s] = sg
            seg[s] = -bf.funding_7(fund[s], g) if np.isfinite(sg) else float("nan")
        pesi, lunghi, corti = bf.pesi_banda(seg, sigma, lunghi, corti)
        wb = np.zeros(S)
        for s, x in pesi.items():
            wb[simb.index(s)] = x
        d = float(np.abs(wb - W[w]).max())
        max_diff = max(max_diff, d)
        if d > 1e-9:
            diverse += 1
            if len(esempi) < 10:
                lati = [(simb[j], round(float(W[w, j]), 4), round(float(wb[j]), 4)) for j in np.flatnonzero(np.abs(wb - W[w]) > 1e-9)][:6]
                esempi.append({"lunedi": sc.data(g), "differenze": lati})
    salva("parita", {"lunedi": int(len(sett)), "lunedi_con_pesi_diversi": diverse, "universi_diversi": universi_diversi,
                     "differenza_massima": max_diff, "esempi": esempi,
                     "nota": "il bot riceve qui gli stessi dati del pannello (funding del pannello, primo giorno = prima candela); "
                             "le differenze di dati vere (onboardDate, contratti in chiusura, tipo del sottostante, funding sommato "
                             "senza arrotondamento) non sono in questo confronto"})


# ---------------------------------------------------------------------------
# il conto con i costi a limite e il conto vero simulato
# ---------------------------------------------------------------------------

def tassi_limite(D, H, costo, oltre):
    """Il costo per unita' di ogni variazione D (settimane x monete): limite all'apertura del lunedi' per un'ora (MAKER) se il
    prezzo va oltre il livello di ``oltre``, altrimenti a mercato all'apertura delle 01:00 piu' il movimento contro (come
    `cinquantaseiesima.costo_limite`); senza candele orarie, a mercato."""
    O0, H0, L0, O1 = H["O00"], H["H00"], H["L00"], H["O01"]
    ok = np.isfinite(O0) & np.isfinite(H0) & np.isfinite(L0) & np.isfinite(O1) & (O0 > 0)
    compra = D > 0
    with np.errstate(invalid="ignore", divide="ignore"):
        preso = np.where(compra, L0 < O0 * (1 - oltre), H0 > O0 * (1 + oltre))
        contro = np.where(compra, O1 / O0 - 1, 1 - O1 / O0)
    tasso = np.where(ok & preso, MAKER, np.where(ok, costo[None, :] + np.nan_to_num(contro), costo[None, :]))
    return tasso, ok & preso, ok


def variazioni(W, R):
    D = np.zeros_like(W)
    deriva = np.zeros(W.shape[1])
    R0 = np.nan_to_num(R)
    for w in range(W.shape[0]):
        D[w] = W[w] - deriva
        lordo = float((W[w] * R0[w]).sum())
        deriva = W[w] * (1 + R0[w]) / (1 + lordo) if 1 + lordo > 0 else np.zeros_like(W[w])
    return D


def conto_con_tassi(W, R, F, tasso_per_d):
    """Come `terza.conto` (capitale che si compone, pesi che derivano), con un costo per unita' diverso per ogni variazione."""
    Wn, S = W.shape
    R0 = np.nan_to_num(R)
    righe = []
    deriva = np.zeros(S)
    for w in range(Wn):
        x = W[w]
        d = x - deriva
        lordo = float((x * R0[w]).sum())
        spese = float((np.abs(d) * tasso_per_d[w]).sum())
        fund = float((x * F[w]).sum())
        netto = lordo - spese - fund
        righe.append({"lordo": lordo, "spese": spese, "funding": fund, "netto": netto, "giro": float(np.abs(d).sum())})
        deriva = x * (1 + R0[w]) / (1 + netto) if 1 + netto > 0 else np.zeros(S)
    return pd.DataFrame(righe)


def carica_filtri(simboli):
    f = json.loads(FILTRI.read_text(encoding="utf-8"))["filtri"]
    vmin = np.array([float(f[s]["valore_minimo"]) if s in f else 5.0 for s in simboli])
    passo = np.array([float(f[s]["passo"]) if s in f else 0.0 for s in simboli])
    qmin = np.array([float(f[s]["quantita_minima"]) if s in f else 0.0 for s in simboli])
    return vmin, passo, qmin, np.array([s in f for s in simboli])


def simula_conto(b, H, capitale, modo_costi="mercato", oltre=0.0, minimi=True, chiusure_libere=False, composto=False,
                 entrata="00", fine=FINE_MAZZO, W=None, inizio=INIZIO, registra=False):
    """Il conto vero simulato, settimana per settimana, dalla partenza a conto vuoto il primo lunedi'.

    Ogni lunedi': obiettivo in quantita' = peso x base / prezzo (base = capitale fisso, o il valore del conto se ``composto``);
    variazione arrotondata verso zero al passo di oggi; saltata se sotto la quantita' minima o il valore minimo (anche le chiusure,
    come `demo_binance.ordini_del_giorno`; con ``chiusure_libere`` le riduzioni sotto il minimo si fanno, come «solo riduzione»).
    Prezzo: l'apertura del lunedi' (``entrata`` "00") o l'apertura delle 01:00 ("01") con il rendimento fino alla stessa ora del
    lunedi' dopo. Costi: ``mercato`` (TAKER + scarto della moneta, come la ricerca) o ``limite`` (`tassi_limite` con ``oltre``).
    Funding sul valore della posizione al lunedi' (come `terza.conto`). Una moneta senza prezzo il lunedi' (tolta dal listino) si
    chiude al suo ultimo valore, con il costo a mercato (come l'uscita implicita della ricerca)."""
    pan, ps = b["pan"], b["ps"]
    W = b["W"] if W is None else W
    S = W.shape[1]
    lun = ps["lunedi"]
    t0 = pan["t0"]
    sett = np.flatnonzero((lun >= inizio) & (lun <= fine))
    vmin, passo, qmin, _ = carica_filtri(pan["simboli"])
    costo = b["costo"]
    R = np.nan_to_num(ps["R"])
    if entrata == "01":
        P = H["O01"]
        with np.errstate(invalid="ignore", divide="ignore"):
            R1 = np.vstack([P[1:] / P[:-1] - 1, np.full((1, S), np.nan)])
        R = np.where(np.isfinite(R1), R1, R)
        prezzo = np.where(np.isfinite(P), P, pan["open"][lun - t0])
    else:
        prezzo = pan["open"][lun - t0]
    q = np.zeros(S)                                 # quantita' tenute (unita' di moneta, con il segno)
    ultimo_valore = np.zeros(S)                     # prezzo della moneta alla fine della settimana prima
    E = float(capitale)
    righe = []
    voluti = saltati = sotto_vmin = sotto_passo = polvere = 0
    mai_aperte = np.zeros(S, int)
    esposizione = []
    valori = {}                                     # con ``registra``: i valori tenuti dopo gli ordini del lunedi' (USDT)
    for w in sett:
        p = prezzo[w]
        vivo = np.isfinite(p) & (p > 0)
        base = E if composto else float(capitale)
        valore_prima = np.where(vivo, q * np.nan_to_num(p), 0.0)
        # monete con posizione e senza prezzo: chiusura al valore della settimana prima (uscita implicita)
        spese = 0.0
        morte = (q != 0) & ~vivo
        if morte.any():
            spese += float((np.abs(q[morte] * ultimo_valore[morte]) * costo[morte]).sum())
            q[morte] = 0.0
        obi = np.where(vivo, W[w] * base / np.where(vivo, p, 1.0), 0.0)
        delta = obi - q
        da_fare = vivo & (np.abs(delta * np.nan_to_num(p)) > 1e-9)
        if minimi:
            qa_ = np.abs(delta)
            qr = np.where(passo > 0, np.floor(qa_ / np.where(passo > 0, passo, 1.0) + 1e-9) * passo, qa_)
            val = qr * np.nan_to_num(p)
            riduce = (obi == 0) | ((q != 0) & (np.sign(q) == np.sign(obi)) & (np.abs(obi) < np.abs(q)))
            ok_q = qr >= qmin - 1e-12
            ok_v = val >= vmin - 1e-9
            ok = (qr > 0) & ok_q & ((ok_v | riduce) if chiusure_libere else ok_v)
            d = np.where(da_fare & ok, np.sign(delta) * qr, 0.0)
            voluti += int(da_fare.sum())
            saltati += int((da_fare & (d == 0)).sum())
            sotto_vmin += int((da_fare & ~ok_v).sum())
            sotto_passo += int((da_fare & (qr == 0)).sum())
            mai_aperte += ((W[w] != 0) & (q == 0) & (d == 0) & vivo).astype(int)
        else:
            d = np.where(da_fare, delta, 0.0)
        dv = d * np.nan_to_num(p)                   # valore scambiato con il segno (USDT)
        if modo_costi == "limite":
            tasso, _, _ = tassi_limite(np.sign(dv)[None, :], {k: v[w][None, :] for k, v in H.items()}, costo, oltre)
            tasso = tasso[0]
        else:
            tasso = costo
        spese += float((np.abs(dv) * tasso).sum())
        q = q + d
        # le quantita' restano sulla griglia del passo (senza, i resti della virgola mobile, 1e-16, sembrano posizioni)
        q = np.where(passo > 0, np.round(q / np.where(passo > 0, passo, 1.0)) * passo, q)
        q = np.where(np.abs(q * np.nan_to_num(p)) < 1e-9, 0.0, q)
        valore = np.where(vivo, q * np.nan_to_num(p), 0.0)
        if registra:
            valori[int(lun[w])] = (valore.copy(), E, spese)
        lordo = float((valore * R[w]).sum())
        fund = float((valore * ps["F"][w]).sum())
        netto = lordo - spese - fund
        r = netto / E if composto else netto / float(capitale)
        polvere += int(((W[w] == 0) & (q != 0)).sum())
        esposizione.append(float(np.abs(valore).sum() / base) if base > 0 else 0.0)
        righe.append({"lunedi": int(lun[w]), "netto": r, "lordo": lordo / base, "spese": spese / base, "funding": fund / base,
                      "lorda": esposizione[-1], "netta": float(valore.sum() / base) if base > 0 else 0.0,
                      "monete": int((q != 0).sum()), "ordini": int((d != 0).sum())})
        ultimo_valore = np.where(vivo, np.nan_to_num(p) * (1 + R[w]), 0.0)
        E = E + netto if composto else E
        if E <= 0:
            break
    df = pd.DataFrame(righe).set_index("lunedi")
    df.attrs = {"ordini_voluti": voluti, "saltati": saltati, "sotto_valore_minimo": sotto_vmin, "sotto_un_passo": sotto_passo,
                "settimane_moneta_con_polvere": polvere, "mai_aperte": mai_aperte, "valori": valori}
    return df


def parte_costi():
    b = carica_base()
    H = carica_ore()
    ps, W = b["ps"], b["W"]
    D = variazioni(W, ps["R"])
    out = {}
    base = te.conto(W, ps["R"], ps["F"], b["costo"])
    base.index = ps["lunedi"]
    out["mercato (ricerca)"] = numeri(nel_periodo(base["netto"])) | {"spese_annue": float(nel_periodo(base["spese"]).mean() * 52)}
    sett = (ps["lunedi"] >= INIZIO) & (ps["lunedi"] <= FINE_MAZZO)
    for oltre in (0.0, 0.0005, 0.001, 0.002):
        tasso, preso, ok = tassi_limite(D, H, b["costo"], oltre)
        df = conto_con_tassi(W, ps["R"], ps["F"], tasso)
        df.index = ps["lunedi"]
        x = nel_periodo(df["netto"])
        dd = np.abs(D) > 1e-9
        out[f"limite oltre {100 * oltre:.2f}%"] = numeri(x) | {
            "spese_annue": float(nel_periodo(df["spese"]).mean() * 52),
            "variazioni": int((dd & sett[:, None]).sum()), "eseguite_a_limite": int((dd & preso & sett[:, None]).sum()),
            "senza_ore": int((dd & ~ok & sett[:, None]).sum()),
            "costo_medio_per_unita": float((np.abs(D) * tasso)[sett].sum() / np.abs(D)[sett].sum())}
    # costi doppi e tripli a mercato
    for k in (2, 3):
        df = te.conto(W, ps["R"], ps["F"], b["costo"] * k)
        df.index = ps["lunedi"]
        out[f"mercato x{k}"] = numeri(nel_periodo(df["netto"]))
    # scarto delle altre allo 0,10% fuori dalle prime 50 per volume del lunedi'
    costo10 = b["costo"].copy()
    tasso = np.tile(b["costo"], (W.shape[0], 1))
    for w in range(W.shape[0]):
        rango = np.argsort(-ps["peso"][w], kind="stable")
        fuori = np.ones(W.shape[1], bool)
        fuori[rango[:50]] = False
        tasso[w, fuori] = TAKER + 0.001
    df = conto_con_tassi(W, ps["R"], ps["F"], tasso)
    df.index = ps["lunedi"]
    out["mercato, scarto 0,10% fuori dalle prime 50"] = numeri(nel_periodo(df["netto"]))
    out["costo_medio_per_unita_a_mercato"] = float((np.abs(D) * b["costo"][None, :])[sett].sum() / np.abs(D)[sett].sum())
    salva("costi", out)


def parte_conto():
    b = carica_base()
    H = carica_ore()
    pan, ps = b["pan"], b["ps"]
    out = {"filtri": "bot/portafoglio/filtri_conto_vero.json (6 novembre 2026)"}
    rif = simula_conto(b, H, 1e9, minimi=False)
    ricerca = te.conto(b["W"], ps["R"], ps["F"], b["costo"])
    ricerca.index = ps["lunedi"]
    x_r = nel_periodo(ricerca["netto"])
    out["controllo_simulatore"] = {"senza_minimi_capitale_fisso": numeri(rif["netto"]),
                                   "ricerca_composta": numeri(x_r),
                                   "nota": "capitale fisso: i rendimenti sono sul capitale di partenza, senza la deriva dei pesi verso il conto"}
    rif_c = simula_conto(b, H, 1e9, minimi=False, composto=True)
    out["controllo_simulatore"]["senza_minimi_composto"] = numeri(rif_c["netto"])
    out["controllo_simulatore"]["differenza_media_settimanale_composto_contro_ricerca"] = float(
        (rif_c["netto"] - x_r.reindex(rif_c.index)).abs().mean())
    serie = {"ricerca (mercato)": x_r, "senza minimi, fisso": rif["netto"]}
    simb = pan["simboli"]
    for cap in (200, 250, 280, 300, 500, 1000, 2000):
        for modo, oltre in (("mercato", 0.0), ("limite", 0.0), ("limite", 0.0005), ("limite", 0.001)):
            for libere in ((False, True) if cap in (280, 300, 1000) else (False,)):
                if modo == "limite" and cap not in (280, 300, 1000):
                    continue
                d = simula_conto(b, H, cap, modo_costi=modo, oltre=oltre, chiusure_libere=libere)
                nome = f"{cap} USDT, {modo}" + (f" oltre {100 * oltre:.2f}%" if modo == "limite" else "") + (", chiusure libere" if libere else "")
                at = d.attrs
                ma = at["mai_aperte"]
                out[nome] = numeri(d["netto"]) | {
                    "per_anno": per_anno(d["netto"]), "spese_annue": float(d["spese"].mean() * 52),
                    "funding_annuo_pagato": float(d["funding"].mean() * 52),
                    "esposizione_lorda_media": float(d["lorda"].mean()), "esposizione_netta_media": float(d["netta"].mean()),
                    "netta_min": float(d["netta"].min()), "netta_max": float(d["netta"].max()),
                    "ordini_voluti": at["ordini_voluti"], "saltati": at["saltati"],
                    "quota_saltati": at["saltati"] / max(1, at["ordini_voluti"]),
                    "sotto_valore_minimo": at["sotto_valore_minimo"], "sotto_un_passo": at["sotto_un_passo"],
                    "settimane_moneta_con_polvere": at["settimane_moneta_con_polvere"],
                    "monete_al_lunedi": float(d["monete"].mean()), "ordini_al_lunedi": float(d["ordini"].mean()),
                    "settimane_voluta_e_mai_aperta_prime": sorted(((simb[j], int(ma[j])) for j in np.flatnonzero(ma)), key=lambda kv: -kv[1])[:12],
                    "correlazione_con_la_ricerca": float(np.corrcoef(d["netto"], x_r.reindex(d.index))[0, 1])}
                serie[nome] = d["netto"]
                log(nome, f"Sharpe {out[nome]['sharpe']:.3f}", f"annuo {out[nome]['annuo']:+.3f}", f"saltati {out[nome]['quota_saltati']:.2f}")
    # il valore del conto che si compone (come il bot: obiettivo = peso x valore del conto)
    for cap in (280, 1000):
        d = simula_conto(b, H, cap, composto=True, modo_costi="limite", oltre=0.0005)
        out[f"{cap} USDT composto, limite oltre 0,05%"] = numeri(d["netto"]) | {"per_anno_composto": per_anno_composto(d["netto"]),
                                                                              "valore_finale": float(cap * np.prod(1 + d["netto"]))}
        serie[f"{cap} USDT composto, limite oltre 0,05%"] = d["netto"]
        # quando il conto passa i 600 USDT (VALORE_MASSIMO_PER_ORDINI = 2 x CAPITALE_MASSIMO): da li' niente ordini nuovi nel bot
        eq = cap * np.cumprod(1 + d["netto"].to_numpy())
        oltre600 = np.flatnonzero(eq > 600)
        out[f"{cap} USDT composto, limite oltre 0,05%"]["primo_lunedi_oltre_600"] = sc.data(int(d.index[oltre600[0]])) if len(oltre600) else None
    # partenza a conto vuoto in lunedi' diversi (una per trimestre): il primo anno dopo la partenza
    partenze = {}
    lun = ps["lunedi"]
    for g in lun[(lun >= INIZIO) & (lun <= sc.giorno(2025, 10, 6))][::13]:
        d = simula_conto(b, H, 280, modo_costi="limite", oltre=0.0005, inizio=int(g), fine=int(g) + 52 * 7)
        r = simula_conto(b, H, 1e9, minimi=False, modo_costi="limite", oltre=0.0005, inizio=int(g), fine=int(g) + 52 * 7)
        partenze[sc.data(int(g))] = {"280": float(d["netto"].sum()), "senza_minimi": float(r["netto"].sum()),
                                     "prima_settimana_spese_280": float(d["spese"].iloc[0])}
    out["partenze_a_conto_vuoto_un_anno"] = partenze
    # lo stesso conto fino al 19 ottobre 2026 (ultima settimana con il funding tutto vero): il 2026 a 280 USDT dipende da due settimane
    fino19 = {}
    for nome, cap, kw in (("ricerca", 1e9, {"minimi": False}), ("280 USDT, mercato", 280.0, {}),
                          ("280 USDT, limite oltre 0.00%", 280.0, {"modo_costi": "limite", "oltre": 0.0}),
                          ("280 USDT, limite oltre 0.05%", 280.0, {"modo_costi": "limite", "oltre": 0.0005}),
                          ("300 USDT, limite oltre 0.05%", 300.0, {"modo_costi": "limite", "oltre": 0.0005})):
        d = simula_conto(b, H, cap, fine=sc.giorno(2026, 10, 19), **kw)
        x = pd.Series(d["netto"].to_numpy(), index=d.index)
        fino19[nome] = {"settimane": int(len(x)), "sharpe": numeri(x)["sharpe"], "2026_l_anno": per_anno(x)[2026],
                        "2026_composto": per_anno_composto(x)[2026]}
    out["fino_al_19_ottobre"] = fino19
    pd.DataFrame(serie).to_pickle(CACHE / "serie_conto.pkl")
    salva("conto", out)


# ---------------------------------------------------------------------------
# B. tempi: entrata alle 01:00 e alle 02:00, una settimana di ritardo
# ---------------------------------------------------------------------------

def parte_tempi():
    b = carica_base()
    H = carica_ore()
    pan, ps, W = b["pan"], b["ps"], b["W"]
    S = W.shape[1]
    out = {}
    for ora in ("O01", "O02", "O04"):
        P = H[ora]
        with np.errstate(invalid="ignore", divide="ignore"):
            R1 = np.vstack([P[1:] / P[:-1] - 1, np.full((1, S), np.nan)])
        mancano = ~np.isfinite(R1) & (W != 0)
        R = np.where(np.isfinite(R1), R1, ps["R"])
        df = te.conto(W, R, ps["F"], b["costo"])
        df.index = ps["lunedi"]
        sett = (ps["lunedi"] >= INIZIO) & (ps["lunedi"] <= FINE_MAZZO)
        out[f"entrata alle {ora[1:]}:00"] = numeri(nel_periodo(df["netto"])) | {
            "coppie_tenute_senza_ora_(rendimento_del_giorno)": int((mancano & sett[:, None]).sum())}
    base = te.conto(W, ps["R"], ps["F"], b["costo"])
    base.index = ps["lunedi"]
    out["entrata alle 00:00 (ricerca)"] = numeri(nel_periodo(base["netto"]))
    # una settimana di ritardo: i pesi del lunedi' prima (un lunedi' saltato dal conto, problema 181 della revisione)
    W1 = np.vstack([np.zeros((1, S)), W[:-1]])
    df = te.conto(W1, ps["R"], ps["F"], b["costo"])
    df.index = ps["lunedi"]
    out["pesi di una settimana prima"] = numeri(nel_periodo(df["netto"]))
    # un lunedi' su 4 saltato (i pesi restano quelli della settimana prima)
    Wk = W.copy()
    for w in range(1, W.shape[0]):
        if w % 4 == 0:
            Wk[w] = Wk[w - 1]
    df = te.conto(Wk, ps["R"], ps["F"], b["costo"])
    df.index = ps["lunedi"]
    out["un lunedi' su 4 saltato"] = numeri(nel_periodo(df["netto"]))
    salva("tempi", out)


# ---------------------------------------------------------------------------
# C. rischio: giorno peggiore, limite prudente nel giorno, pesi con la deriva, distanza dalla liquidazione
# ---------------------------------------------------------------------------

def percorso_giornaliero(b, valori: dict, capitale: float) -> pd.DataFrame:
    """Il valore del conto giorno per giorno dalle posizioni del lunedi' (``valori`` = {lunedi': (valori USDT, valore del conto, spese)}):
    le posizioni derivano con il prezzo nella settimana; ogni giorno il rendimento da apertura ad apertura e il funding del giorno; il
    limite prudente nel giorno mette tutti i long al minimo e tutti gli short al massimo. Il valore del lunedi' e' quello del simulatore
    (capitale piu' i netti delle settimane prima)."""
    pan = b["pan"]
    t0 = pan["t0"]
    O, Hh, Ll = pan["open"], pan["high"], pan["low"]
    r = sc.rendimenti(pan)
    F = pan["funding"]
    righe = []
    for g, (v0, E0, spese) in sorted(valori.items()):
        m = g - t0
        v = v0.copy()
        E = E0 - spese
        for d in range(7):
            t = m + d
            with np.errstate(invalid="ignore", divide="ignore"):
                giu = np.where(v > 0, Ll[t] / O[t] - 1, 0.0) + np.where(v < 0, Hh[t] / O[t] - 1, 0.0)
            peggio = E + float((v * np.nan_to_num(giu)).sum())
            pnl = float((v * r[t]).sum() - (v * F[t]).sum())
            E = E + pnl
            righe.append({"giorno": g + d, "valore": E, "peggio_nel_giorno": peggio})
            v = v * (1 + r[t])
    return pd.DataFrame(righe).set_index("giorno")


def stop_sul_conto(p: pd.DataFrame, capitale: float, stop: float = 0.35, pavimento: float = 0.65) -> dict:
    """Il primo giorno in cui lo stop del conto vero (`conto_vero.STOP_CONTO`, `PAVIMENTO_RIPARTI`) sarebbe scattato: valore sotto il piu'
    alto fra il 65% del massimo e il 65% del capitale di partenza; con il valore di fine giorno e con il limite prudente nel giorno."""
    picco = p["valore"].cummax().shift(1).fillna(capitale).clip(lower=capitale)
    livello = np.maximum((1 - stop) * picco, pavimento * capitale)
    out = {}
    for col in ("valore", "peggio_nel_giorno"):
        sotto = p[col] < livello
        out[col] = sc.data(int(p.index[np.argmax(sotto.to_numpy())])) if sotto.any() else None
    dd = p["valore"] / p["valore"].cummax() - 1
    out["discesa_massima_giornaliera"] = float(dd.min())
    out["giorno_della_discesa_massima"] = sc.data(int(dd.idxmin()))
    out["discesa_massima_con_il_peggio_nel_giorno"] = float((p["peggio_nel_giorno"] / p["valore"].cummax().shift(1).fillna(capitale) - 1).min())
    return out


def parte_rischio():
    b = carica_base()
    pan, ps, W = b["pan"], b["ps"], b["W"]
    t0 = pan["t0"]
    O, Hh, Ll, C = pan["open"], pan["high"], pan["low"], pan["close"]
    r = sc.rendimenti(pan)
    F = pan["funding"]
    lun = ps["lunedi"]
    sett = np.flatnonzero((lun >= INIZIO) & (lun <= FINE_MAZZO))
    giorni, peggio_giorno, peggio_dentro = [], [], []
    peso_max = []
    for w in sett:
        m = lun[w] - t0
        v = W[w].copy()                              # valore delle posizioni in frazione del conto del lunedi'
        E = 1.0
        for d in range(7):
            t = m + d
            o = O[t]
            with np.errstate(invalid="ignore", divide="ignore"):
                giu = np.where(v > 0, Ll[t] / o - 1, 0.0) + np.where(v < 0, Hh[t] / o - 1, 0.0)
            giu = np.nan_to_num(giu)
            pnl = float((v * r[t]).sum() - (v * F[t]).sum())
            dentro = float((v * giu).sum())          # longs al minimo e shorts al massimo, tutti insieme
            giorni.append(t + t0)
            peggio_giorno.append(pnl / E)
            peggio_dentro.append(dentro / E)
            peso_max.append(float(np.abs(v).max() / E))
            v = v * (1 + r[t])
            E = E + pnl
    g = pd.Series(peggio_giorno, index=giorni)
    dentro = pd.Series(peggio_dentro, index=giorni)
    pm = pd.Series(peso_max, index=giorni)
    W_s = W[sett]
    out = {"giorno_peggiore": {"valore": float(g.min()), "giorno": sc.data(int(g.idxmin()))},
           "giorni_sotto_-5%": int((g < -0.05).sum()), "giorni_sotto_-10%": int((g < -0.10).sum()),
           "limite_prudente_nel_giorno": {"valore": float(dentro.min()), "giorno": sc.data(int(dentro.idxmin()))},
           "peggiori_5_limite_prudente": {sc.data(int(i)): round(float(v), 4) for i, v in dentro.nsmallest(5).items()},
           "peso_massimo_al_lunedi": float(np.abs(W_s).max()),
           "lunedi_oltre_0,60": int((np.abs(W_s).max(axis=1) > 0.60).sum()),
           "lunedi_somma_oltre_2": int((np.abs(W_s).sum(axis=1) > 2.0 + 1e-9).sum()),
           "peso_massimo_con_la_deriva": {"valore": float(pm.max()), "giorno": sc.data(int(pm.idxmax()))},
           "giorni_con_una_moneta_oltre_0,30": int((pm > 0.30).sum()),
           "lunedi_con_meno_di_10_per_lato": int((((W_s > 0).sum(axis=1) < 10) | ((W_s < 0).sum(axis=1) < 10)).sum())}
    # la moneta piu' pesante e quante volte
    j_max = np.unravel_index(np.argmax(np.abs(W_s)), W_s.shape)
    out["moneta_piu_pesante"] = {"simbolo": pan["simboli"][j_max[1]], "lunedi": sc.data(int(lun[sett][j_max[0]])),
                                 "peso": float(W_s[j_max])}
    # settimana peggiore e discesa in USDT con 280
    df = te.conto(W, ps["R"], ps["F"], b["costo"])
    df.index = lun
    x = nel_periodo(df["netto"])
    eq = np.cumprod(1 + x.to_numpy())
    out["settimana_peggiore"] = {"valore": float(x.min()), "lunedi": sc.data(int(x.idxmin()))}
    out["discesa_massima_in_USDT_con_280"] = float(280 * (eq / np.maximum.accumulate(eq) - 1).min())
    # lo stop sul conto (-35% dal massimo o sotto il 65% del capitale) sul percorso giornaliero, con il capitale che si compone
    H = carica_ore()
    for nome, cap, kw in (("ricerca, senza minimi", 1e9, {"minimi": False}),
                          ("280 USDT, limite oltre 0,05%", 280.0, {"modo_costi": "limite", "oltre": 0.0005}),
                          ("280 USDT, a mercato", 280.0, {}),
                          ("280 USDT, chiusure libere, limite oltre 0,05%", 280.0, {"modo_costi": "limite", "oltre": 0.0005, "chiusure_libere": True}),
                          ("1000 USDT, limite oltre 0,05%", 1000.0, {"modo_costi": "limite", "oltre": 0.0005})):
        d = simula_conto(b, H, cap, composto=True, registra=True, fine=int(lun[-1]), **kw)
        p = percorso_giornaliero(b, d.attrs["valori"], cap)
        s = stop_sul_conto(p, cap)
        s["settimana_peggiore"] = float(d["netto"].min())
        s["fino_al"] = sc.data(int(p.index[-1]))
        # lo stesso con la partenza in ogni trimestre (lo stop dipende da quando si parte)
        partenze = {}
        for g in lun[(lun >= INIZIO) & (lun <= sc.giorno(2026, 1, 5))][::13]:
            d2 = simula_conto(b, H, cap, composto=True, registra=True, inizio=int(g), fine=int(lun[-1]), **kw)
            s2 = stop_sul_conto(percorso_giornaliero(b, d2.attrs["valori"], cap), cap)
            partenze[sc.data(int(g))] = {"stop_fine_giorno": s2["valore"], "stop_nel_giorno": s2["peggio_nel_giorno"],
                                        "discesa_giornaliera": round(s2["discesa_massima_giornaliera"], 4)}
        s["partenze_ogni_trimestre"] = partenze
        s["partenze_con_lo_stop_nel_giorno"] = sum(1 for v in partenze.values() if v["stop_nel_giorno"])
        s["partenze"] = len(partenze)
        out[f"stop: {nome}"] = s
        log(nome, s["valore"], s["peggio_nel_giorno"], round(s["discesa_massima_giornaliera"], 3), s["partenze_con_lo_stop_nel_giorno"], len(partenze))
    # liquidazione: margine unico (CROSSED), leva 5, esposizione lorda 2 volte il conto; mantenimento del primo scaglione di
    # Binance fra lo 0,4% e il 2,5% del nozionale (da verificare per ogni moneta): il conto si liquida solo se perde circa il
    # 95-99% del suo valore; lo stop sul conto chiude a -35% dal massimo (controllo ogni minuto)
    out["liquidazione"] = {"margine": "CROSSED (demo_binance._margine_unico)", "leva": 5, "esposizione_lorda": 2.0,
                           "mantenimento_ipotesi": [0.004, 0.025],
                           "perdita_che_liquida_ipotesi": [1 - 2 * 0.025, 1 - 2 * 0.004],
                           "perdita_peggiore_prudente_nel_giorno": float(dentro.min())}
    salva("rischio", out)


# ---------------------------------------------------------------------------
# D. misure: concentrazione, anni, climi, operazioni
# ---------------------------------------------------------------------------

def clima(ps, pan):
    """Il clima di ogni settimana dal rendimento del Bitcoin dei 91 giorni prima del lunedi' (chiusura della domenica su quella di 91
    giorni prima): sopra +15% rialzo, sotto -15% ribasso, altrimenti laterale. Definizione scritta qui prima del calcolo."""
    j = pan["simboli"].index("BTCUSDT")
    C = pan["close"][:, j]
    lun = ps["lunedi"] - pan["t0"]
    with np.errstate(invalid="ignore", divide="ignore"):
        r = C[lun - 1] / C[lun - 92] - 1
    return pd.Series(np.where(r > 0.15, "rialzo", np.where(r < -0.15, "ribasso", "laterale")), index=ps["lunedi"])


def misure_di(x: pd.Series, ps, pan) -> dict:
    tot = float(x.sum())
    top5 = float(x.nlargest(5).sum())
    mesi = x.groupby(pd.to_datetime(x.index.to_numpy() * 86400, unit="s").to_period("M")).sum()
    top3m = float(mesi.nlargest(3).sum())
    cl = clima(ps, pan).reindex(x.index)
    climi = {}
    for c in ("rialzo", "laterale", "ribasso"):
        y = x[cl == c]
        climi[c] = {"settimane": int(len(y)), "annuo": float(y.mean() * 52) if len(y) else None,
                    "sharpe": float(y.mean() / y.std(ddof=1) * math.sqrt(52)) if len(y) > 2 and y.std(ddof=1) > 0 else None}
    return {"somma_dei_rendimenti": tot, "quota_5_settimane_migliori": top5 / tot, "quota_3_mesi_migliori": top3m / tot,
            "5_settimane_migliori": {sc.data(int(i)): round(float(v), 4) for i, v in x.nlargest(5).items()},
            "3_mesi_migliori": {str(k): round(float(v), 4) for k, v in mesi.nlargest(3).items()},
            "mesi_negativi": int((mesi < 0).sum()), "mesi": int(len(mesi)), "climi": climi,
            "per_anno": per_anno(x), "per_anno_composto": per_anno_composto(x)}


def operazioni(W, R, F, costo, lun):
    """Le operazioni (una moneta da quando entra in un lato a quando esce): rendimento lordo piu' funding contro le spese di entrata e
    uscita, in frazione del conto (pesi che derivano come in `terza.conto`, capitale che si compone ignorato)."""
    S = W.shape[1]
    R0 = np.nan_to_num(R)
    ops = []
    aperta = {}
    sett = (lun >= INIZIO) & (lun <= FINE_MAZZO)
    for w in range(W.shape[0]):
        for j in np.flatnonzero((W[w] != 0) | np.isin(np.arange(S), list(aperta))):
            segno = np.sign(W[w, j])
            if j in aperta and (segno == 0 or segno != aperta[j]["segno"]):
                a = aperta.pop(j)
                a["spese"] += abs(a["ultimo"]) * costo[j]
                ops.append(a)
            if segno != 0:
                if j not in aperta:
                    aperta[j] = {"j": j, "segno": segno, "da": int(lun[w]), "lordo": 0.0, "funding": 0.0, "spese": abs(W[w, j]) * costo[j],
                                 "settimane": 0, "nel_periodo": bool(sett[w])}
                a = aperta[j]
                a["lordo"] += W[w, j] * R0[w]
                a["funding"] += W[w, j] * F[w, j]
                a["settimane"] += 1
                a["ultimo"] = W[w, j] * (1 + R0[w])
    ops = [o for o in ops if o["nel_periodo"]]
    netto = np.array([o["lordo"] - o["funding"] - o["spese"] for o in ops])
    lordo = np.array([o["lordo"] - o["funding"] for o in ops])
    spese = np.array([o["spese"] for o in ops])
    vinc = netto[netto > 0].sum()
    perd = -netto[netto < 0].sum()
    return {"operazioni": int(len(ops)), "settimane_medie": float(np.mean([o["settimane"] for o in ops])),
            "media_netta": float(netto.mean()), "media_prima_delle_spese": float(lordo.mean()), "spesa_media": float(spese.mean()),
            "profit_factor": float(vinc / perd) if perd > 0 else None, "vincenti": float((netto > 0).mean())}


def parte_misure():
    b = carica_base()
    pan, ps, W = b["pan"], b["ps"], b["W"]
    df = b["df"]
    x = nel_periodo(df["netto"])
    out = {"ricerca (mercato)": numeri(x) | misure_di(x, ps, pan)}
    out["ricerca: esposizione"] = {"settimane_con_posizioni": int((nel_periodo(df["monete"]) > 0).sum()),
                                   "monete_medie": float(nel_periodo(df["monete"]).mean()),
                                   "giro_medio": float(nel_periodo(df["giro"]).mean()),
                                   "spese_medie_settimana": float(nel_periodo(df["spese"]).mean()),
                                   "netto_medio_settimana": float(x.mean())}
    out["ricerca: operazioni"] = operazioni(W, ps["R"], ps["F"], b["costo"], ps["lunedi"])
    f = CACHE / "serie_conto.pkl"
    if f.exists():
        serie = pd.read_pickle(f)
        for nome in ("280 USDT, limite oltre 0.05%", "1000 USDT, limite oltre 0.05%", "280 USDT, mercato", "1000 USDT, mercato"):
            if nome in serie:
                y = serie[nome].dropna()
                out[nome] = numeri(y) | misure_di(y, ps, pan)
    # BTC sulle stesse settimane, per capire
    btc = pd.Series(ps["R"][:, pan["simboli"].index("BTCUSDT")], index=ps["lunedi"])
    out["BTC comprato e tenuto, stesse settimane"] = numeri(nel_periodo(btc))
    out["correlazione_con_BTC"] = float(np.corrcoef(x, nel_periodo(btc))[0, 1])
    salva("misure", out)


# ---------------------------------------------------------------------------
# E. sensibilita' dei parametri (±10% e ±20%)
# ---------------------------------------------------------------------------

def parte_sensi():
    b = carica_base()
    pan, ps = b["pan"], b["ps"]
    out = {}
    def fai(nome, **kw):
        W, ps2 = f5(pan, ps=ps, **kw)
        costo = sc.costi_moneta(ps2["simboli"])
        df = te.conto(W, ps2["R"], ps2["F"], costo)
        df.index = ps2["lunedi"]
        x = nel_periodo(df["netto"])
        out[nome] = {k: v for k, v in numeri(x).items() if k in ("sharpe", "annuo", "discesa_max", "t")} | {
            "anni_negativi": [a for a, v in per_anno(x).items() if v <= 0], "spese_annue": float(nel_periodo(df["spese"]).mean() * 52)}
        log(nome, round(out[nome]["sharpe"], 3))
    fai("F5 (20/40, 7 giorni, 30 giorni, 100 monete)")
    for e_ in (0.16, 0.18, 0.22, 0.24):
        fai(f"entrata {e_:.2f}", entra=e_)
    for r_ in (0.32, 0.36, 0.44, 0.48):
        fai(f"uscita {r_:.2f}", resta=r_)
    for e_, r_ in ((0.16, 0.32), (0.18, 0.36), (0.22, 0.44), (0.24, 0.48)):
        fai(f"entrata {e_:.2f} e uscita {r_:.2f}", entra=e_, resta=r_)
    for g in (5, 6, 8, 9):
        fai(f"funding di {g} giorni", giorni_f=g)
    for g in (24, 27, 33, 36):
        fai(f"volatilita' di {g} giorni", giorni_s=g)
    for n in (80, 90, 110, 120):
        fai(f"universo {n} monete", n_uni=n)
    salva("sensi", out)


# ---------------------------------------------------------------------------
# E. probabilita' che non sia fortuna (Sharpe corretto), con N alla scelta e con N di oggi; t con le settimane legate
# ---------------------------------------------------------------------------

def t_newey_west(x: np.ndarray, ritardi: int) -> float:
    x = np.asarray(x, float)
    n = len(x)
    m = x.mean()
    e = x - m
    g0 = (e @ e) / n
    s = g0
    for k in range(1, ritardi + 1):
        gk = (e[k:] @ e[:-k]) / n
        s += 2 * (1 - k / (ritardi + 1)) * gk
    return float(m / math.sqrt(s / n)) if s > 0 else float("nan")


def parte_corretto():
    from research.programma6 import asticella as ast
    from scipy import stats
    b = carica_base()
    df = b["df"]
    cands = {}
    x = ast.periodo(df["netto"])
    cands["F5 ricerca a mercato (oggi)"] = x
    f = CACHE / "serie_conto.pkl"
    if f.exists():
        serie = pd.read_pickle(f)
        for nome in ("280 USDT, mercato", "280 USDT, limite oltre 0.00%", "280 USDT, limite oltre 0.05%", "280 USDT, limite oltre 0.10%",
                     "280 USDT, mercato, chiusure libere", "280 USDT, limite oltre 0.05%, chiusure libere",
                     "300 USDT, mercato", "300 USDT, limite oltre 0.00%", "300 USDT, limite oltre 0.05%", "300 USDT, limite oltre 0.10%",
                     "1000 USDT, limite oltre 0.00%", "1000 USDT, limite oltre 0.05%", "1000 USDT, limite oltre 0.10%", "1000 USDT, mercato"):
            if nome in serie:
                cands[nome] = ast.periodo(serie[nome].dropna())
    vecchia = pd.read_csv(RADICE / "research/programma6/risultati_ventiquattresima/settimane_F5.csv.gz", index_col=0)["netto"]
    cands["F5 della prova 24 (prima delle parita')"] = ast.periodo(vecchia)
    def dsr(i, sr_v, N):
        return te.sharpe_corretto(i["sharpe"], i["settimane"], i["asimmetria"], i["curtosi"], sr_v, 52, n_prove=N)
    def numeri_k(s):
        nn = numeri(s)
        return {k: nn[k] for k in ("sharpe", "settimane", "asimmetria", "curtosi")}
    prove = ast.le_prove()
    nuove = ast.serie_nuove()
    out = {"candidate": {n: numeri_k(s) | {"t": numeri(s)["t"], "t_newey_west_4": t_newey_west(s.to_numpy(), 4),
                                           "t_newey_west_13": t_newey_west(s.to_numpy(), 13),
                                           "autocorrelazione_1": float(s.autocorr(1)), "autocorrelazione_2": float(s.autocorr(2))}
                         for n, s in cands.items()}}
    def num(nome):
        t = nome.split()[0]
        t = "2" if t.startswith("2") and not t[1:].isdigit() else t
        try:
            return int(t)
        except ValueError:
            return 10 ** 6
    scenari = {}
    for etichetta, fino in (("fino alla prova 24 (F5 scelta per il paper)", 24), ("fino alla prova 56 (F9: il paper passa agli ordini limite)", 56),
                            ("mazzo di oggi (tutte le prove)", None)):
        if fino is None:
            serie, soli = ast.mazzo()
        else:
            serie = {n: ast.periodo(s) for n, s, _ in prove if s is not None and num(n) <= fino}
            serie.update({n: ast.periodo(s) for n, s in nuove.items() if num(n) <= fino})
            soli = [sr for n, s, sr in prove if s is None and num(n) <= fino]
        for taglio in (0.5, 0.3, 0.7):
            gr = ast.gruppi(serie, taglio)
            sr_g, sr_v = ast.per_v(gr, soli, False), ast.per_v(gr, soli, True)
            N = len(sr_g)
            ris = {"serie": len(serie), "senza_serie": len(soli), "famiglie": N, "in_V": len(sr_v),
                   "deviazione_V_annua": float(np.std(sr_v, ddof=1)), "deviazione_tutti_annua": float(np.std(sr_g, ddof=1))}
            for n, s in cands.items():
                i = numeri_k(s)
                ris[n] = {"con_l_aggiunta": dsr(i, sr_v, N), "senza_l_aggiunta": dsr(i, sr_g, N)}
            scenari[f"{etichetta}, taglio {taglio}"] = ris
            log(etichetta, taglio, N, {n: round(v["con_l_aggiunta"], 3) for n, v in ris.items() if isinstance(v, dict)})
    out["scenari"] = scenari
    # il gruppo di F5 nel mazzo di oggi
    serie, soli = ast.mazzo()
    gr = ast.gruppi(serie, 0.5)
    out["gruppo_di_F5_oggi"] = next((g["membri"] for g in gr if "24 F5" in g["membri"]), None)
    salva("corretto", out)


def parte_orario():
    """Lo stop sul conto con le candele da 1 ora: nelle settimane in cui il limite prudente del giorno passa il livello dello stop, il
    valore del conto ora per ora (chiusure orarie) e il limite prudente dell'ora (long al minimo e short al massimo della stessa ora).
    Il massimo del conto si aggiorna ogni ora (come `valuta` del bot). Prezzi scambiati, non il mark: per lo stop vale il mark, che ha
    meno picchi (KNOWN_PITFALLS 41), quindi e' un limite prudente."""
    from research.programma6 import quarta as qa
    b = carica_base()
    H = carica_ore()
    pan = b["pan"]
    t0 = pan["t0"]
    simb = pan["simboli"]
    lun = b["ps"]["lunedi"]
    ore_cache = {}

    def ore(j):
        if j not in ore_cache:
            ore_cache[j] = qa.ore(simb[j])
        return ore_cache[j]

    out = {}
    for nome, cap, kw in (("ricerca, senza minimi", 1e9, {"minimi": False}),
                          ("280 USDT, limite oltre 0,05%", 280.0, {"modo_costi": "limite", "oltre": 0.0005}),
                          ("1000 USDT, limite oltre 0,05%", 1000.0, {"modo_costi": "limite", "oltre": 0.0005})):
        risultati = {}
        partenze = [int(g) for g in lun[(lun >= INIZIO) & (lun <= sc.giorno(2026, 1, 5))][::13]]
        for g0 in partenze:
            d = simula_conto(b, H, cap, composto=True, registra=True, inizio=g0, fine=int(lun[-1]), **kw)
            val = d.attrs["valori"]
            p = percorso_giornaliero(b, val, cap)
            picco_g = p["valore"].cummax().shift(1).fillna(cap).clip(lower=cap)
            livello_g = np.maximum(0.65 * picco_g, 0.65 * cap)
            settimane = sorted({int(lun[np.searchsorted(lun, gg, side="right") - 1]) for gg in p.index[p["peggio_nel_giorno"] < livello_g]})
            primo_chiusura, primo_ora, peggio = None, None, 0.0
            picco = cap
            # il massimo del conto prima di ogni settimana dal percorso giornaliero (fine giorno), poi ora per ora nella settimana
            for gw in settimane:
                v0, E0, spese = val[gw]
                prima = p.loc[p.index < gw, "valore"]
                picco = max(cap, float(prima.max()) if len(prima) else cap)
                held = np.flatnonzero(v0 != 0)
                ore_sett = np.arange(gw * 24, gw * 24 + 168)
                Cm = np.full((168, len(held)), np.nan)
                Hm, Lm = Cm.copy(), Cm.copy()
                O0 = np.array([pan["open"][gw - t0, j] for j in held])
                for k, j in enumerate(held):
                    z = ore(j)
                    if z.empty:
                        continue
                    zz = z.reindex(ore_sett)
                    Cm[:, k], Hm[:, k], Lm[:, k] = zz["close"].to_numpy(), zz["high"].to_numpy(), zz["low"].to_numpy()
                # ore mancanti: l'ultimo prezzo noto (prima ora: l'apertura del lunedi')
                for M in (Cm, Hm, Lm):
                    df_ = pd.DataFrame(M).ffill()
                    M[:] = df_.fillna(pd.Series(O0)).to_numpy()
                v = v0[held]
                E = E0 - spese
                for h in range(168):
                    chius = E + float((v * (Cm[h] / O0 - 1)).sum())
                    estremo = np.where(v > 0, Lm[h], Hm[h])
                    dentro = E + float((v * (estremo / O0 - 1)).sum())
                    liv = max(0.65 * picco, 0.65 * cap)
                    peggio = min(peggio, dentro / picco - 1)
                    if primo_chiusura is None and chius < liv:
                        primo_chiusura = time.strftime("%Y-%m-%d %H:00", time.gmtime((gw * 24 + h) * 3600))
                    if primo_ora is None and dentro < liv:
                        primo_ora = time.strftime("%Y-%m-%d %H:00", time.gmtime((gw * 24 + h) * 3600))
                    picco = max(picco, chius)
                if primo_chiusura and primo_ora:
                    break
            risultati[sc.data(g0)] = {"settimane_controllate": len(settimane), "stop_alla_chiusura_oraria": primo_chiusura,
                                      "stop_con_il_limite_prudente_dell_ora": primo_ora, "peggio_dal_massimo_nell_ora": round(peggio, 4)}
            log(nome, sc.data(g0), len(settimane), primo_chiusura, primo_ora, round(peggio, 3))
        out[nome] = {"partenze": risultati,
                     "partenze_con_stop_alla_chiusura_oraria": sum(1 for v in risultati.values() if v["stop_alla_chiusura_oraria"]),
                     "partenze_con_stop_nel_limite_prudente_dell_ora": sum(1 for v in risultati.values() if v["stop_con_il_limite_prudente_dell_ora"]),
                     "partenze_totali": len(risultati)}
    salva("orario", out)


def parte_polvere():
    """Le posizioni sotto il valore minimo che il bot non chiude (`demo_binance.ordini_del_giorno`, chiusure comprese): a 280 USDT a
    capitale fisso, la differenza dalla ricerca per anno scomposta in monete mai aperte, polvere (tenute e non volute) e taglia; i casi
    peggiori del 2026; la discesa di un conto partito il 29 settembre 2025 (si compone, limite oltre 0,05%), con e senza chiusure libere."""
    b = carica_base()
    H = carica_ore()
    pan, ps, W = b["pan"], b["ps"], b["W"]
    simb = pan["simboli"]
    lun = ps["lunedi"]
    t0 = pan["t0"]
    vmin, passo, qmin, _ = carica_filtri(simb)
    sett = np.flatnonzero((lun >= INIZIO) & (lun <= FINE_MAZZO))
    O = pan["open"][lun - t0]
    R = np.nan_to_num(ps["R"])
    F = ps["F"]
    cap = 280.0
    q = np.zeros(len(simb))
    righe, casi = [], []
    for w in sett:
        p = O[w]
        vivo = np.isfinite(p) & (p > 0)
        q[(q != 0) & ~vivo] = 0.0
        obi = np.where(vivo, W[w] * cap / np.where(vivo, p, 1.0), 0.0)
        delta = obi - q
        da_fare = vivo & (np.abs(delta * np.nan_to_num(p)) > 1e-9)
        qr = np.where(passo > 0, np.floor(np.abs(delta) / np.where(passo > 0, passo, 1.0) + 1e-9) * passo, np.abs(delta))
        ok = (qr > 0) & (qr >= qmin - 1e-12) & (qr * np.nan_to_num(p) >= vmin - 1e-9)
        q = q + np.where(da_fare & ok, np.sign(delta) * qr, 0.0)
        q = np.where(passo > 0, np.round(q / np.where(passo > 0, passo, 1.0)) * passo, q)
        q = np.where(np.abs(q * np.nan_to_num(p)) < 1e-9, 0.0, q)
        v = np.where(vivo, q * np.nan_to_num(p), 0.0) / cap
        x = W[w]
        diff = (v - x) * R[w] - (v - x) * F[w]
        mai, polv = (x != 0) & (v == 0), (x == 0) & (v != 0)
        righe.append({"lunedi": int(lun[w]), "mai_aperte": float(diff[mai].sum()), "polvere": float(diff[polv].sum()),
                      "taglia": float(diff[~mai & ~polv].sum()), "polvere_corte": int((polv & (v < 0)).sum()),
                      "polvere_lunghe": int((polv & (v > 0)).sum())})
        if lun[w] >= sc.giorno(2026, 1, 1):
            for j in np.flatnonzero(polv):
                casi.append({"cosa": "polvere", "lunedi": sc.data(int(lun[w])), "moneta": simb[j], "valore_usdt": round(float(v[j] * cap), 2),
                             "rendimento_settimana": round(float(R[w, j]), 3), "punti_del_capitale": round(float(100 * (v[j] * R[w, j] - v[j] * F[w, j])), 2)})
    df = pd.DataFrame(righe).set_index("lunedi")
    anni = pd.to_datetime(df.index.to_numpy() * 86400, unit="s").year
    out = {"differenza_dalla_ricerca_per_anno_in_punti": (df.groupby(anni)[["mai_aperte", "polvere", "taglia"]].sum() * 100).round(2).to_dict(orient="index"),
           "polvere_media_per_lunedi": {"corte": float(df["polvere_corte"].mean()), "lunghe": float(df["polvere_lunghe"].mean())},
           "casi_peggiori_della_polvere_nel_2026": sorted(casi, key=lambda c: c["punti_del_capitale"])[:6]}
    j = simb.index("TUTUSDT")
    out["TUT_nella_settimana_del_3_agosto_2026"] = {sc.data(g): [round(float(pan[k][g - t0, j]), 5) for k in ("open", "high", "low", "close")]
                                                   + [round(float(pan["quote_volume"][g - t0, j]) / 1e6, 1)]
                                                   for g in range(sc.giorno(2026, 8, 3), sc.giorno(2026, 8, 11))}
    for nome, kw in (("bot (chiusure sotto il minimo saltate)", {}), ("chiusure libere", {"chiusure_libere": True}),
                     ("senza minimi", {"minimi": False})):
        c = 1e9 if nome == "senza minimi" else 280.0
        d = simula_conto(b, H, c, composto=True, registra=True, inizio=sc.giorno(2025, 9, 29), fine=int(lun[-1]),
                         modo_costi="limite", oltre=0.0005, **kw)
        pth = percorso_giornaliero(b, d.attrs["valori"], c)
        v = pd.Series(pth["valore"].to_numpy() / c, index=pth.index)
        pk = v.cummax()
        dd = v / pk - 1
        i = int(dd.idxmin())
        w = pd.Series(d["netto"].to_numpy(), index=d.index)
        out[f"partenza 29 settembre 2025, {nome}"] = {
            "massimo": round(float(pk.loc[i]), 4), "giorno_del_massimo": sc.data(int(v.loc[:i].idxmax())), "minimo": round(float(v.loc[i]), 4),
            "giorno_del_minimo": sc.data(i), "discesa": round(float(dd.min()), 4), "valore_finale": round(float(v.iloc[-1]), 4),
            "fino_al": sc.data(int(v.index[-1])), "settimane_peggiori": {sc.data(int(k)): round(float(x), 4) for k, x in w.nsmallest(4).items()}}
    salva("polvere", out)


def parte_avanti():
    """Il paper di F5 del bot (dal log della macchina: `ops/results/0674`, `0689`, `0727`, `0745`, `0768`, equity dopo il ribilancio piu'
    il costo) contro la ricerca sulle stesse settimane (funding di novembre stimato nel pannello); il funding sulla posizione che deriva
    nella settimana; i lunedi' con meno di 10 monete in un lato."""
    b = carica_base()
    pan, ps, W, df = b["pan"], b["ps"], b["W"], b["df"]
    log_bot = {"2026-10-26": (9996.00, 4.00), "2026-11-02": (9852.92, 2.38), "2026-11-09": (10106.54, 2.50),
               "2026-11-16": (10584.77, 2.42), "2026-11-23": (10558.39, 1.35)}
    date = list(log_bot)
    out = {"settimane": {}}
    for a, z in zip(date[:-1], date[1:]):
        r_bot = (log_bot[z][0] + log_bot[z][1]) / log_bot[a][0] - 1
        g = sc.giorno(*map(int, a.split("-")))
        out["settimane"][a] = {"paper_del_bot": round(r_bot, 5), "ricerca": round(float(df.loc[g, "netto"]), 5),
                               "funding_della_ricerca_(stimato)": round(float(-df.loc[g, "funding"]), 5)}
    out["totale_paper"] = float(np.prod([1 + v["paper_del_bot"] for v in out["settimane"].values()]) - 1)
    out["totale_ricerca"] = float(np.prod([1 + v["ricerca"] for v in out["settimane"].values()]) - 1)
    r = sc.rendimenti(pan)
    F = pan["funding"]
    t0 = pan["t0"]
    lun = ps["lunedi"]
    sett = np.flatnonzero((lun >= INIZIO) & (lun <= FINE_MAZZO))
    fd, fw = [], []
    for w in sett:
        m = lun[w] - t0
        v = W[w].copy()
        tot = 0.0
        for d in range(7):
            tot += float((v * F[m + d]).sum())
            v = v * (1 + r[m + d])
        fd.append(tot)
        fw.append(float((W[w] * ps["F"][w]).sum()))
    fd, fw = np.array(fd), np.array(fw)
    x = nel_periodo(df["netto"])
    out["funding_annuo_sul_peso_del_lunedi"] = float(-fw.mean() * 52)
    out["funding_annuo_sulla_posizione_che_deriva"] = float(-fd.mean() * 52)
    out["sharpe_con_il_funding_sulla_posizione_che_deriva"] = numeri(pd.Series(x.to_numpy() + fw - fd, index=x.index))["sharpe"]
    Ws = W[sett]
    out["lunedi_con_meno_di_10_monete_in_un_lato"] = [
        {"lunedi": sc.data(int(lun[sett][k])), "long": int((Ws[k] > 0).sum()), "short": int((Ws[k] < 0).sum()),
         "peso_massimo": round(float(np.abs(Ws[k]).max()), 3)} for k in range(len(sett)) if (Ws[k] > 0).sum() < 10 or (Ws[k] < 0).sum() < 10]
    salva("avanti", out)


def parte_buchi():
    """I giorni senza candela fra la prima e l'ultima di ogni moneta nel 2022 e nel 2023 (26-28 febbraio e 1-2 aprile 2022, 1-5 febbraio
    2023) presi dall'interfaccia pubblica di Binance (`www.binance.com/fapi/v1/klines`, candele da 1 giorno, la stessa fonte di
    `buchi_archivio.py`) e salvati nella cartella della cache (mai in `research/data/`); poi F5 rifatta con il pannello riempito in
    memoria. I file orari mensili dell'archivio non hanno quei giorni."""
    import requests
    b = carica_base()
    pan = {k: (v.copy() if isinstance(v, np.ndarray) else v) for k, v in b["pan"].items()}
    t0 = pan["t0"]
    C = pan["close"]
    simb = pan["simboli"]
    gruppi = {"2022-02": [sc.giorno(2022, 2, d) for d in (26, 27, 28)], "2022-04": [sc.giorno(2022, 4, d) for d in (1, 2)],
              "2023-02": [sc.giorno(2023, 2, d) for d in range(1, 6)]}
    cartella = CACHE / "giorni_buchi"
    cartella.mkdir(exist_ok=True)
    riempiti, scaricati = 0, 0
    for j, s in enumerate(simb):
        ok = np.isfinite(C[:, j])
        idx = np.flatnonzero(ok)
        if not len(idx):
            continue
        for mese, gg in gruppi.items():
            manca = [g for g in gg if idx[0] <= g - t0 <= idx[-1] and not ok[g - t0]]
            if not manca:
                continue
            f = cartella / f"{s}-{mese}.json"
            if not f.exists():
                r = requests.get("https://www.binance.com/fapi/v1/klines", params={"symbol": s, "interval": "1d",
                                 "startTime": gg[0] * 86_400_000, "limit": len(gg)}, timeout=30)
                r.raise_for_status()
                f.write_text(r.text, encoding="utf-8")
                scaricati += 1
                time.sleep(0.2)
            for riga in json.loads(f.read_text(encoding="utf-8")):
                g = int(riga[0]) // 86_400_000
                tt = g - t0
                if g in manca and not np.isfinite(pan["close"][tt, j]):
                    pan["open"][tt, j], pan["high"][tt, j], pan["low"][tt, j], pan["close"][tt, j] = map(float, riga[1:5])
                    pan["quote_volume"][tt, j] = float(riga[7])
                    riempiti += 1
    W2, ps2 = f5(pan)
    df2 = te.conto(W2, ps2["R"], ps2["F"], sc.costi_moneta(ps2["simboli"]))
    df2.index = ps2["lunedi"]
    x1, x2 = nel_periodo(b["df"]["netto"]), nel_periodo(df2["netto"])
    n1, n2 = numeri(x1), numeri(x2)
    d = x2 - x1
    salva("buchi", {"fonte": "www.binance.com/fapi/v1/klines 1d, scaricate nella cartella della cache", "file_scaricati_ora": scaricati,
                    "giorni_moneta_riempiti": riempiti, "prima": {k: n1[k] for k in ("sharpe", "annuo", "discesa_max")},
                    "dopo": {k: n2[k] for k in ("sharpe", "annuo", "discesa_max")}, "somma_differenze_punti": float(d.sum()) * 100,
                    "differenze": {sc.data(int(i)): float(v) for i, v in d[d.abs() > 1e-9].items()}})


PARTI = {"buchi": parte_buchi, "polvere": parte_polvere, "avanti": parte_avanti, "orario": parte_orario, "base": parte_base, "ore": parte_ore, "dati": parte_dati, "taglio": parte_taglio, "parita": parte_parita,
         "tempi": parte_tempi, "costi": parte_costi, "conto": parte_conto, "rischio": parte_rischio, "misure": parte_misure,
         "sensi": parte_sensi, "corretto": parte_corretto}

if __name__ == "__main__":
    PARTI[A.parte]()
