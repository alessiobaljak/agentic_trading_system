"""L'OMBRA DEI SEGNALI RIFIUTATI (26 set 2026, backlog J6).

Cosa si protegge. Un segnale rifiutato (cooldown, tetto per coin, peso sotto
soglia, posizione aperta, esplorative al tetto, veto di regime, margine, rischio
direzionale, stop largo) lasciava solo una riga di log: nessuno sapeva se
avrebbe vinto, e i freni si tarano solo con quel numero (H5: 9 rifiutati con PF
1,23 contro 15 aperti con PF 0,50). Qui si verificano:
  * `registra`: chiave idempotente per candela, campi, ripieghi, fail-open;
  * `simula_segnale` / `valuta_pendenti` su candele sintetiche: tp, stop,
    trailing, orizzonte, candele insufficienti, scaduto, budget di chiamate;
  * `riassunto` per classe di motivo;
  * `motivo_rifiuto` con la classe nuova «posizione aperta»;
  * l'orchestratore passa il `dettaglio` a `_rifiuto` (callback e Firebase);
  * il report stampa con e senza dati ed esce con 0.
"""
from __future__ import annotations

from datetime import datetime, timezone

import pytest

from bot.config import settings
from bot.core.firebase_client import FirebaseClient
from bot.core.models import (AssetSnapshot, Direction, IndicatorSnapshot,
                             OrchestratorDecision, Regime)
from bot.learning import rifiutati
from bot.orchestrator.orchestrator import MOTIVI_RIFIUTO, Orchestrator, motivo_rifiuto
from scripts import rifiutati_report as rep

# un'apertura di candela 15m tonda: 2026-09-26 10:00 UTC
T0 = 1790416800.0
TF = 900


class _C:
    """Una candela minima (open_time/open/high/low/close), come la usa il motore."""

    def __init__(self, i: int, o: float, h: float, l: float, c: float, t0: float = T0):
        self.open_time = datetime.fromtimestamp(t0 + i * TF, tz=timezone.utc)
        self.open, self.high, self.low, self.close, self.volume = o, h, l, c, 1.0


def _piatte(n: int, prezzo: float = 100.0, t0: float = T0) -> list[_C]:
    return [_C(i, prezzo, prezzo + 0.1, prezzo - 0.1, prezzo, t0) for i in range(n)]


def _fb() -> FirebaseClient:
    """Uno store in memoria NUOVO per test (non il singleton)."""
    return FirebaseClient()


def _registra(fb, now=T0 + 30, **kw):
    base = dict(symbol="AUSDT", strategy="mean_reversion", direction="long",
                motivo="cooldown dopo stop (37m)", timeframe="15m", entry=100.0,
                stop=98.0, target=104.0, scale_r_mults=(1.5, 3.0, 5.0), feats={"rsi": 20},
                selector_p=0.4, now=now)
    base.update(kw)
    return rifiutati.registra(fb, **base)


# --------------------------------------------------------------------------- #
# 1. registra                                                                  #
# --------------------------------------------------------------------------- #
def test_registra_scrive_il_documento_con_chiave_per_candela_e_campi():
    fb = _fb()
    doc_id = _registra(fb)
    assert doc_id == "202609261000_AUSDT_mean_reversion"
    d = fb.get_doc(rifiutati.COLLECTION, doc_id)
    assert d["stato"] == "in_attesa" and d["motivo_classe"] == "cooldown"
    assert d["direction"] == "long" and d["entry"] == 100.0 and d["stop"] == 98.0
    assert d["target"] == 104.0 and d["scale_r_mults"] == [1.5, 3.0, 5.0]
    assert d["feats"] == {"rsi": 20} and d["selector_p"] == 0.4
    assert d["ts"] == T0 + 30 and d["ts_candela"] == T0 and d["timeframe"] == "15m"
    assert d["esplorativa"] is False and d["id"] == doc_id


