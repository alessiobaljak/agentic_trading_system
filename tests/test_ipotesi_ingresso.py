"""LA SESTA IPOTESI: LE CONDIZIONI D'INGRESSO (26 set 2026, backlog I4ter).

Cosa si protegge:
  1. le variabili di un trade si leggono da `feats_at_entry` e, per i trade
     vecchi, si ricavano da `indicators_at_entry` con LE STESSE formule del gate
     (stessi numeri: altrimenti due generazioni di trade parlerebbero due lingue);
  2. l'ipotesi scatta esattamente alla regola dichiarata (4 perdite, 3/4 dallo
     stesso lato, vinti dall'altro) e non sotto;
  3. il testo e `da_ts` sono come per le altre ipotesi; il documento resta
     JSON-safe (Firestore) e piccolo (solo conteggi e mediane);
  4. ogni tipo diventa UNA spec figlia con un solo cambiamento e un id nuovo,
     o None dove il vocabolario non lo esprime;
  5. la discovery mette davvero la figlia in coda.
Il paper PROPONE: nessuna soglia qui viene dal risultato del paper.
"""
import json

from bot.config import settings
from bot.core.models import AssetSnapshot, IndicatorSnapshot, Regime
from bot.learning.referti import (MIN_INGRESSO, MIN_VINTI_INGRESSO, QUOTA_INGRESSO,
                                  TIPI_INGRESSO, VARIABILI_INGRESSO, aggrega_referti,
                                  riassunto_ipotesi, variabili_ingresso_del_trade)
from bot.strategies.generated import spec_id
from bot.strategies.generator import (_ADX, _RSI_HIGH, _RSI_LOW, _VOL, _VOL_PCT,
                                      TIPI_VARIANTE, varianti_da_referto)
from scripts.discover_strategies import firma_spec, varianti_dai_referti
from tests.test_referti import _pm, _t, _tipi
from tests.test_varianti_referti import _Fb, _ipotesi, _spec_rsi


# --------------------------------------------------------------------------- #
# 1. Le variabili: da feats_at_entry e da indicators_at_entry, stessi numeri     #
# --------------------------------------------------------------------------- #
def _ind(**kw):
    base = dict(timeframe="15m", rsi=52.0, adx=14.0, atr=1.2, close=100.0,
                ema_slow=98.0, bb_upper=105.0, bb_lower=95.0, volume=800.0,
                volume_sma=1000.0, ema_fast=99.0)
    base.update(kw)
    return base


def test_variabili_da_feats_e_da_indicatori_danno_gli_stessi_numeri():
    """Un trade del 24 set (solo indicators_at_entry) e uno del 26 (feats_at_entry
    scritto da `feats_ingresso`) devono dare le stesse quattro variabili."""
    from backtesting.engine import feats_ingresso
    ind = _ind()
    snap = AssetSnapshot(symbol="AUSDT", price=100.0, regime=Regime.SIDEWAYS,
                         indicators={"15m": IndicatorSnapshot(**ind)})
    feats = feats_ingresso(snap, "15m", entry=100.0, stop=98.0)
    nuovo = variabili_ingresso_del_trade({"feats_at_entry": feats})
    vecchio = variabili_ingresso_del_trade({"indicators_at_entry": {"15m": ind},
                                            "timeframe": "15m"})
    assert nuovo == vecchio
    assert nuovo == {"adx": 14.0, "vol_ratio": 0.8, "atr_pct": 0.012, "rsi": 52.0}


