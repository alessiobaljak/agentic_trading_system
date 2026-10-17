"""Verifica indipendente di ``research/src/statistica3.py`` contro ``research/PROTOCOLLO_3.md``.

Sezioni: 8.4 (contano solo gli ordini eseguiti), 10.1 entrate casuali, 10.2 p-value, 10.3 soglie di
costruzione, validazione e vault, 10.4 Benjamini-Hochberg, Passo 2 Fase 2 e Fase 4 (le undici verifiche),
Passo 6 punto 4 (altre monete).

Solo dati sintetici: passeggiate casuali con seme fisso, una serie piatta (pareggi esatti) e una serie con
un vantaggio inserito apposta (per vedere anche la strada in cui tutto passa). Poche simulazioni (20-50)
dove la funzione lo permette, 1.000 dove il protocollo le chiede (p-value della 10.2).

Per vedere QUALI trade tiene ogni simulazione, la fixture ``spia`` avvolge ``statistica3.simula_da``:
l'esito del motore resta quello vero, ma il trade e' avvolto in un oggetto che annota quando la
simulazione ne legge l'R, cioe' quando lo tiene. I test controllano anche che la media di ogni gruppo
annotato sia proprio il valore che il modulo restituisce per quella simulazione.
"""

from __future__ import annotations

import dataclasses
import datetime as dt

import numpy as np
import pytest

from research.src import statistica3 as st
from research.src.catalogo3 import (TIMEFRAME_MS, Serie, compila, funding_regolato, normalizza,
                                    prima_candela_dopo_regolamento, sposta_periodi)
from research.src.motore3 import (COSTI_DOPPI, COSTI_NORMALI, Regole, Risultato, Trade, esegui, metriche,
                                  simula_da)

ORA = 3_600_000
GIORNO = 24 * ORA


# ---------------------------------------------------------------------------
# serie sintetiche
# ---------------------------------------------------------------------------


def _ms(giorno: str) -> int:
    return int(dt.datetime.strptime(giorno, "%Y-%m-%d").replace(tzinfo=dt.timezone.utc).timestamp() * 1000)


def _costruisci(tf, ts, rend, vol, ombra_su, ombra_giu, f_ts, f_r, p0=20000.0) -> Serie:
    close = p0 * np.exp(np.cumsum(rend))
    op = np.r_[p0, close[:-1]]
    hi = np.maximum(op, close) * (1 + ombra_su)
    lo = np.minimum(op, close) * (1 - ombra_giu)
    return Serie(tf, ts, op, hi, lo, close, vol, op.copy(), hi.copy(), lo.copy(), close.copy(), f_ts, f_r)


def serie_casuale(n, tf="1h", seme=1, inizio="2020-11-01", sigma=0.004, togli=None) -> Serie:
    """Passeggiata casuale con seme fisso; ``togli`` = indici delle candele da togliere (buchi, 9.6)."""
    rng = np.random.default_rng(seme)
    d = TIMEFRAME_MS[tf]
    ts = _ms(inizio) + d * np.arange(n, dtype=np.int64)
    rend = rng.normal(0, sigma, n)
    su = np.abs(rng.normal(0, sigma / 2, n))
    giu = np.abs(rng.normal(0, sigma / 2, n))
    vol = rng.uniform(80, 120, n)
    f_ts = np.arange(_ms(inizio), ts[-1] + d, 8 * ORA, dtype=np.int64)
    f_r = rng.normal(0.0001, 0.0002, len(f_ts))
    s = _costruisci(tf, ts, rend, vol, su, giu, f_ts, f_r)
    if togli is None:
        return s
    tieni = np.ones(n, dtype=bool)
    tieni[togli] = False
    return Serie(tf, s.ts[tieni], s.open[tieni], s.high[tieni], s.low[tieni], s.close[tieni], s.volume[tieni],
                 s.mark_open[tieni], s.mark_high[tieni], s.mark_low[tieni], s.mark_close[tieni],
                 s.funding_ts, s.funding_tasso)


def serie_con_vantaggio(tf, seme=7) -> Serie:
    """Tutto il periodo di costruzione (2019-09-08 -> 2022-09-30). Ogni 40 candele un volume tre volte la
    media su una candela verde (segnale E12), poi 12 candele di +0,5% e 12 di -0,5% (il prezzo torna
    indietro: entrare a caso non guadagna niente). Il volume non dipende dal prezzo, quindi il segnale e'
    esattamente dove e' stato messo il vantaggio."""
    d = TIMEFRAME_MS[tf]
    t0, t1 = _ms("2019-09-08"), _ms("2022-10-01")
    n = (t1 - t0) // d
    rng = np.random.default_rng(seme)
    ts = t0 + d * np.arange(n, dtype=np.int64)
    rend = rng.normal(0, 0.002, n)
    vol = rng.uniform(90, 110, n)
    for s_ in range(60, n - 30, 40):
        rend[s_] = 0.003
        vol[s_] = 300.0
        rend[s_ + 1:s_ + 13] += 0.005
        rend[s_ + 13:s_ + 25] -= 0.005
    su = np.abs(rng.normal(0, 0.001, n))
    giu = np.abs(rng.normal(0, 0.001, n))
    f_ts = np.arange(t0, t1, 8 * ORA, dtype=np.int64)
    return _costruisci(tf, ts, rend, vol, su, giu, f_ts, np.full(len(f_ts), 0.0001))


def serie_piatta(n, inizio="2021-01-04") -> Serie:
    """Prezzo fermo a 20.000 e funding costante +0,05% ogni 8 ore (2021-01-04 e' un lunedi')."""
    t0 = _ms(inizio)
    ts = t0 + ORA * np.arange(n, dtype=np.int64)
    p = np.full(n, 20000.0)
    f_ts = np.arange(t0, ts[-1] + ORA, 8 * ORA, dtype=np.int64)
    return Serie("1h", ts, p, p, p, p, np.full(n, 100.0), p, p, p, p, f_ts, np.full(len(f_ts), 0.0005))


# ---------------------------------------------------------------------------
# varianti (solo valori del catalogo, sezione 7)
# ---------------------------------------------------------------------------


def _v(**kw) -> dict:
    v = {"timeframe": "1h", "direzione": "long", "filtro": None, "ingresso": {"codice": "E7", "n": 7},
         "conferma": None, "tipo_ingresso": {"codice": "M"}, "stop": {"codice": "S3", "pct": 0.03},
         "uscite": [{"codice": "U2", "n": 24}]}
    v.update(kw)
    return v


#: a mercato; sulla serie di base il candidato e' in posizione circa i due terzi del tempo
V_MERCATO = _v()
#: limit 0,25 x ATR, validita' 3 candele
V_LIMIT = _v(tipo_ingresso={"codice": "L", "k": 0.25, "validita": 3}, stop={"codice": "S1", "k": 1.5},
             uscite=[{"codice": "U1", "k": 2.0}, {"codice": "U2", "n": 12}])
V_SHORT = _v(direzione="short", stop={"codice": "S1", "k": 1.5},
             uscite=[{"codice": "U1", "k": 2.0}, {"codice": "U2", "n": 12}])
V_VANTAGGIO = {"timeframe": "4h", "direzione": "long", "filtro": None, "ingresso": {"codice": "E12", "soglia": 2.0},
               "conferma": None, "tipo_ingresso": {"codice": "M"}, "stop": {"codice": "S3", "pct": 0.01},
               "uscite": [{"codice": "U1", "k": 2.0}, {"codice": "U2", "n": 12}]}

DECISIVE_MERCATO = ["1_robustezza", "2_timeframe_adiacenti", "3_blocchi", "4_senza_i_migliori", "5_costi_doppi",
                    "6_troncamento", "7_liquidazione"]
DECISIVE_LIMIT = DECISIVE_MERCATO + ["8_riempimento_severo"]


@pytest.fixture(scope="module")
def serie():
    return serie_casuale(1500)


# ---------------------------------------------------------------------------
# la spia sulle entrate casuali
# ---------------------------------------------------------------------------


@pytest.fixture
def spia(monkeypatch):
    """Osserva le entrate casuali: ``registro`` riceve (candela scelta, trade) di ogni trade delle
    simulazioni TENUTE, nell'ordine (con ``statistica3._OSSERVATORE``: i giri di taratura e quelli
    scartati perche' non hanno esattamente i trade del candidato non contano); ``chiamate`` ogni
    decisione forzata che le entrate casuali chiedono al motore."""
    registro = []
    chiamate = []
    vera = st.simula_da

    def finta(c, j, regole, costi, fine, forzato=False):
        e = vera(c, j, regole, costi, fine, forzato=forzato)
        chiamate.append({"j": int(j), "regole": regole, "costi": costi, "fine": fine, "forzato": forzato,
                         "tipo": e.tipo})
        return e

    monkeypatch.setattr(st, "simula_da", finta)
    monkeypatch.setattr(st, "_OSSERVATORE", lambda presi: registro.extend(presi))
    return registro, chiamate


