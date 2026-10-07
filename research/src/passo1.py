"""Il Passo 1 eseguito: la selezione delle monete di campagna, dalla rete ai file.

SOLO PER IL COORDINAMENTO (branch ``research/coordinamento``). Mette insieme le
funzioni pure di ``selezione.py`` e le poche letture di rete ammesse dal Passo 1:
la lista dei contratti di oggi (listing), l'indice dell'archivio (quali
contratti hanno dati, compresi i delistati, e fino a quando), e le candele
GIORNALIERE del solo 2023 per il volume. Nessun prezzo del vault viene
scaricato: delle date dopo il 2023 si leggono solo i NOMI dei file.

Uso (dal coordinamento):
    python -m research.src.passo1            # scrive in research/universo/ e research/campagne/*/scheda_moneta.md
Le candele giornaliere del 2023 finiscono in research/data/insample/<SIMBOLO>/klines/1d/
(fuori da git) e restano utili alle campagne.
"""
from __future__ import annotations

import csv
import json
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import date
from pathlib import Path
from typing import Dict, List, Optional

from research.src import dati
from research.src import selezione as sel

RADICE = dati.RADICE_DEFAULT
CARTELLA_UNIVERSO = RADICE / "universo"
CARTELLA_CAMPAGNE = RADICE / "campagne"
#: quante letture dell'indice in parallelo (sono richieste leggere di soli nomi)
LAVORATORI = 8


def _di(msg: str) -> None:
    print(msg, flush=True)


def contratti_di_oggi(fetch=None) -> Dict[str, dict]:
    """{simbolo: contratto} dei perpetui in USDT di exchangeInfo (tutti gli stati)."""
    out = {}
    for c in dati.lista_contratti(fetch):
        if c.get("quoteAsset") == "USDT" and c.get("contractType") == "PERPETUAL" and c.get("symbol"):
            out[str(c["symbol"])] = c
    return out


def candidata_da_archivio(simbolo: str, oggi: Dict[str, dict], nomi_file: List[str]) -> sel.Candidata:
    """La candidata con listing, primo e ultimo mese; il volume si aggiunge dopo."""
    primo, ultimo = sel.primo_e_ultimo_mese(nomi_file)
    contratto = oggi.get(simbolo)
    negoziata = bool(contratto) and contratto.get("status") == "TRADING"
    if contratto and contratto.get("onboardDate"):
        listing, da = sel.data_da_ms(int(contratto["onboardDate"])), "exchangeInfo"
    elif primo is not None:
        listing, da = primo, "archivio"
    else:
        listing, da = None, "sconosciuta"
    return sel.Candidata(simbolo=simbolo, negoziata_oggi=negoziata, listing=listing, listing_da=da,
                         primo_mese=primo, ultimo_mese=ultimo)


def volume_2023(simbolo: str, radice: Path = RADICE, fetch=None):
    """(media, giorni) del volume in USDT nel 2023 dalle candele giornaliere, scaricate
    (o gia' su disco) con il caricatore e il suo blocco del vault."""
    percorsi = dati.scarica_periodo(simbolo, "klines", "1d", sel.INIZIO_FINESTRA_VOLUME,
                                    sel.FINE_FINESTRA_VOLUME, radice, fetch)
    giorni = []
    for p in percorsi:
        giorni.extend(sel.volume_quote_giornaliero(dati.righe_csv_da_zip(p)))
    return sel.volume_medio_nella_finestra(giorni)


