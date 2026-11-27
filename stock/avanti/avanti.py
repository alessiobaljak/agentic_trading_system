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

TENTATIVI_RETE, TENTATIVI_429 = 3, 3


def _richiesta(metodo: str, percorso: str, **kw) -> dict | list:
    """Una richiesta al conto demo. Un errore di rete si ritenta tre volte e poi diventa ErroreAlpaca (mai un'eccezione diversa a
    metà di un giro di ordini). Una risposta 429 (troppe richieste: il limite è condiviso con la ricerca) si ritenta dopo qualche
    secondo: Alpaca non l'ha eseguita. Un ordine nuovo (POST su /v2/orders) dopo un errore di rete si ritenta solo se ha il suo nome
    unico (`client_order_id`), e prima si guarda per nome se il tentativo di prima è arrivato (audit del 27 novembre 2026): così non
    si manda mai due volte lo stesso ordine."""
    ordine = metodo == "POST" and percorso.startswith("/v2/orders")
    nome = (kw.get("json") or {}).get("client_order_id") if ordine else None
    rete = troppe = 0
    while True:
        try:
            r = requests.request(metodo, f"{CONTO_URL}{percorso}", headers=alpaca._intestazioni(), timeout=30, **kw)
        except requests.RequestException as e:
            rete += 1
            if ordine and not nome:
                raise alpaca.ErroreAlpaca(f"rete su {percorso.split('?')[0]}: {type(e).__name__} (ordine senza nome: non si "
                                          "ritenta)") from None
            if rete >= TENTATIVI_RETE:
                raise alpaca.ErroreAlpaca(f"rete su {percorso.split('?')[0]}: {type(e).__name__}") from None
            time.sleep(2)
            if nome:
                gia = _ordine_per_nome(nome)
                if gia is not None:
                    return gia
            continue
        if r.status_code == 429 and troppe < TENTATIVI_429:
            troppe += 1
            time.sleep(2 * troppe)
            continue
        break
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
        # audit del 27 novembre 2026: con uscite parziali il guadagno è quello della parte chiusa (il resto aperto lo conta il conto
        # come non realizzato); uscite in più dell'ingresso non si contano oltre la quantità entrata, e la nota lo dice
        chiusa = min(q_out, q_in)
        guadagno = segno * (p_out - p_in) * chiusa if q_out else float("nan")
        parziale = q_out and q_out < q_in - 1e-9
        nota = ""
        if parziale:
            nota = f"uscite {q_out:g} su {q_in:g}: resto aperto"
        elif q_out > q_in + 1e-9:
            nota = f"uscite {q_out:g} su {q_in:g}: uscite in più, da guardare"
        righe.append({"giorno": giorno, "simbolo": o["simbolo"], "lato": o["lato"], "quantita": q_in, "ingresso": round(p_in, 4),
                      "ora_ingresso": min(e["transaction_time"] for e in entrata), "uscita_prezzo": round(p_out, 4),
                      "ora_uscita": max((e["transaction_time"] for e in uscite), default=""),
                      "uscita": ("parziale" if parziale else "/".join(sorted(come))) if uscite else "aperta",
                      "guadagno": round(guadagno, 2), "proporzione": round(guadagno / (p_in * chiusa), 6) if q_out else float("nan"),
                      "commissione_ib": round(commissione_ib(q_in, p_in) + (commissione_ib(q_out, p_out) if q_out else 0), 2),
                      "stop": o["stop"], "obiettivo": o["obiettivo"], "riferimento": o["riferimento"], "nota": nota})
    return righe


def righe_aperte_prima(oggi: str, diario: pd.DataFrame | None = None) -> list[str]:
    """Le operazioni dei giorni prima di oggi rimaste «aperte» o «parziali» nel diario: una posizione passata la notte e non ancora
    completata. Finché ce n'è una, il capitale virtuale non è affidabile e non partono ordini nuovi (audit del 27 novembre 2026)."""
    if diario is None:
        f = QUI / "diario.csv"
        diario = pd.read_csv(f) if f.exists() else pd.DataFrame(columns=COLONNE)
    if not len(diario):
        return []
    d = diario[(diario["giorno"].astype(str) < oggi) & diario["uscita"].astype(str).isin({"aperta", "parziale"})]
    return [f"{g} {s}" for g, s in zip(d["giorno"].astype(str), d["simbolo"].astype(str))]


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

