"""Lancia la prova a placebo dell'esame di gruppo (regole in ``regole.md`` di questa cartella) e scrive una riga per
placebo e periodo in ``esiti_k<k>.jsonl`` di questa cartella.

Per ogni combinazione (6 regole x 2 direzioni x timeframe 1h e 4h: 24) e sfasamento k (0..3, piu' 4, 5... se il
riassunto lo chiede sul solo conteggio), nel periodo di costruzione e in quello di validazione:

1. legge le serie di ogni moneta SOLO con ``gruppo.CaricatoreDisco`` (regole.md, punto 2), anche per gli istanti di
   segnale: last e mark allineati con ``dati.carica_serie_allineate`` dai file mensili del timeframe (a 4 ore i file
   nativi a 4 ore, mai aggregati dall'1h), funding, mesi sotto la liquidita'; le date sono quelle di ``gruppo.py``
   (``gruppo._periodi``, ``dati.periodi_gruppo``). ``CaricatoreDisco`` ha una sola radice (schede in
   ``<radice>/campagne/GRUPPO/schede``, prezzi in ``<radice>/data/insample``): la prova gli passa la «radice di
   lettura» ``<lavoro>/radice``, fatta di due collegamenti simbolici, ``data`` verso i dati scaricati (fuori da git)
   e ``campagne/GRUPPO/schede`` verso le schede del branch principale (``radice_di_lettura``). Cosi' ``gruppo.py``
   resta com'e' e non c'e' un caricatore della prova;
2. calcola gli istanti di segnale della regola da manuale su ogni moneta (``placebo_gruppo.segnali_regola``, la
   regola della prova del 9 ottobre), senza segnali nelle prime 60 barre e, in validazione, solo nelle barre dal
   2023-01-17 (gli indicatori sono caldi: la serie parte dal primo giorno della moneta, come in ``gruppo.py``);
3. sceglie lo sfasamento comune d, uniforme fra il margine e L - margine, con seme crc32 dell'etichetta
   «GRUPPO|timeframe|regola|direzione|periodo|k» (L: barre della finestra unione sul calendario; margine: 30 giorni
   di barre, al massimo L // 4), e sposta dello stesso d, in cerchio sulla finestra unione, TUTTI gli istanti di
   tutte le monete (regole.md, punto 3.2);
4. converte gli istanti spostati in ingressi per moneta, saltando e contando quelli fuori dalla finestra della
   moneta («fuori_finestra»), senza barra nella serie («buco») o in una barra vietata («vietata»: le stesse barre
   che ``gruppo.py`` vieta alla (b), cioe' segnale non valido o non calcolabile, riscaldamento compreso, mesi sotto
   la liquidita' e, in validazione, le barre prima del 2023-01-17; la loro impronta si confronta con quella che
   riporta l'esame);
5. in costruzione ``gruppo.conta_trade_di_gruppo`` (scarto sotto 700 trade sommati o con una moneta oltre il 10%: la
   placebo non si giudica) e poi ``gruppo.esame_di_gruppo``; in validazione ``gruppo.esame_di_gruppo`` (si giudica
   con almeno 300 trade sommati: lo filtra il riassunto). Sempre con ``ingressi_placebo``, senza marcatore di
   campagna, con la cartella di lavoro ``<lavoro>/gruppo/<identita'>`` (fuori da git e da ``research/campagne/``).

Non stampa nessuna misura: solo l'avanzamento e la copertura dei dati. Le misure le calcola ``riassunto.py`` a prova
finita.

Prima di qualunque esame, a ogni lancio, il **controllo di copertura dei dati** (``controlla_copertura``): per ogni
moneta, a 1 ora e a 4 ore, barre in costruzione e in validazione, funding e candele 1d del last in entrambi i
periodi, e i mesi dei file presenti rispetto a quelli attesi dal primo mese della scheda al 2023-12; una riga
stampata per moneta. Se a una moneta manca qualcosa il lancio si ferma; nel lancio vero si ferma anche se i mesi di
candele a 1 ora e di funding non sono quelli scritti nel punto 2 delle regole.

Riproducibilita' (regole.md, punto 5). Ogni riga porta l'``identita``: le cinque impronte degli strumenti (dai file
sul disco, uguali a quelle in memoria e a quelle del punto 7), lo SHA-256 di ``placebo_gruppo.py``, di questo file e
di ``regole.md``, l'impronta dell'elenco delle monete (``monete.csv`` e posizioni), delle 80 schede e di tutti i file
di dati delle monete (``dati.calcola_impronte``); piu' gli hash dei commit. Il **lancio vero** rifiuta: ``regole.md``
ancora in BOZZA; ``placebo_gruppo.py``, ``esegui.py``, ``riassunto.py`` o ``regole.md`` non committati o con
l'ultimo commit che li tocca non ancora su ``origin/research/coordinamento``; codice non committato in
``research/src/``, ``research/config/`` o ``research/campagne/GRUPPO/`` del branch principale; un branch principale
che non contiene il commit 08e4ad95; impronte diverse da quelle compilate al punto 7 di ``regole.md``; un file di
esiti con righe di un'altra identita'; una cartella di lavoro dentro un worktree. Prima di scrivere ogni riga
l'identita' si ricalcola: se un file e' cambiato durante il lancio la riga non si scrive e il lancio si ferma.

``--funzionamento`` serve solo alle prove di funzionamento: ammette regole in bozza, codice non committato e
``--impronte-attese FILE`` (formato di ``sha256sum``), segna le righe e le scrive in
``<lavoro>/esiti_funzionamento/``, mai in questa cartella; il riassunto non da' mai un esito con quelle righe.

Ripresa: le righe gia' scritte con la stessa identita' e senza errore si saltano; una riga con ``errore`` si rifa'
al lancio dopo. ``gruppo.py`` tiene il suo file di avanzamento per esame: un esame interrotto riprende dalle monete
gia' fatte.

Uso (da qualunque cartella; il branch principale e' il primo worktree di ``git worktree list``, oppure
``PLACEBO_PRINCIPALE``):

    python research/taratura/placebo_gruppo/esegui.py --radice-dati <radice con data/insample/> \\
        [--lavoro <cartella fuori da git>] [--k 0 1 2 3] [--massimo-minuti 100] [--processi 4] \\
        [--solo-copertura] [--funzionamento [--impronte-attese <file>]]

Si lancia in pezzi: con ``--massimo-minuti`` non parte un nuovo esame dopo quel tempo (quello in corso finisce:
a 1 ora un esame puo' durare decine di minuti, stima non misurata) e il codice d'uscita e' 3; rilanciato,
riprende da solo. Codice d'uscita 0: tutto fatto (o copertura controllata con ``--solo-copertura``); 2: tre errori
di fila (fermo); 3: fermato per il tempo; 4: un file dell'identita' e' cambiato durante il lancio (fermo, la riga
non e' scritta).
"""

from __future__ import annotations

import argparse
import bisect
import hashlib
import json
import math
import multiprocessing
import os
import re
import subprocess
import sys
import time
import traceback
import zlib
from concurrent.futures import ProcessPoolExecutor
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from types import SimpleNamespace
from typing import Callable, Dict, List, Mapping, Optional, Sequence, Tuple

import numpy as np

QUI = Path(__file__).resolve().parent
#: il commit degli strumenti di gruppo da cui parte la prova (il branch principale deve contenerlo)
COMMIT_MINIMO = "08e4ad95"


def trova_principale() -> Path:
    """La radice del branch principale: ``PLACEBO_PRINCIPALE`` o il primo worktree di ``git worktree list``."""
    variabile = os.environ.get("PLACEBO_PRINCIPALE")
    if variabile:
        radice = Path(variabile).resolve()
    else:
        uscita = subprocess.run(["git", "-C", str(QUI), "worktree", "list", "--porcelain"], capture_output=True,
                                text=True, check=True).stdout
        righe = [r[len("worktree "):] for r in uscita.splitlines() if r.startswith("worktree ")]
        if not righe:
            raise RuntimeError("git worktree list non elenca nessun worktree: serve PLACEBO_PRINCIPALE")
        radice = Path(righe[0]).resolve()  # il worktree principale e' sempre il primo
    if not (radice / "research" / "src" / "gruppo.py").is_file():
        raise RuntimeError(f"{radice} non ha research/src/gruppo.py: non e' il branch principale con gli strumenti")
    return radice


PRINCIPALE = trova_principale()


def _metti_nel_percorso() -> None:
    """``research`` dal branch principale (mai dal worktree di coordinamento) e ``placebo_gruppo`` da questa cartella."""
    for voce in (str(PRINCIPALE), str(QUI)):
        while voce in sys.path:
            sys.path.remove(voce)
    sys.path.insert(0, str(QUI))
    sys.path.insert(0, str(PRINCIPALE))
    gia = sys.modules.get("research")
    if gia is not None and Path(gia.__file__).resolve().parent != PRINCIPALE / "research":
        raise ImportError(f"research e' gia' importato da {gia.__file__}, non dal branch principale {PRINCIPALE}")


