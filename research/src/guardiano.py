#!/usr/bin/env python3
"""Il guardiano del protocollo di ricerca (PROTOCOLLO.md, sezione 2).

E' un hook `PreToolUse` di Claude Code: viene eseguito PRIMA di ogni azione del
modello (lettura, scrittura, ricerca, comando) e decide se lasciarla passare.
Riceve su stdin un JSON con `tool_name`, `tool_input` e `cwd`; risponde con il
codice di uscita: 0 = consenti, 2 = blocca (il testo su stderr e' il motivo
mostrato al modello).

Perche' esiste: durante una campagna su una moneta il modello non deve vedere
log, ipotesi e risultati delle altre monete, ne' i dati del bot costruiti sul
periodo del vault. Una regola scritta e' disciplina; questo e' un blocco che non
dipende dalla buona volonta' di chi lavora.

Come decide:
  * legge il marcatore `<radice>/research/.sessione` (JSON, mai in git). Se non
    c'e' o e' vuoto, non fa nulla: le sessioni che non fanno ricerca non devono
    accorgersi del guardiano. Se c'e' ma e' rotto, blocca: un marcatore
    illeggibile e' un errore da sistemare, non da ignorare;
  * `{"tipo": "campagna", "simbolo": "X"}` -> lista BIANCA (Passo 3): solo i
    percorsi ammessi della campagna; tutto il resto e' vietato;
  * `{"tipo": "coordinamento"}` -> lista NERA: tutto ammesso tranne i
    `percorsi_vietati`, i segreti e `research/data/vault/` finche' il vault e'
    chiuso (manca `research/vault/APERTURA.md`);
  * in modalita' attiva qualunque errore imprevisto blocca (fail-closed): un
    guardiano che si rompe non deve aprire la porta.

Cosa ha insegnato la revisione avversaria (test_guardiano_revisione_2.py):
giudicare il TESTO di un percorso non basta. Il percorso va risolto sul disco
(un link simbolico dentro la cartella ammessa puo' puntare ovunque); tutto cio'
che la shell espande DOPO il giudizio (`$(...)`, `${...}`, graffe, `*`, `\\x2f`)
va rifiutato o espanso prima; i prefissi trasparenti (`command`, `exec`,
`timeout`, `sh -c`) non devono nascondere il programma vero; i comandi che
leggono tutto il repo senza nominare un percorso (`grep -r`, `find`,
`git grep`, `git log -p`, `python -c`) vanno bloccati in campagna; e il
marcatore, il guardiano stesso e la lista dei vietati non devono essere
riscrivibili da chi e' sorvegliato.

Il guardiano NON legge il contenuto dei file che il modello scrive ed esegue:
uno script in una cartella ammessa puo' fare cio' che vuole. E' una barriera
contro la deriva e la distrazione, non contro un avversario con il codice in
mano; il protocollo lo sa (sezione 2).

Solo libreria standard, per essere veloce (< 1 s) e non dipendere da nulla.
Le funzioni di giudizio ricevono percorso e contesto e restituiscono un
verdetto, per poter essere provate senza eseguire lo script.
"""
from __future__ import annotations

import fnmatch
import glob
import itertools
import json
import os
import re
import shlex
import sys
from dataclasses import dataclass, field

#: strumenti che indicano un singolo file
_STRUMENTI_FILE = {"Read", "Write", "Edit", "MultiEdit", "NotebookEdit"}
#: strumenti che SCRIVONO un singolo file
_STRUMENTI_SCRITTURA = {"Write", "Edit", "MultiEdit", "NotebookEdit"}
#: strumenti di ricerca: guardano una cartella intera
_STRUMENTI_RICERCA = {"Glob", "Grep"}

#: nomi di file che contengono segreti: vietati sempre, in ogni cartella.
#: Si confrontano con il NOME del file (basename), non con il percorso.
#: `.env.*` non e' nella specifica ma e' gia' nel deny di .claude/settings.json:
#: il repo li considera segreti, e il guardiano fa lo stesso.
SEGRETI = (".env", ".env.*", "*.env", "tuning.env", "*service-account*.json", "*.pem", "*.key")
#: cartelle vietate in OGNI modalita': `.git/config` puo' contenere il token
#: del remoto (il repo e' pubblico, un token in chiaro e' compromesso per sempre).
_CARTELLE_SEMPRE_VIETATE = (".git",)
#: dispositivi della shell che non sono file del repo (`2>/dev/null`)
_DISPOSITIVI = ("/dev/null", "/dev/stdout", "/dev/stderr", "/dev/stdin", "/dev/tty", "/dev/fd/")

#: file singoli ammessi in una campagna (percorsi relativi alla radice)
_CAMPAGNA_FILE = (
    "research/PROTOCOLLO.md",
    "research/CHANGELOG.md",
    "research/lezioni/metodo.md",
    "research/.sessione",
    "CLAUDE.md",
    ".gitignore",
)
#: cartelle ammesse in una campagna (tutto il contenuto). `{S}` e' il simbolo.
_CAMPAGNA_CARTELLE = (
    "research/config",
    "research/src",
    "research/campagne/{S}",
    "research/data/insample/{S}",
    "research/data/insample/BTCUSDT",
    ".claude",
)
#: in campagna si possono LEGGERE ma mai SCRIVERE: sono il guardiano stesso, il
#: suo marcatore, la sua lista dei vietati e la configurazione che lo registra.
#: Una sessione sorvegliata che puo' riscriverli si libera da sola.
_PROTETTI_FILE = (
    "research/.sessione",
    "research/src/guardiano.py",
    "research/config/percorsi_vietati.txt",
)
_PROTETTI_CARTELLE = (".claude",)

