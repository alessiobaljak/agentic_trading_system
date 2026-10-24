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
"""
from __future__ import annotations

import base64
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
LEVA = 5
VALIDITA_LIMITE_S = 3600
OGNI_VALUTAZIONE_S = 3600
ATTESA_DOPO_ERRORE_S = 1800


def _url(percorso: str) -> str:
    url = DEMO + percorso
    if urlparse(url).hostname != HOST_DEMO:
        raise ValueError(f"indirizzo non ammesso: {url}")
    return url


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
    """{simbolo: (passo di prezzo, passo di quantita', quantita' minima, valore minimo)} dai filtri di exchangeInfo."""
    out = {}
    for x in (info or {}).get("symbols", []):
        f = {g["filterType"]: g for g in x.get("filters", [])}
        try:
            out[x["symbol"]] = (float(f["PRICE_FILTER"]["tickSize"]), float(f["LOT_SIZE"]["stepSize"]),
                                float(f["LOT_SIZE"]["minQty"]), float((f.get("MIN_NOTIONAL") or {}).get("notional", 5.0)))
        except (KeyError, TypeError, ValueError):
            continue
    return out


def id_ordine(giorno: int, simbolo: str) -> str:
    """L'identificativo dell'ordine per Binance (ammessi solo ``.A-Za-z0-9:/_-``, al massimo 36): le monete con il nome in altri
    caratteri (per esempio 币安人生USDT) prendono un'impronta del nome. Il 24 ottobre il primo ribilancio sul demo si e' fermato qui."""
    nome = simbolo if re.fullmatch(r"[.A-Za-z0-9:/_-]+", simbolo) else "h" + hashlib.sha1(simbolo.encode()).hexdigest()[:12]
    return f"g1d-{giorno}-{nome}"[:36]


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


class ClienteDemo:
    """Le richieste al conto demo dei future (firmate con la chiave del conto demo)."""

    def __init__(self, chiave: str, segreto: str, http: Callable = requests.request) -> None:
        self.chiave, self.http = chiave, http
        self.firma = firmatore(segreto)

    def chiedi(self, metodo: str, percorso: str, parametri: Optional[dict] = None, firmata: bool = False):
        p = dict(parametri or {})
        if firmata:
            p["timestamp"] = int(time.time() * 1000)
            p["recvWindow"] = 5000
        q = urlencode(p)
        if firmata:
            q += "&signature=" + self.firma(q)
        r = self.http(metodo, _url(percorso) + ("?" + q if q else ""), headers={"X-MBX-APIKEY": self.chiave}, timeout=15)
        if r.status_code >= 400:
            raise RuntimeError(f"{metodo} {percorso}: {r.status_code} {r.text[:200]}")
        return r.json()


class DemoG1:
    def __init__(self, fb, cliente: Optional[ClienteDemo] = None, file_stato: Path = FILE_STATO, file_g1: Path = FILE_G1,
                 interruttore: Path = INTERRUTTORE) -> None:
        self.fb = fb
        self._cliente = cliente
        self.file_stato, self.file_g1, self.interruttore = Path(file_stato), Path(file_g1), Path(interruttore)
        self._ultimo_tentativo = 0.0

    # ---- stato ----
    def acceso(self) -> bool:
        if self.interruttore == INTERRUTTORE and os.environ.get("PYTEST_CURRENT_TEST"):
            return False
        return self.interruttore.exists()

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
            self.fb.set_rtdb(f"/demo_binance/{ramo}", valore)

    # ---- il giro ----
    def tick(self, now: float) -> None:
        if not self.acceso():
            return
        try:
            c = self.cliente()
        except Exception as exc:  # noqa: BLE001
            self._scrivi("stato", {"stato": f"chiave del conto demo non leggibile: {type(exc).__name__}", "aggiornato": now})
            return
        if c is None:
            self._scrivi("stato", {"stato": "manca la chiave del conto demo (BINANCE_DEMO_API_KEY nel .env)", "aggiornato": now})
            return
        if now - self._ultimo_tentativo < ATTESA_DOPO_ERRORE_S and self._ultimo_tentativo:
            return
        try:
            st = self.carica()
            if st.get("ordini") and now >= float(st["ordini"]["piazzati"]) + VALIDITA_LIMITE_S:
                st = self.chiudi_ordini(c, st, now)
            g1 = json.loads(self.file_g1.read_text(encoding="utf-8")) if self.file_g1.exists() else {}
            giorno = int(g1.get("ultimo_lunedi", 0))
            if giorno and giorno > int(st.get("ultimo_giorno", 0)) and not st.get("ordini"):
                st = self.ribilancia(c, st, g1.get("pesi") or {}, giorno, now)
            if now - float(st.get("ultima_valutazione", 0)) >= OGNI_VALUTAZIONE_S:
                st = self.valuta(c, st, now)
            self.salva(st)
        except Exception as exc:  # noqa: BLE001
            self._ultimo_tentativo = now
            print(f"[demo_binance] errore, si riprova fra 30 minuti: {exc}")
            self._scrivi("errore", {"testo": str(exc)[:300], "ora": now})

    def _conto(self, c: ClienteDemo) -> tuple:
        conto = c.chiedi("GET", "/fapi/v2/account", firmata=True)
        posizioni = {x["symbol"]: float(x["positionAmt"]) for x in conto.get("positions", []) if float(x.get("positionAmt") or 0)}
        return float(conto["totalMarginBalance"]), float(conto["totalWalletBalance"]), posizioni

    def ribilancia(self, c: ClienteDemo, st: dict, pesi: dict, giorno: int, now: float) -> dict:
        f = filtri(c.chiedi("GET", "/fapi/v1/exchangeInfo"))
        prezzi = {x["symbol"]: float(x["markPrice"]) for x in c.chiedi("GET", "/fapi/v1/premiumIndex") if float(x.get("markPrice") or 0) > 0}
        if not st.get("modo_controllato"):
            # una posizione per moneta (non due, long e short separate): gli ordini qui non hanno il lato della posizione
            if c.chiedi("GET", "/fapi/v1/positionSide/dual", firmata=True).get("dualSidePosition"):
                c.chiedi("POST", "/fapi/v1/positionSide/dual", {"dualSidePosition": "false"}, firmata=True)
            st["modo_controllato"] = True
        # gli ordini rimasti aperti (un tentativo interrotto) si annullano prima di contare le posizioni: senza, si raddoppiano
        aperti = sorted({o["symbol"] for o in c.chiedi("GET", "/fapi/v1/openOrders", firmata=True) or []})
        for s in aperti:
            c.chiedi("DELETE", "/fapi/v1/allOpenOrders", {"symbol": s}, firmata=True)
        equity, _, posizioni = self._conto(c)
        st.setdefault("capitale_iniziale", equity)
        mancano = sorted(s for s in pesi if s not in f)
        leve = set(st.get("leve") or [])
        piazzati, rifiutati = [], []
        for s, lato, q, limite, riduce in ordini_del_giorno(pesi, posizioni, prezzi, equity, f):
            p = {"symbol": s, "side": lato, "type": "LIMIT", "timeInForce": "GTC", "quantity": testo(q), "price": testo(limite),
                 "newClientOrderId": id_ordine(giorno, s)}
            if riduce:
                p["reduceOnly"] = "true"
            try:                                       # un ordine rifiutato non ferma gli altri
                if s not in leve:
                    c.chiedi("POST", "/fapi/v1/leverage", {"symbol": s, "leverage": LEVA}, firmata=True)
                    leve.add(s)
                r = c.chiedi("POST", "/fapi/v1/order", p, firmata=True)
            except RuntimeError as exc:
                rifiutati.append({"simbolo": s, "errore": str(exc)[:200]})
                continue
            piazzati.append({"simbolo": s, "lato": lato, "quantita": q, "limite": limite, "riduce": riduce, "id": r.get("orderId")})
        st.update({"ultimo_giorno": giorno, "leve": sorted(leve), "ordini": {"piazzati": now, "lista": piazzati}})
        data = time.strftime("%Y-%m-%d", time.gmtime(giorno * 86400))
        self._scrivi(f"ribilanciamenti/{data}", {"ordini": len(piazzati), "equity": equity, "monete_mancanti_sul_demo": mancano,
                                                 "rifiutati": rifiutati, "annullati_prima": aperti, "piazzati": now})
        print(f"[demo_binance] decisione G1 del {data}: {len(piazzati)} ordini limite sul conto demo, {len(rifiutati)} rifiutati")
        return st

    def chiudi_ordini(self, c: ClienteDemo, st: dict, now: float) -> dict:
        """Dopo l'ora: gli ordini limite non eseguiti (o eseguiti in parte) si annullano e il resto va a mercato."""
        eseguiti_limite = a_mercato = 0
        for o in st["ordini"]["lista"]:
            stato = c.chiedi("GET", "/fapi/v1/order", {"symbol": o["simbolo"], "orderId": o["id"]}, firmata=True)
            fatta = float(stato.get("executedQty") or 0)
            if stato.get("status") == "FILLED":
                eseguiti_limite += 1
                continue
            if stato.get("status") in ("NEW", "PARTIALLY_FILLED"):
                c.chiedi("DELETE", "/fapi/v1/order", {"symbol": o["simbolo"], "orderId": o["id"]}, firmata=True)
            resto = round(float(o["quantita"]) - fatta, 10)
            if resto > 0:
                p = {"symbol": o["simbolo"], "side": o["lato"], "type": "MARKET", "quantity": testo(resto)}
                if o.get("riduce"):
                    p["reduceOnly"] = "true"
                try:
                    c.chiedi("POST", "/fapi/v1/order", p, firmata=True)
                    a_mercato += 1
                except RuntimeError as exc:          # per esempio sotto il minimo dopo un'esecuzione parziale
                    print(f"[demo_binance] resto di {o['simbolo']} non inviato: {exc}")
        n = len(st["ordini"]["lista"])
        st["limite_eseguiti"] = int(st.get("limite_eseguiti", 0)) + eseguiti_limite
        st["limite_totali"] = int(st.get("limite_totali", 0)) + n
        st["a_mercato"] = int(st.get("a_mercato", 0)) + a_mercato
        data = time.strftime("%Y-%m-%d", time.gmtime(int(st["ultimo_giorno"]) * 86400))
        self._scrivi(f"ribilanciamenti/{data}/limite", {"ordini": n, "eseguiti_a_limite": eseguiti_limite, "a_mercato": a_mercato,
                                                        "controllato": now})
        st.pop("ordini")
        return st

    def valuta(self, c: ClienteDemo, st: dict, now: float) -> dict:
        equity, wallet, posizioni = self._conto(c)
        st.setdefault("capitale_iniziale", equity)
        st["ultima_valutazione"] = now
        iniziale = float(st["capitale_iniziale"])
        self._scrivi("stato", {"stato": "acceso", "equity": round(equity, 2), "saldo": round(wallet, 2), "capitale_iniziale": iniziale,
                               "rendimento": equity / iniziale - 1 if iniziale else 0.0,
                               "long": sum(1 for v in posizioni.values() if v > 0), "short": sum(1 for v in posizioni.values() if v < 0),
                               "limite_eseguiti": int(st.get("limite_eseguiti", 0)), "limite_totali": int(st.get("limite_totali", 0)),
                               "ordini_in_attesa": len((st.get("ordini") or {}).get("lista") or []), "aggiornato": now})
        self._scrivi(f"giorni/{time.strftime('%Y-%m-%d', time.gmtime(now))}", round(equity, 2))
        return st
