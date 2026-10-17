"""Test del motore di backtest (research/src/motore.py), con esempi calcolati a mano.

Ogni test riporta nei commenti il conto fatto a mano, cosi' chi legge puo'
rifarlo senza eseguire il codice. Le candele hanno durata 1 ora: ts = i * ORA,
close_ts = ts + ORA - 1 (stile Binance, chiusura inclusa).
"""

import pytest

from research.src import motore
from research.src.motore import Candela, Parametri, Segnale

ORA = 3_600_000


def candela(i: int, o: float, h: float, l: float, c: float, volume: float = 1.0) -> Candela:
    return Candela(ts=i * ORA, open=o, high=h, low=l, close=c, volume=volume, close_ts=i * ORA + ORA - 1)


def senza_costi(**kw) -> Parametri:
    """Parametri con costi azzerati: isolano la logica di prezzo dal conto dei costi."""
    base = dict(commissione_per_lato=0.0, slippage_per_lato=0.0)
    base.update(kw)
    return Parametri(**base)


def strategia_segnale_alla_barra(k: int, segnale: Segnale):
    """Strategia che emette ``segnale`` solo alla chiusura della barra k."""

    def strategia(storia, posizione):
        if posizione is None and len(storia) - 1 == k:
            return segnale
        return None

    return strategia


# ---------------------------------------------------------------------------
# (1) ingresso all'apertura della barra successiva, mai lookahead
# ---------------------------------------------------------------------------


def test_ingresso_barra_successiva_e_nessun_lookahead():
    candele = [
        candela(0, 100, 101, 99, 100),
        candela(1, 105, 106, 104, 105),  # l'ingresso deve avvenire QUI, a 105
        candela(2, 105, 107, 104, 106),
        candela(3, 106, 108, 105, 107),
    ]
    viste = []  # (numero barre viste, ts dell'ultima barra vista) per ogni chiamata

    def strategia(storia, posizione):
        viste.append((len(storia), storia[-1].ts))
        if posizione is None and len(storia) == 1:
            return Segnale("long", stop=90.0, target=None)
        return None

    ris = motore.esegui(candele, None, None, [], strategia, senza_costi())

    # La strategia alla barra i vede esattamente i+1 barre e l'ultima e' la barra i:
    # mai la barra i+1. L'ultima barra non chiama la strategia (chiude per fine dati).
    assert viste == [(1, 0), (2, ORA), (3, 2 * ORA)]
    assert len(ris.trades) == 1
    t = ris.trades[0]
    assert t.ts_entrata == ORA  # apertura della barra 1, non la barra 0 del segnale
    assert t.entrata == 105.0  # l'open della barra 1, non il close della barra 0 (100)


# ---------------------------------------------------------------------------
# (2) stop e target nella stessa barra; gap in apertura oltre lo stop
# ---------------------------------------------------------------------------


def test_stop_e_target_stessa_barra_vince_lo_stop_o_il_target_secondo_parametro():
    # Entrata 100 all'open della barra 1; stop 99, target 102. La barra 1 tocca
    # sia 98 (sotto lo stop) sia 103 (sopra il target).
    candele = [candela(0, 100, 101, 99.5, 100), candela(1, 100, 103, 98, 101), candela(2, 101, 102, 100, 101)]
    strategia = strategia_segnale_alla_barra(0, Segnale("long", stop=99.0, target=102.0))

    ris = motore.esegui(candele, None, None, [], strategia, senza_costi(riempimento_intrabarra="stop_prima"))
    assert ris.trades[0].esito == "stop"
    assert ris.trades[0].uscita == 99.0
    # Conto a mano: quantita = 1000 * 0.01 / (100 - 99) = 10; pnl = 10 * (99 - 100) = -10; R = -10 / 10 = -1
    assert ris.trades[0].pnl == pytest.approx(-10.0)
    assert ris.trades[0].r == pytest.approx(-1.0)

    ris2 = motore.esegui(candele, None, None, [], strategia, senza_costi(riempimento_intrabarra="target_prima"))
    assert ris2.trades[0].esito == "target"
    assert ris2.trades[0].uscita == 102.0
    # pnl = 10 * (102 - 100) = +20; R = 20 / 10 = +2
    assert ris2.trades[0].pnl == pytest.approx(20.0)
    assert ris2.trades[0].r == pytest.approx(2.0)


