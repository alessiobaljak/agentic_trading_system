"""Prova 156 (NOVANTAQUATTRESIMA.md + regole corrette 2024ab1): G1 che esce dal lato venduto per N giorni dopo una fiammata (> +20% tenuto).
Uso:  python3 -m research.programma7.novantaquattresima"""
from __future__ import annotations

import json, math, sys, time
from pathlib import Path
import numpy as np
import pandas as pd
from research.programma7.novantatreesima import numeri_giorni, t_semplice, nw_t, commit

QUI = Path(__file__).resolve().parent
RIS = QUI / "risultati_novantaquattresima"
SEME = 156
SOGLIA_F = 0.20
VARIANTI = {"A": 3, "B": 7}


def esclusione(flame: np.ndarray, idx: np.ndarray, N: int) -> np.ndarray:
    """(giorni x monete) vero se nei N giorni prima (D-N..D-1) c'e' stata una fiammata: fine = max(fine, F+N)."""
    if N == 0:
        return np.zeros((len(idx), flame.shape[1]), bool)
    c = np.vstack([np.zeros((1, flame.shape[1]), int), np.cumsum(flame.astype(int), axis=0)])   # c[i] = fiammate nelle righe < i
    return (c[idx] - c[idx - N]) > 0


def cum(R: np.ndarray, k: int, j: int, h: int) -> float:
    return float(np.prod(1 + R[k:k + h, j]) - 1)


