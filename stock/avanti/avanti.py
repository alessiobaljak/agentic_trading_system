"""La misura in avanti sul conto demo di Alpaca (`stock/avanti/REGOLE.md`).

    python -m stock.avanti.avanti controlla   # il collegamento al conto demo (nessun ordine)
    python -m stock.avanti.avanti elenco      # le 10 azioni del mese (elenco_AAAA-MM.csv), se manca
    python -m stock.avanti.avanti apri        # alle 9:46 di New York: la candela e gli ordini
    python -m stock.avanti.avanti chiudi      # alle 15:55: chiude tutto, poi scrive il diario
    python -m stock.avanti.avanti riepilogo   # riepilogo.md dal diario

Le chiavi si leggono solo dall'ambiente (come `stock/dati/alpaca.py`) e non si scrivono mai.
"""
from __future__ import annotations

import json
import math
import sys
import time
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import requests

from stock.dati import alpaca

QUI = Path(__file__).resolve().parent
NY = "America/New_York"
CONTO_URL = alpaca.DEMO_URL
QUOTA = 0.98
POSTI = 10
MULTIPLO = 10.0
MINUTI_CANDELA = 15
IB_PER_AZIONE, IB_MINIMA = 0.005, 1.0
COLONNE = ["giorno", "simbolo", "lato", "quantita", "ingresso", "ora_ingresso", "uscita_prezzo", "ora_uscita", "uscita",
           "guadagno", "proporzione", "commissione_ib", "stop", "obiettivo", "riferimento", "nota"]


# ---- il collegamento -------------------------------------------------------------------------------------------------

def _richiesta(metodo: str, percorso: str, **kw) -> dict | list:
    r = requests.request(metodo, f"{CONTO_URL}{percorso}", headers=alpaca._intestazioni(), timeout=30, **kw)
    if r.status_code >= 400:
        raise alpaca.ErroreAlpaca(f"{r.status_code} su {percorso.split('?')[0]}: {r.text[:200]}")
    return r.json() if r.text else {}


def ny_adesso() -> pd.Timestamp:
    return pd.Timestamp.now(tz=NY)


def seduta_di_oggi() -> dict | None:
    """Apertura e chiusura di oggi dal calendario di Alpaca, o None se oggi la borsa è chiusa."""
    oggi = ny_adesso().date().isoformat()
    cal = _richiesta("GET", "/v2/calendar", params={"start": oggi, "end": oggi})
    if not cal or cal[0]["date"] != oggi:
        return None
    return {"apertura": pd.Timestamp(f"{oggi} {cal[0]['open']}", tz=NY), "chiusura": pd.Timestamp(f"{oggi} {cal[0]['close']}", tz=NY)}


# ---- le regole (funzioni pure, provate da stock/tests/test_avanti.py) --------------------------------------------------

def candela(minuti: pd.DataFrame, apertura: pd.Timestamp) -> dict | None:
    """Apertura, massimo, minimo e chiusura dei primi MINUTI_CANDELA minuti; None se manca la prima o l'ultima barra."""
    t = minuti.index.tz_convert(NY)
    dentro = minuti[(t >= apertura) & (t < apertura + pd.Timedelta(minutes=MINUTI_CANDELA))]
    if dentro.empty:
        return None
    tt = dentro.index.tz_convert(NY)
    if tt[0] != apertura or tt[-1] != apertura + pd.Timedelta(minutes=MINUTI_CANDELA - 1):
        return None
    return {"open": float(dentro["open"].iloc[0]), "high": float(dentro["high"].max()), "low": float(dentro["low"].min()),
            "close": float(dentro["close"].iloc[-1])}


