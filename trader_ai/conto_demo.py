"""Il collegamento al conto demo SUO di Binance (future USDⓈ-M, soldi finti): dati, saldo, posizione, ordini, stop e obiettivo.

* **Solo il conto demo**: ogni richiesta va a `demo-fapi.binance.com`; `_url` rifiuta qualunque altro indirizzo, quindi questo codice
  non può mandare un ordine al conto vero nemmeno per errore.
* **Solo le chiavi sue**: `TRADER_AI_DEMO_API_KEY` e `TRADER_AI_DEMO_API_SECRET` (chiave generata dal sistema, firma HMAC SHA256).
  `controlla_chiavi` rifiuta di partire se mancano o se sono uguali a chiavi d'altri presenti nell'ambiente.
* **Stop e obiettivo** sono ordini condizionati del servizio «algo» di Binance (`POST /fapi/v1/algoOrder`, `algoType=CONDITIONAL`,
  `STOP_MARKET` / `TAKE_PROFIT_MARKET` con `closePosition=true` e `triggerPrice`): da dicembre 2025 `/fapi/v1/order` rifiuta questi
  tipi con l'errore -4120 (registro delle modifiche di Binance, 6 novembre e 10 dicembre 2025).
* **Margine separato** (`ISOLATED`): il margine scelto dal modello è quello che l'operazione può perdere al massimo.
"""
from __future__ import annotations

import hashlib
import hmac
import math
import os
import re
import time
from typing import Callable, Optional
from urllib.parse import urlencode, urlparse

import requests

HOST = "demo-fapi.binance.com"
BASE = "https://" + HOST
#: Variabili di chiavi d'altri conti che, se presenti nell'ambiente, non devono coincidere con le nostre.
CHIAVI_ALTRUI = ("BINANCE_DEMO_API_KEY", "BINANCE_DEMO_API_SECRET", "BINANCE_API_KEY", "BINANCE_API_SECRET")


def _url(percorso: str) -> str:
    url = BASE + percorso
    if urlparse(url).hostname != HOST:
        raise ValueError(f"indirizzo non ammesso: {url}")
    return url


def senza_firma(testo) -> str:
    return re.sub(r"signature=[^\s'\"<>&]*", "signature=[tolta]", str(testo))


def controlla_chiavi(amb: Optional[dict] = None) -> tuple[str, str]:
    """Le chiavi del trader AI dall'ambiente; errore se mancano o se sono uguali a quelle di un altro conto."""
    amb = os.environ if amb is None else amb
    k, s = (amb.get("TRADER_AI_DEMO_API_KEY") or "").strip(), (amb.get("TRADER_AI_DEMO_API_SECRET") or "").strip()
    if not k or not s:
        raise SystemExit("mancano TRADER_AI_DEMO_API_KEY o TRADER_AI_DEMO_API_SECRET")
    for nome in CHIAVI_ALTRUI:
        altra = (amb.get(nome) or "").strip()
        if altra and altra in (k, s):
            raise SystemExit(f"le chiavi del trader AI coincidono con {nome}: rifiuto di partire")
    return k, s


def arrotonda(x: float, passo: float) -> float:
    """Per difetto al multiplo del passo (quantità e prezzi di Binance)."""
    if passo <= 0:
        return x
    n = math.floor(x / passo + 1e-9)
    cifre = max(0, -int(math.floor(math.log10(passo))))
    return round(n * passo, cifre)


def testo(x: float) -> str:
    return f"{x:.10f}".rstrip("0").rstrip(".")


