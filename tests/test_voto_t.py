"""H1-misura, 30 set 2026 (si' del proprietario): il voto t di ogni validata.

Cosa si protegge, su dati finti:
  * la t (walk-forward e holdout, coi loro trade) sta nel NUCLEO del registro:
    sopravvive all'alleggerimento e alla codifica compatta, e il merge della
    discovery la scrive anche per una coppia NON ancora validata;
  * l'ultimo esame (holdout) calcola la t senza cambiare il verdetto;
  * la passata una tantum (`scripts/t_validate.py`) scrive SOLO il suo file
    locale: nessuna scrittura Firebase, registro identico prima e dopo; l'holdout
    si calcola sui dati tagliati al giorno della validazione; un lucchetto
    impedisce due passate insieme e il file si scrive in modo atomico;
  * la sezione FUORI CAMPIONE divide per t (e per t/radice(n)), stampa la regola
    PRIMA dei numeri, resta nel mezzo KB in piu' e non fa letture in piu';
  * la riga della lista bianca, esatta.

30 set 2026, revisione del lavoro B (correzioni ai rilievi confermati): t a 3
decimali nel registro (come il file), t fissata alla promozione, walk-forward
sui dati del giorno della validazione, lucchetto del kernel, file salvato dopo
ogni coin, controllo del gate prima di ogni coin, divisione per segnale (non
per coppia), holdout con meno di 5 trade fuori dai gruppi, soglia fissa per
t/radice(n), voci del file scartate se di un'altra configurazione o validazione.
"""
import copy
import datetime as dt
import json
import math
import multiprocessing
import os
import signal
import time
from types import SimpleNamespace

import pandas as pd
import pytest

from bot.core.firebase_client import _BREVI, decode_pairs, encode_pairs, encode_registry
from scripts import optimize as op
from scripts import portafoglio_backtest as pb
from scripts import t_validate as tv

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CAMPI_T = ("last_t", "last_trades", "last_t_holdout", "last_trades_holdout")
CAMPI_VAL = ("val_t", "val_trades", "val_t_holdout", "val_trades_holdout", "val_uscita")


def _ts(y, m, d, h=0, mi=0):
    return dt.datetime(y, m, d, h, mi, tzinfo=dt.timezone.utc).timestamp()


@pytest.fixture(autouse=True)
def _niente_systemd(monkeypatch):
    """Nei test il gate non c'e': nessuna unita' attiva, nessun timer. Cosi' il
    risultato non dipende dalla macchina (su un runner con systemd vero
    `systemctl` risponde). I test del gate li rimettono a mano."""
    monkeypatch.setattr(tv, "servizio_gate_attivo", lambda: False)
    monkeypatch.setattr(tv, "secondi_al_prossimo_giro", lambda ora=None: None)


# --------------------------------------------------------------------------- #
# 1. il nucleo del registro                                                    #
# --------------------------------------------------------------------------- #
def test_la_t_e_nel_nucleo_e_sopravvive_all_alleggerimento_e_alla_codifica():
    assert set(CAMPI_T) <= op.REGISTRY_CORE_FIELDS
    assert set(CAMPI_VAL) <= op.REGISTRY_CORE_FIELDS and set(CAMPI_VAL) <= set(_BREVI)
    rec = {"pass_count": 1, "last_seen_at": 1e9, "generated": True, "last_pf": 1.4,
           "last_t": 1.87, "last_trades": 140, "last_t_holdout": 0.62,
           "last_trades_holdout": 9, "holdout": {"ok": True, "t": 0.62}, "regime_pf": {"x": 1}}
    pairs = {"AUSDT|gen_a": rec}
    # la coppia NON e' validata: l'alleggerimento toglie i descrittivi, non la t
    slim = decode_pairs(op.slim_registry(pairs, []))["AUSDT|gen_a"]
    for c in CAMPI_T:
        assert slim[c] == rec[c], c
    assert "holdout" not in slim and "regime_pf" not in slim
    # e anche l'alleggerimento d'emergenza (tetto sforato) la tiene
    emerg = decode_pairs(op.slim_registry(pairs, ["AUSDT|gen_a"], max_bytes=10))["AUSDT|gen_a"]
    for c in CAMPI_T:
        assert emerg[c] == rec[c], c
    # nomi brevi nel documento, nomi lunghi a chi legge
    enc = encode_registry(pairs)
    assert '"t": 1.87' in enc and '"o": 9' in enc and "last_t" not in enc
    assert len(set(_BREVI.values())) == len(_BREVI)       # nessuna lettera doppia


def test_scrivi_voto_t_scrive_solo_i_quattro_campi():
    rec = {"pass_count": 2, "last_params": {"a": 1}}
    op.scrivi_voto_t(rec, 2.3456, 57, {"ok": True, "t": 0.123, "trades": 8, "pf": 2.0})
    # 3 decimali, come prima del lavoro B e come il file della passata
    assert rec == {"pass_count": 2, "last_params": {"a": 1}, "last_t": 2.346,
                   "last_trades": 57, "last_t_holdout": 0.123, "last_trades_holdout": 8}
    rec2 = {}
    op.scrivi_voto_t(rec2, None, None, {"ok": True})       # holdout senza t: niente zeri
    assert rec2 == {}


def test_una_t_sotto_2_resta_sotto_2_nel_registro():
    """Il rilievo del 30 set: a 2 decimali 1,995-1,999 diventava 2.0 e passava
    la soglia t >= 2 del report e di `statistica_t`."""
    from bot.core.registry import statistica_t
    for t in (1.995, 1.996, 1.997, 1.999):
        rec = {"pass_count": 3}
        op.scrivi_voto_t(rec, t, 40, {"t": t, "trades": 9})
        assert rec["last_t"] < 2.0 and rec["last_t_holdout"] < 2.0, t
        assert statistica_t({"A|gen_a": rec})["sopra_2"] == 0
        dopo = decode_pairs(encode_registry({"A|gen_a": rec}))["A|gen_a"]
        assert dopo["last_t"] == t


def test_l_holdout_nel_registro_senza_il_doppione_della_t():
    h = {"ok": True, "t": 0.617, "trades": 7, "pf": 1.4}
    assert op.holdout_per_registro(h) == {"ok": True, "trades": 7, "pf": 1.4}
    assert h["t"] == 0.617                                 # l'originale non si tocca
    assert op.holdout_per_registro(None) is None


def test_impronta_uscita():
    assert op.impronta_uscita({}) == "-/-/-"
    assert op.impronta_uscita({"scale_r_mults": [1, 2.0, 3], "sl_to_breakeven": True,
                               "profit_lock_keep": 0.75, "rsi": 30}) == "1,2,3/1/0.75"
    assert op.impronta_uscita({"sl_to_breakeven": False}) == "-/0/-"
    assert op.impronta_uscita(None) == "-/-/-"


def test_il_merge_della_discovery_scrive_la_t_anche_a_una_coppia_non_validata():
    from scripts.discover_strategies import merge_into_registry

    class FB:
        def __init__(self):
            self.docs = {}

        def get_doc(self, c, d):
            return self.docs.get((c, d), {})

        def set_doc(self, c, d, data):
            self.docs[(c, d)] = data

    fb = FB()
    fb.docs[("strategy_registry", "validated")] = {"pairs": encode_pairs({})}
    e = {"symbol": "A", "strategy": "gen_t", "params": {}, "oos_pf": 1.5,
         "oos_pnl_pct": 0.3, "oos_trades": 40, "oos_win_rate": 0.5, "passed": True,
         "holdout": {"ok": True, "t": 1.234, "trades": 7}, "data_end": 1e9, "t_stat": 2.31}
    merge_into_registry(fb, {"A|gen_t": e}, ["A|gen_t"], evaluated_symbols={"A"})
    rec = decode_pairs(fb.docs[("strategy_registry", "validated")]["pairs"])["A|gen_t"]
    assert rec["pass_count"] == 1                        # 1 conferma: alleggerita
    assert "holdout" not in rec                          # il descrittivo se ne va...
    assert (rec["last_t"], rec["last_trades"], rec["last_t_holdout"],
            rec["last_trades_holdout"]) == (2.31, 40, 1.234, 7)   # ...la t resta
    assert not any(c in rec for c in CAMPI_VAL)          # non e' validata: niente t fissata


