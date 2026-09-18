"""DUE DOMANDE DEL PROPRIETARIO, 18 SETTEMBRE, E I FATTI CHE LE RISPONDONO.

  1. «l'ho visto in positivo per quasi 10 ore e alla fine siamo andati in stop
     loss, com'e' possibile?»
  2. «in una giornata di rialzo abbiamo aperto 4 posizioni su 5 short — mi ricordo
     che vedere il trend era una prerogativa».

Nessuna delle due era un bug, ed e' proprio per questo che meritano un test: sono
due comportamenti VOLUTI, sorprendenti, e finora scritti in nessun posto che si
rompa se qualcuno li cambia per sbaglio.

IL PUNTO DEL PRIMO. Il profit-lock si arma al `PROFIT_LOCK_TRIGGER` della distanza
entry->TP, e sotto scale-out quel «TP» e' l'ULTIMO gradino della scala, non il
primo. Con la scala 2/4/6 di VETUSDT il TP finale sta a 6R, quindi la protezione
si accende a 3R: fino a li' lo stop resta quello originale e TUTTO il guadagno non
realizzato puo' tornare indietro. Misurato sui primi 7 trade chiusi
(`docs/state.md`, 18 set): mfe mediana 0.52R, trade oltre 3R **zero**. Il
profit-lock non si e' mai armato, e con quei numeri non poteva.

IL PUNTO DEL SECONDO. Il trend NON mette il veto: modula la size e basta
(`Orchestrator.decide_all`, `size_mult >= 0.5`). E' una scelta, non una svista —
meta' delle feature generate sono di ritorno alla media e per costruzione vendono
la forza. Quindi «molte short in un rialzo» e' il comportamento atteso, e la
domanda utile diventa se stia pagando: da qui il blocco DIREZIONE in `trade_stats`.
"""
import pytest

from bot.core.models import Regime
from bot.execution.exit_logic import locked_stop
from scripts.trade_stats import direction_report


def _t(direction: str, pnl: float, regime: str = "bull_trending", mfe: float = 0.5):
    return {"direction": direction, "pnl": pnl, "regime_at_entry": regime,
            "mfe_r": mfe}


# --------------------------------------------------------------------------- #
# 1. Il profit-lock e' ancorato all'ULTIMO gradino, non al primo                #
# --------------------------------------------------------------------------- #
def _stop_con_scala(mults, best_fav_r: float) -> float:
    """Stop effettivo per un long con entry 100, R=1 e la scala data, dopo aver
    visto `best_fav_r` R a favore. Replica esattamente cio' che fanno executor e
    motore del gate: `final_target = ladder[-1]`."""
    from bot.config import settings
    entry, base_stop = 100.0, 99.0          # R = 1
    final_target = entry + mults[-1] * 1.0
    prima = (settings.PROFIT_LOCK_ENABLED, settings.PROFIT_LOCK_TRIGGER,
             settings.PROFIT_LOCK_KEEP)
    settings.PROFIT_LOCK_ENABLED, settings.PROFIT_LOCK_TRIGGER = True, 0.5
    settings.PROFIT_LOCK_KEEP = 0.5
    try:
        return locked_stop(entry, final_target, True, entry + best_fav_r, base_stop)
    finally:
        (settings.PROFIT_LOCK_ENABLED, settings.PROFIT_LOCK_TRIGGER,
         settings.PROFIT_LOCK_KEEP) = prima


def test_con_la_scala_lunga_la_protezione_non_si_arma_sotto_3R():
    """LA RISPOSTA ALLA PRIMA DOMANDA, in una riga eseguibile: con la scala 2/4/6
    un trade puo' stare ore a +1.9R e uscire comunque allo stop PIENO, perche' la
    protezione si accende solo a 3R."""
    assert _stop_con_scala((2.0, 4.0, 6.0), 1.9) == 99.0, (
        "lo stop dovrebbe essere ancora quello originale: il lock si arma a 3R")


