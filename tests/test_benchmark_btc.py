"""
IL BENCHMARK BTC DAL PRIMO GIORNO DEL PAPER (28 set 2026).

Il proprietario ha detto si': il controllo orario confronta il rendimento del
conto con BTC comprato il primo giorno del paper e tenuto. Il prezzo di partenza
lo scrive UNA volta il bot (`TradingBot._btc_inizio_paper`, da Binance: GitHub non
lo raggiunge) in `rtdb:/account/btc_inizio = {ts, close}`; il controllo lo legge
dal RTDB (nessuna lettura Firestore in piu') e pubblica
`paper.benchmark.btc_dal_paper_pct`, `btc_inizio`, `noi_pct`, `differenza_pct`.

Qui si prova: che il valore si scrive una volta e non si riscrive, che un
fallimento riprova al massimo una volta l'ora e non solleva mai, che una candela
non ancora chiusa non si scrive, che il conto torna, che la lettura lo dice e che
la voce di `manca` sparisce quando il numero c'e'.
"""
from __future__ import annotations

from datetime import datetime, timezone
from types import SimpleNamespace

import pytest

from bot.core.firebase_client import FirebaseClient
from bot.core.models import Candle
from bot.learning import controllo as c
from tests.test_controllo import NOW, _doc, _fb, _finto_bot

#: l'inizio del paper della fixture di test_controllo (10 giorni prima di NOW),
#: portato qui a un istante non allineato all'ora
INIZIO = NOW - 10 * 86400 + 600
#: la prima candela 1h che APRE a/dopo l'inizio
PRIMA_ORA = INIZIO - 600 + 3600


def _candela(apre: float, close: float) -> Candle:
    return Candle(open_time=datetime.fromtimestamp(apre, timezone.utc), open=close, high=close,
                  low=close, close=close, volume=1.0,
                  close_time=datetime.fromtimestamp(apre + 3599.999, timezone.utc))


class _Prezzi:
    """Un PriceAgent finto: registra le chiamate, restituisce candele da `start_ms`."""

    def __init__(self, candele=None, errore: Exception | None = None):
        self.candele = candele
        self.errore = errore
        self.chiamate: list[dict] = []

    def get_candles(self, symbol, interval, limit=200, start_ms=None):
        self.chiamate.append({"symbol": symbol, "interval": interval, "limit": limit,
                              "start_ms": start_ms})
        if self.errore:
            raise self.errore
        if self.candele is not None:
            return list(self.candele)
        return [_candela(PRIMA_ORA + 3600 * i, 55000.0 + i) for i in range(limit)]


def _bot(fb, prezzi):
    return _finto_bot(fb, price=prezzi)


def _fb_con_inizio(inizio: float = INIZIO) -> FirebaseClient:
    fb = FirebaseClient()
    fb.set_rtdb("/account/paper_started_at", inizio)
    return fb


# --------------------------------------------------------------------------- #
# 1. il bot scrive il prezzo di partenza, una volta                             #
# --------------------------------------------------------------------------- #
def test_il_bot_scrive_btc_inizio_una_volta_dalla_prima_candela_dopo_l_inizio(capsys):
    from bot.main import TradingBot
    fb, prezzi = _fb_con_inizio(), _Prezzi()
    bot = _bot(fb, prezzi)
    TradingBot._btc_inizio_paper(bot, NOW)
    assert fb.get_rtdb("/account/btc_inizio") == {"ts": PRIMA_ORA, "close": 55000.0}
    assert prezzi.chiamate == [{"symbol": "BTCUSDT", "interval": "1h", "limit": 3,
                                "start_ms": int(INIZIO * 1000)}]
    assert "[benchmark] BTC all'inizio del paper: 55000.00" in capsys.readouterr().out
    # scritto: nessun'altra chiamata, neanche ore dopo
    TradingBot._btc_inizio_paper(bot, NOW + 7200)
    TradingBot._btc_inizio_paper(bot, NOW + 86400)
    assert len(prezzi.chiamate) == 1


def test_un_valore_gia_scritto_e_coerente_non_si_riscrive_neanche_dopo_un_riavvio():
    from bot.main import TradingBot
    fb, prezzi = _fb_con_inizio(), _Prezzi()
    fb.set_rtdb("/account/btc_inizio", {"ts": PRIMA_ORA, "close": 42.0})
    bot = _bot(fb, prezzi)                       # processo nuovo: nessuna memoria
    TradingBot._btc_inizio_paper(bot, NOW)
    assert prezzi.chiamate == []
    assert fb.get_rtdb("/account/btc_inizio") == {"ts": PRIMA_ORA, "close": 42.0}
    assert bot._btc_inizio_fatto is True


