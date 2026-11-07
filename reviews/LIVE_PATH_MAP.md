# Mappa del percorso degli ordini

Prima versione parziale: 7 nov 2026 (commit `b29f5713`). **Completata il 7 nov 2026** con la revisione completa
(`reviews/reports/2026-11-07-primo-avvio.md`), sul codice di `782a01fc` (branch `claude/brave-albattani-1b12fv`), identico a `b29f5713`
per tutti i file qui sotto. I numeri di riga valgono per quel codice: al prossimo cambio si ricontrollano.

## 1. Chi manda ordini (solo due punti, verificato con grep)

| Parte | Dove | Verso dove | Acceso da |
|---|---|---|---|
| G1 sul conto demo | `bot/portafoglio/demo_binance.py` (`DemoG1`, `ClienteDemo`) | solo `demo-fapi.binance.com` | file `ops/demo_binance_acceso` + chiavi `BINANCE_DEMO_*` |
| Vecchio esecutore, ramo reale | `bot/execution/executor.py` (`_submit_live_entry`, `_place_protective_orders`, `_close`...) | python-binance, rete di prova o conto vero | `DRY_RUN` falso (`bot/config.py:64`), rete da `BINANCE_TESTNET` (`:69`) |

Solo lettura, nessun ordine: i paper `bot/portafoglio/f5.py` (F5, G1, G11, G1N) e `eventi.py` (dati pubblici da `fapi.binance.com`,
`f5.py:47`), `scripts/verify_keys.py` (legge il conto). `bot/risk/portafoglio.py` è una simulazione, non è nel percorso.

## 2. Il giro del bot (un solo filo)

`TradingBot.run` (`bot/main.py:2514`), un giro ogni 30 secondi (`sleep_s`, `:2653`). In ordine: vecchio bot (scansione `:2589`,
`trading_cycle` `:2590`), battito `/bot_status/heartbeat` (`:2623`), poi ognuno nel suo `try`: paper F5 e G1 (`:2627-2641`),
**demo `:2643`**, paper degli eventi. Il demo aspetta quindi la fine del vecchio ciclo; ogni chiamata a Firebase può durare fino a 120 s
(nessun `httpTimeout`, `bot/core/firebase_client.py:420-425`; predefinito di `firebase_admin` 6.5.0). Il demo non ha un battito suo.

## 3. Paper, demo e conto vero

- `DRY_RUN` da variabile d'ambiente, predefinito vero (`config.py:64`), letto con `_get_bool` (`:46-50`): **vale vero solo per
  `1/true/yes/y/on`; `si`, un errore di battitura o un valore vuoto valgono falso**. Lo stesso per `BINANCE_TESTNET` (`:69`).
- `tuning.env` caricato dopo il `.env` con sovrascrittura e senza elenco delle chiavi ammesse (`config.py:35`); lo scrive solo
  `scripts/supervisor.py`, che non tocca `DRY_RUN` (`bot/learning/supervisor.py:95-103`).
- Vecchio esecutore: con `DRY_RUN` falso crea `binance.client.Client(BINANCE_API_KEY, BINANCE_API_SECRET, testnet=BINANCE_TESTNET)`
  (`executor.py:243-255`); se fallisce torna in paper (`:254-255`). Log d'avvio: `main.py:2519`, `:2532`, `executor.py:251-252`.
- Demo: indipendente da `DRY_RUN` per scelta (`demo_binance.py:18-19`); indirizzo fisso `DEMO`/`HOST_DEMO` (`:64-65`), `_url` rifiuta ogni
  altro host (`:96-100`, test `tests/test_demo_binance.py:89-97`); chiavi `BINANCE_DEMO_API_KEY`, `BINANCE_DEMO_API_SECRET` o il file
  `BINANCE_DEMO_PRIVATE_KEY_PATH` (`:266-272`, `:408-413`); firma HMAC, Ed25519 o RSA (`:249-263`).
- Chiavi del conto vero: sulla macchina secondo il proprietario (`docs/backlog.md`, voce del conto vero, aggiunta del 6 nov); nome non noto.
- Riconciliatore del vecchio ramo: spento in `DRY_RUN` (`reconciler.py:230-233`).

