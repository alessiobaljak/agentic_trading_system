"""Riesame della prova 55 (C3: un solo punteggio dalla media dei ranghi di F5, K2 e M7, con la banda di F5), 12 novembre 2026.

Solo lettura della ricerca: importa le funzioni, non esegue nessun ``main`` (catalogo, voce 11). Ha bisogno delle previsioni di
M7 rifatte con ``prova28_m7_2026-11-11.py`` (cartella come argomento: ``Pm.npy``, ``lunedi.npy``, ``Ps_seme1.npy``). Scrive solo
``audits/repro/prova55_2026-11-12_esito_<parte>.json``.

Parti:
  base         riproduzione del file della prova (con il residuo delle parita'), C3 corretta, F5 e F5 + M7 + K2 sulle stesse
               settimane, esame come scritto e con le regole di oggi, Sharpe corretto in tutti i modi, misure, climi
  m7r          M7 con gli ingredienti di funding arrotondati a 12 decimali (il residuo anche dentro il modello); scrive Pm_r.npy
               nella cartella data
  sensibilita  +-10% e +-20% su banda, volatilita', giorni dei segnali, universo; C3 e F5 con lo stesso cambio
  tempi        prova del taglio (C3 e M7 seme 1), entrata un giorno dopo, entrata all'01:00 e alle 04:00
  dati         buchi, anomalie, monete ferme, funding stimato, candele grezze, interesse aperto, perdita nei buchi del 2022
  rischio      perdita peggiore nel giorno e nella settimana, peso massimo, filtri del conto vero, conto a 280 e 1.000 USDT
  m7r_dsr      Sharpe corretto di C3 con M7 arrotondato (dopo ``m7r``)
  zombi        posizioni tenute nei giorni a volume zero (moneta tolta dal listino a meta' settimana)
  senza        solo per capire: il punteggio senza K1 (funding e M7) e senza M7 (funding e K1)

Uso: PYTHONPATH=<radice> python3 audits/repro/prova55_2026-11-12.py <parte> <cartella_m7>
"""
from __future__ import annotations

import importlib
import json
import math
import sys
from collections import Counter
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))

from research.programma5.strumenti import motore5 as m5  # noqa: E402
from research.programma6 import asticella as ast  # noqa: E402
from research.programma6 import cinquantacinquesima as cq  # noqa: E402
from research.programma6 import dodicesima as do  # noqa: E402
from research.programma6 import esecuzione as es  # noqa: E402
from research.programma6 import ottava as ot  # noqa: E402
from research.programma6 import quattordicesima as q  # noqa: E402
from research.programma6 import quindicesima as qd  # noqa: E402
from research.programma6 import seconda as sc  # noqa: E402
from research.programma6 import sesta as se  # noqa: E402
from research.programma6 import terza as te  # noqa: E402
from research.programma6 import undicesima as un  # noqa: E402
from research.programma6 import ventitreesima as vt  # noqa: E402
from research.src.dati import funding_da_zip  # noqa: E402

a28 = importlib.import_module("prova28_2026-11-11")

QUI = Path(__file__).parent
RADICE = QUI.parents[1]
P6 = RADICE / "research" / "programma6"
INIZIO = sc.giorno(2022, 1, 3)                 # CINQUANTACINQUESIMA.md, sezione 2 (q.INIZIO)
FINE_DICHIARATA = sc.giorno(2026, 10, 5)       # «al 5 ottobre 2026» (ultimo lunedi', convenzione di asticella.periodo)
FINE_PROVA = sc.giorno(2026, 10, 12)           # ultimo lunedi' del file della prova (23 ottobre)
N_CONTO = 312                                  # python3 -m research.src.registro --riepilogo, 12 novembre 2026


def esito_file(parte: str) -> Path:
    return QUI / f"prova55_2026-11-12_esito_{parte}.json"


# ---------------------------------------------------------------------------
# componenti (con i valori di base identiche alle funzioni della ricerca; controllato in ``base``)
# ---------------------------------------------------------------------------

def f7(pan, lun, k=7, residuo=False):
    """Il funding dei k giorni prima del lunedi'; ``residuo`` = come il 23 ottobre alle 04:23 (senza l'arrotondamento)."""
    Fc = np.vstack([np.zeros((1, pan["funding"].shape[1])), np.cumsum(pan["funding"], axis=0)])
    x = Fc[lun] - Fc[lun - k]
    return x if residuo else np.round(x, 12)


def k1(pan, ps, pm, k=7, residuo=False):
    lun = ps["lunedi"] - pan["t0"]
    parti = [-f7(pan, lun, k, residuo), a28.acquisti_k(pan, lun, k), a28.oi_k(pm, lun, k)]
    Z = np.stack(parti, axis=2)
    R = te.ranghi(np.where(np.isfinite(Z), Z, np.nan), ps["U"])
    ok = np.isfinite(Z)
    with np.errstate(all="ignore"):
        kk = np.where(ok, R, 0.0).sum(axis=2) / ok.sum(axis=2)
    return np.where(ok[:, :, 0] & (ok.sum(axis=2) >= 2), kk, np.nan)


def pesi(pan, ps, pm, Pm, residuo=False, entra=0.20, resta=0.40, giorni_sig=30, k=7, minimo=2):
    """I pesi di C3, F5, K2 e M7 (M7 solo se ``Pm`` c'e')."""
    lun = ps["lunedi"] - pan["t0"]
    sig = a28.sigma(pan, lun, giorni_sig)
    f = -f7(pan, lun, k, residuo)
    kk = k1(pan, ps, pm, k, residuo)
    W = {"F5": a28.banda(np.where(np.isfinite(sig), f, np.nan), ps["U"], sig, entra, resta),
         "K2": a28.banda(np.where(np.isfinite(sig), kk, np.nan), ps["U"], sig, entra, resta)}
    if Pm is not None:
        c = punteggio(f, kk, Pm, ps["U"], minimo)
        W["C3"] = a28.banda(np.where(np.isfinite(sig), c, np.nan), ps["U"], sig, entra, resta)
        W["M7"] = a28.banda(np.where(np.isfinite(sig), Pm, np.nan), ps["U"], sig, entra, resta)
    return W, sig


