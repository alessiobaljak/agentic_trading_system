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
    percorsi ammessi della campagna e solo gli strumenti ammessi; tutto il
    resto e' vietato;
  * `{"tipo": "coordinamento"}` -> lista NERA: tutto ammesso tranne i
    `percorsi_vietati`, i segreti e `research/data/vault/` finche' il vault e'
    chiuso (manca `research/vault/APERTURA.md`); gli strumenti diversi da
    file, ricerche e Bash non li guarda;
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

Cosa ha aggiunto la revisione del 7 ottobre 2026 (test_guardiano_4_4.py): i
tentativi precedenti di una campagna, quando ci sono, vivono in
`research/archivio/campagna/<SIMBOLO>`, con file agli STESSI percorsi della
campagna nuova, e il branch principale ha nei messaggi dei commit il lavoro di
coordinamento e ~1.500 commit del bot scritti nel periodo del vault. Quindi, in
campagna:
  * git passa solo con i sottocomandi di una lista BIANCA
    (`_GIT_AMMESSI_CAMPAGNA`): niente cambi di branch, unioni, esportazioni,
    letture di oggetti per hash, alias;
  * `commit`, `push`, `pull`, `reset` e `stash` solo con HEAD sul proprio
    branch (lo si chiede a git); `fetch` e `pull` solo con il nome del proprio
    branch (senza, scaricano tutti i branch e ne stampano i nomi); `push` solo
    verso il proprio branch, senza forzature ne' cancellazioni;
  * la STORIA (`git log`, `shortlog`, `whatchanged`, `rev-list`, `blame`,
    `annotate`) si guarda solo ristretta alla propria cartella
    `research/campagne/<SIMBOLO>/`: senza percorso, o con un percorso fuori,
    stamperebbe i messaggi di tutto il branch principale. Le opzioni che
    scavalcano il filtro sul percorso (`--sparse`, `--boundary`, `--full-diff`...)
    e quelle che stampano il CONTENUTO dei commit (`-p`, `-L`, `-S`...) sono
    vietate, e per `log` e simili i percorsi vanno dopo `--` (un'opzione con
    valore, `--grep percorso`, se li ingoia lascia git senza filtro);
  * i comandi che stampano o rimettono sul disco il contenuto di una revisione
    (`show <rif>:<percorso>`, `diff`, `restore -s`, `blame`, `grep`, `reset`)
    accettano solo HEAD, il proprio branch o `origin/<proprio branch>`, senza
    `~N` ne' hash: un antenato di HEAD puo' essere un commit del branch
    principale con una versione vecchia di un file della propria cartella;
  * un hash, dove resta ammesso (`log`, `rev-parse`, `ls-tree`), e' "proprio"
    solo se e' un antenato di HEAD (`git merge-base --is-ancestor`);
  * le opzioni e le variabili che portano git altrove o gli fanno eseguire
    altro (`-c`, `--git-dir`, `--work-tree`, `--exec-path`, `GIT_*=`) sono
    vietate; un file scritto da un'opzione (`--output=`) si giudica come
    scrittura;
  * gli strumenti diversi da file, ricerche e Bash passano solo se sono in una
    lista BIANCA: gli strumenti MCP (GitHub legge ogni branch, i prompt delle
    sessioni remote possono parlare di altre campagne) e gli Artifact sono
    vietati; WebFetch apre solo i siti di articoli scientifici di una lista
    BIANCA, e WebSearch rifiuta le ricerche che puntano a questo repository.
  Per questo `.claude/settings.json` registra il guardiano per TUTTI gli
  strumenti (matcher `*`); senza marcatore la risposta resta immediata.

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
import functools
import glob
import itertools
import json
import os
import re
import shlex
import subprocess
import sys
import unicodedata
import urllib.parse
from dataclasses import dataclass, field

#: strumenti che indicano un singolo file
_STRUMENTI_FILE = {"Read", "Write", "Edit", "MultiEdit", "NotebookEdit"}
#: strumenti che SCRIVONO un singolo file
_STRUMENTI_SCRITTURA = {"Write", "Edit", "MultiEdit", "NotebookEdit"}
#: strumenti di ricerca: guardano una cartella intera
_STRUMENTI_RICERCA = {"Glob", "Grep"}
#: in campagna, gli altri strumenti passano solo se sono qui (lista BIANCA): non
#: leggono file ne' storia (liste di cose da fare, processi gia' giudicati,
#: sotto-agenti le cui azioni passano a loro volta dal guardiano). WebFetch e
#: WebSearch si giudicano a parte, per indirizzo e per testo. Tutto il resto, in
#: particolare ogni `mcp__*` (GitHub legge qualunque branch, i prompt delle
#: sessioni remote possono parlare di altre campagne) e gli Artifact, e' vietato.
_STRUMENTI_AMMESSI_CAMPAGNA = frozenset({
    "TodoWrite", "TaskCreate", "TaskGet", "TaskList", "TaskUpdate", "TaskStop", "TaskOutput",
    "BashOutput", "KillShell", "KillBash", "ToolSearch", "Agent", "Task",
    "AskUserQuestion", "Skill", "EnterPlanMode", "ExitPlanMode",
})
#: i soli siti che WebFetch apre in campagna (anche i sottodomini): articoli
#: scientifici e loro indici. Una lista NERA non bastava: ogni CDN o specchio di
#: GitHub (jsdelivr, githack, sourcegraph, archive.org...) serve qualunque branch
#: di questo repo pubblico, archivi compresi.
_HOST_AMMESSI_WEB = (
    "arxiv.org", "ssrn.com", "doi.org", "nber.org", "jstor.org", "sciencedirect.com",
    "springer.com", "wiley.com", "tandfonline.com", "oup.com", "cambridge.org",
    "semanticscholar.org", "researchgate.net", "repec.org", "wikipedia.org",
    # editori a cui rimanda spesso doi.org per gli articoli di finanza
    "aeaweb.org", "informs.org", "mdpi.com", "elsevier.com", "sagepub.com", "emerald.com",
    "cfainstitute.org", "pm-research.com",
)
#: testi che una ricerca sul web in campagna non puo' contenere (in minuscolo):
#: portano a questo repository, ai suoi branch o agli specchi che li servono
_PAROLE_VIETATE_RICERCA = (
    "github", "gitlab", "jsdelivr", "githack", "sourcegraph",
    "agentic_trading_system", "agentic-trading-system", "agentic trading", "alessiobaljak", "baljak",
    "research/archivio", "research/campagna", "research/coordinamento", "archivio/campagna",
    "research/campagne",
)
#: quante volte si decodifica `%xx` prima di arrendersi (un indirizzo onesto si
#: stabilizza in uno o due passi)
_MAX_DECODIFICHE = 8
#: un nome di dominio semplice: lettere, cifre e trattini, l'ultima parte comincia
#: con una lettera (cosi' un indirizzo IP, scritto in qualunque forma, non passa)
_HOST_VALIDO = re.compile(r"^(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z](?:[a-z0-9-]*[a-z0-9])?$")

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
#: un hash di git (abbreviato o pieno), con eventuali `~N` / `^N`
_HASH = re.compile(r"^([0-9a-f]{7,40})(?:~[0-9]*|\^[0-9]*)*$")
#: quanto puo' durare la domanda a git "questo hash e' un antenato di HEAD?"
_TEMPO_GIT = 3
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
#: in campagna ogni altra variabile `GIT_*` e' vietata: `GIT_EXEC_PATH` fa eseguire
#: a git i programmi di un'altra cartella, `GIT_CONFIG_COUNT`/`KEY_n`/`VALUE_n`
#: cambiano la configurazione come `git -c`, `GIT_INDEX_FILE` e
#: `GIT_OBJECT_DIRECTORY` portano git su un altro indice o altri oggetti. Queste no.
_VARIABILI_GIT_INNOCUE = {
    "GIT_TERMINAL_PROMPT", "GIT_AUTHOR_NAME", "GIT_AUTHOR_EMAIL", "GIT_AUTHOR_DATE",
    "GIT_COMMITTER_NAME", "GIT_COMMITTER_EMAIL", "GIT_COMMITTER_DATE",
}
#: builtin che assegnano variabili (anche gia' esportate): `export GIT_EDITOR=...`
_BUILTIN_ASSEGNAZIONE = {"export", "declare", "typeset", "readonly", "local"}

