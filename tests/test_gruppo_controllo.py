"""IL GRUPPO DI CONTROLLO DEL FUORI CAMPIONE: la raccolta (30 set 2026, K3).

Si verifica che:
  * il campione delle bocciate sia casuale e riproducibile col seme, e che
    non tocchi il generatore della discovery (stesso giro con e senza raccolta);
  * entrino solo bocciate con almeno 30 trade, non validate, non nel registro
    con conferme, non varianti troncate;
  * la foto delle conferme si faccia una volta al giorno italiano;
  * un disco che solleva non faccia mai fallire il giro (fail-open);
  * i file si rileggano con tutto cio' che serve al rigioco.
"""
import inspect
import os
import random
from datetime import datetime, timezone
from types import SimpleNamespace

import numpy as np
import pandas as pd
import pytest

from bot.strategies.generated import spec_id
from scripts import discover_strategies as d
from scripts import gruppo_controllo as gc

NOW = datetime(2026, 9, 30, 10, 0, tzinfo=timezone.utc).timestamp()
GLOBALE = {"scale_r_mults": [1.5, 3.0, 5.0], "sl_to_breakeven": True, "profit_lock_keep": 0.5}


def _spec(**extra):
    spec = {"features": [{"kind": "rsi_extreme", "low": 30.0, "high": 70.0}],
            "volume_mult": 0.0, "min_adx": 0.0, "atr_mult_stop": 1.5, "rr": 2.0}
    spec.update(extra)
    spec["id"] = spec_id(spec)
    return spec


def _esito(passa: bool, trades: int = 40, **extra) -> dict:
    r = {"passed": passa, "pf": 1.3 if passa else 0.9, "pnl": 0.2 if passa else -0.05,
         "trades": trades, "win": 0.5, "holdout": {}, "regime_pf": {}, "max_dd": 0.1,
         "scale_r_mults": None, "sl_to_breakeven": None, "profit_lock_keep": None,
         "data_end": NOW - 900, "fail_criteria": [] if passa else ["pf"],
         "fail_binding": "" if passa else "pf", "fail_shortfall": 0.0 if passa else 0.1,
         "near_miss": False, "t_stat": 0.7, "oos_rows": [], "window_pnls": [0.1, -0.2, 0.0],
         "direzione_pf": {}, "solo_propria_config": False}
    r.update(extra)
    return r


def _voci(n: int) -> list[dict]:
    return [{"key": f"C{i:03d}USDT|gen_{i:03d}", "symbol": f"C{i:03d}USDT",
             "spec_id": f"gen_{i:03d}", "trades": 30 + i} for i in range(n)]


@pytest.fixture
def attivo(monkeypatch):
    monkeypatch.setattr(gc, "ATTIVO", True)
    monkeypatch.setattr(gc, "CAMPIONE", 50)
    monkeypatch.setattr(gc, "MIN_TRADE", 30)
    monkeypatch.setattr(gc, "TETTO_MB", 300.0)


# --------------------------------------------------------------------------- #
# 1. il campione: casuale, riproducibile, senza toccare altri generatori       #
# --------------------------------------------------------------------------- #
def test_campione_riproducibile_col_seme_e_indipendente_dall_ordine():
    voci = _voci(500)
    a = gc.campiona(voci, 50, seme=12345)
    b = gc.campiona(list(reversed(voci)), 50, seme=12345)      # altro ordine dei worker
    c = gc.campiona(voci, 50, seme=54321)
    assert [v["key"] for v in a] == [v["key"] for v in b]
    assert len(a) == 50 and len({v["key"] for v in a}) == 50
    assert [v["key"] for v in a] != [v["key"] for v in c]
    # non sono le prime ne' le ultime: e' un'estrazione, non una classifica
    assert [v["key"] for v in a] != sorted(v["key"] for v in voci)[:50]


def test_campione_senza_doppioni_e_con_pochi_candidati_prende_tutti():
    voci = _voci(10) + _voci(10)            # la stessa coppia arrivata due volte
    tutte = gc.campiona(voci, 50, seme=1)
    assert len(tutte) == 10
    assert gc.campiona([], 50, seme=1) == []


