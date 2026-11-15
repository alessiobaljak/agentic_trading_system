"""Audit della prova 157 (CB, funding coperto su BTC ed ETH), 15 novembre 2026. Solo lettura fuori da `audits/`.

Non chiama mai `novantacinquesima.esegui` (riscrive i risultati e il registro delle varianti, voce 11): importa le funzioni.
Uso (dalla radice del repository):
  python3 -I audits/repro/prova157_2026-11-15.py scarica <cartella>   # mark orario dei perpetui e pronti giornalieri dall'archivio
  python3 -I audits/repro/prova157_2026-11-15.py dati <cartella>      # buchi, duplicati, orari, funding regolamento per regolamento
  python3 -I audits/repro/prova157_2026-11-15.py rifai                # ricalcolo, esame, Sharpe corretto, misure, sensibilita'
  python3 -I audits/repro/prova157_2026-11-15.py margine <cartella>   # margine vero, liquidazioni con il mark orario, regola sicura
  python3 -I audits/repro/prova157_2026-11-15.py filtri <cartella>    # il conto a 1.000 e 280 USDT con i passi veri
  python3 -I audits/repro/prova157_2026-11-15.py extra <cartella>     # salita massima nella giornata e prova del taglio del segnale
  python3 -I audits/repro/prova157_2026-11-15.py esempio              # riproduzione minima dell'errore del margine (fallisce se sparisce)
`simula` e' un simulatore a patrimonio (contanti, pronti, portafoglio dei future): con regola "scritta" e funding "codice" ridà la prova
a 1e-16; poi aggiunge funding regolamento per regolamento al mark, liquidazione al mark orario, regola di margine "sicura", passi veri.
Esiti in `audits/repro/prova157_2026-11-15_esito_<parte>.json`; a schermo poche righe.
"""
from __future__ import annotations

import io
import json
import math
import sys
import urllib.request
import zipfile
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
from research.programma7 import prima as pr  # noqa: E402
from research.programma7 import trentacinquesima as t35  # noqa: E402
from research.src.dati import funding_da_zip  # noqa: E402

QUI = Path(__file__).parent
ESITO = QUI / "prova157_2026-11-15_esito_{}.json"
MONETE = ("BTCUSDT", "ETHUSDT")
MESI = [f"{a}-{m:02d}" for a in range(2020, 2027) for m in range(1, 13) if "2020-12" <= f"{a}-{m:02d}" <= "2026-10"]
RIS = RADICE / "research" / "programma7" / "risultati_novantacinquesima"
DUE = {"A": 30, "B": 90}


def salva(parte: str, x) -> None:
    ESITO.with_name(ESITO.name.format(parte)).write_text(json.dumps(x, ensure_ascii=False, indent=1, default=float), encoding="utf-8")


# ---------------------------------------------------------------------------------------------------------------------------
# scarico (cartella temporanea, mai research/data)
# ---------------------------------------------------------------------------------------------------------------------------
URL = {"mark1h": "https://data.binance.vision/data/futures/um/monthly/markPriceKlines/{s}/1h/{s}-1h-{m}.zip",
       "perp1h": "https://data.binance.vision/data/futures/um/monthly/klines/{s}/1h/{s}-1h-{m}.zip",
       "spot1d": "https://data.binance.vision/data/spot/monthly/klines/{s}/1d/{s}-1d-{m}.zip"}


def scarica(cartella: Path) -> None:
    from concurrent.futures import ThreadPoolExecutor
    lavori = [(k, s, m) for k in URL for s in MONETE for m in MESI]

    def uno(x):
        k, s, m = x
        f = cartella / k / f"{s}-{m}.zip"
        if f.exists():
            return x, "ok"
        f.parent.mkdir(parents=True, exist_ok=True)
        try:
            with urllib.request.urlopen(URL[k].format(s=s, m=m), timeout=60) as r:
                f.write_bytes(r.read())
            return x, "ok"
        except Exception as e:  # noqa: BLE001
            return x, repr(e)[:80]
    with ThreadPoolExecutor(max_workers=12) as ex:
        esiti = list(ex.map(uno, lavori))
    ko = [(x, e) for x, e in esiti if e != "ok"]
    print(f"file {len(esiti)}, errori {len(ko)}", ko[:5])


