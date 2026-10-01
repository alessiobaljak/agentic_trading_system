"""UNA RIGA AL GIORNO, PER SEMPRE (1 ott 2026, la cattura dei dati mancanti).

Alla prima pubblicazione del controllo di ogni giorno italiano il bot scrive in
Firestore `giorni/{ieri}`: equity, uPnL, rischio e posizioni aperte, BTC,
regime globale, riavvii, trade chiusi, cicli fatti contro attesi, decisioni,
aperti, rifiutati, scarti, minuti di stream giu', commit e config_hash. Una
scrittura al giorno, nessuna lettura Firestore; la foglia RTDB
`/giorni_fatti/{giorno}` evita di riscriverla dopo un riavvio.
"""
from __future__ import annotations

import types

import pytest

from bot.core.firebase_client import FirebaseClient
from bot.core.tempo import giorno_locale, inizio_giorno_locale
from bot.learning import cattura
from bot.main import conta_giorno, scrivi_riga_del_giorno

NOW = 1_800_000_000.0
OGGI_0 = inizio_giorno_locale(NOW)
IERI = giorno_locale(OGGI_0 - 1)


def _dati():
    return {
        "equity": 1000.0,
        "positions": {"BTCUSDT": {"unrealized_pnl": 12.5, "risk_effective_pct": 0.01},
                      "ETHUSDT": {"unrealized_pnl": -2.5, "risk_effective_pct": 0.005}},
        "btc_history": [{"ts": NOW - 7200, "close": 60000.0}, {"ts": NOW - 3600, "close": 61000.0}],
        "bot_status": {"regime": "sideways"},
        "avvii": [OGGI_0 - 3600, OGGI_0 - 7200, OGGI_0 - 3 * 86400],
    }


def _trades():
    return [{"exit_ts": OGGI_0 - 100, "pnl": 3.0}, {"exit_ts": OGGI_0 - 200, "pnl": -1.0},
            {"exit_ts": OGGI_0 + 100, "pnl": 9.0}]


def test_riga_giorno_pura():
    conti = dict(cattura.conti_vuoti(), cicli=90, decisioni=12, aperti=4, rifiutati=7,
                 scarti_silenziosi=2, stream_giu_s=180.0, dal=OGGI_0 - 86000)
    r = cattura.riga_giorno(IERI, _dati(), conti, NOW, 900.0,
                            versione={"commit": "abc1234", "config_hash": "0123456789ab"},
                            trades=_trades())
    assert r["giorno"] == IERI and r["foto_at"] == NOW
    assert r["equity"] == 1000.0 and r["upnl"] == 10.0 and r["equity_a_mercato"] == 1010.0
    assert r["rischio_aperto_pct"] == pytest.approx(0.015) and r["posizioni_aperte"] == 2
    assert r["btc_close"] == 61000.0 and r["regime_globale"] == "sideways"
    assert r["riavvii"] == 2
    assert r["trade_chiusi"] == 2 and r["pnl_chiusi"] == 2.0
    assert r["cicli"] == 90 and r["cicli_attesi"] == 96
    assert r["decisioni"] == 12 and r["aperti"] == 4 and r["rifiutati"] == 7
    assert r["scarti_silenziosi"] == 2 and r["stream_giu_min"] == 3.0
    assert r["contatori_dal"] == OGGI_0 - 86000
    assert r["commit"] == "abc1234" and r["config_hash"] == "0123456789ab"


def test_riga_giorno_senza_contatori_lo_dice():
    r = cattura.riga_giorno(IERI, {}, None, NOW, 900.0)
    assert r["cicli"] is None and r["contatori_dal"] is None and r["stream_giu_min"] is None
    assert r["commit"] is None


def test_conta_giorno_tiene_tre_giorni():
    bot = types.SimpleNamespace()
    for d in range(5):
        conta_giorno(bot, "cicli", 1, NOW + d * 86400)
    assert len(bot._conti_giorno) == 3
    conta_giorno(bot, "cicli", 2, NOW + 4 * 86400)
    assert bot._conti_giorno[giorno_locale(NOW + 4 * 86400)]["cicli"] == 3


def test_una_scrittura_al_giorno_anche_dopo_un_riavvio(capsys):
    fb = FirebaseClient()
    bot = types.SimpleNamespace(fb=fb, _decision_interval_s=900,
                                _versione={"commit": "abc1234", "config_hash": "x"})
    conta_giorno(bot, "cicli", 5, OGGI_0 - 1000)
    scrivi_riga_del_giorno(bot, _dati(), _trades(), NOW)
    doc = fb.get_doc("giorni", IERI)
    assert doc["cicli"] == 5 and doc["commit"] == "abc1234"
    assert fb.get_rtdb(f"/giorni_fatti/{IERI}")
    assert f"[giorni] riga del {IERI}" in capsys.readouterr().out
    # seconda ora dello stesso giorno: niente
    fb.set_doc("giorni", IERI, {"marcatore": True})
    scrivi_riga_del_giorno(bot, _dati(), _trades(), NOW + 3600)
    assert fb.get_doc("giorni", IERI) == {"marcatore": True}
    # riavvio (stato in RAM perso, contatori vuoti): la foglia RTDB lo ferma
    nuovo = types.SimpleNamespace(fb=fb, _decision_interval_s=900)
    scrivi_riga_del_giorno(nuovo, _dati(), [], NOW + 7200)
    assert fb.get_doc("giorni", IERI) == {"marcatore": True}
    assert nuovo._riga_giorno == {"giorno": IERI, "verificato": True}


def test_la_riga_non_solleva_mai(capsys):
    rotto = types.SimpleNamespace(get_rtdb=lambda p: None,
                                  set_doc=lambda *a: (_ for _ in ()).throw(RuntimeError("giu'")))
    bot = types.SimpleNamespace(fb=rotto, _decision_interval_s=900)
    scrivi_riga_del_giorno(bot, _dati(), [], NOW)
    assert "non scritta" in capsys.readouterr().out
    assert bot._riga_giorno["giorno"] is None                     # si riprova fra un'ora
