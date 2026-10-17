"""LA SESSIONE ORARIA LEGGE LA CANDELA, NON L'OROLOGIO (27 set 2026, backlog J13).

Ops 0310/0311 (la classe «IGNOTO» dell'indagine sugli ingressi, 5 trade tutti
di `gen_6d06dca0` = «rsi_extreme 20/75 AND session 8-16»): `_feat_session`
leggeva `datetime.now()`. Nel backtest ogni barra della storia prendeva l'ora
in cui GIRAVA il gate (alle 03:30 UTC «fuori sessione» ovunque -> solo short,
alle 13:00 «dentro» ovunque -> solo long); nel bot l'ora era quella della
decisione, per cui alle 03:30 apriva short e il motore rigirato alle 13 non
trovava il segnale.

Qui si difende la parita': motore e bot portano `AssetSnapshot.ts` (apertura
dell'ultima candela CHIUSA del timeframe primario) e la feature giudica su
quell'ora, qualunque cosa dica l'orologio; `spiega` stampa l'ora della candela;
senza `ts` si torna all'orologio, con un avviso stampato una volta sola.
"""
import datetime as _dt_mod
from datetime import datetime, timedelta, timezone

import pytest

from backtesting.engine import Backtester
from bot.core.indicators import compute_indicator_frame
from bot.core.models import AssetSnapshot, Candle, IndicatorSnapshot, Regime, epoch_utc
from bot.strategies import generated as g
from bot.strategies.generated import GeneratedStrategy
from tests.test_spiega import _ind, _serie

SPEC = {"id": "gen_sessione", "features": [{"kind": "rsi_extreme", "low": 20.0, "high": 75.0},
                                           {"kind": "session", "hour_from": 8, "hour_to": 16}],
        "atr_mult_stop": 1.5, "rr": 2.0}


def _orologio(monkeypatch, ora: int):
    """Inchioda `datetime.now()` a un'ora UTC: la feature NON deve accorgersene."""
    class _Fisso(datetime):
        @classmethod
        def now(cls, tz=None):
            return datetime(2026, 9, 27, ora, 7, tzinfo=timezone.utc)
    monkeypatch.setattr(_dt_mod, "datetime", _Fisso)
    assert _dt_mod.datetime.now(timezone.utc).hour == ora


def _asset(ts_ora: int | None, rsi: float = 80.0) -> AssetSnapshot:
    ts = None if ts_ora is None else datetime(2026, 9, 18, ts_ora, 30, tzinfo=timezone.utc).timestamp()
    return AssetSnapshot(symbol="ORCAUSDT", price=1.42, close_chiusa=1.419, ts=ts,
                         regime=Regime.SIDEWAYS, indicators={"15m": _ind(rsi=rsi)})


@pytest.fixture(autouse=True)
def _avviso_pulito():
    g._AVVISO_ORA_CALENDARIO["stampato"] = False
    yield
    g._AVVISO_ORA_CALENDARIO["stampato"] = False


def test_la_sessione_giudica_l_ora_della_candela_e_ignora_l_orologio(monkeypatch):
    # AGGIORNATO il 27 set 2026 (sera): la sessione e' un FILTRO per i due lati
    # (dentro -> entrambi ammessi, fuori -> nessuno), non sceglie piu' il lato.
    # Il punto del test resta lo stesso: conta l'ora della CANDELA, non l'orologio.
    st = GeneratedStrategy(SPEC)
    # rsi 80 -> solo short; la sessione 8-16 decide se si opera
    _orologio(monkeypatch, 13)                        # orologio DENTRO la sessione
    notte = st.spiega(_asset(3))                      # candela delle 03:30 UTC
    assert notte["ora_utc"] == 3
    assert notte["features"]["session"]["valori"]["ora_utc"] == 3
    assert notte["features"]["session"]["valori"]["dentro"] is False
    assert notte["features"]["session"]["long"] is False and notte["features"]["session"]["short"] is False
    assert notte["direzione_finale"] is None          # fuori sessione: nessun segnale
    assert "fermano session" in notte["motivo"]
    assert st.generate_signal(_asset(3)) is None

    _orologio(monkeypatch, 3)                         # orologio FUORI dalla sessione
    giorno = st.spiega(_asset(13))                    # candela delle 13:30 UTC
    assert giorno["ora_utc"] == 13
    assert giorno["features"]["session"]["valori"]["dentro"] is True
    assert giorno["features"]["session"]["long"] is True and giorno["features"]["session"]["short"] is True
    assert giorno["direzione_finale"] == "short"      # dentro: decide l'rsi, che dice short
    assert st.generate_signal(_asset(13)) is not None