def test_variabili_mancanti_sono_none_non_zero():
    assert variabili_ingresso_del_trade({}) == {v: None for v in VARIABILI_INGRESSO}
    assert variabili_ingresso_del_trade("boh") == {v: None for v in VARIABILI_INGRESSO}
    v = variabili_ingresso_del_trade({"indicators_at_entry": {"15m": _ind(volume_sma=0.0, adx=None)}})
    assert v["vol_ratio"] is None and v["adx"] is None and v["rsi"] == 52.0
    # feats presenti ma con un buco: il buco resta None, non si ripiega sugli indicatori
    v = variabili_ingresso_del_trade({"feats_at_entry": {"rsi": 50.0, "adx": None},
                                      "indicators_at_entry": {"15m": _ind()}})
    assert v == {"adx": None, "vol_ratio": None, "atr_pct": None, "rsi": 50.0}
    # feats tutti None: si ricava dagli indicatori
    v = variabili_ingresso_del_trade({"feats_at_entry": {"rsi": None},
                                      "indicators_at_entry": {"15m": _ind()}})
    assert v["adx"] == 14.0


def test_variabili_scelgono_il_timeframe_del_trade_poi_quello_del_bot_poi_il_primo():
    tf_bot = settings.ORCHESTRATOR_TIMEFRAME
    ind = {"1h": _ind(timeframe="1h", adx=40.0), tf_bot: _ind(adx=14.0),
           "4h": _ind(timeframe="4h", adx=60.0)}
    if tf_bot == "1h":
        ind["1h"] = _ind(timeframe="1h", adx=14.0)
    assert variabili_ingresso_del_trade({"indicators_at_entry": ind, "timeframe": "4h"})["adx"] == 60.0
    assert variabili_ingresso_del_trade({"indicators_at_entry": ind})["adx"] == 14.0
    solo = {"4h": _ind(timeframe="4h", adx=60.0)}
    assert variabili_ingresso_del_trade({"indicators_at_entry": solo})["adx"] == 60.0
    # snapshot come oggetto (Trade in memoria), non solo come dict
    obj = {"15m": IndicatorSnapshot(**_ind(close=None))}
    v = variabili_ingresso_del_trade({"indicators_at_entry": obj, "timeframe": "15m",
                                      "entry_price": 200.0})
    assert v["atr_pct"] == 0.006      # senza close si divide per il prezzo d'ingresso


# --------------------------------------------------------------------------- #
# 2. L'ipotesi scatta alla regola dichiarata, non sotto                         #
# --------------------------------------------------------------------------- #
def _perso_ingresso(i, **feats):
    """perdita di classe ingresso, direzioni alternate (cosi' non scattano le
    ipotesi per direzione), con le variabili d'ingresso date."""
    base = {"adx": 30.0, "vol_ratio": 1.5, "atr_pct": 0.01, "rsi": 25.0}
    base.update(feats)
    return _t(direction=("long", "short")[i % 2], pm=_pm(classe="ingresso", mfe=0.1),
              feats_at_entry=base, entry_ts=1000.0 + i)


def _vinto(i, **feats):
    base = {"adx": 30.0, "vol_ratio": 1.5, "atr_pct": 0.01, "rsi": 25.0}
    base.update(feats)
    return _t(direction=("long", "short")[i % 2], pnl=+3.0, pm=_pm(classe="uscita"),
              feats_at_entry=base, entry_ts=2000.0 + i)


def test_le_costanti_sono_dichiarate():
    assert MIN_INGRESSO == 4 and MIN_VINTI_INGRESSO == 2 and QUOTA_INGRESSO == 0.75
    assert TIPI_INGRESSO == ("ingresso_adx", "ingresso_vol_ratio", "ingresso_atr_pct", "ingresso_rsi")


def test_ingresso_adx_scatta_a_quattro_perdite_con_adx_basso_e_vinti_sopra():
    persi = [_perso_ingresso(i, adx=a) for i, a in enumerate((12.0, 14.0, 18.0, 25.0, 15.0))]
    vinti = [_vinto(i, adx=a) for i, a in enumerate((27.0, 30.0))]
    doc = aggrega_referti(persi + vinti)
    assert _tipi(doc) == ["ingresso_adx"]
    h = doc["ipotesi"][0]
    assert h["campione"] == 5 and h["variabile"] == "adx" and h["soglia"] == 20.0
    assert h["mediana_persi"] == 14.5 and h["mediana_vinti"] == 28.5
    assert h["motivo"] == ("4 perdite d'ingresso su 5 con ADX < 20 (mediana 14), "
                           "vinti mediana 28")
    assert h["da_ts"] == 1000.0, "la data del primo trade del paper, come le altre"
    assert riassunto_ipotesi(doc) == [
        "gen_a: ingresso_adx — 4 perdite d'ingresso su 5 con ADX < 20 (mediana 14), "
        "vinti mediana 28 (campione 5)"]


