"""IL GIORNO DEL PROPRIETARIO (28 set 2026, `bot/core/tempo.py`).

Il proprietario legge le giornate in ora italiana; i report contavano per
giorno UTC e la dashboard contava solo le validate mentre il portafoglio
sommava tutto (27 set: +3,25 sul conto, +1,26 sulle validate, «entrambi per
giorno UTC»). Qui si verifica che esista UNA definizione di giorno
(`giorno_locale`, Europe/Rome con l'ora legale), che la usino il controllo, il
portafoglio simulato, il PnL del paper per giorno e `trade_stats`, che il
ripiego senza tzdata sia UTC+2 dichiarato, e che i due conti (tutti /
validate) stiano uno accanto all'altro.
"""
from __future__ import annotations

import inspect
from datetime import datetime, timezone

import pytest

from bot.core import tempo


def _utc(y, m, d, h=0, mi=0) -> float:
    return datetime(y, m, d, h, mi, tzinfo=timezone.utc).timestamp()


def test_confini_in_ora_legale_e_solare():
    assert tempo.GIORNO_TZ == "Europe/Rome"
    # estate (UTC+2): le 23:30 UTC del 24 sono gia' il 25 in Italia
    assert tempo.giorno_locale(_utc(2026, 9, 24, 23, 30)) == "2026-09-25"
    assert tempo.giorno_locale(_utc(2026, 9, 24, 21, 59)) == "2026-09-24"
    assert tempo.giorno_locale(_utc(2026, 9, 24, 22, 0)) == "2026-09-25"
    # inverno (UTC+1): le 22:30 UTC del 15 gennaio sono ancora il 15
    assert tempo.giorno_locale(_utc(2026, 1, 15, 22, 30)) == "2026-01-15"
    assert tempo.giorno_locale(_utc(2026, 1, 15, 23, 0)) == "2026-01-16"
    # il giorno del cambio d'ora (25 ott 2026, 01:00 UTC): resta un giorno di 25 ore
    assert tempo.giorno_locale(_utc(2026, 10, 24, 22, 30)) == "2026-10-25"
    assert tempo.giorno_locale(_utc(2026, 10, 25, 22, 30)) == "2026-10-25"
    assert tempo.giorno_locale(_utc(2026, 10, 25, 23, 0)) == "2026-10-26"
    assert tempo.inizio_giorno_locale(_utc(2026, 9, 25, 12)) == _utc(2026, 9, 24, 22)
    assert tempo.inizio_giorno_locale(_utc(2026, 1, 15, 12)) == _utc(2026, 1, 14, 23)


def test_giorno_da_iso_naive_e_con_fuso():
    assert tempo.giorno_da_iso("2026-09-24T23:30:00") == "2026-09-25"          # naive = UTC
    assert tempo.giorno_da_iso("2026-09-24T23:30:00+00:00") == "2026-09-25"
    assert tempo.giorno_da_iso("2026-09-24T23:30:00Z") == "2026-09-25"
    assert tempo.giorno_da_iso("2026-09-25T01:30:00+02:00") == "2026-09-25"    # gia' italiana
    assert tempo.giorno_da_iso("boh") is None and tempo.giorno_da_iso(None) is None


def test_ripiego_senza_tzdata_e_utc_piu_2_dichiarato(monkeypatch, capsys):
    import zoneinfo
    monkeypatch.setattr(tempo, "_FUSO", None)
    monkeypatch.setattr(tempo, "_RIPIEGO", False)

    def _manca(_):
        raise zoneinfo.ZoneInfoNotFoundError("no tzdata")
    monkeypatch.setattr(zoneinfo, "ZoneInfo", _manca)
    assert tempo.giorno_locale(_utc(2026, 1, 15, 22, 30)) == "2026-01-16"   # UTC+2 fisso: sbaglia di un'ora
    assert tempo.ripiego_attivo() is True
    assert "giornate a UTC+2 fisso" in capsys.readouterr().out
    monkeypatch.setattr(tempo, "_FUSO", None)
    monkeypatch.setattr(tempo, "_RIPIEGO", False)


