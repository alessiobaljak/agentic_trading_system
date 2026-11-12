"""Audit del 12 novembre 2026: riesame della prova 96 (G22, la deriva del Bitcoin dopo il comunicato della Fed).

Importa le funzioni di `research/programma7/trentaquattresima.py` senza eseguire il suo `main` (che riscrive i risultati, catalogo
voce 11) e rifà il calcolo su due fonti: la lettura della prova (`esecuzione.ore_di`, oggi i file mensili di `research/data/p6h`) e i
file mensili da 1 ora scaricati dall'archivio pubblico di Binance in una cartella temporanea (impronte verificate). I minuti dei 46
giorni di riunione e il funding servono per l'entrata ritardata e per il regolamento delle 00:00 dentro la tenuta.

Uso: PYTHONPATH=<radice> python3 audits/repro/prova96_2026-11-12.py <cartella scaricata> [parte ...]
Parti: scarica base dati p funding entrata sensibilita misure controllo asticella (senza parti: tutte tranne scarica). Esito in `prova96_2026-11-12_esito_<parte>.json`.
La cartella scaricata contiene `1h/BTCUSDT-1h-AAAA-MM.zip` (dicembre 2020 - ottobre 2026), `1m/BTCUSDT-1m-<giorno>.zip` (i 46 giorni)
e `funding/BTCUSDT-fundingRate-AAAA-MM.zip`, tutti da `data.binance.vision/data/futures/um/`: si preparano con
`python3 audits/repro/prova96_2026-11-12.py <cartella> scarica` (impronte `.CHECKSUM` verificate; mai in `research/data/`).
`prova96_comunicati_fed.txt`: l'ora di pubblicazione di ogni comunicato, letta il 12 novembre 2026 dalle pagine
`federalreserve.gov/newsevents/pressreleases/monetaryAAAAMMGGa.htm` («For release at 2:00 p.m. EST/EDT»); il calendario delle
riunioni da `federalreserve.gov/monetarypolicy/fomccalendars.htm` (2021-2026: le 46 date delle regole, piu' il voto per notazione
del 22 agosto 2025 e la riunione del 27-28 ottobre 2026, fuori dalla prova).
"""
from __future__ import annotations

import datetime as dt
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

from research.programma5.strumenti import motore5 as m5
from research.programma6 import esecuzione as es
from research.programma6 import seconda as sc
from research.programma7 import trentaquattresima as t34

QUI = Path(__file__).parent
RADICE = QUI.parents[1]
CSV = RADICE / "research" / "programma7" / "risultati_trentaquattresima" / "eventi_G22.csv"
COSTO = float(sc.costi_moneta(["BTCUSDT"])[0])


def salva(parte: str, out: dict) -> None:
    (QUI / f"prova96_2026-11-12_esito_{parte}.json").write_text(json.dumps(out, ensure_ascii=False, indent=1, default=str),
                                                                  encoding="utf-8")


def ore_archivio(cart: Path) -> tuple[pd.DataFrame, dict]:
    """Le candele da 1 ora dai file mensili scaricati, con i controlli sul grezzo (duplicati, ordine, ore non intere)."""
    parti = [m5._csv_da_zip(p, m5.KLINE) for p in sorted((cart / "1h").glob("*.zip"))]
    df = pd.concat(parti, ignore_index=True)
    ot = m5._ms(df["open_time"]).astype(np.int64)
    ct = m5._ms(df["close_time"]).astype(np.int64)
    ctrl = {"righe": int(len(df)), "duplicati_open_time": int(ot.duplicated().sum()),
            "fuori_ordine": int((ot.diff().dropna() <= 0).sum()),
            "open_time_non_su_ora_intera": int((ot % 3_600_000 != 0).sum()),
            "chiusura_non_a_59m59s": int(((ct - ot) != 3_599_999).sum())}
    df["ora"] = ot // 3_600_000
    df = df.drop_duplicates("ora", keep="last").set_index("ora").sort_index()[["open", "high", "low", "close"]].astype(float)
    pieno = np.arange(df.index.min(), df.index.max() + 1)
    ctrl["ore_mancanti"] = int(len(pieno) - len(df))
    ctrl["prima"], ctrl["ultima"] = str(dt.datetime.utcfromtimestamp(int(df.index.min()) * 3600)), \
        str(dt.datetime.utcfromtimestamp(int(df.index.max()) * 3600))
    return df.reindex(pieno), ctrl


