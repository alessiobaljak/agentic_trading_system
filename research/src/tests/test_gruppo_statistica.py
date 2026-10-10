"""Test delle funzioni statistiche della campagna di gruppo (``campagne/GRUPPO/regole.md``, sezioni 5, 6 e 13).

Quattro famiglie di prove, come chiede la sezione 13 di regole.md:
* con UNA moneta sola e pavimento 0 le funzioni di gruppo danno gli stessi
  numeri del percorso delle campagne singole (``baseline_da_trade``,
  ``baseline_casuale``, ``contro_baseline``), bit per bit;
* due monete calcolate a mano;
* l'esito non cambia con l'ordine delle monete (ne' dei trade);
* casi limite (non valutabile, liste vuote, parita', arrotondamenti).
In piu': ``contro_baseline`` con ``pavimento_minimo`` = 0 e' identica alla
versione di prima, confrontata con una copia congelata qui sotto.
"""
from __future__ import annotations

import dataclasses
import math
import random
from datetime import datetime, timezone
from fractions import Fraction

import numpy as np
import pytest

from research.src import motore
from research.src import statistica as st
from research.src.motore import Candela, Parametri, Segnale
from research.src.statistica import TradeDiGruppo

# ---------------------------------------------------------------------------
# La versione di prima di contro_baseline (com'era fino al commit a52b11de,
# protocollo 4.5), copiata cosi' com'era: il riferimento per «con 0 e'
# identica a prima».
# ---------------------------------------------------------------------------


def _confronto_prima(r_candidato, lunghezza_blocco, baseline_media, baseline_errore_standard, n, seme,
                     errore_minimo_candidato=0.0):
    from scipy.stats import t as student

    arr = st._come_array(r_candidato, "r_candidato")
    base = float(baseline_media)
    errore_base = float(baseline_errore_standard)
    if math.isnan(base) or math.isinf(base) or math.isnan(errore_base) or errore_base < 0:
        raise ValueError("baseline_media deve essere un numero finito e baseline_errore_standard non negativo")
    pavimento = float(errore_minimo_candidato)
    if not math.isfinite(pavimento) or pavimento < 0:
        raise ValueError("errore_minimo_candidato deve essere un numero finito non negativo")
    if not np.isfinite(arr).all():
        raise ValueError("r_candidato contiene valori non finiti")
    b = int(lunghezza_blocco)
    if b < 1:
        raise ValueError("lunghezza_blocco deve essere almeno 1")
    differenza = float(arr.mean()) - base
    k = arr.size // b
    non_valutabile = {
        "differenza": differenza, "errore_standard": math.inf, "margine": math.inf, "soglia": math.inf,
        "gradi_liberta": max(0, k - 1), "netta": False, "t": -math.inf, "p_value": 1.0,
        "errore_candidato": math.inf, "n_blocchi": int(k), "valutabile": False,
    }
    if k < st.MINIMO_BLOCCHI or math.isinf(errore_base):
        return non_valutabile
    errore_c, _ = st._errore_media_corretto(arr, b, n, seme)
    errore_c = max(errore_c, pavimento)
    errore = math.sqrt(errore_c ** 2 + errore_base ** 2)
    if errore_c == 0.0:
        return dict(non_valutabile, errore_candidato=0.0)
    gradi = k - 1
    soglia = float(student.ppf(st.LIVELLO_NETTAMENTE, gradi))
    t = differenza / errore
    return {
        "differenza": differenza, "errore_standard": errore, "margine": soglia * errore, "soglia": soglia,
        "gradi_liberta": int(gradi), "netta": bool(t > soglia), "t": float(t),
        "p_value": float(student.sf(t, gradi)), "errore_candidato": errore_c, "n_blocchi": int(k),
        "valutabile": True,
    }


def _contro_baseline_prima(r_candidato, lunghezza_blocco, baseline, n=2000, seme=0):
    tipo = baseline.get("tipo")
    arr = st._come_array(r_candidato, "r_candidato")
    if tipo == "b":
        pavimento = float(baseline["errore_minimo_candidato"])
    elif tipo == "a":
        pavimento = float(baseline["deviazione_standard"]) / math.sqrt(arr.size)
    else:
        raise ValueError("baseline: serve il dizionario di baseline_casuale (tipo b) o di baseline_da_trade (tipo a)")
    ris = _confronto_prima(arr, lunghezza_blocco, float(baseline["media"]), float(baseline["errore_standard"]), n,
                           seme, pavimento)
    ris.update({"baseline_media": float(baseline["media"]),
                "baseline_errore_standard": float(baseline["errore_standard"]),
                "errore_minimo": pavimento})
    return ris


CHIAVI_NUOVE = {"errore_minimo_baseline", "pavimento_minimo", "origine_pavimento", "errore_candidato_senza_pavimento"}


def _stesso_valore(a, b) -> bool:
    """Uguaglianza esatta, anche di tipo; NaN uguale a NaN."""
    if isinstance(a, float) and isinstance(b, float) and math.isnan(a) and math.isnan(b):
        return True
    return type(a) is type(b) and a == b


def _uguale_a_prima(nuovo: dict, prima: dict) -> None:
    for chiave, valore in prima.items():
        assert _stesso_valore(nuovo[chiave], valore), (chiave, nuovo[chiave], valore)
    assert set(nuovo) == set(prima) | CHIAVI_NUOVE


def _casi_confronto():
    """Candidati e baseline vari: (b), (a) valutabile e no, pochi blocchi, serie costante, soli vincenti."""
    rng = np.random.default_rng(20261010)
    candidati = [
        ([0.1] * 30, 1),                                   # soli vincenti
        ([0.0] * 12, 2),                                   # serie costante
        (list(rng.normal(0.4, 0.8, 100)), 2),
        (list(rng.normal(0.0, 1.0, 9)), 4),                # k = 2: non valutabile
        (list(rng.normal(0.05, 1.0, 300)), 7),
        (list(np.where(rng.random(200) < 0.9, 0.1, -1.0)), 5),
        (list(rng.standard_t(3, 57) * 0.5), 3),
    ]
    baseline = [
        st.baseline_casuale(list(rng.normal(0.0, 0.15, 200))),
        st.baseline_casuale(list(rng.normal(-0.1, 0.02, 37))),
        st.baseline_da_trade(list(rng.normal(0.0, 0.8, 600)), 2),
        st.baseline_da_trade(list(rng.normal(0, 1, 40)), 15),        # non valutabile
        st.baseline_da_trade([0.2] * 50, 5),                         # deviazione 0
    ]
    for r, blocco in candidati:
        for base in baseline:
            yield r, blocco, base


# ---------------------------------------------------------------------------
# contro_baseline con pavimento_minimo
# ---------------------------------------------------------------------------


