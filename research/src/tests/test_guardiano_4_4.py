"""Revisione 4.4 del guardiano (7 ottobre 2026): la storia, l'archivio, gli altri strumenti.

Che cosa si protegge e perche'. Quando una campagna della prova di processo si
rifa', la sessione nuova lavora su un branch NUOVO `research/campagna/<SIMBOLO>`
nato dal branch principale, e il tentativo precedente diventa
`research/archivio/campagna/<SIMBOLO>`, con file agli STESSI percorsi
(`research/campagne/<SIMBOLO>/log.jsonl`, `ipotesi.md`, `consegna.md`...). La
sessione nuova non deve poterli leggere, e nemmeno i messaggi dei commit del
branch principale: parlano del lavoro di coordinamento, e ~1.500 commit del bot
sono stati scritti nel periodo chiuso del vault (2024-2026).

Una revisione avversaria ha trovato, in campagna, tre buchi:
  1. i comandi di storia senza percorso (`git log`, `git show HEAD`,
     `git shortlog`, `git rev-list --format=%B`, `git blame` di un file fuori
     dalla propria cartella) stampavano i messaggi di tutto il branch principale;
  2. qualunque hash valeva come "proprio": un hash dell'archivio (lo stampava
     `git fetch`) apriva `git show <hash>:research/campagne/X/log.jsonl`;
     `show-branch`, `name-rev`, `describe` non erano vietati;
  3. il guardiano vedeva solo file, ricerche e Bash: gli strumenti MCP di GitHub
     (che leggono qualunque branch), quelli delle sessioni remote (i cui prompt
     possono parlare di altre campagne), gli Artifact e WebFetch verso
     raw.githubusercontent.com passavano senza controllo.

Altre due revisioni e una prova d'attacco hanno trovato, sempre in campagna
(sezione «seconda revisione» in fondo):
  A. con HEAD sul branch principale `git commit` e `git push origin HEAD`
     finivano sul principale;
  B. `git fetch` e `git pull` senza il nome del branch scaricavano tutti i branch
     e ne stampavano i nomi, archivi compresi;
  C. la storia della propria cartella comincia sul branch principale: `git log -p`,
     `git show HEAD~3:<file>`, `git diff HEAD~3` stampavano versioni VECCHIE dei
     suoi file (un campo della scheda tolto dopo); e altri comandi git (`clean -X`,
     `stash -a`, `update-index`) toglievano il marcatore o rimettevano sul disco
     una versione vecchia;
  D. WebFetch con una lista nera: ogni specchio di GitHub (jsdelivr, githack,
     sourcegraph, archive.org) serviva gli altri branch;
  E. WebSearch senza controllo sul testo della ricerca;
  F. `git --exec-path` (e le variabili `GIT_*`) facevano eseguire a git altro.

I test costruiscono un VERO repo git in una cartella temporanea: un branch
`main` con quattro commit (uno tocca CLAUDE.md, uno crea la scheda della moneta
con un campo, uno toglie quel campo, uno il protocollo), un archivio
`research/archivio/campagna/BTCUSDT` che aggiunge un `log.jsonl`, e il branch di
campagna `research/campagna/BTCUSDT` nato da `main`, con un commit suo, attivo,
e il marcatore di campagna. BTCUSDT qui e' solo il simbolo d'esempio. Per la
seconda revisione serve anche un remoto: un repo "nudo" `origine.git` con gli
stessi branch, e una sessione che apre il proprio branch come dice la sezione 9
del protocollo. Per i buchi ogni test prima ESEGUE il comando in bash e mostra
che stampa davvero qualcosa di riservato (cosi' nessun test segnala un falso
buco), poi pretende che il guardiano, eseguito come hook, lo rifiuti. Per i
comandi ammessi mostra che l'uscita non contiene nulla di riservato e che il
guardiano li lascia passare.
"""
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

RADICE_REPO = Path(__file__).resolve().parents[3]
GUARDIANO = RADICE_REPO / "research" / "src" / "guardiano.py"
VIETATI_REPO = RADICE_REPO / "research" / "config" / "percorsi_vietati.txt"

RIFIUTO = "[guardiano] azione rifiutata"
PROPRIO = "research/campagna/BTCUSDT"

#: testi riconoscibili: se compaiono nell'uscita di un comando, il comando ha letto troppo
MSG_PRINCIPALE = "MESSAGGIO_DEL_PRINCIPALE"  # commit di main che non tocca la propria cartella
MSG_CLAUDE = "MESSAGGIO_CLAUDE"  # commit di main che tocca CLAUDE.md
MSG_ARCHIVIO = "MESSAGGIO_ARCHIVIO"  # commit dell'archivio
CONTENUTO_ARCHIVIO = "ARCHIVIO_RISERVATO"  # log.jsonl dell'archivio
CONTENUTO_UNIVERSO = "UNIVERSO_RISERVATO"  # file di coordinamento toccato dallo stesso commit della scheda
CONTENUTO_VECCHIO = "CAMPO_RIMOSSO"  # un campo della scheda che un commit di main ha tolto dopo
ALTRA_MONETA = "ETHUSDT"  # la scheda di un'altra moneta, sul branch principale
RISERVATI = (MSG_PRINCIPALE, MSG_CLAUDE, MSG_ARCHIVIO, CONTENUTO_ARCHIVIO, CONTENUTO_UNIVERSO,
             CONTENUTO_VECCHIO, ALTRA_MONETA)


# ---------------------------------------------------------------------------
# attrezzi
# ---------------------------------------------------------------------------


def _ambiente_git(casa: Path) -> dict:
    """Ambiente per il git dei test: niente configurazione dell'utente, autore fisso."""
    ambiente = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    ambiente.update(
        HOME=str(casa),
        GIT_CONFIG_NOSYSTEM="1",
        GIT_AUTHOR_NAME="Prova",
        GIT_AUTHOR_EMAIL="prova@example.com",
        GIT_COMMITTER_NAME="Prova",
        GIT_COMMITTER_EMAIL="prova@example.com",
    )
    return ambiente


def _git(radice: Path, *argomenti: str) -> str:
    esito = subprocess.run(
        ["git", "-c", "commit.gpgsign=false", *argomenti],
        cwd=str(radice), env=_ambiente_git(radice.parent), capture_output=True, text=True, timeout=30,
    )
    assert esito.returncode == 0, esito.stderr
    return esito.stdout.strip()


def _scrivi(radice: Path, percorso: str, testo: str) -> None:
    p = radice / percorso
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(testo)


def _commit(radice: Path, messaggio: str, *percorsi: str) -> None:
    _git(radice, "add", *percorsi)
    _git(radice, "commit", "-q", "-m", messaggio)


def _storia_principale(radice: Path) -> None:
    """I quattro commit di `main` (radice gia' inizializzata, su `main`)."""
    _scrivi(radice, ".gitignore", "research/.sessione\nresearch/data/\n")
    _scrivi(radice, "research/config/percorsi_vietati.txt", VIETATI_REPO.read_text(encoding="utf-8"))
    _scrivi(radice, "research/src/motore.py", "# motore\n")
    _scrivi(radice, "docs/state.md", "stato\n")
    _scrivi(radice, "CLAUDE.md", "istruzioni\n")
    _commit(radice, f"C1 {MSG_CLAUDE}: istruzioni", ".")
    # il commit della scheda tocca anche un file di coordinamento (l'universo delle monete)
    # e crea la scheda di un'altra moneta; la scheda ha un campo che un commit dopo togliera'
    _scrivi(radice, "research/campagne/BTCUSDT/scheda_moneta.md", f"scheda BTCUSDT {CONTENUTO_VECCHIO}\n")
    _scrivi(radice, f"research/campagne/{ALTRA_MONETA}/scheda_moneta.md", "scheda\n")
    _scrivi(radice, "research/universo/monete_campagna.csv", f"{CONTENUTO_UNIVERSO}\n")
    _commit(radice, "C2 scheda BTCUSDT", ".")
    _scrivi(radice, "research/campagne/BTCUSDT/scheda_moneta.md", "scheda BTCUSDT\n")
    _commit(radice, "C2b scheda BTCUSDT ripulita", ".")
    # un commit del principale che CITA la cartella della campagna ma non la tocca
    _scrivi(radice, "research/PROTOCOLLO.md", "protocollo\n")
    _commit(radice, f"C3 {MSG_PRINCIPALE}: coordinamento, cita research/campagne/BTCUSDT/", ".")


def _costruisci_repo(radice: Path) -> dict:
    """Il repo di prova: main, archivio, campagna attiva. Restituisce gli hash che servono."""
    radice.mkdir(parents=True)
    _git(radice, "init", "-q", "-b", "main")
    _storia_principale(radice)
    vecchio = _git(radice, "rev-parse", "HEAD~2")  # C2: la scheda con il campo poi tolto
    # l'archivio: stesso percorso della campagna nuova
    _git(radice, "checkout", "-q", "-b", "research/archivio/campagna/BTCUSDT")
    _scrivi(radice, "research/campagne/BTCUSDT/log.jsonl", f"{CONTENUTO_ARCHIVIO}\n")
    _commit(radice, f"{MSG_ARCHIVIO}: archivio", ".")
    archivio = _git(radice, "rev-parse", "HEAD")
    # la campagna nuova, nata da main, con un commit suo
    _git(radice, "checkout", "-q", "main")
    _git(radice, "checkout", "-q", "-b", PROPRIO)
    _scrivi(radice, "research/campagne/BTCUSDT/ipotesi.md", "ipotesi nuove\n")
    _commit(radice, "campagna: ipotesi", ".")
    # come dopo un `git push -u`: il proprio branch esiste anche sul remoto
    _git(radice, "update-ref", f"refs/remotes/origin/{PROPRIO}", "HEAD")
    _scrivi(radice, "research/.sessione", json.dumps({"tipo": "campagna", "simbolo": "BTCUSDT"}))
    return {
        "archivio": archivio,
        "archivio_corto": archivio[:10],
        "padre": _git(radice, "rev-parse", "HEAD~1"),  # la punta di main, antenato di HEAD
        "vecchio": vecchio,  # antenato di HEAD anche lui, ma con la scheda vecchia
        "blob_vecchio": _git(radice, "rev-parse", f"{vecchio}:research/campagne/BTCUSDT/scheda_moneta.md"),
    }


