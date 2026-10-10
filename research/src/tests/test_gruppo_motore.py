"""Gli strumenti del motore per la campagna di gruppo (campagne/GRUPPO/regole.md, sezione 13).

* ``simula_baseline_casuale``: la chiave ``r_medio_per_seme`` (sezione 5, punto 4)
  e ``rifiuta_poche_simulazioni=False``; con il predefinito il risultato e'
  identico a quello di prima (copia congelata qui sotto).
* ``simula_sfasamento_comune``: le strategie sfasate (sezione 5, punto 5, e
  sezione 9, punto 3): lo stesso spostamento su tutte le monete, in cerchio sulla
  finestra unione, con gli ingressi saltati contati per motivo e un'istanza nuova
  della strategia casuale a ogni s.
* ``metriche_di_gruppo`` (sezione 9, punto 2) e ``posizioni_aperte_insieme``
  (sezione 8, punto 2), calcolate a mano.
* ``somme_dei_trade`` e ``metriche_di_gruppo_da_somme`` (sezione 9, punto 4: le
  sfasate del vault): a mano, e sugli stessi trade uguali a ``metriche_di_gruppo``
  (lo stesso numero di trade; profit factor, rendimento e R medio entro 1e-12
  relativo).

Candele da 1 ora. Nei test degli sfasamenti la barra in posizione p ha
ts = T0 + p * ORA, con T0 la mezzanotte UTC del 2022-01-01: la posizione e'
quella sul calendario, l'indice nella serie puo' essere diverso (buchi, serie
che partono dopo).
"""
import inspect
import math
import pickle
from datetime import datetime, timezone

import numpy as np
import pytest

from research.src import motore
from research.src import statistica as st
from research.src.motore import Candela, Parametri, Segnale, TradeSfasato

ORA = 3_600_000
T0 = 1_640_995_200_000  # 2022-01-01 00:00 UTC


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


def candela_pos(p: int, livello: float = 100.0) -> Candela:
    """La barra in posizione p sul calendario (ts = T0 + p ore), prezzi lontani da ogni stop."""
    o = livello + (p % 7)
    return Candela(ts=T0 + p * ORA, open=o, high=o + 1.0, low=o - 1.0, close=o + 0.5, volume=1.0,
                   close_ts=T0 + p * ORA + ORA - 1)


def serie_su_posizioni(posizioni, livello: float = 100.0):
    return [candela_pos(p, livello) for p in posizioni]


def finestra(da_pos: int, a_pos_inclusa: int):
    """(inizio, fine INCLUSA) in ms dalla barra da_pos alla barra a_pos_inclusa."""
    return (T0 + da_pos * ORA, T0 + (a_pos_inclusa + 1) * ORA - 1)


def crea_casuale_fabbrica(durata: int = 3, registro=None, valido=lambda ingressi: True):
    """La fabbrica della strategia casuale: long alle barre di ``ingressi``, chiude dopo ``durata`` barre.

    ``registro`` (lista) riceve l'insieme degli ingressi di ogni istanza creata.
    Se ``valido(ingressi)`` e' falso lo stop sta sopra il prezzo: il motore scarta
    ogni segnale e la simulazione resta senza trade.
    """

    def crea(ingressi):
        if registro is not None:
            registro.append(ingressi)
        ok = valido(ingressi)
        stato = {"entrata_i": None, "ultima_len": 0}

        def strategia(storia, posizione):
            if len(storia) <= stato["ultima_len"]:
                raise RuntimeError("istanza della strategia riusata: serve un'istanza nuova a ogni esecuzione")
            stato["ultima_len"] = len(storia)
            i = len(storia) - 1
            if posizione is None:
                stato["entrata_i"] = None
                if i in ingressi:
                    c = storia[-1].close
                    return Segnale("long", stop=c * (0.5 if ok else 1.5))
                return None
            if stato["entrata_i"] is None:
                stato["entrata_i"] = i
            if i - stato["entrata_i"] >= durata - 1:
                return "chiudi"
            return None

        return strategia

    return crea


# ---------------------------------------------------------------------------
# simula_baseline_casuale: r_medio_per_seme e rifiuta_poche_simulazioni
# ---------------------------------------------------------------------------


def _simula_baseline_casuale_fino_al_10_ottobre(candele, crea_strategia_casuale, n_trade, durata_media, parametri,
                                                 candele_stop=None, candele_mark=None, funding=(), barre_vietate=(),
                                                 n_simulazioni=200, primo_seme=0):
    """Copia congelata del corpo di ``motore.simula_baseline_casuale`` prima della campagna di gruppo."""
    if n_trade < 1:
        raise ValueError("n_trade deve essere almeno 1")
    vietate = list(barre_vietate) + [(len(candele) - 1, len(candele))]
    r_medi, trade_per_sim, non_validi, senza_barra = [], [], [], []
    vuote = 0
    semi = list(range(primo_seme, primo_seme + n_simulazioni))
    tutti_gli_ingressi = st.entrate_casuali_per_semi(len(candele), n_trade, durata_media, semi, vietate)
    for ingressi_lista in tutti_gli_ingressi:
        strategia = crea_strategia_casuale(frozenset(ingressi_lista))
        ris = motore.esegui(candele, candele_stop, candele_mark, list(funding), strategia, parametri)
        non_validi.append(ris.n_segnali_non_validi)
        senza_barra.append(ris.n_segnali_senza_barra)
        if not ris.trades:
            vuote += 1
            continue
        r_medi.append(sum(t.r for t in ris.trades) / len(ris.trades))
        trade_per_sim.append(len(ris.trades))
    if len(r_medi) < 2:
        raise ValueError(f"simula_baseline_casuale: solo {len(r_medi)} simulazioni con trade su {n_simulazioni}")
    base = st.baseline_casuale(r_medi)
    base["trade_per_simulazione"] = trade_per_sim
    base["simulazioni_vuote"] = vuote
    base["segnali_non_validi_per_simulazione"] = non_validi
    base["segnali_senza_barra_per_simulazione"] = senza_barra
    return base


