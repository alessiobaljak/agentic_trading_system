"""Fase 0: scarico dei dati in-sample di SOLUSDT (e di BTCUSDT come riferimento di mercato).

Uso: python -m research.campagne.SOLUSDT.codice.scarica SIMBOLO TIPO INTERVALLO
Scarica solo i mesi da 2020-09 a 2023-12 (il caricatore rifiuta comunque ogni
data oltre il 2023-12-31 a vault chiuso). Stampa i mesi assenti e gli URL senza CHECKSUM.
"""
import sys
from datetime import date

from research.src import dati

simbolo, tipo, intervallo = sys.argv[1], sys.argv[2], sys.argv[3]
if intervallo == "-":
    intervallo = None
dati.azzera_checksum_mancanti()
percorsi = dati.scarica_periodo(simbolo, tipo, intervallo, date(2020, 9, 1), date(2023, 12, 31))
attesi = [(a, m) for a in range(2020, 2024) for m in range(1, 13) if (a, m) >= (2020, 9)]
presenti = {p.name for p in percorsi}
assenti = [f"{a}-{m:02d}" for a, m in attesi
           if dati.nome_file_mese(simbolo, tipo, intervallo, a, m) not in presenti]
print(f"{simbolo} {tipo} {intervallo}: {len(percorsi)} file, assenti={assenti}, checksum_mancanti={list(dati.CHECKSUM_MANCANTI)}")
