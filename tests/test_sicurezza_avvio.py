"""La revisione del percorso degli ordini del 7 novembre 2026 (reviews/reports/2026-11-07-primo-avvio.md), problemi 5, 6-8 e 9:
DRY_RUN e la rete di prova valgono falso solo se scritti esattamente cosi'; il file delle tarature non cambia modalita', parita' e
segreti; la parita' col backtest non parte con DRY_RUN falso; il ramo reale del vecchio esecutore non crea il client del conto vero."""
import sys
import types

import pytest

from bot import config as cfg


@pytest.mark.parametrize("valore,atteso", [("false", False), (" False ", False), ("true", True), ("si", True), ("treu", True),
                                           ("", True), ("0", True), ("no", True)])
def test_dry_run_solo_false_esatto_lo_spegne(monkeypatch, valore, atteso):
    monkeypatch.setenv("DRY_RUN", valore)
    assert cfg._get_bool_sicuro("DRY_RUN") is atteso


def test_dry_run_assente_vale_vero(monkeypatch):
    monkeypatch.delenv("BINANCE_TESTNET", raising=False)
    assert cfg._get_bool_sicuro("BINANCE_TESTNET") is True


def test_tarature_senza_modalita_ne_segreti(tmp_path, monkeypatch):
    f = tmp_path / "tuning.env"
    f.write_text("DRY_RUN=false\nBINANCE_TESTNET=false\nBACKTEST_PARITY=true\nBINANCE_API_KEY=x\nTARATURA_DI_PROVA_7NOV=3\n")
    for k in ("TARATURA_DI_PROVA_7NOV",):
        monkeypatch.delenv(k, raising=False)
    prima = {k: cfg.os.environ.get(k) for k in ("DRY_RUN", "BINANCE_TESTNET", "BACKTEST_PARITY", "BINANCE_API_KEY")}
    try:
        scartate = cfg.carica_tuning(str(f))
        assert sorted(scartate) == ["BACKTEST_PARITY", "BINANCE_API_KEY", "BINANCE_TESTNET", "DRY_RUN"]
        assert cfg.os.environ.get("TARATURA_DI_PROVA_7NOV") == "3"
        assert {k: cfg.os.environ.get(k) for k in prima} == prima       # niente cambiato
    finally:
        cfg.os.environ.pop("TARATURA_DI_PROVA_7NOV", None)
    assert cfg.carica_tuning(str(tmp_path / "manca.env")) == []


def test_parita_col_backtest_rifiutata_con_soldi_veri(tmp_path, capsys):
    acceso = tmp_path / "conto_vero_acceso"
    acceso.write_text("si")
    vero = types.SimpleNamespace(DRY_RUN=False, BINANCE_TESTNET=True, BACKTEST_PARITY=True)
    with pytest.raises(SystemExit, match="BACKTEST_PARITY"):        # anche con l'interruttore del conto vero
        cfg.controlla_avvio(vero, interruttore_conto_vero=str(acceso))
    cfg.controlla_avvio(types.SimpleNamespace(DRY_RUN=True, BINANCE_TESTNET=True, BACKTEST_PARITY=True))
    assert "ambiente: DRY_RUN=False" in capsys.readouterr().out


def test_dry_run_falso_senza_interruttore_parte_con_il_conto_vero_in_sole_protezioni(tmp_path, capsys):
    """Fase 2 del conto vero (docs/conto_vero.md) e revisione dell'8 novembre 2026, problema 53: con DRY_RUN falso e la parità
    spenta il bot parte sempre (paper e demo accesi); senza l'interruttore ops/conto_vero_acceso il conto vero gira nelle sole
    protezioni. Con la parità accesa l'avvio resta rifiutato anche senza interruttore. Per difetto guarda il file del conto vero."""
    from pathlib import Path

    from bot.portafoglio import conto_vero as cv
    s = types.SimpleNamespace(DRY_RUN=False, BINANCE_TESTNET=True, BACKTEST_PARITY=False)
    interruttore = tmp_path / "conto_vero_acceso"
    cfg.controlla_avvio(s, interruttore_conto_vero=str(interruttore))      # non esce
    assert "conto vero solo nelle protezioni" in capsys.readouterr().out
    interruttore.write_text("si")
    cfg.controlla_avvio(s, interruttore_conto_vero=str(interruttore))
    assert "solo G1 sul conto vero" in capsys.readouterr().out
    with pytest.raises(SystemExit, match="BACKTEST_PARITY"):
        cfg.controlla_avvio(types.SimpleNamespace(DRY_RUN=False, BINANCE_TESTNET=True, BACKTEST_PARITY=True),
                            interruttore_conto_vero=str(tmp_path / "manca"))
    assert Path(cfg.INTERRUTTORE_CONTO_VERO) == cv.INTERRUTTORE
    main = (Path(cfg.__file__).resolve().parent / "main.py").read_text(encoding="utf-8")
    assert "controlla_avvio(settings)\n    TradingBot().run()" in main          # dopo il controllo il bot parte tutto


def test_vecchio_esecutore_non_crea_il_client_del_conto_vero(monkeypatch):
    from bot.core.firebase_client import FirebaseClient
    from bot.execution.executor import ExecutionEngine
    chiamato = []
    finto = types.ModuleType("binance.client")
    finto.Client = lambda *a, **k: chiamato.append(1)
    monkeypatch.setitem(sys.modules, "binance.client", finto)
    eng = ExecutionEngine(firebase=FirebaseClient(), dry_run=False)
    assert eng.dry_run is True and eng._client is None and not chiamato
