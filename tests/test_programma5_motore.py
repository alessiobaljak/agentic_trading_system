"""Il motore comune del programma 5 (research/programma5/strumenti/motore5.py): simulatore, costi, funding, caso,
bootstrap e guardiano dei periodi."""
import numpy as np
import pandas as pd
import pytest

from research.programma5.strumenti import motore5 as m5


def _df(prezzi, alti=None, bassi=None, inizio=27_000_000):
    prezzi = np.asarray(prezzi, float)
    alti = prezzi if alti is None else np.asarray(alti, float)
    bassi = prezzi if bassi is None else np.asarray(bassi, float)
    idx = np.arange(inizio, inizio + len(prezzi))
    return pd.DataFrame({"open": prezzi, "high": alti, "low": bassi, "close": prezzi,
                         "volume": 1.0, "quote_volume": 1.0, "taker_buy_volume": 0.5, "periodo": True}, index=idx)


def test_uscita_a_tempo_con_i_costi_di_btc():
    df = _df([100, 100, 101, 102, 103, 104, 105])
    t = m5.simula(df, "BTCUSDT", np.array([0]), np.array([1]), m5.Uscita(minuti=3))
    # ingresso all'apertura del minuto 1 (100), uscita alla chiusura del minuto 3 (102)
    assert t.iloc[0]["lordo"] == pytest.approx(0.02)
    assert t.iloc[0]["costo"] == pytest.approx(2 * (0.0005 + 0.0001))
    assert t.iloc[0]["netto"] == pytest.approx(0.02 - 0.0012)
    assert t.iloc[0]["netto_doppio"] == pytest.approx(0.02 - 0.0024)


def test_stop_prima_del_target_nella_stessa_candela_e_scarto_doppio_nelle_esplosioni():
    df = _df([100, 100, 100, 100], alti=[100, 100, 103, 100], bassi=[100, 100, 97, 100])
    t = m5.simula(df, "DOGEUSDT", np.array([0]), np.array([1]), m5.Uscita(minuti=3, stop=0.02, target=0.02),
                  esplosione=np.array([True]))
    assert t.iloc[0]["motivo"] == "stop"
    assert t.iloc[0]["lordo"] == pytest.approx(-0.02)
    assert t.iloc[0]["costo"] == pytest.approx(2 * (0.0005 + 2 * 0.0002))


def test_short_e_funding_pagato_dal_long_e_incassato_dallo_short():
    df = _df([100] * 10)
    fund = pd.DataFrame({"ore": [8], "tasso": [0.001]}, index=[df.index[4]])
    lungo = m5.simula(df, "BTCUSDT", np.array([0]), np.array([1]), m5.Uscita(minuti=6), fund)
    corto = m5.simula(df, "BTCUSDT", np.array([0]), np.array([-1]), m5.Uscita(minuti=6), fund)
    assert lungo.iloc[0]["funding"] == pytest.approx(0.001)
    assert corto.iloc[0]["funding"] == pytest.approx(-0.001)
    # un regolamento fuori dal trade non conta
    fuori = pd.DataFrame({"ore": [8], "tasso": [0.001]}, index=[df.index[9]])
    assert m5.simula(df, "BTCUSDT", np.array([0]), np.array([1]), m5.Uscita(minuti=3), fuori).iloc[0]["funding"] == 0


def test_il_caso_tiene_mese_e_direzione():
    df = _df(np.linspace(100, 110, 5000))
    t = m5.simula(df, "BTCUSDT", np.array([10, 2000]), np.array([1, -1]), m5.Uscita(minuti=5))
    c = m5.caso(df, "BTCUSDT", t, m5.Uscita(minuti=5), ripetizioni=3)
    assert len(c) == 6 and set(c["direzione"]) == {1, -1}


