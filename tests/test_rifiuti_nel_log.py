"""I RIFIUTI D'INGRESSO NEL LOG (25 set 2026, backlog H5).

Cosa si protegge. Il check end-to-end del learning ha trovato che i rifiuti del
bot prima di aprire (cooldown per coin, tetto per coin al giorno, margine, peso
sotto soglia, veto di regime, stop troppo largo, rischio direzionale) finivano
SOLO in RTDB /decision_status, che ogni ciclo sovrascrive: da fuori non si
potevano contare, e H5 («i segnali non aperti rendono piu' di quelli aperti?»)
vive proprio di quel conteggio. E il freno globale da deriva (size x0,5 su OGNI
trade) non compariva in nessun log ne' comando.

Quattro cose, ognuna col suo test:
  * l'orchestratore stampa «[rifiuto] coin strategia: peso ...» / «veto di
    regime», una riga per coppia e per ciclo, al massimo 20 poi «... e altri N»;
  * in bot/main.py ogni `_publish_decision_status` flat del percorso di apertura
    ha accanto la sua riga «[rifiuto]» (verificato sul sorgente, un TradingBot
    finto e' troppo pesante);
  * trade_stats scrive «FRENO attivo» solo se il freno di serie e' acceso,
    altrimenti «(freno spento)»;
  * state_snapshot, col globale in `drift`, scrive la riga «freno globale
    attivo» coi numeri di settings.
"""
import inspect

from bot.config import settings
from bot.core.models import AssetSnapshot, IndicatorSnapshot, Regime
from bot.orchestrator.orchestrator import Orchestrator


# ---- attrezzi ----------------------------------------------------------------
def _asset(sym: str = "BTCUSDT") -> AssetSnapshot:
    """Condizioni che fanno scattare mean_reversion LONG (stesse di
    tests/test_runtime_adapt.py): prezzo sotto BB inferiore, RSI 20 -> conf 65."""
    ind = IndicatorSnapshot(timeframe="15m", rsi=20.0, atr=2.0, close=94.0,
                            bb_lower=95.0, bb_upper=105.0, bb_mid=100.0)
    return AssetSnapshot(symbol=sym, price=94.0, regime=Regime.SIDEWAYS,
                         indicators={"15m": ind})


def _orch(symbols: list[str], peso: float | None = None) -> Orchestrator:
    """Orchestratore con adattamento finto: coppie validate, peso a scelta."""
    o = Orchestrator()
    o.adaptation._passed = {f"{s}|mean_reversion" for s in symbols}
    o.adaptation._has_opt_data = True
    if peso is not None:
        o.adaptation._weights = {f"mean_reversion|{r.value}": peso for r in Regime}
    return o


def _righe_rifiuto(out: str) -> list[str]:
    return [r for r in out.splitlines() if r.startswith("[rifiuto]")]


# ---- orchestratore: peso sotto soglia ------------------------------------------
# Dal 26 set 2026 (pavimento della panchina, passo 4) un peso sotto soglia NON
# rifiuta piu': la decisione passa a size ridotta con una riga «[panchina]»
# (tests/test_freno_pool.py). Il rifiuto di prima resta con PANCHINA_PAVIMENTO a
# 0: e' quello che questi test verificano, perche' la riga e la classe restano.
def test_peso_sotto_soglia_lascia_una_riga_rifiuto(monkeypatch, capsys):
    """conf 65 x peso 0,3 = 19,5 < 30: niente decisione, ma UNA riga nel log
    (col pavimento della panchina spento)."""
    monkeypatch.setattr(settings, "BACKTEST_PARITY", False)
    monkeypatch.setattr(settings, "PANCHINA_PAVIMENTO", 0.0)
    o = _orch(["BTCUSDT"], peso=0.3)
    decisioni = o.decide_all({"BTCUSDT": _asset()}, Regime.SIDEWAYS)
    assert decisioni == []
    righe = _righe_rifiuto(capsys.readouterr().out)
    assert len(righe) == 1
    assert righe[0].startswith("[rifiuto] BTCUSDT mean_reversion: peso 0.30")
    assert "soglia" in righe[0]


def test_con_peso_pieno_nessun_rifiuto_e_la_decisione_esce(monkeypatch, capsys):
    """Controprova: stesso segnale, peso 1 -> apre, e il log resta pulito."""
    monkeypatch.setattr(settings, "BACKTEST_PARITY", False)
    o = _orch(["BTCUSDT"], peso=1.0)
    decisioni = o.decide_all({"BTCUSDT": _asset()}, Regime.SIDEWAYS)
    assert [d.asset for d in decisioni] == ["BTCUSDT"]
    assert _righe_rifiuto(capsys.readouterr().out) == []


def test_peso_zero_dice_che_la_strategia_e_spenta(monkeypatch, capsys):
    monkeypatch.setattr(settings, "BACKTEST_PARITY", False)
    o = _orch(["BTCUSDT"], peso=0.0)
    assert o.decide_all({"BTCUSDT": _asset()}, Regime.SIDEWAYS) == []
    righe = _righe_rifiuto(capsys.readouterr().out)
    assert len(righe) == 1 and "peso 0.00" in righe[0] and "spenta" in righe[0]


