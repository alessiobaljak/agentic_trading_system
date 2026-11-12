"""Audit del mazzo dello Sharpe corretto per famiglie (12 nov 2026, commit 78235da).

Uso (dalla radice): PYTHONPATH=. python3 audits/repro/mazzo_2026-11-12.py <parte> [cartella_cache]
Parti:
  cache      costruisce le serie (le_prove, serie_nuove di oggi e del commit 366d72c) e le salva in un pickle nella cartella data
  numeri     rifa' i numeri della tabella di MAZZO_ASTICELLA.md con una DSR scritta qui da capo (Bailey e Lopez de Prado 2014)
  copertura  confronta il mazzo con il conto del registro, prova per prova (49-152)
  allinea    settimane al lunedi', ritardi di una settimana fra serie gemelle, doppioni, periodo
  eventi     controlli sulle prove a eventi aggiunte (righe perse, durate, colonna r)
  fino57     G1 con il mazzo fermo alla prova 57 (domanda di metodo)
  sensi      sensibilita': conferme fuori, escluse dentro come «soli», 151 dentro, taglio 0,3/0,7
Non scrive fuori da audits/ (gli esiti in audits/repro/mazzo_2026-11-12_esito_<parte>.json; la cache nella cartella data).
"""
from __future__ import annotations

import importlib.util
import json
import math
import pickle
import re
import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

RADICE = Path(__file__).resolve().parents[2]
QUI = Path(__file__).parent
sys.path.insert(0, str(RADICE))
from research.programma6 import asticella as ast  # noqa: E402
from research.programma6 import seconda as sc  # noqa: E402

CACHE = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("/tmp")
K = ("sharpe", "settimane", "asimmetria", "curtosi")


def salva(parte, out):
    (QUI / f"mazzo_2026-11-12_esito_{parte}.json").write_text(json.dumps(out, ensure_ascii=False, indent=1, default=float),
                                                              encoding="utf-8")


def asticella_del_commit(commit: str, cartella: Path):
    testo = subprocess.run(["git", "show", f"{commit}:research/programma6/asticella.py"], cwd=RADICE, check=True,
                           capture_output=True, text=True).stdout
    f = cartella / f"asticella_{commit}.py"
    f.write_text(testo, encoding="utf-8")
    spec = importlib.util.spec_from_file_location(f"asticella_{commit}", f)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    m.QUI = Path(ast.__file__).parent
    return m


def parte_cache():
    prove = ast.le_prove()
    nuove = ast.serie_nuove()
    vecchie = asticella_del_commit("366d72c", CACHE).serie_nuove()
    with open(CACHE / "mazzo.pkl", "wb") as f:
        pickle.dump({"prove": prove, "nuove": nuove, "vecchie": vecchie}, f)
    print(len(prove), len(nuove), len(vecchie))


def carica():
    with open(CACHE / "mazzo.pkl", "rb") as f:
        return pickle.load(f)


# --- la DSR scritta da capo (Bailey e Lopez de Prado 2014, eq. della «Deflated Sharpe Ratio»), per controllare te.sharpe_corretto
def dsr(sr_annuo, n, g3, g4, sr_v_annui, N, periodi=52):
    sr = sr_annuo / math.sqrt(periodi)
    v = np.var(np.asarray(sr_v_annui, float) / math.sqrt(periodi), ddof=1)
    em = 0.5772156649015329
    sr0 = math.sqrt(v) * ((1 - em) * stats.norm.ppf(1 - 1.0 / N) + em * stats.norm.ppf(1 - 1.0 / (N * math.e)))
    return float(stats.norm.cdf((sr - sr0) * math.sqrt(n - 1) / math.sqrt(1 - g3 * sr + (g4 - 1) / 4 * sr ** 2)))


