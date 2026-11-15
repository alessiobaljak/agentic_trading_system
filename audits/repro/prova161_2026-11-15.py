"""Audit della prova 161 (CM, funding coperto su BTC ed ETH con il margine vero), 15 novembre 2026. Solo lettura fuori da `audits/`.

Non chiama mai `novantanovesima.esegui` (riscrive risultati e registro delle varianti, voce 11 del catalogo): importa le funzioni.
Uso (dalla radice del repository):
  python3 -I audits/repro/prova161_2026-11-15.py dati          # orari, buchi, duplicati, funding regolamento per regolamento, stimati
  python3 -I audits/repro/prova161_2026-11-15.py rifai         # ricalcolo con il codice della prova, confronto con i file salvati
  python3 -I audits/repro/prova161_2026-11-15.py indipendente  # simulatore ora per ora scritto dall'auditor dalle regole
  python3 -I audits/repro/prova161_2026-11-15.py margine       # rialzi peggiori, giorni saltati, mantenimento, prezzo scambiato
  python3 -I audits/repro/prova161_2026-11-15.py sensi         # soglie, N, ritardo del segnale, costi (+-10%, +-20%)
  python3 -I audits/repro/prova161_2026-11-15.py misure        # concentrazione, 2021, dal 2022, clima, autocorrelazione, Sharpe corretto
  python3 -I audits/repro/prova161_2026-11-15.py filtri        # passi veri, valore minimo a pronti, capitale
Esiti in `audits/repro/prova161_2026-11-15_esito_<parte>.json`; a schermo poche righe.
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

RADICE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RADICE))

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from research.programma6 import asticella as ast  # noqa: E402
from research.programma6 import seconda as sc  # noqa: E402
from research.programma6 import sesta as se  # noqa: E402
from research.programma6 import terza as te  # noqa: E402
from research.programma7 import novantacinquesima as n95  # noqa: E402
from research.programma7 import novantanovesima as nv  # noqa: E402
from research.programma7 import novantanovesima_dati as dat  # noqa: E402
from research.programma7 import prima as pr  # noqa: E402
from research.programma7 import trentacinquesima as t35  # noqa: E402
from research.src.dati import funding_da_zip  # noqa: E402

QUI = Path(__file__).parent
ESITO = QUI / "prova161_2026-11-15_esito_{}.json"
MONETE = ("BTCUSDT", "ETHUSDT")
RIS = RADICE / "research" / "programma7" / "risultati_novantanovesima"
DUE = {"A": 30, "B": 90}


def salva(parte: str, x) -> None:
    ESITO.with_name(ESITO.name.format(parte)).write_text(json.dumps(x, ensure_ascii=False, indent=1, default=float), encoding="utf-8")


_CACHE: dict = {}


def base():
    """Pannello, pronti, ore (con il caricatore della prova), indici del periodo."""
    if "pan" in _CACHE:
        return _CACHE
    pan = sc.pannello()
    t0 = pan["t0"]
    n_p = pan["open"].shape[0]
    Op = t35.tabella_pronti(list(MONETE), t0, n_p)
    a, b = se.INIZIO - t0, pr.FINE - 1 - t0
    js = [pan["simboli"].index(s) for s in MONETE]
    H = [nv.ore_moneta(s, pan, j) for s, j in zip(MONETE, js)]
    cp = float(sc.costi_moneta(pan["simboli"])[js[0]])
    ps = te.pannello_settimane(pan, log=lambda x: None, indicatori_si=False)
    btc_w = pd.Series(ps["R"][:, pan["simboli"].index("BTCUSDT")], index=ps["lunedi"])
    _CACHE.update(pan=pan, t0=t0, Op=Op, a=a, b=b, js=js, H=H, cp=cp, btc_w=btc_w)
    return _CACHE


def segnali(N, ritardo=0):
    c = base()
    F = c["pan"]["funding"]
    a, b = c["a"], c["b"]
    return np.column_stack([n95.segnale(F[:, j], a - ritardo, b - ritardo, N) for j in c["js"]])


def numeri(d: pd.DataFrame) -> dict:
    c = base()
    w = nv.settimane(d)
    e = te.esame(w, c["btc_w"], inizio=se.INIZIO, anni_pieni=se.ANNI_PIENI)
    t = e["intero"]["sharpe"] * math.sqrt(e["intero"]["settimane"] / 52)
    r = d["netto"].to_numpy()
    lun22 = pr.lunedi_del_giorno(np.array([sc.giorno(2022, 1, 3)]))[0]
    w22 = w["netto"][w.index >= lun22]
    return {"annuo_media52": e["intero"]["annuo"], "composto": float(np.prod(1 + r) ** (365 / len(r)) - 1), "sharpe": e["intero"]["sharpe"],
            "t": t, "discesa": e["intero"]["discesa_max"], "per_anno": e["per_anno"],
            "dal_2022_media52": float(w22.mean() * 52), "dal_2022_sharpe": float(w22.mean() / w22.std(ddof=1) * math.sqrt(52)),
            "dal_2022_t": float(w22.mean() / w22.std(ddof=1) * math.sqrt(len(w22))),
            "finale_su_1000": float(np.prod(1 + r) * 1000), "settimane": int(len(w))}


# ---------------------------------------------------------------------------------------------------------------------------
# A. dati
# ---------------------------------------------------------------------------------------------------------------------------
def dati() -> dict:
    c = base()
    pan, t0, a, b, Op = c["pan"], c["t0"], c["a"], c["b"], c["Op"]
    out = {}
    h_da, h_a = (se.INIZIO - 1) * 24, (pr.FINE + 1) * 24        # dal 3 gennaio 2021 alle 00:00 del 6 ottobre 2026
    for s in MONETE:
        o = {}
        for tipo in ("mark1h", "perp1h"):
            fs = sorted((dat.DATI / tipo).glob(f"{s}-*.zip"))
            d = pd.concat([dat.leggi(f) for f in fs], ignore_index=True)
            hh = d["t"].to_numpy() // 3_600_000
            k = (hh >= h_da) & (hh < h_a)
            dd_ = d[k]
            ore = dd_["t"].to_numpy() // 3_600_000
            o[tipo] = {"righe": int(k.sum()), "duplicati": int(len(ore) - len(np.unique(ore))),
                       "fuori_ordine": int((np.diff(dd_["t"].to_numpy()) <= 0).sum()),
                       "non_allo_scoccare": int((dd_["t"].to_numpy() % 3_600_000 != 0).sum()),
                       "ore_mancanti": int(len(np.setdiff1d(np.arange(h_da, h_a), ore))),
                       "alto_sotto_apertura": int((dd_["high"].to_numpy(float) < dd_["open"].to_numpy(float) - 1e-9).sum()),
                       "valori_non_positivi": int((dd_[["open", "high"]].to_numpy(float) <= 0).sum())}
            o[tipo + "_serie"] = dd_.set_index(dd_["t"] // 3_600_000)[["open", "high"]].astype(float)
        m, p = o.pop("mark1h_serie"), o.pop("perp1h_serie")
        j = m.join(p, lsuffix="_m", rsuffix="_p", how="inner")
        rap = j["open_m"] / j["open_p"] - 1
        alto = j["high_m"] / j["open_m"] - 1
        o["mark_contro_scambiato_apertura"] = {"mediana": float(rap.median()), "p01": float(rap.quantile(0.001)), "p999": float(rap.quantile(0.999)),
                                               "oltre_1pct": int((rap.abs() > 0.01).sum()),
                                               "peggiori": {str(pd.Timestamp(int(i) * 3600, unit="s")): float(v) for i, v in rap.abs().nlargest(5).items()}}
        o["mark_alto_orario_su_apertura_max"] = {str(pd.Timestamp(int(i) * 3600, unit="s")): float(v) for i, v in alto.nlargest(5).items()}
        H = c["H"][MONETE.index(s)]
        o["ore_mark_riempite_dal_codice"] = H["mark_riempite"]; o["ore_ancora_vuote"] = H["ancora_vuote"]
        # pronti giornalieri
        jj = MONETE.index(s)
        S = Op[a:b + 2, jj]
        sp = pd.read_csv(t35.DATI / f"{s}.csv.gz")
        g = sp["giorno"].to_numpy()
        gk = g[(g >= se.INIZIO) & (g <= pr.FINE)]
        mo00 = np.array([H["mo"][(t + t0) * 24 - H["h0"]] for t in range(a, b + 2)])
        bas = S / mo00 - 1
        o["pronti"] = {"giorni_nel_periodo": int(len(gk)), "attesi": int(pr.FINE - se.INIZIO + 1), "nan_nel_periodo": int(np.isnan(S).sum()),
                       "duplicati": int(len(gk) - len(np.unique(gk))), "fuori_ordine": int((np.diff(g) <= 0).sum()),
                       "pronti_su_mark_00": {"mediana": float(np.median(bas)), "min": float(bas.min()), "max": float(bas.max()),
                                             "oltre_1pct": int((np.abs(bas) > 0.01).sum()),
                                             "peggiori": {sc.data(int(se.INIZIO + i)): float(bas[i]) for i in np.argsort(-np.abs(bas))[:5]}}}
        # funding regolamento per regolamento
        righe = []
        for f in sorted((sc.DATI / s / "funding").glob("*.zip")):
            righe += funding_da_zip(f)
        R = pd.DataFrame(righe, columns=["ts", "ore", "tasso"])
        dup = int(R.duplicated("ts").sum())
        R = R.drop_duplicates("ts").sort_values("ts")
        hr = R["ts"].to_numpy() // 3_600_000
        kk = (hr > (se.INIZIO) * 24) & (hr <= (pr.FINE) * 24)          # regolamenti tenuti: dalle 08 del 4 gennaio alle 00 del 5 ottobre
        Rk = R[kk]
        attesi = np.arange(se.INIZIO * 24 + 8, pr.FINE * 24 + 1, 8)
        oh = (Rk["ts"].to_numpy() // 3_600_000)
        resto = Rk["ts"].to_numpy() % 3_600_000
        o["funding"] = {"duplicati_file": dup, "regolamenti_nel_periodo": int(len(Rk)), "attesi_ogni_8_ore": int(len(attesi)),
                        "mancanti": [str(pd.Timestamp(int(x) * 3600, unit="s")) for x in np.setdiff1d(attesi, oh)][:20],
                        "n_mancanti": int(len(np.setdiff1d(attesi, oh))),
                        "fuori_dalle_00_08_16": int(((oh % 24) % 8 != 0).sum()), "ms_oltre_lo_scoccare_max": int(resto.max()),
                        "intervalli_diversi_da_8": int((Rk["ore"] != 8).sum()), "tasso_min": float(Rk["tasso"].min()), "tasso_max": float(Rk["tasso"].max()),
                        "quota_al_tasso_base_0_0001": float((np.abs(Rk["tasso"] - 0.0001) < 1e-9).mean()),
                        "quota_negativi": float((Rk["tasso"] < 0).mean())}
        # funding del pannello (segnale) contro il vero, nei giorni che il segnale legge (a-90 .. b)
        vero = sc.funding_giorni(s)
        jp = c["js"][jj]
        gg = np.arange(a - 90, b + 1)
        Fp = pan["funding"][gg, jp]
        Fv = vero.reindex(gg + t0).to_numpy()
        diff = np.abs(np.nan_to_num(Fv, nan=-9) - Fp)
        o["funding_pannello_contro_vero"] = {"giorni": int(len(gg)), "senza_vero": int(np.isnan(Fv).sum()), "diversi_1e12": int((diff > 1e-12).sum()),
                                             "esempi": {sc.data(int(gg[i] + t0)): [float(Fp[i]), None if np.isnan(Fv[i]) else float(Fv[i])]
                                                        for i in np.flatnonzero(diff > 1e-12)[:5]}}
        # buchi del 2022 dell'archivio giornaliero (voce 1) per il pannello delle due monete
        C = pan["close"][a:b + 2, jp]
        o["pannello_giorni_senza_candela_nel_periodo"] = [sc.data(int(se.INIZIO + i)) for i in np.flatnonzero(~np.isfinite(C))][:10]
        V = pan["quote_volume"][a:b + 2, jp]
        o["pannello_volume_zero"] = int((V == 0).sum())
        out[s] = o
    salva("dati", out)
    for s in MONETE:
        x = out[s]
        print(s, "mark", x["mark1h"], "\n   perp", x["perp1h"], "\n   pronti", {k: v for k, v in x["pronti"].items() if k != "pronti_su_mark_00"},
              "\n   funding", {k: v for k, v in x["funding"].items() if k not in ("mancanti",)}, "\n   pannello", x["funding_pannello_contro_vero"]["diversi_1e12"],
              x["funding_pannello_contro_vero"]["senza_vero"], x["pannello_giorni_senza_candela_nel_periodo"])
    return out


# ---------------------------------------------------------------------------------------------------------------------------
# F. ricalcolo con il codice della prova (senza esegui) e confronto con i file salvati
# ---------------------------------------------------------------------------------------------------------------------------
def conto(N=None, sig=None, cp=None, cs=nv.CS_STD, passi=None, **cambi):
    """nv.simula con le costanti del modulo cambiate per la durata della chiamata (sensibilita')."""
    c = base()
    vecchi = {k: getattr(nv, k) for k in cambi}
    try:
        for k, v in cambi.items():
            setattr(nv, k, v)
        s_ = sig if sig is not None else segnali(N)
        return nv.simula(c["Op"], c["H"], s_, c["a"], c["b"], c["t0"], c["cp"] if cp is None else cp, cs, passi=passi)
    finally:
        for k, v in vecchi.items():
            setattr(nv, k, v)


def rifai() -> dict:
    c = base()
    out = {}
    sett = {}
    for v, N in DUE.items():
        d, ev = conto(N)
        w = nv.settimane(d)
        sett[v] = w
        g0 = pd.read_csv(RIS / f"giorni_{v}.csv.gz", index_col=0)
        w0 = pd.read_csv(RIS / f"settimane_{v}.csv.gz", index_col=0)
        out[v] = {"numeri": numeri(d), "liquidazioni": len(ev["liquidazioni"]), "rifornimenti": ev["rifornimenti"], "ingressi": ev["ingressi"],
                  "margine_apertura_min": ev["margine_apertura_min"], "leva_max": ev["leva_max"],
                  "diff_max_giorni_netto": float(np.max(np.abs(g0["netto"].to_numpy() - d["netto"].to_numpy()))),
                  "diff_max_settimane_netto": float(np.max(np.abs(w0["netto"].to_numpy() - w["netto"].to_numpy()))),
                  "somma_netti_usdt_meno_finale": float(1000 + d["netto_usdt"].sum() - np.prod(1 + d["netto"].to_numpy()) * 1000)}
    cand = {}
    for v in DUE:
        e = te.numeri_settimana(sett[v]["netto"])
        cand[f"161 {v}"] = {k: e[k] for k in ("sharpe", "asimmetria", "curtosi")} | {"settimane": e["settimane"]}
    corr = ast.corretto_famiglie({f"161 {v}": sett[v]["netto"] for v in DUE}, cand)
    out["corretto"] = {k: corr[k] for k in ("serie", "senza_serie", "famiglie", "in_v", "deviazione_v")} | {
        "candidate": {k: {"corretto": x["corretto"], "gruppo": x["gruppo"]} for k, x in corr["candidate"].items()}}
    # soglia sr0 dell'esame: lo Sharpe settimanale che da' 0,5 e quello che da' 0,80
    from scipy import stats
    sr_v = None
    serie, soli = ast.mazzo({f"161 {v}": sett[v]["netto"] for v in DUE})
    gr = ast.gruppi(serie, ast.TAGLIO)
    sr_v = ast.per_v(gr, soli, True)
    var = float(np.var([x / math.sqrt(52) for x in sr_v], ddof=1))
    Nf = len(ast.per_v(gr, soli, False))
    g = 0.5772156649
    sr0 = math.sqrt(var) * ((1 - g) * stats.norm.ppf(1 - 1 / Nf) + g * stats.norm.ppf(1 - 1 / (Nf * math.e)))
    out["corretto"]["sr0_annuo"] = sr0 * math.sqrt(52)
    out["corretto"]["N_famiglie"] = Nf
    salva("rifai", out)
    for v in DUE:
        x = out[v]
        print(v, {k: round(x["numeri"][k], 5) for k in ("annuo_media52", "composto", "sharpe", "t", "discesa", "dal_2022_media52")},
              "liq", x["liquidazioni"], "rif", x["rifornimenti"], "diff", x["diff_max_giorni_netto"], x["diff_max_settimane_netto"])
    print("corretto", out["corretto"]["candidate"], "famiglie", out["corretto"]["famiglie"], "sr0 annuo", round(out["corretto"]["sr0_annuo"], 3))
    return out


# ---------------------------------------------------------------------------------------------------------------------------
# F. simulatore indipendente dell'auditor (scritto dalle regole, dati letti da capo)
# ---------------------------------------------------------------------------------------------------------------------------
def dati_propri():
    """Ore del mark e del prezzo scambiato, pronti giornalieri e regolamenti, letti senza i caricatori della prova."""
    if "propri" in _CACHE:
        return _CACHE["propri"]
    D0, D1 = se.INIZIO, pr.FINE                         # giorni dall'epoca: primo giorno tenuto, giorno dell'uscita finale
    h0 = (D0 - 1) * 24
    nh = (D1 + 2) * 24 - h0
    out = {}
    for s in MONETE:
        arr = {}
        for tipo in ("mark1h", "perp1h"):
            o_, hi = np.full(nh, np.nan), np.full(nh, np.nan)
            for f in sorted((dat.DATI / tipo).glob(f"{s}-*.zip")):
                d = dat.leggi(f)
                k = d["t"].to_numpy(np.int64) // 3_600_000 - h0
                ok = (k >= 0) & (k < nh)
                o_[k[ok]] = d["open"].to_numpy(float)[ok]; hi[k[ok]] = d["high"].to_numpy(float)[ok]
            arr[tipo] = (o_, hi)
        mo = np.where(np.isnan(arr["mark1h"][0]), arr["perp1h"][0], arr["mark1h"][0])
        mh = np.where(np.isnan(arr["mark1h"][1]), arr["perp1h"][1], arr["mark1h"][1])
        sp = pd.read_csv(t35.DATI / f"{s}.csv.gz").set_index("giorno")["open"]
        S = sp.reindex(np.arange(D0, D1 + 1)).to_numpy(float)
        righe = []
        for f in sorted((sc.DATI / s / "funding").glob("*.zip")):
            righe += funding_da_zip(f)
        R = pd.DataFrame(righe, columns=["ts", "ore", "tasso"]).drop_duplicates("ts")
        tasso = np.zeros(nh)
        k = R["ts"].to_numpy(np.int64) // 3_600_000 - h0
        ok = (k >= 0) & (k < nh)
        tasso[k[ok]] = R["tasso"].to_numpy(float)[ok]
        # segnale: somma dei 3N regolamenti che finiscono alle 00:00 del giorno (tutti quelli tenuti nei giorni D-N..D-1)
        hr = R["ts"].to_numpy(np.int64) // 3_600_000
        ser = pd.Series(R["tasso"].to_numpy(float), index=hr).sort_index()
        out[s] = {"mo": mo, "mh": mh, "ph": arr["perp1h"][1], "S": S, "tasso": tasso, "reg": ser}
    out["h0"], out["D0"], out["D1"] = h0, D0, D1
    _CACHE["propri"] = out
    return out


def segnale_proprio(s: str, N: int, ritardo: int = 0) -> np.ndarray:
    p = dati_propri()
    reg = p[s]["reg"]
    hr, v = reg.index.to_numpy(), reg.to_numpy()
    cum = np.concatenate([[0.0], np.cumsum(v)])
    out = []
    for D in range(p["D0"], p["D1"]):
        fine = (D - ritardo) * 24                        # ultimo regolamento letto: le 00:00 del giorno (o del giorno prima)
        inizio = (D - ritardo - N) * 24                  # escluso: le 00:00 di D-N appartengono al giorno D-N-1
        i1 = np.searchsorted(hr, fine, side="right"); i0 = np.searchsorted(hr, inizio, side="right")
        out.append(round(cum[i1] - cum[i0], 12) > 0)
    return np.array(out)


def simula_propria(N=None, sig=None, *, ingresso=0.60, soglia=0.45, mmr=(0.005, 0.005), cs=0.0015, cp=0.0006, alto="mark",
                   salta=frozenset(), salta_tutto=frozenset(), verbose=False, passi=None, capitale=1000.0):
    """Un conto a patrimonio ora per ora. ``salta``: giorni (indice) in cui il bot non rifornisce; ``salta_tutto``: giorni in cui non fa
    niente (ne' uscite ne' rifornimenti). ``alto``: "mark" o "scambiato" per il controllo della liquidazione dentro la giornata."""
    p = dati_propri()
    h0, D0, D1 = p["h0"], p["D0"], p["D1"]
    nd = D1 - D0
    sigs = sig if sig is not None else np.column_stack([segnale_proprio(s, N) for s in MONETE])
    K = 2
    C = [capitale / 2, capitale / 2]; Qs = [0.0, 0.0]; Qp = [0.0, 0.0]; W = [0.0, 0.0]; Pe = [0.0, 0.0]
    dentro = [False, False]; scop = [False, False]
    patr = np.zeros(nd + 1)
    ev = {"liq": [], "rif": [0, 0], "min_apertura": [9.0, 9.0], "min_dentro_giorno": [9.0, 9.0], "spese": 0.0, "funding": 0.0,
          "rif_usdt": 0.0, "min_dentro_quando": ["", ""], "giorni_rif": [[], []], "margine_dopo_apertura": np.full((nd, 2), np.nan),
          "nozionale": np.zeros((nd, 2)), "rif_valori": [[], []], "bloccati": [0, 0], "chiusure_da_rifornimento": [0, 0], "patr_moneta": np.zeros((nd, 2)), "patr_dopo": np.zeros(nd)}
    for i in range(nd + 1):
        D = D0 + i
        h = D * 24 - h0
        m = [p[s]["mo"][h] for s in MONETE]
        sp = [p[s]["S"][i] for s in MONETE]
        # regolamento delle 00:00 sulla quantita' tenuta (prima di tutto)
        for k, s in enumerate(MONETE):
            if Qp[k] > 0 and i > 0:
                f = p[s]["tasso"][h] * Qp[k] * m[k]
                W[k] += f; ev["funding"] += f
        patr[i] = sum(C[k] + Qs[k] * sp[k] + W[k] - Qp[k] * (m[k] - Pe[k]) for k in range(K))
        if i == nd:                                       # uscita finale all'apertura del 5 ottobre
            for k in range(K):
                if dentro[k]:
                    ev["spese"] += Qs[k] * sp[k] * cs + Qp[k] * m[k] * cp
                    C[k] += Qs[k] * sp[k] * (1 - cs) + W[k] - Qp[k] * (m[k] - Pe[k]) - Qp[k] * m[k] * cp
                    Qs[k] = Qp[k] = W[k] = 0.0
            patr[i] = sum(C)
            break
        fermo = i in salta_tutto
        for k in range(K):                                # liquidazione al mark delle 00:00
            if Qp[k] > 0 and W[k] - Qp[k] * (m[k] - Pe[k]) < mmr[k] * Qp[k] * m[k]:
                ev["liq"].append((sc.data(D), 0, MONETE[k])); W[k] = 0.0; Qp[k] = 0.0; scop[k] = True
        if not fermo:
            for k in range(K):                            # uscite
                if dentro[k] and (not sigs[i, k] or scop[k]):
                    ev["spese"] += Qs[k] * sp[k] * cs + Qp[k] * m[k] * cp
                    C[k] += Qs[k] * sp[k] * (1 - cs) + W[k] - Qp[k] * (m[k] - Pe[k]) - Qp[k] * m[k] * cp
                    Qs[k] = Qp[k] = W[k] = 0.0; dentro[k] = scop[k] = False
            for k in range(K):                            # entrate
                if not dentro[k] and sigs[i, k]:
                    if not dentro[1 - k]:
                        C[0] = C[1] = (C[0] + C[1]) / 2
                    q = C[k] / (sp[k] * (1 + cs) + ingresso * m[k])
                    if passi is not None:
                        q = math.floor(q / passi[k][0] + 1e-9) * passi[k][0]
                        if q < passi[k][1] - 1e-12 or q * sp[k] < passi[k][2]:
                            ev["bloccati"][k] += 1
                            continue
                    C[k] -= q * sp[k] * (1 + cs) + ingresso * q * m[k]
                    W[k] = ingresso * q * m[k] - q * m[k] * cp
                    ev["spese"] += q * sp[k] * cs + q * m[k] * cp
                    Qs[k] = Qp[k] = q; Pe[k] = m[k]; dentro[k] = True
            for k in range(K):                            # rifornimento
                if dentro[k] and Qp[k] > 0:
                    MB = W[k] - Qp[k] * (m[k] - Pe[k])
                    r = MB / (Qp[k] * m[k])
                    ev["min_apertura"][k] = min(ev["min_apertura"][k], r)
                    if r < soglia and i not in salta:
                        x = (ingresso * Qp[k] * m[k] - MB) / (sp[k] * (1 - cs) - cp * m[k] + ingresso * m[k])
                        if passi is not None:
                            x = math.ceil(x / passi[k][0] - 1e-9) * passi[k][0]
                        x = min(Qp[k], x)
                        ev["rif_valori"][k].append(x * sp[k])
                        W[k] += x * sp[k] * (1 - cs) - x * m[k] * cp - x * (m[k] - Pe[k])
                        ev["spese"] += x * sp[k] * cs + x * m[k] * cp; ev["rif_usdt"] += x * sp[k]
                        Qs[k] -= x; Qp[k] -= x; ev["rif"][k] += 1; ev["giorni_rif"][k].append(i)
                        if Qp[k] <= 1e-12:
                            C[k] += Qs[k] * sp[k] * (1 - cs) + W[k]; ev["spese"] += Qs[k] * sp[k] * cs
                            Qs[k] = Qp[k] = W[k] = 0.0; dentro[k] = False; ev["chiusure_da_rifornimento"][k] += 1
                    MBd = W[k] - Qp[k] * (m[k] - Pe[k])
                    ev["margine_dopo_apertura"][i, k] = MBd / (Qp[k] * m[k]) if Qp[k] > 0 else np.nan
        if i < nd:
            for k in range(K):
                ev["nozionale"][i, k] = Qp[k] * m[k]
                ev["patr_moneta"][i, k] = C[k] + Qs[k] * sp[k] + W[k] - Qp[k] * (m[k] - Pe[k])
            ev["patr_dopo"][i] = ev["patr_moneta"][i].sum()
        for k, s in enumerate(MONETE):                    # le ore del giorno
            if Qp[k] <= 0:
                continue
            for hh in range(24):
                j = h + hh
                if hh in (8, 16):
                    f = p[s]["tasso"][j] * Qp[k] * p[s]["mo"][j]
                    W[k] += f; ev["funding"] += f
                M = p[s]["mh"][j] if alto == "mark" else max(p[s]["mh"][j], p[s]["ph"][j])
                rr = (W[k] - Qp[k] * (M - Pe[k])) / (Qp[k] * M)
                if rr < ev["min_dentro_giorno"][k]:
                    ev["min_dentro_giorno"][k] = rr; ev["min_dentro_quando"][k] = f"{sc.data(D)} {hh:02d}"
                if rr < mmr[k]:
                    ev["liq"].append((sc.data(D), hh, s)); W[k] = 0.0; Qp[k] = 0.0; scop[k] = True
                    break
    netto = patr[1:] / patr[:-1] - 1
    d = pd.DataFrame({"netto": netto, "netto_doppio": netto, "spese": 0.0, "funding": 0.0, "giro": 0.0, "long": 0.0, "short": 0.0,
                      "dentro_BTC": 1, "dentro_ETH": 1}, index=np.arange(D0, D1))
    return d, ev


def indipendente() -> dict:
    out = {}
    for v, N in DUE.items():
        d, ev = simula_propria(N)
        d0 = pd.read_csv(RIS / f"giorni_{v}.csv.gz", index_col=0)
        sig_mio = np.column_stack([segnale_proprio(s, N) for s in MONETE])
        sig_prova = segnali(N)
        x = numeri(d)
        out[v] = {"numeri": x, "liquidazioni": ev["liq"], "rifornimenti": ev["rif"], "margine_min_apertura": ev["min_apertura"],
                  "margine_min_dentro_giorno": ev["min_dentro_giorno"], "quando": ev["min_dentro_quando"],
                  "spese_usdt": ev["spese"], "funding_usdt": ev["funding"], "rifornimento_usdt": ev["rif_usdt"],
                  "segnali_diversi_dalla_prova": int((sig_mio != sig_prova).sum()),
                  "diff_max_netto_giorni": float(np.max(np.abs(d["netto"].to_numpy() - d0["netto"].to_numpy()))),
                  "finale_prova": float(np.prod(1 + d0["netto"].to_numpy()) * 1000)}
        print(v, {k: round(x[k], 5) for k in ("annuo_media52", "composto", "sharpe", "t", "finale_su_1000")}, "liq", len(ev["liq"]), "rif", ev["rif"],
              "min aperture", np.round(ev["min_apertura"], 4), "min nel giorno", np.round(ev["min_dentro_giorno"], 4), ev["min_dentro_quando"],
              "segnali diversi", out[v]["segnali_diversi_dalla_prova"], "diff", out[v]["diff_max_netto_giorni"])
    salva("indipendente", out)
    return out


# ---------------------------------------------------------------------------------------------------------------------------
# C. margine: rialzi peggiori, giorni saltati, mantenimento, prezzo scambiato
# ---------------------------------------------------------------------------------------------------------------------------
def rialzi() -> dict:
    """Il rialzo peggiore dall'apertura delle 00:00 al massimo delle 24/48/72 ore dopo, col mark (riempito) e col prezzo scambiato;
    e col pannello giornaliero (massimo del giorno o di due giorni sull'apertura), come nelle regole."""
    p = dati_propri()
    c = base()
    pan = c["pan"]
    h0, D0, D1 = p["h0"], p["D0"], p["D1"]
    out = {}
    for k, s in enumerate(MONETE):
        o = {}
        for nome, alto in (("mark", p[s]["mh"]), ("scambiato", p[s]["ph"])):
            for w in (24, 48, 72):
                best, quando = -1.0, ""
                for D in range(D0, D1):
                    h = D * 24 - h0
                    r = np.nanmax(alto[h:h + w]) / p[s]["mo"][h] - 1
                    if r > best:
                        best, quando = r, sc.data(D)
                o[f"{nome}_{w}h"] = [best, quando]
        j = pan["simboli"].index(s)
        a, b = c["a"], c["b"]
        O, Hh = pan["open"][:, j], pan["high"][:, j]
        r1 = Hh[a:b + 1] / O[a:b + 1] - 1
        r2 = np.maximum(Hh[a:b + 1], Hh[a + 1:b + 2]) / O[a:b + 1] - 1
        o["pannello_1g"] = [float(r1.max()), sc.data(int(se.INIZIO + r1.argmax()))]
        o["pannello_2g"] = [float(r2.max()), sc.data(int(se.INIZIO + r2.argmax()))]
        out[s] = o
    # il rialzo che liquida partendo da un margine r all'apertura: r - x >= mmr (1 + x)  ->  x = (r - mmr) / (1 + mmr)
    out["rialzo_che_liquida_da_45pct"] = (0.45 - 0.005) / 1.005
    out["rialzo_che_liquida_da_31_7pct"] = (0.317 - 0.005) / 1.005
    out["margine_che_regge_40_7pct_piu_mantenimento"] = 0.407 + 0.005 * 1.407
    return out


def margine() -> dict:
    out = {"rialzi": rialzi()}
    base_ = {}
    for v, N in DUE.items():
        d, ev = simula_propria(N)
        base_[v] = (d, ev)
        fin = float(np.prod(1 + d["netto"].to_numpy()) * 1000)
        o = {"finale": fin}
        # 1) margine al massimo orario nelle 48 e 72 ore dopo ogni apertura, senza rifornimento (dopo l'apertura di oggi)
        p = dati_propri()
        # 2) un giorno saltato e due giorni saltati su ogni giorno di rifornimento (solo i rifornimenti; poi tutto fermo)
        for nome, kw in (("salta_1_rif", "salta"), ("salta_2_rif", "salta"), ("fermo_1", "salta_tutto"), ("fermo_2", "salta_tutto")):
            liq, mins, peggio = 0, [], []
            giorni = sorted(set(ev["giorni_rif"][0]) | set(ev["giorni_rif"][1]))
            for g in giorni:
                sk = {g} if nome.endswith("1") or nome.endswith("1_rif") else {g, g + 1}
                d2, e2 = simula_propria(N, **{kw: frozenset(sk)})
                liq += len(e2["liq"]) > 0
                mins.append(min(e2["min_dentro_giorno"]))
                peggio.append((sc.data(se.INIZIO + g), float(min(e2["min_dentro_giorno"])), len(e2["liq"])))
            o[nome] = {"prove": len(giorni), "con_liquidazione": liq, "margine_minimo_nella_giornata": float(min(mins)) if mins else None,
                       "peggiori": sorted(peggio, key=lambda x: x[1])[:3]}
        # 3) il bot che rifornisce solo ogni 2, 3, 7 giorni
        for ogni in (2, 3, 7):
            for fase in range(ogni):
                sk = frozenset(i for i in range(len(d)) if (i % ogni) != fase)
                d2, e2 = simula_propria(N, salta=sk)
                o[f"ogni_{ogni}_fase_{fase}"] = {"liquidazioni": e2["liq"][:3], "n_liq": len(e2["liq"]), "rif": e2["rif"],
                                                  "margine_min_giorno": [float(x) for x in e2["min_dentro_giorno"]],
                                                  "composto": float(np.prod(1 + d2["netto"].to_numpy()) ** (365 / len(d2)) - 1)}
        # 4) mantenimento e prezzo scambiato
        for nome, kw in (("mmr_0_4_0_5", {"mmr": (0.004, 0.005)}), ("mmr_1", {"mmr": (0.01, 0.01)}), ("mmr_2_5", {"mmr": (0.025, 0.025)}),
                         ("alto_scambiato", {"alto": "scambiato"})):
            d2, e2 = simula_propria(N, **kw)
            o[nome] = {"liquidazioni": e2["liq"], "margine_min_giorno": [float(x) for x in e2["min_dentro_giorno"]], "quando": e2["min_dentro_quando"]}
        # 5) senza nessun rifornimento: quando sarebbe stato liquidato
        d2, e2 = simula_propria(N, salta=frozenset(range(len(d))))
        o["senza_rifornimenti"] = {"liquidazioni": e2["liq"][:6], "n_liq": len(e2["liq"]),
                                   "composto": float(np.prod(1 + d2["netto"].to_numpy()) ** (365 / len(d2)) - 1)}
        # 6) il margine dopo le azioni dell'apertura: quante aperture sotto il 45% (dovrebbero essere 0) e il minimo
        mda = ev["margine_dopo_apertura"]
        o["aperture_dopo_azioni_sotto_45"] = int(np.nansum(mda < 0.45 - 1e-9))
        out[v] = o
        print(v, {k: (x if not isinstance(x, dict) else {kk: x[kk] for kk in list(x)[:3]}) for k, x in o.items() if not k.startswith("ogni_")})
        print("  ogni", {k: (x["n_liq"], round(min(x["margine_min_giorno"]), 3)) for k, x in o.items() if k.startswith("ogni_")})
    print(json.dumps(out["rialzi"]))
    salva("margine", out)
    return out


# ---------------------------------------------------------------------------------------------------------------------------
# E. sensibilita' (+-10%, +-20%), ritardo del segnale, costi
# ---------------------------------------------------------------------------------------------------------------------------
def _riga(d, ev):
    x = numeri(d)
    return {"composto": x["composto"], "annuo_media52": x["annuo_media52"], "sharpe": x["sharpe"], "t": x["t"],
            "anno_min": min(x["per_anno"].values()), "anni_negativi": [a for a, r in x["per_anno"].items() if r <= 0],
            "dal_2022": x["dal_2022_media52"], "liq": len(ev["liq"]), "rif": sum(ev["rif"]), "margine_min_giorno": float(min(ev["min_dentro_giorno"]))}


def sensi() -> dict:
    out = {}
    for v, N in DUE.items():
        o = {}
        o["base"] = _riga(*simula_propria(N))
        for f in (0.8, 0.9, 1.1, 1.2):
            o[f"N_x{f}"] = {"N": round(N * f)} | _riga(*simula_propria(round(N * f)))
            o[f"ingresso_x{f}"] = _riga(*simula_propria(N, ingresso=0.60 * f)) if 0.60 * f > 0.45 else "non valido (sotto la soglia)"
            o[f"soglia_x{f}"] = _riga(*simula_propria(N, soglia=0.45 * f)) if 0.45 * f < 0.60 else "non valido (sopra l'ingresso)"
            o[f"tutte_e_due_x{f}"] = _riga(*simula_propria(N, ingresso=0.60 * f, soglia=0.45 * f))
        sig1 = np.column_stack([segnale_proprio(s, N, ritardo=1) for s in MONETE])
        o["segnale_un_giorno_dopo"] = _riga(*simula_propria(sig=sig1))
        o["costi_x1_5"] = _riga(*simula_propria(N, cs=0.0015 * 1.5, cp=0.0006 * 1.5))
        o["costi_x2"] = _riga(*simula_propria(N, cs=0.003, cp=0.0012))
        o["pronti_0_10_perpetuo_0_07"] = _riga(*simula_propria(N, cs=0.0010, cp=0.0007))
        o["regola_della_revisione_33_50"] = _riga(*simula_propria(N, ingresso=0.50, soglia=1 / 3))
        out[v] = o
        for k, x in o.items():
            if isinstance(x, dict):
                print(v, f"{k:28s}", f"{100 * x['composto']:+.2f}% m52 {100 * x['annuo_media52']:+.2f}% S {x['sharpe']:.2f} t {x['t']:.2f} "
                      f"anno_min {100 * x['anno_min']:+.2f}% dal22 {100 * x['dal_2022']:+.2f}% liq {x['liq']} rif {x['rif']} mmin {x['margine_min_giorno']:.3f}")
    sd = np.ones((pr.FINE - se.INIZIO, 2), bool)
    out["sempre_dentro"] = _riga(*simula_propria(sig=sd))
    print("sempre dentro", out["sempre_dentro"])
    salva("sensi", out)
    return out


# ---------------------------------------------------------------------------------------------------------------------------
# D. misure: concentrazione, 2021, dal 2022, clima, esposizione, autocorrelazione, Sharpe corretto
# ---------------------------------------------------------------------------------------------------------------------------
def _dsr(sr_annuo, n, asim, curt, sr0_annuo):
    from scipy import stats
    sr, sr0 = sr_annuo / math.sqrt(52), sr0_annuo / math.sqrt(52)
    den = math.sqrt(max(1e-12, 1 - asim * sr + (curt - 1) / 4 * sr * sr))
    return float(stats.norm.cdf((sr - sr0) * math.sqrt(n - 1) / den))


def misure() -> dict:
    c = base()
    pan = c["pan"]
    rif = json.loads(ESITO.with_name(ESITO.name.format("rifai")).read_text())
    sr0 = rif["corretto"]["sr0_annuo"]
    out = {"sr0_annuo_196_famiglie": sr0}
    jb = pan["simboli"].index("BTCUSDT")
    for v, N in DUE.items():
        d, ev = simula_propria(N)
        r = d["netto"].to_numpy()
        eq = np.cumprod(1 + r) * 1000
        pat = np.concatenate([[1000.0], eq])
        gu = np.diff(pat)                                         # USDT per giorno
        date = pd.to_datetime(d.index.to_numpy() * 86400, unit="s")
        tot = pat[-1] - 1000
        anno = pd.Series(gu, index=date).groupby(date.year).sum()
        mese = pd.Series(gu, index=date).groupby(date.to_period("M")).sum()
        w = nv.settimane(d)["netto"]
        wu = pd.Series(gu, index=pr.lunedi_del_giorno(d.index.to_numpy())).groupby(level=0).sum()
        o = {"guadagno_usdt": float(tot), "per_anno_usdt": {int(k): float(x) for k, x in anno.items()},
             "quota_2021": float(anno.loc[2021] / tot), "quota_5_giorni_migliori": float(np.sort(gu)[-5:].sum() / tot),
             "quota_5_settimane_migliori": float(wu.nlargest(5).sum() / tot), "quota_3_mesi_migliori": float(mese.nlargest(3).sum() / tot),
             "3_mesi_migliori": {str(k): float(x) for k, x in mese.nlargest(3).items()}}
        # dal 2022: numeri e anni
        lun22 = pr.lunedi_del_giorno(np.array([sc.giorno(2022, 1, 3)]))[0]
        w22 = w[w.index >= lun22]
        e22 = te.numeri_settimana(w22)
        eall = te.numeri_settimana(w)
        o["dal_2022"] = {"settimane": e22["settimane"], "annuo_media52": e22["annuo"], "sharpe": e22["sharpe"], "t": e22["sharpe"] * math.sqrt(len(w22) / 52),
                         "usdt_2022_2026": float(pat[-1] - pat[np.searchsorted(d.index.to_numpy(), sc.giorno(2022, 1, 3))]),
                         "composto": float(np.prod(1 + w22.to_numpy()) ** (52 / len(w22)) - 1),
                         "dsr_con_sr0_dell_esame": _dsr(e22["sharpe"], len(w22), e22["asimmetria"], e22["curtosi"], sr0)}
        # discesa e durata, Sortino, profit factor settimanale
        dd_ = eq / np.maximum.accumulate(eq) - 1
        sotto = 0; lungo = 0
        for x in dd_:
            sotto = sotto + 1 if x < -1e-12 else 0
            lungo = max(lungo, sotto)
        neg = w[w < 0]
        o["misure"] = {"discesa_giornaliera": float(dd_.min()), "durata_discesa_max_giorni": int(lungo),
                       "sortino": float(w.mean() / math.sqrt((np.minimum(w, 0) ** 2).mean()) * math.sqrt(52)),
                       "profit_factor_settimane": float(w[w > 0].sum() / -neg.sum()) if len(neg) else None, "settimane_negative": int(len(neg)),
                       "volatilita_annua": eall["volatilita"], "asimmetria": eall["asimmetria"], "curtosi": eall["curtosi"]}
        # autocorrelazione delle settimane e Sharpe di Lo (2002)
        rho = [float(w.autocorr(k)) for k in range(1, 13)]
        q = 52
        eta = q / math.sqrt(q + 2 * sum((q - k) * rho[k - 1] for k in range(1, 13)))
        sr_w = w.mean() / w.std(ddof=1)
        neff = len(w) / (1 + 2 * sum(rho))
        o["autocorrelazione"] = {"rho_1_12": rho, "sharpe_lo_annuo": float(sr_w * eta), "sharpe_iid_annuo": float(sr_w * math.sqrt(52)),
                                 "settimane_efficaci": float(neff),
                                 "dsr_con_settimane_efficaci": _dsr(eall["sharpe"], int(neff), eall["asimmetria"], eall["curtosi"], sr0),
                                 "dsr_con_sharpe_di_lo_e_settimane_efficaci_doppio_conto": _dsr(eall["sharpe"] * eta / math.sqrt(52), int(neff), eall["asimmetria"],
                                                                                                eall["curtosi"], sr0),
                                 "t_con_settimane_efficaci": float(sr_w * math.sqrt(neff))}
        # esposizione: nozionale del perpetuo sul patrimonio, per anno
        noz = ev["nozionale"].sum(1) / ev["patr_dopo"]
        o["esposizione_nozionale_su_patrimonio"] = {int(y): float(noz[date.year == y].mean()) for y in sorted(set(date.year))}
        o["esposizione_min_max"] = [float(noz[noz > 0].min()), float(noz.max())]
        quota_btc = ev["patr_moneta"][:, 0] / ev["patr_dopo"]
        o["quota_patrimonio_BTC"] = {"min": float(quota_btc.min()), "max": float(quota_btc.max()), "fine": float(quota_btc[-1])}
        # clima di mercato (definizione dell'auditor): rendimento del Bitcoin nelle 13 settimane che finiscono con la settimana,
        # oltre +15% rialzo, sotto -15% ribasso, altrimenti laterale
        btc_w = c["btc_w"]
        c13 = (1 + btc_w).rolling(13).apply(np.prod, raw=True) - 1
        cl = pd.Series(np.where(c13 > 0.15, "rialzo", np.where(c13 < -0.15, "ribasso", "laterale")), index=btc_w.index)
        j = pd.concat([w, cl.rename("clima")], axis=1, join="inner")
        o["clima"] = {k: {"settimane": int(len(g)), "annuo_media52": float(g["netto"].mean() * 52), "positive": float((g["netto"] > 0).mean())}
                      for k, g in j.groupby("clima")}
        # rendimento medio a ingresso contro costo medio (operazioni = periodi dentro, poche)
        o["ingressi"] = int(sum(1 for k in range(2) for i in range(1, len(ev["nozionale"])) if ev["nozionale"][i, k] > 0 and ev["nozionale"][i - 1, k] == 0) +
                            sum(1 for k in range(2) if ev["nozionale"][0, k] > 0))
        o["spese_usdt"] = ev["spese"]; o["funding_usdt"] = ev["funding"]; o["rifornimento_usdt"] = ev["rif_usdt"]
        o["spese_su_guadagno"] = float(ev["spese"] / tot)
        out[v] = o
        print(v, {k: (round(x, 4) if isinstance(x, float) else x) for k, x in o.items() if k in ("guadagno_usdt", "quota_2021", "quota_5_giorni_migliori",
              "quota_5_settimane_migliori", "quota_3_mesi_migliori", "spese_su_guadagno", "ingressi")})
        print("   dal 2022", {k: round(x, 4) for k, x in o["dal_2022"].items()}, "\n   autocorr", [round(x, 2) for x in o["autocorrelazione"]["rho_1_12"][:6]],
              {k: round(x, 3) for k, x in o["autocorrelazione"].items() if k != "rho_1_12"},
              "\n   esposizione", {k: round(x, 3) for k, x in o["esposizione_nozionale_su_patrimonio"].items()}, o["quota_patrimonio_BTC"],
              "\n   clima", o["clima"], "\n   misure", {k: (round(x, 4) if isinstance(x, float) else x) for k, x in o["misure"].items()},
              "\n   anni usdt", {k: round(x, 1) for k, x in o["per_anno_usdt"].items()})
    salva("misure", out)
    return out



def robustezza_t() -> dict:
    """Il t e lo Sharpe corretto con le settimane non indipendenti: Newey-West, Lo (2002) con piu' ritardi, bootstrap a blocchi lunghi,
    anni di calendario. Solo per capire quanto l'esame (che le tratta come indipendenti) sopravvaluta la precisione."""
    rif = json.loads(ESITO.with_name(ESITO.name.format("rifai")).read_text())
    sr0 = rif["corretto"]["sr0_annuo"]
    out = {}
    for v, N in DUE.items():
        d, ev = simula_propria(N)
        w = nv.settimane(d)["netto"]
        lun22 = pr.lunedi_del_giorno(np.array([sc.giorno(2022, 1, 3)]))[0]
        o = {}
        for nome, x in (("intero", w), ("dal_2022", w[w.index >= lun22])):
            xv = x.to_numpy(); n = len(xv); mu = xv.mean(); e = xv - mu
            g0 = (e @ e) / n
            r = {}
            for L in (4, 13, 26, 52):
                s_ = g0 + 2 * sum((1 - l / (L + 1)) * (e[l:] @ e[:-l]) / n for l in range(1, L + 1))
                rho = [float(pd.Series(xv).autocorr(k)) for k in range(1, L + 1)]
                q = 52
                ql = min(L, q - 1)
                eta = q / math.sqrt(max(1e-12, q + 2 * sum((q - k) * rho[k - 1] for k in range(1, ql + 1))))
                sr_w = mu / xv.std(ddof=1)
                neff = n * g0 / s_
                num = te.numeri_settimana(x)
                r[f"ritardi_{L}"] = {"t_newey_west": float(mu / math.sqrt(s_ / n)), "sharpe_lo": float(sr_w * eta), "settimane_efficaci": float(neff),
                                     "dsr_settimane_efficaci": _dsr(num["sharpe"], max(3, int(neff)), num["asimmetria"], num["curtosi"], sr0)}
            bb = {}
            for B in (4, 13, 26, 52):
                b_ = sc.bootstrap_blocchi(xv, blocco=B, n=4000)
                bb[B] = {"basso_annuo": b_["basso"] * 52, "p": b_["p"]}
            r["bootstrap_blocchi"] = bb
            o[nome] = r
        dd_ = d.copy()
        date = pd.to_datetime(dd_.index.to_numpy() * 86400, unit="s")
        ya = (1 + dd_["netto"]).groupby(date.year).prod() - 1
        o["anni_calendario"] = {int(k): float(x) for k, x in ya.items()}
        piena = ya.loc[[2021, 2022, 2023, 2024, 2025]]
        o["sharpe_annuale_anni_pieni"] = float(piena.mean() / piena.std(ddof=1))
        o["sharpe_annuale_2022_2025"] = float(piena.loc[2022:].mean() / piena.loc[2022:].std(ddof=1))
        out[v] = o
        print(v, json.dumps({k: {kk: {a: round(b, 3) for a, b in vv.items()} if isinstance(vv, dict) and kk != "bootstrap_blocchi" else vv
                                 for kk, vv in o[k].items()} for k in ("intero", "dal_2022")}))
        print("  ", o["anni_calendario"], round(o["sharpe_annuale_anni_pieni"], 2), round(o["sharpe_annuale_2022_2025"], 2))
    salva("robustezza_t", out)
    return out


# ---------------------------------------------------------------------------------------------------------------------------
# C. filtri: passi veri, valore minimo a pronti (5 USDT, da verificare), capitale
# ---------------------------------------------------------------------------------------------------------------------------
def filtri() -> dict:
    passi, _ = nv.passi_veri()
    out = {"passi_del_repository": passi}
    for v, N in DUE.items():
        o = {}
        # convalida: il mio conto con i passi a 1.000 USDT contro il controllo della prova
        d, ev = simula_propria(N, passi=passi)
        g0 = pd.read_csv(RIS / f"giorni_{v}_passi1000.csv.gz", index_col=0)
        o["diff_con_la_prova_passi1000"] = float(np.max(np.abs(d["netto"].to_numpy() - g0["netto"].to_numpy())))
        for cap in (250.0, 280.0, 500.0, 1000.0, 2000.0):
            d, ev = simula_propria(N, passi=passi, capitale=cap)
            x = numeri(d)
            o[f"capitale_{int(cap)}"] = {"composto": x["composto"], "sharpe": x["sharpe"], "anno_min": min(x["per_anno"].values()),
                                          "dal_2022": x["dal_2022_media52"], "liq": len(ev["liq"]), "ingressi_bloccati": ev["bloccati"], "rif": ev["rif"],
                                          "chiusure_da_rifornimento": ev["chiusure_da_rifornimento"],
                                          "rifornimenti_a_pronti_sotto_5_usdt": [int(sum(1 for y in ev["rif_valori"][k] if y < 5)) for k in range(2)],
                                          "rifornimento_min_usdt": [float(min(ev["rif_valori"][k])) if ev["rif_valori"][k] else None for k in range(2)],
                                          "giorni_dentro": [int((ev["nozionale"][:, k] > 0).sum()) for k in range(2)]}
        out[v] = o
        print(v, "diff", o["diff_con_la_prova_passi1000"])
        for k, y in o.items():
            if k.startswith("capitale"):
                print("  ", k, {a: (round(b, 4) if isinstance(b, float) else b) for a, b in y.items()})
    salva("filtri", out)
    return out



# ---------------------------------------------------------------------------------------------------------------------------
# E. Sharpe corretto: tagli, con e senza l'aggiunta del 23 ottobre, N = conto; anche «sempre dentro»
# ---------------------------------------------------------------------------------------------------------------------------
def corretti() -> dict:
    from scipy import stats
    sett = {}
    for v, N in DUE.items():
        d, _ = simula_propria(N)
        sett[v] = nv.settimane(d)["netto"]
    d, _ = simula_propria(sig=np.ones((pr.FINE - se.INIZIO, 2), bool))
    sett["sempre_dentro"] = nv.settimane(d)["netto"]
    out = {}
    for taglio in (0.3, 0.5, 0.7):
        serie, soli = ast.mazzo({f"161 {v}": sett[v] for v in DUE})
        gr = ast.gruppi(serie, taglio)
        srg, srv = ast.per_v(gr, soli, False), ast.per_v(gr, soli, True)
        gm = 0.5772156649

        def sr0(lst, N):
            var = float(np.var([x / math.sqrt(52) for x in lst], ddof=1))
            return math.sqrt(var) * ((1 - gm) * stats.norm.ppf(1 - 1 / N) + gm * stats.norm.ppf(1 - 1 / (N * math.e))) * math.sqrt(52)
        o = {"famiglie": len(srg), "sr0_con_aggiunta": sr0(srv, len(srg)), "sr0_senza_aggiunta": sr0(srg, len(srg)),
             "famiglia_piu_alta": max(({"sharpe": g["sharpe"], "membri": g["membri"]} for g in gr), key=lambda x: x["sharpe"])}
        for v, w in sett.items():
            e = te.numeri_settimana(w)
            o[v] = {"con_aggiunta": te.sharpe_corretto(e["sharpe"], e["settimane"], e["asimmetria"], e["curtosi"], srv, 52, n_prove=len(srg)),
                    "senza_aggiunta": te.sharpe_corretto(e["sharpe"], e["settimane"], e["asimmetria"], e["curtosi"], srg, 52, n_prove=len(srg)),
                    "N_conto_328": te.sharpe_corretto(e["sharpe"], e["settimane"], e["asimmetria"], e["curtosi"], srv, 52, n_prove=328)}
        out[f"taglio_{taglio}"] = o
        print(taglio, {k: (round(x, 3) if isinstance(x, float) else x) for k, x in o.items() if k not in DUE and k != "sempre_dentro"},
              {k: {a: round(b, 4) for a, b in o[k].items()} for k in ("A", "B", "sempre_dentro")})
    salva("corretti", out)
    return out


# ---------------------------------------------------------------------------------------------------------------------------
# 8. rischi del conto vero: il tasso di base del funding (0,01% ogni 8 ore) e i limiti del bot su una gamba sola
# ---------------------------------------------------------------------------------------------------------------------------
def tasso_base() -> dict:
    """Se Binance portasse a zero la parte d'interesse del funding, i regolamenti esattamente allo 0,01% (dentro la banda dello 0,05%)
    andrebbero a zero e gli altri resterebbero uguali (formula: premio + limitato(interesse - premio, +-0,05%)); segnale invariato."""
    p = dati_propri()
    orig = {s: p[s]["tasso"].copy() for s in MONETE}
    out = {}
    for v, N in DUE.items():
        sig = np.column_stack([segnale_proprio(s, N) for s in MONETE])
        d0, e0 = simula_propria(sig=sig)
        try:
            for s in MONETE:
                t = orig[s].copy(); t[np.abs(t - 0.0001) < 1e-12] = 0.0; p[s]["tasso"] = t
            d1, e1 = simula_propria(sig=sig)
        finally:
            for s in MONETE:
                p[s]["tasso"] = orig[s]
        x0, x1 = numeri(d0), numeri(d1)
        out[v] = {"funding_usdt": e0["funding"], "funding_senza_tasso_base": e1["funding"], "quota_dal_tasso_base": 1 - e1["funding"] / e0["funding"],
                  "composto": x0["composto"], "composto_senza_tasso_base": x1["composto"], "dal_2022_senza": x1["dal_2022_media52"],
                  "per_anno_senza": x1["per_anno"]}
        print(v, {k: (round(x, 4) if isinstance(x, float) else {a: round(b, 4) for a, b in x.items()}) for k, x in out[v].items()})
    salva("tasso_base", out)
    return out


def limiti_bot() -> dict:
    """Quanti giorni la sola gamba venduta perde piu' del 5% (perdita giornaliera massima del bot, hard_limits.DAILY_LOSS_LIMIT)
    del patrimonio o del margine (60% del nozionale), da apertura ad apertura del mark."""
    p = dati_propri()
    h0, D0, D1 = p["h0"], p["D0"], p["D1"]
    out = {}
    for v, N in DUE.items():
        d, ev = simula_propria(N)
        noz, patr = ev["nozionale"], ev["patr_dopo"]
        res = {}
        for k, s in enumerate(MONETE):
            mo = np.array([p[s]["mo"][(D0 + i) * 24 - h0] for i in range(D1 - D0 + 1)])
            r = mo[1:] / mo[:-1] - 1
            loss = noz[:, k] * np.maximum(r, 0)
            W = 0.6 * noz[:, k]
            dentro = noz[:, k] > 0
            res[s] = {"giorni_dentro": int(dentro.sum()), "oltre_5pct_del_patrimonio": int(((loss / patr) > 0.05)[dentro].sum()),
                      "oltre_5pct_del_margine_al_60": int(((loss / np.where(W > 0, W, 1)) > 0.05)[dentro].sum()),
                      "perdita_max_su_patrimonio": float((loss / patr).max())}
        out[v] = res
        print(v, res)
    salva("limiti_bot", out)
    return out


if __name__ == "__main__":
    globals()[sys.argv[1]](*sys.argv[2:])