def test_un_valore_di_un_paper_precedente_si_riscrive():
    """Un `ts` fuori da [inizio, inizio + 1 h) non e' la prima candela di QUESTO
    paper (reset, inizio riscritto a mano): tenerlo sarebbe un benchmark falso."""
    from bot.main import TradingBot
    fb, prezzi = _fb_con_inizio(), _Prezzi()
    fb.set_rtdb("/account/btc_inizio", {"ts": INIZIO - 30 * 86400, "close": 42.0})
    TradingBot._btc_inizio_paper(_bot(fb, prezzi), NOW)
    assert fb.get_rtdb("/account/btc_inizio") == {"ts": PRIMA_ORA, "close": 55000.0}


def test_un_fallimento_riprova_al_massimo_una_volta_l_ora(capsys):
    from bot.main import TradingBot
    fb, prezzi = _fb_con_inizio(), _Prezzi(candele=[])
    bot = _bot(fb, prezzi)
    TradingBot._btc_inizio_paper(bot, NOW)
    assert fb.get_rtdb("/account/btc_inizio") is None
    assert "riprovo fra un'ora" in capsys.readouterr().out
    TradingBot._btc_inizio_paper(bot, NOW + 600)          # troppo presto
    TradingBot._btc_inizio_paper(bot, NOW + 3599)
    assert len(prezzi.chiamate) == 1
    prezzi.candele = None                                  # Binance torna
    TradingBot._btc_inizio_paper(bot, NOW + 3600)
    assert len(prezzi.chiamate) == 2
    assert fb.get_rtdb("/account/btc_inizio") == {"ts": PRIMA_ORA, "close": 55000.0}


def test_non_solleva_mai(capsys):
    from bot.main import TradingBot
    fb = _fb_con_inizio()
    bot = _bot(fb, _Prezzi(errore=RuntimeError("binance giu'")))
    TradingBot._btc_inizio_paper(bot, NOW)                 # nessuna eccezione
    assert fb.get_rtdb("/account/btc_inizio") is None
    assert "non scritto (binance giu')" in capsys.readouterr().out
    # nemmeno col database che solleva
    rotto = SimpleNamespace(get_rtdb=lambda p: (_ for _ in ()).throw(RuntimeError("rtdb")))
    TradingBot._btc_inizio_paper(_bot(rotto, _Prezzi()), NOW)


def test_senza_inizio_del_paper_o_con_la_candela_ancora_aperta_non_scrive():
    from bot.main import TradingBot
    fb, prezzi = FirebaseClient(), _Prezzi()
    TradingBot._btc_inizio_paper(_bot(fb, prezzi), NOW)
    assert prezzi.chiamate == [] and fb.get_rtdb("/account/btc_inizio") is None
    # paper partito 20 minuti fa: la sua prima candela chiude fra un'ora
    fb = _fb_con_inizio(NOW - 1200)
    apre = NOW - 1200 - (NOW - 1200) % 3600 + 3600
    prezzi = _Prezzi(candele=[_candela(apre, 61000.0)])
    TradingBot._btc_inizio_paper(_bot(fb, prezzi), apre + 60)
    assert fb.get_rtdb("/account/btc_inizio") is None


def test_get_candles_passa_starttime_solo_se_chiesto():
    from bot.agents.price_agent import PriceAgent
    agente = PriceAgent()
    visti = []
    agente._get = lambda path, params: visti.append(dict(params)) or []
    agente.get_candles("BTCUSDT", "1h", limit=5)
    agente.get_candles("BTCUSDT", "1h", limit=3, start_ms=1_700_000_000_000)
    assert visti[0] == {"symbol": "BTCUSDT", "interval": "1h", "limit": 5}
    assert visti[1] == {"symbol": "BTCUSDT", "interval": "1h", "limit": 3,
                        "startTime": 1_700_000_000_000}


# --------------------------------------------------------------------------- #
# 2. il controllo lo pubblica                                                   #
# --------------------------------------------------------------------------- #
def _fb_benchmark(close_inizio: float = 55000.0):
    fb = _fb()
    # la fixture: paper dal NOW - 10 g, anello BTC fino a NOW (ultima 61.990)
    fb.set_rtdb("/account/btc_inizio", {"ts": NOW - 10 * 86400 + 1800, "close": close_inizio})
    return fb


