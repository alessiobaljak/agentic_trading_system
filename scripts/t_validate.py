"""IL VOTO t DI TUTTE LE VALIDATE, UNA TANTUM (30 set 2026, H1-misura, si' del proprietario).

Il voto t dice quanto il guadagno medio di una strategia e' grande rispetto a
quanto oscilla da un trade all'altro (`backtesting.engine.t_stat`). Il gate lo
scrive nel registro (`last_t`) solo quando una coppia RIPASSA, e le declassate
non ripassano: il 30 set la t c'era per 42 validate su 202, esattamente le non
declassate (ops 0363). Senza questa passata la divisione «t alta / t bassa» del
FUORI CAMPIONE sarebbe «attive contro declassate» con un altro nome.

Per quali coppie: le validate generate, e le coppie USCITE dal registro che il
`portafoglio` rigioca e il cui record c'e' ancora (sostituite, non piu' viste:
`pb.coppie_uscite`, senza letture in piu'). Le uscite di tipo «rimossa» hanno
il record cancellato e qui non si votano (dal 16 set sono 0, ops 0373): il
report le conta a parte nella riga «senza t». Ogni coppia si vota con la
configurazione d'uscita che OPERA OGGI (`last_params` sopra la spec, come il
motore del `portafoglio`), e la voce lo registra (`uscita`).

Cosa calcola, TUTTO SUI DATI DEL GIORNO DELLA VALIDAZIONE: le candele si
tagliano alla mezzanotte UTC del giorno di `validated_at` (dove finivano i dati
del giro che l'ha validata; per le validate senza data il 25 set, come il
report), e sui dati tagliati si calcolano
  * la t del WALK-FORWARD (le 3 finestre fuori campione del gate, sul corpo
    senza holdout) e il numero di trade;
  * la t dell'HOLDOUT (l'ultimo esame, 45 giorni) e il numero di trade.
Sono le finestre che il gate aveva quel giorno. 30 set 2026, revisione del
lavoro B: prima il walk-forward girava sui dati di OGGI, e la sua ultima
finestra conteneva i giorni dell'holdout passati dalla validazione (fino a 44):
gli stessi trade entravano in tutte e due le t, e la t cambiava col giorno in
cui girava la passata. Senza il taglio, poi, l'holdout di oggi conterrebbe
proprio i giorni fuori campione che il report misura. Una t su meno di 2 trade
(walk-forward) o meno di GATE_HOLDOUT_MIN_TRADES (holdout) si scrive vuota: non
e' una misura (`t_stat` da' 0.0 sotto 2 trade, e con 2-4 trade una t enorme).

DOVE SCRIVE: SOLO il file locale `data/voto_t/validate.json` sulla VPS
(`portafoglio_backtest.FILE_VOTI_T`), che la sezione FUORI CAMPIONE legge senza
nessuna lettura Firestore. NON scrive il registro, e la scelta e' voluta: il
registro e' un solo campo stringa che la discovery riscrive PER INTERO a ogni
giro, senza lock e senza transazioni (`finalizza_registro` -> `set_doc`). Una
passata di 15 minuti che lo rilegge e riscrive puo' cancellare in silenzio le
conferme guadagnate nel frattempo; anche rileggendolo un attimo prima di
scrivere resta una finestra, e un errore li' costa settimane di attesa. Col
file il rischio e' zero: pass_count, verdetti, declassate e last_params non si
possono toccare perche' il documento non viene nemmeno scritto. Per le coppie
promosse d'ora in poi la t della promozione resta comunque nel registro, fissata
(`val_t` & C., `optimize.fissa_voto_t`, 30 set 2026): il report la usa quando
la coppia non e' nel file.

IL FILE SI AGGIORNA DOPO OGNI COIN (30 set 2026, revisione del lavoro B): prima
si scriveva solo alla fine, e un errore fuori dai controlli per coppia o un
worker ucciso dal kernel buttavano tutta la passata. Ora un errore di una coin
e' una riga «errore» per le sue coppie, e un worker ucciso lascia nel file le
coin gia' finite (la passata esce con 1 e lo dice).

CONCORRENZA: un lucchetto del kernel (`fcntl.flock` su
`data/voto_t/in_corso.lock`, tenuto aperto per tutta la passata) impedisce due
passate insieme; il kernel lo toglie quando il processo muore, quindi non
restano lucchetti orfani. 30 set 2026, revisione del lavoro B: prima era un
file creato in esclusiva col pid scritto dopo, e due avvii nello stesso istante
potevano girare insieme. Con `--su-file` il lucchetto si prende PRIMA di
toccare referto e pid: un secondo avvio non svuota il referto di chi gira. Il
file dei voti si riscrive in modo atomico (temporaneo + `os.replace`),
rileggendolo sotto il lucchetto subito prima: il report non legge mai un file a
meta'. Le voci gia' presenti non si ricalcolano, salvo `--rifai`, o se la
coppia opera oggi un'altra configurazione d'uscita, o se e' stata validata di
nuovo in un altro giorno (`pb.voce_scaduta`): in quei casi si rifanno da sole.

IL GIRO DEL GATE, per la MEMORIA e non per il registro (il 24 set quattro giri
sono morti per OOM con UN gruppo da 8 worker da ~2,3 GB l'uno su 15 GB,
docs/andremo_live.md; due gruppi insieme fanno lo stesso conto):
  * non parte se il giro e' in corso (processi in /proc o unita'
    `trading-optimizer.service` attiva) o se il prossimo avvio del timer e' a
    meno di MARGINE_PARTENZA_S (40 minuti); in sfondo (`--budget 0`) aspetta,
    al massimo 4 ore; nel canale ops esce subito e lo dice;
  * prima di ogni coin ricontrolla: se il giro e' partito o manca meno di
    MARGINE_FERMATA_S (10 minuti), le coin rimaste diventano righe «giro» e i
    worker si liberano. Le coppie gia' votate restano nel file: si rilancia.
30 set 2026, revisione del lavoro B: prima si guardava solo alla partenza, e
un giro partito a passata avviata contava la RAM con i worker della passata
ancora in memoria (1 worker, cioe' un giro ~6 volte piu' lento, oppure OOM).

COSTO: 2 letture Firestore (registro e spec), 0 scritture, nessun riavvio.
Tempo STIMATO, non misurato: 15-20 minuti per ~200 coppie su ~70 coin con 6
worker prima della revisione del 30 set (costo fisso per coin ~85 s: candele,
indicatori, snapshot; stima dell'autopsia del 26 set, 15-17 minuti per 62 coin).
Ora le 3 finestre del walk-forward si ricalcolano per ogni giorno di validazione
diverso della coin, non una volta per coin: di piu', da misurare con `--limit`.
Supera i 900 s del canale ops: sulla VPS si lancia in sfondo con `systemd-run`
(voce `voto-t-completo` in ops/allowlist.example, priorita' bassa come il gate)
e il referto si legge con `voto-t-esito`.

Uso (sulla VPS):
    .venv/bin/python -m scripts.t_validate --limit 10          # prova rapida
    .venv/bin/python -m scripts.t_validate --su-file --budget 0  # (da systemd-run)
    .venv/bin/python -m scripts.t_validate --esito
Senza Firebase (test, locale) stampa «nessuna validata» ed esce con 0.
"""
from __future__ import annotations

