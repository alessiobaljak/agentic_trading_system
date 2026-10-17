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
    assert "di origine AI fra quelle che hanno passato il gate: 1 su 2" in righe


def test_zero_spec_AI_nel_gate_non_e_un_allarme():
    """IL FALSO ALLARME DEL 20 SETTEMBRE. Il validatore aveva appena accettato 20
    proposte su 20 e il registro diceva «0 su 416»: il messaggio concludeva «l'AI
    non ha girato, oppure le proposte non vengono salvate». Sbagliato due volte —
    la verita' era la terza, non contemplata: le proposte erano appena state
    accettate e non avevano ancora avuto un giro per passare il gate, dove passa
    lo 0,25% delle valutazioni."""
    fb = _Fb(docs={("discovered_strategies", "specs"): {"specs": {
        "gen_b": {"features": []}}}})
    righe = _cattura(lambda: ai_status.stato_proposte(fb))
    assert "normale finche' le proposte AI sono poche o recenti" in righe
    assert "non ha girato" not in righe


def test_proporre_e_passare_il_gate_sono_DUE_righe_diverse():
    """Confonderle e' cio' che ha prodotto il falso allarme: la prima dice se l'AI
    lavora (subito), la seconda se il suo lavoro regge (settimane)."""
    fb = _Fb(docs={
        ("ai_hypotheses", "last"): {"proposte": 20, "accettate": 20,
                                    "motivi": {}, "at": 1.0},
        ("discovered_strategies", "specs"): {"specs": {"gen_b": {"features": []}}}})
    righe = _cattura(lambda: ai_status.stato_proposte(fb))
    assert "20/20 accettate dal validatore" in righe
    assert "di origine AI fra quelle che hanno passato il gate: 0 su 1" in righe


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
    assert "non leggibili" in _cattura(lambda: ai_status.stato_proposte(_Rotto()))


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


# ---- l'ombra: contare con la chiave che si scrive (25 set 2026) ------------ #
def _decisione(choice, actual, at=1.0):
    """Un documento `ai_shadow` come lo scrive bot/main.py: verdetto calcolato
    dalla STESSA `compare` di produzione, non ricopiato a mano nel test."""
    from bot.ai.shadow import compare
    return {"choice": choice, "actual": actual,
            "verdict": compare({"choice": choice}, actual), "at": at}


def test_l_accordo_si_conta_con_la_chiave_che_scrive_compare():
    """IL FALSO ZERO DEL 25 SETTEMBRE. Qui si contava «accordo», `compare`
    scrive «agree»: «d'accordo col bot 0/60» da giorni, indistinguibile da un
    vero zero. Due accordi su tre cicli con trade aperto devono uscire 2/3."""
    righe = [_decisione("BTCUSDT|breakout", "BTCUSDT|breakout"),
             _decisione("ETHUSDT|momentum", "ETHUSDT|momentum"),
             _decisione("BTCUSDT|breakout", "ETHUSDT|momentum"),
             _decisione("BTCUSDT|breakout", None),
             _decisione(None, None)]
    out = _cattura(lambda: ai_status.stato_ombra(_Fb(righe=righe)))
    assert "d'accordo col bot 2/3 volte" in out
    assert "0/5" not in out


def test_la_chiave_dell_accordo_non_e_ricopiata_a_mano():
    """Se `compare` cambiasse parola, il contatore deve seguirla da solo:
    la chiave si chiede a `compare`, non si scrive come stringa."""
    from bot.ai.shadow import compare
    assert ai_status._ACCORDO == compare({"choice": "x"}, "x")
    src = inspect.getsource(ai_status.stato_ombra)
    assert '"accordo"' not in src and '"agree"' not in src


def test_l_ombra_dice_in_quanti_cicli_il_bot_aveva_un_trade():
    """Senza un trade aperto dal bot nello stesso ciclo l'ombra non puo' essere
    «d'accordo»: un 0/60 con 57 cicli fermi e' uno 0/3, ed e' un'altra notizia."""
    righe = [_decisione("BTCUSDT|breakout", None) for _ in range(4)] + \
            [_decisione(None, "ETHUSDT|momentum")]
    out = _cattura(lambda: ai_status.stato_ombra(_Fb(righe=righe)))
    assert "trade aperto nello stesso ciclo in 1 decisioni, in 4 no" in out
    assert "d'accordo col bot 0/1 volte" in out


def test_senza_trade_aperti_l_accordo_e_non_misurabile_non_zero():
    """Se il bot non ha mai aperto nei cicli dell'ombra, «0/N» sarebbe una
    bugia: il numero giusto e' «non misurabile»."""
    righe = [_decisione("BTCUSDT|breakout", None), _decisione(None, None)]
    out = _cattura(lambda: ai_status.stato_ombra(_Fb(righe=righe)))
    assert "non misurabile" in out
    assert "d'accordo col bot 0/" not in out


def test_ogni_esito_di_compare_ha_una_spiegazione():
    """La riga degli esiti stampa la chiave grezza di Firebase con una glossa:
    tutti e cinque i casi di `compare` devono averla, cosi' nessuno deve
    riaprire shadow.py per leggere la schermata."""
    from bot.ai.shadow import compare
    casi = [("x", "x"), ("x", "y"), ("x", None), (None, "x"), (None, None)]
    for choice, actual in casi:
        assert compare({"choice": choice}, actual) in ai_status._ESITI
    righe = [_decisione("BTCUSDT|breakout", None) for _ in range(3)]
    out = _cattura(lambda: ai_status.stato_ombra(_Fb(righe=righe)))
    assert "shadow_only ×3: avrebbe operato, il bot no" in out
