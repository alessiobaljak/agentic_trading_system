"""Aggiunge al log una nota il cui contenuto sta in un file JSON di lavoro/ (testo lungo senza heredoc né virgolette nella shell).

Uso: nota_libera.py <nome del file in lavoro/>. Il file contiene un dizionario JSON: diventa la voce, con tipo «nota»
(se non è dato), id progressivo e data dall'orologio della macchina.
"""

import json
import sys
from pathlib import Path

CODICE = Path(__file__).resolve().parent
sys.path.insert(0, str(CODICE))

import registro  # noqa: E402


def main():
    campi = json.loads((CODICE.parent / "lavoro" / sys.argv[1]).read_text(encoding="utf-8"))
    campi.setdefault("tipo", "nota")
    voce = registro.aggiungi(campi)
    print(voce["id"], voce["data"])


if __name__ == "__main__":
    main()
