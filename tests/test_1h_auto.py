"""LA PASSATA A 1 ORA SU ~30 COIN, «auto30» (26 set 2026, passo 5 del piano del
26 set 15:xx, backlog C1).

Il numero che l'ha fatta nascere: a 1 ora le candidate battono il pareggio nel
29-37% dei casi contro l'8% dei 15 minuti (C1), ma la passata girava su 5 coin
e in 4 giorni ha prodotto una sola candidata (ADAUSDT, 1 conferma): 0,22% di
passaggio su 460 valutazioni il 26 set. Da oggi `DISCOVERY_EXTRA` vale
«1h:auto30»: le 5 fisse + le coin con coppie a 1 ora + le coin con validate
(piu' coppie prima) + il top per volume, fino a 30; 2 minuti per 5 coin
misurati il 26 set -> ~12 minuti, dentro i 40 massimi."""
from __future__ import annotations

import inspect
import subprocess
import types

import pytest

from bot.core.firebase_client import encode_pairs
from scripts import optimize as o

NOW = 1_758_844_800.0 + 3 * 3600
FISSE = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "ADAUSDT", "BCHUSDT"]
UNIVERSO = ["BTCUSDT", "ETHUSDT", "XRPUSDT", "BNBUSDT", "SOLUSDT", "DOGEUSDT"] + \
           [f"V{i:02d}USDT" for i in range(40)]


def _rec(sym, sid, passi=3, **extra):
    r = {"symbol": sym, "strategy": sid, "generated": True, "pass_count": passi,
         "last_seen_at": NOW - 100}
    r.update(extra)
    return r


def _pairs():
    p = {"XXXUSDT|gen_1": _rec("XXXUSDT", "gen_1"), "XXXUSDT|gen_2": _rec("XXXUSDT", "gen_2"),
         "XXXUSDT|gen_3": _rec("XXXUSDT", "gen_3"),
         "YYYUSDT|gen_4": _rec("YYYUSDT", "gen_4"),
         "ZZZUSDT|gen_5": _rec("ZZZUSDT", "gen_5"), "ZZZUSDT|gen_6": _rec("ZZZUSDT", "gen_6"),
         "BTCUSDT|gen_7": _rec("BTCUSDT", "gen_7"),                       # gia' fra le fisse
         "WWWUSDT|gen_8": _rec("WWWUSDT", "gen_8", passi=2),              # non validata
         "OLDUSDT|gen_9": _rec("OLDUSDT", "gen_9", last_seen_at=NOW - 30 * 86400),   # congelata
         "QQQUSDT|gen_1h": _rec("QQQUSDT", "gen_1h", passi=1),            # coppia a 1 ora in cammino
         "AAAUSDT|gen_1h": _rec("AAAUSDT", "gen_1h", passi=0)}            # a 0: non conta
    return p


SPECS = {"gen_1h": {"id": "gen_1h", "timeframe": "1h"}, "gen_1": {"id": "gen_1"}}


class _FB:
    def __init__(self, pairs=None, specs=None, rotto=False):
        self.docs = {("strategy_registry", "validated"): {"pairs": encode_pairs(pairs or {})},
                     ("discovered_strategies", "specs"): {"specs": encode_pairs(specs or {})}}
        self.rotto = rotto

    def get_doc(self, c, k):
        if self.rotto:
            raise RuntimeError("giu'")
        return self.docs.get((c, k))


# --------------------------------------------------------------------------- #
# 1. il default e le costanti dichiarate                                      #
# --------------------------------------------------------------------------- #
def test_il_default_e_auto30_e_il_tetto_resta_40_minuti():
    assert o.DISCOVERY_EXTRA == "1h:auto30"
    assert o.DISCOVERY_EXTRA_VECCHIO_DEFAULT == "1h:BTCUSDT,ETHUSDT,SOLUSDT,ADAUSDT,BCHUSDT"
    assert o.DISCOVERY_EXTRA_MAX_S == 2400
    assert o.MINUTI_1H_PER_COIN == pytest.approx(0.4)      # 2 min per 5 coin, 26 set
    assert list(o.COIN_1H_FISSE) == FISSE


