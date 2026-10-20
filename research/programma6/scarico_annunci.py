"""Programma 6: gli annunci pubblici di Binance (titolo e ora di pubblicazione) delle sezioni «New Cryptocurrency Listing»
(48), «Latest Binance News» (49) e «Delisting» (161), dall'elenco pubblico del sito. Solo titoli e date: servono a trovare
gli eventi (etichetta di monitoraggio, rimozioni, quotazioni) per le prove a eventi.

Scrive in ``research/data/annunci/<sezione>.json`` (fuori da git) e in ``scarico_annunci.json`` quanti annunci e
l'impronta dell'elenco. Uso: python3 -m research.programma6.scarico_annunci
"""
from __future__ import annotations

import hashlib
import json
import time
import urllib.request
from pathlib import Path

RADICE = Path(__file__).resolve().parents[2]
DATI = RADICE / "research" / "data" / "annunci"
QUI = Path(__file__).parent
URL = "https://www.binance.com/bapi/composite/v1/public/cms/article/list/query?type=1&catalogId={c}&pageNo={p}&pageSize=50"
SEZIONI = {48: "quotazioni", 49: "notizie", 161: "rimozioni"}


def pagina(c: int, p: int) -> tuple:
    """(annunci della pagina, totale della sezione)."""
    for prova in range(4):
        try:
            with urllib.request.urlopen(URL.format(c=c, p=p), timeout=30) as r:
                cat = json.loads(r.read())["data"]["catalogs"][0]
                return cat["articles"], int(cat["total"])
        except Exception:
            time.sleep(2 ** (prova + 1))
    raise RuntimeError(f"pagina {p} della sezione {c} non scaricata")


def main() -> int:
    DATI.mkdir(parents=True, exist_ok=True)
    imp = {}
    for c, nome in SEZIONI.items():
        tutti, p, totale = [], 1, 1
        while (p - 1) * 50 < totale:
            a, totale = pagina(c, p)
            if not a:
                break
            tutti += [{"id": x["id"], "titolo": x["title"], "ms": x["releaseDate"]} for x in a]
            p += 1
            time.sleep(0.5)
        tutti = sorted({x["id"]: x for x in tutti}.values(), key=lambda x: x["ms"])
        (DATI / f"{nome}.json").write_text(json.dumps(tutti, ensure_ascii=False, indent=0), encoding="utf-8")
        righe = "\n".join(f"{x['id']} {x['ms']} {x['titolo']}" for x in tutti)
        imp[nome] = {"annunci": len(tutti), "totale_dichiarato": totale, "sha256": hashlib.sha256(righe.encode()).hexdigest(),
                     "primo": tutti[0]["ms"] if tutti else None, "ultimo": tutti[-1]["ms"] if tutti else None}
        print(f"[annunci] {nome}: {len(tutti)}", flush=True)
    (QUI / "scarico_annunci.json").write_text(json.dumps(imp, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
