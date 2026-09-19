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


def test_NESSUN_punto_costruisce_il_client_senza_le_intestazioni():
    """LA REGOLA GENERALE, dopo averla vista fallire due volte in un giorno.

    `bot/ai/client.py` e' «l'unico punto da cui il sistema parla con un modello» —
    lo dice la sua docstring — ma non era vero: orchestratore, ciclo di
    apprendimento notturno e i due script di verifica costruivano il client da
    soli. Finche' non serviva niente di speciale la differenza non si vedeva; il
    giorno in cui e' servita un'intestazione, quei quattro punti avrebbero preso
    400 mentre il resto funzionava — e il sintomo sarebbe stato «l'AI a volte si',
    a volte no».

    Questo test non chiede di passare per `ask_json` (la narrativa settimanale
    vuole testo libero, non JSON): chiede che CHIUNQUE costruisca un client usi le
    stesse intestazioni.
    """
    import pathlib
    import re

    radice = pathlib.Path(".")
    colpevoli = []
    for f in list(radice.glob("bot/**/*.py")) + list(radice.glob("scripts/*.py")):
        testo = f.read_text(encoding="utf-8")
        for m in re.finditer(r"anthropic\.Anthropic\((.*?)\)", testo, re.S):
            if "default_headers" not in m.group(1):
                colpevoli.append(f"{f}: {m.group(0)[:70]}")
    assert not colpevoli, (
        "client costruiti senza le intestazioni condivise:\n" + "\n".join(colpevoli))


def test_il_controllo_nomina_cio_che_e_rotto():
    """Il 19 settembre `connectivity_check` ha stampato «RISULTATO: GitHub <->
    Firebase OK ✅» mentre la chiave Anthropic era morta da sei giorni, e il
    workflow mostrava il pallino verde. Chi guarda l'ultima riga — o la lista dei
    workflow — vedeva un sistema sano.

    Il codice d'uscita resta legato a Firebase, che e' il contratto di questo
    controllo e non va cambiato di nascosto. Ma cio' che e' rotto dev'essere
    NOMINATO nel riepilogo, non lasciato a chi scorre venti righe all'indietro."""
    import inspect

    from scripts import connectivity_check as cc

    src = inspect.getsource(cc.main)
    assert "_FALLITI" in src and "controlli FALLITI" in src
    assert "_FALLITI.append" in inspect.getsource(cc._line)
