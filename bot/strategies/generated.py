"""
Strategie GENERATE — il "cervello" che inventa nuove strategie.

Una strategia generata NON è codice nuovo: è una combinazione DICHIARATIVA di
"feature" (mattoncini booleani su indicatori), interpretata da un unico motore
verificato (`GeneratedStrategy`). Questo permette di crearne a decine/centinaia
in sicurezza (nessun codice arbitrario eseguito) e di validarle con lo STESSO
gate del backtest (walk-forward OOS, al netto dei costi) delle 6 strategie base.

Spec di una strategia (pura DATA, salvabile su Firebase):
    {
      "id": "gen_ab12cd34",
      "features": [
          {"kind": "rsi_extreme", "low": 30, "high": 70},
          {"kind": "bb_touch"}
      ],
      "volume_mult": 0.0,        # >0 = filtro volume (volume > volume_sma*mult)
      "atr_mult_stop": 1.5,
      "rr": 2.0
    }

Ogni feature vota una direzione: (long_ok, short_ok). La strategia entra LONG se
TUTTE le feature sono long_ok (e simmetrico per lo SHORT). Niente contraddizioni.
"""
from __future__ import annotations

import hashlib
import json
from typing import Optional

from bot.core.models import AssetSnapshot, Direction, IndicatorSnapshot, Regime, StrategySignal
from bot.strategies.base import Strategy, StrategyContext

ALL_REGIMES = {Regime.BULL_TRENDING, Regime.BEAR_TRENDING, Regime.SIDEWAYS, Regime.HIGH_UNCERTAINTY}


def _feat_rsi_extreme(i: IndicatorSnapshot, price: float, f: dict):
    if i.rsi is None:
        return None
    return (i.rsi <= f.get("low", 30.0), i.rsi >= f.get("high", 70.0))


def _feat_rsi_momentum(i: IndicatorSnapshot, price: float, f: dict):
    if i.rsi is None:
        return None
    mid = f.get("mid", 50.0)
    return (i.rsi >= mid, i.rsi <= mid)


def _feat_bb_touch(i: IndicatorSnapshot, price: float, f: dict):
    if None in (i.bb_upper, i.bb_lower):
        return None
    return (price <= i.bb_lower, price >= i.bb_upper)


def _feat_bb_break(i: IndicatorSnapshot, price: float, f: dict):
    if None in (i.bb_upper, i.bb_lower):
        return None
    return (price >= i.bb_upper, price <= i.bb_lower)


def _feat_vwap_momentum(i: IndicatorSnapshot, price: float, f: dict):
    if i.vwap is None:
        return None
    return (price > i.vwap, price < i.vwap)


def _feat_vwap_reversion(i: IndicatorSnapshot, price: float, f: dict):
    if i.vwap is None:
        return None
    return (price < i.vwap, price > i.vwap)


def _feat_ema_cross(i: IndicatorSnapshot, price: float, f: dict):
    if None in (i.ema_fast, i.ema_slow):
        return None
    return (i.ema_fast > i.ema_slow, i.ema_fast < i.ema_slow)


def _feat_macd_cross(i: IndicatorSnapshot, price: float, f: dict):
    if None in (i.macd, i.macd_signal):
        return None
    return (i.macd > i.macd_signal, i.macd < i.macd_signal)


def _feat_macd_hist(i: IndicatorSnapshot, price: float, f: dict):
    if i.macd_hist is None:
        return None
    return (i.macd_hist > 0, i.macd_hist < 0)


def _feat_price_ema(i: IndicatorSnapshot, price: float, f: dict):
    if i.ema_slow is None:
        return None
    return (price > i.ema_slow, price < i.ema_slow)


def _feat_macd_zero(i: IndicatorSnapshot, price: float, f: dict):
    if i.macd is None:
        return None
    return (i.macd > 0, i.macd < 0)


def _feat_price_bb_mid(i: IndicatorSnapshot, price: float, f: dict):
    if i.bb_mid is None:
        return None
    return (price > i.bb_mid, price < i.bb_mid)


def _feat_stoch_extreme(i: IndicatorSnapshot, price: float, f: dict):
    if i.stoch_k is None:
        return None
    return (i.stoch_k <= f.get("low", 20.0), i.stoch_k >= f.get("high", 80.0))


def _feat_stoch_momentum(i: IndicatorSnapshot, price: float, f: dict):
    if None in (i.stoch_k, i.stoch_d):
        return None
    return (i.stoch_k > i.stoch_d, i.stoch_k < i.stoch_d)


