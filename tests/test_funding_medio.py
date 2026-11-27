"""La misura in avanti dell'idea 45 (research/programma6/paper/REGOLE.md, sezione 18; audit del 26 novembre 2026, punti ciechi
8): il funding medio dei 7 giorni dell'universo di F5 e F5 con l'esposizione dimezzata sotto -11% l'anno, solo dalle settimane
dal lunedi' 30 novembre 2026. Tutto su dati finti."""
import json

import numpy as np
import pytest

from research.programma6 import seconda as sc
from research.programma6.paper import funding_medio as fm

INIZIO = fm.INIZIO
MONETE = 30


def _pannello(fine: int, giorni: int = 330, giu=(), base: float = 0.0003) -> dict:
    """Un pannello finto che finisce il giorno ``fine``: 30 monete sopra il volume minimo, il funding di ogni moneta diverso
    (cosi' F5 ha i due lati, circa +11% l'anno in media) e, nei giorni ``giu``, tutto il mercato a -0,2% al giorno."""
    t0 = fine - giorni + 1
    rng = np.random.default_rng(1)
    C = 100 * np.exp(np.cumsum(rng.normal(0, 0.03, (giorni, MONETE)), axis=0))
    O = np.vstack([C[:1], C[:-1]])
    V = 5e6 + np.zeros((giorni, MONETE)) + np.arange(MONETE) * 1e4
    F = base + np.linspace(-0.0004, 0.0004, MONETE)[None, :] + rng.normal(0, 0.0002, (giorni, MONETE))
    for g in giu:
        F[g - t0] -= 0.002
    return {"t0": t0, "simboli": [f"M{j:02d}USDT" for j in range(MONETE)], "open": O, "close": C, "high": C, "low": C,
            "quote_volume": V, "funding": F}


def test_inizio_e_un_lunedi_dopo_la_regola():
    assert sc.data(INIZIO) == "2026-11-30" and (INIZIO + 3) % 7 == 0
    assert INIZIO > sc.giorno(2026, 11, 27)


def test_soglia_e_media_dell_universo():
    soglia_7 = fm.SOGLIA_ANNUA * 7 / 365
    assert fm.esposizione(np.array([soglia_7 - 1e-9, soglia_7 + 1e-9, np.nan])).tolist() == [0.5, 1.0, 1.0]
    s7 = np.array([[1.0, 2.0, 3.0, 100.0], [5.0, 5.0, 5.0, 5.0]])
    U = np.array([[True, True, True, False], [False, False, False, False]])
    sig = np.array([[0.1, np.nan, 0.2, 0.1], [0.1, 0.1, 0.1, 0.1]])
    medio, n = fm.funding_medio_7(s7, U, sig)
    assert medio[0] == 2.0 and n.tolist() == [2, 0] and np.isnan(medio[1])    # fuori dall'universo e senza volatilita'
    assert fm.annuo(-0.0021) == pytest.approx(-0.0021 * 365 / 7)


def test_dimezza_la_settimana_dopo_il_funding_basso_non_quella_stessa():
    # il mercato a -0,2% al giorno nei 7 giorni di tenuta dal 30 novembre: si dimezza la settimana del 7 dicembre, che li ha
    # prima; quella del 30 novembre (decisa con i 7 giorni di prima) resta piena. Usare il funding della settimana stessa
    # (guardare avanti) dimezzerebbe quella del 30 novembre
    pan = _pannello(fine=INIZIO + 23, giu=range(INIZIO, INIZIO + 7))
    res = fm.calcola(pan, paper_json=None)
    st = res["settimane"]
    assert [x["lunedi"] for x in st] == ["2026-11-30", "2026-12-07", "2026-12-14"]
    assert [x["esposizione"] for x in st] == [1.0, 0.5, 1.0]
    assert st[1]["funding_medio_annuo"] < fm.SOGLIA_ANNUA < st[0]["funding_medio_annuo"]
    assert st[2]["funding_medio_annuo"] > fm.SOGLIA_ANNUA and st[0]["monete"] == MONETE
    s = fm.serie(pan)
    f5, rg = s["f5"], s["regola"]
    i = int(np.flatnonzero(s["lunedi"] == INIZIO)[0])
    assert (s["W"][i] != 0).sum() >= 12                                         # F5 ha davvero le posizioni
    assert rg.iloc[i].equals(f5.iloc[i])                                       # piena dopo piena: uguale a F5
    assert rg["lordo"].iloc[i + 1] == pytest.approx(0.5 * f5["lordo"].iloc[i + 1], abs=1e-15)
    assert rg["funding"].iloc[i + 1] == pytest.approx(0.5 * f5["funding"].iloc[i + 1], abs=1e-15)
    assert st[1]["differenza"] != 0
    assert rg["lordo"].iloc[i + 2] == f5["lordo"].iloc[i + 2]                  # di nuovo piena: stessi pesi...
    assert rg["spese"].iloc[i + 2] > f5["spese"].iloc[i + 2]                   # ...ma la spesa per tornare pieni c'e'
    t = res["totale"]
    assert t["settimane"] == 3 and t["dimezzate"] == 1
    assert t["F5"] == pytest.approx(np.prod(1 + f5["netto"].to_numpy()[i:i + 3]) - 1, abs=1e-6)
    assert t["F5_regola"] == pytest.approx(np.prod(1 + rg["netto"].to_numpy()[i:i + 3]) - 1, abs=1e-6)
    # la settimana del 21 dicembre non e' chiusa (dati fino al 23): solo la decisione, piena
    c = res["settimana_in_corso"]
    assert c["lunedi"] == "2026-12-21" and c["esposizione"] == 1.0 and c["monete"] == MONETE


