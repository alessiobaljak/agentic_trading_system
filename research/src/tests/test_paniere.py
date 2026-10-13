"""La serie di paniere della seconda edizione (research/src/paniere.py): allineamento, rendimenti, classifica,
giorni forti; soprattutto la CAUSALITA' (ogni valore al giorno t usa solo chiusure fino a t)."""
import numpy as np
import pytest

from research.src import paniere
from research.src.motore import Candela

G = paniere.GIORNO_MS


def _c(giorno: int, close: float) -> Candela:
    return Candela(ts=giorno * G, open=close, high=close, low=close, close=close, volume=1.0, close_ts=giorno * G + G - 1)


def _serie(simbolo_chiusure):
    return {s: [_c(g, c) for g, c in enumerate(chiusure, start=100) if c is not None] for s, chiusure in simbolo_chiusure.items()}


def test_allinea_giorni_calendario_comune_e_buchi():
    cand = _serie({"B": [1, 2, 3, 4], "A": [10, None, 30]})
    giorni, simboli, chiusure = paniere.allinea_giorni(cand)
    assert simboli == ("A", "B") and len(giorni) == 4 and giorni[0] == 100 * G
    assert chiusure[:, 1].tolist() == [1, 2, 3, 4]
    assert chiusure[0, 0] == 10 and np.isnan(chiusure[1, 0]) and chiusure[2, 0] == 30 and np.isnan(chiusure[3, 0])


def test_allinea_giorni_rifiuta_candele_non_giornaliere_e_doppioni():
    with pytest.raises(ValueError):
        paniere.allinea_giorni({"A": [Candela(ts=G + 1, open=1, high=1, low=1, close=1, volume=1, close_ts=2 * G)]})
    with pytest.raises(ValueError):
        paniere.allinea_giorni({"A": [_c(1, 1.0), _c(1, 2.0)]})


def test_rendimento_n_giorni_e_classifica():
    cand = _serie({"A": [100, 110, 121, 133.1], "B": [100, 90, 81, 72.9], "C": [100, 100, None, 100]})
    giorni, simboli, chiusure = paniere.allinea_giorni(cand)
    rend = paniere.rendimento_n_giorni(chiusure, 1)
    assert np.isnan(rend[0]).all()
    assert rend[1, 0] == pytest.approx(0.10) and rend[1, 1] == pytest.approx(-0.10) and rend[1, 2] == pytest.approx(0.0)
    assert np.isnan(rend[2, 2]) and np.isnan(rend[3, 2])   # C manca il giorno 2: ne' il 2 ne' il 3
    rango, n = paniere.classifica(rend, simboli)
    assert n.tolist() == [0, 3, 2, 2]
    assert rango[1].tolist() == [1, 3, 2] and rango[2, 0] == 1 and rango[2, 1] == 2 and np.isnan(rango[2, 2])


def test_classifica_parita_rotta_dall_ordine_alfabetico():
    rend = np.array([[0.1, 0.1, 0.05]])
    rango, n = paniere.classifica(rend, ["ZZZ", "AAA", "MMM"])
    assert rango[0].tolist() == [2, 1, 3] and n[0] == 3


def test_serie_paniere_e_causale():
    rng = np.random.default_rng(0)
    base = {s: list(100 * np.cumprod(1 + rng.normal(0, 0.03, 80))) for s in ("A", "B", "C", "D")}
    sp = paniere.serie_paniere(_serie(base), n_giorni=5, storia_minima=10)
    # cambio il futuro (giorni >= 50): niente cambia prima del giorno 50
    base2 = {s: v[:50] + list(np.array(v[50:]) * 3.0) for s, v in base.items()}
    sp2 = paniere.serie_paniere(_serie(base2), n_giorni=5, storia_minima=10)
    for s in base:
        assert np.array_equal(sp["rango"][s][:50], sp2["rango"][s][:50], equal_nan=True)
        assert np.allclose(sp["rendimento"][s][:50], sp2["rendimento"][s][:50], equal_nan=True)
    assert np.array_equal(sp["n_monete"][:50], sp2["n_monete"][:50])
    # storia minima: nei primi 9 giorni nessuna classifica
    assert sp["n_monete"][:9].tolist() == [0] * 9 and sp["n_monete"][10] == 4
    assert sp["indice"][int(sp["giorni"][7])] == 7


def test_giorni_forti_usa_solo_i_giorni_precedenti():
    r = np.zeros(100)
    r[30:90] = 0.01
    r[95] = 0.5                    # un giorno enorme
    dev = paniere.deviazione_mobile(r, 60, 40)
    assert np.isnan(dev[:60]).all() and dev[95] == pytest.approx(np.std(r[35:95], ddof=1))
    forti = paniere.giorni_forti(r, 2.0, 60, 40)
    assert forti[95] == 1 and forti[96] == 0
    # il giorno 95 non entra nella sua deviazione: cambiarlo non cambia dev[95]
    r2 = r.copy(); r2[95] = 5.0
    assert paniere.deviazione_mobile(r2, 60, 40)[95] == dev[95]
    r3 = r.copy(); r3[95] = -0.5
    assert paniere.giorni_forti(r3, 2.0, 60, 40)[95] == -1
