"""Configurazione comune dei test di ``research/src/`` (``campagne/GRUPPO/regole.md``, sezione 11, punto 6, e sezione 13).

I test girano sempre SENZA marcatore di campagna, anche quando li lancia una sessione di campagna, che ha il
marcatore vero in ``research/.sessione`` (la frase della sezione 11, punto 6, di regole.md le chiede di
«rilanciare i test di research/src/tests/»). ``dati.py`` cerca il marcatore in ``dati.RADICE_PROGETTO`` (e
``gruppo.py`` lo legge da li'): senza questa fixture, con un marcatore vero, i rifiuti voluti in campagna
(lista dei contratti, indice dell'archivio, simboli fuori dall'elenco, argomenti dei test di ``gruppo.py``)
farebbero fallire test che non c'entrano, e una sessione potrebbe credere che ``src/`` sia rotto.

La fixture e' di sessione e automatica: gira prima delle fixture di modulo (come ``esame_tre`` di
``test_gruppo_esecutore.py``) e punta ``dati.RADICE_PROGETTO`` a una cartella vuota per tutta la sessione dei
test, poi la rimette com'era. I test che simulano una sessione scrivono il loro marcatore in un progetto finto
(le fixture ``progetto`` dei singoli file). Vale solo nel processo dei test: i processi del gruppo di
``gruppo.py`` (``processi`` > 1) ricevono dal processo che avvia l'esame se c'e' un marcatore di campagna, e
rileggono il marcatore vero solo dentro le funzioni di ``dati`` (i test con piu' processi usano dati in memoria).
Il guardiano non usa ``dati.RADICE_PROGETTO``: i suoi test non cambiano.
"""

import pytest

from research.src import dati


@pytest.fixture(scope="session", autouse=True)
def progetto_senza_marcatore(tmp_path_factory):
    """``dati.RADICE_PROGETTO`` punta a un progetto vuoto, senza marcatore, per tutta la sessione dei test."""
    vera = dati.RADICE_PROGETTO
    dati.RADICE_PROGETTO = tmp_path_factory.mktemp("progetto_senza_marcatore")
    try:
        yield dati.RADICE_PROGETTO
    finally:
        dati.RADICE_PROGETTO = vera
