"""Programma 6, ventiduesima prova (VENTIDUESIMA.md): la leva che entra continua, conferma sulle monete 101-200. L1: long il
quinto con la quota a pronti scesa di piu' (7 giorni contro 90), short il quinto con la quota salita di piu'; L2: la media dei
ranghi di +acquisti a mercato dei 7 giorni e −cambio della quota a pronti. Pesi secondo la volatilita', scarto 0,10%.

Uso: python3 -m research.programma6.ventiduesima
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from research.programma6 import nona as no
from research.programma6 import ottava as ot
from research.programma6 import quattordicesima as q
from research.programma6 import seconda as sc
from research.programma6 import sesta as se
from research.programma6 import settima as st
from research.programma6 import terza as te
from research.programma6 import ventesima as ve
from research.programma6.motore import TAKER

QUI = Path(__file__).parent
RIS = QUI / "risultati_ventiduesima"
P_SOGLIA = 0.005


def segnali(pan: dict, lun: np.ndarray, U: np.ndarray, spot: np.ndarray) -> dict:
    perp = pan["quote_volume"]
    q7, q90 = ve.quota(spot, perp, lun, 7, ve.MIN_7), ve.quota(spot, perp, lun, 90, ve.MIN_90)
    with np.errstate(all="ignore"):
        cambio = np.where((q7 > 0) & (q90 > 0), np.log(q7 / q90), np.nan)
    acq = no.g1(pan, lun)
    a, b = q.rango_nan(acq, U & np.isfinite(cambio)), q.rango_nan(-cambio, U & np.isfinite(acq))
    return {"L1": -cambio, "L2": (a + b) / 2}


def esame(df: pd.DataFrame) -> dict:
    d = df[(df.index >= se.INIZIO) & (df["monete"] > 0)]
    date = pd.to_datetime(d.index.to_numpy() * 86400, unit="s")
    e = {"settimane_operate": int(len(d)), "dal": sc.data(int(d.index.min())) if len(d) else "",
         "intero": te.numeri_settimana(d["netto"]), "boot": sc.bootstrap_blocchi(d["netto"].to_numpy(), blocco=4),
         "costi_doppi": float(d["netto_doppio"].mean()), "spese_annue": float(d["spese"].mean() * 52),
         "dal_prezzo_annuo": float(d["lordo"].mean() * 52), "dal_funding_annuo": float(-d["funding"].mean() * 52),
         "per_anno": {int(a): {"settimane": int((date.year == a).sum()), "annuo": float(d["netto"][date.year == a].mean() * 52)}
                      for a in sorted(set(date.year))}}
    u = d[d.index >= sc.ULTIMO_ANNO]
    e["ultimo_anno"] = float(u["netto"].mean() * 52) if len(u) else float("nan")
    e["senza_5_migliori"] = float(d["netto"].sort_values(ascending=False).iloc[5:].mean())
    b = e["boot"]
    es = "CONFERMATA"
    anni = [v for v in e["per_anno"].values() if v["settimane"] >= 26]
    if not (b["basso"] > 0 and b["p"] <= P_SOGLIA):
        es = f"netto non sopra zero con p ≤ 0,005 (p {b['p']:.4f})"
    elif sum(1 for v in anni if v["annuo"] > 0) < 0.75 * len(anni):
        es = "positiva in meno dei tre quarti degli anni"
    elif not e["ultimo_anno"] > 0:
        es = "non positiva nell'ultimo anno"
    elif not e["costi_doppi"] > 0:
        es = "non positiva a costi doppi"
    elif not e["senza_5_migliori"] > 0:
        es = "non positiva senza le 5 settimane migliori"
    e["esito"] = es
    return e


def esegui(log=print) -> dict:
    pan = sc.pannello()                      # gia' con le correzioni del 20 ottobre (seconda.py, terza.py)
    ps = te.pannello_settimane(pan, log=lambda x: None, indicatori_si=False)
    ps2 = te.pannello_settimane(pan, log=lambda x: None, da=100, a=200, indicatori_si=False)
    lun = ps["lunedi"] - pan["t0"]
    sig = ot.sigma_30(pan, lun)
    spot = ve.volume_a_pronti(pan)
    k1 = pd.read_csv(QUI / "risultati_dodicesima" / "settimane_K1.csv.gz", index_col=0)["netto"]
    RIS.mkdir(exist_ok=True)
    out = {}
    for universo, p_, costo in (("101_200", ps2, np.full(len(ps["simboli"]), TAKER + st.SCARTO)),
                                ("cento", ps, sc.costi_moneta(ps["simboli"]))):
        U = p_["U"]
        dentro = p_["lunedi"] >= se.INIZIO
        S = segnali(pan, lun, U, spot)
        info = {"monete_settimana": int(U[dentro].sum()),
                "senza_segnale_L1": int((U & ~np.isfinite(S["L1"]))[dentro].sum())}
        for nome in ("L1", "L2"):
            ct = np.where(np.isfinite(sig), S[nome], np.nan)
            Wt = te.pesi_portafoglio(ct, U, np.nan_to_num(1.0 / sig), True)
            df = te.conto(Wt, p_["R"], p_["F"], costo)
            df.index = p_["lunedi"]
            df.to_csv(RIS / f"settimane_{nome}_{universo}.csv.gz")
            e = esame(df)
            d = df[df.index >= se.INIZIO]
            c = d.index.intersection(k1.index)
            e["correlazione_K1"] = float(np.corrcoef(d.loc[c, "netto"], k1.loc[c])[0, 1])
            e["dati"] = info
            out[f"{nome}_{universo}"] = e
            log(f"[ventiduesima] {nome} {universo}: Sharpe {e['intero']['sharpe']:.2f}, p {e['boot']['p']:.4f}, {e['esito']}")
    (RIS / "esame.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    righe = ["# Programma 6 — risultati della ventiduesima prova (la leva che entra continua: conferma sulle monete 101-200)", "",
             "Regole in `VENTIDUESIMA.md` (scritte prima). Dal 4 gennaio 2021, ogni lunedì; le 101-200 con scarto 0,10% sono la "
             "prova, le 100 solo per confronto.", "",
             "| Variante | Monete | Settimane | Rendimento/anno | Sharpe | Media settimanale (intervallo) | p | Spese l'anno | "
             "Ultimo anno | Correlazione K1 | Esito |", "|---|---|---|---|---|---|---|---|---|---|---|"]
    for k, e in out.items():
        nome, universo = k.split("_", 1)
        i, b = e["intero"], e["boot"]
        righe.append(f"| {nome} | {universo.replace('_', '-')} | {e['settimane_operate']} | {100 * i['annuo']:+.1f}% | "
                     f"{i['sharpe']:.2f} | {100 * b['media']:+.3f}% ({100 * b['basso']:+.3f}; {100 * b['alto']:+.3f}) | "
                     f"{b['p']:.4f} | {100 * e['spese_annue']:.1f}% | {100 * e['ultimo_anno']:+.1f}% | "
                     f"{e['correlazione_K1']:.2f} | {e['esito'] if universo == '101_200' else '(confronto)'} |")
    for k, e in out.items():
        righe += ["", f"**{k}, per anno**: " + ", ".join(f"{a} {100 * v['annuo']:+.1f}% ({v['settimane']})" for a, v in e["per_anno"].items())]
    testo = "\n".join(righe) + "\n"
    (QUI / "RISULTATI_VENTIDUESIMA.md").write_text(testo, encoding="utf-8")
    log(testo)
    return out


if __name__ == "__main__":
    esegui(log=lambda x: print(x, flush=True))
    print("VENTIDUESIMA FINITA", flush=True)
