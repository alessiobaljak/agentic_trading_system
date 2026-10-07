"""Revisione 4.4 del guardiano (7 ottobre 2026): la storia, l'archivio, gli altri strumenti.

Che cosa si protegge e perche'. Le campagne BTCUSDT, ETHUSDT e SOLUSDT si
rifanno da capo, ognuna su un branch NUOVO `research/campagna/<SIMBOLO>` nato dal
branch principale. I tentativi precedenti diventano
`research/archivio/campagna/<SIMBOLO>` e hanno file agli STESSI percorsi della
campagna nuova (`research/campagne/<SIMBOLO>/log.jsonl`, `ipotesi.md`,
`consegna.md`...). La sessione nuova non deve poterli leggere, e nemmeno i
messaggi dei commit del branch principale: raccontano come e' finito il
tentativo precedente, e ~1.500 commit del bot sono stati scritti nel periodo
chiuso del vault (2024-2026).

Una revisione avversaria ha trovato, in campagna, tre buchi:
  1. i comandi di storia senza percorso (`git log`, `git show HEAD`,
     `git shortlog`, `git rev-list --format=%B`, `git blame` di un file fuori
     dalla propria cartella) stampavano i messaggi di tutto il branch principale;
  2. qualunque hash valeva come "proprio": un hash dell'archivio (lo stampa
     `git fetch`) apriva `git show <hash>:research/campagne/X/log.jsonl`;
     `show-branch`, `name-rev`, `describe` non erano vietati;
  3. il guardiano vedeva solo file, ricerche e Bash: gli strumenti MCP di GitHub
     (che leggono qualunque branch), quelli delle sessioni remote (i cui prompt
     ricordano il tentativo precedente), gli Artifact e WebFetch verso
     raw.githubusercontent.com passavano senza controllo.

I test costruiscono un VERO repo git in una cartella temporanea: un branch
`main` con tre commit (uno tocca CLAUDE.md, uno la scheda della moneta, uno il
protocollo), l'archivio `research/archivio/campagna/BTCUSDT` che aggiunge il
`log.jsonl` del tentativo precedente, e il branch di campagna
`research/campagna/BTCUSDT` nato da `main`, con un commit suo, attivo, e il
marcatore di campagna. Per i buchi della storia ogni test prima ESEGUE il
comando in bash e mostra che stampa davvero qualcosa di riservato (cosi' nessun
test segnala un falso buco), poi pretende che il guardiano, eseguito come hook,
lo rifiuti. Per i comandi ammessi mostra che l'uscita non contiene nulla di
riservato e che il guardiano li lascia passare.
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

#: testi riconoscibili: se compaiono nell'uscita di un comando, il comando ha letto troppo
MSG_PRINCIPALE = "MESSAGGIO_DEL_PRINCIPALE"  # commit di main che non tocca la propria cartella
MSG_CLAUDE = "MESSAGGIO_CLAUDE"  # commit di main che tocca CLAUDE.md
MSG_ARCHIVIO = "MESSAGGIO_ARCHIVIO"  # commit dell'archivio del tentativo precedente
CONTENUTO_ARCHIVIO = "ARCHIVIO_RISERVATO"  # log.jsonl del tentativo precedente
CONTENUTO_UNIVERSO = "UNIVERSO_RISERVATO"  # file di coordinamento toccato dallo stesso commit della scheda
RISERVATI = (MSG_PRINCIPALE, MSG_CLAUDE, MSG_ARCHIVIO, CONTENUTO_ARCHIVIO, CONTENUTO_UNIVERSO)


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


def _costruisci_repo(radice: Path) -> dict:
    """Il repo di prova: main, archivio, campagna attiva. Restituisce gli hash che servono."""
    radice.mkdir(parents=True)
    _git(radice, "init", "-q", "-b", "main")
    _scrivi(radice, "research/config/percorsi_vietati.txt", VIETATI_REPO.read_text(encoding="utf-8"))
    _scrivi(radice, "research/src/motore.py", "# motore\n")
    _scrivi(radice, "docs/state.md", "stato\n")
    _scrivi(radice, "CLAUDE.md", "istruzioni\n")
    _commit(radice, f"C1 {MSG_CLAUDE}: istruzioni", ".")
    # il commit della scheda tocca anche un file di coordinamento (l'universo delle monete)
    _scrivi(radice, "research/campagne/BTCUSDT/scheda_moneta.md", "scheda BTCUSDT\n")
    _scrivi(radice, "research/universo/monete_campagna.csv", f"{CONTENUTO_UNIVERSO}\n")
    _commit(radice, "C2 scheda BTCUSDT", ".")
    # un commit del principale che CITA la cartella della campagna ma non la tocca
    _scrivi(radice, "research/PROTOCOLLO.md", "protocollo\n")
    _commit(radice, f"C3 {MSG_PRINCIPALE}: com'e' finito research/campagne/BTCUSDT/", ".")
    # l'archivio del tentativo precedente: stesso percorso della campagna nuova
    _git(radice, "checkout", "-q", "-b", "research/archivio/campagna/BTCUSDT")
    _scrivi(radice, "research/campagne/BTCUSDT/log.jsonl", f"{CONTENUTO_ARCHIVIO}\n")
    _commit(radice, f"{MSG_ARCHIVIO}: tentativo precedente", ".")
    archivio = _git(radice, "rev-parse", "HEAD")
    # la campagna nuova, nata da main, con un commit suo
    _git(radice, "checkout", "-q", "main")
    _git(radice, "checkout", "-q", "-b", "research/campagna/BTCUSDT")
    _scrivi(radice, "research/campagne/BTCUSDT/ipotesi.md", "ipotesi nuove\n")
    _commit(radice, "campagna: ipotesi", ".")
    # come dopo un `git push -u`: il proprio branch esiste anche sul remoto
    _git(radice, "update-ref", "refs/remotes/origin/research/campagna/BTCUSDT", "HEAD")
    _scrivi(radice, "research/.sessione", json.dumps({"tipo": "campagna", "simbolo": "BTCUSDT"}))
    return {
        "archivio": archivio,
        "archivio_corto": archivio[:10],
        "padre": _git(radice, "rev-parse", "HEAD~1"),  # la punta di main, antenato di HEAD
    }


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


def _bash_vero(radice: Path, comando: str) -> str:
    """Esegue DAVVERO il comando in bash nel repo di prova: stdout+stderr."""
    esito = subprocess.run(
        ["bash", "-c", comando], cwd=str(radice), env=_ambiente_git(radice.parent),
        capture_output=True, text=True, timeout=30,
    )
    return esito.stdout + esito.stderr


class _Repo:
    def __init__(self, radice: Path, hash_: dict):
        self.radice = radice
        self.hash = hash_

    def comando(self, schema: str) -> str:
        """`{archivio}`, `{archivio_corto}`, `{padre}` diventano gli hash veri."""
        return schema.format(**self.hash)


@pytest.fixture(scope="module")
def repo(tmp_path_factory) -> _Repo:
    radice = tmp_path_factory.mktemp("guardiano_4_4") / "repo"
    return _Repo(radice, _costruisci_repo(radice))


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
    assert _git(repo.radice, "rev-parse", "--abbrev-ref", "HEAD") == "research/campagna/BTCUSDT"
    assert not (repo.radice / "research/campagne/BTCUSDT/log.jsonl").exists()
    assert CONTENUTO_ARCHIVIO in _bash_vero(repo.radice, f"git show {repo.hash['archivio']}:research/campagne/BTCUSDT/log.jsonl")
    assert MSG_PRINCIPALE in _bash_vero(repo.radice, "git log")


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
        "git log --format=%B -p -- research/campagne/BTCUSDT/",
        "git log --oneline research/campagna/BTCUSDT -- research/campagne/BTCUSDT/",
        "git log --oneline {padre} -- research/campagne/BTCUSDT/",
        "git log --no-walk --format=%B HEAD~1 -- research/campagne/BTCUSDT/",
        "git log -L1,1:research/campagne/BTCUSDT/scheda_moneta.md --format=%B",
        "git shortlog HEAD -- research/campagne/BTCUSDT/",
        "git rev-list --format=%B HEAD -- research/campagne/BTCUSDT/",
        "git blame research/campagne/BTCUSDT/scheda_moneta.md",
        "git blame --porcelain -- research/campagne/BTCUSDT/scheda_moneta.md",
        "git annotate research/campagne/BTCUSDT/scheda_moneta.md",
        "git format-patch --stdout -2 -- research/campagne/BTCUSDT/",
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
    codice, errore = _bash(repo.radice, comando)
    assert codice == 2, f"BUCO: il guardiano consente {comando!r}"
    assert errore.startswith(RIFIUTO)
    assert "sessione campagna BTCUSDT" in errore


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
        "git log HEAD~1..HEAD -- research/campagne/BTCUSDT/",
        "git log HEAD@{{1}} -- research/campagne/BTCUSDT/",
        "git log -L1,1:CLAUDE.md",
        "git log HEAD:research/campagne/BTCUSDT/ -- research/campagne/BTCUSDT/",
        "git blame -C -C -C research/campagne/BTCUSDT/scheda_moneta.md",
        "git blame -S research/campagne/BTCUSDT/rev.txt research/campagne/BTCUSDT/scheda_moneta.md",
    ],
)
def test_storia_altri_rifiuti(repo: _Repo, comando: str):
    codice, errore = _bash(repo.radice, repo.comando(comando))
    assert codice == 2, f"BUCO: il guardiano consente {comando!r}"
    assert errore.startswith(RIFIUTO)


# ---------------------------------------------------------------------------
# B. git show: solo `<rif>:<percorso>`
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "comando",
    [
        "git show {padre}:research/campagne/BTCUSDT/scheda_moneta.md",
        "git show HEAD:research/campagne/BTCUSDT/ipotesi.md",
        "git show HEAD~1:research/campagne/BTCUSDT/scheda_moneta.md",
        "git show HEAD~1:research/src/motore.py",
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
        ("git show --stat HEAD~2", "C2 scheda"),
    ],
)
def test_show_che_stampa_il_messaggio_rifiutato(repo: _Repo, comando: str, riservato: str):
    comando = repo.comando(comando)
    assert riservato in _bash_vero(repo.radice, comando)
    codice, errore = _bash(repo.radice, comando)
    assert codice == 2, f"BUCO: il guardiano consente {comando!r}"
    assert errore.startswith(RIFIUTO)


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
    """L'hash dell'archivio puo' arrivare da `git fetch`: non e' un antenato di HEAD."""
    comando = comando.format(riservato=CONTENUTO_ARCHIVIO, **repo.hash)
    assert riservato in _bash_vero(repo.radice, comando)
    codice, errore = _bash(repo.radice, comando)
    assert codice == 2, f"BUCO: il guardiano consente {comando!r}"
    assert errore.startswith(RIFIUTO)


@pytest.mark.parametrize(
    "comando",
    [
        "git diff {padre} -- research/campagne/BTCUSDT/",
        "git diff HEAD~1 -- research/campagne/BTCUSDT/",
        "git ls-tree {padre} -- research/campagne/BTCUSDT/",
        "git rev-parse {padre}",
    ],
)
def test_hash_antenato_di_head_ammesso(repo: _Repo, comando: str):
    codice, errore = _bash(repo.radice, repo.comando(comando))
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
    codice, errore = _bash(repo.radice, comando)
    assert codice == 2, f"BUCO: il guardiano consente {comando!r}"
    assert errore.startswith(RIFIUTO)


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
        ("git diff --output=.claude/settings.json HEAD~1 -- research/campagne/BTCUSDT/", 2),
        ("git log --output=research/src/guardiano.py -- research/campagne/BTCUSDT/", 2),
        ("git diff --output docs/x.txt HEAD~1 -- research/campagne/BTCUSDT/", 2),
        ("git diff-files --output=research/.sessione", 2),
        ("git diff --output=research/campagne/BTCUSDT/diff.txt HEAD~1 -- research/campagne/BTCUSDT/", 0),
        ("git format-patch -o research/campagne/BTCUSDT/patch -1 -- research/campagne/BTCUSDT/", 0),
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
    ammessa, il file del tentativo precedente."""
    radice = tmp_path / "repo"
    hash_ = _costruisci_repo(radice)
    _bash_vero(radice, f"git restore -s{hash_['archivio']} -- research/campagne/BTCUSDT/log.jsonl")
    assert CONTENUTO_ARCHIVIO in (radice / "research/campagne/BTCUSDT/log.jsonl").read_text()


