"""Revisione avversaria n. 1 del motore (research/src/motore.py): i conti dei soldi.

Ogni test rifa' a mano, con numeri tondi, un pezzo del conto: quantita',
commissioni per lato, slippage per lato (con la direzione del peggioramento
per long e short), funding, liquidazione isolated e cross, R, curva del
capitale, drawdown, rendimento per anno, moltiplicatore dei costi.

I test che FALLISCONO sono voluti: smascherano un difetto e restano qui per chi
corregge. In cima a ciascuno c'e' scritto cosa ci si aspetta e perche'.

Candele di 1 ora: ts = base + i * ORA, close_ts = ts + ORA - 1.
"""

from datetime import datetime, timezone

import pytest

from research.src import motore
from research.src.motore import Candela, Parametri, Segnale

ORA = 3_600_000


def candela(i: int, o: float, h: float, l: float, c: float, base: int = 0) -> Candela:
    return Candela(ts=base + i * ORA, open=o, high=h, low=l, close=c, volume=1.0, close_ts=base + i * ORA + ORA - 1)


def senza_costi(**kw) -> Parametri:
    base = dict(commissione_per_lato=0.0, slippage_per_lato=0.0)
    base.update(kw)
    return Parametri(**base)


def segnale_alla_barra(k: int, segnale: Segnale):
    """Strategia che emette ``segnale`` solo alla chiusura della barra k (se non ha posizione)."""

    def strategia(storia, posizione):
        if posizione is None and len(storia) - 1 == k:
            return segnale
        return None

    return strategia


# ---------------------------------------------------------------------------
# Conti a mano che TORNANO (documentano cosa e' giusto): long e short completi
# ---------------------------------------------------------------------------


def test_long_completo_a_mano_con_commissioni_slippage_e_funding():
    # Segnale alla barra 0, ingresso all'apertura della barra 1 a 100, stop 99, target 102.
    # Capitale 1000, rischio 1% -> quantita' = 1000 * 0.01 / |100 - 99| = 10 (sull'apertura).
    # Entrata vera (long compra piu' caro): 100 * (1 + 0.0002) = 100.02.
    # Notional 1000.2 <= 2000 (leva max 2): non ridotto.
    # Rischio iniziale = 10 * (100.02 - 99) = 10.2.
    # Settlement all'apertura della barra 2 (posizione aperta da tutta la barra 1),
    # tasso +0.0001, mark open 100: long PAGA 0.0001 * 10 * 100 = 0.10.
    # Target toccato nella barra 3 (high 102.5): uscita vera (long vende piu' basso)
    # = 102 * (1 - 0.0002) = 101.9796.
    # pnl lordo = 10 * (102 - 100) = 20.
    # commissioni = 0.0005 * 10 * (100.02 + 101.9796) = 0.0005 * 2019.996 = 1.009998.
    # slippage = 10 * (0.02 + 0.0204) = 0.404.
    # pnl = 20 - 1.009998 - 0.404 - 0.10 = 18.486002.
    # R = 18.486002 / 10.2 = 1.81235...
    candele = [
        candela(0, 100, 100.5, 99.5, 100),
        candela(1, 100, 100.5, 99.5, 100),
        candela(2, 100, 101, 99.5, 100),
        candela(3, 100, 102.5, 99.5, 101),
    ]
    ris = motore.esegui(candele, None, None, [(2 * ORA, 0.0001)], segnale_alla_barra(0, Segnale("long", 99.0, 102.0)), Parametri())
    t = ris.trades[0]
    assert t.esito == "target"
    assert t.quantita == pytest.approx(10.0)
    assert t.entrata == pytest.approx(100.02)
    assert t.uscita == pytest.approx(101.9796)
    assert t.pnl_lordo == pytest.approx(20.0)
    assert t.commissioni == pytest.approx(1.009998)
    assert t.slippage_costo == pytest.approx(0.404)
    assert t.funding_pagato == pytest.approx(0.10)
    assert t.pnl == pytest.approx(18.486002)
    assert t.rischio_iniziale == pytest.approx(10.2)
    assert t.r == pytest.approx(18.486002 / 10.2)
    assert ris.capitale_finale == pytest.approx(1018.486002)


