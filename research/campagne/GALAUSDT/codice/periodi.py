"""Stampa le date di costruzione e validazione di GALAUSDT (Fase 0, punto 1)."""

from datetime import date

from research.src.dati import periodi_campagna

if __name__ == "__main__":
    p = periodi_campagna(date(2021, 9, 1))
    for chiave, valore in p.items():
        print(chiave, valore)
