"""Controllo dei dati per l'idea I26 (il tono delle notizie): quante notizie datate ha Alpaca, anno per anno.

    python -m stock.prove.p028a      # servono le chiavi di Alpaca: gira su GitHub (azioni-ricerca)

**Non è una prova e non guarda nessun rendimento**: conta le notizie, per decidere se le regole della prova 28 si possono scrivere
(serve un archivio che parta dal 2015-2016 con notizie per la maggior parte dei titoli) e quanto costa scaricarle. Campione fisso:
un titolo ogni 17 dell'elenco attuale dell'S&P 500 in ordine alfabetico (30 titoli), le notizie di marzo di ogni anno dal 2015 al
2025; più tre giorni interi con tutte le notizie di tutti i titoli, per stimare la mole. Nel repository vanno solo i conteggi.
"""
from __future__ import annotations

from collections import Counter
from datetime import UTC, datetime

import numpy as np
import pandas as pd

from stock.dati import alpaca
from stock.prove.p001 import QUI


def main():
    membri = sorted(pd.read_csv(QUI.parent / "avanti" / "sp500_membri.csv")["simbolo"])
    campione = membri[::17]
    righe, fonti, senza_riassunto, totale = [], Counter(), 0, 0
    for anno in range(2015, 2026):
        conti, incompleti, per_notizia = [], 0, []
        for s in campione:
            n, completo = alpaca.notizie([s], datetime(anno, 3, 1, tzinfo=UTC), datetime(anno, 4, 1, tzinfo=UTC), pagine_massime=10)
            conti.append(len(n))
            incompleti += not completo
            for x in n:
                fonti[x.get("source", "?")] += 1
                senza_riassunto += not (x.get("summary") or "").strip()
                per_notizia.append(len(x.get("symbols") or []))
                totale += 1
        c = np.array(conti)
        righe.append(f"| {anno} | {int(np.median(c))} | {c.mean():.0f} | {int((c == 0).sum())} su {len(c)} | {int(c.min())}–{int(c.max())} | "
                     f"{incompleti} | {np.median(per_notizia) if per_notizia else 0:.0f} |")
        print(righe[-1], flush=True)
    giorni = []
    for g in (datetime(2016, 3, 15, tzinfo=UTC), datetime(2020, 3, 16, tzinfo=UTC), datetime(2024, 3, 15, tzinfo=UTC)):
        n, completo = alpaca.notizie(None, g, g.replace(hour=23, minute=59), pagine_massime=200)
        con_simbolo = sum(1 for x in n if x.get("symbols"))
        ore = Counter(pd.Timestamp(x["created_at"]).tz_convert("America/New_York").hour for x in n)
        fuori = sum(v for h, v in ore.items() if h < 9 or h >= 16)
        giorni.append(f"| {g:%Y-%m-%d} | {len(n)}{'' if completo else ' (o più: fermato a 200 pagine)'} | {con_simbolo} | "
                      f"{fuori / max(len(n), 1):.0%} |")
        print(giorni[-1], flush=True)
    testo = ["# Controllo dei dati per la prova 28 (il tono delle notizie) — quante notizie ha Alpaca", "",
             f"Calcolato da `python -m stock.prove.p028a` il {datetime.now(UTC):%Y-%m-%d %H:%M} UTC. Non è una prova: nessun rendimento "
             "guardato, solo conteggi. Campione fisso di 30 titoli dell'S&P 500 (uno ogni 17 in ordine alfabetico: "
             f"{', '.join(campione)}), notizie di marzo di ogni anno.", "",
             "| Anno | Notizie per titolo nel mese (mediana) | Media | Titoli senza notizie | Minimo–massimo | Titoli con l'elenco troncato "
             "(oltre 500) | Titoli citati per notizia (mediana) |", "|---|---|---|---|---|---|---|", *righe, "",
             f"Notizie del campione: {totale}; senza riassunto (solo il titolo): {senza_riassunto / max(totale, 1):.0%}; fonti: "
             + ", ".join(f"{k} {v}" for k, v in fonti.most_common(5)) + ".", "",
             "| Giorno intero, tutti i titoli | Notizie | Con almeno un titolo citato | Fuori dall'orario di borsa (prima delle 9 o dopo le 16 "
             "di New York) |", "|---|---|---|---|", *giorni]
    (QUI / "P028a_risultati.md").write_text("\n".join(testo) + "\n")
    print("\n".join(testo[-8:]))


if __name__ == "__main__":
    main()
