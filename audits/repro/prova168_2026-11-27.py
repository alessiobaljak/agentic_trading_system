#!/usr/bin/env python3
"""Audit della prova 168 (G1, G11, G1 neutra e F5 insieme sullo stesso conto; regole `research/programma7/CENTOSESTA.md`), 27 nov 2026.

Uso (dalla radice del repository):
    python3 -I audits/repro/prova168_2026-11-27.py <parte> [--codice DIR] [--cache DIR] [--etichetta X]
Parti: `base` per prima (pesi, candele orarie e conti nella cache), poi `esame`, `costi`, `conto`, `rischio`, `misure`, `sensi`,
`taglio`, `dati`, `buchi`, `avanti`. Esiti in `audits/repro/prova168_2026-11-27_esito_<parte><etichetta>.json`.

Non chiama mai `centosesta.esegui` ne' `centosesta.avanti` (scrivono in `research/` e nel registro delle varianti): i passi sono
ricopiati qui dalle righe 152-226 di `research/programma7/centosesta.py`. Non scrive fuori da `audits/` e dalla cartella di cache.
Con `--codice` si prova il codice di un altro commit (cartella fatta con `git archive`, con `research/data` collegata a quella vera).
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
ARG.add_argument("--cache", required=True)
ARG.add_argument("--etichetta", default="")
ARG.add_argument("--pannello", default="")
A = ARG.parse_args()
CODICE = Path(A.codice)
sys.path.insert(0, str(CODICE))
CACHE = Path(A.cache)
CACHE.mkdir(parents=True, exist_ok=True)

from research.programma6 import asticella as ast  # noqa: E402
from research.programma6 import cinquantaseiesima as cs  # noqa: E402
from research.programma6 import cinquantunesima as cu  # noqa: E402
from research.programma6 import esecuzione as es  # noqa: E402
from research.programma6 import ottava as ot  # noqa: E402
from research.programma6 import seconda as sc  # noqa: E402
from research.programma6 import sesta as se  # noqa: E402
from research.programma6 import terza as te  # noqa: E402
from research.programma6 import ventiquattresima as vq  # noqa: E402
from research.programma6.motore import MAKER  # noqa: E402
from research.programma7 import prima as pr  # noqa: E402
from research.programma7 import tredicesima as t13  # noqa: E402
from research.programma7 import ventiquattresima as f5n  # noqa: E402

if A.pannello:                       # un pannello congelato in una cartella temporanea (mai in research/data)
    sc.PANNELLO = Path(A.pannello)

P7 = RADICE / "research" / "programma7"
P6 = RADICE / "research" / "programma6"
SALVATE = {"G1": P7 / "risultati_prima" / "settimane_G1.csv.gz", "G11": P7 / "risultati_tredicesima" / "settimane_G11.csv.gz",
           "G1N": P7 / "risultati_ventiseiesima" / "settimane_G1N.csv.gz",
           "F5": P6 / "risultati_controllo_parita" / "settimane_F5.csv.gz",
           "A": P7 / "risultati_centosesta" / "settimane_A.csv.gz", "B": P7 / "risultati_centosesta" / "settimane_B.csv.gz"}
FILTRI = RADICE / "bot" / "portafoglio" / "filtri_conto_vero.json"


def log(*a):
    print(time.strftime("%H:%M:%S"), *a, flush=True)


def salva(parte: str, out: dict) -> None:
    f = QUI / f"prova168_2026-11-27_esito_{parte}{A.etichetta}.json"
    f.write_text(json.dumps(out, ensure_ascii=False, indent=1, default=float), encoding="utf-8")
    log("scritto", f.name)


def leggi_salvata(n: str) -> pd.DataFrame:
    d = pd.read_csv(SALVATE[n], index_col=0)
    return d[(d.index >= se.INIZIO) & (d.index < pr.FINE)]


# ---------------------------------------------------------------------------------------------------------------------------------
# i pesi delle quattro (passi di `centosesta.esegui`, righe 165-172), con i parametri variabili per la sensibilita'
# ---------------------------------------------------------------------------------------------------------------------------------

def funding_n(pan, idx, n):
    if n == 7:
        return se.funding_7(pan, idx)
    Fc = np.vstack([np.zeros((1, pan["funding"].shape[1])), np.cumsum(pan["funding"], axis=0)])
    return np.round(Fc[idx] - Fc[idx - n], 12)


def sigma_n(pan, idx, n):
    if n == 30:
        return ot.sigma_30(pan, idx)
    C = pan["close"]
    with np.errstate(all="ignore"):
        r = np.vstack([np.full((1, C.shape[1]), np.nan), C[1:] / C[:-1] - 1])
    out = np.full((len(idx), C.shape[1]), np.nan)
    minimo = int(round(20 * n / 30))
    for k, m in enumerate(idx):
        f = r[max(0, m - n): m]
        cnt = np.isfinite(f).sum(axis=0)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", RuntimeWarning)
            sd = np.nanstd(f, axis=0, ddof=1)
        out[k] = np.where((cnt >= minimo) & (sd > 0), sd, np.nan)
    return out


def fresco(pan, idx, U, n):
    if n == 7:
        return t13.segnale_fresco(pan, idx, U)
    f7 = -funding_n(pan, idx, n)
    f1 = -np.round(pan["funding"][idx - 1], 12)
    Z = np.stack([f7, f1], axis=2)
    ok = np.isfinite(Z)
    Rk = te.ranghi(np.where(ok, Z, np.nan), U)
    nn = ok.sum(axis=2)
    with np.errstate(all="ignore"):
        s = np.where(ok, Rk, 0.0).sum(axis=2) / nn
    return np.where(ok.all(axis=2), s, np.nan)


def pesi_quattro(pan, entra=0.20, resta=0.40, gf=7, gs=30, gb=90, n_uni=100, ps=None):
    if ps is None:
        ps = te.pannello_settimane(pan, log=lambda x: None, indicatori_si=False, a=n_uni)
    giorni = np.arange(se.INIZIO, pr.FINE, dtype=np.int64)
    idx = giorni - pan["t0"]
    Ud = pr.universo_del_giorno(giorni, ps["lunedi"], ps["U"])
    sig = sigma_n(pan, idx, gs)
    vecchi = (vq.ENTRA, vq.RESTA, f5n.GIORNI_BETA, f5n.MIN_BETA)
    vq.ENTRA, vq.RESTA = entra, resta
    f5n.GIORNI_BETA, f5n.MIN_BETA = gb, int(round(45 * gb / 90))
    try:
        W1 = vq.pesi_banda(np.where(np.isfinite(sig), -funding_n(pan, idx, gf), np.nan), Ud, sig)
        W11 = vq.pesi_banda(np.where(np.isfinite(sig), fresco(pan, idx, Ud, gf), np.nan), Ud, sig)
        beta = f5n.beta_delle_monete(pan, Ud, idx)
        WN = f5n.scala_neutra(W1, beta)[0]
        lun = ps["lunedi"] - pan["t0"]
        sg = sigma_n(pan, lun, gs)
        Wt = vq.pesi_banda(np.where(np.isfinite(sg), -funding_n(pan, lun, gf), np.nan), ps["U"], sg)
    finally:
        vq.ENTRA, vq.RESTA, f5n.GIORNI_BETA, f5n.MIN_BETA = vecchi
    W5 = pr.universo_del_giorno(giorni, ps["lunedi"], Wt)
    return {"G1": W1, "G11": W11, "G1N": WN, "F5g": W5, "Wt": Wt, "B": (W1 + W11 + WN + W5) / 4, "ps": ps, "giorni": giorni,
            "idx": idx, "Ud": Ud}


# ---------------------------------------------------------------------------------------------------------------------------------
# candele orarie delle 00:00 e delle 01:00 di ogni giorno (`esecuzione.ore_di`, come `cinquantaseiesima.spese_a_limite`)
# ---------------------------------------------------------------------------------------------------------------------------------

def carica_ore(pan, giorni, usati) -> dict:
    f = CACHE / "ore_168.pkl"
    if f.exists():
        with open(f, "rb") as h:
            H = pickle.load(h)
        if set(usati) <= set(H["fatti"]):
            return H
    else:
        H = {k: np.full((len(giorni), len(pan["simboli"])), np.nan) for k in ("O0", "H0", "L0", "O1")}
        H["ok"] = np.zeros((len(giorni), len(pan["simboli"])), bool)
        H["fatti"] = []
    ore0, ore1 = giorni * 24, giorni * 24 + 1
    for n, j in enumerate(usati):
        if j in H["fatti"]:
            continue
        b = es.ore_di(pan["simboli"][j])
        H["fatti"].append(j)
        if b.empty:
            continue
        b = b[~b.index.duplicated(keep="last")]
        x0 = b.reindex(ore0)
        x1 = b.reindex(ore1)
        H["O0"][:, j], H["H0"][:, j], H["L0"][:, j] = x0["open"].to_numpy(), x0["high"].to_numpy(), x0["low"].to_numpy()
        H["O1"][:, j] = x1["open"].to_numpy()
        H["ok"][:, j] = np.isfinite(x0[["open", "high", "low", "close"]].to_numpy()).all(axis=1) & \
            np.isfinite(x1[["open", "high", "low", "close"]].to_numpy()).all(axis=1)
        if n % 50 == 0:
            log(f"ore {n}/{len(usati)}")
    with open(f, "wb") as h:
        pickle.dump(H, h)
    return H


def tasso(D, H, costo, oltre=0.0, modo="limite"):
    """Il costo per unita' di ogni variazione (giorni x monete) come `cinquantaseiesima.costo_limite`: limite all'apertura delle 00:00
    per un'ora, eseguito se il minimo (chi compra) o il massimo (chi vende) passano l'apertura di almeno ``oltre``; altrimenti a
    mercato alle 01:00 con il movimento contro; senza candele orarie, a mercato. ``modo`` "mercato": tutto a mercato."""
    if modo == "mercato":
        return np.broadcast_to(costo[None, :], D.shape), np.zeros(D.shape, bool)
    if modo.startswith("misto"):
        # una quota ``q`` del valore a mercato (il demo di G1: 27% a regime, 60% alla partenza da vuoto; gate2, 12 novembre), il
        # resto come la ricerca (limite al tocco): media dei due costi per unita'
        q = float(modo[5:])
        t0_, preso0 = tasso(D, H, costo, 0.0, "limite")
        return (1 - q) * t0_ + q * costo[None, :], preso0
    O0, H0, L0, O1, ok = H["O0"], H["H0"], H["L0"], H["O1"], H["ok"]
    compra = D > 0
    with np.errstate(invalid="ignore", divide="ignore"):
        preso = np.where(compra, L0 < O0 * (1 - oltre), H0 > O0 * (1 + oltre))
        contro = np.where(compra, O1 / O0 - 1, 1 - O1 / O0)
    t = np.where(ok & preso, MAKER, np.where(ok, costo[None, :] + np.nan_to_num(contro), costo[None, :]))
    return t, ok & preso


def conto(W, R, F, costo, giorni, H, oltre=0.0, modo="limite"):
    """`centosesta.conto_giorni` con le spese vettoriali (uguali a `cs.spese_a_limite` con ``oltre`` 0, controllato in `base`)."""
    g = te.conto(W, R, F, costo)
    D = cu.variazioni(W, R)
    t, preso = tasso(D, H, costo, oltre, modo)
    nz = np.abs(D) > 1e-9
    g["spese"] = (np.abs(D) * t * nz).sum(axis=1)
    g["netto"] = g["lordo"] - g["spese"] - g["funding"]
    g["netto_doppio"] = g["lordo"] - 2 * g["spese"] - g["funding"]
    return g, pr.per_settimana(g, giorni), int(nz.sum()), int((nz & preso).sum())


def _anni(x: pd.Series):
    return pd.to_datetime(x.index.to_numpy() * 86400, unit="s").year


def per_anno(x: pd.Series) -> dict:
    """Come `asticella.per_anno` (copiata: il codice del commit della prova non l'ha)."""
    return {int(a): float(v * 52) for a, v in x.groupby(_anni(x)).mean().items()}


def per_anno_composto(x: pd.Series) -> dict:
    return {int(a): float(v) for a, v in ((1 + x).groupby(_anni(x)).prod() - 1).items()}


def rapporto_robusto(x, ritardi: int = 4) -> float:
    """Come `asticella.rapporto_robusto` (Newey e West, pesi di Bartlett), copiata per il codice del commit della prova."""
    v = np.asarray(pd.Series(x, dtype=float).dropna(), dtype=float)
    u = v - v.mean()
    n = len(u)
    lunga = float(u @ u) / n
    for k in range(1, min(int(ritardi), n - 1) + 1):
        lunga += 2.0 * (1.0 - k / (ritardi + 1.0)) * float(u[k:] @ u[:-k]) / n
    return float(v.var() / lunga) if lunga > 0 and v.var() > 0 else 1.0


def numeri(x: pd.Series) -> dict:
    n = te.numeri_settimana(x)
    v = x.to_numpy(float)
    giu = v[v < 0]
    dd = np.sqrt((np.minimum(v, 0) ** 2).mean())
    n["sortino"] = float(v.mean() / dd * math.sqrt(52)) if dd > 0 else 0.0
    n["per_anno"] = per_anno(x)
    n["per_anno_composto"] = per_anno_composto(x)
    n["t_semplice"] = n["sharpe"] * math.sqrt(len(v) / 52)
    r = rapporto_robusto(x, 4)
    n["rapporto_robusto"], n["t_robusto"] = r, n["sharpe"] * math.sqrt(len(v) * r / 52)
    n["settimane_negative"] = int(len(giu))
    return n


def breve(n: dict) -> dict:
    return {k: (round(v, 5) if isinstance(v, float) else v) for k, v in n.items()
            if k in ("settimane", "annuo", "sharpe", "discesa_max", "t_semplice", "t_robusto", "rapporto_robusto", "sortino")}


def carica_base() -> dict:
    with open(CACHE / "base_168.pkl", "rb") as h:
        return pickle.load(h)


# ---------------------------------------------------------------------------------------------------------------------------------
# base: rifare la prova e confrontarla con le serie pubblicate
# ---------------------------------------------------------------------------------------------------------------------------------

def parte_base():
    pan = sc.pannello()
    out = {"pannello": {"primo": sc.data(pan["t0"]), "ultimo": sc.data(pan["t0"] + pan["close"].shape[0] - 1),
                        "monete": len(pan["simboli"])}, "codice": str(CODICE)}
    P = pesi_quattro(pan)
    ps, giorni, idx = P["ps"], P["giorni"], P["idx"]
    R = sc.rendimenti(pan)[idx]
    F = np.nan_to_num(pan["funding"][idx])
    costo = sc.costi_moneta(pan["simboli"])
    btc = pd.Series(ps["R"][:, ps["simboli"].index("BTCUSDT")], index=ps["lunedi"])
    log("pesi fatti")
    # le 120 monete di ogni lunedi' (per la sensibilita') e quelle tenute: candele orarie
    ps120 = te.pannello_settimane(pan, log=lambda x: None, indicatori_si=False, a=120)
    U120 = pr.universo_del_giorno(giorni, ps120["lunedi"], ps120["U"])
    usati = sorted(set(np.flatnonzero(np.abs(P["B"]).sum(axis=0) > 0).tolist()) | set(np.flatnonzero(U120.any(axis=0)).tolist()))
    H = carica_ore(pan, giorni, usati)
    log("ore fatte")
    serie = {}
    for n in ("G1", "G11", "G1N", "B"):
        g, s, nt, nl = conto(P[n], R, F, costo, giorni, H)
        serie[n] = s
        out[f"ordini_{n}"] = {"variazioni": nt, "a_limite": nl}
        if n == "B":
            gB = g
    d5 = te.conto(P["Wt"], ps["R"], ps["F"], costo)
    d5.index = ps["lunedi"]
    serie["F5"] = d5[(d5.index >= se.INIZIO) & (d5.index < pr.FINE)]
    col = list(pr.COLONNE)
    serie["A"] = sum(serie[n][col] for n in ("G1", "G11", "G1N", "F5")) / 4
    serie["A"]["monete"] = sum(serie[n]["monete"] for n in ("G1", "G11", "G1N", "F5"))
    # le spese ufficiali di B (la funzione della prova) contro quelle vettoriali
    sp_uff, nt_uff, nl_uff, ns_uff = cs.spese_a_limite(P["B"], R, giorni, pan["simboli"], costo)
    out["controllo_spese_B"] = {"diff_max_giorno": float(np.abs(sp_uff - gB["spese"].to_numpy()).max()),
                                "ufficiali": [int(nt_uff), int(nl_uff), int(ns_uff)], "vettoriali": out["ordini_B"],
                                "spese_annue_ufficiali": float(sp_uff.sum() / len(giorni) * 365)}
    log("controllo spese fatto", out["controllo_spese_B"])
    # confronto con le serie pubblicate
    for n in ("G1", "G11", "G1N", "F5", "A", "B"):
        old = leggi_salvata(n)
        new = serie[n]
        c = old.index.intersection(new.index)
        dn = (old.loc[c, "netto"] - new.loc[c, "netto"]).abs()
        top = dn.sort_values(ascending=False).head(5)
        out[f"confronto_{n}"] = {"settimane": [int(len(old)), int(len(new)), int(len(c))],
                                 "diverse_oltre_1e-9": int((dn > 1e-9).sum()), "diff_max": float(dn.max()),
                                 "peggiori": {sc.data(int(i)): [float(old.loc[i, "netto"]), float(new.loc[i, "netto"])] for i in top.index},
                                 "pubblicata": breve(numeri(old["netto"])), "rifatta_oggi": breve(numeri(new["netto"]))}
        for colonna in ("lordo", "spese", "funding"):
            out[f"confronto_{n}"][f"diff_max_{colonna}"] = float((old.loc[c, colonna] - new.loc[c, colonna]).abs().max())
    # A pubblicata contro A rifatta dalle quattro serie salvate (deve essere identica)
    q = {n: leggi_salvata(n) for n in ("G1", "G11", "G1N", "F5")}
    a2 = sum(q[n][col] for n in q) / 4
    out["A_dalle_salvate"] = {"diff_max": float((a2["netto"] - leggi_salvata("A")["netto"]).abs().max())}
    # i numeri della prova (terza.esame) sulle serie pubblicate, per riprodurre la tabella
    e = json.loads((P7 / "risultati_centosesta" / "esame.json").read_text())
    for n in ("A", "B"):
        ee = te.esame(leggi_salvata(n), btc, inizio=se.INIZIO, anni_pieni=se.ANNI_PIENI)
        out[f"esame_terza_{n}"] = {"rifatto": {k: ee["intero"][k] for k in ("sharpe", "annuo", "discesa_max")} | {"spese_annue": ee["spese_annue"]},
                                   "pubblicato": {k: e["esame"][n]["intero"][k] for k in ("sharpe", "annuo", "discesa_max")} | {"spese_annue": e["esame"][n]["spese_annue"]}}
    # giorno peggiore
    gs = pd.read_csv(P7 / "risultati_centosesta" / "giorni_B.csv.gz")
    out["giorni_B"] = {"pubblicato_peggiore": [sc.data(int(gs.loc[gs["netto"].idxmin(), "giorno"])), float(gs["netto"].min())],
                       "rifatto_peggiore": [sc.data(int(giorni[int(np.argmin(gB["netto"].to_numpy()))])), float(gB["netto"].min())],
                       "diff_max_netto": float(np.abs(gs["netto"].to_numpy() - gB["netto"].to_numpy()).max()),
                       "giorni_diversi_oltre_1e-6": int((np.abs(gs["netto"].to_numpy() - gB["netto"].to_numpy()) > 1e-6).sum())}
    base = {"P": {k: v for k, v in P.items() if k != "ps"}, "ps": {k: ps[k] for k in ("lunedi", "U", "R", "F")}, "R": R, "F": F,
            "costo": costo, "btc": btc, "serie": serie, "gB": gB, "simboli": pan["simboli"], "t0": pan["t0"]}
    with open(CACHE / "base_168.pkl", "wb") as h:
        pickle.dump(base, h)
    salva("base", out)


# ---------------------------------------------------------------------------------------------------------------------------------
# esame: l'esame in vigore (asticella.esame), la regola scritta prima, la famiglia della candidata in V, i costi del bot
# ---------------------------------------------------------------------------------------------------------------------------------

def esame_con(nuove: dict, base_mazzo, famiglia_in_v=False) -> dict:
    e = ast.esame(nuove=nuove, candidate=list(nuove), base=base_mazzo)
    out = {}
    for n, c in e["candidate"].items():
        out[n] = {"probabilita_in_vigore": c["in_vigore"]["probabilita"], "t_robusto": c["in_vigore"]["t"],
                  "settimane_efficaci": c["in_vigore"]["settimane_efficaci"], "esito": c["in_vigore"]["esito"],
                  "regola_fino_al_27_novembre": c["non_ufficiali"]["regola_fino_al_27_novembre"]["probabilita"],
                  "controllo_13": (c["non_ufficiali"]["controllo_13_ritardi"] or {}).get("probabilita"),
                  "anni_composti_positivi": c["non_ufficiali"].get("ogni_anno_positivo_composto"),
                  "sharpe": c["misure"]["sharpe"], "gruppo_n": len(c["gruppo"])}
    out["_mazzo"] = {"famiglie": e["in_vigore"]["famiglie"], "in_v": e["in_vigore"]["in_v"], "dev_v": e["in_vigore"]["deviazione_v"]}
    if famiglia_in_v:
        # la V in vigore ma con dentro la famiglia della candidata (domanda aperta di ASTICELLA.md, sezione 7)
        serie, soli = dict(base_mazzo[0]), list(base_mazzo[1])
        serie.update({n: ast.periodo(s) for n, s in nuove.items()})
        gr = e["gruppi"]
        gr_b = ast._senza(gr, serie, ast.BOCCIATE_DAL_REVISORE)
        N = e["in_vigore"]["famiglie"]
        for n in nuove:
            fam = next(g for g in gr_b if n in g["membri"])
            tv = [(g["sharpe"], g["settimane"]) for g in gr_b if g is not fam]
            v = [sr for sr, w in tv if abs(sr * math.sqrt(w / 52)) <= 3] + [fam["sharpe"]]
            v += [float(x) for x in soli if abs(float(x) * math.sqrt(getattr(x, "settimane", 300) / 52)) <= 3]
            c = e["candidate"][n]
            m = c["misure"]
            p = te.sharpe_corretto(m["sharpe"], c["in_vigore"]["settimane_efficaci"], m["asimmetria"], m["curtosi"], v, 52, n_prove=N)
            out[n]["probabilita_famiglia_in_v"] = p
            out[n]["famiglia"] = {"membri": len(fam["membri"]), "sharpe": fam["sharpe"]}
    return out


def parte_esame():
    b = carica_base()
    base_mazzo = ast.mazzo()
    log("mazzo letto", len(base_mazzo[0]), len(base_mazzo[1]))
    out = {}
    out["pubblicate"] = esame_con({"168 A": leggi_salvata("A")["netto"], "168 B": leggi_salvata("B")["netto"]}, base_mazzo, True)
    log("pubblicate", out["pubblicate"])
    out["rifatte_oggi"] = esame_con({"168 A": b["serie"]["A"]["netto"], "168 B": b["serie"]["B"]["netto"]}, base_mazzo, True)
    log("rifatte", out["rifatte_oggi"])
    out["G1_sola"] = esame_con({"57 G1": leggi_salvata("G1")["netto"]}, base_mazzo, True)
    salva("esame", out)


# ---------------------------------------------------------------------------------------------------------------------------------
# costi: B e A con il limite che deve andare oltre lo 0,05% e lo 0,10% e tutto a mercato (l'ordine del bot, GTC al mark)
# ---------------------------------------------------------------------------------------------------------------------------------

def parte_costi():
    b = carica_base()
    pan = sc.pannello()
    giorni, R, F, costo = b["P"]["giorni"], b["R"], b["F"], b["costo"]
    H = carica_ore(pan, giorni, [])
    base_mazzo = ast.mazzo()
    out = {}
    for nome, oltre, modo in (("limite_al_tocco", 0.0, "limite"), ("limite_oltre_0,05%", 0.0005, "limite"),
                              ("limite_oltre_0,10%", 0.001, "limite"), ("tutto_a_mercato", 0.0, "mercato")):
        s = {}
        info = {}
        for n in ("G1", "G11", "G1N", "B"):
            g, s[n], nt, nl = conto(b["P"][n], R, F, costo, giorni, H, oltre, modo)
            info[n] = {**breve(numeri(s[n]["netto"])), "spese_annue": float(s[n]["spese"].mean() * 52), "quota_limite": nl / max(nt, 1)}
        s["A"] = sum(s[n][["netto"]] for n in ("G1", "G11", "G1N")) / 4 + b["serie"]["F5"][["netto"]] / 4
        info["A"] = breve(numeri(s["A"]["netto"]))
        ex = esame_con({"168 A": s["A"]["netto"], "168 B": s["B"]["netto"]}, base_mazzo, True)
        out[nome] = {"numeri": info, "esame": ex}
        log(nome, {k: (round(v["probabilita_in_vigore"], 3), round(v.get("probabilita_famiglia_in_v", 0), 3)) for k, v in ex.items() if k[0] != "_"})
    # F5 dentro A con ordini limite (F9): controllo descrittivo, non una variante
    salva("costi", out)


# ---------------------------------------------------------------------------------------------------------------------------------
# conto vero simulato, giorno per giorno: filtri veri di oggi (passo, quantita' minima, valore minimo), 1.000 e 10.000 USDT
# ---------------------------------------------------------------------------------------------------------------------------------

def carica_filtri(simboli):
    f = json.loads(FILTRI.read_text(encoding="utf-8"))["filtri"]
    nomi = [sc.simbolo_base(s)[0] for s in simboli]
    vmin = np.array([float(f[s]["valore_minimo"]) if s in f else 5.0 for s in nomi])
    passo = np.array([float(f[s]["passo"]) if s in f else 0.0 for s in nomi])
    qmin = np.array([float(f[s]["quantita_minima"]) if s in f else 0.0 for s in nomi])
    return vmin, passo, qmin, np.array([s in f for s in nomi])


def simula(W, giorni, pan, H, costo, capitale, modo="limite", oltre=0.0, minimi=True, chiusure_libere=False, composto=True,
           solo_lunedi=False):
    """Il conto vero simulato, partenza a conto vuoto il 4 gennaio 2021. Ogni giorno alle 00:00 (o solo il lunedi'): obiettivo in
    quantita' = peso x base / apertura; variazione arrotondata verso zero al passo; saltata se sotto la quantita' o il valore minimo
    (anche le chiusure, come `demo_binance.ordini_del_giorno`; con ``chiusure_libere`` le riduzioni si fanno, come «solo riduzione»).
    Costi: limite (`tasso`) o mercato; funding sul valore tenuto (come `terza.conto`); quantita' sulla griglia del passo (voce 48)."""
    t0 = pan["t0"]
    idx = giorni - t0
    Pz = pan["open"][idx]
    Rz = sc.rendimenti(pan)[idx]
    Fz = np.nan_to_num(pan["funding"][idx])
    S = W.shape[1]
    vmin, passo, qmin, _ = carica_filtri(pan["simboli"])
    q = np.zeros(S)
    ultimo = np.zeros(S)
    E = float(capitale)
    righe = []
    voluti = saltati = 0
    for k in range(len(giorni)):
        p = Pz[k]
        vivo = np.isfinite(p) & (p > 0)
        base = E if composto else float(capitale)
        spese = 0.0
        morte = (q != 0) & ~vivo
        if morte.any():
            spese += float((np.abs(q[morte] * ultimo[morte]) * costo[morte]).sum())
            q[morte] = 0.0
        lun = (int(giorni[k]) + 3) % 7 == 0
        if solo_lunedi and not lun:
            d = np.zeros(S)
        else:
            obi = np.where(vivo, W[k] * base / np.where(vivo, p, 1.0), 0.0)
            delta = obi - q
            da_fare = vivo & (np.abs(delta * np.nan_to_num(p)) > 1e-9)
            if minimi:
                qa_ = np.abs(delta)
                qr = np.where(passo > 0, np.floor(qa_ / np.where(passo > 0, passo, 1.0) + 1e-9) * passo, qa_)
                val = qr * np.nan_to_num(p)
                riduce = (obi == 0) | ((q != 0) & (np.sign(q) == np.sign(obi)) & (np.abs(obi) < np.abs(q)))
                ok_v = val >= vmin - 1e-9
                ok = (qr > 0) & (qr >= qmin - 1e-12) & ((ok_v | riduce) if chiusure_libere else ok_v)
                d = np.where(da_fare & ok, np.sign(delta) * qr, 0.0)
                voluti += int(da_fare.sum())
                saltati += int((da_fare & (d == 0)).sum())
            else:
                d = np.where(da_fare, delta, 0.0)
        dv = d * np.nan_to_num(p)
        if modo == "limite":
            HH = {kk: v[k][None, :] for kk, v in H.items() if kk != "fatti"}
            t, _ = tasso(np.sign(dv)[None, :], HH, costo, oltre, "limite")
            t = t[0]
        else:
            t = costo
        spese += float((np.abs(dv) * t).sum())
        q = q + d
        q = np.where(passo > 0, np.round(q / np.where(passo > 0, passo, 1.0)) * passo, q)
        q = np.where(np.abs(q * np.nan_to_num(p)) < 1e-9, 0.0, q)
        valore = np.where(vivo, q * np.nan_to_num(p), 0.0)
        lordo = float((valore * Rz[k]).sum())
        fund = float((valore * Fz[k]).sum())
        netto = lordo - spese - fund
        r = netto / (E if composto else float(capitale))
        righe.append({"giorno": int(giorni[k]), "netto": r, "lorda": float(np.abs(valore).sum() / base),
                      "netta": float(valore.sum() / base), "spese": spese / base, "ordini": int((d != 0).sum()),
                      "fuori_obiettivo": float(np.abs(valore / base - W[k]).sum())})
        ultimo = np.where(vivo, np.nan_to_num(p) * (1 + Rz[k]), 0.0)
        E = E + netto if composto else E
        if E <= 0:
            break
    df = pd.DataFrame(righe).set_index("giorno")
    df.attrs = {"voluti": voluti, "saltati": saltati}
    return df


def settimanale(df: pd.DataFrame) -> pd.Series:
    return df["netto"].groupby(pr.lunedi_del_giorno(df.index.to_numpy())).sum()


def parte_conto():
    b = carica_base()
    pan = sc.pannello()
    giorni, costo = b["P"]["giorni"], b["costo"]
    H = carica_ore(pan, giorni, [])
    base_mazzo = ast.mazzo()
    out = {}
    casi = [("B_senza_minimi_limite", "B", 1000, dict(minimi=False)),
            ("B_1000_limite", "B", 1000, {}), ("B_1000_limite_chiusure_libere", "B", 1000, dict(chiusure_libere=True)),
            ("B_1000_mercato", "B", 1000, dict(modo="mercato")),
            ("B_10000_limite", "B", 10000, {}), ("B_10000_mercato", "B", 10000, dict(modo="mercato")),
            ("B_1000_limite_capitale_fisso", "B", 1000, dict(composto=False))]
    sim = {}
    for nome, w, cap, kw in casi:
        df = simula(b["P"][w], giorni, pan, H, costo, cap, **kw)
        x = settimanale(df)
        sim[nome] = x
        out[nome] = {**breve(numeri(x)), "per_anno": per_anno(x), "voluti": df.attrs["voluti"], "saltati": df.attrs["saltati"],
                     "fuori_obiettivo_medio": float(df["fuori_obiettivo"].mean()), "netta_min_max": [float(df["netta"].min()), float(df["netta"].max())],
                     "lorda_media": float(df["lorda"].mean()), "giorno_peggiore": [sc.data(int(df["netto"].idxmin())), float(df["netto"].min())]}
        log(nome, out[nome]["sharpe"], out[nome]["annuo"])
    # A a 1.000 USDT: quattro conti da 250 (F5 solo il lunedi', a mercato come nella prova)
    for cap, nome in ((250, "A_1000_quattro_da_250"), (2500, "A_10000_quattro_da_2500")):
        parti = {}
        for w in ("G1", "G11", "G1N"):
            parti[w] = settimanale(simula(b["P"][w], giorni, pan, H, costo, cap))
        parti["F5"] = settimanale(simula(b["P"]["F5g"], giorni, pan, H, costo, cap, modo="mercato", solo_lunedi=True))
        x = sum(parti.values()) / 4
        sim[nome] = x
        out[nome] = {**breve(numeri(x)), "per_anno": per_anno(x), "parti": {k: breve(numeri(v)) for k, v in parti.items()}}
        log(nome, out[nome]["sharpe"])
    for coppia in (("B_1000_limite", "A_1000_quattro_da_250"), ("B_10000_limite", "A_10000_quattro_da_2500"),
                   ("B_1000_mercato", "A_1000_quattro_da_250")):
        ex = esame_con({"168 B": sim[coppia[0]], "168 A": sim[coppia[1]]}, base_mazzo, True)
        out[f"esame_{coppia[0]}_{coppia[1]}"] = ex
        log("esame", coppia, {k: round(v["probabilita_in_vigore"], 3) for k, v in ex.items() if k[0] != "_"})
    salva("conto", out)


# ---------------------------------------------------------------------------------------------------------------------------------
# rischio: leva, peso per moneta, giorni sotto -5%, perdita peggiore possibile nel giorno, distanza dalla liquidazione
# ---------------------------------------------------------------------------------------------------------------------------------

def parte_rischio():
    b = carica_base()
    pan = sc.pannello()
    giorni, idx = b["P"]["giorni"], b["P"]["idx"]
    out = {}
    O, Hh, L = pan["open"][idx], pan["high"][idx], pan["low"][idx]
    with np.errstate(invalid="ignore", divide="ignore"):
        su = np.nan_to_num(Hh / O - 1)
        giu = np.nan_to_num(L / O - 1)
    for n in ("B", "G1", "G1N"):
        W = b["P"][n]
        lorda, netta = np.abs(W).sum(axis=1), W.sum(axis=1)
        mx = np.abs(W).max(axis=1)
        peggio = np.where(W > 0, W * giu, np.where(W < 0, W * su, 0.0)).sum(axis=1)    # tutti i lunghi al minimo, tutti i corti al massimo
        k = int(np.argmin(peggio))
        jmx = int(np.argmax(np.abs(W[int(np.argmax(mx))])))
        singolo = np.where(W < 0, W * su, np.where(W > 0, W * giu, 0.0))
        ks, js = np.unravel_index(int(np.argmin(singolo)), singolo.shape)
        out[n] = {"lorda_media": float(lorda.mean()), "lorda_max": float(lorda.max()), "netta_min_max": [float(netta.min()), float(netta.max())],
                  "peso_max_moneta": [float(mx.max()), sc.data(int(giorni[int(np.argmax(mx))])), b["simboli"][jmx]],
                  "giorni_con_una_moneta_oltre_10%": int((mx > 0.10).sum()), "giorni_con_una_moneta_oltre_20%": int((mx > 0.20).sum()),
                  "monete_per_lato_min": [int((W > 0).sum(axis=1)[lorda > 0].min()), int((W < 0).sum(axis=1)[lorda > 0].min())],
                  "perdita_peggiore_possibile_nel_giorno": [float(peggio[k]), sc.data(int(giorni[k]))],
                  "perdita_peggiore_di_una_moneta": [float(singolo[ks, js]), sc.data(int(giorni[ks])), b["simboli"][js], float(W[ks, js])],
                  "giorni_peggio_possibile_oltre_-20%": int((peggio < -0.20).sum())}
    gB = b["gB"]
    x = gB["netto"].to_numpy()
    sotto = np.flatnonzero(x < -0.05)
    out["B_giorni_sotto_-5%"] = {"n": int(len(sotto)), "date": [sc.data(int(giorni[i])) for i in sotto],
                                 "valori": [float(x[i]) for i in sotto],
                                 "giorno_dopo": [float(x[i + 1]) for i in sotto if i + 1 < len(x)]}
    out["nota_liquidazione"] = ("margine unico: con lorda 2 e mantenimento fra lo 0,4% e il 2,5% del nozionale la liquidazione vuole una "
                                "perdita del conto fra il 95% e il 99%; confronto con la perdita peggiore possibile nel giorno")
    salva("rischio", out)


# ---------------------------------------------------------------------------------------------------------------------------------
# misure: concentrazione, anni, climi, durata della discesa, esposizione, guadagno per ordine contro costo per ordine
# ---------------------------------------------------------------------------------------------------------------------------------

def durata_discesa(x: pd.Series) -> int:
    eq = np.cumprod(1 + x.to_numpy())
    picco = np.maximum.accumulate(eq)
    sotto = eq < picco - 1e-12
    lung = m = 0
    for s_ in sotto:
        m = m + 1 if s_ else 0
        lung = max(lung, m)
    return int(lung)


def parte_misure():
    b = carica_base()
    out = {}
    btc = b["btc"]
    for n in ("A", "B", "G1"):
        x = leggi_salvata(n)["netto"]
        tot = x.sum()
        mesi = x.groupby(pd.to_datetime(x.index.to_numpy() * 86400, unit="s").to_period("M")).sum()
        b13 = np.log1p(btc).rolling(13).sum().reindex(x.index)
        clima = np.where(b13 > np.log(1.2), "rialzo", np.where(b13 < np.log(0.8), "ribasso", "laterale"))
        out[n] = {**breve(numeri(x)), "durata_discesa_settimane": durata_discesa(x),
                  "quota_5_settimane_migliori": float(x.nlargest(5).sum() / tot), "quota_3_mesi_migliori": float(mesi.nlargest(3).sum() / tot),
                  "per_clima": {c: {"settimane": int((clima == c).sum()), "annuo": float(x[clima == c].mean() * 52),
                                    "sharpe": ast.sharpe(x[clima == c])} for c in ("rialzo", "laterale", "ribasso")}}
    gB = b["gB"]
    y = gB["netto"]
    out["B_giorni"] = {"giorni": int(len(y)), "quota_5_giorni_migliori": float(y.nlargest(5).sum() / y.sum()),
                       "lordo_per_variazione_contro_spesa": None}
    W = b["P"]["B"]
    out["B_esposizione"] = {"lorda_media": float(np.abs(W).sum(axis=1).mean()), "giorni_senza_posizioni": int((np.abs(W).sum(axis=1) == 0).sum())}
    out["B_guadagno_e_spese_l_anno"] = {"lordo": float(gB["lordo"].mean() * 365), "spese": float(gB["spese"].mean() * 365),
                                        "funding_pagato": float(gB["funding"].mean() * 365)}
    out["definizione_clima"] = "rendimento del Bitcoin delle 13 settimane fino a quella compresa: sopra +20% rialzo, sotto -20% ribasso"
    salva("misure", out)


# ---------------------------------------------------------------------------------------------------------------------------------
# sensibilita': ogni parametro +-10% e +-20% insieme nelle quattro componenti
# ---------------------------------------------------------------------------------------------------------------------------------

def parte_sensi():
    b = carica_base()
    pan = sc.pannello()
    giorni, R, F, costo = b["P"]["giorni"], b["R"], b["F"], b["costo"]
    H = carica_ore(pan, giorni, [])
    ex = json.loads((QUI / f"prova168_2026-11-27_esito_esame{A.etichetta}.json").read_text())
    e0 = ast.esame(nuove={"168 B": leggi_salvata("B")["netto"]}, candidate=["168 B"])
    v, N = e0["in_vigore"]["v"], e0["in_vigore"]["famiglie"]
    ps100 = te.pannello_settimane(pan, log=lambda x: None, indicatori_si=False)
    casi = [("base", {})]
    for p_, base_v, passi in (("entra", 0.20, (0.16, 0.18, 0.22, 0.24)), ("resta", 0.40, (0.32, 0.36, 0.44, 0.48)),
                              ("gf", 7, (5, 6, 8, 9)), ("gs", 30, (24, 27, 33, 36)), ("gb", 90, (72, 81, 99, 108)),
                              ("n_uni", 100, (80, 90, 110, 120))):
        casi += [(f"{p_}={x}", {p_: x}) for x in passi]
    out = {"nota": "probabilita' con la V e l'N dell'esame in vigore fissi (mazzo di oggi) e le settimane efficaci della variante",
           "N": N, "in_v": len(v), "riferimento": ex["pubblicate"]["168 B"]["probabilita_in_vigore"]}
    for nome, kw in casi:
        P = pesi_quattro(pan, ps=None if "n_uni" in kw else ps100, **kw)
        s = {}
        for n in ("G1", "G11", "G1N", "B"):
            s[n] = conto(P[n], R, F, costo, giorni, H)[1]["netto"]
        d5 = te.conto(P["Wt"], P["ps"]["R"], P["ps"]["F"], costo)
        d5.index = P["ps"]["lunedi"]
        s["F5"] = d5["netto"][(d5.index >= se.INIZIO) & (d5.index < pr.FINE)]
        s["A"] = (s["G1"] + s["G11"] + s["G1N"] + s["F5"]) / 4
        riga = {}
        for n in ("A", "B", "G1"):
            m = numeri(s[n])
            w = max(3, int(round(m["settimane"] * m["rapporto_robusto"])))
            riga[n] = {"sharpe": m["sharpe"], "annuo": m["annuo"], "discesa": m["discesa_max"], "t_robusto": m["t_robusto"],
                       "anni_positivi": all(vv > 0 for vv in m["per_anno"].values()),
                       "probabilita": te.sharpe_corretto(m["sharpe"], w, m["asimmetria"], m["curtosi"], v, 52, n_prove=N)}
        out[nome] = riga
        log(nome, {k: (round(r["sharpe"], 3), round(r["probabilita"], 3)) for k, r in riga.items()})
    salva("sensi", out)


# ---------------------------------------------------------------------------------------------------------------------------------
# taglio: i pesi di un giorno con il pannello fermo alla chiusura del giorno prima (piu' l'apertura del giorno) contro il calcolo intero
# ---------------------------------------------------------------------------------------------------------------------------------

def parte_taglio():
    b = carica_base()
    pan = sc.pannello()
    out = {}
    giorni = b["P"]["giorni"]
    date = [(2021, 5, 19), (2022, 6, 13), (2022, 11, 9), (2023, 3, 13), (2024, 8, 5), (2025, 10, 10), (2025, 10, 13), (2026, 6, 1),
            (2026, 9, 30)]
    for a_, m_, g_ in date:
        d = sc.giorno(a_, m_, g_)
        k = int(np.flatnonzero(giorni == d)[0])
        i = d - pan["t0"]
        pc = {kk: (vv.copy() if isinstance(vv, np.ndarray) else vv) for kk, vv in pan.items()}
        for kk in ("high", "low", "close", "quote_volume", "taker_buy_quote_volume", "funding"):
            pc[kk][i:] = np.nan if kk != "funding" else 0.0
        pc["open"][i + 1:] = np.nan
        P = pesi_quattro(pc)
        out[sc.data(d)] = {n: float(np.abs(P[n][k] - b["P"][n][k]).max()) for n in ("G1", "G11", "G1N", "F5g", "B")}
        log(sc.data(d), out[sc.data(d)])
    salva("taglio", out)


# ---------------------------------------------------------------------------------------------------------------------------------
# dati: buchi, monete tolte dal listino, funding stimato, salti, candele orarie
# ---------------------------------------------------------------------------------------------------------------------------------

def parte_dati():
    b = carica_base()
    pan = sc.pannello()
    giorni, idx = b["P"]["giorni"], b["P"]["idx"]
    W = b["P"]["B"]
    tenute = np.abs(W) > 0
    C, O, V = pan["close"][idx], pan["open"][idx], pan["quote_volume"][idx]
    out = {}
    # buchi: giorni senza candela mentre la moneta e' tenuta
    manca = tenute & ~np.isfinite(C)
    out["giorni_moneta_tenuti_senza_candela"] = int(manca.sum())
    out["dove"] = {}
    for k, j in zip(*np.nonzero(manca)):
        out["dove"].setdefault(sc.data(int(giorni[k])), []).append(b["simboli"][j])
    out["dove"] = {k: (len(v), v[:8]) for k, v in sorted(out["dove"].items())}
    out["peso_lordo_tenuto_nei_buchi"] = float(np.abs(W[manca]).sum())
    # monete ferme (volume zero e prezzo uguale) tenute
    with np.errstate(invalid="ignore"):
        ferme = tenute & (np.nan_to_num(V) == 0)
    out["giorni_moneta_tenuti_a_volume_zero"] = int(ferme.sum())
    # salti: rendimenti del giorno tenuto oltre il 50%
    Rz = b["R"]
    grandi = tenute & (np.abs(Rz) > 0.5)
    out["giorni_moneta_tenuti_oltre_50%"] = [(sc.data(int(giorni[k])), b["simboli"][j], float(Rz[k, j]), float(W[k, j]))
                                             for k, j in zip(*np.nonzero(grandi))][:30]
    # candele orarie: variazioni senza le due ore (pagate a mercato)
    D = cu.variazioni(W, Rz)
    H = carica_ore(pan, giorni, [])
    nz = np.abs(D) > 1e-9
    out["variazioni_senza_ore"] = [int((nz & ~H["ok"]).sum()), int(nz.sum())]
    with np.errstate(invalid="ignore", divide="ignore"):
        rel = np.abs(H["O0"] / O - 1)
    okr = tenute & np.isfinite(rel)
    out["apertura_oraria_contro_giornaliera"] = {"coppie": int(okr.sum()), "oltre_0,1%": int((rel[okr] > 0.001).sum()),
                                                 "massimo": float(rel[okr].max())}
    # funding: il pannello contro i regolamenti veri (archivio + interfaccia) nei giorni tenuti
    tenute_j = np.flatnonzero(tenute.any(axis=0))
    stimati, senza, diversi, tot = 0, 0, 0, 0
    esempi = []
    for j in tenute_j:
        s = b["simboli"][j]
        base_s, _, al = sc.simbolo_base(s)
        try:
            vero = sc.funding_giorni(base_s)
        except Exception as e:  # noqa: BLE001
            esempi.append((s, "errore " + str(e)[:80]))
            continue
        kk = np.flatnonzero(tenute[:, j])
        g = giorni[kk]
        if al is not None:
            kk, g = kk[g < al], g[g < al]
        pv = pan["funding"][idx[kk], j]
        vv = vero.reindex(g).to_numpy()
        tot += len(kk)
        nov = ~np.isfinite(vv)
        senza += int(nov.sum())
        dif = np.isfinite(vv) & (np.abs(pv - np.nan_to_num(vv)) > 1e-10)
        diversi += int(dif.sum())
        stimati += int((nov & (np.abs(pv) > 0)).sum())
        if (dif.any() or (nov & (np.abs(pv) > 0)).any()) and len(esempi) < 20:
            esempi.append((s, int(dif.sum()), int((nov & (np.abs(pv) > 0)).sum()), [sc.data(int(x)) for x in g[dif | (nov & (np.abs(pv) > 0))][:4]]))
    out["funding"] = {"giorni_moneta_tenuti": tot, "senza_regolamento_vero": senza, "senza_vero_ma_non_zero_nel_pannello": stimati,
                      "diversi_dal_vero": diversi, "esempi": esempi}
    # le colonne dei simboli rilanciati e i contratti che non sono monete nel periodo
    out["colonne_prima_del"] = [s for j, s in enumerate(b["simboli"]) if "_prima_del_" in s and tenute[:, j].any()]
    salva("dati", out)


def parte_buchi():
    """I giorni senza candela tenuti da B riempiti con le candele da 1 giorno dell'interfaccia pubblica (www.binance.com/fapi/v1/klines),
    salvate nella cartella della cache, poi B rifatta in memoria (lo stesso metodo di `f5_conto_vero_2026-11-27.py buchi`)."""
    import requests
    b = carica_base()
    pan = {k: (v.copy() if isinstance(v, np.ndarray) else v) for k, v in sc.pannello().items()}
    giorni, idx = b["P"]["giorni"], b["P"]["idx"]
    C = pan["close"]
    cartella = CACHE / "giorni_buchi"
    cartella.mkdir(exist_ok=True)
    riempiti = scaricati = 0
    for j, s in enumerate(pan["simboli"]):
        ok = np.isfinite(C[:, j])
        fin = np.flatnonzero(ok)
        if not len(fin):
            continue
        manca = [int(i) for i in range(max(fin[0], idx[0]), min(fin[-1], idx[-1]) + 1) if not ok[i]]
        if not manca:
            continue
        base_s = sc.simbolo_base(s)[0]
        blocchi = []
        for i in manca:
            if blocchi and i == blocchi[-1][-1] + 1:
                blocchi[-1].append(i)
            else:
                blocchi.append([i])
        for bl in blocchi:
            g0 = bl[0] + pan["t0"]
            f = cartella / f"{base_s}-{g0}-{len(bl)}.json"
            if not f.exists():
                r = requests.get("https://www.binance.com/fapi/v1/klines", params={"symbol": base_s, "interval": "1d",
                                 "startTime": g0 * 86_400_000, "limit": len(bl)}, timeout=30)
                f.write_text(r.text if r.status_code == 200 else "[]", encoding="utf-8")
                scaricati += 1
                time.sleep(0.15)
            try:
                righe = json.loads(f.read_text(encoding="utf-8"))
            except Exception:  # noqa: BLE001
                righe = []
            for riga in righe if isinstance(righe, list) else []:
                tt = int(riga[0]) // 86_400_000 - pan["t0"]
                if tt in bl and not np.isfinite(pan["close"][tt, j]):
                    pan["open"][tt, j], pan["high"][tt, j], pan["low"][tt, j], pan["close"][tt, j] = map(float, riga[1:5])
                    pan["quote_volume"][tt, j] = float(riga[7])
                    riempiti += 1
    log("riempiti", riempiti, "scaricati", scaricati)
    P = pesi_quattro(pan)
    R = sc.rendimenti(pan)[idx]
    F = np.nan_to_num(pan["funding"][idx])
    H = carica_ore(pan, giorni, [])
    s = {}
    for n in ("G1", "B"):
        s[n] = conto(P[n], R, F, b["costo"], giorni, H)[1]["netto"]
    out = {"giorni_moneta_riempiti": riempiti, "file_scaricati_ora": scaricati,
           "B_prima": breve(numeri(b["serie"]["B"]["netto"])), "B_dopo": breve(numeri(s["B"])),
           "G1_prima": breve(numeri(b["serie"]["G1"]["netto"])), "G1_dopo": breve(numeri(s["G1"]))}
    salva("buchi", out)


def parte_avanti():
    """Ricontrollo aritmetico della parte in avanti dal file della prova (non la rifa dalle risposte della macchina)."""
    d = pd.read_csv(P7 / "risultati_centosesta" / "avanti.csv")
    out = {"intervalli": int(len(d)), "giorni": int(d["giorni"].sum()), "da": d["da"].iloc[0], "a": d["a"].iloc[-1]}
    for n in ("G1", "G11", "G1N", "F5", "un_quarto"):
        out[n] = float(np.prod(1 + d[n]) - 1)
    out["un_quarto_e_la_media"] = float(np.abs(d[["G1", "G11", "G1N", "F5"]].mean(axis=1) - d["un_quarto"]).max())
    salva("avanti", out)


def parte_ultima():
    """La causa dello scarto dell'ultima settimana (28 settembre - 4 ottobre 2026) fra le serie salvate il 25 ottobre (G1, G11, G1N) e
    quelle di oggi: il funding di ottobre stimato nel pannello di allora (voce 3; il file mensile di ottobre esce a novembre e il codice
    di allora non leggeva l'interfaccia). Si rifanno G1, G11 e G1N con il funding dal 1 ottobre 2026 messo alla media dei 90 giorni prima
    (come `seconda.riempi_funding`) e si confronta l'ultima settimana con le serie salvate."""
    b = carica_base()
    pan = {k: (v.copy() if isinstance(v, np.ndarray) else v) for k, v in sc.pannello().items()}
    giorni, idx = b["P"]["giorni"], b["P"]["idx"]
    ott = sc.giorno(2026, 10, 1) - pan["t0"]
    Fp = pan["funding"]
    c_ok = np.isfinite(pan["close"])
    for j in range(Fp.shape[1]):
        cop = np.flatnonzero(c_ok[:ott, j])[-90:]
        if len(cop):
            Fp[ott:, j] = np.where(c_ok[ott:, j], Fp[cop, j].mean(), 0.0)
    P = pesi_quattro(pan)
    R = sc.rendimenti(pan)[idx]
    F = np.nan_to_num(Fp[idx])
    H = carica_ore(pan, giorni, [])
    out = {}
    ultima = sc.giorno(2026, 9, 28)
    for n in ("G1", "G11", "G1N"):
        s = conto(P[n], R, F, b["costo"], giorni, H)[1]
        old = leggi_salvata(n)
        out[n] = {"salvata": {c: float(old.loc[ultima, c]) for c in ("lordo", "spese", "funding", "netto")},
                  "oggi_funding_vero": {c: float(b["serie"][n].loc[ultima, c]) for c in ("lordo", "spese", "funding", "netto")},
                  "oggi_ottobre_stimato": {c: float(s.loc[ultima, c]) for c in ("lordo", "spese", "funding", "netto")}}
    salva("ultima", out)


def parte_misto():
    b = carica_base()
    pan = sc.pannello()
    giorni, R, F, costo = b["P"]["giorni"], b["R"], b["F"], b["costo"]
    H = carica_ore(pan, giorni, [])
    base_mazzo = ast.mazzo()
    out = {}
    for q in (0.27, 0.40, 0.60):
        s = {}
        for n in ("G1", "G11", "G1N", "B"):
            s[n] = conto(b["P"][n], R, F, costo, giorni, H, 0.0, f"misto{q}")[1]
        s["A"] = sum(s[n][["netto"]] for n in ("G1", "G11", "G1N")) / 4 + b["serie"]["F5"][["netto"]] / 4
        ex = esame_con({"168 A": s["A"]["netto"], "168 B": s["B"]["netto"], "57 G1": s["G1"]["netto"]}, base_mazzo, True)
        out[f"quota_a_mercato_{q}"] = {"numeri": {n: {**breve(numeri(s[n]["netto"])), "spese_annue": float(s[n]["spese"].mean() * 52) if "spese" in s[n] else None}
                                                  for n in ("A", "B", "G1")}, "esame": ex}
        log(q, {k: (round(v["probabilita_in_vigore"], 3), round(v.get("probabilita_famiglia_in_v", 0), 3)) for k, v in ex.items() if k[0] != "_"})
    salva("misto", out)


def parte_ore_rischio():
    """La perdita nel giorno ora per ora (candele da 1 ora, `esecuzione.ore_di`) nei 12 giorni con la perdita peggiore possibile piu'
    grande e nei 6 giorni peggiori veri di B: (a) tutti i lunghi al minimo e tutti i corti al massimo della stessa ora, (b) alle
    chiusure orarie. Rispetto all'apertura del giorno, con i pesi del giorno."""
    b = carica_base()
    pan = sc.pannello()
    giorni, idx = b["P"]["giorni"], b["P"]["idx"]
    W = b["P"]["B"]
    O, Hh, L = pan["open"][idx], pan["high"][idx], pan["low"][idx]
    with np.errstate(invalid="ignore", divide="ignore"):
        su, giu = np.nan_to_num(Hh / O - 1), np.nan_to_num(L / O - 1)
    peggio = np.where(W > 0, W * giu, np.where(W < 0, W * su, 0.0)).sum(axis=1)
    scelti = list(np.argsort(peggio)[:12]) + list(np.argsort(b["gB"]["netto"].to_numpy())[:6])
    out = {}
    cache_ore = {}
    for k in dict.fromkeys(int(x) for x in scelti):
        js = np.flatnonzero(W[k] != 0)
        h0 = int(giorni[k]) * 24
        a = np.zeros(24)
        c = np.zeros(24)
        mancano = 0
        for j in js:
            s_ = b["simboli"][j]
            if s_ not in cache_ore:
                cache_ore[s_] = es.ore_di(s_)
            z = cache_ore[s_]
            z = z[~z.index.duplicated(keep="last")].reindex(range(h0, h0 + 24))
            o = O[k, j]
            if not np.isfinite(o) or z["close"].isna().all():
                mancano += 1
                continue
            lo, hi, cl = (z[x].ffill().to_numpy() for x in ("low", "high", "close"))
            w = W[k, j]
            a += np.nan_to_num(w * ((lo if w > 0 else hi) / o - 1))
            c += np.nan_to_num(w * (cl / o - 1))
        out[sc.data(int(giorni[k]))] = {"peggio_col_giornaliero": float(peggio[k]), "peggio_ora_per_ora": float(a.min()),
                                        "ora_peggiore": int(a.argmin()), "minimo_alle_chiusure_orarie": float(c.min()),
                                        "netto_del_giorno": float(b["gB"]["netto"].iloc[k]), "monete": int(len(js)), "senza_ore": mancano,
                                        "lorda": float(np.abs(W[k]).sum())}
        log(sc.data(int(giorni[k])), out[sc.data(int(giorni[k]))])
    salva("ore_rischio", out)


def parte_partenze():
    """Il conto vero a capitale fisso (1.000 USDT per B, quattro da 250 per A), partito vuoto in date diverse fino al 4 ottobre 2026,
    contro la ricerca sugli stessi giorni (voce 44: per F5 la partenza del 29 settembre 2025 dava -35,7%)."""
    b = carica_base()
    pan = sc.pannello()
    giorni, costo = b["P"]["giorni"], b["costo"]
    H = carica_ore(pan, giorni, [])
    out = {}
    for a_, m_, g_ in ((2021, 1, 4), (2024, 1, 1), (2025, 1, 6), (2025, 9, 29), (2026, 1, 5)):
        d0 = sc.giorno(a_, m_, g_)
        k0 = int(np.flatnonzero(giorni == d0)[0])
        gg = giorni[k0:]
        Hk = {k: (v[k0:] if k != "fatti" else v) for k, v in H.items()}
        riga = {}
        for nome, kw in (("B_1000_limite", {}), ("B_1000_mercato", dict(modo="mercato")),
                         ("B_1000_limite_chiusure_libere", dict(chiusure_libere=True))):
            df = simula(b["P"]["B"][k0:], gg, pan, Hk, costo, 1000, composto=False, **kw)
            x = df["netto"]
            eq = 1 + x.cumsum()
            riga[nome] = {"totale": float(x.sum()), "discesa_max_sul_capitale": float((eq - eq.cummax()).min()),
                          "sharpe": float(x.mean() / x.std() * math.sqrt(365)), "saltati": df.attrs["saltati"], "voluti": df.attrs["voluti"]}
        parti = []
        for w, mo, sl in (("G1", "limite", False), ("G11", "limite", False), ("G1N", "limite", False), ("F5g", "mercato", True)):
            parti.append(simula(b["P"][w][k0:], gg, pan, Hk, costo, 250, composto=False, modo=mo, solo_lunedi=sl)["netto"])
        x = sum(parti) / 4
        eq = 1 + x.cumsum()
        riga["A_quattro_da_250"] = {"totale": float(x.sum()), "discesa_max_sul_capitale": float((eq - eq.cummax()).min()),
                                    "sharpe": float(x.mean() / x.std() * math.sqrt(365)),
                                    "F5_da_250": float(parti[3].sum()), "F5_discesa": float(((1 + parti[3].cumsum()) - (1 + parti[3].cumsum()).cummax()).min())}
        ric = b["gB"]["netto"].iloc[k0:]
        eqr = np.cumprod(1 + ric.to_numpy())
        riga["ricerca_B_stessi_giorni"] = {"totale_somma": float(ric.sum()), "discesa_max": float((eqr / np.maximum.accumulate(eqr) - 1).min()),
                                           "sharpe": float(ric.mean() / ric.std() * math.sqrt(365))}
        out[sc.data(d0)] = riga
        log(sc.data(d0), {k: round(v["totale"] if "totale" in v else v["totale_somma"], 3) for k, v in riga.items()})
    salva("partenze", out)


def parte_tempi():
    """Entrata un'ora dopo la decisione (voce 14): rendimento dall'apertura delle 01:00 all'apertura delle 01:00 del giorno dopo (dove
    ci sono le candele orarie; altrimenti il giorno), funding come prima. Costi: tutto a mercato (confronto con il mercato alle 00:00)
    e il limite della ricerca come approssimazione."""
    b = carica_base()
    pan = sc.pannello()
    giorni, R, F, costo = b["P"]["giorni"], b["R"], b["F"], b["costo"]
    H = carica_ore(pan, giorni, [])
    O1 = H["O1"]
    with np.errstate(invalid="ignore", divide="ignore"):
        R1 = np.vstack([O1[1:] / O1[:-1] - 1, np.full((1, O1.shape[1]), np.nan)])
    R1 = np.where(np.isfinite(R1), R1, R)
    out = {"quota_giorni_moneta_con_ore": float(np.isfinite(O1).mean())}
    base_mazzo = ast.mazzo()
    for nome, RR, modo in (("00_mercato", R, "mercato"), ("01_mercato", R1, "mercato"), ("00_limite", R, "limite"), ("01_limite_approssimato", R1, "limite")):
        s_ = {n: conto(b["P"][n], RR, F, costo, giorni, H, 0.0, modo)[1] for n in ("G1", "B")}
        out[nome] = {n: breve(numeri(v["netto"])) for n, v in s_.items()}
        if nome.startswith("01"):
            out[nome]["esame"] = esame_con({"168 B": s_["B"]["netto"]}, base_mazzo, True)
        log(nome, {n: round(v["sharpe"], 3) for n, v in out[nome].items() if n != "esame"})
    salva("tempi", out)


PARTI = {"base": parte_base, "esame": parte_esame, "costi": parte_costi, "conto": parte_conto, "rischio": parte_rischio,
         "misure": parte_misure, "sensi": parte_sensi, "taglio": parte_taglio, "dati": parte_dati, "buchi": parte_buchi,
         "avanti": parte_avanti, "ultima": parte_ultima, "misto": parte_misto, "ore_rischio": parte_ore_rischio, "partenze": parte_partenze, "tempi": parte_tempi}

if __name__ == "__main__":
    PARTI[A.parte]()