def test_contro_baseline_con_pavimento_zero_e_identica_a_prima():
    casi = 0
    for r, blocco, base in _casi_confronto():
        prima = _contro_baseline_prima(r, blocco, base)
        _uguale_a_prima(st.contro_baseline(r, blocco, base), prima)
        _uguale_a_prima(st.contro_baseline(r, blocco, base, pavimento_minimo=0.0), prima)
        _uguale_a_prima(st.contro_baseline(r, blocco, base, 2000, 0, 0), prima)
        casi += 1
    assert casi == 35


def test_contro_baseline_con_pavimento_zero_identica_su_casi_casuali():
    rng = np.random.default_rng(7)
    for _ in range(150):
        n = int(rng.integers(1, 90))
        blocco = int(rng.integers(1, 12))
        r = list(rng.normal(float(rng.normal(0, 0.2)), float(rng.uniform(0.1, 2)), n))
        base_b = st.baseline_casuale(list(rng.normal(0.0, float(rng.uniform(0.01, 0.3)), int(rng.integers(2, 60)))))
        base_a = st.baseline_da_trade(list(rng.normal(0.0, 1.0, int(rng.integers(1, 200)))), int(rng.integers(1, 30)))
        for base in (base_b, base_a):
            _uguale_a_prima(st.contro_baseline(r, blocco, base), _contro_baseline_prima(r, blocco, base))


def test_batte_nettamente_e_p_value_restano_quelli_di_prima():
    rng = np.random.default_rng(11)
    for r, blocco, base in _casi_confronto():
        for e_min in (0.0, 0.05, float(rng.uniform(0, 0.4))):
            args = (r, blocco, float(base["media"]), float(base["errore_standard"]))
            if math.isinf(args[3]):
                args = (r, blocco, float(base["media"]), math.inf)
            prima = _confronto_prima(*args, 2000, 0, e_min)
            assert st.batte_nettamente(*args, errore_minimo_candidato=e_min) == prima
            assert st.p_value_vs_baseline(*args, errore_minimo_candidato=e_min) == prima["p_value"]


def test_contro_baseline_le_chiavi_nuove_con_pavimento_zero():
    rng = np.random.default_rng(3)
    base = st.baseline_casuale(list(rng.normal(0.0, 0.15, 200)))
    r = list(rng.normal(0.1, 1.0, 120))
    ris = st.contro_baseline(r, 4, base)
    assert ris["pavimento_minimo"] == 0.0
    assert ris["origine_pavimento"] == "baseline"
    assert ris["errore_minimo"] == ris["errore_minimo_baseline"] == base["errore_minimo_candidato"]
    errore, _ = st._errore_media_corretto(np.asarray(r), 4, 2000, 0)
    assert ris["errore_candidato_senza_pavimento"] == errore


def test_contro_baseline_pavimento_minimo_piu_alto_vince():
    rng = np.random.default_rng(4)
    base = st.baseline_casuale(list(rng.normal(0.0, 0.05, 200)))
    r = list(rng.normal(0.2, 1.0, 150))
    minimo = 0.5  # molto sopra l'errore del bootstrap (~0,08) e il pavimento della (b) (~0,05)
    ris = st.contro_baseline(r, 3, base, pavimento_minimo=minimo)
    assert ris["errore_minimo"] == minimo and ris["origine_pavimento"] == "pavimento_minimo"
    assert ris["errore_minimo_baseline"] == base["errore_minimo_candidato"]
    assert ris["errore_candidato"] == minimo
    assert ris["errore_candidato_senza_pavimento"] < minimo
    # e' esattamente batte_nettamente con quel pavimento
    atteso = st.batte_nettamente(r, 3, base["media"], base["errore_standard"], errore_minimo_candidato=minimo)
    assert {k: ris[k] for k in atteso} == atteso
    # un pavimento_minimo sotto quello della baseline non cambia nulla, a parte la chiave che lo riporta
    basso = st.contro_baseline(r, 3, base, pavimento_minimo=base["errore_minimo_candidato"] / 2)
    zero = st.contro_baseline(r, 3, base)
    assert {k: v for k, v in basso.items() if k != "pavimento_minimo"} == \
           {k: v for k, v in zero.items() if k != "pavimento_minimo"}
    # a pari valore il pavimento resta «della baseline»
    pari = st.contro_baseline(r, 3, base, pavimento_minimo=base["errore_minimo_candidato"])
    assert pari["origine_pavimento"] == "baseline"


def test_contro_baseline_pavimento_minimo_contro_la_a():
    rng = np.random.default_rng(5)
    a = st.baseline_da_trade(list(rng.normal(0.0, 0.8, 600)), 2)
    cand = list(rng.normal(0.4, 0.8, 100))
    ris = st.contro_baseline(cand, 2, a, pavimento_minimo=1.0)
    assert ris["errore_minimo_baseline"] == a["deviazione_standard"] / 10.0
    assert ris["errore_minimo"] == 1.0 and ris["origine_pavimento"] == "pavimento_minimo"
    assert ris["netta"] is False  # 0,4 di differenza su un errore di almeno 1


@pytest.mark.parametrize("valore", [None, -0.1, math.nan, math.inf, True])
def test_contro_baseline_pavimento_minimo_non_valido(valore):
    base = st.baseline_casuale([0.0, 0.1, -0.1, 0.05])
    with pytest.raises(ValueError):
        st.contro_baseline([0.1, 0.2, -0.1, 0.3, 0.0, 0.1], 1, base, pavimento_minimo=valore)


def test_contro_baseline_errore_senza_pavimento_none_sotto_tre_blocchi_e_calcolato_con_a_non_valutabile():
    rng = np.random.default_rng(6)
    base = st.baseline_casuale(list(rng.normal(0.0, 0.1, 50)))
    assert st.contro_baseline(list(rng.normal(0, 1, 8)), 3, base)["errore_candidato_senza_pavimento"] is None
    # (a) non valutabile: il confronto non lo e', ma l'errore del candidato si stima lo stesso
    a = st.baseline_da_trade(list(rng.normal(0, 1, 40)), 15)
    r = list(rng.normal(0.1, 1.0, 60))
    ris = st.contro_baseline(r, 2, a)
    assert ris["valutabile"] is False
    assert ris["errore_candidato_senza_pavimento"] == st._errore_media_corretto(np.asarray(r), 2, 2000, 0)[0]


# ---------------------------------------------------------------------------
# ordina_trade_di_gruppo
# ---------------------------------------------------------------------------


def _t(simbolo, entrata, uscita, r=0.0, pnl=0.0):
    return TradeDiGruppo(simbolo, entrata, uscita, r, pnl)


def test_ordine_fisso_uscita_simbolo_entrata():
    trade = [
        _t("AAVEUSDT", 5, 20),
        _t("1000SHIBUSDT", 7, 20),   # stessa uscita: le cifre vengono prima delle lettere
        _t("ADAUSDT", 1, 10),
        _t("AAVEUSDT", 21, 30),
        _t("ADAUSDT", 12, 20),
        _t("ADAUSDT", 22, 30),
        _t("ZILUSDT", 3, 20),
    ]
    attese = [
        ("ADAUSDT", 1, 10),
        ("1000SHIBUSDT", 7, 20), ("AAVEUSDT", 5, 20), ("ADAUSDT", 12, 20), ("ZILUSDT", 3, 20),
        ("AAVEUSDT", 21, 30), ("ADAUSDT", 22, 30),
    ]
    ordinati = st.ordina_trade_di_gruppo(trade)
    assert [(t.simbolo, t.ts_entrata, t.ts_uscita) for t in ordinati] == attese
    assert "1000SHIBUSDT" < "AAVEUSDT" < "ADAUSDT"


