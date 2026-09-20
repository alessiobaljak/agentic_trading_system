"""PERCHE' UNA PROPOSTA DELL'AI VIENE SCARTATA — il motivo, non solo il conteggio.

Primo giro col livello AI riacceso, 19 settembre, ore 20:38: il modello ha proposto
20 strategie e il log ha detto

    [ai-hypotheses] 19/20 proposte scartate (fuori vocabolario)

Il 95% buttato, e nessun modo di sapere QUALE regola le fermasse: feature inventate?
troppe? parametri fuori fascia? combinazioni vietate? Con quel messaggio l'unica
mossa possibile era cambiare il prompt a caso e risperare — mentre le correzioni
sono diverse per ogni causa. E' lo stesso buco che il gate aveva prima
dell'autopsia: si contavano i morti senza sapere di cosa.

Una cosa che questi test NON fanno: cambiare la severita' del filtro. Stringerlo o
allentarlo mentre si misura renderebbe il prossimo giro non confrontabile con
questo, e perderemmo proprio il dato per cui la diagnostica e' stata aggiunta.
"""
from bot.ai import hypotheses as h


def _feat(kind: str) -> dict:
    """Una feature COMPLETA: ogni parametro obbligatorio riempito a meta' fascia.

    Scriverla a mano e' il modo di sbagliare: la prima versione di questo file
    usava `{"kind": "rsi_momentum"}` e veniva scartata perche' `mid` e'
    obbligatorio. Cioe' sono caduto nella stessa trappola del modello — che e'
    anche l'indizio piu' forte su cosa stia davvero fermando le sue proposte."""
    f = {"kind": kind}
    for nome, (lo, hi) in h._FEATURE_PARAMS.get(kind, {}).items():
        f[nome] = (lo + hi) / 2
    if kind == "session":
        f["hour_from"], f["hour_to"] = 8, 20
    return f


def _spec(**kw):
    base = {"mechanism": "prova", "features": [_feat("rsi_momentum")],
            "atr_mult_stop": 1.5, "rr": 2.0, "min_adx": 0.0, "volume_mult": 0.0}
    base.update(kw)
    return base


def _motivo(raw) -> str:
    return h._esamina_spec(raw)[1]


# --------------------------------------------------------------------------- #
# Ogni causa ha il SUO motivo, perche' ognuna si corregge in modo diverso      #
# --------------------------------------------------------------------------- #
def test_una_feature_inventata_viene_nominata():
    """La correzione e' ricordare al modello il vocabolario. Se il messaggio non
    dice il nome inventato non si sa nemmeno quale sia."""
    m = _motivo(_spec(features=[{"kind": "supercazzola_index"}]))
    assert "inesistente" in m and "supercazzola_index" in m


def test_un_parametro_mancante_dice_quale():
    """Correzione diversa: l'esempio nel prompt deve mostrare quel parametro."""
    m = _motivo(_spec(features=[{"kind": "rsi_extreme"}]))
    assert "manca il parametro" in m and "rsi_extreme" in m


def test_un_numero_fuori_fascia_dice_valore_e_fascia():
    """Correzione ancora diversa: dichiarare le fasce ammesse. Serve sapere sia
    quanto ha proposto sia quanto era permesso, altrimenti si tira a indovinare."""
    m = _motivo(_spec(rr=99.0))
    assert "rr=99" in m and "fuori dalla fascia" in m


def test_troppe_feature_dicono_quante():
    m = _motivo(_spec(features=[_feat("rsi_momentum"), _feat("macd_hist"),
                                _feat("ema_cross"), _feat("vwap_momentum")]))
    assert "troppe feature" in m and "4" in m


def test_la_stessa_feature_due_volte():
    m = _motivo(_spec(features=[_feat("rsi_momentum"), _feat("rsi_momentum")]))
    assert "ripetuta" in m


def test_senza_direzionale_lo_dice():
    m = _motivo(_spec(features=[_feat("volatility_regime")]))
    assert "direzionale" in m


def test_una_coppia_incompatibile_nomina_le_due_feature():
    """Sapere QUALI due si escludono e' l'unica informazione utile: l'elenco delle
    coppie vietate non e' nel prompt, e senza i nomi non si puo' aggiungerlo."""
    coppia = sorted(next(iter(h._INCOMPATIBLE)))
    m = _motivo(_spec(features=[_feat(k) for k in coppia]))
    assert "incompatibile" in m
    for k in coppia:
        assert k in m


def test_una_proposta_valida_non_ha_motivo():
    spec, motivo = h._esamina_spec(_spec())
    assert spec is not None and motivo == ""
    assert spec["mechanism"] == "prova"


