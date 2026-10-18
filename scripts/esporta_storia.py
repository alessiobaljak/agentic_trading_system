"""
ESPORTA LA STORIA — copia nel repo i dati che oggi vivono solo in Firebase e sulla
macchina.

Perche' (18 ott 2026, richiesta del proprietario di «storicizzare tutti i dati
raccolti», `docs/storia/README.md` sezione 7): i trade del paper, il registro del gate
con le specifiche delle strategie generate e le misure della macchina (`data/...`) non
sono nel repository. Un reset del paper (`scripts/reset_paper.py`) cancella i trade
senza copia, e senza le specifiche le coppie del vecchio gate non si possono piu'
rigiocare. Prima di riscrivere il gate se ne fa una fotografia.

Cosa scrive, in `ops/results/archivio_AAAAMMGG/` (l'agente ops committa tutto cio' che
sta sotto `ops/results`, quindi la copia arriva su GitHub insieme alla risposta):
  firestore/<collection>.json.gz   tutti i documenti, {id: dati}
  rtdb/<nodo>.json.gz              ogni nodo di primo livello del Realtime DB
  macchina/<cartella>.tar.gz       le cartelle di misura in `data/` (senza file .env)
  INDICE.json                      per ogni file: documenti, byte, SHA-256; e cosa e'
                                   rimasto fuori, con il motivo
Sullo schermo (cioe' nella risposta ops) un riepilogo corto.

SICUREZZA. Il repository e' pubblico. Ogni valore di testo sotto una chiave che sa di
segreto (token, password, chiave, credenziale...) diventa "[OSCURATO]", ogni testo
passa da `redact` dell'agente ops, gli indirizzi e-mail diventano "[EMAIL]", e i file
.env, le chiavi e gli account di servizio non entrano negli archivi della macchina. Nei
file di testo della macchina (json, jsonl, csv, md, txt) vale la stessa pulizia.

LETTURE. Firestore ha una quota giornaliera, e a settembre e' gia' finita una volta
(backlog J14): prima si contano i documenti di ogni collection (una lettura ogni mille),
poi si copiano in ordine di importanza finche' il totale resta sotto `TETTO_LETTURE`.
Le collection lasciate fuori sono scritte nell'indice e nel riepilogo: si copiano un
altro giorno.

Senza Firebase collegato non scrive niente (cosi' i test e le macchine di sviluppo non
lasciano archivi vuoti nel repo).

Uso (sulla VPS, anche dal canale ops con la voce `esporta-storia`):
    .venv/bin/python -m scripts.esporta_storia
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import io
import json
import os
import re
import sys
import tarfile
from datetime import datetime, timezone
from typing import Any, Optional

from scripts.ops_agent import APP_DIR, RES_DIR, redact

#: quante letture di documenti Firestore al massimo in un giro (la quota gratuita e'
#: di 50.000 al giorno, e il bot ne usa 7-9.000: ops 0449, 0527)
TETTO_LETTURE = int(os.getenv("ESPORTA_TETTO_LETTURE", "20000"))
#: un file oltre questa dimensione (compresso) non si scrive: GitHub rifiuta i file
#: sopra i 100 MB
TETTO_FILE_MB = float(os.getenv("ESPORTA_TETTO_FILE_MB", "90"))
#: tutto l'archivio di un giro, compresso
TETTO_TOTALE_MB = float(os.getenv("ESPORTA_TETTO_TOTALE_MB", "200"))

#: prima le collection che non si possono rifare (i trade, il registro e le specifiche
#: delle strategie), poi le misure; le altre in ordine alfabetico, dopo queste
PRIORITA = (
    "trades", "strategy_registry", "discovered_strategies", "strategy_params",
    "strategy_weights", "gate_history", "gate_autopsy", "drift", "learning",
    "calibration", "supervisor", "selector", "portfolio", "memory", "insights",
    "report_giornaliero", "dashboard", "asset_scores", "ai_hypotheses", "ai_reports",
    "ai_shadow",
)
#: chiavi il cui valore di testo non deve finire in un repo pubblico
CHIAVE_SEGRETA = re.compile(
    r"(?i)(api[_-]?key|secret|token|password|passwd|credential|private[_-]?key"
    r"|service[_-]?account|chat[_-]?id|webhook)")
EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
#: nomi di file della macchina che non si archiviano mai
FILE_ESCLUSI = re.compile(
    r"(?i)(^\.env|\.env$|\.env\.|service[-_]?account|\.pem$|\.key$|allowlist|"
    r"credential|token)")
TESTO = (".json", ".jsonl", ".csv", ".md", ".txt", ".tsv")


def oscura(valore: Any, chiave: str = "") -> Any:
    """Toglie da una struttura cio' che somiglia a un segreto o a un indirizzo."""
    if isinstance(valore, dict):
        return {EMAIL.sub("[EMAIL]", str(k)): oscura(v, str(k)) for k, v in valore.items()}
    if isinstance(valore, (list, tuple)):
        return [oscura(v, chiave) for v in valore]
    if isinstance(valore, str):
        if CHIAVE_SEGRETA.search(chiave):
            return "[OSCURATO]"
        return EMAIL.sub("[EMAIL]", redact(valore))
    if CHIAVE_SEGRETA.search(chiave) and "chat" in chiave.lower():
        # un numero di chat Telegram e' un indirizzo, non una misura
        return "[OSCURATO]"
    return valore