# ---- orchestratore: veto di regime ----------------------------------------------
def test_veto_di_regime_lascia_una_riga_rifiuto(monkeypatch, capsys):
    """Il gate ha visto la coppia perdere in sideways (PF 0,5 su 20 trade): il
    segnale c'e' ma viene scartato -> riga «veto di regime»."""
    monkeypatch.setattr(settings, "BACKTEST_PARITY", False)
    monkeypatch.setattr(settings, "REGIME_FILTER_ENABLED", True)
    o = _orch(["BTCUSDT"], peso=1.0)
    o.adaptation._regime_pf = {"BTCUSDT|mean_reversion": {
        "sideways": {"pf": 0.5, "trades": settings.GATE_REGIME_MIN_TRADES + 10}}}
    assert o.decide_all({"BTCUSDT": _asset()}, Regime.SIDEWAYS) == []
    righe = _righe_rifiuto(capsys.readouterr().out)
    assert righe == ["[rifiuto] BTCUSDT mean_reversion: veto di regime (sideways)"]


def test_veto_di_regime_senza_segnale_non_e_un_rifiuto(monkeypatch, capsys):
    """Coppia vetata ma senza segnale (RSI neutro): nessuna riga, altrimenti il
    conteggio di H5 si gonfia di scarti che non erano trade."""
    monkeypatch.setattr(settings, "BACKTEST_PARITY", False)
    monkeypatch.setattr(settings, "REGIME_FILTER_ENABLED", True)
    o = _orch(["BTCUSDT"], peso=1.0)
    o.adaptation._regime_pf = {"BTCUSDT|mean_reversion": {
        "sideways": {"pf": 0.5, "trades": settings.GATE_REGIME_MIN_TRADES + 10}}}
    a = _asset()
    a.indicators["15m"].rsi = 50.0          # niente estremo -> niente segnale
    assert o.decide_all({"BTCUSDT": a}, Regime.SIDEWAYS) == []
    assert _righe_rifiuto(capsys.readouterr().out) == []


# ---- orchestratore: il tetto al rumore -------------------------------------------
def test_piu_di_venti_rifiuti_stampano_venti_righe_e_il_conto(monkeypatch, capsys):
    monkeypatch.setattr(settings, "BACKTEST_PARITY", False)
    monkeypatch.setattr(settings, "PANCHINA_PAVIMENTO", 0.0)     # rifiuto di prima
    syms = [f"C{i:02d}USDT" for i in range(25)]
    o = _orch(syms, peso=0.3)
    assert o.decide_all({s: _asset(s) for s in syms}, Regime.SIDEWAYS) == []
    righe = _righe_rifiuto(capsys.readouterr().out)
    assert len(righe) == 21
    assert righe[-1] == "[rifiuto] ... e altri 5"
    # una riga per coppia, nessun doppione
    assert len({r.split(":")[0] for r in righe[:20]}) == 20


def test_i_rifiuti_non_si_accumulano_fra_un_ciclo_e_l_altro(monkeypatch, capsys):
    """Due cicli di seguito: il secondo stampa i SUOI rifiuti, non anche quelli
    del primo (altrimenti il log crescerebbe a ogni candela)."""
    monkeypatch.setattr(settings, "BACKTEST_PARITY", False)
    monkeypatch.setattr(settings, "PANCHINA_PAVIMENTO", 0.0)     # rifiuto di prima
    o = _orch(["BTCUSDT"], peso=0.3)
    o.decide_all({"BTCUSDT": _asset()}, Regime.SIDEWAYS)
    o.decide_all({"BTCUSDT": _asset()}, Regime.SIDEWAYS)
    assert len(_righe_rifiuto(capsys.readouterr().out)) == 2


# ---- bot/main.py: ogni flat del percorso di apertura ha la sua riga ----------------
def test_ogni_flat_di_try_open_ha_accanto_una_riga_rifiuto():
    """Verifica sul sorgente di `_try_open` (un TradingBot finto e' troppo
    pesante). Il conteggio NON e' 1:1 ma flat + 1, e il +1 e' voluto: lo
    short-circuit «margine esaurito» sotto parita' non pubblica /decision_status
    (lo fa il giro a fine ciclo) ma nel log deve contare come gli altri, perche'
    e' esattamente uno dei motivi che H5 chiede di contare.

    I blocchi GLOBALI di trading_cycle (pausa, Firebase muto, riconciliazione,
    stream appena ripreso, STOP AND PROTECT) restano fuori: non scartano UN
    segnale, fermano tutto il ciclo ogni 30 secondi, e una riga «[rifiuto]» a
    ogni giro renderebbe il log illeggibile senza aggiungere un conteggio utile."""
    from bot import main as bot_main
    src = inspect.getsource(bot_main.TradingBot._try_open)
    n_flat = src.count('"outcome": "flat"')
    n_rifiuto = src.count("_rifiuto(") - 1          # meno la `def _rifiuto(`
    assert n_flat >= 10                             # il percorso ha davvero i controlli
    assert n_rifiuto == n_flat + 1
    assert 'print(f"[rifiuto] {decision.asset} {decision.strategy} "' in src
    # i motivi che H5 vuole contare compaiono con quelle parole
    for parola in ("cooldown", "tetto per coin", "margine esaurito", "risk gate",
                   "margine insufficiente"):
        assert parola in src, parola


