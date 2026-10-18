"""E-112 — reti di ordini limite su C2, fase 2 (piano.md). Uso: PYTHONPATH=. python3 research/programma5/esplorazione/E-112/esplora.py"""
import json
import sys
import warnings
from pathlib import Path

import numpy as np

from research.programma5.strumenti.esplora_limiti import esplora, promossa
from research.programma5.strumenti.scarico import MONETE

QUI = Path(__file__).parent
CENTO = json.loads((QUI.parents[1] / "universo_top100.json").read_text())["scelte"]


# piano.md, aggiunta prima del calcolo: le famiglie gia' provate su V2 dalle idee J non si promuovono
def visto_v2(nome, r):
    return nome.startswith(("R acquisto", "S acquisto"))


def riga(n, r):
    sem = " ".join(f"{a}:{100 * m:+.2f}({k})" for a, (k, m) in r.get("per_semestre", {}).items())
    monete = [m for k, m in r.get("per_moneta", {}).values() if k >= 10]
    giuste = sum(1 for m in monete if m > 0)
    doppio = f"{100 * r['doppio']:+.3f}%" if "doppio" in r else ""
    return (f"| {n} | {r['trade']} | {100 * r['lordo']:+.3f}% | {doppio} | {100 * r['contro_caso']:+.3f}% | {r['t']:+.2f} | "
            f"{sem} | {giuste}/{len(monete)} | {'**sì**' if r['promossa'] else ('visto V2' if r.get('visto_V2') else '')} |")


def main():
    warnings.filterwarnings("ignore")
    ris = esplora(tuple(CENTO), "C2")
    for n, r in ris.items():
        r["visto_V2"] = visto_v2(n, r)
        r["promossa"] = bool(r.get("trade")) and promossa(n, r, monete_min=20) and not r["visto_V2"]
    (QUI / "risultati.json").write_text(json.dumps(ris, ensure_ascii=False, indent=0), encoding="utf-8")
    validi = {n: r for n, r in ris.items() if r.get("trade", 0) > 0 and np.isfinite(r.get("t", np.nan))}
    promosse = {n: r for n, r in validi.items() if r["promossa"]}
    testa = ["| Cella | Trade | Lordo (R) / netto (S) | Netto a costi doppi (S) | Contro il caso | t | Per semestre | "
             "Monete positive (≥10 trade) | Promossa |", "|---|---|---|---|---|---|---|---|---|"]
    righe = ["# E-112 — risultati", "", "Calcolo di `esplora.py` su C2, 100 monete (piano: `piano.md`).", "",
             f"Celle: **{len(ris)}** ({len(validi)} con trade). Promosse: **{len(promosse)}**.", "", "## Celle promosse", ""]
    righe += (testa + [riga(n, r) for n, r in sorted(promosse.items(), key=lambda x: -x[1]["t"])]) if promosse \
        else ["Nessuna."]
    righe += ["", "## Le 30 celle con t più alto", ""] + testa
    righe += [riga(n, r) for n, r in sorted(validi.items(), key=lambda x: -x[1]["t"])[:30]]
    righe += ["", "Tutte le celle sono in `risultati.json`."]
    (QUI / "risultati.md").write_text("\n".join(righe) + "\n", encoding="utf-8")
    print(f"promosse {len(promosse)}")


if __name__ == "__main__":
    sys.exit(main())
