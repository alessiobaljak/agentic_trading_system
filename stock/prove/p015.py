"""Calcolo della prova 15 (`P015_calma_e_agitazione.md`): regole lì, scritte prima.

    python -m stock.prove.p015     # scrive stock/prove/P015_risultati.md
"""
from stock.prove.p005 import esegui
from stock.strategie.tendenza import strategia_calma

if __name__ == "__main__":
    esegui("15", "P015_calma_e_agitazione.md", lambda s, cal, rett: strategia_calma(s, cal, rett),
           lambda rett, esecuzioni: esecuzioni["giorno"].min(), leva_massima=1.5, interesse=0.06)