def test_gap_in_apertura_oltre_lo_stop_riempie_all_open():
    # Entrata 100 (barra 1), stop 99. La barra 2 apre a 97, gia' sotto lo stop:
    # lo stop si riempie a 97 (peggio di 99), non a 99.
    candele = [
        candela(0, 100, 101, 99.5, 100),
        candela(1, 100, 101, 99.5, 100.5),
        candela(2, 97, 98, 96, 97),
        candela(3, 97, 98, 96, 97),
    ]
    strategia = strategia_segnale_alla_barra(0, Segnale("long", stop=99.0, target=110.0))
    ris = motore.esegui(candele, None, None, [], strategia, senza_costi())
    t = ris.trades[0]
    assert t.esito == "stop"
    assert t.uscita == 97.0
    # Uscita dentro la barra 2: si sa solo che e' avvenuta entro la sua chiusura.
    assert t.ts_uscita == candele[2].close_ts
    # quantita 10; pnl = 10 * (97 - 100) = -30; R = -30 / 10 = -3
    assert t.pnl == pytest.approx(-30.0)
    assert t.r == pytest.approx(-3.0)


def test_gap_in_apertura_oltre_il_target_riempie_all_open():
    # Short entrata 100, target 95; la barra 2 apre a 93 (oltre il target): uscita a 93.
    candele = [
        candela(0, 100, 101, 99.5, 100),
        candela(1, 100, 100.5, 99.5, 100),
        candela(2, 93, 94, 92, 93),
        candela(3, 93, 94, 92, 93),
    ]
    strategia = strategia_segnale_alla_barra(0, Segnale("short", stop=101.0, target=95.0))
    ris = motore.esegui(candele, None, None, [], strategia, senza_costi())
    assert ris.trades[0].esito == "target"
    assert ris.trades[0].uscita == 93.0


# ---------------------------------------------------------------------------
# (3) funding
# ---------------------------------------------------------------------------


def test_funding_long_con_tasso_positivo_paga():
    # Long entrata 100 (barra 1), quantita = 1000 * 0.01 / (100 - 99) = 10.
    # Settlement all'apertura della barra 2 (ts = 2 ore), tasso +0.001, mark open 100:
    # funding = 0.001 * 10 * 100 = 1.0 pagato. La posizione resta aperta fino a fine dati
    # (close finale 100): pnl_lordo = 0, pnl = -1.0.
    candele = [candela(0, 100, 101, 99.5, 100), candela(1, 100, 101, 99.5, 100), candela(2, 100, 101, 99.5, 100), candela(3, 100, 101, 99.5, 100)]
    strategia = strategia_segnale_alla_barra(0, Segnale("long", stop=99.0, target=None))
    ris = motore.esegui(candele, None, None, [(2 * ORA, 0.001)], strategia, senza_costi())
    t = ris.trades[0]
    assert t.esito == "fine_dati"
    assert t.funding_pagato == pytest.approx(1.0)
    assert t.pnl == pytest.approx(-1.0)

    # Tasso negativo: il long INCASSA 1.0 (funding_pagato negativo).
    ris2 = motore.esegui(candele, None, None, [(2 * ORA, -0.001)], strategia, senza_costi())
    assert ris2.trades[0].funding_pagato == pytest.approx(-1.0)
    assert ris2.trades[0].pnl == pytest.approx(+1.0)

    # Short con tasso positivo incassa. Stop a 102 (mai toccato): quantita = 10 / 2 = 5;
    # funding = -(0.001 * 5 * 100) = -0.5 (negativo = incasso).
    strategia_short = strategia_segnale_alla_barra(0, Segnale("short", stop=102.0, target=None))
    ris3 = motore.esegui(candele, None, None, [(2 * ORA, 0.001)], strategia_short, senza_costi())
    assert ris3.trades[0].quantita == pytest.approx(5.0)
    assert ris3.trades[0].funding_pagato == pytest.approx(-0.5)


def test_funding_nella_candela_di_chiusura_si_conta_solo_se_costo():
    # Long entrata 100 (barra 1), stop 99, quantita 10. Lo stop scatta nella barra 2,
    # dove cade anche un settlement (ts = 2 ore, mark open 100).
    candele = [candela(0, 100, 101, 99.5, 100), candela(1, 100, 101, 99.5, 100), candela(2, 100, 101, 98, 99), candela(3, 99, 100, 98, 99)]
    strategia = strategia_segnale_alla_barra(0, Segnale("long", stop=99.0, target=None))

    # Caso 1: tasso +0.001 -> costo per il long: si conta. funding = 1.0;
    # pnl = 10 * (99 - 100) - 1.0 = -11.0
    ris = motore.esegui(candele, None, None, [(2 * ORA, 0.001)], strategia, senza_costi())
    assert ris.trades[0].esito == "stop"
    assert ris.trades[0].funding_pagato == pytest.approx(1.0)
    assert ris.trades[0].pnl == pytest.approx(-11.0)

    # Caso 2: tasso -0.001 -> sarebbe un incasso per il long: NON si conta. pnl = -10.0
    ris2 = motore.esegui(candele, None, None, [(2 * ORA, -0.001)], strategia, senza_costi())
    assert ris2.trades[0].esito == "stop"
    assert ris2.trades[0].funding_pagato == pytest.approx(0.0)
    assert ris2.trades[0].pnl == pytest.approx(-10.0)


