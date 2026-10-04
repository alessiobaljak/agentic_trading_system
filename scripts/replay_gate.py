"""R1: IL GATE RIGIOCATO NEL PASSATO (1 ott 2026, si' del proprietario, «vai con R1»).

La domanda: il gate sceglie strategie con un vantaggio vero, o soprattutto
fortuna? Si rifa' il gate a date passate, con i soli dati fino a quella data, e
si guarda come sono andate DOPO le candidate che ha fatto passare e quelle che
ha bocciato. La regola della lettura e' scritta PRIMA dei numeri, in
docs/andremo_live.md (ultima sezione, «R1, il gate rigiocato nel passato»), ed
e' copiata in `REGOLA_R1`: qui si applica, non si cambia.

COSA FA, per ognuna delle 26 date (una ogni 14 giorni all'indietro; la piu'
recente e' l'ultima che lascia 14 giorni interi di dati dopo di se'):
  * genera le candidate NUOVE della data (`generate_specs` con un seme fisso per
    data, `seme_della_data`, e le gemelle tolte con `scarta_gemelle` come nel
    giro vero) e le giudica su ogni coin con il gate di produzione
    (`discover_strategies.evaluate_spec`: finestre walk-forward + holdout di 45
    giorni, soglie GATE_* di oggi), usando SOLO le candele prima della data. Le
    scale e i keep provati sono quelli fissi: niente proposte dal paper (il
    paper non e' un insieme di allenamento, e sarebbe comunque il futuro);
  * poi rigioca col motore OGNI candidata, con la configurazione d'uscita che
    il gate le ha scelto (scala, break-even, keep; le bocciate con quella
    globale, come le giudica il gate), e tiene i trade ENTRATI nei 14 giorni dopo
    la data, in R netto dei costi del motore (R = pnl_pct / stop_pct, la stessa
    di `portafoglio_backtest.fuori_campione` per i trade del motore);
  * nessuna AI, nessuna vita del registro (finestre, declassate, purga).

DATI: le candele si caricano FINO A OGGI con la stessa chiamata del gate
(`load_candles(coin, intervallo, inizio, oggi)`) e si tagliano IN MEMORIA
(`discover_strategies._taglio_a`, come `scripts/t_validate.py`). Mai una fine
nel passato a `load_candles`: con una fine passata il caricatore riscrive la
cache e `_drop_older` cancella quella di oggi del gate (data_loader.py). Gli
indicatori del gate si calcolano sulle candele GIA' tagliate, e il contesto di
mercato (BTC) del gate e' costruito sulle candele di BTC tagliate alla stessa
data: niente dopo la data arriva al gate.

DOVE SCRIVE: SOLO file locali in data/replay_gate/ (ignorata da git): il piano
(`piano.json`: date, monete, semi, impostazioni), un file per unita' di lavoro
(`unita/<data>/<coin>.json`, scritto una volta, in modo atomico, appena l'unita'
e' finita), il referto della lancio in sfondo e il pid. NESSUNA scrittura
Firebase (dal 2 ott una sola lettura del registro, per le monete operate: decisione
del proprietario), il registro non si tocca, nessun riavvio, DRY_RUN non
c'entra: il bot non vede niente di tutto questo.

MAI INSIEME AL GIRO DEL GATE (la memoria non basta, docs/andremo_live.md 24
set): lucchetto del kernel (flock) contro due lanci insieme; non parte se il
giro e' in corso o parte fra meno di 40 minuti (in sfondo aspetta, al massimo 4
ore); prima di OGNI unita' ricontrolla, e se il giro parte fra meno di 10
minuti le unita' rimaste non si fanno (si rifanno al lancio dopo). Le stesse
funzioni e gli stessi margini di `scripts/t_validate.py`; in piu' non parte
mentre gira la passata del voto t, che ha i suoi worker.

A PEZZI: ogni lancio lavora al massimo BUDGET_S secondi (2,5 ore: sta in una
pausa del gate) e riprende da dove si era fermato il precedente (le unita' gia'
nel file non si rifanno; un lancio ucciso perde solo le unita' in corso). Il
PRIMO lancio, finche' nessuna data e' completa, fa solo le prime PROVA_DATE
date: e' la «prova piccola» della regola, si guardano i numeri e poi si
rilancia per il resto.

COSTO, STIMATO e non misurato sulla VPS. Misurato il 1 ott in locale (un
core, candele SINTETICHE a 15m dal 2022, alla data piu' recente): una unita'
(una coin a una data) con 100 candidate ~150 s, cioe' ~33 s fissi (snapshot
delle finestre) + ~1,2 s a candidata; RSS del processo ~2,3 GB. Con 50
candidate ~95 s: 26 date x 120-150 coin con un anno di storia alla data, su 6
worker, ~13-17 ore. Con 100 candidate sarebbero ~22-28 ore: per questo il
default e' 50 (`CANDIDATE_PER_DATA`). Il referto stampa i tempi VERI per
unita', da cui `--esito` ricava il resto.

Uso (sulla VPS):
    .venv/bin/python -m scripts.replay_gate --su-file      # da systemd-run (`replay-gate`)
    .venv/bin/python -m scripts.replay_gate --esito        # avanzamento e lettura
In locale, in primo piano: `python -m scripts.replay_gate --limit 2`.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import math
import multiprocessing
import os
import sys
import time
from collections import Counter
from concurrent.futures import ProcessPoolExecutor, as_completed
from concurrent.futures.process import BrokenProcessPool
from datetime import date
from statistics import mean

from backtesting.data_loader import load_candles
from backtesting.engine import HORIZON_BARS
from backtesting.optimizer import WalkForwardOptimizer
from backtesting.parallel import n_workers
from bot.core import finestra_r1
from backtesting.quality import looks_delisted
from bot.config import settings, timeframe_hours
from bot.core.indicators import compute_indicator_frame
from bot.execution.exit_logic import ladder_multiples
from bot.strategies.generated import MARKET_FEATURES, MARKET_SYMBOL
from bot.strategies.generator import generate_specs
from scripts import discover_strategies as d
from scripts import portafoglio_backtest as pb
from scripts import t_validate as tv
from scripts.optimize import _min_history, top_symbols_by_volume
from scripts.t_validate import (crea_operata, lascia_lucchetto, prendi_lucchetto,
                                scrivi_atomico, secondi_al_prossimo_giro, servizio_gate_attivo)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
#: la cartella di questo lavoro, sulla VPS (ignorata da git)
DIR_R1 = os.path.join(ROOT, "data", "replay_gate")
FILE_PIANO = os.path.join(DIR_R1, "piano.json")
DIR_UNITA = os.path.join(DIR_R1, "unita")
FILE_ESITO = os.path.join(DIR_R1, "ultimo.txt")
FILE_PID = os.path.join(DIR_R1, "ultimo.pid")
FILE_LOCK = os.path.join(DIR_R1, "in_corso.lock")
#: «R1 e' attivo»: il gate salta il giro delle 12 UTC (bot/core/finestra_r1.py)
FILE_ATTIVO = finestra_r1.FILE_ATTIVO
VERSIONE = 1
#: 2 ott 2026, decisione del proprietario: R1 solo sulle monete che il bot opera
SOLO_MONETE_OPERATE = True

# R2 — LA TARATURA DI R1 (3 ott 2026, si' del proprietario, backlog R2): R1 ha
# passato 0 candidate su 16.000 in 2 date recenti (ops 0458). E' R1 troppo severo
# o le candidate a caso quasi non passano nemmeno nel gate vero? Le STESSE 50
# candidate di R1 alla data R2_DATA (seme della data) giudicate dal gate di
# produzione coi dati di OGGI sulle monete del piano, in una cartella a parte:
# niente registro, niente Firebase. REGOLA scritta prima dei numeri: con
# R2_SOGLIA_SEVERO (3) o piu' passate R1 e' piu' severo del gate -> R1 SI FERMA
# (file «attivo» tolto: il gate torna a 8 giri) finche' non e' corretto; con
# 0-1 passate lo 0 di R1 e' vero -> scatta il cambio di piano del 2 ott (lo
# decide il proprietario); con 2 non si decide. Gira UNA volta, all'inizio del
# primo lancio che la trova non fatta, prima delle unita' di R1.
R2_ATTIVO = True
R2_DATA = "2026-09-17"
R2_SOGLIA_SEVERO = 3
DIR_R2 = os.path.join(DIR_R1, "r2")
DIR_UNITA_R2 = os.path.join(DIR_R2, "unita")
FILE_R2_ESITO = os.path.join(DIR_R2, "esito.json")

#: la regola (docs/andremo_live.md, 1 ott 2026): 26 date, una ogni 14 giorni,
#: e i 14 giorni dopo ogni data
N_DATE = 26
PASSO_GIORNI = 14
DOPO_GIORNI = 14
#: almeno tanti trade delle passate nei 14 giorni dopo, altrimenti «non si sa»
MIN_TRADE_PASSATE = 80
#: «differenza + margine sotto 0,10R» -> il gate sceglie soprattutto fortuna
SOGLIA_FORTUNA_R = 0.10
REGOLA_R1 = (
    "a ogni data il gate (soglie di oggi, niente AI, niente vita del registro) giudica "
    "candidate nuove coi soli dati fino alla data; poi i trade del motore delle stesse "
    "candidate entrati nei 14 giorni dopo, in R netto, con l'uscita scelta dal gate. "
    "«Passate» (tutto il gate, holdout compreso) contro «bocciate»: R medio a trade e "
    "differenza passate - bocciate; margine = 2 errori standard, il piu' largo fra quello "
    "per data e quello trade per trade. Almeno 80 trade delle passate, altrimenti «non si "
    "sa». Differenza oltre il margine -> il gate ha un vantaggio vero (il problema e' il "
    "mercato o il bot). Differenza + margine sotto 0,10R -> il gate sceglie soprattutto "
    "fortuna (la prossima modifica va nel gate). Altrimenti -> non si sa")
LIMITI_R1 = ("monete di oggi (le sopravvissute), motore senza scivolamento, niente AI, "
             "funding medio della coin dagli ultimi ~11 mesi (anche dopo la data): alzano "
             "il livello di tutti, pesano poco sul confronto. Non e' il gate di produzione: "
             "la vita del registro non c'e'.")

#: QUANTE CANDIDATE PER DATA: 50, per stare intorno alle ~13 ore in tutto (STIMA
#: dal tempo misurato in locale, vedi il docstring: ~33 s fissi per unita' +
#: ~1,2 s a candidata; con 100 sarebbero ~22-28 ore). Bastano: nella misura il
#: ~2% delle candidate passava con ~10 trade nei 14 giorni dopo, cioe' migliaia
#: di trade delle passate su 26 date, contro gli 80 minimi della regola. Si
#: fissa nel piano al primo lancio.
CANDIDATE_PER_DATA = int(os.getenv("REPLAY_GATE_CANDIDATE", "50"))
#: le monete: le prime 200 per volume di OGGI, come il giro del gate (`--top
#: 200` in scripts/install_optimizer_timer.sh). Fissate nel piano al primo lancio
TOP = int(os.getenv("REPLAY_GATE_TOP", "200"))
#: il primo lancio (nessuna data completa) fa solo queste date: la prova piccola
PROVA_DATE = 2
#: secondi di lavoro per lancio (2,5 ore: sta in una pausa del gate)
BUDGET_S = float(os.getenv("REPLAY_GATE_BUDGET_S", str(2.5 * 3600)))
#: 4 e non 6 (revisione del 1 ott): misurati ~2,3 GB per processo in locale, contro i
#: 2,0 stimati da `n_workers`; con 6 sarebbero ~14 GB dei 15 della macchina, bot compreso
WORKERS = int(os.getenv("REPLAY_GATE_WORKERS", "4"))
#: un'unita' finita con un errore si riprova al lancio dopo, poi resta errore
TENTATIVI_MAX = 2
#: stati di un'unita' che non si rifanno
FINALI = ("ok", "storia", "delistata")
#: i margini sul giro del gate: gli stessi del voto t
MARGINE_PARTENZA_S = tv.MARGINE_PARTENZA_S
MARGINE_FERMATA_S = tv.MARGINE_FERMATA_S
#: 8 ore e non 4 (1 ott 2026): il controllo del mattino lancia R1 alle ~08:15
#: italiane e la finestra libera arriva solo dopo il giro delle 09 UTC
ATTESA_MAX_S = float(os.getenv("REPLAY_GATE_ATTESA_S", str(8 * 3600)))
ATTESA_PASSO_S = tv.ATTESA_PASSO_S
#: i processi pesanti: il giro del gate e la passata del voto t (ognuno coi suoi
#: worker: due gruppi insieme non stanno in memoria)
MODULI_PESANTI = tuple(tv.MODULI_GIRO) + ("scripts.t_validate",)

#: stato per-worker (optimizer, BTC, contesti, deadline)
_S: dict = {}


def di(msg: str = "") -> None:
    print(msg, flush=True)


# --------------------------------------------------------------------------- #
# Funzioni pure: date, semi, candidate, finestra dopo, lettura                 #
# --------------------------------------------------------------------------- #
def _ts(giorno: str) -> float:
    """La mezzanotte UTC di «AAAA-MM-GG»."""
    return dt.datetime.combine(date.fromisoformat(giorno), dt.time(),
                               dt.timezone.utc).timestamp()


def date_del_piano(oggi: date, n: int = N_DATE, passo: int = PASSO_GIORNI,
                   dopo: int = DOPO_GIORNI) -> list[str]:
    """Le date, dalla piu' recente: l'ultima che lascia `dopo` giorni interi di
    dati (i dati arrivano alla mezzanotte di oggi), poi una ogni `passo`."""
    ultima = oggi - dt.timedelta(days=dopo)
    return [(ultima - dt.timedelta(days=passo * k)).isoformat() for k in range(n)]


def seme_della_data(giorno: str) -> int:
    """Il seme delle candidate di una data: la data stessa (20250918). Fisso:
    un lancio ripreso il giorno dopo genera le stesse candidate."""
    return int(giorno.replace("-", ""))


def candidate_della_data(giorno: str, n: int) -> list[dict]:
    """Le candidate NUOVE della data: `generate_specs` col seme della data, poi
    le gemelle (stessa logica, id diverso) tolte come nel giro vero. Nessuna
    spec nota: alla data il registro di oggi non esisteva."""
    specs = generate_specs(int(n), seed=seme_della_data(giorno))
    specs, _ = d.scarta_gemelle(specs, {})
    return specs


def usa_mercato(spec: dict) -> bool:
    return any((f.get("kind") in MARKET_FEATURES)
               for f in (spec.get("features") or []) if isinstance(f, dict))


def uscita_scelta(r: dict) -> dict | None:
    """La configurazione d'uscita che il gate ha scelto (`evaluate_spec`), nei
    nomi che legge il motore; None = quella globale (le bocciate, o il gate
    senza scale)."""
    if not r.get("scale_r_mults"):
        return None
    return {"scale_r_mults": [float(x) for x in r["scale_r_mults"]],
            "sl_to_breakeven": r.get("sl_to_breakeven"),
            "profit_lock_keep": r.get("profit_lock_keep")}


def r_dopo(trades: list[dict], inizio: float, fine: float, secondi_barra: float) -> dict:
    """I trade (dict di `pb.trade_in_dict`) ENTRATI in (inizio, fine]: l'ingresso
    e' alla chiusura della candela del segnale (`entry_ts` e' la sua apertura,
    quindi ingresso = entry_ts + una candela). R = pnl_pct / stop_pct, come
    `pb.fuori_campione` per il motore. Fuori, contati: chi esce sull'ultima
    candela dei dati (ancora aperto, `fine_dati`) e chi non ha lo stop."""
    rs: list[float] = []
    fine_dati = senza_stop = 0
    for t in trades:
        ingresso = float(t.get("entry_ts") or 0) + secondi_barra
        if not (inizio < ingresso <= fine):
            continue
        if t.get("fine_dati"):
            fine_dati += 1
            continue
        stop = float(t.get("stop_pct") or 0)
        if stop <= 0:
            senza_stop += 1
            continue
        rs.append(round(float(t.get("pnl_pct") or 0.0) / stop, 4))
    return {"r": rs, "fine_dati": fine_dati, "senza_stop": senza_stop}


def somme(rs) -> list:
    """[n, somma, somma dei quadrati] di una lista di R: bastano per media,
    deviazione standard ed errori standard, senza tenere milioni di numeri (le
    bocciate di 26 date possono fare milioni di trade)."""
    rs = [float(r) for r in rs]
    return [len(rs), sum(rs), sum(r * r for r in rs)]


def _piu(a: list, b) -> list:
    return [a[0] + int(b[0]), a[1] + float(b[1]), a[2] + float(b[2])]


def somme_per_data(unita: list[dict]) -> dict:
    """{data: {passate, bocciate, conferme3: [n, somma, quadrati]}} da tutte le
    unita' finite. `conferme3`: le passate che passavano anche 7 e 14 giorni
    prima (solo con `--conferme`, solo informativo)."""
    out: dict = {}
    for u in unita:
        if not isinstance(u, dict) or u.get("stato") != "ok":
            continue
        g = out.setdefault(u.get("data"), {"passate": [0, 0.0, 0.0], "bocciate": [0, 0.0, 0.0],
                                            "conferme3": [0, 0.0, 0.0]})
        for c in u.get("passate") or []:
            sq = somme(c.get("r") or [])
            g["passate"] = _piu(g["passate"], sq)
            if c.get("conferme") == 2:
                g["conferme3"] = _piu(g["conferme3"], sq)
        b = u.get("bocciate") or {}
        g["bocciate"] = _piu(g["bocciate"], (b.get("n", 0), b.get("s", 0.0), b.get("q", 0.0)))
    return out


def statistiche_da_somme(nsq) -> dict:
    """n, R medio e deviazione standard (n-1) da [n, somma, quadrati]: gli
    stessi numeri di `pb.statistiche_lato` sulla lista (verificato nei test)."""
    n, s, q = int(nsq[0]), float(nsq[1]), float(nsq[2])
    media = s / n if n else None
    dev = math.sqrt(max(0.0, (q - s * s / n) / (n - 1))) if n >= 2 else None
    return {"n": n, "r_medio": media, "dev_std": dev}


def errore_per_data(per_data: dict, a: str = "passate", b: str = "bocciate") -> float | None:
    """L'errore standard della differenza media(a) - media(b) RAGGRUPPATO PER
    DATA: la formula di `pb.errore_standard_per_giorno` (u_g = contributo della
    data g alla differenza, varianza G/(G-1) x somma u_g^2) calcolata dalle
    somme invece che dalla lista dei trade (stesso numero, verificato nei test).
    None con meno di 2 trade per lato o meno di 2 date."""
    tot_a = [0, 0.0, 0.0]
    tot_b = [0, 0.0, 0.0]
    for g in per_data.values():
        tot_a, tot_b = _piu(tot_a, g[a]), _piu(tot_b, g[b])
    if tot_a[0] < 2 or tot_b[0] < 2:
        return None
    ma, mb = tot_a[1] / tot_a[0], tot_b[1] / tot_b[0]
    u = []
    for g in per_data.values():
        if not g[a][0] and not g[b][0]:
            continue
        u.append((g[a][1] - g[a][0] * ma) / tot_a[0] - (g[b][1] - g[b][0] * mb) / tot_b[0])
    if len(u) < 2:
        return None
    return math.sqrt(len(u) / (len(u) - 1) * sum(x * x for x in u))


def lettura(per_data: dict) -> dict:
    """I numeri della regola e l'esito, dalle somme per data. Il margine e' 2
    errori standard, il piu' largo fra quello PER DATA (`errore_per_data`: i
    trade della stessa data non sono indipendenti) e quello trade per trade
    (la formula di `pb.errore_standard_differenza`); `pb.errore_regola` prende
    il piu' largo, e senza quello per data (meno di 2 date) la regola non
    decide."""
    tot = {k: [0, 0.0, 0.0] for k in ("passate", "bocciate")}
    for g in per_data.values():
        for k in tot:
            tot[k] = _piu(tot[k], g[k])
    a, b = statistiche_da_somme(tot["passate"]), statistiche_da_somme(tot["bocciate"])
    diff = (a["r_medio"] - b["r_medio"]
            if a["r_medio"] is not None and b["r_medio"] is not None else None)
    es_trade = pb.errore_standard_differenza(a, b)
    es_data = errore_per_data(per_data) if per_data else None
    es = pb.errore_regola(es_trade, es_data)
    margine = 2.0 * es if es is not None else None
    if a["n"] < MIN_TRADE_PASSATE:
        esito = "non si sa"
        perche = f"{a['n']} trade delle passate, ne servono {MIN_TRADE_PASSATE}"
    elif diff is None or margine is None:
        esito = "non si sa"
        perche = "differenza o margine non calcolabili (servono almeno 2 date)"
    elif diff > margine:
        esito = "il gate ha un vantaggio vero"
        perche = "differenza oltre il margine"
    elif diff + margine < SOGLIA_FORTUNA_R:
        esito = "il gate sceglie soprattutto fortuna"
        perche = f"differenza + margine sotto {SOGLIA_FORTUNA_R:.2f}R"
    else:
        esito = "non si sa"
        perche = "differenza dentro il margine, ma il caso migliore supera 0,10R"
    return {"passate": a, "bocciate": b, "differenza": diff, "errore_trade": es_trade,
            "errore_data": es_data, "margine": margine, "esito": esito, "perche": perche}


def differenze_per_data(per_data: dict) -> dict:
    """Solo informativo: per ogni data con trade da tutti e due i lati, R medio
    delle passate meno R medio delle bocciate."""
    out = {}
    for g in sorted(per_data):
        pa, bo = per_data[g]["passate"], per_data[g]["bocciate"]
        if pa[0] and bo[0]:
            out[g] = pa[1] / pa[0] - bo[1] / bo[0]
    return out


# --------------------------------------------------------------------------- #
# Il piano e i file delle unita'                                               #
# --------------------------------------------------------------------------- #
def _leggi_json(path: str) -> dict | None:
    try:
        with open(path, encoding="utf-8") as f:
            doc = json.load(f)
        return doc if isinstance(doc, dict) else None
    except (OSError, ValueError):
        return None


def leggi_piano(path: str | None = None) -> dict | None:
    return _leggi_json(path or FILE_PIANO)


def crea_piano(args, oggi: date, universo: list[str]) -> dict:
    """Il piano del lavoro, fissato al primo lancio: le date, le monete, quante
    candidate e i semi, e le impostazioni di motore e gate con cui si giudica
    (`d.motore_del_giro`, le stesse della riga «giro» del gruppo di controllo).
    I lanci dopo usano QUESTO, anche se cambiano il giorno o le monete in testa
    al volume."""
    date_ = date_del_piano(oggi)
    return {"versione": VERSIONE,
            "creato_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
            "oggi": oggi.isoformat(), "date": date_, "universo": list(universo),
            "candidate_per_data": int(args.candidate),
            "semi": {g: seme_della_data(g) for g in date_},
            "interval": args.interval, "start": args.start, "source": args.source,
            "windows": int(args.windows), "motore": d.motore_del_giro(args)}


def path_unita(giorno: str, coin: str, base: str | None = None) -> str:
    return os.path.join(base or DIR_UNITA, giorno, f"{coin}.json")


def leggi_unita(base: str | None = None) -> dict:
    """{(data, coin): record} di tutte le unita' scritte."""
    base = base or DIR_UNITA
    out: dict = {}
    try:
        giorni = os.listdir(base)
    except OSError:
        return out
    for g in giorni:
        cartella = os.path.join(base, g)
        try:
            nomi = os.listdir(cartella)
        except OSError:
            continue
        for n in nomi:
            if not n.endswith(".json"):
                continue
            rec = _leggi_json(os.path.join(cartella, n))
            if rec is not None:
                out[(g, n[:-len(".json")])] = rec
    return out


