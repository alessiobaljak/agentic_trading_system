"""Programma 7, trentesima prova (TRENTESIMA.md): il clima del mercato (punteggio 0-100 ricostruito dal pannello con le regole della
skill «crypto-regime-analyzer», senza il peso di Bitcoin sul totale) come regolatore dell'esposizione di G1 (ogni giorno) e di F5
(ogni lunedi'): sotto 40 i pesi si dimezzano, altrimenti restano.

Uso: python3 -m research.programma7.trentesima
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from research.programma6 import asticella as ast
from research.programma6 import cinquantaseiesima as cs
from research.programma6 import ottava as ot
from research.programma6 import seconda as sc
from research.programma6 import sesta as se
from research.programma6 import terza as te
from research.programma6 import ventiquattresima as vq
from research.programma7 import prima as pr

QUI = Path(__file__).parent
RIS = QUI / "risultati_trentesima"

PESI = {"bitcoin": 25.0, "ampiezza": 20.0, "funding": 15.0, "discesa": 15.0, "slancio": 10.0}
PESO_MINIMO = 55.0            # il 65% di 85: sotto, il punteggio manca
SOGLIA = 40.0                 # la fascia «avversa» della skill
META = 0.5
FASCIA_PIATTA = 0.005         # la pendenza della media a 200 giorni: fra -0,5% e +0,5% e' piatta


def _precalcoli(pan: dict) -> dict:
    """Le medie mobili, la quota sopra le medie, lo slancio e le misure di Bitcoin per ogni giorno del pannello (indice del pannello)."""
    C = pd.DataFrame(pan["close"])
    m50 = C.rolling(50, min_periods=50).mean()
    m200 = C.rolling(200, min_periods=200).mean()
    jb = pan["simboli"].index("BTCUSDT")
    b = C[jb]
    lb = np.log(b)
    vol30 = lb.diff().rolling(30, min_periods=30).std(ddof=1) * np.sqrt(365)
    return {"C": C.to_numpy(), "m50": m50.to_numpy(), "m200": m200.to_numpy(),
            "sopra50": (C > m50).to_numpy() & m50.notna().to_numpy(), "sopra200": (C > m200).to_numpy() & m200.notna().to_numpy(),
            "valida200": m200.notna().to_numpy(), "slancio": (C / C.shift(30) - 1).to_numpy(),
            "jb": jb, "btc": b.to_numpy(), "m50b": m50[jb].to_numpy(), "m200b": m200[jb].to_numpy(),
            "vol30": vol30.to_numpy(), "max365": b.rolling(365, min_periods=365).max().to_numpy()}


def _fascia(x: float, soglie: list, valori: list, altrimenti: float) -> float:
    for s, v in zip(soglie, valori):
        if x >= s:
            return v
    return altrimenti


def ingredienti(pre: dict, pan: dict, k: int, u: np.ndarray) -> dict:
    """I cinque ingredienti del clima al giorno k del pannello (dati fino alla chiusura di k compresa), per l'universo u (monete).
    Ogni ingrediente e' un numero 0-100 o NaN se mancano i dati."""
    out = {}
    # 1. la tendenza di Bitcoin
    p, m50, m200 = pre["btc"][k], pre["m50b"][k], pre["m200b"][k]
    m200_prima = pre["m200b"][k - 20] if k >= 20 else np.nan
    if np.isfinite([p, m50, m200, m200_prima]).all():
        if m50 > m200:
            base = 90 if p > m50 else (65 if p > m200 else 55)
        else:
            base = 45 if p > m50 else 15
        pend = m200 / m200_prima - 1
        base += 10 if pend > FASCIA_PIATTA else (-10 if pend < -FASCIA_PIATTA else 0)
        out["bitcoin"] = float(min(100, max(0, base)))
    else:
        out["bitcoin"] = np.nan
    # 2. l'ampiezza delle monete minori
    alt = u.copy()
    alt[pre["jb"]] = False
    alt &= pre["valida200"][k]
    if alt.sum() >= 5:
        q200 = 100 * pre["sopra200"][k][alt].mean()
        q50 = 100 * pre["sopra50"][k][alt].mean()
        base = _fascia(q200, [80, 65, 50, 35, 20], [95, 80, 65, 45, 25], 10)
        base += 5 if q50 - q200 >= 15 else (-5 if q50 - q200 <= -15 else 0)
        out["ampiezza"] = float(min(100, max(0, base)))
    else:
        out["ampiezza"] = np.nan
    # 4. il funding dei perpetui (equivalente a 8 ore, in frazione)
    f = pan["funding"][k][u]
    f = f[np.isfinite(f)] / 3
    if f.size >= 2:
        fm = 100 * f.mean()           # in percento
        if fm <= -0.010:
            out["funding"] = 80.0
        elif fm <= 0:
            out["funding"] = 65.0
        elif fm <= 0.010:
            out["funding"] = 75.0
        elif fm <= 0.030:
            out["funding"] = 55.0
        elif fm <= 0.060:
            out["funding"] = 30.0
        else:
            out["funding"] = 10.0
    else:
        out["funding"] = np.nan
    # 5. la discesa e la volatilita' di Bitcoin
    mx, v = pre["max365"][k], pre["vol30"][k]
    if np.isfinite(mx) and np.isfinite(p) and mx > 0:
        dd = 1 - p / mx
        base = 90 if dd <= 0.10 else (75 if dd <= 0.20 else (55 if dd <= 0.35 else (35 if dd <= 0.50 else (20 if dd <= 0.65 else 10))))
        terzo_alto = False
        campioni = pre["vol30"][[k - 7 * m for m in range(1, 53) if k - 7 * m >= 0]]
        campioni = campioni[np.isfinite(campioni)]
        if np.isfinite(v) and campioni.size >= 12:
            basso, alto = np.quantile(campioni, [1 / 3, 2 / 3])
            if v <= basso:
                base += 10
            elif v >= alto:
                base -= 10
                terzo_alto = True
        if dd > 0.65 and terzo_alto:
            base = max(base, 15)
        out["discesa"] = float(min(100, max(0, base)))
    else:
        out["discesa"] = np.nan
    # 6. lo slancio a 30 giorni
    s = pre["slancio"][k][u]
    s = s[np.isfinite(s)]
    if s.size >= 5:
        q = 100 * (s > 0).mean()
        out["slancio"] = _fascia(q, [85, 65, 45, 25, 10], [90, 75, 55, 35, 20], 35)
    else:
        out["slancio"] = np.nan
    return out


