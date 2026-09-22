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
    h = hashlib.sha1(json.dumps(payload, sort_keys=True, default=str).encode()).hexdigest()[:8]
    return f"gen_{h}"


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
        return " AND ".join(parts) or "vuota"

    @property
    def _tf(self) -> str:
        return self.timeframe

    def generate_signal(
        self, asset: AssetSnapshot, ctx: Optional[StrategyContext] = None
    ) -> Optional[StrategySignal]:
        i = asset.ind(self._tf)
        if i is None or not self._features:
            return None
        price = asset.price
        # Il mercato si risolve UNA volta, non per feature: se manca e la spec lo
        # chiede, il segnale non nasce. Meglio nessun trade che un trade deciso
        # su un mercato immaginario.
        mercato = mercato_da_contesto(ctx, self._tf) if self.usa_mercato else None
        # l'occhio a 1 ora: solo se la spec lo chiede (stesso principio del mercato)
        htf = asset.ind("1h") if self.usa_htf else None
        long_ok, short_ok = True, True
        for f in self._features:
            kind = f.get("kind")
            if kind in MARKET_FEATURES:
                res = MARKET_FEATURES[kind](i, price, f, mercato)
            elif kind in HTF_FEATURES:
                res = HTF_FEATURES[kind](htf, price, f)
            else:
                fn = FEATURE_LIBRARY.get(kind)
                if fn is None:
                    return None
                res = fn(i, price, f)
            if res is None:
                return None  # dati indicatore mancanti -> niente segnale
            long_ok = long_ok and res[0]
            short_ok = short_ok and res[1]

        # filtro volume opzionale (gate su entrambe le direzioni)
        if self._volume_mult > 0:
            if i.volume is None or i.volume_sma is None or i.volume <= i.volume_sma * self._volume_mult:
                return None
        # filtro ADX opzionale: opera solo se il trend è abbastanza forte
        if self._min_adx > 0:
            if i.adx is None or i.adx < self._min_adx:
                return None

        if long_ok == short_ok:
            return None  # nessuna direzione netta (o entrambe -> contraddittorio)
        direction = Direction.LONG if long_ok else Direction.SHORT
        stop, target = self._atr_stop_target(asset, direction, self._tf, self._atr_mult_stop, self._rr)
        return self._signal(asset, direction, confidence=60.0,
                            reasoning=f"[gen] {self.description}", stop=stop, target=target)
