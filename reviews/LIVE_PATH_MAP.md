# Mappa del percorso degli ordini

Prima versione: 7 nov 2026 (`b29f5713`, primo avvio, `reports/2026-11-07-primo-avvio.md`). **Riscritta l'8 nov sul `1a8522f`** (fase 1
del conto vero, quarto giro, in funzione dal riavvio delle 19:02 UTC); righe di `demo_binance.py` delle sezioni 7-8 di `1a8522f` (nel
`ff89531` `_da_fermo` `:974`, `protezioni` `:951`). Fase 2 `ff89531` (contenuta in `16c5712`, in funzione); approvazione su Firebase: sezione 14.

## 1. Chi manda ordini (grep del 7 nov; ricontrollato l'8 nov sulla fase 2: nessun altro client firmato, python-binance solo in `scripts/verify_keys.py`)

| Parte | Dove | Verso dove | Acceso da |
|---|---|---|---|
| G1 sul conto demo | `bot/portafoglio/demo_binance.py` (`DemoG1`, `ClienteDemo`) | solo `demo-fapi.binance.com` | file `ops/demo_binance_acceso` + chiavi `BINANCE_DEMO_*` |
| Conto vero (**spento**; F5 dal 25 nov, `03ee29e`; dal 28 nov, `34989ea` e `b9959ac`: **di nuovo G1**, sezione 14) | `bot/portafoglio/conto_vero.py` (`ContoVeroG1`, `ClienteVero`) | solo `fapi.binance.com` | interruttore + `DRY_RUN` falso + codice approvato (tag; dal 12 nov, non committato: Firebase) + saldo USDT leggibile (dal 28 nov) + chiavi (sezione 14) |
| Vecchio esecutore, ramo reale | `bot/execution/executor.py` | **nessuno: bloccato dal `9f47972c`** | `_init_binance` non crea il client e rimette `dry_run` vero (`executor.py:244-254`) |

Solo lettura, nessun ordine: i paper `bot/portafoglio/f5.py` (F5, G1, G11, G1N) e `eventi.py` (dati pubblici da `fapi.binance.com`,
`f5.py:47`, `:163-168`), `scripts/verify_keys.py` (legge il conto, `:33-38`), dal 12 nov (`3566bd4`) la fotografia
dello stato (`scripts/state_snapshot.py:844-874` `SoloLettura`: solo GET su `userTrades`, `commissionRate`, `income`, `positionRisk` e
`time` del conto demo, con la chiave del demo, con la richiesta «stato»; finestra vietata 23:50-01:45 UTC `:830`, stop al primo 429/418
`:862-869`, soglia del peso usato 600 `:822`, tetto 1.000 per sezione `:821`; righe del 17 nov); dal 14 nov (`96c6094`) `positionRisk`
(`:817-818`, `sezione_pesi_g1_oggi`) e un solo cliente per le sezioni (`:120-126`); dal 17 nov (`d5c6708`, APPROVE) una terza sezione,
`sezione_funding_demo_paper` (`:1194-1289`), che rilegge `income` FUNDING_FEE dei 3 giorni con lo stesso cliente (`:232`). **27 nov (non committato)**: anche `GET fapi.binance.com/fapi/v1/markPriceKlines` pubblico, senza chiave,
al massimo 12 per stato, fuori dalle 23:50-01:45, stop al primo 429/418 (`state_snapshot.py:1020-1051`). `bot/risk/portafoglio.py` è una simulazione.

## 2. Il giro del bot (un solo filo)

`main()` (`bot/main.py:2656-2659`): prima `controlla_avvio` (`config.py:787-800`), poi `TradingBot.run` (`main.py:2514`), un giro ogni 30
secondi. In ordine: vecchio bot (scansione, `trading_cycle`), battito `/bot_status/heartbeat`, poi ognuno nel suo `try`: paper F5, G1,
G11, G1N, demo, conto vero, eventi. Dal 27 nov (`16c5712`): F5, conto vero, G1, demo, G11, G1N, eventi; **28 nov (`34989ea`)**: F5,
G1, conto vero, demo, G11, G1N, eventi (`main.py:2739-2766`); vecchio bot saltato con `ops/gate_fermo` e niente aperto nel vecchio paper (`:2560-2608`). Il demo aspetta degli
scaricamenti dei paper (alla mezzanotte minuti); ogni chiamata a Firebase può durare fino a 120 s (nessun `httpTimeout`,
`bot/core/firebase_client.py:420-425`). Unico avvio: `python -m bot.main`. Servizio (secondo `docs/hetzner_setup.md:117-118`):
`Restart=always`, `RestartSec=10`: dopo un crash riparte con l'ultimo codice scaricato dal branch.