# ---------------------------------------------------------------------------
# (4) liquidazione
# ---------------------------------------------------------------------------


def test_prezzo_liquidazione_isolated_leva_2_long_e_short():
    # Capitale 1000, rischio 1%, leva_max 2, mmr 0.01, senza slippage.
    # Long entrata 100, stop 99.5: quantita = 10 / 0.5 = 20; notional = 2000 = capitale * 2
    # -> non ridotto (non supera il tetto), leva effettiva = 2.
    # liq long = 100 * (1 - 1/2 + 0.01) = 100 * 0.51 = 51
    # Distanza stop 0.5 <= 0.8 * 49 = 39.2 -> nessuna violazione.
    candele = [candela(0, 100, 101, 99.6, 100), candela(1, 100, 101, 99.6, 100), candela(2, 100, 101, 99.6, 100)]
    p = senza_costi(leva_max=2.0, tasso_margine_mantenimento=0.01)
    ris = motore.esegui(candele, None, None, [], strategia_segnale_alla_barra(0, Segnale("long", stop=99.5)), p)
    t = ris.trades[0]
    assert t.quantita == pytest.approx(20.0)
    assert t.ridotto is False
    assert t.leva_effettiva == pytest.approx(2.0)
    assert t.prezzo_liquidazione == pytest.approx(51.0)
    assert t.violazione_liquidazione is False

    # Short entrata 100, stop 100.5: quantita 20, leva 2.
    # liq short = 100 * (1 + 1/2 - 0.01) = 100 * 1.49 = 149
    ris2 = motore.esegui(candele, None, None, [], strategia_segnale_alla_barra(0, Segnale("short", stop=100.5)), p)
    assert ris2.trades[0].prezzo_liquidazione == pytest.approx(149.0)
    assert ris2.trades[0].violazione_liquidazione is False

    # Verifica diretta della formula pura, anche in cross: leva_cross = notional / capitale = 0.5
    # -> long liq = 100 * (1 - 2 + 0.01) < 0 -> azzerato (mai liquidato).
    assert motore.prezzo_liquidazione(100.0, "long", 0.5, p) == 0.0


def test_violazione_liquidazione_contata_quando_lo_stop_supera_0_8_della_distanza():
    # Rischio 95%, capitale 1000, leva_max 2, mmr 0.01. Long entrata 100, stop 55:
    # quantita = 950 / 45 = 21.11; notional 2111 > 2000 -> ridotta a 20 (ridotto), leva 2.
    # liq = 51, distanza liquidazione 49, soglia 0.8 * 49 = 39.2; distanza stop 45 > 39.2 -> violazione.
    candele = [candela(0, 100, 101, 99.6, 100), candela(1, 100, 101, 99.6, 100), candela(2, 100, 101, 99.6, 100)]
    p = senza_costi(rischio_per_trade=0.95, leva_max=2.0)
    ris = motore.esegui(candele, None, None, [], strategia_segnale_alla_barra(0, Segnale("long", stop=55.0)), p)
    t = ris.trades[0]
    assert t.ridotto is True
    assert t.quantita == pytest.approx(20.0)
    assert t.prezzo_liquidazione == pytest.approx(51.0)
    assert t.violazione_liquidazione is True
    m = ris.metriche()
    assert m["n_violazioni_liquidazione"] == 1
    assert m["n_ridotti"] == 1


def test_chiusura_per_liquidazione_se_il_mark_tocca_il_prezzo_prima_dello_stop():
    # Long entrata 100, stop 99.5, quantita 20, liq 51 (vedi test sopra).
    # Nella barra 2 la serie dei segnali (e dello stop) non scende sotto 99.6, ma il
    # mark price scende a 50 < 51: la posizione si chiude per liquidazione a 51.
    # pnl = 20 * (51 - 100) = -980; rischio iniziale = 20 * 0.5 = 10; R = -98.
    candele = [candela(0, 100, 101, 99.6, 100), candela(1, 100, 101, 99.6, 100), candela(2, 100, 101, 99.6, 100), candela(3, 100, 101, 99.6, 100)]
    mark = [candela(0, 100, 101, 99.6, 100), candela(1, 100, 101, 99.6, 100), candela(2, 100, 101, 50, 60), candela(3, 60, 61, 59, 60)]
    p = senza_costi(leva_max=2.0)
    ris = motore.esegui(candele, None, mark, [], strategia_segnale_alla_barra(0, Segnale("long", stop=99.5)), p)
    t = ris.trades[0]
    assert t.esito == "liquidazione"
    assert t.uscita == pytest.approx(51.0)
    assert t.ts_uscita == candele[2].close_ts  # avvenuta dentro la barra 2
    assert t.pnl == pytest.approx(-980.0)
    assert t.r == pytest.approx(-98.0)
    assert ris.capitale_finale == pytest.approx(20.0)

    # Se invece nella stessa barra anche la serie stop tocca lo stop (piu' vicino della
    # liquidazione), vince lo stop: il prezzo passa prima da 99.5.
    candele_con_stop = candele[:2] + [candela(2, 100, 101, 99, 99.2), candela(3, 99, 100, 98, 99)]
    ris2 = motore.esegui(candele_con_stop, None, mark, [], strategia_segnale_alla_barra(0, Segnale("long", stop=99.5)), p)
    assert ris2.trades[0].esito == "stop"
    assert ris2.trades[0].uscita == pytest.approx(99.5)


