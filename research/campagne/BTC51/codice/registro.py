"""Scrittura del log della campagna BTC51 (research/campagne/BTC51/log.jsonl), solo in aggiunta.

Ogni voce prende l'orario dall'orologio della macchina. Le voci con un ``id`` si
controllano: una ``registrazione`` con un id gia' registrato, o un ``risultato``
senza la sua registrazione, o un secondo ``risultato`` per lo stesso id, alzano
un errore invece di scrivere.

Uso da riga di comando (voce ``nota`` libera):
    python3 research/campagne/BTC51/codice/registro.py "testo della nota"
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List

CARTELLA = Path(__file__).resolve().parent.parent
LOG = CARTELLA / "log.jsonl"


def adesso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def voci() -> List[Dict]:
    if not LOG.is_file():
        return []
    righe = [r for r in LOG.read_text(encoding="utf-8").splitlines() if r.strip()]
    return [json.loads(r) for r in righe]


def aggiungi(voce: Dict) -> Dict:
    voce = dict(voce)
    voce.setdefault("data", adesso())
    esistenti = voci()
    vid = voce.get("id")
    tipo = voce.get("tipo")
    if vid is not None and tipo in ("registrazione", "risultato"):
        registrate = {v.get("id") for v in esistenti if v.get("tipo") == "registrazione"}
        con_risultato = {v.get("id") for v in esistenti if v.get("tipo") == "risultato"}
        if tipo == "registrazione" and vid in registrate:
            raise ValueError(f"id {vid} gia' registrato")
        if tipo == "risultato" and vid not in registrate:
            raise ValueError(f"risultato per {vid} senza registrazione")
        if tipo == "risultato" and vid in con_risultato:
            raise ValueError(f"risultato per {vid} gia' scritto")
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps(voce, ensure_ascii=False) + "\n")
    return voce


def prossimo_id(prefisso: str) -> str:
    """Il primo id libero della forma <prefisso>-NNN (es. V-001)."""
    usati = set()
    for v in voci():
        vid = str(v.get("id", ""))
        if vid.startswith(prefisso + "-") and vid[len(prefisso) + 1:].isdigit():
            usati.add(int(vid[len(prefisso) + 1:]))
    n = 1
    while n in usati:
        n += 1
    return f"{prefisso}-{n:03d}"


#: Il testo di una nota da riga di comando si scrive qui (il guardiano non accetta testi lunghi
#: come argomento), poi si lancia lo script senza argomenti: la nota entra nel log e il file si svuota.
NOTA_IN_ATTESA = CARTELLA / "codice" / "nota_in_attesa.txt"

if __name__ == "__main__":
    testo = NOTA_IN_ATTESA.read_text(encoding="utf-8").strip() if NOTA_IN_ATTESA.is_file() else ""
    if not testo:
        raise SystemExit(f"nessuna nota in {NOTA_IN_ATTESA}")
    print(json.dumps(aggiungi({"tipo": "nota", "testo": testo}), ensure_ascii=False))
    NOTA_IN_ATTESA.write_text("", encoding="utf-8")
