# Mappa del percorso degli ordini

Prima versione: 7 nov 2026 (`b29f5713`); completata col primo avvio (`reviews/reports/2026-11-07-primo-avvio.md`, codice di `782a01fc`).
**Aggiornata il 7 nov 2026 sul commit `9f47972c`** (correzioni dei 9 problemi Alti, `reviews/reports/2026-11-07-correzioni-9-problemi.md`):
i numeri di riga di `bot/portafoglio/demo_binance.py`, `bot/config.py` e `bot/execution/executor.py` valgono per `9f47972c`; `bot/main.py`
è cambiato solo in coda (`:2657-2658`), quindi i suoi numeri restano quelli di prima. Al prossimo cambio si ricontrollano.

## 1. Chi manda ordini (verificato con grep il 7 nov su `9f47972c`)

| Parte | Dove | Verso dove | Acceso da |
|---|---|---|---|
| G1 sul conto demo | `bot/portafoglio/demo_binance.py` (`DemoG1`, `ClienteDemo`) | solo `demo-fapi.binance.com` | file `ops/demo_binance_acceso` + chiavi `BINANCE_DEMO_*` |
| Vecchio esecutore, ramo reale | `bot/execution/executor.py` | **nessuno: bloccato dal `9f47972c`** | `_init_binance` non crea il client e rimette `dry_run` vero (`executor.py:243-253`) |

Solo lettura, nessun ordine: i paper `bot/portafoglio/f5.py` (F5, G1, G11, G1N) e `eventi.py` (dati pubblici da `fapi.binance.com`,
`f5.py:47`), `scripts/verify_keys.py` (legge il conto con python-binance, `:33-38`). `bot/risk/portafoglio.py` è una simulazione.

## 2. Il giro del bot (un solo filo)

`main()` (`bot/main.py:2656-2659`): prima `controlla_avvio` (`config.py:787-794`), poi `TradingBot.run` (`main.py:2514`), un giro ogni 30
secondi (`sleep_s`, `:2653`). In ordine: vecchio bot (scansione `:2589`, `trading_cycle` `:2590`), battito `/bot_status/heartbeat` (`:2623`),
poi ognuno nel suo `try`: paper F5 e G1 (`:2627-2641`), **demo `:2643`**, paper degli eventi. Il demo aspetta la fine del vecchio ciclo; ogni
chiamata a Firebase può durare fino a 120 s (nessun `httpTimeout`, `bot/core/firebase_client.py:420-425`). Il demo non ha un battito suo.
Unico avvio: `python -m bot.main` (`main.py:13`, `:2662-2663`).

## 3. Paper, demo e conto vero

- `DRY_RUN` e `BINANCE_TESTNET` con `_get_bool_sicuro` (`config.py:78-90`, usati a `:105`, `:110`): **solo «false»** (maiuscole e spazi
  ignorati) li spegne; assente, vuoto, «si», «0», «no», errori di battitura → vero, con un avviso se il valore non è «true».
  `BACKTEST_PARITY` vero solo con «true» (`:713`).
- File delle tarature (scritto da `scripts/supervisor.py`): `carica_tuning` (`config.py:34-52`, chiamata a `:61`) applica tutto **tranne**
  `DRY_RUN`, `BINANCE_TESTNET`, `BACKTEST_PARITY` (`:30`) e i nomi con KEY, SECRET, TOKEN, PASSWORD, CREDENTIAL, FIREBASE (`:31`). È un
  elenco di chiavi vietate, non di ammesse: i limiti del vecchio bot restano regolabili da lì. Il supervisore scrive solo `GATE_*`.
- Avvio: `controlla_avvio` stampa `DRY_RUN`, `BINANCE_TESTNET`, `BACKTEST_PARITY` e **rifiuta l'avvio con `DRY_RUN` falso e parità accesa**.
- Vecchio esecutore: sempre in prova. Con `DRY_RUN` falso: esecutore in prova, riconciliatore acceso (`reconciler.py:232`) che vede Binance
  «irraggiungibile» e aspetta (`main.py:1204-1206`, `reconciler.py:93-100`), dashboard con `dry_run` falso (`main.py:957`).
