"""Stima dei trade (sezione 8) per le varianti elencate: conta i segnali sui dati di costruzione."""
import json
import sys

from research.campagne.SOLUSDT.codice import campagna as cp
from research.campagne.SOLUSDT.codice import strategie as st
from research.campagne.SOLUSDT.codice.varianti import VARIANTI, regola

nomi = sys.argv[1:] or list(VARIANTI)
out = {}
for nome in nomi:
    idea, tf, direzione, costruttore, durata = VARIANTI[nome]
    r = regola(nome)
    s = cp.stima_trade(st.fabbrica(r, direzione), tf, cp.COSTRUZIONE, durata)
    out[nome] = s
    print(nome, json.dumps(s))