import argparse
import datetime as dt
import fcntl
import json
import multiprocessing
import os
import re
import subprocess
import sys
import time
from collections import Counter
from concurrent.futures import ProcessPoolExecutor, as_completed
from concurrent.futures.process import BrokenProcessPool
from datetime import date

from backtesting.data_loader import load_candles
from backtesting.engine import t_stat
from backtesting.parallel import n_workers
from backtesting.quality import looks_delisted
from bot.config import settings, timeframe_hours
from bot.core.firebase_client import decode_pairs, get_firebase
from bot.core.indicators import compute_indicator_frame
from bot.core.registry import coppie_validate
from bot.strategies.generated import MARKET_FEATURES, GeneratedStrategy
from scripts import discover_strategies as d
from scripts import portafoglio_backtest as pb
from scripts.autopsia_validate import config_operata, config_str
from scripts.optimize import impronta_uscita

#: la cartella dei file di questa passata, sulla VPS (ignorata da git)
DIR_VOTI = os.path.dirname(pb.FILE_VOTI_T)
#: dove `--su-file` scrive tutto cio' che avrebbe stampato, e il pid
FILE_ESITO = os.path.join(DIR_VOTI, "ultimo.txt")
FILE_PID = os.path.join(DIR_VOTI, "ultimo.pid")
#: il lucchetto: il file resta, il lucchetto del kernel (flock) vale solo
#: mentre una passata lo tiene aperto
FILE_LOCK = os.path.join(DIR_VOTI, "in_corso.lock")
#: deadline propria nel canale ops (sotto i 900 s); da systemd-run `--budget 0`
BUDGET_S = float(os.getenv("VOTO_T_BUDGET_S", "720"))
#: gli stessi worker della discovery sulla VPS (`n_workers` li riduce se la RAM
#: non basta: e' il tetto che ha salvato i giri del 24 set dall'OOM)
WORKERS = int(os.getenv("VOTO_T_WORKERS", "6"))
#: versione del formato del file (2: niente `wf_troncato`, c'e' `uscita`)
VERSIONE = 2
#: i moduli del giro del gate: mentre girano, questa passata aspetta
MODULI_GIRO = ("scripts.discover_strategies", "scripts.optimize")
#: l'unita' e il timer del gate (scripts/install_optimizer_timer.sh): ogni 3 ore,
#: con fino a 10 minuti di ritardo casuale
SERVIZIO_GATE = "trading-optimizer.service"
TIMER_GATE = "trading-optimizer.timer"
#: non si parte se il prossimo giro del gate e' piu' vicino di cosi': la durata
#: STIMATA della passata (15-20 minuti prima del 30 set, ora di piu') piu' i 10
#: minuti di ritardo casuale del timer. Non e' tarato: se la passata dura di
#: piu', la fermata qui sotto la chiude prima del giro
MARGINE_PARTENZA_S = 40 * 60.0
#: prima di ogni coin: se il prossimo giro e' piu' vicino di cosi', la passata
#: si ferma. Una coin costa ~85 s (stima): cosi' i worker sono liberi prima che
#: il giro conti la RAM (lo fa ~1 minuto dopo l'avvio, ops 0365)
MARGINE_FERMATA_S = 10 * 60.0
#: quanto aspettare al massimo la fine di un giro (piu' del giro piu' lungo
#: visto nei log ops, 2h49 il 28 set), e ogni quanto guardare
ATTESA_MAX_S = 4 * 3600.0
ATTESA_PASSO_S = 60.0

#: stato per-worker di QUESTO script (deadline), accanto a `d._W`
_S: dict = {}
#: i lucchetti tenuti da questo processo: percorso -> descrittore aperto
_LUCCHETTI: dict = {}


def di(msg: str = "") -> None:
    """Stampa SUBITO: un processo ucciso dal timeout del canale ops non lascia
    una riga se stdout accumula a blocchi."""
    print(msg, flush=True)