- Demo: indipendente da `DRY_RUN` per scelta (`demo_binance.py:18-19`); indirizzo fisso `DEMO`/`HOST_DEMO` (`:64-65`), `_url` rifiuta ogni
  altro host (`:98-102`, test `tests/test_demo_binance.py:108-116`); chiavi `BINANCE_DEMO_API_KEY`, `BINANCE_DEMO_API_SECRET` o il file
  `BINANCE_DEMO_PRIVATE_KEY_PATH` (`:275-281`, `:417-422`); firma HMAC, Ed25519 o RSA (`:258-272`).
- Chiavi del conto vero: sulla macchina (backlog, voce del conto vero, aggiunta del 6 nov); nome non noto; **non limitate all'indirizzo
  della macchina** (risposta del proprietario del 7 nov, `docs/backlog.md`, commit `435c5594`); permesso di prelievo non detto. Nessun
  codice attivo le usa per ordini (vecchio ramo bloccato); `scripts/verify_keys.py` legge soltanto.

## 4. Limiti fissi (`bot/risk/hard_limits.py`, invariati il 7 nov su `9f47972c`)

| Invariante | Valore | Riga | Dove si applica |
|---|---|---|---|
| Leva massima | `MAX_LEVERAGE = 5.0` | `:17` | `safety_leverage_cap` `:46`; `risk_manager.py:77,83,93`; `:212-214` (ultimo cancello) |
| Rischio per operazione | `MAX_RISK_PER_TRADE = 0.03` | `:18` | `safety_risk_cap` `:53-57`; `risk_manager.py:79,94,215-217` |
| Perdita giornaliera massima | `DAILY_LOSS_LIMIT = 0.05` | `:21` | `circuit_breakers.py:79` (fermo del giorno), `:57-58` (messaggio) |
| Stop di fila prima della pausa | `CONSECUTIVE_SL_LIMIT = 6` | `:25` | `circuit_breakers.py:85` |
| Durata della pausa | `CONSECUTIVE_SL_PAUSE = 2 h` | `:26` | `circuit_breakers.py:86` (la nota a `:88` dice «4h»: testo sbagliato) |
| Rischio dimezzato in alta volatilità | `HIGH_VOL_SIGMA = 3.0`, `HIGH_VOL_SIZE_FACTOR = 0.5` | `:27-28` | `safety_risk_cap` |
| Finestra senza posizioni attorno agli eventi macro | `MACRO_FLAT_HOURS = 2.0` | `:29` | `circuit_breakers.py:92-101` |
| Leva ridotta con la volatilità | 3σ→2x, 2σ→3x, 1.5σ→4x | `:33-37` | `safety_leverage_cap` `:40-50` |

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
  posizioni (`main.py:1741`). Dal `9f47972c` l'avvio con `DRY_RUN` falso e parità accesa è rifiutato (`config.py:792-794`).

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

## 7. G1 sul conto demo (`bot/portafoglio/demo_binance.py`, codice di `9f47972c`)

**Costanti** (nel codice, fuori da `hard_limits.py`, nessun test tiene la leva): `LEVA = 5` (`:73`, inviata a `:751`), `STOP_CONTO = 0.35`
dal massimo (`:80`), **`OGNI_CONTROLLO_STOP_S = 60`** (`:77`), **`TENTATIVI_PRIMA_DELL_ALLARME = 3`** (`:78`), `OGNI_VALUTAZIONE_S = 3600`
(`:75`), `ATTESA_DOPO_ERRORE_S = 1800` (`:76`, ora solo per il ribilancio), `VALIDITA_LIMITE_S = 3600` (`:74`), `SOGLIA_CONFRONTO = 0.02`
(`:81`), `QUOTA_EVENTI = 0.05` (`:71`, eventi spenti sul demo).

**Ingressi**: decisione di G1 da `data/paper_g1.json` (`ultimo_lunedi`, `pesi`; `:506-510`), scritta da `PaperG1` alle 00:05 UTC su
giorni chiusi (`f5.py:597-615`, `:91-156`). **Nessun controllo** su età, somma, tetto per moneta o valori dei pesi. Capitale ridotto dal
file `ops/demo_binance_capitale` (`:93`, `capitale_voluto` `:330-338`: qualunque numero positivo; oggi `1000`), filtri del conto vero da
`filtri_conto_vero.json` (`:94`, copia fissa del 6 nov, `piu_severi` `:199-212`).

