"""Programma 7, prova 152 (file `novantesima.py`): il limite alla concentrazione di G1 (`NOVANTESIMA.md`, regole del commit b9e473a).

Tre varianti (V1 tetto 20%, V2 almeno 10 monete nei giorni rari, V3 minimo 10 con esposizione ridotta e tetto) accanto a G1 com'e'.
Conto 1: periodo di G1, spese confermate, senza minimi (`analisi.conto`). Conto 2: 280 USDT con i minimi di Binance (motore della
prova 148, `ottantaseiesima.conto_vero`), conti A e A2.

Uso: CACHE_G1N=<cartella> python3 -m research.programma7.novantesima [--controllo65]
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import rankdata

from research.programma6 import seconda as sc
from research.programma6 import terza as te
from research.programma7 import ottantaseiesima as o86
from research.programma7.revisione_g1n import analisi as an
from research.programma7.revisione_g1n import nucleo as nu
from research.src import prove

QUI = Path(__file__).parent
OUT = QUI / "risultati_novantesima"
ID = "novantesima"
CAP = 280.0
SOGLIA_PESO, SOGLIA_SHARPE, SOGLIA_DISCESA, SOGLIA_T = 0.20, 0.15, 0.03, 3.0


def log(*a):
    print(time.strftime("%H:%M:%S"), *a, flush=True)


def _lato(w, segno):
    return np.where(np.sign(w) == segno, w, 0.0)


def _tetto(v):
    return nu.tetto_lato(v, SOGLIA_PESO)


def pesi_variante(pan, idx, U, variante, ammessi=None, diario=None):
    """I pesi giorno per giorno (lati fissi a 1 e 1). ``variante`` in G1, V1, V2, V3. ``ammessi``: maschera delle monete che V2 puo'
    aggiungere (conto a 280 USDT: solo con i filtri di Binance). ``diario``: lista dove si scrivono i giorni rari."""
    rc = nu.ritorni_chiusura(pan["close"])
    F, V = pan["funding"], pan["quote_volume"]
    simboli = np.array(pan["simboli"])
    S = rc.shape[1]
    W = np.zeros((len(idx), S))
    lunghi, corti = set(), set()
    for k, i in enumerate(idx):
        sig = nu.sigma30(rc, i)
        ct = np.where(np.isfinite(sig), -nu.funding7(F, i), np.nan)
        w, lunghi, corti = nu.passo_banda(ct, U[k], sig, lunghi, corti)       # gli insiemi che portano la banda non cambiano mai
        if variante == "G1":
            W[k] = w
            continue
        out = np.zeros(S)
        valide = np.flatnonzero(U[k] & np.isfinite(ct) & np.isfinite(sig) & (sig > 0))
        if variante == "V2":
            vol = np.nanmean(V[i - 30:i], axis=0) if i >= 30 else np.full(S, np.nan)
        for segno in (1.0, -1.0):
            v = _lato(w, segno)
            n = int((v != 0).sum())
            if variante == "V1":
                if n >= 5:
                    v = _tetto(v)
            elif variante == "V3":
                if n < 10:
                    if n > 0:
                        v = v * (n / 10)
                    if diario is not None:
                        diario.append((int(i + pan["t0"]), segno, n))
                if n >= 5:
                    v = _tetto(v)
            elif variante == "V2" and n < 10:
                esito = "ok"
                if len(valide) < nu.MIN_MONETE:
                    esito = "universo_sotto_20"
                else:
                    scelte = set(np.flatnonzero(w != 0).tolist())
                    altro = set(np.flatnonzero(_lato(w, -segno) != 0).tolist())
                    cand = [j for j in valide if j not in scelte and j not in altro]
                    if ammessi is not None:
                        cand = [j for j in cand if ammessi[j]]
                    # ordine: segnale (lunghi: ct piu' alto prima; corti: ct piu' basso prima), a pari merito volume piu' alto, poi simbolo
                    cand.sort(key=lambda j: (-segno * ct[j], -(vol[j] if np.isfinite(vol[j]) else -1.0), str(simboli[j])))
                    serve = 10 - n
                    if len(cand) < serve:
                        esito = "rango_insufficiente"
                    else:
                        lato = sorted(scelte & set(np.flatnonzero(_lato(w, segno) != 0).tolist())) + cand[:serve]
                        inv = 1.0 / sig[lato]
                        v = np.zeros(S)
                        v[lato] = segno * inv / inv.sum()
                if diario is not None:
                    diario.append((int(i + pan["t0"]), segno, n, esito))
            out += v
        W[k] = out
    return W


def deriva_massima(W, R, F):
    """Peso massimo (assoluto) per lato prima del ribilanciamento, con i pesi che derivano col prezzo (come `nucleo.variazioni`)."""
    T, S = W.shape
    deriva = np.zeros(S)
    mv, mc = np.zeros(T), np.zeros(T)
    for k in range(T):
        mv[k] = max(0.0, float((-deriva).max()))
        mc[k] = max(0.0, float(deriva.max()))
        x = W[k]
        netto = float(x @ R[k]) - float(x @ F[k])
        deriva = x * (1 + R[k]) / (1 + netto) if 1 + netto > 0 else np.zeros(S)     # senza spese: misura a parte
    return mv, mc


def giorni_moneta_oltre_3(W, EXC):
    """Misura della revisione di G1 (`g1_parte2_2026-11-12.py`, `giorni_moneta_oltre_3pc_di_perdita`): peso voluto * escursione peggiore
    della giornata (comprate: minimo/apertura-1; vendute: massimo/apertura-1), perdite oltre il 3% del capitale. Si riporta, non decide."""
    su, giu = EXC
    return int(((W * np.where(W > 0, giu, su)) < -0.03).sum())


def sortino(x):
    x = np.asarray(x, float)
    dd = np.sqrt(np.mean(np.minimum(x, 0) ** 2))
    return float(x.mean() / dd * np.sqrt(52)) if dd > 0 else 0.0


def serie_conto(d):
    s = an.settimane(d)["netto"]
    return s


def misure_conto(d, W, R, F, giorni):
    s = an.sintesi(d)
    w = an.settimane(d)
    nu_ = nu.numeri(w["netto"].to_numpy())
    s["t"] = float(nu_["sharpe"] * np.sqrt(nu_["n"] / 52))
    s["sortino"] = sortino(w["netto"].to_numpy())
    s["spese_annue"] = float(d["spese"].sum() / len(d) * 365)
    s["giro_giornaliero"] = float(np.abs(np.diff(W, axis=0)).sum(axis=1).mean())
    return s


def main():
    t0 = time.time()
    solo65 = "--controllo65" in sys.argv
    pan = sc.pannello()
    simboli = pan["simboli"]
    giorni = np.arange(an.INIZIO, an.FINE, dtype=np.int64)
    idx = giorni - pan["t0"]
    R = nu.ritorni_tenuta(pan["open"], pan["close"])[idx]
    F = np.nan_to_num(pan["funding"][idx])
    O = pan["open"][idx]
    costo = np.array([nu.costo_di(s) for s in simboli])
    U = nu.universo_giorni(pan, idx)
    OUT.mkdir(parents=True, exist_ok=True)
    log("universo pronto")

    # G1 con il codice della prova 148 (nucleo.pesi con i lati fissi a 1 e 1) e controllo che il mio G1 sia identico
    W_nucleo, _, _ = nu.pesi(pan, idx, U, fisso=(1.0, 1.0))
    Wg = pesi_variante(pan, idx, U, "G1")
    assert np.array_equal(W_nucleo, Wg), "G1 del mio ciclo diverso da nucleo.pesi"
    with np.errstate(all="ignore"):
        EXC = (np.nan_to_num(pan["high"][idx] / O - 1), np.nan_to_num(pan["low"][idx] / O - 1))
    n65 = giorni_moneta_oltre_3(Wg, EXC)
    log("giorni-moneta oltre il 3% (G1):", n65, "(atteso 65)")
    if solo65 or n65 != 65:
        (OUT / "controllo65.json").write_text(json.dumps({"giorni_moneta_oltre_3_G1": n65, "atteso": 65}), encoding="utf-8")
        if n65 != 65:
            log("NON TORNA: ci si ferma come scritto nelle regole")
        return

    filtri = json.loads(o86.FILTRI.read_text(encoding="utf-8"))["vero"]
    ammessi = np.array([s in filtri for s in simboli])
    vmin, passo, qmin = o86.carica_filtri(simboli)

    diari = {}
    Wc1, Wc2 = {"G1": Wg}, {"G1": Wg}
    for v in ("V1", "V2", "V3"):
        diari[v] = []
        Wc1[v] = pesi_variante(pan, idx, U, v, None, diari[v])
        Wc2[v] = pesi_variante(pan, idx, U, v, ammessi, None) if v == "V2" else Wc1[v]
    log("pesi pronti", f"{time.time() - t0:.0f} s")
    usati = sorted({simboli[j] for v in Wc1 for j in np.flatnonzero(np.abs(Wc1[v]).sum(axis=0) > 0)} |
                   {simboli[j] for j in np.flatnonzero(np.abs(Wc2["V2"]).sum(axis=0) > 0)})
    ore = an.candele_ore(usati)
    log("candele orarie pronte", len(usati))

    ris = {"periodo": [sc.data(int(giorni[0])), sc.data(int(giorni[-1]))], "giorni": int(len(giorni)), "capitale": CAP,
           "giorni_moneta_oltre_3_G1": n65, "varianti": {}}
    serie = {}
    for v in ("G1", "V1", "V2", "V3"):
        W1 = Wc1[v]
        d1 = an.conto(v, W1, R, F, costo, giorni, simboli, ore)
        m1 = misure_conto(d1, W1, R, F, giorni)
        mv, mc = deriva_massima(W1, R, F)
        m1["peso_max_venduta_voluto"] = float((-W1).max())
        m1["peso_max_comprata_voluto"] = float(W1.max())
        m1["peso_max_venduta_con_deriva"] = float(mv.max())
        m1["peso_max_comprata_con_deriva"] = float(mc.max())
        m1["giorni_peso_venduta_oltre_20pc"] = int(((-W1).max(axis=1) > SOGLIA_PESO + 1e-12).sum())
        m1["giorni_moneta_oltre_3pc"] = giorni_moneta_oltre_3(W1, EXC)
        nl = (W1 > 0).sum(axis=1)
        ns = (W1 < 0).sum(axis=1)
        m1["giorni_con_lunghi_sotto_10"] = int((nl < 10).sum())
        m1["giorni_con_corti_sotto_10"] = int((ns < 10).sum())
        m1["variazioni"], m1["a_limite"] = d1.attrs["variazioni"], d1.attrs["a_limite"]
        m1["numeri_settimana_corretto"] = te.numeri_settimana(an.settimane(d1)["netto"])
        serie[v] = an.settimane(d1)["netto"]
        r = {"conto1": m1, "conto2": {}}
        for nome, ch in (("A", False), ("A2", True)):
            W2 = Wc2[v]
            X, D, st = o86.conto_vero(W2, R, O, CAP, vmin, passo, qmin, True, ch)
            d2 = o86.netto_del_conto(X, D, R, F, costo, giorni, simboli, ore)
            m2 = an.sintesi(d2)
            w2 = an.settimane(d2)["netto"].to_numpy()
            m2["t"] = float(nu.numeri(w2)["sharpe"] * np.sqrt(len(w2) / 52))
            m2.update(st)
            r["conto2"][nome] = m2
            log(v, nome, f"Sharpe {m2['sharpe']:.2f}", f"discesa {m2['discesa']:.1%}", f"saltati {st['ordini_saltati']}")
        if v == "V2":
            r["v2_monete_senza_filtri_non_aggiunte_nel_conto2"] = int((Wc1["V2"] != Wc2["V2"]).any(axis=1).sum())
        r["giorni_rari"] = [list(map(str, x)) for x in diari.get(v, [])]
        ris["varianti"][v] = r
        log(v, f"Sharpe {m1['sharpe']:.2f} discesa {m1['discesa']:.1%} t {m1['t']:.1f} venduta max {m1['peso_max_venduta_voluto']:.1%}")

    # esame scritto
    g = ris["varianti"]["G1"]
    for v in ("V1", "V2", "V3"):
        r = ris["varianti"][v]
        m = r["conto1"]
        c1 = {"peso_venduta_max_al_massimo_20pc": m["peso_max_venduta_voluto"] <= SOGLIA_PESO + 1e-12,
              "sharpe_scende_al_massimo_0_15": m["sharpe"] >= g["conto1"]["sharpe"] - SOGLIA_SHARPE,
              "discesa_peggiora_al_massimo_3_punti": m["discesa"] >= g["conto1"]["discesa"] - SOGLIA_DISCESA,
              "ogni_anno_positivo": all(x > 0 for x in m["per_anno"].values()), "t_almeno_3": m["t"] >= SOGLIA_T}
        c2 = {}
        for nome in ("A", "A2"):
            a, ra = r["conto2"][nome], g["conto2"][nome]
            c2[nome] = {"ogni_anno_positivo": all(x > 0 for x in a["per_anno"].values()),
                        "sharpe_scende_al_massimo_0_15": a["sharpe"] >= ra["sharpe"] - SOGLIA_SHARPE,
                        "ordini_saltati_non_piu_di_G1": a["ordini_saltati"] <= ra["ordini_saltati"]}
        r["esame"] = {"conto1": c1, "conto2": c2,
                      "passa": bool(all(c1.values()) and all(all(x.values()) for x in c2.values()))}

    # Sharpe corretto: per prova (N = 312) e per famiglie (asticella dell'11 novembre)
    try:
        from research.programma6 import asticella as ast
        nuove = {f"152 {v}": serie[v] for v in ("V1", "V2", "V3")}
        cand = {f"152 {v}": ris["varianti"][v]["conto1"]["numeri_settimana_corretto"] for v in ("V1", "V2", "V3")}
        cr = ast.corretto_rivisto(nuove, cand)
        prove_ = ast.le_prove()
        ser = {n: ast.periodo(s) for n, s, _ in prove_ if s is not None}
        ser.update({n: ast.periodo(s) for n, s in ast.serie_nuove().items()})
        ser.update({n: ast.periodo(s) for n, s in nuove.items()})
        soli = [x for _, s, x in prove_ if s is None]
        gr = ast.gruppi(ser, ast.TAGLIO)
        sr_tutti, sr_v = ast.per_v(gr, soli, False), ast.per_v(gr, soli, True)
        for v in ("V1", "V2", "V3"):
            i = cand[f"152 {v}"]
            a = (i["sharpe"], i["settimane"], i["asimmetria"], i["curtosi"])
            ris["varianti"][v]["sharpe_corretto"] = {
                "per_famiglie": cr["candidate"][f"152 {v}"]["corretto"],
                "per_famiglie_con_aggiunta": cr["candidate"][f"152 {v}"]["corretto_con_aggiunta"],
                "famiglie_N": cr["gruppi"], "gruppo_della_variante": cr["candidate"][f"152 {v}"]["gruppo"],
                "per_prova_N312": float(te.sharpe_corretto(*a, sr_v, 52, n_prove=312)),
                "t": cr["candidate"][f"152 {v}"]["t"]}
    except Exception as e:                                           # non decide l'esame: si scrive l'errore
        ris["sharpe_corretto_errore"] = repr(e)
        log("Sharpe corretto non calcolato:", repr(e))

    (OUT / "risultati.json").write_text(json.dumps(ris, indent=1, ensure_ascii=False, default=str), encoding="utf-8")
    pd.DataFrame({k: v for k, v in serie.items()}).to_csv(OUT / "settimane_conto1.csv.gz", float_format="%.8f")
    for v in ("V1", "V2", "V3"):
        r = ris["varianti"][v]
        m = r["conto1"]
        prove.registra(ID, v, {"variante": v, "tetto": SOGLIA_PESO if v != "V2" else None, "minimo_monete": 10 if v != "V1" else None,
                               "capitale_conto2": CAP}, "giornaliera, conti settimanali", int(len(giorni)),
                       {"sharpe": m["sharpe"], "annuo": m["annuo"], "discesa": m["discesa"], "t": m["t"],
                        "peso_max_venduta": m["peso_max_venduta_voluto"], "sharpe_A": r["conto2"]["A"]["sharpe"],
                        "sharpe_A2": r["conto2"]["A2"]["sharpe"], "sharpe_G1": g["conto1"]["sharpe"],
                        "discesa_G1": g["conto1"]["discesa"]},
                       "passa" if r["esame"]["passa"] else "non passa", "esame scritto della prova 152; seme: nessuno (calcolo deterministico)",
                       seme=0)
    log("fatto", f"{time.time() - t0:.0f} s")


if __name__ == "__main__":
    main()