def candidate() -> dict:
    au, p7 = RADICE / "audits" / "repro", RADICE / "research" / "programma7"
    mis = json.loads((au / "g1_parte2_2026-11-12_esito_misure.json").read_text())["misure"]
    p28 = json.loads((au / "prova28_2026-11-11_esito.json").read_text())["misure"]
    b55 = json.loads((au / "prova55_2026-11-12_esito_base.json").read_text())
    b55 = b55.get("base", b55)["misure_C3_corretta_dichiarato"]
    r152 = json.loads((p7 / "risultati_novantesima" / "risultati.json").read_text())["varianti"]
    out = {"G1": [mis["G1"][x] for x in K], "G1 a 280 USDT (A)": [mis["A280"][x] for x in K],
           "F5 + M7 + K2 al 12 ottobre": [p28["fino_al_2026-10-12"]["F5 + M7 + K2"][x] for x in K],
           "F5 + M7 + K2 al 19 ottobre": [p28["fino_al_2026-10-19_funding_vero"]["F5 + M7 + K2"][x] for x in K],
           "C3 corretta al 5 ottobre": [b55[x] for x in K]}
    out.update({f"152 {v}": [r152[v]["conto1"]["numeri_settimana_corretto"][x] for x in K] for v in ("V1", "V2", "V3")})
    return out


def famiglie(prove, nuove, taglio=ast.TAGLIO, soli_in_piu=()):
    serie = {n: ast.periodo(s) for n, s, _ in prove if s is not None}
    serie.update({n: ast.periodo(s) for n, s in nuove.items()})
    soli = [x for _, s, x in prove if s is None] + list(soli_in_piu)
    gr = ast.gruppi(serie, taglio)
    return serie, gr, ast.per_v(gr, soli, False), ast.per_v(gr, soli, True)


def corretti(prove, nuove, cand, taglio=ast.TAGLIO, soli_in_piu=(), N_in_piu=0):
    serie, gr, sr_g, sr_v = famiglie(prove, nuove, taglio, soli_in_piu)
    N = len(sr_g) + N_in_piu
    return {"serie": len(serie), "famiglie": N, "in_V": len(sr_v), "dev_V": round(float(np.std(sr_v, ddof=1)), 4),
            "corretto": {n: round(dsr(*a, sr_v, N), 4) for n, a in cand.items()},
            "_gr": gr}


def parte_numeri():
    from research.programma6 import terza as te
    m = carica()
    cand = candidate()
    out = {"candidate": cand}
    for nome, mazzo in (("prima", m["vecchie"]), ("dopo", m["nuove"])):
        r = corretti(m["prove"], mazzo, cand)
        # stesso numero con la funzione del repository (te.sharpe_corretto) per vedere che la formula coincide
        _, gr, sr_g, sr_v = famiglie(m["prove"], mazzo)
        r["repo"] = {n: round(te.sharpe_corretto(*a, sr_v, 52, n_prove=len(sr_g)), 4) for n, a in cand.items()}
        r["gruppo_di_G1"] = next(g["membri"] for g in r.pop("_gr") if "57 G1" in g["membri"])
        out[nome] = r
        print(nome, r["serie"], r["famiglie"], r["in_V"], r["dev_V"], r["corretto"])
    s152 = pd.read_csv(RADICE / "research/programma7/risultati_novantesima/settimane_conto1.csv.gz", index_col=0)
    r = corretti(m["prove"], {**m["vecchie"], **{f"152 {v}": s152[v] for v in ("V1", "V2", "V3")}}, cand)
    r.pop("_gr")
    out["prima_con_152"] = r
    print("prima con la 152", r["serie"], r["famiglie"], r["corretto"])
    # la 152 come l'ha calcolata la prova (novantesima.py: corretto_rivisto con le sole tre serie, V di tutti i gruppi)
    cr = ast.corretto_rivisto({f"152 {v}": s152[v] for v in ("V1", "V2", "V3")},
                              {f"152 {v}": dict(zip(K, cand[f"152 {v}"])) for v in ("V1", "V2", "V3")})
    out["152_come_nella_prova"] = {"gruppi": cr["gruppi"], **{n: round(c["corretto"], 4) for n, c in cr["candidate"].items()}}
    print("152 come nella prova", out["152_come_nella_prova"])
    pubblicato = json.loads((RADICE / "research/programma6/risultati_asticella/mazzo_12_novembre.json").read_text())
    out["pubblicato"] = {k: {"serie": v["serie"], "famiglie": v["famiglie"], "in_V": v["in_V"], "corretto": v["corretto"]}
                         for k, v in pubblicato["scenari"].items() if k in ("prima", "dopo", "prima, con le tre serie della 152")}
    out["pubblicato_152"] = pubblicato["152_come_nella_prova"]
    salva("numeri", out)


