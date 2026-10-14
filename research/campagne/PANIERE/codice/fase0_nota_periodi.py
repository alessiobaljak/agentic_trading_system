"""Scrive nel log la nota dei periodi (regole del gruppo, sezione 2, punto 1), da lavoro/fase0_periodi.json, prima di caricare un prezzo."""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import registro  # noqa: E402

CARTELLA = Path(__file__).resolve().parents[1]


def main():
    p = json.loads((CARTELLA / "lavoro" / "fase0_periodi.json").read_text(encoding="utf-8"))
    voce = registro.aggiungi({
        "tipo": "nota",
        "testo": (
            "Fase 0, punto 1 (regole del gruppo, sezione 2, punto 1): periodi calcolati con dati.periodi_gruppo "
            "sui primi mesi delle 80 schede del paniere, prima di caricare qualunque prezzo. Taglio comune: "
            "costruzione fino al 2023-01-16 compreso (fine_costruzione_ts 2023-01-16 23:59:59.999 UTC), "
            "validazione dal 2023-01-17 al 2023-12-31 per tutte le monete. Per ogni moneta l'inizio della "
            "costruzione è il primo giorno del primo mese della scheda (campo inizio_costruzione). Dettaglio "
            "completo in lavoro/fase0_periodi.json."
        ),
        "fine_costruzione": p["fine_costruzione"],
        "inizio_validazione": p["inizio_validazione"],
        "fine_validazione": p["fine_validazione"],
        "giorni_validazione": p["giorni_validazione"],
        "giorni_moneta": p["giorni_moneta"],
        "giorni_moneta_obiettivo": p["giorni_moneta_obiettivo"],
        "giorni_moneta_costruzione": p["giorni_moneta_costruzione"],
        "inizio_costruzione": {s: v["inizio_costruzione"] for s, v in p["monete"].items()},
        "giorni_costruzione": {s: v["giorni_costruzione"] for s, v in p["monete"].items()},
    })
    print(voce["id"], voce["data"])


if __name__ == "__main__":
    main()
