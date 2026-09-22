"""LA CONFERMA A 1 ORA — «guardare la moneta con due occhi», come mattoncino.

Idea del proprietario (22 set 2026): il trader opera a 15 minuti ma prima di
aprire guarda l'ora. Qui NON e' una regola per tutti: e' una feature direzionale
che il generatore puo' usare e il gate misura coin per coin. La sua paura era
«ridurre troppo i trade»: come feature, le strategie senza conferma continuano
a operare, e quelle con conferma entrano solo se il gate le valida anche con
meno segnali. Il rischio lo filtra il gate, non arriva al paper.
"""
import inspect

from bot.strategies.generated import HTF_FEATURES, FEATURE_LIBRARY, GeneratedStrategy, feature_esiste


class _H:
    def __init__(self, fast, slow):
        self.ema_fast, self.ema_slow = fast, slow


def test_long_solo_con_l_ora_in_salita_short_solo_in_discesa():
    fn = HTF_FEATURES["htf_confirm"]
    assert fn(_H(11, 10), 1.0, {}) == (True, False)
    assert fn(_H(9, 10), 1.0, {}) == (False, True)
    assert fn(_H(10, 10), 1.0, {}) == (False, False), "medie uguali: nessuna conferma"


def test_senza_l_ora_non_si_inventa_un_segnale():
    """Stessa regola del mercato e dei dati sintetici: manca il dato, niente
    trade — non un trade deciso su un'ora immaginaria."""
    assert HTF_FEATURES["htf_confirm"](None, 1.0, {}) is None
    assert HTF_FEATURES["htf_confirm"](_H(None, 10), 1.0, {}) is None


def test_la_spec_legge_l_ora_dallo_snapshot_della_STESSA_coin():
    """Il caso MUBARAK: a 15 minuti RSI a 88 (segnale short), a 1 ora medie in
    salita netta. Con la conferma in AND lo short non nasce; senza, nasce.
    E l'ora viene da `asset.ind("1h")`, che il backtest porta reale (senza
    look-ahead) e il bot calcola fra i suoi TIMEFRAMES."""
    class _I:
        rsi = 88.0
        ema_fast = ema_slow = 1.0
        bb_upper = bb_lower = bb_mid = 1.0
        atr = 1.0
        adx = None
        volume = volume_sma = None

    class _Asset:
        price = 1.0
        symbol = "MUBARAKUSDT"
        regime = None

        def ind(self, tf):
            return _H(11, 10) if tf == "1h" else _I()

    con = GeneratedStrategy({"id": "gen_c", "features": [
        {"kind": "rsi_extreme", "low": 30, "high": 70}, {"kind": "htf_confirm"}],
        "atr_mult_stop": 1.5, "rr": 2.0})
    senza = GeneratedStrategy({"id": "gen_s", "features": [
        {"kind": "rsi_extreme", "low": 30, "high": 70}],
        "atr_mult_stop": 1.5, "rr": 2.0})
    assert con.usa_htf is True and senza.usa_htf is False
    assert con.generate_signal(_Asset(), None) is None, "lo short contro l'ora in salita non deve nascere"
    assert senza.generate_signal(_Asset(), None) is not None


def test_e_nel_vocabolario_ovunque():
    """Motore, generatore casuale, validatore e prompt: se manca in uno, o
    nessuno la propone o il validatore la scarta come inesistente."""
    from bot.ai import hypotheses as h
    from bot.strategies.generator import _DIRECTIONAL

    assert "htf_confirm" in _DIRECTIONAL
    assert feature_esiste("htf_confirm")
    assert "htf_confirm" not in FEATURE_LIBRARY, "firma diversa: non va nella libreria normale"
    assert "set(HTF_FEATURES)" in inspect.getsource(h.propose)
    spec, motivo = h._esamina_spec({
        "mechanism": "compra la debolezza solo se l'ora sale",
        "features": [{"kind": "rsi_extreme", "low": 30, "high": 70}, {"kind": "htf_confirm"}],
        "atr_mult_stop": 1.5, "min_adx": 0.0, "volume_mult": 0.0})
    assert spec is not None, motivo


def test_l_ora_si_risolve_solo_se_la_spec_la_usa():
    """La lezione del 22 set (il contesto di mercato che sforava le 3 ore):
    niente lavoro per candela per chi non lo chiede."""
    src = inspect.getsource(GeneratedStrategy.generate_signal)
    assert 'asset.ind("1h") if self.usa_htf else None' in src


def test_l_ipotesi_opposta_esiste_lo_short_sul_calo_momentaneo():
    """Il proprietario: «se la short vuole sfruttare un calo momentaneo anche se
    il trend e' in salita, questo trade DEVE aprirsi». `htf_fade` vende
    l'eccesso rispetto alla media oraria, senza guardare la direzione del
    trend. Con la conferma sono incompatibili: il gate sceglie."""
    import random

    from bot.ai import hypotheses as h
    from bot.strategies.generator import _DIRECTIONAL, _INCOMPATIBLE, _feature_with_params

    fn = HTF_FEATURES["htf_fade"]

    class _S:
        ema_fast, ema_slow = 11.0, 10.0      # trend orario in salita

    assert fn(_S(), 10.5, {"htf_gap": 0.02}) == (False, True), "sopra la media: short si', anche col trend su"
    assert fn(_S(), 9.5, {"htf_gap": 0.02}) == (True, False)
    assert fn(_S(), 10.1, {"htf_gap": 0.02}) == (False, False), "troppo vicino alla media: nessuna delle due"
    assert fn(None, 10.0, {}) is None
    assert "htf_fade" in _DIRECTIONAL and frozenset({"htf_confirm", "htf_fade"}) in _INCOMPATIBLE
    assert "htf_gap" in _feature_with_params("htf_fade", random.Random(0))
    spec, motivo = h._esamina_spec({"mechanism": "vendi l'eccesso orario",
                                    "features": [{"kind": "htf_fade", "htf_gap": 0.01}],
                                    "atr_mult_stop": 1.5, "min_adx": 0.0, "volume_mult": 0.0})
    assert spec is not None, motivo
    assert h._esamina_spec({"mechanism": "x", "features": [{"kind": "htf_fade", "htf_gap": 0.01}, {"kind": "htf_confirm"}],
                            "atr_mult_stop": 1.5, "min_adx": 0.0, "volume_mult": 0.0})[0] is None