def _simulazioni(registro, n_trade, n_sim):
    """Divide il registro nelle simulazioni: ognuna tiene ESATTAMENTE ``n_trade`` trade."""
    assert len(registro) == n_trade * n_sim
    return [registro[k * n_trade:(k + 1) * n_trade] for k in range(n_sim)]


def _senza_sovrapposizioni(trades) -> bool:
    """Un trade vive dalla chiusura della candela della decisione all'uscita: il successivo puo' decidere
    solo dalla candela di uscita in poi (9.2, punti 4 e 5)."""
    ordinati = sorted(trades, key=lambda t: t.indice_segnale)
    return all(b.indice_segnale >= a.indice_uscita for a, b in zip(ordinati, ordinati[1:]))


def _massimo_senza_sovrapposizioni(c, inizio, fine, regole=Regole(), costi=COSTI_NORMALI) -> int:
    """Oracolo indipendente: il numero MASSIMO di trade senza sovrapposizioni che il periodo puo' tenere
    (intervalli [decisione, candela libera), scelta per fine piu' vicina: e' l'ottimo)."""
    intervalli = []
    for j in np.flatnonzero(c.ammessa[inizio:fine + 1]) + inizio:
        e = simula_da(c, int(j), regole, costi, fine, forzato=True)
        if e.tipo == "trade":
            intervalli.append((max(e.libero_da, int(j) + 1), int(j)))
    intervalli.sort()
    contati, libero = 0, -1
    for b, a in intervalli:
        if a >= libero:
            contati += 1
            libero = b
    return contati


# ---------------------------------------------------------------------------
# 10.1 entrate casuali
# ---------------------------------------------------------------------------


def test_10_1_ogni_simulazione_ha_esattamente_i_trade_del_candidato(serie, spia):
    """10.1: «stesso numero di trade del candidato» (lo prende la Fase 2 dal candidato)."""
    registro, _ = spia
    out = st.fase2(V_MERCATO, serie, 0, len(serie) - 1, n_simulazioni=50)
    n = out["metriche"]["trade"]
    assert n == len(out["risultato"].trade) > 20
    for k, prese in enumerate(_simulazioni(registro, n, 50)):
        assert len({j for j, _ in prese}) == n
        # il valore restituito e' l'R medio proprio di quei trade
        # stessi trade, somme fatte in due modi: uguali a meno dell'ultima cifra (numpy 2.5)
        assert out["valori_casuali"][k] == pytest.approx(sum(t.r for _, t in prese) / n, rel=0, abs=1e-12)


@pytest.mark.parametrize("variante", [V_MERCATO, V_LIMIT], ids=["mercato", "limit"])
def test_10_1_nessuna_sovrapposizione_fra_i_trade_di_una_simulazione(serie, spia, variante):
    """10.1: «senza sovrapposizioni fra trade della stessa simulazione»."""
    registro, _ = spia
    out = st.fase2(variante, serie, 0, len(serie) - 1, n_simulazioni=50)
    n = out["metriche"]["trade"]
    assert _senza_sovrapposizioni(out["risultato"].trade)  # il candidato, per confronto
    for prese in _simulazioni(registro, n, 50):
        assert _senza_sovrapposizioni([t for _, t in prese])
        for j, t in prese:
            assert t.indice_segnale == j < t.indice_ingresso <= t.indice_uscita


def test_10_1_ingressi_solo_fra_le_candele_ammesse_del_periodo(spia):
    """10.1: ingressi «fra tutte le candele ammesse del periodo (dopo il riscaldamento della variante e
    fuori dai buchi nei dati, 7.8 e 9.6)». Il riscaldamento si ricontrolla a mano: 3 x RSI(7) = 21."""
    registro, _ = spia
    s = serie_casuale(1500, seme=3, togli=np.arange(700, 710))
    v = _v(stop={"codice": "S3", "pct": 0.02}, uscite=[{"codice": "U2", "n": 12}])
    c = compila(v, s)
    inizio, fine = 10, len(s) - 40
    inizi = np.r_[0, np.flatnonzero(np.diff(s.ts) != s.durata) + 1]
    assert list(inizi) == [0, 700]
    riscaldamento = 21

    def ammessa_a_mano(j):
        return j - inizi[inizi <= j].max() >= riscaldamento

    attese = sum(ammessa_a_mano(j) for j in range(inizio, fine + 1))
    n = len(esegui(c, Regole(), COSTI_NORMALI, inizio, fine).trade)
    out = st.entrate_casuali(c, n, inizio, fine, n_simulazioni=50)
    assert out["candele_ammesse"] == attese
    scelte = []
    for prese in _simulazioni(registro, n, 50):
        for j, t in prese:
            assert inizio <= j <= fine
            assert ammessa_a_mano(j) and c.ammessa[j]
            assert t.indice_uscita <= fine  # stesso periodo: la simulazione non legge oltre la fine
            scelte.append(j)
    scelte = np.array(scelte)
    assert scelte.min() >= riscaldamento
    assert not np.any((scelte >= 700) & (scelte < 700 + riscaldamento))  # riscaldamento dopo il buco
    assert np.any(scelte >= 700 + riscaldamento) and np.any(scelte < 700)


def test_10_1_ingressi_anche_quando_il_candidato_e_in_posizione(serie, spia):
    """10.1: «indipendentemente da quando il candidato è in posizione» (appendice 2, punto 4)."""
    registro, _ = spia
    fine = len(serie) - 1
    c = compila(V_MERCATO, serie)
    ris = esegui(c, Regole(), COSTI_NORMALI, 0, fine)
    in_posizione = np.zeros(len(serie), dtype=bool)
    for t in ris.trade:
        in_posizione[t.indice_ingresso:t.indice_uscita] = True
    ammesse = np.flatnonzero(c.ammessa[:fine + 1])
    quota_attesa = in_posizione[ammesse].mean()
    assert quota_attesa > 0.5  # il candidato e' in posizione per lunghi tratti
    st.entrate_casuali(c, len(ris.trade), 0, fine, n_simulazioni=50)
    scelte = np.array([j for j, _ in registro])
    assert in_posizione[scelte].mean() > 0.5 * quota_attesa


def test_10_1_ingressi_anche_dove_il_filtro_del_candidato_e_falso(serie, spia):
    """10.1: le entrate casuali non ereditano il filtro di tendenza del candidato (appendice 2, punto 4)."""
    registro, _ = spia
    fine = len(serie) - 1
    c = compila(_v(filtro={"codice": "F1", "n": 50, "lato": "sopra"}), serie)
    filtro = c.dettagli["filtro"]
    ris = esegui(c, Regole(), COSTI_NORMALI, 0, fine)
    assert ris.trade and all(filtro[t.indice_segnale] for t in ris.trade)
    ammesse = np.flatnonzero(c.ammessa[:fine + 1])
    quota_attesa = (~filtro[ammesse]).mean()
    assert quota_attesa > 0.2
    st.entrate_casuali(c, len(ris.trade), 0, fine, n_simulazioni=50)
    scelte = np.array([j for j, _ in registro])
    assert (~filtro[scelte]).mean() > 0.5 * quota_attesa


def test_10_1_stesso_ingresso_a_mercato_stesso_stop_stesse_uscite(serie, spia):
    """10.1: a mercato all'apertura successiva; stesso stop calcolato all'ingresso, stesse uscite."""
    registro, _ = spia
    fine = len(serie) - 1
    c = compila(V_MERCATO, serie)
    ris = esegui(c, Regole(), COSTI_NORMALI, 0, fine)
    st.entrate_casuali(c, len(ris.trade), 0, fine, n_simulazioni=50)
    assert registro
    for j, t in registro:
        e = serie.open[j + 1] * (1 + 0.0001)  # 9.3: apertura x (1 + 0,0001)
        assert t.tipo_ingresso == "M" and t.long and t.indice_ingresso == j + 1
        assert t.prezzo_ingresso == pytest.approx(e, rel=1e-12)
        assert t.stop_iniziale == pytest.approx(e * (1 - 0.03), rel=1e-12)  # S3 3%
        assert t.target is None
        assert t.motivo in {"stop", "stop_salto", "tempo", "fine_dati"}
        if t.motivo == "tempo":
            assert t.indice_uscita == t.indice_ingresso + 24  # U2: candela di ingresso = prima delle 24
        comm = t.quantita * t.prezzo_ingresso * 0.0005 + t.quantita * t.prezzo_uscita * 0.0005
        assert t.commissioni == pytest.approx(comm, rel=1e-9)
    del_candidato = {t.indice_segnale: t for t in ris.trade}
    uguali = [(t, del_candidato[j]) for j, t in registro if j in del_candidato]
    assert len(uguali) > 10
    for a, b in uguali:  # un ingresso casuale sul segnale del candidato fa esattamente il suo trade
        assert dataclasses.asdict(a) == dataclasses.asdict(b)