def test_ordine_entrata_a_pari_uscita_e_simbolo():
    # a pari uscita e simbolo decide l'entrata (il motore non lo produce, ma l'ordine resta definito)
    a, b = _t("BTCUSDT", 10, 50), _t("BTCUSDT", 5, 50)
    assert st.ordina_trade_di_gruppo([a, b]) == [b, a]


def test_ordine_invariante_alle_permutazioni():
    rng = random.Random(1)
    trade = []
    for simbolo in ("ETHUSDT", "1INCHUSDT", "XRPUSDT", "ADAUSDT"):
        entrata = 0
        for _ in range(25):
            entrata += rng.randint(1, 5)
            uscita = entrata + rng.randint(0, 6)
            trade.append(_t(simbolo, entrata, uscita, rng.uniform(-1, 2), rng.uniform(-10, 20)))
            entrata = uscita
    riferimento = st.ordina_trade_di_gruppo(trade)
    for _ in range(20):
        rng.shuffle(trade)
        assert st.ordina_trade_di_gruppo(trade) == riferimento


def test_ordine_con_una_moneta_e_quello_del_motore():
    trade = [_t("SOLUSDT", 0, 5), _t("SOLUSDT", 5, 9), _t("SOLUSDT", 12, 30)]
    assert st.ordina_trade_di_gruppo(list(reversed(trade))) == trade


def test_ordine_casi_limite():
    assert st.ordina_trade_di_gruppo([]) == []
    with pytest.raises(ValueError):
        st.ordina_trade_di_gruppo([_t("BTCUSDT", 10, 5)])
    with pytest.raises(ValueError):
        st.ordina_trade_di_gruppo([_t("BTCUSDT", 10, 20), _t("BTCUSDT", 10, 30)])
    with pytest.raises(ValueError):
        st.ordina_trade_di_gruppo([_t("", 1, 2)])
    # stesso istante d'entrata su monete diverse: va bene
    assert len(st.ordina_trade_di_gruppo([_t("BTCUSDT", 10, 20), _t("ETHUSDT", 10, 20)])) == 2


def test_trade_di_gruppo_in_json_e_ritorno():
    t = _t("AAVEUSDT", 1_700_000_000_000, 1_700_003_600_000, 0.25, 2.5)
    assert TradeDiGruppo(**dataclasses.asdict(t)) == t
    with pytest.raises(TypeError):
        sorted([t, t])  # nessun ordine proprio: si ordina solo con ordina_trade_di_gruppo


# ---------------------------------------------------------------------------
# baseline_da_trade_di_gruppo (regole.md, sezione 5, punto 3)
# ---------------------------------------------------------------------------


def _dizionario_a(media, errore, deviazione, n_trade, n_blocchi):
    return {"tipo": "a", "media": media, "errore_standard": errore, "n_trade": n_trade, "n_blocchi": n_blocchi,
            "deviazione_standard": deviazione, "valutabile": n_blocchi >= st.MINIMO_BLOCCHI}


def test_a_di_gruppo_una_moneta_uguale_alla_a_singola():
    rng = np.random.default_rng(21)
    for _ in range(40):
        r_a = list(rng.normal(float(rng.normal(0, 0.1)), float(rng.uniform(0.2, 2.0)), int(rng.integers(30, 400))))
        blocco_a = int(rng.integers(1, 10))
        singola = st.baseline_da_trade(r_a, blocco_a)
        assert singola["valutabile"] is True
        n_cand = int(rng.integers(5, 200))
        gruppo = st.baseline_da_trade_di_gruppo({"ETHUSDT": singola}, {"ETHUSDT": n_cand})
        for chiave in ("tipo", "media", "errore_standard", "deviazione_standard", "valutabile", "n_trade"):
            assert _stesso_valore(gruppo[chiave], singola[chiave]), chiave
        assert gruppo["pesi"] == {"ETHUSDT": 1.0} and gruppo["n_trade_candidato"] == n_cand
        r_cand = list(rng.normal(0.1, 1.0, n_cand))
        blocco_c = int(rng.integers(1, 6))
        assert st.contro_baseline(r_cand, blocco_c, gruppo) == st.contro_baseline(r_cand, blocco_c, singola)
        _uguale_a_prima(st.contro_baseline(r_cand, blocco_c, gruppo),
                        _contro_baseline_prima(r_cand, blocco_c, singola))


def test_radice_del_quadrato_e_esatta():
    # la deviazione combinata con una moneta e' radice(1 · dev · dev): deve tornare dev bit per bit
    rng = np.random.default_rng(22)
    for dev in list(rng.uniform(0, 10, 20000)) + list(rng.lognormal(0, 5, 20000)):
        assert math.sqrt(1.0 * (dev * dev)) == dev


def test_a_di_gruppo_una_moneta_con_pochi_blocchi_differisce_per_scelta():
    # regole.md 5.3: con meno di 3 blocchi interi e_j = dev_j e il confronto si fa; nelle campagne singole
    # la (a) e' non valutabile. Una differenza voluta del testo, non un errore del codice.
    rng = np.random.default_rng(23)
    singola = st.baseline_da_trade(list(rng.normal(0, 1, 40)), 15)
    assert singola["valutabile"] is False and singola["n_blocchi"] == 2
    gruppo = st.baseline_da_trade_di_gruppo({"ETHUSDT": singola}, {"ETHUSDT": 50})
    assert gruppo["valutabile"] is True
    assert gruppo["errore_standard"] == singola["deviazione_standard"]
    assert gruppo["monete_errore_da_deviazione"] == ["ETHUSDT"]
    r = list(rng.normal(0.1, 1.0, 50))
    assert st.contro_baseline(r, 2, singola)["valutabile"] is False
    assert st.contro_baseline(r, 2, gruppo)["valutabile"] is True


