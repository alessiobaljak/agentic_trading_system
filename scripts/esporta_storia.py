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

TEMPO. Il canale ops ferma un comando dopo 900 secondi: il primo giro (ops 0624) e' stato
fermato a meta' delle cartelle della macchina. Ci si ferma da soli dopo `TEMPO_MAX_S`, con
l'indice salvato; rilanciando, si riprende da dove ci si era fermati senza rileggere
Firestore. Le cartelle grandi si dividono in parti.

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
import time
from datetime import datetime, timezone
from typing import Any, Optional

from scripts.ops_agent import APP_DIR, RES_DIR, redact

#: quante letture di documenti Firestore al massimo in un giro (la quota gratuita e'
#: di 50.000 al giorno, e il bot ne usa 7-9.000: ops 0449, 0527)
TETTO_LETTURE = int(os.getenv("ESPORTA_TETTO_LETTURE", "20000"))
#: un file oltre questa dimensione (compresso) non si scrive: GitHub rifiuta i file
#: sopra i 100 MB
TETTO_FILE_MB = float(os.getenv("ESPORTA_TETTO_FILE_MB", "90"))
#: tutto l'archivio, compresso
TETTO_TOTALE_MB = float(os.getenv("ESPORTA_TETTO_TOTALE_MB", "200"))
#: il canale ops ferma un comando dopo 900 s (`OPS_TIMEOUT_S`): ci si ferma prima, con
#: l'indice salvato, e il giro dopo riprende
TEMPO_MAX_S = float(os.getenv("ESPORTA_TEMPO_MAX_S", "780"))
#: una cartella della macchina oltre questo peso (non compresso) si divide in parti
PARTE_MB_GREZZI = float(os.getenv("ESPORTA_PARTE_MB", "300"))

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


#: «"chiave segreta": "valore"» dentro un testo JSON, trovato senza leggere il JSON: i file
#: della macchina sono grandi, e leggerli riga per riga ha fatto scadere il primo giro
#: (ops 0624, 900 secondi). I numeri restano (i conteggi dei token sono misure), tranne
#: il numero della chat Telegram, che e' un indirizzo.
COPPIA_SEGRETA = re.compile(
    r'("[^"\n]*(?:api[_-]?key|secret|token|password|passwd|credential|private[_-]?key'
    r'|service[_-]?account|chat[_-]?id|webhook)[^"\n]*"\s*:\s*)"(?:[^"\\\n]|\\.)*"', re.I)
CHAT_NUMERO = re.compile(r'("[^"\n]*chat[_-]?id[^"\n]*"\s*:\s*)-?\d+', re.I)


def _pulisci_testo(testo: str) -> str:
    """Un testo della macchina, con la pulizia di `oscura` fatta sul testo."""
    testo = COPPIA_SEGRETA.sub(r'\1"[OSCURATO]"', testo)
    testo = CHAT_NUMERO.sub(r'\1"[OSCURATO]"', testo)
    return EMAIL.sub("[EMAIL]", redact(testo))


def _pulisci_file(nome: str, grezzo: bytes) -> bytes:
    """Il contenuto di un file della macchina da mettere nell'archivio: i testi puliti,
    i `.gz` aperti, puliti e richiusi, il resto com'e'."""
    nome = nome.lower()
    if nome.endswith(".gz"):
        try:
            dentro = gzip.decompress(grezzo).decode("utf-8")
        except (OSError, EOFError, UnicodeDecodeError):
            return grezzo
        return gzip.compress(_pulisci_testo(dentro).encode("utf-8"), mtime=0)
    if not nome.endswith(TESTO):
        return grezzo
    try:
        return _pulisci_testo(grezzo.decode("utf-8")).encode("utf-8")
    except UnicodeDecodeError:
        return grezzo


def _parti(cartella: str, nomi: list[str]) -> list[list[str]]:
    """I file divisi in parti di al massimo PARTE_MB_GREZZI MB non compressi, cosi'
    ogni archivio resta sotto il tetto di GitHub e un giro interrotto non perde tutto."""
    parti: list[list[str]] = [[]]
    peso = 0.0
    for rel in nomi:
        mb = os.path.getsize(os.path.join(cartella, rel)) / 1e6
        if parti[-1] and peso + mb > PARTE_MB_GREZZI:
            parti.append([])
            peso = 0.0
        parti[-1].append(rel)
        peso += mb
    return parti


def _ordine(collezioni: list[str]) -> list[str]:
    prima = [c for c in PRIORITA if c in collezioni]
    return prima + sorted(c for c in collezioni if c not in PRIORITA)


def _sha(percorso: str) -> str:
    h = hashlib.sha256()
    with open(percorso, "rb") as f:
        for blocco in iter(lambda: f.read(1 << 20), b""):
            h.update(blocco)
    return h.hexdigest()


class TempoFinito(Exception):
    """Il giro ha usato il suo tempo: si salva l'indice e si riprende al giro dopo."""


