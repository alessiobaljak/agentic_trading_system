"""Impronte dei dati della campagna BTC51 (sezione 12 del protocollo).

Senza argomenti: aggiunge in fondo a fase0_dati.md la tabella delle impronte SHA-256 dei file in
data/insample/BTCUSDT (solo se non c'e' gia').
Con ``verifica``: riscarica i file mancanti e confronta le impronte con quelle di fase0_dati.md;
scrive l'esito in data/insample/BTCUSDT/verifica_impronte.txt («IMPRONTE UGUALI» o le differenze).
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

RADICE_REPO = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(RADICE_REPO))

from research.src import dati  # noqa: E402

FASE0 = Path(__file__).resolve().parent.parent / "fase0_dati.md"
TITOLO = "### Elenco delle impronte"
ESITO = dati.RADICE_DEFAULT / "data" / "insample" / "BTCUSDT" / "verifica_impronte.txt"


def leggi_impronte() -> dict:
    testo = FASE0.read_text(encoding="utf-8")
    parte = testo.split(TITOLO, 1)[1]
    return dict(re.findall(r"^\| `([^`]+)` \| `([0-9a-f]{64})` \|$", parte, flags=re.M))


def scrivi() -> None:
    testo = FASE0.read_text(encoding="utf-8")
    if TITOLO in testo:
        raise SystemExit("impronte gia' presenti in fase0_dati.md")
    impronte = dati.registra_impronte("BTCUSDT")
    righe = ["", TITOLO, "", f"{len(impronte)} file, percorsi relativi a `research/data/insample/BTCUSDT/`.", "",
             "| File | SHA-256 |", "|---|---|"]
    righe += [f"| `{nome}` | `{h}` |" for nome, h in impronte.items()]
    with open(FASE0, "a", encoding="utf-8") as f:
        f.write("\n".join(righe) + "\n")
    print("ok", len(impronte))


def verifica() -> None:
    from datetime import date
    attese = leggi_impronte()
    for tipo in ("klines", "markPriceKlines"):
        for tf in ("15m", "30m", "1h", "2h", "4h", "6h", "8h", "12h", "1d"):
            dati.scarica_periodo("BTCUSDT", tipo, tf, date(2020, 1, 1), date(2023, 12, 31))
    dati.scarica_periodo("BTCUSDT", "fundingRate", None, date(2020, 1, 1), date(2023, 12, 31))
    differenze = dati.verifica_impronte("BTCUSDT", dati.RADICE_DEFAULT, attese)
    esito = "IMPRONTE UGUALI" if not differenze else "IMPRONTE DIVERSE\n" + "\n".join(differenze)
    ESITO.write_text(f"{len(attese)} file attesi\n{esito}\n", encoding="utf-8")
    print(esito.splitlines()[0])


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "verifica":
        verifica()
    else:
        scrivi()