**Il giro `tick`** (`:477-529`), in ordine:
1. acceso? (`:478`); chiave (`:480-487`);
2. **protezioni, a ogni giro e anche dopo un errore** (`:490-498`, `protezioni` `:532-551`): stato locale (`carica` `:424-428`), conto
   ridotto (`:352-367`), **pulsante** RTDB `/commands/demo_binance_chiudi_tutto` (`:86`) o testo nuovo nel file `ops/demo_binance_chiudi_tutto`
   (`:90`, `_comando_file` `:448-459`) → `chiudi_tutto` (`:461-474`); **stop sul conto ogni minuto** (`:544-550`): massimo aggiornato ogni
   minuto, chiude a −35%; stato salvato (`:494`). Un errore qui: log, `/demo_binance/errore` con `dove: protezioni`, riprova al giro dopo,
   nessuna attesa (`:495-498`);
3. **da fermo** (`_da_fermo` `:553-587`), poi il giro finisce (`:499-500`): «riparti» solo dopo la pulizia del comando vecchio
   (`riparti_pulito`, `_pulisci_riparti` `:612-625`, chiamata anche in `chiudi_tutto` `:469`) e con il comando consumato davvero
   (`_riparti` `:627-640`: file con testo nuovo, oppure RTDB `/commands/demo_binance_riparti` `:87` con il falso scritto e confermato);
   riparte con il massimo di adesso (`:562`) e `ultimo_giorno` a 0 (`:561`); altrimenti **ogni minuto** posizioni rilette e richiuse
   (`:566-579`), allarme su `/demo_binance/allarme` dopo 3 tentativi (`:574-578`), `vuoto` segnato quando il conto è vuoto (`:580-583`);
4. **attesa di 30 minuti dopo un errore**, solo per il ribilancio (`:501-502`);
5. dopo un'ora gli ordini limite → `chiudi_ordini` (`:504-505`, `:777-836`): fase 1 per ordine (lettura, annullo se aperto, **annullo
   rifiutato solo stampato** `:788-791`, `controllato` e salvataggio `:792-794`); fase 2: resto = obiettivo (`st["obiettivi"]`) − posizione
   vera, al passo verso zero e sopra i minimi (`:799-812`), identificativo fisso `id_mercato(chiave, simbolo)` (`:143-147`, chiave = data
   del giorno o `…-eventi-HHMM`), lettura dell'identificativo prima dell'invio (`_ordine_esiste` `:642-651`: −2013 = non esiste, altri errori
   fermano), «solo riduzione» se riduce (`:815-819`), `mercato_fatto` e salvataggio dopo ogni moneta (`:825-826`);
6. decisione nuova → `parti_da_zero` se c'è un capitale in attesa (`:369-407`; annullo ordini non protetto `:378-379`) e `ribilancia`
   (`:715-775`); eventi (`:515-519`);
7. ogni ora `valuta` (`:838-860`, ha ancora il suo stop `:844-845`), `controlla_margine` (`:668-690`), `confronta` (`:692-713`);
8. errore → `_ultimo_tentativo`, stampa, RTDB `/demo_binance/errore` (`:526-529`); lo stato del giro non si salva (salvo quello già
   salvato dalle protezioni e da `chiudi_ordini`).

**Ordini** (`ribilancia`): filtri da `exchangeInfo` (`:717`, `filtri` `:121-131`, valore minimo predefinito 5 se manca `:128`), prezzi mark
(`:720`); una posizione per moneta, controllata una volta (`:721-725`); ordini aperti annullati prima di contare le posizioni (`:727-731`);
`ordini_del_giorno` (`:150-169`): quantità al passo verso zero, sotto i minimi saltate, prezzo limite al passo, «solo riduzione» se riduce o
chiude (`:167`); identificativo limite `id_ordine` nuovo a ogni tentativo (`:134-140`, `:743`); margine unico e leva 5 alla prima volta per
moneta (`:747-752`); un rifiuto non ferma gli altri (`:754-756`); obiettivi salvati (`:758-762`), chiave del ribilancio (`:764`).

**Chiusure** (`_chiudi_posizioni` `:589-610`, usata da `chiudi_tutto` e da `_da_fermo`): lettura degli ordini aperti (errore → si annulla
moneta per moneta sulle posizioni), annullo per moneta con errori presi, chiusura a mercato «solo riduzione» della quantità piena, un errore
non ferma le altre monete.

