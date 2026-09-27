"""IL PAPER ENTRA DOVE ENTRA IL GATE? — il classificatore trade per trade (27 set 2026, J12).

Ops 0304 ha misurato 20 ingressi del paper su 37 con un trade del motore entro
due barre. `scripts/ingressi_report.py` apre quel numero: per ogni trade del
paper una classe sola, decisa in un ordine fisso, e per la classe «la regola
non scatta» un sotto-motivo che dice DOVE le due parti differiscono.

Qui si difende cio' che rende quella classificazione credibile:
  * la candela del segnale del paper e' quella CHIUSA prima dell'ingresso (la
    stessa convenzione con cui il motore data i suoi trade);
  * l'ordine delle classi: prima l'abbinamento, poi «il motore era dentro»,
    poi il cooldown, poi la regola, poi «lontano»;
  * un trade del motore si usa una volta sola (come in ops 0304);
  * il confronto degli indicatori tratta un valore mancante come differenza;
  * la lettura finale viene da regole, e dice «regge» solo sopra l'obiettivo;
  * lo script e' in sola lettura, parte senza argomenti e senza Firebase esce 0.
"""
import inspect
import os
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

from backtesting.engine import Backtester
from bot.core.indicators import compute_indicator_frame
from bot.core.models import Candle, IndicatorSnapshot
from bot.strategies.generated import GeneratedStrategy
from scripts import ingressi_report as ir

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TF = 900.0                       # 15 minuti
T0 = 1_749_999_600.0             # un confine di candela (multiplo di 900)


def _g(entry_bar: int, bars_held: int = 4, pnl: float = 0.01, direction: str = "long"):
    """Un trade del motore che entra alla barra `entry_bar` (da T0)."""
    return SimpleNamespace(entry_ts=T0 + entry_bar * TF, bars_held=bars_held, pnl_pct=pnl,
                           direction=direction)


def _p(bar: int, direction: str = "long", **extra) -> dict:
    """Un trade del paper deciso alla chiusura della barra `bar`: `signal_candle_ts`
    e' il confine (apertura della barra dopo), `entry_time` qualche secondo dopo."""
    ts = T0 + (bar + 1) * TF
    t = {"symbol": "XUSDT", "strategy": "gen_x", "direction": direction,
         "entry_time": datetime.fromtimestamp(ts + 7, tz=timezone.utc).isoformat(),
         "signal_candle_ts": ts, "entry_price": 1.0, "pnl": -1.0, "exit_reason": "stop_loss"}
    t.update(extra)
    return t


# --------------------------------------------------------------------------- #
# 1. la candela del paper                                                      #
# --------------------------------------------------------------------------- #
def test_la_candela_del_paper_e_quella_chiusa_prima_dell_ingresso():
    assert ir.barra_del_paper(_p(10), TF) == T0 + 10 * TF
    # senza `signal_candle_ts` (trade vecchi): dal confine, una barra indietro
    t = _p(10)
    del t["signal_candle_ts"]
    assert ir.barra_del_paper(t, TF) == T0 + 10 * TF
    assert ir.barra_del_paper({"entry_time": "boh"}, TF) == 0.0


def test_finestra_e_uscita_dedotta_di_un_trade_del_motore():
    g = _g(5, bars_held=3, pnl=-0.01)
    assert ir.finestra_trade(g, TF) == (T0 + 5 * TF, T0 + 8 * TF)
    assert ir.uscita_dedotta(g) == "stop"
    assert ir.uscita_dedotta(_g(5, bars_held=3, pnl=0.02)) == "guadagno"
    assert ir.uscita_dedotta(_g(5, bars_held=96, pnl=-0.01)) == "orizzonte"
    # il cooldown si apre SOLO dopo uno stop in perdita
    assert ir.in_cooldown_dopo(g, TF, 4) == (T0 + 8 * TF, T0 + 12 * TF)
    assert ir.in_cooldown_dopo(_g(5, bars_held=3, pnl=0.02), TF, 4) is None
    assert ir.in_cooldown_dopo(g, TF, 0) is None


