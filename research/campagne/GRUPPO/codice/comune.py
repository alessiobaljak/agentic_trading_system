"""Funzioni comuni agli script di lavoro della campagna di gruppo (non e' codice di variante).

Legge l'elenco ufficiale ``monete.csv`` e le schede; nessun calcolo d'esame.
"""
import csv
import json
import re
import sys
from pathlib import Path

RADICE_PROGETTO = Path(__file__).resolve().parents[4]
if str(RADICE_PROGETTO) not in sys.path:
    sys.path.insert(0, str(RADICE_PROGETTO))

from research.src import dati  # noqa: E402

CARTELLA_GRUPPO = RADICE_PROGETTO / "research" / "campagne" / "GRUPPO"
RADICE_RICERCA = RADICE_PROGETTO / "research"
LOG = CARTELLA_GRUPPO / "log.jsonl"


def monete():
    """I simboli di monete.csv, nell'ordine del file (j = posizione)."""
    with open(CARTELLA_GRUPPO / "monete.csv", encoding="utf-8", newline="") as flusso:
        righe = list(csv.DictReader(flusso))
    return [r["simbolo"] for r in righe]


def schede():
    """{simbolo: scheda letta da dati.leggi_scheda_gruppo}, in ordine di monete.csv."""
    return {s: dati.leggi_scheda_gruppo(s) for s in monete()}


def periodi():
    """dati.periodi_gruppo sui primi mesi delle schede."""
    return dati.periodi_gruppo({s: v["primo_mese"] for s, v in schede().items()})


def prossimo_id():
    """Il prossimo id GRUPPO-NNN del log (il piu' alto + 1)."""
    numeri = [0]
    for riga in LOG.read_text(encoding="utf-8").splitlines():
        if riga.strip():
            m = re.fullmatch(r"GRUPPO-(\d+)", json.loads(riga)["id"])
            if m:
                numeri.append(int(m.group(1)))
    return f"GRUPPO-{max(numeri) + 1:03d}"


def aggiungi_al_log(voce):
    """Aggiunge una voce in coda al log (solo in aggiunta). ``data`` deve venire da date -u."""
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z", str(voce.get("data", ""))):
        raise ValueError("data mancante o non nel formato di date -u")
    with open(LOG, "a", encoding="utf-8") as flusso:
        flusso.write(json.dumps(voce, ensure_ascii=False) + "\n")