# ---------------------------------------------------------------------------
# (5) R e pnl con costi, al centesimo
# ---------------------------------------------------------------------------


def test_r_e_pnl_con_commissioni_e_slippage_al_centesimo():
    # Capitale 1000, rischio 1%, commissione 0.0005, slippage 0.0002.
    # Barra 1 apre a 100: quantita = 1000 * 0.01 / (100 - 99) = 10 (dimensionata sull'open).
    # Entrata vera = 100 * (1 + 0.0002) = 100.02; rischio iniziale = 10 * (100.02 - 99) = 10.2.
    # Target 102 toccato nella barra 2 senza gap: uscita vera = 102 * (1 - 0.0002) = 101.9796.
    # pnl_lordo (prezzi di riferimento) = 10 * (102 - 100) = 20.00
    # commissioni = 0.0005 * 10 * (100.02 + 101.9796) = 0.005 * 201.9996 = 1.009998
    # slippage = 10 * (0.02 + 0.0204) = 0.404
    # pnl = 20 - 1.009998 - 0.404 = 18.586002 -> 18.59 al centesimo; R = 18.586002 / 10.2 = 1.8222
    candele = [candela(0, 100, 101, 99.5, 100), candela(1, 100, 101, 99.5, 100.5), candela(2, 100.5, 102.5, 100, 102), candela(3, 102, 103, 101, 102)]
    p = Parametri(commissione_per_lato=0.0005, slippage_per_lato=0.0002, rischio_per_trade=0.01, capitale_iniziale=1000.0)
    ris = motore.esegui(candele, None, None, [], strategia_segnale_alla_barra(0, Segnale("long", stop=99.0, target=102.0)), p)
    t = ris.trades[0]
    assert t.esito == "target"
    assert t.entrata == pytest.approx(100.02)
    assert t.uscita == pytest.approx(101.9796)
    assert t.quantita == pytest.approx(10.0)
    assert t.rischio_iniziale == pytest.approx(10.2)
    assert t.pnl_lordo == pytest.approx(20.0)
    assert t.commissioni == pytest.approx(1.009998)
    assert t.slippage_costo == pytest.approx(0.404)
    assert t.pnl == pytest.approx(18.586002)
    assert t.pnl == pytest.approx(18.59, abs=0.005)
    assert t.r == pytest.approx(18.586002 / 10.2)
    # Verifica incrociata: pnl = quantita * (uscita vera - entrata vera) - commissioni
    assert t.pnl == pytest.approx(10 * (101.9796 - 100.02) - t.commissioni)
    m = ris.metriche()
    assert m["n_trade"] == 1 and m["vinti"] == 1 and m["win_rate"] == 1.0
    assert m["pnl_totale"] == pytest.approx(t.pnl)
    assert m["rendimento_totale"] == pytest.approx(t.pnl / 1000.0)
    assert m["costi_totali"] == pytest.approx(t.commissioni + t.slippage_costo)
    assert m["per_direzione"]["long"]["n"] == 1 and m["per_direzione"]["short"]["n"] == 0


# ---------------------------------------------------------------------------
# (6) trade ridotto per il tetto di leva
# ---------------------------------------------------------------------------


def test_trade_ridotto_al_tetto_di_leva():
    # Capitale 1000, rischio 1%, leva_max 2. Long entrata 100, stop 99.9:
    # quantita piena = 10 / 0.1 = 100 -> notional 10000 > 2000 -> ridotta a 2000 / 100 = 20.
    # rischio iniziale = 20 * 0.1 = 2.0 (non piu' 10). Stop a 99.9 nella barra 2: pnl = 20 * -0.1 = -2.0, R = -1.
    candele = [candela(0, 100, 101, 99.95, 100), candela(1, 100, 101, 99.95, 100), candela(2, 100, 101, 99.8, 99.9), candela(3, 99.9, 100, 99.8, 99.9)]
    ris = motore.esegui(candele, None, None, [], strategia_segnale_alla_barra(0, Segnale("long", stop=99.9)), senza_costi(leva_max=2.0))
    t = ris.trades[0]
    assert t.ridotto is True
    assert t.quantita == pytest.approx(20.0)
    assert t.rischio_iniziale == pytest.approx(2.0)
    assert t.pnl == pytest.approx(-2.0)
    assert t.r == pytest.approx(-1.0)
    assert ris.metriche()["n_ridotti"] == 1