@pytest.mark.parametrize(
    "comando",
    [
        "git restore -s HEAD~1 -- research/campagne/BTCUSDT/ipotesi.md",
        "git restore -sHEAD -- research/campagne/BTCUSDT/ipotesi.md",
        "git restore --source={padre} -- research/campagne/BTCUSDT/scheda_moneta.md",
        "git branch",
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
    ["git status", "git fetch", "git pull", "git push origin research/campagna/BTCUSDT",
     "git add research/campagne/BTCUSDT/ipotesi.md && git commit -m 'campagna: ipotesi'",
     "git diff research/src/motore.py", "git grep scheda -- research/campagne/BTCUSDT/",
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
        "https://arxiv.org/abs/1234?x=github.com",
        "http://www.example.com/path/github.com",
        "https://data.binance.vision/?prefix=data/futures/um/",
        "https://notgithub.com/x",
        "https://github.com.example.org/x",
        "https://en.wikipedia.org/wiki/Momentum_(finance)",
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
    for strumento in ("WebFetch", "mcp__github__list_branches", "mcp__github__get_file_contents",
                      "mcp__Claude_Code_Remote__list_sessions", "Artifact", "Read", "Bash"):
        assert _matcher_copre(matcher, strumento), strumento
    # il vecchio matcher non li copriva: e' il buco che questo test chiude
    vecchio = "Read|Write|Edit|MultiEdit|NotebookEdit|Glob|Grep|Bash"
    assert not _matcher_copre(vecchio, "WebFetch")
    assert not _matcher_copre(vecchio, "mcp__github__list_branches")


def test_senza_marcatore_nessuna_domanda_a_git(senza_marcatore: Path, monkeypatch):
    """Ora che il guardiano gira per ogni strumento, senza marcatore deve restare
    muto e veloce: nemmeno un hash fa partire git."""
    from research.src import guardiano as g

    chiamate = []
    monkeypatch.setattr(g.subprocess, "run", lambda *a, **k: chiamate.append(a) or None)
    carico = json.dumps({"tool_name": "Bash", "tool_input": {"command": "git show abcdef1234:x"},
                         "cwd": str(senza_marcatore)})
    monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(senza_marcatore))
    monkeypatch.setattr(g.sys, "stdin", __import__("io").StringIO(carico))
    assert g.main() == 0
    assert chiamate == []
