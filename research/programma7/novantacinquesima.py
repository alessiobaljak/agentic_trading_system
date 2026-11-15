"""Programma 7, prova 157 (NOVANTACINQUESIMA.md, con le regole corrette del 15 novembre): CB, il funding coperto su BTC ed ETH senza ricambio.
Quantita' ferme finche' si e' dentro; conto in frazioni del capitale totale (1), senza capitalizzare; metà del capitale a moneta.

Uso: python3 -m research.programma7.novantacinquesima
"""
from __future__ import annotations

import json
import math
import traceback
from pathlib import Path

import numpy as np
import pandas as pd

from research.programma6 import asticella as ast
from research.programma6 import seconda as sc
from research.programma6 import sesta as se
from research.programma6 import terza as te
from research.programma7 import prima as pr
from research.programma7 import trentacinquesima as t35
from research.src import prove

QUI = Path(__file__).parent
RIS = QUI / "risultati_novantacinquesima"
ID = "novantacinquesima"
MONETE = ("BTCUSDT", "ETHUSDT")
CAPITALE_MONETA = 0.5            # capitale totale 1, metà a moneta
NOZIONALE = CAPITALE_MONETA / 1.5
RISERVA = CAPITALE_MONETA / 3.0   # il terzo del capitale della moneta, fuori dal nozionale
CS_STD, CS_LIM = 0.0015, 0.0011   # pronti per lato: 0,10%+0,05% ; limite 0,10%+0,01%
CP_LIM = 0.0002 + 0.0001


def segnale(F: np.ndarray, a: int, b: int, N: int | None) -> np.ndarray:
    """Dentro il giorno t (a..b) se la media di F[t-N..t-1] > 0; N None = sempre dentro."""
    if N is None:
        return np.ones(b - a + 1, bool)
    return np.array([F[t - N:t].mean() > 0 for t in range(a, b + 1)])


def simula_moneta(S, P, Ph, F, sig, a, b, cs, cp):
    n = b - a + 1
    z = lambda: np.zeros(n)  # noqa: E731
    o = {k: z() for k in ("funding", "base", "spese", "long", "short", "giro", "dentro", "margine")}
    o["salita_max"], o["perdita_max_apertura"], o["perdita_max_massimo"], o["giri"], o["riduzioni"] = 0.0, 0.0, 0.0, 0, 0
    dentro = False
    Q = Pe = Rc = 0.0
    Se = 0.0
    for k, t in enumerate(range(a, b + 1)):
        vuole = bool(sig[k])
        if dentro and not vuole:
            o["spese"][k] += Q * S[t] * cs + Q * P[t] * cp
            o["giro"][k] += Q * S[t]
            dentro = False
            continue
        if not dentro:
            if not vuole:
                continue
            Q, Pe, Se, Rc, dentro = NOZIONALE / S[t], P[t], S[t], RISERVA, True
            o["spese"][k] += Q * S[t] * cs + Q * P[t] * cp
            o["giro"][k] += Q * S[t]
            o["giri"] += 1
        else:
            L = Q * (P[t] - Pe)
            if L > Rc:
                e = L - Rc
                q = min(Q, e / (S[t] * (1 - cs)))
                o["spese"][k] += q * S[t] * cs + q * P[t] * cp
                o["giro"][k] += q * S[t]
                Q -= q
                Rc += e
                o["riduzioni"] += 1
                if Q <= 1e-15:
                    dentro = False
                    continue
        o["dentro"][k] = 1
        o["salita_max"] = max(o["salita_max"], S[t] / Se - 1)
        o["perdita_max_apertura"] = max(o["perdita_max_apertura"], Q * (P[t] - Pe) / RISERVA)
        o["perdita_max_massimo"] = max(o["perdita_max_massimo"], Q * (Ph[t] - Pe) / RISERVA)
        lungo, corto = Q * (S[t + 1] - S[t]), -Q * (P[t + 1] - P[t])
        o["long"][k], o["short"][k], o["base"][k] = lungo, corto, lungo + corto
        o["funding"][k] = F[t] * Q * P[t]
        if t == b:     # uscita finale all'apertura del 5 ottobre
            o["spese"][k] += Q * S[t + 1] * cs + Q * P[t + 1] * cp
            o["giro"][k] += Q * S[t + 1]
    return o


