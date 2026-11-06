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
    modo (controllo a ogni valutazione, ogni ora);
  * **il confronto fra le posizioni vere e quelle volute**: ogni ora, senza ordini in corso, le quantità che Binance dice che teniamo
    contro quelle decise all'ultimo ribilancio; ogni moneta con uno scarto oltre il 2% del conto va su RTDB in
    `/demo_binance/confronto` (si sistema da sola al ribilancio dopo).
* **Il conto ridotto** (il proprietario, 6 novembre 2026: «voglio partire con 250 euro», poi «spegni eventi»; prova 148,
  `research/programma7/RISULTATI_OTTANTASEIESIMA.md`): con un numero nel file `ops/demo_binance_capitale` (per esempio 280) il demo
  lavora come un conto di quella cifra. Il valore usato per le posizioni, lo stop e i rapporti è il capitale più il guadagno da quando
  il conto ridotto è partito; il resto del conto demo resta fermo. I filtri degli ordini sono severi almeno come quelli del conto vero
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
ATTESA_DOPO_ERRORE_S = 1800
STOP_CONTO = 0.35                      # il proprietario, 1° novembre 2026: chiude tutto a −35% dal massimo del conto
SOGLIA_CONFRONTO = 0.02                # uno scarto oltre il 2% del conto su una moneta si segnala
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


