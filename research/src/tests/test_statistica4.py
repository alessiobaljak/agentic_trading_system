"""Test delle verifiche cambiate o nuove del protocollo 4 (`research/PROTOCOLLO_4.md`, Fase 4,
verifiche 1, 3, 3bis e 4; `research/src/statistica4.py`)."""
from __future__ import annotations

import numpy as np
import pytest

from research.src import statistica3 as st3
from research.src import statistica4 as st4
from research.src.catalogo3 import Serie, compila
from research.src.motore3 import COSTI_NORMALI, Regole, esegui
from research.src.tests.test_statistica3 import V_MERCATO, _ms, _ris, _v, serie_casuale


def _etichette(mosse):
    return [e for e, _ in mosse]


# --------------------------------------------------------------------------- verifica 1


def test_soglia_del_funding_a_zero_si_sposta_di_un_passo():
    v = _v(ingresso={"codice": "E11", "soglia": 0.0, "lato": "sotto"})
    mosse, non_provate = st4.mosse_robustezza_4(v)
    soglie = sorted(w["ingresso"]["soglia"] for e, w in mosse if e.startswith("ingresso.soglia"))
    assert soglie == [-0.00005, 0.00005]
    assert all("passo fisso" in e for e in _etichette(mosse) if e.startswith("ingresso.soglia"))
    assert non_provate == []
    # nel protocollo 3 la stessa soglia non si muoveva
    assert not [e for e, _ in st3.mosse_robustezza(v) if e.startswith("ingresso.soglia")]


def test_soglia_negativa_che_l_arrotondamento_non_sposta():
    v = _v(ingresso={"codice": "E11", "soglia": -0.0001, "lato": "sotto"})
    mosse, _ = st4.mosse_robustezza_4(v)
    soglie = {e.split()[1]: w["ingresso"]["soglia"] for e, w in mosse if e.startswith("ingresso.soglia")}
    # il -20% va verso lo zero, il +20% si allontana
    assert soglie["-20%"] == pytest.approx(-0.00005)
    assert soglie["+20%"] == pytest.approx(-0.00015)


def test_soglia_che_l_arrotondamento_sposta_non_usa_il_passo_fisso():
    v = _v(ingresso={"codice": "E11", "soglia": 0.0003, "lato": "sopra"}, direzione="short")
    mosse, _ = st4.mosse_robustezza_4(v)
    soglie = sorted(w["ingresso"]["soglia"] for e, w in mosse if e.startswith("ingresso.soglia"))
    assert soglie == pytest.approx([0.00025, 0.00035])
    assert not any("passo fisso" in e for e in _etichette(mosse) if e.startswith("ingresso.soglia"))


def test_validita_di_una_candela_non_scende_a_zero():
    v = _v(tipo_ingresso={"codice": "L", "k": 0.25, "validita": 1}, stop={"codice": "S1", "k": 1.5})
    mosse, non_provate = st4.mosse_robustezza_4(v)
    validita = [w["tipo_ingresso"]["validita"] for e, w in mosse if e.startswith("tipo_ingresso.validita")]
    assert validita == [2]
    assert any(e.startswith("tipo_ingresso.validita -20%") and "non valido" in e for e in non_provate)


def test_le_altre_mosse_sono_quelle_del_protocollo_3():
    """Per una variante senza valori che l'arrotondamento non sposta, le mosse sono le stesse."""
    v = _v(stop={"codice": "S1", "k": 2.0}, uscite=[{"codice": "U2", "n": 24}])
    nuove = [(e.replace(" (passo fisso)", ""), w) for e, w in st4.mosse_robustezza_4(v)[0]]
    vecchie = st3.mosse_robustezza(v)
    assert [w for _, w in nuove] == [w for _, w in vecchie]


# --------------------------------------------------------------------------- verifica 3


def test_blocchi_di_otto_mesi():
    ris = _ris([(_ms("2020-02-01"), 1.0), (_ms("2020-09-30"), 1.0), (_ms("2020-10-01"), -1.0),
                (_ms("2021-06-01"), 1.0), (_ms("2022-02-01"), 1.0)])
    esito = st4.stabilita_blocchi_4(ris)
    assert [b["trade"] for b in esito["blocchi"]] == [2, 1, 1, 1]
    assert [b["da"] for b in esito["blocchi"]] == ["inizio", "2020-10-01", "2021-06-01", "2022-02-01"]
    # il modulo del protocollo 3 non e' toccato
    assert st3.BLOCCHI[0] == ("inizio", "2020-06-30")


# --------------------------------------------------------------------------- verifica 3bis


def _serie_giornaliera(prezzi_per_semestre):
    """Una candela al giorno; il prezzo va linearmente dall'apertura alla chiusura di ogni semestre."""
    ts, op, cl = [], [], []
    for (inizio, fine), (p0, p1) in prezzi_per_semestre:
        t0, t1 = _ms(inizio), _ms(fine)
        giorni = (t1 - t0) // 86_400_000
        for k in range(giorni):
            a = p0 + (p1 - p0) * k / giorni
            b = p0 + (p1 - p0) * (k + 1) / giorni
            ts.append(t0 + k * 86_400_000)
            op.append(a)
            cl.append(b)
    ts, op, cl = np.array(ts), np.array(op), np.array(cl)
    hi, lo = np.maximum(op, cl), np.minimum(op, cl)
    return Serie("1d", ts, op, hi, lo, cl, np.ones(len(ts)), op, hi, lo, cl, ts[:1], [0.0])


SEMESTRI = [(("2021-01-01", "2021-07-01"), (10.0, 20.0)),   # +100%: forte rialzo
            (("2021-07-01", "2022-01-01"), (20.0, 22.0)),   # +10%
            (("2022-01-01", "2022-07-01"), (22.0, 11.0))]   # -50%: forte ribasso