## 3. Paper, demo e conto vero

- `DRY_RUN` e `BINANCE_TESTNET` con `_get_bool_sicuro` (`config.py:78-90`, usati a `:105`, `:110`): **solo «false»** li spegne;
  assente, vuoto, errori di battitura → vero, con un avviso (`:88-89`). `BACKTEST_PARITY` vero solo con «true». `/bot_status/dry_run`
  (stato, dashboard): dal riavvio col codice del 27 nov a ogni avvio e ogni ora col vecchio fermo (`main.py:1101-1104`, `:2603`).
- Tarature (`carica_tuning`, `config.py:34-52`): tutto **tranne** `DRY_RUN`, `BINANCE_TESTNET`, `BACKTEST_PARITY` (`:30`) e i nomi con
  KEY, SECRET, TOKEN, PASSWORD, CREDENTIAL, FIREBASE (`:31`). Elenco di vietate, non di ammesse.
- Avvio (`controlla_avvio`, `config.py:791-813`, da `ff89531`, in funzione con `16c5712`): con `DRY_RUN` falso il bot parte sempre (senza
  interruttore il conto vero fa solo le protezioni), salvo `BACKTEST_PARITY` vero (rifiutato); fino a `1a8522f` lo rifiutava (29; 35 chiuso).
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
**27 nov (non committato)**: aperture e aumenti saltati sulle monete «non disponibili sul demo» (stato ≠ TRADING, o -1121/-4140 negli ultimi
7 giorni; chiusure e riduzioni partono (sulle monete non disponibili), `demo_binance.py:1608`; conto vero mai); allarme `ordini_rifiutati`; `/demo_binance/ore`; telefono.
Telefono: per tipo, uno all'ora; **28 nov (`34989ea`)**: `telefono` solo a invio riuscito, segnato dal giro (`demo_binance.py:790-869`),
fermo e stop sempre (`:156`), 429 oltre 30 minuti una volta (`:1281-1311`); monitor per tipo, 429 dopo 30 minuti (`monitor.py:135-224`).
**28 nov, minimi (demo e conto vero)**: sotto il valore minimo parte «solo riduzione» solo la **chiusura intera** (`ordine_saltato` `:347-355`,
`:382`, `:407`, resto `:2053`; riduzioni saltate, 269 chiuso, 3cac1aeb); inversione su moneta in sola riduzione → solo la chiusura (`:1813-1860`).
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
- **La chiave di amministratore ignora le regole**: ce l'hanno il bot, `scripts/ops_agent.py:419-423` (27 nov; riletto dal branch ogni minuto)
  e i flussi di GitHub `connectivity.yml:24`, `monitoring.yml:24`, `learning.yml:25`, `snapshot.yml:33,43` (anche a ogni push).