def _costruisci_con_origine(base: Path) -> Path:
    """Un remoto nudo `origine.git` con main, l'archivio e il proprio branch, e una
    SESSIONE che apre il proprio branch come dice la sezione 9 del protocollo:
    scarica solo `main`, poi `git fetch origin <proprio>`, `checkout -b`, marcatore.
    Restituisce la radice della sessione (il remoto e' `base / "origine.git"`)."""
    base.mkdir(parents=True)
    _git(base, "init", "-q", "--bare", "-b", "main", "origine.git")
    coordinamento = base / "coordinamento"
    coordinamento.mkdir()
    _git(coordinamento, "init", "-q", "-b", "main")
    _storia_principale(coordinamento)
    _git(coordinamento, "remote", "add", "origin", str(base / "origine.git"))
    _git(coordinamento, "push", "-q", "origin", "main")
    _git(coordinamento, "checkout", "-q", "-b", "research/archivio/campagna/BTCUSDT")
    _scrivi(coordinamento, "research/campagne/BTCUSDT/log.jsonl", f"{CONTENUTO_ARCHIVIO}\n")
    _commit(coordinamento, f"{MSG_ARCHIVIO}: archivio", ".")
    _git(coordinamento, "push", "-q", "origin", "HEAD")
    _git(coordinamento, "checkout", "-q", "main")
    _git(coordinamento, "checkout", "-q", "-b", PROPRIO)
    _scrivi(coordinamento, "research/campagne/BTCUSDT/log.jsonl", '{"evento": "inizio"}\n')
    _commit(coordinamento, "campagna: inizio", ".")
    _git(coordinamento, "push", "-q", "origin", "HEAD")
    # la sessione di campagna: all'inizio ha solo main...
    sessione = base / "sessione"
    sessione.mkdir()
    _git(sessione, "init", "-q", "-b", "main")
    _git(sessione, "remote", "add", "origin", str(base / "origine.git"))
    _git(sessione, "fetch", "-q", "origin", "main")
    _git(sessione, "reset", "-q", "--hard", "origin/main")
    # ...poi apre il proprio branch (sezione 9), e solo dopo scrive il marcatore
    _git(sessione, "fetch", "-q", "origin", PROPRIO)
    _git(sessione, "checkout", "-q", "-b", PROPRIO, f"origin/{PROPRIO}")
    assert _git(sessione, "branch", "--show-current") == PROPRIO
    _scrivi(sessione, "research/.sessione", json.dumps({"tipo": "campagna", "simbolo": "BTCUSDT"}))
    return sessione


def _esegui(radice: Path, tool_name: str, tool_input):
    """Lancia il guardiano come hook; restituisce (exit code, stderr)."""
    ambiente = dict(os.environ)
    ambiente["CLAUDE_PROJECT_DIR"] = str(radice)
    carico = json.dumps({"tool_name": tool_name, "tool_input": tool_input, "cwd": str(radice)})
    esito = subprocess.run(
        [sys.executable, str(GUARDIANO)], input=carico, capture_output=True, text=True,
        env=ambiente, cwd=str(radice), timeout=20,
    )
    return esito.returncode, esito.stderr


def _bash(radice: Path, comando: str):
    return _esegui(radice, "Bash", {"command": comando})


def _bash_vero_esito(radice: Path, comando: str) -> tuple[int, str]:
    """Esegue DAVVERO il comando in bash nel repo di prova: (exit code, stdout+stderr)."""
    esito = subprocess.run(
        ["bash", "-c", comando], cwd=str(radice), env=_ambiente_git(radice.parent),
        capture_output=True, text=True, timeout=30,
    )
    return esito.returncode, esito.stdout + esito.stderr


def _bash_vero(radice: Path, comando: str) -> str:
    return _bash_vero_esito(radice, comando)[1]


def _rifiutato(radice: Path, comando: str) -> None:
    codice, errore = _bash(radice, comando)
    assert codice == 2, f"BUCO: il guardiano consente {comando!r}"
    assert errore.startswith(RIFIUTO), errore
    assert "sessione campagna BTCUSDT" in errore


class _Repo:
    def __init__(self, radice: Path, hash_: dict):
        self.radice = radice
        self.hash = hash_

    def comando(self, schema: str) -> str:
        """`{archivio}`, `{archivio_corto}`, `{padre}`, `{vecchio}`, `{blob_vecchio}` diventano gli hash veri."""
        return schema.format(**self.hash)


@pytest.fixture(scope="module")
def repo(tmp_path_factory) -> _Repo:
    radice = tmp_path_factory.mktemp("guardiano_4_4") / "repo"
    return _Repo(radice, _costruisci_repo(radice))


@pytest.fixture
def repo_nuovo(tmp_path: Path) -> _Repo:
    """Come `repo`, ma nuovo per ogni test: per i comandi che cambiano il disco."""
    radice = tmp_path / "repo"
    return _Repo(radice, _costruisci_repo(radice))


@pytest.fixture(scope="module")
def sessione_condivisa(tmp_path_factory) -> Path:
    """La sessione con il remoto, condivisa: solo per i giudizi del guardiano."""
    return _costruisci_con_origine(tmp_path_factory.mktemp("guardiano_origine") / "base")


@pytest.fixture
def sessione(tmp_path: Path) -> Path:
    """La sessione con il remoto, nuova per ogni test: per i comandi eseguiti davvero."""
    return _costruisci_con_origine(tmp_path / "base")


def _radice_semplice(tmp_path: Path, nome: str, marcatore) -> Path:
    """Una radice senza git, per gli strumenti: con il marcatore dato (None = nessuno)."""
    radice = tmp_path / nome
    (radice / "research" / "config").mkdir(parents=True)
    (radice / "research" / "campagne" / "BTCUSDT").mkdir(parents=True)
    shutil.copy(VIETATI_REPO, radice / "research" / "config" / "percorsi_vietati.txt")
    if marcatore is not None:
        (radice / "research" / ".sessione").write_text(json.dumps(marcatore))
    return radice


@pytest.fixture
def campagna(tmp_path: Path) -> Path:
    return _radice_semplice(tmp_path, "campagna", {"tipo": "campagna", "simbolo": "BTCUSDT"})


@pytest.fixture
def coordinamento(tmp_path: Path) -> Path:
    return _radice_semplice(tmp_path, "coordinamento", {"tipo": "coordinamento"})


@pytest.fixture
def senza_marcatore(tmp_path: Path) -> Path:
    return _radice_semplice(tmp_path, "senza_marcatore", None)


# ---------------------------------------------------------------------------
# il repo di prova e' quello che dice di essere
# ---------------------------------------------------------------------------


def test_il_repo_di_prova_ha_archivio_e_campagna(repo: _Repo):
    assert _git(repo.radice, "rev-parse", "--abbrev-ref", "HEAD") == PROPRIO
    assert not (repo.radice / "research/campagne/BTCUSDT/log.jsonl").exists()
    assert CONTENUTO_ARCHIVIO in _bash_vero(repo.radice, f"git show {repo.hash['archivio']}:research/campagne/BTCUSDT/log.jsonl")
    assert MSG_PRINCIPALE in _bash_vero(repo.radice, "git log")
    # la scheda di oggi non ha il campo; quella di un antenato di HEAD si'
    assert CONTENUTO_VECCHIO not in (repo.radice / "research/campagne/BTCUSDT/scheda_moneta.md").read_text()
    assert _git(repo.radice, "merge-base", "--is-ancestor", repo.hash["vecchio"], "HEAD") == ""


def test_la_sessione_con_il_remoto_e_quella_della_sezione_9(sessione_condivisa: Path):
    """Sul disco della sessione ci sono solo main e il proprio branch: l'archivio
    e' sul remoto, e un `git fetch` senza nome lo porterebbe giu'."""
    remoti = _git(sessione_condivisa, "branch", "-r")
    assert PROPRIO in remoti and "archivio" not in remoti
    assert "research/archivio/campagna/BTCUSDT" in _git(sessione_condivisa.parent / "origine.git", "branch")


# ---------------------------------------------------------------------------
# A. la storia: solo ristretta alla propria cartella
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "comando",
    [
        "git log -- research/campagne/BTCUSDT/",
        "git log --format=%cI -- research/campagne/BTCUSDT/log.jsonl",
        "git log -1 --stat -- research/campagne/BTCUSDT/",
        "git log --oneline origin/research/campagna/BTCUSDT -- research/campagne/BTCUSDT/",
        "git log --format=%B --name-status -- research/campagne/BTCUSDT/",
        "git log --numstat --shortstat --format=%H -- research/campagne/BTCUSDT/",
        "git log --oneline research/campagna/BTCUSDT -- research/campagne/BTCUSDT/",
        "git log --oneline {padre} -- research/campagne/BTCUSDT/",
        "git log --oneline {vecchio} -- research/campagne/BTCUSDT/",
        "git log --pretty=format:%s --name-only -- research/campagne/BTCUSDT/",
        "git shortlog HEAD -- research/campagne/BTCUSDT/",
        "git rev-list --format=%B HEAD -- research/campagne/BTCUSDT/",
        "git blame research/campagne/BTCUSDT/scheda_moneta.md",
        "git blame --porcelain -- research/campagne/BTCUSDT/scheda_moneta.md",
        "git blame HEAD -- research/campagne/BTCUSDT/scheda_moneta.md",
        "git annotate research/campagne/BTCUSDT/scheda_moneta.md",
    ],
)
def test_storia_della_propria_cartella_ammessa(repo: _Repo, comando: str):
    """Ammessa, e davvero innocua: l'uscita non contiene nulla di riservato."""
    comando = repo.comando(comando)
    uscita = _bash_vero(repo.radice, comando)
    assert "fatal" not in uscita, uscita
    for riservato in RISERVATI:
        assert riservato not in uscita, f"{comando!r} stampa {riservato}"
    codice, errore = _bash(repo.radice, comando)
    assert codice == 0, errore


@pytest.mark.parametrize(
    "comando, riservato",
    [
        ("git log", MSG_PRINCIPALE),
        ("git log --oneline -20", MSG_PRINCIPALE),
        ("git log -5 --format=%B", MSG_PRINCIPALE),
        ("git log -- CLAUDE.md", MSG_CLAUDE),
        ("git log -- research/PROTOCOLLO.md", MSG_PRINCIPALE),
        ("git log -- research/campagne/BTCUSDT/ CLAUDE.md", MSG_CLAUDE),
        ("git log -- research/campagne/BTCUSDT/ research/PROTOCOLLO.md", MSG_PRINCIPALE),
        ("git shortlog HEAD", MSG_PRINCIPALE),
        ("git blame --porcelain research/PROTOCOLLO.md", MSG_PRINCIPALE),
        ("git blame --porcelain CLAUDE.md", MSG_CLAUDE),
        ("git annotate --porcelain CLAUDE.md", MSG_CLAUDE),
        ("git rev-list --format=%B HEAD", MSG_PRINCIPALE),
        ("git rev-list --format=%B HEAD -- CLAUDE.md", MSG_CLAUDE),
        ("git format-patch --stdout -1 HEAD~1", MSG_PRINCIPALE),
        ("git log --stat -- research/", MSG_PRINCIPALE),
        # opzioni che scavalcano il filtro sul percorso
        ("git log --sparse --format=%B -- research/campagne/BTCUSDT/", MSG_PRINCIPALE),
        ("git log --boundary -1 --format=%B -- research/campagne/BTCUSDT/", MSG_PRINCIPALE),
        ("git log --simplify-by-decoration --format=%B -- research/campagne/BTCUSDT/", MSG_PRINCIPALE),
        ("git log -p --full-diff -- research/campagne/BTCUSDT/", CONTENUTO_UNIVERSO),
        ("git rev-list --sparse --format=%B HEAD -- research/campagne/BTCUSDT/", MSG_PRINCIPALE),
        # un'opzione con valore ingoia il percorso: git resta senza filtro
        ("git log --grep research/campagne/BTCUSDT/", MSG_PRINCIPALE),
        # i riferimenti presi da stdin non si vedono
        ("echo {archivio} | git log --stdin --format=%B -- research/campagne/BTCUSDT/", MSG_ARCHIVIO),
    ],
)
def test_storia_fuori_dalla_propria_cartella_rifiutata(repo: _Repo, comando: str, riservato: str):
    comando = repo.comando(comando)
    assert riservato in _bash_vero(repo.radice, comando), "il comando non stampa il riservato: non e' un buco"
    _rifiutato(repo.radice, comando)