## 4. Limiti fissi (`bot/risk/hard_limits.py`)

| Invariante | Valore | Riga | Dove si applica |
|---|---|---|---|
| Leva massima | `MAX_LEVERAGE = 5.0` | `:17` | `safety_leverage_cap` `:46`; `risk_manager.py:77,83,93` (precedenza, leva intera); `:212-214` (ultimo cancello) |
| Rischio per operazione | `MAX_RISK_PER_TRADE = 0.03` | `:18` | `safety_risk_cap` `:53-57`; `risk_manager.py:79,94,215-217` |
| Perdita giornaliera massima | `DAILY_LOSS_LIMIT = 0.05` | `:21` | `circuit_breakers.py:79` (fermo del giorno), `:57-58` (messaggio) |
| Stop di fila prima della pausa | `CONSECUTIVE_SL_LIMIT = 6` | `:25` | `circuit_breakers.py:85` |
| Durata della pausa | `CONSECUTIVE_SL_PAUSE = 2 h` | `:26` | `circuit_breakers.py:86` (la nota a `:88` dice «4h»: testo sbagliato) |
| Rischio dimezzato in alta volatilità | `HIGH_VOL_SIGMA = 3.0`, `HIGH_VOL_SIZE_FACTOR = 0.5` | `:27-28` | `safety_risk_cap` |
| Finestra senza posizioni attorno agli eventi macro | `MACRO_FLAT_HOURS = 2.0` | `:29` | `circuit_breakers.py:92-101` |
| Leva ridotta con la volatilità | 3σ→2x, 2σ→3x, 1.5σ→4x | `:33-37` | `safety_leverage_cap` `:40-50` |

Valgono **solo per il vecchio bot** (`RiskManager`): nessun file di `bot/portafoglio/` importa `hard_limits`.

Fuori dai limiti fissi, da variabile d'ambiente (vecchio bot): numero massimo di posizioni `MAX_OPEN_POSITIONS` 5 (`config.py:176`,
applicato a `main.py:1741`), quota per posizione `MAX_POSITION_EQUITY_FRACTION` 1,0 (`:181`), stop massimo `MAX_STOP_PCT` 6% (`:707`),
perdita per moneta al giorno `RISK_PER_COIN_DAY` 1,5% (`:700`, `bot/risk/daily_cap.py`), rischio per direzione 3% (`:237`),
correlazione 0,85 e 3 posizioni (`:222-223`, `bot/risk/correlation_guard.py`).

**Test di guardia** (il loro fallimento è un allarme, non un test da correggere): `tests/test_risk.py:32` (leva 10 → 5, con
`MAX_LEVERAGE == 5.0`), `:41` (rischio 3%), `:75` (fermo a −6%), `:84` (nessun fermo a −2,1%), `:94` (pausa dopo 6 stop), `:103`
(ultimo cancello); `tests/test_sizing.py:104` (leva fra 1 e 5 con il moltiplicatore 1,3).

## 5. Interruttori del vecchio bot (`bot/risk/circuit_breakers.py`)

- Stato in RTDB `/risk_state`: caricato a `main.py:516`, salvato da `_persist_risk_state` (`main.py:2157-2158`).
- `register_trade_result` (`:72-90`) a ogni chiusura: `main.py:1523` (strategia), `:1549` (chiusure manuali). Un'eccezione lì esce da
  `trading_cycle` e salta il resto del ciclo (presa solo a `main.py:2603-2607`).
- Entra nell'ultimo cancello: `risk_manager.py:220`.
- **`BACKTEST_PARITY=true`** (`config.py:672`): `blocking_reason` sempre `None` (`circuit_breakers.py:50-52`) e niente tetto delle
  posizioni (`main.py:1741`). Nessun controllo lo vieta con `DRY_RUN` falso.

## 6. Parametri della dashboard (vecchio bot)

Catena: `dashboard/app/components/RiskControl.tsx:55,108` → Firestore `user_risk_settings/current` → `read_user_risk`
(`main.py:610-619`, prima di ogni trade) → `RiskSettings` (`bot/core/models.py:187-196`: `leverage`, `risk_per_trade`, `updated_at`,
`updated_by`; nessun controllo, accetta `nan` e `inf`; i campi in più si scartano) → `risk_manager.py:63-94`.