def piano(c: dict, valore_conto: float) -> dict | None:
    """Lato, quantità, stop e obiettivo (prezzi arrotondati al centesimo), o None se la candela è piatta."""
    segno = float(np.sign(c["close"] - c["open"]))
    if segno == 0:
        return None
    stop = c["low"] if segno > 0 else c["high"]
    rischio = abs(c["close"] - stop)
    obiettivo = c["close"] + segno * MULTIPLO * rischio
    q = math.floor(QUOTA * valore_conto / POSTI / c["close"])
    if q <= 0 or rischio <= 0 or obiettivo <= 0:
        return None
    return {"lato": "buy" if segno > 0 else "sell", "quantita": q, "stop": round(stop, 2), "obiettivo": round(obiettivo, 2),
            "riferimento": c["close"]}


def commissione_ib(quantita: float, prezzo: float) -> float:
    return min(max(IB_PER_AZIONE * abs(quantita), IB_MINIMA), 0.01 * abs(quantita) * prezzo)


def operazioni_del_giorno(giorno: str, ordini: list[dict], esecuzioni: list[dict], gambe: dict[str, str]) -> list[dict]:
    """Una riga per ordine d'ingresso eseguito. `esecuzioni`: le esecuzioni di Alpaca del giorno (symbol, side, qty, price,
    transaction_time, order_id); `gambe`: id d'ordine -> «stop» / «obiettivo» per le gambe eseguite."""
    righe = []
    for o in ordini:
        if not o.get("id"):
            righe.append({"giorno": giorno, "simbolo": o["simbolo"], "lato": o.get("lato", ""), "nota": o.get("nota", "saltato")})
            continue
        mie = [e for e in esecuzioni if e["symbol"] == o["simbolo"]]
        entrata = [e for e in mie if e["order_id"] == o["id"]]
        if not entrata:
            righe.append({"giorno": giorno, "simbolo": o["simbolo"], "lato": o["lato"], "nota": "ordine non eseguito"})
            continue
        lato_uscita = "sell" if o["lato"] == "buy" else "buy"
        uscite = [e for e in mie if e["side"].startswith(lato_uscita) and e["order_id"] != o["id"]]
        q_in = sum(float(e["qty"]) for e in entrata)
        p_in = sum(float(e["qty"]) * float(e["price"]) for e in entrata) / q_in
        q_out = sum(float(e["qty"]) for e in uscite)
        p_out = sum(float(e["qty"]) * float(e["price"]) for e in uscite) / q_out if q_out else float("nan")
        segno = 1 if o["lato"] == "buy" else -1
        come = {gambe.get(e["order_id"], "chiusura") for e in uscite}
        guadagno = segno * (p_out - p_in) * q_in if q_out else float("nan")
        righe.append({"giorno": giorno, "simbolo": o["simbolo"], "lato": o["lato"], "quantita": q_in, "ingresso": round(p_in, 4),
                      "ora_ingresso": min(e["transaction_time"] for e in entrata), "uscita_prezzo": round(p_out, 4),
                      "ora_uscita": max((e["transaction_time"] for e in uscite), default=""),
                      "uscita": "/".join(sorted(come)) if uscite else "aperta",
                      "guadagno": round(guadagno, 2), "proporzione": round(guadagno / (p_in * q_in), 6) if q_out else float("nan"),
                      "commissione_ib": round(commissione_ib(q_in, p_in) + (commissione_ib(q_out, p_out) if q_out else 0), 2),
                      "stop": o["stop"], "obiettivo": o["obiettivo"], "riferimento": o["riferimento"],
                      "nota": "" if abs(q_out - q_in) < 1e-9 else f"uscite {q_out:g} su {q_in:g}"})
    return righe


# giorni in cui non si è seguita la regola (REGOLE.md, deviazioni): restano nel diario ma non contano nel giudizio
GIORNI_FUORI_REGOLA = {"2026-11-11"}


