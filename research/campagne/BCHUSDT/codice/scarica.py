"""Fase 0, punto 2: scarica i dati in-sample di BCHUSDT e il riferimento BTCUSDT.

BCHUSDT: candele last (klines) e mark (markPriceKlines) su tutti i timeframe
ammessi, e il funding, da 2020-01 a 2023-12 (primo mese della scheda; mai oltre il
2023-12-31: il caricatore lo rifiuta da solo). BTCUSDT: solo candele last su tutti
i timeframe ammessi (riferimento di mercato). I file si scaricano con
``scarica_periodo`` di src/dati.py, con il controllo del CHECKSUM remoto acceso.
Alla fine registra le impronte (SHA-256) dei file di BCHUSDT e di BTCUSDT in
``campagne/BCHUSDT/impronte.json`` e stampa i CHECKSUM mancanti.
"""
import json
from concurrent.futures import ThreadPoolExecutor
from datetime import date
from pathlib import Path

from research.src import dati

INIZIO = date(2020, 1, 1)
FINE = date(2023, 12, 31)
TIMEFRAME = ["15m", "30m", "1h", "2h", "4h", "6h", "8h", "12h", "1d"]
CARTELLA = Path(__file__).resolve().parent.parent


def lavori():
    for tf in TIMEFRAME:
        yield ("BCHUSDT", "klines", tf)
        yield ("BCHUSDT", "markPriceKlines", tf)
        yield ("BTCUSDT", "klines", tf)
    yield ("BCHUSDT", "fundingRate", None)


def esegui(lavoro):
    simbolo, tipo, tf = lavoro
    percorsi = dati.scarica_periodo(simbolo, tipo, tf, INIZIO, FINE)
    return simbolo, tipo, tf, len(percorsi)


def main():
    with ThreadPoolExecutor(max_workers=8) as pool:
        for simbolo, tipo, tf, n in pool.map(esegui, list(lavori())):
            print(simbolo, tipo, tf, "file:", n, flush=True)
    impronte = {
        "BCHUSDT": dati.calcola_impronte("BCHUSDT"),
        "BTCUSDT": dati.calcola_impronte("BTCUSDT"),
    }
    (CARTELLA / "impronte.json").write_text(json.dumps(impronte, indent=1, sort_keys=True), encoding="utf-8")
    print("impronte:", {k: len(v) for k, v in impronte.items()})
    print("checksum mancanti:", len(dati.CHECKSUM_MANCANTI))
    for url in dati.CHECKSUM_MANCANTI:
        print("  ", url)


if __name__ == "__main__":
    main()