def barre_a_gruppi(simboli: list[str], timeframe: str, inizio, fine, rettifica: str = "raw",
                   falliti: list | None = None) -> dict[str, pd.DataFrame]:
    """Le barre di molti titoli a gruppi di 100. Se un gruppo fallisce (per esempio un simbolo che Alpaca non conosce fa fallire
    tutta la richiesta), si riprova un titolo alla volta e si salta solo quello che non va (audit del 27 novembre 2026); i titoli
    saltati vanno in `falliti` come (titolo, errore)."""
    out: dict[str, pd.DataFrame] = {}
    for i in range(0, len(simboli), 100):
        gruppo = simboli[i:i + 100]
        try:
            out.update(alpaca.barre_di_piu(gruppo, timeframe, inizio, fine, rettifica=rettifica))
        except alpaca.ErroreAlpaca as e:
            print(f"gruppo {i}-{i + len(gruppo)}: {str(e)[:100]}; riprovo un titolo alla volta", flush=True)
            for sim in gruppo:
                try:
                    out[sim] = alpaca.barre(sim, timeframe, inizio, fine, rettifica=rettifica)
                except alpaca.ErroreAlpaca as e1:
                    print(f"{sim}: senza barre ({str(e1)[:80]})", flush=True)
                    if falliti is not None:
                        falliti.append((sim, str(e1)))
    return out


def sconosciuto(errore: str) -> bool:
    """Un rifiuto di Alpaca sul simbolo (400, 404, 422): il titolo non c'è, non è un guasto passeggero."""
    return errore[:3] in {"400", "404", "422"}


def elenco(mese: str | None = None) -> list[str]:
    from stock.universo.costruisci import GIORNI, QUANTI, STESSA_AZIENDA
    mese = mese or ny_adesso().strftime("%Y-%m")
    f = QUI / f"elenco_{mese}.csv"
    if f.exists():
        return pd.read_csv(f)["simbolo"].tolist()
    # i membri dell'S&P 500 (solo i simboli, informazione pubblica), aggiornati ogni mese da `membri.py` (audit del 27 novembre 2026);
    # Alpaca scrive BRK.B con il punto
    from stock.avanti import membri as mb
    eta = mb.eta_in_giorni()
    if eta is None or eta > mb.GIORNI_DI_VALIDITA:
        print(f"ATTENZIONE: i membri dell'S&P 500 non si aggiornano da {'?' if eta is None else f'{eta:.0f}'} giorni "
              "(python -m stock.avanti.membri)", flush=True)
    membri = pd.read_csv(QUI / "sp500_membri.csv")["simbolo"].tolist()
    primo = pd.Timestamp(f"{mese}-01", tz=NY)
    dollari = {}
    falliti: list = []
    barre = barre_a_gruppi(membri, "1Day", (primo - pd.Timedelta(days=120)).to_pydatetime(), (primo - pd.Timedelta(minutes=1)).to_pydatetime(),
                           falliti=falliti)
    passeggeri = [x for x, e in falliti if not sconosciuto(e)]
    if passeggeri or len(barre) < 0.98 * len(membri):
        # un elenco scritto con dei buchi resterebbe per tutto il mese: meglio nessun file, il giro dopo riprova (revisione separata)
        raise alpaca.ErroreAlpaca(f"elenco del {mese} non scritto: prezzi per {len(barre)} titoli su {len(membri)}, guasti su "
                                  f"{', '.join(passeggeri[:10]) or 'nessuno'}")
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
    """Le posizioni della prima candela: tutte tranne i titoli della miscela e della prova 45, che stanno nello stesso conto
    (stock/avanti/conto.py)."""
    from stock.avanti import conto
    return conto.separa(_richiesta("GET", "/v2/positions"))[0]


def _ordini_aperti_candela() -> list[dict]:
    from stock.avanti import conto
    return [o for o in _richiesta("GET", "/v2/orders", params={"status": "open", "limit": 500}) if conto.della_candela(o["symbol"])]


