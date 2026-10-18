"""Scrive nel log, prima del primo test, la nota con l'ordine delle 18 varianti e il rimando alle previsioni."""

import json
import sys
from pathlib import Path

CODICE = Path(__file__).resolve().parent
sys.path.insert(0, str(CODICE))

import registro  # noqa: E402


def main():
    prev = json.loads((CODICE / "previsioni.json").read_text(encoding="utf-8"))
    voce = registro.aggiungi({
        "tipo": "nota",
        "testo": ("Controllo positivo passato in tutte e due le direzioni (PANIERE-012 e PANIERE-014: long t 4,84 senza "
                  "ritardo e -0,45 con il ritardo; short 6,02 e -0,14; batte nettamente (a) e (b), nessuna moneta senza "
                  "ingressi della (b), terreno della seconda edizione con l'ordine limite). Ordine dei test delle 18 "
                  "varianti, scritto prima di qualunque conta_trade: quello qui sotto, in serie con codice/lotto.py "
                  "(conta, registra o scarta, esamina in costruzione). Previsioni e criterio di successo di ogni "
                  "variante in codice/previsioni.json, copiati nella registrazione di ciascuna. Moduli: "
                  "codice/tendenza.py (A), codice/trasversale.py (B), codice/ritardo.py (C); parametri in "
                  "codice/varianti_A.json, varianti_B.json, varianti_C.json."),
        "ordine": prev["ordine"],
    })
    print(voce["id"], voce["data"])


if __name__ == "__main__":
    main()