| Controllo | Dove | Comportamento |
|---|---|---|
| Dashboard | `dashboard/app/lib/hardLimits.ts:13-17` | taglia a 1-5x e 0,5-3% (comodità, non sicurezza) |
| Regole Firestore | `firebase/firestore.rules:32-41` | solo il proprietario, leva 1-5, rischio (0, 3%]; non chiude l'elenco dei campi; utente segnaposto (`:27`) |
| Bot | `main.py:616-619` | documento illeggibile → 2x e 1% in silenzio |
| Bot | `risk_manager.py:77-80`, `:212-217` | oltre il limite → tagliato con una nota, non rifiutato |
| Bot | `risk_manager.py:63-65`, `:230-237` | rischio `nan` → approvato con quantità `nan` (provato il 7 nov) |

Il bot usa l'Admin SDK: le regole non lo limitano (`firestore.rules:6-8`).

## 7. G1 sul conto demo (`bot/portafoglio/demo_binance.py`)

**Costanti** (nel codice, fuori da `hard_limits.py`, nessun test tiene la leva): `LEVA = 5` (`:73`, inviata a `:639`; i due lati
fanno il 200% del capitale), `STOP_CONTO = 0.35` dal massimo (`:78`, controllo `:702`), `OGNI_VALUTAZIONE_S = 3600` (`:75`),
`ATTESA_DOPO_ERRORE_S = 1800` (`:76`), `VALIDITA_LIMITE_S = 3600` (`:74`), `SOGLIA_CONFRONTO = 0.02` (`:79`), `QUOTA_EVENTI = 0.05`
(`:71`, eventi spenti sul demo: `ops/demo_binance_eventi_acceso` non c'è).

**Ingressi**: decisione di G1 da `data/paper_g1.json` (`ultimo_lunedi`, `pesi`; `:516-520`), scritta da `PaperG1` alle 00:05 UTC su
giorni chiusi (`f5.py:597-615`, `:91-156`, attesa del regolamento delle 00:00 `:516-522`). **Nessun controllo** su età, somma, tetto per
moneta o valori dei pesi prima degli ordini. Capitale ridotto dal file `ops/demo_binance_capitale` (`:91`, `:321-329`: qualunque numero
positivo; oggi `1000`), filtri del conto vero da `filtri_conto_vero.json` (`:92`, copia fissa del 6 nov, `piu_severi` `:190-203`).

**Il giro `tick`** (`:474-539`), in ordine:
1. acceso? (`:475`); chiave (`:477-484`);
2. **attesa di 30 minuti dopo un errore** (`:485-486`) — vale anche per pulsante e stop;
3. stato locale `data/demo_binance.json` (`:488`, `carica` `:415-419` dà `{}` su errore; `salva` atomico `:421-425`); capitale (`:489`);
4. **pulsante**: RTDB `/commands/demo_binance_chiudi_tutto` (`:84`, `:490`) o testo nuovo nel file `ops/demo_binance_chiudi_tutto`
   (`:88`, `:491`, `_comando_file` `:439-450`) → `chiudi_tutto` (`:452-471`): annulla gli ordini, chiude a mercato con «solo riduzione»,
   segna `fermo`; una chiusura rifiutata va solo in `errori` (`:463-464`);
5. **da fermo** (`:497-513`): solo «riparti» (RTDB `/commands/demo_binance_riparti` `:85` o file `:89`), che riparte con il massimo di
   adesso (`:502`); altrimenti solo il valore del conto. Nessun nuovo tentativo sulle posizioni rimaste;
6. dopo un'ora gli ordini limite non eseguiti → annullati e resto a mercato (`chiudi_ordini` `:665-694`; resto dalla quantità
   pianificata, nessun identificativo, `DELETE` `:675` non protetto);