def _uguali(a, b) -> bool:
    if isinstance(a, np.ndarray) or isinstance(b, np.ndarray):
        return isinstance(a, np.ndarray) and isinstance(b, np.ndarray) and a.dtype == b.dtype and np.array_equal(a, b)
    return type(a) is type(b) and a == b


def _min_pari(ingressi) -> bool:
    return min(ingressi) % 2 == 0


def test_simula_baseline_casuale_predefinita_identica_a_prima():
    # Una parte delle simulazioni resta senza trade (stop dalla parte sbagliata
    # quando il primo ingresso e' dispari): cosi' anche simulazioni_vuote e le
    # posizioni dei None contano.
    candele = serie_a_dente(600)
    argomenti = dict(n_simulazioni=20, primo_seme=3000, barre_vietate=[(0, 15)])
    prima = _simula_baseline_casuale_fino_al_10_ottobre(
        candele, crea_casuale_fabbrica(valido=_min_pari), 40, 5, Parametri(), **argomenti)
    ora = motore.simula_baseline_casuale(candele, crea_casuale_fabbrica(valido=_min_pari), 40, 5, Parametri(),
                                         **argomenti)
    assert 0 < prima["simulazioni_vuote"] < 18  # lo scenario ha vuote e piene
    assert set(ora) == set(prima) | {"r_medio_per_seme"}
    for chiave in prima:
        assert _uguali(ora[chiave], prima[chiave]), chiave


def test_r_medio_per_seme_coerente_con_valori_e_con_i_semi():
    candele = serie_a_dente(600)
    vietate = [(0, 15)]
    ris = motore.simula_baseline_casuale(candele, crea_casuale_fabbrica(valido=_min_pari), 40, 5, Parametri(),
                                         barre_vietate=vietate, n_simulazioni=20, primo_seme=3000)
    per_seme = ris["r_medio_per_seme"]
    assert len(per_seme) == 20
    assert [x for x in per_seme if x is not None] == list(ris["valori"])
    assert sum(x is None for x in per_seme) == ris["simulazioni_vuote"]
    # la posizione s e' il seme 3000 + s: ricalcolo a mano seme per seme
    for s, valore in enumerate(per_seme):
        ingressi = st.entrate_casuali(len(candele), 40, 5, 3000 + s, vietate + [(len(candele) - 1, len(candele))])
        esec = motore.esegui(candele, None, None, [], crea_casuale_fabbrica(valido=_min_pari)(frozenset(ingressi)),
                             Parametri())
        if esec.trades:
            assert valore == sum(t.r for t in esec.trades) / len(esec.trades)
        else:
            assert valore is None and not _min_pari(ingressi)


def test_rifiuta_poche_simulazioni_false_restituisce_comunque_semi_e_conteggi():
    candele = serie_a_dente(600)
    vietate_tutte = [(0, 15), (len(candele) - 1, len(candele))]
    semi = list(range(7000, 7010))
    primo = tuple(st.entrate_casuali_per_semi(len(candele), 40, 5, semi, vietate_tutte)[0])

    def solo_il_primo(ingressi):
        return tuple(sorted(ingressi)) == primo

    argomenti = dict(barre_vietate=[(0, 15)], n_simulazioni=10, primo_seme=7000)
    # predefinito: una sola simulazione con trade -> ValueError come sempre
    with pytest.raises(ValueError, match="solo 1 simulazioni"):
        motore.simula_baseline_casuale(candele, crea_casuale_fabbrica(valido=solo_il_primo), 40, 5, Parametri(),
                                       **argomenti)
    ris = motore.simula_baseline_casuale(candele, crea_casuale_fabbrica(valido=solo_il_primo), 40, 5, Parametri(),
                                         rifiuta_poche_simulazioni=False, **argomenti)
    assert set(ris) == {"r_medio_per_seme", "trade_per_simulazione", "simulazioni_vuote",
                        "segnali_non_validi_per_simulazione", "segnali_senza_barra_per_simulazione"}
    assert ris["r_medio_per_seme"][0] is not None and ris["r_medio_per_seme"][1:] == [None] * 9
    assert ris["simulazioni_vuote"] == 9 and len(ris["trade_per_simulazione"]) == 1
    assert len(ris["segnali_non_validi_per_simulazione"]) == 10
    with pytest.raises(ValueError):  # non si passa a contro_baseline per sbaglio
        st.contro_baseline([0.1] * 30, 1, ris)
    # nessuna simulazione con trade
    vuota = motore.simula_baseline_casuale(candele, crea_casuale_fabbrica(valido=lambda i: False), 40, 5, Parametri(),
                                           rifiuta_poche_simulazioni=False, **argomenti)
    assert vuota["r_medio_per_seme"] == [None] * 10 and vuota["simulazioni_vuote"] == 10
    # con almeno 2 simulazioni con trade il risultato e' quello del predefinito
    a = motore.simula_baseline_casuale(candele, crea_casuale_fabbrica(valido=_min_pari), 40, 5, Parametri(),
                                       **argomenti)
    b = motore.simula_baseline_casuale(candele, crea_casuale_fabbrica(valido=_min_pari), 40, 5, Parametri(),
                                       rifiuta_poche_simulazioni=False, **argomenti)
    assert set(a) == set(b) and all(_uguali(a[k], b[k]) for k in a)


