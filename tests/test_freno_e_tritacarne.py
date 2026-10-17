"""IL FRENO CHE NON FRENAVA, IL TRITACARNE, LE GEMELLE, LE PAROLE CHE MANCAVANO.

21 settembre 2026, in un giorno: MUBARAKUSDT +37% in trenta ore con RSI a 88 e noi
short; USELESSUSDT tre short consecutivi mentre saliva (stop 11:00, rientro 11:01,
stop 11:25); rischio per trade 0,91% dove il freno sul controtrend avrebbe dovuto
dimezzarlo. Quattro cause, tutte nel codice da luglio, nessuna letta:

  1. il rilevatore di regime chiamava «incertezza» qualunque cosa con volatilita'
     alta — quindi PIU' una coin correva, MENO era «in trend», e il freno, che
     legge il trend, restava a zero;
  2. l'anti-whipsaw esisteva nel bot ed era ignorato in parita' perche' il gate
     non ce l'aveva: il gate rientrava alla candela dopo, il bot al minuto dopo;
  3. tre strategie su USELESSUSDT con PF 1,541 / 1,541 / 1,54: la stessa scommessa
     con id diversi, che il bot metteva in fila dopo ogni stop;
  4. nel vocabolario non c'era modo di dire «questa non e' un'oscillazione, e' una
     salita verticale», e `min_adx` selezionava apposta i trend forti da vendere.

Questi test tengono ferme le correzioni, e soprattutto i loro CONFINI: cosa
cambia e cosa resta identico, perche' la parita' gate<->paper e' l'unica cosa che
questo sistema fa con precisione e ogni correzione qui e' stata fatta su entrambi
i lati o su nessuno.
"""
import inspect
import types
from datetime import datetime, timezone

import pytest

from backtesting.data_loader import _synthetic
from backtesting.engine import Backtester, cooldown_bars
from bot.agents.regime_detector import RegimeDetector
from bot.config import settings
from bot.core.models import AssetSnapshot, Direction, IndicatorSnapshot, Regime


# --------------------------------------------------------------------------- #
# 1) REGIME: un trend violento e' un trend                                    #
# --------------------------------------------------------------------------- #
def _btc(*, ema_fast=100.0, ema_slow=100.0, atr=1.0, close=100.0, macd_hist=0.0):
    return AssetSnapshot(symbol="BTCUSDT", price=close, indicators={
        "1h": IndicatorSnapshot(timeframe="1h", ema_fast=ema_fast, ema_slow=ema_slow,
                                atr=atr, close=close, macd_hist=macd_hist)})


D = RegimeDetector()


def test_una_salita_verticale_e_un_trend_non_un_incertezza():
    """IL CASO MUBARAK. EMA nettamente separate verso l'alto, momentum positivo,
    ATR al 6% del prezzo: prima era «incertezza», cioe' zero per il freno. E' un
    trend, il piu' violento che ci sia."""
    r = D.detect(_btc(ema_fast=108.0, ema_slow=100.0, atr=6.0, macd_hist=2.0))
    assert r is Regime.BULL_TRENDING
    r = D.detect(_btc(ema_fast=92.0, ema_slow=100.0, atr=6.0, macd_hist=-2.0))
    assert r is Regime.BEAR_TRENDING


def test_volatilita_alta_SENZA_direzione_resta_incertezza():
    """Il confine della correzione: la volatilita' decide solo quando una
    direzione non c'e'. EMA sovrapposte e ATR al 5% e' ancora incertezza."""
    assert D.detect(_btc(atr=5.0)) is Regime.HIGH_UNCERTAINTY


def test_ema_e_momentum_discordi_restano_incertezza_anche_con_volatilita_alta():
    r = D.detect(_btc(ema_fast=108.0, ema_slow=100.0, atr=6.0, macd_hist=-2.0))
    assert r is Regime.HIGH_UNCERTAINTY


def test_il_trend_violento_porta_l_incertezza_come_secondario():
    """Non si butta via l'informazione: la volatilita' resta visibile come regime
    secondario, che e' esattamente il ruolo che `detect_detailed` gli aveva
    gia' dato per i casi vicini alla soglia."""
    r = D.detect_detailed(_btc(ema_fast=108.0, ema_slow=100.0, atr=6.0, macd_hist=2.0))
    assert r.primary is Regime.BULL_TRENDING
    assert r.secondary is Regime.HIGH_UNCERTAINTY


def test_il_freno_ora_scatta_su_una_salita_verticale():
    """La conseguenza che conta: short contro una coin in salita verticale ->
    controtrend -> size ridotta. Prima `_trend_align` riceveva «incertezza» e
    restituiva zero."""
    from bot.orchestrator.orchestrator import Orchestrator

    regime = D.detect(_btc(ema_fast=108.0, ema_slow=100.0, atr=6.0, macd_hist=2.0))
    assert Orchestrator._trend_align(regime, Direction.SHORT.value) == -1.0


