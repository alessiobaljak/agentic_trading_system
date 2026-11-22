"""Programma 7, prova 168 (CENTOSESTA.md): G1, G11, G1 neutra e F5 insieme sullo stesso conto.
A = quattro conti in uno (media dei quattro netti); B = un portafoglio solo (media dei pesi giornalieri, spese e funding sul peso netto).
Regole scritte prima (CENTOSESTA.md, con la «Chiusura della verifica» che vale su tutto il resto). Nessun seme: tutto deterministico.

Uso: python3 -m research.programma7.centosesta
"""
from __future__ import annotations

import glob
import json
import re
import subprocess
import traceback
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd

from research.programma6 import asticella as ast
from research.programma6 import cinquantaseiesima as cs
from research.programma6 import cinquantunesima as cu
from research.programma6 import ottava as ot
from research.programma6 import seconda as sc
from research.programma6 import sesta as se
from research.programma6 import terza as te
from research.programma6 import ventiquattresima as vq
from research.programma7 import prima as pr
from research.programma7 import tredicesima as t13
from research.programma7 import ventiquattresima as f5n
from research.src.prove import registra

QUI = Path(__file__).parent
P6 = QUI.parent / "programma6"
RIS = QUI / "risultati_centosesta"
RADICE = QUI.parent.parent
ID = "centosesta"
SCALA = "settimanale (somma dei giorni; F5 dal lunedi')"
COL = pr.COLONNE
PARAMETRI = {"periodo": "2021-01-04..2026-10-04 (300 settimane)", "F5": "risultati_controllo_parita (parita' corrette, a mercato)",
             "spese_B": "cs.spese_a_limite sul peso netto", "F5_in_B": "pesi costanti ogni giorno, banda dal 2020"}


def esito_regole(e: dict, corretto: float, t: float) -> str:
    """Le condizioni di CENTOSESTA.md: netto positivo, ogni anno positivo, t da 3, Sharpe corretto da 0,80 (non `te.esito`)."""
    m = []
    if not e["intero"]["annuo"] > 0:
        m.append("netto non positivo")
    neg = [a for a, v in e["per_anno"].items() if not v > 0]
    if neg:
        m.append("anni non positivi " + ",".join(map(str, neg)))
    if not t >= 3:
        m.append(f"t {t:.2f} sotto 3")
    if not corretto >= 0.80:
        m.append(f"Sharpe corretto {corretto:.2f} sotto 0,80")
    return "PROMETTENTE" if not m else "NON PROMETTENTE: " + "; ".join(m)


def conto_giorni(Wx, R, F, giorni, simboli, costo):
    """Conto dei giorni come G1 (te.conto + spese a limite del motore di G1): (giorni, settimane, n_variazioni, n_limite)."""
    g = te.conto(Wx, R, F, costo)
    sp, n_tot, n_lim, _ = cs.spese_a_limite(Wx, R, giorni, simboli, costo)
    g["spese"] = sp
    g["netto"] = g["lordo"] - g["spese"] - g["funding"]
    g["netto_doppio"] = g["lordo"] - 2 * g["spese"] - g["funding"]
    return g, pr.per_settimana(g, giorni), n_tot, n_lim


def buchi_nel_periodo(pan, giorni) -> dict:
    """Giorni senza candela fra la prima e l'ultima di ogni moneta, dentro il periodo (dal pannello ufficiale, che ha gia' i giorni
    riempiti dall'interfaccia pubblica)."""
    C = pan["close"]
    out = {}
    a, b = int(giorni[0] - pan["t0"]), int(giorni[-1] - pan["t0"])
    for j, s in enumerate(pan["simboli"]):
        ok = np.flatnonzero(np.isfinite(C[:, j]))
        if len(ok) == 0:
            continue
        mancanti = [int(i + pan["t0"]) for i in range(max(a, ok[0]), min(b, ok[-1]) + 1) if not np.isfinite(C[i, j])]
        if mancanti:
            out[s] = [sc.data(g) for g in mancanti]
    return {"monete_con_buchi": out, "giorni_senza_nessuna_candela": [sc.data(int(g)) for g in giorni
                                                                     if not np.isfinite(C[int(g - pan["t0"])]).any()]}


def peggiori(x: pd.Series) -> dict:
    i = x.idxmin()
    return {"valore": float(x.min()), "data": sc.data(int(i))}


