"""BACKTEST DI PORTAFOGLIO — la simulazione pura con trade sintetici.

24 set 2026: il gate valida una coppia alla volta con 10.000$ fissi; il paper e'
la prima volta in cui le coppie validate girano insieme con i limiti veri del
conto. Qui si verifica che `simula` applichi quei limiti come il bot: una
posizione per coin, tetto di posizioni, tetto di perdita per coin al giorno,
tetto di rischio per direzione (nuovo trade compreso, confronto stretto: la
regola di `_directional_risk_blocks`), e che il PnL in valuta segua l'equity
corrente. Dal 24 set anche i due what-if (stop giornaliero di portafoglio,
netto direzionale in R), le due misure (win rate dopo k perdite, diversification
ratio) e il riepilogo per Firebase senza liste annidate.
"""
import math
from datetime import datetime, timezone

import pytest

from bot.risk import portafoglio as pf
from bot.risk.portafoglio import diversification_ratio, simula, wr_condizionato

BARRA = 900.0  # 15 minuti
T0 = datetime(2026, 9, 21, 10, 0, tzinfo=timezone.utc).timestamp()

#: limiti "larghi" di partenza: ogni test stringe SOLO quello che vuole misurare
LARGHI = {"max_posizioni": 50, "una_per_coin": True, "tetto_coin_giorno": 0.0,
          "tetto_direzione": 0.0, "cooldown_ore": 0.0, "rischio_per_trade": 0.01,
          "tetto_giorno": 0.0, "netto_r_max": 0.0}


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
    """La regola del bot: aperte nello stesso verso + il nuovo, confronto
    stretto. Tre short da 1% aperti + il quarto = 4% > 3%: il quarto non entra;
    un long nello stesso istante si', perche' la direzione e' un'altra."""
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


def test_tetto_per_direzione_il_terzo_al_3_percento_entra():
    """Due short aperti (2%) + il terzo = 3%: NON supera il 3%, entra. Fino al
    24 set si contavano solo le aperte con `>=` e si bloccava un trade prima
    del bot. Con tetto 2% invece il terzo (2% + 1% > 2%) non entra."""
    tr = [_t("A", "short", T0, bars=8), _t("B", "short", T0 + BARRA, bars=8),
          _t("C", "short", T0 + 2 * BARRA, bars=8)]
    out = simula(tr, 10_000, {**LARGHI, "tetto_direzione": 0.03}, secondi_barra=BARRA)
    assert out["n_aperti"] == 3 and out["saltati"]["tetto_direzione"] == 0
    out2 = simula(tr, 10_000, {**LARGHI, "tetto_direzione": 0.02}, secondi_barra=BARRA)
    assert out2["n_aperti"] == 2 and out2["saltati"]["tetto_direzione"] == 1


def test_tetto_per_direzione_esatto_anche_con_equity_non_tonda():
    """Tre volte l'1% deve valere ESATTAMENTE il 3% anche quando l'equity non
    e' un numero tondo: l'aritmetica binaria non deve bloccare il terzo."""
    tr = [_t("A", "long", T0, bars=8), _t("B", "long", T0 + BARRA, bars=8),
          _t("C", "long", T0 + 2 * BARRA, bars=8)]
    for eq in (9_876.54, 10_333.33, 7.77):
        out = simula(tr, eq, {**LARGHI, "tetto_direzione": 0.03}, secondi_barra=BARRA)
        assert out["n_aperti"] == 3, eq


def test_limiti_default_leggono_il_tetto_del_bot(monkeypatch):
    """Il tetto per direzione e' MAX_DIRECTIONAL_RISK_PCT (quello che il bot
    applica dall'8 set), non la chiave doppia MAX_RISK_PER_DIRECTION."""
    monkeypatch.setattr(pf.settings, "MAX_DIRECTIONAL_RISK_PCT", 0.05, raising=False)
    monkeypatch.setattr(pf.settings, "MAX_RISK_PER_DIRECTION", 0.01, raising=False)
    lim = pf.limiti_default()
    assert lim["tetto_direzione"] == 0.05
    # i what-if partono spenti: il bot non li ha
    assert lim["tetto_giorno"] == 0.0 and lim["netto_r_max"] == 0.0


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


def test_stop_giornaliero_di_portafoglio_ferma_fino_a_mezzanotte():
    """Un -2R e due -1R su tre coin nello stesso giorno = -395,02 (il rischio
    si legge sull'equity corrente: 200 + 98 + 97,02), oltre il 3% dei 10.000 di
    inizio giornata: il quarto trade del giorno (su un'altra coin) non si apre;
    il giorno dopo si riparte. Con tetto 5% (500) non scatta."""
    domani = T0 + 86_400
    tr = [_t("A", "long", T0, bars=1, pnl_pct=-0.02), _t("B", "long", T0 + 2 * BARRA, bars=1),
          _t("C", "long", T0 + 4 * BARRA, bars=1),
          _t("D", "long", T0 + 6 * BARRA, bars=1, pnl_pct=0.02),     # fermato
          _t("E", "long", domani, bars=1, pnl_pct=0.02)]             # riparte
    out = simula(tr, 10_000, {**LARGHI, "tetto_giorno": 0.03}, secondi_barra=BARRA)
    assert out["n_aperti"] == 4
    assert out["saltati"]["tetto_giorno"] == 1
    assert out["giorni_fermati"] == 1
    assert out["pnl_per_giorno"]["2026-09-21"] == -395.02
    _contabilita_chiusa(out)
    largo = simula(tr, 10_000, {**LARGHI, "tetto_giorno": 0.05}, secondi_barra=BARRA)
    assert largo["n_aperti"] == 5 and largo["giorni_fermati"] == 0


