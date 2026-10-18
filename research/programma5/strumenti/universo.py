"""Programma 5, fase 2: la scelta meccanica delle 12 monete nuove (REGOLE.md, sezione 7).

Fra i perpetui USDT-M dell'archivio di Binance con le candele da 1 minuto mensili da settembre 2023 o prima e un file
giornaliero di ottobre 2026, esclusi le 12 del programma e le monete stabili, le 12 con il volume in USDT piu' alto nel
settembre 2026 (somma della colonna quote_volume delle candele giornaliere del mese). Scrive ``universo_fase2.json``.

Uso: python3 -m research.programma5.strumenti.universo [top100]
"""
from __future__ import annotations

import io
import json
import re
import zipfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from research.programma5.strumenti.scarico import ELENCO, MONETE, _leggi, _prendi, elenca

QUI = Path(__file__).resolve().parents[1]
STABILI = ("USDC", "FDUSD", "TUSD", "BUSD", "USDP", "DAI")
BASE = "https://data.binance.vision/"


def simboli() -> list:
    out, marker = [], ""
    while True:
        url = (f"{ELENCO}?prefix=data/futures/um/monthly/klines/&delimiter=/&max-keys=1000"
               + (f"&marker={marker}" if marker else ""))
        testo = _leggi(url)
        trovati = re.findall(r"<Prefix>data/futures/um/monthly/klines/([^<]+)/</Prefix>", testo)
        out += trovati
        if "<IsTruncated>true</IsTruncated>" not in testo or not trovati:
            return sorted(set(out))
        marker = re.findall(r"<NextMarker>([^<]+)</NextMarker>", testo)
        marker = marker[0] if marker else f"data/futures/um/monthly/klines/{trovati[-1]}/"


def esame(s: str, ultimo_primo_mese: str = "2023-09", escludi=MONETE):
    if not s.endswith("USDT") or s in escludi or any(s.startswith(x) for x in STABILI):
        return None
    if not re.fullmatch(r"[A-Z0-9]+USDT", s):
        return None
    mensili = elenca(f"data/futures/um/monthly/klines/{s}/1m/")
    mesi = sorted(re.search(r"-(\d{4}-\d{2})\.zip$", k).group(1) for k in mensili)
    if not mesi or mesi[0] > ultimo_primo_mese:
        return None
    if not elenca(f"data/futures/um/daily/klines/{s}/1d/{s}-1d-2026-10-"):
        return None
    contenuto = _prendi(f"{BASE}data/futures/um/monthly/klines/{s}/1d/{s}-1d-2026-09.zip")
    if contenuto is None:
        return None
    with zipfile.ZipFile(io.BytesIO(contenuto)) as z:
        righe = z.read(z.namelist()[0]).decode().strip().splitlines()
    volume = 0.0
    for r in righe:
        campi = r.split(",")
        if campi[0].isdigit():
            volume += float(campi[7])
    return {"simbolo": s, "primo_mese": mesi[0], "volume_settembre_2026": volume}


def main_top100() -> int:
    """REGOLE.md, sezione 7bis: le 100 con il volume piu' alto del settembre 2026, quotate entro febbraio 2025."""
    tutti = simboli()
    with ThreadPoolExecutor(max_workers=8) as ex:
        esiti = [e for e in ex.map(lambda s: esame(s, "2025-02", ()), tutti) if e]
    esiti.sort(key=lambda e: -e["volume_settembre_2026"])
    scelte = [e["simbolo"] for e in esiti[:100]]
    (QUI / "universo_top100.json").write_text(json.dumps({"simboli_guardati": len(tutti), "ammessi": esiti,
                                                          "scelte": scelte}, indent=1), encoding="utf-8")
    print(len(tutti), "simboli;", len(esiti), "ammessi; le 12 del programma dentro:",
          sum(1 for s in MONETE if s in scelte))
    return 0


def main() -> int:
    tutti = simboli()
    with ThreadPoolExecutor(max_workers=8) as ex:
        esiti = [e for e in ex.map(esame, tutti) if e]
    esiti.sort(key=lambda e: -e["volume_settembre_2026"])
    scelte = [e["simbolo"] for e in esiti[:12]]
    (QUI / "universo_fase2.json").write_text(json.dumps({"simboli_guardati": len(tutti), "ammessi": esiti,
                                                         "scelte": scelte}, indent=1), encoding="utf-8")
    print(len(tutti), "simboli;", len(esiti), "ammessi; scelte:", scelte)
    return 0


if __name__ == "__main__":
    import sys
    raise SystemExit(main_top100() if sys.argv[1:] == ["top100"] else main())