_metti_nel_percorso()

from research.src import dati, gruppo, motore, statistica  # noqa: E402
from research.src.guardiano import MONETA_RIFERIMENTO, MONETE_GRUPPO  # noqa: E402

import placebo_gruppo as PG  # noqa: E402

for _modulo, _cartella in ((gruppo, PRINCIPALE / "research" / "src"), (PG, QUI)):
    if Path(_modulo.__file__).resolve().parent != _cartella:
        raise ImportError(f"{_modulo.__name__} viene da {_modulo.__file__}, non da {_cartella}")

MODULO = QUI / "placebo_gruppo.py"
REGOLE_DELLA_PROVA = QUI / "regole.md"
#: versione del formato delle righe di esiti (2: identita' con regole, monete, schede e dati; 10 ottobre 2026)
FORMATO = 2
K_DELLA_PROVA = (0, 1, 2, 3)
PERIODI = ("costruzione", "validazione")
COMBINAZIONI = tuple((tf, r, d) for tf in PG.TIMEFRAME for r in PG.REGOLE for d in PG.DIREZIONI)
SALTI = ("fuori_finestra", "buco", "vietata")
#: il margine dello sfasamento comune (regole.md, punto 3.2): 30 giorni di barre, al massimo L // 4
MARGINE_GIORNI = 30
GIORNO_MS = 86_400_000
#: i file della prova che il lancio vero vuole committati e pushati (regole.md, intestazione e punto 5)
FILE_DELLA_PROVA = ("placebo_gruppo.py", "esegui.py", "riassunto.py", "regole.md")
#: dove devono stare, pushati, prima del lancio vero
RAMO_REMOTO = "origin/research/coordinamento"
#: il codice della prova che entra nell'identita' di una riga (con regole.md)
CODICE_DELLA_PROVA = ("placebo_gruppo.py", "esegui.py")
#: dove il lancio vero scrive gli esiti (regole.md, punto 5: un file per sfasamento, in questa cartella)
ESITI_DEFINITIVI = QUI
#: la cartella di lavoro predefinita (radice di lettura, file di avanzamento e dei trade di gruppo.py): accanto al
#: worktree di coordinamento, fuori da git
LAVORO_PREDEFINITO = Path(os.environ.get("PLACEBO_LAVORO") or (QUI.parents[2].parent / "placebo_gruppo_lavoro"))
#: le schede del branch principale e l'elenco delle monete
SCHEDE_DEL_PRINCIPALE = PRINCIPALE / "research" / dati.CARTELLA_SCHEDE_GRUPPO
MONETE_DEL_PRINCIPALE = PRINCIPALE / MONETE_GRUPPO
#: le serie di file che la prova legge (regole.md, punto 2): (tipo, intervallo)
SERIE_DEI_FILE = (("klines", "1h"), ("markPriceKlines", "1h"), ("klines", "4h"), ("markPriceKlines", "4h"),
                  ("klines", "1d"), ("fundingRate", None))
#: i mesi scaricati il 10 ottobre per le 80 monete (regole.md, punto 2)
MESI_DICHIARATI = {"klines/1h": 3061, "markPriceKlines/1h": 3061, "fundingRate": 3044}
#: una regola per tipo di uscita: il segnale non valido dipende solo da direzione e uscita
REGOLA_DELL_USCITA = {u: next(r for r in PG.REGOLE if PG.USCITA_DELLA_REGOLA[r] == u) for u in PG.USCITE}


# ---------------------------------------------------------------------------
# Piccoli attrezzi
# ---------------------------------------------------------------------------


def sha256_file(percorso: Path) -> str:
    sha = hashlib.sha256()
    with open(percorso, "rb") as flusso:
        for blocco in iter(lambda: flusso.read(1 << 20), b""):
            sha.update(blocco)
    return sha.hexdigest()


def _sha256_canonico(valore: object) -> str:
    return hashlib.sha256(json.dumps(valore, sort_keys=True, separators=(",", ":"),
                                     ensure_ascii=False).encode("utf-8")).hexdigest()


def _git(cartella: Path, *argomenti: str) -> str:
    return subprocess.run(["git", "-C", str(cartella), *argomenti], capture_output=True, text=True, check=True).stdout


def _mappa(funzione: Callable, compiti: Sequence, processi: int) -> list:
    """``funzione`` su ogni compito, nell'ordine; con ``processi`` > 1 in processi ``spawn`` (come ``gruppo.py``)."""
    if processi <= 1 or len(compiti) <= 1:
        return [funzione(c) for c in compiti]
    with ProcessPoolExecutor(max_workers=min(processi, len(compiti)),
                             mp_context=multiprocessing.get_context("spawn")) as esecutore:
        return list(esecutore.map(funzione, compiti))


# ---------------------------------------------------------------------------
# La radice di lettura di gruppo.CaricatoreDisco (regole.md, punto 2)
# ---------------------------------------------------------------------------


def _collegamento(percorso: Path, bersaglio: Path) -> None:
    """Crea il collegamento simbolico ``percorso`` -> ``bersaglio``; se c'e' gia' deve puntare li' (SystemExit se no)."""
    bersaglio = Path(bersaglio).resolve()
    if percorso.is_symlink():
        if percorso.resolve() != bersaglio:
            raise SystemExit(f"{percorso} punta a {percorso.resolve()}, non a {bersaglio}: usa un'altra --lavoro")
        return
    if percorso.exists():
        raise SystemExit(f"{percorso} esiste e non e' un collegamento simbolico: usa un'altra --lavoro")
    percorso.parent.mkdir(parents=True, exist_ok=True)
    percorso.symlink_to(bersaglio, target_is_directory=True)


def radice_di_lettura(lavoro: Path, radice_dati: Path, schede: Path = SCHEDE_DEL_PRINCIPALE) -> Path:
    """La radice che si passa a ``gruppo.CaricatoreDisco``: ``<lavoro>/radice``.

    ``CaricatoreDisco`` ha UNA radice: legge le schede in ``<radice>/campagne/GRUPPO/schede/`` e i prezzi in
    ``<radice>/data/insample/``. I prezzi della prova stanno in ``radice_dati`` (fuori da git), le schede nel branch
    principale: la radice di lettura e' fatta di due collegamenti simbolici, ``data`` -> ``<radice_dati>/data`` e
    ``campagne/GRUPPO/schede`` -> ``schede``. E' il modo meno invasivo: ``gruppo.py`` non cambia, la prova non ha un
    caricatore suo, i dati e il branch principale non si toccano. Senza ``vault/APERTURA.md`` il vault resta chiuso
    (``dati.controlla_vault``).
    """
    radice_dati = Path(radice_dati).resolve()
    if not (radice_dati / "data" / "insample").is_dir():
        raise SystemExit(f"{radice_dati} non contiene data/insample/: serve la radice dei dati scaricati")
    if not Path(schede).is_dir():
        raise SystemExit(f"le schede del gruppo non ci sono in {schede}")
    radice = Path(lavoro).resolve() / "radice"
    _collegamento(radice / "data", radice_dati / "data")
    _collegamento(radice / dati.CARTELLA_SCHEDE_GRUPPO, Path(schede))
    if (radice / "vault").exists():
        raise SystemExit(f"{radice / 'vault'} non deve esistere: la prova non tocca il vault")
    return radice


def controlla_lavoro(lavoro: Path, vietate: Sequence[Path]) -> Path:
    """La cartella di lavoro: fuori da ogni worktree (i file di gruppo.py hanno numeri parziali). SystemExit se no."""
    cartella = Path(lavoro).resolve()
    for vietata in vietate:
        vietata = Path(vietata).resolve()
        if cartella == vietata or vietata in cartella.parents:
            raise SystemExit(f"la cartella di lavoro {cartella} sta dentro {vietata}: va fuori da git (--lavoro)")
    return cartella


# ---------------------------------------------------------------------------
# Lo sfasamento comune (regole.md, punto 3.2)
# ---------------------------------------------------------------------------


def etichetta(timeframe: str, regola: str, direzione: str, periodo: str, k: int) -> str:
    return f"GRUPPO|{timeframe}|{regola}|{direzione}|{periodo}|{int(k)}"


def seme_di(testo: str) -> int:
    """Il seme di una placebo: crc32 dell'etichetta (niente dipende dall'ordine di esecuzione)."""
    return zlib.crc32(testo.encode("utf-8"))


