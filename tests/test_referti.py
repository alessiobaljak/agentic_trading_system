"""REFERTI AGGREGATI — dai post_mortem alle ipotesi per il gate.

Cosa si protegge: le regole sono DICHIARATE (costanti) e scattano esattamente al
campione minimo, non sotto; gli esiti esterni (manual/kill_switch/circuit_breaker)
non contano; i rilievi si contano solo sui trade in perdita con referto; le
ipotesi per direzione non hanno bisogno del referto; l'ordine e' deterministico
(la discovery confronta il documento fra un giro e l'altro). Il paper PROPONE:
questo modulo non deve mai toccare un parametro (backlog F1/B8).
"""
import inspect

from bot.learning.referti import (ESITI_ESTERNI, MIN_CAMPIONE, MIN_STOP_LARGO,
                                  aggrega_referti, riassunto_ipotesi)


def _t(strat="gen_a", sym="AUSDT", direction="long", pnl=-5.0, reason="stop_loss",
       pm=None, **extra):
    t = {"strategy": strat, "symbol": sym, "direction": direction, "pnl": pnl,
         "exit_reason": reason}
    if pm is not None:
        t["post_mortem"] = pm
    t.update(extra)
    return t


def _pm(classe="uscita", stop_largo=False, lock_mai=False, contro=None):
    return {"classe": classe, "stop_largo": stop_largo,
            "lock_mai_armato": lock_mai, "controtrend": contro,
            "verdetto": "x"}


def _tipi(doc, strat="gen_a"):
    return [h["tipo"] for h in doc["ipotesi"] if h["strategia"] == strat]


# ---- le costanti sono quelle dichiarate ------------------------------------ #
def test_le_soglie_sono_dichiarate_e_non_tarate():
    assert MIN_CAMPIONE == 3 and MIN_STOP_LARGO == 2
    assert ESITI_ESTERNI == {"manual", "kill_switch", "circuit_breaker"}


# ---- solo_long / solo_short ------------------------------------------------- #
def test_solo_long_scatta_al_campione_minimo_non_sotto():
    """3 short tutti persi -> solo_long; con 2 e' ancora rumore."""
    doc = aggrega_referti([_t(direction="short") for _ in range(2)])
    assert _tipi(doc) == []
    doc = aggrega_referti([_t(direction="short") for _ in range(3)])
    assert _tipi(doc) == ["solo_long"]
    h = doc["ipotesi"][0]
    assert h["campione"] == 3 and h["motivo"] == "short 3/3 persi"


def test_solo_long_non_scatta_se_uno_short_ha_vinto():
    doc = aggrega_referti([_t(direction="short") for _ in range(4)]
                          + [_t(direction="short", pnl=+1.0)])
    assert _tipi(doc) == []


def test_solo_short_specchio_e_direzione_case_insensitive():
    """Il campo direction arriva anche come 'LONG' (enum serializzato)."""
    doc = aggrega_referti([_t(direction="LONG") for _ in range(3)])
    assert _tipi(doc) == ["solo_short"]
    assert doc["per_direzione"]["long"]["n"] == 3
    assert doc["per_strategia"]["gen_a"]["long_n"] == 3


def test_ipotesi_per_direzione_senza_referto():
    """Bastano pnl e direzione: scattano anche sui trade chiusi prima del 23 set."""
    doc = aggrega_referti([_t(direction="short") for _ in range(3)])
    assert doc["n_con_referto"] == 0
    assert _tipi(doc) == ["solo_long"]


def test_pnl_zero_non_e_ne_vinto_ne_perso():
    doc = aggrega_referti([_t(direction="short", pnl=0.0) for _ in range(3)])
    b = doc["per_strategia"]["gen_a"]
    assert b["n"] == 3 and b["vinti"] == 0 and b["persi"] == 0
    assert b["short_n"] == 3 and b["short_persi"] == 0
    # tre pareggi NON sono tre perdite: la regola chiede MIN_CAMPIONE perdite
    # vere, non «nessun vinto» (altrimenti il motivo direbbe «3/3 persi»)
    assert _tipi(doc) == []
    doc = aggrega_referti([_t(direction="short", pnl=0.0)]
                          + [_t(direction="short") for _ in range(3)])
    assert [h["motivo"] for h in doc["ipotesi"]] == ["short 3/4 persi"]


