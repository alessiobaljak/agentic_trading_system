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


def test_rimbalzo_compra_i_peggiori_della_settimana_e_usa_l_elenco_del_mese_dopo():
    from datetime import date as D
    from stock.strategie.rimbalzo import QUANTI, strategia_rimbalzo
    giorni = list(pd.bdate_range("2020-01-24", "2020-02-07").date)      # ven 24 gen → ven 7 feb
    simboli = ["A", "B", "C", "D", "E"]
    cadute = {"A": -0.10, "B": -0.05, "C": 0.0, "D": 0.05, "E": -0.20}
    barre_ = {}
    rett = {}
    for s in simboli:
        p = [100.0] * 5 + [100.0 * (1 + cadute[s])] * 6    # il ven 31 gen (sesta chiusura) cambia
        df = pd.DataFrame({"open": p, "high": p, "low": p, "close": p},
                          index=pd.DatetimeIndex([str(g) for g in giorni], tz="America/New_York").tz_convert("UTC"))
        barre_[s] = df
        rett[s] = pd.Series(p, index=pd.Index(giorni))
    # elenco di gennaio senza E, di febbraio con E: la decisione del 31 gennaio esegue a febbraio → vale febbraio
    universo = pd.DataFrame([{"mese": "2020-01", "posizione": i + 1, "simbolo": s} for i, s in enumerate("ABCD")]
                            + [{"mese": "2020-02", "posizione": i + 1, "simbolo": s} for i, s in enumerate("ABCDE")])
    r = simula_conto(barre_, strategia_rimbalzo(universo, giorni, rett), Costi())
    primi = r.esecuzioni[r.esecuzioni.giorno == D(2020, 2, 3)]
    assert sorted(primi["simbolo"]) == ["A", "B", "E"] and QUANTI == 3
    # il venerdì 7 febbraio i rendimenti di 5 sedute sono 0 per tutti: si sceglie per ordine stabile, nessun ordine dopo l'ultimo giorno
    assert r.esecuzioni["giorno"].max() == D(2020, 2, 3)


def test_tendenza_entra_se_l_anno_e_in_guadagno_ed_esce_se_no():
    from stock.strategie import tendenza
    giorni = list(pd.bdate_range("2019-01-01", periods=300).date)
    p = [100.0 + i * 0.1 for i in range(270)] + [80.0] * 30            # sale per 270 sedute, poi crolla
    df = pd.DataFrame({"open": p, "high": p, "low": p, "close": p},
                      index=pd.DatetimeIndex([str(g) for g in giorni], tz="America/New_York").tz_convert("UTC"))
    rett = pd.Series(p, index=pd.Index(giorni))
    r = simula_conto({"X": df}, tendenza.strategia("X", giorni, rett), Costi())
    e = r.esecuzioni
    # prima decisione possibile: fine del primo mese con 253 chiusure; si compra; poi, dopo il crollo, alla fine del mese si vende
    assert e["quantita"].iloc[0] > 0 and e["quantita"].iloc[-1] < 0
    primo = e["giorno"].iloc[0]
    assert giorni.index(primo) >= tendenza.SEDUTE


def test_cambio_del_mese_entra_al_penultimo_ed_esce_al_quarto():
    from datetime import date as D
    from stock.strategie.calendario import posizione_nel_mese, strategia_cambio_del_mese
    giorni = list(pd.bdate_range("2020-01-02", "2020-02-14").date)
    assert posizione_nel_mese(giorni)[D(2020, 1, 31)] == (22, 22)
    p = [100.0] * len(giorni)
    df = pd.DataFrame({"open": p, "high": p, "low": p, "close": p},
                      index=pd.DatetimeIndex([str(g) for g in giorni], tz="America/New_York").tz_convert("UTC"))
    r = simula_conto({"X": df}, strategia_cambio_del_mese("X", giorni), Costi())
    e = r.esecuzioni
    # gennaio 2020 (giorni feriali): penultimo 30 gennaio; febbraio: quarto giorno 6 febbraio
    assert list(e["giorno"])[:2] == [D(2020, 1, 30), D(2020, 2, 6)]   # (il calendario tagliato al 14 febbraio fa poi un altro giro)
    assert e["quantita"].iloc[0] > 0 and e["quantita"].iloc[1] < 0