@pytest.mark.parametrize(
    "comando",
    [
        "git log research/campagne/BTCUSDT/",  # percorso senza `--`: potrebbe essere ingoiato
        # `whatchanged` qui senza la prova in bash: le versioni nuove di git lo stanno togliendo
        "git whatchanged",
        "git whatchanged -2 --format=%B",
        "git whatchanged -- CLAUDE.md",
        "git shortlog",
        "git blame CLAUDE.md",
        "git rev-list HEAD",
        "git cherry",
        "git cherry -v HEAD~1",
        "git format-patch -1 -- research/campagne/BTCUSDT/",  # scriverebbe le patch nella radice
        "git log --follow -- research/campagne/BTCUSDT/scheda_moneta.md",
        # con git 2.55 (server di GitHub) stampa il messaggio di HEAD~1 anche se non tocca la cartella
        "git log --no-walk --format=%B HEAD~1 -- research/campagne/BTCUSDT/",
        "git log --no-walk=unsorted HEAD~1 -- research/campagne/BTCUSDT/",
        "git rev-list --no-walk --format=%B HEAD~1 -- research/campagne/BTCUSDT/",
        "git log HEAD~1..HEAD -- research/campagne/BTCUSDT/",
        "git log HEAD@{{1}} -- research/campagne/BTCUSDT/",
        "git log -L1,1:CLAUDE.md",
        "git log HEAD:research/campagne/BTCUSDT/ -- research/campagne/BTCUSDT/",
        "git blame -C -C -C research/campagne/BTCUSDT/scheda_moneta.md",
        "git blame -S research/campagne/BTCUSDT/rev.txt research/campagne/BTCUSDT/scheda_moneta.md",
    ],
)
def test_storia_altri_rifiuti(repo: _Repo, comando: str):
    _rifiutato(repo.radice, repo.comando(comando))


# ---------------------------------------------------------------------------
# B. git show: solo `<rif>:<percorso>`
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "comando",
    [
        "git show HEAD:research/campagne/BTCUSDT/ipotesi.md",
        "git show HEAD:research/campagne/BTCUSDT/scheda_moneta.md",
        "git show HEAD:research/src/motore.py",
        "git show origin/research/campagna/BTCUSDT:research/campagne/BTCUSDT/ipotesi.md",
        "git show research/campagna/BTCUSDT:research/campagne/BTCUSDT/ipotesi.md",
    ],
)
def test_show_rif_percorso_ammesso(repo: _Repo, comando: str):
    comando = repo.comando(comando)
    uscita = _bash_vero(repo.radice, comando)
    assert "fatal" not in uscita, uscita
    for riservato in RISERVATI:
        assert riservato not in uscita
    codice, errore = _bash(repo.radice, comando)
    assert codice == 0, errore


@pytest.mark.parametrize(
    "comando, riservato",
    [
        ("git show", "campagna: ipotesi"),
        ("git show HEAD~1", MSG_PRINCIPALE),
        ("git show -s HEAD~1", MSG_PRINCIPALE),
        ("git show -s --format=%B {padre}", MSG_PRINCIPALE),
        ("git show --stat HEAD~2", "C2b scheda"),
    ],
)
def test_show_che_stampa_il_messaggio_rifiutato(repo: _Repo, comando: str, riservato: str):
    comando = repo.comando(comando)
    assert riservato in _bash_vero(repo.radice, comando)
    _rifiutato(repo.radice, comando)


@pytest.mark.parametrize(
    "comando",
    [
        "git show HEAD",
        # con un percorso git 2.43 stampa il messaggio solo dei commit che lo toccano;
        # la regola resta semplice: in campagna `git show` e' solo `<rif>:<percorso>`
        "git show --stat HEAD -- research/campagne/BTCUSDT/",
        "git show --stat HEAD~1 -- research/campagne/BTCUSDT/",
        "git show HEAD~2 -- research/campagne/BTCUSDT/",
        "git show HEAD:research/campagne/BTCUSDT/ipotesi.md HEAD",
        "git show HEAD:research/campagne/BTCUSDT/ipotesi.md -- research/campagne/BTCUSDT/",
        "git show HEAD:docs/state.md",
        "git show HEAD:research/campagne/ETHUSDT/log.jsonl",
        "git show HEAD:",
        "git show :research/campagne/BTCUSDT/ipotesi.md",
        "git show HEAD@{{1}}:research/campagne/BTCUSDT/ipotesi.md",
        "git show HEAD^{{tree}}:research/campagne/BTCUSDT/ipotesi.md",
    ],
)
def test_show_altri_rifiuti(repo: _Repo, comando: str):
    assert _bash(repo.radice, repo.comando(comando))[0] == 2


# ---------------------------------------------------------------------------
# C e D. riferimenti: hash solo se antenati di HEAD, niente nomi di branch
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "comando, riservato",
    [
        ("git show {archivio}:research/campagne/BTCUSDT/log.jsonl", CONTENUTO_ARCHIVIO),
        ("git show {archivio_corto}:research/campagne/BTCUSDT/log.jsonl", CONTENUTO_ARCHIVIO),
        ("git log {archivio} -- research/campagne/BTCUSDT/", MSG_ARCHIVIO),
        ("git log --format=%B {archivio_corto}~0 -- research/campagne/BTCUSDT/", MSG_ARCHIVIO),
        ("git diff {archivio} -- research/campagne/BTCUSDT/", CONTENUTO_ARCHIVIO),
        ("git diff HEAD {archivio} -- research/campagne/BTCUSDT/log.jsonl", CONTENUTO_ARCHIVIO),
        ("git grep {riservato} {archivio} -- research/campagne/BTCUSDT/", CONTENUTO_ARCHIVIO),
        ("git ls-tree -r {archivio} -- research/campagne/BTCUSDT/", "log.jsonl"),
    ],
)
def test_hash_dell_archivio_rifiutato(repo: _Repo, comando: str, riservato: str):
    """L'hash dell'archivio poteva arrivare da `git fetch`: non e' un antenato di HEAD."""
    comando = comando.format(riservato=CONTENUTO_ARCHIVIO, **repo.hash)
    assert riservato in _bash_vero(repo.radice, comando)
    _rifiutato(repo.radice, comando)


@pytest.mark.parametrize(
    "comando",
    [
        # dove git stampa solo nomi, hash e messaggi della propria cartella, un antenato di HEAD
        # resta ammesso; dove stampa contenuti no (sezione «C» della seconda revisione)
        "git ls-tree {padre} -- research/campagne/BTCUSDT/",
        "git ls-tree HEAD~3 -- research/campagne/BTCUSDT/",
        "git ls-tree --name-only {vecchio}:research/campagne/BTCUSDT",
        "git rev-parse {padre}",
        "git rev-parse HEAD~3",
        "git merge-base HEAD {vecchio}",
    ],
)
def test_hash_antenato_di_head_ammesso(repo: _Repo, comando: str):
    comando = repo.comando(comando)
    uscita = _bash_vero(repo.radice, comando)
    assert "fatal" not in uscita, uscita
    for riservato in RISERVATI:
        assert riservato not in uscita
    codice, errore = _bash(repo.radice, comando)
    assert codice == 0, errore


def test_hash_senza_repo_git_rifiutato(campagna: Path):
    """Fuori da un repo git (o se git non risponde) nessun hash e' proprio: nel dubbio si blocca."""
    assert _bash(campagna, "git show abcdef1234:research/campagne/BTCUSDT/log.jsonl")[0] == 2
    assert _bash(campagna, "git log abcdef1234 -- research/campagne/BTCUSDT/")[0] == 2


@pytest.mark.parametrize(
    "comando",
    [
        "git show-branch -r",
        "git show-branch",
        "git name-rev HEAD",
        "git describe --all",
        "git describe",
        "git diff-tree --always --pretty=%B HEAD~1 -- research/campagne/BTCUSDT/",
        "git range-diff HEAD~1 HEAD~1 HEAD",
    ],
)
def test_comandi_che_stampano_nomi_o_messaggi_vietati(repo: _Repo, comando: str):
    _rifiutato(repo.radice, comando)


# ---------------------------------------------------------------------------
# buchi vicini trovati durante la revisione: scritture e programmi nascosti in git
# ---------------------------------------------------------------------------


def test_git_output_non_puo_svuotare_il_marcatore(tmp_path: Path):
    """`git diff --output=research/.sessione` con un'uscita vuota svuota il
    marcatore: un marcatore vuoto vale come assente, e il guardiano si spegne."""
    radice = tmp_path / "repo"
    hash_ = _costruisci_repo(radice)
    comando = "git diff --output=research/.sessione HEAD -- research/campagne/BTCUSDT/nessuno"
    codice, errore = _bash(radice, comando)
    assert codice == 2, "BUCO: --output riscrive il marcatore"
    # la prova che il trucco funziona davvero: dopo, il guardiano non interviene piu'
    _bash_vero(radice, comando)
    assert (radice / "research" / ".sessione").read_text() == ""
    assert _bash(radice, f"git show {hash_['archivio']}:research/campagne/BTCUSDT/log.jsonl")[0] == 0


