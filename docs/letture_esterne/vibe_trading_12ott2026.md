# HKUDS/Vibe-Trading — riassunto in sola lettura (12 ott 2026)

Clone letto: `/tmp/claude-0/-home-user-agentic-trading-system/9da12ffe-13c5-5904-8f7e-5ce576103042/scratchpad/repos/vibe-trading`
(profondità 1: un solo commit visibile). Tutti i percorsi qui sotto sono relativi a quella cartella.
Nessuno script eseguito, nessuna installazione, nessuna modifica: solo lettura di file.

---

## 1. Cos'è

**Autori.** Il pacchetto dichiara `authors = [{name = "HKUDS", email = "hkuds@connect.hku.hk"}]`
(`pyproject.toml`, riga 9). Il dominio `connect.hku.hk` è quello dell'Università di Hong Kong, quindi
sì, è il gruppo HKUDS di HKU. Il `NOTICE` dice «Copyright 2026 HKUDS contributors». Il README
(sezione «Ecosystem», righe 2202-2231) lo colloca accanto ad altri progetti HKUDS: NanoBot,
AI-Trader («Agent-Native Signal & Copy Trading Platform»), CLI-Anything, OpenSpace, ClawTeam.
Nel repo non ho trovato il nome del laboratorio né dei ricercatori.

**Scopo dichiarato.** «An open-source research workspace for turning finance questions into runnable
analysis» (`README.md`, riga 363); «Natural-language finance research AI agent with backtesting»
(`pyproject.toml`, riga 4). Slogan: «Your Personal Trading Agent» (`README.md`, riga 9). In pratica:
un agente LLM che, da una richiesta in linguaggio naturale, scarica dati, scrive codice di strategia,
lancia un backtest, produce report, e può (opzionalmente) passare ordini a un broker dentro limiti fissati
dall'utente.

