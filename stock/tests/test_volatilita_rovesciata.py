"""Il segnale e gli episodi della prova 44 (senza rete)."""
from datetime import date

import pandas as pd

from stock.prove import p044

G = [date(2020, 2, d) for d in (20, 21, 24, 25, 26, 27, 28)]


def test_rovesciata_se_il_vix_e_maggiore_o_uguale():
    vix = pd.Series([15.0, 20.0, 25.0, 18.0], index=G[:4])
    tre = pd.Series([18.0, 20.0, 22.0], index=G[:3])
    s = p044.segnale(vix, tre)
    assert s.to_dict() == {G[0]: False, G[1]: True, G[2]: True}         # pari conta come rovesciata; senza VIX3M il giorno manca


def test_episodi_dentro_il_giorno_dopo_e_fuori_il_giorno_dopo():
    rov = pd.Series([False, True, True, False, True, True, True], index=G)
    assert p044.episodi(rov, G) == [(G[2], G[4]), (G[5], None)]          # 21 rovesciata → dentro il 24; 25 normale → fuori il 26


def test_strategia_ordini_solo_quando_cambia():
    from stock.simulatore.portafoglio import StatoConto
    rov = pd.Series([True, True, False], index=G[:3])
    d = p044.strategia(rov)
    storia = lambda s: pd.DataFrame({"close": [20.0]})  # noqa: E731
    fuori = StatoConto(contanti=100_000.0)
    assert [o[0] for o in d(G[0], storia, fuori)] == ["VIXY"]           # entra
    dentro = StatoConto(contanti=2_000.0, azioni={"VIXY": 4900.0}, ultimo_prezzo={"VIXY": 20.0})
    assert d(G[1], storia, dentro) == []                                   # resta: nessun ordine
    o = d(G[2], storia, dentro)
    assert o[0][0] == "VIXY" and o[0][1].quantita == -4900.0              # esce tutto