# --------------------------------------------------------------------------- #
# 2. la composizione di autoN                                                  #
# --------------------------------------------------------------------------- #
def test_auto30_fisse_poi_coppie_a_1h_poi_validate_poi_volume():
    coin, fonti = o.coin_1h_auto(30, _pairs(), UNIVERSO, specs=SPECS, now=NOW)
    assert coin[:5] == FISSE
    assert coin[5] == "QQQUSDT", "una coppia a 1 ora in cammino non si ferma"
    # validate: XXX (3 coppie) prima di ZZZ (2) prima di YYY (1); BTC e' gia' dentro;
    # WWW (2 pass) e OLD (congelata) non sono validate
    assert coin[6:9] == ["XXXUSDT", "ZZZUSDT", "YYYUSDT"]
    # poi il volume, nell'ordine del volume, senza doppioni
    assert coin[9:] == [s for s in UNIVERSO if s not in coin[:9]][:21]
    assert len(coin) == 30 and len(set(coin)) == 30
    assert fonti == {"fisse": 5, "con_1h": 1, "con_validate": 3, "top_volume": 21}


def test_il_tetto_n_si_rispetta_e_le_fisse_vengono_prima():
    coin, fonti = o.coin_1h_auto(7, _pairs(), UNIVERSO, specs=SPECS, now=NOW)
    assert coin == FISSE + ["QQQUSDT", "XXXUSDT"]
    assert fonti == {"fisse": 5, "con_1h": 1, "con_validate": 1, "top_volume": 0}
    assert o.coin_1h_auto(0, _pairs(), UNIVERSO, now=NOW)[0] == []
    assert o.coin_1h_auto(3, {}, [], now=NOW)[0] == FISSE[:3]


def test_a_parita_di_ingressi_la_lista_e_la_stessa():
    a, _ = o.coin_1h_auto(30, _pairs(), UNIVERSO, specs=SPECS, now=NOW)
    b, _ = o.coin_1h_auto(30, dict(reversed(list(_pairs().items()))), UNIVERSO, specs=SPECS, now=NOW)
    assert a == b


def test_senza_registro_restano_fisse_e_volume():
    coin, fonti = o.coin_1h_auto(10, {}, UNIVERSO, now=NOW)
    assert coin == FISSE + ["XRPUSDT", "BNBUSDT", "DOGEUSDT", "V00USDT", "V01USDT"]
    assert fonti["top_volume"] == 5


# --------------------------------------------------------------------------- #
# 3. la variabile d'ambiente: lista esplicita, autoN, il vecchio default        #
# --------------------------------------------------------------------------- #
def test_la_vecchia_lista_di_5_coin_vale_come_auto30(monkeypatch):
    monkeypatch.setattr(o, "top_symbols_by_volume", lambda n: list(UNIVERSO))
    fb = _FB(_pairs(), SPECS)
    coin, modo = o.risolvi_coin_extra("BTCUSDT,ETHUSDT,SOLUSDT,ADAUSDT,BCHUSDT", fb, now=NOW)
    assert modo.startswith("vecchio default -> auto30:") and len(coin) == 30
    assert coin[:6] == FISSE + ["QQQUSDT"]
    # spazi e minuscole non contano: e' la stessa lista scritta a mano nella unit
    coin2, modo2 = o.risolvi_coin_extra(" btcusdt, ethusdt,solusdt , adausdt,bchusdt ", fb, now=NOW)
    assert coin2 == coin and modo2 == modo


def test_una_lista_esplicita_si_rispetta_senza_toccare_registro_o_rete(monkeypatch):
    def niente(n):
        raise AssertionError("con una lista esplicita non si chiede il volume")
    monkeypatch.setattr(o, "top_symbols_by_volume", niente)
    coin, modo = o.risolvi_coin_extra("BTCUSDT,XRPUSDT", _FB(rotto=True), now=NOW)
    assert coin == ["BTCUSDT", "XRPUSDT"] and modo == "lista"
    coin, modo = o.risolvi_coin_extra("btcusdt , xrpusdt", None, now=NOW)
    assert coin == ["BTCUSDT", "XRPUSDT"]


