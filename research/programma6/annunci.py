"""Programma 6: gli eventi dagli annunci pubblici di Binance (`scarico_annunci.py`): le monete messe sotto l'etichetta di
monitoraggio, le monete che Binance toglie dal listino a pronti, le monete quotate a pronti che avevano gia' il perpetuo.
Solo titoli e ore di pubblicazione: nessun prezzo.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

RADICE = Path(__file__).resolve().parents[2]
DATI = RADICE / "research" / "data" / "annunci"


def _carica(*nomi) -> list:
    tutti = []
    for n in nomi:
        tutti += json.loads((DATI / f"{n}.json").read_text(encoding="utf-8"))
    return sorted({x["id"]: x for x in tutti}.values(), key=lambda x: x["ms"])


def _sigle(testo: str) -> list:
    """«A, B, C & D» → [A, B, C, D]; toglie quello che c'e' fra parentesi («SLX (SLIMEX)» → SLX)."""
    testo = re.sub(r"\([^)]*\)", "", testo)
    parti = re.split(r",\s*|\s*&\s*|\s+and\s+", testo)
    return [p.strip() for p in parti if re.fullmatch(r"[A-Z0-9]{1,15}", p.strip())]


def eventi_monitoraggio() -> list:
    """(ms, annuncio, sigla) per ogni moneta aggiunta all'etichetta di monitoraggio."""
    out = []
    for x in _carica("notizie", "rimozioni", "quotazioni"):
        m = re.search(r"Extend the Monitoring Tag to (?:Include )?(.+?)(?:,? and Remove|, Remove| on 20\d\d-|$)", x["titolo"])
        if m:
            out += [(x["ms"], x["id"], s) for s in _sigle(m.group(1))]
    return out


def eventi_rimozione() -> list:
    """(ms, annuncio, sigla) per ogni moneta che Binance toglie dal listino a pronti («Binance Will Delist ...»)."""
    out = []
    for x in _carica("rimozioni", "notizie"):
        m = re.match(r"Binance Will Delist (.+?) on 20\d\d-\d\d-\d\d", x["titolo"])
        if m:
            out += [(x["ms"], x["id"], s) for s in _sigle(m.group(1))]
    return out


def eventi_quotazione() -> list:
    """(ms, annuncio, sigla) per ogni quotazione a pronti con la sigla fra parentesi («Binance Will List Nome (SIGLA)»)."""
    out = []
    for x in _carica("quotazioni"):
        m = re.match(r"Binance Will (?:List|Add) (.+?)(?: with Seed Tag Applied| on | and |$)", x["titolo"])
        if m and "Futures" not in x["titolo"] and "Margin" not in x["titolo"]:
            out += [(x["ms"], x["id"], s) for s in re.findall(r"\(([A-Z0-9]{1,15})\)", m.group(1))]
    return out


def perpetuo(sigla: str, simboli) -> str:
    """Il perpetuo contro USDT della sigla (anche con il prefisso dei multipli), o ''."""
    for p in (f"{sigla}USDT", f"1000{sigla}USDT", f"1000000{sigla}USDT", f"1M{sigla}USDT"):
        if p in simboli:
            return p
    return ""