# --------------------------------------------------------------------------- #
# 2. il classificatore, una classe per volta                                   #
# --------------------------------------------------------------------------- #
def _diag_no(**kw):
    base = {"scatta_motore": {-1: False, 0: False, 1: False}, "scatta_motore_k": False,
            "diffs": [], "indicatori_paper": {"rsi": 30.0}, "contesto": {}, "attiva_nel_regime": True}
    base.update(kw)
    return lambda p, b: base


def test_ABBINATO_entro_due_barre_con_scarto_e_direzione():
    righe = ir.classifica_coppia([_p(10, "short")], [_g(11, direction="short")], TF, 4, diagnosi=_diag_no())
    r = righe[0]
    assert r["classe"] == "ABBINATO"
    assert r["delta_min"] == 15.0 and r["stessa_direzione"] is True
    righe = ir.classifica_coppia([_p(10, "short")], [_g(10, direction="long")], TF, 4, diagnosi=_diag_no())
    assert righe[0]["classe"] == "ABBINATO" and righe[0]["stessa_direzione"] is False
    assert "DIVERSA" in righe[0]["dettaglio"]


def test_un_trade_del_motore_si_usa_una_volta_sola():
    """Due trade del paper vicini allo stesso segnale: il secondo NON e' abbinato
    (altrimenti la parita' sembrerebbe perfetta mentre non lo e')."""
    righe = ir.classifica_coppia([_p(10), _p(11)], [_g(10, bars_held=1, pnl=0.01)], TF, 4,
                                 diagnosi=_diag_no())
    assert [r["classe"] for r in righe][0] == "ABBINATO"
    assert righe[1]["classe"] != "ABBINATO"


def test_MOTORE_IN_POSIZIONE_quando_il_motore_era_ancora_dentro():
    g = _g(2, bars_held=20, pnl=0.02)
    righe = ir.classifica_coppia([_p(10)], [g], TF, 4, diagnosi=_diag_no())
    assert righe[0]["classe"] == "MOTORE_IN_POSIZIONE"
    assert righe[0]["motore"] is g and "cascata" in righe[0]["dettaglio"]
    # la barra d'uscita stessa e' ancora «dentro» (il motore riparte dalla successiva)
    righe = ir.classifica_coppia([_p(22)], [g], TF, 4, diagnosi=_diag_no())
    assert righe[0]["classe"] == "MOTORE_IN_POSIZIONE"


def test_MOTORE_IN_COOLDOWN_dopo_uno_stop_in_perdita():
    g = _g(2, bars_held=3, pnl=-0.01)          # uscita alla barra 5, cooldown 6..9
    righe = ir.classifica_coppia([_p(8)], [g], TF, 4, diagnosi=_diag_no())
    assert righe[0]["classe"] == "MOTORE_IN_COOLDOWN"
    assert "3ª di 4" in righe[0]["dettaglio"]
    # dopo un'uscita in GUADAGNO non c'e' cooldown: si passa alla regola
    righe = ir.classifica_coppia([_p(8)], [_g(2, bars_held=3, pnl=0.03)], TF, 4, diagnosi=_diag_no())
    assert righe[0]["classe"] == "REGOLA_NON_SCATTA"


def test_REGOLA_NON_SCATTA_con_sotto_motivo():
    diffs = [{"campo": "rsi", "motore": 41.0, "paper": 28.0, "diff": 0.3}]
    righe = ir.classifica_coppia([_p(10)], [], TF, 4, diagnosi=_diag_no(diffs=diffs, scatta_bot200=True))
    assert righe[0]["classe"] == "REGOLA_NON_SCATTA"
    assert righe[0]["sotto"] == "INDICATORI_DIVERSI"
    assert "rsi 41/28" in righe[0]["dettaglio"] and "199 candele" in righe[0]["dettaglio"]


