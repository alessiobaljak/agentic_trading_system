"""Programma 6, il paper delle candidate (paper/REGOLE.md): ricostruisce la tabella con i dati nuovi, stima il funding dei
giorni non ancora nell'archivio dall'indice del premio orario, ricalcola F2, C1 e A1 con lo stesso codice delle prove e
scrive il periodo P (dal 20 ottobre 2026) e le posizioni di adesso in ``PAPER.md`` e ``paper.json``.

Uso: python3 -m research.programma6.paper.aggiorna   (dopo ``scarico_giorni`` con P6_PREMIO=1)
"""
from __future__ import annotations

import json
import math
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

from research.programma5.strumenti import motore5 as m5
from research.programma6 import seconda as sc
from research.programma6 import sesta as se
from research.programma6 import terza as te

QUI = Path(__file__).parent
INIZIO_GIORNI = sc.giorno(2026, 10, 20)
INIZIO_SETTIMANE = sc.giorno(2026, 10, 26)
INIZIO_E4_MS = sc.giorno(2026, 10, 21) * 86_400_000
INTERESSE, TETTO = 0.0001, 0.0005


# ---------------------------------------------------------------------------
# il funding stimato dall'indice del premio (REGOLE.md, sezione 2)
# ---------------------------------------------------------------------------

def premio_ore(simbolo: str) -> pd.Series:
    """L'indice del premio a 1 ora (chiusura), indice = ora dall'epoca."""
    file = sorted((sc.DATI / simbolo / "premio").glob("*.zip"))
    if not file:
        return pd.Series(dtype=float)
    df = pd.concat([m5._csv_da_zip(p, m5.KLINE) for p in file], ignore_index=True)
    ore = (m5._ms(df["open_time"]) // 3_600_000).to_numpy()
    return pd.Series(df["close"].astype(float).to_numpy(), index=ore).groupby(level=0).last().sort_index()


def funding_da_premio(p: pd.Series) -> pd.Series:
    """Funding stimato per giorno di tenuta: per ognuno dei tre intervalli di 8 ore del giorno, premio medio + l'interesse
    dello 0,01% riportato entro ±0,05% (la formula di Binance); il regolamento a fine intervallo tocca il giorno stesso."""
    if p.empty:
        return pd.Series(dtype=float)
    intervallo = p.index.to_numpy() // 8
    media = p.groupby(intervallo).mean()
    tasso = media + np.clip(INTERESSE - media, -TETTO, TETTO)
    giorno = (media.index.to_numpy() * 8) // 24
    return pd.Series(tasso.to_numpy(), index=giorno).groupby(level=0).sum()


def applica_stima(pan: dict) -> dict:
    """Sostituisce, moneta per moneta, il funding dei giorni dopo l'ultimo regolamento dell'archivio con la stima dal
    premio (dove c'e'). Ritorna, per moneta, il primo giorno stimato."""
    stimati = {}
    T = pan["close"].shape[0]
    for j, s in enumerate(pan["simboli"]):
        fv = sc.funding_giorni(s)
        ultimo = int(fv.index.max()) if len(fv) else None
        st = funding_da_premio(premio_ore(s))
        if ultimo is None or st.empty:
            continue
        st = st[(st.index > ultimo) & (st.index >= pan["t0"]) & (st.index < pan["t0"] + T)]
        if st.empty:
            continue
        pan["funding"][st.index.to_numpy() - pan["t0"], j] = st.to_numpy()
        stimati[s] = sc.data(int(st.index.min()))
    return stimati


# ---------------------------------------------------------------------------
# le candidate
# ---------------------------------------------------------------------------

def _riassunto(x: pd.Series, per_anno: int) -> dict:
    v = x.to_numpy(float)
    if len(v) < 2:
        return {"periodi": int(len(v)), "totale": float(np.prod(1 + v) - 1) if len(v) else 0.0}
    sd = v.std(ddof=1)
    return {"periodi": int(len(v)), "totale": float(np.prod(1 + v) - 1), "media": float(v.mean()),
            "sharpe": float(v.mean() / sd * math.sqrt(per_anno)) if sd > 0 else 0.0}


def posizioni_settimana(pan: dict, m: int, segnale: np.ndarray, peso_volume: bool, peso=None, universo: bool = False):
    """Le posizioni del lunedi' di indice ``m`` (universo e pesi come nella terza prova)."""
    C, O, V = pan["close"], pan["open"], pan["quote_volume"]
    ok = np.isfinite(C)
    primo = np.where(ok.any(0), ok.argmax(0), C.shape[0])
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)
        med = np.nan_to_num(np.nanmedian(V[max(0, m - 30): m], axis=0))
    amm = ok[m - 1] & (m - primo >= te.STORIA_MIN) & (med >= sc.VOLUME_MIN)
    cand = np.flatnonzero(amm)
    U = np.zeros((1, C.shape[1]), bool)
    U[0, cand[np.argsort(-med[cand], kind="stable")][:te.N_UNIVERSO]] = True
    if universo:
        return [pan["simboli"][j] for j in np.flatnonzero(U[0])]
    pesi = med if peso is None else peso
    W = te.pesi_portafoglio(segnale[None, :], U, pesi[None, :], peso_volume)[0]
    return {"long": {pan["simboli"][j]: round(float(W[j]), 4) for j in np.flatnonzero(W > 0)},
            "short": {pan["simboli"][j]: round(float(W[j]), 4) for j in np.flatnonzero(W < 0)}}