def punteggio(f, k, m, U, minimo=2):
    if minimo == 2:
        return cq.punteggio(f, k, m, U)
    Z = np.stack([f, k, m], axis=2)
    ok = np.isfinite(Z)
    R = te.ranghi(np.where(ok, Z, np.nan), U)
    n = ok.sum(axis=2)
    with np.errstate(all="ignore"):
        s = np.where(ok, R, 0.0).sum(axis=2) / n
    return np.where(ok[:, :, 0] & (n >= minimo) & U, s, np.nan)


def conti(W, ps, costo):
    out = {n: a28.conto(W[n], ps, costo) for n in W}
    if all(n in out for n in ("F5", "M7", "K2")):
        out["F5+M7+K2"] = qd.combina({"F5": out["F5"], "M7": out["M7"], "K2": out["K2"]})
    return out


def taglia(df, fine, inizio=INIZIO):
    return df[(df.index >= inizio) & (df.index <= fine)]


def sharpe(x):
    return round(te.numeri_settimana(x)["sharpe"], 3)


def anni(x):
    date = pd.to_datetime(x.index.to_numpy() * 86400, unit="s")
    pa = {int(a): float(x[date.year == a].mean() * 52) for a in sorted(set(date.year))}
    return {"per_anno": {a: round(v, 4) for a, v in pa.items()}, "positivi": f"{sum(v > 0 for v in pa.values())}/{len(pa)}"}


def base_comune(cartella: Path, indicatori=False):
    pan = sc.pannello()
    ps = te.pannello_settimane(pan, log=lambda x: None, indicatori_si=indicatori)
    pm = un.pannello_metrics(pan)
    costo = sc.costi_moneta(ps["simboli"])
    Pm = np.load(cartella / "Pm.npy")
    assert (np.load(cartella / "lunedi.npy") == ps["lunedi"]).all()
    return pan, ps, pm, costo, Pm


