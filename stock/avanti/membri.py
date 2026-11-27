"""I membri di oggi dell'S&P 500 per il demo (`sp500_membri.csv`: l'elenco del mese della prima candela e l'ampiezza della miscela).

Audit del 27 novembre 2026 (`stock/AUDIT_2026-11-27.md`, sezione 3): il file era fermo ai membri del 30 settembre e nessun programma lo
aggiornava. Da qui si aggiorna ogni mese, prima del primo giorno di borsa del mese, da una fonte scritta (l'elenco pubblico di Wikipedia,
che riporta i comunicati di S&P Dow Jones Indices); solo simboli, informazione pubblica. Se la lettura non torna (meno di 490 o più di
510 simboli, o simboli strani) il file non si tocca.

    python -m stock.avanti.membri          # aggiorna sp500_membri.csv e sp500_membri_fonte.json, e stampa le differenze
"""
from __future__ import annotations

import io
import json
import re
from datetime import UTC, datetime
from pathlib import Path

import pandas as pd
import requests

QUI = Path(__file__).resolve().parent
FILE = QUI / "sp500_membri.csv"
FONTE = QUI / "sp500_membri_fonte.json"
URL = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
SIMBOLO = re.compile(r"^[A-Z]{1,5}(\.[A-Z])?$")
GIORNI_DI_VALIDITA = 45


def dalla_pagina(html: str) -> list[str]:
    """I simboli della prima tabella della pagina (colonna «Symbol»), nella forma di Alpaca (BRK.B con il punto)."""
    tabelle = pd.read_html(io.StringIO(html), keep_default_na=False)      # una cella vuota non diventa «NAN»
    t = next(x for x in tabelle if "Symbol" in x.columns)
    simboli = sorted({str(s).strip().upper().replace("-", ".") for s in t["Symbol"] if str(s).strip()})
    strani = [s for s in simboli if not SIMBOLO.match(s)]
    if strani or not 490 <= len(simboli) <= 510:
        raise ValueError(f"lettura che non torna: {len(simboli)} simboli, strani {strani[:5]}")
    return simboli


def eta_in_giorni(adesso: datetime | None = None) -> float | None:
    """Da quanti giorni l'elenco non si aggiorna (None se non si sa)."""
    if not FONTE.exists():
        return None
    letto = datetime.fromisoformat(json.loads(FONTE.read_text())["letto_il"])
    return ((adesso or datetime.now(UTC)) - letto).total_seconds() / 86400


def aggiorna() -> str:
    r = requests.get(URL, headers={"User-Agent": "Mozilla/5.0 (ricerca)"}, timeout=30)
    r.raise_for_status()
    nuovi = dalla_pagina(r.text)
    vecchi = pd.read_csv(FILE)["simbolo"].tolist() if FILE.exists() else []
    entrati, usciti = sorted(set(nuovi) - set(vecchi)), sorted(set(vecchi) - set(nuovi))
    pd.DataFrame({"simbolo": nuovi}).to_csv(FILE, index=False)
    FONTE.write_text(json.dumps({"fonte": URL, "letto_il": datetime.now(UTC).isoformat(timespec="seconds"), "simboli": len(nuovi),
                                 "entrati": entrati, "usciti": usciti}, indent=1, ensure_ascii=False))
    return f"membri dell'S&P 500: {len(nuovi)} (entrati {', '.join(entrati) or 'nessuno'}; usciti {', '.join(usciti) or 'nessuno'})"


if __name__ == "__main__":
    print(aggiorna())
