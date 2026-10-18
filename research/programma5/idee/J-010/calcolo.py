"""J-010 — Reti d'acquisto sotto il prezzo con uscita a mercato (monete fuori dalla fase 1) (scheda.md). Uso: PYTHONPATH=. python3 research/programma5/idee/J-010/calcolo.py C2|V2"""
import json
import sys
from pathlib import Path

from research.programma5.strumenti.fase2 import MONETE_F2
from research.programma5.strumenti.idee_fase2 import per_moneta_rete
from research.programma5.strumenti.idee_minuti import aggrega
from research.programma5.strumenti.rapporto import scrivi
from research.programma5.strumenti.scarico import MONETE as FASE1

QUI = Path(__file__).parent
CENTO = json.loads((QUI.parents[1] / "universo_top100.json").read_text())["scelte"]
VARIANTI = {"J-010a": {"tipo": "R", "lato": "acquisto", "k": 6, "H": 1440}, "J-010b": {"tipo": "R", "lato": "acquisto", "k": 3, "H": 60}, "J-010c": {"tipo": "R", "lato": "acquisto", "k": 3, "H": 1440}}

if __name__ == "__main__":
    periodo = sys.argv[1] if len(sys.argv) > 1 else "C2"
    monete = MONETE_F2 if periodo == "C2" else tuple(s for s in CENTO if s not in FASE1)
    aggrega("J-010", VARIANTI, periodo, QUI, per_moneta_rete, monete=monete)
    print(scrivi("J-010", periodo))
