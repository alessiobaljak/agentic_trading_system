"""Strumenti comuni della campagna BTCUSDT: parametri, dati, log.

Niente strategie qui: solo cio' che serve a tutte le varianti. I parametri del
motore vengono da research/config/parametri.yaml e dalla scheda della moneta
(sezione 7 del protocollo), non dai valori d'esempio di ``Parametri``.
"""
from __future__ import annotations

import json
import sys
from datetime import date, datetime, timezone
from pathlib import Path

RADICE_REPO = Path(__file__).resolve().parents[4]
if str(RADICE_REPO) not in sys.path:
    sys.path.insert(0, str(RADICE_REPO))

from research.src import dati, motore  # noqa: E402

SIMBOLO = "BTCUSDT"
CARTELLA = RADICE_REPO / "research" / "campagne" / SIMBOLO
LOG = CARTELLA / "log.jsonl"
PRIMO_GIORNO = date(2020, 1, 1)  # scheda_moneta.md
SLIPPAGE = 0.0001  # scheda_moneta.md: fascia 0,01% per lato
PERIODI = dati.periodi_campagna(PRIMO_GIORNO)

TIMEFRAME = ["15m", "30m", "1h", "2h", "4h", "6h", "8h", "12h", "1d"]


def parametri(**cambi) -> motore.Parametri:
    """I parametri del motore da parametri.yaml (congelati) e dalla scheda."""
    base = dict(
        commissione_per_lato=0.0005,
        slippage_per_lato=SLIPPAGE,
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
    base.update(cambi)
    return motore.Parametri(**base)


def adesso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def voci_log() -> list:
    if not LOG.is_file():
        return []
    return [json.loads(r) for r in LOG.read_text(encoding="utf-8").splitlines() if r.strip()]


def aggiungi_log(voce: dict) -> dict:
    """Aggiunge una voce in fondo al log (solo in aggiunta, mai riscrivere)."""
    voce = dict(voce)
    voce.setdefault("data", adesso())
    riga = json.dumps(voce, ensure_ascii=False, sort_keys=False, default=_json_default)
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(riga + "\n")
    return voce


def _json_default(x):
    if isinstance(x, (date, datetime)):
        return x.isoformat()
    try:
        import numpy as np
        if isinstance(x, np.generic):
            return x.item()
        if isinstance(x, np.ndarray):
            return x.tolist()
    except ImportError:
        pass
    if x == float("inf"):
        return "inf"
    raise TypeError(f"non serializzabile: {type(x)}")
