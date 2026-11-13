"""Prova 154 (NOVANTADUESIMA.md, regole corrette il 13 novembre, commit a7c3e08): la dimensione media dello scambio fra le monete,
decisa ogni giorno come G1 (segnale S = media corta / media lunga di quote_volume/count; long il quinto piu' alto).

Uso (dalla radice del repo):  python3 -m research.programma7.novantaduesima [controllo|calcola]
"""
from __future__ import annotations

import json
import math
import os
import subprocess
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

QUI = Path(__file__).resolve().parent
RIS = QUI / "risultati_novantaduesima"
SCRATCH = Path("/tmp/claude-0/-home-user-agentic-trading-system/9da12ffe-13c5-5904-8f7e-5ce576103042/scratchpad")
SEME = 154
MIN_SCAMBI = 100
# variante: (finestra corta, finestra lunga, minimo valido corta, minimo valido lunga)  -- riga «Regole corrette», punto 3
VARIANTI = {"A": (3, 30, 2, 15), "B": (7, 90, 4, 45)}


def candele_count(simbolo: str) -> pd.DataFrame:
    """Come `seconda.candele` (stessi file, archivio mensile vince sui giorni dall'interfaccia pubblica) ma tiene anche `count`."""
    from research.programma5.strumenti import motore5 as m5
    from research.programma6.seconda import DATI
    file = sorted((DATI / simbolo / "giorni").glob("*.zip"))
    if not file:
        return pd.DataFrame()
    api = [pd.read_csv(p) for p in sorted((DATI / simbolo / "giorni_api").glob("*.csv"))]
    df = pd.concat(api + [m5._csv_da_zip(p, m5.KLINE) for p in file], ignore_index=True)
    df["giorno"] = m5._ms(df["open_time"]) // 86_400_000
    df = df.drop_duplicates("giorno", keep="last").set_index("giorno").sort_index()
    return df[["close", "quote_volume", "count"]].astype(float)


def matrice_count(pan: dict, log=print) -> np.ndarray:
    f = SCRATCH / "count_matrice.npy"
    T, S = pan["close"].shape
    if f.exists():
        M = np.load(f)
        if M.shape == (T, S):
            return M
    M = np.full((T, S), np.nan)
    for j, s in enumerate(pan["simboli"]):
        c = candele_count(s)
        if len(c):
            r = c.index.to_numpy() - pan["t0"]
            ok = (r >= 0) & (r < T)
            M[r[ok], j] = c["count"].to_numpy()[ok]
        if j % 100 == 0:
            log(f"[count] {j}/{S}")
    SCRATCH.mkdir(parents=True, exist_ok=True)
    np.save(f, M)
    return M


def controllo(pan: dict) -> dict:
    """Su 3 monete: close e quote_volume del lettore nuovo uguali a quelli di `seconda.candele` e a quelli del pannello."""
    from research.programma6 import seconda as sc
    out = {}
    for s in ("BTCUSDT", "ETHUSDT", "SOLUSDT"):
        a, b = candele_count(s), sc.candele(s)
        comuni = a.index.intersection(b.index)
        j = pan["simboli"].index(s)
        r = comuni.to_numpy() - pan["t0"]
        dentro = (r >= 0) & (r < pan["close"].shape[0])
        r, comuni_p = r[dentro], comuni[dentro]
        out[s] = {"giorni": int(len(a)), "giorni_seconda": int(len(b)), "uguali_indici": bool(a.index.equals(b.index)),
                  "close_max_diff": float(np.abs(a.loc[comuni, "close"] - b.loc[comuni, "close"]).max()),
                  "qv_max_diff": float(np.abs(a.loc[comuni, "quote_volume"] - b.loc[comuni, "quote_volume"]).max()),
                  "close_pannello_max_diff": float(np.nanmax(np.abs(pan["close"][r, j] - a.loc[comuni_p, "close"].to_numpy()))),
                  "count_mancanti_o_zero": int((~(a["count"] > 0)).sum()), "count_sotto_100": int((a["count"] < MIN_SCAMBI).sum())}
    return out


def segnale(D: np.ndarray, corta: int, lunga: int, mc: int, ml: int) -> np.ndarray:
    """S[i] = media di D sui `corta` giorni i-corta..i-1 / media sui `lunga` giorni i-lunga..i-1 (solo giorni validi, cioe' finiti);
    nan se i giorni validi sono meno di mc (corta) o ml (lunga)."""
    ok = np.isfinite(D)
    X = np.where(ok, D, 0.0)
    cx, co = np.vstack([np.zeros((1, D.shape[1])), np.cumsum(X, axis=0)]), np.vstack([np.zeros((1, D.shape[1])), np.cumsum(ok, axis=0)])
    S = np.full(D.shape, np.nan)
    for i in range(lunga, D.shape[0]):
        ns, nl = co[i] - co[i - corta], co[i] - co[i - lunga]
        with np.errstate(all="ignore"):
            ms, ml_ = (cx[i] - cx[i - corta]) / ns, (cx[i] - cx[i - lunga]) / nl
            v = (ns >= mc) & (nl >= ml) & (ml_ > 0)
            S[i] = np.where(v, ms / ml_, np.nan)
    return S


