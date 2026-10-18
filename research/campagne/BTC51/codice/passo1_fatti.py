"""Passo 1, punti 2-3: impronte dei file e fatti per fase0_dati.md.

* impronte SHA-256 di tutti i file scaricati (dati.registra_impronte);
* conteggi di costruzione e validazione, buchi, volume 2023, intervalli di funding (dati.fatti_passo1_3:
  della validazione escono solo conteggi, nessun prezzo);
* solo sulla costruzione (fino al 2022-09-30): barre tolte dall'allineamento last/mark per timeframe,
  orari dei regolamenti di funding fuori da 00/08/16 UTC, e le candele anomale (le piu' grandi per
  escursione e per variazione, su 1h e 1d), da tenere e segnalare.

Esito in data/insample/BTCUSDT/passo1_fatti.json (fuori da git); la sessione lo riporta in fase0_dati.md.
"""

from __future__ import annotations

import json
import sys
from collections import Counter
from datetime import date, datetime, timezone
from pathlib import Path

RADICE_REPO = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(RADICE_REPO))

from research.src import dati  # noqa: E402

SIMBOLO = "BTCUSDT"
TIMEFRAME = ("15m", "30m", "1h", "2h", "4h", "6h", "8h", "12h", "1d")
INIZIO = date(2020, 1, 1)
FINE_COSTR = date(2022, 9, 30)
USCITA = dati.RADICE_DEFAULT / "data" / "insample" / SIMBOLO / "passo1_fatti.json"


def iso(ms: int) -> str:
    return datetime.fromtimestamp(ms / 1000, tz=timezone.utc).strftime("%Y-%m-%d %H:%M")


def main() -> None:
    impronte = dati.registra_impronte(SIMBOLO)
    fatti = dati.fatti_passo1_3(SIMBOLO)

    allineamento = {}
    for tf in TIMEFRAME:
        al = dati.carica_serie_allineate(SIMBOLO, tf, INIZIO, FINE_COSTR)
        allineamento[tf] = {
            "tenute": len(al["candele"]),
            "tolte_last": [iso(t) for t in al["tolte_last"]][:50],
            "n_tolte_last": al["n_tolte_last"],
            "tolte_mark": [iso(t) for t in al["tolte_mark"]][:50],
            "n_tolte_mark": al["n_tolte_mark"],
            "n_volume_mancante": al["n_volume_mancante"],
        }

    funding = dati.carica_funding_dettaglio(SIMBOLO, INIZIO, FINE_COSTR)
    ore = Counter(datetime.fromtimestamp(t / 1000, tz=timezone.utc).strftime("%H:%M:%S") for t, _, _ in funding)
    passi = Counter((b[0] - a[0]) // 3_600_000 for a, b in zip(funding[:-1], funding[1:]))
    ore_dichiarate = Counter(o for _, o, _ in funding)

    anomale = {}
    for tf in ("1h", "1d"):
        cc = dati.carica_candele(SIMBOLO, tf, INIZIO, FINE_COSTR)
        righe = []
        for prec, c in zip(cc[:-1], cc[1:]):
            righe.append({
                "ora": iso(c.ts),
                "escursione_pct": round(100 * (c.high - c.low) / c.open, 2),
                "variazione_pct": round(100 * (c.close - prec.close) / prec.close, 2),
                "salto_apertura_pct": round(100 * (c.open - prec.close) / prec.close, 2),
            })
        anomale[tf] = {
            "per_escursione": sorted(righe, key=lambda r: -r["escursione_pct"])[:10],
            "per_variazione": sorted(righe, key=lambda r: -abs(r["variazione_pct"]))[:10],
            "salti_apertura_oltre_1pct": [r for r in righe if abs(r["salto_apertura_pct"]) > 1.0],
        }

    out = {
        "n_file": len(impronte),
        "impronte": impronte,
        "fatti_passo1_3": fatti,
        "allineamento_costruzione": allineamento,
        "funding_costruzione": {
            "regolamenti": len(funding),
            "orari_utc": dict(ore),
            "distanze_ore": {str(k): v for k, v in passi.items()},
            "ore_dichiarate_nel_file": {str(k): v for k, v in ore_dichiarate.items()},
            "primo": iso(funding[0][0]) if funding else None,
        },
        "candele_anomale_costruzione": anomale,
    }
    USCITA.write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print("ok")


if __name__ == "__main__":
    main()