# ---------------------------------------------------------------------------
# (7) ritardo di una barra
# ---------------------------------------------------------------------------


def test_ritardo_barre_sposta_l_ingresso_di_una_barra():
    candele = [candela(0, 100, 101, 99, 100), candela(1, 101, 102, 100, 101), candela(2, 103, 104, 102, 103), candela(3, 103, 104, 102, 103)]
    strategia = strategia_segnale_alla_barra(0, Segnale("long", stop=90.0))
    normale = motore.esegui(candele, None, None, [], strategia, senza_costi(ritardo_barre=0))
    ritardato = motore.esegui(candele, None, None, [], strategia, senza_costi(ritardo_barre=1))
    assert normale.trades[0].ts_entrata == ORA and normale.trades[0].entrata == 101.0
    assert ritardato.trades[0].ts_entrata == 2 * ORA and ritardato.trades[0].entrata == 103.0


# ---------------------------------------------------------------------------
# (8) buy and hold
# ---------------------------------------------------------------------------


def test_buy_and_hold_su_serie_nota():
    # Primo open 100, ultimo close 110, commissione 0.0005, slippage 0.0002.
    # entrata = 100.02; uscita = 110 * 0.9998 = 109.978
    # commissioni = 0.0005 * (100.02 + 109.978) = 0.104999
    # pnl = 109.978 - 100.02 - 0.104999 = 9.853001; rendimento = 9.853001 / 100.02 = 0.098510
    candele = [candela(0, 100, 101, 99, 100), candela(1, 100, 112, 99, 105), candela(2, 105, 111, 104, 110)]
    p = Parametri(commissione_per_lato=0.0005, slippage_per_lato=0.0002)
    assert motore.buy_and_hold(candele, p) == pytest.approx(9.853001 / 100.02, abs=1e-6)
    # Senza costi: +10%; short senza costi: -10%.
    assert motore.buy_and_hold(candele, senza_costi()) == pytest.approx(0.10)
    assert motore.buy_and_hold(candele, senza_costi(), direzione="short") == pytest.approx(-0.10)
    # Short con costi: entrata = 99.98, uscita = 110.022; commissioni = 0.0005 * 210.002 = 0.105001
    # pnl = 99.98 - 110.022 - 0.105001 = -10.147001; rendimento = -10.147001 / 99.98
    assert motore.buy_and_hold(candele, p, direzione="short") == pytest.approx(-10.147001 / 99.98, abs=1e-6)


# ---------------------------------------------------------------------------
# (9) ricucitura di due contratti
# ---------------------------------------------------------------------------


def test_ricuci_serie_riscala_e_dichiara_il_punto():
    # Contratto "1000X" (prezzi x1000, quantita /1000) seguito dal contratto "X":
    # fattore_prezzo 1/1000, fattore_quantita 1000. La barra 2 della prima serie si
    # sovrappone alla seconda e si scarta; la cucitura e' la prima barra della seconda.
    prima = [candela(0, 2000, 2100, 1900, 2050, volume=5), candela(1, 2050, 2200, 2000, 2100, volume=6), candela(2, 9999, 9999, 9999, 9999, volume=1)]
    dopo = [candela(2, 2.1, 2.2, 2.0, 2.15, volume=7000), candela(3, 2.15, 2.3, 2.1, 2.2, volume=8000)]
    unite, ts_cucitura = motore.ricuci_serie(prima, dopo, fattore_prezzo=1 / 1000, fattore_quantita=1000)
    assert ts_cucitura == 2 * ORA
    assert [c.ts for c in unite] == [0, ORA, 2 * ORA, 3 * ORA]
    assert unite[0].open == pytest.approx(2.0) and unite[0].high == pytest.approx(2.1) and unite[0].low == pytest.approx(1.9) and unite[0].close == pytest.approx(2.05)
    assert unite[0].volume == pytest.approx(5000)
    assert unite[1].close == pytest.approx(2.1) and unite[1].volume == pytest.approx(6000)
    assert unite[2] == dopo[0] and unite[3] == dopo[1]


# ---------------------------------------------------------------------------
# (10) fine dei dati
# ---------------------------------------------------------------------------


