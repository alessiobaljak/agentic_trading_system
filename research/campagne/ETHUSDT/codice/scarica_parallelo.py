"""Come scarica.py, ma con piu' scarichi insieme (stessi file, stesso caricatore).

Usa ``dati.scarica_mese`` mese per mese (blocco del vault e CHECKSUM compresi),
solo per i mesi dal 2020-01 al 2023-12. Un file gia' su disco non si riscarica.
Scrive il riepilogo in research/data/insample/ETHUSDT/scarico_esito.txt.
"""

import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

RADICE_REPO = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(RADICE_REPO))

from research.src import dati  # noqa: E402

TIMEFRAME = ["15m", "30m", "1h", "2h", "4h", "6h", "8h", "12h", "1d"]
MESI = [(a, m) for a in range(2020, 2024) for m in range(1, 13)]
ESITO = RADICE_REPO / "research" / "data" / "insample" / "ETHUSDT" / "scarico_esito.txt"


def lavori():
    for tf in TIMEFRAME:
        for a, m in MESI:
            yield ("ETHUSDT", "klines", tf, a, m)
            yield ("ETHUSDT", "markPriceKlines", tf, a, m)
            yield ("BTCUSDT", "klines", tf, a, m)
    for a, m in MESI:
        yield ("ETHUSDT", "fundingRate", None, a, m)


def uno(lavoro):
    simbolo, tipo, tf, a, m = lavoro
    percorso = dati.scarica_mese(simbolo, tipo, tf, a, m)
    return lavoro, percorso is not None


def main() -> None:
    elenco = list(lavori())
    with ThreadPoolExecutor(max_workers=12) as pool:
        esiti = list(pool.map(uno, elenco))
    assenti = [l for l, ok in esiti if not ok]
    righe = [f"file richiesti: {len(elenco)}", f"presenti: {len(elenco) - len(assenti)}", f"assenti (404): {len(assenti)}"]
    righe += [f"  assente: {l}" for l in assenti]
    righe.append(f"CHECKSUM mancanti: {len(dati.CHECKSUM_MANCANTI)}")
    righe += [f"  {u}" for u in sorted(set(dati.CHECKSUM_MANCANTI))]
    ESITO.write_text("\n".join(righe) + "\n", encoding="utf-8")
    print("\n".join(righe[:3]))


if __name__ == "__main__":
    main()