def test_10_1_stessa_direzione_short(serie, spia):
    registro, _ = spia
    fine = len(serie) - 1
    c = compila(V_SHORT, serie)
    ris = esegui(c, Regole(), COSTI_NORMALI, 0, fine)
    assert ris.trade and not any(t.long for t in ris.trade)
    st.entrate_casuali(c, len(ris.trade), 0, fine, n_simulazioni=20)
    assert registro
    for j, t in registro:
        e = serie.open[j + 1] * (1 - 0.0001)
        assert not t.long
        assert t.prezzo_ingresso == pytest.approx(e, rel=1e-12)
        assert t.stop_iniziale == pytest.approx(e + 1.5 * c.atr_stop[j], rel=1e-12)
        assert t.target == pytest.approx(e - 2.0 * 1.5 * c.atr_stop[j], rel=1e-12)


def test_10_1_stesso_ingresso_limit_e_contano_solo_gli_ordini_eseguiti(serie, spia):
    """10.1: ordine limit inserito alla chiusura della candela scelta, stessi k e validita', stesse regole
    di esecuzione (7.7); «si generano ordini finché quelli eseguiti sono tanti quanti i trade del
    candidato». 8.4: anche per il candidato contano solo gli ordini eseguiti."""
    registro, chiamate = spia
    fine = len(serie) - 1
    out = st.fase2(V_LIMIT, serie, 0, fine, n_simulazioni=50)
    c = out["compilata"]
    n = out["metriche"]["trade"]
    cont = out["risultato"].contatori
    assert n == cont["ordini_eseguiti"] and cont["ordini_cancellati"] > 0
    for prese in _simulazioni(registro, n, 50):
        for j, t in prese:
            lim = serie.close[j] - 0.25 * c.atr_limite[j]
            assert t.tipo_ingresso == "L"
            assert t.prezzo_ingresso == pytest.approx(lim, rel=1e-12)  # sempre il prezzo limit
            assert j + 1 <= t.indice_ingresso <= j + 3  # attivo dalla candela dopo, per 3 candele
            assert serie.low[t.indice_ingresso] < lim  # eseguito solo se il prezzo SUPERA il limit
            assert all(serie.low[k] >= lim for k in range(j + 1, t.indice_ingresso))
            stop = lim - 1.5 * c.atr_stop[j]
            assert t.stop_iniziale == pytest.approx(stop, rel=1e-12)
            assert t.target == pytest.approx(lim + 2.0 * (lim - stop), rel=1e-12)
            if t.motivo == "target":
                assert t.indice_uscita > t.indice_ingresso  # nella candela di esecuzione vale solo lo stop
            if t.motivo == "tempo":
                assert t.indice_uscita == t.indice_ingresso + 12
    non_eseguiti = {ch["j"] for ch in chiamate if ch["tipo"] == "limite_non_eseguito"}
    assert non_eseguiti  # le simulazioni ne hanno incontrati...
    assert not non_eseguiti & {j for j, _ in registro}  # ...e non li hanno contati


@pytest.mark.parametrize("costi,taker,maker,slip", [(COSTI_NORMALI, 0.0005, 0.0002, 0.0001),
                                                     (COSTI_DOPPI, 0.0010, 0.0004, 0.0002)],
                         ids=["costi_normali", "costi_doppi"])
def test_10_1_stessi_costi(serie, spia, costi, taker, maker, slip):
    """10.1: «stessi costi» (sezione 6; costi doppi per le verifiche che li chiedono)."""
    registro, chiamate = spia
    fine = len(serie) - 1
    c = compila(V_LIMIT, serie)
    ris = esegui(c, Regole(), costi, 0, fine)
    st.entrate_casuali(c, len(ris.trade), 0, fine, Regole(), costi, n_simulazioni=20)
    assert chiamate and all(ch["costi"] == costi and ch["fine"] == fine for ch in chiamate)
    for _, t in registro:
        comm = t.quantita * t.prezzo_ingresso * maker + t.quantita * t.prezzo_uscita * taker
        assert t.commissioni == pytest.approx(comm, rel=1e-9)
        if t.motivo == "tempo":
            assert t.prezzo_uscita == pytest.approx(serie.open[t.indice_uscita] * (1 - slip), rel=1e-12)
        if t.motivo == "stop":
            assert t.prezzo_uscita == pytest.approx(t.stop_iniziale * (1 - slip), rel=1e-12)
        if t.motivo == "target":
            assert t.prezzo_uscita == pytest.approx(t.target * (1 - slip), rel=1e-12)
    del_candidato = {t.indice_segnale: t for t in ris.trade}
    uguali = [(t, del_candidato[j]) for j, t in registro if j in del_candidato]
    assert uguali
    for a, b in uguali:
        assert dataclasses.asdict(a) == dataclasses.asdict(b)


def test_10_1_seme_2026_riproducibile(serie):
    """10.1: seme fisso 2026. SCELTA del modulo: un solo generatore per tutte le simulazioni in fila."""
    fine = len(serie) - 1
    c = compila(V_MERCATO, serie)
    n = len(esegui(c, Regole(), COSTI_NORMALI, 0, fine).trade)
    a = st.entrate_casuali(c, n, 0, fine, n_simulazioni=40)
    b = st.entrate_casuali(c, n, 0, fine, n_simulazioni=40, seme=2026)
    assert st.SEME == 2026 and a["seme"] == 2026 and st.N_SIMULAZIONI == 1000
    np.testing.assert_array_equal(a["valori"], b["valori"])
    altro = st.entrate_casuali(c, n, 0, fine, n_simulazioni=40, seme=2027)
    assert not np.array_equal(a["valori"], altro["valori"])
    corte = st.entrate_casuali(c, n, 0, fine, n_simulazioni=20)
    np.testing.assert_array_equal(corte["valori"], a["valori"][:20])


def test_10_1_simulazione_impossibile(serie):
    """Se il periodo non puo' tenere i trade del candidato senza sovrapposizioni, il modulo si ferma."""
    c = compila(_v(uscite=[{"codice": "U2", "n": 48}]), serie)
    ammesse = int(c.ammessa[:200].sum())
    with pytest.raises(st.SimulazioneImpossibile):
        st.entrate_casuali(c, ammesse + 1, 0, 199, n_simulazioni=5)
    assert _massimo_senza_sovrapposizioni(c, 0, 199) < 10  # l'oracolo: 10 trade non ci stanno
    with pytest.raises(st.SimulazioneImpossibile):
        st.entrate_casuali(c, 10, 0, 199, n_simulazioni=5)
    with pytest.raises(ValueError):
        st.entrate_casuali(c, 0, 0, len(serie) - 1, n_simulazioni=5)


def test_10_1_non_si_ferma_se_il_candidato_stesso_dimostra_che_i_trade_ci_stanno(serie):
    """10.1 chiede 1.000 simulazioni con lo stesso numero di trade del candidato. Qui il candidato
    (U2 48 candele, in posizione circa il 75% del tempo) e' lui stesso una disposizione valida senza
    sovrapposizioni: le simulazioni devono potersi fare, non fermarsi con SimulazioneImpossibile."""
    fine = len(serie) - 1
    c = compila(_v(uscite=[{"codice": "U2", "n": 48}]), serie)
    ris = esegui(c, Regole(), COSTI_NORMALI, 0, fine)
    n = len(ris.trade)
    assert _senza_sovrapposizioni(ris.trade)
    assert _massimo_senza_sovrapposizioni(c, 0, fine) >= n
    out = st.entrate_casuali(c, n, 0, fine, n_simulazioni=50)
    assert len(out["valori"]) == 50