@pytest.mark.parametrize(
    "comando, atteso",
    [
        ("git diff --output=.claude/settings.json HEAD -- research/campagne/BTCUSDT/", 2),
        ("git log --output=research/src/guardiano.py -- research/campagne/BTCUSDT/", 2),
        ("git diff --output docs/x.txt HEAD -- research/campagne/BTCUSDT/", 2),
        ("git diff-files --output=research/.sessione", 2),
        ("git diff --output=research/campagne/BTCUSDT/diff.txt HEAD -- research/campagne/BTCUSDT/", 0),
        # dal 7 ott 2026 `format-patch` e' vietato del tutto: stampa il contenuto dei commit
        ("git format-patch -o research/campagne/BTCUSDT/patch -1 -- research/campagne/BTCUSDT/", 2),
        ("git format-patch -o .claude -1 -- research/campagne/BTCUSDT/", 2),
    ],
)
def test_git_scritture_nascoste_nelle_opzioni(repo: _Repo, comando: str, atteso: int):
    codice, errore = _bash(repo.radice, comando)
    assert codice == atteso, errore


@pytest.mark.parametrize(
    "comando",
    [
        "git grep -O'cd docs; cat state.md' stato -- research/src",
        "git grep --open-files-in-pager=less stato -- research/src",
        "git difftool -y -x 'cd docs; cat state.md' HEAD~1",
        "git mergetool",
        "git submodule foreach 'cd ../docs; cat state.md'",
        "git var -l",
        "git checkout-index -a --prefix=research/campagne/BTCUSDT/copia/",
        "git --work-tree=research/campagne/BTCUSDT/copia reset --hard",
        "git --git-dir=research/campagne/BTCUSDT/altro.git log -- research/campagne/BTCUSDT/",
        "git fetch --stdin origin",
        # i comandi su parse-options accettano le opzioni abbreviate
        "git grep --open='cd docs; cat state.md' stato -- research/src",
        "git fetch --stdi origin",
        "git branch --al",
        "git branch --remo",
        "git restore --pathspec-from=research/campagne/BTCUSDT/elenco",
        # il riferimento attaccato a un'opzione si controlla come gli altri
        "git restore -s{archivio} -- research/campagne/BTCUSDT/log.jsonl",
        "git restore --source={archivio} -- research/campagne/BTCUSDT/log.jsonl",
        "git restore --sour={archivio} -- research/campagne/BTCUSDT/log.jsonl",
        "git restore -s {archivio} -- research/campagne/BTCUSDT/log.jsonl",
        "git reset {archivio} -- research/campagne/BTCUSDT/log.jsonl",
        "git cherry-pick -n {archivio}",
    ],
)
def test_git_che_esegue_o_copia_rifiutato(repo: _Repo, comando: str):
    comando = repo.comando(comando)
    codice, errore = _bash(repo.radice, comando)
    assert codice == 2, f"BUCO: il guardiano consente {comando!r}"


def test_restore_dall_archivio_porta_il_file_sul_disco(tmp_path: Path):
    """La prova che `git restore -s<hash>` rimette sul disco, in una cartella
    ammessa, il file dell'archivio."""
    radice = tmp_path / "repo"
    hash_ = _costruisci_repo(radice)
    _bash_vero(radice, f"git restore -s{hash_['archivio']} -- research/campagne/BTCUSDT/log.jsonl")
    assert CONTENUTO_ARCHIVIO in (radice / "research/campagne/BTCUSDT/log.jsonl").read_text()


@pytest.mark.parametrize(
    "comando",
    [
        "git restore -s HEAD -- research/campagne/BTCUSDT/ipotesi.md",
        "git restore -sHEAD -- research/campagne/BTCUSDT/ipotesi.md",
        "git restore --source=origin/research/campagna/BTCUSDT -- research/campagne/BTCUSDT/scheda_moneta.md",
        "git branch",
        "git branch --show-current",
        "git ls-files --exclude-standard -- research/campagne/BTCUSDT/",
    ],
)
def test_git_con_riferimento_proprio_attaccato_ammesso(repo: _Repo, comando: str):
    codice, errore = _bash(repo.radice, repo.comando(comando))
    assert codice == 0, errore


def test_git_grep_o_esegue_davvero(repo: _Repo):
    """La prova che `git grep -O` esegue un programma (qui `echo`) scelto da chi chiama."""
    assert "ESEGUITO" in _bash_vero(repo.radice, "git grep -O'echo ESEGUITO' scheda -- research/campagne/BTCUSDT")


@pytest.mark.parametrize(
    "comando",
    ["git status",
     # dal 7 ott 2026 `git fetch` e `git pull` vogliono il nome del proprio branch: senza,
     # scaricano tutti i branch e ne stampano i nomi, archivi compresi (seconda revisione, B)
     "git fetch origin research/campagna/BTCUSDT", "git pull origin research/campagna/BTCUSDT",
     "git push origin research/campagna/BTCUSDT",
     "git add research/campagne/BTCUSDT/ipotesi.md && git commit -m 'campagna: ipotesi'",
     "git diff research/src/motore.py", "git diff --cached -- research/campagne/BTCUSDT/",
     "git diff HEAD -- research/campagne/BTCUSDT/",
     "git grep scheda -- research/campagne/BTCUSDT/",
     "git whatchanged --format=%B -- research/campagne/BTCUSDT/"],
)
def test_git_di_tutti_i_giorni_resta_ammesso(repo: _Repo, comando: str):
    codice, errore = _bash(repo.radice, comando)
    assert codice == 0, errore


# ---------------------------------------------------------------------------
# E. gli altri strumenti: lista bianca in campagna
# ---------------------------------------------------------------------------

STRUMENTI_VIETATI = [
    ("mcp__github__get_file_contents",
     {"owner": "x", "repo": "y", "path": "research/campagne/BTCUSDT/log.jsonl", "ref": "research/archivio/campagna/BTCUSDT"}),
    ("mcp__github__list_branches", {"owner": "x", "repo": "y"}),
    ("mcp__github__list_commits", {"owner": "x", "repo": "y"}),
    ("mcp__github__get_commit", {"owner": "x", "repo": "y", "sha": "abc"}),
    ("mcp__github__search_code", {"query": "research/campagne/BTCUSDT"}),
    ("mcp__claude-code-remote__list_triggers", {}),
    ("mcp__Claude_Code_Remote__list_sessions", {}),
    ("mcp__Claude_Code_Remote__get_trigger", {"trigger_id": "trig_x"}),
    ("Artifact", {"action": "list"}),
    ("ArtifactComments", {}),
    ("ArtifactData", {}),
    ("Monitor", {"command": "cat docs/state.md"}),
    ("strumento_sconosciuto", {}),
]


@pytest.mark.parametrize("tool_name, tool_input", STRUMENTI_VIETATI)
def test_campagna_strumenti_fuori_lista_rifiutati(campagna: Path, tool_name: str, tool_input: dict):
    codice, errore = _esegui(campagna, tool_name, tool_input)
    assert codice == 2, f"BUCO: {tool_name} consentito in campagna"
    assert errore.startswith(RIFIUTO)
    assert tool_name in errore
    assert errore.count("\n") <= 1


@pytest.mark.parametrize("tool_name, tool_input", STRUMENTI_VIETATI + [
    ("WebFetch", {"url": "https://raw.githubusercontent.com/x/y/z", "prompt": "p"}),
    ("WebFetch", {"url": "https://cdn.jsdelivr.net/gh/x/y@research/archivio/campagna/BTCUSDT/z", "prompt": "p"}),
    ("WebSearch", {"query": "github agentic_trading_system research/archivio/campagna"}),
    ("WebSearch", {"query": "momentum", "allowed_domains": ["github.com"]}),
])
def test_coordinamento_e_senza_marcatore_strumenti_non_toccati(coordinamento: Path, senza_marcatore: Path,
                                                               tool_name: str, tool_input: dict):
    assert _esegui(coordinamento, tool_name, tool_input) == (0, "")
    assert _esegui(senza_marcatore, tool_name, tool_input) == (0, "")


@pytest.mark.parametrize(
    "tool_name, tool_input",
    [
        ("WebSearch", {"query": "momentum crypto paper"}),
        ("TaskCreate", {"subject": "x"}),
        ("TaskUpdate", {"taskId": "1"}),
        ("ToolSearch", {"query": "select:WebFetch"}),
        ("TodoWrite", {"todos": []}),
        ("Agent", {"prompt": "x"}),
        ("Task", {"prompt": "x"}),
        ("AskUserQuestion", {"questions": []}),
        ("BashOutput", {"bash_id": "1"}),
        ("KillShell", {"shell_id": "1"}),
        ("ExitPlanMode", {}),
        ("Skill", {"skill": "x"}),
    ],
)
def test_campagna_strumenti_in_lista_ammessi(campagna: Path, tool_name: str, tool_input: dict):
    codice, errore = _esegui(campagna, tool_name, tool_input)
    assert codice == 0, errore


@pytest.mark.parametrize(
    "url",
    [
        "https://raw.githubusercontent.com/x/y/z",
        "https://github.com/x",
        "https://api.github.com/repos",
        "https://codeload.github.com/x/y/zip/refs/heads/research/archivio/campagna/BTCUSDT",
        "https://gist.github.com/x",
        "https://objects.githubusercontent.com/x",
        "https://x.github.io/y",
        "https://github.githubassets.com/x",
        "https://claude.ai/code/artifact/x",
        "https://docs.anthropic.com/x",
        "https://anthropic.com/",
        "https://GitHub.COM./x",
        "https://git%68ub.com/x",
        "https://user:pw@github.com/x",
        "https://github.com:443/x",
        "https://github.com\\@example.com/",
        "https://example.com\\@github.com/",
        "https://ｇｉｔｈｕｂ.com/x",
        "http://140.82.112.3/x",
        "http://2354212867/x",
        "http://[::1]/x",
        "http://localhost:8000/x",
        "file:///etc/passwd",
        "ftp://example.com/x",
        "https:///x",
        "non e' un indirizzo",
        "",
        "https://cdn.jsdelivr.net/gh/x/y@research/archivio/campagna/BTCUSDT/research/campagne/BTCUSDT/log.jsonl",
        "https://cdn.jsdelivr.net/gh/x/y@research%2Farchivio%2Fcampagna%2FBTCUSDT/log.jsonl",
        # dal 7 ott 2026 WebFetch apre solo i siti di una lista BIANCA (seconda revisione, D):
        # questi una volta passavano
        "http://www.example.com/path/github.com",
        "https://data.binance.vision/?prefix=data/futures/um/",
        "https://notgithub.com/x",
        "https://github.com.example.org/x",
    ],
)
def test_campagna_webfetch_rifiutato(campagna: Path, url: str):
    codice, errore = _esegui(campagna, "WebFetch", {"url": url, "prompt": "leggi"})
    assert codice == 2, f"BUCO: WebFetch {url!r} consentito in campagna"
    assert errore.startswith(RIFIUTO)


def test_campagna_webfetch_senza_url_rifiutato(campagna: Path):
    assert _esegui(campagna, "WebFetch", {"prompt": "leggi"})[0] == 2


