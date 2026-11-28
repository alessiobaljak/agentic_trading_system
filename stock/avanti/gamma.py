"""La prova 45 sul conto demo (`stock/avanti/GAMMA.md`). Nei giorni in cui la copertura delle opzioni del giorno prima è sotto zero,
l'ultima mezz'ora segue la giornata dello SPY: si compra o si vende VOO mezz'ora prima della chiusura e si esce all'asta di chiusura.
Sta nello stesso conto demo della prima candela e della miscela, con capitale virtuale e titolo suoi (`stock/avanti/conto.py`).

    python -m stock.avanti.gamma auto        # tutti gli avvii: guarda l'orologio e fa la cosa giusta per quest'ora
    python -m stock.avanti.gamma controlla   # sola lettura: VOO vendibile allo scoperto, potere d'acquisto, dato della copertura
    python -m stock.avanti.gamma ordini      # sola lettura: gli ordini della prova 45 degli ultimi giorni

Chi avvia non deve essere puntuale: un avvio in anticipo aspetta l'ora dell'ingresso, un avvio in ritardo non entra mai fuori regola.
Nel repository vanno solo i nostri ordini e i nostri prezzi eseguiti: mai il valore della copertura né i prezzi scaricati.
"""
from __future__ import annotations

import csv
import io
import json
import math
import sys
import time
from datetime import date

import pandas as pd
import requests

from stock.avanti import avanti as av
from stock.avanti import conto
from stock.dati import alpaca

QUI = av.QUI
DIARIO = conto.DIARIO_GAMMA
GIORNI = QUI / "gamma_giorni"
SEGNALE = "SPY"
TITOLO = conto.SIMBOLI_GAMMA[0]
QUOTA = 0.98
PRIMA_DELLA_CHIUSURA = pd.Timedelta(minutes=30)
RITARDO_MASSIMO = pd.Timedelta(minutes=5)
ATTESA_BARRA = pd.Timedelta(seconds=60)
LIMITE_ASTA = pd.Timedelta(minutes=10)          # Alpaca accetta gli ordini alla chiusura fino a 10 minuti prima della fine
USCITA_A_MERCATO = pd.Timedelta(minutes=2)
TENTATIVI_ASTA = 3
# il lavoro di GitHub dura al massimo 350 minuti: attesa (4 ore e 30) + mezz'ora fino alla chiusura + 7 minuti dopo stanno sotto
ATTESA_MASSIMA = pd.Timedelta(hours=4, minutes=30)
DOPO_LA_CHIUSURA = pd.Timedelta(minutes=2)
DIX_URL = "https://squeezemetrics.com/monitor/static/DIX.csv"
ID = "gamma"
PRIMO_GIORNO = date(2026, 11, 24)                # la misura parte il 24 novembre 2026 (GAMMA.md): prima niente, nemmeno le righe
MORTI = {"canceled", "pending_cancel", "expired", "rejected", "done_for_day", "replaced", "pending_replace", "suspended"}
VIVI = {"new", "accepted", "pending_new", "accepted_for_bidding", "held", "partially_filled", "calculated", "stopped"}
COLONNE = ["giorno", "simbolo", "copertura_del", "copertura", "r", "lato", "quantita", "ingresso", "ora_ingresso", "scarto_ingresso_pb",
           "uscita_prezzo", "ora_uscita", "uscita", "guadagno", "proporzione", "commissione_ib", "nota"]


# ---- le regole (funzioni pure, provate da stock/tests/test_gamma.py) --------------------------------------------------

def copertura(testo_csv: str, giorno: date) -> float | None:
    """Il valore della colonna `gex` di SqueezeMetrics con la data `giorno`, o None se manca."""
    for r in csv.DictReader(io.StringIO(testo_csv)):
        if (r.get("date") or "").strip() == giorno.isoformat():
            try:
                x = float(r["gex"])
            except (TypeError, ValueError, KeyError):
                return None
            return x if math.isfinite(x) else None
    return None


def direzione(chiusura_ieri: float, chiusura_segnale: float) -> tuple[float, str | None]:
    """(r, lato): r = chiusura della barra del segnale / chiusura di ieri − 1; «buy» se r > 0, «sell» se r < 0, None se r = 0."""
    r = chiusura_segnale / chiusura_ieri - 1
    return r, ("buy" if r > 0 else "sell" if r < 0 else None)


def quantita(capitale: float, prezzo: float) -> int:
    """Il 98% del capitale virtuale diviso per il prezzo, azioni intere."""
    return int(QUOTA * capitale / prezzo)


def cosa_fare(adesso: pd.Timestamp, seduta: dict | None, deciso_oggi: bool, posizione: bool, diario_scritto: bool) -> str:
    """Cosa fare a quest'ora: «entra», «tardi», «segui», «chiudi_subito», «fuori_orario», «diario» o «niente: perché»."""
    if seduta is None:
        return "niente: oggi la borsa è chiusa" + (" (c'è una posizione: si chiude al prossimo giorno di borsa)" if posizione else "")
    if adesso.date() < PRIMO_GIORNO and not posizione:
        return f"niente: la misura parte il {PRIMO_GIORNO}"
    apertura, chiusura = seduta["apertura"], seduta["chiusura"]
    ingresso = chiusura - PRIMA_DELLA_CHIUSURA
    # il dopo borsa finisce 4 ore dopo la chiusura (al massimo le 20:00; nei giorni corti le 17:00): revisione del 27 novembre 2026
    mattina = apertura.normalize() + pd.Timedelta(hours=4)
    sera = min(chiusura + pd.Timedelta(hours=4), apertura.normalize() + pd.Timedelta(hours=20))
    if posizione and not deciso_oggi:
        # una posizione di un altro giorno (non deve succedere): via subito, a mercato in seduta, con ordini limite fuori orario
        if apertura + pd.Timedelta(minutes=1) <= adesso < chiusura - pd.Timedelta(seconds=45):
            return "chiudi_subito"
        if mattina <= adesso < sera and not (chiusura - pd.Timedelta(seconds=45) <= adesso < chiusura + DOPO_LA_CHIUSURA):
            return "fuori_orario"
        return "niente: posizione di un altro giorno, adesso non si può chiudere"
    if not deciso_oggi:
        if adesso < ingresso - ATTESA_MASSIMA:
            return "niente: troppo presto per l'ingresso"
        return "entra" if adesso <= ingresso + RITARDO_MASSIMO else "tardi"
    if posizione:
        if adesso < chiusura + DOPO_LA_CHIUSURA:
            return "segui"
        return "fuori_orario" if adesso < sera else f"niente: posizione aperta dopo le {sera:%H:%M}, si chiude dalle 4:00"
    if not diario_scritto and adesso >= chiusura + DOPO_LA_CHIUSURA:
        return "diario"
    return "niente: la giornata è già fatta"


