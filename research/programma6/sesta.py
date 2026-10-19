"""Programma 6, sesta prova (SESTA.md): il funding come segnale fra monete. Ogni lunedi', fra le 100 monete
dell'universo della terza prova, long il quinto con la somma del funding dei 7 giorni prima piu' bassa, short il quinto
con la piu' alta; conto, costi ed esame della terza prova.

Uso: python3 -m research.programma6.sesta
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from research.programma6 import seconda as sc
from research.programma6 import terza as te

QUI = Path(__file__).parent
RIS = QUI / "risultati_sesta"
INIZIO = sc.giorno(2021, 1, 4)
ANNI_PIENI = (2021, 2022, 2023, 2024, 2025)
PROVE_PROGRAMMA = 26


def funding_7(pan: dict, lunedi_idx: np.ndarray) -> np.ndarray:
    """La somma del funding dei 7 giorni di tenuta prima di ogni lunedi' (settimane × monete)."""
    Fc = np.vstack([np.zeros((1, pan["funding"].shape[1])), np.cumsum(pan["funding"], axis=0)])
    return Fc[lunedi_idx] - Fc[lunedi_idx - 7]


def esegui(log=print) -> dict:
    pan = sc.pannello()
    ps = te.pannello_settimane(pan, log=log)
    lun_idx = ps["lunedi"] - pan["t0"]
    S7 = funding_7(pan, lun_idx)
    costo = sc.costi_moneta(ps["simboli"])
    jb = ps["simboli"].index("BTCUSDT")
    btc = pd.Series(ps["R"][:, jb], index=ps["lunedi"])
    RIS.mkdir(exist_ok=True)
    out = {}
    for v, pesato in (("F1", True), ("F2", False)):
        Wt = te.pesi_portafoglio(-S7, ps["U"], ps["peso"], pesato)
        df = te.conto(Wt, ps["R"], ps["F"], costo)
        df.index = ps["lunedi"]
        # quanto viene dal funding (incassato o pagato) e quanto dal prezzo
        df["dal_funding"] = -df["funding"]
        df.to_csv(RIS / f"settimane_{v}.csv.gz")
        e = te.esame(df, btc, inizio=INIZIO, anni_pieni=ANNI_PIENI)
        d = df[df.index >= INIZIO]
        e["dal_funding_annuo"] = float(d["dal_funding"].mean() * 52)
        e["dal_prezzo_annuo"] = float(d["lordo"].mean() * 52)
        e["stimate_ottobre_2026"] = int((d.index >= sc.giorno(2026, 10, 1)).sum())
        out[v] = e
        (RIS / f"{v}.json").write_text(json.dumps(e, ensure_ascii=False, indent=1), encoding="utf-8")
        log(f"[sesta] {v} fatto")
    (RIS / "btc.json").write_text(json.dumps(te.numeri_settimana(btc[btc.index >= INIZIO]), indent=1), encoding="utf-8")
    return out


def rapporto() -> str:
    sr = sc.sharpe_prove()
    for v in ("C1", "C2", "C3"):
        sr.append(json.loads((te.RIS / f"{v}.json").read_text())["intero"]["sharpe"])
    for v in ("F1", "F2"):
        f = RIS / f"{v}.json"
        if f.exists():
            sr.append(json.loads(f.read_text())["intero"]["sharpe"])
    while len(sr) < PROVE_PROGRAMMA:
        sr.append(0.0)
    btc = json.loads((RIS / "btc.json").read_text())
    righe = ["# Programma 6 — risultati della sesta prova (il funding fra monete)", "",
             "Regole in `SESTA.md` (scritte prima). Settimane dal 4 gennaio 2021 all'ultima completa; le 100 monete più "
             "scambiate di ogni settimana fra tutte quelle dell'archivio; long il quinto con il funding dei 7 giorni prima "
             "più basso, short il quinto più alto, leva lorda 2.", "",
             "| Variante | Rendimento/anno | Intervallo (settimana) | Volatilità | Sharpe | Sharpe corretto | Discesa massima | "
             "Anni positivi | Ultimo anno | Costi doppi (settimana) | Dal funding/anno | Dal prezzo/anno | Lato long/anno | "
             "Lato short/anno | In più del BTC/anno | Esito |", "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for v in ("F1", "F2"):
        e = json.loads((RIS / f"{v}.json").read_text())
        i = e["intero"]
        dsr = te.sharpe_corretto(i["sharpe"], i["settimane"], i["asimmetria"], i["curtosi"], sr, 52)
        anni = sum(1 for x in e["per_anno"].values() if x > 0)
        righe.append(f"| {v} | {100 * i['annuo']:+.1f}% | {100 * e['boot']['basso']:+.2f}%; {100 * e['boot']['alto']:+.2f}% | "
                     f"{100 * i['volatilita']:.1f}% | {i['sharpe']:.2f} | {dsr:.2f} | {100 * i['discesa_max']:.1f}% | "
                     f"{anni}/{len(e['per_anno'])} | {100 * e['ultimo_anno']:+.1f}% | {100 * e['costi_doppi']:+.2f}% | "
                     f"{100 * e['dal_funding_annuo']:+.1f}% | {100 * e['dal_prezzo_annuo']:+.1f}% | "
                     f"{100 * e['long_annuo']:+.1f}% | {100 * e['short_annuo']:+.1f}% | {100 * e['extra_btc_annuo']:+.1f}% | "
                     f"{te.esito(e, dsr)} |")
    righe += ["", f"Bitcoin sempre comprato nelle stesse settimane: {100 * btc['annuo']:+.1f}% l'anno, Sharpe {btc['sharpe']:.2f}.",
              "", "| Variante | " + " | ".join(str(a) for a in range(2021, 2027)) + " | Dopo aprile 2025 |",
              "|---|" + "---|" * 7]
    for v in ("F1", "F2"):
        e = json.loads((RIS / f"{v}.json").read_text())
        pa = e["per_anno"]
        d = e["dopo_aprile_2025"]
        righe.append(f"| {v} | " + " | ".join(f"{100 * pa.get(str(a), float('nan')):+.1f}%" for a in range(2021, 2027))
                     + f" | {100 * d['annuo']:+.1f}%; {d['sharpe']:.2f} |")
    e1 = json.loads((RIS / "F1.json").read_text())
    righe += ["", f"Le ultime {e1['stimate_ottobre_2026']} settimane (ottobre 2026) usano il funding stimato: l'archivio non "
                  "ha ancora il file del mese."]
    testo = "\n".join(righe) + "\n"
    (QUI / "RISULTATI_SESTA.md").write_text(testo, encoding="utf-8")
    return testo


if __name__ == "__main__":
    esegui(log=lambda x: print(x, flush=True))
    print(rapporto())
    print("SESTA FINITA", flush=True)