def _feat_volatility_regime(i: IndicatorSnapshot, price: float, f: dict):
    """VOLATILITA' RELATIVA (ATR/prezzo) sopra/sotto una soglia.

    Aggiunta perche' il generatore era interamente fatto di oscillatori sullo
    stesso timeframe: sapeva DOVE sta il prezzo, mai in che CONDIZIONE e' il
    mercato. Le stesse soglie RSI significano cose diverse a volatilita' 0.5% o 5%."""
    if i.atr is None or price <= 0:
        return None
    vol = i.atr / price
    hi = f.get("vol_pct", 0.02)
    return (vol < hi, vol >= hi)      # (calmo, agitato): filtro di CONDIZIONE


def _feat_trend_strength(i: IndicatorSnapshot, price: float, f: dict):
    """ADX sopra/sotto soglia: distingue mercato che TENDE da mercato che oscilla.
    Con lo scale-out conta molto: i gradini alti si raggiungono solo se tende."""
    if i.adx is None:
        return None
    lo = f.get("adx_lo", 20.0)
    return (i.adx >= lo, i.adx < lo)


def _feat_volume_surge(i: IndicatorSnapshot, price: float, f: dict):
    """Volume sopra la sua media per un fattore: partecipazione reale al movimento
    (un breakout senza volume e' spesso rumore)."""
    if i.volume is None or not i.volume_sma:
        return None
    mult = f.get("vol_mult_feat", 1.5)
    return (i.volume >= i.volume_sma * mult, i.volume < i.volume_sma * mult)


def _feat_session(i: IndicatorSnapshot, price: float, f: dict):
    """SESSIONE oraria (UTC): la crypto non e' uniforme nelle 24h — la sessione
    asiatica e quella US hanno liquidita' e comportamenti diversi. Primo elemento
    NON tecnico del generatore."""
    from datetime import datetime, timezone
    h = datetime.now(timezone.utc).hour
    lo, hi = f.get("hour_from", 12), f.get("hour_to", 21)
    inside = (lo <= h < hi) if lo <= hi else (h >= lo or h < hi)
    return (inside, not inside)


# --------------------------------------------------------------------------- #
# IL MERCATO COME INGREDIENTE DELLA DECISIONE, NON COME VETO                   #
#                                                                              #
# 21 settembre 2026. Due short consecutivi su USELESSUSDT dentro una giornata   #
# di rialzo, -16,90 in quaranta minuti. Le feature che li hanno prodotti dicono #
# «RSI sopra 70 -> vendi» e «prezzo sopra la banda -> vendi»: guardano SOLO     #
# quella coin. Il mercato, per una strategia generata, non esisteva — non era   #
# «poco pesato», non era proprio nella stanza (`discover_strategies` non        #
# caricava nemmeno BTC).                                                       #
#                                                                              #
# La correzione NON e' vietare gli short quando il mercato sale. Dentro una     #
# giornata di rialzo ci sono ritracciamenti del 2-3%, e prenderli e' esattamente#
# il mestiere di una strategia di ritorno alla media. Il problema e' che la     #
# strategia non aveva modo di distinguere «sto vendendo un ritracciamento» da   #
# «sto stando davanti a un treno», perche' non vedeva il treno.                 #
#                                                                              #
# Quindi il mercato entra come MATTONCINO: il generatore puo' usarlo, il GATE   #
# misura se serve davvero, e nessuno gli impone una regola decisa a tavolino.   #
# Una feature di mercato che non aiuta viene bocciata come tutto il resto.      #
#                                                                              #
# Firma diversa dalle altre (`m` = snapshot del mercato) di proposito: cosi' le #
# diciotto feature esistenti non vengono toccate, e una spec che chiede il      #
# mercato dove il mercato non c'e' non produce segnale invece di inventarselo.  #
# --------------------------------------------------------------------------- #
#: L'asset che rappresenta «il mercato». BTC e' gia' il contesto che il gate
#: carica per le strategie cross-asset (`scripts/optimize.py:67`), quindi usando
#: lo stesso non serve una seconda pipeline dati.
MARKET_SYMBOL = "BTCUSDT"


class MercatoSnap:
    """Il minimo che serve alle feature di mercato: prezzo e due medie.

    Esiste per non far sapere alle feature come si naviga uno `AssetSnapshot`
    (quale timeframe, quale dizionario): cosi' si testano con tre numeri e non
    con mezzo modello."""

    __slots__ = ("price", "ema_fast", "ema_slow")

    def __init__(self, price, ema_fast, ema_slow):
        self.price, self.ema_fast, self.ema_slow = price, ema_fast, ema_slow