def test_short_completo_a_mano_con_commissioni_slippage_e_funding():
    # Short: apertura 100, stop 101, target 98. quantita' = 1000 * 0.01 / 1 = 10.
    # Entrata vera (short vende piu' basso): 100 * (1 - 0.0002) = 99.98.
    # Rischio iniziale = 10 * (101 - 99.98) = 10.2.
    # Settlement all'apertura della barra 2, tasso +0.0001, mark open 100:
    # lo short INCASSA 0.10 -> funding_pagato = -0.10.
    # Target toccato nella barra 3 (low 97.5): uscita vera (short ricompra piu' caro)
    # = 98 * (1 + 0.0002) = 98.0196.
    # pnl lordo = 10 * (100 - 98) = 20.
    # commissioni = 0.0005 * 10 * (99.98 + 98.0196) = 0.0005 * 1979.996 = 0.989998.
    # slippage = 10 * (0.02 + 0.0196) = 0.396.
    # pnl = 20 - 0.989998 - 0.396 + 0.10 = 18.714002.   R = 18.714002 / 10.2.
    candele = [
        candela(0, 100, 100.5, 99.5, 100),
        candela(1, 100, 100.5, 99.5, 100),
        candela(2, 100, 100.5, 99, 100),
        candela(3, 100, 100.5, 97.5, 99),
    ]
    ris = motore.esegui(candele, None, None, [(2 * ORA, 0.0001)], segnale_alla_barra(0, Segnale("short", 101.0, 98.0)), Parametri())
    t = ris.trades[0]
    assert t.esito == "target"
    assert t.entrata == pytest.approx(99.98)
    assert t.uscita == pytest.approx(98.0196)
    assert t.pnl_lordo == pytest.approx(20.0)
    assert t.commissioni == pytest.approx(0.989998)
    assert t.slippage_costo == pytest.approx(0.396)
    assert t.funding_pagato == pytest.approx(-0.10)
    assert t.pnl == pytest.approx(18.714002)
    assert t.rischio_iniziale == pytest.approx(10.2)
    assert t.r == pytest.approx(18.714002 / 10.2)


def test_liquidazione_isolated_e_cross_a_mano():
    # Trade RIDOTTO: stop a 0.1 dall'apertura -> quantita' 1000*0.01/0.1 = 100, notional
    # 10000 > tetto 2000 -> quantita' = 2000/100 = 20, leva effettiva 2.
    # isolated long:  liq = 100 * (1 - 1/2 + 0.01) = 51.
    # isolated short: liq = 100 * (1 + 1/2 - 0.01) = 149.
    # cross: leva_cross = notional / capitale = 2000 / 1000 = 2 -> stessi prezzi.
    # Trade NON ridotto long con notional 1000 = capitale: leva 1 -> liq = 100 * 0.01 = 1
    # sia isolated sia cross (tutto il capitale e' margine in entrambi i casi).
    candele = [candela(0, 100, 100.05, 99.95, 100), candela(1, 100, 100.05, 99.95, 100), candela(2, 100, 100.05, 99.95, 100)]
    for modalita in ("isolated", "cross"):
        p = senza_costi(modalita_margine=modalita)
        lungo = motore.esegui(candele, None, None, [], segnale_alla_barra(0, Segnale("long", 99.9, None)), p).trades[0]
        corto = motore.esegui(candele, None, None, [], segnale_alla_barra(0, Segnale("short", 100.1, None)), p).trades[0]
        assert lungo.ridotto and corto.ridotto
        assert lungo.quantita == pytest.approx(20.0)
        assert lungo.prezzo_liquidazione == pytest.approx(51.0), modalita
        assert corto.prezzo_liquidazione == pytest.approx(149.0), modalita
        normale = motore.esegui(candele, None, None, [], segnale_alla_barra(0, Segnale("long", 99.0, None)), p).trades[0]
        assert not normale.ridotto
        assert normale.prezzo_liquidazione == pytest.approx(1.0), modalita