def test_registra_e_idempotente_nella_stessa_candela_e_non_sovrascrive():
    fb = _fb()
    a = _registra(fb, now=T0 + 30)
    # lo stesso segnale 5 minuti dopo (stessa candela): stesso doc, non riscritto
    d = fb.get_doc(rifiutati.COLLECTION, a)
    d["stato"] = "valutato"
    fb.set_doc(rifiutati.COLLECTION, a, d)
    b = _registra(fb, now=T0 + 300, motivo="un altro motivo")
    assert a == b
    assert fb.get_doc(rifiutati.COLLECTION, a)["stato"] == "valutato"
    assert fb.get_doc(rifiutati.COLLECTION, a)["motivo_classe"] == "cooldown"
    # la candela dopo e' un altro documento; a 1h la chiave segue l'ora
    c = _registra(fb, now=T0 + TF + 1)
    assert c == "202609261015_AUSDT_mean_reversion"
    h = _registra(fb, now=T0 + 1800, timeframe="1h")
    assert h == "202609261000_AUSDT_mean_reversion" or h.startswith("202609261000")


def test_registra_ripieghi_e_fail_open():
    fb = _fb()
    # senza stop/target: i ripieghi del motore (2% e 4%); direzione dall'enum
    doc_id = _registra(fb, direction=Direction.SHORT, stop=None, target=None,
                       scale_r_mults=None, feats="no", selector_p="x")
    d = fb.get_doc(rifiutati.COLLECTION, doc_id)
    assert d["direction"] == "short" and d["stop"] == pytest.approx(102.0)
    assert d["target"] == pytest.approx(96.0) and d["scale_r_mults"] is None
    assert d["feats"] is None and d["selector_p"] is None
    # entry rotta -> niente documento, niente eccezione
    assert _registra(fb, entry=None) is None
    assert _registra(fb, entry="boh") is None
    assert fb.query_collection(rifiutati.COLLECTION) == [d]

    class _Rotto:
        def get_doc(self, *a):
            raise RuntimeError("firestore giu'")

        def set_doc(self, *a):
            raise RuntimeError("firestore giu'")

    assert _registra(_Rotto()) is None
    assert _registra(None) is None


def test_registra_decisione_prende_timeframe_e_scala_dall_adattamento():
    fb = _fb()

    class _Adapt:
        def timeframe_for(self, s):
            return "1h"

        def params_for(self, sym):
            return {"gen_x": {"scale_r_mults": [1.0, 2.0, 3.0]}}

    dec = OrchestratorDecision(asset="BUSDT", strategy="gen_x", direction=Direction.SHORT,
                               size_multiplier=1.0, confidence=60.0, reasoning="",
                               suggested_stop=103.0, suggested_target=94.0, esplorativa=True)
    doc_id = rifiutati.registra_decisione(fb, dec, "posizione gia' aperta su questa coin",
                                          entry=100.0, now=T0 + 10, adaptation=_Adapt())
    d = fb.get_doc(rifiutati.COLLECTION, doc_id)
    assert d["timeframe"] == "1h" and d["scale_r_mults"] == [1.0, 2.0, 3.0]
    assert d["motivo_classe"] == "posizione aperta" and d["esplorativa"] is True
    assert d["direction"] == "short" and d["stop"] == 103.0 and d["target"] == 94.0
    # senza adattamento: timeframe del bot, nessuna scala
    d2 = fb.get_doc(rifiutati.COLLECTION, rifiutati.registra_decisione(
        fb, dec, "cooldown", entry=100.0, now=T0 + TF + 10))
    assert d2["timeframe"] == settings.ORCHESTRATOR_TIMEFRAME and d2["scale_r_mults"] is None


