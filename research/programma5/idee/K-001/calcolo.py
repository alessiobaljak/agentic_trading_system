"""K-001 — il modello che mette insieme i segnali (scheda.md). Uso: PYTHONPATH=. python3 research/programma5/idee/K-001/calcolo.py C2|V2"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

from research.programma5.strumenti import modello as mo
from research.programma5.strumenti import portafoglio as pf
from research.programma5.strumenti.fase2 import MONETE_F2

QUI = Path(__file__).parent
LAMBDA = (1, 10, 100, 1000)
INIZIO_2025 = 29_453_760 - 525_600      # 2025-01-01 00:00 UTC in minuti dall'epoca


def netto_per_decisione(t: pd.DataFrame) -> float:
    return float(t.groupby("decisione")["netto"].sum().mean()) if len(t) else float("nan")


def rapporto(periodo: str, t: pd.DataFrame, casi: pd.DataFrame, extra: dict) -> None:
    e = pf.esame_portafoglio(t, casi)
    per_dec = t.groupby("decisione").agg(minuto=("minuto", "first"), netto=("netto", "sum"))
    giorno = per_dec["minuto"] // 1440
    somme = per_dec.groupby(giorno)["netto"].sum()
    e["senza_migliore"] = float(per_dec["netto"][giorno != somme.idxmax()].mean())
    if periodo == "V2":
        prima = per_dec["minuto"] < pf.MEZZO_V2
        e["per_meta"] = {"2025-07 → 2025-12": {"trade": int(prima.sum()), "netto": float(per_dec["netto"][prima].mean())},
                         "2026-01 → 2026-09": {"trade": int((~prima).sum()), "netto": float(per_dec["netto"][~prima].mean())}}
    e.update(extra)
    ok, motivo = pf.esito(periodo, e, 1)
    if periodo == "V2" and ok and not e["netto"]["media"] > e.get("caso_netto", float("inf")):
        ok, motivo = False, "non meglio del caso"
    e["esito"] = motivo
    (QUI / f"{periodo}.json").write_text(json.dumps(e, ensure_ascii=False, indent=1, default=float), encoding="utf-8")
    t.to_csv(QUI / f"trade_{periodo}_K-001a.csv.gz", index=False)
    nt = e["netto"]
    righe = [f"# K-001 — periodo {periodo}", "", f"Numeri da `{periodo}.json`; netto **del portafoglio** a decisione (un "
             "giorno), per unità di capitale; esame di REGOLE.md, sezioni 7 e 10.", "",
             "| Variante | Portafogli | Gambe | Netto | Intervallo al 95% | p | A costi doppi | Senza il giorno migliore | "
             "Caso | Esito |", "|---|---|---|---|---|---|---|---|---|---|",
             f"| K-001a | {e['portafogli']} | {e['trade']} | {100 * nt['media']:+.3f}% | {100 * nt['basso']:+.3f}; "
             f"{100 * nt['alto']:+.3f} | {nt['p']:.4f} | {100 * e['netto_doppio']['media']:+.3f}% | "
             f"{100 * e['senza_migliore']:+.3f}% | {100 * e.get('caso_netto', float('nan')):+.3f}% | "
             f"{'**' + motivo + '**' if ok else motivo} |"]
    if e.get("per_meta"):
        righe.append("\n* per metà: " + ", ".join(f"{k} {100 * v['netto']:+.3f}% ({v['trade']})" for k, v in e["per_meta"].items()))
    if "scelta_lambda" in extra:
        righe.append("\n* scelta di λ (netto a portafoglio sul primo semestre 2025, costruendo sul 2024): " +
                     ", ".join(f"{k}: {100 * v:+.3f}%" for k, v in extra["scelta_lambda"].items()))
    (QUI / f"{periodo}.md").write_text("\n".join(righe) + "\n", encoding="utf-8")
    print("\n".join(righe))


def casi(ore, dec, monete, Z, pesi, A24, ripetizioni=20):
    rng = np.random.default_rng(2026)
    out = []
    for r in range(ripetizioni):
        c = mo.portafoglio_da_previsioni(ore, dec, monete, Z, pesi, A24, rng=rng)
        c["ripetizione"] = r
        out.append(c)
    return pd.concat(out, ignore_index=True)


def main(periodo: str) -> None:
    ore, dec, monete, Z, Y, A24 = mo.dataset(MONETE_F2, periodo, "K-001")
    minuti_dec = (ore[dec] + 1) * 60
    if periodo == "C2":
        prima = minuti_dec < INIZIO_2025
        scelta = {}
        for lam in LAMBDA:
            b = mo.ridge(Z[prima], Y[prima], lam)
            t = mo.portafoglio_da_previsioni(ore, dec[~prima], monete, Z[~prima], b, A24)
            scelta[str(lam)] = netto_per_decisione(t)
        lam = float(max(scelta, key=lambda k: scelta[k]))
        pesi = mo.ridge(Z, Y, lam)
        (QUI / "pesi.json").write_text(json.dumps({"lambda": lam, "pesi": dict(zip(mo.SEGNALI, map(float, pesi))),
                                                   "scelta_lambda": scelta}, indent=1), encoding="utf-8")
        extra = {"scelta_lambda": scelta, "lambda": lam}
    else:
        dati = json.loads((QUI / "pesi.json").read_text())
        pesi = np.array([dati["pesi"][s] for s in mo.SEGNALI])
        extra = {"lambda": dati["lambda"]}
    t = mo.portafoglio_da_previsioni(ore, dec, monete, Z, pesi, A24)
    rapporto(periodo, t, casi(ore, dec, monete, Z, pesi, A24), extra)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "C2")
