"""La copia dei trader di Hyperliquid (research/trader_copiati/HYPERLIQUID.md): la scelta dei due gruppi e il portafoglio copiato,
con la media dei pesi (sezione 2) e con ogni conto a esposizione uguale (aggiunta del 5 novembre 2026)."""
import gzip
import json

import pytest

from research.trader_copiati import conto_hyperliquid as ch
from research.trader_copiati import hyperliquid as hl


def _riga(indirizzo, conto, roi, pnl=1.0, vol=2e7):
    return {"ethAddress": indirizzo, "accountValue": str(conto),
            "windowPerformances": [["month", {"vlm": str(vol), "pnl": str(pnl), "roi": str(roi)}]]}


def test_scelte_dei_due_gruppi():
    classifica = [_riga("a", 5e6, 0.1), _riga("b", 2e6, 0.9), _riga("c", 9e6, 0.5), _riga("d", 5e5, 3.0),
                  _riga("e", 8e6, 2.0, pnl=-1.0), _riga("f", 7e6, 1.0, vol=1e6)]
    assert [c["indirizzo"] for c in hl.scegli(classifica)] == ["b", "c", "a"]          # rendimento del mese
    assert [c["indirizzo"] for c in hl.scegli_balene(classifica)] == ["c", "a", "b"]   # valore del conto


@pytest.fixture
def archivio(tmp_path, monkeypatch):
    monkeypatch.setattr(ch, "ARCHIVIO", tmp_path)
    (tmp_path / "scelti_2026-11-02.json").write_text(json.dumps({"conti": [{"indirizzo": "x"}, {"indirizzo": "y"}]}))
    (tmp_path / "scelti_balene_2026-11-05.json").write_text(json.dumps({"conti": [{"indirizzo": "y"}]}))
    righe = []
    for ora in ("2026-11-05 08:29", "2026-11-05 12:20"):
        righe.append({"ora": ora, "indirizzo": "x", "conto": 100.0,
                      "posizioni": [{"moneta": "ETH", "quantita": -1, "valore": 1000.0}]})          # venduto, leva 10
        righe.append({"ora": ora, "indirizzo": "y", "conto": 100.0,
                      "posizioni": [{"moneta": "BTC", "quantita": 1, "valore": 100.0}]})           # comprato, leva 1
    with gzip.open(tmp_path / "posizioni_2026-11.jsonl.gz", "wt", encoding="utf-8") as g:
        for r in righe:
            g.write(json.dumps(r) + "\n")
    return tmp_path


def test_media_dei_pesi_scalata_a_due(archivio):
    gg = ch.giri({"ETHUSDT", "BTCUSDT"})
    p = gg["pesi"].iloc[0]
    # media: ETH −5, BTC +0,5; lorda 5,5 → scalata a 2
    assert p["ETHUSDT"] == pytest.approx(-5 * 2 / 5.5)
    assert p["BTCUSDT"] == pytest.approx(0.5 * 2 / 5.5)


def test_esposizione_uguale_e_balene(archivio):
    gg = ch.giri({"ETHUSDT", "BTCUSDT"}, "scelti_", True, "2026-11-05 08:40")
    assert len(gg) == 1                                   # solo i giri dopo l'aggiunta
    p = gg["pesi"].iloc[0]
    assert p["ETHUSDT"] == pytest.approx(-1.0) and p["BTCUSDT"] == pytest.approx(1.0)   # ognuno a 2, poi la media
    bal = ch.giri({"ETHUSDT", "BTCUSDT"}, "scelti_balene_", False, "2026-11-05 08:40")
    assert bal["pesi"].iloc[0] == {"BTCUSDT": pytest.approx(1.0)}
    assert ch._scelti("scelti_") == {"2026-11-02": {"x", "y"}}                          # non prende i file delle balene
