"""Audit di G1 (12 nov 2026), seconda parte: dati, rischio (leva, liquidazione, stop, delisting), misure, Sharpe corretto.
Richiede la cache di `g1_2026-11-12.py base` (CACHE_G1N). Scrive solo `g1_parte2_2026-11-12_esito_<parte>.json` qui accanto.
Uso: CACHE_G1N=<cartella> PYTHONPATH=<radice> python3 audits/repro/g1_parte2_2026-11-12.py dati|rischio|misure
"""
from __future__ import annotations

import importlib.util
import json
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd

from research.programma6 import seconda as sc

QUI = Path(__file__).parent
spec = importlib.util.spec_from_file_location("g1a", QUI / "g1_2026-11-12.py")
g1a = importlib.util.module_from_spec(spec)
spec.loader.exec_module(g1a)
ESITO = QUI / f"g1_parte2_2026-11-12_esito_{sys.argv[1] if len(sys.argv) > 1 else 'x'}.json"


def salva(k, v):
    d = json.loads(ESITO.read_text()) if ESITO.exists() else {}
    d[k] = v
    ESITO.write_text(json.dumps(d, indent=1, ensure_ascii=False, default=float))


def parte_dati():
    b = g1a.basi()
    pan = sc.pannello()
    t0, idx, giorni, W = b["t0"], b["idx"], b["giorni"], b["W"]
    X = np.load(g1a.CACHE / "X_A280.npy")
    S = len(b["simboli"])
    C, O, V = pan["close"], pan["open"], pan["quote_volume"]
    usati = np.flatnonzero((np.abs(W).sum(axis=0) > 0) | (np.abs(X).sum(axis=0) > 0))
    out = {"monete_usate": int(len(usati))}
    # buchi dentro la vita di ogni moneta, nel periodo
    ok = np.isfinite(C)
    buchi = {}
    perso = []
    for j in usati:
        vivi = np.flatnonzero(ok[:, j])
        a, z = vivi[0], vivi[-1]
        for i in range(max(a, idx[0]), min(z, idx[-1]) + 1):
            if not ok[i, j]:
                buchi.setdefault(sc.data(int(i + t0)), []).append(b["simboli"][j])
        # movimento perso: posizione del giorno prima di un buco, chiusura prima -> apertura dopo
        for i in range(max(a, idx[0]) + 1, min(z, idx[-1]) + 1):
            if ok[i - 1, j] and not ok[i, j]:
                dopo = i + np.argmax(ok[i:, j])
                k = int(i - 1 - idx[0])
                if 0 <= k < len(giorni) and W[k, j] != 0 and np.isfinite(O[dopo, j]):
                    perso.append((sc.data(int(i + t0)), b["simboli"][j], float(W[k, j]), float(O[dopo, j] / C[i - 1, j] - 1)))
    out["giorni_con_buchi"] = {d: len(v) for d, v in sorted(buchi.items())}
    pp = pd.DataFrame(perso, columns=["giorno", "moneta", "peso", "movimento_perso"])
    pp["effetto"] = pp["peso"] * pp["movimento_perso"]
    out["movimento_perso_nei_buchi"] = {"posizioni": int(len(pp)), "effetto_totale_su_G1": float(pp["effetto"].sum()),
                                        "per_giorno": pp.groupby("giorno")["effetto"].sum().round(5).to_dict(),
                                        "peggiori": pp.reindex(pp["effetto"].abs().sort_values(ascending=False).index).head(8).values.tolist()}
    # giorni fermi (volume zero) tenuti
    fermi = np.isfinite(C[idx]) & (np.nan_to_num(V[idx]) == 0)
    out["giorni_fermi_tenuti_G1"] = int((fermi & (W != 0)).sum())
    out["giorni_fermi_tenuti_A280"] = int((fermi & (np.abs(X) > 1e-12)).sum())
    # funding: pannello contro il dato vero, nei giorni tenuti
    stimati, senza, diversi = 0, 0, []
    tenuti = (W != 0) | (np.abs(X) > 1e-12)
    for j in usati:
        vero = sc.funding_giorni(b["simboli"][j])
        g = giorni[tenuti[:, j]]
        if not len(g):
            continue
        fv = vero.reindex(g)
        fp = b["F"][tenuti[:, j], j]
        mancano = fv.isna().to_numpy()
        senza += int(mancano.sum())
        stimati += int((mancano & (fp != 0)).sum())
        dd = np.abs(np.nan_to_num(fv.to_numpy()) - fp)
        for gg in g[(dd > 1e-9) & ~mancano]:
            diversi.append((sc.data(int(gg)), b["simboli"][j]))
    out["funding_giorni_tenuti_senza_dato_vero"] = senza
    out["funding_giorni_tenuti_stimati_diversi_da_zero"] = stimati
    out["funding_giorni_tenuti_diversi_dal_vero"] = len(diversi)
    out["funding_diversi_esempi"] = diversi[:10]
    # orari dei regolamenti: minuti e secondi dal giro d'ora (letti dai dati, non assunti), intervalli fra regolamenti
    from research.src import dati as rd
    fuori, interv = 0, {}
    tot = 0
    for j in usati[:]:
        s = b["simboli"][j]
        righe = []
        for p in sorted((sc.DATI / s / "funding").glob("*.zip")):
            righe += rd.funding_da_zip(p)
        if not righe:
            continue
        ts = np.array(sorted({r[0] for r in righe}))
        ts = ts[(ts // 86_400_000 >= giorni[0]) & (ts // 86_400_000 <= giorni[-1] + 1)]
        tot += len(ts)
        fuori += int(((ts % 3_600_000) > 60_000).sum())
        for h in np.round(np.diff(ts) / 3_600_000).astype(int):
            interv[int(h)] = interv.get(int(h), 0) + 1
    out["regolamenti"] = {"totale": tot, "oltre_un_minuto_dal_giro_d_ora": fuori,
                          "intervalli_ore": dict(sorted(interv.items())[:12])}
    # candele orarie per gli ordini eseguiti di A (00 e 01 UTC)
    D = np.load(g1a.CACHE / "D_A280.npy")
    senza_ore = 0
    for j in np.flatnonzero(np.abs(D).sum(axis=0) > 0):
        bb = b["ore"].get(b["simboli"][j]) or {}
        for k in np.flatnonzero(np.abs(D[:, j]) > 1e-12):
            h = int(giorni[k]) * 24
            if h not in bb or h + 1 not in bb:
                senza_ore += 1
    out["A280_ordini_senza_candele_orarie"] = senza_ore
    out["A280_ordini"] = int((np.abs(D) > 1e-12).sum())
    # valori anomali: rendimenti giornalieri oltre il 50% su monete tenute
    R = b["R"]
    m = (np.abs(R) > 0.5) & tenuti
    an_ = [(sc.data(int(giorni[k])), b["simboli"][j], float(R[k, j]), float(W[k, j])) for k, j in zip(*np.nonzero(m))]
    out["rendimenti_oltre_50pc_tenuti"] = sorted(an_, key=lambda x: -abs(x[2] * x[3]))[:12]
    # monete nuove (prima candela dal 2025-06) tenute: per i contratti su azioni e TradFi
    primo = np.where(ok.any(axis=0), ok.argmax(axis=0), 10 ** 6)
    nuove = [(b["simboli"][j], sc.data(int(primo[j] + t0)), int((W[:, j] != 0).sum())) for j in usati if primo[j] + t0 >= sc.giorno(2025, 6, 1)]
    out["monete_nuove_tenute"] = nuove
    # orari UTC delle candele giornaliere (campione)
    from research.programma5.strumenti import motore5 as m5
    nonutc = 0
    camp = usati[:: max(1, len(usati) // 40)]
    for j in camp:
        for p in sorted((sc.DATI / b["simboli"][j] / "giorni").glob("*.zip"))[-3:]:
            df = m5._csv_da_zip(p, m5.KLINE)
            nonutc += int((m5._ms(df["open_time"]) % 86_400_000 != 0).sum())
    out["candele_giornaliere_non_a_mezzanotte_campione"] = {"monete": len(camp), "candele_fuori": nonutc}
    print(json.dumps(out, default=float)[:3000])
    salva("dati", out)


def parte_rischio():
    b = g1a.basi()
    pan = sc.pannello()
    idx, giorni, W = b["idx"], b["giorni"], b["W"]
    X = np.load(g1a.CACHE / "X_A280.npy")
    g = pd.read_csv(g1a.CACHE / "giorni.csv", index_col=0)
    H, L, O, C = pan["high"][idx], pan["low"][idx], pan["open"][idx], pan["close"][idx]
    with np.errstate(all="ignore"):
        su, giu = np.nan_to_num(H / O - 1), np.nan_to_num(L / O - 1)
    out = {}
    for nome, P in (("G1", W), ("A280", X)):
        lunghi, corti = np.where(P > 0, P, 0), np.where(P < 0, P, 0)
        peggio = (corti * su + lunghi * giu).sum(axis=1)
        crollo, rialzo = (P * giu).sum(axis=1), (P * su).sum(axis=1)
        caso = np.minimum(crollo, rialzo)
        k = int(np.argmin(peggio))
        out[nome] = {"peso_massimo_moneta": float(np.abs(P).max()), "lordo_massimo": float(np.abs(P).sum(axis=1).max()),
                     "lato_lungo_max": float(lunghi.sum(axis=1).max()), "lato_corto_max": float(-corti.sum(axis=1).max()),
                     "perdita_peggiore_possibile_nel_giorno": float(peggio[k]), "giorno": sc.data(int(giorni[k])),
                     "quantile_1pc": float(np.percentile(peggio, 1)), "mercato_intero_peggiore": float(caso.min()),
                     "giorno_mercato_intero": sc.data(int(giorni[int(np.argmin(caso))])),
                     "giorni_perdita_oltre_5pc": int((g[nome] < -0.05).sum()), "peggior_giorno": float(g[nome].min()),
                     "giorni_moneta_oltre_3pc_di_perdita": int(((P * (np.where(P > 0, giu, su))) < -0.03).sum())}
        # stop a -35% dal massimo (controllo ogni minuto): conto che si compone; dentro il giorno il caso «mercato intero»
        eq, picco, minimo, toccato = 1.0, 1.0, 1.0, []
        for k in range(len(giorni)):
            dentro = eq * (1 + caso[k])
            if dentro / picco < 0.65 or dentro < 0.65:
                toccato.append(sc.data(int(giorni[k])))
            minimo = min(minimo, dentro / picco)
            eq *= 1 + g[nome].iloc[k]
            picco = max(picco, eq)
        out[nome]["stop_35_toccato_caso_mercato_intero"] = toccato[:10]
        out[nome]["minimo_rispetto_al_picco_dentro_il_giorno"] = float(minimo)
        # chiusura giornaliera
        eqs = np.cumprod(1 + g[nome].to_numpy())
        out[nome]["discesa_chiusure_conto_che_si_compone"] = float((eqs / np.maximum.accumulate(eqs) - 1).min())
        s = (1 + g[nome]).cumprod()
        dd = s / s.cummax() - 1
        fondo = int(np.argmin(dd.to_numpy()))
        inizio = int(np.argmax(s.to_numpy()[:fondo + 1]))
        rec = np.flatnonzero(s.to_numpy()[fondo:] >= s.to_numpy()[inizio])
        out[nome]["discesa_durata_giorni"] = {"dal": sc.data(int(giorni[inizio])), "fondo": sc.data(int(giorni[fondo])),
                                              "recupero": sc.data(int(giorni[fondo + rec[0]])) if len(rec) else None,
                                              "giorni": int((rec[0] + fondo - inizio) if len(rec) else len(giorni) - inizio)}
    # rialzi dentro il giorno sui corti (cross a leva 5: la liquidazione e' del conto, non della moneta)
    s = su[X < 0]
    out["A280_corti_rialzo_nel_giorno"] = {"posizioni_giorno": int(len(s)), "oltre_20pc": int((s > 0.2).sum()),
                                           "oltre_50pc": int((s > 0.5).sum()), "massimo": float(s.max())}
    # monete tolte dal listino nel periodo: guadagno di G1 negli ultimi 30 giorni prima dell'ultima candela
    ok = np.isfinite(pan["close"])
    ultimo = np.where(ok.any(axis=0), ok.shape[0] - 1 - ok[::-1].argmax(axis=0), -1)
    R = b["R"]
    tolte = []
    for j in np.flatnonzero((np.abs(W).sum(axis=0) > 0)):
        u = ultimo[j]
        if idx[0] <= u <= idx[-1] - 1:
            k1 = int(u - idx[0])
            k0 = max(0, k1 - 30)
            tolte.append((b["simboli"][j], sc.data(int(u + b["t0"])), float((W[k0:k1 + 1, j] * R[k0:k1 + 1, j]).sum()),
                          float((X[k0:k1 + 1, j] * R[k0:k1 + 1, j]).sum()), float(W[k1, j])))
    out["tolte_dal_listino"] = {"monete": len(tolte), "guadagno_G1_ultimi_30_giorni": float(sum(t[2] for t in tolte)),
                                "guadagno_A280_ultimi_30_giorni": float(sum(t[3] for t in tolte)),
                                "tenute_all_ultimo_giorno": [t for t in tolte if t[4] != 0][:15],
                                "maggiori": sorted(tolte, key=lambda t: -abs(t[2]))[:8]}
    print(json.dumps(out, default=float)[:3500])
    salva("rischio", out)


def numeri(x: np.ndarray) -> dict:
    sd = x.std(ddof=1)
    giu = x[x < 0]
    dsd = math.sqrt((np.minimum(x, 0) ** 2).mean())
    return {"sharpe": float(x.mean() / sd * math.sqrt(52)), "sortino": float(x.mean() / dsd * math.sqrt(52)),
            "asimmetria": float(pd.Series(x).skew()), "curtosi": float(pd.Series(x).kurt() + 3), "settimane": int(len(x))}


def parte_misure():
    from research.programma6 import asticella as ast
    from research.programma6 import terza as te
    from research.programma7.revisione_g1n import analisi as an
    b = g1a.basi()
    pan = sc.pannello()
    g = pd.read_csv(g1a.CACHE / "giorni.csv", index_col=0)
    X = np.load(g1a.CACHE / "X_A280.npy")
    out = {}
    # clima di mercato: rendimento del Bitcoin nel mese (chiusura su chiusura): > +10% rialzo, < -10% ribasso, altrimenti laterale
    jb = pan["simboli"].index("BTCUSDT")
    cb = pd.Series(pan["close"][b["idx"], jb], index=pd.to_datetime(b["giorni"] * 86400, unit="s"))
    mese_r = cb.resample("ME").last().pct_change()
    mese_r.iloc[0] = cb.resample("ME").last().iloc[0] / cb.iloc[0] - 1
    clima = np.where(mese_r > 0.10, "rialzo", np.where(mese_r < -0.10, "ribasso", "laterale"))
    clima = pd.Series(clima, index=mese_r.index.to_period("M"))
    for nome in ("G1", "A280"):
        x = g[nome]
        dt = pd.to_datetime(x.index * 86400, unit="s")
        w = an.settimane(pd.DataFrame({"n": x}))["n"].to_numpy()
        o = numeri(w)
        tot = x.sum()
        o["guadagno_totale_somma"] = float(tot)
        o["quota_5_giorni_migliori"] = float(x.nlargest(5).sum() / tot)
        mesi = x.groupby(dt.to_period("M")).sum()
        o["quota_3_mesi_migliori"] = float(mesi.nlargest(3).sum() / tot)
        o["mesi_positivi"] = f"{int((mesi > 0).sum())}/{len(mesi)}"
        o["3_mesi_migliori"] = {str(k): float(v) for k, v in mesi.nlargest(3).items()}
        cl = clima.reindex(dt.to_period("M")).to_numpy()
        o["per_clima"] = {c: {"mesi": int((clima == c).sum()), "annuo": float(x[cl == c].mean() * 365),
                              "sharpe_giornaliero_annuo": float(x[cl == c].mean() / x[cl == c].std(ddof=1) * math.sqrt(365))}
                          for c in ("rialzo", "laterale", "ribasso")}
        out[nome] = o
    out["A280_esposizione_lorda_media"] = float(np.abs(X).sum(axis=1).mean())
    out["A280_lordo_su_spese"] = {"lordo_annuo": float(g["A280_lordo"].mean() * 365), "funding_incassato_annuo": float(-g["A280_funding"].mean() * 365),
                                  "spese_annue": float(g["A280_spese"].mean() * 365)}
    D = np.load(g1a.CACHE / "D_A280.npy")
    n_ord = int((np.abs(D) > 1e-12).sum())
    out["A280_per_ordine"] = {"ordini": n_ord, "netto_medio_per_ordine_in_frazione": float(g["A280"].sum() / n_ord),
                              "spesa_media_per_ordine": float(g["A280_spese"].sum() / n_ord)}
    # Sharpe corretto: le due maniere di contare le prove (catalogo, voce 16)
    prove = ast.le_prove()
    serie = {n: ast.periodo(s) for n, s, _ in prove if s is not None}
    serie.update({n: ast.periodo(s) for n, s in ast.serie_nuove().items()})
    soli = [sr for _, s, sr in prove if s is None]
    gr = ast.gruppi(serie, ast.TAGLIO)
    sr_g = ast.per_v(gr, soli, False)
    sr_v = ast.per_v(gr, soli, True)
    out["asticella"] = {"gruppi": len(sr_g), "in_v_con_aggiunta": len(sr_v), "serie": len(serie), "soli": len(soli)}
    for nome in ("G1", "A280"):
        x = g[nome]
        w = an.settimane(pd.DataFrame({"n": x}))["n"]
        w = w[w.index >= sc.giorno(2021, 1, 4)]
        n = numeri(w.to_numpy())
        r = {}
        for etich, N in (("N_gruppi", len(sr_g)), ("N_conto_309", 309)):
            r[etich + "_V_con_aggiunta"] = te.sharpe_corretto(n["sharpe"], n["settimane"], n["asimmetria"], n["curtosi"], sr_v, 52, n_prove=N)
            r[etich + "_V_tutti_i_gruppi"] = te.sharpe_corretto(n["sharpe"], n["settimane"], n["asimmetria"], n["curtosi"], sr_g, 52, n_prove=N)
        r["t"] = n["sharpe"] * math.sqrt(n["settimane"] / 52)
        out["corretto_" + nome] = r
    print(json.dumps(out, default=float)[:3500])
    salva("misure", out)


if __name__ == "__main__":
    globals()["parte_" + sys.argv[1]]()