## 11. Il canale `ops/`
- `scripts/ops_agent.py` ogni minuto: `git fetch origin <branch>` e avanti veloce (`:543-547`, 27 nov; altrimenti rebase con annullo,
  `:341-373`), richieste contro la lista bianca della macchina, oscuramento dei segreti (27 nov: anche chiavi intere, `:50-146`), battito in `ops/heartbeat.md`. Committato: non
  scarica i tag (provato l'8 nov, git 2.43: 55); `ff89531` porta il tag del conto vero forzato, il cambio del 12 nov lo toglie. Lo script
  si rilegge a ogni giro: un suo cambio vale dal primo `git pull`, senza riavvio, e può fare qualunque cosa sulla macchina. La macchina segue
  `claude/brave-albattani-1b12fv`: ciò che si spinge lì entra in funzione al riavvio, anche dopo un crash.
- File letti dal demo nel repo: `ops/demo_binance_acceso`, `ops/demo_binance_capitale` (`1000`), `ops/demo_binance_chiudi_tutto` e
  `ops/demo_binance_riparti` (assenti), `ops/demo_binance_eventi_acceso` (assente). Chi può scrivere sul branch comanda il demo.
- Stato del demo e del conto vero in `data/` (non tracciato e non ignorato). Orologio: `systemd-timesyncd` attivo.

## 12. Test del percorso
`tests/test_demo_binance.py` (81 test al `1a8522f`; Binance finto `_Demo`, guasti una volta sola, `HOST` dalla fase 2), `tests/test_conto_vero.py`
(fase 2, secondo giro: 790 righe), `tests/test_sicurezza_avvio.py`, `tests/test_g1_poco_capitale.py`, `tests/test_demo_contro_paper.py`,
`tests/test_paper_f5.py`, `tests/test_risk.py`, `tests/test_sizing.py`, `tests/test_kill_switch_levels.py`, `tests/test_reconciler.py`,
`tests/test_live_orders.py`, `tests/test_execution.py`, `tests/test_strategie_restano_accese.py`; trader AI `trader_ai/tests/` (sezione 15).
Suite intera il 28 nov (conto vero su G1, `34989ea`): `3131 passed` in 175 s; nuovo `tests/test_conto_vero_g1.py` (32).

## 13. Punti noti aperti
Demo (`1a8522f`): Bassi 51 («riparti» controllato prima della richiusura) e 52 (tentativi che non crescono con un «riparti» in attesa);
dal primo avvio 11 (nessun avviso), 14 (stesso filo del vecchio bot), 17-20 e 24 (vecchio bot), 34 (identificativi degli eventi), 35
(`DRY_RUN` falso ferma anche il demo; chiuso al riavvio con `ff89531`). Fuori dal codice: chiavi vere non limitate all'indirizzo,
prelievo non detto; regole pubblicate senza i comandi del demo e del conto vero; servizio che riparte da solo con l'ultimo codice
spinto. Conto vero: 54 ii Alto, 70, 268-270 Medi, 78, 271-273 Bassi (sezione 14). Paper: 83 Basso latente. Fotografia dello stato:
89 chiuso (`96c6094`); 17 nov (`d5c6708`, APPROVE; 90-92 corretti dalla sessione principale) Bassi 90-94 (testi e conteggi della sezione del funding, letture doppie, test). 27 nov: 203-207, 218 chiusi (riavvio del 27); bot: 217, 221 Bassi aperti (211, 213, 219, 220 corretti il 28, non committati).
Chiusi: 1-9, 12, 15, 21, 25-27, 29-33, 36-50; 10, 13, 16, 22 in parte; 23 come chiesto; 28 nel 13.

## 14. Il conto vero: fase 2 (`ff89531`), versione approvata su Firebase (`a267c40`), secondo giro del 12 nov non committato
Rapporti: `reports/2026-11-08-fase2-conto-vero*.md`, `reports/2026-11-12-conto-vero-versione-firebase.md` (committato come `a267c40`),
`-2.md` (secondo giro). Righe del primo giro (`a267c40`); il secondo giro sposta di circa +30 righe da `:90` in poi.
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
  **Secondo giro (non committato)**: con Firebase muto vale il commit dell'ultima lettura vera fino a 10 minuti, sempre con git; una
  lettura vera senza approvazione (revoca) vale subito, una revoca non letta fino a 10 minuti (`_verifica_versione` `:441-466`); da
  spento controllo ogni 10 minuti, all'accensione subito; fermo riscritto finché arriva; «non ancora letta» prima del primo controllo.
  **Chi scrive l'approvazione**: Alessio dalla dashboard, ma anche la chiave di amministratore (sezione 10): 54 ii aperto.
- **Condizioni degli ordini** (`motivo_niente_ordini` `:728-773`): codice, Firebase che ha risposto sullo stato dell'accensione (66),
  capitale nel file fino a 300 e non oltre il saldo (dal 28 nov: saldo USDT, sotto), saldo non sotto il valore, valore fino a 600, conto vuoto alla prima accensione.
  Con un motivo (`_ordini_nuovi_ammessi` `:787-815`): `blocco`, freno del cliente, ordini limite annullati allo scadere senza resto;
  alla fine del blocco si riparte dalla decisione di G1 dopo. Un buco di Firebase valeva come un blocco (74, chiuso nel secondo giro).
- **«Riparti», dal 12 nov**: solo dalla dashboard, richiesta `/commands/conto_vero_riparti` vera e conferma
  `/commands/conto_vero_riparti_conferma` uguale all'ora del fermo in secondi interi (`codice_riparti` `:211-219`, `_riparti_confermato`
  `:666-678`); pulite all'entrata nel fermo (`:691-701`), la conferma tolta dopo l'uso (`:680-689`); nessun file (`:656-659`, `:316`).
  In `ff89531`: solo dal file `ops/conto_vero_riparti`.