# --------------------------------------------------------------------------- #
# 2. simula_segnale (TP unico: SCALE_OUT_ENABLED e' spento nei test)             #
# --------------------------------------------------------------------------- #
def test_simula_tp_unico_long_tp_stop_e_orizzonte(monkeypatch):
    monkeypatch.setattr(settings, "SCALE_OUT_ENABLED", False)
    # entry 100, stop 98 (R=2), target 104 (2R)
    tp = _piatte(3) + [_C(3, 100, 104.5, 99.5, 104)]
    r = rifiutati.simula_segnale(tp, "long", 100.0, 98.0, 104.0)
    assert r["esito"] == "tp" and r["pnl_r"] == 2.0 and r["barre"] == 4
    assert r["mfe_r"] == pytest.approx(2.25) and r["mae_r"] == pytest.approx(0.25)
    stop = _piatte(2) + [_C(2, 100, 100.5, 97.0, 97.5)]
    r = rifiutati.simula_segnale(stop, "long", 100.0, 98.0, 104.0)
    assert r["esito"] == "stop" and r["pnl_r"] == -1.0 and r["barre"] == 3
    assert r["mae_r"] == pytest.approx(1.5)
    # stop e TP nella stessa candela: lo stop vince (prudente, come il motore)
    r = rifiutati.simula_segnale([_C(0, 100, 105, 97, 100)], "long", 100.0, 98.0, 104.0)
    assert r["esito"] == "stop"
    # 96 barre piatte: orizzonte, chiuso al close (100 -> 0R)
    r = rifiutati.simula_segnale(_piatte(120), "long", 100.0, 98.0, 104.0)
    assert r["esito"] == "orizzonte" and r["pnl_r"] == 0.0 and r["barre"] == 96
    # 95 barre: ancora in attesa
    r = rifiutati.simula_segnale(_piatte(95), "long", 100.0, 98.0, 104.0)
    assert r["esito"] is None and r["pnl_r"] is None and r["barre"] == 95
    # R non calcolabile
    assert rifiutati.simula_segnale(_piatte(5), "long", 100.0, 100.0, 104.0) is None
    assert rifiutati.simula_segnale(_piatte(5), "long", 0.0, 98.0, 104.0) is None


def test_simula_trailing_e_short(monkeypatch):
    monkeypatch.setattr(settings, "SCALE_OUT_ENABLED", False)
    monkeypatch.setattr(settings, "PROFIT_LOCK_ENABLED", True)
    monkeypatch.setattr(settings, "PROFIT_LOCK_TRIGGER", 0.5)
    monkeypatch.setattr(settings, "PROFIT_LOCK_KEEP", 0.5)
    # long 100/98/104: sale a 103 (armato: 3 >= 0.5*4), lock a 100+0.5*3 = 101.5,
    # poi la candela dopo scende a 101 -> esce a 101.5 = +0.75R «trailing»
    cs = [_C(0, 100, 103, 99.8, 102.5), _C(1, 102.5, 102.6, 101.0, 101.2)]
    r = rifiutati.simula_segnale(cs, "long", 100.0, 98.0, 104.0)
    assert r["esito"] == "trailing" and r["pnl_r"] == pytest.approx(0.75)
    assert r["mfe_r"] == pytest.approx(1.5)
    # short 100/102/96: scende a 96 -> tp +2R; a 102.5 -> stop -1R
    r = rifiutati.simula_segnale([_C(0, 100, 100.2, 95.9, 96.5)], "short", 100.0, 102.0, 96.0)
    assert r["esito"] == "tp" and r["pnl_r"] == 2.0
    r = rifiutati.simula_segnale([_C(0, 100, 102.5, 99.5, 102)], Direction.SHORT, 100.0, 102.0, 96.0)
    assert r["esito"] == "stop" and r["pnl_r"] == -1.0
    # keep esplicito piu' alto: lock a 100 + 0.65*3 = 101.95
    r = rifiutati.simula_segnale(cs, "long", 100.0, 98.0, 104.0, keep=0.65)
    assert r["pnl_r"] == pytest.approx(0.975)


def test_simula_scale_out_come_il_motore(monkeypatch):
    monkeypatch.setattr(settings, "SCALE_OUT_ENABLED", True)
    monkeypatch.setattr(settings, "SCALE_OUT_FRACTIONS", (0.3, 0.3, 0.4))
    monkeypatch.setattr(settings, "PROFIT_LOCK_ENABLED", False)
    # long 100/98 (R=2), scala 1/2/3 -> 102, 104, 106
    tutti = [_C(0, 100, 106.5, 99.9, 106)]
    r = rifiutati.simula_segnale(tutti, "long", 100.0, 98.0, r_mults=(1, 2, 3))
    assert r["esito"] == "tp" and r["pnl_r"] == pytest.approx(0.3 * 1 + 0.3 * 2 + 0.4 * 3)
    # primo gradino, poi break-even (default globale True): torna a 100 -> «stop» a
    # entry sul residuo: 0.3*1R + 0.7*0 = +0.3R
    cs = [_C(0, 100, 102.2, 99.9, 102), _C(1, 102, 102.1, 99.5, 99.8)]
    r = rifiutati.simula_segnale(cs, "long", 100.0, 98.0, r_mults=(1, 2, 3), breakeven=True)
    assert r["esito"] == "stop" and r["pnl_r"] == pytest.approx(0.3)
    # senza break-even: lo stop resta a 98, la seconda candela non lo tocca ->
    # dopo 96 barre piatte a 100: orizzonte, 0.3*1R + 0.7*0
    r = rifiutati.simula_segnale(cs + _piatte(96, 100.0), "long", 100.0, 98.0,
                                 r_mults=(1, 2, 3), breakeven=False)
    assert r["esito"] == "orizzonte" and r["pnl_r"] == pytest.approx(0.3)