def mercato_da_contesto(ctx, timeframe: str):
    """Lo snapshot del mercato dal contesto cross-asset, o None.

    None NON viene mai sostituito con un valore di comodo: una spec che chiede
    il mercato dove il mercato non c'e' deve smettere di produrre segnali, non
    produrne di finti. E' la stessa regola dei dati sintetici nel backtest."""
    if ctx is None:
        return None
    asset = (getattr(ctx, "all_assets", None) or {}).get(MARKET_SYMBOL)
    if asset is None:
        return None
    ind = asset.ind(timeframe)
    if ind is None:
        return None
    return MercatoSnap(getattr(asset, "price", None), ind.ema_fast, ind.ema_slow)


def _mkt_market_trend(i, price: float, f: dict, m):
    """Va CON il mercato: long se il mercato sale, short se scende."""
    if m is None or m.ema_fast is None or m.ema_slow is None:
        return None
    return (m.ema_fast > m.ema_slow, m.ema_fast < m.ema_slow)


def _mkt_market_fade(i, price: float, f: dict, m):
    """Va CONTRO il mercato. Non e' il gemello inutile del precedente: e'
    l'ipotesi opposta, e serve che il gate possa misurarle entrambe invece di
    ricevere gia' decisa quella che credo io."""
    if m is None or m.ema_fast is None or m.ema_slow is None:
        return None
    return (m.ema_fast < m.ema_slow, m.ema_fast > m.ema_slow)


def _mkt_relative_strength(i, price: float, f: dict, m):
    """FORZA RELATIVA: la coin e' piu' forte o piu' debole del mercato?

    E' il mattoncino che mancava di piu', ed e' fra le basi del mestiere:
    comprare cio' che sale piu' del mercato e vendere cio' che sale meno. Con
    questo una strategia puo' shortare una coin debole ANCHE in un mercato
    rialzista — che e' la cosa sensata — invece di shortare quella che corre
    piu' di tutte solo perche' ha l'RSI alto.

    Si confrontano due distanze dalla media, non due prezzi: una percentuale e'
    paragonabile fra coin, un prezzo no."""
    if m is None or None in (i.ema_slow, m.ema_slow) or not i.ema_slow or not m.ema_slow:
        return None
    if m.price is None or not m.price:
        return None
    coin = (price - i.ema_slow) / i.ema_slow
    mercato = (m.price - m.ema_slow) / m.ema_slow
    soglia = float(f.get("rs_gap", 0.0))
    return (coin - mercato >= soglia, mercato - coin >= soglia)


#: feature che guardano il MERCATO. Firma `(i, price, f, m)`; `m` e' lo snapshot
#: dell'asset di riferimento (BTC) allo stesso istante, o None se non disponibile.
MARKET_FEATURES = {
    "market_trend": _mkt_market_trend,
    "market_fade": _mkt_market_fade,
    "relative_strength": _mkt_relative_strength,
}


# --------------------------------------------------------------------------- #
# LA CONFERMA A 1 ORA — «guardare la moneta con due occhi»                     #
#                                                                              #
# Idea del proprietario, 22 set 2026: il trader opera a 5 o 15 minuti ma prima #
# di aprire guarda l'ora e chiede «la direzione che prendo e' coerente con     #
# quello che vedo a 1 ora?». Qui e' un MATTONCINO direzionale, non una regola  #
# per tutti: il gate misura coin per coin se la conferma aiuta, e nel registro #
# convivono strategie con e senza. Il costo — meno segnali, e qualche          #
# ritracciamento vero perso perche' le medie orarie girano tardi — lo paga     #
# solo chi la usa, e solo se il gate lo giudica un buon affare.                #
#                                                                              #
# L'occhio a 1 ora esiste gia' da tutte e due le parti: il motore di backtest   #
# porta la 1h REALE nello snapshot (senza look-ahead, `_htf_for`) e il bot la  #
# calcola fra i suoi TIMEFRAMES. Nessuna nuova pipeline: parita' gratis.       #
# --------------------------------------------------------------------------- #
def _htf_confirm(h, price: float, f: dict):
    """Long solo se a 1 ora la media veloce sta sopra la lenta; short solo se
    sotto. `h` e' lo snapshot degli indicatori a 1h della STESSA coin."""
    if h is None or h.ema_fast is None or h.ema_slow is None:
        return None
    return (h.ema_fast > h.ema_slow, h.ema_fast < h.ema_slow)