def test_curva_capitale_drawdown_e_rendimento_per_anno_a_mano():
    # Base: 2024-12-31 22:00 UTC. Barra 0 segnale; barra 1 (23:00, ancora 2024) ingresso
    # a 100 con stop 99 e stop toccato -> -10 (senza costi): capitale 990, chiuso nel 2024.
    # Alla chiusura della barra 1 nuovo segnale; barra 2 = 2025-01-01 00:00: ingresso a 100,
    # quantita' = 990 * 0.01 / 1 = 9.9, target 102 toccato -> +19.8: capitale 1009.8, nel 2025.
    # Curva: (t0, 1000), (close_ts barra 1, 990), (close_ts barra 2, 1009.8),
    # (close_ts ultima, 1009.8). Le uscite dentro la barra (stop, target) portano
    # il close_ts della barra, non l'apertura: lo stop della barra 1 e' registrato
    # a 23:59:59.999 del 31 dic 2024 (ancora 2024), il target della barra 2 a
    # 00:59:59.999 del 1 gen 2025. (Correzione del correttore: la versione
    # originale di questo test aspettava l'apertura della barra, che la revisione
    # n. 4 ha mostrato essere un istante in cui l'uscita non poteva essere avvenuta.)
    # Drawdown massimo = (1000 - 990) / 1000 = 0.01.
    # Rendimento 2024 = -10 / 1000 = -0.01; 2025 = 19.8 / 990 = 0.02.
    base = 1735682400000
    candele = [
        candela(0, 100, 100.5, 99.5, 100, base),
        candela(1, 100, 100.5, 98.5, 99.5, base),
        candela(2, 100, 102.5, 99.5, 101, base),
        candela(3, 101, 101.5, 100.5, 101, base),
    ]

    def strategia(storia, posizione):
        if posizione is None and len(storia) - 1 in (0, 1):
            return Segnale("long", 99.0, 102.0)
        return None

    ris = motore.esegui(candele, None, None, [], strategia, senza_costi())
    assert [t.pnl for t in ris.trades] == pytest.approx([-10.0, 19.8])
    assert ris.curva_capitale == [
        (base, 1000.0),
        (base + 2 * ORA - 1, pytest.approx(990.0)),
        (base + 3 * ORA - 1, pytest.approx(1009.8)),
        (base + 4 * ORA - 1, pytest.approx(1009.8)),
    ]
    m = ris.metriche()
    assert m["drawdown_max"] == pytest.approx(0.01)
    assert m["rendimento_per_anno"] == {2024: pytest.approx(-0.01), 2025: pytest.approx(0.02)}
    assert m["rendimento_totale"] == pytest.approx(0.0098)


# ---------------------------------------------------------------------------
# DIFETTO 1: gap in apertura oltre lo stop (o oltre il target) e regola intra-barra
# ---------------------------------------------------------------------------


def test_difetto_target_prima_non_puo_vincere_se_la_barra_apre_gia_oltre_lo_stop():
    # Long a 100, stop 99, target 102. La barra 2 APRE a 97 (sotto lo stop) e poi sale a 103.
    # L'apertura e' il primo prezzo della barra: lo stop si riempie a 97 PRIMA che
    # qualunque prezzo possa toccare 102. L'ordine qui NON e' ambiguo, quindi
    # "target_prima" non puo' applicarsi: atteso esito "stop" a 97 (gap all'apertura).
    # Il motore invece restituisce "target" a 102: un trade perso diventa vinto.
    candele = [candela(0, 100, 100.5, 99.5, 100), candela(1, 100, 100.5, 99.5, 100), candela(2, 97, 103, 96, 100)]
    p = senza_costi(riempimento_intrabarra="target_prima")
    t = motore.esegui(candele, None, None, [], segnale_alla_barra(0, Segnale("long", 99.0, 102.0)), p).trades[0]
    assert t.esito == "stop"
    assert t.uscita == pytest.approx(97.0)
    assert t.pnl == pytest.approx(-30.0)  # 10 * (97 - 100)


def test_difetto_stop_prima_non_puo_vincere_se_la_barra_apre_gia_oltre_il_target():
    # Long a 100, stop 99, target 102. La barra 2 APRE a 103 (sopra il target) e poi
    # scende a 98. Il take-profit limit si riempie all'apertura, a 103, prima che il
    # prezzo possa scendere a 99: atteso esito "target" a 103 (gap all'apertura).
    # Il motore restituisce "stop" a 99 (nemmeno al prezzo di apertura): un trade
    # vinto diventa perso. Con "stop_prima" l'errore e' pessimista ma e' un numero
    # sbagliato, non una scelta prudente: l'ordine dei due eventi e' noto.
    candele = [candela(0, 100, 100.5, 99.5, 100), candela(1, 100, 100.5, 99.5, 100), candela(2, 103, 104, 98, 100)]
    p = senza_costi(riempimento_intrabarra="stop_prima")
    t = motore.esegui(candele, None, None, [], segnale_alla_barra(0, Segnale("long", 99.0, 102.0)), p).trades[0]
    assert t.esito == "target"
    assert t.uscita == pytest.approx(103.0)


# ---------------------------------------------------------------------------
# DIFETTO 2: il moltiplicatore dei costi raddoppia anche gli INCASSI di funding
# ---------------------------------------------------------------------------


