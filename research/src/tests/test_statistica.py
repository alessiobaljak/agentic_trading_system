"""Test del modulo `statistica` (sezione 8 del protocollo), con esempi a mano.

Ogni numero atteso e' calcolabile con carta e penna o e' una proprieta' che
deve valere qualunque sia il caso (riproducibilita', limiti, monotonia).
"""
from __future__ import annotations

import math

import numpy as np
import pytest

from research.src import statistica as st

# ---------------------------------------------------------------------------
# Benjamini-Hochberg
# ---------------------------------------------------------------------------


def test_bh_esempio_da_manuale():
    # m=5, q=0.1: soglie k/m*q = 0.02, 0.04, 0.06, 0.08, 0.10.
    # p ordinati 0.01<=0.02 si', 0.02<=0.04 si', 0.03<=0.06 si', 0.04<=0.08 si', 0.2<=0.10 no -> k=4.
    assert st.benjamini_hochberg([0.01, 0.02, 0.03, 0.04, 0.2], q=0.1) == [True, True, True, True, False]


def test_bh_nessuno_passa():
    assert st.benjamini_hochberg([0.5, 0.6], q=0.1) == [False, False]


def test_bh_rispetta_ordine_originale():
    # Stessi p dell'esempio da manuale ma mescolati: passano gli stessi quattro.
    p = [0.2, 0.03, 0.01, 0.04, 0.02]
    assert st.benjamini_hochberg(p, q=0.1) == [False, True, True, True, True]


def test_bh_step_up_fa_passare_chi_da_solo_non_passerebbe():
    # m=2, q=0.1: soglie 0.05 e 0.10. p(1)=0.06 > 0.05 da solo cadrebbe, ma
    # p(2)=0.09 <= 0.10 -> k=2 e passano entrambi (procedura step-up).
    assert st.benjamini_hochberg([0.06, 0.09], q=0.1) == [True, True]


def test_bh_lista_vuota_e_valori_fuori_intervallo():
    assert st.benjamini_hochberg([]) == []
    with pytest.raises(ValueError):
        st.benjamini_hochberg([0.5, 1.5])


def test_bh_parita_esatta_sulla_soglia_passa():
    # p(7) = 0.07 con m = 10 e q = 0.1: la soglia esatta e' 7/10*0.1 = 0.07,
    # ma in virgola mobile viene 0.06999999999999999. Il protocollo dice
    # «<=»: la parita' deve passare.
    p = [0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.5, 0.6, 0.7]
    assert st.benjamini_hochberg(p, q=0.1) == [True] * 7 + [False] * 3
    # un pelo sopra la soglia (ben oltre la tolleranza) NON passa
    p[6] = 0.07 + 1e-6
    assert st.benjamini_hochberg(p, q=0.1) == [True] * 6 + [False] * 4


# ---------------------------------------------------------------------------
# Bootstrap a blocchi
# ---------------------------------------------------------------------------


def test_bootstrap_serie_costante_errore_zero():
    r = st.bootstrap_blocchi([2.0] * 50, lunghezza_blocco=5, n=200, seme=1)
    assert r["media"] == 2.0
    assert r["errore_standard"] == 0.0
    assert r["intervallo_95"] == (2.0, 2.0)
    assert len(r["campioni"]) == 200


def test_bootstrap_intervallo_contiene_la_media_e_ha_errore_ragionevole():
    rng = np.random.default_rng(42)
    serie = rng.normal(loc=1.0, scale=2.0, size=400)
    r = st.bootstrap_blocchi(serie, lunghezza_blocco=10, n=1000, seme=0)
    media = float(np.mean(serie))
    assert r["media"] == pytest.approx(media)
    basso, alto = r["intervallo_95"]
    assert basso < media < alto
    # per dati indipendenti l'errore standard della media e' sigma/sqrt(N) = 0.1:
    # il bootstrap deve dare un numero dello stesso ordine
    assert 0.05 < r["errore_standard"] < 0.2


