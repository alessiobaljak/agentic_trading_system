"""Prova 153 (NOVANTUNESIMA.md): il libro degli ordini fra le monete, deciso ogni giorno come G1.

Uso (dalla radice del repo):
  python3 -m research.programma7.novantunesima scarica   # riprende da dove si e' fermato; prima misura 500 coppie e decide 100/60
  python3 -m research.programma7.novantunesima calcola   # solo a scarico finito
Gli zip grezzi stanno solo in memoria: si tiene il riassunto giornaliero (somma e numero dei rapporti per rilevazione, A e B).
"""
from __future__ import annotations

import hashlib
import io
import json
import sys
import time
import zipfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import numpy as np
import pandas as pd

from research.programma5.strumenti.libro import aggrega_giorno  # noqa: F401  (richiamato dalle regole; il riassunto per rilevazione e' qui sotto)
from research.programma5.strumenti.scarico import BASE, _prendi
from research.src.dati import leggi_checksum

QUI = Path(__file__).resolve().parent
RIS = QUI / "risultati_novantunesima"
RIASSUNTI = RIS / "riassunti.csv"
SCELTA = RIS / "scelta.json"
PROVA_N, SOGLIA_ORE, N_COPPIE_TOT, PARALLELO = 500, 10.0, 137200, 8
SEME = 153


def coppie(n_uni: int):
    """[(simbolo, giorno_indice_assoluto)] ordinate per giorno e simbolo, dall'universo di G1 (n_uni = 100 o 60)."""
    import research.programma7.revisione_g1n.nucleo as nu
    from research.programma6 import seconda as sc
    from research.programma7.revisione_g1n import analisi as an
    pan = sc.pannello()
    giorni = np.arange(sc.giorno(2023, 1, 2), an.FINE, dtype=np.int64)
    vecchio = nu.N_UNI
    nu.N_UNI = n_uni
    try:
        U = nu.universo_giorni(pan, giorni - pan["t0"])
    finally:
        nu.N_UNI = vecchio
    sim = pan["simboli"]
    # il segnale del giorno D usa il file del giorno D-1: la coppia e' (moneta dell'universo di D, giorno D-1)
    return [(sim[j], int(giorni[k]) - 1) for k in range(len(giorni)) for j in np.flatnonzero(U[k])]


def riassunto(contenuto: bytes) -> dict:
    """Per ogni rilevazione (istante) con tutti e due i lati: (acquisti - vendite)/(acquisti + vendite); somma e numero, A (5%) e B (1%)."""
    with zipfile.ZipFile(io.BytesIO(contenuto)) as z:
        df = pd.read_csv(io.BytesIO(z.read(z.namelist()[0])))
    df = df[df["percentage"].isin([-5, 5, -1, 1])]
    larga = df.pivot_table(index="timestamp", columns="percentage", values="notional", aggfunc="last")
    out = {}
    for nome, k in (("A", 5), ("B", 1)):
        if -k in larga.columns and k in larga.columns:
            b, a = larga[-k], larga[k]
            r = ((b - a) / (b + a)).replace([np.inf, -np.inf], np.nan).dropna()
            out[nome] = (float(r.sum()), int(len(r)))
        else:
            out[nome] = (0.0, 0)
    return out


def una(coppia):
    s, g = coppia
    from research.programma6 import seconda as sc
    d = sc.data(g)
    chiave = f"data/futures/um/daily/bookDepth/{s}/{s}-bookDepth-{d}.zip"
    c = _prendi(BASE + chiave)
    if c is None:
        return s, g, None, None
    somma = _prendi(BASE + chiave + ".CHECKSUM")
    imp = hashlib.sha256(c).hexdigest()
    if somma is not None and leggi_checksum(somma, chiave) != imp:
        raise RuntimeError(f"CHECKSUM diverso per {chiave}")
    return s, g, imp, riassunto(c)


def fatte():
    if not RIASSUNTI.exists():
        return set()
    d = pd.read_csv(RIASSUNTI, usecols=["simbolo", "giorno"])
    return set(zip(d["simbolo"], d["giorno"].astype(int)))


