"""Programma 7, prova 159 (NOVANTASETTESIMA.md, con le regole corrette del 15 novembre 2026): BQ, la base dei future trimestrali di
Bitcoin ed Ether come rendimento fisso. A: coin-margined, 50% Bitcoin + 50% Ether, dal 25 settembre 2020 (Ether dal 25 dicembre 2020).
B: Bitcoin in USDT al 100%, dal 25 marzo 2022, con la liquidazione se la perdita aperta del future supera la riserva.

Conto in frazioni del capitale totale (1 = pronti 0,8 + riserva 0,2: la riserva e' 0,25 del pronti), senza capitalizzare.
Uso: python3 -m research.programma7.novantasettesima
"""
from __future__ import annotations

import glob
import json
import math
import os
import traceback
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd

from research.programma6 import asticella as ast
from research.programma6 import seconda as sc
from research.programma6 import terza as te
from research.src import prove

QUI = Path(__file__).parent
RIS = QUI / "risultati_novantasettesima"
DATI = QUI.parent / "data" / "trimestrali_binance"
ID = "novantasettesima"
FINE_GIORNO = 20730            # 4 ottobre 2026 compreso (giorni dall
RISERVA = 0.25                 # frazione del nozionale a pronti
CS = 0.0015                    # pronti per lato: 0,10% + 0,05%
CF_LIM = 0.0002 + 0.0001       # future all'ingresso: limite 0,02% + scarto 0,01%
CF_MKT = 0.0005 + 0.0001       # future a mercato (liquidazione): 0,05% + 0,01%
COSTO_CICLO = 2 * CS + CF_LIM  # 0,33% del nozionale
MS_H, MS_D = 3600000, 86400000