def riga_operazione(giorno: str, dec: dict, esecuzioni: list[dict], escludi: set[str] | None = None) -> dict:
    """La riga del diario di un giorno con l'ordine d'ingresso, dalle esecuzioni di VOO del giorno. `escludi`: gli ordini che altri
    giorni hanno segnato come uscita di una loro posizione rimasta (non sono uscite di questo ingresso: audit del 27 novembre 2026)."""
    base = {k: dec.get(k) for k in ("copertura_del", "copertura", "r", "lato", "scarto_ingresso_pb")}
    base.update({"giorno": giorno, "simbolo": TITOLO})
    mie = [e for e in esecuzioni if e["symbol"] == TITOLO and e["order_id"] not in (escludi or set())]
    entrata = [e for e in mie if e["order_id"] == dec.get("id_ingresso")]
    if not entrata:
        return {**base, "nota": dec.get("nota") or "ordine d'ingresso non eseguito"}
    lato_uscita = "sell" if dec["lato"] == "buy" else "buy"
    uscite = [e for e in mie if str(e["side"]).startswith(lato_uscita) and e["order_id"] != dec["id_ingresso"]]
    q_in = sum(float(e["qty"]) for e in entrata)
    p_in = sum(float(e["qty"]) * float(e["price"]) for e in entrata) / q_in
    q_out = sum(float(e["qty"]) for e in uscite)
    p_out = sum(float(e["qty"]) * float(e["price"]) for e in uscite) / q_out if q_out else float("nan")
    segno = 1 if dec["lato"] == "buy" else -1
    # con uscite parziali il guadagno è quello della parte chiusa; uscite in più non contano oltre l'ingresso (audit, 27 novembre 2026)
    chiusa = min(q_out, q_in)
    guadagno = segno * (p_out - p_in) * chiusa if q_out else float("nan")
    parziale = q_out and q_out < q_in - 1e-9
    come = {(dec.get("uscite") or {}).get(e["order_id"], "asta" if e["order_id"] == dec.get("id_asta") else "altro") for e in uscite}
    nota = [dec["nota"]] if dec.get("nota") else []
    if parziale:
        nota.append(f"uscite {q_out:g} su {q_in:g}: resto aperto")
    elif q_out > q_in + 1e-9:
        nota.append(f"uscite {q_out:g} su {q_in:g}: uscite in più, da guardare")
    return {**base, "quantita": q_in, "ingresso": round(p_in, 4), "ora_ingresso": min(e["transaction_time"] for e in entrata),
            "uscita_prezzo": round(p_out, 4) if q_out else float("nan"),
            "ora_uscita": max((e["transaction_time"] for e in uscite), default=""),
            "uscita": ("parziale" if parziale else "/".join(sorted(come))) if uscite else "aperta",
            "guadagno": round(guadagno, 2) if q_out else float("nan"),
            "proporzione": round(guadagno / (p_in * chiusa), 6) if q_out else float("nan"),
            "commissione_ib": round(av.commissione_ib(q_in, p_in) + (av.commissione_ib(q_out, p_out) if q_out else 0), 2),
            "nota": "; ".join(nota)}


# ---- il conto e i dati ----------------------------------------------------------------------------------------------

def sedute() -> list[dict]:
    oggi = av.ny_adesso().date()
    cal = av._richiesta("GET", "/v2/calendar", params={"start": (oggi - pd.Timedelta(days=12)).isoformat(),
                                                       "end": (oggi + pd.Timedelta(days=5)).isoformat()})
    return [{"giorno": date.fromisoformat(c["date"]), "apertura": pd.Timestamp(f"{c['date']} {c['open']}", tz=av.NY),
             "chiusura": pd.Timestamp(f"{c['date']} {c['close']}", tz=av.NY)} for c in cal]


def scarica_copertura(tentativi: int = 4) -> str:
    for n in range(tentativi):
        try:
            r = requests.get(DIX_URL, headers={"User-Agent": "Mozilla/5.0 (ricerca)"}, timeout=30)
            if r.status_code == 200 and r.text.startswith("date"):
                return r.text
        except requests.RequestException:
            pass
        time.sleep(5 * (n + 1))
    raise RuntimeError("il dato della copertura di SqueezeMetrics non si scarica")


def chiusura_di_ieri(ieri: dict) -> float | None:
    """La chiusura dell'ultima barra al minuto della seduta di ieri (tutte le borse, come nella prova)."""
    df = alpaca.barre(SEGNALE, "1Min", (ieri["chiusura"] - pd.Timedelta(minutes=15)).to_pydatetime(),
                      ieri["chiusura"].to_pydatetime(), feed="sip")
    if df.empty:
        return None
    df = df[df.index < ieri["chiusura"].tz_convert("UTC")]
    return float(df["close"].iloc[-1]) if not df.empty else None


def chiusura_del_segnale(ingresso: pd.Timestamp) -> float | None:
    """La chiusura della barra al minuto che finisce all'ora dell'ingresso (borsa IEX, in tempo reale); None se non arriva."""
    inizio = ingresso - pd.Timedelta(minutes=1)
    fine = ingresso + ATTESA_BARRA
    while True:
        j = alpaca._get(f"{alpaca.DATI_URL}/v2/stocks/bars", {"symbols": SEGNALE, "timeframe": "1Min", "feed": "iex",
                                                               "start": inizio.tz_convert("UTC").isoformat(),
                                                               "end": ingresso.tz_convert("UTC").isoformat(), "limit": 10})
        df = alpaca.barre_da_righe((j.get("bars") or {}).get(SEGNALE, []))
        barra = df[df.index == inizio.tz_convert("UTC")]
        if not barra.empty:
            return float(barra["close"].iloc[-1])
        if av.ny_adesso() >= fine:
            return None
        time.sleep(3)


