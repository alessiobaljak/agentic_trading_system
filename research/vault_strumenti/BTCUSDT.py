#!/usr/bin/env python3
"""Lanciatore del Passo 5 (protocollo 4.5) per il candidato BTCUSDT-V10.

Il candidato gira con il SUO codice: i moduli si importano dal worktree staccato sulla
punta del branch della campagna (``research/campagne/BTCUSDT/codice/`` e ``research/src/``
di quel worktree, commit 8634b6ac), aggiungendolo a ``sys.path`` come faceva lo script di
validazione della campagna. Qui non c'e' copia del codice del candidato: ci sono solo il
giro del vault, il tasso del caso e i controlli.

Modi
----
``parita``      (gira adesso, solo in-sample). Riscarica con ``dati.scarica_periodo`` del
                worktree le tre serie del candidato (klines 1h, markPriceKlines 1h,
                fundingRate) dal 2020-01 al 2023-12, le confronta con le impronte della
                campagna (``impronte.json``, 144 voci su 912) e si ferma se una differisce.
                Poi rifa' la validazione chiamando ``validazione.valida('V10')`` della
                campagna, con il log rediretto in memoria (il file ``log.jsonl`` non si
                tocca), e la costruzione con ``quadro.valuta_costruzione``; confronta ogni
                numero con le voci del log. Dimostra che la gemella delle entrate casuali
                (usata per il tasso del caso) da' gli stessi R medi di
                ``motore.simula_baseline_casuale`` sui semi 0..199. Misura i tempi.
``requisiti-apertura``  stampa cosa deve contenere APERTURA.md per questo candidato.
``prova-vault`` (gira adesso, solo in-sample). Esegue lo stesso codice del modo vault
                (guardia, marcatore, impronta, regola dei dati D1-D3, esame, esiti limite) sul
                periodo di VALIDAZIONE, al posto del vault, in una cartella di prova: serve a
                provarlo e a verificare che riproduce i numeri della validazione. La regola dei
                dati vale come nel vault (``--ferma-sui-dati`` resta accettato e non cambia nulla).
``vault``       (solo dopo l'apertura). Tutto a posti FISSI, qualunque siano gli argomenti:
                - legge ``/home/user/coordinamento/research/vault/APERTURA.md``; finche' manca
                  si ferma con ``VaultChiuso`` senza scrivere nulla (R4). Pretende che contenga
                  l'ID del candidato, lo SHA-256 completo di ``regole.md`` e di ogni file di
                  codice controllato contro il worktree, e i semi 0-999; poi la copia da se' in
                  ``research/vault/APERTURA.md`` del worktree (uguale byte per byte, verificata),
                  dove la cerca ``dati.controlla_vault`` del candidato;
                - una volta sola (R2): risultato ``research/vault/BTCUSDT-V10_vault.json`` e
                  marcatore ``research/vault/BTCUSDT-V10_giro_iniziato.json`` del coordinamento.
                  Il marcatore si scrive PRIMA di scaricare o caricare i dati del vault; se il
                  risultato esiste, o il marcatore e' di un giro con un'altra impronta, rifiuta.
                  Riprende solo lo STESSO giro (stesso lanciatore, codice, apertura, regole e
                  file di dati);
                - avanzamento a pezzi in ``research/vault_strumenti/avanzamento/BTCUSDT-V10/``
                  del coordinamento (R6), con un'impronta che contiene lo SHA-256 del
                  lanciatore, del codice e dei file di dati; ogni pezzo porta lo SHA-256
                  dell'impronta e la ripresa rifiuta pezzi senza impronta o di un altro giro (R3);
                - regola dei dati (D1-D4, sostituisce la vecchia R1):
                  D1. PRIMA di caricare la serie, STOP SENZA risultato se manca o non si legge
                      anche un solo file mensile 2024-01 -> 2026-09 di una serie usata (klines 1h,
                      markPriceKlines 1h, fundingRate; V10 non usa BTC come serie esterna);
                  D2. dopo il caricamento e PRIMA di eseguire il candidato, STOP SENZA risultato
                      solo se l'ultima barra allineata non e' la barra delle 23:00 del 2026-09-30,
                      o un mese ha meno del 50% delle barre allineate attese, o un mese non ha
                      nessun settlement di funding;
                  D3. tutto il resto si riporta e basta (JSON e riassunto): barre attese, last,
                      mark, allineate e quota per mese, con un AVVISO sotto il 99%; settlement di
                      funding per mese con gli intervalli osservati;
                  D4. uno STOP di D1/D2 non consuma il vault: il marcatore dice «fermo sui dati,
                      candidato non eseguito» e lo stesso giro riparte con lo stesso lanciatore
                      dopo aver risolto il problema (i file di dati si fissano per sempre solo
                      quando il candidato viene eseguito);
                - esiti (R5, solo DOPO che il candidato e' stato eseguito): «passa», «non passa»,
                  «non si sa» (sotto i trade minimi, anche 0), «non valutabile» (entrate casuali
                  non costruibili, o uno STOP dopo l'esecuzione del candidato): da li' ogni fine
                  scrive il risultato, prima il JSON e poi il riassunto .md (R6). Un'interruzione
                  (Ctrl-C, errore del codice) lascia il giro da riprendere.

Codici d'uscita: 0 risultato scritto; 2 risultato «non valutabile» per uno STOP dopo l'esecuzione
del candidato; 3 vault chiuso; 4 fermo sui dati SENZA risultato (vault non consumato).

Uso
---
    python3 -I BTCUSDT.py parita --uscita /percorso/vault_parita_BTCUSDT.json
    python3 -I BTCUSDT.py requisiti-apertura      (oppure: apertura)
    python3 -I BTCUSDT.py prova-vault /cartella/di/prova [--n-caso 1000] [--ferma-sui-dati]
    python3 -I BTCUSDT.py vault

Opzioni: ``--worktree`` (predefinito /home/user/vault_BTCUSDT; nel modo vault solo quello),
``--pezzo`` (semi per file di avanzamento, 50), ``--avanzamento`` (solo per la prova),
``--senza-scarico``.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import platform
import re
import subprocess
import sys
import time
import zipfile
from collections import Counter
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from types import SimpleNamespace

sys.dont_write_bytecode = True  # niente __pycache__ nel worktree della campagna

SIMBOLO = "BTCUSDT"
VID = "V10"
CANDIDATO = f"{SIMBOLO}-{VID}"
WORKTREE_DEFAULT = Path("/home/user/vault_BTCUSDT")
COMMIT_ATTESO = "8634b6ac11fd80a92341b966c1a29684c6588b8a"

# Posti FISSI del modo vault (R2, R4, R6): non dipendono dagli argomenti.
COORD_RICERCA = Path("/home/user/coordinamento/research")
VAULT_COORD = COORD_RICERCA / "vault"
APERTURA_COORD = VAULT_COORD / "APERTURA.md"
RISULTATO_VAULT = VAULT_COORD / f"{CANDIDATO}_vault.json"
RIASSUNTO_VAULT = VAULT_COORD / f"{CANDIDATO}_vault.md"
MARCATORE_VAULT = VAULT_COORD / f"{CANDIDATO}_giro_iniziato.json"
AVANZAMENTO_VAULT = COORD_RICERCA / "vault_strumenti" / "avanzamento" / CANDIDATO
APERTURA_REL_WORKTREE = "research/vault/APERTURA.md"
SEMI_CASO_VAULT = (0, 999)

# Regola dei dati (D1-D4, sostituisce la vecchia R1, uguale per i tre lanciatori)
TF = "1h"  # il timeframe del candidato (controllato contro varianti.TUTTE[VID]().tf)
SOGLIA_AVVISO_BARRE = 0.99  # D3: sotto questa quota di barre allineate un mese ha un AVVISO (solo riportato)
SOGLIA_BLOCCO_BARRE = 0.50  # D2: sotto questa quota il giro si ferma SENZA risultato
STATO_FERMO_DATI = "fermo sui dati, candidato non eseguito"
STATO_FERMO_DATI_DOPO = ("fermo sui dati, candidato gia' eseguito in un tentativo interrotto: "
                         "si riprende solo con gli stessi file")

# SHA-256 dei file del candidato alla punta 8634b6ac (analisi preparatoria, ricontrollati
# l'11 ott 2026 sul worktree): sono quelli da scrivere in APERTURA.md.
FILE_ATTESI = {
    "research/campagne/BTCUSDT/candidati/V10/regole.md": "34ed067ea5b6d01b5e7d6e91f11e8e844b6e90e25c0d12bc3513b2ff22ca37e1",
    "research/campagne/BTCUSDT/codice/varianti.py": "6e79b249d6261731a4933fdb62f8d8b4ece6c41d7f2ea9dc965458b719d80b5e",
    "research/campagne/BTCUSDT/codice/quadro.py": "4faac8024b1e315d618b12ad325b11f0b218de6a026fb124f0ab3d066c101b06",
    "research/campagne/BTCUSDT/codice/comune.py": "5df5b8cd4f8089969e0e61c83498ca84a13ea54c622768bae7f1830ec2a67ee1",
    "research/campagne/BTCUSDT/codice/validazione.py": "350aa8d4a52c3671e79e3f02653051ab0680b63ab7020b65b2232d08b4191217",
    "research/src/motore.py": "b3d5e1a93954f5b8cad34b74937592cf2b0ade237cbcc1e789a0ee195e6b0970",
    "research/src/dati.py": "874f04ca5fec791cba3b54cd25895f52085823c22f5d067eece19abea435ef4e",
    "research/src/statistica.py": "b823dcfc5f50eb3ad6e55c23c94f02f8b0162121127752e8213e24b75046ae7f",
    "research/src/__init__.py": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    "research/__init__.py": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    "research/config/parametri.yaml": None,  # si riporta, non c'e' un valore atteso scritto prima
    "research/campagne/BTCUSDT/impronte.json": "3632020f86ec6e5c22489de4c5fee9cb85686a65bd80be1d7ebc72f81b6fd7ac",
}
FILE_REGOLE = "research/campagne/BTCUSDT/candidati/V10/regole.md"
FILE_IMPRONTE = "research/campagne/BTCUSDT/impronte.json"
# i file di codice che il lanciatore usa e controlla contro il worktree: i loro SHA-256 vanno in APERTURA.md
FILE_CODICE = tuple(rel for rel, h in FILE_ATTESI.items() if h and rel.endswith(".py"))

# Solo le serie del candidato (V10 non usa volumi, altri timeframe o altre monete).
SERIE = (("klines", "1h"), ("markPriceKlines", "1h"), ("fundingRate", None))
PREFISSI_IMPRONTE = ("klines/1h/", "markPriceKlines/1h/", "fundingRate/")
INIZIO_IN_SAMPLE = date(2020, 1, 1)
FINE_IN_SAMPLE = date(2023, 12, 31)
INIZIO_VAULT = date(2024, 1, 1)
FINE_VAULT = date(2026, 9, 30)
MS_ORA = 3_600_000
MS_GIORNO = 86_400_000

# Numeri dell'in-sample scritti dalla campagna (fase0_dati.md)
ATTESI_INSAMPLE = {"barre_last": 35_064, "barre_tolte": 192, "settlement_funding": 4_383}

PEZZO_DEFAULT = 50
ID_VAL = f"{CANDIDATO}-VAL"


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
    """Rende serializzabile in JSON standard: numpy -> python, inf/nan -> stringhe."""
    try:
        import numpy as np
    except ImportError:  # pragma: no cover
        np = None
    if isinstance(x, dict):
        return {str(k): pulito(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [pulito(v) for v in x]
    if np is not None:
        if isinstance(x, np.ndarray):
            return [pulito(v) for v in x.tolist()]
        if isinstance(x, np.generic):
            x = x.item()
    if isinstance(x, float):
        if math.isnan(x):
            return "nan"
        if math.isinf(x):
            return "inf" if x > 0 else "-inf"
        return x
    if isinstance(x, (date, datetime)):
        return x.isoformat()
    if isinstance(x, Path):
        return str(x)
    return x


def scrivi_json(p: Path, dati_json) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.with_name(p.name + ".parziale")
    tmp.write_text(json.dumps(pulito(dati_json), ensure_ascii=False, indent=1, allow_nan=False) + "\n", encoding="utf-8")
    os.replace(tmp, p)


def scrivi_testo(p: Path, testo: str) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.with_name(p.name + ".parziale")
    tmp.write_text(testo, encoding="utf-8")
    os.replace(tmp, p)


def confronta(atteso, trovato, percorso: str = "", tolleranza_rel: float = 0.0) -> list:
    """Differenze fra due strutture JSON (dopo il giro JSON): lista vuota = identiche.

    Con ``tolleranza_rel`` > 0 due numeri non interi si considerano uguali se differiscono
    meno di quella frazione (serve solo a separare le differenze in virgola mobile, di
    pochi ulp, da quelle vere: la parita' esatta si giudica sempre con tolleranza 0).
    """
    diff = []
    if isinstance(atteso, dict) and isinstance(trovato, dict):
        for k in sorted(set(atteso) | set(trovato)):
            p = f"{percorso}.{k}" if percorso else str(k)
            if k not in atteso:
                diff.append(f"{p}: in piu' nel rifatto ({trovato[k]!r})")
            elif k not in trovato:
                diff.append(f"{p}: manca nel rifatto (atteso {atteso[k]!r})")
            else:
                diff += confronta(atteso[k], trovato[k], p, tolleranza_rel)
        return diff
    if isinstance(atteso, list) and isinstance(trovato, list):
        if len(atteso) != len(trovato):
            return [f"{percorso}: lunghezza {len(atteso)} attesa, {len(trovato)} trovata"]
        for i, (a, b) in enumerate(zip(atteso, trovato)):
            diff += confronta(a, b, f"{percorso}[{i}]", tolleranza_rel)
        return diff
    if isinstance(atteso, bool) or isinstance(trovato, bool):
        if atteso is not trovato:
            diff.append(f"{percorso}: atteso {atteso!r}, trovato {trovato!r}")
        return diff
    if isinstance(atteso, (int, float)) and isinstance(trovato, (int, float)):
        if atteso != trovato:
            if (tolleranza_rel > 0 and (isinstance(atteso, float) or isinstance(trovato, float))
                    and abs(trovato - atteso) <= tolleranza_rel * max(abs(atteso), abs(trovato))):
                return diff
            diff.append(f"{percorso}: atteso {atteso!r}, trovato {trovato!r} (differenza {trovato - atteso:+.3g})")
        return diff
    if atteso != trovato:
        diff.append(f"{percorso}: atteso {atteso!r}, trovato {trovato!r}")
    return diff


def giro_json(m, x):
    """Lo stesso passaggio che fa ``comune.aggiungi_log`` prima di scrivere nel log."""
    return json.loads(json.dumps(x, ensure_ascii=False, default=m.comune._json_default))


# ---------------------------------------------------------------------------
# Il codice del candidato
# ---------------------------------------------------------------------------


def carica_moduli(worktree: Path) -> SimpleNamespace:
    """Importa il codice del candidato dal SUO worktree (sys.path), senza copiarlo."""
    worktree = worktree.resolve()
    codice = worktree / "research" / "campagne" / SIMBOLO / "codice"
    if not codice.is_dir():
        raise SystemExit(f"STOP: manca il codice del candidato in {codice}")
    for p in (str(codice), str(worktree)):
        while p in sys.path:
            sys.path.remove(p)
    sys.path[:0] = [str(codice), str(worktree)]
    for nome in ("research", "research.src", "comune", "quadro", "varianti", "validazione"):
        if nome in sys.modules:
            raise SystemExit(f"STOP: il modulo {nome} era gia' importato da un'altra parte")
    import comune  # noqa: E402  (mette RADICE_REPO = worktree in sys.path)
    import quadro  # noqa: E402
    import varianti  # noqa: E402
    import validazione  # noqa: E402  (nessun effetto all'import: il main e' protetto)
    from research.src import dati, motore, statistica  # noqa: E402
    import numpy as np  # noqa: E402
    import yaml  # noqa: E402

    for mod in (comune, quadro, varianti, validazione, dati, motore, statistica):
        f = Path(mod.__file__).resolve()
        if worktree not in f.parents:
            raise SystemExit(f"STOP: {mod.__name__} viene da {f}, non dal worktree {worktree}")
    if Path(comune.RADICE_REPO).resolve() != worktree:
        raise SystemExit(f"STOP: comune.RADICE_REPO = {comune.RADICE_REPO}, atteso {worktree}")
    if Path(dati.RADICE_DEFAULT).resolve() != worktree / "research":
        raise SystemExit(f"STOP: dati.RADICE_DEFAULT = {dati.RADICE_DEFAULT}, atteso {worktree / 'research'}")

    # Nessuna scrittura nel log della campagna da questo lanciatore.
    def _vietato(*_a, **_k):
        raise RuntimeError("il lanciatore non scrive mai nel log della campagna")
    comune.aggiungi_log = _vietato
    validazione.aggiungi_log = _vietato

    return SimpleNamespace(comune=comune, quadro=quadro, varianti=varianti, validazione=validazione,
                           dati=dati, motore=motore, statistica=statistica, np=np, yaml=yaml,
                           worktree=worktree, codice=codice)


def _git(worktree: Path, *argomenti) -> str:
    r = subprocess.run(["git", "-C", str(worktree), *argomenti], capture_output=True, text=True, check=True)
    return r.stdout.strip()


def controlla_codice(worktree: Path, fermati: bool = True) -> dict:
    """Commit della punta, nessuna modifica ai file tracciati, SHA-256 dei file del candidato."""
    commit = _git(worktree, "rev-parse", "HEAD")
    modificati = [r for r in _git(worktree, "status", "--porcelain", "--untracked-files=no").splitlines() if r.strip()]
    file_ = {}
    problemi = []
    for rel, atteso in FILE_ATTESI.items():
        p = worktree / rel
        trovato = sha256_file(p) if p.is_file() else None
        file_[rel] = {"sha256": trovato, "atteso": atteso,
                      "uguale": (trovato == atteso) if atteso else None}
        if atteso and trovato != atteso:
            problemi.append(f"{rel}: sha256 {trovato} diverso da {atteso}")
    if commit != COMMIT_ATTESO:
        problemi.append(f"commit del worktree {commit}, atteso {COMMIT_ATTESO}")
    if modificati:
        problemi.append(f"file tracciati modificati nel worktree: {modificati}")
    esito = {"commit": commit, "commit_atteso": COMMIT_ATTESO, "file_tracciati_modificati": modificati,
             "file": file_, "problemi": problemi, "ok": not problemi}
    if problemi and fermati:
        raise SystemExit("STOP: il codice del candidato non e' quello congelato:\n  " + "\n  ".join(problemi))
    return esito


def leggi_regole_esame(m) -> dict:
    """I valori del criterio del vault da research/config/parametri.yaml del worktree."""
    y = m.yaml.safe_load((m.worktree / "research" / "config" / "parametri.yaml").read_text(encoding="utf-8"))
    re_ = y["regole_esame"]
    cv = re_["criterio_vault"]
    out = {
        "stato_parametri": y.get("stato"),
        "pf_minimo": float(cv["profit_factor_minimo"]),
        "trade_minimi": int(cv["trade_minimi"]),
        "rendimento_totale_positivo": bool(cv["rendimento_totale_positivo"]),
        "percentile_caso": float(cv["r_medio_sopra_percentile_caso"]),
        "simulazioni_caso": int(re_["simulazioni_caso"]),
        "simulazioni_baseline_casuale": int(re_["simulazioni_baseline_casuale"]),
        "semi_baseline_casuale": dict(re_["semi_baseline_casuale"]),
        "trade_minimi_vault": int(re_["trade_minimi"]["vault"]),
        "bootstrap": dict(re_["bootstrap"]),
    }
    if out["trade_minimi"] != out["trade_minimi_vault"]:
        raise SystemExit("STOP: criterio_vault.trade_minimi diverso da trade_minimi.vault in parametri.yaml")
    if not out["rendimento_totale_positivo"]:
        raise SystemExit("STOP: parametri.yaml non chiede il rendimento positivo, ma criterio_vault lo applica sempre")
    if out["bootstrap"] != {"ricampionamenti": 2000, "seme": 0}:
        raise SystemExit("STOP: il bootstrap di parametri.yaml non e' quello predefinito di contro_baseline (2000, 0)")
    # i parametri del motore la campagna li scrive in comune.parametri(): si confrontano con lo yaml
    par = m.comune.parametri()
    fa, rd = y["fatti"], y["fatti"]["regole_dimensione_bot"]
    coppie = {
        "commissione_per_lato": (fa["commissione_taker_per_lato"]["valore"], par.commissione_per_lato),
        "rischio_per_trade": (rd["rischio_per_trade"], par.rischio_per_trade),
        "leva_max": (rd["leva_max"], par.leva_max),
        "modalita_margine": (rd["modalita_margine_proposta"], par.modalita_margine),
        "tasso_margine_mantenimento": (rd["tasso_margine_mantenimento"], par.tasso_margine_mantenimento),
        "capitale_iniziale": (rd["capitale_iniziale"], par.capitale_iniziale),
        "margine_minimo_da_liquidazione": (re_["margine_minimo_da_liquidazione"], par.margine_minimo_da_liquidazione),
        "riempimento_intrabarra": (re_["riempimento_intrabarra"], par.riempimento_intrabarra),
    }
    out["parametri_motore_contro_yaml"] = {k: {"yaml": a_, "motore": b_, "uguale": a_ == b_} for k, (a_, b_) in coppie.items()}
    out["parametri_motore_uguali_allo_yaml"] = all(v["uguale"] for v in out["parametri_motore_contro_yaml"].values())
    return out


# ---------------------------------------------------------------------------
# Dati
# ---------------------------------------------------------------------------


def impronte_attese(m) -> dict:
    p = m.worktree / FILE_IMPRONTE
    if sha256_file(p) != FILE_ATTESI[FILE_IMPRONTE]:
        raise SystemExit(f"STOP: {p} non e' quello scritto in fase0_dati.md")
    tutte = json.loads(p.read_text(encoding="utf-8"))
    attese = {k: v for k, v in tutte.items() if k.startswith(PREFISSI_IMPRONTE)}
    if len(attese) != 144:
        raise SystemExit(f"STOP: attese 144 impronte per le tre serie del candidato, trovate {len(attese)}")
    return {"tutte": len(tutte), "attese": attese}


def prepara_insample(m, scarica: bool) -> dict:
    """Riscarica (se mancano) e verifica i 144 file in-sample del candidato."""
    imp = impronte_attese(m)
    m.dati.azzera_checksum_mancanti()
    scaricati = {}
    t0 = time.perf_counter()
    if scarica:
        for tipo, tf in SERIE:
            gia = sum(1 for a, me in m.dati.mesi_del_periodo(INIZIO_IN_SAMPLE, FINE_IN_SAMPLE)
                      if m.dati.percorso_mese(SIMBOLO, tipo, tf, a, me).is_file())
            percorsi = m.dati.scarica_periodo(SIMBOLO, tipo, tf, INIZIO_IN_SAMPLE, FINE_IN_SAMPLE)
            scaricati[f"{tipo}/{tf}" if tf else tipo] = {"presenti_prima": gia, "presenti_dopo": len(percorsi)}
    secondi = time.perf_counter() - t0
    differenze = m.dati.verifica_impronte(SIMBOLO, m.dati.RADICE_DEFAULT, imp["attese"])
    esito = {"impronte_nel_file": imp["tutte"], "impronte_confrontate": len(imp["attese"]),
             "differenze": differenze, "uguali": not differenze, "scarico": scaricati,
             "checksum_mancanti": list(m.dati.CHECKSUM_MANCANTI), "secondi_scarico": round(secondi, 1),
             "sha256_impronte_json": FILE_ATTESI[FILE_IMPRONTE]}
    if differenze:
        raise SystemExit("STOP: i dati in-sample riscaricati non sono quelli della campagna:\n  "
                         + "\n  ".join(differenze))
    return esito


def descrivi_serie(m, fine: date, da_ts: int) -> dict:
    """Conta barre e buchi della serie del candidato, con la regola last/mark della campagna."""
    last = m.dati.carica_candele(SIMBOLO, "1h", m.comune.PRIMO_GIORNO, fine)
    mark = m.dati.carica_candele(SIMBOLO, "1h", m.comune.PRIMO_GIORNO, fine, tipo="markPriceKlines")
    candele, mark_al, funding = m.quadro.carica("1h", fine)
    nel = [c for c in candele if c.ts >= da_ts]
    giorni = {}
    for c in nel:
        giorni[c.ts // MS_GIORNO] = giorni.get(c.ts // MS_GIORNO, 0) + 1
    primo_g, ultimo_g = da_ts // MS_GIORNO, m.dati.ms_da_data(fine) // MS_GIORNO
    attese = (ultimo_g - primo_g + 1) * 24
    corti = sorted(g for g in range(primo_g, ultimo_g + 1) if giorni.get(g, 0) != 24)
    return {
        "fine": fine.isoformat(),
        "barre_last_tutte": len(last), "barre_mark_tutte": len(mark), "barre_comuni_tutte": len(candele),
        "barre_tolte_tutte": len(last) - len(candele),
        "nel_periodo": {
            "da": datetime.fromtimestamp(da_ts / 1000, tz=timezone.utc).isoformat(),
            "barre_attese": attese,
            "barre_last": sum(1 for c in last if c.ts >= da_ts),
            "barre_mark": sum(1 for c in mark if c.ts >= da_ts),
            "barre_comuni": len(nel),
            "giorni_senza_24_barre_comuni": [datetime.fromtimestamp(g * MS_GIORNO / 1000, tz=timezone.utc).date().isoformat()
                                             for g in corti],
            "settlement_funding": sum(1 for t, _ in funding if t >= da_ts),
        },
        "settlement_funding_tutti": len(funding),
        "prima_barra": datetime.fromtimestamp(candele[0].ts / 1000, tz=timezone.utc).isoformat() if candele else None,
        "ultima_barra": datetime.fromtimestamp(candele[-1].ts / 1000, tz=timezone.utc).isoformat() if candele else None,
        "buchi_nella_serie": m.motore._verifica_serie(candele),
    }


def _rel_dati(m, p: Path) -> str:
    """Il nome di un file mensile relativo a ``data/<insample|vault>/<SIMBOLO>`` (come impronte.json)."""
    for area in ("vault", "insample"):
        base = m.dati.RADICE_DEFAULT / "data" / area / SIMBOLO
        if base in p.parents:
            return p.relative_to(base).as_posix()
    return p.as_posix()


def controlla_file_mensili(m, inizio: date, fine: date, errori_scarico=None) -> dict:
    """D1: ogni file mensile del periodo delle serie usate (``SERIE``) deve esserci e leggersi.

    Si fa PRIMA di caricare la serie, in due passate su tutti i file:
    1. esistenza e zip (nessuna riga letta): ``testzip`` (CRC di ogni membro) e un solo .csv;
    2. lettura con il lettore del candidato (``candele_da_zip`` / ``funding_da_zip``), che e' lo
       stesso del caricamento: si contano solo le righe, nessun valore si usa o si riporta.
    Se un file manca o non si legge solleva ``FermoSuiDati`` (nessun risultato, vault non
    consumato). Ritorna l'impronta SHA-256 e il numero di righe di ogni file.
    """
    file_ = []
    for tipo, tf in SERIE:
        for a, me in m.dati.mesi_del_periodo(inizio, fine):
            p = m.dati.percorso_mese(SIMBOLO, tipo, tf, a, me)
            file_.append((tipo, _rel_dati(m, p), p))
    mancanti, illeggibili = [], []
    for _tipo, rel, p in file_:  # 1) esistenza e zip
        if not p.is_file():
            mancanti.append(rel)
            continue
        try:
            with zipfile.ZipFile(p) as z:
                rotto = z.testzip()
                csv_ = [n for n in z.namelist() if n.lower().endswith(".csv")]
            if rotto is not None:
                illeggibili.append(f"{rel}: il membro {rotto} non passa il controllo CRC")
            elif len(csv_) != 1:
                illeggibili.append(f"{rel}: attesi un solo .csv nello zip, trovati {csv_}")
        except Exception as e:  # zip rotto, file illeggibile: e' un dato che non si legge
            illeggibili.append(f"{rel}: {type(e).__name__}: {e}")
    righe, impronte = {}, {}
    if not mancanti and not illeggibili:
        for tipo, rel, p in file_:  # 2) lettura con il lettore del candidato (solo il numero di righe)
            try:
                letto = m.dati.funding_da_zip(p) if tipo == "fundingRate" else m.dati.candele_da_zip(p)
            except Exception as e:
                illeggibili.append(f"{rel}: {type(e).__name__}: {e}")
                continue
            righe[rel] = len(letto)
            impronte[rel] = sha256_file(p)
    esito = {"periodo": [inizio.isoformat(), fine.isoformat()], "file_attesi": len(file_),
             "file_presenti": len(file_) - len(mancanti), "mancanti": mancanti, "illeggibili": illeggibili,
             "errori_scarico": list(errori_scarico or []), "righe": righe, "impronte": impronte}
    if mancanti or illeggibili:
        raise FermoSuiDati(
            f"D1: {len(mancanti)} file mensili mancanti e {len(illeggibili)} illeggibili nel periodo "
            f"{inizio.isoformat()} -> {fine.isoformat()}: il candidato non e' stato eseguito, nessun risultato",
            {"mancanti": mancanti, "illeggibili": illeggibili, "errori_scarico": list(errori_scarico or [])})
    return esito


def prepara_vault(m, scarica: bool) -> dict:
    """Scarica (a vault aperto) i file del vault che mancano, poi D1 sui 99 file mensili."""
    m.dati.azzera_checksum_mancanti()
    errori = []
    if scarica:
        for tipo, tf in SERIE:
            try:
                m.dati.scarica_periodo(SIMBOLO, tipo, tf, INIZIO_VAULT, FINE_VAULT)
            except (m.dati.VaultChiuso, m.dati.OltreIlVault):
                raise
            except Exception as e:  # rete, CHECKSUM diverso...: i file che mancano li trova D1
                errori.append(f"{tipo}/{tf or ''}: {type(e).__name__}: {e}")
    esito = controlla_file_mensili(m, INIZIO_VAULT, FINE_VAULT, errori)
    if esito["file_attesi"] != 99:
        raise SystemExit(f"STOP: attesi 99 file mensili del vault, ne elenco {esito['file_attesi']}")
    esito["checksum_mancanti"] = list(m.dati.CHECKSUM_MANCANTI)
    return esito


def prepara_insample_o_fermo(m, scarica: bool) -> dict:
    """``prepara_insample`` con i problemi dei dati in-sample (file mancanti o diversi da quelli della
    campagna, scarico fallito) trasformati in ``FermoSuiDati``: prima del candidato non consumano."""
    try:
        return prepara_insample(m, scarica)
    except (m.dati.VaultChiuso, m.dati.OltreIlVault):
        raise
    except SystemExit as e:
        raise FermoSuiDati(f"dati in-sample: {e}") from None
    except Exception as e:
        raise FermoSuiDati(f"dati in-sample, scarico: {type(e).__name__}: {e}") from None


# ---------------------------------------------------------------------------
# Metriche, gemella delle entrate casuali
# ---------------------------------------------------------------------------


def composto(trades, par) -> tuple:
    """Rendimento composto e drawdown dei trade dati, dal capitale iniziale, come ``valida``."""
    ts = sorted(trades, key=lambda t: t.ts_uscita)
    cap, picco, dd = par.capitale_iniziale, par.capitale_iniziale, 0.0
    for t in ts:
        cap += t.pnl_pct * cap
        picco = max(picco, cap)
        dd = max(dd, (picco - cap) / picco)
    return cap / par.capitale_iniziale - 1, dd


def composto_per_anno(trades) -> dict:
    out = {}
    for t in sorted(trades, key=lambda t: t.ts_uscita):
        a = str(datetime.fromtimestamp(t.ts_uscita / 1000, tz=timezone.utc).year)
        out[a] = out.get(a, 1.0) * (1 + t.pnl_pct)
    return {a: round(v - 1, 4) for a, v in out.items()}


def metriche_criterio(m, trades, par, r_medio: float) -> dict:
    """Le quattro chiavi di ``criterio_vault``, NON arrotondate."""
    rend, dd = composto(trades, par)
    return {"profit_factor": m.statistica.profit_factor([t.pnl for t in trades]), "n_trade": len(trades),
            "rendimento_totale": rend, "r_medio": r_medio, "drawdown_max": dd}


def simula_caso(m, candele, crea_casuale, n_trade, durata, par, mark, funding, vietate, semi, inizio_ts: int) -> list:
    """Gemella di ``motore.simula_baseline_casuale`` che tiene, per ogni seme, anche le
    metriche del criterio del vault (la funzione della campagna restituisce solo gli R medi).

    Riga per riga come la funzione della campagna: stesse barre vietate piu' l'ultima barra,
    ``statistica.entrate_casuali_per_semi`` con la tabella costruita una volta, una strategia
    nuova per seme con ``crea_casuale(frozenset(ingressi))``, ``motore.esegui`` con le stesse
    serie, ``candele_stop=None``, ``list(funding)``, e R medio = somma degli R / numero di trade
    nell'ordine dei trade del motore.
    """
    vietate_tutte = list(vietate) + [(len(candele) - 1, len(candele))]
    semi = list(semi)
    ingressi = m.statistica.entrate_casuali_per_semi(len(candele), n_trade, durata, semi, vietate_tutte)
    out = []
    for seme, lista in zip(semi, ingressi):
        strategia = m.motore._strategia_nuova(crea_casuale, "simula_caso", "crea_casuale(ingressi)", frozenset(lista))
        ris = m.motore.esegui(candele, None, mark, list(funding), strategia, par)
        tr = ris.trades
        r_medio = (sum(t.r for t in tr) / len(tr)) if tr else None
        mc = metriche_criterio(m, tr, par, r_medio if r_medio is not None else -math.inf)
        out.append({"seme": seme, "n_trade": len(tr), "r_medio": r_medio,
                    "profit_factor": mc["profit_factor"], "rendimento_totale": mc["rendimento_totale"],
                    "drawdown_max": mc["drawdown_max"], "segnali_non_validi": ris.n_segnali_non_validi,
                    "segnali_senza_barra": ris.n_segnali_senza_barra,
                    "trade_entrati_prima_del_periodo": sum(1 for t in tr if t.ts_entrata < inizio_ts)})
    return out


class Spia:
    """Avvolge ``motore.simula_baseline_casuale`` per leggere argomenti, risultato e tempo.

    Il comportamento non cambia: chiama la funzione originale e ne restituisce il risultato.
    """

    def __init__(self, motore):
        self.motore = motore
        self.originale = motore.simula_baseline_casuale
        self.chiamate = []

    def __enter__(self):
        def avvolta(*a, **k):
            t0 = time.perf_counter()
            r = self.originale(*a, **k)
            self.chiamate.append({"args": a, "kwargs": k, "risultato": r, "secondi": time.perf_counter() - t0})
            return r
        self.motore.simula_baseline_casuale = avvolta
        return self

    def __exit__(self, *_e):
        self.motore.simula_baseline_casuale = self.originale
        return False


def prova_gemella(m, chiamata, inizio_ts: int) -> dict:
    """Stessi argomenti della (b) della campagna, semi 0..n-1: R medi identici?"""
    a, k = chiamata["args"], chiamata["kwargs"]
    candele, crea_casuale, n_trade, durata, par, stop, mark, funding, vietate = a[:9]
    if stop is not None:
        raise SystemExit("STOP: la (b) della campagna usa candele_stop: la gemella non lo prevede")
    n_sim = int(k.get("n_simulazioni", 200))
    primo = int(k.get("primo_seme", 0))
    t0 = time.perf_counter()
    sims = simula_caso(m, candele, crea_casuale, n_trade, durata, par, mark, funding, vietate, range(primo, primo + n_sim),
                       inizio_ts)
    secondi = time.perf_counter() - t0
    gemella = [s["r_medio"] for s in sims if s["n_trade"] > 0]
    campagna = [float(x) for x in chiamata["risultato"]["valori"]]
    tps_g = [s["n_trade"] for s in sims if s["n_trade"] > 0]
    tps_c = list(chiamata["risultato"]["trade_per_simulazione"])
    uguali = gemella == campagna
    diff_max = max((abs(x - y) for x, y in zip(gemella, campagna)), default=0.0) if len(gemella) == len(campagna) else None
    return {"semi": [primo, primo + n_sim - 1], "simulazioni": n_sim, "n_trade": n_trade, "durata_media_barre": durata,
            "barre": len(candele), "r_medi_identici": uguali, "trade_per_simulazione_identici": tps_g == tps_c,
            "differenza_massima": diff_max, "media_gemella": sum(gemella) / len(gemella),
            "media_campagna": float(chiamata["risultato"]["media"]),
            "percentile_90_gemella": m.statistica.percentile(gemella, 90),
            "secondi_gemella": round(secondi, 2), "secondi_campagna": round(chiamata["secondi"], 2),
            "secondi_per_simulazione_gemella": round(secondi / n_sim, 4),
            "secondi_per_simulazione_campagna": round(chiamata["secondi"] / n_sim, 4)}


# ---------------------------------------------------------------------------
# Modo parita
# ---------------------------------------------------------------------------


def cmd_parita(args) -> int:
    t_inizio = time.perf_counter()
    m = carica_moduli(Path(args.worktree))
    codice = controlla_codice(m.worktree)
    regole_esame = leggi_regole_esame(m)
    dati_is = prepara_insample(m, scarica=not args.senza_scarico)
    serie = descrivi_serie(m, FINE_IN_SAMPLE, m.comune.PERIODI["inizio_ts"])
    problemi_serie = []
    if serie["barre_last_tutte"] != ATTESI_INSAMPLE["barre_last"]:
        problemi_serie.append(f"barre last {serie['barre_last_tutte']} invece di {ATTESI_INSAMPLE['barre_last']}")
    if serie["barre_tolte_tutte"] != ATTESI_INSAMPLE["barre_tolte"]:
        problemi_serie.append(f"barre tolte {serie['barre_tolte_tutte']} invece di {ATTESI_INSAMPLE['barre_tolte']}")
    if serie["settlement_funding_tutti"] != ATTESI_INSAMPLE["settlement_funding"]:
        problemi_serie.append(f"settlement {serie['settlement_funding_tutti']} invece di {ATTESI_INSAMPLE['settlement_funding']}")

    log = m.comune.voci_log()
    sha_log = sha256_file(m.comune.LOG)
    val_log = [v for v in log if v.get("id") == ID_VAL and v.get("tipo") == "risultato"][-1]
    reg_log = [v for v in log if v.get("id") == ID_VAL and v.get("tipo") == "registrazione"][-1]
    cos_log = [v for v in log if v.get("id") == CANDIDATO and v.get("tipo") == "risultato"][-1]

    # 1) la validazione, con la funzione della campagna e il log in memoria
    voci_senza_val = [v for v in log if v.get("id") != ID_VAL]
    catturate = []

    def voci_finte():
        return voci_senza_val + catturate

    def aggiungi_finta(voce):
        catturate.append(dict(voce))
        return voce

    vecchie = (m.validazione.voci_log, m.validazione.aggiungi_log)
    m.validazione.voci_log, m.validazione.aggiungi_log = voci_finte, aggiungi_finta
    try:
        with Spia(m.motore) as spia_val:
            t0 = time.perf_counter()
            m.validazione.valida(VID)
            secondi_validazione = time.perf_counter() - t0
    finally:
        m.validazione.voci_log, m.validazione.aggiungi_log = vecchie
    val_nuovo = [c for c in catturate if c.get("tipo") == "risultato"]
    reg_nuova = [c for c in catturate if c.get("tipo") == "registrazione"]
    if len(val_nuovo) != 1 or len(spia_val.chiamate) != 1:
        raise SystemExit("STOP: la validazione rifatta non ha prodotto un solo risultato e una sola (b)")
    val_nuovo = giro_json(m, val_nuovo[0])
    diff_val = confronta({k: v for k, v in val_log.items() if k != "data"}, val_nuovo)
    diff_val_sostanziali = confronta({k: v for k, v in val_log.items() if k != "data"}, val_nuovo, tolleranza_rel=1e-12)
    diff_reg = confronta({k: v for k, v in reg_log.items() if k != "data"}, giro_json(m, reg_nuova[0])) if reg_nuova else ["registrazione non rifatta"]

    # 2) la gemella delle entrate casuali contro la (b) della validazione (semi 0..199)
    gemella = prova_gemella(m, spia_val.chiamate[0], m.comune.PERIODI["inizio_validazione_ts"])

    # 3) la costruzione (quadro.valuta_costruzione, come prova.py)
    costruzione = None
    if not args.senza_costruzione:
        with Spia(m.motore) as spia_cos:
            t0 = time.perf_counter()
            esito_c = m.quadro.valuta_costruzione(m.varianti.TUTTE[VID]())
            secondi_c = time.perf_counter() - t0
        trovato_c = giro_json(m, esito_c)
        atteso_c = {k: v for k, v in cos_log.items() if k not in ("id", "tipo", "data", "previsione_corretta", "commento")}
        diff_c = confronta(atteso_c, trovato_c)
        diff_c_sostanziali = confronta(atteso_c, trovato_c, tolleranza_rel=1e-12)
        ch = spia_cos.chiamate[0]
        costruzione = {"differenze": diff_c, "identica": not diff_c, "differenze_oltre_1e-12_relativo": diff_c_sostanziali,
                       "secondi": round(secondi_c, 1),
                       "barre": len(ch["args"][0]), "secondi_b": round(ch["secondi"], 2),
                       "secondi_per_simulazione_b": round(ch["secondi"] / 200, 4),
                       "rifatta": {k: trovato_c.get(k) for k in ("metriche", "baseline_a", "baseline_b", "percentile_caso", "candidato")}}

    # 4) tempi e stima del vault
    ch = spia_val.chiamate[0]
    barre_val = len(ch["args"][0])
    s_sim = ch["secondi"] / 200
    barre_vault_stima = serie["barre_comuni_tutte"] + 24 * ((FINE_VAULT - INIZIO_VAULT).days + 1)
    s_sim_vault = s_sim * barre_vault_stima / barre_val
    n_sim_vault = regole_esame["simulazioni_caso"] + regole_esame["simulazioni_baseline_casuale"]
    stima = {"barre_validazione": barre_val, "secondi_per_simulazione_validazione": round(s_sim, 4),
             "barre_vault_stimate": barre_vault_stima,
             "secondi_per_simulazione_vault_stimati": round(s_sim_vault, 4),
             "simulazioni_vault": n_sim_vault,
             "minuti_simulazioni_vault_stimati": round(n_sim_vault * s_sim_vault / 60, 1),
             "nota": "stima lineare nel numero di barre (motore.esegui scorre tutte le barre dal 2020); "
                     "in piu' candidato, (a), barre vietate e tabelle delle entrate (pochi secondi ciascuno)"}

    sha_log_dopo = sha256_file(m.comune.LOG)
    controllo_dopo = controlla_codice(m.worktree, fermati=False)
    esito = {
        "candidato": CANDIDATO, "modo": "parita", "data": adesso(),
        "worktree": str(m.worktree), "codice": codice, "codice_dopo": {"ok": controllo_dopo["ok"], "problemi": controllo_dopo["problemi"]},
        "log_campagna": {"sha256_prima": sha_log, "sha256_dopo": sha_log_dopo, "intatto": sha_log == sha_log_dopo},
        "regole_esame": regole_esame,
        "dati_insample": dati_is, "serie": serie, "problemi_serie": problemi_serie,
        "validazione": {"differenze": diff_val, "identica": not diff_val,
                        "differenze_oltre_1e-12_relativo": diff_val_sostanziali, "differenze_registrazione": diff_reg,
                        "secondi": round(secondi_validazione, 1), "rifatta": val_nuovo,
                        "attesa_dal_log": {k: v for k, v in val_log.items() if k != "data"}},
        "gemella_caso": gemella,
        "costruzione": costruzione,
        "tempi": stima,
        "python": platform.python_version(), "numpy": m.np.__version__,
        "scipy": versioni(m)["scipy"], "versioni": versioni(m), "sha256_lanciatore": sha256_lanciatore(),
        "requisiti_APERTURA": requisiti_apertura(),
        "secondi_totali": round(time.perf_counter() - t_inizio, 1),
    }
    resto_ok = bool(not diff_reg and gemella["r_medi_identici"] and gemella["trade_per_simulazione_identici"]
                    and not problemi_serie and esito["log_campagna"]["intatto"] and controllo_dopo["ok"])
    esito["parita_esatta"] = bool(resto_ok and not diff_val and (costruzione is None or costruzione["identica"]))
    # differenze di pochi ulp nei numeri NON arrotondati (p.es. il p-value scritto con 17 cifre):
    # si dichiarano, ma non sono numeri diversi della consegna
    esito["parita_a_meno_della_virgola_mobile"] = bool(
        resto_ok and not diff_val_sostanziali
        and (costruzione is None or not costruzione["differenze_oltre_1e-12_relativo"]))
    scrivi_json(Path(args.uscita), esito)
    print(json.dumps(pulito({"parita_esatta": esito["parita_esatta"],
                             "parita_a_meno_della_virgola_mobile": esito["parita_a_meno_della_virgola_mobile"],
                             "differenze_validazione": diff_val,
                             "differenze_registrazione": diff_reg,
                             "differenze_costruzione": costruzione and costruzione["differenze"],
                             "gemella": {k: gemella[k] for k in ("r_medi_identici", "trade_per_simulazione_identici", "differenza_massima")},
                             "problemi_serie": problemi_serie, "tempi": stima, "uscita": args.uscita}),
                     ensure_ascii=False, indent=1))
    return 0 if esito["parita_a_meno_della_virgola_mobile"] else 1


# ---------------------------------------------------------------------------
# APERTURA.md (R4)
# ---------------------------------------------------------------------------

# I semi del tasso del caso scritti in APERTURA.md: «0-999», «0–999», «0..999», «da 0 a 999»
RE_SEMI = re.compile(r"(?<![\w.,])0\s*(?:-|–|—|‒|\.\.\.?|…|\s(?:a|fino a|to)\s)\s*999(?!\d)")


def requisiti_apertura() -> dict:
    """Cosa deve contenere APERTURA.md per questo candidato (R4)."""
    sha = {rel: FILE_ATTESI[rel] for rel in (FILE_REGOLE, *FILE_CODICE)}
    semi = f"{SEMI_CASO_VAULT[0]}-{SEMI_CASO_VAULT[1]}"
    testo = "\n".join([f"Candidato {CANDIDATO} (commit {COMMIT_ATTESO})",
                       f"Semi del tasso del caso: {semi}",
                       "SHA-256 dei file congelati:"]
                      + [f"- {h}  {rel}" for rel, h in sha.items()]) + "\n"
    return {"id": CANDIDATO, "sha256": sha, "semi": semi,
            "dove": str(APERTURA_COORD),
            "copia_nel_worktree": str(WORKTREE_DEFAULT / APERTURA_REL_WORKTREE),
            "testo_minimo": testo,
            "nota": "lo SHA-256 va scritto per intero (64 cifre esadecimali); i due __init__.py sono file vuoti "
                    "e hanno lo SHA-256 del file vuoto. Il testo_minimo contiene tutto cio' che il lanciatore "
                    "pretende; APERTURA.md puo' contenere altro (data, ora, altri candidati)."}


def controlla_apertura(m, sorgente: Path, copia: Path) -> dict:
    """R4. Legge l'APERTURA.md del coordinamento e pretende che contenga l'ID del candidato,
    lo SHA-256 completo di regole.md e di ogni file di codice controllato contro il worktree,
    e i semi 0-999. Poi la copia da se' accanto al ``dati.py`` del candidato (dove la cerca
    ``dati.controlla_vault``), se non c'e', e verifica che la copia sia uguale byte per byte.

    Finche' la sorgente manca (o e' vuota) solleva ``VaultChiuso`` senza scrivere nulla.
    """
    try:
        grezzo = sorgente.read_bytes()
    except FileNotFoundError:
        raise m.dati.VaultChiuso(f"manca {sorgente}: il vault e' chiuso") from None
    testo = grezzo.decode("utf-8", errors="replace")
    if not testo.strip():
        raise m.dati.VaultChiuso(f"{sorgente} e' vuoto: non e' un'apertura")
    basso = testo.lower()
    mancano = []
    if re.search(rf"(?<![A-Za-z0-9]){re.escape(CANDIDATO)}(?![A-Za-z0-9])", testo) is None:
        mancano.append(f"l'ID del candidato {CANDIDATO}")
    hash_trovati = {}
    for rel, h in requisiti_apertura()["sha256"].items():
        hash_trovati[rel] = re.search(rf"(?<![0-9a-f]){h}(?![0-9a-f])", basso) is not None
        if not hash_trovati[rel]:
            mancano.append(f"lo SHA-256 completo di {rel} ({h})")
    semi = RE_SEMI.search(testo)
    if semi is None:
        mancano.append(f"i semi {SEMI_CASO_VAULT[0]}-{SEMI_CASO_VAULT[1]} del tasso del caso")
    if mancano:
        raise SystemExit(f"STOP: {sorgente} non contiene:\n  " + "\n  ".join(mancano))
    if copia.exists():
        if not copia.is_file() or copia.read_bytes() != grezzo:
            raise SystemExit(f"STOP: {copia} esiste ma non e' uguale byte per byte a {sorgente}")
        stato_copia = "gia' presente, uguale byte per byte"
    else:
        copia.parent.mkdir(parents=True, exist_ok=True)
        tmp = copia.with_name(copia.name + ".parziale")
        tmp.write_bytes(grezzo)
        os.replace(tmp, copia)
        if copia.read_bytes() != grezzo:
            raise SystemExit(f"STOP: la copia {copia} appena scritta non e' uguale byte per byte a {sorgente}")
        stato_copia = "copiata dal lanciatore, uguale byte per byte (verificato)"
    return {"sorgente": str(sorgente), "copia": str(copia), "sha256": hashlib.sha256(grezzo).hexdigest(),
            "sha256_copia": sha256_file(copia), "byte": len(grezzo), "id_trovato": True,
            "hash_trovati": hash_trovati, "semi_trovati": semi.group(0), "copia_stato": stato_copia}


# ---------------------------------------------------------------------------
# Guardia «una volta sola», marcatore e avanzamento (R2, R3)
# ---------------------------------------------------------------------------


class Fermo(Exception):
    """Uno STOP voluto durante il giro.

    DOPO che il candidato e' stato eseguito non esce mai senza traccia: chi lo prende scrive il
    risultato, con esito «non valutabile» e il motivo (R5). PRIMA dell'esecuzione del candidato
    ``esegui_giro`` lo trasforma in ``FermoSuiDati`` (nessun risultato, D4). ``parziale`` e' il
    risultato costruito fin li' (con le metriche del candidato, se il candidato ha gia' girato).
    """

    def __init__(self, motivo: str, dettagli=None, parziale=None):
        super().__init__(motivo)
        self.motivo = motivo
        self.dettagli = dettagli
        self.parziale = parziale


class FermoSuiDati(Exception):
    """D1/D2 (e ogni altro STOP voluto prima che il candidato sia eseguito): il giro si ferma SENZA
    scrivere un risultato. Il vault non e' consumato (D4): il marcatore registra «fermo sui dati,
    candidato non eseguito» col motivo, e lo stesso giro riparte con lo stesso lanciatore dopo aver
    risolto il problema."""

    def __init__(self, motivo: str, dettagli=None, controllo_dati=None):
        super().__init__(motivo)
        self.motivo = motivo
        self.dettagli = dettagli
        self.controllo_dati = controllo_dati


def sha256_json(x) -> str:
    return sha256_testo(json.dumps(pulito(x), ensure_ascii=False, sort_keys=True, separators=(",", ":")))


def sha256_lanciatore() -> str:
    return sha256_file(Path(__file__).resolve())


def versioni(m) -> dict:
    try:
        import scipy  # noqa: E402
        v_scipy = scipy.__version__
    except ImportError:  # pragma: no cover
        v_scipy = None
    return {"python": platform.python_version(), "numpy": m.np.__version__, "scipy": v_scipy,
            "piattaforma": platform.platform(), "macchina": platform.machine()}


def versioni_per_impronta(m) -> dict:
    """D5: le versioni che entrano nell'impronta del giro."""
    v = versioni(m)
    return {"python": v["python"], "numpy": v["numpy"], "scipy": v["scipy"]}