def test_con_la_scala_corta_lo_stesso_movimento_protegge():
    """Lo stesso identico movimento, con la scala 1/2/3, ARMA la protezione: il TP
    finale e' a 3R quindi il lock scatta a 1.5R. Non e' la volatilita' della coin a
    decidere se il guadagno viene protetto — e' la scala che il gate le ha
    assegnato. Due coppie possono comportarsi in modo opposto sullo stesso grafico."""
    stop = _stop_con_scala((1.0, 2.0, 3.0), 1.9)
    assert stop > 99.0, "a 1.9R con TP finale a 3R il lock deve essere armato"
    assert stop == pytest.approx(100.95)    # entry + KEEP(0.5) * 1.9R


def test_oltre_la_soglia_il_lock_si_arma_anche_sulla_scala_lunga():
    """Per non lasciare il sospetto che sia rotto: a 3.5R si arma e blocca meta'."""
    assert _stop_con_scala((2.0, 4.0, 6.0), 3.5) == pytest.approx(101.75)


def test_gate_e_paper_usano_lo_STESSO_ancoraggio():
    """LA COSA CHE CONTA DAVVERO. Che il lock si armi tardi e' severo ma onesto:
    il gate ha validato VETUSDT a PF 1.63 CON questa regola dentro. Diventerebbe
    disonesto solo se i due divergessero — allora il PF promesso descriverebbe un
    sistema diverso da quello che opera. E' la stessa classe di problema che ha
    prodotto BIRBUSDT (1.51 promesso, 0.16 vissuto)."""
    import inspect

    from backtesting import engine
    from bot.execution import executor

    for mod in (engine, executor):
        src = inspect.getsource(mod)
        assert "final_target = ladder[-1][0]" in src, (
            f"{mod.__name__} non ancora il lock all'ultimo gradino")
        assert "locked_stop(entry" in src or "locked_stop(pos.entry_price" in src


# --------------------------------------------------------------------------- #
# 2. Il report per direzione: quante short, e stanno pagando?                  #
# --------------------------------------------------------------------------- #
def test_conta_long_e_short_col_loro_pnl():
    rep = direction_report([_t("short", -3.24), _t("short", -2.0),
                            _t("long", +4.11)])
    assert rep["per_direzione"]["short"]["trade"] == 2
    assert rep["per_direzione"]["short"]["pnl"] == -5.24
    assert rep["per_direzione"]["long"]["trade"] == 1
    assert rep["per_direzione"]["long"]["vinti"] == 1


def test_il_controtrend_usa_il_criterio_dell_orchestratore():
    """Short in bull e long in bear sono controtrend; il laterale e' neutro. Se
    questa riga divergesse da `Orchestrator._trend_align`, il report direbbe
    «controtrend» di trade che il bot ha considerato in trend quando li ha
    dimensionati — e il PnL della riga non vorrebbe dire piu' niente."""
    rep = direction_report([
        _t("short", -3.0, "bull_trending"),     # contro
        _t("long", +1.0, "bull_trending"),      # in trend
        _t("long", -2.0, "bear_trending"),      # contro
        _t("short", +0.5, "sideways"),          # neutro
    ])
    a = rep["allineamento"]
    assert a["contro"]["trade"] == 2 and a["contro"]["pnl"] == -5.0
    assert a["in_trend"]["trade"] == 1
    assert a["neutro"]["trade"] == 1


def test_un_regime_mancante_non_diventa_laterale():
    """Un trade senza `regime_at_entry` finisce in 'ignoto', non fra i neutri:
    contarlo come laterale gonfierebbe proprio la riga che serve a decidere."""
    rep = direction_report([{"direction": "short", "pnl": -1.0}])
    assert rep["allineamento"]["ignoto"]["trade"] == 1
    assert rep["allineamento"]["neutro"]["trade"] == 0


def test_la_matrice_incrocia_regime_e_direzione():
    """E' la tabella che risponde alla domanda cosi' com'e' stata posta: «in una
    giornata di rialzo, quante short?»."""
    rep = direction_report([_t("short", -1.0), _t("short", -1.0), _t("long", 1.0)])
    assert rep["matrice"]["bull_trending"] == {"short": 2, "long": 1}


def test_i_regimi_usati_qui_esistono_davvero():
    """Se un giorno un valore di `Regime` venisse rinominato, i test sopra
    resterebbero verdi confrontando stringhe morte."""
    for nome in ("bull_trending", "bear_trending", "sideways"):
        assert Regime(nome)
