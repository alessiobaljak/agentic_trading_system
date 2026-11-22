"""Prova 167 (CENTOCINQUESIMA.md). Passo 1: costruisce l'elenco degli eventi (centocinquesima_dati.costruisci, senza prezzi).
Se gli eventi sono meno di 40: esito «campione troppo piccolo», nessun prezzo caricato, nessun rendimento, prova fuori dal conto.
Il passo 2 (prezzi, varianti A e B, esame con asticella.corretto_famiglie) NON e' implementato: non e' stato eseguito perche' il
passo 1 ha dato meno di 40 eventi. Se le regole cambiano, il passo 2 va scritto sul modello della prova 163.

Uso: python3 -m research.programma7.centocinquesima
"""
from __future__ import annotations

import json

from research.programma7.centocinquesima_dati import costruisci

SOGLIA = 40


def main() -> None:
    r = costruisci()
    n = r["rapporto"]["eventi"]
    if n < SOGLIA:
        print(json.dumps({"esito": "campione troppo piccolo", "eventi": n, "soglia": SOGLIA, "conti": r["rapporto"]["conti"]}, ensure_ascii=False))
        return
    raise SystemExit(f"{n} eventi: il passo 2 non e' implementato in questo file")


if __name__ == "__main__":
    main()
