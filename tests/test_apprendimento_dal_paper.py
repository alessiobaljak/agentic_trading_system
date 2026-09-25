"""L'ANELLO CHE MANCAVA: il paper misura, il gate decide.

Richiesta del proprietario, 19 settembre: «l'AI deve apprendere da ogni trade, non
voglio che dica dati insufficienti... il compito dell'AI nel paper e' migliorare le
performance delle strategie, altrimenti a che serve».

Aveva ragione su un punto che non avevo visto: il sistema misurava tutto e non lo
diceva a chi deve inventare le soluzioni. L'AI riceveva UNA riga di contesto
(«Timeframe 15m. Universo: crypto futures USDT-M») e proponeva alla cieca; e la
misura piu' informativa del paper — `mfe_r`, dove arriva davvero il prezzo —
finiva nel rapporto di deriva e li' moriva.

Ha scelto (AskUserQuestion, 19 settembre) che tutto passi dal GATE: il paper
propone, il gate valida con le sue tre conferme, e niente cambia dal vivo prima.
Cosi' il verdetto dei 40 trade resta valido, perche' nessuno sposta il bersaglio
mentre si misura.

DUE COSE VANNO PROTETTE QUI, e sono la ragione del file:
  1. la scala dal paper e' un CANDIDATO, mai una sostituzione — altrimenti dodici
     trade scavalcherebbero la validazione;
  2. senza dati, tutto deve comportarsi ESATTAMENTE come prima.
"""
import pytest

from bot.execution.exit_logic import SCALE_LADDER_CANDIDATES, ladder_from_mfe
from scripts.discover_strategies import (candidate_ladders, prove_dal_paper,
                                         scala_dal_paper)


# --------------------------------------------------------------------------- #
# 1. La scala ricavata da dove il prezzo arriva davvero                        #
# --------------------------------------------------------------------------- #
def test_con_pochi_trade_non_si_ricava_niente():
    """La soglia non e' timidezza: sotto una decina di numeri un quantile e' rumore
    travestito da misura, e una scala sbagliata resterebbe addosso alle coppie per
    settimane."""
    assert ladder_from_mfe([0.5, 0.8, 1.2]) is None
    assert ladder_from_mfe([]) is None
    assert ladder_from_mfe(None) is None


def test_la_scala_segue_la_distribuzione_misurata():
    """Il caso vero del 19 settembre: mfe mediana 0,74R contro un primo gradino a
    1,5-2,0R. La scala derivata deve avere il primo gradino ALLA PORTATA del
    mercato, non oltre."""
    mfes = [0.2, 0.3, 0.45, 0.5, 0.6, 0.74, 0.9, 1.1, 1.5, 1.9, 2.4, 3.1]
    scala = ladder_from_mfe(mfes)
    assert scala is not None
    assert scala[0] <= 1.0, f"primo gradino fuori portata: {scala}"
    assert scala[0] < scala[1] < scala[2], "i gradini devono crescere"


def test_i_gradini_non_possono_mai_coincidere():
    """Con una distribuzione piatta i tre quantili tornano lo stesso numero. Una
    scala con due gradini uguali farebbe incassare due fette allo stesso prezzo:
    va separata, non accettata."""
    scala = ladder_from_mfe([0.8] * 20)
    assert scala is not None
    assert scala[0] < scala[1] < scala[2]


def test_una_distribuzione_impossibile_non_produce_una_scala():
    """Se anche la mediana e' irraggiungibile, meglio nessuna proposta che una
    proposta assurda: restano le quattro fisse."""
    assert ladder_from_mfe([50.0] * 20) is None


def test_i_valori_negativi_o_nulli_non_entrano_nel_conto():
    """`mfe_r` puo' essere 0 su un trade stoppato subito: contarlo abbasserebbe la
    mediana a un valore che non descrive nessun movimento."""
    scala = ladder_from_mfe([0.0] * 10 + [1.0, 1.2, 1.4, 1.6, 1.8, 2.0,
                                          2.2, 2.4, 2.6, 2.8])
    assert scala is not None and scala[0] >= 1.0


# --------------------------------------------------------------------------- #
# 2. Il paper PROPONE, il gate DISPONE                                         #
# --------------------------------------------------------------------------- #
def test_la_scala_del_paper_si_aggiunge_e_non_sostituisce():
    """IL PUNTO PIU' IMPORTANTE DEL FILE. Se sostituisse, una misura su dodici
    trade deciderebbe gli obiettivi di tutte le coppie senza passare da nessuna
    validazione — esattamente cio' che il proprietario ha scelto di NON fare."""
    fuori = candidate_ladders((0.75, 1.5, 2.5))
    assert len(fuori) == len(SCALE_LADDER_CANDIDATES) + 1
    for fissa in SCALE_LADDER_CANDIDATES:
        assert tuple(fissa) in {tuple(c) for c in fuori}
    assert (0.75, 1.5, 2.5) in {tuple(c) for c in fuori}


def test_senza_scala_dal_paper_i_candidati_sono_quelli_di_sempre():
    assert candidate_ladders(None) == SCALE_LADDER_CANDIDATES
    assert candidate_ladders(()) == SCALE_LADDER_CANDIDATES


