"""BACKTEST DI PORTAFOGLIO — la simulazione pura con trade sintetici.

24 set 2026: il gate valida una coppia alla volta con 10.000$ fissi; il paper e'
la prima volta in cui le coppie validate girano insieme con i limiti veri del
conto. Qui si verifica che `simula` applichi quei limiti come il bot: una
posizione per coin, tetto di posizioni, tetto di perdita per coin al giorno,
tetto di rischio per direzione, e che il PnL in valuta segua l'equity corrente.
"""
from datetime import datetime, timezone

from bot.risk.portafoglio import simula

BARRA = 900.0  # 15 minuti
T0 = datetime(2026, 9, 21, 10, 0, tzinfo=timezone.utc).timestamp()

#: limiti "larghi" di partenza: ogni test stringe SOLO quello che vuole misurare
LARGHI = {"max_posizioni": 50, "una_per_coin": True, "tetto_coin_giorno": 0.0,
          "tetto_direzione": 0.0, "cooldown_ore": 0.0, "rischio_per_trade": 0.01}


def _t(sym, direction, entry, bars=4, pnl_pct=-0.01, stop_pct=0.01, strategy="gen_a"):
    return {"symbol": sym, "strategy": strategy, "direction": direction,
            "entry_ts": entry, "bars_held": bars, "pnl_pct": pnl_pct,
            "stop_pct": stop_pct}


def _contabilita_chiusa(out):
    """Ogni trade candidato e' o aperto o saltato con un motivo: mai perso."""
    assert out["n_aperti"] + sum(out["saltati"].values()) == out["n_candidati"]


def test_una_per_coin_e_max_posizioni():
    """Due trade sulla stessa coin che si sovrappongono: il secondo salta. Con
    max 2 posizioni, il terzo su una terza coin salta."""
    tr = [_t("AAA", "long", T0, bars=8),
          _t("AAA", "long", T0 + BARRA, bars=8, strategy="gen_b"),   # AAA aperta
          _t("BBB", "long", T0 + BARRA),
          _t("CCC", "long", T0 + 2 * BARRA)]                            # 2 aperte
    out = simula(tr, 10_000, {**LARGHI, "max_posizioni": 2}, secondi_barra=BARRA)
    assert out["n_aperti"] == 2
    assert out["saltati"]["coin_gia_aperta"] == 1
    assert out["saltati"]["max_posizioni"] == 1
    assert out["posizioni_contemporanee"]["max"] == 2
    _contabilita_chiusa(out)


def test_tetto_per_direzione_blocca_il_quarto_short_non_il_long():
    """Tre short da 1% aperti = 3% di rischio: con tetto 3% il quarto short non
    entra; un long nello stesso istante si', perche' la direzione e' un'altra."""
    tr = [_t("A", "short", T0, bars=8), _t("B", "short", T0 + BARRA, bars=8),
          _t("C", "short", T0 + 2 * BARRA, bars=8),
          _t("D", "short", T0 + 3 * BARRA, bars=8),
          _t("E", "long", T0 + 3 * BARRA, bars=8)]
    out = simula(tr, 10_000, {**LARGHI, "tetto_direzione": 0.03}, secondi_barra=BARRA)
    assert out["n_aperti"] == 4
    assert out["saltati"]["tetto_direzione"] == 1
    assert out["saltati_direzione"] == {"long": 0, "short": 1}
    assert out["stessa_direzione_max"] == 3
    assert out["per_direzione"]["long"]["n"] == 1
    _contabilita_chiusa(out)


def test_tetto_per_coin_al_giorno_chiude_fino_a_mezzanotte():
    """Due stop da 1R sulla stessa coin (-2% ≥ 1,5%): il terzo trade del giorno
    non si apre; il giorno dopo la coin riparte."""
    domani = T0 + 86_400
    tr = [_t("X", "short", T0), _t("X", "short", T0 + 5 * BARRA),
          _t("X", "short", T0 + 10 * BARRA),                    # bloccato
          _t("X", "short", domani, pnl_pct=0.02)]               # riapre
    out = simula(tr, 10_000, {**LARGHI, "tetto_coin_giorno": 0.015}, secondi_barra=BARRA)
    assert out["n_aperti"] == 3
    assert out["saltati"]["tetto_coin_giorno"] == 1
    # dopo il primo stop solo (-1%) la coin era ancora operabile
    out1 = simula(tr[:2], 10_000, {**LARGHI, "tetto_coin_giorno": 0.015}, secondi_barra=BARRA)
    assert out1["n_aperti"] == 2