def eventi(c: pd.DataFrame, tenuta: int = t34.TENUTA, ritardo: int = 0, riunioni=None) -> pd.DataFrame:
    """Le operazioni come `trentaquattresima.esegui`; ``ritardo`` sposta entrata e uscita di altrettante ore (segno sempre dall'ora h)."""
    righe = []
    for d in (riunioni or t34.RIUNIONI):
        h = t34.ora_utc(d)
        serve = [h, h + 1 + ritardo, h + 1 + ritardo + tenuta]
        if any(k not in c.index or not np.isfinite(c.loc[k, "open"]) for k in serve) or not np.isfinite(c.loc[h, "close"]):
            continue
        segno = np.sign(c.loc[h, "close"] - c.loc[h, "open"])
        if segno == 0:
            continue
        r = segno * (c.loc[h + 1 + ritardo + tenuta, "open"] / c.loc[h + 1 + ritardo, "open"] - 1) - 2 * COSTO
        righe.append({"data": d, "h": h, "ora_utc": h % 24, "segno": int(segno), "r": float(r)})
    return pd.DataFrame(righe)


def esame(ev: pd.DataFrame) -> dict:
    b = t34.bootstrap(ev["r"].to_numpy())
    m1, m2 = ev[ev["data"] < "2024"]["r"].mean(), ev[ev["data"] >= "2024"]["r"].mean()
    return {**b, "vinte": float((ev["r"] > 0).mean()), "prima_meta": float(m1), "seconda_meta": float(m2),
            "per_anno": {a: round(float(x["r"].mean()), 6) for a, x in ev.groupby(ev["data"].str[:4])},
            "passa_scritto": bool(b["p"] <= 0.01 and b["media"] > 0 and m1 > 0 and m2 > 0)}


def controllo(c: pd.DataFrame, media_riunioni: float, n_ev: int) -> dict:
    riunioni = set(t34.RIUNIONI)
    contr = []
    for g in range(sc.giorno(2021, 1, 4), sc.giorno(2026, 10, 5) + 1):
        data = sc.data(g)
        if data in riunioni or dt.date.fromisoformat(data).weekday() >= 5:
            continue
        op = t34.operazione(c, t34.ora_utc(data), COSTO)
        if op:
            contr.append(op["r"])
    contr = np.asarray(contr)
    rng = np.random.default_rng(t34.SEME)
    medie = np.array([rng.choice(contr, size=n_ev, replace=False).mean() for _ in range(t34.ESTRAZIONI)])
    return {"giorni": int(len(contr)), "nan": int(np.isnan(contr).sum()), "media": float(np.nanmean(contr)),
            "dev_std": float(np.nanstd(contr, ddof=1)), "quota": float((medie >= media_riunioni).mean()),
            "medie_caso_p99": float(np.quantile(medie, 0.99)), "medie_caso_max": float(medie.max()), "valori": contr}


# ------------------------------------------------------------------------------------------------------------------------------