def test_bootstrap_riproducibile_e_sensibile_al_seme():
    serie = list(range(30))
    a = st.bootstrap_blocchi(serie, 3, n=100, seme=7)
    b = st.bootstrap_blocchi(serie, 3, n=100, seme=7)
    c = st.bootstrap_blocchi(serie, 3, n=100, seme=8)
    assert np.array_equal(a["campioni"], b["campioni"])
    assert not np.array_equal(a["campioni"], c["campioni"])


def test_bootstrap_blocco_lungo_quanto_la_serie_e_rifiutato():
    # Questo test prima ACCETTAVA il difetto (blocco >= N ridotto in silenzio,
    # errore 0 "per costruzione"): un errore 0 a valle rendeva "netta" qualsiasi
    # differenza e dava il p-value minimo. Ora il caso degenere e' rifiutato.
    with pytest.raises(ValueError):
        st.bootstrap_blocchi([1.0, 2.0, 3.0, 4.0], lunghezza_blocco=100, n=50, seme=0)
    with pytest.raises(ValueError):
        st.bootstrap_blocchi([1.0, 2.0, 3.0, 4.0], lunghezza_blocco=4, n=50, seme=0)
    with pytest.raises(ValueError):
        st.bootstrap_blocchi([1.0, 2.0, 3.0, 4.0], lunghezza_blocco=0, n=50, seme=0)
    # blocco 3 su 4 elementi: ammesso (2 blocchi), e il numero di blocchi e' nel risultato
    r = st.bootstrap_blocchi([1.0, 2.0, 3.0, 4.0], lunghezza_blocco=3, n=50, seme=0)
    assert r["media"] == 2.5
    assert r["n_blocchi"] == 2
    assert st.bootstrap_degenere(4, 4) is True
    assert st.bootstrap_degenere(4, 3) is False


def test_bootstrap_statistica_diversa():
    r = st.bootstrap_blocchi([1.0, 2.0, 3.0, 100.0], lunghezza_blocco=1, n=100, seme=0, statistica=np.median)
    assert r["media"] == 2.5


def test_bootstrap_rifiuta_serie_vuota_e_nan():
    with pytest.raises(ValueError):
        st.bootstrap_blocchi([], 1)
    with pytest.raises(ValueError):
        st.bootstrap_blocchi([1.0, float("nan")], 1)


def test_indici_blocchi_sono_contigui_e_circolari():
    rng = np.random.default_rng(0)
    idx = st._indici_blocchi_circolari(n_valori=10, lunghezza_blocco=4, n=5, rng=rng)
    assert idx.shape == (5, 10)
    # dentro ogni blocco gli indici crescono di 1 modulo 10
    for riga in idx:
        for inizio in range(0, 8, 4):
            blocco = riga[inizio:inizio + 4]
            assert all((blocco[j + 1] - blocco[j]) % 10 == 1 for j in range(3))


# ---------------------------------------------------------------------------
# «Nettamente»
# ---------------------------------------------------------------------------


def test_differenza_nettamente_serie_chiaramente_diverse():
    rng = np.random.default_rng(1)
    a = rng.normal(1.0, 0.5, size=200)
    b = rng.normal(0.0, 0.5, size=200)
    r = st.differenza_nettamente(a, b, lunghezza_blocco=5, n=500, seme=0)
    assert r["netta"] is True
    assert r["segno"] == 1
    assert r["differenza"] == pytest.approx(float(np.mean(a) - np.mean(b)))
    assert r["margine"] == pytest.approx(2 * r["errore_standard"])


def test_differenza_nettamente_serie_uguali():
    rng = np.random.default_rng(2)
    a = rng.normal(0.0, 1.0, size=100)
    r = st.differenza_nettamente(a, a, lunghezza_blocco=5, n=500, seme=0)
    assert r["differenza"] == 0.0
    assert r["netta"] is False
    assert r["segno"] == 0


