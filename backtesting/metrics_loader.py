"""
STORICO di open interest / long-short / taker ratio da data.binance.vision.

PERCHE' ESISTE
Il bot legge gia' open interest e long/short ratio DAL VIVO
(`bot/agents/onchain_agent.py`), ma l'endpoint REST di Binance ne tiene solo 30
giorni: troppo poco perche' il GATE 1, che valida su 4,6 anni, possa usarli. E'
il motivo per cui quelle grandezze non sono mai entrate nella ricerca.

Gli stessi numeri esistono pero' come file scaricabili, senza chiave, dal 2020.
Stessa fonte del vivo: ricerca e produzione non possono disallinearsi.

QUATTRO TRAPPOLE, tutte verificate a mano il 20 settembre 2026 — sono il motivo
per cui questo file esiste invece di tre righe di `requests.get`:

1. esistono SOLO i file giornalieri (i mensili, che ci sono per le klines, qui
   non ci sono): su tutto l'universo sarebbero ~850.000 richieste;
2. i file recenti NON sono ordinati per orario — 2026-09-18 di BTCUSDT parte
   alle 00:35, passa per le 23:20 e finisce alle 22:30;
3. i file del 2020 e inizio 2021 hanno OGNI riga duplicata (BTCUSDT
   2020-09-01: 576 righe, 288 uniche);
4. l'hostname `data.binance.vision` non sempre risponde: si usa l'origine S3,
   come gia' fa `scripts/survivorship_report.py`.

E una quinta, che nessun codice puo' risolvere: il dataset NON e' documentato
nel README ufficiale di Binance. Puo' sparire o cambiare formato senza
preavviso, quindi chi lo usa deve reggere l'assenza di un giorno senza rompersi.

SOLA LETTURA. Questo modulo scarica e legge: non tocca il registro, non tocca il
paper, e non e' collegato a niente che decida trade.
"""
from __future__ import annotations

import csv
import hashlib
import io
import os
import zipfile
from datetime import date, datetime, timedelta, timezone
from typing import Iterator

import requests
import xml.etree.ElementTree as ET

S3 = "https://s3-ap-northeast-1.amazonaws.com/data.binance.vision"
PREFIX = "data/futures/um/daily/metrics"
NS = {"s3": "http://s3.amazonaws.com/doc/2006-03-01/"}
CACHE_DIR = os.environ.get("METRICS_CACHE", "data_cache/metrics")

# Le colonne del CSV, nell'ordine in cui Binance le scrive. Dichiararle serve a
# accorgersi SUBITO se il formato cambia: un dataset non documentato che cambia
# in silenzio e' esattamente il modo in cui una ricerca si avvelena senza
# accorgersene.
COLONNE = ("create_time", "symbol", "sum_open_interest", "sum_open_interest_value",
           "count_toptrader_long_short_ratio", "sum_toptrader_long_short_ratio",
           "count_long_short_ratio", "sum_taker_long_short_vol_ratio")


class FormatoInatteso(RuntimeError):
    """Il CSV non ha le colonne attese. Meglio fermarsi che leggere numeri
    dalla colonna sbagliata: un backtest alimentato male sembra funzionare."""


def url_zip(symbol: str, giorno: date) -> str:
    return f"{S3}/{PREFIX}/{symbol}/{symbol}-metrics-{giorno.isoformat()}.zip"


def giorni(dal: date, al: date) -> Iterator[date]:
    g = dal
    while g <= al:
        yield g
        g += timedelta(days=1)


# --------------------------------------------------------------------------- #
# ELENCO — quanto storico esiste davvero, SENZA scaricarlo                     #
# --------------------------------------------------------------------------- #
def elenco_giorni(symbol: str, timeout: int = 30,
                  sessione: requests.Session | None = None) -> dict[date, int]:
    """{giorno: byte del file zip} per tutto lo storico del simbolo.

    Il listing S3 riporta gia' la DIMENSIONE di ogni file: per sapere quanto
    pesa lo storico non serve scaricarlo. Quattro richieste per simbolo invece
    di millesettecento — e' la differenza fra una misura che si fa e una che si
    rimanda."""
    get = (sessione or requests).get
    fuori: dict[date, int] = {}
    marker = ""
    while True:
        params = {"prefix": f"{PREFIX}/{symbol}/"}
        if marker:
            params["marker"] = marker
        r = get(S3, params=params, timeout=timeout)
        r.raise_for_status()
        root = ET.fromstring(r.text)
        chiavi = root.findall("s3:Contents", NS)
        if not chiavi:
            break
        for c in chiavi:
            key = c.findtext("s3:Key", "", NS)
            if not key.endswith(".zip"):       # .CHECKSUM: stesso giorno, non e' dato
                continue
            nome = key.rsplit("/", 1)[-1]
            try:
                g = date.fromisoformat(nome[:-4].rsplit("-metrics-", 1)[1])
            except (IndexError, ValueError):
                continue
            fuori[g] = int(c.findtext("s3:Size", "0", NS) or 0)
        if (root.findtext("s3:IsTruncated", "false", NS) or "false").lower() != "true":
            break
        marker = chiavi[-1].findtext("s3:Key", "", NS)
        if not marker:
            break
    return fuori


