"""La funzione unica dell'esame (`research/programma6/asticella.esame`, 27 novembre 2026; audit del 26 novembre: esame-1, 2, 4, 8, 10 e
punti ciechi 2; regole in `research/programma6/ASTICELLA.md`, sezioni 6 e 7).

* L'esame in vigore dal 27 novembre 2026 (decisione del proprietario, ASTICELLA.md, sezione 7): V simmetrica senza le serie bocciate
  dal revisore, t robusto di Newey e West con 4 ritardi, probabilita' sulle settimane efficaci (era il numero non ufficiale «(d)»).
  Una candidata senza serie nel mazzo si giudica sulle settimane semplici e il risultato lo dice.
* Accanto, non ufficiali: la regola fino al 27 novembre (la stessa probabilita' di `corretto_famiglie`; G1 alla prova 57 0,945; sul
  mazzo fino alla 169 con le prove senza serie su 300 settimane come allora, 168 B 0,749 e G1 0,593; dopo le correzioni del punto 1
  0,722 e 0,561), (a) senza 157, 159 e 161 e il controllo con 13 ritardi, rifatti qui a mano su un mazzo finto.
I test sul mazzo vero usano il mazzo fino alla prova 169 (o alla 57): le prove nuove non li cambiano."""
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from research.programma6 import asticella as ast
from research.programma6 import seconda as sc
from research.programma6 import terza as te

RADICE = Path(__file__).resolve().parents[1]
P7 = RADICE / "research" / "programma7"


def _t(sr, settimane):
    return sr * math.sqrt(settimane / 52)


# ------------------------------------------------------------------------------------------------ correzioni del punto 1 (esame-4, 8)

def test_per_v_usa_le_settimane_delle_prove_senza_serie():
    # la 151: Sharpe -1,27 su 19 settimane, t -0,77: entra in V; con le 300 settimane del programma (t -3,05) ne restava fuori
    assert ast.per_v([], [ast.Solo(-1.27, 19)], True) == [-1.27]
    assert ast.per_v([], [-1.27], True) == []                      # un numero semplice vale ancora 300 settimane (prove 1 e 2B)
    assert ast.per_v([], [ast.Solo(-1.27, 19)], False) == [-1.27]


def test_per_v_simmetrica_toglie_anche_le_vincenti():
    gr = [{"sharpe": 2.0, "settimane": 300}, {"sharpe": -2.0, "settimane": 300}, {"sharpe": 0.5, "settimane": 300}]
    assert ast.per_v(gr, [], True) == [2.0, 0.5]                   # in vigore: fuori solo t sotto -3
    assert ast.per_v(gr, [], True, simmetrica=True) == [0.5]       # non ufficiale: fuori anche t sopra +3
    assert ast.per_v(gr, [], False) == [2.0, -2.0, 0.5]


def test_senza_serie_con_le_settimane_vere():
    s = dict(ast.senza_serie())
    assert all(isinstance(x, ast.Solo) for x in s.values())
    assert s["151 WE"].settimane == 19 and s["153 A"].settimane == 196 and s["153 B"].settimane == 196
    assert s["110 CC"].settimane == 286 and {s[n].settimane for n in s if n.startswith(("108 ", "111 "))} == {143}
    assert _t(s["153 B"], 196) > -3 > _t(s["153 A"], 196)            # 153 B (t -2,45) entra in V, 153 A (t -3,09) no
    assert ast.per_v([], [s["151 WE"], s["153 A"], s["153 B"]], True) == [float(s["151 WE"]), float(s["153 B"])]


def test_la_g10_ha_le_settimane_ferme():
    g = ast.periodo(ast.serie_programma7()["68 G10"])
    assert len(g) == 301 and set(np.diff(g.index.to_numpy())) == {7}   # prima: 150 settimane, salti fino a 126 giorni
    assert int((g != 0).sum()) == 150
    assert ast.sharpe(g) == pytest.approx(-1.348, abs=1e-3)
    assert _t(ast.sharpe(g), len(g)) < -3                            # resta fuori da V


def _settimane(n=300):
    return sc.giorno(2021, 1, 4) + 7 * np.arange(n)


