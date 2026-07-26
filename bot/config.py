"""
Configurazione centrale del bot.

IMPORTANTE — separazione delle responsabilità:
  * Questo file contiene impostazioni operative e DEFAULT regolabili.
  * I LIMITI DI SICUREZZA HARDCODED (hard cap leverage/size, circuit breaker)
    NON stanno qui: vivono in `bot/risk/hard_limits.py`, non sono modificabili
    né da config, né da Firebase, né dall'LLM.
  * I parametri regolabili dall'utente (leverage, risk per trade) vivono su
    Firebase in `user_risk_settings`; i valori qui sotto sono solo i fallback
    usati se Firebase non è raggiungibile.
"""
from __future__ import annotations

import os
from functools import lru_cache

from dotenv import load_dotenv

load_dotenv()


def timeframe_hours(tf: str) -> float:
    """Durata di UNA candela del timeframe in ORE. Helper CONDIVISO (config, engine,
    executor, script): un'unica mappa, niente valori 1h hardcoded sparsi."""
    return {"1m": 1 / 60, "5m": 1 / 12, "15m": 0.25,
            "30m": 0.5, "1h": 1.0, "4h": 4.0}.get(tf, 1.0)


def _get_bool(key: str, default: bool) -> bool:
    val = os.getenv(key)
    if val is None:
        return default
    return val.strip().lower() in {"1", "true", "yes", "y", "on"}


def _get_float(key: str, default: float) -> float:
    try:
        return float(os.getenv(key, default))
    except (TypeError, ValueError):
        return default


