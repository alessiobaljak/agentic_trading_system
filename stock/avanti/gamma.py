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
USCITA_A_MERCATO = pd.Timedelta(minutes=5)
DOPO_LA_CHIUSURA = pd.Timedelta(minutes=2)
DIX_URL = "https://squeezemetrics.com/monitor/static/DIX.csv"
ID = "gamma"
MORTI = {"canceled", "pending_cancel", "expired", "rejected", "done_for_day", "replaced", "pending_replace", "suspended"}
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
    apertura, chiusura = seduta["apertura"], seduta["chiusura"]
    ingresso = chiusura - PRIMA_DELLA_CHIUSURA
    mattina, sera = apertura.normalize() + pd.Timedelta(hours=4), apertura.normalize() + pd.Timedelta(hours=20)
    if posizione and not deciso_oggi:
        # una posizione di un altro giorno (non deve succedere): via subito, a mercato in seduta, con ordini limite fuori orario
        if apertura + pd.Timedelta(minutes=1) <= adesso < chiusura - pd.Timedelta(seconds=45):
            return "chiudi_subito"
        if mattina <= adesso < sera and not (chiusura - pd.Timedelta(seconds=45) <= adesso < chiusura + DOPO_LA_CHIUSURA):
            return "fuori_orario"
        return "niente: posizione di un altro giorno, adesso non si può chiudere"
    if not deciso_oggi:
        if adesso < ingresso - av.ATTESA_MASSIMA:
            return "niente: troppo presto per l'ingresso"
        return "entra" if adesso <= ingresso + RITARDO_MASSIMO else "tardi"
    if posizione:
        if adesso < chiusura + DOPO_LA_CHIUSURA:
            return "segui"
        return "fuori_orario" if adesso < sera else "niente: posizione aperta dopo le 20:00, si chiude dalle 4:00"
    if not diario_scritto and adesso >= chiusura + DOPO_LA_CHIUSURA:
        return "diario"
    return "niente: la giornata è già fatta"