def test_il_controllo_pubblica_btc_dal_primo_giorno_e_il_confronto():
    doc = _doc(fb=_fb_benchmark())
    p = doc["paper"]
    bm = p["benchmark"]
    assert doc["meta"]["errori"] == []
    assert bm["btc_inizio"] == {"ts": NOW - 10 * 86400 + 1800, "close": 55000.0}
    assert bm["btc_dal_paper_pct"] == pytest.approx(round((61990.0 / 55000.0 - 1) * 100, 2))
    assert bm["btc_dal_paper_pct"] == pytest.approx(12.71)
    assert bm["noi_pct"] == p["rendimento_pct"] and bm["noi_pct"] is not None
    assert bm["differenza_pct"] == pytest.approx(round(p["rendimento_pct"] - 12.71, 2))
    assert "rtdb:/account/btc_inizio" in p["fonti"]


def test_la_chiusura_piu_recente_vince_e_una_vecchia_non_vale():
    fb = _fb_benchmark(50000.0)
    # /bot_status piu' fresco dell'anello: vale lui
    st = fb.get_rtdb("/bot_status")
    fb.set_rtdb("/bot_status", {**st, "btc_close": 65000.0, "updated_at": NOW - 60})
    fb.set_rtdb("/btc_history", [{"ts": NOW - 3600, "close": 60000.0}])
    assert _doc(fb=fb)["paper"]["benchmark"]["btc_dal_paper_pct"] == pytest.approx(30.0)
    # tutto piu' vecchio di 3 ore: nessun numero (un prezzo vecchio sarebbe una bugia)
    fb.set_rtdb("/bot_status", {**st, "btc_close": 65000.0, "updated_at": NOW - 4 * 3600})
    fb.set_rtdb("/btc_history", [{"ts": NOW - 4 * 3600, "close": 60000.0}])
    doc = _doc(fb=fb)
    assert doc["paper"]["benchmark"]["btc_dal_paper_pct"] is None
    assert doc["paper"]["benchmark"]["differenza_pct"] is None
    voce = [m for m in doc["manca"] if m["evidenza"].startswith("benchmark")]
    assert voce and "chiusura BTC recente" in voce[0]["perche"]


def test_btc_inizio_che_non_e_di_questo_paper_non_si_usa():
    fb = _fb()
    fb.set_rtdb("/account/btc_inizio", {"ts": NOW - 40 * 86400, "close": 30000.0})
    bm = _doc(fb=fb)["paper"]["benchmark"]
    assert bm["btc_inizio"] is None and bm["btc_dal_paper_pct"] is None
    assert c.btc_inizio_valido({"ts": 5.0, "close": 0}) is None
    assert c.btc_inizio_valido({"ts": 5.0, "close": 2.0}) == {"ts": 5.0, "close": 2.0}
    assert c.btc_inizio_valido({"ts": 5.0, "close": 2.0}, paper_dal=10.0) is None


def test_la_lettura_del_paper_dice_btc_dal_primo_giorno():
    doc = _doc(fb=_fb_benchmark())
    lettura = doc["paper"]["lettura"]
    r = doc["paper"]["rendimento_pct"]
    assert "BTC dal primo giorno +12,7%" in lettura
    assert f"(noi {'+' if r >= 0 else ''}{c._num(r, 1)}%)" in lettura
    assert len(lettura) <= c.LETTURA_MAX and not lettura.endswith("…")


def test_la_lettura_lascia_cadere_gli_stop_prima_di_troncare():
    p = {"conto": {"trades": 1234, "vinti": 600, "pnl": -12345.67}, "giorni_paper": 123,
         "rendimento_pct": -12.3,
         "benchmark": {"btc_dal_paper_pct": 11.6, "noi_pct": -12.3},
         "uscite": [{"motivo": "stop_loss", "quota": 0.57}],
         "oggi": {"trades": 3, "trades_tutti": 5, "pnl": -1.25, "pnl_tutti": 3.5}}
    testo = c.lettura_paper(p)
    assert "BTC dal primo giorno +11,6% (noi -12,3%)" in testo
    assert "Stop nel" not in testo and "Oggi +3,50 (validate -1,25)." in testo
    # senza benchmark la frase resta quella di prima
    senza = c.lettura_paper({**p, "benchmark": {}})
    assert "BTC" not in senza and "Stop nel 57% delle uscite." in senza


def test_manca_perde_la_voce_del_benchmark_quando_il_numero_c_e():
    senza = _doc()                                  # fixture senza btc_inizio
    voci = [m["evidenza"] for m in senza["manca"]]
    assert "benchmark BTC buy&hold dal primo giorno del paper" in voci
    perche = next(m["perche"] for m in senza["manca"] if m["evidenza"].startswith("benchmark"))
    assert "/account/btc_inizio" in perche
    con = _doc(fb=_fb_benchmark())
    assert len(con["manca"]) == len(senza["manca"]) - 1
    assert not any(m["evidenza"].startswith("benchmark") for m in con["manca"])
    # «cosa aspetta il si'» resta sempre
    assert any("aspetta" in m["evidenza"] for m in con["manca"])