def test_trade_senza_strategia_non_propone():
    doc = aggrega_referti([_t(strat="") for _ in range(3)]
                          + [_t(strat=None, direction="short") for _ in range(3)])
    assert doc["per_strategia"]["?"]["n"] == 6
    assert doc["ipotesi"] == []


# ---- conferma_trend --------------------------------------------------------- #
def test_conferma_trend_da_perdite_controtrend():
    persi = _misti(3, pm=_pm(contro=True))
    vinti = [_t(pnl=+3.0, pm=_pm(contro=True))]      # il vinto non conta come rilievo
    doc = aggrega_referti(persi + vinti)
    assert doc["per_strategia"]["gen_a"]["controtrend"] == 3
    assert _tipi(doc) == ["conferma_trend"]
    assert doc["ipotesi"][0]["campione"] == 3
    doc2 = aggrega_referti(persi[:2] + vinti)
    assert _tipi(doc2) == []


def _misti(n, **kw):
    """n trade a direzioni alternate: cosi' nessuna delle due arriva a
    MIN_CAMPIONE e non scattano le ipotesi per direzione."""
    return [_t(direction=("long", "short")[i % 2], **kw) for i in range(n)]


def test_conferma_trend_da_classe_ingresso_solo_se_zero_vinti():
    persi = _misti(3, pm=_pm(classe="ingresso"))
    assert _tipi(aggrega_referti(persi)) == ["conferma_trend"]
    # un vinto qualsiasi spegne la variante «ingresso»: la strategia sa vincere
    assert _tipi(aggrega_referti(persi + [_t(pnl=+2.0)])) == []


def test_una_sola_ipotesi_conferma_trend_per_strategia():
    """Entrambe le condizioni vere -> una sola voce (strategia, tipo)."""
    persi = _misti(3, pm=_pm(classe="ingresso", contro=True))
    doc = aggrega_referti(persi)
    assert _tipi(doc) == ["conferma_trend"]


# ---- stop_stretto ----------------------------------------------------------- #
def test_stop_stretto_scatta_a_due_stop_larghi_in_perdita():
    doc = aggrega_referti([_t(pm=_pm(stop_largo=True))])
    assert _tipi(doc) == []
    doc = aggrega_referti([_t(pm=_pm(stop_largo=True)) for _ in range(2)])
    assert _tipi(doc) == ["stop_stretto"]
    assert doc["ipotesi"][0]["campione"] == 2


def test_stop_largo_su_trade_vinto_non_conta():
    doc = aggrega_referti([_t(pnl=+1.0, pm=_pm(stop_largo=True)) for _ in range(3)])
    assert doc["per_strategia"]["gen_a"]["stop_largo"] == 0
    assert _tipi(doc) == []


# ---- esclusioni e bucket ---------------------------------------------------- #
def test_esiti_esterni_esclusi():
    """Un kill switch non dice nulla sull'edge della strategia."""
    trades = [_t(direction="short", reason=r) for r in ESITI_ESTERNI]
    trades += [_t(direction="short") for _ in range(2)]
    doc = aggrega_referti(trades)
    assert doc["n_trades"] == 2
    assert _tipi(doc) == []            # 2 short, non 5


def test_bucket_per_coin_e_direzione():
    trades = [_t(sym="AUSDT", direction="long", pnl=+4.0, pm=_pm()),
              _t(sym="AUSDT", direction="short", pnl=-2.0, pm=_pm(lock_mai=True)),
              _t(sym="BUSDT", direction="short", pnl=-3.0, pm=_pm(classe="protezione"))]
    doc = aggrega_referti(trades)
    a = doc["per_coin"]["AUSDT"]
    assert (a["n"], a["vinti"], a["persi"], a["pnl"]) == (2, 1, 1, 2.0)
    assert a["long_n"] == 1 and a["long_vinti"] == 1 and a["short_n"] == 1
    assert a["lock_mai"] == 1 and a["uscita"] == 1     # solo il perso porta rilievi
    s = doc["per_direzione"]["short"]
    assert s["n"] == 2 and s["persi"] == 2 and s["protezione"] == 1
    assert doc["per_direzione"]["long"]["n"] == 1
    assert doc["n_con_referto"] == 3 and doc["n_persi_con_referto"] == 2