def ultimo_prezzo(simbolo: str) -> float:
    return float(alpaca._get(f"{alpaca.DATI_URL}/v2/stocks/{simbolo}/trades/latest", {"feed": "iex"})["trade"]["p"])


def posizione() -> float:
    """Le azioni di VOO nel conto (negative se vendute allo scoperto), 0 se nessuna."""
    return sum(float(p["qty"]) for p in conto.di_gamma(av._richiesta("GET", "/v2/positions")))


def capitale() -> float:
    """Il capitale virtuale della prova 45 prima dell'ingresso: 100'000 più i guadagni del diario."""
    d = pd.read_csv(DIARIO) if DIARIO.exists() else pd.DataFrame(columns=COLONNE)
    return conto.valore_gamma([], d)               # lo stesso conto della Plancia, con le tasse sulle vendite (27 novembre 2026)


def leggi_giorno(giorno: str) -> dict | None:
    f = GIORNI / f"{giorno}.json"
    return json.loads(f.read_text()) if f.exists() else None


def scrivi_giorno(dec: dict) -> None:
    GIORNI.mkdir(exist_ok=True)
    (GIORNI / f"{dec['giorno']}.json").write_text(json.dumps(dec, indent=1, ensure_ascii=False))


def annota(riga: dict) -> None:
    """Scrive (o riscrive) la riga del giorno nel diario."""
    d = pd.read_csv(DIARIO) if DIARIO.exists() else pd.DataFrame(columns=COLONNE)
    d = d[d["giorno"].astype(str) != riga["giorno"]]
    pd.concat([d, pd.DataFrame([riga], columns=COLONNE)], ignore_index=True).to_csv(DIARIO, index=False)


def manda(corpo: dict, scadenza: pd.Timestamp | None = None) -> dict | None:
    """Manda un ordine con il suo nome unico; se Alpaca lo rifiuta ma un ordine vivo con lo stesso nome c'è già, vale quello. Con
    `scadenza`, dopo quell'ora un tentativo fallito non si rimanda."""
    try:
        return av._richiesta("POST", "/v2/orders", json=corpo, scadenza=scadenza)
    except alpaca.ErroreAlpaca as e:
        gia = _ordine_per_nome(corpo["client_order_id"])
        if gia is not None and gia.get("status") not in MORTI:
            return gia
        print(f"ordine {corpo['client_order_id']} rifiutato: {str(e)[:160]}", flush=True)
        return None


# ---- le azioni ------------------------------------------------------------------------------------------------------

def decidi_senza_ordine(dec: dict, nota: str) -> str:
    dec["nota"] = nota
    scrivi_giorno(dec)
    annota({k: dec.get(k) for k in ("giorno", "copertura_del", "copertura", "r", "lato")} | {"simbolo": TITOLO, "nota": nota})
    print(pubblica(), flush=True)                  # anche nei giorni senza operazione (audit del 27 novembre 2026)
    return f"{dec['giorno']}: {nota}"


def entra(oggi: dict, ieri: dict) -> str:
    giorno = oggi["giorno"].isoformat()
    ingresso = oggi["chiusura"] - PRIMA_DELLA_CHIUSURA
    attesa = (ingresso - av.ny_adesso()).total_seconds()
    if attesa > 0:
        print(f"aspetto l'ingresso delle {ingresso:%H:%M} di New York ({attesa / 60:.0f} minuti)", flush=True)
        time.sleep(attesa)
    if leggi_giorno(giorno) is not None:
        return f"{giorno}: già deciso da un altro avvio"
    dec = {"giorno": giorno, "copertura_del": ieri["giorno"].isoformat()}
    try:
        gex = copertura(scarica_copertura(), ieri["giorno"])
    except RuntimeError as e:
        gex = None
        print(str(e), flush=True)
    if gex is None:
        dec["copertura"] = "mancante"
        return decidi_senza_ordine(dec, f"saltato: manca la copertura del {ieri['giorno']}")
    dec["copertura"] = "sotto zero" if gex < 0 else "sopra zero"
    if gex >= 0:
        return decidi_senza_ordine(dec, "niente: copertura sopra zero")
    c_ieri = chiusura_di_ieri(ieri)
    c_oggi = chiusura_del_segnale(ingresso)
    if c_ieri is None or c_oggi is None:
        return decidi_senza_ordine(dec, f"saltato: manca la barra {'di ieri' if c_ieri is None else 'del segnale'}")
    r, lato = direzione(c_ieri, c_oggi)
    dec["r"], dec["lato"] = round(r, 6), lato
    if lato is None:
        return decidi_senza_ordine(dec, "niente: r uguale a zero")
    if av.ny_adesso() > ingresso + RITARDO_MASSIMO:
        return decidi_senza_ordine(dec, f"saltato: dati arrivati in ritardo ({av.ny_adesso():%H:%M:%S})")
    if posizione() != 0:
        return decidi_senza_ordine(dec, "saltato: c'è già una posizione su VOO, va guardata a mano")
    aperte = righe_aperte_prima(giorno)
    if aperte:
        # come la prima candela: con una riga di un giorno prima non completata (per esempio una VOO chiusa a mano dal sito) il capitale
        # virtuale è sbagliato e la vendita di quella posizione conterebbe come guadagno di oggi (revisione del 27 novembre 2026)
        esito = decidi_senza_ordine(dec, f"saltato: righe del diario ancora aperte da prima ({', '.join(aperte)}), va guardato a mano")
        print(pubblica({"ora": int(time.time()), "testo": f"prova 45: righe del diario ancora aperte da prima: {', '.join(aperte)}"}))
        return esito
    prezzo = ultimo_prezzo(TITOLO)
    q = quantita(capitale(), prezzo)
    if av.ny_adesso() > ingresso + RITARDO_MASSIMO:      # l'ora si ricontrolla subito prima dell'ordine
        return decidi_senza_ordine(dec, f"saltato: troppo tardi per l'ingresso ({av.ny_adesso():%H:%M:%S})")
    nome = f"gamma-{giorno}-in"
    o = manda({"symbol": TITOLO, "qty": str(q), "side": lato, "type": "market", "time_in_force": "day", "client_order_id": nome},
              scadenza=ingresso + RITARDO_MASSIMO)
    if o is None:
        return decidi_senza_ordine(dec, "saltato: ordine d'ingresso non partito (rifiutato da Alpaca, o tempo scaduto dopo un errore)")
    dec.update({"id_ingresso": o["id"], "inviato": av._ora_ny(o.get("submitted_at")), "quantita_chiesta": q})
    scrivi_giorno(dec)                                  # subito: un giro che muore dopo l'ordine non lo perde
    for _ in range(30):
        o = av._richiesta("GET", f"/v2/orders/{dec['id_ingresso']}")
        if o.get("status") in ("filled",) or o.get("status") in MORTI:
            break
        time.sleep(2)
    fatte = float(o.get("filled_qty") or 0)
    if o.get("status") != "filled":
        try:
            av._richiesta("DELETE", f"/v2/orders/{dec['id_ingresso']}")
        except alpaca.ErroreAlpaca:
            pass
        dec["nota"] = f"ingresso {o.get('status')}: eseguite {fatte:g} su {q}"
    if fatte > 0 and o.get("filled_avg_price"):
        segno = 1 if lato == "buy" else -1
        dec["scarto_ingresso_pb"] = round(segno * (float(o["filled_avg_price"]) / prezzo - 1) * 1e4, 2)
    scrivi_giorno(dec)
    if fatte <= 0:
        return decidi_senza_ordine(dec, dec.get("nota") or "ingresso non eseguito")
    print(f"{giorno}: ingresso {lato} {fatte:g} {TITOLO} alle {av.ny_adesso():%H:%M:%S}", flush=True)
    return segui(oggi)