# --------------------------------------------------------------------------- #
# La logica sta in UN posto solo                                              #
# --------------------------------------------------------------------------- #
def test_la_porta_vecchia_e_quella_nuova_non_possono_divergere():
    """`_clean_spec` resta per chi non vuole il motivo, ma deve passare di qui:
    due copie della stessa regola che si separano nel tempo sono il difetto piu'
    caro di questo progetto — ci e' gia' costato tre copie di `judge_window`."""
    for caso in (_spec(), _spec(rr=99.0), _spec(features=[{"kind": "boh"}]), 42):
        assert h._clean_spec(caso) == h._esamina_spec(caso)[0]
    for caso in (_feat("rsi_momentum"), {"kind": "boh"}, "non un dict"):
        assert h._clean_feature(caso) == h._esamina_feature(caso)[0]


def test_il_log_elenca_i_motivi_non_solo_il_numero():
    import inspect

    src = inspect.getsource(h.propose)
    assert "motivi.most_common" in src
    # il messaggio STAMPATO, non i commenti (che citano quello vecchio apposta)
    stampate = [r for r in src.splitlines() if "print(" in r or "dettaglio" in r]
    assert any("dettaglio" in r for r in stampate)
    assert not any("fuori vocabolario" in r for r in stampate)


def test_i_duplicati_sono_contati_a_parte():
    """Venti proposte che collassano sullo stesso id non sono venti errori di
    vocabolario: e' il modello che si ripete, e si corregge chiedendo varieta'.
    Confonderle manderebbe a sistemare il vocabolario per un problema che non c'e'."""
    import inspect

    assert "duplicata" in inspect.getsource(h.propose)


def test_una_proposta_che_non_e_un_oggetto_non_fa_esplodere_niente():
    """Il modello puo' rispondere con una lista di stringhe: deve diventare uno
    scarto contato, non un'eccezione che porta giu' il giro di discovery."""
    assert h._esamina_spec("stringa") == (None, "proposta non e' un oggetto")
    assert h._esamina_spec(None)[0] is None


# --------------------------------------------------------------------------- #
# L'esito sopravvive al log                                                   #
# --------------------------------------------------------------------------- #
def test_l_esito_dell_ultimo_giro_resta_disponibile():
    """IL DIFETTO DEL 20 SETTEMBRE. La diagnosi dei motivi c'era gia' e non e'
    stata leggibile lo stesso: il canale ops mostra le ultime 80 righe del
    journal, la discovery gira ogni tre ore e in mezzo l'ottimizzo ne scrive
    migliaia. Sei ore dopo, il motivo per cui il 95% delle proposte veniva buttato
    era scorso via — terza volta in due giorni che un'informazione esiste e non si
    riesce a raggiungerla."""
    from bot.config import settings

    prima = settings.ANTHROPIC_API_KEY
    settings.ANTHROPIC_API_KEY = ""          # `propose` esce subito, senza chiamate
    try:
        h.ULTIMO_ESITO.clear()
        assert h.propose(5) == []
        # senza chiave non si propone niente: l'esito resta vuoto, non finto
        assert not h.ULTIMO_ESITO
    finally:
        settings.ANTHROPIC_API_KEY = prima


def test_l_esito_registra_proposte_accettate_e_motivi(monkeypatch):
    """Il conteggio DEVE venire dalla stessa passata che accetta o scarta: due
    conteggi separati divergerebbero al primo caso di confine."""
    from bot.config import settings

    monkeypatch.setattr(settings, "ANTHROPIC_API_KEY", "finta")
    monkeypatch.setattr(settings, "AI_ENABLED", True)
    monkeypatch.setattr(h, "ask_json", lambda *a, **k: {"specs": [
        _spec(),                                   # buona
        _spec(rr=99.0),                            # numero fuori fascia
        _spec(features=[{"kind": "inventata"}]),   # feature inesistente
        _spec(features=[{"kind": "inventata"}]),   # stesso motivo, conta 2
    ]})
    h.ULTIMO_ESITO.clear()
    specs = h.propose(10)

    assert len(specs) == 1
    assert h.ULTIMO_ESITO["proposte"] == 4 and h.ULTIMO_ESITO["accettate"] == 1
    motivi = h.ULTIMO_ESITO["motivi"]
    assert sum(motivi.values()) == 3
    assert any("inesistente" in m and q == 2 for m, q in motivi.items())
    assert any("fuori dalla fascia" in m for m in motivi)


def test_la_discovery_salva_l_esito_e_ai_stato_lo_mostra():
    """Registrarlo in memoria e non salvarlo lascerebbe il problema identico: il
    processo della discovery muore a fine giro."""
    import inspect

    from scripts import ai_status
    from scripts import discover_strategies as d

    src = inspect.getsource(d.main)
    assert "ULTIMO_ESITO" in src and 'set_doc("ai_hypotheses", "last"' in src
    assert 'get_doc("ai_hypotheses", "last")' in inspect.getsource(ai_status.stato_proposte)
