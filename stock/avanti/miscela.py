"""La miscela sul conto demo (`stock/avanti/MISCELA.md`): un sesto del capitale a ciascuna delle regole delle prove 7, 15 e 16, su SPY e
QQQ, in un conto demo di Alpaca suo. Le regole sono quelle scritte nelle prove, senza numeri nuovi.

    python -m stock.avanti.miscela sera   # dopo la chiusura: decisioni della settimana e del mese, ordini per l'apertura di domani
    python -m stock.avanti.miscela fed    # nei giorni della banca centrale: aspetta le 14:00 (vigilia) o le 13:59 (giorno) e compra o vende
    python -m stock.avanti.miscela controlla

Le chiavi sono quelle del conto demo della miscela, passate dal lavoro di GitHub come ALPACA_API_KEY_ID / ALPACA_API_SECRET_KEY.
"""
from __future__ import annotations

import json
import math
import sys
import time
from datetime import date, datetime, timezone

import numpy as np
import pandas as pd

from stock.avanti import avanti as av
from stock.dati import alpaca, fomc

QUI = av.QUI
STATO = QUI / "miscela_stato.json"
DIARIO = QUI / "miscela_diario.csv"
SIMBOLI = ("SPY", "QQQ")
PARTI = 6                      # 3 regole × 2 fondi, un sesto ciascuna
QUOTA = 0.98
SOGLIA = 0.10                  # le regole 15 e 16 non si muovono per meno del 10% della loro parte
COMUNICATI = sorted(set(fomc.COMUNICATI_CHIUSO + fomc.COMUNICATI_AVANTI))
ID = "miscela"


# ---- le regole (funzioni pure, provate da stock/tests/test_avanti.py) ------------------------------------------------

def quota_calma(chiusure: pd.Series) -> float:
    """Prova 15: 16% / volatilità annua delle ultime 21 sedute, fra 0 e 1,5."""
    r = chiusure.iloc[-22:].pct_change().dropna()
    v = float(r.std(ddof=1) * math.sqrt(252))
    return float(min(max(0.16 / v, 0.0), 1.5)) if v > 0 else 1.5


def ampiezza(chiusure: dict[str, pd.Series]) -> float:
    """Prova 16: la quota dei titoli con almeno 200 chiusure che chiudono sopra la loro media di 200 sedute."""
    sopra = n = 0
    for c in chiusure.values():
        if len(c) >= 200:
            n += 1
            sopra += int(c.iloc[-1] > c.iloc[-200:].mean())
    return sopra / n if n else float("nan")


def giorni_fed(oggi: date, calendario: list[date]) -> str | None:
    """Prova 7: «vigilia» se domani di borsa c'è il comunicato (si compra alle 14:00), «giorno» se c'è oggi (si vende alle 13:59)."""
    if oggi in COMUNICATI:
        return "giorno"
    dopo = [d for d in calendario if d > oggi]
    if dopo and dopo[0] in COMUNICATI:
        return "vigilia"
    return None


def esposizione(stato: dict) -> dict[str, float]:
    """La frazione del conto per fondo: la media delle tre regole, ognuna con un sesto del capitale per fondo."""
    return {s: (stato["fed"] * QUOTA + stato["calma"][s] * QUOTA + stato["ampiezza"]) / PARTI for s in SIMBOLI}


def ordini(valore: float, esp: dict[str, float], prezzi: dict[str, float], posizioni: dict[str, float]) -> dict[str, int]:
    """Le azioni da comprare (+) o vendere (−) per arrivare all'esposizione; niente ordini sotto il 10% di una parte."""
    out = {}
    for s in SIMBOLI:
        voluto = int(valore * esp[s] / prezzi[s])
        d = voluto - int(posizioni.get(s, 0))
        if d and (abs(d) * prezzi[s] >= SOGLIA * valore / PARTI or voluto == 0):
            out[s] = d
    return out


# ---- il conto -------------------------------------------------------------------------------------------------------

def leggi_stato() -> dict:
    if STATO.exists():
        return json.loads(STATO.read_text())
    return {"fed": 0.0, "calma": {s: 0.0 for s in SIMBOLI}, "ampiezza": 0.0, "ultima_sera": None}


def scrivi_stato(stato: dict) -> None:
    STATO.write_text(json.dumps(stato, indent=1, ensure_ascii=False))


def annota(riga: dict) -> None:
    df = pd.DataFrame([riga])
    df.to_csv(DIARIO, mode="a", header=not DIARIO.exists(), index=False)


