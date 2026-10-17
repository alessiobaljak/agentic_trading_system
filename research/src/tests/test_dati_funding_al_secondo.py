"""Il caricatore arrotonda al secondo l'istante dei settlement di funding (CHANGELOG, 8 ott 2026)."""

from datetime import date

from research.src import dati
from research.src.motore import Candela, Parametri, Segnale, esegui
from research.src.tests.test_dati import ORA, TS_2023_01_01, FetchFinto, zip_in_memoria


def test_settlement_con_millisecondi_riportati_al_secondo(tmp_path):
    t0 = TS_2023_01_01
    testo = f"{t0 + 2},8,0.0001\n{t0 + 8 * ORA + 47},8,0.0002\n{t0 + 16 * ORA},8,0.0003\n"
    fetch = FetchFinto({dati.url_mese("BTCUSDT", "fundingRate", None, 2023, 1): zip_in_memoria("f.csv", testo)})
    dati.scarica_periodo("BTCUSDT", "fundingRate", None, date(2023, 1, 1), date(2023, 1, 31), tmp_path, fetch)
    assert dati.carica_funding("BTCUSDT", date(2023, 1, 1), date(2023, 1, 31), tmp_path) == [
        (t0, 0.0001), (t0 + 8 * ORA, 0.0002), (t0 + 16 * ORA, 0.0003)]


def test_con_l_arrotondamento_il_funding_all_ingresso_e_ambiguo():
    """Long entrato all'apertura di una barra con un settlement (incasso) nello stesso istante:
    il momento e' ambiguo e un incasso non si conta (sezione 7). Con 47 ms di ritardo il
    motore lo contava come incasso certo."""
    t0 = TS_2023_01_01
    candele = [Candela(t0 + k * ORA, 100, 101, 99, 100, 1, t0 + (k + 1) * ORA - 1) for k in range(4)]
    stato = {"fatto": False}

    def strategia(storia, pos):
        if pos is None and not stato["fatto"]:
            stato["fatto"] = True
            return Segnale("long", stop=90)
        return "chiudi" if pos is not None else None

    def funding_pagato(funding):
        stato["fatto"] = False
        return esegui(candele, None, None, funding, strategia, Parametri()).trades[0].funding_pagato

    tasso_negativo = -0.001  # il long incassa
    assert funding_pagato([(t0 + ORA, tasso_negativo)]) == 0.0
    assert funding_pagato([(t0 + ORA + 47, tasso_negativo)]) < 0.0  # il caso che l'arrotondamento evita