def unita_chiusa(rec: dict | None) -> bool:
    """True se l'unita' non si rifa': finita, o in errore gia' riprovata."""
    if not isinstance(rec, dict):
        return False
    if rec.get("stato") in FINALI:
        return True
    return rec.get("stato") == "errore" and int(rec.get("tentativi") or 0) >= TENTATIVI_MAX


def date_complete(piano: dict, fatte: dict) -> list[str]:
    return [g for g in piano["date"]
            if all(unita_chiusa(fatte.get((g, c))) for c in piano["universo"])]


def lavoro_da_fare(piano: dict, fatte: dict, limit: int = 0) -> tuple[list, bool]:
    """(unita' da fare in questo lancio, nell'ordine delle date dalla piu'
    recente; prova piccola si'/no). Finche' nessuna data e' completa, solo le
    prime PROVA_DATE date."""
    prova = not date_complete(piano, fatte)
    date_ = piano["date"][:PROVA_DATE] if prova else piano["date"]
    lavoro = [(g, c) for g in date_ for c in piano["universo"]
              if not unita_chiusa(fatte.get((g, c)))]
    if limit and limit > 0:
        lavoro = lavoro[:limit]
    return lavoro, prova


def salva_unita(rec: dict, base: str | None = None) -> bool:
    """Scrive il file dell'unita' (atomico) se l'esito vale: le unita' fermate
    per tempo, per il giro o da un worker morto NON si scrivono (si rifanno).
    Un errore porta il numero di tentativi."""
    stato = rec.get("stato")
    if stato not in FINALI and stato != "errore":
        return False
    path = path_unita(rec["data"], rec["coin"], base)
    if stato == "errore":
        prima = _leggi_json(path) or {}
        rec = {**rec, "tentativi": int(prima.get("tentativi") or 0) + 1}
    scrivi_atomico(path, rec)
    return True