def test_a_di_gruppo_due_monete_a_mano():
    # n = 3 e 1 (N = 4, pesi 0,75 e 0,25); A_j = 0,2 e -0,2; e_j = 0,04 e 0,08; dev_j = 1 e 2.
    base = {"AAAUSDT": _dizionario_a(0.2, 0.04, 1.0, 50, 10), "BBBUSDT": _dizionario_a(-0.2, 0.08, 2.0, 40, 5)}
    g = st.baseline_da_trade_di_gruppo(base, {"AAAUSDT": 3, "BBBUSDT": 1})
    assert g["tipo"] == "a" and g["valutabile"] is True and g["motivo"] is None
    assert g["media"] == pytest.approx(0.75 * 0.2 - 0.25 * 0.2)              # 0,1
    assert g["errore_standard"] == pytest.approx(0.75 * 0.04 + 0.25 * 0.08)  # 0,05
    assert g["deviazione_standard"] == pytest.approx(math.sqrt((3 * 1 + 1 * 4) / 4))
    assert g["pesi"] == {"AAAUSDT": 0.75, "BBBUSDT": 0.25}
    assert g["n_trade"] == 90 and g["n_trade_candidato"] == 4 and g["n_monete"] == 2
    # il pavimento della (a) in contro_baseline e' radice(somma n_j dev_j^2) / N = radice(7) / 4
    ris = st.contro_baseline([0.5, -0.1, 0.3, 0.1], 1, g)
    assert ris["errore_minimo"] == pytest.approx(math.sqrt(7) / 4)
    # con la seconda moneta sotto i 3 blocchi il suo e_j e' la sua deviazione standard (2)
    base["BBBUSDT"] = _dizionario_a(-0.2, math.inf, 2.0, 40, 2)
    g = st.baseline_da_trade_di_gruppo(base, {"AAAUSDT": 3, "BBBUSDT": 1})
    assert g["valutabile"] is True and g["monete_errore_da_deviazione"] == ["BBBUSDT"]
    assert g["errore_standard"] == pytest.approx(0.75 * 0.04 + 0.25 * 2.0)
    assert g["per_moneta"]["BBBUSDT"]["errore_usato"] == 2.0


def test_a_di_gruppo_due_monete_vere():
    rng = np.random.default_rng(24)
    a1 = st.baseline_da_trade(list(rng.normal(0.05, 0.9, 300)), 3)
    a2 = st.baseline_da_trade(list(rng.normal(-0.02, 1.4, 180)), 4)
    n1, n2 = 70, 30
    g = st.baseline_da_trade_di_gruppo({"X1USDT": a1, "X2USDT": a2}, {"X1USDT": n1, "X2USDT": n2})
    assert g["media"] == pytest.approx((n1 * a1["media"] + n2 * a2["media"]) / 100, rel=1e-14)
    assert g["errore_standard"] == pytest.approx((n1 * a1["errore_standard"] + n2 * a2["errore_standard"]) / 100,
                                                 rel=1e-14)
    assert g["deviazione_standard"] == pytest.approx(
        math.sqrt((n1 * a1["deviazione_standard"] ** 2 + n2 * a2["deviazione_standard"] ** 2) / 100), rel=1e-14)


def test_a_di_gruppo_non_valutabile_senza_eccezioni():
    base = {"AAAUSDT": _dizionario_a(0.2, 0.04, 1.0, 50, 10), "BBBUSDT": _dizionario_a(0.3, math.inf, 0.0, 1, 0)}
    g = st.baseline_da_trade_di_gruppo(base, {"AAAUSDT": 3, "BBBUSDT": 1})
    assert g["valutabile"] is False and math.isinf(g["errore_standard"])
    assert g["monete_con_meno_di_2_trade"] == ["BBBUSDT"] and "BBBUSDT" in g["motivo"]
    assert g["media"] == pytest.approx(0.75 * 0.2 + 0.25 * 0.3)
    r = [0.5, -0.1, 0.3, 0.1, 0.2, 0.0]
    ris = st.contro_baseline(r, 1, g)
    assert ris["valutabile"] is False and ris["netta"] is False and ris["t"] == -math.inf and ris["p_value"] == 1.0
    # una (a) senza trade (None): numero e deviazione non esistono, il confronto e' non valutabile e non alza
    base["BBBUSDT"] = None
    g = st.baseline_da_trade_di_gruppo(base, {"AAAUSDT": 3, "BBBUSDT": 1})
    assert g["valutabile"] is False and math.isnan(g["media"]) and math.isnan(g["deviazione_standard"])
    assert g["per_moneta"]["BBBUSDT"] is None
    ris = st.contro_baseline(r, 1, g)
    assert ris["valutabile"] is False and ris["netta"] is False and math.isnan(ris["differenza"])
    assert ris["errore_candidato_senza_pavimento"] is not None  # 6 blocchi: l'errore del candidato si stima
    ris = st.contro_baseline(r, 1, g, pavimento_minimo=0.3)
    assert ris["valutabile"] is False and ris["origine_pavimento"] == "pavimento_minimo"


def test_a_di_gruppo_monete_senza_trade_e_monete_mancanti():
    a = _dizionario_a(0.2, 0.04, 1.0, 50, 10)
    # una moneta con n_j = 0 pesa zero: il suo dizionario si ignora, anche se c'e'
    g1 = st.baseline_da_trade_di_gruppo({"AAAUSDT": a}, {"AAAUSDT": 5, "BBBUSDT": 0})
    g2 = st.baseline_da_trade_di_gruppo({"AAAUSDT": a, "BBBUSDT": _dizionario_a(9.0, 1.0, 1.0, 9, 9)},
                                        {"AAAUSDT": 5, "BBBUSDT": 0})
    assert g1 == g2 and g1["n_monete"] == 1 and g1["media"] == 0.2
    with pytest.raises(ValueError):  # manca la (a) di una moneta con trade
        st.baseline_da_trade_di_gruppo({"AAAUSDT": a}, {"AAAUSDT": 5, "BBBUSDT": 2})
    with pytest.raises(ValueError):  # moneta sconosciuta
        st.baseline_da_trade_di_gruppo({"AAAUSDT": a, "CCCUSDT": a}, {"AAAUSDT": 5})
    with pytest.raises(ValueError):  # N = 0
        st.baseline_da_trade_di_gruppo({}, {"AAAUSDT": 0})
    with pytest.raises(ValueError):  # n_j negativo
        st.baseline_da_trade_di_gruppo({"AAAUSDT": a}, {"AAAUSDT": -1})
    with pytest.raises(ValueError):  # non e' una (a)
        st.baseline_da_trade_di_gruppo({"AAAUSDT": st.baseline_casuale([0.1, 0.2])}, {"AAAUSDT": 5})


def test_a_di_gruppo_invariante_all_ordine_delle_monete():
    rng = np.random.default_rng(25)
    simboli = ["ZRXUSDT", "1INCHUSDT", "AAVEUSDT", "ETCUSDT", "MKRUSDT", "ADAUSDT"]
    base = {s: st.baseline_da_trade(list(rng.normal(0, 1, int(rng.integers(20, 200)))), int(rng.integers(1, 30)))
            for s in simboli}
    n = {s: int(rng.integers(0, 80)) for s in simboli}
    riferimento = st.baseline_da_trade_di_gruppo(base, n)
    rnd = random.Random(2)
    for _ in range(10):
        ordine = simboli[:]
        rnd.shuffle(ordine)
        risultato = st.baseline_da_trade_di_gruppo({s: base[s] for s in ordine}, {s: n[s] for s in reversed(ordine)})
        assert risultato == riferimento
        assert list(risultato["pesi"]) == sorted(risultato["pesi"])