def test_il_pavimento_del_freno_e_una_manopola():
    src = inspect.getsource(__import__("bot.orchestrator.orchestrator",
                                       fromlist=["Orchestrator"]).Orchestrator.decide_all)
    assert "settings.TREND_TILT_FLOOR" in src and "max(0.5," not in src
    assert 0.0 < settings.TREND_TILT_FLOOR <= 1.0


# --------------------------------------------------------------------------- #
# 2) TRITACARNE: la stessa attesa dopo uno stop, nel motore E nel bot         #
# --------------------------------------------------------------------------- #
def test_le_ore_diventano_barre_con_una_sola_conversione():
    assert cooldown_bars(1.0, 0.25) == 4      # 1h a 15m
    assert cooldown_bars(1.0, 1.0) == 1
    assert cooldown_bars(0.3, 1.0) == 1       # mai zero se il cooldown e' attivo
    assert cooldown_bars(0.0, 0.25) == 0      # spento
    assert cooldown_bars(4.0, 0.0) == 0


class _SempreLong:
    """Entra a ogni barra, con lo stop cosi' vicino da prenderlo quasi subito:
    e' il tritacarne in laboratorio."""
    name = "sempre_long"
    params: dict = {}

    def is_active_in(self, regime):
        return True

    def generate_signal(self, snap, ctx=None):
        return types.SimpleNamespace(direction=Direction.LONG,
                                     suggested_stop=snap.price * 0.999,
                                     suggested_target=snap.price * 1.20,
                                     confidence=60.0, strategy=self.name)


def _giro(cooldown_hours: float, monkeypatch) -> int:
    monkeypatch.setattr(settings, "COOLDOWN_HOURS", cooldown_hours)
    candles = _synthetic(datetime(2023, 1, 1, tzinfo=timezone.utc),
                         datetime(2023, 2, 1, tzinfo=timezone.utc))
    st = Backtester(window=50).run_strategy(_SempreLong(), "BTCUSDT", candles)
    return len(st.trades)


def test_nel_motore_dopo_uno_stop_in_perdita_si_aspetta(monkeypatch):
    """Il numero che decide: con l'attesa attiva i rientri immediati spariscono e
    i trade sono meno. Prima il motore ripartiva sempre dalla candela dopo."""
    senza = _giro(0.0, monkeypatch)
    con = _giro(4.0, monkeypatch)          # 4 barre a interval_hours=1.0
    assert senza > 0
    assert con < senza, f"con cooldown {con} trade, senza {senza}: l'attesa non agisce"


def test_l_attesa_scatta_solo_su_uno_stop_IN_PERDITA():
    """Uno stop alzato dal profit-lock che chiude in guadagno non e' una trappola:
    il codice deve guardare `pnl_pct <= 0`, non solo «e' uscito su uno stop»."""
    src = inspect.getsource(Backtester.run_strategy)
    assert "if was_stop and pnl_pct <= 0 and settings.COOLDOWN_HOURS > 0:" in src
    assert "i += cooldown_bars(settings.COOLDOWN_HOURS, self.interval_hours)" in src


def test_ogni_uscita_su_stop_marca_was_stop():
    """Tre rami di uscita su stop (scale-out, classico long, classico short): se
    uno non marca il flag, quel tipo di trade rientra subito e la parita' col bot
    si rompe in silenzio proprio li'."""
    src = inspect.getsource(Backtester.run_strategy)
    assert src.count("was_stop = True") == 3


def test_nel_bot_il_cooldown_vale_anche_in_parita():
    """Era `if not settings.BACKTEST_PARITY and now < cd_until` — cioe' spento
    proprio nella modalita' in cui giriamo. Ora il gate ha la stessa attesa,
    quindi il bot puo' applicarla senza divergere."""
    from bot.main import TradingBot

    src = inspect.getsource(TradingBot._try_open)
    assert "if now < cd_until:" in src
    assert "not settings.BACKTEST_PARITY and now < cd_until" not in src


# --------------------------------------------------------------------------- #
# 3) GEMELLE: la stessa logica ha la stessa firma                             #
# --------------------------------------------------------------------------- #
from scripts.discover_strategies import firma_spec, gemelle_validate, scarta_gemelle  # noqa: E402


def _spec(sid, rsi_high=70.0, rr=2.0, min_adx=20.0, kinds=("rsi_extreme",)):
    feats = []
    for k in kinds:
        f = {"kind": k}
        if k == "rsi_extreme":
            f.update(low=30.0, high=rsi_high)
        feats.append(f)
    return {"id": sid, "features": feats, "rr": rr, "min_adx": min_adx,
            "atr_mult_stop": 1.5, "volume_mult": 0.0}