# ---------------------------------------------------------------------------
# simula_sfasamento_comune
# ---------------------------------------------------------------------------


def _sfasa(candele, crea, ts_segnali, unione, moneta, sfasamenti, vietate=(), parametri=None):
    return motore.simula_sfasamento_comune(candele, crea, ts_segnali, unione, moneta, ORA, sfasamenti,
                                           parametri or Parametri(), barre_vietate=vietate)


def test_spostamento_a_mano_in_cerchio_sulla_finestra():
    # Finestra unione di 24 barre (L = 24), la moneta la copre tutta: indice = posizione.
    # Segnali alle posizioni 2 e 18. d = 0 -> 2, 18; d = 3 -> 5, 21; d = 5 -> 7, 23
    # (23 e' l'ultima barra: vietata come nella (b)); d = 10 -> 12, 28 mod 24 = 4.
    candele = serie_su_posizioni(range(24))
    registro = []
    ris = _sfasa(candele, crea_casuale_fabbrica(3, registro), [T0 + 2 * ORA, T0 + 18 * ORA],
                 finestra(0, 23), finestra(0, 23), [0, 3, 5, 10])
    assert ris["L"] == 24 and ris["n_segnali"] == 2 and ris["sfasamenti"] == [0, 3, 5, 10]
    assert registro == [frozenset({2, 18}), frozenset({5, 21}), frozenset({7}), frozenset({4, 12})]
    assert [s["d"] for s in ris["per_sfasamento"]] == [0, 3, 5, 10]
    assert ris["per_sfasamento"][2]["saltati"] == {"fuori_finestra": 0, "buco": 0, "vietata": 1, "posizione_aperta": 0}
    assert [len(s["trade"]) for s in ris["per_sfasamento"]] == [2, 2, 1, 2]
    # i trade sono quelli del motore sugli stessi ingressi
    for registrati, sfasata in zip(registro, ris["per_sfasamento"]):
        diretto = motore.esegui(candele, None, None, [], crea_casuale_fabbrica(3)(registrati), Parametri())
        assert sfasata["trade"] == [TradeSfasato(t.ts_entrata, t.ts_uscita, t.r, t.pnl) for t in diretto.trades]
        assert all(isinstance(t, TradeSfasato) for t in sfasata["trade"])


def test_stesso_spostamento_su_tutte_le_monete():
    # Due monete con le stesse barre e gli stessi segnali: stessi ingressi spostati,
    # stessi trade. Una terza moneta con prezzi diversi e una serie che comincia 10
    # barre prima (indici diversi) sposta gli stessi istanti negli stessi istanti.
    unione = finestra(10, 59)  # L = 50
    segnali = [T0 + p * ORA for p in (12, 20, 33, 47, 58)]
    sfasamenti = [0, 7, 25, 44]
    reg_a, reg_b, reg_c = [], [], []
    a = _sfasa(serie_su_posizioni(range(10, 60)), crea_casuale_fabbrica(3, reg_a), segnali, unione, unione, sfasamenti)
    b = _sfasa(serie_su_posizioni(range(10, 60)), crea_casuale_fabbrica(3, reg_b), segnali, unione, unione, sfasamenti)
    serie_c = serie_su_posizioni(range(0, 60), livello=37.0)
    c = _sfasa(serie_c, crea_casuale_fabbrica(3, reg_c), segnali, unione, finestra(0, 59), sfasamenti)
    assert reg_a == reg_b and a == b
    istanti_a = [sorted(T0 + (10 + i) * ORA for i in ing) for ing in reg_a]
    istanti_c = [sorted(serie_c[i].ts for i in ing) for ing in reg_c]
    assert istanti_a == istanti_c
    # a mano, d = 44, posizione nuova = (p - 10 + 44) mod 50 + 10:
    # 12 -> 56, 20 -> 14, 33 -> 27, 47 -> 41, 58 -> 52 (nessuno sull'ultima barra, la 59)
    assert istanti_a[3] == [T0 + p * ORA for p in (14, 27, 41, 52, 56)]


def test_ingressi_saltati_contati_per_motivo():
    # Finestra unione: posizioni 0..47 (L = 48). La moneta comincia dopo: la sua
    # finestra e' 24..47 e la sua serie ha un buco alla posizione 30. Indici della
    # serie: posizioni 24..29 -> 0..5, 31..47 -> 6..22. Riscaldamento vietato: indici
    # 0..2 (posizioni 24..26); l'ultima barra (indice 22, posizione 47) e' vietata da
    # sola. Segnali del candidato alle posizioni 27, 33, 35, 44, 45; posizioni di 4 barre.
    #
    # d = 3:  27->30 buco; 33->36 (indice 11); 35->38 (indice 13); 44->47 ultima barra,
    #         vietata; 45->48 mod 48 = 0, fuori dalla finestra della moneta.
    #         Ingresso all'indice 11 -> entra a 12 e resta aperta fino alla chiusura di 15:
    #         il segnale all'indice 13 cade a posizione aperta. 1 trade.
    # d = 27: 27->6, 33->12, 35->14, 44->23 fuori; 45->72 mod 48 = 24 = indice 0, vietata.
    # d = 40: 27->67 mod 48 = 19 fuori; 33->25 = indice 1 vietata; 35->27 = indice 3;
    #         44->36 = indice 11; 45->37 = indice 12, a posizione aperta. 2 trade.
    posizioni = [p for p in range(24, 48) if p != 30]
    candele = serie_su_posizioni(posizioni)
    segnali = [T0 + p * ORA for p in (27, 33, 35, 44, 45)]
    registro = []
    ris = _sfasa(candele, crea_casuale_fabbrica(4, registro), segnali, finestra(0, 47), finestra(24, 47),
                 [3, 27, 40], vietate=[(0, 3)])
    s3, s27, s40 = ris["per_sfasamento"]
    assert registro == [frozenset({11, 13}), frozenset(), frozenset({3, 11, 12})]
    assert s3["saltati"] == {"fuori_finestra": 1, "buco": 1, "vietata": 1, "posizione_aperta": 1}
    assert s3["ingressi"] == 2 and len(s3["trade"]) == 1
    assert s27["saltati"] == {"fuori_finestra": 4, "buco": 0, "vietata": 1, "posizione_aperta": 0}
    assert s27["ingressi"] == 0 and s27["trade"] == []
    assert s40["saltati"] == {"fuori_finestra": 1, "buco": 0, "vietata": 1, "posizione_aperta": 1}
    assert s40["ingressi"] == 3 and len(s40["trade"]) == 2
    assert ris["saltati_totali"] == {"fuori_finestra": 6, "buco": 1, "vietata": 3, "posizione_aperta": 2}
    for s in ris["per_sfasamento"]:
        assert s["segnali_non_validi"] == s["segnali_senza_barra"] == s["capitale_esaurito"] == 0
        assert len(s["trade"]) + sum(s["saltati"].values()) == ris["n_segnali"]
    # i trade dello sfasamento 40 entrano dopo le barre 3 e 11 (ts delle posizioni 28 e 37)
    assert [t.ts_entrata for t in s40["trade"]] == [T0 + 28 * ORA, T0 + 37 * ORA]


