"""I due controlli in avanti di ogni giro delle 4 ore (righe in REVISIONE_107.md e REVISIONE_105.md).

1. Annunci di Binance di chiusura dei perpetui pubblicati dopo il 21 ottobre 2026 09:30 UTC (l'ultimo noto: PTB e MITO).
2. Monete che scambiano contro il dollaro su Coinbase e hanno il perpetuo in USDT su Binance, e che non sono nell'elenco di quelle gia'
   viste (`controlli_avanti_coinbase.json`, accanto a questo file): sono le quotazioni nuove da misurare con la regola della prova 105.

Fino all'8 novembre 2026 lo script stava fuori dal repo e confrontava con `research/data/coinbase/primi_giorni.json`; il contenitore
nuovo dell'8 novembre li ha persi entrambi. L'elenco delle monete gia' viste ora sta nel repo: si aggiunge una moneta solo a mano,
dopo averla scritta nella tabella di REVISIONE_105.md (o dopo aver visto che e' vecchia), con `--aggiungi SIGLA`.

Uso: python3 -m research.programma7.controlli_avanti [--aggiungi SIGLA ...]
"""
from __future__ import annotations

import json
import sys
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

QUI = Path(__file__).resolve().parent
VISTE = QUI / "controlli_avanti_coinbase.json"
DOPO = datetime(2026, 10, 21, 9, 31, tzinfo=timezone.utc)   # dopo l'annuncio di PTB e MITO
ANNUNCI = ("https://www.binance.com/bapi/composite/v1/public/cms/article/list/query"
           "?type=1&catalogId=161&pageNo=1&pageSize=20")
BINANCE = "https://www.binance.com/fapi/v1/exchangeInfo"
COINBASE = "https://api.exchange.coinbase.com/products"


def _leggi(url: str):
    req = urllib.request.Request(url, headers={"User-Agent": "controlli-avanti/1.0", "Accept": "application/json"})
    for prova in range(3):
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.loads(r.read().decode())
        except Exception:                                    # noqa: BLE001 - rete: si riprova
            if prova == 2:
                raise
            time.sleep(2 ** prova)


def annunci_di_chiusura() -> tuple[list[tuple[str, str]], int]:
    dati = _leggi(ANNUNCI)
    articoli = [a for c in dati["data"]["catalogs"] for a in c.get("articles", [])]
    trovati = []
    for a in articoli:
        quando = datetime.fromtimestamp(a["releaseDate"] / 1000, tz=timezone.utc)
        titolo = a["title"]
        if quando >= DOPO and "Futures" in titolo and "Delist" in titolo:
            trovati.append((quando.strftime("%Y-%m-%d %H:%M"), titolo))
    return trovati, len(articoli)


def coinbase_con_perpetuo() -> list[str]:
    perpetui = {s["baseAsset"] for s in _leggi(BINANCE)["symbols"]
                if s.get("contractType") == "PERPETUAL" and s.get("quoteAsset") == "USDT" and s.get("status") == "TRADING"}
    coinbase = {p["base_currency"] for p in _leggi(COINBASE)
                if p.get("quote_currency") == "USD" and p.get("status") == "online" and not p.get("trading_disabled")}
    return sorted(perpetui & coinbase)


def main(argv: list[str]) -> int:
    viste = set(json.loads(VISTE.read_text())["viste"]) if VISTE.exists() else set()
    if argv[:1] == ["--aggiungi"]:
        viste |= set(argv[1:])
        VISTE.write_text(json.dumps({"nota": "monete gia' viste su Coinbase con il perpetuo di Binance (controlli_avanti.py)",
                                     "viste": sorted(viste)}, indent=1) + "\n")
        print(f"elenco delle monete gia' viste: {len(viste)}")
        return 0
    trovati, letti = annunci_di_chiusura()
    print(f"annunci di chiusura dopo il 21 ottobre: {trovati or 'nessuno'} | letti {letti}")
    insieme = coinbase_con_perpetuo()
    nuove = [s for s in insieme if s not in viste]
    print(f"monete su Coinbase con il perpetuo: {len(insieme)}; non ancora viste: {nuove or 'nessuna'}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