#: in campagna git passa SOLO con uno di questi sottocomandi (lista BIANCA). Fuori
#: restano, fra gli altri: i cambi di branch (`checkout`, `switch`), le unioni e
#: le riscritture (`merge`, `rebase`, `cherry-pick`, `revert`: HEAD stesso puo'
#: essere un commit del branch principale, e `revert HEAD` rimetterebbe sul disco
#: la versione precedente dei suoi file), le patch (`apply`, `am`, `format-patch`),
#: le esportazioni (`archive`, `bundle`), le letture di oggetti per hash
#: (`cat-file`, `merge-tree`, `update-index --cacheinfo` seguito da `restore`,
#: `verify-commit -v`, `notes`), i nomi e i riferimenti di tutti i branch
#: (`show-ref`, `for-each-ref`, `ls-remote`, `show-branch`, `name-rev`,
#: `describe`, `tag`), la configurazione (`config`, `var`), i programmi scelti da
#: chi chiama (`difftool`, `mergetool`, `submodule`), `clean` (con `-X` cancella
#: il marcatore, che git ignora) e gli alias.
_GIT_AMMESSI_CAMPAGNA = frozenset({
    "status", "add", "rm", "mv", "commit", "push", "pull", "fetch", "remote",
    "log", "shortlog", "whatchanged", "rev-list", "rev-parse", "merge-base",
    "show", "diff", "diff-index", "diff-files", "blame", "annotate", "grep",
    "ls-tree", "ls-files", "restore", "reset", "stash", "branch",
    "check-ignore", "check-attr", "count-objects", "help", "version",
})
#: sottocomandi che in campagna si fanno solo con HEAD sul proprio branch: con
#: HEAD sul branch principale un `commit` e un `push origin HEAD` finirebbero li'.
#: (`merge`, `rebase`, `cherry-pick`, `revert`, `am`, `apply` non sono ammessi affatto.)
_GIT_SUL_PROPRIO_BRANCH = frozenset({"commit", "push", "pull", "reset", "stash"})
#: sottocomandi git che prendono riferimenti (branch, commit): si controllano uno a uno
_GIT_CON_RIFERIMENTI = {
    "log", "show", "diff", "blame", "grep", "rev-parse", "rev-list", "merge-base",
    "ls-tree", "restore", "reset", "branch", "shortlog", "whatchanged",
    "diff-index", "ls-files", "annotate", "count-objects", "stash",
}
#: sottocomandi che stampano o rimettono sul disco il CONTENUTO di una revisione:
#: accettano solo i riferimenti "stretti" (HEAD, il proprio branch, origin/il
#: proprio branch), senza `~N`/`^N` e senza hash. Un antenato di HEAD e' anche un
#: commit del branch principale: `git show HEAD~3:research/campagne/X/scheda_moneta.md`
#: stamperebbe una versione vecchia, con campi tolti dopo.
_GIT_CONTENUTO = frozenset({"show", "diff", "diff-index", "restore", "blame", "annotate", "grep", "reset", "stash"})
#: sottocomandi che senza percorso elencano i file di tutto il repo (anche le
#: cartelle delle altre monete, che `ls research/campagne` non mostra)
_GIT_CON_PERCORSO_OBBLIGATORIO = frozenset({"ls-tree", "ls-files"})
#: sottocomandi git che mostrano la STORIA, cioe' i messaggi dei commit. La
#: storia del branch di campagna e' quella del branch principale: in campagna si
#: guarda solo ristretta alla propria cartella `research/campagne/<SIMBOLO>/`.
_GIT_STORIA = {"log", "shortlog", "whatchanged", "rev-list", "blame", "annotate"}
#: comandi di storia in cui un'opzione con valore puo' ingoiare il percorso
#: (`git log --grep research/campagne/X/` cerca il testo e non filtra nulla):
#: per questi i percorsi vanno dopo `--`. `blame` vuole comunque un file. Sono
#: anche quelli in cui le opzioni di CONTENUTO (`-p`...) sono vietate.
_GIT_STORIA_CON_DOPPIO_TRATTINO = {"log", "shortlog", "whatchanged", "rev-list"}
#: opzioni che, nei comandi di storia, mostrano commit che NON toccano i percorsi
#: dati (`--sparse` tutti, `--boundary` e `--simplify-by-decoration` quelli di
#: confine o con un nome) o file fuori (`--full-diff`, `--follow` sui nomi vecchi)
_GIT_STORIA_OPZIONI_VIETATE = ("--sparse", "--boundary", "--simplify-by-decoration", "--full-diff",
                               "--follow", "--merge", "--bisect")
