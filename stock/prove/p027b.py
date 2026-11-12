"""La prova 27 rifatta con i prezzi corretti (il simbolo di allora): correzione dei dati del 12 novembre 2026, non una prova nuova.

    python -m stock.prove.p027b      # su GitHub (azioni-ricerca); scrive P027b_risultati.md

L'elenco degli acquisti è `dati/P027b_acquisti.csv.gz` (`p027_acquisti.py --allora`: fuori dall'indice secondo i simboli di allora).
"""
from stock.prove import p027

if __name__ == "__main__":
    p027.main(allora=True)