def _json_gz(dati: Any) -> bytes:
    testo = json.dumps(oscura(dati), ensure_ascii=False, sort_keys=True, default=str)
    return gzip.compress(testo.encode("utf-8"), mtime=0)


def _pulisci_testo(nome: str, grezzo: bytes) -> bytes:
    """Un file di testo della macchina, con la stessa pulizia di Firebase."""
    try:
        testo = grezzo.decode("utf-8")
    except UnicodeDecodeError:
        return grezzo
    if nome.endswith(".json"):
        try:
            return json.dumps(oscura(json.loads(testo)), ensure_ascii=False,
                              default=str).encode("utf-8")
        except ValueError:
            pass
    if nome.endswith(".jsonl"):
        righe = []
        for riga in testo.splitlines():
            try:
                righe.append(json.dumps(oscura(json.loads(riga)), ensure_ascii=False,
                                        default=str))
            except ValueError:
                righe.append(EMAIL.sub("[EMAIL]", redact(riga)))
        return ("\n".join(righe) + "\n").encode("utf-8")
    return EMAIL.sub("[EMAIL]", redact(testo)).encode("utf-8")


def _tar_gz(cartella: str, nomi: list[str]) -> tuple[bytes, int]:
    """Un archivio dei file `nomi` (percorsi relativi a `cartella`), puliti."""
    buf = io.BytesIO()
    n = 0
    with tarfile.open(fileobj=buf, mode="w:gz") as tar:
        for rel in nomi:
            percorso = os.path.join(cartella, rel)
            with open(percorso, "rb") as f:
                grezzo = f.read()
            if rel.lower().endswith(TESTO):
                grezzo = _pulisci_testo(rel.lower(), grezzo)
            info = tarfile.TarInfo(rel)
            info.size = len(grezzo)
            info.mtime = int(os.path.getmtime(percorso))
            tar.addfile(info, io.BytesIO(grezzo))
            n += 1
    return buf.getvalue(), n


def _ordine(collezioni: list[str]) -> list[str]:
    prima = [c for c in PRIORITA if c in collezioni]
    return prima + sorted(c for c in collezioni if c not in PRIORITA)


class Archivio:
    """Scrive i file e tiene l'indice, con i tetti di dimensione."""

    def __init__(self, uscita: str) -> None:
        self.uscita = uscita
        self.file: list[dict] = []
        self.fuori: list[dict] = []
        self.byte = 0

    def scrivi(self, rel: str, dati: bytes, voci: int, tipo: str) -> bool:
        mb = len(dati) / 1e6
        if mb > TETTO_FILE_MB:
            self.fuori.append({"file": rel, "motivo": f"{mb:.1f} MB compressi, oltre "
                               f"il tetto di {TETTO_FILE_MB:g} MB per file"})
            return False
        if (self.byte + len(dati)) / 1e6 > TETTO_TOTALE_MB:
            self.fuori.append({"file": rel, "motivo": f"tetto dell'archivio "
                               f"({TETTO_TOTALE_MB:g} MB) raggiunto"})
            return False
        percorso = os.path.join(self.uscita, rel)
        os.makedirs(os.path.dirname(percorso), exist_ok=True)
        with open(percorso, "wb") as f:
            f.write(dati)
        self.byte += len(dati)
        self.file.append({"file": rel, "tipo": tipo, "voci": voci, "byte": len(dati),
                          "sha256": hashlib.sha256(dati).hexdigest()})
        return True