#: opzioni che, nei comandi di storia, stampano il CONTENUTO dei commit (patch,
#: righe, parole) o scelgono i commit in base al contenuto (`-S`, `-G`): la
#: storia della propria cartella comincia sul branch principale, con versioni
#: vecchie dei suoi file. Restano ammesse `--stat`, `--numstat`, `--shortstat`,
#: `--name-only`, `--name-status`, `--format`/`--pretty`, `--oneline`.
_GIT_STORIA_CONTENUTO_LUNGHE = (
    "--patch", "--patch-with-stat", "--patch-with-raw", "--unified", "--function-context",
    "--word-diff", "--word-diff-regex", "--color-words", "--cc", "--diff-merges", "--remerge-diff",
    "--binary", "--ext-diff", "--textconv", "--full-diff", "--pickaxe-all", "--pickaxe-regex",
    "--find-object", "--dd",
)
#: le stesse, corte; e le lettere corte che prendono un valore attaccato (`-U3`, `-n5`)
_GIT_STORIA_CONTENUTO_CORTE = "puULWcmSG"
_GIT_STORIA_CORTE_CON_VALORE = "nUlOSGLMCB"
#: opzioni lunghe che sono un INIZIO di quelle vietate ma esistono da sole (git
#: preferisce sempre il nome esatto all'abbreviazione)
_GIT_STORIA_OPZIONI_ESATTE_AMMESSE = ("--color", "--text")
#: sottocomandi git che modificano l'albero di lavoro o l'indice (o scrivono file)
_GIT_SCRIVE = {
    "rm", "mv", "add", "restore", "clean", "apply", "am", "stash", "reset", "commit",
    "revert", "cherry-pick", "checkout", "switch", "merge", "rebase", "pull", "format-patch",
}
#: opzioni di git che allargano lo sguardo a tutti i branch o ai reflog
_GIT_OPZIONI_VIETATE = ("--all", "--branches", "--remotes", "--tags", "--glob", "--mirror",
                        "--walk-reflogs", "-g", "--reflog", "--exclude-hidden", "--alternate-refs")
#: opzioni che prendono riferimenti o percorsi da stdin o da un file: il guardiano
#: non li vede (un hash dell'archivio passerebbe per `echo <hash> | git log --stdin`)
_GIT_OPZIONI_DA_FUORI = ("--stdin", "--pathspec-from-file")
#: opzioni globali di git (prima del sottocomando) che prendono un valore separato
_GIT_GLOBALI_CON_VALORE = ("-C", "--namespace")
#: parole che `git stash` accetta come proprio sottocomando
_GIT_STASH_PAROLE = {"push", "pop", "list", "drop", "apply", "show", "clear", "save", "branch", "create", "store"}
#: ...e quelle vietate in campagna: `store`/`create` fanno di un commit qualunque
#: (un merge dal principale) una voce dello stash, che `stash show -p` stampa;
#: `branch` crea un branch e ci passa sopra
_GIT_STASH_VIETATE = {"branch", "create", "store"}
#: il nome di un remoto (`origin`): non un indirizzo, non un percorso
_NOME_REMOTO = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
#: le opzioni ammesse in campagna per push, fetch e pull (lista BIANCA, nomi
#: esatti): fuori restano forzature (`-f`, `--force-with-lease`, il `+` del
#: refspec), cancellazioni (`-d`, `--delete`, `--prune`), `--all`, `--mirror`,
#: `--tags` e i programmi remoti (`--upload-pack`, `--receive-pack`, `--exec`)
_GIT_SYNC_OPZIONI = {
    "push": frozenset({"-u", "--set-upstream", "-q", "--quiet", "-v", "--verbose", "--progress",
                       "--no-progress", "-n", "--dry-run", "--porcelain"}),
    "fetch": frozenset({"-q", "--quiet", "-v", "--verbose", "--progress", "--no-progress", "-n",
                        "--no-tags", "--dry-run", "--no-write-fetch-head"}),
    "pull": frozenset({"-q", "--quiet", "-v", "--verbose", "--progress", "--no-progress", "--no-tags",
                       "--ff", "--no-ff", "--ff-only", "--rebase", "--no-rebase", "--no-edit", "--stat",
                       "-n", "--no-stat"}),
}
#: `git commit` che copia il messaggio di un altro commit (forse del branch
#: principale), che poi `git log --format=%B -- <propria cartella>` stamperebbe
_GIT_COMMIT_COPIA_MESSAGGIO = ("--reuse-message", "--reedit-message", "--fixup", "--squash")
#: opzioni lunghe di `git commit` che prendono un valore, anche separato
_GIT_COMMIT_LUNGHE_CON_VALORE = ("--message", "--file", "--template", "--author", "--date", "--trailer",
                                 "--reuse-message", "--reedit-message", "--fixup", "--squash", "--cleanup")

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


def _variabile_pericolosa(nome: str) -> bool:
    """In campagna: una variabile che, assegnata, cambia cio' che un comando fa o dove legge."""
    return nome in _VARIABILI_PERICOLOSE or (nome.startswith("GIT_") and nome not in _VARIABILI_GIT_INNOCUE)


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
    if prog in _BUILTIN_ASSEGNAZIONE:
        for a in argomenti:
            if _variabile_pericolosa(a.split("=", 1)[0]):
                return rifiuta(f"{prog} {a.split('=', 1)[0]} cambia cio' che i comandi successivi fanno")
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


def _ambiente_git(radice: str) -> dict:
    """L'ambiente per le domande che il guardiano fa a git: senza le variabili
    `GIT_*` (potrebbero puntare a un altro repo) e senza cercare un repo sopra la radice."""
    ambiente = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    ambiente["GIT_CEILING_DIRECTORIES"] = os.path.dirname(radice)
    return ambiente


@functools.lru_cache(maxsize=64)
def _antenato_di_head(sha: str, radice: str) -> bool:
    """True se `sha` e' un commit della storia del branch corrente (antenato di HEAD).

    Lo chiede a git (`merge-base --is-ancestor`), senza shell, nella radice del
    repo, con un tempo massimo (vedi `_ambiente_git`). Qualunque errore (non e'
    un repo, hash ambiguo, non e' un commit, tempo scaduto) vale "no": nel
    dubbio l'hash non e' proprio.
    """
    try:
        esito = subprocess.run(
            ["git", "merge-base", "--is-ancestor", sha, "HEAD"],
            cwd=radice, env=_ambiente_git(radice), stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL, timeout=_TEMPO_GIT, check=False,
        )
    except (OSError, ValueError, subprocess.SubprocessError):
        return False
    return esito.returncode == 0


@functools.lru_cache(maxsize=4)
def _branch_corrente(radice: str) -> str | None:
    """Il nome del branch su cui sta HEAD (`git rev-parse --abbrev-ref HEAD`), o None.

    Stesse cautele di `_antenato_di_head`. Con HEAD staccato git risponde
    `HEAD`; fuori da un repo, o se git non risponde in tempo, None: in
    entrambi i casi il branch non e' il proprio, e nel dubbio si blocca.
    """
    try:
        esito = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            cwd=radice, env=_ambiente_git(radice), stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL, timeout=_TEMPO_GIT, check=False, text=True,
        )
    except (OSError, ValueError, subprocess.SubprocessError):
        return None
    if esito.returncode != 0:
        return None
    return esito.stdout.strip() or None