def test_stop_giornaliero_e_sul_netto_del_giorno():
    """Una vincita da +2R prima di due stop da -1R lascia il giorno a 0: il
    tetto del 2% NON scatta (e' perdita netta del portafoglio, non somma dei
    soli stop come il tetto per coin)."""
    tr = [_t("A", "long", T0, bars=1, pnl_pct=0.02),
          _t("B", "long", T0 + 2 * BARRA, bars=1), _t("C", "long", T0 + 4 * BARRA, bars=1),
          _t("D", "long", T0 + 6 * BARRA, bars=1, pnl_pct=0.01)]
    out = simula(tr, 10_000, {**LARGHI, "tetto_giorno": 0.02}, secondi_barra=BARRA)
    assert out["saltati"]["tetto_giorno"] == 0 and out["n_aperti"] == 4


def test_netto_direzionale_in_r():
    """Con netto massimo 2R: due long aperti fanno +2R; il terzo long
    porterebbe a +3R e salta; uno short nello stesso istante porta a +1R ed
    entra. Poi un long (di nuovo +2R) entra."""
    tr = [_t("A", "long", T0, bars=20), _t("B", "long", T0 + BARRA, bars=20),
          _t("C", "long", T0 + 2 * BARRA, bars=20),          # +3R: salta
          _t("D", "short", T0 + 2 * BARRA, bars=20),         # +1R: entra
          _t("E", "long", T0 + 3 * BARRA, bars=20)]          # +2R: entra
    out = simula(tr, 10_000, {**LARGHI, "netto_r_max": 2.0}, secondi_barra=BARRA)
    assert out["n_aperti"] == 4
    assert out["saltati"]["netto_r"] == 1
    assert out["per_direzione"]["short"]["n"] == 1
    _contabilita_chiusa(out)
    spento = simula(tr, 10_000, {**LARGHI, "netto_r_max": 0.0}, secondi_barra=BARRA)
    assert spento["n_aperti"] == 5


def test_ordine_dei_motivi_direzione_prima_di_giorno_e_netto():
    """Un trade che violerebbe tetto direzione E netto viene attribuito al
    primo dei due nell'ordine di MOTIVI: cosi' ogni colonna del what-if
    cumulativo sposta solo i trade che SOLO quel limite fermerebbe."""
    assert pf.MOTIVI.index("tetto_direzione") < pf.MOTIVI.index("tetto_giorno") \
        < pf.MOTIVI.index("netto_r")
    tr = [_t(f"C{i}", "long", T0 + i * BARRA, bars=20) for i in range(4)]
    out = simula(tr, 10_000, {**LARGHI, "tetto_direzione": 0.02, "netto_r_max": 2.0},
                 secondi_barra=BARRA)
    # il terzo e il quarto li fermerebbero entrambi (2% + 1% > 2%; 3R > 2R):
    # li conta il tetto direzione, che viene prima; il netto resta a zero
    assert out["saltati"]["tetto_direzione"] == 2 and out["saltati"]["netto_r"] == 0
    assert out["n_aperti"] == 2


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


# --------------------------------------------------------------------------- #
# MISURE DEL 24 SET: win rate dopo k perdite, diversification ratio           #
# --------------------------------------------------------------------------- #
def test_wr_condizionato_su_sequenza_nota():
    """gen_a: L L W L L L L W W; gen_b: L W. Sui candidati, per strategia.
    Dopo esattamente 1 perdita: gen_a idx1 (L), idx4 (L), gen_b idx1 (W) -> 1/3.
    Dopo 2: gen_a idx2 (W), idx5 (L) -> 1/2. Dopo 3: idx6 (L) -> 0/1.
    Dopo 4: idx7 (W) -> 1/1. Dopo 5: nessuno. Incondizionato 4/11."""
    seq_a = [-1, -1, 1, -1, -1, -1, -1, 1, 1]
    seq_b = [-1, 1]
    pronti = ([{"strategy": "gen_a", "pnl_pct": 0.01 * v} for v in seq_a]
              + [{"strategy": "gen_b", "pnl_pct": 0.01 * v} for v in seq_b])
    wc = wr_condizionato(pronti)
    assert wc["incondizionato"] == {"n": 11, "wr": round(4 / 11, 4)}
    k = wc["dopo_k"]
    assert (k["1"]["n"], k["1"]["wr"]) == (3, round(1 / 3, 4))
    assert (k["2"]["n"], k["2"]["wr"]) == (2, 0.5)
    assert (k["3"]["n"], k["3"]["wr"]) == (1, 0.0)
    assert (k["4"]["n"], k["4"]["wr"]) == (1, 1.0)
    assert k["5"] == {"n": 0, "wr": 0.0, "diff_punti": 0.0, "t": 0.0}
    # differenza in punti e t = diff / sqrt(p(1-p)/n)
    p = 4 / 11
    diff = (1 / 3 - p) * 100
    assert k["1"]["diff_punti"] == round(diff, 2)
    assert k["1"]["t"] == round(diff / (math.sqrt(p * (1 - p) / 3) * 100), 2)
    assert k["4"]["t"] > 0 and k["3"]["t"] < 0


