"""DIREZIONE x CONTESTO BTC nei referti (26 set 2026, backlog J7).

La domanda dell'audit: «short 54 trade, -44,95» (E1) vuol dire «short» o
«short con BTC su»? Qui si protegge la misura: il contesto viene SOLO da
`feats_at_entry.market_up` (mai inventato dagli indicatori della coin), ogni
trade cade in una casella sola, i conteggi sono per strategia e globali, e la
settima ipotesi `controtrend_btc` scatta al campione dichiarato (MIN_CAMPIONE
perdite contro il contesto, zero vinti contro) e non sotto. In discovery
diventa una figlia `conferma_trend` con l'etichetta del referto.
"""
import inspect

from bot.learning.referti import (CASELLE_CONTESTO, TIPI,
                                  aggrega_referti, casella_contesto,
                                  contesto_btc_del_trade, riassunto_ipotesi)


def _t(strat="gen_a", direction="long", pnl=-5.0, market_up=None, reason="stop_loss",
       **extra):
    t = {"strategy": strat, "symbol": "AUSDT", "direction": direction, "pnl": pnl,
         "exit_reason": reason}
    if market_up is not None:
        t["feats_at_entry"] = {"market_up": market_up, "rsi": 50.0}
    t.update(extra)
    return t


def _tipi(doc, strat="gen_a"):
    return [h["tipo"] for h in doc["ipotesi"] if h["strategia"] == strat]


# ---- il contesto di un trade ------------------------------------------------ #
def test_il_contesto_viene_solo_da_feats_at_entry():
    assert contesto_btc_del_trade(_t(market_up=1.0)) is True
    assert contesto_btc_del_trade(_t(market_up=0.0)) is False
    assert contesto_btc_del_trade(_t(market_up=True)) is True
    # trade vecchio: indicatori della coin, NON di BTC -> ignoto, non inventato
    assert contesto_btc_del_trade(_t(indicators_at_entry={"15m": {"ema_fast": 2, "ema_slow": 1}})) is None
    assert contesto_btc_del_trade(_t(feats_at_entry={"rsi": 50.0})) is None
    assert contesto_btc_del_trade(_t(feats_at_entry={"market_up": None})) is None
    assert contesto_btc_del_trade("non un dict") is None


def test_le_caselle():
    assert casella_contesto("long", True) == "long_con"
    assert casella_contesto("long", False) == "long_contro"
    assert casella_contesto("short", False) == "short_con"
    assert casella_contesto("short", True) == "short_contro"
    assert casella_contesto("long", None) == "ignoto"
    assert casella_contesto("?", True) == "ignoto"
    assert CASELLE_CONTESTO == ("long_con", "long_contro", "short_con", "short_contro", "ignoto")


# ---- il bucket per strategia e globale -------------------------------------- #
def test_per_contesto_conta_per_strategia_e_globale():
    trades = [_t(strat="gen_a", direction="short", pnl=-3.0, market_up=1.0),
              _t(strat="gen_a", direction="short", pnl=+2.0, market_up=0.0),
              _t(strat="gen_b", direction="long", pnl=+4.0, market_up=1.0),
              _t(strat="gen_b", direction="long", pnl=-1.0),            # ignoto
              _t(strat="gen_b", direction="long", pnl=-1.0, reason="manual", market_up=0.0)]
    doc = aggrega_referti(trades)
    pc = doc["per_contesto"]
    assert set(pc) == {"globale", "per_strategia"}
    g = pc["globale"]
    assert set(g) == set(CASELLE_CONTESTO)
    assert g["short_contro"] == {"trade": 1, "vinti": 0, "pnl": -3.0}
    assert g["short_con"] == {"trade": 1, "vinti": 1, "pnl": 2.0}
    assert g["long_con"] == {"trade": 1, "vinti": 1, "pnl": 4.0}
    assert g["long_contro"] == {"trade": 0, "vinti": 0, "pnl": 0.0}
    assert g["ignoto"] == {"trade": 1, "vinti": 0, "pnl": -1.0}     # il manual e' fuori
    assert pc["per_strategia"]["gen_a"]["short_contro"]["trade"] == 1
    assert pc["per_strategia"]["gen_b"]["ignoto"]["trade"] == 1
    assert list(pc["per_strategia"]) == ["gen_a", "gen_b"]
    # il contatore di servizio non finisce nel documento
    for b in list(pc["per_strategia"].values()) + [g]:
        for c in b.values():
            assert set(c) == {"trade", "vinti", "pnl"}


