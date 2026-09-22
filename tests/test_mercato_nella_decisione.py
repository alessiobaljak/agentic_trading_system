"""IL MERCATO ENTRA NELLA DECISIONE — come ingrediente, non come veto.

21 settembre 2026, USELESSUSDT: due short consecutivi dentro una giornata di
rialzo, -16,90 in quaranta minuti. Le feature che li hanno prodotti dicono «RSI
sopra 70 -> vendi» e «prezzo sopra la banda -> vendi», e guardano SOLO quella
coin. Indagando: `scripts/discover_strategies.py` non caricava nemmeno BTC, quindi
per una strategia generata il mercato non era «poco pesato» — non era nella stanza.

La correzione NON e' vietare gli short quando il mercato sale. Dentro un rialzo ci
sono ritracciamenti del 2-3%, e prenderli e' il mestiere di una strategia di
ritorno alla media. Il punto e' che la strategia non poteva distinguere «sto
vendendo un ritracciamento» da «sto davanti a un treno». Quindi il mercato diventa
un MATTONCINO che il generatore puo' usare e il GATE misura — non una regola decisa
da me a tavolino.

Questi test tengono ferme le tre proprieta' che rendono onesta quella misura.
"""
import inspect

from bot.strategies.generated import (FEATURE_LIBRARY, MARKET_FEATURES, MARKET_SYMBOL,
                                      GeneratedStrategy, MercatoSnap,
                                      mercato_da_contesto)


def _mercato(prezzo=100.0, veloce=11.0, lenta=10.0) -> MercatoSnap:
    return MercatoSnap(prezzo, veloce, lenta)


def test_il_mercato_che_sale_favorisce_il_long_non_lo_impone():
    """`market_trend` e' una feature come le altre: dice in che direzione spinge,
    e poi il gate decide se quella spinta valga qualcosa. Non blocca niente da
    sola — con altre feature in AND puo' benissimo uscire uno short."""
    su = MARKET_FEATURES["market_trend"](None, 1.0, {}, _mercato(veloce=11, lenta=10))
    giu = MARKET_FEATURES["market_trend"](None, 1.0, {}, _mercato(veloce=9, lenta=10))
    assert su == (True, False)
    assert giu == (False, True)


def test_esiste_anche_l_ipotesi_OPPOSTA():
    """`market_fade` non e' un gemello inutile: e' l'ipotesi contraria, e serve che
    il gate possa misurarle entrambe invece di ricevere gia' decisa quella che
    credo io. Se tenessi solo `market_trend` avrei messo la mia opinione dentro il
    vocabolario."""
    su = MARKET_FEATURES["market_fade"](None, 1.0, {}, _mercato(veloce=11, lenta=10))
    assert su == (False, True)


def test_la_forza_relativa_permette_di_shortare_in_un_mercato_che_sale():
    """LA RISPOSTA VERA alla domanda del proprietario: «non vuol dire che se il
    mercato e' rialzista tutte long». Con la forza relativa una coin DEBOLE si puo'
    shortare anche mentre il mercato sale — che e' il mestiere — invece di shortare
    quella che corre piu' di tutte solo perche' ha l'RSI alto."""
    class _I:
        ema_slow = 100.0

    mercato = MercatoSnap(price=110.0, ema_fast=11.0, ema_slow=100.0)  # mercato +10%
    forte = MARKET_FEATURES["relative_strength"](_I(), 120.0, {}, mercato)   # coin +20%
    debole = MARKET_FEATURES["relative_strength"](_I(), 102.0, {}, mercato)  # coin +2%
    assert forte == (True, False), "la coin piu' forte del mercato va comprata"
    assert debole == (False, True), "la coin piu' debole va venduta, anche in rialzo"


def test_la_forza_relativa_confronta_PERCENTUALI_non_prezzi():
    """Un prezzo di 0,004 e uno di 60.000 non si confrontano. Distanze dalla media
    in percentuale si'."""
    src = inspect.getsource(MARKET_FEATURES["relative_strength"])
    assert "/ i.ema_slow" in src and "/ m.ema_slow" in src


def test_senza_mercato_non_si_inventa_un_segnale():
    """La regola dei dati sintetici, applicata qui: una spec che chiede il mercato
    dove il mercato non c'e' deve smettere di produrre segnali, non produrne di
    finti. Un trade deciso su un mercato immaginario e' peggio di nessun trade."""
    for nome, fn in MARKET_FEATURES.items():
        assert fn(None, 1.0, {}, None) is None, nome
    assert mercato_da_contesto(None, "15m") is None


def test_una_spec_che_chiede_il_mercato_tace_se_manca():
    """La prova end-to-end: `generate_signal` non deve cadere e non deve decidere."""
    class _Ind:
        rsi = 80.0
        ema_fast = ema_slow = 1.0
        bb_upper = bb_lower = bb_mid = 1.0

    class _Asset:
        price = 1.0
        symbol = "X"

        def ind(self, tf):
            return _Ind()

    spec = {"id": "gen_test", "features": [{"kind": "market_trend"}],
            "atr_mult_stop": 1.5, "rr": 2.0}
    assert GeneratedStrategy(spec).generate_signal(_Asset(), None) is None


def test_le_feature_di_mercato_NON_sono_nel_vocabolario_normale():
    """Firma diversa (`m` in piu'): se finissero in FEATURE_LIBRARY verrebbero
    chiamate con quattro argomenti su una funzione che ne prende tre, e il guasto
    apparirebbe solo al primo giro vero del gate, tre ore dopo."""
    for nome in MARKET_FEATURES:
        assert nome not in FEATURE_LIBRARY, nome


