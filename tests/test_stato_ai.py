"""UN COMANDO PER SAPERE SE L'AI STA LAVORANDO.

Il 19 settembre sono serviti TRE comandi diversi e la lettura incrociata dei loro
log per scoprire che l'AI era ferma da sei giorni. Una diagnosi che costa cosi'
tanto non viene rifatta: e infatti non era stata rifatta per sei giorni.

Questo file protegge le proprieta' che rendono quella diagnosi affidabile — cioe'
le tre che oggi sono mancate tutte insieme.
"""
import inspect

from scripts import ai_status


class _Fb:
    def __init__(self, docs=None, righe=None):
        self.docs = docs or {}
        self.righe = righe or []

    def get_doc(self, coll, doc):
        return self.docs.get((coll, doc), {})

    def query_collection(self, coll, *a, **k):
        return self.righe if coll == "ai_shadow" else []


def test_la_chiave_si_prova_chiamando_davvero():
    """«Configurata» e «funzionante» non sono la stessa cosa: la chiave del 19
    settembre era configurata E rifiutata da sei giorni, e qualunque controllo che
    si fermasse a `if ANTHROPIC_API_KEY:` avrebbe detto che andava tutto bene."""
    src = inspect.getsource(ai_status.prova_chiave)
    assert "messages.create" in src
    assert "max_tokens=5" in src, "la prova deve costare una frazione di centesimo"


def test_l_errore_della_chiave_non_viene_troncato():
    """«401 invalid x-api-key» e «400 not scoped to a workspace» hanno lo stesso
    sintomo visibile e cause opposte. Oggi troncare il messaggio e' bastato a far
    sembrare rotta una chiave buona: qui il testo esce intero."""
    src = inspect.getsource(ai_status.prova_chiave)
    assert "{exc}" in src and "str(exc)[:" not in src


def test_la_chiave_usa_le_intestazioni_condivise():
    src = inspect.getsource(ai_status.prova_chiave)
    assert "default_headers=_headers()" in src


def test_le_proposte_si_riconoscono_dal_meccanismo():
    """Le spec dell'AI e quelle casuali hanno lo stesso tipo di id, di proposito
    («niente corsie preferenziali»). L'unica traccia e' `mechanism`: se questo
    controllo guardasse un altro campo direbbe sempre zero, e leggeremmo «l'AI non
    propone» mentre propone."""
    fb = _Fb(docs={("discovered_strategies", "specs"): {"specs": {
        "gen_a": {"features": [], "mechanism": "ritorno alla media dopo uno spike"},
        "gen_b": {"features": []},
    }}})
    righe = _cattura(lambda: ai_status.stato_proposte(fb))
    assert "1 spec con un meccanismo dichiarato su 2" in righe


def test_senza_proposte_lo_dice_invece_di_tacere():
    fb = _Fb(docs={("discovered_strategies", "specs"): {"specs": {
        "gen_b": {"features": []}}}})
    righe = _cattura(lambda: ai_status.stato_proposte(fb))
    assert "nessuna spec motivata" in righe


def test_l_ombra_vuota_spiega_perche_puo_essere_normale():
    """Zero decisioni in ombra puo' voler dire «e' rotto» o «il bot e' ripartito da
    dieci minuti». Dare il primo verdetto quando vale il secondo manderebbe a
    caccia di un guasto che non c'e' — e' successo oggi."""
    righe = _cattura(lambda: ai_status.stato_ombra(_Fb()))
    assert "nessuna decisione registrata" in righe
    assert "ripartito da poco" in righe


def test_le_prove_mostrate_sono_quelle_davvero_mandate():
    """Se questo script stampasse un riassunto SUO delle prove, verificheremmo un
    testo che non arriva a nessuno. Deve chiamare la stessa funzione della
    discovery — la lezione della sonda che contava su un timeframe diverso da
    quello su cui gira il bot."""
    src = inspect.getsource(ai_status.stato_prove)
    assert "prove_dal_paper" in src and "scala_dal_paper" in src


def test_un_guasto_di_firebase_non_fa_cadere_la_diagnosi():
    """Una diagnosi che muore quando qualcosa non va e' inutile proprio quando
    serve."""
    class _Rotto:
        def get_doc(self, *a, **k):
            raise RuntimeError("giu'")

        def query_collection(self, *a, **k):
            raise RuntimeError("giu'")

    assert "non leggibile" in _cattura(lambda: ai_status.stato_ombra(_Rotto()))
    assert "non leggibile" in _cattura(lambda: ai_status.stato_proposte(_Rotto()))


def test_e_sola_lettura():
    """Una diagnosi che modifica lo stato non e' una diagnosi. Nessuna scrittura,
    in nessuna funzione."""
    src = inspect.getsource(ai_status)
    for vietato in ("set_doc(", "set_rtdb(", "delete"):
        assert vietato not in src, f"ai_status scrive: {vietato}"


def test_ricorda_che_l_ai_non_decide_i_trade():
    """Chi legge questa schermata fra sei mesi deve trovarci il confine, non
    doverlo ricostruire."""
    assert "NON decide i trade" in inspect.getsource(ai_status.main)


def _cattura(fn) -> str:
    import contextlib
    import io

    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        fn()
    return buf.getvalue()
