"""Aggiunge al log una voce `nota` con il testo di data/insample/XRPUSDT/nota.json.

Il file contiene un oggetto JSON con almeno "testo" (e campi facoltativi, es. pausa_da/pausa_a).
L'id e' progressivo (XRPUSDT-Nnnn), la data e' l'orologio della macchina.
"""
import json

from research.src import dati
from research.campagne.XRPUSDT.codice import quadro

f = dati.RADICE_DEFAULT / "data" / "insample" / "XRPUSDT" / "nota.json"
voce = json.loads(f.read_text(encoding="utf-8"))
n = [int(v["id"].split("-N")[1]) for v in quadro.leggi_log() if "-N" in v.get("id", "")]
voce = {"id": f"XRPUSDT-N{(max(n) if n else 0) + 1:03d}", "tipo": voce.pop("tipo", "nota"), "data": quadro.adesso(), **voce}
quadro.scrivi_log(voce)
f.unlink()
print(voce["id"], voce["data"])