def test_differenza_nettamente_segno_negativo():
    r = st.differenza_nettamente([0.0] * 40, [1.0] * 40, lunghezza_blocco=4, n=100, seme=0)
    assert r["differenza"] == -1.0
    assert r["errore_standard"] == 0.0
    assert r["netta"] is True
    assert r["segno"] == -1
    assert r["degenere"] is False


def test_differenza_nettamente_caso_degenere_non_e_mai_netta():
    # blocco lungo quanto la serie (o di piu'): il bootstrap non stima nulla.
    # Prima il margine veniva 0 e una differenza di 1e-9 era "netta"; ora il
    # giudizio prudente: non netta, errore e margine infiniti, segnalato.
    rng = np.random.default_rng(3)
    caso = list(rng.normal(0.0, 1.0, 30))
    cand = [x + 1e-9 for x in caso]
    for blocco in (30, 40):
        r = st.differenza_nettamente(cand, caso, lunghezza_blocco=blocco, n=200, seme=0)
        assert r["degenere"] is True
        assert r["netta"] is False
        assert r["errore_standard"] == math.inf and r["margine"] == math.inf
        assert r["differenza"] == pytest.approx(1e-9, rel=1e-3)
        assert r["segno"] == 1
    # basta che UNA delle due serie sia troppo corta per il blocco
    r = st.differenza_nettamente(cand * 3, caso, lunghezza_blocco=30, n=200, seme=0)
    assert r["degenere"] is True and r["netta"] is False
    # appena sotto il limite non e' degenere
    r = st.differenza_nettamente(cand, caso, lunghezza_blocco=29, n=200, seme=0)
    assert r["degenere"] is False and r["netta"] is False


# ---------------------------------------------------------------------------
# p-value
# ---------------------------------------------------------------------------


def test_p_value_bootstrap_vs_caso_degenere_vale_uno():
    # stesso caso: prima usciva 1/(n+1) (il MINIMO) per un vantaggio di 1e-9;
    # ora esce 1.0 = nessuna evidenza, il candidato non passa l'asticella.
    rng = np.random.default_rng(3)
    caso = list(rng.normal(0.0, 1.0, 30))
    cand = [x + 1e-9 for x in caso]
    assert st.p_value_bootstrap_vs_caso(cand, caso, lunghezza_blocco=30, n=200, seme=0) == 1.0
    assert st.p_value_bootstrap_vs_caso(cand, caso, lunghezza_blocco=40, n=200, seme=0) == 1.0
    assert st.p_value_bootstrap_vs_caso(cand * 3, caso, lunghezza_blocco=30, n=200, seme=0) == 1.0
    # con blocco ammesso e vantaggio nullo il p-value sta intorno a 0,5
    p = st.p_value_bootstrap_vs_caso(cand, caso, lunghezza_blocco=10, n=2000, seme=0)
    assert 0.3 < p < 0.7


def test_p_value_unilaterale_con_correzione():
    nulla = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]  # n = 9
    # valori >= 0.75: 0.8, 0.9 -> k=2 -> (2+1)/(9+1)
    assert st.p_value_unilaterale(0.75, nulla) == pytest.approx(0.3)
    # nessun valore raggiunge 2.0 -> (0+1)/(9+1), mai zero
    assert st.p_value_unilaterale(2.0, nulla) == pytest.approx(0.1)
    # tutti raggiungono -1 -> (9+1)/(9+1) = 1
    assert st.p_value_unilaterale(-1.0, nulla) == pytest.approx(1.0)
    # il confronto e' >= (incluso)
    assert st.p_value_unilaterale(0.9, nulla) == pytest.approx(0.2)
    assert st.p_value_unilaterale(0.0, []) == 1.0


def test_p_value_bootstrap_vs_caso_piccolo_se_candidato_batte_il_caso():
    rng = np.random.default_rng(3)
    cand = rng.normal(0.5, 0.5, size=100)
    caso = rng.normal(0.0, 0.5, size=100)
    p = st.p_value_bootstrap_vs_caso(cand, caso, lunghezza_blocco=5, n=1000, seme=0)
    assert p < 0.01
    # il minimo e' 1/(n+1), mai zero
    assert p >= 1 / 1001