# --- copertura: il registro prova per prova
def conto_registro() -> dict:
    """Le varianti che il registro conta, prova per prova, ricavate dalla colonna «Varianti nel conto» e dalla somma della riga
    «Totale nel conto» (le conferme non contano, «1 a eventi + 1 portafoglio» conta 1: e' l'unico allineamento con la somma)."""
    from research.src.registro import leggi
    d = leggi()["prove"]
    out = {}
    for n in sorted(d):
        if n < 49 or n > 152:
            continue
        c = re.sub(r"\s+", " ", d[n][1])
        if c.startswith("conferma") or c == "—" or "di conferma" in c:
            out[n] = 0
        else:
            out[n] = int(re.findall(r"\d+", c)[0])
    return out


def parte_copertura():
    m = carica()
    reg = conto_registro()
    per_prova = {}
    for nome in m["nuove"]:
        per_prova.setdefault(int(nome.split()[0]), []).append(nome)
    righe, diff = [], {}
    for n in range(49, 153):
        r, k = reg.get(n), len(per_prova.get(n, []))
        if r != k:
            diff[n] = {"registro": r, "mazzo": k, "nel_mazzo": per_prova.get(n, [])}
    out = {"conto_registro_49_152": sum(v for v in reg.values() if v), "serie_mazzo_49_152": sum(len(v) for v in per_prova.values()),
           "differenze": diff, "prove_nel_registro_49_152": len(reg)}
    # doppioni esatti o quasi nel mazzo intero
    tutte = {n: ast.periodo(s) for n, s, _ in m["prove"] if s is not None}
    tutte.update({n: ast.periodo(s) for n, s in m["nuove"].items()})
    nomi = list(tutte)
    gemelle = []
    for i in range(len(nomi)):
        for j in range(i + 1, len(nomi)):
            a, b = tutte[nomi[i]], tutte[nomi[j]]
            c = a.index.intersection(b.index)
            if len(c) < 8:
                continue
            x, y = a.loc[c], b.loc[c]
            if np.allclose(x.to_numpy(), y.to_numpy(), atol=1e-12) and (x.abs() > 0).sum() > 0:
                gemelle.append([nomi[i], nomi[j], "identiche", int(len(c))])
            elif x.std() > 0 and y.std() > 0:
                rho = float(np.corrcoef(x, y)[0, 1])
                if rho > 0.98:
                    gemelle.append([nomi[i], nomi[j], round(rho, 4), int(len(c))])
    out["gemelle"] = gemelle
    print(json.dumps({k: v for k, v in out.items() if k != "gemelle"}, ensure_ascii=False, default=str)[:3000])
    print("gemelle:", gemelle[:40])
    salva("copertura", out)


