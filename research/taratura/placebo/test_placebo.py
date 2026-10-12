"""Test della prova a placebo: lo sfasamento, la causalita' dei segnali, le strategie, il giudizio e il riassunto."""
import io
import json
from contextlib import redirect_stdout
from datetime import date

import numpy as np

from research.src.motore import Candela, Parametri, StoriaChiusa, esegui
from research.taratura.placebo import placebo as P
from research.taratura.placebo import riassunto as R


def _serie(n=600, seme=1, passo=3_600_000, t0=0):
    rng = np.random.default_rng(seme)
    prezzo = 100 * np.exp(np.cumsum(rng.normal(0, 0.01, n)))
    out = []
    for i, p in enumerate(prezzo):
        o = p * (1 + rng.normal(0, 0.002))
        h = max(o, p) * (1 + abs(rng.normal(0, 0.003)))
        l = min(o, p) * (1 - abs(rng.normal(0, 0.003)))
        ts = t0 + i * passo
        out.append(Candela(ts, o, h, l, p, 1.0, ts + passo - 1))
    return out


def test_sposta_conserva_numero_e_distanze_circolari():
    idx = [70, 71, 75, 200, 350]
    spostati, d = P.sposta(idx, 60, 460, seme=7, minimo=50)
    L = 400
    assert len(spostati) == len(idx)
    assert 50 <= d <= L - 50
    assert spostati == frozenset(60 + ((i - 60 + d) % L) for i in idx)
    assert all(60 <= i < 460 for i in spostati)


def test_sposta_usa_quasi_tutto_il_cerchio():
    ds = [P.sposta([100], 0, 20_000, seme=s, minimo=720)[1] for s in range(400)]
    assert min(ds) >= 720 and max(ds) <= 20_000 - 720
    assert min(ds) < 3000 and max(ds) > 17_000  # non solo fra L/4 e 3L/4
    # periodo corto: il minimo scende a L//4
    _, d = P.sposta([5], 0, 100, seme=1, minimo=720)
    assert 25 <= d <= 75


def test_sposta_riproducibile_e_seme_diverso():
    a, _ = P.sposta(range(60, 300, 7), 60, 460, P.seme_di("X", "1h", "rsi", "long", "costruzione", 0), 50)
    b, _ = P.sposta(range(60, 300, 7), 60, 460, P.seme_di("X", "1h", "rsi", "long", "costruzione", 0), 50)
    c, _ = P.sposta(range(60, 300, 7), 60, 460, P.seme_di("X", "1h", "rsi", "long", "costruzione", 1), 50)
    assert a == b and a != c


def test_segnali_e_atr_causali():
    c = _serie()
    for regola in P.REGOLE:
        for direzione in P.DIREZIONI:
            piena = P.segnali_regola(c, regola, direzione)
            tagliata = P.segnali_regola(c[:400], regola, direzione)
            assert (piena[:400] == tagliata).all(), (regola, direzione)
    assert np.allclose(P.atr_semplice(c)[:400], P.atr_semplice(c[:400]), equal_nan=True)


def test_uscita_a_tempo_conta_le_barre_anche_con_un_buco():
    c = _serie()
    c = c[:150] + c[151:]  # un buco: manca una barra
    indice_di = {x.ts: k for k, x in enumerate(c)}
    atr = P.atr_semplice(c)
    u = P.Uscita("tempo", 5, 3_600_000)
    seg = P.calcolo_segnale(atr, "long", u, 60)
    ris = esegui(c, None, None, [], P.fabbrica(frozenset({100, 147, 300}), seg, u, indice_di)(), Parametri())
    assert ris.trades, "servono trade per provare l'uscita"
    usciti_a_tempo = [t for t in ris.trades if t.esito == "segnale"]
    assert usciti_a_tempo
    for t in usciti_a_tempo:
        assert indice_di[t.ts_uscita] - indice_di[t.ts_entrata] == 5  # 5 barre tenute, esce all'apertura della sesta


def test_niente_segnali_nel_riscaldamento_e_nei_mesi_illiquidi():
    c = _serie()
    atr = P.atr_semplice(c)
    illiquida = np.zeros(len(c), dtype=bool)
    illiquida[200:300] = True
    seg = P.calcolo_segnale(atr, "short", P.Uscita("atr", 24, 3_600_000), 60, illiquida)
    assert seg(StoriaChiusa(c, 30)) is None
    assert seg(StoriaChiusa(c, 250)) is None
    s = seg(StoriaChiusa(c, 100))
    assert s is not None and s.stop > c[99].close and s.target < c[99].close


def test_giudica_con_pochi_trade_non_giudica_e_un_errore_resta_nella_riga():
    c = _serie()
    atr = P.atr_semplice(c)
    u = P.Uscita("atr", 24, 3_600_000)
    e = P.giudica(c, frozenset({100, 200}), atr, "long", u, 60, P.parametri_moneta(0.0005), 70, True)
    assert e["giudicata"] is False and e["n_trade"] <= 2
    rotta = P.giudica(c, frozenset({100}), np.array([1.0]), "long", u, 60, P.parametri_moneta(0.0005), 1, True)
    assert rotta["giudicata"] is False and "errore" in rotta


