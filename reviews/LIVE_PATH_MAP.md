# Mappa del percorso degli ordini

Prima versione: 7 nov 2026 (`b29f5713`), completata col primo avvio (`reviews/reports/2026-11-07-primo-avvio.md`). **Riscritta l'8 nov
2026 sul codice committato `1a8522f`** (fase 1 del conto vero, approvata al quarto giro, in funzione dal riavvio delle 19:02 UTC).
I numeri di riga di `demo_binance.py` nelle sezioni 7-8 valgono per `1a8522f` (nel `ff89531` il file è cresciuto: `_da_fermo` è a
`:974`, `protezioni` a `:951`). **12 nov 2026**: la fase 2 è committata come `ff89531` (verificato uguale alle copie riviste), il bot
sulla macchina non l'ha ancora caricata (riavvio con l'ok di Alessio); le modifiche non committate del 12 nov (versione approvata su
Firebase) sono nella sezione 14.

## 1. Chi manda ordini (grep del 7 nov; ricontrollato l'8 nov sulla fase 2: nessun altro client firmato, python-binance solo in `scripts/verify_keys.py`)

| Parte | Dove | Verso dove | Acceso da |
|---|---|---|---|
| G1 sul conto demo | `bot/portafoglio/demo_binance.py` (`DemoG1`, `ClienteDemo`) | solo `demo-fapi.binance.com` | file `ops/demo_binance_acceso` + chiavi `BINANCE_DEMO_*` |
| G1 sul conto vero (**fase 2, `ff89531`, spento**) | `bot/portafoglio/conto_vero.py` (`ContoVeroG1`, `ClienteVero`) | solo `fapi.binance.com` | interruttore + `DRY_RUN` falso + codice approvato (tag; dal 12 nov, non committato: Firebase) + capitale + chiavi (sezione 14) |
| Vecchio esecutore, ramo reale | `bot/execution/executor.py` | **nessuno: bloccato dal `9f47972c`** | `_init_binance` non crea il client e rimette `dry_run` vero (`executor.py:244-254`) |

Solo lettura, nessun ordine: i paper `bot/portafoglio/f5.py` (F5, G1, G11, G1N) e `eventi.py` (dati pubblici da `fapi.binance.com`,
`f5.py:47`, `:163-168`), `scripts/verify_keys.py` (legge il conto, `:33-38`). `bot/risk/portafoglio.py` è una simulazione.

## 2. Il giro del bot (un solo filo)

`main()` (`bot/main.py:2656-2659`): prima `controlla_avvio` (`config.py:787-800`), poi `TradingBot.run` (`main.py:2514`), un giro ogni 30
secondi. In ordine: vecchio bot (scansione, `trading_cycle`), battito `/bot_status/heartbeat`, poi ognuno nel suo `try`: paper F5, G1,
G11, G1N, **demo `:2643`** (fase 2: il conto vero subito dopo), paper degli eventi. Il demo aspetta la fine del vecchio ciclo e degli
scaricamenti dei paper (alla mezzanotte minuti); ogni chiamata a Firebase può durare fino a 120 s (nessun `httpTimeout`,
`bot/core/firebase_client.py:420-425`). Unico avvio: `python -m bot.main`. Servizio (secondo `docs/hetzner_setup.md:117-118`):
`Restart=always`, `RestartSec=10`: dopo un crash riparte con l'ultimo codice scaricato dal branch.

## 3. Paper, demo e conto vero

- `DRY_RUN` e `BINANCE_TESTNET` con `_get_bool_sicuro` (`config.py:78-90`, usati a `:105`, `:110`): **solo «false»** li spegne;
  assente, vuoto, errori di battitura → vero, con un avviso (`:88-89`). `BACKTEST_PARITY` vero solo con «true». Sulla macchina il bot
  dichiarava `DRY_RUN: True` il 5 nov (`ops/results/0702-5nov-stato-entrate-demo-bis.md:17`).
- Tarature (`carica_tuning`, `config.py:34-52`): tutto **tranne** `DRY_RUN`, `BINANCE_TESTNET`, `BACKTEST_PARITY` (`:30`) e i nomi con
  KEY, SECRET, TOKEN, PASSWORD, CREDENTIAL, FIREBASE (`:31`). Elenco di vietate, non di ammesse.