def test_p_value_bootstrap_vs_caso_grande_se_candidato_non_batte_il_caso():
    rng = np.random.default_rng(4)
    cand = rng.normal(0.0, 0.5, size=100)
    # stessa serie da entrambe le parti (ricampionata con semi diversi): la
    # differenza delle medie oscilla intorno a zero, quindi p vicino a 0,5
    p = st.p_value_bootstrap_vs_caso(cand, cand, lunghezza_blocco=5, n=1000, seme=0)
    assert 0.3 < p < 0.7
    caso = rng.normal(0.0, 0.5, size=100)
    # candidato peggiore del caso -> p vicino a 1
    p_peggio = st.p_value_bootstrap_vs_caso(cand - 1.0, caso, lunghezza_blocco=5, n=1000, seme=0)
    assert p_peggio > 0.99


def test_p_value_bootstrap_riproducibile():
    cand = [0.3, -0.2, 0.5, 0.1, 0.4, -0.1, 0.2, 0.6, 0.0, 0.3] * 4
    caso = [0.0, 0.1, -0.3, 0.2, -0.1, 0.0, 0.1, -0.2, 0.2, 0.0] * 4
    p1 = st.p_value_bootstrap_vs_caso(cand, caso, 3, n=300, seme=5)
    p2 = st.p_value_bootstrap_vs_caso(cand, caso, 3, n=300, seme=5)
    assert p1 == p2


# ---------------------------------------------------------------------------
# percentile e metriche
# ---------------------------------------------------------------------------


def test_percentile_lineare():
    assert st.percentile([1, 2, 3, 4, 5], 50) == 3.0
    assert st.percentile([1, 2, 3, 4], 50) == 2.5  # interpolazione lineare
    assert st.percentile([10, 20], 90) == pytest.approx(19.0)
    assert st.percentile([5.0], 90) == 5.0


def test_profit_factor_casi_limite():
    assert st.profit_factor([2.0, -1.0, 3.0, -1.0]) == pytest.approx(2.5)
    assert st.profit_factor([1.0, 2.0]) == math.inf  # nessuna perdita
    assert st.profit_factor([-1.0, -2.0]) == 0.0  # nessun guadagno
    assert st.profit_factor([]) == 0.0
    assert st.profit_factor([0.0, 0.0]) == 0.0  # ne' guadagni ne' perdite


def test_win_rate():
    assert st.win_rate([1.0, -1.0, 2.0, 0.0]) == 0.5  # 2 vinti su 4: lo zero non e' vinto
    assert st.win_rate([1.0, -1.0, 0.0, 0.0]) == 0.25
    assert st.win_rate([]) == 0.0


def test_drawdown_su_curva_a_mano():
    assert st.drawdown_max_da_curva([100, 120, 90, 130]) == pytest.approx(0.25)
    assert st.drawdown_max_da_curva([100, 110, 120]) == 0.0  # mai in calo
    assert st.drawdown_max_da_curva([100, 50, 75, 25]) == pytest.approx(0.75)
    assert st.drawdown_max_da_curva([]) == 0.0


def _ts(anno: int, mese: int = 1, giorno: int = 1) -> int:
    from datetime import datetime, timezone

    return int(datetime(anno, mese, giorno, tzinfo=timezone.utc).timestamp() * 1000)