@pytest.mark.parametrize(
    "url",
    [
        "https://arxiv.org/abs/1234",
        "https://arxiv.org/abs/1234.5678",
        "https://arxiv.org/abs/1234?x=github.com",
        "https://export.arxiv.org/api/query?search_query=all:momentum%20crypto",
        "https://en.wikipedia.org/wiki/Momentum_(finance)",
        "https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2089463",
        "https://doi.org/10.1016/j.jfineco.2011.11.003",
        "https://www.nber.org/papers/w14929",
        "https://www.jstor.org/stable/2328882",
        "https://www.sciencedirect.com/science/article/pii/S0304405X11002613",
        "https://link.springer.com/article/10.1007/x",
        "https://onlinelibrary.wiley.com/doi/10.1111/jofi.12365",
        "https://www.tandfonline.com/doi/full/10.1080/x",
        "https://academic.oup.com/rfs/article/x",
        "https://www.cambridge.org/core/journals/x",
        "https://api.semanticscholar.org/graph/v1/paper/search?query=momentum",
        "https://www.researchgate.net/publication/x",
        "https://ideas.repec.org/p/x.html",
        "http://arxiv.org:443/abs/1234",
    ],
)
def test_campagna_webfetch_ammesso(campagna: Path, url: str):
    codice, errore = _esegui(campagna, "WebFetch", {"url": url, "prompt": "leggi"})
    assert codice == 0, errore


# ---------------------------------------------------------------------------
# F. registrazione: il guardiano vede TUTTI gli strumenti
# ---------------------------------------------------------------------------


def _matcher_copre(matcher: str, strumento: str) -> bool:
    """Come Claude Code legge il matcher: `*` o vuoto = tutto, altrimenti un'espressione regolare."""
    return matcher in ("*", "") or re.fullmatch(matcher, strumento) is not None


def test_settings_registra_il_guardiano_per_tutti_gli_strumenti():
    settings = json.loads((RADICE_REPO / ".claude" / "settings.json").read_text(encoding="utf-8"))
    voci = [v for v in settings["hooks"]["PreToolUse"] if "guardiano.py" in json.dumps(v)]
    assert len(voci) == 1
    matcher = voci[0].get("matcher", "")
    assert matcher in ("*", ""), f"il guardiano non vede tutti gli strumenti: matcher {matcher!r}"
    for strumento in ("WebFetch", "WebSearch", "mcp__github__list_branches", "mcp__github__get_file_contents",
                      "mcp__Claude_Code_Remote__list_sessions", "Artifact", "Read", "Bash"):
        assert _matcher_copre(matcher, strumento), strumento
    # il vecchio matcher non li copriva: e' il buco che questo test chiude
    vecchio = "Read|Write|Edit|MultiEdit|NotebookEdit|Glob|Grep|Bash"
    assert not _matcher_copre(vecchio, "WebFetch")
    assert not _matcher_copre(vecchio, "mcp__github__list_branches")


def test_senza_marcatore_nessuna_domanda_a_git(senza_marcatore: Path, monkeypatch):
    """Ora che il guardiano gira per ogni strumento, senza marcatore deve restare
    muto e veloce: nemmeno un hash, un commit o un push fanno partire git."""
    from research.src import guardiano as g

    chiamate = []
    monkeypatch.setattr(g.subprocess, "run", lambda *a, **k: chiamate.append(a) or None)
    monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(senza_marcatore))
    for comando in ("git show abcdef1234:x", "git commit -m x && git push origin HEAD"):
        carico = json.dumps({"tool_name": "Bash", "tool_input": {"command": comando},
                             "cwd": str(senza_marcatore)})
        monkeypatch.setattr(g.sys, "stdin", __import__("io").StringIO(carico))
        assert g.main() == 0
    assert chiamate == []


# ===========================================================================
# seconda revisione (7 ottobre 2026): due revisioni avversarie e una prova d'attacco
# ===========================================================================

# ---------------------------------------------------------------------------
# A. commit, push, pull, reset, stash solo con HEAD sul proprio branch
# ---------------------------------------------------------------------------

_SCRIVE_SUL_BRANCH = [
    "git commit -F research/data/insample/BTCUSDT/msg.txt",
    "git commit -m 'campagna: log'",
    "git add research/campagne/BTCUSDT/log.jsonl && git commit -m x",
    "git push",
    "git push origin",
    "git push origin HEAD",
    "git push -u origin research/campagna/BTCUSDT",
    "git pull origin research/campagna/BTCUSDT",
    "git pull --ff-only origin research/campagna/BTCUSDT",
    # dal 10 ott 2026 `reset` e `stash` solo con -q: senza, stampano l'oggetto del commit
    # HEAD («HEAD is now at <hash> <oggetto>», «WIP on <branch>: <hash> <oggetto>»), che
    # subito dopo l'apertura del branch e' un commit del branch principale (il coordinamento
    # o il bot). `git stash list` lo stampa anche con -q, ed e' vietato. Le forme senza -q
    # sono in test_reset_e_stash_senza_q_stampano_l_oggetto_di_head, qui sotto.
    "git reset -q --hard",
    "git reset -q -- research/campagne/BTCUSDT/log.jsonl",
    "git stash -q",
    "git stash pop -q",
]


def test_commit_e_push_dal_branch_principale_finiscono_sul_principale(sessione: Path):
    """Il buco: marcatore scritto con HEAD sul branch principale. `git commit` e
    `git push origin HEAD` passavano, e il commit finiva sul principale del remoto."""
    _git(sessione, "checkout", "-q", "main")
    _scrivi(sessione, "research/data/insample/BTCUSDT/msg.txt", "SUL_PRINCIPALE\n")
    _scrivi(sessione, "research/campagne/BTCUSDT/log.jsonl", '{"evento": "x"}\n')
    for comando in _SCRIVE_SUL_BRANCH:
        codice, errore = _bash(sessione, comando)
        assert codice == 2, f"BUCO: con HEAD su main il guardiano consente {comando!r}"
        assert "proprio branch" in errore
    # la prova: eseguiti davvero, commit e push finiscono sul principale del remoto
    codice, uscita = _bash_vero_esito(
        sessione, "git add research/campagne/BTCUSDT/log.jsonl && "
                  "git commit -q -F research/data/insample/BTCUSDT/msg.txt && git push -q origin HEAD")
    assert codice == 0, uscita
    assert _git(sessione.parent / "origine.git", "log", "-1", "--format=%s", "main") == "SUL_PRINCIPALE"


def test_head_staccato_rifiutato(sessione: Path):
    _git(sessione, "checkout", "-q", "--detach")
    for comando in ("git commit -m x", "git push origin HEAD", "git pull origin research/campagna/BTCUSDT"):
        assert _bash(sessione, comando)[0] == 2, comando


def test_sul_proprio_branch_commit_e_push_ammessi(sessione_condivisa: Path):
    for comando in _SCRIVE_SUL_BRANCH:
        codice, errore = _bash(sessione_condivisa, comando)
        assert codice == 0, f"{comando!r}: {errore}"


_RESET_E_STASH_SENZA_Q = [
    "git reset --hard",
    "git reset --hard HEAD",
    "git reset -- research/campagne/BTCUSDT/log.jsonl",
    "git reset",
    "git stash",
    "git stash push",
    "git stash push -m nota -- research/campagne/BTCUSDT/",
    "git stash save nota",
    "git stash pop",
    "git stash apply",
    "git stash drop",
    "git stash list",
    "git stash list -q",
    "git stash list --quiet",
]


def test_reset_e_stash_senza_q_stampano_l_oggetto_di_head(sessione: Path):
    """Il buco (revisione del 10 ottobre 2026): subito dopo l'apertura del branch, se il
    remoto non aveva ancora il proprio branch, HEAD e' l'ultimo commit del branch
    principale. Qui lo si rifa' portando il proprio branch sulla punta di main (senza
    marcatore, come fa la sezione 9): `git reset --hard` e `git stash` ne stampano
    l'oggetto, che e' un messaggio del coordinamento; `git stash list` lo stampa anche
    con -q. Le forme con -q non stampano nulla, e il guardiano ammette solo quelle."""
    marcatore = (sessione / "research" / ".sessione").read_text()
    (sessione / "research" / ".sessione").unlink()
    _git(sessione, "reset", "-q", "--hard", "origin/main")
    (sessione / "research" / ".sessione").write_text(marcatore)
    assert _git(sessione, "branch", "--show-current") == PROPRIO
    assert MSG_PRINCIPALE in _git(sessione, "log", "-1", "--format=%s")
    # la prova: senza -q l'oggetto di HEAD (del principale) finisce sullo schermo
    assert MSG_PRINCIPALE in _bash_vero(sessione, "git reset --hard")
    _scrivi(sessione, "research/src/motore.py", "# motore cambiato\n")
    assert MSG_PRINCIPALE in _bash_vero(sessione, "git stash")
    assert MSG_PRINCIPALE in _bash_vero(sessione, "git stash list -q")
    _git(sessione, "stash", "drop", "-q")
    # il guardiano rifiuta le forme senza -q, e dice quella giusta senza chiedere all'utente
    for comando in _RESET_E_STASH_SENZA_Q:
        codice, errore = _bash(sessione, comando)
        assert codice == 2, f"BUCO: il guardiano consente {comando!r}"
        assert errore.startswith(RIFIUTO), errore
        if "list" not in comando:
            assert "aggiungi -q (o --quiet)" in errore and "non serve chiedere all'utente" in errore, errore
    # ...e ammette quelle con -q, che eseguite davvero non stampano nulla di riservato
    _scrivi(sessione, "research/src/motore.py", "# motore cambiato\n")
    for comando in ("git stash -q", "git stash pop -q", "git stash push -q -m 'prima di provare'",
                    "git stash apply --quiet", "git stash drop -q", "git reset -q --hard",
                    "git reset --quiet -- research/campagne/BTCUSDT/log.jsonl", "git stash show",
                    "git stash clear"):
        codice, errore = _bash(sessione, comando)
        assert codice == 0, f"{comando!r}: {errore}"
        uscita = _bash_vero(sessione, comando)
        for riservato in (MSG_PRINCIPALE, MSG_CLAUDE, MSG_ARCHIVIO, "C2", "C3"):
            assert riservato not in uscita, f"{comando!r} stampa {riservato}: {uscita}"


@pytest.mark.parametrize(
    "comando",
    [
        "git push origin HEAD:research/campagna/BTCUSDT",
        "git push origin HEAD:refs/heads/research/campagna/BTCUSDT",
        "git push origin refs/heads/research/campagna/BTCUSDT",
        "git push origin research/campagna/BTCUSDT:research/campagna/BTCUSDT",
        "git push --set-upstream origin research/campagna/BTCUSDT",
        "git push -uq origin research/campagna/BTCUSDT",
        "git push --dry-run origin HEAD",
        "GIT_TERMINAL_PROMPT=0 git push origin research/campagna/BTCUSDT",
    ],
)
def test_push_verso_il_proprio_branch_ammesso(sessione_condivisa: Path, comando: str):
    codice, errore = _bash(sessione_condivisa, comando)
    assert codice == 0, errore