def controlla_semi(regole_esame: dict) -> None:
    n_b = regole_esame["simulazioni_baseline_casuale"]
    if regole_esame["semi_baseline_casuale"] != {"primo": 0, "ultimo": n_b - 1}:
        raise SystemExit("STOP: semi della (b) diversi da 0..199 in parametri.yaml")


def impronta_di_avvio(*, etichetta: str, sha_l: str, codice: dict, sha_apertura, regole_esame: dict, n_caso: int,
                      pezzo: int, worktree: Path, avanzamento: Path, risultato: Path, versioni_impronta: dict) -> dict:
    """Cio' che si sa PRIMA di toccare i dati del periodo: lanciatore, codice, apertura, regole, e le
    versioni di python, numpy e scipy (D5: una ripresa con un ambiente diverso non e' lo stesso giro)."""
    return {"candidato": CANDIDATO, "etichetta": etichetta, "commit": codice["commit"],
            "sha256_lanciatore": sha_l, "versioni": versioni_impronta,
            "sha256_codice": {rel: v["sha256"] for rel, v in codice["file"].items()},
            "sha256_APERTURA": sha_apertura,
            "regole_esame": regole_esame, "n_caso": n_caso, "n_b": regole_esame["simulazioni_baseline_casuale"],
            "pezzo": pezzo, "worktree": str(worktree), "avanzamento": str(avanzamento), "risultato": str(risultato)}