# --------------------------------------------------------------------------- #
# Il giro del gate (memoria): gli stessi controlli del voto t                  #
# --------------------------------------------------------------------------- #
def giro_in_corso(proc: str = "/proc", moduli: tuple = MODULI_PESANTI) -> list[int]:
    """I pid dei processi pesanti in corso (giro del gate, voto t). Come
    `t_validate.giro_in_corso`, con in piu' la passata del voto t. Fail-open."""
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
        if any(m in cmd for m in moduli):
            trovati.append(int(voce))
    return sorted(trovati)


#: quanto aspettare per ricontrollare, nell'ora del giro saltato: il servizio del
#: gate parte lo stesso, vede la finestra di R1 ed esce in pochi secondi
RICONTROLLO_SALTATO_S = 20.0


def gate_in_arrivo(margine_s: float) -> str | None:
    """None se si puo' lavorare; altrimenti perche' no, in una frase.

    Nell'ora del giro SALTATO (12 UTC, R1 attivo: bot/core/finestra_r1.py) il
    servizio del gate parte comunque e si chiude subito: un gate «in corso» visto
    in quell'ora si ricontrolla dopo RICONTROLLO_SALTATO_S, e conta solo se c'e'
    ancora (un giro delle 09 UTC lungo, che sfora nelle 12, resta un giro vero)."""
    motivo = _gate_in_arrivo(margine_s)
    if motivo and finestra_r1.slot_saltato(time.time(), FILE_ATTIVO):
        time.sleep(RICONTROLLO_SALTATO_S)
        motivo = _gate_in_arrivo(margine_s)
    return motivo