7. decisione nuova → `parti_da_zero` se c'è un capitale in attesa (`:360-398`) e `ribilancia` (`:603-663`);
8. ogni ora `valuta` (`:696-718`, **stop sul conto** `:702-703`), `controlla_margine` (`:556-578`), `confronta` (`:580-601`).
9. errore → `_ultimo_tentativo`, stampa, RTDB `/demo_binance/errore` (`:536-539`); lo stato del giro non si salva.

**Ordini** (`ribilancia`): filtri da `exchangeInfo` (`:605`, `filtri` `:119-129`, valore minimo predefinito 5 se manca `:126`),
prezzi mark (`:608`); una posizione per moneta, controllata una volta (`:609-613`); ordini aperti annullati prima di contare le
posizioni (`:615-620`); `ordini_del_giorno` (`:141-160`): quantità al passo verso zero, sotto i minimi saltate, prezzo limite al passo
(`giu` per comprare, `su` per vendere), «solo riduzione» se riduce o chiude (`:158`); identificativo `id_ordine` nuovo a ogni tentativo
(`:132-138`, `:631`); margine unico (`CROSSED`) e leva 5 alla prima volta per moneta (`:635-640`, `leve` nello stato); un rifiuto non
ferma gli altri (`:642-644`). Ordini limite GTC al mark, un'ora (`:630`).

**Errori**: `ClienteDemo.chiedi` (`:282-293`): `timeout=15`, finestra 5 s, ogni risposta ≥ 400 → `RuntimeError` con 200 caratteri della
risposta; nessuna gestione di 429/418 né di `Retry-After`; nessuna lettura dell'ora di Binance. Nessun avviso Telegram nel modulo.

**Conto ridotto**: valore = `totalMarginBalance` − scarto (`:545`, scarto `:357`, `:393`); lo stop e i rapporti usano questo valore.

## 8. Pulsanti che chiudono tutto

