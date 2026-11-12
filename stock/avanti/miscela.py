"""La miscela sul conto demo (`stock/avanti/MISCELA.md`): un sesto del capitale a ciascuna delle regole delle prove 7, 15 e 16, su SPY e
QQQ. Sta nello **stesso conto demo** della prima candela (decisione del proprietario, 12 novembre 2026), con il suo capitale virtuale e
i suoi titoli (`stock/avanti/conto.py`). Le regole sono quelle scritte nelle prove, senza numeri nuovi.

    python -m stock.avanti.miscela auto       # tutti gli avvii automatici: guarda l'orologio e fa la cosa giusta per quest'ora
    python -m stock.avanti.miscela controlla

Chi avvia non deve essere puntuale (come `avanti.py`): la decisione della sera si può prendere a qualunque ora fra la chiusura e
l'apertura del giorno dopo (ordini «all'apertura»); la regola della banca centrale aspetta accesa le 14:00 o le 13:59.
"""
from __future__ import annotations

import json
import math
import sys
import time
from datetime import date, datetime, timezone

import pandas as pd

from stock.avanti import avanti as av
from stock.avanti import conto
from stock.dati import alpaca, fomc

QUI = av.QUI
STATO = QUI / "miscela_stato.json"
DIARIO = QUI / "miscela_diario.csv"
SIMBOLI = conto.SIMBOLI_MISCELA
PARTI = 6                      # 3 regole × 2 fondi, un sesto ciascuna
QUOTA = 0.98
SOGLIA = 0.10                  # niente ordini sotto il 10% di una parte
COMUNICATI = sorted(set(fomc.COMUNICATI_CHIUSO + fomc.COMUNICATI_AVANTI))
ID = "miscela"
TOLLERANZA_FED = pd.Timedelta(minutes=20)


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
    """La frazione del capitale per fondo: la media delle tre regole, ognuna con un sesto del capitale per fondo."""
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


def cosa_fare(adesso: pd.Timestamp, sedute: list[dict], stato: dict) -> tuple[str, dict]:
    """(azione, dettagli): «fed», «sera» o «niente: perché». `sedute`: le sedute intorno a oggi (giorno, apertura, chiusura), in
    ordine. Funzione pura: un avvio in anticipo aspetta, un avvio in ritardo non fa mai niente fuori regola."""
    oggi = adesso.date()
    di_oggi = next((s for s in sedute if s["giorno"] == oggi), None)
    if di_oggi is not None:
        tipo = giorni_fed(oggi, [s["giorno"] for s in sedute if s["giorno"] >= oggi])
        fatta = tipo is None or (tipo == "vigilia" and stato["fed"] > 0) or (tipo == "giorno" and stato["fed"] == 0)
        if not fatta:
            ora = pd.Timestamp(f"{oggi} {'14:00' if tipo == 'vigilia' else '13:59'}", tz=av.NY)
            if ora - av.ATTESA_MASSIMA <= adesso <= ora + TOLLERANZA_FED:
                return "fed", {"tipo": tipo, "ora": ora}
            if adesso > ora + TOLLERANZA_FED and adesso < di_oggi["chiusura"]:
                return "niente: troppo tardi per la regola della banca centrale, oggi si salta", {"saltata": tipo}
    if any(s["apertura"] <= adesso < s["chiusura"] for s in sedute):
        return "niente: la borsa è aperta, la sera si decide dopo la chiusura", {}
    chiuse = [s for s in sedute if s["chiusura"] <= adesso]
    prossime = [s for s in sedute if s["apertura"] > adesso]
    if not chiuse or not prossime:
        return "niente: calendario insufficiente", {}
    ultima, prossima = chiuse[-1], prossime[0]
    if stato.get("ultima_sera") == ultima["giorno"].isoformat():
        return "niente: la sera è già fatta", {}
    if adesso > prossima["apertura"] - pd.Timedelta(minutes=5):
        return "niente: troppo tardi per gli ordini all'apertura", {}
    return "sera", {"ultima": ultima, "prossima": prossima}


# ---- il conto -------------------------------------------------------------------------------------------------------

def leggi_stato() -> dict:
    if STATO.exists():
        return json.loads(STATO.read_text())
    return {"fed": 0.0, "calma": {s: 0.0 for s in SIMBOLI}, "ampiezza": 0.0, "ultima_sera": None}


def scrivi_stato(stato: dict) -> None:
    STATO.write_text(json.dumps(stato, indent=1, ensure_ascii=False))


def annota(riga: dict) -> None:
    pd.DataFrame([riga]).to_csv(DIARIO, mode="a", header=not DIARIO.exists(), index=False)


