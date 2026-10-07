"""Fase 0, punto 2: scarica i dati in-sample di ETHUSDT (e BTCUSDT come riferimento di mercato).

Solo file mensili fino al 2023-12 (il caricatore rifiuta oltre, a vault chiuso):
* ETHUSDT klines 15m (base: tutti i timeframe ammessi da 30m a 1d si aggregano da qui,
  sono multipli esatti di 15 minuti allineati all'UTC) e 1d (controllo dell'aggregazione
  e volume giornaliero in USDT);
* ETHUSDT markPriceKlines 15m (liquidazioni);
* ETHUSDT fundingRate;
* BTCUSDT klines 15m (riferimento di mercato, ammesso dal Passo 3).
Alla fine registra le impronte SHA-256 dei file di ETHUSDT e stampa i mesi assenti e
gli URL senza CHECKSUM remoto.
"""
from __future__ import annotations

import json
import sys
from datetime import date
from pathlib import Path

QUI = Path(__file__).resolve().parent
REPO = QUI.parent.parent.parent.parent
sys.path.insert(0, str(REPO))
from research.src import dati  # noqa: E402

INIZIO = date(2020, 1, 1)
FINE = dati.FINE_IN_SAMPLE
RADICE = dati.RADICE_DEFAULT

richieste = [
    ("ETHUSDT", "klines", "15m"),
    ("ETHUSDT", "klines", "1d"),
    ("ETHUSDT", "markPriceKlines", "15m"),
    ("ETHUSDT", "fundingRate", None),
    ("BTCUSDT", "klines", "15m"),
]

esito = {}
dati.azzera_checksum_mancanti()
for simbolo, tipo, intervallo in richieste:
    attesi = list(dati.mesi_del_periodo(INIZIO, FINE))
    percorsi = dati.scarica_periodo(simbolo, tipo, intervallo, INIZIO, FINE, RADICE)
    presenti = {p.name for p in percorsi}
    assenti = [f"{a}-{m:02d}" for a, m in attesi
               if dati.nome_file_mese(simbolo, tipo, intervallo, a, m) not in presenti]
    chiave = f"{simbolo}/{tipo}/{intervallo or ''}"
    esito[chiave] = {"file": len(percorsi), "mesi_attesi": len(attesi), "mesi_assenti": assenti}
    print(chiave, "file:", len(percorsi), "/", len(attesi), "assenti:", assenti)

impronte = dati.registra_impronte("ETHUSDT", RADICE)
print("impronte ETHUSDT registrate:", len(impronte))
print("checksum remoti mancanti:", len(dati.CHECKSUM_MANCANTI))
(QUI.parent / "fase0_scarico.json").write_text(json.dumps({
    "esito": esito,
    "checksum_mancanti": list(dati.CHECKSUM_MANCANTI),
    "n_impronte_ethusdt": len(impronte),
}, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
