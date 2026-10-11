#!/usr/bin/env python3
"""Lanciatore del Passo 5 (protocollo 4.5) per il candidato ADAUSDT-037.

Il candidato gira con il SUO codice: i moduli si importano dal worktree staccato sulla punta
del branch della campagna (``research/campagne/ADAUSDT/codice/`` e ``research/src/`` di quel
worktree, commit 47d6b2cc), aggiungendolo a ``sys.path`` come fanno gli script della campagna
(``comune.py`` mette in testa la radice del worktree, ``validazione.py`` la cartella ``codice``).
Qui non c'e' copia del codice del candidato: ci sono solo il giro del vault, il tasso del caso e
i controlli. Nel worktree il lanciatore scrive solo i dati scaricati in ``research/data/`` (fuori
da git), nel modo vault la copia di ``research/vault/APERTURA.md`` (uguale byte per byte a quella
del coordinamento) e, a fine giro, il segno ``research/data/vault/ADAUSDT_giro_vault_fatto.json``.
Nessun file tracciato del worktree si tocca; ogni modo controlla anche che nel worktree non ci
siano file non tracciati o ignorati che potrebbero essere importati al posto del codice vero.

Modi
----
``parita``      (gira adesso, solo in-sample). Riscarica con ``dati.scarica_periodo`` del worktree
                le quattro serie del candidato (ADAUSDT klines 15m, markPriceKlines 15m e
                fundingRate; BTCUSDT klines 15m) dal 2020-01 al 2023-12, le confronta con le
                impronte della campagna (``impronte.json``, 192 voci su 1.344: solo quelle delle
                quattro serie) e si ferma se una differisce. Controlla i conteggi di
                ``fase0_dati.md``. Poi rifa' la costruzione con ``run.testa`` e la validazione
                eseguendo ``validazione.py`` della campagna, cosi' com'e', con il log della
                campagna sostituito da una copia di lavoro (il ``log.jsonl`` del worktree non si
                tocca), e confronta ogni campo delle due voci rifatte con quelle del log, e i
                numeri della consegna uno per uno. Dimostra che la gemella delle entrate casuali
                (quella del tasso del caso) da' gli stessi R medi di
                ``motore.simula_baseline_casuale`` sui semi 0..199. Misura i tempi e stima quelli
                del vault.
``requisiti-apertura``  stampa cosa deve contenere APERTURA.md per questo candidato.
``prova-vault`` (gira adesso, solo in-sample). Esegue lo STESSO giro del modo vault (guardia
                «una volta sola», marcatore, impronta dell'avanzamento, regola dei dati D1-D4,
                esame, esiti limite, scrittura) sul periodo di VALIDAZIONE al posto del vault,
                con tutti i file nella cartella di prova data come argomento. La regola dei dati
                vale come nel vault (``--ferma-sui-dati`` resta accettato e non cambia nulla).
                Non legge APERTURA.md (il vault resta chiuso).
``vault``       (solo dopo l'apertura). Tutto a posti FISSI, qualunque siano gli argomenti, e solo
                sul worktree /home/user/vault_ADAUSDT:
                1. (R4) legge ``/home/user/coordinamento/research/vault/APERTURA.md``; finche'
                   manca (o e' vuota) si ferma con ``VaultChiuso`` (codice d'uscita 3) senza
                   scrivere nulla. Pretende che contenga l'ID ``ADAUSDT-037``, lo SHA-256
                   completo di ``regole.md`` e di ogni file di codice controllato contro il
                   worktree (``requisiti-apertura`` li stampa) e i semi 0-999; la copia da se'
                   in ``research/vault/APERTURA.md`` del worktree (dove la cerca
                   ``dati.controlla_vault`` del candidato), uguale byte per byte (verificato),
                   solo DOPO il controllo del marcatore (una copia gia' presente e diversa ferma
                   tutto prima di scrivere qualunque file);
                2. (R2) una volta sola: risultato
                   ``/home/user/coordinamento/research/vault/ADAUSDT-037_vault.json`` e marcatore
                   ``/home/user/coordinamento/research/vault/ADAUSDT-037_giro_iniziato.json``. Il
                   marcatore si crea in modo esclusivo (O_EXCL) PRIMA di scaricare e caricare i
                   dati del vault, dentro un lucchetto ``fcntl`` (D5). Se il risultato esiste,
                   rifiuta sempre; se esiste il marcatore, rifiuta salvo la ripresa dello STESSO
                   giro (stessa impronta d'avvio: lanciatore, codice, APERTURA.md, regole, semi,
                   dati in-sample, versioni di python, numpy e scipy). In cima al marcatore
                   ``stato`` e ``motivo`` sono sempre quelli dell'ultimo passo: a giro finito il
                   motivo torna vuoto (D5); la storia dei passi resta in ``storia``;
                3. (R3, R6) avanzamento a pezzi in
                   ``/home/user/coordinamento/research/vault_strumenti/avanzamento/ADAUSDT-037/``
                   (fuori da research/vault/), con il file ``IMPRONTA.json``: l'impronta del giro
                   contiene lo SHA-256 del lanciatore, dei file del codice, dei file di dati
                   (in-sample e vault) e le versioni di python, numpy e scipy (D5). Ogni pezzo
                   porta l'impronta; la ripresa rifiuta pezzi senza impronta, con un'impronta
                   diversa, o se manca ``IMPRONTA.json``;
                4. regola dei dati (D1-D4, sostituisce la vecchia R1, uguale per i tre lanciatori):
                   D1. PRIMA di leggere qualunque candela, STOP SENZA risultato se manca o non si
                       legge (zip rotto, CRC sbagliato, nessun CSV o piu' di uno, CSV vuoto) anche
                       un solo file mensile 2024-01 -> 2026-09 di una serie usata: ADAUSDT klines
                       15m, markPriceKlines 15m, fundingRate e BTCUSDT klines 15m (132 file);
                   D2. dopo il caricamento e PRIMA di eseguire il candidato, STOP SENZA risultato
                       solo se l'ultima barra allineata last/mark non e' quella delle 23:45 del
                       2026-09-30, se un mese ha meno del 50% delle barre allineate attese, o se un
                       mese non ha nessun settlement di funding. ADAUSDT-037 usa BTC nel segnale
                       (rendimento di BTC a 24 ore): per BTCUSDT valgono le stesse soglie (ultima
                       barra e 50% per mese);
                   D3. tutto il resto si riporta e basta, nel JSON e nel riassunto: per mese barre
                       attese, last, mark, allineate e quota, BTC e quota, barre di ADA senza BTC,
                       con un AVVISO sotto il 99% (come le barre tolte dichiarate dalla campagna);
                       settlement di funding per mese con gli intervalli osservati e quelli
                       dichiarati dai file (nessun numero atteso costruito sull'intervallo piu'
                       corto), con un AVVISO se fra due settlement passa piu' dell'intervallo
                       dichiarato;
                   D4. uno STOP di D1/D2 (o un errore qualunque) PRIMA dell'esecuzione del
                       candidato non consuma il vault: nessun risultato, il marcatore registra
                       «fermo sui dati, candidato non eseguito» (o l'errore) e lo stesso giro
                       riparte con lo stesso lanciatore dopo aver risolto il problema (uscita 4).
                       I file di dati si fissano per sempre quando il candidato viene eseguito;
                5. (R5, solo DOPO che il candidato e' stato eseguito) esiti: «passa», «non passa»,
                   «non si sa» (sotto i trade minimi del vault, anche con 0 trade: sezione 8),
                   «non valutabile» (entrate casuali non costruibili, o qualunque STOP dopo
                   l'esecuzione del candidato). Da li' ogni fine scrive il risultato: prima il
                   JSON, poi il riassunto .md, poi il marcatore «finito» e il segno (R6). Solo
                   un'interruzione (kill, Ctrl-C) lascia il giro da riprendere; nella ripresa di
                   un giro in cui il candidato e' gia' stato eseguito un file che manca ferma
                   senza risultato (si rimette lo stesso file), un file DIVERSO da' «non
                   valutabile».

Regola del giro (vault e prova): la serie si carica con ``comune.carica`` della campagna, dal
2020-01-01 (primo giorno della campagna) alla fine del periodo, con ``carica_serie_allineate``
(intersezione last/mark), funding e BTCUSDT sugli stessi ts; gli indicatori sono caldi. Il
candidato, la (a) e la (b) con 200 semi si fanno con ``comune.valuta(var, periodo="validazione")``
dopo aver messo in memoria (non nel file) ``comune.FINE_VALIDAZIONE`` = fine del periodo e
``comune.FINE_COSTRUZIONE_TS`` = l'ultimo ms prima del periodo: e' la stessa convenzione della
validazione (nessun ingresso su segnali di barre che chiudono entro il taglio, contano i trade
entrati dopo il taglio). Per questo il blocco ``come_validazione`` del risultato porta
``"periodo": "validazione"``: e' l'etichetta del codice della campagna, il periodo vero e' quello
del campo ``periodo`` del risultato. Le 1.000 entrate casuali del tasso del caso usano
``statistica.entrate_casuali_per_semi`` e ``motore.esegui`` con gli stessi argomenti di
``motore.simula_baseline_casuale`` (barre vietate = quelle della (b) della campagna, cioe' tutte
le barre fino al taglio, i mesi esclusi, le barre col segnale non valido, piu' l'ultima barra),
ma tengono per ogni seme tutte le metriche del criterio, non solo l'R medio. Esito: il
``criterio_vault`` di ``statistica``; in piu' (sezione 7) un candidato che passerebbe ma ha
violazioni di liquidazione e' «non passa», e un trade entrato prima del taglio ferma il giro.

Codici d'uscita: 0 risultato scritto (qualunque esito); 3 vault chiuso; 4 fermo SENZA risultato
prima dell'esecuzione del candidato (D1, D2 o un errore: il vault non e' consumato, si riparte con
lo stesso lanciatore); 5 interruzione voluta (solo la prova della ripresa).

Uso
---
    python3 -I ADAUSDT.py parita --uscita /percorso/vault_parita_ADAUSDT.json
    python3 -I ADAUSDT.py requisiti-apertura      (oppure: apertura)
    python3 -I ADAUSDT.py prova-vault /cartella/di/prova [--n-caso 1000]
    python3 -I ADAUSDT.py vault

Opzioni: ``--worktree`` (predefinito /home/user/vault_ADAUSDT; nel modo vault solo quello),
``--processi`` (4, non cambia i numeri), ``--senza-scarico``; per la prova ``--pezzo`` (semi per
file di avanzamento, 50) e, solo in-sample, ``--dal``/``--fine`` (per provare gli esiti limite).
"""
from __future__ import annotations

import argparse
import fcntl
import hashlib
import json
import math
import multiprocessing as mp
import os
import platform
import re
import runpy
import subprocess
import sys
import time
import traceback
import zipfile
from collections import Counter
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from types import SimpleNamespace

sys.dont_write_bytecode = True  # niente __pycache__ nel worktree della campagna

# SHA-256 di questo file letto all'import, cioe' del codice che gira (R3, R6): una modifica del file
# a giro iniziato non cambia l'impronta del giro in corso, e cambia quella del giro successivo.
SHA256_LANCIATORE = hashlib.sha256(Path(__file__).resolve().read_bytes()).hexdigest()

SIMBOLO = "ADAUSDT"
CANDIDATO = "ADAUSDT-037"
ID_VAL = "ADAUSDT-037-V06"
WORKTREE_DEFAULT = Path("/home/user/vault_ADAUSDT")
COMMIT_ATTESO = "47d6b2cce7d9ac8983c0bfa680c5c82696eae6aa"
CODICE_REL = "research/campagne/ADAUSDT/codice"
FILE_REGOLE = "research/campagne/ADAUSDT/candidati/ADAUSDT-037/regole.md"
FILE_IMPRONTE = "research/campagne/ADAUSDT/impronte.json"
FILE_LOG = "research/campagne/ADAUSDT/log.jsonl"
FILE_PARAMETRI = "research/config/parametri.yaml"

# SHA-256 dei file del candidato alla punta 47d6b2cc (analisi preparatoria, ricontrollati l'11 ott
# 2026 sul worktree): sono quelli da scrivere in APERTURA.md. registrazioni.py entra perche'
# varianti.py lo importa all'ultima riga; run.py e registro.py perche' validazione.py li usa.
FILE_ATTESI = {
    FILE_REGOLE: "731a06569ef2d6f4408af87c648b7e2b0f3b92a02475ff41a27241b5c73654c9",
    f"{CODICE_REL}/varianti.py": "e447ec1898e2b62f0600a9e0450fb8da3b6544590a8e7abf0f0c51bbdad04841",
    f"{CODICE_REL}/comune.py": "acf2086ab5c3f302dfc1f5b708398197e33f6a7683f23426b3ceeb323a667215",
    f"{CODICE_REL}/registrazioni.py": "861f7dc8761a21f07138ceef2a9aa9ab1cd14813e28936fb3dc91768cd3913bd",
    f"{CODICE_REL}/validazione.py": "228e16a68d05e9312303eaf240775300a5bd91f2098a6eb9a5f143ef19c214cf",
    f"{CODICE_REL}/run.py": "99f50c6ca28b05a894ebbf5bb8ebe0bb39df9ebc32d05d2602f4d0dbac7f945f",
    f"{CODICE_REL}/registro.py": "a2629684dcba6d344e7050343c63d884f56c2e2df7d538fd7b6eac091ebc48d3",
    "research/src/dati.py": "395b52409494f79ebec28a57866162b60aa37750cb15482232f536b3bf49a950",
    "research/src/motore.py": "b3d5e1a93954f5b8cad34b74937592cf2b0ade237cbcc1e789a0ee195e6b0970",
    "research/src/statistica.py": "e5d5f0e42b7f4823b6db4a91152b32fc6b2d2bf6b0b3bddf4183ee542d1c3f92",
    "research/src/__init__.py": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    "research/__init__.py": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    # impronta scritta in fase0_dati.md
    FILE_IMPRONTE: "7d3b9d8915a35db71127933fca3c38d8edf121402772d360ee795f3523ef2911",
    FILE_PARAMETRI: None,  # si riporta; i valori che servono si controllano uno per uno
}

# Solo le serie del candidato: ADA last e mark a 15m, funding di ADA, BTC last a 15m.
SERIE = (("ADAUSDT", "klines", "15m"), ("ADAUSDT", "markPriceKlines", "15m"),
         ("ADAUSDT", "fundingRate", None), ("BTCUSDT", "klines", "15m"))
PREFISSI_IMPRONTE = {"ADAUSDT": ("klines/15m/", "markPriceKlines/15m/", "fundingRate/"),
                     "BTCUSDT": ("klines/15m/",)}
INIZIO_IN_SAMPLE = date(2020, 1, 1)
FINE_IN_SAMPLE = date(2023, 12, 31)
INIZIO_VAULT = date(2024, 1, 1)
FINE_VAULT = date(2026, 9, 30)
TAGLIO_VAULT_TS = 1704067199999  # 2023-12-31 23:59:59.999 UTC: contano i trade entrati dopo
MS_15M = 900_000

# Numeri dell'in-sample scritti dalla campagna (fase0_dati.md, tabella a 15m e paragrafi)
ATTESI_FASE0 = {"barre_tenute": 137_151, "tolte_last": 193, "tolte_mark": 1_147, "volume_mancante": 0,
                "settlement_funding": 4_327, "barre_btc": 140_256}

PEZZO_DEFAULT = 50
PROCESSI_DEFAULT = 4

# Posti FISSI del modo vault (R2, R6): non dipendono da argomenti ne' da dove sta questo file.
VAULT_COORD = Path("/home/user/coordinamento/research/vault")
APERTURA_COORD = VAULT_COORD / "APERTURA.md"
RISULTATO_VAULT = VAULT_COORD / f"{CANDIDATO}_vault.json"
RIASSUNTO_VAULT = VAULT_COORD / f"{CANDIDATO}_vault.md"
MARCATORE_VAULT = VAULT_COORD / f"{CANDIDATO}_giro_iniziato.json"
AVANZAMENTO_VAULT = Path("/home/user/coordinamento/research/vault_strumenti/avanzamento") / CANDIDATO
APERTURA_REL_WORKTREE = "research/vault/APERTURA.md"  # dove la cerca dati.controlla_vault del candidato
SEGNO_REL_WORKTREE = "research/data/vault/ADAUSDT_giro_vault_fatto.json"  # segno in piu' (fuori da git)

# I semi delle entrate casuali del tasso del caso (simulazioni_caso = 1000 di parametri.yaml).
# parametri.yaml non li scrive: li deve scrivere APERTURA.md (R4).
SEMI_CASO = (0, 999)

# Regola dei dati del coordinamento (D1-D5, sostituisce la vecchia R1; uguale per i tre lanciatori).
# D2: sotto il 50% delle barre allineate attese in un mese il giro si ferma PRIMA di eseguire il
# candidato, senza risultato; D3: sotto il 99% e' solo un AVVISO, come le barre tolte dichiarate dalla
# campagna (nell'in-sample di ADA, dal 2021, 2022-10 al 96,8% e 2023-02 al 96,4%, per un giorno intero
# di mark mancante: fase0_dati.md).
TF = "15m"                       # il timeframe del candidato (controllato contro varianti.VARIANTI)
QUOTA_BARRE_BLOCCO = 0.50        # D2: barre allineate per mese, sulle attese
QUOTA_BARRE_AVVISO = 0.99        # D3
BTC_NEL_SEGNALE = True           # ADAUSDT-037 usa il rendimento di BTC a 24 ore nel segnale: per BTC
                                 # valgono le stesse soglie di D2 (ultima barra e 50% per mese)
STATO_FERMO_DATI = "fermo sui dati, candidato non eseguito"
STATO_FERMO_ERRORE = "fermo per un errore prima del candidato, candidato non eseguito"
STATO_FERMO_DATI_DOPO = ("fermo sui dati, candidato gia' eseguito in un tentativo interrotto: si riprende solo "
                         "con gli stessi file")
MS_ORA = 3_600_000

# R4: i file che APERTURA.md deve elencare con lo SHA-256 completo: regole.md e ogni file di codice
# controllato contro il worktree (impronte.json e' un file di dati, parametri.yaml la configurazione).
FILE_CODICE = tuple(rel for rel in FILE_ATTESI if rel.endswith(".py"))
FILE_PER_APERTURA = (FILE_REGOLE, *FILE_CODICE)