def riassunto(diario: pd.DataFrame) -> dict:
    diario = diario[~diario["giorno"].astype(str).isin(GIORNI_FUORI_REGOLA)]
    fatte = diario.dropna(subset=["proporzione"])
    x = fatte["proporzione"].astype(float)
    netta = x - fatte["commissione_ib"].astype(float) / (fatte["ingresso"].astype(float) * fatte["quantita"].astype(float))
    t = lambda s: float(s.mean() / s.std(ddof=1) * np.sqrt(len(s))) if len(s) > 1 and s.std(ddof=1) > 0 else float("nan")  # noqa: E731
    servono = (3 * netta.std(ddof=1) / netta.mean()) ** 2 if len(netta) > 1 and netta.mean() > 0 else float("nan")
    return {"giorni": diario["giorno"].nunique(), "operazioni": len(fatte), "saltate": int(len(diario) - len(fatte)),
            "in_guadagno": float((x > 0).mean()) if len(x) else float("nan"),
            "media": float(x.mean()) if len(x) else float("nan"), "t": t(x),
            "media_netta_ib": float(netta.mean()) if len(netta) else float("nan"), "t_netto_ib": t(netta),
            "dollari": float(fatte["guadagno"].astype(float).sum()), "commissioni_ib": float(fatte["commissione_ib"].astype(float).sum()),
            "servono_per_t3": servono}


# ---- i comandi -----------------------------------------------------------------------------------------------------

def elenco(mese: str | None = None) -> list[str]:
    from stock.universo.costruisci import GIORNI, QUANTI, STESSA_AZIENDA
    mese = mese or ny_adesso().strftime("%Y-%m")
    f = QUI / f"elenco_{mese}.csv"
    if f.exists():
        return pd.read_csv(f)["simbolo"].tolist()
    # i membri dell'S&P 500 (solo i simboli, informazione pubblica): copiati nel repository il 11 nov 2026 da sp500_attuale.csv, così
    # l'elenco si calcola anche su GitHub; Alpaca scrive BRK.B con il punto
    membri = pd.read_csv(QUI / "sp500_membri.csv")["simbolo"].tolist()
    primo = pd.Timestamp(f"{mese}-01", tz=NY)
    dollari = {}
    for i in range(0, len(membri), 100):
        barre = alpaca.barre_di_piu(membri[i:i + 100], "1Day", (primo - pd.Timedelta(days=120)).to_pydatetime(),
                                    (primo - pd.Timedelta(minutes=1)).to_pydatetime())
        for s, df in barre.items():
            if len(df) >= GIORNI:
                dollari[s] = float((df["close"] * df["volume"]).iloc[-GIORNI:].mean())
    migliori: dict[str, tuple[str, float]] = {}
    for s, v in dollari.items():
        k = STESSA_AZIENDA.get(s, s)
        if k not in migliori or v > migliori[k][1]:
            migliori[k] = (s, v)
    scelti = [s for s, _ in sorted(migliori.values(), key=lambda x: -x[1])[:QUANTI]]
    pd.DataFrame({"mese": mese, "posizione": range(1, len(scelti) + 1), "simbolo": scelti}).to_csv(f, index=False)
    return scelti


def _posizioni_candela() -> list[dict]:
    """Le posizioni della prima candela: tutte tranne i titoli della miscela, che sta nello stesso conto (stock/avanti/conto.py)."""
    from stock.avanti import conto
    return conto.separa(_richiesta("GET", "/v2/positions"))[0]


def _ordini_aperti_candela() -> list[dict]:
    from stock.avanti import conto
    return [o for o in _richiesta("GET", "/v2/orders", params={"status": "open", "limit": 500}) if not conto.della_miscela(o["symbol"])]


def _cancella_ordini_candela() -> None:
    """Cancella gli ordini aperti della prima candela (non quelli della miscela) e aspetta che siano spariti."""
    for o in _ordini_aperti_candela():
        try:
            _richiesta("DELETE", f"/v2/orders/{o['id']}")
        except alpaca.ErroreAlpaca:
            pass                                  # già cancellato insieme alla sua gamba gemella
    for _ in range(30):
        if not _ordini_aperti_candela():
            return
        time.sleep(1)