def _gate_in_arrivo(margine_s: float) -> str | None:
    pids = giro_in_corso()
    if pids:
        return (f"il giro del gate (o la passata del voto t) e' in corso "
                f"(pid {', '.join(map(str, pids))})")
    if servizio_gate_attivo():
        return f"il giro del gate e' in corso ({tv.SERVIZIO_GATE} attivo)"
    s = secondi_al_prossimo_giro()
    # il giro delle 12 UTC si salta mentre R1 e' attivo (bot/core/finestra_r1.py):
    # per R1 il «prossimo giro» e' quello dopo, 3 ore piu' tardi
    if s is not None and finestra_r1.slot_saltato(time.time() + s, FILE_ATTIVO):
        s += 3 * 3600.0
    if s is not None and s < margine_s:
        return f"il prossimo giro del gate parte fra {max(0.0, s) / 60:.0f} minuti"
    return None


def aspetta_il_giro(aspetta: bool) -> bool:
    """True quando si puo' partire. In primo piano non si aspetta (si esce e lo
    si dice); in sfondo si aspetta, al massimo ATTESA_MAX_S."""
    t0 = time.time()
    detto = False
    while True:
        motivo = gate_in_arrivo(MARGINE_PARTENZA_S)
        if not motivo:
            return True
        if not aspetta:
            di(f"[r1] {motivo}: non parto ora, per non tenere in memoria due gruppi di "
               f"worker. Usa `replay-gate`, che aspetta da solo.")
            return False
        if time.time() - t0 > ATTESA_MAX_S:
            di(f"[r1] {motivo}, e aspetto da {ATTESA_MAX_S / 3600:.0f} ore: esco senza "
               f"aver fatto niente. Rilancia.")
            return False
        if not detto:
            di(f"[r1] {motivo}: aspetto, poi parto.")
            detto = True
        time.sleep(ATTESA_PASSO_S)


# --------------------------------------------------------------------------- #
# Il calcolo (nei worker)                                                      #
# --------------------------------------------------------------------------- #
def _init(cfg: dict, end: str, deadline: float, conferme: bool = False) -> None:
    """Lo stato del worker: un optimizer con le finestre del gate e la deadline.
    BTC (il contesto di mercato) si carica alla prima spec che lo usa."""
    _S.clear()
    _S.update(opt=WalkForwardOptimizer(n_windows=int(cfg["windows"]), interval=cfg["interval"]),
              cfg=dict(cfg), end=end, deadline=float(deadline or 0.0),
              conferme=bool(conferme), min_history=_min_history(cfg["interval"]),
              btc=None, btc_letto=False, ctx_gate={}, ctx_dopo={}, specs={})


def _scaduto() -> bool:
    dl = float(_S.get("deadline") or 0.0)
    return bool(dl) and time.time() > dl


def _carica(sym: str):
    """LA STESSA CHIAMATA DEL GATE: fino a OGGI (`end` del lancio), mai una fine
    nel passato. Il taglio alla data si fa dopo, in memoria."""
    cfg = _S["cfg"]
    return load_candles(sym, cfg["interval"], cfg["start"], _S["end"], prefer=cfg["source"])


def _btc():
    if not _S.get("btc_letto"):
        _S["btc_letto"] = True
        try:
            _S["btc"] = _carica(MARKET_SYMBOL)
        except Exception as exc:  # noqa: BLE001
            di(f"[r1] contesto di mercato non disponibile ({str(exc)[:80]})")
            _S["btc"] = None
    return _S.get("btc")


def contesto_gate(taglio: float):
    """Il contesto di mercato del GATE alla data: BTC tagliato prima della data,
    indicatori calcolati sul tagliato. Uno solo in memoria per worker (tre con
    `--conferme`, che giudica anche 7 e 14 giorni prima)."""
    cache = _S["ctx_gate"]
    if taglio in cache:
        return cache[taglio]
    if len(cache) >= (3 if _S.get("conferme") else 1):
        cache.clear()
    btc = _btc()
    ctx = None
    if btc:
        k = d._taglio_a(btc, taglio - 1.0)
        if k >= 200:
            ctx = _S["opt"].bt.build_context(MARKET_SYMBOL, btc[:k])
    cache[taglio] = ctx
    return ctx


def contesto_dopo(taglio: float, fine: float):
    """Il contesto di mercato del rigioco DOPO la data: solo il pezzo che serve
    (dal riscaldamento prima della data a `fine`, la fine del pezzo rigiocato)."""
    chiave = (taglio, fine)
    cache = _S["ctx_dopo"]
    if chiave in cache:
        return cache[chiave]
    cache.clear()
    btc = _btc()
    ctx = None
    if btc:
        a = max(0, d._taglio_a(btc, taglio - 1.0) - _S["opt"].bt.window)
        b = d._taglio_a(btc, fine)
        if b - a >= 200:
            fr = compute_indicator_frame(btc[:b]).iloc[a:b].reset_index(drop=True)
            ctx = _S["opt"].bt.build_context(MARKET_SYMBOL, btc[a:b], frame=fr)
    cache[chiave] = ctx
    return ctx


def _specs(giorno: str) -> list[dict]:
    cache = _S["specs"]
    if giorno not in cache:
        cache.clear()
        cache[giorno] = candidate_della_data(giorno, _S["cfg"]["candidate_per_data"])
    return cache[giorno]


def giudica(opt, sym: str, candles, taglio: float, specs: list[dict], ctx_fn) -> list[dict] | None:
    """Il gate alla data `taglio` su UNA coin: SOLO le candele aperte prima del
    taglio (chiuse entro il taglio), indicatori calcolati su quelle. None se la
    storia alla data e' sotto il minimo del gate. Gli esiti nell'ordine delle
    spec: il risultato di `evaluate_spec` cosi' com'e'."""
    k = d._taglio_a(candles, taglio - 1.0)
    if k < _S["min_history"]:
        return None
    cand = candles[:k]
    frame = compute_indicator_frame(cand)
    d.svuota_cache_motore(opt)
    out = []
    for spec in specs:
        out.append(d.evaluate_spec(
            opt, sym, cand, frame, spec,
            scale_candidates=d.candidate_ladders(), keep_candidates=d.candidate_keeps(),
            context_by_ts=ctx_fn(taglio) if usa_mercato(spec) else None,
            run_end=dt.datetime.fromtimestamp(taglio, dt.timezone.utc).date().isoformat(),
            interval=_S["cfg"]["interval"]))
    d.svuota_cache_motore(opt)
    return out