# Numeri della consegna (consegna.md), come sono scritti, con i decimali scritti.
# (nome, periodo, valore scritto, decimali, funzione che lo legge dalla voce rifatta)
CONSEGNA = [
    ("trade", "validazione", 82, 0, lambda v: v["metriche"]["trade"]),
    ("R medio a trade", "validazione", 0.624, 3, lambda v: v["metriche"]["r_medio"]),
    ("R medio senza i 3 migliori", "validazione", 0.014, 3, lambda v: v["metriche"]["r_medio_senza_3_migliori"]),
    ("profit factor", "validazione", 2.15, 2, lambda v: v["metriche"]["profit_factor"]),
    ("win rate %", "validazione", 39, 0, lambda v: 100 * v["metriche"]["win_rate"]),
    ("rendimento 2022 %", "validazione", -5.4, 1, lambda v: 100 * v["metriche"]["rendimento_per_anno"]["2022"]),
    ("rendimento 2023 %", "validazione", 68.7, 1, lambda v: 100 * v["metriche"]["rendimento_per_anno"]["2023"]),
    ("R per anno 2022", "validazione", -0.683, 3, lambda v: v["metriche"]["r_medio_per_anno"]["2022"]),
    ("R per anno 2023", "validazione", 0.765, 3, lambda v: v["metriche"]["r_medio_per_anno"]["2023"]),
    ("baseline (a)", "validazione", -1.154, 3, lambda v: v["baseline_a"]["media"]),
    ("t contro la (a)", "validazione", 3.65, 2, lambda v: v["baseline_a"]["t"]),
    ("baseline (b)", "validazione", -0.312, 3, lambda v: v["baseline_b"]["media"]),
    ("t contro la (b)", "validazione", 2.28, 2, lambda v: v["baseline_b"]["t"]),
    ("percentile fra le (b)", "validazione", 99, 0, lambda v: v["percentile_caso"]),
    ("p-value contro la (b)", "validazione", 0.0139, 4, lambda v: v["baseline_b"]["p_value"]),
    ("90° percentile della (b)", "validazione", 0.0401, 4, lambda v: v["baseline_b"]["percentile_90"]),
    ("buy and hold 2022 long %", "validazione", -32, 0, lambda v: 100 * v["buy_and_hold_per_anno"]["2022"]["long"]),
    ("buy and hold 2023 long %", "validazione", 142, 0, lambda v: 100 * v["buy_and_hold_per_anno"]["2023"]["long"]),
    ("stop medio %", "validazione", 1.6, 1, lambda v: 100 * v["metriche"]["stop_medio_pct"]),
    ("durata media ore", "validazione", 10.9, 1, lambda v: v["metriche"]["durata_media_ore"]),
    ("buchi nei dati", "validazione", 3, 0, lambda v: v["metriche"]["buchi_dati"]),
    ("trade ridotti", "validazione", 0, 0, lambda v: v["metriche"]["trade_ridotti"]),
    ("violazioni di liquidazione", "validazione", 0, 0, lambda v: v["metriche"]["violazioni_liquidazione"]),
    ("asticella BH 10% m=1 passa", "validazione", True, None, lambda v: v["asticella"]["passa"]),
    ("trade", "costruzione", 178, 0, lambda v: v["metriche"]["trade"]),
    ("R medio a trade", "costruzione", 0.252, 3, lambda v: v["metriche"]["r_medio"]),
    ("R medio senza i 3 migliori", "costruzione", 0.109, 3, lambda v: v["metriche"]["r_medio_senza_3_migliori"]),
    ("profit factor", "costruzione", 1.42, 2, lambda v: v["metriche"]["profit_factor"]),
    ("win rate %", "costruzione", 43, 0, lambda v: 100 * v["metriche"]["win_rate"]),
    ("rendimento 2020 %", "costruzione", 26.7, 1, lambda v: 100 * v["metriche"]["rendimento_per_anno"]["2020"]),
    ("rendimento 2021 %", "costruzione", 24.2, 1, lambda v: 100 * v["metriche"]["rendimento_per_anno"]["2021"]),
    ("rendimento 2022 %", "costruzione", -3.1, 1, lambda v: 100 * v["metriche"]["rendimento_per_anno"]["2022"]),
    ("R per anno 2020", "costruzione", 0.399, 3, lambda v: v["metriche"]["r_medio_per_anno"]["2020"]),
    ("R per anno 2021", "costruzione", 0.305, 3, lambda v: v["metriche"]["r_medio_per_anno"]["2021"]),
    ("R per anno 2022", "costruzione", -0.069, 3, lambda v: v["metriche"]["r_medio_per_anno"]["2022"]),
    ("drawdown massimo %", "costruzione", 10.5, 1, lambda v: 100 * v["metriche"]["drawdown_max"]),
    ("baseline (a)", "costruzione", -0.736, 3, lambda v: v["baseline_a"]["media"]),
    ("t contro la (a)", "costruzione", 2.31, 2, lambda v: v["baseline_a"]["t"]),
    ("baseline (b)", "costruzione", -0.137, 3, lambda v: v["baseline_b"]["media"]),
    ("t contro la (b)", "costruzione", 2.51, 2, lambda v: v["baseline_b"]["t"]),
    ("percentile fra le (b)", "costruzione", 98, 0, lambda v: v["percentile_caso"]),
    ("stop medio %", "costruzione", 3.1, 1, lambda v: 100 * v["metriche"]["stop_medio_pct"]),
    ("stop oltre il 6%", "costruzione", 17, 0, lambda v: v["metriche"]["stop_oltre_6pct"]),
    ("durata media ore", "costruzione", 12.5, 1, lambda v: v["metriche"]["durata_media_ore"]),
    ("trade ridotti", "costruzione", 0, 0, lambda v: v["metriche"]["trade_ridotti"]),
    ("violazioni di liquidazione", "costruzione", 0, 0, lambda v: v["metriche"]["violazioni_liquidazione"]),
]


# ---------------------------------------------------------------------------
# Utilita'
# ---------------------------------------------------------------------------


def adesso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for blocco in iter(lambda: f.read(1 << 20), b""):
            h.update(blocco)
    return h.hexdigest()


