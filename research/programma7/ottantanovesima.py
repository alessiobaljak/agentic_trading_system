"""Programma 7, ottantanovesima prova (prova 151 del registro): il weekend dei perpetui su azioni, il rimbalzo del lunedi' (`OTTANTANOVESIMA.md`).

Fasi:
  python3 -m research.programma7.ottantanovesima elenco    # scrive l'elenco dei contratti ammessi/esclusi (PRIMA di ogni calcolo)
  python3 -m research.programma7.ottantanovesima esegui    # segnale, conto, esame, registro delle varianti
Le candele a 1 ora si scaricano prima con `python3 -m research.programma6.scarico_ore <SIMBOLI>` (elenco in `ELENCO_CONTRATTI.json`).
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd

QUI = Path(__file__).parent
OUT = QUI / "risultati_ottantanovesima"
ID = "ottantanovesima"
SEME = 2026
N_PROVE = 309                      # 308 prima di questa prova + questa
SOGLIA_SHARPE_CORRETTO, SOGLIA_T = 0.80, 3.0
TOP, LATO, MIN_CONTRATTI, MIN_STORIA, FINESTRA_VOL = 30, 6, 20, 40, 28
MAKER, TAKER = 0.0002, 0.0005

# Contratti tolti (decisione di chi esegue, scritta prima del calcolo; le regole la affidano a una lista in un file)
NON_AMERICANI = {
    "ASMLUSDT": "citato nelle regole", "BYDUSDT": "citato nelle regole", "EWJUSDT": "citato nelle regole",
    "EWYUSDT": "citato nelle regole", "EWZUSDT": "citato nelle regole",
    "HK0625USDT": "Hong Kong", "HK0700USDT": "Hong Kong", "HK0992USDT": "Hong Kong", "HK1810USDT": "Hong Kong",
    "KODEX200USDT": "Corea (fondo)", "KUAISHOUUSDT": "Hong Kong", "LGELECTRONICSUSDT": "Corea", "MEITUANUSDT": "Hong Kong",
    "MINIMAXUSDT": "Hong Kong", "NAVERUSDT": "Corea", "POPMARTUSDT": "Hong Kong", "SAMSUNGUSDT": "Corea",
    "SAMSUNGEMUSDT": "Corea", "SKHYNIXUSDT": "Corea", "SKHYUSDT": "Corea (nato 2026-04, nome simile a SK Hynix: dubbio)",
    "HANMIUSDT": "Corea", "HYUNDAIUSDT": "Corea", "TENCENTUSDT": "Hong Kong", "UNITREEUSDT": "Cina", "ZHIPUUSDT": "Hong Kong",
    "CXMTUSDT": "Cina", "GIGADEVUSDT": "Cina", "KORUUSDT": "fondo a leva sulla Corea (come EWY)",
}
SENZA_QUOTAZIONE_USA = {"ANTHROPICUSDT": "non quotata", "OPENAIUSDT": "non quotata", "SPCXUSDT": "non quotata (pre-quotazione)"}
LEVA_2X = {"CSOPSAMSUNG2LUSDT": "2L", "CSOPSKHYNIX2LUSDT": "2L"}
MATERIE_PRIME = {"BZUSDT": "petrolio", "CLUSDT": "petrolio"}


def candidati() -> list:
    from research.programma6.esclusi import ESCLUSI
    i0 = ESCLUSI.index("AAOIUSDT")
    return list(ESCLUSI[i0:])        # azioni e fondi + aggiunte del 19 ottobre (SECONDA.md, sezione 9)


def elenco() -> dict:
    tolti = {**{k: "non americano: " + v for k, v in NON_AMERICANI.items()},
             **{k: "senza quotazione americana: " + v for k, v in SENZA_QUOTAZIONE_USA.items()},
             **{k: "leva 2L" for k in LEVA_2X}, **{k: "materia prima: " + v for k, v in MATERIE_PRIME.items()}}
    c = candidati()
    ammessi = [s for s in c if s not in tolti]
    out = {"candidati": len(c), "ammessi": ammessi, "tolti": {s: tolti[s] for s in c if s in tolti}}
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "ELENCO_CONTRATTI.json").write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")
    md = ["# Elenco dei contratti della prova 151 (scritto prima di ogni calcolo)", "",
          f"Partenza: i {len(c)} contratti di `esclusi.py` da AAOIUSDT in poi (azioni e fondi, piu' le aggiunte del 19 ottobre 2026 di "
          "`SECONDA.md`, sezione 9). Tolti secondo le regole: leva 2L, non americani, materie prime; tolti per lettura mia: senza "
          "quotazione americana. Restano le azioni americane, i certificati americani (BABA, PDD, TSM, NVO, SONY, NOK) e i fondi "
          "americani, anche a leva 3x o inversi (le regole tolgono solo i «2L»).", "",
          f"## Ammessi ({len(ammessi)})", ", ".join(ammessi), "", f"## Tolti ({len(out['tolti'])})"]
    md += [f"* {s}: {m}" for s, m in out["tolti"].items()]
    (OUT / "ELENCO_CONTRATTI.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    return out




# ----------------------------------------------------------------------------------------------------------------- dati
FESTIVI_USA = {"2026-01-19": "Martin Luther King", "2026-02-16": "Presidents Day", "2026-05-25": "Memorial Day", "2026-09-07": "Labor Day"}
LETTURE = [
    "prezzo 'alle 00:00 del lunedi'' = apertura della candela di 1 ora delle 00:00 UTC; base = apertura della candela delle 22:00 UTC del venerdi' (50 ore prima)",
    "universo del lunedi': contratti con almeno 40 giorni di storia (prima candela almeno 960 ore prima di lunedi' 00:00) e con tutte le candele che servono "
    "(venerdi' 22, lunedi' 00, 01, 02, 13 e 22); fra questi i 30 con piu' volume in dollari (somma del volume in dollari delle candele a 1 ora) delle 672 ore prima",
    "con 20-29 contratti il quinto = parte intera di n/5 (pesi uguali, ogni lato al 100%)",
    "ordine d'entrata: limite a 0,02% sull'apertura delle 01:00 per un'ora: preso se il minimo dell'ora e' sotto l'apertura (acquisto) o il massimo sopra (vendita), "
    "costo 0,02%; altrimenti mercato 0,05% + scarto piu' lo spostamento del prezzo nell'ora (stessa regola di `cinquantaseiesima.costo_limite`); uscita a mercato 0,05% + scarto",
    "rendimento di un contratto = apertura 22:00 / apertura 01:00 - 1; funding = tassi dei regolamenti con tempo da 01:00 (incluso) a 22:00 (escluso), long paga, short incassa",
    "scarto 0,02% (0,01% BTC/ETH/SOL, che qui non ci sono); controllo informativo con 0,05% per tutti",
    "quarto trimestre = ottobre e primo lunedi' di novembre; trimestre negativo = somma dei rendimenti settimanali sotto zero",
]


def carica_ore(s: str) -> pd.DataFrame:
    """Candele da 1 ora (indice = ora dall'epoca) con il volume in dollari, dai file dell'archivio gia' scaricati."""
    from research.programma5.strumenti import motore5 as m5
    from research.programma6 import quarta as qa
    file = sorted((qa.DATI / s / "ore").glob("*.zip"))
    if not file:
        return pd.DataFrame()
    df = pd.concat([m5._csv_da_zip(p, m5.KLINE) for p in file], ignore_index=True)
    df["ora"] = m5._ms(df["open_time"]) // 3_600_000
    df = df.drop_duplicates("ora", keep="last").set_index("ora").sort_index()
    df = df[["open", "high", "low", "close", "quote_volume"]].astype(float)
    return df.reindex(np.arange(df.index.min(), df.index.max() + 1))


def carica_funding(s: str) -> np.ndarray:
    from research.programma6 import seconda as sc
    from research.src.dati import funding_da_zip
    righe = []
    for p in sorted((sc.DATI / s / "funding").glob("*.zip")):
        righe += funding_da_zip(p)
    a = np.array([(r[0], r[2]) for r in righe], float).reshape(-1, 2)
    return a[np.argsort(a[:, 0])] if len(a) else a


def costo_ingresso(o, h, l, p1, compra, a_mercato):
    if (l < o) if compra else (h > o):
        return MAKER, True
    contro = (p1 / o - 1) if compra else (1 - p1 / o)
    return a_mercato + contro, False


def lunedi_da_provare() -> list:
    d0, d1 = pd.Timestamp("2026-01-05"), pd.Timestamp("2026-11-02")
    return [int(t.timestamp() // 86400) for t in pd.date_range(d0, d1, freq="7D")]


def conto_settimane(dati: dict, fund: dict, scarto_alt: float | None = None):
    """Righe per lunedi' e per contratto. ``scarto_alt``: scarto di prezzo diverso da quello ufficiale (controllo)."""
    from research.programma5.strumenti import motore5 as m5
    sett, dett = [], []
    for d in lunedi_da_provare():
        h0 = d * 24
        data = str(pd.Timestamp(d * 86400, unit="s").date())
        need = [h0 - 50, h0, h0 + 1, h0 + 2, h0 + 13, h0 + 22]
        c = []
        for s, b in dati.items():
            if b.index.min() > h0 - MIN_STORIA * 24 or b.index.max() < h0 + 22:
                continue
            ok = True
            for h in need:
                if h not in b.index or not np.isfinite(b.loc[h, ["open", "high", "low", "close"]].to_numpy()).all():
                    ok = False
                    break
            if not ok:
                continue
            vol = float(np.nansum(b.loc[max(b.index.min(), h0 - FINESTRA_VOL * 24):h0 - 1, "quote_volume"].to_numpy()))
            c.append((s, vol))
        if len(c) < MIN_CONTRATTI:
            sett.append({"lunedi": data, "contratti": len(c), "fatta": False})
            continue
        c = sorted(c, key=lambda x: -x[1])[:TOP]
        simb = [s for s, _ in c]
        R = np.array([math.log(dati[s].loc[h0, "open"] / dati[s].loc[h0 - 50, "open"]) for s in simb])
        Rm = R - np.median(R)
        k = len(simb) // 5
        ordine = np.argsort(Rm, kind="stable")
        lunghi, corti = ordine[:k], ordine[-k:]
        riga = {"lunedi": data, "festivo": FESTIVI_USA.get(data, ""), "contratti": len(simb), "fatta": True, "per_lato": k}
        gross, g1, g2, costo, costo_alt, fl, ncost, npreso = 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0, 0
        lato = {"long": 0.0, "short": 0.0}
        for lato_n, idxs, sgn in (("long", lunghi, 1), ("short", corti, -1)):
            for i in idxs:
                s = simb[i]
                b = dati[s]
                o1, e = b.loc[h0 + 1, "open"], b.loc[h0 + 22, "open"]
                m13 = b.loc[h0 + 13, "open"]
                r = sgn * (e / o1 - 1)
                lato[lato_n] += r / k
                g1 += sgn * (m13 / o1 - 1) / k
                g2 += sgn * (e / m13 - 1) / k
                sc_uff = m5.scarto(s)
                cc = []
                for sca in (sc_uff, 0.0005 if scarto_alt is None else scarto_alt):
                    am = TAKER + sca
                    ce, preso = costo_ingresso(o1, b.loc[h0 + 1, "high"], b.loc[h0 + 1, "low"], b.loc[h0 + 2, "open"], sgn > 0, am)
                    cc.append(ce + am)
                    if sca == sc_uff:
                        npreso += preso
                        ncost += 1
                costo += cc[0] / k
                costo_alt += cc[1] / k
                f = fund[s]
                t0, t1 = (h0 + 1) * 3_600_000, (h0 + 22) * 3_600_000
                tassi = f[(f[:, 0] >= t0) & (f[:, 0] < t1), 1].sum() if len(f) else 0.0
                fl += sgn * tassi / k          # long paga (+), short incassa: costo = sgn * tasso
                dett.append({"lunedi": data, "contratto": s, "lato": lato_n, "R_senza_mediana": float(Rm[i]), "rendimento": float(r),
                             "tassi_funding": float(tassi)})
        riga.update({"lordo": lato["long"] + lato["short"], "long": lato["long"], "short": lato["short"], "prima_borsa": g1, "dentro_borsa": g2,
                     "spese": costo, "spese_scarto_005": costo_alt, "funding": fl, "limite_eseguiti": npreso / ncost,
                     "netto": lato["long"] + lato["short"] - costo - fl, "netto_scarto_005": lato["long"] + lato["short"] - costo_alt - fl})
        sett.append(riga)
    return pd.DataFrame(sett), pd.DataFrame(dett)


def numeri(x: pd.Series) -> dict:
    from research.programma6 import terza as te
    return te.numeri_settimana(x)


def esegui():
    import research.programma6.asticella as ast
    from research.programma6 import terza as te
    from research.src.prove import registra
    OUT.mkdir(parents=True, exist_ok=True)
    ammessi = json.loads((OUT / "ELENCO_CONTRATTI.json").read_text())["ammessi"]
    par = {"contratti": "elenco ELENCO_CONTRATTI.json (%d)" % len(ammessi), "top": TOP, "lato": "quinto (6 per lato)", "segnale": "R weekend meno mediana, long i bassi",
           "entrata": "01:00 UTC lunedi', limite 0,02% un'ora poi mercato 0,05%", "uscita": "22:00 UTC lunedi' a mercato", "scarto": 0.0002,
           "dal": "primo lunedi' con almeno 20 contratti", "al": "2026-11-02", "N_prove": N_PROVE}
    try:
        dati = {s: carica_ore(s) for s in ammessi}
        dati = {s: b for s, b in dati.items() if len(b)}
        fund = {s: carica_funding(s) for s in dati}
        sett, dett = conto_settimane(dati, fund)
        sett.to_csv(OUT / "settimane.csv", index=False)
        dett.to_csv(OUT / "contratti_per_settimana.csv", index=False)
        f = sett[sett["fatta"]].reset_index(drop=True)
        netto = f["netto"]
        e = numeri(netto)
        e["t"] = e["sharpe"] * math.sqrt(e["settimane"] / 52)
        prove = ast.le_prove()
        serie = {n: ast.periodo(s) for n, s, _ in prove if s is not None}
        serie.update({n: ast.periodo(s) for n, s in ast.serie_nuove().items()})
        soli = [sr for _, s, sr in prove if s is None]
        gr = ast.gruppi(serie, ast.TAGLIO)
        sr_base = ast.per_v(gr, soli, True)
        sr_v = sr_base + [e["sharpe"]]
        e["sharpe_corretto"] = te.sharpe_corretto(e["sharpe"], e["settimane"], e["asimmetria"], e["curtosi"], sr_v, 52, n_prove=N_PROVE)
        e["sharpe_corretto_solo_gruppi"] = te.sharpe_corretto(e["sharpe"], e["settimane"], e["asimmetria"], e["curtosi"], sr_base, 52, n_prove=N_PROVE)
        e["cumulato"] = float((1 + netto).prod() - 1)
        e["prima_data"], e["ultima_data"] = f["lunedi"].iloc[0], f["lunedi"].iloc[-1]
        e["settimane_positive"] = int((netto > 0).sum())
        e["settimane_saltate_per_pochi_contratti"] = int((~sett["fatta"]).sum())
        # trimestri
        tr = pd.PeriodIndex(pd.to_datetime(f["lunedi"]), freq="Q").astype(str)
        e["per_trimestre"] = {str(k): float(v) for k, v in netto.groupby(tr.to_numpy()).sum().items()}
        e["trimestri_negativi"] = sum(1 for v in e["per_trimestre"].values() if v < 0)
        # lati e senza i 3 lunedi' migliori
        migl = netto.nlargest(3).index
        senza = f.drop(migl)
        e["senza_3_migliori"] = {"netto_media": float(senza["netto"].mean()), "long_media": float(senza["long"].mean()),
                                 "short_media": float(senza["short"].mean())}
        e["lati"] = {"long_media": float(f["long"].mean()), "short_media": float(f["short"].mean()), "long_annuo": float(f["long"].mean() * 52),
                     "short_annuo": float(f["short"].mean() * 52)}
        e["divisione"] = {"prima_borsa_media": float(f["prima_borsa"].mean()), "dentro_borsa_media": float(f["dentro_borsa"].mean()),
                          "prima_borsa_t": float(f["prima_borsa"].mean() / f["prima_borsa"].std(ddof=1) * math.sqrt(len(f))),
                          "dentro_borsa_t": float(f["dentro_borsa"].mean() / f["dentro_borsa"].std(ddof=1) * math.sqrt(len(f)))}
        e["costi"] = {"spese_settimana": float(f["spese"].mean()), "spese_annue": float(f["spese"].mean() * 52), "funding_settimana": float(f["funding"].mean()),
                      "limite_eseguiti": float(f["limite_eseguiti"].mean()), "giro_per_settimana": 4.0, "lordo_annuo": float(f["lordo"].mean() * 52)}
        e["scarto_005"] = numeri(f["netto_scarto_005"]) | {"t": numeri(f["netto_scarto_005"])["sharpe"] * math.sqrt(len(f) / 52)}
        e["contratti_per_settimana"] = {"min": int(f["contratti"].min()), "mediana": float(f["contratti"].median()), "max": int(f["contratti"].max())}
        e["festivi"] = {r["lunedi"]: [r["festivo"], round(float(r["netto"]), 5)] for _, r in f[f["festivo"] != ""].iterrows()}
        # esame
        perche = []
        if not e["annuo"] > 0:
            perche.append("netto non positivo")
        if e["trimestri_negativi"] > 1:
            perche.append(f"{e['trimestri_negativi']} trimestri negativi")
        if e["t"] < SOGLIA_T:
            perche.append(f"t {e['t']:.2f} sotto 3")
        if e["sharpe_corretto"] < SOGLIA_SHARPE_CORRETTO:
            perche.append(f"Sharpe corretto {e['sharpe_corretto']:.2f} sotto 0,80")
        if e["senza_3_migliori"]["long_media"] < 0 or e["senza_3_migliori"]["short_media"] < 0:
            perche.append("un lato da solo sotto zero senza i 3 lunedi' migliori")
        corto = e["t"] < SOGLIA_T and e["settimane"] < 40
        e["esito"] = ("passa l'esame: va a backtest-auditor" if not perche else
                      ("dati troppo corti (" if corto else "non passa (") + "; ".join(perche) + ")")
        e["dati_troppo_corti"] = bool(corto)
        registra(ID, "unica", par, "settimana (lunedi' 01:00-22:00 UTC)", int(e["settimane"]),
                 {k: round(float(v), 4) for k, v in {"annuo": e["annuo"], "sharpe": e["sharpe"], "t": e["t"], "sharpe_corretto": e["sharpe_corretto"],
                                                     "discesa_max": e["discesa_max"], "spese_annue": e["costi"]["spese_annue"],
                                                     "sharpe_scarto_005": e["scarto_005"]["sharpe"], "annuo_scarto_005": e["scarto_005"]["annuo"]}.items()}
                 | {"settimane_positive": f"{e['settimane_positive']}/{e['settimane']}"}, e["esito"], seme=SEME,
                 note=f"{len(dati)} contratti con candele; contratti per settimana {e['contratti_per_settimana']}; controllo scarto 0,05% solo informativo")
    except Exception as ex:  # noqa: BLE001
        registra(ID, "unica", par, "settimana (lunedi' 01:00-22:00 UTC)", 0, {}, "errore", note=repr(ex), seme=SEME)
        raise
    (OUT / "esame.json").write_text(json.dumps({"letture": LETTURE, "N_prove": N_PROVE, **e}, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    scrivi(e, len(dati))
    return e


def scrivi(e: dict, n_con_candele: int):
    pc = lambda v: f"{100 * v:.2f}%"
    L = ["# Risultati della prova 151 (ottantanovesima): il weekend dei perpetui su azioni, il rimbalzo del lunedi'", "",
         "Calcolo di `ottantanovesima.py` (seme 2026), una sola variante come scritto in `OTTANTANOVESIMA.md`. Elenco dei contratti: "
         "`risultati_ottantanovesima/ELENCO_CONTRATTI.md` (fissato prima del calcolo).", "",
         f"**Esito secondo le regole: {e['esito']}**", "",
         f"* Lunedi' usati: {e['settimane']} (dal {e['prima_data']} al {e['ultima_data']}); saltati per meno di 20 contratti: {e['settimane_saltate_per_pochi_contratti']}. "
         f"Contratti per lunedi': min {e['contratti_per_settimana']['min']}, mediana {e['contratti_per_settimana']['mediana']:.0f}, max {e['contratti_per_settimana']['max']} "
         f"(contratti dell'elenco con candele: {n_con_candele}).",
         f"* Netto: {pc(e['annuo'])} l'anno (media per lunedi' x 52), {pc(e['cumulato'])} sull'intero periodo; discesa piu' grande {pc(e['discesa_max'])}.",
         f"* Sharpe {e['sharpe']:.2f}; t {e['t']:.2f}; Sharpe corretto (N={N_PROVE}) {e['sharpe_corretto']:.2f} (solo gruppi: {e['sharpe_corretto_solo_gruppi']:.2f}).",
         f"* Settimane positive: {e['settimane_positive']} su {e['settimane']}. Per trimestre (somma dei rendimenti): "
         + ", ".join(f"{k} {pc(v)}" for k, v in e["per_trimestre"].items()) + f"; trimestri negativi {e['trimestri_negativi']}.",
         f"* Lato long {pc(e['lati']['long_annuo'])} l'anno, lato short {pc(e['lati']['short_annuo'])} l'anno (lordi di costi e funding). "
         f"Senza i 3 lunedi' migliori, media per lunedi': netto {pc(e['senza_3_migliori']['netto_media'])}, long {pc(e['senza_3_migliori']['long_media'])}, short {pc(e['senza_3_migliori']['short_media'])}.",
         f"* Scarto di prezzo 0,05% (controllo, non entra nel giudizio): {pc(e['scarto_005']['annuo'])} l'anno, Sharpe {e['scarto_005']['sharpe']:.2f}, t {e['scarto_005']['t']:.2f}.",
         f"* Costi: lordo {pc(e['costi']['lordo_annuo'])} l'anno; spese {pc(e['costi']['spese_annue'])} l'anno ({pc(e['costi']['spese_settimana'])} per lunedi', giro 4 volte il capitale), "
         f"funding {pc(e['costi']['funding_settimana'])} per lunedi'; ordini limite eseguiti {pc(e['costi']['limite_eseguiti'])}.",
         f"* Dove nasce (descrittivo, lordo): prima della Borsa (01:00-13:00) {pc(e['divisione']['prima_borsa_media'])} per lunedi' (t {e['divisione']['prima_borsa_t']:.2f}); "
         f"dentro la Borsa (13:00-22:00) {pc(e['divisione']['dentro_borsa_media'])} (t {e['divisione']['dentro_borsa_t']:.2f}).",
         f"* Lunedi' festivi americani (fatti lo stesso): {json.dumps(e['festivi'], ensure_ascii=False)}.", "",
         "## Letture delle regole", ""] + [f"* {x}" for x in LETTURE]
    (QUI / "RISULTATI_OTTANTANOVESIMA.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L[:14]))


if __name__ == "__main__":
    if sys.argv[1:] == ["elenco"]:
        r = elenco()
        print(len(r["ammessi"]), "ammessi,", len(r["tolti"]), "tolti")
    elif sys.argv[1:] == ["esegui"]:
        esegui()