def rigioca_dopo(opt, sym: str, candles, taglio: float, voci: list[dict],
                 specs: list[dict]) -> None:
    """I trade del motore di ogni candidata entrati nei DOPO_GIORNI dopo la
    data, con la sua configurazione d'uscita. Il motore parte alla data (il
    riscaldamento e' prima, `bt.window` candele: lo stesso pezzo che l'holdout del
    gate, `_holdout_check`, mette prima del suo taglio) e va oltre la fine della
    finestra di HORIZON_BARS candele, cosi' anche i trade entrati alla fine
    hanno un'uscita vera. Scrive `r`, `fine_dati`, `senza_stop` in ogni voce."""
    secondi_barra = timeframe_hours(_S["cfg"]["interval"]) * 3600.0
    fine = taglio + DOPO_GIORNI * 86400.0
    fine_pezzo = fine + (HORIZON_BARS + 2) * secondi_barra
    a = max(0, d._taglio_a(candles, taglio - 1.0) - opt.bt.window)
    b = d._taglio_a(candles, fine_pezzo)
    if b - a <= opt.bt.window + 1:
        for v in voci:
            v.update(r=[], fine_dati=0, senza_stop=0)
        return
    seg = candles[a:b]
    frame = compute_indicator_frame(candles[:b]).iloc[a:b].reset_index(drop=True)
    fine_ts = float(seg[-1].open_time.timestamp())
    d.svuota_cache_motore(opt)
    for spec, v in zip(specs, voci):
        g = crea_operata(spec, v.get("uscita"))()
        st = opt.bt.run_strategy(g, sym, seg, frame=frame,
                                 context_by_ts=contesto_dopo(taglio, fine_pezzo) if usa_mercato(spec)
                                 else None)
        scala = ladder_multiples(getattr(g, "params", None))
        trades = [pb.trade_in_dict(t, sym, spec["id"], scala=scala, fine_ts=fine_ts,
                                   secondi_barra=secondi_barra) for t in st.trades]
        v.update(r_dopo(trades, taglio, fine, secondi_barra))
    d.svuota_cache_motore(opt)


def voce_candidata(spec: dict, r: dict) -> dict:
    """Cosa resta di una candidata: verdetto, criterio che l'ha fermata, trade
    nel gate, holdout, uscita scelta. Solo numeri e stringhe corte."""
    hold = r.get("holdout") if isinstance(r.get("holdout"), dict) else {}
    v = {"id": spec["id"], "passata": bool(r.get("passed")),
         "binding": None if r.get("passed") else (r.get("fail_binding") or "?"),
         "trade_gate": int(r.get("trades") or 0), "uscita": uscita_scelta(r)}
    if hold:
        v["holdout"] = {"trades": hold.get("trades"), "pf": hold.get("pf"),
                        "ok": bool(hold.get("ok"))}
    return v


def rigioca_unita(sym: str, giorno: str, candles) -> dict:
    """UNA unita': il gate alla data su una coin, poi i 14 giorni dopo."""
    opt = _S["opt"]
    taglio = _ts(giorno)
    specs = _specs(giorno)
    esiti = giudica(opt, sym, candles, taglio, specs, contesto_gate)
    if esiti is None:
        return {"stato": "storia"}
    voci = [voce_candidata(s, r) for s, r in zip(specs, esiti)]
    if _S.get("conferme"):
        # SOLO INFORMATIVO (non decide): le passate alla data passano anche 7 e
        # 14 giorni prima? Come le validate a 3 conferme. Solo per le passate
        passate = [(s, v) for s, v in zip(specs, voci) if v["passata"]]
        for v in voci:
            if v["passata"]:
                v["conferme"] = 0
        for giorni_prima in (7, 14):
            if not passate:
                break
            prima = giudica(opt, sym, candles, taglio - giorni_prima * 86400.0,
                            [s for s, _ in passate], contesto_gate)
            for (_s, v), r in zip(passate, prima or []):
                v["conferme"] += int(bool(r.get("passed")))
    rigioca_dopo(opt, sym, candles, taglio, voci, specs)
    return record_unita(voci, conferme=bool(_S.get("conferme")))


def record_unita(voci: list[dict], conferme: bool = False) -> dict:
    """Il record di un'unita' finita, piccolo: le PASSATE una per una (con la
    lista dei loro R dopo la data: sono poche), le BOCCIATE riassunte (quante,
    per criterio, e le somme dei loro R: possono essere migliaia di trade per
    unita')."""
    passate = [v for v in voci if v.get("passata")]
    bocciate = [v for v in voci if not v.get("passata")]
    tot = [0, 0.0, 0.0]
    for v in bocciate:
        tot = _piu(tot, somme(v.get("r") or []))
    return {"stato": "ok", "n_candidate": len(voci), "passate": passate,
            "bocciate": {"n_candidate": len(bocciate),
                         "per_criterio": dict(Counter(str(v.get("binding")) for v in bocciate)),
                         "con_trade": sum(1 for v in bocciate if v.get("r")),
                         "n": tot[0], "s": round(tot[1], 6), "q": round(tot[2], 6),
                         "fine_dati": sum(int(v.get("fine_dati") or 0) for v in bocciate),
                         "senza_stop": sum(int(v.get("senza_stop") or 0) for v in bocciate)},
            "conferme_calcolate": bool(conferme)}


def _una_unita(item) -> dict:
    """Il lavoro di un worker: prima il tempo e il giro del gate, poi candele
    (fino a oggi), controlli come il gate, `rigioca_unita`. Un errore e' un
    esito dell'unita', non la fine del lancio."""
    giorno, sym = item
    base = {"data": giorno, "coin": sym}
    if _scaduto():
        return {**base, "stato": "tempo"}
    ferma = gate_in_arrivo(MARGINE_FERMATA_S)
    if ferma:
        return {**base, "stato": "giro", "errore": ferma}
    t0 = time.time()
    try:
        candles = _carica(sym)
        if not candles:
            # puo' essere la rete per un momento: un errore, che si riprova
            return {**base, "stato": "errore", "errore": "nessuna candela"}
        if looks_delisted(candles, _S["end"], timeframe_hours(_S["cfg"]["interval"])):
            return {**base, "stato": "delistata",
                    "errore": f"serie ferma al {candles[-1].open_time:%Y-%m-%d}"}
        rec = {**base, **rigioca_unita(sym, giorno, candles)}
    except Exception as exc:  # noqa: BLE001
        return {**base, "stato": "errore", "errore": str(exc)[:120],
                "secondi": round(time.time() - t0, 1)}
    rec["secondi"] = round(time.time() - t0, 1)
    rec["calcolata_at"] = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
    if rec.get("stato") == "ok":
        n_t = sum(len(v.get("r") or []) for v in rec["passate"])
        di(f"[r1] {giorno} {sym}: {rec['n_candidate']} candidate, {len(rec['passate'])} "
           f"passate ({n_t} trade dopo), bocciate {rec['bocciate']['n']} trade dopo, "
           f"{rec['secondi']:.0f}s")
    return rec


def esegui_e_salva(lavoro: list, workers: int, initargs: tuple, salva,
                   unita=None) -> tuple[list[dict], str | None]:
    """Unita' per unita', e `salva(record)` appena ognuna e' finita (nel padre,
    che tiene il lucchetto). Come `t_validate.esegui_e_salva`: un worker ucciso
    dal kernel non fa perdere le unita' gia' finite; le sue diventano
    «interrotta» (non si scrivono, si rifanno)."""
    righe: list[dict] = []
    unita = unita or _una_unita
    if workers <= 1 or len(lavoro) <= 1:
        _init(*initargs)
        for item in lavoro:
            try:
                rec = unita(item)
            except Exception as exc:  # noqa: BLE001
                rec = {"data": item[0], "coin": item[1], "stato": "errore",
                       "errore": str(exc)[:120]}
            salva(rec)
            righe.append(rec)
        return righe, None
    interrotta = None
    with ProcessPoolExecutor(max_workers=workers, initializer=_init, initargs=initargs) as ex:
        futuri = {ex.submit(unita, item): item for item in lavoro}
        for f in as_completed(futuri):
            giorno, sym = futuri[f]
            try:
                rec = f.result()
            except BrokenProcessPool as exc:
                interrotta = interrotta or f"un worker e' morto (memoria?): {str(exc)[:100]}"
                righe.append({"data": giorno, "coin": sym, "stato": "interrotta"})
                continue
            except Exception as exc:  # noqa: BLE001
                rec = {"data": giorno, "coin": sym, "stato": "errore",
                       "errore": f"worker: {str(exc)[:100]}"}
            salva(rec)
            righe.append(rec)
    return righe, interrotta


