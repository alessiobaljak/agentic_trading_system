"""Prova di causalita' per troncamento (ricerca di lookahead dopo il crollo col ritardo, Fase 4).

  python prova_troncamento.py <ID> [<ID> ...]

Per ogni barra di segnale candidata (le barre che chiudono alle 23:30 UTC) e per un campione di altre
barre, ricostruisce le regole della variante sulla serie TRONCATA a quella barra (s.last[:i+1]: nessuna
barra futura esiste) e confronta condizione(i) e segnale(i) con quelli calcolati sulla serie intera.
Se tutto coincide, nessun valore usato alla barra i dipende da barre successive: niente lookahead nel
codice della variante. Sola lettura.
"""
import sys
from dataclasses import replace
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import comune  # noqa: E402
from varianti import VARIANTI  # noqa: E402

GIORNO = 24 * 3_600_000

for vid in sys.argv[1:]:
    tf, costr = VARIANTI[vid][0], VARIANTI[vid][1]
    s = comune.carica(tf, "costruzione")
    intera = costr(s)
    passo = comune.ms_tf(tf)
    da_provare = [i for i, c in enumerate(s.last) if (c.ts + passo) % GIORNO == 23 * 3_600_000 + 30 * 60_000]
    da_provare += list(range(500, len(s.last), 997))  # altre barre, sparse
    diverse, provate, segnali = 0, 0, 0
    for i in sorted(set(da_provare)):
        tronca = replace(s, last=s.last[: i + 1], mark=s.mark[: i + 1])
        r = costr(tronca)
        c1, c2 = intera.condizione(i), r.condizione(i)
        g1, g2 = intera.segnale(i), r.segnale(i)
        provate += 1
        segnali += bool(c1)
        if c1 != c2 or g1 != g2:
            diverse += 1
            if diverse <= 5:
                print("  DIVERSA alla barra", i, c1, c2, g1, g2)
    print(vid, "barre provate", provate, "con condizione vera", segnali, "diverse", diverse, flush=True)