def _cancella_ordini_candela(ferma_se_restano: bool = False) -> None:
    """Cancella gli ordini aperti della prima candela (non quelli della miscela né della prova 45) e aspetta che siano spariti.
    Con `ferma_se_restano` (prima di un ordine fuori orario) un ordine rimasto aperto ferma il giro: una gamba viva più un ordine di
    chiusura venderebbero due volte (audit del 27 novembre 2026, come la prova 45)."""
    for o in _ordini_aperti_candela():
        try:
            _richiesta("DELETE", f"/v2/orders/{o['id']}")
        except alpaca.ErroreAlpaca:
            pass                                  # già cancellato insieme alla sua gamba gemella
    for _ in range(30):
        restano = _ordini_aperti_candela()
        if not restano:
            return
        time.sleep(1)
    if ferma_se_restano:
        raise alpaca.ErroreAlpaca("prima candela: ordini ancora aperti, niente ordine fuori orario: " + ", ".join(
            f"{o.get('symbol')} {o.get('status')}" for o in restano))


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
    completa_righe(oggi)
    aperte = righe_aperte_prima(oggi)
    if aperte:
        # audit del 27 novembre 2026: con una riga di un altro giorno non completata il capitale virtuale è sbagliato (le quantità
        # verrebbero doppie o nulle): niente ordini, l'allarme sulla Plancia e il lavoro rosso
        testo = f"righe del diario ancora aperte da prima: {', '.join(aperte)}; niente ordini nuovi, va guardato a mano"
        print(_plancia({"contabilita": {"ora": int(time.time()), "testo": testo}}))
        raise alpaca.ErroreAlpaca(testo)
    from stock.avanti import conto as conto_mod
    v = conto_mod.adesso()
    valore = v["candela"]                         # il capitale virtuale della prima candela (il conto è condiviso con la miscela)
    if v["posizioni_candela"]:
        return "ci sono posizioni aperte da prima: niente ordini nuovi, va guardato a mano"
    parametri = {"symbols": ",".join(simboli), "timeframe": "1Min", "start": s["apertura"].tz_convert("UTC").isoformat(),
                 "end": pronto.tz_convert("UTC").isoformat(), "feed": "iex", "limit": 10000}
    j = alpaca._get(f"{alpaca.DATI_URL}/v2/stocks/bars", parametri)
    # l'ora si ricontrolla qui: lo scarico delle barre può aver ritentato per minuti
    if ny_adesso() > s["apertura"] + pd.Timedelta(minutes=30):
        return f"troppo tardi ({ny_adesso():%H:%M} di New York): dopo le 10:00 non si entra, il giorno si salta"
    ordini = []
    try:
        for sim in simboli:
            df = alpaca.barre_da_righe((j.get("bars") or {}).get(sim, []))
            c = candela(df, s["apertura"]) if not df.empty else None
            p = piano(c, valore) if c else None
            if p is None:
                ordini.append({"simbolo": sim, "nota": "saltato: candela mancante o piatta"})
                continue
            # il nome unico per giorno e titolo: Alpaca rifiuta un secondo ordine con lo stesso nome, anche se due lavori partono insieme
            nome = f"candela15-{oggi}-{sim}"
            corpo = {"symbol": sim, "qty": str(p["quantita"]), "side": p["lato"], "type": "market", "time_in_force": "day",
                     "order_class": "bracket", "take_profit": {"limit_price": f"{p['obiettivo']:.2f}"},
                     "stop_loss": {"stop_price": f"{p['stop']:.2f}"}, "client_order_id": nome}
            try:
                o = _richiesta("POST", "/v2/orders", json=corpo)
            except alpaca.ErroreAlpaca as e:
                try:
                    o = _ordine_per_nome(nome)    # già mandato (da un altro avvio, o da un tentativo andato a buon fine)?
                except alpaca.ErroreAlpaca as e2:
                    # non si sa se l'ordine c'è: si scrive con il suo nome e il diario lo cerca di nuovo (mai «saltato» a occhi chiusi)
                    ordini.append({"simbolo": sim, **p, "nome": nome,
                                   "nota": f"da verificare: rifiutato ({str(e)[:80]}), ricerca per nome fallita ({str(e2)[:60]})"})
                    continue
                if o is None:
                    ordini.append({"simbolo": sim, **p, "nota": f"saltato: rifiutato ({str(e)[:120]})"})
                    continue
            ordini.append({"simbolo": sim, **p, "id": o["id"], "nome": nome, "inviato": _ora_ny(o.get("submitted_at"))})
    finally:
        # il file del giorno si scrive comunque, anche se un errore ferma il giro a metà: senza, il diario perderebbe la giornata
        if ordini:
            f_oggi.parent.mkdir(exist_ok=True)
            f_oggi.write_text(json.dumps({"giorno": oggi, "valore_conto": round(valore, 2), "ordini": ordini}, indent=1,
                                         ensure_ascii=False))
    n = sum(1 for o in ordini if o.get("id"))
    print(_plancia({"contabilita": None}))
    return f"{oggi}: {n} ordini inviati su {len(simboli)} titoli ({', '.join(o['simbolo'] for o in ordini if o.get('id'))})"


def _ordine_per_nome(nome: str) -> dict | None:
    """L'ordine con questo nome, o None se Alpaca risponde che non esiste (404). Un errore di rete o di Alpaca NON vale «non esiste»:
    dopo tre tentativi diventa ErroreAlpaca (audit del 27 novembre 2026: prima un ordine vivo poteva finire nel diario come
    «saltato»; è la regola della prova 45)."""
    for n in range(3):
        try:
            return _richiesta("GET", "/v2/orders:by_client_order_id", params={"client_order_id": nome})
        except alpaca.ErroreAlpaca as e:
            if str(e).startswith("404"):
                return None
            if n == 2:
                raise
            time.sleep(3)
    return None


def _ora_ny(iso: str | None) -> str:
    return (pd.Timestamp(iso).tz_convert(NY) if iso else ny_adesso()).isoformat()


def _ordini_candela_su_alpaca(oggi: str) -> list[dict]:
    """Gli ordini d'ingresso della prima candela di oggi, come li ha Alpaca (dal nome unico), con le gambe."""
    return [o for o in _ordini_dal(oggi) if str(o.get("client_order_id", "")).startswith(f"candela15-{oggi}-")]