def test_ABBINATO_LONTANO_fra_2_e_8_barre_quando_la_regola_scatta_vicino():
    diag = _diag_no(scatta_motore={-1: False, 0: False, 1: True})
    righe = ir.classifica_coppia([_p(10)], [_g(15)], TF, 4, diagnosi=diag)
    assert righe[0]["classe"] == "ABBINATO_LONTANO"
    assert righe[0]["delta_min"] == 75.0
    # oltre le 8 barre non e' piu' «lontano»: e' la regola che non scatta. Il
    # metro e' quello di ops 0304 (`_accoppia`): lo scarto si misura da
    # `entry_time`, qualche secondo dopo il confine, quindi la barra 19 (8 barre
    # meno 7 s) rientra ancora e la 20 no.
    righe = ir.classifica_coppia([_p(10)], [_g(20)], TF, 4, diagnosi=diag)
    assert righe[0]["classe"] == "REGOLA_NON_SCATTA"


def test_SENZA_MOTORE_quando_la_candela_non_c_e_o_la_data_non_si_legge():
    righe = ir.classifica_coppia([_p(10)], [], TF, 4, diagnosi=lambda p, b: None)
    assert righe[0]["classe"] == "SENZA_MOTORE"
    righe = ir.classifica_coppia([{"entry_time": None}], [_g(10)], TF, 4, diagnosi=_diag_no())
    assert righe[0]["classe"] == "SENZA_MOTORE"
    # una diagnosi che esplode non ferma la coppia
    def _boom(p, b):
        raise RuntimeError("frame rotto")
    righe = ir.classifica_coppia([_p(10)], [], TF, 4, diagnosi=_boom)
    assert righe[0]["classe"] == "SENZA_MOTORE" and "frame rotto" in righe[0]["dettaglio"]


def test_l_ordine_delle_classi_e_quello_dichiarato():
    """Abbinato batte «dentro»; «dentro» batte il cooldown; il cooldown batte la
    regola: lo stesso trade, con i trade del motore giusti, cambia classe
    nell'ordine e mai al contrario."""
    dentro = _g(2, bars_held=20, pnl=-0.01)
    stesso = _g(10)
    righe = ir.classifica_coppia([_p(10)], [dentro, stesso], TF, 4, diagnosi=_diag_no())
    assert righe[0]["classe"] == "ABBINATO"
    righe = ir.classifica_coppia([_p(10)], [dentro], TF, 4, diagnosi=_diag_no())
    assert righe[0]["classe"] == "MOTORE_IN_POSIZIONE"
    assert list(ir.CLASSI) == ["ABBINATO", "MOTORE_IN_POSIZIONE", "MOTORE_IN_COOLDOWN",
                               "REGOLA_NON_SCATTA", "ABBINATO_LONTANO", "SENZA_MOTORE"]


# --------------------------------------------------------------------------- #
# 3. il confronto degli indicatori e i sotto-motivi                            #
# --------------------------------------------------------------------------- #
def test_diff_indicatori_sopra_il_5_percento_e_i_mancanti():
    motore = IndicatorSnapshot(timeframe="15m", rsi=40.0, adx=20.0, atr=1.0, close=100.0)
    paper = {"rsi": 41.0, "adx": 30.0, "atr": None, "close": 100.0, "volume": 5.0}
    d = {x["campo"]: x for x in ir.diff_indicatori(motore, paper)}
    assert "rsi" not in d and "close" not in d           # entro il 5%
    assert d["adx"]["diff"] > 0.3                          # 20 contro 30
    assert d["atr"]["diff"] is None and d["atr"]["paper"] is None   # mancante da una parte
    assert d["volume"]["motore"] is None                   # mancante dall'altra
    assert ir.diff_indicatori(None, None) == []
    assert ir.diff_indicatori({"rsi": 0.0}, {"rsi": 0.0}) == []


