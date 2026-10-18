"""E-103 — esplorazione a ore su C2, fase 2 (piano.md). Uso: PYTHONPATH=. python3 research/programma5/esplorazione/E-103/esplora.py"""
import json
import sys
import warnings
from pathlib import Path

import numpy as np

from research.programma5.strumenti.esplora_calendario import esplora
from research.programma5.strumenti.scarico import MONETE

QUI = Path(__file__).parent
NUOVE = json.loads((QUI.parents[1] / "universo_fase2.json").read_text())["scelte"]


def riga(n, r):
    sem = " ".join(f"{a}:{100 * m:+.2f}({k})" for a, (k, m) in r.get("per_semestre", {}).items())
    monete = [m for k, m in r.get("per_moneta", {}).values() if k >= 10]
    segno = np.sign(r.get("lordo", 0))
    giuste = sum(1 for m in monete if segno * m > 0)
    return (f"| {n} | {r['trade']} | {100 * r['lordo']:+.3f}% | {100 * r['contro_caso']:+.3f}% | {r['t']:+.2f} | {sem} | "
            f"{giuste}/{len(monete)} | {'**sì**' if r['promossa'] else ''}{' (parente R)' if r.get('parente_R') else ''} |")


def main():
    warnings.filterwarnings("ignore")
    ris = esplora(tuple(MONETE) + tuple(NUOVE), "C2")
    (QUI / "risultati.json").write_text(json.dumps(ris, ensure_ascii=False, indent=0), encoding="utf-8")
    validi = {n: r for n, r in ris.items() if r.get("trade", 0) > 0 and np.isfinite(r.get("t", np.nan))}
    promosse = {n: r for n, r in validi.items() if r["promossa"]}
    testa = ["| Cella | Trade | Lordo «segue» | Contro il caso | t | Per semestre (lordo %, trade) | Monete col segno "
             "(≥10 trade) | Promossa |", "|---|---|---|---|---|---|---|---|"]
    righe = ["# E-103 — risultati", "", "Calcolo di `esplora.py` su C2 (2024-01-01 → 2025-06-30), 24 monete (piano: "
             "`piano.md`). Lordo a trade, funding compreso, senza commissioni e scarto (0,12-0,14% a giro). Negativo = "
             "conviene «contro».", "", f"Celle: **{len(ris)}** ({len(validi)} con trade). Promosse: **{len(promosse)}**.",
             "", "## Celle promosse", ""]
    righe += (testa + [riga(n, r) for n, r in sorted(promosse.items(), key=lambda x: -abs(x[1]["t"]))]) if promosse \
        else ["Nessuna."]
    righe += ["", "## Le 40 celle con |t| più alto", ""] + testa
    righe += [riga(n, r) for n, r in sorted(validi.items(), key=lambda x: -abs(x[1]["t"]))[:40]]
    righe += ["", "Tutte le celle sono in `risultati.json`."]
    (QUI / "risultati.md").write_text("\n".join(righe) + "\n", encoding="utf-8")
    print(f"promosse {len(promosse)}")


if __name__ == "__main__":
    sys.exit(main())