# --------------------------------------------------------------------------- #
# 3. valuta_pendenti                                                           #
# --------------------------------------------------------------------------- #
def _fn_candele(per_symbol: dict, chiamate: list):
    def fn(symbol, tf, limit):
        chiamate.append((symbol, tf, limit))
        return per_symbol.get(symbol, [])
    return fn


def test_valuta_pendenti_tp_stop_e_attesa(monkeypatch):
    monkeypatch.setattr(settings, "SCALE_OUT_ENABLED", False)
    fb = _fb()
    a = _registra(fb, symbol="AUSDT")                      # long 100/98/104
    b = _registra(fb, symbol="BUSDT", direction="short", stop=102.0, target=96.0)
    c = _registra(fb, symbol="CUSDT")
    candele = {"AUSDT": _piatte(2) + [_C(2, 100, 104.2, 99.9, 104)],     # tp alla 3a
               "BUSDT": [_C(0, 100, 102.3, 99.9, 102)],                   # stop alla 1a
               "CUSDT": _piatte(5)}                                       # niente
    chiamate: list = []
    # troppo presto: la candela d'ingresso non e' chiusa da 2 barre -> nessuna chiamata
    assert rifiutati.valuta_pendenti(fb, _fn_candele(candele, chiamate), T0 + TF) == 0
    assert chiamate == []
    now = T0 + 6 * TF
    n = rifiutati.valuta_pendenti(fb, _fn_candele(candele, chiamate), now)
    assert n == 2 and len(chiamate) == 3
    da = fb.get_doc(rifiutati.COLLECTION, a)
    assert da["stato"] == "valutato" and da["esito"] == "tp" and da["pnl_r"] == 2.0
    assert da["barre"] == 3 and da["valutato_at"] == now
    db = fb.get_doc(rifiutati.COLLECTION, b)
    assert db["stato"] == "valutato" and db["esito"] == "stop" and db["pnl_r"] == -1.0
    assert fb.get_doc(rifiutati.COLLECTION, c)["stato"] == "in_attesa"
    # un secondo giro non rivaluta i valutati: una sola chiamata (CUSDT)
    chiamate.clear()
    assert rifiutati.valuta_pendenti(fb, _fn_candele(candele, chiamate), now) == 0
    assert [s for s, _, _ in chiamate] == ["CUSDT"]


def test_valuta_pendenti_usa_solo_candele_chiuse_dalla_candela_d_ingresso(monkeypatch):
    monkeypatch.setattr(settings, "SCALE_OUT_ENABLED", False)
    fb = _fb()
    a = _registra(fb)
    # candele PRIMA dell'ingresso col TP dentro: non contano; la candela in
    # formazione (open_time + 15m > now) nemmeno
    prima = [_C(-2, 100, 110, 99, 100), _C(-1, 100, 110, 99, 100)]
    dopo = _piatte(3) + [_C(3, 100, 104.5, 99.9, 104)]
    now = T0 + 3 * TF + 60          # la 4a candela (i=3) e' ancora aperta
    rifiutati.valuta_pendenti(fb, lambda s, tf, l: prima + dopo, now)
    assert fb.get_doc(rifiutati.COLLECTION, a)["stato"] == "in_attesa"
    rifiutati.valuta_pendenti(fb, lambda s, tf, l: prima + dopo, T0 + 4 * TF)
    d = fb.get_doc(rifiutati.COLLECTION, a)
    assert d["esito"] == "tp" and d["barre"] == 4
    # candele che NON partono dalla candela d'ingresso (buco): si aspetta
    b = _registra(fb, symbol="BUSDT")
    tardi = [_C(i, 100, 104.5, 99.9, 104) for i in range(2, 6)]
    rifiutati.valuta_pendenti(fb, lambda s, tf, l: tardi, T0 + 7 * TF)
    assert fb.get_doc(rifiutati.COLLECTION, b)["stato"] == "in_attesa"


