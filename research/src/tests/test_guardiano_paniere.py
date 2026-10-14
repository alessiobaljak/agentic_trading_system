"""Il guardiano e la campagna del PANIERE (seconda edizione, 13 ottobre 2026).

La campagna del paniere e' una campagna «di gruppo» con il marcatore
`{"tipo": "campagna", "simbolo": "PANIERE"}` e la cartella `research/campagne/PANIERE/`:
stesse regole del gruppo (test_guardiano_gruppo.py), elenco delle monete proprio
(`research/campagne/PANIERE/monete.csv`, byte per byte uguale a quello del gruppo:
stessa impronta approvata), schede proprie in sola lettura. Qui si prova solo cio'
che cambia: che PANIERE abbia esattamente i permessi di GRUPPO, e che GRUPPO non
li perda.
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
MONETE_GRUPPO = RADICE_REPO / "research" / "campagne" / "GRUPPO" / "monete.csv"
MONETE_PANIERE = RADICE_REPO / "research" / "campagne" / "PANIERE" / "monete.csv"
RIFIUTO = "[guardiano] azione rifiutata"
ELENCO_RIFIUTATO = "[guardiano] l'elenco delle monete del gruppo non e' quello approvato"
MONETE = tuple(MONETE_GRUPPO.read_text(encoding="utf-8").splitlines()[1:])


def _scrivi(radice: Path, percorso: str, testo: str) -> None:
    p = radice / percorso
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(testo, encoding="utf-8")


def _radice(radice: Path, simbolo: str = "PANIERE") -> Path:
    """Una radice finta con le due campagne di gruppo (GRUPPO finita, PANIERE in corso), una moneta di campagna
    (ETHUSDT) e i dati in-sample delle 80 monete, di BTCUSDT e di ETHUSDT."""
    (radice / "research" / "config").mkdir(parents=True)
    shutil.copy(VIETATI_REPO, radice / "research" / "config" / "percorsi_vietati.txt")
    _scrivi(radice, "research/config/parametri.yaml", "gruppo: {}\n")
    _scrivi(radice, "research/src/motore.py", "# motore\n")
    _scrivi(radice, "research/src/guardiano.py", "# guardiano segnaposto\n")
    _scrivi(radice, "research/PROTOCOLLO.md", "protocollo\n")
    _scrivi(radice, "research/PROTOCOLLO_2.md", "seconda edizione\n")
    _scrivi(radice, "research/CHANGELOG.md", "changelog\n")
    _scrivi(radice, "research/lezioni/metodo.md", "metodo\n")
    _scrivi(radice, "research/campagne/ETHUSDT/scheda_moneta.md", "scheda ETHUSDT\n")
    for s in ("GRUPPO", "PANIERE"):
        cartella = radice / "research" / "campagne" / s
        cartella.mkdir(parents=True, exist_ok=True)
        shutil.copy(MONETE_GRUPPO, cartella / "monete.csv")
        for moneta in MONETE:
            _scrivi(radice, f"research/campagne/{s}/schede/{moneta}.md", f"scheda {moneta}\n")
        _scrivi(radice, f"research/campagne/{s}/regole.md", "regole\n")
        _scrivi(radice, f"research/campagne/{s}/via_libera_validazione.md", "via libera\n")
        _scrivi(radice, f"research/campagne/{s}/ipotesi.md", "ipotesi\n")
        _scrivi(radice, f"research/campagne/{s}/log.jsonl", "")
        _scrivi(radice, f"research/campagne/{s}/codice/strategia.py", "# strategia\n")
    for moneta in MONETE + ("BTCUSDT", "ETHUSDT"):
        _scrivi(radice, f"research/data/insample/{moneta}/x.zip", "dati\n")
    _scrivi(radice, "research/data/vault/AAVEUSDT/x.zip", "vault\n")
    _scrivi(radice, "docs/state.md", "riservato\n")
    (radice / ".claude").mkdir()
    _scrivi(radice, ".claude/settings.json", "{}\n")
    _scrivi(radice, "research/.sessione", json.dumps({"tipo": "campagna", "simbolo": simbolo}))
    return radice


def _esegui(radice: Path, tool_name: str, tool_input):
    ambiente = dict(os.environ)
    ambiente["CLAUDE_PROJECT_DIR"] = str(radice)
    carico = json.dumps({"tool_name": tool_name, "tool_input": tool_input, "cwd": str(radice)})
    esito = subprocess.run([sys.executable, str(GUARDIANO)], input=carico, capture_output=True, text=True,
                           env=ambiente, cwd=str(radice), timeout=20)
    return esito.returncode, esito.stderr


def _read(radice: Path, percorso: str):
    return _esegui(radice, "Read", {"file_path": percorso})


def _write(radice: Path, percorso: str):
    return _esegui(radice, "Write", {"file_path": percorso, "content": "x"})


@pytest.fixture(scope="module")
def paniere(tmp_path_factory) -> Path:
    return _radice(tmp_path_factory.mktemp("guardiano_paniere") / "repo")


def test_l_elenco_del_paniere_nel_repo_e_quello_approvato():
    assert MONETE_PANIERE.read_bytes() == MONETE_GRUPPO.read_bytes()
    assert hashlib.sha256(MONETE_PANIERE.read_bytes()).hexdigest() == g._IMPRONTA_MONETE_GRUPPO
    assert g.leggi_monete_gruppo(str(RADICE_REPO), simbolo="PANIERE") == MONETE
    assert g.leggi_monete_gruppo(str(RADICE_REPO)) == MONETE          # GRUPPO come prima
    schede = {p.stem for p in (RADICE_REPO / "research" / "campagne" / "PANIERE" / "schede").glob("*.md")}
    assert schede == set(MONETE)
    with pytest.raises(g.ElencoGruppoNonApprovato):
        g.leggi_monete_gruppo(str(RADICE_REPO), simbolo="ETHUSDT")


def test_monete_dati_ammesse_del_paniere():
    assert g.monete_dati_ammesse("PANIERE", frozenset(MONETE)) == frozenset(MONETE) | {"BTCUSDT"}
    assert g.monete_dati_ammesse("ETHUSDT") == frozenset({"ETHUSDT", "BTCUSDT"})
    assert "PANIERE" in g.SIMBOLI_GRUPPO and "GRUPPO" in g.SIMBOLI_GRUPPO


def test_il_paniere_legge_i_dati_delle_80_monete_e_di_btc_non_di_una_moneta_di_campagna(paniere):
    assert _read(paniere, "research/data/insample/AAVEUSDT/x.zip")[0] == 0
    assert _read(paniere, "research/data/insample/BTCUSDT/x.zip")[0] == 0
    codice, errore = _read(paniere, "research/data/insample/ETHUSDT/x.zip")
    assert codice == 2 and errore.startswith(RIFIUTO) and "sessione campagna PANIERE" in errore
    assert _read(paniere, "research/data/vault/AAVEUSDT/x.zip")[0] == 2
    assert _read(paniere, "research/data/insample")[0] == 2


def test_il_paniere_vede_solo_la_propria_cartella(paniere):
    assert _read(paniere, "research/campagne/PANIERE/ipotesi.md")[0] == 0
    assert _write(paniere, "research/campagne/PANIERE/ipotesi.md")[0] == 0
    assert _read(paniere, "research/campagne/GRUPPO/log.jsonl")[0] == 2
    assert _read(paniere, "research/campagne/GRUPPO/ipotesi.md")[0] == 2
    assert _read(paniere, "research/campagne/GRUPPO/schede/AAVEUSDT.md")[0] == 2
    assert _read(paniere, "research/campagne/GRUPPO/codice/strategia.py")[0] == 2
    assert _read(paniere, "research/campagne/ETHUSDT/scheda_moneta.md")[0] == 2
    assert _read(paniere, "docs/state.md")[0] == 2
    assert _read(paniere, "research/PROTOCOLLO_2.md")[0] == 2   # non e' fra i file ammessi: lo cita regole.md


def test_i_file_del_paniere_scritti_dal_coordinamento_sono_in_sola_lettura(paniere):
    for percorso in ("research/campagne/PANIERE/monete.csv", "research/campagne/PANIERE/schede/AAVEUSDT.md",
                     "research/campagne/PANIERE/regole.md", "research/campagne/PANIERE/via_libera_validazione.md"):
        assert _read(paniere, percorso)[0] == 0, percorso
        codice, errore = _write(paniere, percorso)
        assert codice == 2 and errore.startswith(RIFIUTO), percorso


def test_il_paniere_legge_le_regole_del_gruppo_che_eredita_ma_non_le_scrive(paniere):
    """Correzione del 14 ott 2026: le regole della campagna PANIERE ereditano quelle del gruppo
    (`research/campagne/GRUPPO/regole.md`), che la sessione deve poter leggere; resta in sola lettura, e il
    resto della cartella del gruppo resta vietato. Una campagna di una moneta sola non le legge."""
    assert g.ammesso_in_campagna("research/campagne/GRUPPO/regole.md", "PANIERE")
    assert g.ammesso_in_campagna("research/campagne/GRUPPO/regole.md", "GRUPPO")
    assert not g.ammesso_in_campagna("research/campagne/GRUPPO/regole.md", "ETHUSDT")
    assert not g.ammesso_in_campagna("research/campagne/GRUPPO/via_libera_validazione.md", "PANIERE")
    assert not g.ammesso_in_campagna("research/campagne/GRUPPO/ipotesi.md", "PANIERE")
    assert g.e_protetto("research/campagne/GRUPPO/regole.md")
    assert _read(paniere, "research/campagne/GRUPPO/regole.md")[0] == 0
    codice, errore = _write(paniere, "research/campagne/GRUPPO/regole.md")
    assert codice == 2 and errore.startswith(RIFIUTO)
    assert _esegui(paniere, "Bash", {"command": "cat research/campagne/GRUPPO/regole.md"})[0] == 0
    assert _esegui(paniere, "Bash", {"command": "cat research/campagne/GRUPPO/ipotesi.md"})[0] == 2


def test_un_elenco_del_paniere_cambiato_rifiuta_ogni_azione(tmp_path):
    radice = _radice(tmp_path / "repo")
    p = radice / "research" / "campagne" / "PANIERE" / "monete.csv"
    p.write_bytes(p.read_bytes().replace(b"AAVEUSDT", b"ETHUSDT0"))
    codice, errore = _read(radice, "research/campagne/PANIERE/ipotesi.md")
    assert codice == 2 and errore.startswith(ELENCO_RIFIUTATO)


def test_il_gruppo_resta_come_prima(tmp_path):
    radice = _radice(tmp_path / "repo", simbolo="GRUPPO")
    assert _read(radice, "research/data/insample/AAVEUSDT/x.zip")[0] == 0
    assert _read(radice, "research/campagne/GRUPPO/ipotesi.md")[0] == 0
    assert _read(radice, "research/campagne/PANIERE/ipotesi.md")[0] == 2
    assert _read(radice, "research/campagne/PANIERE/regole.md")[0] == 2   # l'eredita' va in un verso solo
    assert _write(radice, "research/campagne/GRUPPO/monete.csv")[0] == 2
    moneta = _radice(tmp_path / "repo_eth", simbolo="ETHUSDT")
    assert _read(moneta, "research/campagne/GRUPPO/regole.md")[0] == 2
