"""Audit della prova 28 (K2 e F5 + M7 + K2 a rischio uguale), 11 novembre 2026: riproduzione con i dati di oggi, sguardo
nel futuro (prova del taglio), entrata ritardata, conto fatto su un solo conto con le posizioni compensate, costi di
riequilibrio, perdita peggiore nella settimana e nel giorno, filtri del conto vero, misure, sensibilità e Sharpe corretto.

Solo lettura della ricerca: importa le funzioni, non esegue nessun ``main``. Ha bisogno delle previsioni di M7 ricalcolate da
``prova28_m7_2026-11-11.py`` (cartella come argomento). Scrive solo ``audits/repro/prova28_2026-11-11_esito.json``.

Uso: python3 audits/repro/prova28_2026-11-11.py <cartella_m7>
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd

from research.programma6 import asticella as ast
from research.programma6 import dodicesima as do
from research.programma6 import nona as no
from research.programma6 import ottava as ot
from research.programma6 import quindicesima as qd
from research.programma6 import seconda as sc
from research.programma6 import terza as te
from research.programma6 import undicesima as un
from research.programma6 import venticinquesima as v25
from research.programma6 import ventiquattresima as vq

QUI = Path(__file__).parent
RADICE = QUI.parents[1]
P6 = RADICE / "research" / "programma6"
INIZIO = sc.giorno(2022, 1, 3)
FINE_ORIGINALE = sc.giorno(2026, 10, 12)        # ultimo lunedi' della prova del 20 ottobre (250 settimane)
FINE_FUNDING_VERO = sc.giorno(2026, 10, 19)     # ultimo lunedi' con il funding della settimana tutto vero
N_REGISTRO, N_BRIEF = 308, 309


# ---------------------------------------------------------------------------
# componenti con parametri (per la sensibilita'); con i valori di base sono identiche alle funzioni della ricerca
# ---------------------------------------------------------------------------

def sigma(pan, lun, giorni=30):
    if giorni == 30:
        return ot.sigma_30(pan, lun)
    C = pan["close"]
    with np.errstate(all="ignore"):
        r = np.vstack([np.full((1, C.shape[1]), np.nan), C[1:] / C[:-1] - 1])
    out = np.full((len(lun), C.shape[1]), np.nan)
    minimo = math.ceil(giorni * 20 / 30)
    for k, m in enumerate(lun):
        f = r[max(0, m - giorni): m]
        n = np.isfinite(f).sum(axis=0)
        with np.errstate(all="ignore"):
            import warnings
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", RuntimeWarning)
                sd = np.nanstd(f, axis=0, ddof=1)
        out[k] = np.where((n >= minimo) & (sd > 0), sd, np.nan)
    return out


def funding_k(pan, lun, k=7):
    Fc = np.vstack([np.zeros((1, pan["funding"].shape[1])), np.cumsum(pan["funding"], axis=0)])
    return np.round(Fc[lun] - Fc[lun - k], 12)


def acquisti_k(pan, lun, k=7):
    if k == 7:
        return no.g1(pan, lun)
    V, B = pan["quote_volume"], pan["taker_buy_quote_volume"]
    out = np.full((len(lun), V.shape[1]), np.nan)
    minimo = math.ceil(5 * k / 7)
    for i, m in enumerate(lun):
        v, b = V[max(0, m - k): m], B[max(0, m - k): m]
        ok = np.isfinite(v) & np.isfinite(b) & (v > 0)
        sv, sb = np.where(ok, v, 0).sum(axis=0), np.where(ok, b, 0).sum(axis=0)
        with np.errstate(all="ignore"):
            out[i] = np.where((ok.sum(axis=0) >= minimo) & (sv > 0), sb / sv, np.nan)
    return out


def oi_k(pm, lun, k=7):
    oi = pm["oi"]
    with np.errstate(all="ignore"):
        out = np.log(oi[lun - 1]) - np.log(oi[lun - 1 - k])
    out[~np.isfinite(out)] = np.nan
    return out


def segnale_k1(pan, ps, pm, k=7):
    lun = ps["lunedi"] - pan["t0"]
    if k == 7:
        return do.segnale_k1(pan, ps, pm)
    parti = [-funding_k(pan, lun, k), acquisti_k(pan, lun, k), oi_k(pm, lun, k)]
    Z = np.stack(parti, axis=2)
    R = te.ranghi(np.where(np.isfinite(Z), Z, np.nan), ps["U"])
    ok = np.isfinite(Z)
    somma = np.where(ok, R, 0.0).sum(axis=2)
    n = ok.sum(axis=2)
    with np.errstate(all="ignore"):
        kk = somma / n
    return np.where(ok[:, :, 0] & (n >= 2), kk, np.nan)


def banda(ct, U, sig, entra=0.20, resta=0.40):
    vecchi = (vq.ENTRA, vq.RESTA)
    vq.ENTRA, vq.RESTA = entra, resta
    try:
        return vq.pesi_banda(ct, U, sig)
    finally:
        vq.ENTRA, vq.RESTA = vecchi


def conto(W, ps, costo):
    df = te.conto(W, ps["R"], ps["F"], costo)
    df.index = ps["lunedi"]
    return df


def tre_pesi(pan, ps, pm, Pm, costo, entra=0.20, resta=0.40, giorni_sig=30, k=7):
    lun = ps["lunedi"] - pan["t0"]
    sig = sigma(pan, lun, giorni_sig)
    W = {"F5": banda(np.where(np.isfinite(sig), -funding_k(pan, lun, k), np.nan), ps["U"], sig, entra, resta),
         "K2": banda(np.where(np.isfinite(sig), segnale_k1(pan, ps, pm, k), np.nan), ps["U"], sig, entra, resta)}
    if Pm is not None:
        W["M7"] = banda(np.where(np.isfinite(sig), Pm, np.nan), ps["U"], sig, entra, resta)
    return W, sig


# ---------------------------------------------------------------------------
# misure
# ---------------------------------------------------------------------------

def periodo(df, fine):
    return df[(df.index >= INIZIO) & (df.index <= fine)]


def misure(x: pd.Series, spese: pd.Series | None = None) -> dict:
    v = x.to_numpy(float)
    n = te.numeri_settimana(x)
    giu = v[v < 0]
    dd = np.sqrt((np.minimum(v, 0) ** 2).mean())
    eq = np.cumprod(1 + v)
    picco = np.maximum.accumulate(eq)
    sotto = eq < picco
    lunga, cur = 0, 0
    for s in sotto:
        cur = cur + 1 if s else 0
        lunga = max(lunga, cur)
    date = pd.to_datetime(x.index.to_numpy() * 86400, unit="s")
    per_anno = {int(a): float(x[date.year == a].mean() * 52) for a in sorted(set(date.year))}
    mesi = x.groupby(date.to_period("M")).sum()
    pos = v[v > 0].sum()
    out = {**{k: round(float(val), 4) for k, val in n.items()},
           "t": round(n["sharpe"] * math.sqrt(n["settimane"] / 52), 3),
           "sortino": round(float(v.mean() / dd * math.sqrt(52)), 3) if dd > 0 else None,
           "discesa_durata_settimane": int(lunga), "cumulato": round(float(eq[-1] - 1), 3),
           "profit_factor_settimane": round(float(pos / -giu.sum()), 3) if len(giu) else None,
           "settimane_positive": round(float((v > 0).mean()), 3),
           "per_anno": {a: round(val, 4) for a, val in per_anno.items()},
           "anni_positivi": f"{sum(1 for val in per_anno.values() if val > 0)}/{len(per_anno)}",
           "quota_5_settimane_migliori": round(float(np.sort(v)[-5:].sum() / v.sum()), 3),
           "quota_3_mesi_migliori": round(float(np.sort(mesi.to_numpy())[-3:].sum() / v.sum()), 3),
           "senza_5_settimane_migliori_sharpe": round(te.numeri_settimana(pd.Series(np.sort(v)[:-5]))["sharpe"], 3)}
    if spese is not None:
        out["media_settimana"] = round(float(v.mean()), 5)
        out["spese_medie_settimana"] = round(float(spese.mean()), 5)
    return out


def sharpe(x):
    return round(te.numeri_settimana(x)["sharpe"], 3)


# ---------------------------------------------------------------------------
# prova del taglio: i pesi di un lunedi' calcolati con i soli dati fino a quel momento
# ---------------------------------------------------------------------------

def tagliato(pan, pm, m):
    """Pannello con le righe fino alla domenica ``m - 1``, l'apertura del lunedi' ``m`` e sette giorni vuoti dopo."""
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
    pm2 = {}
    for k, a in pm.items():
        b = np.full((T2, a.shape[1]), np.nan)
        b[:m] = a[:m]
        pm2[k] = b
    return out, pm2


def prova_taglio(pan, pm, Wpieni, lunedi_pieni, date) -> dict:
    esiti = {}
    for d in date:
        g = sc.giorno(*d)
        m = g - pan["t0"]
        p2, pm2 = tagliato(pan, pm, m)
        ps2 = te.pannello_settimane(p2, log=lambda x: None, indicatori_si=False)
        W2, _ = tre_pesi(p2, ps2, pm2, None, None)
        w2 = int(np.flatnonzero(ps2["lunedi"] == g)[0])
        w1 = int(np.flatnonzero(lunedi_pieni == g)[0])
        esiti[sc.data(g)] = {n: float(np.abs(W2[n][w2] - Wpieni[n][w1]).max()) for n in ("F5", "K2")}
    return esiti


# ---------------------------------------------------------------------------
# il conto su un solo conto (posizioni compensate) e la perdita peggiore
# ---------------------------------------------------------------------------

def pesi_insieme(W, pesi):
    out = np.zeros_like(W["F5"])
    for n in ("F5", "M7", "K2"):
        out += pesi[n].to_numpy()[:, None] * W[n]
    return out


def perdita_peggiore(pan, ps, Wc, sett):
    """Per ogni settimana: il giorno peggiore (apertura su apertura) e il peggio possibile nella settimana con i minimi per i
    long e i massimi per gli short tutti insieme (limite prudente)."""
    O, H, L = pan["open"], pan["high"], pan["low"]
    r = sc.rendimenti(pan)
    lun = ps["lunedi"] - pan["t0"]
    peggior_giorno, peggior_sett, giorni_sotto_5 = [], [], 0
    for w in sett:
        m = lun[w]
        x = Wc[w]
        j = np.flatnonzero(x != 0)
        if not len(j):
            continue
        cum = np.cumprod(1 + r[m:m + 7, j], axis=0)
        val = 1 + (x[j] * (cum - 1)).sum(axis=1)
        prima = np.concatenate([[1.0], val[:-1]])
        g = val / prima - 1
        giorni_sotto_5 += int((g < -0.05).sum())
        peggior_giorno.append((float(g.min()), sc.data(int(ps["lunedi"][w]))))
        o0 = O[m, j]
        with np.errstate(all="ignore"):
            hmax = np.nanmax(H[m:m + 7, j], axis=0) / o0 - 1
            lmin = np.nanmin(L[m:m + 7, j], axis=0) / o0 - 1
        avverso = np.where(x[j] > 0, np.nan_to_num(lmin), np.nan_to_num(hmax))
        peggior_sett.append((float((x[j] * avverso).sum()), sc.data(int(ps["lunedi"][w]))))
    pg = sorted(peggior_giorno)[:3]
    pw = sorted(peggior_sett)[:3]
    return {"giorno_peggiore": [[round(a, 4), b] for a, b in pg], "giorni_sotto_meno_5%": giorni_sotto_5,
            "settimana_peggiore_tutti_gli_estremi_insieme": [[round(a, 4), b] for a, b in pw],
            "esposizione_lorda_media": round(float(np.abs(Wc[sett]).sum(axis=1).mean()), 3),
            "esposizione_lorda_massima": round(float(np.abs(Wc[sett]).sum(axis=1).max()), 3),
            "peso_massimo_di_una_moneta": round(float(np.abs(Wc[sett]).max()), 4)}


def filtri(pan, ps, Wc, sett, capitale) -> dict:
    """Ordini del lunedi' (variazioni dei pesi compensati) sotto il valore minimo del conto vero e scarto dell'arrotondamento
    della quantita'. Il capitale resta fisso (prudente: un conto che cresce ha ordini piu' grandi)."""
    fl = json.loads((RADICE / "bot" / "portafoglio" / "filtri_conto_vero.json").read_text())["filtri"]
    O = pan["open"]
    lun = ps["lunedi"] - pan["t0"]
    R0 = np.nan_to_num(ps["R"])
    sotto, tot, val_sotto, val_tot, senza, err = 0, 0, 0.0, 0.0, 0, []
    pos_sotto, pos_tot = 0, 0
    for w in sett:
        prima = Wc[w - 1] * (1 + R0[w - 1]) if w > 0 else np.zeros(Wc.shape[1])
        d = np.abs(Wc[w] - prima) * capitale
        for j in np.flatnonzero(d > 1e-9):
            s = ps["simboli"][j]
            f = fl.get(s)
            tot += 1
            val_tot += d[j]
            if f is None:
                senza += 1
                continue
            if d[j] < f["valore_minimo"]:
                sotto += 1
                val_sotto += d[j]
            q = d[j] / O[lun[w], j]
            if q > 0 and np.isfinite(q):
                qa = round(q / f["passo"]) * f["passo"]
                err.append(abs(qa - q) / q)
        for j in np.flatnonzero(Wc[w] != 0):
            f = fl.get(ps["simboli"][j])
            if f is None:
                continue
            pos_tot += 1
            if abs(Wc[w, j]) * capitale < f["valore_minimo"]:
                pos_sotto += 1
    return {"capitale_usdt": capitale, "ordini": tot, "ordini_sotto_il_minimo": round(sotto / tot, 3),
            "valore_degli_ordini_sotto_il_minimo": round(val_sotto / val_tot, 3),
            "ordini_su_monete_senza_filtro_oggi": round(senza / tot, 3),
            "posizioni_sotto_il_minimo": round(pos_sotto / max(pos_tot, 1), 3),
            "errore_arrotondamento_mediano": round(float(np.median(err)), 4) if err else None,
            "errore_arrotondamento_95": round(float(np.quantile(err, 0.95)), 4) if err else None}


def climi(x: pd.Series, pan, ps) -> dict:
    """Clima del mese (dichiarato qui, prima di guardare): Bitcoin nel mese del lunedi' sopra +5% rialzo, sotto -5% ribasso,
    altrimenti laterale (chiusure giornaliere del pannello)."""
    jb = pan["simboli"].index("BTCUSDT")
    c = pd.Series(pan["close"][:, jb], index=pd.to_datetime((np.arange(len(pan["close"])) + pan["t0"]) * 86400, unit="s"))
    mens = c.resample("ME").last().pct_change()
    mens.index = mens.index.to_period("M")
    date = pd.to_datetime(x.index.to_numpy() * 86400, unit="s").to_period("M")
    clima = np.where(mens.reindex(date).to_numpy() > 0.05, "rialzo", np.where(mens.reindex(date).to_numpy() < -0.05, "ribasso", "laterale"))
    out = {}
    for k in ("rialzo", "laterale", "ribasso"):
        s = x[clima == k]
        out[k] = {"settimane": int(len(s)), "annuo": round(float(s.mean() * 52), 4), "sharpe": sharpe(s)}
    return out


# ---------------------------------------------------------------------------

def main(cartella_m7: Path) -> dict:
    pan = sc.pannello()
    ps = te.pannello_settimane(pan, log=lambda x: None, indicatori_si=False)
    pm = un.pannello_metrics(pan)
    lun = ps["lunedi"] - pan["t0"]
    costo = sc.costi_moneta(ps["simboli"])
    Pm = np.load(cartella_m7 / "Pm.npy")
    assert (np.load(cartella_m7 / "lunedi.npy") == ps["lunedi"]).all()
    W, sig = tre_pesi(pan, ps, pm, Pm, costo)
    comp = {n: conto(W[n], ps, costo) for n in W}
    tre = qd.combina({"F5": comp["F5"], "M7": comp["M7"], "K2": comp["K2"]})
    out = {"pannello": {"primo": sc.data(pan["t0"]), "ultimo": sc.data(pan["t0"] + pan["close"].shape[0] - 1)}}

    # 1. riproduzione: file della prova (20 ottobre), file dopo le parita' (23 ottobre), oggi
    vecchi = {"K2": pd.read_csv(P6 / "risultati_ventottesima" / "settimane_K2.csv.gz", index_col=0),
              "F5 + M7 + K2": pd.read_csv(P6 / "risultati_ventottesima" / "settimane_F5_M7_K2.csv.gz", index_col=0)}
    parita = {"K2": pd.read_csv(P6 / "risultati_controllo_parita" / "settimane_K2.csv.gz", index_col=0),
              "F5 + M7 + K2": pd.read_csv(P6 / "risultati_controllo_parita" / "settimane_F5_M7_K2.csv.gz", index_col=0)}
    oggi = {"K2": comp["K2"], "F5 + M7 + K2": tre}
    rip = {}
    for n in oggi:
        a, b, c = (periodo(x, FINE_ORIGINALE)["netto"] for x in (vecchi[n], parita[n], oggi[n]))
        rip[n] = {"sharpe_file_prova": sharpe(a), "sharpe_file_parita": sharpe(b), "sharpe_oggi_stesse_250": sharpe(c),
                  "settimane_diverse_da_parita": int(((b - c).abs() > 1e-9).sum()),
                  "settimane_diverse": [sc.data(int(t)) for t in (b - c)[(b - c).abs() > 1e-9].index][:6]}
    out["riproduzione"] = rip

    # 2. misure su tre periodi
    per = {}
    for nome_p, fine in (("fino_al_2026-10-12", FINE_ORIGINALE), ("fino_al_2026-10-19_funding_vero", FINE_FUNDING_VERO),
                         ("fino_al_2026-11-02_ultima_settimana_stimata", int(ps["lunedi"][-1]))):
        per[nome_p] = {"K2": misure(periodo(comp["K2"], fine)["netto"], periodo(comp["K2"], fine)["spese"]),
                       "F5 + M7 + K2": misure(periodo(tre, fine)["netto"]),
                       "F5": {"sharpe": sharpe(periodo(comp["F5"], fine)["netto"])},
                       "M7": {"sharpe": sharpe(periodo(comp["M7"], fine)["netto"])}}
    out["misure"] = per
    d = periodo(tre, FINE_FUNDING_VERO)
    out["pesi_medi_della_miscela"] = {n: round(float(d[f"peso_{n}"].mean()), 3) for n in ("F5", "M7", "K2")}
    out["pesi_primo_trimestre_2022"] = {n: round(float(d[f"peso_{n}"][d.index < sc.giorno(2022, 4, 4)].mean()), 3) for n in ("F5", "M7", "K2")}
    out["correlazioni"] = {f"{a}-{b}": round(float(np.corrcoef(periodo(comp[a], FINE_FUNDING_VERO)["netto"], periodo(comp[b], FINE_FUNDING_VERO)["netto"])[0, 1]), 3)
                           for a, b in (("F5", "K2"), ("F5", "M7"), ("K2", "M7"))}

    # 3. M7 prima del 2022 vale zero (non ha previsioni): la volatilita' delle 26 settimane della miscela parte con gli zeri
    m7n = comp["M7"].copy()
    m7n.loc[m7n.index < INIZIO, ["netto", "netto_doppio"]] = np.nan
    tre_nan = qd.combina({"F5": comp["F5"], "M7": m7n, "K2": comp["K2"]})
    out["miscela_senza_gli_zeri_di_M7"] = {"sharpe": sharpe(periodo(tre_nan, FINE_FUNDING_VERO)["netto"]),
                                           "per_anno": misure(periodo(tre_nan, FINE_FUNDING_VERO)["netto"])["per_anno"],
                                           "peso_M7_primo_trimestre_2022": round(float(periodo(tre_nan, sc.giorno(2022, 3, 28))["peso_M7"].mean()), 3)}
    eq = {n: periodo(comp[n], FINE_FUNDING_VERO)["netto"] for n in ("F5", "M7", "K2")}
    uguale = (eq["F5"] + eq["M7"] + eq["K2"]) / 3
    out["miscela_a_terzi_fissi"] = {"sharpe": sharpe(uguale), "per_anno": misure(uguale)["per_anno"]}

    # 4. un solo conto: pesi compensati fra le tre, con il riequilibrio pagato
    pesi = tre[["peso_F5", "peso_M7", "peso_K2"]].rename(columns=lambda c: c[5:])
    Wc = pesi_insieme(W, pesi)
    unico = conto(Wc, ps, costo)
    u = periodo(unico, FINE_FUNDING_VERO)
    out["un_solo_conto"] = {"sharpe": sharpe(u["netto"]), "annuo": round(float(u["netto"].mean() * 52), 4),
                            "spese_annue": round(float(u["spese"].mean() * 52), 4), "giro_medio": round(float(u["giro"].mean()), 3),
                            "per_anno": misure(u["netto"])["per_anno"],
                            "spese_annue_somma_delle_tre": round(float(sum(periodo(comp[n], FINE_FUNDING_VERO)["spese"].mean() * pesi.loc[u.index, n].mean() for n in ("F5", "M7", "K2")) * 52), 4)}

    # 5. costi: doppi e scarto delle altre allo 0,10%
    costo10 = np.array([sc.TAKER + (0.0001 if s in ("BTCUSDT", "ETHUSDT", "SOLUSDT") else 0.0010) for s in ps["simboli"]])
    u10 = periodo(conto(Wc, ps, costo10), FINE_FUNDING_VERO)
    out["costi"] = {"taker": sc.TAKER, "scarto_altre": 0.0002, "costo_per_giro_btc": float(costo[ps["simboli"].index("BTCUSDT")]),
                    "un_solo_conto_costi_doppi_sharpe": sharpe(u["netto"] - u["spese"]),
                    "un_solo_conto_scarto_altre_0,10%_sharpe": sharpe(u10["netto"])}

    # 6. entrata ritardata di un giorno (martedi' apertura -> martedi' dopo)
    r = sc.rendimenti(pan)
    lr = np.log1p(np.clip(r, -0.999999, None))
    cum = np.vstack([np.zeros((1, r.shape[1])), np.cumsum(lr, axis=0)])
    Fc = np.vstack([np.zeros((1, r.shape[1])), np.cumsum(pan["funding"], axis=0)])
    ok = lun + 8 <= r.shape[0]
    R1 = np.full_like(ps["R"], np.nan)
    F1 = np.zeros_like(ps["F"])
    R1[ok] = np.expm1(cum[lun[ok] + 8] - cum[lun[ok] + 1])
    F1[ok] = Fc[lun[ok] + 8] - Fc[lun[ok] + 1]
    rit = {}
    for n in ("F5", "M7", "K2"):
        x = te.conto(W[n], R1, F1, costo)
        x.index = ps["lunedi"]
        rit[n] = x
    tre_r = qd.combina(rit)
    out["entrata_un_giorno_dopo"] = {"K2": sharpe(periodo(rit["K2"], FINE_FUNDING_VERO)["netto"]),
                                     "F5 + M7 + K2": sharpe(periodo(tre_r, FINE_FUNDING_VERO)["netto"])}

    # 7. sguardo nel futuro: prova del taglio su sei lunedi'
    out["prova_del_taglio_differenza_massima_dei_pesi"] = prova_taglio(
        pan, pm, W, ps["lunedi"], [(2022, 3, 7), (2022, 11, 14), (2023, 6, 5), (2024, 8, 5), (2025, 4, 7), (2026, 10, 12)])

    # 8. perdita peggiore, leva, filtri del conto vero
    sett = np.flatnonzero((ps["lunedi"] >= INIZIO) & (ps["lunedi"] <= FINE_FUNDING_VERO))
    out["perdita_peggiore_un_solo_conto"] = perdita_peggiore(pan, ps, Wc, sett)
    out["perdita_peggiore_K2"] = perdita_peggiore(pan, ps, W["K2"], sett)
    out["filtri"] = [filtri(pan, ps, Wc, sett, c) for c in (280, 1000, 10000)]
    out["climi"] = {"K2": climi(periodo(comp["K2"], FINE_FUNDING_VERO)["netto"], pan, ps),
                    "F5 + M7 + K2": climi(periodo(tre, FINE_FUNDING_VERO)["netto"], pan, ps)}

    # 9. contributo delle monete a K2 (lordo)
    lordo_m = (W["K2"][sett] * np.nan_to_num(ps["R"][sett])).sum(axis=0)
    ordine = np.argsort(-np.abs(lordo_m))[:8]
    out["K2_monete_che_pesano_di_piu_lordo"] = {ps["simboli"][j]: round(float(lordo_m[j]), 3) for j in ordine}
    out["K2_lordo_totale"] = round(float(lordo_m.sum()), 3)

    # 10. sensibilita' (+-10% e +-20%): banda, finestra della volatilita', giorni dei segnali, finestra della miscela, universo
    sens = {}
    F = FINE_FUNDING_VERO

    def una(etichetta, **kw):
        W2, _ = tre_pesi(pan, ps, pm, Pm, costo, **kw)
        c2 = {n: conto(W2[n], ps, costo) for n in W2}
        t2 = qd.combina({"F5": c2["F5"], "M7": c2["M7"], "K2": c2["K2"]})
        sens[etichetta] = {"K2": sharpe(periodo(c2["K2"], F)["netto"]), "F5 + M7 + K2": sharpe(periodo(t2, F)["netto"]),
                           "anni_positivi_miscela": misure(periodo(t2, F)["netto"])["anni_positivi"],
                           "anni_positivi_K2": misure(periodo(c2["K2"], F)["netto"])["anni_positivi"]}

    for e in (0.16, 0.18, 0.22, 0.24):
        una(f"entrata {e}", entra=e)
    for rr in (0.32, 0.36, 0.44, 0.48):
        una(f"uscita {rr}", resta=rr)
    for g in (24, 27, 33, 36):
        una(f"volatilita' {g} giorni", giorni_sig=g)
    for k in (6, 8):
        una(f"segnali {k} giorni (F5 e K2)", k=k)
    for fin in (21, 23, 29, 31):
        t2 = qd.combina({"F5": comp["F5"], "M7": comp["M7"], "K2": comp["K2"]}, finestra=fin, minimo=min(13, fin // 2))
        sens[f"miscela {fin} settimane"] = {"F5 + M7 + K2": sharpe(periodo(t2, F)["netto"]),
                                            "anni_positivi_miscela": misure(periodo(t2, F)["netto"])["anni_positivi"]}
    for n_u in (80, 90, 110, 120):
        ps2 = te.pannello_settimane(pan, log=lambda x: None, a=n_u, indicatori_si=False)
        W2, _ = tre_pesi(pan, ps2, pm, None, costo)
        c2 = {n: conto(W2[n], ps2, costo) for n in W2}
        t2 = qd.combina({"F5": c2["F5"], "M7": comp["M7"], "K2": c2["K2"]})
        sens[f"universo {n_u} (M7 resta a 100)"] = {"K2": sharpe(periodo(c2["K2"], F)["netto"]),
                                                     "F5 + M7 + K2": sharpe(periodo(t2, F)["netto"])}
    out["sensibilita"] = sens

    # 11. Sharpe corretto: come la prova (52 prove), come l'asticella del 23 ottobre (gruppi) e come le prove di oggi (N = conto)
    sr = v25.prove_fino_alla_ventiquattresima()
    e25 = json.loads((P6 / "risultati_venticinquesima" / "esame.json").read_text())
    sr += [e25["M7"]["intero"]["sharpe"], e25["F5 + M7"]["intero"]["sharpe"]]
    e28 = json.loads((P6 / "risultati_ventottesima" / "esame.json").read_text())
    sr52 = sr + [e28["K2"]["intero"]["sharpe"], e28["F5 + M7 + K2"]["intero"]["sharpe"]]
    prove = ast.le_prove()
    serie = {n: ast.periodo(s) for n, s, _ in prove if s is not None}
    serie.update({n: ast.periodo(s) for n, s in ast.serie_nuove().items()})
    soli = [x for _, s, x in prove if s is None]
    gr = ast.gruppi(serie, ast.TAGLIO)
    sr_tutti = ast.per_v(gr, soli, False)
    sr_v = ast.per_v(gr, soli, True)
    dsr = {"prove_nella_lista_52": len(sr52), "gruppi": len(sr_tutti), "gruppi_in_V": len(sr_v),
           "deviazione_V": round(float(np.std(sr_v, ddof=1)), 3)}
    for n, nome_g in (("K2", "28 K2"), ("F5 + M7 + K2", "28 F5+M7+K2")):
        dsr[n] = {"gruppo": next((g["membri"] for g in gr if nome_g in g["membri"]), [])}
        for nome_p, fine in (("2026-10-12", FINE_ORIGINALE), ("2026-10-19", FINE_FUNDING_VERO)):
            x = periodo(oggi[n], fine)["netto"]
            i = te.numeri_settimana(x)
            a = (i["sharpe"], i["settimane"], i["asimmetria"], i["curtosi"])
            dsr[n][nome_p] = {"sharpe": round(i["sharpe"], 3), "t": round(i["sharpe"] * math.sqrt(i["settimane"] / 52), 2),
                              "come_la_prova_52": round(te.sharpe_corretto(*a, sr52, 52), 3),
                              "gruppi_23_ottobre": round(te.sharpe_corretto(*a, sr_v, 52, n_prove=len(sr_tutti)), 3),
                              f"N_{N_REGISTRO}": round(te.sharpe_corretto(*a, sr_v, 52, n_prove=N_REGISTRO), 3),
                              f"N_{N_BRIEF}": round(te.sharpe_corretto(*a, sr_v, 52, n_prove=N_BRIEF), 3)}
    # file della prova, per riprodurre 0,47 e 0,76
    for n in ("K2", "F5 + M7 + K2"):
        i = e28[n]["intero"]
        dsr[n]["file_della_prova_come_scritto"] = round(te.sharpe_corretto(i["sharpe"], i["settimane"], i["asimmetria"], i["curtosi"], sr52, 52), 3)
    out["sharpe_corretto"] = dsr
    (QUI / "prova28_2026-11-11_esito.json").write_text(json.dumps(out, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    return out


if __name__ == "__main__":
    o = main(Path(sys.argv[1]))
    print(json.dumps(o["riproduzione"], ensure_ascii=False))
    print(json.dumps(o["sharpe_corretto"], ensure_ascii=False)[:1500])
    print(json.dumps(o["prova_del_taglio_differenza_massima_dei_pesi"], ensure_ascii=False))
