"""Il conto SIMULATO del trader AI (decisione del proprietario del 24 novembre 2026: «conto simulato sul programma va bene»).

Perché: il proprietario può creare solo chiavi nuove sullo stesso account Binance, e il conto demo di quell'account è già usato da
un'altra strategia (la prova del 24 novembre si è fermata al primo punto: 53 monete sul conto). Il trader non deve toccarlo (decisione
del 23 novembre; i dettagli in REGOLE.md).

Come funziona:
* **Prezzi veri, nessuna chiave**: candele, prezzo mark, funding e interesse aperto dalle pagine pubbliche dei future di Binance
  (`fapi.binance.com`, solo richieste GET senza chiave; dalla macchina rispondono, dagli Stati Uniti no).
* **Ordini simulati con le spese vere** (decisione del 7 novembre): 0,05% a mercato, 0,02% con ordine limite eseguito; scarto di prezzo
  0,01% su BTC, ETH e SOL e 0,02% sulle altre, sempre contro di noi.
* **Stop, obiettivo, limite e liquidazione minuto per minuto** sulle candele da 1 minuto chiuse dall'ultimo controllo: se nella stessa
  candela si toccano stop e obiettivo vale lo stop (il caso peggiore); se la candela apre già oltre lo stop si esce all'apertura.
  Liquidazione: si perde tutto il margine della posizione (margine separato), al prezzo di liquidazione approssimato (1/leva meno lo 0,5%
  di mantenimento).
* **Funding vero**: ogni pagamento pubblicato da Binance (`/fapi/v1/fundingRate`) mentre la posizione è aperta si paga o si incassa sul
  valore della posizione al prezzo mark del momento.
* Stessa interfaccia di `conto_demo.ContoDemo`: `avvio.Trader` non sa se il conto è vero o simulato.
"""
from __future__ import annotations

import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Optional
from urllib.parse import urlencode, urlparse

import requests

HOST_PUBBLICO = "fapi.binance.com"
COMMISSIONE_MERCATO = 0.0005
COMMISSIONE_LIMITE = 0.0002
MANTENIMENTO = 0.005
CAPITALE_INIZIALE = 1000.0


def scarto(simbolo: str) -> float:
    return 0.0001 if simbolo in ("BTCUSDT", "ETHUSDT", "SOLUSDT") else 0.0002


class MercatoPubblico:
    """Solo dati pubblici, solo GET, nessuna chiave."""

    def __init__(self, simbolo: str, http: Callable = requests.get) -> None:
        self.simbolo, self.http = simbolo, http
        self._filtri: Optional[dict] = None

    def chiedi(self, percorso: str, parametri: dict):
        url = f"https://{HOST_PUBBLICO}{percorso}?{urlencode(parametri)}"
        if urlparse(url).hostname != HOST_PUBBLICO:
            raise ValueError(f"indirizzo non ammesso: {url}")
        r = self.http(url, timeout=15)
        if r.status_code >= 400:
            raise RuntimeError(f"GET {percorso}: {r.status_code} {r.text[:200]}")
        return r.json()

    def klines(self, intervallo: str, n: int = 200, inizio_ms: Optional[int] = None) -> list:
        p = {"symbol": self.simbolo, "interval": intervallo, "limit": n}
        if inizio_ms is not None:
            p["startTime"] = inizio_ms
        return self.chiedi("/fapi/v1/klines", p)

    def mercato(self) -> dict:
        pi = self.chiedi("/fapi/v1/premiumIndex", {"symbol": self.simbolo})
        oi = self.chiedi("/fapi/v1/openInterest", {"symbol": self.simbolo})
        return {"prezzo": float(pi["markPrice"]), "funding": float(pi["lastFundingRate"]),
                "prossimo_funding_ms": int(pi["nextFundingTime"]), "interesse_aperto": float(oi["openInterest"])}

    def funding_da(self, inizio_ms: int) -> list:
        return self.chiedi("/fapi/v1/fundingRate", {"symbol": self.simbolo, "startTime": inizio_ms, "limit": 100})

    def filtri(self) -> dict:
        if self._filtri is None:
            info = self.chiedi("/fapi/v1/exchangeInfo", {})
            s = next(x for x in info["symbols"] if x["symbol"] == self.simbolo)
            f = {x["filterType"]: x for x in s["filters"]}
            self._filtri = {"passo_prezzo": float(f["PRICE_FILTER"]["tickSize"]),
                            "passo_quantita": float(f.get("MARKET_LOT_SIZE", f["LOT_SIZE"])["stepSize"]),
                            "passo_quantita_limite": float(f["LOT_SIZE"]["stepSize"]),
                            "quantita_min": float(f["LOT_SIZE"]["minQty"]),
                            "valore_min": float(f.get("MIN_NOTIONAL", {}).get("notional", 0) or 0)}
        return self._filtri


