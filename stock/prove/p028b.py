"""Scarica l'archivio delle notizie per la prova 28 (`P028_tono_delle_notizie.md`). Non calcola niente e non guarda nessun prezzo.

    python -m stock.prove.p028b      # su GitHub (azioni-ricerca); riprende da dove era arrivato, si ferma dopo 4 ore
"""
from __future__ import annotations

from datetime import UTC, datetime

from stock.dati import notizie
from stock.prove.p001 import QUI


def main():
    restano = notizie.scarica(2016, 2024, minuti=240)
    fatti = len(notizie.mesi(2016, 2024)) - len(restano)
    (QUI / "P028b_risultati.md").write_text(
        f"# Prova 28 — lo scarico delle notizie\n\nAggiornato il {datetime.now(UTC):%Y-%m-%d %H:%M} UTC: mesi scaricati {fatti} su "
        f"{len(notizie.mesi(2016, 2024))}" + ("; **completo**.\n" if not restano else f"; restano {len(restano)} mesi: rilanciare.\n"))
    print(f"mesi scaricati {fatti}, restano {len(restano)}")


if __name__ == "__main__":
    main()