#: riferimento a un branch del protocollo dentro un comando
_BRANCH = re.compile(r"research/(?:coordinamento|archivio|campagna)(?:/[A-Za-z0-9_.-]+)?")
#: separatori fra comandi dentro una stessa riga di shell
_SEPARATORI = {"&&", "||", ";", "|", "(", ")", ";;", "&", "|&"}
#: una redirezione in uscita: il token DOPO e' un file che viene scritto
_REDIREZIONE_SCRITTURA = re.compile(r"^(?:[0-9]*>+[&|]?|&>>?|<>)$")
#: un'espansione di graffe con virgola: `{a,b}` -> `a`, `b`
_GRAFFE = re.compile(r"\{([^{}]*,[^{}]*)\}")
#: `$NOME` o `${NOME}` in testa a un token
_VARIABILE_IN_TESTA = re.compile(r"^\$(?:([A-Za-z_][A-Za-z0-9_]*)|\{([A-Za-z_][A-Za-z0-9_]*)\})")
#: una sequenza che `printf`/`echo -e`/`$'..'` trasformano in un carattere (`\x2f` = `/`)
_ESCAPE_NASCOSTO = re.compile(r"\\(?:x[0-9A-Fa-f]|[0-7]{2,3}|u[0-9A-Fa-f]{4}|U)")
#: un hash di git (abbreviato o pieno)
_HASH = re.compile(r"^[0-9a-f]{7,40}$")
#: HEAD con eventuali `~N` / `^N` (la storia del PROPRIO branch)
_HEAD = re.compile(r"^HEAD(?:~[0-9]*|\^[0-9]*)*$")
#: un comando di `sed` che legge o scrive un file o esegue una shell (`r f`, `w f`, `e cmd`)
_SED_FILE = re.compile(r"(?:^|[;\n\s])[0-9,$~!]*\s*[rRwWe]\s+\S")

#: programmi che stampano le variabili d'ambiente (possono contenere chiavi)
_PROGRAMMI_AMBIENTE = {"env", "printenv"}
#: builtin che stampano l'ambiente se chiamati senza assegnazione (`export -p`, `declare`)
_BUILTIN_AMBIENTE = {"export", "declare", "typeset"}
#: programmi vietati in campagna: eseguono codice o argomenti che il guardiano
#: non puo' vedere (`eval`, `xargs`), creano scorciatoie sul disco (`ln`), o
#: sono interpreti il cui programma e' sempre in linea (`awk`, `perl -e`...).
_PROGRAMMI_VIETATI_CAMPAGNA = {
    "eval", "xargs", "ln", "source", ".",
    "awk", "gawk", "mawk", "nawk",
    "perl", "ruby", "node", "nodejs", "php", "lua", "luajit",
}
#: interpreti che con `-c` / `-` eseguono codice dalla riga di comando o da stdin
_INTERPRETI = re.compile(r"^(?:python|python3|python3\.[0-9]+|pypy|pypy3)$")
#: shell: con `-c` il comando interno si giudica a sua volta
_SHELL = {"sh", "bash", "dash", "zsh", "ksh", "mksh", "fish"}
#: prefissi che eseguono il comando che segue senza cambiarne il senso.
#: Il valore sono le opzioni che prendono un argomento (da saltare in coppia).
_PREFISSI_TRASPARENTI = {
    "command": (), "builtin": (), "exec": (), "nohup": (), "time": (), "caffeinate": (),
    "chronic": (), "unbuffer": (), "doas": ("-u",), "sudo": ("-u", "-g"),
    "nice": ("-n", "--adjustment"), "ionice": ("-c", "-n", "-p"),
    "stdbuf": ("-i", "-o", "-e"), "timeout": ("-s", "-k", "--signal", "--kill-after"),
}
#: ricerche che senza percorso guardano tutta la cartella corrente
_GREP_RICORSIVI = {"rg", "ag", "ack", "pt", "ugrep", "ug"}
_GREP = {"grep", "egrep", "fgrep"} | _GREP_RICORSIVI
_FIND = {"find", "fd", "fdfind"}
#: programmi che leggono soltanto: con questi un file protetto si puo' aprire
_LETTORI = {
    "cat", "head", "tail", "less", "more", "wc", "grep", "egrep", "fgrep", "rg",
    "diff", "ls", "stat", "file", "cmp", "md5sum", "sha1sum", "sha256sum", "cut",
    "sort", "uniq", "nl", "od", "hexdump", "xxd", "strings", "tr", "column", "cd",
    "python", "python3", "test", "[", "realpath", "readlink", "dirname", "basename",
}
#: variabili che, assegnate davanti a un comando, gli fanno eseguire altro
#: (`GIT_PAGER='cat docs/x' git log`) o cambiano dove legge.
_VARIABILI_PERICOLOSE = {
    "PAGER", "GIT_PAGER", "EDITOR", "VISUAL", "GIT_EDITOR", "GIT_SEQUENCE_EDITOR",
    "LESSOPEN", "LESSCLOSE", "PYTHONSTARTUP", "PYTHONPATH", "PERL5OPT", "LD_PRELOAD",
    "LD_LIBRARY_PATH", "BASH_ENV", "ENV", "PROMPT_COMMAND", "GIT_SSH_COMMAND", "GIT_SSH",
    "GIT_EXTERNAL_DIFF", "GIT_DIR", "GIT_WORK_TREE", "GIT_CONFIG", "GIT_CONFIG_GLOBAL",
    "GIT_CONFIG_SYSTEM", "GIT_CONFIG_PARAMETERS", "HOME", "PATH", "IFS", "CDPATH",
    "CLAUDE_PROJECT_DIR",
}