def leggi_zip(f: Path) -> pd.DataFrame:
    with zipfile.ZipFile(f) as z:
        grezzo = z.read(z.namelist()[0])
    h = 0 if grezzo[:1].isalpha() else None
    d = pd.read_csv(io.BytesIO(grezzo), header=h)
    d = d.iloc[:, :6]
    d.columns = ["open_time", "open", "high", "low", "close", "volume"]
    t = pd.to_numeric(d["open_time"])
    d["open_time"] = t.where(t < 10 ** 14, t // 1000)
    return d


def orarie(cartella: Path, tipo: str, s: str) -> pd.DataFrame:
    d = pd.concat([leggi_zip(f) for f in sorted((cartella / tipo).glob(f"{s}-*.zip"))], ignore_index=True)
    return d


# ---------------------------------------------------------------------------------------------------------------------------
# dati
# ---------------------------------------------------------------------------------------------------------------------------
def regolamenti(s: str) -> pd.DataFrame:
    righe = []
    for p in sorted((sc.DATI / s / "funding").glob("*.zip")):
        righe += funding_da_zip(p)
    d = pd.DataFrame(righe, columns=["ts", "ore", "tasso"])
    return d


def dati(cartella: Path) -> dict:
    pan = sc.pannello()
    t0 = pan["t0"]
    a, b = se.INIZIO - t0, pr.FINE - 1 - t0
    out = {}
    for s in MONETE:
        j = pan["simboli"].index(s)
        x = {}
        # candele giornaliere del perpetuo: file grezzi (duplicati, ordine, mezzanotte UTC), giorni dall'interfaccia pubblica
        grezzi = []
        for p in sorted((sc.DATI / s / "giorni").glob("*.zip")):
            g = sc.m5._csv_da_zip(p, sc.m5.KLINE)
            g["file"] = p.name
            grezzi.append(g)
        g = pd.concat(grezzi, ignore_index=True)
        ms = sc.m5._ms(g["open_time"])
        giorno = ms // 86_400_000
        dentro = (giorno >= se.INIZIO - 90) & (giorno <= pr.FINE)
        x["perp_righe_periodo"] = int(dentro.sum())
        x["perp_giorni_unici_periodo"] = int(giorno[dentro].nunique())
        x["perp_duplicati_periodo"] = int(giorno[dentro].duplicated().sum())
        x["perp_non_mezzanotte"] = int((ms[dentro] % 86_400_000 != 0).sum())
        tutti = set(range(se.INIZIO - 90, pr.FINE + 1))
        mancano = sorted(tutti - set(giorno[dentro].tolist()))
        x["perp_giorni_mancanti_nell_archivio"] = [sc.data(t) for t in mancano]
        api = sorted((sc.DATI / s / "giorni_api").glob("*.csv"))
        x["perp_file_api"] = [p.name for p in api]
        # incoerenze del pannello
        sl = slice(a - 90, b + 2)
        o, h, lo, c = (pan[k][sl, j] for k in ("open", "high", "low", "close"))
        x["pannello_nan"] = int(sum(np.isnan(v).sum() for v in (o, h, lo, c)))
        x["pannello_apertura_contro_chiusura_prima_max"] = float(np.max(np.abs(o[1:] / c[:-1] - 1)))
        # funding regolamento per regolamento: orari veri, numero al giorno, valori estremi
        R = regolamenti(s).drop_duplicates("ts").sort_values("ts")
        R["min"] = R["ts"] // 60_000
        R["giorno_tenuta"] = (R["min"] - 1) // 1440
        Rp = R[(R["giorno_tenuta"] >= se.INIZIO - 90) & (R["giorno_tenuta"] <= pr.FINE - 1)]
        ora = (Rp["ts"] // 1000 % 86400) / 3600
        x["regolamenti_periodo"] = int(len(Rp))
        x["orari_dei_regolamenti"] = {f"{k:.3f}": int(v) for k, v in ora.round(3).value_counts().sort_index().items()}
        x["secondi_oltre_l_ora_max"] = float(((Rp["ts"] // 1000) % 3600).max())
        x["intervallo_ore"] = {int(k): int(v) for k, v in Rp["ore"].value_counts().items()}
        per_g = Rp.groupby("giorno_tenuta").size()
        x["giorni_con_regolamenti_diversi_da_3"] = {sc.data(int(k)): int(v) for k, v in per_g[per_g != 3].items()}
        x["giorni_senza_regolamento"] = [sc.data(t) for t in sorted(set(range(se.INIZIO - 90, pr.FINE)) - set(per_g.index))]
        x["tasso_max"], x["tasso_min"] = float(Rp["tasso"].max()), float(Rp["tasso"].min())
        x["quota_regolamenti_al_tasso_di_base_0_0001"] = float((Rp["tasso"].round(8) == 0.0001).mean())
        # pannello contro i regolamenti veri
        somma = Rp.groupby("giorno_tenuta")["tasso"].sum()
        F = pd.Series(pan["funding"][:, j], index=np.arange(t0, t0 + len(pan["funding"])))
        idx = np.arange(se.INIZIO - 90, pr.FINE)
        x["pannello_contro_regolamenti_max_diff"] = float(np.max(np.abs(F.reindex(idx).to_numpy() - somma.reindex(idx).fillna(0).to_numpy())))
        # pronti: file della prova contro i file mensili riscaricati (mezzanotte UTC, duplicati, buchi)
        Op = t35.tabella_pronti([s], t0, len(pan["open"]))[:, 0]
        sp = orarie(cartella, "spot1d", s)
        sp["giorno"] = sp["open_time"] // 86_400_000
        x["pronti_non_mezzanotte"] = int((sp["open_time"] % 86_400_000 != 0).sum())
        x["pronti_duplicati"] = int(sp["giorno"].duplicated().sum())
        sp = sp.drop_duplicates("giorno").set_index("giorno")
        giorni_p = np.arange(se.INIZIO, pr.FINE + 1)
        x["pronti_mancanti_riscaricati"] = [sc.data(t) for t in giorni_p if t not in sp.index]
        x["pronti_nan_nella_prova"] = int(np.isnan(Op[giorni_p - t0]).sum())
        x["pronti_prova_contro_riscaricati_max_diff_rel"] = float(np.nanmax(np.abs(Op[giorni_p - t0] / sp["open"].reindex(giorni_p).to_numpy() - 1)))
        P = pan["open"][giorni_p - t0, j]
        base = P / Op[giorni_p - t0] - 1
        x["base_aperture"] = {"media": float(base.mean()), "max": float(base.max()), "min": float(base.min()),
                              "giorno_max_abs": sc.data(int(giorni_p[np.argmax(np.abs(base))]))}
        # mark orario: buchi, orari
        mk = orarie(cartella, "mark1h", s)
        ore = mk["open_time"] // 3_600_000
        x["mark_ore"] = int(len(mk))
        x["mark_duplicati"] = int(ore.duplicated().sum())
        x["mark_non_allo_scoccare"] = int((mk["open_time"] % 3_600_000 != 0).sum())
        tutte = np.arange((se.INIZIO - 1) * 24, pr.FINE * 24 + 24)
        manc = np.setdiff1d(tutte, ore.to_numpy())
        x["mark_ore_mancanti"] = int(len(manc))
        x["mark_ore_mancanti_giorni"] = sorted({sc.data(int(h // 24)) for h in manc})[:40]
        out[s] = x
    salva("dati", out)
    for s in MONETE:
        x = out[s]
        print(s, "dup", x["perp_duplicati_periodo"], "mancanti", x["perp_giorni_mancanti_nell_archivio"], "regolamenti!=3",
              len(x["giorni_con_regolamenti_diversi_da_3"]), "pannello-veri", x["pannello_contro_regolamenti_max_diff"],
              "pronti diff", x["pronti_prova_contro_riscaricati_max_diff_rel"], "mark mancanti", x["mark_ore_mancanti"])
    return out


# ---------------------------------------------------------------------------------------------------------------------------
# ricalcolo, esame, Sharpe corretto, misure, sensibilita'
# ---------------------------------------------------------------------------------------------------------------------------
_SEGNALE = n95.segnale


def carica():
    pan = sc.pannello()
    Op = t35.tabella_pronti(list(MONETE), pan["t0"], pan["open"].shape[0])
    ps = te.pannello_settimane(pan, log=lambda x: None, indicatori_si=False)
    btc_w = pd.Series(ps["R"][:, pan["simboli"].index("BTCUSDT")], index=ps["lunedi"])
    return pan, Op, btc_w


def misura(w: pd.Series) -> dict:
    v = w.to_numpy(float)
    sd = v.std(ddof=1)
    giu = np.sqrt(np.mean(np.minimum(v, 0) ** 2))
    sh = float(v.mean() / sd * math.sqrt(52)) if sd > 0 else 0.0
    return {"settimane": int(len(v)), "annuo": float(v.mean() * 52), "sharpe": sh, "t": sh * math.sqrt(len(v) / 52),
            "sortino": float(v.mean() / giu * math.sqrt(52)) if giu > 0 else None}


def esame_di(w: pd.DataFrame, btc_w, nuove_nome=None) -> dict:
    e = te.esame(w, btc_w, inizio=se.INIZIO, anni_pieni=se.ANNI_PIENI)
    e["t"] = e["intero"]["sharpe"] * math.sqrt(e["intero"]["settimane"] / 52)
    return e


def conto_con(pan, Op, N, segnale=None, limite=False, cs=None, cp_molt=1.0):
    """`n95.conto` con un segnale o costi diversi (sostituzione temporanea delle funzioni del modulo, senza scrivere niente)."""
    vecchi = (n95.segnale, n95.CS_STD, n95.sc.costi_moneta)
    try:
        if segnale is not None:
            n95.segnale = segnale
        if cs is not None:
            n95.CS_STD = cs
        if cp_molt != 1.0:
            n95.sc.costi_moneta = lambda simboli: vecchi[2](simboli) * cp_molt
        return n95.conto(pan, Op, N, limite=limite)
    finally:
        n95.segnale, n95.CS_STD, n95.sc.costi_moneta = vecchi


def ritardo(k):
    def s(F, a, b, N):
        return _SEGNALE(F, a - k, b - k, N)
    return s


def sharpe_corretti(nuove: dict, cand: dict, n_conto=None) -> dict:
    out = {}
    for taglio in (ast.TAGLIO,) + tuple(ast.ALTRI_TAGLI):
        c = ast.corretto_famiglie(nuove, cand, taglio=taglio)
        riga = {"famiglie": c["famiglie"], "in_v": c["in_v"], "deviazione_v": c["deviazione_v"],
                "candidate": {k: {"corretto": v["corretto"], "gruppo": v["gruppo"]} for k, v in c["candidate"].items()}}
        if n_conto:
            serie, soli = ast.mazzo(nuove)
            gr = ast.gruppi(serie, taglio)
            sr_v = ast.per_v(gr, soli, True)
            sr_tutti = ast.per_v(gr, soli, False)
            for k, i in cand.items():
                riga["candidate"][k]["corretto_N_conto"] = te.sharpe_corretto(i["sharpe"], i["settimane"], i["asimmetria"], i["curtosi"],
                                                                            sr_v, 52, n_prove=n_conto)
                riga["candidate"][k]["corretto_senza_aggiunta"] = te.sharpe_corretto(i["sharpe"], i["settimane"], i["asimmetria"],
                                                                                   i["curtosi"], sr_tutti, 52)
        out[str(taglio)] = riga
    return out


def concentrazione(d: pd.DataFrame, w: pd.DataFrame) -> dict:
    r = d["netto"]
    tot = float(r.sum())
    mesi = pd.to_datetime(d.index.to_numpy() * 86400, unit="s").to_period("M")
    m = r.groupby(mesi).sum()
    anni = pd.to_datetime(d.index.to_numpy() * 86400, unit="s").year
    eq = r.cumsum().to_numpy()
    sotto, lungo, inizio = 0, 0, 0
    picco = -1e9
    for k, x in enumerate(eq):
        if x >= picco:
            picco, sotto = x, 0
        else:
            sotto += 1
            lungo = max(lungo, sotto)
    return {"totale": tot, "quota_5_giorni_migliori": float(r.nlargest(5).sum() / tot),
            "quota_5_settimane_migliori": float(w["netto"].nlargest(5).sum() / tot),
            "quota_3_mesi_migliori": float(m.nlargest(3).sum() / tot), "3_mesi_migliori": {str(k): float(v) for k, v in m.nlargest(3).items()},
            "quota_2021": float(r[anni == 2021].sum() / tot), "giorni_discesa_piu_lunga_somma": int(lungo)}


def clima(d: pd.DataFrame, pan) -> dict:
    """Clima del mese dal rendimento del Bitcoin del mese (apertura del primo giorno contro apertura del primo del mese dopo):
    rialzo sopra +10%, ribasso sotto -10%, laterale altrimenti (definizione dell'audit, descrittiva)."""
    j = pan["simboli"].index("BTCUSDT")
    t0 = pan["t0"]
    date = pd.to_datetime(d.index.to_numpy() * 86400, unit="s")
    mesi = date.to_period("M")
    out = {"rialzo": [], "ribasso": [], "laterale": []}
    for m in sorted(set(mesi)):
        giorni = d.index[mesi == m]
        r_btc = pan["open"][giorni.max() + 1 - t0, j] / pan["open"][giorni.min() - t0, j] - 1
        k = "rialzo" if r_btc > 0.10 else ("ribasso" if r_btc < -0.10 else "laterale")
        out[k].append(float(d["netto"][mesi == m].sum()))
    return {k: {"mesi": len(v), "media_mese": float(np.mean(v)) if v else None, "positivi": int(sum(x > 0 for x in v))} for k, v in out.items()}


def periodi_dentro(d: pd.DataFrame, s: str) -> dict:
    x = d[f"dentro_{s}"].to_numpy()
    netto = (d[f"funding_{s}"] + d[f"base_{s}"] - d[f"spese_{s}"]).to_numpy()
    spese = d[f"spese_{s}"].to_numpy()
    tratti, k = [], 0
    while k < len(x):
        if x[k]:
            j = k
            while j < len(x) and x[j]:
                j += 1
            fine = min(j, len(x) - 1)        # il giorno dell'uscita paga le spese
            tratti.append((k, j, float(netto[k:fine + 1].sum()), float(spese[k:fine + 1].sum())))
            k = j
        else:
            k += 1
    return {"tratti": len(tratti), "giorni": [j - k for k, j, _, _ in tratti], "netto": [n for *_, n, _ in tratti],
            "spese": [c for *_, c in tratti]}


def rifai() -> dict:
    pan, Op, btc_w = carica()
    out = {"varianti": {}}
    pub = json.loads((RIS / "esame.json").read_text())
    sett = {}
    for v, N in DUE.items():
        d, per = n95.conto(pan, Op, N)
        w = n95.settimane(d)
        d0 = pd.read_csv(RIS / f"giorni_{v}.csv.gz", index_col=0)
        w0 = pd.read_csv(RIS / f"settimane_{v}.csv.gz", index_col=0)
        e = esame_di(w, btc_w)
        sett[v] = w
        x = {"diff_giorni_max": float(np.max(np.abs(d["netto"].to_numpy() - d0["netto"].to_numpy()))),
             "diff_settimane_max": float(np.max(np.abs(w["netto"].to_numpy() - w0["netto"].to_numpy()))),
             "giorni": len(d), "primo": sc.data(int(d.index[0])), "ultimo": sc.data(int(d.index[-1])),
             "settimane": len(w), "prima_settimana": sc.data(int(w.index[0])), "ultima_settimana": sc.data(int(w.index[-1])),
             "annuo": e["intero"]["annuo"], "sharpe": e["intero"]["sharpe"], "t": e["t"], "discesa": e["intero"]["discesa_max"],
             "asimmetria": e["intero"]["asimmetria"], "curtosi": e["intero"]["curtosi"], "volatilita": e["intero"]["volatilita"],
             "per_anno_esame": e["per_anno"], "pubblicato": {k: pub[v][k] for k in ("annuo_capitale", "sharpe", "t", "discesa_settimanale",
                                                                                    "sharpe_corretto", "per_anno_esame")},
             "sortino": misura(w["netto"])["sortino"], "esposizione_giorni_dentro": {s[:3]: int(d[f"dentro_{s[:3]}"].sum()) for s in MONETE},
             "giri": {s[:3]: per[s]["giri"] for s in MONETE}, "riduzioni_margine": {s[:3]: per[s]["riduzioni"] for s in MONETE},
             "concentrazione": concentrazione(d, w), "clima": clima(d, pan),
             "periodi": {s: periodi_dentro(d, s) for s in ("BTC", "ETH")}}
        # dal 2022 e solo dal 2023 (descrittivo: la regola conta il 2021)
        for da in (2022, 2023, 2024):
            ww = w["netto"][w.index >= sc.giorno(da, 1, 3 if da == 2022 else (2 if da == 2023 else 1))]
            x[f"dal_{da}"] = misura(ww)
        # costi: doppi, limite, pronti 0,10%/0,20%, perpetuo doppio
        x["costi"] = {}
        for nome, kw in {"limite": {"limite": True}, "pronti_0_10": {"cs": 0.0010}, "pronti_0_20": {"cs": 0.0020},
                         "pronti_0_30": {"cs": 0.0030}, "perpetuo_x2": {"cp_molt": 2.0}, "tutto_x2": {"cs": 0.0030, "cp_molt": 2.0}}.items():
            dd, _ = conto_con(pan, Op, N, **kw)
            x["costi"][nome] = misura(n95.settimane(dd)["netto"])
        # tempi: segnale di un giorno e di due giorni prima
        x["ritardo"] = {}
        for k in (1, 2, 7):
            dd, _ = conto_con(pan, Op, N, segnale=ritardo(k))
            ww = n95.settimane(dd)
            x["ritardo"][str(k)] = misura(ww["netto"]) | {"per_anno": esame_di(ww, btc_w)["per_anno"]}
        # sensibilita' +-10% e +-20% su N
        x["sensibilita"] = {}
        for f in (0.8, 0.9, 1.1, 1.2):
            NN = int(round(N * f))
            dd, _ = conto_con(pan, Op, NN)
            ww = n95.settimane(dd)
            x["sensibilita"][str(NN)] = misura(ww["netto"]) | {"per_anno": esame_di(ww, btc_w)["per_anno"]}
        out["varianti"][v] = x
    # sempre dentro
    d, per = n95.conto(pan, Op, None)
    w = n95.settimane(d)
    out["sempre_dentro"] = misura(w["netto"]) | {"per_anno": esame_di(w, btc_w)["per_anno"], "riduzioni": {s[:3]: per[s]["riduzioni"] for s in MONETE}}
    # Sharpe corretto: come la prova (N = famiglie, tagli 0,5 0,3 0,7), con N = conto del registro, senza l'aggiunta
    cand = {}
    for v in DUE:
        e = esame_di(sett[v], btc_w)["intero"]
        cand[f"157 {v}"] = {k: e[k] for k in ("sharpe", "asimmetria", "curtosi", "settimane")}
    out["sharpe_corretto"] = sharpe_corretti({f"157 {v}": sett[v]["netto"] for v in DUE}, cand, n_conto=322)
    # Sharpe corretto sulle sole settimane dal 2022 (descrittivo: quanto regge senza il 2021)
    cand22, nuove22 = {}, {}
    for v in DUE:
        ww = sett[v][sett[v].index >= sc.giorno(2022, 1, 3)]
        i = te.numeri_settimana(ww["netto"])
        cand22[f"157 {v}"] = {k: i[k] for k in ("sharpe", "asimmetria", "curtosi", "settimane")}
        nuove22[f"157 {v}"] = sett[v]["netto"]
    out["sharpe_corretto_dal_2022"] = sharpe_corretti(nuove22, cand22, n_conto=322)
    salva("rifai", out)
    for v, x in out["varianti"].items():
        print(v, f"diff {x['diff_giorni_max']:.1e}/{x['diff_settimane_max']:.1e}", f"annuo {x['annuo']:.4f} sharpe {x['sharpe']:.3f} t {x['t']:.2f}",
              "dal2022", {k: round(x['dal_2022'][k], 3) for k in ('annuo', 'sharpe', 't')})
    print("corretto", {k: {c: round(y["corretto"], 4) for c, y in r["candidate"].items()} for k, r in out["sharpe_corretto"].items()})
    return out


# ---------------------------------------------------------------------------------------------------------------------------
# margine: simulatore a patrimonio (pronti nel portafoglio a pronti, margine nel portafoglio dei future, contanti)
# ---------------------------------------------------------------------------------------------------------------------------
def ore_moneta(cartella: Path, s: str, pan, j: int) -> dict:
    """Apertura e massimo orari del mark (riempiti con il prezzo scambiato dove il mark manca) e del prezzo scambiato."""
    h0, h1 = (se.INIZIO - 1) * 24, (pr.FINE + 2) * 24
    n = h1 - h0
    mo, mh, lo_, lh = (np.full(n, np.nan) for _ in range(4))
    for tipo, (o_, h_) in (("mark1h", (mo, mh)), ("perp1h", (lo_, lh))):
        d = orarie(cartella, tipo, s)
        k = (d["open_time"] // 3_600_000).to_numpy() - h0
        ok = (k >= 0) & (k < n)
        o_[k[ok]] = d["open"].to_numpy(float)[ok]
        h_[k[ok]] = d["high"].to_numpy(float)[ok]
    riempite = int(np.isnan(mo).sum())
    mo = np.where(np.isnan(mo), lo_, mo)
    mh = np.where(np.isnan(mh), lh, mh)
    # dove manca anche il prezzo scambiato orario: apertura e massimo del giorno (prudente)
    t0 = pan["t0"]
    giorno = (np.arange(n) + h0) // 24 - t0
    ancora = int(np.isnan(mo).sum() + np.isnan(lh).sum())
    mo = np.where(np.isnan(mo), pan["open"][giorno, j], mo)
    mh = np.where(np.isnan(mh), pan["high"][giorno, j], mh)
    lh = np.where(np.isnan(lh), pan["high"][giorno, j], lh)
    R = regolamenti(s).drop_duplicates("ts")
    tasso = np.zeros(n)
    k = (R["ts"].to_numpy() // 3_600_000) - h0
    ok = (k >= 0) & (k < n)
    tasso[k[ok]] = R["tasso"].to_numpy(float)[ok]
    return {"h0": h0, "mark_open": mo, "mark_high": mh, "ultimo_high": lh, "tasso": tasso, "mark_riempite": riempite,
            "riempite_col_giorno": ancora}


def simula(S, P, F, sig, a, b, t0, H, *, regola="scritta", k=1 / 3, liquida=False, alto="mark", mmr=0.005,
           funding="regolamenti", cs=0.0015, cp=0.0006, cap=0.5, passo=None, usdt=None, ricapitalizza=False):
    """Una moneta. Patrimonio = contanti + pronti + portafoglio dei future (con la perdita aperta al prezzo di apertura).
    Il netto del giorno e' la differenza del patrimonio fra due aperture (stessa convenzione di `n95.simula_moneta`)."""
    n = b - a + 1
    netto = np.zeros(n)
    C = Qs = Qp = W = Pe = Rc = 0.0
    dentro = scoperto = False
    alto_arr = H["mark_high"] if alto == "mark" else H["ultimo_high"]
    ev = {"liquidazioni": [], "giorni_sotto_mantenimento": [], "ribilanci": 0, "margine_min": 9.9, "giorno_margine_min": "",
          "giri": 0, "notional_max_su_iniziale": 0.0}
    E_moneta = cap

    def arrotonda(q, su=False):
        if passo is None:
            return q
        x = q * usdt / passo
        return (math.ceil(x - 1e-9) if su else math.floor(x + 1e-9)) * passo / usdt

    def patrimonio(t):
        return C + Qs * S[t] + W - Qp * (P[t] - Pe)

    for i, t in enumerate(range(a, b + 1)):
        E0 = patrimonio(t)
        vuole = bool(sig[i])
        if dentro and (not vuole or scoperto):
            C += Qs * S[t] * (1 - cs) + W - Qp * (P[t] - Pe) - Qp * P[t] * cp
            Qs = Qp = W = 0.0
            dentro = scoperto = False
        if not dentro and vuole:
            noz = (E_moneta + C if ricapitalizza else cap) / 1.5   # C qui e' il guadagno accumulato della moneta (contanti)
            q = arrotonda(noz / S[t])
            if q > 0:
                Qs = Qp = q
                riserva = noz / 2
                C -= q * S[t] * (1 + cs) + riserva
                W, Pe, Rc, dentro = riserva - q * P[t] * cp, P[t], riserva, True
                ev["giri"] += 1
        elif dentro:
            if regola == "scritta":
                L = Qp * (P[t] - Pe)
                if L > Rc:
                    e = L - Rc
                    q = min(Qp, e / (S[t] * (1 - cs)))
                    Qs -= q
                    W += q * S[t] * (1 - cs) - q * P[t] * cp - q * (P[t] - Pe)
                    Qp -= q
                    Rc += e
                    ev["ribilanci"] += 1
            elif regola == "sicura":
                MB = W - Qp * (P[t] - Pe)
                if MB < k * Qp * P[t]:
                    x = (0.5 * Qp * P[t] - MB) / (S[t] * (1 - cs) - P[t] * cp + 0.5 * P[t])
                    x = min(Qp, arrotonda(x, su=True))
                    Qs -= x
                    W += x * S[t] * (1 - cs) - x * P[t] * cp - x * (P[t] - Pe)
                    Qp -= x
                    ev["ribilanci"] += 1
            if Qp <= 1e-15:
                C += Qs * S[t] * (1 - cs) + W
                Qs = Qp = W = 0.0
                dentro = False
        if dentro and Qp > 0:
            mb0 = (W - Qp * (P[t] - Pe)) / (Qp * P[t])
            ev.setdefault("aperture_sotto_zero", 0)
            ev.setdefault("aperture_sotto_mantenimento", 0)
            ev.setdefault("aperture_leva_oltre_5", 0)
            ev.setdefault("apertura_margine_min", 9.9)
            ev["aperture_sotto_zero"] += int(mb0 < 0)
            ev["aperture_sotto_mantenimento"] += int(mb0 < mmr)
            ev["aperture_leva_oltre_5"] += int(mb0 < 0.2)
            ev["apertura_margine_min"] = min(ev["apertura_margine_min"], mb0)
            ev["notional_max_su_iniziale"] = max(ev["notional_max_su_iniziale"], Qp * P[t] / (cap / 1.5))
            T = t + t0
            sotto = False
            for h in range(24):
                hh = T * 24 + h - H["h0"]
                if funding == "regolamenti" and h in (8, 16):
                    W += H["tasso"][hh] * Qp * H["mark_open"][hh]
                M = alto_arr[hh]
                MB = W - Qp * (M - Pe)
                r = MB / (Qp * M)
                if r < ev["margine_min"]:
                    ev["margine_min"], ev["giorno_margine_min"] = r, sc.data(T)
                if MB < mmr * Qp * M:
                    sotto = True
                    if liquida:
                        ev["liquidazioni"].append({"giorno": sc.data(T), "ora": h, "prezzo": (W + Qp * Pe) / (Qp * (1 + mmr)),
                                                   "entrata": Pe, "notional": Qp * M})
                        W, Qp, scoperto = 0.0, 0.0, True
                        break
            if sotto:
                ev["giorni_sotto_mantenimento"].append(sc.data(T))
            if Qp > 0:
                hh = (T + 1) * 24 - H["h0"]
                W += (H["tasso"][hh] * Qp * H["mark_open"][hh]) if funding == "regolamenti" else F[t] * Qp * P[t]
        if t == b and dentro:
            C += Qs * S[t + 1] * (1 - cs) + W - Qp * (P[t + 1] - Pe) - Qp * P[t + 1] * cp
            Qs = Qp = W = 0.0
            dentro = False
        netto[i] = patrimonio(t + 1) - E0
    return netto, ev


def episodi(giorni: list) -> list:
    if not giorni:
        return []
    g = [sc.giorno(*map(int, x.split("-"))) for x in giorni]
    out, inizio, prima = [], g[0], g[0]
    for x in g[1:]:
        if x != prima + 1:
            out.append((sc.data(inizio), sc.data(prima), prima - inizio + 1))
            inizio = x
        prima = x
    out.append((sc.data(inizio), sc.data(prima), prima - inizio + 1))
    return out


def numeri_serie(netto_giorni: np.ndarray, btc_w, giorni: np.ndarray) -> dict:
    d = pd.Series(netto_giorni, index=giorni)
    w = d.groupby(pr.lunedi_del_giorno(giorni)).sum()
    m = misura(w)
    date = pd.to_datetime(w.index.to_numpy() * 86400, unit="s")
    m["per_anno"] = {int(y): float(w[date.year == y].mean() * 52) for y in sorted(set(date.year))}
    m["ogni_anno_positivo"] = all(v > 0 for v in m["per_anno"].values())
    i = te.numeri_settimana(w)
    m |= {"asimmetria": i["asimmetria"], "curtosi": i["curtosi"], "discesa": i["discesa_max"]}
    m["serie"] = w
    return m


def scenari_margine(cartella: Path, scenari: dict, varianti=DUE, salva_come="margine") -> dict:
    pan, Op, btc_w = carica()
    t0 = pan["t0"]
    a, b = se.INIZIO - t0, pr.FINE - 1 - t0
    giorni = np.arange(se.INIZIO, pr.FINE, dtype=np.int64)
    costo = sc.costi_moneta(pan["simboli"])
    H = {s: ore_moneta(cartella, s, pan, pan["simboli"].index(s)) for s in MONETE}
    out = {"ore_mark_riempite": {s: H[s]["mark_riempite"] for s in MONETE},
           "ore_riempite_col_giorno": {s: H[s]["riempite_col_giorno"] for s in MONETE}, "scenari": {}}
    serie = {}
    for v, N in varianti.items():
        for nome, kw in scenari.items():
            tot = np.zeros(len(giorni))
            evs = {}
            for col, s in enumerate(MONETE):
                j = pan["simboli"].index(s)
                F = pan["funding"][:, j]
                sig = n95.segnale(F, a, b, N)
                kw2 = dict(kw)
                if "passo" in kw2:
                    kw2["passo"] = kw2["passo"][s]
                nt, ev = simula(Op[:, col], pan["open"][:, j], F, sig, a, b, t0, H[s], cp=float(costo[j]), **kw2)
                tot += nt
                ev["episodi_sotto_mantenimento"] = episodi(ev["giorni_sotto_mantenimento"])
                ev["giorni_sotto_mantenimento"] = len(ev["giorni_sotto_mantenimento"])
                evs[s[:3]] = ev
            m = numeri_serie(tot, btc_w, giorni)
            serie[(v, nome)] = m.pop("serie")
            out["scenari"][f"{v} {nome}"] = m | {"eventi": evs}
    return out, serie, btc_w


SCENARI = {
    "convalida (come la prova)": {"regola": "scritta", "funding": "codice"},
    "scritta, mark, conta": {"regola": "scritta"},
    "scritta, prezzo scambiato, conta": {"regola": "scritta", "alto": "ultimo"},
    "scritta, mark, liquida": {"regola": "scritta", "liquida": True},
    "sicura leva 3, mark, liquida": {"regola": "sicura", "k": 1 / 3, "liquida": True},
    "sicura leva 3, prezzo scambiato, liquida": {"regola": "sicura", "k": 1 / 3, "liquida": True, "alto": "ultimo"},
    "sicura leva 2,5, mark, liquida": {"regola": "sicura", "k": 0.4, "liquida": True},
    "sicura leva 4, mark, liquida": {"regola": "sicura", "k": 0.25, "liquida": True},
    "sicura leva 3, ricapitalizza": {"regola": "sicura", "k": 1 / 3, "liquida": True, "ricapitalizza": True},
}


def margine(cartella: Path) -> dict:
    out, serie, btc_w = scenari_margine(cartella, SCENARI)
    # convalida contro la prova
    for v in DUE:
        d0 = pd.read_csv(RIS / f"settimane_{v}.csv.gz", index_col=0)["netto"]
        out["scenari"][f"{v} convalida (come la prova)"]["diff_settimane_max"] = float(np.max(np.abs(serie[(v, "convalida (come la prova)")].to_numpy() - d0.to_numpy())))
    # Sharpe corretto per la regola sicura a leva 3 (mark), le due varianti insieme al posto di 157 A e 157 B
    nuove = {f"157 {v}": serie[(v, "sicura leva 3, mark, liquida")] for v in DUE}
    cand = {f"157 {v}": {k: out["scenari"][f"{v} sicura leva 3, mark, liquida"][k] for k in ("sharpe", "asimmetria", "curtosi", "settimane")} for v in DUE}
    c = ast.corretto_famiglie(nuove, cand)
    out["sharpe_corretto_sicura_leva3"] = {k: x["corretto"] for k, x in c["candidate"].items()}
    salva("margine", out)
    for nome, x in out["scenari"].items():
        liq = {s: len(e["liquidazioni"]) for s, e in x["eventi"].items()}
        sotto = {s: e["giorni_sotto_mantenimento"] for s, e in x["eventi"].items()}
        print(f"{nome}: annuo {x['annuo']:.4f} sharpe {x['sharpe']:.2f} t {x['t']:.1f} anni+ {x['ogni_anno_positivo']} liq {liq} sotto {sotto}")
    return out


PASSO = {"BTCUSDT": 0.001, "ETHUSDT": 0.001}   # bot/portafoglio/filtri_conto_vero.json (passo del perpetuo; il pronti ha passi piu' fini)


def filtri(cartella: Path) -> dict:
    sc_ = {}
    for usdt in (1000, 280):
        sc_[f"sicura leva 3, {usdt} USDT"] = {"regola": "sicura", "k": 1 / 3, "liquida": True, "passo": PASSO, "usdt": usdt}
        sc_[f"scritta, liquida, {usdt} USDT"] = {"regola": "scritta", "liquida": True, "passo": PASSO, "usdt": usdt}
    out, serie, _ = scenari_margine(cartella, sc_)
    # dal 2022 per la regola sicura senza passi (per il punto del 2021)
    o2, s2, _ = scenari_margine(cartella, {"sicura leva 3": {"regola": "sicura", "k": 1 / 3, "liquida": True}})
    for v in DUE:
        w = s2[(v, "sicura leva 3")]
        out["scenari"][f"{v} sicura leva 3 dal 2022"] = misura(w[w.index >= sc.giorno(2022, 1, 3)])
    salva("filtri", out)
    for nome, x in out["scenari"].items():
        if "eventi" in x:
            print(f"{nome}: annuo {x['annuo']:.4f} sharpe {x['sharpe']:.2f} anni {{{', '.join(f'{k}: {v:.3f}' for k, v in x['per_anno'].items())}}} giri "
                  f"{ {s: e['giri'] for s, e in x['eventi'].items()} } liq { {s: len(e['liquidazioni']) for s, e in x['eventi'].items()} }")
        else:
            print(nome, {k: round(v, 3) for k, v in x.items() if v is not None})
    return out


def extra(cartella: Path) -> dict:
    """Salita massima nella giornata (mark e prezzo scambiato) e prova del taglio del segnale."""
    pan, Op, _ = carica()
    out = {}
    for s in MONETE:
        j = pan["simboli"].index(s)
        H = ore_moneta(cartella, s, pan, j)
        x = {}
        for nome, arr in (("mark", H["mark_high"]), ("scambiato", H["ultimo_high"])):
            best, giorno = 0.0, ""
            for T in range(se.INIZIO, pr.FINE):
                hh = T * 24 - H["h0"]
                r = float(np.max(arr[hh:hh + 24]) / H["mark_open"][hh] - 1)
                if r > best:
                    best, giorno = r, sc.data(T)
            x[nome] = {"salita_max_nella_giornata": best, "giorno": giorno}
        # salita su 2 e 3 giorni dall'apertura (un controllo al giorno che salta un giro)
        for k in (2, 3):
            best, giorno = 0.0, ""
            for T in range(se.INIZIO, pr.FINE - k):
                hh = T * 24 - H["h0"]
                r = float(np.max(H["mark_high"][hh:hh + 24 * k]) / H["mark_open"][hh] - 1)
                if r > best:
                    best, giorno = r, sc.data(T)
            x[f"mark_{k}_giorni"] = {"salita_max": best, "giorno": giorno}
        # taglio: il segnale del giorno t non cambia se si cancella il funding dal giorno t in poi
        F = pan["funding"][:, j].copy()
        a, b = se.INIZIO - pan["t0"], pr.FINE - 1 - pan["t0"]
        rng = np.random.default_rng(157)
        diversi = 0
        for N in (30, 90):
            pieno = n95.segnale(F, a, b, N)
            for t in rng.integers(a, b + 1, 300):
                G = F.copy()
                G[t:] = rng.normal(0, 0.01, len(G) - t)
                diversi += int(n95.segnale(G, t, t, N)[0] != pieno[t - a])
        x["taglio_segnali_diversi_su_600"] = diversi
        out[s] = x
    salva("extra", out)
    print(json.dumps(out, indent=None))
    return out


def esempio() -> dict:
    """Riproduzione minima: prezzi inventati (pronti = perpetuo), funding zero, sempre dentro. Il conto della prova e questo simulatore
    danno lo stesso netto; il margine vero all'apertura dopo la regola scritta diventa negativo dal secondo giorno di rialzo."""
    S = np.array([100.0, 100, 160, 165, 170, 175, 175])
    P = S.copy()
    F = np.zeros_like(S)
    sig = np.ones(5, bool)
    a, b = 1, 5
    o = n95.simula_moneta(S, P, P, F, sig, a, b, n95.CS_STD, 0.0006)
    netto_prova = o["funding"] + o["base"] - o["spese"]
    H = {"h0": 0, "mark_open": np.repeat(P, 24), "mark_high": np.repeat(P, 24), "ultimo_high": np.repeat(P, 24), "tasso": np.zeros(len(P) * 24)}
    nt, ev = simula(S, P, F, sig, a, b, 0, H, regola="scritta", funding="codice")
    out = {"netto_prova": netto_prova.tolist(), "netto_audit": nt.tolist(), "diff": float(np.max(np.abs(nt - netto_prova))),
           "riduzioni": o["riduzioni"], "margine_vero_all_apertura_min_su_nozionale": ev["apertura_margine_min"],
           "aperture_sotto_zero": ev["aperture_sotto_zero"]}
    salva("esempio", out)
    print(json.dumps(out))
    assert out["diff"] < 1e-12 and out["aperture_sotto_zero"] >= 2
    return out


if __name__ == "__main__":
    parte = sys.argv[1]
    cart = Path(sys.argv[2]) if len(sys.argv) > 2 else None
    if parte == "scarica":
        scarica(cart)
    elif parte == "dati":
        dati(cart)
    else:
        globals()[parte](*([cart] if cart else []))