# --------------------------------------------------------------------------- #
# R2: le candidate di R1 giudicate dal gate vero, coi dati di oggi             #
# --------------------------------------------------------------------------- #
def _una_unita_r2(item) -> dict:
    """UNA coin: le candidate della data R2 giudicate con TUTTE le candele
    (fino a oggi, `end` del lancio), cioe' come il gate vero. Niente rigioco
    dopo: conta solo chi passa."""
    giorno, sym = item
    base = {"data": giorno, "coin": sym}
    if _scaduto():
        return {**base, "stato": "tempo"}
    ferma = gate_in_arrivo(MARGINE_FERMATA_S)
    if ferma:
        return {**base, "stato": "giro", "errore": ferma}
    t0 = time.time()
    try:
        candles = _carica(sym)
        if not candles:
            return {**base, "stato": "errore", "errore": "nessuna candela"}
        specs = _specs(giorno)
        oggi = _ts(_S["end"]) + 86400.0            # tutte le candele caricate
        esiti = giudica(_S["opt"], sym, candles, oggi, specs, contesto_gate)
        if esiti is None:
            return {**base, "stato": "storia", "secondi": round(time.time() - t0, 1)}
        voci = [voce_candidata(sp, r) for sp, r in zip(specs, esiti)]
        rec = {**base, "stato": "ok", "n_candidate": len(voci),
               "passate": [v for v in voci if v["passata"]],
               "per_criterio": dict(Counter(str(v.get("binding")) for v in voci
                                           if not v["passata"]))}
    except Exception as exc:  # noqa: BLE001
        return {**base, "stato": "errore", "errore": str(exc)[:120],
                "secondi": round(time.time() - t0, 1)}
    rec["secondi"] = round(time.time() - t0, 1)
    di(f"[r2] {sym}: {rec['n_candidate']} candidate, {len(rec['passate'])} passate nel "
       f"gate di oggi, {rec['secondi']:.0f}s")
    return rec


def _una_unita_g7(item) -> dict:
    """L'unita' di G7 (scripts/gate_sul_caso.py) col modulo di QUESTO processo:
    lanciato con `python -m`, lo stato dei worker sta in `__main__` (ops 0485:
    importato da gate_sul_caso il modulo era un altro, vuoto)."""
    from scripts import gate_sul_caso as g7
    return g7._una_unita_g7(item, sys.modules[__name__])


def salva_unita_r2(rec: dict) -> bool:
    """Come `salva_unita`, nella cartella di R2: solo esiti finali o errori (col
    numero di tentativi, per non riprovare all'infinito)."""
    if rec.get("stato") not in FINALI and rec.get("stato") != "errore":
        return False
    os.makedirs(DIR_UNITA_R2, exist_ok=True)
    path = os.path.join(DIR_UNITA_R2, f"{rec['coin']}.json")
    if rec.get("stato") == "errore":
        prima = _leggi_json(path) or {}
        rec = {**rec, "tentativi": int(prima.get("tentativi") or 0) + 1}
    scrivi_atomico(path, rec)
    return True


def leggi_unita_r2(base: str | None = None) -> dict:
    base = base or DIR_UNITA_R2
    out: dict = {}
    try:
        nomi = os.listdir(base)
    except OSError:
        return out
    for n in nomi:
        if n.endswith(".json"):
            rec = _leggi_json(os.path.join(base, n))
            if isinstance(rec, dict):
                out[rec.get("coin") or n[:-5]] = rec
    return out


def lavoro_r2(piano: dict, fatte: dict) -> list:
    return [(R2_DATA, c) for c in (piano.get("universo") or [])
            if not unita_chiusa(fatte.get(c))]


def lettura_r2(piano: dict | None, fatte: dict) -> dict:
    """I numeri di R2 e l'esito con la regola (scritta prima dei numeri)."""
    monete = list((piano or {}).get("universo") or [])
    ok = [r for c, r in fatte.items() if c in monete and r.get("stato") == "ok"]
    passate = sum(len(r.get("passate") or []) for r in ok)
    coppie = sum(int(r.get("n_candidate") or 0) for r in ok)
    crit: Counter = Counter()
    for r in ok:
        crit.update(r.get("per_criterio") or {})
    completa = bool(monete) and all(unita_chiusa(fatte.get(c)) for c in monete)
    if not completa:
        esito = "in corso"
    elif passate >= R2_SOGLIA_SEVERO:
        esito = "R1 E' PIU' SEVERO DEL GATE: R1 si ferma finche' non e' corretto"
    elif passate <= 1:
        esito = ("lo 0 di R1 e' vero: le candidate a caso quasi non passano nemmeno nel gate "
                 "di oggi. Scatta il cambio di piano del 2 ott (lo decide il proprietario)")
    else:
        esito = "2 passate: non si decide"
    return {"data": R2_DATA, "monete": len(monete), "fatte": len(ok), "coppie": coppie,
            "passate": passate, "per_criterio": dict(crit.most_common(6)),
            "completa": completa, "esito": esito}


def righe_lettura_r2(piano: dict | None, fatte: dict) -> list[str]:
    if not R2_ATTIVO or not piano:
        return []
    r = lettura_r2(piano, fatte)
    if not r["fatte"] and not r["completa"]:
        return ["[r2] taratura di R1 (le sue 50 candidate del 17 set nel gate di oggi): non "
                "ancora fatta, parte all'inizio del prossimo lancio"]
    out = [f"[r2] TARATURA DI R1 · candidate del {r['data']} giudicate dal gate di OGGI su "
           f"{r['fatte']}/{r['monete']} monete · {r['coppie']} coppie · PASSATE {r['passate']}",
           f"  REGOLA R2 (3 ott, scritta prima dei numeri): >= {R2_SOGLIA_SEVERO} passate -> R1 e' "
           f"piu' severo del gate, si ferma finche' non e' corretto; 0-1 -> lo 0 di R1 e' vero, "
           f"cambio di piano; 2 -> non si decide",
           f"  bocciate per criterio: " + ", ".join(f"{k} {v}" for k, v in r["per_criterio"].items()),
           f"  ESITO R2: {r['esito']}" + ("" if r["completa"] else " (PARZIALE)")]
    return out


# --------------------------------------------------------------------------- #
# Stampa                                                                       #
# --------------------------------------------------------------------------- #
def _fmt_r(v) -> str:
    return pb._fmt_r(v)


def _gruppo(s: dict) -> str:
    if not s or not s.get("n"):
        return "0 trade"
    return f"{s['n']} trade, R medio {_fmt_r(s['r_medio'])}R"


def _margine_testo(let: dict) -> str:
    e_t, e_d = let["errore_trade"], let["errore_data"]
    m = "n.d." if let["margine"] is None else f"±{let['margine']:.2f}"
    d_ = "n.d." if e_d is None else f"{2 * e_d:.2f}"
    t_ = "n.d." if e_t is None else f"{2 * e_t:.2f}"
    return f"margine {m} (2 errori standard: per data {d_}, trade per trade {t_}; vale il piu' largo)"