def _ordine_per_nome(nome: str) -> dict | None:
    """L'ordine con questo nome, o None se Alpaca risponde che non esiste (404). Un errore di rete o di Alpaca NON vale «non esiste»:
    ferma il giro (se no un ingresso di oggi verrebbe preso per una posizione di un altro giorno)."""
    for n in range(3):
        try:
            return av._richiesta("GET", "/v2/orders:by_client_order_id", params={"client_order_id": nome})
        except alpaca.ErroreAlpaca as e:
            if str(e).startswith("404"):
                return None
            if n == 2:
                raise
            time.sleep(3)
    return None


def stato_asta(dec: dict) -> str | None:
    """Lo stato dell'ultimo ordine alla chiusura mandato per il giorno, o None se non ce n'è."""
    if not dec.get("id_asta"):
        return None
    return av._richiesta("GET", f"/v2/orders/{dec['id_asta']}").get("status")


def _nota(dec: dict, testo: str) -> None:
    if testo not in (dec.get("nota") or ""):
        dec["nota"] = "; ".join(x for x in (dec.get("nota"), testo) if x)
    scrivi_giorno(dec)


def _aspetta(fino: pd.Timestamp) -> None:
    attesa = (fino - av.ny_adesso()).total_seconds()
    if attesa > 0:
        time.sleep(attesa)


def _manda_asta(giorno: str, q: float, dec: dict) -> bool:
    """Manda l'ordine alla chiusura con un nome nuovo a ogni tentativo (al massimo 3 per giorno)."""
    n = int(dec.get("tentativi_asta", 0)) + 1
    if n > TENTATIVI_ASTA:
        return False
    dec["tentativi_asta"] = n
    nome = f"gamma-{giorno}-asta-{n}"
    o = manda({"symbol": TITOLO, "qty": str(int(abs(q))), "side": "sell" if q > 0 else "buy", "type": "market",
               "time_in_force": "cls", "client_order_id": nome})
    if o is None:
        scrivi_giorno(dec)
        return False
    dec["id_asta"], dec["nome_asta"] = o["id"], nome
    scrivi_giorno(dec)
    return True


def esci_a_mercato(dec: dict, perche: str) -> None:
    o = av._richiesta("DELETE", f"/v2/positions/{TITOLO}")
    dec.setdefault("uscite", {})[o.get("id", "")] = "mercato"
    _nota(dec, perche)


def segui(oggi: dict) -> str:
    """Con la posizione aperta, fino a 2 minuti dalla fine della seduta: l'ordine alla chiusura dev'essere vivo. Se manca, è stato
    rifiutato, cancellato o è scaduto, si rimanda finché Alpaca li accetta (10 minuti prima della fine); se non si può, a 2 minuti
    dalla fine si esce a mercato. Dopo la chiusura si aspetta che l'asta sia finita, poi il controllo e il diario."""
    giorno = oggi["giorno"].isoformat()
    dec = leggi_giorno(giorno) or {"giorno": giorno}
    chiusura = oggi["chiusura"]
    a_mercato = chiusura - USCITA_A_MERCATO
    while av.ny_adesso() < a_mercato:
        q = posizione()
        # una posizione che non si vede ancora (Alpaca la mostra con un attimo di ritardo dopo l'esecuzione) non vuol dire chiusa:
        # si riguarda al giro dopo, mai un'uscita prima delle 15:58
        if q != 0:
            stato = stato_asta(dec)
            viva = stato in VIVI or stato == "filled"
            if not viva and not (av.ny_adesso() < chiusura - LIMITE_ASTA and _manda_asta(giorno, q, dec)):
                _nota(dec, f"ordine alla chiusura {stato or 'non accettato'}: uscita a mercato")
                _aspetta(a_mercato)
                break
        time.sleep(min(30.0, max(1.0, (a_mercato - av.ny_adesso()).total_seconds())))
    adesso = av.ny_adesso()
    if (a_mercato - pd.Timedelta(seconds=5) <= adesso < chiusura - pd.Timedelta(seconds=45) and posizione() != 0
            and stato_asta(dec) not in VIVI | {"filled"}):
        esci_a_mercato(dec, "uscita a mercato 2 minuti prima della fine")
    _aspetta(chiusura + DOPO_LA_CHIUSURA)
    return dopo_la_chiusura(oggi, dec)


