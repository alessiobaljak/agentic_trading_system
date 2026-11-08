"""G1 sul conto demo di Binance (Binance Demo Trading, future USDⓈ-M): ordini veri su un conto con soldi finti.

Il proprietario (24 ottobre 2026): «perché per le crypto non usiamo Binance demo per simulare i nostri ordini (un paper live)?».
Il paper del bot (`f5.PaperG1`) simula gli ordini sui prezzi veri; qui le stesse decisioni di G1 diventano **ordini veri** sul
conto demo, cosi' le dimensioni minime, i passi di prezzo, i rifiuti, l'esecuzione degli ordini limite, il saldo e il funding li
decide Binance, non la nostra ipotesi. Il confronto fra i due dice quanto ci illude la simulazione.

* **Solo il conto demo**: tutte le richieste vanno a `demo-fapi.binance.com` (l'indirizzo dei future di prova nella documentazione
  ufficiale); `_url` rifiuta qualunque altro indirizzo, quindi questo codice non puo' mandare un ordine al conto vero nemmeno per
  errore. Le chiavi sono quelle del conto demo (`BINANCE_DEMO_API_KEY`, `BINANCE_DEMO_API_SECRET` nel `.env` della macchina),
  diverse da quelle del conto vero; mai nel repository. Vanno bene tutti e due i tipi di chiave di Binance: quella generata dal
  sistema (il segreto, firma HMAC) e quella generata da sé (la chiave privata Ed25519 o RSA in un file PEM sulla macchina, il cui
  percorso va in `BINANCE_DEMO_PRIVATE_KEY_PATH`; oppure il testo PEM in `BINANCE_DEMO_API_SECRET`).
* **Cosa fa**: quando G1 prende una decisione nuova (il giorno in `data/paper_g1.json` cambia), porta le posizioni del conto demo
  ai pesi di G1 per il valore del conto: ogni variazione come ordine limite al prezzo mark, valido un'ora; dopo l'ora quello che
  resta si annulla e si fa a mercato (come la ricerca, prova 56). Leva 5 su ogni moneta (i due lati insieme fanno il 200% del
  capitale). Ogni ora legge il conto e scrive su RTDB in `/demo_binance`.
* Acceso solo dal file `ops/demo_binance_acceso` e solo se le chiavi ci sono; `DRY_RUN` del bot non c'entra (il conto vero non si
  tocca mai).
* **Gli eventi accanto a G1** (il proprietario, 31 ottobre 2026: «ok aggiungi gli eventi sul demo accanto a G1»; interruttore suo,
  `ops/demo_binance_eventi_acceso`): le operazioni aperte del paper degli eventi (`data/paper_eventi.json`, N3 ed E4) si sommano ai
  pesi di G1, ognuna con il 5% del conto come nel paper (short la moneta, long il Bitcoin per lo stesso valore). Quando il paper apre
  o chiude un'operazione, il demo porta ai pesi nuovi **solo** quella moneta e il Bitcoin, con gli stessi ordini limite per un'ora e
  poi a mercato; lo fa dopo il ribilancio di G1 del giorno (o dalle 02:00 UTC, se G1 non ha deciso), cosi' i due non si accavallano.
  Il conto demo e' uno solo: il rendimento si confronta con la somma dei due paper.
* **Le protezioni** (il proprietario, 1° novembre 2026: «sì prepara e soglia −35%»; prima dei soldi veri, revisione con le skill,
  `research/programma7/REVISIONE_SKILL_G1.md`):
  * **il margine unico**: a ogni moneta nuova si chiede a Binance il margine unico per tutto il conto (`CROSSED`); ogni ora si
    controlla, e una moneta con il margine separato si chiude, si passa al margine unico e si riapre al ribilancio dopo;
  * **il pulsante che chiude tutto** (dashboard, `/commands/demo_binance_chiudi_tutto`; oppure un testo nuovo nel file
    `ops/demo_binance_chiudi_tutto`): annulla gli ordini e chiude tutte le posizioni a mercato; poi il demo resta fermo finché non
    arriva «riparti» (`/commands/demo_binance_riparti`, o un testo nuovo in `ops/demo_binance_riparti`);
  * **lo stop sul conto**: se il valore del conto scende del 35% dal suo massimo, il demo chiude tutto da solo e si ferma allo stesso
    modo (controllo ogni minuto, anche dopo un errore; da fermo si richiude ogni minuto fino al conto vuoto: revisione del 7 novembre 2026);
  * **il confronto fra le posizioni vere e quelle volute**: ogni ora, senza ordini in corso, le quantità che Binance dice che teniamo
    contro quelle decise all'ultimo ribilancio; ogni moneta con uno scarto oltre il 2% del conto va su RTDB in
    `/demo_binance/confronto` (si sistema da sola al ribilancio dopo).
* **Il conto ridotto** (il proprietario, 6 novembre 2026: «voglio partire con 250 euro», poi «spegni eventi»; prova 148,
  `research/programma7/RISULTATI_OTTANTASEIESIMA.md`): con un numero nel file `ops/demo_binance_capitale` (per esempio 280) il demo
  lavora come un conto di quella cifra. Il valore usato per le posizioni, lo stop e i rapporti è il capitale più il guadagno da quando
  il conto ridotto è partito; il resto del conto demo resta fermo. Dal 7 novembre un capitale nuovo parte solo alla decisione di G1
  dopo (la mezzanotte): prima si chiude tutto, poi si riapre da zero, come farà il conto vero. I filtri degli ordini sono severi almeno come quelli del conto vero
  (`filtri_conto_vero.json`). All'avvio i valori della fase di prima (`giorni`, `diario`, `ribilanciamenti`) passano in
  `/demo_binance/fasi/`, così grafici e rapporti ripartono puliti. Togliere il file non fa tornare al conto intero.
"""
from __future__ import annotations

import base64
import calendar
import hashlib
import hmac
import json
import math
import os
import re
import time
from pathlib import Path
from typing import Callable, Optional
from urllib.parse import quote, urlencode, urlparse

import requests

RADICE = Path(__file__).resolve().parents[2]
DEMO = "https://demo-fapi.binance.com"
HOST_DEMO = "demo-fapi.binance.com"
INTERRUTTORE = RADICE / "ops" / "demo_binance_acceso"
FILE_STATO = RADICE / "data" / "demo_binance.json"
FILE_G1 = RADICE / "data" / "paper_g1.json"
INTERRUTTORE_EVENTI = RADICE / "ops" / "demo_binance_eventi_acceso"
FILE_EVENTI = RADICE / "data" / "paper_eventi.json"
QUOTA_EVENTI = 0.05                    # come il paper degli eventi: il 5% del capitale per operazione
ATTESA_G1_S = 2 * 3600                 # gli eventi del giorno aspettano il ribilancio di G1 fino alle 02:00 UTC
LEVA = 5
VALIDITA_LIMITE_S = 3600
OGNI_VALUTAZIONE_S = 3600
ATTESA_DOPO_ERRORE_S = 1800                # dopo un errore, il ribilancio aspetta; le protezioni no (revisione del 7 nov 2026)
OGNI_CONTROLLO_STOP_S = 60                 # stop sul conto e conto vuoto da fermo: ogni minuto, non ogni ora
TENTATIVI_PRIMA_DELL_ALLARME = 3           # da fermo, chiusure che non svuotano il conto: allarme dopo 3 tentativi
ATTESA_DOPO_CHIUSURA_S = 2.0           # dopo le chiusure a mercato, prima di rileggere il conto (parti_da_zero)
STOP_CONTO = 0.35                      # il proprietario, 1° novembre 2026: chiude tutto a −35% dal massimo del conto
SOGLIA_CONFRONTO = 0.02                # uno scarto oltre il 2% del conto su una moneta si segnala
# i limiti che il conto vero erediterà (revisione del percorso degli ordini del 7 novembre 2026: reviews/reports/2026-11-07-primo-avvio.md,
# problemi 10-23, e reviews/reports/2026-11-07-correzione-32.md, problemi 36-38); gli allarmi vanno in /demo_binance/allarmi/<tipo>
SOMMA_PESI_MASSIMA = 2.5               # problema 10: G1 ha i due lati da 1 ciascuno (200%); ogni operazione a eventi aggiunge il 10%
PESO_MASSIMO_MONETA = 0.60             # problema 10: il peso più alto di G1 sul passato è il 47,8% (BLZ, 5 feb 2024, docs/backlog.md)
ETA_MASSIMA_DECISIONE_S = 26 * 3600    # problema 12: G1 decide ogni giorno alle 00:05 UTC; una decisione più vecchia non si esegue
RITENTATIVI_LIMITE = 3                 # problema 13: un 429 o un 418 di Binance si riprova 3 volte, con attese crescenti
ATTESE_LIMITE_S = (1.0, 2.0, 4.0)
ATTESA_LIMITE_MAX_S = 10.0             # un Retry-After più lungo non si aspetta dentro la richiesta: si ferma il giro
ATTESA_DOPO_LIMITE_S = 120.0           # 429 senza Retry-After: dopo i ritentativi nessuna richiesta per 2 minuti
ATTESA_418_SENZA_RETRY_S = 600.0       # 418 (indirizzo bloccato) senza Retry-After: 10 minuti senza richieste, con allarme
CAPITALE_MASSIMO = 10_000.0            # problema 16: un capitale sopra 10.000 USDT nel file non si usa
DATA_FILTRI_VERI = "2026-11-06"        # problema 16: la data della copia dei filtri del conto vero (filtri_conto_vero.json)
ETA_MASSIMA_FILTRI_GIORNI = 30         # oltre, allarme: la copia va riscaricata dal conto vero
PAVIMENTO_RIPARTI = 0.65               # problema 23: sotto il 65% del capitale di partenza della fase, «riparti» non riaccende;
                                       # e lo stop sul conto scatta anche lì (revisione dell'8 novembre 2026, decisione 2)
ATTESA_LIMITE_TETTO_S = 600.0          # problema 44: per un 429 un'attesa chiesta oltre 10 minuti vale 10 minuti, con allarme;
                                       # per un 418 no: chi riprova durante il blocco lo allunga (da 2 minuti fino a 3 giorni)
PEZZI_MASSIMI = 20                     # problema 43: una chiusura si divide al massimo in 20 ordini (il resto al tentativo dopo)
# le entrate vere del conto (research/programma7/MIGLIORARE_G1.md, voci 2-3; sì del proprietario del 5 novembre 2026): funding e
# commissioni del giorno, lette da /fapi/v1/income; i giorni chiusi si recuperano dal primo giorno del demo, al massimo 20 per volta
INIZIO_DEMO = "2026-10-24"
GIORNI_RECUPERO_MAX = 20
COMANDO_CHIUDI = "/commands/demo_binance_chiudi_tutto"
COMANDO_RIPARTI = "/commands/demo_binance_riparti"
# gli stessi due comandi come file nel repository (funzionano anche senza la dashboard: li scrive la sessione su richiesta del
# proprietario, la macchina li riceve con il git pull di ogni minuto); si eseguono una volta per ogni testo nuovo del file
FILE_CHIUDI = RADICE / "ops" / "demo_binance_chiudi_tutto"
FILE_RIPARTI = RADICE / "ops" / "demo_binance_riparti"
# il conto ridotto (vedi sopra): il capitale in USDT nel file; i filtri del conto vero accanto a questo modulo
FILE_CAPITALE = RADICE / "ops" / "demo_binance_capitale"
FILE_FILTRI_VERI = Path(__file__).with_name("filtri_conto_vero.json")
RAMI_DELLA_FASE = ("giorni", "diario", "ribilanciamenti")


def _url(percorso: str) -> str:
    url = DEMO + percorso
    if urlparse(url).hostname != HOST_DEMO:
        raise ValueError(f"indirizzo non ammesso: {url}")
    return url


def senza_firma(testo) -> str:
    """Il testo di un errore senza la parte firmata dell'indirizzo (la query con ``signature=``): restano metodo, percorso e codice
    (revisione del 7 novembre 2026, problema 21). Gli errori di rete di ``requests`` riportano l'indirizzo intero."""
    t = re.sub(r"\?[^\s'\"<>]*signature=[^\s'\"<>]*", "?[parametri tolti]", str(testo))
    return re.sub(r"signature=[^\s'\"<>&]*", "signature=[tolta]", t)


