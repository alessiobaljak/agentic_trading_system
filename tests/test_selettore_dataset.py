"""PASSO 0 DEL SELETTORE — il dataset (docs/disegno_cervello.md, Punto 2).

Fino al 24 set 2026 un `SimTrade` diceva com'era andato un trade ma non in che
condizioni era nato: senza le variabili all'ingresso nessun modello puo'
imparare quando un segnale valido paga. Qui si verifica che:
  * `feats_ingresso` legge le variabili giuste dallo snapshot, e non inventa
    niente quando manca qualcosa (banda nulla, nessun contesto di mercato);
  * `famiglia_spec` etichetta le spec in modo stabile;
  * `evaluate_spec` produce le righe SOLO per le spec che passano;
  * la scrittura del file e' in append, nel formato condiviso, e fail-open.
"""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone

import pandas as pd
import pytest

from backtesting.engine import GateVerdict, SimTrade, StrategyStats, feats_ingresso
from bot.core.models import AssetSnapshot, IndicatorSnapshot
from bot.strategies.generated import famiglia_spec
from scripts import discover_strategies as d


# --------------------------------------------------------------------------- #
# feats_ingresso                                                               #
# --------------------------------------------------------------------------- #
def _snap(price=100.0, **ind) -> AssetSnapshot:
    base = dict(rsi=28.0, adx=31.5, stoch_k=15.0, atr=2.0, ema_fast=99.0, ema_slow=104.0,
                bb_upper=110.0, bb_lower=90.0, volume=300.0, volume_sma=200.0)
    base.update(ind)
    s = AssetSnapshot(symbol="XUSDT", price=price)
    s.indicators["15m"] = IndicatorSnapshot(timeframe="15m", **base)
    return s


class _Strat:
    params = {"scale_r_mults": [2.0, 4.0, 1.5]}


def test_feats_ingresso_legge_le_variabili_dallo_snapshot():
    f = feats_ingresso(_snap(), "15m", entry=100.0, stop=97.0, strategy=_Strat(),
                       ctx_snap=None, hour=13)
    assert f["rsi"] == 28.0 and f["adx"] == 31.5 and f["stoch_k"] == 15.0
    assert f["atr_pct"] == 0.02                       # atr / prezzo
    assert f["dist_ema"] == round(100 / 104 - 1, 4)   # prezzo / ema lenta - 1
    assert f["bb_pos"] == 0.5                         # a meta' fra le bande
    assert f["vol_ratio"] == 1.5                      # volume / media volume
    assert f["stop_pct"] == 0.03                      # |entry - stop| / entry
    assert f["r1"] == 1.5                             # il gradino PIU' BASSO della scala
    assert f["hour"] == 13
    assert f["market_up"] is None                     # nessun contesto: non si inventa
    # nessuna identita' della coin fra le variabili
    assert "symbol" not in f
    for v in f.values():
        assert v is None or isinstance(v, (int, float))


def test_feats_ingresso_banda_nulla_e_valori_mancanti_danno_none():
    f = feats_ingresso(_snap(bb_upper=100.0, bb_lower=100.0, volume_sma=None, rsi=None),
                       "15m", 100.0, 97.0, None, None)
    assert f["bb_pos"] is None
    assert f["vol_ratio"] is None
    assert f["rsi"] is None
    assert f["hour"] is None


def test_feats_ingresso_senza_params_usa_la_scala_globale():
    from bot.config import settings

    f = feats_ingresso(_snap(), "15m", 100.0, 97.0, None, None)
    assert f["r1"] == round(min(settings.SCALE_OUT_R_MULTIPLES), 4)


def test_feats_ingresso_mercato_dal_contesto_a_1h():
    btc = AssetSnapshot(symbol="BTCUSDT", price=50_000.0)
    btc.indicators["1h"] = IndicatorSnapshot(timeframe="1h", ema_fast=101.0, ema_slow=100.0)
    assert feats_ingresso(_snap(), "15m", 100.0, 97.0, None, btc)["market_up"] == 1.0
    btc.indicators["1h"] = IndicatorSnapshot(timeframe="1h", ema_fast=99.0, ema_slow=100.0)
    assert feats_ingresso(_snap(), "15m", 100.0, 97.0, None, btc)["market_up"] == 0.0
    # contesto senza le medie: non si decide
    btc.indicators["1h"] = IndicatorSnapshot(timeframe="1h")
    assert feats_ingresso(_snap(), "15m", 100.0, 97.0, None, btc)["market_up"] is None


def test_feats_ingresso_timeframe_sbagliato_non_esplode():
    """Uno snapshot senza la riga richiesta (es. replay di un vecchio motore)
    produce variabili vuote, non un errore: il gate non deve mai cadere per il
    dataset."""
    f = feats_ingresso(_snap(), "4h", 100.0, 97.0, None, None)
    assert f["rsi"] is None and f["stop_pct"] == 0.03


