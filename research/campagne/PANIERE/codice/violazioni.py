"""Elenca i trade salvati con violazione_liquidazione (moneta, date, entrata, stop, distanza dello stop in %).

Uso: violazioni.py <file in trade/> [...]
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

CARTELLA = Path(__file__).resolve().parents[1]


def main():
    for nome in sys.argv[1:]:
        for riga in (CARTELLA / "trade" / nome).read_text().splitlines():
            t = json.loads(riga)
            if t.get("violazione_liquidazione"):
                giorno = datetime.fromtimestamp(t["ts_entrata"] / 1000, tz=timezone.utc).date().isoformat()
                distanza = abs(t["entrata"] - t["stop"]) / t["entrata"] * 100
                print(nome, t["simbolo"], giorno, "entrata", t["entrata"], "stop", t["stop"],
                      f"distanza {distanza:.1f}%", "esito", t["esito"], "r", round(t["r"], 3), "ridotto", t["ridotto"])


if __name__ == "__main__":
    main()