def parte_base(cart: Path) -> dict:
    vecchio = pd.read_csv(CSV)
    c_loc = es.ore_di("BTCUSDT")
    c_arc, ctrl = ore_archivio(cart)
    out = {"costo_per_lato": COSTO, "controlli_grezzo_archivio": ctrl}
    for nome, c in (("ore_di_locale", c_loc), ("archivio_scaricato", c_arc)):
        ev = eventi(c)
        un = vecchio.merge(ev, on="data", suffixes=("_v", "_n"))
        out[nome] = {"eventi": int(len(ev)), "uguali_al_csv_committato": int(len(un)),
                     "segni_diversi": int((un["segno_v"] != un["segno_n"]).sum()),
                     "diff_r_max": float((un["r_v"] - un["r_n"]).abs().max()),
                     "ore_utc_diverse": int((un["ora_utc_v"] != un["ora_utc_n"]).sum()), "esame": esame(ev)}
    # ora del comunicato: confronto con le pagine della Fed (EST -> 19 UTC, EDT -> 18 UTC)
    fed = {}
    for riga in (QUI / "prova96_comunicati_fed.txt").read_text().splitlines():
        p = riga.split()
        fed[p[0]] = p[4]
    atteso = {d: (19 if fed[d] == "EST" else 18) for d in t34.RIUNIONI}
    out["ora_utc_contro_fed"] = {"diverse": [d for d in t34.RIUNIONI if t34.ora_utc(d) % 24 != atteso[d]],
                                 "inverno_19": sum(v == 19 for v in atteso.values()), "estate_18": sum(v == 18 for v in atteso.values())}
    # prova del taglio: il segno con le candele fino all'ora h compresa (niente dopo)
    diversi = 0
    for d in t34.RIUNIONI:
        h = t34.ora_utc(d)
        tagliato = c_arc.loc[:h]
        s1 = np.sign(tagliato.loc[h, "close"] - tagliato.loc[h, "open"])
        s2 = np.sign(c_arc.loc[h, "close"] - c_arc.loc[h, "open"])
        diversi += int(s1 != s2)
    out["taglio_segni_diversi"] = diversi
    salva("base", out)
    return out


def parte_dati(cart: Path) -> dict:
    c, ctrl = ore_archivio(cart)
    out = {"grezzo": ctrl}
    finestra = []
    for d in t34.RIUNIONI:
        h = t34.ora_utc(d)
        w = c.loc[h - 3:h + 8]
        ret = (w["close"] / w["open"] - 1).abs()
        finestra.append({"data": d, "nan": int(w.isna().sum().sum()), "ore": int(len(w)),
                         "salto_chiusura_h_apertura_h1": float(c.loc[h + 1, "open"] / c.loc[h, "close"] - 1),
                         "salto_max_chiusura_apertura": float((w["open"].shift(-1) / w["close"] - 1).abs().max()),
                         "ora_peggiore_abs": float(ret.max()), "alto_basso_incoerenti": int(((w["high"] < w[["open", "close"]].max(axis=1)) |
                                                                                              (w["low"] > w[["open", "close"]].min(axis=1))).sum())})
    f = pd.DataFrame(finestra)
    out["finestre"] = {"nan_totali": int(f["nan"].sum()), "salto_max_assoluto": float(f["salto_max_chiusura_apertura"].max()),
                       "ora_piu_ampia": f.loc[f["ora_peggiore_abs"].idxmax(), ["data", "ora_peggiore_abs"]].to_dict(),
                       "candele_incoerenti": int(f["alto_basso_incoerenti"].sum())}
    # le ore dai minuti dei 46 giorni contro le candele orarie (apertura dell'ora h, chiusura di h, apertura di h+1)
    diff = []
    for d in t34.RIUNIONI:
        mm = m5._csv_da_zip(cart / "1m" / f"BTCUSDT-1m-{d}.zip", m5.KLINE)
        mm["minuto"] = m5._ms(mm["open_time"]) // 60_000
        mm = mm.drop_duplicates("minuto").set_index("minuto").sort_index()
        h = t34.ora_utc(d)
        a, b = h * 60, (h + 1) * 60
        try:
            o_h, c_h, o_h1 = float(mm.loc[a, "open"]), float(mm.loc[b - 1, "close"]), float(mm.loc[b, "open"])
        except KeyError:
            diff.append({"data": d, "manca": True})
            continue
        diff.append({"data": d, "manca": False, "minuti_nell_ora": int(((mm.index >= a) & (mm.index < b)).sum()),
                     "d_open_h": o_h / c.loc[h, "open"] - 1, "d_close_h": c_h / c.loc[h, "close"] - 1, "d_open_h1": o_h1 / c.loc[h + 1, "open"] - 1})
    dd = pd.DataFrame(diff)
    ok = dd[~dd["manca"]]
    out["minuti_contro_ore"] = {"giorni": int(len(dd)), "mancanti": int(dd["manca"].sum()),
                                "ore_con_meno_di_60_minuti": int((ok["minuti_nell_ora"] < 60).sum()),
                                "diff_max": float(ok[["d_open_h", "d_close_h", "d_open_h1"]].abs().max().max())}
    # le ore anomale nel periodo della prova (|chiusura/apertura - 1| oltre l'8%)
    per = c.loc[t34.ora_utc("2021-01-04"):t34.ora_utc("2026-10-05") + 24]
    r = per["close"] / per["open"] - 1
    out["ore_oltre_8_per_cento"] = [(str(dt.datetime.utcfromtimestamp(int(k) * 3600)), round(float(v), 4)) for k, v in r[r.abs() > 0.08].items()]
    out["ore_nan_nel_periodo"] = int(per["close"].isna().sum())
    salva("dati", out)
    return out