def avanti(log=print) -> dict:
    """Parte in avanti a tavolino dalle risposte «stato» (grep sulle righe equity; mai gli archivi)."""
    file = sorted(f for f in glob.glob(str(RADICE / "ops" / "results" / "*stato*.md")) if Path(f).is_file())
    r = subprocess.run(["grep", "-H", "-E", r"^_eseguito: |^## Paper (F5|G1 \(|G11|G1N)|^- equity: \*\*\$[0-9,.]+\*\* su", *file],
                       capture_output=True, text=True)
    per_file: dict = {}
    sez = {}
    for riga in r.stdout.splitlines():
        f, _, testo = riga.partition(":")
        d = per_file.setdefault(f, {"ora": None, "eq": {}})
        sez.setdefault(f, None)
        m = re.match(r"_eseguito: (\d{4}-\d\d-\d\d \d\d:\d\d) UTC_", testo)
        if m:
            d["ora"] = datetime.strptime(m.group(1), "%Y-%m-%d %H:%M")
            continue
        m = re.match(r"## Paper (F5|G1 \(|G11|G1N)", testo)
        if m:
            sez[f] = {"F5": "F5", "G1 (": "G1", "G11": "G11", "G1N": "G1N"}[m.group(1)]
            continue
        m = re.match(r"- equity: \*\*\$([0-9,.]+)\*\* su", testo)
        if m and sez[f] and sez[f] not in d["eq"]:
            d["eq"][sez[f]] = float(m.group(1).replace(",", ""))
    quattro = [(d["ora"], d["eq"], Path(f).name) for f, d in per_file.items()
               if d["ora"] and len(d["eq"]) == 4 and d["ora"] >= datetime(2026, 10, 31)]
    scelte = {}
    for ora, eq, nome in quattro:
        g = ora.date()
        dist = abs((ora - datetime(g.year, g.month, g.day, 4, 15)).total_seconds())
        if g not in scelte or dist < scelte[g][0]:
            scelte[g] = (dist, ora, eq, nome)
    giorni = sorted(scelte)
    righe = []
    for a, b in zip(giorni[:-1], giorni[1:]):
        ea, eb = scelte[a][2], scelte[b][2]
        row = {"da": str(a), "a": str(b), "giorni": (b - a).days, "file_da": scelte[a][3], "file_a": scelte[b][3]}
        for n in ("G1", "G11", "G1N", "F5"):
            row[n] = eb[n] / ea[n] - 1
        row["un_quarto"] = float(np.mean([row[n] for n in ("G1", "G11", "G1N", "F5")]))
        righe.append(row)
    d = pd.DataFrame(righe)
    RIS.mkdir(exist_ok=True)
    d.to_csv(RIS / "avanti.csv", index=False)
    out = {"prima_lettura": str(giorni[0]) if giorni else None, "ultima_lettura": str(giorni[-1]) if giorni else None,
           "letture": len(giorni), "intervalli": len(d), "giorni_coperti": int(d["giorni"].sum()) if len(d) else 0}
    if len(d):
        for n in ("G1", "G11", "G1N", "F5", "un_quarto"):
            x = d[n].to_numpy()
            out[n] = {"cumulato": float(np.prod(1 + x) - 1), "peggiore_intervallo": float(x.min()),
                      "media_per_giorno": float(np.prod(1 + x) ** (1 / d["giorni"].sum()) - 1)}
        out["peggiore_intervallo_data"] = {n: d.loc[d[n].idxmin(), ["da", "a"]].tolist() for n in ("G1", "un_quarto")}
        eqc = np.cumprod(1 + d["un_quarto"].to_numpy())
        out["discesa_un_quarto"] = float((eqc / np.maximum.accumulate(eqc) - 1).min())
        eqg = np.cumprod(1 + d["G1"].to_numpy())
        out["discesa_G1"] = float((eqg / np.maximum.accumulate(eqg) - 1).min())
    return out