def f2_e_c1(pan: dict) -> dict:
    ps = te.pannello_settimane(pan, log=lambda x: None)
    costo = sc.costi_moneta(ps["simboli"])
    out = {}
    lun_idx = ps["lunedi"] - pan["t0"]
    S7 = se.funding_7(pan, lun_idx)
    Wt = te.pesi_portafoglio(-S7, ps["U"], ps["peso"], False)
    df = te.conto(Wt, ps["R"], ps["F"], costo)
    df.index = ps["lunedi"]
    out["F2"] = df
    from research.programma6 import ottava as ot
    out["F3"] = ot.portafoglio_f3(pan, ps, costo)
    # F5 (VENTIQUATTRESIMA.md, solo informazione): il segnale di F3 con la banda, entrata nel 20% e uscita sotto il 40%
    from research.programma6 import ventiquattresima as vq
    sig5 = ot.sigma_30(pan, lun_idx)
    ct5 = np.where(np.isfinite(sig5), -S7, np.nan)
    W5 = vq.pesi_banda(ct5, ps["U"], sig5)
    d5 = te.conto(W5, ps["R"], ps["F"], costo)
    d5.index = ps["lunedi"]
    out["F5"] = d5
    from research.programma6 import dodicesima as do
    from research.programma6 import undicesima as un
    pm = un.pannello_metrics(pan)
    out["K1"] = do.portafoglio_k1(pan, ps, pm, costo)
    # K2 (VENTOTTESIMA.md, costruzione, solo informazione): il segnale di K1 con la banda di F5
    dk2 = te.conto(vq.pesi_banda(np.where(np.isfinite(sig5), do.segnale_k1(pan, ps, pm), np.nan), ps["U"], sig5),
                   ps["R"], ps["F"], costo)
    dk2.index = ps["lunedi"]
    out["K2"] = dk2
    # M1: il modello ad alberi della quattordicesima prova, con la stessa cadenza di riallenamento
    from research.programma6 import quattordicesima as q
    X, _, Y = q.tabella_settimanale(pan, ps, ps["U"])
    P, _ = q.previsioni("M1", X, Y, ps["U"], ps["lunedi"], 6, lambda x: None)
    sigw = ot.sigma_30(pan, ps["lunedi"] - pan["t0"])
    Wm = te.pesi_portafoglio(np.where(np.isfinite(sigw), P, np.nan), ps["U"], np.nan_to_num(1.0 / sigw), True)
    dm = te.conto(Wm, ps["R"], ps["F"], costo)
    dm.index = ps["lunedi"]
    out["M1"] = dm
    # M6 (VENTITREESIMA.md, solo informazione): la media dei ranghi di cinque modelli come M1 con i semi 1-5
    from research.programma6 import ventitreesima as vt
    P6 = [vt.previsioni_seme(s, X, Y, ps["U"], ps["lunedi"]) for s in vt.SEMI]
    with np.errstate(all="ignore"):
        Pm6 = np.where(ps["U"], vt.media_ranghi(P6, ps["U"]), np.nan)
    out["M6"] = vt.portafoglio(Pm6, ps, sigw)
    # M7 (VENTICINQUESIMA.md, solo informazione): la previsione di M6 con la banda di F5
    d7 = te.conto(vq.pesi_banda(np.where(np.isfinite(sigw), Pm6, np.nan), ps["U"], sigw), ps["R"], ps["F"], costo)
    d7.index = ps["lunedi"]
    out["M7"] = d7
    wm = int(np.flatnonzero(np.isfinite(P).any(axis=1))[-1])
    out["M1_ultima"] = {"lunedi": sc.data(int(ps["lunedi"][wm])),
                        "long": {ps["simboli"][j]: round(float(Wm[wm, j]), 4) for j in np.flatnonzero(Wm[wm] > 0)},
                        "short": {ps["simboli"][j]: round(float(Wm[wm, j]), 4) for j in np.flatnonzero(Wm[wm] < 0)}}
    Zr = te.ranghi(ps["Z"], ps["U"])
    ct, _ = te.segnale("C1", Zr, ps["R"], ps["U"], ps["peso"])
    Wc = te.pesi_portafoglio(ct, ps["U"], ps["peso"], True)
    dc = te.conto(Wc, ps["R"], ps["F"], costo)
    dc.index = ps["lunedi"]
    out["C1"] = dc
    # le posizioni di adesso per F2: l'ultimo lunedi' con la domenica prima nei dati
    # anche il lunedi' subito dopo l'ultimo giorno dei dati: la sua decisione usa solo la domenica prima
    giorni = np.arange(pan["close"].shape[0] + 1) + pan["t0"]
    lun = np.flatnonzero((giorni + 3) % 7 == 0)
    m = int(lun[-1])
    s7 = (np.cumsum(pan["funding"], axis=0)[m - 1] - np.cumsum(pan["funding"], axis=0)[m - 8])
    out["F2_adesso"] = {"lunedi": sc.data(m + pan["t0"]), **posizioni_settimana(pan, m, -s7, False)}
    # le monete entrate nell'universo nelle ultime 4 settimane (da controllare: devono essere monete, SECONDA.md sezione 9)
    out["nuove"] = sorted(set(posizioni_settimana(pan, m, np.zeros(len(pan["simboli"])), False, universo=True))
                          - set(posizioni_settimana(pan, m - 28, np.zeros(len(pan["simboli"])), False, universo=True)))
    from research.programma6 import ottava as ot
    sig = ot.sigma_30(pan, np.array([m]))[0]
    out["F3_adesso"] = {"lunedi": sc.data(m + pan["t0"]),
                        **posizioni_settimana(pan, m, np.where(np.isfinite(sig), -s7, np.nan), True,
                                              peso=np.nan_to_num(1.0 / sig))}
    # F5 adesso: la banda portata avanti dalle settimane intere fino al lunedi' m (lo stato dipende dalle settimane prima)
    Um5 = np.zeros((1, len(pan["simboli"])), bool)
    Um5[0, [pan["simboli"].index(x) for x in posizioni_settimana(pan, m, np.zeros(len(pan["simboli"])), False,
                                                                 universo=True)]] = True
    prima = ps["lunedi"] - pan["t0"] < m
    ct_m = np.vstack([ct5[prima], np.where(np.isfinite(sig), -s7, np.nan)[None]])
    W5m = vq.pesi_banda(ct_m, np.vstack([ps["U"][prima], Um5]), np.vstack([sig5[prima], sig[None]]))[-1]
    out["F5_adesso"] = {"lunedi": sc.data(m + pan["t0"]),
                        "long": {pan["simboli"][j]: round(float(W5m[j]), 4) for j in np.flatnonzero(W5m > 0)},
                        "short": {pan["simboli"][j]: round(float(W5m[j]), 4) for j in np.flatnonzero(W5m < 0)}}
    # K1 adesso: i tre ranghi fra le monete dell'universo del lunedi' m
    from research.programma6 import nona as no
    Um = np.zeros((1, len(pan["simboli"])), bool)
    Um[0, [pan["simboli"].index(x) for x in posizioni_settimana(pan, m, np.zeros(len(pan["simboli"])), False, universo=True)]] = True
    with np.errstate(all="ignore"):
        oi = pm["oi"]
        p2 = np.log(oi[m - 1]) - np.log(oi[m - 8])
    Zk = np.stack([-s7, no.g1(pan, np.array([m]))[0], np.where(np.isfinite(p2), p2, np.nan)], axis=1)[None]
    Rk = te.ranghi(Zk, Um)[0]
    okk = np.isfinite(Zk[0])
    kk = np.where(okk[:, 0] & (okk.sum(axis=1) >= 2), np.where(okk, Rk, 0).sum(axis=1) / np.maximum(okk.sum(axis=1), 1), np.nan)
    out["K1_adesso"] = {"lunedi": sc.data(m + pan["t0"]),
                        **posizioni_settimana(pan, m, np.where(np.isfinite(sig), kk, np.nan), True,
                                              peso=np.nan_to_num(1.0 / sig))}
    # C1 adesso: il segnale dell'ultima settimana completa (quello della settimana in corso richiede la domenica)
    w = int(np.flatnonzero(np.isfinite(ct).any(axis=1))[-1])
    out["C1_ultima"] = {"lunedi": sc.data(int(ps["lunedi"][w])),
                        "long": sorted(ps["simboli"][j] for j in np.flatnonzero(Wc[w] > 0)),
                        "short": sorted(ps["simboli"][j] for j in np.flatnonzero(Wc[w] < 0))}
    return out