#: sottocomandi git vietati in campagna: cambiano branch, esportano un albero,
#: mostrano l'intera storia o i riferimenti di tutti i branch, o la configurazione
#: (che contiene l'URL del remoto, forse col token).
_GIT_VIETATI = {
    "checkout", "switch", "merge", "rebase", "worktree", "archive", "cat-file",
    "reflog", "ls-remote", "for-each-ref", "show-ref", "bundle", "fast-export",
    "fast-import", "bisect", "filter-branch", "replace", "clone", "config",
    "credential", "credential-store", "credential-cache", "daemon", "instaweb",
    "gui", "citool", "pack-refs", "update-ref", "symbolic-ref", "read-tree",
    "write-tree", "commit-tree", "mktree", "unpack-file", "verify-pack", "pack-objects",
    "unpack-objects", "index-pack", "fsck", "svn", "p4", "cvsexportcommit", "request-pull",
}
#: sottocomandi git che prendono riferimenti (branch, commit): si controllano uno a uno
_GIT_CON_RIFERIMENTI = {
    "log", "show", "diff", "blame", "grep", "rev-parse", "rev-list", "merge-base",
    "describe", "name-rev", "ls-tree", "restore", "reset", "cherry-pick", "revert",
    "branch", "tag", "range-diff", "format-patch", "shortlog", "whatchanged",
    "fetch", "pull", "push", "cherry", "notes", "diff-tree", "diff-index", "ls-files",
    "annotate", "count-objects", "verify-commit", "verify-tag", "stash",
}
#: sottocomandi git che modificano l'albero di lavoro o l'indice
_GIT_SCRIVE = {
    "rm", "mv", "add", "restore", "clean", "apply", "am", "stash", "reset", "commit",
    "revert", "cherry-pick", "checkout", "switch", "merge", "rebase", "pull",
}
#: opzioni di git che allargano lo sguardo a tutti i branch o ai reflog
_GIT_OPZIONI_VIETATE = ("--all", "--branches", "--remotes", "--tags", "--glob", "--mirror",
                        "--walk-reflogs", "-g", "--reflog", "--exclude-hidden", "--alternate-refs")
#: `git log`: opzioni che stampano il CONTENUTO dei file, non solo i commit
_GIT_LOG_CONTENUTO = ("-p", "--patch", "-u", "--unified", "--cc", "-c", "--full-diff", "--raw",
                      "--patch-with-stat", "--patch-with-raw", "--combined-all-paths")
_GIT_LOG_CONTENUTO_PREFISSI = ("-L", "-S", "-G", "-U", "--pickaxe", "--unified=")
#: `git show`: opzioni con cui NON stampa il contenuto
_GIT_SHOW_SOLO_META = ("-s", "--no-patch", "--stat", "--name-only", "--name-status", "--summary",
                       "--shortstat", "--numstat", "--dirstat", "--check")
#: parole che `git stash` accetta come proprio sottocomando
_GIT_STASH_PAROLE = {"push", "pop", "list", "drop", "apply", "show", "clear", "save", "branch", "create", "store"}

#: quante espansioni di graffe o di glob si seguono prima di arrendersi
_MAX_ESPANSIONI = 500
#: profondita' massima di `sh -c "sh -c ..."`
_MAX_PROFONDITA = 3


@dataclass(frozen=True)
class Contesto:
    """Tutto cio' che serve per giudicare un'azione, letto una volta sola."""

    radice: str
    tipo: str  # "campagna" | "coordinamento"
    simbolo: str = ""
    vietati: tuple[str, ...] = ()
    vault_aperto: bool = False
    primo_livello: frozenset[str] = field(default_factory=frozenset)

    @property
    def etichetta(self) -> str:
        if self.tipo == "campagna":
            return f"sessione campagna {self.simbolo}"
        return "sessione coordinamento"

    @property
    def campagna(self) -> bool:
        return self.tipo == "campagna"

    @property
    def proprio_branch(self) -> str:
        return f"research/campagna/{self.simbolo}"


@dataclass(frozen=True)
class Verdetto:
    """Esito di un controllo: consentito o no, e cosa ha fatto scattare il no."""

    consentito: bool
    oggetto: str = ""


OK = Verdetto(True)


# ---------------------------------------------------------------------------
# radice, marcatore, elenco dei vietati
# ---------------------------------------------------------------------------


def radice_progetto(dati: dict) -> str:
    """La radice del repo: CLAUDE_PROJECT_DIR, poi `cwd` del JSON, poi la cartella corrente."""
    for candidato in (os.environ.get("CLAUDE_PROJECT_DIR"), dati.get("cwd")):
        if isinstance(candidato, str) and candidato.strip():
            return os.path.abspath(candidato)
    return os.path.abspath(os.getcwd())


def percorso_marcatore(radice: str) -> str:
    return os.path.join(radice, "research", ".sessione")


def marcatore_presente(radice: str) -> bool:
    """True se il marcatore esiste e non e' vuoto (solo spazi = vuoto)."""
    percorso = percorso_marcatore(radice)
    try:
        with open(percorso, encoding="utf-8") as f:
            return bool(f.read().strip())
    except OSError:
        return False


def leggi_marcatore(radice: str) -> dict:
    """Legge il marcatore e lo valida. Solleva ValueError se e' rotto."""
    with open(percorso_marcatore(radice), encoding="utf-8") as f:
        testo = f.read()
    dati = json.loads(testo)
    if not isinstance(dati, dict):
        raise ValueError("il marcatore deve essere un oggetto JSON")
    tipo = dati.get("tipo")
    if tipo == "campagna":
        simbolo = dati.get("simbolo")
        if not isinstance(simbolo, str) or not re.fullmatch(r"[A-Z0-9_]+", simbolo):
            raise ValueError("una campagna richiede un simbolo (lettere maiuscole e cifre)")
        return {"tipo": "campagna", "simbolo": simbolo}
    if tipo == "coordinamento":
        return {"tipo": "coordinamento"}
    raise ValueError(f"tipo di sessione sconosciuto: {tipo!r}")


