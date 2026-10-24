"""Il simulatore a più titoli su casi costruiti a mano."""
import pandas as pd
import pytest

from stock.simulatore.costi import Costi
from stock.simulatore.motore import Ordine
from stock.simulatore.portafoglio import simula_conto, verso_pesi


def barre(righe, giorni, **colonne):
    idx = pd.DatetimeIndex(giorni, tz="America/New_York").tz_convert("UTC")
    df = pd.DataFrame(righe, columns=["open", "high", "low", "close"], index=idx)
    for k, v in colonne.items():
        df[k] = v
    return df


G = ["2020-01-06", "2020-01-07", "2020-01-08", "2020-01-09"]


def al_giorno(piano):
    """piano: {indice del giorno: [(simbolo, Ordine)]}"""
    def s(giorno, storia, stato):
        return piano.get(G.index(str(giorno)), [])
    return s


def test_vendite_prima_degli_acquisti_e_valore_con_l_ultima_chiusura():
    a = barre([(100, 100, 100, 100)] * 4, G)
    b = barre([(50, 50, 50, 50), (50, 50, 50, 50), (50, 60, 50, 60), (70, 70, 70, 70)], G)
    piano = {0: [("A", Ordine(990, "mercato"))],
             # il giorno 2 vende A e compra B con gli stessi contanti: funziona solo se la vendita va prima
             1: [("B", Ordine(1980, "mercato")), ("A", Ordine(-990, "mercato"))]}
    r = simula_conto({"A": a, "B": b}, al_giorno(piano), Costi(), capitale=100_000)
    assert r.rifiutati == 0
    assert list(r.esecuzioni["simbolo"]) == ["A", "A", "B"]
    # 1000 di contanti + 1980 * 70 alla fine
    assert r.valore.iloc[-1] == pytest.approx(1_000 + 1_980 * 70)


def test_ordine_senza_barra_non_si_esegue_e_titolo_bloccato():
    a = barre([(100, 100, 100, 100)] * 2, G[:2])                  # sparisce dopo il 7 gennaio
    b = barre([(10, 10, 10, 10)] * 4, G)
    piano = {0: [("A", Ordine(10, "mercato"))], 1: [("A", Ordine(-10, "mercato"))]}
    r = simula_conto({"A": a, "B": b}, al_giorno(piano), Costi())
    assert r.senza_barra == 1 and r.bloccati == ["A"]
    # A resta valutato all'ultima chiusura
    assert r.valore.iloc[-1] == pytest.approx(100_000)


def test_leva_sul_conto_intero_e_dividendo_su_un_titolo():
    a = barre([(100, 100, 100, 100), (100, 100, 100, 100), (99, 99, 99, 99), (99, 99, 99, 99)], G, dividendo=[0, 0, 1, 0])
    b = barre([(100, 100, 100, 100)] * 4, G)
    piano = {0: [("A", Ordine(600, "mercato")), ("B", Ordine(500, "mercato"))]}
    r = simula_conto({"A": a, "B": b}, al_giorno(piano), Costi())
    # 600 di A passano, 500 di B porterebbero il lordo a 110'000 > 100'000: rifiutato
    assert r.rifiutati == 1
    assert r.dividendi == pytest.approx(600)
    assert r.valore.iloc[-1] == pytest.approx(100_000)


def test_frazionamento_e_costi_per_titolo():
    a = barre([(400, 400, 400, 400), (400, 400, 400, 400), (100, 100, 100, 100), (100, 100, 100, 100)], G,
              frazionamento=[1, 1, 4, 1])
    piano = {0: [("A", Ordine(10, "mercato"))], 2: [("A", Ordine(-40, "mercato"))]}
    r = simula_conto({"A": a}, al_giorno(piano), {"A": Costi(mezzo_scarto=0.001)})
    assert list(r.esecuzioni["quantita"]) == [10, -40]
    assert r.valore.iloc[-1] == pytest.approx(100_000 - 4 - 4)


def test_la_strategia_non_vede_il_giorno_dopo():
    a = barre([(1, 1, 1, 1), (2, 2, 2, 2), (3, 3, 3, 3), (4, 4, 4, 4)], G)
    visti = []

    def s(giorno, storia, stato):
        visti.append(float(storia("A")["close"].iloc[-1]))
        assert storia("X") is None
        return []
    simula_conto({"A": a}, s, Costi())
    assert visti == [1, 2, 3, 4]


def test_verso_pesi():
    from stock.simulatore.portafoglio import StatoConto
    st = StatoConto(contanti=10_000, azioni={"C": 5}, ultimo_prezzo={"C": 100})
    o = dict((s, x.quantita) for s, x in verso_pesi(st, {"A": 0.5, "B": 0.5}, {"A": 10, "B": 20}, quota=1.0))
    # valore 10500: A 525 azioni, B 262, C si vende
    assert o == {"A": 525, "B": 262, "C": -5}
