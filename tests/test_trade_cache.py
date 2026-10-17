"""LA CACHE DEI TRADE CHIUSI (28 set 2026, dopo la quota Firestore esaurita).

Il bot rileggeva i trade da Firestore a ogni candela (verdetti), dopo ogni
chiusura e ogni ora (pesi), ogni ora (controllo) e a ogni decisione (tetto per
coin): ~20.000 letture al giorno per sapere cio' che aveva scritto lui. Qui si
verifica, sul Firebase in memoria e col contatore delle letture:
  * la cache si carica intera al primo uso (N letture) e poi `recent` e
    `all_since` non leggono piu';
  * l'aggiornamento incrementale legge solo i trade con exit_ts >= ultimo
    visto (1 lettura se non c'e' niente di nuovo) e vede uno scrittore esterno;
  * `log` e `aggiorna` (i verdetti scritti sul posto) aggiornano la cache;
  * la verifica giornaliera conta la collection (1 lettura) e ricarica se non
    torna, stampando `[trades] cache disallineata`; `manutenzione` gira una
    volta al giorno;
  * il controllo riceve i trade dalla cache e NON li rilegge, e pubblica la
    verifica come `CACHE_TRADE_DISALLINEATA` (info).
"""
from __future__ import annotations

import inspect
from datetime import datetime, timedelta, timezone

from bot.core.firebase_client import FirebaseClient
from bot.core.models import ClosedTrade, Direction, ExitReason, Regime
from bot.learning import controllo as c
from bot.learning import trade_logger as tl
from bot.learning.trade_logger import TradeLogger

T0 = 1_790_000_000.0


def _doc(i: int, exit_ts: float | None = None, **extra) -> dict:
    d = {"trade_id": f"t{i}", "symbol": "AUSDT", "strategy": "gen_a", "pnl": float(i),
         "exit_reason": "stop_loss", "exit_ts": T0 + i * 3600 if exit_ts is None else exit_ts}
    d.update(extra)
    return d


def _fb_con(n: int) -> FirebaseClient:
    fb = FirebaseClient()
    for i in range(n):
        fb.set_doc("trades", f"t{i}", _doc(i))
    return fb


def _letture(fb) -> int:
    return fb.letture()["totale"]


def _closed(i: int, now: datetime) -> ClosedTrade:
    return ClosedTrade(
        trade_id=f"n{i}", symbol="ETHUSDT", strategy="vwap_reversion", direction=Direction.LONG,
        timeframe="15m", entry_time=now - timedelta(hours=2), exit_time=now - timedelta(minutes=i),
        entry_price=100, exit_price=102, size=1, notional=100, leverage=2, pnl=2.0, pnl_pct=0.02,
        exit_reason=ExitReason.TAKE_PROFIT, regime_at_entry=Regime.SIDEWAYS)


# --------------------------------------------------------------------------- #
# 1. caricamento e letture dalla cache                                        #
# --------------------------------------------------------------------------- #
def test_la_cache_si_carica_al_primo_uso_e_poi_non_legge_piu():
    fb = _fb_con(12)
    lg = TradeLogger(fb)
    assert lg.n_cache is None
    rec = lg.recent(5)
    assert [t["trade_id"] for t in rec] == ["t11", "t10", "t9", "t8", "t7"]
    assert lg.n_cache == 12 and _letture(fb) == 12               # N letture, una volta
    # dieci letture di fila: zero letture Firestore (l'incrementale e' ogni 5 minuti)
    for _ in range(10):
        assert len(lg.recent(100)) == 12
        assert len(lg.all_since(T0 + 6 * 3600)) == 6
    assert _letture(fb) == 12
    assert {r["chi"] for r in fb.letture()["per_chiamante"]} == {"trade"}
    assert lg.all_since(0.0)[0]["trade_id"] == "t11"               # ordine decrescente per exit_ts
    assert lg.all_since(T0 + 100 * 3600) == []


