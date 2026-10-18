"""M-001 — diagnosi **dopo** l'esame (non cambia l'esito di W.md): (1) la prova a placebo con 200 ripetizioni invece di 20,
per sapere se la procedura guarda avanti o se il -0,164% era rumore; (2) il confronto con il caso: gli stessi trade scelti da
M-001c (stessa moneta, stesso mese d'ingresso, stessa direzione, stessa durata, stessi costi) a un'ora qualunque del mese.

Uso: PYTHONPATH=. python3 research/programma5/idee/M-001/diagnosi.py
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
from calcolo import N_MESI, PRIMO, ULTIMO, VARIANTI  # noqa: E402

from research.programma5.strumenti import meta  # noqa: E402
from research.programma5.strumenti.esplora_calendario import celle as celle_calendario  # noqa: E402
from research.programma5.strumenti.esplora_fase2 import BTC, celle_moneta  # noqa: E402
from research.programma5.strumenti.fase2 import MONETE_F2  # noqa: E402

QUI = Path(__file__).parent


def main():
    ore, P, A = meta.pannello(MONETE_F2, "W", "M-001")
    # direzione «segue» e durata di ogni cella
    b, btc = P["ETHUSDT"], P[BTC]
    info = {n: (int(d[0]), h) for n, f, h, p, c, d, v in celle_moneta("ETHUSDT", b, btc, A)}
    info.update({n: (int(d[0]), h) for n, f, h, p, c, d in celle_calendario(b)})
    out = {}
    # (2) il caso per M-001c
    t = pd.read_csv(QUI / "trade_W_M-001c.csv.gz")
    rng = np.random.default_rng(2026)
    mese_ora = meta.indice_mese(ore * 60)
    casi = []
    for r in range(20):
        valori = np.full(len(t), np.nan)
        for i, (s, m_ent, cella, verso, c) in enumerate(zip(t["simbolo"], meta.indice_mese(t["minuto"].to_numpy()),
                                                            t["cella"], t["verso"], t["costo"])):
            d, h = info[cella]
            D = d * (1 if verso == "segue" else -1)
            a = A[h][s]
            if cella.startswith("G1"):
                continue                      # coperte con BTC: il caso semplice non vale
            pos = np.flatnonzero((mese_ora == m_ent) & np.isfinite(a))
            if len(pos):
                valori[i] = D * a[rng.choice(pos)] - c
        casi.append(np.nanmean(valori))
    escluse = int(t["cella"].str.startswith("G1").sum())
    out["caso_M-001c"] = {"netto_caso_medio": float(np.mean(casi)), "netto_caso_min": float(np.min(casi)),
                          "netto_caso_max": float(np.max(casi)), "netto_strategia": float(t["netto"].mean()),
                          "netto_strategia_senza_G1": float(t["netto"][~t["cella"].str.startswith("G1")].mean()),
                          "trade_G1_esclusi": escluse}
    print(out["caso_M-001c"], flush=True)
    # (1) placebo con 200 ripetizioni per M-001c
    per_cella = meta.trade_candidate(MONETE_F2, "W", "M-001", log=lambda x: None)
    cand = meta.con_versi(per_cella)
    v = VARIANTI["M-001c"]
    rng = np.random.default_rng(7)
    netti, costi = [], []
    for r in range(200):
        segni = {k: rng.choice([-1.0, 1.0], len(x)) for k, x in cand.items()}
        tp, _ = meta.scegli_e_tieni(cand, v["L"], v["K"], PRIMO, ULTIMO, N_MESI, segni=segni)
        netti.append(float(tp["netto"].mean()))
        costi.append(float(tp["costo"].mean()))
        if r % 20 == 19:
            print(r + 1, np.mean(netti), np.std(netti) / np.sqrt(len(netti)), np.mean(costi), flush=True)
    out["placebo_200_M-001c"] = {"netto_medio": float(np.mean(netti)),
                                 "errore_della_media": float(np.std(netti) / np.sqrt(len(netti))),
                                 "costo_medio": float(np.mean(costi)), "ripetizioni": 200}
    (QUI / "diagnosi.json").write_text(json.dumps(out, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
