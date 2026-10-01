"""LE FUNZIONI SERVONO? (1 ott 2026): il confronto d'esito per funzione, i USDT
risparmiati dalle riduzioni di size, l'ombra AI legata ai trade, l'origine."""
import scripts.trade_stats as ts
from bot.learning import contributi as c


def _t(r, **kw):
    """Un trade con R = r (entry 10, stop originale 9, size 1)."""
    t = {"entry_price": 10.0, "orig_stop": 9.0, "size": 1.0, "pnl": float(r),
         "direction": "long", "strategy": kw.pop("strategy", "gen_a")}
    t.update(kw)
    return t


def test_confronto_regola():
    assert c.confronto([0.1] * 5, [0.0] * 20, "meglio")["verdetto"] == "campione piccolo"
    buoni = [1.0, 1.2, 0.8, 1.1, 0.9] * 4
    zero = [0.1, -0.1, 0.0, 0.05, -0.05] * 4
    assert c.confronto(buoni, zero, "meglio")["verdetto"] == "contribuisce"
    assert c.confronto(buoni, zero, "peggio")["verdetto"] == "va contro"
    rumore = [1.0, -1.0] * 10
    assert c.confronto(rumore, [0.0, 0.1] * 10, "meglio")["verdetto"] == "non si vede ancora"


def test_freno_usdt_risparmiati_e_gruppi():
    sf = {"alloc_note": "alloc: convinzione x1.00 · learning neutro (nessun dato) · FRENO x0.50 (deriva)"}
    frenati = [_t(-1.0, size_factors_at_entry=sf) for _ in range(12)]
    liberi = [_t(0.5) for _ in range(12)]
    voce = c.contributi(frenati + liberi)[0]
    assert voce["nome"].startswith("freno globale")
    assert voce["confronto"]["verdetto"] == "contribuisce"     # frena chi poi perde
    # 12 perdite da 1 USDT a meta' size: a size piena sarebbero state 12 in piu'
    assert voce["usdt_risparmiati"] == 12.0 and voce["n_usdt"] == 12
    capped = dict(sf, capped_by_position_limit=True)
    voce2 = c.contributi([_t(-1.0, size_factors_at_entry=capped)])[0]
    assert voce2["n_usdt"] == 0


def test_peso_dalla_nota():
    t = _t(1.0, size_factors_at_entry={"alloc_note": "alloc: convinzione x1.00 · learning x1.25"})
    assert abs(c._peso(t) - 1.0) < 1e-9
    assert c._peso(_t(1.0)) is None


def test_esplorative_contro_validate_e_declassate():
    trades = ([_t(0.5, esplorativa=True) for _ in range(10)]
              + [_t(-0.2, declassata=True, risk_effective_pct=0.12) for _ in range(10)]
              + [_t(0.1, risk_effective_pct=0.5) for _ in range(10)])
    voci = {v["nome"]: v for v in c.contributi(trades)}
    assert voci["paper esplorativo"]["confronto"]["toccati"]["n"] == 10
    dec = voci["declassate a un quarto"]
    assert dec["confronto"]["toccati"]["n"] == 10 and dec["confronto"]["altri"]["n"] == 10
    assert dec["rischio_medio_pct"] == {"declassate": 0.12, "attive": 0.5}


def test_ombra_ai_lega_i_trade_per_id():
    trades = [_t(-1.0, trade_id=f"v{i}") for i in range(10)] + \
             [_t(1.0, trade_id=f"a{i}") for i in range(10)]
    dec = [{"verdict": "shadow_veto", "trade_ids": [f"v{i}" for i in range(10)]},
           {"verdict": "agree", "trade_ids": [f"a{i}" for i in range(10)]},
           {"verdict": "both_flat", "trade_ids": []},
           {"verdict": "shadow_veto", "trade_ids": ["v0", "sconosciuto"]}]    # doppione e id ignoto
    o = c.ombra_ai(trades, dec)
    assert o["confronto"]["toccati"]["n"] == 10 and o["confronto"]["altri"]["n"] == 10
    assert o["confronto"]["verdetto"] == "contribuisce"     # i vetati perdevano davvero


def test_per_origine():
    specs = {"gen_ai": {"mechanism": "x"}, "gen_v": {"origine": "referto"}, "gen_c": {}}
    trades = [_t(1.0, strategy="gen_ai"), _t(-1.0, strategy="gen_c"), _t(0.5, strategy="gen_v"),
              _t(9.0, strategy="gen_ai", esplorativa=True)]
    po = c.per_origine(trades, specs)
    assert po["ai"]["n"] == 1 and po["ai"]["r_medio"] == 1.0
    assert po["casuali"]["r_medio"] == -1.0 and po["varianti"]["n"] == 1


def test_stampa_nel_report(capsys):
    trades = [_t(0.5) for _ in range(3)]
    ts.print_funzioni_servono(trades, [], {})
    out = capsys.readouterr().out
    assert "LE FUNZIONI SERVONO?" in out and "ombra AI" in out and "ORIGINE DELLE STRATEGIE" in out
    ts.print_funzioni_servono(trades, None, None)
    assert "ombra AI" not in capsys.readouterr().out