def sha256_testo(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def pulito(x):
    """Per il JSON finale: numeri numpy in numeri Python, inf e nan in stringhe, chiavi in stringhe."""
    try:
        import numpy as np
        if isinstance(x, np.generic):
            x = x.item()
        elif isinstance(x, np.ndarray):
            x = x.tolist()
    except ImportError:  # pragma: no cover
        pass
    if isinstance(x, float) and (math.isinf(x) or math.isnan(x)):
        return str(x)
    if isinstance(x, dict):
        return {str(k): pulito(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [pulito(v) for v in x]
    if isinstance(x, Path):
        return str(x)
    return x


def scrivi_json(p: Path, contenuto, grezzo: bool = False) -> None:
    """Scrittura atomica. ``grezzo``: senza ``pulito`` (i file di avanzamento tengono inf come Infinity)."""
    p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.with_name(p.name + f".tmp{os.getpid()}")
    testo = json.dumps(contenuto if grezzo else pulito(contenuto), ensure_ascii=False, indent=1)
    tmp.write_text(testo + "\n", encoding="utf-8")
    os.replace(tmp, p)


def scrivi_testo(p: Path, testo: str) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.with_name(p.name + f".tmp{os.getpid()}")
    tmp.write_text(testo, encoding="utf-8")
    os.replace(tmp, p)


def scrivi_json_nuovo(p: Path, contenuto) -> bool:
    """Scrive ``p`` solo se non esiste (link atomico: mai una sovrascrittura). False se c'era gia'."""
    p.parent.mkdir(parents=True, exist_ok=True)
    testo = json.dumps(pulito(contenuto), ensure_ascii=False, indent=1) + "\n"
    tmp = p.with_name(p.name + f".tmp{os.getpid()}")
    tmp.write_text(testo, encoding="utf-8")
    try:
        os.link(tmp, p)
        return True
    except FileExistsError:
        return False
    except OSError:  # file system senza link: creazione esclusiva diretta
        try:
            with open(p, "x", encoding="utf-8") as f:
                f.write(testo)
            return True
        except FileExistsError:
            return False
    finally:
        tmp.unlink(missing_ok=True)


def sha256_json(x) -> str:
    return sha256_testo(json.dumps(pulito(x), ensure_ascii=False, sort_keys=True, separators=(",", ":")))


def sha256_lanciatore() -> str:
    """Lo SHA-256 di questo file com'era quando e' stato importato (cioe' del codice che sta girando)."""
    return SHA256_LANCIATORE


def versioni() -> dict:
    """R6: le versioni con cui il conto e' stato fatto."""
    out = {"python": platform.python_version(), "implementazione": platform.python_implementation(),
           "sistema": platform.platform()}
    for nome in ("numpy", "scipy", "yaml"):
        try:
            out[nome] = __import__(nome).__version__
        except Exception as e:  # pragma: no cover
            out[nome] = f"non disponibile: {e}"
    return out


def versioni_impronta() -> dict:
    """D5: le versioni che entrano nell'impronta del giro (una ripresa con un ambiente diverso non e'
    lo stesso giro: i p-value possono cambiare all'ultima cifra da una versione di scipy all'altra)."""
    v = versioni()
    return {"python": v["python"], "numpy": v["numpy"], "scipy": v["scipy"]}


def _iso(ts) -> str | None:
    if ts is None:
        return None
    return datetime.fromtimestamp(ts / 1000, tz=timezone.utc).strftime("%Y-%m-%d %H:%M")


def _mese(ts: int) -> str:
    d = datetime.fromtimestamp(ts / 1000, tz=timezone.utc)
    return f"{d.year:04d}-{d.month:02d}"


class Fermo(Exception):
    """Uno STOP voluto DOPO che il candidato e' stato eseguito (R5, D4): chi lo prende scrive
    comunque il risultato, con esito «non valutabile» e il motivo. ``parziale`` e' il risultato
    costruito fin li' (con le metriche del candidato, se ci sono gia')."""

    def __init__(self, motivo: str, dettagli=None):
        super().__init__(motivo)
        self.motivo = motivo
        self.dettagli = dettagli
        self.parziale = None


class FermoSenzaRisultato(Exception):
    """D1, D2 o un errore PRIMA che il candidato sia eseguito (D4): il giro si ferma SENZA scrivere
    un risultato e il vault non e' consumato. Il marcatore registra lo stato (``STATO_FERMO_DATI``,
    «fermo sui dati, candidato non eseguito», o ``STATO_FERMO_ERRORE``) col motivo; lo stesso giro
    riparte con lo stesso lanciatore dopo aver risolto il problema. Codice d'uscita 4."""

    def __init__(self, regola: str, motivo: str, dettagli=None, stato: str = STATO_FERMO_DATI):
        super().__init__(f"{regola}: {motivo}")
        self.regola = regola
        self.motivo = motivo
        self.dettagli = dettagli
        self.stato = stato


class InterruzioneVoluta(BaseException):
    """Solo per la prova della ripresa: un'interruzione come un kill, senza risultato."""


def _numero(x) -> bool:
    return isinstance(x, (int, float)) and not isinstance(x, bool)


def confronta(atteso, trovato, percorso: str = "", tolleranza_rel: float = 0.0) -> list:
    """Differenze campo per campo (lista vuota = tutto uguale). Numeri: uguaglianza esatta salvo tolleranza."""
    diff = []
    if isinstance(atteso, dict) and isinstance(trovato, dict):
        for k in sorted(set(atteso) | set(trovato), key=str):
            sotto = f"{percorso}.{k}" if percorso else str(k)
            if k not in trovato:
                diff.append(f"{sotto}: c'e' nel log, manca nel rifatto")
            elif k not in atteso:
                diff.append(f"{sotto}: c'e' nel rifatto, manca nel log")
            else:
                diff += confronta(atteso[k], trovato[k], sotto, tolleranza_rel)
    elif isinstance(atteso, list) and isinstance(trovato, list):
        if len(atteso) != len(trovato):
            diff.append(f"{percorso}: lunghezza {len(atteso)} nel log, {len(trovato)} nel rifatto")
        else:
            for i, (a, b) in enumerate(zip(atteso, trovato)):
                diff += confronta(a, b, f"{percorso}[{i}]", tolleranza_rel)
    elif _numero(atteso) and _numero(trovato):
        a, b = float(atteso), float(trovato)
        if a == b or (math.isnan(a) and math.isnan(b)):
            return diff
        if tolleranza_rel and abs(a - b) <= tolleranza_rel * max(abs(a), abs(b)):
            return diff
        diff.append(f"{percorso}: log {atteso!r}, rifatto {trovato!r} (differenza {b - a:+.3g})")
    elif atteso != trovato:
        diff.append(f"{percorso}: log {atteso!r}, rifatto {trovato!r}")
    return diff


# ---------------------------------------------------------------------------
# Il codice del candidato (dal worktree, mai copiato)
# ---------------------------------------------------------------------------


def carica_moduli(worktree: Path) -> SimpleNamespace:
    """Importa il codice della campagna dal worktree, come fanno i suoi script."""
    worktree = worktree.resolve()
    codice = worktree / CODICE_REL
    if not (codice / "comune.py").is_file():
        raise SystemExit(f"STOP: {codice}/comune.py non c'e': il worktree non e' quello della campagna")
    for presente in ("research", "comune", "varianti", "registro", "run", "registrazioni"):
        if presente in sys.modules:
            raise SystemExit(f"STOP: il modulo {presente!r} e' gia' importato da altrove: rilanciare in un processo nuovo")
    sys.path.insert(0, str(worktree))
    sys.path.insert(0, str(codice))
    import comune  # noqa: E402  (mette in testa a sys.path la radice del worktree, come in campagna)
    import registro  # noqa: E402
    import run  # noqa: E402
    import varianti  # noqa: E402
    from research.src import dati, motore, statistica  # noqa: E402

    for mod in (comune, registro, run, varianti, dati, motore, statistica):
        if worktree not in Path(mod.__file__).resolve().parents:
            raise SystemExit(f"STOP: {mod.__name__} viene da {mod.__file__}, non dal worktree {worktree}")
    if dati.RADICE_DEFAULT.resolve() != worktree / "research":
        raise SystemExit(f"STOP: dati.RADICE_DEFAULT = {dati.RADICE_DEFAULT}, non {worktree / 'research'}")
    return SimpleNamespace(worktree=worktree, codice=codice, comune=comune, registro=registro, run=run,
                           varianti=varianti, dati=dati, motore=motore, statistica=statistica)


def _git(worktree: Path, *argomenti) -> str:
    return subprocess.run(["git", "-C", str(worktree), *argomenti], capture_output=True, text=True,
                          check=True).stdout.strip()


def file_fuori_da_git(worktree: Path) -> dict:
    """File non tracciati e ignorati del worktree. Ammessi solo i dati (``research/data/``), la copia
    di ``research/vault/APERTURA.md`` e le cartelle ``__pycache__`` (Python non importa mai un .pyc
    da li' senza il suo .py). Ogni altro file potrebbe essere importato al posto di un modulo vero
    (codice/ e la radice del worktree stanno in testa a sys.path): e' un problema."""
    non_tracciati = _git(worktree, "ls-files", "--others", "--exclude-standard").splitlines()
    ignorati = _git(worktree, "ls-files", "--others", "--ignored", "--exclude-standard", "--directory").splitlines()
    sospetti = []
    for rel in non_tracciati + ignorati:
        rel_pulito = rel.strip().strip('"')
        if not rel_pulito:
            continue
        if rel_pulito == "research/data/" or rel_pulito.startswith("research/data/"):
            continue
        if rel_pulito == APERTURA_REL_WORKTREE:
            continue
        if "__pycache__" in Path(rel_pulito).parts:
            continue
        sospetti.append(rel_pulito)
    return {"non_tracciati": non_tracciati, "ignorati": ignorati, "non_ammessi": sospetti}


def controlla_codice(worktree: Path, fermati: bool = True) -> dict:
    """Commit, file tracciati senza modifiche, nessun file estraneo, SHA-256 dei file del candidato."""
    head = _git(worktree, "rev-parse", "HEAD")
    modificati = _git(worktree, "status", "--porcelain", "--untracked-files=no")
    fuori = file_fuori_da_git(worktree)
    file = {}
    diversi = []
    for rel, atteso in FILE_ATTESI.items():
        trovato = sha256_file(worktree / rel)
        file[rel] = trovato
        if atteso and trovato != atteso:
            diversi.append(f"{rel}: atteso {atteso}, trovato {trovato}")
    esito = {"commit": head, "commit_atteso": COMMIT_ATTESO, "file_tracciati_modificati": modificati.splitlines(),
             "file_fuori_da_git": fuori, "sha256": file, "sha256_diversi": diversi}
    problemi = []
    if head != COMMIT_ATTESO:
        problemi.append(f"commit {head}, atteso {COMMIT_ATTESO}")
    if modificati:
        problemi.append(f"file tracciati modificati nel worktree: {modificati}")
    if fuori["non_ammessi"]:
        problemi.append(f"file non tracciati o ignorati nel worktree, che potrebbero essere importati: "
                        f"{fuori['non_ammessi'][:20]}")
    problemi += diversi
    esito["problemi"] = problemi
    esito["ok"] = not problemi
    if problemi and fermati:
        raise SystemExit("STOP: il codice del candidato non e' quello congelato: " + "; ".join(problemi))
    return esito


def leggi_regole_esame(m) -> dict:
    """I valori del Passo 5 da research/config/parametri.yaml del worktree, controllati uno per uno."""
    import yaml

    p = m.dati.RADICE_DEFAULT / "config" / "parametri.yaml"
    y = yaml.safe_load(p.read_text(encoding="utf-8"))
    r = y["regole_esame"]
    cv = r["criterio_vault"]
    out = {
        "file": str(p), "sha256": sha256_file(p), "stato": y.get("stato"),
        "simulazioni_caso": int(r["simulazioni_caso"]),
        "simulazioni_baseline_casuale": int(r["simulazioni_baseline_casuale"]),
        "semi_baseline_casuale": dict(r["semi_baseline_casuale"]),
        "bootstrap": dict(r["bootstrap"]),
        "profit_factor_minimo": float(cv["profit_factor_minimo"]),
        "trade_minimi_vault": int(cv["trade_minimi"]),
        "trade_minimi_vault_sezione_8": int(r["trade_minimi"]["vault"]),
        "rendimento_totale_positivo": bool(cv["rendimento_totale_positivo"]),
        "percentile_caso": int(cv["r_medio_sopra_percentile_caso"]),
    }
    attesi = {"simulazioni_caso": 1000, "simulazioni_baseline_casuale": 200, "profit_factor_minimo": 1.10,
              "trade_minimi_vault": 30, "trade_minimi_vault_sezione_8": 30, "rendimento_totale_positivo": True,
              "percentile_caso": 90}
    diversi = [f"{k}: {out[k]!r} (atteso {v!r})" for k, v in attesi.items() if out[k] != v]
    C = m.comune
    if (C.N_SIM, C.BOOT_N, C.BOOT_SEME) != (out["simulazioni_baseline_casuale"], out["bootstrap"]["ricampionamenti"],
                                             out["bootstrap"]["seme"]):
        diversi.append(f"comune.N_SIM/BOOT_N/BOOT_SEME = {(C.N_SIM, C.BOOT_N, C.BOOT_SEME)} diversi da parametri.yaml")
    if out["semi_baseline_casuale"] != {"primo": 0, "ultimo": 199}:
        diversi.append(f"semi_baseline_casuale {out['semi_baseline_casuale']}")
    if diversi:
        raise SystemExit("STOP: parametri.yaml del worktree non ha i valori attesi: " + "; ".join(diversi))
    return out


# ---------------------------------------------------------------------------
# Dati
# ---------------------------------------------------------------------------


def impronte_attese(m) -> dict:
    p = m.worktree / FILE_IMPRONTE
    if sha256_file(p) != FILE_ATTESI[FILE_IMPRONTE]:
        raise SystemExit(f"STOP: {p} non e' quello scritto in fase0_dati.md")
    tutte = json.loads(p.read_text(encoding="utf-8"))
    return {s: {k: v for k, v in tutte[s].items() if k.startswith(pref)} for s, pref in PREFISSI_IMPRONTE.items()}


def prepara_insample(m, scarica: bool) -> dict:
    """Riscarica (se manca) e verifica con le impronte della campagna; si ferma a una differenza."""
    t0 = time.time()
    scaricati = {}
    if scarica:
        for s, tipo, tf in SERIE:
            percorsi = m.dati.scarica_periodo(s, tipo, tf, INIZIO_IN_SAMPLE, FINE_IN_SAMPLE)
            scaricati[f"{s}/{tipo}/{tf or ''}".rstrip("/")] = len(percorsi)
    attese = impronte_attese(m)
    differenze = {}
    for s, voci in attese.items():
        differenze[s] = m.dati.verifica_impronte(s, m.dati.RADICE_DEFAULT, voci)
    esito = {"file_per_serie_su_disco": scaricati, "impronte_confrontate": {s: len(v) for s, v in attese.items()},
             "differenze": differenze, "checksum_remoti_mancanti": list(m.dati.CHECKSUM_MANCANTI),
             "secondi": round(time.time() - t0, 1)}
    esito["uguali"] = not any(differenze.values())
    return esito


def controlla_fase0(m) -> dict:
    """I conteggi a 15m di fase0_dati.md, rifatti sui file appena verificati."""
    d = m.dati
    s = d.carica_serie_allineate(SIMBOLO, "15m", INIZIO_IN_SAMPLE, FINE_IN_SAMPLE)
    fund = d.carica_funding(SIMBOLO, INIZIO_IN_SAMPLE, FINE_IN_SAMPLE)
    btc = d.carica_candele("BTCUSDT", "15m", INIZIO_IN_SAMPLE, FINE_IN_SAMPLE)
    trovati = {"barre_tenute": len(s["candele"]), "tolte_last": s["n_tolte_last"], "tolte_mark": s["n_tolte_mark"],
               "volume_mancante": s["n_volume_mancante"], "settlement_funding": len(fund), "barre_btc": len(btc)}
    giorni_tolti_last = sorted({datetime.fromtimestamp(t / 1000, tz=timezone.utc).strftime("%Y-%m-%d")
                                for t in s["tolte_last"]})
    return {"attesi": ATTESI_FASE0, "trovati": trovati,
            "differenze": [f"{k}: atteso {v}, trovato {trovati[k]}" for k, v in ATTESI_FASE0.items() if trovati[k] != v],
            "giorni_tolti_dal_last": giorni_tolti_last,
            "prima_barra": datetime.fromtimestamp(s["candele"][0].ts / 1000, tz=timezone.utc).isoformat()}


def sha256_dati_insample(m) -> dict:
    """SHA-256 dei 192 file in-sample delle quattro serie (gia' verificati con le impronte)."""
    d = m.dati
    out = {}
    for s, tipo, tf in SERIE:
        for anno, mese in d.mesi_del_periodo(INIZIO_IN_SAMPLE, FINE_IN_SAMPLE):
            p = d.percorso_mese(s, tipo, tf, anno, mese)
            rel = p.relative_to(d.RADICE_DEFAULT).as_posix()
            if not p.is_file():
                raise SystemExit(f"STOP: manca il file in-sample {rel}")
            out[rel] = sha256_file(p)
    return out


def stato_file(p: Path) -> str | None:
    """D1: ``None`` se il file mensile c'e' e si legge; altrimenti il motivo («manca» o l'errore).

    «Si legge» vuol dire: e' uno zip valido, contiene uno e un solo .csv, non vuoto, e i CRC di tutto
    lo zip tornano (``testzip`` decomprime ogni byte). Le righe non si interpretano: nessuna candela
    entra in memoria prima che D1 sia passato.
    """
    if not p.is_file():
        return "manca"
    try:
        with zipfile.ZipFile(p) as z:
            csv = [n for n in z.namelist() if n.lower().endswith(".csv")]
            if len(csv) != 1:
                return f"attesi un solo .csv nello zip, trovati {csv}"
            if z.getinfo(csv[0]).file_size == 0:
                return f"{csv[0]} e' vuoto"
            rotto = z.testzip()
            if rotto is not None:
                return f"CRC sbagliato in {rotto}"
    except Exception as e:  # zip rotto, file illeggibile...
        return f"non si legge ({type(e).__name__}: {e})"
    return None


def controlla_file_mensili(m, inizio: date, fine: date) -> dict:
    """D1, PRIMA di leggere qualunque candela: ogni file mensile delle serie usate (``SERIE``: ADA
    last, ADA mark, funding di ADA, BTC) fra il mese di ``inizio`` e quello di ``fine`` deve esserci
    e leggersi. Se ne manca o non se ne legge anche uno solo: ``FermoSenzaRisultato`` (nessun
    risultato, D4). Ritorna lo SHA-256 di ogni file controllato."""
    d = m.dati
    mesi = list(d.mesi_del_periodo(inizio, fine))
    file, mancanti, illeggibili = {}, [], []
    for s, tipo, tf in SERIE:
        for anno, mese in mesi:
            p = d.percorso_mese(s, tipo, tf, anno, mese)
            rel = p.relative_to(d.RADICE_DEFAULT).as_posix()
            motivo = stato_file(p)
            if motivo == "manca":
                mancanti.append(rel)
            elif motivo is not None:
                illeggibili.append({"file": rel, "motivo": motivo})
            else:
                file[rel] = sha256_file(p)
    esito = {"regola": "D1", "mesi": [f"{a:04d}-{me:02d}" for a, me in (mesi[0], mesi[-1])],
             "serie": [f"{s}/{tipo}/{tf or ''}".rstrip("/") for s, tipo, tf in SERIE],
             "file_attesi": len(SERIE) * len(mesi), "file_presenti_e_leggibili": len(file),
             "mancanti": mancanti, "illeggibili": illeggibili, "sha256": file}
    if mancanti or illeggibili:
        raise FermoSenzaRisultato(
            "D1", f"{len(mancanti)} file mensili mancanti e {len(illeggibili)} illeggibili su {esito['file_attesi']} "
                  f"({esito['mesi'][0]} -> {esito['mesi'][1]}): nessuna candela e' stata letta",
            {"mancanti": mancanti[:50], "illeggibili": illeggibili[:50]})
    return esito


def prepara_vault(m, scarica: bool, ap: dict) -> dict:
    """Solo a vault aperto, DOPO il marcatore: copia APERTURA.md nel worktree (R4), scarica i 132 file
    del vault (4 serie x 33 mesi) e applica D1 (presenti e leggibili). Qui nessuna candela si legge:
    uno STOP non scrive un risultato e lo stesso giro riparte dopo aver risolto (D4).
    """
    d = m.dati
    copia = copia_apertura(ap, m.worktree / APERTURA_REL_WORKTREE)
    d.controlla_vault(FINE_VAULT)  # di nuovo, con la copia al suo posto, prima di toccare la rete
    t0 = time.time()
    errori_scarico = []
    if scarica:
        for s, tipo, tf in SERIE:
            try:
                d.scarica_periodo(s, tipo, tf, INIZIO_VAULT, FINE_VAULT)
            except Exception as e:  # rete, CHECKSUM diverso...: i file che mancano li trova D1
                errori_scarico.append(f"{s}/{tipo}/{tf or ''}: {type(e).__name__}: {e}")
    try:
        d1 = controlla_file_mensili(m, INIZIO_VAULT, FINE_VAULT)
    except FermoSenzaRisultato as e:
        if errori_scarico:
            e.dettagli = dict(e.dettagli or {}, errori_dello_scarico=errori_scarico)
        raise
    return {"file": d1["file_presenti_e_leggibili"], "sha256": d1["sha256"], "sha256_elenco": sha256_json(d1["sha256"]),
            "D1": {k: v for k, v in d1.items() if k != "sha256"}, "errori_dello_scarico": errori_scarico,
            "apertura_copia": copia, "checksum_remoti_mancanti": list(d.CHECKSUM_MANCANTI),
            "secondi": round(time.time() - t0, 1)}


def _ore(x: float) -> str:
    return f"{x:g}"


def _pc(x, d: int = 1) -> str:
    return f"{100 * (x or 0):.{d}f}%".replace(".", ",")


def controllo_dati(m, inizio_ts: int, fine: date) -> dict:
    """D2 e D3, dopo il caricamento e PRIMA di eseguire il candidato: mese per mese, le barre della
    serie che usa il candidato e i settlement di funding del periodo che inizia a ``inizio_ts`` e
    finisce con il giorno ``fine``. Le serie si leggono con le funzioni del candidato, dal 2020-01-01
    come ``comune.carica`` (``sha256_ts_allineate`` permette di controllare che la serie del
    candidato sia proprio questa).

    Blocchi (D2: ``ok`` falso, il giro si ferma SENZA risultato):
      * l'ultima barra della serie allineata last/mark non e' quella delle 23:45 di ``fine``;
      * un mese con meno del 50% delle barre allineate attese;
      * un mese senza nessun settlement di funding;
      * per BTCUSDT, che ADAUSDT-037 usa nel segnale (``BTC_NEL_SEGNALE``), le stesse soglie: ultima
        barra e 50% delle barre attese per mese (se BTC servisse solo da contesto: solo avvisi).
    Tutto il resto si riporta (D3): per mese barre attese, last, mark, allineate e quota, BTC e
    quota, barre di ADA senza BTC, con un AVVISO sotto il 99%; settlement di funding con gli
    intervalli osservati (ore fra un settlement e il precedente) e quelli dichiarati dai file, con
    un AVVISO se fra due settlement passa piu' dell'intervallo dichiarato. Nessun numero di
    settlement «attesi» costruito sull'intervallo piu' corto.
    """
    d = m.dati
    s = d.carica_serie_allineate(SIMBOLO, TF, INIZIO_IN_SAMPLE, fine)
    dettaglio = d.carica_funding_dettaglio(SIMBOLO, INIZIO_IN_SAMPLE, fine)
    btc = d.carica_candele("BTCUSDT", TF, INIZIO_IN_SAMPLE, fine)
    fine_ts = d.ms_da_data(fine + timedelta(days=1))
    ultima_attesa = fine_ts - MS_15M
    candele = s["candele"]

    def nel(ts):
        return inizio_ts <= ts < fine_ts

    c_com = Counter(_mese(c.ts) for c in candele if nel(c.ts))
    c_tl = Counter(_mese(t) for t in s["tolte_last"] if nel(t))
    c_tm = Counter(_mese(t) for t in s["tolte_mark"] if nel(t))
    ts_btc = {c.ts for c in btc}
    c_btc = Counter(_mese(c.ts) for c in btc if nel(c.ts))
    c_senza_btc = Counter(_mese(c.ts) for c in candele if nel(c.ts) and c.ts not in ts_btc)
    c_fund = Counter(_mese(t) for t, _o, _r in dettaglio if nel(t))
    ore_dich: dict = {}
    for t, ore, _r in dettaglio:
        if nel(t):
            ore_dich.setdefault(_mese(t), set()).add(ore)
    # intervalli osservati: ore fra ogni settlement del periodo e il precedente (anche del mese prima)
    interv: dict = {}
    buchi_funding = []
    for (t0, o0, _r0), (t1, o1, _r1) in zip(dettaglio, dettaglio[1:]):
        if not nel(t1):
            continue
        ore = (t1 - t0) / MS_ORA
        interv.setdefault(_mese(t1), Counter())[_ore(ore)] += 1
        if ore > max(o0, o1) + 1 / 60:
            # il buco si conta nel mese del primo settlement che manca (dentro il periodo)
            primo_mancante = max(t0 + o0 * MS_ORA, inizio_ts)
            buchi_funding.append({"mese": _mese(primo_mancante), "settlement_prima": _iso(t0), "settlement_dopo": _iso(t1),
                                  "ore": round(ore, 3), "ore_dichiarate": sorted({o0, o1})})
    buchi_f_mese = Counter(b["mese"] for b in buchi_funding)
    mesi, blocchi, avvisi = [], [], []
    inizio_d = datetime.fromtimestamp(inizio_ts / 1000, tz=timezone.utc).date()
    for a, me in d.mesi_del_periodo(inizio_d, fine):
        k = f"{a:04d}-{me:02d}"
        da = max(inizio_ts, d.ms_da_data(date(a, me, 1)))
        a_ = min(fine_ts, d.ms_da_data(date(a + (me == 12), me % 12 + 1, 1)))
        attese = (a_ - da) // MS_15M
        quota = c_com[k] / attese if attese else None
        quota_btc = c_btc[k] / attese if attese else None
        riga = {"mese": k, "barre_attese": int(attese),
                "barre_last": c_com[k] + c_tl[k], "barre_mark": c_com[k] + c_tm[k],
                "barre_allineate": c_com[k], "tolte_dal_last": c_tl[k], "tolte_dal_mark": c_tm[k],
                "quota_allineate": round(quota, 4) if quota is not None else None,
                "barre_btc": c_btc[k], "quota_btc": round(quota_btc, 4) if quota_btc is not None else None,
                "barre_ada_senza_btc": c_senza_btc[k],
                "settlement_funding": c_fund[k], "ore_funding_dichiarate": sorted(ore_dich.get(k, ())),
                "intervalli_osservati_ore": dict(sorted((interv.get(k) or {}).items(), key=lambda x: float(x[0]))),
                "buchi_di_funding": buchi_f_mese[k], "avvisi": []}
        if not attese or c_com[k] < QUOTA_BARRE_BLOCCO * attese:
            blocchi.append(f"{k}: {c_com[k]} barre allineate last/mark su {attese} attese "
                           f"({_pc(quota)}, sotto il {_pc(QUOTA_BARRE_BLOCCO, 0)})")
        elif c_com[k] < QUOTA_BARRE_AVVISO * attese:
            riga["avvisi"].append(f"barre allineate al {_pc(quota)} (sotto il {_pc(QUOTA_BARRE_AVVISO, 0)}: "
                                  f"{c_tl[k]} tolte dal last perche' manca il mark, {c_tm[k]} tolte dal mark perche' "
                                  f"manca il last)")
        if not attese or c_btc[k] < QUOTA_BARRE_BLOCCO * attese:
            testo = (f"{k}: {c_btc[k]} barre di BTCUSDT su {attese} attese ({_pc(quota_btc)}, sotto il "
                     f"{_pc(QUOTA_BARRE_BLOCCO, 0)})")
            if BTC_NEL_SEGNALE:
                blocchi.append(testo + " (BTC e' nel segnale del candidato)")
            else:  # pragma: no cover  (non e' il caso di ADAUSDT-037)
                riga["avvisi"].append(testo)
        elif c_btc[k] < QUOTA_BARRE_AVVISO * attese:
            riga["avvisi"].append(f"barre di BTCUSDT al {_pc(quota_btc)} (sotto il {_pc(QUOTA_BARRE_AVVISO, 0)})")
        if c_senza_btc[k]:
            riga["avvisi"].append(f"{c_senza_btc[k]} barre di ADA senza la barra di BTC (segnale non calcolabile li' e "
                                  f"96 posizioni dopo)")
        if c_fund[k] == 0:
            blocchi.append(f"{k}: nessun settlement di funding")
        elif buchi_f_mese[k]:
            riga["avvisi"].append(f"{buchi_f_mese[k]} volte fra due settlement passa piu' dell'intervallo dichiarato")
        mesi.append(riga)
        avvisi += [f"{k}: {x}" for x in riga["avvisi"]]
    ultima = candele[-1].ts if candele else None
    if ultima != ultima_attesa:
        blocchi.append(f"la serie allineata last/mark finisce a {_iso(ultima) or 'nessuna barra'}, non all'ultima barra "
                       f"attesa {_iso(ultima_attesa)}")
    ultima_btc = btc[-1].ts if btc else None
    if ultima_btc != ultima_attesa:
        testo = f"BTCUSDT finisce a {_iso(ultima_btc) or 'nessuna barra'}, non all'ultima barra attesa {_iso(ultima_attesa)}"
        if BTC_NEL_SEGNALE:
            blocchi.append(testo + " (BTC e' nel segnale del candidato)")
        else:  # pragma: no cover
            avvisi.append(testo)
    buchi = []
    for p_, q_ in zip(candele, candele[1:]):
        if q_.ts >= inizio_ts and q_.ts - p_.ts != MS_15M:
            buchi.append({"ultima_barra_prima": _iso(p_.ts), "prima_barra_dopo": _iso(q_.ts),
                          "barre_mancanti": (q_.ts - p_.ts) // MS_15M - 1})
    giorni_con_barre_tolte = sorted({datetime.fromtimestamp(t / 1000, tz=timezone.utc).strftime("%Y-%m-%d")
                                     for t in list(s["tolte_last"]) + list(s["tolte_mark"]) if nel(t)})
    interv_tot = Counter()
    for c in interv.values():
        interv_tot.update(c)
    return {
        "ok": not blocchi, "blocchi": blocchi, "avvisi": avvisi,
        "regola": {"D2_blocco_barre_per_mese_sotto": QUOTA_BARRE_BLOCCO, "D3_avviso_barre_per_mese_sotto": QUOTA_BARRE_AVVISO,
                   "D2_blocco_mese_senza_settlement": True, "D2_blocco_ultima_barra": _iso(ultima_attesa),
                   "btc_nel_segnale": BTC_NEL_SEGNALE, "timeframe": TF},
        "periodo": {"da": _iso(inizio_ts), "fine": fine.isoformat()},
        "ultima_barra_allineata": _iso(ultima), "ultima_barra_attesa": _iso(ultima_attesa),
        "ultima_barra_btc": _iso(ultima_btc),
        "mesi_sotto_il_99": [r["mese"] for r in mesi if (r["quota_allineate"] or 0) < QUOTA_BARRE_AVVISO],
        "barre_attese_nel_periodo": sum(r["barre_attese"] for r in mesi),
        "barre_allineate_nel_periodo": sum(r["barre_allineate"] for r in mesi),
        "tolte_dal_last_nel_periodo": sum(r["tolte_dal_last"] for r in mesi),
        "tolte_dal_mark_nel_periodo": sum(r["tolte_dal_mark"] for r in mesi),
        "barre_btc_nel_periodo": sum(r["barre_btc"] for r in mesi),
        "barre_ada_senza_btc_nel_periodo": sum(r["barre_ada_senza_btc"] for r in mesi),
        "volume_mancante_nel_periodo": sum(1 for c in candele if nel(c.ts) and s["volume_usdt"].get(c.ts) is None),
        "settlement_nel_periodo": sum(r["settlement_funding"] for r in mesi),
        "intervalli_di_funding_osservati_ore": dict(sorted(interv_tot.items(), key=lambda x: float(x[0]))),
        "buchi_di_funding": buchi_funding[:100], "n_buchi_di_funding": len(buchi_funding),
        "buchi_nel_periodo": len(buchi), "barre_mancanti_nei_buchi": sum(b["barre_mancanti"] for b in buchi),
        "elenco_buchi": buchi[:100], "giorni_con_barre_tolte": giorni_con_barre_tolte,
        "barre_serie_dal_2020": len(candele),
        "sha256_ts_allineate": sha256_testo(",".join(str(c.ts) for c in candele)),
        "mesi": mesi,
    }


# ---------------------------------------------------------------------------
# Le entrate casuali del tasso del caso (gemella di motore.simula_baseline_casuale)
# ---------------------------------------------------------------------------

_LAVORO_CASO: dict = {}
_FD_LUCCHETTO = None  # descrittore del lucchetto del giro in corso (si chiude nei figli)


def metriche_simulazione(m, ris, par) -> dict:
    """Le metriche del criterio (e del rapporto) per una strategia a entrate casuali.

    L'R medio e' calcolato con la stessa espressione di simula_baseline_casuale (somma / numero),
    il rendimento totale come valuta della campagna (somma dei pnl / 1000: composto, perche' la
    dimensione segue il capitale), profit factor e drawdown da motore.calcola_metriche.
    """
    tr = ris.trades
    n = len(tr)
    out = {"n_trade": n, "segnali_non_validi": ris.n_segnali_non_validi,
           "segnali_senza_barra": ris.n_segnali_senza_barra}
    if n == 0:
        out.update(r_medio=None, profit_factor=0.0, rendimento_totale=0.0, drawdown_max=0.0, win_rate=0.0,
                   r_medio_per_anno={}, esiti={}, trade_ridotti=0)
        return out
    met = m.motore.calcola_metriche(ris)
    out.update(r_medio=sum(t.r for t in tr) / n, profit_factor=met["profit_factor"],
               rendimento_totale=float(sum(t.pnl for t in tr) / par.capitale_iniziale),
               drawdown_max=met["drawdown_max"], win_rate=met["win_rate"],
               r_medio_per_anno=m.comune._r_per_anno(tr), esiti=met["esiti"], trade_ridotti=met["n_ridotti"])
    return out


def simula_semi(L: dict, semi) -> dict:
    """Le strategie casuali di questi semi: stessi passi di motore.simula_baseline_casuale."""
    m = L["m"]
    candele = L["candele"]
    n = len(candele)
    # come simula_baseline_casuale: un segnale alla chiusura dell'ultima barra non ha dove entrare
    vietate = list(L["vietate"]) + [(n - 1, n)]
    t0 = time.perf_counter()
    tutti = m.statistica.entrate_casuali_per_semi(n, L["n_trade"], L["durata"], list(semi), vietate)
    t_tab = time.perf_counter() - t0
    out = []
    for seme, ingressi_lista in zip(semi, tutti):
        t1 = time.perf_counter()
        ingressi = frozenset(ingressi_lista)
        strategia = m.motore._strategia_nuova(L["crea"], "gemella", "crea_casuale(ingressi)", ingressi)
        ris = m.motore.esegui(candele, None, L["mark"], list(L["funding"]), strategia, L["param"])
        d = metriche_simulazione(m, ris, L["param"])
        d["seme"] = int(seme)
        d["ingressi_sha256"] = sha256_testo(json.dumps(sorted(ingressi_lista)))[:16]
        d["secondi"] = round(time.perf_counter() - t1, 4)
        out.append(d)
    return {"semi": [int(s) for s in semi], "simulazioni": out, "secondi_tabella": round(t_tab, 3)}


def _pezzo_caso(semi):
    return simula_semi(_LAVORO_CASO, semi)


def prepara_lavoro(m, D, F, n_trade: int, durata: int, vietate) -> dict:
    return {"m": m, "candele": D["candele"], "mark": D["mark"], "funding": D["funding"], "crea": F.crea_casuale,
            "n_trade": n_trade, "durata": durata, "vietate": vietate, "param": m.comune.PARAM}


def _figlio_senza_lucchetto() -> None:
    """Nei processi figli: chiude la copia del descrittore del lucchetto ereditata dal fork, cosi' il
    lucchetto (fcntl) dura quanto il processo principale e non quanto un figlio rimasto indietro."""
    if _FD_LUCCHETTO is not None:
        try:
            os.close(_FD_LUCCHETTO)
        except OSError:
            pass


def simula_in_parallelo(L: dict, pezzi, processi: int, ogni_pezzo=None) -> list:
    """Esegue i pezzi (tuple di semi) in processi fork; ``ogni_pezzo`` riceve ogni esito appena arriva."""
    global _LAVORO_CASO
    _LAVORO_CASO = L
    esiti = []
    if not pezzi:
        return esiti
    ctx = mp.get_context("fork")
    with ctx.Pool(min(processi, len(pezzi)), initializer=_figlio_senza_lucchetto) as pool:
        for r in pool.imap_unordered(_pezzo_caso, pezzi):
            esiti.append(r)
            if ogni_pezzo is not None:
                ogni_pezzo(r)
    return esiti


# ---------------------------------------------------------------------------
# Modo parita
# ---------------------------------------------------------------------------


def _voci_log(p: Path) -> list:
    return [json.loads(r) for r in p.read_text(encoding="utf-8").splitlines() if r.strip()]


def _senza_data(v: dict) -> dict:
    return {k: x for k, x in v.items() if k != "data"}


def cmd_parita(args) -> int:
    t_inizio = time.time()
    uscita = Path(args.uscita).resolve()
    lavoro = uscita.parent / f"parita_{SIMBOLO}_lavoro"
    lavoro.mkdir(parents=True, exist_ok=True)
    m = carica_moduli(Path(args.worktree))
    esito: dict = {"candidato": CANDIDATO, "modo": "parita", "data": adesso(), "worktree": str(m.worktree),
                   "python": platform.python_version(), "versioni": versioni(), "sha256_lanciatore": sha256_lanciatore(),
                   "problemi": []}
    esito["codice"] = controlla_codice(m.worktree)
    esito["regole_esame"] = leggi_regole_esame(m)
    log_campagna = m.worktree / FILE_LOG
    sha_log_prima = sha256_file(log_campagna)

    # 1) dati in-sample: riscarico e impronte (STOP a una differenza)
    esito["dati_insample"] = prepara_insample(m, scarica=not args.senza_scarico)
    if not esito["dati_insample"]["uguali"]:
        esito["problemi"].append("impronte in-sample diverse da quelle della campagna: STOP")
        scrivi_json(uscita, esito)
        print(json.dumps(pulito(esito["dati_insample"]), ensure_ascii=False, indent=1))
        raise SystemExit("STOP: le impronte dei dati riscaricati non sono quelle della campagna")
    esito["fase0"] = controlla_fase0(m)
    esito["problemi"] += [f"fase0: {x}" for x in esito["fase0"]["differenze"]]

    # 2) log di lavoro: quello della campagna senza le due voci da rifare (il file vero non si tocca)
    voci = _voci_log(log_campagna)
    originali = {(v["id"], v["tipo"]): v for v in voci}
    da_rifare = [(CANDIDATO, "risultato"), (ID_VAL, "risultato")]
    log_lavoro = lavoro / "log_di_lavoro.jsonl"
    righe = [r for r in log_campagna.read_text(encoding="utf-8").splitlines()
             if r.strip() and (json.loads(r)["id"], json.loads(r)["tipo"]) not in da_rifare]
    log_lavoro.write_text("\n".join(righe) + "\n", encoding="utf-8")
    m.registro.LOG = log_lavoro
    m.run.USCITA = lavoro
    if Path(m.registro.LOG).resolve() == log_campagna.resolve():
        raise SystemExit("STOP: il log di lavoro coincide con quello della campagna")

    tempi = {}
    rifatte = {}
    # 3) costruzione, con run.testa della campagna (scrive solo nel log di lavoro)
    if not args.senza_costruzione:
        t = time.time()
        m.run.testa(CANDIDATO)
        tempi["costruzione_valuta"] = round(time.time() - t, 1)
        rifatte[CANDIDATO] = [v for v in _voci_log(log_lavoro) if v["id"] == CANDIDATO and v["tipo"] == "risultato"][-1]
    # 4) validazione: lo script della campagna cosi' com'e'
    t = time.time()
    g = runpy.run_path(str(m.codice / "validazione.py"), run_name="validazione_della_campagna")
    tempi["validazione_valuta"] = round(time.time() - t, 1)
    rifatte[ID_VAL] = [v for v in _voci_log(log_lavoro) if v["id"] == ID_VAL and v["tipo"] == "risultato"][-1]

    confronti = {}
    for ident, nuova in rifatte.items():
        vecchia = originali[(ident, "risultato")]
        confronti[ident] = {"campi_confrontati": len(vecchia) - 1,
                            "differenze_esatte": confronta(_senza_data(vecchia), _senza_data(nuova)),
                            "differenze_oltre_1e-12_relativo": confronta(_senza_data(vecchia), _senza_data(nuova),
                                                                         tolleranza_rel=1e-12),
                            "data_della_voce_originale": vecchia["data"]}
    esito["confronto_con_il_log"] = confronti

    # 5) i numeri della consegna, uno per uno, con i decimali con cui sono scritti
    tabella = []
    for nome, periodo, scritto, decimali, leggi in CONSEGNA:
        voce = rifatte.get(CANDIDATO if periodo == "costruzione" else ID_VAL)
        if voce is None:
            continue
        rifatto = leggi(voce)
        if decimali is None:
            uguale = rifatto == scritto
            arrotondato = rifatto
        else:
            arrotondato = round(float(rifatto), decimali)
            uguale = abs(arrotondato - float(scritto)) < 0.5 * 10 ** (-decimali) + 1e-12
        tabella.append({"periodo": periodo, "numero": nome, "consegna": scritto, "rifatto": rifatto,
                        "rifatto_arrotondato": arrotondato, "uguale": bool(uguale)})
    esito["consegna"] = {"numeri": tabella, "diversi": [r for r in tabella if not r["uguale"]]}

    # 6) la gemella delle entrate casuali contro la (b) della campagna (simula_baseline_casuale), semi 0..199
    v = g["v"]
    C = m.comune
    var = m.varianti.VARIANTI[CANDIDATO]
    D = C.carica(var.tf, "validazione")
    F = C.Fabbriche(var, D, solo_dopo_ts=C.FINE_COSTRUZIONE_TS)
    trades = v["_trades"]
    durata = m.motore.durata_media_barre(trades, D["passo"])
    vietate, quota = F.barre_vietate(C.PARAM)
    L = prepara_lavoro(m, D, F, len(trades), durata, vietate)
    # tempo di una simulazione, in un solo processo (5 semi, tabella compresa a parte)
    t = time.perf_counter()
    sequenziale = simula_semi(L, range(5))
    tempi["sequenziale_5_semi_secondi"] = round(time.perf_counter() - t, 2)
    tempi["secondi_tabella_entrate_validazione"] = sequenziale["secondi_tabella"]
    tempi["secondi_per_simulazione_validazione"] = round(
        sum(s["secondi"] for s in sequenziale["simulazioni"]) / len(sequenziale["simulazioni"]), 4)
    pezzo = 50
    pezzi = [tuple(range(k, min(k + pezzo, 200))) for k in range(0, 200, pezzo)]
    t = time.time()
    ris_g = simula_in_parallelo(L, pezzi, args.processi)
    tempi["gemella_200_semi_in_parallelo"] = round(time.time() - t, 1)
    sims = sorted((s for r in ris_g for s in r["simulazioni"]), key=lambda s: s["seme"])
    r_gemella = [s["r_medio"] for s in sims if s["n_trade"] > 0]
    r_b = [float(x) for x in v["_valori_b"]]
    differenti = [i for i, (a, b) in enumerate(zip(r_gemella, r_b)) if a != b]
    base_g = m.statistica.baseline_casuale(r_gemella)
    esito["gemella"] = {
        "semi": [0, 199], "funzione_della_campagna": "motore.simula_baseline_casuale (via comune.baseline_b)",
        "n_r_medi_gemella": len(r_gemella), "n_r_medi_campagna": len(r_b),
        "r_medi_identici": bool(len(r_gemella) == len(r_b) and not differenti),
        "posizioni_diverse": differenti[:20],
        "differenza_massima": max((abs(a - b) for a, b in zip(r_gemella, r_b)), default=None),
        "trade_per_simulazione_medio_gemella": sum(s["n_trade"] for s in sims if s["n_trade"]) / max(1, len(r_gemella)),
        "trade_per_simulazione_medio_campagna": v["baseline_b"]["trade_per_simulazione_medio"],
        "media_gemella": base_g["media"], "media_campagna": v["baseline_b"]["media"],
        "percentile_90_gemella": base_g["percentile_90"], "percentile_90_campagna": v["baseline_b"]["percentile_90"],
        "durata_media_barre": durata, "durata_media_barre_campagna": v["baseline_b"]["durata_media_barre"],
        "quota_barre_vietate": quota, "quota_barre_vietate_campagna": v["baseline_b"]["quota_barre_vietate"],
        "segnali_scartati_gemella": sum(s["segnali_non_validi"] for s in sims),
    }
    if not esito["gemella"]["r_medi_identici"]:
        esito["problemi"].append("la gemella NON da' gli stessi R medi della (b) della campagna")

    # 7) stima del tempo del vault (lineare nel numero di barre: esegui scorre tutta la serie dal 2020)
    barre_val = len(D["candele"])
    giorni_vault = (FINE_VAULT - INIZIO_VAULT).days + 1
    barre_vault = barre_val + giorni_vault * 96  # stima: nessun buco nel vault
    fattore = barre_vault / barre_val
    s_sim = tempi["secondi_per_simulazione_validazione"]
    n_sim_vault = esito["regole_esame"]["simulazioni_caso"] + esito["regole_esame"]["simulazioni_baseline_casuale"]
    par_sec = n_sim_vault * s_sim * fattore / args.processi
    # il tempo per simulazione MISURATO con i processi in parallelo (la gemella dei 200 semi)
    s_sim_par = tempi["gemella_200_semi_in_parallelo"] * min(args.processi, len(pezzi)) / 200
    tempi["stima_vault"] = {
        "barre_serie_validazione": barre_val, "barre_serie_vault_stimate": barre_vault,
        "fattore_barre": round(fattore, 3), "simulazioni": n_sim_vault,
        "secondi_per_simulazione_stimati": round(s_sim * fattore, 3),
        "minuti_simulazioni_con_processi": round(par_sec / 60, 1), "processi": args.processi,
        "secondi_per_simulazione_in_parallelo_misurati": round(s_sim_par, 4),
        "minuti_simulazioni_con_processi_dal_tempo_in_parallelo": round(
            n_sim_vault * s_sim_par * fattore / min(args.processi, len(pezzi)) / 60, 1),
        "nota": "stima: tempo per simulazione misurato in un solo processo sulla validazione, scalato per le barre; "
                "con i processi in parallelo sulla stessa macchina ogni simulazione rallenta un po'. In piu': "
                "scarico dei 132 file del vault, candidato, (a), barre vietate, preparazione degli indicatori e "
                "tabelle delle entrate (pochi secondi ciascuno, misurati nella prova-vault).",
    }
    tempi["totale_parita"] = round(time.time() - t_inizio, 1)
    esito["tempi_secondi"] = tempi

    # 8) niente e' stato scritto nel worktree
    esito["log_campagna_intatto"] = sha256_file(log_campagna) == sha_log_prima
    esito["file_tracciati_modificati_dopo"] = _git(m.worktree, "status", "--porcelain", "--untracked-files=no").splitlines()
    if not esito["log_campagna_intatto"] or esito["file_tracciati_modificati_dopo"]:
        esito["problemi"].append("il worktree della campagna e' cambiato durante la parita'")
    esatta = all(not c["differenze_esatte"] for c in confronti.values())
    esito["parita_esatta"] = bool(esatta and not esito["consegna"]["diversi"] and esito["gemella"]["r_medi_identici"]
                                  and esito["dati_insample"]["uguali"] and not esito["fase0"]["differenze"])
    esito["parita_a_meno_della_virgola_mobile"] = bool(
        all(not c["differenze_oltre_1e-12_relativo"] for c in confronti.values())
        and not esito["consegna"]["diversi"] and esito["gemella"]["r_medi_identici"])
    scrivi_json(uscita, esito)
    print(json.dumps(pulito({"parita_esatta": esito["parita_esatta"],
                             "parita_a_meno_della_virgola_mobile": esito["parita_a_meno_della_virgola_mobile"],
                             "differenze": {k: c["differenze_esatte"] for k, c in confronti.items()},
                             "consegna_diversi": esito["consegna"]["diversi"],
                             "gemella": {k: esito["gemella"][k] for k in ("r_medi_identici", "differenza_massima")},
                             "impronte_uguali": esito["dati_insample"]["uguali"], "fase0": esito["fase0"]["differenze"],
                             "problemi": esito["problemi"], "tempi": tempi, "uscita": str(uscita)}),
                     ensure_ascii=False, indent=1))
    return 0 if esito["parita_esatta"] else 1


# ---------------------------------------------------------------------------
# APERTURA.md (R4)
# ---------------------------------------------------------------------------

# I semi del tasso del caso scritti in APERTURA.md: «0-999», «0–999», «0..999», «da 0 a 999»
RE_SEMI = re.compile(r"(?<![\w.,])0\s*(?:-|–|—|‒|\.\.\.?|…|\s(?:a|fino a|to)\s)\s*999(?!\d)")
# l'ID scritto come tale: non vale quello dentro un percorso (candidati/ADAUSDT-037/regole.md)
RE_ID = re.compile(rf"(?<![A-Za-z0-9/_.]){re.escape(CANDIDATO)}(?![0-9/_])")


def requisiti_apertura() -> dict:
    """Cosa deve contenere APERTURA.md per questo candidato (R4)."""
    return {"id": CANDIDATO,
            "sha256": {rel: FILE_ATTESI[rel] for rel in FILE_PER_APERTURA},
            "semi": f"{SEMI_CASO[0]}-{SEMI_CASO[1]}",
            "dove": str(APERTURA_COORD),
            "copia_nel_worktree": str(WORKTREE_DEFAULT / APERTURA_REL_WORKTREE),
            "nota": "lo SHA-256 va scritto per intero (64 cifre esadecimali), uno per file; i due __init__.py sono "
                    "file vuoti e hanno lo SHA-256 del file vuoto. validazione.py serve alla parita' ma si "
                    "controlla contro il worktree, quindi va elencato anche lui."}


def leggi_apertura(m, sorgente: Path) -> dict:
    """R4, prima di tutto il resto del modo vault. Finche' ``sorgente`` manca (o e' vuota) solleva
    ``VaultChiuso`` senza scrivere nulla. Pretende l'ID del candidato, lo SHA-256 completo di
    regole.md e di ogni file di codice controllato contro il worktree, e i semi 0-999: se ne
    manca uno, STOP senza scrivere nulla."""
    try:
        grezzo = sorgente.read_bytes()
    except (FileNotFoundError, IsADirectoryError, NotADirectoryError):
        raise m.dati.VaultChiuso(f"manca {sorgente}: il vault e' chiuso") from None
    testo = grezzo.decode("utf-8", errors="replace")
    if not testo.strip():
        raise m.dati.VaultChiuso(f"{sorgente} e' vuoto: non e' un'apertura")
    basso = testo.lower()
    mancano = []
    id_trovato = RE_ID.search(testo) is not None
    if not id_trovato:
        mancano.append(f"l'ID del candidato {CANDIDATO}")
    hash_trovati = {}
    for rel, h in requisiti_apertura()["sha256"].items():
        hash_trovati[rel] = re.search(rf"(?<![0-9a-f]){h}(?![0-9a-f])", basso) is not None
        if not hash_trovati[rel]:
            mancano.append(f"lo SHA-256 completo di {rel} ({h})")
    semi = RE_SEMI.search(testo)
    if semi is None:
        mancano.append(f"i semi {SEMI_CASO[0]}-{SEMI_CASO[1]} delle entrate casuali del tasso del caso")
    if mancano:
        raise SystemExit(f"STOP (R4): {sorgente} non contiene:\n  " + "\n  ".join(mancano))
    altri = {rel: (h in basso) for rel, h in FILE_ATTESI.items() if h and rel not in FILE_PER_APERTURA}
    return {"sorgente": str(sorgente), "grezzo": grezzo, "sha256": hashlib.sha256(grezzo).hexdigest(),
            "byte": len(grezzo), "id_trovato": id_trovato, "hash_trovati": hash_trovati,
            "semi_trovati": semi.group(0), "altri_hash_presenti_non_richiesti": altri}


def copia_apertura(ap: dict, copia: Path) -> dict:
    """R4: copia APERTURA.md accanto al ``dati.py`` del candidato, se non c'e'; poi verifica che la
    copia sia uguale byte per byte. Una copia gia' presente e diversa ferma tutto."""
    grezzo = ap["grezzo"]
    if copia.exists() or copia.is_symlink():
        if copia.is_symlink() or not copia.is_file() or copia.read_bytes() != grezzo:
            raise SystemExit(f"STOP (R4): {copia} esiste ma non e' uguale byte per byte a {ap['sorgente']}")
        stato = "gia' presente"
    else:
        copia.parent.mkdir(parents=True, exist_ok=True)
        tmp = copia.with_name(copia.name + f".parziale{os.getpid()}")
        tmp.write_bytes(grezzo)
        os.replace(tmp, copia)
        stato = "copiata dal lanciatore"
    if copia.is_symlink() or copia.read_bytes() != grezzo:
        raise SystemExit(f"STOP (R4): la copia {copia} non e' uguale byte per byte a {ap['sorgente']}")
    return {"copia": str(copia), "sha256_copia": sha256_file(copia), "stato": stato + ", uguale byte per byte (verificato)"}


# ---------------------------------------------------------------------------
# Guardia «una volta sola», marcatore e avanzamento (R2, R3)
# ---------------------------------------------------------------------------


def posti_vault(m) -> SimpleNamespace:
    return SimpleNamespace(risultato=RISULTATO_VAULT, riassunto=RIASSUNTO_VAULT, marcatore=MARCATORE_VAULT,
                           avanzamento=AVANZAMENTO_VAULT, segno=m.worktree / SEGNO_REL_WORKTREE)


def posti_prova(cartella: Path, etichetta: str) -> SimpleNamespace:
    return SimpleNamespace(risultato=cartella / f"{CANDIDATO}_{etichetta}.json",
                           riassunto=cartella / f"{CANDIDATO}_{etichetta}.md",
                           marcatore=cartella / f"{CANDIDATO}_{etichetta}_giro_iniziato.json",
                           avanzamento=cartella / "avanzamento" / CANDIDATO, segno=None)


def rifiuta_se_fatto(posti) -> None:
    """R2: se il risultato (o il suo riassunto, un suo doppione, il segno) esiste, il giro non riparte."""
    for p in (posti.risultato, posti.riassunto, posti.segno):
        if p is not None and (p.exists() or p.is_symlink()):
            raise SystemExit(f"RIFIUTO (R2): {p} esiste gia': il giro si fa una volta sola")
    doppioni = sorted(posti.risultato.parent.glob(f"{posti.risultato.stem}_doppione_*.json"))
    if doppioni:
        raise SystemExit(f"RIFIUTO (R2): {doppioni[0]} esiste gia': il giro si fa una volta sola")


def controlla_marcatore(posti, sha_avvio: str) -> dict:
    """R2: un marcatore esistente ferma tutto, salvo la ripresa dello STESSO giro (stessa impronta
    d'avvio: lanciatore, codice, APERTURA.md, regole, semi, dati in-sample, versioni) non ancora
    finito. Vale anche dopo un fermo sui dati (D4): si riparte con lo stesso lanciatore."""
    p = posti.marcatore
    if not (p.exists() or p.is_symlink()):
        return {"ripresa": False}
    try:
        mk = json.loads(p.read_text(encoding="utf-8"))
        if not isinstance(mk, dict):
            raise ValueError("non e' un oggetto JSON")
    except Exception as e:
        raise SystemExit(f"RIFIUTO (R2): {p} esiste ma non si legge ({type(e).__name__}: {e}): decide il proprietario")
    if mk.get("stato") == "finito":
        raise SystemExit(f"RIFIUTO (R2): {p} dice che il giro e' finito (risultato {mk.get('risultato')})")
    if mk.get("impronta_avvio_sha256") != sha_avvio:
        nota = ("il candidato non e' mai stato eseguito in quel giro, quindi il vault non e' consumato (D4)"
                if not mk.get("candidato_eseguito") else "in quel giro il candidato e' gia' stato eseguito")
        raise SystemExit(f"RIFIUTO (R2): {p} esiste ed e' di un giro diverso (impronta d'avvio "
                         f"{mk.get('impronta_avvio_sha256')}, questa {sha_avvio}). Si riprende solo lo stesso giro: "
                         f"stesso lanciatore, codice, APERTURA.md, regole, semi, dati in-sample e versioni di python, "
                         f"numpy e scipy. Stato del marcatore: {mk.get('stato')!r}; {nota}. Decide il proprietario.")
    return {"ripresa": True, "marcatore_precedente": mk}


def crea_marcatore(p: Path, contenuto: dict) -> bool:
    """R2, D5: crea il marcatore in modo esclusivo (O_EXCL): se c'e' gia', False e nulla si scrive."""
    p.parent.mkdir(parents=True, exist_ok=True)
    testo = json.dumps(pulito(contenuto), ensure_ascii=False, indent=1) + "\n"
    try:
        fd = os.open(p, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
    except FileExistsError:
        return False
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        f.write(testo)
        f.flush()
        os.fsync(f.fileno())
    return True


def leggi_marcatore(p: Path) -> dict:
    try:
        mk = json.loads(p.read_text(encoding="utf-8"))
    except Exception as e:
        raise SystemExit(f"RIFIUTO (R2): il marcatore {p} non si legge piu' durante il giro ({type(e).__name__}: {e})")
    if not isinstance(mk, dict):
        raise SystemExit(f"RIFIUTO (R2): il marcatore {p} non e' un oggetto JSON")
    return mk


def aggiorna_marcatore(p: Path, stato: str, *, motivo=None, dettagli=None, **campi) -> None:
    """Cambia lo stato del marcatore. In cima ``stato``, ``motivo`` e ``dettagli`` sono SEMPRE quelli
    dell'ultimo passo (D5): a ogni cambio si riscrivono e, senza motivo, si azzerano (``null``), cosi'
    un giro finito non porta in cima il motivo di un fermo o di un'interruzione di prima. Ogni passo
    resta, col suo motivo, nella lista ``storia``."""
    mk = leggi_marcatore(p)
    mk.update(pulito(campi))
    mk["stato"] = stato
    mk["motivo"] = motivo
    mk["dettagli"] = pulito(dettagli)
    voce = {"data": adesso(), "stato": stato}
    if motivo:
        voce["motivo"] = motivo
    mk.setdefault("storia", []).append(voce)
    mk["aggiornato"] = adesso()
    scrivi_json(p, mk)


def segna_candidato_eseguito(p: Path) -> None:
    """D4: scritto nel marcatore PRIMA di eseguire il candidato. Da qui i file di dati restano
    fissati per sempre e ogni fine del giro scrive un risultato (R5)."""
    mk = leggi_marcatore(p)
    campi = {"candidato_eseguito": True}
    if mk.get("candidato_eseguito"):
        campi["candidato_rieseguito_nelle_riprese"] = list(mk.get("candidato_rieseguito_nelle_riprese") or []) + [adesso()]
    else:
        campi["candidato_eseguito_dal"] = adesso()
    aggiorna_marcatore(p, "candidato in esecuzione: da qui ogni fine scrive un risultato (R5)", **campi)


def fermo_senza_risultato(posti, e: FermoSenzaRisultato) -> None:
    """D4: lo STOP prima dell'esecuzione del candidato non scrive un risultato e non consuma il vault.
    Il marcatore registra stato e motivo (in cima, e nella lista ``fermi_senza_risultato``)."""
    fermi = list(leggi_marcatore(posti.marcatore).get("fermi_senza_risultato") or [])
    fermi.append({"data": adesso(), "regola": e.regola, "stato": e.stato, "motivo": e.motivo, "dettagli": e.dettagli})
    aggiorna_marcatore(posti.marcatore, e.stato, motivo=f"{e.regola}: {e.motivo}", dettagli=e.dettagli,
                       fermi_senza_risultato=fermi)


def prepara_avanzamento(avanzamento: Path, impronta_giro: str, componenti: dict, candidato_eseguito: bool) -> dict:
    """R3, PRIMA di leggere i dati: il file IMPRONTA.json della cartella di avanzamento. Si rifiuta
    di riprendere pezzi senza impronta, con un'impronta diversa, o se manca IMPRONTA.json.

    D4: se il candidato non e' mai stato eseguito (tentativo precedente fermo sui dati) non ci
    possono essere pezzi; un IMPRONTA.json con un'impronta diversa (per esempio file di dati
    rimessi a posto) si sostituisce, e quella vecchia resta in ``impronte_tentativi_precedenti``."""
    avanzamento.mkdir(parents=True, exist_ok=True)
    p_imp = avanzamento / "IMPRONTA.json"
    lavori = sorted(avanzamento.glob("pezzo_*.json"))
    p_val = avanzamento / "valuta.json"
    if p_val.exists():
        lavori.append(p_val)
    if lavori and not candidato_eseguito:
        raise SystemExit(f"RIFIUTO (R3): in {avanzamento} ci sono {len(lavori)} file di avanzamento ma il marcatore "
                         f"dice che il candidato non e' mai stato eseguito: non si sa da dove vengono")
    nuovo = {"candidato": CANDIDATO, "impronta_giro": impronta_giro, "componenti": componenti, "data": adesso()}
    if not p_imp.exists():
        if lavori:
            raise SystemExit(f"RIFIUTO (R3): in {avanzamento} ci sono {len(lavori)} file di avanzamento ma manca "
                             f"IMPRONTA.json: non si sa da che giro vengono, non si riprendono")
        scrivi_json(p_imp, nuovo)
        stato = "nuovo"
    else:
        try:
            imp = json.loads(p_imp.read_text(encoding="utf-8"))
        except Exception as e:
            raise SystemExit(f"RIFIUTO (R3): {p_imp} non si legge ({type(e).__name__}: {e})")
        if imp.get("impronta_giro") != impronta_giro:
            if candidato_eseguito or lavori:
                raise SystemExit(f"RIFIUTO (R3): {p_imp} e' di un giro diverso (impronta {imp.get('impronta_giro')}, "
                                 f"questa {impronta_giro}): non si mescola")
            nuovo["impronte_tentativi_precedenti"] = list(imp.get("impronte_tentativi_precedenti") or []) + [
                {"impronta_giro": imp.get("impronta_giro"), "data": imp.get("data"),
                 "nota": "tentativo fermo prima dell'esecuzione del candidato (D4)"}]
            scrivi_json(p_imp, nuovo)
            stato = "nuovo (il tentativo precedente si era fermato prima del candidato, con un'altra impronta)"
        else:
            stato = "ripresa"
    for p in lavori:
        try:
            dp = json.loads(p.read_text(encoding="utf-8"))
        except Exception as e:
            raise SystemExit(f"RIFIUTO (R3): {p} non si legge ({type(e).__name__}: {e})")
        if not dp.get("impronta_giro"):
            raise SystemExit(f"RIFIUTO (R3): {p} non porta l'impronta del giro: non si riprende")
        if dp["impronta_giro"] != impronta_giro:
            raise SystemExit(f"RIFIUTO (R3): {p} e' di un giro diverso (impronta diversa): non si mescola")
    return {"cartella": str(avanzamento), "stato": stato, "pezzi_presenti": len([p for p in lavori if p != p_val]),
            "valuta_presente": p_val.exists()}


def impronta_calcolo(D, trades, n_trade: int, durata, vietate, taglio: int, n_caso: int, impronta_giro: str) -> str:
    """Impronta di cio' che decide le simulazioni, calcolata dopo aver letto i dati (serie, trade
    del candidato, barre vietate) e legata all'impronta del giro (lanciatore, codice, file di dati)."""
    h = hashlib.sha256()
    h.update(impronta_giro.encode())
    for c in D["candele"]:
        h.update(f"{c.ts},{c.open!r},{c.high!r},{c.low!r},{c.close!r};".encode())
    for c in D["mark"]:
        h.update(f"{c.ts},{c.open!r},{c.high!r},{c.low!r},{c.close!r};".encode())
    for t, r in D["funding"]:
        h.update(f"{t},{r!r};".encode())
    h.update(json.dumps({"taglio": taglio, "n_trade": n_trade, "durata": durata, "n_caso": n_caso,
                         "vietate": [list(x) for x in vietate],
                         "trade": [(t.ts_entrata, t.ts_uscita, repr(t.r)) for t in trades]}).encode())
    return h.hexdigest()


def registra_impronta_calcolo(avanzamento: Path, impronta_giro: str, imp_calc: str) -> None:
    p_imp = avanzamento / "IMPRONTA.json"
    try:
        imp = json.loads(p_imp.read_text(encoding="utf-8"))
    except Exception as e:
        raise Fermo(f"{p_imp} non si legge durante il giro ({type(e).__name__}: {e})")
    if imp.get("impronta_giro") != impronta_giro:
        raise Fermo(f"{p_imp} e' cambiato durante il giro (impronta diversa)")
    if imp.get("impronta_calcolo") is None:
        imp["impronta_calcolo"] = imp_calc
        imp["data_impronta_calcolo"] = adesso()
        scrivi_json(p_imp, imp)
    elif imp["impronta_calcolo"] != imp_calc:
        raise Fermo("l'impronta del calcolo (serie, trade, barre vietate) non e' quella dei pezzi gia' calcolati: "
                    "non si mescola")


class Lucchetto:
    """Un solo giro alla volta sulla stessa cartella di avanzamento (D5: atomico). Lucchetto ``fcntl``
    esclusivo e non bloccante su ``IN_CORSO.json``: il sistema lo toglie da se' se il processo muore,
    quindi non c'e' un lucchetto «vecchio» da indovinare. Dopo averlo preso si controlla che il file
    sul disco sia ancora quello aperto (chi finisce lo toglie): se no, si riprova."""

    def __init__(self, cartella: Path):
        self.p = cartella / "IN_CORSO.json"
        self.fd = None

    def __enter__(self):
        global _FD_LUCCHETTO
        self.p.parent.mkdir(parents=True, exist_ok=True)
        for _ in range(5):
            fd = os.open(self.p, os.O_RDWR | os.O_CREAT, 0o644)
            try:
                fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except (BlockingIOError, PermissionError):
                try:
                    altro = os.read(fd, 4096).decode("utf-8", errors="replace")
                finally:
                    os.close(fd)
                raise SystemExit(f"RIFIUTO: un altro giro e' in corso ({self.p}: {altro.strip() or 'senza dettagli'})")
            try:
                stesso = os.fstat(fd).st_ino == os.stat(self.p).st_ino
            except FileNotFoundError:
                stesso = False
            if not stesso:  # tolto o sostituito da chi ha appena finito: si riprova sul file nuovo
                os.close(fd)
                continue
            os.ftruncate(fd, 0)
            os.write(fd, json.dumps({"pid": os.getpid(), "data": adesso()}).encode("utf-8"))
            self.fd = fd
            _FD_LUCCHETTO = fd
            return self
        raise SystemExit(f"RIFIUTO: il lucchetto {self.p} cambia di continuo: un altro giro sta partendo")

    def __exit__(self, *_e):
        global _FD_LUCCHETTO
        try:
            if os.stat(self.p).st_ino == os.fstat(self.fd).st_ino:
                self.p.unlink()
        except FileNotFoundError:
            pass
        finally:
            _FD_LUCCHETTO = None
            os.close(self.fd)  # chiudere rilascia il lucchetto


# ---------------------------------------------------------------------------
# L'esame di un periodo (vault, o validazione per la prova)
# ---------------------------------------------------------------------------

CONDIZIONI = ("profit_factor", "trade_minimi", "rendimento_positivo", "sopra_il_caso")


def _criterio(m, metriche: dict, p90: float, regole: dict) -> dict:
    return m.statistica.criterio_vault(metriche, p90, trade_minimi=regole["trade_minimi_vault"],
                                       pf_minimo=regole["profit_factor_minimo"])


def _criterio_senza_caso(metriche: dict, regole: dict, motivo: str) -> dict:
    """Le condizioni del criterio che non dipendono dal caso, quando le entrate casuali mancano."""
    pf = float(metriche["profit_factor"])
    n = int(metriche["n_trade"])
    rend = float(metriche["rendimento_totale"])
    return {"esito": False, "motivo": motivo,
            "condizioni": {"profit_factor": bool(pf >= regole["profit_factor_minimo"]),
                           "trade_minimi": bool(n >= regole["trade_minimi_vault"]),
                           "rendimento_positivo": bool(rend > 0.0), "sopra_il_caso": None},
            "valori": {"profit_factor": pf, "n_trade": n, "rendimento_totale": rend, "r_medio": metriche.get("r_medio"),
                       "r_caso_percentile_90": None, "pf_minimo": float(regole["profit_factor_minimo"]),
                       "trade_minimi": int(regole["trade_minimi_vault"])}}


def descrivi_periodo(fine: date, taglio: int) -> dict:
    return {"serie_dal": INIZIO_IN_SAMPLE.isoformat(), "dal": _iso(taglio + 1), "fine": fine.isoformat(),
            "taglio_ts": taglio,
            "regola": "contano i trade entrati dopo il taglio (ts_entrata > taglio); nessun ingresso su segnali di barre "
                      "che chiudono entro il taglio; indicatori caldi dalla serie dal 2020"}


def prepara_esame(m, *, fine: date, taglio: int, controlli: dict) -> SimpleNamespace:
    """PRIMA dell'esecuzione del candidato (D4: uno STOP qui non scrive un risultato): carica la
    serie con ``comune.carica`` della campagna, controlla che sia quella appena controllata da D2/D3
    e prepara gli indicatori del candidato (``Fabbriche``: nessun trade si calcola qui)."""
    C = m.comune
    tempi: dict = {}
    # la convenzione della validazione, spostata: costanti in memoria, il file comune.py non cambia
    C.FINE_VALIDAZIONE = fine
    C.FINE_COSTRUZIONE_TS = taglio
    C._CACHE.clear()
    var = m.varianti.VARIANTI[CANDIDATO]
    if var.tf != TF:
        raise FermoSenzaRisultato("prima del candidato", f"il timeframe del candidato e' {var.tf!r}, il lanciatore "
                                  f"controlla i dati a {TF!r}", stato=STATO_FERMO_ERRORE)
    t = time.time()
    D = C.carica(var.tf, "validazione")
    tempi["carica"] = round(time.time() - t, 1)
    candele = D["candele"]
    if not candele:
        raise FermoSenzaRisultato("D2", "la serie del periodo e' vuota")
    if candele[-1].close_ts > m.dati.ms_da_data(fine) + 86_400_000 - 1:
        raise FermoSenzaRisultato("prima del candidato", "la serie va oltre la fine del periodo", stato=STATO_FERMO_ERRORE)
    sha_ts = sha256_testo(",".join(str(c.ts) for c in candele))
    if sha_ts != controlli.get("sha256_ts_allineate"):
        raise FermoSenzaRisultato("prima del candidato", "la serie di comune.carica non e' quella controllata dalla "
                                  "regola dei dati (D2-D3)", {"barre_comune_carica": len(candele),
                                                              "barre_controllate": controlli.get("barre_serie_dal_2020")},
                                  stato=STATO_FERMO_ERRORE)
    t = time.time()
    F = C.Fabbriche(var, D, solo_dopo_ts=taglio)
    tempi["indicatori"] = round(time.time() - t, 1)
    return SimpleNamespace(var=var, D=D, F=F, tempi=tempi)


def esame(m, prep: SimpleNamespace, *, fine: date, taglio: int, etichetta: str, n_caso: int, pezzo: int,
          avanzamento: Path, regole: dict, contesto: dict, processi: int, impronta_giro: str,
          ferma_dopo_pezzi=None) -> dict:
    """Esegue il candidato (``prep`` viene da ``prepara_esame``), lo giudica sul periodo che segue
    ``taglio`` fino a ``fine`` e calcola il tasso del caso.

    Torna il risultato con l'esito; ogni STOP diventa ``Fermo`` con il risultato parziale (R5: il
    candidato e' eseguito, da qui ogni fine scrive un risultato)."""
    C, mo, st = m.comune, m.motore, m.statistica
    tempi: dict = dict(prep.tempi)
    t_tot = time.time()
    ris: dict = {"candidato": CANDIDATO, "etichetta": etichetta, "data": adesso(),
                 "periodo": descrivi_periodo(fine, taglio), "regole_esame": regole, "contesto": contesto,
                 "tempi_secondi": tempi}
    try:
        var, D, F = prep.var, prep.D, prep.F
        par = C.PARAM
        candele, mark, funding = D["candele"], D["mark"], D["funding"]
        t = time.time()
        ris_c = mo.esegui(candele, None, mark, funding, F.crea_strategia(), par)
        trades = [x for x in ris_c.trades if x.ts_entrata > taglio]
        prima_del_taglio = [x for x in ris_c.trades if x.ts_entrata <= taglio]
        tempi["candidato"] = round(time.time() - t, 1)
        ultimo_giorno = m.dati.ms_da_data(fine)
        ris["extra"] = {
            "trade_prima_del_taglio_nell_esecuzione": len(prima_del_taglio),
            "trade_chiusi_a_fine_dati": sum(1 for x in trades if x.esito == "fine_dati"),
            "trade_entrati_l_ultimo_giorno": sum(1 for x in trades if x.ts_entrata >= ultimo_giorno),
            "ultima_barra_della_serie": _iso(candele[-1].ts),
            "buchi_dati_tutta_la_serie_dal_2020": ris_c.n_buchi_dati,
            "funding_in_buco_tutta_la_serie_dal_2020": ris_c.n_funding_in_buco,
        }
        if prima_del_taglio:
            raise Fermo(f"{len(prima_del_taglio)} trade del candidato entrati prima del taglio: le Fabbriche della "
                        f"campagna dovevano impedirlo, il conto non e' quello della validazione")
        t = time.time()
        vietate, quota_vietate = F.barre_vietate(par)
        tempi["barre_vietate"] = round(time.time() - t, 1)
        n_trade = len(trades)
        durata = mo.durata_media_barre(trades, D["passo"]) if trades else None
        imp_calc = impronta_calcolo(D, trades, n_trade, durata, vietate, taglio, n_caso, impronta_giro)
        registra_impronta_calcolo(avanzamento, impronta_giro, imp_calc)
        ris["impronta_calcolo"] = imp_calc

        # 1) come in validazione: candidato, (a), (b) con 200 semi e contro_baseline, percentile, buy and hold
        p_val = avanzamento / "valuta.json"
        if p_val.exists():
            sal = json.loads(p_val.read_text(encoding="utf-8"))
            if sal.get("impronta_giro") != impronta_giro or sal.get("impronta_calcolo") != imp_calc:
                raise Fermo(f"{p_val} viene da un giro diverso (impronta diversa): non si mescola")
            come_val, valori_b, tempi["valuta"] = sal["come_validazione"], sal["valori_b"], sal["secondi"]
            tempi["valuta_ripresa_da_avanzamento"] = True
        else:
            t = time.time()
            v = C.valuta(var, periodo="validazione", processi=processi)
            sec = round(time.time() - t, 1)
            chiavi = [(x.ts_entrata, x.ts_uscita, x.r) for x in v.get("_trades", [])]
            if chiavi != [(x.ts_entrata, x.ts_uscita, x.r) for x in trades]:
                raise Fermo("i trade di comune.valuta non sono quelli dell'esecuzione del candidato")
            # stessa forma della voce del log (registro._serializza dopo run._pulisci)
            come_val = json.loads(json.dumps(m.run._pulisci(C.per_log(v)), default=m.registro._serializza))
            valori_b = [float(x) for x in v.get("_valori_b", [])]
            scrivi_json(p_val, {"impronta_giro": impronta_giro, "impronta_calcolo": imp_calc,
                                "come_validazione": come_val, "valori_b": valori_b, "secondi": sec, "data": adesso()},
                        grezzo=True)
            tempi["valuta"] = sec
        ris["come_validazione"] = come_val
        ris["come_validazione_nota"] = (
            "uscita di comune.valuta(periodo='validazione') con FINE_VALIDAZIONE e FINE_COSTRUZIONE_TS spostati in "
            "memoria: «periodo»: «validazione» e' l'etichetta del codice della campagna, il periodo vero e' il campo "
            "«periodo» del risultato. buchi_dati e funding_in_buco qui dentro sono contati su tutta la serie dal 2020.")

        # 2) le metriche del candidato sui soli trade del periodo
        r = [x.r for x in trades]
        met_v = come_val["metriche"]
        curva = [(taglio, par.capitale_iniziale)]
        cap = par.capitale_iniziale
        for x in sorted(trades, key=lambda x: x.ts_uscita):
            cap += x.pnl
            curva.append((x.ts_uscita, cap))
        metriche = {
            "n_trade": n_trade,
            "profit_factor": met_v.get("profit_factor", 0.0),
            "rendimento_totale": met_v.get("rendimento_totale", 0.0),
            # l'R medio della consegna e' quello di valuta (np.mean); somma/numero si riporta accanto
            "r_medio": float(met_v["r_medio"]) if n_trade else None,
            "r_medio_somma_su_numero": float(sum(r) / n_trade) if n_trade else None,
            "drawdown_max": mo.drawdown_massimo(curva),
            "drawdown_max_curva_del_motore": mo.drawdown_massimo(ris_c.curva_capitale),
            "capitale_finale_da_1000": cap,
        }
        for k in ("r_medio_per_anno", "trade_per_anno", "rendimento_per_anno", "r_medio_senza_3_migliori", "win_rate",
                  "esiti", "trade_ridotti", "violazioni_liquidazione", "segnali_non_validi", "stop_medio_pct",
                  "stop_oltre_6pct", "durata_media_ore"):
            if k in met_v:
                metriche[k] = met_v[k]
        for k in ("buchi_dati", "funding_in_buco"):  # contati dal motore su tutta la serie dal 2020
            if k in met_v:
                metriche[f"{k}_tutta_la_serie_dal_2020"] = met_v[k]
        cd = contesto.get("controllo_dati") or {}
        metriche["buchi_nel_periodo"] = cd.get("buchi_nel_periodo")
        metriche["buy_and_hold_per_anno"] = come_val.get("buy_and_hold_per_anno")
        ris["metriche"] = metriche
        violazioni = int(met_v.get("violazioni_liquidazione") or 0)
        sotto_minimo = n_trade < regole["trade_minimi_vault"]

        caso: dict = {"calcolato": False, "simulazioni": n_caso, "semi": [0, n_caso - 1], "n_trade_richiesti": n_trade,
                      "durata_media_barre": durata, "barre_vietate_quota": quota_vietate,
                      "barre_vietate_intervalli": len(vietate), "barre_serie": len(candele)}
        ris["caso"] = caso
        errore_b = (come_val.get("baseline_b") or {}).get("errore") if n_trade else None
        if n_trade == 0 or errore_b:
            motivo_caso = ("nessun trade nel periodo: le entrate casuali non si possono costruire" if n_trade == 0 else
                           f"le entrate casuali non si possono costruire: {errore_b}")
            caso["motivo"] = motivo_caso
            crit = _criterio_senza_caso(metriche, regole, motivo_caso)
            ris["criterio_vault"] = crit
            if sotto_minimo:
                esito, motivo = "non si sa", (f"{n_trade} trade, sotto i {regole['trade_minimi_vault']} minimi del vault "
                                              f"(sezione 8); {motivo_caso}")
            else:
                esito, motivo = "non valutabile", f"{motivo_caso} (sezione 8: la variante e' non valutabile)"
        else:
            # 3) le entrate casuali, a pezzi, con ripresa (solo pezzi con la stessa impronta)
            semi = list(range(n_caso))
            pezzi = [tuple(semi[k:k + pezzo]) for k in range(0, n_caso, pezzo)]
            fatti = {}
            for p in sorted(avanzamento.glob("pezzo_*.json")):
                dati_p = json.loads(p.read_text(encoding="utf-8"))
                if dati_p.get("impronta_giro") != impronta_giro or dati_p.get("impronta_calcolo") != imp_calc:
                    raise Fermo(f"{p} viene da un giro diverso (impronta diversa): non si mescola")
                fatti[tuple(dati_p["semi"])] = dati_p
            ripresi = len([pz for pz in pezzi if pz in fatti])
            da_fare = [pz for pz in pezzi if pz not in fatti]
            L = prepara_lavoro(m, D, F, n_trade, durata, vietate)
            nuovi = [0]

            def salva(r_pezzo):
                semi_p = r_pezzo["semi"]
                nome = avanzamento / f"pezzo_{semi_p[0]:04d}_{len(semi_p):03d}.json"
                scrivi_json(nome, dict(r_pezzo, impronta_giro=impronta_giro, impronta_calcolo=imp_calc, data=adesso()),
                            grezzo=True)
                fatti[tuple(semi_p)] = r_pezzo
                nuovi[0] += 1
                if ferma_dopo_pezzi is not None and nuovi[0] >= ferma_dopo_pezzi:
                    raise InterruzioneVoluta(f"interrotto di proposito dopo {nuovi[0]} pezzi (prova della ripresa)")

            t = time.time()
            simula_in_parallelo(L, da_fare, processi, salva)
            tempi["simulazioni_caso"] = round(time.time() - t, 1)
            tempi["pezzi_ripresi"] = ripresi
            tempi["pezzi_calcolati"] = len(da_fare)
            sims = sorted((s for pz in pezzi for s in fatti[pz]["simulazioni"]), key=lambda s: s["seme"])
            if [s["seme"] for s in sims] != semi:
                raise Fermo("i semi delle simulazioni non sono 0..n-1, una volta ciascuno")
            for s in sims:
                if s["r_medio"] is None:
                    s["r_medio"] = float("nan")  # vuota: non entra nel percentile, non passa il criterio
            r_medi = [s["r_medio"] for s in sims if s["n_trade"] > 0]
            if not r_medi:
                raise Fermo("tutte le simulazioni del caso sono vuote: il 90° percentile non si calcola")
            p90 = st.percentile(r_medi, regole["percentile_caso"])
            crit = _criterio(m, metriche, p90, regole)
            ris["criterio_vault"] = crit
            for s in sims:
                c = _criterio(m, s, p90, regole)
                s["passa"] = c["esito"]
                s["condizioni"] = c["condizioni"]
            tasso = st.tasso_del_caso([s["passa"] for s in sims])
            conteggi = {k: sum(1 for s in sims if s["condizioni"][k]) for k in CONDIZIONI}
            conteggi["tutte"] = sum(1 for s in sims if s["passa"])
            # 4) la gemella contro la (b) della campagna sui semi in comune (0..199)
            semi_b = min(C.N_SIM, n_caso)  # la (b) della campagna usa i semi 0..N_SIM-1
            r_g = [s["r_medio"] for s in sims if s["seme"] < semi_b and s["n_trade"] > 0]
            if n_caso >= C.N_SIM:
                gemella_ok = bool(r_g == valori_b)
            else:  # prova ridotta: si confronta l'inizio (vale se non ci sono simulazioni vuote)
                gemella_ok = bool(r_g == valori_b[:len(r_g)])
            pf = [s["profit_factor"] for s in sims if s["n_trade"] > 0]
            caso.update({
                "calcolato": True,
                "percentile_90": p90, "metodo_percentile": "statistica.percentile (numpy, lineare)",
                "tasso_del_caso": tasso, "passano": conteggi["tutte"],
                "condizioni_passate_dalle_simulazioni": conteggi,
                "simulazioni_vuote": sum(1 for s in sims if s["n_trade"] == 0),
                "r_medio_media": float(sum(r_medi) / len(r_medi)),
                "r_medio_min": min(r_medi), "r_medio_max": max(r_medi),
                "trade_per_simulazione_medio": sum(s["n_trade"] for s in sims) / len(sims),
                "trade_per_simulazione_min": min(s["n_trade"] for s in sims),
                "segnali_scartati_totali": sum(s["segnali_non_validi"] for s in sims),
                "quota_profit_factor_sopra_minimo": sum(1 for x in pf if x >= regole["profit_factor_minimo"]) / len(sims),
                "quota_rendimento_positivo": sum(1 for s in sims if s["rendimento_totale"] > 0) / len(sims),
                "quota_trade_minimi": sum(1 for s in sims if s["n_trade"] >= regole["trade_minimi_vault"]) / len(sims),
                "percentile_del_candidato_fra_le_simulazioni_caso": st.percentile_del_candidato(metriche["r_medio"], r_medi),
                "semi_confrontati_con_la_b": len(r_g),
                "gemella_uguale_alla_b_sui_semi_comuni": gemella_ok,
                "secondi_per_simulazione_medio": sum(s["secondi"] for s in sims) / len(sims),
            })
            ris["simulazioni_caso"] = sims
            if not gemella_ok:
                raise Fermo("le entrate casuali del tasso del caso non ridanno la (b) della campagna sui semi "
                            f"0..{semi_b - 1}", {"r_gemella": r_g[:50], "r_b": valori_b[:50]})
            if sotto_minimo:
                esito, motivo = "non si sa", (f"{n_trade} trade, sotto i {regole['trade_minimi_vault']} minimi del vault "
                                              f"(sezione 8)")
            elif crit["esito"] and violazioni:
                esito, motivo = "non passa", (f"passa le quattro condizioni del criterio del vault ma ha {violazioni} "
                                              f"violazioni di liquidazione: sezione 7, un candidato con violazioni non "
                                              f"va avanti")
            elif crit["esito"]:
                esito, motivo = "passa", "tutte e quattro le condizioni del criterio del vault"
            else:
                cadute = [k for k, ok in crit["condizioni"].items() if not ok]
                esito, motivo = "non passa", f"condizioni del criterio del vault non passate: {', '.join(cadute)}"
        ris["esito"] = esito
        ris["motivo"] = motivo
        tempi["totale_esame"] = round(time.time() - t_tot, 1)
        return ris
    except Fermo as e:
        e.parziale = ris
        raise
    except (SystemExit, Exception) as e:
        f = Fermo(f"STOP inatteso durante l'esame: {type(e).__name__}: {e}", traceback.format_exc()[-6000:])
        f.parziale = ris
        raise f from e


def risultato_fermo(e: Fermo, base: dict, candidato_eseguito: bool = True) -> dict:
    """Il risultato di uno STOP DOPO l'esecuzione del candidato (R5, D4): esito «non valutabile» col
    motivo. ``candidato_eseguito`` dice se il candidato e' stato eseguito in QUESTO tentativo (in una
    ripresa puo' esserlo stato solo in un tentativo precedente, interrotto)."""
    ris = dict(e.parziale) if e.parziale else dict(base)
    ris["esito"] = "non valutabile"
    ris["motivo"] = e.motivo
    ris["fermo"] = {"motivo": e.motivo, "dettagli": e.dettagli, "candidato_eseguito": bool(candidato_eseguito),
                    "metriche_del_candidato_calcolate": "come_validazione" in ris}
    ris.setdefault("caso", {"calcolato": False, "motivo": e.motivo})
    ris.setdefault("criterio_vault", None)
    return ris


class _NonCalcolato(dict):
    def __missing__(self, _k):
        return "non calcolato"

    def get(self, k, default=None):
        v = dict.get(self, k, default)
        return "non calcolato" if v is None else v


def note_periodo(ris: dict) -> dict:
    """R6: le note su ultimo giorno e buchi, in chiaro."""
    cd = _NonCalcolato((ris.get("contesto") or {}).get("controllo_dati") or {})
    ex = _NonCalcolato(ris.get("extra") or {})
    return {
        "ultimo_giorno": (
            f"Ultima barra della serie allineata: {cd.get('ultima_barra_allineata')} (attesa "
            f"{cd.get('ultima_barra_attesa')}). Una posizione ancora aperta sull'ultima barra si chiude al close della "
            f"barra delle 23:45 con esito fine_dati (la regola d'uscita direbbe all'apertura delle 00:00 del giorno dopo) "
            f"e il settlement di funding delle 00:00 del giorno dopo non si conta. Trade chiusi cosi': "
            f"{ex.get('trade_chiusi_a_fine_dati')}; trade entrati l'ultimo giorno: {ex.get('trade_entrati_l_ultimo_giorno')}."),
        "buchi": (
            f"Nel periodo: {cd.get('buchi_nel_periodo')} buchi nella serie allineata last/mark "
            f"({cd.get('barre_mancanti_nei_buchi')} barre mancanti); barre tolte dal last {cd.get('tolte_dal_last_nel_periodo')}, "
            f"dal mark {cd.get('tolte_dal_mark_nel_periodo')}; giorni con barre tolte {cd.get('giorni_con_barre_tolte')}. "
            f"Barre di ADA senza BTC: {cd.get('barre_ada_senza_btc_nel_periodo')} (il rendimento di BTC a 24 ore del "
            f"candidato si calcola 96 posizioni indietro nella serie: una barra senza BTC toglie il segnale in quella "
            f"posizione e 96 posizioni dopo; con un buco, 96 posizioni indietro sono piu' di 24 ore). Sulla serie intera "
            f"dal 2020 il motore conta {ex.get('buchi_dati_tutta_la_serie_dal_2020')} buchi e "
            f"{ex.get('funding_in_buco_tutta_la_serie_dal_2020')} settlement di funding caduti in un buco con posizione "
            f"aperta: sono i numeri che il codice della campagna chiama buchi_dati e funding_in_buco."),
        "funding": (f"Settlement di funding nel periodo: {cd.get('settlement_nel_periodo')}; intervalli osservati fra "
                    f"un settlement e il precedente (ore: quante volte) {cd.get('intervalli_di_funding_osservati_ore')}; "
                    f"volte in cui fra due settlement passa piu' dell'intervallo dichiarato dai file: "
                    f"{cd.get('n_buchi_di_funding')}. Nessun mese senza settlement (altrimenti D2 avrebbe fermato il giro "
                    f"prima del candidato); nessun numero «atteso» costruito sull'intervallo piu' corto."),
        "mesi_sotto_il_99": (f"Mesi con meno del 99% delle barre allineate attese (AVVISO, D3; sotto il 50% il giro si "
                             f"sarebbe fermato prima del candidato, D2): {cd.get('mesi_sotto_il_99')}."),
        "controllo_dati_ok": dict.get(cd, "ok"),
        "blocchi_dati": dict.get(cd, "blocchi"),
        "avvisi_dati": dict.get(cd, "avvisi"),
    }


def completa_risultato(ris: dict, m, *, sha_l: str, regole: dict, n_caso: int, impronta_avvio: dict, sha_avvio: str,
                       impronta_giro, guardia: dict, posti) -> dict:
    """R6: versioni, SHA-256 del lanciatore, semi, impronte, guardia, note."""
    n_b = regole["simulazioni_baseline_casuale"]
    ris["versioni"] = versioni()
    ris["sha256_lanciatore"] = sha_l
    ris["lanciatore"] = str(Path(__file__).resolve())
    ris["semi"] = {"caso": [0, n_caso - 1], "baseline_b": [0, n_b - 1], "bootstrap": regole["bootstrap"],
                   "nota": "i semi del caso e della (b) partono da 0: la (b) a 200 semi sono i primi 200 semi del caso"}
    ris["impronta"] = {"impronta_avvio_sha256": sha_avvio, "impronta_avvio": impronta_avvio,
                       "impronta_giro": impronta_giro, "impronta_calcolo": ris.get("impronta_calcolo")}
    ris["guardia"] = {"ripresa": guardia.get("ripresa"), "marcatore": str(posti.marcatore),
                      "risultato": str(posti.risultato), "riassunto": str(posti.riassunto),
                      "avanzamento": str(posti.avanzamento)}
    try:
        dopo = controlla_codice(m.worktree, fermati=False)
        ris["codice_dopo_il_giro"] = {"ok": dopo["ok"], "problemi": dopo["problemi"]}
    except Exception as e:  # pragma: no cover
        ris["codice_dopo_il_giro"] = {"ok": False, "problemi": [f"controllo non riuscito: {type(e).__name__}: {e}"]}
    ris["note"] = note_periodo(ris)
    return ris


def _f(x, d=3) -> str:
    if x is None:
        return "-"
    if isinstance(x, str):
        return x
    if isinstance(x, bool):
        return "sì" if x else "no"
    if isinstance(x, float) and (math.isinf(x) or math.isnan(x)):
        return str(x)
    return f"{x:.{d}f}".replace(".", ",")


def _pct(x, d=1) -> str:
    if x is None or isinstance(x, str):
        return "-" if x is None else x
    return f"{100 * x:+.{d}f}%".replace(".", ",")


def _sn(b) -> str:
    return "sì" if b is True else ("no" if b is False else "non calcolata")


def riassunto(ris: dict, titolo: str) -> str:
    per = ris.get("periodo") or {}
    ve = ris.get("versioni") or {}
    co = (ris.get("contesto") or {}).get("codice") or {}
    righe = [
        f"# {titolo}", "",
        f"Candidato {CANDIDATO} (long, 15 minuti: rottura dell'intervallo d'apertura con media a 20 giorni e BTC in "
        f"calo nelle 24 ore). Trade contati se entrano dal {per.get('dal')} UTC, fino al {per.get('fine')}. Scritto il "
        f"{ris.get('data')} dal lanciatore `research/vault_strumenti/ADAUSDT.py` (SHA-256 {ris.get('sha256_lanciatore')}) "
        f"con il codice del candidato (commit {str(co.get('commit', COMMIT_ATTESO))[:8]} del branch della campagna). "
        f"Python {ve.get('python')}, numpy {ve.get('numpy')}, scipy {ve.get('scipy')}. Il JSON accanto, scritto prima "
        f"di questo file, è il risultato completo.", "",
        f"## Esito: **{str(ris.get('esito')).upper()}**", "",
    ]
    if ris.get("motivo"):
        righe += [f"Motivo: {ris['motivo']}.", ""]
    fe = ris.get("fermo")
    if fe:
        righe += [f"Il giro si è fermato dopo l'esecuzione del candidato (R5: il risultato si scrive comunque). "
                  f"Candidato eseguito in questo tentativo: {_sn(fe.get('candidato_eseguito'))}; metriche del candidato "
                  f"calcolate: {_sn(fe.get('metriche_del_candidato_calcolate'))}. Dettagli: {str(fe.get('dettagli'))[:3000]}", ""]
    cr = ris.get("criterio_vault") or {}
    va, cond = cr.get("valori"), cr.get("condizioni")
    ca = ris.get("caso") or {}
    if va and cond:
        p90 = va.get("r_caso_percentile_90")
        righe += [
            "| condizione del criterio del vault | valore | soglia | passa |", "|---|---|---|---|",
            f"| profit factor dopo i costi | {_f(va.get('profit_factor'), 2)} | almeno {_f(va.get('pf_minimo'), 2)} | {_sn(cond.get('profit_factor'))} |",
            f"| trade | {va.get('n_trade')} | almeno {va.get('trade_minimi')} | {_sn(cond.get('trade_minimi'))} |",
            f"| rendimento totale (composto da 1000) | {_pct(va.get('rendimento_totale'))} | sopra zero | {_sn(cond.get('rendimento_positivo'))} |",
            f"| R medio a trade dopo i costi | {_f(va.get('r_medio'))} | sopra {_f(p90)} (90° percentile delle "
            f"{ca.get('simulazioni')} entrate casuali) | {_sn(cond.get('sopra_il_caso'))} |",
            "",
        ]
    if ca.get("calcolato"):
        cp = ca.get("condizioni_passate_dalle_simulazioni") or {}
        righe += [
            f"**Tasso del caso:** {ca['passano']} strategie a entrate casuali su {ca['simulazioni']} passano lo stesso "
            f"criterio con lo stesso 90° percentile ({_f(100 * ca['tasso_del_caso'], 1)}%). Stessa direzione (long), stesso "
            f"numero di ingressi ({ca['n_trade_richiesti']}), distanza minima = durata media del candidato "
            f"({ca['durata_media_barre']} barre da 15 minuti), stessa uscita, semi {ca['semi'][0]}..{ca['semi'][1]}.", "",
            f"Quante delle {ca['simulazioni']} passano ogni condizione: profit factor {cp.get('profit_factor')}, trade minimi "
            f"{cp.get('trade_minimi')}, rendimento positivo {cp.get('rendimento_positivo')}, sopra il 90° percentile "
            f"{cp.get('sopra_il_caso')}, tutte insieme {cp.get('tutte')}. Simulazioni vuote {ca.get('simulazioni_vuote')}; "
            f"trade per simulazione in media {_f(ca.get('trade_per_simulazione_medio'), 1)} (minimo "
            f"{ca.get('trade_per_simulazione_min')}); R medio da {_f(ca.get('r_medio_min'))} a {_f(ca.get('r_medio_max'))}, "
            f"media {_f(ca.get('r_medio_media'))}. Il candidato sta al percentile "
            f"{_f(ca.get('percentile_del_candidato_fra_le_simulazioni_caso'), 1)} (indizio, non prova).", "",
        ]
    else:
        righe += [f"**Tasso del caso:** non calcolato ({ca.get('motivo')}).", ""]
    met = ris.get("metriche") or {}
    cv = ris.get("come_validazione") or {}
    if met.get("n_trade"):
        righe += ["## Metriche del periodo (come nella consegna)", ""]
        rpa = met.get("r_medio_per_anno") or {}
        righe += [
            f"* Trade {met['n_trade']}; R medio {_f(met.get('r_medio'))}; senza i 3 migliori "
            f"{_f(met.get('r_medio_senza_3_migliori'))}; profit factor {_f(met.get('profit_factor'), 2)}; win rate "
            f"{_f(100 * (met.get('win_rate') or 0), 0)}%.",
            f"* Rendimento totale composto da 1000: {_pct(met.get('rendimento_totale'))} (capitale finale "
            f"{_f(met.get('capitale_finale_da_1000'), 1)}); drawdown massimo {_f(100 * (met.get('drawdown_max') or 0), 1)}% "
            f"(sui soli trade del periodo, dal capitale iniziale).",
            "* Per anno d'uscita: " + "; ".join(
                f"{a} R {_f(rpa[a])}, {(met.get('trade_per_anno') or {}).get(a, 0)} trade, rendimento "
                f"{_pct((met.get('rendimento_per_anno') or {}).get(a))}" for a in sorted(rpa)) + ".",
            "* Buy and hold per anno (contesto, long / short): " + "; ".join(
                f"{a} {_pct(b.get('long'), 0)} / {_pct(b.get('short'), 0)}"
                for a, b in sorted((met.get("buy_and_hold_per_anno") or {}).items())) + ".",
            f"* Esiti: {met.get('esiti')}; stop medio {_f(100 * (met.get('stop_medio_pct') or 0), 1)}%; stop oltre il 6% "
            f"{met.get('stop_oltre_6pct')}; durata media {_f(met.get('durata_media_ore'), 1)} ore; trade ridotti "
            f"{met.get('trade_ridotti')}; violazioni di liquidazione {met.get('violazioni_liquidazione')}.",
        ]
        a, b = cv.get("baseline_a") or {}, cv.get("baseline_b") or {}
        righe += [
            f"* Baseline (a), solo per il rapporto: {_f(a.get('media'))}, t {_f(a.get('t'), 2)}, netta {_sn(a.get('netta'))}.",
            f"* Baseline (b) con 200 semi e contro_baseline come in validazione, solo per il rapporto: {_f(b.get('media'))}, "
            f"t {_f(b.get('t'), 2)}, netta {_sn(b.get('netta'))}, p-value {_f(b.get('p_value'), 4)}, percentile del "
            f"candidato {_f(cv.get('percentile_caso'), 1)}.", "",
        ]
    cd = (ris.get("contesto") or {}).get("controllo_dati")
    if cd:
        d1 = (ris.get("contesto") or {}).get("dati_periodo", {}).get("D1") or {}
        righe += [
            "## I dati del periodo, mese per mese (regola dei dati D1-D3, prima del candidato)", "",
            f"D1 (file mensili presenti e leggibili, prima di leggere le candele): {d1.get('file_presenti_e_leggibili')} su "
            f"{d1.get('file_attesi')} ({(d1.get('mesi') or ['?', '?'])[0]} -> {(d1.get('mesi') or ['?', '?'])[-1]}). "
            f"D2 (blocchi, prima del candidato): {cd.get('blocchi') or 'nessuno'}. Ultima barra allineata "
            f"{cd.get('ultima_barra_allineata')} (attesa {cd.get('ultima_barra_attesa')}), ultima di BTCUSDT "
            f"{cd.get('ultima_barra_btc')}.", "",
            f"D3 (AVVISI, solo riportati: mesi sotto il 99% delle barre attese, barre di ADA senza BTC, settlement "
            f"oltre l'intervallo dichiarato): {cd.get('avvisi') or 'nessuno'}.", "",
            "| mese | barre attese | last | mark | allineate | quota | BTC | quota BTC | ADA senza BTC | settlement | "
            "intervalli osservati (ore: volte) | ore dichiarate | avviso |",
            "|---|---|---|---|---|---|---|---|---|---|---|---|---|",
        ]
        righe += [f"| {r_['mese']} | {r_['barre_attese']} | {r_['barre_last']} | {r_['barre_mark']} | {r_['barre_allineate']} | "
                  f"{_f(r_['quota_allineate'], 4)} | {r_['barre_btc']} | {_f(r_.get('quota_btc'), 4)} | "
                  f"{r_['barre_ada_senza_btc']} | {r_['settlement_funding']} | "
                  f"{', '.join(f'{k}: {v}' for k, v in (r_.get('intervalli_osservati_ore') or {}).items()) or '-'} | "
                  f"{', '.join(str(o) for o in r_.get('ore_funding_dichiarate') or []) or '-'} | "
                  f"{'AVVISO: ' + '; '.join(r_['avvisi']) if r_.get('avvisi') else ''} |" for r_ in cd.get("mesi", [])]
        righe.append("")
    note = ris.get("note") or {}
    righe += ["## Da dichiarare", ""]
    for k in ("ultimo_giorno", "buchi", "mesi_sotto_il_99", "funding"):
        if note.get(k):
            righe.append(f"* {note[k]}")
    righe.append("* Il blocco `come_validazione` del JSON porta «periodo»: «validazione» perché è l'uscita di "
                 "`comune.valuta(periodo=\"validazione\")` con le due costanti spostate in memoria; il periodo vero è "
                 "quello scritto sopra.")
    ex = ris.get("extra") or {}
    righe += ["", "## Controlli", ""]
    if "gemella_uguale_alla_b_sui_semi_comuni" in ca:
        righe.append(f"* Le entrate casuali del tasso del caso ridanno la (b) della campagna sui semi "
                     f"0..{ca['semi_confrontati_con_la_b'] - 1}: {_sn(ca['gemella_uguale_alla_b_sui_semi_comuni'])}.")
    if ex:
        righe.append(f"* Trade del candidato entrati prima del taglio nell'esecuzione: "
                     f"{ex.get('trade_prima_del_taglio_nell_esecuzione')} (deve essere 0).")
    if ca.get("barre_vietate_quota") is not None:
        righe.append(f"* Barre vietate alle entrate casuali (quota sulla serie dal 2020): {_f(100 * ca['barre_vietate_quota'], 1)}%.")
    cdg = ris.get("codice_dopo_il_giro") or {}
    righe.append(f"* Codice del candidato dopo il giro uguale a quello congelato: {_sn(cdg.get('ok'))} {cdg.get('problemi') or ''}".rstrip() + ".")
    imp = ris.get("impronta") or {}
    righe.append(f"* Impronta d'avvio {imp.get('impronta_avvio_sha256')}; impronta del giro {imp.get('impronta_giro')}; "
                 f"ripresa di un giro interrotto: {_sn((ris.get('guardia') or {}).get('ripresa'))}.")
    righe.append(f"* Semi: {ris.get('semi')}.")
    righe.append(f"* Tempi (secondi): {ris.get('tempi_secondi')}.")
    return "\n".join(righe) + "\n"


def scrivi_risultato(ris: dict, posti, titolo: str) -> Path:
    """R6: prima il JSON (mai sovrascritto), poi il riassunto .md, poi il marcatore «finito» (con il
    motivo in cima azzerato, D5) e il segno."""
    dest = posti.risultato
    if not scrivi_json_nuovo(dest, ris):  # comparso durante il giro: non si sovrascrive, ma si scrive (R5)
        dest = dest.with_name(f"{dest.stem}_doppione_{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}.json")
        ris["attenzione"] = f"{posti.risultato} e' comparso durante il giro: questo risultato non lo sovrascrive"
        scrivi_json_nuovo(dest, ris)
    sha = sha256_file(dest)
    if dest == posti.risultato:
        try:
            testo = riassunto(ris, titolo)
        except Exception as e:  # il JSON e' gia' scritto: il riassunto non deve farlo perdere
            testo = (f"# {titolo}\n\nEsito: **{str(ris.get('esito')).upper()}**. Il riassunto completo non si e' potuto "
                     f"scrivere ({type(e).__name__}: {e}): vale il JSON {dest.name}.\n")
        scrivi_testo(posti.riassunto, testo)
    aggiorna_marcatore(posti.marcatore, "finito", motivo=None, dettagli=None, risultato=str(dest), sha256_risultato=sha,
                       esito=ris.get("esito"), finito=adesso())
    if posti.segno is not None and dest == posti.risultato and not posti.segno.exists():
        scrivi_json(posti.segno, {"candidato": CANDIDATO, "data": adesso(), "risultato": str(dest),
                                  "sha256_risultato": sha, "esito": ris.get("esito")})
    return dest


STATO_FERMO_ERRORE_DOPO = ("fermo per un errore prima di rieseguire il candidato, gia' eseguito in un tentativo "
                           "interrotto: si riprende solo con gli stessi file")


def _ferma_senza_risultato(posti, e: FermoSenzaRisultato, eseguito_prima: bool):
    """D4: registra il fermo nel marcatore (nessun risultato) e lo rilancia. In una ripresa di un giro
    in cui il candidato e' gia' stato eseguito (tentativo interrotto) il fermo prima di rieseguirlo
    vale come la continuazione dell'interruzione: si riprende con gli stessi file (D1 e le impronte
    lo controllano), e il risultato si scrive quando il giro finisce."""
    if eseguito_prima:
        e.stato = STATO_FERMO_DATI_DOPO if e.stato == STATO_FERMO_DATI else STATO_FERMO_ERRORE_DOPO
    fermo_senza_risultato(posti, e)
    raise e


def _compatto(controlli: dict) -> list:
    return [{k: r_.get(k) for k in ("mese", "barre_attese", "barre_allineate", "quota_allineate", "barre_btc", "quota_btc",
                                     "settlement_funding", "avvisi")} for r_ in controlli.get("mesi", [])]


def giro(m, *, posti, etichetta: str, fine: date, taglio: int, n_caso: int, pezzo: int, regole: dict, codice: dict,
         contesto: dict, sha_apertura, sha_insample: dict, prepara_periodo, processi: int, titolo: str,
         ferma_dopo_pezzi=None, dopo_esame=None):
    """Il giro comune al modo vault e alla prova.

    Ordine: guardia (R2) e lucchetto; marcatore creato con O_EXCL, o ripresa dello stesso giro;
    D1 (``prepara_periodo``: file mensili presenti e leggibili, nessuna candela letta); impronte
    (R3, D5); D2-D3 (``controllo_dati``) e preparazione (``prepara_esame``); il marcatore segna
    «candidato eseguito»; esame; scrittura (R6). PRIMA dell'esecuzione del candidato ogni STOP esce
    con ``FermoSenzaRisultato`` (nessun risultato, vault non consumato, D4); DOPO, ogni fine scrive
    il risultato (R5). Un'interruzione (kill, Ctrl-C) lascia il giro da riprendere."""
    sha_l = sha256_lanciatore()
    ver = versioni_impronta()
    impronta_avvio = {
        "candidato": CANDIDATO, "etichetta": etichetta, "lanciatore": str(Path(__file__).resolve()),
        "sha256_lanciatore": sha_l, "versioni": ver, "commit": codice["commit"], "sha256_codice": codice["sha256"],
        "sha256_apertura": sha_apertura, "regole_esame": regole, "n_caso": n_caso, "semi_caso": [0, n_caso - 1],
        "pezzo": pezzo, "taglio_ts": taglio, "fine": fine.isoformat(),
        "sha256_dati_insample_elenco": sha256_json(sha_insample),
    }
    sha_avvio = sha256_json(impronta_avvio)
    rifiuta_se_fatto(posti)
    posti.avanzamento.mkdir(parents=True, exist_ok=True)
    with Lucchetto(posti.avanzamento):
        rifiuta_se_fatto(posti)
        guardia = controlla_marcatore(posti, sha_avvio)
        prec = guardia.get("marcatore_precedente") or {}
        eseguito_prima = bool(prec.get("candidato_eseguito"))
        tentativo = {"pid": os.getpid(), "inizio": adesso(), "ripresa": guardia["ripresa"],
                     "candidato_gia_eseguito": eseguito_prima}
        # R2: il marcatore si scrive PRIMA di scaricare e leggere i dati del periodo
        if guardia["ripresa"]:
            aggiorna_marcatore(posti.marcatore, "ripreso: dati del periodo non ancora letti",
                               tentativi=list(prec.get("tentativi") or []) + [tentativo])
        else:
            stato0 = "iniziato: dati del periodo non ancora letti"
            if not crea_marcatore(posti.marcatore, {
                    "candidato": CANDIDATO, "etichetta": etichetta, "stato": stato0, "motivo": None, "dettagli": None,
                    "nota": "creato in modo esclusivo (O_EXCL) PRIMA di scaricare e leggere i dati del periodo (R2, D5): "
                            "finche' esiste, il giro non riparte, salvo la ripresa dello stesso giro (stessa impronta "
                            "d'avvio). Finche' candidato_eseguito e' false, uno STOP non ha consumato il vault (D4).",
                    "candidato_eseguito": False, "impronta_avvio_sha256": sha_avvio, "impronta_avvio": impronta_avvio,
                    "risultato_atteso": str(posti.risultato), "avanzamento": str(posti.avanzamento),
                    "tentativi": [tentativo], "iniziato": adesso(), "storia": [{"data": adesso(), "stato": stato0}]}):
                raise SystemExit(f"RIFIUTO (R2): {posti.marcatore} e' comparso mentre partiva il giro")
        base = {"candidato": CANDIDATO, "etichetta": etichetta, "data": adesso(), "periodo": descrivi_periodo(fine, taglio),
                "regole_esame": regole, "contesto": contesto}

        def con_risultato(fermo: Fermo, eseguito_ora: bool, impronta_giro):
            print(f"FERMO: {fermo.motivo}", flush=True)
            r_ = risultato_fermo(fermo, base, candidato_eseguito=eseguito_ora)
            completa_risultato(r_, m, sha_l=sha_l, regole=regole, n_caso=n_caso, impronta_avvio=impronta_avvio,
                               sha_avvio=sha_avvio, impronta_giro=impronta_giro, guardia=guardia, posti=posti)
            return r_, scrivi_risultato(r_, posti, titolo)

        # D1: i file del periodo, presenti e leggibili (nessuna candela letta: uno STOP non scrive il risultato)
        try:
            dati_periodo = prepara_periodo()
        except FermoSenzaRisultato as e:
            _ferma_senza_risultato(posti, e, eseguito_prima)
        except (SystemExit, Exception) as e:
            _ferma_senza_risultato(posti, FermoSenzaRisultato(
                "prima del candidato", f"{type(e).__name__}: {e}", traceback.format_exc()[-3000:],
                stato=STATO_FERMO_ERRORE), eseguito_prima)
        sha_dati = dict(sha_insample)
        sha_dati.update(dati_periodo.get("sha256") or {})
        sha_dati_elenco = sha256_json(sha_dati)
        componenti = {"impronta_avvio_sha256": sha_avvio, "sha256_lanciatore": sha_l, "versioni": ver,
                      "sha256_codice": codice["sha256"], "sha256_dati": sha_dati}
        impronta_giro = sha256_json(componenti)
        contesto["dati_periodo"] = dati_periodo
        mk = leggi_marcatore(posti.marcatore)
        if eseguito_prima and mk.get("sha256_dati_elenco") != sha_dati_elenco:
            # D4, R5: il candidato e' gia' stato eseguito su altri file: lo stesso giro non puo' finire sugli stessi dati
            return con_risultato(Fermo(
                f"i file di dati non sono quelli con cui il candidato e' stato eseguito in un tentativo interrotto "
                f"(elenco {mk.get('sha256_dati_elenco')}, ora {sha_dati_elenco}): lo stesso giro non puo' finire sugli "
                f"stessi dati"), False, impronta_giro)
        precedenti = list(mk.get("sha256_dati_tentativi_precedenti") or [])
        if not eseguito_prima and mk.get("sha256_dati_elenco") and mk["sha256_dati_elenco"] != sha_dati_elenco:
            precedenti.append({"sha256_dati_elenco": mk["sha256_dati_elenco"], "n_file_dati": mk.get("n_file_dati"),
                               "sostituito": adesso(), "nota": "tentativo fermo prima dell'esecuzione del candidato (D4): "
                                                               "i file si potevano ancora cambiare"})
        try:
            stato_av = prepara_avanzamento(posti.avanzamento, impronta_giro, componenti, eseguito_prima)  # R3
        except SystemExit as e:
            aggiorna_marcatore(posti.marcatore, "rifiuto: avanzamento non riprendibile (R3)", motivo=str(e))
            raise
        contesto["avanzamento"] = stato_av
        aggiorna_marcatore(posti.marcatore, "lettura dei dati del periodo (D2-D3), candidato " +
                           ("gia' eseguito in un tentativo interrotto" if eseguito_prima else "non ancora eseguito"),
                           sha256_dati_elenco=sha_dati_elenco, n_file_dati=len(sha_dati), impronta_giro=impronta_giro,
                           sha256_dati_tentativi_precedenti=precedenti)
        # D2-D3 e preparazione: candele lette, candidato non ancora eseguito (uno STOP non scrive il risultato)
        try:
            controlli = controllo_dati(m, taglio + 1, fine)
            contesto["controllo_dati"] = controlli
            if controlli["blocchi"]:
                raise FermoSenzaRisultato("D2", "i dati del periodo non permettono il giro: " + "; ".join(controlli["blocchi"]),
                                          {"blocchi": controlli["blocchi"], "avvisi": controlli["avvisi"],
                                           "mesi": _compatto(controlli)})
            if controlli["avvisi"]:
                print("AVVISO (D3, solo riportato nel risultato):\n  " + "\n  ".join(controlli["avvisi"]), flush=True)
            prep = prepara_esame(m, fine=fine, taglio=taglio, controlli=controlli)
        except FermoSenzaRisultato as e:
            _ferma_senza_risultato(posti, e, eseguito_prima)
        except (SystemExit, Exception) as e:
            _ferma_senza_risultato(posti, FermoSenzaRisultato(
                "prima del candidato", f"{type(e).__name__}: {e}", traceback.format_exc()[-3000:],
                stato=STATO_FERMO_ERRORE), eseguito_prima)
        # D4: da qui il candidato e' eseguito e ogni fine scrive il risultato (R5)
        segna_candidato_eseguito(posti.marcatore)
        try:
            ris = esame(m, prep, fine=fine, taglio=taglio, etichetta=etichetta, n_caso=n_caso, pezzo=pezzo,
                        avanzamento=posti.avanzamento, regole=regole, contesto=contesto, processi=processi,
                        impronta_giro=impronta_giro, ferma_dopo_pezzi=ferma_dopo_pezzi)
        except Fermo as e:
            print(f"FERMO: {e.motivo}", flush=True)
            ris = risultato_fermo(e, base)
        except (SystemExit, Exception) as e:
            print(f"FERMO: {type(e).__name__}: {e}", flush=True)
            ris = risultato_fermo(Fermo(f"STOP inatteso: {type(e).__name__}: {e}", traceback.format_exc()[-6000:]), base)
        if dopo_esame is not None:
            try:
                dopo_esame(ris)
            except Exception as e:  # pragma: no cover
                ris["dopo_esame_errore"] = f"{type(e).__name__}: {e}"
        completa_risultato(ris, m, sha_l=sha_l, regole=regole, n_caso=n_caso, impronta_avvio=impronta_avvio,
                           sha_avvio=sha_avvio, impronta_giro=impronta_giro, guardia=guardia, posti=posti)
        dest = scrivi_risultato(ris, posti, titolo)
    return ris, dest


def stampa_esito(ris: dict, dest: Path, extra: dict | None = None) -> None:
    ca = ris.get("caso") or {}
    cr = ris.get("criterio_vault") or {}
    out = {"esito": ris.get("esito"), "motivo": ris.get("motivo"), "condizioni": cr.get("condizioni"),
           "valori": cr.get("valori"), "tasso_del_caso": ca.get("tasso_del_caso"), "p90": ca.get("percentile_90"),
           "condizioni_passate_dalle_simulazioni": ca.get("condizioni_passate_dalle_simulazioni"),
           "gemella": ca.get("gemella_uguale_alla_b_sui_semi_comuni"),
           "controllo_dati_ok": (ris.get("note") or {}).get("controllo_dati_ok"),
           "avvisi_dati_D3": (ris.get("note") or {}).get("avvisi_dati"),
           "tempi": ris.get("tempi_secondi"), "risultato": str(dest)}
    if extra:
        out.update(extra)
    print(json.dumps(pulito(out), ensure_ascii=False, indent=1))


# ---------------------------------------------------------------------------
# Modo prova-vault (sul periodo di validazione, o su un pezzo dell'in-sample)
# ---------------------------------------------------------------------------


def cmd_prova_vault(args) -> int:
    m = carica_moduli(Path(args.worktree))
    cartella = Path(args.cartella).resolve()
    etichetta = "prova_validazione"
    posti = posti_prova(cartella, etichetta)
    rifiuta_se_fatto(posti)
    codice = controlla_codice(m.worktree)
    regole = leggi_regole_esame(m)
    n_caso = args.n_caso if args.n_caso is not None else regole["simulazioni_caso"]
    if n_caso < 1:
        raise SystemExit("--n-caso deve essere almeno 1")
    fine = date.fromisoformat(args.fine) if args.fine else FINE_IN_SAMPLE
    if fine > FINE_IN_SAMPLE:
        raise SystemExit("STOP: la prova si fa solo sull'in-sample (fine entro il 2023-12-31)")
    taglio = (m.dati.ms_da_data(date.fromisoformat(args.dal)) - 1) if args.dal else m.comune.FINE_COSTRUZIONE_TS
    if taglio + 1 > m.dati.ms_da_data(fine):
        raise SystemExit("STOP: --dal deve venire entro --fine")
    dati_is = prepara_insample(m, scarica=not args.senza_scarico)
    if not dati_is["uguali"]:
        raise SystemExit(f"STOP: impronte in-sample diverse: {dati_is['differenze']}")
    sha_is = sha256_dati_insample(m)
    contesto = {"codice": codice, "dati_insample": dati_is,
                "nota": "PROVA sul periodo di validazione (in-sample), non e' il vault; APERTURA.md non si legge"}
    periodo_della_validazione = not args.dal and not args.fine

    def dopo_esame(ris):
        if not periodo_della_validazione or "come_validazione" not in ris:
            return
        val_log = [v for v in _voci_log(m.worktree / FILE_LOG) if v["id"] == ID_VAL and v["tipo"] == "risultato"][-1]
        attesi = {k: v for k, v in val_log.items() if k in ris["come_validazione"]}
        ris["confronto_con_la_validazione_del_log"] = confronta(attesi, ris["come_validazione"])
        ris["confronto_con_la_validazione_del_log_oltre_1e-12_relativo"] = confronta(attesi, ris["come_validazione"],
                                                                                    tolleranza_rel=1e-12)
        ris["campi_della_validazione_confrontati"] = sorted(attesi)

    inizio_periodo = datetime.fromtimestamp((taglio + 1) / 1000, tz=timezone.utc).date()

    def prepara_prova() -> dict:  # D1 sui mesi del periodo di prova (file in-sample, gia' verificati)
        d1 = controlla_file_mensili(m, inizio_periodo, fine)
        return {"file": d1["file_presenti_e_leggibili"], "sha256": d1["sha256"],
                "D1": {k: v for k, v in d1.items() if k != "sha256"},
                "nota": "prova: i file del periodo sono in-sample, gia' verificati con le impronte della campagna"}

    ris, dest = giro(m, posti=posti, etichetta=etichetta, fine=fine, taglio=taglio, n_caso=n_caso, pezzo=args.pezzo,
                     regole=regole, codice=codice, contesto=contesto, sha_apertura=None, sha_insample=sha_is,
                     prepara_periodo=prepara_prova, processi=args.processi,
                     titolo="PROVA del lanciatore del vault sull'in-sample (non è il vault)",
                     ferma_dopo_pezzi=args.ferma_dopo_pezzi, dopo_esame=dopo_esame)
    stampa_esito(ris, dest, {
        "differenze_con_la_validazione": ris.get("confronto_con_la_validazione_del_log"),
        "differenze_oltre_1e-12": ris.get("confronto_con_la_validazione_del_log_oltre_1e-12_relativo")})
    return 0


# ---------------------------------------------------------------------------
# Modo vault (solo dopo l'apertura)
# ---------------------------------------------------------------------------


def cmd_vault(args) -> int:
    wt = Path(args.worktree).resolve()
    if wt != WORKTREE_DEFAULT.resolve():
        raise SystemExit(f"STOP: il modo vault gira solo sul worktree {WORKTREE_DEFAULT}, non su {wt}")
    m = carica_moduli(wt)
    # 1) R4, PRIMA DI TUTTO: l'apertura del coordinamento. Finche' manca: VaultChiuso, senza scrivere nulla.
    ap = leggi_apertura(m, APERTURA_COORD)
    posti = posti_vault(m)
    rifiuta_se_fatto(posti)  # R2 (il marcatore si controlla dopo, con l'impronta d'avvio)
    if m.dati.ms_da_data(INIZIO_VAULT) - 1 != TAGLIO_VAULT_TS or m.dati.FINE_VAULT != FINE_VAULT:
        raise SystemExit("STOP: le date del vault di dati.py non sono quelle del lanciatore")
    codice = controlla_codice(m.worktree)
    regole = leggi_regole_esame(m)
    n_caso = regole["simulazioni_caso"]
    if (0, n_caso - 1) != SEMI_CASO:
        raise SystemExit(f"STOP: simulazioni_caso {n_caso} non corrisponde ai semi {SEMI_CASO} scritti in APERTURA.md")
    # 2) la copia di APERTURA.md accanto al dati.py del candidato si fa nel giro, DOPO il controllo del
    #    marcatore (prepara_vault); qui solo un controllo in lettura: una copia gia' presente e diversa
    #    ferma tutto prima di scrivere qualunque file
    copia = m.worktree / APERTURA_REL_WORKTREE
    if (copia.exists() or copia.is_symlink()) and (copia.is_symlink() or not copia.is_file()
                                                   or copia.read_bytes() != ap["grezzo"]):
        raise SystemExit(f"STOP (R4): {copia} esiste ma non e' uguale byte per byte a {ap['sorgente']}")
    apertura = {k: v for k, v in ap.items() if k != "grezzo"}
    # 3) in-sample: riscarico se manca e impronte della campagna
    dati_is = prepara_insample(m, scarica=not args.senza_scarico)
    if not dati_is["uguali"]:
        raise SystemExit(f"STOP: impronte in-sample diverse: {dati_is['differenze']}")
    sha_is = sha256_dati_insample(m)
    contesto = {"codice": codice, "dati_insample": dati_is, "apertura": apertura}
    ris, dest = giro(m, posti=posti, etichetta="vault", fine=FINE_VAULT, taglio=TAGLIO_VAULT_TS, n_caso=n_caso,
                     pezzo=PEZZO_DEFAULT, regole=regole, codice=codice, contesto=contesto, sha_apertura=ap["sha256"],
                     sha_insample=sha_is, prepara_periodo=lambda: prepara_vault(m, not args.senza_scarico, ap),
                     processi=args.processi, titolo=f"Vault di {CANDIDATO} (Passo 5)")
    stampa_esito(ris, dest)
    return 0


def cmd_requisiti_apertura(_args) -> int:
    print(json.dumps(requisiti_apertura(), ensure_ascii=False, indent=1))
    return 0


# ---------------------------------------------------------------------------


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--worktree", default=str(WORKTREE_DEFAULT))
    ap.add_argument("--processi", type=int, default=PROCESSI_DEFAULT)
    sub = ap.add_subparsers(dest="modo", required=True)
    p1 = sub.add_parser("parita", help="solo in-sample: riscarica, verifica e rifa' costruzione e validazione")
    p1.add_argument("--uscita", required=True, help="file JSON dell'esito")
    p1.add_argument("--senza-scarico", action="store_true")
    p1.add_argument("--senza-costruzione", action="store_true")
    sub.add_parser("requisiti-apertura", aliases=["apertura"], help="cosa deve contenere APERTURA.md per questo candidato")
    p2 = sub.add_parser("prova-vault", help="lo stesso giro del vault, sull'in-sample (validazione)")
    p2.add_argument("cartella", help="cartella della prova (risultato, riassunto, marcatore, avanzamento)")
    p2.add_argument("--pezzo", type=int, default=PEZZO_DEFAULT, help="semi per file di avanzamento")
    p2.add_argument("--senza-scarico", action="store_true")
    p2.add_argument("--n-caso", type=int, default=None, help="simulazioni del caso (predefinito: parametri.yaml)")
    p2.add_argument("--ferma-sui-dati", action="store_true",
                    help="non cambia nulla: la regola dei dati D1-D4 vale sempre, come nel vault")
    p2.add_argument("--dal", default=None, help="solo in-sample: primo giorno contato (AAAA-MM-GG)")
    p2.add_argument("--fine", default=None, help="solo in-sample: ultimo giorno (AAAA-MM-GG, entro il 2023-12-31)")
    p2.add_argument("--ferma-dopo-pezzi", type=int, default=None, help=argparse.SUPPRESS)
    p3 = sub.add_parser("vault", help="il giro vero, solo dopo l'apertura; posti fissi")
    p3.add_argument("--senza-scarico", action="store_true")
    args = ap.parse_args(argv)
    if getattr(args, "pezzo", PEZZO_DEFAULT) < 1 or args.processi < 1:
        raise SystemExit("--pezzo e --processi devono essere almeno 1")
    try:
        if args.modo == "parita":
            return cmd_parita(args)
        if args.modo in ("requisiti-apertura", "apertura"):
            return cmd_requisiti_apertura(args)
        if args.modo == "prova-vault":
            return cmd_prova_vault(args)
        return cmd_vault(args)
    except FermoSenzaRisultato as e:  # D1, D2 o un errore prima del candidato (D4): codice d'uscita 4
        print(f"FERMO SENZA RISULTATO ({e.stato}): {e.regola}: {e.motivo}", file=sys.stderr)
        if isinstance(e.dettagli, dict):
            for k, v in e.dettagli.items():
                if v and k != "mesi":
                    print(f"  {k}: {v}", file=sys.stderr)
        print("Nessun risultato scritto: il vault non e' consumato. Risolto il problema, si rilancia lo stesso comando "
              "con lo stesso lanciatore.", file=sys.stderr)
        return 4
    except InterruzioneVoluta as e:
        print(f"INTERROTTO: {e}", file=sys.stderr)
        return 5
    except Exception as e:  # VaultChiuso e OltreIlVault: messaggio chiaro, codice d'uscita 3
        if type(e).__name__ in ("VaultChiuso", "OltreIlVault"):
            print(f"{type(e).__name__}: {e}", file=sys.stderr)
            return 3
        raise


if __name__ == "__main__":
    sys.exit(main())
