"""L'universo «di allora» (`METODO.md`, sezione 2, approvata il 24 ottobre 2026).

In ogni mese, le 10 azioni con più dollari scambiati nei 3 mesi prima (63 giorni di borsa), scelte fra
quelle che erano nell'S&P 500 l'ultimo giorno del mese prima. Regole scritte prima del calcolo:

* **Dollari scambiati** = chiusura × volume, sui prezzi NON rettificati (il prodotto non cambia con i
  frazionamenti), media dei 63 giorni di borsa che finiscono l'ultimo giorno del mese prima.
* Serve la storia completa dei 63 giorni: un titolo con meno giorni non entra in quel mese.
* **Una sola classe di azioni per azienda** (GOOG e GOOGL sono la stessa azienda): resta quella con più
  dollari scambiati (`STESSA_AZIENDA`).
* La composizione dell'indice viene da https://github.com/fja05680/sp500 («S&P 500 Historical
  Components & Changes (Updated).csv»), con i simboli di allora (FB prima del 2022, non META). I prezzi
  da Alpaca, che ha anche i titoli tolti dal listino.

    python -m stock.universo.costruisci --composizione <file csv> [--dal 2016-04 --al 2024-12]
"""
from __future__ import annotations

import argparse
import csv
from datetime import UTC, date, datetime
from pathlib import Path

import pandas as pd

from stock.dati import alpaca, archivio
from stock.dati.controlli import date_ny

GIORNI = 63
QUANTI = 10
STESSA_AZIENDA = {"GOOG": "GOOGL", "FOX": "FOXA", "NWS": "NWSA", "DISCK": "DISCA", "DISCB": "DISCA",
                  "UA": "UAA", "BRK.A": "BRK.B", "LEN.B": "LEN", "HEI.A": "HEI"}
QUI = Path(__file__).resolve().parent


def carica_composizione(percorso) -> list[tuple[date, frozenset]]:
    csv.field_size_limit(10 ** 9)
    with open(percorso) as fh:
        righe = [(date.fromisoformat(r["date"]), frozenset(t for t in r["tickers"].split(",") if t))
                 for r in csv.DictReader(fh)]
    return sorted(righe)


def membri_al(composizione, giorno: date) -> frozenset:
    """L'elenco in vigore in quel giorno: l'ultimo con data non successiva."""
    ultimo = None
    for d, m in composizione:
        if d > giorno:
            break
        ultimo = m
    if ultimo is None:
        raise ValueError(f"nessuna composizione prima del {giorno}")
    return ultimo


def dollari_giornalieri(df: pd.DataFrame) -> pd.Series:
    """Dollari scambiati per giorno di New York."""
    return pd.Series((df["close"] * df["volume"]).to_numpy(), index=pd.Index(date_ny(df.index)))


def dieci_di_allora(dollari: dict[str, pd.Series], composizione, giorni_borsa: list[date],
                    mesi: list[pd.Period]) -> pd.DataFrame:
    """Per ogni mese: le `QUANTI` con più dollari medi nei `GIORNI` giorni di borsa prima del mese.
    `giorni_borsa` è il calendario. Restituisce mese, posizione (1 = la più scambiata), simbolo."""
    out = []
    giorni_borsa = sorted(giorni_borsa)
    for m in mesi:
        primo = m.start_time.date()
        prima = [g for g in giorni_borsa if g < primo]
        if len(prima) < GIORNI:
            continue
        finestra = prima[-GIORNI:]
        membri = membri_al(composizione, finestra[-1])
        medie = {}
        for t in membri:
            s = dollari.get(t)
            if s is None:
                continue
            v = s.reindex(finestra)
            if v.isna().any():
                continue
            medie[t] = float(v.mean())
        migliori: dict[str, tuple[str, float]] = {}
        for t, v in medie.items():
            chiave = STESSA_AZIENDA.get(t, t)
            if chiave not in migliori or v > migliori[chiave][1]:
                migliori[chiave] = (t, v)
        scelti = sorted(migliori.values(), key=lambda x: -x[1])[:QUANTI]
        out += [{"mese": str(m), "posizione": i + 1, "simbolo": t} for i, (t, _) in enumerate(scelti)]
    return pd.DataFrame(out, columns=["mese", "posizione", "simbolo"])


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--composizione", required=True)
    ap.add_argument("--dal", default="2016-04")
    ap.add_argument("--al", default="2024-12")
    a = ap.parse_args(argv)
    comp = carica_composizione(a.composizione)
    inizio = datetime(2016, 1, 1, 5, tzinfo=UTC)
    fine = datetime(2025, 1, 1, 5, tzinfo=UTC)          # il periodo chiuso (dal 2025) non si scarica
    tutti = sorted(set().union(*[m for d, m in comp if date(2015, 9, 1) <= d <= date(2024, 12, 31)]))
    dollari, vuoti = {}, []
    for i, t in enumerate(tutti):
        df = archivio.carica(t, "1Day_raw")
        if df is None:
            df = alpaca.barre(t, "1Day", inizio, fine)
            archivio.salva(df, t, "1Day_raw")
        if df.empty:
            vuoti.append(t)
            continue
        dollari[t] = dollari_giornalieri(df)
        if i % 100 == 0:
            print(f"{i}/{len(tutti)}", flush=True)
    cal = alpaca.calendario("2016-01-01", "2024-12-31")
    mesi = list(pd.period_range(a.dal, a.al, freq="M"))
    u = dieci_di_allora(dollari, comp, list(cal.index), mesi)
    u.to_csv(QUI / "dieci_di_allora.csv", index=False)
    conteggio = u["simbolo"].value_counts()
    righe = ["# L'universo «di allora»", "",
             f"Scritto da `python -m stock.universo.costruisci` il {datetime.now(UTC):%Y-%m-%d %H:%M} UTC. Regole nel file del "
             "programma. Elenco mese per mese in `dieci_di_allora.csv`.", "",
             f"* Mesi: {u['mese'].nunique()} (dal {a.dal} al {a.al}); simboli dell'indice nel periodo: {len(tutti)}; "
             f"senza nessun prezzo su Alpaca: {len(vuoti)}.",
             f"* Titoli entrati almeno una volta fra i 10: {len(conteggio)}.", "",
             "| Simbolo | Mesi fra i 10 |", "|---|---|"] + [f"| {t} | {n} |" for t, n in conteggio.items()]
    righe += ["", "## Simboli dell'indice senza prezzi su Alpaca", "", ", ".join(vuoti) or "Nessuno."]
    (QUI / "ESITO_UNIVERSO.md").write_text("\n".join(righe) + "\n")
    print("\n".join(righe))


if __name__ == "__main__":
    main()
