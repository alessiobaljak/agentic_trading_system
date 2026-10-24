"""Il simulatore su casi costruiti a mano: ogni numero atteso è calcolato a mano nel commento."""
import pandas as pd
import pytest

from stock.simulatore.costi import Costi
from stock.simulatore.finestre import PeriodoChiuso, controlla_periodo, finestre
from stock.simulatore.motore import Ordine, simula, simula_anche_doppi, statistiche, verso


def barre(righe, giorni=None, **colonne):
    """righe = [(o, h, l, c), ...]; una barra al giorno dal 5 gennaio 2016 (lunedì)."""
    idx = pd.DatetimeIndex(giorni or pd.bdate_range("2016-01-05", periods=len(righe)), tz="America/New_York")
    df = pd.DataFrame(righe, columns=["open", "high", "low", "close"], index=idx.tz_convert("UTC"))
    for k, v in colonne.items():
        df[k] = v
    return df


def una_volta(ordini_alla_barra):
    """Strategia che alla chiusura della barra i manda gli ordini dati (dizionario i -> lista)."""
    def s(storia, stato):
        return ordini_alla_barra.get(len(storia) - 1, [])
    return s


ZERO = Costi()


def test_a_mercato_si_esegue_all_apertura_della_barra_dopo_con_i_costi():
    b = barre([(100, 101, 99, 100), (102, 103, 101, 103), (103, 104, 102, 104)])
    c = Costi(per_azione=0.01, minima=1.0, mezzo_scarto=0.001, slittamento=0.0005)
    r = simula(b, una_volta({0: [Ordine(10, "mercato")]}), c, capitale=10_000)
    e = r.esecuzioni.iloc[0]
    # deciso alla chiusura della barra 0, eseguito all'apertura della barra 1: 102 * 1,0015 = 102,153
    assert e["t"] == b.index[1]
    assert e["prezzo"] == pytest.approx(102.153)
    # commissione: max(1, 0,01*10) = 1
    assert e["commissione"] == pytest.approx(1.0)
    assert r.costo_scarto == pytest.approx(10 * 0.153)
    # valore alla chiusura della barra 2: 10000 - 1021,53 - 1 + 10*104 = 10017,47
    assert r.valore.iloc[2] == pytest.approx(10_017.47)
    assert r.valore.iloc[0] == pytest.approx(10_000)


def test_la_strategia_non_vede_la_barra_in_cui_si_esegue():
    b = barre([(100, 101, 99, 100), (50, 51, 49, 50), (60, 61, 59, 60)])
    viste = []

    def s(storia, stato):
        viste.append(len(storia))
        assert storia.index[-1] <= b.index[len(storia) - 1]
        return []
    simula(b, s, ZERO)
    assert viste == [1, 2, 3]


def test_limite_toccato_non_si_esegue_passato_oltre_si():
    # acquisto a 99: la barra 1 ha minimo esattamente 99 (toccato), la barra 2 minimo 98,99 (passato)
    b = barre([(100, 101, 99.5, 100), (100, 100.5, 99, 100), (100, 100.5, 98.99, 99.5)])
    r = simula(b, una_volta({0: [Ordine(5, "limite", 99)], 1: [Ordine(5, "limite", 99)]}), ZERO)
    assert len(r.esecuzioni) == 1
    assert r.esecuzioni.iloc[0]["t"] == b.index[2]
    assert r.esecuzioni.iloc[0]["prezzo"] == pytest.approx(99)


def test_limite_di_vendita_toccato_non_si_esegue():
    b = barre([(100, 100, 100, 100), (100, 101, 99, 100), (100, 101.01, 99, 100)])
    s = una_volta({0: [Ordine(-5, "limite", 101)], 1: [Ordine(-5, "limite", 101)]})
    r = simula(b, s, ZERO, leva_massima=2)
    assert list(r.esecuzioni["t"]) == [b.index[2]]


def test_limite_con_apertura_gia_oltre_paga_l_apertura_piu_mezzo_scarto():
    b = barre([(100, 100, 100, 100), (97, 98, 96, 97)])
    c = Costi(mezzo_scarto=0.01)
    r = simula(b, una_volta({0: [Ordine(1, "limite", 99)]}), c)
    # 97 * 1,01 = 97,97, sotto il limite 99
    assert r.esecuzioni.iloc[0]["prezzo"] == pytest.approx(97.97)


def test_il_limite_vale_una_sola_barra():
    b = barre([(100, 100, 100, 100), (100, 100, 99.5, 100), (100, 100, 90, 95)])
    r = simula(b, una_volta({0: [Ordine(1, "limite", 99)]}), ZERO)
    assert r.esecuzioni.empty