def parte_p(cart: Path) -> dict:
    from scipy import stats
    c, _ = ore_archivio(cart)
    x = eventi(c)["r"].to_numpy()
    n = len(x)
    semi = [t34.bootstrap(x, seme=s)["p"] for s in range(50)]
    rng = np.random.default_rng(t34.SEME)
    medie = rng.choice(x, size=(10000, n), replace=True).mean(axis=1)
    centrate = medie - x.mean()
    segni = np.random.default_rng(t34.SEME).choice([-1.0, 1.0], size=(200_000, n))
    flip = (segni * x).mean(axis=1)
    t = x.mean() / (x.std(ddof=1) / np.sqrt(n))
    out = {"eventi": n, "media": float(x.mean()), "dev_std": float(x.std(ddof=1)),
           "p_come_la_prova_seme_2026": t34.bootstrap(x)["p"],
           "p_bootstrap_50_semi": {"min": float(min(semi)), "max": float(max(semi)), "media": float(np.mean(semi))},
           "p_bootstrap_2000_estrazioni": t34.bootstrap(x, n=2000)["p"],
           "p_bootstrap_centrato": float((centrate >= x.mean()).mean()),
           "p_t_una_coda": float(stats.t.sf(t, n - 1)), "t": float(t),
           "p_segni_mescolati": float((flip >= x.mean()).mean()),
           "p_wilcoxon_una_coda": float(stats.wilcoxon(x, alternative="greater").pvalue),
           "p_segno_binomiale": float(stats.binomtest(int((x > 0).sum()), n, 0.5, alternative="greater").pvalue),
           "vinte": int((x > 0).sum()),
           "media_senza_la_migliore": float(np.sort(x)[:-1].mean()),
           "p_senza_la_migliore": t34.bootstrap(np.sort(x)[:-1])["p"],
           "media_senza_le_3_migliori": float(np.sort(x)[:-3].mean())}
    # effetto massimo per arrivare a p 0,01 con la stessa dispersione: quanto dovrebbe salire la media
    for delta in np.arange(0, 0.01, 0.0001):
        if t34.bootstrap(x + delta)["p"] <= 0.01:
            out["aumento_media_per_p_0_01"] = float(delta)
            break
    salva("p", out)
    return out


def funding_archivio(cart: Path) -> pd.DataFrame:
    parti = [m5._csv_da_zip(p, ["calc_time", "funding_interval_hours", "last_funding_rate"]) for p in sorted((cart / "funding").glob("*.zip"))]
    f = pd.concat(parti, ignore_index=True)
    f["ms"] = m5._ms(f["calc_time"]).astype(np.int64)
    f = f.drop_duplicates("ms").sort_values("ms")
    return f


