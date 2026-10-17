"""I fatti del Passo 0: controllo dei riferimenti al codice del bot.

Il documento `research/config/regole_dimensione.md` afferma cose sul bot e per
ognuna cita `file:riga`. Un riferimento sbagliato (file rinominato, riga
spostata) rende l'affermazione non verificabile, e un fatto non verificabile
non vale (sezione 3.2 del protocollo: «ogni affermazione con file:riga»).

Qui vivono le funzioni PURE che leggono quei riferimenti e li confrontano con
il repository: estrazione dal testo, conteggio delle righe, controllo che la
riga esista e che contenga il frammento atteso. Niente import dal bot: il
modulo appartiene al protocollo di ricerca (solo libreria standard).
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

#: un riferimento e' «percorso/relativo.ext:riga» oppure «...:riga_da-riga_a».
#: Il percorso parte da una cartella del repo e finisce con un'estensione nota.
_RIFERIMENTO = re.compile(
    r"(?P<file>(?:bot|backtesting|scripts|research)/[\w./-]+\.(?:py|sh|md|txt|yaml))"
    r":(?P<da>\d+)(?:-(?P<a>\d+))?"
)


@dataclass(frozen=True)
class Riferimento:
    """Un rimando a un intervallo di righe di un file del repository."""

    file: str
    riga_da: int
    riga_a: int

    @property
    def testo(self) -> str:
        if self.riga_a == self.riga_da:
            return f"{self.file}:{self.riga_da}"
        return f"{self.file}:{self.riga_da}-{self.riga_a}"


def estrai_riferimenti(testo: str) -> list[Riferimento]:
    """Tutti i riferimenti `file:riga` o `file:riga-riga` del testo, nell'ordine
    in cui compaiono. Un intervallo scritto al contrario (es. 50-40) viene
    raddrizzato: e' un refuso, non un rimando a zero righe."""
    out: list[Riferimento] = []
    for m in _RIFERIMENTO.finditer(testo):
        da = int(m.group("da"))
        a = int(m.group("a")) if m.group("a") else da
        out.append(Riferimento(m.group("file"), min(da, a), max(da, a)))
    return out


def conta_righe(percorso: Path) -> int:
    """Numero di righe del file (0 se non esiste). Si legge come testo con
    sostituzione dei caratteri non decodificabili: qui conta solo quante righe
    ci sono, non cosa dicono."""
    if not percorso.is_file():
        return 0
    with percorso.open("r", encoding="utf-8", errors="replace") as fh:
        return sum(1 for _ in fh)


def verifica_riferimenti(riferimenti: list[Riferimento], radice: Path) -> list[str]:
    """I problemi trovati (lista vuota = tutto a posto). Un riferimento e' buono
    se il file esiste sotto `radice` e la riga finale non supera la lunghezza
    del file. Il controllo e' su ogni riferimento, non si ferma al primo:
    chi corregge il documento vuole l'elenco completo."""
    problemi: list[str] = []
    righe_per_file: dict[str, int] = {}
    for r in riferimenti:
        if r.file not in righe_per_file:
            righe_per_file[r.file] = conta_righe(radice / r.file)
        n = righe_per_file[r.file]
        if n == 0:
            problemi.append(f"{r.testo}: file mancante")
        elif r.riga_a > n:
            problemi.append(f"{r.testo}: il file ha solo {n} righe")
    return problemi


def riga(percorso: Path, numero: int) -> str:
    """Il contenuto della riga `numero` (da 1), o stringa vuota se non c'e'."""
    if numero < 1 or not percorso.is_file():
        return ""
    with percorso.open("r", encoding="utf-8", errors="replace") as fh:
        for i, contenuto in enumerate(fh, start=1):
            if i == numero:
                return contenuto.rstrip("\n")
    return ""


def verifica_ancore(ancore: dict[str, str], radice: Path) -> list[str]:
    """Per ogni `file:riga` -> frammento atteso, controlla che la riga lo
    contenga. E' il controllo forte: non basta che la riga esista, deve dire
    cio' che il documento le attribuisce. Ritorna i problemi (vuoto = ok)."""
    problemi: list[str] = []
    for ref, atteso in ancore.items():
        rifs = estrai_riferimenti(ref)
        if len(rifs) != 1:
            problemi.append(f"{ref}: non e' un riferimento valido")
            continue
        r = rifs[0]
        contenuto = riga(radice / r.file, r.riga_da)
        if atteso not in contenuto:
            problemi.append(f"{r.testo}: atteso «{atteso}», trovato «{contenuto.strip()}»")
    return problemi


def sezioni_mancanti(testo: str, attese: list[str]) -> list[str]:
    """Le intestazioni Markdown (`#`, `##`, ...) attese ma assenti dal testo.
    Il confronto e' sul testo dell'intestazione, senza i cancelletti."""
    presenti = {
        m.group(1).strip()
        for m in re.finditer(r"^#{1,6}\s+(.+?)\s*$", testo, flags=re.MULTILINE)
    }
    return [s for s in attese if s not in presenti]


#: Le parole che compaiono nei nomi delle variabili sensibili del bot (chiavi
#: API, segreti, token, password, chiavi private, credenziali Firebase).
#: Senza distinzione fra maiuscole e minuscole: un `binance_api_secret: ...` in
#: YAML o un `"private_key": "..."` in JSON sono segreti quanto `API_SECRET=`.
_PAROLE_SENSIBILI = r"(?:api_key|secret|token|password|private_key|credential)"

#: Un valore «vero» dopo «=» o «:»: almeno 8 caratteri senza spazi, fra quelli
#: tipici di chiavi, token base64/JWT e intestazioni PEM (`-----BEGIN ...`).
#: Il nome puo' essere seguito da altre parole (`CREDENTIALS_JSON`) e, in JSON,
#: da una virgoletta di chiusura prima dei due punti.
_SEGRETO = re.compile(
    r"\w*" + _PAROLE_SENSIBILI + r"\w*[\"']?\s*[=:]\s*[\"']?[A-Za-z0-9_\-/+=.]{8,}",
    flags=re.IGNORECASE,
)


def contiene_segreti(testo: str) -> list[str]:
    """Righe che sembrano assegnare un valore a una chiave, un segreto, un
    token, una password, una chiave privata o delle credenziali (es.
    `BINANCE_API_SECRET=abc`, `FIREBASE_PRIVATE_KEY=...`,
    `"private_key": "-----BEGIN PRIVATE KEY-----"`). Il documento deve
    riportare solo i NOMI dei parametri (sezione 2 del protocollo) e vive in
    un repo pubblico: questo controllo e' l'unica rete. Un nome seguito da «=»
    e da niente, o da un segnaposto fra parentesi, non e' un valore."""
    sospette: list[str] = []
    for linea in testo.splitlines():
        if _SEGRETO.search(linea):
            sospette.append(linea.strip())
    return sospette