def test_il_trade_simulato_porta_le_feats_anche_nel_dict():
    t = SimTrade(strategy="s", regime="sideways", direction="long", entry_price=1, exit_price=1,
                 pnl_pct=0.0, max_adverse_pct=0.0, confidence=60, is_win=False, pnl=0.0,
                 symbol="XUSDT", feats={"rsi": 28.0})
    assert t.as_trade_dict()["feats"] == {"rsi": 28.0}
    assert SimTrade(strategy="s", regime="sideways", direction="long", entry_price=1,
                    exit_price=1, pnl_pct=0.0, max_adverse_pct=0.0, confidence=60,
                    is_win=False, pnl=0.0, symbol="XUSDT").feats == {}


# --------------------------------------------------------------------------- #
# famiglia_spec                                                                #
# --------------------------------------------------------------------------- #
def _spec(*kinds):
    return {"id": "gen_x", "features": [{"kind": k} for k in kinds]}


def test_famiglia_spec_sui_casi():
    assert famiglia_spec(_spec("rsi_extreme", "bb_touch")) == "reversion"
    assert famiglia_spec(_spec("ema_cross", "macd_hist", "volume_surge")) == "momentum"
    assert famiglia_spec(_spec("bb_break")) == "breakout"
    # misto a parita': reversion > momentum > breakout
    assert famiglia_spec(_spec("rsi_extreme", "ema_cross")) == "reversion"
    assert famiglia_spec(_spec("bb_break", "macd_zero")) == "momentum"
    # la maggioranza vince sulla precedenza
    assert famiglia_spec(_spec("rsi_extreme", "ema_cross", "price_ema")) == "momentum"
    # solo filtri, o niente: "altro"
    assert famiglia_spec(_spec("volatility_regime", "session")) == "altro"
    assert famiglia_spec({"id": "gen_v"}) == "altro"


# --------------------------------------------------------------------------- #
# evaluate_spec -> oos_rows                                                    #
# --------------------------------------------------------------------------- #
class _Candle:
    def __init__(self, ts):
        self.open_time = ts


class _Bt:
    """Motore finto: due trade per finestra, con le feats gia' a bordo."""
    window = 0

    def run_strategy(self, g, symbol, candles, frame=None, context_by_ts=None):
        st = StrategyStats(strategy=g.name)
        for k, pnl in enumerate((0.02, -0.01)):
            st.trades.append(SimTrade(
                strategy=g.name, regime="sideways", direction="long" if k == 0 else "short",
                entry_price=1.0, exit_price=1.0, pnl_pct=pnl, max_adverse_pct=0.0,
                confidence=60, is_win=pnl > 0, pnl=pnl * 100, symbol=symbol,
                hour_bucket=7 + k, regime_at_entry="sideways", mfe_r=1.2, bars_held=5,
                entry_ts=1_700_000_000.0 + k, feats={"rsi": 28.0, "bb_pos": None}))
        return st


class _Opt:
    holdout_bars = 0
    bt = _Bt()

    def split_holdout(self, candles):
        return candles, len(candles)

    def _windows(self, n):
        return [(0, 0, 0, n)]


def _chiama(monkeypatch, passa: bool):
    monkeypatch.setattr(d, "gate_verdict",
                        lambda *a, **k: GateVerdict(ok=passa, failed=() if passa else ("pf",),
                                                    binding="" if passa else "pf"))
    monkeypatch.setattr(d.settings, "SCALE_OUT_ENABLED", False)
    candles = [_Candle(datetime(2026, 9, 24, tzinfo=timezone.utc))] * 4
    frame = pd.DataFrame({"close": [1.0] * 4})
    return d.evaluate_spec(_Opt(), "XUSDT", candles, frame, _spec("rsi_extreme"),
                           run_end="2026-09-24", interval="15m")


def test_evaluate_spec_da_le_righe_solo_se_passa(monkeypatch):
    r = _chiama(monkeypatch, passa=False)
    assert r["passed"] is False and r["oos_rows"] == []

    r = _chiama(monkeypatch, passa=True)
    assert r["passed"] is True
    assert len(r["oos_rows"]) == 2
    riga = r["oos_rows"][0]
    # IL CONTRATTO con chi addestra: queste chiavi, questi tipi
    assert set(riga) == {"symbol", "strategy", "direction", "regime", "entry_ts",
                         "pnl_pct", "pnl", "is_win", "mfe_r", "bars_held", "hour",
                         "famiglia", "feats", "run_end", "interval"}
    assert riga["symbol"] == "XUSDT" and riga["strategy"] == "gen_x"
    assert riga["direction"] == "long" and riga["regime"] == "sideways"
    assert riga["pnl_pct"] == 0.02 and riga["is_win"] is True and riga["hour"] == 7
    assert riga["famiglia"] == "reversion"
    assert riga["feats"] == {"rsi": 28.0, "bb_pos": None}
    assert riga["run_end"] == "2026-09-24" and riga["interval"] == "15m"
    assert r["oos_rows"][1]["direction"] == "short"