@pytest.mark.parametrize(
    "comando",
    [
        "git push origin main",
        "git push origin HEAD:main",
        "git push origin HEAD:refs/heads/main",
        "git push origin research/campagna/BTCUSDT:main",
        "git push origin HEAD:refs/heads/altro",
        "git push origin research/campagna/BTCUSDT research/campagna/BTCUSDT:main",
        "git push --all origin",
        "git push --mirror origin",
        "git push --tags origin",
        "git push --follow-tags origin research/campagna/BTCUSDT",
        "git push origin --delete research/campagna/BTCUSDT",
        "git push -d origin research/campagna/BTCUSDT",
        "git push origin :research/campagna/BTCUSDT",
        "git push -f origin research/campagna/BTCUSDT",
        "git push -uf origin research/campagna/BTCUSDT",
        "git push --force origin research/campagna/BTCUSDT",
        "git push --force-with-lease origin research/campagna/BTCUSDT",
        "git push origin +research/campagna/BTCUSDT",
        "git push origin +HEAD:research/campagna/BTCUSDT",
        "git push --prune origin research/campagna/BTCUSDT",
        "git push --receive-pack='cat docs/state.md' origin research/campagna/BTCUSDT",
        "git push --exec=x origin research/campagna/BTCUSDT",
        "git push --repo=altro research/campagna/BTCUSDT",
        "git push ../origine.git research/campagna/BTCUSDT",
        "git push https://example.com/x.git research/campagna/BTCUSDT",
        "git push origin research/campagna/BTCUSDT:research/campagna/ETHUSDT",
    ],
)
def test_push_fuori_dal_proprio_branch_rifiutato(sessione_condivisa: Path, comando: str):
    _rifiutato(sessione_condivisa, comando)


@pytest.mark.parametrize(
    "comando",
    [
        "git commit -C HEAD~1 -m x",
        "git commit -CHEAD~1",
        "git commit -c HEAD~1",
        "git commit -aC HEAD~1",
        "git commit --reuse-message=HEAD~1",
        "git commit --reuse-message HEAD~1",
        "git commit --reedit-message=HEAD~1",
        "git commit --fixup=HEAD~1",
        "git commit --fixup HEAD~1",
        "git commit --squash=HEAD~1",
        "git commit --amend",
        "git commit --amend --no-edit",
    ],
)
def test_commit_che_copia_un_messaggio_rifiutato(sessione_condivisa: Path, comando: str):
    _rifiutato(sessione_condivisa, comando)


def test_commit_che_copia_un_messaggio_lo_mette_nella_propria_storia(repo_nuovo: _Repo):
    """La prova: `git commit -C <commit del principale>` porta il suo messaggio
    nella storia della propria cartella, che `git log --format=%B` stampa."""
    radice = repo_nuovo.radice
    _scrivi(radice, "research/campagne/BTCUSDT/nota.md", "nota\n")
    _bash_vero(radice, "git add research/campagne/BTCUSDT/nota.md && git commit -q -C HEAD~1")
    assert MSG_PRINCIPALE in _bash_vero(radice, "git log -1 --format=%B -- research/campagne/BTCUSDT/")


@pytest.mark.parametrize(
    "comando",
    [
        "git commit --amend -m 'campagna: log'",
        "git commit --amend -F research/data/insample/BTCUSDT/msg.txt",
        "git commit -am 'campagna: log'",
        "git commit -m 'C: HEAD~1 era sbagliato'",
        "git commit --author='Prova <prova@example.com>' -m x",
    ],
)
def test_commit_con_messaggio_proprio_ammesso(sessione_condivisa: Path, comando: str):
    codice, errore = _bash(sessione_condivisa, comando)
    assert codice == 0, errore


# ---------------------------------------------------------------------------
# B. fetch e pull: solo con il nome del proprio branch
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("comando", ["git fetch", "git fetch origin", "git fetch --prune", "git pull", "git pull origin"])
def test_fetch_e_pull_senza_nome_stampano_gli_archivi(sessione: Path, comando: str):
    """Il buco: senza il nome del branch, git scarica TUTTI i branch del remoto e
    ne stampa i nomi, archivi compresi."""
    _git(sessione, "branch", "-q", "--set-upstream-to", f"origin/{PROPRIO}")  # per `git pull` senza nulla
    codice, errore = _bash(sessione, comando)
    assert codice == 2, f"BUCO: il guardiano consente {comando!r}"
    assert errore.startswith(RIFIUTO)
    assert "research/archivio/campagna/BTCUSDT" in _bash_vero(sessione, comando)


@pytest.mark.parametrize(
    "comando",
    [
        "git fetch origin main",
        "git fetch origin HEAD",
        "git fetch origin refs/heads/main",
        "git fetch origin 'refs/heads/*:refs/remotes/origin/*'",
        "git fetch origin research/campagna/BTCUSDT main",
        "git fetch origin research/campagna/BTCUSDT research/campagna/BTCUSDT",
        "git fetch origin research/campagna/BTCUSDT:research/campagna/BTCUSDT",
        "git fetch origin +research/campagna/BTCUSDT:refs/remotes/origin/research/campagna/BTCUSDT",
        "git fetch origin research/campagna/BTCUSDT:refs/remotes/origin/main",
        "git fetch --all",
        "git fetch --multiple origin research/campagna/BTCUSDT",
        "git fetch --tags origin research/campagna/BTCUSDT",
        "git fetch -t origin research/campagna/BTCUSDT",
        "git fetch --prune origin research/campagna/BTCUSDT",
        "git fetch --refmap='' origin research/campagna/BTCUSDT",
        "git fetch --upload-pack='cat docs/state.md' origin research/campagna/BTCUSDT",
        "git fetch ../origine.git research/campagna/BTCUSDT",
        "git fetch origin research/campagna/ETHUSDT",
        "git fetch origin research/archivio/campagna/BTCUSDT",
        "git pull --all",
        "git pull origin main",
        "git pull origin research/campagna/BTCUSDT main",
        "git pull --rebase=interactive origin research/campagna/BTCUSDT",
        "git pull -s ours origin research/campagna/BTCUSDT",
        "git pull --allow-unrelated-histories origin research/campagna/BTCUSDT",
    ],
)
def test_fetch_e_pull_fuori_dal_proprio_branch_rifiutati(sessione_condivisa: Path, comando: str):
    _rifiutato(sessione_condivisa, comando)


def test_fetch_di_un_hash_rifiutato(repo: _Repo):
    """Un hash (anche dell'archivio) non e' il nome del proprio branch."""
    for comando in ("git fetch origin {archivio}", "git fetch origin {padre}", "git pull origin {archivio}"):
        _rifiutato(repo.radice, repo.comando(comando))


@pytest.mark.parametrize(
    "comando",
    [
        "git fetch origin research/campagna/BTCUSDT",
        "git fetch -q origin research/campagna/BTCUSDT",
        "git fetch --no-tags origin refs/heads/research/campagna/BTCUSDT",
        "git fetch origin research/campagna/BTCUSDT:refs/remotes/origin/research/campagna/BTCUSDT",
        "git fetch origin refs/heads/research/campagna/BTCUSDT:refs/remotes/origin/research/campagna/BTCUSDT",
        "git pull origin research/campagna/BTCUSDT",
        "git pull --ff-only origin research/campagna/BTCUSDT",
        "git pull --rebase origin research/campagna/BTCUSDT",
        "git pull --no-edit -q origin research/campagna/BTCUSDT",
    ],
)
def test_fetch_e_pull_del_proprio_branch_ammessi_e_innocui(sessione: Path, comando: str):
    codice, errore = _bash(sessione, comando)
    assert codice == 0, errore
    codice, uscita = _bash_vero_esito(sessione, comando)
    assert codice == 0, uscita
    assert "archivio" not in uscita and "main" not in uscita, uscita


# ---------------------------------------------------------------------------
# C. il contenuto di una revisione: solo HEAD e il proprio branch
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "comando",
    [
        # opzioni che stampano il contenuto dei commit nella storia della propria cartella
        "git log -p -- research/campagne/BTCUSDT/",
        "git log --format=%B -p -- research/campagne/BTCUSDT/",
        "git log --patch -- research/campagne/BTCUSDT/",
        "git log --patch-with-stat -- research/campagne/BTCUSDT/",
        "git log -U0 -- research/campagne/BTCUSDT/",
        "git log --unified=1 -- research/campagne/BTCUSDT/",
        "git log -sp -- research/campagne/BTCUSDT/",
        "git log -L1,1:research/campagne/BTCUSDT/scheda_moneta.md --format=%B",
        "git log -p --word-diff -- research/campagne/BTCUSDT/",
        # git show / diff / blame / grep su un antenato di HEAD
        "git show {vecchio}:research/campagne/BTCUSDT/scheda_moneta.md",
        "git show HEAD~3:research/campagne/BTCUSDT/scheda_moneta.md",
        "git show HEAD^^^:research/campagne/BTCUSDT/scheda_moneta.md",
        "git diff HEAD~3 -- research/campagne/BTCUSDT/",
        "git diff {vecchio} HEAD -- research/campagne/BTCUSDT/scheda_moneta.md",
        "git diff HEAD~3:research/campagne/BTCUSDT/scheda_moneta.md HEAD:research/campagne/BTCUSDT/scheda_moneta.md",
        "git diff-index -p HEAD~3 -- research/campagne/BTCUSDT/",
        "git blame HEAD~3 -- research/campagne/BTCUSDT/scheda_moneta.md",
        "git annotate HEAD~3 -- research/campagne/BTCUSDT/scheda_moneta.md",
        "git grep CAMPO HEAD~3 -- research/campagne/BTCUSDT/",
        # esporta le patch
        "git format-patch --stdout -2 -- research/campagne/BTCUSDT/",
    ],
)
def test_contenuto_vecchio_della_propria_cartella_rifiutato(repo: _Repo, comando: str):
    """Il buco: la storia della propria cartella comincia sul branch principale.
    Un antenato di HEAD ha una versione vecchia della scheda, con un campo tolto dopo."""
    comando = repo.comando(comando)
    assert CONTENUTO_VECCHIO in _bash_vero(repo.radice, comando), "il comando non stampa il riservato: non e' un buco"
    _rifiutato(repo.radice, comando)