def test_bootstrap_dice_p_piccolo_per_un_guadagno_netto_e_grande_per_zero():
    rng = np.random.default_rng(1)
    minuti = np.arange(0, 1440 * 300, 1440)
    buono = m5.bootstrap_giorni(rng.normal(0.01, 0.01, 300), minuti)
    nullo = m5.bootstrap_giorni(rng.normal(0.0, 0.01, 300), minuti)
    assert buono["p"] < 0.001 and buono["basso"] > 0
    assert nullo["p"] > 0.01


def test_il_guardiano_non_apre_la_validazione_senza_regola_congelata():
    with pytest.raises(m5.PeriodoChiuso):
        m5.controlla_periodo("V", "I-999")
    with pytest.raises(m5.PeriodoChiuso):
        m5.controlla_periodo("R", None)
    m5.controlla_periodo("C", None)


def test_i_file_giornalieri_e_mensili_si_riconoscono_per_data():
    from datetime import date
    assert m5._dentro("BTCUSDT-metrics-2020-09-01.zip", date(2020, 9, 1), date(2020, 9, 30))
    assert not m5._dentro("BTCUSDT-metrics-2023-01-01.zip", date(2020, 1, 1), date(2022, 12, 31))
    assert m5._dentro("BTCUSDT-1m-2022-12.zip", date(2020, 1, 1), date(2022, 12, 31))
    assert not m5._dentro("BTCUSDT-1m-2023-01.zip", date(2020, 1, 1), date(2022, 12, 31))
    assert m5._dentro("BTCUSDT-1m-2026-10-05.zip", date(2026, 10, 1), date(2099, 12, 31))


def test_ordine_limite_si_esegue_solo_attraversando_il_livello():
    # minimo che tocca il livello senza attraversarlo: niente; minimo sotto: eseguito al livello
    df = _df([100, 100, 100, 100, 100, 100], bassi=[100, 99, 100, 98.5, 100, 100])
    nulla = m5.simula_limite(df, "BTCUSDT", np.array([0]), np.array([99.0]), np.array([1]), validita=3, tenuta=1)
    assert nulla.empty
    t = m5.simula_limite(df, "BTCUSDT", np.array([0]), np.array([99.0]), np.array([1]), validita=4, tenuta=1)
    assert len(t) == 1 and t.iloc[0]["decisione"] == 3
    assert t.iloc[0]["lordo"] == pytest.approx(100 / 99 - 1)
    assert t.iloc[0]["costo"] == pytest.approx(0.0002 + 0.0005 + 2 * 0.0001)


def test_ordine_limite_di_vendita_e_niente_ordini_nuovi_col_trade_aperto():
    df = _df([100] * 12, alti=[100, 102, 100, 100, 100, 100, 100, 102, 100, 100, 100, 100])
    t = m5.simula_limite(df, "DOGEUSDT", np.array([0, 2, 6]), np.array([101.0, 101.0, 101.0]),
                         np.array([-1, -1, -1]), validita=2, tenuta=3)
    # il primo si esegue al minuto 1 ed esce al 4; il secondo parte al 2 (trade aperto): saltato; il terzo al 7
    assert list(t["decisione"]) == [1, 7]
    assert t.iloc[0]["lordo"] == pytest.approx(-(100 / 101 - 1))


def test_le_barre_orarie_passano_dal_guardiano_anche_dalla_cache():
    from research.programma5.strumenti import ore
    with pytest.raises(m5.PeriodoChiuso):
        ore.barre("BTCUSDT", "V", "I-999")


def test_la_gamba_a_tempo_delle_idee_a_ore_e_uguale_al_simulatore():
    from research.programma5.strumenti import idee_ore
    rng = np.random.default_rng(3)
    prezzi = 100 * np.exp(np.cumsum(rng.normal(0, 0.001, 400)))
    df = _df(prezzi)
    fund = pd.DataFrame({"ore": [8, 8], "tasso": [0.001, -0.0005]}, index=[df.index[50], df.index[200]])
    pos = np.array([10, 40, 150, 300])
    lordo, costo, fu = idee_ore._tempo(df, "DOGEUSDT", pos, -1, 60, fund)
    t = m5.simula(df, "DOGEUSDT", pos, -np.ones(4, int), m5.Uscita(minuti=60), fund, esplosione=np.ones(4, bool))
    assert np.allclose(lordo, t["lordo"]) and np.allclose(costo, t["costo"]) and np.allclose(fu, t["funding"])