def parte_allinea():
    m = carica()
    tutte = {n: s for n, s, _ in m["prove"] if s is not None}
    tutte.update(m["nuove"])
    out = {"non_lunedi": {}, "fuori_periodo": {}, "ritardo": []}
    for n, s in tutte.items():
        ix = np.asarray(s.index, dtype=np.int64)
        bad = ix[(ix % 7) != 4]
        if len(bad):
            out["non_lunedi"][n] = [sc.data(int(x)) for x in bad]
        p = ast.periodo(s)
        out["fuori_periodo"][n] = [sc.data(int(p.index.min())), sc.data(int(p.index.max())), int(len(p))] if len(p) else None
    # ritardo: per ogni serie aggiunta, la correlazione piu' alta con le altre a 0 e a +-1 settimana
    P = {n: ast.periodo(s) for n, s in tutte.items()}
    aggiunte = [n for n in m["nuove"] if n not in m["vecchie"]]
    for n in aggiunte:
        a = P[n]
        best = None
        for o, b in P.items():
            if o == n:
                continue
            r = {}
            for lag in (-1, 0, 1):
                bb = b.copy()
                bb.index = bb.index + 7 * lag
                c = a.index.intersection(bb.index)
                x, y = a.loc[c], bb.loc[c]
                ok = (x.abs() > 0) | (y.abs() > 0)
                r[lag] = float(np.corrcoef(x[ok], y[ok])[0, 1]) if ok.sum() >= 52 and x[ok].std() > 0 and y[ok].std() > 0 else 0.0
            if best is None or max(abs(r[-1]), abs(r[1])) > max(abs(best[1][-1]), abs(best[1][1])):
                best = (o, r)
            if max(abs(r[-1]), abs(r[1])) > 0.3 and max(abs(r[-1]), abs(r[1])) > abs(r[0]):
                out["ritardo"].append([n, o, {k: round(v, 3) for k, v in r.items()}])
    # G1 e le sue gemelle: 148 B, 152 V1-V3, 124 G1M, 142 G1S, 61 G1T, 88 G1 120/80
    g = P["57 G1"]
    out["gemelle_di_G1"] = {}
    for o in ("148 B", "152 V1", "152 V2", "152 V3", "124 G1M", "142 G1S", "61 G1T", "88 G1 120/80", "93 G1-S", "92 G1 clima", "69 G11"):
        if o not in P:
            continue
        r = {}
        for lag in (-1, 0, 1):
            bb = P[o].copy()
            bb.index = bb.index + 7 * lag
            c = g.index.intersection(bb.index)
            r[lag] = round(float(np.corrcoef(g.loc[c], bb.loc[c])[0, 1]), 4)
        out["gemelle_di_G1"][o] = r
    print(json.dumps(out["non_lunedi"]), "\n", out["ritardo"][:30], "\n", out["gemelle_di_G1"])
    salva("allinea", out)



