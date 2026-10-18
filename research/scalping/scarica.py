"""Scalping sulla volatilita': scarico delle candele da 1 minuto (regole in research/scalping/regole.md).

Usa il caricatore della ricerca (research/src/dati.py) con il controllo del CHECKSUM; scrive le impronte in
research/scalping/scarico.json. Solo 2020-2022: il 2023 resta per la validazione.
"""
from __future__ import annotations

import json
from datetime import date
from pathlib import Path

from research.src import dati

MONETE = ("BTCUSDT", "ETHUSDT", "SOLUSDT", "XRPUSDT", "BNBUSDT", "DOGEUSDT")
INIZIO, FINE = date(2020, 1, 1), date(2022, 12, 31)


def main() -> int:
    out = {}
    for s in MONETE:
        percorsi = dati.scarica_periodo(s, "klines", "1m", INIZIO, FINE, verifica_checksum=True)
        out[s] = {p.name: dati.impronta_bytes(p.read_bytes()) for p in percorsi}
        print(f"[scarico] {s}: {len(percorsi)} mesi", flush=True)
    out["_checksum_mancanti"] = sorted(getattr(dati, "CHECKSUM_MANCANTI", []) or [])
    Path(__file__).with_name("scarico.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