**Errori**: `ClienteDemo.chiedi` (`:291-302`): `timeout=15`, finestra 5 s, ogni risposta ≥ 400 → `RuntimeError` con 200 caratteri; nessuna
gestione di 429/418 né dell'attesa chiesta; nessuna lettura dell'ora di Binance. Nessun avviso Telegram nel modulo.

**Conto ridotto**: valore = `totalMarginBalance` − scarto (`_conto` `:653-657`, scarto `:366`, `:402`); stop e rapporti usano questo valore.

## 8. Pulsanti che chiudono tutto

| Sistema | Comando | Senza Firebase | Ritardo massimo |
|---|---|---|---|
| Demo | RTDB `/commands/demo_binance_chiudi_tutto` (regola nel repo: solo vero/falso, `database.rules.json:18-21`; pubblicata? vedi sezione 10) | no | un giro (30 s + vecchio ciclo), anche dopo un errore |
| Demo | file `ops/demo_binance_chiudi_tutto`, testo nuovo | sì (arriva con il `git pull` dell'agente ops, ogni minuto) | 1 min + un giro, anche dopo un errore |
| Demo | stop sul conto −35% dal massimo | sì | **1 minuto** + un giro, anche dopo un errore |
| Demo, da fermo | conto rimasto aperto | sì | richiuso ogni minuto, allarme al terzo tentativo |
| Vecchio bot | RTDB `/commands/kill_switch` e `/commands/bot_state`, `main.py:860-872`, `kill_switch.py:40-59` | **no** | valutato solo a `main.py:1585`, dopo tre uscite anticipate (`:1559`, `:1568`, `:1578`); dal `9f47972c` chiude solo posizioni di prova (ramo reale bloccato) |

Esecuzione del vecchio pulsante: `_emergency_close` (`main.py:1265-1290`) → `force_close_all` (`executor.py:1099-1108`) → `_close`.

## 9. Vecchio ramo reale (`bot/execution/executor.py`): **bloccato dal `9f47972c`**

`_init_binance` (`:243-253`) non crea il client e rimette `dry_run` vero; test `tests/test_sicurezza_avvio.py:49`. Il codice qui sotto resta,
raggiungibile solo dai test con un client finto (`tests/test_live_orders.py`, `tests/test_execution.py`); difetti noti, da non riusare:
- Ingresso: leva per moneta (`:619`), ordine LIMIT GTC con `round(..., 6)` (`:620-623`), `_await_fill` (`:663-681`), sotto la quota
  minima annulla e chiude il resto (`:637-643`, `:691-701`).
- Protezioni: `STOP_MARKET` «solo riduzione» sull'ultimo prezzo (`:717-725`), obiettivi `TAKE_PROFIT_MARKET` (`:727-742`); un rifiuto si
  stampa e basta. Stop spostato con annulla-e-rimetti (`_sync_exchange_stop` `:744-776`).
- Chiusure: a mercato «solo riduzione» sulla quantità interna (`:1049-1067`); la posizione esce dallo stato anche se la chiusura fallisce
  (`:1091`). Margine mai impostato. Nessun identificativo d'ordine.
- `bot/execution/error_handler.py`: non usato da nessun file.
- Riconciliatore (`reconciler.py`, filo suo ogni 60 s, `config.py:663-664`): `_exchange_state` (`main.py:1201-1226`) conta stop e obiettivi
  insieme; senza client restituisce «irraggiungibile» (`:1204-1206`). Azioni in `_apply_reconciliation` (`main.py:1228-1253`).

## 10. Firebase

- `set_rtdb` non solleva mai, restituisce vero o falso e aggiorna **sempre** lo specchio in memoria (`firebase_client.py:652-679`);
  `get_rtdb` su errore restituisce lo specchio (`:681-702`). Il demo guarda il valore restituito solo per il «riparti» (`demo_binance.py:623`, `:635`).
- Regole nel repo: `firebase/firestore.rules` (solo `user_risk_settings` scrivibile, `:32-41`), `firebase/database.rules.json` (solo
  `kill_switch`, `close_position`, `demo_binance_chiudi_tutto`, `demo_binance_riparti`, `close_position_meta` scrivibili), con l'utente
  `REPLACE_WITH_YOUR_FIREBASE_UID`. **Il proprietario non le ha mai pubblicate** (risposta del 7 nov, `docs/backlog.md`, `435c5594`):
  quali regole valgono si vede solo nella console; se il database accetta scritture da chiunque, chiunque comanda il demo.

## 11. Il canale `ops/`

- `scripts/ops_agent.py` ogni minuto (timer systemd): `git pull` (avanti veloce, altrimenti rebase con annullo, `:271-303`), esegue le
  richieste contro la lista bianca della macchina (non nel repo), senza shell, con oscuramento dei segreti (`:53-75`), battito in
  `ops/heartbeat.md`. La macchina segue `claude/brave-albattani-1b12fv`: **ciò che si spinge lì è già sulla macchina**; entra in funzione
  al riavvio del bot (il 7 nov `9f47972c` era spinto prima del verdetto; riavvii automatici da confermare).
- File letti dal demo nel repo: `ops/demo_binance_acceso`, `ops/demo_binance_capitale` (`1000`), `ops/demo_binance_chiudi_tutto` e
  `ops/demo_binance_riparti` (oggi assenti), `ops/demo_binance_eventi_acceso` (assente). Chi può scrivere sul branch comanda il demo.
- Orologio: `systemd-timesyncd` attivo negli elenchi dei processi (`ops/results/0196-processi.md`, `0413-1ott-processi-col-gate.md`).

## 12. Test del percorso

`tests/test_demo_binance.py` (30 test; dal 7 nov il Binance finto ha posizioni che seguono gli ordini e guasti a richiesta; **non toglie
dagli aperti un ordine annullato con `DELETE /fapi/v1/order`**), `tests/test_sicurezza_avvio.py` (12), `tests/test_g1_poco_capitale.py`,
`tests/test_demo_contro_paper.py`, `tests/test_paper_f5.py`, `tests/test_risk.py`, `tests/test_sizing.py`, `tests/test_kill_switch_levels.py`,
`tests/test_reconciler.py`, `tests/test_live_orders.py`, `tests/test_execution.py`. Suite intera al 7 nov su `9f47972c`: `2562 passed`.
Non coperti: guasti h (annullo rifiutato), i (secondo ribilancio nello stesso giorno), d2 («riparti» a file senza conferma di Firebase).

## 13. Punti noti aperti (dettaglio nei rapporti del 7 nov)

Demo: **annullo rifiutato → ordine limite vivo più mercato, posizione doppia (25, Alto)**; secondo ribilancio dello stesso giorno senza resti
(26); «riparti» a file legato a Firebase (27); protezioni senza attese crescenti (28); da fermo ordini aperti non riannullati (31); pesi
senza controllo (10); nessun avviso (11); decisione di G1 senza età massima (12); 429/418 (13); stesso filo del vecchio bot (14); massimo
dello stop solo in locale (15); capitale senza tetto (16); bassi 21-23. Vecchio bot (in prova): parametri della dashboard (17), chiusura di
una moneta che chiude tutto (18), limiti in variabili d'ambiente (20), nota sbagliata (24), stato incoerente con `DRY_RUN` falso (29),
documentazione ferma (30). Fuori dal codice: chiavi vere non limitate all'indirizzo, prelievo non detto; regole di Firebase mai pubblicate.
Chiusi il 7 nov: 2, 3, 4, 5, 9 (corretti), 6, 7, 8 (ramo reale bloccato), 1 in parte (resta il 25).

## Storia degli invarianti

- 7 nov 2026: nessun invariante cambiato nel codice. Una modifica proposta (leva massima 10, perdita giornaliera dalla dashboard) ha
  avuto REQUEST CHANGES: `reviews/reports/2026-11-07-limiti-leva-perdita-giornaliera.md`.
- 7 nov 2026, primo avvio: mappati per la prima volta gli invarianti del demo (leva 5, stop −35% ogni ora, pulsanti, margine unico,
  una posizione per moneta, capitale ridotto 1000). Nessuno cambiato.
- 7 nov 2026, `9f47972c` (REQUEST CHANGES per il Problema 25): stop sul conto **da ogni ora a ogni minuto** (massimo aggiornato ogni
  minuto), pulsante e stop anche dopo un errore; da fermo chiusure ritentate ogni minuto con allarme; «riparti» solo con comando pulito e
  consumato; resti a mercato dalla posizione vera con identificativo fisso; `DRY_RUN` e rete di prova spenti solo da «false»; tarature
  senza modo, parità e segreti; avvio rifiutato con parità e `DRY_RUN` falso; vecchio ramo reale bloccato. Limiti fissi invariati.
