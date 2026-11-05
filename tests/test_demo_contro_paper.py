"""Il confronto giorno per giorno fra G1 sul demo e G1 nel paper (scripts/state_snapshot.py, MIGLIORARE_G1.md voce 1)."""
import pytest

from scripts import state_snapshot as ss


def test_confronto_giorni():
    demo = {"2026-11-01": 5000, "2026-11-02": 5100, "2026-11-03": 5049}
    paper = {"2026-10-31": 9000, "2026-11-01": 10000, "2026-11-02": 10150, "2026-11-03": 10048.5}
    r = ss.confronto_giorni(demo, paper, {"2026-11-02": 100, "2026-11-03": 110})
    assert [x["giorno"] for x in r] == ["2026-11-02", "2026-11-03"]
    assert r[0]["demo"] == pytest.approx(0.02) and r[0]["paper"] == pytest.approx(0.015)
    assert r[0]["differenza"] == pytest.approx(0.005)
    assert r[0]["eventi"] is None and r[1]["eventi"] == pytest.approx(0.10)


class _Fb:
    def __init__(self, dati):
        self.dati = dati

    def get_rtdb(self, ramo):
        return self.dati.get(ramo)


def test_sezione_vuota_e_piena():
    assert "non ancora" in "\n".join(ss.sezione_demo_contro_paper(_Fb({})))
    testo = "\n".join(ss.sezione_demo_contro_paper(_Fb({
        "/demo_binance/giorni": {"2026-11-01": 5000, "2026-11-02": 5100, "2026-11-03": 5000},
        "/paper_g1/giorni": {"2026-11-01": 10000, "2026-11-02": 10100, "2026-11-03": 10000}})))
    assert "| 2026-11-02 | +2.00% | +1.00% | +1.00% | — |" in testo
    assert "2 giorni" in testo
