"""Il conto SIMULATO del trader AI (decisione del proprietario del 24 novembre 2026: «conto simulato sul programma va bene»).

Perché: il proprietario può creare solo chiavi nuove sullo stesso account Binance, e il conto demo di quell'account è già usato da
un'altra strategia (la prova del 24 novembre si è fermata al primo punto: 53 monete sul conto). Il trader non deve toccarlo (decisione
del 23 novembre; i dettagli in REGOLE.md).

Come funziona:
* **Prezzi veri, nessuna chiave**: candele, prezzo mark, funding e interesse aperto dalle pagine pubbliche dei future di Binance
  (`fapi.binance.com`, solo richieste GET senza chiave). Dopo un rifiuto per troppe richieste (429) o un blocco (418) nessuna
  richiesta fino alla fine della pausa chiesta (almeno 2 o 10 minuti): l'indirizzo della macchina è lo stesso del bot.
* **Ordini simulati con le spese vere** (decisione del 7 novembre): 0,05% a mercato, 0,02% con ordine limite eseguito; scarto di prezzo
  0,01% su BTC, ETH e SOL e 0,02% sulle altre, sempre contro di noi.
* **Minuto per minuto**, su tutte le candele da 1 minuto chiuse dall'ultimo controllo (anche dopo giorni di fermo: si legge finché il
  recupero è completo, altrimenti errore e nessuna decisione):
  * stop, obiettivo e liquidazione scattano sul **prezzo mark** (come gli ordini veri del trader, `workingType=MARK_PRICE`); si esce al
    livello meno lo scarto, o all'apertura del minuto se il minuto apre già oltre; stop e obiettivo nello stesso minuto: vale lo stop;
  * l'ordine limite si esegue solo se il prezzo **passa oltre** il limite (non basta toccarlo: in coda prima di noi c'è altra gente);
  * il minuto in cui parte un ordine non conta: si comincia dal minuto dopo (i prezzi di prima non potevano toccarlo).
  Liquidazione: si perde tutto il margine della posizione (margine separato), al prezzo approssimato (1/leva meno lo 0,5%).
* **Funding vero**: ogni pagamento pubblicato da Binance (`/fapi/v1/fundingRate`), anche se arriva in ritardo, si applica una volta
  sola alla posizione che era aperta in quel momento (anche se nel frattempo si è chiusa).
* **Stop e obiettivo solo per il loro lato** e **i conti di ogni posizione** (nome dell'ordine, spese, funding, uscita e modo), letti da
  `esito_ordine` (controllo del 26 novembre 2026, punti 2.2 e 2.4).
* **Un solo stato, su file, sotto blocco**: ogni operazione rilegge il file e lo riscrive sotto un blocco, così il servizio e il comando
  «chiudi» lanciato a mano non si sovrascrivono (revisione del 24 novembre 2026, problema 152).
* Stessa interfaccia di `conto_demo.ContoDemo`: `avvio.Trader` non sa se il conto è vero o simulato.
"""
from __future__ import annotations

import fcntl
import json
import time
from contextlib import contextmanager
from pathlib import Path
from typing import Callable, Optional
from urllib.parse import urlencode, urlparse

import requests

from trader_ai.conto_demo import candele_da_klines

HOST_PUBBLICO = "fapi.binance.com"
COMMISSIONE_MERCATO = 0.0005
COMMISSIONE_LIMITE = 0.0002
MANTENIMENTO = 0.005
CAPITALE_INIZIALE = 1000.0
MIN = 60_000


def scarto(simbolo: str) -> float:
    return 0.0001 if simbolo in ("BTCUSDT", "ETHUSDT", "SOLUSDT") else 0.0002