def test_tutti_i_lettori_usano_lo_stesso_giorno():
    from bot.learning import controllo
    from bot.risk import portafoglio
    from scripts import portafoglio_backtest, trade_stats
    assert "giorno_locale(ts)" in inspect.getsource(controllo._giorno)
    assert "giorno_locale(ts)" in inspect.getsource(portafoglio._giorno)
    assert "inizio_giorno_locale(ts)" in inspect.getsource(portafoglio._mezzanotte)
    assert "giorno_locale(float(ts))" in inspect.getsource(portafoglio_backtest._giorno_uscita)
    assert "giorno_da_iso(t.get(\"exit_time\"))" in inspect.getsource(portafoglio_backtest._giorno_uscita)
    assert "giorno_locale(float(ex))" in inspect.getsource(trade_stats.main)
    assert "per giorno (ora italiana)" in inspect.getsource(trade_stats.main)
    # i timestamp restano UTC: il logger scrive exit_ts in epoch, senza fuso
    from bot.learning.trade_logger import TradeLogger
    assert 'data["exit_ts"] = trade.exit_time.timestamp()' in inspect.getsource(TradeLogger.log)


def test_il_portafoglio_simulato_e_il_paper_contano_la_stessa_giornata():
    from bot.risk.portafoglio import simula
    from scripts.portafoglio_backtest import pnl_paper_per_giorno
    from tests.test_portafoglio import BARRA, LARGHI, _t
    # un trade che chiude alle 22:30 UTC del 21 (00:30 del 22 in Italia): giorno 22
    t0 = _utc(2026, 9, 21, 22, 0)
    out = simula([_t("A", "long", t0, pnl_pct=0.02, bars=2)], 10_000, LARGHI, secondi_barra=BARRA)
    assert list(out["pnl_per_giorno"]) == ["2026-09-22"]
    paper = pnl_paper_per_giorno([{"exit_ts": t0 + 2 * BARRA, "pnl": 200.0}])
    assert paper == {"2026-09-22": 200.0}


def test_il_controllo_porta_i_due_conti_nello_stesso_giorno_italiano():
    from bot.learning import controllo as c
    from tests.test_controllo import _trade
    mezzanotte_it = _utc(2026, 9, 26, 22, 0)                     # 00:00 del 27 in Italia
    now = mezzanotte_it + 8 * 3600
    validate = [_trade(1, +1.26, exit_ts=mezzanotte_it + 60)]
    tutti = validate + [_trade(2, +1.99, "manual", exit_ts=mezzanotte_it + 120)]
    g = c.giornate(validate, now, tutti=tutti)
    riga = g["ultime_7"][-1]
    assert riga["data"] == "2026-09-27" and riga["pnl_validate"] == 1.26 and riga["pnl_tutti"] == 3.25
    assert g["tz"] == "Europe/Rome"
    og = c.oggi(validate, now, tutti=tutti)
    assert og["data"] == "2026-09-27" and og["pnl"] == 1.26 and og["pnl_tutti"] == 3.25
    # lo stesso trade alle 23:59 UTC del 26 sarebbe stato «il 26» in UTC
    assert c._giorno(mezzanotte_it + 60) == "2026-09-27"
    assert datetime.fromtimestamp(mezzanotte_it + 60, tz=timezone.utc).strftime("%Y-%m-%d") == "2026-09-26"


@pytest.mark.parametrize("nome", ["ControlloPaper.tsx"])
def test_la_dashboard_dichiara_l_ora_italiana_e_i_due_conti(nome):
    import os
    root = os.path.join(os.path.dirname(__file__), "..", "dashboard", "app", "components")
    if not os.path.isdir(root):
        pytest.skip("dashboard non nel checkout")
    with open(os.path.join(root, nome), encoding="utf-8") as f:
        src = f.read()
    assert "giornate in ora italiana" in src
    assert "pnl_tutti" in src and "conto" in src and "validate" in src
    assert "Oggi (UTC)" not in src
