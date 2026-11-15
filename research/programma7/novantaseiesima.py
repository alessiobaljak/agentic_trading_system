"""Prova 158 (NOVANTASEIESIMA.md, regole 810c620 e 049a4ae): G1 con la leva piu' alta (m = 1,5 e 2) con lo stop del conto vero.
Pesi m * W di G1 (prima.py), spese e funding ricalcolati; stop a -35% dal massimo sulle chiusure orarie, fuori fino al primo lunedi'
con data almeno il giorno dello stop + 3; liquidazione col caso peggiore dell'ora (candele a 1 ora).

Uso (dalla radice del repo):  python3 -m research.programma7.novantaseiesima
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
RIS = QUI / "risultati_novantaseiesima"
SEME = 158
M = {"G1": 1.0, "A": 1.5, "B": 2.0}
MARGINE, MARGINE_ALTO = 0.01, 0.025
SOGLIA_STOP = 0.65
N_STOP = 2


def commit() -> str:
    return subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True).stdout.strip()


def main():
    from research.programma6 import asticella as ast, cinquantaseiesima as cs, esecuzione as es, seconda as sc, sesta as se, terza as te
    from research.programma6 import ottava as ot, ventiquattresima as vq
    from research.programma7 import prima as pr
    from research.src import prove
    RIS.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    cm = commit()
    pan = sc.pannello()
    ps = te.pannello_settimane(pan, log=lambda x: None, indicatori_si=False)
    giorni = np.arange(se.INIZIO, pr.FINE, dtype=np.int64)
    nd = len(giorni)
    idx = giorni - pan["t0"]
    Ud = pr.universo_del_giorno(giorni, ps["lunedi"], ps["U"])
    sig = ot.sigma_30(pan, idx)
    W = vq.pesi_banda(np.where(np.isfinite(sig), -se.funding_7(pan, idx), np.nan), Ud, sig)
    R = sc.rendimenti(pan)[idx]
    R0 = np.nan_to_num(R)
    F = np.nan_to_num(pan["funding"][idx])
    simboli = pan["simboli"]
    costo = sc.costi_moneta(simboli)
    anno = pd.to_datetime(giorni * 86400, unit="s").year.to_numpy()
    print(f"[pronto] {time.time() - t0:.0f}s", flush=True)

    cache = {}

    def ore(s):
        if s not in cache:
            cache[s] = es.ore_di(s)
        return cache[s]

    # ---------------- 1. conti senza stop per m e controlli di parita' ----------------
    def conta(m: float) -> pd.DataFrame:
        Wv = W * m
        d = te.conto(Wv, R, F, costo)
        spese, n_tot, n_lim, n_senza = cs.spese_a_limite(Wv, R, giorni, simboli, costo, ore_di=ore)
        d["spese"] = spese
        d["netto"] = d["lordo"] - d["spese"] - d["funding"]
        d.attrs["ordini"] = [n_tot, n_lim, n_senza]
        return d

    senza = {k: conta(m) for k, m in M.items()}
    print(f"[conti senza stop] {time.time() - t0:.0f}s", flush=True)
    g1 = senza["G1"]
    rif = pd.read_csv(pr.RIS / "giorni_G1.csv.gz")
    ok_g = giorni < sc.giorno(2026, 9, 30)
    cols = ("lordo", "spese", "funding", "netto", "giro", "monete")
    dc = {c: np.abs(g1[c].to_numpy().astype(float) - rif[c].to_numpy().astype(float)) for c in cols}
    par = {"righe": [len(g1), len(rif)], "stessi_giorni": bool((rif["giorno"].to_numpy() == giorni).all()),
           "differenza_massima_fino_29_settembre": {c: float(dc[c][ok_g].max()) for c in cols},
           "giorni_con_differenza_dopo_29_settembre": int(sum(any(dc[c][k] > 1e-12 for c in cols) for k in range(nd) if not ok_g[k]))}
    par["coincide"] = bool(par["stessi_giorni"] and len(g1) == len(rif) and
                           all(par["differenza_massima_fino_29_settembre"][c] < 1e-12 for c in ("lordo", "funding", "giro", "monete")))
    dsp = dc["spese"] > 1e-12
    par["spese_giorni_diversi_per_anno"] = {int(a): int(dsp[(anno == a) & ok_g].sum()) for a in sorted(set(anno))}
    par["somma_spese_oggi_e_riferimento"] = [float(g1["spese"].sum()), float(rif["spese"].sum())]
    par["ordini_G1_oggi_[variazioni,limite,senza_candele]"] = g1.attrs["ordini"]
    par["ordini_per_m"] = {k: senza[k].attrs["ordini"] for k in M}
    par["coerenza"] = {}
    for k in ("A", "B"):
        par["coerenza"][k] = {"lordo_meno_m_lordo1": float(np.abs(senza[k]["lordo"] - M[k] * g1["lordo"]).max()),
                              "funding_meno_m_funding1": float(np.abs(senza[k]["funding"] - M[k] * g1["funding"]).max()),
                              "spese_rapporto_a_G1": float(senza[k]["spese"].sum() / g1["spese"].sum()),
                              "stesse_variazioni_col_limite": senza[k].attrs["ordini"][1] == g1.attrs["ordini"][1]}
    # il 2024 e il 2025 devono coincidere (spese)
    par["spese_2024_2025_coincidono"] = bool(dsp[((anno == 2024) | (anno == 2025)) & ok_g].sum() == 0)
    (RIS / "parita.json").write_text(json.dumps(par, indent=1))
    print("[parita]", json.dumps(par)[:900], flush=True)
    prove.registra("novantaseiesima", "G1_parita", {"m": 1, "controllo": "lordo, funding, giro, monete fino al 29 settembre 2026 entro 1e-12"},
                   "giornaliera", nd, par, "parita ok" if par["coincide"] else "parita NON ok", note="controllo, non variante", seme=SEME, commit=cm)
    if not par["coincide"]:
        print("PARITA NON COINCIDE: mi fermo", flush=True)
        return 1

    # ---------------- 2. candele a 1 ora: rapporti per giorno e moneta ----------------
    usate = np.flatnonzero((W != 0).any(axis=0))
    g0 = int(giorni[0])
    oraidx = np.arange(g0 * 24, (g0 + nd) * 24, dtype=np.int64)
    OHLC = {}
    for j in usate:
        b = ore(simboli[j])
        if b.empty:
            OHLC[j] = None
            continue
        r = b[["open", "high", "low", "close"]].reindex(oraidx).to_numpy(float).reshape(nd, 24, 4)
        OHLC[j] = r
    print(f"[ore] {time.time() - t0:.0f}s, monete {len(usate)}", flush=True)
    G = []       # per giorno: (nz, C, Lo, Hi) rapporti al prezzo delle 00:00, forma (24, k)
    solo_giorno = {"coppie": 0, "totale": 0, "peso_solo_giorno": 0.0, "peso_tot": 0.0, "ore_mancanti_dentro": 0, "per_anno": {}}
    scarto_chiusura = []
    liq_moneta = []
    for k in range(nd):
        nz = np.flatnonzero(W[k])
        C = np.ones((24, len(nz)))
        Lo = np.ones((24, len(nz)))
        Hi = np.ones((24, len(nz)))
        for q, j in enumerate(nz):
            a = OHLC.get(j)
            solo_giorno["totale"] += 1
            solo_giorno["peso_tot"] += abs(W[k, j])
            ya = int(anno[k])
            pa = solo_giorno["per_anno"].setdefault(ya, [0, 0, 0.0, 0.0])
            pa[1] += 1
            pa[3] += abs(W[k, j])
            o0 = np.nan if a is None else a[k, 0, 0]
            if a is None or not np.isfinite(o0) or not np.isfinite(a[k, :, 3]).any():
                C[23, q] = Lo[23, q] = Hi[23, q] = 1 + R0[k, j]
                solo_giorno["coppie"] += 1
                solo_giorno["peso_solo_giorno"] += abs(W[k, j])
                pa[0] += 1
                pa[2] += abs(W[k, j])
                continue
            c = pd.Series(a[k, :, 3]).ffill().fillna(o0).to_numpy()
            solo_giorno["ore_mancanti_dentro"] += int((~np.isfinite(a[k, :, 3])).sum())
            h = np.where(np.isfinite(a[k, :, 1]), a[k, :, 1], c)
            l = np.where(np.isfinite(a[k, :, 2]), a[k, :, 2], c)
            C[:, q], Hi[:, q], Lo[:, q] = c / o0, h / o0, l / o0
            scarto_chiusura.append(abs(C[23, q] - (1 + R0[k, j])))
        G.append((nz, C, Lo, Hi))
    sg = solo_giorno
    sg["quota_peso_solo_giorno"] = sg["peso_solo_giorno"] / sg["peso_tot"]
    sg["per_anno"] = {a: {"monete_giorno": v[0], "su": v[1], "quota_peso": v[2] / v[3] if v[3] else 0.0} for a, v in sg["per_anno"].items()}
    sg["differenza_chiusura_ora23_e_R_media"] = float(np.mean(scarto_chiusura))
    sg["differenza_chiusura_ora23_e_R_massima"] = float(np.max(scarto_chiusura))
    print(f"[rapporti orari] {time.time() - t0:.0f}s solo-giorno {sg['coppie']}/{sg['totale']}", flush=True)

    # controllo per singola moneta (formula esatta, margine iniziale 20%, mantenimento 1%); non dipende da m
    soglia_alta, soglia_bassa = 1.2 / 1.01, 0.8 / 0.99
    for k in range(nd):
        nz, C, Lo, Hi = G[k]
        for q, j in enumerate(nz):
            if W[k, j] < 0 and Hi[:, q].max() >= soglia_alta:
                liq_moneta.append((sc.data(int(giorni[k])), simboli[j], "venduta", float(W[k, j]), float(Hi[:, q].max())))
            if W[k, j] > 0 and Lo[:, q].min() <= soglia_bassa:
                liq_moneta.append((sc.data(int(giorni[k])), simboli[j], "comprata", float(W[k, j]), float(Lo[:, q].min())))

    # ---------------- 3. simulazione del conto con e senza stop ----------------
    lun_ok = lambda x: x + ((-(x + 3)) % 7)           # primo lunedi' >= x
    ap_cache = {}

    def spese_apertura(m: float, k: int) -> float:
        key = (m, k)
        if key not in ap_cache:
            W2 = np.vstack([np.zeros(W.shape[1]), W[k] * m])
            s, *_ = cs.spese_a_limite(W2, np.zeros_like(W2), np.array([giorni[k], giorni[k]]), simboli, costo, ore_di=ore)
            ap_cache[key] = float(s[1])
        return ap_cache[key]

    def simula(nome: str, m: float, stop: bool = True, attesa: str = "lunedi") -> dict:
        d = senza[nome]
        lordo, fund, sp_n = d["lordo"].to_numpy(), d["funding"].to_numpy(), d["spese"].to_numpy()
        cap = 1.0
        massimo = 1.0
        capitale_fase = 1.0
        fuori_fino = -1
        capS = np.zeros(nd + 1)
        rit = np.zeros(nd)
        spD, fuD = np.zeros(nd), np.zeros(nd)
        eventi, liq1, liq25, fuori_giorni = [], [], [], []
        X, Y = [], []          # valori orari: chiusure e caso peggiore (con il valore alle 00:00 davanti)
        nuova_fase = True
        for k in range(nd):
            capS[k] = cap
            if k < fuori_fino:
                fuori_giorni.append(k)
                X += [cap]; Y += [cap]
                continue
            if k == fuori_fino:
                capitale_fase = cap
                massimo = cap
                nuova_fase = True
            nz, C, Lo, Hi = G[k]
            w = W[k, nz] * m
            sp = spese_apertura(m, k) if (nuova_fase and k > 0 and fuori_fino == k) else sp_n[k]
            nuova_fase = False
            Vc = 1 + (C - 1) @ w - sp
            pos_w = w > 0
            peg = np.where(pos_w, Lo, Hi)
            Vw = 1 + (peg - 1) @ w - sp
            Pw = peg @ np.abs(w)
            l1 = np.flatnonzero(Vw <= MARGINE * Pw)
            l2 = np.flatnonzero(Vw <= MARGINE_ALTO * Pw)
            h_stop = None
            run_max = massimo
            if stop:
                for h in range(24):
                    v = cap * Vc[h]
                    run_max = max(run_max, v)
                    livello = max(SOGLIA_STOP * run_max, SOGLIA_STOP * capitale_fase)
                    if v <= livello:
                        h_stop = h
                        break
            last = 23 if h_stop is None else h_stop
            if len(l1) and l1[0] <= last:
                liq1.append((sc.data(int(giorni[k])), int(l1[0]), float(Vw[l1[0]]), float(Pw[l1[0]])))
            if len(l2) and l2[0] <= last:
                liq25.append((sc.data(int(giorni[k])), int(l2[0])))
            X += [cap] + list(cap * Vc[:last + 1])
            Y += [cap] + list(cap * Vw[:last + 1])
            fk = float(F[k, nz] @ w)
            if h_stop is None:
                r = lordo[k] - sp - fund[k]
                spD[k], fuD[k] = sp, fund[k]
                rit[k] = r
                cap *= 1 + r
                massimo = max(run_max, cap)
            else:
                chius = float((np.abs(w) * C[h_stop] * costo[nz]).sum())
                f = fk * (h_stop + 1) / 24
                r = (Vc[h_stop] - 1) - f - chius
                spD[k], fuD[k] = sp + chius, f
                livello = max(SOGLIA_STOP * run_max, SOGLIA_STOP * capitale_fase)
                rit[k] = r
                cap *= 1 + r
                if attesa == "lunedi":
                    fuori_fino = lun_ok(k + 3)
                elif attesa == "1":
                    fuori_fino = k + 1
                elif attesa == "28":
                    fuori_fino = k + 28
                else:
                    fuori_fino = 10 ** 9
                eventi.append({"giorno": sc.data(int(giorni[k])), "ora": h_stop, "valore_ora_su_capitale_00": float(Vc[h_stop]),
                               "valore_conto_dopo": float(cap), "livello": float(livello), "sotto_il_livello_di": float(livello - capS[k] * Vc[h_stop]),
                               "riparte": sc.data(int(giorni[fuori_fino])) if fuori_fino < nd else "dopo la fine",
                               "giorni_fuori": int(min(fuori_fino, nd) - k - 1)})
        capS[nd] = cap
        X, Y = np.array(X), np.array(Y)
        picco = np.maximum.accumulate(X)
        out = {"capitale": capS, "rit": rit, "spese": spD, "funding": fuD, "eventi": eventi, "liq1": liq1, "liq25": liq25,
               "fuori": np.array(fuori_giorni, dtype=int), "dd_ora_chiusure": float((X / picco - 1).min()),
               "dd_ora_peggiore": float((Y / picco - 1).min())}
        # i giorni fuori dopo la fine (ripartenza oltre il periodo) sono gia' contati nel ciclo (k < fuori_fino)
        return out

    def metriche(s: dict, nome: str) -> dict:
        cp = s["capitale"]
        rg = cp[1:] / cp[:-1] - 1
        wk = cp[7::7][: nd // 7] / cp[0:nd:7][: nd // 7] - 1
        lun = giorni[0::7][: nd // 7]
        ws = pd.Series(wk, index=lun)
        z = te.numeri_settimana(ws)
        z["t"] = z["sharpe"] * math.sqrt(z["settimane"] / 52)
        somm = pd.Series(rg).groupby(np.arange(nd) // 7).sum().to_numpy()
        zs = te.numeri_settimana(pd.Series(somm))
        zs["t"] = zs["sharpe"] * math.sqrt(zs["settimane"] / 52)
        eq = cp[1:]
        dd_g = float((eq / np.maximum.accumulate(np.concatenate([[1.0], eq]))[1:] - 1).min())
        per_anno = {int(a): float(np.prod(1 + rg[anno == a]) - 1) for a in sorted(set(anno))}
        anni = nd / 365.25
        tot = float(cp[-1] - 1)
        return {"rendimento_composto": tot, "annuo_composto": float((cp[-1]) ** (1 / anni) - 1), "per_anno_composto": per_anno,
                "settimanale_da_equity": z, "settimanale_sommato": zs, "discesa_fine_giorno": dd_g,
                "giorno_peggiore": float(rg.min()), "giorno_peggiore_data": sc.data(int(giorni[int(rg.argmin())])),
                "discesa_dentro_giorno_chiusure": s["dd_ora_chiusure"], "discesa_dentro_giorno_caso_peggiore": s["dd_ora_peggiore"],
                "spese_annue_punti": float(s["spese"].mean() * 365), "funding_annuo_punti": float(s["funding"].mean() * 365),
                "stop_scatti": len(s["eventi"]), "stop_eventi": s["eventi"], "giorni_fuori": int(len(s["fuori"])),
                "liquidazioni_1pc": len(s["liq1"]), "liquidazioni_2_5pc": len(s["liq25"]),
                "liquidazioni_1pc_elenco": s["liq1"][:20], "equity_finale": float(cp[-1])}, ws

    ris, sett = {}, {}
    for nome, m in M.items():
        tv = time.time()
        s = simula(nome, m, True)
        ris[nome], sett[nome] = metriche(s, nome)
        ris[nome]["senza_stop"] = None
        s0 = simula(nome, m, False)
        ris[nome]["senza_stop"], _ = metriche(s0, nome)
        # sensibilita' dello stop
        ris[nome]["sensibilita"] = {}
        for att in ("1", "28", "mai"):
            sa = simula(nome, m, True, att)
            mm, _ = metriche(sa, nome)
            ris[nome]["sensibilita"][att] = {k: mm[k] for k in ("rendimento_composto", "per_anno_composto", "discesa_fine_giorno", "stop_scatti", "giorni_fuori")}
        # rendimento perso nelle giornate fuori (di G1 senza stop)
        fu = s["fuori"]
        ris[nome]["rendimento_perso_giorni_fuori_senza_stop"] = float(senza[nome]["netto"].to_numpy()[fu].sum()) if len(fu) else 0.0
        ris[nome]["ordini"] = senza[nome].attrs["ordini"]
        pd.DataFrame({"giorno": giorni, "capitale_inizio_giorno": s["capitale"][:-1], "rendimento": s["rit"], "spese": s["spese"],
                      "funding": s["funding"]}).to_csv(RIS / f"giorni_{nome}_con_stop.csv.gz", index=False)
        sett[nome].rename("netto").to_csv(RIS / f"settimane_{nome if nome != 'G1' else 'G1'}.csv.gz")
        print(f"[{nome}] {time.time() - tv:.0f}s stop {ris[nome]['stop_scatti']} liq {ris[nome]['liquidazioni_1pc']}", flush=True)

    # ---------------- 4. Sharpe corretto con le famiglie ----------------
    def cand(nome):
        z = ris[nome]["settimanale_da_equity"]
        return {k: z[k] for k in ("sharpe", "settimane", "asimmetria", "curtosi")}
    corr = {}
    cf = ast.corretto_famiglie({"158 A": sett["A"], "158 B": sett["B"]}, {"158 A": cand("A"), "158 B": cand("B")})
    corr["A_B"] = {k: cf[k] for k in ("serie", "senza_serie", "famiglie", "in_v", "deviazione_v", "taglio")} | {n: v for n, v in cf["candidate"].items()}
    for tg in ast.ALTRI_TAGLI:
        c2 = ast.corretto_famiglie({"158 A": sett["A"], "158 B": sett["B"]}, {"158 A": cand("A"), "158 B": cand("B")}, taglio=tg)
        corr[f"taglio_{tg}"] = {"famiglie": c2["famiglie"], **{k: c2["candidate"][k]["corretto"] for k in c2["candidate"]}}
    c1 = ast.corretto_famiglie({"158 G1": sett["G1"]}, {"158 G1": cand("G1")})
    corr["G1"] = {k: c1[k] for k in ("famiglie", "in_v")} | {"158 G1": c1["candidate"]["158 G1"]}
    print(f"[corretto] {time.time() - t0:.0f}s", flush=True)

    # ---------------- 5. controlli descrittivi ----------------
    desc = {}
    for nome, m in M.items():
        d = senza[nome]
        netto = d["netto"].to_numpy()
        peggiori = np.argsort(netto)[:10]
        elenco = []
        for k in peggiori:
            contr = W[k] * m * R0[k]
            j = int(np.argmin(contr))
            elenco.append({"giorno": sc.data(int(giorni[k])), "netto": float(netto[k]), "moneta": simboli[j], "contributo": float(contr[j])})
        short30 = [(k, float(-(np.minimum(W[k], 0)).sum() * m)) for k in range(nd) if ((W[k] < 0) & (R0[k] > 0.30)).any()]
        desc[nome] = {"giorno_peggiore_senza_stop": float(netto.min()), "10_peggiori": elenco,
                      "quota_giorni_perdita_oltre_10pc": float((netto < -0.10).mean()),
                      "peso_massimo_moneta": float(np.abs(W).max() * m), "giorni_peso_moneta_oltre_60pc": int((np.abs(W) * m > 0.60).any(axis=1).sum()),
                      "giorni_con_venduta_oltre_+30pc": len(short30),
                      "peso_lato_venduto_in_quei_giorni_medio": float(np.mean([x[1] for x in short30])) if short30 else 0.0,
                      "correlazione_giornaliera_con_G1": float(np.corrcoef(netto, g1["netto"].to_numpy())[0, 1])}
    desc["liquidazione_per_moneta"] = {"monete_giorno": len(liq_moneta), "monete": sorted({x[1] for x in liq_moneta}),
                                       "elenco": liq_moneta[:40], "peso_medio_G1": float(np.mean([abs(x[3]) for x in liq_moneta])) if liq_moneta else 0.0,
                                       "formula": "venduta se massimo/00:00 >= 1,2/1,01; comprata se minimo/00:00 <= 0,8/0,99; ore con candele; giorni senza candele: solo chiusura"}
    desc["candele_a_1_ora"] = sg

    # ---------------- 6. esame ----------------
    esito = {}
    for nome in ("A", "B", "G1"):
        r = ris[nome]
        cc = corr["A_B"][f"158 {nome}"] if nome != "G1" else corr["G1"]["158 G1"]
        e1 = {"netto_positivo": r["rendimento_composto"] > 0, "ogni_anno_positivo": all(v > 0 for v in r["per_anno_composto"].values()),
              "t_almeno_3": r["settimanale_da_equity"]["t"] >= 3, "sharpe_corretto_almeno_0.80": cc["corretto"] >= 0.80}
        e2 = {"nessuna_liquidazione_con_stop": r["liquidazioni_1pc"] == 0, "stop_al_massimo_2": r["stop_scatti"] <= N_STOP}
        r["esame_1"], r["criteri_conto_vero"] = e1, e2
        r["sharpe_corretto"] = cc
        r["rende_piu_di_G1_con_stop"] = r["rendimento_composto"] > ris["G1"]["rendimento_composto"]
        esito[nome] = "promettente" if (all(e1.values()) and all(e2.values())) else ("esame superato ma non adatta al conto vero" if all(e1.values()) else "non promettente")
        misure = {k: r[k] for k in ("rendimento_composto", "per_anno_composto", "discesa_fine_giorno", "discesa_dentro_giorno_caso_peggiore",
                                    "stop_scatti", "liquidazioni_1pc", "liquidazioni_2_5pc", "giorni_fuori", "esame_1", "criteri_conto_vero")}
        misure["sharpe_corretto"] = cc["corretto"]
        misure["t"] = r["settimanale_da_equity"]["t"]
        prove.registra("novantaseiesima", {"G1": "G1_con_stop_riferimento", "A": "A", "B": "B"}[nome],
                       {"m": M[nome], "esposizione_lorda": 2 * M[nome], "stop": 0.35, "pavimento": 0.65, "ripartenza": "primo lunedi' >= stop + 3 giorni",
                        "margine": MARGINE, "periodo": "2021-01-04..2026-10-04"}, "giornaliera con candele a 1 ora", nd, misure, esito[nome],
                       note="riferimento, non variante" if nome == "G1" else "", seme=SEME, commit=cm)
    out = {"commit": cm, "parita": par, "risultati": ris, "sharpe_corretto_famiglie": corr, "descrittivi": desc, "esito": esito}
    (RIS / "esame.json").write_text(json.dumps(out, indent=1, default=str))
    for nome in ("G1", "A", "B"):
        r = ris[nome]
        print(nome, esito[nome], f"comp {r['rendimento_composto']:+.2f} disc {r['discesa_fine_giorno']:.3f}/{r['discesa_dentro_giorno_caso_peggiore']:.3f} "
              f"sharpe {r['settimanale_da_equity']['sharpe']:.2f} t {r['settimanale_da_equity']['t']:.2f} corr {r['sharpe_corretto']['corretto']:.2f} "
              f"stop {r['stop_scatti']} liq {r['liquidazioni_1pc']}/{r['senza_stop']['liquidazioni_1pc']}", flush=True)
    print(f"FINITA {time.time() - t0:.0f}s", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