def test_ingresso_non_scatta_sotto_le_quattro_perdite_o_con_due_vinti_in_meno():
    persi = [_perso_ingresso(i, adx=12.0) for i in range(4)]
    vinti = [_vinto(i, adx=30.0) for i in range(2)]
    assert _tipi(aggrega_referti(persi[:3] + vinti)) == []
    assert _tipi(aggrega_referti(persi + vinti[:1])) == []
    assert _tipi(aggrega_referti(persi + vinti)) == ["ingresso_adx"]
    # la variabile deve essere NOTA: una perdita senza adx non conta nel campione
    senza = [_perso_ingresso(i, adx=None) for i in range(4)]
    assert _tipi(aggrega_referti(persi[:3] + senza + vinti)) == []


def test_ingresso_rispetta_la_quota_tre_su_quattro():
    """4 perdite: 3 sotto 20 e 1 sopra = 75% -> scatta; 2 su 4 no. 5 perdite:
    3 su 5 e' 60% -> no."""
    vinti = [_vinto(i, adx=30.0) for i in range(2)]
    tre_su_quattro = [_perso_ingresso(i, adx=a) for i, a in enumerate((10.0, 12.0, 15.0, 30.0))]
    assert _tipi(aggrega_referti(tre_su_quattro + vinti)) == ["ingresso_adx"]
    due_su_quattro = [_perso_ingresso(i, adx=a) for i, a in enumerate((10.0, 12.0, 35.0, 30.0))]
    assert _tipi(aggrega_referti(due_su_quattro + vinti)) == []
    tre_su_cinque = tre_su_quattro + [_perso_ingresso(4, adx=40.0)]
    assert _tipi(aggrega_referti(tre_su_cinque + vinti)) == []


def test_ingresso_non_scatta_se_i_vinti_stanno_dallo_stesso_lato():
    """Se anche i vinti nascono con ADX basso, l'ADX basso non spiega le perdite."""
    persi = [_perso_ingresso(i, adx=12.0) for i in range(4)]
    vinti_bassi = [_vinto(i, adx=a) for i, a in enumerate((15.0, 18.0, 30.0))]   # mediana 18
    assert _tipi(aggrega_referti(persi + vinti_bassi)) == []
    vinti_alti = [_vinto(i, adx=a) for i, a in enumerate((15.0, 25.0, 30.0))]    # mediana 25
    assert _tipi(aggrega_referti(persi + vinti_alti)) == ["ingresso_adx"]


def test_ingresso_conta_solo_le_perdite_di_classe_ingresso():
    """Una perdita di classe uscita (andata a favore) con ADX basso non e' una
    perdita D'INGRESSO: la condizione all'apertura non l'ha uccisa."""
    persi = [_perso_ingresso(i, adx=12.0) for i in range(3)]
    uscita = [_t(direction="long", pm=_pm(classe="uscita", mfe=0.8),
                 feats_at_entry={"adx": 12.0, "vol_ratio": 1.5, "atr_pct": 0.01, "rsi": 25.0})]
    vinti = [_vinto(i, adx=30.0) for i in range(2)]
    doc = aggrega_referti(persi + uscita + vinti)
    assert "ingresso_adx" not in _tipi(doc)
    assert doc["ingresso"]["gen_a"]["adx"]["persi"] == 3