def righe_lettura(piano: dict | None, fatte: dict) -> list[str]:
    """Avanzamento, la regola PRIMA dei numeri, i numeri, l'esito (PARZIALE
    finche' le 26 date non sono complete) e le righe informative."""
    if not piano:
        return ["[r1] nessun piano: il lavoro non e' ancora partito (lancia `replay-gate`)."]
    fatte = unita_del_piano(piano, fatte)
    date_ = list(piano.get("date") or [])
    complete = date_complete(piano, fatte)
    unita = [u for u in fatte.values() if isinstance(u, dict)]
    ok = [u for u in unita if u.get("stato") == "ok"]
    stati = Counter(str(u.get("stato")) for u in unita)
    totale = len(date_) * len(piano.get("universo") or [])
    chiuse = sum(1 for u in unita if unita_chiusa(u))
    candidate = sum(int(u.get("n_candidate") or 0) for u in ok)
    n_pass = sum(len(u.get("passate") or []) for u in ok)
    per_data = somme_per_data(ok)
    let = lettura(per_data)
    out = [f"[r1] AVANZAMENTO · date complete {len(complete)} su {len(date_)} · unita' "
           f"(coin x data) chiuse {chiuse} su {totale}"
           + "".join(f" · {k} {v}" for k, v in sorted(stati.items())),
           f"  candidate giudicate {candidate} (passate {n_pass}) · trade dopo la data: passate "
           f"{let['passate']['n']}, bocciate {let['bocciate']['n']} · piano del "
           f"{piano.get('oggi')}: {piano.get('candidate_per_data')} candidate per data, "
           f"{len(piano.get('universo') or [])} monete, date {date_[-1] if date_ else '?'} -> "
           f"{date_[0] if date_ else '?'}"]
    secondi = [float(u["secondi"]) for u in ok if u.get("secondi")]
    mancano = totale - chiuse
    if secondi and mancano:
        out.append(f"  tempo medio misurato per unita' {mean(secondi):.0f}s: per le {mancano} "
                   f"rimaste STIMA ~{mean(secondi) * mancano / max(1, WORKERS) / 3600:.1f} ore "
                   f"con {WORKERS} worker (un tetto: le unita' senza storia costano meno)")
    parziale = len(complete) < len(date_)
    out.append(f"  REGOLA R1 (scritta prima dei numeri, docs/andremo_live.md): {REGOLA_R1}.")
    out.append(f"  passate: {_gruppo(let['passate'])} · bocciate: {_gruppo(let['bocciate'])} · "
               f"differenza {_fmt_r(let['differenza'])}R · {_margine_testo(let)}")
    if parziale:
        out.append(f"  LETTURA PARZIALE ({len(complete)} date complete su {len(date_)}: non "
                   f"decide ancora): {let['esito'].upper()} — {let['perche']}.")
    else:
        out.append(f"  LETTURA: {let['esito'].upper()} — {let['perche']}.")
    # per data, informativo
    diff_d = differenze_per_data(per_data)
    per_g: dict = {}
    for u in ok:
        per_g.setdefault(u.get("data"), []).append(u)
    righe_d = []
    for g in date_:
        us = per_g.get(g)
        if not us:
            continue
        sp = statistiche_da_somme(per_data[g]["passate"])
        sb = statistiche_da_somme(per_data[g]["bocciate"])
        np_ = sum(len(u.get("passate") or []) for u in us)
        righe_d.append(f"    {g}{' *' if g in complete else '  '} coin {len(us):>3} · passate "
                       f"{np_:>3} · trade {sp['n']:>4} {_fmt_r(sp['r_medio']):>6}R · bocciate "
                       f"trade {sb['n']:>6} {_fmt_r(sb['r_medio']):>6}R"
                       + (f" · diff {_fmt_r(diff_d[g])}" if g in diff_d else ""))
    if righe_d:
        out.append("  per data (* = completa; solo informativo):")
        out.extend(righe_d)
    if diff_d:
        pos = sum(1 for v in diff_d.values() if v > 0)
        out.append(f"  differenza positiva in {pos} date su {len(diff_d)} con trade da tutti e "
                   f"due i lati (informativo)")
    binding: Counter = Counter()
    fuori = Counter()
    for u in ok:
        b = u.get("bocciate") or {}
        binding.update({k: int(v) for k, v in (b.get("per_criterio") or {}).items()})
        fuori["fine_dati"] += int(b.get("fine_dati") or 0)
        fuori["senza_stop"] += int(b.get("senza_stop") or 0)
        for c in u.get("passate") or []:
            fuori["fine_dati"] += int(c.get("fine_dati") or 0)
            fuori["senza_stop"] += int(c.get("senza_stop") or 0)
    if binding:
        out.append("  bocciate per criterio: " + ", ".join(
            f"{k} {v}" for k, v in binding.most_common(6)))
    if fuori["fine_dati"] or fuori["senza_stop"]:
        out.append(f"  trade fuori dal conto: {fuori['fine_dati']} ancora aperti a fine dati, "
                   f"{fuori['senza_stop']} senza stop")
    con = [u for u in ok if u.get("conferme_calcolate")]
    if con:
        tot3 = [0, 0.0, 0.0]
        for g in per_data.values():
            tot3 = _piu(tot3, g["conferme3"])
        out.append(f"  SOLO INFORMATIVO, non decide: passate anche 7 e 14 giorni prima (come a 3 "
                   f"conferme), su {len(con)} unita': {_gruppo(statistiche_da_somme(tot3))}")
    out.append(f"  limiti dichiarati: {LIMITI_R1}")
    return out


# --------------------------------------------------------------------------- #
# main                                                                         #
# --------------------------------------------------------------------------- #
def _processo_vivo(pid: int) -> bool:
    return tv._processo_vivo(pid)


def esito() -> int:
    """Lo stato dell'ultimo lancio (se gira ancora) e le sue ultime righe, poi
    avanzamento e lettura ricalcolati dai file delle unita'. Sola lettura."""
    if os.path.exists(FILE_ESITO):
        mtime = dt.datetime.fromtimestamp(os.path.getmtime(FILE_ESITO), dt.timezone.utc)
        pid, vivo = None, False
        try:
            with open(FILE_PID, encoding="utf-8") as f:
                pid = int(f.read().strip() or 0)
            vivo = _processo_vivo(pid) if pid else False
        except (OSError, ValueError):
            pid = None
        stato = "ANCORA IN CORSO" if vivo else "finito"
        di(f"[r1] ultimo lancio: referto scritto {mtime:%Y-%m-%d %H:%M:%S} UTC · "
           + (f"processo {pid} {stato}" if pid else "pid non registrato"))
        try:
            with open(FILE_ESITO, encoding="utf-8", errors="replace") as f:
                coda = f.read().splitlines()[-12:]
        except OSError:
            coda = []
        if coda:
            di("  ultime righe del referto:")
            for r in coda:
                di(f"  | {r[:160]}")
    else:
        di(f"[r1] nessun lancio in sfondo registrato ({FILE_ESITO}).")
    di("-" * 74)
    piano = leggi_piano()
    for r in righe_lettura_r2(piano, leggi_unita_r2()):
        di(r)
    from scripts import gate_sul_caso as g7
    for r in g7.righe_lettura_g7((piano or {}).get("universo"), g7.leggi_unita_g7()):
        di(r)
    for r in righe_lettura(piano, leggi_unita()):
        di(r)
    return 0


def _gia_in_corso() -> None:
    di(f"[r1] un altro lancio e' gia' in corso ({FILE_LOCK}): non ne parte un altro. "
       f"L'avanzamento si legge con `replay-gate-esito`.")


def su_file(args) -> int:
    """Da `systemd-run`: lucchetto PRIMA di toccare referto e pid (come il voto
    t), poi tutto cio' che si stampa va nel referto, e in sfondo si aspetta la
    pausa del gate."""
    os.makedirs(DIR_R1, exist_ok=True)
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
        # R1 E' ATTIVO (1 ott 2026): da qui il gate salta il giro delle 12 UTC,
        # finche' le date non sono tutte fatte (bot/core/finestra_r1.py)
        with open(FILE_ATTIVO, "w", encoding="utf-8") as f:
            f.write(f"{time.time():.0f}\n")
        di(f"[r1] su file, pid {os.getpid()}, avvio "
           f"{dt.datetime.now(dt.timezone.utc):%Y-%m-%d %H:%M:%S} UTC")
        try:
            return _sotto_lucchetto(args, aspetta=True)
        except BaseException as exc:  # noqa: BLE001
            di(f"[r1] interrotto: {exc!r}")
            return 1
    finally:
        lascia_lucchetto(FILE_LOCK)


def passata(args) -> int:
    """In primo piano: stesso lucchetto, ma non si aspetta il gate."""
    if prendi_lucchetto(FILE_LOCK) is None:
        _gia_in_corso()
        return 0
    try:
        return _sotto_lucchetto(args, aspetta=False)
    finally:
        lascia_lucchetto(FILE_LOCK)


def _sotto_lucchetto(args, aspetta: bool) -> int:
    if not aspetta_il_giro(aspetta):
        return 0
    return _lancio(args)


def unita_del_piano(piano: dict | None, fatte: dict) -> dict:
    """Le sole unita' delle monete del piano (2 ott 2026: col piano ristretto
    alle monete operate, le unita' gia' fatte delle altre restano su disco ma non
    entrano nella lettura)."""
    if not piano:
        return fatte
    monete = set(piano.get("universo") or [])
    return {k: v for k, v in (fatte or {}).items() if k[1] in monete}


def monete_operate() -> list[str] | None:
    """Le monete delle coppie validate che il bot opera (registro, UNA lettura
    Firestore). None se il registro non si legge: allora il piano non cambia."""
    try:
        from bot.core.firebase_client import decode_pairs, get_firebase
        from bot.core.registry import coppie_validate
        reg = get_firebase().get_doc("strategy_registry", "validated") or {}
        coppie = coppie_validate(decode_pairs(reg.get("pairs")))
        return sorted({k.split("|", 1)[0] for k in coppie}) or None
    except Exception as exc:  # noqa: BLE001
        di(f"[r1] monete operate non lette ({str(exc)[:120]}): piano invariato")
        return None


