"""LA STORIA DEL GATE, TENUTA (1 ott 2026, la cattura dei dati mancanti).

A fine giro la discovery aggiunge a `data/gate_storia/AAAA-MM.jsonl` una riga
del giro e una per coppia del registro. Zero Firestore, fail-open. Qui anche la
misura dello spazio citata in testa a `scripts/gate_storia.py`.
"""
from __future__ import annotations

import inspect
import json

from scripts import gate_storia

NOW = 1_800_000_000.0     # 15 gen 2027 UTC


def _pairs(n: int) -> dict:
    out = {}
    for i in range(n):
        out[f"COIN{i:04d}USDT|gen_{i:012x}"] = {
            "pass_count": i % 5, "fail_count": i % 3, "last_pf": 1.23456 + i % 7,
            "last_win_rate": 0.4567, "last_t": 2.3456, "declassata": i % 11 == 0,
            "last_params": {"scale_r_mults": [1.5, 3, 5]}, "regime_pf": {"bull": {"pf": 2}}}
    return out


def test_righe_del_giro():
    pairs = _pairs(3)
    validate = [sorted(pairs)[1]]
    righe = gate_storia.righe_giro(pairs, validate, n_eval=120, n_passed=4,
                                   binding={"pf": 50, "trades": 30}, durata_s=3600.4,
                                   modalita="completa", commit="abc", interval="15m", now=NOW)
    giro = righe[0]
    assert giro["tipo"] == "giro" and giro["n_eval"] == 120 and giro["n_passed"] == 4
    assert giro["binding"] == {"pf": 50, "trades": 30} and giro["durata_s"] == 3600
    assert giro["coppie"] == 3 and giro["validate"] == 1 and giro["commit"] == "abc"
    c = righe[2]
    assert c["tipo"] == "c" and c["k"] == sorted(pairs)[1] and c["v"] == 1
    assert c["p"] == 1 and c["f"] == 1 and c["pf"] == 2.235 and c["wr"] == 0.457 and c["t"] == 2.35
    assert "last_params" not in c and "regime_pf" not in c       # compatta
    assert righe[1]["d"] == 1 and "v" not in righe[1]


def test_scrive_in_append_nel_file_del_mese(tmp_path):
    pairs = _pairs(2)
    n1 = gate_storia.registra_giro(pairs, [], n_eval=1, n_passed=0, binding={}, durata_s=1,
                                   modalita="solo urgenti", commit=None, interval="1h", now=NOW,
                                   cartella=str(tmp_path))
    n2 = gate_storia.registra_giro(pairs, [], n_eval=2, n_passed=0, binding=None, durata_s=1,
                                   modalita="completa", commit=None, interval="15m",
                                   now=NOW + 3600, cartella=str(tmp_path))
    path = tmp_path / "2027-01.jsonl"
    righe = [json.loads(r) for r in path.read_text().splitlines()]
    assert len(righe) == 6 and n1 > 0 and n2 > 0
    assert [r["n_eval"] for r in righe if r["tipo"] == "giro"] == [1, 2]


def test_non_solleva_mai(tmp_path):
    bloccata = tmp_path / "file"
    bloccata.write_text("x")                        # una cartella che e' un file
    assert gate_storia.scrivi([{"a": 1}], NOW, cartella=str(bloccata / "sotto")) == 0
    assert gate_storia.registra_giro(None, None, n_eval=None, n_passed=None, binding="rotto",
                                     durata_s=None, modalita=None, commit=None, interval="15m",
                                     now=NOW, cartella=str(tmp_path)) >= 0


def test_quanto_pesa_una_riga_coppia(tmp_path):
    """La stima in testa a scripts/gate_storia.py: ~92 byte a coppia, ~270 KB a
    giro col tetto di 3.000 coppie."""
    n = gate_storia.scrivi(gate_storia.righe_giro(_pairs(3000), list(_pairs(3000))[:200],
                                                  n_eval=1, n_passed=0, binding={}, durata_s=1,
                                                  modalita="completa", commit="abc1234",
                                                  interval="15m", now=NOW),
                           NOW, cartella=str(tmp_path))
    per_coppia = n / 3000
    assert 80 <= per_coppia <= 100, per_coppia
    assert n < 300 * 1024


def test_la_discovery_la_chiama_a_fine_giro():
    from scripts import discover_strategies as ds
    src = inspect.getsource(ds.main)
    assert "gate_storia.registra_giro(" in src
    assert "binding=diag_binding" in src
    fin = inspect.getsource(ds.finalizza_registro)
    assert "_ULTIMO_REGISTRO.update(" in fin


def test_cartella_fuori_da_git():
    import pathlib
    gi = (pathlib.Path(__file__).resolve().parents[1] / ".gitignore").read_text()
    assert "data/gate_storia/" in gi
