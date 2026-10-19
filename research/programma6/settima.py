"""Programma 6, settima prova (SETTIMA.md): la regola F2 della sesta prova (funding fra monete, pesi uguali) sulle monete
dalla 101ª alla 200ª per volume di ogni settimana, con lo scarto allo 0,10%.

Uso: python3 -m research.programma6.settima
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from research.programma5.strumenti import motore5 as m5
from research.programma6 import seconda as sc
from research.programma6 import sesta as se
from research.programma6 import terza as te
from research.programma6.motore import TAKER

QUI = Path(__file__).parent
RIS = QUI / "risultati_settima"
SCARTO = 0.0010


def esegui(log=print) -> dict:
    pan = sc.pannello()
    ps = te.pannello_settimane(pan, log=log, da=100, a=200, indicatori_si=False)
    S7 = se.funding_7(pan, ps["lunedi"] - pan["t0"])
    costo = np.full(len(ps["simboli"]), TAKER + SCARTO)
    Wt = te.pesi_portafoglio(-S7, ps["U"], ps["peso"], False)
    df = te.conto(Wt, ps["R"], ps["F"], costo)
    df.index = ps["lunedi"]
    df["dal_funding"] = -df["funding"]
    RIS.mkdir(exist_ok=True)
    df.to_csv(RIS / "settimane.csv.gz")
    d = df[(df.index >= se.INIZIO) & (df["monete"] > 0)]
    date = pd.to_datetime(d.index.to_numpy() * 86400, unit="s")
    e = {"settimane_operate": int(len(d)), "dal": sc.data(int(d.index.min())) if len(d) else "",
         "intero": te.numeri_settimana(d["netto"]), "boot": sc.bootstrap_blocchi(d["netto"].to_numpy(), blocco=4),
         "costi_doppi": float(d["netto_doppio"].mean()), "giro_medio": float(d["giro"].mean()),
         "dal_funding_annuo": float(d["dal_funding"].mean() * 52), "dal_prezzo_annuo": float(d["lordo"].mean() * 52),
         "spese_annue": float(d["spese"].mean() * 52)}
    anni = {}
    for a in sorted(set(date.year)):
        x = d["netto"][date.year == a]
        anni[int(a)] = {"settimane": int(len(x)), "annuo": float(x.mean() * 52)}
    e["per_anno"] = anni
    u = d[d.index >= sc.ULTIMO_ANNO]
    e["ultimo_anno"] = float(u["netto"].mean() * 52) if len(u) else float("nan")
    s = d["netto"].sort_values(ascending=False)
    e["senza_5_migliori"] = float(s.iloc[5:].mean())
    f2 = pd.read_csv(QUI / "risultati_sesta" / "settimane_F2.csv.gz", index_col=0)["netto"]
    comuni = d.index.intersection(f2.index)
    e["correlazione_F2"] = float(np.corrcoef(d.loc[comuni, "netto"], f2.loc[comuni])[0, 1])
    e["esito"] = esito(e)
    (RIS / "esame.json").write_text(json.dumps(e, ensure_ascii=False, indent=1), encoding="utf-8")
    log(f"[settima] {e['settimane_operate']} settimane: {e['esito']}")
    return e


def esito(e: dict) -> str:
    b = e["boot"]
    if not (b["basso"] > 0 and b["p"] <= 0.01):
        return f"netto non sopra zero con p ≤ 0,01 (p {b['p']:.4f})"
    anni = [v for v in e["per_anno"].values() if v["settimane"] >= 26]
    if sum(1 for v in anni if v["annuo"] > 0) < 0.75 * len(anni):
        return "positiva in meno dei tre quarti degli anni"
    if not e["ultimo_anno"] > 0:
        return "non positiva nell'ultimo anno"
    if not e["costi_doppi"] > 0:
        return "non positiva a costi doppi"
    if not e["senza_5_migliori"] > 0:
        return "non positiva senza le 5 settimane migliori"
    if not e["dal_prezzo_annuo"] >= -0.5 * e["dal_funding_annuo"]:
        return "il prezzo si mangia più di metà del funding"
    return "CONFERMATA"


def rapporto() -> str:
    e = json.loads((RIS / "esame.json").read_text())
    i, b = e["intero"], e["boot"]
    righe = ["# Programma 6 — risultati della settima prova (il funding fra monete, monete 101-200)", "",
             "Regole in `SETTIMA.md` (scritte prima): la regola F2 della sesta prova, identica, sulle monete dalla 101ª alla "
             "200ª per volume di ogni settimana; scarto 0,10% a lato.", "",
             f"* **Settimane operate**: {e['settimane_operate']} (dal {e['dal']}).",
             f"* **Rendimento**: {100 * i['annuo']:+.1f}% l'anno, volatilità {100 * i['volatilita']:.1f}%, Sharpe {i['sharpe']:.2f}, "
             f"discesa massima {100 * i['discesa_max']:.1f}%.",
             f"* **Media settimanale**: {100 * b['media']:+.3f}% (intervallo {100 * b['basso']:+.3f}; {100 * b['alto']:+.3f}, p {b['p']:.4f}).",
             f"* **Dal funding** {100 * e['dal_funding_annuo']:+.1f}% l'anno, **dal prezzo** {100 * e['dal_prezzo_annuo']:+.1f}%, "
             f"spese {100 * e['spese_annue']:.1f}%.",
             f"* **A costi doppi**: {100 * e['costi_doppi']:+.3f}% a settimana. **Senza le 5 settimane migliori**: "
             f"{100 * e['senza_5_migliori']:+.3f}%.",
             f"* **Ultimo anno** (dal 2025-10-01): {100 * e['ultimo_anno']:+.1f}% l'anno.",
             f"* **Correlazione con F2** (le 100 più scambiate): {e['correlazione_F2']:.2f}.", "",
             "| Anno | Settimane | Rendimento annualizzato |", "|---|---|---|"]
    for a, v in e["per_anno"].items():
        righe.append(f"| {a} | {v['settimane']} | {100 * v['annuo']:+.1f}% |")
    righe += ["", f"**Esito: {e['esito']}**"]
    testo = "\n".join(righe) + "\n"
    (QUI / "RISULTATI_SETTIMA.md").write_text(testo, encoding="utf-8")
    return testo


if __name__ == "__main__":
    esegui(log=lambda x: print(x, flush=True))
    print(rapporto())
    print("SETTIMA FINITA", flush=True)