def esegui(log=print) -> dict:
    RIS.mkdir(exist_ok=True)
    esito_var = {}
    try:
        pan = sc.pannello()
        ps = te.pannello_settimane(pan, log=lambda x: None, indicatori_si=False)
        giorni = np.arange(se.INIZIO, pr.FINE, dtype=np.int64)
        idx = giorni - pan["t0"]
        Ud = pr.universo_del_giorno(giorni, ps["lunedi"], ps["U"])
        sig = ot.sigma_30(pan, idx)
        R = sc.rendimenti(pan)[idx]
        F = np.nan_to_num(pan["funding"][idx])
        costo = sc.costi_moneta(pan["simboli"])
        btc = pd.Series(ps["R"][:, ps["simboli"].index("BTCUSDT")], index=ps["lunedi"])
        buchi = buchi_nel_periodo(pan, giorni)
        log(f"[168] buchi nel periodo: {buchi['monete_con_buchi']} / giorni vuoti {buchi['giorni_senza_nessuna_candela']}")
        # pesi giornalieri delle quattro (passi della verifica)
        W1 = vq.pesi_banda(np.where(np.isfinite(sig), -se.funding_7(pan, idx), np.nan), Ud, sig)
        W11 = vq.pesi_banda(np.where(np.isfinite(sig), t13.segnale_fresco(pan, idx, Ud), np.nan), Ud, sig)
        beta = f5n.beta_delle_monete(pan, Ud, idx)
        WN = f5n.scala_neutra(W1, beta)[0]
        lun = ps["lunedi"] - pan["t0"]
        sg = ot.sigma_30(pan, lun)
        Wt = vq.pesi_banda(np.where(np.isfinite(sg), -se.funding_7(pan, lun), np.nan), ps["U"], sg)     # dal 2020: la banda ha memoria
        W5 = pr.universo_del_giorno(giorni, ps["lunedi"], Wt)
        log("[168] pesi fatti")
        # controllo dei pesi: le serie rifatte contro quelle salvate
        stor = {"G1": pd.read_csv(QUI / "risultati_prima" / "settimane_G1.csv.gz", index_col=0),
                "G11": pd.read_csv(QUI / "risultati_tredicesima" / "settimane_G11.csv.gz", index_col=0),
                "G1N": pd.read_csv(QUI / "risultati_ventiseiesima" / "settimane_G1N.csv.gz", index_col=0),
                "F5": pd.read_csv(P6 / "risultati_controllo_parita" / "settimane_F5.csv.gz", index_col=0)}
        f9 = pd.read_csv(P6 / "risultati_controllo_parita" / "settimane_F9.csv.gz", index_col=0)
        stor = {n: d[(d.index >= se.INIZIO) & (d.index < pr.FINE)] for n, d in stor.items()}
        f9 = f9[(f9.index >= se.INIZIO) & (f9.index < pr.FINE)]
        comuni = stor["G1"].index
        for n, d in stor.items():
            assert d.index.equals(comuni), f"indici diversi: {n}"
        assert len(comuni) == 300 and int(comuni[0]) == se.INIZIO
        giorni_g, sett, ordini, lim = {}, {}, {}, {}
        for n, Wx in (("G1", W1), ("G11", W11), ("G1N", WN)):
            giorni_g[n], sett[n], ordini[n], lim[n] = conto_giorni(Wx, R, F, giorni, pan["simboli"], costo)
        d5 = te.conto(Wt, ps["R"], ps["F"], costo)
        d5.index = ps["lunedi"]
        d5 = d5[(d5.index >= se.INIZIO) & (d5.index < pr.FINE)]
        DW = cu.variazioni(Wt, ps["R"])
        ok5 = (ps["lunedi"] >= se.INIZIO) & (ps["lunedi"] < pr.FINE)
        ordini["F5"] = int((np.abs(DW[ok5]) > 1e-9).sum())
        scarto = {n: float(np.abs(sett[n]["netto"].to_numpy() - stor[n]["netto"].to_numpy()).max()) for n in ("G1", "G11", "G1N")}
        scarto["F5"] = float(np.abs(d5["netto"].to_numpy() - stor["F5"]["netto"].to_numpy()).max())
        log(f"[168] scarto massimo fra le serie rifatte e le salvate (netto settimanale): {scarto}")
    except Exception:  # noqa: BLE001
        err = traceback.format_exc()
        for v in ("A", "B"):
            registra(ID, v, {**PARAMETRI, "variante": v}, SCALA, 0, {}, "ERRORE", note="errore nei preparativi: " + err[-400:], seme=0)
        raise
    out = {"buchi": buchi, "scarto_serie_rifatte": scarto, "ordini": ordini}
    nuove, cand, es = {}, {}, {}
    # --- A: quattro conti in uno
    try:
        quattro = {n: stor[n] for n in ("G1", "G11", "G1N", "F5")}
        A = sum(quattro[n][list(COL)] for n in quattro) / 4
        A["monete"] = sum(quattro[n]["monete"] for n in quattro)
        A.index.name = "settimana"
        A.to_csv(RIS / "settimane_A.csv.gz")
        es["A"] = te.esame(A, btc, inizio=se.INIZIO, anni_pieni=se.ANNI_PIENI)
        nuove["168 A"], cand["168 A"] = A["netto"], es["A"]["intero"]
    except Exception:  # noqa: BLE001
        registra(ID, "A", {**PARAMETRI, "variante": "A"}, SCALA, 0, {}, "ERRORE", note=traceback.format_exc()[-400:], seme=0)
        out["A_errore"] = traceback.format_exc()
    # --- B: un portafoglio solo
    try:
        Wn = (W1 + W11 + WN + W5) / 4
        gB, B, ordB, limB = conto_giorni(Wn, R, F, giorni, pan["simboli"], costo)
        B.to_csv(RIS / "settimane_B.csv.gz")
        gB.assign(giorno=giorni).to_csv(RIS / "giorni_B.csv.gz", index=False)
        es["B"] = te.esame(B, btc, inizio=se.INIZIO, anni_pieni=se.ANNI_PIENI)
        nuove["168 B"], cand["168 B"] = B["netto"], es["B"]["intero"]
        ordini["B"], lim["B"] = ordB, limB
        out["B_lordo_max_medio"] = {"lordo_peso_medio": float(np.abs(Wn).sum(axis=1).mean()), "lordo_peso_massimo": float(np.abs(Wn).sum(axis=1).max())}
    except Exception:  # noqa: BLE001
        registra(ID, "B", {**PARAMETRI, "variante": "B"}, SCALA, 0, {}, "ERRORE", note=traceback.format_exc()[-400:], seme=0)
        out["B_errore"] = traceback.format_exc()
    # --- l'esame, con tutte e due in `nuove`
    if nuove:
        fam = ast.corretto_famiglie(nuove, cand)
        out["famiglie"] = {k: v for k, v in fam.items() if k != "candidate"}
        for v, nome in (("A", "168 A"), ("B", "168 B")):
            if nome not in fam["candidate"]:
                continue
            r = fam["candidate"][nome]
            e = es[v]
            e["sharpe_corretto"], e["t"], e["gruppo"] = r["corretto"], r["t"], r["gruppo"]
            e["esito"] = esito_regole(e, r["corretto"], r["t"])
            i = e["intero"]
            registra(ID, v, {**PARAMETRI, "variante": v}, SCALA, i["settimane"],
                     {"sharpe": round(i["sharpe"], 4), "annuo": round(i["annuo"], 4), "discesa_max": round(i["discesa_max"], 4),
                      "spese_annue": round(e["spese_annue"], 4), "sharpe_corretto": round(r["corretto"], 4), "t": round(r["t"], 3),
                      "ordini": ordini.get(v) if v == "B" else sum(ordini[n] for n in ("G1", "G11", "G1N", "F5"))},
                     e["esito"], note="codice non committato al momento del calcolo; famiglie=" + str(fam["famiglie"]), seme=0)
    out["esame"] = es
    # --- confronto con G1 da sola e le altre
    for n in ("G1", "G11", "G1N", "F5"):
        es[n] = te.esame(stor[n], btc, inizio=se.INIZIO, anni_pieni=se.ANNI_PIENI)
    gg = pd.read_csv(QUI / "risultati_prima" / "giorni_G1.csv.gz")
    out["giorno_peggiore"] = {"G1": peggiori(pd.Series(giorni_g["G1"]["netto"].to_numpy(), index=giorni)),
                              "G1_file_salvato": peggiori(pd.Series(gg["netto"].to_numpy(), index=gg["giorno"]))}
    if "B" in es:
        out["giorno_peggiore"]["B"] = peggiori(pd.Series(gB["netto"].to_numpy(), index=giorni))
    sp = {n: stor[n]["netto"] for n in stor}
    for v in ("A", "B"):
        if v in es:
            sp[v] = (A if v == "A" else B)["netto"]
    out["settimana_peggiore"] = {n: peggiori(s) for n, s in sp.items()}
    out["correlazioni"] = pd.DataFrame(sp).corr().round(3).to_dict()
    out["ordini_totali"] = {**{n: int(v) for n, v in ordini.items()}, "A": int(sum(ordini[n] for n in ("G1", "G11", "G1N", "F5")))}
    # --- controlli descrittivi: F9 e B con la sola F5
    e9 = te.esame(f9, btc, inizio=se.INIZIO, anni_pieni=se.ANNI_PIENI)
    out["F9"] = {"sharpe": e9["intero"]["sharpe"], "annuo": e9["intero"]["annuo"], "discesa_max": e9["intero"]["discesa_max"],
                 "spese_annue": e9["spese_annue"]}
    try:
        _, S5, ord5, _ = conto_giorni(W5, R, F, giorni, pan["simboli"], costo)
        e5b = te.esame(S5, btc, inizio=se.INIZIO, anni_pieni=se.ANNI_PIENI)
        out["B_con_sola_F5"] = {"sharpe": e5b["intero"]["sharpe"], "annuo": e5b["intero"]["annuo"], "discesa_max": e5b["intero"]["discesa_max"],
                                "spese_annue": e5b["spese_annue"], "ordini": ord5,
                                "correlazione_con_F5_settimanale": float(np.corrcoef(S5["netto"], stor["F5"]["netto"])[0, 1]),
                                "scarto_medio_netto_settimanale": float((S5["netto"].to_numpy() - stor["F5"]["netto"].to_numpy()).mean())}
    except Exception:  # noqa: BLE001
        out["B_con_sola_F5_errore"] = traceback.format_exc()
    out["avanti"] = avanti()
    (RIS / "esame.json").write_text(json.dumps(out, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    log("[168] finito")
    return out


def rifatte(log=print) -> dict:
    """Controllo descrittivo, senza registrare: G1, G11 e G1N rifatte con il codice di oggi (come entrano in B) contro le serie salvate
    (che sono del 30 ottobre e usano il pannello di allora). Scrive `risultati_centosesta/rifatte.json`."""
    pan = sc.pannello()
    ps = te.pannello_settimane(pan, log=lambda x: None, indicatori_si=False)
    giorni = np.arange(se.INIZIO, pr.FINE, dtype=np.int64)
    idx = giorni - pan["t0"]
    Ud = pr.universo_del_giorno(giorni, ps["lunedi"], ps["U"])
    sig = ot.sigma_30(pan, idx)
    R, F = sc.rendimenti(pan)[idx], np.nan_to_num(pan["funding"][idx])
    costo = sc.costi_moneta(pan["simboli"])
    btc = pd.Series(ps["R"][:, ps["simboli"].index("BTCUSDT")], index=ps["lunedi"])
    W1 = vq.pesi_banda(np.where(np.isfinite(sig), -se.funding_7(pan, idx), np.nan), Ud, sig)
    out = {}
    for n, Wx in (("G1", W1), ("G11", vq.pesi_banda(np.where(np.isfinite(sig), t13.segnale_fresco(pan, idx, Ud), np.nan), Ud, sig)),
                  ("G1N", f5n.scala_neutra(W1, f5n.beta_delle_monete(pan, Ud, idx))[0])):
        g, s, n_tot, _ = conto_giorni(Wx, R, F, giorni, pan["simboli"], costo)
        e = te.esame(s, btc, inizio=se.INIZIO, anni_pieni=se.ANNI_PIENI)
        out[n] = {**{k: e["intero"][k] for k in ("sharpe", "annuo", "volatilita", "discesa_max")}, "spese_annue": e["spese_annue"],
                  "ordini": n_tot, "per_anno": e["per_anno"], "settimana_peggiore": peggiori(s["netto"]),
                  "giorno_peggiore": peggiori(pd.Series(g["netto"].to_numpy(), index=giorni))}
        if n == "G1":
            out["correlazione_B_G1_rifatta"] = float(np.corrcoef(s["netto"], pd.read_csv(RIS / "settimane_B.csv.gz", index_col=0)["netto"])[0, 1])
    (RIS / "rifatte.json").write_text(json.dumps(out, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    return out


if __name__ == "__main__":
    import sys
    if "--rifatte" in sys.argv:
        print(json.dumps(rifatte(), default=str)[:3000])
        raise SystemExit
    o = esegui(log=lambda x: print(x[:300], flush=True))
    for v in ("A", "B"):
        e = o["esame"].get(v)
        if e:
            i = e["intero"]
            print(f"{v}: Sharpe {i['sharpe']:.2f} annuo {100 * i['annuo']:+.1f}% discesa {100 * i['discesa_max']:.1f}% "
                  f"corretto {e['sharpe_corretto']:.2f} t {e['t']:.2f} -> {e['esito']}", flush=True)
    print("CENTOSESTA FINITA", flush=True)
