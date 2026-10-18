"""M-001 — controllo che il codice di oggi (motore5.py con il periodo WA in piu') rifaccia **gli stessi** trade di M-001c
sul periodo W: serve alla prova in avanti (REGOLE.md, sezione 9), che usa M-001c com'era.
Uso: PYTHONPATH=. python3 research/programma5/idee/M-001/riprova_W.py"""
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
from calcolo import N_MESI, PRIMO, ULTIMO, VARIANTI  # noqa: E402

from research.programma5.strumenti import meta  # noqa: E402
from research.programma5.strumenti.fase2 import MONETE_F2  # noqa: E402

QUI = Path(__file__).parent
cand = meta.con_versi(meta.trade_candidate(MONETE_F2, "W", "M-001", log=lambda x: None))
v = VARIANTI["M-001c"]
t, _ = meta.scegli_e_tieni(cand, v["L"], v["K"], PRIMO, ULTIMO, N_MESI)
vecchi = pd.read_csv(QUI / "trade_W_M-001c.csv.gz")
nuovi = t.reset_index(drop=True)
uguali = (len(vecchi) == len(nuovi) and (vecchi["minuto"].to_numpy() == nuovi["minuto"].to_numpy()).all()
          and (vecchi["simbolo"].to_numpy() == nuovi["simbolo"].to_numpy()).all()
          and abs(vecchi["netto"].to_numpy() - nuovi["netto"].to_numpy()).max() < 1e-12)
testo = f"trade W di M-001c: prima {len(vecchi)}, oggi {len(nuovi)}; uguali: {uguali}\n"
(QUI / "riprova_W.txt").write_text(testo, encoding="utf-8")
print(testo)
