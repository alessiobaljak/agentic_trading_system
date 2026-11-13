"""Prova 155 (NOVANTATREESIMA.md, regole corrette il 13 novembre 2026, commit 8010fc8 e 946cf8a): G1 con il freno del DVOL.
Si cambia solo il peso del giorno: W_variante = m * W di G1 pieno (m = 1, 0,5 o 0). Parita' con la prova 120 obbligatoria prima di tutto.

Uso (dalla radice del repo):  python3 -m research.programma7.novantatreesima
"""
from __future__ import annotations

import json
import math
import subprocess
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

QUI = Path(__file__).resolve().parent
RIS = QUI / "risultati_novantatreesima"
DVOL = QUI.parents[1] / "research" / "data" / "dvol" / "BTC.json"
SEME = 155
FINESTRA, MINIMO, SOGLIA = 180, 170, 0.80
VARIANTI = {"A": 0.5, "B": 0.0}


def commit() -> str:
    return subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True).stdout.strip()


def segnale(dv: dict, giorni: np.ndarray, ritardo: int = 0) -> tuple:
    """Per ogni giorno D: (sopra, rango, presenti). Valore = chiusura di D-1-ritardo; confronto = le 180 chiusure prima di lei (lei esclusa).
    Rango = (minori + meta' degli uguali) / presenti; sopra = rango > 0,80; con meno di 170 presenti o senza valore: piena (sopra = False)."""
    sopra = np.zeros(len(giorni), bool)
    rango = np.full(len(giorni), np.nan)
    pres = np.zeros(len(giorni), int)
    for k, D in enumerate(giorni):
        v = int(D) - 1 - ritardo
        if v not in dv or int(D) - 1 - FINESTRA < min(dv):      # finestra intera di 180 giorni (regola del 13 novembre, punto 3)
            continue
        w = np.array([dv[g] for g in range(v - FINESTRA, v) if g in dv])
        pres[k] = len(w)
        if len(w) < MINIMO:
            continue
        x = dv[v]
        rango[k] = ((w < x).sum() + 0.5 * (w == x).sum()) / len(w)
        sopra[k] = rango[k] > SOGLIA
    return sopra, rango, pres


def nw_t(d: np.ndarray, lag: int = 7) -> float:
    n = len(d)
    e = d - d.mean()
    s = e @ e / n
    for l in range(1, lag + 1):
        s += 2 * (1 - l / (lag + 1)) * (e[l:] @ e[:-l] / n)
    return float(d.mean() / math.sqrt(s / n))


def t_semplice(d: np.ndarray) -> float:
    return float(d.mean() / (d.std(ddof=1) / math.sqrt(len(d))))


def numeri_giorni(x: np.ndarray, giorni: np.ndarray) -> dict:
    eq = np.cumprod(1 + x)
    anno = pd.to_datetime(giorni * 86400, unit="s").year
    return {"giorni": int(len(x)), "annuo_365": float(x.mean() * 365), "sharpe_365": float(x.mean() / x.std(ddof=1) * math.sqrt(365)),
            "t_giornaliero": t_semplice(x), "discesa_giornaliera": float((eq / np.maximum.accumulate(eq) - 1).min()),
            "per_anno": {int(a): float(x[anno == a].mean() * 365) for a in sorted(set(anno))},
            "giorni_per_anno": {int(a): int((anno == a).sum()) for a in sorted(set(anno))}}


