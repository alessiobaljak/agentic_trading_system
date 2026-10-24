"""I controlli dei prezzi, la rettifica, lo scarto e l'archivio, su casi costruiti a mano.
Nessuna chiamata di rete: Alpaca è finto."""
from datetime import date, datetime, timezone

import pandas as pd
import pytest

from stock.dati import alpaca, archivio, controlli, scarto


def giornaliere(righe, giorni):
    idx = pd.DatetimeIndex(giorni, tz="America/New_York").tz_convert("UTC")
    df = pd.DataFrame(righe, columns=["open", "high", "low", "close"], index=idx)
    df["volume"] = 1000
    return df


def cal(giorni, chiusura="16:00"):
    d = pd.to_datetime(pd.Index(giorni))
    return pd.DataFrame({"apertura": (d + pd.Timedelta("9h30min")).tz_localize("America/New_York"),
                         "chiusura": (d + pd.Timedelta(chiusura + ":00")).tz_localize("America/New_York")},
                        index=pd.Index(d.date))


def azioni(*righe):
    return pd.DataFrame(righe, columns=["data", "tipo", "rapporto", "importo"])


def test_barre_incoerenti():
    df = giornaliere([(10, 11, 9, 10), (10, 9.5, 9, 9.2), (0, 1, 0, 1)], ["2016-01-04", "2016-01-05", "2016-01-06"])
    tipi = [p["controllo"] for p in controlli.controlla_barre(df)]
    assert tipi.count("ohlc") == 1 and tipi.count("prezzo") == 1
    df2 = pd.concat([df.iloc[:1], df.iloc[:1]])
    assert "doppione" in [p["controllo"] for p in controlli.controlla_barre(df2)]


def test_buchi_e_giorni_chiusi():
    c = cal(["2016-01-04", "2016-01-05", "2016-01-06", "2016-01-07"])
    df = giornaliere([(1, 1, 1, 1)] * 4, ["2016-01-04", "2016-01-06", "2016-01-07", "2016-01-09"])
    p = controlli.controlla_giorni(df, c)
    assert [(x["controllo"], x["quando"]) for x in p] == [("buco", "2016-01-05"), ("giorno chiuso", "2016-01-09")]
    assert controlli.controlla_giorni(df.iloc[:0], c)[0]["controllo"] == "buco"


def test_minuti_con_chiusura_anticipata_e_ore_fuori_seduta():
    # 25 nov 2016 chiude alle 13:00: 210 minuti attesi
    c = pd.concat([cal(["2016-11-25"], "13:00"), cal(["2016-11-28"])])
    t1 = pd.date_range("2016-11-25 09:30", periods=210, freq="min", tz="America/New_York")
    fuori = pd.DatetimeIndex(["2016-11-25 08:00", "2016-11-25 14:00"], tz="America/New_York")
    t2 = pd.date_range("2016-11-28 09:30", periods=300, freq="min", tz="America/New_York")  # 300 su 390
    idx = t1.append(fuori).append(t2).sort_values().tz_convert("UTC")
    df = pd.DataFrame({"open": 1.0, "high": 1.0, "low": 1.0, "close": 1.0, "volume": 1}, index=idx)
    p, riep = controlli.controlla_minuti(df, c)
    assert riep == {"dentro": 510, "fuori": 2, "giorni": 2}
    assert [(x["controllo"], x["quando"]) for x in p] == [("minuti mancanti", "2016-11-28")]


def test_salto_senza_frazionamento_e_frazionamento_visto():
    giorni = ["2020-08-27", "2020-08-28", "2020-08-31", "2020-09-01"]
    df = giornaliere([(500, 500, 500, 500), (500, 500, 500, 500), (127, 130, 125, 129), (129, 129, 129, 60)], giorni)
    a = azioni((date(2020, 8, 31), "frazionamento", 4.0, 0.0))
    assert controlli.controlla_salti(df, a) == []
    # senza l'azione societaria, lo stesso salto è un problema
    p = controlli.controlla_salti(df, azioni())
    assert [x["quando"] for x in p] == ["2020-08-31"]
    # un frazionamento dichiarato che nei prezzi non c'è
    df_piatto = giornaliere([(500, 500, 500, 500)] * 4, giorni)
    assert controlli.controlla_salti(df_piatto, a)[0]["controllo"] == "frazionamento non visto"