def test_il_worker_passa_le_righe_al_main():
    """Il collegamento e' letterale, quindi si controlla nel sorgente: il worker
    accoda `oos_rows` e le ritorna come ottavo elemento; il main le spacchetta."""
    import inspect

    uno = inspect.getsource(d._disc_one)
    assert 'rows.extend(r.get("oos_rows") or [])' in uno
    assert "near[:10]}, rows)" in uno
    main = inspect.getsource(d.main)
    assert "summary, diag, rows in parallel_map(" in main
    assert "scrivi_dataset_selettore(" in main


# --------------------------------------------------------------------------- #
# scrittura del file                                                           #
# --------------------------------------------------------------------------- #
class _Fb:
    def __init__(self, rompi=False):
        self.docs, self.rompi = {}, rompi

    def set_doc(self, coll, doc, data):
        if self.rompi:
            raise RuntimeError("firestore giu'")
        self.docs[f"{coll}/{doc}"] = data


def _righe(n, fam="reversion"):
    return [{"symbol": "XUSDT", "strategy": "gen_x", "direction": "long", "regime": "sideways",
             "entry_ts": 1.0 + i, "pnl_pct": 0.01, "pnl": 1.0, "is_win": True, "mfe_r": 1.0,
             "bars_held": 3, "hour": 9, "famiglia": fam, "feats": {"rsi": 30.0, "bb_pos": None},
             "run_end": "2026-09-24", "interval": "15m"} for i in range(n)]


def test_scrittura_in_append_e_riepilogo_su_firestore(tmp_path, monkeypatch):
    monkeypatch.setattr(d, "SELETTORE_DIR", str(tmp_path / "sel"))
    fb = _Fb()
    path = d.scrivi_dataset_selettore(fb, _righe(3) + _righe(1, "momentum"),
                                      "2026-09-24", "15m", n_pairs=2)
    assert path == os.path.join(str(tmp_path / "sel"), "2026-09-24_15m.jsonl")
    # secondo giro dello stesso giorno: si ACCODA, non si sovrascrive
    d.scrivi_dataset_selettore(fb, _righe(2), "2026-09-24", "15m", n_pairs=1)
    with open(path, encoding="utf-8") as fh:
        righe = [json.loads(l) for l in fh if l.strip()]
    assert len(righe) == 6
    assert righe[0]["feats"] == {"rsi": 30.0, "bb_pos": None}
    doc = fb.docs["selector/dataset"]
    assert doc["n_rows_run"] == 2 and doc["n_pairs_run"] == 1     # l'ULTIMO giro
    assert doc["run_end"] == "2026-09-24" and doc["interval"] == "15m"
    assert doc["file"] == path
    assert doc["per_famiglia"] == {"reversion": 2}
    assert doc["updated_at"] > 0


def test_senza_righe_non_si_scrive_niente(tmp_path, monkeypatch):
    monkeypatch.setattr(d, "SELETTORE_DIR", str(tmp_path / "sel"))
    fb = _Fb()
    assert d.scrivi_dataset_selettore(fb, [], "2026-09-24", "15m", 0) is None
    assert not (tmp_path / "sel").exists()
    assert fb.docs == {}


def test_la_scrittura_e_fail_open(tmp_path, monkeypatch):
    """Ne' un Firestore giu' ne' una cartella non scrivibile fanno fallire il
    giro: il registro delle coppie vale piu' del dataset."""
    monkeypatch.setattr(d, "SELETTORE_DIR", str(tmp_path / "sel"))
    path = d.scrivi_dataset_selettore(_Fb(rompi=True), _righe(1), "2026-09-24", "15m", 1)
    assert path is not None and os.path.exists(path)         # il file c'e' comunque
    # cartella impossibile (un file al suo posto)
    (tmp_path / "blocco").write_text("x")
    monkeypatch.setattr(d, "SELETTORE_DIR", str(tmp_path / "blocco"))
    assert d.scrivi_dataset_selettore(_Fb(), _righe(1), "2026-09-24", "15m", 1) is None


def test_il_dataset_non_finisce_in_git():
    with open(os.path.join(os.path.dirname(__file__), "..", ".gitignore")) as fh:
        assert "data/selettore/" in fh.read()