def test_il_cerchio_e_sulla_finestra_unione_non_su_quella_della_moneta():
    # Unione 0..19 (L = 20), moneta 10..19. Segnale alla posizione 15, d = 7:
    # 22 mod 20 = 2, fuori dalla moneta. Un cerchio sulla sola finestra della moneta
    # (L = 10) lo avrebbe portato a 12, dentro.
    candele = serie_su_posizioni(range(10, 20))
    ris = _sfasa(candele, crea_casuale_fabbrica(2), [T0 + 15 * ORA], finestra(0, 19), finestra(10, 19), [7, 16])
    assert ris["per_sfasamento"][0]["saltati"]["fuori_finestra"] == 1
    assert ris["per_sfasamento"][0]["trade"] == []
    # d = 16: 31 mod 20 = 11, dentro (indice 1)
    assert ris["per_sfasamento"][1]["ingressi"] == 1
    assert ris["per_sfasamento"][1]["trade"][0].ts_entrata == T0 + 12 * ORA


def test_segnale_prima_della_finestra_unione_si_sposta_e_si_conta():
    # Validazione: la serie comincia prima (posizioni 0..47), la finestra unione e
    # quella della moneta sono 24..47 (L = 24) e le barre prima sono vietate. Il
    # trade entrato alla prima barra della finestra ha il segnale alla posizione 23,
    # cioe' -1 nella finestra: con d = 2 va a (-1 + 2) mod 24 = 1, posizione 25.
    candele = serie_su_posizioni(range(48))
    registro = []
    ris = _sfasa(candele, crea_casuale_fabbrica(2, registro), [T0 + 23 * ORA, T0 + 30 * ORA], finestra(24, 47),
                 finestra(24, 47), [2], vietate=[(0, 24)])
    assert ris["segnali_fuori_dalla_finestra_unione"] == 1
    assert registro == [frozenset({25, 32})]


def test_istanza_nuova_a_ogni_sfasamento():
    # La strategia della fabbrica alza RuntimeError se vede di nuovo la prima barra:
    # passa solo se ogni s usa un'istanza nuova. Una fabbrica senza argomenti e'
    # rifiutata con un messaggio che dice cosa vuole.
    candele = serie_su_posizioni(range(30))
    registro = []
    ris = _sfasa(candele, crea_casuale_fabbrica(2, registro), [T0 + 3 * ORA, T0 + 9 * ORA], finestra(0, 29),
                 finestra(0, 29), [0, 1, 2, 3, 4])
    assert len(registro) == 5 and len(ris["per_sfasamento"]) == 5
    with pytest.raises(TypeError, match="UN argomento"):
        _sfasa(candele, lambda: crea_casuale_fabbrica(2)(frozenset()), [T0 + 3 * ORA], finestra(0, 29),
               finestra(0, 29), [0])


def test_sfasamento_deterministico_e_trasportabile_fra_processi():
    posizioni = [p for p in range(0, 120) if p not in (40, 41, 77)]
    candele = serie_su_posizioni(posizioni)
    segnali = [T0 + p * ORA for p in (5, 18, 19, 52, 80, 101)]
    argomenti = (segnali, finestra(0, 119), finestra(0, 119), list(range(0, 120, 6)))
    a = _sfasa(candele, crea_casuale_fabbrica(5), *argomenti, vietate=[(0, 4)])
    b = _sfasa(candele, crea_casuale_fabbrica(5), *argomenti, vietate=[(0, 4)])
    assert a == b
    assert pickle.loads(pickle.dumps(a)) == a


def test_sfasamento_rifiuta_argomenti_sbagliati():
    candele = serie_su_posizioni(range(24))
    crea = crea_casuale_fabbrica(2)
    # fine della finestra passata ESCLUSA: la durata non e' un multiplo della barra
    with pytest.raises(ValueError, match="INCLUSA"):
        _sfasa(candele, crea, [T0], (T0, T0 + 24 * ORA), finestra(0, 23), [1])
    # istante fuori dalla griglia del calendario della finestra unione
    with pytest.raises(ValueError, match="griglia"):
        _sfasa(candele, crea, [T0 + 3 * ORA], (T0 + 60_000, T0 + 60_000 + 20 * ORA - 1), finestra(0, 23), [1])
    # istante che non e' una barra della serie
    with pytest.raises(ValueError, match="non e' una barra"):
        _sfasa(candele, crea, [T0 + 30 * ORA], finestra(0, 23), finestra(0, 23), [1])
    with pytest.raises(ValueError, match="coincidono"):
        _sfasa(candele, crea, [T0 + 3 * ORA, T0 + 3 * ORA], finestra(0, 23), finestra(0, 23), [1])