def liquidazione(lato: str, entrata: float, leva: float) -> float:
    return entrata * (1 - 1 / leva + MANTENIMENTO) if lato == "lungo" else entrata * (1 + 1 / leva - MANTENIMENTO)


class ContoSimulato:
    def __init__(self, mercato: MercatoPubblico, file_stato: Path, ora_ms: Callable[[], int] = lambda: int(time.time() * 1000),
                 capitale: float = CAPITALE_INIZIALE) -> None:
        self.m, self.simbolo, self.file, self.ora_ms = mercato, mercato.simbolo, Path(file_stato), ora_ms
        self.pausa_fino = 0.0
        self._ultimo_aggiornamento = -1
        self.s = self._carica(capitale)

    # --- stato -----------------------------------------------------------------------------------------------------
    def _carica(self, capitale: float) -> dict:
        try:
            return json.loads(self.file.read_text())
        except FileNotFoundError:
            return {"portafoglio": capitale, "posizione": None, "ordini": [], "algo": [], "leva": 1,
                    "ultimo_minuto_ms": None, "ultimo_funding_ms": None, "movimenti": [], "prossimo_id": 1}

    def _salva(self) -> None:
        self.file.parent.mkdir(parents=True, exist_ok=True)
        tmp = self.file.with_suffix(".tmp")
        tmp.write_text(json.dumps(self.s, ensure_ascii=False, indent=1))
        tmp.replace(self.file)

    def _movimento(self, cosa: str, importo: float, **altro) -> None:
        self.s["portafoglio"] += importo
        self.s["movimenti"] = (self.s["movimenti"] + [{"ora_ms": self.ora_ms(), "cosa": cosa, "importo": round(importo, 6),
                                                          **altro}])[-500:]

    # --- il mercato fa il suo corso: limite, stop, obiettivo, liquidazione, funding --------------------------------
    def aggiorna(self) -> None:
        adesso = self.ora_ms()
        if adesso - self._ultimo_aggiornamento < 5000:
            return
        self._ultimo_aggiornamento = adesso
        if self.s["ultimo_minuto_ms"] is None:
            self.s["ultimo_minuto_ms"] = adesso - adesso % 60000
            self.s["ultimo_funding_ms"] = adesso
            self._salva()
            return
        for k in self.m.klines("1m", 1000, self.s["ultimo_minuto_ms"]):
            apertura_ms, chiusura_ms = int(k[0]), int(k[6]) + 1
            if apertura_ms < self.s["ultimo_minuto_ms"] or chiusura_ms > adesso:
                continue
            self._candela(float(k[1]), float(k[2]), float(k[3]))
            self.s["ultimo_minuto_ms"] = chiusura_ms
        self._funding(adesso)
        self._salva()

    def _candela(self, apertura: float, massimo: float, minimo: float) -> None:
        sc = scarto(self.simbolo)
        p = self.s["posizione"]
        if p is None:
            for o in list(self.s["ordini"]):
                tocca = minimo <= o["prezzo"] if o["lato"] == "lungo" else massimo >= o["prezzo"]
                if tocca:
                    self.s["ordini"].remove(o)
                    self._apri_posizione(o["lato"], o["quantita"], o["prezzo"], o["leva"], COMMISSIONE_LIMITE, "limite eseguito")
                    p = self.s["posizione"]
                    break
        if p is None:
            return
        lungo = p["lato"] == "lungo"
        stop = next((a for a in self.s["algo"] if a["tipo"] == "STOP_MARKET"), None)
        obiettivo = next((a for a in self.s["algo"] if a["tipo"] == "TAKE_PROFIT_MARKET"), None)
        avverso = minimo if lungo else massimo
        favorevole = massimo if lungo else minimo
        livelli = []                                  # (prezzo dell'evento, come): il primo che si incontra andando contro
        if stop:
            livelli.append((stop["prezzo"], "stop"))
        livelli.append((p["liquidazione"], "liquidazione"))
        livelli.sort(key=lambda x: -x[0] if lungo else x[0])
        for livello, come in livelli:
            if (avverso <= livello) if lungo else (avverso >= livello):
                oltre = (apertura <= livello) if lungo else (apertura >= livello)
                if come == "liquidazione":
                    self._chiudi_posizione(livello, "liquidazione", perdita_margine=True)
                else:
                    uscita = (apertura if oltre else livello) * ((1 - sc) if lungo else (1 + sc))
                    self._chiudi_posizione(uscita, "stop")
                return
        if obiettivo and ((favorevole >= obiettivo["prezzo"]) if lungo else (favorevole <= obiettivo["prezzo"])):
            oltre = (apertura >= obiettivo["prezzo"]) if lungo else (apertura <= obiettivo["prezzo"])
            uscita = (apertura if oltre else obiettivo["prezzo"]) * ((1 - sc) if lungo else (1 + sc))
            self._chiudi_posizione(uscita, "obiettivo")

    def _funding(self, adesso: int) -> None:
        p = self.s["posizione"]
        dal = self.s["ultimo_funding_ms"] or adesso
        if p is not None:
            for f in self.m.funding_da(dal + 1):
                t = int(f["fundingTime"])
                if dal < t <= adesso and t >= p["aperta_ms"]:
                    prezzo = float(f.get("markPrice") or 0) or p["entrata"]
                    valore = p["quantita"] * prezzo
                    tasso = float(f["fundingRate"])
                    self._movimento("funding", -valore * tasso if p["lato"] == "lungo" else valore * tasso, tasso=tasso)
        self.s["ultimo_funding_ms"] = adesso

    def _apri_posizione(self, lato, quantita, prezzo, leva, commissione, come) -> None:
        valore = quantita * prezzo
        self._movimento("commissione", -valore * commissione, come=come)
        self.s["posizione"] = {"lato": lato, "quantita": quantita, "entrata": prezzo, "leva": leva,
                               "margine": valore / leva, "liquidazione": liquidazione(lato, prezzo, leva),
                               "aperta_ms": self.ora_ms()}

    def _chiudi_posizione(self, uscita: float, come: str, perdita_margine: bool = False) -> None:
        p = self.s["posizione"]
        segno = 1 if p["lato"] == "lungo" else -1
        if perdita_margine:
            self._movimento("liquidazione", -p["margine"], prezzo=uscita)
        else:
            self._movimento("risultato", segno * (uscita - p["entrata"]) * p["quantita"], prezzo=uscita, come=come)
            self._movimento("commissione", -p["quantita"] * uscita * COMMISSIONE_MERCATO, come=come)
        self.s["posizione"] = None
        self.s["algo"] = []                           # stop e obiettivo «chiudi tutto» non servono più

    # --- la stessa interfaccia di ContoDemo ------------------------------------------------------------------------
    def candele(self, intervallo: str, ora_ms: Optional[int] = None, n: int = 200) -> list:
        ora_ms = ora_ms or self.ora_ms()
        out = []
        for k in self.m.klines(intervallo, n):
            chiusa_ms = int(k[6]) + 1
            if chiusa_ms > ora_ms:
                continue
            out.append({"apertura": float(k[1]), "massimo": float(k[2]), "minimo": float(k[3]), "chiusura": float(k[4]),
                        "volume": float(k[5]), "chiusa": datetime.fromtimestamp(chiusa_ms / 1000, timezone.utc)})
        return out

    def mercato(self) -> dict:
        return self.m.mercato()

    def filtri(self) -> dict:
        return self.m.filtri()

    def modo_doppio(self) -> bool:
        return False

    def saldo(self) -> dict:
        self.aggiorna()
        p = self.s["posizione"]
        aperto, impegnato = 0.0, 0.0
        if p is not None:
            prezzo = self.m.mercato()["prezzo"]
            aperto = (1 if p["lato"] == "lungo" else -1) * (prezzo - p["entrata"]) * p["quantita"]
            aperto = max(aperto, -p["margine"])         # margine separato: non si perde più del margine
            impegnato = p["margine"]
        impegnato += sum(o["quantita"] * o["prezzo"] / o["leva"] for o in self.s["ordini"])
        return {"conto": self.s["portafoglio"] + aperto, "disponibile": self.s["portafoglio"] - impegnato,
                "portafoglio": self.s["portafoglio"]}

    def posizioni_tutte(self) -> list:
        self.aggiorna()
        p = self.s["posizione"]
        if p is None:
            return []
        return [{"simbolo": self.simbolo, "lato": p["lato"], "quantita": p["quantita"], "entrata": p["entrata"],
                 "leva": p["leva"], "liquidazione": p["liquidazione"]}]

    posizioni_simbolo = posizioni_tutte

    def ordini_tutti(self) -> list:
        self.aggiorna()
        return ([{"symbol": self.simbolo, "clientOrderId": o["cid"], "_algo": False} for o in self.s["ordini"]]
                + [{"symbol": self.simbolo, "algoId": a["algoId"], "clientAlgoId": a["cid"], "_algo": True} for a in self.s["algo"]])

    ordini_simbolo = ordini_tutti

    def prepara(self, leva: int) -> None:
        self.s["leva"] = int(leva)

    def apri(self, lato: str, quantita: float, cid: str, tipo: str = "MARKET", prezzo: Optional[float] = None) -> dict:
        mark = self.m.mercato()["prezzo"]
        leva = self.s["leva"]
        compra = lato == "lungo"
        incrocia = tipo == "LIMIT" and ((prezzo >= mark) if compra else (prezzo <= mark))
        if tipo == "MARKET" or incrocia:             # un limite che incrocia il prezzo si esegue subito, a mercato
            esecuzione = mark * ((1 + scarto(self.simbolo)) if compra else (1 - scarto(self.simbolo)))
            if quantita * esecuzione / leva + quantita * esecuzione * COMMISSIONE_MERCATO > self.saldo()["disponibile"]:
                raise RuntimeError('{"code":-2019,"msg":"Margin is insufficient."}')
            self._apri_posizione(lato, quantita, esecuzione, leva, COMMISSIONE_MERCATO, "a mercato")
            self._salva()
            return {"avgPrice": str(esecuzione), "executedQty": str(quantita)}
        if quantita * prezzo / leva > self.saldo()["disponibile"]:
            raise RuntimeError('{"code":-2019,"msg":"Margin is insufficient."}')
        self.s["ordini"].append({"cid": cid, "lato": lato, "quantita": quantita, "prezzo": prezzo, "leva": leva})
        self._salva()
        return {"avgPrice": "0", "executedQty": "0"}

    def condizionato(self, lato_posizione: str, tipo: str, prezzo: float, cid: str) -> dict:
        mark = self.m.mercato()["prezzo"]
        lungo = lato_posizione == "lungo"
        subito = (mark <= prezzo if lungo else mark >= prezzo) if tipo == "STOP_MARKET" else \
            (mark >= prezzo if lungo else mark <= prezzo)
        if subito:
            raise RuntimeError('{"code":-2021,"msg":"Order would immediately trigger."}')
        algo_id = self.s["prossimo_id"]
        self.s["prossimo_id"] += 1
        self.s["algo"].append({"algoId": algo_id, "cid": cid, "tipo": tipo, "prezzo": prezzo, "lato": lato_posizione})
        self._salva()
        return {"algoId": algo_id}

    def annulla_condizionato(self, ordine: dict) -> None:
        self.s["algo"] = [a for a in self.s["algo"] if a["algoId"] != ordine.get("algoId")]
        self._salva()

    def annulla_tutto(self) -> None:
        self.s["ordini"], self.s["algo"] = [], []
        self._salva()

    def chiudi(self, pos: Optional[dict], cid: str) -> Optional[dict]:
        esito = None
        if self.s["posizione"] is not None and pos:
            mark = self.m.mercato()["prezzo"]
            lungo = self.s["posizione"]["lato"] == "lungo"
            uscita = mark * ((1 - scarto(self.simbolo)) if lungo else (1 + scarto(self.simbolo)))
            self._chiudi_posizione(uscita, "chiusa a mercato")
            esito = {"avgPrice": str(uscita)}
        self.annulla_tutto()
        return esito