def test_l_aggiornamento_incrementale_vede_uno_scrittore_esterno_con_una_lettura():
    fb = _fb_con(3)
    lg = TradeLogger(fb)
    lg.aggiorna_min_s = 0                                          # ogni chiamata (nei test)
    lg.recent(1)
    assert _letture(fb) == 3
    # niente di nuovo: la query >= ultimo exit_ts torna 1 documento = 1 lettura
    lg.recent(1)
    assert _letture(fb) == 4 and lg.n_cache == 3
    # uno scrittore ESTERNO (uno script) aggiunge due trade: li vede, 3 letture (1 vecchio + 2 nuovi)
    fb.set_doc("trades", "t3", _doc(3))
    fb.set_doc("trades", "t4", _doc(4))
    assert [t["trade_id"] for t in lg.recent(2)] == ["t4", "t3"]
    assert _letture(fb) == 7 and lg.n_cache == 5
    # un trade con exit_ts piu' vecchio dell'ultimo visto NON si vede (per
    # disegno: e' il caso della ricarica giornaliera)
    fb.set_doc("trades", "t_vecchio", _doc(99, exit_ts=T0 - 10))
    lg.recent(1)
    assert lg.n_cache == 5
    assert lg.ricarica() == 6 and lg.n_cache == 6


def test_la_frequenza_dell_incrementale_e_dichiarata():
    assert tl.AGGIORNA_MIN_S == 300.0 and tl.RICARICA_S == 86400.0
    fb = _fb_con(2)
    lg = TradeLogger(fb)
    lg.recent(1)
    fb.set_doc("trades", "t2", _doc(2))
    lg.recent(1)
    assert lg.n_cache == 2                     # entro i 5 minuti non chiede
    lg._aggiornata_at -= 301                   # cinque minuti dopo
    lg.recent(1)
    assert lg.n_cache == 3


# --------------------------------------------------------------------------- #
# 2. le scritture del bot aggiornano la cache                                 #
# --------------------------------------------------------------------------- #
def test_log_e_aggiorna_allineano_la_cache_senza_letture():
    fb = _fb_con(2)
    lg = TradeLogger(fb)
    lg.recent(1)
    n0 = _letture(fb)
    now = datetime.now(timezone.utc)
    lg.log(_closed(1, now))
    assert lg.n_cache == 3 and lg.recent(1)[0]["trade_id"] == "n1"
    assert fb.get_doc("trades", "n1", chi="test")["exit_ts"] == lg.recent(1)[0]["exit_ts"]
    # il verdetto scritto sul posto (evaluate_pending_trailing): stesso dict, via `aggiorna`
    t = lg.recent(1)[0]
    t["trailing_verdict"] = "premature"
    lg.aggiorna(t)
    assert fb.get_doc("trades", "n1", chi="test")["trailing_verdict"] == "premature"
    assert lg.recent(1)[0]["trailing_verdict"] == "premature"
    assert _letture(fb) == n0 + 2                                  # solo le due get_doc del test
    # `log` prima del primo uso non carica la cache
    lg2 = TradeLogger(_fb_con(1))
    lg2.log(_closed(2, now))
    assert lg2.n_cache is None and _letture(lg2.fb) == 0
    assert len(lg2.recent(10)) == 2


def test_il_bot_scrive_i_verdetti_via_logger_e_il_controllo_usa_la_cache():
    from bot.main import TradingBot
    src = inspect.getsource(TradingBot.evaluate_pending_trailing)
    assert "self.logger.aggiorna(t)" in src and 'self.fb.set_doc("trades"' not in src
    pc = inspect.getsource(TradingBot._publish_controllo)
    assert "trades = self.logger.all_since(0.0)" in pc
    assert 'cache_trade=getattr(self.logger, "ultima_verifica", None)' in pc
    # i lettori di main.py passano tutti dal logger: nessuna query diretta ai trade
    main_src = inspect.getsource(inspect.getmodule(TradingBot))
    assert 'query_collection("trades"' not in main_src


# --------------------------------------------------------------------------- #
# 3. la verifica giornaliera                                                  #
# --------------------------------------------------------------------------- #
def test_verifica_conta_con_una_lettura_e_ricarica_se_non_torna(capsys):
    fb = _fb_con(4)
    lg = TradeLogger(fb)
    lg.recent(1)
    n0 = _letture(fb)
    esito = lg.verifica(now=T0)
    assert esito == {"firestore": 4, "cache": 4, "allineata": True, "verificata_at": T0, "ricaricata": False}
    assert _letture(fb) == n0 + 1                                  # l'aggregazione: 1 lettura
    assert lg.ultima_verifica == esito
    # un documento cancellato da fuori: il conteggio non torna -> ricarica + riga
    fb.delete_doc("trades", "t1")
    esito = lg.verifica(now=T0 + 10)
    assert esito["allineata"] is False and esito["ricaricata"] is True
    assert esito["firestore"] == 3 and esito["cache"] == 4 and lg.n_cache == 3
    assert "[trades] cache disallineata: 3 su Firestore vs 4 in cache, ricaricata (3)" in capsys.readouterr().out