**Ultimo commit.** `c25fea2b`, 12 ott 2026 19:30 (+08:00), autore «alexwan», «feat(providers): add
claude-cli provider backed by local `claude -p` (#1804)» (`git log`). Il numero 1804 è il numero della
pull request: il progetto ha fatto oltre 1800 fra PR e issue.

**Età.** Il `CHANGELOG.md` parte dalla versione 0.1.8 del 17 mag 2026 e arriva alla 0.1.16 del
29 set 2026 (righe 261-3233). Quindi ~5 mesi di storia visibile; la release 0.1.16 dichiara «492
commits and 116 merged pull requests since 0.1.15, from 16 contributors» (`README.md`, riga 85).

**Licenza.** MIT (`LICENSE`). Il `NOTICE` aggiunge Apache-2.0 per le formule prese da Microsoft Qlib
e dichiara che le formule di Kakushadze (101 alpha), Guotai Junan (191 alpha) e Fama-French sono
«contenuto matematico», non coperto da copyright.

**Dimensione.** 2815 file tracciati (`git ls-files | wc -l`); 153 MB di cui: `.git/` 59 MB,
`assets/` 35 MB (due video `Frontend.mp4` 16 MB e `cli.mp4` 11 MB, più png), un font CJK da 20 MB
in `agent/src/shadow_account/assets/VibeCJK-Regular.ttf`, `agent/` 46 MB. Non ci sono dati di
mercato né notebook nel repo. Codice: 1985 file `.py` sotto `agent/`, 810 file di test, 7128
funzioni `def test_` (conteggio grep). Il `README.md` da solo è 369 KB, tradotto in 6 altre lingue.

**Articolo scientifico.** Nessuno. Non c'è `CITATION.cff`, nessun bibtex, nessun «our paper». L'unico
arXiv citato è Kakushadze 2015 «101 Formulaic Alphas» (arXiv:1601.00991) come fonte delle formule
(`agent/src/factors/zoo/alpha101/LICENSE.md`, riga 14). È un prodotto software, non una ricerca
pubblicata.

**Segni di adozione visibili nel repo.** Badge Trendshift (repo 25527) e PyPI `vibe-trading-ai`
(`README.md`, righe 16-24); 18 connettori broker; Discord, Feishu, WeChat; 7 lingue; un incidente di
Discord impostore del 18 giu 2026 e un token falso «VibeTrading_HKU» che hanno dovuto smentire
(`SECURITY.md`; `README.md` riga 53). Il numero di stelle non è scritto nel repo.

## 2. Architettura: cosa fa davvero

**Agente.** Un ciclo ReAct su LangChain/LangGraph (`agent/src/agent/loop.py`; dipendenze in
`pyproject.toml` righe 23-27). Fino a 50 iterazioni per esecuzione (`loop.py`, riga 190). 110 tool
auto-scoperti, 90 «skill» (file `SKILL.md`), 30 «swarm» cioè squadre di agenti con ruoli
(`agent/src/swarm/presets/`), 76 tool esposti via MCP (`README.md`, righe 2128-2200).

**Ruoli degli agenti.** I preset sono squadre di «analisti» in prosa. Esempio
`agent/src/swarm/presets/crypto_trading_desk.yaml`: «Funding Rate & Basis Analyst», «Liquidation &
Microstructure Analyst», «On-Chain & Stablecoin Flow Analyst», «Risk Manager»; ciascuno con un prompt
di sistema lungo, tool `bash/read_file/write_file/get_market_data/read_url`, massimo 50 iterazioni e
30 minuti. L'uscita è un report testuale, non un segnale numerico testabile.

**Dati.** 29 caricatori di prezzi OHLCV (`agent/backtest/loaders/`), con catene di ripiego per mercato
(`README.md`, righe 584-612). Crypto: `okx`, `binance`, `ccxt`; il `ccxt_loader.py` scarica per i
perpetui USD-M sia le candele di scambio sia quelle di mark price e i regolamenti del funding (righe
315-378), con intervalli 1m/5m/15m/30m/1h/4h/1d (righe 33-43). Oltre ai prezzi: 22 tool di sola lettura
su fondamentali, flussi, notizie, SEC, 13F, opzioni, paper arXiv (`README.md`, riga 655). Social: ci
sono preset «sentiment_intelligence_team» e «social_alpha_team» e una ricerca web DuckDuckGo
(`web_search_tool.py`), ma nessuna serie storica di social usabile in un backtest.

**Mercati e orizzonte.** Azioni Cina/HK/USA/Canada/UK/India/Corea/Vietnam/Brasile/Argentina, crypto spot
e perpetui, futures, forex, opzioni: 11 motori (`agent/backtest/engines/`). L'orizzonte di default è
giornaliero e 10 anni («data frequency (daily)», «default to 10 years back», skill
`agent/src/skills/strategy-generate/SKILL.md`, righe 20-33); l'intraday fino a 1 minuto è supportato dal
runner (`agent/backtest/runner.py`, riga 42).

**Come decide un trade nel backtest.** L'LLM scrive due file: `config.json` e `code/signal_engine.py`,
una classe `SignalEngine.generate(data_map) -> {codice: serie di segnali in [-1, 1]}`
(`strategy-generate/SKILL.md`, righe 60-78). Poi il tool `backtest` lancia `python -m backtest.runner`
in un sottoprocesso (`agent/src/tools/backtest_tool.py`), e il motore esegue barra per barra senza LLM.
Il riempimento è all'apertura della barra successiva: «close is not available information: using it is
lookahead» (`agent/backtest/engines/base.py`, riga 629). Quindi il backtest è deterministico; la
strategia dipende da cosa ha scritto il modello quella volta.

**Come decide un trade dal vivo.** Un processo persistente (`agent/src/live/runtime/runner.py`) che a
ogni «tick» fa: kill switch → scadenza mandato → riconciliazione posizioni → turno autonomo dell'LLM →
audit. Il prompt del turno (righe 219-263) elenca i limiti del mandato (capitale, nozionale massimo per
ordine, esposizione massima, leva, strumenti, trade al giorno) e chiude con: «Assess the current
opportunity set, then act within the mandate. If no action is warranted this tick, hold and explain
why.» Cioè: dal vivo decide l'LLM, in modo discrezionale, con i tool; non c'è una strategia sistematica.
Un gate meccanico «fail-closed» (`agent/src/live/enforcement.py`, `order_guard.py`) rifiuta ordini fuori
mandato e un file `HALT` ferma tutto senza bisogno che il modello collabori (`halt.py`).

**Esecuzione.** Broker reali tramite 18 connettori (`agent/src/trading/connectors/`). Per Binance: paper
= testnet spot (`testnet.binance.vision`), live = mainnet, con chiavi e host diversi
(`connectors/binance/__init__.py`, righe 8-13). **I perpetui USD-M sono in sola lettura**: «USD-M permits
only signed account and position reads against fapi.binance.com; all order and market-data surfaces are
rejected» (`connectors/binance/sdk.py`, righe 3-5). Quindi con questo progetto non si fa paper né live
sui futures perpetui Binance: solo backtest.

**Controllo dei numeri.** C'è un «grounding gate» (`agent/src/agent/grounding/`): ogni cifra nella
risposta deve corrispondere a un'evidenza prodotta da un tool, altrimenti viene tagliata (`README.md`,
riga 85). Le «run card» registrano hash del backtest e citazioni metrica → riga del CSV
(`agent/backtest/run_card.py`, righe 456-505). Un manifest con hash di prompt, skill, tool e versioni
(`README.md`, «Governance & Audit Trail»).