def punteggio(ing: dict) -> float:
    """La media pesata degli ingredienti disponibili, pesi ridistribuiti; NaN se i pesi disponibili sono sotto il minimo."""
    disp = [(PESI[n], v) for n, v in ing.items() if np.isfinite(v)]
    peso = sum(p for p, _ in disp)
    if peso < PESO_MINIMO:
        return np.nan
    return float(sum(p * v for p, v in disp) / peso)


def clima(pan: dict, idx: np.ndarray, U: np.ndarray, pre: dict | None = None) -> tuple:
    """Il punteggio del clima per ogni giorno di decisione idx (indice del pannello), con i dati fino al giorno prima (idx-1) e
    l'universo U (decisioni × monete). Ritorna (punteggi, tabella degli ingredienti)."""
    pre = pre or _precalcoli(pan)
    righe = []
    for n, k in enumerate(np.asarray(idx) - 1):
        righe.append(ingredienti(pre, pan, int(k), U[n]) if k >= 0 else {m: np.nan for m in PESI})
    tab = pd.DataFrame(righe)
    tab["punteggio"] = [punteggio(r) for r in righe]
    return tab["punteggio"].to_numpy(), tab


def regolatore(punti: np.ndarray) -> np.ndarray:
    """Il fattore sui pesi: META sotto la soglia, 1 altrimenti e dove il punteggio manca."""
    p = np.asarray(punti, dtype=float)
    return np.where(np.isfinite(p) & (p < SOGLIA), META, 1.0)