def test_difetto_moltiplicatore_costi_raddoppia_gli_incassi_di_funding():
    # Short a 100 (quantita' 10), settlement all'apertura della barra 2 con tasso +0.0001:
    # lo short incassa 0.0001 * 10 * 100 = 0.10. La prova a costi doppi deve
    # peggiorare (o lasciare uguale) il risultato: un incasso non e' un costo.
    # Il motore invece lo moltiplica per 2: con moltiplicatore 2 lo short incassa 0.20
    # e il pnl MIGLIORA (0.20 contro 0.10). Una strategia short in regime di funding
    # positivo (il caso normale sul crypto) passa la prova a costi doppi piu' facilmente.
    candele = [candela(0, 100, 100.5, 99.5, 100), candela(1, 100, 100.5, 99.5, 100), candela(2, 100, 100.5, 99.5, 100), candela(3, 100, 100.5, 99.5, 100)]
    strategia = segnale_alla_barra(0, Segnale("short", 101.0, None))
    normale = motore.esegui(candele, None, None, [(2 * ORA, 0.0001)], strategia, senza_costi(moltiplicatore_costi=1.0)).trades[0]
    doppio = motore.esegui(candele, None, None, [(2 * ORA, 0.0001)], strategia, senza_costi(moltiplicatore_costi=2.0)).trades[0]
    assert normale.funding_pagato == pytest.approx(-0.10)
    assert doppio.pnl <= normale.pnl + 1e-9, "a costi doppi il pnl non puo' migliorare"
    assert doppio.funding_pagato == pytest.approx(-0.10), "un incasso di funding non va raddoppiato"


# ---------------------------------------------------------------------------
# DIFETTO 3: settlement all'apertura della barra di INGRESSO contato anche se incasso
# ---------------------------------------------------------------------------


def test_difetto_funding_all_apertura_della_barra_di_ingresso_contato_anche_se_incasso():
    # Short che entra all'apertura della barra 1; un settlement cade ESATTAMENTE a quel
    # ts (tasso +0.0001, incasso per lo short). La posizione nasce nello stesso istante
    # del settlement: momento ambiguo (su Binance la foto delle posizioni e' presa al
    # settlement, un ordine mandato all'apertura arriva dopo). Il motore applica gia'
    # la regola "momento ambiguo = solo se costo" per l'uscita da segnale all'apertura
    # (vedi test sotto, che passa); per l'ingresso invece conta tutto, incasso compreso:
    # funding_pagato = -0.05 (quantita' 1000*0.01/2 = 5, 0.0001 * 5 * 100). Atteso 0.
    candele = [candela(0, 100, 100.5, 99.5, 100), candela(1, 100, 100.5, 99.5, 100), candela(2, 100, 100.5, 99.5, 100)]
    t = motore.esegui(candele, None, None, [(1 * ORA, 0.0001)], segnale_alla_barra(0, Segnale("short", 102.0, None)), senza_costi()).trades[0]
    assert t.ts_entrata == 1 * ORA
    assert t.funding_pagato == pytest.approx(0.0), "incasso in un momento ambiguo: non va contato"


def test_riferimento_funding_all_apertura_della_barra_di_uscita_da_segnale_solo_se_costo():
    # Caso speculare gia' gestito bene dal motore: "chiudi" alla barra 1, uscita
    # all'apertura della barra 2 dove cade un settlement con incasso per lo short.
    # Il motore non lo conta (0.0): la stessa regola manca nell'ingresso.
    candele = [candela(0, 100, 100.5, 99.5, 100), candela(1, 100, 100.5, 99.5, 100), candela(2, 100, 100.5, 99.5, 100), candela(3, 100, 100.5, 99.5, 100)]

    def strategia(storia, posizione):
        if posizione is None and len(storia) - 1 == 0:
            return Segnale("short", 102.0, None)
        if posizione is not None and len(storia) - 1 == 1:
            return "chiudi"
        return None

    t = motore.esegui(candele, None, None, [(2 * ORA, 0.0001)], strategia, senza_costi()).trades[0]
    assert t.esito == "segnale" and t.ts_uscita == 2 * ORA
    assert t.funding_pagato == pytest.approx(0.0)


# ---------------------------------------------------------------------------
# DIFETTO 4 (minore): manca il pnl del trade in percentuale del capitale
# ---------------------------------------------------------------------------


def test_difetto_trade_senza_pnl_in_percentuale_del_capitale():
    # Sezione 7, "Unita'": R e ANCHE pnl in percentuale del capitale. Il Trade espone
    # r e pnl in valuta, non la frazione del capitale al momento dell'ingresso.
    candele = [candela(0, 100, 100.5, 99.5, 100), candela(1, 100, 102.5, 99.5, 101)]
    t = motore.esegui(candele, None, None, [], segnale_alla_barra(0, Segnale("long", 99.0, 102.0)), senza_costi()).trades[0]
    nomi = [n for n in vars(t) if "pct" in n or "percent" in n or "frazione" in n]
    assert nomi, "nessun campo del Trade con il pnl in percentuale del capitale"
