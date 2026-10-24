"""I dividendi che mancano ad Alpaca, presi da una seconda fonte e scritti a mano con la fonte.

Il 24 ottobre 2026 il confronto fra Alpaca e Yahoo (grafico mensile con gli eventi, 2016-2024, 12
titoli; `stock/dati/ESITO_DIVIDENDI.md`) ha trovato che allo SPY mancano 3 dividendi su 36. Le due
fonti coincidono sugli altri 33 entro lo 0,3%. Yahoo non è perfetto: gli manca il dividendo di QQQ del
21 settembre 2020 e ha due importi di AVGO del 2018 sbagliati di un fattore 2. Per questo si aggiunge
solo ciò che manca ad Alpaca, uno per uno, e non si sostituisce una fonte con l'altra.
"""
from __future__ import annotations

from datetime import date

import pandas as pd

FONTE_YAHOO = "Yahoo, query1.finance.yahoo.com/v8/finance/chart/SPY (events=div), letto il 24 ott 2026"

# (giorno di stacco, dollari per azione, fonte, nota)
DIVIDENDI_AGGIUNTI: dict[str, list[tuple[date, float, str, str]]] = {
    "SPY": [
        (date(2016, 3, 18), 1.05, FONTE_YAHOO, "manca anche nei prezzi rettificati di Alpaca"),
        (date(2018, 6, 15), 1.246, FONTE_YAHOO, "manca anche nei prezzi rettificati di Alpaca"),
        (date(2024, 12, 20), 1.966, FONTE_YAHOO,
         "c'è nei prezzi rettificati di Alpaca (passo dello 0,336%, circa 1,97 dollari): due fonti d'accordo"),
        (date(2026, 9, 18), 1.889, FONTE_YAHOO,
         "trovato nel controllo dei prezzi del periodo chiuso, prima del calcolo della prova 2"),
    ],
    "QQQ": [
        (date(2026, 9, 21), 0.751, "Yahoo, query1.finance.yahoo.com/v8/finance/chart/QQQ (events=div), letto il 24 ott 2026",
         "trovato nel controllo dei prezzi del periodo chiuso, prima del calcolo della prova 2"),
    ],
}


def azioni_complete(simbolo: str, azioni: pd.DataFrame) -> pd.DataFrame:
    """Le azioni societarie di Alpaca più i dividendi aggiunti a mano (solo i giorni che mancano)."""
    aggiunti = DIVIDENDI_AGGIUNTI.get(simbolo, [])
    gia = set(azioni.loc[azioni["tipo"] == "dividendo", "data"]) if not azioni.empty else set()
    righe = [{"data": d, "tipo": "dividendo", "rapporto": 1.0, "importo": x} for d, x, _, _ in aggiunti if d not in gia]
    if not righe:
        return azioni
    out = pd.concat([azioni, pd.DataFrame(righe)], ignore_index=True)
    return out.sort_values(["data", "tipo"]).reset_index(drop=True)


def confronta_dividendi(nostri: pd.DataFrame, altri: dict[date, float], frazionamenti_altri: dict[date, float],
                        tolleranza: float = 0.01) -> list[dict]:
    """Confronta i dividendi di Alpaca (importi di allora) con quelli di un'altra fonte che li divide per
    i frazionamenti successivi (come Yahoo). Gli importi dell'altra fonte si riportano a quelli di
    allora moltiplicandoli per i frazionamenti con data successiva. Restituisce le differenze: giorno,
    importo nostro, importo dell'altra fonte riportato, tipo («manca a noi», «manca a loro»,
    «importo diverso»)."""
    nostri_d = dict(zip(nostri.loc[nostri["tipo"] == "dividendo", "data"], nostri.loc[nostri["tipo"] == "dividendo", "importo"]))

    def riportato(d, x):
        f = 1.0
        for ds, r in frazionamenti_altri.items():
            if ds > d:
                f *= r
        return x * f

    out = []
    for d in sorted(set(nostri_d) | set(altri)):
        a = nostri_d.get(d)
        b = riportato(d, altri[d]) if d in altri else None
        if a is None:
            out.append({"data": d, "nostro": None, "altro": b, "tipo": "manca a noi"})
        elif b is None:
            out.append({"data": d, "nostro": a, "altro": None, "tipo": "manca a loro"})
        elif abs(a - b) > tolleranza * max(abs(a), 1e-9):
            out.append({"data": d, "nostro": a, "altro": b, "tipo": "importo diverso"})
    return out


def valuta_scissioni(azioni: pd.DataFrame, apertura) -> tuple[pd.DataFrame, list[str]]:
    """Le scissioni diventano un incasso in contanti il giorno di stacco: rapporto × apertura del titolo
    nuovo quel giorno (chi le riceve potrebbe venderle subito). `apertura(simbolo, giorno)` restituisce
    il prezzo o None. Restituisce le azioni societarie con le scissioni trasformate in dividendi, e
    l'elenco di quelle senza prezzo (che restano fuori e vanno dette)."""
    if azioni.empty or "nuovo" not in azioni or not (azioni["tipo"] == "scissione").any():
        return azioni, []
    righe, mancanti = [], []
    for _, a in azioni.iterrows():
        if a["tipo"] != "scissione":
            righe.append(a.to_dict())
            continue
        p = apertura(a["nuovo"], a["data"])
        if p is None:
            mancanti.append(f"{a['data']} {a['nuovo']}")
            continue
        righe.append({"data": a["data"], "tipo": "dividendo", "rapporto": 1.0, "importo": float(a["rapporto"]) * p,
                      "nuovo": a["nuovo"]})
    return pd.DataFrame(righe).sort_values(["data", "tipo"]).reset_index(drop=True), mancanti