def chiusure_rettificate(simboli: list[str], giorni: int) -> dict[str, pd.Series]:
    fine = datetime.now(timezone.utc)
    inizio = (pd.Timestamp(fine) - pd.Timedelta(days=giorni)).to_pydatetime()
    out = {}
    for i in range(0, len(simboli), 100):
        for s, df in alpaca.barre_di_piu(simboli[i:i + 100], "1Day", inizio, fine, rettifica="all").items():
            if not df.empty:
                out[s] = df["close"]
    return out


def calendario_da(oggi: date) -> list[date]:
    cal = av._richiesta("GET", "/v2/calendar", params={"start": oggi.isoformat(), "end": (oggi + pd.Timedelta(days=40)).date().isoformat()})
    return [date.fromisoformat(c["date"]) for c in cal]


def manda(diff: dict[str, int], tif: str) -> list[str]:
    fatti = []
    for s, q in diff.items():
        corpo = {"symbol": s, "qty": str(abs(q)), "side": "buy" if q > 0 else "sell", "type": "market", "time_in_force": tif}
        o = av._richiesta("POST", "/v2/orders", json=corpo)
        fatti.append(f"{s} {q:+d} ({o.get('status')})")
    return fatti


def posizioni() -> dict[str, float]:
    return {p["symbol"]: float(p["qty"]) for p in av._richiesta("GET", "/v2/positions")}


def sera() -> str:
    """Dopo la chiusura: a fine settimana la regola della calma, a fine mese quella dell'ampiezza; ordini all'apertura di domani."""
    oggi = av.ny_adesso().date()
    cal = calendario_da(oggi)
    if not cal or cal[0] != oggi:
        return f"{oggi}: borsa chiusa, niente"
    # Alpaca accetta gli ordini «all'apertura» solo dalle 19:00 di New York in poi: si aspetta le 19:01
    pronto = pd.Timestamp(f"{oggi} 19:01", tz=av.NY)
    attesa = (pronto - av.ny_adesso()).total_seconds()
    if attesa > 3 * 3600:
        return f"{oggi}: troppo presto, la sera si decide dopo le 19:00 di New York"
    if attesa > 0:
        time.sleep(attesa)
    stato = leggi_stato()
    if stato.get("ultima_sera") == oggi.isoformat():
        return f"{oggi}: la sera di oggi è già fatta"
    domani = cal[1] if len(cal) > 1 else None
    note = []
    fine_settimana = domani is None or domani.isocalendar()[1] != oggi.isocalendar()[1]
    fine_mese = domani is None or domani.month != oggi.month
    primo_giro = stato.get("ultima_sera") is None
    ch = chiusure_rettificate(list(SIMBOLI), 60)
    if fine_settimana or primo_giro:
        for s in SIMBOLI:
            q = quota_calma(ch[s])
            if abs(q - stato["calma"][s]) * QUOTA > SOGLIA or primo_giro:
                stato["calma"][s] = round(q, 4)
        note.append(f"calma {stato['calma']}")
    if fine_mese or primo_giro:
        membri = pd.read_csv(QUI / "sp500_membri.csv")["simbolo"].tolist()
        a = ampiezza(chiusure_rettificate(membri, 330))
        stato["ampiezza"] = QUOTA if a >= 0.5 else QUOTA / 2
        note.append(f"ampiezza {a:.1%}")
    conto = av._richiesta("GET", "/v2/account")
    valore = float(conto["equity"])
    prezzi = {s: float(ch[s].iloc[-1]) for s in SIMBOLI}
    av._richiesta("DELETE", "/v2/orders")
    diff = ordini(valore, esposizione(stato), prezzi, posizioni())
    fatti = manda(diff, "opg") if diff else []
    stato["ultima_sera"] = oggi.isoformat()
    scrivi_stato(stato)
    annota({"giorno": oggi.isoformat(), "comando": "sera", "valore": round(valore, 2), "fed": stato["fed"],
            "calma_SPY": stato["calma"]["SPY"], "calma_QQQ": stato["calma"]["QQQ"], "ampiezza": stato["ampiezza"],
            "ordini": "; ".join(fatti), "note": "; ".join(note)})
    print(pubblica())
    return f"{oggi}: sera fatta ({'; '.join(note) or 'nessuna decisione nuova'}); ordini per l'apertura: {', '.join(fatti) or 'nessuno'}"