def test_giudica_giudica_come_una_campagna(monkeypatch):
    c = _serie(n=2500, seme=3)
    atr = P.atr_semplice(c)
    u = P.Uscita("atr", 24, 3_600_000)
    ingressi = frozenset(range(70, 2400, 25))
    monkeypatch.setattr(P, "SIMULAZIONI", 20)
    monkeypatch.setattr(P, "RICAMPIONAMENTI", 200)
    e = P.giudica(c, ingressi, atr, "long", u, 60, P.parametri_moneta(0.0005), 30, True)
    assert e["giudicata"] is True
    for chiave in ("netta_b", "p_b", "t_b", "netta_a", "candidato", "blocco", "durata_media"):
        assert chiave in e, chiave
    assert 0.0 <= e["p_b"] <= 1.0


def test_valuta_moneta_prefisso_e_ingressi(monkeypatch):
    passo = 3_600_000
    t0 = 1_577_836_800_000  # 2020-01-01
    serie = _serie(n=3000, seme=5, passo=passo, t0=t0)
    per = {"inizio": date(2020, 1, 1), "fine_validazione": date(2023, 12, 31),
           "fine_costruzione_ts": serie[2099].close_ts, "inizio_validazione_ts": serie[2100].ts}
    monkeypatch.setattr(P.dati, "periodi_campagna", lambda primo: per)
    monkeypatch.setattr(P.dati, "_percorsi_presenti", lambda *a, **k: [None] * len(P._mesi_attesi(date(2020, 1, 1))))
    monkeypatch.setattr(P.dati, "carica_candele", lambda *a, **k: serie)
    monkeypatch.setattr(P, "mesi_illiquidi", lambda *a, **k: {})  # tutti illiquidi: nessun segnale
    p = P.carica_periodi("X", date(2020, 1, 1), "1h", None)
    assert len(p["costruzione"]) == 2100 and p["inizio_valid"] == P.PREFISSO_VALIDAZIONE
    assert p["validazione"][P.PREFISSO_VALIDAZIONE].ts == serie[2100].ts
    monkeypatch.setattr(P, "giudica", lambda candele, ingressi, atr, d, u, primo, par, minimo, con_baseline_a, illiquida:
                        {"ingressi_ok": all(primo <= i < len(candele) - 1 for i in ingressi),
                         "primo": primo, "tutte_illiquide": bool(illiquida[primo:].all())})
    esiti = P.valuta_moneta("X", date(2020, 1, 1), 0.0005, "1h", None)
    assert len(esiti) == 24
    assert all(e["ingressi_ok"] for e in esiti)
    assert {e["primo"] for e in esiti if e["periodo"] == "costruzione"} == {P.RISCALDAMENTO}
    assert {e["primo"] for e in esiti if e["periodo"] == "validazione"} == {P.PREFISSO_VALIDAZIONE}
    assert all(e["tutte_illiquide"] for e in esiti)


def test_carica_periodi_rifiuta_mesi_mancanti(monkeypatch):
    monkeypatch.setattr(P.dati, "_percorsi_presenti", lambda *a, **k: [None, None])
    try:
        P.carica_periodi("X", date(2020, 1, 1), "1h", None)
    except ValueError as e:
        assert "file mensili" in str(e)
    else:
        raise AssertionError("doveva rifiutare")


def test_riassunto_non_stampa_quote_con_campione_insufficiente(tmp_path, monkeypatch):
    righe = []
    for m in range(80):
        for tf in ("1h", "4h"):
            righe.append({"simbolo": f"M{m}", "timeframe": tf, "sfasamento_k": 0, "periodo": "costruzione",
                          "regola": "rsi", "giudicata": True, "valutabile_b": True, "netta_b": True, "p_b": 0.01,
                          "n_trade": 100, "versione_codice": "x"})
    (tmp_path / "esiti_k0.jsonl").write_text("\n".join(json.dumps(r) for r in righe) + "\n")
    monkeypatch.setattr(R, "QUI", tmp_path)
    out = io.StringIO()
    with redirect_stdout(out):
        codice = R.main(["0"])
    testo = out.getvalue()
    assert codice == 1 and "CAMPIONE INSUFFICIENTE" in testo
    assert "M1" not in testo and "%" not in testo


def test_riassunto_si_ferma_se_manca_una_coppia(tmp_path, monkeypatch):
    (tmp_path / "esiti_k0.jsonl").write_text(json.dumps({"simbolo": "A", "timeframe": "1h", "sfasamento_k": 0,
                                                          "periodo": "costruzione", "regola": "rsi"}) + "\n")
    monkeypatch.setattr(R, "QUI", tmp_path)
    out = io.StringIO()
    with redirect_stdout(out):
        codice = R.main(["0"])
    assert codice == 1 and "COPERTURA INCOMPLETA" in out.getvalue()


def test_intervallo_per_moneta_piu_largo_di_wilson_con_monete_correlate():
    righe = []
    for m in range(40):
        tutte = m < 4  # 4 monete con tutte le placebo «nette»: correlazione forte
        for j in range(25):
            righe.append({"simbolo": f"M{m}", "x": tutte})
    mis = R.misura(righe, lambda r: r["x"])
    assert mis["monete"][1] - mis["monete"][0] > mis["wilson"][1] - mis["wilson"][0]