def a1(pan: dict) -> tuple:
    U = sc.universo(pan, sc.N_A)
    W = sc.pesi_regola(pan, "A1", U)
    df = sc.portafoglio(pan, W)
    # le posizioni di adesso: i pesi decisi all'ultima chiusura (senza la maschera del giorno dopo, che non c'e' ancora)
    C = pan["close"]
    t = C.shape[0] - 1
    s = sc._per_moneta(C, lambda c: sc.segnale_moneta(c))[t]
    mm = sc._per_moneta(C, sc.moltiplicatore)[t]
    peso = np.nan_to_num(s) * np.nan_to_num(mm) / sc.N_A * U[t]
    adesso = {pan["simboli"][j]: round(float(peso[j]), 4) for j in np.flatnonzero(peso > 0)}
    return df, {"giorno": sc.data(t + pan["t0"]), "pesi": dict(sorted(adesso.items(), key=lambda x: -x[1]))}


def esegui(log=print) -> dict:
    pan = sc.costruisci_pannello(log=lambda x: None)
    # i dati sulle posizioni dei giorni nuovi (per K1), con la tabella appena ricostruita
    from research.programma6 import scarico_metrics
    scarico_metrics.main()
    stimati = applica_stima(pan)
    ultimo = sc.data(pan["t0"] + pan["close"].shape[0] - 1)
    log(f"[paper] dati fino al {ultimo}; funding stimato per {len(stimati)} monete")
    w = f2_e_c1(pan)
    da, a1_adesso = a1(pan)
    res = {"dati_fino_al": ultimo, "funding_stimato_dal": min(stimati.values()) if stimati else None, "candidate": {}}
    for nome in ("F3", "F5", "K1", "K2", "M1", "M6", "M7", "F2", "C1"):
        d = w[nome]
        d = d[d.index >= INIZIO_SETTIMANE]
        res["candidate"][nome] = {"settimane": {sc.data(int(k)): round(float(v), 6) for k, v in d["netto"].items()},
                                  **_riassunto(d["netto"], 52)}
    # riga derivata, solo informazione: meta' F3 e meta' K1 (stesso capitale diviso in due)
    f3, k1 = w["F3"], w["K1"]
    comb = (0.5 * f3["netto"] + 0.5 * k1["netto"].reindex(f3.index).fillna(0.0))
    comb = comb[comb.index >= INIZIO_SETTIMANE]
    res["candidate"]["metà F3 + metà K1 (derivata)"] = {"settimane": {sc.data(int(k)): round(float(v), 6) for k, v in comb.items()},
                                                       **_riassunto(comb, 52)}
    # F3 e M1 a rischio uguale (QUINDICESIMA.md): i pesi dalle 26 settimane prima di ciascuna, anche di prima del periodo P
    from research.programma6 import quindicesima as qd
    fm = qd.combina({"F3": w["F3"], "M1": w["M1"]})["netto"]
    fm = fm[fm.index >= INIZIO_SETTIMANE]
    res["candidate"]["F3 + M1 a rischio uguale"] = {"settimane": {sc.data(int(k)): round(float(v), 6) for k, v in fm.items()},
                                                   **_riassunto(fm, 52)}
    # F5 + M7 a rischio uguale (VENTICINQUESIMA.md, solo informazione)
    f57 = qd.combina({"F5": w["F5"], "M7": w["M7"]})["netto"]
    f57 = f57[f57.index >= INIZIO_SETTIMANE]
    res["candidate"]["F5 + M7 a rischio uguale (informazione)"] = {
        "settimane": {sc.data(int(k)): round(float(v), 6) for k, v in f57.items()}, **_riassunto(f57, 52)}
    # F5 + M7 + K2 a rischio uguale (VENTOTTESIMA.md, costruzione, solo informazione)
    f572 = qd.combina({"F5": w["F5"], "M7": w["M7"], "K2": w["K2"]})["netto"]
    f572 = f572[f572.index >= INIZIO_SETTIMANE]
    res["candidate"]["F5 + M7 + K2 a rischio uguale (informazione)"] = {
        "settimane": {sc.data(int(k)): round(float(v), 6) for k, v in f572.items()}, **_riassunto(f572, 52)}
    # E4 (VENTISEIESIMA.md, REGOLE.md sezione 9): gli eventi del periodo P, dai file mensili del funding
    from research.programma6 import ventiseiesima as vs
    e4 = vs.tabella(pan, [x for x in vs.eventi(pan) if x[1] >= INIZIO_E4_MS], -1)
    res["eventi_E4"] = e4.astype(object).where(e4.notna(), None).to_dict(orient="records") if len(e4) else []
    d = da[da.index >= INIZIO_GIORNI]
    res["candidate"]["A1"] = {"giorni": {sc.data(int(k)): round(float(v), 6) for k, v in d["netto"].items()},
                              **_riassunto(d["netto"], 365)}
    res["adesso"] = {"F3": w["F3_adesso"], "F5": w["F5_adesso"], "K1": w["K1_adesso"], "M1": w["M1_ultima"], "F2": w["F2_adesso"],
                     "C1": w["C1_ultima"], "A1": a1_adesso}
    res["nuove_nell_universo"] = w["nuove"]
    (QUI / "paper.json").write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    (QUI / "PAPER.md").write_text(rapporto(res), encoding="utf-8")
    return res


