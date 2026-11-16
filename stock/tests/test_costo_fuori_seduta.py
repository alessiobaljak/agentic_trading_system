"""Le misure del controllo dopo la prova 36: la quotazione prima dell'ordine, dove apre la barra, lo scarto effettivo, il netto."""
import pandas as pd

from stock.prove import p036b


def t(s: str) -> pd.Timestamp:
    return pd.Timestamp(s, tz="America/New_York").tz_convert("UTC")


Q = pd.DataFrame({"bid": [9.0, 0.0, 9.9, 10.0], "ask": [11.0, 10.1, 10.1, 10.2], "bid_size": 1, "ask_size": 1},
                 index=pd.DatetimeIndex([t("2024-03-04 17:01:10"), t("2024-03-04 17:01:50"), t("2024-03-04 17:01:55"),
                                         t("2024-03-04 17:02:20")], name="t"))


def test_quotazione_prima_salta_le_non_valide_e_il_futuro():
    q = p036b.quotazione_prima(Q, t("2024-03-04 17:02"))
    assert q["bid"] == 9.9 and q["ask"] == 10.1
    assert p036b.quotazione_prima(Q, t("2024-03-04 17:01")) is None


def test_posizione_della_barra():
    assert p036b.posizione(10.1, 9.9, 10.1) == 1.0
    assert abs(p036b.posizione(10.0, 9.9, 10.1)) < 1e-12
    assert p036b.posizione(9.9, 9.9, 10.1) == -1.0


def test_scarto_effettivo_col_mezzo_del_momento():
    s = pd.DataFrame({"prezzo": [10.05, 10.2], "quantita": [100, 100]},
                     index=pd.DatetimeIndex([t("2024-03-04 17:02:05"), t("2024-03-04 17:02:30")], name="t"))
    e = p036b.scarto_effettivo(s, Q)
    assert abs(e - (0.05 / 10.0 + 0.1 / 10.1) / 2) < 1e-12        # mezzo 10,0 per la prima, 10,1 per la seconda
    assert pd.isna(p036b.scarto_effettivo(s.iloc[:0], Q))


def test_netto_e_ore():
    n = p036b.netto(0.01, 0.002, 100.0)                       # 100 azioni: commissioni 1 + 1 dollaro su 10'000
    assert abs(n - (0.01 - 0.002 - 2e-4 - 2e-4 * 1.01 - 2.0 / 10_000)) < 1e-12
    assert p036b.ora_di(t("2024-03-04 16:30")) == "16:00-16:59" and p036b.ora_di(t("2024-03-04 05:00")) == "4:00-6:59"
    assert p036b.ora_di(t("2024-03-04 12:00")) == "in seduta" and p036b.ora_di(t("2024-03-04 19:59")) == "18:00-19:59"


def test_scarto_effettivo_con_ore_di_precisione_diversa():
    s = pd.DataFrame({"prezzo": [10.05]}, index=pd.DatetimeIndex([t("2024-03-04 17:02:05")], name="t").as_unit("us"))
    s["quantita"] = 100
    q = Q.copy()
    q.index = q.index.as_unit("ns")
    assert abs(p036b.scarto_effettivo(s, q) - 0.05 / 10.0) < 1e-12
