"""Controllo delle impronte dopo un nuovo scaricamento (sezione 5 del protocollo).

Uso: python research/campagne/ETHUSDT/codice/controllo_impronte.py

Confronta i file in data/insample/ETHUSDT e data/insample/BTCUSDT con le impronte
registrate in Fase 0 (impronte.json, la cui impronta e' scritta in fase0_dati.md) usando
``dati.verifica_impronte``. Scrive l'esito in data/insample/ETHUSDT/lavoro/impronte_esito.txt:
se una impronta cambia, STOP.
"""

import hashlib
import json
import re
import sys
from pathlib import Path

RADICE_REPO = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(RADICE_REPO))

from research.src import dati  # noqa: E402

CARTELLA = RADICE_REPO / "research" / "campagne" / "ETHUSDT"
USCITA = RADICE_REPO / "research" / "data" / "insample" / "ETHUSDT" / "lavoro" / "impronte_esito.txt"


def main() -> None:
    testo = (CARTELLA / "impronte.json").read_text(encoding="utf-8")
    sha = hashlib.sha256(testo.encode("utf-8")).hexdigest()
    registrata = re.findall(r"[0-9a-f]{64}", (CARTELLA / "fase0_dati.md").read_text(encoding="utf-8"))
    righe = [f"impronta di impronte.json: {sha}", f"uguale a quella di fase0_dati.md: {sha in registrata}"]
    attese = json.loads(testo)
    radice = RADICE_REPO / "research"
    totale = 0
    for simbolo in ("ETHUSDT", "BTCUSDT"):
        differenze = dati.verifica_impronte(simbolo, radice, attese[simbolo])
        totale += len(differenze)
        righe.append(f"{simbolo}: {len(attese[simbolo])} file attesi, differenze {len(differenze)}")
        righe += [f"  {d}" for d in differenze]
    righe.append("ESITO: " + ("tutte uguali" if totale == 0 and sha in registrata else "DIFFERENZE: STOP"))
    USCITA.parent.mkdir(parents=True, exist_ok=True)
    USCITA.write_text("\n".join(righe) + "\n", encoding="utf-8")
    print("\n".join(righe[-4:]))


if __name__ == "__main__":
    main()