def _e_riferimento_proprio(token: str, ctx: Contesto) -> bool:
    """HEAD (con `~N`/`^N`), il proprio branch (anche `origin/...`) o un hash proprio.

    Un hash (anche con `~N`/`^N`) e' proprio solo se e' un antenato di HEAD:
    un hash qualunque puo' venire dall'archivio di un tentativo precedente
    (lo stampava `git fetch`), e `git log <hash> -- research/campagne/X/`
    mostrerebbe i suoi commit. Se la base e' un antenato, lo sono anche i suoi
    genitori. Intervalli (`a..b`), `@{...}`, `^{...}`, `:/testo` non sono propri.
    Vale solo dove git stampa nomi e messaggi, non contenuti: per quelli vedi
    `_e_riferimento_stretto`.
    """
    proprio = ctx.proprio_branch
    if _HEAD.match(token) or token in (proprio, f"origin/{proprio}"):
        return True
    m = _HASH.match(token)
    return m is not None and _antenato_di_head(m.group(1), ctx.radice)


def _e_riferimento_stretto(token: str, ctx: Contesto) -> bool:
    """Esattamente HEAD, il proprio branch o `origin/<proprio branch>`.

    I soli riferimenti ammessi dai comandi che stampano o rimettono sul disco il
    CONTENUTO di una revisione (`_GIT_CONTENUTO`): un antenato di HEAD (`HEAD~3`,
    un hash) puo' essere un commit del branch principale con una versione
    vecchia di un file della propria cartella.
    """
    return token in ("HEAD", ctx.proprio_branch, f"origin/{ctx.proprio_branch}")


def _refspec_push(ctx: Contesto) -> frozenset[str]:
    """I refspec con cui `git push` puo' scrivere: solo il proprio branch, mai forzato."""
    b = ctx.proprio_branch
    pieno = f"refs/heads/{b}"
    return frozenset({"HEAD", b, pieno, f"HEAD:{b}", f"HEAD:{pieno}", f"{b}:{b}", f"{b}:{pieno}", f"{pieno}:{pieno}"})


def _refspec_fetch(ctx: Contesto) -> frozenset[str]:
    """I refspec con cui `git fetch` e `git pull` possono scaricare: solo il proprio branch."""
    b = ctx.proprio_branch
    pieno = f"refs/heads/{b}"
    remoto = f"refs/remotes/origin/{b}"
    return frozenset({b, pieno, f"{b}:{remoto}", f"{pieno}:{remoto}"})


def _opzione_lunga(opzione: str, lunghe: tuple[str, ...]) -> bool:
    """True se `opzione` (prima di `=`) e' una delle `lunghe` o un loro inizio.

    I comandi di git costruiti su parse-options accettano le abbreviazioni:
    `git grep --open=cmd` e' `--open-files-in-pager=cmd`, `git branch --al` e'
    `--all`. Le opzioni corte (`-g`) contano solo se uguali.
    """
    nome = opzione.split("=", 1)[0]
    if nome in lunghe:
        return True
    return nome.startswith("--") and len(nome) > 2 and any(lunga.startswith(nome) for lunga in lunghe if lunga.startswith("--"))


def _destinazioni_git(resto: list[str]) -> list[str]:
    """I file (o le cartelle) che un'opzione fa SCRIVERE a git.

    `--output=<file>` (log, show, diff... e anche `diff-files`) scrive l'uscita
    in un file: con un'uscita vuota svuoterebbe `research/.sessione`, e senza
    marcatore il guardiano si spegne. Un'opzione senza valore restituisce ""
    (che si rifiuta: e' la radice).
    """
    destinazioni: list[str] = []
    for j, a in enumerate(resto):
        if a == "--":
            break
        nome, uguale, valore = a.partition("=")
        if _opzione_lunga(nome, ("--output", "--output-directory")):
            destinazioni.append(valore if uguale else (resto[j + 1] if j + 1 < len(resto) else ""))
    return destinazioni


def _lettere_corte(opzione: str, con_valore: str) -> str:
    """Le lettere di un gruppo di opzioni corte (`-nO` -> `nO`), fino alla prima
    che prende un valore attaccato (`-L1,5` -> `L`): il resto e' il valore."""
    if not opzione.startswith("-") or opzione.startswith("--"):
        return ""
    lettere = ""
    for c in opzione[1:]:
        lettere += c
        if c in con_valore:
            break
    return lettere


def _opzione_di_contenuto(a: str) -> bool:
    """Nei comandi di storia: un'opzione che stampa o cerca il CONTENUTO dei commit."""
    if a.startswith("--"):
        nome = a.split("=", 1)[0]
        if nome in _GIT_STORIA_OPZIONI_ESATTE_AMMESSE:
            return False
        return nome.startswith(("--word-diff", "--pickaxe")) or _opzione_lunga(nome, _GIT_STORIA_CONTENUTO_LUNGHE)
    return any(c in _GIT_STORIA_CONTENUTO_CORTE for c in _lettere_corte(a, _GIT_STORIA_CORTE_CON_VALORE))


def _giudica_sincronizzazione(sub: str, resto: list[str], ctx: Contesto, rifiuta) -> Verdetto:
    """`git push`, `git fetch`, `git pull` in campagna: solo il proprio branch.

    Forma: opzioni della lista bianca `_GIT_SYNC_OPZIONI`, poi il nome del
    remoto, poi i refspec.
      * `fetch` e `pull` vogliono ESATTAMENTE un refspec, il proprio branch
        (`_refspec_fetch`): senza, scaricano tutti i branch e ne stampano i
        nomi (archivi compresi); con un hash o un altro nome, scaricano altro;
      * `push` accetta solo refspec verso il proprio branch (`_refspec_push`),
        mai forzati (`+`) ne' cancellazioni; senza refspec (`git push`,
        `git push origin`) spinge il branch corrente, che `_giudica_git` ha
        gia' verificato essere il proprio.
    """
    ammesse = _GIT_SYNC_OPZIONI[sub]
    corte = {o[1] for o in ammesse if len(o) == 2}
    posizionali: list[str] = []
    solo_operandi = False
    for a in resto:
        if a == "--" and not solo_operandi:
            solo_operandi = True
            continue
        if a.startswith("-") and len(a) > 1 and not solo_operandi:
            if a in ammesse or (not a.startswith("--") and all(c in corte for c in a[1:])):
                continue
            return rifiuta(f"git {sub} {a}: in campagna sono ammesse solo le opzioni {', '.join(sorted(ammesse))}")
        posizionali.append(a)
    b = ctx.proprio_branch
    if sub == "push" and not posizionali:
        return OK
    if sub != "push" and len(posizionali) <= 1:
        return rifiuta(f"git {sub} senza il nome del proprio branch scarica tutti i branch e ne stampa i nomi: "
                       f"usa `git {sub} origin {b}`")
    remoto, refspec = posizionali[0], posizionali[1:]
    if not _NOME_REMOTO.match(remoto):
        return rifiuta(f"git {sub} {remoto}: il remoto deve essere un nome (origin), non un indirizzo o un percorso")
    if sub == "push":
        for r in refspec:
            if r not in _refspec_push(ctx):
                return rifiuta(f"git push {r}: in campagna si spinge solo il proprio branch, senza forzare "
                               f"(`git push -u origin {b}`)")
        return OK
    if len(refspec) != 1 or refspec[0] not in _refspec_fetch(ctx):
        return rifiuta(f"git {sub} {' '.join(refspec)}: in campagna si scarica solo il proprio branch "
                       f"(`git {sub} origin {b}`)")
    return OK