def riga_operazione(giorno: str, dec: dict, esecuzioni: list[dict]) -> dict:
    """La riga del diario di un giorno con l'ordine d'ingresso, dalle esecuzioni di VOO del giorno."""
    base = {k: dec.get(k) for k in ("copertura_del", "copertura", "r", "lato", "scarto_ingresso_pb")}
    base.update({"giorno": giorno, "simbolo": TITOLO})
    mie = [e for e in esecuzioni if e["symbol"] == TITOLO]
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
    guadagno = segno * (p_out - p_in) * q_in if q_out else float("nan")
    come = {(dec.get("uscite") or {}).get(e["order_id"], "asta" if e["order_id"] == dec.get("id_asta") else "altro") for e in uscite}
    nota = [dec["nota"]] if dec.get("nota") else []
    if q_out and abs(q_out - q_in) > 1e-9:
        nota.append(f"uscite {q_out:g} su {q_in:g}")
    return {**base, "quantita": q_in, "ingresso": round(p_in, 4), "ora_ingresso": min(e["transaction_time"] for e in entrata),
            "uscita_prezzo": round(p_out, 4) if q_out else float("nan"),
            "ora_uscita": max((e["transaction_time"] for e in uscite), default=""),
            "uscita": "/".join(sorted(come)) if uscite else "aperta", "guadagno": round(guadagno, 2) if q_out else float("nan"),
            "proporzione": round(guadagno / (p_in * q_in), 6) if q_out else float("nan"),
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
    return conto.CAPITALE_GAMMA + float(pd.to_numeric(d["guadagno"], errors="coerce").dropna().sum())


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


def manda(corpo: dict) -> dict | None:
    """Manda un ordine con il suo nome unico; se Alpaca lo rifiuta ma un ordine vivo con lo stesso nome c'è già, vale quello."""
    try:
        return av._richiesta("POST", "/v2/orders", json=corpo)
    except alpaca.ErroreAlpaca as e:
        gia = av._ordine_per_nome(corpo["client_order_id"])
        if gia is not None and gia.get("status") not in MORTI:
            return gia
        print(f"ordine {corpo['client_order_id']} rifiutato: {str(e)[:160]}", flush=True)
        return None


# ---- le azioni ------------------------------------------------------------------------------------------------------

def decidi_senza_ordine(dec: dict, nota: str) -> str:
    dec["nota"] = nota
    scrivi_giorno(dec)
    annota({k: dec.get(k) for k in ("giorno", "copertura_del", "copertura", "r", "lato")} | {"simbolo": TITOLO, "nota": nota})
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
    prezzo = ultimo_prezzo(TITOLO)
    q = quantita(capitale(), prezzo)
    nome = f"gamma-{giorno}-in"
    o = manda({"symbol": TITOLO, "qty": str(q), "side": lato, "type": "market", "time_in_force": "day", "client_order_id": nome})
    if o is None:
        return decidi_senza_ordine(dec, "saltato: ordine d'ingresso rifiutato da Alpaca")
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


def _manda_asta(giorno: str, q: float, dec: dict) -> bool:
    nome = f"gamma-{giorno}-asta"
    o = manda({"symbol": TITOLO, "qty": str(int(abs(q))), "side": "sell" if q > 0 else "buy", "type": "market",
               "time_in_force": "cls", "client_order_id": nome})
    if o is None:
        return False
    dec["id_asta"] = o["id"]
    scrivi_giorno(dec)
    return True


def segui(oggi: dict) -> str:
    """Con la posizione aperta: l'ordine alla chiusura (se manca), o a mercato 5 minuti prima della fine se Alpaca lo rifiuta; poi
    dopo la chiusura il controllo, la chiusura fuori orario se serve, e il diario."""
    giorno = oggi["giorno"].isoformat()
    dec = leggi_giorno(giorno) or {"giorno": giorno}
    asta = av._ordine_per_nome(f"gamma-{giorno}-asta")
    viva = asta is not None and asta.get("status") not in MORTI
    if asta is not None and asta.get("status") == "filled":
        viva = True
    if not viva and av.ny_adesso() < oggi["chiusura"] - LIMITE_ASTA:
        q = posizione()
        viva = q == 0 or _manda_asta(giorno, q, dec)
    if not viva:
        fine = oggi["chiusura"] - USCITA_A_MERCATO
        attesa = (fine - av.ny_adesso()).total_seconds()
        if attesa > 0:
            time.sleep(attesa)
        if av.ny_adesso() < oggi["chiusura"] - pd.Timedelta(seconds=45) and posizione() != 0:
            o = av._richiesta("DELETE", f"/v2/positions/{TITOLO}")
            dec.setdefault("uscite", {})[o.get("id", "")] = "mercato"
            dec["nota"] = "; ".join(x for x in (dec.get("nota"), "ordine alla chiusura rifiutato: uscita a mercato") if x)
            scrivi_giorno(dec)
    attesa = (oggi["chiusura"] + DOPO_LA_CHIUSURA - av.ny_adesso()).total_seconds()
    if attesa > 0:
        time.sleep(attesa)
    if posizione() != 0:
        return fuori_orario(giorno)
    return scrivi_diario(giorno)


def fuori_orario(giorno: str) -> str:
    """Emergenza: chiude VOO dopo la seduta (o prima dell'apertura) con un ordine limite valido fuori orario, al prezzo dell'ultimo
    scambio peggiorato dello 0,5% perché si esegua; se dopo un minuto è ancora aperta, l'errore ferma il giro e avvisa."""
    dec = leggi_giorno(giorno) or {"giorno": giorno}
    for o in av._richiesta("GET", "/v2/orders", params={"status": "open", "limit": 500}):
        if conto.della_gamma(o["symbol"]):
            try:
                av._richiesta("DELETE", f"/v2/orders/{o['id']}")
            except alpaca.ErroreAlpaca:
                pass
    time.sleep(5)
    q = posizione()
    if q != 0:
        ultimo = ultimo_prezzo(TITOLO)
        limite = round(ultimo * (0.995 if q > 0 else 1.005), 2)
        o = av._richiesta("POST", "/v2/orders", json={"symbol": TITOLO, "qty": str(int(abs(q))), "side": "sell" if q > 0 else "buy",
                                                      "type": "limit", "limit_price": f"{limite:.2f}", "time_in_force": "day",
                                                      "extended_hours": True})
        if dec.get("id_ingresso"):
            dec.setdefault("uscite", {})[o["id"]] = "fuori orario"
            dec["nota"] = "; ".join(x for x in (dec.get("nota"), "chiusa fuori orario") if x)
            scrivi_giorno(dec)
        time.sleep(60)
    rimasta = posizione()
    esito = scrivi_diario(giorno) if dec.get("id_ingresso") else f"{giorno}: chiusa una posizione rimasta da un altro giorno"
    print(pubblica({"posizioni_aperte_gamma": {"ora": int(time.time()), "testo": f"VOO ancora aperta: {rimasta:g}"}} if rimasta else None))
    if rimasta:
        raise alpaca.ErroreAlpaca(f"prova 45: POSIZIONE ANCORA APERTA su {TITOLO} ({rimasta:g}) dopo la chiusura fuori orario ({esito})")
    return f"chiusa fuori orario; {esito}"


def scrivi_diario(giorno: str) -> str:
    dec = leggi_giorno(giorno)
    if dec is None or not dec.get("id_ingresso"):
        return f"{giorno}: nessun ingresso, niente da aggiungere al diario"
    riga = riga_operazione(giorno, dec, av.esecuzioni_del_giorno(giorno))
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


def auto() -> str:
    adesso = av.ny_adesso()
    tutte = sedute()
    oggi = next((s for s in tutte if s["giorno"] == adesso.date()), None)
    giorno = adesso.date().isoformat()
    pos = posizione() != 0
    deciso = leggi_giorno(giorno) is not None
    if not deciso and pos:
        o = av._ordine_per_nome(f"gamma-{giorno}-in")      # il file del giorno manca ma l'ordine di oggi c'è (un giro morto a metà)
        if o is not None:
            scrivi_giorno({"giorno": giorno, "id_ingresso": o["id"], "lato": o["side"], "nota": "ricostruito da Alpaca"})
            deciso = True
    scritto = DIARIO.exists() and giorno in set(pd.read_csv(DIARIO)["giorno"].astype(str))
    azione = cosa_fare(adesso, oggi, deciso, pos, scritto)
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
        av._richiesta("DELETE", f"/v2/positions/{TITOLO}")
        time.sleep(10)
        raise alpaca.ErroreAlpaca(f"prova 45: chiusa a mercato una posizione su {TITOLO} rimasta da un altro giorno: va guardato")
    if azione == "fuori_orario":
        return fuori_orario(giorno if deciso else "altro giorno")
    if azione == "diario":
        return scrivi_diario(giorno)
    return azione


# ---- la Plancia e i controlli ---------------------------------------------------------------------------------------

def pubblica(allarmi: dict | None = None) -> str:
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
             "operazioni": plancia.operazioni_recenti(fatte) or None}
        agg = {"battito": int(time.time()), f"strategie/{ID}": s}
        if allarmi is not None:
            agg["allarmi/posizioni_aperte_gamma"] = allarmi.get("posizioni_aperte_gamma")
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
    return "\n".join(righe)


def ordini_recenti(giorni: int = 5) -> str:
    dopo = (pd.Timestamp.now(tz="UTC") - pd.Timedelta(days=giorni)).isoformat()
    tutti = av._richiesta("GET", "/v2/orders", params={"status": "all", "limit": 500, "after": dopo, "direction": "asc"})
    righe = [" | ".join(str(o.get(k)) for k in ("client_order_id", "symbol", "side", "qty", "type", "time_in_force", "status",
                                                  "submitted_at", "filled_at", "filled_qty", "filled_avg_price"))
             for o in tutti if conto.della_gamma(o["symbol"])]
    return "\n".join(righe or ["nessun ordine della prova 45"]) + f"\nposizione su {TITOLO} adesso: {posizione():g}"


if __name__ == "__main__":
    comando = sys.argv[1] if len(sys.argv) > 1 else "controlla"
    funzioni = {"auto": auto, "controlla": controlla, "ordini": ordini_recenti, "plancia": pubblica}
    print(funzioni[comando]())