class Settings:
    """Impostazioni globali, lette una sola volta all'avvio."""

    # ---- Modalità ----
    # DRY_RUN True => paper trading, nessun ordine reale (GATE 2). Default sicuro.
    DRY_RUN: bool = _get_bool("DRY_RUN", True)

    # ---- Binance ----
    BINANCE_API_KEY: str = os.getenv("BINANCE_API_KEY", "")
    BINANCE_API_SECRET: str = os.getenv("BINANCE_API_SECRET", "")
    BINANCE_TESTNET: bool = _get_bool("BINANCE_TESTNET", True)
    QUOTE_ASSET: str = "USDT"  # universo: tutti i perpetual *USDT

    # ---- Anthropic / Claude ----
    # NB: usiamo `or` (non il default di getenv) perché nei workflow GitHub una
    # variabile mappata a un secret inesistente arriva come STRINGA VUOTA, non
    # come assente — e una stringa vuota farebbe fallire l'API ("model: String
    # should have at least 1 character").
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    ANTHROPIC_MODEL: str = os.getenv("ANTHROPIC_MODEL") or "claude-opus-4-8"

    # ---- Data agents ----
    LUNARCRUSH_API_KEY: str = os.getenv("LUNARCRUSH_API_KEY", "")
    COINGLASS_API_KEY: str = os.getenv("COINGLASS_API_KEY", "")
    NEWSAPI_KEY: str = os.getenv("NEWSAPI_KEY", "")

    # ---- Firebase ----
    FIREBASE_SERVICE_ACCOUNT: str = os.getenv("FIREBASE_SERVICE_ACCOUNT", "")
    FIREBASE_RTDB_URL: str = os.getenv("FIREBASE_RTDB_URL", "")

    # ---- Telegram ----
    TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
    TELEGRAM_CHAT_ID: str = os.getenv("TELEGRAM_CHAT_ID", "")

    # ---- Fallback parametri regolabili (i valori reali vengono da Firebase) ----
    # Questi sono usati solo se `user_risk_settings` non è raggiungibile.
    DEFAULT_LEVERAGE: float = 2.0
    DEFAULT_RISK_PER_TRADE: float = 0.01  # 1% del capitale

    # ---- Trading loop ----
    # TIMEFRAME UNICO del sistema. Le strategie leggono gli indicatori di QUESTO
    # timeframe (live) e l'optimizer/discover validano su QUESTO stesso intervallo
    # (default --interval). Un solo knob -> gate e live non possono divergere.
    # Il registro validato DEVE essere ricostruito quando questo valore cambia.
    ORCHESTRATOR_TIMEFRAME: str = os.getenv("ORCHESTRATOR_TIMEFRAME", "15m")
    SCAN_INTERVAL_HOURS: int = 4          # market scanner ogni 4h
    REGIME_INTERVAL_MINUTES: int = 60     # regime detector ogni ora
    MAX_OPEN_POSITIONS: int = int(os.getenv("MAX_OPEN_POSITIONS", "5"))  # cap posizioni APERTE
    # cap per-posizione: una singola posizione usa al massimo questa frazione di
    # equity come MARGINE -> piu' posizioni coesistono, nessuna prende tutta la
    # liquidita'. 1.0 = nessun cap (comportamento storico). In BACKTEST_PARITY, se
    # lasciato a 1.0, si usa in automatico 0.10 (~10 posizioni simultanee).
    MAX_POSITION_EQUITY_FRACTION: float = float(os.getenv("MAX_POSITION_EQUITY_FRACTION", "1.0"))
    # su quante crypto (tra le più liquide scansionate) cercare un SEGNALE a ogni
    # ciclo. Disaccoppiato dal cap posizioni: valuti TUTTO il mercato liquido, apri max 5.
    SELECT_UNIVERSE: int = int(os.getenv("SELECT_UNIVERSE", "100"))
    # SANITY FLOOR di liquidità: la liquidità VERA è gestita dal modello di costo
    # (bot/core/costs.py, spread più largo sulle coin sottili), che valida ogni coppia
    # coi suoi costi reali -> l'intero universo validato è tradabile. Questa soglia
    # esclude solo le coin MORTE/delistate (fill impossibile). Default 1M (basso).
    # Alzabile via env per i soldi veri se si vuole prudenza extra. 0 = disattivato.
    SCAN_MIN_VOLUME_24H: float = float(os.getenv("SCAN_MIN_VOLUME_24H", "1000000"))
    # FAIL-SAFE di validazione: quando esiste un registro validato, opera SOLO le
    # coppie (coin, strategia) che hanno passato il gate. Se True (default) e il
    # registro non è caricato (errore transitorio / reset), il bot resta FLAT
    # invece di tradare tutto senza validazione. Mettere False solo in bootstrap.
    REQUIRE_VALIDATED_PAIRS: bool = os.getenv("REQUIRE_VALIDATED_PAIRS", "true").lower() == "true"
    # se True, PRIMA che il GATE 1 abbia coppie validate (>= MIN_PASSES passaggi) il
    # bot opera in bootstrap le coppie a 1 passaggio (per accumulare dati paper).
    # DEFAULT False: non si trada su strategie non validate; il bot resta flat finche'
    # il gate non e' popolato.
    BOOTSTRAP_TRADE_UNVALIDATED: bool = os.getenv("BOOTSTRAP_TRADE_UNVALIDATED", "false").lower() == "true"
    # il bot NON va in paper finche' il GATE 1 non e' "ready" (copertura >= soglia
    # OPTIMIZER_READY_FRACTION, default 60%): resta FLAT anche se qualche singola
    # coppia e' gia' validata. E' cio' che promette il messaggio Telegram ("GATE 1
    # SUPERATO -> si puo' passare al paper"). False = trada le validate appena
    # esistono, senza aspettare la copertura dell'universo.
    REQUIRE_GATE1_READY: bool = os.getenv("REQUIRE_GATE1_READY", "true").lower() == "true"
    # cooldown anti-whipsaw: stop su una coin dopo uno STOP LOSS (no rientro).
    # Espresso in BARRE del timeframe (4 barre: 1h a 15m, 4h a 1h) cosi' il
    # comportamento non cambia di scala quando si cambia ORCHESTRATOR_TIMEFRAME.
    # L'env COOLDOWN_HOURS (in ore) vince se impostato.
    COOLDOWN_HOURS: float = float(os.getenv(
        "COOLDOWN_HOURS", str(4 * timeframe_hours(ORCHESTRATOR_TIMEFRAME))))
    # adattamento real-time: dopo N stop consecutivi una STRATEGIA va in panchina
    # (il bot continua con le altre), per STRATEGY_COOLDOWN_HOURS (8 barre).
    STRATEGY_LOSS_STREAK: int = int(os.getenv("STRATEGY_LOSS_STREAK", "3"))
    STRATEGY_COOLDOWN_HOURS: float = float(os.getenv(
        "STRATEGY_COOLDOWN_HOURS", str(8 * timeframe_hours(ORCHESTRATOR_TIMEFRAME))))
    # rientro in prova (probation): un gruppo strategia×regime SENZA trade recenti
    # recupera il peso verso 1.0 in questo numero di giorni (invece di risorgere
    # DI COLPO a 1.0 quando i vecchi trade escono dalla finestra dei 30g).
    WEIGHT_RECOVERY_DAYS: float = float(os.getenv("WEIGHT_RECOVERY_DAYS", "30"))
    MAX_CORRELATED_POSITIONS: int = 3     # correlazione >0.85
    CORRELATION_THRESHOLD: float = 0.85

    # ---- Anti-overfitting ----
    # Frazione di capitale SEMPRE su configurazione baseline non adattata.
    BASELINE_CAPITAL_FRACTION: float = 0.20

    # ---- Learning ----
    LEARNING_LOOKBACK_DAYS: tuple[int, ...] = (30, 60, 90)
    MIN_TRADES_FOR_KELLY: int = 100       # Kelly suggerito dopo 100+ trade
    MIN_TRADES_PER_WEIGHT: int = 5        # minimo campione per fidarsi di un peso

    # ---- Timeframes raccolti dal price agent ----
    TIMEFRAMES: tuple[str, ...] = ("1m", "5m", "15m", "1h")

    # ---- Protezione profitto (profit-lock) ----
    # Quando una posizione va in profitto ma non tocca il TP, blocca una parte del
    # guadagno invece di restituirlo. STESSI parametri nel backtest (GATE 1) e nel
    # live, così il paper resta coerente con ciò che è stato validato.
    #   - ENABLED: attiva/disattiva il meccanismo
    #   - TRIGGER: frazione della distanza entry->TP raggiunta la quale si "arma"
    #     (0.5 = a metà strada verso il take profit)
    #   - KEEP: frazione del MIGLIOR profitto visto che viene bloccata come stop
    #     (0.5 = se il picco era +2%, lo stop sale a +1%)
    PROFIT_LOCK_ENABLED: bool = os.getenv("PROFIT_LOCK_ENABLED", "true").lower() == "true"
    PROFIT_LOCK_TRIGGER: float = float(os.getenv("PROFIT_LOCK_TRIGGER", "0.5"))
    PROFIT_LOCK_KEEP: float = float(os.getenv("PROFIT_LOCK_KEEP", "0.5"))

    # ---- SCALE-OUT su multipli di R (TP scaglionati) ----
    # Chiude la posizione a fette a livelli di profitto multipli di R (R = distanza
    # entry->stop base). Es. default: 50% a 1R, 30% a 2R, 20% a 3R (finale).
    # Appena scatta il PRIMO TP, lo stop del residuo va a BREAK-EVEN (entry): da lì
    # il trade è netto positivo anche se inverte, e il residuo corre fino al TP
    # finale protetto dal profit-lock. DISATTIVO di default: va prima ri-validato
    # nel GATE 1 (parità engine<->paper) e confrontato col modello attuale.
    SCALE_OUT_ENABLED: bool = os.getenv("SCALE_OUT_ENABLED", "false").lower() == "true"
    SCALE_OUT_R_MULTIPLES: list[float] = tuple(
        float(x) for x in os.getenv("SCALE_OUT_R_MULTIPLES", "1,2,3").split(",") if x.strip()
    )
    SCALE_OUT_FRACTIONS: list[float] = tuple(
        float(x) for x in os.getenv("SCALE_OUT_FRACTIONS", "0.5,0.3,0.2").split(",") if x.strip()
    )
    SCALE_OUT_SL_TO_BREAKEVEN: bool = os.getenv("SCALE_OUT_SL_TO_BREAKEVEN", "true").lower() == "true"

    # ---- GATE 1 (soglie di validazione) ----
    # Una coppia (coin, strategia) è validata SOLO se, fuori campione (OOS):
    #   - ha almeno GATE_MIN_TRADES trade
    #   - profit factor >= GATE_PF_THRESHOLD
    #   - win-rate >= GATE_WIN_RATE_FLOOR
    #   - ritorno OOS totale >= GATE_MIN_TOTAL_RETURN ("profittevole, e di tanto")
    #   - è profittevole in OGNI finestra OOS (no "in perdita un anno, recupero il
    #     dopo"): almeno GATE_CONSISTENCY_FRACTION delle finestre dev'essere > 0
    GATE_PF_THRESHOLD: float = float(os.getenv("GATE_PF_THRESHOLD", "1.25"))
    GATE_MIN_TRADES: int = int(os.getenv("GATE_MIN_TRADES", "20"))
    GATE_WIN_RATE_FLOOR: float = float(os.getenv("GATE_WIN_RATE_FLOOR", "0.45"))
    GATE_MIN_TOTAL_RETURN: float = float(os.getenv("GATE_MIN_TOTAL_RETURN", "0.15"))
    GATE_CONSISTENCY_FRACTION: float = float(os.getenv("GATE_CONSISTENCY_FRACTION", "1.0"))

    # ---- Selezione per il PAPER/LIVE: robustezza minima ----
    # Una coppia (coin, strategia) e' tradabile SOLO se la sua STRATEGIA e' validata
    # su >= MIN_COINS_PER_STRATEGY coin distinte (filtra i flukes a coin singola, che
    # sono i piu' a rischio overfit). 3 = "solida+robusta" nel dashboard. 1 = nessun
    # filtro (trada tutte le validate).
    MIN_COINS_PER_STRATEGY: int = int(os.getenv("MIN_COINS_PER_STRATEGY", "3"))

    # ---- Parità col backtest (fase di validazione paper) ----
    # Quando True, il bot DISATTIVA i controlli che il backtest non modella (cooldown
    # post-stop, panchina strategia, circuit breaker giornaliero) così il paper
    # riproduce le stesse condizioni del GATE 1 e il confronto e' valido. Per il
    # trading con soldi VERI va rimesso a False (controlli di sicurezza riattivi).
    BACKTEST_PARITY: bool = os.getenv("BACKTEST_PARITY", "false").lower() == "true"

    # ---- Trend come contesto di decisione (SOLO live/paper, non nel backtest) ----
    # Il trend (coin + mercato) e' un fattore IN PIU' che modula la SIZE, NON un veto:
    # un segnale CONTROtrend apre lo stesso ma piu' piccolo; in-trend resta pieno.
    # (size_multiplier e' clampato <=1, quindi il tilt puo' solo ridurre.)
    TREND_TILT_ENABLED: bool = os.getenv("TREND_TILT_ENABLED", "true").lower() == "true"
    TREND_TILT_STRENGTH: float = float(os.getenv("TREND_TILT_STRENGTH", "0.5"))


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
