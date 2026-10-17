"""Il report dei rifiutati leggeva `post_mortem.stop_pct` (una FRAZIONE) come
percentuale: stop 100 volte piu' vicino, R degli aperti 100 volte piu' grande
(−6,80 invece di −0,17, ops 0289). Corretto il 27 set 2026."""
from scripts.rifiutati_report import r_aperto, stop_originale


def test_lo_stop_dal_referto_e_una_frazione():
    t = {"entry_price": 100.0, "direction": "long", "post_mortem": {"stop_pct": 0.02}}
    assert abs(stop_originale(t) - 98.0) < 1e-9
    t["direction"] = "short"
    assert abs(stop_originale(t) - 102.0) < 1e-9


def test_un_valore_sopra_1_e_una_percentuale():
    t = {"entry_price": 100.0, "direction": "long", "post_mortem": {"stop_pct": 2.0}}
    assert abs(stop_originale(t) - 98.0) < 1e-9


def test_una_perdita_allo_stop_vale_circa_meno_1R():
    t = {"entry_price": 100.0, "direction": "long", "size": 10.0, "pnl": -20.0,
         "post_mortem": {"stop_pct": 0.02}}
    assert abs(r_aperto(t) - (-1.0)) < 1e-9
