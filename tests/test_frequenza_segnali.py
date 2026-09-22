"""LA SONDA SUI SEGNALI DEVE MISURARE LA SCALA SU CUI IL BOT OPERA.

Il 19 settembre `frequenza` ha risposto «22 trade attesi in 7 giorni, ~3.1 al
giorno» contro i ~3 al giorno che il paper apriva davvero. Messi vicini, quei due
numeri dicevano «tutto torna, nessun segnale viene soppresso» — ed era una
conclusione che non si poteva trarre: **la sonda contava su candele da un'ora, il
bot gira a quindici minuti**. Su candele quattro volte piu' larghe i segnali sono
molti di meno, quindi il numero degli "attesi" era strutturalmente basso.

E' la forma di difetto piu' cara di questo progetto, quella che ha prodotto
BIRBUSDT: non un numero sbagliato, ma un numero GIUSTO PER UN'ALTRA DOMANDA, messo
accanto a uno che risponde a questa. Un test lo rende difficile da rifare.

La voce in lista bianca non puo' passare argomenti (`ops/README.md`: mai `+args`),
quindi il default non e' una comodita' — e' l'unica cosa che verra' mai eseguita.
"""
import inspect

from bot.config import settings
from scripts import signal_frequency as sf


def test_il_default_e_il_timeframe_del_bot():
    """Se questi due divergono, il report confronta mele con pere ogni volta che
    qualcuno lancia `frequenza` dalla lista bianca."""
    ap = [a for a in _argomenti() if a.dest == "interval"][0]
    assert ap.default == settings.ORCHESTRATOR_TIMEFRAME


def test_non_c_e_piu_un_timeframe_scritto_a_mano():
    """La versione precedente aveva `default="1h"` e una mappa `{"15m":..,"1h":..}`
    accanto: due posti in cui scrivere una scala, nessuno dei due legato al bot."""
    src = inspect.getsource(sf.main)
    assert 'default="1h"' not in src


def test_ogni_timeframe_supportato_ha_la_sua_durata():
    """Un timeframe assente cadeva nel default `1.0` ora/candela: a 5m avrebbe
    contato i trade su una finestra dodici volte piu' lunga di quella dichiarata,
    senza dirlo."""
    assert sf.ORE_PER_CANDELA[settings.ORCHESTRATOR_TIMEFRAME] > 0
    assert sf.ORE_PER_CANDELA["15m"] == 0.25 and sf.ORE_PER_CANDELA["1h"] == 1.0


def test_il_warmup_si_adatta_al_timeframe():
    """L'engine salta le prime 200 candele per gli indicatori. Il buffer di storia
    deve coprirle: fisso a 12 giorni bastava a 1h e sarebbe stato insufficiente a
    4h, cioe' la finestra contata non sarebbe stata quella dichiarata."""
    src = inspect.getsource(sf.main)
    assert "200 * ore" in src, "il warmup non e' piu' legato alla larghezza candela"


def test_avvisa_quando_la_scala_non_e_quella_del_bot():
    """Resta possibile lanciarlo a mano su un'altra scala — serve, per confrontare
    i timeframe. Ma il report deve DIRLO, perche' chi lo legge dopo non ha il
    comando sotto gli occhi."""
    src = inspect.getsource(sf.main)
    assert "NON sono confrontabili" in src


def _argomenti():
    """Gli argomenti dichiarati da `main`, senza eseguirlo."""
    import argparse

    catturati = []
    vero = argparse.ArgumentParser.add_argument

    def spia(self, *a, **k):
        azione = vero(self, *a, **k)
        catturati.append(azione)
        return azione

    class _Stop(Exception):
        pass

    def basta(self, *a, **k):
        raise _Stop

    argparse.ArgumentParser.add_argument = spia
    argparse.ArgumentParser.parse_args = basta
    try:
        sf.main()
    except _Stop:
        pass
    finally:
        argparse.ArgumentParser.add_argument = vero
        del argparse.ArgumentParser.parse_args
    return catturati