def _htf_fade(h, price: float, f: dict):
    """L'IPOTESI OPPOSTA alla conferma, e il proprietario ha insistito perche'
    e' «vitale»: dentro un trend orario in salita ci sono cali momentanei, e uno
    short che li sfrutta DEVE potersi aprire. Qui si vende l'eccesso rispetto
    alla media oraria: short se il prezzo sta sopra la media lenta a 1h di
    almeno `htf_gap` (frazione del prezzo), long se sta sotto di altrettanto.
    Non guarda la direzione del trend: guarda quanto il prezzo se n'e'
    allontanato. Con `htf_confirm` nella stessa spec sarebbero in contraddizione:
    sono incompatibili, e il gate misura quale delle due paga, coin per coin."""
    if h is None or h.ema_slow is None or not h.ema_slow:
        return None
    gap = (price - h.ema_slow) / h.ema_slow
    soglia = float(f.get("htf_gap", 0.0))
    return (gap <= -soglia, gap >= soglia)


#: feature che guardano il TIMEFRAME SUPERIORE della stessa coin. Firma
#: `(h, price, f)`: `h` e' `asset.ind("1h")`, o None se non disponibile.
HTF_FEATURES = {
    "htf_confirm": _htf_confirm,
    "htf_fade": _htf_fade,
}


def feature_esiste(kind: str) -> bool:
    """L'UNICA definizione di «questa feature esiste».

    Le feature di mercato hanno una firma diversa e quindi vivono in un
    dizionario separato. Chi valida le proposte deve guardare entrambi: la prima
    versione guardava solo `FEATURE_LIBRARY`, e il validatore avrebbe scartato
    come «inesistenti» proprio le feature appena aggiunte al vocabolario. Un
    controllo che non conosce meta' del vocabolario e' una trappola, non una
    regola — l'abbiamo gia' pagata il 20 settembre con `rr`."""
    return kind in FEATURE_LIBRARY or kind in MARKET_FEATURES or kind in HTF_FEATURES

def _feat_not_stretched(i: IndicatorSnapshot, price: float, f: dict):
    """NON SOVRAESTESO: il prezzo sta entro `stretch_max` ATR dalla media lenta.

    E' la parola che mancava al vocabolario il 21 settembre 2026. MUBARAKUSDT a
    +37% in trenta ore, RSI 88: per `rsi_extreme` e `bb_touch` era il segnale di
    vendita piu' forte possibile, e nessun mattoncino poteva dire «questa non e'
    un'oscillazione, e' una salita verticale». Ora una strategia di ritorno alla
    media puo' dichiarare fino a dove accetta di vendere la forza — e il gate
    misura se serve. Non direzionale: blocca entrambi i lati."""
    if None in (i.atr, i.ema_slow) or not i.atr:
        return None
    ok = abs(price - i.ema_slow) / i.atr <= float(f.get("stretch_max", 3.0))
    return (ok, ok)


def _feat_adx_below(i: IndicatorSnapshot, price: float, f: dict):
    """ADX SOTTO soglia: opera solo quando il trend e' debole.

    E' l'opposto di `min_adx`, che lascia passare il segnale SOLO con ADX alto —
    cioe' solo quando un trend c'e'. Combinato con feature di ritorno alla media,
    `min_adx` significa «opera solo quando c'e' un trend forte, e vendilo»: la
    selezione attiva dei momenti peggiori, misurata il 21 settembre 2026. Qui il
    generatore ha finalmente anche l'ipotesi contraria; sceglie il gate."""
    if i.adx is None:
        return None
    ok = i.adx < float(f.get("adx_hi", 30.0))
    return (ok, ok)


# nome feature -> (funzione, è_direzionale). Le non direzionali sono filtri.
FEATURE_LIBRARY = {
    "rsi_extreme": _feat_rsi_extreme,
    "rsi_momentum": _feat_rsi_momentum,
    "bb_touch": _feat_bb_touch,
    "bb_break": _feat_bb_break,
    "vwap_momentum": _feat_vwap_momentum,
    "vwap_reversion": _feat_vwap_reversion,
    "ema_cross": _feat_ema_cross,
    "macd_cross": _feat_macd_cross,
    "macd_hist": _feat_macd_hist,
    "price_ema": _feat_price_ema,
    "macd_zero": _feat_macd_zero,
    "price_bb_mid": _feat_price_bb_mid,
    "stoch_extreme": _feat_stoch_extreme,
    "stoch_momentum": _feat_stoch_momentum,
    # --- CONDIZIONE di mercato (non direzionali): dicono QUANDO operare, non dove
    "volatility_regime": _feat_volatility_regime,
    "trend_strength": _feat_trend_strength,
    "volume_surge": _feat_volume_surge,
    "session": _feat_session,
    "not_stretched": _feat_not_stretched,
    "adx_below": _feat_adx_below,
}