def test_valuta_pendenti_orizzonte_scaduto_e_budget(monkeypatch):
    monkeypatch.setattr(settings, "SCALE_OUT_ENABLED", False)
    fb = _fb()
    a = _registra(fb, symbol="AUSDT")
    b = _registra(fb, symbol="BUSDT")
    c = _registra(fb, symbol="CUSDT")
    piatte = _piatte(110)
    # orizzonte: 96 candele chiuse senza uscita -> «orizzonte» a 0R
    now = T0 + 97 * TF
    n = rifiutati.valuta_pendenti(fb, lambda s, tf, l: piatte if s == "AUSDT" else [], now,
                                  max_per_giro=1)
    assert n == 1                                            # budget: una chiamata
    da = fb.get_doc(rifiutati.COLLECTION, a)
    assert da["esito"] == "orizzonte" and da["pnl_r"] == 0.0 and da["barre"] == 96
    assert fb.get_doc(rifiutati.COLLECTION, b)["stato"] == "in_attesa"
    # oltre orizzonte + margine senza candele: scaduto (una funzione che alza
    # un'eccezione vale come «niente candele», e non ferma il giro)
    def rotta(s, tf, l):
        raise RuntimeError("binance 451")
    n = rifiutati.valuta_pendenti(fb, rotta, T0 + 105 * TF, margine_barre=8)
    assert n == 2
    assert fb.get_doc(rifiutati.COLLECTION, b)["stato"] == "scaduto"
    assert fb.get_doc(rifiutati.COLLECTION, c)["stato"] == "scaduto"
    assert fb.get_doc(rifiutati.COLLECTION, c)["valutato_at"] == T0 + 105 * TF
    # ma un segnale vecchio CON le candele giuste si valuta comunque
    d = _registra(fb, symbol="DUSDT", now=T0 + 30)
    assert fb.get_doc(rifiutati.COLLECTION, d)["stato"] == "in_attesa"
    n = rifiutati.valuta_pendenti(fb, lambda s, tf, l: _piatte(2) + [_C(2, 100, 104.5, 99.9, 104)],
                                  T0 + 105 * TF)
    assert n == 1 and fb.get_doc(rifiutati.COLLECTION, d)["esito"] == "tp"


def test_valuta_pendenti_fail_open_senza_firebase():
    class _Rotto:
        def query_collection(self, *a, **k):
            raise RuntimeError("giu'")
    assert rifiutati.valuta_pendenti(_Rotto(), lambda *a: [], T0) == 0


# --------------------------------------------------------------------------- #
# 4. riassunto                                                                 #
# --------------------------------------------------------------------------- #
def test_riassunto_per_motivo(monkeypatch):
    monkeypatch.setattr(settings, "SCALE_OUT_ENABLED", False)
    fb = _fb()
    _registra(fb, symbol="AUSDT", motivo="cooldown dopo stop (5m)")
    _registra(fb, symbol="BUSDT", motivo="cooldown dopo stop (9m)")
    _registra(fb, symbol="CUSDT", motivo="cooldown dopo stop (9m)")
    _registra(fb, symbol="DUSDT", motivo="posizione gia' aperta su questa coin")
    _registra(fb, symbol="EUSDT", motivo="tetto per coin al giorno: x", now=T0 - 40 * 86400)
    candele = {"AUSDT": _piatte(2) + [_C(2, 100, 104.5, 99.9, 104)],     # tp +2R
               "BUSDT": [_C(0, 100, 100.5, 97.5, 98)],                    # stop -1R
               "DUSDT": [_C(0, 100, 103, 99.9, 103), _C(1, 103, 103, 99.9, 100)]}  # trailing
    rifiutati.valuta_pendenti(fb, lambda s, tf, l: candele.get(s, []), T0 + 6 * TF)
    r = rifiutati.riassunto(fb, giorni=30, now=T0 + 6 * TF)
    assert r["totale"] == 4 and set(r["per_motivo"]) == {"cooldown", "posizione aperta"}
    cd = r["per_motivo"]["cooldown"]
    assert cd["n"] == 3 and cd["valutati"] == 2 and cd["in_attesa"] == 1 and cd["scaduti"] == 0
    assert cd["pnl_r_medio"] == pytest.approx(0.5) and cd["quota_vincenti"] == 0.5
    assert cd["mfe_r_mediana"] == pytest.approx((2.25 + 0.25) / 2)
    assert cd["esiti"] == {"tp": 1, "stop": 1}
    pa = r["per_motivo"]["posizione aperta"]
    assert pa["valutati"] == 1 and pa["esiti"] == {"trailing": 1} and pa["pnl_r_medio"] > 0
    # vuoto e rotto: mai un'eccezione
    assert rifiutati.riassunto(_fb(), now=T0)["per_motivo"] == {}

    class _Rotto:
        def query_collection(self, *a, **k):
            raise RuntimeError("giu'")
    assert rifiutati.riassunto(_Rotto(), now=T0)["totale"] == 0