def parte_eventi():
    """Le prove a eventi aggiunte: quante operazioni entrano, media di r, durate mancanti o negative, uscite fuori dalle settimane
    del portafoglio della 41, operazioni saltate dal tetto di 20 aperte."""
    from research.programma6 import quarantunesima as qu
    registrati = []
    vero = qu.portafoglio

    def spia(ev):
        registrati.append(ev.copy())
        return vero(ev)

    qu.portafoglio = spia
    try:
        out_s = ast._eventi_mancanti(Path(ast.__file__).parent.parent / "programma7")
    finally:
        qu.portafoglio = vero
    out = {}
    lo, hi = qu.PRIMO_LUNEDI, qu.A + 14
    for nome, ev in zip(out_s, registrati):
        d = ev.sort_values(["ora", "simbolo"]).reset_index(drop=True)
        aperte, tenute = [], []
        for k, x in d.iterrows():
            aperte = [u for u in aperte if u > x["ora"]]
            if len(aperte) >= qu.MAX_APERTE:
                continue
            aperte.append(x["uscita_h"])
            tenute.append(k)
        t = d.loc[tenute]
        lun = ((t["uscita_h"].to_numpy() // 24 + 3) // 7) * 7 - 3
        fuori = int(((lun < lo) | (lun >= hi)).sum())
        durata = (d["uscita_h"] - d["ora"]).to_numpy()
        out[nome] = {"operazioni": int(len(d)), "media_r": round(float(d["r"].mean()), 5),
                     "durata_ore_mediana": float(np.median(durata)), "durate_negative_o_nulle": int((durata <= 0).sum()),
                     "durate_assurde": int((np.abs(durata) > 24 * 400).sum()),
                     "saltate_dal_tetto": int(len(d) - len(tenute)), "uscite_fuori_settimane": fuori,
                     "prima": sc.data(int(d["ora"].min() // 24)), "ultima": sc.data(int(d["ora"].max() // 24))}
        print(nome, out[nome])
    salva("eventi", out)



def p9c_filtrate() -> dict:
    """Le prove 81 e 82 come le hanno calcolate le loro regole: solo le fiammate con il funding dell'ultimo regolamento almeno
    +0,01% per 8 ore (`programma9/seconda.py:24,93-94`, `programma9/terza.py:31-32`), con lo stesso trattamento del mazzo."""
    from research.programma6 import quarantunesima as qu
    p9 = Path(ast.__file__).parent.parent / "programma9"
    out = {}
    for n, f in (("81 P9C", "risultati_seconda/eventi_P9C.csv"), ("82 P9C lunga", "risultati_terza/eventi_P9C_lunga.csv")):
        d = pd.read_csv(p9 / f)
        d = d[d["funding_8h"].notna() & (d["funding_8h"] >= 0.0001)].reset_index(drop=True)
        ev = pd.DataFrame({"simbolo": d["simbolo"].to_numpy(), "ora": d["entrata_min"].to_numpy() // 60,
                           "uscita_h": -(-d["uscita_min"].to_numpy() // 60), "r": d["r"].to_numpy()})
        out[n] = qu.portafoglio(ev[np.isfinite(ev["r"])])["netto"]
        out[n + " (righe)"] = len(d)
    return out


def serie_151() -> pd.Series:
    d = pd.read_csv(Path(ast.__file__).parent.parent / "programma7/risultati_ottantanovesima/settimane.csv", index_col=0)
    d = d[d["fatta"].astype(bool)]
    return pd.Series(d["netto"].to_numpy(), index=[sc.giorno(*map(int, x.split("-"))) for x in d.index])


def parte_sensi():
    m = carica()
    cand = {k: v for k, v in candidate().items() if k in ("G1", "G1 a 280 USDT (A)", "F5 + M7 + K2 al 12 ottobre",
                                                          "C3 corretta al 5 ottobre", "152 V1")}
    p9c = p9c_filtrate()
    cc = json.loads((Path(ast.__file__).parent.parent / "programma7/risultati_quarantottesima/esame.json").read_text())
    sr_cc = cc["CC_opzioni"]["sharpe"]
    A = dict(m["nuove"])
    B = {**A, "81 P9C": p9c["81 P9C"], "82 P9C lunga": p9c["82 P9C lunga"]}
    C = {n: s for n, s in B.items() if not n.startswith(("50 ", "106 "))}
    D = {**C, "151 WE": serie_151()}
    scen = {"A pubblicato": (A, (), 0), "B 81 e 82 filtrate": (B, (), 0), "C B senza le conferme 50 e 106": (C, (), 0),
            "D C con la 151": (D, (), 0), "E D con CC sola": (D, (sr_cc,), 0),
            "F E con 108 e 111 come 2 famiglie fuori da V": (D, (sr_cc, -10.0, -10.0), 0),
            "G E con 108 e 111 come 26 famiglie fuori da V": (D, (sr_cc,) + (-10.0,) * 26, 0)}
    out = {"righe_81_82_filtrate": [p9c["81 P9C (righe)"], p9c["82 P9C lunga (righe)"]], "sharpe_CC_opzioni": sr_cc, "scenari": {}}
    for nome, (mz, soli, k) in scen.items():
        r = corretti(m["prove"], mz, cand, soli_in_piu=soli, N_in_piu=k)
        r.pop("_gr")
        out["scenari"][nome] = r
        print(nome, r["serie"], r["famiglie"], r["in_V"], r["dev_V"], r["corretto"])
    for tg in ast.ALTRI_TAGLI:
        r = corretti(m["prove"], A, cand, taglio=tg)
        r.pop("_gr")
        out["scenari"][f"A con taglio {tg}"] = r
        print("taglio", tg, r["famiglie"], r["in_V"], r["corretto"])
    salva("sensi", out)


def parte_fino57():
    """Domanda di metodo: G1 con il mazzo fermo alla prova 57 (le prove 1-57), e con le prove dopo la 57 che stanno nella famiglia
    di G1 (le varianti di G1 provate dopo: la scelta di tenere G1 e' anche una scelta fra quelle)."""
    m = carica()
    cand = {k: v for k, v in candidate().items() if k in ("G1", "G1 a 280 USDT (A)")}
    fino57 = {n: s for n, s in m["nuove"].items() if int(n.split()[0]) <= 57}
    fino57_senza50 = {n: s for n, s in fino57.items() if not n.startswith("50 ")}
    _, gr, _, _ = famiglie(m["prove"], m["nuove"])
    fam_g1 = next(g["membri"] for g in gr if "57 G1" in g["membri"])
    dopo_in_famiglia = [n for n in fam_g1 if n.split()[0].isdigit() and int(n.split()[0]) > 57]
    piu_famiglia = {**fino57, **{n: m["nuove"][n] for n in dopo_in_famiglia}}
    fino56 = {n: s for n, s in m["nuove"].items() if int(n.split()[0]) <= 56}
    out = {"famiglia_di_G1_dopo_la_57": dopo_in_famiglia, "scenari": {}}
    for nome, mz in (("prove 1-57", fino57), ("prove 1-57 senza la conferma 50", fino57_senza50),
                     ("prove 1-56 (senza G1 nel mazzo)", fino56),
                     ("prove 1-57 piu' le varianti di G1 provate dopo", piu_famiglia),
                     ("prove 1-148 (prima della scelta del demo dell 8 novembre)",
                      {n: s for n, s in m["nuove"].items() if int(n.split()[0]) <= 148}),
                     ("tutte (mazzo del 12 novembre)", m["nuove"])):
        r = corretti(m["prove"], mz, cand)
        r.pop("_gr")
        out["scenari"][nome] = r
        print(nome, r["serie"], r["famiglie"], r["in_V"], r["dev_V"], r["corretto"])
    salva("fino57", out)



def parte_sensi2():
    """Le correzioni senza la 151 (motivo dell'esclusione discutibile ma dichiarato) e la 108 e la 111 contate come la prova 1 (una
    famiglia per indicatore: 9 + 4) o come la 1 e la 2B nel conto (una per variante contata: 18 + 8)."""
    m = carica()
    cand = {k: v for k, v in candidate().items() if k in ("G1", "G1 a 280 USDT (A)", "F5 + M7 + K2 al 12 ottobre",
                                                          "F5 + M7 + K2 al 19 ottobre", "C3 corretta al 5 ottobre", "152 V1")}
    p9c = p9c_filtrate()
    sr_cc = json.loads((Path(ast.__file__).parent.parent / "programma7/risultati_quarantottesima/esame.json").read_text())["CC_opzioni"]["sharpe"]
    C = {n: s for n, s in {**m["nuove"], "81 P9C": p9c["81 P9C"], "82 P9C lunga": p9c["82 P9C lunga"]}.items()
         if not n.startswith(("50 ", "106 "))}
    out = {"sharpe_nel_periodo": {n: round(ast.sharpe(ast.periodo(s)), 3) for n, s in (("151 WE", serie_151()),
                                                                                       ("147 GA2C", m["nuove"]["147 GA2C"]))},
           "settimane_nel_periodo": {"151 WE": int(len(ast.periodo(serie_151()))), "147 GA2C": int(len(ast.periodo(m["nuove"]["147 GA2C"])))},
           "scenari": {}}
    for nome, soli in (("errori corretti, CC sola, 108 e 111 come 13 famiglie (come la prova 1)", (sr_cc,) + (-10.0,) * 13),
                       ("errori corretti, CC sola, 108 e 111 come 26 famiglie (una per variante contata, come 1 e 2B)",
                        (sr_cc,) + (-10.0,) * 26)):
        r = corretti(m["prove"], C, cand, soli_in_piu=soli)
        r.pop("_gr")
        out["scenari"][nome] = r
        print(nome, r["famiglie"], r["in_V"], r["dev_V"], r["corretto"])
    print(out["sharpe_nel_periodo"], out["settimane_nel_periodo"])
    salva("sensi2", out)



def parte_regola_scritta():
    """ASTICELLA.md:31-32 (le prove senza serie contano ognuna come un gruppo a se'): 108 (18) e 111 (8) fuori da V (t molto sotto
    -3: -0,11% a operazione con p 1,00), CC della 110 con il suo Sharpe; da sola e con le altre correzioni (81-82 filtrate, 50 e 106 fuori)."""
    m = carica()
    cand = candidate()
    cc = json.loads((Path(ast.__file__).parent.parent / "programma7/risultati_quarantottesima/esame.json").read_text())["CC_opzioni"]["sharpe"]
    soli = (cc,) + (-10.0,) * 26
    p9c = p9c_filtrate()
    C = {n: s for n, s in {**m["nuove"], "81 P9C": p9c["81 P9C"], "82 P9C lunga": p9c["82 P9C lunga"]}.items()
         if not n.startswith(("50 ", "106 "))}
    out = {}
    for nome, mz in (("solo_regola_scritta", m["nuove"]), ("tutte_le_correzioni_senza_151", C)):
        r = corretti(m["prove"], mz, cand, soli_in_piu=soli)
        r.pop("_gr")
        out[nome] = r
        print(nome, r["famiglie"], r["in_V"], r["corretto"])
    salva("regola_scritta", out)


def parte_varianti_g1():
    """Le varianti d'ordine della revisione di G1 (g1_corretto_varianti_2026-11-12_esito.json) con il mazzo nuovo: stima con
    l'asimmetria e la curtosi del caso base (rifatta sul mazzo di prima ridà i numeri della revisione entro 0,002)."""
    m = carica()
    v = json.loads((QUI / "g1_corretto_varianti_2026-11-12_esito.json").read_text())
    mis = json.loads((QUI / "g1_parte2_2026-11-12_esito_misure.json").read_text())["misure"]
    mom = {"G1": (mis["G1"]["asimmetria"], mis["G1"]["curtosi"]), "A280": (mis["A280"]["asimmetria"], mis["A280"]["curtosi"])}
    out = {}
    for nome, mz in (("prima", m["vecchie"]), ("dopo", m["nuove"])):
        _, gr, sg, sv = famiglie(m["prove"], mz)
        for k, x in v.items():
            a, c = mom["G1" if k.startswith("G1") else "A280"]
            out.setdefault(k, {})[nome] = round(dsr(x["sharpe"], 300, a, c, sv, len(sg)), 4)
    for k in out:
        out[k]["registrato_prima"] = round(v[k]["N_gruppi"], 4)
        print(k, out[k])
    salva("varianti_g1", out)



def parte_sharpe_registro():
    """Lo Sharpe di ogni serie aggiunta (dalla prima settimana operata) accanto ai numeri «Sharpe ...» della sua riga del registro."""
    from research.src.registro import leggi
    m = carica()
    reg = leggi()["prove"]
    out = {}
    for n in [n for n in m["nuove"] if n not in m["vecchie"] and not n.startswith("149 ")]:
        s, k = m["nuove"][n].dropna(), int(n.split()[0])
        s = s[s.index >= s[s != 0].index.min()] if (s != 0).any() else s
        testo = re.sub(r"\s+", " ", reg[k][2]) if k in reg else ""
        out[n] = {"file": round(ast.sharpe(s), 2), "registro": re.findall(r"Sharpe[^0-9−\-]{0,25}([−\-]?\d+,\d+)", testo)[:4]}
        print(n, out[n])
    salva("sharpe_registro", out)


if __name__ == "__main__":
    globals()["parte_" + sys.argv[1]]()
