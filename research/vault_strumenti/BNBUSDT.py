#!/usr/bin/env python3
"""Passo 5 del protocollo 4.5: il lanciatore del candidato BNBUSDT-045 (campagna BNBUSDT).

Il candidato gira con il SUO codice: ``research/campagne/BNBUSDT/codice/`` (comune.py,
varianti.py, registro.py) e ``research/src/`` del worktree della sua campagna
(branch ``research/campagna/BNBUSDT``, punta 2e29620a), importati da li' con sys.path, come
faceva ``codice/validazione.py``. Qui non c'e' nessuna copia di quel codice: prima di
importarlo il lanciatore controlla lo SHA-256 di ogni file contro il commit della consegna.

Tre modi.

``parita`` (solo in-sample, gira a vault chiuso)
    1. riscarica con ``dati.scarica_periodo`` del worktree, dal 2020-02-01 al 2023-12-31, solo le
       serie che servono: BNBUSDT klines 1h, markPriceKlines 1h, fundingRate, e BTCUSDT klines 1h
       (riferimento di mercato della consegna);
    2. le confronta con le impronte della campagna (``impronte.json``, la cui impronta e' scritta
       in ``fase0_dati.md``): una differenza ferma tutto (STOP del protocollo);
    3. rifa' la validazione ESATTAMENTE come ``codice/validazione.py`` (stessa variante, stessa
       ``comune.valuta``, stesso p-value e stessa asticella; senza scrivere nel log) e la
       costruzione come ``codice/lancia.py``, e confronta campo per campo con le voci del log e
       con i numeri scritti in ``consegna.md``;
    4. fa girare il motore del modo vault sul periodo di VALIDAZIONE, con gli stessi passi del
       vault (marcatore, controllo dei file, impronta, caricamento, controllo dei dati, avanzamento
       a pezzi, 1000 simulazioni, criterio, tasso del caso, risultato e riassunto): fermate sui
       dati senza risultato e ripartenza (file mancante, file illeggibile, mese sotto il 50%, mese
       senza funding, ultima barra mancante), interruzione e ripresa, pezzi manomessi rifiutati,
       marcatore di un altro giro o di un altro lanciatore rifiutato, guardia «una volta sola»;
       controlla che riproduca le voci del log e che la gemella delle entrate casuali dia, seme
       per seme, gli stessi R medi di ``motore.simula_baseline_casuale`` sui semi 0..199. La
       cartella della prova (``--cartella-prova``) dev'essere nuova o vuota: il lanciatore la
       svuota da se' solo se sta dentro lo scratchpad della sessione che l'ha scritto;
    5. misura i tempi e stima quello del modo vault.
    Scrive l'esito in un file JSON (``--uscita``).

``apertura`` / ``requisiti-apertura`` (sola lettura, stesso modo con due nomi)
    Stampa cosa deve contenere ``research/vault/APERTURA.md`` del coordinamento per questo
    candidato: l'ID, lo SHA-256 completo di regole.md e di ogni file controllato, i semi 0-999.

``vault`` (gira solo dopo l'apertura del vault; nessun percorso da scegliere)
    Posti FISSI, qualunque siano gli argomenti:
      risultato    /home/user/coordinamento/research/vault/BNBUSDT-045_vault.json
      riassunto    /home/user/coordinamento/research/vault/BNBUSDT-045_vault.md (dopo il JSON)
      marcatore    /home/user/coordinamento/research/vault/BNBUSDT-045_giro_iniziato.json
      avanzamento  /home/user/coordinamento/research/vault_strumenti/avanzamento/BNBUSDT-045/
    Ordine:
     1. se il risultato esiste, o il marcatore esiste ed e' di un lanciatore diverso o dice che
        il risultato e' gia' stato scritto: GiaEseguito (sola lettura, nulla scritto);
     2. codice congelato (SHA-256 su disco e al commit della consegna);
     3. se manca ``/home/user/coordinamento/research/vault/APERTURA.md``: VaultChiuso (sollevata
        da ``dati.controlla_vault`` del worktree), PRIMA di scrivere qualunque file. APERTURA.md
        deve contenere BNBUSDT-045, lo SHA-256 completo di regole.md e di ogni file controllato, e
        i semi 0-999; il lanciatore lo copia da se' in ``<worktree>/research/vault/APERTURA.md``
        se non c'e' e verifica che sia uguale byte per byte (se c'e' ed e' diverso: STOP);
     4. marcatore, creato in modo esclusivo (O_EXCL). Se c'e' gia' (stesso lanciatore): se il
        candidato non e' mai stato eseguito si riparte; se e' stato eseguito si riprende solo lo
        STESSO giro (stessa impronta, controllata prima di caricare);
     5. regola dei dati D1 (nessuna candela letta): file in-sample presenti, leggibili e con le
        impronte della campagna; scarico del vault (2024-01-01 -> 2026-09-30) con
        ``dati.scarica_periodo`` del worktree; FERMO SUI DATI se manca o non si legge (zip rotto,
        CRC sbagliato, niente CSV) anche un solo file mensile 2024-01 -> 2026-09 di una serie usata
        (BNBUSDT last, mark, funding e BTCUSDT 1h);
     6. impronta del giro: SHA-256 del lanciatore, di ogni file controllato del candidato, di ogni
        file di dati (in-sample e vault), di APERTURA.md, i semi e le versioni di python, numpy e
        scipy (D5). Scritta nel marcatore prima di caricare;
     7. caricamento e regola dei dati D2: FERMO SUI DATI solo se l'ultima barra allineata non e' il
        2026-09-30 alle 23:00 UTC, se un mese ha meno del 50% delle barre allineate attese, o se un
        mese non ha nessun settlement di funding. Per BTC (solo contesto: correlazione) solo avvisi.
        Tutto il resto (D3) e' riportato nel JSON e nel .md: per mese barre attese, last, mark,
        allineate e quota, con un AVVISO sotto il 99%; settlement di funding per mese con gli
        intervalli osservati; la parte prima del 2024 confrontata con la Fase 0 (33.904/192/224);
     8. il marcatore passa a «candidato in esecuzione»; poi il giudizio: serie dal 2020-02-01
        (indicatori caldi, come in validazione), trade contati se entrano dal 2024-01-01 00:00 UTC,
        metriche della consegna, (a) e (b) del vault per il rapporto, 1000 entrate casuali (semi
        0..999) a pezzi nell'avanzamento, 90° percentile, ``criterio_vault`` con i valori di
        ``parametri.yaml`` e tasso del caso.
    Fermate e uscite PRIMA dell'esecuzione del candidato (D1, D2, un errore, un Ctrl-C): nessun
    risultato, il vault non e' consumato; il marcatore registra «fermo sui dati, candidato non
    eseguito» (o l'errore) e si riparte con lo STESSO lanciatore dopo aver risolto (uscita 6 per
    le fermate sui dati). DOPO l'esecuzione del candidato (D4) ogni uscita scrive il risultato, con
    esito «passa», «non passa», «non si sa» (sotto i trade minimi del vault, sezione 8), «non
    valutabile» (entrate casuali non costruibili), «STOP» (un controllo fallito, nessun giudizio) o
    «errore» (eccezione del lanciatore, nessun giudizio); solo un'interruzione (Ctrl-C) lascia il
    giro da riprendere. A giro finito il campo «motivo» in cima al marcatore torna vuoto.

Uso:
    python3 research/vault_strumenti/BNBUSDT.py parita --uscita /percorso/vault_parita_BNBUSDT.json \\
        --cartella-prova /percorso/cartella_nuova
    python3 research/vault_strumenti/BNBUSDT.py requisiti-apertura     (oppure: apertura)
    python3 research/vault_strumenti/BNBUSDT.py vault
"""
from __future__ import annotations

import sys

sys.dont_write_bytecode = True  # niente __pycache__ nel worktree della campagna

import argparse  # noqa: E402
import contextlib  # noqa: E402
import fcntl  # noqa: E402
import hashlib  # noqa: E402
import json  # noqa: E402
import math  # noqa: E402
import os  # noqa: E402
import re  # noqa: E402
import shutil  # noqa: E402
import subprocess  # noqa: E402
import tempfile  # noqa: E402
import time  # noqa: E402
import traceback  # noqa: E402
import zipfile  # noqa: E402
from dataclasses import dataclass  # noqa: E402
from datetime import date, datetime, timedelta, timezone  # noqa: E402
from pathlib import Path  # noqa: E402
from typing import Callable, Dict, List, Optional, Sequence, Tuple  # noqa: E402

# ---------------------------------------------------------------------------
# Il candidato e il suo codice congelato
# ---------------------------------------------------------------------------

CANDIDATO = "BNBUSDT-045"
SIMBOLO = "BNBUSDT"
TF = "1h"
WORKTREE_DEFAULT = Path("/home/user/vault_BNBUSDT")
COMMIT = "2e29620af29acfaf70b0340eedfd28a4113cd65c"  # punta di research/campagna/BNBUSDT
CAMPAGNA_REL = "research/campagne/BNBUSDT"
REGOLE_REL = "research/campagne/BNBUSDT/candidati/BNBUSDT-045/regole.md"

# SHA-256 dei file al commit della consegna (calcolati con git show <commit>:<percorso>).
IMPRONTE_CODICE = {
    REGOLE_REL: "e5b2bd86046e0ff402b60c50a99613300eb967dd22b15444d08c614144a9cf61",
    "research/campagne/BNBUSDT/codice/varianti.py": "55170e59bf87d3582c1f5dd937c6a923c4720881b7ebdc0662f9f45b3878daad",
    "research/campagne/BNBUSDT/codice/comune.py": "96419bd65e0696bbfc985f07853b6f890f81a69d91f82e77a5906fe7aed66c69",
    "research/campagne/BNBUSDT/codice/validazione.py": "5f4629398cc9294e629bfc7baceaa709afdbf3b9ed6e67ad71dd75317f99ed27",
    "research/campagne/BNBUSDT/codice/registro.py": "27ae6760ad24cd5c49b90371414732e54eaa0f063aed6ef41abfb4942e371748",
    "research/src/dati.py": "395b52409494f79ebec28a57866162b60aa37750cb15482232f536b3bf49a950",
    "research/src/motore.py": "b3d5e1a93954f5b8cad34b74937592cf2b0ade237cbcc1e789a0ee195e6b0970",
    "research/src/statistica.py": "e5d5f0e42b7f4823b6db4a91152b32fc6b2d2bf6b0b3bddf4183ee542d1c3f92",
    "research/src/__init__.py": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    "research/__init__.py": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    "research/config/parametri.yaml": "736fe598b5179db70d3f63f134922fea428322ce40476c59c9204740653b066f",
    "research/campagne/BNBUSDT/impronte.json": "b4e4731ea4b792e63b5669d316b32e01aaad0b0209c462eac2a719b31f9fc338",
}
# fase0_dati.md: «Impronta di impronte.json: b4e4731e...»
IMPRONTA_IMPRONTE_JSON = "b4e4731ea4b792e63b5669d316b32e01aaad0b0209c462eac2a719b31f9fc338"

# Le serie che il candidato usa (i03 a 1h: OHLC last, mark per liquidazione e allineamento,
# funding per i costi; BTCUSDT 1h solo per la correlazione della consegna).
SERIE = [
    (SIMBOLO, "klines", TF),
    (SIMBOLO, "markPriceKlines", TF),
    (SIMBOLO, "fundingRate", None),
    ("BTCUSDT", "klines", TF),
]

# La variante congelata: varianti.i03("1h", vid, max_barre=12, solo_fine_settimana=True)
KW_VARIANTE = {"max_barre": 12, "solo_fine_settimana": True}

INIZIO_VAULT_TS = 1704067200000  # 2024-01-01 00:00 UTC
SEMI_CASO = list(range(0, 1000))  # non sono in parametri.yaml: APERTURA.md li deve scrivere (0-999)
BLOCCO_SEMI = 50  # simulazioni per pezzo del file di avanzamento

# Regola dei dati del coordinamento (D1-D5, sostituisce R1). D2: un mese con meno del 50% delle barre
# allineate attese ferma il giro PRIMA di eseguire il candidato, senza risultato; D3: sotto il 99% e'
# solo un AVVISO, come le barre tolte dichiarate dalle campagne (nell'in-sample di BNBUSDT 4 mesi su 46
# stanno sotto il 99%, fino all'83,9% di 2021-07, per giorni interi di mark mancanti).
QUOTA_BARRE_FERMO = 0.50
QUOTA_BARRE_AVVISO = 0.99
BTC_NEL_SEGNALE = False  # BTCUSDT serve solo alla correlazione della consegna: per BTC solo avvisi (D2)
# Conteggi della Fase 0 a 1h (fase0_dati.md): la parte prima del 2024 della serie lunga, riportata (D3)
FASE0_INSAMPLE = {"barre_tenute": 33904, "tolte_last": 192, "tolte_mark": 224}

# ---------------------------------------------------------------------------
# Posti fissi del modo vault (requisiti R2 e R6 del coordinamento)
# ---------------------------------------------------------------------------

COORDINAMENTO_RICERCA = Path("/home/user/coordinamento/research")
VAULT_COORD = COORDINAMENTO_RICERCA / "vault"
APERTURA_COORD = VAULT_COORD / "APERTURA.md"
AVANZAMENTO_VAULT = COORDINAMENTO_RICERCA / "vault_strumenti" / "avanzamento" / CANDIDATO
# l'unico posto in cui la prova del modo parita' svuota da se' una cartella gia' piena
SCRATCHPAD = Path("/tmp/claude-0/-home-user-agentic-trading-system/9da12ffe-13c5-5904-8f7e-5ce576103042/scratchpad")

# Moduli del candidato, importati da importa_candidato()
C = V = dati = motore = statistica = registro = None  # type: ignore


class Stop(RuntimeError):
    """Un controllo e' fallito: il protocollo dice STOP."""


class GiaEseguito(RuntimeError):
    """Il risultato o il marcatore di un altro giro esiste gia': il vault si giudica una volta sola."""


class Interrotto(RuntimeError):
    """Interruzione voluta (solo nella prova della ripresa)."""


class FermoSuiDati(RuntimeError):
    """Regola dei dati D1 o D2: il giro si ferma PRIMA di eseguire il candidato, senza risultato.

    Il vault non e' consumato: il marcatore registra «fermo sui dati, candidato non eseguito» e si
    riparte con lo stesso lanciatore dopo aver risolto il problema."""

    def __init__(self, regola: str, motivo: str, dettagli: Optional[Dict[str, object]] = None):
        super().__init__(f"{regola}: {motivo}")
        self.regola = regola
        self.motivo = motivo
        self.dettagli = dettagli or {}


STATO_FERMO = "fermo sui dati, candidato non eseguito"