def leggi_vietati(radice: str) -> tuple[str, ...]:
    """Le righe di `research/config/percorsi_vietati.txt` (senza commenti e vuote)."""
    percorso = os.path.join(radice, "research", "config", "percorsi_vietati.txt")
    try:
        with open(percorso, encoding="utf-8") as f:
            righe = f.read().splitlines()
    except OSError:
        return ()
    voci = []
    for riga in righe:
        riga = riga.split("#", 1)[0].strip()
        if riga:
            voci.append(riga)
    return tuple(voci)


def costruisci_contesto(radice: str, marcatore: dict) -> Contesto:
    # la radice si risolve sul disco: i percorsi si confrontano con la sua forma reale
    radice = os.path.realpath(radice)
    try:
        primo_livello = frozenset(os.listdir(radice))
    except OSError:
        primo_livello = frozenset()
    return Contesto(
        radice=radice,
        tipo=marcatore["tipo"],
        simbolo=marcatore.get("simbolo", ""),
        vietati=leggi_vietati(radice),
        vault_aperto=os.path.isfile(os.path.join(radice, "research", "vault", "APERTURA.md")),
        primo_livello=primo_livello,
    )


# ---------------------------------------------------------------------------
# normalizzazione e giudizio di un singolo percorso
# ---------------------------------------------------------------------------


def _assoluto(percorso: str, radice: str) -> str:
    """Il percorso assoluto e normalizzato (senza `..`), con `~` espanso. Non tocca il disco."""
    p = os.path.expanduser(percorso.strip())
    if not os.path.isabs(p):
        p = os.path.join(radice, p)
    return os.path.normpath(p)


def normalizza(percorso: str, radice: str) -> str:
    """Percorso relativo alla radice, con `..`, `.` e i LINK SIMBOLICI risolti.

    Un percorso assoluto dentro la radice diventa relativo; uno fuori (o che esce
    con `..`) comincia con `..`. `~` viene espanso. La radice stessa e' `.`.
    I link si risolvono con `realpath`: un link dentro una cartella ammessa che
    punta altrove deve essere giudicato per dove PORTA, non per come si chiama.
    Per un file che non esiste `realpath` risolve la parte che esiste e lascia il
    resto com'e', quindi un percorso inesistente si giudica lo stesso.
    """
    reale = os.path.realpath(_assoluto(percorso, radice))
    return os.path.relpath(reale, os.path.realpath(radice))


def _sotto(rel: str, cartella: str) -> bool:
    cartella = cartella.rstrip("/")
    return rel == cartella or rel.startswith(cartella + "/")


def e_segreto(rel: str) -> bool:
    nome = os.path.basename(rel)
    return any(fnmatch.fnmatch(nome, pat) for pat in SEGRETI)


def e_dispositivo(percorso: str) -> bool:
    """`/dev/null` e simili: redirezioni, non file del repo."""
    return any(percorso == d or (d.endswith("/") and percorso.startswith(d)) for d in _DISPOSITIVI)


def e_vietato_da_elenco(rel: str, vietati: tuple[str, ...]) -> bool:
    """Applica `percorsi_vietati.txt`.

    Una voce che finisce con `/` e' una cartella (vale dalla radice: `data/` non
    tocca `research/data/`). Una voce con `*` o senza `/` e' un pattern sul NOME
    del file, e vale solo FUORI da `research/`: dentro, i dati di mercato e i
    risultati delle campagne sono proprio `.csv` e `.jsonl`, e sono legittimi.
    """
    if rel.startswith(".."):
        return False  # fuori dalla radice: deciso altrove
    nome = os.path.basename(rel)
    dentro_research = _sotto(rel, "research")
    for voce in vietati:
        if voce.endswith("/"):
            if _sotto(rel, voce):
                return True
        elif "*" in voce or "/" not in voce:
            if not dentro_research and (fnmatch.fnmatch(nome, voce) or fnmatch.fnmatch(rel, voce)):
                return True
        elif _sotto(rel, voce):
            return True
    return False


def ammesso_in_campagna(rel: str, simbolo: str) -> bool:
    """Lista bianca del Passo 3. `research/campagne/BTCUSDT` solo se il simbolo e' BTCUSDT."""
    if rel in _CAMPAGNA_FILE:
        return True
    return any(_sotto(rel, c.format(S=simbolo)) for c in _CAMPAGNA_CARTELLE)


def e_protetto(rel: str) -> bool:
    """I file che in campagna si leggono ma non si scrivono (il guardiano e i suoi)."""
    return rel in _PROTETTI_FILE or any(_sotto(rel, c) for c in _PROTETTI_CARTELLE)


def giudica_percorso(percorso: str, ctx: Contesto, *, radice_ok: bool = False, scrittura: bool = False) -> Verdetto:
    """Il verdetto su un percorso, in base alla modalita' della sessione.

    `radice_ok`: la radice stessa (`.`) e' consentita (serve per `cd <radice>`,
    che non legge nulla); altrove no, perche' una ricerca su `.` guarda tutto.
    `scrittura`: l'azione modifica il file; in campagna i file protetti si
    possono leggere ma non scrivere.
    """
    rifiuto = Verdetto(False, percorso)
    if e_dispositivo(_assoluto(percorso, ctx.radice)):
        return OK
    rel = normalizza(percorso, ctx.radice)
    if e_segreto(rel):
        return rifiuto
    if any(_sotto(rel, c) for c in _CARTELLE_SEMPRE_VIETATE):
        return rifiuto
    if ctx.campagna:
        if rel == ".":
            return OK if radice_ok else rifiuto
        if rel.startswith(".."):
            return rifiuto
        if scrittura and e_protetto(rel):
            return rifiuto
        if not ammesso_in_campagna(rel, ctx.simbolo):
            return rifiuto
        if e_vietato_da_elenco(rel, ctx.vietati):
            return rifiuto
        return OK
    # coordinamento: lista nera
    if e_vietato_da_elenco(rel, ctx.vietati):
        return rifiuto
    if _sotto(rel, "research/data/vault") and not ctx.vault_aperto:
        return rifiuto
    return OK