def sedute_intorno() -> list[dict]:
    oggi = av.ny_adesso().date()
    cal = av._richiesta("GET", "/v2/calendar", params={"start": (oggi - pd.Timedelta(days=10)).isoformat(),
                                                       "end": (oggi + pd.Timedelta(days=12)).isoformat()})
    return [{"giorno": date.fromisoformat(c["date"]), "apertura": pd.Timestamp(f"{c['date']} {c['open']}", tz=av.NY),
             "chiusura": pd.Timestamp(f"{c['date']} {c['close']}", tz=av.NY)} for c in cal]


def chiusure_rettificate(simboli: list[str], giorni: int) -> dict[str, pd.Series]:
    fine = datetime.now(timezone.utc)
    inizio = (pd.Timestamp(fine) - pd.Timedelta(days=giorni)).to_pydatetime()
    out = {}
    for i in range(0, len(simboli), 100):
        for s, df in alpaca.barre_di_piu(simboli[i:i + 100], "1Day", inizio, fine, rettifica="all").items():
            if not df.empty:
                out[s] = df["close"]
    return out


def posizioni() -> dict[str, float]:
    return {p["symbol"]: float(p["qty"]) for p in conto.separa(av._richiesta("GET", "/v2/positions"))[1]}


def cancella_ordini() -> None:
    """Cancella gli ordini aperti della miscela (mai quelli della prima candela)."""
    for o in av._richiesta("GET", "/v2/orders", params={"status": "open", "limit": 500}):
        if conto.della_miscela(o["symbol"]):
            try:
                av._richiesta("DELETE", f"/v2/orders/{o['id']}")
            except alpaca.ErroreAlpaca:
                pass
    time.sleep(3)


def manda(diff: dict[str, int], tif: str, nome: str) -> list[str]:
    fatti = []
    for s, q in diff.items():
        corpo = {"symbol": s, "qty": str(abs(q)), "side": "buy" if q > 0 else "sell", "type": "market", "time_in_force": tif,
                 "client_order_id": f"miscela-{nome}-{s}"}      # nome unico: Alpaca rifiuta un doppione
        try:
            o = av._richiesta("POST", "/v2/orders", json=corpo)
            fatti.append(f"{s} {q:+d} ({o.get('status')})")
        except alpaca.ErroreAlpaca as e:
            fatti.append(f"{s} {q:+d} RIFIUTATO ({str(e)[:100]})")
    return fatti


def sera(ultima: dict, prossima: dict) -> str:
    """Dopo la chiusura di `ultima`: a fine settimana la regola della calma, a fine mese quella dell'ampiezza; ordini validi
    all'apertura di `prossima`. Alpaca accetta gli ordini «all'apertura» dalle 19:00 di New York: prima si aspetta."""
    giorno = ultima["giorno"]
    pronto = pd.Timestamp(f"{giorno} 19:01", tz=av.NY)
    attesa = (pronto - av.ny_adesso()).total_seconds()
    if attesa > 0:
        time.sleep(attesa)
    stato = leggi_stato()
    primo_giro = stato.get("ultima_sera") is None
    conto.parti(giorno.isoformat())                # la fotografia della partenza (una volta sola)
    note = []
    fine_settimana = prossima["giorno"].isocalendar()[:2] != giorno.isocalendar()[:2]
    fine_mese = prossima["giorno"].month != giorno.month
    ch = chiusure_rettificate(list(SIMBOLI), 60)
    for s in SIMBOLI:
        if ch[s].index[-1].tz_convert(av.NY).date() != giorno:
            return f"{giorno}: manca la chiusura di oggi di {s} (controllo dei dati), la sera si rifà al prossimo avvio"
    if fine_settimana or primo_giro:
        for s in SIMBOLI:
            q = quota_calma(ch[s])
            if abs(q - stato["calma"][s]) * QUOTA > SOGLIA or primo_giro:
                stato["calma"][s] = round(q, 4)
        note.append(f"calma {stato['calma']}")
    if fine_mese or primo_giro:
        membri = pd.read_csv(QUI / "sp500_membri.csv")["simbolo"].tolist()
        tutte = chiusure_rettificate(membri, 330)
        if len(tutte) < 0.9 * len(membri):         # il controllo dei dati: almeno il 90% dei titoli
            return f"{giorno}: prezzi per {len(tutte)} titoli su {len(membri)} (controllo dei dati), la sera si rifà al prossimo avvio"
        a = ampiezza(tutte)
        stato["ampiezza"] = QUOTA if a >= 0.5 else QUOTA / 2
        note.append(f"ampiezza {a:.1%}")
    valore = conto.adesso()["miscela"]
    prezzi = {s: float(ch[s].iloc[-1]) for s in SIMBOLI}
    cancella_ordini()
    diff = ordini(valore, esposizione(stato), prezzi, posizioni())
    fatti = manda(diff, "opg", f"sera-{giorno}") if diff else []
    stato["ultima_sera"] = giorno.isoformat()
    scrivi_stato(stato)
    annota({"giorno": giorno.isoformat(), "comando": "sera", "valore": round(valore, 2), "fed": stato["fed"],
            "calma_SPY": stato["calma"]["SPY"], "calma_QQQ": stato["calma"]["QQQ"], "ampiezza": stato["ampiezza"],
            "ordini": "; ".join(fatti), "note": "; ".join(note)})
    print(conto.registra(giorno.isoformat()), flush=True)
    print(pubblica())
    return f"{giorno}: sera fatta ({'; '.join(note) or 'nessuna decisione nuova'}); ordini per l'apertura: {', '.join(fatti) or 'nessuno'}"