class _FbMemoria:
    def __init__(self):
        self.docs = {("strategy_registry", "validated"): {"pairs": encode_pairs({})}}

    def get_doc(self, c, d):
        return self.docs.get((c, d), {})

    def set_doc(self, c, d, data):
        self.docs[(c, d)] = data


def test_la_t_si_fissa_alla_promozione_e_un_ripasso_non_la_cambia():
    """Il rilievo del 30 set: il report usava `last_t` solo se la coppia non
    era ripassata, e ripassare dipende dai giorni fuori campione. Ora la t della
    promozione e' fissata (`val_t` & C.) e un ripasso riscrive solo `last_t`."""
    from scripts.discover_strategies import merge_into_registry
    fb = _FbMemoria()
    lp = {"scale_r_mults": [1, 2, 3], "sl_to_breakeven": True, "profit_lock_keep": 0.75}
    e = {"symbol": "A", "strategy": "gen_t", "params": {}, "oos_pf": 1.5,
         "oos_pnl_pct": 0.3, "oos_trades": 40, "oos_win_rate": 0.5, "passed": True,
         "holdout": {"ok": True, "t": 1.234, "trades": 7}, "data_end": 1e9, "t_stat": 2.31,
         "conferme_retro": op.MIN_PASSES - 1, **lp}
    merge_into_registry(fb, {"A|gen_t": e}, ["A|gen_t"], evaluated_symbols={"A"})
    rec = decode_pairs(fb.docs[("strategy_registry", "validated")]["pairs"])["A|gen_t"]
    assert rec["pass_count"] >= op.MIN_PASSES and rec.get("validated_at")
    assert (rec["val_t"], rec["val_trades"], rec["val_t_holdout"],
            rec["val_trades_holdout"]) == (2.31, 40, 1.234, 7)
    assert rec["val_uscita"] == op.impronta_uscita(rec["last_params"]) == "1,2,3/1/0.75"
    assert rec["holdout"] == {"ok": True, "trades": 7}  # validata intera, senza la t doppia
    va = rec["validated_at"]
    # il giorno dopo ripassa con un'altra t: `last_t` cambia, la t fissata no
    e2 = {**e, "t_stat": 3.5, "holdout": {"ok": True, "t": 2.9, "trades": 8},
          "data_end": 1e9 + 86400, "conferme_retro": 0}
    merge_into_registry(fb, {"A|gen_t": e2}, ["A|gen_t"], evaluated_symbols={"A"})
    rec = decode_pairs(fb.docs[("strategy_registry", "validated")]["pairs"])["A|gen_t"]
    assert rec["last_t"] == 3.5 and rec["val_t"] == 2.31 and rec["validated_at"] == va
    assert rec["last_passed_at"] > 0
    v = pb.voto_t_coppia("A|gen_t", rec, {})
    assert v == {"t": 2.31, "n": 40, "t_holdout": 1.234, "n_holdout": 7, "fonte": "registro"}


def test_fissa_voto_t_toglie_la_t_di_una_vita_precedente():
    rec = {"val_t": 3.1, "val_trades": 90, "val_uscita": "-/-/-", "last_params": {}}
    op.fissa_voto_t(rec)                                  # oggi nessuna t: via anche la vecchia
    assert not any(c in rec for c in CAMPI_VAL)
    rec = {"last_t": 1.5, "last_trades": 33, "last_params": {"profit_lock_keep": 0.5}}
    op.fissa_voto_t(rec)
    assert rec["val_t"] == 1.5 and rec["val_trades"] == 33 and rec["val_uscita"] == "-/-/0.5"
    assert "val_t_holdout" not in rec


def test_l_holdout_calcola_la_t_senza_cambiare_il_verdetto():
    from backtesting.engine import StrategyStats, t_stat
    from backtesting.optimizer import WalkForwardOptimizer
    opt = WalkForwardOptimizer(n_windows=1)
    base = _ts(2026, 9, 1)
    candles = [SimpleNamespace(open_time=dt.datetime.fromtimestamp(base + i * 900, dt.timezone.utc))
               for i in range(400)]
    frame = pd.DataFrame({"x": range(400)})
    cut = 300
    trades = [SimpleNamespace(pnl_pct=p, entry_ts=base + (cut + i) * 900, is_win=p > 0,
                              trailing_verdict=None)
              for i, p in enumerate([0.02, -0.01, 0.015, 0.01, -0.005, 0.02, 0.01])]
    prima = [SimpleNamespace(pnl_pct=5.0, entry_ts=base, is_win=True, trailing_verdict=None)]
    opt.bt = SimpleNamespace(window=50, run_strategy=lambda *a, **k: StrategyStats(
        strategy="s", trades=prima + trades))
    h = opt._holdout_check(SimpleNamespace(name="s"), "A", candles, frame, cut)
    assert h["trades"] == 7 and h["ok"] is True
    assert math.isclose(h["t"], round(t_stat(trades), 3))  # solo i trade dell'holdout


# --------------------------------------------------------------------------- #
# 2. la passata una tantum                                                     #
# --------------------------------------------------------------------------- #
def test_taglio_alla_mezzanotte_del_giorno_della_validazione():
    t, o = tv.taglio_validazione({"validated_at": _ts(2026, 9, 26, 17, 40)})
    assert (t, o) == (_ts(2026, 9, 26), "validated_at")
    t, o = tv.taglio_validazione({})                    # senza data: dal 25 set, come il report
    assert (t, o) == (_ts(2026, 9, 25), "senza_data")
    t, o = tv.taglio_validazione({"validated_at": _ts(2026, 9, 20),
                                  "sessione_azzerata_at": _ts(2026, 9, 27)})
    assert t is None and o == "azzerata_senza_data"


def test_coppie_da_votare_filtri_e_ordine():
    ora = time.time()
    v = {"pass_count": 3, "last_seen_at": ora, "validated_at": ora - 86400}
    pairs = {"AUSDT|gen_a": dict(v), "AUSDT|gen_b": dict(v), "BUSDT|gen_c": dict(v),
             "CUSDT|breakout": dict(v), "DUSDT|gen_x": dict(v), "EUSDT|gen_h": dict(v),
             "FUSDT|gen_z": {**v, "validated_at": _ts(2026, 9, 20),
                             "sessione_azzerata_at": _ts(2026, 9, 27)},
             "GUSDT|gen_poche": {"pass_count": 1, "last_seen_at": ora}}
    specs = {"gen_a": {"id": "gen_a"}, "gen_b": {"id": "gen_b"}, "gen_c": {"id": "gen_c"},
             "gen_h": {"id": "gen_h", "timeframe": "1h"}, "gen_z": {"id": "gen_z"}}
    lavoro, saltate = tv.coppie_da_votare(pairs, specs, "15m", gia_fatte={"BUSDT|gen_c": {}})
    assert [s for s, _ in lavoro] == ["AUSDT"]
    assert [k for k, *_ in lavoro[0][1]] == ["AUSDT|gen_a", "AUSDT|gen_b"]
    assert saltate == {"gia_nel_file": 1, "base": 1, "senza_spec": 1, "altro_timeframe": 1,
                       "azzerata_senza_data": 1}
    lavoro, _ = tv.coppie_da_votare(pairs, specs, "15m", gia_fatte={"BUSDT|gen_c": {}}, rifai=True)
    assert {s for s, _ in lavoro} == {"AUSDT", "BUSDT"}


