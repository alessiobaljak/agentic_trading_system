"""Programma 5: scarico dei dati dall'archivio pubblico di Binance, con il CHECKSUM (REGOLE.md, sezione 3).

Scrive in ``research/data/p5/<SIMBOLO>/<tipo>/`` (fuori da git) e le impronte in
``research/programma5/scarico_<tipo>.json``. Riprende da dove si e' fermato: un file gia' scaricato e verificato non si
riscarica. I file che il server non ha (404) non sono errori: una moneta non quotata, un giorno non ancora pubblicato.

Uso:
    python3 -m research.programma5.strumenti.scarico klines      # 1 minuto, mensili + giornalieri del mese in corso
    python3 -m research.programma5.strumenti.scarico metrics     # giornalieri
    python3 -m research.programma5.strumenti.scarico funding     # mensili
    python3 -m research.programma5.strumenti.scarico premium     # indice del premio sullo spot, 1 ora, mensili
    python3 -m research.programma5.strumenti.scarico --dal 2023-09 klines SIMBOLO ...   # solo dal mese indicato
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from datetime import date, timedelta
from pathlib import Path

from research.src.dati import USER_AGENT, fetch_http, leggi_checksum

RADICE = Path(__file__).resolve().parents[3]
DATI = RADICE / "research" / "data" / "p5"
QUI = Path(__file__).resolve().parents[1]
BASE = "https://data.binance.vision/"
ELENCO = "https://s3-ap-northeast-1.amazonaws.com/data.binance.vision"
MONETE = ("BTCUSDT", "ETHUSDT", "SOLUSDT", "XRPUSDT", "BNBUSDT", "DOGEUSDT",
          "ADAUSDT", "LINKUSDT", "AVAXUSDT", "LTCUSDT", "DOTUSDT", "TRXUSDT")
PREFISSI = {
    "klines": ["data/futures/um/monthly/klines/{s}/1m/", "data/futures/um/daily/klines/{s}/1m/"],
    "metrics": ["data/futures/um/daily/metrics/{s}/"],
    "funding": ["data/futures/um/monthly/fundingRate/{s}/"],
    "premium": ["data/futures/um/monthly/premiumIndexKlines/{s}/1h/"],
}


def _leggi(url: str, tentativi: int = 6) -> str:
    """Una pagina dell'elenco S3, con nuovi tentativi sulle connessioni interrotte."""
    import time
    for k in range(tentativi):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
            with urllib.request.urlopen(req, timeout=60) as r:
                return r.read().decode("utf-8")
        except OSError:
            if k == tentativi - 1:
                raise
            time.sleep(2 ** k)


def elenca(prefisso: str) -> list:
    """Le chiavi .zip sotto un prefisso, con la paginazione dell'elenco S3."""
    chiavi, marker = [], ""
    while True:
        url = f"{ELENCO}?prefix={prefisso}&max-keys=1000" + (f"&marker={marker}" if marker else "")
        testo = _leggi(url)
        trovate = re.findall(r"<Key>([^<]+)</Key>", testo)
        chiavi += [k for k in trovate if k.endswith(".zip")]
        if "<IsTruncated>true</IsTruncated>" not in testo or not trovate:
            return chiavi
        marker = trovate[-1]


def _scelte(tipo: str, s: str) -> list:
    chiavi = []
    for p in PREFISSI[tipo]:
        chiavi += elenca(p.format(s=s))
    if tipo == "klines":
        # i giornalieri servono solo per i mesi che non hanno ancora il file mensile
        mesi = {re.search(r"-(\d{4}-\d{2})\.zip$", k).group(1) for k in chiavi if "/monthly/" in k}
        chiavi = [k for k in chiavi if "/monthly/" in k
                  or re.search(r"-(\d{4}-\d{2})-\d{2}\.zip$", k).group(1) not in mesi]
    return sorted(chiavi)


def _prendi(url: str, tentativi: int = 6):
    """``fetch_http`` con nuovi tentativi sugli errori di rete (connessioni interrotte), attese crescenti."""
    import time
    for k in range(tentativi):
        try:
            return fetch_http(url)
        except OSError:
            if k == tentativi - 1:
                raise
            time.sleep(2 ** k)


def _scarica(chiave: str, s: str, tipo: str):
    nome = chiave.rsplit("/", 1)[1]
    dest = DATI / s / tipo / nome
    if dest.exists() and dest.with_suffix(".zip.ok").exists():
        return nome, dest.with_suffix(".zip.ok").read_text().strip()
    contenuto = _prendi(BASE + chiave)
    if contenuto is None:
        return nome, None
    somma = _prendi(BASE + chiave + ".CHECKSUM")
    impronta = hashlib.sha256(contenuto).hexdigest()
    if somma is not None and leggi_checksum(somma, chiave) != impronta:
        raise RuntimeError(f"CHECKSUM diverso per {chiave}")
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_suffix(".tmp")
    tmp.write_bytes(contenuto)
    tmp.replace(dest)
    dest.with_suffix(".zip.ok").write_text(impronta if somma is not None else impronta + " senza-checksum")
    return nome, impronta


def _mese(chiave: str) -> str:
    m = re.search(r"-(\d{4}-\d{2})(?:-\d{2})?\.zip$", chiave)
    return m.group(1) if m else ""


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    dal = ""
    if "--dal" in argv:
        i = argv.index("--dal")
        dal = argv[i + 1]
        del argv[i: i + 2]
    tipo = argv[0] if argv else "klines"
    monete = argv[1:] or list(MONETE)
    impronte_file = QUI / f"scarico_{tipo}.json"
    impronte = json.loads(impronte_file.read_text()) if impronte_file.exists() else {}
    for s in monete:
        chiavi = [k for k in _scelte(tipo, s) if _mese(k) >= dal]
        with ThreadPoolExecutor(max_workers=8) as ex:
            esiti = list(ex.map(lambda k: _scarica(k, s, tipo), chiavi))
        impronte[s] = {**impronte.get(s, {}), **{n: h for n, h in esiti if h}}
        impronte_file.write_text(json.dumps(impronte, indent=0, sort_keys=True))
        print(f"[scarico] {tipo} {s}: {len(impronte[s])} file (fino a {max(impronte[s]) if impronte[s] else '-'})",
              flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