# --------------------------------------------------------------------------- #
# Il vincolo di una posizione per moneta                                       #
# --------------------------------------------------------------------------- #
def test_segnali_sovrapposti_sulla_stessa_coin_contano_uno():
    """ORCAUSDT ha sei strategie validate. Il conto grezzo somma i loro trade come
    se potessero stare aperti tutti insieme; il bot ne tiene UNA per moneta. Senza
    questa distinzione il numero grezzo finiva accanto ai trade veri del paper e la
    differenza sembrava un difetto — mentre e' il comportamento voluto."""
    # tre segnali che si accavallano nella stessa ora
    assert sf.apribili_una_per_coin([(0, 3600), (600, 4200), (1200, 4800)]) == 1


def test_segnali_in_fila_contano_tutti():
    """Se la moneta si libera prima del segnale successivo, il bot li apre tutti:
    il vincolo non deve nascondere una soppressione vera."""
    assert sf.apribili_una_per_coin([(0, 100), (200, 300), (400, 500)]) == 3


def test_l_ordine_di_arrivo_non_dipende_da_come_sono_elencati():
    """I trade arrivano raggruppati per strategia, non in ordine di tempo: se la
    funzione non riordinasse, il conto dipenderebbe dall'ordine delle strategie."""
    disordinati = [(400, 500), (0, 100), (200, 300)]
    assert sf.apribili_una_per_coin(disordinati) == 3


def test_un_segnale_che_arriva_esattamente_alla_chiusura_entra():
    """Il confine: la posizione si chiude e la moneta e' libera nello stesso
    istante. Escluderlo sottostimerebbe gli apribili, cioe' renderebbe il divario
    col paper piu' piccolo del vero — l'errore nella direzione comoda."""
    assert sf.apribili_una_per_coin([(0, 100), (100, 200)]) == 2


def test_nessun_segnale_nessun_apribile():
    assert sf.apribili_una_per_coin([]) == 0


def test_i_selezionati_sono_gli_stessi_che_vengono_contati():
    """Il conto e il dettaglio devono venire dalla STESSA regola. Se divergessero,
    il totale della settimana e la ripartizione giorno per giorno racconterebbero
    due storie diverse dello stesso fatto — e non ci sarebbe modo di sapere quale
    delle due e' quella su cui si sta decidendo."""
    casi = [
        [(0, 3600), (600, 4200), (1200, 4800)],
        [(0, 100), (200, 300), (400, 500)],
        [(400, 500), (0, 100), (200, 300)],
        [],
    ]
    for c in casi:
        assert len(sf.selezionati_una_per_coin(c)) == sf.apribili_una_per_coin(c)


def test_il_dettaglio_restituisce_le_finestre_davvero_prese():
    """Non un conteggio: servono gli orari, perche' il confronto col paper si fa
    giorno per giorno e il totale della settimana non e' confrontabile."""
    presi = sf.selezionati_una_per_coin([(0, 3600), (600, 4200), (7200, 9000)])
    assert presi == [(0, 3600), (7200, 9000)]


def test_il_report_riparte_gli_apribili_per_giorno():
    """Il totale settimanale sovrastima per costruzione: la sonda usa le coppie
    validate di OGGI su giorni in cui il registro ne aveva meno. Senza la
    ripartizione, l'unica risposta possibile era «rifacciamo la misura fra una
    settimana»."""
    src = inspect.getsource(sf.main)
    assert "APRIBILI giorno per giorno" in src
    assert "selezionati_una_per_coin" in src


def test_anche_i_trade_veri_sono_ripartiti_per_giorno():
    """Il confronto ha bisogno di due serie, non di una serie e una media."""
    from scripts import trade_stats

    assert "per giorno (UTC)" in inspect.getsource(trade_stats.main)



def test_la_sonda_conta_anche_OGGI():
    """22 set 2026: la tabella giorno per giorno si fermava a ieri, perche' il
    taglio delle candele e' escluso a mezzanotte. Alla domanda «e' normale che
    oggi non abbia aperto niente?» non poteva rispondere. Oggi si stampa sempre,
    anche a zero: e' esattamente la riga che serve."""
    import inspect

    from scripts import signal_frequency as sf

    src = inspect.getsource(sf.main)
    assert "end=(date.today() + timedelta(days=1)).isoformat()" in src
    assert "per_giorno.setdefault(oggi, 0)" in src