def pesi_fuori_dai_limiti(*insiemi, somma_massima: float = SOMMA_PESI_MASSIMA,
                          peso_massimo: float = PESO_MASSIMO_MONETA) -> Optional[str]:
    """Il controllo indipendente dei pesi prima degli ordini (revisione del 7 novembre 2026, problema 10): ogni peso è un numero
    finito, la somma dei valori assoluti non supera ``SOMMA_PESI_MASSIMA`` e nessuna moneta pesa più di ``PESO_MASSIMO_MONETA``.
    ``insiemi``: i pesi di G1 e quelli degli eventi, controllati uno per uno e sommati. Il motivo del rifiuto, o None. Pesi di G1
    vuoti si rifiutano anche loro (revisione dell'8 novembre 2026, problema 42: il demo chiudeva tutto senza allarme); il numero
    minimo di monete per lato è l'idea 97 del registro, una prova a parte. ``somma_massima`` e ``peso_massimo``: i limiti del conto
    (il conto vero ha i suoi, `conto_vero.py`)."""
    if insiemi and isinstance(insiemi[0], dict) and not insiemi[0]:
        return "pesi di G1 vuoti"
    for w in insiemi:
        if not isinstance(w, dict):
            return "pesi non leggibili"
        for s, v in w.items():
            try:
                x = float(v)
            except (TypeError, ValueError):
                return f"peso non numerico per {s}"
            if not math.isfinite(x):
                return f"peso non finito per {s}"
    tot = somma_pesi(*insiemi)
    lorda = sum(abs(v) for v in tot.values())
    if lorda > somma_massima + 1e-9:
        return f"somma dei pesi {100 * lorda:.1f}%, oltre il {100 * somma_massima:.0f}%"
    for s, v in sorted(tot.items()):
        if abs(v) > peso_massimo + 1e-9:
            return f"{s} pesa {100 * v:+.1f}%, oltre il {100 * peso_massimo:.0f}%"
    return None


def arrotonda(x: float, passo: float, verso: str = "giu") -> float:
    """``x`` a un multiplo di ``passo`` (verso il basso o verso l'alto), senza gli errori della virgola mobile."""
    if passo <= 0:
        return x
    n = x / passo
    n = math.floor(n + 1e-9) if verso == "giu" else math.ceil(n - 1e-9)
    decimali = max(0, -int(math.floor(math.log10(passo)))) if passo < 1 else 0
    return round(n * passo, decimali)


def testo(x: float) -> str:
    """Un numero per Binance, senza la notazione con l'esponente (1e-05 non e' ammesso)."""
    t = f"{x:.10f}".rstrip("0").rstrip(".")
    return t if t else "0"


def filtri(info: dict) -> dict:
    """{simbolo: (passo di prezzo, passo di quantita', quantita' minima, valore minimo)} dai filtri di exchangeInfo. Una moneta senza
    il valore minimo (MIN_NOTIONAL) non si tratta: prima si usavano 5 USDT scritti a mano (revisione del 7 novembre 2026, problema 22)."""
    out = {}
    for x in (info or {}).get("symbols", []):
        f = {g["filterType"]: g for g in x.get("filters", [])}
        try:
            out[x["symbol"]] = (float(f["PRICE_FILTER"]["tickSize"]), float(f["LOT_SIZE"]["stepSize"]),
                                float(f["LOT_SIZE"]["minQty"]), float(f["MIN_NOTIONAL"]["notional"]))
        except (KeyError, TypeError, ValueError):
            continue
    return out


def filtri_mercato(info: dict) -> dict:
    """{simbolo: (passo, quantita' minima, quantita' massima a mercato, quantita' massima a limite)}: gli ordini a mercato hanno i
    filtri loro (MARKET_LOT_SIZE; senza, quelli degli ordini limite) e tutti e due una quantita' massima (problema 22)."""
    out = {}
    for x in (info or {}).get("symbols", []):
        f = {g["filterType"]: g for g in x.get("filters", [])}
        lotto = f.get("LOT_SIZE") or {}
        mercato = f.get("MARKET_LOT_SIZE") or lotto
        try:
            out[x["symbol"]] = (float(mercato["stepSize"]), float(mercato["minQty"]),
                                float(mercato.get("maxQty") or math.inf), float(lotto.get("maxQty") or math.inf))
        except (KeyError, TypeError, ValueError):
            continue
    return out


def pezzi_di_chiusura(q: float, massimo: float, passo: float) -> list:
    """Una chiusura oltre la quantità massima a mercato in pezzi dentro il massimo (revisione dell'8 novembre 2026, problema 43)."""
    q = abs(float(q))
    pezzo = arrotonda(massimo, passo, "giu") if math.isfinite(massimo) and passo > 0 else massimo
    if not math.isfinite(pezzo) or pezzo <= 0 or q <= pezzo:
        return [q]
    out = []
    while q > pezzo and len(out) < PEZZI_MASSIMI:
        out.append(pezzo)
        q = round(q - pezzo, 10)
    if len(out) < PEZZI_MASSIMI and q > 0:          # oltre i 20 pezzi niente: il resto si richiude al tentativo dopo (problema 49)
        out.append(q)
    return out


def _pavimento(st: dict, pavimento: float = PAVIMENTO_RIPARTI) -> float:
    """Il ``PAVIMENTO_RIPARTI`` del capitale di partenza della fase. Non vale solo quando il conto, vuoto dopo un «riparti», aspetta la
    fase nuova di un capitale in attesa (da `parti_da_zero` vale il pavimento del capitale nuovo); con le posizioni della fase vecchia
    aperte vale anche con un capitale in attesa (revisione dell'8 novembre 2026, secondo giro, problema 47)."""
    if st.get("capitale_in_attesa") and st.get("riparti_attende_g1"):
        return 0.0
    return pavimento * float(st.get("capitale_iniziale") or 0)


def livello_di_stop(st: dict, stop: float = STOP_CONTO, pavimento: float = PAVIMENTO_RIPARTI) -> float:
    """Il valore del conto sotto il quale lo stop chiude tutto: il più alto fra il −35% dal massimo e il ``PAVIMENTO_RIPARTI`` del
    capitale di partenza della fase, così dopo un «riparti» la perdita totale resta entro il 35% del capitale (revisione dell'8
    novembre 2026, decisione 2)."""
    return max((1 - stop) * float(st["massimo"]), _pavimento(st, pavimento))


def motivo_dello_stop(st: dict, equity: float, stop: float = STOP_CONTO, pavimento: float = PAVIMENTO_RIPARTI) -> str:
    if (1 - stop) * float(st["massimo"]) >= _pavimento(st, pavimento):
        return f"stop sul conto: {100 * (equity / st['massimo'] - 1):.1f}% dal massimo"
    return f"stop sul conto: {100 * (equity / float(st['capitale_iniziale']) - 1):.1f}% dal capitale di partenza della fase"


def con_tetto(q: float, massimo: float, passo: float) -> float:
    """La quantita' ``q`` non oltre la quantita' massima di Binance (arrotondata al passo)."""
    if not math.isfinite(massimo) or q <= massimo:
        return q
    return arrotonda(massimo, passo, "giu")


def id_ordine(giorno: int, simbolo: str, tentativo: int = 0) -> str:
    """L'identificativo dell'ordine per Binance (ammessi solo ``.A-Za-z0-9:/_-``, al massimo 36): le monete con il nome in altri
    caratteri (per esempio 币安人生USDT) prendono un'impronta del nome. Il 24 ottobre il primo ribilancio sul demo si e' fermato qui,
    e il secondo tentativo dello stesso giorno con «ClientOrderId is duplicated»: per questo c'e' anche il tentativo (i secondi
    dell'ora, modulo 100.000)."""
    nome = simbolo if re.fullmatch(r"[.A-Za-z0-9:/_-]+", simbolo) else "h" + hashlib.sha1(simbolo.encode()).hexdigest()[:12]
    return f"g1d-{giorno}-{tentativo % 100_000}-{nome}"[:36]


def id_mercato(chiave: str, simbolo: str, giro: int = 0) -> str:
    """L'identificativo FISSO dell'ordine a mercato di una moneta per un ribilancio (revisione del 7 novembre 2026, problema 1): lo
    stesso a ogni tentativo dello stesso ribilancio, cosi' prima di mandarlo si controlla che non sia gia' partito; ``giro`` (l'ora
    del ribilancio) lo cambia per un secondo ribilancio dello stesso giorno, per esempio dopo un «riparti» (problema 26)."""
    nome = simbolo if re.fullmatch(r"[.A-Za-z0-9:/_-]+", simbolo) else "h" + hashlib.sha1(simbolo.encode()).hexdigest()[:12]
    return f"g1m-{chiave}-{int(giro) % 100000}-{nome}"[:36]


def ordini_del_giorno(pesi: dict, posizioni: dict, prezzi: dict, equity: float, f: dict) -> list:
    """Gli ordini per portare le posizioni ai pesi: [(simbolo, lato, quantita', prezzo limite, riduce)]. Le quantita' sono
    arrotondate al passo verso zero; si salta cio' che resta sotto la quantita' o il valore minimo."""
    out = []
    for s in sorted(set(pesi) | {k for k, v in posizioni.items() if v}):
        if s not in prezzi or s not in f:
            continue
        tick, passo, qmin, vmin = f[s]
        p = prezzi[s]
        attuale = float(posizioni.get(s, 0.0))
        obiettivo = float(pesi.get(s, 0.0)) * equity / p
        delta = obiettivo - attuale
        q = arrotonda(abs(delta), passo, "giu")
        if q < qmin or q * p < vmin:
            continue
        lato = "BUY" if delta > 0 else "SELL"
        limite = arrotonda(p, tick, "giu" if lato == "BUY" else "su")
        riduce = obiettivo == 0.0 or (attuale != 0 and (attuale > 0) == (obiettivo > 0) and abs(obiettivo) < abs(attuale))
        out.append((s, lato, q, limite, bool(riduce)))
    return out


def sotto_il_minimo(pesi: dict, posizioni: dict, prezzi: dict, equity: float, f: dict) -> dict:
    """Le variazioni volute che non diventano ordini perché restano sotto la quantità o il valore minimo (le stesse regole di
    `ordini_del_giorno`). La prova 148 se le aspetta con 280 USDT: circa 9 su 10 (`research/programma7/RISULTATI_OTTANTASEIESIMA.md`).
    Si contano solo le differenze da un centesimo in su."""
    n, valore = 0, 0.0
    for s in sorted(set(pesi) | {k for k, v in posizioni.items() if v}):
        if s not in prezzi or s not in f:
            continue
        _, passo, qmin, vmin = f[s]
        p = prezzi[s]
        delta = float(pesi.get(s, 0.0)) * equity / p - float(posizioni.get(s, 0.0))
        if abs(delta) * p < 0.01:
            continue
        q = arrotonda(abs(delta), passo, "giu")
        if q < qmin or q * p < vmin:
            n += 1
            valore += abs(delta) * p
    return {"variazioni": n, "valore_in_frazione_del_conto": round(valore / equity, 4) if equity > 0 else 0.0}


def filtri_veri(file: Path = FILE_FILTRI_VERI) -> dict:
    try:
        return dict(json.loads(Path(file).read_text(encoding="utf-8")).get("filtri") or {})
    except Exception:  # noqa: BLE001
        return {}


def piu_severi(f: dict, veri: dict) -> dict:
    """I filtri del demo resi severi almeno come quelli del conto vero. Il demo è più largo: il passo del Bitcoin è 0,0001 invece di
    0,001; BCH, LTC, ETC e LINK hanno il minimo di 5 USDT invece di 20. Il passo vero si usa solo se è un multiplo di quello del demo."""
    out = {}
    for s, (tick, passo, qmin, vmin) in f.items():
        v = veri.get(s)
        if v:
            pv = float(v.get("passo") or 0)
            if passo > 0 and pv > passo and abs(pv / passo - round(pv / passo)) < 1e-6:
                passo = pv
            qmin = max(qmin, float(v.get("quantita_minima") or 0))
            vmin = max(vmin, float(v.get("valore_minimo") or 0))
        out[s] = (tick, passo, qmin, vmin)
    return out


def pesi_eventi(aperte: dict) -> dict:
    """I pesi delle operazioni aperte del paper degli eventi: ognuna short la moneta e long il Bitcoin per il 5% del conto."""
    w: dict = {}
    for p in (aperte or {}).values():
        s = p.get("simbolo")
        if not s or s == "BTCUSDT":
            continue
        w[s] = w.get(s, 0.0) - QUOTA_EVENTI
        w["BTCUSDT"] = w.get("BTCUSDT", 0.0) + QUOTA_EVENTI
    return w