# ---- la settima ipotesi ----------------------------------------------------- #
def test_controtrend_btc_scatta_al_campione_minimo_non_sotto():
    """Long con BTC giu' e short con BTC su si sommano; con 2 e' ancora un caso."""
    persi = [_t(direction="long", market_up=0.0), _t(direction="short", market_up=1.0),
             _t(direction="long", market_up=0.0)]
    assert "controtrend_btc" not in _tipi(aggrega_referti(persi[:2]))
    doc = aggrega_referti(persi)
    assert _tipi(doc) == ["controtrend_btc"]
    h = doc["ipotesi"][0]
    assert h["campione"] == 3 and h["motivo"] == "3/3 persi contro il contesto BTC"
    assert riassunto_ipotesi(doc) == [
        "gen_a: controtrend_btc — 3/3 persi contro il contesto BTC (campione 3)"]


def test_controtrend_btc_non_scatta_con_un_vinto_contro_ne_con_le_perdite_a_favore():
    persi = [_t(direction="long", market_up=0.0) for _ in range(3)]
    assert _tipi(aggrega_referti(persi + [_t(direction="long", pnl=+1.0, market_up=0.0)])) == []
    # vinti A FAVORE non spengono l'ipotesi: la regola guarda solo il lato contro
    doc = aggrega_referti(persi + [_t(direction="long", pnl=+1.0, market_up=1.0)])
    assert _tipi(doc) == ["controtrend_btc"]
    assert doc["ipotesi"][0]["motivo"] == "3/3 persi contro il contesto BTC"
    # tre perdite A FAVORE del contesto: nessuna ipotesi (e nessun solo_short: 3
    # long persi lo farebbero scattare, per questo qui i vinti)
    con = [_t(direction="long", market_up=1.0) for _ in range(3)]
    assert "controtrend_btc" not in _tipi(aggrega_referti(con))


def test_controtrend_btc_ignora_i_trade_senza_contesto_e_i_pareggi():
    """Trade vecchi (ignoto) non contano ne' come contro ne' come a favore; un
    pareggio contro non e' una perdita."""
    doc = aggrega_referti([_t(direction="long") for _ in range(3)]
                          + [_t(direction="long", pnl=0.0, market_up=0.0)])
    assert "controtrend_btc" not in _tipi(doc)
    doc = aggrega_referti([_t(direction="long", market_up=0.0) for _ in range(3)]
                          + [_t(direction="long", pnl=0.0, market_up=0.0)])
    assert doc["ipotesi"][0]["motivo"] == "3/4 persi contro il contesto BTC"


def test_controtrend_btc_convive_con_le_altre_e_ordine_deterministico():
    trades = ([_t(direction="short", market_up=1.0, entry_ts=10.0 + i) for i in range(3)]
              + [_t(strat="gen_b", direction="long", pnl=+1.0, market_up=0.0)])
    d1, d2 = aggrega_referti(trades), aggrega_referti(list(reversed(trades)))
    assert d1 == d2
    assert [(h["strategia"], h["tipo"]) for h in d1["ipotesi"]] == [
        ("gen_a", "controtrend_btc"), ("gen_a", "solo_long")]
    assert all(h["da_ts"] == 10.0 for h in d1["ipotesi"])
    assert "controtrend_btc" in TIPI and TIPI.index("controtrend_btc") == len(TIPI) - 1


