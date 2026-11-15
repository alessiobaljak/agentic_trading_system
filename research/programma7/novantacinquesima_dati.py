"""Prova 157 (NOVANTACINQUESIMA.md): scarico dei prezzi a pronti di BTCUSDT ed ETHUSDT (mesi 2020-12 .. 2026-10) con le funzioni del
caricatore della prova 97 (non modificato), e impronte dei file. Non calcola nessun rendimento.

Uso: python3 -m research.programma7.novantacinquesima_dati
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from research.programma7 import trentacinquesima as t35

RIS = Path(__file__).parent / "risultati_novantacinquesima"
MESI = [f"{a}-{m:02d}" for a in range(2020, 2027) for m in range(1, 13) if "2020-12" <= f"{a}-{m:02d}" <= "2026-10"]
COPPIE = ("BTCUSDT", "ETHUSDT")


def main() -> None:
    t35.MESI = MESI                      # l'elenco passato da fuori; il file della 97 non si tocca
    stati = t35.scarica(list(COPPIE), log=lambda x: None)
    RIS.mkdir(exist_ok=True)
    imp = {}
    for s in COPPIE:
        f = t35.DATI / f"{s}.csv.gz"
        imp[s] = {"stato": stati[s], "sha256": hashlib.sha256(f.read_bytes()).hexdigest(), "byte": f.stat().st_size}
    (RIS / "impronte_pronti.json").write_text(json.dumps(imp, indent=1))
    print(json.dumps(imp, indent=1))


if __name__ == "__main__":
    main()