def test_fine_dati_chiude_la_posizione_aperta_all_ultimo_close():
    # Long entrata 100 (barra 1), nessuno stop/target toccato; ultimo close 104.
    # quantita 10 (stop 99); pnl = 10 * (104 - 100) = 40; R = 4.
    candele = [candela(0, 100, 101, 99.5, 100), candela(1, 100, 101, 99.5, 101), candela(2, 101, 105, 100, 104)]
    ris = motore.esegui(candele, None, None, [], strategia_segnale_alla_barra(0, Segnale("long", stop=99.0, target=120.0)), senza_costi())
    t = ris.trades[0]
    assert t.esito == "fine_dati"
    assert t.uscita == 104.0
    assert t.ts_uscita == candele[-1].close_ts
    assert t.pnl == pytest.approx(40.0) and t.r == pytest.approx(4.0)
    assert ris.capitale_finale == pytest.approx(1040.0)
    assert ris.curva_capitale[0] == (0, 1000.0)
    assert ris.curva_capitale[-1] == (candele[-1].close_ts, pytest.approx(1040.0))


# ---------------------------------------------------------------------------
# (11) costi doppi
# ---------------------------------------------------------------------------


def test_costi_doppi_peggiorano_il_pnl_del_doppio_di_commissioni_e_slippage():
    # Stesso trade del test (5). Con moltiplicatore 2: commissione 0.001, slippage 0.0004.
    # Quantita sempre 10 (dimensionata sull'open). Entrata 100.04, uscita 101.9592.
    # commissioni = 0.001 * 10 * (100.04 + 101.9592) = 2.019992 (normale: 1.009998, x2 = 2.019996)
    # slippage = 10 * (0.04 + 0.0408) = 0.808 (normale 0.404, esattamente il doppio)
    # pnl = 20 - 2.019992 - 0.808 = 17.172008; pnl_lordo - 2 * (1.009998 + 0.404) = 17.172004:
    # il residuo di 4e-6 viene dal notional del riempimento, che cambia di pochissimo con lo slippage.
    candele = [candela(0, 100, 101, 99.5, 100), candela(1, 100, 101, 99.5, 100.5), candela(2, 100.5, 102.5, 100, 102), candela(3, 102, 103, 101, 102)]
    strategia = strategia_segnale_alla_barra(0, Segnale("long", stop=99.0, target=102.0))
    normale = motore.esegui(candele, None, None, [], strategia, Parametri(moltiplicatore_costi=1.0)).trades[0]
    doppio = motore.esegui(candele, None, None, [], strategia, Parametri(moltiplicatore_costi=2.0)).trades[0]
    assert doppio.entrata == pytest.approx(100.04) and doppio.uscita == pytest.approx(102 * (1 - 0.0004))
    assert doppio.slippage_costo == pytest.approx(2 * normale.slippage_costo, rel=1e-6)
    assert doppio.commissioni == pytest.approx(2.019992)
    assert doppio.commissioni == pytest.approx(2 * normale.commissioni, rel=1e-4)
    assert doppio.pnl == pytest.approx(17.172008)
    assert doppio.pnl == pytest.approx(doppio.pnl_lordo - 2 * (normale.commissioni + normale.slippage_costo), abs=1e-4)
    assert doppio.pnl < normale.pnl


# ---------------------------------------------------------------------------
# Altri comportamenti richiesti dall'API
# ---------------------------------------------------------------------------


def test_chiudi_esce_all_apertura_della_barra_successiva():
    # Long entrata 100 (barra 1). Alla chiusura della barra 2 la strategia dice "chiudi":
    # uscita all'open della barra 3 (= 103), esito "segnale". pnl = 10 * 3 = 30.
    candele = [candela(0, 100, 101, 99.5, 100), candela(1, 100, 101, 99.5, 101), candela(2, 101, 102, 100, 102), candela(3, 103, 104, 102, 103), candela(4, 103, 104, 102, 103)]

    def strategia(storia, posizione):
        if posizione is None and len(storia) == 1:
            return Segnale("long", stop=99.0)
        if posizione is not None and len(storia) == 3:
            return "chiudi"
        return None

    ris = motore.esegui(candele, None, None, [], strategia, senza_costi())
    t = ris.trades[0]
    assert t.esito == "segnale" and t.ts_uscita == 3 * ORA and t.uscita == 103.0
    assert t.pnl == pytest.approx(30.0)


def test_segnale_con_stop_dalla_parte_sbagliata_non_apre_e_si_conta():
    candele = [candela(0, 100, 101, 99, 100), candela(1, 100, 101, 99, 100), candela(2, 100, 101, 99, 100)]
    ris = motore.esegui(candele, None, None, [], strategia_segnale_alla_barra(0, Segnale("long", stop=101.0)), senza_costi())
    assert ris.trades == []
    assert ris.n_segnali_non_validi == 1
    assert ris.metriche()["n_segnali_non_validi"] == 1


