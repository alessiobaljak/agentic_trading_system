"""Programma 6, seconda prova: le candele giornaliere e il funding di tutti i perpetui USDT-M dell'archivio pubblico di
Binance, anche quelli tolti dal listino (SECONDA.md, sezione 2), con il CHECKSUM.

Scrive in ``research/data/p6g/<SIMBOLO>/{giorni,funding}/`` (fuori da git) e in ``scarico_giorni.json`` un'impronta per
simbolo e tipo: numero di file, primo e ultimo, e lo SHA-256 dell'elenco ordinato «nome impronta» (si ricalcola dai file).
Riprende da dove si e' fermato.

Uso: python3 -m research.programma6.scarico_giorni [SIMBOLO ...]
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

from research.programma5.strumenti.scarico import BASE, _prendi, elenca
from research.programma5.strumenti.universo import STABILI, simboli
from research.src.dati import leggi_checksum

RADICE = Path(__file__).resolve().parents[2]
DATI = RADICE / "research" / "data" / "p6g"
QUI = Path(__file__).parent
MESE_IN_CORSO = datetime.now(timezone.utc).strftime("%Y-%m")


def ammesso(s: str) -> bool:
    return bool(re.fullmatch(r"[A-Z0-9]+USDT", s)) and not any(s.startswith(x) for x in STABILI)


def _mese_piu(m: str, k: int) -> str:
    a, mm = int(m[:4]), int(m[5:7]) - 1 + k
    return f"{a + mm // 12:04d}-{mm % 12 + 1:02d}"


def _mesi(chiavi_: list) -> list:
    return sorted({x.group(1) for x in (re.search(r"-(\d{4}-\d{2})\.zip$", k) for k in chiavi_) if x})


def _giornalieri(prefisso: str, ultimo: str) -> list:
    """I file giornalieri dei mesi dopo l'ultimo mensile pubblicato, fino al mese in corso (solo se l'ultimo mensile e'
    degli ultimi due mesi: una moneta tolta dal listino da tempo non ha giornalieri)."""
    out = []
    if not ultimo or ultimo < _mese_piu(MESE_IN_CORSO, -2):
        return out
    m = _mese_piu(ultimo, 1)
    while m <= MESE_IN_CORSO:
        out += elenca(f"{prefisso}-{m}-")
        m = _mese_piu(m, 1)
    return out


def chiavi(s: str, premio: bool = False) -> dict:
    mensili = elenca(f"data/futures/um/monthly/klines/{s}/1d/")
    mm = _mesi(mensili)
    giorni = list(mensili) + _giornalieri(f"data/futures/um/daily/klines/{s}/1d/{s}-1d", mm[-1] if mm else "")
    funding = elenca(f"data/futures/um/monthly/fundingRate/{s}/")
    out = {"giorni": sorted(giorni), "funding": sorted(funding)}
    if premio:
        # l'indice del premio orario dei mesi senza il file del funding (per stimarlo: programma6/paper/REGOLE.md)
        fm = _mesi(funding)
        out["premio"] = sorted(_giornalieri(f"data/futures/um/daily/premiumIndexKlines/{s}/1h/{s}-1h", fm[-1] if fm else ""))
    return out


def _scarica(chiave: str, dest: Path):
    nome = chiave.rsplit("/", 1)[1]
    f = dest / nome
    ok = f.with_suffix(".zip.ok")
    if f.exists() and ok.exists():
        return nome, ok.read_text().strip()
    contenuto = _prendi(BASE + chiave)
    if contenuto is None:
        return nome, None
    somma = _prendi(BASE + chiave + ".CHECKSUM")
    impronta = hashlib.sha256(contenuto).hexdigest()
    if somma is not None and leggi_checksum(somma, chiave) != impronta:
        raise RuntimeError(f"CHECKSUM diverso per {chiave}")
    dest.mkdir(parents=True, exist_ok=True)
    tmp = f.with_suffix(".tmp")
    tmp.write_bytes(contenuto)
    tmp.replace(f)
    ok.write_text(impronta if somma is not None else impronta + " senza-checksum")
    return nome, ok.read_text().strip()


def impronta(esiti: list) -> dict:
    righe = sorted(f"{n} {h}" for n, h in esiti if h)
    return {"file": len(righe), "primo": righe[0].split()[0] if righe else "", "ultimo": righe[-1].split()[0] if righe else "",
            "sha256": hashlib.sha256("\n".join(righe).encode()).hexdigest()}


def uno(s: str, premio: bool = False) -> dict:
    out = {}
    for tipo, ch in chiavi(s, premio).items():
        with ThreadPoolExecutor(max_workers=8) as ex:
            esiti = list(ex.map(lambda k: _scarica(k, DATI / s / tipo), ch))
        out[tipo] = impronta(esiti)
    return out


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    tutti = argv or [s for s in simboli() if ammesso(s)]
    dest = QUI / "scarico_giorni.json"
    imp = json.loads(dest.read_text()) if dest.exists() else {}
    import os
    premio = os.environ.get("P6_PREMIO") == "1"
    if os.environ.get("P6_IMPRONTE"):
        dest = Path(os.environ["P6_IMPRONTE"]) / "scarico_giorni.json"
        if not dest.exists() and (QUI / "scarico_giorni.json").exists():
            imp = json.loads((QUI / "scarico_giorni.json").read_text())
        elif dest.exists():
            imp = json.loads(dest.read_text())
    with ThreadPoolExecutor(max_workers=int(os.environ.get("P6_FILI", "4"))) as ex:
        for s, r in zip(tutti, ex.map(lambda x: uno(x, premio), tutti)):
            imp[s] = r
            print(f"[giorni] {s}: {r['giorni']['file']} giorni/mesi, {r['funding']['file']} funding", flush=True)
            dest.write_text(json.dumps(imp, indent=0, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