def test_ingresso_vol_ratio():
    persi = [_perso_ingresso(i, vol_ratio=v) for i, v in enumerate((0.5, 0.7, 0.9, 1.2))]
    vinti = [_vinto(i, vol_ratio=v) for i, v in enumerate((1.3, 0.9, 1.8))]
    doc = aggrega_referti(persi + vinti)
    assert _tipi(doc) == ["ingresso_vol_ratio"]
    h = doc["ipotesi"][0]
    assert h["soglia"] == 1.0 and h["mediana_vinti"] == 1.3
    assert h["motivo"] == ("3 perdite d'ingresso su 4 con volume sotto la media "
                           "(vol_ratio < 1) (mediana 0.70), vinti mediana 1.30")
    vinti_bassi = [_vinto(i, vol_ratio=v) for i, v in enumerate((0.8, 0.9, 1.8))]
    assert _tipi(aggrega_referti(persi + vinti_bassi)) == []


def test_ingresso_atr_pct_usa_il_75_percentile_dei_vinti_o_il_3_per_cento():
    """Vinti a 1,0-1,6% (75° percentile 1,45%): perdite oltre quel confine sono
    «volatilita' alta». La soglia misurata viaggia nell'ipotesi per la figlia."""
    vinti = [_vinto(i, atr_pct=a) for i, a in enumerate((0.010, 0.012, 0.014, 0.016))]
    persi = [_perso_ingresso(i, atr_pct=a) for i, a in enumerate((0.020, 0.025, 0.018, 0.010))]
    doc = aggrega_referti(persi + vinti)
    assert _tipi(doc) == ["ingresso_atr_pct"]
    h = doc["ipotesi"][0]
    assert h["soglia"] == 0.0145 and h["mediana_vinti"] == 0.013
    assert h["motivo"] == ("3 perdite d'ingresso su 4 con volatilita' alta (ATR > 1.45% "
                           "del prezzo) (mediana 2.00%), vinti mediana 1.30%")
    # vinti molto volatili: il confine e' comunque il 3%, non il loro percentile
    vinti_alti = [_vinto(i, atr_pct=a) for i, a in enumerate((0.040, 0.050))]
    persi_alti = [_perso_ingresso(i, atr_pct=0.045) for i in range(4)]
    doc = aggrega_referti(persi_alti + vinti_alti)
    assert _tipi(doc) == [], "i vinti (mediana 4,5%) stanno dallo stesso lato del 3%"
    persi_alti = [_perso_ingresso(i, atr_pct=0.045) for i in range(4)]
    vinti_calmi = [_vinto(i, atr_pct=a) for i, a in enumerate((0.010, 0.050))]
    doc = aggrega_referti(persi_alti + vinti_calmi)
    assert _tipi(doc) == ["ingresso_atr_pct"] and doc["ipotesi"][0]["soglia"] == 0.03


def test_ingresso_rsi_neutro():
    persi = [_perso_ingresso(i, rsi=r) for i, r in enumerate((45.0, 50.0, 58.0, 30.0))]
    vinti = [_vinto(i, rsi=r) for i, r in enumerate((25.0, 72.0, 28.0))]     # mediana 28
    doc = aggrega_referti(persi + vinti)
    assert _tipi(doc) == ["ingresso_rsi"]
    h = doc["ipotesi"][0]
    assert "soglia" not in h, "la banda e' dichiarata, non misurata"
    assert h["motivo"] == ("3 perdite d'ingresso su 4 con RSI neutro (40-60) (mediana 50), "
                           "vinti mediana 28")
    vinti_neutri = [_vinto(i, rsi=r) for i, r in enumerate((45.0, 55.0, 28.0))]  # mediana 45
    assert _tipi(aggrega_referti(persi + vinti_neutri)) == []


def test_piu_variabili_insieme_e_ordine_deterministico():
    persi = [_perso_ingresso(i, adx=12.0, vol_ratio=0.5) for i in range(4)]
    vinti = [_vinto(i, adx=30.0, vol_ratio=1.5) for i in range(2)]
    d1 = aggrega_referti(persi + vinti)
    d2 = aggrega_referti(list(reversed(persi + vinti)))
    assert d1 == d2
    assert _tipi(d1) == ["ingresso_adx", "ingresso_vol_ratio"]
    # convive con le altre: 4 perdite d'ingresso + 0 vinti -> anche conferma_trend
    d3 = aggrega_referti(persi)
    assert _tipi(d3) == ["conferma_trend"], "senza vinti l'ingresso_* non ha il confronto"