def test_semantica_dal_27_set_dentro_entrambi_fuori_nessuno():
    # AGGIORNATO il 27 set 2026: prima dentro -> (True, False) e fuori -> (False, True)
    # (la feature sceglieva il lato). Ora e' un filtro: dentro -> (True, True),
    # fuori -> (False, False); giro di mezzanotte compreso. Il dettaglio dei due
    # lati e' in tests/test_sessione_filtro.py.
    f = {"kind": "session", "hour_from": 8, "hour_to": 16}
    assert g._feat_session(None, 1.0, f, ora=8) == (True, True)
    assert g._feat_session(None, 1.0, f, ora=15) == (True, True)
    assert g._feat_session(None, 1.0, f, ora=16) == (False, False)
    assert g._feat_session(None, 1.0, f, ora=3) == (False, False)
    notturna = {"kind": "session", "hour_from": 22, "hour_to": 4}
    assert g._feat_session(None, 1.0, notturna, ora=23) == (True, True)
    assert g._feat_session(None, 1.0, notturna, ora=2) == (True, True)
    assert g._feat_session(None, 1.0, notturna, ora=12) == (False, False)


def test_lo_snapshot_del_motore_porta_l_apertura_della_barra():
    candles = _serie(400)
    frame = compute_indicator_frame(candles)
    bt = Backtester(window=200, interval_hours=0.25)
    snap = bt._snapshot_from_frame("XUSDT", frame, 300)
    assert snap.ts == candles[300].open_time.timestamp() == epoch_utc(frame.iloc[300]["open_time"])
    assert datetime.fromtimestamp(snap.ts, timezone.utc).hour == candles[300].open_time.hour


def test_epoch_utc_legge_un_datetime_senza_fuso_come_utc():
    naive = datetime(2026, 9, 18, 3, 30)
    aware = datetime(2026, 9, 18, 3, 30, tzinfo=timezone.utc)
    assert epoch_utc(naive) == epoch_utc(aware) == aware.timestamp()
    assert datetime.fromtimestamp(epoch_utc(naive), timezone.utc).hour == 3


def test_build_snapshot_porta_l_apertura_dell_ultima_candela_chiusa():
    from bot.agents.price_agent import PriceAgent
    from bot.config import settings
    now = datetime.now(timezone.utc)
    t0 = (now - timedelta(hours=60)).replace(minute=0, second=0, microsecond=0)

    def _candles(symbol, interval, limit=200):
        out = []
        for k in range(150):
            px = 100.0 + (k % 7) * 0.1
            out.append(Candle(open_time=t0 + timedelta(minutes=15 * k), open=px, high=px + 0.2,
                              low=px - 0.2, close=px, volume=100.0,
                              close_time=t0 + timedelta(minutes=15 * (k + 1))))
        out[-1] = out[-1].model_copy(update={"close": 123.45, "close_time": now + timedelta(minutes=10)})
        return out

    pa = PriceAgent.__new__(PriceAgent)
    pa.get_candles = _candles
    pa.get_premium = lambda symbol: {}
    pa.get_ticker_24h = lambda symbol: {}
    pa.get_open_interest = lambda symbol: None
    snap = pa.build_snapshot("XUSDT")
    chiuse = _candles("XUSDT", settings.ORCHESTRATOR_TIMEFRAME)[:-1]
    assert snap.ts == chiuse[-1].open_time.timestamp()       # apertura dell'ultima CHIUSA
    assert snap.ts != _candles("XUSDT", "15m")[-1].open_time.timestamp()   # non quella in formazione
    assert snap.close_chiusa == chiuse[-1].close


