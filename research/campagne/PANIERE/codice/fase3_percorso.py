"""Fase 3: il percorso medio dei trade già fatti (costruzione), giorno per giorno della tenuta, in R.

Per ogni trade salvato: rischio = |entrata - stop|; per ogni giorno d da 0 (il giorno dell'ingresso) a 4, il guadagno
non realizzato alla chiusura del giorno d, in R, dalle candele giornaliere del last (dati.carica_candele, fino al
2023-01-16). Media su tutti i trade e mediana; anche separato per regime di Bitcoin (sopra/sotto la media a 100).
Solo descrizione dei trade di varianti già esaminate: serve a ragionare su un ritocco dell'uscita.

Uso: fase3_percorso.py <id> [<id> ...]
"""

import json
import statistics
import sys
from datetime import date
from pathlib import Path

RADICE = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(RADICE))

from research.src import dati  # noqa: E402

CARTELLA = Path(__file__).resolve().parents[1]
GIORNO = 86_400_000


def main():
    esito = {}
    cache = {}
    for id_variante in sys.argv[1:]:
        percorsi = {d: [] for d in range(5)}
        for riga in (CARTELLA / "trade" / f"{id_variante}_costruzione.jsonl").read_text().splitlines():
            t = json.loads(riga)
            s = t["simbolo"]
            if s not in cache:
                cache[s] = {c.ts: c.close for c in dati.carica_candele(s, "1d", date(2020, 1, 1), date(2023, 1, 16))}
            rischio = abs(t["entrata"] - t["stop"])
            verso = 1 if t["direzione"] == "long" else -1
            for d in range(5):
                ts = t["ts_entrata"] + d * GIORNO
                if ts > t["ts_uscita"] or ts not in cache[s]:
                    break
                percorsi[d].append(verso * (cache[s][ts] - t["entrata"]) / rischio)
        esito[id_variante] = {f"chiusura del giorno {d}": {"n": len(v), "media_r": round(statistics.fmean(v), 3),
                                                           "mediana_r": round(statistics.median(v), 3)}
                              for d, v in percorsi.items() if v}
    (CARTELLA / "lavoro" / "fase3_percorso.json").write_text(json.dumps(esito, indent=1, ensure_ascii=False) + "\n",
                                                             encoding="utf-8")
    print(json.dumps(esito, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()
