#!/usr/bin/env python3
"""Le misure della prova a placebo a barre giornaliere: il riassunto della prova a 1 ora
(``taratura/placebo_gruppo/riassunto.py``) con i cambiamenti dichiarati: timeframe «1d», le sei regole con i nomi di
``placebo_paniere.py``, le soglie di ``regole.md`` di questa cartella (40 placebo valutabili per periodo, le quote del
gruppo), e le regole di questa cartella. Scrive ``risultati.md`` qui se chiamato con ``--md``.

Uso: ``python research/taratura/placebo_paniere/riassunto.py [--json FILE] [--md]``.
"""
from __future__ import annotations

import argparse
import io
import json
import subprocess
import sys
from contextlib import redirect_stdout
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Sequence

QUI = Path(__file__).resolve().parent
sys.path.insert(0, str(QUI.parents[2]))
sys.path.insert(0, str(QUI.parent / "placebo_gruppo"))

# il lanciatore del paniere si carica dal SUO file (il nome `esegui` nel percorso e' quello della prova a 1 ora):
# importandolo imposta sul modulo `esegui` della prova a 1 ora le regole, il modulo e le serie di questa prova
import importlib.util  # noqa: E402

_spec = importlib.util.spec_from_file_location("esegui_paniere", QUI / "esegui.py")
EP = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(EP)
PP = EP.PP
import riassunto as R  # noqa: E402  (il riassunto della prova a 1 ora)

R.TIMEFRAME = ("1d",)
R.REGOLE = PP.REGOLE
R.DIREZIONI = PP.DIREZIONI
R.COMBINAZIONI = tuple((tf, r, d) for tf in R.TIMEFRAME for r in PP.REGOLE for d in PP.DIREZIONI)
#: le soglie scritte in regole.md di questa cartella (sezione 4)
SOGLIE = {"campione_minimo": 40, "quota_costruzione": 0.03, "quota_validazione": 0.13}
R.SOGLIE_DELLE_REGOLE = dict(SOGLIE)
_soglie_gruppo = R.soglie_da_parametri


def soglie_da_parametri(percorso: Path):
    soglie = _soglie_gruppo(percorso)
    soglie.update(SOGLIE)
    return soglie


R.soglie_da_parametri = soglie_da_parametri


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Le misure della prova a placebo a barre giornaliere")
    parser.add_argument("--json", type=Path, default=None)
    parser.add_argument("--md", action="store_true", help="scrive anche risultati.md in questa cartella")
    args = parser.parse_args(argv)
    testo = io.StringIO()
    argomenti = ["--cartella", str(QUI)]
    json_tmp = args.json or (QUI / "riassunto.json")
    argomenti += ["--json", str(json_tmp)]
    with redirect_stdout(testo):
        codice = R.main(argomenti)
    stampa = testo.getvalue()
    print(stampa)
    if args.md:
        commit = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=QUI, capture_output=True, text=True).stdout.strip()
        intestazione = (f"# Prova a placebo a barre giornaliere — risultati\n\n"
                        f"Scritto da `riassunto.py` di questa cartella il {datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}, "
                        f"commit {commit}; regole in `regole.md` (soglie: al massimo il 3% di «nette» in costruzione, al massimo il 13% "
                        f"con p sotto 0,10 in validazione, almeno 40 placebo valutabili per periodo). Le righe sono in `esiti_k<k>.jsonl`, "
                        f"il riassunto completo in `riassunto.json`.\n\n```\n")
        (QUI / "risultati.md").write_text(intestazione + stampa + "```\n", encoding="utf-8")
        print("scritto", QUI / "risultati.md")
    return codice


if __name__ == "__main__":
    raise SystemExit(main())