| Sistema | Comando | Senza Firebase | Ritardo massimo |
|---|---|---|---|
| Demo | RTDB `/commands/demo_binance_chiudi_tutto` (regola: solo vero/falso, `database.rules.json:18-21`) | no | giro (30 s + vecchio ciclo) |
| Demo | file `ops/demo_binance_chiudi_tutto`, testo nuovo | sì (arriva con il `git pull` dell'agente ops, ogni minuto) | 1 min + giro, **+30 min dopo un errore** |
| Demo | stop sul conto −35% dal massimo | sì | **fino a 1 ora** (+30 min dopo un errore) |
| Vecchio bot | RTDB `/commands/kill_switch` (vero/falso, `database.rules.json:7-10`) e `/commands/bot_state` (nessuna regola: non scrivibile dalla dashboard), `main.py:860-872`, `kill_switch.py:40-59` | **no** | valutato solo a `main.py:1585`, dopo tre uscite anticipate: flusso appena ripreso (`:1559`), Firebase muto da 300 s (`:1568`, `config.py:734-735`), riconciliazione che blocca (`:1578`) |

Esecuzione del vecchio pulsante: `_emergency_close` (`main.py:1265-1290`) → `force_close_all` (`executor.py:1101-1110`) → `_close`.

## 9. Vecchio ramo reale (`bot/execution/executor.py`, solo `DRY_RUN` falso)

- Ingresso: leva per moneta (`:621`), ordine LIMIT GTC con `round(..., 6)` (`:622-625`), attesa del riempimento (`_await_fill`
  `:665-683`, si ferma al primo errore di lettura `:673-675`), sotto la quota minima annulla e chiude il resto (`:639-645`, `:693-703`).
- Protezioni: `STOP_MARKET` «solo riduzione» sulla quantità piena (`:719-727`, senza tipo di prezzo = ultimo prezzo), obiettivi
  `TAKE_PROFIT_MARKET` (`:729-744`); un rifiuto si stampa e basta. Stop spostato con annulla-e-rimetti (`_sync_exchange_stop` `:746-778`).
- Chiusure: a mercato «solo riduzione» sulla quantità interna (`:1051-1069`), poi annullo di tutti gli ordini della moneta; la posizione
  esce dallo stato anche se la chiusura fallisce (`:1093`). Margine mai impostato. Nessun identificativo d'ordine.
- `bot/execution/error_handler.py` (classificazione degli errori): non usato da nessun file (grep del 7 nov).
- Riconciliatore (`reconciler.py`, filo suo ogni 60 s, `config.py:622-633`): `_exchange_state` (`main.py:1201-1226`) conta stop e
  obiettivi insieme sia come protezione sia come doppioni (`:1215-1222`): con stop + obiettivo c'è sempre un «doppione» critico;
  con il solo obiettivo la posizione risulta protetta (`reconciler.py:113-120`). Azioni in `_apply_reconciliation` (`main.py:1228-1253`):
  la chiusura di una moneta usa `force_close_all`, che chiude tutte le posizioni.

## 10. Firebase

- `set_rtdb` non solleva mai e restituisce vero o falso (`firebase_client.py:652-679`); `get_rtdb` su errore restituisce l'ultimo valore
  noto (`:681-705`). I chiamanti del demo non guardano il valore restituito.
- Regole: `firebase/firestore.rules` (solo `user_risk_settings` scrivibile, `:32-41`), `firebase/database.rules.json` (solo
  `kill_switch`, `close_position`, `demo_binance_chiudi_tutto`, `demo_binance_riparti`, `close_position_meta` scrivibili). Utente
  `REPLACE_WITH_YOUR_FIREBASE_UID` in tutti e due: regole pubblicate da confermare con Alessio.

## 11. Il canale `ops/`

- `scripts/ops_agent.py` ogni minuto (timer systemd): `git pull` (avanti veloce, altrimenti rebase con annullo se fallisce,
  `:271-303`), esegue le richieste contro la lista bianca della macchina (non nel repo), senza shell, con oscuramento dei segreti
  (`:53-75`), battito in `ops/heartbeat.md` (oggi la macchina segue `claude/brave-albattani-1b12fv`).
- File letti dal demo nel repo: `ops/demo_binance_acceso`, `ops/demo_binance_capitale` (`1000`), `ops/demo_binance_chiudi_tutto` e
  `ops/demo_binance_riparti` (oggi assenti), `ops/demo_binance_eventi_acceso` (assente). Chi può scrivere sul branch comanda il demo.
- Orologio: `systemd-timesyncd` attivo negli elenchi dei processi (`ops/results/0196-processi.md`, `0413-1ott-processi-col-gate.md`).

## 12. Test del percorso

`tests/test_demo_binance.py` (25 test: indirizzo, arrotondamenti, ordini, pulsante, stop −35%, margine, file, conto ridotto),
`tests/test_g1_poco_capitale.py`, `tests/test_demo_contro_paper.py`, `tests/test_paper_f5.py`, `tests/test_risk.py`, `tests/test_sizing.py`,
`tests/test_kill_switch_levels.py`, `tests/test_reconciler.py` (solo la funzione pura, non `_exchange_state`), `tests/test_live_orders.py`,
`tests/test_execution.py`. Suite intera al 7 nov: `2545 passed`. Non coperti: i guasti a-g del rapporto del primo avvio.

## 13. Punti noti aperti (dettaglio nel rapporto del primo avvio)

Demo: resto a mercato doppio dopo un errore; pulsante e stop sordi 30 min dopo un errore, stop solo ogni ora; chiudi tutto senza nuovi
tentativi; «riparti» stantio che annulla lo stop; pesi senza controllo; nessun avviso; decisione di G1 senza età massima; 429/418;
stesso filo del vecchio bot; massimo dello stop solo in locale; capitale senza tetto. Vecchio ramo: `DRY_RUN` letto male; riconciliatore;
ordini non arrotondati e chiusure che lasciano scoperto; pulsante dietro tre uscite anticipate; parità col backtest.

## Storia degli invarianti

- 7 nov 2026: nessun invariante cambiato nel codice. Una modifica proposta (leva massima 10, perdita giornaliera dalla dashboard) ha
  avuto REQUEST CHANGES: `reviews/reports/2026-11-07-limiti-leva-perdita-giornaliera.md`.
- 7 nov 2026, primo avvio: mappati per la prima volta gli invarianti del demo (leva 5, stop −35% ogni ora, pulsanti, margine unico,
  una posizione per moneta, capitale ridotto 1000). Nessuno cambiato.
