"""Verifica di causalita' degli indicatori di tutte le varianti (o di quelle passate per nome)."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import quadro as q  # noqa: E402
import varianti  # noqa: E402

nomi = sys.argv[1:] or [n for n in varianti.VARIANTI if n != "CONTROLLO"]
for nome in nomi:
    v = varianti.VARIANTI[nome]
    serie = q.carica(v.tf, con_btc=v.con_btc)
    n = q.candele_costruzione(serie)
    serie.candele = serie.candele[:n]
    problemi = q.verifica_causalita(v, serie)
    print(json.dumps({"nome": nome, "causale": not problemi, "problemi": problemi[:5]}), flush=True)