def test_usciti_dall_indice_compra_il_giorno_dell_uscita_e_vende_dopo_20_sedute():
    from datetime import date as D
    from stock.strategie import usciti
    giorni = list(pd.bdate_range("2020-01-02", periods=40).date)
    comp = [(D(2019, 12, 1), frozenset({"A", "B"})), (D(2020, 1, 6), frozenset({"B"}))]   # A esce il 6 gennaio
    ev = usciti.eventi_di_uscita(comp, D(2020, 1, 1), D(2020, 12, 31))
    assert ev == [(D(2020, 1, 6), "A")]
    p = [100.0] * 40
    df = pd.DataFrame({"open": p, "high": p, "low": p, "close": p},
                      index=pd.DatetimeIndex([str(g) for g in giorni], tz="America/New_York").tz_convert("UTC"))
    r = simula_conto({"A": df}, usciti.strategia(ev, giorni), Costi())
    e = r.esecuzioni
    assert list(e["giorno"]) == [D(2020, 1, 6), giorni[giorni.index(D(2020, 1, 6)) + 20]]
    assert e["quantita"].iloc[0] == 100      # il 10% di 100'000 a 100 dollari


def test_raggruppamento_paga_la_frazione_in_contanti():
    # 1 nuova ogni 5 (rapporto 0,2): 908 azioni diventano 181,6 → 181 azioni e 0,6 pagata in contanti
    a = barre([(10, 10, 10, 10), (10, 10, 10, 10), (50, 50, 50, 50), (50, 50, 50, 50)], G, frazionamento=[1, 1, 0.2, 1])
    r = simula_conto({"A": a}, al_giorno({0: [("A", Ordine(908, "mercato"))], 2: [("A", Ordine(-181, "mercato"))]}), Costi())
    assert list(r.esecuzioni["quantita"]) == [908, -181]
    assert r.valore.iloc[-1] == pytest.approx(100_000)


def test_dopo_i_bilanci_compra_solo_dopo_una_reazione_migliore_dell_indice():
    from datetime import date as D
    from stock.strategie import dopo_bilanci as db
    giorni = list(pd.bdate_range("2020-01-02", periods=40).date)
    # comunicato il 9 gennaio: prima = 8, dopo = 10; decisione il 10, ingresso il 13
    pA = [100.0] * 6 + [110.0] * 34          # A sale del 10% il 10 gennaio (indice +0)
    pB = [100.0] * 6 + [99.0] * 34           # B scende
    idx = pd.Series([100.0] * 40, index=pd.Index(giorni))
    barre_ = {s: pd.DataFrame({"open": p, "high": p, "low": p, "close": p},
                              index=pd.DatetimeIndex([str(g) for g in giorni], tz="America/New_York").tz_convert("UTC"))
              for s, p in (("A", pA), ("B", pB))}
    rett = {s: pd.Series(p, index=pd.Index(giorni)) for s, p in (("A", pA), ("B", pB))}
    universo = pd.DataFrame([{"mese": "2020-01", "posizione": 1, "simbolo": "A"}, {"mese": "2020-01", "posizione": 2, "simbolo": "B"},
                             {"mese": "2020-02", "posizione": 1, "simbolo": "A"}, {"mese": "2020-02", "posizione": 2, "simbolo": "B"}])
    com = {"A": [D(2020, 1, 9)], "B": [D(2020, 1, 9)]}
    assert D(2020, 1, 10) in db.piano(com, giorni)
    r = simula_conto(barre_, db.strategia(com, universo, giorni, rett, idx), Costi())
    e = r.esecuzioni
    assert list(e["simbolo"]) == ["A", "A"]
    assert list(e["giorno"]) == [D(2020, 1, 13), giorni[giorni.index(D(2020, 1, 13)) + 20]]


def test_rimbalzo_sull_indice_usa_i_membri_del_giorno():
    from datetime import date as D
    from stock.strategie.rimbalzo import strategia_rimbalzo_indice
    giorni = list(pd.bdate_range("2020-01-24", "2020-02-07").date)
    cadute = {"A": -0.10, "B": -0.05, "C": 0.0, "Z": -0.50}
    barre_, rett = {}, {}
    for s, c in cadute.items():
        p = [100.0] * 5 + [100.0 * (1 + c)] * 6
        barre_[s] = pd.DataFrame({"open": p, "high": p, "low": p, "close": p},
                                 index=pd.DatetimeIndex([str(g) for g in giorni], tz="America/New_York").tz_convert("UTC"))
        rett[s] = pd.Series(p, index=pd.Index(giorni))
    membri = lambda g: ["A", "B", "C"]          # Z non è nell'indice: non si compra anche se è caduto di più  # noqa: E731
    r = simula_conto(barre_, strategia_rimbalzo_indice(membri, giorni, rett, quanti=2), Costi())
    assert sorted(r.esecuzioni[r.esecuzioni.giorno == D(2020, 2, 3)]["simbolo"]) == ["A", "B"]