def dopo_la_chiusura(oggi: dict, dec: dict) -> str:
    """A seduta finita: si aspetta che l'ordine alla chiusura sia finito (fino a 7 minuti dopo la fine), poi, se VOO è ancora aperta,
    la chiusura fuori orario; infine il diario."""
    giorno = oggi["giorno"].isoformat()
    fine = oggi["chiusura"] + pd.Timedelta(minutes=7)
    while stato_asta(dec) in VIVI and av.ny_adesso() < fine:
        time.sleep(15)
    if posizione() != 0:
        return fuori_orario(giorno)
    return scrivi_diario(giorno)


def _cancella_ordini_gamma() -> None:
    """Cancella gli ordini aperti di VOO e controlla che siano spariti: se ne resta uno, il giro si ferma PRIMA di mandarne un altro
    (due uscite insieme raddoppierebbero la vendita)."""
    for o in av._richiesta("GET", "/v2/orders", params={"status": "open", "limit": 500}):
        if conto.della_gamma(o["symbol"]):
            try:
                av._richiesta("DELETE", f"/v2/orders/{o['id']}")
            except alpaca.ErroreAlpaca:
                pass
    for _ in range(10):
        time.sleep(3)
        restano = [o for o in av._richiesta("GET", "/v2/orders", params={"status": "open", "limit": 500})
                   if conto.della_gamma(o["symbol"])]
        if not restano:
            return
    raise alpaca.ErroreAlpaca("prova 45: ordini su VOO ancora aperti, niente ordine fuori orario: " + ", ".join(
        f"{o.get('client_order_id')} ({o.get('status')})" for o in restano))


def _ordine_fuori_orario(q: float, giorno: str, nome: str | None = None) -> dict:
    """L'ordine limite fuori orario, con un nome unico (audit del 27 novembre 2026: senza, dopo un errore di rete poteva partire due
    volte)."""
    ultimo = ultimo_prezzo(TITOLO)
    limite = round(ultimo * (0.995 if q > 0 else 1.005), 2)
    return av._richiesta("POST", "/v2/orders", json={"symbol": TITOLO, "qty": str(int(abs(q))), "side": "sell" if q > 0 else "buy",
                                                    "type": "limit", "limit_price": f"{limite:.2f}", "time_in_force": "day",
                                                    "extended_hours": True,
                                                    "client_order_id": nome or f"gamma-{giorno}-fo-{av.ny_adesso():%H%M%S}"})


def fuori_orario(giorno: str) -> str:
    """Emergenza: chiude VOO dopo la seduta con un ordine limite valido fuori orario, al prezzo dell'ultimo scambio peggiorato dello
    0,5% perché si esegua; se dopo un minuto è ancora aperta, l'errore ferma il giro e avvisa."""
    dec = leggi_giorno(giorno) or {"giorno": giorno}
    _cancella_ordini_gamma()
    q = posizione()
    if q != 0:
        o = _ordine_fuori_orario(q, giorno)
        dec.setdefault("uscite", {})[o["id"]] = "fuori orario"
        _nota(dec, "chiusa fuori orario")
        time.sleep(60)
    rimasta = posizione()
    # l'allarme PRIMA del diario: se il diario fallisce, l'allarme esce lo stesso (audit del 27 novembre 2026)
    print(pubblica({"ora": int(time.time()), "testo": f"VOO ancora aperta: {rimasta:g}"} if rimasta else None))
    try:
        esito = scrivi_diario(giorno)
    except Exception as e:
        if rimasta:
            raise alpaca.ErroreAlpaca(f"prova 45: POSIZIONE ANCORA APERTA su {TITOLO} ({rimasta:g}); e diario non scritto "
                                      f"({type(e).__name__}: {str(e)[:100]})") from e
        raise
    # di nuovo dopo il diario, che pubblica senza allarme (revisione separata del 27 novembre 2026)
    print(pubblica({"ora": int(time.time()), "testo": f"VOO ancora aperta: {rimasta:g}"} if rimasta else None))
    if rimasta:
        raise alpaca.ErroreAlpaca(f"prova 45: POSIZIONE ANCORA APERTA su {TITOLO} ({rimasta:g}) dopo la chiusura fuori orario ({esito})")
    return f"chiusa fuori orario; {esito}"


def chiudi_rimasta(oggi_iso: str, in_seduta: bool) -> str:
    """Una posizione su VOO rimasta da un giorno prima (non deve succedere: c'erano l'asta, l'uscita a mercato e quella fuori orario).
    Si chiude subito (a mercato in seduta, con un ordine limite fuori orario prima o dopo), si completa la riga del giorno
    dell'ingresso con questa uscita, e si scrive una riga di oggi che lo dice (così la contabilità non conta l'uscita due volte)."""
    _cancella_ordini_gamma()
    q = posizione()
    if q == 0:
        return "niente: la posizione non c'è più"
    # il giorno dell'ingresso: l'ultimo con un ingresso dello stesso lato della posizione rimasta; va nel nome dell'ordine
    # («gamma-rim-{giorno}-»), che il conto riconosce da Alpaca (revisione separata del 27 novembre 2026; prima era un DELETE senza nome)
    lato = "buy" if q > 0 else "sell"
    prima = [json.loads(f.read_text()) for f in sorted(GIORNI.glob("*.json")) if f.stem < oggi_iso]
    orig = next((d for d in reversed(prima) if d.get("id_ingresso") and d.get("lato") == lato), None)
    nome = f"gamma-rim-{orig['giorno'] if orig else 'ignoto'}-{av.ny_adesso():%H%M%S}"
    if in_seduta:
        o = av._richiesta("POST", "/v2/orders", json={"symbol": TITOLO, "qty": str(int(abs(q))), "side": "sell" if q > 0 else "buy",
                                                      "type": "market", "time_in_force": "day", "client_order_id": nome})
    else:
        o = _ordine_fuori_orario(q, oggi_iso, nome=nome)
    time.sleep(60)
    if orig is not None:
        orig.setdefault("uscite", {})[o.get("id", "")] = "giorno dopo"
        orig["chiusa_il"] = oggi_iso               # per completare la riga a un avvio dopo, se l'uscita arriva tardi
        orig["nota"] = "; ".join(x for x in (orig.get("nota"), f"chiusa il {oggi_iso}") if x)
        scrivi_giorno(orig)
        # tutte le uscite del giorno dopo segnate per questo ingresso (anche quelle di un giro prima), non solo quella di adesso
        es = av.esecuzioni_del_giorno(orig["giorno"]) + [e for e in av.esecuzioni_del_giorno(oggi_iso)
                                                          if e["order_id"] in orig["uscite"]]
        annota(riga_operazione(orig["giorno"], orig, es, escludi=uscite_di_altri_giorni(orig["giorno"], es, orig)))
    d = pd.read_csv(DIARIO) if DIARIO.exists() else pd.DataFrame(columns=COLONNE)
    if oggi_iso not in set(d["giorno"].astype(str)):
        annota({"giorno": oggi_iso, "simbolo": TITOLO,
                "nota": f"chiusa la posizione rimasta del {orig['giorno'] if orig else 'giorno prima'}"})
    rimasta = posizione()
    print(pubblica({"ora": int(time.time()), "testo": f"VOO rimasta da un altro giorno, ancora aperta: {rimasta:g}"}
                   if rimasta else None))
    if rimasta:
        raise alpaca.ErroreAlpaca(f"prova 45: POSIZIONE RIMASTA su {TITOLO} ancora aperta ({rimasta:g})")
    return f"chiusa una posizione su VOO rimasta da un altro giorno ({-q:+g})"