def ricostruisci_giorno(oggi: str) -> bool:
    """Se il file del giorno manca ma Alpaca ha gli ordini di oggi (un giro morto a metà, o un salvataggio fallito), lo riscrive da
    quelli: così il giro dopo non li prende per posizioni di un altro giorno e il diario non perde la giornata."""
    f_oggi = QUI / "giorni" / f"{oggi}.json"
    if f_oggi.exists():
        return True
    ordini = []
    for o in sorted(_ordini_candela_su_alpaca(oggi), key=lambda x: x.get("submitted_at") or ""):
        gambe = o.get("legs") or []
        stop = next((float(g["stop_price"]) for g in gambe if g.get("stop_price")), None)
        obiettivo = next((float(g["limit_price"]) for g in gambe if g.get("limit_price")), None)
        ordini.append({"simbolo": o["symbol"], "lato": o["side"], "quantita": int(float(o["qty"])), "stop": stop,
                       "obiettivo": obiettivo, "riferimento": None, "id": o["id"], "inviato": _ora_ny(o.get("submitted_at"))})
    if not ordini:
        return False
    f_oggi.parent.mkdir(exist_ok=True)
    f_oggi.write_text(json.dumps({"giorno": oggi, "ricostruito_da_alpaca": True, "ordini": ordini}, indent=1, ensure_ascii=False))
    return True


def esecuzioni_del_giorno(oggi: str) -> list[dict]:
    """Tutte le esecuzioni del giorno (a pagine da 100)."""
    out, pagina = [], None
    while True:
        parametri = {"date": oggi, "page_size": 100, "direction": "asc"}
        if pagina:
            parametri["page_token"] = pagina
        pezzo = _richiesta("GET", "/v2/account/activities/FILL", params=parametri)
        out += pezzo
        if len(pezzo) < 100:
            return out
        pagina = pezzo[-1]["id"]


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
    rimaste = _aspetta_chiusure()
    time.sleep(30)
    # l'allarme PRIMA del diario: se il diario fallisce, l'allarme delle posizioni rimaste esce lo stesso (audit del 27 novembre 2026)
    allarme = {"posizioni_aperte": {"ora": int(time.time()), "testo": f"posizioni ancora aperte dopo la chiusura: {', '.join(rimaste)}"}}
    print(_plancia(allarme if rimaste else None))
    try:
        esito = scrivi_diario(oggi)
    except Exception as e:
        if rimaste:
            raise alpaca.ErroreAlpaca(f"POSIZIONI ANCORA APERTE dopo la chiusura: {', '.join(rimaste)}; e diario non scritto "
                                      f"({type(e).__name__}: {str(e)[:100]})") from e
        raise
    print(_plancia(allarme if rimaste else None))      # di nuovo, con il diario di oggi
    if rimaste:
        raise alpaca.ErroreAlpaca(f"POSIZIONI ANCORA APERTE dopo la chiusura: {', '.join(rimaste)} ({esito})")
    return esito


ATTESA_CHIUSURE_S = 60


def _aspetta_chiusure(secondi: float = ATTESA_CHIUSURE_S) -> list[str]:
    """I titoli ancora aperti dopo le chiusure, ricontrollati ogni 5 secondi fino a `secondi`. 24 nov 2026: le chiusure partite
    alle 15:55 sono finite alle 15:55:47, ma il controllo guardava subito e ha dato un falso allarme su INTC a metà della vendita."""
    fine = time.monotonic() + secondi
    rimaste = None
    while True:
        try:
            rimaste = [p["symbol"] for p in _posizioni_candela()]
        except alpaca.ErroreAlpaca:
            if rimaste is None and time.monotonic() >= fine:
                raise                                   # nessuna lettura riuscita: l'errore si vede
        if rimaste is not None and (not rimaste or time.monotonic() >= fine):
            return rimaste
        time.sleep(5)


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
        # gli ordini fuori orario valgono fino alla fine del dopo borsa (4 ore dopo la chiusura, al massimo le 20:00 di New York; nei
        # giorni corti le 17:00): dopo si aspettano le 4:00 (audit del 27 novembre 2026)
        sera = min(chiusura + pd.Timedelta(hours=4), apertura.normalize() + pd.Timedelta(hours=20))
        return "fuori_orario" if adesso < sera else "niente: posizioni aperte dopo le 20:00, si chiudono dalle 4:00"
    return "diario" if ordini_di_oggi and not diario_scritto else "niente: giornata chiusa"


def auto() -> str:
    """Il comando di tutti gli avvii automatici: guarda l'orologio e il conto, e fa la cosa giusta per quest'ora. A seduta finita
    e senza posizioni scrive anche i valori di fine giornata delle due strategie del conto (stock/avanti/conto.py)."""
    esito = _auto()
    try:
        from stock.avanti import conto
        g = seduta_da_registrare(ny_adesso())
        if g is not None:
            print(conto.registra(g["giorno"], g["chiusura"]), flush=True)
    except Exception as e:  # noqa: BLE001 — la contabilità non deve mai far fallire gli ordini
        print(f"valori di fine giornata non scritti ({type(e).__name__}: {str(e)[:120]})", flush=True)
    return esito