def test_campione_uniforme_non_sceglie_i_migliori():
    """Su molte estrazioni ogni voce esce con la stessa frequenza (circa
    50/200), indipendentemente dai suoi numeri."""
    voci = _voci(200)
    conta = {v["key"]: 0 for v in voci}
    for s in range(400):
        for v in gc.campiona(voci, 50, seme=s):
            conta[v["key"]] += 1
    attesa = 400 * 50 / 200
    assert min(conta.values()) > attesa * 0.6 and max(conta.values()) < attesa * 1.4


def test_campione_e_seme_non_toccano_i_generatori_globali(monkeypatch, tmp_path, attivo):
    monkeypatch.delenv("CONTROLLO_GRUPPI_SEME", raising=False)
    random.seed(7)
    np.random.seed(7)
    prima_py, prima_np = random.getstate(), np.random.get_state()
    gc.nuovo_seme()
    gc.campiona(_voci(300), 50, seme=99)
    gc.raccogli(idonee=_voci(300), pairs={}, spec_di=lambda s, i: {"id": i},
                foto_di=lambda: [], interval="15m", run_end="2026-09-30",
                start="2022-01-01", windows=3, now=NOW, cartella=str(tmp_path))
    assert random.getstate() == prima_py
    dopo_np = np.random.get_state()
    assert prima_np[0] == dopo_np[0] and (prima_np[1] == dopo_np[1]).all()


def test_seme_dichiarato_dall_ambiente(monkeypatch):
    monkeypatch.setenv("CONTROLLO_GRUPPI_SEME", "4242")
    assert gc.nuovo_seme() == 4242
    monkeypatch.delenv("CONTROLLO_GRUPPI_SEME")
    assert 0 <= gc.nuovo_seme() < 2 ** 31


# --------------------------------------------------------------------------- #
# 2. chi entra: solo bocciate con >= 30 trade                                  #
# --------------------------------------------------------------------------- #
def test_solo_bocciate_con_almeno_30_trade(attivo):
    sp = _spec()
    assert gc.voce_idonea("XUSDT", sp, _esito(False, trades=30), set(), GLOBALE) is not None
    assert gc.voce_idonea("XUSDT", sp, _esito(False, trades=29), set(), GLOBALE) is None
    assert gc.voce_idonea("XUSDT", sp, _esito(True, trades=300), set(), GLOBALE) is None
    # una validata bocciata oggi sta nel gruppo delle validate, non qui
    assert gc.voce_idonea("XUSDT", sp, _esito(False), {f"XUSDT|{sp['id']}"}, GLOBALE) is None
    # una variante troncata e' giudicata su dati vecchi: fuori
    tronc = _spec(origine="referto", ipotesi_da=NOW - 86400)
    assert gc.voce_idonea("XUSDT", tronc, _esito(False), set(), GLOBALE) is None
    # un esito storto non solleva
    assert gc.voce_idonea("XUSDT", sp, None, set(), GLOBALE) is None


def test_voce_porta_motivo_e_uscita_usata(attivo):
    sp = _spec()
    v = gc.voce_idonea("XUSDT", sp, _esito(False), set(), GLOBALE)
    assert v["key"] == f"XUSDT|{sp['id']}" and v["uscita_fonte"] == "globale"
    assert v["uscita"] == GLOBALE and v["fail_binding"] == "pf" and v["fail_criteria"] == ["pf"]
    # caduta DOPO la scelta della scala (passo 3 o holdout): la configurazione scelta
    r = _esito(False, scale_r_mults=[2.0, 4.0], sl_to_breakeven=False, profit_lock_keep=0.75,
               holdout={"ok": False}, fail_binding="holdout", fail_criteria=["holdout"])
    v = gc.voce_idonea("XUSDT", sp, r, set(), GLOBALE)
    assert v["uscita_fonte"] == "scelta_dal_gate"
    assert v["uscita"] == {"scale_r_mults": [2.0, 4.0], "sl_to_breakeven": False,
                           "profit_lock_keep": 0.75}
    assert v["holdout_ok"] is False


def test_fuori_chi_nel_registro_ha_gia_una_conferma():
    voci = _voci(3)
    pairs = {voci[0]["key"]: {"pass_count": 1}, voci[1]["key"]: {"pass_count": 0}}
    assert [v["key"] for v in gc.togli_dal_registro(voci, pairs)] == [voci[1]["key"], voci[2]["key"]]