def apri() -> str:
    s = seduta_di_oggi()
    if s is None:
        return "oggi la borsa è chiusa: niente ordini"
    if s["chiusura"] - s["apertura"] != pd.Timedelta(hours=6, minutes=30):
        return "oggi la seduta è corta: niente ordini (regola 0)"
    adesso = ny_adesso()
    pronto = s["apertura"] + pd.Timedelta(minutes=MINUTI_CANDELA)
    # 11 nov 2026: un orario di GitHub è partito con 7 ore di ritardo e ha mandato gli ordini alle 15:08. Dopo le 10:00 non si entra mai.
    if adesso > s["apertura"] + pd.Timedelta(minutes=30):
        return f"troppo tardi ({adesso:%H:%M} di New York): dopo le 10:00 non si entra, il giorno si salta"
    if adesso < pronto:
        time.sleep((pronto - adesso).total_seconds() + 5)
    oggi = adesso.date().isoformat()
    f_oggi = QUI / "giorni" / f"{oggi}.json"
    if f_oggi.exists():
        return f"gli ordini di oggi ci sono già ({f_oggi.name}): non si ripetono"
    simboli = elenco()
    from stock.avanti import conto as conto_mod
    v = conto_mod.adesso()
    valore = v["candela"]                         # il capitale virtuale della prima candela (il conto è condiviso con la miscela)
    if v["posizioni_candela"]:
        return "ci sono posizioni aperte da prima: niente ordini nuovi, va guardato a mano"
    parametri = {"symbols": ",".join(simboli), "timeframe": "1Min", "start": s["apertura"].tz_convert("UTC").isoformat(),
                 "end": pronto.tz_convert("UTC").isoformat(), "feed": "iex", "limit": 10000}
    j = alpaca._get(f"{alpaca.DATI_URL}/v2/stocks/bars", parametri)
    ordini = []
    for sim in simboli:
        df = alpaca.barre_da_righe((j.get("bars") or {}).get(sim, []))
        c = candela(df, s["apertura"]) if not df.empty else None
        p = piano(c, valore) if c else None
        if p is None:
            ordini.append({"simbolo": sim, "nota": "saltato: candela mancante o piatta"})
            continue
        # il nome unico per giorno e titolo: Alpaca rifiuta un secondo ordine con lo stesso nome, anche se due lavori partono insieme
        corpo = {"symbol": sim, "qty": str(p["quantita"]), "side": p["lato"], "type": "market", "time_in_force": "day",
                 "order_class": "bracket", "take_profit": {"limit_price": f"{p['obiettivo']:.2f}"},
                 "stop_loss": {"stop_price": f"{p['stop']:.2f}"}, "client_order_id": f"candela15-{oggi}-{sim}"}
        try:
            o = _richiesta("POST", "/v2/orders", json=corpo)
            ordini.append({"simbolo": sim, **p, "id": o["id"], "inviato": ny_adesso().isoformat()})
        except alpaca.ErroreAlpaca as e:
            ordini.append({"simbolo": sim, **p, "nota": f"saltato: rifiutato ({str(e)[:120]})"})
    f_oggi.parent.mkdir(exist_ok=True)
    f_oggi.write_text(json.dumps({"giorno": oggi, "valore_conto": valore, "ordini": ordini}, indent=1, ensure_ascii=False))
    n = sum(1 for o in ordini if o.get("id"))
    print(_plancia())
    return f"{oggi}: {n} ordini inviati su {len(simboli)} titoli ({', '.join(o['simbolo'] for o in ordini if o.get('id'))})"