def test_da_indicatori_vecchi_scatta_come_da_feats():
    """Trade del 24 set (solo indicators_at_entry): stessa ipotesi."""
    def vecchio(i, adx, pnl):
        return _t(direction=("long", "short")[i % 2], pnl=pnl,
                  pm=_pm(classe="ingresso" if pnl < 0 else "uscita", mfe=0.1),
                  indicators_at_entry={"15m": _ind(adx=adx)}, timeframe="15m")
    trades = [vecchio(i, 12.0, -5.0) for i in range(4)] + [vecchio(i, 30.0, +3.0) for i in range(2)]
    assert _tipi(aggrega_referti(trades)) == ["ingresso_adx"]


# --------------------------------------------------------------------------- #
# 3. Il documento: piccolo e JSON-safe                                          #
# --------------------------------------------------------------------------- #
def test_il_documento_porta_conteggi_e_mediane_ed_e_json_safe():
    persi = [_perso_ingresso(i, adx=12.0, rsi=None) for i in range(4)]
    vinti = [_vinto(i, adx=30.0) for i in range(2)]
    doc = aggrega_referti(persi + vinti)
    ing = doc["ingresso"]["gen_a"]
    assert set(ing) <= set(VARIABILI_INGRESSO)
    assert ing["adx"] == {"persi": 4, "vinti": 2, "mediana_persi": 12.0, "mediana_vinti": 30.0}
    assert ing["rsi"] == {"persi": 0, "vinti": 2, "mediana_persi": None, "mediana_vinti": 25.0}
    json.dumps(doc)                                   # Firestore accetta solo JSON
    for b in doc["per_strategia"].values():
        assert all(not isinstance(v, (list, dict)) for v in b.values())
    # trade senza strategia e senza dati: niente voce
    assert "?" not in doc["ingresso"]
    assert aggrega_referti([])["ingresso"] == {}
    assert aggrega_referti([_t()])["ingresso"] == {}


# --------------------------------------------------------------------------- #
# 4. Le figlie del generatore                                                    #
# --------------------------------------------------------------------------- #
def test_i_tipi_del_referto_sono_tutti_nel_generatore():
    assert set(TIPI_INGRESSO) <= set(TIPI_VARIANTE)


def test_figlia_ingresso_adx():
    gen = _spec_rsi()
    v = varianti_da_referto(gen, "ingresso_adx")
    assert v["min_adx"] == 25.0 and v["id"] != gen["id"] and v["id"] == spec_id(v)
    assert v["origine"] == "referto" and v["genitore"] == gen["id"] and v["ipotesi"] == "ingresso_adx"
    assert v["features"] == gen["features"] and v["volume_mult"] == gen["volume_mult"]
    assert varianti_da_referto(_spec_rsi(min_adx=20.0), "ingresso_adx")["min_adx"] == 25.0
    assert varianti_da_referto(_spec_rsi(min_adx=25.0), "ingresso_adx") is None
    assert varianti_da_referto(_spec_rsi(min_adx=30.0), "ingresso_adx") is None
    assert max(_ADX) == 25.0, "se la griglia cresce, il gradino sopra 25 diventa lecito"
    assert firma_spec(v) != firma_spec(gen)


def test_figlia_ingresso_vol_ratio():
    gen = _spec_rsi()
    v = varianti_da_referto(gen, "ingresso_vol_ratio")
    assert v["volume_mult"] == 1.5 and v["id"] != gen["id"]
    assert varianti_da_referto(_spec_rsi(volume_mult=1.5), "ingresso_vol_ratio")["volume_mult"] == 2.0
    assert varianti_da_referto(_spec_rsi(volume_mult=2.0), "ingresso_vol_ratio") is None
    assert max(_VOL) == 2.0
    assert firma_spec(v) != firma_spec(gen)


