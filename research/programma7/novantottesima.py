"""Prova 160 (NOVANTOTTESIMA.md, regole 3dc968b): G1 con stop (prova 158) + funding coperto 161 B, quote fisse, riequilibrio il primo del mese.
Uso (dalla radice del repo):  python3 -m research.programma7.novantottesima
"""
from __future__ import annotations

import json
import math
import traceback
from pathlib import Path

import numpy as np
import pandas as pd

from research.programma6 import asticella as ast
from research.programma6 import terza as te
from research.src import prove

QUI = Path(__file__).resolve().parent
RIS = QUI / "risultati_novantottesima"
ID = "novantottesima"
SEME = 160
VARIANTI = {"A": 0.8, "B": 0.6}
COSTO_G1 = 0.0005 + 0.0002      # commissione a mercato + scarto sulle altre monete
COSTO_COP = 0.0005 + 0.0001     # commissione a mercato + scarto BTC/ETH
CAP = 1000.0


def carica():
    g = pd.read_csv(QUI / "risultati_novantaseiesima" / "giorni_G1_con_stop.csv.gz", index_col="giorno")["rendimento"]
    c = pd.read_csv(QUI / "risultati_novantanovesima" / "giorni_B.csv.gz", index_col=0)["netto"]
    assert g.index.equals(c.index) and len(g) == 2100, "date diverse"
    return g, c


def miscela(rg: np.ndarray, rc: np.ndarray, giorni: np.ndarray, w: float, modo: str = "mensile"):
    """modo: mensile (con costi), mensile_zero (senza costi), giornaliero_zero (pesi fissi ogni giorno, costo zero)."""
    mese = pd.to_datetime(giorni * 86400, unit="s").to_period("M").to_numpy()
    n = len(rg)
    r = np.zeros(n)
    vg, vc = w, 1 - w
    costi = 0.0
    for i in range(n):
        v0 = vg + vc
        if modo == "giornaliero_zero":
            vg, vc = w * v0, (1 - w) * v0
        elif i > 0 and mese[i] != mese[i - 1]:
            mosso = abs(vg - w * v0)
            c = mosso * (COSTO_G1 + COSTO_COP) if modo == "mensile" else 0.0
            costi += c
            v = v0 - c
            vg, vc = w * v, (1 - w) * v
        vg *= 1 + rg[i]
        vc *= 1 + rc[i]
        r[i] = vg + vc
    eq = r.copy()
    prev = np.concatenate([[1.0], eq[:-1]])
    return pd.Series(eq / prev - 1, index=giorni), costi