def test_scalping_uscita_a_limite_solo_dal_minuto_dopo_e_ad_attraversamento():
    from research.programma5.strumenti import scalping
    # minuto 1: minimo 98,5 (sotto 99: eseguito a 99) e massimo 101 nello stesso minuto: il target 100 non vale li'
    # minuto 2: massimo 100 (tocca ma non attraversa); minuto 3: massimo 100,5 (attraversa): uscita a 100
    df = _df([100, 100, 99.5, 99.8, 99.9, 99.9], alti=[100, 101, 100, 100.5, 100, 100],
             bassi=[100, 98.5, 99.2, 99.5, 99.5, 99.5])
    sg = np.log(100 / 99)
    t = scalping.simula_doppio(df, "BTCUSDT", np.array([0]), np.array([99.0]), np.array([sg]), np.array([1]),
                               m=1.0, validita=3, tenuta=4)
    assert len(t) == 1 and t.iloc[0]["motivo"] == "target"
    assert t.iloc[0]["lordo"] == pytest.approx(100 / 99 - 1)
    assert t.iloc[0]["costo"] == pytest.approx(2 * 0.0002)
    # senza attraversamento del target: uscita a mercato alla chiusura del minuto 1 + 2, con costi a mercato
    t2 = scalping.simula_doppio(df, "BTCUSDT", np.array([0]), np.array([99.0]), np.array([sg]), np.array([1]),
                                m=1.0, validita=3, tenuta=1)
    assert t2.iloc[0]["motivo"] == "tempo" and t2.iloc[0]["lordo"] == pytest.approx(99.5 / 99 - 1)
    assert t2.iloc[0]["costo"] == pytest.approx(0.0002 + 0.0005 + 2 * 0.0001)


def test_fase_2_costruzione_aperta_e_prova_solo_con_la_regola_congelata():
    m5.controlla_periodo("C2", None)
    with pytest.raises(m5.PeriodoChiuso):
        m5.controlla_periodo("V2", "J-999")
    with pytest.raises(m5.PeriodoChiuso):
        m5.controlla_periodo("V2", None)


def test_portafoglio_long_le_prime_short_le_ultime_con_i_costi_di_ogni_gamba():
    from research.programma5.strumenti import portafoglio as pf
    ore = np.arange(10)
    punti = {"AUSDT": np.full(10, 3.0), "BUSDT": np.full(10, 2.0), "CUSDT": np.full(10, 1.0), "DUSDT": np.full(10, 0.0)}
    A = {"AUSDT": np.full(10, 0.02), "BUSDT": np.full(10, 0.01), "CUSDT": np.full(10, 0.0), "DUSDT": np.full(10, -0.01)}
    t = pf.gambe(ore, punti, A, np.array([2]), quanti=1, minimo=4, verso=1)
    assert set(t["simbolo"]) == {"AUSDT", "DUSDT"}
    # portafoglio: (0,02 - (-0,01)) / 2 = 0,015 lordo; costi: meta' capitale per gamba, un giro a mercato ciascuna
    assert t["lordo"].sum() == pytest.approx(0.015)
    assert t["costo"].sum() == pytest.approx(0.5 * 2 * (0.0005 + 0.0002) * 2)
    contro = pf.gambe(ore, punti, A, np.array([2]), quanti=1, minimo=4, verso=-1)
    assert contro["lordo"].sum() == pytest.approx(-0.015)
    e = pf.esame_portafoglio(t, t.assign(ripetizione=0), n_boot=50)
    assert e["portafogli"] == 1 and e["per_moneta"]["AUSDT"]["netto"] == pytest.approx(0.02 - 0.005)