def fed(tipo: str, ora: pd.Timestamp) -> str:
    """Prova 7: alla vigilia del comunicato si compra alle 14:00, il giorno del comunicato si vende alle 13:59."""
    oggi = av.ny_adesso().date()
    attesa = (ora - av.ny_adesso()).total_seconds()
    if attesa > 0:
        time.sleep(attesa)
    stato = leggi_stato()
    valore = conto.adesso()["miscela"]
    if valore is None:
        return f"{oggi}: la miscela non è ancora partita (serve una sera prima), la regola della banca centrale si salta"
    stato["fed"] = 1.0 if tipo == "vigilia" else 0.0
    ultimo = {s: float(alpaca._get(f"{alpaca.DATI_URL}/v2/stocks/{s}/trades/latest", {"feed": "iex"})["trade"]["p"])
              for s in SIMBOLI}
    diff = ordini(valore, esposizione(stato), ultimo, posizioni())
    fatti = manda(diff, "day", f"fed-{tipo}-{oggi}") if diff else []
    scrivi_stato(stato)
    annota({"giorno": oggi.isoformat(), "comando": f"fed {tipo}", "valore": round(valore, 2), "fed": stato["fed"],
            "calma_SPY": stato["calma"]["SPY"], "calma_QQQ": stato["calma"]["QQQ"], "ampiezza": stato["ampiezza"],
            "ordini": "; ".join(fatti), "note": f"alle {av.ny_adesso():%H:%M:%S} di New York"})
    print(pubblica())
    return f"{oggi}: banca centrale ({tipo}) fatta alle {av.ny_adesso():%H:%M:%S}: {', '.join(fatti) or 'nessun ordine'}"


def auto() -> str:
    adesso = av.ny_adesso()
    azione, d = cosa_fare(adesso, sedute_intorno(), leggi_stato())
    print(f"{adesso:%Y-%m-%d %H:%M:%S} di New York: {azione}", flush=True)
    if azione == "fed":
        return fed(d["tipo"], d["ora"])
    if azione == "sera":
        return sera(d["ultima"], d["prossima"])
    if d.get("saltata"):
        oggi, comando = adesso.date().isoformat(), f"fed {d['saltata']} SALTATA"
        gia = DIARIO.exists() and ((pd.read_csv(DIARIO)[["giorno", "comando"]].astype(str) == [oggi, comando]).all(axis=1)).any()
        if not gia:                                # una riga sola per giorno
            annota({"giorno": oggi, "comando": comando, "note": azione})
    return azione


def pubblica() -> str:
    try:
        from stock.avanti import plancia
        v = conto.adesso()
        if v["miscela"] is None:
            return "Plancia: la miscela non è ancora partita"
        valore = v["miscela"]
        adesso = int(time.time())
        s = {"nome": "Miscela (banca centrale, calma, ampiezza)", "tipo": "demo", "ordine": 2, "valuta": "USD",
             "descrizione": "Un sesto del capitale a ciascuna di tre regole su SPY e QQQ: prima della banca centrale, più investiti "
                            "con il mercato calmo, metà fuori quando la salita la fanno in poche. Stesso conto demo della prima "
                            "candela, capitale virtuale suo.",
             "capitale": conto.CAPITALE_MISCELA, "valore": round(valore, 2),
             "rendimento": round(valore / conto.CAPITALE_MISCELA - 1, 6),
             "comprate": sum(1 for p in v["posizioni_miscela"] if float(p["qty"]) > 0), "vendute": 0, "aggiornato": adesso,
             "pesi": {plancia.chiave(p["symbol"]): round(float(p["market_value"]) / valore, 4) for p in v["posizioni_miscela"]} or None,
             "giorni": conto.giorni("miscela") or None, "primo_giorno_dal_capitale": True}
        errore = plancia.scrivi({"battito": adesso, f"strategie/{ID}": s})
        return errore or f"Plancia: pubblicata la miscela (valore {valore:,.2f} dollari)"
    except Exception as e:  # noqa: BLE001
        return f"Plancia: errore nella pubblicazione della miscela ({type(e).__name__}: {str(e)[:120]})"


if __name__ == "__main__":
    comando = sys.argv[1] if len(sys.argv) > 1 else "controlla"
    funzioni = {"auto": auto, "controlla": av.controlla, "plancia": pubblica}
    print(funzioni[comando]())