def test_le_settimane_vuote_si_tolgono_coppia_per_coppia():
    rng = np.random.default_rng(3)
    i = _settimane()
    a = pd.Series(rng.normal(0, 0.02, 300), index=i)
    b = a + rng.normal(0, 0.004, 300)
    b.iloc[:100] = np.nan                                            # come APT e MATIC prima della quotazione (prova 149)
    nomi, R = ast.correlazioni({"a": a, "b": b, "c": pd.Series(rng.normal(0, 0.02, 300), index=i)})
    assert R[0, 1] > 0.9                                             # prima del 27 novembre: NaN, cioe' 0
    gr = ast.gruppi({"a": a, "b": b, "c": pd.Series(rng.normal(0, 0.02, 300), index=i)}, ast.TAGLIO)
    assert any({"a", "b"} <= set(g["membri"]) for g in gr)


# ------------------------------------------------------------------------------------------------ la funzione, su un mazzo finto

def _mazzo_finto():
    rng = np.random.default_rng(11)
    i = _settimane()
    f = rng.normal(0.006, 0.03, 300)
    s = {"57 G1": f + rng.normal(0, 0.005, 300), "88 G1N": f + rng.normal(0, 0.005, 300)}
    fisso = 0.004 + rng.normal(0, 0.002, 300)
    s.update({"157 A": fisso, "157 B": fisso + rng.normal(0, 0.0005, 300), "161 A": 0.9 * fisso + rng.normal(0, 0.0006, 300),
              "159 A": 0.003 + rng.normal(0, 0.003, 300), "201 L": rng.normal(-0.01, 0.02, 300)})
    s.update({f"200 X{k}": rng.normal(0, 0.02, 300) for k in range(8)})
    s["57 G1"][1:] += 0.4 * s["57 G1"][:-1] - 0.4 * 0.006            # settimane legate a quelle prima, come G1
    serie = {n: pd.Series(v, index=i) for n, v in s.items()}
    soli = [ast.Solo(-0.5), ast.Solo(-1.27, 19), ast.Solo(-10.0, 143)]
    return serie, soli


def _v_simmetrica(gr, serie, soli):
    """V in vigore dal 27 novembre 2026, a mano: le famiglie senza 157 A e 157 B (una famiglia vuota non entra), fuori quelle con il t
    sotto -3 e sopra +3 (anche per le prove senza serie, sulle loro settimane)."""
    vb = []
    for g in gr:
        resto = [n for n in g["membri"] if n not in ("157 A", "157 B")]
        if not resto:
            continue
        media = pd.concat([serie[n] for n in resto], axis=1).mean(axis=1)
        sr, ww = ast.sharpe(media), int(media.notna().sum())
        if abs(_t(sr, ww)) <= 3:
            vb.append(sr)
    return vb + [float(x_) for x_ in soli if abs(_t(float(x_), x_.settimane)) <= 3]


def _efficaci(x, w, ritardi):
    v = x.to_numpy(float)
    u = v - v.mean()
    lunga = u @ u / len(u) + sum(2 * (1 - j / (ritardi + 1)) * (u[j:] @ u[:-j]) / len(u) for j in range(1, ritardi + 1))
    return v.var() / lunga


def _a_mano(serie, soli, nome):
    """L'esame rifatto senza `esame`: le formule di ASTICELLA.md, sezioni 3, 5, 6 e 7."""
    gr = ast.gruppi(serie, ast.TAGLIO)
    N, V_prima = len(ast.per_v(gr, soli, False)), ast.per_v(gr, soli, True)
    V = _v_simmetrica(gr, serie, soli)
    x = serie[nome].dropna()
    m = te.numeri_settimana(x)
    sh, w, a, k = m["sharpe"], m["settimane"], m["asimmetria"], m["curtosi"]
    r = _efficaci(x, w, 4)
    w_eff = max(3, int(round(w * r)))
    out = {"N": N, "V": V, "w_eff": w_eff, "t": sh * math.sqrt(w * r / 52), "p": te.sharpe_corretto(sh, w_eff, a, k, V, 52, n_prove=N)}
    out["p_prima"] = te.sharpe_corretto(sh, w, a, k, V_prima, 52, n_prove=N)                     # la regola fino al 27 novembre
    out["t_prima"] = sh * math.sqrt(w / 52)
    sa = {n: v for n, v in serie.items() if not n.startswith(("157 ", "159 ", "161 "))}            # (a), con la regola in vigore
    gra = ast.gruppi(sa, ast.TAGLIO)
    out["p_a"] = te.sharpe_corretto(sh, w_eff, a, k, _v_simmetrica(gra, sa, soli), 52, n_prove=len(ast.per_v(gra, soli, False)))
    r13 = _efficaci(x, w, 13)                                                                     # il controllo con 13 ritardi
    out["w13"] = max(3, int(round(w * r13)))
    out["t13"] = sh * math.sqrt(w * r13 / 52)
    out["p13"] = te.sharpe_corretto(sh, out["w13"], a, k, V, 52, n_prove=N)
    out["misure"] = m
    return out


