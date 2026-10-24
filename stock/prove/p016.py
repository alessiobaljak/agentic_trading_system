"""Calcolo della prova 16 (`P016_ampiezza.md`): regole lì, scritte prima.

    python -m stock.prove.p016     # scrive stock/prove/P016_risultati.md
"""
from datetime import date

from stock.dati import alpaca
from stock.prove.p005 import esegui
from stock.prove.p011 import carica_tutti, membri_dell_indice
from stock.strategie import ampiezza as amp

if __name__ == "__main__":
    membri, simboli = membri_dell_indice()
    _, rett, _ = carica_tutti(simboli, date(2024, 12, 31))
    cal = list(alpaca.calendario("2016-01-01", "2024-12-31").index)
    serie = amp.serie_ampiezza(rett, membri, cal)
    print(f"ampiezza: {len(serie)} giorni, sotto il 50% nel {float((serie < 0.5).mean()):.0%} dei giorni", flush=True)
    esegui("16", "P016_ampiezza.md", lambda s, c, r: amp.strategia(s, c, serie),
           lambda r, esecuzioni: esecuzioni["giorno"].min())