#: FAMIGLIE di strategia per il selettore (docs/disegno_cervello.md, Punto 2):
#: un modello per famiglia, non per strategia — per strategia i trade sono
#: troppo pochi. Contano solo le feature DIREZIONALI: i filtri (volatilita',
#: sessione, volume...) dicono quando operare, non in che verso.
FAMIGLIE_FEATURE = {
    "reversion": {"rsi_extreme", "bb_touch", "vwap_reversion", "stoch_extreme",
                  "market_fade", "htf_fade"},
    "momentum": {"rsi_momentum", "ema_cross", "macd_cross", "macd_hist", "macd_zero",
                 "price_ema", "price_bb_mid", "vwap_momentum", "stoch_momentum",
                 "market_trend", "htf_confirm", "relative_strength"},
    "breakout": {"bb_break"},
}


def famiglia_spec(spec: dict) -> str:
    """"reversion" | "momentum" | "breakout" | "altro": la famiglia di una spec.

    Vince la famiglia con piu' feature direzionali; a parita' l'ordine e'
    reversion > momentum > breakout (una spec che compra l'RSI basso E la media
    che gira e' prima di tutto un rientro alla media). Nessuna feature
    direzionale -> "altro". E' l'etichetta con cui il dataset del selettore
    raggruppa i trade (passo 0, 24 set 2026): deve restare STABILE, perche' un
    modello addestrato su una famiglia si applica ai trade della stessa."""
    kinds = [f.get("kind") for f in (spec.get("features") or []) if isinstance(f, dict)]
    conteggi = {fam: sum(1 for k in kinds if k in feats)
                for fam, feats in FAMIGLIE_FEATURE.items()}
    vincente, massimo = "altro", 0
    for fam in ("reversion", "momentum", "breakout"):   # ordine = tie-break
        if conteggi[fam] > massimo:
            vincente, massimo = fam, conteggi[fam]
    return vincente


def spec_id(spec: dict) -> str:
    """Hash stabile della LOGICA (feature+soglie), così la stessa strategia ha
    sempre lo stesso id tra run (la validazione cumulativa funziona per nome).
    Include il TIMEFRAME: la stessa logica a 15m e a 1h sono strategie DIVERSE
    (SL/TP/durate diverse) — senza, una spec rigenerata dopo un cambio timeframe
    erediterebbe pesi e storia della gemella dell'era precedente."""
    from bot.config import settings
    payload = {
        "features": sorted((f.get("kind"), tuple(sorted((k, v) for k, v in f.items() if k != "kind")))
                           for f in spec.get("features", [])),
        "volume_mult": spec.get("volume_mult", 0.0),
        "min_adx": spec.get("min_adx", 0.0),
        "atr_mult_stop": spec.get("atr_mult_stop"),
        "rr": spec.get("rr"),
        # dal 22 set 2026 la spec puo' portare il SUO timeframe (strategie native
        # a 1 ora): se manca, e' quella del bot, come e' sempre stato — cosi' gli
        # id delle spec esistenti non cambiano di una virgola.
        "timeframe": spec.get("timeframe") or settings.ORCHESTRATOR_TIMEFRAME,
    }
    # dal 23 set 2026 una spec puo' operare UN SOLO lato (`solo`: "long" o
    # "short"): e' la variante che il paper propone quando un lato perde sempre
    # (backlog B8). Entra nell'hash SOLO se c'e' ed e' valido, per la stessa
    # ragione del timeframe: gli id delle spec note non devono cambiare di una
    # virgola. Normalizzato come lo legge GeneratedStrategy: "Long" e "long"
    # sono la stessa strategia, "boh" e' come non averlo.
    # Da dove viene la variante (origine/genitore/ipotesi) NON e' logica: due
    # spec identiche nate in modi diversi sono la stessa strategia.
    solo = str(spec.get("solo") or "").lower()
    if solo in ("long", "short"):
        payload["solo"] = solo
    h = hashlib.sha1(json.dumps(payload, sort_keys=True, default=str).encode()).hexdigest()[:8]
    return f"gen_{h}"