def test_10_1_le_entrate_casuali_non_scelgono_i_trade_in_base_a_quando_finiscono():
    """Glossario e 10.1: un'entrata casuale e' una «strategia fittizia che entra in momenti scelti a caso ma
    esce con le stesse regole del candidato», con ingressi «scelti a caso fra tutte le candele ammesse».
    Su una passeggiata casuale nessuna candela ammessa vale piu' di un'altra: l'R medio atteso delle
    simulazioni e' quello di un trade aperto su una candela ammessa qualunque. Tenere un trade solo se la
    sua durata «ci sta» fra quelli gia' presi sceglie di piu' i trade brevi (qui: gli stop, -1 R) e abbassa la
    media del caso, cosi' il candidato sembra migliore del caso senza merito (appendice 2, punto 4).
    Il candidato qui e' in posizione circa meta' del tempo. Tolleranza 0,03 R (il vantaggio minimo e' 0,2 R)."""
    v = _v(stop={"codice": "S1", "k": 1.5}, uscite=[{"codice": "U1", "k": 2.0}, {"codice": "U2", "n": 24}])
    scarti = []
    for seme in (1, 2, 3, 4):
        s = serie_casuale(3000, seme=seme)
        c = compila(v, s)
        fine = len(s) - 1
        n = len(esegui(c, Regole(), COSTI_NORMALI, 0, fine).trade)
        out = st.entrate_casuali(c, n, 0, fine, n_simulazioni=200)
        tutti = [simula_da(c, int(j), Regole(), COSTI_NORMALI, fine, forzato=True)
                 for j in np.flatnonzero(c.ammessa[:fine + 1])]
        media_di_tutti = float(np.mean([e.trade.r for e in tutti if e.tipo == "trade"]))
        scarti.append(out["media"] - media_di_tutti)
    assert abs(float(np.mean(scarti))) <= 0.03, scarti


# ---------------------------------------------------------------------------
# 10.2 p-value
# ---------------------------------------------------------------------------


def test_10_2_formula_con_i_pareggi():
    """p = (1 + simulazioni con R medio MAGGIORE O UGUALE a quello del candidato) / 1.001."""
    valori = np.full(1000, -0.1)
    valori[:7] = 0.25  # pareggi esatti: contano
    valori[7:12] = 0.4
    assert st.p_value(0.25, valori) == (1 + 12) / 1001
    assert st.p_value(0.25, list(valori)) == (1 + 12) / 1001
    assert st.p_value(0.2500001, valori) == (1 + 5) / 1001
    assert st.p_value(0.41, valori) == 1 / 1001
    assert st.p_value(-0.1, valori) == 1.0
    assert st.p_value(-5.0, valori) == 1.0


@pytest.mark.parametrize("n", [0, 50, 999, 1001, 2000])
def test_10_2_servono_esattamente_1000_simulazioni(n):
    with pytest.raises(ValueError):
        st.p_value(0.1, np.zeros(n))


def test_10_2_pareggi_esatti_anche_nella_fase2():
    """Prezzo fermo e funding costante: ogni trade di 24 candele attraversa esattamente 3 regolamenti, quindi
    il candidato e ogni simulazione con soli trade completi hanno lo STESSO R medio, bit per bit. I trade
    casuali tagliati dalla fine dei dati pagano meno funding e valgono di piu'. Tutte e 1.000 le simulazioni
    contano: p = 1.001 / 1.001."""
    s = serie_piatta(8 * 168 + 24)
    v = {"timeframe": "1h", "direzione": "long", "filtro": {"codice": "F6", "giorni": "fine_settimana"},
         "ingresso": {"codice": "E11", "soglia": 0.0003}, "conferma": None, "tipo_ingresso": {"codice": "M"},
         "stop": {"codice": "S3", "pct": 0.01}, "uscite": [{"codice": "U2", "n": 24}]}
    out = st.fase2(v, s, 0, len(s) - 1)
    ris = out["risultato"]
    assert len(ris.trade) == 16 and all(t.motivo == "tempo" for t in ris.trade)
    assert len({t.r for t in ris.trade}) == 1
    valori = out["valori_casuali"]
    assert len(valori) == 1000
    # ci sono pareggi (uguali bit per bit con numpy 1.26, all'ultima cifra con numpy 2.5)
    assert np.sum(np.abs(valori - out["metriche"]["r_medio"]) < 1e-12) > 0
    assert out["p_value"] == 1.0


# ---------------------------------------------------------------------------
# 10.3 soglie e Passo 6 punto 4
# ---------------------------------------------------------------------------


def _m(trade, r, pf=2.0):
    return {"trade": trade, "r_medio": r, "profit_factor": pf}


def test_10_3_numeri_del_protocollo():
    assert st.SOGLIE_COSTRUZIONE == {"trade": 150, "r_medio": 0.2, "p_value": 0.023}
    assert st.SOGLIE_VALIDAZIONE == {"trade": 60, "frazione_di_costruzione": 0.5, "profit_factor": 1.05}
    assert st.SOGLIE_VAULT == {"trade": 100, "profit_factor": 1.10, "q": 0.10}
    assert st.SOGLIE_ALTRE_MONETE == {"trade": 100, "profit_factor": 1.10, "p_value": 0.10}


@pytest.mark.parametrize("trade,r,p,manca", [
    (150, 0.2, 0.023, None),
    (149, 0.2, 0.023, "trade"),
    (150, 0.19999, 0.023, "r_medio"),
    (150, 0.2, 0.0231, "p_value"),
    (150, 0.2, 23 / 1001, None),
    (150, 0.2, 24 / 1001, "p_value"),
    (150, 0.2, None, "p_value"),
    (1000, 1.5, 1 / 1001, None),
])
def test_10_3_costruzione(trade, r, p, manca):
    """Almeno 150 trade; R medio di almeno 0,2 R; p-value di 0,023 o meno."""
    e = st.supera_costruzione(_m(trade, r), p)
    assert e["supera"] == (manca is None)
    falliti = {k for k, x in e.items() if k != "supera" and not x}
    assert falliti == (set() if manca is None else {manca})


@pytest.mark.parametrize("trade,r,pf,r_doppi,r_costr,manca", [
    (60, 0.1, 1.05, 0.001, 0.2, set()),
    (59, 0.1, 1.05, 0.001, 0.2, {"trade"}),
    (60, 0.0999, 1.05, 0.001, 0.2, {"meta_di_costruzione"}),
    (60, 0.15, 1.05, 0.01, 0.3, set()),  # esattamente la meta'
    (60, 0.14999, 1.05, 0.01, 0.3, {"meta_di_costruzione"}),
    (60, 0.5, 1.2, 0.3, 0.4, set()),  # meglio della costruzione: va bene
    (60, 0.1, 1.0499, 0.001, 0.2, {"profit_factor"}),
    (60, 0.1, 1.05, 0.0, 0.2, {"costi_doppi"}),
    (60, 0.1, 1.05, -0.01, 0.2, {"costi_doppi"}),
    (60, 0.0, 1.05, 0.001, 0.0, {"r_positivo"}),
])
def test_10_3_validazione(trade, r, pf, r_doppi, r_costr, manca):
    """Almeno 60 trade; R medio positivo; almeno la meta' di quello di costruzione; profit factor di almeno
    1,05; R medio positivo anche a costi doppi."""
    e = st.supera_validazione(_m(trade, r, pf), {"r_medio": r_doppi}, r_costr)
    assert e["supera"] == (not manca)
    assert {k for k, x in e.items() if k != "supera" and not x} == manca


@pytest.mark.parametrize("trade,r,pf,r_doppi,manca", [
    (100, 0.01, 1.10, 0.001, set()),
    (99, 0.01, 1.10, 0.001, {"trade"}),
    (100, 0.0, 1.10, 0.001, {"r_positivo"}),
    (100, 0.01, 1.0999, 0.001, {"profit_factor"}),
    (100, 0.01, 1.10, 0.0, {"costi_doppi"}),
    (100, 0.01, 1.10, -0.2, {"costi_doppi"}),
])
def test_10_3_vault(trade, r, pf, r_doppi, manca):
    """Almeno 100 trade; R medio positivo dopo i costi e a costi doppi; profit factor di almeno 1,10
    (l'asticella di Benjamini-Hochberg si applica a parte, a tutti i candidati insieme)."""
    e = st.supera_vault(_m(trade, r, pf), {"r_medio": r_doppi})
    assert e["supera_senza_asticella"] == (not manca)
    assert {k for k, x in e.items() if k != "supera_senza_asticella" and not x} == manca


@pytest.mark.parametrize("trade,r,pf,p,manca", [
    (100, 0.01, 1.10, 0.10, set()),
    (99, 0.01, 1.10, 0.10, {"trade"}),
    (100, 0.0, 1.10, 0.10, {"r_positivo"}),
    (100, 0.01, 1.0999, 0.10, {"profit_factor"}),
    (100, 0.01, 1.10, 0.1001, {"p_value"}),
    (100, 0.01, 1.10, 100 / 1001, set()),
    (100, 0.01, 1.10, 101 / 1001, {"p_value"}),
    (100, 0.01, 1.10, None, {"p_value"}),
])
def test_passo6_altre_monete(trade, r, pf, p, manca):
    """Passo 6 punto 4: almeno 100 trade, R medio positivo, profit factor di almeno 1,10, p-value di 0,10
    o meno."""
    e = st.regge_altra_moneta(_m(trade, r, pf), p)
    assert e["regge"] == (not manca)
    assert {k for k, x in e.items() if k != "regge" and not x} == manca


