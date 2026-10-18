"""Diagnosi (solo lettura degli strumenti) dei due test di research/src/tests/test_statistica3.py che falliscono
su questa macchina: quanto sono lontani i valori confrontati e con quali versioni delle librerie.
Nessun dato di mercato: usa la serie piatta del test. Esito stampato a schermo.
"""

from __future__ import annotations

import platform
import sys
from pathlib import Path

RADICE_REPO = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(RADICE_REPO))

import numpy as np  # noqa: E402

from research.src import statistica3 as st  # noqa: E402
from research.src.tests import test_statistica3 as tt  # noqa: E402


def main() -> None:
    print("python", platform.python_version(), "numpy", np.__version__)
    s = tt.serie_piatta(8 * 168 + 24)
    v = {"timeframe": "1h", "direzione": "long", "filtro": {"codice": "F6", "giorni": "fine_settimana"},
         "ingresso": {"codice": "E11", "soglia": 0.0003}, "conferma": None, "tipo_ingresso": {"codice": "M"},
         "stop": {"codice": "S3", "pct": 0.01}, "uscite": [{"codice": "U2", "n": 24}]}
    out = st.fase2(v, s, 0, len(s) - 1)
    cand = out["metriche"]["r_medio"]
    valori = out["valori_casuali"]
    vicini = valori[np.abs(valori - cand) < 1e-9]
    print("candidato", repr(cand), "trade r", repr(out["risultato"].trade[0].r))
    print("simulazioni vicine", len(vicini), "differenze distinte", sorted({float(x - cand) for x in vicini}))
    print("p_value", out["p_value"], "con pareggi contati", (1 + int(np.sum(valori >= cand - 1e-12))) / 1001)


if __name__ == "__main__":
    main()
