"""Fase 0, punto 1: date di costruzione e validazione con periodi_campagna, scritte nel log PRIMA dei prezzi."""
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from research.src.dati import periodi_campagna  # noqa: E402
import registro  # noqa: E402

p = periodi_campagna(date(2021, 9, 1))
voce = {
    "id": "DYDXUSDT-N001",
    "tipo": "nota",
    "argomento": "Fase 0 punto 1: periodi della campagna, calcolati prima di caricare i prezzi",
    "fonte": "scheda_moneta.md (primo mese di dati 2021-09-01) e periodi_campagna di research/src/dati.py",
    "periodi": {k: (v.isoformat() if isinstance(v, date) else v) for k, v in p.items()},
    "commento": "La campagna e' aperta dal coordinamento su delega (protocollo 4.5, approvato 2026-10-09 12:06 UTC). "
                "Branch research/campagna/DYDXUSDT creato dal principale (il riferimento remoto non esisteva). "
                "Test del guardiano: 693 passati. Un rifiuto del guardiano alle 17:2x UTC: il comando "
                "'cd .../research && cat ...' e' stato rifiutato perche' la cartella research/ in se' non e' fra i percorsi "
                "ammessi; i file richiesti (scheda, parametri) sono stati poi letti con percorsi ammessi. Registrato qui.",
}
print(registro.aggiungi(voce))
