"""P35: il mazzo contiene le serie giuste? Effetto delle serie vecchie (prima delle parita') e della 157 bocciata. Sola lettura."""
import json
import math
import pickle
import sys
from pathlib import Path

import numpy as np
import pandas as pd

REPO = Path("/home/user/agentic_trading_system")
sys.path.insert(0, str(REPO))
OUT = Path(__file__).parent
from research.programma6 import asticella as ast  # noqa: E402
from research.programma6 import terza as te  # noqa: E402

P6 = REPO / "research/programma6"
P7 = REPO / "research/programma7"
serie, soli = pickle.load(open(OUT / "mazzo.pkl", "rb"))
mis = json.loads((REPO / "audits/repro/g1_parte2_2026-11-12_esito_misure.json").read_text())["misure"]["G1"]
K = ("sharpe", "settimane", "asimmetria", "curtosi")
e57 = json.loads((P7 / "risultati_prima/esame.json").read_text())["intero"]
cand = {"G1 misura g1_parte2": tuple(mis[k] for k in K), "G1 esame.json 57": tuple(e57[k] for k in K)}

par = {"24 F5": "settimane_F5.csv.gz", "28 K2": "settimane_K2.csv.gz", "28 F5+M7+K2": "settimane_F5_M7_K2.csv.gz",
       "56 F9": "settimane_F9.csv.gz"}
nuove = {}
for n, f in par.items():
    s = pd.read_csv(P6 / "risultati_controllo_parita" / f, index_col=0)["netto"]
    s = ast.periodo(s)
    vecchia = serie[n]
    c = vecchia.index.intersection(s.index)
    print(f"{n}: Sharpe nel mazzo {ast.sharpe(vecchia):.3f} ({len(vecchia)} sett.), dopo le parita' {ast.sharpe(s):.3f} ({len(s)} sett.); "
          f"settimane diverse {int(((vecchia.loc[c] - s.loc[c]).abs() > 1e-9).sum())} su {len(c)}")
    nuove[n] = s

e = json.loads((P7 / "risultati_novantacinquesima").joinpath("esame.json").read_text()) if (P7 / "risultati_novantacinquesima/esame.json").exists() else {}


def conto(serie_d, soli_l, etichetta, solo_fino=None):
    s = dict(serie_d)
    z = list(soli_l)
    if solo_fino is not None:
        s = {k: v for k, v in s.items() if not k.split()[0].isdigit() or int(k.split()[0]) <= solo_fino}
        z = None
    gr = ast.gruppi(s, ast.TAGLIO)
    if z is None:
        prove = ast.le_prove()
        z = [x for _, ss, x in prove if ss is None]
    sr_g, sr_v = ast.per_v(gr, z, False), ast.per_v(gr, z, True)
    r = {c: round(te.sharpe_corretto(*a, sr_v, 52, n_prove=len(sr_g)), 4) for c, a in cand.items()}
    print(f"{etichetta:60s} serie {len(s)} N {len(sr_g)} in V {len(sr_v)} dev {np.std(sr_v, ddof=1):.4f} {r}")


conto(serie, soli, "mazzo di oggi")
conto({**serie, **nuove}, soli, "mazzo di oggi con F5, K2, miscela e F9 dopo le parita'")
conto(serie, soli, "fino alla 57 (serie di oggi)", solo_fino=57)
conto({**serie, **nuove}, soli, "fino alla 57 con le serie dopo le parita'", solo_fino=57)
senza157 = {k: v for k, v in serie.items() if not k.startswith("157 ")}
conto(senza157, soli, "mazzo di oggi senza la 157 (calcolo bocciato dal revisore)")