class ContoDemo:
    def __init__(self, chiave: str, segreto: str, simbolo: str, http: Callable = requests.request) -> None:
        self.chiave, self.simbolo, self.http = chiave, simbolo, http
        self._s = segreto.encode()
        self.scarto_ms = 0
        self._filtri: Optional[dict] = None

    # --- richieste -------------------------------------------------------------------------------------------------
    def chiedi(self, metodo: str, percorso: str, parametri: Optional[dict] = None, firmata: bool = False):
        p = dict(parametri or {})
        if firmata:
            p["timestamp"] = int(time.time() * 1000) + self.scarto_ms
            p["recvWindow"] = 5000
        q = urlencode(p)
        if firmata:
            q += "&signature=" + hmac.new(self._s, q.encode(), hashlib.sha256).hexdigest()
        try:
            r = self.http(metodo, _url(percorso) + ("?" + q if q else ""), headers={"X-MBX-APIKEY": self.chiave}, timeout=15)
        except requests.RequestException as exc:
            raise RuntimeError(f"{metodo} {percorso}: rete: {senza_firma(exc)[:200]}") from None
        if r.status_code >= 400:
            if firmata and '"code":-1021' in r.text.replace(" ", ""):        # orologio: si rilegge l'ora di Binance
                self.scarto_ms = int(self.chiedi("GET", "/fapi/v1/time")["serverTime"]) - int(time.time() * 1000)
            raise RuntimeError(f"{metodo} {percorso}: {r.status_code} {senza_firma(r.text)[:200]}")
        return r.json()

    # --- dati di mercato (pubblici) --------------------------------------------------------------------------------
    def candele(self, intervallo: str, ora_ms: Optional[int] = None, n: int = 200) -> list:
        """Solo candele chiuse: quella ancora aperta (chiusura dopo adesso) si toglie."""
        from datetime import datetime, timezone

        ora_ms = ora_ms or int(time.time() * 1000)
        righe = self.chiedi("GET", "/fapi/v1/klines", {"symbol": self.simbolo, "interval": intervallo, "limit": n})
        out = []
        for k in righe:
            chiusa_ms = int(k[6]) + 1
            if chiusa_ms > ora_ms:
                continue
            out.append({"apertura": float(k[1]), "massimo": float(k[2]), "minimo": float(k[3]), "chiusura": float(k[4]),
                        "volume": float(k[5]), "chiusa": datetime.fromtimestamp(chiusa_ms / 1000, timezone.utc)})
        return out

    def mercato(self) -> dict:
        pi = self.chiedi("GET", "/fapi/v1/premiumIndex", {"symbol": self.simbolo})
        oi = self.chiedi("GET", "/fapi/v1/openInterest", {"symbol": self.simbolo})
        return {"prezzo": float(pi["markPrice"]), "funding": float(pi["lastFundingRate"]),
                "prossimo_funding_ms": int(pi["nextFundingTime"]), "interesse_aperto": float(oi["openInterest"])}

    def filtri(self) -> dict:
        if self._filtri is None:
            info = self.chiedi("GET", "/fapi/v1/exchangeInfo")
            s = next(x for x in info["symbols"] if x["symbol"] == self.simbolo)
            f = {x["filterType"]: x for x in s["filters"]}
            self._filtri = {"passo_prezzo": float(f["PRICE_FILTER"]["tickSize"]),
                            "passo_quantita": float(f["MARKET_LOT_SIZE"]["stepSize"] if "MARKET_LOT_SIZE" in f
                                                    else f["LOT_SIZE"]["stepSize"]),
                            "quantita_min": float(f["LOT_SIZE"]["minQty"]),
                            "valore_min": float(f.get("MIN_NOTIONAL", {}).get("notional", 0) or 0)}
        return self._filtri

    # --- conto -----------------------------------------------------------------------------------------------------
    def saldo(self) -> dict:
        a = self.chiedi("GET", "/fapi/v2/account", firmata=True)
        return {"conto": float(a["totalMarginBalance"]), "disponibile": float(a["availableBalance"]),
                "portafoglio": float(a["totalWalletBalance"])}

    def posizione(self) -> Optional[dict]:
        for p in self.chiedi("GET", "/fapi/v2/positionRisk", {"symbol": self.simbolo}, firmata=True):
            q = float(p["positionAmt"])
            if p["symbol"] == self.simbolo and q != 0:
                liq = float(p.get("liquidationPrice") or 0)
                return {"lato": "lungo" if q > 0 else "corto", "quantita": abs(q), "entrata": float(p["entryPrice"]),
                        "leva": float(p.get("leverage") or 1), "liquidazione": liq or None}
        return None

    def ordini_aperti(self) -> list:
        return self.chiedi("GET", "/fapi/v1/openOrders", {"symbol": self.simbolo}, firmata=True)

    def ordini_condizionati(self) -> list:
        r = self.chiedi("GET", "/fapi/v1/openAlgoOrders", {"symbol": self.simbolo}, firmata=True)
        return r if isinstance(r, list) else r.get("orders", [])

    # --- ordini ----------------------------------------------------------------------------------------------------
    def prepara(self, leva: int) -> None:
        try:
            self.chiedi("POST", "/fapi/v1/marginType", {"symbol": self.simbolo, "marginType": "ISOLATED"}, firmata=True)
        except RuntimeError as e:
            if "-4046" not in str(e):           # «già ISOLATED»
                raise
        self.chiedi("POST", "/fapi/v1/leverage", {"symbol": self.simbolo, "leverage": int(leva)}, firmata=True)

    def apri(self, lato: str, quantita: float, tipo: str = "MARKET", prezzo: Optional[float] = None) -> dict:
        p = {"symbol": self.simbolo, "side": "BUY" if lato == "lungo" else "SELL", "type": tipo,
             "quantity": testo(quantita), "newOrderRespType": "RESULT"}
        if tipo == "LIMIT":
            p.update(price=testo(prezzo), timeInForce="GTC")
        return self.chiedi("POST", "/fapi/v1/order", p, firmata=True)

    def condizionato(self, lato_posizione: str, tipo: str, prezzo: float) -> dict:
        """Stop (`STOP_MARKET`) o obiettivo (`TAKE_PROFIT_MARKET`) che chiude tutta la posizione al prezzo mark."""
        p = {"algoType": "CONDITIONAL", "symbol": self.simbolo, "side": "SELL" if lato_posizione == "lungo" else "BUY",
             "type": tipo, "triggerPrice": testo(prezzo), "closePosition": "true", "workingType": "MARK_PRICE"}
        return self.chiedi("POST", "/fapi/v1/algoOrder", p, firmata=True)

    def annulla_condizionato(self, algo_id) -> None:
        self.chiedi("DELETE", "/fapi/v1/algoOrder", {"algoId": algo_id}, firmata=True)

    def annulla_tutto(self) -> None:
        for percorso in ("/fapi/v1/allOpenOrders", "/fapi/v1/algoOpenOrders"):
            try:
                self.chiedi("DELETE", percorso, {"symbol": self.simbolo}, firmata=True)
            except RuntimeError as e:
                print(f"[trader_ai] annullamento {percorso}: {e}")

    def chiudi(self, pos: dict) -> Optional[dict]:
        self.annulla_tutto()
        if not pos:
            return None
        p = {"symbol": self.simbolo, "side": "SELL" if pos["lato"] == "lungo" else "BUY", "type": "MARKET",
             "quantity": testo(pos["quantita"]), "reduceOnly": "true", "newOrderRespType": "RESULT"}
        return self.chiedi("POST", "/fapi/v1/order", p, firmata=True)