def test_mercati_forti():
    s = _serie_giornaliera(SEMESTRI)
    rialzo = [(_ms("2021-02-01") + k * 3_600_000, 0.5) for k in range(30)]
    ribasso = [(_ms("2022-02-01") + k * 3_600_000, -0.2) for k in range(30)]
    esito = st4.mercati_forti(_ris(rialzo + ribasso), s)
    assert esito["semestri"]["2021H1"] == pytest.approx(1.0)
    assert esito["forte_rialzo"]["trade"] == 30 and esito["forte_ribasso"]["trade"] == 30
    assert esito["supera"] is False
    esito = st4.mercati_forti(_ris(rialzo + ribasso[:29]), s)
    assert esito["forte_ribasso"]["decide"] is False and esito["supera"] is True
    esito = st4.mercati_forti(_ris([(_ms("2021-08-01"), -1.0)]), s)
    assert esito["non_applicabile"] is True and esito["supera"] is True


# --------------------------------------------------------------------------- verifica 4


def test_senza_i_migliori_contro_il_caso():
    # candidato: 100 trade, 95 da +0,1 e 5 da +5 -> R medio 0,345; senza i 5 migliori +0,1
    ris = _ris([(_ms("2021-01-01") + k, 5.0 if k < 5 else 0.1) for k in range(100)])
    # caso con lo stesso tipo di uscita: 5 trade da +5 e 95 da -0,2 -> R medio +0,06; senza i migliori -0,2
    casuali = [[5.0] * 5 + [-0.2] * 95 for _ in range(10)]
    esito = st4.senza_i_migliori_4(ris, casuali)
    assert esito["trade_tolti"] == 5
    assert esito["vantaggio"] == pytest.approx(0.345 - 0.06)
    assert esito["vantaggio_senza_migliori"] == pytest.approx(0.1 + 0.2)
    assert esito["supera"] is True
    # stesso candidato, ma il caso non vive di pochi grandi guadagni: il vantaggio sparisce
    piatti = [[0.0] * 100 for _ in range(10)]
    esito = st4.senza_i_migliori_4(ris, piatti)
    assert esito["supera"] is False  # 0,1 < meta' di 0,345
    # senza i migliori il candidato non e' positivo: non supera comunque
    ris_neg = _ris([(_ms("2021-01-01") + k, 6.0 if k < 5 else -0.1) for k in range(100)])
    assert st4.senza_i_migliori_4(ris_neg, casuali)["supera"] is False


def test_entrate_casuali_con_trade_danno_le_stesse_simulazioni():
    s = serie_casuale(3000, seme=11)
    c = compila(V_MERCATO, s)
    ris = esegui(c, Regole(), COSTI_NORMALI, 0, len(s.ts) - 1)
    n = len(ris.trade)
    assert n > 20
    normale = st3.entrate_casuali(c, n, 0, len(s.ts) - 1, Regole(), COSTI_NORMALI, n_simulazioni=50)
    con, trade = st4.entrate_casuali_con_trade(c, n, 0, len(s.ts) - 1, Regole(), COSTI_NORMALI, n_simulazioni=50)
    assert np.array_equal(normale["valori"], con["valori"])
    assert len(trade) == 50 and all(len(x) == n for x in trade)
    assert np.allclose([np.mean(x) for x in trade], con["valori"])
    assert st3._OSSERVATORE is None


# --------------------------------------------------------------------------- Fase 2 e Fase 4 complete


def test_fase2_4_con_i_costi_di_btc_e_la_fase2_del_protocollo_3():
    from research.src.motore3 import Costi
    from research.src.tests.test_statistica3 import V_VANTAGGIO, serie_con_vantaggio
    s = serie_con_vantaggio("4h")
    fine = len(s.ts) - 1
    vecchia = st3.fase2(V_VANTAGGIO, s, 0, fine, n_simulazioni=100)
    nuova = st4.fase2_4(V_VANTAGGIO, s, 0, fine, regole=Regole(), costi=Costi(), n_simulazioni=100)
    assert nuova["metriche"]["r_medio"] == vecchia["metriche"]["r_medio"]
    assert nuova["p_value"] == vecchia["p_value"]
    link = st4.fase2_4(V_VANTAGGIO, s, 0, fine, n_simulazioni=100)
    assert link["metriche"]["trade"] == vecchia["metriche"]["trade"]
    assert link["metriche"]["r_medio"] < vecchia["metriche"]["r_medio"]  # slippage 0,02% invece di 0,01%


def test_fase4_4_ha_le_verifiche_del_protocollo_4():
    from research.src.tests.test_statistica3 import V_VANTAGGIO, serie_con_vantaggio
    s = serie_con_vantaggio("4h")
    fine = len(s.ts) - 1

    def serie_di(tf):
        x = serie_con_vantaggio(tf)
        return x, 0, len(x.ts) - 1

    giornaliera = serie_con_vantaggio("1d")
    esito = st4.fase4_4(V_VANTAGGIO, s, 0, fine, serie_di, giornaliera)
    for chiave in ("1_robustezza", "2_timeframe_adiacenti", "3_blocchi", "3bis_mercati_forti",
                   "4_senza_i_migliori", "5_costi_doppi", "6_troncamento", "7_liquidazione",
                   "9_intrabarra_opposta", "10_ritardo"):
        assert chiave in esito
    assert esito["3_blocchi"]["blocchi"][1]["da"] == "2020-10-01"
    assert "casuali_r_medio_senza_migliori" in esito["4_senza_i_migliori"]
    assert "12" in esito["manca"]