# ---------------------------------------------------------------------------
# baseline_casuale_di_gruppo (regole.md, sezione 5, punto 4)
# ---------------------------------------------------------------------------


def _con_vuote(valori, quota, rng):
    return [None if rng.random() < quota else float(v) for v in valori]


def test_b_di_gruppo_una_moneta_uguale_alla_b_singola():
    rng = np.random.default_rng(31)
    for _ in range(40):
        lista = _con_vuote(rng.normal(float(rng.normal(0, 0.1)), float(rng.uniform(0.01, 0.4)), 200),
                           float(rng.uniform(0, 0.3)), rng)
        singola = st.baseline_casuale([x for x in lista if x is not None])
        n_cand = int(rng.integers(10, 300))
        gruppo = st.baseline_casuale_di_gruppo({"SOLUSDT": lista}, {"SOLUSDT": n_cand})
        for chiave in ("tipo", "media", "errore_standard", "errore_minimo_candidato", "n_simulazioni",
                       "percentile_90"):
            assert _stesso_valore(gruppo[chiave], singola[chiave]), chiave
        assert np.array_equal(gruppo["valori"], singola["valori"])
        assert gruppo["valutabile"] is True and gruppo["b_per_moneta"] == {"SOLUSDT": singola["media"]}
        assert gruppo["m_mancanti"] == lista.count(None) and gruppo["m_parziali"] == 0
        r = list(rng.normal(0.05, 1.0, n_cand))
        blocco = int(rng.integers(1, 8))
        assert st.contro_baseline(r, blocco, gruppo) == st.contro_baseline(r, blocco, singola)
        _uguale_a_prima(st.contro_baseline(r, blocco, gruppo), _contro_baseline_prima(r, blocco, singola))


def _serie_casuale(n, seme):
    rng = np.random.default_rng(seme)
    prezzo = 100.0
    out = []
    for i in range(n):
        o = prezzo
        c = o * math.exp(float(rng.normal(0, 0.01)))
        h, l = max(o, c) * (1 + float(rng.uniform(0, 0.005))), min(o, c) * (1 - float(rng.uniform(0, 0.005)))
        out.append(Candela(ts=i * 3_600_000, open=o, high=h, low=l, close=c, volume=1.0,
                           close_ts=i * 3_600_000 + 3_599_999))
        prezzo = c
    return out


def _crea_casuale(direzione="long", durata=4):
    def crea(ingressi):
        stato = {"entrata_i": None}

        def strategia(storia, posizione):
            i = len(storia) - 1
            if posizione is None:
                stato["entrata_i"] = None
                if i in ingressi:
                    c = storia[-1].close
                    return Segnale(direzione, stop=c * (0.97 if direzione == "long" else 1.03),
                                   target=c * (1.02 if direzione == "long" else 0.98))
                return None
            if stato["entrata_i"] is None:
                stato["entrata_i"] = i
            if i - stato["entrata_i"] >= durata - 1:
                return "chiudi"
            return None
        return strategia
    return crea


def test_b_di_gruppo_una_moneta_con_il_motore_vero():
    # il percorso intero: motore.simula_baseline_casuale (campagna singola) e la (b) di gruppo con una moneta
    candele = _serie_casuale(900, 41)
    singola = motore.simula_baseline_casuale(candele, _crea_casuale(), 60, 6, Parametri(), n_simulazioni=40,
                                             primo_seme=1000 * 7)
    per_seme = singola["r_medio_per_seme"]
    assert len(per_seme) == 40
    gruppo = st.baseline_casuale_di_gruppo({"ADAUSDT": per_seme}, {"ADAUSDT": 60})
    for chiave in ("media", "errore_standard", "errore_minimo_candidato", "n_simulazioni", "percentile_90"):
        assert _stesso_valore(gruppo[chiave], singola[chiave]), chiave
    assert np.array_equal(gruppo["valori"], singola["valori"])
    r = list(np.random.default_rng(42).normal(0.1, 1.0, 60))
    assert st.contro_baseline(r, 3, gruppo) == st.contro_baseline(r, 3, singola)


def test_b_di_gruppo_due_monete_a_mano():
    # n = 1 e 3; m_A = [0,1; vuota; 0,3; vuota], m_B = [0,2; 0,4; vuota; vuota]
    # M(0) = (1·0,1 + 3·0,2) / 4 = 0,175; M(1) = 0,4 (solo B); M(2) = 0,3 (solo A); M(3) non esiste.
    liste = {"AAAUSDT": [0.1, None, 0.3, None], "BBBUSDT": [0.2, 0.4, None, None]}
    g = st.baseline_casuale_di_gruppo(liste, {"AAAUSDT": 1, "BBBUSDT": 3})
    attese = [0.175, 0.4, 0.3]
    assert g["tipo"] == "b" and g["valutabile"] is True and g["motivo"] is None
    assert list(g["valori"]) == pytest.approx(attese)
    assert g["media"] == pytest.approx(0.875 / 3)
    assert g["errore_minimo_candidato"] == pytest.approx(float(np.std(attese, ddof=1)))
    assert g["errore_standard"] == pytest.approx(float(np.std(attese, ddof=1)) / math.sqrt(3))
    assert g["percentile_90"] == pytest.approx(float(np.percentile(attese, 90)))
    assert g["n_simulazioni"] == 3 and g["m_mancanti"] == 1 and g["m_parziali"] == 2
    assert g["b_per_moneta"] == pytest.approx({"AAAUSDT": 0.2, "BBBUSDT": 0.3})
    assert g["pesi"] == {"AAAUSDT": 0.25, "BBBUSDT": 0.75}
    assert g["simulazioni_per_moneta"] == 4
    assert g["simulazioni_con_trade_per_moneta"] == {"AAAUSDT": 2, "BBBUSDT": 2}
    # contro_baseline lo usa com'e': pavimento = deviazione standard delle M(s)
    ris = st.contro_baseline([0.5, -0.1, 0.3, 0.1, 0.2, 0.4], 2, g)
    assert ris["valutabile"] is True and ris["errore_minimo"] == g["errore_minimo_candidato"]
    # il percentile del candidato fra le M(s)
    assert st.percentile_del_candidato(0.35, g["valori"]) == pytest.approx(200 / 3)


def test_b_di_gruppo_pesi_del_candidato_non_delle_simulazioni():
    # una moneta con molti trade del candidato pesa di piu' anche se le sue simulazioni hanno meno trade
    g = st.baseline_casuale_di_gruppo({"AAAUSDT": [1.0, 1.0], "BBBUSDT": [0.0, 0.0]}, {"AAAUSDT": 9, "BBBUSDT": 1})
    assert list(g["valori"]) == pytest.approx([0.9, 0.9])