def finestra_unione(periodi: Mapping, periodo: str, monete: Sequence[str]) -> Tuple[int, int]:
    """[inizio, fine] in ms (fine compresa) della finestra unione: in costruzione dal primo giorno piu' antico delle
    monete al taglio, in validazione dal 2023-01-17 al 2023-12-31."""
    if periodo == "costruzione":
        return min(periodi["monete"][s]["inizio_ts"] for s in monete), int(periodi["fine_costruzione_ts"])
    if periodo == "validazione":
        return (int(periodi["inizio_validazione_ts"]),
                dati.ms_da_data(periodi["fine_validazione"] + timedelta(days=1)) - 1)
    raise ValueError(f"periodo sconosciuto: {periodo!r}")


def barre_e_margine(inizio: int, fine: int, ms: int) -> Tuple[int, int]:
    """L (barre della finestra contate sul calendario) e il margine (30 giorni di barre, al massimo L // 4)."""
    durata = fine + 1 - inizio
    giorni = MARGINE_GIORNI * GIORNO_MS
    if durata <= 0 or durata % ms or giorni % ms:
        raise ValueError(f"finestra {inizio}-{fine} o margine non fatti di barre intere da {ms} ms")
    L = durata // ms
    margine = min(giorni // ms, L // 4)
    if margine < 1:
        raise ValueError(f"finestra di {L} barre troppo corta per uno sfasamento")
    return L, margine


def sfasamento(testo: str, L: int, margine: int) -> int:
    """d uniforme fra ``margine`` e ``L - margine`` (compresi), con il seme dell'etichetta."""
    if not 1 <= margine <= L - margine:
        raise ValueError(f"margine {margine} non valido per {L} barre")
    return int(np.random.default_rng(seme_di(testo)).integers(margine, L - margine + 1))


def sposta_istanti(istanti_per_moneta: Mapping[str, Sequence[int]], inizio: int, L: int, ms: int,
                   d: int) -> Dict[str, List[int]]:
    """Ogni istante di ogni moneta spostato di ``d`` barre in cerchio sulla finestra unione [inizio, inizio + L·ms).

    Lo stesso ``d`` per tutte le monete: due istanti uguali su monete diverse restano uguali. ValueError per un
    istante fuori dalla finestra o non allineato alle barre.
    """
    spostati: Dict[str, List[int]] = {}
    for simbolo in sorted(istanti_per_moneta):
        nuovi = []
        for ts in istanti_per_moneta[simbolo]:
            scarto = int(ts) - inizio
            if scarto < 0 or scarto % ms or scarto // ms >= L:
                raise ValueError(f"{simbolo}: l'istante {ts} non e' una barra della finestra unione")
            nuovi.append(inizio + ((scarto // ms + d) % L) * ms)
        spostati[simbolo] = nuovi
    return spostati


def ingressi_per_moneta(spostati: Mapping[str, Sequence[int]], monete: Mapping[str, Mapping], chiave_vietate: str,
                        ms: int) -> Tuple[Dict[str, List[int]], Dict[str, object]]:
    """Gli istanti spostati che diventano ingressi di ogni moneta, e i saltati contati per motivo.

    ``monete[s]``: ``finestra`` [da, a] (ms, compresi), ``ts`` (le barre della serie, crescenti) e ``vietate``
    {chiave: {``maschera``: un byte per barra, 1 se vietata}}. Un istante si salta se la barra che apre li' non sta
    tutta nella finestra della moneta («fuori_finestra»), se la serie non ha quella barra («buco») o se la barra e'
    vietata («vietata»), in quest'ordine.
    """
    ingressi: Dict[str, List[int]] = {}
    saltati = {motivo: 0 for motivo in SALTI}
    per_moneta: Dict[str, int] = {}
    for simbolo in sorted(spostati):
        info = monete[simbolo]
        da, a = info["finestra"]
        ts_serie = info["ts"]
        maschera = info["vietate"][chiave_vietate]["maschera"]
        tenuti = []
        for ts in spostati[simbolo]:
            if ts < da or ts + ms - 1 > a:
                saltati["fuori_finestra"] += 1
                continue
            j = int(np.searchsorted(ts_serie, ts))
            if j >= len(ts_serie) or int(ts_serie[j]) != ts:
                saltati["buco"] += 1
                continue
            if maschera[j]:
                saltati["vietata"] += 1
                continue
            tenuti.append(int(ts))
        ingressi[simbolo] = sorted(tenuti)
        if tenuti:
            per_moneta[simbolo] = len(tenuti)
    conteggi = {"ingressi": sum(per_moneta.values()), "monete_con_ingressi": len(per_moneta), "saltati": saltati,
                "ingressi_per_moneta": per_moneta}
    return ingressi, conteggi


# ---------------------------------------------------------------------------
# Il controllo di copertura dei dati (prima del lancio)
# ---------------------------------------------------------------------------


def mesi_dei_file(simbolo: str, primo_mese: date, radice: Path) -> Dict[str, Dict[str, object]]:
    """Per ogni serie di ``SERIE_DEI_FILE``: i mesi attesi (dal primo mese della scheda al 2023-12), quanti file ci sono
    e quali mesi mancano (``dati.percorso_mese``, i percorsi del caricatore)."""
    mesi = list(dati.mesi_del_periodo(primo_mese, dati.FINE_IN_SAMPLE))
    risultato = {}
    for tipo, intervallo in SERIE_DEI_FILE:
        mancanti = [f"{a:04d}-{m:02d}" for a, m in mesi
                    if not dati.percorso_mese(simbolo, tipo, intervallo, a, m, radice).is_file()]
        nome = tipo if intervallo is None else f"{tipo}/{intervallo}"
        risultato[nome] = {"attesi": len(mesi), "presenti": len(mesi) - len(mancanti), "mancanti": mancanti}
    return risultato


def copertura_moneta(compito: Mapping) -> Dict[str, object]:
    """I dati di una moneta come li vede ``gruppo.py`` (``gruppo._carica_moneta`` con il caricatore della prova), per
    timeframe e periodo: barre, regolamenti di funding, giorni con le candele 1d del last, mesi sotto la liquidita'."""
    caricatore, simbolo = compito["caricatore"], compito["simbolo"]
    date_periodo = {"costruzione": (compito["inizio"], compito["fine_costruzione"]),
                    "validazione": (compito["inizio_validazione"], compito["fine_validazione"])}
    periodi = {}
    for timeframe in PG.TIMEFRAME:
        for periodo, (da, a) in date_periodo.items():
            serie = gruppo._carica_moneta(caricatore, simbolo, timeframe, date.fromisoformat(da), date.fromisoformat(a))
            periodi[f"{timeframe}|{periodo}"] = {"barre": len(serie["candele"]), "funding": len(serie["funding"]),
                                                 "giorni_1d": serie["giorni_1d"],
                                                 "mesi_sotto_liquidita": len(serie["mesi_sotto_liquidita"])}
    radice = getattr(caricatore, "radice", None)
    return {"simbolo": simbolo, "primo_mese": compito["primo_mese"], "periodi": periodi,
            "file": None if radice is None else mesi_dei_file(simbolo, date.fromisoformat(compito["primo_mese"]),
                                                              Path(radice))}


def problemi_di_copertura(tabella: Mapping[str, Mapping]) -> List[str]:
    """Le mancanze che fermano il lancio: una moneta senza barre a 1 ora o a 4 ore in un periodo, senza funding o senza
    candele 1d del last in un periodo (come ``gruppo._controlla_dati_in_campagna``, qui per entrambi i periodi)."""
    problemi = []
    for simbolo in sorted(tabella):
        for chiave, voce in tabella[simbolo]["periodi"].items():
            timeframe, periodo = chiave.split("|")
            if not voce["barre"]:
                problemi.append(f"{simbolo}: nessuna barra {timeframe} in {periodo}")
            if timeframe == PG.TIMEFRAME[0]:  # funding e 1d non dipendono dal timeframe
                if not voce["funding"]:
                    problemi.append(f"{simbolo}: nessun regolamento di funding in {periodo}")
                if not voce["giorni_1d"]:
                    problemi.append(f"{simbolo}: nessuna candela 1d del last in {periodo}")
    return problemi


def totali_dei_file(tabella: Mapping[str, Mapping]) -> Dict[str, Dict[str, int]]:
    totali: Dict[str, Dict[str, int]] = {}
    for voce in tabella.values():
        for nome, conto in (voce.get("file") or {}).items():
            t = totali.setdefault(nome, {"attesi": 0, "presenti": 0})
            t["attesi"] += conto["attesi"]
            t["presenti"] += conto["presenti"]
    return totali


def riga_di_copertura(voce: Mapping) -> str:
    p = voce["periodi"]
    parti = [f"{voce['simbolo']} (dal {voce['primo_mese']}):"]
    for timeframe in PG.TIMEFRAME:
        parti.append(f"{timeframe} barre {p[f'{timeframe}|costruzione']['barre']}/{p[f'{timeframe}|validazione']['barre']}")
    prima = PG.TIMEFRAME[0]
    parti.append(f"funding {p[f'{prima}|costruzione']['funding']}/{p[f'{prima}|validazione']['funding']}")
    parti.append(f"giorni 1d {p[f'{prima}|costruzione']['giorni_1d']}/{p[f'{prima}|validazione']['giorni_1d']}")
    parti.append(f"mesi sotto la liquidita' {p[f'{prima}|costruzione']['mesi_sotto_liquidita']}/"
                 f"{p[f'{prima}|validazione']['mesi_sotto_liquidita']}")
    if voce.get("file"):
        file = []
        for nome, conto in voce["file"].items():
            testo = f"{nome} {conto['presenti']}/{conto['attesi']}"
            if conto["mancanti"]:
                testo += f" (mancano {', '.join(conto['mancanti'])})"
            file.append(testo)
        parti.append("file " + "; ".join(file))
    return " ".join(parti[:1]) + " " + ", ".join(parti[1:])


def controlla_copertura(caricatore, monete=None, processi: int = 1, severa: bool = True,
                        stampa: Callable[[str], None] = print) -> Dict[str, object]:
    """Il controllo di copertura dei dati prima del lancio, con una riga stampata per moneta.

    Barre in costruzione / in validazione a 1 ora e a 4 ore, funding e giorni 1d per periodo (costruzione /
    validazione), mesi sotto la liquidita', file presenti / attesi per serie con i mesi che mancano. SystemExit se a
    una moneta manca qualcosa (``problemi_di_copertura``) o, con ``severa``, se i totali dei mesi di candele a 1 ora e
    di funding non sono quelli del punto 2 delle regole (``MESI_DICHIARATI``). Ritorna la tabella e i totali.
    """
    posizioni, ufficiali = gruppo._monete_con_posizione(monete)
    periodi = gruppo._periodi(caricatore, posizioni, ufficiali, gruppo.regole_del_gruppo())
    compiti = [{"caricatore": caricatore, "simbolo": s,
                "primo_mese": caricatore.scheda(s)["primo_mese"].isoformat(),
                "inizio": periodi["monete"][s]["inizio"].isoformat(),
                "fine_costruzione": periodi["fine_costruzione"].isoformat(),
                "inizio_validazione": periodi["inizio_validazione"].isoformat(),
                "fine_validazione": periodi["fine_validazione"].isoformat()} for s in sorted(posizioni)]
    tabella = {voce["simbolo"]: voce for voce in _mappa(copertura_moneta, compiti, processi)}
    stampa("copertura dei dati (barre costruzione/validazione; funding, giorni 1d e mesi sotto la liquidita' "
           "costruzione/validazione; file presenti/attesi):")
    for simbolo in sorted(tabella):
        stampa("  " + riga_di_copertura(tabella[simbolo]))
    totali = totali_dei_file(tabella)
    if totali:
        stampa("totali dei file: " + "; ".join(f"{nome} {t['presenti']}/{t['attesi']}" for nome, t in totali.items()))
    problemi = problemi_di_copertura(tabella)
    diversi = [f"{nome}: {totali.get(nome, {}).get('presenti')} mesi, il punto 2 delle regole ne dice {atteso}"
               for nome, atteso in MESI_DICHIARATI.items() if totali and totali.get(nome, {}).get("presenti") != atteso]
    if problemi:
        raise SystemExit("copertura dei dati incompleta, nessun esame parte:\n" + "\n".join(problemi))
    if diversi:
        if severa:
            raise SystemExit("i dati non sono quelli descritti nel punto 2 delle regole:\n" + "\n".join(diversi))
        stampa("ATTENZIONE (solo funzionamento): " + "; ".join(diversi))
    stampa(f"copertura: {len(tabella)} monete, tutte con barre a 1 ora e a 4 ore, funding e candele 1d nei due periodi")
    return {"monete": len(tabella), "totali": totali, "tabella": tabella}


# ---------------------------------------------------------------------------
# La preparazione di un timeframe e di un periodo (una moneta per processo)
# ---------------------------------------------------------------------------


def prepara_moneta(compito: Mapping) -> Dict[str, object]:
    """Serie, istanti di segnale di ogni regola e barre vietate di una moneta, come le vede ``gruppo.py``.

    La serie viene da ``gruppo._carica_moneta`` con il caricatore della prova (``gruppo.CaricatoreDisco``): la stessa
    chiamata, con le stesse date, dei pezzi dell'esame.
    """
    caricatore, simbolo, timeframe = compito["caricatore"], compito["simbolo"], compito["timeframe"]
    inizio, fine = date.fromisoformat(compito["inizio"]), date.fromisoformat(compito["fine"])
    serie = gruppo._carica_moneta(caricatore, simbolo, timeframe, inizio, fine)
    candele = serie["candele"]
    ts = np.array([c.ts for c in candele], dtype=np.int64)
    parametri = gruppo.parametri_moneta(compito["slippage"])
    conteggio = compito["inizio_conteggio_ts"]
    indice = 0 if conteggio is None else bisect.bisect_left(ts.tolist(), conteggio)
    liquidita = [tuple(x) for x in dati.barre_vietate_liquidita(candele, serie["mesi_sotto_liquidita"])]
    prima = [(0, indice)] if indice > 0 else []
    ctx = SimpleNamespace(timeframe=timeframe, ms_per_barra=dati.durata_intervallo(timeframe))
    vietate = {}
    for direzione in PG.DIREZIONI:
        for uscita in PG.USCITE:
            p = {"regola": REGOLA_DELL_USCITA[uscita], "direzione": direzione}
            non_valide = [tuple(x) for x in motore.barre_vietate_segnale_non_valido(
                candele, PG.crea_segnale(ctx, p), parametri)]
            maschera = gruppo._bandierine(len(candele), non_valide + liquidita + prima)  # come _Preparato.barre_vietate
            vietate[f"{direzione}|{uscita}"] = {"maschera": bytes(maschera),
                                                "impronta": hashlib.sha256(bytes(maschera)).hexdigest(),
                                                "totale": sum(maschera)}
    segnali = {}
    for regola in PG.REGOLE:
        for direzione in PG.DIREZIONI:
            scatta = PG.segnali_regola(candele, regola, direzione)
            scatta[:max(PG.RISCALDAMENTO, indice)] = False
            segnali[f"{regola}|{direzione}"] = ts[scatta].tolist()
    return {"simbolo": simbolo, "ts": ts, "finestra": tuple(compito["finestra"]), "barre": len(candele),
            "barre_nel_periodo": len(candele) - indice, "indice_conteggio": indice, "vietate": vietate,
            "segnali": segnali}


def prepara(timeframe: str, periodo: str, caricatore, monete=None, processi: int = 1) -> Dict[str, object]:
    """Le monete, i periodi (quelli di ``gruppo.py``) e i dati di ``prepara_moneta`` per ogni moneta."""
    posizioni, ufficiali = gruppo._monete_con_posizione(monete)
    periodi = gruppo._periodi(caricatore, posizioni, ufficiali, gruppo.regole_del_gruppo())
    ms = dati.durata_intervallo(timeframe)
    inizio, fine = finestra_unione(periodi, periodo, sorted(posizioni))
    L, margine = barre_e_margine(inizio, fine, ms)
    fine_periodo = periodi["fine_costruzione"] if periodo == "costruzione" else periodi["fine_validazione"]
    compiti = []
    for simbolo in sorted(posizioni):
        date_s = periodi["monete"][simbolo]
        finestra = ((date_s["inizio_ts"], int(periodi["fine_costruzione_ts"])) if periodo == "costruzione"
                    else (inizio, fine))
        compiti.append({"caricatore": caricatore, "simbolo": simbolo, "timeframe": timeframe,
                        "inizio": date_s["inizio"].isoformat(), "fine": fine_periodo.isoformat(),
                        "inizio_conteggio_ts": None if periodo == "costruzione" else int(periodi["inizio_validazione_ts"]),
                        "slippage": caricatore.scheda(simbolo)["slippage_per_lato"], "finestra": finestra})
    risultati = _mappa(prepara_moneta, compiti, processi)
    return {"timeframe": timeframe, "periodo": periodo, "ms": ms, "finestra_unione": (inizio, fine), "L": L,
            "margine": margine, "monete": {r["simbolo"]: r for r in risultati}, "argomento_monete": monete,
            "fine_costruzione": periodi["fine_costruzione"].isoformat()}


# ---------------------------------------------------------------------------
# Una placebo in un periodo
# ---------------------------------------------------------------------------


def id_esame(timeframe: str, regola: str, direzione: str, k: int) -> str:
    return f"PG-{timeframe}-{regola}-{direzione}-k{int(k)}"


def _somma_senza_barra(per_moneta: Mapping) -> int:
    return sum(int((v.get("ingressi_dati") or {}).get("senza_barra", 0)) for v in per_moneta.values())


def t_con_pavimento(contro_b: Mapping, pavimento: float) -> Optional[float]:
    """Il t del confronto con la (b) con un altro pavimento delle sfasate, con l'aritmetica di
    ``statistica.contro_baseline``: errore del candidato = il piu' alto fra l'errore del bootstrap, il pavimento della
    (b) e ``pavimento``; t = differenza / radice(errore del candidato² + errore della (b)²). None se il confronto non
    e' valutabile o manca un numero. Solo per la misura informativa della sfasata piu' vicina."""
    chiavi = ("differenza", "errore_candidato_senza_pavimento", "errore_minimo_baseline", "baseline_errore_standard")
    if not contro_b.get("valutabile") or any(contro_b.get(c) is None for c in chiavi):
        return None
    valori = [float(contro_b[c]) for c in chiavi]
    if not all(math.isfinite(v) for v in valori):
        return None
    differenza, bootstrap, pavimento_b, errore_b = valori
    errore_c = max(bootstrap, max(pavimento_b, float(pavimento)))
    if errore_c == 0.0:
        return None
    return differenza / math.sqrt(errore_c ** 2 + errore_b ** 2)


def sfasata_piu_vicina(sfasamenti: Sequence[int], L: int, d: int, m: Sequence[Optional[float]], n: Sequence[int],
                       n_trade: int, contro_b: Optional[Mapping]) -> Dict[str, object]:
    """La sfasata del pavimento che rimette gli ingressi della placebo piu' vicino a dove la regola li ha calcolati
    (d_s piu' vicino a L - d in cerchio), e il pavimento e il t senza di lei. Solo informativa (regole.md, punto 8)."""
    bersaglio = (L - d) % L
    distanze = [min((s - bersaglio) % L, (bersaglio - s) % L) for s in sfasamenti]
    i = int(min(range(len(sfasamenti)), key=lambda j: (distanze[j], j)))
    valori = [x for x in m if x is not None]
    media = float(np.mean(valori)) if valori else None
    sd = float(np.std(valori, ddof=1)) if len(valori) >= 2 else None
    senza = statistica.pavimento_sfasamento([x for j, x in enumerate(m) if j != i],
                                            [x for j, x in enumerate(n) if j != i], n_trade)
    t_senza = uguale = None
    if contro_b is not None and senza["valutabile"]:
        t_attuale = t_con_pavimento(contro_b, float(contro_b.get("pavimento_minimo") or 0.0))
        uguale = t_attuale is not None and t_attuale == contro_b.get("t")
        if uguale:
            t_senza = t_con_pavimento(contro_b, float(senza["pavimento"]))
    return {"indice": i, "d_s": int(sfasamenti[i]), "distanza_barre": int(distanze[i]),
            "m_s": m[i], "scarto_in_sd": None if (m[i] is None or not sd) else (float(m[i]) - media) / sd,
            "pavimento": senza["pavimento"], "t": t_senza, "ricalcolo_uguale": uguale}


def sfasate_dall_avanzamento(esame: Mapping, ms: int, d: Optional[int] = None,
                             finestra_placebo: Optional[Sequence[int]] = None) -> Optional[Dict[str, object]]:
    """M'(s) delle strategie sfasate dell'esame, rilette dal suo file di avanzamento, e il percentile del candidato.

    Le righe ``sfasate`` con l'impronta dell'esame e la condizione della sua griglia (ricostruita dalla chiave
    ``pavimento_sfasate``, come in ``gruppo._griglia``); M'(s) e n'(s) con ``statistica.medie_sfasate``, la lettura
    di ``gruppo.py``. Il pavimento ricalcolato deve essere quello dell'esame (``pavimento_uguale``).
    ``percentile``: quota per 100 delle M'(s) sotto l'R medio; ``sopra_p90``: R medio sopra il 90° percentile.
    Con ``d`` e la finestra unione della placebo uguale a quella del pavimento, ``senza_la_piu_vicina``
    (``sfasata_piu_vicina``).
    """
    pav = esame.get("pavimento_sfasate")
    if not pav:
        return None
    griglia = statistica.griglia_sfasamenti(pav["L"], pav["margine_richiesto"], pav["sfasamenti_richiesti"])
    if griglia["numero"] != pav["numero"] or griglia["margine"] != pav["margine"]:
        raise RuntimeError("la griglia delle sfasate ricostruita non e' quella dell'esame")
    condizione = gruppo._sha256_testo(gruppo._canonico({"finestra": list(pav["finestra_unione"]), "ms": ms,
                                                        "sfasamenti": griglia["sfasamenti"]}))
    impronta = esame["impronte"]["esame"]
    per_moneta: Dict[str, list] = {}
    with open(esame["file"]["avanzamento"], "rb") as flusso:
        for riga in flusso:
            if b'"sfasate"' not in riga:
                continue
            try:
                voce = json.loads(riga)
            except json.JSONDecodeError:
                continue
            if (voce.get("formato") != gruppo.FORMATO_AVANZAMENTO or voce.get("impronta") != impronta
                    or voce.get("pezzo") != "sfasate" or voce.get("condizione") != condizione):
                continue
            simbolo, per_s = voce["simbolo"], voce["dati"]["per_s"]
            if per_moneta.get(simbolo, per_s) != per_s:
                raise RuntimeError(f"due righe diverse delle sfasate di {simbolo} nell'avanzamento")
            per_moneta[simbolo] = per_s
    attese = sorted(s for s, v in esame["per_moneta"].items() if v["trade"] > 0)
    if sorted(per_moneta) != attese:
        raise RuntimeError(f"sfasate nell'avanzamento per {sorted(per_moneta)}, attese per {attese}")
    m, n = statistica.medie_sfasate(per_moneta, pav["numero"])
    n_trade = int(esame["metriche"]["n_trade"])
    ricalcolato = statistica.pavimento_sfasamento(m, n, n_trade)
    valori = [x for x in m if x is not None]
    r_medio = float(esame["metriche"]["r_medio"])
    p90 = float(np.percentile(valori, 90)) if valori else None
    vicina = None
    if d is not None and finestra_placebo is not None and list(finestra_placebo) == list(pav["finestra_unione"]):
        b = esame.get("baseline_b")
        vicina = sfasata_piu_vicina(griglia["sfasamenti"], int(pav["L"]), int(d), m, n, n_trade,
                                    None if b is None else {k: b.get(k) for k in _CHIAVI_CONTRO_B})
    return {"con_trade": len(valori), "media": float(np.mean(valori)) if valori else None,
            "percentile": statistica.percentile_del_candidato(r_medio, valori) if valori else None,
            "p90": p90, "sopra_p90": None if p90 is None else bool(r_medio > p90),
            "pavimento_uguale": ricalcolato["pavimento"] == pav["pavimento"],
            "senza_la_piu_vicina": vicina}


_CHIAVI_CONTRO_B = ("valutabile", "p_value", "t", "netta", "gradi_liberta", "soglia", "differenza",
                    "errore_differenza", "errore_candidato", "errore_minimo", "origine_pavimento",
                    "errore_minimo_baseline", "pavimento_minimo", "errore_candidato_senza_pavimento", "n_blocchi",
                    "baseline_media", "baseline_errore_standard", "motivo_non_valutabile")
_CHIAVI_PAVIMENTO = ("pavimento", "valutabile", "media_r_sfasate", "sfasate", "sfasate_con_trade", "L", "margine",
                     "margine_richiesto", "numero", "finestra_unione", "ingressi_totali", "saltati_totali",
                     "segnali_coincidenti", "quota_trade_mediana", "durata_massima_barre")


def estrai_esame(esame: Mapping, impronte_vietate: Mapping[str, str], ms: int, d: Optional[int] = None,
                 finestra_placebo: Optional[Sequence[int]] = None) -> Dict[str, object]:
    """I numeri dell'esame che la riga tiene (punto 5 delle regole), dalle chiavi del risultato di ``gruppo.py``.

    ``contro_b``: il confronto con la (b) con il pavimento delle sfasate (p_value, t, netta, valutabile, gradi...);
    ``senza_pavimento``: lo stesso senza il pavimento delle sfasate (``senza_pavimento_sfasate`` dell'esame; i
    gradi sono gli stessi, ``n_blocchi`` - 1). ``pavimento_decide``: il pavimento delle sfasate e' l'errore del
    candidato (piu' alto del pavimento della (b) e dell'errore del bootstrap). ``vietate_diverse``: le monete con
    trade le cui barre vietate (impronta della maschera) non sono quelle calcolate qui per i salti.
    ``impronta_variante`` e ``impronte_strumenti``: quelle dell'esame, che il lancio confronta con l'identita'.
    """
    metriche = esame["metriche"]
    per_moneta = esame["per_moneta"]
    b = esame.get("baseline_b")
    contro_b = senza = None
    decide = False
    if b is not None:
        contro_b = {k: b.get(k) for k in _CHIAVI_CONTRO_B}
        senza = dict(b["senza_pavimento_sfasate"])
        senza["gradi_liberta"] = (int(esame["n_blocchi"]) - 1) if senza.get("valutabile") else None
        piano = contro_b.get("errore_candidato_senza_pavimento")
        decide = bool(contro_b["valutabile"] and contro_b["origine_pavimento"] == "pavimento_minimo"
                      and piano is not None and contro_b["pavimento_minimo"] > piano)
    a = esame.get("baseline_a")
    diverse = sorted(s for s, v in per_moneta.items()
                     if v.get("barre_vietate") is not None and v["barre_vietate"]["impronta"] != impronte_vietate[s])
    pav = esame.get("pavimento_sfasate")
    return {
        "trade": int(metriche["n_trade"]),
        "r_medio": metriche.get("r_medio"),
        "B": None if b is None else b.get("media"),
        "pavimento_b": None if contro_b is None else contro_b.get("errore_minimo_baseline"),
        "monete_con_trade": esame["monete_con_trade"],
        "monete_nel_periodo": esame.get("monete_nel_periodo"),
        "quota_moneta_piu_presente": esame["quota_moneta_piu_presente"],
        "moneta_piu_presente": esame["moneta_piu_presente"],
        "trade_per_moneta": {s: int(v["trade"]) for s, v in per_moneta.items() if v["trade"]},
        "valutabile": bool(esame["valutabile"]),
        "motivi_non_valutabile": esame["motivi_non_valutabile"],
        "blocco": esame.get("blocco"),
        "n_blocchi": esame.get("n_blocchi"),
        "uscite_massime_in_un_giorno": esame.get("uscite_massime_in_un_giorno"),
        "durata_massima_barre": esame.get("durata_massima_barre"),
        "effetto_grappolo": esame.get("effetto_grappolo"),
        "percentile_caso": esame.get("percentile_caso"),
        "contro_b": contro_b,
        "senza_pavimento": senza,
        "pavimento_sfasate": None if pav is None else {k: pav.get(k) for k in _CHIAVI_PAVIMENTO},
        "pavimento_decide": decide,
        "sfasate": sfasate_dall_avanzamento(esame, ms, d, finestra_placebo),
        "contro_a": None if a is None else {k: a.get(k) for k in ("valutabile", "p_value", "t", "netta", "media")},
        "candidato": esame.get("candidato"),
        "validazione": esame.get("validazione"),
        "liquidazione": esame.get("liquidazione"),
        "ingressi_senza_barra": _somma_senza_barra(per_moneta),
        "vietate_diverse": diverse,
        "impronta_esame": esame["impronte"]["esame"],
        "impronta_variante": esame["impronte"]["variante"],
        "impronte_strumenti": dict(sorted(esame["impronte"]["strumenti"].items())),
        "ripresa": esame.get("ripresa"),
        "file": esame.get("file"),
    }


def esegui_placebo(prep: Mapping, regola: str, direzione: str, k: int, *, caricatore, cartella_gruppo: Path,
                   radice, processi: int = 1) -> Dict[str, object]:
    """Una placebo in un periodo: sfasamento, ingressi, ``conta_trade_di_gruppo`` (costruzione), ``esame_di_gruppo``."""
    timeframe, periodo, ms = prep["timeframe"], prep["periodo"], prep["ms"]
    testo = etichetta(timeframe, regola, direzione, periodo, k)
    uscita = PG.USCITA_DELLA_REGOLA[regola]
    inizio, fine = prep["finestra_unione"]
    L, margine = prep["L"], prep["margine"]
    d = sfasamento(testo, L, margine)
    monete = prep["monete"]
    chiave = f"{regola}|{direzione}"
    originali = {s: info["segnali"][chiave] for s, info in monete.items()}
    spostati = sposta_istanti(originali, inizio, L, ms, d)
    vietate = f"{direzione}|{uscita}"
    ingressi, conteggi = ingressi_per_moneta(spostati, monete, vietate, ms)
    regole = gruppo.regole_del_gruppo()
    riga: Dict[str, object] = {
        "formato": FORMATO, "etichetta": testo, "timeframe": timeframe, "regola": regola, "direzione": direzione,
        "uscita": uscita, "periodo": periodo, "k": int(k), "seme": seme_di(testo), "d": d, "L": L,
        "margine": margine, "finestra_unione": [inizio, fine], "monete": len(monete),
        "barre_per_moneta": {s: int(info["barre_nel_periodo"]) for s, info in sorted(monete.items())},
        "segnali": dict(conteggi, originali=sum(len(v) for v in originali.values()),
                        monete_con_segnali=sum(1 for v in originali.values() if v)),
        "minimi": {"costruzione": regole["trade_minimi"]["costruzione"],
                   "validazione": regole["trade_minimi"]["validazione"],
                   "quota_massima_moneta": regole["quota_massima_moneta"]},
        "conta": None, "giudicata": False, "esame": None, "errore": None,
    }
    p = {"regola": regola, "direzione": direzione}
    comuni = dict(processi=processi, radice=radice, monete=prep["argomento_monete"], caricatore=caricatore,
                  ingressi_placebo=ingressi, **OPZIONI_ESAME)
    if periodo == "costruzione":
        conta = gruppo.conta_trade_di_gruppo(MODULO, p, timeframe, **comuni)
        riga["conta"] = {k2: conta[k2] for k2 in ("trade_stimati", "esito", "motivi", "minimo", "quota_massima",
                                                  "quota_moneta_piu_presente", "moneta_piu_presente",
                                                  "monete_con_trade", "stima_trade_validazione")}
        riga["conta"]["ingressi_senza_barra"] = _somma_senza_barra(conta["per_moneta"])
        if conta["esito"] == "scarto":
            return riga  # sotto 700 trade o una moneta oltre il 10%: non si giudica (regole.md, punto 4)
    esame = gruppo.esame_di_gruppo(MODULO, p, timeframe, periodo, id_esame(timeframe, regola, direzione, k),
                                   cartella_campagna=cartella_gruppo, **comuni)
    impronte_vietate = {s: info["vietate"][vietate]["impronta"] for s, info in monete.items()}
    riga["esame"] = estrai_esame(esame, impronte_vietate, ms, d, [inizio, fine])
    minimo = regole["trade_minimi"][periodo]
    riga["giudicata"] = periodo == "costruzione" or riga["esame"]["trade"] >= minimo
    return riga


# ---------------------------------------------------------------------------
# Impronte, git, identita', ripresa
# ---------------------------------------------------------------------------


#: argomenti in piu' per ``conta_trade_di_gruppo`` ed ``esame_di_gruppo`` (per esempio il terreno d'ingresso della
#: seconda edizione): vuoto per la prova a 1 ora, lo riempie il lanciatore della prova del paniere
OPZIONI_ESAME: Dict[str, object] = {}


def leggi_impronte(testo: str) -> Dict[str, str]:
    """Le impronte dei cinque file da righe nel formato di ``sha256sum`` (anche fra apici inversi, in un elenco o in
    una tabella): una riga conta se ha UNA impronta di 64 cifre esadecimali e UNO dei cinque percorsi.
    ValueError se lo stesso file ha due impronte diverse."""
    trovate: Dict[str, str] = {}
    for riga in testo.splitlines():
        campi = [c.strip("`*-:,;()") for c in riga.replace("|", " ").split()]
        impronte = [c.lower() for c in campi if re.fullmatch(r"[0-9a-fA-F]{64}", c)]
        nomi = [c for c in campi if c in gruppo.FILE_DEL_VIA_LIBERA]
        if len(impronte) != 1 or len(nomi) != 1:
            continue
        if trovate.get(nomi[0], impronte[0]) != impronte[0]:
            raise ValueError(f"{nomi[0]} ha due impronte diverse")
        trovate[nomi[0]] = impronte[0]
    return trovate


def in_bozza(testo: str) -> bool:
    """``regole.md`` e' ancora in bozza: c'e' il riquadro «**BOZZA.**» (il punto 7 nomina «la riga BOZZA» senza
    asterischi, e non conta)."""
    return "**BOZZA" in testo


def impronte_attese(file_impronte: Optional[Path], regole: Path = REGOLE_DELLA_PROVA, *,
                    funzionamento: bool = False) -> Tuple[Optional[Dict[str, str]], str, bool]:
    """Le cinque impronte attese e da dove vengono, e se ``regole.md`` e' in bozza.

    Lancio vero: solo dalle righe compilate al punto 7 di ``regole.md`` (SystemExit con ``--impronte-attese``, con
    le regole in bozza o se ne manca una). ``funzionamento``: da ``file_impronte`` se c'e' (e uguali a quelle di
    ``regole.md`` se li' sono compilate), se no da ``regole.md`` se compilate, se no nessuna (None: niente confronto).
    """
    testo = regole.read_text(encoding="utf-8")
    bozza = in_bozza(testo)
    da_regole = leggi_impronte(testo)
    if not funzionamento:
        if file_impronte is not None:
            raise SystemExit("--impronte-attese vale solo con --funzionamento: nel lancio vero le impronte sono quelle "
                             "del punto 7 di regole.md")
        if bozza:
            raise SystemExit(f"{regole} e' ancora in BOZZA: il lancio vero vuole le regole chiuse, committate e "
                             "pushate (intestazione di regole.md; GRUPPO, sezione 11, punto 1)")
        attese, fonte = da_regole, str(regole)
    elif file_impronte is not None:
        attese, fonte = leggi_impronte(Path(file_impronte).read_text(encoding="utf-8")), str(file_impronte)
        if da_regole and da_regole != attese:
            raise SystemExit(f"le impronte di {file_impronte} non sono quelle scritte in {regole}")
    elif da_regole:
        attese, fonte = da_regole, str(regole)
    else:
        return None, "nessuna (funzionamento)", bozza
    mancanti = [nome for nome in gruppo.FILE_DEL_VIA_LIBERA if nome not in attese]
    if mancanti:
        raise SystemExit(f"mancano le impronte attese di {', '.join(mancanti)} ({fonte}): compila il punto 7 di "
                         "regole.md" + (" o passa --impronte-attese" if funzionamento else ""))
    return attese, fonte, bozza


def controlla_prova(cartella: Path = QUI, file: Sequence[str] = FILE_DELLA_PROVA,
                    ramo: str = RAMO_REMOTO) -> Dict[str, str]:
    """Il codice e le regole della prova sono committati e pushati (lancio vero). SystemExit con il motivo se no.

    ``git status`` dei file vuoto (niente modifiche, niente file nuovi), e l'ultimo commit che li tocca contenuto in
    ``ramo`` (il ramo remoto come lo conosce questo worktree: si aggiorna con il push).
    """
    sporchi = _git(cartella, "status", "--porcelain", "--", *file).strip()
    if sporchi:
        raise SystemExit("codice o regole della prova non committati (committali e pushali prima del lancio):\n"
                         + sporchi)
    ultimo = _git(cartella, "log", "-1", "--format=%H", "--", *file).strip()
    if not ultimo:
        raise SystemExit(f"nessun commit contiene {', '.join(file)}")
    if subprocess.run(["git", "-C", str(cartella), "rev-parse", "--verify", "--quiet", ramo],
                      capture_output=True).returncode != 0:
        raise SystemExit(f"il ramo {ramo} non c'e' in questo worktree: pusha il branch di coordinamento")
    if subprocess.run(["git", "-C", str(cartella), "merge-base", "--is-ancestor", ultimo, ramo],
                      capture_output=True).returncode != 0:
        raise SystemExit(f"il commit {ultimo[:8]} della prova non e' su {ramo}: pushalo prima del lancio")
    return {"commit_prova": _git(cartella, "rev-parse", "HEAD").strip(), "commit_file_della_prova": ultimo}


def controlla_principale(attese: Optional[Mapping[str, str]], *, pulito: bool = True) -> Dict[str, str]:
    """Il codice del branch principale: committato (``pulito``), con il commit 08e4ad95, con le impronte attese in
    memoria e sul disco (se ``attese`` non e' None). SystemExit con il motivo se no."""
    if pulito:
        sporco = [r for r in _git(PRINCIPALE, "status", "--porcelain", "--", "research/src", "research/config",
                                  "research/campagne/GRUPPO").splitlines() if "__pycache__" not in r]
        if sporco:
            raise SystemExit("codice non committato nel branch principale:\n" + "\n".join(sporco))
    if subprocess.run(["git", "-C", str(PRINCIPALE), "merge-base", "--is-ancestor", COMMIT_MINIMO, "HEAD"],
                      capture_output=True).returncode != 0:
        raise SystemExit(f"il branch principale non contiene il commit {COMMIT_MINIMO} degli strumenti di gruppo")
    in_memoria = gruppo.impronte_degli_strumenti()
    su_disco = {nome: sha256_file(PRINCIPALE / nome) for nome in gruppo.FILE_DEL_VIA_LIBERA}
    diverse = [nome for nome in gruppo.FILE_DEL_VIA_LIBERA if in_memoria[nome] != su_disco[nome]
               or (attese is not None and su_disco[nome] != attese[nome])]
    if diverse:
        raise SystemExit(f"impronte diverse da quelle attese (o fra memoria e disco): {', '.join(diverse)}")
    return {"commit_principale": _git(PRINCIPALE, "rev-parse", "HEAD").strip(),
            "ramo_principale": _git(PRINCIPALE, "branch", "--show-current").strip()}


def impronta_dei_dati(radice: Path, monete: Sequence[str]) -> str:
    """SHA-256 di {simbolo: ``dati.calcola_impronte``} (ogni file .zip in-sample, con il suo SHA-256) per le monete e
    per BTCUSDT (che ``CaricatoreDisco.btc`` legge, se c'e')."""
    return _sha256_canonico({s: dati.calcola_impronte(s, Path(radice))
                             for s in sorted(set(monete) | {MONETA_RIFERIMENTO})})


def impronta_delle_schede(radice: Path, monete: Sequence[str]) -> str:
    """SHA-256 di {simbolo: SHA-256 della scheda} per le schede che ``CaricatoreDisco`` legge."""
    cartella = Path(radice) / dati.CARTELLA_SCHEDE_GRUPPO
    return _sha256_canonico({s: sha256_file(cartella / f"{s}.md") for s in sorted(monete)})


def identita_corrente(radice: Path, posizioni: Mapping[str, int], funzionamento: bool,
                      regole: Path = REGOLE_DELLA_PROVA) -> Dict[str, object]:
    """Cio' che rende due righe confrontabili: tutto quello da cui dipendono i loro numeri.

    Le cinque impronte (dai file sul disco), il codice della prova e ``regole.md``, l'elenco delle monete
    (``monete.csv`` e le posizioni j), le schede, i dati, e se e' un lancio di funzionamento. Gli hash dei commit
    stanno nella riga ma non qui: il branch principale riceve commit di continuo (ops, stato) senza cambiare questi
    file.
    """
    return {
        "formato": FORMATO,
        "strumenti": {nome: sha256_file(PRINCIPALE / nome) for nome in sorted(gruppo.FILE_DEL_VIA_LIBERA)},
        "codice": {nome: sha256_file(QUI / nome) for nome in CODICE_DELLA_PROVA},
        "regole.md": sha256_file(regole),
        "monete": {"monete.csv": sha256_file(MONETE_DEL_PRINCIPALE),
                   "posizioni": _sha256_canonico(sorted([s, int(j)] for s, j in posizioni.items()))},
        "schede": impronta_delle_schede(radice, sorted(posizioni)),
        "dati": impronta_dei_dati(radice, sorted(posizioni)),
        "funzionamento": bool(funzionamento),
    }


def differenze_di_identita(prima: Mapping, adesso: Mapping) -> List[str]:
    return sorted(k for k in set(prima) | set(adesso) if prima.get(k) != adesso.get(k))


def controlla_esame_contro_identita(riga: Mapping, identita: Mapping) -> List[str]:
    """L'esame della riga ha usato il modulo e gli strumenti dell'identita' (``esame['impronte']`` di gruppo.py)."""
    esame = riga.get("esame")
    if not esame:
        return []
    diverse = []
    if esame.get("impronta_variante") != identita["codice"]["placebo_gruppo.py"]:
        diverse.append("placebo_gruppo.py (impronta della variante dell'esame)")
    if esame.get("impronte_strumenti") != identita["strumenti"]:
        diverse.append("strumenti (impronte dell'esame)")
    return diverse


def righe_fatte(percorso: Path, identita: Mapping) -> set:
    """Le etichette gia' fatte (senza errore) in un file di esiti; SystemExit se il file ha righe di un'altra identita'.

    Una riga interrotta a meta' (illeggibile) si ignora.
    """
    fatte: set = set()
    if not percorso.is_file():
        return fatte
    for riga in percorso.read_text(encoding="utf-8").splitlines():
        if not riga.strip():
            continue
        try:
            voce = json.loads(riga)
        except json.JSONDecodeError:
            continue
        if voce.get("identita") != identita:
            raise SystemExit(f"{percorso} contiene righe di un'altra identita' (codice, regole, strumenti, monete, "
                             "schede o dati diversi): spostalo prima di rilanciare (regole.md, punti 5 e 6)")
        if not voce.get("errore"):
            fatte.add(voce["etichetta"])
    return fatte


def scrivi_riga(percorso: Path, riga: Mapping) -> None:
    """Aggiunge una riga JSON al file (chiudendo prima una riga interrotta), e la scrive sul disco."""
    percorso.parent.mkdir(parents=True, exist_ok=True)
    testo = json.dumps(riga, sort_keys=True, ensure_ascii=False)
    with open(percorso, "ab") as flusso:
        if flusso.tell() > 0:
            with open(percorso, "rb") as lettura:
                lettura.seek(-1, os.SEEK_END)
                if lettura.read(1) != b"\n":
                    flusso.write(b"\n")
        flusso.write(testo.encode("utf-8") + b"\n")
        flusso.flush()
        os.fsync(flusso.fileno())


def compiti_da_fare(ks: Sequence[int], timeframe: Sequence[str], periodi: Sequence[str],
                    fatte: Mapping[int, set]) -> List[Tuple[str, str, str, str, int]]:
    """(timeframe, periodo, regola, direzione, k) ancora da fare, raggruppati per timeframe e periodo (i dati si
    preparano una volta per gruppo)."""
    return [(tf, periodo, regola, direzione, k)
            for tf in timeframe for periodo in periodi for regola in PG.REGOLE for direzione in PG.DIREZIONI
            for k in ks if etichetta(tf, regola, direzione, periodo, k) not in fatte[k]]


# ---------------------------------------------------------------------------
# Il lancio
# ---------------------------------------------------------------------------


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Prova a placebo dell'esame di gruppo (regole.md di questa cartella)")
    parser.add_argument("--radice-dati", type=Path, default=os.environ.get("PLACEBO_RADICE_DATI"),
                        help="la radice con data/insample/<SIMBOLO>/ (fuori da git)")
    parser.add_argument("--lavoro", type=Path, default=LAVORO_PREDEFINITO,
                        help="la cartella di lavoro, fuori da git (radice di lettura, avanzamento e trade di gruppo.py)")
    parser.add_argument("--k", type=int, nargs="+", default=list(K_DELLA_PROVA))
    parser.add_argument("--timeframe", nargs="+", default=["4h", "1h"], choices=list(PG.TIMEFRAME))
    parser.add_argument("--periodo", nargs="+", default=list(PERIODI), choices=list(PERIODI))
    parser.add_argument("--massimo-minuti", type=float, default=None)
    parser.add_argument("--processi", type=int, default=4)
    parser.add_argument("--solo-copertura", action="store_true",
                        help="fa solo i controlli e la copertura dei dati, nessun esame")
    parser.add_argument("--funzionamento", action="store_true",
                        help="prova di funzionamento: righe segnate, in <lavoro>/esiti_funzionamento/, mai un esito")
    parser.add_argument("--impronte-attese", type=Path, default=None, help="solo con --funzionamento")
    args = parser.parse_args(argv)
    if args.radice_dati is None or not (Path(args.radice_dati) / "data" / "insample").is_dir():
        parser.error("--radice-dati deve essere la cartella che contiene data/insample/")
    inizio = time.monotonic()
    funzionamento = bool(args.funzionamento)
    lavoro = controlla_lavoro(args.lavoro, [QUI.parents[2], PRINCIPALE])
    attese, fonte, bozza = impronte_attese(args.impronte_attese, funzionamento=funzionamento)
    if funzionamento:
        codice = {"commit_prova": _git(QUI, "rev-parse", "HEAD").strip(), "commit_file_della_prova": None}
        codice.update(controlla_principale(attese, pulito=False))
    else:
        codice = controlla_prova()
        codice.update(controlla_principale(attese))
    if dati.marcatore_di_campagna() is not None:
        raise SystemExit("c'e' un marcatore di campagna nel branch principale: la prova gira senza (regole.md, punto 3.5)")
    radice = radice_di_lettura(lavoro, args.radice_dati)
    caricatore = gruppo.CaricatoreDisco(str(radice))
    posizioni, _ = gruppo._monete_con_posizione(None)
    controlla_copertura(caricatore, None, args.processi, severa=not funzionamento)
    identita = identita_corrente(radice, posizioni, funzionamento)
    if args.solo_copertura:
        print(f"solo copertura: identita' {_sha256_canonico(identita)[:16]}, nessun esame", flush=True)
        return 0
    esiti = (lavoro / "esiti_funzionamento") if funzionamento else ESITI_DEFINITIVI
    cartella_gruppo = lavoro / "gruppo" / _sha256_canonico(identita)[:16]
    ks = sorted(set(args.k))
    fatte = {k: righe_fatte(esiti / f"esiti_k{k}.jsonl", identita) for k in ks}
    compiti = compiti_da_fare(ks, args.timeframe, args.periodo, fatte)
    print(f"principale {codice['commit_principale'][:8]} ({codice['ramo_principale']}), prova "
          f"{codice['commit_prova'][:8]}, impronte attese da {fonte}"
          f"{' (FUNZIONAMENTO: righe segnate, nessun esito)' if funzionamento else ''}; esiti in {esiti}; "
          f"k {ks}: da fare {len(compiti)}, gia' fatte {sum(len(v) for v in fatte.values())}", flush=True)
    preparato: Optional[Dict[str, object]] = None
    errori_di_fila = 0
    for n, (tf, periodo, regola, direzione, k) in enumerate(compiti, 1):
        minuti = (time.monotonic() - inizio) / 60
        if args.massimo_minuti is not None and minuti >= args.massimo_minuti:
            print(f"fermato dopo {minuti:.1f} minuti: {len(compiti) - n + 1} da fare, rilancia per continuare",
                  flush=True)
            return 3
        if preparato is None or (preparato["timeframe"], preparato["periodo"]) != (tf, periodo):
            preparato = None  # libera la memoria del gruppo di prima
            t0 = time.monotonic()
            preparato = prepara(tf, periodo, caricatore, None, args.processi)
            print(f"dati {tf} {periodo} pronti: {len(preparato['monete'])} monete, L {preparato['L']}, "
                  f"{time.monotonic() - t0:.0f} s", flush=True)
        t0 = time.monotonic()
        try:
            riga = esegui_placebo(preparato, regola, direzione, k, caricatore=caricatore,
                                  cartella_gruppo=cartella_gruppo, radice=radice, processi=args.processi)
            errori_di_fila = 0
        except Exception as errore:  # noqa: BLE001 - si scrive nella riga e si rifa' al lancio dopo
            riga = {"formato": FORMATO, "etichetta": etichetta(tf, regola, direzione, periodo, k), "timeframe": tf,
                    "regola": regola, "direzione": direzione, "periodo": periodo, "k": k,
                    "errore": f"{type(errore).__name__}: {errore}\n{traceback.format_exc()}"[:4000]}
            errori_di_fila += 1
        # prima di scrivere: niente e' cambiato durante il calcolo (codice, regole, strumenti, monete, schede, dati)
        cambiati = differenze_di_identita(identita, identita_corrente(radice, posizioni, funzionamento))
        cambiati += controlla_esame_contro_identita(riga, identita)
        if cambiati:
            print(f"FERMO: durante {riga['etichetta']} e' cambiato {', '.join(cambiati)}; la riga non e' scritta. "
                  "Rimetti i file com'erano o rilancia tutto in una cartella nuova (regole.md, punto 6)", flush=True)
            return 4
        riga.update({"identita": identita, "impronte_attese_da": fonte, "regole_bozza": bozza,
                     "funzionamento": funzionamento, "radice_dati": str(Path(args.radice_dati).resolve()),
                     "lavoro": str(lavoro), "secondi": round(time.monotonic() - t0, 1),
                     "scritta": datetime.now(timezone.utc).isoformat(timespec="seconds"), **codice})
        scrivi_riga(esiti / f"esiti_k{k}.jsonl", riga)
        stato = "ERRORE" if riga.get("errore") else ("scarto" if riga.get("conta") and not riga.get("esame")
                                                     else "esame fatto")
        print(f"[{n}/{len(compiti)}] {riga['etichetta']}: {stato}, {riga['secondi']:.0f} s", flush=True)
        if errori_di_fila >= 3:
            print("tre errori di fila: fermo (le righe con errore si rifanno al lancio dopo)", flush=True)
            return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