- **Stato perso** → fermo, chiusure, «riparti» nuovo (`_stato_perso` `:546-571`); stop spento prima della prima accensione (`:637-642`): 70 aperto.
- Creazione protetta (`crea_conto_vero` `:891-913`, allarme `/conto_vero/allarmi/creazione`), giro subito dopo il demo (`main.py:2655-2661`).
- Dashboard (non committata): `ComandiContoVero.tsx` (approva `:132-154`, chiudi tutto `:205-223`, riparti in due passi `:170-204`;
  disattivati da spento), dati da `lib/strategie.ts:259-268`.
- Test di guardia del 54 (secondo giro): nessun file fuori da conto vero, test e dashboard nomina i quattro comandi; non vede la costante importata (78).
- Problemi aperti: 54 (ii) Alto; 70, 268 (dashboard dice F5), 269, 270 Medi; 78, 271-273 Bassi. Chiusi: 53, 55, 57, 59, 60 (nel codice), 61-68, 71-77; 56, 58, 69 come scelto.
- 25-28 nov: F5 (`03ee29e`, 194 ore, il lunedì; 180-182 superati). **28 nov (`34989ea`, `reports/2026-11-28-conto-vero-G1.md`)**: di nuovo
  **G1** (`conto_vero.py:152-155`: `paper_g1.json`, 26 h). **Capitale** = min(saldo USDT `walletBalance` della riga USDT letto dopo le chiusure,
  300, file facoltativo) a ogni fase nuova (`:874-889`); saldo illeggibile o ≤ 0 → niente ordini (`:919-921`). Fase nuova (`_fase_dal_saldo`
  `:625-662`): prima accensione, prelievo, numero nuovo o file tolto; mai dopo stop e «riparti». **Prelievo** (riga USDT, `:956-971`): niente
  ordini subito, alla decisione dopo chiude tutto e riparte dal saldo; prelievo e valore oltre 600 non fermano la fase nuova, gli altri motivi
  sì (`:941`, `:980-999`, `blocco_duro`); pavimento tenuto con il prelievo (`:800-809`). Senza test: 270.

## 15. Il trader AI (area `trader_ai/`, dal 23 nov; versione 9 = `5aaf950`, diciannovesima e riesame; righe di `bcf284d`, della 9 nei suoi punti)
Programma suo sulla macchina (`trader_ai/vps/installa.sh`); dati in `/opt/trader-ai-dati` (solo `trader_ai/avanti` va in git, `vps/salva.sh`),
messaggi interi in `.../trader_ai/messaggi_modello` (`avvio.py:59-60`, `:123`, `:1206`). Dal 24 nov **conto simulato** (`conto_simulato.py`:
solo GET pubblici su `fapi.binance.com`, nessuna chiave, `:42`, `:62-78`); demo suo pronto ma spento (`conto_demo.py`: solo
`demo-fapi.binance.com` `:30-45`, chiavi `TRADER_AI_DEMO_*` diverse da G1 e conto vero `:34`, `:52-63`; `config.json` «simulato»).
* leva intera 1-10 (`limiti.py:16`, `:99-100`; `schema.py:19`); margine separato (`conto_demo.py:237-243`) più commissione dentro il
  disponibile (`limiti.py:105-110`); una sola operazione o un solo limite in attesa (`:94-98`);
* stop obbligatorio sul conto: controllo (`limiti.py:66-81`, `:119-124`, `:134-149`), messo subito (`avvio.py:889-904`; limite eseguito
  subito `:871-878`), rimesso o chiusura a ogni passo (`:251-259`, `:762-780`), spostato senza scoprire (`:924-947`, `:987-1031`); limite
  sparito: esito e rilettura, errore = nessuna azione, «eseguito» del demo confermato al passo dopo (`:546-580`; non in `_annulla_limite`:
  198); obiettivo di un limite sul conto all'esecuzione (`:782-798`); ordini rimasti annullati a inizio passo e prima di aprire
  (`:217-222`, `:838-840`; demo: 199); **annullando un limite si toglie prima il solo limite** (`avvio.py:954`; `conto_simulato.py:433-438`;
  `conto_demo.py:272-279`), stop e obiettivo solo se non si è eseguito (`avvio.py:975`), se no chiusura con `_chiudi_ora` (`:976-985`;
  demo: provare che `allOpenOrders` lasci gli ordini «algo»);