def test_il_generatore_e_l_AI_le_conoscono():
    """Aggiungerle al motore senza metterle nel vocabolario le renderebbe
    inutilizzabili: nessuno le proporrebbe mai, e il gate non potrebbe misurarle."""
    from bot.ai import hypotheses as h
    from bot.strategies.generator import _DIRECTIONAL, _INCOMPATIBLE

    for nome in MARKET_FEATURES:
        assert nome in _DIRECTIONAL, nome
    assert frozenset({"market_trend", "market_fade"}) in _INCOMPATIBLE, (
        "andare col mercato E contro il mercato insieme non lascia passare niente")
    # l'elenco mandato al modello nasce da ENTRAMBI i vocabolari, non solo da uno
    src = inspect.getsource(h.propose)
    assert "set(FEATURE_LIBRARY) | set(MARKET_FEATURES)" in src
    # e il parametro della forza relativa e' dichiarato nel prompt di sistema,
    # generato dalle stesse costanti che validano
    assert "feature relative_strength: richiede" in h.SYSTEM and "rs_gap" in h.SYSTEM


def test_il_validatore_ACCETTA_le_feature_di_mercato():
    """IL DIFETTO CHE STAVO PER INTRODURRE. Il controllo diceva
    `if kind not in FEATURE_LIBRARY`, e le feature di mercato vivono in un
    dizionario separato perche' hanno una firma diversa: il validatore avrebbe
    scartato come «inesistenti» proprio le feature appena messe nel vocabolario.
    Il modello le avrebbe proposte e nessuna sarebbe mai arrivata al gate — con lo
    stesso sintomo muto di `rr` il 20 settembre."""
    from bot.ai import hypotheses as h2

    spec, motivo = h2._esamina_spec({
        "mechanism": "compra la forza, vendi la debolezza",
        "features": [{"kind": "relative_strength", "rs_gap": 0.01}],
        "atr_mult_stop": 1.5, "rr": 2.0, "min_adx": 0.0, "volume_mult": 0.0})
    assert spec is not None, f"scartata: {motivo}"


def test_il_generatore_casuale_da_il_parametro_della_forza_relativa():
    """Proporre la feature senza il suo parametro la fa scartare dal validatore:
    e' lo scarto che il 20 settembre ha bruciato il 74% delle proposte AI."""
    import random

    from bot.strategies.generator import _feature_with_params

    f = _feature_with_params("relative_strength", random.Random(0))
    assert "rs_gap" in f


def test_il_GATE_carica_davvero_il_mercato():
    """IL DIFETTO CENTRALE, e il piu' silenzioso. `scripts/optimize.py` caricava
    BTC da sempre; la discovery — che valida TUTTE le spec che il bot opera — no.
    Senza questa riga una spec di mercato non produce segnali e viene bocciata per
    dati mancanti invece che per demerito: sembrerebbe che il mercato «non serve»,
    e sarebbe una conclusione tratta da un caricamento dimenticato."""
    from scripts import discover_strategies as d

    src = inspect.getsource(d._disc_init)
    assert "build_context(MARKET_SYMBOL" in src
    uno = inspect.getsource(d._disc_one)
    assert 'context_by_ts=_W.get("btc_ctx")' in uno


def test_anche_l_holdout_vede_il_mercato():
    """Un holdout senza mercato boccerebbe proprio le spec da misurare, e per il
    motivo sbagliato."""
    from scripts import discover_strategies as d

    src = inspect.getsource(d.evaluate_spec)
    assert "context_by_ts=context_by_ts" in src
    assert src.count("context_by_ts=context_by_ts") >= 2, (
        "OOS e holdout devono ricevere lo STESSO contesto")


def test_il_mercato_e_lo_STESSO_asset_che_usa_gia_il_gate():
    """BTC e' gia' il contesto cross-asset di `scripts/optimize.py`: usando lo
    stesso simbolo non serve una seconda pipeline dati, e ricerca e produzione non
    possono divergere su cosa sia «il mercato»."""
    from bot.strategies.momentum_cross_asset import BTC_SYMBOL

    assert MARKET_SYMBOL == BTC_SYMBOL


def test_il_mercato_si_risolve_SOLO_se_la_spec_lo_usa(monkeypatch):
    """22 set 2026: il giro e' passato da ~2h a oltre 2h53 (finestra sforata)
    perche' il contesto di mercato veniva risolto a ogni candela per ogni spec,
    anche per le ~550 senza feature di mercato. Una spec senza quelle feature
    non deve nemmeno toccarlo."""
    from bot.strategies import generated as g

    def esplode(*a, **k):
        raise AssertionError("mercato risolto per una spec che non lo usa")
    monkeypatch.setattr(g, "mercato_da_contesto", esplode)

    class _Ind:
        rsi = 80.0
        ema_fast = ema_slow = 1.0
        bb_upper = bb_lower = bb_mid = 1.0
        atr = 1.0
        adx = None
        volume = volume_sma = None

    class _Asset:
        price = 1.0
        symbol = "X"
        regime = None          # `_signal` lo legge per etichettare il segnale

        def ind(self, tf):
            return _Ind()

    senza = g.GeneratedStrategy({"id": "gen_s", "features": [{"kind": "rsi_extreme", "low": 30, "high": 70}],
                                 "atr_mult_stop": 1.5, "rr": 2.0})
    assert senza.usa_mercato is False
    senza.generate_signal(_Asset(), None)      # non deve esplodere
    con = g.GeneratedStrategy({"id": "gen_c", "features": [{"kind": "market_trend"}],
                               "atr_mult_stop": 1.5, "rr": 2.0})
    assert con.usa_mercato is True


def test_la_discovery_passa_il_contesto_solo_a_chi_lo_usa():
    from scripts import discover_strategies as d

    src = inspect.getsource(d._disc_one)
    assert 'context_by_ts=_W.get("btc_ctx") if usa_mercato else None' in src