def main():
    from research.programma6 import asticella as ast, cinquantaseiesima as cs, seconda as sc, sesta as se, terza as te
    from research.programma6 import ottava as ot, ventiquattresima as vq
    from research.programma7 import prima as pr
    from research.src import prove
    RIS.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    cm = commit()
    pan = sc.pannello()
    ps = te.pannello_settimane(pan, log=lambda x: None, indicatori_si=False)
    giorni = np.arange(se.INIZIO, pr.FINE, dtype=np.int64)
    idx = giorni - pan["t0"]
    Ud = pr.universo_del_giorno(giorni, ps["lunedi"], ps["U"])
    sig = ot.sigma_30(pan, idx)
    W = vq.pesi_banda(np.where(np.isfinite(sig), -se.funding_7(pan, idx), np.nan), Ud, sig)
    R = sc.rendimenti(pan)[idx]
    F = np.nan_to_num(pan["funding"][idx])
    costo = sc.costi_moneta(pan["simboli"])
    print(f"[pronto] {time.time() - t0:.0f}s", flush=True)

    def conta(m: np.ndarray) -> pd.DataFrame:
        Wv = W * m[:, None]
        d = te.conto(Wv, R, F, costo)
        spese, n_tot, n_lim, n_senza = cs.spese_a_limite(Wv, R, giorni, pan["simboli"], costo)
        d["spese"] = spese
        d["netto"] = d["lordo"] - d["spese"] - d["funding"]
        d.attrs["ordini"] = [n_tot, n_lim, n_senza]
        return d

    # --- 1. parita' obbligatoria (m = 1) ---
    g1 = conta(np.ones(len(giorni)))
    rif = pd.read_csv(pr.RIS / "giorni_G1.csv.gz")
    stesso_giorno = bool((rif["giorno"].to_numpy() == giorni).all())
    ok_g = giorni < sc.giorno(2026, 9, 30)
    cols = ("lordo", "spese", "funding", "netto", "giro", "monete")
    dc = {c: np.abs(g1[c].to_numpy().astype(float) - rif[c].to_numpy().astype(float)) for c in cols}
    par = {"righe": [len(g1), len(rif)], "stessi_giorni": stesso_giorno,
           "differenza_massima_fino_29_settembre": {c: float(dc[c][ok_g].max()) for c in cols},
           "differenze_ultimi_giorni": {sc.data(int(g)): {c: float(dc[c][k]) for c in cols} for k, g in enumerate(giorni) if not ok_g[k] and any(dc[c][k] > 1e-12 for c in cols)},
           "giorni_con_differenza_dopo_29_settembre": int(sum(any(dc[c][k] > 1e-12 for c in cols) for k in range(len(giorni)) if not ok_g[k]))}
    par["coincide"] = bool(stesso_giorno and len(g1) == len(rif) and all(v < 1e-12 for v in par["differenza_massima_fino_29_settembre"].values()))
    print("[parita]", json.dumps(par)[:1500], flush=True)
    (RIS / "parita.json").write_text(json.dumps(par, indent=1))
    prove.registra("novantatreesima", "G1_parita_2", {"m": 1, "controllo": "parita fino al 29 settembre 2026, tutte le colonne (regola 8f87e9d)"}, "giornaliera",
                   len(g1), par, "parita ok" if par["coincide"] else "parita NON ok", note="controllo, non variante", seme=SEME, commit=cm)
    if not par["coincide"]:
        print("PARITA NON COINCIDE: mi fermo", flush=True)
        return 1

    # --- 2. segnale ---
    dv = {int(k): float(v) for k, v in json.loads(DVOL.read_text()).items()}
    sopra, rango, pres = segnale(dv, giorni)
    calc = np.isfinite(rango)
    primo = int(giorni[np.flatnonzero(calc)[0]])
    ultimo = int(giorni[-1])
    sel = giorni >= primo
    lun = pr.lunedi_del_giorno(giorni)
    prima_lun = primo + (7 - ((primo + 3) % 7)) % 7           # primo lunedi' >= primo
    selw = giorni >= prima_lun
    info = {"primo_giorno_con_rango": sc.data(primo), "ultimo_giorno": sc.data(ultimo), "giorni_giudicati": int(sel.sum()),
            "primo_lunedi_serie_settimanale": sc.data(prima_lun), "giorni_senza_rango_dopo_il_primo": int((~calc & sel).sum()),
            "giorni_con_meno_di_180_presenti_dopo_il_primo": int(((pres < FINESTRA) & sel).sum()),
            "giorni_sopra_80": int(sopra[sel].sum()), "quota_sopra_80": float(sopra[sel].mean()),
            "dvol_primo_giorno": sc.data(min(dv)), "dvol_ultimo_giorno": sc.data(max(dv)), "dvol_giorni": len(dv),
            "lettura_rango": "valore = chiusura di D-1; confronto = 180 chiusure D-181..D-2; rango = (minori + meta' uguali)/presenti; >0,80; <170 presenti = piena"}
    print("[segnale]", json.dumps(info), flush=True)

    def sett(dd: pd.Series) -> pd.Series:
        return dd[selw].groupby(lun[selw]).sum()

    def esame(nome: str, d: pd.DataFrame, ritardo: bool = False) -> dict:
        x = d["netto"].to_numpy()
        r = numeri_giorni(x[sel], giorni[sel])
        w = sett(pd.Series(x, index=giorni))
        z = te.numeri_settimana(w)
        z["t"] = z["sharpe"] * math.sqrt(z["settimane"] / 52)
        r["settimanale"] = z
        r["spese_annue"] = float(d["spese"].to_numpy()[sel].mean() * 365)
        r["funding_annuo"] = float(d["funding"].to_numpy()[sel].mean() * 365)
        r["giro_medio_giorno"] = float(d["giro"].to_numpy()[sel].mean())
        r["ordini_variazioni_limite_senza_candele"] = d.attrs.get("ordini")
        r["giorni_con_posizioni"] = int((d["monete"].to_numpy()[sel] > 0).sum())
        pd.DataFrame({"giorno": giorni, "netto": x, "lordo": d["lordo"], "spese": d["spese"], "funding": d["funding"],
                      "monete": d["monete"]}).to_csv(RIS / f"giorni_{nome}.csv.gz", index=False)
        w.rename("netto").to_csv(RIS / f"settimane_{nome}.csv.gz")
        return r, w, x

    ris, serie, nett = {}, {}, {}
    ris["G1"], serie["G1"], nett["G1"] = esame("G1", g1)
    ordine = []
    for v, m in VARIANTI.items():
        tv = time.time()
        try:
            mm = np.where(sopra, m, 1.0)
            d = conta(mm)
            ris[v], serie[v], nett[v] = esame(v, d)
            ordine.append(v)
        except Exception as ex:
            ris[v] = {"errore": repr(ex)}
        print(f"[{v}] {time.time() - tv:.0f}s", flush=True)
    # controllo descrittivo con un giorno di ritardo in piu' (chiusura di D-2)
    sopra2, _, _ = segnale(dv, giorni, ritardo=1)
    for v, m in VARIANTI.items():
        n = f"{v}_ritardo"
        try:
            d = conta(np.where(sopra2, m, 1.0))
            ris[n], _, nett[n] = esame(n, d)
            ris[n]["giorni_sopra_80"] = int(sopra2[sel].sum())
        except Exception as ex:
            ris[n] = {"errore": repr(ex)}
    # giorni sopra e sotto la soglia per G1 e anni per differenza
    x1 = nett["G1"][sel]
    s_ = sopra[sel]
    ris["G1_sopra_sotto"] = {
        "sopra": {"giorni": int(s_.sum()), "media_giorno": float(x1[s_].mean()), "annuo_365": float(x1[s_].mean() * 365),
                  "sharpe_365": float(x1[s_].mean() / x1[s_].std(ddof=1) * math.sqrt(365)), "somma": float(x1[s_].sum())},
        "sotto": {"giorni": int((~s_).sum()), "media_giorno": float(x1[~s_].mean()), "annuo_365": float(x1[~s_].mean() * 365),
                  "sharpe_365": float(x1[~s_].mean() / x1[~s_].std(ddof=1) * math.sqrt(365)), "somma": float(x1[~s_].sum())}}
    # differenze con G1
    gs = giorni[sel]
    wk = pr.lunedi_del_giorno(giorni)[selw]
    for v in [k for k in ris if k in ("A", "B", "A_ritardo", "B_ritardo") and "errore" not in ris[k]]:
        d = nett[v][sel] - x1
        dw = pd.Series(nett[v][selw] - nett["G1"][selw]).groupby(wk).sum().to_numpy()
        ris[v]["differenza_con_G1"] = {"media_giorno": float(d.mean()), "annuo_365": float(d.mean() * 365), "t_semplice_giorni": t_semplice(d),
                                       "t_settimanale": t_semplice(dw), "t_robusto_newey_west_7": nw_t(d), "settimane": int(len(dw))}
    # Sharpe corretto con le famiglie
    cand = {f"155 {v}": {k: ris[v]["settimanale"][k] for k in ("sharpe", "settimane", "asimmetria", "curtosi")} for v in ordine}
    cand["155 G1 stessi giorni"] = {k: ris["G1"]["settimanale"][k] for k in ("sharpe", "settimane", "asimmetria", "curtosi")}
    corr_f = {}
    if ordine:
        cf = ast.corretto_famiglie({f"155 {v}": serie[v] for v in ordine}, cand)
        corr_f = {k: cf[k] for k in ("serie", "senza_serie", "famiglie", "in_v", "deviazione_v", "taglio")}
        for k, v in cf["candidate"].items():
            corr_f[k] = v
        for v in ordine:
            ris[v]["sharpe_corretto_famiglie"] = cf["candidate"][f"155 {v}"]
        ris["G1"]["sharpe_corretto_famiglie"] = cf["candidate"]["155 G1 stessi giorni"]
        # controllo con taglio 0,3 e 0,7 (descrittivo)
        for tg in ast.ALTRI_TAGLI:
            c2 = ast.corretto_famiglie({f"155 {v}": serie[v] for v in ordine}, cand, taglio=tg)
            corr_f[f"taglio_{tg}"] = {"famiglie": c2["famiglie"], **{k: c2["candidate"][k]["corretto"] for k in c2["candidate"]}}
    # correlazione dei giorni con G1
    for v in ordine:
        ris[v]["correlazione_giornaliera_con_G1"] = float(np.corrcoef(nett[v][sel], x1)[0, 1])
    # esame
    esito = {}
    for v in VARIANTI:
        r = ris[v]
        if "errore" in r:
            esito[v] = "errore"
            continue
        dg, g = r["differenza_con_G1"], ris["G1"]
        pa = r["per_anno"]
        e = {"netto_positivo": r["annuo_365"] > 0, "ogni_anno_positivo": all(a > 0 for a in pa.values()),
             "t_almeno_3": r["settimanale"]["t"] >= 3, "sharpe_corretto_almeno_0.80": r["sharpe_corretto_famiglie"]["corretto"] >= 0.80,
             "sharpe_sopra_G1": r["settimanale"]["sharpe"] > g["settimanale"]["sharpe"] and r["sharpe_365"] > g["sharpe_365"],
             "differenza_media_positiva": dg["media_giorno"] > 0, "differenza_t_almeno_2": dg["t_semplice_giorni"] >= 2}
        r["esame"] = e
        esito[v] = "promettente" if all(e.values()) else "non promettente"
    for v in VARIANTI:
        r = ris[v]
        if "errore" in r:
            misure, n = {}, 0
        else:
            misure = {k: r[k] for k in ("annuo_365", "sharpe_365", "discesa_giornaliera", "per_anno", "spese_annue", "differenza_con_G1", "esame")}
            misure["t_sett"] = r["settimanale"]["t"]
            misure["sharpe_corretto"] = r["sharpe_corretto_famiglie"]["corretto"]
            n = r["giorni"]
        prove.registra("novantatreesima", v, {"variante": v, "m_sopra_80": VARIANTI[v], "soglia_rango": SOGLIA, "finestra": FINESTRA,
                       "minimo_presenti": MINIMO, "periodo": f"{sc.data(primo)}..{sc.data(ultimo)}"}, "giornaliera (settimane per lo Sharpe)", n,
                       misure, esito[v], note=r.get("errore", ""), seme=SEME, commit=cm)
    for v in ("A", "B"):
        n = f"{v}_ritardo"
        r = ris[n]
        misure = {} if "errore" in r else {k: r[k] for k in ("annuo_365", "sharpe_365", "discesa_giornaliera", "giorni_sopra_80")}
        prove.registra("novantatreesima", n, {"variante": v, "m_sopra_80": VARIANTI[v], "ritardo_giorni": 1, "controllo": "descrittivo"},
                       "giornaliera", 0 if "errore" in r else r["giorni"], misure, "controllo, nessuna soglia",
                       note="non e' una variante; " + r.get("errore", ""), seme=SEME, commit=cm)
    out = {"commit": cm, "parita": par, "segnale": info, "risultati": ris, "famiglie": corr_f, "esito": esito}
    (RIS / "esame.json").write_text(json.dumps(out, indent=1, default=str))
    pd.DataFrame({"giorno": giorni, "sopra_80": sopra, "rango": rango, "presenti": pres}).to_csv(RIS / "segnale.csv.gz", index=False)
    for v in VARIANTI:
        r = ris[v]
        if "errore" in r:
            print(v, "ERRORE", r["errore"]); continue
        print(v, esito[v], f"annuo {r['annuo_365']:.3f} sharpe {r['sharpe_365']:.2f} t {r['settimanale']['t']:.2f} disc {r['discesa_giornaliera']:.3f}",
              f"corr {r['sharpe_corretto_famiglie']['corretto']:.2f} dt {r['differenza_con_G1']['t_semplice_giorni']:.2f}", flush=True)
    print("G1", f"annuo {ris['G1']['annuo_365']:.3f} sharpe {ris['G1']['sharpe_365']:.2f}", "FINITA", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
