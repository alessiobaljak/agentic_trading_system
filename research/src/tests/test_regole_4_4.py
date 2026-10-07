"""Le due regole nuove della versione 4.4 del protocollo (sezione 8).

1. La stima dei trade e' una sola: ``motore.conta_trade``, il numero di trade che
   il motore produce con le regole complete della variante sui soli dati di
   costruzione. Restituisce solo conteggi, mai risultati, e rifiuta le candele
   oltre la fine della costruzione.
2. «Nettamente» ha una sola lettura: ``statistica.batte_nettamente``, la media del
   candidato contro UN numero di baseline, con l'errore standard della
   differenza. Per la baseline (b) quel numero e' la media delle simulazioni
   casuali (``baseline_casuale``), il cui errore e' piccolo; per la (a) la media
   dei suoi trade con il suo errore (``baseline_da_trade``). Il p-value
   dell'asticella (``p_value_vs_baseline``) usa la stessa lettura.
"""
import math

import numpy as np
import pytest

from research.src import motore
from research.src import statistica as st
from research.src.motore import Candela, Parametri, Segnale

ORA = 3_600_000


def candela(i: int, o: float, h: float, l: float, c: float) -> Candela:
    return Candela(ts=i * ORA, open=o, high=h, low=l, close=c, volume=1.0, close_ts=i * ORA + ORA - 1)


