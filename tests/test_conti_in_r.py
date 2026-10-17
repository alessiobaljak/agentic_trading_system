"""
Il lato REPORT delle voci aperte del backlog, fatto il 1 ott 2026:

* K8 — `trades` mette accanto alle righe in USDT gli stessi gruppi in R
  (direzione, regime all'apertura, rispetto al trend, direzione x BTC, per
  strategia), con la colonna «tutto» e quella dei trade entrati dal 27 set
  19:40 UTC, quanti trade sono senza R, i costi in R e il lordo in R;
* K4 — la riga «caso»: accanto ai numeri d'uscita del paper, quelli di un
  prezzo casuale con le nostre uscite, costanti della simulazione del 30 set;
* J15 — `controllo` dice che i «cambiamenti del learning» sono rispetto al
  controllo di un'ora fa, non a ieri;
* lo spazio: la tabella del keep per strategia mostra per nome solo chi ha
  almeno 2 verdetti (le altre in una riga), cosi' `trades` resta sotto il
  taglio dell'agente ops.
"""
from __future__ import annotations

import inspect
from datetime import datetime, timezone

from scripts import trade_stats as ts

PRIMA = datetime(2026, 9, 25, 12, 0, tzinfo=timezone.utc).timestamp()   # nel difetto
DOPO = datetime(2026, 9, 29, 12, 0, tzinfo=timezone.utc).timestamp()    # dopo il taglio


def _t(pnl, *, d="long", ts_=DOPO, reg="bull_trending", gid="gen_a", up=None,
       stop=True, costo=None, lordo=None, size=10.0, **extra):
    """Un trade con entry 100 e stop originale a 1 di distanza: rischio = size."""
    t = {"strategy": gid, "symbol": "AUSDT", "direction": d, "pnl": pnl,
         "entry_price": 100.0, "size": size, "entry_ts": ts_, "exit_ts": ts_ + 600,
         "regime_at_entry": reg, "exit_reason": "time_exit"}
    if stop:
        t["orig_stop"] = 99.0 if d == "long" else 101.0
    if up is not None:
        t["feats_at_entry"] = {"market_up": up}
    if costo is not None:
        t["total_cost_usdt"] = costo
    if lordo is not None:
        t["gross_pnl_usdt"] = lordo
    t.update(extra)
    return t


# --------------------------------------------------------------------------- #
# K8: i conti in R                                                             #
# --------------------------------------------------------------------------- #
def test_le_size_diverse_pesano_uguale_in_r():
    # stesso esito in R (-1R e +1R), size 10 e 5: in USDT -10 + 5 = -5, in R 0
    rep = ts.conti_in_r_report([_t(-10.0, size=10.0), _t(5.0, size=5.0)])
    tutte = rep["tutte"]["tutto"]
    assert tutte == {"n": 2, "senza_r": 0, "r_medio": 0.0, "r_tot": 0.0}


def test_due_colonne_tutto_e_dal_27_set():
    trades = [_t(-10.0, ts_=PRIMA), _t(-10.0, ts_=PRIMA), _t(20.0, ts_=DOPO)]
    rep = ts.conti_in_r_report(trades)
    assert rep["dal_ts"] == ts.DAL_REGOLA_3_OTT          # lo stesso taglio della regola del 3 ott
    assert rep["direzione"]["long"]["tutto"] == {"n": 3, "senza_r": 0, "r_medio": 0.0, "r_tot": 0.0}
    assert rep["direzione"]["long"]["dal"] == {"n": 1, "senza_r": 0, "r_medio": 2.0, "r_tot": 2.0}
    assert rep["direzione"]["short"]["tutto"]["n"] == 0


def test_i_trade_senza_r_si_contano_per_gruppo():
    trades = [_t(-10.0), _t(3.0, stop=False), _t(3.0, size=0)]
    rep = ts.conti_in_r_report(trades)
    assert rep["tutte"]["tutto"] == {"n": 1, "senza_r": 2, "r_medio": -1.0, "r_tot": -1.0}
    assert rep["strategia"]["gen_a"]["dal"]["senza_r"] == 2