def test_coppie_da_votare_rifa_le_voci_che_non_valgono_piu_e_vota_le_uscite():
    ora = time.time()
    va = _ts(2026, 9, 26, 17)
    v = {"pass_count": 3, "last_seen_at": ora, "validated_at": va,
         "last_params": {"profit_lock_keep": 0.75}}
    pairs = {"AUSDT|gen_a": dict(v), "BUSDT|gen_b": dict(v), "CUSDT|gen_c": dict(v),
             # uscita dal registro (sostituita), record ancora presente
             "DUSDT|gen_d": {**v, "sostituita_da": "DUSDT|gen_e", "sostituita_at": ora - 3600}}
    specs = {k: {"id": k} for k in ("gen_a", "gen_b", "gen_c", "gen_d")}
    buona = {"dati_fino_a": "2026-09-26", "uscita": "-/-/0.75"}
    gia = {"AUSDT|gen_a": dict(buona),                               # vale: si salta
           "BUSDT|gen_b": {**buona, "uscita": "-/-/0.5"},             # config cambiata
           "CUSDT|gen_c": {**buona, "dati_fino_a": "2026-09-01"}}     # altra validazione
    rifatte = tv.Counter()
    lavoro, saltate = tv.coppie_da_votare(pairs, specs, "15m", gia_fatte=gia,
                                          uscite=["DUSDT|gen_d", "ZUSDT|gen_z"],
                                          rifatte=rifatte)
    chiavi = sorted(k for _s, lst in lavoro for k, *_ in lst)
    assert chiavi == ["BUSDT|gen_b", "CUSDT|gen_c", "DUSDT|gen_d"]  # Z: nessun record
    assert saltate == {"gia_nel_file": 1}
    assert rifatte == {"config_cambiata": 1, "altra_validazione": 1}


def test_le_uscite_da_votare_sono_quelle_rigiocabili_col_record():
    ora = time.time()
    v = {"pass_count": 3, "last_seen_at": ora, "validated_at": ora - 5 * 86400,
         "generated": True}
    pairs = {"AUSDT|gen_a": dict(v),
             "BUSDT|gen_b": {**v, "sostituita_da": "BUSDT|gen_c", "sostituita_at": ora - 3600},
             "CUSDT|breakout": {**v, "sostituita_da": "x", "sostituita_at": ora - 3600}}
    validate = tv.coppie_validate(pairs)
    assert tv._uscite_da_votare(pairs, validate) == ["BUSDT|gen_b"]   # base: non rigiocabile


class _OptFinto:
    """Solo cio' che `vota_coin` usa: holdout di H candele, finestre fisse,
    un motore che restituisce trade diversi a seconda della lunghezza dei dati."""
    H = 20

    def __init__(self):
        self.holdout_su = []
        self.finestre_su = []
        self.holdout_bars = self.H
        self.bt = SimpleNamespace(run_strategy=self._run, _prep_cache={}, _htf_cache={})

    def split_holdout(self, c):
        return c[:len(c) - self.H], len(c) - self.H

    def _windows(self, n):
        self.finestre_su.append(n)
        return [(0, 10, 10, 20), (10, 20, 20, 30)]

    def _run(self, g, sym, candles, frame=None, context_by_ts=None):
        from backtesting.engine import StrategyStats
        return StrategyStats(strategy="s", trades=[SimpleNamespace(pnl_pct=p) for p in
                                                   (0.02, -0.01, 0.015, 0.01)])

    def _holdout_check(self, g, sym, candles, frame, cut, context_by_ts=None):
        self.holdout_su.append((len(candles), len(frame), cut))
        return {"ok": True, "trades": 6, "t": 1.5}


def _candele(n, inizio):
    return [SimpleNamespace(open_time=dt.datetime.fromtimestamp(inizio + i * 86400, dt.timezone.utc))
            for i in range(n)]


def test_vota_coin_holdout_sui_dati_del_giorno_della_validazione(monkeypatch):
    monkeypatch.setattr(tv, "compute_indicator_frame", lambda c: pd.DataFrame({"i": range(len(c))}))
    inizio = _ts(2026, 6, 1)
    candles = _candele(122, inizio)            # una candela al giorno fino al 30 set
    opt = _OptFinto()
    W = {"opt": opt, "args": SimpleNamespace(interval="15m"), "min_history": 30, "btc_ctx": None}
    t1, t2 = _ts(2026, 9, 26), _ts(2026, 9, 20)
    lista = [("AUSDT|gen_a", {"id": "gen_a"}, {"profit_lock_keep": 0.75}, t1),
             ("AUSDT|gen_b", {"id": "gen_b"}, {}, t2),
             ("AUSDT|gen_c", {"id": "gen_c"}, {}, t1)]
    righe = tv.vota_coin(W, "AUSDT", lista, candles)
    assert [r["stato"] for r in righe] == ["ok", "ok", "ok"]
    # walk-forward E holdout sui dati tagliati al giorno della validazione: due
    # tagli (26 e 20 set), le candele fino al giorno prima del taglio compreso.
    # 30 set 2026, revisione del lavoro B: prima il walk-forward girava sui dati
    # di oggi (corpo di 102 candele per tutte) e la sua ultima finestra entrava
    # nell'holdout del giorno della validazione
    n26 = sum(1 for c in candles if c.open_time.timestamp() < t1)
    n20 = sum(1 for c in candles if c.open_time.timestamp() < t2)
    assert sorted(opt.finestre_su) == sorted([n20 - 20, n26 - 20, n26 - 20])
    assert sorted(opt.holdout_su) == sorted([(n20, n20, n20 - 20), (n26, n26, n26 - 20),
                                             (n26, n26, n26 - 20)])
    a = righe[0]
    assert a["t_holdout"] == 1.5 and a["n_holdout"] == 6 and a["n"] == 8
    assert a["dati_fino_a"] == "2026-09-26" and "wf_troncato" not in a
    assert "keep0.75" in a["config"] and a["uscita"] == "-/-/0.75"


def test_la_t_su_troppi_pochi_trade_resta_vuota(monkeypatch):
    """Sotto 2 trade (walk-forward) o sotto il minimo del gate (holdout, 5) la t
    non e' una misura: `t_stat` da' 0.0, o numeri enormi con 2-4 trade."""
    monkeypatch.setattr(tv, "compute_indicator_frame", lambda c: pd.DataFrame({"i": range(len(c))}))
    candles = _candele(122, _ts(2026, 6, 1))
    opt = _OptFinto()
    opt._holdout_check = lambda *a, **k: {"ok": False, "trades": 2, "t": 11.0}
    from backtesting.engine import StrategyStats
    opt.bt.run_strategy = lambda *a, **k: StrategyStats(strategy="s", trades=[])
    W = {"opt": opt, "args": SimpleNamespace(interval="15m"), "min_history": 30, "btc_ctx": None}
    r = tv.vota_coin(W, "AUSDT", [("AUSDT|gen_v", {"id": "gen_v"}, {}, _ts(2026, 9, 20))],
                     candles)[0]
    assert r["stato"] == "ok"
    assert r["t"] is None and r["n"] == 0
    assert r["t_holdout"] is None and r["n_holdout"] == 2


def test_unisci_voti_solo_le_votate_e_non_riscrive_senza_rifai():
    esistenti = {"A|gen_a": {"t": 1.0, "n": 50}}
    righe = [{"key": "A|gen_a", "stato": "ok", "t": 9.0, "n": 1},
             {"key": "B|gen_b", "stato": "ok", "t": 2.5, "n": 80, "t_holdout": 0.3,
              "n_holdout": 7, "dati_fino_a": "2026-09-26"},
             {"key": "C|gen_c", "stato": "tempo"}, {"key": "D|gen_d", "stato": "errore"}]
    voti, nuove = tv.unisci_voti(esistenti, righe)
    assert nuove == 1 and voti["A|gen_a"] == {"t": 1.0, "n": 50}
    assert set(voti) == {"A|gen_a", "B|gen_b"} and voti["B|gen_b"]["t_holdout"] == 0.3
    voti, nuove = tv.unisci_voti(esistenti, righe, rifai=True)
    assert nuove == 2 and voti["A|gen_a"]["t"] == 9.0
    # una riga calcolata con un'altra configurazione (la passata l'ha rivotata
    # perche' la vecchia non valeva piu') sostituisce la voce anche senza --rifai
    vecchie = {"A|gen_a": {"t": 1.0, "uscita": "-/-/0.5", "dati_fino_a": "2026-09-26"}}
    nuova = [{"key": "A|gen_a", "stato": "ok", "t": 2.2, "uscita": "-/-/0.75",
              "dati_fino_a": "2026-09-26"}]
    voti, nuove = tv.unisci_voti(vecchie, nuova)
    assert nuove == 1 and voti["A|gen_a"]["t"] == 2.2
    voti, nuove = tv.unisci_voti(voti, nuova)           # rifatta una volta, poi stabile
    assert nuove == 0