def test_wr_condizionato_e_sui_candidati_non_solo_sugli_aperti():
    """Con max 1 posizione, il secondo trade (che si sovrappone) e' saltato ma
    conta lo stesso nella sequenza: la serie di una strategia e' la sua."""
    tr = [_t("A", "long", T0, bars=8), _t("B", "long", T0 + BARRA, bars=8),
          _t("C", "long", T0 + 20 * BARRA, bars=8, pnl_pct=0.01)]
    out = simula(tr, 10_000, {**LARGHI, "max_posizioni": 1}, secondi_barra=BARRA)
    assert out["n_aperti"] == 2
    wc = out["wr_condizionato"]
    assert wc["incondizionato"]["n"] == 3
    assert wc["dopo_k"]["2"]["n"] == 1 and wc["dopo_k"]["2"]["wr"] == 1.0
    assert wc["dopo_k"]["1"]["n"] == 1 and wc["dopo_k"]["1"]["wr"] == 0.0


def _due_coppie(segno_b: int):
    """Tre giorni, due coin: A fa +2R, -1R, +1R; B lo stesso (segno_b=+1) o
    l'opposto (segno_b=-1). Stesso istante d'ingresso -> stesso rischio."""
    g = 86_400
    tr = []
    for i, r in enumerate((0.02, -0.01, 0.01)):
        tr.append(_t("A", "long", T0 + i * g, pnl_pct=r, strategy="gen_a"))
        tr.append(_t("B", "long", T0 + i * g, pnl_pct=segno_b * r, strategy="gen_b"))
    return tr


def test_diversification_ratio_identiche_1_opposte_0():
    uguali = simula(_due_coppie(+1), 10_000, LARGHI, secondi_barra=BARRA)
    assert uguali["n_coppie_aperte"] == 2
    assert uguali["diversification_ratio"] == pytest.approx(1.0, abs=1e-3)
    opposte = simula(_due_coppie(-1), 10_000, LARGHI, secondi_barra=BARRA)
    assert opposte["diversification_ratio"] == pytest.approx(0.0, abs=1e-3)
    # funzione pura: una coppia sola -> 1; giorni mancanti valgono 0
    assert diversification_ratio({"d1": 1.0, "d2": -1.0}, {"x": {"d1": 1.0, "d2": -1.0}}) == 1.0
    assert diversification_ratio({"d1": 1.0}, {"x": {"d1": 1.0}}) is None
    assert diversification_ratio({"d1": 0.0, "d2": 0.0}, {"x": {}}) is None


# --------------------------------------------------------------------------- #
# RIEPILOGO PER FIREBASE: niente liste annidate (ops/results/0184)            #
# --------------------------------------------------------------------------- #
def _lista_annidata(v, dentro=False) -> bool:
    """Verifica ricorsiva, indipendente da quella dello script."""
    if isinstance(v, (list, tuple)):
        return dentro or any(_lista_annidata(x, True) for x in v)
    if isinstance(v, dict):
        return any(_lista_annidata(x, dentro) for x in v.values())
    return False


def test_riepilogo_compatto_senza_liste_annidate():
    sp = pytest.importorskip("scripts.portafoglio_backtest")
    g = 86_400
    tr = [_t("A", "long", T0 + i * g, pnl_pct=r)
          for i, r in enumerate((0.02, -0.01, -0.03, 0.01, -0.02, 0.005, -0.015))]
    out = simula(tr, 10_000, LARGHI, secondi_barra=BARRA)
    rc = sp.riepilogo_compatto(out)
    assert "curva" not in rc and "pnl_per_giorno" not in rc
    assert not _lista_annidata(rc)
    assert not sp.contiene_liste_annidate(rc)
    assert len(rc["giorni_peggiori"]) == 5
    assert rc["giorni_peggiori"][0] == {"giorno": "2026-09-23", "pnl": out["pnl_per_giorno"]["2026-09-23"]}
    assert rc["giorni_peggiori"][0]["pnl"] <= rc["giorni_peggiori"][1]["pnl"]
    # il documento intero come lo pubblica lo script
    doc = {"scenari": {"a": rc, "b": rc}, "limiti": out["limiti"], "lettura": "x"}
    assert not _lista_annidata(doc)
    # il controllo dello script vede davvero una tupla dentro una lista
    assert sp.contiene_liste_annidate({"x": [("g", 1.0)]})
    assert sp.contiene_liste_annidate({"x": {"y": [[1, 2]]}})
