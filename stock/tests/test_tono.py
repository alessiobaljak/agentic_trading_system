from datetime import UTC, datetime

import pandas as pd

from stock.strategie import tono


def test_il_voto():
    assert tono.voto("Acme Q1 EPS Beats Estimate, Raises Guidance") == 1
    assert tono.voto("Acme Misses on Sales; Analyst Downgrades") == -1
    assert tono.voto("Analyst Maintains Buy on Acme, Lowers Price Target") == 0
    assert tono.voto("Acme shares surge") == 0          # le parole del movimento del prezzo non contano
    assert tono.voto("") == 0


def _notizie(righe):
    return pd.DataFrame({"creata": pd.to_datetime([r[0] for r in righe], utc=True, format="ISO8601"), "simboli": [r[1] for r in righe],
                         "testo": [r[2] for r in righe]})


def test_il_tono_del_mese_usa_solo_le_notizie_dentro_i_confini_e_dell_azienda():
    confini = [datetime(2016, 1, 1, tzinfo=UTC), datetime(2016, 2, 1, tzinfo=UTC), datetime(2016, 3, 1, tzinfo=UTC)]
    n = _notizie([("2016-01-05", ["AAA"], "beats"), ("2016-01-06", ["AAA"], "beats"), ("2016-01-07", ["AAA", "BBB"], "misses"),
                  ("2016-01-08", ["AAA", "B", "C", "D"], "fraud"),        # cita 4 simboli: non conta
                  ("2016-02-01T00:00:00", ["AAA"], "misses"),            # sul confine: appartiene al primo mese
                  ("2016-02-01T00:00:01", ["AAA"], "fraud"),             # dopo il confine: secondo mese
                  ("2016-03-02", ["AAA"], "record"), ("2015-12-31", ["AAA"], "record")])
    t = tono.toni(n, confini)
    assert len(t) == 2
    assert t[0]["AAA"] == (0.0, 4)                 # +1 +1 −1 −1
    assert "BBB" not in t[0]                       # una sola notizia: meno di tre
    assert t[1] == {}                              # una sola notizia nel secondo mese


def test_la_scelta():
    t = {f"S{i:02d}": (1.0 - i / 100, 3) for i in range(30)}
    t["S05"] = (1.0, 9)                            # pari al primo, più notizie: passa davanti
    t["FUORI"] = (1.0, 50)
    ammessi = {s for s in t if s != "FUORI"}
    assert tono.scegli(t, ammessi) == ["S05", "S00", "S01", "S02", "S03", "S04"]       # il 20% di 30
    assert tono.scegli(t, set(list(ammessi)[:24])) == []                              # meno di 25: fuori
    grande = {f"T{i:03d}": (0.5, 3) for i in range(400)}
    assert len(tono.scegli(grande, set(grande))) == 50                                # al massimo 50


def test_i_fondi():
    assert tono.e_un_fondo("iShares Russell 2000 ETF") and tono.e_un_fondo("Some Growth Fund")
    assert not tono.e_un_fondo("Apple Inc. Common Stock") and not tono.e_un_fondo("")


def test_la_scelta_dal_basso_e_la_strategia_al_contrario():
    t = {f"S{i:02d}": (i / 100, 3) for i in range(30)}
    t["S10"] = (0.0, 9)                            # pari al più basso, più notizie: passa davanti
    assert tono.scegli(t, set(t), piu_bassi=True) == ["S10", "S00", "S01", "S02", "S03", "S04"]
    assert tono.scegli(t, set(t)) == ["S29", "S28", "S27", "S26", "S25", "S24"]