# ---- trade_stats: l'etichetta del freno di serie dice il vero --------------------
def _quattro_perdite():
    return [{"strategy": "gen_x", "symbol": "AUSDT", "direction": "long",
             "pnl": -5.0, "exit_reason": "stop_loss", "exit_ts": 100.0 + i,
             "entry_ts": 90.0 + i} for i in range(4)]


class _FakeFB:
    def __init__(self, status=None):
        self._status = status

    def query_collection(self, *a, **k):
        return _quattro_perdite()

    def get_rtdb(self, path):
        return self._status


def _trade_stats_out(monkeypatch, capsys, acceso: bool, status=None) -> str:
    from scripts import trade_stats
    monkeypatch.setattr(settings, "STREAK_BRAKE_ENABLED", acceso)
    monkeypatch.setattr(settings, "STREAK_BRAKE_LOSSES", 4)
    monkeypatch.setattr(trade_stats, "get_firebase", lambda: _FakeFB(status))
    assert trade_stats.main() == 0
    return capsys.readouterr().out


def test_trade_stats_freno_spento_lo_dice(monkeypatch, capsys):
    out = _trade_stats_out(monkeypatch, capsys, acceso=False)
    assert "SERIE DI PERDITE" in out
    assert "gen_x" in out and "4 perdite di fila" in out
    assert "freno spento" in out
    assert "FRENO attivo" not in out


def test_trade_stats_freno_acceso_lo_dice(monkeypatch, capsys):
    out = _trade_stats_out(monkeypatch, capsys, acceso=True)
    assert "<- FRENO attivo" in out
    assert "freno spento" not in out


def test_trade_stats_rifiuti_rimandano_al_log_senza_inventare_contatori(monkeypatch, capsys):
    stato = {"ts": 1_790_000_000.0, "outcome": "flat",
             "reason": "cooldown su AUSDT dopo stop (37m)"}
    out = _trade_stats_out(monkeypatch, capsys, acceso=False, status=stato)
    assert "RIFIUTI D'INGRESSO" in out
    assert "solo l'ultimo" in out and "cooldown su AUSDT dopo stop (37m)" in out
    assert "righe [rifiuto]" in out
    # senza /decision_status non si inventa niente
    out2 = _trade_stats_out(monkeypatch, capsys, acceso=False, status=None)
    assert "nessun /decision_status leggibile" in out2
    assert "righe [rifiuto]" in out2


# ---- state_snapshot: il freno globale si vede -----------------------------------
class _FakeDriftFB:
    def __init__(self, doc):
        self._doc = doc

    def get_doc(self, collection, doc_id):
        assert (collection, doc_id) == ("drift", "current")
        return self._doc


def _drift_doc(verdetto: str) -> dict:
    return {
        "global": {"verdict": verdetto, "trades": 42, "live_pf": 0.6,
                   "expected_pf": 1.8, "reason": "PF 0.60 vs 1.80 atteso"},
        "pairs": {"AUSDT|gen_x": {"verdict": "ok", "trades": 3, "live_pf": 1.1,
                                  "expected_pf": 1.5, "reason": ""}},
        "strategies": {}, "serie": {},
    }


def test_state_snapshot_globale_in_drift_mostra_il_freno(monkeypatch):
    from scripts.state_snapshot import _drift_section
    monkeypatch.setattr(settings, "DRIFT_ENABLED", True)
    monkeypatch.setattr(settings, "DRIFT_WEIGHT_FACTOR", 0.5)
    monkeypatch.setattr(settings, "DRIFT_PF_RATIO", 0.6)
    testo = "\n".join(_drift_section(_FakeDriftFB(_drift_doc("drift"))))
    assert "**freno globale attivo**" in testo
    assert "size x0.5" in testo and "leva x0.71" in testo
    assert "sotto 0.6 x atteso" in testo
    assert "PF 0.60 vs 1.80 atteso" in testo


def test_state_snapshot_globale_ok_non_parla_di_freno(monkeypatch):
    from scripts.state_snapshot import _drift_section
    monkeypatch.setattr(settings, "DRIFT_ENABLED", True)
    testo = "\n".join(_drift_section(_FakeDriftFB(_drift_doc("ok"))))
    assert "freno globale" not in testo


def test_state_snapshot_drift_spento_lo_dice(monkeypatch):
    from scripts.state_snapshot import _drift_section
    monkeypatch.setattr(settings, "DRIFT_ENABLED", False)
    testo = "\n".join(_drift_section(_FakeDriftFB(_drift_doc("drift"))))
    assert "freno globale SPENTO" in testo
    assert "freno globale attivo" not in testo
