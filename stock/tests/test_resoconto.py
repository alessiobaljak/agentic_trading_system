"""Il resoconto del lunedì (stock/avanti/resoconto.py) su diari costruiti a mano: niente rete, niente conto."""
import math

import pandas as pd
import pytest

from stock.avanti import resoconto as rs

COLONNE = ["giorno", "simbolo", "lato", "quantita", "ingresso", "ora_ingresso", "uscita_prezzo", "ora_uscita", "uscita", "guadagno",
           "proporzione", "commissione_ib", "stop", "obiettivo", "riferimento", "nota"]


def _riga(giorno, simbolo, lato, q, ingresso, ora, uscita_p, uscita, rif, stop, nota=""):
    segno = 1 if lato == "buy" else -1
    guadagno = float("nan") if math.isnan(uscita_p) else segno * (uscita_p - ingresso) * q
    return [giorno, simbolo, lato, q, ingresso, ora, uscita_p, ora, uscita, round(guadagno, 2),
            float("nan") if math.isnan(guadagno) else guadagno / (ingresso * q), 2.0, stop, 0.0, rif, nota]


def _diario():
    righe = [
        # giorno puntuale: compra a 100,05 con la candela a 100 (5 pb peggio), esce allo stop a 98,9 con lo stop a 99 (10 pb peggio)
        _riga("2026-11-10", "AAA", "buy", 100, 100.05, "2026-11-10T14:45:05Z", 98.9, "stop", 100.0, 99.0),
        # vendita: vende a 49,99 con la candela a 50 (2 pb peggio), chiude a 49
        _riga("2026-11-10", "BBB", "sell", 200, 49.99, "2026-11-10T14:45:06Z", 49.0, "chiusura", 50.0, 51.0),
        # giorno fuori regola: non conta
        _riga("2026-11-11", "CCC", "buy", 10, 10.0, "2026-11-11T14:45:05Z", 11.0, "chiusura", 10.0, 9.0),
        # giorno in ritardo (9:57): conta, ma il suo costo sta fuori dalla media dei giorni puntuali
        _riga("2026-11-12", "DDD", "buy", 100, 101.0, "2026-11-12T14:57:00Z", 102.0, "obiettivo", 100.0, 99.0),
        # rifiutato perché già oltre lo stop
        ["2026-11-12", "EEE", "sell", float("nan"), float("nan"), None, float("nan"), None, "", float("nan"), float("nan"),
         float("nan"), 10.0, 0.0, 9.0, "saltato: rifiutato (422 {\"code\":42210000})"],
    ]
    return pd.DataFrame(righe, columns=COLONNE)


def test_costo_d_ingresso_e_scarto_allo_stop_hanno_il_segno_del_peggio():
    assert rs.costo_ingresso_pb("buy", 100.05, 100.0) == pytest.approx(5.0)
    assert rs.costo_ingresso_pb("sell", 49.99, 50.0) == pytest.approx(2.0)
    assert rs.costo_ingresso_pb("sell", 50.01, 50.0) == pytest.approx(-2.0)      # vendere più in alto è meglio
    assert rs.scarto_stop_pb("buy", 98.9, 99.0) == pytest.approx(10.1, abs=0.05)  # l'acquisto esce sotto lo stop: peggio
    assert rs.scarto_stop_pb("sell", 51.05, 51.0) == pytest.approx(9.8, abs=0.05)
    assert math.isnan(rs.costo_ingresso_pb("buy", float("nan"), 100.0))


def test_giorni_in_ritardo_gia_oltre_lo_stop_e_giorno_fuori_regola():
    d = _diario()
    assert rs.giorni_in_ritardo(d) == {"2026-11-12": "09:57"}
    assert rs.gia_oltre_lo_stop(d) == 1
    assert set(rs.nel_giudizio(d)["giorno"]) == {"2026-11-10", "2026-11-12"}


def test_la_tabella_per_settimana_torna_con_il_totale_senza_il_giorno_fuori_regola():
    d = _diario()
    s = rs.settimane(d)
    fatte = rs.chiuse(rs.nel_giudizio(d))
    assert int(s["operazioni"].sum()) == len(fatte) == 3
    assert float(s["guadagno"].sum()) == pytest.approx(float(fatte["guadagno"].sum()))


def test_il_t_si_misura_sui_giorni_non_sulle_operazioni():
    # due giorni con 10 operazioni identiche ciascuno: sulle operazioni sembrano 20 osservazioni, sui giorni sono 2
    righe = []
    for giorno, p in (("2026-11-16", 0.01), ("2026-11-17", -0.005)):
        for i in range(10):
            righe.append(_riga(giorno, f"T{i}", "buy", 100, 100.0, f"{giorno}T14:45:05Z", 100 * (1 + p), "chiusura", 100.0, 99.0))
    d = pd.DataFrame(righe, columns=COLONNE)
    g = rs.per_giorno(rs.chiuse(d))
    assert len(g) == 2 and g.iloc[0] == pytest.approx(0.01)
    assert abs(rs.t_di(g)) < abs(rs.t_di(rs.chiuse(d)["proporzione"]))


def test_spy_negli_stessi_giorni_composto():
    spy = pd.DataFrame({"open": [100.0, 101.0, 99.0, 100.0], "close": [100.0, 102.0, 98.0, 101.0]},
                       index=pd.to_datetime(["2026-11-09", "2026-11-10", "2026-11-11", "2026-11-12"]))
    s = rs.spy_negli_stessi_giorni(spy, ["2026-11-10", "2026-11-12"])
    assert s["giorni"] == 2
    assert s["apertura_chiusura"] == pytest.approx(102 / 101 * 101 / 100 - 1)
    assert s["chiusura_chiusura"] == pytest.approx(102 / 100 * 101 / 98 - 1)


def test_il_testo_si_scrive_anche_senza_lo_spy_e_senza_i_diari_delle_altre():
    t = rs.testo(_diario(), None, None, None)
    assert "non disponibile" in t and "2026-11-12 (dalle 09:57)" in t and "Ancora nessun giorno" in t
    valori = pd.DataFrame({"giorno": ["2026-11-10", "2026-11-12"], "conto": [100500.0, 99000.0],
                           "prima_candela": [100500.0, 99000.0], "miscela": [float("nan"), 100000.0], "gamma": [float("nan")] * 2})
    t2 = rs.testo(_diario(), valori, None, None)
    assert "-1,00% dal capitale di partenza" in t2