def test_b_di_gruppo_non_valutabile_senza_eccezioni():
    n = {"AAAUSDT": 2, "BBBUSDT": 5}
    r = [0.5, -0.1, 0.3, 0.1, 0.2, 0.4, 0.0]
    # una moneta con una sola simulazione con trade
    g = st.baseline_casuale_di_gruppo({"AAAUSDT": [0.1, None, None], "BBBUSDT": [0.2, 0.1, 0.0]}, n)
    assert g["valutabile"] is False and math.isinf(g["errore_standard"])
    assert g["monete_con_meno_di_2_simulazioni"] == ["AAAUSDT"]
    assert st.contro_baseline(r, 1, g)["valutabile"] is False
    # gli ingressi non entrano su una moneta (None al posto della lista)
    g = st.baseline_casuale_di_gruppo({"AAAUSDT": None, "BBBUSDT": [0.2, 0.1, 0.0]}, n)
    assert g["valutabile"] is False and g["monete_senza_ingressi"] == ["AAAUSDT"]
    assert g["b_per_moneta"]["AAAUSDT"] is None
    assert st.contro_baseline(r, 1, g)["valutabile"] is False
    # una sola M(s): numero c'e', pavimento no
    g = st.baseline_casuale_di_gruppo({"AAAUSDT": [0.1, None, None], "BBBUSDT": [0.2, None, None]},
                                      {"AAAUSDT": 1, "BBBUSDT": 1})
    assert g["valutabile"] is False and g["n_simulazioni"] == 1 and math.isnan(g["errore_minimo_candidato"])
    ris = st.contro_baseline(r, 1, g)
    assert ris["valutabile"] is False and ris["p_value"] == 1.0
    ris = st.contro_baseline(r, 1, g, pavimento_minimo=0.2)  # con il pavimento delle sfasate: idem, senza eccezioni
    assert ris["valutabile"] is False and ris["errore_minimo"] == 0.2
    assert ris["origine_pavimento"] == "pavimento_minimo"
    # nessuna M(s): neanche il numero
    g = st.baseline_casuale_di_gruppo({"AAAUSDT": [None, None], "BBBUSDT": [None, None]},
                                      {"AAAUSDT": 1, "BBBUSDT": 1})
    assert g["valutabile"] is False and math.isnan(g["media"]) and g["m_mancanti"] == 2
    ris = st.contro_baseline(r, 1, g, pavimento_minimo=0.1)
    assert ris["valutabile"] is False and ris["netta"] is False and math.isnan(ris["differenza"])


def test_b_di_gruppo_errori_nei_dati():
    with pytest.raises(ValueError):  # simulazioni di numero diverso
        st.baseline_casuale_di_gruppo({"AAAUSDT": [0.1, 0.2], "BBBUSDT": [0.1, 0.2, 0.3]},
                                      {"AAAUSDT": 1, "BBBUSDT": 1})
    with pytest.raises(ValueError):  # NaN invece di None
        st.baseline_casuale_di_gruppo({"AAAUSDT": [0.1, math.nan, 0.2]}, {"AAAUSDT": 1})
    with pytest.raises(ValueError):  # manca una moneta con trade
        st.baseline_casuale_di_gruppo({"AAAUSDT": [0.1, 0.2]}, {"AAAUSDT": 1, "BBBUSDT": 1})
    # una moneta con n_j = 0 non ha (b): la sua lista si ignora, anche di lunghezza diversa
    g = st.baseline_casuale_di_gruppo({"AAAUSDT": [0.1, 0.2], "BBBUSDT": [9.0]}, {"AAAUSDT": 1, "BBBUSDT": 0})
    assert g["n_monete"] == 1 and list(g["valori"]) == [0.1, 0.2]


def test_b_di_gruppo_invariante_all_ordine_delle_monete():
    rng = np.random.default_rng(33)
    simboli = ["ZRXUSDT", "1INCHUSDT", "AAVEUSDT", "ETCUSDT", "MKRUSDT"]
    liste = {s: _con_vuote(rng.normal(0, 0.2, 200), 0.2, rng) for s in simboli}
    n = {s: int(rng.integers(1, 90)) for s in simboli}
    riferimento = st.baseline_casuale_di_gruppo(liste, n)
    rnd = random.Random(3)
    for _ in range(10):
        ordine = simboli[:]
        rnd.shuffle(ordine)
        risultato = st.baseline_casuale_di_gruppo({s: liste[s] for s in ordine}, {s: n[s] for s in reversed(ordine)})
        assert np.array_equal(risultato["valori"], riferimento["valori"])
        assert {k: v for k, v in risultato.items() if k != "valori"} == \
               {k: v for k, v in riferimento.items() if k != "valori"}


# ---------------------------------------------------------------------------
# pavimento_sfasamento (regole.md, sezione 5, punto 5)
# ---------------------------------------------------------------------------


def test_pavimento_sfasamento_a_mano():
    # M' = 0,1 / 0,3 / vuota / 0,2 con n' = 10, 40, 0, 10 e N = 40: media delle M' 0,2;
    # valori (-0,1)·radice(1/4) = -0,05, 0,1·1 = 0,1, 0·radice(1/4) = 0
    # deviazione standard (ddof 1) di (-1/20, 1/10, 0) = radice(7/1200)
    p = st.pavimento_sfasamento([0.1, 0.3, None, 0.2], [10, 40, 0, 10], 40)
    assert p["valutabile"] is True
    assert p["pavimento"] == pytest.approx(math.sqrt(7 / 1200))
    assert p["media_r_sfasate"] == pytest.approx(0.2)
    assert (p["sfasate"], p["sfasate_con_trade"], p["sfasate_senza_trade"]) == (4, 3, 1)
    assert (p["quota_trade_minima"], p["quota_trade_mediana"], p["quota_trade_massima"]) == (0.0, 0.25, 1.0)


def test_pavimento_sfasamento_senza_trade_saltati_e_la_deviazione_delle_m():
    rng = np.random.default_rng(51)
    m = list(rng.normal(0, 0.1, 200))
    p = st.pavimento_sfasamento(m, [57] * 200, 57)
    assert p["pavimento"] == pytest.approx(float(np.std(m, ddof=1)), rel=1e-12)


def test_pavimento_sfasamento_non_valutabile_e_errori():
    p = st.pavimento_sfasamento([0.1, None, None], [5, 0, 0], 10)
    assert p["pavimento"] is None and p["valutabile"] is False and p["media_r_sfasate"] == 0.1
    p = st.pavimento_sfasamento([], [], 10)
    assert p["pavimento"] is None and p["sfasate"] == 0 and p["quota_trade_mediana"] is None
    with pytest.raises(ValueError):  # R medio senza trade
        st.pavimento_sfasamento([0.1, 0.2, 0.0], [5, 5, 0], 10)
    with pytest.raises(ValueError):  # trade senza R medio
        st.pavimento_sfasamento([0.1, 0.2, None], [5, 5, 3], 10)
    with pytest.raises(ValueError):  # lunghezze diverse
        st.pavimento_sfasamento([0.1, 0.2], [5], 10)
    with pytest.raises(ValueError):  # N = 0
        st.pavimento_sfasamento([0.1, 0.2], [5, 5], 0)
    with pytest.raises(ValueError):
        st.pavimento_sfasamento([0.1, math.nan], [5, 5], 10)
    # il pavimento non valutabile non entra in contro_baseline
    with pytest.raises(ValueError):
        st.contro_baseline([0.1] * 10, 1, st.baseline_casuale([0.0, 0.1]), pavimento_minimo=p["pavimento"])