* fermo a mano (`avvio.py:162-163`, `:190`, `:801`, `:865`, `:880`); `chiudi` del proprietario (`:1033-1076`): fermo a file, chiusura, poi
  nel blocco registra anche l'operazione chiusa da sola sul conto e il limite eseguito e chiuso (letture nel blocco: 241); conto estraneo
  → fermo senza toccare niente (`:169-184`, `:198-207`, `:805`); intenzione salvata prima dell'invio (`:854-863`, `:235-241`);
* obiettivo del 3% del conto della mezzanotte UTC, al centesimo, **dopo le spese di chiusura** (`limiti.py:15`, `:51-63`; `avvio.py:309-366`):
  fermo fino a mezzanotte solo se il guadagno letto dopo la chiusura arriva al 3% (`:341-348`), se no evento e modello subito (`:349-366`);
  fermo tolto se durante il fermo il conto scende sotto il 3% senza niente di aperto (`:290-308`); limite in attesa annullato come dal
  modello (`:314-321`); stato e motivo salvati dopo ogni chiusura del programma (`_ricorda` `:144-156`, `:260-263`, `_chiudi_ora`
  `:751-760`); nessuna perdita massima; tetto di 5 dollari prima di ogni chiamata (`costi.py:22`, `giro.py:33-44`);
* quando chiamare (versione 9): sveglia in ogni risposta (`schema.py:17-21`, `:42-43`), salvata con la risposta letta anche se scartata,
  tolta senza (`avvio.py:438-443`); prezzo mark sopra o sotto, 1-240 minuti, almeno uno (`sveglia.py:21-22`, `:53-74`); in più limite
  eseguito e mezzanotte (`avvio.py:383-390`; buco 271); senza sveglia ogni candela da 15 minuti; chiusure e richiami subito; freno solo il tetto;
* «azzera» (`avvio.py:1101-1129`, `conto_simulato.py:433-445`, `installa.sh:91-94`): solo simulato, fermo a mano, niente di aperto (due
  controlli), sotto il blocco, rifiutato con un'operazione da registrare nello stato (268); inizio, mezzanotte e discesa nuovi, memoria tenuta;
  quel giorno resoconto e messaggio dalla ripartenza (`messaggio.py:211-214`, `:232-234`, `:348-353`; 269); restano 270 in parte, 273, 275;
* esito dal conto (`conto_simulato.py:310-331`; demo `conto_demo.py:162-182`, solo «eseguito»); chiusura registrata anche con l'annullamento
  in errore (`avvio.py:666-670`); uscita stimata corretta (`:673-693`); memoria ricostruita una volta senza l'operazione aperta (201).
Gira la 8 (`5b7dde6e`, 28 nov 06:33 UTC); la 9 con l'ok di Alessio (procedura del riesame). Aperti (`README.md`; i 268-275 del trader non
sono quelli del conto vero): Bassi 173, 175, 200, 201, 240-245, 260-267, 270 e 274 in parte, 271-273, 275; Medi solo demo 198, 199. Prima
di un demo 212 misurato, 234, 242, la prova di `allOpenOrders`, una revisione nuova; prima dei soldi veri 146, 147 (settima), una revisione nuova.

## Storia degli invarianti
- 7 nov 2026: leva 10 e perdita giornaliera dalla dashboard: REQUEST CHANGES, niente cambiato; primo avvio: invarianti del demo mappati.
- 7 nov, `9f47972c`: stop ogni minuto; pulsante e stop anche dopo un errore; chiusure da fermo ritentate; «riparti» solo pulito e
  consumato; resti dalla posizione vera con identificativo fisso; `DRY_RUN` spento solo da «false»; tarature senza modo, parità e
  segreti; vecchio ramo reale bloccato.
- 7 nov, `5d5d26ad`: annullo rifiutato → giro fermo; niente mercato con ordini aperti; «riparti» a file; avvio rifiutato con `DRY_RUN`
  falso in ogni caso. `013f9426` (APPROVE): lettura degli ordini in errore da fermo non ferma le chiusure; allarme degli ordini bloccati.
- 8 nov, fase 1 (APPROVE al quarto giro, **`1a8522f`**, riavvio 19:02 UTC): limiti del demo come costanti con test; 429/418 con attese; massimo dello
  stop anche su Firebase; stop anche al 65% del capitale della fase; fermo salvato prima delle chiusure; «riparti» a conto vuoto, sopra il pavimento,
  riapertura alla decisione di G1 dopo; capitale non oltre il saldo; chiusure in 20 pezzi; -1021 con l'ora di Binance. Limiti fissi invariati.