# --------------------------------------------------------------------------- #
# 5. la classe «posizione aperta»                                              #
# --------------------------------------------------------------------------- #
def test_posizione_aperta_ha_la_sua_classe():
    assert motivo_rifiuto("posizione gia' aperta su questa coin") == "posizione aperta"
    assert motivo_rifiuto("posizione già aperta su questa coin") == "posizione aperta"
    assert "posizione aperta" in MOTIVI_RIFIUTO and MOTIVI_RIFIUTO[-1] == "altro"
    assert motivo_rifiuto("snapshot asset mancante") == "altro"
    assert motivo_rifiuto("cooldown dopo stop (3m)") == "cooldown"


# --------------------------------------------------------------------------- #
# 6. l'orchestratore passa il dettaglio                                        #
# --------------------------------------------------------------------------- #
def _asset(sym: str = "BTCUSDT") -> AssetSnapshot:
    """mean_reversion LONG (come tests/test_rifiuti_nel_log.py)."""
    ind = IndicatorSnapshot(timeframe="15m", rsi=20.0, atr=2.0, close=94.0,
                            bb_lower=95.0, bb_upper=105.0, bb_mid=100.0)
    return AssetSnapshot(symbol=sym, price=94.0, regime=Regime.SIDEWAYS,
                         indicators={"15m": ind})


def _orch(symbols, peso=None, fb=None) -> Orchestrator:
    o = Orchestrator(fb=fb)
    o.adaptation._passed = {f"{s}|mean_reversion" for s in symbols}
    o.adaptation._has_opt_data = True
    if peso is not None:
        o.adaptation._weights = {f"mean_reversion|{r.value}": peso for r in Regime}
    return o


# Dal 26 set 2026 (pavimento della panchina, passo 4) il peso 0,3 non rifiuta
# piu': i tre test sotto verificano il percorso rifiuto -> ombra, quindi tengono
# il rifiuto di prima spegnendo il pavimento (PANCHINA_PAVIMENTO = 0).
def test_peso_sotto_soglia_chiama_il_callback_col_dettaglio(monkeypatch, capsys):
    monkeypatch.setattr(settings, "BACKTEST_PARITY", False)
    monkeypatch.setattr(settings, "PANCHINA_PAVIMENTO", 0.0)
    o = _orch(["BTCUSDT"], peso=0.3)
    visti = []
    o.on_rifiuto = lambda sym, strat, motivo, det: visti.append((sym, strat, motivo, det))
    assert o.decide_all({"BTCUSDT": _asset()}, Regime.SIDEWAYS) == []
    assert len(visti) == 1
    sym, strat, motivo, det = visti[0]
    assert (sym, strat) == ("BTCUSDT", "mean_reversion") and motivo.startswith("peso 0.30")
    assert det["direction"] == "long" and det["entry"] == 94.0
    assert det["stop"] is not None and det["stop"] < 94.0 and det["target"] > 94.0
    assert det["timeframe"] == "15m" and det["esplorativa"] is False
    assert det["feats"] is None and det["selector_p"] is None
    # la riga di log non cambia
    righe = [r for r in capsys.readouterr().out.splitlines() if r.startswith("[rifiuto]")]
    assert righe[0].startswith("[rifiuto] BTCUSDT mean_reversion: peso 0.30")