def test_esame_su_un_mazzo_finto_come_a_mano(monkeypatch):
    serie, soli = _mazzo_finto()
    R = ast.esame(candidate=["57 G1", "88 G1N"], base=(serie, soli))
    c = R["candidate"]["57 G1"]
    m = _a_mano(serie, soli, "57 G1")
    iv = c["in_vigore"]
    assert R["in_vigore"]["famiglie"] == m["N"] and R["in_vigore"]["v"] == pytest.approx(m["V"], abs=1e-12)
    assert iv["settimane_efficaci"] == m["w_eff"] < 300                                           # settimane legate: meno di 300
    assert iv["settimane_usate"] == ast.SETTIMANE_EFFICACI and iv["ritardi"] == 4
    assert iv["t"] == pytest.approx(m["t"], abs=1e-12)
    assert iv["probabilita"] == pytest.approx(m["p"], abs=1e-12)
    assert iv["esito"] == ast.verdetto(m["misure"]["annuo"], iv["per_anno"], m["t"], m["p"], "t robusto")
    assert R["in_vigore"]["bocciate"] == ["157 A", "157 B"]
    assert not any("157 A" in g for g in R["in_vigore"]["fuori_da_v_vincenti"])
    assert any("161 A" in g for g in R["in_vigore"]["fuori_da_v_vincenti"])                        # t sopra +3: fuori da V
    u = c["non_ufficiali"]
    prima = u["regola_fino_al_27_novembre"]                                                        # accanto: la regola di prima
    assert prima["probabilita"] == pytest.approx(m["p_prima"], abs=1e-12) and prima["t"] == pytest.approx(m["t_prima"], abs=1e-12)
    assert prima["settimane"] == 300 and prima["passerebbe"] == (prima["esito"] == "PROMETTENTE")
    assert R["non_ufficiali"]["a_senza_incasso_fisso"]["tolte"] == ["157 A", "157 B", "161 A", "159 A"]
    assert u["a_senza_incasso_fisso"]["probabilita"] == pytest.approx(m["p_a"], abs=1e-12)
    c13 = u["controllo_13_ritardi"]
    assert c13["ritardi"] == 13 and c13["settimane_efficaci"] == m["w13"]
    assert c13["t"] == pytest.approx(m["t13"], abs=1e-12) and c13["probabilita"] == pytest.approx(m["p13"], abs=1e-12)
    # la regola di prima e' la probabilita' di `corretto_famiglie` sullo stesso mazzo
    monkeypatch.setattr(ast, "mazzo", lambda nuove=None, fino_alla=None: (dict(serie), list(soli)))
    cf = ast.corretto_famiglie({}, {"57 G1": m["misure"]})
    assert cf["candidate"]["57 G1"]["corretto"] == pytest.approx(prima["probabilita"], abs=1e-12)
    assert cf["famiglie"] == R["in_vigore"]["famiglie"] and cf["in_v"] == R["non_ufficiali"]["regola_fino_al_27_novembre"]["in_v"]


