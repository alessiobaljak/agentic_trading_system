# NOFX (NoFxAiOS/nofx) — riassunto per il proprietario

Letto il 12 ott 2026 da un clone in sola lettura (un solo commit visibile, `ef476f28`, del 4 ott 2026).
Nessuno script è stato eseguito: solo lettura di file. Ogni affermazione ha accanto il file da cui viene.

## In due righe

È un «terminale di trading» dove la strategia è un modello di linguaggio: ogni N minuti manda al modello
conto, posizioni, candele e segnali, il modello risponde con un JSON di ordini, e il codice Go applica
alcuni limiti e manda gli ordini a un exchange vero. **Non c'è backtest, non c'è modalità carta, non c'è
una prova che renda dopo i costi.** È un prodotto da usare con soldi veri e con dati a pagamento del partner.

---

## 1. Cos'è

* **Chi lo fa.** Società Cryonic Holdings Limited (Isole Vergini Britanniche, n. 2193977), fondatore
  «Tinkle» (@Web3Tinkle); contatto legale `tinklefund@gmail.com`
  (`docs/community/OFFICIAL_ACCOUNTS.md`, `DISCLAIMER.md`). Il README apre con «Backed by vergex.trade»
  e il contratto per i contributori rimanda a `contact@vergex.trade` (`README.md`, `.github/CLA.md`).
  Vergex e Claw402.ai sono la stessa famiglia: Claw402 è il gateway a pagamento che vende sia i modelli
  sia i dati di Vergex (`provider/vergex/client.go`, `mcp/payment/claw402.go`).
* **Scopo dichiarato.** «An open-source trading terminal where the strategy is a language model»
  (`README.md`). La roadmap parla di «Universal AI Trading Operating System» (`docs/roadmap/README.md`).
* **Linguaggio e dimensione.** Backend Go: 293 file, circa 80.000 righe; frontend React/TypeScript:
  155 file, circa 42.000 righe; 80 file di test Go; `go.mod` dichiara Go 1.25 (conteggio fatto con
  `find`/`wc` sul clone). Totale 688 file, 50 MB (dato di chi ha chiesto il riassunto).