def test_rettifica_calcolata_a_mano():
    giorni = ["2020-01-02", "2020-01-03", "2020-01-06", "2020-01-07"]
    raw = giornaliere([(100, 100, 100, 100), (100, 100, 100, 100), (49, 49, 49, 49), (25, 25, 25, 25)], giorni)
    a = azioni((date(2020, 1, 6), "dividendo", 1.0, 2.0), (date(2020, 1, 7), "frazionamento", 2.0, 0.0))
    # dividendo da 2 sul giorno 3: prima del 6 gennaio * (1 - 2/100) = 0,98; poi frazionamento 2:1 il 7: prima * 0,5
    f = controlli.rettifica(raw, a).to_list()
    assert f == pytest.approx([0.49, 0.49, 0.5, 1.0])
    assert controlli.rettifica(raw, a, dividendi=False).to_list() == pytest.approx([0.5, 0.5, 0.5, 1.0])
    # una rettifica «di Alpaca» coerente con la nostra passa; una che dimentica il dividendo no
    giusta = raw.copy()
    giusta["close"] = raw["close"] * pd.Series(f, index=raw.index)
    assert controlli.controlla_rettifica(raw, giusta, a) == []
    sbagliata = raw.copy()
    sbagliata["close"] = raw["close"] * pd.Series([0.5, 0.5, 0.5, 1.0], index=raw.index)
    p = controlli.controlla_rettifica(raw, sbagliata, a)
    assert len(p) == 1 and p[0]["quando"] == "2020-01-02 → 2020-01-03"


def test_cadenza_dividendi_trova_il_trimestre_mancante():
    trimestri = [date(2016, 3, 18), date(2016, 6, 17), date(2016, 9, 16), date(2016, 12, 16), date(2017, 3, 17)]
    a = azioni(*[(d, "dividendo", 1.0, 1.0) for d in trimestri])
    assert controlli.controlla_cadenza_dividendi(a) == []
    p = controlli.controlla_cadenza_dividendi(a.drop(index=2))
    assert [x["quando"] for x in p] == ["2016-06-17 → 2016-12-16"]


def test_scarto_misurato_sulle_fotografie_al_minuto():
    t = pd.DatetimeIndex(["2016-01-04 14:30:01", "2016-01-04 14:30:30", "2016-01-04 14:30:59",
                          "2016-01-04 14:31:10", "2016-01-04 14:32:00", "2016-01-04 14:32:30"], tz="UTC")
    q = pd.DataFrame({"bid": [99.99, 99.98, 100.00, 100.00, 0.0, 100.02],
                      "ask": [100.01, 100.02, 100.02, 99.99, 100.0, 100.04],
                      "bid_size": 1, "ask_size": 1}, index=t)
    m = scarto.misura(q)
    # minuto 14:30: ultima valida 100,00/100,02; 14:31: incrociata, tolta; 14:32: bid 0 tolta, poi 100,02/100,04
    assert m["fotografie"] == 2
    assert m["mediana"] == pytest.approx((0.02 / 100.01 + 0.02 / 100.03) / 2)
    assert scarto.misura(q.iloc[3:5])["fotografie"] == 0


def test_archivio_rifiuta_il_repository_e_rilegge(tmp_path):
    with pytest.raises(archivio.CartellaVietata):
        archivio.cartella_dati(archivio.RADICE_REPO / "stock" / "dati_scaricati")
    df = giornaliere([(1, 2, 0.5, 1.5)], ["2016-01-04"])
    archivio.salva(df, "SPY", "1Day_raw", tmp_path)
    letto = archivio.carica("SPY", "1Day_raw", tmp_path)
    pd.testing.assert_frame_equal(letto, df.rename_axis("t"), check_freq=False, check_dtype=False)
    a = azioni((date(2020, 8, 31), "frazionamento", 4.0, 0.0))
    archivio.salva(a, "SPY", "azioni", tmp_path)
    assert archivio.carica("SPY", "azioni", tmp_path)["data"].iloc[0] == date(2020, 8, 31)
    assert archivio.carica("QQQ", "1Day_raw", tmp_path) is None


class Risposta:
    def __init__(self, codice, corpo):
        self.status_code, self._corpo, self.text = codice, corpo, str(corpo)

    def json(self):
        return self._corpo