def test_una_scala_gia_presente_non_viene_duplicata():
    """Valutare due volte la stessa scala costa tempo di calcolo a ogni giro e non
    aggiunge un'informazione."""
    gia = tuple(SCALE_LADDER_CANDIDATES[0])
    assert candidate_ladders(gia) == SCALE_LADDER_CANDIDATES


# --------------------------------------------------------------------------- #
# 3. Le prove del paper arrivano a chi propone                                 #
# --------------------------------------------------------------------------- #
class _Fb:
    def __init__(self, docs=None, trades=None):
        self.docs = docs or {}
        self.trades = trades or []

    def get_doc(self, coll, doc):
        return self.docs.get((coll, doc), {})

    def query_collection(self, *a, **k):
        return self.trades


def test_il_digest_contiene_i_fatti_che_servono():
    fb = _Fb(
        docs={("drift", "current"): {"global": {"trades": 12, "live_pf": 0.22,
                                                "expected_pf": 1.88,
                                                "mfe_median": 0.74,
                                                "first_rung_r": 1.5}},
              ("gate_autopsy", "current"): {"evaluated": 96727, "passed": 241,
                                            "binding": {"total_return": 65969,
                                                        "regime": 15233}}},
        trades=[{"direction": "short", "pnl": -3.0}, {"direction": "short", "pnl": -2.0},
                {"direction": "long", "pnl": 4.0}])
    testo = prove_dal_paper(fb)
    assert "0.74" in testo and "1.5" in testo      # la raggiungibilita' dei TP
    assert "short" in testo and "long" in testo    # l'asimmetria di direzione
    assert "total_return" in testo                 # dove muoiono le candidate
    assert "12 trade" in testo                     # il campione, sempre accanto


def test_il_digest_dichiara_che_i_campioni_sono_piccoli():
    """Un numero senza il suo campione e' peggio di nessun numero: chi legge non
    saprebbe quanto pesarlo, e tratterebbe dodici trade come una legge."""
    fb = _Fb(docs={("drift", "current"): {"global": {"trades": 12, "live_pf": 0.22,
                                                     "expected_pf": 1.88}}})
    assert "indizi, non leggi" in prove_dal_paper(fb)


def test_senza_dati_il_digest_e_vuoto():
    """Fail-open: il comportamento torna identico a prima, e all'AI non si manda
    una sezione «prove» senza prove dentro."""
    assert prove_dal_paper(_Fb()) == ""


def test_un_guasto_di_firebase_non_ferma_la_discovery():
    """Una diagnosi non disponibile non puo' far cadere un giro di validazione:
    sarebbe un modo nuovo di perdere le conferme di quel giro."""
    class _Rotto:
        def get_doc(self, *a, **k):
            raise RuntimeError("firestore giu'")

        def query_collection(self, *a, **k):
            raise RuntimeError("firestore giu'")

    assert prove_dal_paper(_Rotto()) == ""
    assert scala_dal_paper(_Rotto()) is None


def test_la_discovery_passa_davvero_le_prove_all_ai():
    """Se il digest esistesse ma nessuno lo mettesse nel contesto, i test sopra
    sarebbero verdi e l'AI continuerebbe a proporre bendata."""
    import inspect

    from scripts import discover_strategies as d

    src = inspect.getsource(d.main)
    assert "prove_dal_paper(fb)" in src
    assert "market_context" in src and "prove" in src


def test_la_scala_del_paper_arriva_ai_worker():
    """Calcolarla e non passarla ai processi che valutano sarebbe lavoro sprecato
    e silenzioso: il gate continuerebbe con le quattro fisse."""
    import inspect

    from scripts import discover_strategies as d

    assert "scala_paper" in inspect.getsource(d._disc_init)
    # dal 25 set 2026 i trade del paper si leggono UNA volta nel main
    # (`trades_del_paper`) e si passano alla proposta della scala
    assert "scala_paper = scala_dal_paper(fb, trades=trades_paper)" in inspect.getsource(d.main)
    # il worker la passa a `evaluate_spec`, che la riceve come ARGOMENTO invece di
    # leggerla da uno stato globale: la prima versione la infilava in `_disc_one` e
    # la scelta della scala non e' li' — questo test l'ha trovato
    # dal 25 set 2026 ai candidati si aggiunge anche la scala della SOLA
    # strategia in esame (`scale_per_strategia`): la globale resta il primo argomento
    assert 'candidate_ladders(_W.get("scala_paper"),' in inspect.getsource(d._disc_one)
    assert "scale_candidates" in inspect.getsource(d.evaluate_spec)


def test_evaluate_spec_senza_candidate_usa_quelle_fisse():
    """Chi chiama `evaluate_spec` da fuori (un test, uno script di analisi) non deve
    dover conoscere lo stato dei worker per ottenere il comportamento normale."""
    import inspect

    from scripts import discover_strategies as d

    src = inspect.getsource(d.evaluate_spec)
    assert "scale_candidates or SCALE_LADDER_CANDIDATES" in src