# ---------------------------------------------------------------------------
# 10.4 Benjamini-Hochberg
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("p,atteso", [
    ([0.02, 0.04, 0.30], [True, True, False]),  # l'esempio della 10.4: soglie 0,033 0,067 0,10 -> k = 2
    ([0.30, 0.02, 0.04], [False, True, True]),  # ordine originale conservato
    ([0.05, 0.06, 0.07, 0.5], [True, True, True, False]),  # soglie .025 .05 .075 .1: k = 3 (step-up)
    ([0.06, 0.09], [True, True]),  # 0,06 > 0,05 ma p(2) = 0,09 <= 0,10: passano tutti e due
    ([0.06, 0.11], [False, False]),
    ([0.01, 0.2, 0.021], [True, False, True]),
    ([0.034, 0.5, 0.6], [False, False, False]),  # 0,034 > 0,0333: nessun k
    ([0.1], [True]),  # p(k) <= (k/m) x 0,10: la parita' passa
    ([0.1001], [False]),
    ([0.1, 0.1, 0.1, 0.1], [True, True, True, True]),
    ([0.05, 0.05], [True, True]),
    ([1 / 1001, 30 / 1001, 60 / 1001], [True, True, True]),
    ([], []),
])
def test_10_4_benjamini_hochberg_al_10_percento(p, atteso):
    assert st.asticella_vault(p) == atteso


# ---------------------------------------------------------------------------
# Fase 2
# ---------------------------------------------------------------------------


def test_fase2_metriche_p_value_soglie_buy_and_hold_e_r_per_anno():
    """Fase 2: metriche (9.7), entrate casuali e p-value (10.1, 10.2), soglie di costruzione (10.3); per
    informazione buy and hold nello stesso periodo e somma degli R per anno."""
    s = serie_casuale(1500, seme=5, inizio="2020-12-01")  # dicembre 2020 -> gennaio 2021
    inizio, fine = 30, len(s) - 1
    out = st.fase2(V_MERCATO, s, inizio, fine, n_simulazioni=50)
    m = out["metriche"]
    ris = esegui(compila(V_MERCATO, s), Regole(), COSTI_NORMALI, inizio, fine)
    atteso = metriche(ris, s)
    for k in ("trade", "r_medio", "profit_factor", "drawdown_max_r", "vincenti", "violazioni_liquidazione"):
        assert m[k] == atteso[k]
    valori = out["valori_casuali"]
    assert len(valori) == 50 and out["casuali"]["n_simulazioni"] == 50 and out["casuali"]["seme"] == 2026
    assert out["p_value"] == (1 + int(np.sum(valori >= m["r_medio"]))) / 51
    assert out["esiti"] == st.supera_costruzione(m, out["p_value"])
    assert out["supera"] == out["esiti"]["supera"]
    assert m["trade"] < 150 and out["supera"] is False
    assert out["buy_and_hold"] == pytest.approx(s.close[fine] / s.open[inizio] - 1, rel=1e-12)
    assert out["somma_r_strategia"] == pytest.approx(sum(t.r for t in ris.trade), rel=1e-12)
    per_anno = {}
    for t in ris.trade:
        anno = dt.datetime.fromtimestamp(t.ts_uscita / 1000, tz=dt.timezone.utc).year
        per_anno[anno] = per_anno.get(anno, 0.0) + t.r
    assert set(per_anno) == {2020, 2021}
    assert set(m["r_per_anno"]) == set(per_anno)
    for anno, somma in per_anno.items():
        assert m["r_per_anno"][anno] == pytest.approx(somma, abs=1e-12)


def test_fase2_senza_trade():
    s = serie_casuale(50)
    out = st.fase2(_v(ingresso={"codice": "E7", "n": 21}), s, 0, len(s) - 1, n_simulazioni=20)
    assert out["metriche"]["trade"] == 0
    assert out["p_value"] is None and out["valori_casuali"] is None and out["supera"] is False


@pytest.fixture(scope="module")
def vantaggio():
    s = serie_con_vantaggio("4h")
    return s, st.fase2(V_VANTAGGIO, s, 0, len(s) - 1)  # 1.000 simulazioni e seme 2026: i valori di default


def test_fase2_con_1000_simulazioni_supera_un_vantaggio_vero(vantaggio):
    s, out = vantaggio
    m = out["metriche"]
    valori = out["valori_casuali"]
    assert len(valori) == 1000 and out["casuali"]["seme"] == 2026
    assert out["p_value"] == (1 + int(np.sum(valori >= m["r_medio"]))) / 1001
    assert m["trade"] >= 150 and m["r_medio"] >= 0.2 and out["p_value"] <= 0.023
    assert out["supera"] is True and all(out["esiti"].values())


# ---------------------------------------------------------------------------
# Fase 4, verifica 3: stabilita' nel tempo
# ---------------------------------------------------------------------------


def _trade(ts, r):
    return Trade("M", 0, 1, ts, 100.0, 99.0, None, 2, ts, 100.0, "tempo", 1.0, 1.0, 0.0, 0.0, r, r,
                 False, False, 1)


def _ris(lista):
    return Risultato([_trade(ts, r) for ts, r in lista], 0, 0)


B1, B2, B3, B4 = _ms("2020-01-15"), _ms("2020-08-01"), _ms("2021-06-01"), _ms("2022-03-01")


def test_fase4_blocchi_sono_quelli_del_protocollo():
    """Dall'inizio al 2020-06-30; 2020-07-01 -> 2021-03-31; 2021-04-01 -> 2021-12-31; 2022-01-01 ->
    2022-09-30 (giorni UTC compresi). SCELTA: un trade sta nel blocco della sua candela di ingresso."""
    bordi = [(_ms("2019-09-08"), 0), (_ms("2020-07-01") - ORA, 0), (_ms("2020-07-01"), 1),
             (_ms("2021-04-01") - 1, 1), (_ms("2021-04-01"), 2), (_ms("2022-01-01") - ORA, 2),
             (_ms("2022-01-01"), 3), (_ms("2022-10-01") - ORA, 3)]
    out = st.stabilita_blocchi(_ris([(ts, 1.0) for ts, _ in bordi]))
    assert [b["trade"] for b in out["blocchi"]] == [2, 2, 2, 2]
    for ts, k in bordi:
        o = st.stabilita_blocchi(_ris([(ts, 1.0)]))
        assert [b["trade"] for b in o["blocchi"]] == [int(i == k) for i in range(4)]


@pytest.mark.parametrize("lista,positivi,supera", [
    ([(B1, 1), (B2, 1), (B3, 1), (B4, 1)], 4, True),
    ([(B1, 1), (B2, 1), (B3, 1), (B4, -0.5)], 3, True),  # un blocco negativo e' ammesso
    ([(B1, 1), (B2, 1), (B3, 1)], 3, True),  # blocco vuoto: non positivo, ma 3 su 4 bastano
    ([(B1, 1), (B2, 1)], 2, False),  # due blocchi vuoti
    ([(B1, 2), (B2, 1), (B3, 1), (B4, 0.0)], 3, True),  # 2/4 = esattamente il 50%: non "piu' del 50%"
    ([(B1, 2.02), (B2, 1), (B3, 1), (B4, -0.02)], 3, False),  # 2,02/4 = 50,5%
    ([(B1, 1), (B2, 1), (B3, 0.0), (B4, 0.0)], 2, False),  # quote del 50% ma solo 2 blocchi positivi
    ([(B1, 10), (B2, 10), (B3, 10), (B4, -25)], 3, False),  # somma 5: il primo blocco fa il 200%
    ([(B1, 0.1), (B2, 0.1), (B3, 0.1), (B4, -1)], 3, False),  # somma negativa
    ([(B1, 3), (B1, -2.5), (B2, 1), (B3, 1), (B4, 1)], 4, True),  # conta l'R medio del blocco, non il segno dei trade
])
def test_fase4_stabilita_blocchi(lista, positivi, supera):
    """R medio positivo in almeno 3 blocchi su 4, e nessun blocco fa piu' del 50% della somma degli R."""
    out = st.stabilita_blocchi(_ris(lista))
    assert out["positivi"] == positivi
    assert out["supera"] is supera


# ---------------------------------------------------------------------------
# Fase 4, verifica 4: senza i trade migliori
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("n,tolti", [(1, 1), (20, 1), (21, 2), (100, 5), (150, 8), (151, 8), (160, 8), (161, 9)])
def test_fase4_senza_i_migliori_quanti(n, tolti):
    """Si tolgono i trade migliori, il 5% del totale. SCELTA: per eccesso (150 -> 8; sezione 14: 7-8)."""
    r = list(np.linspace(-1, 2, n))
    out = st.senza_i_migliori(_ris([(B1, x) for x in r]))
    assert out["tolti"] == tolti
    resto = sorted(r)[:n - tolti]
    if resto:
        assert out["r_medio"] == pytest.approx(sum(resto) / len(resto), abs=1e-12)
    assert out["supera"] == (bool(resto) and sum(resto) / len(resto) > 0)