def test_settimana_in_corso_dimezzata():
    pan = _pannello(fine=INIZIO + 23, giu=range(INIZIO + 14, INIZIO + 21))
    res = fm.calcola(pan, paper_json=None)
    assert [x["esposizione"] for x in res["settimane"]] == [1.0, 1.0, 1.0]
    assert res["settimana_in_corso"]["esposizione"] == 0.5
    assert res["settimana_in_corso"]["funding_medio_annuo"] < fm.SOGLIA_ANNUA


def test_nessun_numero_sul_passato():
    # il funding molto basso prima dell'inizio non cambia niente: prima del 30 novembre la regola non c'e'
    pan = _pannello(fine=INIZIO + 9, giu=range(INIZIO - 21, INIZIO - 7))
    s = fm.serie(pan)
    prima = s["lunedi"] < INIZIO
    assert prima.sum() > 10 and (s["k"][prima] == 1.0).all()
    assert np.array_equal(s["regola"]["netto"].to_numpy()[prima], s["f5"]["netto"].to_numpy()[prima])
    assert (fm.annuo(s["medio"][prima]) < fm.SOGLIA_ANNUA).sum() == 2            # sotto la soglia, ma non contano
    res = fm.calcola(pan, paper_json=None)
    assert [x["lunedi"] for x in res["settimane"]] == ["2026-11-30"]
    # un pannello che finisce prima della prima settimana chiusa: nessuna settimana, nessun totale
    for fine, in_corso in ((INIZIO + 3, "2026-11-30"), (INIZIO - 2, None)):
        res = fm.calcola(_pannello(fine=fine), paper_json=None)
        assert res["settimane"] == [] and res["totale"] is None
        assert (res["settimana_in_corso"] or {}).get("lunedi") == in_corso
        assert "nessuna settimana chiusa" in fm.riassunto(res)[1]


def test_giorni_con_il_funding_stimato():
    pan = _pannello(fine=INIZIO + 16)
    M = np.zeros(pan["close"].shape, bool)
    M[INIZIO + 6 - pan["t0"]] = True                                            # domenica 6 dicembre senza il dato vero
    pan["funding_stimato"] = M
    res = fm.calcola(pan, paper_json=None)
    a, b = res["settimane"]
    s = fm.serie(pan)
    i = int(np.flatnonzero(s["lunedi"] == INIZIO)[0])
    assert a["stimati_finestra"] == 0 and a["stimati_settimana"] == int((s["W"][i] != 0).sum())
    assert b["stimati_finestra"] == MONETE and b["stimati_settimana"] == 0
    assert "giorni-moneta" in fm.riassunto(res)[1]
    del pan["funding_stimato"]
    assert fm.calcola(pan, paper_json=None)["settimane"][0]["stimati_finestra"] is None


def test_esegui_scrive_il_file_e_poche_righe(tmp_path, monkeypatch):
    pan = _pannello(fine=INIZIO + 23, giu=range(INIZIO, INIZIO + 7))
    from research.programma6.paper import aggiorna as ag
    chiamate = []
    monkeypatch.setattr(sc, "pannello", lambda: pan)
    monkeypatch.setattr(ag, "applica_stima", lambda p: chiamate.append(p is pan) or {})
    paper = tmp_path / "paper.json"                                             # F5 del paper sullo stesso pannello
    ok = fm.calcola(_pannello(fine=INIZIO + 23, giu=range(INIZIO, INIZIO + 7)))["settimane"]
    paper.write_text(json.dumps({"candidate": {"F5": {"settimane": {x["lunedi"]: x["F5"] for x in ok}}}}), encoding="utf-8")
    righe = []
    uscita = tmp_path / "funding_medio.json"
    res = fm.esegui(uscita, log=righe.append, paper_json=paper)
    assert chiamate == [True]                                                   # la stima del paper, sullo stesso pannello
    letto = json.loads(uscita.read_text(encoding="utf-8"))
    assert [x["lunedi"] for x in letto["settimane"]] == ["2026-11-30", "2026-12-07", "2026-12-14"]
    assert letto["confronto_con_paper"] == {"settimane": 3, "scarto_massimo": 0.0}
    assert res["totale"]["dimezzate"] == 1 and 3 <= len(righe) <= 20
    assert not any("attenzione" in r for r in righe)
