"""DUE DOMANDE DEL PROPRIETARIO, 18 SETTEMBRE, E I FATTI CHE LE RISPONDONO.

  1. «l'ho visto in positivo per quasi 10 ore e alla fine siamo andati in stop
     loss, com'e' possibile?»
  2. «in una giornata di rialzo abbiamo aperto 4 posizioni su 5 short — mi ricordo
     che vedere il trend era una prerogativa».

Nessuna delle due era un bug, ed e' proprio per questo che meritano un test: sono
due comportamenti VOLUTI, sorprendenti, e finora scritti in nessun posto che si
rompa se qualcuno li cambia per sbaglio.

IL PUNTO DEL PRIMO (com'era fino al 21 settembre). Il profit-lock si armava al
`PROFIT_LOCK_TRIGGER` della distanza entry->TP, e sotto scale-out quel «TP» era
l'ULTIMO gradino della scala, non il primo. Con la scala 2/4/6 di VETUSDT il TP finale sta a 6R, quindi la protezione
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
# 1. Il profit-lock e' ancorato al PRIMO gradino (dal 21 set 2026; era l'ultimo) #
# --------------------------------------------------------------------------- #
def _stop_con_scala(mults, best_fav_r: float) -> float:
    """Stop effettivo per un long con entry 100, R=1 e la scala data, dopo aver
    visto `best_fav_r` R a favore. Replica cio' che fanno executor e motore:
    l'ancora e' `lock_anchor(ladder)`, cioe' il PRIMO gradino."""
    from bot.config import settings
    from bot.execution.exit_logic import lock_anchor
    entry, base_stop = 100.0, 99.0          # R = 1
    ladder = [(entry + m * 1.0, f) for m, f in zip(mults, (0.3, 0.3, 0.4))]
    prima = (settings.PROFIT_LOCK_ENABLED, settings.PROFIT_LOCK_TRIGGER,
             settings.PROFIT_LOCK_KEEP)
    settings.PROFIT_LOCK_ENABLED, settings.PROFIT_LOCK_TRIGGER = True, 0.5
    settings.PROFIT_LOCK_KEEP = 0.5
    try:
        return locked_stop(entry, lock_anchor(ladder), True, entry + best_fav_r, base_stop)
    finally:
        (settings.PROFIT_LOCK_ENABLED, settings.PROFIT_LOCK_TRIGGER,
         settings.PROFIT_LOCK_KEEP) = prima


def test_con_la_scala_lunga_la_protezione_si_arma_a_1R():
    """IL CASO DEL 18 SETTEMBRE, corretto: con la scala 2/4/6 il lock si arma a
    meta' strada dal PRIMO gradino (1R), non dall'ultimo (3R). Un trade a +1,9R
    per tre ore ora esce vicino al pareggio, non allo stop pieno. Misurato: 13
    stop su 21 erano trade andati a favore (mfe mediana 0,69R) senza toccare il
    primo gradino."""
    assert _stop_con_scala((2.0, 4.0, 6.0), 1.9) == pytest.approx(100.95)
    assert _stop_con_scala((2.0, 4.0, 6.0), 0.9) == 99.0, "sotto 1R non ancora armato"


def test_con_la_scala_corta_si_arma_prima():
    """1,5/3/5: primo gradino a 1,5R, lock a 0,75R."""
    assert _stop_con_scala((1.5, 3.0, 5.0), 0.8) > 99.0
    assert _stop_con_scala((1.5, 3.0, 5.0), 0.7) == 99.0


def test_il_lock_puo_solo_migliorare():
    assert _stop_con_scala((2.0, 4.0, 6.0), 3.5) == pytest.approx(101.75)


def test_gate_e_paper_usano_lo_STESSO_ancoraggio():
    """LA COSA CHE CONTA DAVVERO: i due lati devono coincidere, altrimenti il PF
    promesso descrive un sistema diverso da quello che opera (BIRBUSDT: 1,51
    promesso, 0,16 vissuto). L'ancora e' UNA funzione, usata da entrambi."""
    import inspect

    from backtesting import engine
    from bot.execution import executor

    for mod in (engine, executor):
        src = inspect.getsource(mod)
        assert "lock_anchor(ladder)" in src, f"{mod.__name__} non usa lock_anchor"
        assert "locked_stop(entry, final_target" not in src
        assert "locked_stop(pos.entry_price, final_target" not in src


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