def test_esame_di_una_candidata_senza_serie_usa_le_settimane_semplici():
    serie, soli = _mazzo_finto()
    mis = {"sharpe": 2.4, "settimane": 200, "asimmetria": 0.0, "curtosi": 3.0, "annuo": 0.5, "per_anno": {"2023": 0.4, "2024": 0.6}}
    R = ast.esame(candidate={"300 senza serie": mis}, base=(serie, soli))
    c = R["candidate"]["300 senza serie"]
    iv = c["in_vigore"]
    assert c["serie"] is None and iv["settimane_usate"] == ast.SETTIMANE_SEMPLICI and iv["ritardi"] is None
    assert iv["settimane_efficaci"] == 200 and iv["t"] == pytest.approx(2.4 * math.sqrt(200 / 52), abs=1e-12)
    gr = ast.gruppi(serie, ast.TAGLIO)
    V, N = _v_simmetrica(gr, serie, soli), len(ast.per_v(gr, soli, False))
    assert iv["probabilita"] == pytest.approx(te.sharpe_corretto(2.4, 200, 0.0, 3.0, V, 52, n_prove=N), abs=1e-12)   # la V in vigore
    assert "t robusto" not in iv["esito"] and c["non_ufficiali"]["controllo_13_ritardi"] is None


def test_esame_con_le_misure_della_prova_e_un_altro_nome():
    serie, soli = _mazzo_finto()
    mis = {"sharpe": 1.5, "settimane": 250, "asimmetria": 0.0, "curtosi": 3.0, "annuo": 0.3, "per_anno": {"2021": 0.1, "2022": -0.2}}
    R = ast.esame(candidate={"G1 altra misura": {**mis, "serie": "57 G1"}}, base=(serie, soli))
    c = R["candidate"]["G1 altra misura"]
    assert c["serie"] == "57 G1" and "57 G1" in c["gruppo"]
    assert c["misure"]["sharpe"] == 1.5 and c["misure"]["settimane"] == 250
    assert c["in_vigore"]["per_anno"] == {2021: 0.1, 2022: -0.2} and not c["in_vigore"]["ogni_anno_positivo"]
    assert c["in_vigore"]["esito"].startswith("NON PROMETTENTE: anni non positivi 2022; t robusto")
    r = ast.rapporto_robusto(serie["57 G1"], 4)
    assert c["in_vigore"]["settimane_efficaci"] == max(3, int(round(250 * r)))
    assert c["in_vigore"]["t"] == pytest.approx(1.5 * math.sqrt(250 * r / 52), abs=1e-12)
    assert c["non_ufficiali"]["regola_fino_al_27_novembre"]["t"] == pytest.approx(1.5 * math.sqrt(250 / 52), abs=1e-12)


def test_verdetto():
    assert ast.verdetto(0.5, {2021: 0.1, 2022: 0.2}, 3.0, 0.80) == "PROMETTENTE"                 # le soglie sono comprese
    assert ast.verdetto(0.5, {2021: 0.1, 2022: -0.01}, 4.0, 0.9) == "NON PROMETTENTE: anni non positivi 2022"
    assert ast.verdetto(0.5, {}, 4.0, 0.9) == "NON PROMETTENTE: anni non misurati"
    assert ast.verdetto(-0.1, {2021: -0.1}, 2.0, 0.5) == ("NON PROMETTENTE: netto non positivo; anni non positivi 2021; t 2.00 sotto 3; "
                                                         "probabilita' che non sia fortuna 0.50 sotto 0,80")
    assert ast.verdetto(0.5, {2021: 0.1}, 2.5, 0.9, "t robusto") == "NON PROMETTENTE: t robusto 2.50 sotto 3"


