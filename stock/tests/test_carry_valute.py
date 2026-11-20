"""Il segnale della prova 43: il tasso di due mesi prima, la scelta delle valute, l'ultimo giorno del mese."""
from datetime import date


def test_carry_tasso_di_due_mesi_prima_e_scelta_delle_valute():
    from stock.prove import p043
    assert p043.mese_del_tasso(date(2016, 1, 29)) == "2015-11" and p043.mese_del_tasso(date(2016, 2, 29)) == "2015-12"
    t = {"FXA": 2.0, "FXB": 0.5, "FXC": 1.0, "FXE": -0.3, "FXF": -0.7, "FXY": -0.3}
    assert p043.scegli(t) == (["FXA", "FXC"], ["FXE", "FXF"])            # a pari tasso (FXE, FXY) in ordine alfabetico
    assert p043.scegli({"FXA": 1.0}) == ([], [])                          # senza tutte e sei: niente
    assert p043.fine_dei_mesi([date(2016, 1, 28), date(2016, 1, 29), date(2016, 2, 1)]) == [date(2016, 1, 29), date(2016, 2, 1)]
