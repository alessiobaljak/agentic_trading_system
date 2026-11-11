"""Pubblica la misura in avanti sulla Plancia: Firebase Realtime Database, sotto `/azioni` (forma in dashboard/GUIDA_SCHEDA_AZIONI.md).

Chi scrive e con quali permessi è in `stock/avanti/FIREBASE.md`. Le credenziali si leggono solo dall'ambiente e non si scrivono mai:
`AZIONI_FIREBASE_URL` (l'indirizzo del database), `AZIONI_FIREBASE_API_KEY` (la chiave web del progetto), `AZIONI_FIREBASE_EMAIL` e
`AZIONI_FIREBASE_PASSWORD` (l'utente dedicato alle azioni, che le regole fanno scrivere solo sotto `/azioni`). Senza credenziali non
pubblica e lo dice: la misura in avanti va avanti lo stesso.

    python -m stock.avanti.plancia          # pubblica adesso
    python -m stock.avanti.plancia --prova  # stampa quello che pubblicherebbe, senza scrivere
"""
from __future__ import annotations

import json
import math
import os
import sys
import time
from pathlib import Path

import pandas as pd
import requests

from stock.avanti import avanti as av

ID = "prima_candela_15m"
PRIMO_GIORNO = "2026-11-09"
CAPITALE = 100_000.0
FUSO = "Europe/Zurich"
SOGLIA_BATTITO_S = 100 * 3600        # si pubblica nei giorni di borsa: un fine settimana con un giorno di festa sta sotto le 100 ore
GIORNI_OPERAZIONI = 30


def chiave(simbolo: str) -> str:
    """Firebase non accetta . # $ [ ] / nelle chiavi: BRK.B -> BRK_B (la scheda rimette il punto)."""
    for c in ".#$[]/":
        simbolo = simbolo.replace(c, "_")
    return simbolo


def _numero(x) -> float | None:
    try:
        x = float(x)
    except (TypeError, ValueError):
        return None
    return None if math.isnan(x) or math.isinf(x) else x


def giorni_dal_conto(storia: dict) -> dict[str, float]:
    """Il valore del conto a fine giorno, dai dati di Alpaca (timestamp in secondi, equity), dal primo giorno della misura."""
    out = {}
    for t, v in zip(storia.get("timestamp") or [], storia.get("equity") or []):
        v = _numero(v)
        if v is None or v <= 0:
            continue
        g = pd.Timestamp(t, unit="s", tz="UTC").tz_convert(av.NY).date().isoformat()
        if g >= PRIMO_GIORNO:
            out[g] = round(v, 2)
    return out


def operazioni_recenti(diario: pd.DataFrame) -> dict[str, list[dict]]:
    if diario.empty:
        return {}
    giorni = sorted(diario["giorno"].unique())[-GIORNI_OPERAZIONI:]
    out = {}
    for g in giorni:
        righe = []
        for r in diario[diario["giorno"] == g].itertuples():
            righe.append({k: v for k, v in {
                "simbolo": r.simbolo, "lato": r.lato if isinstance(r.lato, str) else "",
                "quantita": _numero(r.quantita), "ingresso": _numero(r.ingresso), "uscita_prezzo": _numero(r.uscita_prezzo),
                "uscita": r.uscita if isinstance(r.uscita, str) else "", "guadagno": _numero(r.guadagno),
                "proporzione": _numero(r.proporzione), "commissione_ib": _numero(r.commissione_ib),
                "nota": r.nota if isinstance(r.nota, str) else "",
                "ora_ingresso": r.ora_ingresso if isinstance(r.ora_ingresso, str) else "",
            }.items() if v is not None and v != ""})
        out[g] = righe
    return out