def entrate_del_conto(c, da_ms: int, a_ms: int) -> dict:
    """Le entrate del conto demo fra due istanti (``/fapi/v1/income``, estremi compresi): il funding incassato (positivo se
    incassato, negativo se pagato) e le commissioni pagate (positive), in USDT; le righe in un'altra valuta si contano a parte."""
    out = {"funding_incassato": 0.0, "commissioni_pagate": 0.0, "righe": 0, "altre_valute": 0}
    for tipo, chiave, segno in (("FUNDING_FEE", "funding_incassato", 1.0), ("COMMISSION", "commissioni_pagate", -1.0)):
        inizio = int(da_ms)
        while True:
            righe = c.chiedi("GET", "/fapi/v1/income", {"incomeType": tipo, "startTime": inizio, "endTime": int(a_ms),
                                                        "limit": 1000}, firmata=True) or []
            for r in righe:
                if (r.get("asset") or "USDT") != "USDT":
                    out["altre_valute"] += 1
                    continue
                out[chiave] += segno * float(r.get("income") or 0)
            out["righe"] += len(righe)
            if len(righe) < 1000:
                break
            inizio = max(int(r.get("time") or 0) for r in righe) + 1
    out["funding_incassato"] = round(out["funding_incassato"], 4)
    out["commissioni_pagate"] = round(out["commissioni_pagate"], 4)
    return out


def somma_pesi(*pesi: dict) -> dict:
    out: dict = {}
    for w in pesi:
        for s, v in (w or {}).items():
            out[s] = out.get(s, 0.0) + float(v)
    return {s: v for s, v in out.items() if abs(v) > 1e-12}


def firmatore(segreto: str) -> Callable[[str], str]:
    """La firma delle richieste secondo il tipo di chiave: il segreto della chiave generata dal sistema (HMAC SHA256, esadecimale)
    o la chiave privata PEM della chiave generata da sé (Ed25519, o RSA con SHA256; in base64, codificata per l'indirizzo)."""
    if "-----BEGIN" not in segreto:
        s = segreto.encode()
        return lambda q: hmac.new(s, q.encode(), hashlib.sha256).hexdigest()
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import ed25519, padding, rsa

    k = serialization.load_pem_private_key(segreto.encode(), password=None)
    if isinstance(k, ed25519.Ed25519PrivateKey):
        return lambda q: quote(base64.b64encode(k.sign(q.encode())).decode(), safe="")
    if isinstance(k, rsa.RSAPrivateKey):
        return lambda q: quote(base64.b64encode(k.sign(q.encode(), padding.PKCS1v15(), hashes.SHA256())).decode(), safe="")
    raise ValueError("chiave privata di tipo non previsto (servono Ed25519 o RSA)")


def segreto_dall_ambiente() -> str:
    """Il segreto della chiave del conto demo: il file PEM indicato in BINANCE_DEMO_PRIVATE_KEY_PATH, se c'e', altrimenti
    BINANCE_DEMO_API_SECRET."""
    percorso = os.environ.get("BINANCE_DEMO_PRIVATE_KEY_PATH", "")
    if percorso and Path(percorso).exists():
        return Path(percorso).read_text(encoding="utf-8")
    return os.environ.get("BINANCE_DEMO_API_SECRET", "").replace("\\n", "\n")


class LimiteBinance(Exception):
    """Binance risponde 429 (troppe richieste) o 418 (indirizzo bloccato) anche dopo i ritentativi. Non e' un RuntimeError apposta:
    non diventa il rifiuto di un ordine (il ciclo passerebbe all'ordine dopo, verso il blocco dell'indirizzo) ma ferma il giro, e
    nessuna richiesta parte per ``attesa_s`` secondi (revisione del 7 novembre 2026, problema 13). ``codice``: 429 o 418."""

    def __init__(self, testo: str, attesa_s: float, codice: int = 429) -> None:
        super().__init__(testo)
        self.attesa_s, self.codice = float(attesa_s), int(codice)


def _codice(r) -> Optional[int]:
    """Il codice d'errore di Binance nella risposta (per esempio -1021), se c'è."""
    try:
        d = r.json()
        return int(d["code"]) if isinstance(d, dict) and d.get("code") is not None else None
    except Exception:  # noqa: BLE001
        return None


def _retry_after(r) -> Optional[float]:
    """I secondi dell'intestazione Retry-After di Binance, se c'e'."""
    h = getattr(r, "headers", None) or {}
    try:
        x = float(h.get("Retry-After"))
    except (AttributeError, TypeError, ValueError):
        return None
    return x if math.isfinite(x) and x >= 0 else None


class ClienteDemo:
    """Le richieste al conto demo dei future (firmate con la chiave del conto demo). Il conto vero (`conto_vero.ClienteVero`) cambia
    solo ``_url`` (l'indirizzo ammesso) e ``NOME`` (il prefisso del log)."""

    NOME = "demo_binance"

    @staticmethod
    def _url(percorso: str) -> str:
        return _url(percorso)

    def __init__(self, chiave: str, segreto: str, http: Callable = requests.request) -> None:
        self.chiave, self.http = chiave, http
        self.firma = firmatore(segreto)
        self.scarto_ora_ms = 0                     # l'ora di Binance meno quella della macchina, dopo un errore d'orario (problema 44)

    def _rileggi_ora(self) -> None:
        """L'ora di Binance (``/fapi/v1/time``, senza firma): lo scarto con l'orologio della macchina va nelle firme dopo."""
        try:
            r = self.http("GET", self._url("/fapi/v1/time"), headers={"X-MBX-APIKEY": self.chiave}, timeout=15)
            if r.status_code < 400:
                self.scarto_ora_ms = int(r.json()["serverTime"]) - int(time.time() * 1000)
                print(f"[{self.NOME}] ora di Binance riletta: scarto {self.scarto_ora_ms} ms")
        except Exception as exc:  # noqa: BLE001
            print(f"[{self.NOME}] ora di Binance non letta: {senza_firma(exc)[:150]}")

    def chiedi(self, metodo: str, percorso: str, parametri: Optional[dict] = None, firmata: bool = False):
        """Una richiesta; 429 e 418 si riprovano con attese crescenti (o quella del Retry-After), poi ``LimiteBinance``. Gli errori
        di rete escono senza la parte firmata dell'indirizzo (problema 21). Un errore d'orario (-1021: la richiesta non è stata
        eseguita) fa rileggere l'ora di Binance e si riprova una volta sola (revisione dell'8 novembre 2026, problema 44)."""
        tentativo, ora_riletta = 0, False
        while True:
            p = dict(parametri or {})
            if firmata:                                # a ogni tentativo un'ora e una firma nuove (la finestra e' di 5 secondi)
                p["timestamp"] = int(time.time() * 1000) + self.scarto_ora_ms
                p["recvWindow"] = 5000
            q = urlencode(p)
            if firmata:
                q += "&signature=" + self.firma(q)
            try:
                r = self.http(metodo, self._url(percorso) + ("?" + q if q else ""), headers={"X-MBX-APIKEY": self.chiave}, timeout=15)
            except requests.RequestException as exc:
                pulito = senza_firma(str(exc))
                if pulito == str(exc):
                    raise
                try:
                    nuovo = type(exc)(pulito)
                except Exception:  # noqa: BLE001
                    nuovo = requests.RequestException(pulito)
                raise nuovo from None
            if firmata and not ora_riletta and r.status_code == 400 and _codice(r) == -1021:
                ora_riletta = True
                self._rileggi_ora()
                continue
            if r.status_code not in (418, 429):
                break
            attesa = _retry_after(r)
            if r.status_code == 418 and attesa is None:  # indirizzo bloccato: riprovare subito allunga il blocco
                attesa = ATTESA_418_SENZA_RETRY_S
            if tentativo >= RITENTATIVI_LIMITE or (attesa is not None and attesa > ATTESA_LIMITE_MAX_S):
                raise LimiteBinance(f"{metodo} {percorso}: {r.status_code} dopo {tentativo + 1} tentativi: {r.text[:120]}",
                                    attesa if attesa is not None else ATTESA_DOPO_LIMITE_S, r.status_code)
            time.sleep(attesa if attesa is not None else ATTESE_LIMITE_S[min(tentativo, len(ATTESE_LIMITE_S) - 1)])
            tentativo += 1
        if r.status_code >= 400:
            raise RuntimeError(f"{metodo} {percorso}: {r.status_code} {r.text[:200]}")
        return r.json()


