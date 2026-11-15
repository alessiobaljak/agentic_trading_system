"""Programma 7, prova 161 (NOVANTANOVESIMA.md, con le regole corrette del 15 novembre dopo la verifica): il funding coperto su BTC ed ETH
con il margine vero (la 157 rifatta). Due portafogli per moneta (pronti e future), prezzo mark orario, margine al 60% rifornito
sotto il 45%, liquidazione con il massimo orario del mark, patrimonio totale composto, riequilibrio solo al rientro.
Non modifica il codice della 157 ne' i caricatori (li importa).

Uso: python3 -m research.programma7.novantanovesima
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
from research.programma7 import novantacinquesima as n95
from research.programma7 import novantanovesima_dati as dat
from research.programma7 import prima as pr
from research.programma7 import trentacinquesima as t35
from research.src import prove
from research.src.dati import funding_da_zip

QUI = Path(__file__).parent
RIS = QUI / "risultati_novantanovesima"
ID = "novantanovesima"
MONETE = ("BTCUSDT", "ETHUSDT")
CS_STD, CS_LIM = 0.0015, 0.0011       # pronti per lato (regole): 0,10%+0,05% ; limite 0,10%+0,01%
CP_LIM = 0.0003                        # perpetuo a limite: 0,02% + 0,01% di scarto
MARGINE_INGRESSO, MARGINE_SOGLIA, MMR = 0.60, 0.45, 0.005
CAPITALE = 1000.0                      # il conto e' lineare: 1.000 USDT iniziali, meta' a moneta


# ----------------------------------------------------------------------------------------------------------------------
# dati orari
# ----------------------------------------------------------------------------------------------------------------------
def ore_moneta(s: str, pan, j: int) -> dict:
    h0, h1 = (se.INIZIO - 1) * 24, (pr.FINE + 2) * 24
    n = h1 - h0
    mo, mh, lo_, lh = (np.full(n, np.nan) for _ in range(4))
    for tipo, (o_, h_) in (("mark1h", (mo, mh)), ("perp1h", (lo_, lh))):
        fs = sorted((dat.DATI / tipo).glob(f"{s}-*.zip"))
        d = pd.concat([dat.leggi(f) for f in fs], ignore_index=True)
        k = (d["t"] // 3_600_000).to_numpy() - h0
        ok = (k >= 0) & (k < n)
        o_[k[ok]] = d["open"].to_numpy(float)[ok]
        h_[k[ok]] = d["high"].to_numpy(float)[ok]
    riempite = int(np.isnan(mo).sum())
    mo = np.where(np.isnan(mo), lo_, mo)
    mh = np.where(np.isnan(mh), lh, mh)
    t0 = pan["t0"]
    giorno = (np.arange(n) + h0) // 24 - t0
    ancora = int(np.isnan(mo).sum() + np.isnan(mh).sum())
    mo = np.where(np.isnan(mo), pan["open"][giorno, j], mo)       # ultimo ripiego (non dovrebbe servire)
    mh = np.where(np.isnan(mh), pan["high"][giorno, j], mh)
    righe = []
    for p in sorted((sc.DATI / s / "funding").glob("*.zip")):
        righe += funding_da_zip(p)
    R = pd.DataFrame(righe, columns=["ts", "ore", "tasso"]).drop_duplicates("ts")
    tasso = np.zeros(n)
    k = (R["ts"].to_numpy() // 3_600_000) - h0
    ok = (k >= 0) & (k < n)
    tasso[k[ok]] = R["tasso"].to_numpy(float)[ok]
    return {"h0": h0, "mo": mo, "mh": mh, "tasso": tasso, "mark_riempite": riempite, "ancora_vuote": ancora}


# ----------------------------------------------------------------------------------------------------------------------
# il conto: le due monete insieme (il riequilibrio al rientro le lega)
# ----------------------------------------------------------------------------------------------------------------------
def simula(S, H, sigs, a, b, t0, cp, cs, passi=None):
    """S: pronti (giorni x 2); H: lista di dizionari orari; sigs: segnali (n x 2). passi: [(passo, minimo, valore_minimo)] per moneta o None.
    Restituisce i giorni (DataFrame) e gli eventi."""
    n = b - a + 1
    K = 2
    C = [CAPITALE / 2] * K
    Qs, Qp, W, Pe = [0.0] * K, [0.0] * K, [0.0] * K, [0.0] * K
    dentro, scop = [False] * K, [False] * K
    Se = [0.0] * K
    fund = np.zeros((n, K)); spese = np.zeros((n, K)); rif = np.zeros((n, K)); nrif = np.zeros((n, K), int)
    giro = np.zeros(n); den = np.zeros((n, K), int)
    pre = np.zeros(n + 1)
    ev = {"liquidazioni": [], "ingressi": [0, 0], "rifornimenti": [0, 0], "giorni_sotto_mantenimento_apertura": 0, "ingressi_bloccati": [0, 0],
          "margine_apertura_min": [9.9, 9.9], "leva_max": [0.0, 0.0], "salita_max_pronti": [0.0, 0.0], "nozionale_max_su_iniziale": [0.0, 0.0],
          "aperture_leva_oltre_5": [0, 0], "x_max_su_Q": [0.0, 0.0]}

    def mo(k, T, h=0):
        return H[k]["mo"][T * 24 + h - H[k]["h0"]]

    def pat(k, s, m):
        return C[k] + Qs[k] * s + W[k] - Qp[k] * (m - Pe[k])

    def arr(q, k, su=False):
        if passi is None:
            return q
        p = passi[k][0]
        x = q / p
        return (math.ceil(x - 1e-9) if su else math.floor(x + 1e-9)) * p

    def esci(k, s, m, i, finale=False):
        spese[i, k] += Qs[k] * s * cs + Qp[k] * m * cp
        giro[i] += Qs[k] * s
        C[k] += Qs[k] * s * (1 - cs) + W[k] - Qp[k] * (m - Pe[k]) - Qp[k] * m * cp
        Qs[k] = Qp[k] = W[k] = 0.0
        dentro[k] = scop[k] = False

    for i, t in enumerate(range(a, b + 1)):
        T = t + t0
        s = [S[t, k] for k in range(K)]
        m = [mo(k, T) for k in range(K)]
        pre[i] = sum(pat(k, s[k], m[k]) for k in range(K))
        # (2) liquidazione all'apertura (dopo il regolamento delle 00:00, gia' dentro W)
        for k in range(K):
            if dentro[k] and Qp[k] > 0 and W[k] - Qp[k] * (m[k] - Pe[k]) < MMR * Qp[k] * m[k]:
                ev["liquidazioni"].append({"giorno": sc.data(T), "ora": 0, "moneta": MONETE[k], "apertura": True})
                W[k], Qp[k], scop[k] = 0.0, 0.0, True
        # (3) uscite
        for k in range(K):
            if dentro[k] and (not bool(sigs[i, k]) or scop[k]):
                esci(k, s[k], m[k], i)
        # entrate (A1: riequilibrio se l'altra e' fuori)
        for k in range(K):
            if not dentro[k] and bool(sigs[i, k]):
                o = 1 - k
                if not dentro[o]:
                    tot = C[k] + C[o]
                    C[k] = C[o] = tot / 2
                cap = C[k]
                q = arr(cap / (s[k] * (1 + cs) + MARGINE_INGRESSO * m[k]), k)
                if passi is not None and (q < passi[k][1] - 1e-12 or q * s[k] < passi[k][2]):
                    ev["ingressi_bloccati"][k] += 1
                    continue
                if q <= 0:
                    continue
                Qs[k] = Qp[k] = q
                C[k] -= q * s[k] * (1 + cs) + MARGINE_INGRESSO * q * m[k]
                W[k] = MARGINE_INGRESSO * q * m[k] - q * m[k] * cp
                Pe[k], Se[k], dentro[k] = m[k], s[k], True
                spese[i, k] += q * s[k] * cs + q * m[k] * cp
                giro[i] += q * s[k]
                ev["ingressi"][k] += 1
        # (4) rifornimento del margine
        for k in range(K):
            if dentro[k] and Qp[k] > 0:
                Q = Qp[k]
                MB = W[k] - Q * (m[k] - Pe[k])
                r = MB / (Q * m[k])
                ev["margine_apertura_min"][k] = min(ev["margine_apertura_min"][k], r)
                ev["aperture_leva_oltre_5"][k] += int(r < 0.2)
                ev["leva_max"][k] = max(ev["leva_max"][k], 1 / r if r > 0 else 99.0)
                ev["nozionale_max_su_iniziale"][k] = max(ev["nozionale_max_su_iniziale"][k], Q * m[k] / (CAPITALE / 2 / 1.6))
                if r < MARGINE_SOGLIA:
                    x = (MARGINE_INGRESSO * Q * m[k] - MB) / (s[k] * (1 - cs) - cp * m[k] + MARGINE_INGRESSO * m[k])
                    x = min(Q, arr(x, k, su=True))
                    if x > 0:
                        W[k] += x * s[k] * (1 - cs) - x * m[k] * cp - x * (m[k] - Pe[k])
                        spese[i, k] += x * s[k] * cs + x * m[k] * cp
                        giro[i] += x * s[k]
                        Qs[k] -= x
                        Qp[k] -= x
                        rif[i, k] += x * s[k]; nrif[i, k] += 1; ev["rifornimenti"][k] += 1
                        ev["x_max_su_Q"][k] = max(ev["x_max_su_Q"][k], x / Q)
                        if Qp[k] <= 1e-12:
                            C[k] += Qs[k] * s[k] * (1 - cs) + W[k]
                            Qs[k] = Qp[k] = W[k] = 0.0
                            dentro[k] = False
        # dentro la giornata: ore, regolamenti delle 08 e 16, massimo orario del mark
        for k in range(K):
            if dentro[k]:
                den[i, k] = 1
                ev["salita_max_pronti"][k] = max(ev["salita_max_pronti"][k], s[k] / Se[k] - 1)
            if not (dentro[k] and Qp[k] > 0):
                continue
            for h in range(24):
                hh = T * 24 + h - H[k]["h0"]
                if h in (8, 16):
                    f = H[k]["tasso"][hh] * Qp[k] * H[k]["mo"][hh]
                    W[k] += f; fund[i, k] += f
                M = H[k]["mh"][hh]
                if W[k] - Qp[k] * (M - Pe[k]) < MMR * Qp[k] * M:
                    ev["liquidazioni"].append({"giorno": sc.data(T), "ora": h, "moneta": MONETE[k], "apertura": False})
                    W[k], Qp[k], scop[k] = 0.0, 0.0, True
                    break
            if Qp[k] > 0:                                        # regolamento delle 00:00 del giorno dopo
                hh = (T + 1) * 24 - H[k]["h0"]
                f = H[k]["tasso"][hh] * Qp[k] * H[k]["mo"][hh]
                W[k] += f; fund[i, k] += f
    # fine: uscita finale all'apertura del 5 ottobre (spese nel giorno 4)
    T1 = b + 1 + t0
    s1 = [S[b + 1, k] for k in range(K)]
    m1 = [mo(k, T1) for k in range(K)]
    pre[n] = sum(pat(k, s1[k], m1[k]) for k in range(K))
    for k in range(K):
        if dentro[k]:
            esci(k, s1[k], m1[k], n - 1)
    post = sum(C)
    patr = pre.copy()
    patr[n] = post
    giorni = np.arange(se.INIZIO, se.INIZIO + n, dtype=np.int64)
    d = pd.DataFrame(index=giorni)
    d["patrimonio_apertura"] = pre[:n]
    d["netto"] = patr[1:] / pre[:n] - 1
    d["netto_usdt"] = patr[1:] - pre[:n]
    d["funding_usdt"] = fund.sum(1); d["spese_usdt"] = spese.sum(1); d["rifornimento_usdt"] = rif.sum(1); d["rifornimenti"] = nrif.sum(1)
    d["base_usdt"] = d["netto_usdt"] - d["funding_usdt"] + d["spese_usdt"]
    for k, nm in enumerate(("BTC", "ETH")):
        d[f"funding_usdt_{nm}"] = fund[:, k]; d[f"spese_usdt_{nm}"] = spese[:, k]; d[f"dentro_{nm}"] = den[:, k]
    d["spese"] = d["spese_usdt"] / d["patrimonio_apertura"]
    d["funding"] = d["funding_usdt"] / d["patrimonio_apertura"]
    d["netto_doppio"] = d["netto"] - d["spese"]
    d["giro"] = giro / d["patrimonio_apertura"]
    d["dentro"] = den.max(1)
    d["long"] = 0.0; d["short"] = 0.0
    return d, ev


def settimane(d: pd.DataFrame) -> pd.DataFrame:
    s = d.copy()
    s["settimana"] = pr.lunedi_del_giorno(d.index.to_numpy())
    g = s.groupby("settimana")
    w = pd.DataFrame({"netto": g["netto"].apply(lambda x: float(np.prod(1 + x.to_numpy()) - 1)),
                      "netto_doppio": g["netto_doppio"].apply(lambda x: float(np.prod(1 + x.to_numpy()) - 1))})
    for c in ("spese", "funding", "giro", "long", "short"):
        w[c] = g[c].sum()
    w["monete"] = g[["dentro_BTC", "dentro_ETH"]].max().sum(axis=1)
    return w


def dd(r: np.ndarray) -> float:
    eq = np.cumprod(1 + r)
    return float((eq / np.maximum.accumulate(eq) - 1).min())


def cagr(r: np.ndarray, anni: float) -> float:
    return float(np.prod(1 + r) ** (1 / anni) - 1)


def passi_veri():
    f = json.loads((Path(__file__).resolve().parents[2] / "bot" / "portafoglio" / "filtri_conto_vero.json").read_text())["filtri"]
    return [(f[s]["passo"], f[s]["quantita_minima"], f[s]["valore_minimo"]) for s in MONETE], {s: f[s] for s in MONETE}


def esegui(log=print) -> dict:
    RIS.mkdir(exist_ok=True)
    pan = sc.pannello()
    n_p = pan["open"].shape[0]
    Op = t35.tabella_pronti(list(MONETE), pan["t0"], n_p)
    t0 = pan["t0"]
    a, b = se.INIZIO - t0, pr.FINE - 1 - t0
    simboli = pan["simboli"]
    js = [simboli.index(s) for s in MONETE]
    H = [ore_moneta(s, pan, j) for s, j in zip(MONETE, js)]
    costo = sc.costi_moneta(simboli)
    cp_std = float(costo[js[0]])
    assert abs(cp_std - float(costo[js[1]])) < 1e-12
    ps = te.pannello_settimane(pan, log=lambda x: None, indicatori_si=False)
    btc_w = pd.Series(ps["R"][:, simboli.index("BTCUSDT")], index=ps["lunedi"])
    jb = simboli.index("BTCUSDT")
    btc_g = pd.Series(pan["open"][a + 1:b + 2, jb] / pan["open"][a:b + 1, jb] - 1, index=np.arange(se.INIZIO, pr.FINE))
    g1 = pd.read_csv(QUI / "risultati_prima" / "giorni_G1.csv.gz")["netto"]
    g1.index = np.arange(se.INIZIO, se.INIZIO + len(g1))
    cc = pd.read_csv(QUI / "risultati_trentacinquesima" / "settimane_CC.csv.gz", index_col=0)["netto"]
    g1w = pd.read_csv(QUI / "risultati_prima" / "settimane_G1.csv.gz", index_col=0)["netto"]
    passi, filtri_usati = passi_veri()

    def segnali(N):
        return np.column_stack([n95.segnale(pan["funding"][:, j], a, b, N) for j in js])

    S = Op
    varianti = {"A": 30, "B": 90}
    out, gg, sett, extra = {}, {}, {}, {}
    for v, N in varianti.items():
        par = {"N": N, "monete": list(MONETE), "pronti_per_lato": CS_STD, "perpetuo_per_lato": cp_std, "margine_ingresso": MARGINE_INGRESSO,
               "soglia_rifornimento": MARGINE_SOGLIA, "mantenimento": MMR, "periodo": "2021-01-04..2026-10-04"}
        try:
            d, ev = simula(S, H, segnali(N), a, b, t0, cp_std, CS_STD)
            w = settimane(d)
            w.to_csv(RIS / f"settimane_{v}.csv.gz")
            d.to_csv(RIS / f"giorni_{v}.csv.gz")
            gg[v], sett[v] = d, w
            e = te.esame(w, btc_w, inizio=se.INIZIO, anni_pieni=se.ANNI_PIENI)
            e["t"] = e["intero"]["sharpe"] * math.sqrt(e["intero"]["settimane"] / 52)
            out[v] = {"esame": e, "ev": ev}
            prove.registra(ID, v, par, "giornaliera, esame sulle settimane", len(d),
                           {"annuo_capitale": e["intero"]["annuo"], "sharpe": e["intero"]["sharpe"], "t": e["t"], "discesa": e["intero"]["discesa_max"],
                            "per_anno": e["per_anno"], "liquidazioni": len(ev["liquidazioni"]), "rifornimenti": ev["rifornimenti"]},
                           "calcolata", "bootstrap interno di terza.esame; deterministico; liquidazioni=%d" % len(ev["liquidazioni"]))
        except Exception:  # noqa: BLE001
            prove.registra(ID, v, par, "giornaliera", 0, {}, "errore", traceback.format_exc()[-300:])
            raise
    # Sharpe corretto
    cand = {f"161 {v}": {k: out[v]["esame"]["intero"][k] for k in ("sharpe", "asimmetria", "curtosi")} | {"settimane": out[v]["esame"]["intero"]["settimane"]}
            for v in varianti}
    corr = ast.corretto_famiglie({f"161 {v}": sett[v]["netto"] for v in varianti}, cand)
    # controlli descrittivi
    lun22 = pr.lunedi_del_giorno(np.array([sc.giorno(2022, 1, 3)]))[0]
    desc = {"filtri_usati": filtri_usati, "ore_mark_riempite": {s: h["mark_riempite"] for s, h in zip(MONETE, H)},
            "ore_ancora_vuote": {s: h["ancora_vuote"] for s, h in zip(MONETE, H)}}
    for v, N in varianti.items():
        d, w, e, ev = gg[v], sett[v], out[v]["esame"], out[v]["ev"]
        c = corr["candidate"][f"161 {v}"]
        e["sharpe_corretto"], e["gruppo"] = c["corretto"], c["gruppo"]
        r = d["netto"].to_numpy()
        anni_tot = len(d) / 365.0
        wr = w["netto"]
        w22 = wr[wr.index >= lun22]
        mesi = pd.to_datetime(d.index.to_numpy() * 86400, unit="s")
        eq = pd.Series(np.cumprod(1 + r) * CAPITALE, index=mesi)
        em = eq.groupby(eq.index.to_period("M")).last()
        inizio_m = pd.concat([pd.Series([CAPITALE]), em.iloc[:-1].reset_index(drop=True)]).to_numpy()
        mens = em.to_numpy() / inizio_m - 1
        anno = mesi.year
        per_anno = {}
        for y in sorted(set(anno)):
            k = anno == y
            e0 = float(d["patrimonio_apertura"][k].iloc[0]); e1 = float(eq[k].iloc[-1])
            per_anno[int(y)] = {"rendimento_pct": 100 * (e1 / e0 - 1), "funding_usdt": float(d["funding_usdt"][k].sum()), "base_usdt": float(d["base_usdt"][k].sum()),
                                "spese_usdt": float(d["spese_usdt"][k].sum()), "rifornimento_usdt": float(d["rifornimento_usdt"][k].sum()),
                                "rifornimenti": int(d["rifornimenti"][k].sum()), "netto_usdt": float(d["netto_usdt"][k].sum()),
                                "funding_BTC": float(d["funding_usdt_BTC"][k].sum()), "funding_ETH": float(d["funding_usdt_ETH"][k].sum())}
        fuori = d[["dentro_BTC", "dentro_ETH"]].sum(axis=1) == 0
        sd22 = float(w22.std(ddof=1))
        cond = {"netto_positivo": bool(e["intero"]["annuo"] > 0), "ogni_anno_positivo": bool(all(x > 0 for x in e["per_anno"].values())),
                "t_almeno_3": bool(e["t"] >= 3), "sharpe_corretto_almeno_0_80": bool(c["corretto"] >= 0.80),
                "nessuna_liquidazione": bool(len(ev["liquidazioni"]) == 0)}
        e["condizioni"] = cond
        corr_w = lambda x, y_: float(pd.concat([x, y_], axis=1, join="inner").corr().iloc[0, 1])  # noqa: E731
        f157 = pd.read_csv(QUI / "risultati_novantacinquesima" / f"settimane_{v}.csv.gz", index_col=0)["netto"]
        desc[v] = {
            "annuo_capitale_media52": e["intero"]["annuo"], "annuo_capitale_composto": cagr(r, anni_tot), "usdt_su_1000_media52": e["intero"]["annuo"] * 1000,
            "usdt_su_1000_composto": cagr(r, anni_tot) * 1000, "patrimonio_finale_su_1000": float(eq.iloc[-1]),
            "dal_2022": {"settimane": int(len(w22)), "annuo_media52": float(w22.mean() * 52), "composto": float(np.prod(1 + w22.to_numpy()) ** (52 / len(w22)) - 1),
                         "sharpe": float(w22.mean() / sd22 * math.sqrt(52)), "usdt_su_1000_media52": float(w22.mean() * 52 * 1000)},
            "volatilita": e["intero"]["volatilita"], "sharpe": e["intero"]["sharpe"], "t": e["t"], "sharpe_corretto": c["corretto"], "famiglie": corr["famiglie"],
            "gruppo": c["gruppo"], "discesa_giornaliera": dd(r), "discesa_settimanale": e["intero"]["discesa_max"], "peggiore_settimana": float(wr.min()),
            "mesi_positivi": int((mens > 0).sum()), "mesi": int(len(mens)),
            "giorni": {"positivi": int(((d["netto"] > 0) & ~fuori).sum()), "fuori": int(fuori.sum()), "dentro_negativi": int(((d["netto"] <= 0) & ~fuori).sum())},
            "per_anno_calendario": per_anno, "per_anno_esame_settimane": e["per_anno"], "condizioni": cond,
            "passa_quattro_condizioni": bool(all(cond[k] for k in list(cond)[:4])), "passa_con_nessuna_liquidazione": bool(all(cond.values())),
            "liquidazioni": ev["liquidazioni"], "n_liquidazioni": len(ev["liquidazioni"]),
            "rifornimenti": {"BTC": ev["rifornimenti"][0], "ETH": ev["rifornimenti"][1]}, "rifornimento_usdt_totale": float(d["rifornimento_usdt"].sum()),
            "ingressi": ev["ingressi"], "giorni_dentro": {s[:3]: int(d[f"dentro_{s[:3]}"].sum()) for s in MONETE},
            "margine_apertura_minimo": ev["margine_apertura_min"], "leva_max_apertura": ev["leva_max"], "aperture_leva_oltre_5": ev["aperture_leva_oltre_5"],
            "salita_max_pronti_in_posizione": ev["salita_max_pronti"], "nozionale_max_su_iniziale": ev["nozionale_max_su_iniziale"],
            "quota_riforn_max_su_Q": ev["x_max_su_Q"], "costo_medio_annuo_capitale": float(d["spese"].mean() * 365),
            "costi_doppi_annuo": e["costi_doppi"], "per_trimestre_positivi": {y: sum(1 for q in range(1, 5) if e["per_trimestre"][f"{y}T{q}"] > 0) for y in se.ANNI_PIENI},
            "corr_G1_giorni": float(pd.concat([d["netto"], g1], axis=1, join="inner").corr().iloc[0, 1]),
            "corr_BTC_giorni": float(pd.concat([d["netto"], btc_g], axis=1, join="inner").corr().iloc[0, 1]),
            "corr_G1_settimane": corr_w(wr, g1w), "corr_97CC_settimane": corr_w(wr, cc), "corr_157_settimane": corr_w(wr, f157),
            "corr_BTC_settimane": corr_w(wr, btc_w), "annuo_157_stesse_settimane": float(f157.mean() * 52),
        }
        # controlli descrittivi con le stesse serie
        dl, evl = simula(S, H, segnali(N), a, b, t0, CP_LIM, CS_LIM)
        dp, evp = simula(S, H, segnali(N), a, b, t0, cp_std, CS_STD, passi=passi)
        da, eva = simula(S, H, np.ones((b - a + 1, 2), bool), a, b, t0, cp_std, CS_STD)
        dap, evap = simula(S, H, np.ones((b - a + 1, 2), bool), a, b, t0, cp_std, CS_STD, passi=passi)
        ann = len(d) / 365.0
        desc[v]["controlli"] = {
            "ordini_limite": {"annuo_composto": cagr(dl["netto"].to_numpy(), ann), "annuo_media52": float(settimane(dl)["netto"].mean() * 52),
                              "liquidazioni": len(evl["liquidazioni"])},
            "passi_veri_1000_USDT": {"annuo_composto": cagr(dp["netto"].to_numpy(), ann), "annuo_media52": float(settimane(dp)["netto"].mean() * 52),
                                     "liquidazioni": len(evp["liquidazioni"]), "rifornimenti": evp["rifornimenti"], "ingressi_bloccati": evp["ingressi_bloccati"],
                                     "ingressi": evp["ingressi"]},
            "sempre_dentro": {"annuo_composto": cagr(da["netto"].to_numpy(), ann), "annuo_media52": float(settimane(da)["netto"].mean() * 52),
                              "sharpe": float(settimane(da)["netto"].mean() / settimane(da)["netto"].std(ddof=1) * math.sqrt(52)),
                              "liquidazioni": len(eva["liquidazioni"]), "rifornimenti": eva["rifornimenti"], "ingressi": eva["ingressi"]},
            "sempre_dentro_passi_veri": {"annuo_composto": cagr(dap["netto"].to_numpy(), ann), "liquidazioni": len(evap["liquidazioni"]),
                                         "ingressi_bloccati": evap["ingressi_bloccati"], "rifornimenti": evap["rifornimenti"]},
        }
        dl.to_csv(RIS / f"giorni_{v}_limite.csv.gz"); dp.to_csv(RIS / f"giorni_{v}_passi1000.csv.gz")
    # soglia di capitale per la gamba del Bitcoin
    pb = passi[0]
    soglie = {}
    for nome, prezzo in (("4_ottobre_2026", float(Op[b, 0])), ("massimo_periodo", float(np.nanmax(Op[a:b + 1, 0])))):
        qmin = max(pb[1], math.ceil(pb[2] / prezzo / pb[0] - 1e-9) * pb[0])
        qmin = math.ceil(qmin / pb[0] - 1e-9) * pb[0]
        cap_moneta = qmin * (prezzo * (1 + CS_STD) + MARGINE_INGRESSO * prezzo)
        soglie[nome] = {"prezzo": prezzo, "quantita_minima": qmin, "capitale_moneta": cap_moneta, "capitale_totale_due_monete": 2 * cap_moneta}
    desc["soglia_capitale_gamba_bitcoin"] = soglie
    (RIS / "esame.json").write_text(json.dumps(desc, ensure_ascii=False, indent=1, default=float), encoding="utf-8")
    pc = lambda x: f"{100 * x:+.2f}%"  # noqa: E731
    for v in varianti:
        x = desc[v]
        log(f"{v}: anno {pc(x['annuo_capitale_composto'])} (media52 {pc(x['annuo_capitale_media52'])}), dal 2022 {pc(x['dal_2022']['annuo_media52'])}, Sharpe {x['sharpe']:.2f}, "
            f"t {x['t']:.2f}, disc {pc(x['discesa_settimanale'])}, corretto {x['sharpe_corretto']:.2f}, liq {x['n_liquidazioni']}, rif {x['rifornimenti']}, 4 cond {x['passa_quattro_condizioni']}")
    return desc


if __name__ == "__main__":
    esegui()
