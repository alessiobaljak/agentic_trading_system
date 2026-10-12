"""Lancia la prova a placebo (regole in regole.md) e scrive un esito per riga in esiti_k<k>.jsonl.

Non stampa nessuna misura: solo l'avanzamento. Le misure le calcola riassunto.py a prova finita.
Un file per sfasamento k: la prova k = 2 (una regola corretta) e' un'altra prova e non si mescola.
Ogni riga porta l'hash del commit del codice; il file rifiuta righe di un'altra versione del codice.
Riprende da dove era rimasta: una coppia (moneta, timeframe) gia' presente non si rifa'. Un errore di
una moneta si scrive come riga con ``errore`` (e la coppia si rifa' al prossimo lancio).
Uso, dalla radice del repository: python -m research.taratura.placebo.esegui [k]
"""
from __future__ import annotations

import json
import subprocess
import sys
import time
from datetime import date
from multiprocessing import Pool
from pathlib import Path

from research.taratura.placebo import placebo as P
from research.taratura.placebo.scarica import RADICE_DATI, monete

QUI = Path(__file__).resolve().parent


def file_esiti(k: int) -> Path:
    return QUI / f"esiti_k{k}.jsonl"


def versione_codice() -> str:
    """Hash del commit corrente; con modifiche non committate nella cartella della prova, rifiuta."""
    sporco = subprocess.run(["git", "status", "--porcelain", "--", str(QUI), str(QUI.parent.parent / "src")],
                            capture_output=True, text=True, check=True).stdout
    righe = [r for r in sporco.splitlines() if not r.endswith(".jsonl")]
    if righe:
        raise SystemExit("codice della prova o di src/ non committato: committa prima di lanciare\n" + "\n".join(righe))
    return subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, check=True).stdout.strip()


def _compito(arg):
    simbolo, primo, slippage, tf, k = arg
    t0 = time.time()
    try:
        esiti = P.valuta_moneta(simbolo, date.fromisoformat(primo), float(slippage), tf, RADICE_DATI, k)
        return simbolo, tf, k, esiti, None, time.time() - t0
    except Exception as e:  # una moneta che fallisce si riporta e non ferma le altre
        return simbolo, tf, k, [], f"{type(e).__name__}: {e}", time.time() - t0


def fatti(percorso: Path, versione: str) -> set:
    if not percorso.exists():
        return set()
    visti = set()
    with open(percorso) as f:
        for riga in f:
            e = json.loads(riga)
            if e.get("versione_codice") != versione:
                raise SystemExit(f"{percorso.name} contiene righe di un'altra versione del codice "
                                 f"({e.get('versione_codice')}): usa un file nuovo")
            if not e.get("errore_moneta"):
                visti.add((e["simbolo"], e["timeframe"]))
    return visti


def main() -> int:
    k = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    versione = versione_codice()
    percorso = file_esiti(k)
    gia = fatti(percorso, versione)
    compiti = [(m["simbolo"], m["primo_mese_archivio"], m["fascia_slippage"], tf, k)
               for m in monete() for tf in P.TIMEFRAME if (m["simbolo"], tf) not in gia]
    compiti.sort(key=lambda c: c[3] != "1h")  # prima le 1h, le piu' lunghe
    print(f"versione {versione[:8]}, sfasamento k={k}: compiti da fare {len(compiti)} (gia' fatti {len(gia)})",
          flush=True)
    with Pool(4) as pool, open(percorso, "a") as out:
        for n, (simbolo, tf, kk, esiti, errore, sec) in enumerate(pool.imap_unordered(_compito, compiti), 1):
            if errore:
                out.write(json.dumps({"simbolo": simbolo, "timeframe": tf, "sfasamento_k": kk,
                                      "errore_moneta": errore, "versione_codice": versione}) + "\n")
                print(f"[{n}/{len(compiti)}] {simbolo} {tf}: ERRORE {errore}", flush=True)
            else:
                for e in esiti:
                    e["versione_codice"] = versione
                    out.write(json.dumps(e, ensure_ascii=False) + "\n")
                errori = sum(1 for e in esiti if e.get("errore"))
                print(f"[{n}/{len(compiti)}] {simbolo} {tf}: {len(esiti)} righe, {errori} con errore, {sec:.0f}s",
                      flush=True)
            out.flush()
    return 0


if __name__ == "__main__":
    sys.exit(main())