def test_il_backtest_di_una_spec_con_sessione_non_dipende_dall_orologio(monkeypatch):
    candles = _serie(600)
    frame = compute_indicator_frame(candles)
    spec = {"id": "s", "features": [{"kind": "rsi_extreme", "low": 35.0, "high": 65.0},
                                    {"kind": "session", "hour_from": 8, "hour_to": 16}]}
    esiti = {}
    for ora in (3, 13):
        _orologio(monkeypatch, ora)
        bt = Backtester(window=200, interval_hours=0.25)
        st = bt.run_strategy(GeneratedStrategy(spec), "XUSDT", candles, frame=frame)
        esiti[ora] = [(t.entry_ts, t.direction, round(t.pnl_pct, 10)) for t in st.trades]
    assert esiti[3], "la serie deve produrre trade, altrimenti il confronto e' vuoto"
    assert esiti[3] == esiti[13]
    # e i trade seguono la candela: dal 27 set 2026 (sera) la sessione e' un
    # filtro, quindi TUTTI i segnali stanno dentro 8-16, in entrambi i versi
    # (`entry_ts` e' l'apertura della barra del SEGNALE, `candles[i].open_time`)
    lati = set()
    for entry_ts, direction, _ in esiti[3]:
        ora_segnale = datetime.fromtimestamp(entry_ts, timezone.utc).hour
        assert 8 <= ora_segnale < 16, (ora_segnale, direction)
        lati.add(direction)
    assert lati == {"long", "short"}     # entrambi i lati: dentro la fascia decide l'rsi


def test_spiega_stampa_l_ora_della_candela(monkeypatch):
    from scripts.ingressi_report import fmt_verdetto
    _orologio(monkeypatch, 13)
    st = GeneratedStrategy(SPEC)
    v = st.spiega(_asset(3))
    testo = fmt_verdetto(v)
    assert "ora_utc=3" in testo and "ora_utc=13" not in testo


def test_senza_ts_si_torna_all_orologio_e_lo_si_dice_una_volta(monkeypatch, capsys):
    _orologio(monkeypatch, 13)
    st = GeneratedStrategy(SPEC)
    v1 = st.spiega(_asset(None))
    v2 = st.spiega(_asset(None))
    assert v1["ora_utc"] == v2["ora_utc"] == 13
    out = capsys.readouterr().out
    assert out.count("[session] ora dal calendario: snapshot senza ts") == 1


def test_una_spec_senza_sessione_non_legge_l_ora_e_non_avvisa(capsys):
    st = GeneratedStrategy({"id": "r", "features": [{"kind": "rsi_extreme", "low": 20.0, "high": 75.0}]})
    v = st.spiega(_asset(None))
    assert "ora_utc" not in v and st.usa_sessione is False
    assert "[session]" not in capsys.readouterr().out


def test_lo_strumento_degli_ingressi_mette_la_candela_del_paper_sullo_snapshot():
    from scripts.ingressi_report import Diagnosta
    t = {"entry_price": 1.42, "indicators_at_entry": {"15m": {"rsi": 80.0, "close": 1.419, "atr": 0.01}}}
    b = datetime(2026, 9, 18, 3, 30, tzinfo=timezone.utc).timestamp()
    snap = Diagnosta.snapshot_dal_trade("ORCAUSDT", t, b)
    assert snap is not None and snap.ts == b
    assert Diagnosta.snapshot_dal_trade("ORCAUSDT", t).ts is None


def test_gate_progress_conta_le_validate_con_la_sessione():
    from scripts.gate_progress import riga_sessione
    specs = {"gen_a": {"features": [{"kind": "session", "hour_from": 8, "hour_to": 16}]},
             "gen_b": {"features": [{"kind": "rsi_extreme"}]}}
    riga = riga_sessione(["ORCAUSDT|gen_a", "VETUSDT|gen_a", "XUSDT|gen_b", "YUSDT|gen_z"], specs)
    assert riga.startswith("  FEATURE session: 2 validate su 4 usano la sessione oraria")
    assert "fino al 27 set valutata con l'orologio del giro, non della candela: passaggi da rifare" in riga
    assert riga.endswith(" · 1 senza spec nel documento")     # senza `pairs`: nessuna azzerata
    assert riga_sessione([], None).startswith("  FEATURE session: 0 validate su 0")


def test_la_discovery_conta_le_spec_note_con_la_sessione():
    from scripts.discover_strategies import riga_cervello_sessione
    existing = {"gen_a": {"features": [{"kind": "session", "hour_from": 8, "hour_to": 16}]},
                "gen_b": {"features": [{"kind": "bb_touch"}]}, "rotto": "non una spec"}
    riga = riga_cervello_sessione(existing)
    assert riga.startswith("[cervello] sessione oraria: 1 spec note su 3 usano `session`")
    assert "passaggi azzerati" in riga
    assert riga_cervello_sessione(None).startswith("[cervello] sessione oraria: 0 spec note su 0")


def test_usa_sessione():
    assert g.usa_sessione(SPEC) is True
    assert g.usa_sessione({"features": [{"kind": "rsi_extreme"}]}) is False
    assert g.usa_sessione({"features": ["session"]}) is False
    assert g.usa_sessione(None) is False
