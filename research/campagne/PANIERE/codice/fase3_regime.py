"""Fase 3: quanti trade (già fatti, di costruzione) cadono con Bitcoin in tendenza e quanti no, e con che R.

Non conta i trade di regole nuove (vietato): guarda soltanto i trade salvati delle varianti già esaminate, divisi
secondo la posizione di Bitcoin il giorno di segnale: chiusura sopra o sotto la media semplice delle ultime 100
chiusure, e rendimento degli ultimi 60 giorni positivo o no (le grandezze del filtro dell'idea A, su Bitcoin). Serve a
sapere, prima di un ritocco, quanto taglierebbe un filtro di regime e se resterebbero 700 trade.

Uso: fase3_regime.py <id> [<id> ...]
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
    btc = dati.carica_candele("BTCUSDT", "1d", date(2020, 1, 1), date(2023, 1, 16))
    indice = {c.ts: i for i, c in enumerate(btc)}
    esito = {}
    for id_variante in sys.argv[1:]:
        righe = (CARTELLA / "trade" / f"{id_variante}_costruzione.jsonl").read_text().splitlines()
        gruppi = {}
        for riga in righe:
            t = json.loads(riga)
            i = indice.get(t["ts_entrata"] - GIORNO)
            if i is None or i < 100:
                chiave = "non calcolabile"
            else:
                media = statistics.fmean(c.close for c in btc[i - 99:i + 1])
                sopra = btc[i].close > media
                rend = btc[i].close / btc[i - 60].close - 1 > 0
                chiave = f"btc {'sopra' if sopra else 'sotto'} la media 100, rendimento 60 {'positivo' if rend else 'non positivo'}"
            gruppi.setdefault(chiave, []).append(t["r"])
        esito[id_variante] = {k: {"n": len(v), "r_medio": round(statistics.fmean(v), 3)} for k, v in sorted(gruppi.items())}
    (CARTELLA / "lavoro" / "fase3_regime.json").write_text(json.dumps(esito, indent=1, ensure_ascii=False) + "\n",
                                                           encoding="utf-8")
    print(json.dumps(esito, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()
