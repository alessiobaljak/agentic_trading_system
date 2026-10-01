"""Quello che la DASHBOARD legge senza che nessuno lo aggiorni a mano.

1 ott 2026, richieste del proprietario: «cosa aspetta il sì» in dashboard senza
aggiornarlo a mano (backlog J2) e, dopo, il REPORT GIORNALIERO in una sezione
sola della dashboard.

Questo script gira SULLA MACCHINA, dove il repo e' aggiornato dall'agente ops:
  * dopo ogni giro del gate (lo lancia `scripts/discover_strategies.py` alla
    fine, in un processo a parte con un tempo massimo: un suo errore non tocca
    il gate);
  * a richiesta, dal canale ops (`report-giornaliero`).

Cosa pubblica:
  * `dashboard/backlog` (Firestore) e `/backlog` (RTDB): `docs/backlog.md` letto
    da `bot.learning.backlog_doc` — una fonte sola, nessuna copia.

Uso:
  python -m scripts.report_giornaliero --pubblica   # legge e scrive Firebase
  python -m scripts.report_giornaliero              # stampa e basta
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import time

from bot.learning.backlog_doc import leggi_backlog

#: la radice del repo (questo file sta in scripts/)
RADICE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VERSIONE_SCHEMA = 1


def _commit(radice: str = RADICE) -> str | None:
    """L'hash corto del commit del repo sulla macchina: dice da quale versione
    dei file viene il documento. None se git non risponde."""
    try:
        out = subprocess.run(["git", "-C", radice, "rev-parse", "--short", "HEAD"],
                             capture_output=True, text=True, timeout=10)
        return out.stdout.strip() or None
    except Exception:  # noqa: BLE001
        return None


def doc_backlog(radice: str = RADICE, now: float | None = None) -> dict:
    """Il documento del backlog per la dashboard. Senza file: gruppi vuoti e
    `errore`, mai un'eccezione."""
    now = time.time() if now is None else now
    meta = {"versione_schema": VERSIONE_SCHEMA, "generato_at": now,
            "fonte": "docs/backlog.md", "commit": _commit(radice)}
    try:
        with open(os.path.join(radice, "docs", "backlog.md"), encoding="utf-8") as f:
            testo = f.read()
    except OSError as exc:
        return {"meta": {**meta, "errore": f"backlog non leggibile ({exc})"[:200]},
                "gruppi": [], "aspetta_si": [], "n_voci": 0, "aggiornato": None}
    return {"meta": meta, **leggi_backlog(testo)}


def _scrivi(fb, collezione: str, doc_id: str, percorso_rtdb: str, doc: dict) -> bool:
    """Firestore e specchio RTDB, come il documento del gate. Non solleva mai."""
    from bot.core.registry import pulisci_per_firestore
    doc = pulisci_per_firestore(doc)
    ok = False
    try:
        fb.set_doc(collezione, doc_id, doc)
        ok = True
    except Exception as exc:  # noqa: BLE001
        print(f"[report] Firestore {collezione}/{doc_id} non scritto ({str(exc)[:160]})")
    try:
        fb.set_rtdb(percorso_rtdb, doc)
    except Exception as exc:  # noqa: BLE001
        print(f"[report] RTDB {percorso_rtdb} non scritto ({str(exc)[:160]})")
    return ok


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--pubblica", action="store_true",
                    help="scrive in Firebase (senza: stampa e basta)")
    args = ap.parse_args(argv)
    backlog = doc_backlog()
    print(f"[report] backlog: {backlog.get('n_voci', 0)} voci in "
          f"{len(backlog.get('gruppi') or [])} gruppi, aspettano il si' "
          f"{len(backlog.get('aspetta_si') or [])} (commit {backlog['meta'].get('commit')})")
    if not args.pubblica:
        print(json.dumps(backlog, ensure_ascii=False, indent=1)[:4000])
        return 0
    from bot.core.firebase_client import get_firebase
    fb = get_firebase()
    ok = _scrivi(fb, "dashboard", "backlog", "/backlog", backlog)
    print(f"[report] backlog pubblicato: {'si' if ok else 'NO'}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
