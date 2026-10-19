"""Programma 6: il calcolo di tutte le famiglie con le finestre che avanzano e l'esame (METODO.md, sezione 6).

Uso: python3 -m research.programma6.esegui [famiglia ...]
Scrive ``research/programma6/risultati/<famiglia>.json`` (esame, scelte per trimestre, PBO) e, alla fine,
``RISULTATI.md`` con lo Sharpe corretto per tutte le famiglie provate.
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

from research.programma6 import dati
from research.programma6 import finestre as fi
from research.programma6.famiglie import FAMIGLIE

QUI = Path(__file__).parent
RIS = QUI / "risultati"


def una(famiglia: str) -> dict:
    combo, tr = fi.trade_famiglia(famiglia, dati.CENTO, log=lambda x: None)
    t, scelte = fi.avanza(tr, combo)
    e = fi.esame(t)
    e["pbo"] = fi.pbo(tr, len(combo))
    e["combinazioni"] = len(combo)
    e["scelte"] = [{"trimestre": datetime.fromtimestamp(s["da"] * 60, tz=timezone.utc).strftime("%Y-%m"),
                    "combinazione": combo[s["combinazione"]] if s["combinazione"] >= 0 else None} for s in scelte]
    RIS.mkdir(exist_ok=True)
    (RIS / f"{famiglia}.json").write_text(json.dumps(e, ensure_ascii=False, indent=1, default=float), encoding="utf-8")
    if len(t):
        t.to_csv(RIS / f"trade_{famiglia}.csv.gz", index=False)
    return e


def esito(e: dict, dsr: float) -> str:
    if not e.get("trade"):
        return "non opera"
    if not e["R"]["basso"] > 0:
        return "netto con l'intervallo non sopra zero"
    if not dsr >= 0.95:
        return f"Sharpe corretto {dsr:.2f} sotto 0,95"
    if not e["pbo"] < 0.5:
        return f"probabilità di sovra-adattamento {e['pbo']:.2f}"
    anni = [a for a in e["per_anno"].values() if a["trade"] > 0]
    if sum(1 for a in anni if a["R"] > 0) < 4:
        return "positiva in meno di 4 anni"
    if not e["ultimo_anno"]["R"] > 0:
        return "non positiva nell'ultimo anno"
    if not e["netto_doppio"] > 0:
        return "non positiva a costi doppi"
    monete = [m for m in e["per_moneta"].values() if m["trade"] >= 20]
    if sum(1 for m in monete if m["R"] > 0) < 0.55 * len(monete):
        return "positiva su meno del 55% delle monete"
    return "VALIDA"


def rapporto() -> None:
    tutte = {f.stem: json.loads(f.read_text()) for f in sorted(RIS.glob("*.json"))}
    sr = [e["capitale"]["sharpe_annuo"] for e in tutte.values() if e.get("trade")]
    righe = ["# Programma 6 — risultati delle finestre che avanzano", "",
             "Solo i trimestri di prova (2021-01 → 2026-10), con la combinazione scelta ogni volta sui 12 mesi prima. R = "
             "netto in multipli del rischio; capitale con il rischio dell'1% a trade e la leva al massimo 5 volte. Costi: "
             "commissioni, scarto, funding.", "",
             "| Famiglia | Trade | R a trade | Intervallo | Netto a trade | Capitale/anno | Sharpe annuo | Sharpe corretto | "
             "PBO | Anni positivi | Ultimo anno (R) | Esito |", "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for f, e in tutte.items():
        if not e.get("trade"):
            righe.append(f"| {f} | 0 | | | | | | | | | | non opera |")
            continue
        cap = e["capitale"]
        dsr = fi.sharpe_corretto(cap["sharpe_annuo"], cap["giorni"], cap["asimmetria"], cap["curtosi"], sr)
        anni = sum(1 for a in e["per_anno"].values() if a["trade"] > 0 and a["R"] > 0)
        righe.append(f"| {f} | {e['trade']} | {e['R']['media']:+.3f} | {e['R']['basso']:+.3f}; {e['R']['alto']:+.3f} | "
                     f"{100 * e['netto']['media']:+.3f}% | {100 * cap['rendimento_annuo']:+.1f}% | {cap['sharpe_annuo']:.2f} | "
                     f"{dsr:.2f} | {e['pbo']:.2f} | {anni}/{len(e['per_anno'])} | {e['ultimo_anno']['R']:+.3f} | "
                     f"{esito(e, dsr)} |")
    (QUI / "RISULTATI.md").write_text("\n".join(righe) + "\n", encoding="utf-8")
    print("\n".join(righe))


if __name__ == "__main__":
    for f in (sys.argv[1:] or list(FAMIGLIE)):
        e = una(f)
        print(f, e.get("trade"), flush=True)
    rapporto()
