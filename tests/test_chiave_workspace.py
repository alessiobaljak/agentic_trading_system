"""UNA CHIAVE VALIDA PUO' COMUNQUE NON FUNZIONARE, E L'ERRORE SEMBRA LO STESSO.

Il 19 settembre il livello AI era spento da sei giorni per una chiave rifiutata
(401, `invalid x-api-key`). Rimessa una chiave nuova, l'errore e' cambiato in:

    400 — «This API key is not scoped to a workspace, so this request must include
           the anthropic-workspace-id header»

Cioe': la chiave era BUONA. A colpo d'occhio nel log le due righe si somigliano —
entrambe finiscono con «-> proseguo senza AI» — e sarebbe stato facile concludere
«la chiave e' ancora sbagliata» e mandare il proprietario a rifarla per la seconda
volta. Due casi diversi con lo stesso sintomo visibile sono esattamente cio' che
questo progetto paga piu' caro.

Da qui `ANTHROPIC_WORKSPACE_ID`: vuoto per una chiave gia' legata a un workspace
(comportamento identico a prima), valorizzato per una chiave d'organizzazione.
"""
import inspect

from bot.ai import client as ai_client
from bot.config import settings


def test_senza_workspace_nessuna_intestazione_extra():
    """Il caso normale non deve cambiare di una virgola: una chiave legata a un
    workspace funziona da sola, e mandare un'intestazione vuota sarebbe un modo
    nuovo di rompere una cosa che funzionava."""
    prima = settings.ANTHROPIC_WORKSPACE_ID
    settings.ANTHROPIC_WORKSPACE_ID = ""
    try:
        assert ai_client._headers() == {}
    finally:
        settings.ANTHROPIC_WORKSPACE_ID = prima


def test_col_workspace_l_intestazione_viene_mandata():
    prima = settings.ANTHROPIC_WORKSPACE_ID
    settings.ANTHROPIC_WORKSPACE_ID = "wrkspc_123"
    try:
        assert ai_client._headers() == {"anthropic-workspace-id": "wrkspc_123"}
    finally:
        settings.ANTHROPIC_WORKSPACE_ID = prima


def test_spazi_accidentali_non_rompono_la_chiamata():
    """Il valore arriva da un `.env` compilato a mano: uno spazio in coda
    produrrebbe un'intestazione non valida e un errore che NON assomiglia alla sua
    causa. Si ripulisce qui, dove il costo e' una riga."""
    prima = settings.ANTHROPIC_WORKSPACE_ID
    settings.ANTHROPIC_WORKSPACE_ID = "  wrkspc_123  "
    try:
        assert ai_client._headers() == {"anthropic-workspace-id": "wrkspc_123"}
    finally:
        settings.ANTHROPIC_WORKSPACE_ID = prima


def test_solo_spazi_vale_come_vuoto():
    prima = settings.ANTHROPIC_WORKSPACE_ID
    settings.ANTHROPIC_WORKSPACE_ID = "   "
    try:
        assert ai_client._headers() == {}
    finally:
        settings.ANTHROPIC_WORKSPACE_ID = prima


def test_il_client_vero_usa_quelle_intestazioni():
    """Se `_headers()` esistesse ma nessuno la passasse al client, il test sopra
    sarebbe verde e il sistema continuerebbe a prendere 400."""
    src = inspect.getsource(ai_client.ask_json)
    assert "default_headers=_headers()" in src


def test_la_prova_di_connettivita_chiama_come_il_bot():
    """LA LEZIONE GIA' PAGATA OGGI, in un altro punto: la sonda sui segnali
    contava su candele da un'ora mentre il bot gira a quindici minuti, e rispondeva
    «tutto torna» a una domanda diversa da quella posta.

    Una prova della chiave che costruisse il client a modo suo direbbe FAIL quando
    il bot funziona, o OK quando il bot e' fermo. Deve usare le stesse
    intestazioni."""
    from scripts import connectivity_check

    src = inspect.getsource(connectivity_check.info_others)
    assert "from bot.ai.client import _headers" in src
    assert "default_headers=_headers()" in src


def test_il_parametro_e_documentato_dove_si_compila():
    """Chi mette la chiave legge `.env.example`, non il codice."""
    with open(".env.example", encoding="utf-8") as f:
        testo = f.read()
    assert "ANTHROPIC_WORKSPACE_ID" in testo
    assert "not scoped to a workspace" in testo