def test_segnali_che_coprono_piu_di_l_barre_con_un_buco_prima_della_finestra():
    # Validazione con il ritardo di una barra e un buco subito prima della finestra (revisione del 10 ottobre):
    # la serie va dalla posizione 0 alla 47 senza la 23; finestra unione e della moneta 24..47 (L = 24), barre
    # prima vietate. Il trade entrato alla prima barra della finestra (24) ha il segnale due barre prima nella
    # serie, alla posizione 21 (p = -3); un altro ha il segnale alla 45 (p = 21). Prima gli istanti «coprivano 25
    # barre, oltre L» e l'esame si fermava; ora lo spostamento e' una rotazione sui resti: -3 e 21 hanno lo
    # stesso resto modulo 24, quindi cadono sempre nella stessa barra. Con d = 5 vanno entrambi a (21 + 5) mod
    # 24 = 2, posizione 26 = indice 25: un ingresso solo, l'altro saltato e contato «a posizione aperta».
    posizioni = [p for p in range(48) if p != 23]
    candele = serie_su_posizioni(posizioni)
    registro = []
    ris = _sfasa(candele, crea_casuale_fabbrica(2, registro), [T0 + 21 * ORA, T0 + 45 * ORA], finestra(24, 47),
                 finestra(24, 47), [5, 2], vietate=[(0, 23)])
    assert ris["segnali_fuori_dalla_finestra_unione"] == 1 and ris["segnali_coincidenti"] == 1
    s5, s2 = ris["per_sfasamento"]
    assert registro[0] == frozenset({25})
    assert s5["ingressi"] == 2 and s5["coincidenti"] == 1 and len(s5["trade"]) == 1
    assert s5["saltati"] == {"fuori_finestra": 0, "buco": 0, "vietata": 0, "posizione_aperta": 1}
    # d = 2: (21 + 2) mod 24 = 23, posizione 47, l'ultima barra: vietata per tutti e due
    assert s2["ingressi"] == 0 and s2["coincidenti"] == 0
    assert s2["saltati"] == {"fuori_finestra": 0, "buco": 0, "vietata": 2, "posizione_aperta": 0}
    for s in ris["per_sfasamento"]:
        assert s["ingressi"] + s["saltati"]["fuori_finestra"] + s["saltati"]["buco"] + s["saltati"]["vietata"] \
            == ris["n_segnali"]
    # due istanti a distanza L - 2 (resti diversi) non coincidono
    ris = _sfasa(candele, crea_casuale_fabbrica(2), [T0 + 22 * ORA, T0 + 44 * ORA], finestra(24, 47),
                 finestra(24, 47), [5], vietate=[(0, 23)])
    assert ris["segnali_coincidenti"] == 0 and ris["per_sfasamento"][0]["ingressi"] == 2


def test_il_caso_della_revisione_a_1d_non_si_ferma():
    # serie 1d dal 2022-01-01 al 2023-12-31 senza il 2023-01-15 e il 2023-01-16; segnali al 2023-01-14 (il trade
    # entra il 2023-01-17, primo giorno di validazione) e al 2023-12-30; finestre dal 2023-01-17 al 2023-12-31.
    giorno = 86_400_000
    inizio = _ms(2023, 1, 17)
    togli = {_ms(2023, 1, 15), _ms(2023, 1, 16)}
    candele = [Candela(ts, 100.0, 101.0, 99.0, 100.5, 1.0, ts + giorno - 1)
               for ts in range(_ms(2022, 1, 1), _ms(2024, 1, 1), giorno) if ts not in togli]
    finestra_v = (inizio, _ms(2024, 1, 1) - 1)
    prima = sum(1 for c in candele if c.ts < inizio)
    ris = motore.simula_sfasamento_comune(candele, crea_casuale_fabbrica(2), [_ms(2023, 1, 14), _ms(2023, 12, 30)],
                                          finestra_v, finestra_v, giorno, [30, 100, 200], Parametri(),
                                          barre_vietate=[(0, prima)])
    assert ris["L"] == 349 and ris["segnali_fuori_dalla_finestra_unione"] == 1 and ris["segnali_coincidenti"] == 0
    assert all(s["ingressi"] == 2 for s in ris["per_sfasamento"])


# ---------------------------------------------------------------------------
# metriche_di_gruppo
# ---------------------------------------------------------------------------


def _ms(anno, mese, giorno, ora=0):
    return int(datetime(anno, mese, giorno, ora, tzinfo=timezone.utc).timestamp() * 1000)


def _trade_a_mano():
    # AAA: uscita 2022-12-31 10:00 (r 1, +10 USDT); uscita 2023-01-02 00:00 (r -1,5, -30).
    # BBB: uscita 2023-01-02 00:00, lo STESSO istante (r 2, +20); 2023-01-05 (r -0,5, -5);
    #      2023-01-06 (r -0,75, -4).
    x1, x2, x3, x4 = _ms(2022, 12, 31, 10), _ms(2023, 1, 2), _ms(2023, 1, 5), _ms(2023, 1, 6)
    return {
        "AAA": [TradeSfasato(x1 - ORA, x1, 1.0, 10.0), TradeSfasato(x2 - 5 * ORA, x2, -1.5, -30.0)],
        "BBB": [TradeSfasato(x2 - 2 * ORA, x2, 2.0, 20.0), TradeSfasato(x3 - ORA, x3, -0.5, -5.0),
                TradeSfasato(x4 - ORA, x4, -0.75, -4.0)],
    }