def test_figlia_ingresso_atr_pct_solo_per_spec_solo_long():
    """`volatility_regime` dice «long se calmo, short se agitato»: un tetto a due
    lati non esiste nel vocabolario. La figlia nasce solo con `solo: long`."""
    assert varianti_da_referto(_spec_rsi(), "ingresso_atr_pct") is None
    assert varianti_da_referto(_spec_rsi(solo="short"), "ingresso_atr_pct", 0.02) is None
    gen = _spec_rsi(solo="long")
    v = varianti_da_referto(gen, "ingresso_atr_pct", 0.0145)
    assert v["features"][-1] == {"kind": "volatility_regime", "vol_pct": 0.01}
    assert v["solo"] == "long" and v["id"] != gen["id"] and v["id"] == spec_id(v)
    # senza soglia: sotto il 3% dichiarato
    assert varianti_da_referto(gen, "ingresso_atr_pct")["features"][-1]["vol_pct"] == 0.02
    # soglia sotto il gradino minimo: non esprimibile
    assert varianti_da_referto(gen, "ingresso_atr_pct", min(_VOL_PCT)) is None
    # feature gia' presente: scende di un gradino, mai sale, mai sotto il minimo
    con = _spec_rsi(solo="long", features=[{"kind": "rsi_extreme", "low": 30.0, "high": 70.0},
                                           {"kind": "volatility_regime", "vol_pct": 0.03}])
    v2 = varianti_da_referto(con, "ingresso_atr_pct", 0.025)
    assert [f["vol_pct"] for f in v2["features"] if f["kind"] == "volatility_regime"] == [0.02]
    assert len(v2["features"]) == 2
    assert varianti_da_referto(con, "ingresso_atr_pct", 0.05) is None, "0,03 non e' sotto 0,03"
    con_min = _spec_rsi(solo="long", features=[{"kind": "rsi_extreme", "low": 30.0, "high": 70.0},
                                               {"kind": "volatility_regime", "vol_pct": 0.01}])
    assert varianti_da_referto(con_min, "ingresso_atr_pct", 0.025) is None


def test_figlia_ingresso_rsi_stringe_la_banda_di_un_gradino():
    gen = _spec_rsi()                                   # 30 / 70
    v = varianti_da_referto(gen, "ingresso_rsi")
    assert v["features"] == [{"kind": "rsi_extreme", "low": 25.0, "high": 75.0}]
    assert v["id"] != gen["id"] and firma_spec(v) != firma_spec(gen)
    # ai limiti della griglia: si muove solo il lato che puo'; ai limiti su
    # entrambi, None
    ai_limiti = _spec_rsi(features=[{"kind": "rsi_extreme", "low": min(_RSI_LOW), "high": 70.0}])
    v2 = varianti_da_referto(ai_limiti, "ingresso_rsi")
    assert v2["features"] == [{"kind": "rsi_extreme", "low": min(_RSI_LOW), "high": 75.0}]
    fermo = _spec_rsi(features=[{"kind": "rsi_extreme", "low": min(_RSI_LOW), "high": max(_RSI_HIGH)}])
    assert varianti_da_referto(fermo, "ingresso_rsi") is None
    senza = _spec_rsi(features=[{"kind": "rsi_momentum", "mid": 50.0}])
    assert varianti_da_referto(senza, "ingresso_rsi") is None
    assert varianti_da_referto(_spec_rsi(features=[{"kind": "bb_touch"}]), "ingresso_rsi") is None


def test_le_figlie_d_ingresso_sono_pure_e_non_toccano_il_genitore():
    gen = _spec_rsi(solo="long")
    copia = json.loads(json.dumps(gen))
    for tipo in TIPI_INGRESSO:
        varianti_da_referto(gen, tipo, 0.02)
    assert gen == copia


