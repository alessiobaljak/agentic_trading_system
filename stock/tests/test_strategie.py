"""La strategia dell'ultima mezz'ora e l'asticella, su casi costruiti a mano."""
import math

import numpy as np
import pandas as pd
import pytest

from stock.simulatore import asticella
from stock.simulatore.costi import Costi
from stock.simulatore.motore import simula
from stock.strategie import ultima_mezzora as um

NY = "America/New_York"


def calendario(giorni, chiusura="16:00"):
    d = pd.to_datetime(pd.Index(giorni))
    return pd.DataFrame({"apertura": (d + pd.Timedelta("9h30min")).tz_localize(NY),
                         "chiusura": (d + pd.Timedelta(chiusura + ":00")).tz_localize(NY)}, index=pd.Index(d.date))


def giornata(giorno, prezzi, chiusura="16:00"):
    """Barre al minuto di una seduta; `prezzi` = funzione minuto (0 = apertura) -> prezzo."""
    ap = pd.Timestamp(f"{giorno} 09:30", tz=NY)
    n = int((pd.Timestamp(f"{giorno} {chiusura}", tz=NY) - ap).total_seconds() // 60)
    idx = pd.date_range(ap, periods=n, freq="min")
    p = np.array([prezzi(i) for i in range(n)], dtype=float)
    return pd.DataFrame({"open": p, "high": p, "low": p, "close": p, "volume": 1}, index=idx.tz_convert("UTC"))


def test_compra_se_la_giornata_sale_e_chiude_prima_della_chiusura():
    # ieri chiude a 100; oggi sale fino a 101 alle 15:30, poi 102 nell'ultima mezz'ora
    ieri = giornata("2020-01-02", lambda i: 100.0)
    oggi = giornata("2020-01-03", lambda i: 101.0 if i < 360 else 102.0)
    b = pd.concat([ieri, oggi])
    cal = calendario(["2020-01-02", "2020-01-03"])
    seg = um.prepara(b, cal, set())
    r = simula(b, um.strategia(seg), Costi(), capitale=10_000)
    e = r.esecuzioni
    assert list(e["etichetta"]) == ["ingresso", "uscita"]
    t = e["t"].dt.tz_convert(NY)
    assert t.iloc[0].strftime("%H:%M") == "15:30" and t.iloc[1].strftime("%H:%M") == "15:59"
    # 98% di 10000 / 101 = 97 azioni; comprate a 102 (apertura delle 15:30) e vendute a 102: zero
    assert e["quantita"].iloc[0] == 97
    assert r.valore.iloc[-1] == pytest.approx(10_000)


def test_vende_allo_scoperto_se_la_giornata_scende_e_rispetta_la_chiusura_anticipata():
    ieri = giornata("2016-11-23", lambda i: 100.0)
    # 25 novembre: chiude alle 13:00 (210 minuti); segnale alla barra delle 12:29
    oggi = giornata("2016-11-25", lambda i: 99.0 if i < 180 else 98.0, chiusura="13:00")
    b = pd.concat([ieri, oggi])
    cal = calendario(["2016-11-23"]).pipe(lambda c: pd.concat([c, calendario(["2016-11-25"], "13:00")]))
    r = simula(b, um.strategia(um.prepara(b, cal, set())), Costi(), capitale=10_000)
    e = r.esecuzioni
    assert e["quantita"].iloc[0] < 0
    assert e["t"].dt.tz_convert(NY).iloc[0].strftime("%H:%M") == "12:30"
    assert e["t"].dt.tz_convert(NY).iloc[1].strftime("%H:%M") == "12:59"


def test_giorno_escluso_e_barra_mancante_non_si_opera():
    ieri = giornata("2020-01-02", lambda i: 100.0)
    oggi = giornata("2020-01-03", lambda i: 101.0)
    cal = calendario(["2020-01-02", "2020-01-03"])
    b = pd.concat([ieri, oggi])
    assert np.isnan(um.prepara(b, cal, {pd.Timestamp("2020-01-03").date()})["direzione"]).all()
    senza = b.drop(index=pd.Timestamp("2020-01-03 15:29", tz=NY).tz_convert("UTC"))
    assert np.isnan(um.prepara(senza, cal, set())["direzione"]).all()


def test_il_segnale_non_usa_il_futuro():
    rng = np.random.default_rng(0)
    giorni = pd.bdate_range("2020-01-06", periods=5)
    b = pd.concat([giornata(str(d.date()), lambda i: 100 + rng.normal()) for d in giorni])
    cal = calendario([str(d.date()) for d in giorni])
    tutto = um.prepara(b, cal, set())
    for taglio in (500, 1000, 1500):
        parte = um.prepara(b.iloc[:taglio], cal, set())
        np.testing.assert_array_equal(parte["direzione"][: taglio - 400], tutto["direzione"][: taglio - 400])


def test_solo_seduta():
    ieri = giornata("2020-01-02", lambda i: 100.0)
    fuori = pd.DataFrame({"open": 1.0, "high": 1.0, "low": 1.0, "close": 1.0, "volume": 1},
                         index=pd.DatetimeIndex(["2020-01-02 08:00", "2020-01-02 16:00"], tz=NY).tz_convert("UTC"))
    b = pd.concat([ieri, fuori]).sort_index()
    assert len(um.solo_seduta(b, calendario(["2020-01-02"]))) == 390


def test_asticella():
    # con un solo gruppo la soglia è zero
    assert asticella.soglia_per_caso(1, 0.01) == 0.0
    # più prove, soglia più alta
    assert asticella.soglia_per_caso(10, 0.01) > asticella.soglia_per_caso(2, 0.01) > 0
    rng = np.random.default_rng(1)
    buona = pd.Series(rng.normal(0.002, 0.01, 2000))
    nulla = pd.Series(rng.normal(0.0, 0.01, 2000))
    assert asticella.sharpe_probabilistico(buona, 0.0) > 0.99
    assert asticella.sharpe_probabilistico(nulla, 0.05) < 0.05
    # due serie quasi uguali fanno un gruppo solo; una indipendente un altro
    simile = buona + rng.normal(0, 0.001, 2000)
    g = asticella.gruppi({"a": buona, "b": simile, "c": nulla})
    assert sorted(map(sorted, g)) == [["a", "b"], ["c"]]
    r = asticella.sharpe_corretto(buona, {"a": buona, "b": simile, "c": nulla})
    assert r["gruppi"] == 2 and r["varianza"] == pytest.approx(1 / 2000)


def _giorni_piatti(n, prezzo=100.0):
    giorni = pd.bdate_range("2020-01-06", periods=n)
    parti = []
    for d in giorni:
        g = giornata(str(d.date()), lambda i: prezzo)
        g["vwap"] = prezzo
        parti.append(g)
    return giorni, parti


def test_zona_di_rumore_compra_sopra_il_limite_ed_esce_a_fine_giornata():
    from stock.strategie import zona_di_rumore as zr
    giorni, parti = _giorni_piatti(15)
    # 14 giorni con oscillazione dell'1% fissa dopo l'apertura: σ = 1% per ogni minuto dopo il primo
    for p in parti[:14]:
        p.loc[p.index[1:], ["open", "high", "low", "close", "vwap"]] = 101.0
    # oggi apre a 100 (ieri ha chiuso a 101) e sale a 103 dalle 9:45
    oggi = parti[14]
    oggi.loc[oggi.index[15:], ["open", "high", "low", "close", "vwap"]] = 103.0
    b = pd.concat(parti)
    cal = calendario([str(d.date()) for d in giorni])
    seg = zr.prepara(b, cal, set())
    i = np.where(seg["decisione"])[0][0]
    # limite alto alle 10:00 = max(100, 101) × 1,01 = 102,01
    assert seg["alto"][i] == pytest.approx(102.01)
    assert seg["basso"][i] == pytest.approx(100 * 0.99)
    r = simula(b, zr.strategia(seg), Costi(), capitale=10_000)
    e = r.esecuzioni
    assert list(e["etichetta"]) == ["decisione", "fine giornata"]
    assert e["t"].dt.tz_convert(NY).iloc[0].strftime("%H:%M") == "10:00"
    assert e["quantita"].iloc[0] == math.floor(0.98 * 10_000 / 103)


def test_zona_di_rumore_non_usa_il_futuro_e_vuole_14_giorni():
    from stock.strategie import zona_di_rumore as zr
    rng = np.random.default_rng(2)
    giorni = pd.bdate_range("2020-01-06", periods=20)
    parti = []
    for d in giorni:
        g = giornata(str(d.date()), lambda i: 100 + rng.normal())
        g["vwap"] = g["close"]
        parti.append(g)
    b = pd.concat(parti)
    cal = calendario([str(d.date()) for d in giorni])
    tutto = zr.prepara(b, cal, set())
    # i primi 14 giorni non decidono
    assert not tutto["decisione"][: 14 * 390].any() and tutto["decisione"][14 * 390:].any()
    # tagliando il futuro, tutti i livelli fino alla barra del taglio restano uguali (anche nel giorno tagliato)
    for taglio in (17 * 390 + 200, 18 * 390 + 31, 19 * 390 + 360):
        parte = zr.prepara(b.iloc[:taglio], cal, set())
        fino = (taglio // 390) * 390 if taglio % 390 < 389 else taglio
        for k in ("alto", "basso", "vwap"):
            np.testing.assert_array_equal(parte[k][:fino], tutto[k][:fino])
        np.testing.assert_array_equal(parte["decisione"][:fino], tutto["decisione"][:fino])
        # nel giorno tagliato i valori calcolati (se ce ne sono) coincidono con quelli veri
        oggi = slice(fino, taglio)
        ok = ~np.isnan(parte["alto"][oggi])
        np.testing.assert_array_equal(parte["alto"][oggi][ok], tutto["alto"][oggi][ok])
        np.testing.assert_array_equal(parte["vwap"][oggi][ok], tutto["vwap"][oggi][ok])


def test_notte_compra_alla_sera_vende_alla_mattina_e_incassa_il_dividendo():
    from stock.strategie import notte
    g1 = giornata("2020-01-02", lambda i: 100.0 if i < 389 else 101.0)     # ultima barra (15:59) apre a 101
    g2 = giornata("2020-01-03", lambda i: 103.0)                             # mattina dopo: 103
    b = pd.concat([g1, g2])
    cal = calendario(["2020-01-02", "2020-01-03"])
    az = pd.DataFrame([{"data": pd.Timestamp("2020-01-03").date(), "tipo": "dividendo", "rapporto": 1.0, "importo": 0.5}])
    b = notte.con_dividendi(b, az)
    assert b["dividendo"].sum() == 0.5 and b["dividendo"].iloc[390] == 0.5
    r = simula(b, notte.strategia(notte.prepara(b, cal, set())), Costi(), capitale=10_000)
    e = r.esecuzioni
    assert list(e["etichetta"]) == ["sera", "mattina", "sera"]   # la seconda sera ricompra
    assert e["t"].dt.tz_convert(NY).iloc[0].strftime("%H:%M") == "15:59" and e["prezzo"].iloc[0] == 101
    assert e["t"].dt.tz_convert(NY).iloc[1].strftime("%Y-%m-%d %H:%M") == "2020-01-03 09:30"
    q = math.floor(0.98 * 10_000 / 100)
    assert r.valore.iloc[-1] == pytest.approx(10_000 + q * (103 - 101) + q * 0.5)