def test_pnl_in_valuta_segue_l_equity_corrente():
    """+2R su 10.000 = +200 (1% × 2); poi -1R su 10.200 = -102: l'equity si
    aggiorna alla chiusura e il rischio del trade dopo si legge su quella."""
    tr = [_t("A", "long", T0, pnl_pct=0.02, stop_pct=0.01),
          _t("B", "long", T0 + 10 * BARRA, pnl_pct=-0.01, stop_pct=0.01)]
    out = simula(tr, 10_000, LARGHI, secondi_barra=BARRA)
    assert out["equity_finale"] == 10_098.0
    assert out["pnl_totale"] == 98.0
    assert out["per_direzione"]["long"] == {"n": 2, "pnl": 98.0}


def test_giorni_utile_perdita_e_drawdown_su_sequenza_nota():
    """Quattro giorni: +2R, -1R, -1R, +1R. Due giorni in utile, due in perdita;
    il drawdown e' dal picco 10.200 al minimo 9.997,02 = 1,99%."""
    g = 86_400
    tr = [_t("A", "long", T0, pnl_pct=0.02),
          _t("A", "long", T0 + g, pnl_pct=-0.01),
          _t("A", "long", T0 + 2 * g, pnl_pct=-0.01),
          _t("A", "long", T0 + 3 * g, pnl_pct=0.01)]
    out = simula(tr, 10_000, LARGHI, secondi_barra=BARRA)
    assert out["giorni_utile"] == 2 and out["giorni_perdita"] == 2
    assert out["max_drawdown_pct"] == 1.99
    assert len(out["pnl_per_giorno"]) == 4
    assert out["pnl_per_giorno"]["2026-09-21"] == 200.0
    # curva a fine giornata: quattro giorni, l'ultimo punto e' l'equity finale
    assert len(out["curva"]) == 4
    assert out["curva"][-1][1] == out["equity_finale"]
    assert out["trade_al_giorno"] == {"min": 1, "media": 1.0, "max": 1}


def test_trade_senza_stop_viene_scartato_e_contato():
    tr = [_t("A", "long", T0, pnl_pct=0.02, stop_pct=0.0),
          {**_t("B", "long", T0 + BARRA), "stop_pct": None},
          _t("C", "long", T0 + 2 * BARRA, pnl_pct=0.01)]
    out = simula(tr, 10_000, LARGHI, secondi_barra=BARRA)
    assert out["saltati"]["senza_stop"] == 2
    assert out["n_aperti"] == 1
    assert out["equity_finale"] == 10_100.0
    _contabilita_chiusa(out)


def test_tetto_direzione_zero_non_blocca_nulla():
    tr = [_t(f"C{i}", "short", T0 + i * BARRA, bars=20) for i in range(6)]
    out = simula(tr, 10_000, {**LARGHI, "tetto_direzione": 0.0}, secondi_barra=BARRA)
    assert out["n_aperti"] == 6
    assert out["saltati"]["tetto_direzione"] == 0
    assert out["stessa_direzione_max"] == 6
    assert out["quota_contemporanee_stessa_direzione"] == 1.0


def test_cooldown_dopo_uno_stop_in_perdita():
    """Stop su X alle 10:00 chiuso dopo 4 barre (11:00): con cooldown di un'ora
    X non riapre alle 11:30, riapre alle 12:15."""
    tr = [_t("X", "long", T0, bars=4),
          _t("X", "long", T0 + 6 * BARRA),                  # 11:30, in cooldown
          _t("X", "long", T0 + 9 * BARRA, pnl_pct=0.01)]    # 12:15, ok
    out = simula(tr, 10_000, {**LARGHI, "cooldown_ore": 1.0}, secondi_barra=BARRA)
    assert out["saltati"]["cooldown"] == 1
    assert out["n_aperti"] == 2