def _giudica_commit(resto: list[str], rifiuta) -> Verdetto:
    """`git commit` in campagna: mai il messaggio di un altro commit.

    `-C`/`-c <commit>`, `--reuse-message`, `--fixup`, `--squash` copiano il
    messaggio di un commit qualunque (anche del branch principale) in uno nuovo
    che tocca la propria cartella: `git log --format=%B -- <propria cartella>`
    lo stamperebbe. Per lo stesso motivo `--amend` vuole un messaggio nuovo
    (`-m` o `-F`): appena creato il branch, HEAD e' un commit del principale.
    """
    con_messaggio = False
    correzione = False
    salta = False
    for a in resto:
        if salta:
            salta = False
            continue
        if a == "--":
            break
        if not a.startswith("-") or a == "-":
            continue
        if a.startswith("--"):
            if _opzione_lunga(a, _GIT_COMMIT_COPIA_MESSAGGIO):
                return rifiuta(f"git commit {a} copia il messaggio di un altro commit")
            con_messaggio |= _opzione_lunga(a, ("--message", "--file"))
            correzione |= _opzione_lunga(a, ("--amend",))
            salta = "=" not in a and _opzione_lunga(a, _GIT_COMMIT_LUNGHE_CON_VALORE)
            continue
        lettere = _lettere_corte(a, "mFtCcSu")
        if "C" in lettere or "c" in lettere:
            return rifiuta(f"git commit {a} copia il messaggio di un altro commit")
        con_messaggio |= lettere[-1:] in ("m", "F")
        salta = lettere[-1:] in ("m", "F", "t") and len(a) == len(lettere) + 1
    if correzione and not con_messaggio:
        return rifiuta("git commit --amend senza -m/-F tiene il messaggio di HEAD, che puo' essere un commit "
                       "del branch principale")
    return OK


def _giudica_git(argomenti: list[str], ctx: Contesto, comando: str) -> Verdetto:
    """git in campagna: solo i sottocomandi della lista bianca, solo il proprio
    branch, mai il contenuto della storia, mai i messaggi dei commit fuori dalla
    propria cartella (vedi `_giudica_git_sottocomando`).

    Dopo il giudizio sulla forma, `commit`, `push`, `pull`, `reset` e `stash`
    passano solo se HEAD e' sul proprio branch (lo si chiede a git): con HEAD
    sul branch principale e il marcatore gia' scritto, `git commit` e
    `git push origin HEAD` finirebbero sul principale.
    """
    rifiuta = lambda motivo: Verdetto(False, f"{comando!r} ({motivo})")  # noqa: E731
    # opzioni globali: `-c chiave=valore` cambia pager/editor/alias, e il guardiano non lo vede;
    # `--work-tree`/`--git-dir` portano git su un altro albero (`reset --hard` lo riempirebbe
    # con tutto il repo) o su un altro repository; `--exec-path` fa eseguire a git i suoi
    # programmi (anche `git` stesso, che `pull` richiama) da un'altra cartella
    i = 0
    while i < len(argomenti) and argomenti[i].startswith("-"):
        globale = argomenti[i].split("=", 1)[0]
        if globale in ("-c", "--config-env"):
            return rifiuta("git -c cambia la configurazione sotto il guardiano")
        if globale in ("--work-tree", "--git-dir"):
            return rifiuta(f"git {globale} porta git su un altro albero di lavoro o un altro repository")
        if globale == "--exec-path":
            return rifiuta("git --exec-path fa eseguire a git i programmi di un'altra cartella")
        i += 2 if argomenti[i] in _GIT_GLOBALI_CON_VALORE else 1
    if i >= len(argomenti):
        return OK
    sub, resto = argomenti[i], argomenti[i + 1:]
    if sub not in _GIT_AMMESSI_CAMPAGNA:
        return rifiuta(f"git {sub} non e' fra i sottocomandi ammessi in campagna (esce dal proprio branch, "
                       "legge altro o esegue cio' che il guardiano non vede)")
    verdetto = _giudica_git_sottocomando(sub, resto, ctx, rifiuta)
    if verdetto.consentito and sub in _GIT_SUL_PROPRIO_BRANCH:
        corrente = _branch_corrente(ctx.radice)
        if corrente != ctx.proprio_branch:
            dove = f"con HEAD su {corrente}" if corrente else "senza sapere su quale branch e' HEAD"
            return rifiuta(f"git {sub} {dove}: in campagna si fa solo sul proprio branch {ctx.proprio_branch}")
    return verdetto