# --------------------------------------------------------------------------- #
# 3. il worker: stesso giro con e senza raccolta                               #
# --------------------------------------------------------------------------- #
class _Candle:
    def __init__(self, ts):
        self.open_time = ts


def _gira_disc_one(monkeypatch, attiva: bool):
    specs = [_spec(volume_mult=v) for v in (0.0, 1.5, 2.0, 2.5)]
    esiti = {specs[0]["id"]: _esito(True), specs[1]["id"]: _esito(False, trades=45),
             specs[2]["id"]: _esito(False, trades=12), specs[3]["id"]: _esito(False, trades=80)}
    visto = []

    def finto(opt, sym, candles, frame, spec, **kw):
        visto.append((spec["id"], sorted(kw)))
        return dict(esiti[spec["id"]])
    prima = dict(d._W)
    monkeypatch.setattr(gc, "ATTIVO", attiva)
    try:
        d._W.clear()
        d._W.update(opt=SimpleNamespace(bt=None), end="2026-09-30", min_history=2,
                    args=SimpleNamespace(interval="15m", start="2022-01-01", source="auto"),
                    specs=specs, scala_paper=None, keep_paper=None, scale_strategie={},
                    btc_ctx=None, specs_per_symbol={}, bocciate_ok=False,
                    gia_validate=set(), config_validate={})
        monkeypatch.setattr(d, "load_candles",
                            lambda *a, **k: [_Candle(datetime(2026, 9, 30, tzinfo=timezone.utc))] * 4)
        monkeypatch.setattr("backtesting.quality.looks_delisted", lambda *a, **k: False)
        monkeypatch.setattr(d, "compute_indicator_frame", lambda c: pd.DataFrame({"close": [1.0] * len(c)}))
        monkeypatch.setattr(d, "evaluate_spec", finto)
        random.seed(3)
        ris = d._disc_one("XUSDT")
        stato = random.getstate()
    finally:
        d._W.clear()
        d._W.update(prima)
    return ris, visto, stato, specs


def test_disc_one_identico_con_e_senza_raccolta(monkeypatch):
    con, visto_con, stato_con, specs = _gira_disc_one(monkeypatch, True)
    senza, visto_senza, stato_senza, _ = _gira_disc_one(monkeypatch, False)
    assert visto_con == visto_senza          # stesse spec, stesso ordine, stessi argomenti
    assert stato_con == stato_senza          # nessun numero casuale consumato
    assert len(con) == len(senza) == 9
    for i, (a, b) in enumerate(zip(con, senza)):
        if i == 6:                           # diag: uguale tranne la lista del controllo
            assert {k: v for k, v in a.items() if k != "controllo"} == \
                   {k: v for k, v in b.items() if k != "controllo"}
        else:
            assert a == b
    # e con la raccolta accesa le idonee sono le bocciate con >= 30 trade
    assert [v["spec_id"] for v in con[6]["controllo"]] == [specs[1]["id"], specs[3]["id"]]
    assert senza[6]["controllo"] == []


# --------------------------------------------------------------------------- #
# 4. i file: foto una volta al giorno, formato rileggibile, fail-open          #
# --------------------------------------------------------------------------- #
def _raccogli(cartella, now=NOW, idonee=None, foto=None, interval="15m", seme=777):
    specs = {v["spec_id"]: {"id": v["spec_id"], "features": [], "rr": 2.0}
             for v in (idonee if idonee is not None else _voci(120))}
    chiamate = []

    def foto_di():
        chiamate.append(1)
        return foto if foto is not None else [{"key": "A|x", "pass_count": 1}]
    riga = gc.raccogli(idonee=idonee if idonee is not None else _voci(120), pairs={},
                       spec_di=lambda s, i: specs.get(i), foto_di=foto_di, interval=interval,
                       run_end="2026-09-30", start="2022-01-01", windows=3, now=now,
                       seme=seme, cartella=str(cartella))
    return riga, chiamate