def serie_a_dente(n: int):
    """Prezzo che sale di 1 per 5 barre e poi scende di 1 per 5 barre, all'infinito."""
    out = []
    p = 100.0
    for i in range(n):
        passo = 1.0 if (i // 5) % 2 == 0 else -1.0
        o = p
        c = p + passo
        out.append(candela(i, o, max(o, c) + 0.2, min(o, c) - 0.2, c))
        p = c
    return out


def strategia_ogni_k(k: int, direzione: str, durata: int):
    """Entra ogni k barre (se libera) con stop largo e chiude dopo ``durata`` barre."""

    stato = {"entrata_i": None}

    def strategia(storia, posizione):
        i = len(storia) - 1
        if posizione is None:
            stato["entrata_i"] = None
            if i % k == 0:
                prezzo = storia[-1].close
                stop = prezzo * (0.5 if direzione == "long" else 1.5)
                return Segnale(direzione, stop=stop)
            return None
        if stato["entrata_i"] is None:
            stato["entrata_i"] = i
        if i - stato["entrata_i"] >= durata - 1:
            return "chiudi"
        return None

    return strategia


# ---------------------------------------------------------------------------
# conta_trade
# ---------------------------------------------------------------------------


def test_conta_trade_uguale_al_numero_di_trade_del_motore():
    candele = serie_a_dente(200)
    fine = candele[-1].close_ts
    conteggio = motore.conta_trade(candele, lambda: strategia_ogni_k(10, "long", 3), fine, Parametri())
    vero = motore.esegui(candele, None, None, [], strategia_ogni_k(10, "long", 3), Parametri())
    assert conteggio["trade"] == len(vero.trades) > 0
    assert conteggio["long"] == conteggio["trade"] and conteggio["short"] == 0
    assert conteggio["barre"] == 200


def test_conta_trade_la_durata_la_decide_l_uscita_non_una_stima():
    # Segnale ogni barra: con uscita dopo 1 barra i trade sono molti di piu' che
    # con uscita dopo 9, perche' la posizione occupa il motore. Nessuna
    # «occupazione» da dichiarare: la conta il motore.
    candele = serie_a_dente(300)
    fine = candele[-1].close_ts
    corta = motore.conta_trade(candele, lambda: strategia_ogni_k(1, "short", 1), fine, Parametri())
    lunga = motore.conta_trade(candele, lambda: strategia_ogni_k(1, "short", 9), fine, Parametri())
    assert corta["short"] > 2 * lunga["short"] > 0


def test_conta_trade_restituisce_solo_conteggi_mai_risultati():
    candele = serie_a_dente(120)
    c = motore.conta_trade(candele, lambda: strategia_ogni_k(7, "long", 2), candele[-1].close_ts, Parametri())
    assert set(c) == {"trade", "long", "short", "segnali_non_validi", "segnali_senza_barra", "barre"}
    assert all(isinstance(v, int) for v in c.values())


def test_conta_trade_rifiuta_le_candele_oltre_la_fine_della_costruzione():
    candele = serie_a_dente(50)
    fine = candele[39].close_ts  # la costruzione finisce alla barra 39
    with pytest.raises(ValueError, match="costruzione"):
        motore.conta_trade(candele, lambda: strategia_ogni_k(5, "long", 2), fine, Parametri())
    ok = motore.conta_trade(candele[:40], lambda: strategia_ogni_k(5, "long", 2), fine, Parametri())
    assert ok["barre"] == 40


def test_conta_trade_usa_gli_stessi_costi_del_test_vero():
    # Con lo slippage un target vicinissimo all'apertura diventa «dalla parte
    # sbagliata» del riempimento: il test vero scarta il segnale. Il conteggio usa
    # gli stessi Parametri, quindi coincide con il test vero anche qui.
    candele = serie_a_dente(300)
    fine = candele[-1].close_ts

    def crea():
        def strategia(storia, posizione):
            if posizione is None and len(storia) % 4 == 0:
                c = storia[-1].close
                return Segnale("long", stop=c * 0.9, target=c * 1.00005)
            return None
        return strategia

    con_costi = Parametri(slippage_per_lato=0.001)
    conteggio = motore.conta_trade(candele, crea, fine, con_costi)
    vero = motore.esegui(candele, None, None, [], crea(), con_costi)
    assert conteggio["trade"] == len(vero.trades)
    assert conteggio["segnali_non_validi"] == vero.n_segnali_non_validi > 0


def test_conta_trade_vuole_la_fabbrica_non_la_strategia():
    candele = serie_a_dente(50)
    with pytest.raises(TypeError, match="FUNZIONE"):
        motore.conta_trade(candele, strategia_ogni_k(5, "long", 2), candele[-1].close_ts, Parametri())


def test_conta_trade_lo_stato_della_strategia_non_passa_al_test():
    # Una strategia con un contatore interno: contata e poi testata con una
    # istanza NUOVA dalla stessa fabbrica, da' gli stessi trade di una mai contata.
    candele = serie_a_dente(400)
    fine = candele[-1].close_ts

    def crea():
        stato = {"barre": 0}

        def strategia(storia, posizione):
            stato["barre"] += 1
            if posizione is None and stato["barre"] % 7 == 0:
                return Segnale("long", stop=storia[-1].close * 0.5)
            if posizione is not None and stato["barre"] % 7 == 3:
                return "chiudi"
            return None
        return strategia

    c = motore.conta_trade(candele, crea, fine, Parametri())
    vero = motore.esegui(candele, None, None, [], crea(), Parametri())
    assert c["trade"] == len(vero.trades) > 0


def test_conta_trade_serie_vuota():
    assert motore.conta_trade([], lambda: strategia_ogni_k(5, "long", 2), 0, Parametri())["trade"] == 0


# ---------------------------------------------------------------------------
# baseline_casuale, baseline_da_trade, percentile_del_candidato
# ---------------------------------------------------------------------------


def test_baseline_casuale_media_ed_errore_della_media():
    valori = [0.1, -0.1, 0.0, 0.2, -0.2]
    b = st.baseline_casuale(valori)
    assert b["media"] == pytest.approx(0.0)
    assert b["errore_standard"] == pytest.approx(np.std(valori, ddof=1) / math.sqrt(5))
    assert b["n_simulazioni"] == 5


def test_baseline_casuale_serve_almeno_due_simulazioni():
    with pytest.raises(ValueError):
        st.baseline_casuale([0.1])


def test_baseline_da_trade_non_valutabile_sotto_tre_blocchi():
    b = st.baseline_da_trade([0.1, 0.2, 0.3, 0.1, 0.0, 0.2], lunghezza_blocco=3)
    assert b["valutabile"] is False and math.isinf(b["errore_standard"])
    b = st.baseline_da_trade(list(np.random.default_rng(0).normal(0, 1, 30)), lunghezza_blocco=10)
    assert b["valutabile"] is True and b["n_blocchi"] == 3 and b["errore_standard"] > 0


def test_percentile_del_candidato_strettamente_minore():
    assert st.percentile_del_candidato(0.2, [0.1, 0.2, 0.3, 0.0]) == 50.0
    assert st.percentile_del_candidato(1.0, [0.1, 0.2]) == 100.0


# ---------------------------------------------------------------------------
# batte_nettamente e p_value_vs_baseline
# ---------------------------------------------------------------------------


def _rumore(n, media, sd, seme):
    return list(np.random.default_rng(seme).normal(media, sd, n))


def test_batte_nettamente_vantaggio_grande():
    cand = _rumore(150, 0.5, 0.6, 1)
    r = st.batte_nettamente(cand, 3, 0.0, 0.005, n=1000)
    assert r["netta"] is True and r["t"] > r["soglia"] and r["valutabile"] is True
    assert r["errore_standard"] == pytest.approx(math.sqrt(r["errore_candidato"] ** 2 + 0.005 ** 2))
    assert r["margine"] == pytest.approx(r["soglia"] * r["errore_standard"])


def test_batte_nettamente_e_solo_verso_l_alto():
    cand = _rumore(150, -0.5, 0.6, 2)
    r = st.batte_nettamente(cand, 3, 0.0, 0.0, n=1000)
    assert r["differenza"] < -r["margine"] and r["netta"] is False and r["t"] < 0


def test_batte_nettamente_candidato_uguale_alla_baseline_non_e_netto():
    cand = _rumore(150, 0.0, 0.6, 3)
    r = st.batte_nettamente(cand, 3, float(np.mean(cand)), 0.0, n=1000)
    assert r["differenza"] == pytest.approx(0.0) and r["netta"] is False


def test_sotto_tre_blocchi_non_valutabile():
    # 30 trade: blocco 10 -> 3 blocchi, si valuta; blocco 11 -> 2 blocchi, no.
    # Con 2 blocchi l'errore del bootstrap crolla e un candidato senza vantaggio
    # risulterebbe «netto» circa una volta su tre (revisione del 7 ott).
    cand = _rumore(30, 0.1, 1.0, 4)
    assert st.batte_nettamente(cand, 10, 0.0, 0.0)["valutabile"] is True
    r = st.batte_nettamente(cand, 11, 0.0, 0.0)
    assert r["valutabile"] is False and r["netta"] is False and r["t"] == -math.inf and r["p_value"] == 1.0
    assert st.p_value_vs_baseline(cand, 11, 0.0, 0.0) == 1.0


def test_non_valutabile_con_errore_della_baseline_infinito_o_serie_costante():
    r = st.batte_nettamente(_rumore(50, 1, 0.1, 5), 3, 0.0, math.inf)
    assert r["valutabile"] is False and r["netta"] is False
    r = st.batte_nettamente([0.3] * 40, 4, 0.0, 0.0)
    assert r["valutabile"] is False and r["netta"] is False and r["t"] == -math.inf
    assert st.p_value_vs_baseline([0.3] * 40, 4, 0.0, 0.0) == 1.0


def test_l_errore_della_baseline_e_obbligatorio_e_controllato():
    with pytest.raises(TypeError):
        st.batte_nettamente([0.1] * 20, 2, 0.0)  # manca baseline_errore_standard
    with pytest.raises(ValueError):
        st.batte_nettamente([0.1] * 20, 2, 0.0, -1.0)
    with pytest.raises(ValueError):
        st.batte_nettamente([0.1] * 20, 2, float("nan"), 0.0)


def test_la_soglia_e_quella_di_student_e_con_molti_blocchi_vale_circa_due():
    r = st.batte_nettamente(_rumore(600, 0.0, 1.0, 6), 1, 0.0, 0.0, n=300)
    assert r["gradi_liberta"] == 599 and 2.0 < r["soglia"] < 2.01
    r = st.batte_nettamente(_rumore(30, 0.0, 1.0, 6), 10, 0.0, 0.0, n=300)
    assert r["gradi_liberta"] == 2 and r["soglia"] > 4.5


def test_netta_e_p_value_dicono_sempre_la_stessa_cosa():
    for seme in range(40):
        cand = _rumore(70, 0.15, 0.6, 100 + seme)
        r = st.batte_nettamente(cand, 3, 0.0, 0.01, n=500, seme=seme)
        p = st.p_value_vs_baseline(cand, 3, 0.0, 0.01, n=500, seme=seme)
        assert p == pytest.approx(r["p_value"])
        assert r["netta"] == (p < 1 - st.LIVELLO_NETTAMENTE)


def test_taratura_senza_vantaggio_netta_circa_una_volta_su_quaranta():
    # 400 candidati senza vantaggio, 70 trade indipendenti, blocco 3: «netta»
    # deve uscire intorno al 2,3% (qui si accetta fino al 5%), il p-value <= 0,10
    # intorno al 10% (fino al 15%). Prima della correzione del blocco e della
    # soglia di Student, con blocchi lunghi si arrivava al 9-30%.
    rng = np.random.default_rng(2026)
    netti = 0
    p10 = 0
    for k in range(400):
        cand = rng.normal(0.0, 0.6, 70)
        r = st.batte_nettamente(cand, 3, 0.0, 0.0, n=300, seme=k)
        netti += r["netta"]
        p10 += r["p_value"] <= 0.10
    assert netti / 400 < 0.05 and 0.05 < p10 / 400 < 0.15


def test_la_lettura_unica_e_meno_larga_del_confronto_con_una_corsa_sola():
    # Il problema della 4.3: candidato contro UNA corsa casuale (la mediana) somma
    # l'errore di quella corsa. Contro la media di 200 corse l'errore della
    # baseline quasi sparisce.
    rng = np.random.default_rng(7)
    n_trade = 120
    corse = [rng.normal(0.0, 0.6, n_trade) for _ in range(200)]
    medie = [float(np.mean(c)) for c in corse]
    mediana = corse[int(np.argsort(medie)[100])]
    cand = list(rng.normal(0.12, 0.6, n_trade))
    vecchia = st.differenza_nettamente(cand, mediana, lunghezza_blocco=3, n=1000, seme=0)
    base = st.baseline_casuale(medie)
    nuova = st.batte_nettamente(cand, 3, base["media"], base["errore_standard"], n=1000, seme=0)
    assert nuova["errore_standard"] < vecchia["errore_standard"] / 1.25
    assert base["errore_standard"] < nuova["errore_candidato"] / 8


def test_t_ordina_le_varianti_per_vicinanza_e_le_non_valutabili_vanno_in_fondo():
    vicina = st.batte_nettamente(_rumore(150, 0.08, 0.6, 5), 3, 0.0, 0.0, n=500)
    lontana = st.batte_nettamente(_rumore(150, -0.08, 0.6, 5), 3, 0.0, 0.0, n=500)
    non_valutabile = st.batte_nettamente(_rumore(20, 0.5, 0.6, 5), 10, 0.0, 0.0)
    ordine = sorted([("non_valutabile", non_valutabile), ("lontana", lontana), ("vicina", vicina)],
                    key=lambda x: x[1]["t"], reverse=True)
    assert [nome for nome, _ in ordine] == ["vicina", "lontana", "non_valutabile"]


def test_p_value_vs_baseline_piccolo_se_il_candidato_batte_la_baseline():
    cand = _rumore(80, 0.5, 0.6, 6)
    assert st.p_value_vs_baseline(cand, 3, 0.0, 0.005, n=1000) < 0.01


def test_p_value_vs_baseline_circa_mezzo_se_uguale_e_riproducibile():
    cand = _rumore(80, 0.0, 0.6, 8)
    p = st.p_value_vs_baseline(cand, 3, float(np.mean(cand)), 0.0, n=2000)
    assert 0.45 < p < 0.55
    c2 = _rumore(60, 0.1, 0.5, 10)
    assert st.p_value_vs_baseline(c2, 3, 0.0, 0.01, n=300, seme=4) == st.p_value_vs_baseline(c2, 3, 0.0, 0.01, n=300, seme=4)


# ---------------------------------------------------------------------------
# lunghezza_blocco
# ---------------------------------------------------------------------------

GIORNO = 86_400_000


def test_blocco_trade_distanti_piu_di_un_giorno_vale_uno():
    entrate = [i * 3 * GIORNO for i in range(10)]
    uscite = [e + ORA for e in entrate]
    assert st.lunghezza_blocco(entrate, uscite) == 1


def test_blocco_conta_i_trade_dello_stesso_giorno():
    # 4 trade di un'ora per giorno, giorni consecutivi: in una finestra di 24 ore
    # escono al massimo 4 trade (le uscite del giorno dopo cadono oltre la finestra).
    entrate = [g * GIORNO + k * 2 * ORA for g in range(5) for k in range(4)]
    uscite = [e + ORA for e in entrate]
    assert st.lunghezza_blocco(entrate, uscite) == 4


def test_blocco_usa_la_durata_massima_se_supera_il_giorno():
    # una posizione dura 3 giorni: la finestra e' di 3 giorni, non di 1
    entrate = [0, 1 * GIORNO, 2 * GIORNO, 10 * GIORNO]
    uscite = [3 * GIORNO, 1 * GIORNO + ORA, 2 * GIORNO + ORA, 10 * GIORNO + ORA]
    assert st.lunghezza_blocco(entrate, uscite) == 3


def test_blocco_rifiuta_dati_incoerenti():
    with pytest.raises(ValueError):
        st.lunghezza_blocco([], [])
    with pytest.raises(ValueError):
        st.lunghezza_blocco([10], [5])
    with pytest.raises(ValueError):
        st.lunghezza_blocco([1, 2], [3])


# ---------------------------------------------------------------------------
# StoriaChiusa: la vista senza copia da' gli stessi trade della copia
# ---------------------------------------------------------------------------


def _strategia_che_legge_in_tanti_modi(converti):
    """Usa len, indici negativi, fette, iterazione e somma: con ``converti`` la
    storia diventa prima una lista (il comportamento fino al 7 ott)."""

    def strategia(storia, posizione):
        if converti:
            storia = list(storia)
        if len(storia) < 12:
            return None
        ultime = storia[-10:]
        media = sum(c.close for c in ultime) / len(ultime)
        massimo = max(c.high for c in storia[-12:-2])
        primo = storia[0].open
        if posizione is None:
            if storia[-1].close > media and storia[-2].close <= media and storia[-1].close > primo * 0.5:
                return Segnale("long", stop=storia[-1].close * 0.98, target=massimo * 1.01)
            if storia[-1].close < media and storia[-3].close >= media:
                return Segnale("short", stop=storia[-1].close * 1.02)
            return None
        if posizione.direzione == "short" and storia[-1].close > media:
            return "chiudi"
        return None

    return strategia


def test_la_vista_da_gli_stessi_trade_della_copia():
    rng = np.random.default_rng(3)
    candele = []
    p = 100.0
    for i in range(1500):
        o = p
        c = p * (1 + rng.normal(0, 0.01))
        candele.append(candela(i, o, max(o, c) * (1 + abs(rng.normal(0, 0.004))), min(o, c) * (1 - abs(rng.normal(0, 0.004))), c))
        p = c
    vista = motore.esegui(candele, None, None, [], _strategia_che_legge_in_tanti_modi(False), Parametri())
    copia = motore.esegui(candele, None, None, [], _strategia_che_legge_in_tanti_modi(True), Parametri())
    assert len(vista.trades) > 20
    assert vista.trades == copia.trades and vista.curva_capitale == copia.curva_capitale


def test_la_vista_non_lascia_vedere_il_futuro():
    candele = serie_a_dente(10)
    v = motore.StoriaChiusa(candele, 4)
    assert len(v) == 4 and v[-1] is candele[3] and v[0] is candele[0]
    assert v[1:3] == candele[1:3] and v[::-1] == candele[3::-1] and list(v) == candele[:4]
    assert v[2:100] == candele[2:4] and v[-100:2] == candele[:2]
    with pytest.raises(IndexError):
        v[4]
    with pytest.raises(IndexError):
        v[-5]
    assert candele[5] not in v and candele[2] in v and v.index(candele[2]) == 2
    with pytest.raises(TypeError):
        v[1.0]
    with pytest.raises(TypeError):
        v["1"]
    assert v[np.int64(1)] is candele[1] and v[True] is candele[1]


def test_la_strategia_non_raggiunge_il_futuro_neppure_dall_attributo_interno():
    candele = serie_a_dente(60)
    viste = []

    def strategia(storia, posizione):
        viste.append((len(storia), len(storia._base)))
        return None

    motore.esegui(candele, None, None, [], strategia, Parametri())
    assert viste and all(n == m for n, m in viste)


# ---------------------------------------------------------------------------
# simula_baseline_casuale e durata_media_barre
# ---------------------------------------------------------------------------


def _crea_casuale(direzione="long", durata=3):
    def crea(ingressi):
        stato = {"entrata_i": None}

        def strategia(storia, posizione):
            i = len(storia) - 1
            if posizione is None:
                stato["entrata_i"] = None
                if i in ingressi:
                    c = storia[-1].close
                    return Segnale(direzione, stop=c * (0.5 if direzione == "long" else 1.5))
                return None
            if stato["entrata_i"] is None:
                stato["entrata_i"] = i
            if i - stato["entrata_i"] >= durata - 1:
                return "chiudi"
            return None
        return strategia
    return crea


def test_simula_baseline_casuale_riproducibile_e_con_i_trade_attesi():
    candele = serie_a_dente(600)
    a = motore.simula_baseline_casuale(candele, _crea_casuale(), 40, 5, Parametri(), n_simulazioni=20)
    b = motore.simula_baseline_casuale(candele, _crea_casuale(), 40, 5, Parametri(), n_simulazioni=20)
    assert a["media"] == b["media"] and a["n_simulazioni"] == 20 and a["simulazioni_vuote"] == 0
    # ingressi distanti 5 barre e posizioni di 3 barre: nessun ingresso si perde
    assert all(n == 40 for n in a["trade_per_simulazione"])
    assert a["errore_standard"] > 0


def test_simula_baseline_casuale_senza_spazio_alza_errore():
    candele = serie_a_dente(50)
    with pytest.raises(ValueError):
        motore.simula_baseline_casuale(candele, _crea_casuale(), 40, 5, Parametri(), n_simulazioni=3)


def test_durata_media_barre():
    candele = serie_a_dente(200)
    ris = motore.esegui(candele, None, None, [], strategia_ogni_k(10, "long", 3), Parametri())
    d = motore.durata_media_barre(ris.trades, ORA)
    assert d in (2, 3)
    with pytest.raises(ValueError):
        motore.durata_media_barre([], ORA)


# ---------------------------------------------------------------------------
# parametri.yaml e costanti del codice dicono la stessa cosa
# ---------------------------------------------------------------------------


def test_parametri_yaml_uguali_alle_costanti_del_codice():
    yaml = pytest.importorskip("yaml")
    from pathlib import Path
    percorso = Path(__file__).resolve().parents[2] / "config" / "parametri.yaml"
    regole = yaml.safe_load(percorso.read_text(encoding="utf-8"))["regole_esame"]
    assert regole["minimo_blocchi_bootstrap"] == st.MINIMO_BLOCCHI
    assert regole["livello_nettamente"] == st.LIVELLO_NETTAMENTE
    assert regole["trade_minimi"] == {"costruzione": 70, "validazione": 30, "vault": 30}
    assert regole["simulazioni_baseline_casuale"] == 200
    assert regole["semi_baseline_casuale"] == {"primo": 0, "ultimo": 199}
    assert regole["bootstrap"] == {"ricampionamenti": 2000, "seme": 0}
