"""Conta i trade (conta_trade, una volta sola) delle varianti passate per nome, in serie."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import quadro as q  # noqa: E402
import varianti  # noqa: E402

CONTEGGI = q.CARTELLA_DATI / "risultati" / "conteggi.json"
CONTEGGI.parent.mkdir(parents=True, exist_ok=True)
for nome in sys.argv[1:]:
    fatti = json.loads(CONTEGGI.read_text()) if CONTEGGI.is_file() else {}
    if nome in fatti:
        print(nome, "GIA' CONTATA:", json.dumps(fatti[nome]), flush=True)
        continue
    c = q.conta(varianti.VARIANTI[nome])
    fatti[nome] = c
    CONTEGGI.write_text(json.dumps(fatti, indent=1))
    print(json.dumps({"nome": nome, **c}), flush=True)
