"""Audit di G1 nella configurazione del conto vero a 250 USDT (28 novembre 2026, backtest-auditor).

G1 = prova 57 (`research/programma7/PRIMA.md`), calcolata con il nucleo riscritto (`research/programma7/revisione_g1n/nucleo.py`).
Il conto vero (`bot/portafoglio/conto_vero.py`, spento; dal 28 novembre torna a G1) riusa il ribilancio del demo
(`bot/portafoglio/demo_binance.py`): ogni giorno verso le 00:05 UTC ordini limite GTC al prezzo mark per un'ora, poi il resto a mercato;
quantita' arrotondate al passo verso zero, saltato ogni ordine sotto la quantita' minima o il valore minimo (anche le chiusure,
`ordini_del_giorno`, `demo_binance.py:324-343`); leva 5, margine unico; stop sul conto a -35% dal massimo con il pavimento al 65% del
capitale; oltre 600 USDT di valore niente ordini nuovi (`conto_vero.py:127`).

Uso (dalla radice del repository):
  python3 -I audits/repro/g1_conto_vero_250_2026-11-28.py <parte> --pannello <pickle> --cache <cartella>
Parti (in quest'ordine: base prima, conto prima di misure/esame/esame_v): base ore dati taglio parita parita_ricerca buchi conto
polvere rischio orario discese_partenze rumore mancanti tempi misure sensi esame esame_v esame_costi avanti
Ogni parte scrive solo `audits/repro/g1_conto_vero_250_2026-11-28_esito_<parte>.json` e la cache (mai `research/data/`).
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
ARG.add_argument("--pannello", default="")
ARG.add_argument("--cache", required=True)
A = ARG.parse_args()
sys.path.insert(0, str(RADICE))
CACHE = Path(A.cache)
CACHE.mkdir(parents=True, exist_ok=True)
assert "research/data" not in str(CACHE.resolve()), "la cache non va in research/data"

from research.programma6 import seconda as sc  # noqa: E402
from research.programma7.revisione_g1n import nucleo as nu  # noqa: E402

INIZIO = sc.giorno(2021, 1, 4)              # PRIMA.md, sezione 2: «Dal 4 gennaio 2021 al 4 ottobre 2026»
FINE = sc.giorno(2026, 10, 5)               # escluso: l'ultimo giorno tenuto e' il 4 ottobre 2026
FILTRI = RADICE / "bot" / "portafoglio" / "filtri_conto_vero.json"
CAPITALE = 250.0
TETTO_VALORE = 600.0                        # conto_vero.VALORE_MASSIMO_PER_ORDINI
STOP, PAVIMENTO = 0.35, 0.65


def log(*a):
    print(time.strftime("%H:%M:%S"), *a, flush=True)


def salva(parte: str, out: dict) -> None:
    f = QUI / f"g1_conto_vero_250_2026-11-28_esito_{parte}.json"
    f.write_text(json.dumps(out, ensure_ascii=False, indent=1, default=float), encoding="utf-8")
    log("scritto", f.name)


def pannello() -> dict:
    return pd.read_pickle(A.pannello) if A.pannello else sc.pannello()


def lunedi(giorni) -> np.ndarray:
    g = np.asarray(giorni, np.int64)
    return g - ((g + 3) % 7)


def anno(giorni) -> np.ndarray:
    return pd.to_datetime(np.asarray(giorni) * 86400, unit="s").year.to_numpy()


def settimane(d: pd.Series) -> pd.Series:
    return d.groupby(lunedi(d.index.to_numpy())).sum()


def misure(w: pd.Series) -> dict:
    v = w.to_numpy(float)
    sd = v.std(ddof=1)
    eq = np.cumprod(1 + v)
    dd = eq / np.maximum.accumulate(eq) - 1
    lungo = cur = 0
    for s_ in dd < -1e-12:
        cur = cur + 1 if s_ else 0
        lungo = max(lungo, cur)
    dsd = math.sqrt((np.minimum(v, 0) ** 2).mean())
    a = anno(w.index)
    return {"settimane": int(len(v)), "annuo": float(v.mean() * 52), "volatilita": float(sd * math.sqrt(52)),
            "sharpe": float(v.mean() / sd * math.sqrt(52)) if sd > 0 else 0.0,
            "sortino": float(v.mean() * 52 / (dsd * math.sqrt(52))) if dsd > 0 else 0.0,
            "t": float(v.mean() / sd * math.sqrt(len(v))) if sd > 0 else 0.0,
            "discesa_max": float(dd.min()), "discesa_settimane_piu_lunga": int(lungo),
            "per_anno": {int(y): float(v[a == y].mean() * 52) for y in sorted(set(a))},
            "per_anno_composto": {int(y): float(np.prod(1 + v[a == y]) - 1) for y in sorted(set(a))}}


def misure_giorni(d: pd.Series) -> dict:
    v = d.to_numpy(float)
    eq = np.cumprod(1 + v)
    dd = eq / np.maximum.accumulate(eq) - 1
    k = int(np.argmin(dd))
    picco = int(np.argmax(eq[:k + 1])) if k > 0 else 0
    rec = np.flatnonzero(eq[k:] >= eq[picco])
    return {"discesa_giornaliera": float(dd.min()), "dal": sc.data(int(d.index[picco])), "al": sc.data(int(d.index[k])),
            "recupero": sc.data(int(d.index[k + rec[0]])) if len(rec) else "mai",
            "giorni_dal_massimo_al_recupero": int(rec[0] + k - picco) if len(rec) else None,
            "sharpe_giornaliero_365": float(v.mean() / v.std(ddof=1) * math.sqrt(365))}


# ---------------------------------------------------------------------------
# G1 della ricerca (nucleo) e le candele delle ore 00 e 01
# ---------------------------------------------------------------------------

def carica_base(fine: int = FINE) -> dict:
    f = CACHE / f"base_{fine}.pkl"
    if f.exists():
        return pickle.loads(f.read_bytes())
    pan = pannello()
    simboli = pan["simboli"]
    giorni = np.arange(INIZIO, fine, dtype=np.int64)
    idx = giorni - pan["t0"]
    t = time.time()
    U = nu.universo_giorni(pan, idx)
    W, _, _ = nu.pesi(pan, idx, U, fisso=(1.0, 1.0))
    log(f"pesi G1 fino al {sc.data(int(fine - 1))} in {time.time() - t:.0f}s")
    b = {"giorni": giorni, "idx": idx, "simboli": simboli, "U": U, "W": W,
         "R": nu.ritorni_tenuta(pan["open"], pan["close"])[idx], "F": np.nan_to_num(pan["funding"][idx]),
         "O": pan["open"][idx], "H": pan["high"][idx], "L": pan["low"][idx],
         "costo": np.array([nu.costo_di(s) for s in simboli]),
         "stimato": pan["funding_stimato"][idx]}
    f.write_bytes(pickle.dumps(b))
    return b


def carica_ore(simboli_usati: list) -> dict:
    """{simbolo: {ora: (open, high, low, close)}} per le ore 00 e 01 UTC dal 4 gennaio 2021 (come `analisi.candele_ore`)."""
    f = CACHE / "ore.pkl"
    ore = pickle.loads(f.read_bytes()) if f.exists() else {}
    mancano = [s for s in simboli_usati if s not in ore]
    if mancano:
        from research.programma6 import esecuzione as es
        for n, s in enumerate(mancano):
            b = es.ore_di(s)
            if b.empty:
                ore[s] = {}
                continue
            b = b[(b.index >= INIZIO * 24) & (b.index % 24 < 2)]
            ore[s] = {int(h): tuple(float(v) for v in r) for h, r in zip(b.index, b[["open", "high", "low", "close"]].to_numpy())}
            if n % 50 == 0:
                log(f"[ore] {n}/{len(mancano)}")
        f.write_bytes(pickle.dumps(ore))
    return ore


def matrici_ore(b: dict, ore: dict) -> dict:
    """O00, H00, L00, O01 come matrici giorni x monete (NaN dove manca)."""
    f = CACHE / f"matrici_ore_{int(b['giorni'][-1])}.pkl"
    if f.exists():
        return pickle.loads(f.read_bytes())
    T, S = b["W"].shape
    M = {k: np.full((T, S), np.nan) for k in ("O00", "H00", "L00", "O01")}
    pos = {int(g): k for k, g in enumerate(b["giorni"])}
    for j, s in enumerate(b["simboli"]):
        z = ore.get(s)
        if not z:
            continue
        for h, (o, hi, lo, c) in z.items():
            g, ora = divmod(h, 24)
            k = pos.get(g)
            if k is None:
                continue
            if ora == 0:
                M["O00"][k, j], M["H00"][k, j], M["L00"][k, j] = o, hi, lo
            else:
                M["O01"][k, j] = o
    f.write_bytes(pickle.dumps(M))
    return M


def tasso_limite(segno: np.ndarray, M: dict, k: int, costo: np.ndarray, oltre: float) -> tuple:
    """Costo per unita' di valore scambiato il giorno k: limite all'apertura delle 00:00 per un'ora (MAKER) se il prezzo passa il
    livello di ``oltre``, altrimenti a mercato alle 01:00 con il movimento contro (come `nucleo.spese_limite`); senza ore, a mercato."""
    o, hi, lo, p1 = M["O00"][k], M["H00"][k], M["L00"][k], M["O01"][k]
    ok = np.isfinite(o) & np.isfinite(hi) & np.isfinite(lo) & np.isfinite(p1) & (o > 0)
    compra = segno > 0
    with np.errstate(invalid="ignore", divide="ignore"):
        preso = np.where(compra, lo < o * (1 - oltre), hi > o * (1 + oltre))
        contro = np.where(compra, p1 / o - 1, 1 - p1 / o)
    return np.where(ok & preso, nu.MAKER, np.where(ok, costo + np.nan_to_num(contro), costo)), ok & preso, ok


def conto_ricerca(b: dict, M: dict | None, modo: str = "limite", oltre: float = 0.0, quota_mercato: float = 0.0) -> pd.DataFrame:
    """Il conto della ricerca (pesi che derivano, capitale che si compone, nessun minimo): come `nucleo.variazioni` con il costo per
    variazione di ``modo`` ("mercato", "limite" con ``oltre``, "misto" con ``quota_mercato`` del valore a mercato)."""
    W, R, F, costo = b["W"], b["R"], b["F"], b["costo"]
    T, S = W.shape
    deriva = np.zeros(S)
    righe = np.zeros((T, 5))
    for k in range(T):
        x = W[k]
        D = x - deriva
        if modo == "mercato" or M is None:
            tasso = costo
        else:
            tl, _, _ = tasso_limite(np.sign(D), M, k, costo, oltre)
            tasso = tl if modo == "limite" else quota_mercato * costo + (1 - quota_mercato) * tl
        lordo = float(x @ R[k])
        fund = float(x @ F[k])
        spese = float(np.abs(D) @ tasso)
        netto = lordo - spese - fund
        righe[k] = (lordo, spese, fund, netto, float(np.abs(D).sum()))
        deriva = x * (1 + R[k]) / (1 + netto) if 1 + netto > 0 else np.zeros(S)
    return pd.DataFrame(righe, columns=["lordo", "spese", "funding", "netto", "giro"], index=b["giorni"])


# ---------------------------------------------------------------------------
# il conto vero simulato
# ---------------------------------------------------------------------------

def carica_filtri(simboli):
    f = json.loads(FILTRI.read_text(encoding="utf-8"))["filtri"]
    vmin = np.array([float(f[s]["valore_minimo"]) if s in f else 5.0 for s in simboli])
    passo = np.array([float(f[s]["passo"]) if s in f else 0.0 for s in simboli])
    qmin = np.array([float(f[s]["quantita_minima"]) if s in f else 0.0 for s in simboli])
    return vmin, passo, qmin, np.array([s in f for s in simboli])


def simula(b: dict, M: dict | None, capitale: float = CAPITALE, base: str = "tetto", minimi: bool = True,
           chiusure: str = "saltate", modo: str = "limite", oltre: float = 0.0, quota_mercato: float = 0.0,
           da: int = 0, a: int | None = None, stop: bool = False, registra: bool = False, W=None,
           posizioni_dei_giorni: set | None = None) -> dict:
    """Il conto vero simulato giorno per giorno dal giorno ``da`` (indice) a conto vuoto, come il bot.

    Ogni giorno alle 00:00 (il prezzo mark delle 00:05 approssimato con l'apertura): obiettivo = peso x base / prezzo, con base =
    il valore del conto (``base`` "composto"; "tetto": oltre ``TETTO_VALORE`` il valore torna al capitale, il resto si preleva, come
    un capitale nuovo; "fisso": sempre il capitale); variazione arrotondata verso zero al passo; con ``minimi`` saltata se sotto la
    quantita' minima o il valore minimo. ``chiusure``: "saltate" (il bot di oggi, anche le chiusure), "chiusure" (le chiusure a zero
    sotto il valore minimo partono come «solo riduzione», con la quantita' minima), "riduzioni" (tutte le riduzioni). Costi di
    ``modo`` come `conto_ricerca`. Una moneta tenuta senza prezzo (tolta dal listino) si chiude al valore del giorno prima a mercato.
    Con ``stop``: il conto si chiude a mercato (costo della moneta) la prima volta che il valore a fine giorno va sotto il -35% dal
    massimo o il 65% del capitale, e da li' resta vuoto."""
    W = b["W"] if W is None else W
    R, F, O, costo = b["R"], b["F"], b["O"], b["costo"]
    T, S = W.shape
    a = T if a is None else a
    vmin, passo, qmin, _ = carica_filtri(b["simboli"])
    pg = np.where(passo > 0, passo, 1.0)
    q = np.zeros(S)
    ultimo = np.zeros(S)
    E = float(capitale)
    massimo = E
    prelevato = 0.0
    n_prelievi = 0
    fermo_dal = None
    da_rifare = False
    reset_frac = 0.0
    eventi, durate = [], {}
    posizioni = {}
    out = {k: np.zeros(a - da) for k in ("r", "E", "spese", "lordo", "funding", "voluti", "saltati", "saltati_valore",
                                           "chiusure_saltate", "polvere_n", "polvere_valore", "polvere_pnl", "lorda", "netta",
                                           "monete", "ordini", "giro", "peggio_nel_giorno")}
    for k in range(da, a):
        i = k - da
        p = O[k]
        vivo = np.isfinite(p) & (p > 0)
        pp = np.where(vivo, p, 1.0)
        spese = 0.0
        morte = (q != 0) & ~vivo
        if morte.any():
            spese += float((np.abs(q[morte] * ultimo[morte]) * costo[morte]).sum())
            q[morte] = 0.0
        if fermo_dal is not None:
            out["E"][i] = E
            continue
        if da_rifare:
            # il capitale nuovo (oltre il tetto di valore): alla decisione si chiude tutto a mercato e si riapre da zero
            # (`demo_binance.parti_da_zero`); il resto oltre il capitale resta fuori dal conto del bot
            v0 = np.where(vivo, q * pp, q * ultimo)
            c_reset = float((np.abs(v0) * costo).sum())
            reset_frac = c_reset / E               # il costo delle chiusure va alla fase che finisce (nella serie, quel giorno)
            q[:] = 0.0
            prelevato += E - c_reset - capitale
            n_prelievi += 1
            E = capitale
            massimo = E
            da_rifare = False
        bas = E if base in ("composto", "tetto") else capitale
        obi = np.where(vivo, W[k] * bas / pp, 0.0)
        delta = obi - q
        da_fare = vivo & (np.abs(delta * pp) >= (0.01 if minimi else 1e-12))
        if minimi:
            qa_ = np.abs(delta)
            qr = np.where(passo > 0, np.floor(qa_ / pg + 1e-9) * passo, qa_)
            val = qr * pp
            chiude = (obi == 0) & (q != 0)
            riduce = chiude | ((q != 0) & (np.sign(q) == np.sign(obi)) & (np.abs(obi) < np.abs(q)))
            ok_q = qr >= qmin - 1e-12
            ok_v = val >= vmin - 1e-9
            if chiusure == "chiusure":
                ok_v = ok_v | chiude
            elif chiusure == "riduzioni":
                ok_v = ok_v | riduce
            ok = (qr > 0) & ok_q & ok_v
            d = np.where(da_fare & ok, np.sign(delta) * qr, 0.0)
            salt = da_fare & (d == 0)
            out["voluti"][i] = int(da_fare.sum())
            out["saltati"][i] = int(salt.sum())
            out["saltati_valore"][i] = float((np.abs(delta) * pp)[salt].sum() / E) if E > 0 else 0.0
            out["chiusure_saltate"][i] = int((salt & chiude).sum())
        else:
            d = np.where(da_fare, delta, 0.0)
            out["voluti"][i] = int(da_fare.sum())
        dv = d * pp
        if modo == "mercato" or M is None:
            tasso = costo
        else:
            tl, _, _ = tasso_limite(np.sign(dv), M, k, costo, oltre)
            tasso = tl if modo == "limite" else quota_mercato * costo + (1 - quota_mercato) * tl
        spese += float((np.abs(dv) * tasso).sum())
        q = q + d
        if minimi:
            q = np.where(passo > 0, np.round(q / pg) * passo, q)
        q = np.where(np.abs(q * pp) < 1e-9, 0.0, q)
        valore = np.where(vivo, q * pp, 0.0)
        if posizioni_dei_giorni is not None and int(b["giorni"][k]) in posizioni_dei_giorni:
            posizioni[int(b["giorni"][k])] = (valore.copy(), E, spese, massimo)
        lordo = float(valore @ R[k])
        fund = float(valore @ F[k])
        netto = lordo - spese - fund
        polv = (W[k] == 0) & (q != 0)
        if registra:
            for j in np.flatnonzero(polv):
                eff = float(valore[j] * R[k, j] - valore[j] * F[k, j]) / E
                durate[j] = durate.get(j, 0) + 1
                if abs(eff) > 0.002:
                    eventi.append({"giorno": sc.data(int(b["giorni"][k])), "simbolo": b["simboli"][j],
                                   "valore_usdt": round(float(valore[j]), 2), "rendimento": round(float(R[k, j]), 4),
                                   "effetto_sul_conto": round(eff, 5)})
        with np.errstate(invalid="ignore", divide="ignore"):
            su, giu = np.nan_to_num(b["H"][k] / pp - 1), np.nan_to_num(b["L"][k] / pp - 1)
        peggio = float(np.where(valore < 0, valore * su, valore * giu).sum())
        den = E if base != "fisso" else capitale
        out["r"][i] = (netto / den if den > 0 else 0.0) - reset_frac
        reset_frac = 0.0
        out["spese"][i], out["lordo"][i], out["funding"][i] = spese / den, lordo / den, fund / den
        out["polvere_n"][i] = int(polv.sum())
        out["polvere_valore"][i] = float(np.abs(valore[polv]).sum() / E)
        out["polvere_pnl"][i] = float((valore[polv] * R[k][polv]).sum() - (valore[polv] * F[k][polv]).sum()) / E
        out["lorda"][i] = float(np.abs(valore).sum() / E)
        out["netta"][i] = float(valore.sum() / E)
        out["monete"][i] = int((q != 0).sum())
        out["ordini"][i] = int((d != 0).sum())
        out["giro"][i] = float(np.abs(dv).sum() / E)
        out["peggio_nel_giorno"][i] = (peggio - spese) / E
        ultimo = np.where(vivo, pp * (1 + R[k]), 0.0)
        E_prima = E
        E = E + netto
        out["E"][i] = E
        if E <= 0:
            fermo_dal = k
            continue
        massimo = max(massimo, E)
        if stop and E <= max((1 - STOP) * massimo, PAVIMENTO * capitale):
            v_fine = q * ultimo
            E -= float((np.abs(v_fine) * costo).sum())
            q[:] = 0.0
            out["E"][i] = E
            fermo_dal = k
            continue
        if base == "tetto" and E > TETTO_VALORE:
            da_rifare = True
        _ = E_prima
    giorni = b["giorni"][da:a]
    df = pd.DataFrame(out, index=giorni)
    return {"df": df, "fermo_dal": None if fermo_dal is None else sc.data(int(b["giorni"][fermo_dal])),
            "prelevato": prelevato, "prelievi": n_prelievi, "valore_finale": E, "eventi_polvere": eventi,
            "durate_polvere": {b["simboli"][j]: n for j, n in durate.items()}, "posizioni": posizioni}


def sintesi(df: pd.DataFrame, col: str = "r") -> dict:
    w = settimane(df[col])
    m = misure(w)
    m.update(misure_giorni(df[col]))
    return m


# ---------------------------------------------------------------------------
# le parti
# ---------------------------------------------------------------------------

def parte_base():
    b = carica_base()
    W = b["W"]
    usati = [b["simboli"][j] for j in np.flatnonzero(np.abs(W).sum(axis=0) > 0)]
    ore = carica_ore(usati)
    M = matrici_ore(b, ore)
    out = {"periodo": [sc.data(int(b["giorni"][0])), sc.data(int(b["giorni"][-1]))], "giorni": int(len(b["giorni"])),
           "monete_usate": len(usati)}
    # il nucleo cosi' com'e' (variazioni + spese_limite) contro il conto di questo script
    lordo, sp_m, fund, D = nu.variazioni(W, b["R"], b["F"], b["costo"])
    sp_l, n, n_lim = nu.spese_limite(D, b["giorni"], b["simboli"], b["costo"], ore, 0.0)
    netto_nu = pd.Series(lordo - sp_l - fund, index=b["giorni"])
    netto_nu_m = pd.Series(lordo - sp_m - fund, index=b["giorni"])
    out["nucleo_limite"] = sintesi(pd.DataFrame({"r": netto_nu}))
    out["nucleo_mercato"] = sintesi(pd.DataFrame({"r": netto_nu_m}))
    out["nucleo_variazioni"] = {"totali": int(n), "a_limite": int(n_lim)}
    for nome, kw in {"limite_al_tocco": dict(modo="limite", oltre=0.0), "limite_oltre_0,05%": dict(modo="limite", oltre=0.0005),
                     "limite_oltre_0,10%": dict(modo="limite", oltre=0.001), "tutto_a_mercato": dict(modo="mercato")}.items():
        d = conto_ricerca(b, M, **kw)
        out[nome] = sintesi(d.rename(columns={"netto": "r"}))
        out[nome]["spese_annue"] = float(d["spese"].mean() * 365)
        out[nome]["giro_annuo"] = float(d["giro"].mean() * 365)
        if nome == "limite_al_tocco":
            out["differenza_max_con_il_nucleo"] = float(np.abs(d["netto"].to_numpy() - netto_nu.to_numpy()).max())
    # le monete per lato e il peso massimo
    nl, ns = (W > 0).sum(axis=1), (W < 0).sum(axis=1)
    out["lati"] = {"min_lunghi": int(nl.min()), "min_corti": int(ns.min()), "giorni_senza_pesi": int(((nl == 0) | (ns == 0)).sum()),
                   "peso_massimo": float(np.abs(W).max()), "giorno_peso_massimo": sc.data(int(b["giorni"][np.abs(W).max(axis=1).argmax()])),
                   "giorni_oltre_0,60": int((np.abs(W).max(axis=1) > 0.60 + 1e-9).sum()),
                   "giorni_lorda_oltre_2": int((np.abs(W).sum(axis=1) > 2.0 + 1e-9).sum())}
    salva("base", out)


def parte_ore():
    b = carica_base()
    W = b["W"]
    usati = [b["simboli"][j] for j in np.flatnonzero(np.abs(W).sum(axis=0) > 0)]
    ore = carica_ore(usati)
    M = matrici_ore(b, ore)
    tenute = (np.abs(W) > 0)
    out = {k: {"coppie_tenute_senza": int((tenute & ~np.isfinite(v)).sum()), "coppie_tenute": int(tenute.sum())} for k, v in M.items()}
    ok = tenute & np.isfinite(M["O00"]) & np.isfinite(b["O"])
    rel = np.abs(M["O00"][ok] / b["O"][ok] - 1)
    out["apertura_ora_contro_giorno"] = {"coppie": int(ok.sum()), "oltre_0,1%": int((rel > 0.001).sum()), "massimo": float(rel.max())}
    # ordine e doppioni nelle ore (le chiavi sono le ore dall'epoca: un doppione e' impossibile, l'ordine si controlla)
    fuori = sum(1 for s in usati if ore.get(s) and list(ore[s]) != sorted(ore[s]))
    out["monete_con_ore_fuori_ordine"] = fuori
    out["monete_senza_ore"] = [s for s in usati if not ore.get(s)]
    salva("ore", out)


def parte_dati():
    from research.programma6 import buchi_archivio as ba
    pan = pannello()
    b = carica_base()
    W, giorni = b["W"], b["giorni"]
    tenute = np.abs(W) > 0
    out = {}
    # buchi: giorni senza candela per una moneta tenuta il giorno prima (uscita implicita) dentro il periodo
    C = pan["close"][b["idx"]]
    senza = tenute & ~np.isfinite(b["O"])
    out["coppie_tenute_senza_apertura"] = int(senza.sum())
    bu = []
    for j in np.flatnonzero(tenute.any(axis=0)):
        s = b["simboli"][j]
        try:
            m = ba.giorni_mancanti(sc.simbolo_base(s)[0], int(INIZIO))
        except Exception as exc:  # noqa: BLE001
            bu.append({"simbolo": s, "errore": str(exc)[:80]})
            continue
        m = [g for g in m if INIZIO <= g < FINE]
        if m:
            k = np.searchsorted(giorni, m)
            tenuto_prima = [g for g, kk in zip(m, k) if kk > 0 and tenute[kk - 1, j]]
            if tenuto_prima:
                bu.append({"simbolo": s, "giorni_mancanti_tenuti": [sc.data(int(g)) for g in tenuto_prima][:6],
                           "n": len(tenuto_prima)})
    out["buchi_con_la_moneta_tenuta"] = bu
    # monete ferme (volume zero) tenute
    V = pan["quote_volume"][b["idx"]]
    ferme = tenute & np.isfinite(C) & (np.nan_to_num(V) == 0)
    out["coppie_tenute_ferme"] = int(ferme.sum())
    # valori anomali fra le tenute
    R = b["R"]
    out["rendimenti_tenuti_estremi"] = {"sopra_+100%": int((tenute & (R > 1.0)).sum()), "sotto_-60%": int((tenute & (R < -0.6)).sum()),
                                        "massimo": float(R[tenute].max()), "minimo": float(R[tenute].min())}
    k, j = np.unravel_index(np.argmax(np.where(tenute, R, -9)), R.shape)
    out["rendimenti_tenuti_estremi"]["dove_massimo"] = [b["simboli"][j], sc.data(int(giorni[k])), float(W[k, j])]
    # high/low incoerenti
    Hh, Ll, Oo = b["H"], b["L"], b["O"]
    out["candele_incoerenti_tenute"] = int((tenute & np.isfinite(Oo) & ((Hh < Oo - 1e-12) | (Ll > Oo + 1e-12) | (Ll > Hh))).sum())
    # funding: stimato, zero
    st = b["stimato"]
    out["funding_stimato_tenuto"] = {"coppie": int((tenute & st).sum()), "peso_lordo_giorni": float(np.abs(W)[st & tenute].sum()),
                                     "giorni": sorted({sc.data(int(g)) for g in giorni[(tenute & st).any(axis=1)]})[:40]}
    # funding stimato nei 7 giorni del segnale (cambia il segnale)
    Fp = pan["funding_stimato"]
    segn = np.zeros(len(giorni), int)
    for kk, i in enumerate(b["idx"]):
        segn[kk] = int(Fp[i - 7:i][:, b["U"][kk]].any(axis=0).sum())
    out["segnale_con_funding_stimato"] = {"giorni": int((segn > 0).sum()), "monete_giorno": int(segn.sum())}
    zero = tenute & np.isfinite(C) & (b["F"] == 0) & (np.nan_to_num(V) > 0)
    out["funding_zero_tenuto"] = {"coppie": int(zero.sum()), "quota": float(zero.sum() / tenute.sum())}
    # orari dei regolamenti letti dai dati: intervalli fra regolamenti delle monete tenute (archivio mensile)
    from research.src.dati import funding_da_zip
    intervalli = {}
    campione = [b["simboli"][j] for j in np.flatnonzero(tenute.any(axis=0))]
    rng = np.random.default_rng(5)
    for s in rng.choice(campione, min(40, len(campione)), replace=False):
        base = sc.simbolo_base(s)[0]
        righe = []
        for p in sorted((sc.DATI / base / "funding").glob("*.zip")):
            righe += funding_da_zip(p)
        if not righe:
            continue
        ts = np.sort(np.unique(np.array([r[0] for r in righe], np.int64)))
        ts = ts[(ts >= INIZIO * 86400000) & (ts < FINE * 86400000)]
        dh = np.round(np.diff(ts) / 3_600_000).astype(int)
        minuti = (ts // 60000) % 60
        vals, cnt = np.unique(dh, return_counts=True)
        intervalli[str(s)] = {"intervalli_ore": {int(v): int(c) for v, c in zip(vals, cnt) if c > 2},
                              "regolamenti_non_all_ora_tonda": int((minuti != 0).sum())}
    out["intervalli_del_funding_campione"] = intervalli
    out["giorni_universo_sotto_100"] = int((b["U"].sum(axis=1) < 100).sum())
    salva("dati", out)


def parte_taglio():
    """Pesi di G1 del giorno d col pannello tagliato alle 00:00 di d (prezzi dopo l'apertura di d cancellati, funding dei giorni di
    tenuta da d in poi a zero) contro i pesi col pannello intero."""
    pan = pannello()
    b = carica_base()
    rng = np.random.default_rng(28)
    prove = sorted(set(rng.choice(np.arange(INIZIO + 200, FINE - 1), 6, replace=False).tolist()) | {int(FINE - 1)})
    righe = []
    for d in prove:
        i = d - pan["t0"]
        p = {k: (v.copy() if isinstance(v, np.ndarray) else v) for k, v in pan.items()}
        for c in ("high", "low", "close", "quote_volume", "taker_buy_quote_volume"):
            p[c][i:] = np.nan
        p["open"][i + 1:] = np.nan
        p["funding"][i:] = 0.0
        g = np.arange(INIZIO, d + 1, dtype=np.int64)
        idx = g - pan["t0"]
        U = nu.universo_giorni(p, idx)
        W2, _, _ = nu.pesi(p, idx, U, fisso=(1.0, 1.0))
        k = int(d - INIZIO)
        righe.append({"giorno": sc.data(int(d)), "diff_max": float(np.abs(W2[k] - b["W"][k]).max()),
                      "monete": int((b["W"][k] != 0).sum())})
        log(righe[-1])
    salva("taglio", {"giorni": righe})


def parte_parita():
    """Le funzioni pure del bot (`bot/portafoglio/f5.py`) contro il nucleo, 60 giorni a caso, con la candela in corso falsata
    (come `revisione_g1n/parita_bot.py`, senza scrivere fuori da audits/)."""
    from bot.portafoglio import f5 as bot
    pan = pannello()
    b = carica_base()
    simboli = pan["simboli"]
    C, O, V, F = pan["close"], pan["open"], pan["quote_volume"], pan["funding"]
    ok = np.isfinite(C)
    primo_i = np.where(ok.any(axis=0), ok.argmax(axis=0), C.shape[0])
    primo = {s: int(primo_i[j] + pan["t0"]) for j, s in enumerate(simboli)}
    rng = np.random.default_rng(57)
    giorni_prova = sorted(rng.choice(np.arange(INIZIO + 1, FINE), 60, replace=False).tolist())
    righe = []
    for d in giorni_prova:
        k = int(d - INIZIO)
        i = int(d - pan["t0"])
        attivi = [j for j in range(len(simboli)) if np.isfinite(C[i - 99:i + 1, j]).any()]
        giornaliere = {}
        for j in attivi:
            g = {}
            for t in range(i - 99, i + 1):
                if np.isfinite(O[t, j]) or np.isfinite(C[t, j]):
                    g[t + pan["t0"]] = (float(O[t, j]), float(C[t, j] if t < i else C[t, j] * 7.0), float(V[t, j] if t < i else V[t, j] * 7.0))
            giornaliere[simboli[j]] = g
        uni = bot.universo(giornaliere, {s: primo[s] for s in giornaliere}, bot.lunedi_di(int(d)))
        uni_r = sorted(simboli[j] for j in np.flatnonzero(b["U"][k]))
        sigma = {s: bot.sigma_30({t: v[1] for t, v in giornaliere[s].items()}, int(d)) for s in uni}
        funding = {s: {t + pan["t0"]: float(F[t, simboli.index(s)]) for t in range(i - 8, i)} for s in uni}
        segnale = {s: (-bot.funding_7(funding[s], int(d)) if np.isfinite(sigma[s]) else float("nan")) for s in uni}
        prev = b["W"][k - 1] if k > 0 else np.zeros(len(simboli))
        lunghi = {simboli[j] for j in np.flatnonzero(prev > 0)}
        corti = {simboli[j] for j in np.flatnonzero(prev < 0)}
        pesi, _, _ = bot.pesi_banda(segnale, sigma, lunghi, corti)
        v = np.zeros(len(simboli))
        for s, w in pesi.items():
            v[simboli.index(s)] = w
        righe.append({"giorno": sc.data(int(d)), "universo_uguale": sorted(uni) == uni_r, "diff_universo": len(set(uni) ^ set(uni_r)),
                      "diff_max_G1": float(np.abs(v - b["W"][k]).max()), "lati_cambiati": int((np.sign(v) != np.sign(b["W"][k])).sum())})
    out = {"giorni": len(righe), "universo_uguale": sum(r["universo_uguale"] for r in righe),
           "diff_max_G1": max(r["diff_max_G1"] for r in righe), "giorni_con_lati_cambiati": sum(1 for r in righe if r["lati_cambiati"]),
           "righe": righe}
    log({k: v for k, v in out.items() if k != "righe"})
    salva("parita", out)


VARIANTI_CONTO = {
    # nome: argomenti di simula
    "ricerca_senza_minimi_composto": dict(minimi=False, base="composto"),
    "bot_oggi_tetto": dict(minimi=True, base="tetto", chiusure="saltate"),
    "solo_riduzione_chiusure_tetto": dict(minimi=True, base="tetto", chiusure="chiusure"),
    "solo_riduzione_riduzioni_tetto": dict(minimi=True, base="tetto", chiusure="riduzioni"),
    "bot_oggi_fisso": dict(minimi=True, base="fisso", chiusure="saltate"),
    "solo_riduzione_chiusure_fisso": dict(minimi=True, base="fisso", chiusure="chiusure"),
    "bot_oggi_composto_senza_tetto": dict(minimi=True, base="composto", chiusure="saltate"),
    "senza_minimi_tetto": dict(minimi=False, base="tetto"),
    "bot_oggi_fisso_280 (come la prova 148 A)": dict(minimi=True, base="fisso", chiusure="saltate", capitale=280.0),
    "solo_riduzione_chiusure_fisso_280 (come la prova 148 A2)": dict(minimi=True, base="fisso", chiusure="chiusure", capitale=280.0),
    "bot_oggi_tetto_300": dict(minimi=True, base="tetto", chiusure="saltate", capitale=300.0),
    "solo_riduzione_chiusure_tetto_300": dict(minimi=True, base="tetto", chiusure="chiusure", capitale=300.0),
}
COSTI = {
    "limite_al_tocco": dict(modo="limite", oltre=0.0),
    "tutto_a_mercato": dict(modo="mercato"),
    "limite_oltre_0,05%": dict(modo="limite", oltre=0.0005),
    "limite_oltre_0,10%": dict(modo="limite", oltre=0.001),
    "misto_27%_a_mercato": dict(modo="misto", oltre=0.0, quota_mercato=0.27),
    "misto_58%_a_mercato": dict(modo="misto", oltre=0.0, quota_mercato=0.58),
}


def _riassunto(r: dict) -> dict:
    df = r["df"]
    s = sintesi(df)
    nel = df[df.index < FINE]
    s.update({"spese_annue": float(df["spese"].mean() * 365), "giro_annuo": float(df["giro"].mean() * 365),
              "funding_annuo": float(df["funding"].mean() * 365), "lorda_media": float(df["lorda"].mean()),
              "netta_media": float(df["netta"].mean()), "netta_min": float(df["netta"].min()), "netta_max": float(df["netta"].max()),
              "monete_medie": float(df["monete"].mean()), "ordini_al_giorno": float(df["ordini"].mean()),
              "voluti_al_giorno": float(df["voluti"].mean()), "saltati_al_giorno": float(df["saltati"].mean()),
              "quota_saltati": float(df["saltati"].sum() / max(1, df["voluti"].sum())),
              "valore_saltato_medio": float(df["saltati_valore"].mean()),
              "chiusure_saltate_totali": int(df["chiusure_saltate"].sum()),
              "polvere_coppie": int(df["polvere_n"].sum()), "polvere_valore_medio": float(df["polvere_valore"].mean()),
              "polvere_pnl_annuo": float(df["polvere_pnl"].mean() * 365),
              "prelievi": r["prelievi"], "prelevato": r["prelevato"], "valore_finale": r["valore_finale"], "fermo_dal": r["fermo_dal"],
              "giorni": int(len(nel))})
    return s


def parte_conto():
    b = carica_base()
    usati = [b["simboli"][j] for j in np.flatnonzero(np.abs(b["W"]).sum(axis=0) > 0)]
    M = matrici_ore(b, carica_ore(usati))
    out = {"capitale": CAPITALE, "periodo": [sc.data(int(b["giorni"][0])), sc.data(int(b["giorni"][-1]))]}
    # verifica del simulatore: senza minimi e composto deve rifare il conto della ricerca
    r0 = simula(b, M, minimi=False, base="composto", modo="limite")["df"]["r"]
    c0 = conto_ricerca(b, M, modo="limite")["netto"]
    out["verifica_simulatore_contro_ricerca"] = float(np.abs(r0.to_numpy() - c0.to_numpy()).max())
    log("verifica", out["verifica_simulatore_contro_ricerca"])
    for nome_c, kc in COSTI.items():
        for nome_v, kv in VARIANTI_CONTO.items():
            if nome_c not in ("limite_al_tocco", "tutto_a_mercato") and nome_v not in (
                    "ricerca_senza_minimi_composto", "bot_oggi_tetto", "solo_riduzione_chiusure_tetto"):
                continue
            r = simula(b, M, **kv, **kc)
            out[f"{nome_v} | {nome_c}"] = _riassunto(r)
            s = out[f"{nome_v} | {nome_c}"]
            log(f"{nome_v} | {nome_c}: Sharpe {s['sharpe']:.2f} annuo {s['annuo']:+.1%} discesa {s['discesa_max']:.1%} "
                f"saltati {s['quota_saltati']:.0%}")
            if nome_c == "limite_al_tocco" and nome_v in ("bot_oggi_tetto", "solo_riduzione_chiusure_tetto", "ricerca_senza_minimi_composto"):
                (CACHE / f"serie_{nome_v}.pkl").write_bytes(pickle.dumps(r["df"]))
            if nome_c == "tutto_a_mercato" and nome_v in ("bot_oggi_tetto", "solo_riduzione_chiusure_tetto"):
                (CACHE / f"serie_{nome_v}_mercato.pkl").write_bytes(pickle.dumps(r["df"]))
            if nome_c == "limite_oltre_0,05%" and nome_v in ("bot_oggi_tetto", "solo_riduzione_chiusure_tetto"):
                (CACHE / f"serie_{nome_v}_oltre005.pkl").write_bytes(pickle.dumps(r["df"]))
            if nome_c == "misto_27%_a_mercato" and nome_v in ("bot_oggi_tetto",):
                (CACHE / f"serie_{nome_v}_misto27.pkl").write_bytes(pickle.dumps(r["df"]))
    # i rifiuti giorno per giorno (bot di oggi, limite al tocco)
    df = pickle.loads((CACHE / "serie_bot_oggi_tetto.pkl").read_bytes())
    sal = df["saltati"]
    out["rifiuti_per_giorno"] = {
        "voluti": {"media": float(df["voluti"].mean()), "mediana": float(df["voluti"].median())},
        "saltati": {"media": float(sal.mean()), "mediana": float(sal.median()), "p90": float(sal.quantile(0.9)), "massimo": int(sal.max())},
        "quota_saltati_media_per_giorno": float((sal / df["voluti"].clip(lower=1)).mean()),
        "valore_saltato_in_frazione_del_conto": {"media": float(df["saltati_valore"].mean()), "mediana": float(df["saltati_valore"].median()),
                                                "p90": float(df["saltati_valore"].quantile(0.9)), "massimo": float(df["saltati_valore"].max()),
                                                "giorno_massimo": sc.data(int(df["saltati_valore"].idxmax()))},
        "chiusure_saltate": {"totali": int(df["chiusure_saltate"].sum()), "giorni_con_almeno_una": int((df["chiusure_saltate"] > 0).sum())},
        "per_anno_saltati_medi": {int(y): float(sal[anno(df.index) == y].mean()) for y in sorted(set(anno(df.index)))},
        "primo_giorno": {"voluti": int(df["voluti"].iloc[0]), "saltati": int(df["saltati"].iloc[0]),
                         "valore_saltato": float(df["saltati_valore"].iloc[0]), "lorda_dopo": float(df["lorda"].iloc[0])}}
    # quanto pesano: differenza giornaliera con la ricerca senza minimi sugli stessi costi
    ric = pickle.loads((CACHE / "serie_ricerca_senza_minimi_composto.pkl").read_bytes())["r"]
    diff = df["r"] - ric
    out["peso_dei_minimi"] = {"differenza_media_annua": float(diff.mean() * 365), "oscillazione_giornaliera": float(diff.std()),
                              "oscillazione_settimanale": float(settimane(diff).std()),
                              "correlazione_settimanale": float(np.corrcoef(settimane(df["r"]), settimane(ric))[0, 1]),
                              "polvere_pnl_annuo": float(df["polvere_pnl"].mean() * 365),
                              "esposizione_netta_p5_p95": [float(df["netta"].quantile(0.05)), float(df["netta"].quantile(0.95))]}
    # le perdite peggiori da posizioni non volute (bot di oggi)
    salva("conto", out)


def parte_polvere():
    """Le posizioni rimaste sotto il minimo (non volute dalla strategia): i giorni in cui pesano di piu' sul conto, con il bot di oggi
    e con le chiusure «solo riduzione» (stesso simulatore, base "tetto", limite al tocco e tutto a mercato)."""
    b = carica_base()
    usati = [b["simboli"][j] for j in np.flatnonzero(np.abs(b["W"]).sum(axis=0) > 0)]
    M = matrici_ore(b, carica_ore(usati))
    out = {}
    for chius in ("saltate", "chiusure"):
        for modo in ("limite", "mercato"):
            r = simula(b, M, base="tetto", chiusure=chius, modo=modo, registra=True)
            ev = sorted(r["eventi_polvere"], key=lambda x: x["effetto_sul_conto"])
            df = r["df"]
            dur = r["durate_polvere"]
            out[f"{chius} | {modo}"] = {
                "coppie_giorno_di_polvere": int(df["polvere_n"].sum()), "al_giorno": float(df["polvere_n"].mean()),
                "valore_medio_in_frazione_del_conto": float(df["polvere_valore"].mean()),
                "valore_massimo": float(df["polvere_valore"].max()), "giorno_valore_massimo": sc.data(int(df["polvere_valore"].idxmax())),
                "effetto_annuo": float(df["polvere_pnl"].mean() * 365),
                "giorno_peggiore": [sc.data(int(df["polvere_pnl"].idxmin())), float(df["polvere_pnl"].min())],
                "peggiori": ev[:8], "migliori": ev[-5:][::-1], "eventi_oltre_0,2%": len(ev),
                "monete_piu_lunghe": sorted(dur.items(), key=lambda x: -x[1])[:8]}
            log(chius, modo, out[f"{chius} | {modo}"]["coppie_giorno_di_polvere"], out[f"{chius} | {modo}"]["effetto_annuo"])
    salva("polvere", out)


def parte_rischio():
    """Lo stop sul conto da ogni partenza (ogni 7 giorni, da conto vuoto alla mezzanotte), con il bot di oggi e con le chiusure
    «solo riduzione»; il limite prudente nel giorno; la distanza dalla liquidazione."""
    b = carica_base()
    usati = [b["simboli"][j] for j in np.flatnonzero(np.abs(b["W"]).sum(axis=0) > 0)]
    M = matrici_ore(b, carica_ore(usati))
    T = b["W"].shape[0]
    out = {}
    for nome, kv in {"bot_oggi": dict(chiusure="saltate"), "solo_riduzione_chiusure": dict(chiusure="chiusure")}.items():
        for costo_n, kc in {"limite_al_tocco": dict(modo="limite"), "tutto_a_mercato": dict(modo="mercato")}.items():
            righe = []
            for da in range(0, T - 30, 7):
                r = simula(b, M, base="tetto", stop=True, da=da, **kv, **kc)
                df = r["df"]
                e = df["E"].to_numpy()
                an = min(len(e), 365)
                righe.append({"partenza": sc.data(int(b["giorni"][da])), "stop": r["fermo_dal"],
                              "un_anno": float(e[an - 1] / CAPITALE - 1) if r["fermo_dal"] is None or an < len(e) else None,
                              "minimo_primo_anno": float(e[:an].min() / CAPITALE - 1)})
            stop = [x for x in righe if x["stop"]]
            entro = [x for x in stop if (sc.giorno(*map(int, x["stop"].split("-"))) - sc.giorno(*map(int, x["partenza"].split("-")))) <= 365]
            out[f"{nome} | {costo_n}"] = {
                "partenze": len(righe), "con_stop": len(stop), "con_stop_entro_un_anno": len(entro),
                "date_dello_stop": sorted({x["stop"] for x in stop}),
                "partenze_con_stop_entro_un_anno": [x["partenza"] for x in entro][:60],
                "minimo_primo_anno_peggiore": float(min(x["minimo_primo_anno"] for x in righe)),
                "quota_partenze_in_perdita_dopo_un_anno": float(np.mean([x["un_anno"] is not None and x["un_anno"] < 0 for x in righe[:-52]])),
                "partenze_peggiori": sorted(righe, key=lambda x: x["minimo_primo_anno"])[:6]}
            log(nome, costo_n, out[f"{nome} | {costo_n}"]["con_stop"], out[f"{nome} | {costo_n}"]["con_stop_entro_un_anno"])
    # tutto il periodo dal 4 gennaio 2021 senza stop: discese e limite prudente nel giorno
    r = simula(b, M, base="tetto", chiusure="saltate", modo="limite")
    df = r["df"]
    e = (1 + df["r"]).cumprod()
    dd = e / e.cummax() - 1
    disc = []
    x = dd.to_numpy()
    k = 0
    while k < len(x):
        if x[k] < -0.15:
            j = k
            while j < len(x) and x[j] < 0:
                j += 1
            seg = x[k:j]
            m = k + int(np.argmin(seg))
            disc.append({"minimo": sc.data(int(df.index[m])), "profondita": float(x[m]), "fine": sc.data(int(df.index[j - 1]))})
            k = j
        else:
            k += 1
    disc.sort(key=lambda z: z["profondita"])
    out["discese_oltre_15%_bot_oggi"] = disc[:8]
    # limite prudente: tutti i lunghi al minimo e i corti al massimo dello stesso giorno, dal valore di inizio giorno
    pg = df["peggio_nel_giorno"]
    out["limite_prudente_nel_giorno"] = {"peggiore": float(pg.min()), "giorno": sc.data(int(pg.idxmin())),
                                         "quantile_1%": float(pg.quantile(0.01)), "giorni_sotto_-20%": int((pg < -0.2).sum()),
                                         "giorni_sotto_-35%": int((pg < -0.35).sum())}
    # discesa intragiornaliera prudente dal massimo: valore di inizio giorno x (1 + peggio) contro il massimo delle chiusure
    inizio = e.shift(1).fillna(1.0)
    basso = inizio * (1 + pg)
    dd_p = basso / e.cummax().shift(1).fillna(1.0) - 1
    out["discesa_prudente_dal_massimo"] = {"peggiore": float(dd_p.min()), "giorno": sc.data(int(dd_p.idxmin())),
                                           "giorni_oltre_-35%": int((dd_p < -0.35).sum()),
                                           "giorni": [sc.data(int(g)) for g in dd_p.index[dd_p < -0.35]][:20]}
    out["liquidazione"] = {"lorda_media": float(df["lorda"].mean()), "lorda_massima": float(df["lorda"].max()),
                           "nota": "margine unico: con lorda 2 il mantenimento (circa 0,4-1% del nozionale per moneta piccola, da verificare) "
                                   "e' circa 1-2% del conto; la liquidazione chiede una perdita del 98% circa del conto, lo stop a -35% viene prima"}
    salva("rischio", out)


def parte_misure():
    b = carica_base()
    out = {}
    for nome in ("bot_oggi_tetto", "solo_riduzione_chiusure_tetto", "ricerca_senza_minimi_composto"):
        df = pickle.loads((CACHE / f"serie_{nome}.pkl").read_bytes())
        r = df["r"]
        w = settimane(r)
        tot = r.sum()
        mesi = r.groupby(pd.to_datetime(r.index.to_numpy() * 86400, unit="s").to_period("M")).sum()
        o = {"giorni": int(len(r)), "giorni_con_ordini": int((df["ordini"] > 0).sum()),
             "quota_dei_5_giorni_migliori": float(r.nlargest(5).sum() / tot), "quota_dei_3_mesi_migliori": float(mesi.nlargest(3).sum() / tot),
             "mesi_migliori": {str(k): float(v) for k, v in mesi.nlargest(3).items()},
             "esposizione_lorda_media": float(df["lorda"].mean()), "giorni_con_posizioni": int((df["monete"] > 0).sum()),
             "rendimento_medio_al_giorno": float(r.mean()), "spese_medie_al_giorno": float(df["spese"].mean())}
        # clima del mercato: rendimento a 30 giorni del Bitcoin al giorno prima (rialzo > +10%, ribasso < -10%, altrimenti laterale)
        jb = b["simboli"].index("BTCUSDT")
        btc = pd.Series(b["O"][:, jb], index=b["giorni"])
        r30 = btc / btc.shift(30) - 1
        clima = np.where(r30 > 0.10, "rialzo", np.where(r30 < -0.10, "ribasso", "laterale"))
        o["clima"] = {c: {"giorni": int((clima == c).sum()), "annuo": float(r[clima == c].mean() * 365),
                          "sharpe_giornaliero": float(r[clima == c].mean() / r[clima == c].std() * math.sqrt(365))}
                      for c in ("rialzo", "ribasso", "laterale")}
        o["definizione_clima"] = "Bitcoin: apertura di oggi contro quella di 30 giorni prima; oltre +10% rialzo, sotto -10% ribasso"
        out[nome] = o
    salva("misure", out)


def parte_sensi():
    """Parametri variati del 10% e del 20% (banda, giorni del funding, giorni della volatilita', monete dell'universo), sul conto a
    250 USDT del bot di oggi e sulla ricerca, con il limite al tocco."""
    pan = pannello()
    b = carica_base()
    usati = [b["simboli"][j] for j in np.flatnonzero(np.abs(b["W"]).sum(axis=0) > 0)]
    M = matrici_ore(b, carica_ore(usati))
    idx = b["idx"]
    rc = nu.ritorni_chiusura(pan["close"])
    Fp = pan["funding"]
    out = {}
    orig = (nu.ENTRA, nu.RESTA, nu.N_UNI)

    def pesi_con(entra, resta, gf, gs, n_uni):
        nu.ENTRA, nu.RESTA, nu.N_UNI = entra, resta, n_uni
        U = nu.universo_giorni(pan, idx) if n_uni != 100 else b["U"]
        W = np.zeros_like(b["W"])
        lunghi, corti = set(), set()
        for k, i in enumerate(idx):
            f = rc[i - gs:i]
            n = np.isfinite(f).sum(axis=0)
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                sd = np.nanstd(f, axis=0, ddof=1)
            sig = np.where((n >= int(round(20 * gs / 30))) & (sd > 0), sd, np.nan)
            ct = np.where(np.isfinite(sig), -np.round(Fp[i - gf:i].sum(axis=0), 12), np.nan)
            W[k], lunghi, corti = nu.passo_banda(ct, U[k], sig, lunghi, corti)
        nu.ENTRA, nu.RESTA, nu.N_UNI = orig
        return W

    casi = {"originale": (0.20, 0.40, 7, 30, 100)}
    for f in (0.8, 0.9, 1.1, 1.2):
        casi[f"entra x{f}"] = (0.20 * f, 0.40, 7, 30, 100)
        casi[f"resta x{f}"] = (0.20, 0.40 * f, 7, 30, 100)
        casi[f"volatilita' x{f}"] = (0.20, 0.40, 7, int(round(30 * f)), 100)
        casi[f"universo x{f}"] = (0.20, 0.40, 7, 30, int(round(100 * f)))
    for gf in (6, 8):
        casi[f"funding {gf} giorni"] = (0.20, 0.40, gf, 30, 100)
    for nome, par in casi.items():
        t = time.time()
        W = pesi_con(*par)
        bb = dict(b)
        bb["W"] = W
        ric = conto_ricerca(bb, M, modo="limite")
        bot = simula(bb, M, base="tetto", chiusure="saltate", modo="limite")["df"]
        sr, sb = misure(settimane(ric["netto"])), misure(settimane(bot["r"]))
        out[nome] = {"parametri": par, "ricerca": {"sharpe": sr["sharpe"], "annuo": sr["annuo"], "per_anno": sr["per_anno"]},
                     "conto_250": {"sharpe": sb["sharpe"], "annuo": sb["annuo"], "discesa": sb["discesa_max"], "per_anno": sb["per_anno"]}}
        log(nome, f"{sr['sharpe']:.2f} {sb['sharpe']:.2f} ({time.time() - t:.0f}s)")
    salva("sensi", out)


def parte_esame():
    from research.programma6 import asticella as ast
    out = {}
    serie = {}
    for nome, f in {"G1 250 bot oggi (limite al tocco)": "serie_bot_oggi_tetto.pkl",
                    "G1 250 solo riduzione (limite al tocco)": "serie_solo_riduzione_chiusure_tetto.pkl",
                    "G1 250 bot oggi (tutto a mercato)": "serie_bot_oggi_tetto_mercato.pkl",
                    "G1 250 solo riduzione (tutto a mercato)": "serie_solo_riduzione_chiusure_tetto_mercato.pkl",
                    "G1 250 bot oggi (limite oltre 0,05%)": "serie_bot_oggi_tetto_oltre005.pkl",
                    "G1 250 solo riduzione (limite oltre 0,05%)": "serie_solo_riduzione_chiusure_tetto_oltre005.pkl",
                    "G1 250 bot oggi (27% a mercato)": "serie_bot_oggi_tetto_misto27.pkl",
                    "G1 ricerca senza minimi (limite al tocco)": "serie_ricerca_senza_minimi_composto.pkl"}.items():
        df = pickle.loads((CACHE / f).read_bytes())
        serie[nome] = settimane(df["r"])
    for quale, fino in (("mazzo alla prova 57", 57), ("mazzo di oggi", None)):
        base = ast.mazzo(None, fino_alla=fino)
        ris = {}
        for nome, s in serie.items():
            e = ast.esame({nome: s}, [nome], base=base)
            c = e["candidate"][nome]
            ris[nome] = {"sharpe": c["misure"]["sharpe"], "annuo": c["misure"]["annuo"], "settimane": c["misure"]["settimane"],
                         "probabilita": c["in_vigore"]["probabilita"], "t_robusto": c["in_vigore"]["t"],
                         "t_semplice": c["in_vigore"]["t_semplice"], "rapporto": c["in_vigore"]["rapporto"],
                         "ogni_anno_positivo": c["in_vigore"]["ogni_anno_positivo"], "esito": c["in_vigore"]["esito"],
                         "regola_fino_al_27_novembre": c["non_ufficiali"]["regola_fino_al_27_novembre"],
                         "famiglie": e["in_vigore"]["famiglie"], "in_v": e["in_vigore"]["in_v"]}
            log(quale, nome, f"{ris[nome]['probabilita']:.3f} t {ris[nome]['t_robusto']:.2f}")
        out[quale] = ris
    salva("esame", out)


# demo e paper di G1 giorno per giorno (equity a fine giorno, % del giorno): ops/results/0788-28nov-stato-ribilancio-1000.md (15-28
# novembre) e ops/results/0778-27nov-stato-ribilancio-1000.md (9-13 novembre), 0785-27nov-stato-tre-ore-dopo-il-riavvio.md (14 novembre)
DEMO_PAPER = {
    "2026-11-09": (0.88, 0.78), "2026-11-10": (-0.13, -0.22), "2026-11-11": (-1.25, -1.38), "2026-11-12": (0.08, 0.37),
    "2026-11-13": (1.69, 2.84), "2026-11-14": (2.26, 3.51), "2026-11-15": (-0.27, -0.58), "2026-11-16": (1.37, 1.49),
    "2026-11-17": (-0.79, -0.17), "2026-11-18": (-0.99, -1.50), "2026-11-19": (-1.11, -1.13), "2026-11-20": (1.88, 1.16),
    "2026-11-21": (-3.13, -3.07), "2026-11-22": (-2.09, -1.33), "2026-11-23": (1.71, 0.96), "2026-11-24": (-0.59, 0.23),
    "2026-11-25": (-1.39, -2.07), "2026-11-26": (2.87, 3.01), "2026-11-27": (2.69, 3.17), "2026-11-28": (0.70, 0.62)}


def parte_avanti():
    """Dal 5 ottobre all'ultimo giorno del pannello (dati dopo il periodo dichiarato: solo confronto, nessun giudizio) e dal 9 novembre:
    la ricerca, il conto a 250 USDT e a 1.000 USDT (il demo e' a 1.000 dall'8 novembre) contro il demo e il paper (ops/results)."""
    pan = pannello()
    fine = int(pan["t0"] + pan["close"].shape[0])           # escluso: l'ultimo giorno tenuto e' l'ultimo del pannello
    b = carica_base(fine)
    usati = [b["simboli"][j] for j in np.flatnonzero(np.abs(b["W"]).sum(axis=0) > 0)]
    M = matrici_ore(b, carica_ore(usati))
    out = {"ultimo_giorno": sc.data(int(b["giorni"][-1])),
           "funding_stimato_dopo_il_4_ottobre": int(b["stimato"][b["giorni"] >= FINE].sum())}
    k5 = int(np.searchsorted(b["giorni"], FINE))
    k9 = int(np.searchsorted(b["giorni"], sc.giorno(2026, 11, 9)))
    ric = conto_ricerca(b, M, modo="limite")["netto"]
    ric_m = conto_ricerca(b, M, modo="mercato")["netto"]
    serie = {}
    for nome, da in (("dal 5 ottobre", k5), ("dal 9 novembre", k9)):
        o = {"ricerca_limite": float(np.prod(1 + ric.iloc[da:].to_numpy()) - 1),
             "ricerca_mercato": float(np.prod(1 + ric_m.iloc[da:].to_numpy()) - 1), "giorni": int(len(ric) - da)}
        for cap in (250.0, 1000.0):
            for ch in ("saltate", "chiusure"):
                for modo in ("limite", "mercato"):
                    r = simula(b, M, capitale=cap, base="composto", chiusure=ch, modo=modo, da=da)
                    o[f"conto {int(cap)} {ch} {modo}"] = float(r["valore_finale"] / cap - 1)
                    serie[(nome, cap, ch, modo)] = r["df"]
        out[nome] = o
    d9 = serie[("dal 9 novembre", 250.0, "saltate", "limite")]
    d9k = serie[("dal 9 novembre", 1000.0, "saltate", "limite")]
    righe = {}
    for g in b["giorni"][k9:]:
        s = sc.data(int(g))
        dm, pp = DEMO_PAPER.get(s, (None, None))
        righe[s] = {"demo": dm, "paper": pp, "ricerca": round(100 * float(ric.loc[g]), 3),
                    "conto_250": round(100 * float(d9.loc[g, "r"]), 3), "conto_1000": round(100 * float(d9k.loc[g, "r"]), 3),
                    "saltati_250": int(d9.loc[g, "saltati"]), "voluti_250": int(d9.loc[g, "voluti"]),
                    "saltati_1000": int(d9k.loc[g, "saltati"])}
    out["giorni"] = righe
    comuni = [s for s, r in righe.items() if r["demo"] is not None]
    def comp(xs):
        return float(np.prod([1 + x / 100 for x in xs]) - 1)
    out["somme_sui_giorni_comuni"] = {"giorni": len(comuni), "da": comuni[0], "a": comuni[-1],
                                      **{k: comp([righe[s][k] for s in comuni]) for k in ("demo", "paper", "ricerca", "conto_250", "conto_1000")}}
    dd = np.array([righe[s]["demo"] - righe[s]["conto_1000"] for s in comuni])
    dp = np.array([righe[s]["paper"] - righe[s]["ricerca"] for s in comuni])
    d250 = np.array([righe[s]["conto_250"] - righe[s]["ricerca"] for s in comuni])
    out["differenze_al_giorno_punti"] = {"demo_meno_conto_1000": [float(dd.mean()), float(dd.std(ddof=1))],
                                         "paper_meno_ricerca": [float(dp.mean()), float(dp.std(ddof=1))],
                                         "conto_250_meno_ricerca": [float(d250.mean()), float(d250.std(ddof=1))]}
    # la partenza da vuoto del 9 novembre a 250 USDT: il primo giorno
    out["partenza_9_novembre_250"] = {"voluti": int(d9["voluti"].iloc[0]), "saltati": int(d9["saltati"].iloc[0]),
                                      "valore_saltato": float(d9["saltati_valore"].iloc[0]), "lorda": float(d9["lorda"].iloc[0]),
                                      "netta": float(d9["netta"].iloc[0]), "monete": int(d9["monete"].iloc[0])}
    salva("avanti", out)


def parte_buchi():
    """I giorni senza candela fra la prima e l'ultima di ogni moneta (26-28 febbraio e 1-2 aprile 2022, 1-5 febbraio 2023) presi
    dall'interfaccia pubblica di Binance (`www.binance.com/fapi/v1/klines`, candele da 1 giorno, la fonte di `buchi_archivio.py`),
    salvati nella cache (mai in `research/data/`); poi G1 rifatta con il pannello riempito in memoria (ricerca e conto a 250)."""
    import requests
    pan = pannello()
    pan = {k: (v.copy() if isinstance(v, np.ndarray) else v) for k, v in pan.items()}
    t0 = pan["t0"]
    C = pan["close"]
    gruppi = {"2022-02": [sc.giorno(2022, 2, d) for d in (26, 27, 28)], "2022-04": [sc.giorno(2022, 4, d) for d in (1, 2)],
              "2023-02": [sc.giorno(2023, 2, d) for d in range(1, 6)]}
    cartella = CACHE / "giorni_buchi"
    cartella.mkdir(exist_ok=True)
    riempiti = scaricati = errori = 0
    for j, s in enumerate(pan["simboli"]):
        ok = np.isfinite(C[:, j])
        idx = np.flatnonzero(ok)
        if not len(idx):
            continue
        for mese, gg in gruppi.items():
            manca = [g for g in gg if idx[0] <= g - t0 <= idx[-1] and not ok[g - t0]]
            if not manca:
                continue
            base = sc.simbolo_base(s)[0]
            f = cartella / f"{s}-{mese}.json"
            if not f.exists():
                try:
                    r = requests.get("https://www.binance.com/fapi/v1/klines", params={"symbol": base, "interval": "1d",
                                     "startTime": gg[0] * 86_400_000, "limit": len(gg)}, timeout=30)
                    r.raise_for_status()
                    f.write_text(r.text, encoding="utf-8")
                    scaricati += 1
                    time.sleep(0.15)
                except Exception:  # noqa: BLE001
                    errori += 1
                    continue
            for riga in json.loads(f.read_text(encoding="utf-8")):
                g = int(riga[0]) // 86_400_000
                tt = g - t0
                if g in manca and not np.isfinite(pan["close"][tt, j]):
                    pan["open"][tt, j], pan["high"][tt, j], pan["low"][tt, j], pan["close"][tt, j] = map(float, riga[1:5])
                    pan["quote_volume"][tt, j] = float(riga[7])
                    riempiti += 1
    giorni = np.arange(INIZIO, FINE, dtype=np.int64)
    idx = giorni - t0
    U = nu.universo_giorni(pan, idx)
    W, _, _ = nu.pesi(pan, idx, U, fisso=(1.0, 1.0))
    b0 = carica_base()
    usati = [b0["simboli"][j] for j in np.flatnonzero(np.abs(b0["W"]).sum(axis=0) > 0)]
    M = matrici_ore(b0, carica_ore(usati))
    b = dict(b0)
    b.update({"W": W, "U": U, "R": nu.ritorni_tenuta(pan["open"], pan["close"])[idx], "O": pan["open"][idx],
              "H": pan["high"][idx], "L": pan["low"][idx]})
    out = {"fonte": "www.binance.com/fapi/v1/klines 1d, nella cache", "file_scaricati_ora": scaricati, "errori": errori,
           "giorni_moneta_riempiti": riempiti}
    for nome, bb in (("prima", b0), ("dopo", b)):
        ric = conto_ricerca(bb, M, modo="limite")["netto"]
        bot = simula(bb, M, base="tetto", chiusure="saltate", modo="limite")["df"]["r"]
        sr, sb = misure(settimane(ric)), misure(settimane(bot))
        out[nome] = {"ricerca": {k: sr[k] for k in ("sharpe", "annuo", "discesa_max")},
                     "conto_250_bot_oggi": {k: sb[k] for k in ("sharpe", "annuo", "discesa_max")}}
    (CACHE / "pannello_riempito_W.pkl").write_bytes(pickle.dumps({"W": W, "R": b["R"], "O": b["O"], "H": b["H"], "L": b["L"], "U": U}))
    salva("buchi", out)


def parte_tempi():
    """Entrata all'istante della decisione contro un'ora dopo (apertura delle 01:00, tutto a mercato, rendimento da 01:00 a 01:00) e
    un giorno dopo (pesi di ieri), sulla ricerca e sul conto a 250 USDT del bot di oggi; i giorni sotto -5% (limite fisso del vecchio
    sistema, non applicato dal conto vero)."""
    b = carica_base()
    usati = [b["simboli"][j] for j in np.flatnonzero(np.abs(b["W"]).sum(axis=0) > 0)]
    M = matrici_ore(b, carica_ore(usati))
    out = {}
    P1 = M["O01"]
    with np.errstate(invalid="ignore", divide="ignore"):
        R1 = np.vstack([P1[1:] / P1[:-1] - 1, np.full((1, P1.shape[1]), np.nan)])
    b1 = dict(b)
    b1["R"] = np.where(np.isfinite(R1), R1, b["R"])
    b1["O"] = np.where(np.isfinite(P1), P1, b["O"])
    W1 = np.vstack([np.zeros((1, b["W"].shape[1])), b["W"][:-1]])
    b2 = dict(b)
    b2["W"] = W1
    for nome, bb, modo in (("alle 00:00 a mercato", b, "mercato"), ("alle 01:00 a mercato", b1, "mercato"),
                           ("un giorno dopo, limite al tocco", b2, "limite"), ("alle 00:00 limite al tocco", b, "limite")):
        ric = conto_ricerca(bb, M if modo == "limite" else None, modo=modo)["netto"]
        bot = simula(bb, M if modo == "limite" else None, base="tetto", chiusure="saltate", modo=modo)["df"]["r"]
        sr, sb = misure(settimane(ric)), misure(settimane(bot))
        out[nome] = {"ricerca": {"sharpe": sr["sharpe"], "annuo": sr["annuo"]}, "conto_250": {"sharpe": sb["sharpe"], "annuo": sb["annuo"]}}
        log(nome, f"{sr['sharpe']:.2f} {sb['sharpe']:.2f}")
    bot = simula(b, M, base="tetto", chiusure="saltate", modo="limite")["df"]
    out["giorni_sotto_-5%"] = {"conto_250": int((bot["r"] < -0.05).sum()),
                               "peggiori": {sc.data(int(g)): float(v) for g, v in bot["r"].nsmallest(5).items()}}
    salva("tempi", out)


def parte_esame_v():
    """Come `parte_esame` col mazzo alla prova 57, ma con la famiglia della candidata dentro V (domanda aperta di ASTICELLA.md,
    sezione 7; stesso calcolo di `audits/repro/prova168_2026-11-27.py`, `esame_con`)."""
    from research.programma6 import asticella as ast
    from research.programma6 import terza as te
    serie = {}
    for nome, f in {"G1 250 bot oggi (limite al tocco)": "serie_bot_oggi_tetto.pkl",
                    "G1 250 solo riduzione (limite al tocco)": "serie_solo_riduzione_chiusure_tetto.pkl",
                    "G1 250 bot oggi (tutto a mercato)": "serie_bot_oggi_tetto_mercato.pkl",
                    "G1 250 bot oggi (limite oltre 0,05%)": "serie_bot_oggi_tetto_oltre005.pkl",
                    "G1 ricerca senza minimi (limite al tocco)": "serie_ricerca_senza_minimi_composto.pkl"}.items():
        serie[nome] = settimane(pickle.loads((CACHE / f).read_bytes())["r"])
    base = ast.mazzo(None, fino_alla=57)
    out = {}
    for nome, s in serie.items():
        e = ast.esame({nome: s}, [nome], base=base)
        sr_, soli = dict(base[0]), list(base[1])
        sr_.update({nome: ast.periodo(s)})
        gr_b = ast._senza(e["gruppi"], sr_, ast.BOCCIATE_DAL_REVISORE)
        N = e["in_vigore"]["famiglie"]
        fam = next(g for g in gr_b if nome in g["membri"])
        v = [g["sharpe"] for g in gr_b if g is not fam and abs(g["sharpe"] * math.sqrt(g["settimane"] / 52)) <= 3] + [fam["sharpe"]]
        v += [float(x) for x in soli if abs(float(x) * math.sqrt(getattr(x, "settimane", 300) / 52)) <= 3]
        c = e["candidate"][nome]
        m = c["misure"]
        pv = te.sharpe_corretto(m["sharpe"], c["in_vigore"]["settimane_efficaci"], m["asimmetria"], m["curtosi"], v, 52, n_prove=N)
        out[nome] = {"probabilita_in_vigore": c["in_vigore"]["probabilita"], "probabilita_famiglia_in_v": pv,
                     "famiglia": {"membri": len(fam["membri"]), "sharpe": fam["sharpe"]}, "famiglie": N,
                     "controllo_13_ritardi": (c["non_ufficiali"]["controllo_13_ritardi"] or {}).get("probabilita"),
                     "anni_composti_positivi": c["non_ufficiali"].get("ogni_anno_positivo_composto")}
        log(nome, f"{c['in_vigore']['probabilita']:.3f} famiglia in V {pv:.3f}")
    salva("esame_v", out)


def parte_orario():
    """Lo stop sul conto ora per ora nei giorni in cui il limite prudente giornaliero va oltre il -35% dal massimo, o la chiusura oltre il
    -20%: le posizioni del giorno (bot di oggi, base "tetto", limite al tocco) con le candele da 1 ora (`esecuzione.ore_di`): (a) il
    valore alle chiusure orarie, (b) il limite prudente di ogni ora (lunghi al minimo e corti al massimo della stessa ora)."""
    from research.programma6 import esecuzione as es
    b = carica_base()
    usati = [b["simboli"][j] for j in np.flatnonzero(np.abs(b["W"]).sum(axis=0) > 0)]
    M = matrici_ore(b, carica_ore(usati))
    r0 = simula(b, M, base="tetto", chiusure="saltate", modo="limite")
    df = r0["df"]
    e = df["E"]
    inizio = e.shift(1).fillna(CAPITALE)
    # il massimo del conto (con il ritorno al capitale dopo un prelievo): lo rifa' il simulatore nei giorni registrati
    pg = df["peggio_nel_giorno"]
    giorni = set()
    r1 = simula(b, M, base="tetto", chiusure="saltate", modo="limite", posizioni_dei_giorni=set(int(g) for g in df.index))
    pos = r1["posizioni"]
    for g, (v, E, sp, mx) in pos.items():
        if (E * (1 + pg.loc[g]) / mx - 1 < -0.35) or (e.loc[g] / mx - 1 < -0.20):
            giorni.add(g)
    out = {"giorni_controllati": len(giorni)}
    cache_ore = {}
    righe = []
    for g in sorted(giorni):
        v, E, sp, mx = pos[g]
        js = np.flatnonzero(v != 0)
        vals_c = np.zeros(24)
        vals_p = np.zeros(24)
        mancano = 0
        for j in js:
            s = b["simboli"][j]
            if s not in cache_ore:
                cache_ore[s] = es.ore_di(s)
            z = cache_ore[s]
            o = b["O"][int(g - b["giorni"][0]), j]
            ore_g = z.reindex(np.arange(g * 24, g * 24 + 24)) if not z.empty else None
            if ore_g is None or ore_g["close"].isna().any():
                mancano += 1
                continue
            c = ore_g["close"].to_numpy() / o - 1
            hi = np.maximum.accumulate(ore_g["high"].to_numpy()) / o - 1
            lo = np.minimum.accumulate(ore_g["low"].to_numpy()) / o - 1
            h1 = ore_g["high"].to_numpy() / o - 1
            l1 = ore_g["low"].to_numpy() / o - 1
            vals_c += v[j] * c
            vals_p += np.where(v[j] < 0, v[j] * h1, v[j] * l1)
            _ = (hi, lo)
        dd_c = (E - sp + vals_c) / mx - 1
        dd_p = (E - sp + vals_p) / mx - 1
        righe.append({"giorno": sc.data(int(g)), "inizio_dal_massimo": float(E / mx - 1), "fine_dal_massimo": float(e.loc[g] / mx - 1),
                      "peggiore_chiusura_oraria": float(dd_c.min()), "ora": int(np.argmin(dd_c)),
                      "peggiore_prudente_orario": float(dd_p.min()), "ora_prudente": int(np.argmin(dd_p)),
                      "prudente_giornaliero": float((E * (1 + pg.loc[g])) / mx - 1), "monete_senza_ore": mancano, "monete": int(len(js))})
    righe.sort(key=lambda x: x["peggiore_prudente_orario"])
    out["giorni"] = righe
    out["oltre_-35%_chiusure_orarie"] = [r["giorno"] for r in righe if r["peggiore_chiusura_oraria"] < -0.35]
    out["oltre_-35%_prudente_orario"] = [r["giorno"] for r in righe if r["peggiore_prudente_orario"] < -0.35]
    salva("orario", out)


def parte_discese_partenze():
    """Da ogni partenza (ogni 7 giorni, conto vuoto, 250 USDT, base "tetto") la discesa peggiore dal massimo del conto alle chiusure
    giornaliere (il massimo torna al capitale a ogni capitale nuovo, come `_fissa_massimo`): quanto manca allo stop del -35%."""
    b = carica_base()
    usati = [b["simboli"][j] for j in np.flatnonzero(np.abs(b["W"]).sum(axis=0) > 0)]
    M = matrici_ore(b, carica_ore(usati))
    T = b["W"].shape[0]
    out = {}
    for nome, kv in {"bot_oggi | limite": dict(chiusure="saltate", modo="limite"), "bot_oggi | mercato": dict(chiusure="saltate", modo="mercato"),
                     "solo_riduzione | limite": dict(chiusure="chiusure", modo="limite")}.items():
        peggiori = []
        for da in range(0, T - 30, 7):
            r = simula(b, M, base="tetto", da=da, **kv)
            E = r["df"]["E"].to_numpy()
            # il massimo riparte dal capitale dopo ogni prelievo: si ricostruisce dai salti all'indietro oltre il tetto
            mx, dd = CAPITALE, 0.0
            prima = CAPITALE
            for x in E:
                if prima > TETTO_VALORE:
                    mx = CAPITALE
                mx = max(mx, x)
                dd = min(dd, x / mx - 1)
                prima = x
            peggiori.append((sc.data(int(b["giorni"][da])), dd))
        v = np.array([x[1] for x in peggiori])
        out[nome] = {"partenze": len(v), "peggiore": float(v.min()), "partenza_peggiore": peggiori[int(v.argmin())][0],
                     "quantili_5_50_95": [float(np.percentile(v, q)) for q in (5, 50, 95)],
                     "oltre_-30%": int((v < -0.30).sum()), "oltre_-25%": int((v < -0.25).sum())}
        log(nome, out[nome])
    salva("discese_partenze", out)


def parte_rumore():
    """Quanto e' rumoroso il conto con i minimi: capitale fisso da 200 a 400 USDT e partenze spostate di 0-6 giorni (stesse settimane
    dal 18 gennaio 2021), bot di oggi e chiusure «solo riduzione», limite al tocco."""
    b = carica_base()
    usati = [b["simboli"][j] for j in np.flatnonzero(np.abs(b["W"]).sum(axis=0) > 0)]
    M = matrici_ore(b, carica_ore(usati))
    dal = sc.giorno(2021, 1, 18)
    out = {"capitali": {}, "partenze": {}}
    for cap in (200.0, 225.0, 250.0, 275.0, 300.0, 350.0, 400.0, 600.0, 1000.0):
        o = {}
        for ch in ("saltate", "chiusure"):
            r = simula(b, M, capitale=cap, base="fisso", chiusure=ch, modo="limite")["df"]["r"]
            m = misure(settimane(r[r.index >= dal]))
            o[ch] = {"sharpe": m["sharpe"], "annuo": m["annuo"], "min_anno": min(m["per_anno"].values())}
        out["capitali"][int(cap)] = o
        log(int(cap), {k: round(v["sharpe"], 2) for k, v in o.items()})
    for off in range(7):
        o = {}
        for ch in ("saltate", "chiusure"):
            for base in ("fisso", "tetto"):
                r = simula(b, M, capitale=250.0, base=base, chiusure=ch, modo="limite", da=off)["df"]["r"]
                m = misure(settimane(r[r.index >= dal]))
                o[f"{ch} {base}"] = {"sharpe": m["sharpe"], "annuo": m["annuo"]}
        out["partenze"][sc.data(int(b["giorni"][off]))] = o
        log(off, {k: round(v["sharpe"], 2) for k, v in o.items()})
    ric = conto_ricerca(b, M, modo="limite")["netto"]
    out["ricerca_dal_18_gennaio"] = misure(settimane(ric[ric.index >= dal]))["sharpe"]
    salva("rumore", out)


def parte_parita_ricerca():
    """I pesi di G1 del codice della prova 57 (`programma7/prima.py` con le funzioni del programma 6, come `parita_bot.ricerca`) contro
    quelli del nucleo riscritto, sul pannello di oggi."""
    from research.programma6 import ottava as ot, sesta as se, terza as te, ventiquattresima as vq
    from research.programma7 import prima as pr
    pan = pannello()
    b = carica_base()
    ps = te.pannello_settimane(pan, log=lambda x: None, indicatori_si=False)
    Ud = pr.universo_del_giorno(b["giorni"], ps["lunedi"], ps["U"])
    sig = ot.sigma_30(pan, b["idx"])
    Wr = vq.pesi_banda(np.where(np.isfinite(sig), -se.funding_7(pan, b["idx"]), np.nan), Ud, sig)
    out = {"universo_giorni_diversi": int((Ud != b["U"]).any(axis=1).sum()), "pesi_diff_max": float(np.abs(Wr - b["W"]).max()),
           "giorni_con_pesi_diversi": int((np.abs(Wr - b["W"]) > 1e-12).any(axis=1).sum())}
    log(out)
    salva("parita_ricerca", out)


def parte_mancanti():
    """(a) Quanto del peso voluto manca sul conto a 250 USDT del bot di oggi (base "tetto", limite al tocco), moneta per moneta: le
    monete con il minimo di 20 o 50 USDT (ETH, BCH, LTC, ETC, LINK, BTC) e le altre; (b) da ogni partenza (ogni 7 giorni) quanti giorni
    servono perche' il conto passi i 600 USDT (oltre, `conto_vero.py:127`: niente ordini nuovi finche' non c'e' un capitale nuovo)."""
    b = carica_base()
    usati = [b["simboli"][j] for j in np.flatnonzero(np.abs(b["W"]).sum(axis=0) > 0)]
    M = matrici_ore(b, carica_ore(usati))
    giorni = set(int(g) for g in b["giorni"])
    r = simula(b, M, base="tetto", chiusure="saltate", modo="limite", posizioni_dei_giorni=giorni)
    pos = r["posizioni"]
    W = b["W"]
    S = W.shape[1]
    voluto = np.zeros(S)
    tenuto = np.zeros(S)
    stesso_lato = np.zeros(S)
    for k, g in enumerate(b["giorni"]):
        v, E, _, _ = pos[int(g)]
        x = v / E
        voluto += np.abs(W[k])
        tenuto += np.abs(x)
        stesso_lato += np.minimum(np.abs(W[k]), np.abs(x)) * (np.sign(W[k]) == np.sign(x))
    vmin, _, _, _ = carica_filtri(b["simboli"])
    T = len(b["giorni"])
    gruppi = {"minimo 20-50 USDT": vmin >= 20, "minimo 5 USDT": vmin < 20}
    out = {"per_gruppo": {n: {"peso_voluto_medio": float(voluto[m].sum() / T), "peso_tenuto_medio": float(tenuto[m].sum() / T),
                              "coperto_dal_voluto": float(stesso_lato[m].sum() / max(1e-12, voluto[m].sum()))} for n, m in gruppi.items()}}
    peggiori = np.argsort(-(voluto - stesso_lato))[:12]
    out["monete_piu_scoperte"] = [{"simbolo": b["simboli"][j], "minimo": float(vmin[j]), "peso_voluto_medio": float(voluto[j] / T),
                                   "coperto": float(stesso_lato[j] / max(1e-12, voluto[j]))} for j in peggiori]
    # giorni per arrivare a 600 USDT da 250 (conto che si compone, senza tetto)
    giorni_600 = []
    for da in range(0, T - 30, 7):
        E = simula(b, M, base="composto", chiusure="saltate", modo="limite", da=da)["df"]["E"].to_numpy()
        sopra = np.flatnonzero(E > TETTO_VALORE)
        giorni_600.append(int(sopra[0]) + 1 if len(sopra) else None)
    arrivati = [x for x in giorni_600 if x is not None]
    out["giorni_fino_a_600"] = {"partenze": len(giorni_600), "arrivate": len(arrivati),
                                "quantili_10_50_90": [float(np.percentile(arrivati, q)) for q in (10, 50, 90)] if arrivati else None}
    log(out["per_gruppo"], out["giorni_fino_a_600"])
    salva("mancanti", out)


def parte_esame_costi():
    """L'esame in vigore (mazzo alla prova 57 e mazzo di oggi) per il conto a 250 USDT del bot di oggi con il limite che deve passare
    il prezzo dello 0,10% e con il 58% del valore a mercato (la quota delle esecuzioni del demo dal 23 al 28 novembre)."""
    from research.programma6 import asticella as ast
    b = carica_base()
    usati = [b["simboli"][j] for j in np.flatnonzero(np.abs(b["W"]).sum(axis=0) > 0)]
    M = matrici_ore(b, carica_ore(usati))
    serie = {}
    for nome, kc in {"G1 250 bot oggi (limite oltre 0,10%)": dict(modo="limite", oltre=0.001),
                     "G1 250 bot oggi (58% a mercato)": dict(modo="misto", oltre=0.0, quota_mercato=0.58),
                     "G1 250 solo riduzione (limite oltre 0,10%)": dict(modo="limite", oltre=0.001, chiusure="chiusure")}.items():
        kv = {"base": "tetto", "chiusure": kc.pop("chiusure", "saltate")}
        serie[nome] = settimane(simula(b, M, **kv, **kc)["df"]["r"])
    out = {}
    for quale, fino in (("mazzo alla prova 57", 57), ("mazzo di oggi", None)):
        base = ast.mazzo(None, fino_alla=fino)
        out[quale] = {}
        for nome, s in serie.items():
            c = ast.esame({nome: s}, [nome], base=base)["candidate"][nome]
            out[quale][nome] = {"sharpe": c["misure"]["sharpe"], "probabilita": c["in_vigore"]["probabilita"], "t_robusto": c["in_vigore"]["t"],
                                "ogni_anno_positivo": c["in_vigore"]["ogni_anno_positivo"], "esito": c["in_vigore"]["esito"],
                                "per_anno": c["in_vigore"]["per_anno"]}
            log(quale, nome, f"{c['in_vigore']['probabilita']:.3f}")
    salva("esame_costi", out)


PARTI = {"base": parte_base, "ore": parte_ore, "dati": parte_dati, "taglio": parte_taglio, "parita": parte_parita,
         "conto": parte_conto, "polvere": parte_polvere, "rischio": parte_rischio, "misure": parte_misure, "sensi": parte_sensi,
         "esame": parte_esame, "avanti": parte_avanti, "buchi": parte_buchi, "tempi": parte_tempi, "esame_v": parte_esame_v, "orario": parte_orario, "discese_partenze": parte_discese_partenze, "rumore": parte_rumore, "parita_ricerca": parte_parita_ricerca, "mancanti": parte_mancanti, "esame_costi": parte_esame_costi}

if __name__ == "__main__":
    t0 = time.time()
    PARTI[A.parte]()
    log(f"fatto in {time.time() - t0:.0f}s")