# --------------------------------------------------------------------------- #
# Funzioni pure                                                                #
# --------------------------------------------------------------------------- #
def taglio_validazione(rec: dict | None) -> tuple[float | None, str]:
    """(istante del taglio, origine): la mezzanotte UTC del giorno in cui la
    coppia e' diventata validata. Una sola copia della regola, nel report
    (`pb.taglio_validazione`): la passata e il report devono dire la stessa
    cosa, perche' il report controlla che la voce sia di questa validazione."""
    return pb.taglio_validazione(rec)


def crea_operata(spec: dict, last_params: dict | None):
    """La strategia come la rigioca il motore del `portafoglio`: la spec con
    sopra i `last_params` del registro (scala, break-even, keep). Una NUOVA a
    ogni chiamata: il walk-forward ne vuole una per finestra."""
    lp = dict(last_params) if isinstance(last_params, dict) else {}

    def crea():
        g = GeneratedStrategy(spec)
        g.params = {**(getattr(g, "params", {}) or {}), **lp}
        return g
    return crea


def coppie_da_votare(pairs: dict, specs: dict, interval: str, gia_fatte=(),
                     rifai: bool = False, limit: int = 0, now=None, uscite=(),
                     rifatte: Counter | None = None) -> tuple[list, dict]:
    """[(coin, [(chiave, spec, last_params, taglio), ...])] per le validate (e
    le `uscite` rigiocabili col record ancora nel registro) che qui si possono
    votare, e i conteggi di quelle che no: `base` (il report non le rigioca),
    `senza_spec`, `altro_timeframe`, `azzerata_senza_data`, `gia_nel_file`
    (senza `--rifai`). Una voce del file che non vale piu' (altra
    configurazione d'uscita, altra validazione: `pb.voce_scaduta`) NON conta
    come gia' fatta: si rivota, e `rifatte` conta perche'. Le coin con piu'
    coppie prima: se il tempo finisce, si e' fatto il massimo per coin caricata."""
    tf_bot = settings.ORCHESTRATOR_TIMEFRAME
    saltate: Counter = Counter()
    per_coin: dict[str, list] = {}
    gia = (gia_fatte if isinstance(gia_fatte, dict)
           else {k: {} for k in (gia_fatte or ())})
    chiavi = list(coppie_validate(pairs, now))
    viste = set(chiavi)
    chiavi += [k for k in (uscite or ()) if k not in viste and isinstance(pairs.get(k), dict)]
    for key in chiavi:
        rec = pairs.get(key) or {}
        sym, sid = key.split("|", 1)
        if key in gia and not rifai:
            voce = gia.get(key)
            motivo = pb.voce_scaduta(voce, rec) if isinstance(voce, dict) else None
            if not motivo:
                saltate["gia_nel_file"] += 1
                continue
            if rifatte is not None:
                rifatte[motivo] += 1
        if not sid.startswith("gen_"):
            saltate["base"] += 1          # come il `portafoglio`: le base non si rigiocano
            continue
        spec = specs.get(sid) if isinstance(specs, dict) else None
        if not isinstance(spec, dict):
            saltate["senza_spec"] += 1
            continue
        if (spec.get("timeframe") or tf_bot) != interval:
            saltate["altro_timeframe"] += 1
            continue
        taglio, origine = taglio_validazione(rec)
        if taglio is None:
            saltate[origine] += 1
            continue
        per_coin.setdefault(sym, []).append((key, spec, rec.get("last_params") or {}, taglio))
    ordine = sorted(per_coin, key=lambda s: (-len(per_coin[s]), s))
    piatte = [(s, c) for s in ordine for c in per_coin[s]]
    if limit and limit > 0:
        piatte = piatte[:limit]
    out: list = []
    for s, c in piatte:
        if out and out[-1][0] == s:
            out[-1][1].append(c)
        else:
            out.append((s, [c]))
    return out, dict(saltate)


def voce_file(riga: dict) -> dict:
    """La voce del file per una coppia votata: solo numeri, date e due
    stringhe corte (la configurazione leggibile e la sua impronta)."""
    return {"t": riga.get("t"), "n": riga.get("n"),
            "t_holdout": riga.get("t_holdout"), "n_holdout": riga.get("n_holdout"),
            "dati_fino_a": riga.get("dati_fino_a"), "config": riga.get("config"),
            "uscita": riga.get("uscita"), "calcolata_at": riga.get("calcolata_at")}


def unisci_voti(esistenti: dict | None, righe: list[dict], rifai: bool = False) -> tuple[dict, int]:
    """Le voci del file dopo questa passata, e quante sono nuove o rifatte.
    Si aggiungono SOLO le coppie votate davvero (stato «ok»). Una voce gia'
    presente resta com'era, salvo `rifai` o una riga nuova calcolata con
    un'altra configurazione d'uscita o su un altro giorno di validazione (la
    passata l'ha rivotata perche' la vecchia non valeva piu'). Nessuna voce si
    cancella: una coppia uscita dal registro resta nel file, e il report la usa
    quando rigioca le uscite (sopravvivenza)."""
    out = {k: v for k, v in (esistenti or {}).items() if isinstance(v, dict)}
    nuove = 0
    for r in righe:
        if r.get("stato") != "ok":
            continue
        vecchia = out.get(r["key"])
        if vecchia is not None and not rifai:
            if (vecchia.get("uscita") == r.get("uscita")
                    and vecchia.get("dati_fino_a") == r.get("dati_fino_a")):
                continue
        voce = voce_file(r)
        if vecchia == voce:
            continue
        out[r["key"]] = voce
        nuove += 1
    return out, nuove