def test_veto_di_regime_registra_in_firebase(monkeypatch):
    monkeypatch.setattr(settings, "BACKTEST_PARITY", False)
    monkeypatch.setattr(settings, "REGIME_FILTER_ENABLED", True)
    fb = _fb()
    o = _orch(["BTCUSDT"], peso=1.0, fb=fb)
    o.adaptation._regime_pf = {"BTCUSDT|mean_reversion": {
        "sideways": {"pf": 0.5, "trades": settings.GATE_REGIME_MIN_TRADES + 10}}}
    assert o.decide_all({"BTCUSDT": _asset()}, Regime.SIDEWAYS) == []
    docs = fb.query_collection(rifiutati.COLLECTION)
    assert len(docs) == 1
    d = docs[0]
    assert d["motivo_classe"] == "veto di regime" and d["symbol"] == "BTCUSDT"
    assert d["strategy"] == "mean_reversion" and d["entry"] == 94.0 and d["stato"] == "in_attesa"
    # secondo ciclo nella stessa candela: nessun doppione
    o.decide_all({"BTCUSDT": _asset()}, Regime.SIDEWAYS)
    assert len(fb.query_collection(rifiutati.COLLECTION)) == 1


def test_senza_fb_ne_callback_resta_solo_il_contatore(monkeypatch):
    monkeypatch.setattr(settings, "BACKTEST_PARITY", False)
    monkeypatch.setattr(settings, "PANCHINA_PAVIMENTO", 0.0)
    o = _orch(["BTCUSDT"], peso=0.3)
    assert o.fb is None and o.on_rifiuto is None
    assert o.decide_all({"BTCUSDT": _asset()}, Regime.SIDEWAYS) == []
    assert o.rifiuti_ciclo() == [{"motivo": "peso sotto soglia", "n": 1}]


def test_un_callback_che_esplode_non_ferma_il_ciclo(monkeypatch, capsys):
    monkeypatch.setattr(settings, "BACKTEST_PARITY", False)
    monkeypatch.setattr(settings, "PANCHINA_PAVIMENTO", 0.0)
    o = _orch(["BTCUSDT"], peso=0.3)

    def boom(*a):
        raise RuntimeError("firestore giu'")
    o.on_rifiuto = boom
    assert o.decide_all({"BTCUSDT": _asset()}, Regime.SIDEWAYS) == []
    assert o.rifiuti_ciclo() == [{"motivo": "peso sotto soglia", "n": 1}]
    assert "[rifiutati] ombra saltata" in capsys.readouterr().out


def test_rifiuto_senza_dettaglio_non_registra_niente():
    fb = _fb()
    o = Orchestrator(fb=fb)
    o.nuovo_ciclo()
    o._rifiuto("AUSDT", "gen_a", "cooldown dopo stop (5m)")
    assert fb.query_collection(rifiutati.COLLECTION) == []
    assert o.rifiuti_ciclo() == [{"motivo": "cooldown", "n": 1}]


# --------------------------------------------------------------------------- #
# 7. il report                                                                 #
# --------------------------------------------------------------------------- #
def test_report_senza_dati_esce_con_zero(monkeypatch, capsys):
    monkeypatch.setattr(rep, "get_firebase", lambda: _fb())
    assert rep.main([]) == 0
    out = capsys.readouterr().out
    assert "0 registrati" in out and "ombra e' vuota" in out and "REGOLA" in out


