# Mappa del percorso degli ordini

Prima versione: 7 nov 2026 (`b29f5713`); completata col primo avvio (`reviews/reports/2026-11-07-primo-avvio.md`, codice di `782a01fc`).
Aggiornata il 7 nov sul `9f47972c` (`reviews/reports/2026-11-07-correzioni-9-problemi.md`). **Aggiornata il 7 nov 2026 sul commit
`5d5d26ad`** (`reviews/reports/2026-11-07-correzioni-25-31.md`): i numeri di riga di `bot/portafoglio/demo_binance.py`, `bot/config.py` e
`bot/execution/executor.py` valgono per `5d5d26ad` (nell'esecutore +1 rispetto al `9f47972c` dopo la riga 14); `bot/main.py` invariato.
Al prossimo cambio si ricontrollano.

## 1. Chi manda ordini (verificato con grep il 7 nov su `9f47972c`; `5d5d26ad` non aggiunge invii nuovi)

| Parte | Dove | Verso dove | Acceso da |
|---|---|---|---|
| G1 sul conto demo | `bot/portafoglio/demo_binance.py` (`DemoG1`, `ClienteDemo`) | solo `demo-fapi.binance.com` | file `ops/demo_binance_acceso` + chiavi `BINANCE_DEMO_*` |
| Vecchio esecutore, ramo reale | `bot/execution/executor.py` | **nessuno: bloccato dal `9f47972c`** | `_init_binance` non crea il client e rimette `dry_run` vero (`executor.py:244-254`) |

Solo lettura, nessun ordine: i paper `bot/portafoglio/f5.py` (F5, G1, G11, G1N) e `eventi.py` (dati pubblici da `fapi.binance.com`,
`f5.py:47`), `scripts/verify_keys.py` (legge il conto con python-binance, `:33-38`). `bot/risk/portafoglio.py` è una simulazione.

## 2. Il giro del bot (un solo filo)

`main()` (`bot/main.py:2656-2659`): prima `controlla_avvio` (`config.py:787-800`), poi `TradingBot.run` (`main.py:2514`), un giro ogni 30
secondi (`sleep_s`, `:2653`). In ordine: vecchio bot (scansione `:2589`, `trading_cycle` `:2590`), battito `/bot_status/heartbeat` (`:2623`),
poi ognuno nel suo `try`: paper F5 e G1 (`:2627-2641`), **demo `:2643`**, paper degli eventi. Il demo aspetta la fine del vecchio ciclo; ogni
chiamata a Firebase può durare fino a 120 s (nessun `httpTimeout`, `bot/core/firebase_client.py:420-425`). Il demo non ha un battito suo.
Unico avvio: `python -m bot.main` (`main.py:13`, `:2662-2663`). Servizio (secondo `docs/hetzner_setup.md:117-118`, da confermare sulla
macchina): `Restart=always`, `RestartSec=10`: dopo un crash riparte con l'ultimo codice scaricato dal branch.

## 3. Paper, demo e conto vero

- `DRY_RUN` e `BINANCE_TESTNET` con `_get_bool_sicuro` (`config.py:78-90`, usati a `:105`, `:110`): **solo «false»** (maiuscole e spazi
  ignorati) li spegne; assente, vuoto, «si», «0», «no», errori di battitura → vero, con un avviso se il valore non è «true».
  `BACKTEST_PARITY` vero solo con «true» (`:713`). Sulla macchina il bot dichiarava `DRY_RUN: True` il 5 nov
  (`ops/results/0702-5nov-stato-entrate-demo-bis.md:17`).
- File delle tarature (scritto da `scripts/supervisor.py`): `carica_tuning` (`config.py:34-52`, chiamata a `:61`) applica tutto **tranne**
  `DRY_RUN`, `BINANCE_TESTNET`, `BACKTEST_PARITY` (`:30`) e i nomi con KEY, SECRET, TOKEN, PASSWORD, CREDENTIAL, FIREBASE (`:31`). È un
  elenco di chiavi vietate, non di ammesse: i limiti del vecchio bot restano regolabili da lì. Il supervisore scrive solo `GATE_*`.
- Avvio: `controlla_avvio` stampa `DRY_RUN`, `BINANCE_TESTNET`, `BACKTEST_PARITY`; **dal `5d5d26ad` rifiuta l'avvio con `DRY_RUN` falso**
  (`:795-800`; prima solo con la parità accesa, `:792-794`). Il rifiuto ferma anche il demo (stesso processo): Problema 35.
- Vecchio esecutore: sempre in prova; con `DRY_RUN` falso il bot non parte più.
- Demo: indipendente da `DRY_RUN` per scelta (`demo_binance.py:18-19`); indirizzo fisso `DEMO`/`HOST_DEMO` (`:64-65`), `_url` rifiuta ogni
  altro host (`:98-102`, test `tests/test_demo_binance.py:113`); chiavi `BINANCE_DEMO_API_KEY`, `BINANCE_DEMO_API_SECRET` o il file
  `BINANCE_DEMO_PRIVATE_KEY_PATH` (`:276-282`, `:419-424`); firma HMAC, Ed25519 o RSA (`:259-273`).
- Chiavi del conto vero: sulla macchina (backlog, voce del conto vero); nome non noto; **non limitate all'indirizzo della macchina**
  (risposta del proprietario del 7 nov, `docs/backlog.md`, `435c5594`); permesso di prelievo non detto. Nessun codice attivo le usa per
  ordini (vecchio ramo bloccato); `scripts/verify_keys.py` legge soltanto.

## 4. Limiti fissi (`bot/risk/hard_limits.py`, invariati il 7 nov su `5d5d26ad`)

| Invariante | Valore | Riga | Dove si applica |
|---|---|---|---|
| Leva massima | `MAX_LEVERAGE = 5.0` | `:16` | `safety_leverage_cap`; `risk_manager.py:77,83,93`; `:212-214` (ultimo cancello) |
| Rischio per operazione | `MAX_RISK_PER_TRADE = 0.03` | `:17` | `safety_risk_cap`; `risk_manager.py:79,94,215-217` |
| Perdita giornaliera massima | `DAILY_LOSS_LIMIT = 0.05` | `:20` | `circuit_breakers.py:79` (fermo del giorno), `:57-58` (messaggio) |
| Stop di fila prima della pausa | `CONSECUTIVE_SL_LIMIT = 6` | `:24` | `circuit_breakers.py:85` |
| Durata della pausa | `CONSECUTIVE_SL_PAUSE = 2 h` | `:25` | `circuit_breakers.py:86` (la nota a `:88` dice «4h»: testo sbagliato) |
| Rischio dimezzato in alta volatilità | `HIGH_VOL_SIGMA = 3.0`, `HIGH_VOL_SIZE_FACTOR = 0.5` | `:26-27` | `safety_risk_cap` `:53-57` |
| Finestra senza posizioni attorno agli eventi macro | `MACRO_FLAT_HOURS = 2.0` | `:28` | `circuit_breakers.py:92-101` |
| Leva ridotta con la volatilità | 3σ→2x, 2σ→3x, 1.5σ→4x | `:33-37` | `safety_leverage_cap` `:40-50` |

(Righe rilette il 7 nov su `5d5d26ad` con `sed -n 15,58p`: per le costanti una riga prima di quanto scritto nelle versioni precedenti.)
Valgono **solo per il vecchio bot** (`RiskManager`): nessun file di `bot/portafoglio/` importa `hard_limits`.

Da variabile d'ambiente (vecchio bot): numero massimo di posizioni `MAX_OPEN_POSITIONS` 5 (`config.py:217`, applicato a `main.py:1741`),
quota per posizione `MAX_POSITION_EQUITY_FRACTION` 1,0 (`:222`), stop massimo `MAX_STOP_PCT` 6% (`:748`), perdita per moneta al giorno
`RISK_PER_COIN_DAY` 1,5% (`:741`, `bot/risk/daily_cap.py`), rischio per direzione 3% (`:278`), correlazione 0,85 e 3 posizioni (`:263-264`).

**Test di guardia** (il loro fallimento è un allarme, non un test da correggere): `tests/test_risk.py:32` (leva 10 → 5, con
`MAX_LEVERAGE == 5.0`), `:41` (rischio 3%), `:75` (fermo a −6%), `:84` (nessun fermo a −2,1%), `:94` (pausa dopo 6 stop), `:103`
(ultimo cancello); `tests/test_sizing.py:104` (leva fra 1 e 5 con il moltiplicatore 1,3). Avvio: `tests/test_sicurezza_avvio.py`.

## 5. Interruttori del vecchio bot (`bot/risk/circuit_breakers.py`)

- Stato in RTDB `/risk_state`: caricato a `main.py:516`, salvato da `_persist_risk_state` (`main.py:2157-2158`).
- `register_trade_result` (`:72-90`) a ogni chiusura: `main.py:1523`, `:1549`. Un'eccezione lì esce da `trading_cycle` (presa a `main.py:2603-2607`).
- Entra nell'ultimo cancello: `risk_manager.py:220`.
- **`BACKTEST_PARITY=true`** (`config.py:713`): `blocking_reason` sempre `None` (`circuit_breakers.py:50-52`) e niente tetto delle
  posizioni (`main.py:1741`). L'avvio con `DRY_RUN` falso è rifiutato in ogni caso (`config.py:792-800`).

## 6. Parametri della dashboard (vecchio bot, invariati)

Catena: `dashboard/app/components/RiskControl.tsx:55,108` → Firestore `user_risk_settings/current` → `read_user_risk`
(`main.py:610-619`, prima di ogni trade) → `RiskSettings` (`bot/core/models.py:187-196`: nessun controllo, accetta `nan` e `inf`) →
`risk_manager.py:63-94`.

| Controllo | Dove | Comportamento |
|---|---|---|
| Dashboard | `dashboard/app/lib/hardLimits.ts:13-17` | taglia a 1-5x e 0,5-3% (comodità, non sicurezza) |
| Regole Firestore | `firebase/firestore.rules:32-41` | solo il proprietario, leva 1-5, rischio (0, 3%]; non chiude l'elenco dei campi; utente segnaposto (`:27`) |
| Bot | `main.py:616-619` | documento illeggibile → 2x e 1% in silenzio |
| Bot | `risk_manager.py:77-80`, `:212-217` | oltre il limite → tagliato con una nota, non rifiutato |
| Bot | `risk_manager.py:63-65`, `:230-237` | rischio `nan` → approvato con quantità `nan` (provato il 7 nov) |

Il bot usa l'Admin SDK: le regole non lo limitano (`firestore.rules:6-8`).

## 7. G1 sul conto demo (`bot/portafoglio/demo_binance.py`, codice di `5d5d26ad`)

**Costanti** (nel codice, fuori da `hard_limits.py`, nessun test tiene la leva): `LEVA = 5` (`:73`, inviata a `:759`), `STOP_CONTO = 0.35`
dal massimo (`:80`), `OGNI_CONTROLLO_STOP_S = 60` (`:77`, anche attesa dopo un errore delle protezioni), `TENTATIVI_PRIMA_DELL_ALLARME = 3`
(`:78`), `OGNI_VALUTAZIONE_S = 3600` (`:75`), `ATTESA_DOPO_ERRORE_S = 1800` (`:76`, solo per il ribilancio), `VALIDITA_LIMITE_S = 3600`
(`:74`), `SOGLIA_CONFRONTO = 0.02` (`:81`), `QUOTA_EVENTI = 0.05` (`:71`, eventi spenti sul demo).

**Ingressi**: decisione di G1 da `data/paper_g1.json` (`ultimo_lunedi`, `pesi`; `:511-515`), scritta da `PaperG1` alle 00:05 UTC su
giorni chiusi (`f5.py:597-615`, `:91-156`). **Nessun controllo** su età, somma, tetto per moneta o valori dei pesi. Capitale ridotto dal
file `ops/demo_binance_capitale` (`:93`, `capitale_voluto` `:332-340`: qualunque numero positivo; oggi `1000`), filtri del conto vero da
`filtri_conto_vero.json` (`:94`, copia fissa del 6 nov, `piu_severi` `:200-213`).

**Il giro `tick`** (`:479-535`), in ordine:
1. acceso? (`:480`); chiave (`:482-489`);
2. **attesa di un minuto dopo un errore delle protezioni** (`:492-493`, impostata a `:500`): in quel minuto non gira niente, pulsante compreso;
3. **protezioni** (`:494-503`, `protezioni` `:537-556`): stato locale (`carica` `:426-430`), conto ridotto (`:354-369`), **pulsante** RTDB
   `/commands/demo_binance_chiudi_tutto` (`:86`) o testo nuovo nel file `ops/demo_binance_chiudi_tutto` (`:90`, `_comando_file` `:450-461`)
   → `chiudi_tutto` (`:463-477`); **stop sul conto ogni minuto** (`:549-555`): massimo aggiornato ogni minuto, chiude a −35%; stato salvato
   (`:498`). Un errore: log, `/demo_binance/errore` con `dove: protezioni`, attesa di un minuto (`:499-503`);
4. **da fermo** (`_da_fermo` `:558-594`), poi il giro finisce (`:504-505`): «riparti» a file letto a ogni giro, **senza Firebase** (`:562`;
   il testo del file si segna come già visto solo all'entrata, `chiudi_tutto` `:471` → `_pulisci_riparti` `:619-634`); il «riparti» della
   dashboard solo dopo la pulizia su Firebase (`:563-564`) e con il falso scritto e confermato (`_riparti` `:636-648`); riparte con il
   massimo di adesso (`:568`) e `ultimo_giorno` a 0 (`:567`); altrimenti **ogni minuto** posizioni e ordini aperti riletti (`:575-577`;
   **la lettura degli ordini aperti a `:576` non è protetta: Problema 32**), chiusure e annulli anche senza posizioni (`:578-580`),
   allarme su `/demo_binance/allarme` dopo 3 tentativi (`:581-585`), `vuoto` segnato quando non restano né posizioni né ordini (`:587-590`);
5. **attesa di 30 minuti dopo un errore**, solo per il ribilancio (`:506-507`);
6. dopo un'ora gli ordini limite → `chiudi_ordini` (`:509-510`, `:785-853`): fase 1 per ordine (`:791-806`: lettura, annullo se aperto;
   **annullo rifiutato → rilettura, e se l'ordine è ancora aperto il giro si ferma senza segnarlo controllato** `:797-803`; `controllato` e
   salvataggio `:804-806`); **prima del mercato nessun ordine aperto sulle monete della lista** (`:811-814`, altrimenti il giro si ferma:
   Problema 33 se l'ordine non va via); fase 2: resto = obiettivo (`st["obiettivi"]`) − posizione vera, al passo verso zero e sopra i
   minimi (`:815-828`), identificativo `id_mercato(chiave, simbolo, giro)` (`:143-148`; chiave = data del giorno o `…-eventi-HHMM`;
   **giro = ora del ribilancio** `piazzati`, `:818`, uguale per tutti i tentativi dello stesso ribilancio; con la chiave degli eventi restano
   3 caratteri per il nome: Problema 34), lettura dell'identificativo prima dell'invio (`_ordine_esiste` `:650-659`: −2013 = non esiste,
   altri errori fermano), «solo riduzione» se riduce (`:832-836`), `mercato_fatto` e salvataggio dopo ogni moneta (`:842-843`);
7. decisione nuova → `parti_da_zero` se c'è un capitale in attesa (`:516-517`, `:371-409`; annullo ordini non protetto `:380-381`, un
   errore ferma il giro) e `ribilancia` (`:518`, `:723-783`); eventi (`:520-524`); il ribilancio parte solo senza ordini in corso (`:516`);
8. ogni ora `valuta` (`:525-526`, `:855-877`, ha ancora il suo stop `:861-862`), `controlla_margine` (`:676-698`), `confronta` (`:700-721`);
9. errore → `_ultimo_tentativo`, stampa, RTDB `/demo_binance/errore` (`:531-535`); lo stato del giro non si salva (salvo quello già
   salvato dalle protezioni e da `chiudi_ordini`).

**Ordini** (`ribilancia`): filtri da `exchangeInfo` (`:725`, `filtri` `:121-131`, valore minimo predefinito 5 se manca), prezzi mark
(`:728`); una posizione per moneta, controllata una volta (`:729-733`); ordini aperti annullati prima di contare le posizioni (`:734-739`);
`ordini_del_giorno` (`:151-170`): quantità al passo verso zero, sotto i minimi saltate, prezzo limite al passo, «solo riduzione» se riduce o
chiude; identificativo limite `id_ordine` nuovo a ogni tentativo (`:134-140`, `:751`); margine unico e leva 5 alla prima volta per moneta
(`:755-759`); un rifiuto non ferma gli altri (`:761-763`); obiettivi salvati (`:766-770`), chiave del ribilancio (`:771-773`).

**Chiusure** (`_chiudi_posizioni` `:596-617`, usata da `chiudi_tutto` e da `_da_fermo`): lettura degli ordini aperti (errore → si annulla
moneta per moneta sulle posizioni, `:599-603`), annullo per moneta con errori presi, chiusura a mercato «solo riduzione» della quantità
piena, un errore non ferma le altre monete.

**Errori**: `ClienteDemo.chiedi` (`:292-304`): `timeout=15`, finestra 5 s, ogni risposta ≥ 400 → `RuntimeError` con 200 caratteri (i
guasti di rete escono come eccezioni di `requests`, non `RuntimeError`); nessuna gestione di 429/418 né dell'attesa chiesta; nessuna
lettura dell'ora di Binance. Nessun avviso Telegram nel modulo.

**Conto ridotto**: valore = `totalMarginBalance` − scarto (`_conto` `:661-665`, scarto `:368`, `:404`); stop e rapporti usano questo valore.

## 8. Pulsanti che chiudono tutto

| Sistema | Comando | Senza Firebase | Ritardo massimo |
|---|---|---|---|
| Demo | RTDB `/commands/demo_binance_chiudi_tutto` (regola nel repo: solo vero/falso, `database.rules.json:18-21`; pubblicata? sezione 10) | no | un giro (30 s + vecchio ciclo); **un minuto in più dopo un errore delle protezioni** |
| Demo | file `ops/demo_binance_chiudi_tutto`, testo nuovo | sì (arriva con il `git pull` dell'agente ops, ogni minuto) | 1 min + un giro; un minuto in più dopo un errore delle protezioni |
| Demo | stop sul conto −35% dal massimo | sì | **1 minuto** + un giro, anche dopo un errore |
| Demo, da fermo | conto rimasto aperto, ordini rimasti | sì | richiuso ogni minuto, allarme al terzo tentativo; **non se la lettura degli ordini aperti fallisce (Problema 32)** |
| Vecchio bot | RTDB `/commands/kill_switch` e `/commands/bot_state`, `main.py:860-872`, `kill_switch.py:40-59` | **no** | valutato solo a `main.py:1585`, dopo tre uscite anticipate (`:1559`, `:1568`, `:1578`); chiude solo posizioni di prova (ramo reale bloccato) |

Con `DRY_RUN` falso il bot non parte: nessun pulsante del demo funziona (Problema 35).
Esecuzione del vecchio pulsante: `_emergency_close` (`main.py:1265-1290`) → `force_close_all` (`executor.py:1100-1109`) → `_close`.

## 9. Vecchio ramo reale (`bot/execution/executor.py`): **bloccato dal `9f47972c`**

`_init_binance` (`:244-254`) non crea il client e rimette `dry_run` vero; test `tests/test_sicurezza_avvio.py:49`; docstring aggiornata
(`:11-15`). Il codice qui sotto resta, raggiungibile solo dai test con un client finto (`tests/test_live_orders.py`, `tests/test_execution.py`);
difetti noti, da non riusare (righe +1 rispetto al `9f47972c`):
- Ingresso: leva per moneta (`:620`), ordine LIMIT GTC con `round(..., 6)` (`:621-624`), `_await_fill` (`:664-682`), sotto la quota
  minima annulla e chiude il resto (`:638-644`, `:692-702`).
- Protezioni: `STOP_MARKET` «solo riduzione» sull'ultimo prezzo (`:718-726`), obiettivi `TAKE_PROFIT_MARKET` (`:728-743`); un rifiuto si
  stampa e basta. Stop spostato con annulla-e-rimetti (`_sync_exchange_stop` `:745-777`).
- Chiusure: a mercato «solo riduzione» sulla quantità interna (`:1050-1068`); la posizione esce dallo stato anche se la chiusura fallisce
  (`:1092`). Margine mai impostato. Nessun identificativo d'ordine.
- `bot/execution/error_handler.py`: non usato da nessun file.
- Riconciliatore (`reconciler.py`, filo suo ogni 60 s, `config.py:663-664`): `_exchange_state` (`main.py:1201-1226`) conta stop e obiettivi
  insieme; senza client restituisce «irraggiungibile» (`:1204-1206`). Azioni in `_apply_reconciliation` (`main.py:1228-1253`).

## 10. Firebase

- `set_rtdb` non solleva mai, restituisce vero o falso e aggiorna **sempre** lo specchio in memoria (`firebase_client.py:652-679`);
  `get_rtdb` su errore restituisce lo specchio (`:681-702`). Il demo guarda il valore restituito solo per il «riparti» della dashboard
  (`demo_binance.py:632`, `:643`).
- Regole nel repo: `firebase/firestore.rules` (solo `user_risk_settings` scrivibile, `:32-41`), `firebase/database.rules.json` (solo
  `kill_switch`, `close_position`, `demo_binance_chiudi_tutto`, `demo_binance_riparti`, `close_position_meta` scrivibili), con l'utente
  `REPLACE_WITH_YOUR_FIREBASE_UID`. **Il proprietario non le ha mai pubblicate** (risposta del 7 nov, `docs/backlog.md`, `435c5594`):
  quali regole valgono si vede solo nella console; se il database accetta scritture da chiunque, chiunque comanda il demo.

## 11. Il canale `ops/`

- `scripts/ops_agent.py` ogni minuto (timer systemd): `git pull` (avanti veloce, altrimenti rebase con annullo, `:271-303`), esegue le
  richieste contro la lista bianca della macchina (non nel repo), senza shell, con oscuramento dei segreti (`:53-75`), battito in
  `ops/heartbeat.md`. La macchina segue `claude/brave-albattani-1b12fv`: **ciò che si spinge lì è già sulla macchina** ed entra in funzione
  al riavvio del bot, anche dopo un crash (`Restart=always`, sezione 2). Il 7 nov `5d5d26ad` era sul remoto prima del verdetto.
- File letti dal demo nel repo: `ops/demo_binance_acceso`, `ops/demo_binance_capitale` (`1000`), `ops/demo_binance_chiudi_tutto` e
  `ops/demo_binance_riparti` (oggi assenti), `ops/demo_binance_eventi_acceso` (assente). Chi può scrivere sul branch comanda il demo.
- Orologio: `systemd-timesyncd` attivo negli elenchi dei processi (`ops/results/0196-processi.md`, `0413-1ott-processi-col-gate.md`).

## 12. Test del percorso

`tests/test_demo_binance.py` (34 test; il Binance finto ha posizioni che seguono gli ordini, guasti a richiesta una volta sola, e dal
`5d5d26ad` **toglie dagli aperti un ordine annullato** `:106-109` e non mostra i limite eseguiti `:77`, `:87`), `tests/test_sicurezza_avvio.py`,
`tests/test_g1_poco_capitale.py`, `tests/test_demo_contro_paper.py`, `tests/test_paper_f5.py`, `tests/test_risk.py`, `tests/test_sizing.py`,
`tests/test_kill_switch_levels.py`, `tests/test_reconciler.py`, `tests/test_live_orders.py`, `tests/test_execution.py`. Suite intera al 7 nov
su `5d5d26ad`: `2566 passed` in 146 s. Coperti dal `5d5d26ad`: annullo rifiutato (`:696`), secondo ribilancio dello stesso giorno (`:711`),
ordini da fermo senza posizioni (`:729`), «riparti» a file senza Firebase (`:744`). Non coperti: attesa di un minuto (28), lettura degli
ordini aperti che fallisce da fermo (32), ordine aperto che non va via (33), identificativi degli eventi (34).

## 13. Punti noti aperti (dettaglio nei rapporti del 7 nov)

Demo: **lettura degli ordini aperti da fermo non protetta (32, Medio, regressione)**; ordine aperto che non va via blocca il demo senza
allarme (33); identificativi degli eventi troppo corti (34); con `DRY_RUN` falso non parte neanche il demo (35); attese crescenti e 429/418
(13, con il resto del 28); pesi senza controllo (10); nessun avviso (11); decisione di G1 senza età massima (12); stesso filo del vecchio bot
(14); massimo dello stop solo in locale (15); capitale senza tetto (16); bassi 21-23. Vecchio bot (in prova): parametri della dashboard
(17), chiusura di una moneta che chiude tutto (18), limiti in variabili d'ambiente (20), nota sbagliata (24). Fuori dal codice: chiavi vere
non limitate all'indirizzo, prelievo non detto; regole di Firebase mai pubblicate; servizio che riparte da solo con l'ultimo codice spinto.
Chiusi il 7 nov: 2-9 (6-8 per blocco del ramo reale), 1 (con il 25), 25, 26, 27, 29, 30, 31; 28 in parte (resto nel 13).

## Storia degli invarianti

- 7 nov 2026: nessun invariante cambiato nel codice. Una modifica proposta (leva massima 10, perdita giornaliera dalla dashboard) ha
  avuto REQUEST CHANGES: `reviews/reports/2026-11-07-limiti-leva-perdita-giornaliera.md`.
- 7 nov 2026, primo avvio: mappati per la prima volta gli invarianti del demo (leva 5, stop −35% ogni ora, pulsanti, margine unico,
  una posizione per moneta, capitale ridotto 1000). Nessuno cambiato.
- 7 nov 2026, `9f47972c` (REQUEST CHANGES per il Problema 25): stop sul conto da ogni ora a ogni minuto; pulsante e stop anche dopo un
  errore; da fermo chiusure ritentate ogni minuto con allarme; «riparti» solo con comando pulito e consumato; resti a mercato dalla
  posizione vera con identificativo fisso; `DRY_RUN` e rete di prova spenti solo da «false»; tarature senza modo, parità e segreti; avvio
  rifiutato con parità e `DRY_RUN` falso; vecchio ramo reale bloccato. Limiti fissi invariati.
- 7 nov 2026, `5d5d26ad` (REQUEST CHANGES per il Problema 32): annullo rifiutato con ordine aperto → giro fermo, e niente mercato con
  ordini aperti sulle monete della lista; identificativo dei resti uno per ribilancio; «riparti» a file senza Firebase; un minuto di attesa
  dopo un errore delle protezioni (anche per il pulsante); da fermo si annullano anche gli ordini senza posizioni; avvio rifiutato con
  `DRY_RUN` falso in ogni caso. Limiti fissi invariati.
