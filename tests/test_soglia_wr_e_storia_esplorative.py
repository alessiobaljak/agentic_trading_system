"""K10 (la soglia del win rate allentata dal supervisore: si conta e basta) e
K11 (la storia delle esplorative non perde piu' le validate), 1 ott 2026."""
from bot.core.firebase_client import encode_pairs
import scripts.trade_stats as ts
from scripts.discover_strategies import ESPLORATIVE_STORIA_MAX, aggiorna_esplorative
from scripts.gate_progress import riga_esplorative


def _t(sym, gid, pnl, ts_entrata=1.8e9):
    return {"symbol": sym, "strategy": gid, "pnl": pnl, "entry_price": 10.0,
            "orig_stop": 9.0, "size": 1.0, "entry_ts": ts_entrata}


def test_gruppo_win_rate():
    assert ts.gruppo_win_rate({"last_win_rate": 0.45}, 0.3966) == "piena"
    assert ts.gruppo_win_rate({"last_win_rate": 0.40}, 0.3966) == "allentata"
    assert ts.gruppo_win_rate({"last_win_rate": 0.3966}, 0.3966) == "allentata"
    assert ts.gruppo_win_rate({"last_win_rate": 0.30}, 0.3966) == "sotto"
    assert ts.gruppo_win_rate({}, 0.3966) == "ignoto"
    assert ts.gruppo_win_rate(None, 0.3966) == "ignoto"
    assert ts.gruppo_win_rate({"last_win_rate": "x"}, 0.3966) == "ignoto"


def test_soglia_wr_report_conta_coppie_e_r_per_gruppo(capsys):
    pairs = {"A|g1": {"last_win_rate": 0.5}, "B|g2": {"last_win_rate": 0.42},
             "C|g3": {}, "D|g4": {"last_win_rate": 0.30}}
    trades = [_t("A", "g1", 1.0), _t("B", "g2", -1.0, 1.7e9), _t("B", "g2", 0.5),
              _t("Z", "g9", -1.0)]
    rep = ts.soglia_wr_report(trades, pairs, list(pairs), 0.3966)
    g = rep["gruppi"]
    assert [g[k]["coppie"] for k in ("piena", "allentata", "sotto", "ignoto")] == [1, 1, 1, 1]
    assert g["piena"]["tutto"]["n"] == 1 and g["piena"]["tutto"]["r_medio"] == 1.0
    assert g["allentata"]["tutto"]["n"] == 2 and g["allentata"]["tutto"]["r_medio"] == -0.25
    # dal 27 set solo il trade entrato dopo il taglio
    assert g["allentata"]["dal"]["n"] == 1 and g["allentata"]["dal"]["r_medio"] == 0.5
    assert g["non_validate"]["tutto"]["n"] == 1
    ts.print_soglia_wr(rep)
    out = capsys.readouterr().out
    assert "ALLENTATA" in out and "0.3966" in out and "nessuna soglia cambia" in out


def test_soglia_wr_senza_registro_lo_dice(capsys):
    ts.print_soglia_wr(None)
    assert "conteggio saltato" in capsys.readouterr().out


def _storia_piena(n_scartate):
    s = {f"S{i}USDT|gen_s": {"fine": 1000 + i, "esito": "scartata"} for i in range(n_scartate)}
    s["VUSDT|gen_v"] = {"fine": 1, "esito": "validata"}      # la piu' vecchia di tutte
    return s


def test_k11_la_validata_piu_vecchia_resta_e_le_scartate_si_contano():
    doc, st = aggiorna_esplorative({"storia": _storia_piena(ESPLORATIVE_STORIA_MAX)},
                                   [], {}, [], 2000.0)
    assert len(doc["storia"]) == ESPLORATIVE_STORIA_MAX
    assert "VUSDT|gen_v" in doc["storia"] and st["validate_poi"] == 1
    assert doc["scartate_tolte"] == 1 and st["scartate"] == ESPLORATIVE_STORIA_MAX
    # il giro dopo: il conteggio non scende e non si gonfia
    doc2, st2 = aggiorna_esplorative(doc, [], {}, [], 3000.0)
    assert st2["validate_poi"] == 1 and st2["scartate"] == ESPLORATIVE_STORIA_MAX
    assert doc2["scartate_tolte"] == 1


def test_k11_senza_taglio_niente_cambia():
    doc, st = aggiorna_esplorative({"storia": _storia_piena(5)}, [], {}, [], 2000.0)
    assert doc["scartate_tolte"] == 0 and st["scartate"] == 5 and st["validate_poi"] == 1


def test_k11_i_report_sommano_le_scartate_tolte():
    esp = {"pairs": encode_pairs({}), "scartate_tolte": 7,
           "storia": encode_pairs({"A|g": {"esito": "scartata"}, "B|g": {"esito": "validata"}})}
    assert "validate poi 1 · scartate 8" in riga_esplorative(esp)
    rep = ts.esplorativo_report([], esp)
    assert rep["validate_poi"] == 1 and rep["scartate"] == 8