def test_metriche_di_gruppo_a_mano():
    # Tre monete con barre nel periodo (una senza trade), 1.000 USDT ciascuna: 3.000.
    # profit factor = (10 + 20) / (30 + 5 + 4) = 30 / 39; risultato -9 USDT;
    # rendimento -9 / 3000 = -0,003; R medio (1 - 1,5 + 2 - 0,5 - 0,75) / 5 = 0,05;
    # per anno: 2022 -> 1; 2023 -> (-1,5 + 2 - 0,5 - 0,75) / 4 = -0,1875;
    # senza i 2 migliori (2 e 1): (-1,5 - 0,5 - 0,75) / 3.
    # Curva: 3000 -> 3010 -> 3000 (le due uscite del 2 gennaio insieme: -30 + 20)
    # -> 2995 -> 2991: caduta 19 USDT dal picco 3010. In ordine di simbolo, uno per
    # volta, sarebbe passata da 2980 (caduta 30): le uscite dello stesso istante
    # entrano insieme.
    m = motore.metriche_di_gruppo(_trade_a_mano(), n_monete_nel_periodo=3, capitale_per_moneta=1000.0,
                                  trade_migliori_tolti=2)
    assert m["profit_factor"] == pytest.approx(30 / 39)
    assert m["n_trade"] == 5
    assert m["pnl_totale"] == pytest.approx(-9.0)
    assert m["capitale_totale"] == 3000.0 and m["monete_nel_periodo"] == 3 and m["monete_con_trade"] == 2
    assert m["rendimento_totale"] == pytest.approx(-0.003)
    assert m["r_medio"] == pytest.approx(0.05)
    assert m["r_medio_per_anno"] == {2022: pytest.approx(1.0), 2023: pytest.approx(-0.1875)}
    assert m["r_medio_senza_2_migliori"] == pytest.approx(-2.75 / 3)
    assert m["drawdown_max_usdt"] == pytest.approx(19.0)
    assert m["drawdown_max"] == pytest.approx(19.0 / 3010.0)
    assert m["per_moneta"] == {"AAA": {"n_trade": 2, "r_medio": pytest.approx(-0.25)},
                               "BBB": {"n_trade": 3, "r_medio": pytest.approx(0.25)}}
    # le chiavi del criterio_vault ci sono: lo stesso dizionario giudica candidato e sfasate
    esito = st.criterio_vault(m, r_caso_percentile_90=0.0, trade_minimi=0)
    assert esito["condizioni"] == {"profit_factor": False, "trade_minimi": True,
                                   "rendimento_positivo": False, "sopra_il_caso": True}


def test_metriche_di_gruppo_non_dipendono_dall_ordine_ne_dalla_forma_dei_trade():
    trade = _trade_a_mano()
    a = motore.metriche_di_gruppo(trade, 3, 1000.0)
    b = motore.metriche_di_gruppo({"BBB": list(reversed(trade["BBB"])), "AAA": trade["AAA"]}, 3, 1000.0)
    c = motore.metriche_di_gruppo({k: [t._asdict() for t in v] for k, v in trade.items()}, 3, 1000.0)
    assert a == b == c
    assert a["r_medio_senza_30_migliori"] is None  # 5 trade: non ne resta nessuno


def test_metriche_di_gruppo_con_una_moneta_uguali_a_quelle_del_motore():
    candele = serie_a_dente(400)

    def strategia_ogni_k(k, durata):
        stato = {"entrata_i": None}

        def strategia(storia, posizione):
            i = len(storia) - 1
            if posizione is None:
                stato["entrata_i"] = None
                if i % k == 0:
                    c = storia[-1].close
                    return Segnale("long", stop=c - 2.0, target=c + 2.5)
                return None
            if stato["entrata_i"] is None:
                stato["entrata_i"] = i
            if i - stato["entrata_i"] >= durata - 1:
                return "chiudi"
            return None
        return strategia

    ris = motore.esegui(candele, None, None, [], strategia_ogni_k(7, 6), Parametri())
    singola = ris.metriche()
    assert singola["vinti"] > 0 and singola["vinti"] < singola["n_trade"]  # guadagni e perdite
    gruppo = motore.metriche_di_gruppo({"XYZ": ris.trades}, 1, Parametri().capitale_iniziale)
    for chiave in ("profit_factor", "n_trade", "r_medio", "rendimento_totale", "drawdown_max"):
        assert gruppo[chiave] == singola[chiave], chiave


def test_metriche_di_gruppo_senza_trade_e_controlli():
    vuote = motore.metriche_di_gruppo({"AAA": [], "BBB": []}, 2, 1000.0)
    assert vuote["n_trade"] == 0 and vuote["profit_factor"] == 0.0 and vuote["r_medio"] == 0.0
    assert vuote["rendimento_totale"] == 0.0 and vuote["drawdown_max"] == 0.0
    assert vuote["r_medio_senza_30_migliori"] is None and vuote["per_moneta"] == {}
    assert st.criterio_vault(vuote, 0.0, trade_minimi=0)["esito"] is False
    with pytest.raises(ValueError, match="monete con trade"):
        motore.metriche_di_gruppo(_trade_a_mano(), 1, 1000.0)