def test_serie_stop_e_mark_disallineate_sollevano_errore():
    candele = [candela(0, 100, 101, 99, 100), candela(1, 100, 101, 99, 100)]
    stop_mancante = [candela(0, 100, 101, 99, 100)]
    with pytest.raises(ValueError):
        motore.esegui(candele, stop_mancante, None, [], lambda s, p: None, senza_costi())
    with pytest.raises(ValueError):
        motore.esegui(candele, None, stop_mancante, [], lambda s, p: None, senza_costi())


def test_stop_sulla_serie_stop_non_su_quella_dei_segnali():
    # La serie dei segnali non tocca mai 99, la serie stop si' (low 98.5 nella barra 2):
    # lo stop SCATTA perche' si valuta sulla serie stop. Si RIEMPIE pero' sul last
    # (serie dei segnali), che in quella barra non e' mai sceso sotto 99.5: il
    # riempimento e' 99.5, il peggior prezzo del last, non 99 (un prezzo che il
    # mercato non ha fatto). pnl = 10 * (99.5 - 100) = -5.
    candele = [candela(0, 100, 101, 99.5, 100), candela(1, 100, 101, 99.5, 100), candela(2, 100, 101, 99.5, 100), candela(3, 100, 101, 99.5, 100)]
    serie_stop = candele[:2] + [candela(2, 100, 101, 98.5, 100), candela(3, 100, 101, 99.5, 100)]
    ris = motore.esegui(candele, serie_stop, None, [], strategia_segnale_alla_barra(0, Segnale("long", stop=99.0)), senza_costi())
    t = ris.trades[0]
    assert t.esito == "stop" and t.uscita == 99.5 and t.ts_uscita == candele[2].close_ts
    assert t.pnl == pytest.approx(-5.0)
    # Se il last scende fino allo stop (low 98), il riempimento e' lo stop stesso: 99.
    candele2 = candele[:2] + [candela(2, 100, 101, 98, 100), candela(3, 100, 101, 99.5, 100)]
    ris2 = motore.esegui(candele2, serie_stop, None, [], strategia_segnale_alla_barra(0, Segnale("long", stop=99.0)), senza_costi())
    assert ris2.trades[0].uscita == 99.0


def test_metriche_drawdown_e_rendimento_per_anno():
    # Curva: 1000 -> 1100 (2023) -> 880 (2024) -> 990 (2024).
    # Drawdown massimo = (1100 - 880) / 1100 = 0.2.
    # 2023: (1100 - 1000) / 1000 = 0.10; 2024: (990 - 1100) / 1100 = -0.10.
    def trade(pnl, ts):
        return motore.Trade("long", ts - 1, ts, 100, 101, 99, None, 1, False, False, "target", pnl, pnl, 0, 0, 0, 10, pnl / 10, 1, 50)

    ts_2023 = 1_690_000_000_000  # luglio 2023
    ts_2024a = 1_710_000_000_000  # marzo 2024
    ts_2024b = 1_720_000_000_000  # luglio 2024
    trades = [trade(100, ts_2023), trade(-220, ts_2024a), trade(110, ts_2024b)]
    curva = [(0, 1000.0), (ts_2023, 1100.0), (ts_2024a, 880.0), (ts_2024b, 990.0)]
    ris = motore.Risultato(trades, curva, 1000.0, 990.0)
    m = ris.metriche()
    assert m["drawdown_max"] == pytest.approx(0.2)
    assert m["rendimento_per_anno"] == {2023: pytest.approx(0.10), 2024: pytest.approx(-0.10)}
    assert m["profit_factor"] == pytest.approx(210 / 220)
    assert m["win_rate"] == pytest.approx(2 / 3)
    assert m["rendimento_totale"] == pytest.approx(-0.01)


# ---------------------------------------------------------------------------
# Regole aggiunte dopo le revisioni: gap all'apertura, pnl in percentuale,
# capitale esaurito, moltiplicatore dei costi sul funding
# ---------------------------------------------------------------------------