def leggi(d: str) -> pd.DataFrame:
    out = []
    for f in sorted(glob.glob(d + "/*.zip")):
        z = zipfile.ZipFile(f)
        for n in z.namelist():
            x = pd.read_csv(z.open(n), header=None).iloc[:, :5]
            out.append(x)
    x = pd.concat(out)
    x.columns = ["t", "o", "h", "l", "c"]
    x = x[pd.to_numeric(x["t"], errors="coerce").notna()].astype({"t": "int64"})
    x["t"] = np.where(x["t"] > 10 ** 14, x["t"] // 1000, x["t"])         # il pronti dal 2025 e' in microsecondi
    return x.drop_duplicates("t").sort_values("t").set_index("t").astype(float)


def scadenza_ms(code: str) -> int:
    d = pd.Timestamp("20" + code[-6:-4] + "-" + code[-4:-2] + "-" + code[-2:] + " 08:00")
    return int((d - pd.Timestamp("1970-01-01")).total_seconds() * 1000)


class Dati:
    def __init__(self):
        self.fh, self.fd, self.sh, self.sd = {}, {}, {}, {}
        for mk, pre in (("cm", "BTCUSD"), ("cm", "ETHUSD"), ("um", "BTCUSDT")):
            for c in sorted(os.listdir(f"{DATI}/{mk}")):
                if c.startswith(pre + "_"):
                    h = leggi(f"{DATI}/{mk}/{c}/1h")
                    h = h[h.index <= scadenza_ms(c)]                    # le candele ferme dopo la scadenza si ignorano
                    d = leggi(f"{DATI}/{mk}/{c}/1d")
                    d = d[d.index <= scadenza_ms(c)]
                    self.fh[c], self.fd[c] = h, d
        for s in ("BTCUSDT", "ETHUSDT"):
            self.sh[s], self.sd[s] = leggi(f"{DATI}/spot/{s}/1h"), leggi(f"{DATI}/spot/{s}/1d")

    def chiusura_giorno(self, c: str, g: int):
        """Chiusura giornaliera del future (g = giorno dall'epoca), con l'ultima nota se il giorno manca. Ritorna (prezzo, riempito)."""
        d = self.fd[c]
        t = g * MS_D
        if t in d.index:
            return float(d.loc[t, "c"]), False
        prima = d[d.index < t]
        return float(prima["c"].iloc[-1]), True

    def spot_giorno(self, s: str, g: int) -> float:
        return float(self.sd[s].loc[g * MS_D, "c"])


def contratti(pre: str) -> list:
    return sorted({c for c in (os.listdir(f"{DATI}/cm") if pre.endswith("USD") else os.listdir(f"{DATI}/um")) if c.startswith(pre + "_")},
                  key=scadenza_ms)


def simula(D: Dati, pre: str, spot: str, lineare: bool, T0: str, nozionale: float, liquida: bool, a: int, b: int):
    """Una moneta. T0 = codice della prima scadenza T (ingresso dopo T nel contratto successivo). Ritorna (pnl giornaliero dict, operazioni)."""
    lst = contratti(pre)
    i0 = lst.index(T0)
    pnl: dict = {}
    ops = []
    add = lambda g, x: pnl.__setitem__(g, pnl.get(g, 0.0) + x)  # noqa: E731
    for i in range(i0, len(lst) - 1):
        Tms = scadenza_ms(lst[i])
        c = lst[i + 1]
        if Tms // MS_D > b:
            break
        te_ms = Tms + MS_H                      # ingresso all'apertura delle 09:00
        hS, hF = D.sh[spot], D.fh[c]
        op = {"contratto": c, "T": pd.to_datetime(Tms, unit="ms").strftime("%Y-%m-%d"), "dentro": False, "liquidata": False}
        try:
            S08, F08 = float(hS.loc[Tms, "c"]), float(hF.loc[Tms, "c"])
            Se, Fe = float(hS.loc[te_ms, "o"]), float(hF.loc[te_ms, "o"])
        except KeyError:
            op["nota"] = "candela mancante: saltato"
            ops.append(op)
            continue
        Tx = scadenza_ms(c)
        giorni = (Tx - te_ms) / MS_D
        base = (F08 / S08 - 1) * 365 / giorni
        op.update({"base_annua": base, "giorni": giorni, "F_ingresso": Fe, "S_ingresso": Se})
        if not (base > COSTO_CICLO / (giorni / 365)):
            ops.append(op)
            continue
        op["dentro"] = True
        Q = nozionale / Se
        costo_in = nozionale * (CS + CF_LIM)
        add(te_ms // MS_D, -costo_in)
        valore = lambda Sd, Fd: (Q * (Sd - Fd + Fe)) if lineare else (Q * Sd * Fe / Fd)  # noqa: E731
        prec = nozionale
        riemp = 0
        morta = False
        gx = Tx // MS_D
        for g in range(te_ms // MS_D, gx):
            if g > b:
                break
            Fd, r = D.chiusura_giorno(c, g)
            riemp += int(r)
            Sd = D.spot_giorno(spot, g)
            V = valore(Sd, Fd)
            add(g, V - prec)
            prec = V
            if liquida and Q * (Fd - Fe) > RISERVA * nozionale:
                add(g, -(Q * Sd * CS + Q * Fd * CF_MKT))
                op["liquidata"], morta = True, True
                op["giorno_liquidazione"] = pd.to_datetime(g * MS_D, unit="ms").strftime("%Y-%m-%d")
                break
        op["giorni_riempiti"] = riemp
        if not morta and gx <= b:
            Sx, Fx = float(hS.loc[Tx, "o"]), float(hF.loc[Tx, "c"])
            V = valore(Sx, Fx)
            add(gx, V - prec - Q * Sx * CS)
            op["rendimento_ciclo"] = (V - Q * Sx * CS - costo_in - nozionale) / nozionale
        elif not morta:                           # ancora aperto al 4 ottobre: valore di mercato a fine periodo (fuori dall'esame il costo di chiusura)
            op["aperto_alla_fine"] = True
        hh = hF[(hF.index >= te_ms) & (hF.index <= Tx)]
        op["massimo_future_su_ingresso"] = float(hh["h"].max() / Fe - 1)
        op["liquidabile_con_i_massimi"] = bool(Q * (hh["h"].max() - Fe) > RISERVA * nozionale) if lineare else False
        ops.append(op)
    return pnl, ops


def a_serie(pnl: dict, a: int, b: int) -> pd.Series:
    g = np.arange(a, b + 1)
    return pd.Series([pnl.get(int(x), 0.0) for x in g], index=g)


def settimanale(giorni: pd.Series) -> pd.Series:
    s = giorni.groupby(ast._lunedi(giorni.index)).sum()
    return s.rename("netto")


def misure(w: pd.Series, giorni: pd.Series, inizio_att: int) -> dict:
    """Esame sulla serie giornaliera aggregata in settimane intere."""
    n = te.numeri_settimana(w)
    date = pd.to_datetime(w.index.to_numpy() * 86400, unit="s")
    per_anno = {int(y): float(w[date.year == y].sum()) for y in sorted(set(date.year))}
    per_anno_ann = {int(y): float(w[date.year == y].mean() * 52) for y in sorted(set(date.year))}
    gg = giorni[giorni.index >= inizio_att]
    eq = 1 + gg.cumsum()
    dd = float((eq / eq.cummax() - 1).min())
    dm = pd.to_datetime(gg.index.to_numpy() * 86400, unit="s")
    mesi = gg.groupby([dm.year, dm.month]).sum()
    w2 = w[(date.year >= 2024)]
    return {**n, "t": n["sharpe"] * math.sqrt(n["settimane"] / 52), "netto_totale": float(w.sum()),
            "annuo_capitale": float(w.mean() * 52), "discesa_giornaliera": dd, "mesi_positivi": int((mesi > 0).sum()), "mesi": int(len(mesi)),
            "per_anno_somma": per_anno, "per_anno_annualizzato": per_anno_ann,
            "annuo_2024_2026": float(w2.mean() * 52), "settimane_2024_2026": int(len(w2)),
            "annuo_sul_solo_pronti": float(w.mean() * 52 * 1.25)}


def esegui(log=print) -> dict:
    RIS.mkdir(exist_ok=True)
    D = Dati()
    a = 18526                     # 2020-09-21, il lunedi prima del 25 settembre 2020
    b = FINE_GIORNO
    out, serie_sett, serie_giorni, tutte_ops = {}, {}, {}, {}
    par = {"capitale": "1 = pronti 0,8 + riserva 0,2 (25% del pronti), senza capitalizzare", "costo_pronti_lato": CS, "future_ingresso": CF_LIM,
           "future_mercato": CF_MKT, "fine": "2026-10-04"}
    for v in ("A", "B"):
        try:
            if v == "A":
                p1, o1 = simula(D, "BTCUSD", "BTCUSDT", False, "BTCUSD_200925", 0.4, False, a, b)
                p2, o2 = simula(D, "ETHUSD", "ETHUSDT", False, "ETHUSD_201225", 0.4, False, a, b)
                pnl = {g: p1.get(g, 0.0) + p2.get(g, 0.0) for g in set(p1) | set(p2)}
                ops = {"BTC": o1, "ETH": o2}
                inizio_att = 18530
                parv = {**par, "contratti": "BTCUSD+ETHUSD coin-margined", "partenza": "BTC 2020-09-25, ETH 2020-12-25"}
            else:
                pnl, o = simula(D, "BTCUSDT", "BTCUSDT", True, "BTCUSDT_220325", 0.8, True, a, b)
                ops = {"BTC": o}
                inizio_att = 19076   # 2022-03-25
                parv = {**par, "contratti": "BTCUSDT in USDT", "partenza": "2022-03-25", "liquidazione": "perdita aperta del future > riserva a chiusura giornaliera"}
            gi = a_serie(pnl, a, b)
            w = settimanale(gi)
            w = w[w.index <= 20724]                                  # settimane intere fino a quella del 28 settembre (4 ottobre domenica)
            gi = gi[gi.index <= 20730]
            m = misure(w, gi, inizio_att)
            m["periodo_mazzo"] = te.numeri_settimana(ast.periodo(w))
            nd = [x for l in ops.values() for x in l]
            m["trimestri"] = len(nd)
            m["trimestri_dentro"] = sum(1 for x in nd if x["dentro"])
            m["trimestri_saltati"] = m["trimestri"] - m["trimestri_dentro"]
            m["liquidazioni"] = sum(1 for x in nd if x.get("liquidata"))
            m["liquidabili_con_i_massimi"] = sum(1 for x in nd if x.get("liquidabile_con_i_massimi"))
            m["giorni_riempiti"] = sum(x.get("giorni_riempiti", 0) for x in nd)
            m["costo_medio_ciclo"] = COSTO_CICLO
            out[v] = m
            serie_sett[v], serie_giorni[v], tutte_ops[v] = w, gi, ops
            w.to_frame("netto").rename_axis("settimana").to_csv(RIS / f"settimane_{v}.csv.gz")
            gi.to_frame("netto").rename_axis("giorno").to_csv(RIS / f"giorni_{v}.csv.gz")
            (RIS / f"operazioni_{v}.json").write_text(json.dumps(ops, indent=1, default=str))
            prove.registra(ID, v, parv, "giornaliera, esame su settimane intere", int(m["settimane"]),
                           {"annuo_capitale": m["annuo_capitale"], "sharpe": m["sharpe"], "t": m["t"], "discesa": m["discesa_giornaliera"],
                            "liquidazioni": m["liquidazioni"], "per_anno": m["per_anno_somma"]}, "calcolata", "")
        except Exception:  # noqa: BLE001
            prove.registra(ID, v, par, "giornaliera", 0, {}, "errore", traceback.format_exc()[-300:])
            raise
    # Sharpe corretto con le due serie insieme e correlazioni
    cand = {f"159 {v}": {k: out[v]["periodo_mazzo"][k] for k in ("sharpe", "settimane", "asimmetria", "curtosi")} for v in out}
    corr = ast.corretto_famiglie({f"159 {v}": serie_sett[v] for v in out}, cand)
    for v in out:
        c = corr["candidate"][f"159 {v}"]
        out[v]["sharpe_corretto"], out[v]["gruppo"] = c["corretto"], c["gruppo"]
    out["conto"] = {k: corr[k] for k in ("serie", "senza_serie", "famiglie", "in_v", "deviazione_v")}
    # correlazioni con G1 e con la prova 157
    g1 = ast.periodo(ast.serie_programma7()["57 G1"])
    p157 = {v: ast.periodo(pd.read_csv(QUI / "risultati_novantacinquesima" / f"settimane_{v}.csv.gz", index_col=0)["netto"]) for v in ("A", "B")}
    cor = {}
    for v in ("A", "B"):
        s = ast.periodo(serie_sett[v])
        cor[v] = {"G1": float(s.corr(g1.reindex(s.index).dropna().reindex(s.index))),
                  **{f"157 {k}": float(s.corr(p157[k].reindex(s.index))) for k in p157}}
    out["correlazioni"] = cor
    out["descrittivi"] = descrittivi(D, tutte_ops, serie_giorni)
    (RIS / "esame.json").write_text(json.dumps(out, indent=1, default=str))
    imp = json.loads((DATI / "IMPRONTE_TUTTI.json").read_text())
    (RIS / "impronte_file_scaricati.json").write_text(json.dumps(imp, indent=0))
    return out


def descrittivi(D: Dati, tutte_ops: dict, giorni: dict) -> dict:
    d: dict = {}
    # base per trimestre, rendimento netto per trimestre
    righe = []
    for v, ops in tutte_ops.items():
        for m, l in ops.items():
            for x in l:
                righe.append({"variante": v, "moneta": m, **{k: x.get(k) for k in ("T", "contratto", "dentro", "base_annua", "rendimento_ciclo", "liquidata",
                                                                                     "massimo_future_su_ingresso", "giorni_riempiti")}})
    pd.DataFrame(righe).to_csv(RIS / "trimestri.csv", index=False)
    # la base contro il funding medio del perpetuo nello stesso trimestre
    try:
        pan = sc.pannello()
        sim = pan["simboli"]
        t0 = int(pan["t0"])
        conf = []
        for r in righe:
            if r["variante"] == "A" and r["base_annua"] is not None and not pd.isna(r["base_annua"]):
                j = sim.index(r["moneta"] + "USDT")
                g0 = int(pd.Timestamp(r["T"]).timestamp() // 86400)
                g1 = int(pd.Timestamp("20" + r["contratto"][-6:-4] + "-" + r["contratto"][-4:-2] + "-" + r["contratto"][-2:]).timestamp() // 86400)
                f = pan["funding"][g0 - t0:g1 - t0, j]
                conf.append((r["base_annua"], float(np.nanmean(f) * 365)))
        d["base_media_annua"] = float(np.mean([c[0] for c in conf]))
        d["funding_medio_annuo_stessi_trimestri"] = float(np.mean([c[1] for c in conf]))
        d["trimestri_con_base_sopra_funding"] = f"{sum(1 for c in conf if c[0] > c[1])} su {len(conf)}"
    except Exception as ex:  # noqa: BLE001
        d["funding_confronto"] = f"non calcolato: {ex}"
    # margine: rialzo massimo del Bitcoin in 1 e 7 giorni durante un contratto, massimo del future su ingresso
    sd = D.sd["BTCUSDT"]["c"]
    sd.index = (sd.index // MS_D).astype(int)
    r1, r7 = sd.pct_change(1), sd.pct_change(7)
    d["btc_rialzo_max_1g"], d["btc_rialzo_max_7g"] = float(r1.max()), float(r7.max())
    mx = [(x["massimo_future_su_ingresso"], x["contratto"]) for l in tutte_ops["B"].values() for x in l if x.get("massimo_future_su_ingresso") is not None]
    d["B_massimo_future_su_ingresso"] = max(mx) if mx else None
    mxa = [(x["massimo_future_su_ingresso"], x["contratto"]) for m, l in tutte_ops["A"].items() for x in l if x.get("massimo_future_su_ingresso") is not None]
    d["A_massimo_future_su_ingresso"] = max(mxa) if mxa else None
    # stress: base annualizzata dei contratti vivi nei giorni indicati
    st = {}
    for g in ("2021-05-10", "2022-11-09", "2022-11-10", "2022-11-11", "2022-11-12", "2025-10-10"):
        gd = int(pd.Timestamp(g).timestamp() // 86400)
        l = []
        for c, dd in D.fd.items():
            if not c.startswith("BTCUSD_"):
                continue
            tx = scadenza_ms(c)
            if dd.index.min() <= gd * MS_D <= tx and (tx - gd * MS_D) / MS_D > 20 and gd * MS_D in dd.index:
                S = D.spot_giorno("BTCUSDT", gd)
                F = float(dd.loc[gd * MS_D, "c"])
                l.append({c: round((F / S - 1) * 365 / ((tx - gd * MS_D) / MS_D), 4)})
        st[g] = l
    d["stress_base_annua_btc"] = st
    return d


if __name__ == "__main__":
    r = esegui()
    for v in ("A", "B"):
        m = r[v]
        print(v, "annuo", round(m["annuo_capitale"], 4), "sharpe", round(m["sharpe"], 2), "t", round(m["t"], 2), "corretto", round(m["sharpe_corretto"], 2),
              "dd", round(m["discesa_giornaliera"], 4), "liq", m["liquidazioni"], "saltati", m["trimestri_saltati"], "/", m["trimestri"])