def conto(pan, Op, N, limite=False):
    a, b = se.INIZIO - pan["t0"], pr.FINE - 1 - pan["t0"]
    simboli = pan["simboli"]
    costo = sc.costi_moneta(simboli)
    out = {}
    for k, s in enumerate(MONETE):
        j = simboli.index(s)
        F = pan["funding"][:, j]
        sig = segnale(F, a, b, N)
        cp = CP_LIM if limite else float(costo[j])
        out[s] = simula_moneta(Op[:, k], pan["open"][:, j], pan["high"][:, j], F, sig, a, b, CS_LIM if limite else CS_STD, cp)
    giorni = np.arange(se.INIZIO, pr.FINE, dtype=np.int64)
    d = pd.DataFrame(index=giorni)
    for c in ("funding", "base", "spese", "long", "short", "giro", "dentro"):
        d[c] = sum(out[s][c] for s in MONETE)
    for s in MONETE:
        for c in ("funding", "base", "spese", "dentro"):
            d[f"{c}_{s[:3]}"] = out[s][c]
    d["netto"] = d["funding"] + d["base"] - d["spese"]
    d["netto_doppio"] = d["funding"] + d["base"] - 2 * d["spese"]
    return d, out


def settimane(d: pd.DataFrame) -> pd.DataFrame:
    s = d.copy()
    s["settimana"] = pr.lunedi_del_giorno(d.index.to_numpy())
    g = s.groupby("settimana")
    w = g[["base", "spese", "funding", "netto", "netto_doppio", "giro", "long", "short"]].sum()
    w["funding_incassato"] = w["funding"]
    w["funding"] = -w["funding_incassato"]
    w["monete"] = g[["dentro_BTC", "dentro_ETH"]].max().sum(axis=1)
    w["lordo"] = w["base"]
    return w


def discesa(r: np.ndarray) -> float:
    eq = np.cumprod(1 + r)
    return float((eq / np.maximum.accumulate(eq) - 1).min())