def uscite_di_altri_giorni(giorno: str, esecuzioni: list[dict] | None = None, dec: dict | None = None) -> set[str]:
    """Gli ordini che i file degli altri giorni hanno segnato come loro uscite (per esempio la chiusura di una posizione rimasta); con
    `esecuzioni`, anche le chiusure di posizioni rimaste di altri giorni riconosciute dal nome su Alpaca («gamma-rim-<altro giorno>-»),
    che un lavoro morto prima di salvare il file non avrebbe segnato (revisione separata del 27 novembre 2026)."""
    out: set[str] = set()
    for f in sorted(GIORNI.glob("*.json")) if GIORNI.exists() else []:
        if f.stem != giorno:
            out |= set((json.loads(f.read_text()).get("uscite") or {}).keys())
    if esecuzioni:
        d = dec or {}
        noti = {d.get("id_ingresso"), d.get("id_asta")} | set((d.get("uscite") or {}).keys()) | out
        for i in sorted({e["order_id"] for e in esecuzioni if e.get("symbol") == TITOLO} - noti):
            nome = str(av._richiesta("GET", f"/v2/orders/{i}").get("client_order_id", ""))
            # le chiusure di rimaste di altri giorni, e gli ordini di un altro giorno («gamma-<ieri>-fo-»: se Alpaca data le esecuzioni
            # in UTC, la vendita delle 19:30 di ieri cade fra quelle di oggi)
            if nome.startswith("gamma-rim-"):
                if not nome.startswith(f"gamma-rim-{giorno}-"):
                    out.add(i)
            elif nome.startswith("gamma-") and not nome.startswith(f"gamma-{giorno}-"):
                out.add(i)
    return out


def riga_mancante(giorno: str) -> bool:
    """Il giorno ha un ingresso nel suo file ma il diario non ha la sua riga (o ha solo la riga segnaposto «chiusa la posizione
    rimasta»): il diario della sera non è riuscito, e la riga dei valori di fine giornata sarebbe sbagliata."""
    dec = leggi_giorno(giorno)
    if not dec or not dec.get("id_ingresso"):
        return False
    d = pd.read_csv(DIARIO) if DIARIO.exists() else pd.DataFrame(columns=COLONNE)
    riga = d[d["giorno"].astype(str) == giorno]
    if riga.empty:
        return True
    if pd.to_numeric(riga["quantita"], errors="coerce").notna().any():
        return False
    return str(riga["nota"].iloc[-1]) != str(dec.get("nota"))


def righe_aperte_prima(giorno: str) -> list[str]:
    """I giorni prima di `giorno` con una riga «aperta» o «parziale» nel diario della prova 45."""
    if not DIARIO.exists():
        return []
    d = pd.read_csv(DIARIO)
    if not len(d) or "uscita" not in d.columns:
        return []
    return sorted(set(d.loc[(d["giorno"].astype(str) < giorno) & d["uscita"].astype(str).isin({"aperta", "parziale"}), "giorno"]
                      .astype(str)))


def fuori_orario_per_nome(giorno: str, esecuzioni: list[dict]) -> list[dict]:
    """Le chiusure fuori orario del giorno («gamma-<giorno>-fo-») cercate per nome, per la parte che non è fra le esecuzioni del giorno:
    se Alpaca data le esecuzioni in UTC, quelle fra le 19:00 e le 20:00 d'inverno cadono nel giorno dopo (revisione del 27 novembre)."""
    contate: dict[str, float] = {}
    for e in esecuzioni:
        contate[e["order_id"]] = contate.get(e["order_id"], 0.0) + float(e["qty"])
    out = []
    for e in av.uscite_rimaste_per("", giorno, TITOLO, testa=f"gamma-{giorno}-fo-"):
        resto = float(e["qty"]) - contate.get(e["order_id"], 0.0)
        if resto > 1e-9:
            out.append({**e, "qty": resto})
    return out


