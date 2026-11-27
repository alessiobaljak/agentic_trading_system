"""Riscarica le azioni societarie dei titoli già in archivio (solo l'elenco di dividendi, frazionamenti e scissioni: niente prezzi), con la
correzione del 27 novembre 2026 (`alpaca.OLTRE_LA_FINE`): prima mancavano i dividendi staccati nelle ultime settimane di ogni periodo e
pagati dopo la fine (nel 2024 circa 111 su 1846, prova 40b; audit `stock/AUDIT_2026-11-27.md`).

Si lancia una volta sul lavoro di GitHub della ricerca (`azioni_ricerca.yml`, prova «rinnova_azioni»): le chiavi di Alpaca stanno solo lì.
Scrive `stock/prove/RINNOVO_AZIONI_risultati.md` con i dividendi per anno di stacco, prima e dopo (solo conteggi).

    python -m stock.dati.rinnova_azioni
"""
from __future__ import annotations

from collections import Counter
from datetime import UTC, datetime
from pathlib import Path

from stock.dati import alpaca, archivio

# gli stessi periodi degli scarichi che hanno creato gli archivi (p027.DAL/AL, p029.PERIODI, scarica_chiuso.INIZIO/FINE)
RICERCA = (datetime(2015, 11, 1, tzinfo=UTC), datetime(2025, 1, 1, 5, tzinfo=UTC))
CHIUSO = (datetime(2024, 10, 1, tzinfo=UTC), datetime(2026, 10, 1, 5, tzinfo=UTC))
PERIODI = {"azioni": RICERCA, "azioni_allora": RICERCA, "azioni_chiuso": CHIUSO, "azioni_allora_chiuso": CHIUSO}
RISULTATI = Path(__file__).resolve().parents[1] / "prove" / "RINNOVO_AZIONI_risultati.md"


def dividendi_per_anno(simboli: list[str], tipo: str) -> Counter:
    c: Counter = Counter()
    for s in simboli:
        df = archivio.carica(s, tipo)
        if df is not None and not df.empty:
            c.update(d.year for d in df.loc[df["tipo"] == "dividendo", "data"])
    return c


def main() -> str:
    from stock.prove.p027 import aspetta_fuori_dagli_ordini

    radice = archivio.cartella_dati()
    testo = ["# Il rinnovo delle azioni societarie — risultati", "",
             (f"Calcolato da `python -m stock.dati.rinnova_azioni` il {datetime.now(UTC):%Y-%m-%d %H:%M} UTC (lavoro di GitHub). Solo "
              "conteggi dei dividendi per anno di stacco, prima e dopo il rinnovo; niente prezzi."), ""]
    for tipo, (dal, al) in PERIODI.items():
        simboli = sorted(p.parent.name for p in radice.glob(f"*/{tipo}.csv.gz"))
        if not simboli:
            testo.append(f"* `{tipo}`: nessun titolo in archivio.")
            continue
        prima = dividendi_per_anno(simboli, tipo)
        for i in range(0, len(simboli), 500):
            aspetta_fuori_dagli_ordini()
            for s, df in alpaca.azioni_societarie_di_piu(simboli[i:i + 500], dal, al).items():
                archivio.salva(df, s, tipo)
            print(f"{tipo}: {min(i + 500, len(simboli))} su {len(simboli)}", flush=True)
        dopo = dividendi_per_anno(simboli, tipo)
        anni = sorted(set(prima) | set(dopo))
        testo.append(f"* `{tipo}` ({len(simboli)} titoli, dal {dal.date()} al {al.date()}): "
                     + "; ".join(f"{a}: {prima.get(a, 0)} → {dopo.get(a, 0)}" for a in anni) + ".")
    t = "\n".join(testo) + "\n"
    RISULTATI.write_text(t)
    return t


if __name__ == "__main__":
    print(main())