class Archivio:
    """Scrive i file e tiene l'indice, con i tetti di dimensione e di tempo.

    RIPRENDE DA DOVE SI E' FERMATO (18 ott 2026). Il canale ops ferma un comando dopo 900
    secondi (`OPS_TIMEOUT_S`): il primo giro e' stato fermato a meta' delle cartelle della
    macchina. Ogni file si scrive per intero e poi si rinomina, l'indice si riscrive dopo
    ogni file, e un file che c'e' gia' non si rifa': un secondo giro non rilegge Firestore
    (la quota) e continua dalla cartella dove si era fermato."""

    def __init__(self, uscita: str, tempo_max_s: float = TEMPO_MAX_S) -> None:
        self.uscita = uscita
        self.file: list[dict] = []
        self.fuori: list[dict] = []
        self.byte = 0
        self.nuovi = 0
        self.scadenza = time.monotonic() + tempo_max_s
        self.cartelle_finite: list[str] = []
        indice = os.path.join(uscita, "INDICE.json")
        if os.path.exists(indice):
            with open(indice, encoding="utf-8") as f:
                vecchio = json.load(f)
            self.file = vecchio.get("file", [])
            self.cartelle_finite = vecchio.get("cartelle_finite", [])
        noti = {f["file"] for f in self.file}
        # i file scritti da un giro fermato prima di scrivere l'indice
        for radice, _, files in os.walk(uscita):
            for nome in sorted(files):
                rel = os.path.relpath(os.path.join(radice, nome), uscita)
                if rel == "INDICE.json" or rel.endswith(".tmp") or rel in noti:
                    continue
                percorso = os.path.join(radice, nome)
                self.file.append({"file": rel, "tipo": rel.split(os.sep, 1)[0], "voci": None,
                                  "byte": os.path.getsize(percorso), "sha256": _sha(percorso)})
                if rel.startswith("macchina" + os.sep) and "_parte" not in rel:
                    self.cartelle_finite.append(nome[:-len(".tar.gz")])
        self.byte = sum(f["byte"] for f in self.file)

    def fatto(self, rel: str) -> bool:
        return os.path.exists(os.path.join(self.uscita, rel))

    def controlla_tempo(self) -> None:
        if time.monotonic() > self.scadenza:
            raise TempoFinito()

    def _salva_indice(self, letture: int, tetto_letture: int, completo: bool) -> dict:
        indice = {
            "creato": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
            "completo": completo,
            "letture_firestore": letture,
            "tetto_letture": tetto_letture,
            "byte_totali": self.byte,
            "file": self.file,
            "cartelle_finite": self.cartelle_finite,
            "fuori": self.fuori,
        }
        os.makedirs(self.uscita, exist_ok=True)
        tmp = os.path.join(self.uscita, "INDICE.json.tmp")
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(indice, f, ensure_ascii=False, indent=1)
        os.replace(tmp, os.path.join(self.uscita, "INDICE.json"))
        return indice

    def _accetta(self, rel: str, byte: int) -> bool:
        mb = byte / 1e6
        if mb > TETTO_FILE_MB:
            self.fuori.append({"file": rel, "motivo": f"{mb:.1f} MB compressi, oltre "
                               f"il tetto di {TETTO_FILE_MB:g} MB per file"})
            return False
        if (self.byte + byte) / 1e6 > TETTO_TOTALE_MB:
            self.fuori.append({"file": rel, "motivo": f"tetto dell'archivio "
                               f"({TETTO_TOTALE_MB:g} MB) raggiunto"})
            return False
        return True

    def _registra(self, rel: str, percorso: str, voci: int, tipo: str) -> None:
        byte = os.path.getsize(percorso)
        self.byte += byte
        self.nuovi += 1
        self.file.append({"file": rel, "tipo": tipo, "voci": voci, "byte": byte,
                          "sha256": _sha(percorso)})
        print(f"[esporta] {rel}: {voci} voci, {byte / 1e6:.1f} MB", flush=True)

    def scrivi(self, rel: str, dati: bytes, voci: int, tipo: str) -> bool:
        if not self._accetta(rel, len(dati)):
            return False
        percorso = os.path.join(self.uscita, rel)
        os.makedirs(os.path.dirname(percorso), exist_ok=True)
        with open(percorso + ".tmp", "wb") as f:
            f.write(dati)
        os.replace(percorso + ".tmp", percorso)
        self._registra(rel, percorso, voci, tipo)
        return True

    def scrivi_tar(self, rel: str, cartella: str, nomi: list[str]) -> bool:
        """Un archivio dei file `nomi` (relativi a `cartella`), puliti, scritto su disco
        man mano: niente archivi interi in memoria."""
        percorso = os.path.join(self.uscita, rel)
        os.makedirs(os.path.dirname(percorso), exist_ok=True)
        with tarfile.open(percorso + ".tmp", mode="w:gz", compresslevel=6) as tar:
            for nome in nomi:
                self.controlla_tempo()
                origine = os.path.join(cartella, nome)
                with open(origine, "rb") as f:
                    grezzo = _pulisci_file(nome, f.read())
                info = tarfile.TarInfo(nome)
                info.size = len(grezzo)
                info.mtime = int(os.path.getmtime(origine))
                tar.addfile(info, io.BytesIO(grezzo))
        if not self._accetta(rel, os.path.getsize(percorso + ".tmp")):
            os.remove(percorso + ".tmp")
            return False
        os.replace(percorso + ".tmp", percorso)
        self._registra(rel, percorso, len(nomi), "macchina")
        return True