def test_foto_una_volta_al_giorno_italiano_e_bocciate_in_append(tmp_path, attivo, capsys):
    r1, c1 = _raccogli(tmp_path)
    r2, c2 = _raccogli(tmp_path, now=NOW + 3 * 3600)
    assert c1 == [1] and c2 == []            # la seconda volta la foto non si ricostruisce
    assert "salvate 50 bocciate su 120 idonee (seme 777)" in r1 and "foto conferme: 1 coppie" in r1
    assert "foto conferme: già fatta oggi" in r2
    assert "[controllo-gruppi]" in capsys.readouterr().out
    assert len(gc.leggi(tmp_path / "2026-09-30_bocciate.jsonl")) == 100
    assert len(gc.leggi(tmp_path / "2026-09-30_conferme.jsonl")) == 1
    # 22:30 UTC del 30 set = 00:30 del 1 ott in Italia: giorno nuovo, foto nuova
    tardi = datetime(2026, 9, 30, 22, 30, tzinfo=timezone.utc).timestamp()
    r3, c3 = _raccogli(tmp_path, now=tardi)
    assert c3 == [1] and os.path.exists(tmp_path / "2026-10-01_conferme.jsonl")


def test_formato_delle_bocciate_rileggibile_con_tutto_per_il_rigioco(tmp_path, attivo):
    sp = _spec(timeframe="1h")
    v = gc.voce_idonea("XUSDT", sp, _esito(False, trades=33), set(), GLOBALE)
    gc.raccogli(idonee=[v], pairs={}, spec_di=lambda s, i: sp if i == sp["id"] else None,
                foto_di=lambda: [], interval="1h", run_end="2026-09-30", start="2022-01-01",
                windows=3, now=NOW, seme=5, cartella=str(tmp_path), modalita="completa")
    (riga,) = gc.leggi(tmp_path / "2026-09-30_bocciate.jsonl")
    assert riga["formato"] == gc.FORMATO and riga["tipo"] == "bocciata"
    assert riga["key"] == f"XUSDT|{sp['id']}" and riga["spec"] == sp      # spec INTERA
    assert riga["timeframe"] == "1h" and riga["interval"] == "1h"
    assert riga["valutata_at"] == NOW and riga["data_end"] == NOW - 900
    assert riga["uscita"] == GLOBALE and riga["uscita_fonte"] == "globale"
    assert riga["motivo"]["binding"] == "pf" and riga["numeri"]["trades"] == 33
    assert riga["seme"] == 5 and riga["popolazione"] == 1
    assert riga["run_end"] == "2026-09-30" and riga["windows"] == 3


def test_una_riga_con_nan_salta_da_sola(tmp_path, attivo):
    voci = _voci(2)
    voci[0]["pf"] = float("nan")
    _raccogli(tmp_path, idonee=voci)
    righe = gc.leggi(tmp_path / "2026-09-30_bocciate.jsonl")
    assert [r["key"] for r in righe] == [voci[1]["key"]]


def test_fail_open_disco_che_solleva(tmp_path, attivo, monkeypatch):
    import builtins

    def rotto(*a, **k):
        raise OSError("disco pieno")
    monkeypatch.setattr(builtins, "open", rotto)
    riga, _ = _raccogli(tmp_path)            # non solleva
    assert "NON salvat" in riga
    monkeypatch.undo()
    # la cartella non si crea: niente eccezioni, solo una riga
    monkeypatch.setattr(gc, "ATTIVO", True)
    monkeypatch.setattr(gc.os, "makedirs", rotto)
    riga, _ = _raccogli(tmp_path / "nuova")
    assert "raccolta saltata" in riga


def test_fail_open_foto_che_solleva_rifatta_al_giro_dopo(tmp_path, attivo):
    def rotta():
        raise RuntimeError("registro storto")
    riga = gc.raccogli(idonee=[], pairs={}, spec_di=lambda s, i: None, foto_di=rotta,
                       interval="15m", run_end="2026-09-30", start="2022-01-01", windows=3,
                       now=NOW, seme=1, cartella=str(tmp_path))
    assert "foto conferme NON salvata" in riga
    assert not os.path.exists(tmp_path / "2026-09-30_conferme.jsonl")
    _, c = _raccogli(tmp_path)
    assert c == [1]


