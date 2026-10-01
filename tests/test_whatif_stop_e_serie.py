"""H3 (stop giornaliero) e H4 (freno di serie) come WHAT-IF, 1 ott 2026: sul
paper vero (`trade_stats.rigioca_paper`) e sul portafoglio del motore
(`portafoglio.simula` con `serie_k`). Solo misura: il bot non ha nessuna delle
due regole, e spente non cambiano niente."""
from datetime import datetime, timezone

import scripts.trade_stats as ts
from bot.risk.portafoglio import simula

BARRA = 900.0
T0 = datetime(2026, 9, 21, 8, 0, tzinfo=timezone.utc).timestamp()   # 10:00 in Italia
H = 3600.0
LARGHI = {"max_posizioni": 50, "una_per_coin": True, "tetto_coin_giorno": 0.0,
          "tetto_direzione": 0.0, "cooldown_ore": 0.0, "rischio_per_trade": 0.01,
          "tetto_giorno": 0.0, "netto_r_max": 0.0}


def _p(gid, i, pnl, giorno=0):
    en = T0 + giorno * 86400 + i * H
    return {"strategy": gid, "entry_ts": en, "exit_ts": en + 1800, "pnl": pnl}


# ---- paper ----------------------------------------------------------------- #
def test_rigioco_senza_regole_e_il_paper_vero():
    tr = [_p("g1", i, -15.0) for i in range(4)] + [_p("g2", 5, 10.0)]
    r = ts.rigioca_paper(tr)
    assert r["pnl"] == -50.0 and r["saltati"] == 0 and r["ridotti"] == 0 and r["n"] == 5
    assert r["max_dd_pct"] == 6.0


def test_stop_giornaliero_salta_il_resto_del_giorno_e_riparte_domani():
    tr = ([_p("g1", i, -15.0) for i in range(4)] + [_p("g2", 5, 10.0)]
          + [_p("g2", 0, 7.0, giorno=1)])
    r = ts.rigioca_paper(tr, stop_giorno=0.03)
    # -30 = 3% di 1000 dopo due chiusure: saltano gli altri 3 trade del giorno
    assert r["saltati"] == 3 and r["giorni_fermati"] == 1
    assert r["pnl"] == -23.0


def test_freno_di_serie_per_strategia_e_globale():
    tr = [_p("g1", i, -10.0) for i in range(6)] + [_p("g2", 7, 10.0), _p("g1", 8, 10.0)]
    per_strat = ts.rigioca_paper(tr, serie_k=4)
    # per strategia: il 5o e il 6o di g1, e anche la vincita di g1 (la vincita
    # di g2 non azzera la serie di g1); g2 piena
    assert per_strat["ridotti"] == 3
    assert per_strat["pnl"] == -40 - 10 + 10 + 5
    glob = ts.rigioca_paper(tr, serie_k=4, serie_globale=True)
    # del bot: il 5o e il 6o di g1 e la vincita di g2, che azzera: g1 piena
    assert glob["ridotti"] == 3
    assert glob["pnl"] == -40 - 10 + 5 + 10


def test_un_trade_ancora_aperto_non_conta_nella_serie():
    a = {"strategy": "g", "entry_ts": T0, "exit_ts": T0 + 10 * H, "pnl": -5.0}
    tr = [a] + [_p("g", i + 1, -5.0) for i in range(4)]
    # al 5o ingresso ci sono solo 3 perdite CHIUSE (la prima chiude dopo)
    assert ts.rigioca_paper(tr, serie_k=4)["ridotti"] == 0


def test_la_stampa_dice_che_e_solo_misura(capsys):
    ts.print_rigioco_paper([_p("g1", i, -15.0) for i in range(4)])
    out = capsys.readouterr().out
    assert "Solo misura" in out and "stop giornaliero 3%" in out and "del bot" in out
    ts.print_rigioco_paper([])
    assert "nessun trade" in capsys.readouterr().out


# ---- portafoglio del motore -------------------------------------------------- #
def _t(sym, entry, pnl_pct, strategy="gen_a"):
    return {"symbol": sym, "strategy": strategy, "direction": "long",
            "entry_ts": entry, "bars_held": 1, "pnl_pct": pnl_pct, "stop_pct": 0.01}


def test_simula_serie_spenta_non_cambia_niente():
    tr = [_t(f"C{i}", T0 + i * 2 * BARRA, -0.01) for i in range(6)]
    a = simula(tr, 10_000, LARGHI, secondi_barra=BARRA)
    b = simula(tr, 10_000, {**LARGHI, "serie_k": 0}, secondi_barra=BARRA)
    assert a["pnl_totale"] == b["pnl_totale"] and b["ridotti_serie"] == 0


def test_simula_serie_dimezza_dopo_k_perdite_e_si_azzera_alla_vincita():
    tr = ([_t(f"C{i}", T0 + i * 2 * BARRA, -0.01) for i in range(5)]
          + [_t("W", T0 + 10 * 2 * BARRA, 0.01), _t("Z", T0 + 11 * 2 * BARRA, -0.01)])
    out = simula(tr, 10_000, {**LARGHI, "serie_k": 4}, secondi_barra=BARRA)
    # il 5o (dopo 4 perdite) e la vincita (dopo 5) a meta'; dopo la vincita si riparte
    assert out["ridotti_serie"] == 2


def test_simula_serie_globale_conta_tutte_le_strategie():
    tr = [_t(f"C{i}", T0 + i * 2 * BARRA, -0.01, strategy=f"g{i}") for i in range(5)]
    per_strat = simula(tr, 10_000, {**LARGHI, "serie_k": 4}, secondi_barra=BARRA)
    glob = simula(tr, 10_000, {**LARGHI, "serie_k": 4, "serie_globale": True},
                  secondi_barra=BARRA)
    assert per_strat["ridotti_serie"] == 0 and glob["ridotti_serie"] == 1


def test_portafoglio_stampa_i_whatif_singoli(capsys):
    import scripts.portafoglio_backtest as pb
    tr = [_t(f"C{i}", T0 + i * 2 * BARRA, -0.01) for i in range(6)]
    base = simula(tr, 10_000, LARGHI, secondi_barra=BARRA)
    pb.stampa_whatif_singoli(tr, 10_000, LARGHI, base, BARRA, (T0, T0 + 86400))
    out = capsys.readouterr().out
    assert "UNO ALLA VOLTA" in out and "stop giornaliero 3%" in out and "del conto" in out