def test_regime_trend_e_contesto_btc_come_le_righe_in_usdt():
    trades = [_t(10.0, d="long", reg="bull_trending", up=True),     # in trend, long con BTC
              _t(-10.0, d="short", reg="bull_trending", up=True),   # controtrend, short contro BTC
              _t(5.0, d="short", reg="sideways", up=False),         # neutro, short con BTC
              _t(-5.0, d="long", reg=None)]                         # regime e contesto ignoti
    rep = ts.conti_in_r_report(trades)
    assert rep["regime"]["bull_trending"]["tutto"]["r_tot"] == 0.0
    assert rep["regime"]["ignoto"]["tutto"]["r_tot"] == -0.5
    assert rep["trend"]["in_trend"]["tutto"]["r_medio"] == 1.0
    assert rep["trend"]["contro"]["tutto"]["r_medio"] == -1.0
    assert rep["trend"]["neutro"]["tutto"]["r_medio"] == 0.5
    assert rep["trend"]["ignoto"]["tutto"]["n"] == 1
    # direzione x BTC: stessa casella di bot/learning/referti.casella_contesto
    assert rep["contesto"]["long_con"]["tutto"]["r_medio"] == 1.0
    assert rep["contesto"]["short_contro"]["tutto"]["r_medio"] == -1.0
    assert rep["contesto"]["short_con"]["tutto"]["r_medio"] == 0.5
    assert rep["contesto"]["ignoto"]["tutto"]["n"] == 1
    # lo stesso criterio di controtrend del blocco in USDT
    usdt = ts.direction_report(trades)["allineamento"]
    assert {k: usdt[k]["trade"] for k in ("in_trend", "contro", "neutro", "ignoto")} == \
        {k: rep["trend"][k]["tutto"]["n"] for k in ("in_trend", "contro", "neutro", "ignoto")}


def test_costi_e_lordo_in_r_sullo_stesso_rischio():
    trades = [_t(-12.0, costo=2.0, lordo=-10.0), _t(8.0, costo=2.0, lordo=10.0),
              _t(1.0)]                                      # senza campi di costo: fuori da quelle righe
    rep = ts.conti_in_r_report(trades)
    assert rep["costi"]["tutto"] == {"n": 2, "senza_r": 1, "r_medio": 0.2, "r_tot": 0.4}
    assert rep["lordo"]["tutto"] == {"n": 2, "senza_r": 1, "r_medio": 0.0, "r_tot": 0.0}
    # netto = lordo - costi sui trade che hanno i campi
    assert round(rep["lordo"]["tutto"]["r_tot"] - rep["costi"]["tutto"]["r_tot"], 6) == -0.4


def test_per_strategia_le_prime_e_le_altre_in_una_riga(capsys):
    trades = []
    for i in range(ts.R_STRATEGIE_MAX + 3):
        trades += [_t(-10.0, gid=f"gen_{i:02d}")] * (20 - i)
    rep = ts.conti_in_r_report(trades)
    assert list(rep["strategia"]) == [f"gen_{i:02d}" for i in range(ts.R_STRATEGIE_MAX)]
    alt = rep["altre_strategie"]
    assert alt["n"] == 3 and alt["tutto"]["n"] == sum(20 - i for i in range(ts.R_STRATEGIE_MAX,
                                                                          ts.R_STRATEGIE_MAX + 3))
    ts.print_conti_in_r(rep)
    out = capsys.readouterr().out
    assert "CONTI IN R (K8)" in out and "dal 27 set 19:40 UTC" in out
    assert "altre 3" in out and "s/R" in out and "costi stimati" in out and "lordo" in out
    riga = next(r for r in out.splitlines() if r.strip().startswith("gen_00"))
    assert "-1.000" in riga and "-20.00" in riga


def test_stampa_con_gruppi_vuoti_non_si_rompe(capsys):
    ts.print_conti_in_r(ts.conti_in_r_report([]))
    out = capsys.readouterr().out
    assert "TUTTE (netto)" in out and "—" in out


# --------------------------------------------------------------------------- #
# K4: la riga «caso»                                                           #
# --------------------------------------------------------------------------- #
def test_il_caso_sono_costanti_dichiarate_con_la_fonte():
    assert ts.CASO_30SET == {"stop": 0.46, "stop_ingresso": 0.485, "stop_uscita": 0.515,
                             "mfe_mediana_r": 0.81, "primo_target": 0.17, "vinti": 0.54,
                             "r_medio": -0.067}
    assert "revisione_sospese_30set.md" in ts.FONTE_CASO and "K4" in ts.FONTE_CASO
    assert "non ricalcolate" in ts.FONTE_CASO