def ultima_seduta_da_registrare(adesso: pd.Timestamp, sedute: list[dict]) -> dict | None:
    """La seduta di cui scrivere i valori di fine giornata (funzione pura): l'ultima finita da almeno un minuto, solo finché non è
    cominciata la seduta dopo (le posizioni della miscela sono ancora quelle della sera). Così la riga si scrive anche la mattina dopo,
    se la sera nessun giro è arrivato in tempo (revisione separata del 27 novembre 2026)."""
    finite = [x for x in sedute if x["chiusura"] + pd.Timedelta(minutes=1) <= adesso]
    if not finite:
        return None
    ultima = finite[-1]
    dopo = [x for x in sedute if x["apertura"] > ultima["chiusura"]]
    if dopo and adesso >= dopo[0]["apertura"]:
        return None
    return {"giorno": ultima["apertura"].date().isoformat(), "chiusura": ultima["chiusura"]}


def seduta_da_registrare(adesso: pd.Timestamp) -> dict | None:
    inizio = (adesso - pd.Timedelta(days=10)).date().isoformat()
    fine = (adesso + pd.Timedelta(days=5)).date().isoformat()
    cal = _richiesta("GET", "/v2/calendar", params={"start": inizio, "end": fine})
    sedute = [{"apertura": pd.Timestamp(f"{c['date']} {c['open']}", tz=NY), "chiusura": pd.Timestamp(f"{c['date']} {c['close']}", tz=NY)}
              for c in cal]
    return ultima_seduta_da_registrare(adesso, sedute)


def _auto() -> str:
    adesso = ny_adesso()
    oggi = adesso.date().isoformat()
    try:
        fatte = completa_righe(oggi)
        if fatte:
            print(f"righe del diario completate: {', '.join(fatte)}", flush=True)
    except Exception as e:  # noqa: BLE001 — la contabilità non deve fermare la chiusura
        print(f"righe del diario non completate ({type(e).__name__}: {str(e)[:120]})", flush=True)
    f_diario = QUI / "diario.csv"
    scritto = f_diario.exists() and oggi in set(pd.read_csv(f_diario)["giorno"].astype(str))
    posizioni = bool(_posizioni_candela())
    ordini_di_oggi = (QUI / "giorni" / f"{oggi}.json").exists()
    if not ordini_di_oggi and posizioni:
        ordini_di_oggi = ricostruisci_giorno(oggi)     # il file manca ma gli ordini di oggi ci sono: non sono «di un altro giorno»
    azione = cosa_fare(adesso, seduta_di_oggi(), ordini_di_oggi, posizioni, scritto)
    print(f"{adesso:%Y-%m-%d %H:%M:%S} di New York: {azione}", flush=True)
    if azione == "apri":
        # l'elenco del mese PRIMA dell'attesa delle 9:45: il primo giorno del mese non si scaricano 500 titoli alle 9:45 (audit del 27
        # novembre 2026); se qui non riesce, apri() riprova
        try:
            elenco()
        except Exception as e:  # noqa: BLE001
            print(f"elenco del mese non calcolato adesso ({type(e).__name__}: {str(e)[:120]}): si riprova alle 9:45", flush=True)
        return apri()
    if azione == "chiudi":
        return chiudi()
    if azione.startswith("niente: posizioni aperte dopo le 20:00"):
        print(_plancia({"posizioni_aperte": {"ora": int(time.time()), "testo": "posizioni della prima candela aperte dopo le 20:00: "
                                                                                "si chiudono dalle 4:00 di New York"}}))
        return azione
    if azione in ("chiudi_subito", "fuori_orario"):
        if not ordini_di_oggi:
            # posizioni di un altro giorno: si chiudono e la loro uscita va nella riga del giorno dell'ingresso (audit, A1)
            esito = chiudi_rimaste(oggi, in_seduta=azione == "chiudi_subito")
        else:
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


def nelle_ore_fuori_seduta(adesso: pd.Timestamp) -> bool:
    """Alpaca accetta gli ordini limite fuori orario dalle 4:00 alle 20:00 di New York, nei giorni feriali."""
    return adesso.weekday() < 5 and 4 <= adesso.hour < 20


