"""Revisione avversaria n. 2 del modulo `fatti` e di `config/regole_dimensione.md`.

Ogni test qui sotto documenta un difetto trovato rileggendo, uno per uno, i 265
riferimenti distinti del documento contro le righe citate del repository (6 ott
2026). I test che CADONO sono voluti: restano come promemoria per chi corregge,
e tornano verdi quando il difetto e' sistemato.

Difetti coperti:
  * `contiene_segreti` non vede chiavi che non contengono le quattro parole
    fisse (`PRIVATE_KEY`, `CREDENTIALS`) ne' i nomi in minuscolo: un segreto
    Firebase o un JSON di credenziali passerebbe il controllo in un repo pubblico.
  * `bot/config.py:41` e' citato per «timeframe_hours arriva a 4h»: il 4h e' alla
    riga 42.
  * la stima del punto 4.3 elenca 30m e 4h fra i timeframe che richiederebbero di
    toccare `timeframe_hours`: quella mappa li conosce gia' (riga 42).
  * `scripts/gate_vs_paper.py:35-44` e' citato come esempio di chiamata a
    `run_strategy`: quelle righe sono solo import; la chiamata e' altrove.
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

from research.src import fatti

RADICE = Path(__file__).resolve().parents[3]
DOCUMENTO = RADICE / "research" / "config" / "regole_dimensione.md"


@pytest.fixture(scope="module")
def documento() -> str:
    assert DOCUMENTO.is_file(), f"manca {DOCUMENTO}"
    return DOCUMENTO.read_text(encoding="utf-8")


# --------------------------------------------------------------------------- #
# Il rilevatore di segreti ha buchi noti                                        #
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize("linea", [
    "FIREBASE_PRIVATE_KEY=abcdefghijklmnop1234",
    "FIREBASE_CREDENTIALS_JSON=eyJhbGciOiJIUzI1NiJ9",
    "binance_api_secret: abcdefghijklmnop1234",
    '"private_key": "-----BEGIN PRIVATE KEY-----"',
])
def test_contiene_segreti_vede_anche_chiavi_private_e_minuscole(linea):
    """Il documento vive in un repo PUBBLICO: un valore di chiave privata o di
    credenziali che sfugge al controllo e' compromesso per sempre. Oggi lo
    schema cerca solo API_KEY/SECRET/TOKEN/PASSWORD, in maiuscolo."""
    assert fatti.contiene_segreti(linea) != [], f"non rilevato: {linea}"


# --------------------------------------------------------------------------- #
# Riferimenti che non sostengono l'affermazione                                #
# --------------------------------------------------------------------------- #
def test_config_41_non_contiene_il_4h_che_il_documento_gli_attribuisce(documento):
    """Incoerenza 7 e stima 4.3: «timeframe_hours arriva a 4h (bot/config.py:41)».
    La riga 41 contiene 1m/5m/15m; il 4h sta alla riga 42.

    Corretto il 6 ott 2026 (correttore): la prima versione chiedeva che il
    documento citasse ANCORA `bot/config.py:41` e che quella riga contenesse
    «4h»: due condizioni che nessuna correzione puo' soddisfare insieme (la
    riga 41 del bot non si tocca). Il controllo giusto e': la riga 42 contiene
    il 4h, il documento cita la 42 per quell'affermazione e non cita piu' la 41
    (la 41 da sola non sostiene nessuna frase del documento)."""
    assert fatti.verifica_ancore({"bot/config.py:42": '"4h": 4.0'}, RADICE) == []
    assert "arriva a 4h (`bot/config.py:42`)" in documento
    assert re.search(r"bot/config\.py:41(?!\d)", documento) is None, (
        "il documento cita ancora bot/config.py:41: il 4h e' alla riga 42")


def test_stima_4_3_non_deve_elencare_30m_e_4h_come_ignoti_a_timeframe_hours(documento):
    """La stima del punto 4.3 dice: «Se il timeframe della strategia e' 30m, 2h,
    4h, ...: bot/config.py:41 (timeframe_hours)». Ma `timeframe_hours` conosce
    gia' 30m e 4h (riga 42): per quei due la modifica non serve."""
    assert fatti.verifica_ancore({"bot/config.py:42": '"30m": 0.5'}, RADICE) == []
    assert fatti.verifica_ancore({"bot/config.py:42": '"4h": 4.0'}, RADICE) == []
    frase = "Se il timeframe della strategia è 30m, 2h, 4h, 6h, 8h, 12h o 1d"
    assert frase not in documento, (
        "30m e 4h sono gia' in timeframe_hours (bot/config.py:42): la stima li "
        "elenca come se richiedessero la modifica di bot/config.py:41")


def test_gate_vs_paper_35_44_sono_import_non_la_chiamata_a_run_strategy(documento):
    """Punto 5: «basta ... chiamare run_strategy ..., come fa
    scripts/gate_vs_paper.py:35-44». Quelle righe sono gli import del modulo;
    la chiamata vera a `run_strategy` sta piu' avanti (riga 215 e seguenti)."""
    percorso = RADICE / "scripts" / "gate_vs_paper.py"
    righe = [fatti.riga(percorso, n) for n in range(35, 45)]
    assert not any("run_strategy" in r for r in righe), (
        "le righe 35-44 ora contengono run_strategy: rivedere il riferimento")
    # Corretto il 6 ott 2026 (correttore): la prima versione chiedeva che il
    # documento citasse ANCORA le righe 35-44 e che quelle righe contenessero
    # la chiamata: impossibile da soddisfare senza toccare lo script del bot.
    # Il controllo giusto e': il documento cita la riga della chiamata vera.
    assert "scripts/gate_vs_paper.py:35-44" not in documento, (
        "il riferimento va spostato sulla riga che chiama davvero run_strategy")
    assert fatti.verifica_ancore(
        {"scripts/gate_vs_paper.py:215": "run_strategy("}, RADICE) == []
    assert "come fa `scripts/gate_vs_paper.py:215`" in documento


# --------------------------------------------------------------------------- #
# Controlli che reggono (regressione: devono restare verdi)                     #
# --------------------------------------------------------------------------- #
def test_nove_strategie_in_codice_come_dice_il_documento(documento):
    """Il documento dice «ce ne sono 9» e cita l'elenco degli import: il
    conteggio dei decoratori @register_strategy deve combaciare."""
    assert "ce ne sono 9" in documento
    n = 0
    for p in (RADICE / "bot" / "strategies").glob("*.py"):
        if p.name in ("base.py", "__init__.py"):
            continue
        n += sum(1 for l in p.read_text(encoding="utf-8").splitlines()
                 if l.startswith("@register_strategy"))
    assert n == 9


def test_le_affermazioni_negative_restano_vere():
    """«Non trovato» nel documento: workingType, marginType/ISOLATED/CROSSED,
    markPriceKlines/premiumIndexKlines, fundingIntervalHours. Zero occorrenze
    in bot/, backtesting/, scripts/ (file .py e .sh)."""
    parole = ("workingType", "marginType", "futures_change_margin_type",
              "ISOLATED", "CROSSED", "markPriceKlines", "premiumIndexKlines",
              "fundingIntervalHours")
    trovate: list[str] = []
    for cartella in ("bot", "backtesting", "scripts"):
        for p in (RADICE / cartella).rglob("*"):
            if p.suffix not in (".py", ".sh") or not p.is_file():
                continue
            testo = p.read_text(encoding="utf-8", errors="replace")
            for w in parole:
                if w in testo:
                    trovate.append(f"{p.relative_to(RADICE)}: {w}")
    assert trovate == []