def test_stop_scatta_al_tocco_e_un_apertura_oltre_lo_salta():
    # posizione comprata nella barra 1 a 100; stop di vendita a 95
    b = barre([(100, 100, 100, 100), (100, 100, 100, 100), (96, 97, 95, 96), (90, 91, 88, 89)])
    s = una_volta({0: [Ordine(10, "mercato")], 1: [Ordine(-10, "stop", 95, solo_riduce=True)]})
    r = simula(b, s, Costi(mezzo_scarto=0.001))
    uscita = r.esecuzioni.iloc[1]
    # toccato esattamente: si esce a 95 * 0,999
    assert uscita["t"] == b.index[2]
    assert uscita["prezzo"] == pytest.approx(95 * 0.999)

    s2 = una_volta({0: [Ordine(10, "mercato")], 2: [Ordine(-10, "stop", 95, solo_riduce=True)]})
    r2 = simula(b, s2, ZERO)
    # apertura 90 sotto lo stop 95: si paga 90, non 95
    assert r2.esecuzioni.iloc[1]["prezzo"] == pytest.approx(90)


def test_stop_e_obiettivo_nella_stessa_barra_vince_il_caso_peggiore():
    b = barre([(100, 100, 100, 100), (100, 100, 100, 100), (100, 106, 94, 100)])
    uscite = [Ordine(-10, "limite", 105, solo_riduce=True), Ordine(-10, "stop", 95, solo_riduce=True)]
    r = simula(b, una_volta({0: [Ordine(10, "mercato")], 1: uscite}), ZERO)
    assert len(r.esecuzioni) == 2
    assert r.esecuzioni.iloc[1]["tipo"] == "stop"
    assert r.esecuzioni.iloc[1]["prezzo"] == pytest.approx(95)
    assert r.valore.iloc[-1] == pytest.approx(100_000 - 50)


def test_solo_riduce_non_gira_la_posizione():
    b = barre([(100, 100, 100, 100), (100, 100, 100, 100), (100, 100, 100, 100)])
    r = simula(b, una_volta({0: [Ordine(3, "mercato")], 1: [Ordine(-10, "mercato", solo_riduce=True)]}), ZERO)
    assert list(r.esecuzioni["quantita"]) == [3, -3]


def test_leva_oltre_il_limite_rifiutata():
    b = barre([(100, 100, 100, 100), (100, 100, 100, 100)])
    r = simula(b, una_volta({0: [Ordine(1001, "mercato")]}), ZERO, capitale=100_000)
    assert r.esecuzioni.empty and r.rifiutati == 1
    r = simula(b, una_volta({0: [Ordine(1000, "mercato")]}), ZERO, capitale=100_000)
    assert len(r.esecuzioni) == 1


def test_dividendo_incassato_da_chi_ha_le_azioni_e_pagato_da_chi_e_allo_scoperto():
    b = barre([(100, 100, 100, 100), (100, 100, 100, 100), (99, 99, 99, 99)], dividendo=[0, 0, 1.0])
    r = simula(b, una_volta({0: [Ordine(10, "mercato")]}), ZERO)
    # 10 azioni, dividendo 1: incasso 10; prezzo sceso da 100 a 99: valore invariato
    assert r.dividendi == pytest.approx(10)
    assert r.valore.iloc[-1] == pytest.approx(100_000)
    r = simula(b, una_volta({0: [Ordine(-10, "mercato")]}), ZERO)
    assert r.dividendi == pytest.approx(-10)
    assert r.valore.iloc[-1] == pytest.approx(100_000)


def test_frazionamento_moltiplica_le_azioni_e_aggiorna_gli_ordini_in_attesa():
    # 4 per 1 nel giorno 2: prezzo da 400 a 100
    b = barre([(400, 400, 400, 400), (400, 400, 400, 400), (100, 101, 98, 100)], frazionamento=[1, 1, 4])
    s = una_volta({0: [Ordine(10, "mercato")], 1: [Ordine(-10, "limite", 396)]})
    r = simula(b, s, ZERO)
    # l'ordine di vendita a 396 diventa 40 azioni a 99: il massimo 101 passa oltre, apertura 100 oltre il limite
    ultima = r.esecuzioni.iloc[1]
    assert ultima["quantita"] == pytest.approx(-40)
    assert ultima["prezzo"] == pytest.approx(100)
    assert r.valore.iloc[-1] == pytest.approx(100_000)