def test_lucchetto_esclusivo_e_lucchetto_vecchio(tmp_path):
    lock = str(tmp_path / "voto_t" / "in_corso.lock")
    assert tv.prendi_lucchetto(lock) == os.getpid()
    assert open(lock).read() == str(os.getpid())
    # un secondo tentativo (anche dallo stesso processo, un'altra apertura) no
    assert tv.prendi_lucchetto(lock) is None
    tv.lascia_lucchetto(lock)
    assert tv.prendi_lucchetto(lock) == os.getpid()      # libero di nuovo
    tv.lascia_lucchetto(lock)
    # un file rimasto da una passata morta (pid qualunque dentro, anche vuoto)
    # non e' un lucchetto: il kernel l'ha gia' tolto
    for contenuto in ("999999999", ""):
        with open(lock, "w") as f:
            f.write(contenuto)
        assert tv.prendi_lucchetto(lock) == os.getpid()
        tv.lascia_lucchetto(lock)
    tv.lascia_lucchetto(lock)                     # non tenuto: non fa niente


def _tieni_lucchetto(lock, preso, via):
    """Figlio: prende il lucchetto, lo dice, aspetta il via, esce senza lasciarlo."""
    preso.put(tv.prendi_lucchetto(lock))
    via.wait(10)


def test_lucchetto_tenuto_da_un_altro_processo_e_tolto_dal_kernel_alla_sua_morte(tmp_path):
    ctx = multiprocessing.get_context("fork")
    lock = str(tmp_path / "in_corso.lock")
    preso, via = ctx.Queue(), ctx.Event()
    figlio = ctx.Process(target=_tieni_lucchetto, args=(lock, preso, via))
    figlio.start()
    try:
        assert preso.get(timeout=10) == figlio.pid
        assert tv.prendi_lucchetto(lock) is None          # vivo: nessun'altra passata
    finally:
        via.set()
        figlio.join(10)
    # morto senza lasciarlo: il kernel l'ha tolto, nessun lucchetto orfano
    assert tv.prendi_lucchetto(lock) == os.getpid()
    tv.lascia_lucchetto(lock)


def _gara(lock, via, esito):
    via.wait(10)
    if tv.prendi_lucchetto(lock):
        esito.put(1)
        time.sleep(0.2)
        tv.lascia_lucchetto(lock)
    else:
        esito.put(0)


def test_due_avvii_nello_stesso_istante_uno_solo_vince(tmp_path):
    """Il rilievo del 30 set: col vecchio lucchetto (O_EXCL + pid scritto dopo)
    in 238 casi su 300 le due passate lo tenevano insieme."""
    ctx = multiprocessing.get_context("fork")
    for i in range(8):
        lock = str(tmp_path / f"gara{i}.lock")
        via, esito = ctx.Event(), ctx.Queue()
        figli = [ctx.Process(target=_gara, args=(lock, via, esito)) for _ in range(2)]
        for f in figli:
            f.start()
        via.set()
        vinti = sum(esito.get(timeout=10) for _ in figli)
        for f in figli:
            f.join(10)
        assert vinti == 1, i


def test_scrittura_atomica(tmp_path):
    p = str(tmp_path / "v" / "validate.json")
    tv.scrivi_atomico(p, {"coppie": {"A|gen_a": {"t": 2.0}}})
    tv.scrivi_atomico(p, {"coppie": {"A|gen_a": {"t": 3.0}}})
    assert json.load(open(p))["coppie"]["A|gen_a"]["t"] == 3.0
    assert os.listdir(tmp_path / "v") == ["validate.json"]      # nessun temporaneo rimasto


class _FbSoloLettura:
    def __init__(self, docs):
        self.docs = docs
        self.letti = []
        self.scritti = []
        self.is_live = True

    def get_doc(self, c, d, *a, **k):
        self.letti.append((c, d))
        return copy.deepcopy(self.docs.get((c, d)))

    def set_doc(self, *a, **k):
        self.scritti.append(a)

    def __getattr__(self, nome):                 # qualunque altra scrittura: registrata
        return lambda *a, **k: self.scritti.append((nome, a))


def test_la_passata_scrive_solo_la_t_nel_suo_file_e_non_tocca_il_registro(tmp_path, monkeypatch, capsys):
    ora = time.time()
    rec = {"pass_count": 3, "fail_count": 1, "last_seen_at": ora, "validated_at": ora - 86400,
           "declassata": True, "bocciata_notti": 2, "last_params": {"profit_lock_keep": 0.75},
           "generated": True}
    pairs = {"AUSDT|gen_a": rec, "BUSDT|gen_b": dict(rec), "CUSDT|gen_c": dict(rec)}
    reg = {"pairs": encode_registry(pairs), "validated": sorted(pairs), "updated_at": 123}
    specs = {"gen_a": {"id": "gen_a"}, "gen_b": {"id": "gen_b"}, "gen_c": {"id": "gen_c"}}
    fb = _FbSoloLettura({("strategy_registry", "validated"): reg,
                         ("discovered_strategies", "specs"): {"specs": json.dumps(specs)}})
    prima = copy.deepcopy(fb.docs)
    monkeypatch.setattr(tv, "get_firebase", lambda: fb)
    file_voti = str(tmp_path / "voto_t" / "validate.json")
    monkeypatch.setattr(pb, "FILE_VOTI_T", file_voti)
    monkeypatch.setattr(tv, "FILE_LOCK", str(tmp_path / "voto_t" / "in_corso.lock"))
    # una voce gia' nel file (di una passata precedente): non si rifa'
    tv.scrivi_atomico(file_voti, {"coppie": {"CUSDT|gen_c": {"t": 0.5, "n": 30}}})
    monkeypatch.setattr(tv, "_init", lambda *a: None)
    monkeypatch.setattr(tv, "giro_in_corso", lambda: [])
    fatte = []

    def _coin(item):
        sym, lista = item
        fatte.extend(k for k, *_ in lista)
        return [{"key": k, "stato": "ok", "t": 2.4, "n": 90, "t_holdout": 1.1, "n_holdout": 8,
                 "dati_fino_a": "2026-09-29", "config": "x", "uscita": "-/-/0.75",
                 "calcolata_at": "oggi"} if k.startswith("A") else {"key": k, "stato": "tempo"}
                for k, *_ in lista]
    monkeypatch.setattr(tv, "_una_coin", _coin)
    assert tv.main(["--workers", "1"]) == 0
    out = capsys.readouterr().out
    # nessuna scrittura Firebase, documenti identici, due sole letture
    assert fb.scritti == [] and fb.docs == prima
    assert sorted(fb.letti) == [("discovered_strategies", "specs"), ("strategy_registry", "validated")]
    assert sorted(fatte) == ["AUSDT|gen_a", "BUSDT|gen_b"]
    voti = json.load(open(file_voti))["coppie"]
    assert set(voti) == {"AUSDT|gen_a", "CUSDT|gen_c"}               # B non votata per tempo
    assert voti["CUSDT|gen_c"] == {"t": 0.5, "n": 30}                  # la vecchia resta
    assert set(voti["AUSDT|gen_a"]) == {"t", "n", "t_holdout", "n_holdout", "dati_fino_a",
                                        "config", "uscita", "calcolata_at"}
    assert "0 scritture" in out and "NON sono stati toccati" in out
    assert "1 coppie NON votate per tempo" in out
    assert tv.prendi_lucchetto(tv.FILE_LOCK) == os.getpid()           # lucchetto lasciato
    tv.lascia_lucchetto(tv.FILE_LOCK)