def esporta(fb, uscita: str, cartella_dati: Optional[str],
            tetto_letture: int = TETTO_LETTURE) -> dict:
    """Esporta Firestore, RTDB e le cartelle di `cartella_dati` in `uscita`.
    Ritorna l'indice (lo stesso che finisce in INDICE.json)."""
    arch = Archivio(uscita)
    letture = 0

    # 1) Firestore: conta, poi copia in ordine di importanza fino al tetto
    for nome in _ordine(fb.elenca_collezioni()):
        quanti = fb.count_collection(nome, chi="esporta_storia")
        letture += max(1, (quanti + 999) // 1000)
        if letture + quanti > tetto_letture:
            arch.fuori.append({"file": f"firestore/{nome}.json.gz", "motivo":
                               f"{quanti} documenti: oltre il tetto di {tetto_letture} "
                               f"letture per giro (gia' usate {letture})"})
            continue
        docs = fb.documenti(nome, chi="esporta_storia")
        letture += len(docs)
        arch.scrivi(f"firestore/{nome}.json.gz", _json_gz(docs), len(docs), "firestore")

    # 2) Realtime DB: un file per nodo di primo livello
    for nodo in fb.figli_rtdb("/"):
        dati = fb.get_rtdb(f"/{nodo}")
        voci = len(dati) if isinstance(dati, (dict, list)) else 1
        arch.scrivi(f"rtdb/{nodo}.json.gz", _json_gz(dati), voci, "rtdb")

    # 3) la macchina: una cartella di data/ per archivio, i file sciolti insieme
    if cartella_dati and os.path.isdir(cartella_dati):
        sciolti = []
        for voce in sorted(os.listdir(cartella_dati)):
            percorso = os.path.join(cartella_dati, voce)
            if FILE_ESCLUSI.search(voce):
                arch.fuori.append({"file": f"data/{voce}", "motivo": "nome da file "
                                   "riservato (.env, chiavi, credenziali): mai archiviato"})
                continue
            if os.path.isfile(percorso):
                sciolti.append(voce)
                continue
            if not os.path.isdir(percorso):
                continue
            nomi = []
            for radice, _, files in os.walk(percorso):
                for f in sorted(files):
                    rel = os.path.relpath(os.path.join(radice, f), cartella_dati)
                    if FILE_ESCLUSI.search(f):
                        arch.fuori.append({"file": f"data/{rel}", "motivo": "nome da "
                                           "file riservato: mai archiviato"})
                    else:
                        nomi.append(rel)
            if nomi:
                dati, n = _tar_gz(cartella_dati, nomi)
                arch.scrivi(f"macchina/{voce}.tar.gz", dati, n, "macchina")
        if sciolti:
            dati, n = _tar_gz(cartella_dati, sciolti)
            arch.scrivi("macchina/file_sciolti.tar.gz", dati, n, "macchina")

    indice = {
        "creato": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        "letture_firestore": letture,
        "tetto_letture": tetto_letture,
        "byte_totali": arch.byte,
        "file": arch.file,
        "fuori": arch.fuori,
    }
    os.makedirs(uscita, exist_ok=True)
    with open(os.path.join(uscita, "INDICE.json"), "w", encoding="utf-8") as f:
        json.dump(indice, f, ensure_ascii=False, indent=1)
    return indice


def riepilogo(indice: dict, uscita_rel: str) -> str:
    righe = [f"Archivio in {uscita_rel} ({indice['creato']})",
             f"file scritti: {len(indice['file'])} · {indice['byte_totali'] / 1e6:.1f} MB "
             f"compressi · letture Firestore: {indice['letture_firestore']} "
             f"(tetto {indice['tetto_letture']})", ""]
    for f in indice["file"]:
        righe.append(f"  {f['file']:<48} {f['voci']:>7} voci {f['byte'] / 1e3:>9.1f} kB  "
                     f"sha256 {f['sha256'][:12]}")
    if indice["fuori"]:
        righe += ["", "RIMASTI FUORI (da copiare un altro giorno o a mano):"]
        righe += [f"  {f['file']}: {f['motivo']}" for f in indice["fuori"]]
    return "\n".join(righe)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Copia Firebase e data/ in ops/results/archivio_*.")
    ap.add_argument("--uscita", default=None,
                    help="cartella di destinazione (default ops/results/archivio_AAAAMMGG)")
    args = ap.parse_args(argv)

    from bot.core.firebase_client import get_firebase

    fb = get_firebase()
    if not fb.is_live:
        print("Firebase non collegato: niente da esportare, nessun file scritto.")
        return 0
    giorno = datetime.now(timezone.utc).strftime("%Y%m%d")
    uscita = args.uscita or os.path.join(RES_DIR, f"archivio_{giorno}")
    indice = esporta(fb, uscita, os.path.join(APP_DIR, "data"))
    print(riepilogo(indice, os.path.relpath(uscita, APP_DIR)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
