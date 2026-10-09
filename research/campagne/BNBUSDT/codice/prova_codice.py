"""Controllo tecnico: ogni variante prepara gli indicatori e valuta condizione e segnale su
UNA barra senza errori. Non conta segnali ne' trade e non guarda risultati."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import comune as C  # noqa: E402
import varianti as V  # noqa: E402

lista = [V.i01("long", "x"), V.i01("short", "x"), V.i02("long", "x"), V.i02("short", "x"),
         V.i03("1h", "x"), V.i03("4h", "x"), V.i04("x"), V.i05("short", "x"), V.i05("long", "x"),
         V.i06("long", "x"), V.i06("short", "x"), V.i07("x"), V.i08("long", "x"), V.i08("short", "x"),
         V.i09("long", "x"), V.i09("short", "x"), V.i10("long", "x"), V.i10("short", "x"),
         V.i11("long", "x"), V.i11("short", "x"), V.i12(3.0, "x"), V.i13("x")]
for v in lista:
    d = C.carica(v.tf)
    ind = v.prepara(d["candele"])
    i = len(d["candele"]) // 2
    v.condizione(ind, i)
    s = v.segnale(ind, i, d["candele"])
    print(v.tf, v.direzione, "ok", type(s).__name__, sorted(ind.keys())[:3])
