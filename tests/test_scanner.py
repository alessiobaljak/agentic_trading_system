"""Test dello scanner: l'universo è ordinato per VOLUME, non in ordine d'API."""
from bot.agents.market_scanner import MarketScanner, ScanResult
from bot.agents.price_agent import PriceAgent
from bot.config import settings
from bot.core.models import AssetSnapshot, Regime


class _StubPrice(PriceAgent):
    """PriceAgent con risposte HTTP finte (no rete)."""
    def _get(self, path, params):
        if path.endswith("/exchangeInfo"):
            return {"symbols": [
                {"symbol": "AAAUSDT", "contractType": "PERPETUAL", "quoteAsset": "USDT", "status": "TRADING"},
                {"symbol": "BBBUSDT", "contractType": "PERPETUAL", "quoteAsset": "USDT", "status": "TRADING"},
                {"symbol": "CCCUSDT", "contractType": "PERPETUAL", "quoteAsset": "USDT", "status": "TRADING"},
                {"symbol": "OLDUSDT", "contractType": "CURRENT_QUARTER", "quoteAsset": "USDT", "status": "TRADING"},
                {"symbol": "BUSDUSDT", "contractType": "PERPETUAL", "quoteAsset": "BUSD", "status": "TRADING"},
            ]}
        if path.endswith("/ticker/24hr"):
            return [
                {"symbol": "AAAUSDT", "quoteVolume": "1000000"},
                {"symbol": "BBBUSDT", "quoteVolume": "9000000"},   # volume più alto
                {"symbol": "CCCUSDT", "quoteVolume": "5000000"},
                {"symbol": "ZZZUSDT", "quoteVolume": "9.9e9"},      # non perpetual -> ignorato
            ]
        return None


def test_perpetual_filter_excludes_non_perp_and_non_usdt():
    syms = set(_StubPrice().list_perpetual_symbols())
    assert syms == {"AAAUSDT", "BBBUSDT", "CCCUSDT"}  # niente quarterly, niente BUSD


def test_ranked_by_volume_desc():
    ranked = _StubPrice().list_perpetual_symbols_by_volume()
    # ordinati per volume: BBB(9M) > CCC(5M) > AAA(1M); ZZZ ignorato (non perp)
    assert ranked == ["BBBUSDT", "CCCUSDT", "AAAUSDT"]


def test_eval_universe_decoupled_from_max_positions():
    # la selezione per la VALUTAZIONE segnali usa SELECT_UNIVERSE, non
    # MAX_OPEN_POSITIONS: si valutano molte crypto, se ne aprono al massimo 5.
    results = [
        ScanResult(symbol=f"C{i}USDT", score=1.0 - i / 100,
                   components={}, snapshot=AssetSnapshot(symbol=f"C{i}USDT", price=1.0))
        for i in range(60)
    ]
    sel = MarketScanner(price_agent=_StubPrice()).select_assets(results, Regime.SIDEWAYS)
    assert len(sel) == settings.SELECT_UNIVERSE
    assert settings.SELECT_UNIVERSE > settings.MAX_OPEN_POSITIONS  # disaccoppiati