# ---------------------------------------------------------------------------
# comandi di shell: spezzare, espandere, giudicare
# ---------------------------------------------------------------------------


def _spezza(comando: str) -> list[str]:
    """Token del comando, con `&&`, `|`, `;`, `>` come token separati. Mai solleva."""
    try:
        lex = shlex.shlex(comando, posix=True, punctuation_chars=True)
        lex.whitespace_split = True
        return list(lex)
    except ValueError:
        return comando.replace("&&", " && ").replace("|", " | ").replace(";", " ; ").split()


def _segmenti(token: list[str]) -> list[tuple[str, list[str]]]:
    """I singoli comandi di una riga (`a && b | c`), ognuno con il separatore che lo precede."""
    segmenti: list[tuple[str, list[str]]] = [("", [])]
    for t in token:
        if t in _SEPARATORI:
            if segmenti[-1][1]:
                segmenti.append((t, []))
            else:
                segmenti[-1] = (t, segmenti[-1][1])
        else:
            segmenti[-1][1].append(t)
    return [s for s in segmenti if s[1]]


def _e_assegnazione(token: str) -> bool:
    return re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*=.*", token) is not None


def _programma_effettivo(segmento: list[str]) -> tuple[str, list[str], list[str]]:
    """(programma, suoi argomenti, assegnazioni `A=b` davanti).

    Salta i prefissi trasparenti (`command`, `exec`, `timeout 5`, `nice -n 10`,
    `sudo -u x`): `timeout 5 env` e' `env`, e va giudicato come tale.
    """
    assegnazioni: list[str] = []
    i = 0
    while i < len(segmento):
        t = segmento[i]
        if _e_assegnazione(t):
            assegnazioni.append(t)
            i += 1
            continue
        nome = os.path.basename(t)
        if nome in _PREFISSI_TRASPARENTI:
            con_valore = _PREFISSI_TRASPARENTI[nome]
            i += 1
            while i < len(segmento) and segmento[i].startswith("-"):
                i += 2 if segmento[i] in con_valore else 1
            if nome == "timeout" and i < len(segmento) and re.fullmatch(r"[0-9.]+[smhd]?", segmento[i]):
                i += 1  # la durata
            continue
        return nome, segmento[i + 1:], assegnazioni
    return "", [], assegnazioni


def _espandi_graffe(token: str) -> list[str]:
    """`a{b,c}d` -> `abd`, `acd` (come bash). Senza graffe con virgola restituisce il token."""
    risultati = [token]
    for _ in range(8):  # un limite: le graffe annidate sono rare e sospette
        nuovi: list[str] = []
        cambiato = False
        for r in risultati:
            m = _GRAFFE.search(r)
            if m is None:
                nuovi.append(r)
                continue
            cambiato = True
            for alternativa in m.group(1).split(","):
                nuovi.append(r[: m.start()] + alternativa + r[m.end():])
            if len(nuovi) > _MAX_ESPANSIONI:
                return nuovi
        risultati = nuovi
        if not cambiato:
            break
    return risultati


def espandi_token(token: str, ctx: Contesto) -> list[str] | None:
    """Cio' che la shell farebbe diventare il token: una lista di parole, o None se
    non si puo' sapere (e allora si rifiuta: nel dubbio si blocca).

    * `$(...)` e i backtick eseguono un comando: non si puo' sapere il risultato;
    * `$NOME` / `${NOME}` in testa si sostituiscono (CLAUDE_PROJECT_DIR e PWD sono
      la radice); in campagna una variabile sconosciuta non si accetta, in
      coordinamento il resto del token si giudica come relativo alla radice
      (il caso peggiore: la variabile punta alla radice). Ogni altro `$` e' un
      costrutto (`${X-...}`, `$'...'`) che si rifiuta;
    * `{a,b}` si espande; `{1..3}` e `\\x2f` in campagna si rifiutano;
    * `*`, `?`, `[` si espandono sul disco dalla radice; se non combaciano con
      nulla, bash passa il token com'e' e cosi' facciamo noi.
    """
    if "`" in token or "$(" in token:
        return None
    if "$" in token:
        m = _VARIABILE_IN_TESTA.match(token)
        if m is None:
            return None
        nome = m.group(1) or m.group(2)
        resto = token[m.end():]
        if "$" in resto:
            return None
        if nome in ("CLAUDE_PROJECT_DIR", "PWD"):
            valore = ctx.radice
        elif nome == "HOME":
            valore = os.path.expanduser("~")
        elif nome in os.environ:
            valore = os.environ[nome]
        elif ctx.campagna:
            return None
        else:
            # coordinamento, variabile sconosciuta: il resto, visto dalla radice
            valore = ctx.radice if resto.startswith("/") else ""
        token = valore + resto
    if ctx.campagna and (_ESCAPE_NASCOSTO.search(token) or re.search(r"\{[^{}]*\.\.[^{}]*\}", token)):
        return None
    parole = _espandi_graffe(token)
    if len(parole) > _MAX_ESPANSIONI:
        return None
    risultato: list[str] = []
    for parola in parole:
        if not any(c in parola for c in "*?["):
            risultato.append(parola)
            continue
        base = _assoluto(parola, ctx.radice)
        trovati = list(itertools.islice(glob.iglob(base), _MAX_ESPANSIONI + 1))
        if len(trovati) > _MAX_ESPANSIONI:
            if ctx.campagna:
                return None
            trovati = trovati[:_MAX_ESPANSIONI]
        risultato.extend(trovati if trovati else [parola])
    return risultato