def test_fase4_senza_i_migliori_toglie_i_migliori_non_i_primi():
    r = [-0.001] * 142 + [10.0] * 7 + [0.5]  # 150 trade: si tolgono gli 8 migliori, compreso lo 0,5
    np.random.default_rng(0).shuffle(r)
    out = st.senza_i_migliori(_ris([(B1, x) for x in r]))
    assert out["tolti"] == 8
    assert out["r_medio"] == pytest.approx(-0.001)
    assert out["supera"] is False


# ---------------------------------------------------------------------------
# Fase 4, verifica 1: robustezza dei parametri
# ---------------------------------------------------------------------------


def _foglie(x, via=""):
    if isinstance(x, dict):
        out = {}
        for k, y in x.items():
            out.update(_foglie(y, f"{via}.{k}" if via else k))
        return out
    if isinstance(x, (list, tuple)):
        out = {}
        for i, y in enumerate(x):
            out.update(_foglie(y, f"{via}[{i}]"))
        return out
    return {via: x}


def _uguali(a, b):
    if isinstance(a, (int, float)) and isinstance(b, (int, float)) and not isinstance(a, bool):
        return abs(a - b) < 1e-12
    return a == b


def _mosse(v):
    """Ogni mossa cambia UN solo valore della variante: restituisce (percorso, valore nuovo)."""
    base = _foglie(normalizza(v, solo_catalogo=False))
    trovate = []
    for etichetta, w in st.mosse_robustezza(v):
        fw = _foglie(w)
        assert fw.keys() == base.keys(), etichetta
        diversi = [k for k in base if not _uguali(base[k], fw[k])]
        assert len(diversi) == 1, (etichetta, diversi)
        trovate.append((diversi[0], fw[diversi[0]]))
    return trovate


def _insieme(coppie):
    return sorted((k, round(float(x), 10)) for k, x in coppie)


PERIODI = ("n", "veloce", "lenta", "atr", "finestra", "validita", "parametri")


@pytest.mark.parametrize("variante,attese", [
    ({"timeframe": "4h", "direzione": "long", "filtro": {"codice": "F1", "n": 200, "lato": "sopra"},
      "ingresso": {"codice": "E6", "n": 14, "soglie": [30, 70]}, "conferma": {"codice": "C1", "soglia": 1.5},
      "tipo_ingresso": {"codice": "L", "k": 0.5, "validita": 3}, "stop": {"codice": "S1", "k": 1.5},
      "uscite": [{"codice": "U1", "k": 2.0}, {"codice": "U3", "k": 3.0}]},
     [("filtro.n", 160), ("filtro.n", 240), ("ingresso.n", 11), ("ingresso.n", 17),
      # long senza U4: si sposta solo la soglia bassa (quella alta non la usa nessuno)
      ("ingresso.soglie[0]", 34), ("ingresso.soglie[0]", 26),
      ("conferma.n", 16), ("conferma.n", 24), ("conferma.soglia", 1.2),
      ("conferma.soglia", 1.8), ("tipo_ingresso.k", 0.4), ("tipo_ingresso.k", 0.6),
      ("tipo_ingresso.validita", 2), ("tipo_ingresso.validita", 4), ("tipo_ingresso.atr", 11),
      ("tipo_ingresso.atr", 17), ("stop.k", 1.2), ("stop.k", 1.8), ("stop.atr", 11), ("stop.atr", 17),
      ("uscite[0].k", 1.6), ("uscite[0].k", 2.4), ("uscite[1].k", 2.4), ("uscite[1].k", 3.6),
      ("uscite[1].atr", 11), ("uscite[1].atr", 17)]),
    ({"timeframe": "1h", "direzione": "long", "filtro": {"codice": "F4", "lato": "sopra"},
      "ingresso": {"codice": "E9"}, "conferma": {"codice": "C3"}, "tipo_ingresso": {"codice": "M"},
      "stop": {"codice": "S3", "pct": 0.02}, "uscite": [{"codice": "U2", "n": 24}, {"codice": "U4"}]},
     [("filtro.soglia", 0.00025), ("filtro.soglia", 0.00035), ("ingresso.parametri[0]", 10),
      ("ingresso.parametri[0]", 14), ("ingresso.parametri[1]", 21), ("ingresso.parametri[1]", 31),
      ("ingresso.parametri[2]", 7), ("ingresso.parametri[2]", 11), ("conferma.n", 11), ("conferma.n", 17),
      ("stop.pct", 0.016), ("stop.pct", 0.024), ("uscite[0].n", 19), ("uscite[0].n", 29)]),
    # mosse che dopo l'arrotondamento non cambiano il valore: funding 0,00% e validita' 1 non si provano
    ({"timeframe": "1h", "direzione": "long", "filtro": {"codice": "F4", "lato": "sotto"},
      "ingresso": {"codice": "E8"}, "conferma": None, "tipo_ingresso": {"codice": "L", "k": 0.25, "validita": 1},
      "stop": {"codice": "S2", "n": 5}, "uscite": [{"codice": "U1", "k": 1.5}, {"codice": "U2s"}]},
     [("ingresso.parametri[0]", 11), ("ingresso.parametri[0]", 17), ("ingresso.parametri[1]", 2),
      ("ingresso.parametri[1]", 4), ("ingresso.parametri[2]", 2), ("ingresso.parametri[2]", 4),
      ("ingresso.soglie[0]", 26), ("ingresso.soglie[0]", 14), ("tipo_ingresso.k", 0.2), ("tipo_ingresso.k", 0.3),
      ("tipo_ingresso.atr", 11), ("tipo_ingresso.atr", 17), ("stop.n", 4), ("stop.n", 6),
      ("uscite[0].k", 1.2), ("uscite[0].k", 1.8)]),
    # SCELTE del modulo: soglie di ADX e ATR percentile all'intero, Bollinger a 0,1, S3 allo 0,1%
    ({"timeframe": "4h", "direzione": "long", "filtro": {"codice": "F3", "regime": "alta"},
      "ingresso": {"codice": "E3", "n": 20}, "conferma": None, "tipo_ingresso": {"codice": "M"},
      "stop": {"codice": "S1", "k": 1.0}, "uscite": [{"codice": "U2", "n": 6}]},
     [("filtro.atr", 11), ("filtro.atr", 17), ("filtro.finestra", 400), ("filtro.finestra", 600),
      ("filtro.soglia", 56), ("filtro.soglia", 84), ("ingresso.n", 16), ("ingresso.n", 24),
      ("stop.k", 0.8), ("stop.k", 1.2), ("stop.atr", 11), ("stop.atr", 17), ("uscite[0].n", 5),
      ("uscite[0].n", 7)]),
    ({"timeframe": "4h", "direzione": "short", "filtro": {"codice": "F2", "regime": "laterale"},
      "ingresso": {"codice": "E4", "k": 2.5}, "conferma": None, "tipo_ingresso": {"codice": "M"},
      "stop": {"codice": "S3", "pct": 0.03}, "uscite": [{"codice": "U3", "k": 2.0}]},
     [("filtro.n", 11), ("filtro.n", 17), ("filtro.soglia", 16), ("filtro.soglia", 24), ("ingresso.k", 2.0),
      ("ingresso.k", 3.0), ("ingresso.n", 16), ("ingresso.n", 24), ("stop.pct", 0.024), ("stop.pct", 0.036),
      ("uscite[0].k", 1.6), ("uscite[0].k", 2.4), ("uscite[0].atr", 11), ("uscite[0].atr", 17)]),
    ({"timeframe": "1h", "direzione": "long", "filtro": None,
      "ingresso": {"codice": "E1", "media": "EMA", "veloce": 9, "lenta": 20},
      "conferma": {"codice": "C1", "soglia": 2.0}, "tipo_ingresso": {"codice": "M"},
      "stop": {"codice": "S2", "n": 20}, "uscite": [{"codice": "U1", "k": 3.0}]},
     [("ingresso.veloce", 7), ("ingresso.veloce", 11), ("ingresso.lenta", 16), ("ingresso.lenta", 24),
      ("conferma.n", 16), ("conferma.n", 24), ("conferma.soglia", 1.6), ("conferma.soglia", 2.4),
      ("stop.n", 16), ("stop.n", 24), ("uscite[0].k", 2.4), ("uscite[0].k", 3.6)]),
], ids=["F1_E6_C1_L_S1_U1_U3", "F4_E9_C3_S3_U2_U4", "mosse_saltate_F4_E8_L1_S2", "F3_E3_S1_U2",
        "F2_E4_S3_U3", "E1_C1_S2_U1"])