def esegui(radice: Path = RADICE, fetch=None, n: int = sel.NUMERO_MONETE_CAMPAGNA,
           scrivi: bool = True) -> dict:
    t0 = time.time()
    oggi = contratti_di_oggi(fetch)
    _di(f"[passo1] contratti perpetui in USDT su exchangeInfo: {len(oggi)} "
        f"(TRADING {sum(1 for c in oggi.values() if c.get('status') == 'TRADING')})")
    simboli = [s for s in dati.elenca_simboli_archivio(fetch) if sel.e_perpetuo_usdt(s)]
    _di(f"[passo1] contratti perpetui in USDT con una cartella nell'archivio: {len(simboli)}")

    def _nomi(s):
        return s, sel.elenca_file_archivio(s, "1d", fetch)
    candidate: List[sel.Candidata] = []
    with ThreadPoolExecutor(max_workers=LAVORATORI if fetch is None else 1) as ex:
        for simbolo, nomi in ex.map(_nomi, simboli):
            candidate.append(candidata_da_archivio(simbolo, oggi, nomi))
    _di(f"[passo1] indice letto per {len(candidate)} contratti in {time.time() - t0:.0f}s")

    # il volume si scarica solo per chi passa i filtri sul listing e sulla fine dei dati:
    # le altre sono escluse comunque e non vale la pena scaricare 12 file a testa
    da_scaricare = [c for c in candidate
                    if c.listing is not None and c.listing < sel.LIMITE_LISTING
                    and c.ultimo_mese is not None and c.ultimo_mese >= sel.FINE_FINESTRA_VOLUME]
    _di(f"[passo1] volume 2023 da scaricare per {len(da_scaricare)} contratti")
    for i, c in enumerate(da_scaricare, 1):
        try:
            c.volume_medio_2023, c.giorni_2023 = volume_2023(c.simbolo, radice, fetch)
        except Exception as exc:  # noqa: BLE001 - un contratto rotto non ferma la selezione
            c.motivi_esclusione.append(f"errore nello scarico del 2023: {str(exc)[:80]}")
            _di(f"[passo1] {c.simbolo}: {str(exc)[:120]}")
        if i % 20 == 0:
            _di(f"[passo1] volume letto per {i}/{len(da_scaricare)} ({time.time() - t0:.0f}s)")
    risultato = sel.seleziona(candidate, n=n)
    # un errore di scarico resta un motivo di esclusione anche se `valuta` li riscrive
    for c in risultato["escluse"]:
        pass
    risultato["secondi"] = round(time.time() - t0)
    risultato["checksum_mancanti"] = list(dati.CHECKSUM_MANCANTI)
    if scrivi:
        scrivi_risultati(risultato, candidate, radice)
    return risultato


def scrivi_risultati(risultato: dict, candidate: List[sel.Candidata], radice: Path) -> None:
    universo = radice / "universo"
    universo.mkdir(parents=True, exist_ok=True)
    tutte = sorted(candidate, key=lambda c: (-(c.volume_medio_2023 or 0.0), c.simbolo))
    sel.scrivi_csv(universo / "candidate.csv", tutte)
    sel.scrivi_csv(universo / "monete_campagna.csv", risultato["campagna"])
    sel.scrivi_csv(universo / "monete_idonee_non_campagna.csv", risultato["altre_idonee"])
    with open(universo / "conteggi.json", "w", encoding="utf-8") as f:
        json.dump({"conteggi": risultato["conteggi"], "secondi": risultato["secondi"],
                   "checksum_mancanti": risultato["checksum_mancanti"],
                   "data": date.today().isoformat()}, f, ensure_ascii=False, indent=1)
    for c in risultato["campagna"]:
        cartella = radice / "campagne" / c.simbolo
        cartella.mkdir(parents=True, exist_ok=True)
        (cartella / "scheda_moneta.md").write_text(sel.scheda_moneta(c), encoding="utf-8")
    _di(f"[passo1] scritti universo/candidate.csv ({len(tutte)}), monete_campagna.csv "
        f"({len(risultato['campagna'])}), monete_idonee_non_campagna.csv "
        f"({len(risultato['altre_idonee'])}), conteggi.json e {len(risultato['campagna'])} schede")


def main(argv: Optional[List[str]] = None) -> int:
    r = esegui()
    _di(f"[passo1] conteggi: {json.dumps(r['conteggi'], ensure_ascii=False)}")
    for c in r["campagna"]:
        _di(f"  {c.simbolo:14s} listing {c.listing} ({c.listing_da}) · volume 2023 "
            f"{c.volume_medio_2023 / 1e6:,.0f} M USDT/giorno su {c.giorni_2023} giorni · "
            f"slippage {c.fascia_slippage:.2%} · {'negoziata' if c.negoziata_oggi else 'DELISTATA'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