def esegui(log=print) -> dict:
    RIS.mkdir(exist_ok=True)
    pan = sc.pannello()
    n = pan["open"].shape[0]
    Op = t35.tabella_pronti(list(MONETE), pan["t0"], n)
    ps = te.pannello_settimane(pan, log=lambda x: None, indicatori_si=False)
    btc_w = pd.Series(ps["R"][:, pan["simboli"].index("BTCUSDT")], index=ps["lunedi"])
    a = se.INIZIO - pan["t0"]
    b = pr.FINE - 1 - pan["t0"]
    jb = pan["simboli"].index("BTCUSDT")
    btc_g = pd.Series(pan["open"][a + 1:b + 2, jb] / pan["open"][a:b + 1, jb] - 1, index=np.arange(se.INIZIO, pr.FINE))
    g1 = pd.read_csv(QUI / "risultati_prima" / "giorni_G1.csv.gz")["netto"]
    g1.index = np.arange(se.INIZIO, se.INIZIO + len(g1))
    cc = pd.read_csv(QUI / "risultati_trentacinquesima" / "settimane_CC.csv.gz", index_col=0)["netto"]
    g1w = pd.read_csv(QUI / "risultati_prima" / "settimane_G1.csv.gz", index_col=0)["netto"]
    varianti = {"A": 30, "B": 90}
    out, giornalieri, sett, limite_out = {}, {}, {}, {}
    for v, N in varianti.items():
        par = {"N": N, "monete": list(MONETE), "pronti_per_lato": CS_STD, "periodo": "2021-01-04..2026-10-04"}
        try:
            d, per = conto(pan, Op, N)
            dl, _ = conto(pan, Op, N, limite=True)
            w = settimane(d)
            w.to_csv(RIS / f"settimane_{v}.csv.gz")
            d.to_csv(RIS / f"giorni_{v}.csv.gz")
            giornalieri[v], sett[v] = d, w
            e = te.esame(w, btc_w, inizio=se.INIZIO, anni_pieni=se.ANNI_PIENI)
            e["t"] = e["intero"]["sharpe"] * math.sqrt(e["intero"]["settimane"] / 52)
            out[v] = {"esame": e, "per": per, "limite_netto_annuo": float(settimane(dl)["netto"].mean() * 52)}
            prove.registra(ID, v, par, "giornaliera, esame sulle settimane", len(d),
                           {"annuo_capitale": e["intero"]["annuo"], "sharpe": e["intero"]["sharpe"], "t": e["t"],
                            "discesa": e["intero"]["discesa_max"], "per_anno": e["per_anno"]}, "calcolata", "bootstrap interno di terza.esame; deterministico")
        except Exception as ex:  # noqa: BLE001
            prove.registra(ID, v, par, "giornaliera", 0, {}, "errore", traceback.format_exc()[-300:])
            raise
    # Sempre dentro (descrittivo, non e' una variante)
    d_sem, per_sem = conto(pan, Op, None)
    w_sem = settimane(d_sem)
    # Sharpe corretto con le due serie insieme
    cand = {f"157 {v}": {k: out[v]["esame"]["intero"][k] for k in ("sharpe", "asimmetria", "curtosi")} | {"settimane": out[v]["esame"]["intero"]["settimane"]}
            for v in varianti}
    corr = ast.corretto_famiglie({f"157 {v}": sett[v]["netto"] for v in varianti}, cand)
    for v in varianti:
        c = corr["candidate"][f"157 {v}"]
        e = out[v]["esame"]
        e["sharpe_corretto"], e["gruppo"] = c["corretto"], c["gruppo"]
        anni_pos = all(x > 0 for x in e["per_anno"].values())
        e["condizioni"] = {"netto_positivo": bool(e["intero"]["annuo"] > 0), "ogni_anno_positivo": bool(anni_pos),
                           "t_almeno_3": bool(e["t"] >= 3), "sharpe_corretto_almeno_0_80": bool(c["corretto"] >= 0.80)}
        e["passa"] = all(e["condizioni"].values())
    # descrittivi
    desc = {}
    for v in varianti:
        d, w, e = giornalieri[v], sett[v], out[v]["esame"]
        r = d["netto"].to_numpy()
        mesi = pd.to_datetime(d.index.to_numpy() * 86400, unit="s").to_period("M")
        m = d["netto"].groupby(mesi).sum()
        anni = pd.to_datetime(d.index.to_numpy() * 86400, unit="s").year
        per_anno = {}
        for y in sorted(set(anni)):
            k = anni == y
            row = {c: float(d[c][k].sum()) for c in ("funding", "base", "spese", "netto")}
            row |= {f"{c}_{s}": float(d[f"{c}_{s}"][k].sum()) for s in ("BTC", "ETH") for c in ("funding", "base", "spese")}
            row["netto_nozionale"] = row["netto"] * 1.5
            per_anno[int(y)] = row
        dent = d["dentro"] > 0
        fuori = (d[["dentro_BTC", "dentro_ETH"]].sum(axis=1) == 0)
        ww = w["netto"].to_numpy()
        corr_w = lambda x, y_: float(pd.concat([x, y_], axis=1, join="inner").corr().iloc[0, 1])  # noqa: E731
        desc[v] = {
            "annuo_capitale": e["intero"]["annuo"], "annuo_nozionale": e["intero"]["annuo"] * 1.5, "usdt_su_1000": e["intero"]["annuo"] * 1000,
            "volatilita": e["intero"]["volatilita"], "sharpe": e["intero"]["sharpe"], "t": e["t"],
            "discesa_giornaliera": discesa(r), "discesa_settimanale": e["intero"]["discesa_max"], "peggiore_settimana": float(ww.min()),
            "mesi_positivi": int((m > 0).sum()), "mesi": int(len(m)),
            "giorni": {"positivi": int(((r > 0) & ~fuori).sum()), "fuori": int(fuori.sum()), "dentro_negativi": int(((r <= 0) & ~fuori).sum())},
            "per_anno_calendario": per_anno, "per_anno_esame": e["per_anno"], "spese_annue": e["spese_annue"], "costi_doppi_annuo": e["costi_doppi"] * 1,
            "giorni_dentro": {s[:3]: int(d[f"dentro_{s[:3]}"].sum()) for s in MONETE},
            "giri": {s[:3]: out[v]["per"][s]["giri"] for s in MONETE},
            "riduzioni_margine": {s[:3]: out[v]["per"][s]["riduzioni"] for s in MONETE},
            "salita_max_pronti_in_posizione": {s[:3]: out[v]["per"][s]["salita_max"] for s in MONETE},
            "perdita_perpetuo_su_riserva_max_apertura": {s[:3]: out[v]["per"][s]["perdita_max_apertura"] for s in MONETE},
            "perdita_perpetuo_su_riserva_max_massimo_giorno": {s[:3]: out[v]["per"][s]["perdita_max_massimo"] for s in MONETE},
            "limite_annuo_capitale": out[v]["limite_netto_annuo"],
            "corr_G1_giorni": float(pd.concat([d["netto"], g1], axis=1, join="inner").corr().iloc[0, 1]),
            "corr_BTC_giorni": float(pd.concat([d["netto"], btc_g], axis=1, join="inner").corr().iloc[0, 1]),
            "corr_G1_settimane": corr_w(w["netto"], g1w), "corr_97CC_settimane": corr_w(w["netto"], cc),
            "corr_BTC_settimane": corr_w(w["netto"], btc_w),
            "sharpe_corretto": e["sharpe_corretto"], "famiglie": corr["famiglie"], "gruppo": e["gruppo"],
            "condizioni": e["condizioni"], "passa": e["passa"], "extra_non_decisive": {
                "boot_basso": e["boot"]["basso"], "ultimo_anno": e["ultimo_anno"], "costi_doppi": e["costi_doppi"], "extra_btc_annuo": e["extra_btc_annuo"],
                "per_trimestre_positivi": {y: sum(1 for q in range(1, 5) if e["per_trimestre"][f"{y}T{q}"] > 0) for y in se.ANNI_PIENI}},
        }
    desc["sempre_dentro"] = {"annuo_capitale": float(w_sem["netto"].mean() * 52), "sharpe": float(w_sem["netto"].mean() / w_sem["netto"].std(ddof=1) * math.sqrt(52)),
                             "giorni_dentro": {s[:3]: int(d_sem[f"dentro_{s[:3]}"].sum()) for s in MONETE},
                             "giri": {s[:3]: per_sem[s]["giri"] for s in MONETE}, "riduzioni_margine": {s[:3]: per_sem[s]["riduzioni"] for s in MONETE}}
    (RIS / "esame.json").write_text(json.dumps(desc, ensure_ascii=False, indent=1, default=float), encoding="utf-8")
    pc = lambda x: f"{100 * x:+.2f}%"  # noqa: E731
    for v in varianti:
        x = desc[v]
        log(f"{v} N={varianti[v]}: anno {pc(x['annuo_capitale'])} ({x['usdt_su_1000']:+.1f} USDT/1000), Sharpe {x['sharpe']:.2f}, t {x['t']:.2f}, disc {pc(x['discesa_settimanale'])}, "
            f"mesi+ {x['mesi_positivi']}/{x['mesi']}, corretto {x['sharpe_corretto']:.2f}, passa {x['passa']}")
    return desc


if __name__ == "__main__":
    esegui()