def _ordine_limite_fuori_orario(simbolo: str, q: float, giorno: str, nome: str | None = None) -> dict:
    """Un ordine limite valido fuori orario che chiude `q` azioni, al prezzo dell'ultimo scambio peggiorato dello 0,5% perché si esegua,
    con un nome unico (audit del 27 novembre 2026: prima non lo aveva, e dopo un errore di rete poteva partire due volte)."""
    ultimo = float(alpaca._get(f"{alpaca.DATI_URL}/v2/stocks/{simbolo}/trades/latest", {"feed": "iex"})["trade"]["p"])
    limite = round(ultimo * (0.995 if q > 0 else 1.005), 2)
    corpo = {"symbol": simbolo, "qty": str(abs(int(q))), "side": "sell" if q > 0 else "buy", "type": "limit",
             "limit_price": f"{limite:.2f}", "time_in_force": "day", "extended_hours": True,
             "client_order_id": nome or f"candela-fo-{giorno}-{simbolo}-{ny_adesso():%H%M%S}"}
    o = _richiesta("POST", "/v2/orders", json=corpo)
    o["_limite"] = limite
    return o


def chiudi_fuori_orario() -> str:
    """Emergenza: chiude le posizioni di oggi rimaste dopo la seduta con ordini limite validi fuori orario (fino alle 20:00 di New
    York), al prezzo dell'ultimo scambio peggiorato dello 0,5% perché si eseguano."""
    if not nelle_ore_fuori_seduta(ny_adesso()):
        return "niente: fuori dalle ore fuori seduta (dalle 4:00 alle 20:00 di New York)"
    _cancella_ordini_candela(ferma_se_restano=True)
    time.sleep(5)
    oggi = ny_adesso().date().isoformat()
    fatti = []
    for p in _posizioni_candela():
        q = float(p["qty"])
        try:
            o = _ordine_limite_fuori_orario(p["symbol"], q, oggi)
            fatti.append(f"{p['symbol']} {-q:+g} a {o['_limite']} ({o.get('status')})")
        except Exception as e:  # noqa: BLE001 — un titolo rifiutato non deve lasciare gli altri senza ordine di chiusura
            fatti.append(f"{p['symbol']} NON CHIUSO ({type(e).__name__}: {str(e)[:100]})")
    time.sleep(60)
    rimaste = [p["symbol"] for p in _posizioni_candela()]
    print(_plancia({"posizioni_aperte": {"ora": int(time.time()), "testo": f"ancora aperte: {', '.join(rimaste)}"}} if rimaste else None))
    try:
        esito = scrivi_diario(oggi)
    except Exception as e:
        if rimaste:
            raise alpaca.ErroreAlpaca(f"POSIZIONI ANCORA APERTE dopo la chiusura fuori orario: {', '.join(rimaste)}; e diario non "
                                      f"scritto ({type(e).__name__}: {str(e)[:100]})") from e
        raise
    if rimaste:
        raise alpaca.ErroreAlpaca(f"POSIZIONI ANCORA APERTE dopo la chiusura fuori orario: {', '.join(rimaste)} ({'; '.join(fatti)})")
    return f"chiuse fuori orario: {'; '.join(fatti)}; {esito}"


# Le chiusure delle posizioni rimaste da un altro giorno hanno un nome con il giorno dell'ingresso: «candela-rim-AAAA-MM-GG-TITOLO-…»
# («ignoto» se il giorno non si trova). Il conto e il diario le riconoscono da Alpaca, mai dai file del repository, che un altro lavoro
# può vedere vecchi (revisione separata del 27 novembre 2026).
RIM = "candela-rim-"


def _ordini_dal(giorno: str, **filtri) -> list[dict]:
    """Gli ordini di Alpaca mandati da `giorno` (mezzanotte di New York) in poi, con le gambe."""
    inizio = pd.Timestamp(f"{giorno} 00:00", tz=NY).tz_convert("UTC").isoformat()
    return _richiesta("GET", "/v2/orders", params={"status": "all", "after": inizio, "limit": 500, "nested": "true", **filtri})


def giorno_d_ingresso(simbolo: str, q: float, prima_di: str) -> str | None:
    """L'ultimo giorno prima di `prima_di` con un ingresso eseguito della prima candela su `simbolo` dello stesso lato della posizione,
    dagli ordini di Alpaca (il nome «candela15-AAAA-MM-GG-TITOLO»)."""
    lato = "buy" if q > 0 else "sell"
    dal = (pd.Timestamp(prima_di) - pd.Timedelta(days=20)).date().isoformat()
    giorni = [str(o["client_order_id"])[10:20] for o in _ordini_dal(dal, symbols=simbolo)
              if str(o.get("client_order_id", "")).startswith("candela15-") and o.get("side") == lato
              and float(o.get("filled_qty") or 0) > 0 and str(o["client_order_id"])[10:20] < prima_di]
    return max(giorni) if giorni else None