def completa_righe(oggi_iso: str) -> list[str]:
    """A ogni avvio: le righe dei giorni prima con un'uscita segnata il giorno dopo («chiusa_il») ma ancora senza guadagno nel diario
    (l'uscita è arrivata dopo il controllo di 60 secondi) si completano (audit del 27 novembre 2026)."""
    if not DIARIO.exists() or not GIORNI.exists() or posizione() != 0:
        return []
    d = pd.read_csv(DIARIO)
    fatte = []
    for f in sorted(GIORNI.glob("*.json"))[-15:]:
        dec = json.loads(f.read_text())
        if f.stem >= oggi_iso or not dec.get("id_ingresso"):   # oggi lo fa il giro di oggi (diario e fuori orario)
            continue
        riga = d[d["giorno"].astype(str) == f.stem]
        # da rifare: le righe che mancano, e quelle con l'ingresso eseguito ma senza guadagno, «aperte» o «parziali» (anche un'uscita
        # fuori orario dello stesso giorno arrivata tardi); una riga con l'ingresso non eseguito non si riscrive a ogni avvio
        if not riga.empty:
            q = pd.to_numeric(riga["quantita"], errors="coerce")
            if q.isna().all():
                # solo la riga scritta da `decidi_senza_ordine` per questo ingresso (la stessa nota del file del giorno) si lascia: la
                # riga segnaposto «chiusa la posizione rimasta» di un giorno con l'ingresso eseguito va rifatta (revisione, 27 novembre)
                if str(riga["nota"].iloc[-1]) == str(dec.get("nota")):
                    continue
            else:
                piene = riga[q.notna()]
                if not piene["uscita"].astype(str).isin({"aperta", "parziale"}).any() \
                        and pd.to_numeric(piene["guadagno"], errors="coerce").notna().all():
                    continue
        es = av.esecuzioni_del_giorno(f.stem)
        il = dec.get("chiusa_il")
        if il:
            es += [e for e in av.esecuzioni_del_giorno(il) if e["order_id"] in (dec.get("uscite") or {})]
        gia = {e["order_id"] for e in es}
        es += [e for e in av.uscite_rimaste_per("gamma-rim-", f.stem, TITOLO) if e["order_id"] not in gia]
        es += fuori_orario_per_nome(f.stem, es)
        annota(riga_operazione(f.stem, dec, es, escludi=uscite_di_altri_giorni(f.stem, es, dec)))
        fatte.append(f.stem)
    return fatte


def scrivi_diario(giorno: str) -> str:
    dec = leggi_giorno(giorno)
    if dec is None or not dec.get("id_ingresso"):
        return f"{giorno}: nessun ingresso, niente da aggiungere al diario"
    es = av.esecuzioni_del_giorno(giorno)
    es += fuori_orario_per_nome(giorno, es)
    riga = riga_operazione(giorno, dec, es, escludi=uscite_di_altri_giorni(giorno, es, dec))
    annota(riga)
    print(pubblica())
    g = riga.get("guadagno")
    return f"{giorno}: {riga.get('lato')} {riga.get('quantita')} {TITOLO}, uscita {riga.get('uscita')}, guadagno {g} dollari"


def tardi(oggi: dict, ieri: dict) -> str:
    """Un avvio arrivato dopo l'ora dell'ingresso: il giorno si salta, e il diario lo dice (con la copertura, per sapere se si è perso
    un giorno sotto zero)."""
    giorno = oggi["giorno"].isoformat()
    dec = {"giorno": giorno, "copertura_del": ieri["giorno"].isoformat()}
    try:
        gex = copertura(scarica_copertura(), ieri["giorno"])
    except RuntimeError:
        gex = None
    dec["copertura"] = "mancante" if gex is None else "sotto zero" if gex < 0 else "sopra zero"
    return decidi_senza_ordine(dec, f"saltato: avvio in ritardo ({av.ny_adesso():%H:%M} di New York)")


def ricostruisci(giorno: str) -> bool:
    """Se il file del giorno manca (un giro morto prima di salvarlo) ma Alpaca ha l'ingresso di oggi, lo riscrive da lì, con
    l'ultimo ordine alla chiusura: così il giro dopo non prende l'operazione per un giorno saltato."""
    o = _ordine_per_nome(f"gamma-{giorno}-in")
    if o is None:
        return False
    dec = {"giorno": giorno, "id_ingresso": o["id"], "lato": o["side"], "inviato": av._ora_ny(o.get("submitted_at")),
           "nota": "ricostruito da Alpaca"}
    for n in range(1, TENTATIVI_ASTA + 1):
        a = _ordine_per_nome(f"gamma-{giorno}-asta-{n}")
        if a is None:
            break
        dec.update({"id_asta": a["id"], "nome_asta": f"gamma-{giorno}-asta-{n}", "tentativi_asta": n})
    scrivi_giorno(dec)
    return True


def diario_scritto(giorno: str) -> bool:
    """La riga del giorno c'è ed è completa: con un ingresso, solo se ha la quantità (una riga «chiusa la posizione rimasta» no)."""
    if not DIARIO.exists():
        return False
    d = pd.read_csv(DIARIO)
    righe = d[d["giorno"].astype(str) == giorno]
    if righe.empty:
        return False
    dec = leggi_giorno(giorno) or {}
    if not dec.get("id_ingresso"):
        return True
    piene = righe[pd.to_numeric(righe["quantita"], errors="coerce").notna()]
    if not len(piene):
        return False
    # una riga «aperta» o «parziale» senza più la posizione non è scritta: l'uscita fuori orario è arrivata dopo il controllo di 60
    # secondi, e il giro dopo la completa prima dei valori di fine giornata (revisione separata del 27 novembre 2026)
    return not (piene["uscita"].astype(str).isin({"aperta", "parziale"}).any() and posizione() == 0)


def auto() -> str:
    adesso = av.ny_adesso()
    try:
        completate = completa_righe(adesso.date().isoformat())
        if completate:
            print(f"righe completate con l'uscita del giorno dopo: {', '.join(completate)}", flush=True)
    except Exception as e:  # noqa: BLE001 — la contabilità non deve fermare il giro
        print(f"righe dei giorni prima non completate ({type(e).__name__}: {str(e)[:120]})", flush=True)
    tutte = sedute()
    oggi = next((s for s in tutte if s["giorno"] == adesso.date()), None)
    giorno = adesso.date().isoformat()
    pos = posizione() != 0
    deciso = leggi_giorno(giorno) is not None or (oggi is not None and ricostruisci(giorno))
    azione = cosa_fare(adesso, oggi, deciso, pos, diario_scritto(giorno))
    print(f"{adesso:%Y-%m-%d %H:%M:%S} di New York: {azione}", flush=True)
    prima = [s for s in tutte if s["giorno"] < adesso.date()]
    if azione in ("entra", "tardi") and not prima:
        return "niente: calendario senza il giorno di borsa prima"
    if azione == "entra":
        return entra(oggi, prima[-1])
    if azione == "tardi":
        return tardi(oggi, prima[-1])
    if azione == "segui":
        return segui(oggi)
    if azione == "chiudi_subito":
        return chiudi_rimasta(giorno, in_seduta=True)
    if azione == "fuori_orario":
        return fuori_orario(giorno) if deciso else chiudi_rimasta(giorno, in_seduta=False)
    if azione == "diario":
        return scrivi_diario(giorno)
    return azione