def chiudi(aspetta: bool = True) -> str:
    oggi = ny_adesso().date().isoformat()
    s = seduta_di_oggi() if aspetta else None
    if s is not None and ny_adesso() >= s["chiusura"] - pd.Timedelta(seconds=45):
        # un ordine a mercato mandato a seduta finita resterebbe in coda fino all'apertura di domani: si chiude fuori orario
        return chiudi_fuori_orario() if _posizioni_candela() else scrivi_diario(oggi)
    if s is not None:
        # la routine parte prima (le routine arrivano anche con 10 minuti di ritardo): si aspetta 5 minuti prima della chiusura
        ora = s["chiusura"] - pd.Timedelta(minutes=5)
        attesa = (ora - ny_adesso()).total_seconds()
        if attesa > 0:
            time.sleep(attesa)
    # 9 nov 2026: DELETE /v2/positions con cancel_orders cancellava le gambe ma NON chiudeva le posizioni (8 su 10 restavano
    # aperte). Ora: prima si cancellano gli ordini e si aspetta che siano spariti, poi si chiude titolo per titolo e si controlla.
    _cancella_ordini_candela()
    for _ in range(3):
        aperte = _posizioni_candela()
        if not aperte:
            break
        for p in aperte:
            try:
                _richiesta("DELETE", f"/v2/positions/{p['symbol']}")
            except alpaca.ErroreAlpaca as e:
                print(f"chiusura di {p['symbol']} rifiutata: {str(e)[:120]}")
        time.sleep(10)
    rimaste = [p["symbol"] for p in _posizioni_candela()]
    time.sleep(30)
    esito = scrivi_diario(oggi)
    allarme = {"posizioni_aperte": {"ora": int(time.time()), "testo": f"posizioni ancora aperte dopo la chiusura: {', '.join(rimaste)}"}}
    print(_plancia(allarme if rimaste else None))
    if rimaste:
        raise alpaca.ErroreAlpaca(f"POSIZIONI ANCORA APERTE dopo la chiusura: {', '.join(rimaste)} ({esito})")
    return esito


ATTESA_MASSIMA = pd.Timedelta(hours=5, minutes=20)     # un lavoro di GitHub dura al massimo 6 ore


def cosa_fare(adesso: pd.Timestamp, seduta: dict | None, ordini_di_oggi: bool, posizioni: bool, diario_scritto: bool) -> str:
    """Cosa fare a quest'ora (funzione pura): «apri», «chiudi», «fuori_orario», «diario» o «niente: perché». Chi avvia il programma
    non deve essere puntuale: un avvio in anticipo aspetta l'ora giusta, un avvio in ritardo non entra mai fuori regola."""
    if seduta is None:
        return "niente: oggi la borsa è chiusa"
    apertura, chiusura = seduta["apertura"], seduta["chiusura"]
    pronto = apertura + pd.Timedelta(minutes=MINUTI_CANDELA)
    if posizioni and not ordini_di_oggi and adesso < chiusura - pd.Timedelta(seconds=45):
        # posizioni rimaste da un altro giorno: si chiudono subito (prima dell'apertura con gli ordini fuori orario, dalle 4:00)
        if adesso >= apertura + pd.Timedelta(minutes=1):
            return "chiudi_subito"
        return "fuori_orario" if adesso >= apertura - pd.Timedelta(hours=5, minutes=30) else "niente: posizioni di ieri, troppo presto"
    if not ordini_di_oggi and not posizioni and adesso <= apertura + pd.Timedelta(minutes=30):
        return "apri" if pronto - adesso <= ATTESA_MASSIMA else "niente: troppo presto per l'apertura"
    if adesso < chiusura - pd.Timedelta(seconds=45):
        if not ordini_di_oggi and not posizioni:
            return "niente: oggi nessun ordine, niente da chiudere"
        fine = chiusura - pd.Timedelta(minutes=5)
        return "chiudi" if fine - adesso <= ATTESA_MASSIMA else "niente: troppo presto per la chiusura"
    if posizioni:
        return "fuori_orario"
    return "diario" if ordini_di_oggi and not diario_scritto else "niente: giornata chiusa"


def auto() -> str:
    """Il comando di tutti gli avvii automatici: guarda l'orologio e il conto, e fa la cosa giusta per quest'ora. A seduta finita
    e senza posizioni scrive anche i valori di fine giornata delle due strategie del conto (stock/avanti/conto.py)."""
    esito = _auto()
    try:
        s = seduta_di_oggi()
        if s is not None and ny_adesso() >= s["chiusura"] + pd.Timedelta(minutes=1):
            from stock.avanti import conto
            print(conto.registra(ny_adesso().date().isoformat()), flush=True)
    except Exception as e:  # noqa: BLE001 — la contabilità non deve mai far fallire gli ordini
        print(f"valori di fine giornata non scritti ({type(e).__name__}: {str(e)[:120]})", flush=True)
    return esito