class MercatoPubblico:
    """Solo dati pubblici, solo GET, nessuna chiave."""

    def __init__(self, simbolo: str, http: Callable = requests.get) -> None:
        self.simbolo, self.http = simbolo, http
        self.pausa_fino = 0.0
        self._filtri: Optional[dict] = None

    def chiedi(self, percorso: str, parametri: dict):
        if time.time() < self.pausa_fino:
            raise RuntimeError(f"pausa chiesta da Binance per altri {self.pausa_fino - time.time():.0f} s")
        url = f"https://{HOST_PUBBLICO}{percorso}?{urlencode(parametri)}"
        if urlparse(url).hostname != HOST_PUBBLICO:
            raise ValueError(f"indirizzo non ammesso: {url}")
        r = self.http(url, timeout=15)
        if r.status_code in (418, 429):
            try:
                attesa = float((getattr(r, "headers", None) or {}).get("Retry-After"))
            except (TypeError, ValueError):
                attesa = 0.0
            self.pausa_fino = time.time() + max(attesa, 600.0 if r.status_code == 418 else 120.0)
            raise RuntimeError(f"GET {percorso}: {r.status_code}: pausa")
        if r.status_code >= 400:
            raise RuntimeError(f"GET {percorso}: {r.status_code} {r.text[:200]}")
        return r.json()

    def klines(self, intervallo: str, n: int = 200, inizio_ms: Optional[int] = None) -> list:
        p = {"symbol": self.simbolo, "interval": intervallo, "limit": n}
        if inizio_ms is not None:
            p["startTime"] = inizio_ms
        return self.chiedi("/fapi/v1/klines", p)

    def klines_mark(self, n: int = 1000, inizio_ms: Optional[int] = None) -> list:
        p = {"symbol": self.simbolo, "interval": "1m", "limit": n}
        if inizio_ms is not None:
            p["startTime"] = inizio_ms
        return self.chiedi("/fapi/v1/markPriceKlines", p)

    def mercato(self) -> dict:
        pi = self.chiedi("/fapi/v1/premiumIndex", {"symbol": self.simbolo})
        oi = self.chiedi("/fapi/v1/openInterest", {"symbol": self.simbolo})
        return {"prezzo": float(pi["markPrice"]), "indice": float(pi.get("indexPrice") or 0) or None,
                "funding": float(pi["lastFundingRate"]), "prossimo_funding_ms": int(pi["nextFundingTime"]),
                "interesse_aperto": float(oi["openInterest"])}

    def interesse_aperto_storia(self, periodo: str = "15m", n: int = 18) -> list:
        """[(ora in ms, interesse aperto)] a intervalli di `periodo` (pagina pubblica dei dati dei future, stesso indirizzo)."""
        righe = self.chiedi("/futures/data/openInterestHist", {"symbol": self.simbolo, "period": periodo, "limit": n})
        return [(int(r["timestamp"]), float(r["sumOpenInterest"])) for r in righe]

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


def _minuto_dopo(ms: int) -> int:
    return ms - ms % MIN + MIN