def test_prestito_pagato_per_ogni_notte_allo_scoperto():
    b = barre([(100, 100, 100, 100)] * 4)
    r = simula(b, una_volta({0: [Ordine(-100, "mercato")]}), Costi(prestito_annuo=0.0252))
    # 100 azioni * 100 * 0,0252 / 252 = 1 dollaro a notte; allo scoperto dalle barre 1, 2, 3
    assert r.prestito == pytest.approx(3.0)


def test_commissione_minima_massima_e_costi_doppi():
    c = Costi(per_azione=0.005, minima=1.0, massima_percentuale=0.01)
    assert c.commissione(10, 5) == pytest.approx(0.5)      # minimo 1, ma al massimo l'1% di 50
    assert c.commissione(100, 50) == pytest.approx(1.0)    # 0,5 sotto il minimo
    assert c.commissione(1000, 50) == pytest.approx(5.0)
    assert c.raddoppiati().commissione(1000, 50) == pytest.approx(10.0)
    b = barre([(100, 100, 100, 100), (100, 100, 100, 100), (100, 100, 100, 100)])
    s = una_volta({0: [Ordine(10, "mercato")], 1: [Ordine(-10, "mercato")]})
    v, d = simula_anche_doppi(b, s, Costi(mezzo_scarto=0.001, minima=1))
    assert 100_000 - v.valore.iloc[-1] == pytest.approx(2 + 2 * 1.0)
    assert 100_000 - d.valore.iloc[-1] == pytest.approx(4 + 4 * 1.0)


def test_quantita_frazionaria_rifiutata_se_non_ammessa():
    b = barre([(100, 100, 100, 100), (100, 100, 100, 100)])
    with pytest.raises(ValueError):
        simula(b, una_volta({0: [Ordine(1.5, "mercato")]}), ZERO)
    r = simula(b, una_volta({0: [Ordine(1.5, "mercato")]}), ZERO, frazionarie=True)
    assert r.esecuzioni.iloc[0]["quantita"] == 1.5


def test_ordini_non_validi():
    with pytest.raises(ValueError):
        Ordine(1, "limite")
    with pytest.raises(ValueError):
        Ordine(1, "boh")
    with pytest.raises(ValueError):
        Ordine(0)


def test_verso_e_statistiche():
    from stock.simulatore.motore import Stato
    assert verso(Stato(0, 5), 5) == []
    assert verso(Stato(0, 5), 2)[0].quantita == -3
    idx = pd.DatetimeIndex(pd.bdate_range("2016-01-04", periods=3), tz="UTC")
    st = statistiche(pd.Series([100.0, 110.0, 99.0], index=idx))
    assert st["rendimento_totale"] == pytest.approx(-0.01)
    assert st["perdita_massima"] == pytest.approx(99 / 110 - 1)


def test_barre_al_minuto_prestito_solo_all_ultima_barra_del_giorno():
    t = pd.DatetimeIndex(["2016-01-05 09:30", "2016-01-05 09:31", "2016-01-05 15:59", "2016-01-06 09:30"],
                         tz="America/New_York").tz_convert("UTC")
    b = pd.DataFrame({"open": 100.0, "high": 100.0, "low": 100.0, "close": 100.0}, index=t)
    r = simula(b, una_volta({0: [Ordine(-100, "mercato")]}), Costi(prestito_annuo=0.0252))
    # allo scoperto dalla barra 1: notti pagate = alla barra 2 (ultima del 5) e alla 3 (ultima del 6)
    assert r.prestito == pytest.approx(2.0)


def test_finestre_che_avanzano_e_periodo_chiuso():
    from datetime import date
    f = finestre(date(2016, 1, 1), date(2025, 1, 1), chiuso_dal=date(2025, 1, 1))
    assert f[0] == {"scelta": (date(2016, 1, 1), date(2017, 1, 1)), "prova": (date(2017, 1, 1), date(2017, 4, 1))}
    assert f[-1]["prova"] == (date(2024, 10, 1), date(2025, 1, 1))
    # dal 2017 al 2024 compreso: 8 anni di prove da 3 mesi
    assert len(f) == 32
    # le prove non si sovrappongono e coprono tutto
    for a, b_ in zip(f, f[1:]):
        assert a["prova"][1] == b_["prova"][0]
    with pytest.raises(PeriodoChiuso):
        finestre(date(2016, 1, 1), date(2025, 1, 2), chiuso_dal=date(2025, 1, 1))
    with pytest.raises(PeriodoChiuso):
        controlla_periodo(date(2025, 6, 1), date(2025, 1, 1))
