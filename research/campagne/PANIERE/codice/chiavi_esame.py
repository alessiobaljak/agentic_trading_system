"""Stampa le chiavi (non i valori) del dizionario di un esame salvato, per scrivere bene gli script di riassunto."""

import json
import sys
from pathlib import Path

CARTELLA = Path(__file__).resolve().parents[1]


def main():
    esito = json.loads((CARTELLA / "lavoro" / sys.argv[1]).read_text(encoding="utf-8"))
    esame = esito["esami"]["senza_ritardo"]
    print("chiavi:", sorted(esame))
    print("baseline_b:", sorted(esame.get("baseline_b", {})))
    print("baseline_a:", sorted(esame.get("baseline_a", {})))


if __name__ == "__main__":
    main()