def main_calcola():
    os.environ.setdefault("CACHE_G1N", str(SCRATCH / "cache_g1n"))
    import research.programma7.revisione_g1n.nucleo as nu
    from research.programma6 import asticella as ast, seconda as sc, terza as te
    from research.programma7.revisione_g1n import analisi as an
    from research.src import prove
    RIS.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    pan = sc.pannello()
    sim = pan["simboli"]
    ctl = controllo(pan)
    print("[controllo]", json.dumps(ctl)[:600], flush=True)
    CN = matrice_count(pan)
    QV = pan["quote_volume"]
    with np.errstate(all="ignore"):
        D = np.where(np.isfinite(CN) & (CN >= MIN_SCAMBI), QV / CN, np.nan)
    D = np.where(np.isfinite(D) & (D > 0), D, np.nan)
    giorni = np.arange(sc.giorno(2022, 1, 1), an.FINE, dtype=np.int64)
    idx = giorni - pan["t0"]
    U = nu.universo_giorni(pan, idx)
    rc = nu.ritorni_chiusura(pan["close"])
    R = nu.ritorni_tenuta(pan["open"], pan["close"])[idx]
    F = np.nan_to_num(pan["funding"][idx])
    costo = np.array([nu.costo_di(s_) for s_ in sim])
    ore = an.candele_ore(sim)
    print(f"[pronto] {time.time() - t0:.0f}s", flush=True)

    def pesi_da(S):
        W = np.zeros((len(idx), len(sim)))
        lunghi, corti = set(), set()
        for k, i in enumerate(idx):
            sig = nu.sigma30(rc, i)
            ct = np.where(np.isfinite(sig), S[k], np.nan)      # unica differenza da nucleo.pesi: ct = S (e W, senza il fattore beta)
            W[k], lunghi, corti = nu.passo_banda(ct, U[k], sig, lunghi, corti)
        return W

    def conto_w(W):
        return an.conto("x", W, R, F, costo, giorni, sim, ore)

    def sett(dd):
        return an.settimane(dd)["netto"]

    def esame_serie(dd):
        w = sett(dd)
        z = te.numeri_settimana(w)
        z["t"] = z["sharpe"] * math.sqrt(z["settimane"] / 52)
        a = an.anno(w.index)
        z["per_anno"] = {int(y): float(w[a == y].mean() * 52) for y in sorted(set(a))}
        return z

    def senza10(x):
        v = np.sort(np.asarray(x))[:-10]
        return float(v.mean() * 365)

    ris, serie, W_ = {}, {}, {}
    for v, (c, l, mc, ml) in VARIANTI.items():
        tv = time.time()
        rv = {}
        try:
            S = segnale(D, c, l, mc, ml)[idx]
            n_ok = (np.isfinite(S) & U)
            rv["giorni_con_segnale"] = int((n_ok.sum(axis=1) >= nu.MIN_MONETE).sum())
            rv["monete_medie_al_giorno"] = float(n_ok.sum(axis=1).mean())
            W = pesi_da(S)
            W_[v] = (W, S)
            dd = conto_w(W)
            serie[v] = sett(dd)
            rv.update(esame_serie(dd))
            rv["giorni_con_posizioni"] = int((np.abs(W).sum(axis=1) > 0).sum())
            rv["rendimento_netto_annuo_giorni"] = float(dd["netto"].mean() * 365)
            rv["discesa_giornaliera"] = nu.numeri(dd["netto"].to_numpy(), 365)["discesa"]
            rv["sharpe_giornaliero_365"] = nu.numeri(dd["netto"].to_numpy(), 365)["sharpe"]
            rv["giro_medio_giorno"] = float(np.abs(np.diff(W, axis=0, prepend=0)).sum(axis=1).mean())
            rv["spese_annue"] = float(dd["spese"].mean() * 365)
            rv["funding_annuo"] = float(dd["funding"].mean() * 365)
            rv["variazioni_e_a_limite"] = [dd.attrs["variazioni"], dd.attrs["a_limite"]]
            rv["netto_costi_x3_annuo"] = float(dd["netto_triplo"].mean() * 365)
            for lato, WL in (("long", np.where(W > 0, W, 0.0)), ("short", np.where(W < 0, W, 0.0))):
                dl = conto_w(WL)
                rv[f"lato_{lato}"] = {"annuo": float(dl["netto"].mean() * 365), "annuo_senza_10_giorni_migliori": senza10(dl["netto"]),
                                       "per_anno": {int(y): float(dl["netto"][an.anno(giorni) == y].mean() * 365) for y in sorted(set(an.anno(giorni)))}}
            dc = conto_w(pesi_da(-S))                           # controllo al contrario (descrittivo, non una variante)
            ec = esame_serie(dc)
            rv["controllo_al_contrario"] = {"annuo": ec["annuo"], "sharpe": ec["sharpe"], "per_anno": ec["per_anno"]}
            pd.DataFrame({"netto": dd["netto"], "lordo": dd["lordo"], "spese": dd["spese"], "funding": dd["funding"]}).to_csv(RIS / f"giorni_{v}.csv.gz")
            serie[v].to_csv(RIS / f"settimane_{v}.csv.gz")
        except Exception as ex:  # anche una variante fallita si registra
            rv["errore"] = repr(ex)
        ris[v] = rv
        print(f"[{v}] {time.time() - tv:.0f}s", flush=True)

    # correlazioni dalle serie del mazzo (G1 = "57 G1", F5 = "24 F5")
    prove_mazzo = {n: s_ for n, s_, _ in ast.le_prove() if s_ is not None}
    g1 = prove_mazzo.get("57 G1")
    f5 = prove_mazzo.get("24 F5")
    corr = {"serie_mazzo_trovate": [n for n in ("57 G1", "24 F5") if n in prove_mazzo]}
    for v in serie:
        corr[v] = {}
        for nome, ref in (("G1", g1), ("F5", f5)):
            if ref is not None:
                c = serie[v].index.intersection(ref.index)
                corr[v][f"{nome}_settimanale"] = float(np.corrcoef(serie[v].loc[c], ref.loc[c])[0, 1])
                corr[v][f"settimane_comuni_{nome}"] = int(len(c))
        corr[v]["G1_ricalcolata_giornaliera"] = None
    # G1 ricalcolata con la funzione scritta di nucleo (stesso universo e giorni), come controllo della serie del mazzo
    W1, _, _ = nu.pesi(pan, idx, U)
    d1 = conto_w(W1)
    for v in serie:
        corr[v]["G1_ricalcolata_giornaliera"] = float(np.corrcoef(conto_w(W_[v][0])["netto"], d1["netto"])[0, 1])
        c = serie[v].index.intersection(sett(d1).index)
        corr[v]["G1_ricalcolata_settimanale"] = float(np.corrcoef(serie[v].loc[c], sett(d1).loc[c])[0, 1])

    corretto = {}
    ok = {v: serie[v] for v in serie}
    if ok:
        cand = {f"154 {v}": {k: ris[v][k] for k in ("sharpe", "settimane", "asimmetria", "curtosi")} for v in ok}
        corretto = ast.corretto_famiglie({f"154 {v}": s_ for v, s_ in ok.items()}, cand)
        for v in ok:
            ris[v]["sharpe_corretto_famiglie"] = corretto["candidate"][f"154 {v}"]
    commit = subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True).stdout.strip()
    esito = {}
    for v in VARIANTI:
        rv = ris[v]
        if "errore" in rv:
            esito[v] = "errore"
        else:
            anni_ok = all(x > 0 for x in rv["per_anno"].values())
            sc_ = rv["sharpe_corretto_famiglie"]["corretto"]
            lati = all(rv[f"lato_{l}"]["annuo_senza_10_giorni_migliori"] >= 0 for l in ("long", "short"))
            rv["esame"] = {"netto_positivo": rv["annuo"] > 0, "ogni_anno_positivo": anni_ok, "t_almeno_3": rv["t"] >= 3,
                           "sharpe_corretto_almeno_0.80": sc_ >= 0.80, "lati_senza_10_giorni_ok": lati}
            esito[v] = "promettente" if all(rv["esame"].values()) else "non promettente"
        misure = {k: rv.get(k) for k in ("annuo", "sharpe", "t", "discesa_max", "per_anno", "giorni_con_segnale", "spese_annue")}
        misure["sharpe_corretto"] = rv.get("sharpe_corretto_famiglie", {}).get("corretto")
        prove.registra("novantaduesima", v, {"variante": v, "finestre": list(VARIANTI[v][:2]), "validi_min": list(VARIANTI[v][2:]),
                       "banda": [0.2, 0.4], "vol_giorni": 30, "periodo": "2022-01-01..2026-10-04", "min_scambi": MIN_SCAMBI},
                       "giornaliera (settimane per lo Sharpe)", rv.get("giorni_con_posizioni", 0), misure, esito[v],
                       note=rv.get("errore", ""), seme=SEME, commit=commit)
    out = {"controllo_lettore": ctl, "varianti": ris, "correlazioni": corr, "esito": esito, "commit": commit,
           "famiglie": {k: corretto.get(k) for k in ("serie", "senza_serie", "famiglie", "in_v", "deviazione_v", "taglio")}}
    (RIS / "esame.json").write_text(json.dumps(out, indent=1, default=str))
    for v in VARIANTI:
        r = ris[v]
        print(v, esito[v], {k: r.get(k) for k in ("annuo", "sharpe", "t", "discesa_max", "per_anno")},
              "corretto", r.get("sharpe_corretto_famiglie", {}).get("corretto"), "corr", corr.get(v), flush=True)


if __name__ == "__main__":
    main_calcola()
