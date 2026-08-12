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

# I TEST NON DEVONO VEDERE LA CONFIGURAZIONE DI PRODUZIONE.
# load_dotenv() legge il .env della directory corrente: lanciando pytest dalla
# cartella dell'app sulla VPS, l'intera configurazione live (SCALE_OUT_ENABLED,
# leva, cap di size, BACKTEST_PARITY...) finiva dentro i test, che assumono i
# default -> 14 fallimenti fantasma su una macchina e zero sull'altra. Peggio:
# entrava anche FIREBASE_SERVICE_ACCOUNT, quindi la suite si collegava al
# Firebase VERO e poteva scrivergli sopra (un test ha trovato una posizione di
# produzione aperta). conftest.py imposta questa variabile prima di ogni import.
if not os.getenv("TRADING_BOT_TEST_MODE"):
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

    # ---- Livello AI (bot/ai) ----
    # Interruttore unico. A OFF (o senza chiave) il sistema si comporta ESATTAMENTE
    # come prima: il modello non e' mai sul percorso di esecuzione, quindi
    # spegnerlo non toglie nessuna funzione operativa, toglie solo ipotesi.
    AI_ENABLED: bool = os.getenv("AI_ENABLED", "true").lower() == "true"
    AI_TIMEOUT_SECONDS: float = float(os.getenv("AI_TIMEOUT_SECONDS", "120"))
    # quante spec il modello propone per passata di discovery. Poche e motivate
    # battono molte e casuali: ogni candidata in piu' e' un'ipotesi in piu' nel
    # conto del confronto multiplo, cioe' una probabilita' in piu' di promuovere
    # un fortunato. Il resto delle spec resta casuale (esplorazione).
    AI_HYPOTHESES_PER_RUN: int = int(os.getenv("AI_HYPOTHESES_PER_RUN", "20"))
    # filtro di contesto sull'universo: scarta le coin su cui non vale la pena
    # spendere validazione. FAIL-OPEN: senza AI non scarta nulla.
    AI_UNIVERSE_FILTER: bool = os.getenv("AI_UNIVERSE_FILTER", "true").lower() == "true"
    # MODALITA' OMBRA: a ogni decisione il modello dice cosa farebbe, e la sua
    # scelta viene REGISTRATA accanto a quella vera. Non tocca nulla: serve a
    # rispondere con dei numeri alla domanda "aggiungerebbe valore?", prima di
    # dargli un ruolo. Una decisione LLM non e' riproducibile, quindi non e'
    # backtestabile: l'ombra e' l'unico modo di misurarla senza rischiare.
    AI_SHADOW_ENABLED: bool = os.getenv("AI_SHADOW_ENABLED", "true").lower() == "true"
    # PASSO 2 — VETO. Il modello puo' solo dire "questo no", mai "prendi
    # quest'altro". E' l'unico ruolo operativo accettabile prima di una prova,
    # perche' e' falsificabile (si guarda a posteriori se i vietati avrebbero
    # perso) e perche' un veto sbagliato costa un'occasione, non una perdita.
    # DEFAULT False: si arma solo dopo che `scripts.shadow_report` mostra che i
    # veti dell'ombra erano giusti. Il meccanismo c'e', la decisione e' dell'utente.
    AI_VETO_ENABLED: bool = os.getenv("AI_VETO_ENABLED", "false").lower() == "true"

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
    # ogni quanto il bot RICARICA il registro validato (coppie GATE 1 + specs
    # generate + params + flag ready). Default 1h: aggancia in fretta le nuove
    # coppie validate quando la copertura cresce (prima era 6h).
    ADAPT_RELOAD_SECONDS: int = int(os.getenv("ADAPT_RELOAD_SECONDS", "3600"))
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
    # Il correlation guard ESISTEVA ma non era collegato a nulla (audit 04/08): il
    # bot poteva aprire 5 posizioni perfettamente correlate credendo di essere
    # diversificato — una sola scommessa con size 5x. Ora e' nel percorso di
    # apertura. FAIL-OPEN: se lo storico prezzi non e' disponibile non blocca.
    CORRELATION_GUARD_ENABLED: bool = os.getenv("CORRELATION_GUARD_ENABLED", "true").lower() == "true"
    # candele 1h usate per la correlazione (24 = un giorno)
    CORRELATION_LOOKBACK_BARS: int = int(os.getenv("CORRELATION_LOOKBACK_BARS", "24"))
    # ESPOSIZIONE DIREZIONALE: rischio massimo (frazione di equity) impegnato in
    # posizioni della STESSA direzione. Il cap sul numero di posizioni non basta:
    # 5 long correlati rischiano quanto un solo trade con size 5x. Qui si somma il
    # rischio VERO di ciascuna (distanza dallo stop x quantita' residua).
    # 0 = disattivato. Default 3% con rischio/trade all'1%: ~3 posizioni piene
    # nello stesso verso, coerente col breaker giornaliero al 5%.
    MAX_DIRECTIONAL_RISK_PCT: float = float(os.getenv("MAX_DIRECTIONAL_RISK_PCT", "0.03"))

    # ---- INGRESSO LIVE: conferma del fill (solo DRY_RUN=False) ----
    # Il bot piazzava un LIMIT e ASSUMEVA il fill: se il prezzo scappava, gestiva
    # una posizione che non esisteva (stop e TP su quantita' mai comprata). Ora si
    # attende la conferma e si riconcilia con quantita' e prezzo REALI.
    # Secondi di attesa del riempimento prima di rinunciare.
    EXEC_FILL_TIMEOUT_S: float = float(os.getenv("EXEC_FILL_TIMEOUT_S", "20"))
    EXEC_FILL_POLL_S: float = float(os.getenv("EXEC_FILL_POLL_S", "1.0"))
    # frazione minima riempita perche' la posizione valga: sotto, si cancella il
    # resto e si rinuncia (una posizione simbolica costa in fee quanto rende)
    EXEC_MIN_FILL_FRACTION: float = float(os.getenv("EXEC_MIN_FILL_FRACTION", "0.5"))

    # ---- Anti-overfitting ----
    # Frazione di capitale SEMPRE su configurazione baseline non adattata.
    BASELINE_CAPITAL_FRACTION: float = 0.20

    # ---- Learning ----
    LEARNING_LOOKBACK_DAYS: tuple[int, ...] = (30, 60, 90)
    MIN_TRADES_FOR_KELLY: int = 100       # Kelly suggerito dopo 100+ trade
    MIN_TRADES_PER_WEIGHT: int = 5        # minimo campione per fidarsi di un peso
    # ---- Learning robusto (anti-overfitting) ----
    # Sotto questo numero di trade VALIDI (dopo il filtro anomalie) non si aggiorna
    # nessun peso: ricalcolare su una manciata di esiti insegue il rumore, e i pesi
    # guidano size e leva di ogni trade successivo.
    LEARNING_MIN_TRADES_TOTAL: int = int(os.getenv("LEARNING_MIN_TRADES_TOTAL", "50"))
    # smoothing esponenziale verso il peso precedente: stabilizza nel TEMPO (lo
    # shrinkage bayesiano stabilizza rispetto alla numerosita' del campione, che e'
    # un'altra cosa). 1.0 = nessuno smoothing.
    LEARNING_SMOOTHING_ALPHA: float = float(os.getenv("LEARNING_SMOOTHING_ALPHA", "0.3"))
    # variazione aggregata oltre la quale l'aggiornamento viene SOSPESO: un salto
    # cosi' grande e' quasi sempre un difetto (dati sporchi, campo mancante) e non
    # apprendimento. 0 disattiva il controllo.
    LEARNING_MAX_TOTAL_CHANGE: float = float(os.getenv("LEARNING_MAX_TOTAL_CHANGE", "0.40"))
    # trade piu' brevi di cosi' sono artefatti (fill anomalo, dato sporco)
    LEARNING_MIN_TRADE_SECONDS: float = float(os.getenv("LEARNING_MIN_TRADE_SECONDS", "60"))
    # slippage oltre N volte la mediana: misura la liquidita' di quel momento, non
    # la bonta' del segnale
    LEARNING_SLIPPAGE_OUTLIER_MULT: float = float(
        os.getenv("LEARNING_SLIPPAGE_OUTLIER_MULT", "3.0"))
    # quante versioni dei pesi tenere nello storico ad anello (per il rollback)
    LEARNING_HISTORY_VERSIONS: int = int(os.getenv("LEARNING_HISTORY_VERSIONS", "90"))

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
    # entry->stop base). Default VINCENTE dall'A/B (scripts/ab_scale_out.py, 2 seed,
    # fino a 377 coppie): 30% a 1.5R, 30% a 3R, 40% a 5R (finale). Meno aggressivo
    # del 50/30/20 a 1/2/3 (che cappava i vincitori): lasciare correre il 40% fino a
    # 5R alza PF, ritorno OOS e n. coppie profittevoli (win-rate piu' basso ma
    # expectancy migliore). Appena scatta il PRIMO TP lo stop del residuo va a
    # BREAK-EVEN (entry). DISATTIVO di default: si attiva SOLO dopo la ri-validazione
    # completa del GATE 1 sotto questo modello (parita' engine<->paper).
    SCALE_OUT_ENABLED: bool = os.getenv("SCALE_OUT_ENABLED", "false").lower() == "true"
    SCALE_OUT_R_MULTIPLES: list[float] = tuple(
        float(x) for x in os.getenv("SCALE_OUT_R_MULTIPLES", "1.5,3,5").split(",") if x.strip()
    )
    SCALE_OUT_FRACTIONS: list[float] = tuple(
        float(x) for x in os.getenv("SCALE_OUT_FRACTIONS", "0.3,0.3,0.4").split(",") if x.strip()
    )
    SCALE_OUT_SL_TO_BREAKEVEN: bool = os.getenv("SCALE_OUT_SL_TO_BREAKEVEN", "true").lower() == "true"

    # ---- PARITA' SUI WICK (ombre delle candele) ----
    # Il GATE valida sulle candele: un TP/SL si riempie se l'OMBRA (high/low) tocca
    # il livello, anche per un istante. Il bot live invece campiona il prezzo ogni
    # ~30s: i movimenti tra due letture sono INVISIBILI -> perde fill di TP che il
    # gate contava (e schiva stop che il gate prendeva). Su Binance REALE gli ordini
    # TP/SL stanno appoggiati sul book: un'ombra li ESEGUE. Quindi il modello giusto
    # e' quello del gate, e il paper deve allinearsi: a ogni tick si leggono high/low
    # delle ultime candele 1m e i trigger si valutano su quel range.
    # NB: la parita' vale in ENTRAMBE le direzioni (piu' TP riempiti, ma anche piu'
    # stop presi sulle ombre): serve realismo, non numeri piu' belli.
    EXEC_WICK_FILLS_ENABLED: bool = os.getenv("EXEC_WICK_FILLS_ENABLED", "true").lower() == "true"
    # quante candele 1m rileggere a ogni tick (copre il gap tra due letture, con
    # margine se un ciclo e' lento). La sovrapposizione e' innocua: i fill avanzano
    # per stage e lo stop chiude una volta sola.
    EXEC_WICK_LOOKBACK_1M: int = int(os.getenv("EXEC_WICK_LOOKBACK_1M", "3"))
    # Stream WebSocket dei trade: elimina l'ultima ambiguita' delle candele, cioe'
    # l'ORDINE dei prezzi dentro il minuto (se il range tocca sia un TP sia lo stop,
    # una candela non dice quale sia venuto prima). Alimenta lo stesso range hi/lo,
    # ma minuto per minuto in tempo reale. Se lo stream non e' sano si ricade
    # automaticamente sulle candele REST: nessun percorso critico ne dipende.
    EXEC_PRICE_STREAM_ENABLED: bool = os.getenv("EXEC_PRICE_STREAM_ENABLED", "true").lower() == "true"
    # REPLAY del percorso: i prezzi dello stream vengono rigiocati UNO PER UNO nella
    # logica di uscita, nell'ordine in cui sono arrivati — come la matching engine di
    # Binance. Conoscendo l'ordine non serve piu' assumere il peggio quando un range
    # tocca due livelli. Il percorso e' compresso a zigzag: sotto questa soglia
    # un'inversione e' rumore (rimbalzo bid/ask) e non genera un punto.
    EXEC_PATH_REPLAY_ENABLED: bool = os.getenv("EXEC_PATH_REPLAY_ENABLED", "true").lower() == "true"
    # Soglia sotto la quale un'INVERSIONE non entra nel percorso. Default 0 = nessun
    # filtro (si comprimono solo i movimenti monotoni e i prezzi identici).
    # MISURATO: il replay costa ~1.8us per punto -> 1810 punti (un tick da 30s su BTC)
    # sono 3ms, e con 12 posizioni ~40ms su un tick di 30s (0.13%). Filtrare non fa
    # risparmiare nulla di percepibile e COSTA fedelta': con una soglia di 0.02%
    # ($12.80 su BTC) un tuffo di pochi dollari sotto uno stop a break-even veniva
    # cancellato dal percorso, il replay proseguiva e incassava un TP che non doveva
    # raggiungere -> errore in direzione OTTIMISTA, la piu' pericolosa.
    EXEC_PATH_MIN_MOVE_FRAC: float = float(os.getenv("EXEC_PATH_MIN_MOVE_FRAC", "0"))
    # tetto di punti: ~20k = oltre 5 minuti di bookTicker su BTC, quindi si tocca solo
    # se un ciclo si blocca a lungo. Oltre, la coda resta coperta dal range aggregato.
    EXEC_PATH_MAX_POINTS: int = int(os.getenv("EXEC_PATH_MAX_POINTS", "20000"))
    # TIPO di stream da cui leggere il prezzo. Default `bookTicker` (miglior bid/ask):
    # su alcuni IP/provider Binance consegna il BOOK ma NON gli stream di trade
    # (`aggTrade`/`kline_*` restano muti pur con la sottoscrizione accettata), e per
    # simulare un fill il book e' comunque piu' pertinente: un ordine si esegue quando
    # il book raggiunge il prezzo, non quando avviene un trade altrove.
    # Si usa il MID (bid+ask)/2: il costo dello spread e' gia' modellato a parte in
    # bot/core/costs.py, usare il lato del book lo conteggerebbe DUE volte.
    EXEC_STREAM_TYPE: str = os.getenv("EXEC_STREAM_TYPE", "bookTicker")

    # ---- GATE 1 (soglie di validazione) ----
    # Una coppia (coin, strategia) è validata SOLO se, fuori campione (OOS):
    #   - ha almeno GATE_MIN_TRADES trade
    #   - profit factor >= GATE_PF_THRESHOLD
    #   - win-rate >= GATE_WIN_RATE_FLOOR
    #   - ritorno OOS totale >= GATE_MIN_TOTAL_RETURN ("profittevole, e di tanto")
    #   - è profittevole in OGNI finestra OOS (no "in perdita un anno, recupero il
    #     dopo"): almeno GATE_CONSISTENCY_FRACTION delle finestre dev'essere > 0
    GATE_PF_THRESHOLD: float = float(os.getenv("GATE_PF_THRESHOLD", "1.25"))
    # 30 (era 20): con 20 trade la varianza del PF e' enorme e, moltiplicata per
    # migliaia di candidate testate, produce troppi falsi positivi (lotteria).
    GATE_MIN_TRADES: int = int(os.getenv("GATE_MIN_TRADES", "30"))

    # ---- HOLDOUT finale (anti data-snooping) ----
    # Gli ultimi N giorni di storia sono ESCLUSI da train e finestre OOS: la
    # selezione (grid search, scelta spec, pass_count) non li vede MAI. Una coppia
    # passa solo se, DOPO aver passato le finestre, regge anche sull'holdout coi
    # parametri che verrebbero spediti in produzione. Senza questo, migliaia di
    # candidate valutate sempre sulle stesse finestre trasformano l'OOS in un
    # training set (selection bias): e' il difetto che gonfiava il registro.
    # L'holdout e' ROLLING (scorre col tempo), quindi non diventa un bersaglio fisso.
    GATE_HOLDOUT_DAYS: float = float(os.getenv("GATE_HOLDOUT_DAYS", "45"))
    # requisiti sull'holdout: piu' morbidi del gate pieno (45 giorni producono pochi
    # trade), ma DEVE essere profittevole. PF>=1.05 e ritorno>0 con almeno 5 trade.
    GATE_HOLDOUT_PF: float = float(os.getenv("GATE_HOLDOUT_PF", "1.05"))
    GATE_HOLDOUT_MIN_TRADES: int = int(os.getenv("GATE_HOLDOUT_MIN_TRADES", "5"))

    # ---- pass_count ONESTO ----
    # Un pass incrementa il conteggio SOLO se dall'ultimo pass sono entrati almeno
    # queste ore di dati NUOVI. Rivalutare due volte nello stesso giorno gli stessi
    # dati non e' una conferma indipendente: senza questa regola MIN_PASSES=3
    # significava solo "valutata 3 volte", non "confermata 3 volte".
    OPTIMIZER_NEW_DATA_MIN_HOURS: float = float(os.getenv("OPTIMIZER_NEW_DATA_MIN_HOURS", "24"))

    # ---- filtro di regime informato dal gate ----
    # Il gate CONOSCE il PF per-regime di ogni coppia (dai suoi trade OOS) ma prima
    # non lo esportava: il bot tradava in sideways coppie che il gate stesso sapeva
    # perdere in sideways, e il learning doveva riscoprirlo da zero sul paper.
    # Con questo flag una coppia NON opera nel regime corrente se il suo PF in quel
    # regime e' < 1.0 (con almeno GATE_REGIME_MIN_TRADES trade). Fail-open: senza
    # dati per-regime (coppie non ancora ri-validate) non blocca nulla.
    REGIME_FILTER_ENABLED: bool = os.getenv("REGIME_FILTER_ENABLED", "true").lower() == "true"
    GATE_REGIME_MIN_TRADES: int = int(os.getenv("GATE_REGIME_MIN_TRADES", "10"))
    # Una coppia poteva validarsi vivendo di UN SOLO regime: profitto enorme in
    # trend, perdite in laterale, totale positivo -> passava. Poi il paper la
    # trovava in laterale e perdeva. Qui si esige che NESSUN regime con campione
    # sufficiente sia in perdita marcata (il veto live resta la seconda rete).
    # 0 = disattivato.
    GATE_REGIME_MIN_PF: float = float(os.getenv("GATE_REGIME_MIN_PF", "0.8"))

    # ---- RILEVATORE DI DERIVA (anello paper -> gate) ----
    # Il gate promette (PF validato, TP raggiungibili); il paper misura il vissuto.
    # Quando il vissuto contraddice la promessa: si frena SUBITO in produzione e
    # l'evidenza va al gate, che rivalidera' su storia ORA comprensiva del periodo
    # appena vissuto. Il paper FALSIFICA, non ottimizza: tararci i parametri lo
    # consumerebbe come training set (lo stesso difetto rimosso dal gate).
    DRIFT_ENABLED: bool = os.getenv("DRIFT_ENABLED", "true").lower() == "true"
    # campioni minimi per DICHIARARE deriva (sotto -> "watch": si vede, non si agisce).
    # Per-coppia i trade arrivano lentissimi, per strategia e globale molto prima.
    DRIFT_MIN_TRADES_PAIR: int = int(os.getenv("DRIFT_MIN_TRADES_PAIR", "8"))
    DRIFT_MIN_TRADES_STRATEGY: int = int(os.getenv("DRIFT_MIN_TRADES_STRATEGY", "20"))
    DRIFT_MIN_TRADES_GLOBAL: int = int(os.getenv("DRIFT_MIN_TRADES_GLOBAL", "40"))
    # il PF vissuto deve restare almeno a questa frazione di quello validato
    DRIFT_PF_RATIO: float = float(os.getenv("DRIFT_PF_RATIO", "0.6"))
    # la mfe mediana deve arrivare almeno a questa frazione del PRIMO gradino:
    # sotto, la scala di TP e' irraggiungibile per come si muove davvero il prezzo
    DRIFT_MFE_RATIO: float = float(os.getenv("DRIFT_MFE_RATIO", "0.7"))
    # freno applicato a size/leva su una coppia (o strategia) in deriva. Frena, non
    # spegne: rimuovere spetta al gate, che decide sulla storia, non su 8 trade.
    DRIFT_WEIGHT_FACTOR: float = float(os.getenv("DRIFT_WEIGHT_FACTOR", "0.5"))
    DRIFT_WEIGHT_FLOOR: float = float(os.getenv("DRIFT_WEIGHT_FLOOR", "0.25"))

    # ---- CALIBRAZIONE DELLA CONFIDENZA ----
    # allocation() modula size e leva sulla confidenza del segnale, ma nessuno
    # aveva mai verificato che quel numero predicesse l'esito: se fosse rumore,
    # staremmo dimensionando le posizioni su una cifra senza significato — e con
    # convinzione, che e' la parte peggiore. Misurata la relazione, l'influenza
    # della confidenza viene RIDOTTA verso il neutro quando non predice. Non
    # invertita: scommettere contro un segnale che anti-predice su pochi trade
    # e' adattarsi al rumore con un altro nome.
    CALIBRATION_ENABLED: bool = os.getenv("CALIBRATION_ENABLED", "true").lower() == "true"
    CALIBRATION_MIN_TRADES: int = int(os.getenv("CALIBRATION_MIN_TRADES", "30"))
    CALIBRATION_FLAT_ABS: float = float(os.getenv("CALIBRATION_FLAT_ABS", "0.05"))
    CALIBRATION_FLAT_TRUST: float = float(os.getenv("CALIBRATION_FLAT_TRUST", "0.5"))
    GATE_WIN_RATE_FLOOR: float = float(os.getenv("GATE_WIN_RATE_FLOOR", "0.45"))
    GATE_MIN_TOTAL_RETURN: float = float(os.getenv("GATE_MIN_TOTAL_RETURN", "0.15"))
    GATE_CONSISTENCY_FRACTION: float = float(os.getenv("GATE_CONSISTENCY_FRACTION", "1.0"))
    # CONTINUITA' del profitto: ritorno OOS / max drawdown della curva dei trade
    # (recovery factor) >= questa soglia. Rende operativo l'obiettivo "profitto
    # continuo": il PF dice QUANTO si vince, il recovery dice quanto in PROFONDITA'
    # si scava per vincerlo. Il win-rate resta una proprieta' di STILE, non un
    # criterio di validita': un 35% di WR con curva regolare e' benvenuto.
    GATE_MIN_RECOVERY: float = float(os.getenv("GATE_MIN_RECOVERY", "2.0"))
    # ROBUSTEZZA: frazione dei trade MIGLIORI da togliere prima di ricalcolare il PF,
    # e soglia che quel PF ridotto deve comunque superare. Sotto scale-out il
    # risultato lo fanno poche corse lunghe: su BIRBUSDT|gen_472f85b8 l'holdout di 94
    # trade era positivo solo grazie ai 7 migliori, e senza quelli gli altri 87
    # perdevano. Il tasso di coda e' anche la statistica piu' instabile, quindi
    # scegliere il meglio fra 1464 candidate su una metrica che ne dipende seleziona
    # la coda piu' fortunata invece dell'edge. Chiedere PF >= 1 SENZA i colpi migliori
    # distingue "valida" da "e' andata bene". 0 disattiva il test.
    GATE_DROP_TOP_FRAC: float = float(os.getenv("GATE_DROP_TOP_FRAC", "0.05"))
    GATE_MIN_PF_EX_TOP: float = float(os.getenv("GATE_MIN_PF_EX_TOP", "1.0"))
    # RECENCY: emivita (giorni) del peso dei trade nella SCELTA DEI PARAMETRI.
    # Le finestre pesavano tutte uguale: un trade di gennaio 2022 contava quanto uno
    # di oggi, quindi 7 giorni nuovi su 4.6 anni valevano lo 0.42% dell'evidenza e
    # l'ottimo non si spostava MAI — ecco perche' la strategia non "migliorava".
    # Col decadimento i parametri si ritarano sul carattere ATTUALE del mercato.
    # 0 = disattivato (peso uniforme, comportamento storico).
    # NB: pesa SOLO la selezione dei parametri; i criteri di validazione restano
    # non pesati, cosi' il rigore del gate non si ammorbidisce di un grammo.
    GATE_RECENCY_HALFLIFE_DAYS: float = float(os.getenv("GATE_RECENCY_HALFLIFE_DAYS", "180"))

    # ---- Selezione per il PAPER/LIVE: robustezza minima ----
    # Una coppia (coin, strategia) e' tradabile SOLO se la sua STRATEGIA e' validata
    # su >= MIN_COINS_PER_STRATEGY coin distinte (filtra i flukes a coin singola, che
    # sono i piu' a rischio overfit). 3 = "solida+robusta" nel dashboard. 1 = nessun
    # filtro (trada tutte le validate).
    MIN_COINS_PER_STRATEGY: int = int(os.getenv("MIN_COINS_PER_STRATEGY", "3"))

    # ---- Reconciler (bot/execution/reconciler) ----
    # Confronto fra stato interno ed exchange. INERTE in DRY_RUN: senza exchange
    # non c'e' nulla da riconciliare e girerebbe solo per produrre falsi allarmi.
    RECONCILE_ENABLED: bool = os.getenv("RECONCILE_ENABLED", "true").lower() == "true"
    RECONCILE_INTERVAL_SECONDS: float = float(os.getenv("RECONCILE_INTERVAL_SECONDS", "60"))
    # differenze di quantita' sotto questa soglia sono arrotondamenti, non divergenze
    RECONCILE_QTY_TOLERANCE: float = float(os.getenv("RECONCILE_QTY_TOLERANCE", "1e-8"))
    # scarto relativo di saldo oltre il quale si ferma tutto: sotto ci stanno fee
    # non ancora contabilizzate e funding in corso, sopra e' successo altro
    RECONCILE_BALANCE_TOLERANCE: float = float(
        os.getenv("RECONCILE_BALANCE_TOLERANCE", "0.02"))
    # un problema che dura ore non deve produrre un alert al minuto: si smetterebbe
    # di leggerli, che e' il modo piu' comune di rendere inutile un allarme
    RECONCILE_ALERT_COOLDOWN_S: float = float(
        os.getenv("RECONCILE_ALERT_COOLDOWN_S", "300"))

    # ---- Monitoraggio costi (Fase 2.5) ----
    # oltre questa percentuale di equity spesa in costi, il sistema deve rendere
    # tanto SOLO per pareggiare: e' un allarme sul numero di trade o sulle coin
    # scelte, non sulla strategia.
    COST_ALERT_BREAKEVEN_PCT: float = float(os.getenv("COST_ALERT_BREAKEVEN_PCT", "1.5"))

    # ---- Kill switch a livelli (bot/risk/kill_switch) ----
    # STOP AND PROTECT: quanto stretto portare lo stop, in ATR. 0.3 = le posizioni
    # escono al primo movimento avverso serio, ma quelle che corrono continuano.
    KILL_PROTECT_ATR_MULT: float = float(os.getenv("KILL_PROTECT_ATR_MULT", "0.3"))

    # ---- Asset scoring (bot/agents/market_scanner) ----
    # Volatilita' "utile" (ATR/prezzo) per il punteggio: sotto, il movimento non
    # paga i costi; sopra, gli stop saltano per rumore.
    ASSET_IDEAL_ATR_PCT: float = float(os.getenv("ASSET_IDEAL_ATR_PCT", "0.015"))
    # ESCLUSIONI STRUTTURALI. Attive solo fuori da BACKTEST_PARITY: il gate non le
    # modella, e filtrare in live cio' che il gate ha validato crea proprio la
    # divergenza fra promesso ed eseguito che stiamo combattendo.
    # Volume minimo DISATTIVATO di default: questo sistema ha sostituito il filtro
    # netto sul volume col modello di costo (spread piu' largo sulle sottili, e il
    # gate boccia chi non lo batte). Un pavimento a 100M taglierebbe quasi tutto
    # l'universo validato.
    ASSET_MIN_VOLUME_24H: float = float(os.getenv("ASSET_MIN_VOLUME_24H", "0"))
    ASSET_MAX_SPREAD: float = float(os.getenv("ASSET_MAX_SPREAD", "0.001"))
    # funding fuori da questa fascia = costo di mantenimento insostenibile
    ASSET_FUNDING_MIN: float = float(os.getenv("ASSET_FUNDING_MIN", "-0.0010"))
    ASSET_FUNDING_MAX: float = float(os.getenv("ASSET_FUNDING_MAX", "0.0015"))
    # stop consecutivi su una coin oltre i quali va in quarantena
    ASSET_BLACKLIST_STOPS: int = int(os.getenv("ASSET_BLACKLIST_STOPS", "3"))
    ASSET_BLACKLIST_LOOKBACK_DAYS: float = float(
        os.getenv("ASSET_BLACKLIST_LOOKBACK_DAYS", "7"))

    # ---- Parità col backtest (fase di validazione paper) ----
    # Quando True, il bot DISATTIVA i controlli che il backtest non modella (cooldown
    # post-stop, panchina strategia, circuit breaker giornaliero) così il paper
    # riproduce le stesse condizioni del GATE 1 e il confronto e' valido. Per il
    # trading con soldi VERI va rimesso a False (controlli di sicurezza riattivi).
    BACKTEST_PARITY: bool = os.getenv("BACKTEST_PARITY", "false").lower() == "true"
    # TIMING D'INGRESSO nel backtest. False (storico) = si entra alla CHIUSURA della
    # barra che genera il segnale. True = si entra all'APERTURA della barra dopo,
    # cioe' al primo prezzo davvero eseguibile: il bot conosce la chiusura solo a
    # barra chiusa, decide dopo il confine dell'orologio ed esegue al mark di quel
    # momento. E' l'unica delle sei cause di disparita' ipotizzate che sopravvive
    # alla verifica (le altre — indicatori, costi, funding, uscite — sono moduli
    # CONDIVISI, non due implementazioni). Default False finche' l'effetto non e'
    # misurato: `scripts.gate_vs_paper --entry-timing` lo quantifica per coppia.
    BACKTEST_ENTRY_NEXT_OPEN: bool = os.getenv(
        "BACKTEST_ENTRY_NEXT_OPEN", "false").lower() == "true"

    # ---- Trend come contesto di decisione (SOLO live/paper, non nel backtest) ----
    # Il trend (coin + mercato) e' un fattore IN PIU' che modula la SIZE, NON un veto:
    # un segnale CONTROtrend apre lo stesso ma piu' piccolo; in-trend resta pieno.
    # (size_multiplier e' clampato <=1, quindi il tilt puo' solo ridurre.)
    TREND_TILT_ENABLED: bool = os.getenv("TREND_TILT_ENABLED", "true").lower() == "true"
    TREND_TILT_STRENGTH: float = float(os.getenv("TREND_TILT_STRENGTH", "0.5"))

    # ---- Sentiment come contesto di decisione (SOLO live/paper, non nel backtest) ----
    # Overlay di SIZE al final gate, identico nello spirito al trend tilt: il sentiment
    # per-coin (0..1, 0.5 neutro) e' un fattore IN PIU' che puo' solo RIDURRE la size,
    # mai aumentarla. Un LONG con sentiment molto negativo (o uno SHORT con sentiment
    # molto positivo) apre piu' piccolo (fino a SENTIMENT_TILT_FLOOR); allineato/neutro
    # = size piena. Niente dato -> nessuna penalita' (fattore 1.0). Live-only: non tocca
    # il GATE 1 (il backtest non ha il sentiment storico) -> nessuna ri-validazione.
    SENTIMENT_TILT_ENABLED: bool = os.getenv("SENTIMENT_TILT_ENABLED", "true").lower() == "true"
    SENTIMENT_TILT_STRENGTH: float = float(os.getenv("SENTIMENT_TILT_STRENGTH", "0.5"))
    SENTIMENT_TILT_FLOOR: float = float(os.getenv("SENTIMENT_TILT_FLOOR", "0.5"))


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
