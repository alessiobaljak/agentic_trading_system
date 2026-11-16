"""Le parti nuove della prova 36: la notte di borsa, la soglia, il primo istante, l'ingresso, l'uscita, la scelta, il conto."""
from datetime import date

import pandas as pd

from stock.dati import depositi_dirigenti
from stock.prove import p036

CAL = [date(2024, 3, 1), date(2024, 3, 4), date(2024, 3, 5), date(2024, 3, 6)]       # venerdì, lunedì, martedì, mercoledì


def ny(testo: str) -> pd.Timestamp:
    return pd.Timestamp(testo, tz="America/New_York").tz_convert("UTC")


def test_notte_di_borsa():
    assert p036.notte(ny("2024-03-04 11:00"), CAL) == date(2024, 3, 4)
    assert p036.notte(ny("2024-03-04 16:00"), CAL) == date(2024, 3, 4)
    assert p036.notte(ny("2024-03-04 16:01"), CAL) == date(2024, 3, 5)
    assert p036.notte(ny("2024-03-02 10:00"), CAL) == date(2024, 3, 4)             # sabato
    assert p036.notte(ny("2024-03-01 17:00"), CAL) == date(2024, 3, 4)             # venerdì sera


def test_segnali_soglia_sommata_nella_notte():
    e = pd.DataFrame({"numero": ["a", "b", "c", "d", "e"], "simbolo": ["X", "X", "X", "Y", "X"],
                      "valore": [60_000.0, 50_000.0, 500_000.0, 90_000.0, 200_000.0],
                      "accettato": [ny("2024-03-04 17:00"), ny("2024-03-04 18:00"), ny("2024-03-04 19:00"), ny("2024-03-04 17:30"),
                                    ny("2024-03-05 17:00")]})
    s = p036.segnali(e, CAL)
    assert list(s["numero"]) == ["b", "e"]          # b porta X a 110'000 (c nella stessa notte non conta); Y sotto la soglia


def test_primo_istante():
    g, t = p036.primo_istante(ny("2024-03-04 14:03:27"), 2, CAL)
    assert g == date(2024, 3, 4) and t == ny("2024-03-04 14:06")
    g, t = p036.primo_istante(ny("2024-03-04 14:03:00"), 2, CAL)
    assert t == ny("2024-03-04 14:05")
    g, t = p036.primo_istante(ny("2024-03-04 21:10"), 2, CAL)                        # dopo le 19:59: le 4:00 del giorno dopo
    assert g == date(2024, 3, 5) and t == ny("2024-03-05 04:00")
    g, t = p036.primo_istante(ny("2024-03-05 01:00"), 2, CAL)                        # prima delle 4:00: le 4:00 dello stesso giorno
    assert g == date(2024, 3, 5) and t == ny("2024-03-05 04:00")
    g, t = p036.primo_istante(ny("2024-03-02 12:00"), 2, CAL)                        # sabato
    assert g == date(2024, 3, 4)


def test_cerca_ingresso_e_uscita():
    i = pd.DatetimeIndex([ny("2024-03-04 17:01"), ny("2024-03-04 17:09"), ny("2024-03-04 19:59")])
    b = pd.DataFrame({"open": [10.0, 10.5, 11.0]}, index=i)
    assert p036.cerca_ingresso(b, ny("2024-03-04 17:02")) == (ny("2024-03-04 17:09"), 10.5)
    assert p036.cerca_ingresso(b, ny("2024-03-04 19:59"))[1] == 11.0
    assert p036.cerca_ingresso(b.iloc[:2], ny("2024-03-04 17:10")) is None
    assert p036.giorno_d_uscita(ny("2024-03-04 17:09"), CAL) == date(2024, 3, 5)
    assert p036.giorno_d_uscita(ny("2024-03-05 09:29"), CAL) == date(2024, 3, 5)     # prima dell'apertura: esce all'apertura di oggi
    assert p036.giorno_d_uscita(ny("2024-03-05 09:30"), CAL) == date(2024, 3, 6)
    assert p036.fascia(ny("2024-03-05 09:29")) == "prima dell'apertura" and p036.fascia(ny("2024-03-05 16:00")) == "dopo la chiusura"


def op(simbolo, t, g_in, g_out, p_in=100.0, p_out=101.0):
    return p036.Operazione(simbolo, t, t, g_in, p_in, 1.0, g_out, p_out, 1.0, 0.002, 0.01)


def test_scelta_al_massimo_dieci_e_un_titolo_alla_volta():
    t = ny("2024-03-04 17:00")
    ops = [op(f"S{k}", t + pd.Timedelta(minutes=k), date(2024, 3, 4), date(2024, 3, 5)) for k in range(12)]
    ops.append(op("S0", t + pd.Timedelta(minutes=30), date(2024, 3, 4), date(2024, 3, 5)))
    ops.append(op("S11", ny("2024-03-05 10:00"), date(2024, 3, 5), date(2024, 3, 6)))       # dopo l'apertura le prime sono chiuse
    s = p036.scegli_ingressi(ops)
    assert [o.simbolo for o in s] == [f"S{k}" for k in range(10)] + ["S11"]


def test_conto_senza_e_con_costi():
    o = op("X", ny("2024-03-04 17:00"), date(2024, 3, 4), date(2024, 3, 5))
    giorni = CAL[1:]
    r = p036.conto([o], giorni, {"in seduta": 0.0, "fuori seduta": 0.0}, costi=False)
    assert r[date(2024, 3, 4)] == 0.0 and abs(r[date(2024, 3, 5)] - 100 * 1.0 / 100_000) < 1e-12   # 100 azioni, guadagno nel giorno d'uscita
    r2 = p036.conto([o], giorni, {"in seduta": 0.0, "fuori seduta": 0.001})
    assert r2[date(2024, 3, 5)] < r[date(2024, 3, 5)]
    rc = p036.conto([o], giorni, {"in seduta": 0.0, "fuori seduta": 0.0}, costi=False, coperta=True)
    assert abs(rc[date(2024, 3, 5)] - 100 * (1.0 - 0.2) / 100_000) < 1e-12
    assert abs(o.lordo - 0.01) < 1e-12


def test_con_ora_toglie_i_moduli_senza_ora():
    a = pd.DataFrame({"numero": ["1", "2"], "simbolo": ["X", "Y"], "valore": [1.0, 2.0]})
    x, senza = depositi_dirigenti.con_ora(a, {"2": "2024-03-04T21:00:00.000Z"})
    assert senza == 1 and list(x["numero"]) == ["2"] and str(x["accettato"].dt.tz) == "UTC"


def test_il_file_dei_depositi():
    d = pd.read_csv(p036.QUI / "dati" / "P036_depositi.csv.gz", dtype={"simbolo": str}, keep_default_na=False)
    assert d["numero"].is_unique and (d["simbolo"] != "").all() and (d["valore"] >= 0).all()          # due moduli a prezzo zero: li toglie la pulizia del prezzo
    assert pd.to_datetime(d["accettato"], utc=True).dt.year.between(2016, 2025).all()