def fed() -> str:
    """Prova 7: alla vigilia del comunicato si compra alle 14:00, il giorno del comunicato si vende alle 13:59 (prima delle 14:00)."""
    oggi = av.ny_adesso().date()
    cal = calendario_da(oggi)
    if not cal or cal[0] != oggi:
        return f"{oggi}: borsa chiusa"
    tipo = giorni_fed(oggi, cal)
    if tipo is None:
        return f"{oggi}: nessun comunicato della banca centrale oggi o domani"
    stato = leggi_stato()
    if (tipo == "vigilia" and stato["fed"] > 0) or (tipo == "giorno" and stato["fed"] == 0):
        return f"{oggi}: la regola della banca centrale è già fatta ({tipo})"
    ora = pd.Timestamp(f"{oggi} {'14:00' if tipo == 'vigilia' else '13:59'}", tz=av.NY)
    attesa = (ora - av.ny_adesso()).total_seconds()
    if attesa > 0:
        time.sleep(attesa)
    elif attesa < -20 * 60:
        return f"{oggi}: troppo tardi per la regola della banca centrale ({tipo}), si salta e si scrive"
    stato["fed"] = 1.0 if tipo == "vigilia" else 0.0
    conto = av._richiesta("GET", "/v2/account")
    valore = float(conto["equity"])
    ultimo = {s: float(alpaca._get(f"{alpaca.DATI_URL}/v2/stocks/{s}/trades/latest", {"feed": "iex"})["trade"]["p"])
              for s in SIMBOLI}
    diff = ordini(valore, esposizione(stato), ultimo, posizioni())
    fatti = manda(diff, "day") if diff else []
    scrivi_stato(stato)
    annota({"giorno": oggi.isoformat(), "comando": f"fed {tipo}", "valore": round(valore, 2), "fed": stato["fed"],
            "calma_SPY": stato["calma"]["SPY"], "calma_QQQ": stato["calma"]["QQQ"], "ampiezza": stato["ampiezza"],
            "ordini": "; ".join(fatti), "note": f"alle {av.ny_adesso():%H:%M:%S} di New York"})
    print(pubblica())
    return f"{oggi}: banca centrale ({tipo}) fatta alle {av.ny_adesso():%H:%M}: {', '.join(fatti) or 'nessun ordine'}"


def pubblica() -> str:
    try:
        from stock.avanti import plancia
        conto = av._richiesta("GET", "/v2/account")
        pos = av._richiesta("GET", "/v2/positions")
        storia = av._richiesta("GET", "/v2/account/portfolio/history", params={"period": "3M", "timeframe": "1D"})
        valore = float(conto["equity"])
        giorni = {}
        for t, v in zip(storia.get("timestamp") or [], storia.get("equity") or []):
            if v and v > 0:
                giorni[pd.Timestamp(t, unit="s", tz="UTC").tz_convert(av.NY).date().isoformat()] = round(float(v), 2)
        capitale = float(next(iter(giorni.values()), valore)) if giorni else valore
        adesso = int(time.time())
        s = {"nome": "Miscela (banca centrale, calma, ampiezza)", "tipo": "demo", "ordine": 2, "valuta": "USD",
             "descrizione": "Un sesto del capitale a ciascuna di tre regole su SPY e QQQ: prima della banca centrale, più investiti "
                            "con il mercato calmo, metà fuori quando la salita la fanno in poche.",
             "capitale": capitale, "valore": round(valore, 2), "rendimento": round(valore / capitale - 1, 6),
             "comprate": sum(1 for p in pos if float(p["qty"]) > 0), "vendute": 0, "aggiornato": adesso,
             "pesi": {plancia.chiave(p["symbol"]): round(float(p["market_value"]) / valore, 4) for p in pos} or None,
             "giorni": giorni or None, "primo_giorno_dal_capitale": True}
        errore = plancia.scrivi({"battito": adesso, f"strategie/{ID}": s})
        return errore or f"Plancia: pubblicata la miscela (valore {valore:,.2f} dollari)"
    except Exception as e:  # noqa: BLE001
        return f"Plancia: errore nella pubblicazione della miscela ({type(e).__name__}: {str(e)[:120]})"


if __name__ == "__main__":
    comando = sys.argv[1] if len(sys.argv) > 1 else "controlla"
    funzioni = {"sera": sera, "fed": fed, "controlla": av.controlla, "plancia": pubblica}
    print(funzioni[comando]())
