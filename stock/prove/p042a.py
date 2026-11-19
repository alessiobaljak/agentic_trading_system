"""Prova 42, primo passo: l'elenco dei moduli 13D con l'ora di pubblicazione, l'azienda oggetto e il simbolo di allora
(`P042_attivisti.md`, `stock/dati/attivisti.py`). **Non è il calcolo della prova**: solo dati pubblici della SEC, nessun prezzo.

    python -m stock.prove.p042a        # gira su GitHub (azioni-ricerca), con il segreto SEC_CONTATTO; riprende da dove si è fermato

Scrive `dati/sec_attivisti.csv.gz` (solo a elenco completo) e `P042a_risultati.md` (i conteggi e il controllo dell'ora).
"""
from __future__ import annotations

import os
import sys
from datetime import UTC, datetime

from stock.dati import attivisti
from stock.prove.p001 import QUI


def main(argv: list[str]) -> None:
    if not os.environ.get("SEC_CONTATTO"):
        raise SystemExit("manca il segreto SEC_CONTATTO (l'indirizzo di contatto che la SEC chiede): va aggiunto dal proprietario")
    x = attivisti.main(argv)
    d = x["depositi"]
    ore = d["accettazione"].str[8:10].astype(int)
    fasce = {"0-4": (ore < 4).sum(), "4-9:30": ((ore >= 4) & (ore < 9)).sum() + ((ore == 9) & (d["accettazione"].str[10:12] < "30")).sum()}
    fasce["9:30-16"] = ((ore >= 9) & (ore < 16)).sum() - ((ore == 9) & (d["accettazione"].str[10:12] < "30")).sum()
    fasce["16-20"] = ((ore >= 16) & (ore < 20)).sum()
    fasce["20-24"] = (ore >= 20).sum()
    per_anno = d.groupby(d["giorno"].str[:4]).agg(depositi=("numero", "size"), con_simbolo=("simbolo", lambda s: s.notna().sum()))
    testo = ["# Prova 42, primo passo — l'elenco dei moduli 13D", "",
             f"Calcolato da `python -m stock.prove.p042a` il {datetime.now(UTC):%Y-%m-%d %H:%M} UTC (dati pubblici della SEC, nessun "
             "prezzo). **Non è il calcolo della prova.**", "",
             f"* Elenco **{'completo' if x['completo'] else 'NON completo: il lavoro va rilanciato, riprende da dove si è fermato'}**. "
             f"Primi depositi «SC 13D» dal {attivisti.DAL} al {attivisti.FINO} con l'ora e l'oggetto: {len(d)}; scartati perché chi "
             f"deposita è l'azienda stessa: {x['stessa']}; con il simbolo di allora: {int(d['simbolo'].notna().sum())}.",
             "* Per fascia d'ora (l'ora com'è scritta nell'intestazione): " + ", ".join(f"{k} {int(v)}" for k, v in fasce.items()) + ".",
             "", "| Anno | Depositi | Con il simbolo |", "|---|---|---|",
             *[f"| {a} | {r.depositi} | {r.con_simbolo} |" for a, r in per_anno.iterrows()], "",
             "**Il controllo dell'ora** (intestazione contro l'elenco dei depositi dell'azienda, che la prova 36 usa come ora UTC):", "",
             *([f"* {r}" for r in x["controllo"]] or ["* non fatto (elenco non completo, o nessun deposito trovato nell'elenco)"])]
    (QUI / "P042a_risultati.md").write_text("\n".join(testo) + "\n")
    if x["completo"]:
        d.to_csv(QUI / "dati" / "sec_attivisti.csv.gz", index=False)
    print("\n".join(testo[4:]))


if __name__ == "__main__":
    main(sys.argv[1:])