def test_sotto_motivo_in_ordine():
    base = {"scatta_motore_k": False, "diffs": [], "indicatori_paper": {"rsi": 1},
            "attiva_nel_regime": True, "contesto": {}}
    assert ir.sotto_motivo({**base, "scatta_motore_k": True, "tradabile": False})[0] == "SEGNALE_SENZA_TRADE"
    assert ir.sotto_motivo({**base, "scatta_motore_k": True})[0] == "SEGNALE_SENZA_TRADE"
    assert ir.sotto_motivo({**base, "indicatori_paper": None})[0] == "IGNOTO"
    assert ir.sotto_motivo({**base, "diffs": [{"campo": "rsi", "motore": 1, "paper": 2, "diff": 0.5}]})[0] \
        == "INDICATORI_DIVERSI"
    assert ir.sotto_motivo({**base, "scatta_prezzo_vivo": True, "prezzo_paper": 1.0,
                            "prezzo_motore": 0.99})[0] == "PREZZO_VIVO"
    assert ir.sotto_motivo({**base, "attiva_nel_regime": False})[0] == "REGIME_DIVERSO"
    assert ir.sotto_motivo({**base, "contesto": {"usa_mercato": True, "market_up_motore": 1.0,
                                                 "market_up_paper": 0.0}})[0] == "CONTESTO_BTC"
    assert ir.sotto_motivo({**base, "contesto": {"usa_htf": True, "diffs_1h": []}})[0] == "CONTESTO_BTC"
    assert ir.sotto_motivo({**base, "scatta_paper_valori": True})[0] == "REGOLA_DIVERSA"
    assert ir.sotto_motivo({**base, "scatta_paper_valori": False})[0] == "IGNOTO"
    for s in ("INDICATORI_DIVERSI", "PREZZO_VIVO", "REGIME_DIVERSO", "CONTESTO_BTC",
              "REGOLA_DIVERSA", "SEGNALE_SENZA_TRADE", "IGNOTO"):
        assert s in ir.SOTTO_MOTIVI


# --------------------------------------------------------------------------- #
# 4. il riassunto e la lettura                                                 #
# --------------------------------------------------------------------------- #
def _righe(*classi, sotto=None):
    return [{"classe": c, "sotto": (sotto if c == "REGOLA_NON_SCATTA" else None)} for c in classi]


def test_riassunto_conta_classi_sotto_motivi_quote_e_top():
    r = ir.riassunto({
        "A|s": _righe("ABBINATO", "MOTORE_IN_POSIZIONE", "MOTORE_IN_POSIZIONE"),
        "B|s": _righe("ABBINATO", "ABBINATO"),
        "C|s": _righe("REGOLA_NON_SCATTA", sotto="INDICATORI_DIVERSI"),
    })
    assert r["n"] == 6 and r["abbinati"] == 3 and abs(r["quota"] - 0.5) < 1e-9
    assert r["classi"]["MOTORE_IN_POSIZIONE"] == 2 and r["sotto"] == {"INDICATORI_DIVERSI": 1}
    assert r["per_coppia"]["B|s"]["quota"] == 1.0 and r["per_coppia"]["A|s"]["non"] == 2
    assert r["top_non_abbinati"] == ["A|s", "C|s"]     # B non ha non abbinati


def test_lettura_da_regole():
    assert "niente da leggere" in ir.lettura({"n": 0})
    regge = ir.riassunto({"A|s": _righe("ABBINATO", "ABBINATO", "ABBINATO", "ABBINATO", "MOTORE_IN_POSIZIONE")})
    assert "regge" in ir.lettura(regge)
    cascata = ir.riassunto({"A|s": _righe("ABBINATO", "MOTORE_IN_POSIZIONE", "MOTORE_IN_POSIZIONE")})
    assert "CASCATA DALLE USCITE" in ir.lettura(cascata)
    cd = ir.riassunto({"A|s": _righe("MOTORE_IN_COOLDOWN", "MOTORE_IN_COOLDOWN", "ABBINATO")})
    assert "COOLDOWN" in ir.lettura(cd)
    warm = ir.riassunto({"A|s": _righe("REGOLA_NON_SCATTA", "REGOLA_NON_SCATTA", "ABBINATO",
                                        sotto="INDICATORI_DIVERSI")})
    testo = ir.lettura(warm, quota_finestra_bot=0.9)
    assert "WARMUP" in testo and "salgono a 90%" in testo
    assert "non li alza" in ir.lettura(warm, quota_finestra_bot=0.2)
    bug = ir.riassunto({"A|s": _righe("REGOLA_NON_SCATTA", "ABBINATO", sotto="REGOLA_DIVERSA")})
    assert "BUG" in ir.lettura(bug)
    ctx = ir.riassunto({"A|s": _righe("REGOLA_NON_SCATTA", sotto="CONTESTO_BTC")})
    assert "CONTESTO" in ir.lettura(ctx)
    lontano = ir.riassunto({"A|s": _righe("ABBINATO_LONTANO", "ABBINATO")})
    assert "latenza" in ir.lettura(lontano)
    assert ir.OBIETTIVO_ABBINATI == 0.80


