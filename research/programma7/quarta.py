"""Programma 7, quarta prova (QUARTA.md): G3, il long in giornata delle monete con il funding dei 7 giorni piu' basso, lo
specchio di G2 (`seconda.py`).

Uso: python3 -m research.programma7.quarta
"""
from __future__ import annotations

from research.programma7 import seconda as g2

RIS = g2.QUI / "risultati_quarta"


def esegui(log=print) -> dict:
    return g2.esegui(log=log, verso=1, nome="G3", numero="60", ris=RIS, file_risultati="RISULTATI_QUARTA.md",
                     titolo="quarta prova (G3: long in giornata sul funding più basso)", regole="QUARTA.md")


if __name__ == "__main__":
    esegui(log=lambda x: print(x, flush=True))
    print("QUARTA FINITA", flush=True)