def scrivi_atomico(path: str, doc: dict) -> None:
    """Scrive il file in modo atomico: un temporaneo accanto e `os.replace`.
    Chi legge nello stesso istante (il `portafoglio`) vede il file vecchio o
    quello nuovo, mai uno a meta'."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = f"{path}.{os.getpid()}.tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(doc, f, ensure_ascii=False, sort_keys=True)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)


def _processo_vivo(pid: int) -> bool:
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True


def prendi_lucchetto(path: str = FILE_LOCK) -> int | None:
    """Prende il lucchetto del kernel (`fcntl.flock`, esclusivo, senza
    aspettare) sul file `path`, tenuto aperto finche' non si chiama
    `lascia_lucchetto` o il processo muore: in quel caso lo toglie il kernel,
    quindi non esistono lucchetti vecchi da riconoscere. Se un altro processo
    (o un'altra apertura di questo) lo tiene -> None. Ritorna il nostro pid,
    che si scrive anche nel file (solo per chi guarda a mano).

    30 set 2026, revisione del lavoro B: prima era un file creato con O_EXCL e
    il pid scritto DOPO; chi lo leggeva vuoto nel mezzo lo cancellava e se ne
    creava un altro, e le due passate giravano insieme (12 worker)."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    fd = os.open(path, os.O_RDWR | os.O_CREAT, 0o644)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError:
        os.close(fd)
        return None
    try:
        os.ftruncate(fd, 0)
        os.write(fd, str(os.getpid()).encode())
    except OSError:
        pass
    _LUCCHETTI[path] = fd
    return os.getpid()


def lascia_lucchetto(path: str = FILE_LOCK) -> None:
    """Toglie il lucchetto SOLO se lo tiene questo processo. Il file resta: se
    lo si cancellasse, chi lo apre dopo avrebbe un file diverso e due passate
    potrebbero tenere «il» lucchetto insieme."""
    fd = _LUCCHETTI.pop(path, None)
    if fd is None:
        return
    try:
        fcntl.flock(fd, fcntl.LOCK_UN)
    finally:
        os.close(fd)


def giro_in_corso(proc: str = "/proc") -> list[int]:
    """I pid dei processi del giro del gate (discovery o optimize) in corso.
    NON per il registro (questa passata non lo scrive): per la MEMORIA (vedi il
    docstring del modulo: il 24 set gli OOM li ha fatti un solo gruppo da 8
    worker, e due gruppi insieme fanno lo stesso conto). Fail-open: senza /proc
    leggibile ritorna []."""
    trovati: list[int] = []
    try:
        voci = os.listdir(proc)
    except OSError:
        return []
    for voce in voci:
        if not voce.isdigit() or int(voce) == os.getpid():
            continue
        try:
            with open(os.path.join(proc, voce, "cmdline"), "rb") as f:
                cmd = f.read().replace(b"\0", b" ").decode("utf-8", "replace")
        except OSError:
            continue
        if any(m in cmd for m in MODULI_GIRO):
            trovati.append(int(voce))
    return sorted(trovati)


def _systemctl(*argomenti: str) -> str | None:
    """L'uscita di `systemctl ...`, o None se systemctl non c'e' o non risponde."""
    try:
        r = subprocess.run(["systemctl", *argomenti], capture_output=True, text=True,
                           timeout=10, check=False)
    except (OSError, subprocess.SubprocessError):
        return None
    return r.stdout or ""


def servizio_gate_attivo() -> bool:
    """True se l'unita' del gate e' attiva o in avvio (`systemctl is-active`).
    Un oneshot resta «activating» per tutto il giro, anche nell'istante fra i
    suoi due ExecStart, che /proc non vede. Fail-open: senza systemd False."""
    out = _systemctl("is-active", SERVIZIO_GATE)
    return (out or "").strip() in ("active", "activating", "reloading", "deactivating")


def istante_systemd(testo: str | None) -> float | None:
    """Un istante scritto da systemctl: «Wed 2026-09-30 15:00:00 UTC» (ora
    locale della macchina se il fuso non e' UTC), «@1759244400» o un numero di
    microsecondi. None se vuoto o illeggibile."""
    s = (testo or "").strip()
    if not s or s in ("n/a", "0"):
        return None
    if s.startswith("@"):
        try:
            return float(s[1:])
        except ValueError:
            return None
    if s.isdigit():
        return int(s) / 1e6
    m = re.search(r"(\d{4}-\d{2}-\d{2}) (\d{2}:\d{2}:\d{2})(?:\s+(\S+))?", s)
    if not m:
        return None
    try:
        quando = dt.datetime.strptime(f"{m.group(1)} {m.group(2)}", "%Y-%m-%d %H:%M:%S")
    except ValueError:
        # ha la forma di una data ma non lo e' (riverifica del 30 set 2026):
        # illeggibile, quindi None come promesso, mai un'eccezione
        return None
    if (m.group(3) or "").upper() in ("UTC", "GMT", "Z"):
        return quando.replace(tzinfo=dt.timezone.utc).timestamp()
    return quando.timestamp()


def secondi_al_prossimo_giro(ora: float | None = None) -> float | None:
    """Fra quanti secondi il timer del gate avvia il prossimo giro (negativo se
    l'ora e' passata e il giro sta partendo). None se non si sa (niente systemd,
    timer assente): fail-open, resta il controllo prima di ogni coin."""
    quando = istante_systemd(_systemctl("show", TIMER_GATE, "-p", "NextElapseUSecRealtime",
                                        "--value"))
    if quando is None:
        return None
    return quando - (time.time() if ora is None else ora)


def gate_in_arrivo(margine_s: float) -> str | None:
    """None se il gate non gira e il suo prossimo giro e' a piu' di
    `margine_s`; altrimenti perche' no, in una frase."""
    pids = giro_in_corso()
    if pids:
        return f"il giro del gate e' in corso (pid {', '.join(map(str, pids))})"
    if servizio_gate_attivo():
        return f"il giro del gate e' in corso ({SERVIZIO_GATE} attivo)"
    s = secondi_al_prossimo_giro()
    if s is not None and s < margine_s:
        return f"il prossimo giro del gate parte fra {max(0.0, s) / 60:.0f} minuti"
    return None


def aspetta_il_giro(budget: float) -> bool:
    """True quando si puo' partire: nessun giro del gate in corso e il prossimo
    a piu' di MARGINE_PARTENZA_S. Altrimenti: nel canale ops (budget > 0) non si
    aspetta, si esce e lo si dice; in sfondo (budget 0, `voto-t-completo`) si
    aspetta, al massimo ATTESA_MAX_S."""
    t0 = time.time()
    detto = False
    while True:
        motivo = gate_in_arrivo(MARGINE_PARTENZA_S)
        if not motivo:
            return True
        if budget > 0:
            di(f"[voto-t] {motivo}: la passata non parte ora, per non tenere in memoria due "
               f"gruppi di worker. Rilancia a giro finito (e ad almeno "
               f"{MARGINE_PARTENZA_S / 60:.0f} minuti dal successivo), o usa `voto-t-completo` "
               f"che aspetta da solo.")
            return False
        if time.time() - t0 > ATTESA_MAX_S:
            di(f"[voto-t] {motivo}, e aspetto da {ATTESA_MAX_S / 3600:.0f} ore: "
               f"esco senza aver votato niente.")
            return False
        if not detto:
            di(f"[voto-t] {motivo}: aspetto che finisca il giro, poi parto.")
            detto = True
        time.sleep(ATTESA_PASSO_S)


# --------------------------------------------------------------------------- #
# Il calcolo (una coppia)                                                      #
# --------------------------------------------------------------------------- #
def voto_walk_forward(opt, sym: str, candles, frame, crea, nome: str, ctx=None) -> dict:
    """t e trade del walk-forward, sulle STESSE finestre del gate
    (`d.trade_oos_finestre`, corpo senza holdout). t vuota sotto 2 trade."""
    body, _cut = opt.split_holdout(candles)
    st, _ = d.trade_oos_finestre(opt, sym, body, frame, crea, nome, context_by_ts=ctx)
    n = len(st.trades)
    return {"t": round(t_stat(st.trades), 3) if n >= pb.MIN_TRADE_T else None, "n": n}


def voto_holdout(opt, sym: str, candles, frame, crea, ctx=None) -> dict:
    """t e trade dell'holdout (`_holdout_check`, lo stesso dell'ultimo esame
    del gate): gli ultimi GATE_HOLDOUT_DAYS dei dati ricevuti. t vuota sotto il
    minimo di trade del gate (GATE_HOLDOUT_MIN_TRADES): con 0-1 trade `t_stat`
    da' 0.0, con 2-4 numeri enormi, e il gate non l'avrebbe promossa."""
    _body, cut = opt.split_holdout(candles)
    h = opt._holdout_check(crea(), sym, candles, frame, cut, context_by_ts=ctx) or {}
    n = int(h.get("trades") or 0)
    if h.get("t") is None or n < int(settings.GATE_HOLDOUT_MIN_TRADES):
        return {"t_holdout": None, "n_holdout": n}
    return {"t_holdout": round(float(h["t"]), 3), "n_holdout": n}


def _init(args, end: str, deadline: float) -> None:
    """Lo STESSO initializer dei worker della discovery (`_disc_init`: optimizer
    con le finestre del gate, contesto BTC), piu' la deadline di questo script."""
    d._disc_init(args, end, [])
    _S.update(deadline=float(deadline or 0.0))


def _scaduto() -> bool:
    dl = float(_S.get("deadline") or 0.0)
    return bool(dl) and time.time() > dl


def _contesto(W: dict, spec: dict):
    """Il contesto di mercato SOLO alle spec che lo usano, come in `_disc_one`."""
    usa = any((f.get("kind") in MARKET_FEATURES)
              for f in (spec.get("features") or []) if isinstance(f, dict))
    return W.get("btc_ctx") if usa else None


def _riga(key: str, stato: str, **extra) -> dict:
    r = {"key": key, "stato": stato}
    r.update(extra)
    return r


def _iso(ts: float) -> str:
    return dt.datetime.fromtimestamp(float(ts), dt.timezone.utc).date().isoformat()


def vota_coin(W: dict, sym: str, lista: list, candles) -> list[dict]:
    """Tutte le coppie di UNA coin, raggruppate per giorno di validazione: per
    ogni giorno le candele si tagliano a quel giorno, e sui dati tagliati si
    calcolano walk-forward e holdout (un taglio, una serie di snapshot; la
    cache si svuota fra un taglio e l'altro). Fail-open per coppia."""
    opt = W["opt"]
    frame = compute_indicator_frame(candles)
    adesso = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
    righe: dict[str, dict] = {}
    per_taglio: dict[float, list] = {}
    for key, spec, lp, taglio in lista:
        righe[key] = _riga(key, "ok", config=config_str(config_operata(lp)),
                           uscita=impronta_uscita(lp), calcolata_at=adesso,
                           dati_fino_a=_iso(taglio))
        per_taglio.setdefault(taglio, []).append((key, spec, lp))
    for taglio in sorted(per_taglio):
        k = d._taglio_a(candles, taglio - 1.0)
        if k < W["min_history"]:
            for key, _s, _lp in per_taglio[taglio]:
                righe[key] = _riga(key, "storia", errore=f"{k} candele al taglio {_iso(taglio)}")
            continue
        cand_v = candles[:k]
        frame_v = frame.iloc[:k].reset_index(drop=True)
        for key, spec, lp in per_taglio[taglio]:
            if _scaduto():
                righe[key] = _riga(key, "tempo")
                continue
            crea, ctx = crea_operata(spec, lp), _contesto(W, spec)
            try:
                righe[key].update(voto_walk_forward(opt, sym, cand_v, frame_v, crea,
                                                    spec["id"], ctx=ctx))
                righe[key].update(voto_holdout(opt, sym, cand_v, frame_v, crea, ctx=ctx))
            except Exception as exc:  # noqa: BLE001
                righe[key] = _riga(key, "errore", errore=f"t: {str(exc)[:80]}")
        d.svuota_cache_motore(opt)
    return [righe[key] for key, _s, _lp, _t in lista]


def _una_coin(item) -> list[dict]:
    """Il lavoro di un worker: prima si guarda il gate, poi candele e controlli
    come l'autopsia, poi `vota_coin`. Un errore e' una riga per ogni coppia
    della coin, non la fine della passata (30 set 2026: prima un'eccezione
    fuori dai controlli per coppia buttava tutte le coin gia' votate)."""
    sym, lista = item
    W = d._W
    args, end = W["args"], W["end"]
    if _scaduto():
        return [_riga(k, "tempo") for k, _s, _lp, _t in lista]
    ferma = gate_in_arrivo(MARGINE_FERMATA_S)
    if ferma:
        return [_riga(k, "giro", errore=ferma) for k, _s, _lp, _t in lista]
    t_coin = time.time()
    try:
        candles = load_candles(sym, args.interval, args.start, end, prefer=args.source)
    except Exception as exc:  # noqa: BLE001
        di(f"[voto-t] {sym}: candele non disponibili ({str(exc)[:80]})")
        return [_riga(k, "errore", errore=f"candele: {str(exc)[:80]}") for k, _s, _lp, _t in lista]
    try:
        if len(candles) < W["min_history"]:
            return [_riga(k, "storia", errore=f"{len(candles)} candele su {W['min_history']}")
                    for k, _s, _lp, _t in lista]
        if looks_delisted(candles, end, timeframe_hours(args.interval)):
            return [_riga(k, "delistata", errore=f"serie ferma al {candles[-1].open_time:%Y-%m-%d}")
                    for k, _s, _lp, _t in lista]
        righe = vota_coin(W, sym, lista, candles)
    except Exception as exc:  # noqa: BLE001
        di(f"[voto-t] {sym}: errore ({str(exc)[:80]})")
        return [_riga(k, "errore", errore=f"coin: {str(exc)[:80]}") for k, _s, _lp, _t in lista]
    di(f"[voto-t] {sym}: {len(lista)} coppie in {time.time() - t_coin:.0f}s")
    return righe


def esegui_e_salva(lavoro: list, workers: int, initargs: tuple, salva) -> tuple[list[dict], str | None]:
    """Vota coin per coin e chiama `salva(righe_finora)` dopo OGNI coin finita
    (nel processo padre, che tiene il lucchetto). Ritorna (righe, perche' la
    passata si e' interrotta o None).

    Al posto di `parallel_map`, che restituisce i risultati solo tutti insieme:
    un worker ucciso dal kernel (BrokenProcessPool) faceva perdere anche le
    coin gia' finite. Qui le coin finite sono gia' nel file; quelle del worker
    morto (e le altre non finite) diventano righe «interrotta»."""
    righe: list[dict] = []
    if workers <= 1 or len(lavoro) <= 1:
        _init(*initargs)
        for item in lavoro:
            try:
                righe.extend(_una_coin(item))
            except Exception as exc:  # noqa: BLE001
                righe.extend(_riga(k, "errore", errore=f"coin: {str(exc)[:80]}")
                             for k, *_ in item[1])
            salva(righe)
        return righe, None
    interrotta = None
    with ProcessPoolExecutor(max_workers=workers, initializer=_init, initargs=initargs) as ex:
        futuri = {ex.submit(_una_coin, item): item for item in lavoro}
        for f in as_completed(futuri):
            lista = futuri[f][1]
            try:
                righe.extend(f.result())
            except BrokenProcessPool as exc:
                interrotta = interrotta or f"un worker e' morto (memoria?): {str(exc)[:100]}"
                righe.extend(_riga(k, "interrotta") for k, *_ in lista)
                continue
            except Exception as exc:  # noqa: BLE001
                righe.extend(_riga(k, "errore", errore=f"worker: {str(exc)[:80]}")
                             for k, *_ in lista)
            salva(righe)
    return righe, interrotta


# --------------------------------------------------------------------------- #
# Stampa                                                                       #
# --------------------------------------------------------------------------- #
def _f(v, fmt: str = "{:.2f}") -> str:
    return "-" if v is None else fmt.format(v)


def riga_tabella(r: dict) -> str:
    key = r["key"][:38].ljust(38)
    if r.get("stato") != "ok":
        return f"{key} {str(r.get('stato', '?')).upper()} {r.get('errore', '')}".rstrip()
    return (f"{key} t {_f(r.get('t')):>6} ({r.get('n', 0):>4})  holdout {_f(r.get('t_holdout')):>6} "
            f"({r.get('n_holdout', 0):>3})  dati al {r.get('dati_fino_a')}")


def riassunto(righe: list[dict], saltate: dict, n_validate: int, voti: dict,
              nuove: int) -> list[str]:
    """Le righe finali (il canale ops tiene la coda dell'output lungo)."""
    stati = Counter(str(r.get("stato")) for r in righe)
    testa = (f"RIASSUNTO · {n_validate} validate · votate ora {stati.get('ok', 0)} · "
             + " · ".join(f"{k} {v}" for k, v in sorted(stati.items()) if k != "ok"))
    out = [testa.rstrip(" ·")]
    if saltate:
        out.append("  non votate: " + ", ".join(f"{k} {v}" for k, v in sorted(saltate.items())))
    ts = sorted(float(v["t"]) for v in voti.values() if v.get("t") is not None)
    th = [float(v["t_holdout"]) for v in voti.values() if v.get("t_holdout") is not None]
    if ts:
        out.append(f"  nel file {len(voti)} coppie ({nuove} nuove o rifatte ora): t walk-forward "
                   f">= 2 in {sum(1 for t in ts if t >= 2)} su {len(ts)}, mediana "
                   f"{ts[len(ts) // 2]:.2f}; t holdout >= 2 in {sum(1 for t in th if t >= 2)} su "
                   f"{len(th)} (con almeno {settings.GATE_HOLDOUT_MIN_TRADES} trade)")
    else:
        out.append(f"  nel file {len(voti)} coppie ({nuove} nuove o rifatte ora)")
    out.append(f"  scritto solo {pb.FILE_VOTI_T} (Firebase: 2 letture, 0 scritture). "
               f"Il registro, i passaggi, i verdetti e le declassate NON sono stati toccati.")
    return out


# --------------------------------------------------------------------------- #
# main                                                                         #
# --------------------------------------------------------------------------- #
def esito() -> int:
    """Il referto di `--su-file`, quando e' stato scritto e se gira ancora."""
    if not os.path.exists(FILE_ESITO):
        di(f"[voto-t] nessun referto in {FILE_ESITO}: lancia prima `voto-t-completo`.")
        return 0
    mtime = dt.datetime.fromtimestamp(os.path.getmtime(FILE_ESITO), dt.timezone.utc)
    pid, vivo = None, False
    try:
        with open(FILE_PID, encoding="utf-8") as f:
            pid = int(f.read().strip() or 0)
        vivo = _processo_vivo(pid) if pid else False
    except (OSError, ValueError):
        pid = None
    stato = "ANCORA IN CORSO (il referto e' parziale)" if vivo else "finito"
    di(f"[voto-t] referto scritto {mtime:%Y-%m-%d %H:%M:%S} UTC · "
       + (f"processo {pid} {stato}" if pid else "pid non registrato"))
    di("-" * 74)
    with open(FILE_ESITO, encoding="utf-8", errors="replace") as f:
        sys.stdout.write(f.read())
    sys.stdout.flush()
    return 0


def _gia_in_corso() -> None:
    di(f"[voto-t] un'altra passata e' gia' in corso ({FILE_LOCK}): non ne lancio "
       f"un'altra. Il referto si legge con `voto-t-esito`.")


def su_file(args) -> int:
    """Come `ingressi_report --su-file`: si lavora in primo piano, ma tutto
    cio' che si stampa va nel referto su file (lanciato da `systemd-run`, fuori
    dal gruppo dell'agente ops, che a 900 s ucciderebbe tutto).

    Il lucchetto si prende PRIMA di toccare referto e pid (30 set 2026,
    revisione del lavoro B): un secondo avvio mentre il primo gira esce senza
    svuotare il referto del primo e senza scrivere il suo pid (prima
    `voto-t-esito` diceva «finito» a passata ancora in corso). Il suo avviso va
    sull'uscita normale, cioe' nel journal dell'unita'."""
    os.makedirs(DIR_VOTI, exist_ok=True)
    if prendi_lucchetto(FILE_LOCK) is None:
        _gia_in_corso()
        return 0
    try:
        fd_out = os.open(FILE_ESITO, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o644)
        os.dup2(fd_out, 1)
        os.dup2(fd_out, 2)
        os.close(fd_out)
        with open(FILE_PID, "w", encoding="utf-8") as f:
            f.write(str(os.getpid()))
        di(f"[voto-t] su file, pid {os.getpid()}, avvio "
           f"{dt.datetime.now(dt.timezone.utc):%Y-%m-%d %H:%M:%S} UTC")
        try:
            return _sotto_lucchetto(args)
        except BaseException as exc:  # noqa: BLE001
            di(f"[voto-t] interrotto: {exc!r}")
            return 1
    finally:
        lascia_lucchetto(FILE_LOCK)


def passata(args) -> int:
    """Il lavoro vero, sotto il lucchetto."""
    if prendi_lucchetto(FILE_LOCK) is None:
        _gia_in_corso()
        return 0
    try:
        return _sotto_lucchetto(args)
    finally:
        lascia_lucchetto(FILE_LOCK)


def _sotto_lucchetto(args) -> int:
    """Con il lucchetto gia' preso: aspetta il giro del gate, poi la passata."""
    if not aspetta_il_giro(float(args.budget)):
        return 0
    return _passata(args)


def _uscite_da_votare(pairs: dict, validate) -> list[str]:
    """Le coppie uscite dal registro che il `portafoglio` rigioca e il cui
    record c'e' ancora (sostituite, non piu' viste): stessa funzione del
    report, senza diario e senza paper, cioe' senza letture in piu'. Le
    «rimosse» hanno il record cancellato e qui restano fuori."""
    try:
        pav = dt.datetime.combine(dt.date.fromisoformat(pb.PAPER_START), dt.time(),
                                  dt.timezone.utc).timestamp()
    except ValueError:
        pav = pb.VALIDATED_AT_DAL
    uscite = pb.coppie_uscite(pairs, None, validate, None, pav, time.time())
    return sorted(k for k, u in uscite.items()
                  if u.get("rigiocabile") and isinstance(pairs.get(k), dict))


def _passata(args) -> int:
    end = args.end or date.today().isoformat()
    t0 = time.time()
    fb = get_firebase()
    pairs = decode_pairs((fb.get_doc("strategy_registry", "validated") or {}).get("pairs"))
    validate = coppie_validate(pairs)
    if not validate:
        di("[voto-t] nessuna validata nel registro: niente da votare.")
        return 0
    specs = decode_pairs((fb.get_doc("discovered_strategies", "specs") or {}).get("specs"))
    uscite = _uscite_da_votare(pairs, validate)
    gia = pb.voti_t_da_file()
    rifatte: Counter = Counter()
    lavoro, saltate = coppie_da_votare(pairs, specs, args.interval, gia_fatte=gia,
                                       rifai=args.rifai, limit=args.limit, uscite=uscite,
                                       rifatte=rifatte)
    totale = sum(len(lst) for _s, lst in lavoro)
    di(f"[voto-t] {len(validate)} validate e {len(uscite)} uscite rigiocabili · {totale} da "
       f"votare su {len(lavoro)} coin a {args.interval} · dati {args.start}->{end}"
       + (" · non votate: " + ", ".join(f"{k} {v}" for k, v in sorted(saltate.items()))
          if saltate else "")
       + (" · rifatte perche' la voce non valeva piu': "
          + ", ".join(f"{k} {v}" for k, v in sorted(rifatte.items())) if rifatte else ""))
    righe: list[dict] = []
    interrotta = None
    if lavoro:
        workers = max(1, min(int(args.workers), n_workers()))
        deadline = (t0 + float(args.budget)) if args.budget > 0 else 0.0
        di(f"[voto-t] {workers} worker · deadline "
           f"{'nessuna' if not deadline else f'{args.budget:.0f}s'} · il file si aggiorna "
           f"dopo ogni coin")

        def salva(righe_finora: list[dict]) -> None:
            # si rilegge il file SOTTO il lucchetto subito prima di scrivere:
            # nessuna voce scritta nel frattempo va persa
            voti_ora, n = unisci_voti(pb.voti_t_da_file(), righe_finora, rifai=args.rifai)
            if n:
                scrivi_atomico(pb.FILE_VOTI_T, {
                    "versione": VERSIONE, "aggiornato_at": dt.datetime.now(dt.timezone.utc)
                    .isoformat(timespec="seconds"), "interval": args.interval,
                    "coppie": voti_ora})

        righe, interrotta = esegui_e_salva(lavoro, workers, (args, end, deadline), salva)
        righe = sorted(righe, key=lambda r: (r.get("stato") != "ok", r["key"]))
    voti = pb.voti_t_da_file()
    _, nuove = unisci_voti(gia, righe, rifai=args.rifai)
    di()
    for r in righe:
        di(riga_tabella(r))
    di()
    for line in riassunto(righe, saltate, len(validate), voti, nuove):
        di(line)
    stati = Counter(str(r.get("stato")) for r in righe)
    if stati.get("tempo"):
        di(f"  {stati['tempo']} coppie NON votate per tempo: rilancia (le fatte restano nel file)")
    if stati.get("giro"):
        di(f"  {stati['giro']} coppie NON votate perche' il giro del gate stava per partire o "
           f"era partito: rilancia a giro finito (le fatte restano nel file)")
    if interrotta:
        di(f"  PASSATA INTERROTTA: {interrotta}. Le coin finite prima sono nel file; "
           f"{stati.get('interrotta', 0)} coppie da rifare: rilancia.")
    di(f"[voto-t] finito in {time.time() - t0:.0f}s")
    return 1 if interrotta else 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--limit", type=int, default=0, help="quante coppie al massimo (0 = tutte)")
    ap.add_argument("--workers", type=int, default=WORKERS)
    ap.add_argument("--budget", type=float, default=BUDGET_S,
                    help="secondi prima di fermarsi da soli (0 = mai)")
    ap.add_argument("--interval", default=settings.ORCHESTRATOR_TIMEFRAME)
    ap.add_argument("--start", default="2022-01-01")
    ap.add_argument("--end", default=None, help="fine dati (default: oggi)")
    ap.add_argument("--source", default="auto")
    ap.add_argument("--windows", type=int, default=3)
    ap.add_argument("--rifai", action="store_true",
                    help="ricalcola anche le coppie gia' nel file")
    ap.add_argument("--su-file", action="store_true",
                    help="referto in data/voto_t/ultimo.txt, in primo piano (per systemd-run)")
    ap.add_argument("--esito", action="store_true", help="stampa il referto di --su-file")
    args = ap.parse_args(argv)
    if args.esito:
        return esito()
    if args.su_file:
        if os.getenv("TRADING_BOT_TEST_MODE") or not get_firebase().is_live:
            di("[voto-t] --su-file: senza Firebase vivo non c'e' niente da votare (esco 0)")
            return 0
        return su_file(args)
    return passata(args)


if __name__ == "__main__":
    multiprocessing.freeze_support()
    raise SystemExit(main())