def test_due_spec_che_differiscono_solo_per_rr_sono_la_stessa():
    """Sotto scale-out `rr` non tocca le uscite (backlog B2bis): due spec uguali
    tranne `rr` operano in modo identico e devono avere la stessa firma. E' quasi
    certamente cosa sono le tre gemelle di USELESSUSDT."""
    assert firma_spec(_spec("a", rr=1.5)) == firma_spec(_spec("b", rr=3.0))


def test_soglie_vicine_sono_la_stessa_soglia_soglie_lontane_no():
    assert firma_spec(_spec("a", rsi_high=70.0)) == firma_spec(_spec("b", rsi_high=72.0))
    assert firma_spec(_spec("a", rsi_high=70.0)) != firma_spec(_spec("b", rsi_high=80.0))


def test_feature_diverse_sono_spec_diverse():
    assert firma_spec(_spec("a", kinds=("rsi_extreme",))) != \
        firma_spec(_spec("b", kinds=("rsi_extreme", "bb_touch")))


def test_le_gemelle_nuove_vengono_scartate_le_note_restano():
    """«Non buttiamo via nulla»: cio' che e' gia' nel registro passa intatto.
    Si impedisce solo che entrino altre copie."""
    nota = _spec("gen_nota", rr=2.0)
    existing = {"gen_nota": nota}
    candidate = [nota, _spec("gen_copia", rr=2.5), _spec("gen_diversa", rsi_high=85.0),
                 _spec("gen_copia2", rsi_high=85.0, rr=1.5)]
    tenute, scartate = scarta_gemelle(candidate, existing)
    assert [s["id"] for s in tenute] == ["gen_nota", "gen_diversa"]
    assert scartate == 2


def test_le_gemelle_gia_validate_si_VEDONO_e_non_si_toccano():
    existing = {"g1": _spec("g1", rr=1.5), "g2": _spec("g2", rr=3.0),
                "g3": _spec("g3", rsi_high=85.0)}
    pairs = {"USELESSUSDT|g1": {"pass_count": 3}, "USELESSUSDT|g2": {"pass_count": 3},
             "USELESSUSDT|g3": {"pass_count": 3}, "ORCAUSDT|g1": {"pass_count": 1}}
    out = gemelle_validate(pairs, existing)
    assert out == [("USELESSUSDT", ["g1", "g2"])]
    assert "del pairs" not in inspect.getsource(gemelle_validate)


# --------------------------------------------------------------------------- #
# 4) LE PAROLE CHE MANCAVANO: «non sovraesteso» e «trend debole»              #
# --------------------------------------------------------------------------- #
from bot.strategies.generated import FEATURE_LIBRARY  # noqa: E402


class _Ind:
    def __init__(self, atr=1.0, ema_slow=100.0, adx=None):
        self.atr, self.ema_slow, self.adx = atr, ema_slow, adx


def test_non_sovraesteso_blocca_ENTRAMBI_i_lati_quando_il_prezzo_corre():
    """MUBARAK: prezzo a molte ATR dalla media. Per `rsi_extreme` era il segnale
    di vendita piu' forte possibile; con questo mattoncino in AND la spec tace."""
    fn = FEATURE_LIBRARY["not_stretched"]
    assert fn(_Ind(atr=1.0, ema_slow=100.0), 104.0, {"stretch_max": 3.0}) == (False, False)
    assert fn(_Ind(atr=1.0, ema_slow=100.0), 102.0, {"stretch_max": 3.0}) == (True, True)
    assert fn(_Ind(atr=0.0), 102.0, {}) is None


def test_adx_sotto_e_l_opposto_di_min_adx():
    fn = FEATURE_LIBRARY["adx_below"]
    assert fn(_Ind(adx=40.0), 1.0, {"adx_hi": 30.0}) == (False, False)
    assert fn(_Ind(adx=20.0), 1.0, {"adx_hi": 30.0}) == (True, True)


def test_le_condizioni_nuove_sono_nel_vocabolario_e_nel_prompt():
    """Aggiunte al motore ma non al generatore/AI sarebbero mattoncini che nessuno
    puo' usare: il gate non potrebbe mai misurarli."""
    import random

    from bot.ai import hypotheses as h
    from bot.strategies.generator import _CONDITIONAL, _feature_with_params

    for nome, par in (("not_stretched", "stretch_max"), ("adx_below", "adx_hi")):
        assert nome in _CONDITIONAL, nome
        assert par in _feature_with_params(nome, random.Random(0)), nome
        assert f"feature {nome}: richiede" in h.SYSTEM and par in h.SYSTEM
        spec, motivo = h._esamina_spec({
            "mechanism": "prova", "features": [{"kind": "rsi_extreme", "low": 30, "high": 70},
                                               _feature_with_params(nome, random.Random(0))],
            "atr_mult_stop": 1.5, "rr": 2.0, "min_adx": 0.0, "volume_mult": 0.0})
        assert spec is not None, f"{nome} scartata: {motivo}"