def parte_funding(cart: Path) -> dict:
    c, _ = ore_archivio(cart)
    ev = eventi(c)
    f = funding_archivio(cart)
    ms = f["ms"].to_numpy()
    tassi, quanti, ore_reg = [], [], []
    for _, e in ev.iterrows():
        a, b = (e["h"] + 1) * 3_600_000, (e["h"] + 7) * 3_600_000
        dentro = f[(ms > a - 60_000) & (ms <= b + 60_000)]   # tolleranza di un minuto sull'orario del regolamento
        quanti.append(len(dentro))
        tassi.append(float(dentro["last_funding_rate"].astype(float).sum()))
        ore_reg += [dt.datetime.utcfromtimestamp(int(v) // 1000).strftime("%H:%M") for v in dentro["ms"]]
    ev["funding"] = tassi
    ev["r_f"] = ev["r"] - ev["segno"] * ev["funding"] * (1 + 0)          # chi compra paga il funding positivo
    out = {"regolamenti_per_operazione": dict(pd.Series(quanti).value_counts().sort_index().astype(int)),
           "orari_regolamento": dict(pd.Series(ore_reg).value_counts().astype(int)),
           "intervalli_ore_nel_periodo": dict(f["funding_interval_hours"].value_counts().astype(int)) if "funding_interval_hours" in f else None,
           "effetto_medio_a_operazione": float((ev["r_f"] - ev["r"]).mean()),
           "effetto_max_assoluto": float((ev["r_f"] - ev["r"]).abs().max()),
           "esame_con_funding": esame(ev.assign(r=ev["r_f"]))}
    salva("funding", out)
    return out


def parte_entrata(cart: Path) -> dict:
    c, _ = ore_archivio(cart)
    out = {}
    for rit in (1, 2, 5, 15):
        righe = []
        for d in t34.RIUNIONI:
            mm = m5._csv_da_zip(cart / "1m" / f"BTCUSDT-1m-{d}.zip", m5.KLINE)
            mm["minuto"] = m5._ms(mm["open_time"]) // 60_000
            mm = mm.drop_duplicates("minuto").set_index("minuto").sort_index()
            h = t34.ora_utc(d)
            segno = np.sign(c.loc[h, "close"] - c.loc[h, "open"])
            k = (h + 1) * 60 + rit
            if k not in mm.index or segno == 0:
                continue
            p0 = float(mm.loc[k, "open"])
            r = segno * (c.loc[h + 7, "open"] / p0 - 1) - 2 * COSTO
            righe.append({"data": d, "r": float(r)})
        out[f"entrata_{rit}_minuti_dopo"] = esame(pd.DataFrame(righe))
    for rit in (1, 2):
        out[f"tutto_spostato_di_{rit}_ore"] = esame(eventi(c, ritardo=rit))
    salva("entrata", out)
    return out


def parte_sensibilita(cart: Path) -> dict:
    c, _ = ore_archivio(cart)
    out = {}
    for ten in (3, 4, 5, 6, 7, 8, 9, 12):
        e = esame(eventi(c, tenuta=ten))
        out[f"tenuta_{ten}"] = {k: e[k] for k in ("media", "p", "prima_meta", "seconda_meta", "passa_scritto")}
    for costo_mult in (0.0, 0.5, 1.0, 1.5):
        ev = eventi(c)
        ev["r"] = ev["r"] + 2 * COSTO * (1 - costo_mult)
        e = esame(ev)
        out[f"costi_x{costo_mult}"] = {k: e[k] for k in ("media", "p")}
    salva("sensibilita", out)
    return out


def parte_misure(cart: Path) -> dict:
    c, _ = ore_archivio(cart)
    ev = eventi(c)
    f = funding_archivio(cart)
    # serie giornaliera: il rendimento dell'operazione nel giorno UTC dell'entrata, zero negli altri (capitale intero, leva 1)
    g0, g1 = sc.giorno(2021, 1, 1), sc.giorno(2026, 10, 5)
    s = pd.Series(0.0, index=range(g0, g1 + 1))
    for _, e in ev.iterrows():
        s.loc[(e["h"] + 1) // 24] += e["r"]
    eq = (1 + s).cumprod()
    dd = eq / eq.cummax() - 1
    fondo = int(dd.idxmin())
    picco = int(eq.loc[:fondo].idxmax())
    rec = eq.loc[fondo:][eq.loc[fondo:] >= eq.loc[picco]]
    neg = s[s < 0]
    x = ev["r"]
    pos = x[x > 0].sum()
    mesi = ev.groupby(ev["data"].str[:7])["r"].sum().sort_values(ascending=False)
    # clima (definizione dell'auditor, non della prova): rendimento del Bitcoin nei 30 giorni prima del giorno della riunione
    clima = []
    for _, e in ev.iterrows():
        h = e["h"]
        r30 = c.loc[h - 24, "close"] / c.loc[h - 24 * 31, "close"] - 1
        clima.append("rialzo" if r30 > 0.10 else "ribasso" if r30 < -0.10 else "laterale")
    ev["clima"] = clima
    out = {"operazioni": int(len(ev)), "giorni": int(len(s)), "esposizione_ore_quota": float(len(ev) * 6 / (len(s) * 24)),
           "rendimento_composto": float(eq.iloc[-1] - 1), "rendimento_annuo": float(eq.iloc[-1] ** (365 / len(s)) - 1),
           "sharpe_365": float(s.mean() / s.std(ddof=1) * np.sqrt(365)),
           "sortino_365": float(s.mean() / np.sqrt((np.minimum(s, 0) ** 2).mean()) * np.sqrt(365)),
           "discesa_max": float(dd.min()), "discesa_dal": sc.data(picco), "discesa_al_fondo": sc.data(fondo),
           "discesa_recupero": sc.data(int(rec.index[0])) if len(rec) else "non recuperata al 5 ottobre 2026",
           "profit_factor": float(pos / -x[x < 0].sum()), "vinte": float((x > 0).mean()),
           "media_operazione": float(x.mean()), "media_lorda": float(x.mean() + 2 * COSTO), "costo_operazione": 2 * COSTO,
           "operazione_migliore": float(x.max()), "operazione_peggiore": float(x.min()),
           "quota_somma_5_migliori": float(np.sort(x)[-5:].sum() / x.sum()),
           "quota_somma_3_mesi_migliori": float(mesi.iloc[:3].sum() / x.sum()), "tre_mesi_migliori": mesi.iloc[:3].round(4).to_dict(),
           "per_clima": {k: {"n": int(len(v)), "media": float(v["r"].mean())} for k, v in ev.groupby("clima")},
           "per_segno": {int(k): {"n": int(len(v)), "media": float(v["r"].mean())} for k, v in ev.groupby("segno")}}
    salva("misure", out)
    return out


def parte_controllo(cart: Path) -> dict:
    c, _ = ore_archivio(cart)
    ev = eventi(c)
    x = ev["r"].to_numpy()
    co = controllo(c, float(x.mean()), len(x))
    v = co.pop("valori")
    from scipy import stats
    out = {**co, "dev_std_riunioni": float(x.std(ddof=1)),
           "welch_una_coda_riunioni_maggiori": float(stats.ttest_ind(x, v, equal_var=False, alternative="greater").pvalue),
           "controllo_con_la_dispersione_delle_riunioni": "vedi dev_std: con la dispersione delle riunioni la quota non e' 0"}
    # quota con i giorni di controllo riscalati alla dispersione delle riunioni (per capire quanto conta la dispersione)
    vv = (v - v.mean()) / v.std(ddof=1) * x.std(ddof=1) + v.mean()
    rng = np.random.default_rng(t34.SEME)
    medie = np.array([rng.choice(vv, size=len(x), replace=False).mean() for _ in range(t34.ESTRAZIONI)])
    out["quota_con_dispersione_riunioni"] = float((medie >= x.mean()).mean())
    salva("controllo", out)
    return out


PARTI = {"base": parte_base, "dati": parte_dati, "p": parte_p, "funding": parte_funding, "entrata": parte_entrata,
         "sensibilita": parte_sensibilita, "misure": parte_misure, "controllo": parte_controllo}



def parte_asticella(cart: Path) -> dict:
    """Per completezza (l'esame della prova e' la p): lo Sharpe corretto della serie settimanale di G22 (capitale intero a
    operazione, leva 1, la settimana del lunedi' dell'uscita), con N = gruppi (`asticella.corretto_rivisto`) e con N = conto."""
    import math
    from research.programma6 import asticella as ast
    from research.programma6 import terza as te
    c, _ = ore_archivio(cart)
    ev = eventi(c)
    lun = (((ev["h"].to_numpy() + 7) // 24 + 3) // 7) * 7 - 3
    tutte = np.arange(sc.giorno(2021, 1, 4), sc.giorno(2026, 10, 5) + 1, 7)
    s = pd.Series(ev["r"].to_numpy(), index=lun).groupby(level=0).sum().reindex(tutte).fillna(0.0)
    s = ast.periodo(s)
    i = te.numeri_settimana(s)
    r = ast.corretto_rivisto({**ast.serie_nuove(), "96 G22": s}, {"96 G22": i})
    prove = ast.le_prove()
    serie = {n: ast.periodo(x) for n, x, _ in prove if x is not None}
    serie.update({n: ast.periodo(x) for n, x in {**ast.serie_nuove(), "96 G22": s}.items()})
    soli = [sr for _, x, sr in prove if x is None]
    sr_gruppi = ast.per_v(ast.gruppi(serie, ast.TAGLIO), soli, False)
    out = {"intero": i, "t": i["sharpe"] * math.sqrt(i["settimane"] / 52), "gruppi": r["gruppi"],
           "corretto_N_gruppi": r["candidate"]["96 G22"]["corretto"],
           "corretto_N_gruppi_con_aggiunta": r["candidate"]["96 G22"]["corretto_con_aggiunta"],
           "corretto_N_conto_312": te.sharpe_corretto(i["sharpe"], i["settimane"], i["asimmetria"], i["curtosi"], sr_gruppi, 52, n_prove=312),
           "gruppo": r["candidate"]["96 G22"]["gruppo"], "g22_nel_mazzo_di_asticella": "96 G22" in ast.serie_programma7()}
    salva("asticella", out)
    return out


PARTI["asticella"] = parte_asticella


def scarica(cart: Path) -> dict:
    """I file dell'archivio pubblico di Binance che servono all'audit, con il controllo delle impronte."""
    import hashlib
    import subprocess
    from concurrent.futures import ThreadPoolExecutor
    mesi = [f"{a}-{m:02d}" for a in range(2020, 2027) for m in range(1, 13) if "2020-12" <= f"{a}-{m:02d}" <= "2026-10"]
    base = "https://data.binance.vision/data/futures/um"
    lavori = [(f"{base}/daily/klines/BTCUSDT/1m/BTCUSDT-1m-{d}.zip", cart / "1m" / f"BTCUSDT-1m-{d}.zip") for d in t34.RIUNIONI]
    lavori += [(f"{base}/monthly/klines/BTCUSDT/1h/BTCUSDT-1h-{m}.zip", cart / "1h" / f"BTCUSDT-1h-{m}.zip") for m in mesi]
    lavori += [(f"{base}/monthly/fundingRate/BTCUSDT/BTCUSDT-fundingRate-{m}.zip", cart / "funding" / f"BTCUSDT-fundingRate-{m}.zip")
               for m in mesi]

    def uno(x):
        url, f = x
        f.parent.mkdir(parents=True, exist_ok=True)
        if not f.exists():
            subprocess.run(["curl", "-sS", "-m", "120", "-o", str(f), url], capture_output=True)
        r = subprocess.run(["curl", "-sS", "-m", "60", url + ".CHECKSUM"], capture_output=True, text=True)
        return f.exists() and r.stdout.split()[:1] == [hashlib.sha256(f.read_bytes()).hexdigest()]
    with ThreadPoolExecutor(12) as ex:
        ok = list(ex.map(uno, lavori))
    return {"file": len(ok), "impronte_giuste": int(sum(ok))}


PARTI["scarica"] = scarica

if __name__ == "__main__":
    cartella = Path(sys.argv[1])
    for nome in (sys.argv[2:] or [k for k in PARTI if k != "scarica"]):
        r = PARTI[nome](cartella)
        print(nome, json.dumps(r, ensure_ascii=False, default=str)[:1500], flush=True)
