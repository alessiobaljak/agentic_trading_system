"""M-001 — ogni mese i segnali che hanno funzionato nei mesi prima (scheda.md, REGOLE.md sezione 8).
Uso: PYTHONPATH=. python3 research/programma5/idee/M-001/calcolo.py W"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

from research.programma5.strumenti import meta
from research.programma5.strumenti import motore5 as m5
from research.programma5.strumenti.fase2 import MONETE_F2

QUI = Path(__file__).parent
VARIANTI = {"M-001a": {"L": 6, "K": 10}, "M-001b": {"L": 3, "K": 10}, "M-001c": {"L": 12, "K": 10}}
PRIMO, ULTIMO, N_MESI = 12, 80, 81          # 2021-01 ... 2026-09, mesi contati da 2020-01
INIZIO_V2 = meta.minuto_mese(66)           # 2025-07-01


def esame(t: pd.DataFrame, n_boot: int = 10000) -> dict:
    if t.empty:
        return {"trade": 0}
    m = t["minuto"].to_numpy()
    out = {"trade": int(len(t)), "netto": m5.bootstrap_giorni(t["netto"].to_numpy(), m, n_boot),
           "netto_doppio": m5.bootstrap_giorni(t["netto_doppio"].to_numpy(), m, n_boot),
           "lordo": float(t["lordo"].mean()), "costo": float(t["costo"].mean())}
    giorno = m // 1440
    somme = t.groupby(giorno)["netto"].sum()
    out["senza_migliore"] = float(t["netto"][giorno != somme.idxmax()].mean())
    anni = pd.to_datetime(m * 60, unit="s").year
    out["per_anno"] = {int(a): {"trade": int((anni == a).sum()), "netto": float(t["netto"][anni == a].mean())}
                       for a in sorted(set(anni))}
    v2 = t[t["minuto"] >= INIZIO_V2]
    out["V2"] = m5.bootstrap_giorni(v2["netto"].to_numpy(), v2["minuto"].to_numpy(), n_boot) if len(v2) else {}
    out["per_moneta"] = {s: {"trade": int(len(g)), "netto": float(g["netto"].mean())} for s, g in t.groupby("simbolo")}
    out["per_cella"] = {f"{c} | {v}": {"trade": int(len(g)), "netto": float(g["netto"].mean())}
                        for (c, v), g in t.groupby(["cella", "verso"])}
    return out


def esito(e: dict, n_varianti: int) -> tuple:
    if not e.get("trade"):
        return False, "nessun trade"
    nt = e["netto"]
    if not nt["basso"] > 0:
        return False, "netto con l'intervallo non sopra zero"
    if not nt["p"] <= 0.005 / n_varianti:
        return False, f"p {nt['p']:.4f} oltre la soglia {0.005 / n_varianti:.4f}"
    if not e["netto_doppio"]["media"] > 0:
        return False, "non positivo a costi doppi"
    if not e["senza_migliore"] > 0:
        return False, "non positivo togliendo il giorno migliore"
    anni = [a for a in e["per_anno"].values() if a["trade"] > 0]
    if sum(1 for a in anni if a["netto"] > 0) < 4:
        return False, "positivo in meno di 4 anni"
    if not e.get("V2", {}).get("media", -1) > 0:
        return False, "non positivo su V2"
    monete = [x for x in e["per_moneta"].values() if x["trade"] >= 20]
    if sum(1 for x in monete if x["netto"] > 0) < 0.6 * len(monete):
        return False, "positivo su meno del 60% delle monete"
    if not e.get("placebo_ok", False):
        return False, "la prova a placebo non torna"
    return True, "passa: procedura valida"


def main(periodo: str) -> None:
    per_cella = meta.trade_candidate(MONETE_F2, periodo, "M-001")
    cand = meta.con_versi(per_cella)
    print(f"candidate {len(cand)}", flush=True)
    dati, scelte_tutte = {}, {}
    rng = np.random.default_rng(2026)
    for n, v in VARIANTI.items():
        t, scelte = meta.scegli_e_tieni(cand, v["L"], v["K"], PRIMO, ULTIMO, N_MESI)
        e = esame(t)
        # placebo: segno del lordo di ogni trade a caso, 20 ripetizioni
        plac = []
        for r in range(20):
            segni = {k: rng.choice([-1.0, 1.0], len(x)) for k, x in cand.items()}
            tp, _ = meta.scegli_e_tieni(cand, v["L"], v["K"], PRIMO, ULTIMO, N_MESI, segni=segni)
            plac.append((float(tp["netto"].mean()) if len(tp) else float("nan"),
                         float(tp["costo"].mean()) if len(tp) else float("nan"), int(len(tp))))
        pn = np.array([p[0] for p in plac])
        pc = np.array([p[1] for p in plac])
        e["placebo"] = {"netto_medio": float(np.nanmean(pn)), "costo_medio": float(np.nanmean(pc)),
                        "netto_min": float(np.nanmin(pn)), "netto_max": float(np.nanmax(pn)),
                        "trade_medi": float(np.mean([p[2] for p in plac]))}
        # nessun guadagno: il netto medio del placebo non sopra meno i costi (con un margine di un decimo dei costi)
        e["placebo_ok"] = bool(e["placebo"]["netto_medio"] <= -0.9 * e["placebo"]["costo_medio"])
        dati[n] = e
        scelte_tutte[n] = {str(m): [f"{c} | {vv}" for c, vv in s] for m, s in scelte.items()}
        if len(t):
            t.to_csv(QUI / f"trade_{periodo}_{n}.csv.gz", index=False)
        print(n, e.get("trade"), e.get("netto", {}).get("media"), e["placebo"], flush=True)
    (QUI / f"{periodo}.json").write_text(json.dumps(dati, ensure_ascii=False, indent=1, default=float), encoding="utf-8")
    (QUI / f"scelte_{periodo}.json").write_text(json.dumps(scelte_tutte, ensure_ascii=False, indent=0), encoding="utf-8")
    righe = [f"# M-001 — periodo {periodo}", "", "Numeri da `W.json` (calcolo `calcolo.py W`); esame di REGOLE.md, "
             "sezione 8. Netto a trade dopo i costi (scarto doppio), trade scelti dal 2021-01 al 2026-09.", "",
             "| Variante | Trade | Netto | Intervallo al 95% | p | A costi doppi | Senza il giorno migliore | V2 | "
             "Placebo (netto; costo) | Esito |", "|---|---|---|---|---|---|---|---|---|---|"]
    for n, e in dati.items():
        ok, motivo = esito(e, len(dati))
        if not e.get("trade"):
            righe.append(f"| {n} | 0 | | | | | | | | {motivo} |")
            continue
        nt, v2, pl = e["netto"], e.get("V2", {}), e["placebo"]
        righe.append(f"| {n} | {e['trade']} | {100 * nt['media']:+.3f}% | {100 * nt['basso']:+.3f}; {100 * nt['alto']:+.3f} | "
                     f"{nt['p']:.4f} | {100 * e['netto_doppio']['media']:+.3f}% | {100 * e['senza_migliore']:+.3f}% | "
                     f"{100 * v2.get('media', float('nan')):+.3f}% | {100 * pl['netto_medio']:+.3f}%; "
                     f"{100 * pl['costo_medio']:.3f}% | {'**' + motivo + '**' if ok else motivo} |")
    righe += ["", "Per anno (netto medio a trade):", ""]
    for n, e in dati.items():
        if e.get("trade"):
            righe.append(f"* **{n}** — " + ", ".join(f"{a}: {100 * x['netto']:+.3f}% ({x['trade']})"
                                                       for a, x in e["per_anno"].items()))
    (QUI / f"{periodo}.md").write_text("\n".join(righe) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "W")