def rapporto(r: dict) -> str:
    righe = ["# Programma 6 — il paper delle candidate", "",
             f"Regole in `REGOLE.md` (scritte il 19 ottobre 2026, prima dei dati nuovi). Dati fino al **{r['dati_fino_al']}**"
             + (f"; funding stimato dall'indice del premio dal {r['funding_stimato_dal']} (si ricalcola quando l'archivio "
                "pubblica il file del mese)." if r["funding_stimato_dal"] else "."),
             "Periodo P: giorni dal 20 ottobre 2026 (A1), settimane dal 26 ottobre 2026 (F2, C1). Verdetto a 52 e 104 "
             "settimane, mai prima.", "", "| Candidata | Periodi nel periodo P | Rendimento totale | Sharpe da quando è partita |",
             "|---|---|---|---|"]
    for n, c in r["candidate"].items():
        sh = f"{c['sharpe']:.2f}" if "sharpe" in c else "—"
        righe.append(f"| {n} | {c['periodi']} | {100 * c['totale']:+.2f}% | {sh} |")
    a = r["adesso"]
    righe += ["", "## Le posizioni di adesso", "",
              f"* **F3**, settimana dal {a['F3']['lunedi']}: long " + ", ".join(f"{k} {100 * v:.1f}%" for k, v in a['F3']['long'].items())
              + "; short " + ", ".join(f"{k} {100 * v:.1f}%" for k, v in a['F3']['short'].items()) + ".",
              f"* **F5** (informazione), settimana dal {a['F5']['lunedi']}: long "
              + ", ".join(f"{k} {100 * v:.1f}%" for k, v in a['F5']['long'].items()) + "; short "
              + ", ".join(f"{k} {100 * v:.1f}%" for k, v in a['F5']['short'].items()) + ".",
              f"* **K1**, settimana dal {a['K1']['lunedi']}: long " + ", ".join(f"{k} {100 * v:.1f}%" for k, v in a['K1']['long'].items())
              + "; short " + ", ".join(f"{k} {100 * v:.1f}%" for k, v in a['K1']['short'].items()) + ".",
              f"* **M1**, ultima settimana calcolata (dal {a['M1']['lunedi']}; quella in corso si calcola a settimana chiusa): long "
              + ", ".join(f"{k} {100 * v:.1f}%" for k, v in a['M1']['long'].items()) + "; short "
              + ", ".join(f"{k} {100 * v:.1f}%" for k, v in a['M1']['short'].items()) + ".",
              f"* **F2**, settimana dal {a['F2']['lunedi']}: long {', '.join(a['F2']['long'])}; short {', '.join(a['F2']['short'])}.",
              f"* **C1**, ultima settimana calcolata (dal {a['C1']['lunedi']}): long {', '.join(a['C1']['long'])}; short "
              f"{', '.join(a['C1']['short'])}.",
              f"* **A1**, pesi decisi alla chiusura del {a['A1']['giorno']} (frazione del capitale): "
              + (", ".join(f"{k} {100 * v:.1f}%" for k, v in a['A1']['pesi'].items()) or "nessuna posizione") + ".",
              "", f"**E4** (a eventi, dal 21 ottobre; si vedono quando esce il file mensile del funding): "
              + (f"{len(r.get('eventi_E4', []))} eventi, media a 7 giorni "
                 f"{100 * sum(x['r7'] for x in r['eventi_E4'] if x['r7'] is not None) / max(1, sum(1 for x in r['eventi_E4'] if x['r7'] is not None)):+.2f}%"
                 if r.get("eventi_E4") else "nessun evento ancora") + ".",
              "", "**Entrate nell'universo nelle ultime 4 settimane** (da controllare che siano monete): "
              + (", ".join(r.get("nuove_nell_universo", [])) or "nessuna") + "."]
    return "\n".join(righe) + "\n"


if __name__ == "__main__":
    esegui(log=lambda x: print(x, flush=True))
    print((QUI / "PAPER.md").read_text())
    print("PAPER FATTO", flush=True)