def _giudica_git_sottocomando(sub: str, resto: list[str], ctx: Contesto, rifiuta) -> Verdetto:
    """La forma di un sottocomando git ammesso in campagna.

    La storia del branch di campagna contiene TUTTO il repo (docs/ compreso) e
    tutti i messaggi del branch principale: `git log -p`, `git show HEAD`,
    `git diff HEAD~5` li stamperebbero. Quindi:
      * chi prende riferimenti deve usare HEAD, il proprio branch o un hash
        antenato di HEAD; chi stampa CONTENUTI (`_GIT_CONTENUTO`) solo HEAD o
        il proprio branch, senza `~N` ne' hash; `rif:percorso` si giudica
        anche dopo i due punti;
      * i comandi di STORIA (`_GIT_STORIA`) vogliono almeno un percorso, e tutti
        i percorsi dentro `research/campagne/<SIMBOLO>/` (per `log` e simili
        dopo `--`); senza le opzioni che scavalcano il filtro o stampano il
        contenuto dei commit;
      * `git show` solo come `<rif>:<percorso>` (il file, senza il messaggio);
      * `diff` con un riferimento, `grep`, `ls-tree` e `ls-files` vogliono un
        percorso ammesso;
      * un file scritto da un'opzione (`--output=`) si giudica come scrittura;
      * `push`, `fetch`, `pull` si giudicano in `_giudica_sincronizzazione`,
        `commit` in `_giudica_commit`.
    """
    if sub == "remote" and resto:
        return rifiuta("git remote con argomenti mostra l'URL del remoto")
    if sub in _GIT_SYNC_OPZIONI:
        return _giudica_sincronizzazione(sub, resto, ctx, rifiuta)
    for destinazione in _destinazioni_git(resto):
        if not giudica_percorso(destinazione, ctx, scrittura=True).consentito:
            return rifiuta(f"git {sub} scrive in {destinazione!r}, che in campagna non si puo' scrivere")
    if sub == "grep" and any(_opzione_lunga(a, ("--open-files-in-pager",)) or "O" in _lettere_corte(a, "efABCmO")
                             for a in itertools.takewhile(lambda x: x != "--", resto)):
        return rifiuta("git grep -O esegue un programma scelto da chi chiama")
    if sub == "commit":
        return _giudica_commit(resto, rifiuta)
    if sub == "stash":
        for a in itertools.takewhile(lambda x: x != "--", resto):
            if a in _GIT_STASH_VIETATE:
                return rifiuta(f"git stash {a} lavora su un commit qualunque o cambia branch")
            if "a" in _lettere_corte(a, "m"):
                return rifiuta("git stash -a mette da parte anche i file ignorati da git, marcatore compreso")
    if sub not in _GIT_CON_RIFERIMENTI:
        return OK  # status, add, rm, mv, diff-files, help...: niente riferimenti
    storia = sub in _GIT_STORIA
    contenuto = sub in _GIT_CONTENUTO
    for a in resto:
        if a == "--":
            break
        if _opzione_lunga(a, _GIT_OPZIONI_VIETATE):
            return rifiuta(f"git {sub} {a} guarda tutti i branch")
        if _opzione_lunga(a, _GIT_OPZIONI_DA_FUORI):
            return rifiuta(f"git {sub} {a} prende riferimenti o percorsi che il guardiano non vede")
        if storia and _opzione_lunga(a, _GIT_STORIA_OPZIONI_VIETATE):
            return rifiuta(f"git {sub} {a} mostra commit o file fuori dai percorsi dati")
        if sub in _GIT_STORIA_CON_DOPPIO_TRATTINO and _opzione_di_contenuto(a):
            return rifiuta(f"git {sub} {a} stampa il contenuto dei commit: la storia della propria cartella "
                           "comincia sul branch principale, con versioni vecchie dei suoi file")
        if sub in ("blame", "annotate") and any(c in "CS" for c in _lettere_corte(a, "LMCS")):
            # -C: righe copiate da ALTRI file (e i messaggi dei loro commit); -S: storia da un file
            return rifiuta(f"git {sub} {a} guarda fuori dal file dato")
        if sub == "branch" and (_opzione_lunga(a, ("--verbose", "--list")) or (
                a.startswith("-") and not a.startswith("--") and any(c in "arv" for c in a[1:]))):
            return rifiuta(f"git branch {a} mostra gli altri branch e i loro hash")
        # `--source=<rif>`, `ls-files --with-tree=<rif>` (anche abbreviati) e `restore -s<rif>`
        # attaccato: il riferimento va controllato
        sorgente = None
        if "=" in a and _opzione_lunga(a, ("--source", "--with-tree")):
            sorgente = a.split("=", 1)[1]
        elif sub == "restore" and "s" in (lettere := _lettere_corte(a, "s")) and len(a) > len(lettere) + 1:
            sorgente = a[len(lettere) + 1:]
        if sorgente is not None and not (_e_riferimento_stretto(sorgente, ctx) if contenuto
                                         else _e_riferimento_proprio(sorgente, ctx)):
            return rifiuta(f"git {sub} {a}: in campagna si legge solo da HEAD o dal proprio branch "
                           "(senza ~N ne' hash)")
    # operandi: prima di `--` possono essere riferimenti, dopo solo percorsi
    percorsi: list[str] = []  # operandi giudicati come percorsi (tutti ammessi)
    percorsi_prima_del_doppio_trattino = False
    riferimenti: list[str] = []  # riferimenti propri, anche quelli di `rif:percorso`
    rif_percorso = 0  # operandi `rif:percorso`
    operandi_semplici = 0  # operandi che non sono `rif:percorso`
    dopo_doppio_trattino = False
    pattern_visto = False
    salta_valore = False  # il valore separato di `--output <file>` / `stash -m <messaggio>`, gia' giudicato
    for a in resto:
        if salta_valore:
            salta_valore = False
            continue
        if a == "--":
            dopo_doppio_trattino = True
            continue
        if a.startswith("-") and not dopo_doppio_trattino:
            lettere = _lettere_corte(a, "m")
            messaggio_di_stash = sub == "stash" and (
                a == "--message" or (lettere.endswith("m") and len(a) == len(lettere) + 1))
            salta_valore = messaggio_di_stash or (
                "=" not in a and _opzione_lunga(a, ("--output", "--output-directory")))
            continue
        if not dopo_doppio_trattino and sub == "stash" and a in _GIT_STASH_PAROLE:
            continue
        if not dopo_doppio_trattino and sub == "grep" and not pattern_visto and _candidato_percorso(a, ctx.primo_livello) is None:
            pattern_visto = True  # il primo operando di `git grep` e' cio' che si cerca
            continue
        riferimento, _, percorso = a.partition(":") if (":" in a and not dopo_doppio_trattino) else ("", "", "")
        if riferimento:
            if contenuto and not _e_riferimento_stretto(riferimento, ctx):
                return rifiuta(f"git {sub} {a}: in campagna il contenuto si legge solo da HEAD o dal proprio "
                               "branch (senza ~N ne' hash: un antenato puo' essere un commit del branch principale)")
            if not _e_riferimento_proprio(riferimento, ctx):
                return rifiuta(f"git {sub} {a} legge da un altro branch o da un commit che non e' nella propria storia")
            if not giudica_percorso(percorso, ctx).consentito:
                return rifiuta(f"git {sub} {a}: percorso vietato")
            riferimenti.append(riferimento)
            rif_percorso += 1
            continue
        operandi_semplici += 1
        if not dopo_doppio_trattino and _e_riferimento_proprio(a, ctx):
            if contenuto and not _e_riferimento_stretto(a, ctx):
                return rifiuta(f"git {sub} {a}: in campagna il contenuto si legge solo da HEAD o dal proprio "
                               "branch (senza ~N ne' hash: un antenato puo' essere un commit del branch principale)")
            riferimenti.append(a)
            continue
        if _candidato_percorso(a, ctx.primo_livello) is None and not os.path.lexists(os.path.join(ctx.radice, a)):
            # ne' riferimento proprio ne' percorso: `main`, un nome calcolato, un tag, un intervallo,
            # un hash che non e' un antenato di HEAD
            return rifiuta(f"git {sub} {a} non e' HEAD, il proprio branch, un commit della propria storia "
                           "o un percorso ammesso")
        if not giudica_percorso(a, ctx).consentito:
            return rifiuta(f"git {sub} {a}: percorso vietato")
        percorsi.append(a)
        percorsi_prima_del_doppio_trattino |= not dopo_doppio_trattino
    con_percorso_ammesso = bool(percorsi)
    if storia:
        cartella = f"research/campagne/{ctx.simbolo}"
        if rif_percorso:
            return rifiuta(f"git {sub} vuole commit e percorsi, non `rif:percorso`")
        if sub in _GIT_STORIA_CON_DOPPIO_TRATTINO and percorsi_prima_del_doppio_trattino:
            return rifiuta(f"git {sub}: in campagna i percorsi vanno dopo `--` (un'opzione con valore "
                           "puo' ingoiarli e lasciare git senza filtro)")
        if not percorsi:
            return rifiuta(f"git {sub} senza percorso stampa i messaggi di tutta la storia: "
                           f"serve `-- {cartella}/`")
        for p in percorsi:
            if not _sotto(normalizza(p, ctx.radice), cartella):
                return rifiuta(f"git {sub} {p}: in campagna la storia si guarda solo per {cartella}/")
    elif sub == "show":
        if not rif_percorso or operandi_semplici or dopo_doppio_trattino:
            return rifiuta("git show stampa il messaggio di un commit (forse del branch principale): "
                           "in campagna solo `<rif>:<percorso>`")
    elif sub in ("diff", "diff-index"):
        if (riferimenti or sub != "diff") and not con_percorso_ammesso:
            return rifiuta(f"git {sub} con un riferimento confronta tutta la storia: serve un percorso ammesso")
    elif sub == "grep" and not con_percorso_ammesso:
        return rifiuta("git grep senza percorso cerca in tutto il repo")
    elif sub in _GIT_CON_PERCORSO_OBBLIGATORIO and not (con_percorso_ammesso or rif_percorso):
        return rifiuta(f"git {sub} senza percorso elenca i file di tutto il repo, anche le cartelle delle "
                       "altre monete: serve un percorso ammesso")
    return OK