def test_meta_sceglie_solo_con_i_trade_gia_chiusi():
    from research.programma5.strumenti import meta
    gennaio, febbraio, marzo = meta.minuto_mese(0), meta.minuto_mese(1), meta.minuto_mese(2)
    giorni = np.arange(40)
    # candidata «buona» in gennaio (chiusa in gennaio) e una «tardiva» che entra in gennaio ma esce in febbraio
    buona = pd.DataFrame({"moneta": "AUSDT", "entrata": gennaio + giorni[:25] * 1440, "uscita": gennaio + giorni[:25] * 1440 + 60,
                          "lordo": 0.01 + 0.001 * (giorni[:25] % 3), "costo": 0.001, "famiglia": "F1"})
    tardiva = pd.DataFrame({"moneta": "BUSDT", "entrata": gennaio + giorni[:25] * 1440,
                            "uscita": febbraio + 5 * 1440 + giorni[:25], "lordo": 0.05 + 0.001 * (giorni[:25] % 3),
                            "costo": 0.001, "famiglia": "F5"})
    # in febbraio tutte e due operano
    buona = pd.concat([buona, buona.assign(entrata=buona["entrata"] + 31 * 1440, uscita=buona["uscita"] + 31 * 1440)])
    tardiva = pd.concat([tardiva, tardiva.assign(entrata=tardiva["entrata"] + 31 * 1440)])
    cand = {("A", "segue"): buona, ("B", "segue"): tardiva}
    scelti, scelte = meta.scegli_e_tieni(cand, L=1, K=5, primo=1, ultimo=1, n_mesi=4, min_trade=10, t_min=1.0)
    # a inizio febbraio la «tardiva» non ha trade chiusi: si sceglie solo la «buona»
    assert scelte[1] == [("A", "segue")]
    assert set(scelti["cella"]) == {"A"}


def test_meta_t_da_aggregati_come_t_per_giorni():
    from research.programma5.strumenti import meta
    from research.programma5.strumenti.esplorazione import t_giorni
    rng = np.random.default_rng(5)
    uscita = meta.minuto_mese(0) + rng.integers(0, 80 * 1440, 300)
    netto = rng.normal(0.002, 0.01, 300)
    a = meta.aggregati(netto, uscita, 4).sum(axis=0)
    n, m, t = meta.t_da_aggregati(a)
    assert n == 300 and m == pytest.approx(netto.mean()) and t == pytest.approx(t_giorni(netto, uscita // 1440))


def test_fase_3_periodo_intero_solo_con_la_regola_congelata():
    with pytest.raises(m5.PeriodoChiuso):
        m5.controlla_periodo("W", "M-999")


def test_meta2_sceglie_chi_batte_il_caso_non_chi_segue_il_mercato():
    from research.programma5.strumenti import meta, meta2
    gennaio = meta.minuto_mese(0)
    giorni = np.arange(25)
    base = dict(moneta="AUSDT", entrata=gennaio + giorni * 1440, uscita=gennaio + giorni * 1440 + 60, costo=0.001)
    rumore = 0.001 * (giorni % 3)
    # «mercato»: guadagna quanto il mese (base uguale al lordo); «tempismo»: guadagna piu' del mese
    mercato = pd.DataFrame({**base, "lordo": 0.02 + rumore, "base": 0.02 + rumore, "famiglia": "F12"})
    tempismo = pd.DataFrame({**base, "lordo": 0.01 + rumore, "base": 0.002, "famiglia": "F1"})
    feb = lambda t: t.assign(entrata=t["entrata"] + 31 * 1440, uscita=t["uscita"] + 31 * 1440)
    cand = {("M", "segue"): pd.concat([mercato, feb(mercato)]), ("T", "segue"): pd.concat([tempismo, feb(tempismo)])}
    _, scelte = meta2.scegli_eccesso(cand, L=1, K=5, primo=1, ultimo=1, n_mesi=3, min_trade=10, t_min=1.0)
    assert scelte[1] == [("T", "segue")]
