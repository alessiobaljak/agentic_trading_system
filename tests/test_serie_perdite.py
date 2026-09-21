"""QUANTO LUNGA E' UNA SERIE DI PERDITE NORMALE — il metro, prima del giudizio.

21 settembre 2026. Tre strategie validate, undici trade, tutti persi. La domanda
del proprietario e' stata la piu' precisa di tutta la settimana: «nel gate era mai
successo?».

Finora la divergenza si misurava solo col profit factor, che e' una media: dice
che il vissuto e' peggiore della promessa, non se e' FUORI da cio' che la promessa
prevede. Una spec che vince il 57% delle volte perde comunque otto volte di fila,
prima o poi. Senza il metro, ogni striscia di perdite sembra un guasto — e si
finisce per cambiare il sistema mentre sta misurando.

Qui si proteggono i due conti che danno quel metro, e i due modi in cui possono
mentire: contare le SERIE invece delle FINESTRE, e spezzare una serie al confine
fra due finestre di backtest.
"""
import inspect

from scripts import serie_perdite as sp


def test_una_serie_finale_non_viene_persa():
    """IL CASO DI CONFINE, ed e' proprio quello che stiamo vivendo: la striscia in
    corso arriva fino all'ultimo trade. Un conteggio che chiude solo quando arriva
    una vittoria non la vedrebbe mai — la serie piu' importante sarebbe l'unica
    invisibile."""
    assert sp.serie_perdenti([True, False, False, False]) == [3]


def test_le_serie_si_contano_tutte_e_in_ordine():
    assert sp.serie_perdenti([False, True, False, False, True, False]) == [1, 2, 1]
    assert sp.serie_perdenti([True, True]) == []
    assert sp.serie_perdenti([]) == []


def test_le_FINESTRE_non_sono_le_SERIE():
    """Una serie da 4 contiene DUE finestre da 3, e chi guarda il proprio conto le
    vive entrambe. Contare le serie darebbe 1 e farebbe sembrare l'evento piu' raro
    di quanto sia: e' la frequenza che risponde a «quanto spesso capita», quindi
    dev'essere quella delle finestre."""
    esiti = [True, False, False, False, False, True]
    assert sp.serie_perdenti(esiti) == [4]
    assert sp.quante_volte_almeno(esiti, 3) == 2
    assert sp.quante_volte_almeno(esiti, 4) == 1
    assert sp.quante_volte_almeno(esiti, 5) == 0


def test_una_finestra_piu_lunga_della_storia_vale_zero():
    """Con meno trade della finestra chiesta la risposta onesta e' «non lo so»,
    cioe' zero occorrenze — non un errore e non un numero inventato."""
    assert sp.quante_volte_almeno([False, False], 5) == 0
    assert sp.quante_volte_almeno([], 1) == 0
    assert sp.quante_volte_almeno([False], 0) == 0


def test_tutte_perdite_danno_la_serie_intera():
    assert sp.serie_perdenti([False] * 7) == [7]
    assert sp.quante_volte_almeno([False] * 7, 7) == 1


def test_il_gate_si_rigira_in_UNA_passata_non_a_finestre():
    """Se i trade del gate venissero da finestre OOS separate, una serie di perdite
    a cavallo fra due finestre verrebbe contata come due serie corte, e il metro
    sarebbe sistematicamente ottimista — cioe' sbagliato proprio nella direzione
    che farebbe dire «e' tutto normale»."""
    src = inspect.getsource(sp.trade_del_gate)
    assert "n_windows=1" in src
    assert "run_strategy" in src and "_windows(" not in src
    assert 'key=lambda t: float(getattr(t, "entry_ts", 0) or 0)' in src


def test_mai_dati_sintetici():
    """Una serie di perdite misurata su prezzi inventati ha l'aria di una risposta
    ed e' rumore."""
    assert "allow_synthetic=False" in inspect.getsource(sp.trade_del_gate)


def test_gli_ingressi_si_confrontano_con_una_tolleranza_di_due_barre():
    """Il segnale nasce a barra chiusa e il bot esegue dopo: pretendere lo stesso
    istante direbbe «nessuna corrispondenza» anche quando i due guardano la stessa
    soglia."""
    assert "tol = 2 * tf_h * 3600" in inspect.getsource(sp.parita_ingressi)


def test_un_ingresso_del_gate_non_viene_usato_due_volte():
    """Senza questo, un solo segnale del gate potrebbe giustificare tre trade del
    paper e la parita' risulterebbe perfetta mentre non lo e'."""
    class _T:
        def __init__(self, ts):
            self.entry_ts = ts

    ptr = [{"entry_time": 1000}, {"entry_time": 1100}]
    par = sp.parita_ingressi(ptr, [_T(1000)], tf_h=0.25)
    assert par["trovati"] == 1, "un ingresso del gate ha coperto due trade del paper"


def test_un_paper_senza_riscontro_si_vede():
    class _T:
        def __init__(self, ts):
            self.entry_ts = ts

    par = sp.parita_ingressi([{"entry_time": 1000}], [_T(999_000)], tf_h=0.25)
    assert par["trovati"] == 0 and par["paper"] == 1


def test_e_sola_lettura():
    """Il paper sta correndo verso i 40 trade: una diagnosi che cambia lo stato
    butterebbe via l'esperimento che sta diagnosticando."""
    src = inspect.getsource(sp)
    for vietato in ("set_doc(", "set_rtdb(", "update_registry"):
        assert vietato not in src, f"lo script scrive: {vietato}"