def test_trade_migliori_tolti_predefinito_uguale_a_parametri_yaml():
    yaml = pytest.importorskip("yaml")
    from pathlib import Path
    percorso = Path(__file__).resolve().parents[2] / "config" / "parametri.yaml"
    gruppo = yaml.safe_load(percorso.read_text(encoding="utf-8"))["gruppo"]
    predefinito = inspect.signature(motore.metriche_di_gruppo).parameters["trade_migliori_tolti"].default
    assert predefinito == gruppo["fase4"]["trade_migliori_tolti"] == 30
    # e trenta trade migliori tolti su trentuno lasciano il peggiore
    trade = {"AAA": [TradeSfasato(i * ORA, i * ORA + 1, float(i), 1.0) for i in range(31)]}
    assert motore.metriche_di_gruppo(trade, 1, 1000.0)["r_medio_senza_30_migliori"] == 0.0


# ---------------------------------------------------------------------------
# somme_dei_trade e metriche_di_gruppo_da_somme (terzo giro di revisione, il vault)
# ---------------------------------------------------------------------------


def _somme(trade_per_moneta):
    return {s: motore.somme_dei_trade(v) for s, v in trade_per_moneta.items()}


def test_somme_dei_trade_a_mano():
    # AAA: R 1 e -1,5, pnl +10 e -30; BBB: R 2, -0,5, -0,75, pnl +20, -5, -4
    somme = _somme(_trade_a_mano())
    assert somme == {"AAA": [2, -0.5, 10.0, 30.0], "BBB": [3, 0.75, 20.0, 9.0]}
    # un pnl nullo conta come trade ma non e' ne' un guadagno ne' una perdita (come metriche_di_gruppo)
    assert motore.somme_dei_trade([TradeSfasato(0, 1, 0.0, 0.0), {"r": 0.5, "pnl": 2.0, "ts_entrata": 1,
                                                                    "ts_uscita": 2}]) == [2, 0.5, 2.0, 0.0]
    assert motore.somme_dei_trade([]) == [0, 0.0, 0.0, 0.0]
    # la somma degli R e' quella di statistica.riassunto_sfasate, ed e' esatta: non dipende dall'ordine
    r = [0.1] * 10 + [1e16, -1e16]
    trade = [TradeSfasato(i, i + 1, x, x) for i, x in enumerate(r)]
    assert motore.somme_dei_trade(trade)[:2] == st.riassunto_sfasate([r])[0]
    assert motore.somme_dei_trade(trade) == motore.somme_dei_trade(list(reversed(trade)))
    for cattivo in (math.inf, math.nan):
        with pytest.raises(ValueError, match="non finiti"):
            motore.somme_dei_trade([TradeSfasato(0, 1, cattivo, 1.0)])
        with pytest.raises(ValueError, match="non finiti"):
            motore.somme_dei_trade([TradeSfasato(0, 1, 1.0, cattivo)])


def test_metriche_di_gruppo_da_somme_a_mano():
    # gli stessi numeri di test_metriche_di_gruppo_a_mano: profit factor 30 / 39, risultato -9 USDT su 3.000,
    # R medio 0,05
    m = motore.metriche_di_gruppo_da_somme(_somme(_trade_a_mano()), 3, 1000.0)
    assert m["n_trade"] == 5 and m["monete_con_trade"] == 2 and m["monete_nel_periodo"] == 3
    assert m["profit_factor"] == pytest.approx(30 / 39, rel=1e-15)
    assert m["pnl_totale"] == -9.0 and m["capitale_totale"] == 3000.0
    assert m["rendimento_totale"] == pytest.approx(-0.003, rel=1e-15)
    assert m["r_medio"] == pytest.approx(0.05, rel=1e-12)
    assert (m["somma_guadagni"], m["somma_perdite"]) == (30.0, 39.0)
    esito = st.criterio_vault(m, r_caso_percentile_90=0.0, trade_minimi=0)
    assert esito["condizioni"] == {"profit_factor": False, "trade_minimi": True,
                                   "rendimento_positivo": False, "sopra_il_caso": True}


def _trade_casuali(seme: int):
    """Quattro monete: una senza trade, le altre con 50-600 trade, R e pnl reali di segno misto."""
    rng = np.random.default_rng(seme)
    trade = {"DDD": []}
    for simbolo in ("AAA", "BBB", "CCC"):
        n = int(rng.integers(50, 600))
        entrate = np.sort(rng.choice(np.arange(10_000), size=n, replace=False))
        durate = rng.integers(1, 40, size=n)
        r = rng.normal(0.08, 1.1, size=n)
        rischio = rng.uniform(5.0, 15.0, size=n)
        trade[simbolo] = [TradeSfasato(T0 + int(e) * ORA, T0 + int(e + d) * ORA, float(x), float(x * q))
                          for e, d, x, q in zip(entrate, durate, r, rischio)]
    return trade


@pytest.mark.parametrize("seme", range(8))
def test_metriche_di_gruppo_da_somme_uguali_a_metriche_di_gruppo_sugli_stessi_trade(seme):
    trade = _trade_casuali(seme)
    attese = motore.metriche_di_gruppo(trade, 5, 1000.0)
    m = motore.metriche_di_gruppo_da_somme(_somme(trade), 5, 1000.0)
    assert m["n_trade"] == attese["n_trade"] and m["monete_con_trade"] == attese["monete_con_trade"] == 3
    assert m["capitale_totale"] == attese["capitale_totale"]
    for chiave in ("profit_factor", "rendimento_totale", "r_medio", "pnl_totale"):
        assert m[chiave] == pytest.approx(attese[chiave], rel=1e-12, abs=0.0), chiave
    # stesse condizioni del criterio_vault
    for soglia in (0.0, attese["r_medio"] / 2):
        esito, atteso = st.criterio_vault(m, soglia, trade_minimi=0), st.criterio_vault(attese, soglia, trade_minimi=0)
        assert esito["condizioni"] == atteso["condizioni"] and esito["esito"] == atteso["esito"]
    # l'ordine delle monete e la forma delle somme (riletta da un JSON) non cambiano nulla, bit per bit
    rovescio = {s: _somme(trade)[s] for s in reversed(sorted(trade))}
    import json
    assert motore.metriche_di_gruppo_da_somme(rovescio, 5, 1000.0) == m
    assert motore.metriche_di_gruppo_da_somme(json.loads(json.dumps(_somme(trade))), 5, 1000.0) == m