# --------------------------------------------------------------------------- #
# 5. la diagnosi vera, offline, su candele sintetiche                          #
# --------------------------------------------------------------------------- #
def _serie(n: int = 700) -> list[Candle]:
    t0 = datetime(2024, 1, 1, tzinfo=timezone.utc)
    out, px = [], 100.0
    for k in range(n):
        if 300 <= k < 500:
            # un tratto PIATTO: l'RSI resta a meta', il motore non entra e resta
            # libero — la barra «muta» del test sta qui
            px *= 1 + (0.0005 if k % 2 else -0.0005)
        else:
            # onde lunghe: l'RSI tocca davvero gli estremi
            px *= 1 + (0.006 if (k // 25) % 2 == 0 else -0.006) + (0.001 if k % 3 else -0.001)
        out.append(Candle(open_time=t0 + timedelta(minutes=15 * k), open=px, high=px * 1.004,
                          low=px * 0.996, close=px, volume=1000.0 + (k % 5) * 10))
    return out


SPEC = {"id": "gen_test", "features": [{"kind": "rsi_extreme", "low": 35.0, "high": 65.0}],
        "atr_mult_stop": 1.5, "rr": 2.0}


def test_la_diagnosi_riconosce_un_ingresso_del_motore_e_una_barra_muta():
    """Sulle stesse candele: un trade del paper alla candela di un trade del
    motore e' ABBINATO; uno dove il motore e' libero e la regola non scatta
    finisce in REGOLA_NON_SCATTA con un sotto-motivo dichiarato, e la diagnosi
    ha valutato la regola anche «con 199 candele»."""
    candles = _serie()
    frame = compute_indicator_frame(candles)
    bt = Backtester(window=200, interval_hours=0.25)
    make = lambda: GeneratedStrategy(SPEC)  # noqa: E731
    st = bt.run_strategy(make(), "XUSDT", candles, frame=frame)
    gtrades = sorted(st.trades, key=lambda t: t.entry_ts)
    assert gtrades, "la serie sintetica deve produrre trade del motore"
    diag = ir.Diagnosta(bt, make, "XUSDT", candles, frame, "15m")
    tf_s = 900.0

    # un trade del paper deciso alla stessa candela del primo trade del motore
    g0 = gtrades[0]
    k0 = diag.indice(g0.entry_ts)
    snap = diag.snapshot_motore(k0)
    paper_ok = {"symbol": "XUSDT", "strategy": "gen_test", "direction": g0.direction,
                "entry_time": datetime.fromtimestamp(g0.entry_ts + tf_s + 5, tz=timezone.utc).isoformat(),
                "signal_candle_ts": g0.entry_ts + tf_s, "entry_price": g0.entry_price,
                "indicators_at_entry": {"15m": snap.ind("15m").model_dump()},
                "regime_at_entry": snap.regime.value, "pnl": 1.0}
    # una barra dove il motore e' LIBERO (fuori da ogni trade e cooldown) e MUTO
    def _libera(ts):
        for g in gtrades:
            e, u = ir.finestra_trade(g, tf_s)
            # ne' dentro il trade o il suo cooldown, ne' con un ingresso del motore
            # a meno di 9 barre (che sarebbe «abbinato» o «lontano»)
            if e < ts <= u + 4 * tf_s or abs(e - ts) <= 9 * tf_s:
                return False
        return True
    k_muta = None
    for k in range(202, len(candles) - 2):
        ts = candles[k].open_time.timestamp()
        if _libera(ts) and diag.segnale(make(), diag.snapshot_motore(k), k) is None:
            k_muta = k
            break
    assert k_muta is not None
    ts_muta = candles[k_muta].open_time.timestamp()
    paper_muta = {**paper_ok, "signal_candle_ts": ts_muta + tf_s,
                  "entry_time": datetime.fromtimestamp(ts_muta + tf_s + 5, tz=timezone.utc).isoformat(),
                  "indicators_at_entry": {"15m": {**snap.ind("15m").model_dump(), "rsi": 20.0}}}

    righe = ir.classifica_coppia([paper_muta, paper_ok], gtrades, tf_s, 4, diagnosi=diag)
    per = {id(r["paper"]): r for r in righe}
    assert per[id(paper_ok)]["classe"] == "ABBINATO"
    assert per[id(paper_ok)]["stessa_direzione"] is True
    r = per[id(paper_muta)]
    assert r["classe"] == "REGOLA_NON_SCATTA" and r["sotto"] in ir.SOTTO_MOTIVI
    d = r["diagnosi"]
    assert d["scatta_motore"][0] is False and d["scatta_bot200"] is not None
    assert d["regime_motore"] and "rsi" in {x["campo"] for x in d["diffs"]}


def test_la_finestra_come_il_bot_rigira_solo_da_200_barre_prima():
    candles = _serie()
    bt = Backtester(window=200, interval_hours=0.25)
    make = lambda: GeneratedStrategy(SPEC)  # noqa: E731
    assert ir.finestra_come_il_bot(bt, make, "XUSDT", candles, []) == []
    assert ir.finestra_come_il_bot(bt, make, "XUSDT", candles, [50]) == []      # troppo corta
    trades = ir.finestra_come_il_bot(bt, make, "XUSDT", candles, [400, 450])
    primo = candles[max(0, 400 - ir.FINESTRA_BOT)].open_time.timestamp()
    assert all(t.entry_ts >= primo for t in trades)


# --------------------------------------------------------------------------- #
# 6. sola lettura, senza argomenti, senza Firebase, in lista bianca            #
# --------------------------------------------------------------------------- #
def test_e_in_sola_lettura_e_parte_senza_argomenti():
    src = inspect.getsource(ir).split('"""', 2)[-1]
    for vietato in ("set_doc", "set_rtdb", "merge_into_registry", "persist_specs", "update_registry"):
        assert vietato not in src, f"il report chiama `{vietato}`: deve solo misurare"
    main = inspect.getsource(ir.main)
    assert "ap.error(" not in main and '"--budget"' in main and '"--coppie"' in main
    assert ir.BUDGET_S < 900, "la deadline propria deve stare sotto il timeout del canale ops"
    # i mattoni di ops 0304 sono importati, non riscritti
    assert "from scripts.confronto_gate_paper import _accoppia, _costruisci, _ts, trade_del_gate" in src
    # e le tarature per coppia si leggono con le funzioni del bot
    for fn in ("ladder_multiples(sparams)", "breakeven_after_tp1(sparams)", "lock_keep(sparams)"):
        assert fn in main


def test_senza_firebase_esce_con_zero():
    env = {**os.environ, "FIREBASE_SERVICE_ACCOUNT": "", "TRADING_BOT_TEST_MODE": "1",
           "BACKTEST_ALLOW_SYNTHETIC": "false", "DRY_RUN": "true", "PYTHONPATH": ROOT}
    p = subprocess.run([sys.executable, "-m", "scripts.ingressi_report"], cwd=ROOT, env=env,
                       capture_output=True, text=True, timeout=120)
    assert p.returncode == 0, p.stderr[-800:]
    assert "niente da classificare" in p.stdout


def test_la_voce_ops_esiste_nella_lista_bianca_di_esempio():
    from scripts.ops_agent import parse_allowlist
    with open(os.path.join(ROOT, "ops", "allowlist.example"), encoding="utf-8") as f:
        voci = parse_allowlist(f.read())
    assert voci["ingressi"]["cmd"] == ".venv/bin/python -m scripts.ingressi_report"
    assert voci["ingressi"]["args"] is False