- Avvio: in `1a8522f` (in funzione) `controlla_avvio` **rifiuta l'avvio con `DRY_RUN` falso** (problema 29; ferma anche il demo: 35).
  Da `ff89531` (`config.py:791-813`) con `DRY_RUN` falso il bot parte sempre (senza interruttore il conto vero fa solo le protezioni),
  salvo `BACKTEST_PARITY` vero: 35 chiuso al riavvio che carica `ff89531`.
- Con `DRY_RUN` falso nel vecchio sistema (verificato l'8 nov): esecutore sempre in prova (`executor.py:244-254`); riconciliatore acceso
  (`reconciler.py:230-239`, `main.py:2515`) ma senza client «irraggiungibile» (`main.py:1204-1205`) → solo `exchange_down`/`wait`, nessuna azione
  (`reconciler.py:93-100`, `main.py:1235-1255`); Telegram «🔴 LIVE» sulle operazioni del vecchio paper (`main.py:1442`, `:1488`, `:1548`,
  `:1976`); paper esplorativo spento (`adaptation.py:427`); `ops/gate_fermo` ferma solo la ricerca del gate, non il vecchio giro.
- Demo: indipendente da `DRY_RUN` per scelta; indirizzo fisso `DEMO`/`HOST_DEMO` (`demo_binance.py:64-65`), `_url` rifiuta ogni altro
  host (`:116-120`); chiavi `BINANCE_DEMO_API_KEY`, `BINANCE_DEMO_API_SECRET` o il file `BINANCE_DEMO_PRIVATE_KEY_PATH` (`:390-397`,
  `:655-660`); firma HMAC, Ed25519 o RSA (`:373-388`).
- Chiavi del conto vero: `BINANCE_API_KEY`, `BINANCE_API_SECRET` (`config.py:108-109`, nell'ambiente del processo con `load_dotenv`);
  **non limitate all'indirizzo della macchina** (proprietario, 7 nov); prelievo non detto. Nel codice committato nessuno le usa per ordini.

## 4. Limiti fissi (`bot/risk/hard_limits.py`, invariati l'8 nov; righe corrette di uno rispetto alle versioni prima)

| Invariante | Valore | Riga | Dove si applica |
|---|---|---|---|
| Leva massima | `MAX_LEVERAGE = 5.0` | `:17` | `safety_leverage_cap`; `risk_manager.py:77,83,93`; `:212-214` (ultimo cancello) |
| Rischio per operazione | `MAX_RISK_PER_TRADE = 0.03` | `:18` | `safety_risk_cap`; `risk_manager.py:79,94,215-217` |
| Perdita giornaliera massima | `DAILY_LOSS_LIMIT = 0.05` | `:21` | `circuit_breakers.py:79` (fermo del giorno), `:57-58` (messaggio) |
| Stop di fila prima della pausa | `CONSECUTIVE_SL_LIMIT = 6` | `:25` | `circuit_breakers.py:85` |
| Durata della pausa | `CONSECUTIVE_SL_PAUSE = 2 h` | `:26` | `circuit_breakers.py:86` (la nota a `:88` dice «4h»: testo sbagliato) |
| Rischio dimezzato in alta volatilità | `HIGH_VOL_SIGMA = 3.0`, `HIGH_VOL_SIZE_FACTOR = 0.5` | `:27-28` | `safety_risk_cap` |
| Finestra senza posizioni attorno agli eventi macro | `MACRO_FLAT_HOURS = 2.0` | `:29` | `circuit_breakers.py:92-101` |
| Leva ridotta con la volatilità | 3σ→2x, 2σ→3x, 1.5σ→4x | `:33-37` | `safety_leverage_cap` |

Valgono **solo per il vecchio bot** (`RiskManager`): nessun file di `bot/portafoglio/` importa `hard_limits`.
Da variabile d'ambiente (vecchio bot): `MAX_OPEN_POSITIONS` 5 (`config.py:217`), `MAX_POSITION_EQUITY_FRACTION` 1,0, `MAX_STOP_PCT` 6%,
`RISK_PER_COIN_DAY` 1,5%, rischio per direzione 3%, correlazione 0,85 e 3 posizioni.
**Test di guardia** (il loro fallimento è un allarme): `tests/test_risk.py:32`, `:41`, `:75`, `:84`, `:94`, `:103`; `tests/test_sizing.py:104`;
demo `tests/test_demo_binance.py:1520`; conto vero (fase 2) `tests/test_conto_vero.py:67`. Avvio: `tests/test_sicurezza_avvio.py`.

## 5. Interruttori del vecchio bot (`bot/risk/circuit_breakers.py`)

- Stato in RTDB `/risk_state`, caricato a `main.py:516`, salvato da `_persist_risk_state`. `register_trade_result` (`:72-90`) a ogni
  chiusura; entra nell'ultimo cancello (`risk_manager.py:220`).
- **`BACKTEST_PARITY=true`**: `blocking_reason` sempre `None` (`circuit_breakers.py:50-52`) e niente tetto delle posizioni. Con `DRY_RUN`
  falso l'avvio è rifiutato in ogni caso (`config.py:792-800`).

## 6. Parametri della dashboard (vecchio bot, invariati)

Catena: `RiskControl.tsx:55,108` → Firestore `user_risk_settings/current` → `read_user_risk` (`main.py:610-619`) → `RiskSettings`
(`bot/core/models.py:187-196`: nessun controllo, accetta `nan` e `inf`) → `risk_manager.py:63-94`. Dashboard `hardLimits.ts:13-17` taglia
a 1-5x e 0,5-3% (comodità); regole `firestore.rules:32-41` (leva 1-5, rischio (0, 3%], utente segnaposto `:27`); bot: documento
illeggibile → 2x e 1% in silenzio; oltre il limite → tagliato, non rifiutato; rischio `nan` → approvato con quantità `nan` (7 nov).
Il bot usa l'Admin SDK: le regole non lo limitano.

## 7. G1 sul conto demo (`bot/portafoglio/demo_binance.py`, codice di `1a8522f`)

**Costanti** (`:71-99`, fissate da `tests/test_demo_binance.py:1520`): `LEVA = 5` (`:73`), `STOP_CONTO = 0.35` (`:80`), `PAVIMENTO_RIPARTI =
0.65` (`:95`), `SOMMA_PESI_MASSIMA = 2.5`, `PESO_MASSIMO_MONETA = 0.60` (`:84-85`), `ETA_MASSIMA_DECISIONE_S = 26 h` (`:86`),
`CAPITALE_MASSIMO = 10.000` (`:92`), filtri del conto vero del `2026-11-06` con allarme dopo 30 giorni (`:93-94`), 429/418 con 3
ritentativi 1-2-4 s (`:87-91`), tetto di 600 s per il 429, il 418 rispettato per intero (`:97`), chiusure in 20 pezzi al massimo (`:99`),
`OGNI_CONTROLLO_STOP_S = 60`, `ATTESA_DOPO_ERRORE_S = 1800` (`:76-77`).

**Ingressi**: decisione di G1 da `data/paper_g1.json` (scritta da `PaperG1` alle 00:05 UTC; universo senza `ESCLUSI` di
`research/programma6/esclusi.py`, `f5.py:41`, `:201`); pesi controllati (`pesi_fuori_dai_limiti` `:130-156`, vuoti rifiutati) ed età e
data nel futuro (`_decisione_da_non_eseguire` `:872-889`). Capitale ridotto dal file `ops/demo_binance_capitale` (`capitale_voluto`
`:521-542`, fino a 10.000 e non oltre il valore vero `conto_ridotto` `:572-593`, `parti_da_zero` `:598-645`); oggi `1000`.

**Il giro `tick`** (`:763-846`): acceso e chiave; allarmi già scritti letti all'avvio; **attesa dopo un errore delle protezioni o un
limite di Binance** (`:784`); **protezioni** (`:786-797`: `carica` `:662-666`, `conto_ridotto`, `protezioni` `:903-924`, salvataggio;
`LimiteBinance` → `_limite_di_binance` `:848-870`, nessuna richiesta per l'attesa chiesta, allarme `allarmi/limiti_binance`); da fermo il
giro finisce; **30 minuti dopo un errore** solo per il ribilancio (`:803`); poi resto a mercato dopo l'ora (`chiudi_ordini` `:807`),
giorno nel futuro azzerato, decisione nuova → `parti_da_zero` + `ribilancia` (`:820-826`), eventi; ogni ora `valuta` (`:834`,
`:1386-1408`), `controlla_margine` (`:1164-1205`), `confronta` (`:1207-1228`); errore → `_ultimo_tentativo` e `/demo_binance/errore`.

**Protezioni** (`protezioni` `:903-924`): pulsante RTDB `/commands/demo_binance_chiudi_tutto` (`:104`, `:906`) o testo nuovo nel file
`ops/demo_binance_chiudi_tutto` (`:108`, `_comando_file` `:717-728`) → `chiudi_tutto` (`:730-761`: fermo scritto e salvato **prima**
delle chiusure, un errore segna il tentativo e risale); **stop sul conto ogni minuto** (`:918-923`): massimo nel file e in
`/demo_binance/massimo` (`_fissa_massimo` `:679-687`, `_unisci_massimo` `:689-707`), livello = max(65% del massimo, 65% del capitale
della fase; 0 solo con un capitale in attesa a conto vuoto) (`livello_di_stop` `:228-233`, `_pavimento` `:219-226`).
**Da fermo** (`_da_fermo` `:926-996`): «riparti» a file senza Firebase o dalla dashboard con il falso confermato; ammesso solo a conto
vuoto e sopra il pavimento (`_riparti_ammesso` `:1006-1032`; un errore di lettura rimanda il comando); poi il conto resta vuoto fino
alla decisione di G1 dopo (`riparti_attende_g1`, `_giorno_g1` `:1079-1085`). Altrimenti ogni minuto posizioni e ordini riletti
(lettura degli ordini in errore o guasto di rete = «non si sa», si richiude e si annulla anche sulle monete dell'ultimo ribilancio,
`:956-964`), chiusure (`_chiudi_posizioni` `:1034-1061`, in pezzi `_chiudi_moneta` `:1070-1077`), allarme `/demo_binance/allarme` dopo 3
tentativi (`:998-1004`), `vuoto` solo con lettura riuscita e niente aperto.

**Ordini** (`ribilancia` `:1230-1304`): filtri da `exchangeInfo` (`filtri` `:174-186`, valore minimo obbligatorio), resi severi come la
copia del conto vero (`piu_severi` `:314-328`), quantità massime (`filtri_mercato` `:188-202`), prezzi mark; una posizione per moneta
(`:1246-1248`); ordini aperti annullati prima di contare le posizioni; `ordini_del_giorno` (`:265-285`) al passo verso zero, «solo
riduzione» se riduce; LIMIT GTC con `id_ordine` nuovo a ogni tentativo (`:1271-1272`); margine unico e leva alla prima volta per moneta
(`_margine_unico` `:1155-1162`); un rifiuto non ferma gli altri. **Resti** (`chiudi_ordini` `:1306-1384`): annullo rifiutato con ordine
ancora aperto → `_ordini_bloccati` (`:1118-1133`, allarme dopo 2 ore) e giro fermo; niente mercato con ordini aperti sulle monete della
lista; resto = obiettivo − posizione vera, `id_mercato` fisso (`:257-262`) controllato con `_ordine_esiste` (`:1135-1144`).

**Errori**: `ClienteDemo.chiedi` (`:446-487`): `timeout=15`, finestra 5 s, 429/418 ritentati e poi `LimiteBinance`, -1021 con l'ora di
Binance riletta una volta (`:470`), errori senza firma (`senza_firma` `:123-127`). Nessun avviso sul telefono nel modulo.
**Conto ridotto**: valore = `totalMarginBalance` − scarto (`_conto` `:1146-1153`). Chi legge i rami del demo: dashboard `PaperBot.tsx`
(fermo, confronto, stato, allarmi per tipo), fotografia `scripts/state_snapshot.py`.

## 8. Pulsanti che chiudono tutto

| Sistema | Comando | Senza Firebase | Ritardo massimo |
|---|---|---|---|
| Demo | RTDB `/commands/demo_binance_chiudi_tutto` (regola nel repo `database.rules.json:18-21`; pubblicata? sezione 10) | no | un giro (30 s + vecchio ciclo); un minuto dopo un errore delle protezioni; **tutto il blocco con un 418** |
| Demo | file `ops/demo_binance_chiudi_tutto`, testo nuovo | sì (con il `git pull` dell'agente, ogni minuto) | 1 min + un giro; come sopra |
| Demo | stop sul conto −35% dal massimo o sotto il 65% del capitale della fase | sì | 1 minuto + un giro; come sopra |
| Demo, da fermo | conto rimasto aperto, ordini rimasti | sì | richiuso ogni minuto, allarme al terzo tentativo, anche con la lettura degli ordini in errore |
| Conto vero (fase 2) | RTDB `/commands/conto_vero_chiudi_tutto`, file `ops/conto_vero_chiudi_tutto`, stop | file sì | come il demo; anche spento, se acceso una volta e non vuoto (53); pulsante in dashboard e regola nel repository dal 12 nov (non committati; regole non pubblicate) |
| Vecchio bot | RTDB `/commands/kill_switch` e `/commands/bot_state` (`kill_switch.py:40-59`) | **no** | valutato dopo tre uscite anticipate del giro; chiude solo posizioni di prova |

Con `DRY_RUN` falso il bot committato non parte: nessun pulsante del demo funziona (Problema 35).

## 9. Vecchio ramo reale (`bot/execution/executor.py`): **bloccato dal `9f47972c`**

`_init_binance` (`:244-254`) non crea il client e rimette `dry_run` vero; test `tests/test_sicurezza_avvio.py`. Il codice sotto resta,
raggiungibile solo dai test con un client finto; difetti noti, da non riusare: leva per moneta e LIMIT GTC con `round(..., 6)`
(`:620-624`), protezioni `STOP_MARKET` sull'ultimo prezzo (`:718-726`), chiusure sulla quantità interna (`:1050-1068`), margine mai
impostato, nessun identificativo d'ordine. Tutte le chiamate passano da `self.dry_run`/`self._client` (`:620-761`, `:1036-1070`).
`bot/execution/error_handler.py` non usato. Riconciliatore (`reconciler.py`, filo suo ogni 60 s): senza client «irraggiungibile».

## 10. Firebase

- `set_rtdb` non solleva mai, restituisce vero o falso e aggiorna sempre lo specchio in memoria (`firebase_client.py:652-679`);
  `get_rtdb` su errore restituisce lo specchio (`:681-702`). Il demo guarda il valore restituito solo per il «riparti».
- Regole nel repo: `firebase/firestore.rules` (solo `user_risk_settings` scrivibile), `firebase/database.rules.json` (`kill_switch`,
  `close_position`, i due comandi del demo, `close_position_meta`; dal 12 nov, non committati, i quattro del conto vero e `/azioni`),
  utenti segnaposto. **Pubblicate** (foto di Alessio, 12 nov, `docs/conto_vero.md:85-90`): chiuse e con il suo identificativo, ma senza
  i blocchi del demo e del conto vero (i loro pulsanti in dashboard sono rifiutati).
- **La chiave di amministratore ignora le regole**: ce l'hanno il bot, `scripts/ops_agent.py:349-353` (riletto dal branch ogni minuto)
  e i flussi di GitHub `connectivity.yml:24`, `monitoring.yml:24`, `learning.yml:25`, `snapshot.yml:33,43` (anche a ogni push).

## 11. Il canale `ops/`

- `scripts/ops_agent.py` ogni minuto: `git fetch origin <branch>` e avanti veloce (`:473-477`; altrimenti rebase con annullo,
  `:271-303`), richieste contro la lista bianca della macchina, oscuramento dei segreti, battito in `ops/heartbeat.md`. Committato: non
  scarica i tag (provato l'8 nov, git 2.43: 55); `ff89531` porta il tag del conto vero forzato, il cambio del 12 nov lo toglie. Lo script
  si rilegge a ogni giro: un suo cambio vale dal primo `git pull`, senza riavvio, e può fare qualunque cosa sulla macchina. La macchina segue
  `claude/brave-albattani-1b12fv`: ciò che si spinge lì entra in funzione al riavvio, anche dopo un crash.
- File letti dal demo nel repo: `ops/demo_binance_acceso`, `ops/demo_binance_capitale` (`1000`), `ops/demo_binance_chiudi_tutto` e
  `ops/demo_binance_riparti` (assenti), `ops/demo_binance_eventi_acceso` (assente). Chi può scrivere sul branch comanda il demo.
- Stato del demo e del conto vero in `data/` (non tracciato e non ignorato). Orologio: `systemd-timesyncd` attivo.

## 12. Test del percorso

`tests/test_demo_binance.py` (81 test al `1a8522f`; Binance finto `_Demo`, guasti una volta sola, `HOST` dalla fase 2),
`tests/test_conto_vero.py` (fase 2, secondo giro: 790 righe), `tests/test_sicurezza_avvio.py`, `tests/test_g1_poco_capitale.py`,
`tests/test_demo_contro_paper.py`, `tests/test_paper_f5.py`, `tests/test_risk.py`, `tests/test_sizing.py`,
`tests/test_kill_switch_levels.py`, `tests/test_reconciler.py`, `tests/test_live_orders.py`, `tests/test_execution.py`,
`tests/test_strategie_restano_accese.py`. Suite intera l'8 nov con la fase 2 (secondo giro): `2681 passed, 1 failed` in 192 s (il fallito è il test
della firma: libreria `cryptography` del contenitore rotta; passa con `PYTHONPATH=<cartella di lavoro>/cripto`).

## 13. Punti noti aperti

Demo (`1a8522f`): Bassi 51 («riparti» controllato prima della richiusura) e 52 (tentativi che non crescono con un «riparti» in attesa);
dal primo avvio 11 (nessun avviso), 14 (stesso filo del vecchio bot), 17-20 e 24 (vecchio bot), 34 (identificativi degli eventi), 35
(`DRY_RUN` falso ferma anche il demo; chiuso al riavvio con `ff89531`). Fuori dal codice: chiavi vere non limitate all'indirizzo,
prelievo non detto; regole pubblicate senza i comandi del demo e del conto vero; servizio che riparte da solo con l'ultimo codice
spinto. Conto vero: 54 ii Alto, 70 e 74 Medi, 75-77 Bassi (sezione 14).
Chiusi: 1-9, 12, 15, 21, 25-27, 29-33, 36-50; 10, 13, 16, 22 in parte; 23 come chiesto; 28 nel 13.

## 14. Il conto vero: fase 2 committata (`ff89531`) e modifiche non committate del 12 nov 2026

Rapporti della fase 2: `reports/2026-11-08-fase2-conto-vero*.md`. Del 12 nov: `reports/2026-11-12-conto-vero-versione-firebase.md`.
Righe del working tree del 12 nov (`conto_vero.py` 913 righe).
- Indirizzo solo `https://fapi.binance.com` (`_url` `:126-131`); chiavi `BINANCE_API_KEY`/`SECRET` lette solo da acceso (`:397-402`);
  stato `data/conto_vero.json`, ramo `/conto_vero`; pulsante `/commands/conto_vero_chiudi_tutto` o file `ops/conto_vero_chiudi_tutto`.
- **Limiti** (`:108-123`, test `tests/test_conto_vero.py:161-194`): leva 5, capitale 300, valore 600, stop 35%, pavimento 65%, pesi 200%,
  peso per moneta 60%, età 26 h; tolleranza del saldo 0,5% (almeno 1) in 3 letture; redditi fino a 60 s fa con 15 minuti riletti.
- **Spento** (senza interruttore o con `DRY_RUN` vero, `motivo_spento` `:390-395`): mai acceso o già vuoto → nessuna richiesta né chiave
  (`_protezioni_da_spento` `:476-491`); acceso una volta e non vuoto → protezioni con soli ordini «solo riduzione».
- **Codice approvato, dal 12 nov (non committato)**: all'avvio HEAD, data e titolo (`commit_in_esecuzione` `:168-179`) e file caricati
  uguali a HEAD, nessuno cambiato dopo l'avvio (`:346-351`), altrimenti blocco fino al riavvio; ogni minuto, anche da spento
  (`_controlla_versione` `:438-448`), il commit di `/commands/conto_vero_versione_approvata` letto **davvero** da Firebase
  (`leggi_rtdb_davvero`, `firebase_client.py:704-721`; `_letto_davvero` `:182-193`; seconda lettura subito `:427-430`) deve essere
  uguale al commit in memoria e ai file di adesso (`codice_approvato` `:222-287`). Firebase muto = non approvato; allarme
  `versione_approvata` dopo 3 controlli. `/conto_vero/versione` per la dashboard (`:457-474`). In `ff89531`: il tag forzato.
  **Chi scrive l'approvazione**: Alessio dalla dashboard, ma anche la chiave di amministratore (sezione 10): 54 ii aperto.
- **Condizioni degli ordini** (`motivo_niente_ordini` `:728-773`): codice, Firebase che ha risposto sullo stato dell'accensione (66),
  capitale nel file fino a 300 e non oltre il saldo, saldo non sotto il valore, valore fino a 600, conto vuoto alla prima accensione.
  Con un motivo (`_ordini_nuovi_ammessi` `:787-815`): `blocco`, freno del cliente, ordini limite annullati allo scadere senza resto;
  alla fine del blocco si riparte dalla decisione di G1 dopo. **Un buco di Firebase vale come un blocco: 74.**
- **«Riparti», dal 12 nov**: solo dalla dashboard, richiesta `/commands/conto_vero_riparti` vera e conferma
  `/commands/conto_vero_riparti_conferma` uguale all'ora del fermo in secondi interi (`codice_riparti` `:211-219`, `_riparti_confermato`
  `:666-678`); pulite all'entrata nel fermo (`:691-701`), la conferma tolta dopo l'uso (`:680-689`); nessun file (`:656-659`, `:316`).
  In `ff89531`: solo dal file `ops/conto_vero_riparti`.
- **Stato perso** → fermo, chiusure, «riparti» nuovo (`_stato_perso` `:546-571`). Stop spento prima della prima accensione (`:637-642`):
  70 aperto.
- Creazione protetta (`crea_conto_vero` `:891-913`, allarme `/conto_vero/allarmi/creazione`), giro subito dopo il demo
  (`main.py:2655-2661`).
- Dashboard (non committata): `ComandiContoVero.tsx` (approva `:132-154`, chiudi tutto `:205-223`, riparti in due passi `:170-204`;
  disattivati da spento), dati da `lib/strategie.ts:259-268`.
- Problemi aperti: 54 (ii) Alto; 70, 74 Medi; 75, 76, 77 Bassi. Chiusi: 53, 55, 57, 59, 60 (nel codice), 61-68, 71-73; 56, 58, 69 come scelto.

## Storia degli invarianti

- 7 nov 2026: nessun invariante cambiato; la proposta di leva 10 e perdita giornaliera dalla dashboard ha avuto REQUEST CHANGES.
- 7 nov, primo avvio: mappati gli invarianti del demo (leva 5, stop −35%, pulsanti, margine unico, una posizione per moneta, capitale 1000).
- 7 nov, `9f47972c`: stop ogni minuto; pulsante e stop anche dopo un errore; chiusure da fermo ritentate; «riparti» solo pulito e
  consumato; resti dalla posizione vera con identificativo fisso; `DRY_RUN` spento solo da «false»; tarature senza modo, parità e
  segreti; vecchio ramo reale bloccato.
- 7 nov, `5d5d26ad`: annullo rifiutato → giro fermo; niente mercato con ordini aperti; «riparti» a file; avvio rifiutato con `DRY_RUN`
  falso in ogni caso.
- 7 nov, `013f9426` (APPROVE): lettura degli ordini in errore da fermo non ferma le chiusure; allarme degli ordini bloccati.
- 8 nov, fase 1 (quattro giri, APPROVE al quarto; **committata come `1a8522f`**, riavvio delle 19:02 UTC con l'ok del proprietario):
  limiti nuovi del demo come costanti con test; 429/418 con attese; massimo dello stop anche su Firebase; stop anche al 65% del capitale
  della fase; fermo salvato prima delle chiusure; «riparti» a conto vuoto, sopra il pavimento e con la riapertura alla decisione di G1
  dopo; capitale non oltre il saldo; chiusure in 20 pezzi; -1021 con l'ora di Binance. Limiti fissi invariati.
- 8 nov, fase 2 non committata (REQUEST CHANGES): **invariante cambiato**, con `DRY_RUN` falso il bot parte se c'è l'interruttore del
  conto vero; nuovi: G1 sul conto vero con quattro condizioni, freno del cliente, limiti propri con test. Limiti fissi invariati.
- 8 nov, fase 2 secondo giro (REQUEST CHANGES): con `DRY_RUN` vero ordini «solo riduzione» al conto vero se acceso una volta e non
  vuoto; con `DRY_RUN` falso il bot parte sempre; codice approvato su tutti i file caricati; valore = capitale + redditi; «riparti»
  del conto vero solo da file; demo: stato salvato dopo `parti_da_zero`. Limiti fissi invariati.
- 8 nov, fase 2 terzo giro (APPROVE per il commit spento): stop spento prima della prima accensione; blocco per prelievo con
  tolleranza e tre letture; redditi con ritardo e sovrapposizione. Limiti fissi invariati.
- 12 nov (non committato; APPROVE per il commit spento, REQUEST CHANGES per l'accensione): codice approvato dal tag a un commit su
  Firebase scritto dalla dashboard, letto davvero ogni minuto (Firebase muto = non approvato), valido senza riavvio; «riparti» del
  conto vero solo dalla dashboard in due passi, nessun file; l'agente non porta più il tag. Limiti fissi invariati.