# ---------------------------------------------------------------------------
# griglia_sfasamenti (regole.md, sezione 5, punto 5, e sezione 9, punto 3)
# ---------------------------------------------------------------------------


def test_griglia_vault_1d_mille_sfasate():
    # vault 2024-01-01 -> 2026-09-30 a 1d: L = 366 + 365 + 273 = 1004 barre; margine 30 giorni = 30 barre.
    # L - 2·30 + 1 = 945 < 1000: tutti gli interi da 30 a 974, una volta ciascuno.
    giorni = (datetime(2026, 10, 1) - datetime(2024, 1, 1)).days
    assert giorni == 1004
    g = st.griglia_sfasamenti(1004, 30, 1000)
    assert g["tutti_gli_interi"] is True and g["numero"] == 945
    assert g["sfasamenti"] == list(range(30, 975)) and g["margine"] == 30


def test_griglia_formula_con_le_meta_verso_l_alto():
    # L = 7, margine 1, S = 3: d_s = 1 + arrotondamento di s · 5 / 2 -> 1, 1 + 3 (2,5 -> 3, non 2), 6
    assert st.griglia_sfasamenti(7, 1, 3)["sfasamenti"] == [1, 4, 6]
    assert round(2.5) == 2  # l'arrotondamento «al pari» di Python darebbe 3 invece di 4


def test_griglia_validazione_1h_duecento_sfasate():
    # validazione 2023-01-17 -> 2023-12-31 a 1h: L = 349 · 24; margine 30 giorni = 720 barre
    L, margine, S = 349 * 24, 720, 200
    g = st.griglia_sfasamenti(L, margine, S)
    attesi = [margine + math.floor(Fraction(s * (L - 2 * margine), S - 1) + Fraction(1, 2)) for s in range(S)]
    assert g["sfasamenti"] == attesi and g["tutti_gli_interi"] is False and g["numero"] == 200
    assert g["sfasamenti"][0] == margine and g["sfasamenti"][-1] == L - margine
    assert all(b > a for a, b in zip(g["sfasamenti"], g["sfasamenti"][1:]))


def test_griglia_margine_al_massimo_un_quarto_e_casi_limite():
    g = st.griglia_sfasamenti(1004, 300, 1000)
    assert g["margine"] == 251 and g["margine_richiesto"] == 300
    assert g["sfasamenti"] == list(range(251, 754))
    assert st.griglia_sfasamenti(100, 10, 2)["sfasamenti"] == [10, 90]
    # al confine L - 2·margine + 1 == S la formula da' gia' tutti gli interi
    g = st.griglia_sfasamenti(100, 10, 81)
    assert g["tutti_gli_interi"] is False and g["sfasamenti"] == list(range(10, 91))
    g = st.griglia_sfasamenti(100, 10, 82)
    assert g["tutti_gli_interi"] is True and g["sfasamenti"] == list(range(10, 91))
    for argomenti in ((100, 10, 1), (3, 1, 10), (0, 1, 10), (100, -1, 10), (100, 0, 10), (True, 1, 10)):
        with pytest.raises(ValueError):
            st.griglia_sfasamenti(*argomenti)


# ---------------------------------------------------------------------------
# effetto_grappolo (regole.md, sezione 5, punto 9)
# ---------------------------------------------------------------------------


def test_effetto_grappolo_a_mano():
    # errore 0,1, R = 1, -1, 1, -1: varianza (ddof 1) 4/3, N = 4 -> 0,01 · 4 / (4/3) = 0,03
    assert st.effetto_grappolo(0.1, [1.0, -1.0, 1.0, -1.0]) == pytest.approx(0.03)


def test_effetto_grappolo_vicino_a_uno_con_trade_indipendenti():
    r = list(np.random.default_rng(61).normal(0.0, 1.0, 2000))
    base = st.baseline_casuale(list(np.random.default_rng(62).normal(0, 0.02, 200)))
    errore = st.contro_baseline(r, 1, base)["errore_candidato_senza_pavimento"]
    assert st.effetto_grappolo(errore, r) == pytest.approx(1.0, abs=0.1)


def test_effetto_grappolo_casi_limite():
    assert st.effetto_grappolo(None, [0.1, 0.2]) is None
    assert st.effetto_grappolo(math.inf, [0.1, 0.2]) is None
    assert st.effetto_grappolo(0.1, [0.1]) is None
    assert st.effetto_grappolo(0.1, [0.2, 0.2, 0.2]) is None
    with pytest.raises(ValueError):
        st.effetto_grappolo(-0.1, [0.1, 0.2])
    with pytest.raises(ValueError):
        st.effetto_grappolo(math.nan, [0.1, 0.2])


# ---------------------------------------------------------------------------
# estremi_di_gruppo (regole.md, sezione 6, punto 2.5)
# ---------------------------------------------------------------------------


def _ms(anno, mese, giorno, ora=0):
    return int(datetime(anno, mese, giorno, ora, tzinfo=timezone.utc).timestamp() * 1000)


def _trade_estremi():
    return [
        _t("AAAUSDT", _ms(2022, 3, 1, 0), _ms(2022, 3, 1, 10), 2.0),
        _t("AAAUSDT", _ms(2022, 3, 2, 0), _ms(2022, 3, 2, 10), -0.5),
        _t("BBBUSDT", _ms(2022, 3, 1, 0), _ms(2022, 3, 1, 12), 0.5),
        _t("BBBUSDT", _ms(2022, 3, 3, 0), _ms(2022, 3, 3, 10), 0.3),
        _t("CCCUSDT", _ms(2022, 3, 2, 0), _ms(2022, 3, 2, 12), 0.4),
        _t("CCCUSDT", _ms(2022, 3, 3, 0), _ms(2022, 3, 3, 12), -0.2),
    ]


B_MONETE = {"AAAUSDT": 0.1, "BBBUSDT": 0.2, "CCCUSDT": 0.0}