# --------------------------------------------------------------------------- #
# 5. La discovery mette la figlia in coda                                        #
# --------------------------------------------------------------------------- #
def test_varianti_dai_referti_crea_la_figlia_per_i_nuovi_tipi():
    tf = settings.ORCHESTRATOR_TIMEFRAME
    a = _spec_rsi()
    existing = {a["id"]: a}
    doc = {"ipotesi": [_ipotesi(a["id"], "ingresso_adx"), _ipotesi(a["id"], "ingresso_vol_ratio"),
                       _ipotesi(a["id"], "ingresso_rsi"), _ipotesi(a["id"], "ingresso_atr_pct"),
                       _ipotesi(a["id"], "scala_stretta")]}
    out = varianti_dai_referti(_Fb(doc), existing, tf)
    assert sorted(v["ipotesi"] for v in out) == ["ingresso_adx", "ingresso_rsi", "ingresso_vol_ratio"]
    assert all(v["origine"] == "referto" and v["genitore"] == a["id"] for v in out)
    # il gate «ha gia' la risposta» solo per il lato da spegnere: un PF buono
    # per direzione non ferma una variante d'ingresso
    pairs = {f"AUSDT|{a['id']}": {"strategy": a["id"],
                                  "direzione_pf": {"long": {"n": 50, "pf": 1.4},
                                                   "short": {"n": 50, "pf": 1.4}}}}
    doc2 = {"ipotesi": [_ipotesi(a["id"], "ingresso_adx"), _ipotesi(a["id"], "solo_long")]}
    out2 = varianti_dai_referti(_Fb(doc2), existing, tf, pairs=pairs)
    assert [v["ipotesi"] for v in out2] == ["ingresso_adx"]


def test_varianti_dai_referti_passa_la_soglia_misurata_e_la_data():
    tf = settings.ORCHESTRATOR_TIMEFRAME
    a = _spec_rsi(solo="long")
    existing = {a["id"]: a}
    ip = {**_ipotesi(a["id"], "ingresso_atr_pct"), "soglia": 0.0145, "da_ts": 1000.0}
    out = varianti_dai_referti(_Fb({"ipotesi": [ip]}), existing, tf)
    assert len(out) == 1
    assert out[0]["features"][-1] == {"kind": "volatility_regime", "vol_pct": 0.01}
    assert out[0]["ipotesi_da"] == 1000.0
    # soglia storta: si ripiega su quella dichiarata, il giro non si ferma
    ip["soglia"] = "boh"
    out = varianti_dai_referti(_Fb({"ipotesi": [ip]}), existing, tf)
    assert out[0]["features"][-1]["vol_pct"] == 0.02


def test_trade_stats_stampa_le_condizioni_d_ingresso(monkeypatch, capsys):
    from scripts import trade_stats

    class _FakeFB:
        def query_collection(self, *a, **k):
            rows = [_perso_ingresso(i, adx=12.0) for i in range(4)] + [_vinto(i, adx=30.0) for i in range(2)]
            for i, r in enumerate(rows):
                r["strategy"] = "gen_z"
                r["exit_ts"] = 10.0 + i
            return rows

        def get_rtdb(self, *a, **k):
            return None

        def get_doc(self, *a, **k):
            return None

    monkeypatch.setattr(trade_stats, "get_firebase", lambda: _FakeFB())
    assert trade_stats.main() == 0
    out = capsys.readouterr().out
    assert "CONDIZIONI D'INGRESSO (perdite d'ingresso vs vinti, per strategia con >= 4 perdite d'ingresso)" in out
    assert "gen_z: ingresso_adx — 4 perdite d'ingresso su 4 con ADX < 20 (mediana 12), vinti mediana 30 (campione 4)" in out
    riga = [r for r in out.splitlines() if r.strip().startswith("gen_z ") and "|" in r]
    assert len(riga) == 1 and "12.00|30.00" in riga[0] and "4/2" in riga[0]
