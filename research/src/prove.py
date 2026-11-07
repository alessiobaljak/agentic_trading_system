"""Il registro delle varianti di ogni prova (`research/trials/<id_prova>.csv`): una riga per variante provata, anche fallita, in
sola aggiunta. Serve all'auditor (`.claude/agents/backtest-auditor.md`) per contare le varianti e allo Sharpe corretto per il numero
di prove. Un file per prova, così più ricercatori in parallelo non si toccano.

Uso da codice:   from research.src.prove import registra
Uso da riga:     python3 -m research.src.prove --riepilogo [id_prova]

Le righe non si cancellano e non si riscrivono mai: il registro non si tronca, non si archivia e non si riassume.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import os
import re
import subprocess
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

CARTELLA = Path(__file__).resolve().parents[1] / "trials"
CAMPI = ["ora_utc", "id_prova", "id_variante", "parametri", "impronta", "scala", "commit", "seme", "n", "misure", "esito", "note"]


def _id(testo: str) -> str:
    if not re.fullmatch(r"[A-Za-z0-9_-]{1,60}", str(testo)):
        raise ValueError(f"id non valido (solo lettere, cifre, - e _): {testo!r}")
    return str(testo)


def impronta(parametri: dict) -> str:
    return hashlib.sha256(json.dumps(parametri, sort_keys=True, ensure_ascii=False).encode()).hexdigest()[:16]


def _commit() -> str:
    try:
        return subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True, timeout=10).stdout.strip()
    except Exception:  # noqa: BLE001
        return ""


def registra(id_prova: str, id_variante: str, parametri: dict, scala: str, n: int, misure: dict, esito: str, note: str = "",
             seme=None, commit: str | None = None, cartella: Path = CARTELLA) -> dict:
    """Aggiunge una riga a `<cartella>/<id_prova>.csv` (l'intestazione solo la prima volta). Restituisce la riga scritta."""
    riga = {"ora_utc": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"), "id_prova": _id(id_prova),
            "id_variante": _id(id_variante), "parametri": json.dumps(parametri, sort_keys=True, ensure_ascii=False),
            "impronta": impronta(parametri), "scala": scala, "commit": _commit() if commit is None else commit,
            "seme": "" if seme is None else str(seme), "n": int(n),
            "misure": json.dumps(misure, sort_keys=True, ensure_ascii=False), "esito": esito, "note": note}
    cartella = Path(cartella)
    cartella.mkdir(parents=True, exist_ok=True)
    f = cartella / f"{riga['id_prova']}.csv"
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=CAMPI)
    nuovo = not f.exists()
    if nuovo:
        w.writeheader()
    w.writerow(riga)
    fd = os.open(f, os.O_WRONLY | os.O_APPEND | os.O_CREAT, 0o644)      # in sola aggiunta, una scrittura sola
    try:
        os.write(fd, buf.getvalue().encode("utf-8"))
    finally:
        os.close(fd)
    return riga


def riepilogo(cartella: Path = CARTELLA, solo: str | None = None) -> list:
    out = []
    for f in sorted(Path(cartella).glob("*.csv")):
        if solo and f.stem != solo:
            continue
        with f.open(encoding="utf-8", newline="") as fh:
            righe = list(csv.DictReader(fh))
        esiti = Counter(r["esito"] for r in righe)
        out.append(f"{f.stem}: {len(righe)} righe, {len({r['impronta'] for r in righe})} varianti diverse; esiti "
                   + ", ".join(f"{k} {v}" for k, v in esiti.most_common()))
    return out or ["nessun registro delle varianti"]


def main(argv=None):
    p = argparse.ArgumentParser(description="Riepilogo dei registri delle varianti")
    p.add_argument("--riepilogo", nargs="?", const="", default=None, metavar="ID_PROVA")
    a = p.parse_args(argv)
    print("\n".join(riepilogo(solo=a.riepilogo or None)[:20]))


if __name__ == "__main__":
    main()