def test_alpaca_pagine_e_nessuna_chiave_nei_messaggi(monkeypatch):
    monkeypatch.setenv("ALPACA_API_KEY_ID", "CHIAVEFINTA")
    monkeypatch.setenv("ALPACA_API_SECRET_KEY", "SEGRETOFINTO")
    pagine = [
        {"bars": {"SPY": [{"t": "2016-01-04T05:00:00Z", "o": 1, "h": 2, "l": 0.5, "c": 1.5, "v": 10, "n": 3, "vw": 1.2}]},
         "next_page_token": "x"},
        {"bars": {"SPY": [{"t": "2016-01-05T05:00:00Z", "o": 1.5, "h": 2, "l": 1, "c": 1.8, "v": 10, "n": 3, "vw": 1.6}]},
         "next_page_token": None},
    ]
    chiamate = []

    def finto_get(url, headers, params, timeout):
        chiamate.append(dict(params))
        return Risposta(200, pagine[len(chiamate) - 1])
    monkeypatch.setattr(alpaca.requests, "get", finto_get)
    df = alpaca.barre("SPY", "1Day", datetime(2016, 1, 1, tzinfo=timezone.utc), datetime(2016, 1, 8, tzinfo=timezone.utc))
    assert list(df["close"]) == [1.5, 1.8]
    assert chiamate[1]["page_token"] == "x"

    monkeypatch.setattr(alpaca.requests, "get", lambda url, headers, params, timeout: Risposta(403, {"message": "no"}))
    with pytest.raises(alpaca.ErroreAlpaca) as e:
        alpaca.barre("SPY", "1Day", datetime(2016, 1, 1, tzinfo=timezone.utc), datetime(2016, 1, 8, tzinfo=timezone.utc))
    assert "CHIAVEFINTA" not in str(e.value) and "SEGRETOFINTO" not in str(e.value)


def test_alpaca_senza_chiavi(monkeypatch):
    monkeypatch.delenv("ALPACA_API_KEY_ID", raising=False)
    with pytest.raises(alpaca.ErroreAlpaca):
        alpaca._intestazioni()


def test_alpaca_fine_tirata_indietro_di_16_minuti():
    adesso = datetime.now(timezone.utc)
    fine = alpaca._fine_ammessa(adesso)
    assert abs((adesso - fine) - alpaca.RITARDO_PIANO_GRATUITO).total_seconds() < 5
    passato = datetime(2016, 1, 8, tzinfo=timezone.utc)
    assert alpaca._fine_ammessa(passato) == passato


def test_inizio_e_fine_alla_mezzanotte_di_new_york():
    from stock.dati.scarica import _utc
    assert _utc("2016-01-01") == datetime(2016, 1, 1, 5, tzinfo=timezone.utc)          # inverno: UTC-5
    assert _utc("2024-06-30", fine=True) == datetime(2024, 7, 1, 4, tzinfo=timezone.utc)  # estate: UTC-4


def test_dividendi_aggiunti_solo_dove_mancano():
    from stock.dati.integrazioni import DIVIDENDI_AGGIUNTI, azioni_complete
    a = azioni((date(2016, 6, 17), "dividendo", 1.0, 1.078))
    c = azioni_complete("SPY", a)
    assert date(2016, 3, 18) in set(c["data"]) and len(c) == 1 + len(DIVIDENDI_AGGIUNTI["SPY"])
    assert azioni_complete("QQQ", a) is a
    # se Alpaca un giorno lo avesse, non si raddoppia
    b = azioni((date(2016, 3, 18), "dividendo", 1.0, 1.05))
    assert (azioni_complete("SPY", b)["data"] == date(2016, 3, 18)).sum() == 1


def test_confronto_dividendi_riporta_gli_importi_divisi_per_i_frazionamenti():
    from stock.dati.integrazioni import confronta_dividendi
    # AAPL: 0,82 nell'agosto 2020 prima del 4 per 1 del 31 agosto; Yahoo scrive 0,205
    nostri = azioni((date(2020, 8, 7), "dividendo", 1.0, 0.82), (date(2020, 11, 6), "dividendo", 1.0, 0.205),
                    (date(2021, 2, 5), "dividendo", 1.0, 0.205))
    altri = {date(2020, 8, 7): 0.205, date(2020, 11, 6): 0.205, date(2021, 5, 7): 0.22}
    d = confronta_dividendi(nostri, altri, {date(2020, 8, 31): 4.0})
    assert [(str(x["data"]), x["tipo"]) for x in d] == [("2021-02-05", "manca a loro"), ("2021-05-07", "manca a noi")]
