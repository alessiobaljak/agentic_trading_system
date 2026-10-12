"""Aggiunge una nota al log, col testo letto da data/insample/FTMUSDT/nota.txt. Uso: python nota.py ID"""
import sys

from comune import RADICE_REPO, SIMBOLO, aggiungi_log

testo = (RADICE_REPO / "research" / "data" / "insample" / SIMBOLO / "nota.txt").read_text(encoding="utf-8").strip()
print(aggiungi_log({"id": sys.argv[1], "tipo": "nota", "testo": testo}))