class ContoSimulato:
    def __init__(self, mercato: MercatoPubblico, file_stato: Path, ora_ms: Callable[[], int] = lambda: int(time.time() * 1000),
                 capitale: float = CAPITALE_INIZIALE) -> None:
        self.m, self.simbolo, self.file, self.ora_ms = mercato, mercato.simbolo, Path(file_stato), ora_ms
        self.capitale = capitale
        self._ultimo_aggiornamento = -1
        self.s: dict = {}

    @property
    def pausa_fino(self) -> float:
        return self.m.pausa_fino

    # --- stato: riletto e riscritto sotto blocco a ogni operazione -------------------------------------------------
    @contextmanager
    def _stato(self, scrivi: bool = True):
        self.file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.file.with_suffix(".lock"), "a") as blocco:
            fcntl.flock(blocco, fcntl.LOCK_EX)
            try:
                try:
                    self.s = json.loads(self.file.read_text())
                except FileNotFoundError:
                    self.s = {"portafoglio": self.capitale, "posizione": None, "ordini": [], "algo": [], "leva": 1,
                              "ultimo_minuto_ms": None, "ultimo_funding_ms": None, "movimenti": [], "prossimo_id": 1,
                              "chiuse": [], "funding_applicati": []}
                yield self.s
                if scrivi:
                    tmp = self.file.with_suffix(".tmp")
                    tmp.write_text(json.dumps(self.s, ensure_ascii=False, indent=1))
                    tmp.replace(self.file)
            finally:
                fcntl.flock(blocco, fcntl.LOCK_UN)

    def _movimento(self, cosa: str, importo: float, **altro) -> None:
        self.s["portafoglio"] += importo
        self.s["movimenti"] = (self.s["movimenti"] + [{"ora_ms": self.ora_ms(), "cosa": cosa, "importo": round(importo, 6),
                                                          **altro}])[-500:]

    # --- il mercato fa il suo corso --------------------------------------------------------------------------------
    def aggiorna(self, forza: bool = False) -> None:
        adesso = self.ora_ms()
        if not forza and adesso - self._ultimo_aggiornamento < 5000:
            return
        with self._stato():
            self._aggiorna(adesso)
        self._ultimo_aggiornamento = adesso

    def _aggiorna(self, adesso: int) -> None:
        if self.s["ultimo_minuto_ms"] is None:
            self.s["ultimo_minuto_ms"] = adesso - adesso % MIN
            self.s["ultimo_funding_ms"] = adesso
            return
        ultimo_chiuso = adesso - adesso % MIN                   # inizio del minuto in corso = fine dell'ultimo chiuso
        while self.s["ultimo_minuto_ms"] < ultimo_chiuso:
            da = self.s["ultimo_minuto_ms"]
            ultimi = {int(k[0]): k for k in self.m.klines("1m", 1000, da)}
            mark = {int(k[0]): k for k in self.m.klines_mark(1000, da)}
            minuti = sorted(t for t in ultimi if da <= t and int(ultimi[t][6]) + 1 <= adesso)
            if not minuti:
                raise RuntimeError(f"candele da 1 minuto mancanti dal {da}: nessuna decisione finché non arrivano")
            for t in minuti:
                k = ultimi[t]
                km = mark.get(t, k)                             # senza la candela mark si usa quella dei prezzi
                self._candela(t, float(k[1]), float(k[2]), float(k[3]), float(km[1]), float(km[2]), float(km[3]))
                self.s["ultimo_minuto_ms"] = int(k[6]) + 1
                self.s["tolti"] = [a for a in self.s.get("tolti", []) if a["tolto_ms"] >= self.s["ultimo_minuto_ms"]]
        self._funding(adesso)

    def _candela(self, t: int, apertura: float, massimo: float, minimo: float,
                 m_apertura: float, m_massimo: float, m_minimo: float) -> None:
        sc = scarto(self.simbolo)
        p = self.s["posizione"]
        if p is None:
            for o in list(self.s["ordini"]):
                if t < _minuto_dopo(o["messo_ms"]):
                    continue
                oltre = minimo < o["prezzo"] if o["lato"] == "lungo" else massimo > o["prezzo"]
                if oltre:
                    self.s["ordini"].remove(o)
                    self._apri_posizione(o["lato"], o["quantita"], o["prezzo"], o["leva"], COMMISSIONE_LIMITE,
                                         "limite eseguito", aperta_ms=t, cid=o.get("cid"))
                    p = self.s["posizione"]
                    break
        if p is None or t < _minuto_dopo(p["aperta_ms"]) - (MIN if p.get("da_limite") else 0):
            return
        lungo = p["lato"] == "lungo"
        # sempre il caso peggiore per noi (revisioni del 24 novembre, problemi 163 e 167):
        # * l'obiettivo conta dal minuto dopo quello in cui è nato (i prezzi di prima non potevano toccarlo);
        # * lo stop conta già nel minuto in cui nasce, e uno stop tolto resta valido fino alla fine del suo minuto: quando lo stop si
        #   sposta la posizione non resta mai scoperta; fra più stop validi nello stesso minuto vale il più vicino al prezzo.
        #   Ogni stop vale dal minuto in cui nasce al minuto in cui viene tolto, compresi (problema 170).
        def vivo(a):
            nato = a.get("messo_ms", 0) - a.get("messo_ms", 0) % MIN
            tolto = a.get("tolto_ms")
            return nato <= t and (tolto is None or t <= tolto - tolto % MIN)
        # solo gli stop messi per una posizione di questo lato: uno stop rimasto da un'operazione dell'altro lato non chiude questa
        # (controllo del 26 novembre 2026, punto 2.2: uno stop di un lungo a 89.200 chiudeva un corto aperto dopo)
        stop_validi = [a for a in self.s["algo"] + self.s.get("tolti", [])
                       if a["tipo"] == "STOP_MARKET" and a.get("lato", p["lato"]) == p["lato"] and vivo(a)]
        stop = max(stop_validi, key=lambda a: a["prezzo"] if lungo else -a["prezzo"], default=None)
        obiettivo = next((a for a in self.s["algo"] if a["tipo"] == "TAKE_PROFIT_MARKET"
                          and a.get("lato", p["lato"]) == p["lato"] and t >= _minuto_dopo(a.get("messo_ms", 0))), None)
        if p.get("da_limite") and t == p["aperta_ms"]:
            obiettivo = None
        avverso = m_minimo if lungo else m_massimo
        favorevole = m_massimo if lungo else m_minimo
        livelli = [(p["liquidazione"], "liquidazione")] + ([(stop["prezzo"], "stop")] if stop else [])
        livelli.sort(key=lambda x: -x[0] if lungo else x[0])   # il primo che si incontra andando contro
        for livello, come in livelli:
            if (avverso <= livello) if lungo else (avverso >= livello):
                if come == "liquidazione":
                    self._chiudi_posizione(livello, "liquidazione", t, perdita_margine=True)
                else:
                    oltre = (m_apertura <= livello) if lungo else (m_apertura >= livello)
                    uscita = (apertura if oltre else livello) * ((1 - sc) if lungo else (1 + sc))
                    self._chiudi_posizione(uscita, "stop", t)
                return
        if obiettivo and ((favorevole >= obiettivo["prezzo"]) if lungo else (favorevole <= obiettivo["prezzo"])):
            oltre = (m_apertura >= obiettivo["prezzo"]) if lungo else (m_apertura <= obiettivo["prezzo"])
            uscita = (apertura if oltre else obiettivo["prezzo"]) * ((1 - sc) if lungo else (1 + sc))
            self._chiudi_posizione(uscita, "obiettivo", t)

    def _funding(self, adesso: int) -> None:
        """I pagamenti pubblicati dall'ultimo controllo meno 2 ore (arrivano anche in ritardo); ognuno si applica una volta sola,
        alla posizione aperta in quel momento (quella di adesso o una già chiusa)."""
        dal = (self.s["ultimo_funding_ms"] or adesso) - 2 * 3600_000
        posizioni = list(self.s["chiuse"]) + ([self.s["posizione"]] if self.s["posizione"] else [])
        if posizioni:
            for f in self.m.funding_da(dal):
                t = int(f["fundingTime"])
                if t > adesso or t in self.s["funding_applicati"]:
                    continue
                for p in posizioni:
                    if p["aperta_ms"] <= t and (p.get("chiusa_ms") is None or t < p["chiusa_ms"]):
                        prezzo = float(f.get("markPrice") or 0) or p["entrata"]
                        valore = p["quantita"] * prezzo
                        tasso = float(f["fundingRate"])
                        importo = -valore * tasso if p["lato"] == "lungo" else valore * tasso
                        self._movimento("funding", importo, tasso=tasso, funding_ms=t)
                        p["funding"] = p.get("funding", 0.0) + importo      # anche su una posizione già chiusa
                        self.s["funding_applicati"] = (self.s["funding_applicati"] + [t])[-50:]
                        break
        self.s["ultimo_funding_ms"] = adesso

    def _apri_posizione(self, lato, quantita, prezzo, leva, commissione, come, aperta_ms=None, cid=None) -> None:
        valore = quantita * prezzo
        self._movimento("commissione", -valore * commissione, come=come)
        # ogni posizione tiene i suoi conti (nome dell'ordine, spese, funding, uscita): li legge `esito_ordine` (controllo del 26
        # novembre 2026, punti 2.2 e 2.4: la memoria del modello aveva uscite sbagliate e un'operazione mancante)
        self.s["posizione"] = {"lato": lato, "quantita": quantita, "entrata": prezzo, "leva": leva,
                               "margine": valore / leva, "liquidazione": liquidazione(lato, prezzo, leva),
                               "aperta_ms": aperta_ms if aperta_ms is not None else self.ora_ms(),
                               "da_limite": aperta_ms is not None, "cid": cid, "spese_entrata": valore * commissione,
                               "spese": valore * commissione, "funding": 0.0}

    def _chiudi_posizione(self, uscita: float, come: str, t: Optional[int] = None, perdita_margine: bool = False) -> None:
        p = self.s["posizione"]
        segno = 1 if p["lato"] == "lungo" else -1
        if perdita_margine:
            self._movimento("liquidazione", -p["margine"], prezzo=uscita)
            p["risultato_prezzo"] = -p["margine"]
        else:
            p["risultato_prezzo"] = segno * (uscita - p["entrata"]) * p["quantita"]
            self._movimento("risultato", p["risultato_prezzo"], prezzo=uscita, come=come)
            self._movimento("commissione", -p["quantita"] * uscita * COMMISSIONE_MERCATO, come=come)
            p["spese"] = p.get("spese", 0.0) + p["quantita"] * uscita * COMMISSIONE_MERCATO
        p["uscita"], p["come"] = uscita, come
        p["chiusa_ms"] = t if t is not None else self.ora_ms()
        self.s["chiuse"] = (self.s["chiuse"] + [p])[-20:]
        self.s["posizione"] = None
        self.s["algo"], self.s["tolti"] = [], []      # stop e obiettivo «chiudi tutto» non servono più

    # --- la stessa interfaccia di ContoDemo ------------------------------------------------------------------------
    def candele(self, intervallo: str, ora_ms: Optional[int] = None, n: int = 200, inizio_ms: Optional[int] = None) -> list:
        return candele_da_klines(self.m.klines(intervallo, n, inizio_ms), ora_ms or self.ora_ms())

    def mercato(self) -> dict:
        return self.m.mercato()

    def interesse_aperto_storia(self) -> list:
        return self.m.interesse_aperto_storia()

    def esito_ordine(self, cid: Optional[str]) -> Optional[dict]:
        """Che cosa è successo all'ordine di apertura `cid`: {"stato": "in_attesa"} se è un limite ancora sul libro; per una
        posizione aperta o chiusa: entrata, quantità, ora di esecuzione, spese e funding, e da chiusa anche ora, prezzo e modo
        d'uscita e risultato netto; None se non si è mai eseguito (annullato) o se non si trova più."""
        if not cid:
            return None
        self.aggiorna()
        with self._stato(scrivi=False):
            if any(o.get("cid") == cid for o in self.s["ordini"]):
                return {"stato": "in_attesa"}
            for p in ([self.s["posizione"]] if self.s["posizione"] else []) + list(reversed(self.s["chiuse"])):
                if p.get("cid") != cid:
                    continue
                e = {"stato": "aperta" if p.get("chiusa_ms") is None else "chiusa", "entrata": p["entrata"],
                     "quantita": p["quantita"], "eseguita_ms": p["aperta_ms"], "da_limite": bool(p.get("da_limite")),
                     "spese_entrata": p.get("spese_entrata"), "spese": p.get("spese", 0.0), "funding": p.get("funding", 0.0)}
                if p.get("chiusa_ms") is not None:
                    e.update(chiusa_ms=p["chiusa_ms"], uscita=p.get("uscita"), come=p.get("come"),
                             risultato_prezzo=p.get("risultato_prezzo"),
                             netto=(p.get("risultato_prezzo") or 0.0) - p.get("spese", 0.0) + p.get("funding", 0.0))
                return e
            return None

    def storia(self) -> dict:
        """Le posizioni chiuse e i movimenti salvati (sola lettura): servono a ricostruire la memoria scritta prima del 26
        novembre 2026, quando le posizioni non tenevano ancora i loro conti (avvio.Trader._ripara_memoria)."""
        self.aggiorna()
        with self._stato(scrivi=False):
            return json.loads(json.dumps({k: self.s.get(k) for k in ("chiuse", "movimenti", "funding_applicati", "posizione")}))

    def filtri(self) -> dict:
        return self.m.filtri()

    def modo_doppio(self) -> bool:
        return False

    def saldo(self) -> dict:
        self.aggiorna()
        with self._stato(scrivi=False):
            p = self.s["posizione"]
            aperto, impegnato = 0.0, 0.0
            if p is not None:
                prezzo = self.m.mercato()["prezzo"]
                aperto = max((1 if p["lato"] == "lungo" else -1) * (prezzo - p["entrata"]) * p["quantita"], -p["margine"])
                impegnato = p["margine"]
            impegnato += sum(o["quantita"] * o["prezzo"] / o["leva"] for o in self.s["ordini"])
            return {"conto": self.s["portafoglio"] + aperto, "disponibile": self.s["portafoglio"] - impegnato,
                    "portafoglio": self.s["portafoglio"]}

    def posizioni_tutte(self) -> list:
        self.aggiorna()
        with self._stato(scrivi=False):
            p = self.s["posizione"]
            if p is None:
                return []
            return [{"simbolo": self.simbolo, "lato": p["lato"], "quantita": p["quantita"], "entrata": p["entrata"],
                     "leva": p["leva"], "liquidazione": p["liquidazione"]}]

    posizioni_simbolo = posizioni_tutte

    def ordini_tutti(self) -> list:
        self.aggiorna()
        with self._stato(scrivi=False):
            return ([{"symbol": self.simbolo, "clientOrderId": o["cid"], "_algo": False} for o in self.s["ordini"]]
                    + [{"symbol": self.simbolo, "algoId": a["algoId"], "clientAlgoId": a["cid"], "_algo": True}
                       for a in self.s["algo"]])

    ordini_simbolo = ordini_tutti

    def prepara(self, leva: int) -> None:
        with self._stato():
            self.s["leva"] = int(leva)

    def apri(self, lato: str, quantita: float, cid: str, tipo: str = "MARKET", prezzo: Optional[float] = None) -> dict:
        mark = self.m.mercato()["prezzo"]
        disponibile = self.saldo()["disponibile"]
        with self._stato():
            self._aggiorna(self.ora_ms())
            leva = self.s["leva"]
            compra = lato == "lungo"
            incrocia = tipo == "LIMIT" and ((prezzo >= mark) if compra else (prezzo <= mark))
            if tipo == "MARKET" or incrocia:         # un limite che incrocia il prezzo si esegue subito, a mercato
                esecuzione = mark * ((1 + scarto(self.simbolo)) if compra else (1 - scarto(self.simbolo)))
                if quantita * esecuzione / leva + quantita * esecuzione * COMMISSIONE_MERCATO > disponibile:
                    raise RuntimeError('{"code":-2019,"msg":"Margin is insufficient."}')
                self._apri_posizione(lato, quantita, esecuzione, leva, COMMISSIONE_MERCATO, "a mercato", cid=cid)
                return {"avgPrice": str(esecuzione), "executedQty": str(quantita)}
            if quantita * prezzo / leva > disponibile:
                raise RuntimeError('{"code":-2019,"msg":"Margin is insufficient."}')
            self.s["ordini"].append({"cid": cid, "lato": lato, "quantita": quantita, "prezzo": prezzo, "leva": leva,
                                     "messo_ms": self.ora_ms()})
            return {"avgPrice": "0", "executedQty": "0"}

    def condizionato(self, lato_posizione: str, tipo: str, prezzo: float, cid: str) -> dict:
        mark = self.m.mercato()["prezzo"]
        lungo = lato_posizione == "lungo"
        subito = (mark <= prezzo if lungo else mark >= prezzo) if tipo == "STOP_MARKET" else \
            (mark >= prezzo if lungo else mark <= prezzo)
        if subito:
            raise RuntimeError('{"code":-2021,"msg":"Order would immediately trigger."}')
        with self._stato():
            self._aggiorna(self.ora_ms())             # i minuti già chiusi si contano con gli stop di prima (problema 170)
            algo_id = self.s["prossimo_id"]
            self.s["prossimo_id"] += 1
            self.s["algo"].append({"algoId": algo_id, "cid": cid, "tipo": tipo, "prezzo": prezzo, "lato": lato_posizione,
                                   "messo_ms": self.ora_ms()})
        return {"algoId": algo_id}

    def annulla_condizionato(self, ordine: dict) -> None:
        with self._stato():
            self._aggiorna(self.ora_ms())             # i minuti già chiusi si contano con lo stop ancora al suo posto
            tolti = [a for a in self.s["algo"] if a["algoId"] == ordine.get("algoId")]
            self.s["algo"] = [a for a in self.s["algo"] if a["algoId"] != ordine.get("algoId")]
            adesso = self.ora_ms()
            self.s["tolti"] = self.s.get("tolti", []) + [{**a, "tolto_ms": adesso} for a in tolti]

    def annulla_tutto(self) -> None:
        with self._stato():
            # prima i minuti già chiusi, con gli ordini ancora al loro posto (un limite eseguito in un minuto appena chiuso si
            # esegue, come sul conto vero: revisione del 26 novembre 2026, S7)
            self._aggiorna(self.ora_ms())
            self.s["ordini"], self.s["algo"] = [], []

    def chiudi(self, pos: Optional[dict], cid: str) -> Optional[dict]:
        esito = None
        mark = self.m.mercato()["prezzo"]
        with self._stato():
            self._aggiorna(self.ora_ms())             # prima il mercato fa il suo corso (uno stop può essere già scattato)
            if self.s["posizione"] is not None and pos:
                lungo = self.s["posizione"]["lato"] == "lungo"
                uscita = mark * ((1 - scarto(self.simbolo)) if lungo else (1 + scarto(self.simbolo)))
                self._chiudi_posizione(uscita, "chiusa a mercato")
                esito = {"avgPrice": str(uscita)}
            self.s["ordini"], self.s["algo"] = [], []
        return esito