def test_metriche_di_gruppo_da_somme_casi_limite_come_metriche_di_gruppo():
    x = _ms(2023, 1, 2)
    casi = {
        "senza trade": {"AAA": [], "BBB": []},
        "solo guadagni": {"AAA": [TradeSfasato(x - ORA, x, 1.0, 10.0)], "BBB": []},
        "solo perdite": {"AAA": [TradeSfasato(x - ORA, x, -1.0, -10.0)], "BBB": [TradeSfasato(x, x + ORA, -0.5, -4.0)]},
        "pnl nullo": {"AAA": [TradeSfasato(x - ORA, x, 0.0, 0.0)], "BBB": []},
    }
    for nome, trade in casi.items():
        attese = motore.metriche_di_gruppo(trade, 2, 1000.0)
        m = motore.metriche_di_gruppo_da_somme(_somme(trade), 2, 1000.0)
        for chiave in ("profit_factor", "n_trade", "rendimento_totale", "r_medio"):
            assert m[chiave] == attese[chiave], (nome, chiave)
    assert motore.metriche_di_gruppo_da_somme({}, 0, 1000.0)["n_trade"] == 0
    assert motore.metriche_di_gruppo_da_somme({"AAA": [1, 0.5, 2.0, 0.0]}, 1, 0.0)["rendimento_totale"] == 0.0


@pytest.mark.parametrize("somme, motivo", [
    ({"AAA": [1, 0.5, 2.0]}, "servono"),
    ({"AAA": [-1, 0.5, 2.0, 0.0]}, "numero di trade"),
    ({"AAA": [1.5, 0.5, 2.0, 0.0]}, "numero di trade"),
    ({"AAA": [True, 0.5, 2.0, 0.0]}, "numero di trade"),
    ({"AAA": [1, math.nan, 2.0, 0.0]}, "somme non valide"),
    ({"AAA": [1, 0.5, math.inf, 0.0]}, "somme non valide"),
    ({"AAA": [1, 0.5, -2.0, 0.0]}, "somme non valide"),
    ({"AAA": [1, 0.5, 2.0, -1.0]}, "somme non valide"),
    ({"AAA": [0, 0.5, 0.0, 0.0]}, "senza trade"),
])
def test_metriche_di_gruppo_da_somme_controlli(somme, motivo):
    with pytest.raises(ValueError, match=motivo):
        motore.metriche_di_gruppo_da_somme(somme, 1, 1000.0)


def test_metriche_di_gruppo_da_somme_monete_nel_periodo():
    with pytest.raises(ValueError, match="monete con trade"):
        motore.metriche_di_gruppo_da_somme(_somme(_trade_a_mano()), 1, 1000.0)
    # una moneta con zero trade non conta fra quelle con trade
    assert motore.metriche_di_gruppo_da_somme({"AAA": [0, 0.0, 0.0, 0.0], "BBB": [1, 1.0, 1.0, 0.0]}, 1,
                                              1000.0)["monete_con_trade"] == 1


# ---------------------------------------------------------------------------
# posizioni_aperte_insieme
# ---------------------------------------------------------------------------


def test_posizioni_aperte_insieme_a_mano():
    # long A [0, 10), B [5, 15), C [10, 20): A esce a 10 prima che C entri -> 2 long al massimo.
    # short D [12, 30), E [14, 16) -> 2 short. A 14 sono aperte B, C, D, E -> 4 in tutto.
    # F e' lunga zero (entra ed esce a 7): non e' mai aperta.
    def t(direzione, e, u):
        return {"direzione": direzione, "ts_entrata": e, "ts_uscita": u}

    trade = [t("long", 0, 10), t("long", 5, 15), t("long", 10, 20), t("short", 12, 30), t("short", 14, 16),
             t("long", 7, 7)]
    assert motore.posizioni_aperte_insieme(trade) == {"long": 2, "short": 2, "totale": 4}
    assert motore.posizioni_aperte_insieme(list(reversed(trade))) == {"long": 2, "short": 2, "totale": 4}
    assert motore.posizioni_aperte_insieme([]) == {"long": 0, "short": 0, "totale": 0}
    with pytest.raises(ValueError):
        motore.posizioni_aperte_insieme([t("long", 10, 5)])
    with pytest.raises(ValueError):
        motore.posizioni_aperte_insieme([t("lungo", 0, 5)])


def test_posizioni_aperte_insieme_con_i_trade_del_motore():
    # una moneta sola: il motore tiene una posizione alla volta. Due monete con le
    # stesse candele: due posizioni insieme.
    candele = serie_a_dente(200)
    ris = motore.esegui(candele, None, None, [], crea_casuale_fabbrica(4)(frozenset(range(0, 190, 9))), Parametri())
    assert ris.trades
    assert motore.posizioni_aperte_insieme(ris.trades) == {"long": 1, "short": 0, "totale": 1}
    assert motore.posizioni_aperte_insieme(ris.trades + ris.trades) == {"long": 2, "short": 0, "totale": 2}
    assert math.isfinite(motore.metriche_di_gruppo({"A": ris.trades, "B": ris.trades}, 2, 1000.0)["r_medio"])