def test_tetto_di_spazio_e_spenta(tmp_path, attivo, monkeypatch):
    monkeypatch.setattr(gc, "TETTO_MB", 0.0)
    (tmp_path / "vecchio.jsonl").write_text("x" * 100)
    riga, c = _raccogli(tmp_path)
    assert "tetto di spazio superato" in riga and c == []
    monkeypatch.setattr(gc, "ATTIVO", False)
    riga, c = _raccogli(tmp_path)
    assert "spenta" in riga and c == []


def test_pulizia_dei_file_vecchi(tmp_path):
    vecchio = tmp_path / "2026-01-01_bocciate.jsonl"
    vecchio.write_text("{}\n")
    os.utime(vecchio, (NOW - 200 * 86400, NOW - 200 * 86400))
    nuovo = tmp_path / "2026-09-29_bocciate.jsonl"
    nuovo.write_text("{}\n")
    os.utime(nuovo, (NOW - 86400, NOW - 86400))
    assert gc.pulisci(str(tmp_path), giorni=120, now=NOW) == 1
    assert not vecchio.exists() and nuovo.exists()


# --------------------------------------------------------------------------- #
# 5. il ponte nella discovery: spec ritrovata, foto con le regole del registro #
# --------------------------------------------------------------------------- #
def test_ponte_della_discovery_scrive_spec_e_foto(tmp_path, attivo, monkeypatch):
    from bot.core.firebase_client import encode_pairs
    from scripts.optimize import MIN_PASSES
    monkeypatch.setattr(gc, "CONTROLLO_DIR", str(tmp_path))
    comune, figlia = _spec(volume_mult=1.0), _spec(volume_mult=3.0)
    idonee = [gc.voce_idonea("AUSDT", comune, _esito(False), set(), GLOBALE),
              gc.voce_idonea("BUSDT", figlia, _esito(False), set(), GLOBALE),
              # gia' nel registro con una conferma: sta nella foto, non fra le bocciate
              gc.voce_idonea("CUSDT", comune, _esito(False), set(), GLOBALE)]
    pairs = {
        f"VUSDT|{comune['id']}": {"symbol": "VUSDT", "strategy": comune["id"], "generated": True,
                                  "pass_count": MIN_PASSES, "last_seen_at": NOW - 3600,
                                  "declassata": True},
        f"CUSDT|{comune['id']}": {"symbol": "CUSDT", "strategy": comune["id"], "generated": True,
                                  "pass_count": 1, "last_seen_at": NOW - 3600},
    }
    args = SimpleNamespace(interval="15m", start="2022-01-01", windows=3)
    riga = d.raccogli_gruppo_controllo(idonee, {"pairs": encode_pairs(pairs)}, {comune["id"]: comune},
                                       [comune], {"BUSDT": [figlia]}, args, "2026-09-30",
                                       NOW, "completa")
    assert "salvate 2 bocciate su 2 idonee" in riga and "foto conferme: 2 coppie" in riga
    boc = {r["key"]: r for r in gc.leggi(tmp_path / "2026-09-30_bocciate.jsonl")}
    assert set(boc) == {f"AUSDT|{comune['id']}", f"BUSDT|{figlia['id']}"}
    assert boc[f"BUSDT|{figlia['id']}"]["spec"] == figlia
    foto = {r["key"]: r for r in gc.leggi(tmp_path / "2026-09-30_conferme.jsonl")}
    v = foto[f"VUSDT|{comune['id']}"]
    assert v["validata"] is True and v["declassata"] is True and v["pass_count"] == MIN_PASSES
    assert v["istante"] == NOW and v["timeframe"] == "15m" and v["uscita"]["scale_r_mults"]
    c = foto[f"CUSDT|{comune['id']}"]
    assert c["validata"] is False and c["declassata"] is False and c["pass_count"] == 1


def test_main_raccoglie_fuori_dagli_shard_e_prima_del_merge():
    main = inspect.getsource(d.main)
    i_racc = main.index("raccogli_gruppo_controllo(idonee_controllo")
    assert "if args.num_shards <= 1:" in main[i_racc - 400:i_racc]
    assert i_racc < main.index("merge_into_registry(")
    assert 'idonee_controllo.extend(diag.get("controllo") or [])' in main
