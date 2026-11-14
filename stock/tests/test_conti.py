"""Le parti nuove della prova 31: l'utile lordo dalle voci della SEC, i beni alla fine dell'esercizio, i 120 giorni, la scelta."""
from datetime import date

from stock.dati import conti
from stock.prove import p031


def test_utile_lordo_prima_grossprofit_poi_ricavi_meno_costo_con_la_stessa_fine():
    f1, f2 = date(2019, 12, 31), date(2020, 12, 31)
    utile = {1: [(f1, 50.0)]}
    ricavi = {v: {} for v in conti.RICAVI}
    costi = {v: {} for v in conti.COSTO}
    ricavi["Revenues"] = {1: [(f1, 999.0), (f2, 200.0)]}
    costi["CostOfRevenue"] = {1: [(date(2020, 11, 30), 1.0)]}      # fine diversa: non vale
    costi["CostOfGoodsSold"] = {1: [(f2, 120.0)]}
    out = conti.utile_lordo(1, utile, ricavi, costi)
    assert out[f1] == (50.0, "GrossProfit")
    assert out[f2] == (80.0, "Revenues-CostOfGoodsSold")


def test_beni_alla_fine_o_nei_31_giorni_prima():
    beni = {date(2020, 11, 30): 10.0, date(2020, 9, 30): 5.0}
    assert conti.beni_a(date(2020, 11, 30), beni) == 10.0
    assert conti.beni_a(date(2020, 12, 31), beni) == 10.0
    assert conti.beni_a(date(2021, 1, 31), beni) is None


def test_redditivita_solo_esercizi_chiusi_120_giorni_prima():
    es = [(date(2019, 1, 31), 0.1), (date(2020, 1, 31), 0.2), (date(2020, 5, 31), 0.9)]
    assert p031.redditivita_al(es, date(2020, 6, 30)) == 0.2       # l'esercizio di maggio non era ancora pubblico
    assert p031.redditivita_al(es, date(2018, 6, 29)) is None


def test_scegli_venti_per_cento_massimo_cinquanta_minimo_cento():
    assert p031.scegli({f"S{i}": i / 100 for i in range(99)}) == ([], [])
    v = {f"S{i:03d}": i / 1000 for i in range(400)}
    alti, bassi = p031.scegli(v)
    assert len(alti) == len(bassi) == 50
    assert alti == [f"S{i:03d}" for i in range(350, 400)] and bassi == [f"S{i:03d}" for i in range(50)]
    a, b = p031.scegli({f"T{i:03d}": i for i in range(150)})
    assert len(a) == len(b) == 30
    assert p031.finanziaria(6021) and not p031.finanziaria(7372) and not p031.finanziaria(None)