# ---------------------------------------------------------------------------
# Utilita'
# ---------------------------------------------------------------------------


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def sha256_testo(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


# Lo SHA-256 del lanciatore che sta girando (letto all'avvio: il codice in memoria e' questo).
SHA256_LANCIATORE = sha256_file(Path(__file__).resolve())


def adesso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def iso(ts: Optional[int]) -> Optional[str]:
    if ts is None:
        return None
    return datetime.fromtimestamp(ts / 1000, tz=timezone.utc).strftime("%Y-%m-%d %H:%M UTC")


def json_sicuro(x):
    """JSON senza perdita di precisione: numpy -> python, inf/nan -> stringhe, chiavi -> str."""
    try:
        import numpy as np
    except ImportError:  # pragma: no cover
        np = None
    if isinstance(x, dict):
        return {str(k): json_sicuro(v) for k, v in x.items()}
    if isinstance(x, (list, tuple, set, frozenset)):
        return [json_sicuro(v) for v in x]
    if np is not None and isinstance(x, np.ndarray):
        return [json_sicuro(v) for v in x.tolist()]
    if np is not None and isinstance(x, np.generic):
        x = x.item()
    if isinstance(x, float):
        if math.isinf(x):
            return "inf" if x > 0 else "-inf"
        if math.isnan(x):
            return "nan"
    return x


def scrivi_json(p: Path, obj) -> None:
    p = Path(p)
    p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.with_name(p.name + ".parziale")
    tmp.write_text(json.dumps(json_sicuro(obj), ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    os.replace(tmp, p)


def scrivi_json_esclusivo(p: Path, obj) -> None:
    """Crea ``p`` solo se non esiste, in modo atomico (O_CREAT | O_EXCL): due giri non possono creare
    lo stesso file. Il testo si prepara prima, si scrive tutto e si forza su disco (fsync)."""
    p = Path(p)
    p.parent.mkdir(parents=True, exist_ok=True)
    testo = (json.dumps(json_sicuro(obj), ensure_ascii=False, indent=1) + "\n").encode("utf-8")
    try:
        fd = os.open(p, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
    except FileExistsError:
        raise GiaEseguito(f"{p} esiste gia': il vault si giudica una volta sola")
    with os.fdopen(fd, "wb") as f:
        f.write(testo)
        f.flush()
        os.fsync(f.fileno())


def scrivi_testo(p: Path, testo: str) -> None:
    p = Path(p)
    p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.with_name(p.name + ".parziale")
    tmp.write_text(testo, encoding="utf-8")
    os.replace(tmp, p)


def leggi_json(p: Path, cosa: str):
    try:
        return json.loads(Path(p).read_text(encoding="utf-8"))
    except ValueError as e:
        raise Stop(f"{cosa}: {p} non e' un JSON leggibile ({e})")


def versioni_impronta() -> Dict[str, str]:
    """Le versioni che entrano nell'impronta del giro (D5): python, numpy, scipy."""
    v = versioni()
    return {k: v[k] for k in ("python", "python_completa", "numpy", "scipy")}


def versioni() -> Dict[str, str]:
    out = {"python": sys.version.split()[0], "python_completa": sys.version}
    for nome in ("numpy", "scipy", "yaml"):
        try:
            out[nome] = __import__(nome).__version__
        except Exception as e:  # noqa: BLE001
            out[nome] = f"non disponibile ({type(e).__name__})"
    return out


def confronta(rifatto, atteso, percorso: str = "") -> List[str]:
    """Differenze campo per campo (numeri uguali esattamente, dopo l'arrotondamento del log)."""
    diff: List[str] = []
    if isinstance(atteso, dict) and isinstance(rifatto, dict):
        for k in sorted(set(atteso) | set(rifatto)):
            if k not in rifatto:
                diff.append(f"{percorso}.{k}: manca nel rifatto (log {atteso[k]!r})")
            elif k not in atteso:
                diff.append(f"{percorso}.{k}: manca nel log (rifatto {rifatto[k]!r})")
            else:
                diff += confronta(rifatto[k], atteso[k], f"{percorso}.{k}")
        return diff
    if isinstance(atteso, list) and isinstance(rifatto, list):
        if len(atteso) != len(rifatto):
            return [f"{percorso}: lunghezza {len(rifatto)} contro {len(atteso)}"]
        for i, (a, b) in enumerate(zip(rifatto, atteso)):
            diff += confronta(a, b, f"{percorso}[{i}]")
        return diff
    if rifatto != atteso or type(rifatto) is bool and type(atteso) is not bool:
        diff.append(f"{percorso}: rifatto {rifatto!r}, log {atteso!r}")
    return diff


def dentro(p: Path, base: Path) -> bool:
    """True se ``p`` e' ``base`` o sta sotto ``base`` (percorsi risolti)."""
    p, base = Path(p).resolve(), Path(base).resolve()
    return p == base or base in p.parents


# ---------------------------------------------------------------------------
# Import del codice del candidato (dal suo worktree, mai copiato)
# ---------------------------------------------------------------------------


def controlla_codice(worktree: Path) -> Dict[str, object]:
    """SHA-256 dei file congelati: su disco e al commit della consegna devono essere quelli attesi."""
    testa = subprocess.run(["git", "-C", str(worktree), "rev-parse", "HEAD"], capture_output=True, text=True,
                           check=True).stdout.strip()
    righe = {}
    problemi = []
    for rel, atteso in IMPRONTE_CODICE.items():
        su_disco = sha256_file(worktree / rel)
        blob = subprocess.run(["git", "-C", str(worktree), "show", f"{COMMIT}:{rel}"], capture_output=True,
                              check=True).stdout
        al_commit = hashlib.sha256(blob).hexdigest()
        righe[rel] = {"atteso": atteso, "su_disco": su_disco, "al_commit": al_commit}
        if not (su_disco == atteso == al_commit):
            problemi.append(rel)
    esito = {"worktree": str(worktree), "head": testa, "commit_atteso": COMMIT, "file": righe,
             "uguali": not problemi and testa == COMMIT}
    if testa != COMMIT:
        raise Stop(f"il worktree {worktree} e' su {testa}, non sul commit della consegna {COMMIT}")
    if problemi:
        raise Stop(f"file del candidato diversi da quelli congelati: {problemi}")
    return esito


def importa_candidato(worktree: Path) -> None:
    global C, V, dati, motore, statistica, registro
    codice = worktree / CAMPAGNA_REL / "codice"
    for p in (str(codice), str(worktree)):
        if p in sys.path:
            sys.path.remove(p)
    sys.path.insert(0, str(worktree))
    sys.path.insert(0, str(codice))
    import comune as _C  # noqa: E402
    import registro as _registro  # noqa: E402
    import varianti as _V  # noqa: E402
    from research.src import dati as _dati, motore as _motore, statistica as _statistica  # noqa: E402
    C, V, registro = _C, _V, _registro
    dati, motore, statistica = _dati, _motore, _statistica
    # ogni modulo caricato da un worktree o dal repository deve essere uno dei file controllati
    radici = [Path("/home/user").resolve()]
    controllati = {str((worktree / rel).resolve()) for rel in IMPRONTE_CODICE}
    for nome, mod in list(sys.modules.items()):
        f = getattr(mod, "__file__", None)
        if not f:
            continue
        rf = str(Path(f).resolve())
        if any(rf.startswith(str(r) + os.sep) for r in radici) and rf != str(Path(__file__).resolve()):
            if rf not in controllati:
                raise Stop(f"modulo {nome} caricato da {rf}, fuori dai file controllati del candidato")
    assert Path(C.__file__).resolve() == (codice / "comune.py").resolve()
    assert Path(dati.__file__).resolve() == (worktree / "research/src/dati.py").resolve()


def leggi_regole_esame(worktree: Path) -> Dict[str, object]:
    import yaml
    d = yaml.safe_load((worktree / "research/config/parametri.yaml").read_text(encoding="utf-8"))
    re_ = d["regole_esame"]
    cv = re_["criterio_vault"]
    if int(cv["trade_minimi"]) != int(re_["trade_minimi"]["vault"]):
        raise Stop("parametri.yaml: trade_minimi del criterio_vault diverso da trade_minimi.vault")
    if cv["rendimento_totale_positivo"] is not True:
        raise Stop("parametri.yaml: rendimento_totale_positivo non e' true (criterio_vault lo richiede)")
    semi_b = re_["semi_baseline_casuale"]
    out = {
        "pf_minimo": float(cv["profit_factor_minimo"]),
        "trade_minimi": int(cv["trade_minimi"]),
        "percentile_caso": float(cv["r_medio_sopra_percentile_caso"]),
        "simulazioni_caso": int(re_["simulazioni_caso"]),
        "simulazioni_b": int(re_["simulazioni_baseline_casuale"]),
        "primo_seme_b": int(semi_b["primo"]),
        "ultimo_seme_b": int(semi_b["ultimo"]),
        "bootstrap_n": int(re_["bootstrap"]["ricampionamenti"]),
        "bootstrap_seme": int(re_["bootstrap"]["seme"]),
        "fonte": str(worktree / "research/config/parametri.yaml"),
    }
    if out["ultimo_seme_b"] - out["primo_seme_b"] + 1 != out["simulazioni_b"]:
        raise Stop("parametri.yaml: semi della (b) incoerenti col numero di simulazioni")
    if out["simulazioni_caso"] != len(SEMI_CASO):
        raise Stop(f"parametri.yaml chiede {out['simulazioni_caso']} simulazioni del caso, il lanciatore ne ha {len(SEMI_CASO)}")
    return out


# ---------------------------------------------------------------------------
# APERTURA.md (requisito R4): contenuto e copia nel worktree
# ---------------------------------------------------------------------------

_RE_SEMI = re.compile(r"sem[ie]\b[^\n]*?(?<![\d.])0\s*(?:-|–|—|\.\.\.?|→|->|a)\s*999(?![\d])", re.IGNORECASE)


def controlla_apertura(testo: str, impronte: Dict[str, str]) -> Dict[str, object]:
    """APERTURA.md deve contenere l'ID del candidato, lo SHA-256 completo di regole.md e di ogni
    file controllato contro il worktree, e i semi 0-999 delle entrate casuali del tasso del caso."""
    basso = testo.lower()
    id_presente = re.search(rf"(?<![\w-]){re.escape(CANDIDATO)}(?![\w])", testo) is not None
    mancanti = []
    for rel, h in impronte.items():
        if not re.search(rf"(?<![0-9a-f]){h.lower()}(?![0-9a-f])", basso):
            mancanti.append(rel)
    semi = _RE_SEMI.search(testo) is not None
    problemi = []
    if not id_presente:
        problemi.append(f"APERTURA.md non nomina il candidato {CANDIDATO}")
    if mancanti:
        problemi.append(f"APERTURA.md non contiene lo SHA-256 completo di: {mancanti}")
    if not semi:
        problemi.append("APERTURA.md non scrive i semi 0-999 delle entrate casuali (es. «semi 0-999»)")
    return {"id_presente": id_presente, "sha256_mancanti": mancanti, "semi_0_999": semi,
            "file_controllati": len(impronte), "problemi": problemi}


def copia_apertura(sorgente: Path, destinazione: Path) -> Dict[str, object]:
    """Copia l'apertura del coordinamento nel worktree se non c'e'; deve risultare uguale byte per byte."""
    contenuto = Path(sorgente).read_bytes()
    destinazione = Path(destinazione)
    copiata = False
    if destinazione.exists():
        if destinazione.read_bytes() != contenuto:
            raise Stop(f"{destinazione} esiste ed e' diversa da {sorgente}: l'apertura e' una sola")
    else:
        destinazione.parent.mkdir(parents=True, exist_ok=True)
        tmp = destinazione.with_name(destinazione.name + ".parziale")
        tmp.write_bytes(contenuto)
        os.replace(tmp, destinazione)
        copiata = True
    if destinazione.read_bytes() != contenuto:
        raise Stop(f"la copia {destinazione} non e' uguale byte per byte a {sorgente}")
    return {"sorgente": str(sorgente), "destinazione": str(destinazione), "copiata_ora": copiata,
            "sha256": hashlib.sha256(contenuto).hexdigest(), "uguale_byte_per_byte": True}


def testo_per_apertura(impronte: Dict[str, str]) -> str:
    righe = [f"## {CANDIDATO} (campagna {SIMBOLO}, commit {COMMIT})", ""]
    righe.append(f"- regole.md: `{REGOLE_REL}` sha256 {impronte[REGOLE_REL]}")
    for rel, h in impronte.items():
        if rel != REGOLE_REL:
            righe.append(f"- `{rel}` sha256 {h}")
    righe.append("- semi delle 1000 entrate casuali del tasso del caso: 0-999")
    return "\n".join(righe) + "\n"


# ---------------------------------------------------------------------------
# Dati: scarico, impronte e controlli di completezza (solo con dati.py del worktree)
# ---------------------------------------------------------------------------


def nome_serie(s: str, tipo: str, tf: Optional[str]) -> str:
    return f"{s} {tipo} {tf or ''}".strip()


def impronte_attese_filtrate(worktree: Path) -> Dict[str, Dict[str, str]]:
    p = worktree / CAMPAGNA_REL / "impronte.json"
    if sha256_file(p) != IMPRONTA_IMPRONTE_JSON:
        raise Stop("impronte.json diverso da quello registrato in fase0_dati.md")
    tutte = json.loads(p.read_text(encoding="utf-8"))
    out: Dict[str, Dict[str, str]] = {}
    for s, tipo, tf in SERIE:
        pref = f"{tipo}/{tf}/" if tf else f"{tipo}/"
        sel = {k: v for k, v in tutte[s].items() if k.startswith(pref)}
        out.setdefault(s, {}).update(sel)
    return out


def scarica_insample(radice: Path) -> Dict[str, object]:
    dati.azzera_checksum_mancanti()
    out = {}
    t0 = time.perf_counter()
    for s, tipo, tf in SERIE:
        percorsi = dati.scarica_periodo(s, tipo, tf, C.INIZIO, dati.FINE_IN_SAMPLE, radice=radice)
        out[nome_serie(s, tipo, tf)] = len(percorsi)
    return {"file_per_serie": out, "checksum_mancanti": list(dati.CHECKSUM_MANCANTI),
            "periodo": [C.INIZIO.isoformat(), dati.FINE_IN_SAMPLE.isoformat()],
            "secondi": round(time.perf_counter() - t0, 1)}


def verifica_impronte_insample(worktree: Path, radice: Path) -> Dict[str, object]:
    attese = impronte_attese_filtrate(worktree)
    differenze: List[str] = []
    in_piu: List[str] = []
    conteggi = {}
    for s, sel in attese.items():
        differenze += [f"{s}: {d}" for d in dati.verifica_impronte(s, radice, sel)]
        trovate = dati.calcola_impronte(s, radice)
        prefissi = tuple({k.rsplit("/", 1)[0] + "/" for k in sel})
        extra = sorted(k for k in trovate if k.startswith(prefissi) and k not in sel)
        in_piu += [f"{s}: {k}" for k in extra]
        conteggi[s] = len(sel)
    esito = {"file_attesi": conteggi, "differenze": differenze, "file_in_piu_nelle_stesse_cartelle": in_piu,
             "uguali": not differenze and not in_piu,
             "fonte": f"{CAMPAGNA_REL}/impronte.json (sha256 {IMPRONTA_IMPRONTE_JSON}, scritta in fase0_dati.md)"}
    if not esito["uguali"]:
        raise Stop(f"impronte in-sample diverse da quelle della campagna: {differenze + in_piu}")
    return esito


def controlla_zip(p: Path) -> Optional[str]:
    """None se il file mensile si legge come zip di Binance; altrimenti il motivo.

    Controlla l'archivio (un solo .csv, non vuoto) e il CRC di ogni membro (``ZipFile.testzip``):
    i byte si decomprimono per il controllo ma nessuna riga viene interpretata come candela."""
    try:
        with zipfile.ZipFile(p) as z:
            csv = [i for i in z.infolist() if i.filename.lower().endswith(".csv")]
            if len(csv) != 1:
                return f"attesi un solo .csv nello zip, trovati {len(csv)}"
            if csv[0].file_size == 0:
                return "il .csv dentro lo zip e' vuoto"
            rotto = z.testzip()
            if rotto is not None:
                return f"CRC sbagliato in {rotto}"
    except Exception as e:  # noqa: BLE001 - zip rotto, troncato, illeggibile: il file non si legge
        return f"{type(e).__name__}: {e}"
    return None


def file_mensili(radice: Path, inizio: date, fine: date) -> Dict[str, object]:
    """Per ogni serie usata: i file mensili attesi del periodo, i presenti (con SHA-256), i mancanti
    e quelli che non si leggono (``controlla_zip``).

    Legge solo l'elenco dei file e i loro byte (impronta e controllo dello zip): nessuna candela
    viene interpretata."""
    serie: Dict[str, object] = {}
    impronte: Dict[str, str] = {}
    mancanti: Dict[str, List[str]] = {}
    illeggibili: Dict[str, List[str]] = {}
    for s, tipo, tf in SERIE:
        presenti = 0
        manca: List[str] = []
        rotti: List[str] = []
        mesi = list(dati.mesi_del_periodo(inizio, fine))
        for a, m in mesi:
            p = dati.percorso_mese(s, tipo, tf, a, m, radice)
            if p.is_file():
                try:
                    chiave = p.relative_to(radice).as_posix()
                except ValueError:  # fuori dalla radice (solo nelle prove): il percorso intero
                    chiave = str(p)
                try:
                    impronte[chiave] = dati.impronta_file(p)
                except OSError as e:
                    rotti.append(f"{a:04d}-{m:02d} ({type(e).__name__}: {e})")
                    continue
                motivo = controlla_zip(p)
                if motivo is not None:
                    rotti.append(f"{a:04d}-{m:02d} ({motivo})")
                    continue
                presenti += 1
            else:
                manca.append(f"{a:04d}-{m:02d}")
        nome = nome_serie(s, tipo, tf)
        serie[nome] = {"mesi_attesi": len(mesi), "file_leggibili": presenti, "mesi_mancanti": manca,
                       "file_illeggibili": rotti}
        if manca:
            mancanti[nome] = manca
        if rotti:
            illeggibili[nome] = rotti
    return {"periodo": [inizio.isoformat(), fine.isoformat()], "serie": serie, "mancanti": mancanti,
            "illeggibili": illeggibili, "impronte": impronte}


def ferma_se_file_mancanti(fm: Dict[str, object], cosa: str, **altro) -> None:
    """Regola D1: se manca o non si legge anche un solo file mensile, FERMO SUI DATI (nessuna candela
    letta, nessun risultato, ripartenza ammessa con lo stesso lanciatore)."""
    if fm["mancanti"] or fm["illeggibili"]:
        raise FermoSuiDati(
            "D1", f"{cosa} ({fm['periodo'][0]} -> {fm['periodo'][1]}): file mensili mancanti "
                  f"{fm['mancanti'] or 'nessuno'}; illeggibili {fm['illeggibili'] or 'nessuno'}. Nessuna candela "
                  f"letta, candidato non eseguito: si riparte con lo stesso lanciatore dopo aver rimesso i file",
            {"periodo": fm["periodo"], "serie": fm["serie"], "mancanti": fm["mancanti"],
             "illeggibili": fm["illeggibili"], **altro})


def controlla_completezza(*, candele, tolte_last: Sequence[int], tolte_mark: Sequence[int],
                          funding: Sequence[Tuple], btc, inizio: date, fine: date,
                          ms_barra: int, btc_nel_segnale: bool = BTC_NEL_SEGNALE) -> Dict[str, object]:
    """Regola dei dati D2 e D3 sui dati caricati, mese per mese del periodo [inizio, fine].

    ``funding``: righe (ts, ore dichiarate, tasso) di ``dati.carica_funding_dettaglio`` (o coppie
    (ts, tasso): allora le ore dichiarate mancano).

    ``fermano`` (D2, il giro si ferma senza risultato prima di eseguire il candidato): l'ultima barra
    allineata non e' l'ultima barra di ``fine`` al timeframe; un mese ha meno del 50% delle barre
    allineate attese; un mese non ha nessun settlement di funding. Per BTC le stesse condizioni
    fermano solo se ``btc_nel_segnale``; qui (contesto) sono avvisi.

    ``avvisi`` (D3, solo riportati): i mesi sotto il 99% delle barre allineate attese, con le barre
    tolte dall'una e dall'altra parte; BTC. Per ogni mese: barre attese, last, mark, allineate e
    quota; settlement di funding con le ore dichiarate e le distanze osservate fra settlement
    (nessun numero atteso di settlement)."""
    import numpy as np
    from collections import Counter
    da_ms = dati.ms_da_data(inizio)
    a_ms = dati.ms_da_data(fine + timedelta(days=1))
    ts_c = np.array([c.ts for c in candele], dtype=np.int64)
    ts_tl = np.array(sorted(tolte_last), dtype=np.int64)
    ts_tm = np.array(sorted(tolte_mark), dtype=np.int64)
    righe_f = sorted(funding, key=lambda r: r[0])
    ts_f = np.array([int(r[0]) for r in righe_f], dtype=np.int64)
    ore_f = [(int(r[1]) if len(r) >= 3 else None) for r in righe_f]
    def ore_fra(i: int):
        x = round((int(ts_f[i]) - int(ts_f[i - 1])) / dati.MS_ORA, 3)
        return int(x) if x == int(x) else x

    dist_f = [None] + [ore_fra(i) for i in range(1, len(ts_f))]
    ts_b = np.array([c.ts for c in btc], dtype=np.int64) if btc is not None else None

    def conta(arr, lo, hi) -> int:
        return int(np.searchsorted(arr, hi, side="left") - np.searchsorted(arr, lo, side="left"))

    def pct(x: float) -> str:
        return f"{100 * x:.1f}%".replace(".", ",")

    per_mese: Dict[str, Dict[str, object]] = {}
    fermano: List[str] = []
    avvisi: List[str] = []
    for a, m in dati.mesi_del_periodo(inizio, fine):
        chiave = f"{a:04d}-{m:02d}"
        lo = max(dati.ms_da_data(date(a, m, 1)), da_ms)
        hi = min(dati.ms_da_data(date(a + (m == 12), m % 12 + 1, 1)), a_ms)
        attese = (hi - lo) // ms_barra
        nb = conta(ts_c, lo, hi)
        n_tl, n_tm = conta(ts_tl, lo, hi), conta(ts_tm, lo, hi)
        i_f0, i_f1 = int(np.searchsorted(ts_f, lo, side="left")), int(np.searchsorted(ts_f, hi, side="left"))
        quota = nb / attese if attese else None
        riga = {"attese": attese, "last": nb + n_tl, "mark": nb + n_tm, "allineate": nb, "quota": quota,
                "tolte_manca_il_mark": n_tl, "tolte_manca_il_last": n_tm,
                "settlement": i_f1 - i_f0,
                "ore_dichiarate": {str(k): v for k, v in sorted(Counter(
                    o for o in ore_f[i_f0:i_f1] if o is not None).items())},
                "distanze_ore_osservate": {str(k): v for k, v in sorted(Counter(
                    d for d in dist_f[i_f0:i_f1] if d is not None).items())}}
        if attese and nb < QUOTA_BARRE_FERMO * attese:
            fermano.append(f"{chiave}: {nb} barre allineate su {attese} attese ({pct(quota)}), sotto il 50%")
        elif attese and nb < QUOTA_BARRE_AVVISO * attese:
            avvisi.append(f"AVVISO {chiave}: {nb} barre allineate su {attese} attese ({pct(quota)}), sotto il 99% "
                          f"(tolte {n_tl} per mark mancante, {n_tm} per last mancante)")
        riga["avviso_sotto_99"] = bool(attese and nb < QUOTA_BARRE_AVVISO * attese)
        if riga["settlement"] == 0:
            fermano.append(f"{chiave}: nessun settlement di funding")
        if ts_b is not None:
            nbtc = conta(ts_b, lo, hi)
            riga["btc"] = nbtc
            riga["quota_btc"] = nbtc / attese if attese else None
            if attese and nbtc < QUOTA_BARRE_FERMO * attese:
                testo = f"BTC {chiave}: {nbtc} barre su {attese} attese ({pct(nbtc / attese)}), sotto il 50%"
                (fermano if btc_nel_segnale else avvisi).append(testo if btc_nel_segnale else "AVVISO " + testo)
            elif attese and nbtc < QUOTA_BARRE_AVVISO * attese:
                avvisi.append(f"AVVISO BTC {chiave}: {nbtc} barre su {attese} attese ({pct(nbtc / attese)}), sotto il 99%")
        per_mese[chiave] = riga
    ultima_attesa = a_ms - ms_barra
    ultima = int(ts_c[-1]) if len(ts_c) else None
    if ultima != ultima_attesa:
        fermano.append(f"la serie allineata finisce a {iso(ultima)}, non all'ultima barra del "
                       f"{fine.isoformat()} ({iso(ultima_attesa)})")
    if ts_b is None:
        (fermano if btc_nel_segnale else avvisi).append("BTC non caricato: niente correlazione con BTC")
    elif not len(ts_b) or int(ts_b[-1]) != ultima_attesa:
        testo = f"BTC finisce a {iso(int(ts_b[-1]) if len(ts_b) else None)}, non a {iso(ultima_attesa)}"
        (fermano if btc_nel_segnale else avvisi).append(testo if btc_nel_segnale else "AVVISO " + testo)
    # buchi della serie allineata dentro il periodo (barre consecutive a piu' di una barra di distanza)
    nel = ts_c[(ts_c >= da_ms) & (ts_c < a_ms)]
    salti = np.diff(nel) if len(nel) > 1 else np.array([], dtype=np.int64)
    buchi = salti[salti > ms_barra]
    prima = int(nel[0]) if len(nel) else None
    nel_f = [r for r in righe_f if da_ms <= int(r[0]) < a_ms]
    note = {
        "prima_barra_del_periodo": iso(prima), "prima_barra_attesa": iso(da_ms),
        "ultima_barra": iso(ultima), "ultima_barra_attesa": iso(ultima_attesa),
        "barre_ultimo_giorno": conta(ts_c, a_ms - dati.MS_GIORNO, a_ms),
        "barre_attese_ultimo_giorno": dati.MS_GIORNO // ms_barra,
        "buchi_nel_periodo": int(len(buchi)),
        "barre_mancanti_nel_periodo": int((a_ms - da_ms) // ms_barra - len(nel)),
        "buco_piu_lungo_barre": int(buchi.max() // ms_barra - 1) if len(buchi) else 0,
        "funding_nel_periodo": len(nel_f),
        "intervalli_funding_dichiarati": [[iso(int(ts)), ore] for ts, ore in dati.intervallo_funding(nel_f)]
        if nel_f and len(nel_f[0]) >= 3 else None,
        "mesi_sotto_il_99": sum(1 for r in per_mese.values() if r["avviso_sotto_99"]),
    }
    return {"periodo": [inizio.isoformat(), fine.isoformat()],
            "regola": {"fermo_sotto_quota_barre": QUOTA_BARRE_FERMO, "avviso_sotto_quota_barre": QUOTA_BARRE_AVVISO,
                       "fermo_mese_senza_settlement": True, "fermo_ultima_barra": iso(ultima_attesa),
                       "btc_nel_segnale": btc_nel_segnale,
                       "nota": ("D2: fermano il giro prima di eseguire il candidato, senza risultato; "
                                "D3: tutto il resto e' solo riportato")},
            "per_mese": per_mese, "note": note, "fermano": fermano, "avvisi": avvisi}


# ---------------------------------------------------------------------------
# Guardia «una volta sola», marcatore e impronta del giro (requisiti R2 e R3)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Percorsi:
    finale: Path        # il risultato (JSON): la guardia «una volta sola»
    riassunto: Path     # il riassunto .md, scritto dopo il JSON
    marcatore: Path     # scritto prima di caricare i dati del periodo
    avanzamento: Path   # cartella: impronta.json, b.json e i pezzi delle simulazioni

    @classmethod
    def vault(cls) -> "Percorsi":
        return cls(finale=VAULT_COORD / f"{CANDIDATO}_vault.json", riassunto=VAULT_COORD / f"{CANDIDATO}_vault.md",
                   marcatore=VAULT_COORD / f"{CANDIDATO}_giro_iniziato.json", avanzamento=AVANZAMENTO_VAULT)

    @classmethod
    def prova(cls, cartella: Path) -> "Percorsi":
        c = Path(cartella)
        return cls(finale=c / f"{CANDIDATO}_vault.json", riassunto=c / f"{CANDIDATO}_vault.md",
                   marcatore=c / f"{CANDIDATO}_giro_iniziato.json", avanzamento=c / "avanzamento" / CANDIDATO)


assert not dentro(AVANZAMENTO_VAULT, VAULT_COORD)  # l'avanzamento non sta in research/vault/


@contextlib.contextmanager
def lucchetto(cartella: Path):
    """Un solo lanciatore alla volta sulla stessa cartella d'avanzamento (il file resta)."""
    Path(cartella).mkdir(parents=True, exist_ok=True)
    with open(Path(cartella) / ".lucchetto", "w") as f:
        try:
            fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise GiaEseguito(f"un altro lanciatore sta gia' lavorando su {cartella}")
        yield


def _leggi_marcatore(percorsi: Percorsi) -> Dict[str, object]:
    try:
        m = json.loads(percorsi.marcatore.read_text(encoding="utf-8"))
    except ValueError:
        raise GiaEseguito(f"{percorsi.marcatore} esiste e non e' leggibile: un giro e' gia' iniziato")
    if not isinstance(m, dict):
        raise GiaEseguito(f"{percorsi.marcatore} esiste e non e' un marcatore: un giro e' gia' iniziato")
    return m


def guardia_iniziale(percorsi: Percorsi) -> Optional[Dict[str, object]]:
    """Prima di tutto, in sola lettura: il risultato non deve esistere; un marcatore puo' esistere
    solo se l'ha scritto questo stesso lanciatore e se non dice che il risultato e' gia' stato scritto
    (la ripartenza o la ripresa si decidono dopo, in ``prendi_marcatore`` e ``fissa_impronta``)."""
    if percorsi.finale.exists():
        raise GiaEseguito(f"{percorsi.finale} esiste gia': il vault si giudica una volta sola, non si riparte")
    if percorsi.marcatore.exists():
        m = _leggi_marcatore(percorsi)
        if m.get("sha256_lanciatore") != SHA256_LANCIATORE:
            nota = (" Il candidato non e' mai stato eseguito: ripartire con un lanciatore diverso chiede la "
                    "decisione del proprietario e la rimozione a mano del marcatore."
                    if m.get("candidato_eseguito") is False else "")
            raise GiaEseguito(f"{percorsi.marcatore} esiste ed e' di un altro lanciatore "
                              f"(sha256 {m.get('sha256_lanciatore')}, ora {SHA256_LANCIATORE}): "
                              f"non si riparte con un lanciatore diverso.{nota}")
        if m.get("risultato_scritto"):
            raise GiaEseguito(f"{percorsi.marcatore} dice che il risultato e' gia' stato scritto "
                              f"({m.get('risultato_scritto')}): il vault si giudica una volta sola")
        return m
    return None


def contenuto_impronta(etichetta: str, codice: Dict[str, str], file_dati: Dict[str, str],
                       sha256_apertura: Optional[str], regole: Dict[str, object]) -> Dict[str, object]:
    """Cosa identifica un giro: lanciatore, codice del candidato, ogni file di dati, apertura, semi e
    versioni di python, numpy e scipy (D5)."""
    return {"candidato": CANDIDATO, "etichetta": etichetta, "commit": COMMIT,
            "sha256_lanciatore": SHA256_LANCIATORE, "codice": dict(sorted(codice.items())),
            "dati": dict(sorted(file_dati.items())), "sha256_apertura": sha256_apertura,
            "semi_caso": [SEMI_CASO[0], SEMI_CASO[-1], len(SEMI_CASO)],
            "semi_b": [regole["primo_seme_b"], regole["ultimo_seme_b"]], "blocco_semi": BLOCCO_SEMI,
            "versioni": versioni_impronta()}


def impronta_di(contenuto: Dict[str, object]) -> str:
    return sha256_testo(json.dumps(json_sicuro(contenuto), sort_keys=True, ensure_ascii=False))


def _con_storia(m: Dict[str, object], **campi) -> Dict[str, object]:
    tentativo = campi.pop("tentativo", None)
    m.update(campi)
    voce = {"quando": adesso()}
    for k in ("stato", "motivo"):
        if k in campi:
            voce[k] = campi[k]
    if tentativo is not None:
        voce["tentativo"] = tentativo
    m.setdefault("storia", []).append(voce)
    return m


def prendi_marcatore(percorsi: Percorsi) -> Dict[str, object]:
    """Il marcatore «giro iniziato», creato in modo esclusivo (O_EXCL) prima di qualunque controllo
    dei dati del periodo. Se c'e' gia' (stesso lanciatore, controllato da ``guardia_iniziale``):
    candidato mai eseguito -> si riparte (nuovo tentativo); candidato eseguito -> ripresa, che
    ``fissa_impronta`` ammette solo con la stessa impronta, prima di caricare i dati."""
    if percorsi.finale.exists():
        raise GiaEseguito(f"{percorsi.finale} esiste gia': il vault si giudica una volta sola")
    m = guardia_iniziale(percorsi)
    if m is not None:
        tentativo = int(m.get("tentativi", 1)) + 1
        if m.get("candidato_eseguito"):
            _con_storia(m, tentativi=tentativo, tentativo=tentativo,
                        stato="ripresa: il candidato era gia' stato eseguito, si riprende solo con la stessa impronta")
        else:
            m.setdefault("motivi_precedenti", []).append(m.get("motivo"))
            _con_storia(m, tentativi=tentativo, tentativo=tentativo, motivo=None,
                        stato="ripartito: candidato non ancora eseguito")
        scrivi_json(percorsi.marcatore, m)
        return m
    m = {"motivo": None, "stato": "iniziato: candidato non ancora eseguito", "candidato_eseguito": False,
         "candidato": CANDIDATO, "creato": adesso(), "tentativi": 1,
         "sha256_lanciatore": SHA256_LANCIATORE, "lanciatore": str(Path(__file__).resolve()),
         "impronta_giro": None, "impronta": None, "fermate_sui_dati": [],
         "storia": [{"quando": adesso(), "stato": "iniziato: candidato non ancora eseguito", "tentativo": 1}]}
    scrivi_json_esclusivo(percorsi.marcatore, m)
    return m


def fissa_impronta(percorsi: Percorsi, impronta_giro: str, contenuto: Dict[str, object]) -> Dict[str, object]:
    """Dopo il controllo dei file (D1) e PRIMA di caricare i dati: l'impronta del giro nel marcatore.
    Se il candidato e' gia' stato eseguito, si va avanti solo con la stessa impronta (ripresa)."""
    m = _leggi_marcatore(percorsi)
    if m.get("candidato_eseguito"):
        if m.get("impronta_giro") != impronta_giro:
            raise GiaEseguito(f"{percorsi.marcatore}: il candidato e' gia' stato eseguito in un altro giro (impronta "
                              f"{m.get('impronta_giro')}, ora {impronta_giro}): il vault si giudica una volta sola")
        m["riprese"] = int(m.get("riprese", 0)) + 1
        _con_storia(m, stato="ripresa dello stesso giro (stessa impronta): si caricano i dati")
    else:
        if m.get("impronta_giro") not in (None, impronta_giro):
            m.setdefault("impronte_precedenti", []).append(m.get("impronta_giro"))
        _con_storia(m, impronta_giro=impronta_giro, impronta=contenuto,
                    stato="file controllati, impronta fissata: si caricano i dati; candidato non ancora eseguito")
    scrivi_json(percorsi.marcatore, m)
    return m


def segna_esecuzione(percorsi: Percorsi, impronta_giro: str) -> None:
    """Il punto di non ritorno (D4): da qui ogni fine scrive un risultato. Se il marcatore non si
    aggiorna, il candidato non parte (l'eccezione sale prima dell'esecuzione)."""
    m = _leggi_marcatore(percorsi)
    if m.get("impronta_giro") != impronta_giro:
        raise Stop(f"{percorsi.marcatore}: impronta cambiata durante il giro")
    if not m.get("candidato_eseguito"):
        _con_storia(m, candidato_eseguito=True, eseguito_dal=adesso(),
                    stato="candidato in esecuzione: da qui ogni fine scrive un risultato")
        scrivi_json(percorsi.marcatore, m)


def aggiorna_marcatore(percorsi: Percorsi, **campi) -> None:
    """Aggiorna il marcatore e ne allunga la storia; un errore qui si dice e basta."""
    try:
        m = _leggi_marcatore(percorsi)
        scrivi_json(percorsi.marcatore, _con_storia(m, **campi))
    except Exception as e:  # noqa: BLE001 - il marcatore e' una nota: il suo errore non copre quello vero
        print(f"avviso: marcatore non aggiornato ({e})", file=sys.stderr)


def registra_fermo(percorsi: Percorsi, e: FermoSuiDati) -> None:
    """D1/D2: nessun risultato; il marcatore registra la fermata e i dettagli (es. la tabella dei mesi)."""
    try:
        m = _leggi_marcatore(percorsi)
        m.setdefault("fermate_sui_dati", []).append({"quando": adesso(), "regola": e.regola, "motivo": e.motivo,
                                                     "dettagli": e.dettagli})
        scrivi_json(percorsi.marcatore, _con_storia(m, stato=STATO_FERMO, motivo=f"{e.regola}: {e.motivo}"))
    except Exception as x:  # noqa: BLE001
        print(f"avviso: marcatore non aggiornato ({x})", file=sys.stderr)


class Avanzamento:
    """La cartella dell'avanzamento: ``impronta.json``, ``b.json`` e un file per pezzo di simulazioni.

    L'impronta dell'avanzamento e' lo SHA-256 dell'impronta del giro (lanciatore, codice, dati) e
    della chiave dell'esecuzione (trade del candidato, barre vietate, funding, semi); ogni file la
    porta. Alla ripresa: pezzi senza ``impronta.json``, ``impronta.json`` diversa, pezzi senza
    impronta o con un'impronta diversa, o con semi diversi da quelli del loro posto -> STOP: non si
    riusano e non si sovrascrivono.
    """

    def __init__(self, cartella: Path, impronta_giro: str, contenuto: Dict[str, object], chiave: Dict[str, object]):
        self.cartella = Path(cartella)
        self.impronta_giro = impronta_giro
        self.contenuto = contenuto
        self.chiave = chiave
        self.impronta = sha256_testo(json.dumps(json_sicuro({"impronta_giro": impronta_giro, "chiave": chiave}),
                                                sort_keys=True))
        self.aperture_precedenti = 0

    @property
    def file_impronta(self) -> Path:
        return self.cartella / "impronta.json"

    @property
    def file_b(self) -> Path:
        return self.cartella / "b.json"

    def _pezzi(self) -> List[Path]:
        return sorted(self.cartella.glob("pezzo_*.json"))

    def apri(self) -> None:
        self.cartella.mkdir(parents=True, exist_ok=True)
        pezzi = self._pezzi() + ([self.file_b] if self.file_b.exists() else [])
        if not self.file_impronta.exists():
            if pezzi:
                raise Stop(f"avanzamento {self.cartella}: ci sono pezzi ({[p.name for p in pezzi]}) ma manca "
                           f"impronta.json: non li riuso ne' li sovrascrivo")
            scrivi_json(self.file_impronta, {"impronta": self.impronta, "impronta_giro": self.impronta_giro,
                                             "contenuto": self.contenuto, "chiave": self.chiave,
                                             "aperture": [adesso()]})
            return
        d = leggi_json(self.file_impronta, "avanzamento")
        if d.get("impronta") != self.impronta:
            raise Stop(f"avanzamento {self.cartella}: impronta.json e' di un altro giro (impronta "
                       f"{d.get('impronta')}, ora {self.impronta}): non lo riuso ne' lo sovrascrivo")
        for p in pezzi:
            x = leggi_json(p, "avanzamento")
            if not isinstance(x, dict) or "impronta" not in x:
                raise Stop(f"avanzamento {self.cartella}: {p.name} senza impronta: non lo riuso")
            if x["impronta"] != self.impronta:
                raise Stop(f"avanzamento {self.cartella}: {p.name} ha un'impronta diversa ({x['impronta']}): "
                           f"non lo riuso")
        self.aperture_precedenti = len(d.get("aperture", []))
        d["aperture"] = list(d.get("aperture", [])) + [adesso()]
        scrivi_json(self.file_impronta, d)

    def leggi_b(self) -> Optional[Dict[str, object]]:
        if not self.file_b.exists():
            return None
        return leggi_json(self.file_b, "avanzamento")["b"]

    def scrivi_b(self, b: Dict[str, object]) -> None:
        scrivi_json(self.file_b, {"impronta": self.impronta, "b": b, "scritto": adesso()})

    def leggi_simulazioni(self) -> Dict[str, Dict[str, object]]:
        sims: Dict[str, Dict[str, object]] = {}
        for p in self._pezzi():
            x = leggi_json(p, "avanzamento")
            try:
                k = int(p.stem.split("_")[1])
            except (IndexError, ValueError):
                raise Stop(f"avanzamento {self.cartella}: nome di pezzo inatteso {p.name}")
            attesi = SEMI_CASO[k * BLOCCO_SEMI:(k + 1) * BLOCCO_SEMI]
            if x.get("semi") != attesi or sorted(int(s) for s in x.get("simulazioni", {})) != attesi:
                raise Stop(f"avanzamento {self.cartella}: {p.name} non ha i semi del suo posto ({attesi[:1]}..)")
            sims.update(x["simulazioni"])
        return sims

    def scrivi_pezzo(self, k: int, semi: List[int], simulazioni: Dict[str, Dict[str, object]]) -> None:
        scrivi_json(self.cartella / f"pezzo_{k:04d}.json",
                    {"impronta": self.impronta, "semi": semi, "simulazioni": simulazioni, "scritto": adesso()})


# ---------------------------------------------------------------------------
# Il motore del modo vault (provato sul periodo di validazione)
# ---------------------------------------------------------------------------


def _confronto_btc(trades, btc) -> Dict[str, object]:
    """Gemella di comune.confronto_btc con le candele BTC gia' caricate (stesso calcolo)."""
    import numpy as np
    ts = np.array([c.ts for c in btc], dtype=np.int64)
    op = np.array([c.open for c in btc])
    cl = np.array([c.close for c in btc])
    rb, rr, rm = [], [], []
    for t in trades:
        a = np.searchsorted(ts, t.ts_entrata)
        b = np.searchsorted(ts, t.ts_uscita, side="right") - 1
        if a < len(ts) and b >= a:
            rb.append(cl[b] / op[a] - 1)
            rr.append(t.r)
            rm.append((t.uscita / t.entrata - 1) * (1 if t.direzione == "long" else -1))
    if len(rb) < 3:
        return {"n": len(rb)}
    return {"n": len(rb), "corr_r_btc": float(np.corrcoef(rr, rb)[0, 1]),
            "btc_medio_nella_finestra": float(np.mean(rb)),
            "corr_movimento_moneta_btc": float(np.corrcoef(rm, np.array(rb) * (1 if trades[0].direzione == "long" else -1))[0, 1])}


# stato condiviso con i processi figli (fork): impostato prima di creare il pool
_G: Dict[str, object] = {}


def _simula_seme(arg: Tuple[int, Tuple[int, ...]]) -> Dict[str, object]:
    """Una strategia a entrate casuali, eseguita come in simula_baseline_casuale, con le sue metriche."""
    seme, ingressi = arg
    crea = _G["crea_casuale"]
    strategia = crea(frozenset(ingressi))
    ris = motore.esegui(_G["candele"], None, _G["mark"], list(_G["funding"]), strategia, _G["parametri"])
    out = {"seme": seme, "n_ingressi": len(ingressi), "n_trade": len(ris.trades),
           "segnali_non_validi": ris.n_segnali_non_validi, "segnali_senza_barra": ris.n_segnali_senza_barra}
    if not ris.trades:
        out.update({"r_medio": None, "profit_factor": 0.0, "rendimento_totale": 0.0, "drawdown_max": 0.0,
                    "prima_entrata_ts": None})
        return out
    # R medio calcolato come simula_baseline_casuale (stessa somma, stesso ordine)
    out["r_medio"] = sum(t.r for t in ris.trades) / len(ris.trades)
    m = C._metriche_trade(ris.trades)
    out["profit_factor"] = m["profit_factor"]
    out["rendimento_totale"] = m["rendimento_totale"]
    out["drawdown_max"] = m["drawdown_max"]
    out["prima_entrata_ts"] = min(t.ts_entrata for t in ris.trades)
    return out


def _esegui_semi(argomenti: List[Tuple[int, Tuple[int, ...]]], processi: int) -> List[Dict[str, object]]:
    if processi <= 1:
        return [_simula_seme(a) for a in argomenti]
    import multiprocessing as mp
    with mp.get_context("fork").Pool(processi) as pool:
        return pool.map(_simula_seme, argomenti, chunksize=max(1, len(argomenti) // (processi * 4)))


def scrivi_risultato(percorsi: Percorsi, out: Dict[str, object]) -> None:
    """Prima il JSON (creato solo se non esiste: e' lui la guardia), poi il riassunto .md."""
    scrivi_json_esclusivo(percorsi.finale, out)
    try:
        scrivi_testo(percorsi.riassunto, riassunto_md(out))
    except Exception as e:  # noqa: BLE001 - il JSON c'e': il .md mancante si dice, non ferma
        aggiorna_marcatore(percorsi, errore_riassunto=f"{type(e).__name__}: {e}")
        print(f"avviso: riassunto .md non scritto ({type(e).__name__}: {e})", file=sys.stderr)


def esame_periodo(*, etichetta: str, percorsi: Percorsi, prepara: Callable[[], Dict[str, object]],
                  carica: Callable[[], Dict[str, object]], inizio_ts: int, fine: date,
                  regole: Dict[str, object], info: Dict[str, object], dati_obbligatori: bool = True,
                  processi: int = 1, interrompi_dopo_pezzi: Optional[int] = None) -> Dict[str, object]:
    """Il giudizio del candidato su un periodo: trade entrati da ``inizio_ts``, serie calda dall'inizio.

    Nel modo vault ``inizio_ts`` e' il 2024-01-01 00:00 UTC e ``fine`` il 2026-09-30; nella prova
    e' l'inizio della validazione (2022-10-29) con fine 2023-12-31. Chi chiama tiene il lucchetto.

    Ordine: marcatore (O_EXCL); ``prepara()`` = regola D1 sui file, nessuna candela letta, ritorna il
    contenuto dell'impronta; impronta nel marcatore; ``carica()`` = dati e completezza; regola D2
    (``completezza["fermano"]``, se ``dati_obbligatori``); marcatore «candidato in esecuzione»;
    giudizio. Prima dell'esecuzione del candidato ogni fermata o errore NON scrive un risultato (il
    marcatore lo registra e si riparte con lo stesso lanciatore); dopo (D4) ogni uscita scrive il
    risultato, salvo un'interruzione (giro da riprendere con la stessa impronta).
    """
    if percorsi.finale.exists():
        raise GiaEseguito(f"{percorsi.finale} esiste gia': il vault si giudica una volta sola, il lanciatore non riparte")
    marcatore = prendi_marcatore(percorsi)
    info["marcatore"] = {"percorso": str(percorsi.marcatore), "creato": marcatore["creato"],
                         "tentativo": marcatore.get("tentativi", 1)}
    eseguito = False
    base: Dict[str, object] = {}
    try:
        # D1: file mensili presenti e leggibili (nessuna candela letta); contenuto dell'impronta
        t0 = time.perf_counter()
        prep = prepara()
        info.update(prep.get("info", {}))
        info["controllo_file_secondi"] = time.perf_counter() - t0
        contenuto = prep["contenuto"]
        impronta_giro = impronta_di(contenuto)
        fissa_impronta(percorsi, impronta_giro, contenuto)
        base = {
            "candidato": CANDIDATO, "etichetta": etichetta, "simbolo": SIMBOLO, "timeframe": TF, "direzione": "long",
            "esito": None,
            "periodo": {"serie_da": C.INIZIO.isoformat(), "fine_chiesta": fine.isoformat(),
                        "trade_entrati_da_ts": inizio_ts, "trade_entrati_da": datetime.fromtimestamp(
                            inizio_ts / 1000, tz=timezone.utc).isoformat()},
            "sha256_lanciatore": SHA256_LANCIATORE, "lanciatore": str(Path(__file__).resolve()),
            "versioni": versioni(),
            "semi": {"caso": [SEMI_CASO[0], SEMI_CASO[-1]], "n_caso": len(SEMI_CASO),
                     "b": [regole["primo_seme_b"], regole["ultimo_seme_b"]], "bootstrap": regole["bootstrap_seme"]},
            "impronta_giro": impronta_giro,
            "regole_esame": regole,
            "info": info,
            "iniziato": adesso(),
        }
        # caricamento (le candele si leggono QUI) e D2
        t0 = time.perf_counter()
        d = carica()
        info["caricamento"] = dict(d.get("info", {}), secondi=time.perf_counter() - t0)
        comp = d["completezza"]
        info["completezza"] = comp
        if comp["fermano"] and dati_obbligatori:
            raise FermoSuiDati("D2", "dati del periodo sotto le soglie della regola: " + "; ".join(comp["fermano"]) +
                               ". Candidato non eseguito, nessun risultato",
                               {"completezza": comp, "caricamento": info["caricamento"]})
        # D4: da qui ogni fine scrive un risultato
        segna_esecuzione(percorsi, impronta_giro)
        eseguito = True
        out = _esame_dentro(base=base, d=d, percorsi=percorsi, inizio_ts=inizio_ts, fine=fine, regole=regole,
                            impronta_giro=impronta_giro, contenuto=contenuto, processi=processi,
                            interrompi_dopo_pezzi=interrompi_dopo_pezzi)
    except GiaEseguito:
        raise  # un altro giro (o un altro lanciatore): nessuna scrittura
    except (Interrotto, KeyboardInterrupt) as e:
        aggiorna_marcatore(percorsi, motivo=f"interruzione: {type(e).__name__}: {e}", stato=(
            "interrotto durante il giro: si riprende con la stessa impronta" if eseguito else
            "interrotto prima dell'esecuzione del candidato: candidato non eseguito, si riparte"))
        raise
    except Exception as e:  # noqa: BLE001
        if not eseguito:
            if isinstance(e, FermoSuiDati):
                registra_fermo(percorsi, e)
            else:
                aggiorna_marcatore(percorsi, motivo=f"{type(e).__name__}: {e}",
                                   traceback_prima_dell_esecuzione=traceback.format_exc()[-6000:],
                                   stato="errore prima dell'esecuzione del candidato: candidato non eseguito, "
                                         "nessun risultato")
            raise  # niente risultato: il vault non e' consumato
        out = dict(base)  # D4: dopo l'esecuzione del candidato ogni uscita lascia un risultato
        out["esito"] = "STOP" if isinstance(e, (Stop, FermoSuiDati)) else "errore"
        out["motivo"] = f"{type(e).__name__}: {e}"
        out["traceback"] = traceback.format_exc()[-6000:]
        out["finito"] = adesso()
    scrivi_risultato(percorsi, out)
    aggiorna_marcatore(percorsi, motivo=None, stato=f"risultato scritto: {out['esito']}", finito=adesso(),
                       risultato_scritto=str(percorsi.finale))
    return out


def _esame_dentro(*, base, d, percorsi, inizio_ts, fine, regole, impronta_giro, contenuto, processi,
                  interrompi_dopo_pezzi):
    import numpy as np
    candele, mark, funding, ms_barra = d["candele"], d["mark"], d["funding"], d["ms_barra"]
    tempi: Dict[str, float] = {}
    t_tot = time.perf_counter()

    v = V.i03(TF, f"{CANDIDATO}-{base['etichetta']}", **KW_VARIANTE)
    p = C.parametri()
    n = len(candele)
    if n == 0:
        raise Stop("serie vuota")
    primo = next((i for i, c in enumerate(candele) if c.ts >= inizio_ts), None)
    if primo is None:
        raise Stop("nessuna barra dopo l'inizio del periodo")

    # 1. il candidato (stessa esecuzione di comune.valuta)
    t0 = time.perf_counter()
    ris = motore.esegui(candele, None, mark, funding, C.fabbrica(v, candele)(), p)
    tempi["candidato_s"] = time.perf_counter() - t0
    trades = [t for t in ris.trades if t.ts_entrata >= inizio_ts]
    m = C._metriche_trade(trades)
    m["buchi_dati"] = ris.n_buchi_dati
    m["segnali_non_validi"] = ris.n_segnali_non_validi
    out: Dict[str, object] = dict(base)
    out["periodo"] = dict(base["periodo"], barre_serie=n, prima_barra_del_periodo=primo, barre_del_periodo=n - primo,
                          prima_barra_serie=iso(candele[0].ts), prima_barra_periodo=iso(candele[primo].ts),
                          ultima_barra=iso(candele[-1].ts), ultima_barra_ts=candele[-1].ts)
    out["metriche"] = m
    out["buy_and_hold_per_anno"] = C.buy_and_hold_per_anno(candele, inizio_ts)
    out["trade_del_periodo"] = [{"ts_entrata": t.ts_entrata, "ts_uscita": t.ts_uscita, "entrata": t.entrata,
                                 "uscita": t.uscita, "stop": t.stop, "esito": t.esito, "r": t.r, "pnl": t.pnl}
                                for t in sorted(trades, key=lambda t: t.ts_uscita)]
    n_trade = len(trades)
    comp_note = d["completezza"]["note"]
    ultimo = trades and max(trades, key=lambda t: t.ts_uscita)
    out["note_ultimo_giorno_e_buchi"] = {
        **comp_note,
        "fine_chiesta": fine.isoformat(),
        "trade_chiusi_a_fine_dati": m["esiti"].get("fine_dati", 0),
        "ultimo_trade_uscita": iso(ultimo.ts_uscita) if ultimo else None,
        "ultimo_trade_esito": ultimo.esito if ultimo else None,
        "buchi_contati_dal_motore_su_tutta_la_serie": ris.n_buchi_dati,
        "funding_in_buco_su_tutta_la_serie": getattr(ris, "n_funding_in_buco", None),
        "mesi_sotto_il_100_per_cento": {k: f"{r['allineate']}/{r['attese']}" for k, r in
                                        d["completezza"]["per_mese"].items() if r["allineate"] < r["attese"]},
        "avvisi_dei_dati": d["completezza"]["avvisi"],
        "nota": ("una posizione ancora aperta all'ultima barra si chiude a fine dati (esito fine_dati), "
                 "come in validazione; i buchi sono barre tolte dall'allineamento last/mark o assenti nei file"),
    }

    # 2. blocco e (a), solo per il rapporto (come comune.valuta)
    r = C._r_ordinati(trades) if trades else np.array([])
    blocco = None
    if n_trade >= 2:
        blocco = statistica.lunghezza_blocco([t.ts_entrata for t in trades], [t.ts_uscita for t in trades])
        out["blocco"] = blocco
        t0 = time.perf_counter()
        ris_a = motore.esegui(candele, None, mark, funding, C.fabbrica(v, candele, con_condizione=False)(), p)
        tempi["baseline_a_s"] = time.perf_counter() - t0
        trades_a = [t for t in ris_a.trades if t.ts_entrata >= inizio_ts]
        if len(trades_a) >= 2:
            blocco_a = statistica.lunghezza_blocco([t.ts_entrata for t in trades_a], [t.ts_uscita for t in trades_a])
            base_a = statistica.baseline_da_trade(C._r_ordinati(trades_a), blocco_a, regole["bootstrap_n"],
                                                  regole["bootstrap_seme"])
            ca = statistica.contro_baseline(r, blocco, base_a, regole["bootstrap_n"], regole["bootstrap_seme"])
            out["baseline_a"] = {"media": base_a["media"], "errore_standard": base_a["errore_standard"],
                                 "n_trade": base_a["n_trade"], "blocco_a": blocco_a, "n_blocchi_a": base_a["n_blocchi"],
                                 "t": ca["t"], "soglia": ca["soglia"], "netta": ca["netta"],
                                 "valutabile": ca["valutabile"] and base_a["valutabile"],
                                 "differenza": ca["differenza"], "errore_standard_differenza": ca["errore_standard"],
                                 "pavimento_errore": ca["errore_minimo"], "n_blocchi": ca["n_blocchi"]}
        else:
            out["baseline_a"] = {"valutabile": False, "netta": False, "t": "-inf", "n_trade": len(trades_a)}
    else:
        out["non_valutabile_per_il_rapporto"] = "meno di 2 trade: niente blocco, (a) e (b) del rapporto"

    sotto_minimo = n_trade < regole["trade_minimi"]
    motivo_minimo = (f"{n_trade} trade nel periodo, sotto i trade minimi del vault ({regole['trade_minimi']}): "
                     f"sezione 8, l'esito e' «non si sa» e il candidato non va avanti")
    if n_trade == 0:
        out["criterio_vault"] = None
        out["caso"] = None
        out["tasso_del_caso"] = None
        out["nota_caso"] = "nessun trade nel periodo: le entrate casuali (stesso numero di trade) non si costruiscono"
        out["esito"] = "non si sa"
        out["esito_motivo"] = motivo_minimo
        out["btc_stessa_finestra"] = {"n": 0}
        out["tempi_s"] = tempi
        out["finito"] = adesso()
        return out

    # 3. barre vietate alle entrate casuali (come la (b) della campagna) e durata media
    t0 = time.perf_counter()
    vietate = motore.barre_vietate_segnale_non_valido(candele, C.fabbrica_segnale(v, candele), p)
    tempi["barre_vietate_s"] = time.perf_counter() - t0
    n_vietate_segnale = sum(b - a for a, b in vietate)
    ctx = C.contesto(v, candele)
    vietate = vietate + C.intervalli(ctx.esclusi)
    vietate.append((0, primo))
    durata = motore.durata_media_barre(trades, ms_barra)
    out["durata_media_barre"] = durata
    vietate_con_ultima = list(vietate) + [(n - 1, n)]  # come simula_baseline_casuale
    ammesse = np.ones(n, dtype=bool)
    for a, b in vietate_con_ultima:
        ammesse[max(0, a):min(n, b)] = False
    out["barre_vietate"] = {"segnale_non_valido": n_vietate_segnale, "mesi_esclusi": int(ctx.esclusi.sum()),
                            "prima_del_periodo": primo, "ultima_barra": 1,
                            "ammesse": int(ammesse.sum()), "quota_segnale_non_valido": n_vietate_segnale / n}

    # 4. avanzamento con impronta (lanciatore, codice, dati e chiave dell'esecuzione)
    chiave = {
        "candidato": CANDIDATO, "etichetta": base["etichetta"], "commit": COMMIT,
        "codice": {k: v_ for k, v_ in IMPRONTE_CODICE.items()},
        "n_barre": n, "ts_prima": candele[0].ts, "ts_ultima": candele[-1].ts, "inizio_ts": inizio_ts,
        "n_trade": n_trade, "durata": durata, "semi_caso": [SEMI_CASO[0], SEMI_CASO[-1], len(SEMI_CASO)],
        "sha_vietate": sha256_testo(json.dumps(vietate_con_ultima)),
        "sha_trade": sha256_testo(json.dumps([[t.ts_entrata, t.ts_uscita, repr(t.r)] for t in trades])),
        "sha_funding": sha256_testo(json.dumps([[a, repr(b)] for a, b in funding])),
    }
    avz = Avanzamento(percorsi.avanzamento, impronta_giro, contenuto, chiave)
    avz.apri()
    stato_b = avz.leggi_b()
    simulazioni = avz.leggi_simulazioni()
    out["ripresa"] = {"simulazioni_riprese_dal_file": len(simulazioni), "aperture_precedenti": avz.aperture_precedenti,
                      "b_ripresa": stato_b is not None, "impronta_avanzamento": avz.impronta,
                      "cartella_avanzamento": str(percorsi.avanzamento)}

    # 5. la (b) della campagna sul periodo (200 semi), per il rapporto e per la prova della gemella
    if stato_b is None:
        t0 = time.perf_counter()
        try:
            base_b = motore.simula_baseline_casuale(
                candele, C.fabbrica_casuale(v, candele), n_trade, durata, p, candele_mark=mark, funding=funding,
                barre_vietate=vietate, n_simulazioni=regole["simulazioni_b"], primo_seme=regole["primo_seme_b"])
            stato_b = {k: base_b[k] for k in ("valori", "trade_per_simulazione", "simulazioni_vuote",
                                              "segnali_non_validi_per_simulazione",
                                              "segnali_senza_barra_per_simulazione")}
            stato_b["secondi"] = time.perf_counter() - t0
        except ValueError as e:
            stato_b = {"errore": str(e), "secondi": time.perf_counter() - t0}
        avz.scrivi_b(json_sicuro(stato_b))
    tempi["baseline_b_200_s"] = float(stato_b.get("secondi", 0.0))
    base_b = None
    if "errore" not in stato_b:
        base_b = statistica.baseline_casuale([float(x) for x in stato_b["valori"]])
        for k in ("trade_per_simulazione", "simulazioni_vuote", "segnali_non_validi_per_simulazione",
                  "segnali_senza_barra_per_simulazione"):
            base_b[k] = stato_b[k]
        if blocco is not None:
            cb = statistica.contro_baseline(r, blocco, base_b, regole["bootstrap_n"], regole["bootstrap_seme"])
            out["baseline_b"] = C._riassunto_b(base_b, cb, n_vietate_segnale / n)
            out["percentile_caso"] = statistica.percentile_del_candidato(float(r.mean()), base_b["valori"])
    else:
        out["baseline_b"] = {"valutabile": False, "netta": False, "t": "-inf", "errore": stato_b["errore"]}

    # 6. le 1000 entrate casuali: stessi ingressi di statistica.entrate_casuali_per_semi, a pezzi
    t0 = time.perf_counter()
    try:
        tutti = statistica.entrate_casuali_per_semi(n, n_trade, durata, SEMI_CASO, vietate_con_ultima)
    except ValueError as e:
        out["criterio_vault"] = None
        out["caso"] = None
        out["tasso_del_caso"] = None
        out["nota_caso"] = f"entrate casuali non costruibili: {e}"
        out["esito"] = "non si sa" if sotto_minimo else "non valutabile"
        out["esito_motivo"] = (motivo_minimo + "; inoltre " + out["nota_caso"]) if sotto_minimo else (
            "le 1000 entrate casuali con lo stesso numero di trade non si possono costruire: " + str(e))
        out["btc_stessa_finestra"] = _btc_sicuro(trades, d)
        out["tempi_s"] = tempi
        out["finito"] = adesso()
        return out
    tempi["ingressi_1000_s"] = time.perf_counter() - t0
    ingressi_per_seme = {s: tuple(ing) for s, ing in zip(SEMI_CASO, tutti)}
    for s, ing in ingressi_per_seme.items():
        if any(not ammesse[i] for i in ing) or len(ing) != n_trade:
            raise Stop(f"seme {s}: ingressi fuori dalle barre ammesse")

    _G.update({"candele": candele, "mark": mark, "funding": funding, "parametri": p,
               "crea_casuale": C.fabbrica_casuale(v, candele)})
    semi_b = list(range(regole["primo_seme_b"], regole["ultimo_seme_b"] + 1))
    gemella: Optional[Dict[str, object]] = None
    pezzi_fatti = 0
    t_sim = time.perf_counter()
    n_calcolate = 0
    for k in range(0, len(SEMI_CASO), BLOCCO_SEMI):
        semi_pezzo = SEMI_CASO[k:k + BLOCCO_SEMI]
        if not all(str(s) in simulazioni for s in semi_pezzo):
            if interrompi_dopo_pezzi is not None and pezzi_fatti >= interrompi_dopo_pezzi:
                raise Interrotto(f"interruzione voluta dopo {pezzi_fatti} pezzi")
            nuovi = {str(res_s["seme"]): res_s for res_s in
                     _esegui_semi([(s, ingressi_per_seme[s]) for s in semi_pezzo], processi)}
            avz.scrivi_pezzo(k // BLOCCO_SEMI, semi_pezzo, nuovi)
            simulazioni.update(json_sicuro(nuovi))
            n_calcolate += len(semi_pezzo)
            pezzi_fatti += 1
        # la gemella si controlla appena ci sono i semi della (b): se differisce, STOP subito
        if gemella is None and all(str(s) in simulazioni for s in semi_b) and base_b is not None:
            gemella = controlla_gemella(simulazioni, semi_b, stato_b)
            if not gemella["uguale"]:
                raise Stop(f"la gemella delle entrate casuali non da' gli R medi di simula_baseline_casuale: {gemella}")
    tempi["simulazioni_caso_s"] = time.perf_counter() - t_sim
    tempi["simulazioni_calcolate_ora"] = n_calcolate
    if n_calcolate:
        tempi["secondi_per_simulazione"] = tempi["simulazioni_caso_s"] / n_calcolate * max(1, processi)
    if gemella is None and base_b is not None:
        gemella = controlla_gemella(simulazioni, semi_b, stato_b)
    if gemella is None:
        gemella = {"verificabile": False, "uguale": None,
                   "motivo": f"la (b) a {regole['simulazioni_b']} semi non si e' potuta calcolare: {stato_b.get('errore')}"}
    out["gemella"] = gemella

    # 7. criterio del vault, 90° percentile, tasso del caso
    sims = [dict(simulazioni[str(s)]) for s in SEMI_CASO]
    for s in sims:
        if s["prima_entrata_ts"] is not None and s["prima_entrata_ts"] < inizio_ts:
            raise Stop(f"seme {s['seme']}: un trade casuale entra prima del periodo")
    r_medi = [float(s["r_medio"]) for s in sims if s["r_medio"] is not None]
    out["btc_stessa_finestra"] = _btc_sicuro(trades, d)
    if not r_medi:
        out["criterio_vault"] = None
        out["caso"] = None
        out["tasso_del_caso"] = None
        out["nota_caso"] = "tutte le 1000 entrate casuali sono senza trade: il 90° percentile non esiste"
        out["esito"] = "non si sa" if sotto_minimo else "non valutabile"
        out["esito_motivo"] = motivo_minimo if sotto_minimo else out["nota_caso"]
        out["tempi_s"] = tempi
        out["finito"] = adesso()
        return out
    p90 = statistica.percentile(r_medi, regole["percentile_caso"])
    metr_cand = {"profit_factor": m["profit_factor"], "n_trade": m["trade"],
                 "rendimento_totale": m["rendimento_totale"], "r_medio": m["r_medio"]}
    crit = statistica.criterio_vault(metr_cand, p90, regole["trade_minimi"], regole["pf_minimo"])
    esiti = []
    passano = []
    for s in sims:
        ms = {"profit_factor": float(s["profit_factor"]), "n_trade": int(s["n_trade"]),
              "rendimento_totale": float(s["rendimento_totale"]),
              "r_medio": float(s["r_medio"]) if s["r_medio"] is not None else -math.inf}
        cs = statistica.criterio_vault(ms, p90, regole["trade_minimi"], regole["pf_minimo"])
        s["criterio"] = cs["condizioni"]
        s["passa"] = cs["esito"]
        esiti.append(cs["esito"])
        if cs["esito"]:
            passano.append(s["seme"])
    tasso = statistica.tasso_del_caso(esiti)
    cond_caso = {c: sum(1 for s in sims if s["criterio"][c]) for c in ("profit_factor", "trade_minimi",
                                                                      "rendimento_positivo", "sopra_il_caso")}
    out["caso"] = {
        "semi": [SEMI_CASO[0], SEMI_CASO[-1]], "n_simulazioni": len(sims),
        "simulazioni_vuote": sum(1 for s in sims if s["r_medio"] is None),
        "percentile": regole["percentile_caso"], "r_medio_percentile_90": p90,
        "r_medio_media": float(np.mean(r_medi)),
        "r_medio_dev_std": float(np.std(r_medi, ddof=1)) if len(r_medi) > 1 else None,
        "trade_medi": float(np.mean([s["n_trade"] for s in sims])),
        "trade_min": int(min(s["n_trade"] for s in sims)), "trade_max": int(max(s["n_trade"] for s in sims)),
        "segnali_scartati_medi": float(np.mean([s["segnali_non_validi"] for s in sims])),
        "percentile_del_candidato_fra_le_1000": statistica.percentile_del_candidato(m["r_medio"], r_medi),
        "condizioni_superate": cond_caso,
        "tutte_le_condizioni": len(passano),
        "semi_che_passano": passano,
        "per_seme": [{k: s[k] for k in ("seme", "n_trade", "r_medio", "profit_factor", "rendimento_totale",
                                        "drawdown_max", "segnali_non_validi", "passa")} for s in sims],
    }
    out["criterio_vault"] = crit
    out["tasso_del_caso"] = tasso
    if sotto_minimo:
        out["esito"] = "non si sa"
        out["esito_motivo"] = motivo_minimo
    else:
        out["esito"] = "passa" if crit["esito"] else "non passa"
        out["esito_motivo"] = ("tutte e quattro le condizioni del criterio_vault" if crit["esito"] else
                               "cadute: " + ", ".join(c for c, ok in crit["condizioni"].items() if not ok))
    tempi["totale_s"] = time.perf_counter() - t_tot
    out["tempi_s"] = tempi
    out["finito"] = adesso()
    return out


def _btc_sicuro(trades, d) -> Dict[str, object]:
    """Riferimento di mercato (come comune.valuta: un errore non ferma il giudizio)."""
    if d.get("btc") is None:
        return {"errore": d.get("btc_errore", "BTC non caricato")}
    try:
        return _confronto_btc(trades, d["btc"])
    except Exception as e:  # noqa: BLE001
        return {"errore": str(e)}


def controlla_gemella(simulazioni: Dict[str, Dict[str, object]], semi_b: Sequence[int],
                      b: Dict[str, object]) -> Dict[str, object]:
    """Seme per seme: gli R medi della gemella sui semi della (b) sono quelli di simula_baseline_casuale?"""
    sims = [simulazioni[str(s)] for s in semi_b]
    nostri = [float(s["r_medio"]) for s in sims if s["r_medio"] is not None]  # simula esclude le vuote
    loro = [float(x) for x in b["valori"]]
    trade_nostri = [int(s["n_trade"]) for s in sims if s["r_medio"] is not None]
    nv_nostri = [int(s["segnali_non_validi"]) for s in sims]
    stessi_n = len(nostri) == len(loro)
    diff = max((abs(a - c) for a, c in zip(nostri, loro)), default=0.0) if stessi_n else math.inf
    uguali_esatti = stessi_n and all(a == c for a, c in zip(nostri, loro))
    return {
        "verificabile": True,
        "semi": [semi_b[0], semi_b[-1]], "n": len(semi_b),
        "r_medi_uguali_esattamente": bool(uguali_esatti),
        "differenza_massima": diff,
        "trade_per_simulazione_uguali": trade_nostri == [int(x) for x in b["trade_per_simulazione"]],
        "segnali_non_validi_uguali": nv_nostri == [int(x) for x in b["segnali_non_validi_per_simulazione"]],
        "vuote_uguali": (len(semi_b) - len(nostri)) == int(b["simulazioni_vuote"]),
        "uguale": bool(uguali_esatti and trade_nostri == [int(x) for x in b["trade_per_simulazione"]]),
    }


# ---------------------------------------------------------------------------
# Riassunto leggibile (scritto dopo il JSON)
# ---------------------------------------------------------------------------


def _f(x, d=3, segno=True):
    if x is None:
        return "—"
    if isinstance(x, str):
        return x
    if isinstance(x, float) and math.isinf(x):
        return "infinito"
    s = f"{x:+.{d}f}" if segno else f"{x:.{d}f}"
    return s.replace(".", ",")


def _pct(x, d=1, segno=True):
    return _f(100 * x, d, segno) + "%" if x is not None else "—"


ESITI_TESTO = {
    "passa": "PASSA il criterio del vault",
    "non passa": "NON PASSA il criterio del vault",
    "non si sa": "NON SI SA (sezione 8)",
    "non valutabile": "NON VALUTABILE",
    "STOP": "STOP: nessun giudizio",
    "errore": "ERRORE del lanciatore: nessun giudizio",
}


def _righe_dati(o: Dict[str, object]) -> List[str]:
    info = o.get("info", {})
    comp = info.get("completezza")
    righe: List[str] = []
    if not comp:
        return righe
    righe.append("## Dati del periodo")
    righe.append("")
    nt = comp["note"]
    righe.append(f"Ultima barra della serie allineata: {nt['ultima_barra']} (attesa {nt['ultima_barra_attesa']}); "
                 f"barre dell'ultimo giorno {nt['barre_ultimo_giorno']} su {nt['barre_attese_ultimo_giorno']}; "
                 f"prima barra del periodo {nt['prima_barra_del_periodo']}. Buchi nel periodo: {nt['buchi_nel_periodo']} "
                 f"({nt['barre_mancanti_nel_periodo']} barre mancanti, il piu' lungo {nt['buco_piu_lungo_barre']}). "
                 f"Settlement di funding nel periodo: {nt['funding_nel_periodo']}.")
    righe.append("")
    if nt.get("intervalli_funding_dichiarati"):
        righe.append("Intervalli di funding dichiarati nei file (da quando, ore): " + "; ".join(
            f"{a} {_f(float(b), 0, False)} h" for a, b in nt["intervalli_funding_dichiarati"]) + ".")
        righe.append("")
    if comp["fermano"]:
        righe.append("Condizioni che fermano il giro (D2; nel vault fermano prima di eseguire il candidato, "
                     "senza risultato): " + "; ".join(comp["fermano"]) + ".")
        righe.append("")
    if comp["avvisi"]:
        righe.append(f"Avvisi dei dati (D3, solo riportati; mesi sotto il 99%: {nt.get('mesi_sotto_il_99', '—')}):")
        righe.append("")
        righe += [f"- {a}" for a in comp["avvisi"]]
        righe.append("")
    ins = comp.get("in_sample")
    if ins:
        righe.append(f"Parte prima del 2024 della serie lunga: {ins['rifatto']} contro la Fase 0 {ins['fase0_dati.md']} "
                     f"({'uguale' if ins['uguale'] else 'DIVERSA: avviso'}).")
        righe.append("")
    fv = info.get("file_vault")
    if fv:
        conteggi = ", ".join("%s %s/%s" % (k, x["file_leggibili"], x["mesi_attesi"]) for k, x in fv["serie"].items())
        righe.append(f"File mensili del vault leggibili: {conteggi}; mancanti: {fv['mancanti'] or 'nessuno'}; "
                     f"illeggibili: {fv['illeggibili'] or 'nessuno'}. "
                     f"CHECKSUM non pubblicati: {len(info.get('checksum_mancanti_vault', []))}.")
        righe.append("")
    righe.append("| Mese | Barre attese | Last | Mark | Allineate | Quota | Tolte: manca il mark | Tolte: manca il last "
                 "| Settlement di funding | Ore dichiarate | Distanze osservate (ore) | BTC |")
    righe.append("|---|---|---|---|---|---|---|---|---|---|---|---|")
    for k, r in comp["per_mese"].items():
        quota = (_pct(r["quota"], 1, False) + (" AVVISO" if r.get("avviso_sotto_99") else "")) if r["quota"] is not None else "—"
        ore = ", ".join(f"{h}: {n}" for h, n in r["ore_dichiarate"].items()) or "—"
        dist = ", ".join(f"{h}: {n}" for h, n in r["distanze_ore_osservate"].items()) or "—"
        righe.append(f"| {k} | {r['attese']} | {r['last']} | {r['mark']} | {r['allineate']} | {quota} | "
                     f"{r['tolte_manca_il_mark']} | {r['tolte_manca_il_last']} | {r['settlement']} | {ore} | {dist} | "
                     f"{r.get('btc', '—')} |")
    righe.append("")
    return righe


def riassunto_md(o: Dict[str, object]) -> str:
    prova = o["etichetta"] != "vault"
    per = o.get("periodo", {})
    esito = o.get("esito")
    righe = []
    titolo = (f"# {CANDIDATO} — PROVA del motore del vault sul periodo di validazione (non e' il vault)"
              if prova else f"# {CANDIDATO} nel vault ({str(per.get('trade_entrati_da', ''))[:10]} → "
                            f"{per.get('ultima_barra') or per.get('fine_chiesta')})")
    righe.append(titolo)
    righe.append("")
    righe.append(f"**Esito: {ESITI_TESTO.get(esito, esito)}.** {o.get('esito_motivo') or o.get('motivo') or ''}".rstrip())
    righe.append("")
    m = o.get("metriche")
    if esito in ("STOP", "errore") or m is None:
        righe += _righe_dati(o)
        righe += _righe_calcolo(o)
        return "\n".join(righe) + "\n"
    crit = o.get("criterio_vault")
    caso = o.get("caso")
    if crit and caso:
        righe.append(f"Tasso del caso: **{_pct(o['tasso_del_caso'], 1, False)}** ({caso['tutte_le_condizioni']} "
                     f"strategie a entrate casuali su {caso['n_simulazioni']} passano lo stesso criterio).")
        righe.append("")
        c = crit["condizioni"]
        val = crit["valori"]
        righe.append("| Condizione | Valore | Soglia | Esito |")
        righe.append("|---|---|---|---|")
        righe.append(f"| Profit factor dopo i costi | {_f(val['profit_factor'], 2, False)} | almeno {_f(val['pf_minimo'], 2, False)} | {'sì' if c['profit_factor'] else 'no'} |")
        righe.append(f"| Trade | {val['n_trade']} | almeno {val['trade_minimi']} | {'sì' if c['trade_minimi'] else 'no'} |")
        righe.append(f"| Rendimento totale | {_pct(val['rendimento_totale'])} | sopra 0 | {'sì' if c['rendimento_positivo'] else 'no'} |")
        righe.append(f"| R medio dopo i costi | {_f(val['r_medio'], 4)} | sopra {_f(val['r_caso_percentile_90'], 4)} (90° percentile delle 1000 entrate casuali) | {'sì' if c['sopra_il_caso'] else 'no'} |")
        righe.append("")
    else:
        righe.append(f"Criterio del vault non calcolato: {o.get('nota_caso')}")
        righe.append("")
    righe.append("## Metriche sui trade entrati nel periodo")
    righe.append("")
    righe.append("| | Valore |")
    righe.append("|---|---|")
    righe.append(f"| Trade | {m['trade']} ({', '.join(f'{a}: {n}' for a, n in m['trade_per_anno'].items())}) |")
    righe.append(f"| R medio a trade, dopo i costi | {_f(m['r_medio'])} |")
    righe.append(f"| R mediano | {_f(m['r_mediano'])} |")
    righe.append(f"| R medio per anno (anno d'uscita) | {'; '.join(f'{a} {_f(x)}' for a, x in m['r_medio_per_anno'].items())} |")
    righe.append(f"| R medio senza i 3 trade migliori | {_f(m['r_medio_senza_3_migliori'])} |")
    righe.append(f"| Profit factor | {_f(m['profit_factor'], 2, False)} |")
    righe.append(f"| Quota di trade vincenti | {_pct(m['win_rate'], 0, False)} |")
    righe.append(f"| Uscite | {', '.join(f'{n} {k}' for k, n in m['esiti'].items()) or '—'} |")
    righe.append(f"| Rendimento totale (somma dei pnl su 1000, come in validazione) | {_pct(m['rendimento_totale'])} |")
    righe.append(f"| Drawdown massimo | {_pct(m['drawdown_max'])} |")
    righe.append(f"| Costi medi in R / funding medio in R | {_f(m['costi_medi_r'])} / {_f(m['funding_medio_r'], 4)} |")
    a = o.get("baseline_a", {})
    b = o.get("baseline_b", {})
    if a:
        righe.append(f"| Baseline (a) | media {_f(a.get('media'))}; t {_f(a.get('t'), 2, False)}, soglia {_f(a.get('soglia'), 2, False)}, {'netta' if a.get('netta') else 'non netta'} |")
    if b:
        righe.append(f"| Baseline (b), {b.get('n_simulazioni', '—')} simulazioni (semi 0-199) | media {_f(b.get('media'))}; t {_f(b.get('t'), 2, False)}, soglia {_f(b.get('soglia'), 2, False)}, {'netta' if b.get('netta') else 'non netta'}; p-value {_f(b.get('p_value'), 4, False)} |")
    if "percentile_caso" in o:
        righe.append(f"| Percentile fra le 200 simulazioni della (b) (indizio) | {_f(o['percentile_caso'], 1, False)} |")
    if caso:
        righe.append(f"| Percentile fra le 1000 simulazioni del caso (indizio) | {_f(caso['percentile_del_candidato_fra_le_1000'], 1, False)} |")
    bh = o.get("buy_and_hold_per_anno", {})
    bh_testo = "; ".join(f"{y} {_pct(x['long'], 0)}" for y, x in bh.items())
    righe.append(f"| Buy and hold per anno (contesto) | {bh_testo} |")
    btc = o.get("btc_stessa_finestra", {}) or {}
    corr = (_f(btc.get("corr_r_btc"), 2, False) if "corr_r_btc" in btc else
            f"non calcolata ({btc.get('errore') or str(btc.get('n', 0)) + ' trade con BTC, ne servono 3'})")
    righe.append(f"| Correlazione fra R dei trade e BTC nella stessa finestra | {corr} |")
    righe.append(f"| Trade ridotti per il tetto di leva / violazioni del margine | {m['trade_ridotti']} / {m['violazioni_liquidazione']} |")
    righe.append(f"| Buchi nei dati (contati dal motore su tutta la serie) | {m['buchi_dati']} |")
    righe.append("")
    if caso:
        k = caso
        righe.append("## Le entrate casuali (tasso del caso)")
        righe.append("")
        righe.append(f"{k['n_simulazioni']} strategie, semi {k['semi'][0]}-{k['semi'][1]}: stessa moneta, direzione long, "
                     f"{m['trade']} ingressi a distanza di almeno {o['durata_media_barre']} barre (durata media dei trade del "
                     f"periodo), stessa uscita, stop e costi del candidato; ingressi vietati prima della prima barra del "
                     f"periodo, dove il segnale non e' valido ({o['barre_vietate']['segnale_non_valido']} barre), nei mesi "
                     f"esclusi della Fase 0 e all'ultima barra. Trade per simulazione: media {_f(k['trade_medi'], 1, False)} "
                     f"(da {k['trade_min']} a {k['trade_max']}). R medio delle simulazioni: media {_f(k['r_medio_media'], 4)}, "
                     f"90° percentile {_f(k['r_medio_percentile_90'], 4)}. Quante delle {k['n_simulazioni']} passano ogni "
                     f"condizione: profit factor {k['condizioni_superate']['profit_factor']}, trade "
                     f"{k['condizioni_superate']['trade_minimi']}, rendimento {k['condizioni_superate']['rendimento_positivo']}, "
                     f"sopra il percentile {k['condizioni_superate']['sopra_il_caso']}; tutte insieme {k['tutte_le_condizioni']}.")
        righe.append("")
        g = o.get("gemella") or {}
        if g.get("verificabile"):
            righe.append(f"Prova della gemella: sui semi {g.get('semi')} gli R medi sono "
                         f"{'identici' if g.get('r_medi_uguali_esattamente') else 'DIVERSI'} a quelli di "
                         f"`motore.simula_baseline_casuale` (differenza massima {g.get('differenza_massima')}).")
        else:
            righe.append(f"Prova della gemella non fatta: {g.get('motivo')}")
        righe.append("")
    nt = o.get("note_ultimo_giorno_e_buchi")
    if nt:
        righe.append(f"Ultimo giorno: {nt['trade_chiusi_a_fine_dati']} trade chiusi a fine dati; ultimo trade uscito "
                     f"{nt['ultimo_trade_uscita']} ({nt['ultimo_trade_esito']}).")
        righe.append("")
    righe += _righe_dati(o)
    righe += _righe_calcolo(o)
    return "\n".join(righe) + "\n"


def _righe_calcolo(o: Dict[str, object]) -> List[str]:
    per = o.get("periodo", {})
    ver = o.get("versioni", {})
    righe = ["## Come e' stato calcolato", ""]
    righe.append(f"Serie {SIMBOLO} {TF} last e mark da `dati.carica_serie_allineate` dal {per.get('serie_da')} "
                 f"all'ultima barra {per.get('ultima_barra', '—')} (fine chiesta {per.get('fine_chiesta')}; "
                 f"{per.get('barre_serie', '—')} barre, indicatori caldi), funding dai settlement del file; "
                 f"contano i trade entrati dal {per.get('trade_entrati_da')}. Codice del candidato al commit {COMMIT[:8]} "
                 f"(SHA-256 controllati prima dell'import). Criterio da `{o['regole_esame']['fonte']}`. "
                 f"Il rendimento totale e' la somma dei pnl divisa per 1000, con la dimensione sul capitale "
                 f"cresciuto dall'inizio della serie (come in validazione); nelle entrate casuali il capitale "
                 f"all'inizio del periodo e' 1000.")
    righe.append("")
    righe.append(f"Lanciatore sha256 {o.get('sha256_lanciatore')}; impronta del giro {o.get('impronta_giro')}; "
                 f"semi del caso {o.get('semi', {}).get('caso')}, della (b) {o.get('semi', {}).get('b')}; "
                 f"python {ver.get('python')}, numpy {ver.get('numpy')}, scipy {ver.get('scipy')}.")
    righe.append("")
    return righe


# ---------------------------------------------------------------------------
# Modo parita
# ---------------------------------------------------------------------------

# numeri scritti in consegna.md (tabella «Metriche, separate per periodo» e testo)
CONSEGNA_VALIDAZIONE = [
    ("trade", 32, 0), ("trade 2022", 4, 0), ("trade 2023", 28, 0),
    ("R medio dopo i costi", 0.047, 3), ("R mediano", 0.111, 3),
    ("R medio 2022", -0.038, 3), ("R medio 2023", 0.059, 3),
    ("R senza i 3 migliori", 0.008, 3), ("profit factor", 1.49, 2), ("vincenti %", 75, 0),
    ("uscite sul segnale", 29, 0), ("uscite stop", 2, 0), ("uscite fine dati", 1, 0),
    ("rendimento totale %", 1.7, 1), ("drawdown %", -2.3, 1), ("costi medi R", 0.079, 3),
    ("(a) media", -0.094, 3), ("(a) t", 1.94, 2), ("(a) soglia", 2.32, 2), ("(a) netta", False, None),
    ("(b) media", -0.092, 3), ("(b) t", 2.14, 2), ("(b) soglia", 2.32, 2), ("(b) netta", False, None),
    ("percentile fra le simulazioni", 98.5, 1), ("p-value contro la (b)", 0.031, 3),
    ("buy and hold 2022 %", -17, 0), ("buy and hold 2023 %", 26, 0),
    ("correlazione R-BTC", 0.54, 2), ("trade ridotti", 0, 0), ("violazioni margine", 0, 0),
    ("asticella superata (m = 1)", True, None),
]
CONSEGNA_COSTRUZIONE = [
    ("trade", 74, 0), ("trade 2020", 21, 0), ("trade 2021", 34, 0), ("trade 2022", 19, 0),
    ("R medio dopo i costi", 0.138, 3), ("R mediano", 0.200, 3),
    ("R medio 2020", 0.171, 3), ("R medio 2021", 0.184, 3), ("R medio 2022", 0.020, 3),
    ("R senza i 3 migliori", 0.120, 3), ("profit factor", 2.76, 2), ("vincenti %", 76, 0),
    ("uscite sul segnale", 71, 0), ("uscite stop", 3, 0),
    ("rendimento totale %", 10.8, 1), ("drawdown %", -1.6, 1), ("costi medi R", 0.047, 3),
    ("(a) media", -0.047, 3), ("(a) t", 4.12, 2), ("(a) netta", True, None),
    ("(b) media", -0.048, 3), ("(b) t", 3.96, 2), ("(b) netta", True, None),
    ("percentile fra le simulazioni", 100, 0), ("p-value contro la (b)", 0.0003, 4),
    ("buy and hold 2020 %", 49, 0), ("buy and hold 2021 %", 1267, 0), ("buy and hold 2022 %", -42, 0),
    ("correlazione R-BTC", 0.31, 2), ("trade ridotti", 0, 0), ("violazioni margine", 0, 0),
]


def _valori_consegna(voce: Dict[str, object], validazione: bool) -> Dict[str, object]:
    m = voce["metriche"]
    a, b = voce["baseline_a"], voce["baseline_b"]
    out = {"trade": m["trade"], "R medio dopo i costi": m["r_medio"], "R mediano": m["r_mediano"],
           "R senza i 3 migliori": m["r_medio_senza_3_migliori"], "profit factor": m["profit_factor"],
           "vincenti %": 100 * m["win_rate"], "uscite sul segnale": m["esiti"].get("segnale", 0),
           "uscite stop": m["esiti"].get("stop", 0), "uscite fine dati": m["esiti"].get("fine_dati", 0),
           "rendimento totale %": 100 * m["rendimento_totale"], "drawdown %": 100 * m["drawdown_max"],
           "costi medi R": m["costi_medi_r"], "(a) media": a["media"], "(a) t": a["t"], "(a) soglia": a["soglia"],
           "(a) netta": a["netta"], "(b) media": b["media"], "(b) t": b["t"], "(b) soglia": b["soglia"],
           "(b) netta": b["netta"], "percentile fra le simulazioni": voce["percentile_caso"],
           "p-value contro la (b)": b["p_value"], "correlazione R-BTC": voce["btc_stessa_finestra"]["corr_r_btc"],
           "trade ridotti": m["trade_ridotti"], "violazioni margine": m["violazioni_liquidazione"]}
    for anno, n in m["trade_per_anno"].items():
        out[f"trade {anno}"] = n
    for anno, x in m["r_medio_per_anno"].items():
        out[f"R medio {anno}"] = x
    for anno, x in voce["buy_and_hold_per_anno"].items():
        out[f"buy and hold {anno} %"] = 100 * x["long"]
    if validazione:
        out["asticella superata (m = 1)"] = voce["passa_asticella_provvisorio"]
    return out


def confronta_consegna(voce: Dict[str, object], attesi, validazione: bool) -> List[Dict[str, object]]:
    valori = _valori_consegna(voce, validazione)
    righe = []
    for nome, scritto, dec in attesi:
        rifatto = valori.get(nome)
        if dec is None:
            ok = rifatto == scritto
            mostrato = rifatto
        else:
            mostrato = round(float(rifatto), dec) if rifatto is not None else None
            ok = mostrato is not None and abs(mostrato - scritto) < 0.5 * 10 ** (-dec) + 1e-12
        righe.append({"voce": nome, "consegna": scritto, "rifatto": rifatto, "rifatto_arrotondato": mostrato,
                      "uguale": bool(ok)})
    return righe


def voce_log(worktree: Path, vid: str, tipo: str) -> Dict[str, object]:
    for riga in (worktree / CAMPAGNA_REL / "log.jsonl").read_text(encoding="utf-8").splitlines():
        if riga.strip():
            v = json.loads(riga)
            if v["id"] == vid and v["tipo"] == tipo:
                return v
    raise Stop(f"voce {vid} {tipo} non trovata nel log")


def rifai_validazione() -> Tuple[Dict[str, object], float]:
    """Come codice/validazione.py, senza registro.aggiungi (la voce e' gia' nel log)."""
    vid = f"{CANDIDATO}-validazione"
    v = V.i03("1h", vid, max_barre=12, solo_fine_settimana=True)
    t0 = time.perf_counter()
    res = C.valuta(v, periodo="validazione")
    secondi = time.perf_counter() - t0
    m = res["metriche"]
    b = res.get("baseline_b", {})
    p = float(b.get("p_value", 1.0)) if m["trade"] >= 30 and b.get("valutabile") else 1.0
    passa = statistica.benjamini_hochberg([p], 0.10)[0] and m["trade"] >= 30
    voce = {"id": vid, "tipo": "risultato", "metriche": m, "blocco": res.get("blocco"),
            "durata_media_barre": res.get("durata_media_barre"),
            "baseline_a": res.get("baseline_a"), "baseline_b": b, "percentile_caso": res.get("percentile_caso"),
            "buy_and_hold_per_anno": res.get("buy_and_hold_per_anno"),
            "btc_stessa_finestra": res.get("btc_stessa_finestra"),
            "trade_minimi_validazione": m["trade"] >= 30, "p_value_asticella": p, "m_asticella": 1,
            "passa_asticella_provvisorio": bool(passa),
            "previsione_corretta": bool(-0.10 <= m["r_medio"] <= 0.10 and not passa),
            "commento": f"validazione: {m['trade']} trade, R medio {m['r_medio']:+.3f}, p-value {p:.4f}, "
                        f"asticella {'superata' if passa else 'non superata'} (provvisorio)"}
    return registro._pulisci(voce), secondi


def rifai_costruzione() -> Tuple[Dict[str, object], Dict[str, int], float]:
    """Come codice/lancia.py per l'etichetta I-03-1h-T12-W (BNBUSDT-045), senza scrivere nel log."""
    vid = CANDIDATO
    v = V.i03("1h", vid, max_barre=12, solo_fine_settimana=True)
    conteggio = C.conta(v)
    t0 = time.perf_counter()
    res = C.valuta(v)
    secondi = time.perf_counter() - t0
    m = res["metriche"]
    rmin, rmax, batte_b = -0.05, 0.15, False  # previsione registrata: «fra -0.05 e +0.15; non batte nettamente la (b)»
    netta_b = bool(res.get("baseline_b", {}).get("netta"))
    corretta = bool(rmin <= m["r_medio"] <= rmax and netta_b == batte_b)
    commento = (f"{'candidato' if res.get('candidato') else 'non candidato'}; "
                f"{'valutabile' if res.get('valutabile') else 'NON valutabile'}; "
                f"(a) netta {res.get('baseline_a', {}).get('netta')}, (b) netta {netta_b}, R medio {m['r_medio']:+.3f}")
    voce = {"id": vid, "tipo": "risultato", "etichetta": "I-03-1h-T12-W",
            "metriche": m, "blocco": res.get("blocco"), "durata_media_barre": res.get("durata_media_barre"),
            "baseline_a": res.get("baseline_a"), "baseline_b": res.get("baseline_b"),
            "percentile_caso": res.get("percentile_caso"),
            "buy_and_hold_per_anno": res.get("buy_and_hold_per_anno"),
            "btc_stessa_finestra": res.get("btc_stessa_finestra"),
            "valutabile": res.get("valutabile"), "candidato": res.get("candidato"),
            "previsione_corretta": corretta, "commento": commento}
    return registro._pulisci(voce), registro._pulisci(conteggio), secondi


def senza_data(v: Dict[str, object]) -> Dict[str, object]:
    return {k: x for k, x in v.items() if k != "data"}


def modo_parita(worktree: Path, uscita: Path, cartella_prova: Optional[Path], processi: int,
                salta_prova: bool) -> int:
    esito: Dict[str, object] = {"candidato": CANDIDATO, "modo": "parita", "iniziato": adesso(),
                                "lanciatore": str(Path(__file__).resolve()), "sha256_lanciatore": SHA256_LANCIATORE,
                                "versioni": versioni()}
    problemi: List[str] = []
    try:
        if cartella_prova is not None and not salta_prova:
            cartella_prova = prepara_cartella_prova(cartella_prova)  # prima di tutto: niente lavoro buttato
        esito["codice"] = controlla_codice(worktree)
        importa_candidato(worktree)
        regole = leggi_regole_esame(worktree)
        esito["regole_esame"] = regole
        esito["per_apertura"] = {"sha256": dict(IMPRONTE_CODICE), "semi": "0-999",
                                 "testo_suggerito": testo_per_apertura(IMPRONTE_CODICE)}
        radice = dati.RADICE_DEFAULT
        esito["radice_dati"] = str(radice)
        if Path(radice).resolve() != (worktree / "research").resolve():
            raise Stop(f"radice dei dati inattesa: {radice}")

        # 1-2. scarico e impronte
        esito["scarico"] = scarica_insample(radice)
        if esito["scarico"]["checksum_mancanti"]:
            problemi.append(f"CHECKSUM mancanti: {esito['scarico']['checksum_mancanti']}")
        esito["impronte"] = verifica_impronte_insample(worktree, radice)
        scrivi_json(uscita, esito)

        # conteggi della Fase 0 a 1h (fase0_dati.md: 34.096 last, 33.904 tenute, 192 e 224 tolte)
        d = C.carica("1h", "intero")
        s = dati.carica_serie_allineate(SIMBOLO, "1h", C.INIZIO, C.FINE_IN_SAMPLE)
        fase0 = {"barre_last": len(s["candele"]) + s["n_tolte_last"], "barre_tenute": len(d["candele"]),
                 "tolte_last": d["n_tolte_last"], "tolte_mark": d["n_tolte_mark"]}
        fase0_attesi = {"barre_last": 34096, "barre_tenute": 33904, "tolte_last": 192, "tolte_mark": 224}
        esito["fase0_1h"] = {"rifatto": fase0, "fase0_dati.md": fase0_attesi, "uguale": fase0 == fase0_attesi}
        if fase0 != fase0_attesi:
            problemi.append(f"conteggi della Fase 0 diversi: {fase0} contro {fase0_attesi}")

        # 3. validazione e costruzione, campo per campo col log
        val, t_val = rifai_validazione()
        log_val = senza_data(voce_log(worktree, f"{CANDIDATO}-validazione", "risultato"))
        diff_val = confronta(val, log_val)
        esito["validazione"] = {"uguale_al_log": not diff_val, "differenze": diff_val, "secondi_valuta": t_val,
                                "rifatto": val,
                                "consegna": confronta_consegna(val, CONSEGNA_VALIDAZIONE, True)}
        cos, conteggio, t_cos = rifai_costruzione()
        log_cos = senza_data(voce_log(worktree, CANDIDATO, "risultato"))
        log_reg = voce_log(worktree, CANDIDATO, "registrazione")
        diff_cos = confronta(cos, log_cos) + confronta(conteggio, log_reg["conteggio"], ".conteggio")
        esito["costruzione"] = {"uguale_al_log": not diff_cos, "differenze": diff_cos, "secondi_valuta": t_cos,
                                "conteggio": conteggio, "rifatto": cos,
                                "consegna": confronta_consegna(cos, CONSEGNA_COSTRUZIONE, False)}
        for nome in ("validazione", "costruzione"):
            if not esito[nome]["uguale_al_log"]:
                problemi.append(f"{nome}: differenze col log: {esito[nome]['differenze']}")
            male = [r for r in esito[nome]["consegna"] if not r["uguale"]]
            if male:
                problemi.append(f"{nome}: numeri diversi dalla consegna: {male}")
        scrivi_json(uscita, esito)

        # 4. prova del motore del vault sul periodo di validazione
        if not salta_prova:
            esito["prova_motore_vault"] = prova_motore_vault(worktree, regole, val, cartella_prova, processi)
            for k, ok in esito["prova_motore_vault"]["controlli"].items():
                if not ok:
                    problemi.append(f"prova del motore del vault: controllo «{k}» fallito")

        # 5. tempi e stima del modo vault
        esito["stima_vault"] = stima_tempo_vault(esito, d)
    except Stop as e:
        problemi.append(f"STOP: {e}")
        esito["stop"] = str(e)
    esito["problemi"] = problemi
    esito["parita_esatta"] = not problemi
    esito["finito"] = adesso()
    scrivi_json(uscita, esito)
    print(json.dumps({"parita_esatta": esito["parita_esatta"], "problemi": problemi,
                      "stima_vault": esito.get("stima_vault", {}).get("testo")}, ensure_ascii=False, indent=1))
    return 0 if not problemi else 2


def prepara_cartella_prova(cartella: Path) -> Path:
    """La cartella della prova: nuova o vuota. Il lanciatore la svuota da se' SOLO se sta dentro
    lo scratchpad; mai dentro il coordinamento (vault e avanzamento compresi) o il worktree."""
    c = Path(cartella).resolve()
    for vietata in (Path("/home/user/coordinamento"), WORKTREE_DEFAULT, VAULT_COORD, AVANZAMENTO_VAULT):
        if dentro(c, vietata) or dentro(vietata, c):
            raise Stop(f"--cartella-prova {c}: non puo' stare in {vietata} ne' contenerla")
    if c.exists():
        if not c.is_dir():
            raise Stop(f"--cartella-prova {c} esiste e non e' una cartella")
        if any(c.iterdir()):
            if c != SCRATCHPAD.resolve() and dentro(c, SCRATCHPAD):
                shutil.rmtree(c)  # solo dentro lo scratchpad della sessione: e' una prova
            else:
                raise Stop(f"--cartella-prova {c} non e' vuota e non sta nello scratchpad: il lanciatore non la "
                           f"svuota; passane una nuova")
    c.mkdir(parents=True, exist_ok=True)
    return c


def _radice_guasta(base: Path, radice: Path, impronte: Dict[str, str], guasto: str) -> Tuple[Path, str]:
    """Per la prova della regola D1: una radice nella cartella della prova con collegamenti simbolici
    ai file in-sample del periodo, tranne il mark 1h di 2023-06, che manca (``guasto="manca"``) o e'
    una copia troncata a meta' (``guasto="rotto"``). I dati veri non si toccano."""
    r = Path(base) / f"radice_{guasto}"
    bersaglio = dati.percorso_mese(SIMBOLO, "markPriceKlines", TF, 2023, 6, radice)
    for rel in impronte:
        src, dst = Path(radice) / rel, r / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        if src == bersaglio:
            if guasto == "rotto":
                dst.write_bytes(src.read_bytes()[: src.stat().st_size // 2])
            continue
        os.symlink(src, dst)
    return r, bersaglio.name


def prova_motore_vault(worktree: Path, regole: Dict[str, object], val_log: Dict[str, object],
                       cartella: Optional[Path], processi: int) -> Dict[str, object]:
    """Il motore del modo vault sul periodo di validazione, con gli stessi passi del vault: deve rifare
    la voce del log e reggere la regola dei dati (D1-D5), marcatore, ripresa, pezzi manomessi, guardia."""
    d = C.carica("1h", "intero")
    if cartella is None:
        cartella = Path(tempfile.mkdtemp(prefix="vault_prova_BNBUSDT_"))
    cartella = Path(cartella)
    radice = Path(dati.RADICE_DEFAULT)
    inizio_val = C.PERIODI["inizio_validazione"]
    fine = C.FINE_IN_SAMPLE
    controlli: Dict[str, bool] = {}
    H = dati.MS_ORA

    # D1 sul periodo di validazione: file mensili presenti e leggibili (nessuna candela letta)
    file_val = file_mensili(radice, inizio_val, fine)
    controlli["file_mensili_della_validazione_presenti_e_leggibili"] = not file_val["mancanti"] and not file_val["illeggibili"]
    file_tutti = file_mensili(radice, C.INIZIO, fine)
    s_all = dati.carica_serie_allineate(SIMBOLO, "1h", C.INIZIO, fine)
    btc = C.carica_btc("1h", fine)
    f_det = dati.carica_funding_dettaglio(SIMBOLO, C.INIZIO, fine)
    controlli["funding_dettaglio_uguale_al_funding_della_campagna"] = [(a, c) for a, _o, c in f_det] == list(d["funding"])

    def completezza(candele=None, funding=None) -> Dict[str, object]:
        return controlla_completezza(candele=d["candele"] if candele is None else candele, tolte_last=s_all["tolte_last"],
                                     tolte_mark=s_all["tolte_mark"], funding=f_det if funding is None else funding,
                                     btc=btc, inizio=inizio_val, fine=fine, ms_barra=d["ms_barra"])

    comp = completezza()
    # D3: il giorno intero di mark mancante di 2023-02 (648 barre su 672) e' solo un avviso, non ferma
    controlli["giorno_intero_di_mark_mancante_solo_avviso"] = (
        not comp["fermano"] and any(a.startswith("AVVISO 2023-02:") for a in comp["avvisi"])
        and comp["per_mese"]["2023-02"]["allineate"] == 648 and comp["per_mese"]["2023-02"]["attese"] == 672)
    # D2 su dati modificati in memoria (i file non si toccano)
    lo3, hi3 = dati.ms_da_data(date(2023, 3, 1)), dati.ms_da_data(date(2023, 4, 1))
    marzo = [c for c in d["candele"] if lo3 <= c.ts < hi3]
    via = {c.ts for c in marzo[: int(0.6 * len(marzo))]}
    comp_meta = completezza(candele=[c for c in d["candele"] if c.ts not in via])
    lo8, hi8 = dati.ms_da_data(date(2023, 8, 1)), dati.ms_da_data(date(2023, 9, 1))
    comp_senza_funding = completezza(funding=[r for r in f_det if not lo8 <= r[0] < hi8])
    fine_ms = dati.ms_da_data(fine) + 23 * H
    comp_ultima = completezza(candele=[c for c in d["candele"] if c.ts < fine_ms])
    controlli["d2_le_tre_condizioni_riconosciute"] = (
        any(x.startswith("2023-03:") and "sotto il 50%" in x for x in comp_meta["fermano"])
        and any(x.startswith("2023-08: nessun settlement") for x in comp_senza_funding["fermano"])
        and any("la serie allineata finisce" in x for x in comp_ultima["fermano"]))

    contenuto = contenuto_impronta("prova-validazione", dict(IMPRONTE_CODICE), file_tutti["impronte"], None, regole)
    controlli["versioni_nell_impronta"] = set(contenuto["versioni"]) >= {"python", "numpy", "scipy"}
    chiamate = {"prepara": 0, "carica": 0, "marcatore_gia_scritto": []}

    def prepara_da(r: Path, contenuto_x: Optional[Dict[str, object]] = None):
        def _prepara():
            chiamate["prepara"] += 1
            fm = file_mensili(r, inizio_val, fine)
            ferma_se_file_mancanti(fm, "file del periodo di prova")
            return {"contenuto": contenuto_x or contenuto,
                    "info": {"file_periodo": {k: fm[k] for k in ("periodo", "serie", "mancanti", "illeggibili")}}}
        return _prepara

    def carica_con(comp_x: Dict[str, object], perc_: "Percorsi"):
        def _carica():
            chiamate["carica"] += 1
            chiamate["marcatore_gia_scritto"].append(perc_.marcatore.exists())
            return {"candele": d["candele"], "mark": d["mark"], "funding": d["funding"], "btc": btc,
                    "ms_barra": d["ms_barra"], "completezza": comp_x,
                    "info": {"barre": len(d["candele"]), "settlement_funding": len(d["funding"])}}
        return _carica

    kw = dict(etichetta="prova-validazione", inizio_ts=C.INIZIO_VALIDAZIONE_TS, fine=fine, regole=regole,
              dati_obbligatori=True, processi=processi)

    def giro(perc_: Percorsi, prepara=None, comp_x=None, **altro):
        argomenti = dict(kw, **altro)
        with lucchetto(perc_.avanzamento):
            return esame_periodo(percorsi=perc_, prepara=prepara or prepara_da(radice),
                                 carica=carica_con(comp if comp_x is None else comp_x, perc_),
                                 info={"nota": "prova sul periodo di validazione, solo in-sample"}, **argomenti)

    def marcatore_di(perc_: Percorsi) -> Dict[str, object]:
        return json.loads(perc_.marcatore.read_text(encoding="utf-8"))

    def nessun_risultato_e_candidato_non_eseguito(perc_: Percorsi) -> bool:
        m = marcatore_di(perc_)
        av = perc_.avanzamento
        return (not perc_.finale.exists() and not perc_.riassunto.exists() and m.get("stato") == STATO_FERMO
                and m.get("candidato_eseguito") is False and not (av / "impronta.json").exists()
                and not list(av.glob("pezzo_*.json")))

    perc = Percorsi.prova(cartella)
    fermate: Dict[str, object] = {}

    # (a) D1: un file mensile manca, poi un file non si legge -> fermo sui dati, nessuna candela letta
    for guasto in ("manca", "rotto"):
        r_g, nome_g = _radice_guasta(cartella / "radici_di_prova", radice, file_val["impronte"], guasto)
        c0 = chiamate["carica"]
        try:
            giro(perc, prepara=prepara_da(r_g))
            ok = False
        except FermoSuiDati as e:
            m = marcatore_di(perc)
            ok = (e.regola == "D1" and nome_g.replace(".zip", "")[-7:] in str(e) and chiamate["carica"] == c0
                  and nessun_risultato_e_candidato_non_eseguito(perc) and str(m.get("motivo", "")).startswith("D1"))
            fermate[f"d1_file_{guasto}"] = {"motivo": e.motivo, "marcatore_stato": m.get("stato")}
        controlli[f"d1_file_{guasto}_fermo_senza_risultato"] = ok
    controlli["marcatore_creato_prima_dei_dati"] = perc.marcatore.exists() and chiamate["carica"] == 0
    try:
        scrivi_json_esclusivo(perc.marcatore, {"altro": "giro"})
        controlli["marcatore_esclusivo_o_excl"] = False
    except GiaEseguito:
        controlli["marcatore_esclusivo_o_excl"] = marcatore_di(perc).get("candidato") == CANDIDATO

    # (b) D2: mese sotto il 50% (con un'impronta diversa: come un file rimesso dopo), mese senza funding,
    #     ultima barra mancante -> fermo sui dati dopo il caricamento, candidato non eseguito, nessun risultato
    altro_contenuto = json.loads(json.dumps(json_sicuro(contenuto)))
    k0 = sorted(altro_contenuto["dati"])[0]
    altro_contenuto["dati"][k0] = "0" * 64
    impronta_altra = impronta_di(altro_contenuto)
    for nome, comp_x, cont_x in (("mese_sotto_il_50", comp_meta, altro_contenuto),
                                 ("mese_senza_funding", comp_senza_funding, None),
                                 ("ultima_barra_mancante", comp_ultima, None)):
        c0 = chiamate["carica"]
        try:
            giro(perc, prepara=prepara_da(radice, cont_x), comp_x=comp_x)
            ok = False
        except FermoSuiDati as e:
            m = marcatore_di(perc)
            ok = (e.regola == "D2" and chiamate["carica"] == c0 + 1 and nessun_risultato_e_candidato_non_eseguito(perc)
                  and str(m.get("motivo", "")).startswith("D2"))
            if nome == "mese_senza_funding":  # ripartenza ammessa anche con un'impronta diversa
                ok = ok and m.get("impronta_giro") == impronta_di(contenuto) and impronta_altra in m.get("impronte_precedenti", [])
            fermate[f"d2_{nome}"] = {"motivo": e.motivo, "marcatore_stato": m.get("stato")}
        controlli[f"d2_{nome}_fermo_senza_risultato"] = ok
    m = marcatore_di(perc)
    controlli["fermate_registrate_nel_marcatore"] = (len(m.get("fermate_sui_dati", [])) == 5 and m.get("tentativi") == 5
                                                    and m.get("candidato_eseguito") is False)

    # (c) ripartenza coi dati buoni + interruzione voluta dopo 2 pezzi: candidato eseguito, niente risultato
    t0 = time.perf_counter()
    try:
        giro(perc, interrompi_dopo_pezzi=2)
        controlli["interruzione_simulata"] = False
    except Interrotto:
        av = perc.avanzamento
        m = marcatore_di(perc)
        controlli["interruzione_simulata"] = ((av / "impronta.json").exists() and (av / "b.json").exists()
                                              and len(list(av.glob("pezzo_*.json"))) == 2
                                              and not perc.finale.exists() and m.get("candidato_eseguito") is True
                                              and str(m.get("stato", "")).startswith("interrotto durante il giro"))
    t_primo = time.perf_counter() - t0
    controlli["marcatore_scritto_prima_del_caricamento"] = (bool(chiamate["marcatore_gia_scritto"])
                                                           and all(chiamate["marcatore_gia_scritto"]))

    # (d) la ripresa rifiuta pezzi manomessi (copie della cartella interrotta): risultato con STOP (D4)
    manomissioni: Dict[str, object] = {}
    for caso in ("pezzo_senza_impronta", "pezzo_con_impronta_diversa", "manca_impronta_json",
                 "impronta_json_diversa"):
        p2 = Percorsi.prova(cartella / "manomesso" / caso)
        ignora = shutil.ignore_patterns("impronta.json") if caso == "manca_impronta_json" else None
        shutil.copytree(perc.avanzamento, p2.avanzamento, ignore=ignora)
        shutil.copy2(perc.marcatore, p2.marcatore)
        if caso in ("pezzo_senza_impronta", "pezzo_con_impronta_diversa"):
            f = p2.avanzamento / "pezzo_0000.json"
            x = json.loads(f.read_text(encoding="utf-8"))
            if caso == "pezzo_senza_impronta":
                del x["impronta"]
            else:
                x["impronta"] = "0" * 64
            scrivi_json(f, x)
        elif caso == "impronta_json_diversa":
            f = p2.avanzamento / "impronta.json"
            x = json.loads(f.read_text(encoding="utf-8"))
            x["impronta"] = "0" * 64
            scrivi_json(f, x)
        o2 = giro(p2)
        manomissioni[caso] = {"esito": o2["esito"], "motivo": o2.get("motivo"),
                              "risultato_scritto": p2.finale.exists()}
        controlli[f"ripresa_rifiuta_{caso}"] = (o2["esito"] == "STOP" and "avanzamento" in str(o2.get("motivo"))
                                                and p2.finale.exists())

    # (e) un marcatore di un altro giro (candidato gia' eseguito, impronta diversa): rifiuto PRIMA di caricare;
    #     un marcatore di un altro lanciatore: rifiuto prima di tutto
    p3 = Percorsi.prova(cartella / "marcatore_di_un_altro_giro")
    mk = marcatore_di(perc)
    mk["impronta_giro"] = "0" * 64
    scrivi_json(p3.marcatore, mk)
    n0 = chiamate["carica"]
    try:
        giro(p3)
        controlli["marcatore_di_un_altro_giro_rifiutato"] = False
    except GiaEseguito:
        controlli["marcatore_di_un_altro_giro_rifiutato"] = chiamate["carica"] == n0 and not p3.finale.exists()
    p5 = Percorsi.prova(cartella / "marcatore_di_un_altro_lanciatore")
    mk = marcatore_di(perc)
    mk.update({"sha256_lanciatore": "f" * 64, "candidato_eseguito": False, "stato": STATO_FERMO})
    scrivi_json(p5.marcatore, mk)
    n0p = chiamate["prepara"]
    try:
        giro(p5)
        controlli["marcatore_di_un_altro_lanciatore_rifiutato"] = False
    except GiaEseguito:
        controlli["marcatore_di_un_altro_lanciatore_rifiutato"] = chiamate["prepara"] == n0p and not p5.finale.exists()

    # (f) ripresa del giro interrotto, (g) guardia «una volta sola»
    out = giro(perc)
    controlli["ripresa_dal_file"] = (out.get("ripresa", {}).get("simulazioni_riprese_dal_file") == 2 * BLOCCO_SEMI
                                     and out.get("ripresa", {}).get("b_ripresa") is True)
    m = marcatore_di(perc)
    controlli["motivo_azzerato_a_giro_finito"] = (
        "motivo" in m and m["motivo"] is None and list(m)[0] == "motivo"
        and m.get("stato") == f"risultato scritto: {out['esito']}" and m.get("risultato_scritto") == str(perc.finale)
        and m.get("candidato_eseguito") is True and len(m.get("fermate_sui_dati", [])) == 5)
    try:
        giro(perc)
        controlli["guardia_una_volta_sola"] = False
    except GiaEseguito:
        controlli["guardia_una_volta_sola"] = True
    try:
        guardia_iniziale(perc)
        controlli["guardia_iniziale_col_risultato"] = False
    except GiaEseguito:
        controlli["guardia_iniziale_col_risultato"] = True
    controlli["file_finali_scritti"] = (perc.finale.exists() and perc.riassunto.exists()
                                        and perc.marcatore.exists()
                                        and len(list(perc.avanzamento.glob("pezzo_*.json"))) == len(SEMI_CASO) // BLOCCO_SEMI)
    controlli["riassunto_scritto_dopo_il_json"] = perc.riassunto.stat().st_mtime_ns >= perc.finale.stat().st_mtime_ns
    scritto = json.loads(perc.finale.read_text(encoding="utf-8"))
    controlli["risultato_registra_versioni_sha_semi_condizioni_note"] = bool(
        all(k in scritto.get("versioni", {}) for k in ("python", "numpy", "scipy"))
        and scritto.get("sha256_lanciatore") == SHA256_LANCIATORE
        and scritto.get("semi", {}).get("caso") == [0, 999]
        and set((scritto.get("caso") or {}).get("condizioni_superate", {})) ==
        {"profit_factor", "trade_minimi", "rendimento_positivo", "sopra_il_caso"}
        and "barre_ultimo_giorno" in scritto.get("note_ultimo_giorno_e_buchi", {})
        and scritto.get("impronta_giro") == impronta_di(contenuto))
    pm = scritto["info"]["completezza"]["per_mese"]
    controlli["d3_tabella_per_mese_e_avvisi_nel_risultato"] = bool(
        all({"attese", "last", "mark", "allineate", "quota", "settlement", "ore_dichiarate",
             "distanze_ore_osservate"} <= set(r) for r in pm.values())
        and any(a.startswith("AVVISO 2023-02:") for a in scritto["info"]["completezza"]["avvisi"])
        and "AVVISO" in perc.riassunto.read_text(encoding="utf-8"))
    controlli["esito_coerente_col_criterio"] = (
        out.get("esito") == ("passa" if out["criterio_vault"]["esito"] else "non passa"))

    # il motore deve rifare i numeri della validazione del log
    rif = registro._pulisci({"metriche": out["metriche"], "blocco": out.get("blocco"),
                             "durata_media_barre": out.get("durata_media_barre"),
                             "baseline_a": out.get("baseline_a"), "baseline_b": out.get("baseline_b"),
                             "percentile_caso": out.get("percentile_caso"),
                             "buy_and_hold_per_anno": out.get("buy_and_hold_per_anno"),
                             "btc_stessa_finestra": out.get("btc_stessa_finestra")})
    att = {k: val_log[k] for k in rif}
    diff = confronta(rif, att)
    controlli["rifa_la_validazione_del_log"] = not diff
    controlli["gemella_uguale_a_simula_baseline_casuale"] = bool(out["gemella"]["uguale"])
    controlli["percentile_90_delle_200_uguale_al_log"] = (
        round(float(statistica.percentile([s["r_medio"] for s in out["caso"]["per_seme"][:200]], 90)), 6)
        == val_log["baseline_b"]["percentile_90"])
    return {
        "cartella": str(cartella),
        "controlli": controlli,
        "differenze_dal_log": diff,
        "gemella": out["gemella"],
        "esito_sulla_validazione": out["esito"],
        "criterio_vault_sulla_validazione": out["criterio_vault"],
        "tasso_del_caso_sulla_validazione": out["tasso_del_caso"],
        "caso": {k: x for k, x in out["caso"].items() if k != "per_seme"},
        "tempi_s": out["tempi_s"],
        "secondi_prima_parte_interrotta": t_primo,
        "manomissioni": manomissioni,
        "fermate_sui_dati": fermate,
        "completezza_sulla_validazione": {k: comp[k] for k in ("fermano", "avvisi", "note")},
        "file_mensili_validazione": {k: file_val[k] for k in ("periodo", "serie", "mancanti", "illeggibili")},
        "impronta_giro": out["impronta_giro"],
        "versioni_nell_impronta": contenuto["versioni"],
        "nota": ("numeri sul periodo di validazione (in-sample), solo per provare il motore: "
                 "non sono un giudizio del vault"),
    }


def stima_tempo_vault(esito: Dict[str, object], d: Dict[str, object]) -> Dict[str, object]:
    """Stima del modo vault dai tempi misurati, scalati sul numero di barre della serie."""
    prova = esito.get("prova_motore_vault")
    if not prova:
        return {"testo": "prova del motore non eseguita: nessuna stima"}
    t = prova["tempi_s"]
    barre_ora = len(d["candele"])
    # 2024-01-01 -> 2026-09-30: 1004 giorni = 24.096 barre a 1h (stima: senza buchi)
    barre_vault = barre_ora + 1004 * 24
    f = barre_vault / barre_ora
    per_sim = t.get("secondi_per_simulazione")
    n_sim = 1000 + 200
    stima = f * (t["candidato_s"] + t.get("baseline_a_s", 0) + t.get("barre_vietate_s", 0)
                 + t.get("ingressi_1000_s", 0) + n_sim * per_sim)
    return {
        "barre_serie_validazione": barre_ora, "barre_serie_vault_stimate": barre_vault, "fattore": f,
        "secondi_per_simulazione_misurati": per_sim, "simulazioni_vault": n_sim,
        "secondi_stimati_un_processo": stima,
        "testo": (f"una simulazione sulla serie fino al 2023-12-31 ({barre_ora} barre): {per_sim:.3f} s; "
                  f"la serie fino al 2026-09-30 ha circa {barre_vault} barre (x{f:.2f}); "
                  f"con 1000 + 200 simulazioni, il candidato, la (a), le barre vietate e gli ingressi: "
                  f"circa {stima / 60:.0f} minuti con un processo (stima, piu' lo scarico del vault)"),
    }


# ---------------------------------------------------------------------------
# Modo vault
# ---------------------------------------------------------------------------


def modo_vault(worktree: Path, processi: int) -> int:
    perc = Percorsi.vault()
    # 1. una volta sola, prima di qualunque altra cosa (sola lettura, posti fissi)
    guardia_iniziale(perc)
    # 2. codice congelato
    controllo_codice = controlla_codice(worktree)
    importa_candidato(worktree)
    regole = leggi_regole_esame(worktree)
    radice = (worktree / "research").resolve()
    if Path(dati.RADICE_DEFAULT).resolve() != radice:
        raise Stop(f"radice dei dati inattesa: {dati.RADICE_DEFAULT}")
    # 3. il vault e' aperto? Lo dice dati.controlla_vault del worktree sulla radice del coordinamento
    #    (VaultChiuso se manca APERTURA.md), PRIMA di scrivere qualunque file; poi il contenuto (R4) e
    #    la copia nel worktree.
    dati.controlla_vault(dati.FINE_VAULT, COORDINAMENTO_RICERCA)
    impronte_codice = {rel: x["su_disco"] for rel, x in controllo_codice["file"].items()}
    ap = controlla_apertura(APERTURA_COORD.read_text(encoding="utf-8"), impronte_codice)
    if ap["problemi"]:
        raise Stop("; ".join(ap["problemi"]))
    copia = copia_apertura(APERTURA_COORD, radice / "vault" / "APERTURA.md")
    dati.controlla_vault(dati.FINE_VAULT, radice)
    with lucchetto(perc.avanzamento):
        guardia_iniziale(perc)  # di nuovo, col lucchetto preso
        info: Dict[str, object] = {"apertura": {**ap, "percorso": str(APERTURA_COORD), "copia": copia},
                                   "radice_dati": str(radice), "codice": controllo_codice,
                                   "lanciatore": str(Path(__file__).resolve()),
                                   "sha256_lanciatore": SHA256_LANCIATORE,
                                   "posti_fissi": {k: str(getattr(perc, k)) for k in ("finale", "riassunto",
                                                                                      "marcatore", "avanzamento")}}

        def prepara_vault() -> Dict[str, object]:
            """D1 (dopo il marcatore, nessuna candela letta): in-sample presente, leggibile e uguale alla
            campagna; scarico del vault; ogni file mensile 2024-01 -> 2026-09 presente e leggibile."""
            out: Dict[str, object] = {}
            file_insample = file_mensili(radice, C.INIZIO, dati.FINE_IN_SAMPLE)
            ferma_se_file_mancanti(file_insample, "file in-sample")
            try:
                out["impronte_insample"] = verifica_impronte_insample(worktree, radice)
            except Stop as e:
                raise FermoSuiDati("D1", f"file in-sample diversi da quelli della campagna: {e}")
            # scarico del vault (i file gia' presenti non si riscaricano); un errore di scarico si registra
            # e il file resta mancante: lo ferma il controllo qui sotto
            dati.azzera_checksum_mancanti()
            t0 = time.perf_counter()
            errori_scarico: Dict[str, str] = {}
            for s, tipo, tf in SERIE:
                try:
                    dati.scarica_periodo(s, tipo, tf, dati.INIZIO_VAULT, dati.FINE_VAULT, radice=radice)
                except Exception as e:  # noqa: BLE001 - rete, CHECKSUM diverso (file non scritto), ...
                    errori_scarico[nome_serie(s, tipo, tf)] = f"{type(e).__name__}: {e}"
            out["scarico_vault_secondi"] = time.perf_counter() - t0
            out["errori_scarico_vault"] = errori_scarico
            out["checksum_mancanti_vault"] = list(dati.CHECKSUM_MANCANTI)
            file_vault = file_mensili(radice, dati.INIZIO_VAULT, dati.FINE_VAULT)
            out["file_vault"] = {k: file_vault[k] for k in ("periodo", "serie", "mancanti", "illeggibili")}
            ferma_se_file_mancanti(file_vault, "file del vault", errori_scarico=errori_scarico,
                                   checksum_mancanti=out["checksum_mancanti_vault"])
            contenuto = contenuto_impronta("vault", impronte_codice,
                                           {**file_insample["impronte"], **file_vault["impronte"]},
                                           copia["sha256"], regole)
            return {"contenuto": contenuto, "info": out}

        def carica_vault() -> Dict[str, object]:
            """Le candele si leggono qui (dopo l'impronta nel marcatore); poi la completezza (D2, D3)."""
            try:
                s_ = dati.carica_serie_allineate(SIMBOLO, TF, C.INIZIO, dati.FINE_VAULT, radice=radice)
                funding = dati.carica_funding(SIMBOLO, C.INIZIO, dati.FINE_VAULT, radice=radice)
                f_det = dati.carica_funding_dettaglio(SIMBOLO, C.INIZIO, dati.FINE_VAULT, radice=radice)
            except dati.OltreIlVault:
                raise  # non e' un file illeggibile: e' una data fuori dal perimetro (errore, nessun risultato)
            except (ValueError, OSError, zipfile.BadZipFile) as e:
                raise FermoSuiDati("D1", f"un file del periodo non si legge al caricamento: {type(e).__name__}: {e}")
            btc, btc_errore = None, None
            try:
                btc = dati.carica_candele("BTCUSDT", TF, C.INIZIO, dati.FINE_VAULT, radice=radice)
            except Exception as e:  # noqa: BLE001 - BTC serve solo alla correlazione
                btc_errore = f"{type(e).__name__}: {e}"
            ms_barra = dati.durata_intervallo(TF)
            comp = controlla_completezza(candele=s_["candele"], tolte_last=s_["tolte_last"],
                                         tolte_mark=s_["tolte_mark"], funding=f_det, btc=btc,
                                         inizio=dati.INIZIO_VAULT, fine=dati.FINE_VAULT, ms_barra=ms_barra)
            if btc_errore:
                comp["avvisi"].append(f"AVVISO BTC non caricato ({btc_errore}): niente correlazione con BTC")
            # la parte in-sample della serie lunga, confrontata con la Fase 0 (D3: riportata, con avviso)
            pre = {"barre_tenute": sum(1 for c in s_["candele"] if c.ts < INIZIO_VAULT_TS),
                   "tolte_last": sum(1 for x in s_["tolte_last"] if x < INIZIO_VAULT_TS),
                   "tolte_mark": sum(1 for x in s_["tolte_mark"] if x < INIZIO_VAULT_TS)}
            comp["in_sample"] = {"rifatto": pre, "fase0_dati.md": FASE0_INSAMPLE, "uguale": pre == FASE0_INSAMPLE}
            if pre != FASE0_INSAMPLE:
                comp["avvisi"].append(f"AVVISO la parte prima del 2024 della serie non e' quella della Fase 0: "
                                      f"{pre} contro {FASE0_INSAMPLE}")
            return {"candele": s_["candele"], "mark": s_["candele_mark"], "funding": funding, "btc": btc,
                    "btc_errore": btc_errore, "ms_barra": ms_barra, "completezza": comp,
                    "info": {"barre": len(s_["candele"]), "tolte_last": s_["n_tolte_last"],
                             "tolte_mark": s_["n_tolte_mark"], "settlement_funding": len(funding),
                             "barre_btc": len(btc) if btc is not None else None}}

        esito = esame_periodo(etichetta="vault", percorsi=perc, prepara=prepara_vault, carica=carica_vault,
                              inizio_ts=INIZIO_VAULT_TS, fine=dati.FINE_VAULT, regole=regole, info=info,
                              dati_obbligatori=True, processi=processi)
    crit = esito.get("criterio_vault") or {}
    print(json.dumps({"esito": esito.get("esito"), "motivo": esito.get("esito_motivo") or esito.get("motivo"),
                      "criterio_vault": crit.get("esito"), "condizioni": crit.get("condizioni"),
                      "tasso_del_caso": esito.get("tasso_del_caso"),
                      "avvisi_dei_dati": (info.get("completezza") or {}).get("avvisi"),
                      "file": str(perc.finale)}, ensure_ascii=False, indent=1))
    return {"STOP": 2, "errore": 5}.get(esito.get("esito"), 0)


def modo_apertura(worktree: Path) -> int:
    controllo = controlla_codice(worktree)
    impronte = {rel: x["su_disco"] for rel, x in controllo["file"].items()}
    print(json.dumps({"candidato": CANDIDATO, "commit": COMMIT, "sha256": impronte, "semi": "0-999",
                      "sha256_lanciatore": SHA256_LANCIATORE,
                      "posti_fissi": {k: str(getattr(Percorsi.vault(), k)) for k in ("finale", "riassunto",
                                                                                     "marcatore", "avanzamento")}},
                     ensure_ascii=False, indent=1))
    print()
    print(testo_per_apertura(impronte))
    return 0


# ---------------------------------------------------------------------------


def main(argv: Optional[Sequence[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--worktree", type=Path, default=WORKTREE_DEFAULT,
                    help="worktree della campagna BNBUSDT (punta 2e29620a)")
    ap.add_argument("--processi", type=int, default=1, help="processi per le simulazioni (fork); default 1")
    sub = ap.add_subparsers(dest="modo", required=True)
    pp = sub.add_parser("parita", help="solo in-sample: scarico, impronte, validazione rifatta, prova del motore")
    pp.add_argument("--uscita", type=Path, required=True, help="file JSON dell'esito")
    pp.add_argument("--cartella-prova", type=Path, default=None,
                    help="cartella per la prova del motore sul periodo di validazione (nuova o vuota; "
                         "si svuota da sola solo dentro lo scratchpad)")
    pp.add_argument("--senza-prova", action="store_true", help="salta la prova del motore del vault")
    sub.add_parser("apertura", aliases=["requisiti-apertura"],
                   help="stampa cosa deve contenere APERTURA.md per questo candidato (sola lettura)")
    pv = sub.add_parser("vault", help="il giudizio nel vault (solo dopo l'apertura; posti fissi)")
    pv.add_argument("cartella", type=Path, nargs="?", default=None,
                    help=f"facoltativa; se c'e' deve essere {VAULT_COORD} (il risultato va sempre li')")
    a = ap.parse_args(argv)
    worktree = a.worktree.resolve()
    if a.modo == "parita":
        return modo_parita(worktree, a.uscita, a.cartella_prova, a.processi, a.senza_prova)
    try:
        if a.modo in ("apertura", "requisiti-apertura"):
            return modo_apertura(worktree)
        if a.cartella is not None and Path(a.cartella).resolve() != VAULT_COORD.resolve():
            raise Stop(f"il risultato del vault va solo in {VAULT_COORD}, non in {a.cartella}")
        return modo_vault(worktree, a.processi)
    except GiaEseguito as e:
        print(f"GiaEseguito: {e}", file=sys.stderr)
        return 4
    except FermoSuiDati as e:
        print(f"FERMO SUI DATI ({e.regola}), candidato non eseguito, nessun risultato scritto, vault non consumato: "
              f"{e.motivo}. Il marcatore lo registra; si riparte con lo stesso lanciatore dopo aver risolto.",
              file=sys.stderr)
        comp = e.dettagli.get("completezza") if isinstance(e.dettagli, dict) else None
        if comp:
            for riga in comp.get("fermano", []) + comp.get("avvisi", []):
                print(f"  {riga}", file=sys.stderr)
        return 6
    except Stop as e:
        print(f"STOP: {e}", file=sys.stderr)
        return 2
    except Exception as e:  # noqa: BLE001
        if dati is not None and isinstance(e, dati.VaultChiuso):
            print(f"VaultChiuso: {e}", file=sys.stderr)
            return 3
        raise


if __name__ == "__main__":
    sys.exit(main())
