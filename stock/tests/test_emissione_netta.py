"""Le parti nuove della prova 39: il codice SEC di allora e l'emissione netta con la data di deposito e i frazionamenti."""
import math
from datetime import date

from stock.dati.azioni_circolazione import azioni_dichiarate, codice_al
from stock.prove import p039


def test_codice_al_l_ultimo_deposito_entro_un_anno():
    righe = [(date(2017, 3, 1), 111), (date(2018, 6, 1), 111), (date(2019, 2, 1), 222)]
    assert codice_al(righe, date(2018, 12, 31)) == 111
    assert codice_al(righe, date(2019, 2, 1)) == 111                 # il deposito dello stesso giorno non conta ancora
    assert codice_al(righe, date(2019, 3, 1)) == 222                 # il simbolo è passato a un'altra azienda
    assert codice_al(righe, date(2021, 1, 1)) is None                # niente nei 365 giorni prima
    assert codice_al(righe, date(2017, 1, 1)) is None


def test_emissione_con_data_di_deposito_e_frazionamenti():
    d = [(date(2018, 2, 10), date(2018, 1, 20), 1000.0),           # (deposito, riferimento, azioni)
         (date(2019, 2, 12), date(2019, 1, 25), 3800.0),
         (date(2019, 5, 3), date(2019, 4, 20), 3700.0)]
    # a fine marzo 2019: l'ultimo deposito noto è quello di febbraio 2019 (gennaio 2019), contro gennaio 2018, con un frazionamento 4:1
    e = p039.emissione(d, date(2019, 3, 29), {date(2018, 8, 1): 4.0})
    assert abs(e - math.log(3800 / 4000)) < 1e-12
    # il deposito di maggio non si usa prima del giorno dopo il deposito
    assert abs(p039.emissione(d, date(2019, 5, 3), {date(2018, 8, 1): 4.0}) - math.log(3800 / 4000)) < 1e-12
    assert p039.emissione(d, date(2018, 6, 1), {}) is None           # un solo valore
    assert p039.emissione(d[:1] + [(date(2018, 9, 1), date(2018, 8, 20), 990.0)], date(2018, 12, 1), {}) is None   # 7 mesi: troppo vicino


def test_azioni_dichiarate_somma_le_classi_e_si_ferma_al_2024():
    j = {"facts": {"dei": {"EntityCommonStockSharesOutstanding": {"units": {"shares": [
        {"end": "2019-01-25", "val": 100, "accn": "a1", "filed": "2019-02-12"},
        {"end": "2019-01-25", "val": 50, "accn": "a1", "filed": "2019-02-12"},
        {"end": "2025-01-25", "val": 70, "accn": "a2", "filed": "2025-02-12"}]}}}}}
    a = azioni_dichiarate(j)
    assert len(a) == 1 and a["azioni"].iloc[0] == 150
    assert azioni_dichiarate({"facts": {}}).empty