def test_la_passata_non_parte_se_un_altra_e_in_corso(tmp_path, monkeypatch, capsys):
    lock = str(tmp_path / "in_corso.lock")
    assert tv.prendi_lucchetto(lock) == os.getpid()      # «un'altra passata» lo tiene
    monkeypatch.setattr(tv, "FILE_LOCK", lock)
    monkeypatch.setattr(tv, "get_firebase", lambda: (_ for _ in ()).throw(AssertionError("letto")))
    try:
        assert tv.main([]) == 0
        assert "gia' in corso" in capsys.readouterr().out
        assert tv.prendi_lucchetto(lock) is None         # ancora tenuto da chi l'aveva
    finally:
        tv.lascia_lucchetto(lock)


def test_su_file_col_lucchetto_tenuto_non_tocca_referto_ne_pid(tmp_path, monkeypatch, capsys):
    """Il rilievo del 30 set: un secondo avvio `--su-file` svuotava il referto
    della passata in corso e ci metteva il suo pid (poi `voto-t-esito` diceva
    «finito» a passata ancora in corso)."""
    for nome, valore in (("DIR_VOTI", str(tmp_path)),
                         ("FILE_ESITO", str(tmp_path / "ultimo.txt")),
                         ("FILE_PID", str(tmp_path / "ultimo.pid")),
                         ("FILE_LOCK", str(tmp_path / "in_corso.lock"))):
        monkeypatch.setattr(tv, nome, valore)
    (tmp_path / "ultimo.txt").write_text("referto della passata in corso\n" * 20)
    (tmp_path / "ultimo.pid").write_text("4242")
    prima = (tmp_path / "ultimo.txt").read_bytes()
    assert tv.prendi_lucchetto(tv.FILE_LOCK) == os.getpid()
    try:
        assert tv.su_file(SimpleNamespace(budget=0)) == 0
    finally:
        tv.lascia_lucchetto(tv.FILE_LOCK)
    assert (tmp_path / "ultimo.txt").read_bytes() == prima
    assert (tmp_path / "ultimo.pid").read_text() == "4242"
    assert "gia' in corso" in capsys.readouterr().out


def test_giro_in_corso_legge_proc(tmp_path):
    for pid, cmd in (("101", b"python\0-m\0scripts.discover_strategies\0--top\0200"),
                     ("102", b"python\0-m\0scripts.portafoglio_backtest"),
                     ("103", b"python\0-m\0scripts.optimize"), ("self", b"x")):
        (tmp_path / pid).mkdir()
        (tmp_path / pid / "cmdline").write_bytes(cmd)
    assert tv.giro_in_corso(str(tmp_path)) == [101, 103]
    assert tv.giro_in_corso(str(tmp_path / "manca")) == []


def _salva_in(path):
    def salva(righe):
        voti, n = tv.unisci_voti(pb.voti_t_da_file(path), righe)
        if n:
            tv.scrivi_atomico(path, {"coppie": voti})
    return salva


def test_un_errore_su_una_coin_non_butta_le_coin_gia_votate(tmp_path, monkeypatch):
    """Il rilievo del 30 set: un'eccezione fuori dai controlli per coppia (qui
    negli indicatori della seconda coin) usciva da `main` e il file non si
    scriveva: la prima coin, gia' votata, era persa."""
    candles = _candele(122, _ts(2026, 6, 1))
    opt = _OptFinto()
    stato = {"opt": opt, "args": SimpleNamespace(interval="15m", start="x", source="auto"),
             "end": "2026-09-30", "min_history": 30, "btc_ctx": None}
    monkeypatch.setattr(tv.d, "_W", stato, raising=False)
    monkeypatch.setattr(tv, "_init", lambda *a: None)
    monkeypatch.setattr(tv, "load_candles", lambda *a, **k: candles)
    monkeypatch.setattr(tv, "looks_delisted", lambda *a, **k: False)

    def frame(c):
        if frame.chiamate:
            raise ValueError("indicatori rotti")
        frame.chiamate += 1
        return pd.DataFrame({"i": range(len(c))})
    frame.chiamate = 0
    monkeypatch.setattr(tv, "compute_indicator_frame", frame)
    tv._S.clear()
    lavoro = [("AUSDT", [("AUSDT|gen_a", {"id": "gen_a"}, {}, _ts(2026, 9, 20))]),
              ("BUSDT", [("BUSDT|gen_b", {"id": "gen_b"}, {}, _ts(2026, 9, 20))])]
    file_voti = str(tmp_path / "validate.json")
    righe, interrotta = tv.esegui_e_salva(lavoro, 1, (None, "x", 0.0), _salva_in(file_voti))
    assert interrotta is None
    assert {r["key"]: r["stato"] for r in righe} == {"AUSDT|gen_a": "ok", "BUSDT|gen_b": "errore"}
    assert "indicatori rotti" in righe[1]["errore"]
    assert set(pb.voti_t_da_file(file_voti)) == {"AUSDT|gen_a"}


def _coin_o_muori(item):
    """Per il test del worker ucciso: la coin «KILL» manda SIGKILL al suo worker
    (come l'OOM del kernel); le altre rispondono subito."""
    sym, lista = item
    if sym == "KILL":
        time.sleep(1.0)
        os.kill(os.getpid(), signal.SIGKILL)
    return [{"key": k, "stato": "ok", "t": 2.0, "n": 50} for k, *_ in lista]


def test_un_worker_ucciso_lascia_nel_file_le_coin_gia_finite(tmp_path, monkeypatch):
    """Il rilievo del 30 set: con `parallel_map` un worker ucciso dal kernel
    (BrokenProcessPool) faceva perdere anche le coin gia' finite."""
    monkeypatch.setattr(tv, "_una_coin", _coin_o_muori)
    monkeypatch.setattr(tv, "_init", lambda *a: None)
    lavoro = [("AUSDT", [("AUSDT|gen_a",)]), ("BUSDT", [("BUSDT|gen_b",)]),
              ("KILL", [("KILL|gen_k",)])]
    file_voti = str(tmp_path / "validate.json")
    righe, interrotta = tv.esegui_e_salva(lavoro, 2, (None, "x", 0.0), _salva_in(file_voti))
    assert interrotta and "worker" in interrotta
    assert {r["key"]: r["stato"] for r in righe}["KILL|gen_k"] == "interrotta"
    assert set(pb.voti_t_da_file(file_voti)) == {"AUSDT|gen_a", "BUSDT|gen_b"}


def test_istante_systemd():
    assert tv.istante_systemd("Wed 2026-09-30 15:00:00 UTC") == _ts(2026, 9, 30, 15)
    assert tv.istante_systemd("@1759244400") == 1759244400.0
    assert tv.istante_systemd("1759244400000000") == 1759244400.0
    for vuoto in ("", "n/a", None, "0", "boh", "Wed 2026-99-99 25:61:00 UTC"):
        assert tv.istante_systemd(vuoto) is None


def test_gate_in_arrivo(monkeypatch):
    monkeypatch.setattr(tv, "giro_in_corso", lambda: [])
    assert tv.gate_in_arrivo(600) is None
    monkeypatch.setattr(tv, "secondi_al_prossimo_giro", lambda ora=None: 30 * 60.0)
    assert tv.gate_in_arrivo(10 * 60) is None                 # fra 30 minuti: si lavora
    assert "fra 30 minuti" in tv.gate_in_arrivo(40 * 60)      # ma non si parte
    monkeypatch.setattr(tv, "secondi_al_prossimo_giro", lambda ora=None: -5.0)
    assert "fra 0 minuti" in tv.gate_in_arrivo(60)
    monkeypatch.setattr(tv, "servizio_gate_attivo", lambda: True)
    assert "attivo" in tv.gate_in_arrivo(60)                  # fra i due ExecStart
    monkeypatch.setattr(tv, "giro_in_corso", lambda: [7])
    assert "pid 7" in tv.gate_in_arrivo(60)


