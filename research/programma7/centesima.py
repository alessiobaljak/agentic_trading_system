"""Prova 162 (CENTESIMA.md + «Chiusura della verifica»): il funding fra il perpetuo in USDT e quello in USDC della stessa moneta.
Solo le varianti A (30 giorni, soglia 0,006% al giorno, decisione il primo del mese) e B (7 giorni, 0,015%, il lunedi').
Dati: solo quelli scaricati da centesima_dati.py (data.binance.vision). Il motore dei costi e' quello delle regole (commissione 0,05% a
mercato piu' scarto 0,01% su BTC, ETH, SOL e 0,02% sulle altre, per gamba); lo scarto del USDC e' uguale a quello del USDT (limite).

Uso: python3 -m research.programma7.centesima
"""
from __future__ import annotations

import io
import json
import math
import traceback
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd

from research.programma5.strumenti import motore5 as m5
from research.programma6 import asticella as ast
from research.programma6 import seconda as sc
from research.programma6 import terza as te
from research.programma7 import centesima_dati as dat
from research.src import prove
from research.src.dati import funding_da_zip

QUI = Path(__file__).parent
RIS = QUI / "risultati_centesima"
ID = "centesima"
DAY = 86_400_000
DAY0 = sc.giorno(2024, 1, 1)
DAYN = sc.giorno(2026, 11, 1)             # esclusivo
NG = DAYN - DAY0 + 1
ULTIMO = sc.giorno(2026, 10, 30) - DAY0   # ultimo giorno D (indice)
NH = NG * 24
COMM, COMM_LIM = 0.0005, 0.0002
MIN_STORIA = 30
SOGLIA_RISCHIO, MMR = 0.10, 0.005
VARIANTI = {"A": {"L": 30, "theta": 0.00006, "decisione": "primo del mese"},
            "B": {"L": 7, "theta": 0.00015, "decisione": "lunedi"}}