def test_fase4_mosse_robustezza(variante, attese):
    """Verifica 1: ogni parametro numerico +-20%, uno alla volta. Interi per periodi e numero di candele;
    0,1 per multipli di ATR e di R; RSI e stocastico: 20% della distanza da 50; funding a 0,005%."""
    trovate = _mosse(variante)
    assert _insieme(trovate) == _insieme(attese)
    for via, x in trovate:
        foglia = via.split(".")[-1].split("[")[0]
        if foglia in PERIODI:
            assert isinstance(x, int) and not isinstance(x, bool), via
        if foglia == "k":
            assert abs(x * 10 - round(x * 10)) < 1e-9, via


@pytest.mark.parametrize("soglia,attese", [(0.0003, [0.00025, 0.00035]), (0.0005, [0.0004, 0.0006]),
                                           (-0.0001, [])])
def test_fase4_robustezza_soglia_di_funding_e11(soglia, attese):
    """Verifica 1 su E11: la soglia di funding si sposta del 20% e si arrotonda a 0,005% (-0,01% resta
    -0,010%: nessuna mossa). Il lato non cambia: una soglia alta resta «funding sopra la soglia»."""
    s = serie_casuale(600)
    v = _v(ingresso={"codice": "E11", "soglia": soglia}, uscite=[{"codice": "U2", "n": 12}])
    mosse = [(k, x) for k, x in _mosse(v) if k == "ingresso.soglia"]
    assert _insieme(mosse) == _insieme([("ingresso.soglia", x) for x in attese])
    prima = prima_candela_dopo_regolamento(s.ts, s.funding_ts)
    f = funding_regolato(s.ts, s.durata, s.funding_ts, s.funding_tasso)
    for etichetta, w in st.mosse_robustezza(v):
        nuova = w["ingresso"]["soglia"]
        if _uguali(nuova, soglia):
            continue
        c = compila(w, s, solo_catalogo=False)
        with np.errstate(invalid="ignore"):
            atteso = prima & ((f > nuova) if soglia > 0 else (f < nuova))
        np.testing.assert_array_equal(c.dettagli["ingresso"], atteso, err_msg=etichetta)


# ---------------------------------------------------------------------------
# Fase 4, verifica 2: timeframe adiacenti
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("tf,modifiche,atteso", [
    ("1h", {}, ["30m", "2h"]),
    ("15m", {}, ["30m"]),
    ("1d", {}, ["12h"]),
    ("4h", {}, ["2h", "6h"]),
    ("1h", {"ingresso": {"codice": "E10"}}, ["30m"]),
    ("1h", {"filtro": {"codice": "F5", "sessione": "europa"}}, ["30m"]),
    ("1h", {"filtro": {"codice": "F7", "lato": "sopra"}}, ["30m"]),
    ("1h", {"uscite": [{"codice": "U2s"}]}, ["30m"]),
    ("30m", {"ingresso": {"codice": "E10"}}, ["15m", "1h"]),  # 1h e' ancora ammesso (ambiguita' nel report)
])
def test_fase4_timeframe_adiacenti(tf, modifiche, atteso):
    """Verifica 2: timeframe precedente e successivo dell'elenco; se un elemento e' ammesso solo fino a 1h,
    il timeframe piu' lungo non si prova."""
    assert st.timeframe_adiacenti(tf, _v(timeframe=tf, **modifiche)) == atteso


def test_fase4_timeframe_adiacenti_riscala_i_periodi_come_nell_esempio():
    """«EMA 50 su 1h diventa EMA 100 su 30m e EMA 25 su 2h»; orari, soglie e multipli non cambiano."""
    v = _v(filtro={"codice": "F1", "n": 50, "lato": "sopra"}, ingresso={"codice": "E6", "n": 14, "soglie": [30, 70]},
           tipo_ingresso={"codice": "L", "k": 0.5, "validita": 3}, stop={"codice": "S1", "k": 1.5},
           uscite=[{"codice": "U1", "k": 2.0}, {"codice": "U2", "n": 12}])
    for tf, f, (ema, rsi, atr, u2, val) in (("30m", 2.0, (100, 28, 28, 24, 6)), ("2h", 0.5, (25, 7, 7, 6, 2))):
        assert TIMEFRAME_MS["1h"] / TIMEFRAME_MS[tf] == f
        w = sposta_periodi(v, f)
        assert (w["filtro"]["n"], w["ingresso"]["n"], w["stop"]["atr"], w["uscite"][1]["n"],
                w["tipo_ingresso"]["validita"]) == (ema, rsi, atr, u2, val)
        assert w["ingresso"]["soglie"] == [30.0, 70.0]
        assert (w["stop"]["k"], w["uscite"][0]["k"], w["tipo_ingresso"]["k"]) == (1.5, 2.0, 0.5)


# ---------------------------------------------------------------------------
# Fase 4 completa
# ---------------------------------------------------------------------------


def _serie_di_casuali(minuti_base, n_base, inizio="2020-11-01"):
    def serie_di(tf):
        n = int(n_base * minuti_base * 60_000 / TIMEFRAME_MS[tf])
        s2 = serie_casuale(n, tf=tf, seme=11, inizio=inizio)
        return s2, 0, len(s2) - 1
    return serie_di


@pytest.mark.parametrize("variante,decisive", [(V_MERCATO, DECISIVE_MERCATO), (V_LIMIT, DECISIVE_LIMIT)],
                         ids=["mercato", "limit"])
def test_fase4_undici_verifiche_e_flag_candidato(serie, variante, decisive):
    """Le undici verifiche (8 e 11 solo per gli ingressi limit); candidato = tutte le verifiche da 1 a 8
    superate (da 1 a 7 per gli ingressi a mercato)."""
    fine = len(serie) - 1
    base = st.fase2(variante, serie, 0, fine, n_simulazioni=20)
    out = st.fase4(variante, serie, 0, fine, _serie_di_casuali(60, len(serie)), base=base)
    limit = variante["tipo_ingresso"]["codice"] == "L"
    attese = set(decisive) | {"9_intrabarra_opposta", "10_ritardo", "candidato"}
    if limit:
        attese |= {"11_versione_a_mercato"}
    assert set(out) == attese
    assert out["candidato"] == all(out[k]["supera"] for k in decisive)

    c = base["compilata"]
    r0 = base["metriche"]["r_medio"]
    mosse = st.mosse_robustezza(variante)
    assert len(out["1_robustezza"]["prove"]) == len(mosse)
    provate = [p for p in out["1_robustezza"]["prove"] if "r_medio" in p]
    assert out["1_robustezza"]["supera"] == (bool(provate) and all(p["r_medio"] > 0 for p in provate))
    assert [p["timeframe"] for p in out["2_timeframe_adiacenti"]["prove"]] == ["30m", "2h"]
    assert out["3_blocchi"] == st.stabilita_blocchi(base["risultato"])
    assert out["4_senza_i_migliori"] == st.senza_i_migliori(base["risultato"])
    md = metriche(esegui(c, Regole(), COSTI_DOPPI, 0, fine), serie)
    assert out["5_costi_doppi"] == {"r_medio": md["r_medio"], "supera": md["r_medio"] > 0}
    assert out["6_troncamento"] == {"differenze": [], "supera": True}
    assert out["7_liquidazione"]["violazioni"] == base["metriche"]["violazioni_liquidazione"]
    mi = metriche(esegui(c, Regole(intrabarra="target_prima"), COSTI_NORMALI, 0, fine), serie)
    assert out["9_intrabarra_opposta"]["differenza"] == pytest.approx(mi["r_medio"] - r0, abs=1e-12)
    mr = metriche(esegui(c, Regole(ritardo=1), COSTI_NORMALI, 0, fine), serie)
    assert out["10_ritardo"]["r_medio"] == mr["r_medio"]
    if limit:
        ms = metriche(esegui(c, Regole(scarto_riempimento=0.0005), COSTI_NORMALI, 0, fine), serie)
        assert out["8_riempimento_severo"]["r_medio"] == ms["r_medio"]
        assert out["8_riempimento_severo"]["supera"] == (ms["r_medio"] > 0)
        assert ms["trade"] <= base["metriche"]["trade"]
        mercato = dict(variante, tipo_ingresso={"codice": "M"})
        mm = metriche(esegui(compila(mercato, serie), Regole(), COSTI_NORMALI, 0, fine), serie)
        assert out["11_versione_a_mercato"]["r_medio"] == mm["r_medio"]