def test_report_con_dati_confronta_con_gli_aperti(monkeypatch, capsys):
    monkeypatch.setattr(settings, "SCALE_OUT_ENABLED", False)
    fb = _fb()
    monkeypatch.setattr(rep, "get_firebase", lambda: fb)
    import time as _t
    now = _t.time()
    t0 = float(int(now - 6 * TF) // TF * TF) - 10 * TF     # 10 candele fa, tonda
    for i, sym in enumerate(["AUSDT", "BUSDT", "CUSDT"]):
        _registra(fb, symbol=sym, motivo="cooldown dopo stop (5m)", now=t0 + 30)
    _registra(fb, symbol="DUSDT", motivo="posizione gia' aperta su questa coin", now=t0 + 30)
    cand = {"AUSDT": _piatte(1, 100.0, t0) + [_C(1, 100, 104.5, 99.9, 104, t0)],
            "BUSDT": [_C(0, 100, 100.5, 97.5, 98, t0)],
            "CUSDT": _piatte(1, 100.0, t0) + [_C(1, 100, 104.5, 99.9, 104, t0)]}
    rifiutati.valuta_pendenti(fb, lambda s, tf, l: cand.get(s, []), now)
    # due aperti: uno a +1R netto (rischio 2 x 10 = 20 USDT, pnl 20), uno a -1R
    fb.set_doc("trades", "t1", {"trade_id": "t1", "symbol": "XUSDT", "direction": "long",
                                "entry_price": 100.0, "orig_stop": 98.0, "size": 10.0,
                                "pnl": 20.0, "mfe_r": 1.4, "exit_ts": now - 3600})
    fb.set_doc("trades", "t2", {"trade_id": "t2", "symbol": "YUSDT", "direction": "short",
                                "entry_price": 100.0, "post_mortem": {"stop_pct": 2.0},
                                "size": 10.0, "pnl": -20.0, "mfe_r": 0.2, "exit_ts": now - 7200})
    fb.set_doc("trades", "t3", {"trade_id": "t3", "symbol": "ZUSDT", "direction": "long",
                                "entry_price": 100.0, "size": 10.0, "pnl": 5.0,
                                "exit_ts": now - 7200, "esplorativa": True})   # fuori
    fb.set_doc("trades", "t4", {"trade_id": "t4", "symbol": "WUSDT", "direction": "long",
                                "entry_price": 100.0, "stop_price": 100.0, "size": 10.0,
                                "pnl": 5.0, "exit_ts": now - 7200})            # senza R
    assert rep.main(["--min-casi", "2"]) == 0
    out = capsys.readouterr().out
    assert "4 registrati" in out
    assert "cooldown" in out and "posizione aperta" in out
    assert "APERTI nello stesso periodo: 2 trade con R calcolabile (1 senza)" in out
    assert "R medio +0.00" in out
    # cooldown: 2 valutati (+2R, -1R) -> R medio +0.50 > aperti 0.00 su 2 casi -> ritarare
    assert "cooldown" in out and "RITARARE" in out
    # posizione aperta: 0 valutati -> campione insufficiente
    assert "campione insufficiente" in out


def test_verdetto_puro_e_r_aperto():
    pm = {"cooldown": {"n": 40, "valutati": 31, "pnl_r_medio": 0.3},
          "margine": {"n": 10, "valutati": 5, "pnl_r_medio": 2.0},
          "veto di regime": {"n": 35, "valutati": 30, "pnl_r_medio": -0.2}}
    righe = rep.verdetto(pm, {"pnl_r_medio": 0.1}, min_casi=30)
    assert "RITARARE" in righe[0] and "cooldown" in righe[0]
    assert "freno tiene" in righe[1] and "veto di regime" in righe[1]
    assert "insufficiente" in righe[2] and "margine" in righe[2]
    righe = rep.verdetto(pm, {"pnl_r_medio": None}, min_casi=30)
    assert "senza aperti" in righe[0]
    assert rep.r_aperto({"entry_price": 100, "orig_stop": 98, "size": 10, "pnl": -20}) == -1.0
    assert rep.r_aperto({"entry_price": 100, "size": 10, "pnl": -20}) is None
    assert rep.r_aperto({"entry_price": 100, "stop_price": 95, "size": 0, "pnl": 1}) is None


def test_la_voce_ops_rifiutati_e_in_lista_bianca():
    import os
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    with open(os.path.join(root, "ops", "allowlist.example"), encoding="utf-8") as f:
        righe = [r for r in f.read().splitlines() if r.startswith("rifiutati:")]
    assert righe == ["rifiutati:    .venv/bin/python -m scripts.rifiutati_report"]


def test_il_bot_cabla_ombra_dei_rifiuti_e_storia_delle_ipotesi():
    """26 set 2026: le righe di cablaggio in bot/main.py (registra il rifiuto,
    valuta i pendenti ogni candela, storia delle ipotesi dopo i referti)."""
    import inspect
    from bot import main as bot_main
    src_init = inspect.getsource(bot_main.TradingBot.__init__)
    assert "self.orchestrator.fb = self.fb" in src_init
    src_open = inspect.getsource(bot_main.TradingBot._try_open)
    assert "rifiutati.registra_decisione(self.fb, decision, motivo" in src_open
    src_run = inspect.getsource(bot_main.TradingBot.run)
    assert "rifiutati.valuta_pendenti(self.fb, self.price.get_candles, now)" in src_run
    src_ref = inspect.getsource(bot_main.TradingBot._publish_referti)
    assert 'self.fb.set_doc("learning", "ipotesi_storia"' in src_ref
