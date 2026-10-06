"""Test del modulo `fatti` e del documento `config/regole_dimensione.md`.

Due famiglie di controlli:
  * sulle funzioni pure (estrazione dei riferimenti, intestazioni, segreti), con
    testi costruiti a mano;
  * sul documento VERO: ogni `file:riga` punta a una riga esistente, e le righe
    chiave contengono il frammento che il documento attribuisce loro. Se il bot
    cambia una di quelle righe, il test cade e il documento va riletto: e' il
    modo in cui un fatto resta verificabile dopo il giorno in cui e' stato scritto.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from research.src import fatti

RADICE = Path(__file__).resolve().parents[3]
DOCUMENTO = RADICE / "research" / "config" / "regole_dimensione.md"

#: le intestazioni che il Passo 0 chiede (un punto per fatto, piu' le incoerenze)
SEZIONI_ATTESE = [
    "1. `serie_stop`: quale prezzo fa scattare lo stop",
    "2. `regole_dimensione_bot`: rischio, leva, margine, limiti",
    "3. Costi nel bot e nel gate",
    "4. `esecuzione_strategie_bot`: in che forma il bot esegue una strategia",
    "5. `backtest_interno`: il motore di backtest del bot",
    "6. Dati: candele storiche e funding",
    "7. Timeframe del bot e orizzonte massimo di una posizione",
    "Incoerenze con i valori di partenza del protocollo",
]

#: riga citata -> frammento che DEVE contenere. Sono le affermazioni portanti del
#: documento: numeri di default, tipi di ordine, serie dei prezzi, orizzonte.
ANCORE = {
    # serie dello stop
    "bot/main.py:1353": "get_mark_price",
    "bot/agents/price_agent.py:132": "markPrice",
    "bot/agents/price_stream.py:258": "/ 2.0",
    "bot/execution/executor.py:605": "lo <= eff_stop",
    "bot/execution/executor.py:664": "lo <= eff_stop",
    "bot/execution/executor.py:364": 'type="LIMIT"',
    "bot/execution/executor.py:462": 'type="STOP_MARKET"',
    "bot/execution/executor.py:480": "TAKE_PROFIT_MARKET",
    "bot/execution/executor.py:799": 'type="MARKET"',
    "backtesting/engine.py:942": "c.low <= eff_stop",
    "backtesting/engine.py:953": "c.high >= eff_stop",
    # dimensione, leva, limiti
    "bot/core/models.py:193": "leverage: float = 2.0",
    "bot/core/models.py:194": "risk_per_trade: float = 0.01",
    "bot/config.py:161": "DEFAULT_LEVERAGE: float = 2.0",
    "bot/config.py:162": "DEFAULT_RISK_PER_TRADE: float = 0.01",
    "bot/risk/hard_limits.py:17": "MAX_LEVERAGE: float = 5.0",
    "bot/risk/hard_limits.py:18": "MAX_RISK_PER_TRADE: float = 0.03",
    "bot/risk/risk_manager.py:83": "eff_lev = min(alloc_lev, sys_lev_cap, hard_limits.MAX_LEVERAGE)",
    "bot/risk/risk_manager.py:147": "frac = 0.10",
    "bot/config.py:176": "MAX_OPEN_POSITIONS",
    "bot/config.py:181": "MAX_POSITION_EQUITY_FRACTION",
    "bot/config.py:237": "MAX_DIRECTIONAL_RISK_PCT",
    "bot/config.py:686": "RISK_PER_COIN_DAY",
    "bot/config.py:693": "MAX_STOP_PCT",
    "bot/config.py:603": "MIN_COINS_PER_STRATEGY",
    "bot/main.py:1639": "MAX_OPEN_POSITIONS",
    # costi
    "bot/execution/executor.py:178": "BACKTEST_COST_PER_TRADE",
    "bot/execution/executor.py:179": "BACKTEST_FUNDING_PER_8H",
    "backtesting/engine.py:616": "BACKTEST_COST_PER_TRADE",
    "bot/core/costs.py:39": "held_hours / 8.0",
    "backtesting/data_loader.py:29": "fapi/v1/fundingRate",
    "bot/agents/price_agent.py:195": "lastFundingRate",
    # esecuzione delle strategie
    "bot/strategies/base.py:36": "class Strategy(ABC)",
    "bot/strategies/base.py:124": "def register_strategy",
    "bot/strategies/generated.py:555": "class GeneratedStrategy(Strategy)",
    "bot/learning/adaptation.py:510": "in self._passed",
    "bot/learning/adaptation.py:401": "def load_generated",
    "bot/orchestrator/orchestrator.py:304": "get_all_strategies(params_by_strat)",
    "backtesting/optimizer.py:229": "STRATEGY_REGISTRY.items()",
    "bot/config.py:281": '("1m", "5m", "15m", "1h")',
    "bot/config.py:195": "REQUIRE_VALIDATED_PAIRS",
    # backtest interno
    "backtesting/engine.py:43": "HORIZON_BARS = 96",
    "backtesting/engine.py:798": "def run_strategy",
    "backtesting/engine.py:833": "entry = snap.price",
    "backtesting/engine.py:982": "pnl=pnl_pct * self.capital",
    "backtesting/engine.py:485": "MAINTENANCE_BUFFER = 0.005",
    "backtesting/optimizer.py:106": "capital: float = 10_000.0",
    # dati
    "backtesting/data_loader.py:28": "fapi/v1/klines",
    "backtesting/data_loader.py:385": 'start: str = "2022-01-01"',
    "bot/agents/price_agent.py:29": "fapi.binance.com",
    "bot/agents/price_stream.py:47": "fstream.binance.com",
    "backtesting/metrics_loader.py:45": "data.binance.vision",
    # timeframe e orizzonte
    "bot/config.py:169": "ORCHESTRATOR_TIMEFRAME",
    "bot/execution/executor.py:185": "EXEC_MAX_HOLD_HOURS",
    "bot/main.py:2397": "sleep_s: float = 30.0",
}


# --------------------------------------------------------------------------- #
# Funzioni pure                                                                #
# --------------------------------------------------------------------------- #
def test_estrai_riferimenti_singoli_e_intervalli():
    testo = "vedi bot/config.py:12 e backtesting/engine.py:40-45, poi scripts/x.sh:3."
    rifs = fatti.estrai_riferimenti(testo)
    assert [r.testo for r in rifs] == [
        "bot/config.py:12", "backtesting/engine.py:40-45", "scripts/x.sh:3"]
    assert rifs[1].riga_da == 40 and rifs[1].riga_a == 45


def test_estrai_riferimenti_raddrizza_intervallo_rovesciato():
    (r,) = fatti.estrai_riferimenti("bot/main.py:50-40")
    assert (r.riga_da, r.riga_a) == (40, 50)


def test_estrai_riferimenti_ignora_testo_senza_percorso():
    assert fatti.estrai_riferimenti("alle 15:30 del 6 ottobre, versione 4.3") == []


def test_verifica_riferimenti_segnala_file_mancante_e_riga_oltre(tmp_path):
    (tmp_path / "bot").mkdir()
    (tmp_path / "bot" / "a.py").write_text("uno\ndue\ntre\n", encoding="utf-8")
    rifs = fatti.estrai_riferimenti("bot/a.py:2 bot/a.py:3-9 bot/b.py:1")
    problemi = fatti.verifica_riferimenti(rifs, tmp_path)
    assert problemi == ["bot/a.py:3-9: il file ha solo 3 righe", "bot/b.py:1: file mancante"]


def test_riga_e_ancore(tmp_path):
    (tmp_path / "bot").mkdir()
    (tmp_path / "bot" / "a.py").write_text("x = 1\nMAX = 5.0\n", encoding="utf-8")
    assert fatti.riga(tmp_path / "bot" / "a.py", 2) == "MAX = 5.0"
    assert fatti.riga(tmp_path / "bot" / "a.py", 9) == ""
    assert fatti.verifica_ancore({"bot/a.py:2": "MAX = 5.0"}, tmp_path) == []
    (problema,) = fatti.verifica_ancore({"bot/a.py:1": "MAX"}, tmp_path)
    assert problema.startswith("bot/a.py:1: atteso")
    (problema,) = fatti.verifica_ancore({"non un riferimento": "x"}, tmp_path)
    assert "non e' un riferimento valido" in problema


def test_sezioni_mancanti():
    testo = "# Titolo\n\n## Uno\ntesto\n### Due\n"
    assert fatti.sezioni_mancanti(testo, ["Uno", "Due", "Tre"]) == ["Tre"]


def test_contiene_segreti_vede_un_valore_ma_non_un_nome():
    assert fatti.contiene_segreti("parametro BINANCE_API_KEY (solo il nome)") == []
    assert fatti.contiene_segreti("BINANCE_API_KEY=\n") == []
    assert fatti.contiene_segreti("TELEGRAM_BOT_TOKEN=abcdefghij1234") != []


# --------------------------------------------------------------------------- #
# Il documento vero                                                            #
# --------------------------------------------------------------------------- #
@pytest.fixture(scope="module")
def documento() -> str:
    assert DOCUMENTO.is_file(), f"manca {DOCUMENTO}"
    return DOCUMENTO.read_text(encoding="utf-8")


def test_documento_ha_tutte_le_sezioni(documento):
    assert fatti.sezioni_mancanti(documento, SEZIONI_ATTESE) == []


def test_documento_cita_molti_riferimenti_e_tutti_esistono(documento):
    rifs = fatti.estrai_riferimenti(documento)
    assert len(rifs) >= 150, "il documento deve citare il codice riga per riga"
    assert fatti.verifica_riferimenti(rifs, RADICE) == []


def test_documento_ancore_dicono_cio_che_il_documento_afferma(documento):
    # ogni ancora deve anche comparire nel documento: altrimenti il test
    # verificherebbe righe che nessuno cita
    citati = {r.testo for r in fatti.estrai_riferimenti(documento)}
    citati_singoli = set()
    for r in fatti.estrai_riferimenti(documento):
        for n in range(r.riga_da, r.riga_a + 1):
            citati_singoli.add(f"{r.file}:{n}")
    non_citate = [a for a in ANCORE if a not in citati and a not in citati_singoli]
    assert non_citate == [], f"ancore non citate nel documento: {non_citate}"
    assert fatti.verifica_ancore(ANCORE, RADICE) == []


def test_documento_senza_valori_di_segreti(documento):
    assert fatti.contiene_segreti(documento) == []


def test_fatti_negativi_restano_veri():
    """Le affermazioni «non trovato» del documento: se un giorno il bot passa un
    `workingType` o imposta la modalita' di margine, il documento va riscritto."""
    executor = (RADICE / "bot" / "execution" / "executor.py").read_text(encoding="utf-8")
    assert "workingType" not in executor
    assert "marginType" not in executor and "futures_change_margin_type" not in executor
    loader = (RADICE / "backtesting" / "data_loader.py").read_text(encoding="utf-8")
    assert "markPriceKlines" not in loader
    costs = (RADICE / "bot" / "core" / "costs.py").read_text(encoding="utf-8")
    assert "fundingIntervalHours" not in costs