def scarica_lista(lista, t_max=None):
    RIS.mkdir(parents=True, exist_ok=True)
    nuovo = not RIASSUNTI.exists()
    fatto = fatte()
    da_fare = [c for c in lista if c not in fatto]
    t0 = time.time()
    n = 0
    with RIASSUNTI.open("a") as f, ThreadPoolExecutor(max_workers=PARALLELO) as ex:
        if nuovo:
            f.write("simbolo,giorno,presente,sumA,nA,sumB,nB,impronta\n")
        for blocco in range(0, len(da_fare), 64):
            if t_max and time.time() - t0 > t_max:
                break
            for s, g, imp, r in ex.map(una, da_fare[blocco:blocco + 64]):
                if imp is None:
                    f.write(f"{s},{g},0,0,0,0,0,\n")
                else:
                    f.write(f"{s},{g},1,{r['A'][0]!r},{r['A'][1]},{r['B'][0]!r},{r['B'][1]},{imp}\n")
                n += 1
            f.flush()
    return n, time.time() - t0


def main_scarica():
    t_max = float(sys.argv[2]) if len(sys.argv) > 2 else None
    if not SCELTA.exists():
        l100 = coppie(100)
        assert len(l100) == N_COPPIE_TOT, len(l100)
        n, sec = scarica_lista(l100[:PROVA_N])
        stima = sec / n * N_COPPIE_TOT / 3600
        scelta = {"coppie_misurate": n, "secondi": round(sec, 1), "stima_ore_per_137200": round(stima, 2),
                  "soglia_ore": SOGLIA_ORE, "monete": 100 if stima <= SOGLIA_ORE else 60}
        SCELTA.write_text(json.dumps(scelta, indent=1))
        print("[scelta]", scelta, flush=True)
    sc_ = json.loads(SCELTA.read_text())
    lista = coppie(sc_["monete"])
    n, sec = scarica_lista(lista, t_max)
    fatto = fatte()
    manca = sum(1 for c in lista if c not in fatto)
    print(f"[scarico] ora {n} coppie in {sec:.0f}s; totale lista {len(lista)}; ancora da fare {manca}", flush=True)