def test_rendimento_per_anno():
    curva = [
        (_ts(2021, 1, 5), 100.0),
        (_ts(2021, 6, 1), 130.0),
        (_ts(2021, 12, 20), 120.0),  # 2021 chiude a 120 partendo da 100 -> +20%
        (_ts(2022, 3, 1), 90.0),
        (_ts(2022, 11, 1), 150.0),  # 2022 chiude a 150 partendo da 120 -> +25%
        (_ts(2023, 2, 1), 75.0),  # 2023 chiude a 75 partendo da 150 -> -50%
    ]
    r = st.rendimento_per_anno(curva)
    assert set(r) == {2021, 2022, 2023}
    assert r[2021] == pytest.approx(0.20)
    assert r[2022] == pytest.approx(0.25)
    assert r[2023] == pytest.approx(-0.50)
    # i rendimenti si compongono nel totale: 1.2 * 1.25 * 0.5 = 0.75 = 75/100
    assert (1 + r[2021]) * (1 + r[2022]) * (1 + r[2023]) == pytest.approx(0.75)
    # l'ordine della curva non conta
    assert st.rendimento_per_anno(list(reversed(curva))) == r
    assert st.rendimento_per_anno([]) == {}


# ---------------------------------------------------------------------------
# Entrate casuali, tasso del caso, criterio del vault
# ---------------------------------------------------------------------------


def test_entrate_casuali_riproducibili_e_diverse_con_altro_seme():
    a = st.entrate_casuali(1000, 20, 10, seme=3)
    b = st.entrate_casuali(1000, 20, 10, seme=3)
    c = st.entrate_casuali(1000, 20, 10, seme=4)
    assert a == b
    assert a != c
    assert len(a) == 20


def test_entrate_casuali_senza_sovrapposizione_e_dentro_i_limiti():
    for seme in range(5):
        idx = st.entrate_casuali(500, 30, durata_media_barre=12, seme=seme)
        assert idx == sorted(idx)
        assert len(set(idx)) == 30
        assert all(0 <= i < 500 for i in idx)
        assert all(idx[j + 1] - idx[j] >= 12 for j in range(len(idx) - 1))


def test_entrate_casuali_rispettano_barre_vietate():
    vietate = [(0, 50), (200, 260), (480, 500)]
    for seme in range(5):
        idx = st.entrate_casuali(500, 25, 8, seme=seme, barre_vietate=vietate)
        assert len(idx) == 25
        for i in idx:
            assert not any(lo <= i < hi for lo, hi in vietate)
            assert 0 <= i < 500


def test_entrate_casuali_riescono_sempre_se_una_configurazione_esiste():
    # 5 barre, distanza 2, 3 ingressi: l'unica configurazione e' [0, 2, 4] e
    # deve uscire con QUALUNQUE seme (il vecchio greedy falliva con alcuni semi).
    for seme in range(20):
        assert st.entrate_casuali(5, 3, 2, seme) == [0, 2, 4]
    # trade fitti: 80 ingressi a distanza 10 su 1000 barre (massimo 100)
    for seme in range(30):
        idx = st.entrate_casuali(1000, 80, 10, seme)
        assert len(idx) == 80
        assert all(b - a >= 10 for a, b in zip(idx, idx[1:]))
    # al limite esatto: 100 ingressi a distanza 10 su 991 barre (0, 10, ..., 990):
    # una sola configurazione, con qualunque seme
    for seme in (0, 7, 123):
        assert st.entrate_casuali(991, 100, 10, seme=seme) == list(range(0, 991, 10))
    # con 1000 barre invece c'e' gioco (9 barre): 100 ingressi entrano comunque
    idx = st.entrate_casuali(1000, 100, 10, seme=7)
    assert len(idx) == 100 and all(b - a >= 10 for a, b in zip(idx, idx[1:]))
    # anche con barre vietate che lasciano una sola configurazione: [0, 3, 6]
    assert st.entrate_casuali(8, 3, 3, seme=5, barre_vietate=[(7, 8)]) == [0, 3, 6]


def test_entrate_casuali_uniformi_fra_le_configurazioni():
    # 4 barre, distanza 2, 2 ingressi: le configurazioni sono {0,2}, {0,3}, {1,3}
    # e devono uscire con la stessa frequenza (1/3 ciascuna, tolleranza 3%).
    conteggi = {}
    for seme in range(3000):
        chiave = tuple(st.entrate_casuali(4, 2, 2, seme))
        conteggi[chiave] = conteggi.get(chiave, 0) + 1
    assert set(conteggi) == {(0, 2), (0, 3), (1, 3)}
    for valore in conteggi.values():
        assert abs(valore / 3000 - 1 / 3) < 0.03