def uscite_rimaste_per(prefisso: str, giorno: str, simbolo: str) -> list[dict]:
    """Le chiusure di una posizione rimasta del giorno `giorno` su `simbolo` (ordini con il nome `prefisso`+giorno, mandati nei giorni
    dopo), come esecuzioni: titolo, lato, quantità e prezzo medio eseguiti."""
    out = []
    for o in _ordini_dal(giorno, symbols=simbolo):
        if str(o.get("client_order_id", "")).startswith(f"{prefisso}{giorno}-") and float(o.get("filled_qty") or 0) > 0:
            out.append({"symbol": simbolo, "side": o["side"], "qty": o["filled_qty"], "price": o["filled_avg_price"],
                        "transaction_time": o.get("filled_at") or "", "order_id": o["id"]})
    return out


def chiudi_rimaste(oggi: str, in_seduta: bool) -> str:
    """Le posizioni della prima candela rimaste da un altro giorno (non deve succedere: c'è la chiusura delle 15:55 e quella fuori
    orario). Si chiudono con un ordine con il nome «candela-rim-{giorno dell'ingresso}-…» (a mercato in seduta, limite fuori orario
    prima dell'apertura), poi si riscrive la riga del giorno dell'ingresso con questa uscita. Il conto non conta queste vendite come
    guadagno di oggi (le riconosce dal nome): prima il capitale del giorno dopo quasi raddoppiava, la candela mandava quantità doppie e
    la miscela vendeva tutto (audit del 27 novembre 2026). Un giorno d'ingresso che non si trova ferma il giro con un errore."""
    if not in_seduta and not nelle_ore_fuori_seduta(ny_adesso()):
        return "niente: posizioni di un altro giorno, fuori dalle ore fuori seduta (si chiudono dalle 4:00)"
    _cancella_ordini_candela(ferma_se_restano=True)
    fatti, giorni, ignoti = [], set(), []
    for p in _posizioni_candela():
        q, sim = float(p["qty"]), p["symbol"]
        try:
            g = giorno_d_ingresso(sim, q, oggi)
            nome = f"{RIM}{g or 'ignoto'}-{sim}-{ny_adesso():%H%M%S}"
            if in_seduta:
                _richiesta("POST", "/v2/orders", json={"symbol": sim, "qty": str(abs(int(q))), "side": "sell" if q > 0 else "buy",
                                                       "type": "market", "time_in_force": "day", "client_order_id": nome})
            else:
                _ordine_limite_fuori_orario(sim, q, oggi, nome=nome)
            (giorni.add(g) if g else ignoti.append(sim))
            fatti.append(f"{sim} {-q:+g} (ingresso del {g or 'giorno non trovato'})")
        except Exception as e:  # noqa: BLE001 — un titolo rifiutato non deve lasciare gli altri senza ordine di chiusura
            fatti.append(f"{sim} NON CHIUSO ({type(e).__name__}: {str(e)[:100]})")
    time.sleep(60)
    rimaste = [p["symbol"] for p in _posizioni_candela()]
    allarme = None
    if rimaste or ignoti:
        allarme = {"posizioni_aperte": {"ora": int(time.time()), "testo": "prima candela, posizioni rimaste da un altro giorno: "
                                        + "; ".join(fatti)}}
    print(_plancia(allarme))
    for g in sorted(giorni):
        scrivi_diario(g)                           # la riga del giorno dell'ingresso, con l'uscita di oggi
    if rimaste:
        raise alpaca.ErroreAlpaca(f"POSIZIONI RIMASTE da un altro giorno ancora aperte: {', '.join(rimaste)} ({'; '.join(fatti)})")
    if ignoti:
        raise alpaca.ErroreAlpaca(f"posizioni rimaste chiuse, ma senza il giorno dell'ingresso: {', '.join(ignoti)} (va guardato a mano)")
    return f"chiuse le posizioni rimaste da un altro giorno: {'; '.join(fatti)}"


def completa_righe(oggi: str) -> list[str]:
    """Le righe «aperte» o «parziali» dei giorni fino a oggi, senza più posizioni della prima candela, si riscrivono: l'uscita può
    essere arrivata dopo il controllo di 60 secondi (fuori orario, o la chiusura di una rimasta). Si fa a ogni avvio; senza, una riga
    aperta fermava la candela per sempre (revisione separata del 27 novembre 2026)."""
    f = QUI / "diario.csv"
    if not f.exists() or _posizioni_candela():
        return []
    d = pd.read_csv(f)
    aperte = d[(d["giorno"].astype(str) <= oggi) & d["uscita"].astype(str).isin({"aperta", "parziale"})]
    giorni = sorted(set(aperte["giorno"].astype(str)))[-15:]
    for g in giorni:
        scrivi_diario(g)
    return giorni