def _auto() -> str:
    adesso = ny_adesso()
    oggi = adesso.date().isoformat()
    f_diario = QUI / "diario.csv"
    scritto = f_diario.exists() and oggi in set(pd.read_csv(f_diario)["giorno"].astype(str))
    azione = cosa_fare(adesso, seduta_di_oggi(), (QUI / "giorni" / f"{oggi}.json").exists(),
                       bool(_posizioni_candela()), scritto)
    print(f"{adesso:%Y-%m-%d %H:%M:%S} di New York: {azione}", flush=True)
    if azione == "apri":
        return apri()
    if azione == "chiudi":
        return chiudi()
    if azione in ("chiudi_subito", "fuori_orario"):
        esito = chiudi(aspetta=False) if azione == "chiudi_subito" else chiudi_fuori_orario()
        # chiuse le posizioni rimaste: se è ancora in tempo per l'apertura di oggi, si prosegue con quella
        if cosa_fare(ny_adesso(), seduta_di_oggi(), (QUI / "giorni" / f"{oggi}.json").exists(), False, True) == "apri":
            return esito + "; " + apri()
        return esito
    if azione == "diario":
        esito = scrivi_diario(oggi)
        print(_plancia())
        return esito
    return azione


def chiudi_fuori_orario() -> str:
    """Emergenza: chiude le posizioni rimaste dopo la seduta con ordini limite validi fuori orario (fino alle 20:00 di New York),
    al prezzo dell'ultimo scambio peggiorato dello 0,5% perché si eseguano."""
    _cancella_ordini_candela()
    time.sleep(5)
    fatti = []
    for p in _posizioni_candela():
        q = float(p["qty"])
        ultimo = float(alpaca._get(f"{alpaca.DATI_URL}/v2/stocks/{p['symbol']}/trades/latest", {"feed": "iex"})["trade"]["p"])
        limite = round(ultimo * (0.995 if q > 0 else 1.005), 2)
        corpo = {"symbol": p["symbol"], "qty": str(abs(int(q))), "side": "sell" if q > 0 else "buy", "type": "limit",
                 "limit_price": f"{limite:.2f}", "time_in_force": "day", "extended_hours": True}
        o = _richiesta("POST", "/v2/orders", json=corpo)
        fatti.append(f"{p['symbol']} {-q:+g} a {limite} ({o.get('status')})")
    time.sleep(60)
    rimaste = [p["symbol"] for p in _posizioni_candela()]
    oggi = ny_adesso().date().isoformat()
    esito = scrivi_diario(oggi)
    print(_plancia({"posizioni_aperte": {"ora": int(time.time()), "testo": f"ancora aperte: {', '.join(rimaste)}"}} if rimaste else None))
    if rimaste:
        raise alpaca.ErroreAlpaca(f"POSIZIONI ANCORA APERTE dopo la chiusura fuori orario: {', '.join(rimaste)} ({'; '.join(fatti)})")
    return f"chiuse fuori orario: {'; '.join(fatti)}; {esito}"


def scrivi_diario(oggi: str) -> str:
    f_oggi = QUI / "giorni" / f"{oggi}.json"
    if not f_oggi.exists():
        return f"{oggi}: nessun ordine del giorno, niente diario"
    stato = json.loads(f_oggi.read_text())
    esecuzioni = _richiesta("GET", "/v2/account/activities/FILL", params={"date": oggi, "page_size": 100})
    gambe = {}
    for o in stato["ordini"]:
        if o.get("id"):
            dett = _richiesta("GET", f"/v2/orders/{o['id']}", params={"nested": "true"})
            for g in dett.get("legs") or []:
                gambe[g["id"]] = "stop" if g["type"] in ("stop", "stop_limit") else "obiettivo"
    righe = operazioni_del_giorno(oggi, stato["ordini"], esecuzioni, gambe)
    f = QUI / "diario.csv"
    vecchio = pd.read_csv(f) if f.exists() else pd.DataFrame(columns=COLONNE)
    vecchio = vecchio[vecchio["giorno"] != oggi]
    nuovo = pd.concat([vecchio, pd.DataFrame(righe, columns=COLONNE)], ignore_index=True)
    nuovo.to_csv(f, index=False)
    scrivi_riepilogo(nuovo)
    r = pd.DataFrame(righe, columns=COLONNE)
    return f"{oggi}: {r['guadagno'].notna().sum()} operazioni, {r['guadagno'].astype(float).sum():+.2f} dollari"