def _file_della_cartella(arch: Archivio, cartella_dati: str, voce: str) -> list[str]:
    nomi = []
    for radice, _, files in os.walk(os.path.join(cartella_dati, voce)):
        for f in sorted(files):
            rel = os.path.relpath(os.path.join(radice, f), cartella_dati)
            if FILE_ESCLUSI.search(f):
                arch.fuori.append({"file": f"data/{rel}", "motivo": "nome da file "
                                   "riservato: mai archiviato"})
            else:
                nomi.append(rel)
    return sorted(nomi)


def esporta(fb, uscita: str, cartella_dati: Optional[str],
            tetto_letture: int = TETTO_LETTURE, tempo_max_s: float = TEMPO_MAX_S) -> dict:
    """Esporta Firestore, RTDB e le cartelle di `cartella_dati` in `uscita`, riprendendo
    da un giro precedente se c'e'. Ritorna l'indice (lo stesso di INDICE.json)."""
    arch = Archivio(uscita, tempo_max_s)
    letture = 0
    try:
        # 1) Firestore: conta, poi copia in ordine di importanza fino al tetto
        for nome in _ordine(fb.elenca_collezioni()):
            rel = f"firestore/{nome}.json.gz"
            if arch.fatto(rel):
                continue
            arch.controlla_tempo()
            quanti = fb.count_collection(nome, chi="esporta_storia")
            letture += max(1, (quanti + 999) // 1000)
            if letture + quanti > tetto_letture:
                arch.fuori.append({"file": rel, "motivo": f"{quanti} documenti: oltre il "
                                   f"tetto di {tetto_letture} letture per giro (gia' usate "
                                   f"{letture})"})
                continue
            docs = fb.documenti(nome, chi="esporta_storia")
            letture += len(docs)
            arch.scrivi(rel, _json_gz(docs), len(docs), "firestore")
            arch._salva_indice(letture, tetto_letture, False)

        # 2) Realtime DB: un file per nodo di primo livello
        for nodo in fb.figli_rtdb("/"):
            rel = f"rtdb/{nodo}.json.gz"
            if arch.fatto(rel):
                continue
            arch.controlla_tempo()
            dati = fb.get_rtdb(f"/{nodo}")
            voci = len(dati) if isinstance(dati, (dict, list)) else 1
            arch.scrivi(rel, _json_gz(dati), voci, "rtdb")
            arch._salva_indice(letture, tetto_letture, False)

        # 3) la macchina: una cartella di data/ per archivio (diviso in parti se grande),
        #    i file sciolti insieme
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
                if not os.path.isdir(percorso) or voce in arch.cartelle_finite:
                    continue
                parti = _parti(cartella_dati, _file_della_cartella(arch, cartella_dati, voce))
                for i, nomi in enumerate(parti, 1):
                    if not nomi:
                        continue
                    rel = (f"macchina/{voce}.tar.gz" if len(parti) == 1
                           else f"macchina/{voce}_parte{i}.tar.gz")
                    if arch.fatto(rel):
                        continue
                    arch.scrivi_tar(rel, cartella_dati, nomi)
                    arch._salva_indice(letture, tetto_letture, False)
                arch.cartelle_finite.append(voce)
                arch._salva_indice(letture, tetto_letture, False)
            if sciolti and not arch.fatto("macchina/file_sciolti.tar.gz"):
                arch.scrivi_tar("macchina/file_sciolti.tar.gz", cartella_dati, sciolti)
    except TempoFinito:
        arch.fuori.append({"file": "(il resto)", "motivo": f"tempo del giro finito "
                           f"({tempo_max_s:g} s): rilanciare esporta-storia, riprende da qui"})
        indice = arch._salva_indice(letture, tetto_letture, False)
        indice["nuovi"] = arch.nuovi
        return indice
    indice = arch._salva_indice(letture, tetto_letture, True)
    indice["nuovi"] = arch.nuovi
    return indice


def riepilogo(indice: dict, uscita_rel: str) -> str:
    stato = ("COMPLETO" if indice["completo"]
             else "DA CONTINUARE: rilanciare esporta-storia, riprende da dove si e' fermato")
    righe = [f"Archivio in {uscita_rel} ({indice['creato']}): {stato}",
             f"file: {len(indice['file'])} ({indice.get('nuovi', 0)} scritti in questo giro) · "
             f"{indice['byte_totali'] / 1e6:.1f} MB compressi · letture Firestore in questo "
             f"giro: {indice['letture_firestore']} (tetto {indice['tetto_letture']})", ""]
    for f in indice["file"]:
        voci = "?" if f.get("voci") is None else f["voci"]
        righe.append(f"  {f['file']:<48} {voci:>7} voci {f['byte'] / 1e3:>9.1f} kB  "
                     f"sha256 {f['sha256'][:12]}")
    if indice["fuori"]:
        righe += ["", "RIMASTI FUORI (con il motivo):"]
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
