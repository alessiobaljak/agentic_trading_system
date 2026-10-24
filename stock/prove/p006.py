"""Calcolo della prova 6 (`P006_cambio_del_mese.md`): regole lì, scritte prima.

    python -m stock.prove.p006     # scrive stock/prove/P006_risultati.md
"""
from stock.prove.p005 import esegui
from stock.strategie.calendario import strategia_cambio_del_mese

if __name__ == "__main__":
    esegui("6", "P006_cambio_del_mese.md", lambda s, cal, rett: strategia_cambio_del_mese(s, cal),
           lambda rett, esecuzioni: esecuzioni["giorno"].min())