def scrivi_riepilogo(diario: pd.DataFrame | None = None) -> str:
    f = QUI / "diario.csv"
    if diario is None:
        if not f.exists():
            return "diario vuoto"
        diario = pd.read_csv(f)
    a = riassunto(diario)
    settimane = pd.to_datetime(diario["giorno"]).dt.to_period("W-FRI")
    righe = ["# La misura in avanti — riepilogo", "",
             f"Aggiornato il {datetime.now(timezone.utc):%Y-%m-%d %H:%M} UTC da `python -m stock.avanti.avanti` (regole in "
             "`REGOLE.md`, operazioni in `diario.csv`).", "",
             f"* Giorni: {a['giorni']}; operazioni: {a['operazioni']} (saltate o non eseguite: {a['saltate']}).",
             f"* In guadagno: {a['in_guadagno']:.0%}." if a["operazioni"] else "* Ancora nessuna operazione chiusa.",
             f"* Guadagno medio a operazione: {a['media']:+.3%} (t {a['t']:.1f}); con la commissione di Interactive Brokers stimata: "
             f"{a['media_netta_ib']:+.3%} (t {a['t_netto_ib']:.1f}).",
             f"* Totale: {a['dollari']:+,.2f} dollari; commissioni di Interactive Brokers stimate: {a['commissioni_ib']:,.2f} dollari.",
             "* Operazioni che servirebbero per arrivare a t 3 con la media netta di oggi: "
             + (f"circa {a['servono_per_t3']:,.0f}." if not math.isnan(a["servono_per_t3"]) else "nessun numero (media netta non positiva)."),
             "", "| Settimana | Operazioni | Guadagno (dollari) | Commissioni IB stimate |", "|---|---|---|---|"]
    for w, g in diario.groupby(settimane):
        fatte = g.dropna(subset=["guadagno"])
        righe.append(f"| {w.start_time:%Y-%m-%d} | {len(fatte)} | {fatte['guadagno'].astype(float).sum():+,.2f} | "
                     f"{fatte['commissione_ib'].astype(float).sum():,.2f} |")
    (QUI / "riepilogo.md").write_text("\n".join(righe) + "\n")
    return "\n".join(righe)


def _plancia(allarmi: dict | None = None) -> str:
    """Pubblica sulla Plancia; un errore qui non ferma mai gli ordini."""
    try:
        from stock.avanti import plancia
        return plancia.pubblica(allarmi)
    except Exception as e:  # noqa: BLE001
        return f"Plancia: errore nella pubblicazione ({type(e).__name__}: {str(e)[:120]})"


def controlla() -> str:
    c = _richiesta("GET", "/v2/account")
    return f"conto demo raggiungibile: stato {c.get('status')}, valore {float(c['equity']):,.0f} dollari"


if __name__ == "__main__":
    comando = sys.argv[1] if len(sys.argv) > 1 else "controlla"
    funzioni = {"controlla": controlla, "elenco": lambda: ", ".join(elenco()), "apri": apri, "chiudi": chiudi,
                "riepilogo": scrivi_riepilogo, "diario": lambda: scrivi_diario(sys.argv[2]), "plancia": _plancia, "chiudi_fuori_orario": chiudi_fuori_orario, "auto": auto}
    print(funzioni[comando]())