def test_i_numeri_del_paper_accanto_al_caso(capsys):
    scala = {"scale_r_mults": [1.5, 3.0, 5.0]}
    trades = [_t(-10.0, exit_reason="stop_loss", mfe_r=0.1, **scala),      # stop d'ingresso
              _t(-10.0, exit_reason="stop_loss", mfe_r=0.8, **scala),      # stop d'uscita
              _t(15.0, exit_reason="take_profit", mfe_r=1.6, **scala),     # primo target
              _t(5.0, mfe_r=0.9, **scala)]
    rep = ts.firma_del_caso_report(trades)
    assert rep["stop"] == 0.5 and rep["stop_n"] == 2
    assert rep["stop_ingresso"] == 0.5 and rep["stop_uscita"] == 0.5
    assert rep["mfe_mediana_r"] == 0.85 and rep["primo_target"] == 0.25
    assert rep["vinti"] == 0.5 and rep["r_medio"] == 0.0 and rep["r_n"] == 4
    ts.print_firma_del_caso(rep)
    out = capsys.readouterr().out
    assert "PAPER CONTRO IL CASO (K4)" in out and "non ricalcolate" in out
    assert "48.5/51.5%" in out and "0.81R" in out and "-0.067" in out
    riga = next(r for r in out.splitlines() if "massimo toccato mediano" in r)
    assert "0.85R" in riga and "0.81R" in riga


def test_main_stampa_i_blocchi_nuovi_in_ordine():
    src = inspect.getsource(ts.main)
    assert "print_conti_in_r(conti_in_r_report(trades))" in src
    assert "print_firma_del_caso(firma_del_caso_report(trades))" in src
    # il blocco in R sta subito dopo le righe in USDT
    assert src.index("print_direction_report(") < src.index("print_conti_in_r(")
    # la regola del 3 ott resta dov'era, invariata nel taglio
    assert ts.DAL_REGOLA_3_OTT == datetime(2026, 9, 27, 19, 40, tzinfo=timezone.utc).timestamp()


# --------------------------------------------------------------------------- #
# lo spazio: il keep per strategia                                             #
# --------------------------------------------------------------------------- #
def test_il_keep_mostra_per_nome_solo_chi_ha_almeno_due_verdetti(capsys):
    def _v(gid, verdetto):
        return {"strategy": gid, "exit_reason": "trailing_stop", "timeframe": ts.settings.ORCHESTRATOR_TIMEFRAME,
                "trailing_verdict": verdetto, "trailing_knockout_atr": 2.0}
    trades = [_v("gen_due", "premature"), _v("gen_due", "protected"),
              _v("gen_uno", "premature"), _v("gen_altro", "protected")]
    ts.print_keep_per_strategia(trades)
    out = capsys.readouterr().out
    assert any(r.strip().startswith("gen_due") for r in out.splitlines())
    assert not any(r.strip().startswith("gen_uno") for r in out.splitlines())
    assert "+ altre 2 strategie con meno verdetti: 2 verdetti, prematuri 1, protetti 1" in out


# --------------------------------------------------------------------------- #
# J15 e K4 nel testo di `controllo`                                            #
# --------------------------------------------------------------------------- #
def _doc(prec=1759300000.0, cambi=None, paper=None):
    return {"meta": {"generato_da": "ops", "generato_at": 1759303600.0, "precedente_at": prec},
            "learning": {"attivo": {"cambiamenti_24h": [] if cambi is None else cambi}},
            "paper": paper if paper is not None else {
                "trades": 100, "win_rate": 0.56,
                "uscite": [{"motivo": "stop_loss", "quota": 0.44}],
                "stop": {"totale": 83, "sbagliati": 39, "quasi": 43, "oltre_primo_tp": 1},
                "mfe": {"mediana_r": 0.87}}}


def test_controllo_dice_che_il_confronto_e_con_un_ora_fa(capsys):
    from scripts import controllo as cli
    cli.stampa(_doc(cambi=["validate 200 → 202"]))
    out = capsys.readouterr().out
    assert "CAMBIAMENTI DEL LEARNING rispetto al controllo di un'ora fa" in out
    assert "STORIA DEL LEARNING" in out and "NON e' il confronto con ieri" in out
    assert "  - validate 200 → 202" in out
    cli.stampa(_doc())
    assert "nessuno nell'ultima ora" in capsys.readouterr().out
    cli.stampa(_doc(prec=None))
    assert "nessun controllo precedente: niente con cui confrontare" in capsys.readouterr().out


def test_controllo_stampa_il_paper_accanto_al_caso(capsys):
    from scripts import controllo as cli
    cli.stampa(_doc())
    out = capsys.readouterr().out
    assert "PAPER CONTRO IL CASO" in out
    riga = next(r for r in out.splitlines() if r.strip().startswith("stop 44%"))
    assert "(caso 46%)" in riga and "47/52%" in riga and "(caso 48.5/51.5%)" in riga
    assert "0.87R (caso 0.81R)" in riga and "vinti 56% (caso 54%)" in riga
    assert "non ricalcolate" in out
    cli.stampa(_doc(paper={"trades": 0}))
    assert "niente da confrontare" in capsys.readouterr().out
