"""Controllo tecnico: ogni variante prepara gli indicatori e valuta condizione e segnale su
UNA barra senza errori. Non conta segnali ne' trade e non guarda risultati."""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))

import comune as C  # noqa: E402
import varianti as V  # noqa: E402

lista = [V.i08("long", "x"), V.i06("long", "x", "1h"), V.i07("x", 0.8), V.i14("x"),
         V.i15("long", "x"), V.i15("short", "x"), V.i16("x"), V.i17("x")]
for v in lista:
    d = C.carica(v.tf)
    ind = v.prepara(d["candele"])
    i = len(d["candele"]) // 2
    v.condizione(ind, i)
    s = v.segnale(ind, i, d["candele"])
    finiti = {k: bool(np.isfinite(np.asarray(ind[k], dtype=float)[i])) for k in ind if k not in ("ts",)}
    print(v.tf, v.direzione, "ok", type(s).__name__, finiti)