def test_il_gate_che_parte_a_passata_avviata_la_ferma_prima_della_coin(monkeypatch):
    """Il rilievo del 30 set: il gate si guardava solo alla partenza. Ora ogni
    coin ricontrolla: se il giro parte (o manca poco), le coin rimaste non si
    votano (righe «giro») e i worker si liberano."""
    monkeypatch.setattr(tv.d, "_W", {"args": SimpleNamespace(interval="15m"), "end": "x"},
                        raising=False)
    tv._S.clear()
    lista = [("AUSDT|gen_a", {}, {}, 0.0), ("AUSDT|gen_b", {}, {}, 0.0)]
    monkeypatch.setattr(tv, "giro_in_corso", lambda: [4242])
    monkeypatch.setattr(tv, "load_candles", lambda *a, **k: (_ for _ in ()).throw(
        AssertionError("con il gate in corso non si carica niente")))
    righe = tv._una_coin(("AUSDT", lista))
    assert [r["stato"] for r in righe] == ["giro", "giro"]
    assert "pid 4242" in righe[0]["errore"]


def test_col_giro_in_corso_nel_canale_esce_in_sfondo_aspetta(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(tv, "FILE_LOCK", str(tmp_path / "in_corso.lock"))
    monkeypatch.setattr(tv, "giro_in_corso", lambda: [4242])
    monkeypatch.setattr(tv, "get_firebase", lambda: (_ for _ in ()).throw(AssertionError("letto")))
    assert tv.main([]) == 0                                     # canale ops: budget 720
    assert "giro del gate e' in corso (pid 4242)" in capsys.readouterr().out
    assert tv.prendi_lucchetto(tv.FILE_LOCK) == os.getpid()    # lucchetto lasciato
    tv.lascia_lucchetto(tv.FILE_LOCK)
    # il prossimo giro fra 15 minuti: nel canale non si parte nemmeno
    monkeypatch.setattr(tv, "giro_in_corso", lambda: [])
    monkeypatch.setattr(tv, "secondi_al_prossimo_giro", lambda ora=None: 15 * 60.0)
    assert tv.main([]) == 0
    assert "prossimo giro del gate parte fra 15 minuti" in capsys.readouterr().out
    monkeypatch.setattr(tv, "secondi_al_prossimo_giro", lambda ora=None: None)
    # in sfondo: aspetta finche' il giro finisce, poi parte
    giri = iter([[4242], [4242], []])
    monkeypatch.setattr(tv, "giro_in_corso", lambda: next(giri))
    dormite = []
    monkeypatch.setattr(tv.time, "sleep", lambda s: dormite.append(s))
    partita = []
    monkeypatch.setattr(tv, "_passata", lambda args: partita.append(1) or 0)
    assert tv.main(["--budget", "0"]) == 0
    assert dormite == [tv.ATTESA_PASSO_S] * 2 and partita == [1]
    assert "aspetto che finisca" in capsys.readouterr().out


def test_su_file_senza_firebase_esce_0_ed_esito_senza_referto(tmp_path, monkeypatch, capsys):
    monkeypatch.setenv("TRADING_BOT_TEST_MODE", "1")
    assert tv.main(["--su-file", "--budget", "0"]) == 0
    assert "senza Firebase vivo" in capsys.readouterr().out
    monkeypatch.setattr(tv, "FILE_ESITO", str(tmp_path / "ultimo.txt"))
    assert tv.main(["--esito"]) == 0
    assert "nessun referto" in capsys.readouterr().out


def test_la_riga_della_lista_bianca():
    from scripts.ops_agent import parse_allowlist
    with open(os.path.join(ROOT, "ops", "allowlist.example"), encoding="utf-8") as f:
        voci = parse_allowlist(f.read())
    assert voci["voto-t-completo"]["cmd"] == (
        "systemd-run --no-block --collect --unit=voto-t-completo "
        "--nice=15 --property=IOSchedulingClass=idle "
        "--property=WorkingDirectory=/root/agentic_trading_system "
        "/root/agentic_trading_system/.venv/bin/python -m scripts.t_validate --su-file --budget 0")
    assert voci["voto-t-esito"]["cmd"] == ".venv/bin/python -m scripts.t_validate --esito"
    for k in ("voto-t-completo", "voto-t-esito"):
        assert voci[k]["args"] is False
        assert "|" not in voci[k]["cmd"] and ">" not in voci[k]["cmd"] and "&&" not in voci[k]["cmd"]
    with open(os.path.join(ROOT, ".gitignore"), encoding="utf-8") as f:
        assert "data/voto_t/" in f.read()
    assert pb.FILE_VOTI_T.endswith(os.path.join("data", "voto_t", "validate.json"))
    assert tv.FILE_ESITO.endswith(os.path.join("data", "voto_t", "ultimo.txt"))


# --------------------------------------------------------------------------- #
# 3. il FUORI CAMPIONE diviso per t                                            #
# --------------------------------------------------------------------------- #
PAV = _ts(2026, 9, 16)
V = _ts(2026, 9, 26, 12)


def _m(sym, strat, entry, r):
    return {"symbol": sym, "strategy": strat, "direction": "long", "entry_ts": entry,
            "bars_held": 4, "pnl_pct": 0.01 * r, "stop_pct": 0.01, "mfe_r": 1.0,
            "scale_r_mults": None, "fine_dati": False}


def _p(sym, strat, entry, r):
    return {"symbol": sym, "strategy": strat, "direction": "long",
            "entry_time": dt.datetime.fromtimestamp(entry, dt.timezone.utc).isoformat(),
            "exit_ts": entry + 3600, "entry_price": 100.0, "orig_stop": 99.0, "size": 1.0,
            "pnl": r, "mfe_r": 0.5, "exit_reason": "stop_loss"}


def _caso_t():
    """Tre coppie: A (t alta dal file) guadagna, B (t bassa dal file) perde, C ha
    la t nel registro ma scritta DOPO la validazione (ripassata): senza t."""
    pairs = {"A|ga": {"validated_at": V}, "B|gb": {"validated_at": V},
             "C|gc": {"validated_at": V, "last_t": 5.0, "last_trades": 400,
                      "last_passed_at": V + 3 * 86400}}
    voti = {"A|ga": {"t": 3.1, "n": 100, "t_holdout": 2.2, "n_holdout": 9},
            "B|gb": {"t": 1.2, "n": 400, "t_holdout": 0.4, "n_holdout": 12}}
    motore, paper = [], []
    for g in range(6):
        for h in range(3):
            e = V + (g + 1) * 86400 + h * 7200
            motore.append(_m("A", "ga", e, 1.0 if h else -0.5))
            motore.append(_m("B", "gb", e + 900, -1.0 if h else 0.5))
            motore.append(_m("C", "gc", e + 1800, 0.2))
        paper.append(_p("A", "ga", V + (g + 1) * 86400 + 60, 0.4))
        paper.append(_p("B", "gb", V + (g + 1) * 86400 + 960, -0.6))
    return pairs, voti, motore, paper


def test_voto_t_dal_file_prima_poi_dalla_t_fissata_alla_promozione():
    assert pb.voto_t_coppia("A|ga", {}, {"A|ga": {"t": 2.5, "n": 40}})["fonte"] == "passata"
    ok = {"validated_at": V, "last_params": {}, "val_t": 1.4, "val_trades": 60,
          "val_t_holdout": 0.2, "val_trades_holdout": 6, "val_uscita": "-/-/-",
          "last_t": 3.3, "last_passed_at": V + 5 * 86400}
    v = pb.voto_t_coppia("X|gx", ok, {})
    # la t fissata alla promozione, anche se la coppia e' ripassata dopo (il
    # ripasso riscrive solo `last_t`): chi ripassa non esce piu' dai gruppi
    assert v == {"t": 1.4, "n": 60, "t_holdout": 0.2, "n_holdout": 6, "fonte": "registro"}
    # `last_t` da solo (scritto a ogni ripasso) non vale piu'
    assert pb.voto_t_coppia("X|gx", {"validated_at": V, "last_t": 1.4,
                                     "last_passed_at": V}, {}) is None
    assert pb.voto_t_coppia("X|gx", {"validated_at": V}, {}) is None
    # la configurazione d'uscita di oggi non e' quella della t: senza t
    cambiata = {**ok, "last_params": {"profit_lock_keep": 0.5}}
    assert pb.voto_t_con_motivo("X|gx", cambiata, {}) == (None, "config_cambiata")


def test_la_voce_del_file_vale_solo_per_la_stessa_validazione_e_configurazione():
    rec = {"validated_at": _ts(2026, 10, 27, 3), "last_params": {"profit_lock_keep": 0.75},
           "val_t": 0.7, "val_trades": 50, "val_uscita": "-/-/0.75"}
    voce = {"t": 3.1, "n": 90, "dati_fino_a": "2026-10-27", "uscita": "-/-/0.75"}
    assert pb.voto_t_coppia("Q|g", rec, {"Q|g": voce})["t"] == 3.1
    # un'altra vita: la voce e' del 26 set, la coppia e' stata validata di nuovo
    vecchia = {**voce, "dati_fino_a": "2026-09-26"}
    v, da = pb.voto_t_con_motivo("Q|g", rec, {"Q|g": vecchia})
    assert (v["t"], da) == (0.7, "registro")               # la t della vita di oggi
    assert pb.voto_t_con_motivo("Q|g", {k: x for k, x in rec.items() if k != "val_t"
                                        and k != "val_uscita"},
                                {"Q|g": vecchia}) == (None, "altra_validazione")
    # un'altra configurazione d'uscita: la voce non vale
    altra = {**voce, "uscita": "-/-/0.5"}
    assert pb.voce_scaduta(altra, rec) == "config_cambiata"
    # coppia uscita e cancellata dal registro: la voce vale com'e'
    assert pb.voto_t_coppia("Q|g", None, {"Q|g": vecchia})["t"] == 3.1


def test_divisione_per_t_su_dati_finti():
    pairs, voti, motore, paper = _caso_t()
    fc = pb.fuori_campione(motore, paper, pairs, list(pairs), PAV, voti=voti)
    vt = fc["voto_t"]
    wf = vt["walk_forward"]
    assert wf["alta"]["n"] == 18 and wf["bassa"]["n"] == 18
    assert math.isclose(wf["alta"]["r_medio"], 0.5) and math.isclose(wf["bassa"]["r_medio"], -0.5)
    assert math.isclose(wf["differenza"], 1.0)
    assert wf["errore_differenza"] is not None and wf["alta"]["errore_regola"] is not None
    assert wf["paper_alta"] == {"n": 6, "r_medio": 0.4}
    assert math.isclose(wf["paper_bassa"]["r_medio"], -0.6)
    assert vt["holdout"]["alta"]["n"] == 18 and vt["holdout"]["bassa"]["n"] == 18
    # t/radice(n): A 3.1/10 = 0.31, B 1.2/20 = 0.06; mediana 0.185
    q = vt["t_su_radice_n"]
    assert math.isclose(q["mediana"], (0.31 + 0.06) / 2)
    assert q["alta"]["n"] == 18 and math.isclose(q["alta"]["r_medio"], 0.5)
    # C: nel registro solo `last_t` (riscritto a ogni ripasso) -> senza t
    assert vt["senza_t_segnali"] == 18 and vt["senza_t_coppie"] == 1
    assert vt["senza_t_uscite"] == 0
    assert vt["da_passata"] == 2 and vt["da_registro"] == 0
    assert wf["fuori"] == 18 and wf["condivisi"] == 0
    assert wf["alta"]["trade_mediani"] == 100 and wf["bassa"]["trade_mediani"] == 400
    assert vt["holdout"]["alta"]["trade_mediani"] == 9
    # le regole di ottobre non cambiano: stesso motore e stesso paper di prima
    senza = pb.fuori_campione(motore, paper, pairs, list(pairs), PAV)
    assert fc["motore"] == senza["motore"] and fc["lettura"] == senza["lettura"]


def test_la_regola_prima_dei_numeri_e_il_mezzo_kb(capsys):
    pairs, voti, motore, paper = _caso_t()
    fc = pb.fuori_campione(motore, paper, pairs, list(pairs), PAV, voti=voti)
    righe = pb.righe_voto_t(fc["voto_t"])
    testo = "\n".join(righe)
    assert righe[0] == f"  H1 (regola del 30 set): {pb.REGOLA_H1}."
    assert pb.REGOLA_H1 == ("se le coppie a t bassa perdono dopo la validazione e quelle a t "
                            "alta guadagnano, oltre il margine, allora H1-soglia sull'holdout "
                            "diventa la prossima proposta; se no, H1 si chiude con questo numero")
    assert testo.index("H1-soglia") < testo.index("t del gate 2 o piu'")
    # la t spiegata, e detto che nessuna riga decide finche' la regola non lo scrive
    assert "guadagno medio diviso per quanto oscilla" in testo
    assert "Decide solo la riga dell'ultimo esame" in testo
    assert "REGOLA H1 DECISA" in testo and "soglia 1,5" in testo
    assert "t dell'ultimo esame (45 giorni) 1.5 o piu'" in testo and "(DECIDE)" in testo
    assert "H1: " in testo
    assert "t divisa per la radice dei trade, 0.18 o piu'" in testo
    assert "(descrive, non decide)" in testo
    # gruppi in parole e in segnali, margine del gruppo e della differenza
    assert "18 segnali +0.50R ±0.34 · sotto 2: 18 segnali -0.50R ±0.34" in testo
    assert "differenza +1.00R ±" in testo and "paper 6 +0.40R e 6 -0.60R" in testo
    assert "trade mediani 100 e 400" in testo
    assert "senza t 18 segnali (1 coppia, uscite dal registro 0)" in testo
    assert "|" not in testo and "n.d.R" not in testo
    # ~1,1 KB: tutto l'output del `portafoglio` resta sotto i 20.000 caratteri
    # che l'agente ops conserva interi (ops 0373: 14.625 byte)
    assert len(testo.encode("utf-8")) <= 1700, len(testo.encode("utf-8"))  # +~400: regola H1 decisa (30 set sera)
    # con la sezione intera: le righe stanno fra la sopravvivenza e la Lettura
    pb.stampa_fuori_campione(fc, "2026-09-16", 0, None)
    out = capsys.readouterr().out
    assert out.index("tutte le coppie operate") < out.index("H1 (regola") < out.index("Lettura:")
    # senza nessun voto: la regola e una riga sola
    vuoto = pb.righe_voto_t(pb.fuori_campione(motore, paper, pairs, list(pairs), PAV)["voto_t"])
    assert len(vuoto) == 3 and "REGOLA H1 DECISA" in vuoto[1] and "passata una tantum" in vuoto[2]


def test_divisione_per_t_nel_main_senza_letture_in_piu(tmp_path, monkeypatch, capsys):
    """Il main legge il file locale della passata: nessuna lettura Firestore in
    piu' (registro, spec, paper finto e diario, una volta ciascuno) e il
    riepilogo pubblicato resta senza liste annidate."""
    from tests import test_regole_ottobre as tro
    ora = time.time()
    oggi = dt.datetime.fromtimestamp(ora, dt.timezone.utc).date()
    monkeypatch.setattr(pb, "PAPER_START", (oggi - dt.timedelta(days=10)).isoformat())
    v = ora - 6 * 86400
    pairs = {"AAAUSDT|gen_a": {"pass_count": 5, "last_seen_at": ora, "validated_at": v},
             "BBBUSDT|gen_b": {"pass_count": 5, "last_seen_at": ora, "validated_at": v}}
    fb = tro._FbFinto({("strategy_registry", "validated"): {"pairs": pairs},
                       ("discovered_strategies", "specs"): {"specs": {}},
                       ("gate_history", "lifecycle"): {"events": []}})
    monkeypatch.setattr(pb, "get_firebase", lambda: fb)
    monkeypatch.setattr(pb, "WalkForwardOptimizer", lambda **kw: SimpleNamespace(bt=None))

    def _trades(sym, strategie, specs_, args, inizio_ts, bt):
        return [_m(sym, s, ora - g * 86400 - (h * 3600), 1.0 if sym == "AAAUSDT" else -1.0)
                for s, _ in strategie for g in (5, 4, 3, 2) for h in range(3)], [], 6000
    monkeypatch.setattr(pb, "trades_della_coin", _trades)
    monkeypatch.setattr(pb, "_trade_paper", lambda fb_, dal_ts: [])
    f = tmp_path / "validate.json"
    f.write_text(json.dumps({"coppie": {"AAAUSDT|gen_a": {"t": 2.6, "n": 120},
                                        "BBBUSDT|gen_b": {"t": 0.9, "n": 60}}}))
    monkeypatch.setattr(pb, "FILE_VOTI_T", str(f))
    assert pb.main([]) == 0
    out = capsys.readouterr().out
    assert "H1 (regola del 30 set)" in out and "t del gate 2 o piu': 12 segnali +1.00R" in out
    assert sorted(set(fb.letti)) == sorted(fb.letti)
    pubblicato = fb.scritti[("portfolio", "backtest")]["fuori_campione"]
    assert pubblicato["regola_h1"] == pb.REGOLA_H1
    assert pubblicato["voto_t"]["walk_forward"]["alta"]["n"] == 12
    assert not pb.contiene_liste_annidate(fb.scritti[("portfolio", "backtest")])


def test_un_segnale_preso_da_coppie_dei_due_gruppi_conta_una_volta_sola():
    """Il rilievo del 30 set: la stessa candela presa da una gemella a t alta e
    da una a t bassa entrava in tutti e due i gruppi (la somma superava i
    segnali del motore e la differenza si schiacciava). Ora si conta come una
    soglia vera: il segnale resta (fra le alte) se una coppia che lo prende ha
    t alta; va fra le basse solo se tutte le sue coppie hanno t bassa."""
    pairs = {"X|hi": {"validated_at": V}, "X|lo": {"validated_at": V}}
    voti = {"X|hi": {"t": 3.0, "n": 100}, "X|lo": {"t": 1.0, "n": 100}}
    motore = []
    for g in range(10):
        base = V + (g + 1) * 86400
        for j, r in enumerate((0.3, 0.1)):              # presi da tutte e due
            motore.append(_m("X", "hi", base + j * 3600, r))
            motore.append(_m("X", "lo", base + j * 3600, r))
        for j, r in enumerate((0.5, 0.33)):             # solo dalla t alta
            motore.append(_m("X", "hi", base + (2 + j) * 3600, r))
        for j, r in enumerate((-0.2, -0.3)):            # solo dalla t bassa
            motore.append(_m("X", "lo", base + (4 + j) * 3600, r))
    fc = pb.fuori_campione(motore, None, pairs, list(pairs), PAV, voti=voti)
    wf = fc["voto_t"]["walk_forward"]
    assert fc["motore"]["n"] == 60                       # 80 trade = 60 segnali
    assert wf["alta"]["n"] == 40 and wf["bassa"]["n"] == 20
    assert wf["alta"]["n"] + wf["bassa"]["n"] <= fc["motore"]["n"]
    assert wf["condivisi"] == 20 and wf["fuori"] == 0
    # la differenza e' «tenuti con la soglia» meno «tolti dalla soglia»
    tenuti = (0.3 + 0.1 + 0.5 + 0.33) / 4
    assert math.isclose(wf["alta"]["r_medio"], tenuti)
    assert math.isclose(wf["bassa"]["r_medio"], -0.25)
    assert math.isclose(wf["differenza"], tenuti + 0.25)


def test_holdout_su_troppi_pochi_trade_e_campi_mancanti_restano_fuori_e_contati():
    """Una t dell'holdout su meno di 5 trade (0.0 con 0-1 trade, enorme con
    2-4) non va in nessun gruppo; e una coppia senza quel campo e' contata."""
    pairs, _v, motore, paper = _caso_t()
    voti = {"A|ga": {"t": 3.1, "n": 100, "t_holdout": 11.0, "n_holdout": 2},
            "B|gb": {"t": 1.2, "n": 400, "t_holdout": 0.0, "n_holdout": 0}}
    vt = pb.fuori_campione(motore, paper, pairs, list(pairs), PAV, voti=voti)["voto_t"]
    ho = vt["holdout"]
    assert ho["alta"]["n"] == 0 and ho["bassa"]["n"] == 0
    assert ho["fuori"] == 54                             # A, B e C: tutti fuori
    assert vt["walk_forward"]["alta"]["n"] == 18         # il walk-forward non cambia


def test_la_soglia_di_t_su_radice_n_e_fissa_fra_una_lettura_e_l_altra():
    """Il rilievo del 30 set: la mediana si ricalcolava sulle coppie con trade
    in quella lettura, e fra il 7 e il 14 ott i gruppi si rimescolavano senza
    che cambiasse nessuna t. Ora e' la mediana del file della passata."""
    pairs, voti, motore, paper = _caso_t()
    voti = {**voti, "Z|gz": {"t": 2.0, "n": 25}, "Y|gy": {"t": 0.5, "n": 400}}
    rapporti = sorted([3.1 / 10, 1.2 / 20, 2.0 / 5, 0.5 / 20])
    vt7 = pb.fuori_campione(motore, paper, pairs, list(pairs), PAV, voti=voti)["voto_t"]
    solo_a = [r for r in motore if r["symbol"] == "A"]
    vt14 = pb.fuori_campione(solo_a, None, pairs, list(pairs), PAV, voti=voti)["voto_t"]
    for q in (vt7["t_su_radice_n"], vt14["t_su_radice_n"]):
        assert math.isclose(q["mediana"], (rapporti[1] + rapporti[2]) / 2)
        assert q["mediana_da"] == "passata"
    # senza file: la mediana di questa lettura, e lo dice
    reg = {"A|ga": {"validated_at": V, "val_t": 3.1, "val_trades": 100},
           "B|gb": {"validated_at": V, "val_t": 1.2, "val_trades": 400}}
    q = pb.fuori_campione(motore, paper, reg, list(reg), PAV)["voto_t"]["t_su_radice_n"]
    assert q["mediana_da"] == "lettura" and math.isclose(q["mediana"], (0.31 + 0.06) / 2)



def test_lettura_h1_tre_esiti():
    """Regola decisa il 30 set sera: ultimo esame, soglia 1,5, minimo 80 segnali
    per gruppo; proposta oltre il margine, chiusa se differenza + margine < 0,25R."""
    def d(na, nb, diff, e):
        return {"alta": {"n": na}, "bassa": {"n": nb}, "differenza": diff,
                "errore_differenza": e}
    assert pb.SOGLIA_T_HOLDOUT == 1.5 and pb.MIN_SEGNALI_H1 == 80
    assert "non si sa ancora: 79 e 200" in pb.lettura_h1(d(79, 200, 0.9, 0.01))
    assert pb.lettura_h1(d(80, 80, 0.30, 0.10)).startswith("H1: proposta")
    assert pb.lettura_h1(d(80, 80, 0.20, 0.10)).startswith("H1: non si sa ancora")  # bordo: 0,20 non > 0,20
    assert pb.lettura_h1(d(100, 100, 0.05, 0.05)).startswith("H1: chiusa")  # 0,05 + 0,10 < 0,25
    assert pb.lettura_h1(d(100, 100, 0.10, 0.08)).startswith("H1: non si sa ancora")  # 0,26
    assert pb.lettura_h1(None).startswith("H1: non si sa ancora")