def test_trade_senza_post_mortem_contano_ma_senza_rilievi():
    doc = aggrega_referti([_t(), _t(pm="non un dict"), _t(pm=_pm(classe="ingresso"))])
    b = doc["per_strategia"]["gen_a"]
    assert b["n"] == 3 and b["persi"] == 3 and b["ingresso"] == 1
    assert doc["n_con_referto"] == 1


def test_ordine_deterministico():
    """La discovery confronta il documento fra un giro e l'altro: stessa lista,
    stesso ordine, qualunque sia l'ordine dei trade in ingresso."""
    trades = ([_t(strat="gen_b", direction="short") for _ in range(3)]
              + [_t(strat="gen_a", pm=_pm(stop_largo=True)) for _ in range(2)]
              + [_t(strat="gen_a", direction="short") for _ in range(3)])
    d1 = aggrega_referti(trades)
    d2 = aggrega_referti(list(reversed(trades)))
    assert d1 == d2
    assert [(h["strategia"], h["tipo"]) for h in d1["ipotesi"]] == [
        ("gen_a", "solo_long"), ("gen_a", "stop_stretto"), ("gen_b", "solo_long")]
    assert list(d1["per_strategia"]) == ["gen_a", "gen_b"]


def test_documento_vuoto():
    doc = aggrega_referti([])
    assert doc["n_trades"] == 0 and doc["ipotesi"] == []
    assert set(doc["per_direzione"]) == {"long", "short"}
    assert riassunto_ipotesi(doc) == [] and riassunto_ipotesi(None) == []


def test_riassunto_ipotesi_leggibile():
    doc = aggrega_referti([_t(strat="gen_ba3a671f", direction="short") for _ in range(4)])
    assert riassunto_ipotesi(doc) == [
        "gen_ba3a671f: solo_long — short 4/4 persi (campione 4)"]


# ---- il bot pubblica, trades stampa ----------------------------------------- #
def test_il_bot_pubblica_learning_referti_senza_toccare_parametri():
    from bot import main as bot_main
    src = inspect.getsource(bot_main.TradingBot._publish_referti)
    assert 'set_doc("learning", "referti"' in src
    assert "self.adaptation" not in src           # propone, non applica
    rw = inspect.getsource(bot_main.TradingBot.refresh_weights)
    assert "self._publish_referti(trades)" in rw


def test_trade_stats_stampa_ipotesi_anche_senza_referto(monkeypatch, capsys):
    """8 giorni di paper prima del 23 set: nessun post_mortem, ma le ipotesi per
    direzione devono comparire lo stesso."""
    from scripts import trade_stats

    class _FakeFB:
        def query_collection(self, *a, **k):
            return [_t(strat="gen_x", direction="short", exit_ts=1.0 + i,
                       entry_ts=0.5) for i in range(3)]

    monkeypatch.setattr(trade_stats, "get_firebase", lambda: _FakeFB())
    assert trade_stats.main() == 0
    out = capsys.readouterr().out
    assert "nessun trade porta ancora `post_mortem`" in out
    assert "IPOTESI DAI REFERTI" in out
    assert "gen_x: solo_long — short 3/3 persi (campione 3)" in out


def test_trade_stats_tabella_per_strategia(monkeypatch, capsys):
    from scripts import trade_stats

    class _FakeFB:
        def query_collection(self, *a, **k):
            return [_t(strat="gen_y", exit_ts=10.0 + i, entry_ts=1.0,
                       pm=_pm(stop_largo=True)) for i in range(2)]

    monkeypatch.setattr(trade_stats, "get_firebase", lambda: _FakeFB())
    assert trade_stats.main() == 0
    out = capsys.readouterr().out
    assert "PER STRATEGIA (trade in perdita con referto)" in out
    assert "stop troppo largo        x2" in out
    assert "gen_y: stop_stretto — 2 perdite con stop troppo largo (campione 2)" in out