def test_auton_con_un_numero_e_il_ripiego_a_30(monkeypatch):
    monkeypatch.setattr(o, "top_symbols_by_volume", lambda n: list(UNIVERSO))
    coin, modo = o.risolvi_coin_extra("auto10", _FB(_pairs(), SPECS), now=NOW)
    assert len(coin) == 10 and modo.startswith("auto10:")
    coin, modo = o.risolvi_coin_extra("auto", _FB(), now=NOW)
    assert len(coin) == 30 and modo.startswith("auto30:")
    coin, modo = o.risolvi_coin_extra("autoX", _FB(), now=NOW)
    assert len(coin) == 30


def test_registro_illeggibile_non_ferma_la_passata(monkeypatch, capsys):
    monkeypatch.setattr(o, "top_symbols_by_volume", lambda n: list(UNIVERSO))
    coin, modo = o.risolvi_coin_extra("auto30", _FB(rotto=True), now=NOW)
    assert coin[:5] == FISSE and len(coin) == 30
    assert "registro non letto" in capsys.readouterr().out


# --------------------------------------------------------------------------- #
# 4. passata_extra: il comando, la stima stampata, il tetto                    #
# --------------------------------------------------------------------------- #
def test_passata_extra_lancia_30_coin_e_stampa_la_stima(monkeypatch, capsys):
    monkeypatch.setattr(o, "DISCOVERY_EXTRA", "1h:auto30")
    monkeypatch.setattr(o, "top_symbols_by_volume", lambda n: list(UNIVERSO))
    lanciato = {}

    def run(cmd, timeout=None):
        lanciato["cmd"], lanciato["timeout"] = cmd, timeout
        return types.SimpleNamespace(returncode=0)
    monkeypatch.setattr(subprocess, "run", run)
    args = types.SimpleNamespace(windows=3, start="2022-01-01")
    o.passata_extra(args, _FB(_pairs(), SPECS))
    cmd = lanciato["cmd"]
    assert cmd[cmd.index("--interval") + 1] == "1h"
    coin = cmd[cmd.index("--symbols") + 1].split(",")
    assert len(coin) == 30 and coin[:5] == FISSE
    assert lanciato["timeout"] == 2400
    out = capsys.readouterr().out
    assert "discovery a 1h su 30 coin (auto30:" in out
    assert "~12 min stimati: 2 min per 5 coin misurati il 26 set" in out
    assert "(max 40 min)" in out


def test_passata_extra_con_lista_esplicita_e_come_prima(monkeypatch, capsys):
    monkeypatch.setattr(o, "DISCOVERY_EXTRA", "1h:BTCUSDT,ETHUSDT")
    lanciato = {}
    monkeypatch.setattr(subprocess, "run",
                        lambda cmd, timeout=None: (lanciato.__setitem__("cmd", cmd),
                                                   types.SimpleNamespace(returncode=0))[1])
    o.passata_extra(types.SimpleNamespace(windows=3, start="2022-01-01"), None)
    assert lanciato["cmd"][lanciato["cmd"].index("--symbols") + 1] == "BTCUSDT,ETHUSDT"
    assert "su 2 coin (lista)" in capsys.readouterr().out


def test_passata_extra_spenta_o_senza_coin_non_lancia(monkeypatch):
    def niente(*a, **k):
        raise AssertionError("non doveva lanciare")
    monkeypatch.setattr(subprocess, "run", niente)
    monkeypatch.setattr(o, "DISCOVERY_EXTRA", "")
    o.passata_extra(types.SimpleNamespace(windows=3, start="2022-01-01"), None)
    monkeypatch.setattr(o, "DISCOVERY_EXTRA", "1h:")
    o.passata_extra(types.SimpleNamespace(windows=3, start="2022-01-01"), None)


def test_il_main_di_optimize_passa_firebase_alla_passata():
    assert "passata_extra(args, fb)" in inspect.getsource(o.main)
    src = inspect.getsource(o.passata_extra)
    assert "timeout=DISCOVERY_EXTRA_MAX_S" in src
    assert "risolvi_coin_extra(coins, fb, interval=interval)" in src
