"""Il conto demo condiviso fra la prima candela e la miscela (decisione del proprietario, 12 novembre 2026: «per la miscela [...] usa
quello attuale»). Le due strategie stanno nello stesso conto di Alpaca ma non si toccano: si dividono per **titolo** (la miscela
compra solo SPY e QQQ, che non sono mai fra le azioni della prima candela) e ognuna ha il suo **capitale virtuale** di 100'000 dollari,
su cui calcola le quantità e il rendimento. Il conto vero ha quindi fino a circa il doppio dell'esposizione del suo valore: è solo il
contenitore; il risultato di ciascuna si legge sul suo capitale.

La contabilità: alla partenza della miscela si fotografa il valore del conto (`conto_condiviso.json`). Da lì il guadagno della prima
candela è la somma del suo diario (ogni sera è senza posizioni) più il non realizzato dei suoi titoli; tutto il resto della variazione
del conto è della miscela. I valori di fine giornata delle due stanno in `valori.csv` (numeri nostri, non prezzi di borsa).
"""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

QUI = Path(__file__).resolve().parent
STATO = QUI / "conto_condiviso.json"
VALORI = QUI / "valori.csv"
SIMBOLI_MISCELA = ("SPY", "QQQ")
CAPITALE_MISCELA = 100_000.0
COLONNE = ["giorno", "conto", "prima_candela", "miscela"]


def della_miscela(simbolo: str) -> bool:
    return simbolo in SIMBOLI_MISCELA


def separa(posizioni: list[dict]) -> tuple[list[dict], list[dict]]:
    """(posizioni della prima candela, posizioni della miscela)."""
    return ([p for p in posizioni if not della_miscela(p["symbol"])], [p for p in posizioni if della_miscela(p["symbol"])])


def leggi_stato() -> dict | None:
    return json.loads(STATO.read_text()) if STATO.exists() else None


def valori(equity: float, posizioni: list[dict], diario: pd.DataFrame, stato: dict | None, oggi: str | None = None,
           esecuzioni_oggi: list[dict] | None = None) -> tuple[float, float | None]:
    """(valore della prima candela, valore della miscela o None se la miscela non è partita). Funzione pura.

    Il guadagno della prima candela dopo la partenza: il suo diario; per oggi, se il diario non è ancora scritto, i soldi usciti ed
    entrati con le sue esecuzioni di oggi più il valore di mercato delle sue posizioni (parte ogni giorno senza posizioni, quindi è
    il guadagno di oggi, comprese le uscite a stop già avvenute)."""
    if stato is None:
        return float(equity), None
    candela_pos, _ = separa(posizioni)
    giorni = diario["giorno"].astype(str) if len(diario) else pd.Series(dtype=str)
    dopo = diario[giorni > stato["dal"]] if len(diario) else diario
    realizzato = float(pd.to_numeric(dopo["guadagno"], errors="coerce").dropna().sum()) if len(dopo) else 0.0
    if oggi is not None and esecuzioni_oggi is not None and oggi > stato["dal"] and oggi not in set(giorni):
        flusso = sum((1 if str(e["side"]).startswith("sell") else -1) * float(e["qty"]) * float(e["price"])
                     for e in esecuzioni_oggi if not della_miscela(e["symbol"]))
        di_oggi = flusso + sum(float(p.get("market_value") or 0.0) for p in candela_pos)
    else:
        di_oggi = sum(float(p.get("unrealized_pl") or 0.0) for p in candela_pos)
    candela = stato["candela_alla_partenza"] + realizzato + di_oggi
    miscela = CAPITALE_MISCELA + (float(equity) - stato["conto_alla_partenza"]) - (candela - stato["candela_alla_partenza"])
    return float(candela), float(miscela)


def adesso() -> dict:
    """I valori di adesso letti dal conto: {conto, candela, miscela, posizioni_candela, posizioni_miscela}."""
    from stock.avanti import avanti as av
    conto = av._richiesta("GET", "/v2/account")
    posizioni = av._richiesta("GET", "/v2/positions")
    f = QUI / "diario.csv"
    diario = pd.read_csv(f) if f.exists() else pd.DataFrame(columns=av.COLONNE)
    equity = float(conto["equity"])
    stato = leggi_stato()
    oggi = av.ny_adesso().date().isoformat()
    esecuzioni = av.esecuzioni_del_giorno(oggi) if stato is not None else None
    candela, miscela = valori(equity, posizioni, diario, stato, oggi, esecuzioni)
    pc, pm = separa(posizioni)
    return {"conto": equity, "candela": candela, "miscela": miscela, "posizioni_candela": pc, "posizioni_miscela": pm,
            "moltiplicatore": conto.get("multiplier"), "potere_d_acquisto": conto.get("buying_power")}


def parti(giorno: str) -> dict:
    """La fotografia della partenza della miscela: si fa una volta, a prima candela senza posizioni."""
    stato = leggi_stato()
    if stato is not None:
        return stato
    v = adesso()
    if v["posizioni_candela"]:
        raise RuntimeError("la miscela non può partire mentre la prima candela ha posizioni aperte")
    stato = {"dal": giorno, "conto_alla_partenza": v["conto"], "candela_alla_partenza": v["conto"],
             "miscela_alla_partenza": CAPITALE_MISCELA}
    STATO.write_text(json.dumps(stato, indent=1))
    return stato


def leggi_valori() -> pd.DataFrame:
    return pd.read_csv(VALORI) if VALORI.exists() else pd.DataFrame(columns=COLONNE)


def registra(giorno: str) -> str:
    """Scrive la riga di fine giornata, una volta sola per giorno e solo a prima candela senza posizioni."""
    df = leggi_valori()
    if giorno in set(df["giorno"].astype(str)):
        return f"valori del {giorno} già scritti"
    v = adesso()
    if v["posizioni_candela"]:
        return f"valori del {giorno} non scritti: la prima candela ha ancora posizioni"
    riga = {"giorno": giorno, "conto": round(v["conto"], 2), "prima_candela": round(v["candela"], 2),
            "miscela": round(v["miscela"], 2) if v["miscela"] is not None else ""}
    pd.concat([df, pd.DataFrame([riga], columns=COLONNE)], ignore_index=True).to_csv(VALORI, index=False)
    return f"valori del {giorno}: prima candela {riga['prima_candela']}, miscela {riga['miscela'] or '—'}"


def giorni(colonna: str) -> dict[str, float]:
    df = leggi_valori()
    x = pd.to_numeric(df[colonna], errors="coerce")
    return {str(g): float(v) for g, v in zip(df["giorno"], x) if pd.notna(v)}