def giudica_comando(comando: str, ctx: Contesto, profondita: int = 0) -> Verdetto:
    """Giudica una riga di shell: i branch, i programmi, poi ogni percorso (espanso)."""
    if ctx.campagna:
        # qualunque riferimento a un branch del protocollo che non sia il proprio
        for m in _BRANCH.finditer(comando):
            if m.group(0) != ctx.proprio_branch:
                return Verdetto(False, f"{comando!r} (branch {m.group(0)})")
    propri = {ctx.proprio_branch, f"origin/{ctx.proprio_branch}"}
    # i refspec del proprio branch (`HEAD:refs/heads/research/campagna/X`), che `_giudica_git` ha gia' giudicato
    refspec_propri = (_refspec_push(ctx) | _refspec_fetch(ctx)) if ctx.campagna else frozenset()
    for separatore, segmento in _segmenti(_spezza(comando)):
        prog, argomenti, assegnazioni = _programma_effettivo(segmento)
        if ctx.campagna:
            for a in assegnazioni:
                if _variabile_pericolosa(a.split("=", 1)[0]):
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
            if prog == "git" and t in refspec_propri:
                continue  # un refspec del proprio branch, gia' giudicato da `_giudica_git`
            if ctx.campagna and prog == "git" and ":" in t:
                riferimento, _, dopo_i_due_punti = t.partition(":")
                if riferimento and _e_riferimento_proprio(riferimento, ctx):
                    # `<rif>:<percorso>` (`git show HEAD~1:research/...`): conta il percorso
                    t = dopo_i_due_punti
            parole = espandi_token(t, ctx)
            if parole is None:
                return Verdetto(False, f"{comando!r} (il token {t!r} viene espanso dalla shell in modo imprevedibile)")
            for parola in parole:
                cand = _candidato_percorso(parola, ctx.primo_livello)
                if cand is None or (ctx.campagna and prog == "git" and cand in propri):
                    continue  # `--source=origin/<proprio branch>`: un riferimento, gia' giudicato
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


def _decodifica_ripetuta(testo: str) -> str | None:
    """`%xx` decodificato finche' il testo non cambia piu' (`%252F` -> `%2F` -> `/`).
    None se non si stabilizza in `_MAX_DECODIFICHE` passi: nel dubbio si rifiuta."""
    for _ in range(_MAX_DECODIFICHE):
        decodificato = urllib.parse.unquote(testo)
        if decodificato == testo:
            return testo
        testo = decodificato
    return None


def _host_ammesso_web(host: str) -> bool:
    """L'host (gia' in minuscolo) e' uno dei siti ammessi o un loro sottodominio."""
    return any(host == dominio or host.endswith("." + dominio) for dominio in _HOST_AMMESSI_WEB)


def _host_di(testo: str) -> str | None:
    """L'host di un indirizzo http(s) semplice (in minuscolo, senza il punto finale), o None.

    None se l'indirizzo non si legge, non e' http(s), non ha un host, porta
    credenziali (`utente@host`: il browser e Python possono leggerle in modo
    diverso) o l'host non e' un nome di dominio semplice (un IP, caratteri
    codificati o non ASCII che il browser riscriverebbe in un altro nome).
    """
    try:
        parti = urllib.parse.urlsplit(testo)
        host = parti.hostname
        parti.port  # solleva ValueError se la porta non e' un numero
    except ValueError:
        return None
    if parti.scheme.lower() not in ("http", "https") or not host or "@" in parti.netloc:
        return None
    host = host.lower().rstrip(".")
    return host if _HOST_VALIDO.match(host) else None