def restringi_alle_operate(piano: dict, operate: list[str] | None) -> dict:
    """IL PIANO SULLE SOLE MONETE OPERATE (2 ott 2026, decisione del proprietario
    «limita R1 alle 71 monete»): 200 monete erano ~45,8 ore di calcolo (ops 0433),
    cioe' ~18 giorni a 2,5 ore al giorno. Una volta sola: le monete si fissano
    nel piano e non cambiano piu' (le date, i semi e le candidate restano). Le
    operate fuori dalla lista originale entrano anche loro. Pura."""
    if piano.get("filtro") == "monete_operate" or not operate:
        return piano
    prima = list(piano.get("universo") or [])
    nuovo = [c for c in prima if c in set(operate)] + [c for c in operate if c not in set(prima)]
    return {**piano, "universo": nuovo, "filtro": "monete_operate",
            "universo_prima": len(prima),
            "filtro_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")}


def carica_o_crea_piano(args, oggi: date) -> dict:
    """Il piano scritto, o uno nuovo scritto subito; dal 2 ott ristretto UNA
    volta alle monete operate (`restringi_alle_operate`)."""
    piano = leggi_piano()
    if piano and piano.get("versione") == VERSIONE:
        if SOLO_MONETE_OPERATE and piano.get("filtro") != "monete_operate":
            nuovo = restringi_alle_operate(piano, monete_operate())
            if nuovo is not piano:
                scrivi_atomico(FILE_PIANO, nuovo)
                di(f"[r1] piano ristretto alle monete operate: {len(nuovo['universo'])} monete "
                   f"(prima {nuovo['universo_prima']}); le unita' gia' fatte di queste restano")
            return nuovo
        return piano
    operate = monete_operate() if SOLO_MONETE_OPERATE else None
    universo = operate or top_symbols_by_volume(int(args.top))
    piano = crea_piano(args, oggi, universo)
    if operate:
        piano["filtro"] = "monete_operate"
    scrivi_atomico(FILE_PIANO, piano)
    di(f"[r1] piano nuovo: {len(piano['date'])} date ({piano['date'][-1]} -> "
       f"{piano['date'][0]}), {len(universo)} monete, {piano['candidate_per_data']} candidate "
       f"per data, semi = la data. Scritto {FILE_PIANO}")
    return piano


def _lancio(args) -> int:
    # la fine dati del GATE: oggi, con la stessa chiamata (`date.today()`)
    end = date.today().isoformat()
    piano = carica_o_crea_piano(args, date.today())
    workers = max(1, min(int(args.workers), n_workers()))
    deadline = time.time() + float(args.budget) if float(args.budget) > 0 else 0.0
    cfg = {k: piano[k] for k in ("interval", "start", "source", "windows", "candidate_per_data")}
    # R2 PRIMA (3 ott 2026): una volta sola, sulle monete del piano
    if R2_ATTIVO:
        fatte_r2 = leggi_unita_r2()
        lav2 = lavoro_r2(piano, fatte_r2)
        if lav2:
            di(f"[r2] taratura di R1: {len(lav2)} monete da giudicare col gate di oggi "
               f"(candidate del {R2_DATA})")
            esegui_e_salva(lav2, workers, (cfg, end, deadline, False), salva_unita_r2,
                           unita=_una_unita_r2)
            fatte_r2 = leggi_unita_r2()
        let2 = lettura_r2(piano, fatte_r2)
        if let2["completa"]:
            scrivi_atomico(FILE_R2_ESITO, let2)
        for r in righe_lettura_r2(piano, fatte_r2):
            di(r)
        if let2["completa"] and let2["passate"] >= R2_SOGLIA_SEVERO:
            try:
                os.remove(FILE_ATTIVO)
            except OSError:
                pass
            di("[r2] R1 SI FERMA (regola R2): tolto il file «attivo», il gate torna a 8 giri "
               "al giorno. Niente unita' di R1 in questo lancio.")
            return 0
    # G7 DOPO R2 (4 ott 2026): il gate sul prezzo casuale, a 1 ora, sulle monete
    # del piano (scripts/gate_sul_caso.py); finche' non e' completo
    from scripts import gate_sul_caso as g7
    if g7.G7_ATTIVO:
        monete = list(piano.get("universo") or [])
        fatte_g7 = g7.leggi_unita_g7()
        lav7 = g7.lavoro_g7(monete, fatte_g7)
        if lav7:
            di(f"[g7] il gate sul prezzo casuale: {len(lav7)} unita' (moneta x vero/caso) a "
               f"{g7.INTERVALLO}, {g7.N_CANDIDATE} candidate nuove")
            esegui_e_salva(lav7, workers, ({**cfg, "interval": g7.INTERVALLO}, end, deadline,
                                           False), g7.salva_unita_g7, unita=_una_unita_g7)
            fatte_g7 = g7.leggi_unita_g7()
        let7 = g7.lettura_g7(monete, fatte_g7)
        if let7["completa"]:
            scrivi_atomico(os.path.join(g7.dir_g7(), "esito.json"), let7)
        for r in g7.righe_lettura_g7(monete, fatte_g7):
            di(r)
    fatte = leggi_unita()
    lavoro, prova = lavoro_da_fare(piano, fatte, limit=args.limit)
    di(f"[r1] {len(lavoro)} unita' (coin x data) da fare in questo lancio"
       + (f" · PROVA PICCOLA: solo le prime {PROVA_DATE} date, poi si guardano i numeri"
          if prova else "")
       + f" · dati {piano['start']}->{end} a {piano['interval']}, tagliati in memoria")
    righe: list[dict] = []
    interrotta = None
    t0 = time.time()
    if lavoro:
        di(f"[r1] {workers} worker · budget "
           f"{'nessuno' if not deadline else f'{float(args.budget) / 3600:.1f} ore'} · "
           f"ogni unita' si scrive appena finita"
           + (" · conferme a 7 e 14 giorni ACCESE (informative)" if args.conferme else ""))
        righe, interrotta = esegui_e_salva(lavoro, workers, (cfg, end, deadline, args.conferme),
                                           salva_unita)
    stati = Counter(str(r.get("stato")) for r in righe)
    di()
    di(f"[r1] questo lancio: {len(righe)} unita' · "
       + " · ".join(f"{k} {v}" for k, v in sorted(stati.items()))
       + f" · {time.time() - t0:.0f}s")
    if stati.get("tempo"):
        di(f"  {stati['tempo']} unita' non fatte per il budget: rilancia `replay-gate` "
           f"(le fatte restano)")
    if stati.get("giro"):
        di(f"  {stati['giro']} unita' non fatte perche' il giro del gate stava per partire: "
           f"rilancia a giro finito")
    if interrotta:
        di(f"  LANCIO INTERROTTO: {interrotta}. Le unita' finite sono scritte; rilancia.")
    fatte = leggi_unita()
    resto, _ = lavoro_da_fare(piano, fatte)
    if not resto and len(date_complete(piano, fatte)) == len(piano["date"]):
        # tutte le date fatte: il gate torna a 8 giri al giorno
        try:
            os.remove(FILE_ATTIVO)
            di("[r1] TUTTE LE DATE FATTE: tolto il file «attivo», il gate torna a 8 giri "
               "al giorno")
        except OSError:
            pass
    if prova and date_complete(piano, fatte):
        di(f"  PROVA PICCOLA FINITA: guarda i numeri qui sotto; se hanno senso, rilancia "
           f"`replay-gate` per le altre date.")
    di()
    for r in righe_lettura(piano, fatte):
        di(r)
    return 1 if interrotta else 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--esito", action="store_true", help="avanzamento e lettura (sola lettura)")
    ap.add_argument("--su-file", action="store_true",
                    help="referto in data/replay_gate/ultimo.txt, aspetta il gate (per systemd-run)")
    ap.add_argument("--budget", type=float, default=BUDGET_S,
                    help="secondi di lavoro per lancio (0 = nessun limite)")
    ap.add_argument("--workers", type=int, default=WORKERS)
    ap.add_argument("--limit", type=int, default=0, help="al massimo tante unita' (prova locale)")
    ap.add_argument("--conferme", action="store_true",
                    help="anche le conferme a 7 e 14 giorni delle passate (solo informativo)")
    # solo per il PRIMO lancio (poi vale il piano)
    ap.add_argument("--candidate", type=int, default=CANDIDATE_PER_DATA)
    ap.add_argument("--top", type=int, default=TOP)
    ap.add_argument("--interval", default=settings.ORCHESTRATOR_TIMEFRAME)
    ap.add_argument("--start", default="2022-01-01")
    ap.add_argument("--source", default="auto")
    ap.add_argument("--windows", type=int, default=3)
    args = ap.parse_args(argv)
    if args.esito:
        return esito()
    if args.su_file:
        if os.getenv("TRADING_BOT_TEST_MODE"):
            di("[r1] --su-file in modalita' test: non parto (esco 0)")
            return 0
        return su_file(args)
    return passata(args)


if __name__ == "__main__":
    multiprocessing.freeze_support()
    raise SystemExit(main())