def _candidato_percorso(token: str, primo_livello: frozenset[str]) -> str | None:
    """Il frammento di un token che sembra un percorso, o None.

    Un percorso e' un token con `/`, o che comincia con `.` o `~`, o che e' il
    nome di una voce di primo livello del repo (`docs`, `ops`...). Si tolgono
    prima le redirezioni (`2>file`) e le opzioni `--x=file`.
    """
    t = token
    t = re.sub(r"^[0-9]*[<>]+", "", t)
    if "=" in t and not t.startswith("="):
        t = t.split("=", 1)[1]
    if not t or t.startswith("-"):
        return None
    if "/" in t or t.startswith((".", "~")) or t in primo_livello or e_segreto(t):
        return t
    return None


def _ha_percorso(argomenti: list[str], ctx: Contesto) -> bool:
    """True se fra gli argomenti c'e' almeno un operando che sembra un percorso."""
    return any(not a.startswith("-") and _candidato_percorso(a, ctx.primo_livello) is not None for a in argomenti)


def _opzione_contiene(argomenti: list[str], lettere: str, lunghe: tuple[str, ...]) -> bool:
    """Un'opzione corta con una delle `lettere` (`-rn`), o una lunga fra `lunghe`."""
    for a in argomenti:
        if a == "--":
            return False
        if a.startswith("--"):
            if a.split("=", 1)[0] in lunghe:
                return True
        elif a.startswith("-") and len(a) > 1 and any(c in lettere for c in a[1:]):
            return True
    return False


def _giudica_programma(prog: str, argomenti: list[str], separatore: str, ctx: Contesto, comando: str,
                       profondita: int) -> Verdetto:
    """Le regole di campagna legate al PROGRAMMA, non ai suoi percorsi."""
    rifiuta = lambda motivo: Verdetto(False, f"{comando!r} ({motivo})")  # noqa: E731
    if prog in _PROGRAMMI_AMBIENTE:
        return rifiuta("legge le variabili d'ambiente")
    if prog == "set" and (not argomenti or any(a in ("-o", "+o") for a in argomenti)):
        return rifiuta("legge le variabili d'ambiente")
    if prog in _BUILTIN_AMBIENTE and (not argomenti or any(a.startswith("-") for a in argomenti)):
        return rifiuta("legge le variabili d'ambiente")
    if prog in _PROGRAMMI_VIETATI_CAMPAGNA:
        return rifiuta(f"{prog} esegue cio' che il guardiano non puo' vedere")
    if _INTERPRETI.match(prog):
        if any(a in ("-c", "-") for a in argomenti):
            return rifiuta(f"{prog} -c esegue codice che il guardiano non puo' vedere")
        if not any(a == "-m" or a in ("-V", "--version", "-h", "--help") or not a.startswith("-") for a in argomenti):
            return rifiuta(f"{prog} senza script legge il codice da stdin")
    if prog in _SHELL and not _script_di_shell(argomenti) and not any(not a.startswith("-") for a in argomenti):
        return rifiuta(f"{prog} senza script legge i comandi da stdin")
    if prog == "sed":
        for a in argomenti:
            if not a.startswith("-") and _candidato_percorso(a, ctx.primo_livello) is None and _SED_FILE.search(a):
                return rifiuta("sed con un comando r/w/e legge o scrive un file non dichiarato")
    if prog in _GREP:
        ricorsivo = prog in _GREP_RICORSIVI or _opzione_contiene(
            argomenti, "rR", ("--recursive", "--dereference-recursive"))
        if ricorsivo and not _ha_percorso(argomenti, ctx) and not (prog in _GREP_RICORSIVI and separatore == "|"):
            return rifiuta(f"{prog} ricorsivo senza percorso guarda tutto il repo")
    if prog in _FIND and not _ha_percorso(argomenti, ctx):
        return rifiuta(f"{prog} senza percorso guarda tutto il repo")
    if prog == "git":
        return _giudica_git(argomenti, ctx, comando)
    return OK


def _script_di_shell(argomenti: list[str]) -> str | None:
    """Il comando interno di `sh -c '...'` (o `-lc`, `-ec`), oppure None."""
    if not any(a.startswith("-") and not a.startswith("--") and "c" in a[1:] for a in argomenti):
        return None
    return next((a for a in argomenti if not a.startswith("-")), None)


def _e_riferimento_proprio(token: str, ctx: Contesto) -> bool:
    """HEAD (con `~N`/`^N`), il proprio branch (anche `origin/...`) o un hash."""
    proprio = ctx.proprio_branch
    return bool(_HEAD.match(token) or token in (proprio, f"origin/{proprio}") or _HASH.match(token))