def giudica_url(url, ctx: Contesto) -> Verdetto:
    """WebFetch in campagna: solo verso i siti di articoli scientifici di `_HOST_AMMESSI_WEB`.

    Una lista NERA (GitHub, claude.ai, anthropic.com) non bastava: il repo e'
    pubblico, e ogni CDN o specchio di GitHub (cdn.jsdelivr.net, githack,
    sourcegraph, web.archive.org...) serve qualunque branch, archivi compresi.
    L'indirizzo si decodifica (`%xx`) finche' non cambia piu'; si rifiuta se
    era codificato due volte (`%25`), se contiene `\\` o spazi (che il browser e
    Python leggono in modo diverso), se l'host dell'indirizzo com'e' e quello
    dell'indirizzo decodificato non sono lo stesso host ammesso
    (`https://arxiv.org%2F@github.com/` apre github.com), se nomina un branch
    del protocollo che non e' il proprio.
    """
    if not isinstance(url, str) or not url.strip():
        return Verdetto(False, "WebFetch senza indirizzo")
    rifiuta = lambda motivo: Verdetto(False, f"WebFetch {url!r} ({motivo})")  # noqa: E731
    grezzo = url.strip()
    if "\\" in grezzo or any(c.isspace() or ord(c) < 32 or ord(c) == 127 for c in grezzo):
        return rifiuta("l'indirizzo contiene `\\` o spazi")
    decodificato = _decodifica_ripetuta(grezzo)
    if decodificato is None or "%25" in grezzo or "%25" in decodificato:
        return rifiuta("indirizzo codificato piu' volte")
    host = _host_di(grezzo)
    if host is None or _host_di(decodificato) != host:
        return rifiuta("indirizzo illeggibile, non http(s), con credenziali o con un host che non e' un nome "
                       "di dominio semplice")
    if not _host_ammesso_web(host):
        return rifiuta(f"in campagna WebFetch apre solo siti di articoli scientifici "
                       f"({', '.join(_HOST_AMMESSI_WEB)}), non {host}")
    for m in _BRANCH.finditer(decodificato):
        if m.group(0) != ctx.proprio_branch:
            return rifiuta(f"branch {m.group(0)}")
    # un indirizzo dentro l'indirizzo (`?url=https://...`, `?redirect=//...`) o un
    # hash di commit: un sito ammesso con un rinvio aperto porterebbe altrove, e
    # con un hash il controllo dei nomi dei branch non scatta (prova del 7 ott)
    parti = urllib.parse.urlsplit(decodificato)
    resto = (parti.path + "?" + parti.query + "#" + parti.fragment).lower()
    if "http:" in resto or "https:" in resto or "//" in (parti.query + parti.fragment) or "www." in (parti.query + parti.fragment):
        return rifiuta("l'indirizzo ne contiene un altro (rinvio)")
    # (nel percorso un hash di 40 cifre e' normale, per esempio gli articoli di
    # semanticscholar; nei parametri no)
    if re.search(r"(?<![0-9a-f])[0-9a-f]{40}(?![0-9a-f])", (parti.query + "#" + parti.fragment).lower()):
        return rifiuta("l'indirizzo contiene un hash di commit nei parametri")
    return OK


#: lettere di altri alfabeti che sembrano latine (omoglifi): si riportano alla
#: lettera latina prima di cercare le parole vietate, cosi' «gіthub» con una
#: «і» cirillica non sfugge al filtro
_OMOGLIFI = str.maketrans({
    "а": "a", "е": "e", "і": "i", "ї": "i", "о": "o", "р": "p", "с": "c", "у": "y", "х": "x",
    "һ": "h", "ԁ": "d", "ѕ": "s", "ј": "j", "ӏ": "l", "ԛ": "q", "ԝ": "w", "ɡ": "g", "ı": "i",
    "к": "k", "м": "m", "т": "t", "в": "b", "н": "h", "ս": "u", "ո": "n", "ᴜ": "u", "ʜ": "h",
    "α": "a", "ο": "o", "ρ": "p", "ι": "i", "κ": "k", "ν": "v", "τ": "t", "υ": "u", "χ": "x",
})


def _testo_normalizzato(testo: str) -> str:
    """Minuscolo, NFKC, omoglifi riportati al latino, SENZA spazi, punteggiatura e
    caratteri invisibili: «G i t H u b», «git-hub» e «gіthub» diventano «github»."""
    testo = unicodedata.normalize("NFKC", testo).lower().translate(_OMOGLIFI)
    return "".join(c for c in testo if c.isalnum() or c == "/")


def _host_di_dominio(valore: str) -> str:
    """Un dominio scritto a mano (`site:`, `allowed_domains`): `https://www.x.org/a` -> `www.x.org`."""
    valore = valore.strip().strip("\"'").lower()
    valore = re.sub(r"^[a-z][a-z0-9+.-]*://", "", valore)
    valore = re.split(r"[/?#]", valore, maxsplit=1)[0]
    valore = valore.lstrip("*").lstrip(".").rstrip(".")
    return valore


def giudica_ricerca_web(ingresso: dict, ctx: Contesto) -> Verdetto:
    """WebSearch in campagna: ammessa (serve a trovare le fonti di prima del 2024),
    ma non verso questo repository.

    Si rifiuta una ricerca il cui testo, in minuscolo e decodificato (`%xx`)
    finche' non cambia piu', contiene una parola di `_PAROLE_VIETATE_RICERCA`
    (GitHub e i suoi specchi, il nome del repo e del proprietario, i branch del
    protocollo), o un `site:` verso un sito che non e' fra quelli ammessi per
    WebFetch; e una ricerca con `allowed_domains` fuori da quella lista.
    """
    domanda = ingresso.get("query")
    if not isinstance(domanda, str) or not domanda.strip():
        return Verdetto(False, "WebSearch senza testo")
    rifiuta = lambda motivo: Verdetto(False, f"WebSearch {domanda!r} ({motivo})")  # noqa: E731
    decodificata = _decodifica_ripetuta(domanda)
    if decodificata is None:
        return rifiuta("testo codificato troppe volte")
    testo = decodificata.lower()
    compatto = _testo_normalizzato(decodificata)
    for parola in _PAROLE_VIETATE_RICERCA:
        if parola in testo or _testo_normalizzato(parola) in compatto:
            return rifiuta(f"contiene {parola!r}: porta a questo repository o ai suoi branch")
    for m in re.finditer(r"\bsite\s*:\s*(\S*)", testo):
        host = _host_di_dominio(m.group(1))
        if not host or not _host_ammesso_web(host):
            return rifiuta(f"site:{m.group(1)} non e' fra i siti ammessi in campagna")
    domini = ingresso.get("allowed_domains")
    if domini is not None:
        if not isinstance(domini, list) or not all(isinstance(d, str) for d in domini):
            return rifiuta("allowed_domains non e' un elenco di domini")
        for dominio in domini:
            host = _host_di_dominio(_decodifica_ripetuta(dominio) or "")
            if not host or not _host_ammesso_web(host):
                return rifiuta(f"allowed_domains contiene {dominio!r}, che non e' fra i siti ammessi in campagna")
    return OK


def giudica_azione(nome: str, ingresso: dict, ctx: Contesto) -> Verdetto:
    """Il verdetto sull'azione: file singolo, ricerca, comando o altro strumento.

    In campagna nel dubbio blocca: un percorso o un comando mancante si
    rifiuta, e uno strumento che non e' ne' file ne' ricerca ne' Bash passa solo
    se e' nella lista BIANCA `_STRUMENTI_AMMESSI_CAMPAGNA` (WebFetch se l'
    indirizzo passa `giudica_url`, WebSearch se la ricerca passa
    `giudica_ricerca_web`). In coordinamento gli altri strumenti non sono affare
    del guardiano.
    """
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
    if not severo:
        return OK  # coordinamento: gli altri strumenti non sono compito nostro
    if nome == "WebFetch":
        return giudica_url(ingresso.get("url"), ctx)
    if nome == "WebSearch":
        return giudica_ricerca_web(ingresso, ctx)
    if nome in _STRUMENTI_AMMESSI_CAMPAGNA:
        return OK
    return Verdetto(
        False,
        f"lo strumento {nome} (non e' fra quelli ammessi in campagna: puo' leggere altri branch, "
        "la storia o le sessioni precedenti)",
    )


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