#: gli indicatori che ogni feature LEGGE (per `GeneratedStrategy.spiega`): serve a
#: stampare, accanto al voto, i numeri da cui e' nato. "price" = il prezzo di
#: decisione. Non cambia la valutazione: e' documentazione leggibile da macchina.
_CAMPI_FEATURE = {
    "rsi_extreme": ("rsi",), "rsi_momentum": ("rsi",),
    "bb_touch": ("price", "bb_lower", "bb_upper"), "bb_break": ("price", "bb_lower", "bb_upper"),
    "vwap_momentum": ("price", "vwap"), "vwap_reversion": ("price", "vwap"),
    "ema_cross": ("ema_fast", "ema_slow"), "macd_cross": ("macd", "macd_signal"),
    "macd_hist": ("macd_hist",), "price_ema": ("price", "ema_slow"), "macd_zero": ("macd",),
    "price_bb_mid": ("price", "bb_mid"), "stoch_extreme": ("stoch_k",),
    "stoch_momentum": ("stoch_k", "stoch_d"), "volatility_regime": ("price", "atr"),
    "trend_strength": ("adx",), "volume_surge": ("volume", "volume_sma"), "session": (),
    "not_stretched": ("price", "ema_slow", "atr"), "adx_below": ("adx",),
}


def _valori_feature(f: dict, i, price: float, mercato, htf) -> dict:
    """I numeri che una feature ha guardato, piu' i suoi parametri. Solo lettura."""
    kind = f.get("kind")
    out = {k: v for k, v in f.items() if k != "kind"}
    if kind in MARKET_FEATURES:
        out["price"] = price
        if i is not None:
            out["ema_slow"] = i.ema_slow
        out["mercato"] = (None if mercato is None else
                          {"price": mercato.price, "ema_fast": mercato.ema_fast, "ema_slow": mercato.ema_slow})
        return out
    if kind in HTF_FEATURES:
        out["price"] = price
        out["1h"] = (None if htf is None else {"ema_fast": htf.ema_fast, "ema_slow": htf.ema_slow})
        return out
    if kind == "session":
        from datetime import datetime, timezone
        out["ora_utc"] = datetime.now(timezone.utc).hour
    for c in _CAMPI_FEATURE.get(kind, ()):
        out[c] = price if c == "price" else (getattr(i, c, None) if i is not None else None)
    return out