def _giudica_git(argomenti: list[str], ctx: Contesto, comando: str) -> Verdetto:
    """git in campagna: solo il proprio branch, e mai il contenuto dell'intera storia.

    La storia del branch di campagna contiene TUTTO il repo (docs/ compreso):
    `git log -p`, `git show HEAD`, `git diff HEAD~5` lo stamperebbero. Quindi
    chi mostra contenuti deve nominare un percorso ammesso; chi prende
    riferimenti deve usare HEAD, il proprio branch o un hash; `ref:percorso`
    si giudica anche nella parte dopo i due punti.
    """
    rifiuta = lambda motivo: Verdetto(False, f"{comando!r} ({motivo})")  # noqa: E731
    # opzioni globali: `-c chiave=valore` cambia pager/editor/alias, e il guardiano non lo vede
    i = 0
    while i < len(argomenti) and argomenti[i].startswith("-"):
        if argomenti[i] in ("-c", "--config-env"):
            return rifiuta("git -c cambia la configurazione sotto il guardiano")
        i += 2 if argomenti[i] in ("-C", "--git-dir", "--work-tree", "--namespace", "--exec-path") else 1
    if i >= len(argomenti):
        return OK
    sub, resto = argomenti[i], argomenti[i + 1:]
    if sub in _GIT_VIETATI:
        return rifiuta(f"git {sub} e' fuori dal proprio branch")
    if sub == "remote" and resto:
        return rifiuta("git remote con argomenti mostra l'URL del remoto")
    if sub not in _GIT_CON_RIFERIMENTI:
        return OK  # status, add, commit, rm, mv, clean, init, help...: niente riferimenti
    for a in resto:
        if a.split("=", 1)[0] in _GIT_OPZIONI_VIETATE:
            return rifiuta(f"git {sub} {a} guarda tutti i branch")
        if sub == "branch" and (a in ("--verbose", "--list") or (
                a.startswith("-") and not a.startswith("--") and any(c in "arv" for c in a[1:]))):
            return rifiuta(f"git branch {a} mostra gli altri branch e i loro hash")
        if a.startswith("--source=") and not _e_riferimento_proprio(a.split("=", 1)[1], ctx):
            return rifiuta(f"git {sub} {a} legge da un altro branch")
    # operandi: prima di `--` possono essere riferimenti, dopo solo percorsi
    con_percorso_ammesso = False
    dopo_doppio_trattino = False
    pattern_visto = False
    remoto_visto = False
    for a in resto:
        if a == "--":
            dopo_doppio_trattino = True
            continue
        if a.startswith("-") and not dopo_doppio_trattino:
            continue
        if not dopo_doppio_trattino and sub == "stash" and a in _GIT_STASH_PAROLE:
            continue
        if not dopo_doppio_trattino and sub in ("fetch", "pull", "push") and not remoto_visto and "/" not in a:
            remoto_visto = True  # il primo operando e' il nome del remoto (`origin`)
            continue
        if not dopo_doppio_trattino and sub == "grep" and not pattern_visto and _candidato_percorso(a, ctx.primo_livello) is None:
            pattern_visto = True  # il primo operando di `git grep` e' cio' che si cerca
            continue
        riferimento, _, percorso = a.partition(":") if (":" in a and not dopo_doppio_trattino) else ("", "", "")
        if riferimento:
            if not _e_riferimento_proprio(riferimento, ctx):
                return rifiuta(f"git {sub} {a} legge da un altro branch")
            if not giudica_percorso(percorso, ctx).consentito:
                return rifiuta(f"git {sub} {a}: percorso vietato")
            continue
        if not dopo_doppio_trattino and _e_riferimento_proprio(a, ctx):
            continue
        if _candidato_percorso(a, ctx.primo_livello) is None and not os.path.lexists(os.path.join(ctx.radice, a)):
            # ne' riferimento proprio ne' percorso: `main`, un nome calcolato, un tag
            return rifiuta(f"git {sub} {a} non e' HEAD, il proprio branch o un percorso ammesso")
        if giudica_percorso(a, ctx).consentito:
            con_percorso_ammesso = True
        else:
            return rifiuta(f"git {sub} {a}: percorso vietato")
    # chi stampa contenuti deve restringersi a un percorso ammesso
    riferimenti = [a for a in resto if not a.startswith("-") and _e_riferimento_proprio(a.split(":", 1)[0], ctx)]
    if sub in ("log", "whatchanged", "format-patch"):
        mostra = any(a in _GIT_LOG_CONTENUTO or a.startswith(_GIT_LOG_CONTENUTO_PREFISSI) for a in resto) or any(
            a.startswith("-") and not a.startswith("--") and any(c in "puLSGUc" for c in a[1:]) for a in resto)
        if sub != "log":
            mostra = True
        if mostra and not con_percorso_ammesso:
            return rifiuta(f"git {sub} stampa il contenuto di tutta la storia: serve un percorso ammesso")
    elif sub == "show":
        solo_meta = any(a.split("=", 1)[0] in _GIT_SHOW_SOLO_META or a.startswith(("--format", "--pretty")) for a in resto)
        if not solo_meta and not con_percorso_ammesso:
            return rifiuta("git show stampa il contenuto di un commit intero: serve un percorso ammesso")
    elif sub in ("diff", "diff-tree", "diff-index", "range-diff"):
        if (riferimenti or sub != "diff") and not con_percorso_ammesso:
            return rifiuta(f"git {sub} con un riferimento confronta tutta la storia: serve un percorso ammesso")
    elif sub == "grep" and not con_percorso_ammesso:
        return rifiuta("git grep senza percorso cerca in tutto il repo")
    return OK


