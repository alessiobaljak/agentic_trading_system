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

from scripts import confronto_gate_paper as sp


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


# --------------------------------------------------------------------------- #
# IL CONFRONTO COMPLETO: non solo il win rate                                 #
# --------------------------------------------------------------------------- #
def test_i_gradini_si_contano_uguale_dalle_due_parti():
    """LA RICHIESTA DEL 21 SETTEMBRE: «voglio confrontare tutti i dati, non solo
    il win rate». Sotto scale-out «vinto» non dice quasi niente — chi tocca il
    primo gradino e torna a pareggio incassa 0,45R lordi, chi arriva in fondo
    3,35R, ed entrambi sono «vittorie». Il numero di gradini invece si confronta,
    perche' si ricava da `mfe_r`, che esiste sia nel backtest sia nel paper."""
    mults = (1.5, 3.0, 5.0)
    # 0 gradini, 1, 2, 3
    assert sp.gradini_raggiunti([0.4, 2.0, 3.5, 7.0], mults) == [1, 1, 1, 1]
    assert sp.gradini_raggiunti([], mults) == [0, 0, 0, 0]


def test_i_gradini_usano_LA_STESSA_funzione_di_gate_vs_paper():
    """Se questo script ricalcolasse le fasce per conto suo, i due strumenti
    direbbero numeri diversi sulla stessa coppia — e non ci sarebbe modo di
    sapere quale ha ragione. Tre copie di `judge_window` sono gia' costate care."""
    import inspect

    from scripts import gate_vs_paper as gvp

    assert "from scripts.gate_vs_paper import _bucket_of" in inspect.getsource(sp)
    mults = (1.5, 3.0, 5.0)
    for m in (0.0, 1.49, 1.5, 3.0, 4.9, 5.0, 12.0):
        atteso = [0] * (len(mults) + 1)
        atteso[gvp._bucket_of(m, mults)] += 1
        assert sp.gradini_raggiunti([m], mults) == atteso, m


def test_il_gradino_di_confine_conta_come_raggiunto():
    """Un mfe ESATTAMENTE sul gradino lo ha toccato. Metterlo nella fascia sotto
    sposterebbe in silenzio ogni trade di confine dalla parte sbagliata."""
    assert sp.gradini_raggiunti([1.5], (1.5, 3.0, 5.0)) == [0, 1, 0, 0]


def test_si_confrontano_rapporti_e_medie_mai_due_somme():
    """Il backtest somma variazioni di prezzo, il paper USDT: affiancare le due
    somme come se fossero la stessa grandezza e' il modo piu' facile di produrre
    un confronto dall'aria seria e senza senso."""
    d = sp.profilo("X", [1.0], [2.0], [True], (1.5, 3.0, 5.0))
    assert "per_trade" in d and "pf" in d
    assert "pnl_totale" not in d


def test_un_paper_senza_vincite_non_stampa_un_PF_finto(capsys):
    """Con zero guadagni il profit factor non e' zero: non e' calcolabile. Uno
    «0.00» si legge come una misura e non lo e'."""
    mults = (1.5, 3.0, 5.0)
    g = sp.profilo("GATE", [2.0], [1.0], [True], mults)
    p = sp.profilo("PAPER", [0.3, 0.4], [-1.0, -2.0], [False, False], mults)
    sp.stampa_confronto(g, p, mults)
    riga = [r for r in capsys.readouterr().out.splitlines() if "PAPER" in r][0]
    assert "—" in riga and "0.00" not in riga


def test_le_vincite_consecutive_si_contano_come_le_perdite():
    """La stessa funzione, con gli esiti rovesciati: due implementazioni
    separate divergerebbero sul caso di confine (la serie che arriva in fondo),
    che e' proprio quello che interessa."""
    d = sp.profilo("X", [1.0] * 5, [1, 1, 1, -1, -1],
                   [True, True, True, False, False], (1.5, 3.0, 5.0))
    assert d["vincite_max"] == 3 and d["perdite_max"] == 2


def test_le_finestre_dicono_su_quante_possibili(capsys):
    """«7 volte» senza il denominatore non e' una frequenza. Serve sapere su
    quante occasioni, altrimenti non si puo' dire se sia raro o normale."""
    sp._finestre("GATE", [False, False, True, False, False, False], 3)
    out = capsys.readouterr().out
    assert "su 4" in out and "%" in out


def test_una_storia_piu_corta_della_finestra_lo_dice(capsys):
    """Stampare «0 volte» quando la storia e' troppo corta significherebbe dire
    «non succede mai» al posto di «non lo so»."""
    sp._finestre("GATE", [False, False], 5)
    assert "non confrontabile" in capsys.readouterr().out


def test_un_orario_in_formato_ISO_non_diventa_ZERO():
    """IL DIFETTO DEL 21 SETTEMBRE, e il piu' pericoloso di tutta la giornata.

    Questo file aveva un `_ts` suo, `float(v)` e basta. Ma `entry_time` nel paper
    e' una stringa ISO: ogni trade diventava 0, veniva saltato dal confronto, e il
    report stampava «0/21 ingressi combaciano» — che si legge come «il paper non
    sta operando le strategie del gate». Un allarme gravissimo, falso, prodotto
    proprio dallo strumento costruito per scoprirlo.

    La correzione non e' aggiustare la copia: e' non averne una. La funzione si
    importa da `gate_vs_paper`, che gestisce entrambi i formati da sempre."""
    iso = "2026-09-20T16:12:00+00:00"
    assert sp._ts(iso) > 1_700_000_000, "una data ISO non deve valere zero"
    assert sp._ts(1_758_384_720.0) == 1_758_384_720.0
    assert sp._ts(None) == 0.0


def test_il_tempo_NON_viene_riscritto_in_questo_file():
    """Una seconda copia tornerebbe a divergere: e' gia' successo qui, ed era
    invisibile perche' il risultato sbagliato aveva l'aria di una scoperta."""
    import inspect

    src = inspect.getsource(sp)
    assert "def _ts(" not in src, "c'e' di nuovo una copia locale di _ts"
    assert "from scripts.gate_vs_paper import" in src and "_ts" in src


def test_gli_ingressi_combaciano_con_orari_ISO():
    """La prova end-to-end del difetto: con date ISO il confronto deve trovare la
    corrispondenza, non zero."""
    class _T:
        def __init__(self, ts):
            self.entry_ts = ts

    quando = sp._ts("2026-09-20T16:12:00+00:00")
    par = sp.parita_ingressi([{"entry_time": "2026-09-20T16:12:00+00:00"}],
                             [_T(quando + 300)], tf_h=0.25)
    assert par["trovati"] == 1