def test_log_configurazioni_conta_giusto():
    # 4 barre tutte ammesse, distanza 2: con 1 ingresso 4 modi, con 2 ingressi 3 modi
    tabella = st._log_configurazioni(np.ones(4, dtype=bool), 2, 2)
    assert tabella[0, 0] == 0.0
    assert tabella[0, 1] == pytest.approx(math.log(4))
    assert tabella[0, 2] == pytest.approx(math.log(3))
    # distanza 1: sottoinsiemi semplici, binomiale(4, 2) = 6
    tabella = st._log_configurazioni(np.ones(4, dtype=bool), 2, 1)
    assert tabella[0, 2] == pytest.approx(math.log(6))


def test_entrate_casuali_casi_limite():
    assert st.entrate_casuali(100, 0, 5, seme=0) == []
    # 10 barre, distanza 5: ci stanno al massimo 2 ingressi (es. 0 e 5): 3 non si piazzano
    with pytest.raises(ValueError):
        st.entrate_casuali(10, 3, 5, seme=0)
    # tutto vietato -> nessun candidato
    with pytest.raises(ValueError):
        st.entrate_casuali(10, 1, 1, seme=0, barre_vietate=[(0, 10)])
    with pytest.raises(ValueError):
        st.entrate_casuali(0, 1, 1, seme=0)


def test_tasso_del_caso():
    assert st.tasso_del_caso([True, False, False, True]) == 0.5
    assert st.tasso_del_caso([]) == 0.0


def _metriche(pf=1.5, n=40, rend=0.1, r=0.3):
    return {"profit_factor": pf, "n_trade": n, "rendimento_totale": rend, "r_medio": r}


def test_criterio_vault_passa_quando_tutte_vere():
    r = st.criterio_vault(_metriche(), r_caso_percentile_90=0.1)
    assert r["esito"] is True
    assert all(r["condizioni"].values())
    assert set(r["condizioni"]) == {"profit_factor", "trade_minimi", "rendimento_positivo", "sopra_il_caso"}


def test_criterio_vault_condizioni_separate():
    # profit factor sotto 1.10
    r = st.criterio_vault(_metriche(pf=1.05), 0.1)
    assert r["esito"] is False
    assert r["condizioni"]["profit_factor"] is False
    assert r["condizioni"]["trade_minimi"] is True
    # trade sotto il minimo
    r = st.criterio_vault(_metriche(n=29), 0.1)
    assert r["esito"] is False and r["condizioni"]["trade_minimi"] is False
    assert r["condizioni"]["profit_factor"] is True
    # rendimento non positivo (zero non basta)
    r = st.criterio_vault(_metriche(rend=0.0), 0.1)
    assert r["esito"] is False and r["condizioni"]["rendimento_positivo"] is False
    # R medio non sopra il 90° percentile del caso (uguale non basta)
    r = st.criterio_vault(_metriche(r=0.3), r_caso_percentile_90=0.3)
    assert r["esito"] is False and r["condizioni"]["sopra_il_caso"] is False
    # soglie ai bordi: pf esattamente 1.10 e n esattamente 30 passano
    r = st.criterio_vault(_metriche(pf=1.10, n=30), 0.1)
    assert r["esito"] is True


def test_criterio_vault_soglie_personalizzate_e_chiave_mancante():
    r = st.criterio_vault(_metriche(pf=1.2, n=50), 0.1, trade_minimi=60, pf_minimo=1.3)
    assert r["condizioni"]["profit_factor"] is False
    assert r["condizioni"]["trade_minimi"] is False
    with pytest.raises(KeyError):
        st.criterio_vault({"profit_factor": 2.0}, 0.1)
