"""Il riepilogo del registro delle prove (research/src/registro.py) e il registro delle varianti di ogni prova (research/src/prove.py),
usati dagli agenti al posto della lettura integrale dei file."""
import csv

import pytest

from research.src import prove, registro

ESEMPIO = """# Registro

## 1. Prove
| n. | descrizione | conto | risultato | verdetto |
|---|---|---|---|---|
| 147 | GA2C: le notizie | 1 | +0,14% | conferma debole |
| 148 | G1P: G1 con 250 euro | 1 | Sharpe 1,90 | sì, G1 così com'è |

Totale nel conto: 9 + 3 + 1 = **246** (le conferme non contano)

## 5. Idee in coda
1. ~~Una idea chiusa~~ → prova 16.
2. **Il canale Telegram** (scalping): si verifica.
3. **Lo scalping con il libro degli ordini**: serve lo storico.
"""


def test_riepilogo_del_registro(tmp_path):
    f = tmp_path / "REGISTRO.md"
    f.write_text(ESEMPIO, encoding="utf-8")
    d = registro.leggi(f)
    assert sorted(d["prove"]) == [147, 148] and d["conto"] == 246
    assert d["idee_chiuse"] == 1 and [n for n, _ in d["idee_aperte"]] == [2, 3]
    righe = registro.riepilogo(d)
    assert len(righe) <= 20 and "conto delle prove: 246" in righe[0]
    assert any("148" in r and "sì, G1 così com'è" in r for r in righe)


def test_registro_vero_si_legge():
    d = registro.leggi()
    assert len(d["prove"]) > 100 and d["conto"] and d["conto"] >= 246


def test_varianti_in_sola_aggiunta_e_separate(tmp_path):
    prove.registra("P149", "v1", {"k": 10}, "1d", 120, {"sharpe": 1.2}, "fatta", seme=1, commit="abc", cartella=tmp_path)
    prove.registra("P149", "v2", {"k": 20}, "1d", 90, {"sharpe": 0.4}, "fatta", seme=1, commit="abc", cartella=tmp_path)
    prove.registra("P149", "v2", {"k": 20}, "1d", 0, {}, "errore", note="dati mancanti", commit="abc", cartella=tmp_path)
    prove.registra("P150", "v1", {"x": 1}, "1h", 50, {}, "fatta", commit="abc", cartella=tmp_path)
    with (tmp_path / "P149.csv").open(encoding="utf-8", newline="") as fh:
        righe = list(csv.DictReader(fh))
    assert len(righe) == 3 and righe[0]["parametri"] == '{"k": 10}' and righe[2]["esito"] == "errore"
    assert (tmp_path / "P150.csv").exists()                               # un file per prova
    r = prove.riepilogo(tmp_path)
    assert r[0].startswith("P149: 3 righe, 2 varianti diverse") and r[1].startswith("P150: 1 righe")
    with pytest.raises(ValueError):
        prove.registra("../fuori", "v1", {}, "1d", 0, {}, "x", cartella=tmp_path)