def giudica_comando(comando: str, ctx: Contesto, profondita: int = 0) -> Verdetto:
    """Giudica una riga di shell: i branch, i programmi, poi ogni percorso (espanso)."""
    if ctx.campagna:
        # qualunque riferimento a un branch del protocollo che non sia il proprio
        for m in _BRANCH.finditer(comando):
            if m.group(0) != ctx.proprio_branch:
                return Verdetto(False, f"{comando!r} (branch {m.group(0)})")
    propri = {ctx.proprio_branch, f"origin/{ctx.proprio_branch}"}
    for separatore, segmento in _segmenti(_spezza(comando)):
        prog, argomenti, assegnazioni = _programma_effettivo(segmento)
        if ctx.campagna:
            for a in assegnazioni:
                if a.split("=", 1)[0] in _VARIABILI_PERICOLOSE:
                    return Verdetto(False, f"{comando!r} (la variabile {a.split('=', 1)[0]} cambia cio' che il comando fa)")
            v = _giudica_programma(prog, argomenti, separatore, ctx, comando, profondita)
            if not v.consentito:
                return v
        scrive_di_norma = prog not in _LETTORI
        if prog == "git":
            sub = next((a for a in argomenti if not a.startswith("-")), "")
            scrive_di_norma = sub in _GIT_SCRIVE
        # `sh -c '...'`: il comando interno si giudica come comando, in ogni modalita'
        script = _script_di_shell(argomenti) if prog in _SHELL else None
        if script is not None:
            if profondita >= _MAX_PROFONDITA:
                return Verdetto(False, f"{comando!r} ({prog} -c annidato troppe volte)")
            interno = giudica_comando(script, ctx, profondita + 1)
            if not interno.consentito:
                return Verdetto(False, f"{comando!r} (dentro {prog} -c: {interno.oggetto})")
        precedente = ""
        for t in segmento:  # anche il programma: puo' essere `./script.sh`
            dopo_redirezione = bool(_REDIREZIONE_SCRITTURA.match(precedente))
            precedente = t
            if script is not None and t == script:
                continue  # gia' giudicato come comando
            if ctx.campagna and t in propri:
                continue  # e' ESATTAMENTE il proprio branch: non e' un percorso
            parole = espandi_token(t, ctx)
            if parole is None:
                return Verdetto(False, f"{comando!r} (il token {t!r} viene espanso dalla shell in modo imprevedibile)")
            for parola in parole:
                cand = _candidato_percorso(parola, ctx.primo_livello)
                if cand is None:
                    continue
                v = giudica_percorso(
                    cand, ctx,
                    radice_ok=(prog in ("cd", "pushd")),
                    scrittura=(dopo_redirezione or scrive_di_norma),
                )
                if not v.consentito:
                    return Verdetto(False, f"{comando!r} (percorso {cand})")
    return OK


# ---------------------------------------------------------------------------
# l'azione nel suo insieme
# ---------------------------------------------------------------------------


def giudica_azione(nome: str, ingresso: dict, ctx: Contesto) -> Verdetto:
    """Il verdetto sull'azione: file singolo, ricerca o comando. Nel dubbio blocca (in campagna)."""
    severo = ctx.campagna
    if nome in _STRUMENTI_FILE:
        percorso = ingresso.get("file_path") or ingresso.get("notebook_path")
        if not isinstance(percorso, str) or not percorso.strip():
            return Verdetto(False, f"{nome} senza percorso") if severo else OK
        return giudica_percorso(percorso, ctx, scrittura=(nome in _STRUMENTI_SCRITTURA))
    if nome in _STRUMENTI_RICERCA:
        percorso = ingresso.get("path")
        if not isinstance(percorso, str) or not percorso.strip():
            # una ricerca senza percorso guarda tutto il repo
            return Verdetto(False, f"{nome} senza percorso (guarda tutto il repo)") if severo else OK
        schema = ingresso.get("pattern")
        if severo and nome == "Glob" and isinstance(schema, str) and (
            ".." in schema or schema.startswith(("/", "~"))
        ):
            return Verdetto(False, f"Glob con schema {schema!r} (esce dalla cartella)")
        return giudica_percorso(percorso, ctx)
    if nome == "Bash":
        comando = ingresso.get("command")
        if not isinstance(comando, str):
            return Verdetto(False, "Bash senza comando") if severo else OK
        return giudica_comando(comando, ctx)
    # strumenti non coperti dall'hook: non e' compito nostro
    return OK


def messaggio_rifiuto(ctx: Contesto, oggetto: str) -> str:
    oggetto = " ".join(oggetto.splitlines())  # una riga sola, sempre
    return (
        f"[guardiano] azione rifiutata ({ctx.etichetta}): {oggetto} e' fuori dai percorsi "
        "ammessi dal protocollo (Passo 3). Registra il rifiuto nel log e chiedi all'utente."
    )


def main() -> int:
    radice_grezza = os.environ.get("CLAUDE_PROJECT_DIR") or ""
    attivo = bool(radice_grezza) and marcatore_presente(os.path.abspath(radice_grezza))
    try:
        try:
            dati = json.loads(sys.stdin.read() or "{}")
            if not isinstance(dati, dict):
                dati = {}
        except (ValueError, OSError):
            dati = {}
        radice = radice_progetto(dati)
        attivo = marcatore_presente(radice)
        if not attivo:
            return 0
        try:
            marcatore = leggi_marcatore(radice)
        except (ValueError, OSError) as e:
            print(
                f"[guardiano] il marcatore research/.sessione e' rotto ({e}): sistemalo o "
                "toglilo prima di continuare.",
                file=sys.stderr,
            )
            return 2
        ctx = costruisci_contesto(radice, marcatore)
        nome = dati.get("tool_name")
        ingresso = dati.get("tool_input")
        if not isinstance(nome, str) or not isinstance(ingresso, dict):
            print(messaggio_rifiuto(ctx, "azione senza nome o senza parametri"), file=sys.stderr)
            return 2
        verdetto = giudica_azione(nome, ingresso, ctx)
        if verdetto.consentito:
            return 0
        print(messaggio_rifiuto(ctx, verdetto.oggetto), file=sys.stderr)
        return 2
    except Exception as e:  # fail-closed: con marcatore presente un errore blocca
        if attivo:
            print(f"[guardiano] errore interno con marcatore presente, azione rifiutata: {e!r}", file=sys.stderr)
            return 2
        return 0


if __name__ == "__main__":
    sys.exit(main())