def test_varianza_lunga_e_settimane_efficaci():
    rng = np.random.default_rng(5)
    x = rng.normal(0, 1, 400)
    assert ast.rapporto_robusto(x, 0) == pytest.approx(1.0, abs=1e-12)                 # con 0 ritardi le settimane non cambiano
    assert ast.varianza_lunga(x, 0) == pytest.approx(x.var(), abs=1e-12)
    e = rng.normal(0, 1, 20000)
    y = np.zeros_like(e)
    for k in range(1, len(e)):
        y[k] = 0.5 * y[k - 1] + e[k]                                                   # legate: (1 - 0,5) / (1 + 0,5) = 1/3 al limite
    r4, r13 = ast.rapporto_robusto(y, 4), ast.rapporto_robusto(y, 13)
    assert 1 > r4 > r13 > 0.3 and r13 < 0.42
    assert ast.sharpe_minimo(300, [-0.5, 0.5], 10) > 0                                 # e l'esame a quello Sharpe da' 0,80
    s = ast.sharpe_minimo(300, [-0.5, 0.5], 10)
    assert te.sharpe_corretto(s, 300, 0.0, 3.0, [-0.5, 0.5], 52, n_prove=10) == pytest.approx(0.80, abs=1e-6)
    # con la regola in vigore dal 27 novembre: le settimane efficaci (rapporto 1 = settimane non legate = le settimane)
    assert ast.sharpe_minimo(300, [-0.5, 0.5], 10, rapporto=1.0) == s
    assert ast.sharpe_minimo(300, [-0.5, 0.5], 10, rapporto=0.62) == ast.sharpe_minimo(186, [-0.5, 0.5], 10) > s


# ------------------------------------------------------------------------------------------------ il mazzo vero

def _g1_del_12_novembre() -> dict:
    m = json.loads((RADICE / "audits" / "repro" / "g1_parte2_2026-11-12_esito_misure.json").read_text())["misure"]["G1"]
    return {k: m[k] for k in ("sharpe", "settimane", "asimmetria", "curtosi")}


def test_g1_alla_prova_57_0_945_con_la_regola_di_allora_0_931_con_quella_nuova():
    serie, soli = ast.mazzo(fino_alla=57)
    assert len(serie) == 102 and len(soli) == 18
    R = ast.esame(candidate={"G1": {**_g1_del_12_novembre(), "serie": "57 G1"}}, base=(serie, soli))
    c = R["candidate"]["G1"]
    # la regola di quando G1 e' stata scelta (decisione del 23 novembre), accanto: 0,945
    prima = R["non_ufficiali"]["regola_fino_al_27_novembre"]
    assert prima["famiglie"] == 65 and prima["in_v"] == 58 and prima["deviazione_v"] == pytest.approx(0.5667, abs=1e-4)
    assert c["non_ufficiali"]["regola_fino_al_27_novembre"]["probabilita"] == pytest.approx(0.9451, abs=1e-4)
    assert c["non_ufficiali"]["regola_fino_al_27_novembre"]["esito"] == "PROMETTENTE"
    # la regola nuova sullo stesso mazzo: 0,931, sempre promettente
    assert R["in_vigore"]["famiglie"] == 65 and R["in_vigore"]["in_v"] == 57
    assert R["in_vigore"]["deviazione_v"] == pytest.approx(0.5184, abs=1e-4)
    assert c["in_vigore"]["settimane_efficaci"] == 186 and c["in_vigore"]["t"] == pytest.approx(3.75, abs=0.01)   # audit esame-2
    assert c["in_vigore"]["probabilita"] == pytest.approx(0.9313, abs=1e-4)
    assert c["in_vigore"]["esito"] == "PROMETTENTE"
    assert R["non_ufficiali"]["a_senza_incasso_fisso"]["tolte"] == []             # alla 57 non c'erano le prove a incasso fisso
    assert c["non_ufficiali"]["a_senza_incasso_fisso"]["probabilita"] == pytest.approx(c["in_vigore"]["probabilita"], abs=1e-12)
    assert c["non_ufficiali"]["controllo_13_ritardi"]["settimane_efficaci"] == 147
    assert c["non_ufficiali"]["controllo_13_ritardi"]["probabilita"] == pytest.approx(0.9065, abs=1e-4)