class GeneratedStrategy(Strategy):
    """Interpreta una spec dichiarativa. Attiva in tutti i regimi: dove funziona
    lo decide il backtest, non una teoria a priori."""

    def __init__(self, spec: dict) -> None:
        super().__init__(spec.get("params"))
        self.spec = spec
        self.name = spec.get("id") or spec_id(spec)
        self.active_regimes = ALL_REGIMES
        self.description = self._describe()
        self._features = spec.get("features", [])
        # IL TIMEFRAME E' DELLA SPEC (22 set 2026, strategie native a 1 ora). Se
        # manca e' quello del bot, com'e' sempre stato. Da qui dipendono gli
        # indicatori letti (`asset.ind(self._tf)`), lo stop in ATR e — nel bot —
        # l'orologio su cui la strategia decide.
        from bot.config import settings as _st   # locale, come in spec_id (import circolare)
        self.timeframe = spec.get("timeframe") or _st.ORCHESTRATOR_TIMEFRAME
        self._volume_mult = float(spec.get("volume_mult", 0.0) or 0.0)
        self._min_adx = float(spec.get("min_adx", 0.0) or 0.0)
        self._atr_mult_stop = float(spec.get("atr_mult_stop", 1.5))
        self._rr = float(spec.get("rr", 2.0))
        # UN SOLO LATO (23 set 2026, backlog B8). Il paper ha misurato piu' volte
        # una strategia che vince sui long e perde tutti gli short (o viceversa):
        # invece di buttare via l'idea, il paper PROPONE la variante «solo long»
        # e il gate la prova sulla storia come qualunque altra candidata. Qui la
        # spec dichiara il lato; il segnale dell'altro lato non nasce.
        solo = str(spec.get("solo") or "").lower()
        self.solo = solo if solo in ("long", "short") else None
        # IL MERCATO SI GUARDA SOLO SE LA SPEC LO USA. Il 22 set 2026 il giro della
        # discovery e' passato da ~2h a oltre 2h53 (finestra di 3h sforata, giro
        # delle 06:00 saltato): il contesto di mercato veniva risolto a OGNI
        # candela per OGNI spec, anche per le ~550 che non hanno feature di
        # mercato. Sul percorso caldo del backtest (milioni di candele) anche pochi
        # microsecondi diventano decine di minuti. La spec sa dalla nascita se le
        # serve: si decide una volta qui, non a ogni barra.
        self.usa_mercato = any((f.get("kind") in MARKET_FEATURES)
                               for f in self._features if isinstance(f, dict))
        self.usa_htf = any((f.get("kind") in HTF_FEATURES)
                           for f in self._features if isinstance(f, dict))

    def _describe(self) -> str:
        parts = []
        for f in self.spec.get("features", []):
            extra = " ".join(f"{k}={v}" for k, v in f.items() if k != "kind")
            parts.append(f"{f.get('kind')}{(' ' + extra) if extra else ''}")
        testo = " AND ".join(parts) or "vuota"
        solo = str(self.spec.get("solo") or "").lower()
        if solo in ("long", "short"):
            testo += f" [solo {solo}]"
        return testo

    @property
    def _tf(self) -> str:
        return self.timeframe

    # ----------------------------------------------------------------------- #
    # LA REGOLA, VALUTATA UNA VOLTA SOLA (27 set 2026, backlog J12)             #
    #                                                                          #
    # `generate_signal` e `spiega` passano dalla STESSA `_verdetto`: il primo   #
    # ne fa un segnale, il secondo lo restituisce feature per feature. Prima   #
    # la valutazione stava tutta dentro `generate_signal`, e per capire perche' #
    # `gen_6d06dca0` aveva aperto 6 trade su ORCAUSDT/VETUSDT che il motore non #
    # apre (ops 0308, classe IGNOTO) non c'era modo di chiedere alla strategia  #
    # «quale feature ti ha fermato?» senza riscrivere la regola a mano — e una  #
    # regola riscritta a mano e' proprio cio' che non si puo' confrontare.      #
    # ----------------------------------------------------------------------- #
    def _prezzo_decisione(self, asset: AssetSnapshot) -> float:
        """Il prezzo su cui la REGOLA decide.

        Dal 27 set 2026 (`DECISIONE_SU_CHIUSURA`, backlog J12) e' la chiusura
        dell'ultima candela CHIUSA (`asset.close_chiusa`), la stessa su cui
        decide il motore di backtest (`engine._snapshot_from_frame`: `price =
        row["close"]`). Il bot decideva invece sul prezzo VIVO della candela in
        formazione (`price_agent.build_snapshot`: `price = candles[-1].close`):
        ops 0308 ha misurato 5 trade (DEXEUSDT, GPSUSDT) con indicatori identici
        e regola scattata da una parte sola per 1-4 decimillesimi di differenza.
        Il prezzo vivo resta `asset.price` per tutto il resto: esecuzione, stop,
        gate di rischio, feature del selettore. Se `close_chiusa` manca (snapshot
        vecchi, test) si torna al prezzo vivo, com'era."""
        from bot.config import settings as _st
        cc = getattr(asset, "close_chiusa", None)
        if _st.DECISIONE_SU_CHIUSURA and cc is not None:
            return float(cc)
        return asset.price

    def _valuta_feature(self, f: dict, i: IndicatorSnapshot, price: float, mercato, htf):
        """(long_ok, short_ok) di UNA feature, o None se non si puo' valutare
        (feature sconosciuta o dato mancante). E' l'unico posto che sa in quale
        vocabolario vive una feature."""
        kind = f.get("kind")
        if kind in MARKET_FEATURES:
            return MARKET_FEATURES[kind](i, price, f, mercato)
        if kind in HTF_FEATURES:
            return HTF_FEATURES[kind](htf, price, f)
        fn = FEATURE_LIBRARY.get(kind)
        if fn is None:
            return None
        return fn(i, price, f)

    def _verdetto(self, asset: AssetSnapshot, ctx=None, prezzo: Optional[float] = None) -> dict:
        """La regola valutata feature per feature. PURA: non tocca lo snapshot e
        non decide niente da sola — `generate_signal` legge `direzione_finale`.

        Ritorna:
          features        {nome: {"kind", "long", "short", "valori"}} nell'ordine
                          della spec (nome = kind, o kind#n se ripetuto); long/short
                          None quando la feature non si e' potuta valutare
          direzione_finale "long" | "short" | None
          motivo          UNA frase: perche' quella direzione, o perche' nessuna
          prezzo          il prezzo su cui la regola ha deciso
          filtri          esito dei filtri globali (volume, min_adx)
        `prezzo` sovrascrive il prezzo di decisione: serve allo strumento degli
        ingressi per chiedere «e col prezzo vivo del paper?» senza copiare lo
        snapshot."""
        out: dict = {"features": {}, "direzione_finale": None, "motivo": "",
                     "prezzo": None, "prezzo_vivo": asset.price,
                     "close_chiusa": getattr(asset, "close_chiusa", None),
                     "filtri": {}, "solo": self.solo, "timeframe": self._tf}
        i = asset.ind(self._tf)
        if i is None:
            out["motivo"] = f"indicatori del timeframe {self._tf} assenti"
            return out
        if not self._features:
            out["motivo"] = "spec senza feature"
            return out
        price = float(prezzo) if prezzo is not None else self._prezzo_decisione(asset)
        out["prezzo"] = price
        mercato = mercato_da_contesto(ctx, self._tf) if self.usa_mercato else None
        htf = asset.ind("1h") if self.usa_htf else None
        long_ok, short_ok = True, True
        blocco: Optional[str] = None
        for f in self._features:
            kind = str(f.get("kind"))
            nome = kind
            n = 2
            while nome in out["features"]:
                nome, n = f"{kind}#{n}", n + 1
            res = self._valuta_feature(f, i, price, mercato, htf)
            voce = {"kind": kind, "long": None if res is None else bool(res[0]),
                    "short": None if res is None else bool(res[1]),
                    "valori": _valori_feature(f, i, price, mercato, htf)}
            out["features"][nome] = voce
            if res is None and blocco is None:
                blocco = (f"feature {nome} sconosciuta" if not feature_esiste(kind)
                          else f"feature {nome} senza dati")
            if res is not None:
                long_ok = long_ok and res[0]
                short_ok = short_ok and res[1]
        if blocco is not None:
            out["motivo"] = blocco
            return out
        # filtri globali (stesse soglie di sempre, sugli indicatori, non sul prezzo)
        if self._volume_mult > 0:
            ok = not (i.volume is None or i.volume_sma is None
                      or i.volume <= i.volume_sma * self._volume_mult)
            out["filtri"]["volume"] = {"ok": ok, "volume": i.volume, "volume_sma": i.volume_sma,
                                       "mult": self._volume_mult}
            if not ok:
                out["motivo"] = "filtro volume: volume non sopra la media per il fattore"
                return out
        if self._min_adx > 0:
            ok = not (i.adx is None or i.adx < self._min_adx)
            out["filtri"]["min_adx"] = {"ok": ok, "adx": i.adx, "min": self._min_adx}
            if not ok:
                out["motivo"] = f"filtro ADX: {i.adx} sotto {self._min_adx:g}"
                return out
        if long_ok == short_ok:
            frena = [n for n, v in out["features"].items() if not v["long"] and not v["short"]]
            if long_ok:
                out["motivo"] = "contraddittorio: tutte le feature dicono si a entrambi i lati"
            else:
                out["motivo"] = ("nessuna direzione netta" + (": fermano " + ", ".join(frena)
                                                              if frena else ""))
            return out
        if self.solo == "long" and short_ok:
            out["motivo"] = "lato escluso dalla spec (solo long): il segnale sarebbe short"
            return out
        if self.solo == "short" and long_ok:
            out["motivo"] = "lato escluso dalla spec (solo short): il segnale sarebbe long"
            return out
        out["direzione_finale"] = "long" if long_ok else "short"
        out["motivo"] = f"{out['direzione_finale'].upper()}: tutte le feature concordano"
        return out

    def spiega(self, asset: AssetSnapshot, ctx=None, prezzo: Optional[float] = None) -> dict:
        """SOLA LETTURA: la stessa valutazione di `generate_signal`, feature per
        feature, senza produrre ne' alterare alcuna decisione. Vedi `_verdetto`
        per il formato. Un test (`tests/test_spiega.py`) pretende che
        `spiega(...)["direzione_finale"]` e `generate_signal(...)` concordino
        sempre: se un giorno divergono, e' `_verdetto` che va guardata, non
        questo metodo."""
        return self._verdetto(asset, ctx, prezzo=prezzo)

    def generate_signal(
        self, asset: AssetSnapshot, ctx: Optional[StrategyContext] = None
    ) -> Optional[StrategySignal]:
        v = self._verdetto(asset, ctx)
        if v["direzione_finale"] is None:
            return None
        direction = Direction.LONG if v["direzione_finale"] == "long" else Direction.SHORT
        # stop e target restano sul prezzo VIVO (`asset.price`): e' il prezzo a cui
        # il trade si apre davvero, e lo stop in ATR si misura da li'
        stop, target = self._atr_stop_target(asset, direction, self._tf, self._atr_mult_stop, self._rr)
        return self._signal(asset, direction, confidence=60.0,
                            reasoning=f"[gen] {self.description}", stop=stop, target=target)
