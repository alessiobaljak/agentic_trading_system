"""Cose comuni agli script della campagna FTMUSDT: percorsi, periodi, parametri del motore."""
from __future__ import annotations

import json
import sys
from datetime import date, datetime, timezone
from pathlib import Path

RADICE_REPO = Path(__file__).resolve().parents[4]
if str(RADICE_REPO) not in sys.path:
    sys.path.insert(0, str(RADICE_REPO))

from research.src import dati, motore  # noqa: E402

SIMBOLO = "FTMUSDT"
PRIMO_GIORNO = date(2020, 9, 1)  # scheda_moneta.md: primo mese di dati 2020-09
CARTELLA = RADICE_REPO / "research" / "campagne" / SIMBOLO
LOG = CARTELLA / "log.jsonl"
PERIODI = dati.periodi_campagna(PRIMO_GIORNO)

# Parametri del motore: config/parametri.yaml (congelati) e scheda_moneta.md (slippage).
PARAMETRI = motore.Parametri(
    commissione_per_lato=0.0005,
    slippage_per_lato=0.0005,
    rischio_per_trade=0.01,
    leva_max=2.0,
    modalita_margine="isolated",
    tasso_margine_mantenimento=0.025,
    margine_minimo_da_liquidazione=0.8,
    capitale_iniziale=1000.0,
    riempimento_intrabarra="stop_prima",
    moltiplicatore_costi=1.0,
    ritardo_barre=0,
)


def adesso() -> str:
    """Orologio della macchina in UTC (lo stesso di `date -u`), mai a memoria."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def aggiungi_log(voce: dict) -> dict:
    """Aggiunge UNA voce in fondo al log (solo in aggiunta), con la data presa dall'orologio."""
    voce = dict(voce)
    voce["data"] = adesso()
    ordinata = {"id": voce.pop("id"), "tipo": voce.pop("tipo")}
    ordinata["data"] = voce.pop("data")
    ordinata.update(voce)
    ordinata = _pulisci(ordinata)
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps(ordinata, ensure_ascii=False, default=_serializza, allow_nan=False) + "\n")
    return ordinata


def _pulisci(x):
    """JSON valido: infiniti e NaN diventano testo, numpy diventa Python, chiavi in testo."""
    import math
    try:
        import numpy as np
        if isinstance(x, np.generic):
            x = x.item()
        elif isinstance(x, np.ndarray):
            x = x.tolist()
    except ImportError:
        pass
    if isinstance(x, float):
        if math.isnan(x):
            return "nan"
        if math.isinf(x):
            return "inf" if x > 0 else "-inf"
        return round(x, 6)
    if isinstance(x, dict):
        return {str(k): _pulisci(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [_pulisci(v) for v in x]
    return x


def _serializza(x):
    try:
        import numpy as np
        if isinstance(x, np.generic):
            return x.item()
        if isinstance(x, np.ndarray):
            return x.tolist()
    except ImportError:
        pass
    if isinstance(x, float):
        return None
    return str(x)