def test_mazzo_fino_alla_169_regola_nuova_e_regola_di_prima_accanto():
    serie, soli = ast.mazzo(fino_alla=169)
    assert len(serie) == 291 and len(soli) == 48
    R = ast.esame(candidate=["57 G1", "168 A", "168 B", "169 A", "169 B"], base=(serie, soli))
    gr, N = R["gruppi"], R["in_vigore"]["famiglie"]
    # com'era pubblicato: le prove senza serie contate tutte su 300 settimane (le correzioni dei dati della 68 e della 149 non
    # spostano niente: 200 famiglie, 152 in V, deviazione 0,6776)
    v300 = ast.per_v(gr, [float(x) for x in soli], True)
    assert N == 200 and len(v300) == 152 and float(np.std(v300, ddof=1)) == pytest.approx(0.6776, abs=1e-4)
    pubblicato = json.loads((P7 / "risultati_centosesta" / "esame.json").read_text())["esame"]
    p169 = json.loads((P7 / "risultati_centosettima_bis" / "esame.json").read_text())["esame"]
    for nome, atteso in (("57 G1", 0.593), ("168 A", pubblicato["A"]["sharpe_corretto"]), ("168 B", pubblicato["B"]["sharpe_corretto"]),
                         ("169 B", p169["B"]["sharpe_corretto"])):
        m = R["candidate"][nome]["misure"]
        p = te.sharpe_corretto(m["sharpe"], m["settimane"], m["asimmetria"], m["curtosi"], v300, 52, n_prove=N)
        assert p == pytest.approx(atteso, abs=5e-4), nome
    # la regola fino al 27 novembre resta accanto con i numeri di oggi (dopo le correzioni del punto 1: 151 e 153 B in V)
    prima = R["non_ufficiali"]["regola_fino_al_27_novembre"]
    assert prima["famiglie"] == 200 and prima["in_v"] == 154 and prima["deviazione_v"] == pytest.approx(0.6891, abs=1e-4)
    assert prima["v"] == ast.per_v(gr, soli, True)
    for nome, atteso in {"57 G1": 0.5615, "168 A": 0.7020, "168 B": 0.7222, "169 A": 0.5835, "169 B": 0.6918}.items():
        c = R["candidate"][nome]["non_ufficiali"]["regola_fino_al_27_novembre"]
        assert c["probabilita"] == pytest.approx(atteso, abs=2e-4), nome
        assert c["t"] > 4.5 and c["esito"].startswith("NON PROMETTENTE: probabilita' che non sia fortuna"), nome
        assert not c["passerebbe"]
    # la regola in vigore dal 27 novembre: V simmetrica senza 157 (149 famiglie in V), t robusto, settimane efficaci
    assert R["in_vigore"]["in_v"] == 149 and R["in_vigore"]["deviazione_v"] == pytest.approx(0.5798, abs=1e-4)
    assert R["in_vigore"]["bocciate"] == ["157 A", "157 B"]
    attesi = {"57 G1": (0.7646, 3.720, 186), "168 A": (0.8419, 3.905, 178), "168 B": (0.8524, 3.956, 178),
              "169 A": (0.7821, 3.829, 193), "169 B": (0.8506, 4.115, 199)}
    for nome, (p, t, w) in attesi.items():
        iv = R["candidate"][nome]["in_vigore"]
        assert iv["probabilita"] == pytest.approx(p, abs=2e-4), nome
        assert iv["t"] == pytest.approx(t, abs=2e-3) and iv["settimane_efficaci"] == w, nome
        assert iv["ogni_anno_positivo"] and iv["settimane_usate"] == ast.SETTIMANE_EFFICACI
        assert iv["esito"] == ("PROMETTENTE" if p >= 0.80 else "NON PROMETTENTE: probabilita' che non sia fortuna "
                               f"{iv['probabilita']:.2f} sotto 0,80"), nome
    # accanto: (a) senza 157, 159 e 161 e il controllo con 13 ritardi (168 B)
    u = R["candidate"]["168 B"]["non_ufficiali"]
    assert R["non_ufficiali"]["a_senza_incasso_fisso"]["famiglie"] == 198
    assert u["a_senza_incasso_fisso"]["probabilita"] == pytest.approx(0.8527, abs=2e-4)
    assert u["controllo_13_ritardi"]["t"] == pytest.approx(3.47, abs=0.01) and u["controllo_13_ritardi"]["settimane_efficaci"] == 137
    assert u["controllo_13_ritardi"]["probabilita"] == pytest.approx(0.8205, abs=2e-4)
    fuori = R["in_vigore"]["fuori_da_v_vincenti"]
    assert len(fuori) == 5 and any("57 G1" in g for g in fuori) and not any("157 A" in g for g in fuori)