# ---- la Plancia e i controlli ---------------------------------------------------------------------------------------

def pubblica(allarme: dict | None = None) -> str:
    """Pubblica la prova 45 sulla Plancia; `allarme` ({ora, testo}) se VOO è rimasta aperta, None lo azzera."""
    try:
        from stock.avanti import plancia
        v = conto.adesso()
        valore = v["gamma"]
        d = pd.read_csv(DIARIO) if DIARIO.exists() else pd.DataFrame(columns=COLONNE)
        fatte = d.dropna(subset=["quantita"]) if len(d) else d
        s = {"nome": "Ultima mezz'ora (copertura delle opzioni sotto zero)", "tipo": "demo", "ordine": 3, "valuta": "USD",
             "descrizione": "Prova 45: nei giorni in cui la copertura delle opzioni del giorno prima è sotto zero, mezz'ora prima della "
                            "chiusura si compra o si vende VOO nella direzione della giornata; uscita all'asta di chiusura. Stesso "
                            "conto demo, capitale virtuale suo." + (f" Finora {len(fatte)} operazioni su {len(d)} giorni." if len(d) else ""),
             "capitale": conto.CAPITALE_GAMMA, "valore": round(valore, 2), "rendimento": round(valore / conto.CAPITALE_GAMMA - 1, 6),
             "comprate": sum(1 for p in v["posizioni_gamma"] if float(p["qty"]) > 0),
             "vendute": sum(1 for p in v["posizioni_gamma"] if float(p["qty"]) < 0), "aggiornato": int(time.time()),
             "pesi": {plancia.chiave(p["symbol"]): round(float(p["market_value"]) / valore, 4) for p in v["posizioni_gamma"]} or None,
             "giorni": conto.giorni("gamma") or None, "primo_giorno_dal_capitale": True,
             # anche i giorni senza ingresso, con il perché (richiesta del proprietario del 28 novembre 2026)
             "operazioni": plancia.operazioni_recenti(d) or None}
        agg = {"battito": int(time.time()), f"strategie/{ID}": s, "allarmi/posizioni_aperte_gamma": allarme}
        errore = plancia.scrivi(agg)
        return errore or f"Plancia: pubblicata la prova 45 (valore {valore:,.2f} dollari)"
    except Exception as e:  # noqa: BLE001 — la Plancia non deve mai fermare gli ordini
        return f"Plancia: errore nella pubblicazione della prova 45 ({type(e).__name__}: {str(e)[:120]})"


def controlla() -> str:
    """Sola lettura, prima del primo giorno: VOO (e IVV) vendibili allo scoperto, il conto, il dato della copertura."""
    righe = [av.controlla()]
    for s in (TITOLO, "IVV"):
        a = av._richiesta("GET", f"/v2/assets/{s}")
        righe.append(f"{s}: " + ", ".join(f"{k} {a.get(k)}" for k in ("tradable", "shortable", "easy_to_borrow", "marginable")))
    t = scarica_copertura()
    date_ = [r["date"] for r in csv.DictReader(io.StringIO(t))]
    righe.append(f"copertura di SqueezeMetrics: {len(date_)} giorni, l'ultimo il {date_[-1]} (il valore non si stampa)")
    righe.append(f"posizione su {TITOLO} adesso: {posizione():g}; capitale virtuale della prova 45: {capitale():,.2f}")
    righe.append(f"un nome d'ordine che non esiste: {_ordine_per_nome('gamma-controllo-nome-che-non-esiste')} (deve essere None)")
    return "\n".join(righe)


def chiudi_a_mano() -> str:
    """Il comando «chiudi» dato a mano: una VOO rimasta da un altro giorno si chiude con il nome «gamma-rim-», che il conto e il diario
    riconoscono. Mai chiudere a mano dal sito di Alpaca: un ordine senza nome non si sa a quale giorno va (revisione del 27 novembre
    2026). Una posizione entrata oggi la chiudono l'asta e l'uscita fuori orario del giro di oggi."""
    adesso = av.ny_adesso()
    giorno = adesso.date().isoformat()
    if posizione() == 0:
        return "niente: nessuna posizione su VOO"
    if conto.classifica(av._ordini_dal(giorno), giorno)["entrata_gamma"]:
        return "niente: la posizione è entrata oggi, la chiudono l'asta di chiusura e l'uscita fuori orario"
    s = next((x for x in sedute() if x["giorno"] == adesso.date()), None)
    in_seduta = s is not None and s["apertura"] + pd.Timedelta(minutes=1) <= adesso < s["chiusura"] - pd.Timedelta(seconds=45)
    if s is not None and s["chiusura"] - pd.Timedelta(seconds=45) <= adesso < s["chiusura"] + DOPO_LA_CHIUSURA:
        return "niente: è l'ora dell'asta di chiusura, si riprova fra qualche minuto"
    if not in_seduta and not av.nelle_ore_fuori_seduta(adesso):
        return "niente: fuori dalle ore in cui Alpaca accetta ordini (dalle 4:00 alle 20:00 di New York)"
    return chiudi_rimasta(giorno, in_seduta=in_seduta)


def ordini_recenti(giorni: int = 5) -> str:
    dopo = (pd.Timestamp.now(tz="UTC") - pd.Timedelta(days=giorni)).isoformat()
    tutti = av._richiesta("GET", "/v2/orders", params={"status": "all", "limit": 500, "after": dopo, "direction": "asc"})
    righe = [" | ".join(str(o.get(k)) for k in ("client_order_id", "symbol", "side", "qty", "type", "time_in_force", "status",
                                                  "submitted_at", "filled_at", "filled_qty", "filled_avg_price"))
             for o in tutti if conto.della_gamma(o["symbol"])]
    return "\n".join(righe or ["nessun ordine della prova 45"]) + f"\nposizione su {TITOLO} adesso: {posizione():g}"


if __name__ == "__main__":
    comando = sys.argv[1] if len(sys.argv) > 1 else "controlla"
    funzioni = {"auto": auto, "controlla": controlla, "ordini": ordini_recenti, "plancia": pubblica, "chiudi": chiudi_a_mano}
    print(funzioni[comando]())