def buchi(presenti: set[date], dal: date, al: date) -> list[date]:
    """I giorni mancanti nella finestra. Un buco non e' un errore da nascondere:
    e' il dato da guardare prima di costruirci sopra una feature."""
    return [g for g in giorni(dal, al) if g not in presenti]


# --------------------------------------------------------------------------- #
# LETTURA — le tre trappole del contenuto                                     #
# --------------------------------------------------------------------------- #
def leggi_csv(testo: str) -> list[dict]:
    """Righe ORDINATE e SENZA duplicati, con i numeri gia' convertiti.

    Qui vivono la trappola 2 (file recenti non ordinati) e la 3 (file 2020/21
    con ogni riga doppia). Tenerle fuori da questa funzione significherebbe
    ricordarsene in ogni punto d'uso — cioe' dimenticarsene in uno."""
    righe = list(csv.reader(io.StringIO(testo)))
    if not righe:
        return []
    intestazione = tuple(c.strip() for c in righe[0])
    if intestazione != COLONNE:
        raise FormatoInatteso(f"colonne {intestazione} invece di {COLONNE}")

    viste: set[str] = set()
    fuori: list[dict] = []
    for r in righe[1:]:
        if len(r) != len(COLONNE):
            continue
        chiave = r[0]                      # il create_time identifica la riga
        if chiave in viste:
            continue
        viste.add(chiave)
        try:
            ts = datetime.strptime(r[0], "%Y-%m-%d %H:%M:%S").replace(
                tzinfo=timezone.utc)
            fuori.append({
                "ts": ts,
                "symbol": r[1],
                "open_interest": float(r[2]),
                "open_interest_value": float(r[3]),
                "toptrader_ls_conti": float(r[4]),
                "toptrader_ls_posizioni": float(r[5]),
                "ls_conti": float(r[6]),
                "taker_buy_sell": float(r[7]),
            })
        except ValueError:
            continue                        # riga guasta: saltata, non fatale
    fuori.sort(key=lambda d: d["ts"])
    return fuori


def _sha256(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def scarica_giorno(symbol: str, giorno: date, cache_dir: str = CACHE_DIR,
                   timeout: int = 30, verifica: bool = True,
                   sessione: requests.Session | None = None) -> bytes | None:
    """Lo zip di un giorno, dalla cache su disco o dalla rete. None se il giorno
    non esiste (404): un buco e' normale, non un guasto.

    `verifica` confronta lo SHA256 col file `.CHECKSUM` che Binance pubblica
    accanto. Costa una richiesta in piu' e vale: un download troncato produce
    uno zip che si apre lo stesso e dati incompleti che nessuno noterebbe."""
    get = (sessione or requests).get
    os.makedirs(cache_dir, exist_ok=True)
    locale = os.path.join(cache_dir, f"{symbol}-metrics-{giorno.isoformat()}.zip")
    if os.path.exists(locale):
        with open(locale, "rb") as f:
            return f.read()

    r = get(url_zip(symbol, giorno), timeout=timeout)
    if r.status_code == 404:
        return None
    r.raise_for_status()
    dati = r.content

    if verifica:
        c = get(url_zip(symbol, giorno) + ".CHECKSUM", timeout=timeout)
        if c.status_code == 200:
            atteso = (c.text.split() or [""])[0].strip()
            if atteso and atteso != _sha256(dati):
                raise RuntimeError(
                    f"checksum diverso per {symbol} {giorno}: scaricato "
                    f"{_sha256(dati)[:12]}…, atteso {atteso[:12]}…")

    with open(locale, "wb") as f:
        f.write(dati)
    return dati


def apri_zip(dati: bytes) -> str:
    """Il CSV dentro lo zip. Un solo file per archivio, ma non si assume: si
    prende quello che finisce in .csv."""
    with zipfile.ZipFile(io.BytesIO(dati)) as z:
        nomi = [n for n in z.namelist() if n.lower().endswith(".csv")]
        if not nomi:
            raise FormatoInatteso(f"nessun csv nello zip: {z.namelist()}")
        return z.read(nomi[0]).decode("utf-8", "replace")


def carica(symbol: str, dal: date, al: date, cache_dir: str = CACHE_DIR,
           verifica: bool = True,
           sessione: requests.Session | None = None) -> list[dict]:
    """Tutte le righe della finestra, ordinate, senza duplicati e senza buchi
    finti: i giorni assenti semplicemente non compaiono."""
    fuori: list[dict] = []
    for g in giorni(dal, al):
        dati = scarica_giorno(symbol, g, cache_dir, verifica=verifica,
                              sessione=sessione)
        if dati is None:
            continue
        fuori.extend(leggi_csv(apri_zip(dati)))
    fuori.sort(key=lambda d: d["ts"])
    return fuori