def scrivi_diario(oggi: str) -> str:
    f_oggi = QUI / "giorni" / f"{oggi}.json"
    if not f_oggi.exists():
        return f"{oggi}: nessun ordine del giorno, niente diario"
    stato = json.loads(f_oggi.read_text())
    # gli ordini «da verificare» (la ricerca per nome era fallita all'ingresso): si cercano di nuovo
    cambiato = False
    for o in stato["ordini"]:
        if not o.get("id") and o.get("nome") and str(o.get("nota", "")).startswith("da verificare"):
            trovato = _ordine_per_nome(o["nome"])
            o["nota"] = "saltato: l'ordine non c'è (verificato dopo)" if trovato is None else ""
            if trovato is not None:
                o["id"], o["inviato"] = trovato["id"], _ora_ny(trovato.get("submitted_at"))
            cambiato = True
    if cambiato:
        f_oggi.write_text(json.dumps(stato, indent=1, ensure_ascii=False))
    esecuzioni = esecuzioni_del_giorno(oggi)
    gambe: dict[str, str] = {}
    for o in stato["ordini"]:
        if o.get("id"):
            dett = _richiesta("GET", f"/v2/orders/{o['id']}", params={"nested": "true"})
            for g in dett.get("legs") or []:
                gambe[g["id"]] = "stop" if g["type"] in ("stop", "stop_limit") else "obiettivo"
    # audit del 27 novembre 2026: le chiusure di posizioni rimaste di ALTRI giorni eseguite oggi (nome «candela-rim-») non sono uscite
    # delle operazioni di oggi; si riconoscono dal nome, leggendo da Alpaca gli ordini che non sono né ingressi né gambe di oggi
    ingressi = {o["id"] for o in stato["ordini"] if o.get("id")}
    simboli = {o["simbolo"] for o in stato["ordini"] if o.get("id")}
    altri = {e["order_id"] for e in esecuzioni if e["symbol"] in simboli and e["order_id"] not in ingressi and e["order_id"] not in gambe}
    altrui = {i for i in altri if str(_richiesta("GET", f"/v2/orders/{i}").get("client_order_id", "")).startswith(RIM)}
    esecuzioni = [e for e in esecuzioni if e["order_id"] not in altrui]
    righe = operazioni_del_giorno(oggi, stato["ordini"], esecuzioni, gambe)
    # le operazioni rimaste aperte: le loro chiusure dei giorni dopo, dal nome «candela-rim-{oggi}-{titolo}-»
    extra = [e for r in righe if r.get("uscita") in ("aperta", "parziale") for e in uscite_rimaste_per(RIM, oggi, r["simbolo"])]
    if extra:
        gambe.update({e["order_id"]: "giorno dopo" for e in extra})
        righe = operazioni_del_giorno(oggi, stato["ordini"], esecuzioni + extra, gambe)
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
    # la tabella per settimana con gli stessi giorni del totale (senza i giorni fuori regola: audit del 27 novembre 2026)
    diario = diario[~diario["giorno"].astype(str).isin(GIORNI_FUORI_REGOLA)]
    settimane = pd.to_datetime(diario["giorno"]).dt.to_period("W-FRI")
    righe = ["# La misura in avanti — riepilogo", "",
             f"Aggiornato il {datetime.now(timezone.utc):%Y-%m-%d %H:%M} UTC da `python -m stock.avanti.avanti` (regole in "
             "`REGOLE.md`, operazioni in `diario.csv`). Il resoconto completo del lunedì (costo vero dell'ingresso, t sui giorni, "
             "confronto con lo SPY) è in `resoconto.md`.", "",
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


def chiudi_a_mano() -> str:
    """Il comando «chiudi» dato a mano: se le posizioni non sono entrate oggi, passano da `chiudi_rimaste` (con il nome, così il conto
    e il diario le riconoscono); se no la chiusura di sempre."""
    from stock.avanti import conto
    oggi = ny_adesso().date().isoformat()
    entrate = conto.classifica(_ordini_dal(oggi), oggi)["entrate_candela"]
    pos = _posizioni_candela()
    if pos and not any(p["symbol"] in entrate for p in pos):
        s = seduta_di_oggi()
        in_seduta = s is not None and s["apertura"] <= ny_adesso() < s["chiusura"] - pd.Timedelta(seconds=45)
        return chiudi_rimaste(oggi, in_seduta=in_seduta)
    return chiudi()


def controlla() -> str:
    c = _richiesta("GET", "/v2/account")
    return (f"conto demo raggiungibile: stato {c.get('status')}, valore {float(c['equity']):,.0f} dollari, moltiplicatore del margine "
            f"{c.get('multiplier')}, potere d'acquisto {float(c.get('buying_power') or 0):,.0f}, in giornata "
            f"{float(c.get('daytrading_buying_power') or 0):,.0f}, giornate di compravendita contate {c.get('daytrade_count')}")


if __name__ == "__main__":
    comando = sys.argv[1] if len(sys.argv) > 1 else "controlla"
    funzioni = {"controlla": controlla, "elenco": lambda: ", ".join(elenco()), "apri": apri, "chiudi": chiudi_a_mano,
                "riepilogo": scrivi_riepilogo, "diario": lambda: scrivi_diario(sys.argv[2]), "plancia": _plancia, "chiudi_fuori_orario": chiudi_fuori_orario, "auto": auto}
    print(funzioni[comando]())