* **Ultimo commit.** 4 ott 2026, «fix: harden Hyperliquid execution and correct terminal runtime data
  (#1544)». Il numero 1544 indica molti PR. Però `CHANGELOG.md` è fermo alla versione 3.0.0 del
  30 ott 2025 («Last Updated: 2025-11-01»): la documentazione è vecchia rispetto al codice.
* **Licenza.** AGPL-3.0 (`LICENSE`). In `docs/legal/` c'è perfino un dossier contro un concorrente
  accusato di aver copiato un endpoint senza rispettare la licenza.
* **Segni di adozione.** `docs/community/OFFICIAL_ACCOUNTS.md` dice «10,500+ ⭐» (mar 2026); non
  verificabile dal clone. Canale Telegram, 7 traduzioni del README.
* **Promozione commerciale.** Nel `README.md`: nove link di affiliazione a exchange (Binance
  `ref=NOFXENG`, Bybit, OKX, Hyperliquid `join/AITRADING`, Bitget, KuCoin, Gate, Aster, Lighter),
  link Railway con `referralCode=nofx`, sponsor GitHub, «intends to reward contributors», e il gateway
  Claw402 «with official discount». La guida al primo avvio chiede di mettere **1+ USDC** nel wallet
  delle fee AI e **12+ USDC** su Hyperliquid prima di partire. **Nessun token, airdrop o programma a
  punti** trovato (grep su tutto il repo). Il modello di business è: affiliazioni + vendita di modelli e
  dati via micro-pagamenti USDC.

## 2. Architettura: cosa fa davvero

**Il ciclo** (`trader/auto_trader_loop.go`, `docs/architecture/STRATEGY_MODULE.md`): ogni N minuti
(default 15, `store/trader.go:29`; le FAQ dicono «3-5 minuti», sono vecchie) → sceglie le monete
candidate → raccoglie i dati → costruisce prompt di sistema e utente → chiama il modello → estrae
`<reasoning>` e `<decision>` con un JSON di azioni (`open_long`, `open_short`, `close_*`, `hold`,
`wait`, con leva, importo, stop, target, confidenza) → valida → applica i filtri → manda gli ordini →
salva tutto (prompt, ragionamento, risposta grezza) in SQLite/Postgres.

**Modelli.** DeepSeek, OpenAI, Claude, Qwen, Gemini, Grok, Kimi, MiniMax con chiavi proprie
(`mcp/provider/*.go`), oppure il gateway Claw402 che fa pagare ogni chiamata in USDC sulla rete Base
(default `gpt-5.6`; anche `claude-fable`, `claude-opus`, `deepseek-*`, `glm-5`; `mcp/payment/claw402.go`).
Temperatura 0.5 di default, nessun seed (`mcp/client.go:18`): **la stessa situazione può dare risposte
diverse**.

**Dati in ingresso** (`kernel/engine_prompt.go`, `kernel/engine.go`):
* conto, posizioni (con picco di profitto e durata), ultimi 10 trade chiusi, statistiche storiche
  (profit factor, Sharpe, drawdown) con un giudizio in chiaro tipo «Performance: NEEDS IMPROVEMENT»;
* candele OHLCV su più timeframe (da CoinAnk per gli exchange centralizzati, da Hyperliquid per
  Hyperliquid; `market/data.go`), indicatori EMA/MACD/RSI/ATR/Bollinger/volume, open interest, funding;
* «dati quant» da nofxos.ai: flussi istituzionali/retail, variazioni di open interest, classifiche
  (`provider/nofxos/`);
* nel modo Autopilot: «direction board», storia delle inversioni, mappa costo/liquidazioni e matrice
  del tasso di vincita dei detentori, tutti da claw402.ai a pagamento (`provider/vergex/client.go`).
* **Non ci sono**: order book, notizie, social.

**Exchange e mercati.** Binance, Bybit, OKX, Hyperliquid, Bitget, KuCoin, Gate, Aster, Lighter, Indodax
(`trader/<exchange>/`). Perpetui crypto; su Hyperliquid anche azioni USA tokenizzate, oro, indici, FX
(simboli `xyz:`).

**Orizzonte.** Intraday/swing. Il prompt dice «2-4 trade al giorno», tenuta ≥ 45-90 minuti
(`kernel/engine_prompt.go`). Il codice frena il modello: tenuta minima 90 minuti, niente chiusure
«di rumore» (tra -2% e +3% di prezzo) prima di 3 ore, 4 ore di attesa prima di rientrare sulla stessa
moneta (`trader/auto_trader_throttle.go`).

**Rischio, size, leva.** Il modello propone leva, importo, stop e target. Il codice impone: numero
massimo di posizioni (default Autopilot **8**), nozionale massimo = capitale × un fattore (altcoin 1×,
BTC/ETH 5×; in Autopilot 5× su tutto), leva tagliata tra 1 e 20 (`store/strategy.go`), minimo 12 USDT,
margine usabile fino al 100% («Claw402 Autopilot intentionally uses full margin», `store/strategy.go:1071`),
stop e target piazzati sull'exchange subito dopo l'entrata, chiusura automatica di un vincente che rende
il 40% del picco dopo un +5% di prezzo (`trader/auto_trader_risk.go`), «safe mode» senza nuove aperture
dopo 3 fallimenti consecutivi del modello (`trader/auto_trader_loop.go:188`). In Autopilot il codice
**forza la size piena**: leva 10×, nozionale massimo, «do not open small probe positions»
(`trader/auto_trader_risk.go` `applyAutopilotFullSizeOpen`, `kernel/engine_prompt.go`).

**Il punto più importante.** Nel modo predefinito (Autopilot, sorgente `vergex_signal`) il prompt dice
«Follow the current Claw402 direction exactly; candles may explain the signal but may not veto, reverse,
or prematurely exit it», e una macchina a stati nel codice scarta ogni decisione del modello contraria al
board (`kernel/engine_prompt.go` `vergexHoldRules`, `trader/auto_trader_signal_policy.go`
`enforceVergexSignalPolicy`). **Quindi la direzione non la decide il modello: la decide un segnale a
pagamento esterno al repo.** Il modello sceglie solo lo stop e un numero di «confidenza». Solo nel modo
classico (lista statica, AI500, OI top) il modello decide davvero sugli indicatori.

**Cosa c'è di «OS».** Poco. Nessun multi-agente: «Competition» significa più trader (modello × exchange)
affiancati con una classifica per rendimento realizzato, pubblicabile su richiesta
(`api/handler_competition.go`). La «memoria» è il prompt che riceve gli ultimi 10 trade e le statistiche.
`agents.md` e `docs/architecture/AGENT_MEMORY_AND_PLANNING.md` descrivono un assistente di chat
(Telegram) per creare/configurare trader, non un agente di trading. C'è anche un modo griglia separato
(`kernel/grid_engine.go`, `trader/auto_trader_grid*.go`) con riconoscimento del regime di mercato.

## 3. Prove

* **Nessun backtest storico sui prezzi.** Nessun registro di risultati nel repo. Il README rimanda a
  una «public leaderboard» su vergex.trade (sito esterno, non verificabile da qui).
* **C'è solo un «replay»** (`scripts/optimize/`, 650 righe Python): `extract.py` legge le decisioni
  del modello GIÀ REGISTRATE nel database locale (candele a 15 minuti ricavate dal testo dei prompt),
  `simulate.py` le rigioca con parametri diversi di stop, tenuta minima, cooldown, leva, e `search.py`
  cerca i parametri migliori con Optuna (800 prove, 70% addestramento / 30% riservato, punteggio =
  rendimento% − 0,5 × drawdown massimo%). Costi: 7,84 punti base per lato, «measured from trader_fills»
  (`simulate.py:25`). **I dati non ci sono** (`scripts/optimize/.gitignore` esclude `data/`).
* I commenti nel codice citano numeri: «decision replay 2026-07-26, 4154 cycles, 3-fold robustness:
  gates beat no-gates by 34 pts» (`trader/auto_trader_throttle.go:12-16`). Non sono riproducibili:
  mancano dati, periodo esatto, modello usato.
* **Limite dichiarato dagli autori stessi**: «decisions are replayed as recorded. Parameters that would
  have changed WHAT the AI decided are out of scope» (`simulate.py` docstring). Cioè il replay non può
  dire se il modello avrebbe deciso diversamente: non è un backtest della strategia.
* **Riproducibilità.** No: la decisione dipende da una risposta di modello con temperatura 0,5 senza seed
  e, in Autopilot, da un feed esterno a pagamento la cui logica non è nel repo.
* **Rischi dichiarati.** `DISCLAIMER.md`: sperimentale, «you can lose all or more than your initial
  investment»; FAQ: «not guaranteed to be profitable» (`docs/guides/faq.en.md`). Onesto su questo.
* `docs/research/AI-Trader-Analysis-Report.md` (2.500 righe, in cinese) analizza un articolo esterno
  dell'Università di Hong Kong (arXiv 2512.10971); le tabelle di rendimento hanno modelli anonimi
  («Model A/B/C/D») e la classifica è vuota. Non è una prova di NOFX.

## 4. Sicurezza

* **Chiavi degli exchange.** Cifrate nel database con AES-256-GCM tramite il tipo `crypto.EncryptedString`
  (`store/exchange.go:28-40`, `store/ai_model.go:27`, `crypto/crypto.go`); chiave presa dalla variabile
  `DATA_ENCRYPTION_KEY`, generata da `install.sh` e scritta nel `.env`. Cifratura browser→server con RSA
  opzionale (`TRANSPORT_ENCRYPTION`, spento di default). `JWT_SECRET` obbligatorio e ≥ 32 byte, il
  programma rifiuta di partire senza (`config/config.go`). Chiavi private in più da custodire: quella del
  wallet Claw402 (firma pagamenti USDC, `mcp/payment/x402.go`) e quelle di Hyperliquid/Aster/Lighter.
* **Soldi veri.** Sì, sempre. **Non esiste modalità carta o simulata**: grep su tutto il repo trova solo
  i flag `HyperliquidTestnet` e `LighterTestnet` (e Lighter «only supports mainnet»,
  `trader/auto_trader.go:330`). L'unico «simulated» è un capitale finto di 1000 per l'anteprima del
  prompt (`api/strategy.go:521`).
* **Protezioni.** Quelle elencate al punto 2 (stop sull'exchange, chiusura su rientro dal picco, safe
  mode, freni di frequenza, massimo posizioni, tetto al nozionale). **Manca un limite di perdita
  giornaliera o di drawdown a livello di conto nel percorso AI**: `MaxDailyLoss` e `MaxDrawdown` sono
  commentati come «hint», `dailyPnL` viene solo azzerato ogni 24 ore e `stopUntil` non è mai impostato
  (`trader/auto_trader.go:151-152`, `trader/auto_trader_loop.go:62-77`). Il «kill switch» è il bottone
  di stop a mano. Solo il modo griglia ha limiti giornalieri veri con uscita di emergenza
  (`trader/auto_trader_grid.go:183-230`).
* **Dati inviati fuori.**
  - Google Analytics **acceso di default** (`config/config.go` `ExperienceImprovement: true`): per ogni
    trade manda exchange, simbolo, importo in USD, leva, id utente e id trader; per ogni chiamata AI
    manda modello e numero di token (`telemetry/experience.go`). Si spegne con
    `EXPERIENCE_IMPROVEMENT=false`.
  - claw402.ai: riceve i prompt completi (quindi saldo, posizioni, candele) e i pagamenti.
  - nofxos.ai: con una chiave API **scritta nel codice** (`DefaultAuthKey = "cm_568c67eae410d912c54c"`,
    `provider/nofxos/client.go:19`).
  - coinank.com per le candele; ipify/icanhazip per l'IP pubblico; vergex.trade dentro due pagine della
    dashboard in iframe (`web/src/pages/DataPage.tsx`, `StrategyMarketPage.tsx`).
  - Un sistema di «hook» permette di iniettare proxy nei client HTTP (`hook/`): normale, ma da sapere.
* La roadmap del nov 2025 elenca ancora «Implement AES-256 encryption for API keys» come da fare
  (`docs/roadmap/README.md`): il codice lo fa già, la documentazione no.

## 5. Cosa può servire al proprietario e cosa no

**Può servire (come idee, non come codice da copiare):**
1. **Il replay delle decisioni registrate** (`scripts/optimize/simulate.py` + `search.py`): rigiocare le
   uscite del paper con stop/tenuta/cooldown diversi, con costi per lato misurati dai fill e con una
   parte riservata. È un attrezzo di diagnosi, non un backtest: risponde a «come e perché perdiamo»
   (uscita, stop, rientro), che è esattamente una delle domande del diario. Va usato **solo per capire**,
   mai per tarare: il paper non è un training set.
2. **Tre ipotesi concrete da mettere nel gate**, sulle quali loro dicono di aver misurato (senza fonte
   riproducibile): tenuta minima 90 minuti; niente chiusure piatte (−2%/+3% di prezzo) prima di 3 ore;
   4 ore di attesa prima di rientrare sulla stessa moneta (`trader/auto_trader_throttle.go`). Sono
   vicine al problema «il trailing chiude troppo presto». Il numero loro («+34 punti») non vale; la prova
   va rifatta con il gate a tre passaggi.
3. **La protezione dal rientro dal picco armata solo dopo un movimento di prezzo** (+5%), con la nota del
   perché: a 10× il controllo sul margine «strangolava ogni vincente» (`trader/auto_trader_risk.go:13-17`).
   Idea sensata per il trailing, da misurare.
4. **Lista di dati «di struttura»** che loro ritengono utili: variazione di open interest per finestra,
   flussi istituzionali vs retail, mappa delle liquidazioni, costo medio dei detentori. Sono tutti a
   pagamento e non nel repo; possono solo suggerire cosa cercare da fonti pubbliche.
5. Dettagli operativi: stop e target piazzati sull'exchange subito dopo il fill, verifica che la
   posizione sia davvero piatta dopo una chiusura di emergenza (`trader/auto_trader_signal_policy.go`).

**Non serve:**
* Il motore decisionale a modello di linguaggio: non deterministico, non backtestabile, nessuna prova
  dopo i costi. È la stessa cosa che il proprietario ha già spento per lo stesso motivo.
* L'Autopilot: è un «copia-segnale» di un feed a pagamento esterno, con il modello come decoratore.
* Non c'è nulla sul problema vero del proprietario: **trovare un vantaggio dopo i costi su futures a
  15 minuti-1 ora**. Non c'è un backtest, non c'è walk-forward, non c'è un confronto con un benchmark.
* I default dell'Autopilot (leva 10×, margine al 100%, 8 posizioni a size piena, niente posizioni di
  prova) sono il contrario della prudenza che il proprietario pratica.