def sett(r: pd.Series) -> pd.Series:
    lun = ((r.index.to_numpy() + 3) // 7) * 7 - 3
    return r.groupby(lun).apply(lambda x: float(np.prod(1 + x.to_numpy()) - 1))


def nw_t(x: np.ndarray, L: int) -> float:
    x = np.asarray(x, float)
    n = len(x)
    u = x - x.mean()
    s = float(u @ u) / n
    for l in range(1, L + 1):
        s += 2 * (1 - l / (L + 1)) * float(u[l:] @ u[:-l]) / n
    return float(x.mean() / math.sqrt(s / n))


def dd(r: np.ndarray) -> float:
    e = np.cumprod(1 + r)
    return float((e / np.maximum.accumulate(e) - 1).min())


def misure(r: pd.Series) -> dict:
    d = r.to_numpy()
    w = sett(r)
    num = te.numeri_settimana(w)
    anni = len(d) / 365.0
    date = pd.to_datetime(r.index.to_numpy() * 86400, unit="s")
    per_anno_comp = {int(y): float(np.prod(1 + d[date.year == y]) - 1) for y in sorted(set(date.year))}
    wd = pd.to_datetime(w.index.to_numpy() * 86400, unit="s")
    per_anno_sett = {int(y): float(w.to_numpy()[wd.year == y].mean() * 52) for y in sorted(set(wd.year))}
    m = pd.Series(1 + d, index=date).groupby(date.to_period("M")).prod() - 1
    cagr = float(np.prod(1 + d) ** (1 / anni) - 1)
    return {"giorni": len(d), "settimane": num["settimane"], "annuo_composto": cagr, "annuo_media52": num["annuo"],
            "usdt_su_1000_composto": CAP * cagr, "sharpe_sett": num["sharpe"], "asimmetria": num["asimmetria"], "curtosi": num["curtosi"],
            "sharpe_365_giorni": float(d.mean() / d.std(ddof=1) * math.sqrt(365)),
            "t": num["sharpe"] * math.sqrt(num["settimane"] / 52), "t_nw13": nw_t(w.to_numpy(), 13), "t_nw26": nw_t(w.to_numpy(), 26),
            "discesa_giornaliera": dd(d), "discesa_settimanale": num["discesa_max"],
            "mesi_positivi": int((m > 0).sum()), "mesi": int(len(m)), "per_anno_composto": per_anno_comp, "per_anno_media52": per_anno_sett,
            "patrimonio_finale_su_1000": CAP * float(np.prod(1 + d))}


def main():
    RIS.mkdir(exist_ok=True)
    g, c = carica()
    giorni = g.index.to_numpy()
    rg, rc = g.to_numpy(), c.to_numpy()
    out = {"G1": misure(g), "coperto_161B": misure(c)}
    corr = {"giornaliera": float(np.corrcoef(rg, rc)[0, 1]), "settimanale": float(np.corrcoef(sett(g), sett(c))[0, 1])}
    out["correlazione"] = corr
    mix, sett_v, desc = {}, {}, {}
    cand = {}
    for v, w in VARIANTI.items():
        par = {"peso_G1": w, "peso_coperto": 1 - w, "riequilibrio": "primo del mese 00:00 UTC", "costo_G1": COSTO_G1, "costo_coperto": COSTO_COP,
               "G1": "risultati_novantaseiesima/giorni_G1_con_stop", "coperto": "risultati_novantanovesima/giorni_B", "periodo": "2021-01-04..2026-10-04"}
        try:
            r, costi = miscela(rg, rc, giorni, w)
            m = misure(r)
            m["costo_riequilibrio_totale_su_capitale_iniziale"] = costi
            sw = sett(r)
            pd.DataFrame({"netto": sw}).to_csv(RIS / f"settimane_{v}.csv.gz")
            pd.DataFrame({"netto": r}).to_csv(RIS / f"giorni_{v}.csv.gz")
            mix[v], sett_v[v] = (r, m), sw
            for modo in ("giornaliero_zero", "mensile_zero"):
                rz, _ = miscela(rg, rc, giorni, w, modo)
                desc[f"{v}_{modo}"] = {k: misure(rz)[k] for k in ("annuo_composto", "sharpe_sett", "discesa_giornaliera", "mesi_positivi")}
            cand[f"160 {v}"] = {"sharpe": m["sharpe_sett"], "settimane": m["settimane"], "asimmetria": m["asimmetria"], "curtosi": m["curtosi"]}
            out[v] = m
        except Exception:  # noqa: BLE001
            prove.registra(ID, v, par, "giornaliera, esame sulle settimane", 0, {}, "errore", traceback.format_exc()[-300:], seme=SEME)
            raise
    cf = ast.corretto_famiglie({f"160 {v}": sett_v[v] for v in VARIANTI}, cand)
    gm = out["G1"]
    for v in VARIANTI:
        m = out[v]
        m["sharpe_corretto"] = cf["candidate"][f"160 {v}"]["corretto"]
        m["gruppo"] = cf["candidate"][f"160 {v}"]["gruppo"]
        anni_ok = all(x > 0 for x in m["per_anno_media52"].values())
        anni_ok_comp = all(x > 0 for x in m["per_anno_composto"].values())
        esame = {"netto_positivo": m["annuo_composto"] > 0, "ogni_anno_positivo": anni_ok, "ogni_anno_positivo_composto": anni_ok_comp,
                 "t_almeno_3": m["t"] >= 3, "sharpe_corretto_almeno_0_80": m["sharpe_corretto"] >= 0.80}
        utile = {"1_discesa_5_punti_sotto_G1": (m["discesa_giornaliera"] - gm["discesa_giornaliera"]) >= 0.05,
                 "2_sharpe_non_sotto_di_piu_di_0_05": m["sharpe_sett"] >= gm["sharpe_sett"] - 0.05,
                 "3_meno_mesi_negativi_di_G1": (m["mesi"] - m["mesi_positivi"]) < (gm["mesi"] - gm["mesi_positivi"])}
        m["esame"], m["utile"] = esame, utile
        m["passa_esame"] = bool(all(esame[k] for k in ("netto_positivo", "ogni_anno_positivo", "t_almeno_3", "sharpe_corretto_almeno_0_80")))
        m["utile_si"] = bool(all(utile.values()))
        r, _ = mix[v]
        prove.registra(ID, v, {"peso_G1": VARIANTI[v], "peso_coperto": 1 - VARIANTI[v], "riequilibrio": "primo del mese 00:00 UTC"},
                       "giornaliera, esame sulle settimane", len(r),
                       {"annuo": m["annuo_composto"], "sharpe": m["sharpe_sett"], "t": m["t"], "t_nw13": m["t_nw13"], "t_nw26": m["t_nw26"],
                        "sharpe_corretto": m["sharpe_corretto"], "discesa": m["discesa_giornaliera"], "mesi_positivi": m["mesi_positivi"]},
                       "calcolata", f"passa_esame={m['passa_esame']}; utile={m['utile_si']}; famiglie={cf['famiglie']}", seme=SEME)
    # peggiori 10 giornate di G1
    peggiori = g.sort_values().index[:10]
    out["peggiori_10_G1"] = [{"giorno": int(d), "data": str(pd.to_datetime(d * 86400, unit="s").date()), "G1": float(g[d]), "coperto": float(c[d]),
                              "A": float(mix["A"][0][d]), "B": float(mix["B"][0][d])} for d in peggiori]
    out["senza_riequilibrio_e_mensile_a_costo_zero"] = desc
    out["famiglie"] = {"serie": cf["serie"], "famiglie": cf["famiglie"], "in_v": cf["in_v"], "senza_serie": cf["senza_serie"], "taglio": cf["taglio"]}
    (RIS / "esame.json").write_text(json.dumps(out, indent=1, ensure_ascii=False, default=float))
    return out


if __name__ == "__main__":
    o = main()
    for k in ("G1", "coperto_161B", "A", "B"):
        m = o[k]
        print(k, {x: (round(m[x], 4) if isinstance(m[x], float) else m[x]) for x in ("annuo_composto", "sharpe_sett", "t", "t_nw13", "t_nw26", "discesa_giornaliera", "mesi_positivi", "mesi") })
        print("  anni", {y: round(v, 3) for y, v in m["per_anno_composto"].items()})
    for k in ("A", "B"):
        print(k, "corretto", round(o[k]["sharpe_corretto"], 3), "esame", o[k]["passa_esame"], o[k]["esame"], "utile", o[k]["utile_si"], o[k]["utile"])
    print("corr", o["correlazione"], "famiglie", o["famiglie"]["famiglie"])