def test_fase4_candidato_con_un_vantaggio_vero(vantaggio):
    """La strada in cui tutto passa: il vantaggio inserito regge a tutte le verifiche decisive."""
    s, base = vantaggio

    def serie_di(tf):
        x = serie_con_vantaggio(tf)
        return x, 0, len(x) - 1

    out = st.fase4(V_VANTAGGIO, s, 0, len(s) - 1, serie_di, base=base)
    assert all(b["trade"] > 0 for b in out["3_blocchi"]["blocchi"])
    assert [p["timeframe"] for p in out["2_timeframe_adiacenti"]["prove"]] == ["2h", "6h"]
    for k in DECISIVE_MERCATO:
        assert out[k]["supera"], (k, out[k])
    assert out["candidato"] is True


def test_fase4_gira_anche_su_una_variante_e11():
    """E11 (funding oltre soglia) e' un segnale del catalogo: la Fase 4 deve poterlo verificare."""
    s = serie_casuale(600)
    v = _v(ingresso={"codice": "E11", "soglia": 0.0003}, uscite=[{"codice": "U2", "n": 12}])
    base = st.fase2(v, s, 0, len(s) - 1, n_simulazioni=20)
    assert base["metriche"]["trade"] > 0
    out = st.fase4(v, s, 0, len(s) - 1, _serie_di_casuali(60, len(s)), base=base)
    assert set(DECISIVE_MERCATO) <= set(out) and "candidato" in out


def test_fase4_verifica_8_riempimento_severo_almeno_0_05_percento(serie):
    """Verifica 8: «L'ordine è eseguito solo se il prezzo supera il limit di ALMENO lo 0,05%». Con la regola
    normale toccare il limit non basta (7.7, regola 2). La Fase 4 la esegue con scarto_riempimento=0,0005
    (controllato in test_fase4_undici_verifiche_e_flag_candidato)."""
    c0 = compila(V_LIMIT, serie)
    i = int(np.flatnonzero(c0.segnale)[0])
    a = float(c0.atr_limite[i])
    lim = float(serie.close[i]) - 1.0 * 0.25 * a

    def esito(minimo, scarto):
        op, hi, lo, cl = (x.copy() for x in (serie.open, serie.high, serie.low, serie.close))
        for k in (i + 1, i + 2, i + 3):  # le tre candele di validita' restano sopra il limit...
            op[k], cl[k], hi[k], lo[k] = lim * 1.002, lim * 1.002, lim * 1.003, lim * 1.001
        lo[i + 1] = minimo  # ...tranne il minimo della prima
        s2 = Serie("1h", serie.ts, op, hi, lo, cl, serie.volume, op, hi, lo, cl, serie.funding_ts,
                   serie.funding_tasso)
        c = compila(V_LIMIT, s2)
        assert float(c.atr_limite[i]) == a  # l'ordine alla candela i e' lo stesso
        return simula_da(c, i, Regole(scarto_riempimento=scarto), COSTI_NORMALI, len(s2) - 1)

    assert esito(lim, 0.0).tipo == "limite_non_eseguito"  # toccare non basta
    assert esito(lim * (1 - 1e-9), 0.0).tipo == "trade"
    assert esito(lim * (1 - 0.0004), 0.0005).tipo == "limite_non_eseguito"  # solo 0,04% oltre
    assert esito(lim * (1 - 0.0006), 0.0005).tipo == "trade"
    e = esito(lim * (1 - 1.0 * 0.0005), 0.0005)  # esattamente 0,05% oltre il limit: «almeno» -> eseguito
    assert e.tipo == "trade" and e.trade.indice_ingresso == i + 1


def test_fase4_mosse_robustezza_con_u4_spostano_anche_la_soglia_opposta():
    """Con l'uscita U4 il segnale opposto usa l'altra soglia di E6: anche quella si sposta."""
    v = {"timeframe": "4h", "direzione": "long", "filtro": None,
         "ingresso": {"codice": "E6", "n": 14, "soglie": [30, 70]}, "conferma": None,
         "tipo_ingresso": {"codice": "M"}, "stop": {"codice": "S1", "k": 1.5}, "uscite": [{"codice": "U4"}]}
    etichette = [e for e, _ in st.mosse_robustezza(v)]
    assert any("soglie[0]" in e for e in etichette) and any("soglie[1]" in e for e in etichette)


def test_timeframe_adiacenti_arrotondano_le_meta_per_eccesso():
    """EMA 9 da 1h a 2h: 4,5 diventa 5 (non 4, come con l'arrotondamento al pari)."""
    from research.src.catalogo3 import sposta_periodi
    v = {"timeframe": "1h", "direzione": "long", "filtro": None,
         "ingresso": {"codice": "E1", "media": "EMA", "veloce": 9, "lenta": 20}, "conferma": None,
         "tipo_ingresso": {"codice": "M"}, "stop": {"codice": "S1", "k": 1.5}, "uscite": [{"codice": "U2", "n": 12}]}
    w = sposta_periodi(v, 0.5)
    assert w["ingresso"]["veloce"] == 5 and w["ingresso"]["lenta"] == 10 and w["uscite"][0]["n"] == 6


# ---------------------------------------------------------------------------
# 10.1, correzione 1 del collaudo (17 ott 2026): stessa larghezza dello stop del candidato
# ---------------------------------------------------------------------------

V_STOP_VARIABILE = _v(ingresso={"codice": "E3", "n": 20}, stop={"codice": "S2", "n": 10},
                      uscite=[{"codice": "U1", "k": 2.0}, {"codice": "U2", "n": 12}])


def test_10_1_le_entrate_casuali_hanno_la_larghezza_di_stop_del_candidato(spia):
    """Con uno stop che cambia larghezza (minimo delle ultime 10 candele) e un ingresso dopo una rottura
    del massimo di 20 candele (stop piu' larghi del solito), le larghezze dei trade casuali si
    distribuiscono nelle 5 fasce come quelle del candidato, non come quelle di tutte le candele."""
    registro, _ = spia
    s = serie_casuale(3000, seme=11, sigma=0.006)
    c = compila(V_STOP_VARIABILE, s)
    ris = esegui(c, Regole(), COSTI_NORMALI, 0, len(s) - 1)
    n = len(ris.trade)
    assert n >= 40
    out = st.entrate_casuali(c, n, 0, len(s) - 1, n_simulazioni=200)
    q = out["quote_larghezza"]
    tagli = np.asarray(q["tagli"])
    fasce_casuali = np.searchsorted(tagli, [st.larghezza_stop(t) for _, t in registro], side="right")
    quota_casuali = np.bincount(fasce_casuali, minlength=5) / len(fasce_casuali)
    assert np.allclose(quota_casuali, q["candidato"], atol=0.03), (quota_casuali, q)
    # e senza la regola la distribuzione sarebbe un'altra (quella di tutte le candele ammesse)
    assert np.abs(np.asarray(q["candele_ammesse"]) - np.asarray(q["candidato"])).max() > 0.05


def test_10_1_con_lo_stop_fisso_in_percentuale_nessun_peso(serie):
    """Con lo stop S3 tutte le larghezze sono uguali: una sola fascia piena, nessuna candela pesa diversamente."""
    c = compila(V_MERCATO, serie)
    ris = esegui(c, Regole(), COSTI_NORMALI, 0, len(serie) - 1)
    out = st.entrate_casuali(c, len(ris.trade), 0, len(serie) - 1, n_simulazioni=50)
    q = out["quote_larghezza"]
    assert max(q["candidato"]) == pytest.approx(1.0) and max(q["candele_ammesse"]) == pytest.approx(1.0)


def test_10_1_le_larghezze_si_prendono_dal_candidato_se_non_si_passano(serie):
    c = compila(V_SHORT, serie)
    ris = esegui(c, Regole(), COSTI_NORMALI, 0, len(serie) - 1)
    larg = [st.larghezza_stop(t) for t in ris.trade]
    a = st.entrate_casuali(c, len(ris.trade), 0, len(serie) - 1, n_simulazioni=50)
    b = st.entrate_casuali(c, len(ris.trade), 0, len(serie) - 1, n_simulazioni=50, larghezze_candidato=larg)
    assert np.array_equal(a["valori"], b["valori"])


def test_10_2_un_pareggio_all_ultima_cifra_conta_come_pareggio():
    """Correzione del 17 ottobre 2026: una simulazione con R medio piu' basso del candidato di 5,6e-17 (stessi
    trade sommati in un altro ordine) conta come «maggiore o uguale»; una piu' bassa di un millesimo di R no."""
    c = -0.2699730026997294
    valori = np.full(1000, -1.0)
    valori[:3] = c - 5.6e-17
    valori[3:5] = c - 1e-3
    assert st.p_value(c, valori) == pytest.approx(4 / 1001)