def test_classifica_mensile_sceglie_i_meno_nervosi_e_i_piu_saliti():
    import numpy as np
    from stock.strategie import fattori
    giorni = list(pd.bdate_range("2019-01-01", periods=300).date)
    serie = {"CALMO": 100 * np.cumprod(np.full(300, 1.0005)),                      # sale piano, senza scosse
             "NERVOSO": 100 * np.where(np.arange(300) % 2 == 0, 1.0, 1.05),        # oscilla del 5%, non sale
             "SALE": 100 * np.cumprod(np.r_[np.full(150, 1.004), np.full(150, 0.999)])}   # sale molto, poi scende piano
    barre_ = {s: pd.DataFrame({"open": p, "high": p, "low": p, "close": p},
                              index=pd.DatetimeIndex([str(g) for g in giorni], tz="America/New_York").tz_convert("UTC"))
              for s, p in serie.items()}
    rett = {s: pd.Series(p, index=pd.Index(giorni)) for s, p in serie.items()}
    membri = lambda g: list(serie)  # noqa: E731
    r = simula_conto(barre_, fattori.strategia_classifica(membri, giorni, rett, fattori.volatilita, quanti=1), Costi(),
                     leva_massima=2)
    assert set(r.esecuzioni["simbolo"]) == {"CALMO"}
    r = simula_conto(barre_, fattori.strategia_classifica(membri, giorni, rett, fattori.momento, quanti=1, i_piu_bassi=False),
                     Costi(), leva_massima=2)
    assert set(r.esecuzioni["simbolo"]) == {"SALE"}


def test_calma_investe_di_piu_quando_il_mercato_e_calmo():
    import numpy as np
    from stock.strategie import tendenza
    giorni = list(pd.bdate_range("2019-01-01", periods=120).date)
    # 60 sedute calme (0,5% al giorno di oscillazione), poi 60 agitate (4%)
    r = np.r_[np.where(np.arange(60) % 2 == 0, 0.005, -0.005), np.where(np.arange(60) % 2 == 0, 0.04, -0.04)]
    p = 100 * np.cumprod(1 + r)
    df = pd.DataFrame({"open": p, "high": p, "low": p, "close": p},
                      index=pd.DatetimeIndex([str(g) for g in giorni], tz="America/New_York").tz_convert("UTC"))
    rett = pd.Series(p, index=pd.Index(giorni))
    res = simula_conto({"X": df}, tendenza.strategia_calma("X", giorni, rett), Costi(interesse_debito_annuo=0.06), leva_massima=1.5)
    e = res.esecuzioni
    # prima si compra con la leva massima (calma: quota tagliata a 1,5), poi con l'agitazione si vende
    assert e["quantita"].iloc[0] > 0 and e["quantita"].iloc[0] * e["prezzo"].iloc[0] > 140_000
    assert (e["quantita"] < 0).any()


def test_ampiezza_conta_solo_i_membri_e_solo_il_passato():
    from stock.strategie import ampiezza as amp
    giorni = list(pd.bdate_range("2019-01-01", periods=260).date)
    sale = pd.Series([100 + i for i in range(260)], index=pd.Index(giorni), dtype=float)
    scende = pd.Series([400 - i for i in range(260)], index=pd.Index(giorni), dtype=float)
    rett = {"A": sale, "B": scende, "C": sale}
    membri = lambda g: ["A", "B"]  # noqa: E731
    a = amp.serie_ampiezza(rett, membri, giorni)
    assert a.index[0] == giorni[amp.SEDUTE - 1] and a.iloc[-1] == 0.5          # C non è nell'indice: non conta
    # tagliare il futuro non cambia il passato
    corto = amp.serie_ampiezza({k: v.iloc[:230] for k, v in rett.items()}, membri, giorni[:230])
    assert (corto == a.loc[corto.index]).all()