@pytest.mark.parametrize("opzione", ["-S", "-G"])
def test_ricerca_nel_contenuto_dei_commit_rifiutata(repo: _Repo, opzione: str):
    """Il buco: `-S`/`-G` scelgono i commit in base al contenuto, quindi rispondono
    alla domanda «la scheda conteneva X?» anche senza stampare X."""
    comando = f"git log {opzione}{{testo}} --oneline -- research/campagne/BTCUSDT/"
    assert "C2 scheda" in _bash_vero(repo.radice, comando.format(testo=CONTENUTO_VECCHIO))
    assert _bash_vero(repo.radice, comando.format(testo="NON_C_E_MAI_STATO")).strip() == ""
    _rifiutato(repo.radice, comando.format(testo=CONTENUTO_VECCHIO))


@pytest.mark.parametrize(
    "comando",
    [
        "git log --cc -- research/campagne/BTCUSDT/",
        # git 2.43 non accetta `--pat` per `log`; il guardiano lo rifiuta comunque (nel dubbio)
        "git log --pat -- research/campagne/BTCUSDT/",
        "git log -c -- research/campagne/BTCUSDT/",
        "git log -m --stat -- research/campagne/BTCUSDT/",
        "git log --diff-merges=on -- research/campagne/BTCUSDT/",
        "git log --remerge-diff -- research/campagne/BTCUSDT/",
        "git log -W -- research/campagne/BTCUSDT/",
        "git log --function-context -- research/campagne/BTCUSDT/",
        "git log -u -- research/campagne/BTCUSDT/",
        "git log --binary -- research/campagne/BTCUSDT/",
        "git log --ext-diff -- research/campagne/BTCUSDT/",
        "git log --textconv -- research/campagne/BTCUSDT/",
        # in `log` queste stampano il contenuto solo insieme a `-p`; il guardiano le rifiuta comunque
        "git log --word-diff -- research/campagne/BTCUSDT/",
        "git log --color-words -- research/campagne/BTCUSDT/",
        "git log --word-diff-regex=. -- research/campagne/BTCUSDT/",
        "git log --pickaxe-regex -S x -- research/campagne/BTCUSDT/",
        "git log --find-object={blob_vecchio} -- research/campagne/BTCUSDT/",
        "git whatchanged -p -- research/campagne/BTCUSDT/",
        "git shortlog -p HEAD -- research/campagne/BTCUSDT/",
        "git rev-list -p HEAD -- research/campagne/BTCUSDT/",
        # contenuti da un antenato di HEAD o dal proprio branch con un suffisso
        "git diff {padre} -- research/campagne/BTCUSDT/",
        "git diff HEAD~1 -- research/campagne/BTCUSDT/",
        "git diff research/campagna/BTCUSDT~1 -- research/campagne/BTCUSDT/",
        "git show origin/research/campagna/BTCUSDT~1:research/campagne/BTCUSDT/scheda_moneta.md",
        "git restore -s HEAD~1 -- research/campagne/BTCUSDT/ipotesi.md",
        "git restore -sHEAD~3 -- research/campagne/BTCUSDT/scheda_moneta.md",
        "git restore --source={padre} -- research/campagne/BTCUSDT/scheda_moneta.md",
        "git reset HEAD~3 -- research/campagne/BTCUSDT/scheda_moneta.md",
        "git reset --hard HEAD~3",
        "git reset --soft {vecchio}",
        "git cherry-pick HEAD",
        "git revert --no-commit HEAD",
        "git stash store -m x HEAD",
        "git stash create",
        "git stash branch altro",
        "git checkout-index -f -- research/campagne/BTCUSDT/scheda_moneta.md",
        # oggetti letti per hash
        "git update-index --cacheinfo 100644,{blob_vecchio},research/campagne/BTCUSDT/scheda_moneta.md",
        "git merge-tree {vecchio} {vecchio} HEAD",
        "git verify-commit -v HEAD~1",
        "git notes show HEAD~1",
        "git tag -n99",
        "git apply research/campagne/BTCUSDT/patch.diff",
        "git am research/campagne/BTCUSDT/patch.mbox",
        # nomi di tutti i file del repo, anche delle cartelle delle altre monete
        "git ls-files",
        "git ls-tree -r --name-only HEAD",
        "git ls-tree HEAD research/",
        "git ls-tree HEAD:research/campagne",
    ],
)
def test_contenuto_e_oggetti_altri_rifiuti(repo: _Repo, comando: str):
    _rifiutato(repo.radice, repo.comando(comando))


@pytest.mark.parametrize("comando", ["git ls-files", "git ls-tree -r --name-only HEAD"])
def test_elenco_dei_file_senza_percorso_mostra_le_altre_monete(repo: _Repo, comando: str):
    assert ALTRA_MONETA in _bash_vero(repo.radice, comando)
    _rifiutato(repo.radice, comando)


@pytest.mark.parametrize(
    "comando",
    [
        "git restore -s HEAD~3 -- research/campagne/BTCUSDT/scheda_moneta.md",
        "git reset -q --hard HEAD~3",
        "git update-index --cacheinfo 100644,{blob_vecchio},research/campagne/BTCUSDT/scheda_moneta.md "
        "&& git restore research/campagne/BTCUSDT/scheda_moneta.md",
    ],
)
def test_contenuto_vecchio_rimesso_sul_disco_rifiutato(repo_nuovo: _Repo, comando: str):
    """Il buco: questi comandi rimettono sul disco, nella propria cartella, la
    versione vecchia della scheda; da li' un `cat` la legge."""
    comando = repo_nuovo.comando(comando)
    _rifiutato(repo_nuovo.radice, comando)
    _bash_vero(repo_nuovo.radice, comando)
    assert CONTENUTO_VECCHIO in (repo_nuovo.radice / "research/campagne/BTCUSDT/scheda_moneta.md").read_text()


@pytest.mark.parametrize("comando", ["git clean -fX", "git clean -fdX", "git stash push -a", "git stash -a",
                                     "git stash push --all", "git stash -qa"])
def test_comandi_che_tolgono_il_marcatore_rifiutati(repo_nuovo: _Repo, comando: str):
    """Il buco: il marcatore e' ignorato da git (.gitignore), quindi `clean -X` lo
    cancella e `stash -a` lo mette da parte; senza marcatore il guardiano si spegne."""
    _rifiutato(repo_nuovo.radice, comando)
    _bash_vero(repo_nuovo.radice, comando)
    assert not (repo_nuovo.radice / "research" / ".sessione").exists()
    assert _bash(repo_nuovo.radice, "cat docs/state.md")[0] == 0  # guardiano spento


@pytest.mark.parametrize(
    "comando",
    [
        "git show HEAD:research/campagne/BTCUSDT/scheda_moneta.md",
        "git diff HEAD -- research/campagne/BTCUSDT/",
        "git diff origin/research/campagna/BTCUSDT HEAD -- research/campagne/BTCUSDT/",
        "git diff --cached",
        "git diff",
        "git diff --stat -- research/campagne/BTCUSDT/",
        "git blame HEAD -- research/campagne/BTCUSDT/scheda_moneta.md",
        "git grep scheda HEAD -- research/campagne/BTCUSDT/",
        "git restore -- research/campagne/BTCUSDT/scheda_moneta.md",
        "git restore --staged -- research/campagne/BTCUSDT/scheda_moneta.md",
        "git reset -q -- research/campagne/BTCUSDT/scheda_moneta.md",
        "git reset -q --hard origin/research/campagna/BTCUSDT",
        # dal 10 ott 2026 `stash` solo con -q, e `stash list` vietato (stampa l'oggetto di
        # HEAD anche con -q): test_reset_e_stash_senza_q_stampano_l_oggetto_di_head
        "git stash push -q -m 'prima di provare' -- research/campagne/BTCUSDT/",
        "git log --stat -- research/campagne/BTCUSDT/",
        "git ls-files -- research/campagne/BTCUSDT/",
        "git ls-tree -r --name-only HEAD -- research/campagne/BTCUSDT/",
    ],
)
def test_contenuto_di_head_e_del_proprio_branch_ammesso(repo_nuovo: _Repo, comando: str):
    radice = repo_nuovo.radice
    codice, errore = _bash(radice, comando)
    assert codice == 0, errore
    codice, uscita = _bash_vero_esito(radice, comando)
    assert codice == 0, uscita
    for riservato in RISERVATI:
        assert riservato not in uscita, f"{comando!r} stampa {riservato}"


# ---------------------------------------------------------------------------
# D. WebFetch: solo i siti della lista bianca (vedi anche test_campagna_webfetch_*)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "url",
    [
        "https://cdn.jsdelivr.net/gh/x/y@main/research/campagne/BTCUSDT/log.jsonl",
        "https://raw.githack.com/x/y/main/z",
        "https://sourcegraph.com/github.com/x/y",
        "https://web.archive.org/web/2026/https://github.com/x",
        "https://archive.org/x",
        "https://gitlab.com/x/y",
        "https://example.com/",
        "https://arxiv.org.example.com/abs/1",
        "https://evilarxiv.org/abs/1",
        "https://arxiv.org%2F@github.com/",
        "https://arxiv.org%252F@github.com/",
        "https://ssrn.com@github.com/",
        "https://arxiv.org/abs/%252e%252e",
        "https://arxiv.org/abs/research%2Farchivio%2Fcampagna%2FBTCUSDT",
        "https://arxiv.org/abs/research%252Farchivio%252Fcampagna",
        "https://arxiv.org:abc/x",
        "https://xn--arxiv-xyz.org/x",
        "http://ARXIV.ORG.evil.net/x",
    ],
)
def test_webfetch_fuori_dalla_lista_bianca_rifiutato(campagna: Path, url: str):
    codice, errore = _esegui(campagna, "WebFetch", {"url": url, "prompt": "leggi"})
    assert codice == 2, f"BUCO: WebFetch {url!r} consentito in campagna"
    assert errore.startswith(RIFIUTO)


# ---------------------------------------------------------------------------
# E. WebSearch: ammessa, ma non verso questo repository
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "tool_input",
    [
        {"query": "time series momentum Moskowitz 2012"},
        {"query": "cryptocurrency momentum returns 2019 paper"},
        {"query": "site:arxiv.org bitcoin volatility"},
        {"query": "funding rate perpetual futures site:ssrn.com"},
        {"query": "website: trend following"},
        {"query": "momentum", "allowed_domains": ["arxiv.org", "papers.ssrn.com", "*.nber.org"]},
        {"query": "momentum", "blocked_domains": ["github.com"]},
    ],
)
def test_websearch_ammessa(campagna: Path, tool_input: dict):
    codice, errore = _esegui(campagna, "WebSearch", tool_input)
    assert codice == 0, errore