class DemoG1:
    # il nome, i comandi e i limiti di questo conto: il conto vero (`conto_vero.ContoVeroG1`) li cambia con i suoi, senza copiare
    # il codice (fase 2 del piano del conto vero, `docs/conto_vero.md`)
    NOME = "demo_binance"                      # il ramo su Firebase (/demo_binance) e il prefisso del log
    HOST = HOST_DEMO
    COMANDO_CHIUDI, COMANDO_RIPARTI = COMANDO_CHIUDI, COMANDO_RIPARTI
    INTERRUTTORE_DI_SERIE, FILE_CAPITALE_DI_SERIE = INTERRUTTORE, FILE_CAPITALE
    FILE_COMANDI_DI_SERIE = (FILE_CHIUDI, FILE_RIPARTI)
    LEVA, STOP_CONTO, PAVIMENTO_RIPARTI, CAPITALE_MASSIMO = LEVA, STOP_CONTO, PAVIMENTO_RIPARTI, CAPITALE_MASSIMO
    SOMMA_PESI_MASSIMA, PESO_MASSIMO_MONETA = SOMMA_PESI_MASSIMA, PESO_MASSIMO_MONETA
    ETA_MASSIMA_DECISIONE_S = ETA_MASSIMA_DECISIONE_S
    MANCA_CHIAVE = "manca la chiave del conto demo (BINANCE_DEMO_API_KEY nel .env)"
    CHIAVE_VALORE_VERO = "valore_vero_del_conto_demo"
    CHIAVE_ILLEGGIBILE = "chiave del conto demo non leggibile"

    def __init__(self, fb, cliente: Optional[ClienteDemo] = None, file_stato: Path = FILE_STATO, file_g1: Path = FILE_G1,
                 interruttore: Path = INTERRUTTORE, file_eventi: Path = FILE_EVENTI,
                 interruttore_eventi: Path = INTERRUTTORE_EVENTI, file_chiudi: Path = FILE_CHIUDI,
                 file_riparti: Path = FILE_RIPARTI, file_capitale: Path = FILE_CAPITALE) -> None:
        self.fb = fb
        self.file_capitale = Path(file_capitale)
        self._scarto = 0.0                          # valore vero del conto demo meno il valore del conto ridotto
        self._protezioni_ferme_fino = 0.0
        self.file_chiudi, self.file_riparti = Path(file_chiudi), Path(file_riparti)
        self._cliente = cliente
        self.file_stato, self.file_g1, self.interruttore = Path(file_stato), Path(file_g1), Path(interruttore)
        self.file_eventi, self.interruttore_eventi = Path(file_eventi), Path(interruttore_eventi)
        self._ultimo_tentativo = 0.0
        self.capitale_errato: Optional[str] = None  # perché il capitale del file non si usa (problema 16)
        self._accesi = {"limiti_binance"}           # allarmi scritti da questo processo (quello dei limiti si toglie al primo giro buono)
        self._massimo_letto = False                 # il massimo dello stop letto da Firebase (problema 15)
        self._massimo_scritto: Optional[float] = None
        self._avviato = False                       # il log d'avvio (problema 22)
        self._valore_vero: Optional[float] = None   # il valore vero del conto all'ultima lettura (problema 41)

    # ---- stato ----
    def _livello_di_stop(self, st: dict) -> float:
        return livello_di_stop(st, self.STOP_CONTO, self.PAVIMENTO_RIPARTI)

    def _motivo_dello_stop(self, st: dict, equity: float) -> str:
        return motivo_dello_stop(st, equity, self.STOP_CONTO, self.PAVIMENTO_RIPARTI)

    def acceso(self) -> bool:
        if self.interruttore == self.INTERRUTTORE_DI_SERIE and os.environ.get("PYTEST_CURRENT_TEST"):
            return False
        return self.interruttore.exists()

    def eventi_accesi(self) -> bool:
        if self.interruttore_eventi == INTERRUTTORE_EVENTI and os.environ.get("PYTEST_CURRENT_TEST"):
            return False
        return self.interruttore_eventi.exists()

    def capitale_voluto(self) -> Optional[float]:
        """Il capitale del conto ridotto dal file `ops/demo_binance_capitale` (un numero in USDT); None se non c'è. Un valore non
        numerico, non positivo o sopra ``CAPITALE_MASSIMO`` non si usa: None, con il motivo in ``capitale_errato`` (problema 16)."""
        self.capitale_errato = None
        if self.file_capitale == self.FILE_CAPITALE_DI_SERIE and os.environ.get("PYTEST_CURRENT_TEST"):
            return None
        if not self.file_capitale.exists():
            return None
        try:
            t = self.file_capitale.read_text(encoding="utf-8").strip()
        except Exception as exc:  # noqa: BLE001
            self.capitale_errato = f"file del capitale illeggibile ({type(exc).__name__})"
            return None
        try:
            v = float(t.replace(",", "."))
        except ValueError:
            self.capitale_errato = f"capitale non numerico nel file: {t[:40]!r}"
            return None
        if not math.isfinite(v) or v <= 0 or v > self.CAPITALE_MASSIMO:
            self.capitale_errato = (f"capitale fuori dai limiti nel file: {t[:40]!r} (ammesso fino a {self.CAPITALE_MASSIMO:,.0f} "
                                    f"USDT)")
            return None
        return v

    def _allarme(self, st: dict, now: float, tipo: str, testo: Optional[str], **altro) -> None:
        """Gli allarmi del demo, uno per tipo in `/demo_binance/allarmi/{tipo}` (quello del conto non vuoto da fermo resta in
        `/demo_binance/allarme`): così non si cancellano a vicenda. Si scrivono quando cambiano e si tolgono quando la causa finisce;
        quelli accesi sono nello stato (``st['allarmi']``)."""
        accesi = st.setdefault("allarmi", {})
        if testo:
            if accesi.get(tipo) != testo:
                accesi[tipo] = testo
                self._accesi.add(tipo)
                self._scrivi(f"allarmi/{tipo}", {"ora": now, "testo": testo, **altro})
                print(f"[{self.NOME}] ALLARME ({tipo}): {testo}")
        elif tipo in accesi or tipo in self._accesi:
            accesi.pop(tipo, None)
            self._accesi.discard(tipo)
            self._scrivi(f"allarmi/{tipo}", None)

    def _archivia_fase(self, nome: str) -> None:
        """I valori della fase di prima passano in `/demo_binance/fasi/{nome}/`; si cancellano solo dopo la copia."""
        if self.fb is None:
            return
        for ramo in RAMI_DELLA_FASE:
            v = self.fb.get_rtdb(f"/{self.NOME}/{ramo}")
            if not isinstance(v, dict) or not v:
                continue
            self.fb.set_rtdb(f"/{self.NOME}/fasi/{nome}/{ramo}", v)
            for k in list(v):
                self.fb.set_rtdb(f"/{self.NOME}/{ramo}/{k}", None)

    def conto_ridotto(self, c: ClienteDemo, st: dict, now: float) -> dict:
        """Il demo come un conto più piccolo (vedi in cima). Un capitale nuovo nel file non parte subito: resta in attesa fino alla
        decisione di G1 dopo (la mezzanotte), dove `parti_da_zero` chiude tutto e riapre da zero. Il proprietario, 7 novembre 2026:
        «riparti a mezzanotte con il demo a 1000 [...] evita errore di apertura dei 280» (il 6 novembre il passaggio da 5.000 a 280
        a metà mattina era costato circa 11 USDT)."""
        voluto = self.capitale_voluto()
        cr = st.get("conto_ridotto")
        if (voluto and (not cr or float(cr["capitale"]) != voluto) and self._valore_vero is not None
                and voluto > self._valore_vero):    # problema 41: un capitale nuovo non oltre il valore vero del conto
            self.capitale_errato, voluto = self._capitale_oltre_il_saldo(voluto), None
        self._allarme(st, now, "capitale", self.capitale_errato and f"{self.capitale_errato}: resta il capitale in corso",
                      file=self.file_capitale.name)
        if voluto and (not cr or float(cr["capitale"]) != voluto):
            if st.get("capitale_in_attesa") != voluto:
                st["capitale_in_attesa"] = voluto
                self._scrivi("capitale_in_attesa", {"capitale": voluto, "chiesto": now})
                print(f"[{self.NOME}] capitale nuovo {voluto:g} USDT: parte alla prossima decisione di G1, dal conto vuoto")
        elif st.pop("capitale_in_attesa", None) is not None:
            self._scrivi("capitale_in_attesa", None)
        self._scarto = float(cr["valore_vero_all_avvio"]) - float(cr["capitale"]) if cr else 0.0
        return st

    @staticmethod
    def _capitale_oltre_il_saldo(voluto: float) -> str:
        return f"capitale {voluto:g} USDT nel file, sopra il valore vero del conto"

    def parti_da_zero(self, c: ClienteDemo, st: dict, now: float) -> dict:
        """Alla decisione di G1, se c'è un capitale in attesa: annulla gli ordini, chiude tutte le posizioni a mercato (le spese vanno
        alla fase che finisce), archivia la fase, fissa lo scarto sul conto vuoto e lascia che il ribilancio apra tutto da zero, come
        farà il conto vero (`docs/backlog.md`, P26: il primo ingresso alla mezzanotte)."""
        voluto = st.get("capitale_in_attesa")
        if not voluto:
            return st
        cr = st.get("conto_ridotto")
        scarto_prima, self._scarto = self._scarto, 0.0
        self._conto(c)
        vero_prima = float(self._valore_vero)
        if float(voluto) > vero_prima:                 # problema 41: prima di chiudere niente, il capitale contro il valore vero
            self._scarto = scarto_prima
            self.capitale_errato = self._capitale_oltre_il_saldo(float(voluto))
            self._allarme(st, now, "capitale", f"{self.capitale_errato}: resta il capitale in corso", file=self.file_capitale.name,
                          valore_vero=round(vero_prima, 2))
            st.pop("capitale_in_attesa", None)
            self._scrivi("capitale_in_attesa", None)
            return st
        for s in sorted({o["symbol"] for o in c.chiedi("GET", "/fapi/v1/openOrders", firmata=True) or []}):
            c.chiedi("DELETE", "/fapi/v1/allOpenOrders", {"symbol": s}, firmata=True)
        _, _, posizioni = self._conto(c)
        chiuse, errori = [], []
        fm = self._filtri_per_chiudere(c) if posizioni else {}
        for s, q in sorted(posizioni.items()):
            try:
                self._chiudi_moneta(c, s, q, fm)
                chiuse.append(s)
            except RuntimeError as exc:
                errori.append({"simbolo": s, "errore": str(exc)[:200]})
        if chiuse:
            time.sleep(ATTESA_DOPO_CHIUSURA_S)
        self._conto(c)
        vero = float(self._valore_vero)
        data = time.strftime("%Y-%m-%d", time.gmtime(now))
        prima = f"capitale_{float(cr['capitale']):g}" if cr else "conto_intero"
        self._archivia_fase(f"{prima}_fino_al_{data}".replace(".", "_"))
        cr = {"capitale": float(voluto), "valore_vero_all_avvio": vero, "dal": now, "data": data, "da_zero": True,
              "chiuse_prima": len(chiuse), "errori_di_chiusura": errori}
        st["conto_ridotto"] = cr
        st["capitale_iniziale"] = float(voluto)
        self._fissa_massimo(st, float(voluto), now, nuova_serie=True)
        for k in ("obiettivi", "ultima_valutazione", "capitale_in_attesa"):
            st.pop(k, None)
        self._scarto = vero - float(voluto)
        self._scrivi("conto_ridotto", cr)
        self._scrivi("capitale_in_attesa", None)
        print(f"[{self.NOME}] conto ridotto da zero: {voluto:g} USDT (chiuse {len(chiuse)} posizioni, {len(errori)} errori; "
              f"valore vero {vero:,.2f})")
        self.salva(st)          # revisione dell'8 novembre 2026, problema 62: un errore nel ribilancio dopo non la ripete
        return st

    def eventi_aperti(self) -> dict:
        if not self.eventi_accesi():
            return {}
        try:
            return dict(json.loads(self.file_eventi.read_text(encoding="utf-8")).get("aperte") or {})
        except Exception:  # noqa: BLE001
            return {}

    def cliente(self) -> Optional[ClienteDemo]:
        if self._cliente is None:
            k, s = os.environ.get("BINANCE_DEMO_API_KEY", ""), segreto_dall_ambiente()
            if k and s:
                self._cliente = ClienteDemo(k, s)
        return self._cliente

    def carica(self) -> dict:
        try:
            return json.loads(self.file_stato.read_text(encoding="utf-8"))
        except Exception:  # noqa: BLE001
            return {}

    def salva(self, st: dict) -> None:
        self.file_stato.parent.mkdir(parents=True, exist_ok=True)
        tmp = self.file_stato.with_suffix(".tmp")
        tmp.write_text(json.dumps(st, ensure_ascii=False), encoding="utf-8")
        tmp.replace(self.file_stato)

    def _scrivi(self, ramo: str, valore) -> None:
        if self.fb is not None:
            self.fb.set_rtdb(f"/{self.NOME}/{ramo}", valore)

    # ---- il massimo dello stop sul conto, anche su Firebase (revisione del 7 novembre 2026, problema 15) ----
    def _fissa_massimo(self, st: dict, valore: float, now: float, nuova_serie: bool = False) -> None:
        """Il massimo nel file e in `/demo_binance/massimo` (con ``dal``, l'ora in cui la serie è partita: un capitale nuovo o un
        «riparti» ne aprono una nuova). Su Firebase si scrive all'avvio, a ogni serie nuova e quando sale di oltre lo 0,1%."""
        if nuova_serie or st.get("massimo_dal") is None:
            st["massimo_dal"] = now
        st["massimo"] = float(valore)
        if nuova_serie or self._massimo_scritto is None or valore > self._massimo_scritto * 1.001:
            self._scrivi("massimo", {"valore": round(float(valore), 2), "dal": st["massimo_dal"], "ora": now})
            self._massimo_scritto = float(valore)

    def _unisci_massimo(self, st: dict) -> None:
        """All'avvio, e ogni volta che il file non ha il massimo (file perso o illeggibile: ``carica`` dà {}), vale il più alto fra
        il file e Firebase; quello di Firebase solo se è della stessa serie del file, o se il file non dice niente (così una
        scrittura non arrivata dopo un «riparti» non riporta il massimo vecchio)."""
        if self.fb is None or (self._massimo_letto and st.get("massimo") is not None):
            return
        self._massimo_letto = True
        try:
            v = self.fb.get_rtdb(f"/{self.NOME}/massimo")
            valore, dal = float(v["valore"]), v.get("dal")
        except Exception:  # noqa: BLE001
            return
        if not math.isfinite(valore):
            return
        nel_file = st.get("massimo")
        if nel_file is None or st.get("massimo_dal") is None or st.get("massimo_dal") == dal:
            if nel_file is None or valore > float(nel_file):
                print(f"[{self.NOME}] massimo dello stop ripreso da Firebase: {valore:,.2f} (nel file: {nel_file})")
                st["massimo"], st["massimo_dal"] = valore, dal

    def _comando(self, percorso: Optional[str]) -> bool:
        if self.fb is None or not percorso:
            return False
        try:
            return bool(self.fb.get_rtdb(percorso))
        except Exception:  # noqa: BLE001
            return False

    def _comando_file(self, f: Path, st: dict, chiave: str) -> bool:
        """Il comando come file: vale una volta per ogni testo nuovo (il file resta nel repository)."""
        if os.environ.get("PYTEST_CURRENT_TEST") and f in self.FILE_COMANDI_DI_SERIE:
            return False
        try:
            testo_file = f.read_text(encoding="utf-8").strip() if f.exists() else ""
        except Exception:  # noqa: BLE001
            return False
        if testo_file and testo_file != st.get(chiave):
            st[chiave] = testo_file
            return True
        return False

    def chiudi_tutto(self, c: ClienteDemo, st: dict, now: float, motivo: str, equity: Optional[float] = None) -> dict:
        """Annulla tutti gli ordini aperti e chiude tutte le posizioni a mercato; poi il demo resta fermo (``st['fermo']``). Da fermo,
        ``_da_fermo`` richiude ogni minuto quello che resta finché il conto è vuoto (revisione del 7 novembre 2026, problema 3).
        Il fermo si scrive e si salva PRIMA delle chiusure (revisione dell'8 novembre 2026, problema 40): se Binance limita le
        richieste a metà (``LimiteBinance``) o c'è un altro errore, il demo resta fermo con il tentativo e l'errore segnati, l'errore
        risale (l'attesa resta) e dopo ``_da_fermo`` richiude quello che manca."""
        ultime = set(st.get("obiettivi") or {}) | {o.get("simbolo") for o in (st.get("ordini") or {}).get("lista") or []}
        st.pop("ordini", None)
        self._allarme(st, now, "ordini", None)        # gli ordini bloccati li toglie questa chiusura (problema 46)
        fermo = {"motivo": motivo, "ora": now, "equity": None if equity is None else round(equity, 2), "chiuse": 0, "errori": [],
                 "tentativi": 0, "ultimo_controllo": now}
        st["fermo"] = fermo
        fermo["riparti_pulito"] = self._pulisci_riparti(st)
        self._scrivi("fermo", fermo)
        self.salva(st)
        try:
            equity, _, posizioni = self._conto(c)
            chiuse, errori = self._chiudi_posizioni(c, posizioni, anche=ultime)
        except Exception as exc:  # noqa: BLE001
            fermo["tentativi"], fermo["chiuse"] = 1, len(getattr(exc, "chiuse", []))
            fermo["errori"] = list(getattr(exc, "errori", [])) or [{"simbolo": "*", "errore": senza_firma(exc)[:200]}]
            self._scrivi("fermo", fermo)
            self.salva(st)
            print(f"[{self.NOME}] CHIUDI TUTTO interrotto ({motivo}): fermo segnato, si richiude dopo: {senza_firma(exc)[:150]}")
            raise
        fermo.update({"equity": round(equity, 2), "chiuse": len(chiuse), "errori": errori, "tentativi": 1})
        self._scrivi("fermo", fermo)
        self._scrivi("stato", {"stato": f"fermo: {motivo}", "equity": round(equity, 2), "aggiornato": now,
                               "capitale_iniziale": float(st.get("capitale_iniziale", equity))})
        print(f"[{self.NOME}] CHIUSO TUTTO ({motivo}): {len(chiuse)} posizioni chiuse, {len(errori)} errori")
        return st

    # ---- il giro ----
    def tick(self, now: float) -> None:
        if not self.acceso():
            return
        try:
            c = self.cliente()
        except Exception as exc:  # noqa: BLE001
            self._scrivi("stato", {"stato": f"{self.CHIAVE_ILLEGGIBILE}: {type(exc).__name__}", "aggiornato": now})
            return
        if c is None:
            self._scrivi("stato", {"stato": self.MANCA_CHIAVE, "aggiornato": now})
            return
        if not self._avviato:
            self._avviato = True
            self._log_d_avvio(now)
            try:                                       # gli allarmi già scritti si spengono anche con lo stato perso (problema 46)
                scritti = self.fb.get_rtdb(f"/{self.NOME}/allarmi") if self.fb is not None else None
                self._accesi |= {k for k, v in scritti.items() if v} if isinstance(scritti, dict) else set()
            except Exception:  # noqa: BLE001
                pass
        # le protezioni (pulsante, stop sul conto, conto vuoto da fermo, «riparti») girano a OGNI giro, anche dopo un errore
        # (revisione del 7 novembre 2026, problemi 2-4); l'attesa dopo un errore vale solo per il ribilancio
        if now < self._protezioni_ferme_fino:         # dopo un errore nelle protezioni si riprova fra un minuto (problema 28)
            return
        try:
            st = self.carica()
            st = self.conto_ridotto(c, st, now)
            st = self.protezioni(c, st, now)
            self._allarme(st, now, "limiti_binance", None)
            self.salva(st)
        except LimiteBinance as exc:
            self._limite_di_binance(now, exc, "protezioni")
            return
        except Exception as exc:  # noqa: BLE001
            self._protezioni_ferme_fino = now + OGNI_CONTROLLO_STOP_S
            testo_errore = senza_firma(exc)
            print(f"[{self.NOME}] errore nelle protezioni, si riprova fra un minuto: {testo_errore}")
            self._scrivi("errore", {"testo": testo_errore[:300], "ora": now, "dove": "protezioni"})
            return
        if st.get("fermo"):
            return
        if now - self._ultimo_tentativo < ATTESA_DOPO_ERRORE_S and self._ultimo_tentativo:
            return
        try:
            if self._ordini_nuovi_ammessi(c, st, now):  # sempre sul demo; il conto vero ha le sue condizioni (conto_vero.py)
                st = self._ordini_del_giro(c, st, now)
            if now - float(st.get("ultima_valutazione", 0)) >= OGNI_VALUTAZIONE_S:
                st = self.valuta(c, st, now)
                if not st.get("fermo"):
                    st = self.controlla_margine(c, st, now)
                    st = self.confronta(c, st, now)
            self.salva(st)
        except LimiteBinance as exc:
            self._ultimo_tentativo = now
            self._limite_di_binance(now, exc, "ribilancio")
        except Exception as exc:  # noqa: BLE001
            self._ultimo_tentativo = now
            testo_errore = senza_firma(exc)
            print(f"[{self.NOME}] errore, si riprova fra 30 minuti: {testo_errore}")
            self._scrivi("errore", {"testo": testo_errore[:300], "ora": now})

    def _ordini_nuovi_ammessi(self, c: ClienteDemo, st: dict, now: float) -> bool:
        """Se il giro può mandare ordini nuovi (il resto a mercato, il ribilancio di G1, gli eventi). Sul demo sempre; il conto vero
        (`conto_vero.ContoVeroG1`) lo permette solo con tutte le sue condizioni. Le protezioni e la valutazione girano comunque."""
        return True

    def _ordini_del_giro(self, c: ClienteDemo, st: dict, now: float) -> dict:
        """I passi del giro che mandano ordini: il resto a mercato dopo l'ora, la decisione nuova di G1, le operazioni a eventi."""
        if st.get("ordini") and now >= float(st["ordini"]["piazzati"]) + VALIDITA_LIMITE_S:
            st = self.chiudi_ordini(c, st, now)
        if not st.get("ordini"):                   # nessun ribilancio in corso: niente ordini bloccati (problema 46)
            self._allarme(st, now, "ordini", None)
        if int(st.get("ultimo_giorno", 0)) * 86400 > now + 3600:   # problema 45: un giorno nel futuro fermerebbe ogni decisione
            print(f"[{self.NOME}] giorno dell'ultimo ribilancio nel futuro ({st['ultimo_giorno']}): si azzera")
            st["ultimo_giorno"] = 0
        g1 = json.loads(self.file_g1.read_text(encoding="utf-8")) if self.file_g1.exists() else {}
        giorno = int(g1.get("ultimo_lunedi", 0))
        aperte = self.eventi_aperti()
        firma, monete_eventi = sorted(aperte), sorted({p.get("simbolo") for p in aperte.values() if p.get("simbolo")})
        pesi_g1, pesi_ev = g1.get("pesi") or {}, pesi_eventi(aperte)
        fuori = pesi_fuori_dai_limiti(pesi_g1, pesi_ev, somma_massima=self.SOMMA_PESI_MASSIMA,
                                      peso_massimo=self.PESO_MASSIMO_MONETA)
        pesi = somma_pesi(pesi_g1, pesi_ev) if not fuori else {}
        if self._decisione_da_non_eseguire(st, now, giorno, fuori):
            pass                                   # problemi 10 e 12: niente ordini nuovi, l'allarme è scritto
        elif giorno and giorno > int(st.get("ultimo_giorno", 0)) and not st.get("ordini"):
            st = self.parti_da_zero(c, st, now)
            st = self.ribilancia(c, st, pesi, giorno, now)
            st["eventi_firma"], st["eventi_monete"] = firma, monete_eventi
            st.pop("riparti_attende_g1", None)
        elif (firma != list(st.get("eventi_firma") or []) and not st.get("ordini") and int(st.get("ultimo_giorno", 0))
              and not st.get("riparti_attende_g1")      # dopo un «riparti» si aspetta la decisione di G1 (decisione 3)
              and (int(st["ultimo_giorno"]) >= int(now // 86400) or now >= int(now // 86400) * 86400 + ATTESA_G1_S)):
            toccate = set(monete_eventi) | set(st.get("eventi_monete") or []) | {"BTCUSDT"}
            st = self.ribilancia(c, st, pesi, int(st["ultimo_giorno"]), now, solo=toccate)
            st["eventi_firma"], st["eventi_monete"] = firma, monete_eventi
        return st

    def _limite_di_binance(self, now: float, exc: LimiteBinance, dove: str) -> None:
        """Problema 13: Binance limita le richieste anche dopo i ritentativi. Nessuna richiesta, nemmeno delle protezioni, per
        l'attesa chiesta da Binance (almeno un minuto: insistere porta al blocco dell'indirizzo, 418); errore e allarme. Per un 429
        l'attesa ha un tetto di 10 minuti; per un 418 si rispetta tutta, e l'allarme dice fino a quando il conto resta senza
        protezioni. L'allarme si
        toglie al primo giro di protezioni riuscito. Lo stato non si salva qui (``carica`` darebbe {} con il file illeggibile)."""
        attesa = max(OGNI_CONTROLLO_STOP_S, exc.attesa_s)
        if exc.codice != 418:                          # 429: tetto di 10 minuti (problema 44); 418: tutto il blocco di Binance
            attesa = min(attesa, ATTESA_LIMITE_TETTO_S)
        self._protezioni_ferme_fino = max(self._protezioni_ferme_fino, now + attesa)
        testo_errore = senza_firma(exc)
        if exc.codice != 418 and exc.attesa_s > ATTESA_LIMITE_TETTO_S:
            testo_errore += f"; Binance chiedeva {exc.attesa_s:.0f} secondi, si riprova dopo {ATTESA_LIMITE_TETTO_S:.0f}"
        print(f"[{self.NOME}] limiti di Binance ({dove}): {testo_errore}; nessuna richiesta per {attesa:.0f} secondi")
        self._scrivi("errore", {"testo": testo_errore[:300], "ora": now, "dove": dove})
        self._accesi.add("limiti_binance")
        if exc.codice == 418:
            fino = time.strftime("%H:%M:%S UTC del %Y-%m-%d", time.gmtime(now + attesa))
            testo = (f"indirizzo bloccato da Binance (418) fino alle {fino}: fino ad allora il bot non può proteggere il conto "
                     f"(pulsante e stop sul conto fermi, resta solo la liquidazione di Binance) ({dove}): {testo_errore[:150]}")
        else:
            testo = f"Binance limita le richieste ({dove}): {testo_errore[:200]}"
        self._scrivi("allarmi/limiti_binance", {"ora": now, "testo": testo, "riprende": now + attesa, "codice": exc.codice})

    def _decisione_da_non_eseguire(self, st: dict, now: float, giorno: int, fuori: Optional[str]) -> bool:
        """Problemi 10, 12, 42 e 45: la decisione di G1 non si esegue (niente ordini nuovi, nemmeno quelli degli eventi) se è più
        vecchia di ``ETA_MASSIMA_DECISIONE_S`` (il paper di G1 si è fermato: il demo terrebbe le stesse posizioni senza limite), se ha
        una data nel futuro, o se i pesi sono vuoti o fuori dai limiti; allarme in tutti e due i casi, tolto quando la causa finisce. Gli ordini già piazzati finiscono lo stesso."""
        if not giorno:
            vecchia = "nessuna decisione di G1 nel file: niente ordini nuovi"
        elif giorno * 86400 > now + 3600:              # problema 45: una data nel futuro non si esegue (bloccherebbe le vere)
            vecchia = (f"la decisione di G1 ha una data nel futuro ({time.strftime('%Y-%m-%d', time.gmtime(giorno * 86400))}): "
                       f"niente ordini nuovi")
        elif now - giorno * 86400 > self.ETA_MASSIMA_DECISIONE_S:
            vecchia = (f"la decisione di G1 è del {time.strftime('%Y-%m-%d', time.gmtime(giorno * 86400))}, "
                       f"{(now - giorno * 86400) / 3600:.0f} ore fa (oltre {self.ETA_MASSIMA_DECISIONE_S // 3600}): niente ordini nuovi "
                       f"finché il paper di G1 non decide di nuovo")
        else:
            vecchia = None
        self._allarme(st, now, "decisione_g1", vecchia)
        self._allarme(st, now, "pesi", fuori and f"pesi di G1 fuori dai limiti, niente ordini: {fuori}")
        return bool(vecchia or fuori)

    def _ambiente(self, now: float) -> dict:
        return {"ora": now, "indirizzo": self.HOST, "leva": self.LEVA, "stop_sul_conto": self.STOP_CONTO,
                "capitale_nel_file": self.capitale_voluto(), "capitale_errato": self.capitale_errato,
                "capitale_massimo": self.CAPITALE_MASSIMO, "eventi_accesi": self.eventi_accesi(),
                "filtri_del_conto_vero_del": DATA_FILTRI_VERI, "somma_pesi_massima": self.SOMMA_PESI_MASSIMA,
                "peso_massimo_moneta": self.PESO_MASSIMO_MONETA,
                "eta_massima_decisione_ore": self.ETA_MASSIMA_DECISIONE_S // 3600, "pavimento_riparti": self.PAVIMENTO_RIPARTI}

    def _log_d_avvio(self, now: float) -> None:
        """Problema 22: all'avvio, nel log e su Firebase (`/demo_binance/avvio`), l'ambiente in cui il demo lavora."""
        amb = self._ambiente(now)
        print(f"[{self.NOME}] avvio: " + ", ".join(f"{k} {v}" for k, v in amb.items() if k != "ora"))
        self._scrivi("avvio", amb)

    # ---- le protezioni (revisione del 7 novembre 2026, problemi 2-4) ----
    def protezioni(self, c: ClienteDemo, st: dict, now: float) -> dict:
        """Pulsante che chiude tutto e stop sul conto a ogni giro (lo stop: lettura del conto al massimo ogni minuto); da fermo, il
        conto vuoto e il «riparti»."""
        da_dashboard = self._comando(self.COMANDO_CHIUDI)
        da_file = self._comando_file(self.file_chiudi, st, "eseguito_chiudi")
        if da_dashboard or da_file:
            if not st.get("fermo"):
                st = self.chiudi_tutto(c, st, now, "pulsante della dashboard" if da_dashboard else "comando chiudi tutto")
            if da_dashboard:
                self.fb.set_rtdb(self.COMANDO_CHIUDI, False)
        if st.get("fermo"):
            return self._da_fermo(c, st, now)
        self._allarme(st, now, "riparti", None)       # acceso: l'allarme del «riparti» rifiutato non vale più (problema 46)
        self._unisci_massimo(st)
        if now - float(st.get("ultimo_controllo_stop", 0)) >= OGNI_CONTROLLO_STOP_S:
            st["ultimo_controllo_stop"] = now
            equity = self._conto(c)[0]
            iniziale = float(st.setdefault("capitale_iniziale", equity))
            self._fissa_massimo(st, max(float(st.get("massimo", iniziale)), equity), now)
            if equity <= self._livello_di_stop(st):
                st = self.chiudi_tutto(c, st, now, self._motivo_dello_stop(st, equity), equity=equity)
        return st

    def _da_fermo(self, c: ClienteDemo, st: dict, now: float) -> dict:
        """Da fermo: il «riparti» vale solo dopo che il comando vecchio è stato pulito; ogni minuto si rileggono le posizioni e si
        richiude quello che resta, con un allarme se dopo 3 tentativi il conto non è vuoto."""
        fermo = st["fermo"]
        prima_file = st.get("eseguito_riparti")
        da_file = self._comando_file(self.file_riparti, st, "eseguito_riparti")    # il file non ha bisogno di Firebase (problema 27)
        if not da_file and not fermo.get("riparti_pulito"):
            fermo["riparti_pulito"] = self._pulisci_riparti(st, solo_firebase=True)
        elif da_file or self._comando(self.COMANDO_RIPARTI):
            sopra = self._riparti_ammesso(c, st, now)       # prima di consumare il comando: un errore qui lo lascia (problema 46)
            if sopra is None:
                # il conto o gli ordini non si leggono (problema 50): il comando resta per il giro dopo (quello della dashboard non
                # si consuma; quello del file torna da eseguire) e qui sotto le chiusure del minuto continuano
                if da_file:
                    if prima_file is None:
                        st.pop("eseguito_riparti", None)
                    else:
                        st["eseguito_riparti"] = prima_file
            elif (da_file or self._riparti(st)) and sopra:
                st.pop("fermo")
                # il conto resta vuoto fino alla prima decisione di G1 dopo il «riparti», anche con un capitale nuovo, come
                # `parti_da_zero` (revisione dell'8 novembre 2026, decisione 3: il conto vero compra alla mezzanotte)
                st["ultimo_giorno"] = max(int(st.get("ultimo_giorno") or 0), self._giorno_g1(now))
                st["riparti_attende_g1"] = True
                self._fissa_massimo(st, self._conto(c)[0], now, nuova_serie=True)   # lo stop si misura dalla ripartenza
                self._scrivi("fermo", None)
                print(f"[{self.NOME}] ripartito: si riapre alla prossima decisione di G1")
                return st
        if now - float(fermo.get("ultimo_controllo", 0)) < OGNI_CONTROLLO_STOP_S:
            return st
        fermo["ultimo_controllo"] = now
        try:
            equity, _, posizioni = self._conto(c)
            try:
                aperti = c.chiedi("GET", "/fapi/v1/openOrders", firmata=True) or []
            except (RuntimeError, requests.RequestException):
                # non si leggono (risposta d'errore o guasto di rete: è solo una lettura, problemi 32 e 37): non si sa se ci sono
                # ordini, quindi si richiude e si annulla lo stesso, anche sulle monete dell'ultimo ribilancio, e il conto non è
                # «vuoto» (36)
                aperti = None
        except LimiteBinance as exc:                  # nemmeno il conto si legge: il tentativo conta lo stesso (problema 49)
            fermo["tentativi"] = int(fermo.get("tentativi", 0)) + 1
            fermo.pop("vuoto", None)
            fermo["errori"] = [{"simbolo": "*", "errore": f"limiti di Binance: {senza_firma(exc)[:150]}"}]
            self._allarme_del_fermo(fermo, now, "il conto non si legge (Binance limita le richieste)", [])
            self._scrivi("fermo", fermo)
            self.salva(st)
            raise
        if posizioni or aperti or aperti is None:     # anche gli ordini rimasti aperti senza posizioni (problema 31)
            fermo["tentativi"] = int(fermo.get("tentativi", 0)) + 1
            fermo.pop("vuoto", None)                  # ricompaiono posizioni o ordini, o non si sa (problema 36)
            limite = None
            try:
                chiuse, errori = self._chiudi_posizioni(c, posizioni, anche=set(st.get("obiettivi") or {}) if aperti is None else ())
            except LimiteBinance as exc:              # il tentativo conta lo stesso; si salva e l'errore risale (problema 40)
                limite, errori = exc, list(getattr(exc, "errori", []))
            fermo["errori"] = errori
            self._allarme_del_fermo(fermo, now, "il conto non è vuoto" if posizioni or aperti else "gli ordini aperti non si leggono",
                                    sorted(posizioni))
            self._scrivi("fermo", fermo)
            if limite is not None:
                self.salva(st)
                raise limite
        elif not fermo.get("vuoto"):
            fermo["vuoto"] = now
            self._scrivi("fermo", fermo)
            self._scrivi("allarme", None)
        if now - float(st.get("ultima_valutazione", 0)) >= OGNI_VALUTAZIONE_S:
            st["ultima_valutazione"] = now
            self._scrivi(f"giorni/{time.strftime('%Y-%m-%d', time.gmtime(now))}", round(equity, 2))
        return st

    def _allarme_del_fermo(self, fermo: dict, now: float, cosa: str, posizioni: list) -> None:
        """Da fermo, dopo ``TENTATIVI_PRIMA_DELL_ALLARME`` tentativi che non svuotano il conto: allarme in `/demo_binance/allarme`."""
        if fermo["tentativi"] >= TENTATIVI_PRIMA_DELL_ALLARME:
            allarme = {"ora": now, "testo": f"fermo ma {cosa} dopo {fermo['tentativi']} tentativi", "posizioni": posizioni,
                       "errori": fermo.get("errori") or []}
            self._scrivi("allarme", allarme)
            print(f"[{self.NOME}] ALLARME: {allarme['testo']}: {posizioni}")

    def _riparti_ammesso(self, c: ClienteDemo, st: dict, now: float) -> Optional[bool]:
        """Problemi 23 e 48: «riparti» riaccende il demo solo se il conto vale più del ``PAVIMENTO_RIPARTI`` del capitale di partenza
        della fase (allo stesso valore lo stop riscatterebbe al minuto dopo; con un capitale nuovo in attesa il pavimento non conta:
        la decisione di G1 dopo riparte da zero con quello) e solo con il conto vuoto, senza posizioni e senza ordini (riletti qui:
        prima una posizione rimasta restava da sola fino alla decisione dopo). Altrimenti il comando si consuma, il demo resta fermo,
        le chiusure continuano e l'allarme `riparti` dice perché. Se il conto o gli ordini non si leggono (risposta d'errore o guasto
        di rete) torna None: il comando resta per il giro dopo e le chiusure del minuto continuano (revisione dell'8 novembre 2026,
        problema 50; prima l'errore risaliva e fermava le chiusure, come nel 32). ``LimiteBinance`` invece risale."""
        base = float(st.get("capitale_iniziale") or (st.get("conto_ridotto") or {}).get("capitale") or 0)
        try:
            equity, _, posizioni = self._conto(c)
            aperti = sorted({o["symbol"] for o in c.chiedi("GET", "/fapi/v1/openOrders", firmata=True) or []})
        except (RuntimeError, requests.RequestException) as exc:
            print(f"[{self.NOME}] «riparti» rimandato: il conto o gli ordini non si leggono ({senza_firma(exc)[:150]})")
            return None
        if base > 0 and equity <= self.PAVIMENTO_RIPARTI * base and not st.get("capitale_in_attesa"):
            motivo = (f"«riparti» non eseguito: il conto vale {equity:,.2f} USDT, non sopra il {100 * self.PAVIMENTO_RIPARTI:.0f}% "
                      f"del capitale di partenza ({base:,.2f}); serve un capitale nuovo dal proprietario (ops/{self.file_capitale.name}), "
                      f"poi «riparti»")
        elif posizioni or aperti:
            motivo = (f"«riparti» non eseguito: il conto non è vuoto (posizioni: {', '.join(sorted(posizioni)) or 'nessuna'}; "
                      f"ordini aperti: {', '.join(aperti) or 'nessuno'}); il conto resta fermo e richiude, poi «riparti» di nuovo")
        else:
            self._allarme(st, now, "riparti", None)
            return True
        self._allarme(st, now, "riparti", motivo)
        return False

    def _chiudi_posizioni(self, c: ClienteDemo, posizioni: dict, anche=()) -> tuple:
        """Annulla gli ordini aperti e chiude a mercato con «solo riduzione»; un errore su una moneta non ferma le altre. Se gli
        ordini aperti non si leggono (anche per un guasto di rete, problema 37) si annulla sulle monete con una posizione e su
        quelle di ``anche`` (l'ultimo ribilancio, problema 36)."""
        errori, chiuse = [], []
        try:
            try:
                aperti = sorted({o["symbol"] for o in c.chiedi("GET", "/fapi/v1/openOrders", firmata=True) or []})
            except (RuntimeError, requests.RequestException) as exc:
                aperti = sorted(set(posizioni) | {s for s in anche or () if s})
                errori.append({"simbolo": "*", "errore": f"ordini aperti non letti: {senza_firma(exc)[:150]}"})
            for s in aperti:
                try:
                    c.chiedi("DELETE", "/fapi/v1/allOpenOrders", {"symbol": s}, firmata=True)
                except RuntimeError as exc:
                    errori.append({"simbolo": s, "errore": f"annullo: {str(exc)[:150]}"})
            fm = self._filtri_per_chiudere(c) if posizioni else {}
            for s, q in sorted(posizioni.items()):
                try:
                    self._chiudi_moneta(c, s, q, fm)
                    chiuse.append(s)
                except RuntimeError as exc:
                    errori.append({"simbolo": s, "errore": str(exc)[:200]})
        except LimiteBinance as exc:                  # chi chiama segna quello che è stato fatto prima del limite (problema 40)
            errori.append({"simbolo": "*", "errore": f"limiti di Binance: {senza_firma(exc)[:150]}"})
            exc.chiuse, exc.errori = chiuse, errori
            raise
        return chiuse, errori

    def _filtri_per_chiudere(self, c: ClienteDemo) -> dict:
        """I filtri a mercato per dividere le chiusure (problema 43); se non si leggono, le chiusure partono intere."""
        try:
            return filtri_mercato(c.chiedi("GET", "/fapi/v1/exchangeInfo"))
        except (RuntimeError, requests.RequestException):
            return {}

    def _chiudi_moneta(self, c: ClienteDemo, s: str, q: float, fm: dict) -> None:
        """Chiude a mercato con «solo riduzione» la posizione ``q`` di ``s``, in pezzi dentro la quantità massima a mercato
        (revisione dell'8 novembre 2026, problema 43: sopra il massimo Binance rifiuta e la chiusura fallirebbe ogni minuto). Un
        rifiuto ferma i pezzi dopo: il resto si richiude al tentativo dopo, dalla posizione vera."""
        passo, _, massimo, _ = fm.get(s, (0.0, 0.0, math.inf, math.inf))
        for pezzo in pezzi_di_chiusura(q, massimo, passo):
            c.chiedi("POST", "/fapi/v1/order", {"symbol": s, "side": "SELL" if q > 0 else "BUY", "type": "MARKET",
                                                "quantity": testo(pezzo), "reduceOnly": "true"}, firmata=True)

    def _giorno_g1(self, now: float) -> int:
        """Il giorno della decisione di G1 nel file (quello di oggi se il file non si legge o ha una data nel futuro)."""
        try:
            g = int(json.loads(self.file_g1.read_text(encoding="utf-8")).get("ultimo_lunedi", 0))
        except Exception:  # noqa: BLE001
            g = 0
        return g if 0 < g and g * 86400 <= now + 3600 else int(now // 86400)

    def _pulisci_riparti(self, st: dict, solo_firebase: bool = False) -> bool:
        """All'entrata nel fermo il «riparti» vecchio non vale: il testo del file si segna come già visto (solo all'entrata, così un
        testo scritto dopo vale) e il comando della dashboard si rimette a falso. Vero solo se la scrittura è confermata (``set_rtdb``
        del client vero restituisce False se non è arrivata)."""
        if not solo_firebase:
            try:
                st["eseguito_riparti"] = (self.file_riparti.read_text(encoding="utf-8").strip()
                                          if self.file_riparti.exists() else st.get("eseguito_riparti", ""))
            except Exception:  # noqa: BLE001
                pass
        if self.fb is None or not self.COMANDO_RIPARTI:
            return True
        try:
            return self.fb.set_rtdb(self.COMANDO_RIPARTI, False) is not False
        except Exception:  # noqa: BLE001
            return False

    def _riparti(self, st: dict) -> bool:
        """Il «riparti»: dal file, una volta per testo nuovo; dalla dashboard, solo se il comando si consuma davvero (la scrittura
        del falso confermata), così un comando rimasto vero non riaccende il demo da solo (revisione del 7 novembre 2026, problema 4).
        Il file lo legge già ``_da_fermo``."""
        if not self._comando(self.COMANDO_RIPARTI):
            return False
        try:
            ok = self.fb.set_rtdb(self.COMANDO_RIPARTI, False) is not False
        except Exception:  # noqa: BLE001
            ok = False
        if not ok:
            print(f"[{self.NOME}] «riparti» non eseguito: il comando non si è potuto consumare su Firebase; si riprova al giro dopo")
        return ok

    def _ordini_bloccati(self, st: dict, now: float, simboli: list) -> None:
        """Un ordine che non si riesce ad annullare blocca il resto a mercato (giusto: niente posizione doppia); se dura oltre 2 ore,
        allarme (revisione del 7 novembre 2026, problema 33) in `/demo_binance/allarmi/ordini`, non più nella chiave del fermo
        (problema 38). Si contano solo i blocchi di fila: se dall'ultimo blocco sono passati più di 45 minuti, in mezzo c'è stato un
        tentativo che non si è bloccato qui, e si riparte da adesso (dal problema 46 la soglia è 45 minuti: due tentativi di fila
        distano 30 minuti e qualche secondo, uno in mezzo li porta a 60); ``chiudi_ordini`` toglie ``bloccato_dal`` dopo un controllo
        riuscito e l'allarme quando arriva in fondo."""
        ordini = st["ordini"]
        if now - float(ordini.get("bloccato_ultimo", now)) > 1.5 * ATTESA_DOPO_ERRORE_S:
            ordini.pop("bloccato_dal", None)
        ordini.setdefault("bloccato_dal", now)
        ordini["bloccato_ultimo"] = now
        if now - float(ordini["bloccato_dal"]) >= 2 * 3600:
            self._allarme(st, now, "ordini", f"ordini aperti che non si annullano da oltre 2 ore: {sorted(simboli)}",
                          monete=sorted(simboli))
        self.salva(st)

    def _ordine_esiste(self, c: ClienteDemo, simbolo: str, cid: str) -> bool:
        """Vero se un ordine con questo identificativo è già su Binance; «non esiste» (-2013) è falso; ogni altro errore si propaga
        (meglio non mandare che mandare due volte)."""
        try:
            r = c.chiedi("GET", "/fapi/v1/order", {"symbol": simbolo, "origClientOrderId": cid}, firmata=True)
        except RuntimeError as exc:
            if "-2013" in str(exc):
                return False
            raise
        return bool(r and r.get("orderId") is not None)

    def _conto(self, c: ClienteDemo) -> tuple:
        conto = c.chiedi("GET", "/fapi/v2/account", firmata=True)
        self._separati = sorted(x["symbol"] for x in conto.get("positions", []) if x.get("isolated") in (True, "true"))
        posizioni = {x["symbol"]: float(x["positionAmt"]) for x in conto.get("positions", []) if float(x.get("positionAmt") or 0)}
        self._valore_vero = float(conto["totalMarginBalance"])   # senza lo scarto del conto ridotto (problema 41)
        self._saldo_vero = float(conto["totalWalletBalance"])
        self._leve_vere ={x["symbol"]: float(x["leverage"]) for x in conto.get("positions", [])
                           if x["symbol"] in posizioni and x.get("leverage") not in (None, "")}   # problema 22
        return (*self._valori(self._valore_vero, self._saldo_vero), posizioni)

    def _valori(self, margine: float, saldo: float) -> tuple:
        """Il valore e il saldo del conto che il bot usa: sul demo quelli veri meno lo scarto del conto ridotto. Il conto vero
        (`conto_vero.py`, revisione dell'8 novembre 2026, problema 58) li calcola dal capitale e dai redditi, non dal saldo."""
        return margine - self._scarto, saldo - self._scarto

    def _margine_unico(self, c: ClienteDemo, s: str) -> str:
        """Chiede a Binance il margine unico per la moneta; «già unico» (-4046) va bene. Restituisce '' o l'errore."""
        try:
            c.chiedi("POST", "/fapi/v1/marginType", {"symbol": s, "marginType": "CROSSED"}, firmata=True)
        except RuntimeError as exc:
            if "-4046" not in str(exc):
                return str(exc)[:200]
        return ""

    def controlla_margine(self, c: ClienteDemo, st: dict, now: float) -> dict:
        """Ogni ora: le monete con il margine separato si chiudono (se hanno una posizione), passano al margine unico e si riaprono al
        ribilancio dopo."""
        _, _, posizioni = self._conto(c)
        separati = list(getattr(self, "_separati", []))
        sistemate, errori, fm = [], [], None
        for s in separati:
            q = posizioni.get(s, 0.0)
            if q:
                try:
                    self._chiudi_moneta(c, s, q, fm if fm is not None else (fm := self._filtri_per_chiudere(c)))
                except RuntimeError as exc:
                    errori.append({"simbolo": s, "errore": str(exc)[:200]})
                    continue
            e = self._margine_unico(c, s)
            (errori.append({"simbolo": s, "errore": e}) if e else sistemate.append(s))
        if sistemate and any(posizioni.get(s) for s in sistemate):
            st["ultimo_giorno"] = 0                             # si riaprono subito ai pesi di oggi
        # problema 22: anche la leva e la posizione unica per moneta si rileggono ogni ora (prima solo alla prima impostazione)
        leve_rimesse = []
        for s, leva in sorted(getattr(self, "_leve_vere", {}).items()):
            if s in separati or abs(leva - self.LEVA) < 1e-9:
                continue
            try:
                c.chiedi("POST", "/fapi/v1/leverage", {"symbol": s, "leverage": self.LEVA}, firmata=True)
                leve_rimesse.append(s)
            except RuntimeError as exc:
                errori.append({"simbolo": s, "errore": f"leva {leva:g}: {str(exc)[:150]}"})
        try:
            due_lati = bool(c.chiedi("GET", "/fapi/v1/positionSide/dual", firmata=True).get("dualSidePosition"))
        except RuntimeError as exc:
            due_lati = None
            errori.append({"simbolo": "*", "errore": f"modo delle posizioni non letto: {str(exc)[:150]}"})
        if due_lati:
            st.pop("modo_controllato", None)                    # il ribilancio dopo lo rimette a una posizione per moneta
        self._scrivi("margine", {"controllato": now, "separati_trovati": separati, "sistemate": sistemate, "errori": errori,
                                 "leve_rimesse": leve_rimesse, "due_lati": due_lati})
        if leve_rimesse or due_lati:
            print(f"[{self.NOME}] leva rimessa a {self.LEVA} su {leve_rimesse}; posizioni con due lati: {due_lati}")
        if separati:
            print(f"[{self.NOME}] margine separato su {separati}: sistemate {sistemate}, errori {len(errori)}")
        return st

    def confronta(self, c: ClienteDemo, st: dict, now: float) -> dict:
        """Ogni ora, senza ordini in corso: le quantità vere contro quelle volute all'ultimo ribilancio (``st['obiettivi']``)."""
        if st.get("ordini") or not st.get("obiettivi"):
            return st
        equity, _, posizioni = self._conto(c)
        prezzi = {x["symbol"]: float(x["markPrice"]) for x in c.chiedi("GET", "/fapi/v1/premiumIndex") if float(x.get("markPrice") or 0) > 0}
        obiettivi = st["obiettivi"]
        differenze, totale = [], 0.0
        for s in sorted(set(obiettivi) | set(posizioni)):
            if s not in prezzi or equity <= 0:
                continue
            voluto, vero = float(obiettivi.get(s, 0.0)), float(posizioni.get(s, 0.0))
            scarto = (vero - voluto) * prezzi[s] / equity
            totale += abs(scarto)
            if abs(scarto) > SOGLIA_CONFRONTO:
                differenze.append({"simbolo": s, "voluto": round(voluto * prezzi[s] / equity, 4), "vero": round(vero * prezzi[s] / equity, 4),
                                   "scarto": round(scarto, 4)})
        self._scrivi("confronto", {"ora": now, "differenze": differenze, "scarto_totale": round(totale, 4),
                                   "monete": len(set(obiettivi) | set(posizioni))})
        if differenze:
            print(f"[{self.NOME}] posizioni diverse da quelle volute: {[d['simbolo'] for d in differenze]}")
        return st

    def _filtri_degli_ordini(self, info: dict, st: dict, now: float, ribilancio: bool = False) -> dict:
        """I filtri degli ordini da exchangeInfo; con il conto ridotto severi almeno come quelli del conto vero (la copia
        `filtri_conto_vero.json`; al ribilancio, l'allarme se la copia è vecchia). Il conto vero usa solo i suoi (conto_vero.py)."""
        f = filtri(info)
        if st.get("conto_ridotto"):
            if ribilancio:
                eta = (now - calendar.timegm(time.strptime(DATA_FILTRI_VERI, "%Y-%m-%d"))) / 86400
                self._allarme(st, now, "filtri_veri", eta > ETA_MASSIMA_FILTRI_GIORNI and (
                    f"i filtri del conto vero (filtri_conto_vero.json) sono del {DATA_FILTRI_VERI}, {eta:.0f} giorni fa (oltre "
                    f"{ETA_MASSIMA_FILTRI_GIORNI}): vanno riscaricati dal conto vero"))
            return piu_severi(f, filtri_veri())
        if ribilancio:
            self._allarme(st, now, "filtri_veri", None)
        return f

    def ribilancia(self, c: ClienteDemo, st: dict, pesi: dict, giorno: int, now: float, solo: Optional[set] = None) -> dict:
        """Porta il conto ai pesi; con ``solo`` (un'operazione a eventi aperta o chiusa) tocca solo quelle monete."""
        info = c.chiedi("GET", "/fapi/v1/exchangeInfo")
        f = self._filtri_degli_ordini(info, st, now, ribilancio=True)
        qmax = {s: v[3] for s, v in filtri_mercato(info).items()}   # la quantità massima degli ordini limite (problema 22)
        prezzi = {x["symbol"]: float(x["markPrice"]) for x in c.chiedi("GET", "/fapi/v1/premiumIndex") if float(x.get("markPrice") or 0) > 0}
        if not st.get("modo_controllato"):
            # una posizione per moneta (non due, long e short separate): gli ordini qui non hanno il lato della posizione
            if c.chiedi("GET", "/fapi/v1/positionSide/dual", firmata=True).get("dualSidePosition"):
                c.chiedi("POST", "/fapi/v1/positionSide/dual", {"dualSidePosition": "false"}, firmata=True)
            st["modo_controllato"] = True
        # gli ordini rimasti aperti (un tentativo interrotto) si annullano prima di contare le posizioni: senza, si raddoppiano
        aperti = sorted({o["symbol"] for o in c.chiedi("GET", "/fapi/v1/openOrders", firmata=True) or []})
        if solo is not None:
            aperti = [s for s in aperti if s in solo]
        for s in aperti:
            c.chiedi("DELETE", "/fapi/v1/allOpenOrders", {"symbol": s}, firmata=True)
        equity, _, posizioni = self._conto(c)
        st.setdefault("capitale_iniziale", equity)
        mancano = sorted(s for s in pesi if s not in f)
        senza_filtri = sorted(s for s, q in posizioni.items() if q and s not in f and (solo is None or s in solo))
        if solo is None:                               # problema 43: una posizione che il ribilancio non può ridurre
            self._allarme(st, now, "monete_senza_filtri", senza_filtri and (
                f"posizioni su monete senza i filtri di Binance, che il ribilancio non tocca (le chiude il pulsante): "
                f"{', '.join(senza_filtri)}"))
        leve = set(st.get("leve") or [])
        piazzati, rifiutati = [], []
        da_fare = [(s, lato, con_tetto(q, qmax.get(s, math.inf), f[s][1]), limite, riduce)
                   for s, lato, q, limite, riduce in ordini_del_giorno(pesi, posizioni, prezzi, equity, f)]
        saltati = sotto_il_minimo(pesi, posizioni, prezzi, equity, f) if solo is None else None
        if solo is not None:
            da_fare = [o for o in da_fare if o[0] in solo]
        for s, lato, q, limite, riduce in da_fare:
            p = {"symbol": s, "side": lato, "type": "LIMIT", "timeInForce": "GTC", "quantity": testo(q), "price": testo(limite),
                 "newClientOrderId": id_ordine(giorno, s, int(now))}
            if riduce:
                p["reduceOnly"] = "true"
            try:                                       # un ordine rifiutato non ferma gli altri
                if s not in leve:
                    e = self._margine_unico(c, s)
                    if e:
                        raise RuntimeError(f"margine unico non impostato: {e}")
                    c.chiedi("POST", "/fapi/v1/leverage", {"symbol": s, "leverage": self.LEVA}, firmata=True)
                    leve.add(s)
                r = c.chiedi("POST", "/fapi/v1/order", p, firmata=True)
            except RuntimeError as exc:
                rifiutati.append({"simbolo": s, "errore": str(exc)[:200]})
                continue
            piazzati.append({"simbolo": s, "lato": lato, "quantita": q, "limite": limite, "riduce": riduce, "id": r.get("orderId")})
        obiettivi = {} if solo is None else {k: v for k, v in (st.get("obiettivi") or {}).items() if k not in solo}
        for s, w in pesi.items():
            if s in prezzi and (solo is None or s in solo) and w:
                obiettivi[s] = float(w) * equity / prezzi[s]
        st["obiettivi"] = obiettivi
        data = time.strftime("%Y-%m-%d", time.gmtime(giorno * 86400))
        chiave = data if solo is None else f"{time.strftime('%Y-%m-%d', time.gmtime(now))}-eventi-{time.strftime('%H%M', time.gmtime(now))}"
        st.update({"ultimo_giorno": giorno, "leve": sorted(leve), "ordini": {"piazzati": now, "lista": piazzati, "chiave": chiave}})
        voluti = {s for s, w in pesi.items() if w and (solo is None or s in solo)}
        tenuti = {s for s, q in posizioni.items() if q and (solo is None or s in solo)}
        self._scrivi(f"ribilanciamenti/{chiave}", {"ordini": len(piazzati), "equity": equity, "monete_mancanti_sul_demo": mancano,
                                                   "entrate": len(voluti - tenuti), "uscite": len(tenuti - voluti),
                                                   "rifiutati": rifiutati, "annullati_prima": aperti, "piazzati": now,
                                                   "sotto_il_minimo": saltati,
                                                   "solo_eventi": solo is not None})
        cosa = f"decisione G1 del {data}" if solo is None else "operazioni a eventi cambiate"
        print(f"[{self.NOME}] {cosa}: {len(piazzati)} ordini limite sul conto, {len(rifiutati)} rifiutati")
        return st

    def chiudi_ordini(self, c: ClienteDemo, st: dict, now: float) -> dict:
        """Dopo l'ora: gli ordini limite non eseguiti si annullano e quello che manca va a mercato. Quello che manca si calcola dalla
        posizione VERA contro l'obiettivo, non dalla quantità pianificata; ogni ordine a mercato ha un identificativo fisso controllato
        prima di mandarlo; lo stato si salva dopo ogni ordine (revisione del 7 novembre 2026, problema 1: un errore a metà giro faceva
        rimandare due volte lo stesso resto)."""
        ordini = st["ordini"]
        for o in ordini["lista"]:
            if o.get("controllato"):
                continue
            stato = c.chiedi("GET", "/fapi/v1/order", {"symbol": o["simbolo"], "orderId": o["id"]}, firmata=True)
            if stato.get("status") in ("NEW", "PARTIALLY_FILLED"):
                try:
                    c.chiedi("DELETE", "/fapi/v1/order", {"symbol": o["simbolo"], "orderId": o["id"]}, firmata=True)
                except RuntimeError as exc:
                    # annullo rifiutato (per esempio 429): si va avanti solo se l'ordine e' chiuso davvero; se e' ancora aperto si
                    # ferma il giro, senza segnarlo controllato e senza mandare niente a mercato (revisione del 7 nov, problema 25)
                    stato = c.chiedi("GET", "/fapi/v1/order", {"symbol": o["simbolo"], "orderId": o["id"]}, firmata=True)
                    if stato.get("status") in ("NEW", "PARTIALLY_FILLED"):
                        self._ordini_bloccati(st, now, [o["simbolo"]])
                        raise RuntimeError(f"annullo di {o['simbolo']} non riuscito e l'ordine e' ancora aperto: {str(exc)[:120]}")
            o["controllato"] = True
            o["a_limite"] = stato.get("status") == "FILLED"
            self.salva(st)
        info = c.chiedi("GET", "/fapi/v1/exchangeInfo")
        f = self._filtri_degli_ordini(info, st, now)
        fm = filtri_mercato(info)                      # gli ordini a mercato hanno passo e quantità massima loro (problema 22)
        prezzi = {x["symbol"]: float(x["markPrice"]) for x in c.chiedi("GET", "/fapi/v1/premiumIndex") if float(x.get("markPrice") or 0) > 0}
        nella_lista = {o["simbolo"] for o in ordini["lista"]}
        ancora_aperti = sorted({x["symbol"] for x in c.chiedi("GET", "/fapi/v1/openOrders", firmata=True) or []} & nella_lista)
        if ancora_aperti:                              # un ordine limite sul libro e uno a mercato farebbero la posizione doppia
            self._ordini_bloccati(st, now, ancora_aperti)
            raise RuntimeError(f"ordini ancora aperti su {ancora_aperti}: niente a mercato finche' non sono chiusi")
        if ordini.pop("bloccato_dal", None) is not None:   # controllo riuscito: il blocco è finito (problema 38)
            ordini.pop("bloccato_ultimo", None)
            self.salva(st)
        _, _, posizioni = self._conto(c)
        obiettivi = st.get("obiettivi") or {}
        chiave = ordini.get("chiave") or time.strftime("%Y-%m-%d", time.gmtime(int(st["ultimo_giorno"]) * 86400))
        giro = int(float(ordini.get("piazzati", 0)))
        for o in ordini["lista"]:
            if o.get("mercato_fatto"):
                continue
            s = o["simbolo"]
            if s in f and s in prezzi:
                _, passo, qmin, vmin = f[s]
                passo_m, qmin_m, qmax_m, _ = fm.get(s, (passo, qmin, math.inf, math.inf))
                passo, qmin = max(passo, passo_m), max(qmin, qmin_m)
                p = prezzi[s]
                voluto, attuale = float(obiettivi.get(s, 0.0)), float(posizioni.get(s, 0.0))
                delta = voluto - attuale
                q = con_tetto(arrotonda(abs(delta), passo, "giu"), qmax_m, passo)
                if q > 0 and q >= qmin and q * p >= vmin:
                    cid = id_mercato(chiave, s, giro)
                    if not self._ordine_esiste(c, s, cid):
                        riduce = voluto == 0.0 or (attuale != 0 and (attuale > 0) == (voluto > 0) and abs(voluto) < abs(attuale))
                        par = {"symbol": s, "side": "BUY" if delta > 0 else "SELL", "type": "MARKET", "quantity": testo(q),
                               "newClientOrderId": cid}
                        if riduce:
                            par["reduceOnly"] = "true"
                        try:
                            c.chiedi("POST", "/fapi/v1/order", par, firmata=True)
                            ordini["a_mercato"] = int(ordini.get("a_mercato", 0)) + 1
                        except RuntimeError as exc:      # per esempio sotto il minimo dopo un'esecuzione parziale
                            print(f"[{self.NOME}] resto di {s} non inviato: {exc}")
            o["mercato_fatto"] = True
            self.salva(st)
        n = len(ordini["lista"])
        eseguiti_limite = sum(1 for o in ordini["lista"] if o.get("a_limite"))
        a_mercato = int(ordini.get("a_mercato", 0))
        st["limite_eseguiti"] = int(st.get("limite_eseguiti", 0)) + eseguiti_limite
        st["limite_totali"] = int(st.get("limite_totali", 0)) + n
        st["a_mercato"] = int(st.get("a_mercato", 0)) + a_mercato
        self._scrivi(f"ribilanciamenti/{chiave}/limite", {"ordini": n, "eseguiti_a_limite": eseguiti_limite, "a_mercato": a_mercato,
                                                          "controllato": now})
        self._allarme(st, now, "ordini", None)        # il blocco è finito: l'allarme si toglie (problema 38)
        st.pop("ordini")
        return st

    def valuta(self, c: ClienteDemo, st: dict, now: float) -> dict:
        equity, wallet, posizioni = self._conto(c)
        st.setdefault("capitale_iniziale", equity)
        st["ultima_valutazione"] = now
        iniziale = float(st["capitale_iniziale"])
        self._fissa_massimo(st, max(float(st.get("massimo", iniziale)), equity), now)
        if equity <= self._livello_di_stop(st):
            return self.chiudi_tutto(c, st, now, self._motivo_dello_stop(st, equity), equity=equity)
        self._scrivi("stato", {"stato": "acceso", "equity": round(equity, 2), "saldo": round(wallet, 2), "capitale_iniziale": iniziale,
                               "rendimento": equity / iniziale - 1 if iniziale else 0.0,
                               "long": sum(1 for v in posizioni.values() if v > 0), "short": sum(1 for v in posizioni.values() if v < 0),
                               "limite_eseguiti": int(st.get("limite_eseguiti", 0)), "limite_totali": int(st.get("limite_totali", 0)),
                               "ordini_in_attesa": len((st.get("ordini") or {}).get("lista") or []), "aggiornato": now,
                               "massimo": round(st["massimo"], 2), "dal_massimo": equity / st["massimo"] - 1,
                               "stop_a": round(self._livello_di_stop(st), 2),
                               "conto_ridotto": (st.get("conto_ridotto") or {}).get("capitale"),
                               "capitale_in_attesa": st.get("capitale_in_attesa"),
                               self.CHIAVE_VALORE_VERO: round(float(self._valore_vero), 2)})
        oggi = time.strftime('%Y-%m-%d', time.gmtime(now))
        self._scrivi(f"giorni/{oggi}", round(equity, 2))
        self._scrivi(f"diario/{oggi}", {"equity": round(equity, 2), "long": sum(1 for v in posizioni.values() if v > 0),
                                        "short": sum(1 for v in posizioni.values() if v < 0)})
        return self._entrate(c, st, now)

    def _entrate(self, c: ClienteDemo, st: dict, now: float) -> dict:
        """Funding e commissioni veri: quelli di oggi fin qui, e i giorni chiusi non ancora scritti (dal primo giorno del demo).
        Solo lettura: un errore qui non tocca gli ordini."""
        try:
            oggi = int(now // 86400)
            self._scrivi(f"diario/{time.strftime('%Y-%m-%d', time.gmtime(now))}/entrate",
                         entrate_del_conto(c, oggi * 86400_000, int(now * 1000)))
            primo = calendar.timegm(time.strptime(INIZIO_DEMO, "%Y-%m-%d")) // 86400
            d = max(primo, int(st.get("entrate_chiuse_fino", primo - 1)) + 1)
            for _ in range(GIORNI_RECUPERO_MAX):
                if d >= oggi:
                    break
                self._scrivi(f"diario/{time.strftime('%Y-%m-%d', time.gmtime(d * 86400))}/entrate",
                             entrate_del_conto(c, d * 86400_000, (d + 1) * 86400_000 - 1))
                st["entrate_chiuse_fino"] = d
                d += 1
        except Exception as exc:  # noqa: BLE001
            print(f"[{self.NOME}] entrate del conto non lette: {exc}")
        return st