def main():
    from research.programma6 import asticella as ast, cinquantaseiesima as cs, seconda as sc, sesta as se, terza as te
    from research.programma6 import ottava as ot, ventiquattresima as vq
    from research.programma7 import prima as pr
    from research.src import prove
    RIS.mkdir(parents=True, exist_ok=True)
    cm = commit()
    pan = sc.pannello()
    ps = te.pannello_settimane(pan, log=lambda x: None, indicatori_si=False)
    giorni = np.arange(se.INIZIO, pr.FINE, dtype=np.int64)
    idx = giorni - pan["t0"]
    Ud = pr.universo_del_giorno(giorni, ps["lunedi"], ps["U"])
    sig = ot.sigma_30(pan, idx)
    W = vq.pesi_banda(np.where(np.isfinite(sig), -se.funding_7(pan, idx), np.nan), Ud, sig)
    Rtot = sc.rendimenti(pan)
    R = Rtot[idx]
    F = np.nan_to_num(pan["funding"][idx])
    simboli = pan["simboli"]
    costo = sc.costi_moneta(simboli)
    flame = Rtot > SOGLIA_F
    anno = pd.to_datetime(giorni * 86400, unit="s").year.to_numpy()
    lun = pr.lunedi_del_giorno(giorni)

    def conta(N: int):
        esc = esclusione(flame, idx, N)
        togli = (W < 0) & esc
        Wv = np.where(togli, 0.0, W)
        d = te.conto(Wv, R, F, costo)
        spese, n_tot, n_lim, n_senza = cs.spese_a_limite(Wv, R, giorni, simboli, costo)
        d["spese"] = spese
        d["netto"] = d["lordo"] - d["spese"] - d["funding"]
        d.attrs["ordini"] = [n_tot, n_lim, n_senza]
        return d, Wv, togli

    # ---- 1. parita' con N = 0 ----
    g1, W0, _ = conta(0)
    assert np.array_equal(W0, W)
    rif = pd.read_csv(pr.RIS / "giorni_G1.csv.gz")
    ok_g = giorni < sc.giorno(2026, 9, 30)
    cols = ("lordo", "spese", "funding", "netto", "giro", "monete")
    dc = {c: np.abs(g1[c].to_numpy().astype(float) - rif[c].to_numpy().astype(float)) for c in cols}
    stessi = bool((rif["giorno"].to_numpy() == giorni).all())
    par = {"righe": [len(g1), len(rif)], "stessi_giorni": stessi,
           "differenza_massima_fino_29_settembre": {c: float(dc[c][ok_g].max()) for c in cols},
           "spese_giorni_diversi_fino_29_settembre": int((dc["spese"][ok_g] > 1e-12).sum()),
           "somma_spese_oggi_e_riferimento": [float(g1["spese"].sum()), float(rif["spese"].sum())]}
    par["coincide"] = bool(stessi and len(g1) == len(rif) and all(par["differenza_massima_fino_29_settembre"][c] < 1e-12 for c in ("lordo", "funding", "giro", "monete")))
    print("[parita]", json.dumps(par)[:900], flush=True)
    (RIS / "parita.json").write_text(json.dumps(par, indent=1))
    prove.registra("novantaquattresima", "G1_parita_N0", {"N": 0, "controllo": "parita come nella 155"}, "giornaliera", len(g1), par,
                   "parita ok" if par["coincide"] else "parita NON ok", note="controllo, non variante", seme=SEME, commit=cm)
    if not par["coincide"]:
        print("PARITA NON COINCIDE: mi fermo")
        return 1

    def esame(nome, d):
        x = d["netto"].to_numpy()
        r = numeri_giorni(x, giorni)
        w = pd.Series(x).groupby(lun).sum()
        w.index = w.index.astype(np.int64)
        z = te.numeri_settimana(w)
        z["t"] = z["sharpe"] * math.sqrt(z["settimane"] / 52)
        r["settimanale"] = z
        r["somma_per_anno"] = {int(a): float(x[anno == a].sum()) for a in sorted(set(anno))}
        r["spese_annue"] = float(d["spese"].mean() * 365)
        r["funding_annuo"] = float(d["funding"].mean() * 365)
        r["giro_medio_giorno"] = float(d["giro"].mean())
        r["ordini_variazioni_limite_senza_candele"] = d.attrs.get("ordini")
        pd.DataFrame({"giorno": giorni, "netto": x, "lordo": d["lordo"], "spese": d["spese"], "funding": d["funding"], "monete": d["monete"]}
                     ).to_csv(RIS / f"giorni_{nome}.csv.gz", index=False)
        w.rename("netto").to_csv(RIS / f"settimane_{nome}.csv.gz")
        return r, w, x

    ris, serie, nett, Wd, togl, dfs = {}, {}, {}, {}, {}, {"G1": g1}
    ris["G1"], serie["G1"], nett["G1"] = esame("G1", g1)
    xr = rif["netto"].to_numpy()
    ris["G1_riferimento"] = numeri_giorni(xr, giorni)
    wr = pd.Series(xr).groupby(lun).sum()
    ris["G1_riferimento"]["settimanale"] = te.numeri_settimana(wr)
    ris["G1_riferimento"]["settimanale"]["t"] = ris["G1_riferimento"]["settimanale"]["sharpe"] * math.sqrt(len(wr) / 52)
    ordine = []
    for v, N in VARIANTI.items():
        try:
            d, Wv, tg = conta(N)
            dfs[v], Wd[v], togl[v] = d, Wv, tg
            ris[v], serie[v], nett[v] = esame(v, d)
            ordine.append(v)
        except Exception as ex:
            ris[v] = {"errore": repr(ex)}
        print(f"[{v}] fatto", flush=True)
    x1 = nett["G1"]
    wk1 = pd.Series(x1).groupby(lun).sum().to_numpy()
    for v in ordine:
        d = nett[v] - x1
        dw = pd.Series(d).groupby(lun).sum().to_numpy()
        pa = {int(a): float(d[anno == a].sum()) for a in sorted(set(anno))}
        tot = float(d.sum())
        ris[v]["differenza_con_G1"] = {"media_giorno": float(d.mean()), "annuo_365": float(d.mean() * 365), "t_semplice_giorni": t_semplice(d),
            "t_settimanale": t_semplice(dw), "t_robusto_newey_west_7": nw_t(d), "settimane": int(len(dw)), "giorni": int(len(d)),
            "somma_per_anno": pa, "anni_2021_2025_positivi": int(sum(pa[a] > 0 for a in range(2021, 2026))), "somma_totale": tot,
            "quota_2026": (pa[2026] / tot if tot > 0 else None), "quota_2021": (pa[2021] / tot if tot > 0 else None)}
        ris[v]["correlazione_giornaliera_con_G1"] = float(np.corrcoef(nett[v], x1)[0, 1])
        ris[v]["correlazione_settimanale_con_G1"] = float(np.corrcoef(serie[v].to_numpy(), serie["G1"].to_numpy())[0, 1])
    # Sharpe corretto
    cand = {f"156 {v}": {k: ris[v]["settimanale"][k] for k in ("sharpe", "settimane", "asimmetria", "curtosi")} for v in ordine}
    cand["156 G1 stessi giorni"] = {k: ris["G1"]["settimanale"][k] for k in ("sharpe", "settimane", "asimmetria", "curtosi")}
    corr_f = {}
    if ordine:
        cf = ast.corretto_famiglie({f"156 {v}": serie[v] for v in ordine}, cand)
        corr_f = {k: cf[k] for k in ("serie", "senza_serie", "famiglie", "in_v", "deviazione_v", "taglio")} | {"candidate": cf["candidate"]}
        for v in ordine:
            ris[v]["sharpe_corretto_famiglie"] = cf["candidate"][f"156 {v}"]
        ris["G1"]["sharpe_corretto_famiglie"] = cf["candidate"]["156 G1 stessi giorni"]
        for tg in ast.ALTRI_TAGLI:
            c2 = ast.corretto_famiglie({f"156 {v}": serie[v] for v in ordine}, cand, taglio=tg)
            corr_f[f"taglio_{tg}"] = {"famiglie": c2["famiglie"], **{k: c2["candidate"][k]["corretto"] for k in c2["candidate"]}}
    # esame
    esito = {}
    for v in VARIANTI:
        r = ris[v]
        if "errore" in r:
            esito[v] = "errore"; continue
        dg, g = r["differenza_con_G1"], ris["G1"]
        e = {"1_netto_positivo": r["annuo_365"] > 0, "2_ogni_anno_positivo": all(a > 0 for a in r["somma_per_anno"].values()),
             "3_t_settimanale_almeno_3": r["settimanale"]["t"] >= 3, "4_sharpe_corretto_almeno_0.80": r["sharpe_corretto_famiglie"]["corretto"] >= 0.80,
             "5a_differenza_media_positiva": dg["media_giorno"] > 0, "5b_t_differenza_almeno_2": dg["t_semplice_giorni"] >= 2,
             "6_paletto_4_anni_su_5": dg["anni_2021_2025_positivi"] >= 4,
             "7_sharpe_sopra_G1": r["settimanale"]["sharpe"] > g["settimanale"]["sharpe"] and r["sharpe_365"] > g["sharpe_365"]}
        r["esame"] = e
        esito[v] = "promettente" if all(e.values()) else "non promettente"
    # ---- controlli descrittivi ----
    ctl = {}
    # coerenza con la misura di partenza: giornate-moneta venduto con fiammata nel giorno (R>0,20) per anno
    gran = (W < 0) & (R > SOGLIA_F)
    ctl["coerenza_voce12_venduto_con_fiammata_per_anno"] = {int(a): int(gran[anno == a].sum()) for a in sorted(set(anno))}
    for v in ordine:
        tg, Wv, N = togl[v], Wd[v], VARIANTI[v]
        c = {}
        c["giornate_moneta_uscite_per_anno"] = {int(a): int(tg[anno == a].sum()) for a in sorted(set(anno))}
        c["monete_distinte_per_anno"] = {int(a): int(tg[anno == a].any(axis=0).sum()) for a in sorted(set(anno))}
        inizio = tg & ~np.vstack([np.zeros((1, tg.shape[1]), bool), tg[:-1]])
        c["episodi_per_anno"] = {int(a): int(inizio[anno == a].sum()) for a in sorted(set(anno))}
        tolto = np.where(tg, -W, 0).sum(axis=1)
        venduto = np.where(W < 0, -W, 0).sum(axis=1)
        c["quota_peso_venduto_tolto_per_anno"] = {int(a): float(tolto[anno == a].sum() / venduto[anno == a].sum()) for a in sorted(set(anno))}
        # cosa fanno dopo
        celle = np.argwhere(tg)
        altre = (W < 0) & ~tg
        post = {}
        for nome, h in (("N", N), ("D+1", 2), ("D+3", 4), ("D+7", 8)):
            righe = []
            for k, j in celle:
                if k + h > len(idx): continue
                a = cum(R, k, j, h)
                oth = np.flatnonzero(altre[k])
                b = float(np.mean([cum(R, k, jj, h) for jj in oth])) if len(oth) else np.nan
                righe.append((anno[k], a, b))
            df = pd.DataFrame(righe, columns=["anno", "a", "b"])
            post[nome] = {int(a): {"n": int(len(g)), "media": float(g.a.mean()), "mediana": float(g.a.median()), "quota_sale": float((g.a > 0).mean()),
                                    "altre_media": float(g.b.mean()), "altre_mediana": float(g.b.median()), "altre_quota_sale": float((g.b > 0).mean())}
                          for a, g in df.groupby("anno")}
        c["dopo_l_uscita"] = post
        # lati
        lat = {}
        for nm, M in (("G1", W), (v, Wv)):
            d = dfs["G1"] if nm == "G1" else dfs[v]
            out = {}
            for a in sorted(set(anno)):
                s = anno == a
                for lato, segno in (("long", M > 0), ("short", M < 0)):
                    out[f"{int(a)}_{lato}"] = {"prezzo": float((M * R * segno)[s].sum()), "funding": float((M * F * segno)[s].sum()),
                                               "totale_a_mercato": float(d[lato][s].sum())}
            lat[nm] = out
        c["lati"] = lat
        ctl[v] = c
    # 8.4
    def riga(sim, data):
        j = simboli.index(sim)
        t = sc.giorno(*data) - pan["t0"]
        return {"simbolo": sim, "giorno_F": sc.data(sc.giorno(*data)), "R_tenuto_giorno_F": float(Rtot[t, j]), "fiammata": bool(Rtot[t, j] > SOGLIA_F),
                "esclusa_da": sc.data(sc.giorno(*data) + 1)}
    ctl["caso_JCTUSDT_8_nov"] = riga("JCTUSDT", (2026, 11, 8)) if "JCTUSDT" in simboli else "assente"
    ctl["caso_TRXUSDT"] = {d: riga("TRXUSDT", (2026, 10, d)) for d in (27, 28, 29)}
    ctl["discesa_max_settimanale"] = {k: ris[k]["settimanale"]["discesa_max"] for k in ["G1"] + ordine}
    out = {"commit": cm, "parita": par, "risultati": ris, "famiglie": corr_f, "esito": esito, "controlli": ctl}
    (RIS / "esame.json").write_text(json.dumps(out, indent=1, default=str))
    for v in VARIANTI:
        r = ris[v]
        misure = {} if "errore" in r else {k: r[k] for k in ("annuo_365", "sharpe_365", "discesa_giornaliera", "somma_per_anno", "spese_annue", "differenza_con_G1", "esame")} | {
            "t_sett": r["settimanale"]["t"], "sharpe_corretto": r["sharpe_corretto_famiglie"]["corretto"]}
        prove.registra("novantaquattresima", v, {"variante": v, "N": VARIANTI[v], "soglia_fiammata": SOGLIA_F, "periodo": "2021-01-04..2026-10-04"},
                       "giornaliera (settimane per lo Sharpe)", 0 if "errore" in r else r["giorni"], misure, esito[v], note=r.get("errore", ""), seme=SEME, commit=cm)
    for k in ["G1"] + ordine:
        r = ris[k]
        print(k, f"annuo {r['annuo_365']:.3f} sharpe {r['sharpe_365']:.2f} t {r['settimanale']['t']:.2f} disc {r['discesa_giornaliera']:.3f}",
              f"corr {r['sharpe_corretto_famiglie']['corretto']:.2f}", (f"dt {r['differenza_con_G1']['t_semplice_giorni']:.2f} anni {r['differenza_con_G1']['anni_2021_2025_positivi']}/5" if k != "G1" else ""), esito.get(k, ""), flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