def test_documento_vuoto_ha_per_contesto():
    doc = aggrega_referti([])
    assert doc["per_contesto"] == {"globale": {c: {"trade": 0, "vinti": 0, "pnl": 0.0}
                                               for c in CASELLE_CONTESTO},
                                   "per_strategia": {}}


# ---- la discovery: figlia conferma_trend con l'etichetta del referto -------- #
def test_la_discovery_prova_controtrend_btc_come_conferma_trend():
    from scripts import discover_strategies as d
    from bot.strategies.generated import spec_id

    spec = {"features": [{"kind": "rsi_extreme", "low": 30.0, "high": 70.0}],
            "volume_mult": 0.0, "min_adx": 0.0, "atr_mult_stop": 1.5, "rr": 2.0}
    spec["id"] = spec_id(spec)
    doc = {"ipotesi": [{"strategia": spec["id"], "tipo": "controtrend_btc",
                        "motivo": "3/3 persi contro il contesto BTC", "campione": 3}]}
    esiti = {}
    out = d.varianti_dai_referti(None, {spec["id"]: spec}, d.settings.ORCHESTRATOR_TIMEFRAME,
                                 doc=doc, esiti=esiti)
    assert len(out) == 1
    figlia = out[0]
    assert [f["kind"] for f in figlia["features"]] == ["rsi_extreme", "htf_confirm"]
    assert figlia["ipotesi"] == "controtrend_btc" and figlia["genitore"] == spec["id"]
    assert figlia["origine"] == "referto"
    assert esiti == {f"{spec['id']}|controtrend_btc": ("variante_creata", figlia["id"])}
    # la stessa figlia di conferma_trend: una sola in coda, ma entrambe le voci
    # della storia sanno di lei
    doc["ipotesi"].append({"strategia": spec["id"], "tipo": "conferma_trend",
                           "motivo": "3 perdite controtrend", "campione": 3})
    esiti = {}
    out2 = d.varianti_dai_referti(None, {spec["id"]: spec}, d.settings.ORCHESTRATOR_TIMEFRAME,
                                  doc=doc, esiti=esiti)
    assert len(out2) == 1
    assert set(esiti) == {f"{spec['id']}|controtrend_btc", f"{spec['id']}|conferma_trend"}
    assert {v[1] for v in esiti.values()} == {out2[0]["id"]}
    src = inspect.getsource(d.varianti_dai_referti)
    assert 'if tipo == "controtrend_btc":' in src and 'tipo = "conferma_trend"' in src


# ---- trades stampa la tabella ----------------------------------------------- #
def test_trade_stats_stampa_direzione_per_contesto(monkeypatch, capsys):
    from scripts import trade_stats

    class _FakeFB:
        def query_collection(self, *a, **k):
            return ([_t(strat="gen_x", direction="short", exit_ts=1.0 + i, entry_ts=0.5,
                        market_up=1.0) for i in range(3)]
                    + [_t(strat="gen_x", direction="long", pnl=+2.0, exit_ts=9.0, entry_ts=0.5)])

    monkeypatch.setattr(trade_stats, "get_firebase", lambda: _FakeFB())
    assert trade_stats.main() == 0
    out = capsys.readouterr().out
    assert "DIREZIONE x CONTESTO BTC" in out
    riga = next(r for r in out.splitlines() if r.strip().startswith("tutte"))
    assert "0/3 -15.00" in riga and riga.rstrip().endswith("1")      # 1 ignoto
    assert "gen_x: controtrend_btc — 3/3 persi contro il contesto BTC (campione 3)" in out


def test_trade_stats_senza_contesto_lo_dice(monkeypatch, capsys):
    from scripts import trade_stats

    class _FakeFB:
        def query_collection(self, *a, **k):
            return [_t(strat="gen_x", exit_ts=1.0, entry_ts=0.5)]

    monkeypatch.setattr(trade_stats, "get_firebase", lambda: _FakeFB())
    assert trade_stats.main() == 0
    out = capsys.readouterr().out
    assert "nessun trade con il contesto BTC noto (1 ignoti" in out
