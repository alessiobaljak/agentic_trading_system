"""Il collegamento ai prezzi di Alpaca (Market Data API v2, piano gratuito).

Le chiavi si leggono SOLO dall'ambiente (`ALPACA_API_KEY_ID`, `ALPACA_API_SECRET_KEY`) e non
si scrivono mai: né in un file, né in un messaggio d'errore, né in un log. Il repository è
pubblico.

Il piano gratuito non dà gli ultimi 15 minuti dei dati di tutte le borse (risposta 403
«subscription does not permit querying recent SIP data», vista il 24 ottobre 2026): la fine
di ogni richiesta viene quindi tirata indietro di 16 minuti rispetto a adesso.
"""
from __future__ import annotations

import os
import time
from datetime import datetime, timedelta, timezone

import pandas as pd
import requests

DATI_URL = "https://data.alpaca.markets"
# l'endpoint del calendario sta sul server del conto demo, non su quello dei dati
DEMO_URL = "https://paper-api.alpaca.markets"
RITARDO_PIANO_GRATUITO = timedelta(minutes=16)
NY = "America/New_York"


class ErroreAlpaca(RuntimeError):
    pass


def _intestazioni() -> dict:
    chiave = os.environ.get("ALPACA_API_KEY_ID", "")
    segreto = os.environ.get("ALPACA_API_SECRET_KEY", "")
    if not chiave or not segreto:
        raise ErroreAlpaca("mancano ALPACA_API_KEY_ID o ALPACA_API_SECRET_KEY nell'ambiente")
    return {"APCA-API-KEY-ID": chiave, "APCA-API-SECRET-KEY": segreto}


def _get(url: str, parametri: dict, tentativi: int = 5) -> dict:
    """Una richiesta GET con i tentativi per il limite di frequenza (429) e gli errori di rete.

    L'errore riporta il codice e il messaggio di Alpaca, mai le intestazioni."""
    attesa = 2.0
    for n in range(tentativi):
        try:
            r = requests.get(url, headers=_intestazioni(), params=parametri, timeout=60)
        except requests.RequestException as e:
            if n == tentativi - 1:
                raise ErroreAlpaca(f"rete: {type(e).__name__}") from None
            time.sleep(attesa)
            attesa *= 2
            continue
        if r.status_code == 200:
            return r.json()
        if r.status_code in (429, 500, 502, 503, 504) and n < tentativi - 1:
            time.sleep(attesa)
            attesa *= 2
            continue
        raise ErroreAlpaca(f"{r.status_code} su {url.split('?')[0]}: {r.text[:200]}")
    raise ErroreAlpaca("tentativi finiti")


def _fine_ammessa(fine: datetime) -> datetime:
    limite = datetime.now(timezone.utc) - RITARDO_PIANO_GRATUITO
    return min(fine, limite)


def _iso(t: datetime) -> str:
    if t.tzinfo is None:
        t = t.replace(tzinfo=timezone.utc)
    return t.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def barre(simbolo: str, timeframe: str, inizio: datetime, fine: datetime,
          rettifica: str = "raw", feed: str = "sip") -> pd.DataFrame:
    """Le barre di un titolo, tutte le pagine.

    `timeframe`: "1Day" o "1Min" (o un altro valore di Alpaca). `rettifica`: "raw" (prezzi come
    erano scambiati), "split" o "all" (frazionamenti e dividendi), come li calcola Alpaca.
    Restituisce le colonne open, high, low, close, volume, n (operazioni), vwap e l'indice `t` in
    UTC. Le barre al minuto comprendono anche le ore fuori dalla seduta (4:00-20:00 di New York).
    """
    fine = _fine_ammessa(fine)
    parametri = {"symbols": simbolo, "timeframe": timeframe, "start": _iso(inizio), "end": _iso(fine),
                 "adjustment": rettifica, "feed": feed, "limit": 10000, "sort": "asc"}
    righe: list[dict] = []
    while True:
        j = _get(f"{DATI_URL}/v2/stocks/bars", parametri)
        righe.extend((j.get("bars") or {}).get(simbolo, []))
        token = j.get("next_page_token")
        if not token:
            break
        parametri["page_token"] = token
    return barre_da_righe(righe)


def barre_da_righe(righe: list[dict]) -> pd.DataFrame:
    colonne = {"o": "open", "h": "high", "l": "low", "c": "close", "v": "volume", "n": "n", "vw": "vwap"}
    if not righe:
        return pd.DataFrame(columns=list(colonne.values()), index=pd.DatetimeIndex([], tz="UTC", name="t"))
    df = pd.DataFrame(righe).rename(columns=colonne)
    df["t"] = pd.to_datetime(df["t"], utc=True)
    return df.set_index("t")[list(colonne.values())]