def main_calcola():
    import os
    os.environ.setdefault("CACHE_G1N", "/tmp/claude-0/-home-user-agentic-trading-system/9da12ffe-13c5-5904-8f7e-5ce576103042/scratchpad/cache_g1n")
    import math
    import subprocess
    import research.programma7.revisione_g1n.nucleo as nu
    from research.programma6 import asticella as ast, seconda as sc, terza as te
    from research.programma7.revisione_g1n import analisi as an
    from research.src import prove
    scelta = json.loads(SCELTA.read_text())
    n_uni = scelta["monete"]
    lista = coppie(n_uni)
    fatto = fatte()
    manca = [c for c in lista if c not in fatto]
    if manca:
        print(f"[stop] scarico incompleto: mancano {len(manca)} coppie; non si calcola"); return
    pan = sc.pannello()
    sim = pan["simboli"]
    ind = {s_: j for j, s_ in enumerate(sim)}
    giorni = np.arange(sc.giorno(2023, 1, 2), an.FINE, dtype=np.int64)
    idx = giorni - pan["t0"]
    nu.N_UNI = n_uni
    U = nu.universo_giorni(pan, idx)
    d = pd.read_csv(RIASSUNTI)
    mancanti = int((d["presente"] == 0).sum())
    # matrici S[giorno D, moneta] con il file del giorno D-1; rilevazioni < 2.000 -> nessun segnale
    pos = {int(g): k for k, g in enumerate(giorni)}
    SS = {}
    for v, (cs, cn) in {"A": ("sumA", "nA"), "B": ("sumB", "nB")}.items():
        M = np.full((len(giorni), len(sim)), np.nan)
        for s_, g, pr, su, n_ in zip(d["simbolo"], d["giorno"], d["presente"], d[cs], d[cn]):
            k = pos.get(int(g) + 1)
            if k is not None and pr == 1 and n_ >= 2000 and s_ in ind:
                M[k, ind[s_]] = su / n_
        SS[v] = M
    giorni_usati = {v: int((np.isfinite(SS[v]) & U).any(axis=1).sum()) for v in SS}
    monete_giorno = {v: float((np.isfinite(SS[v]) & U).sum(axis=1).mean()) for v in SS}
    rc = nu.ritorni_chiusura(pan["close"])
    R = nu.ritorni_tenuta(pan["open"], pan["close"])[idx]
    F = np.nan_to_num(pan["funding"][idx])
    costo = np.array([nu.costo_di(s_) for s_ in sim])
    ore = an.candele_ore(sim)

    def pesi_da(S):
        W = np.zeros((len(idx), len(sim)))
        lunghi, corti = set(), set()
        for k, i in enumerate(idx):
            sig = nu.sigma30(rc, i)
            ct = np.where(np.isfinite(sig), S[k], np.nan)
            W[k], lunghi, corti = nu.passo_banda(ct, U[k], sig, lunghi, corti)
        return W

    def conto_w(W):
        return an.conto("x", W, R, F, costo, giorni, sim, ore)

    def sett(dd):
        return an.settimane(dd)["netto"]

    def esame_serie(dd):
        w = sett(dd)
        z = te.numeri_settimana(w)
        z["t"] = z["sharpe"] * math.sqrt(z["settimane"] / 52)
        a = an.anno(w.index)
        z["per_anno"] = {int(y): float(w[a == y].mean() * 52) for y in sorted(set(a))}
        return z

    def senza10(x):
        v = np.sort(np.asarray(x))[:-10]
        return float(v.mean() * 365)

    ris, serie = {}, {}
    for v in ("A", "B"):
        t0 = time.time()
        rv = {"giorni_con_segnale": giorni_usati[v], "monete_medie_al_giorno": monete_giorno[v]}
        try:
            W = pesi_da(SS[v])
            dd = conto_w(W)
            serie[v] = sett(dd)
            e = esame_serie(dd)
            rv.update(e)
            rv["rendimento_netto_annuo_giorni"] = float(dd["netto"].mean() * 365)
            rv["discesa_giornaliera"] = nu.numeri(dd["netto"].to_numpy(), 365)["discesa"]
            rv["sharpe_giornaliero_365"] = nu.numeri(dd["netto"].to_numpy(), 365)["sharpe"]
            rv["giro_medio_giorno"] = float(np.abs(np.diff(W, axis=0, prepend=0)).sum(axis=1).mean())
            rv["spese_medie_giorno"] = float(dd["spese"].mean()); rv["spese_annue"] = float(dd["spese"].mean() * 365)
            rv["funding_annuo"] = float(dd["funding"].mean() * 365)
            rv["variazioni_e_a_limite"] = [dd.attrs["variazioni"], dd.attrs["a_limite"]]
            rv["netto_costi_x3_annuo"] = float(dd["netto_triplo"].mean() * 365)
            for lato, WL in (("long", np.where(W > 0, W, 0.0)), ("short", np.where(W < 0, W, 0.0))):
                dl = conto_w(WL)
                rv[f"lato_{lato}"] = {"annuo": float(dl["netto"].mean() * 365), "annuo_senza_10_giorni_migliori": senza10(dl["netto"]),
                                       "per_anno": {int(y): float(dl["netto"][an.anno(giorni) == y].mean() * 365) for y in sorted(set(an.anno(giorni)))}}
            # controllo al contrario (descrittivo)
            dc = conto_w(pesi_da(-SS[v]))
            ec = esame_serie(dc)
            rv["controllo_al_contrario"] = {"annuo": ec["annuo"], "sharpe": ec["sharpe"], "per_anno": ec["per_anno"]}
            rv["_W"] = W
        except Exception as ex:  # anche una variante fallita si registra
            rv["errore"] = repr(ex)
        ris[v] = rv
        print(f"[{v}] {time.time() - t0:.0f}s", flush=True)

    # G1 e F5 per le correlazioni (G1 dalla funzione scritta di nucleo, stesso universo e stessi giorni)
    W1, _, _ = nu.pesi(pan, idx, U)
    g1 = conto_w(W1)
    g1s = sett(g1)
    f5 = next((s_ for n_, s_, _ in ast.le_prove() if n_ == "24 F5"), None)
    corr = {}
    for v in ("A", "B"):
        if v not in serie:
            continue
        c1 = g1s.index.intersection(serie[v].index)
        corr[v] = {"G1_giornaliera": float(np.corrcoef(conto_w(ris[v]["_W"])["netto"], g1["netto"])[0, 1]),
                   "G1_settimanale": float(np.corrcoef(serie[v].loc[c1], g1s.loc[c1])[0, 1])}
        if f5 is not None:
            c5 = serie[v].index.intersection(f5.index)
            corr[v]["F5_settimanale"] = float(np.corrcoef(serie[v].loc[c5], f5.loc[c5])[0, 1]); corr[v]["settimane_comuni_F5"] = int(len(c5))
    # Sharpe corretto per famiglie (asticella.corretto_famiglie, mazzo completo, 12 novembre)
    ok = {v: serie[v] for v in serie}
    cand = {f"153 {v}": {k: ris[v][k] for k in ("sharpe", "settimane", "asimmetria", "curtosi")} for v in ok}
    corretto = ast.corretto_famiglie({f"153 {v}": s_ for v, s_ in ok.items()}, cand) if ok else {}
    sr_gr = None
    for v in ok:
        ris[v]["sharpe_corretto_famiglie"] = corretto["candidate"][f"153 {v}"]
    ris.pop("_dummy", None)
    commit = subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True).stdout.strip()
    esito = {}
    for v in ("A", "B"):
        rv = ris[v]
        rv.pop("_W", None)
        if "errore" in rv:
            esito[v] = "errore"
        else:
            anni_ok = all(x > 0 for x in rv["per_anno"].values())
            sc_ = rv["sharpe_corretto_famiglie"]["corretto"]
            lati = all(rv[f"lato_{l}"]["annuo_senza_10_giorni_migliori"] >= 0 for l in ("long", "short"))
            rv["esame"] = {"netto_positivo": rv["annuo"] > 0, "ogni_anno_positivo": anni_ok, "t_almeno_3": rv["t"] >= 3,
                           "sharpe_corretto_almeno_0.80": sc_ >= 0.80, "lati_senza_10_giorni_ok": lati}
            esito[v] = "promettente" if all(rv["esame"].values()) else "non promettente"
        misure = {k: rv.get(k) for k in ("annuo", "sharpe", "t", "discesa_max", "per_anno", "giorni_con_segnale", "spese_annue")}
        misure["sharpe_corretto"] = rv.get("sharpe_corretto_famiglie", {}).get("corretto")
        prove.registra("novantunesima", v, {"variante": v, "livello_pct": 5 if v == "A" else 1, "monete": n_uni, "banda": [0.2, 0.4],
                       "vol_giorni": 30, "periodo": "2023-01-02..2026-10-04"}, "giornaliera (settimane per lo Sharpe)",
                       rv.get("giorni_con_segnale", 0), misure, esito[v], note=rv.get("errore", ""), seme=SEME, commit=commit)
    out = {"scelta": scelta, "monete": n_uni, "coppie_presenti": int((d["presente"] == 1).sum()), "coppie_mancanti_404": mancanti,
           "varianti": ris, "correlazioni": corr, "esito": esito, "commit": commit}
    (RIS / "esame.json").write_text(json.dumps(out, indent=1, default=str))
    print(json.dumps({v: {"esito": esito[v], "annuo": ris[v].get("annuo"), "sharpe": ris[v].get("sharpe"), "t": ris[v].get("t"),
                          "per_anno": ris[v].get("per_anno"), "corretto": ris[v].get("sharpe_corretto_famiglie", {}).get("corretto")} for v in ris}, default=str))


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "scarica":
        main_scarica()
    elif len(sys.argv) > 1 and sys.argv[1] == "calcola":
        main_calcola()
    else:
        print(__doc__)