def settimane_vere(pan, ps, W) -> dict:
    """Per ogni lunedi' dal 1 settembre 2026: i giorni-moneta tenuti con il funding stimato (media dei 90 giorni)."""
    lun = ps["lunedi"] - pan["t0"]
    out = {}
    da_sett = np.flatnonzero(ps["lunedi"] >= sc.giorno(2026, 9, 1))
    tenute = np.flatnonzero((np.abs(W).sum(axis=0) > 0) | ps["U"][da_sett].any(axis=0))
    reali = {}
    for j in tenute:
        righe = []
        for p in sorted((sc.DATI / ps["simboli"][j] / "funding").glob("*.zip")):
            righe += funding_da_zip(p)
        df = pd.DataFrame(righe, columns=["ts", "ore", "tasso"]).drop_duplicates("ts") if righe else pd.DataFrame(columns=["ts"])
        reali[j] = set(((df["ts"].to_numpy(np.int64) // 60_000 - 1) // 1440).tolist())
    for w in np.flatnonzero(ps["lunedi"] >= sc.giorno(2026, 9, 1)):
        m = lun[w]
        n_tot, n_st = 0, 0
        for j in np.flatnonzero(W[w] != 0):
            for g in range(m, min(m + 7, pan["close"].shape[0])):
                if not np.isfinite(pan["close"][g, j]):
                    continue
                n_tot += 1
                if (g + pan["t0"]) not in reali.get(j, set()):
                    n_st += 1
        # anche il segnale: i 7 giorni prima del lunedi'
        s_tot, s_st = 0, 0
        for j in np.flatnonzero(ps["U"][w]):
            for g in range(m - 7, m):
                if np.isfinite(pan["close"][g, j]):
                    s_tot += 1
                    if (g + pan["t0"]) not in reali.get(j, set()):
                        s_st += 1
        out[sc.data(int(ps["lunedi"][w]))] = {"tenuta_stimati": n_st, "tenuta_giorni": n_tot,
                                              "segnale_stimati": s_st, "segnale_giorni": s_tot}
    return out


# ---------------------------------------------------------------------------
# parte base
# ---------------------------------------------------------------------------

def dsr_tutti(serie_c3: pd.Series, esame_intero: dict, nuove_55: dict) -> dict:
    """Lo Sharpe corretto: come scritto nella prova (mazzo fino alla 55, senza l'aggiunta), con l'aggiunta del 23 ottobre e con
    le regole di oggi (mazzo intero di asticella, gruppi, N = gruppi e N = conto)."""
    i = esame_intero
    a = (i["sharpe"], i["settimane"], i["asimmetria"], i["curtosi"])
    r55 = ast.corretto_rivisto({**nuove_55, "55 C3": serie_c3}, {"55 C3": i})
    out = {"come_scritto_mazzo_fino_alla_55": {"gruppi": r55["gruppi"], "deviazione": round(r55["deviazione"], 3),
                                               "corretto_senza_aggiunta": round(r55["candidate"]["55 C3"]["corretto"], 4),
                                               "corretto_con_aggiunta": round(r55["candidate"]["55 C3"]["corretto_con_aggiunta"], 4),
                                               "gruppo": r55["candidate"]["55 C3"]["gruppo"]}}
    prove = ast.le_prove()
    soli = [x for _, s, x in prove if s is None]
    for taglio in (ast.TAGLIO,) + ast.ALTRI_TAGLI:
        serie = {n: ast.periodo(s) for n, s, _ in prove if s is not None}
        serie.update({n: ast.periodo(s) for n, s in ast.serie_nuove().items()})
        serie["55 C3"] = ast.periodo(serie_c3)
        gr = ast.gruppi(serie, taglio)
        sr_g, sr_v = ast.per_v(gr, soli, False), ast.per_v(gr, soli, True)
        N = len(sr_g)
        riga = {"gruppi_N": N, "in_V_con_aggiunta": len(sr_v), "deviazione_V_con_aggiunta": round(float(np.std(sr_v, ddof=1)), 3),
                "deviazione_V_tutti": round(float(np.std(sr_g, ddof=1)), 3),
                "N_gruppi_V_con_aggiunta": round(te.sharpe_corretto(*a, sr_v, 52, n_prove=N), 4),
                "N_gruppi_V_tutti": round(te.sharpe_corretto(*a, sr_g, 52), 4),
                f"N_conto_{N_CONTO}_V_con_aggiunta": round(te.sharpe_corretto(*a, sr_v, 52, n_prove=N_CONTO), 4)}
        if taglio == ast.TAGLIO:
            riga["gruppo_di_C3"] = next((g["membri"] for g in gr if "55 C3" in g["membri"]), [])
            riga["prove_nel_mazzo_con_serie"] = len(serie)
        out[f"oggi_taglio_{taglio}"] = riga
    return out


def nuove_fino_alla_55() -> dict:
    out = {f"49 {x}": pd.read_csv(P6 / "risultati_quarantanovesima" / f"settimane_{x}.csv.gz", index_col=0)["netto"] for x in ("X1", "X2")}
    for n_, f_ in (("51 F7", "risultati_cinquantunesima/settimane_F7.csv.gz"), ("52 B1", "risultati_cinquantaduesima/settimane_B1.csv.gz"),
                   ("53 F8", "risultati_cinquantatreesima/settimane_F8.csv.gz")):
        out[n_] = pd.read_csv(P6 / f_, index_col=0)["netto"]
    for f_ in sorted((P6 / "risultati_cinquantaquattresima").glob("settimane_*.csv.gz")):
        out[f"54 {f_.name[len('settimane_'):-len('.csv.gz')]}"] = pd.read_csv(f_, index_col=0).iloc[:, 0]
    return out


def regola_oggi(e: dict, dsr: float) -> dict:
    pa = e["per_anno"]
    t = e["intero"]["sharpe"] * math.sqrt(e["intero"]["settimane"] / 52)
    return {"sharpe_corretto": round(dsr, 4), "t": round(t, 3), "anni_positivi": f"{sum(v > 0 for v in pa.values())}/{len(pa)}",
            "passa_0_80": bool(dsr >= 0.80 and t >= 3 and all(v > 0 for v in pa.values()))}


def parte_base(cartella: Path) -> dict:
    pan, ps, pm, costo, Pm = base_comune(cartella)
    lun = ps["lunedi"] - pan["t0"]
    out = {"pannello": {"primo": sc.data(pan["t0"]), "ultimo": sc.data(pan["t0"] + pan["close"].shape[0] - 1),
                        "ultimo_lunedi": sc.data(int(ps["lunedi"][-1]))}}
    # 0. i componenti di questo script sono quelli della ricerca
    kk = k1(pan, ps, pm)
    k_ric = do.segnale_k1(pan, ps, pm)
    out["controllo_componenti"] = {"k1_uguale_a_dodicesima": bool(np.array_equal(np.isfinite(kk), np.isfinite(k_ric))
                                                                   and np.allclose(kk[np.isfinite(kk)], k_ric[np.isfinite(k_ric)], atol=0)),
                                   "f7_uguale_a_sesta": bool(np.array_equal(f7(pan, lun), se.funding_7(pan, lun)))}
    sig = ot.sigma_30(pan, lun)
    c_ric = cq.punteggio(-se.funding_7(pan, lun), k_ric, Pm, ps["U"])
    from research.programma6 import ventiquattresima as vq
    W_ric = vq.pesi_banda(np.where(np.isfinite(sig), c_ric, np.nan), ps["U"], sig)
    Wc, _ = pesi(pan, ps, pm, Pm, residuo=False)
    Wr, _ = pesi(pan, ps, pm, Pm, residuo=True)
    out["controllo_componenti"]["pesi_C3_uguali_al_codice_della_prova_di_oggi"] = bool(np.array_equal(W_ric, Wc["C3"]))
    Cc, Cr = conti(Wc, ps, costo), conti(Wr, ps, costo)
    m7_mio = Cc["M7"]
    m7_file = pd.read_csv(P6 / "risultati_venticinquesima" / "settimane_M7.csv.gz", index_col=0)
    cc_ = taglia(m7_mio, FINE_PROVA).index.intersection(m7_file.index)
    out["controllo_componenti"]["M7_settimane_diverse_dal_file_della_prova_25"] = int(
        (np.abs(m7_mio.loc[cc_, "netto"] - m7_file.loc[cc_, "netto"]) > 1e-9).sum())

    # 1. riproduzione del file della prova
    pub = pd.read_csv(P6 / "risultati_cinquantacinquesima" / "settimane_C3.csv.gz", index_col=0)
    a, b, c = taglia(pub, FINE_PROVA)["netto"], taglia(Cr["C3"], FINE_PROVA)["netto"], taglia(Cc["C3"], FINE_PROVA)["netto"]
    diverse = (a - b).abs() > 1e-9
    out["riproduzione"] = {"sharpe_file_della_prova_250": sharpe(a), "sharpe_rifatto_con_il_residuo_250": sharpe(b),
                           "sharpe_corretta_250": sharpe(c),
                           "settimane_diverse_file_contro_residuo": int(diverse.sum()),
                           "quali": [sc.data(int(t)) for t in a.index[diverse]][:12],
                           "differenza_massima_dove_diverse": round(float((a - b).abs().max()), 6),
                           "file_contro_residuo_fino_al_14_settembre": int(((a - b).abs() > 1e-9)[a.index <= sc.giorno(2026, 9, 14)].sum()),
                           "settimane_diverse_residuo_contro_corretta": int(((b - c).abs() > 1e-9).sum())}
    # lati cambiati dal residuo
    sett = np.flatnonzero((ps["lunedi"] >= INIZIO) & (ps["lunedi"] <= FINE_DICHIARATA))
    sr, sc_ = np.sign(Wr["C3"][sett]), np.sign(Wc["C3"][sett])
    f_c = f7(pan, lun)
    pari = []
    for w in sett:
        x = f_c[w, ps["U"][w]]
        x = x[np.isfinite(x)]
        pari.append(1 - len(np.unique(x)) / max(len(x), 1))
    out["residuo"] = {"posizioni_moneta_settimana_C3": int((sc_ != 0).sum()),
                      "posizioni_cambiate_di_lato_o_entrate_uscite": int((sr != sc_).sum()),
                      "F5_posizioni_cambiate": int((np.sign(Wr["F5"][sett]) != np.sign(Wc["F5"][sett])).sum()),
                      "F5_posizioni": int((np.sign(Wc["F5"][sett]) != 0).sum()),
                      "quota_media_di_monete_in_parita_sul_funding_7": round(float(np.mean(pari)), 4)}

    # 2. periodi: dichiarato, della prova, fino all'ultimo lunedi' con il funding tutto vero
    sv = settimane_vere(pan, ps, Wc["C3"])
    out["funding_stimato_per_lunedi_dal_settembre_2026"] = sv
    vere = [d for d, v in sv.items() if v["tenuta_stimati"] == 0 and v["tenuta_giorni"] > 0]
    ultimo_vero = max(sc.giorno(*map(int, d.split("-"))) for d in vere) if vere else FINE_DICHIARATA
    periodi = {"dichiarato_al_2026-10-05": FINE_DICHIARATA, "della_prova_al_2026-10-12": FINE_PROVA,
               f"funding_vero_al_{sc.data(ultimo_vero)}": ultimo_vero}
    btc = pd.Series(ps["R"][:, ps["simboli"].index("BTCUSDT")], index=ps["lunedi"])
    nuove55 = nuove_fino_alla_55()
    res = {}
    for nome_p, fine in periodi.items():
        r = {}
        for etich, C in (("residuo", Cr), ("corretta", Cc)):
            e = te.esame(taglia(C["C3"], fine, inizio=-10**9), btc, inizio=INIZIO, anni_pieni=q.ANNI_PIENI)
            riga = {"sharpe": round(e["intero"]["sharpe"], 3), "annuo": round(e["intero"]["annuo"], 4),
                    "discesa": round(e["intero"]["discesa_max"], 4), "settimane": e["intero"]["settimane"],
                    "per_anno": {a_: round(v, 4) for a_, v in e["per_anno"].items()}, "boot_basso": round(e["boot"]["basso"], 5),
                    "costi_doppi": round(e["costi_doppi"], 5), "ultimo_anno": round(e["ultimo_anno"], 4),
                    "extra_btc": round(e["extra_btc_annuo"], 4), "giro": round(e["giro_medio"], 3), "spese": round(e["spese_annue"], 4),
                    "trimestri_positivi": {a_: sum(1 for qq in range(1, 5) if e["per_trimestre"][f"{a_}T{qq}"] > 0) for a_ in q.ANNI_PIENI}}
            if etich == "corretta" or nome_p.startswith("della_prova"):
                d = dsr_tutti(C["C3"]["netto"], e["intero"], nuove55)
                riga["sharpe_corretto"] = d
                riga["esito_come_scritto_0_95_senza_aggiunta"] = te.esito(e, d["come_scritto_mazzo_fino_alla_55"]["corretto_senza_aggiunta"])
                riga["esito_come_scritto_0_95_con_aggiunta"] = te.esito(e, d["come_scritto_mazzo_fino_alla_55"]["corretto_con_aggiunta"])
                riga["regola_di_oggi_gruppi"] = regola_oggi(e, d[f"oggi_taglio_{ast.TAGLIO}"]["N_gruppi_V_con_aggiunta"])
                riga["regola_di_oggi_N_conto"] = regola_oggi(e, d[f"oggi_taglio_{ast.TAGLIO}"][f"N_conto_{N_CONTO}_V_con_aggiunta"])
                riga["regola_di_oggi_gruppi_senza_aggiunta"] = regola_oggi(e, d[f"oggi_taglio_{ast.TAGLIO}"]["N_gruppi_V_tutti"])
            r[etich] = riga
        # confronti sulle stesse settimane
        for etich, C in (("residuo", Cr), ("corretta", Cc)):
            for n in ("F5", "K2", "M7", "F5+M7+K2"):
                x = taglia(C[n], fine)["netto"]
                r[etich][f"{n}_stesse_settimane"] = {"sharpe": sharpe(x), "annuo": round(float(x.mean() * 52), 4),
                                                     "discesa": round(te.numeri_settimana(x)["discesa_max"], 4), **anni(x)}
            x5, x3 = taglia(C["F5"], fine)["netto"], taglia(C["C3"], fine)["netto"]
            r[etich]["correlazione_C3_F5"] = round(float(np.corrcoef(x3, x5)[0, 1]), 3)
            r[etich]["C3_meno_F5_sharpe"] = round(sharpe(x3) - sharpe(x5), 3)
            r[etich]["bootstrap_differenza_sharpe_C3_meno_F5"] = boot_diff(x3, x5)
        res[nome_p] = r
    out["periodi"] = res
    # F5 dal 2021 (come la prova 24 e il controllo delle parita'), per il confronto usato nel verdetto
    e21 = {}
    for etich, C in (("residuo", Cr), ("corretta", Cc)):
        for fine in (FINE_DICHIARATA, FINE_PROVA):
            x = taglia(C["F5"], fine, inizio=sc.giorno(2021, 1, 4))["netto"]
            e21[f"{etich}_al_{sc.data(fine)}"] = {"sharpe": sharpe(x), "settimane": len(x)}
    f5_file = pd.read_csv(P6 / "risultati_ventiquattresima" / "settimane_F5.csv.gz", index_col=0)
    e21["file_prova_24_dal_2021_al_2026-10-12"] = sharpe(taglia(f5_file, FINE_PROVA, inizio=sc.giorno(2021, 1, 4))["netto"])
    e21["file_prova_24_dal_2022_al_2026-10-12"] = sharpe(taglia(f5_file, FINE_PROVA)["netto"])
    e21["file_prova_24_dal_2022_al_2026-10-05"] = sharpe(taglia(f5_file, FINE_DICHIARATA)["netto"])
    tre_file = pd.read_csv(P6 / "risultati_ventottesima" / "settimane_F5_M7_K2.csv.gz", index_col=0)
    e21["file_prova_28_F5+M7+K2_dal_2022_al_2026-10-12"] = sharpe(taglia(tre_file, FINE_PROVA)["netto"])
    out["F5_come_nel_verdetto"] = e21

    # 3. misure di C3 corretta sul periodo dichiarato
    d = taglia(Cc["C3"], FINE_DICHIARATA)
    out["misure_C3_corretta_dichiarato"] = a28.misure(d["netto"], d["spese"])
    out["misure_C3_corretta_dichiarato"]["monete_per_lato_media"] = {
        "long": round(float((Wc["C3"][sett] > 0).sum(axis=1).mean()), 1), "short": round(float((Wc["C3"][sett] < 0).sum(axis=1).mean()), 1)}
    out["misure_C3_corretta_dichiarato"]["settimane_senza_posizioni"] = int((d["monete"] == 0).sum())
    out["misure_C3_corretta_dichiarato"]["long_annuo"] = round(float(d["long"].mean() * 52), 4)
    out["misure_C3_corretta_dichiarato"]["short_annuo"] = round(float(d["short"].mean() * 52), 4)
    out["misure_C3_corretta_dichiarato"]["funding_annuo_pagato"] = round(float(d["funding"].mean() * 52), 4)
    out["climi_C3_corretta"] = a28.climi(d["netto"], pan, ps)
    out["climi_F5_corretta"] = a28.climi(taglia(Cc["F5"], FINE_DICHIARATA)["netto"], pan, ps)
    esito_file("base").write_text(json.dumps(out, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    return out


def boot_diff(x: pd.Series, y: pd.Series, blocco=4, n=2000, seme=2026) -> dict:
    """Bootstrap a blocchi (settimane appaiate) della differenza di Sharpe x - y."""
    a, b = x.to_numpy(float), y.to_numpy(float)
    T = len(a)
    rng = np.random.default_rng(seme)
    nb = int(math.ceil(T / blocco))
    d = []
    for _ in range(n):
        idx = (rng.integers(0, T - blocco + 1, nb)[:, None] + np.arange(blocco)[None, :]).ravel()[:T]
        sa, sb = a[idx], b[idx]
        d.append(sa.mean() / sa.std(ddof=1) * math.sqrt(52) - sb.mean() / sb.std(ddof=1) * math.sqrt(52))
    d = np.array(d)
    return {"media": round(float(d.mean()), 3), "basso_2_5": round(float(np.quantile(d, 0.025)), 3),
            "alto_97_5": round(float(np.quantile(d, 0.975)), 3), "quota_sotto_zero": round(float((d < 0).mean()), 3)}


# ---------------------------------------------------------------------------
# parte m7r: il residuo dentro gli ingredienti di M7
# ---------------------------------------------------------------------------

def parte_m7r(cartella: Path) -> dict:
    pan = sc.pannello()
    ps = te.pannello_settimane(pan, log=lambda x: None)
    assert (np.load(cartella / "lunedi.npy") == ps["lunedi"]).all()
    originale = q.ingredienti_giornalieri

    def arrotondati(pan_):
        g = originale(pan_)
        for k in list(g):
            if k.startswith("funding_"):
                g[k] = np.round(g[k], 12)
        return g

    q.ingredienti_giornalieri = arrotondati
    try:
        X, _, Y = q.tabella_settimanale(pan, ps, ps["U"])
    finally:
        q.ingredienti_giornalieri = originale
    Ps = [vt.previsioni_seme(s, X, Y, ps["U"], ps["lunedi"]) for s in vt.SEMI]
    with np.errstate(all="ignore"):
        Pm = np.where(ps["U"], vt.media_ranghi(Ps, ps["U"]), np.nan)
    np.save(cartella / "Pm_r.npy", Pm)
    P0 = np.load(cartella / "Pm.npy")
    ok = np.isfinite(P0) & np.isfinite(Pm)
    out = {"previsioni_diverse": int((np.abs(P0[ok] - Pm[ok]) > 1e-12).sum()), "previsioni": int(ok.sum()),
           "differenza_massima_del_rango": float(np.abs(P0[ok] - Pm[ok]).max())}
    pm = un.pannello_metrics(pan)
    costo = sc.costi_moneta(ps["simboli"])
    W, _ = pesi(pan, ps, pm, Pm)
    C = conti(W, ps, costo)
    W0, _ = pesi(pan, ps, pm, P0)
    C0 = conti(W0, ps, costo)
    for fine in (FINE_DICHIARATA, FINE_PROVA):
        out[f"al_{sc.data(fine)}"] = {n: {"con_M7_arrotondato": sharpe(taglia(C[n], fine)["netto"]),
                                          "con_M7_come_la_prova": sharpe(taglia(C0[n], fine)["netto"])}
                                      for n in ("C3", "M7", "F5+M7+K2", "F5")}
    esito_file("m7r").write_text(json.dumps(out, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    return out


# ---------------------------------------------------------------------------
# parte sensibilita'
# ---------------------------------------------------------------------------

def parte_sensibilita(cartella: Path) -> dict:
    pan, ps, pm, costo, Pm = base_comune(cartella)
    sens = {}

    def una(etichetta, ps_=None, Pm_=None, **kw):
        ps_ = ps if ps_ is None else ps_
        W, _ = pesi(pan, ps_, pm, Pm if Pm_ is None else Pm_, **kw)
        C = {n: a28.conto(W[n], ps_, costo) for n in ("C3", "F5")}
        x3, x5 = taglia(C["C3"], FINE_DICHIARATA)["netto"], taglia(C["F5"], FINE_DICHIARATA)["netto"]
        sens[etichetta] = {"C3": sharpe(x3), "F5_stesso_cambio": sharpe(x5), "C3_meno_F5": round(sharpe(x3) - sharpe(x5), 3),
                           "anni_C3": anni(x3)["positivi"], "annuo_C3": round(float(x3.mean() * 52), 4),
                           "discesa_C3": round(te.numeri_settimana(x3)["discesa_max"], 4)}

    una("base")
    for e in (0.16, 0.18, 0.22, 0.24):
        una(f"entrata {e}", entra=e)
    for r in (0.32, 0.36, 0.44, 0.48):
        una(f"uscita {r}", resta=r)
    for g in (24, 27, 33, 36):
        una(f"volatilita' {g} giorni", giorni_sig=g)
    for k in (6, 8):
        una(f"segnali {k} giorni (funding e K1; M7 resta)", k=k)
    una("tutti e tre i ranghi presenti", minimo=3)
    for n_u in (80, 90, 110, 120):
        ps2 = te.pannello_settimane(pan, log=lambda x: None, a=n_u, indicatori_si=False)
        # M7 resta quello delle 100: sulle monete nuove manca (bastano 2 ranghi su 3)
        una(f"universo {n_u} (M7 resta a 100)", ps_=ps2)
    out = {"sensibilita_periodo_dichiarato": sens}
    v = [x["C3"] for k_, x in sens.items() if k_ != "base"]
    d = [x["C3_meno_F5"] for k_, x in sens.items() if k_ != "base"]
    out["riassunto"] = {"C3_min": min(v), "C3_max": max(v), "C3_meno_F5_min": min(d), "C3_meno_F5_max": max(d),
                        "casi_C3_sopra_F5": sum(1 for x in d if x > 0), "casi": len(d)}
    esito_file("sensibilita").write_text(json.dumps(out, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    return out


# ---------------------------------------------------------------------------
# parte tempi
# ---------------------------------------------------------------------------

def parte_tempi(cartella: Path) -> dict:
    pan, ps, pm, costo, Pm = base_comune(cartella)
    W, _ = pesi(pan, ps, pm, Pm)
    out = {}
    # 1. taglio: i pesi di C3 di un lunedi' con i soli dati fino alla domenica (piu' l'apertura del lunedi'); M7 dal calcolo
    #    intero (le sue previsioni sono controllate a parte qui sotto con il seme 1)
    tg = {}
    for dd in ((2022, 3, 7), (2022, 11, 14), (2023, 6, 5), (2024, 8, 5), (2025, 4, 7), (2026, 10, 5)):
        g = sc.giorno(*dd)
        m = g - pan["t0"]
        p2, pm2 = a28.tagliato(pan, pm, m)
        ps2 = te.pannello_settimane(p2, log=lambda x: None, indicatori_si=False)
        n2 = len(ps2["lunedi"])
        assert (ps2["lunedi"] == ps["lunedi"][:n2]).all()
        W2, _ = pesi(p2, ps2, pm2, Pm[:n2])
        w = n2 - 1
        assert ps2["lunedi"][w] == g
        tg[sc.data(g)] = {n: float(np.abs(W2[n][w] - W[n][w]).max()) for n in ("C3", "F5", "K2")}
    out["taglio_differenza_massima_dei_pesi"] = tg
    a28t = importlib.import_module("prova28_tempi_2026-11-11")
    out["taglio_M7_seme_1"] = a28t.taglio_m7(pan, pm, cartella, [(2025, 4, 7)])
    # 2. entrata un giorno dopo (martedi' apertura -> martedi' dopo), stessi pesi
    lun = ps["lunedi"] - pan["t0"]
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
    for n in ("C3", "F5"):
        x = te.conto(W[n], R1, F1, costo)
        x.index = ps["lunedi"]
        rit[n] = sharpe(taglia(x, FINE_DICHIARATA)["netto"])
    out["entrata_un_giorno_dopo"] = rit
    out["base_00"] = {n: sharpe(taglia(a28.conto(W[n], ps, costo), FINE_DICHIARATA)["netto"]) for n in ("C3", "F5")}
    # 3. entrata all'01:00 e alle 04:00 (candele orarie), uscita alla stessa ora del lunedi' dopo
    usate = np.flatnonzero(np.abs(W["C3"]).sum(axis=0) + np.abs(W["F5"]).sum(axis=0) > 0)
    ore = (1, 4)
    R = {h: ps["R"].copy() for h in ore}
    coperte, tot = 0, 0
    for j in usate:
        try:
            o = es.ore_di(ps["simboli"][j])
        except Exception:
            o = pd.DataFrame()
        if o.empty:
            continue
        op = o["open"]
        for w in range(len(lun)):
            if W["C3"][w, j] == 0 and W["F5"][w, j] == 0:
                continue
            tot += 1
            ora0 = int(ps["lunedi"][w]) * 24
            fatto = True
            for h in ore:
                a_, b_ = op.get(ora0 + h), op.get(ora0 + 7 * 24 + h)
                if a_ is None or b_ is None or not np.isfinite(a_) or not np.isfinite(b_):
                    fatto = False
                    continue
                R[h][w, j] = b_ / a_ - 1
            coperte += int(fatto)
    eo = {"posizioni_con_le_ore": round(coperte / max(tot, 1), 3)}
    for h in ore:
        eo[f"ore_{h:02d}"] = {}
        for n in ("C3", "F5"):
            x = te.conto(W[n], R[h], ps["F"], costo)
            x.index = ps["lunedi"]
            eo[f"ore_{h:02d}"][n] = sharpe(taglia(x, FINE_DICHIARATA)["netto"])
    out["entrata_oraria"] = eo
    esito_file("tempi").write_text(json.dumps(out, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    return out


# ---------------------------------------------------------------------------
# parte dati
# ---------------------------------------------------------------------------

def parte_dati(cartella: Path) -> dict:
    pan, ps, pm, costo, Pm = base_comune(cartella)
    t0 = pan["t0"]
    T, S = pan["close"].shape
    W, _ = pesi(pan, ps, pm, Pm)
    Wc = W["C3"]
    lun = ps["lunedi"] - t0
    DAL = sc.giorno(2021, 12, 1)
    sett = np.flatnonzero((ps["lunedi"] >= INIZIO) & (ps["lunedi"] <= FINE_DICHIARATA))
    in_u = ps["U"][sett].any(axis=0)
    tenute = (Wc[sett] != 0).any(axis=0)
    out = {"settimane": int(len(sett)), "monete_universo": int(in_u.sum()), "monete_tenute_C3": int(tenute.sum())}
    C, O, H, L, V = (pan[k] for k in ("close", "open", "high", "low", "quote_volume"))
    fine_g = FINE_DICHIARATA - t0 + 7
    buchi = {}
    for j in np.flatnonzero(in_u):
        ok = np.isfinite(C[:, j])
        a, b = np.flatnonzero(ok)[[0, -1]]
        dentro = np.arange(max(a, DAL - t0), min(b, fine_g) + 1)
        mancano = dentro[~ok[dentro]]
        if len(mancano):
            buchi[ps["simboli"][j]] = [sc.data(int(g) + t0) for g in mancano]
    cont = Counter(d for v in buchi.values() for d in v)
    out["buchi_nell_universo"] = {"monete": len(buchi), "giorni_piu_frequenti": dict(cont.most_common(8))}
    giorno_t = np.zeros((T, S), bool)
    for w in sett:
        giorno_t[lun[w]: lun[w] + 7] |= Wc[w] != 0
    with np.errstate(all="ignore"):
        r = np.vstack([np.full((1, S), np.nan), C[1:] / C[:-1] - 1])
        fuori = ((O > H * (1 + 1e-9)) | (O < L * (1 - 1e-9)) | (C > H * (1 + 1e-9)) | (C < L * (1 - 1e-9)) | (H < L)) & giorno_t
        nonpos = ((O <= 0) | (C <= 0) | (L <= 0)) & giorno_t
        salti = (np.abs(r) > 0.5) & giorno_t
    el = sorted(((float(r[t, j]), ps["simboli"][j], sc.data(t + t0)) for t, j in zip(*np.nonzero(salti))), key=lambda x: -abs(x[0]))
    out["anomalie_nei_giorni_tenuti"] = {"candele_incoerenti": int(fuori.sum()), "prezzi_non_positivi": int(nonpos.sum()),
                                         "giorni_oltre_50%": len(el), "i_piu_grandi": [[round(a, 3), b, c] for a, b, c in el[:8]]}
    fermi = np.isfinite(C) & (np.nan_to_num(V) == 0)
    out["giorni_fermi_tenuti"] = int((fermi & giorno_t).sum())
    stimati, zero_in_mese, ore_reg, minuti_fuori, interv = Counter(), Counter(), Counter(), 0, Counter()
    non_mezz, dup, ordine = {}, {}, {}
    for j in np.flatnonzero(tenute):
        s = ps["simboli"][j]
        righe = []
        for p in sorted((sc.DATI / s / "funding").glob("*.zip")):
            righe += funding_da_zip(p)
        df = pd.DataFrame(righe, columns=["ts", "ore", "tasso"]).drop_duplicates("ts")
        df = df[df["ts"] >= DAL * 86_400_000]
        sec = (df["ts"] // 1000) % 3600
        minuti_fuori += int(((sec > 60) & (sec < 3540)).sum())
        ore_reg.update(((df["ts"] // 3_600_000) % 24).tolist())
        interv.update(df["ore"].tolist())
        reali = set(((df["ts"].to_numpy() // 60_000 - 1) // 1440).tolist())
        for g in np.flatnonzero(giorno_t[:, j]) + t0:
            if g not in reali and np.isfinite(C[g - t0, j]):
                (stimati if pan["funding"][g - t0, j] != 0 else zero_in_mese)[sc.data(int(g))[:7]] += 1
        file = sorted((sc.DATI / s / "giorni").glob("*.zip"))
        api = [pd.read_csv(p) for p in sorted((sc.DATI / s / "giorni_api").glob("*.csv"))]
        grezzo = pd.concat(api + [m5._csv_da_zip(p, m5.KLINE) for p in file], ignore_index=True)
        ms = m5._ms(grezzo["open_time"])
        nm = int((ms % 86_400_000 != 0).sum())
        if nm:
            non_mezz[s] = nm
        dd = grezzo.assign(ms=ms).loc[ms >= DAL * 86_400_000]
        dd_ = dd[dd.duplicated("ms", keep=False)]
        if len(dd_):
            diversi = dd_.groupby("ms")[["open", "high", "low", "close"]].nunique().max(axis=1)
            if (diversi > 1).any():
                dup[s] = int((diversi > 1).sum())
        for p in file:
            x = m5._ms(m5._csv_da_zip(p, m5.KLINE)["open_time"])
            if not x.is_monotonic_increasing:
                ordine[s] = ordine.get(s, 0) + 1
    out["funding"] = {"giorni_tenuti_stimati_per_mese": dict(sorted(stimati.items())),
                      "giorni_tenuti_a_zero_senza_dato_per_mese": dict(sorted(zero_in_mese.items())),
                      "regolamenti_oltre_il_minuto": minuti_fuori, "ore_dei_regolamenti": dict(sorted(ore_reg.items())),
                      "intervalli_ore": dict(sorted(interv.items()))}
    out["candele_grezze"] = {"orari_non_a_mezzanotte": non_mezz, "duplicati_diversi": dup, "file_fuori_ordine": ordine}
    p2 = un.p2(pm, lun)
    u = ps["U"][sett]
    out["interesse_aperto_mancante_nell_universo"] = round(float((~np.isfinite(p2[sett]) & u).sum() / u.sum()), 4)
    Pmu = np.isfinite(Pm[sett]) & u
    out["M7_mancante_nell_universo"] = round(float(1 - Pmu.sum() / u.sum()), 4)
    a28b = importlib.import_module("prova28_buchi_2026-11-11")
    out["perso_nei_buchi_del_2022"] = a28b.perso_nei_buchi(pan, ps, Wc)
    esito_file("dati").write_text(json.dumps(out, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    return out


# ---------------------------------------------------------------------------
# parte rischio
# ---------------------------------------------------------------------------

def parte_rischio(cartella: Path) -> dict:
    pan, ps, pm, costo, Pm = base_comune(cartella)
    W, _ = pesi(pan, ps, pm, Pm)
    Wc = W["C3"]
    sett = np.flatnonzero((ps["lunedi"] >= INIZIO) & (ps["lunedi"] <= FINE_DICHIARATA))
    out = {"perdita_peggiore_C3": a28.perdita_peggiore(pan, ps, Wc, sett),
           "perdita_peggiore_F5": a28.perdita_peggiore(pan, ps, W["F5"], sett)}
    pmax = np.abs(Wc[sett]).max(axis=1)
    out["peso_massimo_di_una_moneta"] = {"massimo": round(float(pmax.max()), 4), "mediana_settimanale": round(float(np.median(pmax)), 4),
                                         "settimane_sopra_10%": int((pmax > 0.10).sum()), "settimane_sopra_20%": int((pmax > 0.20).sum())}
    j, w = np.unravel_index(np.argmax(np.abs(Wc[sett])), Wc[sett].shape)
    out["peso_massimo_di_una_moneta"]["dove"] = [ps["simboli"][w], sc.data(int(ps["lunedi"][sett][j]))]
    out["filtri"] = [a28.filtri(pan, ps, Wc, sett, c) for c in (280, 1000, 10000)]
    a28c = importlib.import_module("prova28_conto_vero_2026-11-11")
    fl = json.loads((RADICE / "bot" / "portafoglio" / "filtri_conto_vero.json").read_text())["filtri"]
    vecchio = a28.FINE_FUNDING_VERO
    a28.FINE_FUNDING_VERO = FINE_DICHIARATA
    try:
        cv = {}
        for cap in (280, 1000):
            for comp in (True, False):
                s = a28c.simula(pan, ps, Wc, cap, costo, fl, composto=comp)
                cv[f"{cap}_{'composto' if comp else 'fisso'}"] = {"sharpe": sharpe(s), "ordini_saltati": round(s.attrs["saltati"], 3),
                                                                  **anni(s)}
        out["conto_vero_C3"] = cv
    finally:
        a28.FINE_FUNDING_VERO = vecchio
    esito_file("rischio").write_text(json.dumps(out, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    return out


# ---------------------------------------------------------------------------
# parti piccole: Sharpe corretto con M7 arrotondato (dopo ``m7r``) e posizioni tenute nei giorni fermi
# ---------------------------------------------------------------------------

def parte_m7r_dsr(cartella: Path) -> dict:
    pan, ps, pm, costo, Pm = base_comune(cartella)
    W, _ = pesi(pan, ps, pm, np.load(cartella / "Pm_r.npy"))
    c3 = a28.conto(W["C3"], ps, costo)
    btc = pd.Series(ps["R"][:, ps["simboli"].index("BTCUSDT")], index=ps["lunedi"])
    out = {}
    for fine in (FINE_DICHIARATA, FINE_PROVA):
        e = te.esame(taglia(c3, fine, inizio=-10**9), btc, inizio=INIZIO, anni_pieni=q.ANNI_PIENI)
        d = dsr_tutti(c3["netto"], e["intero"], nuove_fino_alla_55())
        out[sc.data(fine)] = {"sharpe": round(e["intero"]["sharpe"], 3), "per_anno": {k: round(v, 3) for k, v in e["per_anno"].items()},
                              "come_scritto": d["come_scritto_mazzo_fino_alla_55"]["corretto_senza_aggiunta"],
                              "con_aggiunta_mazzo_55": d["come_scritto_mazzo_fino_alla_55"]["corretto_con_aggiunta"],
                              "oggi_gruppi": d[f"oggi_taglio_{ast.TAGLIO}"]["N_gruppi_V_con_aggiunta"],
                              "oggi_N312": d[f"oggi_taglio_{ast.TAGLIO}"][f"N_conto_{N_CONTO}_V_con_aggiunta"],
                              "t": round(e["intero"]["sharpe"] * (e["intero"]["settimane"] / 52) ** 0.5, 3)}
    esito_file("m7r_dsr").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    return out


def parte_zombi(cartella: Path) -> dict:
    pan, ps, pm, costo, Pm = base_comune(cartella)
    W, _ = pesi(pan, ps, pm, Pm)
    Wc = W["C3"]
    lun = ps["lunedi"] - pan["t0"]
    C, V = pan["close"], pan["quote_volume"]
    sett = np.flatnonzero((ps["lunedi"] >= INIZIO) & (ps["lunedi"] <= FINE_DICHIARATA))
    righe = []
    for w in sett:
        m = lun[w]
        for j in np.flatnonzero(Wc[w] != 0):
            g = [d for d in range(m, m + 7) if np.isfinite(C[d, j]) and np.nan_to_num(V[d, j]) == 0]
            if g:
                righe.append([ps["simboli"][j], sc.data(int(ps["lunedi"][w])), len(g), round(float(Wc[w, j]), 4),
                              round(float(ps["R"][w, j]), 4), round(float(Wc[w, j] * ps["R"][w, j]), 5)])
    out = {"posizioni": len(righe), "giorni": sum(r[2] for r in righe), "contributo_totale": round(sum(r[5] for r in righe), 4),
           "righe_simbolo_lunedi_giorni_peso_R_contributo": sorted(righe, key=lambda r: -abs(r[5]))}
    esito_file("zombi").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    return out


def parte_senza(cartella: Path) -> dict:
    """Solo per capire quanto pesa K1 (costruzione sul 2022-2026, DODICESIMA.md, sezione 1): C3 con il funding e M7 soli, e con il
    funding e K1 soli (il punteggio con i due ranghi presenti; stessa banda, stessi pesi)."""
    pan, ps, pm, costo, Pm = base_comune(cartella)
    lun = ps["lunedi"] - pan["t0"]
    sig = ot.sigma_30(pan, lun)
    f = -f7(pan, lun)
    kk = k1(pan, ps, pm)
    nan = np.full_like(f, np.nan)
    out = {}
    for nome, (kx, mx) in {"funding_e_M7": (nan, Pm), "funding_e_K1": (kk, nan), "tutti_e_tre": (kk, Pm)}.items():
        c = cq.punteggio(f, kx, mx, ps["U"])
        W = a28.banda(np.where(np.isfinite(sig), c, np.nan), ps["U"], sig)
        x = taglia(a28.conto(W, ps, costo), FINE_DICHIARATA)["netto"]
        out[nome] = {"sharpe": sharpe(x), **anni(x)}
    esito_file("senza").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    return out


if __name__ == "__main__":
    parte, cart = sys.argv[1], Path(sys.argv[2])
    funz = {"base": parte_base, "m7r": parte_m7r, "sensibilita": parte_sensibilita, "tempi": parte_tempi,
            "dati": parte_dati, "rischio": parte_rischio, "m7r_dsr": parte_m7r_dsr, "zombi": parte_zombi,
            "senza": parte_senza}[parte]
    o = funz(cart)
    testo = json.dumps(o, ensure_ascii=False, default=str)
    print(testo[:3000])