def componi(conto: dict, posizioni: list[dict], storia: dict, diario: pd.DataFrame, ordini_oggi: dict | None,
            adesso: float, allarmi: dict | None = None) -> dict:
    """L'oggetto da scrivere sotto /azioni (funzione pura, provata da stock/tests/test_avanti.py)."""
    valore = _numero(conto.get("equity")) or 0.0
    pesi = {}
    for p in posizioni:
        mv = _numero(p.get("market_value"))
        if mv and valore:
            pesi[chiave(p["symbol"])] = round(mv / valore, 4)       # Alpaca dà il valore negativo per le vendute
    giorni = giorni_dal_conto(storia)
    # lo storico di Alpaca arriva con un giorno di ritardo: a posizioni chiuse, il valore di adesso è quello di fine dell'ultimo giorno
    if not diario.empty and not posizioni and valore:
        ultimo = str(diario["giorno"].max())
        giorni.setdefault(ultimo, round(valore, 2))
    a = av.riassunto(diario) if not diario.empty else None
    descrizione = ("La direzione dei primi 15 minuti sulle 10 azioni americane più scambiate del mese; stop e obiettivo fissi, "
                   "tutto chiuso a fine giornata.")
    if a and a["operazioni"]:
        descrizione += (f" Finora {a['operazioni']} operazioni, {a['in_guadagno']:.0%} in guadagno, media {a['media']:+.2%} "
                        f"(t {a['t']:.1f}).")
    strategia = {
        "nome": "Prima candela 15 minuti", "descrizione": descrizione, "tipo": "demo", "ordine": 1, "valuta": "USD",
        "capitale": CAPITALE, "valore": round(valore, 2), "rendimento": round(valore / CAPITALE - 1, 6),
        "comprate": sum(1 for p in posizioni if (_numero(p.get("qty")) or 0) > 0),
        "vendute": sum(1 for p in posizioni if (_numero(p.get("qty")) or 0) < 0),
        "pesi": pesi or None, "aggiornato": int(adesso), "giorni": giorni or None,
        "primo_giorno_dal_capitale": True, "operazioni": operazioni_recenti(diario) or None,
    }
    if ordini_oggi:
        inviati = [o for o in ordini_oggi.get("ordini", []) if o.get("inviato")]
        if inviati:
            ora = pd.Timestamp(min(o["inviato"] for o in inviati)).timestamp()
            uscite = int((diario["giorno"] == ordini_oggi["giorno"]).sum()) if not diario.empty else 0
            strategia["ultimo_ribilancio"] = {"ora": int(ora), "entrate": len(inviati),
                                              "uscite": uscite if uscite and not posizioni else 0}
    return {"battito": int(adesso), "soglia_battito_s": SOGLIA_BATTITO_S, "strategie": {ID: strategia}, "allarmi": allarmi or None}


def raccogli(allarmi: dict | None = None) -> dict:
    conto = av._richiesta("GET", "/v2/account")
    posizioni = av._richiesta("GET", "/v2/positions")
    storia = av._richiesta("GET", "/v2/account/portfolio/history", params={"period": "3M", "timeframe": "1D"})
    f = av.QUI / "diario.csv"
    diario = pd.read_csv(f) if f.exists() else pd.DataFrame(columns=av.COLONNE)
    oggi = av.ny_adesso().date().isoformat()
    fo = av.QUI / "giorni" / f"{oggi}.json"
    ordini = json.loads(fo.read_text()) if fo.exists() else None
    return componi(conto, posizioni, storia, diario, ordini, time.time(), allarmi)


def _credenziali() -> dict | None:
    nomi = ("AZIONI_FIREBASE_URL", "AZIONI_FIREBASE_API_KEY", "AZIONI_FIREBASE_EMAIL", "AZIONI_FIREBASE_PASSWORD")
    valori = {n: os.environ.get(n, "") for n in nomi}
    return valori if all(valori.values()) else None


def pubblica(allarmi: dict | None = None) -> str:
    cred = _credenziali()
    if cred is None:
        return "Plancia: credenziali di Firebase mancanti nell'ambiente, niente pubblicato (stock/avanti/FIREBASE.md)"
    dati = raccogli(allarmi)
    r = requests.post("https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword",
                      params={"key": cred["AZIONI_FIREBASE_API_KEY"]},
                      json={"email": cred["AZIONI_FIREBASE_EMAIL"], "password": cred["AZIONI_FIREBASE_PASSWORD"],
                            "returnSecureToken": True}, timeout=30)
    if r.status_code != 200:
        return f"Plancia: accesso a Firebase rifiutato ({r.status_code}), niente pubblicato"
    token = r.json()["idToken"]
    url = cred["AZIONI_FIREBASE_URL"].rstrip("/")
    w = requests.put(f"{url}/azioni.json", params={"auth": token}, json=dati, timeout=30)
    if w.status_code != 200:
        return f"Plancia: scrittura su /azioni rifiutata ({w.status_code}: {w.text[:120]})"
    s = dati["strategie"][ID]
    return f"Plancia: pubblicato /azioni (valore {s['valore']:,.2f} dollari, {len(s.get('giorni') or {})} giorni)"


if __name__ == "__main__":
    if "--prova" in sys.argv:
        print(json.dumps(raccogli(), indent=1, ensure_ascii=False)[:3000])
    else:
        print(pubblica())