def _righe(diff: list, n: int = 30, larghezza: int = 400) -> str:
    """Le prime differenze, accorciate, per un messaggio di rifiuto leggibile."""
    return "\n  ".join(d if len(d) <= larghezza else d[:larghezza] + " [...]" for d in diff[:n])


def _leggi_json_o_stop(p: Path, cosa: str):
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        raise SystemExit(f"RIFIUTO: {cosa} {p} illeggibile ({e}): decide il proprietario") from None


def guardia_una_volta(p_ris: Path, p_marc: Path, altri, impronta_avvio: dict) -> dict:
    """R2. Se il risultato (o un altro segno di giro finito) esiste, rifiuta. Se esiste il
    marcatore di un giro iniziato, lo riprende solo se l'impronta d'avvio e' la stessa
    (stesso lanciatore, stesso codice, stessa apertura, stesse regole); altrimenti rifiuta.
    Se non esiste nulla, crea il marcatore in modo esclusivo (O_EXCL), PRIMA di qualunque
    accesso ai dati del periodo.
    """
    for p in (p_ris, *altri):
        if p.exists():
            raise SystemExit(f"RIFIUTO: {p} esiste gia': il giro si fa una volta sola")
    voce = pulito(impronta_avvio)
    if p_marc.exists():
        vecchio = _leggi_json_o_stop(p_marc, "il marcatore")
        if not isinstance(vecchio, dict):
            raise SystemExit(f"RIFIUTO: il marcatore {p_marc} non e' un oggetto JSON: decide il proprietario")
        if vecchio.get("stato") == "finito":
            raise SystemExit(f"RIFIUTO: il marcatore {p_marc} dice che il giro e' gia' finito "
                             f"(risultato {vecchio.get('risultato')}): il giro si fa una volta sola")
        if vecchio.get("impronta_avvio") != voce:
            diff = confronta(vecchio.get("impronta_avvio") or {}, voce)
            raise SystemExit(f"RIFIUTO: {p_marc} e' di un giro iniziato con un'impronta diversa (non e' una ripresa "
                             f"dello stesso giro):\n  " + _righe(diff))
        vecchio.setdefault("riprese", []).append({"data": adesso(), "pid": os.getpid()})
        scrivi_json(p_marc, vecchio)
        print(f"[{adesso()}] ripresa dello stesso giro (marcatore {p_marc}, iniziato {vecchio.get('iniziato')})", flush=True)
        return {"marcatore": str(p_marc), "ripresa": True, "iniziato": vecchio.get("iniziato"),
                "riprese": len(vecchio["riprese"])}
    marcatore = {"candidato": CANDIDATO, "iniziato": adesso(), "pid": os.getpid(),
                 "stato": "iniziato: dati del periodo non ancora caricati",
                 "impronta_avvio": voce, "sha256_impronta_avvio": sha256_json(voce), "riprese": [],
                 "storia": [{"data": adesso(), "stato": "iniziato: dati del periodo non ancora caricati"}]}
    p_marc.parent.mkdir(parents=True, exist_ok=True)
    try:
        fd = os.open(p_marc, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
    except FileExistsError:
        raise SystemExit(f"RIFIUTO: {p_marc} e' comparso adesso: un altro giro e' partito") from None
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        f.write(json.dumps(pulito(marcatore), ensure_ascii=False, indent=1, allow_nan=False) + "\n")
        f.flush()
        os.fsync(f.fileno())
    return {"marcatore": str(p_marc), "ripresa": False, "iniziato": marcatore["iniziato"], "riprese": 0}


def aggiorna_marcatore(p_marc: Path, stato: str, *, motivo=None, dettagli=None, **campi) -> None:
    """Cambia lo stato del marcatore. ``motivo`` e ``dettagli`` in cima sono SEMPRE quelli dello stato
    attuale (D5): a ogni cambio si riscrivono, e senza motivo si azzerano (``null``), cosi' un giro
    finito non porta in cima il motivo di un fermo o di un'interruzione di prima. La storia tiene
    ogni stato col suo motivo."""
    dati_m = _leggi_json_o_stop(p_marc, "il marcatore")
    dati_m.update(pulito(campi))
    dati_m["stato"] = stato
    dati_m["motivo"] = motivo
    dati_m["dettagli"] = pulito(dettagli)
    voce = {"data": adesso(), "stato": stato}
    if motivo:
        voce["motivo"] = motivo
    dati_m.setdefault("storia", []).append(voce)
    scrivi_json(p_marc, dati_m)


def candidato_eseguito(p_marc: Path) -> bool:
    return bool(_leggi_json_o_stop(p_marc, "il marcatore").get("candidato_eseguito"))


def segna_candidato_eseguito(p_marc: Path) -> None:
    """D4: scritto nel marcatore PRIMA di chiamare il candidato. Da qui i file di dati restano fissati
    per sempre e ogni fine del giro scrive un risultato (R5)."""
    dati_m = _leggi_json_o_stop(p_marc, "il marcatore")
    campi = {"candidato_eseguito": True}
    if dati_m.get("candidato_eseguito"):
        campi["candidato_rieseguito_nelle_riprese"] = list(dati_m.get("candidato_rieseguito_nelle_riprese") or []) + [adesso()]
    else:
        campi["candidato_eseguito_dal"] = adesso()
    aggiorna_marcatore(p_marc, "candidato in esecuzione: da qui ogni fine scrive un risultato (R5)", **campi)


def fissa_dati_nel_marcatore(p_marc: Path, sha_dati: dict) -> None:
    """Le impronte dei file di dati entrano nel marcatore prima di caricare i dati.

    D4: finche' il candidato non e' stato eseguito, un nuovo tentativo (dopo uno STOP sui dati) puo'
    portare file diversi: le impronte vecchie passano in ``sha256_dati_tentativi_precedenti`` e si
    fissano le nuove. Dopo l'esecuzione del candidato (ripresa di un giro interrotto) i file devono
    essere gli stessi: se sono diversi lo stesso giro non puo' piu' finire sugli stessi dati e si
    solleva ``Fermo`` (chi chiama scrive il risultato, R5)."""
    dati_m = _leggi_json_o_stop(p_marc, "il marcatore")
    voce = pulito(sha_dati)
    if dati_m.get("candidato_eseguito"):
        if dati_m.get("sha256_dati") != voce:
            raise Fermo("i file di dati non sono quelli con cui il candidato e' stato eseguito (giro interrotto e "
                        "ripreso con dati diversi): lo stesso giro non puo' finire sugli stessi dati",
                        confronta(dati_m.get("sha256_dati") or {}, voce)[:50])
        return
    if "sha256_dati" in dati_m:
        if dati_m["sha256_dati"] == voce:
            return
        dati_m.setdefault("sha256_dati_tentativi_precedenti", []).append(
            {"fissati": dati_m.get("sha256_dati_fissati"), "sostituiti": adesso(), "sha256_dati": dati_m["sha256_dati"],
             "nota": "tentativo fermo prima dell'esecuzione del candidato (D4): i file si potevano ancora cambiare"})
    dati_m["sha256_dati"] = voce
    dati_m["sha256_dati_fissati"] = adesso()
    scrivi_json(p_marc, dati_m)


def fermo_senza_risultato(p_marc: Path, e: "FermoSuiDati", eseguito_prima: bool) -> int:
    """D4: lo STOP sui dati prima del candidato non scrive un risultato e non consuma il vault."""
    stato = STATO_FERMO_DATI_DOPO if eseguito_prima else STATO_FERMO_DATI
    # ogni fermo sui dati resta nella sua storia (con la tabella dei mesi, se c'era); in cima solo
    # stato, motivo e dettagli, che il cambio di stato successivo riscrive (D5)
    fermi = list(_leggi_json_o_stop(p_marc, "il marcatore").get("fermi_sui_dati") or [])
    fermi.append({"data": adesso(), "stato": stato, "motivo": e.motivo, "dettagli": e.dettagli,
                  "controllo_dati": e.controllo_dati})
    aggiorna_marcatore(p_marc, stato, motivo=e.motivo, dettagli=e.dettagli, fermi_sui_dati=fermi)
    print(f"FERMO SUI DATI ({stato}): {e.motivo}", flush=True)
    if isinstance(e.dettagli, dict):
        righe = [f"{k}: {v}" for k, v in e.dettagli.items() if v]
    elif isinstance(e.dettagli, list):
        righe = [str(d) for d in e.dettagli]
    else:
        righe = []
    for r_ in righe:
        print(f"  {r_}", flush=True)
    print("Nessun risultato scritto; il vault non e' consumato. Risolto il problema, si rilancia lo stesso comando "
          "con lo stesso lanciatore.", flush=True)
    return 4


def nomi_pezzi(n_b: int, n_caso: int, pezzo: int) -> list:
    return ([f"b_{a:04d}_{b - 1:04d}.json" for a, b in _pezzi(n_b, pezzo)]
            + [f"caso_{a:04d}_{b - 1:04d}.json" for a, b in _pezzi(n_caso, pezzo)])


def _presenti(avanzamento: Path) -> list:
    """I file della cartella di avanzamento, tolti impronta.json e i temporanei ``.parziale``."""
    if not avanzamento.is_dir():
        return []
    return sorted(p.name for p in avanzamento.iterdir()
                  if p.name != "impronta.json" and not p.name.endswith(".parziale"))


def controlla_avanzamento(avanzamento: Path, ingressi: dict, attesi: list) -> dict:
    """R3, PRIMA di caricare i dati del periodo: pezzi senza impronta.json, file estranei, un
    impronta.json con ingressi diversi (lanciatore, codice, dati, regole) o un pezzo che non
    porta lo SHA-256 di quell'impronta fanno rifiutare la ripresa."""
    presenti = _presenti(avanzamento)
    estranei = [n for n in presenti if n not in attesi]
    if estranei:
        raise SystemExit(f"RIFIUTO: in {avanzamento} ci sono file che questo giro non scrive: {estranei}")
    p_imp = avanzamento / "impronta.json"
    if not p_imp.is_file():
        if presenti:
            raise SystemExit(f"RIFIUTO: in {avanzamento} ci sono pezzi ma manca impronta.json: {presenti}. "
                             f"Pezzi senza impronta non si riprendono mai")
        return {"cartella": str(avanzamento), "ripresa": False, "pezzi_presenti": 0}
    imp = _leggi_json_o_stop(p_imp, "l'impronta dell'avanzamento")
    if not isinstance(imp, dict) or imp.get("ingressi") != pulito(ingressi):
        diff = confronta((imp or {}).get("ingressi") if isinstance(imp, dict) else {}, pulito(ingressi))
        raise SystemExit(f"RIFIUTO: l'avanzamento in {avanzamento} e' di un giro con ingressi diversi:\n  "
                         + _righe(diff))
    sha = sha256_json(imp)
    for nome in presenti:
        d = _leggi_json_o_stop(avanzamento / nome, "il pezzo")
        trovata = d.get("impronta") if isinstance(d, dict) else None
        if trovata != sha:
            raise SystemExit(f"RIFIUTO: il pezzo {avanzamento / nome} porta l'impronta {trovata!r}, "
                             f"non quella del giro ({sha})")
    return {"cartella": str(avanzamento), "ripresa": True, "pezzi_presenti": len(presenti), "sha256_impronta": sha}


def prepara_avanzamento(avanzamento: Path, impronta: dict, attesi: list) -> str:
    """Dentro l'esame (dati gia' caricati): stessa regola, ma un rifiuto diventa un esito (R5)."""
    voce = pulito(impronta)
    sha = sha256_json(voce)
    avanzamento.mkdir(parents=True, exist_ok=True)
    presenti = _presenti(avanzamento)
    estranei = [n for n in presenti if n not in attesi]
    if estranei:
        raise Fermo("file estranei nella cartella di avanzamento", estranei)
    p_imp = avanzamento / "impronta.json"
    if p_imp.is_file():
        try:
            vecchia = json.loads(p_imp.read_text(encoding="utf-8"))
        except (OSError, ValueError) as e:
            raise Fermo(f"impronta dell'avanzamento illeggibile: {e}") from None
        if vecchia != voce:
            raise Fermo("l'avanzamento e' di un giro diverso", confronta(vecchia, voce)[:50])
        print(f"[{adesso()}] ripresa dall'avanzamento in {avanzamento}", flush=True)
    else:
        if presenti:
            raise Fermo("pezzi senza impronta.json nella cartella di avanzamento", presenti)
        scrivi_json(p_imp, voce)
    return sha


def leggi_pezzo(p: Path, sha: str, semi: list) -> dict:
    try:
        d = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        raise Fermo(f"pezzo illeggibile {p}: {e}") from None
    if not isinstance(d, dict) or d.get("impronta") != sha:
        raise Fermo(f"il pezzo {p.name} non porta l'impronta di questo giro",
                    {"trovata": d.get("impronta") if isinstance(d, dict) else None, "attesa": sha})
    if d.get("semi") != list(semi):
        raise Fermo(f"il pezzo {p.name} ha i semi {d.get('semi')} invece di {list(semi)}")
    return d


# ---------------------------------------------------------------------------
# Controllo dei dati del periodo (regola D2-D3)
# ---------------------------------------------------------------------------


def _iso(ts: int) -> str:
    return datetime.fromtimestamp(ts / 1000, tz=timezone.utc).isoformat()


def _mese(ts: int) -> str:
    d = datetime.fromtimestamp(ts / 1000, tz=timezone.utc)
    return f"{d.year:04d}-{d.month:02d}"


def _ore(ms: int):
    """Una distanza in ms scritta in ore (intero se e' un numero intero di ore)."""
    return ms // MS_ORA if ms % MS_ORA == 0 else round(ms / MS_ORA, 3)


def controllo_dati(m, inizio_ts: int, fine: date) -> dict:
    """D2 e D3, dopo il caricamento e PRIMA di eseguire il candidato: mese per mese, le barre della
    serie allineata last/mark (quella che usa il candidato) e i settlement di funding del periodo.

    Blocchi (D2, ``ok`` falso: il giro si ferma SENZA risultato):
    * l'ultima barra allineata non e' l'ultima barra di ``fine`` al timeframe del candidato (1h:
      le 23:00 UTC);
    * un mese ha meno del 50% delle barre allineate attese;
    * un mese non ha nessun settlement di funding.
    Tutto il resto si riporta e basta (D3): per mese barre attese, last, mark, allineate e quota,
    con un AVVISO sotto il 99% (come le barre tolte dichiarate dalle campagne); settlement di
    funding per mese con gli intervalli osservati fra settlement consecutivi e le ore dichiarate nei
    file. Nessun numero di settlement «atteso». V10 non usa BTC come serie esterna.
    """
    ms_tf = m.quadro.MS[TF]
    last = m.dati.carica_candele(SIMBOLO, TF, m.comune.PRIMO_GIORNO, fine)
    mark = m.dati.carica_candele(SIMBOLO, TF, m.comune.PRIMO_GIORNO, fine, tipo="markPriceKlines")
    candele, _mark_al, funding = m.quadro.carica(TF, fine)
    dettaglio = m.dati.carica_funding_dettaglio(SIMBOLO, m.comune.PRIMO_GIORNO, fine)
    fine_ts = m.dati.ms_da_data(fine + timedelta(days=1))
    ultima_attesa = fine_ts - ms_tf

    def conta(seq):
        return Counter(_mese(ts) for ts in seq if inizio_ts <= ts < fine_ts)

    c_last, c_mark = conta(c.ts for c in last), conta(c.ts for c in mark)
    c_all, c_fund = conta(c.ts for c in candele), conta(t for t, _ in funding)
    ore_dich = {}
    for ts, ore, _tasso in dettaglio:
        if inizio_ts <= ts < fine_ts:
            ore_dich.setdefault(_mese(ts), set()).add(ore)
    # intervalli osservati: distanza da ogni settlement del periodo al precedente (anche di prima
    # del periodo), contata nel mese del settlement; sono quelli che usa il motore (al minuto)
    ts_f = [t for t, _ in funding]
    intervalli = {}
    for prec, t in zip(ts_f, ts_f[1:]):
        if inizio_ts <= t < fine_ts:
            k_ = str(_ore(t - prec))
            intervalli.setdefault(_mese(t), Counter())[k_] += 1
    mesi, blocchi, avvisi = [], [], []
    inizio_d = datetime.fromtimestamp(inizio_ts / 1000, tz=timezone.utc).date()
    for a, me in m.dati.mesi_del_periodo(inizio_d, fine):
        k = f"{a:04d}-{me:02d}"
        da = max(inizio_ts, m.dati.ms_da_data(date(a, me, 1)))
        a_ = min(fine_ts, m.dati.ms_da_data(date(a + (me == 12), me % 12 + 1, 1)))
        attese = (a_ - da) // ms_tf
        quota = c_all[k] / attese if attese else None
        riga = {"mese": k, "barre_attese": attese, "barre_last": c_last[k], "barre_mark": c_mark[k],
                "barre_allineate": c_all[k], "barre_tolte": c_last[k] - c_all[k],
                "quota_allineate": round(quota, 4) if quota is not None else None,
                "avviso_sotto_99": bool(quota is not None and quota < SOGLIA_AVVISO_BARRE),
                "blocco_sotto_50": bool(quota is None or quota < SOGLIA_BLOCCO_BARRE),
                "settlement": c_fund[k],
                "intervalli_osservati_ore": dict(sorted((intervalli.get(k) or Counter()).items(),
                                                        key=lambda kv: float(kv[0]))),
                "ore_funding_dichiarate": sorted(ore_dich.get(k, ())),
                "blocco_nessun_settlement": c_fund[k] == 0}
        mesi.append(riga)
        if riga["blocco_sotto_50"]:
            blocchi.append(f"{k}: {c_all[k]} barre allineate su {attese} attese "
                           f"({100 * (quota or 0):.1f}%, sotto il {100 * SOGLIA_BLOCCO_BARRE:.0f}%)")
        elif riga["avviso_sotto_99"]:
            avvisi.append(f"AVVISO {k}: {c_all[k]} barre allineate su {attese} attese ({100 * quota:.1f}%, sotto il "
                          f"{100 * SOGLIA_AVVISO_BARRE:.0f}%): last {c_last[k]}, mark {c_mark[k]}, "
                          f"{c_last[k] - c_all[k]} barre tolte dall'allineamento")
        if riga["blocco_nessun_settlement"]:
            blocchi.append(f"{k}: nessun settlement di funding")
    ultima = candele[-1].ts if candele else None
    if ultima != ultima_attesa:
        blocchi.append(f"la serie allineata finisce a {_iso(ultima) if ultima is not None else 'nessuna barra'}, "
                       f"non all'ultima barra attesa {_iso(ultima_attesa)}")
    buchi = []
    for p_, d_ in zip(candele, candele[1:]):
        if d_.ts >= inizio_ts and d_.ts > p_.close_ts + 1:
            buchi.append({"ultima_barra_prima": _iso(p_.ts), "prima_barra_dopo": _iso(d_.ts),
                          "ore_mancanti": (d_.ts - p_.ts) // MS_ORA - 1})
    giorni = Counter(c.ts // MS_GIORNO for c in candele if inizio_ts <= c.ts < fine_ts)
    corti = [datetime.fromtimestamp(g * MS_GIORNO / 1000, tz=timezone.utc).date().isoformat()
             for g in range(inizio_ts // MS_GIORNO, fine_ts // MS_GIORNO) if giorni.get(g, 0) != 24]
    return {
        "ok": not blocchi, "blocchi": blocchi, "avvisi": avvisi,
        "regola": {"timeframe": TF, "blocco_quota_barre_sotto": SOGLIA_BLOCCO_BARRE,
                   "avviso_quota_barre_sotto": SOGLIA_AVVISO_BARRE, "blocco_mese_senza_settlement": True,
                   "blocco_ultima_barra_diversa_da": _iso(ultima_attesa),
                   "btc": "V10 non usa BTC come serie esterna"},
        "periodo": {"da": _iso(inizio_ts), "fine": fine.isoformat()},
        "ultima_barra_allineata": _iso(ultima) if ultima is not None else None,
        "ultima_barra_attesa": _iso(ultima_attesa),
        "ultima_barra_last": _iso(last[-1].ts) if last else None,
        "ultima_barra_mark": _iso(mark[-1].ts) if mark else None,
        "barre_attese_nel_periodo": sum(r["barre_attese"] for r in mesi),
        "barre_allineate_nel_periodo": sum(r["barre_allineate"] for r in mesi),
        "barre_tolte_nel_periodo": sum(r["barre_tolte"] for r in mesi),
        "mesi_con_avviso": [r["mese"] for r in mesi if r["avviso_sotto_99"] and not r["blocco_sotto_50"]],
        "settlement_nel_periodo": sum(r["settlement"] for r in mesi),
        "intervalli_osservati_nel_periodo_ore": dict(sorted(sum((Counter(r["intervalli_osservati_ore"]) for r in mesi),
                                                                Counter()).items(), key=lambda kv: float(kv[0]))),
        "buchi_nel_periodo": len(buchi), "ore_mancanti_nel_periodo": sum(b["ore_mancanti"] for b in buchi),
        "elenco_buchi": buchi[:100],
        "giorni_senza_24_barre_allineate": corti,
        "mesi": mesi,
    }


# ---------------------------------------------------------------------------
# L'esame di un periodo (vault, o validazione per la prova)
# ---------------------------------------------------------------------------


def _conta_vietate(np, vietate, n_barre: int, primo: int) -> dict:
    """Barre vietate alle entrate casuali (unione degli intervalli, piu' l'ultima barra)."""
    ammessi = np.ones(n_barre, dtype=bool)
    for a, b in list(vietate) + [(n_barre - 1, n_barre)]:
        ammessi[max(0, a):min(n_barre, b)] = False
    nel = n_barre - primo
    ammesse_nel = int(ammessi[primo:].sum())
    return {"barre_serie": n_barre, "barre_periodo": nel, "ammesse_nel_periodo": ammesse_nel,
            "vietate_nel_periodo": nel - ammesse_nel, "quota_vietata_nel_periodo": round((nel - ammesse_nel) / nel, 4)}


def _pezzi(n: int, pezzo: int):
    return [(a, min(a + pezzo, n)) for a in range(0, n, pezzo)]


def _criterio_senza_caso(crit_c_metriche: dict, regole_esame: dict, esito: str, motivo: str) -> dict:
    """Le condizioni del criterio che non dipendono dal caso, quando il caso non c'e'."""
    pf = float(crit_c_metriche["profit_factor"])
    rend = float(crit_c_metriche["rendimento_totale"])
    n = int(crit_c_metriche["n_trade"])
    return {"esito": esito, "motivo": motivo,
            "condizioni": {"profit_factor": bool(pf >= regole_esame["pf_minimo"]),
                           "trade_minimi": bool(n >= regole_esame["trade_minimi"]),
                           "rendimento_positivo": bool(rend > 0.0), "sopra_il_caso": None},
            "valori": {"profit_factor": pf, "n_trade": n, "rendimento_totale": rend,
                       "r_medio": float(crit_c_metriche["r_medio"]), "r_caso_percentile_90": None,
                       "pf_minimo": regole_esame["pf_minimo"], "trade_minimi": regole_esame["trade_minimi"]},
            "metriche_usate_non_arrotondate": crit_c_metriche}


def esame(m, candele, mark, funding, inizio_ts: int, etichetta: str, n_caso: int, pezzo: int, avanzamento: Path,
          regole_esame: dict, ingressi: dict, contesto: dict, prima_del_candidato=None) -> dict:
    """Il giro del candidato su un periodo: come ``valida`` della campagna, piu' criterio e caso.

    La serie parte dal primo giorno della campagna (indicatori caldi); contano i trade ENTRATI
    da ``inizio_ts``; le entrate casuali sono vietate prima della prima barra del periodo,
    dove il segnale non e' valido e sull'ultima barra.

    Esiti (R5): «passa» / «non passa» col criterio del vault; «non si sa» sotto i trade minimi
    del vault (anche con 0 trade; sezione 8); «non valutabile» se le entrate casuali non si
    possono costruire. Gli STOP voluti escono come ``Fermo`` col risultato parziale; chi chiama
    scrive il risultato se il candidato e' gia' stato eseguito (R5), altrimenti no (D4).
    ``prima_del_candidato`` si chiama subito prima di eseguire il candidato (segna il marcatore).
    """
    np, st, mo = m.np, m.statistica, m.motore
    t_inizio = time.perf_counter()
    tempi = {}
    v = m.varianti.TUTTE[VID]()
    if v.tf != TF:
        raise SystemExit(f"STOP: il candidato e' a {v.tf}, il lanciatore carica {TF}")
    par = m.comune.parametri()
    n_b = regole_esame["simulazioni_baseline_casuale"]
    tm = regole_esame["trade_minimi"]
    primo = next((i for i, c in enumerate(candele) if c.ts >= inizio_ts), None)
    if primo is None:
        raise Fermo("nessuna barra nel periodo: il candidato non si puo' eseguire")

    # -- il candidato (come valida) -------------------------------------------------------
    if prima_del_candidato is not None:
        prima_del_candidato()
    t0 = time.perf_counter()
    ris = mo.esegui(candele, None, mark, funding, v.fabbrica(candele)(), par)
    trades = sorted([t for t in ris.trades if t.ts_entrata >= inizio_ts], key=lambda t: t.ts_uscita)
    tempi["candidato"] = round(time.perf_counter() - t0, 2)
    met = m.quadro.metriche_trade(trades)
    rend, dd = composto(trades, par)
    met["drawdown_max"] = round(dd, 4)
    met["rendimento_totale_composto"] = round(rend, 4)
    come_val = {"metriche": met}
    r = [t.r for t in trades]
    n = len(trades)
    r_medio_c = float(np.mean(r)) if n else -math.inf
    crit_c_metriche = metriche_criterio(m, trades, par, r_medio_c)
    ultimo_giorno_ts = candele[-1].ts - candele[-1].ts % MS_GIORNO
    extra = {
        "rendimento_composto_per_anno": composto_per_anno(trades),
        "trade_aperti_prima_ancora_in_corso_all_inizio": sum(1 for t in ris.trades if t.ts_entrata < inizio_ts <= t.ts_uscita),
        "trade_chiusi_a_fine_dati": sum(1 for t in trades if t.esito == "fine_dati"),
        "trade_entrati_l_ultimo_giorno": sum(1 for t in trades if t.ts_entrata >= ultimo_giorno_ts),
        "trade_tenuti_oltre_23_ore": sum(1 for t in trades if t.ts_uscita - t.ts_entrata > 23 * MS_ORA),
        "segnali_non_validi_tutta_la_serie": ris.n_segnali_non_validi,
        "segnali_senza_barra_tutta_la_serie": ris.n_segnali_senza_barra,
        "buchi_dati_tutta_la_serie": ris.n_buchi_dati,
        "funding_in_buco_tutta_la_serie": ris.n_funding_in_buco,
        "primo_trade": trades[0].ts_entrata if trades else None,
        "ultimo_trade": trades[-1].ts_entrata if trades else None,
    }
    giorni = [c for c in candele if c.ts >= inizio_ts]
    risultato = {
        "candidato": CANDIDATO, "etichetta": etichetta, "data": adesso(), "esito": None,
        "periodo": {"inizio_ts": inizio_ts, "inizio": _iso(inizio_ts), "ultima_barra": _iso(candele[-1].ts),
                    "barre_serie": len(candele), "barre_periodo": len(giorni), "prima_barra_del_periodo": primo},
        "come_validazione": come_val,
        "extra": extra,
        "regole_esame": regole_esame,
        "parametri_motore": dict(vars(par)),
        "contesto": contesto,
        "tempi_secondi": tempi,
        "avanzamento": str(avanzamento),
    }
    try:
        if n < tm:
            # sezione 8: sotto i trade minimi del vault l'esito e' «non si sa» e il candidato non va avanti
            motivo = (f"{n} trade nel periodo, sotto i {tm} di trade_minimi.vault: per la sezione 8 l'esito e' "
                      f"«non si sa» e il candidato non va avanti")
            come_val["esito"] = f"non si sa: sotto i {tm} trade del vault"
            risultato["esito"] = "non si sa"
            risultato["motivo"] = motivo
            risultato["criterio_vault"] = _criterio_senza_caso(crit_c_metriche, regole_esame, "non si sa", motivo)
            risultato["caso"] = {
                "calcolato": False, "tasso_del_caso": None, "simulazioni": 0, "semi": None,
                "condizioni_passate_dalle_simulazioni": None, "motivo": motivo,
                "nota": f"ogni strategia fittizia avrebbe al piu' {n} trade, sotto i {tm}: nessuna passerebbe "
                        f"il criterio (tasso 0 per costruzione, non calcolato)"}
            tempi["totale"] = round(time.perf_counter() - t_inizio, 1)
            return risultato

        # -- impronta del giro: si riprende solo lo stesso giro (R3) --------------------------
        t0 = time.perf_counter()
        vietate = [(0, primo)] + mo.barre_vietate_segnale_non_valido(candele, v.fabbrica_segnale(candele), par)
        tempi["barre_vietate"] = round(time.perf_counter() - t0, 2)
        durata = mo.durata_media_barre(trades, m.quadro.MS[v.tf])
        impronta = {"ingressi": ingressi, "giro": {
            "barre": len(candele), "prima_barra": candele[0].ts, "ultima_barra": candele[-1].ts,
            "inizio_ts": inizio_ts, "prima_barra_del_periodo": primo, "n_trade": n, "durata_media_barre": durata,
            "sha256_r_candidato": sha256_testo(json.dumps([repr(x) for x in r])),
            "sha256_barre_vietate": sha256_testo(json.dumps(vietate)),
            "sha256_funding": sha256_testo(json.dumps(funding)),
        }}
        sha_imp = prepara_avanzamento(avanzamento, impronta, nomi_pezzi(n_b, n_caso, pezzo))
        risultato["sha256_impronta_avanzamento"] = sha_imp

        # -- (a), come valida ------------------------------------------------------------------
        blocco = st.lunghezza_blocco([t.ts_entrata for t in trades], [t.ts_uscita for t in trades])
        come_val["blocco"] = blocco
        t0 = time.perf_counter()
        try:
            ris_a = mo.esegui(candele, None, mark, funding, v.fabbrica_a(candele)(), par)
            ta = sorted([t for t in ris_a.trades if t.ts_entrata >= inizio_ts], key=lambda t: t.ts_uscita)
            blocco_a = st.lunghezza_blocco([t.ts_entrata for t in ta], [t.ts_uscita for t in ta])
            base_a = st.baseline_da_trade([t.r for t in ta], blocco_a)
            come_val["baseline_a"] = dict(media=round(base_a["media"], 5), n_trade=base_a["n_trade"],
                                          **m.quadro._ridotto(st.contro_baseline(r, blocco, base_a), m.quadro.CHIAVI_CONFRONTO))
        except (ValueError, ZeroDivisionError) as e:
            come_val["baseline_a"] = {"valutabile": False, "motivo": str(e)}
        tempi["baseline_a"] = round(time.perf_counter() - t0, 2)

        # -- (b) con la funzione della campagna, a pezzi di semi ------------------------------
        t0 = time.perf_counter()
        pezzi_b, base_b = [], None
        try:
            for a, b in _pezzi(n_b, pezzo):
                p = avanzamento / f"b_{a:04d}_{b - 1:04d}.json"
                if p.is_file():
                    pezzi_b.append(leggi_pezzo(p, sha_imp, [a, b - 1]))
                    continue
                t1 = time.perf_counter()
                rb = mo.simula_baseline_casuale(candele, v.fabbrica_casuale(candele), n, durata, par, None, mark, funding,
                                                vietate, n_simulazioni=b - a, primo_seme=a)
                dati_pezzo = {"semi": [a, b - 1], "impronta": sha_imp, "valori": [float(x) for x in rb["valori"]],
                              "trade_per_simulazione": list(rb["trade_per_simulazione"]),
                              "simulazioni_vuote": rb["simulazioni_vuote"],
                              "segnali_non_validi_per_simulazione": list(rb["segnali_non_validi_per_simulazione"]),
                              "segnali_senza_barra_per_simulazione": list(rb["segnali_senza_barra_per_simulazione"]),
                              "secondi": round(time.perf_counter() - t1, 2)}
                scrivi_json(p, dati_pezzo)
                pezzi_b.append(dati_pezzo)
                print(f"[{adesso()}] (b) semi {a}..{b - 1}: {dati_pezzo['secondi']} s", flush=True)
            valori_b = [x for pz in pezzi_b for x in pz["valori"]]
            base_b = st.baseline_casuale(valori_b)
            base_b["trade_per_simulazione"] = [x for pz in pezzi_b for x in pz["trade_per_simulazione"]]
            base_b["simulazioni_vuote"] = sum(pz["simulazioni_vuote"] for pz in pezzi_b)
            base_b["segnali_non_validi_per_simulazione"] = [x for pz in pezzi_b for x in pz["segnali_non_validi_per_simulazione"]]
            base_b["segnali_senza_barra_per_simulazione"] = [x for pz in pezzi_b for x in pz["segnali_senza_barra_per_simulazione"]]
        except ValueError as e:
            base_b = None
            come_val["baseline_b"] = {"valutabile": False, "motivo": f"la (b) non si puo' costruire: {e}"}
        tempi["baseline_b"] = round(time.perf_counter() - t0, 2)
        if base_b is not None:
            try:
                cmp_b = st.contro_baseline(r, blocco, base_b)
                come_val["baseline_b"] = dict(media=round(base_b["media"], 5), n_simulazioni=base_b["n_simulazioni"],
                                              trade_per_simulazione_medio=round(float(np.mean(base_b["trade_per_simulazione"])), 2),
                                              durata_media_barre=durata, **m.quadro._ridotto(cmp_b, m.quadro.CHIAVI_CONFRONTO))
                come_val["percentile_caso"] = round(st.percentile_del_candidato(float(np.mean(r)), base_b["valori"]), 2)
                come_val["p_value"] = cmp_b["p_value"]
            except ValueError as e:
                come_val["baseline_b"] = {"valutabile": False, "motivo": str(e)}
        come_val["buy_and_hold_per_anno"] = m.quadro.buy_and_hold_per_anno(giorni, par)

        # -- il caso: n_caso entrate casuali con la gemella, a pezzi --------------------------
        t0 = time.perf_counter()
        sims, motivo_caso = [], None
        crea_casuale = v.fabbrica_casuale(candele)
        try:
            for a, b in _pezzi(n_caso, pezzo):
                p = avanzamento / f"caso_{a:04d}_{b - 1:04d}.json"
                if p.is_file():
                    sims += leggi_pezzo(p, sha_imp, [a, b - 1])["simulazioni"]
                    continue
                t1 = time.perf_counter()
                pz = simula_caso(m, candele, crea_casuale, n, durata, par, mark, funding, vietate, range(a, b), inizio_ts)
                sec = round(time.perf_counter() - t1, 2)
                scrivi_json(p, {"semi": [a, b - 1], "impronta": sha_imp, "secondi": sec, "simulazioni": pz})
                sims += pulito(pz)
                print(f"[{adesso()}] caso semi {a}..{b - 1}: {sec} s", flush=True)
        except ValueError as e:
            motivo_caso = f"le entrate casuali non si possono costruire: {e}"
        tempi["caso"] = round(time.perf_counter() - t0, 2)
        r_medi_caso = [s["r_medio"] for s in sims if s["n_trade"] > 0]
        if motivo_caso is None and not r_medi_caso:
            motivo_caso = "nessuna simulazione casuale ha trade: il 90° percentile del caso non esiste"
        if motivo_caso is not None:
            risultato["esito"] = "non valutabile"
            risultato["motivo"] = motivo_caso
            risultato["criterio_vault"] = _criterio_senza_caso(crit_c_metriche, regole_esame, "non valutabile", motivo_caso)
            risultato["caso"] = {"calcolato": False, "tasso_del_caso": None, "simulazioni": len(sims),
                                 "semi": [0, n_caso - 1], "condizioni_passate_dalle_simulazioni": None,
                                 "motivo": motivo_caso}
            tempi["totale"] = round(time.perf_counter() - t_inizio, 1)
            return risultato
        if [s["seme"] for s in sims] != list(range(n_caso)):
            raise Fermo("i semi del caso non sono 0..n-1 in ordine")
        if any(s["trade_entrati_prima_del_periodo"] for s in sims):
            raise Fermo("una simulazione casuale e' entrata prima del periodo")

        # la gemella deve ridare la (b) della campagna sui semi in comune
        n_comuni = min(n_caso, n_b)
        gemella_uguale = None
        if base_b is not None:
            gem = [s["r_medio"] for s in sims[:n_comuni] if s["n_trade"] > 0]
            camp = [x for pz in pezzi_b for x in pz["valori"]]
            camp_tps = base_b["trade_per_simulazione"]
            if n_comuni < n_b:  # prova ridotta: si confrontano solo i semi in comune
                vuote_prima = sum(1 for s in sims[:n_comuni] if s["n_trade"] == 0)
                camp = camp[:n_comuni - vuote_prima]
                camp_tps = camp_tps[:n_comuni - vuote_prima]
            gemella_uguale = (gem == camp) and ([s["n_trade"] for s in sims[:n_comuni] if s["n_trade"] > 0] == camp_tps)
            if not gemella_uguale:
                raise Fermo("le entrate casuali della gemella non ridanno la (b) della campagna sui semi in comune")

        # -- criterio del vault e tasso del caso -----------------------------------------------
        vuote = sum(1 for s in sims if s["n_trade"] == 0)
        p90 = st.percentile(r_medi_caso, regole_esame["percentile_caso"])
        crit_c = st.criterio_vault(crit_c_metriche, p90, trade_minimi=regole_esame["trade_minimi"],
                                   pf_minimo=regole_esame["pf_minimo"])
        esiti, cond_caso = [], {"profit_factor": 0, "trade_minimi": 0, "rendimento_positivo": 0, "sopra_il_caso": 0}
        for s in sims:
            ms = {"profit_factor": float(s["profit_factor"]) if not isinstance(s["profit_factor"], str) else math.inf,
                  "n_trade": s["n_trade"], "rendimento_totale": s["rendimento_totale"],
                  "r_medio": s["r_medio"] if s["r_medio"] is not None else -math.inf}
            c = st.criterio_vault(ms, p90, trade_minimi=regole_esame["trade_minimi"], pf_minimo=regole_esame["pf_minimo"])
            esiti.append(c["esito"])
            for k_, ok in c["condizioni"].items():
                cond_caso[k_] += int(ok)
        tasso = st.tasso_del_caso(esiti)
        tps = [s["n_trade"] for s in sims]
        caso = {
            "calcolato": True,
            "simulazioni": n_caso, "semi": [0, n_caso - 1], "n_trade_richiesti": n, "durata_media_barre": durata,
            "simulazioni_vuote": vuote, "trade_per_simulazione": {"media": round(float(np.mean(tps)), 2), "min": min(tps), "max": max(tps)},
            "barre_vietate": _conta_vietate(np, vietate, len(candele), primo),
            "r_medi": {"media": float(np.mean(r_medi_caso)),
                       "dev_std": float(np.std(r_medi_caso, ddof=1)) if len(r_medi_caso) > 1 else None,
                       "min": min(r_medi_caso), "max": max(r_medi_caso)},
            "percentile_90": p90,
            "percentile_del_candidato_fra_le_simulazioni_caso": st.percentile_del_candidato(r_medio_c, r_medi_caso),
            "condizioni_passate_dalle_simulazioni": cond_caso,
            "passano_il_criterio": int(sum(esiti)),
            "tasso_del_caso": tasso,
            "gemella_uguale_alla_b_sui_semi_comuni": gemella_uguale,
            "semi_confrontati_con_la_b": [0, n_comuni - 1] if base_b is not None else None,
        }
        risultato["criterio_vault"] = {**crit_c, "metriche_usate_non_arrotondate": crit_c_metriche}
        risultato["caso"] = caso
        risultato["esito"] = "passa" if crit_c["esito"] else "non passa"
        tempi["totale"] = round(time.perf_counter() - t_inizio, 1)
        return risultato
    except Fermo as e:
        if e.parziale is None:
            e.parziale = risultato
        raise


def risultato_fermo(e: Fermo, etichetta: str, inizio_ts: int, contesto: dict, eseguito=None) -> dict:
    """Il risultato di uno STOP dopo l'esecuzione del candidato (R5): esito «non valutabile».
    ``eseguito`` (se dato) dice come e' stato eseguito il candidato quando le sue metriche non ci sono."""
    ris = dict(e.parziale) if e.parziale else {
        "candidato": CANDIDATO, "etichetta": etichetta, "data": adesso(),
        "periodo": {"inizio_ts": inizio_ts, "inizio": _iso(inizio_ts),
                    "ultima_barra": ((contesto or {}).get("controllo_dati") or {}).get("ultima_barra_allineata")},
        "contesto": contesto}
    ris["esito"] = "non valutabile"
    ris["motivo"] = e.motivo
    ris["fermo"] = {"motivo": e.motivo, "dettagli": e.dettagli,
                    "candidato_eseguito": True if eseguito else ("come_validazione" in ris)}
    if eseguito:
        ris["fermo"]["come"] = eseguito
    ris["criterio_vault"] = {**(ris.get("criterio_vault") or {}), "esito": "non valutabile", "motivo": e.motivo}
    ris.setdefault("caso", {"calcolato": False, "tasso_del_caso": None, "motivo": e.motivo})
    return ris


def esegui_giro(m, *, etichetta: str, inizio_ts: int, fine: date, carica_serie, n_caso: int, pezzo: int,
                avanzamento: Path, regole_esame: dict, ingressi: dict, contesto: dict, p_marc: Path) -> dict:
    """Dal caricamento dei dati del periodo in poi.

    PRIMA dell'esecuzione del candidato (D4): un blocco di D2, o ogni altro STOP voluto, esce come
    ``FermoSuiDati``: nessun risultato, il vault non e' consumato. Gli avvisi di D3 si stampano e
    restano nel contesto del risultato.
    DOPO l'esecuzione del candidato (segnata nel marcatore subito prima, anche in una ripresa) torna
    SEMPRE un risultato (R5): ogni STOP voluto (``Fermo`` o ``SystemExit``) diventa «non valutabile».
    """
    stato = {"eseguito": candidato_eseguito(p_marc)}
    eseguito_prima = stato["eseguito"]  # gia' eseguito in un tentativo interrotto (ripresa)
    come_prima = "in un tentativo precedente, interrotto prima di scrivere il risultato"

    def al_via_del_candidato():
        segna_candidato_eseguito(p_marc)
        stato["eseguito"] = True
        stato["in_questo_tentativo"] = True

    def come_eseguito(parziale) -> "str | None":
        """Per il risultato: come e' stato eseguito il candidato, se le sue metriche non ci sono."""
        if "come_validazione" in (parziale or {}):
            return None  # le metriche ci sono: si vede da li'
        if stato.get("in_questo_tentativo"):
            return "in questo tentativo; le metriche non sono nel risultato perche' lo STOP non le portava"
        return come_prima if eseguito_prima else None

    try:
        controlli = controllo_dati(m, inizio_ts, fine)  # D2 e D3
        contesto["controllo_dati"] = controlli
        contesto["serie"] = descrivi_serie(m, fine, inizio_ts)
        for a in controlli["avvisi"]:
            print(a, flush=True)
        if not controlli["ok"]:
            raise Fermo("D2: i dati del periodo non permettono il giro: " + "; ".join(controlli["blocchi"]),
                        controlli["blocchi"])
        candele, mark, funding = carica_serie()
        return esame(m, candele, mark, funding, inizio_ts, etichetta, n_caso, pezzo, avanzamento, regole_esame,
                     ingressi, contesto, prima_del_candidato=al_via_del_candidato)
    except Fermo as e:
        if not stato["eseguito"]:
            raise FermoSuiDati(e.motivo, e.dettagli, contesto.get("controllo_dati")) from None
        print(f"FERMO: {e.motivo}", flush=True)
        return risultato_fermo(e, etichetta, inizio_ts, contesto, eseguito=come_eseguito(e.parziale))
    except SystemExit as e:
        if not stato["eseguito"]:
            raise FermoSuiDati(f"STOP prima dell'esecuzione del candidato: {e}", None,
                               contesto.get("controllo_dati")) from None
        print(f"FERMO: {e}", flush=True)
        return risultato_fermo(Fermo(f"STOP: {e}"), etichetta, inizio_ts, contesto, eseguito=come_eseguito(None))


def note_periodo(ris: dict) -> dict:
    """R6: le note su ultimo giorno e buchi, in chiaro."""
    cd = (ris.get("contesto") or {}).get("controllo_dati") or {}
    ex = ris.get("extra") or {}
    if not cd:
        return {"ultimo_giorno": None, "buchi": None,
                "funding": None, "dati_del_periodo": "i dati del periodo non sono stati caricati in questo tentativo "
                                                   "(il giro si e' fermato prima): niente da dichiarare su ultimo giorno, "
                                                   "buchi e funding",
                "controllo_dati_ok": None, "blocchi_dati": None, "avvisi_dati": None}
    return {
        "ultimo_giorno": (
            f"Ultima barra della serie allineata: {cd.get('ultima_barra_allineata')} (attesa {cd.get('ultima_barra_attesa')}). "
            f"Un trade aperto l'ultimo giorno si chiude al close della barra delle 23:00 con esito fine_dati, senza il "
            f"settlement di funding delle 00:00 del giorno dopo. Trade chiusi cosi': {ex.get('trade_chiusi_a_fine_dati')}; "
            f"trade entrati l'ultimo giorno: {ex.get('trade_entrati_l_ultimo_giorno')}."),
        "buchi": (
            f"Barre tolte dall'allineamento last/mark nel periodo: {cd.get('barre_tolte_nel_periodo')} su "
            f"{cd.get('barre_attese_nel_periodo')} attese; mesi sotto il 99% (AVVISO, regola D3): "
            f"{cd.get('mesi_con_avviso') or 'nessuno'}. "
            f"Buchi nella serie allineata del periodo: {cd.get('buchi_nel_periodo')} ({cd.get('ore_mancanti_nel_periodo')} ore "
            f"mancanti). Giorni senza 24 barre allineate: {len(cd.get('giorni_senza_24_barre_allineate') or [])} (per la "
            f"regola della campagna tolgono il segnale del giorno dopo, senza errore). Trade tenuti oltre 23 ore (manca la "
            f"barra delle 23:00): {ex.get('trade_tenuti_oltre_23_ore')}. Settlement di funding caduti in un buco con "
            f"posizione aperta: {ex.get('funding_in_buco_tutta_la_serie')} (contati su tutta la serie dal 2020)."),
        "funding": (f"Settlement di funding nel periodo: {cd.get('settlement_nel_periodo')}; intervalli osservati fra "
                    f"settlement consecutivi (ore: quante volte): {cd.get('intervalli_osservati_nel_periodo_ore')}. "
                    f"Nessun numero atteso: il conto per mese e' nella tabella."),
        "controllo_dati_ok": cd.get("ok"),
        "blocchi_dati": cd.get("blocchi"),
        "avvisi_dati": cd.get("avvisi"),
    }


def completa_risultato(ris: dict, m, *, sha_l: str, regole_esame: dict, n_caso: int, impronta_avvio: dict,
                       ingressi: dict, guardia: dict, p_marc: Path) -> dict:
    """R6: versioni, SHA-256 del lanciatore, semi, impronte, guardia, note."""
    n_b = regole_esame["simulazioni_baseline_casuale"]
    ris["versioni"] = versioni(m)
    ris["sha256_lanciatore"] = sha_l
    ris["lanciatore"] = str(Path(__file__).resolve())
    ris["semi"] = {"caso": [0, n_caso - 1], "baseline_b": [0, n_b - 1],
                   "bootstrap": regole_esame["bootstrap"]["seme"],
                   "ricampionamenti_bootstrap": regole_esame["bootstrap"]["ricampionamenti"],
                   "nota": "i semi del caso e della (b) partono da 0; la (b) sono i primi 200 semi del caso"}
    ris["impronta"] = {"sha256_impronta_avvio": sha256_json(impronta_avvio), "sha256_ingressi": sha256_json(ingressi),
                       "ingressi": ingressi}
    ris["guardia"] = {**guardia, "marcatore": str(p_marc)}
    dopo = controlla_codice(m.worktree, fermati=False)
    ris["codice_dopo_il_giro"] = {"ok": dopo["ok"], "problemi": dopo["problemi"]}
    ris["note"] = note_periodo(ris)
    return ris


def scrivi_risultato(ris: dict, p_ris: Path, p_md: Path, p_marc: Path, segno: Path, titolo: str) -> Path:
    """Prima il JSON, poi il riassunto (R6), poi il marcatore («finito») e il segno."""
    destinazione = p_ris
    if p_ris.exists():  # comparso durante il giro: non si sovrascrive, ma il risultato resta scritto (R5)
        destinazione = p_ris.with_name(f"{p_ris.stem}_doppione_{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}.json")
        ris["attenzione"] = f"{p_ris} e' comparso durante il giro: questo risultato non lo sovrascrive"
    scrivi_json(destinazione, ris)
    sha = sha256_file(destinazione)
    if destinazione == p_ris:
        scrivi_testo(p_md, riassunto(ris, titolo))
    aggiorna_marcatore(p_marc, "finito", risultato=str(destinazione), sha256_risultato=sha, esito=ris.get("esito"),
                       finito=adesso())
    if destinazione == p_ris and not segno.exists():
        scrivi_json(segno, {"candidato": CANDIDATO, "data": adesso(), "risultato": str(destinazione),
                            "sha256_risultato": sha, "esito": ris.get("esito")})
    return destinazione


def riassunto(ris: dict, titolo: str) -> str:
    sn = lambda x: "sì" if x is True else ("no" if x is False else "non calcolata")  # noqa: E731
    per = ris.get("periodo") or {}
    righe = [
        f"# {titolo}",
        "",
        f"Candidato {ris.get('candidato')} (rottura di volatilità dall'apertura del giorno, long, 1h). "
        f"Periodo dei trade: entrati dal {per.get('inizio')} all'ultima barra {per.get('ultima_barra')}. "
        f"Scritto il {ris.get('data')} dal lanciatore `research/vault_strumenti/BTCUSDT.py` "
        f"(SHA-256 {ris.get('sha256_lanciatore')}), con il codice del candidato (commit {COMMIT_ATTESO[:8]}). "
        f"Versioni: {ris.get('versioni')}.",
        "",
        f"## Esito: **{str(ris.get('esito')).upper()}**",
        "",
    ]
    if ris.get("motivo"):
        righe += [f"Motivo: {ris['motivo']}", ""]
    if ris.get("fermo"):
        righe += [f"Il giro si è fermato: {ris['fermo']['motivo']}. Candidato eseguito: "
                  f"{sn(ris['fermo']['candidato_eseguito'])}. Dettagli: {ris['fermo']['dettagli']}", ""]
    cr = ris.get("criterio_vault") or {}
    va, co = cr.get("valori"), cr.get("condizioni")
    if va and co:
        p90 = va.get("r_caso_percentile_90")
        righe += [
            "| Condizione | Valore | Soglia | Passa |",
            "|---|---|---|---|",
            f"| Profit factor dopo i costi | {va['profit_factor']:.4f} | almeno {va['pf_minimo']:.2f} | {sn(co['profit_factor'])} |",
            f"| Trade | {va['n_trade']} | almeno {va['trade_minimi']} | {sn(co['trade_minimi'])} |",
            f"| Rendimento totale composto | {va['rendimento_totale']:+.4f} | sopra 0 | {sn(co['rendimento_positivo'])} |",
            f"| R medio | {va['r_medio']:+.4f} | sopra il 90° percentile del caso, "
            f"{(f'{p90:+.4f}' if p90 is not None else 'non calcolato')} | {sn(co['sopra_il_caso'])} |",
            "",
        ]
    ca = ris.get("caso") or {}
    if ca.get("calcolato"):
        righe += [
            f"**Tasso del caso: {ca['tasso_del_caso']:.3f}** ({ca['passano_il_criterio']} strategie a entrate casuali su "
            f"{ca['simulazioni']} passano lo stesso criterio con lo stesso 90° percentile; semi {ca['semi'][0]}..{ca['semi'][1]}, "
            f"{ca['n_trade_richiesti']} ingressi ciascuna a distanza almeno {ca['durata_media_barre']} barre, stessa uscita).",
            f"Quante fittizie passano ogni condizione: {ca['condizioni_passate_dalle_simulazioni']}. "
            f"Simulazioni vuote: {ca['simulazioni_vuote']}. Trade per simulazione: {ca['trade_per_simulazione']}.",
            "",
        ]
    elif ca:
        righe += [f"Tasso del caso: non calcolato ({ca.get('motivo')}). {ca.get('nota') or ''}".rstrip(), ""]
    cv = ris.get("come_validazione")
    if cv:
        me = cv["metriche"]
        b = cv.get("baseline_b") or {}
        a = cv.get("baseline_a") or {}
        ex = ris.get("extra") or {}
        righe += [
            "## Le metriche della consegna, sul periodo",
            "",
            "| | |",
            "|---|---|",
            f"| Trade | {me['trade']} (per anno di uscita: {me['trade_per_anno']}) |",
            f"| R medio a trade | {me['r_medio']:+.4f} |",
            f"| R medio per anno | {me['r_medio_per_anno']} |",
            f"| R medio senza i 3 migliori | {me['r_medio_senza_3_migliori']} |",
            f"| Profit factor | {me['profit_factor']} |",
            f"| Win rate | {me['win_rate']} |",
            f"| Drawdown massimo (trade del periodo, dal capitale iniziale) | {me['drawdown_max']} |",
            f"| Rendimento composto | totale {me['rendimento_totale_composto']:+.4f}; per anno {ex.get('rendimento_composto_per_anno')} |",
            f"| Baseline (a) | {a.get('media')}; t {a.get('t')}, soglia {a.get('soglia')}, netta {a.get('netta')}"
            f"{'; ' + str(a.get('motivo')) if a.get('motivo') else ''} |",
            f"| Baseline (b), {b.get('n_simulazioni')} semi | {b.get('media')}; t {b.get('t')}, soglia {b.get('soglia')}, "
            f"netta {b.get('netta')}, p-value {cv.get('p_value')}{'; ' + str(b.get('motivo')) if b.get('motivo') else ''} |",
            f"| Percentile fra le simulazioni della (b) | {cv.get('percentile_caso')} |",
            f"| Buy and hold per anno (contesto) | {cv.get('buy_and_hold_per_anno')} |",
            f"| Trade ridotti per il tetto di leva | {me['ridotti_tetto_leva']} |",
            f"| Violazioni della liquidazione | {me['violazioni_liquidazione']} |",
            f"| Stop oltre il 6% | {me['stop_oltre_6_per_cento']} |",
            f"| Durata media | {me['durata_media_ore']} ore |",
            f"| Esiti | {me['esiti']} |",
            "",
        ]
    cd = (ris.get("contesto") or {}).get("controllo_dati")
    if cd:
        righe += [
            "## I dati del periodo, mese per mese (regola dei dati D2-D3, prima del candidato)",
            "",
            f"Blocchi (D2): {cd['blocchi'] or 'nessuno'}. Ultima barra allineata {cd['ultima_barra_allineata']} "
            f"(attesa {cd['ultima_barra_attesa']}). Barre tolte dall'allineamento: {cd['barre_tolte_nel_periodo']} su "
            f"{cd['barre_attese_nel_periodo']} attese.",
            "",
        ]
        righe += [f"* {a}" for a in cd["avvisi"]] or ["* Nessun mese sotto il 99% delle barre allineate."]
        righe += [
            "",
            "| Mese | Barre attese | Last | Mark | Allineate | Quota | Avviso | Settlement | Intervalli osservati (ore: volte) |",
            "|---|---|---|---|---|---|---|---|---|",
        ]
        righe += [f"| {r_['mese']} | {r_['barre_attese']} | {r_['barre_last']} | {r_['barre_mark']} | {r_['barre_allineate']} | "
                  f"{r_['quota_allineate']} | {'AVVISO' if r_['avviso_sotto_99'] else ''} | {r_['settlement']} | "
                  f"{r_['intervalli_osservati_ore']} |" for r_ in cd["mesi"]]
        righe.append("")
    note = ris.get("note") or {}
    righe += ["## Da dichiarare", ""]
    for k in ("ultimo_giorno", "buchi", "funding", "dati_del_periodo"):
        if note.get(k):
            righe.append(f"* {note[k]}")
    if ca.get("calcolato"):
        righe += [
            f"* Barre vietate alle entrate casuali: {ca['barre_vietate']}.",
            f"* La gemella delle entrate casuali ridà la (b) della campagna sui semi {ca['semi_confrontati_con_la_b']}: "
            f"{sn(ca['gemella_uguale_alla_b_sui_semi_comuni'])}.",
            f"* Il percentile del candidato fra le {ca['simulazioni']} simulazioni del caso: "
            f"{ca['percentile_del_candidato_fra_le_simulazioni_caso']:.1f} (indizio, non prova).",
        ]
    righe += [f"* Semi: {ris.get('semi')}.", f"* Tempi (secondi): {ris.get('tempi_secondi')}."]
    return "\n".join(righe) + "\n"


# ---------------------------------------------------------------------------
# Modo prova-vault (sulla validazione)
# ---------------------------------------------------------------------------


def _dentro(p: Path, cartella: Path) -> bool:
    return p == cartella or cartella in p.parents


def fai_il_giro(m, *, etichetta: str, titolo: str, sha_l: str, regole_esame: dict, n_caso: int, pezzo: int,
                impronta_avvio: dict, guardia: dict, p_ris: Path, p_md: Path, p_marc: Path, segno: Path,
                avanzamento: Path, inizio_ts: int, fine: date, prepara_dati, carica_serie, contesto_base: dict,
                prima_di_scrivere=None):
    """Il giro dopo la guardia, uguale per il vault e per la prova. Torna (codice, risultato, file).

    1. ``prepara_dati`` (D1, PRIMA di caricare la serie): file mensili presenti e leggibili, in-sample
       uguale alla campagna. Uno STOP qui non scrive un risultato (D4).
    2. Le impronte dei file si fissano nel marcatore (definitive solo dall'esecuzione del candidato).
    3. ``esegui_giro``: D2/D3, poi il candidato. Prima del candidato nessun risultato (D4), dopo sempre (R5).
    """
    eseguito_prima = candidato_eseguito(p_marc)
    sha_dati = dati_is = file_d1 = None
    try:
        dati_is, file_d1, sha_dati = prepara_dati()
        fissa_dati_nel_marcatore(p_marc, sha_dati)
        ingressi = {**impronta_avvio, "sha256_dati": sha_dati}
        stato_av = controlla_avanzamento(avanzamento, ingressi,
                                         nomi_pezzi(regole_esame["simulazioni_baseline_casuale"], n_caso, pezzo))
    except FermoSuiDati as e:
        return fermo_senza_risultato(p_marc, e, eseguito_prima), None, None
    except Fermo as e:
        # solo fissa_dati_nel_marcatore, e solo se il candidato e' gia' stato eseguito in un tentativo
        # interrotto: i file sono cambiati, lo stesso giro non puo' finire sugli stessi dati (R5)
        ingressi = {**impronta_avvio, "sha256_dati": sha_dati}
        ris = risultato_fermo(e, etichetta, inizio_ts,
                              {**contesto_base, "dati_insample": dati_is, "file_mensili_D1": file_d1},
                              eseguito="in un tentativo precedente, interrotto prima di scrivere il risultato")
        completa_risultato(ris, m, sha_l=sha_l, regole_esame=regole_esame, n_caso=n_caso, impronta_avvio=impronta_avvio,
                           ingressi=ingressi, guardia=guardia, p_marc=p_marc)
        print(f"FERMO: {e.motivo}", flush=True)
        return 2, ris, scrivi_risultato(ris, p_ris, p_md, p_marc, segno, titolo)
    except BaseException as e:  # errore di scarico non previsto, rifiuto della guardia, interruzione
        aggiorna_marcatore(p_marc, "fermo prima di caricare i dati del periodo", motivo=f"{type(e).__name__}: {e}")
        raise
    aggiorna_marcatore(p_marc, "dati del periodo in caricamento: giro in corso")
    contesto = {**contesto_base, "dati_insample": dati_is, "file_mensili_D1": file_d1, "avanzamento_all_avvio": stato_av}
    try:
        ris = esegui_giro(m, etichetta=etichetta, inizio_ts=inizio_ts, fine=fine, carica_serie=carica_serie,
                          n_caso=n_caso, pezzo=pezzo, avanzamento=avanzamento, regole_esame=regole_esame,
                          ingressi=ingressi, contesto=contesto, p_marc=p_marc)
    except FermoSuiDati as e:
        return fermo_senza_risultato(p_marc, e, False), None, None
    except BaseException as e:  # interruzione o errore non voluto: si riprende lo stesso giro
        stato = ("interrotto durante il giro (si riprende lo stesso giro)" if candidato_eseguito(p_marc) else
                 "interrotto prima dell'esecuzione del candidato (si riprende lo stesso giro)")
        aggiorna_marcatore(p_marc, stato, motivo=f"{type(e).__name__}: {e}")
        raise
    completa_risultato(ris, m, sha_l=sha_l, regole_esame=regole_esame, n_caso=n_caso, impronta_avvio=impronta_avvio,
                       ingressi=ingressi, guardia=guardia, p_marc=p_marc)
    if prima_di_scrivere is not None:
        prima_di_scrivere(ris)
    return (2 if ris.get("fermo") else 0), ris, scrivi_risultato(ris, p_ris, p_md, p_marc, segno, titolo)


def _sha_insample(m, dati_is: dict) -> dict:
    return {"file": dati_is["impronte_confrontate"], "sha256_elenco": sha256_json(impronte_attese(m)["attese"])}


def cmd_prova_vault(args) -> int:
    m = carica_moduli(Path(args.worktree))
    etichetta = "prova_validazione"
    cartella = Path(args.cartella).resolve()
    avanzamento = Path(args.avanzamento).resolve() if args.avanzamento else cartella / "avanzamento" / CANDIDATO
    for p in (cartella, avanzamento):
        if _dentro(p, VAULT_COORD) or _dentro(p, AVANZAMENTO_VAULT.parent):
            raise SystemExit(f"STOP: la prova non scrive in {VAULT_COORD} ne' in {AVANZAMENTO_VAULT.parent} (posti del vault)")
    p_ris = cartella / f"{CANDIDATO}_{etichetta}.json"
    p_md = cartella / f"{CANDIDATO}_{etichetta}.md"
    p_marc = cartella / f"{CANDIDATO}_{etichetta}_giro_iniziato.json"
    segno = cartella / f"{CANDIDATO}_{etichetta}_giro_fatto.json"
    sha_l = sha256_lanciatore()
    codice = controlla_codice(m.worktree)
    regole_esame = leggi_regole_esame(m)
    controlla_semi(regole_esame)
    n_caso = args.n_caso if args.n_caso is not None else regole_esame["simulazioni_caso"]
    impronta_avvio = impronta_di_avvio(etichetta=etichetta, sha_l=sha_l, codice=codice, sha_apertura=None,
                                       regole_esame=regole_esame, n_caso=n_caso, pezzo=args.pezzo, worktree=m.worktree,
                                       avanzamento=avanzamento, risultato=p_ris, versioni_impronta=versioni_per_impronta(m))
    guardia = guardia_una_volta(p_ris, p_marc, (p_md, segno), impronta_avvio)
    inizio_d = m.comune.PERIODI["inizio_validazione"]

    def prepara():
        dati_is = prepara_insample_o_fermo(m, scarica=not args.senza_scarico)
        file_d1 = controlla_file_mensili(m, inizio_d, FINE_IN_SAMPLE)  # D1 sui mesi del periodo di prova
        return dati_is, file_d1, {"insample": _sha_insample(m, dati_is), "vault": None}

    def confronto(ris):
        if "come_validazione" in ris and not ris.get("fermo"):
            val_log = [v for v in m.comune.voci_log() if v.get("id") == ID_VAL and v.get("tipo") == "risultato"][-1]
            attesi = {k: v for k, v in val_log.items() if k in ris["come_validazione"]}
            trovati = giro_json(m, ris["come_validazione"])
            ris["confronto_con_la_validazione_del_log"] = confronta(attesi, trovati)
            ris["confronto_con_la_validazione_del_log_oltre_1e-12_relativo"] = confronta(attesi, trovati, tolleranza_rel=1e-12)

    rc, ris, dest = fai_il_giro(
        m, etichetta=etichetta, titolo="PROVA del lanciatore del vault sul periodo di validazione (non è il vault)",
        sha_l=sha_l, regole_esame=regole_esame, n_caso=n_caso, pezzo=args.pezzo, impronta_avvio=impronta_avvio,
        guardia=guardia, p_ris=p_ris, p_md=p_md, p_marc=p_marc, segno=segno, avanzamento=avanzamento,
        inizio_ts=m.comune.PERIODI["inizio_validazione_ts"], fine=FINE_IN_SAMPLE, prepara_dati=prepara,
        carica_serie=lambda: m.quadro.tutto_insample(TF),
        contesto_base={"codice": codice, "nota": "PROVA sul periodo di validazione, non e' il vault"},
        prima_di_scrivere=confronto)
    if ris is None:
        return rc
    cr = ris.get("criterio_vault") or {}
    note = ris.get("note") or {}
    print(json.dumps(pulito({"esito": ris.get("esito"), "motivo": ris.get("motivo"), "condizioni": cr.get("condizioni"),
                             "tasso_del_caso": (ris.get("caso") or {}).get("tasso_del_caso"),
                             "p90": (ris.get("caso") or {}).get("percentile_90"),
                             "controllo_dati_ok": note.get("controllo_dati_ok"),
                             "blocchi_dati": note.get("blocchi_dati"), "avvisi_dati": note.get("avvisi_dati"),
                             "differenze_con_la_validazione": ris.get("confronto_con_la_validazione_del_log"),
                             "differenze_oltre_1e-12": ris.get("confronto_con_la_validazione_del_log_oltre_1e-12_relativo"),
                             "tempi": ris.get("tempi_secondi"), "risultato": str(dest)}), ensure_ascii=False, indent=1))
    if rc:
        return rc
    return 0 if not ris.get("confronto_con_la_validazione_del_log_oltre_1e-12_relativo") else 1


# ---------------------------------------------------------------------------
# Modo vault (solo dopo l'apertura)
# ---------------------------------------------------------------------------


def cmd_vault(args) -> int:
    # 0) posti fissi (R2, R6): nessun argomento sposta worktree, risultato, marcatore o avanzamento
    if Path(args.worktree).resolve() != WORKTREE_DEFAULT.resolve():
        raise SystemExit(f"STOP: il modo vault gira solo sul worktree {WORKTREE_DEFAULT}")
    if args.cartella is not None and Path(args.cartella).resolve() != VAULT_COORD:
        raise SystemExit(f"STOP: il risultato del vault va solo in {VAULT_COORD} (posto fisso)")
    if args.avanzamento is not None and Path(args.avanzamento).resolve() != AVANZAMENTO_VAULT:
        raise SystemExit(f"STOP: l'avanzamento del vault va solo in {AVANZAMENTO_VAULT} (posto fisso)")
    m = carica_moduli(WORKTREE_DEFAULT)
    # 1) PRIMA DI TUTTO: l'apertura del coordinamento, al suo posto fisso. Finche' manca si
    #    solleva VaultChiuso e non si scrive nulla.
    if not m.dati.vault_aperto(COORD_RICERCA):
        raise m.dati.VaultChiuso(f"manca {APERTURA_COORD}: il vault si apre solo dopo la frase del proprietario")
    sha_l = sha256_lanciatore()
    codice = controlla_codice(m.worktree)
    # 2) R4: contenuto dell'apertura e copia accanto al dati.py del candidato
    apertura = controlla_apertura(m, APERTURA_COORD, m.worktree / APERTURA_REL_WORKTREE)
    m.dati.controlla_vault(m.dati.FINE_VAULT)  # ora anche il codice del candidato vede il vault aperto
    regole_esame = leggi_regole_esame(m)
    controlla_semi(regole_esame)
    n_caso = regole_esame["simulazioni_caso"]
    if n_caso != SEMI_CASO_VAULT[1] - SEMI_CASO_VAULT[0] + 1 or SEMI_CASO_VAULT[0] != 0:
        raise SystemExit(f"STOP: parametri.yaml chiede {n_caso} simulazioni del caso, APERTURA.md i semi "
                         f"{SEMI_CASO_VAULT[0]}-{SEMI_CASO_VAULT[1]}")
    segno = m.dati.RADICE_DEFAULT / "data" / "vault" / f"{SIMBOLO}_giro_vault_fatto.json"
    impronta_avvio = impronta_di_avvio(etichetta="vault", sha_l=sha_l, codice=codice, sha_apertura=apertura["sha256"],
                                       regole_esame=regole_esame, n_caso=n_caso, pezzo=args.pezzo, worktree=m.worktree,
                                       avanzamento=AVANZAMENTO_VAULT, risultato=RISULTATO_VAULT,
                                       versioni_impronta=versioni_per_impronta(m))
    # 3) R2: una volta sola; il marcatore si crea qui (O_EXCL), PRIMA di scaricare o leggere i dati del vault
    guardia = guardia_una_volta(RISULTATO_VAULT, MARCATORE_VAULT, (RIASSUNTO_VAULT, segno), impronta_avvio)
    scarica = not args.senza_scarico

    def prepara():  # D1: nessuna candela si carica se un file mensile manca o non si legge
        dati_is = prepara_insample_o_fermo(m, scarica)
        dati_v = prepara_vault(m, scarica)
        return dati_is, dati_v, {"insample": _sha_insample(m, dati_is), "vault": dati_v["impronte"]}

    rc, ris, dest = fai_il_giro(
        m, etichetta="vault", titolo="Vault di BTCUSDT-V10 (Passo 5)", sha_l=sha_l, regole_esame=regole_esame,
        n_caso=n_caso, pezzo=args.pezzo, impronta_avvio=impronta_avvio, guardia=guardia, p_ris=RISULTATO_VAULT,
        p_md=RIASSUNTO_VAULT, p_marc=MARCATORE_VAULT, segno=segno, avanzamento=AVANZAMENTO_VAULT,
        inizio_ts=m.dati.ms_da_data(INIZIO_VAULT), fine=FINE_VAULT, prepara_dati=prepara,
        carica_serie=lambda: m.quadro.carica(TF, FINE_VAULT), contesto_base={"codice": codice, "apertura": apertura})
    if ris is None:
        return rc
    cr = ris.get("criterio_vault") or {}
    print(json.dumps(pulito({"esito": ris.get("esito"), "motivo": ris.get("motivo"), "condizioni": cr.get("condizioni"),
                             "valori": cr.get("valori"), "tasso_del_caso": (ris.get("caso") or {}).get("tasso_del_caso"),
                             "avvisi_dati": (ris.get("note") or {}).get("avvisi_dati"),
                             "risultato": str(dest)}), ensure_ascii=False, indent=1))
    return rc


def cmd_requisiti_apertura(args) -> int:
    """Stampa cosa deve contenere APERTURA.md per questo candidato (nessun dato letto)."""
    codice = controlla_codice(Path(args.worktree).resolve())
    req = requisiti_apertura()
    print(json.dumps({"candidato": CANDIDATO, "requisiti": req, "codice_controllato": codice["ok"],
                      "sha256_lanciatore_informativo": sha256_lanciatore()}, ensure_ascii=False, indent=1))
    print("\n--- testo minimo per APERTURA.md ---\n" + req["testo_minimo"] + "--- fine ---")
    return 0


# ---------------------------------------------------------------------------


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--worktree", default=str(WORKTREE_DEFAULT))
    sub = ap.add_subparsers(dest="modo", required=True)
    p1 = sub.add_parser("parita", help="solo in-sample: riscarica, verifica e rifa' la validazione")
    p1.add_argument("--uscita", required=True, help="file JSON dell'esito")
    p1.add_argument("--senza-scarico", action="store_true")
    p1.add_argument("--senza-costruzione", action="store_true")
    sub.add_parser("requisiti-apertura", aliases=["apertura"], help="cosa deve contenere APERTURA.md per questo candidato")
    p2 = sub.add_parser("prova-vault", help="il codice del vault sul periodo di validazione")
    p2.add_argument("cartella", help="cartella della prova (fuori da research/vault/ del coordinamento)")
    p2.add_argument("--n-caso", type=int, default=None, help="simulazioni del caso (predefinito: parametri.yaml)")
    p2.add_argument("--ferma-sui-dati", action="store_true",
                    help="non cambia nulla: la regola dei dati D1-D3 vale sempre, come nel vault")
    p3 = sub.add_parser("vault", help="il giro vero, solo dopo l'apertura")
    p3.add_argument("cartella", nargs="?", default=None, help=f"se data, deve essere {VAULT_COORD}")
    for p in (p2, p3):
        p.add_argument("--pezzo", type=int, default=PEZZO_DEFAULT, help="semi per file di avanzamento")
        p.add_argument("--avanzamento", default=None)
        p.add_argument("--senza-scarico", action="store_true")
    args = ap.parse_args(argv)
    if getattr(args, "pezzo", PEZZO_DEFAULT) < 10:
        raise SystemExit("--pezzo deve essere almeno 10 (la (b) della campagna vuole almeno 2 simulazioni con trade)")
    try:
        if args.modo == "parita":
            return cmd_parita(args)
        if args.modo in ("requisiti-apertura", "apertura"):
            return cmd_requisiti_apertura(args)
        if args.modo == "prova-vault":
            return cmd_prova_vault(args)
        return cmd_vault(args)
    except Exception as e:  # VaultChiuso e OltreIlVault: messaggio chiaro, codice d'uscita 3
        if type(e).__name__ in ("VaultChiuso", "OltreIlVault"):
            print(f"{type(e).__name__}: {e}", file=sys.stderr)
            return 3
        raise


if __name__ == "__main__":
    sys.exit(main())