def test_gap_all_apertura_decide_prima_della_regola_intrabarra():
    # Long a 100, stop 95, target 110 (quantita' = 10 / 5 = 2).
    # Barra che apre a 90 e sale a 112: lo stop si riempie a 90 all'apertura anche con
    # "target_prima" (il target arriva quando la posizione non c'e' piu'): pnl = 2 * -10 = -20.
    candele = [candela(0, 100, 101, 99, 100), candela(1, 100, 101, 99, 100), candela(2, 90, 112, 89, 111), candela(3, 111, 112, 110, 111)]
    strategia = strategia_segnale_alla_barra(0, Segnale("long", stop=95.0, target=110.0))
    t = motore.esegui(candele, None, None, [], strategia, senza_costi(riempimento_intrabarra="target_prima")).trades[0]
    assert t.esito == "stop" and t.uscita == 90.0 and t.pnl == pytest.approx(-20.0)
    # Barra che apre a 115 e scende a 94: il target si riempie a 115 anche con "stop_prima".
    candele2 = candele[:2] + [candela(2, 115, 116, 94, 95), candela(3, 95, 96, 94, 95)]
    t2 = motore.esegui(candele2, None, None, [], strategia, senza_costi(riempimento_intrabarra="stop_prima")).trades[0]
    assert t2.esito == "target" and t2.uscita == 115.0 and t2.pnl == pytest.approx(30.0)


def test_gap_oltre_la_liquidazione_chiude_al_prezzo_di_liquidazione():
    # Trade ridotto: stop 99.9 -> quantita' 20, leva 2, liquidazione long 51 (vedi test 6).
    # La barra 2 apre a 30, oltre la liquidazione: chiusura "liquidazione" a 51,
    # perdita 20 * 49 = 980 = margine isolato (2000 / 2) meno il mantenimento; mai 1400.
    candele = [candela(0, 100, 101, 99.95, 100), candela(1, 100, 100.5, 99.95, 100), candela(2, 30, 35, 25, 30), candela(3, 30, 31, 29, 30)]
    ris = motore.esegui(candele, None, None, [], strategia_segnale_alla_barra(0, Segnale("long", stop=99.9)), senza_costi())
    t = ris.trades[0]
    assert t.esito == "liquidazione" and t.uscita == pytest.approx(51.0)
    assert t.pnl == pytest.approx(-980.0)
    assert ris.capitale_finale == pytest.approx(20.0)


def test_pnl_pct_e_frazione_del_capitale_all_ingresso():
    # Trade senza costi: entrata 100, target 102, quantita' 10 -> pnl 20 su capitale 1000 = 2%.
    # Secondo trade: capitale 1020, quantita' 10.2, pnl 20.4 -> 20.4 / 1020 = 2%.
    candele = [candela(0, 100, 101, 99.5, 100), candela(1, 100, 102.5, 99.5, 101), candela(2, 100, 102.5, 99.5, 101), candela(3, 101, 101.5, 100.5, 101)]

    def strategia(storia, posizione):
        if posizione is None and len(storia) - 1 in (0, 1):
            return Segnale("long", 99.0, 102.0)
        return None

    ris = motore.esegui(candele, None, None, [], strategia, senza_costi())
    assert [t.pnl for t in ris.trades] == pytest.approx([20.0, 20.4])
    assert [t.pnl_pct for t in ris.trades] == pytest.approx([0.02, 0.02])


def test_capitale_esaurito_ha_il_suo_contatore():
    # Capitale iniziale 0: il segnale e' valido (stop sotto l'apertura) ma non si puo' aprire.
    candele = [candela(0, 100, 101, 99, 100), candela(1, 100, 101, 99, 100), candela(2, 100, 101, 99, 100)]
    ris = motore.esegui(candele, None, None, [], strategia_segnale_alla_barra(0, Segnale("long", stop=99.0)), senza_costi(capitale_iniziale=0.0))
    assert ris.trades == []
    assert ris.n_segnali_capitale_esaurito == 1 and ris.n_segnali_non_validi == 0
    assert ris.metriche()["n_segnali_capitale_esaurito"] == 1


def test_moltiplicatore_costi_non_tocca_gli_incassi_di_funding():
    # Short a 100, quantita' 10 (stop 101), settlement alla barra 2 con tasso +0.0001:
    # incassa 0.0001 * 10 * 100 = 0.10 sia a moltiplicatore 1 sia a 2. Con tasso
    # -0.0001 lo short PAGA 0.10, che a moltiplicatore 2 diventa 0.20.
    candele = [candela(0, 100, 100.5, 99.5, 100), candela(1, 100, 100.5, 99.5, 100), candela(2, 100, 100.5, 99.5, 100), candela(3, 100, 100.5, 99.5, 100)]
    strategia = strategia_segnale_alla_barra(0, Segnale("short", 101.0, None))
    incasso = motore.esegui(candele, None, None, [(2 * ORA, 0.0001)], strategia, senza_costi(moltiplicatore_costi=2.0)).trades[0]
    assert incasso.funding_pagato == pytest.approx(-0.10)
    costo = motore.esegui(candele, None, None, [(2 * ORA, -0.0001)], strategia, senza_costi(moltiplicatore_costi=2.0)).trades[0]
    assert costo.funding_pagato == pytest.approx(0.20)