@pytest.mark.parametrize(
    "tool_input",
    [
        {"query": "github momentum crypto"},
        {"query": "GitHub BTCUSDT strategy"},
        {"query": "gitlab trading"},
        {"query": "jsdelivr gh"},
        {"query": "githack raw"},
        {"query": "sourcegraph search"},
        {"query": "agentic_trading_system"},
        {"query": "Agentic-Trading-System"},
        {"query": "agentic trading system BTCUSDT"},
        {"query": "alessiobaljak"},
        {"query": "alessio baljak trading"},
        {"query": "research/archivio/campagna/BTCUSDT"},
        {"query": "research/campagna/BTCUSDT log.jsonl"},
        {"query": "research/coordinamento"},
        {"query": "archivio/campagna"},
        {"query": "research/campagne/BTCUSDT/ipotesi.md"},
        {"query": "research%2Farchivio%2Fcampagna"},
        {"query": "git%2568ub momentum"},
        {"query": "momentum site:medium.com"},
        {"query": "momentum site: example.com"},
        {"query": "momentum -site:arxiv.org site:reddit.com"},
        {"query": "momentum SITE:raw.githubusercontent.com"},
        {"query": "momentum site:"},
        {"query": "momentum", "allowed_domains": ["github.com"]},
        {"query": "momentum", "allowed_domains": ["arxiv.org", "medium.com"]},
        {"query": "momentum", "allowed_domains": "arxiv.org"},
        {"query": ""},
        {},
    ],
)
def test_websearch_verso_il_repository_rifiutata(campagna: Path, tool_input: dict):
    codice, errore = _esegui(campagna, "WebSearch", tool_input)
    assert codice == 2, f"BUCO: WebSearch {tool_input!r} consentita in campagna"
    assert errore.startswith(RIFIUTO)


# ---------------------------------------------------------------------------
# F. git --exec-path e le variabili GIT_*
# ---------------------------------------------------------------------------


def test_exec_path_fa_eseguire_un_programma_scelto(sessione: Path):
    """La prova: `git pull` richiama `git` dalla cartella di `--exec-path`."""
    cartella = sessione / "research" / "campagne" / "BTCUSDT" / "bin"
    cartella.mkdir()
    (cartella / "git").write_text("#!/bin/sh\necho ESEGUITO_DA_EXEC_PATH >&2\nexit 1\n")
    (cartella / "git").chmod(0o755)
    comando = "git --exec-path=research/campagne/BTCUSDT/bin pull origin research/campagna/BTCUSDT"
    assert "ESEGUITO_DA_EXEC_PATH" in _bash_vero(sessione, comando)
    _rifiutato(sessione, comando)


def test_variabili_git_cambiano_cio_che_git_fa(repo_nuovo: _Repo):
    """La prova: `GIT_CONFIG_COUNT`/`KEY`/`VALUE` sono un `git -c` sotto altro nome."""
    comando = ("GIT_CONFIG_COUNT=1 GIT_CONFIG_KEY_0=core.editor "
               "GIT_CONFIG_VALUE_0='echo ESEGUITO_DA_CONFIG >&2; false' git commit --allow-empty -q")
    assert "ESEGUITO_DA_CONFIG" in _bash_vero(repo_nuovo.radice, comando)
    _rifiutato(repo_nuovo.radice, comando)


@pytest.mark.parametrize(
    "comando",
    [
        "git --exec-path=research/campagne/BTCUSDT/bin status",
        "git --exec-path research/campagne/BTCUSDT/bin status",
        "git --exec-path",
        "git -C research/campagne/BTCUSDT --exec-path=bin status",
        "GIT_EXEC_PATH=research/campagne/BTCUSDT/bin git pull origin research/campagna/BTCUSDT",
        "GIT_INDEX_FILE=research/campagne/BTCUSDT/indice git status",
        "GIT_OBJECT_DIRECTORY=research/campagne/BTCUSDT/oggetti git status",
        "GIT_NAMESPACE=x git status",
        "export GIT_EXEC_PATH=research/campagne/BTCUSDT/bin",
        "export GIT_EDITOR=x",
        "export GIT_CONFIG_COUNT=1",
        "export PAGER=x",
        "declare GIT_DIR=research/campagne/BTCUSDT/altro.git",
        "readonly GIT_WORK_TREE=x",
        "GIT_CONFIG_COUNT=1; git status",
    ],
)
def test_exec_path_e_variabili_git_rifiutati(repo: _Repo, comando: str):
    _rifiutato(repo.radice, comando)


@pytest.mark.parametrize(
    "comando",
    [
        "git --version",
        "git -C research/campagne/BTCUSDT status",
        "GIT_TERMINAL_PROMPT=0 git status",
        "export LANG=C",
        "export PYTHONHASHSEED=0 && python3 research/src/motore.py",
    ],
)
def test_opzioni_e_variabili_innocue_ammesse(repo: _Repo, comando: str):
    codice, errore = _bash(repo.radice, comando)
    assert codice == 0, errore


def test_coordinamento_git_non_toccato(coordinamento: Path):
    """In coordinamento git non e' affare del guardiano (oltre ai percorsi)."""
    for comando in ("git fetch", "git push origin HEAD:main", "git log -p", "git --exec-path=x status",
                    "git checkout research/campagna/ETHUSDT", "GIT_EXEC_PATH=x git status"):
        assert _bash(coordinamento, comando) == (0, ""), comando


# ---------------------------------------------------------------------------
# i passi di una sessione di campagna funzionano ancora, dopo il marcatore
# ---------------------------------------------------------------------------


def test_passi_della_sessione_di_campagna_ammessi_e_funzionanti(sessione: Path):
    """Quello che una sessione di campagna fa davvero, nell'ordine: il guardiano
    lo consente, e git (eseguito davvero) lo fa senza errori e senza stampare
    nulla dell'archivio."""
    _scrivi(sessione, "research/campagne/BTCUSDT/codice/x.py", "print('ok')\n")
    _scrivi(sessione, "research/data/insample/BTCUSDT/msg.txt", "campagna: un evento nel log\n")
    with open(sessione / "research/campagne/BTCUSDT/log.jsonl", "a") as f:
        f.write('{"evento": "ipotesi"}\n')
    passi = [
        "git status",
        "git branch --show-current",
        "git add research/campagne/BTCUSDT/log.jsonl research/campagne/BTCUSDT/codice/x.py",
        "git commit -F research/data/insample/BTCUSDT/msg.txt",
        "git push -u origin research/campagna/BTCUSDT",
        "git pull origin research/campagna/BTCUSDT",
        "git fetch origin research/campagna/BTCUSDT",
        "git log --format=%cI -- research/campagne/BTCUSDT/log.jsonl",
        "git log --reverse --format=%cI origin/research/campagna/BTCUSDT -- research/campagne/BTCUSDT/log.jsonl",
        "python3 research/campagne/BTCUSDT/codice/x.py",
        "git push",
    ]
    for comando in passi:
        codice, errore = _bash(sessione, comando)
        assert codice == 0, f"{comando!r}: {errore}"
        codice, uscita = _bash_vero_esito(sessione, comando)
        assert codice == 0, f"{comando!r}: {uscita}"
        assert "archivio" not in uscita and MSG_ARCHIVIO not in uscita, uscita
    assert _git(sessione.parent / "origine.git", "log", "-1", "--format=%s", PROPRIO) == "campagna: un evento nel log"
    assert len(_bash_vero(sessione, passi[7]).split()) == 2  # due eventi nel log, due date
    strumenti = [
        ("Read", {"file_path": "research/campagne/BTCUSDT/log.jsonl"}),
        ("Write", {"file_path": "research/campagne/BTCUSDT/ipotesi.md", "content": "x"}),
        ("Edit", {"file_path": "research/campagne/BTCUSDT/log.jsonl", "old_string": "a", "new_string": "b"}),
        ("Read", {"file_path": str(sessione / "research/campagne/BTCUSDT/codice/x.py")}),
        ("WebFetch", {"url": "https://arxiv.org/abs/1234.5678", "prompt": "riassumi"}),
        ("WebSearch", {"query": "time series momentum Moskowitz 2012"}),
    ]
    for nome, ingresso in strumenti:
        codice, errore = _esegui(sessione, nome, ingresso)
        assert codice == 0, f"{nome} {ingresso}: {errore}"


def test_i_test_del_guardiano_si_possono_lanciare_in_campagna(sessione_condivisa: Path):
    comando = "python -m pytest research/src/tests/test_guardiano.py -q -p no:cacheprovider"
    codice, errore = _bash(sessione_condivisa, comando)
    assert codice == 0, errore


# ---------------------------------------------------------------------------
# Terza prova dell'attaccante (7 ott): un indirizzo dentro l'indirizzo di un
# sito ammesso, un hash di commit nei parametri, e parole vietate scritte con
# spazi o con lettere di altri alfabeti.
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("url", [
    "https://doi.org/x?url=https://cdn.jsdelivr.net/gh/o/r@0123456789abcdef0123456789abcdef01234567/x",
    "https://en.wikipedia.org/wiki/X?url=https://raw.githack.com/o/r/HEAD/x",
    "https://www.semanticscholar.org/paper/x?redirect=//cdn.jsdelivr.net/gh/o/r",
    "https://arxiv.org/abs/1?r=0123456789abcdef0123456789abcdef01234567",
    "https://arxiv.org/abs/1#https://github.com/x",
])
def test_campagna_web_rinvii_e_hash_nei_parametri_rifiutati(campagna: Path, url: str):
    codice, errore = _esegui(campagna, "WebFetch", {"url": url, "prompt": "p"})
    assert codice == 2, f"BUCO: WebFetch {url} consentito"


@pytest.mark.parametrize("url", [
    "https://arxiv.org/abs/1234.5678",
    "https://doi.org/10.1016/j.jfineco.2011.11.003",
    "https://www.semanticscholar.org/paper/Time-Series-Momentum/0123456789abcdef0123456789abcdef01234567",
    "https://en.wikipedia.org/wiki/Momentum_(finance)",
    "https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2089463",
])
def test_campagna_web_articoli_ammessi(campagna: Path, url: str):
    codice, errore = _esegui(campagna, "WebFetch", {"url": url, "prompt": "p"})
    assert codice == 0, errore


@pytest.mark.parametrize("domanda", [
    "g i t h u b agentic consegna",
    "gіthub consegna",          # «i» cirillica
    "GIT-HUB agentic",
    "agentic​trading system",  # spazio a larghezza zero
    "alessio baljak",
])
def test_campagna_ricerche_web_mascherate_rifiutate(campagna: Path, domanda: str):
    codice, errore = _esegui(campagna, "WebSearch", {"query": domanda})
    assert codice == 2, f"BUCO: WebSearch {domanda!r} consentita"


@pytest.mark.parametrize("domanda", [
    "time series momentum Moskowitz 2012",
    "funding rate perpetual futures basis paper 2021",
    "digital asset volatility clustering",
])
def test_campagna_ricerche_web_normali_ammesse(campagna: Path, domanda: str):
    codice, errore = _esegui(campagna, "WebSearch", {"query": domanda})
    assert codice == 0, errore