# ----------------------------------------------------------------------------------------------------------------------
def leggi_zip(f: Path) -> pd.DataFrame:
    with zipfile.ZipFile(f) as z:
        g = z.read(z.namelist()[0])
    d = pd.read_csv(io.BytesIO(g), header=0 if g[:1].isalpha() else None).iloc[:, :6]
    d.columns = ["t", "open", "high", "low", "close", "volume"]
    t = pd.to_numeric(d["t"])
    d["t"] = t.where(t < 10 ** 14, t // 1000)
    return d


def serie_tempo(tipo: str, s: str, passo_ms: int, n: int, t0_ms: int) -> np.ndarray:
    out = np.full(n, np.nan)
    for f in sorted((dat.DATI / tipo / s).glob("*.zip")):
        d = leggi_zip(f)
        k = ((d["t"].to_numpy() - t0_ms) // passo_ms).astype(int)
        ok = (k >= 0) & (k < n)
        out[k[ok]] = d["open"].to_numpy(float)[ok]
    return out


def contratto(s: str) -> dict:
    t0 = DAY0 * DAY
    d1 = serie_tempo("d1", s, DAY, NG, t0)
    mk = serie_tempo("mark1h", s, 3_600_000, NH, t0)
    kh = serie_tempo("k1h", s, 3_600_000, NH, t0)
    manc_mark = int(np.isnan(mk).sum())
    riempite = int((np.isnan(mk) & ~np.isnan(kh)).sum())
    mk = np.where(np.isnan(mk), kh, mk)
    righe = []
    for p in sorted((dat.DATI / "funding" / s).glob("*.zip")):
        righe += funding_da_zip(p)
    R = pd.DataFrame(righe, columns=["ts", "ore", "tasso"]).drop_duplicates("ts")
    ts = np.round(R["ts"].to_numpy() / 60000.0).astype(np.int64) * 60000        # al minuto piu' vicino (scarti di pochi ms)
    ta = R["tasso"].to_numpy(float)
    f_sig = np.zeros(NG); n_sig = np.zeros(NG); f_ret = np.zeros(NG); f_h = np.zeros(NH)
    i = ts // DAY - DAY0
    ok = (i >= 0) & (i < NG)
    np.add.at(f_sig, i[ok], ta[ok]); np.add.at(n_sig, i[ok], 1)
    i = (ts - 1) // DAY - DAY0
    ok = (i >= 0) & (i < NG)
    np.add.at(f_ret, i[ok], ta[ok])
    h = -((-ts) // 3_600_000) - DAY0 * 24                                        # ora intera dal pagamento (arrotondata in su)
    ok = (h >= 0) & (h < NH)
    np.add.at(f_h, h[ok], ta[ok])
    return {"d1": d1, "mark": mk, "f_sig": f_sig, "n_sig": n_sig, "f_ret": f_ret, "f_h": f_h, "ore_mark_mancanti_prima_del_riempimento": manc_mark,
            "ore_riempite_dal_prezzo_scambiato": riempite, "ore_ancora_vuote": int(np.isnan(mk).sum())}


def carica_tutto() -> dict:
    P = {}
    for b in dat.BASI:
        T, C = contratto(b + "USDT"), contratto(b + "USDC")
        P[b] = {"T": T, "C": C}
    return P


def prepara(P: dict, L: int, theta: float) -> dict:
    """Per ogni moneta: indicatori giornalieri (segnale per ogni giorno, vivo, storia)."""
    out = {}
    for b, x in P.items():
        T, C = x["T"], x["C"]
        okf = (T["n_sig"] > 0) & (C["n_sig"] > 0)
        okc = np.isfinite(T["d1"]) & np.isfinite(C["d1"])
        valido = okf & okc
        hist = np.concatenate([[0], np.cumsum(valido)[:-1]])                    # giorni validi strettamente prima di i
        dd = np.where(okf, T["f_sig"] - C["f_sig"], np.nan)
        # ultimo giorno con candela e funding per tutti e due
        ul_c = int(np.flatnonzero(okc).max()) if okc.any() else -1
        ul_f = int(min(np.flatnonzero(T["n_sig"] > 0).max(), np.flatnonzero(C["n_sig"] > 0).max())) if okf.any() else -1
        idx = np.arange(NG)
        alive = np.zeros(NG, bool)
        nxt = np.concatenate([okc[1:], [False]])
        alive = okc & nxt & (idx <= ul_f)
        cs = np.concatenate([[0], np.cumsum(okf)])
        cd = np.concatenate([[0], np.cumsum(np.nan_to_num(dd))])
        finestra_ok = np.zeros(NG, bool); d_med = np.full(NG, np.nan)
        for i in range(L, NG):
            if cs[i] - cs[i - L] == L:
                finestra_ok[i] = True
                d_med[i] = (cd[i] - cd[i - L]) / L
        base = alive & (hist >= MIN_STORIA)
        sig = np.zeros(NG, int)
        sig[base & finestra_ok & (d_med > theta)] = 1
        sig[base & finestra_ok & (d_med < -theta)] = -1
        out[b] = {"sig": sig, "alive": alive, "base": base, "finestra_ok": finestra_ok, "d_med": d_med, "hist": hist, "dd": dd,
                  "primo_utile": int(np.flatnonzero(hist >= MIN_STORIA)[0]) if (hist >= MIN_STORIA).any() else -1,
                  "ultimo_candele": ul_c, "ultimo_funding": ul_f}
    return out


def costo_gamba(b: str, comm: float) -> float:
    return comm + m5.scarto(b + "USDT")


def e_decisione(var: str, i: int) -> bool:
    g = DAY0 + i
    if var == "A":
        return pd.Timestamp(g * 86400, unit="s").day == 1
    return (g + 3) % 7 == 0


# ----------------------------------------------------------------------------------------------------------------------
def simula(P: dict, var: str, escludi=(), comm: float = COMM) -> dict:
    v = VARIANTI[var]
    Q = prepara(P, v["L"], v["theta"])
    basi = [b for b in dat.BASI if b not in escludi]
    nb = len(basi)
    sw = np.zeros((nb, NG))
    side = np.zeros(nb, int); wdec = 0.0
    ret = np.zeros(NG); fnd = np.zeros(NG); spe = np.zeros(NG); contrib = np.zeros((nb, NG))
    decisioni = []; ferme_finestra = 0; cambi_lato = 0; ingressi = 0; chiusure_forzate = []; ferme_soglia = 0
    sw_prima = np.zeros(nb)
    inizio = None
    for i in range(0, ULTIMO + 1):
        dec = e_decisione(var, i)
        if dec:
            nuovo = np.array([Q[b]["sig"][i] for b in basi])
            for k, b in enumerate(basi):
                q = Q[b]
                if q["base"][i] and not q["finestra_ok"][i]:
                    ferme_finestra += 1
                elif q["base"][i] and nuovo[k] == 0:
                    ferme_soglia += 1
            cambi_lato += int(((nuovo * side) < 0).sum())
            ingressi += int(((nuovo != 0) & (side == 0)).sum())
            side = nuovo
            n = int((side != 0).sum())
            wdec = 1.0 / n if n else 0.0
            decisioni.append(i)
        cur = np.zeros(nb)
        for k, b in enumerate(basi):
            if side[k] != 0:
                if Q[b]["alive"][i]:
                    cur[k] = side[k] * wdec
                else:
                    chiusure_forzate.append((b, dat_giorno(i)))
                    side[k] = 0
        if inizio is None:
            if (cur != 0).any():
                inizio = i
            else:
                sw_prima = cur
                continue
        sw[:, i] = cur
        for k, b in enumerate(basi):
            x = P[b]
            rc = x["C"]["d1"][i + 1] / x["C"]["d1"][i] - 1 if cur[k] != 0 else 0.0
            rt = x["T"]["d1"][i + 1] / x["T"]["d1"][i] - 1 if cur[k] != 0 else 0.0
            lordo = cur[k] * (rc - rt)
            f = cur[k] * (x["T"]["f_ret"][i] - x["C"]["f_ret"][i])
            s = costo_gamba(b, comm) * 2 * abs(cur[k] - sw_prima[k])
            ret[i] += lordo; fnd[i] += f; spe[i] += s
            contrib[k, i] = lordo + f - s
        sw_prima = cur
    giorni = np.arange(inizio, ULTIMO + 1)
    d = pd.DataFrame({"lordo": ret[inizio:ULTIMO + 1], "funding": fnd[inizio:ULTIMO + 1], "spese": spe[inizio:ULTIMO + 1]}, index=giorni + DAY0)
    d["netto"] = d["lordo"] + d["funding"] - d["spese"]
    d["monete"] = (sw[:, inizio:ULTIMO + 1] != 0).sum(0)
    return {"d": d, "sw": sw, "basi": basi, "Q": Q, "contrib": contrib, "decisioni": decisioni, "inizio": inizio,
            "ferme_finestra": ferme_finestra, "ferme_soglia": ferme_soglia, "cambi_lato": cambi_lato, "ingressi": ingressi,
            "chiusure_forzate": chiusure_forzate, "spese_giorno": spe}


def dat_giorno(i: int) -> str:
    return sc.data(DAY0 + i)


# ----------------------------------------------------------------------------------------------------------------------
def margine(P: dict, r: dict, comm: float = COMM) -> dict:
    """Margine in comune (regola principale) e gamba isolata (descrittiva), con prezzo mark a 1 ora."""
    sw, basi, dec = r["sw"], r["basi"], r["decisioni"] + [ULTIMO + 1]
    nbasi = len(basi)
    spe = r["spese_giorno"]
    rischio = {}; liq = {}; iso_rischio = {}; iso_liq = {}
    lev_max = 0.0; eq_min = 9.9; base_max = {"valore": 0.0}
    mk = {b: (P[b]["T"]["mark"], P[b]["C"]["mark"]) for b in basi}
    f_h = {b: (P[b]["T"]["f_h"], P[b]["C"]["f_h"]) for b in basi}
    for j in range(len(dec) - 1):
        i0, i1 = dec[j], dec[j + 1]
        if i0 < r["inizio"]:
            i0 = r["inizio"]
            if i0 >= i1:
                continue
        h0, h1 = i0 * 24, i1 * 24
        nh = h1 - h0
        eq = np.ones(nh) - spe[i0]
        notional = np.zeros(nh)
        iso_r = np.zeros(nh, bool); iso_l = np.zeros(nh, bool)
        any_pos = False
        for k, b in enumerate(basi):
            s0 = sw[k, i0]
            if s0 == 0:
                continue
            any_pos = True
            w, s = abs(s0), (1 if s0 > 0 else -1)
            ex = next((i for i in range(i0, i1) if sw[k, i] == 0), None)
            he = (ex * 24 - h0) if ex is not None else nh              # ore (relative) in cui la gamba e' viva: [0, he)
            T, C = mk[b]
            def rid(a):
                z = a[h0:h1 + 1].copy()
                nn = np.isnan(z)
                if nn.any():
                    z = pd.Series(z).ffill().bfill().to_numpy()
                return z
            Tz, Cz = rid(T), rid(C)
            xT, xC = Tz[:nh] / Tz[0], Cz[:nh] / Cz[0]
            fa = np.zeros(nh)
            fT, fC = f_h[b]
            fa = np.cumsum(w * s * (fT[h0 + 1:h1 + 1][:nh] - fC[h0 + 1:h1 + 1][:nh]))      # pagamenti con ora in (h0, h]
            pnl = w * s * ((xC - 1) - (xT - 1))
            if he < nh:
                pnl[he:] = pnl[he]
                fa[he:] = fa[he - 1] if he > 0 else 0
                # all'uscita (apertura del giorno ex) si paga la chiusura delle due gambe
                eq[he:] -= costo_gamba(b, comm) * 2 * w
                notional_k = np.where(np.arange(nh) < he, w * (xC + xT), 0.0)
            else:
                notional_k = w * (xC + xT)
            eq += pnl + fa
            notional += notional_k
            viva = np.arange(nh) < he
            # gamba isolata: margine 50% del valore iniziale +- la sola gamba; a rischio se sotto il 10% del valore corrente
            xl, xs = (xC, xT) if s > 0 else (xT, xC)
            ml, ms = 0.5 * w + w * (xl - 1), 0.5 * w - w * (xs - 1)
            vl, vs = w * xl, w * xs
            iso_r |= viva & ((ml < SOGLIA_RISCHIO * vl) | (ms < SOGLIA_RISCHIO * vs))
            iso_l |= viva & ((ml < MMR * vl) | (ms < MMR * vs))
            base = np.abs(Cz[:nh] / Tz[:nh] - 1)
            bm = float(np.max(np.where(viva, base, 0)))
            if bm > base_max["valore"]:
                base_max = {"valore": bm, "moneta": b, "giorno": dat_giorno(i0)}
        if not any_pos:
            continue
        a_r = eq < SOGLIA_RISCHIO
        a_l = eq < MMR * np.maximum(notional, 1e-12)
        a_l &= notional > 0
        with np.errstate(divide="ignore", invalid="ignore"):
            lv = np.where(eq > 0, notional / eq, np.inf)
        lev_max = max(lev_max, float(np.max(lv[notional > 0]))) if (notional > 0).any() else lev_max
        eq_min = min(eq_min, float(eq[notional > 0].min()) if (notional > 0).any() else eq_min)
        for d in range(i0, i1):
            s_ = slice((d - i0) * 24, (d - i0) * 24 + 24)
            rischio[d] = bool(a_r[s_].any()); liq[d] = bool(a_l[s_].any())
            iso_rischio[d] = bool(iso_r[s_].any()); iso_liq[d] = bool(iso_l[s_].any())
    return {"giorni_a_rischio": sorted(d + DAY0 for d, x in rischio.items() if x), "giorni_liquidati": sorted(d + DAY0 for d, x in liq.items() if x),
            "gamba_isolata_a_rischio": int(sum(iso_rischio.values())), "gamba_isolata_liquidata": int(sum(iso_liq.values())),
            "giorni_con_posizione": int(len(rischio)), "leva_massima_conto": lev_max, "equity_minima": eq_min, "base_massima": base_max}


# ----------------------------------------------------------------------------------------------------------------------
def settimanale(d: pd.DataFrame) -> pd.DataFrame:
    g = d.groupby(ast._lunedi(d.index))
    w = pd.DataFrame({"netto": g["netto"].sum(), "spese": g["spese"].sum(), "funding": g["funding"].sum(), "monete": g["monete"].max()})
    return w


def numeri(d: pd.DataFrame, w: pd.DataFrame) -> dict:
    wp = ast.periodo(w["netto"])
    n = te.numeri_settimana(wp)
    r = d["netto"].to_numpy()
    anno = pd.to_datetime(d.index.to_numpy() * 86400, unit="s").year
    per_anno = {int(a): float(r[anno == a].mean() * 365) for a in sorted(set(anno))}
    return {"giorni": int(len(d)), "annuo_capitale": float(r.mean() * 365), "per_anno": per_anno,
            "sharpe_settimane": n["sharpe"], "settimane": n["settimane"], "t": n["sharpe"] * math.sqrt(n["settimane"] / 52),
            "asimmetria": n["asimmetria"], "curtosi": n["curtosi"], "discesa_settimanale": n["discesa_max"],
            "discesa_giornaliera": float((np.cumprod(1 + r) / np.maximum.accumulate(np.cumprod(1 + r)) - 1).min()),
            "sharpe_365_giorni_fino_30_ottobre": float(r.mean() / r.std(ddof=1) * math.sqrt(365)) if r.std() > 0 else 0.0,
            "costo_medio_annuo_capitale": float(d["spese"].mean() * 365), "funding_annuo": float(d["funding"].mean() * 365),
            "lordo_prezzo_annuo": float(d["lordo"].mean() * 365), "giorni_fermi": int((d["monete"] == 0).sum()),
            "monete_medie_in_posizione": float(d["monete"].mean()), "primo_giorno": sc.data(int(d.index[0])), "ultimo_giorno": sc.data(int(d.index[-1])),
            "periodo_esame_dal": sc.data(int(wp.index[0])), "periodo_esame_al": sc.data(int(wp.index[-1]))}


def persistenza(Q: dict, basi) -> dict:
    stessa = opposta = ferma = 0
    for b in basi:
        s = Q[b]["sig"]
        for i in range(0, ULTIMO + 1 - 30):
            if s[i] != 0:
                if s[i + 30] == s[i]:
                    stessa += 1
                elif s[i + 30] == -s[i]:
                    opposta += 1
                else:
                    ferma += 1
    tot = stessa + opposta + ferma
    return {"coppie_moneta_giorno": tot, "stessa_segnalazione": stessa / tot if tot else None, "opposta": opposta / tot if tot else None,
            "ferma_dopo": ferma / tot if tot else None}


def d_per_anno_e_moneta(P: dict) -> dict:
    out = {}
    for b, x in P.items():
        okf = (x["T"]["n_sig"] > 0) & (x["C"]["n_sig"] > 0)
        dd = np.where(okf, x["T"]["f_sig"] - x["C"]["f_sig"], np.nan)
        anni = pd.to_datetime((np.arange(NG) + DAY0) * 86400, unit="s").year
        out[b] = {int(a): (float(np.nanmean(dd[anni == a]) * 100) if np.isfinite(dd[anni == a]).any() else None) for a in (2024, 2025, 2026)}
    return out


def distribuzione_base(P: dict) -> dict:
    v = []
    per_moneta = {}
    for b, x in P.items():
        T, C = x["T"]["mark"], x["C"]["mark"]
        ok = np.isfinite(T) & np.isfinite(C)
        z = (C[ok] / T[ok] - 1)
        v.append(z)
        per_moneta[b] = {"ore": int(ok.sum()), "assoluta_massima_pct": float(100 * np.abs(z).max()) if len(z) else None}
    z = np.concatenate(v)
    q = np.percentile(z, [0.1, 1, 5, 25, 50, 75, 95, 99, 99.9])
    return {"ore_coppia": int(len(z)), "percentili_pct_0.1_1_5_25_50_75_95_99_99.9": [float(100 * a) for a in q],
            "assoluta_massima_pct": float(100 * np.abs(z).max()), "quota_ore_sopra_0.5pct": float((np.abs(z) > 0.005).mean()),
            "quota_ore_sopra_1pct": float((np.abs(z) > 0.01).mean()), "per_moneta_max_pct": {b: m["assoluta_massima_pct"] for b, m in per_moneta.items()}}


def pc(x):
    return f"{100 * x:+.2f}%"


def esegui(log=print) -> dict:
    RIS.mkdir(exist_ok=True)
    P = carica_tutto()
    qualita = {b: {"T": {k: P[b]["T"][k] for k in ("ore_mark_mancanti_prima_del_riempimento", "ore_riempite_dal_prezzo_scambiato", "ore_ancora_vuote")},
                   "C": {k: P[b]["C"][k] for k in ("ore_mark_mancanti_prima_del_riempimento", "ore_riempite_dal_prezzo_scambiato", "ore_ancora_vuote")}}
               for b in dat.BASI}
    res, serie_w = {}, {}
    out = {"qualita_dati_mark": qualita}
    for v, par in VARIANTI.items():
        parametri = {"L": par["L"], "theta_giorno": par["theta"], "decisione": par["decisione"], "commissione": COMM, "scarto": "0,01% BTC ETH SOL, 0,02% altre",
                     "periodo": "2024-01 .. 2026-10-30", "universo": len(dat.BASI), "margine_rischio": SOGLIA_RISCHIO, "mantenimento": MMR}
        try:
            r = simula(P, v)
            d = r["d"]; w = settimanale(d)
            d.to_csv(RIS / f"giorni_{v}.csv.gz"); w.to_csv(RIS / f"settimane_{v}.csv.gz")
            res[v] = {"r": r, "d": d, "w": w, "num": numeri(d, w)}
            serie_w[v] = w["netto"]
        except Exception:  # noqa: BLE001
            prove.registra(ID, v, parametri, "giornaliera, esame sulle settimane", 0, {}, "errore", traceback.format_exc()[-300:])
            raise
    cand = {f"162 {v}": {"sharpe": res[v]["num"]["sharpe_settimane"], "settimane": res[v]["num"]["settimane"], "asimmetria": res[v]["num"]["asimmetria"],
                         "curtosi": res[v]["num"]["curtosi"]} for v in VARIANTI}
    corr = ast.corretto_famiglie({f"162 {v}": serie_w[v] for v in VARIANTI}, cand)
    g1d = pd.read_csv(QUI / "risultati_prima" / "giorni_G1.csv.gz")["netto"]
    g1d.index = np.arange(sc.giorno(2021, 1, 4), sc.giorno(2021, 1, 4) + len(g1d))
    g1w = pd.read_csv(QUI / "risultati_prima" / "settimane_G1.csv.gz", index_col=0)["netto"]
    out["famiglie"] = {"serie_nel_mazzo": corr["serie"], "famiglie": corr["famiglie"], "in_v": corr["in_v"], "deviazione_v": corr["deviazione_v"]}
    out["base_prezzi"] = distribuzione_base(P)
    out["d_media_pct_al_giorno_per_anno_e_moneta"] = d_per_anno_e_moneta(P)
    out["universo"] = {b: {"primo_mese_usdc": dat.PRIMO_MESE[b]} for b in dat.BASI}
    for v in VARIANTI:
        r, d, w, num = res[v]["r"], res[v]["d"], res[v]["w"], res[v]["num"]
        m = margine(P, r)
        c = corr["candidate"][f"162 {v}"]
        for b in dat.BASI:
            q = r["Q"][b]
            out["universo"][b][f"primo_giorno_utile_{v}"] = sc.data(DAY0 + q["primo_utile"]) if q["primo_utile"] >= 0 else None
            out["universo"][b]["ultimo_giorno_candele_entrambi"] = sc.data(DAY0 + q["ultimo_candele"]) if q["ultimo_candele"] >= 0 else None
            out["universo"][b]["ultimo_giorno_funding_entrambi"] = sc.data(DAY0 + q["ultimo_funding"]) if q["ultimo_funding"] >= 0 else None
        cond = {"netto_positivo": bool(num["annuo_capitale"] > 0), "ogni_anno_positivo": bool(all(x > 0 for x in num["per_anno"].values())),
                "t_almeno_3": bool(num["t"] >= 3), "sharpe_corretto_almeno_0_80": bool(c["corretto"] >= 0.80),
                "margine_mai_a_rischio": bool(len(m["giorni_a_rischio"]) == 0)}
        passa = all(cond.values())
        poco = bool(num["annuo_capitale"] < 0.03)
        esito = "passa" if (passa and not poco) else ("non promosso per poco valore" if (passa and poco) else "non passa")
        # controlli descrittivi
        rl = simula(P, v, comm=COMM_LIM); dl = rl["d"]; wl = settimanale(dl)
        contributo = pd.Series(r["contrib"].sum(1), index=r["basi"]).sort_values(ascending=False)
        migliore = contributo.index[0]
        rs = simula(P, v, escludi=(migliore,)); ds = rs["d"]; ws = settimanale(ds)
        nl, ns = numeri(dl, wl), numeri(ds, ws)
        wp = ast.periodo(w["netto"])
        com = pd.concat([wp, g1w], axis=1, join="inner").dropna()
        com.columns = ["x", "g1"]
        dcom = pd.concat([d["netto"], g1d], axis=1, join="inner").dropna()
        mix = 0.8 * com["g1"] + 0.2 * com["x"]
        dec_n = [(int((r["sw"][:, i] != 0).sum())) for i in r["decisioni"] if i >= r["inizio"]]
        extra = {"corr_G1_giorni": float(dcom.corr().iloc[0, 1]), "corr_G1_settimane": float(com.corr().iloc[0, 1]), "settimane_comuni_G1": int(len(com)),
                 "G1_stesse_settimane_annuo": float(com["g1"].mean() * 52), "G1_stesse_settimane_sharpe": float(com["g1"].mean() / com["g1"].std(ddof=1) * math.sqrt(52)),
                 "miscela_80_20_annuo": float(mix.mean() * 52), "miscela_80_20_sharpe": float(mix.mean() / mix.std(ddof=1) * math.sqrt(52))}
        ctrl = {"ordine_limite_0_02": {"annuo_capitale": nl["annuo_capitale"], "sharpe_settimane": nl["sharpe_settimane"], "t": nl["t"],
                                       "per_anno": nl["per_anno"]},
                "senza_la_moneta_migliore": {"moneta": migliore, "contributo_giornaliero_somma": float(contributo.iloc[0]), "annuo_capitale": ns["annuo_capitale"],
                                             "sharpe_settimane": ns["sharpe_settimane"], "per_anno": ns["per_anno"]},
                "contributo_per_moneta_somma_giornaliera_top5": {k: float(x) for k, x in contributo.head(5).items()},
                "contributo_per_moneta_peggiori3": {k: float(x) for k, x in contributo.tail(3).items()},
                "cambi_di_lato": r["cambi_lato"], "ingressi_o_riaperture": r["ingressi"], "decisioni": len([i for i in r["decisioni"] if i >= r["inizio"]]),
                "monete_non_ferme_per_decisione_media": float(np.mean(dec_n)) if dec_n else 0.0,
                "decisioni_con_moneta_ferma_per_giorno_senza_funding": r["ferme_finestra"], "decisioni_con_moneta_ferma_per_soglia": r["ferme_soglia"],
                "chiusure_forzate_contratto_finito_o_buco": r["chiusure_forzate"], "persistenza_30_giorni": persistenza(r["Q"], r["basi"]),
                "regola_gamba_isolata": {"giorni_a_rischio": m["gamba_isolata_a_rischio"], "giorni_liquidati": m["gamba_isolata_liquidata"]},
                "G1": extra}
        out[v] = {"numeri": num, "sharpe_corretto": c["corretto"], "gruppo": c["gruppo"], "condizioni": cond, "esito": esito, "margine_in_comune": m, "controlli": ctrl}
        prove.registra(ID, v, {"L": VARIANTI[v]["L"], "theta_giorno": VARIANTI[v]["theta"], "decisione": VARIANTI[v]["decisione"], "commissione": COMM,
                               "periodo": "2024-01 .. 2026-10-30", "universo": len(dat.BASI)}, "giornaliera, esame sulle settimane", num["giorni"],
                       {"annuo_capitale": num["annuo_capitale"], "per_anno": num["per_anno"], "sharpe": num["sharpe_settimane"], "t": num["t"],
                        "sharpe_corretto": c["corretto"], "discesa": num["discesa_settimanale"], "giorni_a_rischio": len(m["giorni_a_rischio"]),
                        "giorni_liquidati": len(m["giorni_liquidati"]), "costo_medio_annuo": num["costo_medio_annuo_capitale"]},
                       esito, "calcolata; deterministica (nessun seme); condizioni=%s" % json.dumps(cond))
    (RIS / "esame.json").write_text(json.dumps(out, ensure_ascii=False, indent=1, default=float), encoding="utf-8")
    for v in VARIANTI:
        x = out[v]
        n = x["numeri"]
        log(f"{v}: annuo {pc(n['annuo_capitale'])} per anno {{{', '.join(f'{k}: {pc(a)}' for k, a in n['per_anno'].items())}}} Sharpe {n['sharpe_settimane']:.2f} "
            f"t {n['t']:.2f} corretto {x['sharpe_corretto']:.2f} disc {pc(n['discesa_settimanale'])} rischio {len(x['margine_in_comune']['giorni_a_rischio'])} "
            f"liq {len(x['margine_in_comune']['giorni_liquidati'])} costo {pc(n['costo_medio_annuo_capitale'])} -> {x['esito']}")
    return out


if __name__ == "__main__":
    esegui()