def test_manutenzione_gira_una_volta_al_giorno_e_ricarica_per_intero():
    fb = _fb_con(3)
    lg = TradeLogger(fb)
    # prima chiamata: carica (3) + conta (1); allineata, e non ricarica due volte
    assert lg.manutenzione(now=T0)["allineata"] is True
    assert _letture(fb) == 4 and lg.n_cache == 3
    # nello stesso giorno: niente
    assert lg.manutenzione(now=T0 + 3600) is None and _letture(fb) == 4
    # un doc modificato SUL POSTO da fuori (exit_ts vecchio): l'incrementale non lo
    # vede, la ricarica giornaliera si'
    fb.set_doc("trades", "t0", _doc(0, post_stop_verdict="rumore"))
    lg.aggiorna_min_s = 0
    lg.recent(1)
    assert lg.recent(3)[-1].get("post_stop_verdict") is None
    esito = lg.manutenzione(now=T0 + 86400)
    assert esito["allineata"] is True and esito["ricaricata"] is False
    assert lg.recent(3)[-1]["post_stop_verdict"] == "rumore"        # ricaricata per intero
    # un client finto senza `count_collection` conta a mano (nessuna eccezione)
    class _Finto:
        def __init__(self): self.docs = [_doc(0), _doc(1)]
        def query_collection(self, *a, **k): return list(self.docs)
        def set_doc(self, *a): pass
    lg2 = TradeLogger(_Finto())
    assert lg2.verifica(now=T0)["allineata"] is True


def test_manutenzione_non_solleva_mai(capsys):
    class _Rotto:
        def query_collection(self, *a, **k): raise RuntimeError("quota")
    lg = TradeLogger(_Rotto())
    assert lg.manutenzione(now=T0) is None
    assert "manutenzione della cache saltata" in capsys.readouterr().out


# --------------------------------------------------------------------------- #
# 4. il controllo: trade dati = niente rilettura; l'anomalia                  #
# --------------------------------------------------------------------------- #
def test_carica_dati_non_rilegge_i_trade_quando_li_riceve():
    from tests.test_controllo import NOW, _fb
    fb = _fb()
    lg = TradeLogger(fb)
    trades = lg.all_since(0.0)
    n0 = _letture(fb)
    dati = c.carica_dati(fb, NOW, trades=trades)
    letti = {r["chi"]: r["n"] for r in fb.letture()["per_chiamante"]}
    assert dati["trades"] is trades
    assert letti["controllo"] < 100                     # i ~16 documenti + 50 dell'ombra AI
    assert letti["trade"] == n0                         # nessuna lettura in piu' sotto «trade»
    # senza `trades` li legge (etichetta «controllo»)
    c.carica_dati(fb, NOW)
    assert {r["chi"]: r["n"] for r in fb.letture()["per_chiamante"]}["controllo"] > letti["controllo"] + 50
    assert "limit=50" in inspect.getsource(c.carica_dati)


def test_la_verifica_arriva_nel_controllo_come_info():
    from tests.test_controllo import NOW, _fb
    fb = _fb()
    dati = c.carica_dati(fb, NOW, cache_trade={"firestore": 55, "cache": 54, "allineata": False,
                                               "verificata_at": NOW - 60, "ricaricata": True})
    doc = c.costruisci_controllo(dati, NOW, "bot", settings_da_bot=True, durata_ms=10)
    assert doc["salute"]["cache_trade"] == {"firestore": 55, "cache": 54, "allineata": False,
                                            "verificata_at": NOW - 60}
    a = {x["codice"]: x for x in doc["salute"]["anomalie"]}["CACHE_TRADE_DISALLINEATA"]
    assert a["gravita"] == "info" and a["valore"] == 54 and a["soglia"] == 55
    assert doc["meta"]["semaforo_sistema"] != "rosso" or "BOT_FERMO" in a  # le info non colorano
    # da ops il campo resta null anche se passato
    doc_ops = c.costruisci_controllo(dati, NOW, "ops", settings_da_bot=False, durata_ms=10)
    assert doc_ops["salute"]["cache_trade"] is None