def quotazioni(simbolo: str, inizio: datetime, fine: datetime, feed: str = "sip",
               massimo: int | None = None) -> pd.DataFrame:
    """Le quotazioni migliori (acquisto e vendita) fra `inizio` e `fine`. Sono moltissime: si
    chiedono solo per finestre brevi, per misurare lo scarto (`stock/dati/scarto.py`)."""
    fine = _fine_ammessa(fine)
    parametri = {"symbols": simbolo, "start": _iso(inizio), "end": _iso(fine), "feed": feed,
                 "limit": 10000, "sort": "asc"}
    righe: list[dict] = []
    while True:
        j = _get(f"{DATI_URL}/v2/stocks/quotes", parametri)
        righe.extend((j.get("quotes") or {}).get(simbolo, []))
        token = j.get("next_page_token")
        if not token or (massimo is not None and len(righe) >= massimo):
            break
        parametri["page_token"] = token
    if not righe:
        return pd.DataFrame(columns=["bid", "ask", "bid_size", "ask_size"],
                            index=pd.DatetimeIndex([], tz="UTC", name="t"))
    df = pd.DataFrame(righe).rename(columns={"bp": "bid", "ap": "ask", "bs": "bid_size", "as": "ask_size"})
    df["t"] = pd.to_datetime(df["t"], utc=True, format="ISO8601")
    return df.set_index("t")[["bid", "ask", "bid_size", "ask_size"]]


def azioni_societarie(simbolo: str, inizio: datetime, fine: datetime) -> pd.DataFrame:
    """Frazionamenti (anche inversi), dividendi in contanti e scissioni, con la data di stacco.

    Colonne: data (giorno di stacco, New York), tipo ("frazionamento", "dividendo" o "scissione"),
    rapporto (azioni nuove per azione vecchia: del titolo stesso per i frazionamenti, del titolo
    nuovo per le scissioni), importo (dollari per azione, solo dividendi), nuovo (il simbolo del
    titolo staccato, solo scissioni). Alpaca accetta al massimo un anno per richiesta: si va a pezzi."""
    righe: list[dict] = []
    da = inizio.date() if isinstance(inizio, datetime) else inizio
    a = fine.date() if isinstance(fine, datetime) else fine
    while da <= a:
        fino = min(a, da + timedelta(days=360))
        parametri = {"symbols": simbolo, "types": "forward_split,reverse_split,cash_dividend,spin_off",
                     "start": da.isoformat(), "end": fino.isoformat(), "limit": 1000}
        while True:
            j = _get(f"{DATI_URL}/v1/corporate-actions", parametri)
            ca = j.get("corporate_actions") or {}
            for chiave in ("forward_splits", "reverse_splits"):
                for x in ca.get(chiave, []):
                    righe.append({"data": x["ex_date"], "tipo": "frazionamento",
                                  "rapporto": float(x["new_rate"]) / float(x["old_rate"]), "importo": 0.0})
            for x in ca.get("cash_dividends", []):
                righe.append({"data": x["ex_date"], "tipo": "dividendo", "rapporto": 1.0,
                              "importo": float(x["rate"])})
            for x in ca.get("spin_offs", []):
                if x.get("source_symbol") != simbolo:
                    continue
                righe.append({"data": x["ex_date"], "tipo": "scissione",
                              "rapporto": float(x["new_rate"]) / float(x["source_rate"]), "importo": 0.0,
                              "nuovo": x["new_symbol"]})
            token = j.get("next_page_token")
            if not token:
                break
            parametri["page_token"] = token
        da = fino + timedelta(days=1)
    df = pd.DataFrame(righe, columns=["data", "tipo", "rapporto", "importo", "nuovo"])
    df["nuovo"] = df["nuovo"].fillna("")
    if not df.empty:
        df["data"] = pd.to_datetime(df["data"]).dt.date
        df = df.drop_duplicates().sort_values(["data", "tipo"]).reset_index(drop=True)
    return df


def calendario(inizio, fine) -> pd.DataFrame:
    """I giorni di borsa americani con l'ora di apertura e di chiusura della seduta (le chiusure
    anticipate, come il giorno dopo il Ringraziamento, chiudono alle 13:00). Indice: la data."""
    j = _get(f"{DEMO_URL}/v2/calendar", {"start": str(inizio)[:10], "end": str(fine)[:10]})
    df = pd.DataFrame(j)
    df["data"] = pd.to_datetime(df["date"]).dt.date
    df["apertura"] = pd.to_datetime(df["date"] + " " + df["open"]).dt.tz_localize(NY)
    df["chiusura"] = pd.to_datetime(df["date"] + " " + df["close"]).dt.tz_localize(NY)
    return df.set_index("data")[["apertura", "chiusura"]]
