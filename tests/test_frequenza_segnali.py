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