- 8 nov, fase 2 (tre giri: REQUEST CHANGES, REQUEST CHANGES, APPROVE per il commit spento): **invariante cambiato**, con `DRY_RUN` falso il bot parte,
  prima con l'interruttore del conto vero, dal secondo giro sempre; nuovi: G1 sul conto vero con quattro condizioni, freno del cliente, limiti propri
  con test; con `DRY_RUN` vero ordini «solo riduzione» al conto vero se acceso una volta e non vuoto; codice approvato su tutti i file caricati;
  valore = capitale + redditi; «riparti» del conto vero solo da file; demo: stato salvato dopo `parti_da_zero`; al terzo giro stop spento prima della
  prima accensione, blocco per prelievo con tolleranza e tre letture, redditi con ritardo e sovrapposizione. Limiti fissi invariati.
- 12 nov (`a267c40`, `da91124`; APPROVE per il commit spento, REQUEST CHANGES per l'accensione): codice approvato dal tag a un commit su
  Firebase scritto dalla dashboard, letto davvero ogni minuto, valido senza riavvio; Firebase muto: vale la lettura vera degli ultimi 10 minuti;
  da spento ogni 10 minuti; «riparti» del conto vero solo dalla dashboard in due passi, nessun file; l'agente senza tag. Limiti fissi invariati.
- 12 nov, notte (REQUEST CHANGES per l'82; poi `3624baa`): funding dei paper per moneta; il demo legge solo `ultimo_lunedi` e `pesi`. Invariati.
- 14 e 17 nov (APPROVE; `96c6094`, `d5c6708`): lo «stato» legge anche `positionRisk` e `income` FUNDING_FEE del demo. Ordini invariati.
- 25 nov (non committato; secondo giro APPROVE per il commit): **invarianti cambiati** del conto vero: fonte della decisione da G1 (ogni giorno) a
  F5 (ogni lunedì); età massima da 26 a 194 ore; attese fino al lunedì (fino a 7 giorni); posizioni tenute 7 giorni con i limiti dei
  pesi controllati solo al lunedì. Demo e limiti fissi invariati. Secondo giro: nessun invariante nuovo; strategia dichiarata da una costante di classe.
- 26-27 nov, trader AI: versione 7 (`c52fbab`, `82baadc`; APPROVE con condizioni per il simulato, 188 e seguenti) a valori invariati; versione 8
  (`bcf284d`; sedicesima-diciottesima, APPROVE con condizioni): **invarianti cambiati**, il 3% dopo le spese di chiusura e al centesimo; fermo solo
  con il 3% letto sul conto dopo la chiusura, se no si continua; fermo tolto se il conto ci scende sotto durante il fermo. **Rafforzato**: lo stop
  resta mentre si annulla un limite; il «chiudi» del trader registra le chiusure non viste. Tetto, leva, stop obbligatorio e limiti fissi invariati.
- 27 nov (`16c5712`, APPROVE con condizioni): demo, aperture saltate sulle monete non disponibili (chiusure no); paper, ordini limite dal minuto dopo
  i prezzi; giro F5, conto vero, G1, demo, G11, G1N, eventi; vecchio bot fermo con `ops/gate_fermo`; telefono; monitor senza il 429 e il riacceso
  entro l'ora; `DRY_RUN` scritto all'avvio; stato e agente (`e824f22`): prezzi mark pubblici, oscuramento più forte. Limiti fissi e ordini invariati.
- 28 nov, trader AI versione 9 (`5aaf950`; diciannovesima e riesame, APPROVE con condizioni): **invariante cambiato**, il ritmo delle chiamate
  lo decide il modello (1-240 minuti, almeno uno; limite eseguito e mezzanotte), freno solo il tetto di 5 dollari; **nuovo** il conto simulato
  rimesso a 1.000 USDT con il fermo a mano («azzera»). Stop, leva, 3%, «chiudi» e limiti fissi invariati.
- 28 nov (`34989ea` e `b9959ac`; APPROVE con condizioni per il commit spento): **invarianti cambiati**: conto vero su G1 (26 h), capitale dal saldo
  USDT con tetto 300, prelievo → fase nuova alla decisione dopo; demo e conto vero, sotto il minimo solo la chiusura intera con «solo riduzione» (`b9959ac`, 269). Limiti fissi invariati.
