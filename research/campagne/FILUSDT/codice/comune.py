"""Cose comuni della campagna FILUSDT: percorsi, parametri del motore, periodi.

Parametri da config/parametri.yaml e dalla scheda della moneta (sezione 7 del protocollo):
commissione 0,05% per lato, slippage 0,02% per lato (fascia del 2023, scheda), rischio 1%,
leva massima 2, margine isolato, mantenimento 0,025, margine minimo dalla liquidazione 0,8,
capitale 1000, stop prima del target nella stessa barra.
"""
from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

RADICE_REPO = Path(__file__).resolve().parents[4]
if str(RADICE_REPO) not in sys.path:
    sys.path.insert(0, str(RADICE_REPO))

from research.src.motore import Parametri  # noqa: E402
from research.src.dati import periodi_campagna  # noqa: E402

SIMBOLO = "FILUSDT"
PRIMO_GIORNO = date(2020, 10, 1)  # scheda_moneta.md
CARTELLA_CAMPAGNA = RADICE_REPO / "research" / "campagne" / SIMBOLO
CARTELLA_DATI = RADICE_REPO / "research" / "data" / "insample" / SIMBOLO
PERIODI = periodi_campagna(PRIMO_GIORNO)

TIMEFRAME = ["15m", "30m", "1h", "2h", "4h", "6h", "8h", "12h", "1d"]


def parametri(moltiplicatore_costi: float = 1.0, ritardo_barre: int = 0,
              riempimento: str = "stop_prima") -> Parametri:
    return Parametri(
        commissione_per_lato=0.0005,
        slippage_per_lato=0.0002,
        rischio_per_trade=0.01,
        leva_max=2.0,
        modalita_margine="isolated",
        tasso_margine_mantenimento=0.025,
        margine_minimo_da_liquidazione=0.8,
        capitale_iniziale=1000.0,
        riempimento_intrabarra=riempimento,
        moltiplicatore_costi=moltiplicatore_costi,
        ritardo_barre=ritardo_barre,
    )


if __name__ == "__main__":
    for chiave, valore in PERIODI.items():
        print(chiave, valore)