def test_estremi_a_mano():
    e = st.estremi_di_gruppo(_trade_estremi(), 0.05, B_MONETE, trade_migliori=1, giorni_migliori=1,
                             monete_migliori=1)
    # trade: via il 2,0 -> restano 0,5 su 5 trade, R medio 0,1 > B = 0,05
    p = e["senza_trade_migliori"]
    assert p["superata"] is True and p["trade_tolti"] == 1 and p["trade_rimasti"] == 5
    assert p["r_medio"] == pytest.approx(0.1) and p["b"] == 0.05
    # giorni: somme 1 marzo 2,5, 2 marzo -0,1, 3 marzo 0,1 -> via il 1 marzo; restano -0,5, 0,4, 0,3, -0,2
    # (R medio 0) e la B ripesata e' (1·0,1 + 1·0,2 + 2·0) / 4 = 0,075: non superata
    p = e["senza_giorni_migliori"]
    assert p["giorni_tolti"] == ["2022-03-01"] and p["somme_r_giorni_tolti"] == [2.5]
    assert p["trade_tolti"] == 2 and p["trade_rimasti"] == 4
    assert p["r_medio"] == pytest.approx(0.0, abs=1e-15) and p["b_ripesata"] == pytest.approx(0.075)
    assert p["superata"] is False
    # monete: somme A 1,5, B 0,8, C 0,2 -> via A; restano 0,5, 0,3, 0,4, -0,2 (R medio 0,25)
    # e la B ripesata e' (2·0,2 + 2·0) / 4 = 0,1: superata
    p = e["senza_monete_migliori"]
    assert p["monete_tolte"] == ["AAAUSDT"] and p["somme_r_monete_tolte"] == [1.5]
    assert p["r_medio"] == pytest.approx(0.25) and p["b_ripesata"] == pytest.approx(0.1)
    assert p["superata"] is True
    assert e["tutte_superate"] is False


def test_estremi_senza_trade_rimasti_non_superate():
    e = st.estremi_di_gruppo(_trade_estremi(), -5.0, B_MONETE)  # 30 trade, 3 giorni, 3 monete: via tutto
    for chiave in ("senza_trade_migliori", "senza_giorni_migliori", "senza_monete_migliori"):
        assert e[chiave]["superata"] is False and e[chiave]["trade_rimasti"] == 0 and e[chiave]["r_medio"] is None
    assert e["senza_giorni_migliori"]["b_ripesata"] is None
    assert e["tutte_superate"] is False


def test_estremi_con_una_moneta_le_tre_prove():
    # con una moneta sola la B ripesata e' b_j (= B) e la prova sulle monete toglie tutto
    trade = [_t("ETHUSDT", _ms(2022, 1, g), _ms(2022, 1, g, 5), r)
             for g, r in zip(range(1, 11), [1.0, 0.2, 0.1, -0.1, 0.3, 0.0, 0.2, 0.1, 0.4, -0.2])]
    e = st.estremi_di_gruppo(trade, 0.0, {"ETHUSDT": 0.0}, trade_migliori=3, giorni_migliori=3)
    # via 1,0, 0,4 e 0,3: restano 0,2, 0,1, -0,1, 0,0, 0,2, 0,1, -0,2
    assert e["senza_trade_migliori"]["r_medio"] == pytest.approx(0.3 / 7)
    assert e["senza_giorni_migliori"]["b_ripesata"] == 0.0
    assert e["senza_giorni_migliori"]["giorni_tolti"] == ["2022-01-01", "2022-01-09", "2022-01-05"]
    assert e["senza_monete_migliori"]["trade_rimasti"] == 0 and e["senza_monete_migliori"]["superata"] is False


def test_estremi_parita_fra_giorni_e_fra_monete():
    trade = [
        _t("BBBUSDT", _ms(2022, 5, 2), _ms(2022, 5, 2, 3), 1.0),
        _t("AAAUSDT", _ms(2022, 5, 1), _ms(2022, 5, 1, 3), 1.0),
        _t("CCCUSDT", _ms(2022, 5, 3), _ms(2022, 5, 3, 3), 0.1),
    ]
    e = st.estremi_di_gruppo(trade, 0.0, {"AAAUSDT": 0.0, "BBBUSDT": 0.0, "CCCUSDT": 0.0},
                             trade_migliori=1, giorni_migliori=1, monete_migliori=1)
    assert e["senza_giorni_migliori"]["giorni_tolti"] == ["2022-05-01"]   # a pari somma il giorno piu' vecchio
    assert e["senza_monete_migliori"]["monete_tolte"] == ["AAAUSDT"]      # a pari somma l'ordine dei caratteri
    assert e["senza_trade_migliori"]["r_medio"] == pytest.approx(0.55)    # quale 1,0 si tolga non conta


def test_estremi_giorno_utc_dell_uscita():
    # un trade che esce alle 23:59:59.999 appartiene a quel giorno; uno che esce a mezzanotte al giorno dopo
    trade = [
        _t("AAAUSDT", _ms(2022, 6, 1), _ms(2022, 6, 2) - 1, 1.0),
        _t("BBBUSDT", _ms(2022, 6, 1), _ms(2022, 6, 2), 0.5),
        _t("CCCUSDT", _ms(2022, 6, 2), _ms(2022, 6, 2, 5), 0.6),
    ]
    e = st.estremi_di_gruppo(trade, 0.0, {"AAAUSDT": 0.0, "BBBUSDT": 0.0, "CCCUSDT": 0.0}, giorni_migliori=1)
    assert e["senza_giorni_migliori"]["giorni_tolti"] == ["2022-06-02"]   # 0,5 + 0,6 = 1,1 > 1,0
    assert e["senza_giorni_migliori"]["trade_rimasti"] == 1


def test_estremi_invarianti_all_ordine():
    rng = random.Random(71)
    trade = []
    b = {}
    for simbolo in ("ZRXUSDT", "1INCHUSDT", "AAVEUSDT", "ETCUSDT", "MKRUSDT", "ADAUSDT"):
        b[simbolo] = rng.uniform(-0.1, 0.1)
        entrata = _ms(2021, 1, 1)
        for _ in range(40):
            entrata += rng.randint(1, 40) * 3_600_000
            uscita = entrata + rng.randint(1, 30) * 3_600_000
            trade.append(_t(simbolo, entrata, uscita, rng.gauss(0.05, 1.0)))
            entrata = uscita
    riferimento = st.estremi_di_gruppo(trade, 0.01, b)
    for _ in range(10):
        rng.shuffle(trade)
        chiavi = list(b)
        rng.shuffle(chiavi)
        assert st.estremi_di_gruppo(trade, 0.01, {k: b[k] for k in chiavi}) == riferimento


def test_estremi_errori():
    with pytest.raises(ValueError):
        st.estremi_di_gruppo([], 0.0, {})
    with pytest.raises(ValueError):  # manca la b_j di una moneta con trade rimasti
        st.estremi_di_gruppo(_trade_estremi(), 0.0, {"AAAUSDT": 0.1, "BBBUSDT": 0.2}, 1, 1, 1)
    with pytest.raises(ValueError):  # b_j None (la (b) di quella moneta non aveva simulazioni con trade)
        st.estremi_di_gruppo(_trade_estremi(), 0.0, dict(B_MONETE, CCCUSDT=None), 1, 1, 1)
    with pytest.raises(ValueError):
        st.estremi_di_gruppo(_trade_estremi(), math.nan, B_MONETE)
    with pytest.raises(ValueError):
        st.estremi_di_gruppo(_trade_estremi(), 0.0, B_MONETE, trade_migliori=-1)
