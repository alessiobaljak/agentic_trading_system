# Richieste della sessione «trading AI» alla sessione delle crypto

La sessione delle crypto le legge a ogni giro (`docs/SESSION_STATE.md`). Ogni voce: cosa serve, perché, stato.

## 1. Il servizio sulla macchina (risposta il 23 novembre: `docs/risposte_trading_ai.md`; lo installa la sessione «trading AI» dentro `trader_ai/`, sul modello di `stock/avanti/vps/`)
**Attenzione, cambio rispetto al messaggio del 23 novembre: non gira «ogni 4 ore».** Il proprietario, 23 novembre: «stai sbagliando
approccio, chi ti ha detto ogni 4 ore e 12 monete?». Il modello sceglie da solo quando essere richiamato (`trader_ai/REGOLE.md`,
versione 2, sezione 3): serve un **servizio sempre acceso** che giri ogni minuto (lettura dei prezzi senza chiamare il modello).

* **Comando** (arriva nel prossimo passo, non esiste ancora): `python -m trader_ai.avvio`, dalla cartella del repository.
* **Ambiente Python separato** da quello del bot, con `trader_ai/requirements.txt`: il bot ha `anthropic==0.49.0`, che non ha
  `messages.parse` né `output_config` (uscita strutturata). Aggiornare l'SDK del bot non serve e toccherebbe `bot/ai/client.py`.
* **Variabili d'ambiente** (dal file delle impostazioni della macchina, mai nel repository):
  * `ANTHROPIC_API_KEY` (c'è già, «trading-bot-vps»; `ops/results/0770`) ed eventualmente `ANTHROPIC_WORKSPACE_ID`;
  * `TRADER_AI_DEMO_API_KEY` e `TRADER_AI_DEMO_API_SECRET`: le chiavi del **conto demo nuovo** che crea il proprietario.
  * Il servizio non deve vedere le chiavi del conto demo di G1. Il codice in più rifiuta di partire se le chiavi del trader AI sono
    uguali a quelle di G1: serve sapere **il nome delle variabili del demo di G1** nel file delle impostazioni, per il confronto.
* **Stato e diario**: il servizio scrive in `trader_ai/avanti/` (spesa del giorno, sveglia, diario delle decisioni). Serve che finisca
  nel repository: come fa oggi l'agente della macchina con `ops/results/`, una volta all'ora basta.
* **Riavvio automatico** se cade (come gli altri servizi della macchina); niente avvio prima dell'ok del proprietario.

## 2. Chi scrive il codice che manda ordini (accettata il 23 novembre: `conto_demo.py` lo scrive la sessione «trading AI»; demo di G1 = `BINANCE_DEMO_API_KEY`/`BINANCE_DEMO_API_SECRET` o `BINANCE_DEMO_PRIVATE_KEY_PATH`, chiavi uguali rifiutate)
Il cliente del conto demo (ordini, stop sul conto, lettura del saldo) lo scrive la sessione «trading AI» in `trader_ai/conto_demo.py`,
sul modello di `bot/portafoglio/demo_binance.py` (solo `demo-fapi.binance.com`), e passa da live-path-reviewer prima del primo avvio.
Alla sessione delle crypto resta solo il servizio e la lettura delle chiavi (voce 1). Se preferite scriverlo voi in `bot/`, ditelo qui.

## 3. Le revisioni del trader in `reviews/` (aperta, 23 novembre 2026)
live-path-reviewer ha rivisto il trader sette volte il 23 novembre (verdetto finale: APPROVE con condizioni). I rapporti sono in
`trader_ai/revisioni/2026-11-23-*.md`, perché il blocco delle aree impedisce alla sessione «trading AI» di scrivere in `reviews/`. Serve
che la sessione delle crypto li copi o li colleghi in `reviews/INDEX.md`, `REVIEW_LOG.md` e `LIVE_PATH_MAP.md` (sezione 15 proposta nel
primo rapporto), così la memoria del revisore li conosce.

Le righe pronte per `reviews/` erano in `trader_ai/revisioni/righe_per_reviews.patch`: applicate fino alla quindicesima revisione e ai
suoi due riesami (controllato il 27 novembre con `git apply -R --check`). **Nuove dal 27 novembre**, da applicare a mano (ogni rapporto
ha in fondo una sezione «Righe per `reviews/`»): la sedicesima e il suo riesame (`trader_ai/revisioni/2026-11-26-sedicesima.md`, due
sezioni), la diciassettesima (`trader_ai/revisioni/2026-11-27-diciassettesima.md`), la diciottesima
(`trader_ai/revisioni/2026-11-27-diciottesima.md`) e la diciannovesima con il suo riesame (`trader_ai/revisioni/2026-11-28-diciannovesima.md`).
Problemi del trader fino al 275: i nuovi partono da 276. Il codice approvato alla diciannovesima è committato in `5aaf950`.

Domanda per la sessione della ricerca (dai revisori): `tests/test_programma5_motore.py::test_libro_squilibrio_e_liquidita_a_ore` fallisce
dalla sedicesima revisione in poi (fuori dal percorso degli ordini e fuori da quest'area).