def id_ordine(giorno: int, simbolo: str, tentativo: int = 0) -> str:
    """L'identificativo dell'ordine per Binance (ammessi solo ``.A-Za-z0-9:/_-``, al massimo 36): le monete con il nome in altri
    caratteri (per esempio 币安人生USDT) prendono un'impronta del nome. Il 24 ottobre il primo ribilancio sul demo si e' fermato qui,
    e il secondo tentativo dello stesso giorno con «ClientOrderId is duplicated»: per questo c'e' anche il tentativo (i secondi
    dell'ora, modulo 100.000)."""
    nome = simbolo if re.fullmatch(r"[.A-Za-z0-9:/_-]+", simbolo) else "h" + hashlib.sha1(simbolo.encode()).hexdigest()[:12]
    return f"g1d-{giorno}-{tentativo % 100_000}-{nome}"[:36]


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
                 interruttore: Path = INTERRUTTORE, file_eventi: Path = FILE_EVENTI,
                 interruttore_eventi: Path = INTERRUTTORE_EVENTI, file_chiudi: Path = FILE_CHIUDI,
                 file_riparti: Path = FILE_RIPARTI, file_capitale: Path = FILE_CAPITALE) -> None:
        self.fb = fb
        self.file_capitale = Path(file_capitale)
        self._scarto = 0.0                          # valore vero del conto demo meno il valore del conto ridotto
        self.file_chiudi, self.file_riparti = Path(file_chiudi), Path(file_riparti)
        self._cliente = cliente
        self.file_stato, self.file_g1, self.interruttore = Path(file_stato), Path(file_g1), Path(interruttore)
        self.file_eventi, self.interruttore_eventi = Path(file_eventi), Path(interruttore_eventi)
        self._ultimo_tentativo = 0.0

    # ---- stato ----
    def acceso(self) -> bool:
        if self.interruttore == INTERRUTTORE and os.environ.get("PYTEST_CURRENT_TEST"):
            return False
        return self.interruttore.exists()

    def eventi_accesi(self) -> bool:
        if self.interruttore_eventi == INTERRUTTORE_EVENTI and os.environ.get("PYTEST_CURRENT_TEST"):
            return False
        return self.interruttore_eventi.exists()

    def capitale_voluto(self) -> Optional[float]:
        """Il capitale del conto ridotto dal file `ops/demo_binance_capitale` (un numero in USDT); None se non c'è."""
        if self.file_capitale == FILE_CAPITALE and os.environ.get("PYTEST_CURRENT_TEST"):
            return None
        try:
            v = float(self.file_capitale.read_text(encoding="utf-8").strip().replace(",", "."))
        except Exception:  # noqa: BLE001
            return None
        return v if v > 0 else None

    def _archivia_fase(self, nome: str) -> None:
        """I valori della fase di prima passano in `/demo_binance/fasi/{nome}/`; si cancellano solo dopo la copia."""
        if self.fb is None:
            return
        for ramo in RAMI_DELLA_FASE:
            v = self.fb.get_rtdb(f"/demo_binance/{ramo}")
            if not isinstance(v, dict) or not v:
                continue
            self.fb.set_rtdb(f"/demo_binance/fasi/{nome}/{ramo}", v)
            for k in list(v):
                self.fb.set_rtdb(f"/demo_binance/{ramo}/{k}", None)

    def conto_ridotto(self, c: ClienteDemo, st: dict, now: float) -> dict:
        """Il demo come un conto più piccolo (vedi in cima): all'avvio (o a un capitale nuovo nel file) si fissa lo scarto fra il
        valore vero del conto demo e il capitale scelto, si archivia la fase di prima e si torna subito ai pesi di oggi."""
        voluto = self.capitale_voluto()
        cr = st.get("conto_ridotto")
        if voluto and (not cr or float(cr["capitale"]) != voluto) and not st.get("ordini"):
            self._scarto = 0.0
            vero = self._conto(c)[0]
            data = time.strftime("%Y-%m-%d", time.gmtime(now))
            prima = f"capitale_{float(cr['capitale']):g}" if cr else "conto_intero"
            self._archivia_fase(f"{prima}_fino_al_{data}".replace(".", "_"))
            cr = {"capitale": voluto, "valore_vero_all_avvio": vero, "dal": now, "data": data}
            st["conto_ridotto"] = cr
            st["capitale_iniziale"] = voluto
            st["massimo"] = voluto
            st["ultimo_giorno"] = 0                          # al giro stesso le posizioni si riportano ai pesi, alla misura nuova
            st.pop("obiettivi", None)
            st.pop("ultima_valutazione", None)
            self._scrivi("conto_ridotto", cr)
            print(f"[demo_binance] conto ridotto: il demo lavora come un conto di {voluto:g} USDT (valore vero {vero:,.2f})")
        self._scarto = float(cr["valore_vero_all_avvio"]) - float(cr["capitale"]) if cr else 0.0
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
            self.fb.set_rtdb(f"/demo_binance/{ramo}", valore)

    def _comando(self, percorso: str) -> bool:
        if self.fb is None:
            return False
        try:
            return bool(self.fb.get_rtdb(percorso))
        except Exception:  # noqa: BLE001
            return False

    def _comando_file(self, f: Path, st: dict, chiave: str) -> bool:
        """Il comando come file: vale una volta per ogni testo nuovo (il file resta nel repository)."""
        if os.environ.get("PYTEST_CURRENT_TEST") and f in (FILE_CHIUDI, FILE_RIPARTI):
            return False
        try:
            testo_file = f.read_text(encoding="utf-8").strip() if f.exists() else ""
        except Exception:  # noqa: BLE001
            return False
        if testo_file and testo_file != st.get(chiave):
            st[chiave] = testo_file
            return True
        return False

    def chiudi_tutto(self, c: ClienteDemo, st: dict, now: float, motivo: str) -> dict:
        """Annulla tutti gli ordini aperti e chiude tutte le posizioni a mercato; poi il demo resta fermo (``st['fermo']``)."""
        for s in sorted({o["symbol"] for o in c.chiedi("GET", "/fapi/v1/openOrders", firmata=True) or []}):
            c.chiedi("DELETE", "/fapi/v1/allOpenOrders", {"symbol": s}, firmata=True)
        equity, _, posizioni = self._conto(c)
        chiuse, errori = [], []
        for s, q in sorted(posizioni.items()):
            p = {"symbol": s, "side": "SELL" if q > 0 else "BUY", "type": "MARKET", "quantity": testo(abs(q)), "reduceOnly": "true"}
            try:
                c.chiedi("POST", "/fapi/v1/order", p, firmata=True)
                chiuse.append(s)
            except RuntimeError as exc:
                errori.append({"simbolo": s, "errore": str(exc)[:200]})
        st.pop("ordini", None)
        st["fermo"] = {"motivo": motivo, "ora": now, "equity": round(equity, 2), "chiuse": len(chiuse), "errori": errori}
        self._scrivi("fermo", st["fermo"])
        self._scrivi("stato", {"stato": f"fermo: {motivo}", "equity": round(equity, 2), "aggiornato": now,
                               "capitale_iniziale": float(st.get("capitale_iniziale", equity))})
        print(f"[demo_binance] CHIUSO TUTTO ({motivo}): {len(chiuse)} posizioni chiuse, {len(errori)} errori")
        return st

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
            st = self.conto_ridotto(c, st, now)
            da_dashboard = self._comando(COMANDO_CHIUDI)
            da_file = self._comando_file(self.file_chiudi, st, "eseguito_chiudi")
            if da_dashboard or da_file:
                if not st.get("fermo"):
                    st = self.chiudi_tutto(c, st, now, "pulsante della dashboard" if da_dashboard else "comando chiudi tutto")
                if da_dashboard:
                    self.fb.set_rtdb(COMANDO_CHIUDI, False)
            if st.get("fermo"):
                da_dashboard = self._comando(COMANDO_RIPARTI)
                if da_dashboard or self._comando_file(self.file_riparti, st, "eseguito_riparti"):
                    st.pop("fermo")
                    st["ultimo_giorno"] = 0                     # al giro dopo si torna ai pesi di oggi
                    st["massimo"] = self._conto(c)[0]           # lo stop si misura dalla ripartenza
                    if da_dashboard:
                        self.fb.set_rtdb(COMANDO_RIPARTI, False)
                    self._scrivi("fermo", None)
                    print("[demo_binance] ripartito")
                else:
                    if now - float(st.get("ultima_valutazione", 0)) >= OGNI_VALUTAZIONE_S:
                        equity = self._conto(c)[0]
                        st["ultima_valutazione"] = now
                        self._scrivi(f"giorni/{time.strftime('%Y-%m-%d', time.gmtime(now))}", round(equity, 2))
                    self.salva(st)
                    return
            if st.get("ordini") and now >= float(st["ordini"]["piazzati"]) + VALIDITA_LIMITE_S:
                st = self.chiudi_ordini(c, st, now)
            g1 = json.loads(self.file_g1.read_text(encoding="utf-8")) if self.file_g1.exists() else {}
            giorno = int(g1.get("ultimo_lunedi", 0))
            aperte = self.eventi_aperti()
            firma, monete_eventi = sorted(aperte), sorted({p.get("simbolo") for p in aperte.values() if p.get("simbolo")})
            pesi = somma_pesi(g1.get("pesi") or {}, pesi_eventi(aperte))
            if giorno and giorno > int(st.get("ultimo_giorno", 0)) and not st.get("ordini"):
                st = self.ribilancia(c, st, pesi, giorno, now)
                st["eventi_firma"], st["eventi_monete"] = firma, monete_eventi
            elif (firma != list(st.get("eventi_firma") or []) and not st.get("ordini") and int(st.get("ultimo_giorno", 0))
                  and (int(st["ultimo_giorno"]) >= int(now // 86400) or now >= int(now // 86400) * 86400 + ATTESA_G1_S)):
                toccate = set(monete_eventi) | set(st.get("eventi_monete") or []) | {"BTCUSDT"}
                st = self.ribilancia(c, st, pesi, int(st["ultimo_giorno"]), now, solo=toccate)
                st["eventi_firma"], st["eventi_monete"] = firma, monete_eventi
            if now - float(st.get("ultima_valutazione", 0)) >= OGNI_VALUTAZIONE_S:
                st = self.valuta(c, st, now)
                if not st.get("fermo"):
                    st = self.controlla_margine(c, st, now)
                    st = self.confronta(c, st, now)
            self.salva(st)
        except Exception as exc:  # noqa: BLE001
            self._ultimo_tentativo = now
            print(f"[demo_binance] errore, si riprova fra 30 minuti: {exc}")
            self._scrivi("errore", {"testo": str(exc)[:300], "ora": now})

    def _conto(self, c: ClienteDemo) -> tuple:
        conto = c.chiedi("GET", "/fapi/v2/account", firmata=True)
        self._separati = sorted(x["symbol"] for x in conto.get("positions", []) if x.get("isolated") in (True, "true"))
        posizioni = {x["symbol"]: float(x["positionAmt"]) for x in conto.get("positions", []) if float(x.get("positionAmt") or 0)}
        return float(conto["totalMarginBalance"]) - self._scarto, float(conto["totalWalletBalance"]) - self._scarto, posizioni

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
        sistemate, errori = [], []
        for s in separati:
            q = posizioni.get(s, 0.0)
            if q:
                try:
                    c.chiedi("POST", "/fapi/v1/order", {"symbol": s, "side": "SELL" if q > 0 else "BUY", "type": "MARKET",
                                                        "quantity": testo(abs(q)), "reduceOnly": "true"}, firmata=True)
                except RuntimeError as exc:
                    errori.append({"simbolo": s, "errore": str(exc)[:200]})
                    continue
            e = self._margine_unico(c, s)
            (errori.append({"simbolo": s, "errore": e}) if e else sistemate.append(s))
        if sistemate and any(posizioni.get(s) for s in sistemate):
            st["ultimo_giorno"] = 0                             # si riaprono subito ai pesi di oggi
        self._scrivi("margine", {"controllato": now, "separati_trovati": separati, "sistemate": sistemate, "errori": errori})
        if separati:
            print(f"[demo_binance] margine separato su {separati}: sistemate {sistemate}, errori {len(errori)}")
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
            print(f"[demo_binance] posizioni diverse da quelle volute: {[d['simbolo'] for d in differenze]}")
        return st

    def ribilancia(self, c: ClienteDemo, st: dict, pesi: dict, giorno: int, now: float, solo: Optional[set] = None) -> dict:
        """Porta il conto ai pesi; con ``solo`` (un'operazione a eventi aperta o chiusa) tocca solo quelle monete."""
        f = filtri(c.chiedi("GET", "/fapi/v1/exchangeInfo"))
        if st.get("conto_ridotto"):
            f = piu_severi(f, filtri_veri())
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
        leve = set(st.get("leve") or [])
        piazzati, rifiutati = [], []
        da_fare = ordini_del_giorno(pesi, posizioni, prezzi, equity, f)
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
                    c.chiedi("POST", "/fapi/v1/leverage", {"symbol": s, "leverage": LEVA}, firmata=True)
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
        print(f"[demo_binance] {cosa}: {len(piazzati)} ordini limite sul conto demo, {len(rifiutati)} rifiutati")
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
        chiave = st["ordini"].get("chiave") or time.strftime("%Y-%m-%d", time.gmtime(int(st["ultimo_giorno"]) * 86400))
        self._scrivi(f"ribilanciamenti/{chiave}/limite", {"ordini": n, "eseguiti_a_limite": eseguiti_limite, "a_mercato": a_mercato,
                                                          "controllato": now})
        st.pop("ordini")
        return st

    def valuta(self, c: ClienteDemo, st: dict, now: float) -> dict:
        equity, wallet, posizioni = self._conto(c)
        st.setdefault("capitale_iniziale", equity)
        st["ultima_valutazione"] = now
        iniziale = float(st["capitale_iniziale"])
        st["massimo"] = max(float(st.get("massimo", iniziale)), equity)
        if equity <= (1 - STOP_CONTO) * st["massimo"]:
            return self.chiudi_tutto(c, st, now, f"stop sul conto: {100 * (equity / st['massimo'] - 1):.1f}% dal massimo")
        self._scrivi("stato", {"stato": "acceso", "equity": round(equity, 2), "saldo": round(wallet, 2), "capitale_iniziale": iniziale,
                               "rendimento": equity / iniziale - 1 if iniziale else 0.0,
                               "long": sum(1 for v in posizioni.values() if v > 0), "short": sum(1 for v in posizioni.values() if v < 0),
                               "limite_eseguiti": int(st.get("limite_eseguiti", 0)), "limite_totali": int(st.get("limite_totali", 0)),
                               "ordini_in_attesa": len((st.get("ordini") or {}).get("lista") or []), "aggiornato": now,
                               "massimo": round(st["massimo"], 2), "dal_massimo": equity / st["massimo"] - 1,
                               "stop_a": round((1 - STOP_CONTO) * st["massimo"], 2),
                               "conto_ridotto": (st.get("conto_ridotto") or {}).get("capitale"),
                               "valore_vero_del_conto_demo": round(equity + self._scarto, 2)})
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
            print(f"[demo_binance] entrate del conto non lette: {exc}")
        return st