## 6. Segnali di allarme

1. **Rendimento senza prova.** Nessuna cifra nel README (bene), ma il rimando a una classifica esterna e i
   numeri nei commenti («34 pts», «4154 cycles») senza dati né codice che li riproduca.
2. **Trading guidato dal modello senza validazione.** Nessun gate. L'«apprendimento» è il prompt che
   riceve lo Sharpe e chiede al modello di «auto-evolvere» («Sharpe < −0.5: stop trading, observe for 30
   minutes», `docs/prompt-guide.md:611-616`).
3. **Marketing.** Nove affiliazioni exchange, affiliazione Railway, sponsor, «Backed by vergex.trade»,
   gateway a pagamento del partner messo come default, richiesta di USDC al primo avvio.
4. **Token.** Nessuno trovato.
5. **Codice e documenti.** Il codice è ordinato e con test (80 file di test, CI in `.github/workflows/`),
   ma: FAQ e documenti citano file che non esistono (`decision/engine.go`; oggi è `kernel/`), roadmap e
   changelog fermi al 2025, rami `zh`/`en` del prompt identici (codice morto in `kernel/engine_prompt.go`),
   chiave API scritta nel codice, telemetria accesa di default con importi e leva.
6. **Soldi veri per forza.** Niente carta, nessun limite di perdita a livello di conto nel percorso AI.

## Giudizio onesto (5 righe)

NOFX è un prodotto ben confezionato per far girare un modello di linguaggio su un exchange vero, con
qualche freno in codice e un modello di business fatto di affiliazioni e dati a pagamento. Non offre un
approccio diverso al problema del proprietario: non c'è una prova, né riproducibile né no, che renda dopo
i costi, e nel modo predefinito la direzione la decide un segnale esterno chiuso, non il modello. Le uniche
cose da prendere sono tre ipotesi sulle uscite (tenuta minima, banda di rumore, cooldown di rientro) e
l'idea del replay delle decisioni come strumento di diagnosi: da passare dal gate, con i nostri numeri.