def esegui(log=print) -> dict:
    pan = sc.pannello()
    ps = te.pannello_settimane(pan, log=lambda x: None, indicatori_si=False)
    pre = _precalcoli(pan)
    costo = sc.costi_moneta(pan["simboli"])
    R_g = sc.rendimenti(pan)
    # --- G1, ogni giorno
    giorni = np.arange(se.INIZIO, pr.FINE, dtype=np.int64)
    idx = giorni - pan["t0"]
    Ud = pr.universo_del_giorno(giorni, ps["lunedi"], ps["U"])
    sig = ot.sigma_30(pan, idx)
    W = vq.pesi_banda(np.where(np.isfinite(sig), -se.funding_7(pan, idx), np.nan), Ud, sig)
    punti_g, tab_g = clima(pan, idx, Ud, pre)
    fat_g = regolatore(punti_g)
    log(f"[trentesima] clima giornaliero fatto: {int(np.isnan(punti_g).sum())} giorni senza punteggio, "
        f"{int((fat_g < 1).sum())} giorni a meta' esposizione su {len(giorni)}")
    R, F = R_g[idx], np.nan_to_num(pan["funding"][idx])
    conti, ordini = {}, {}
    for nome, Wx in (("G1", W), ("G1 clima", W * fat_g[:, None])):
        mercato = te.conto(Wx, R, F, costo)
        spese, n_tot, n_lim, _ = cs.spese_a_limite(Wx, R, giorni, pan["simboli"], costo)
        d = mercato.copy()
        d["spese"] = spese
        d["netto"] = d["lordo"] - d["spese"] - d["funding"]
        d["netto_doppio"] = d["lordo"] - 2 * d["spese"] - d["funding"]
        conti[nome] = pr.per_settimana(d, giorni)
        conti[nome + " (giorni)"] = d
        ordini[nome] = {"variazioni": n_tot, "a_limite": n_lim}
        log(f"[trentesima] {nome}: conto fatto")
    # --- F5, ogni lunedi'
    lun = ps["lunedi"] - pan["t0"]
    sig_s = ot.sigma_30(pan, lun)
    Ws = vq.pesi_banda(np.where(np.isfinite(sig_s), -se.funding_7(pan, lun), np.nan), ps["U"], sig_s)
    punti_s, tab_s = clima(pan, lun, ps["U"], pre)
    fat_s = regolatore(punti_s)
    for nome, Wx in (("F5", Ws), ("F5 clima", Ws * fat_s[:, None])):
        d = te.conto(Wx, ps["R"], ps["F"], costo)
        d.index = ps["lunedi"]
        conti[nome] = d
        log(f"[trentesima] {nome}: conto fatto")
    RIS.mkdir(exist_ok=True)
    tab_g.index = giorni
    tab_g.to_csv(RIS / "clima_giorni.csv.gz")
    tab_s.index = ps["lunedi"]
    tab_s.to_csv(RIS / "clima_lunedi.csv.gz")
    for nome in ("G1", "G1 clima", "F5", "F5 clima"):
        conti[nome].to_csv(RIS / f"settimane_{nome.replace(' ', '_')}.csv.gz")
    btc = pd.Series(ps["R"][:, ps["simboli"].index("BTCUSDT")], index=ps["lunedi"])
    out = {n: te.esame(conti[n], btc, inizio=se.INIZIO, anni_pieni=se.ANNI_PIENI) for n in ("G1", "G1 clima", "F5", "F5 clima")}
    # per capire (descrittivo)
    dg = conti["G1 (giorni)"]
    avverso = fat_g < 1
    out["clima"] = {"giorni": int(len(giorni)), "senza_punteggio": int(np.isnan(punti_g).sum()), "giorni_avversi": int(avverso.sum()),
                    "punteggio_medio": float(np.nanmean(punti_g)),
                    "quota_fasce": {"avversa": float(np.nanmean(punti_g < 40)), "neutra": float(np.nanmean((punti_g >= 40) & (punti_g < 80))),
                                    "propensa": float(np.nanmean(punti_g >= 80))},
                    "G1_netto_medio_giorni_avversi": float(dg["netto"][avverso].mean()) if avverso.any() else None,
                    "G1_netto_medio_altri_giorni": float(dg["netto"][~avverso].mean()),
                    "F5_settimane_avverse": int((fat_s < 1).sum()),
                    "F5_netto_medio_settimane_avverse": float(conti["F5"]["netto"][fat_s < 1].mean()) if (fat_s < 1).any() else None,
                    "F5_netto_medio_altre": float(conti["F5"]["netto"][fat_s >= 1].mean()),
                    "ingredienti_medi": {n: float(np.nanmean(tab_g[n])) for n in PESI}}
    out["correlazioni"] = {"G1": float(np.corrcoef(conti["G1 clima"]["netto"], conti["G1"]["netto"])[0, 1]),
                           "F5": float(np.corrcoef(conti["F5 clima"]["netto"], conti["F5"]["netto"])[0, 1])}
    out["ordini"] = ordini
    serie = {**ast.serie_nuove(), "92 G1 clima": conti["G1 clima"]["netto"], "92 F5 clima": conti["F5 clima"]["netto"]}
    rivisto = ast.corretto_rivisto(serie, {"92 G1 clima": out["G1 clima"]["intero"], "92 F5 clima": out["F5 clima"]["intero"]})
    for n in ("G1 clima", "F5 clima"):
        r = rivisto["candidate"][f"92 {n}"]
        out[n]["sharpe_corretto"], out[n]["t"], out[n]["gruppi"] = r["corretto_con_aggiunta"], r["t"], rivisto["gruppi"]
        out[n]["esito"] = te.esito(out[n], out[n]["sharpe_corretto"])
        out[n]["regola_del_proprietario"] = bool(out[n]["sharpe_corretto"] >= 0.90 and all(v > 0 for v in out[n]["per_anno"].values())
                                                 and out[n]["t"] > 3)
    (RIS / "esame.json").write_text(json.dumps(out, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    c = out["clima"]
    righe = ["# Programma 7 — risultati della trentesima prova (il clima del mercato come regolatore di G1 e F5)", "",
             "Regole in `TRENTESIMA.md` (scritte prima). Dal 4 gennaio 2021 al 5 ottobre 2026; G1 con gli ordini limite.", "",
             "| | Sharpe | l'anno | volatilità | discesa | per anno |", "|---|---|---|---|---|---|"]
    for n in ("G1", "G1 clima", "F5", "F5 clima"):
        i = out[n]["intero"]
        righe.append(f"| {n} | {i['sharpe']:.2f} | {100 * i['annuo']:+.1f}% | {100 * i['volatilita']:.1f}% | {100 * i['discesa_max']:.1f}% | "
                     + ", ".join(f"{y} {100 * v:+.1f}%" for y, v in out[n]["per_anno"].items()) + " |")
    g_avv = c["G1_netto_medio_giorni_avversi"]
    f_avv = c["F5_netto_medio_settimane_avverse"]
    righe += ["",
              f"* Clima: punteggio medio {c['punteggio_medio']:.0f}; giorni avversi (sotto 40) {c['giorni_avversi']} su {c['giorni']} "
              f"({100 * c['quota_fasce']['avversa']:.0f}%), neutri {100 * c['quota_fasce']['neutra']:.0f}%, propensi "
              f"{100 * c['quota_fasce']['propensa']:.0f}%; senza punteggio {c['senza_punteggio']}.",
              "* Ingredienti medi: " + ", ".join(f"{n} {v:.0f}" for n, v in c["ingredienti_medi"].items()) + ".",
              (f"* G1 nei giorni avversi: netto medio al giorno {100 * g_avv:+.3f}%" if g_avv is not None else "* G1: nessun giorno avverso")
              + f"; negli altri giorni {100 * c['G1_netto_medio_altri_giorni']:+.3f}%.",
              (f"* F5 nelle {c['F5_settimane_avverse']} settimane avverse: netto medio {100 * f_avv:+.2f}%" if f_avv is not None
               else "* F5: nessuna settimana avversa") + f"; nelle altre {100 * c['F5_netto_medio_altre']:+.2f}%.",
              f"* Correlazione con la serie di base: G1 {out['correlazioni']['G1']:.3f}, F5 {out['correlazioni']['F5']:.3f}.",
              *(f"* **{n}**: Sharpe corretto {out[n]['sharpe_corretto']:.2f} ({out[n]['gruppi']} gruppi), t {out[n]['t']:.2f}; esito "
                f"{out[n]['esito']}; regola del proprietario: {'sì' if out[n]['regola_del_proprietario'] else 'no'}." for n in ("G1 clima", "F5 clima"))]
    testo = "\n".join(righe) + "\n"
    (QUI / "RISULTATI_TRENTESIMA.md").write_text(testo, encoding="utf-8")
    log(testo)
    return out


if __name__ == "__main__":
    esegui(log=lambda x: print(x, flush=True))
    print("TRENTESIMA FINITA", flush=True)
