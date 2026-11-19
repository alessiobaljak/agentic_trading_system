"""Le parti senza rete della prova 41: le parole del bilancio, la somiglianza del coseno, il bilancio dell'anno prima."""
from collections import Counter
from datetime import date

import pytest

from stock.dati import testi_bilanci as t


def test_parole_tolgono_dati_nascosti_tag_e_numeri():
    doc = ("<html><ix:header><ix:hidden>segreto nascosto</ix:hidden></ix:header><style>.x{color:red}</style>"
           "<p>Risk &amp; Revenue rose 10% in 2024.</p><script>var abc=1</script><b>RISK</b> up</html>")
    p = t.parole(doc)
    assert p == Counter({"risk": 2, "revenue": 1, "rose": 1})              # «in», «up» troppo corte; numeri fuori


def test_coseno():
    a = Counter({"alfa": 1, "beta": 2})
    assert abs(t.coseno(a, a) - 1.0) < 1e-12
    assert t.coseno(a, Counter({"gamma": 3})) == 0.0
    assert t.coseno(a, Counter()) != t.coseno(a, Counter())               # NaN se uno è vuoto


def test_precedente_stesso_tipo_fra_9_e_15_mesi():
    b = [("10-K", date(2016, 2, 20)), ("10-Q", date(2016, 5, 1)), ("10-Q", date(2016, 8, 1)), ("10-K", date(2017, 2, 25)),
         ("10-Q", date(2017, 5, 3)), ("10-K", date(2017, 10, 1))]
    assert t.precedente(b, 3) == 0                                           # 10-K con il 10-K dell'anno prima
    assert t.precedente(b, 4) == 1                                           # 10-Q di maggio con quello di maggio
    assert t.precedente(b, 0) is None
    assert t.precedente(b, 5) is None                                        # il 10-K di 7 mesi prima è troppo vicino


def test_segnale_della_prova_41_ultimo_bilancio_entro_4_mesi():
    from stock.prove import p041
    b = [(date(2018, 1, 10), 0.95, "10-K"), (date(2018, 4, 20), 0.99, "10-Q"), (date(2018, 8, 1), 0.97, "10-Q")]
    assert p041.segnale(b, date(2018, 5, 31)) == (0.99, "10-Q")
    assert p041.segnale(b, date(2018, 8, 1)) == (0.99, "10-Q")              # il deposito dello stesso giorno non conta ancora
    assert p041.segnale(b, date(2019, 1, 31)) is None                        # l'ultimo è di più di 4 mesi prima


def test_classifica_della_prova_41_dentro_il_tipo_di_bilancio():
    from stock.prove import p041
    q = p041.in_classifica({"A": (0.999, "10-K"), "B": (0.990, "10-K"), "C": (0.995, "10-Q"), "D": (0.980, "10-Q"),
                            "E": (0.980, "10-Q"), "F": (0.970, "10-K")})
    # un 10-K quasi uguale all'anno prima non batte un 10-Q per il solo tipo: ognuno è messo in fila con quelli del suo tipo
    assert q["A"] == pytest.approx(5 / 6) and q["C"] == pytest.approx(5 / 6) and q["F"] == pytest.approx(1 / 6) and q["B"] == 0.5
    assert q["D"] == q["E"] == pytest.approx(1 / 3)                          # a pari valore lo stesso posto (medio: 1,5 su 3)
    assert p041.in_classifica({"X": (0.9, "10-K")}) == {"X": 0.5} and p041.in_classifica({}) == {}