## 3. Validazione: come dimostrano che funziona

**Non lo dimostrano, e non lo sostengono.** Nel README non c'è nessun rendimento del sistema, nessuno
Sharpe, nessun «+X%». Il disclaimer dice: «This broker-trading capability is experimental and not
verified by us against a real broker account» (`README.md`, riga 2402). Le uniche due prove numeriche nel
repo riguardano cose specifiche, non l'agente:

**(a) Studio sui 191 alpha GTJA** (`wiki/research-lab/posts/alpha-191-in-2026.html`). Azioni cinesi CSI
300, 2018-01-02 → 2025-12-31, punto-nel-tempo per la composizione dell'indice, prezzi rettificati.
Misura solo la correlazione di rango (IC) fra alpha e rendimento del giorno dopo: 8 «vivi» (4%), 14
«invertiti» (7%), 168 «morti» (88%), 1 non calcolabile. Dichiarano: «No t-cost adjustment… The bench does
not measure turnover», «Treat this post as a signal-quality scan, not a profitability claim». La prima
versione (17 mag 2026) usava prezzi non rettificati e la composizione attuale dell'indice; corretta il
4 ago e rifatta il 29 set 2026 (nota «Revised» in testa al post).

**(b) Studio interno sulle opzioni** (`docs/sessions/2026-10-09_options_strategy_candidates.md`).
SPY/QQQ/AAPL/MSFT, in-sample 2016-2020, fuori campione 2021-01 → 2026-10-08 con parametri congelati,
costi 1-2% del premio per lato, confronto con buy & hold. Risultato: nessuna strategia di vendita di
premio regge (da -4% a +4% l'anno contro 15-19% del buy & hold); la covered call 0.20 delta su SPY ha
Sharpe 1.10 contro 0.94 del buy & hold. Loro stessi scrivono: «The model has no volatility risk premium…
This backtest cannot validate them either way.» È uno studio onesto ma su azioni USA, a frequenza
giornaliera, con opzioni prezzate a Black-Scholes sulla volatilità storica.

**Strumenti di validazione del motore.** `agent/backtest/validation.py`: test di permutazione Monte
Carlo sull'ordine dei trade (1000 simulazioni, seme 42), intervallo bootstrap dello Sharpe, walk-forward.
15 metriche (`agent/backtest/metrics.py`: sharpe, sortino, calmar, max_drawdown, profit_factor,
information_ratio, benchmark_beta, avg_turnover…). Separazione fra barre di riscaldamento e periodo
valutato (`warmup_bars`, `README.md` riga 141). Non c'è un gate a passaggi fuori campione come quello del
proprietario: il walk-forward è uno strumento che si invoca, non un filtro obbligatorio.

**Costi nel motore crypto** (`agent/backtest/engines/crypto.py`, righe 43-64): maker 0,02%, taker 0,05%,
slippage 0,05% per lato, funding fisso 0,01% ogni 8 ore; opzione `funding_mode="data"` per usare i
regolamenti reali e `perpetual_strict` per mark price, liquidazione isolated/cross e bracket di
manutenzione. Aperture a taker, chiusure a maker (riga 125). 58 test in
`agent/tests/test_crypto_engine.py` (funding dedotto all'ora di regolamento, taker/maker, slippage).

**Lookahead del modello.** Riconosciuto, ma solo come avviso. `agent/backtest/run_card.py`, righe
144-163: se `model_training_cutoff` non è nel config → «Training cutoff for … is unknown; assume results
may reflect what the model remembers»; se la fine del backtest è prima del cutoff → «results may reflect
what the model remembers». Il cutoff lo deve dichiarare l'utente, e il run non viene bloccato.

**Limiti dichiarati.** Molti e chiari: oltre ai due studi, il CHANGELOG 0.1.8 dice che l'universo
`btc-usdt` è a un solo asset e quindi l'IC cross-sectional «returns alive/reversed/dead = 0/0/0 by
construction» (`CHANGELOG.md`, sezione «Known limitations» in fondo). Le news del README elencano bug
di correttezza corretti quasi ogni giorno: fattore momentum che leggeva il prezzo di oggi (30 set),
backtest che valutava un anno in più di quello richiesto (28 ago), audit che restituiva PASS senza aver
verificato nulla (6 set), Sharpe gonfiato dai fermi di mercato (29 lug) (`README.md`, righe 85-175).

## 4. Riproducibilità e dipendenza dal modello

**Serve un LLM.** Sì. Default: OpenRouter con `deepseek/deepseek-v4-pro` (`README.md`, riga 1226;
`agent/src/providers/llm_providers.json`, righe 2-10). Alternative: Anthropic, OpenAI, DeepSeek, Codex
via OAuth, GitHub Copilot, Ollama locale (senza chiave), e dal commit di oggi il provider `claude-cli`
che usa il login locale di Claude Code senza chiave API (`README.md`, righe 1058-1080). Con
l'abbonamento Claude Code CLI quindi non ci sono chiamate API a pagamento; con OpenRouter sì.

**Quante chiamate.** Il repo non pubblica prezzi; dalla struttura: una ricerca singola fa fino a 50
iterazioni, cioè fino a ~50 chiamate al modello (`loop.py`, riga 190); uno swarm come
`crypto_trading_desk` ha 4 agenti × 50 iterazioni = fino a 200 chiamate; il runner live fa un turno agente
per tick, con cadenza di default 60 secondi se il job non ha una pianificazione
(`agent/src/live/runtime/scheduler.py`, riga 36) e ricontrollo ogni 5 minuti. Con finestre di contesto
da 128k fino a 1M token (`agent/src/providers/context_windows.json`) e compattazione automatica, una
sessione di ricerca lunga consuma centinaia di migliaia di token. Stima mia, non un numero del repo.

**Il risultato dipende dal modello.** Sì, e lo dicono loro: «Model choice directly decides whether the
agent uses its tools or fabricates answers from training data» (`README.md`, riga 1217); i modelli
piccoli «will appear to answer from memory» (riga 1223). Il backtest in sé è riproducibile (seme fisso,
manifest con hash, `run_manifest.json`, `llm_usage.json`); la **generazione** della strategia no: due
esecuzioni con lo stesso prompt possono produrre due `signal_engine.py` diversi.

## 5. Cosa può servire al proprietario, e cosa no

**Può servire (idee, non codice da importare):**

1. **Etichetta del cutoff del modello sulle strategie.** Ogni strategia generata da un LLM porta nel run
   card provider, modello e data di cutoff; se il periodo di test finisce prima del cutoff, avviso
   (`run_card.py`, righe 119-163). Il gate del proprietario potrebbe pretendere la stessa cosa e
   rifiutare, non solo avvisare.
2. **Soglie di evidenza esplicite** (`agent/src/strategy_discovery/models.py`, righe 75-89): minimo 10
   trade, minimo 730 giorni di copertura, e la **commissione di pareggio in punti base** (quanta fee
   azzera il rendimento): sotto 5 bps la strategia è «cost-sensitive» e non si raccomanda senza un
   controllo esplicito dei costi; fra 5 e 10 bps è «borderline». Per chi perde «soprattutto per i costi»
   è una metrica da aggiungere al gate: una strategia a 15 minuti con pareggio sotto i costi reali di
   Binance (taker 0,05% = 5 bps per lato, 10 bps andata e ritorno) è morta prima di nascere.
3. **Decadimento dell'evidenza** (stesso file, righe 95-118): evidenza più vecchia di 90 giorni è
   «aging», oltre 180 è «stale» ed esclusa dalle raccomandazioni. Idea per il registro
   `strategy_registry/validated`: una data di scadenza.
4. **Test anti-lookahead a sentinella** (`agent/tests/factors/test_lookahead.py`, descritto in
   `CHANGELOG.md` 0.1.8): si corrompono le righe future e il valore del segnale alla riga sonda deve
   restare identico entro 1e-9. Trasferibile a qualsiasi generatore di segnali.
5. **Motore crypto perpetui con funding reale e mark price** (`crypto.py` + `ccxt_loader.py`): utile
   come secondo motore indipendente per confrontare il PnL netto di una stessa strategia con il proprio
   backtest e scovare differenze di costi. Va letto, non eseguito, finché non si è deciso che è affidabile
   (vedi i bug corretti di recente, punto 3).
6. **Regola «un numero con la sua fonte» resa meccanica** (grounding gate): il proprietario la applica a
   mano; qui è un filtro automatico che taglia la cifra senza evidenza. Concettualmente identico.

**Non serve:**

1. Nessuna strategia pronta per futures crypto a 15 minuti-1 ora. La parte crypto dell'alpha zoo è
   vuota di fatto (universo a un solo asset → IC 0/0/0).
2. L'LLM non è una fonte di vantaggio: il progetto non lo sostiene e i loro due studi dicono il
   contrario (4% di alpha vivi senza costi; strategie di opzioni da manuale che non battono buy & hold).
   Il problema del proprietario (0 su 630 dopo i costi) non è risolto da un agente che scrive strategie
   in linguaggio naturale: cambia solo chi le scrive.
3. Niente paper o live sui perpetui Binance (sola lettura). Il paper è testnet spot.
4. Le squadre di «analisti» producono testo; non è un segnale che passi un gate.
5. Peso: ~60 dipendenze Python obbligatorie (`pyproject.toml`), 2800 file, un README da 369 KB, cambia
   ogni giorno. Portarlo dentro un sistema piccolo e controllato costa più di quanto rende.
6. Il live è discrezionale («assess the opportunity set, then act»): l'opposto di una decisione
   riproducibile.

## 6. Segnali di allarme

* **Affermazioni di rendimento senza prova:** nessuna. È il punto più a favore del progetto.
* **Backtest su periodi noti al modello:** rischio riconosciuto ma gestito solo con un avviso e solo se
  l'utente dichiara il cutoff. Lo studio sulle opzioni ha fuori campione fino all'8 ott 2026, ma i
  parametri li ha scelti una sessione AI in-sample (il file è un log di sessione).
* **Costi:** presenti nel motore (commissioni, slippage, funding); assenti nello studio sugli alpha,
  dichiarato.
* **Codice eseguibile:** non verificato da me (vietato eseguire). C'è CI su GitHub
  (`.github/workflows/test.yml`), 810 file di test. I log in `docs/sessions/` dichiarano «335 tests
  pass» ma sono scritti dall'agente, non verificabili da qui.
* **Bug recenti nel motore:** lookahead in un fattore (30 set), anno extra valutato (28 ago), audit
  PASS a vuoto (6 set), Sharpe gonfiato (29 lug). Onestamente dichiarati nel README, ma vuol dire che il
  motore aveva errori di base fino a poche settimane fa: un numero uscito da qui prima di ottobre 2026
  non è affidabile senza rifare il run.
* **Codice scritto in gran parte da agenti AI:** `AGENT_CONTRIBUTOR_GUIDE.md` esiste apposta; i file in
  `docs/sessions/` sono log di sessione; `CONTRIBUTING.md` vieta i trailer di attribuzione AI, quindi non
  si distingue cosa ha scritto chi. Ritmo: 1804 PR/issue in 5 mesi.
* **Promozione:** README da 369 KB con video, badge, 7 lingue, link di referral QVeris («+1,000 bonus
  credits and supports the project», riga 666), nome «Vibe», ecosistema con una piattaforma di copy
  trading. Non è una truffa, ma è un prodotto che cerca utenti, non un articolo.
* **Nessun articolo scientifico** nonostante l'email universitaria.
* **Truffe attorno al nome:** token falso e Discord impostore (`SECURITY.md`). Non è colpa loro, ma chi
  cerca «Vibe-Trading» in rete trova anche quello.

## Giudizio onesto (5 righe)

1. È un prodotto software serio, enorme e in corsa, fatto da un gruppo universitario ma senza ricerca
   pubblicata: un «banco di lavoro» per far scrivere e testare strategie a un LLM, non un sistema che
   guadagna.
2. Non promette rendimenti, e le due uniche prove che pubblica dicono la stessa cosa che il proprietario
   ha già misurato: le strategie da catalogo quasi mai reggono fuori campione, figuriamoci dopo i costi.
3. La parte che vale la pena studiare è il rigore sui numeri: fonte obbligatoria, cutoff del modello
   dichiarato, commissione di pareggio in punti base, scadenza dell'evidenza, test a sentinella contro il
   lookahead.
4. Non offre nulla di pronto per perpetui Binance a 15 minuti: niente strategie, niente paper, niente
   live su quei contratti; e il motore ha avuto bug di lookahead e metriche fino a settembre 2026.
5. Da leggere come fonte di idee per il gate, non da adottare: il problema del proprietario è trovare un
   vantaggio dopo i costi, e un agente che scrive strategie in linguaggio naturale non lo risolve.
