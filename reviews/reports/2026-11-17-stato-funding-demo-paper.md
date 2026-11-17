# Revisione: lo «stato», funding di G1 regolamento per regolamento, demo contro paper (17 nov 2026)

### Riepilogo e verdetto

**APPROVE** per il commit (nessun riavvio: la macchina rilegge lo script a ogni richiesta «stato»).
0 Bloccanti, 0 Alti, 0 Medi; 5 Bassi nuovi (90-94): due numeri o segni del testo che si leggono male (la colonna «monete» della
riga «altre» confronta cose diverse; «—» non spiegato), un messaggio sbagliato con Firebase muto, una lettura doppia a Binance e a
Firebase, test che non coprono quattro comportamenti. Nessuno tocca la sicurezza: la sezione è di sola lettura, si ferma al primo
429 o 418 insieme alle altre due, rispetta la finestra del ribilancio, non stampa segreti e non fa mai fallire lo stato. Correggere
90-92 nello stesso commit costa poco e si consiglia; se il cambio resta su testi e conteggi (nessun tocco a cliente, lettore, finestra
o richieste) non serve un nuovo giro, bastano i test.

Verifica del commit precedente: `96c6094` (sezione dei pesi di oggi, approvata il 14 nov) è uguale alla copia approvata
(`giro14nov/copia2/`) salvo il commento di `EQUITY_VECCHIA_S` (`state_snapshot.py:1189`), che è la correzione del problema 89:
**89 chiuso**. Il test dei pesi è identico (md5 `05a50a46`).

### Oggetto (branch, commit, file toccati, invarianti coinvolti)

- Branch `claude/brave-albattani-1b12fv`, modifica non committata su `6cad6f4`.
- `scripts/state_snapshot.py` (+101 righe): costanti `GIORNI_FUNDING_CONFRONTO = 3`, `MONETE_FUNDING_CONFRONTO = 6` (`:1190-1191`);
  `sezione_funding_demo_paper` (`:1194-1203`), `_equity_valida` (`:1206-1208`), `_funding_demo_paper` (`:1211-1242`),
  `confronto_funding_regolamenti` (`:1245-1289`); `build()` la chiama in fondo, dopo i pesi, con lo stesso `cliente_demo` (`:232`).
- `tests/test_funding_demo_paper.py` nuovo (6 test).
- Copia rivista: `<cartella di lavoro>/giro17nov/copia/` (md5 `state_snapshot.py` `6b5a6a8c…`, test `27399f22…`, diff in `diff.txt`).
- Invarianti del percorso degli ordini coinvolti: nessuno. Nessun cambio in `bot/`, `firebase/`, `ops/`; `hard_limits.py` invariato.
  L'elenco delle letture ammesse (`PESO_LETTURE`/`AMMESSI`, `:817-818`, `:849`) è invariato: `income` c'era già.

### Checklist A–F

**A. Limiti fissi e interruttori**
- Valori di `bot/risk/hard_limits.py` invariati (nessuna differenza in `bot/`): OK.
- Nessun limite spostato in configurazione, ambiente o Firebase: OK.
- Parametri della dashboard: NON APPLICABILE (la modifica non li legge).
- Limiti di G1 sul demo (`demo_binance.py`): invariati, NON APPLICABILE.
- Pulsante che chiude tutto: invariato, NON APPLICABILE.

**B. Ordini**
- Tutti i punti: NON APPLICABILE. La sezione non manda ordini: `_Lettore.chiedi` usa solo `GET` firmato (`state_snapshot.py:918`),
  la funzione `SoloLettura` rifiuta ogni metodo diverso da GET e ogni percorso fuori elenco prima di partire (`:860-861`), il cliente
  del demo va solo a `demo-fapi.binance.com` (`demo_binance.py:64-65`, `_url` `:437`). Provato sullo stato intero
  (`giro17nov/test_prove_17nov.py::test_build_normale`): metodi `{GET}`, indirizzo `{demo-fapi.binance.com}`, nessuna scrittura su Firebase.

**C. Stato e resilienza**
- Sola lettura su Firebase: solo `get_rtdb` (`:1215-1220`), nessuna scrittura (provato: `fb.scritture == []`): OK.
- 429 e 418: il cliente è quello condiviso di `build()` (`:122-126`, `:232`); `SoloLettura.bloccato` ferma ogni richiesta dopo il primo
  limite, per tutte e tre le sezioni (`:862-869`). Provato sullo stato intero con 429 e 418 alla prima richiesta: **una sola richiesta
  in tutto lo stato**, la sezione scrive «le letture si fermano (Retry-After 30 s)». Il cliente del demo non ritenta: `LimiteInLettura`
  non è un errore di rete (`demo_binance.py:470`) e risale subito: OK.
- Peso: una richiesta `income` (30 a pagina, al massimo 10 pagine = 300) con il suo `_Lettore` (tetto 1.000, `:892`) e la guardia comune
  sul peso usato dall'indirizzo (sopra 600 non parte, `:907-908`; provato con peso 700: la sezione non chiede). Stato intero misurato con
  56 monete: 61 richieste, peso 395, di cui 30 della sezione nuova. Il demo restituisce il peso usato (stati della macchina del 16-17
  nov: 60-220 nel minuto). OK, con la lettura doppia del 93.
- Finestra del ribilancio: controllata per prima, prima di Firebase e di Binance (`:1212-1213`); test `tests/test_funding_demo_paper.py:80-82`: OK.
- Errori: tutto dentro un `try` che restituisce «non letto» (`:1200-1203`); dati sporchi su Firebase (testo al posto di un numero) →
  «non letto: ValueError…», lo stato prosegue (provato): OK. Firebase muto → messaggio sbagliato (92).
- Nessuna richiesta a Binance se mancano il funding del paper o l'equity (`:1226-1229`, test `tests/test_funding_demo_paper.py:85-90`): OK.
- Tempo: una pagina in pratica (circa 200 righe di funding al giorno); il tetto di 180 s della sezione resta; l'agente concede 900 s
  (`ops_agent.py:48`): OK.

**D. Separazione fra paper, demo e conto vero**
- Solo la chiave del demo (`cliente_di_sola_lettura`, `:998-1003`), solo l'indirizzo del demo; nessuna chiave del conto vero: OK.

**E. Segreti e sicurezza**
- Errori con `_motivo` → `senza_firma` (`:881-884`); errore della chiave: solo il tipo (`:1233-1234`). Provato: un errore di rete con
  `signature=…` nell'indirizzo esce come «?[parametri tolti]»; nessuna chiave, segreto o firma nello stato intero: OK.
- Il risultato va in `ops/results/` (repository pubblico) con numeri del conto demo: come la sezione delle esecuzioni, già accettato.
- Su GitHub (`snapshot.yml`) senza chiave del demo: «manca la chiave», nessun dato del demo nel `docs/state.md` pubblico (provato): OK.

**F. Test**
- `python3 -m pytest tests/test_funding_demo_paper.py tests/test_pesi_g1_oggi.py tests/test_demo_esecuzioni.py -q` → **37 passed in 0.76 s**.
- Suite intera: `PYTHONPATH=<cartella di lavoro>/cripto:. python3 -m pytest tests/ -q -p no:cacheprovider` → **2817 passed in 194.25 s**
  (compresi i test dei limiti fissi, del demo, del conto vero e della firma; nello stesso momento girava un'altra suite della sessione
  principale, senza effetti visibili).
- Prove mie sullo stato intero: `giro17nov/test_prove_17nov.py`, 10 passate (normale, «altre», 429, 418, peso alto, Firebase muto,
  senza chiave, firma nell'errore, dati sporchi, peso dello stato intero).
- Mutazioni (`giro17nov/mutazioni.py <radice> <cartella>`, carica davvero la copia mutata): 14 provate, 8 prese (finestra tolta,
  cornice tolta, segno del demo, equity scambiate, tipo d'incasso, richiesta senza funding del paper, cliente nuovo nello stato,
  blocco non ricordato); non prese: il controllo, una equivalente (filtro dei giorni del paper: il ciclo sui giorni filtra già),
  e quattro che cambiano il comportamento (94) più `endTime` oltre adesso (innocua).

### Problemi

**90 — Basso. La colonna «monete demo/paper» della riga «altre» confronta cose diverse.**
`state_snapshot.py:1269` somma il numero di monete di ogni regolamento del paper nelle ore «altre»; `:1272` conta sul demo le monete
distinte (`len(d['monete'])`). Scenario provato (`test_prove_17nov.py::test_altre_conteggio_monete`): due monete con il funding ogni 4
ore, tenute da tutti e due, tre regolamenti nel giorno → `| 2026-11-16 altre | +0.0009% | +0.0300% | -0.0291% | 2/6 |`. Chi legge
pensa che al demo manchino 4 monete, proprio la domanda della voce 3 del piano di G1 (il demo incassa meno funding). Le monete a 4 ore
ci sono davvero (la colonna «altre ore» del funding del demo non è zero negli stati del 16-17 nov).
Correzione suggerita: contare anche sul demo i pagamenti (coppie moneta-ora) nella classe, o scrivere nell'intestazione che il numero
è «pagamenti»; un test con due ore «altre».

**91 — Basso. «—» non è spiegato nel testo stampato.**
`:1286-1288`: la spiegazione è solo nella docstring (`:1248`). Scenario: una moneta grande del demo che il paper ha ma non fra le sue
10 più grandi appare «XYZUSDT +0.0050/—»: si legge «il paper non ce l'ha». Correzione: aggiungere alla riga «— = non fra le 10 più
grandi del paper».

**92 — Basso. Firebase che non risponde diventa «non ancora».**
`:1215-1227`: un errore o un `None` sul ramo `/paper_g1/funding` dà `{}` e la riga «non ancora: il paper di G1 non ha funding per
regolamento in questi giorni». Nel processo dello stato `get_rtdb` non solleva e restituisce lo specchio vuoto
(`bot/core/firebase_client.py:681-702`), quindi lo stesso testo. Provato (`test_build_firebase_muto_sul_funding`). Scenario: un buco di
Firebase all'ora dello stato fa credere che il paper abbia smesso di pubblicare il funding. Correzione: distinguere «ramo non letto»
(`None` o errore) da «letto, senza i giorni».

**93 — Basso. Letture doppie a Binance e a Firebase.**
(a) `:1239` rilegge `income` FUNDING_FEE dei 3 giorni, già letto nello stesso stato dalla sezione delle esecuzioni su 6 giorni
(`:1059`): +30 di peso a ogni stato (misurato: 395 in tutto, guardia dei 600 attiva), nessun rischio oggi. (b) `:1224` legge **tutto**
il ramo `/paper_g1/funding`, che cresce ogni giorno e non si pulisce mai (`bot/portafoglio/f5.py:641-646` scrive, nessuno cancella; stima,
non misura: da 3 a 24 chiavi al giorno da circa 0,4 KB, fino a qualche MB l'anno), anche nell'azione di GitHub a ogni push.
Correzione: passare alla sezione le righe del funding già lette (e chiedere solo se mancano); leggere `/paper_g1/funding/{giorno}` per i
tre giorni. La pulizia del ramo è del paper (`f5.py`), fuori da questa modifica: va nel backlog.

**94 — Basso. Test che non coprono quattro comportamenti.**
Mutazioni non prese: tetto dell'equity tolto (`:1208`), valute diverse da USDT sommate (`:1251`), «ultimo regolamento» preso anche da
«altre» (`:1273`: con un ultimo giorno che finisce con un'ora «altre» la riga delle monete userebbe il regolamento sbagliato), nota «forse
incompleti» mai stampata (`:1242`). Mancano anche Firebase muto (92) e due ore «altre» (90). Il commento del test a `tests/test_funding_demo_paper.py:25`
(«fuori dai giorni letti? no: dentro i 3 giorni») è da pulire. Correzione: aggiungere i casi.

Osservazioni senza problema: l'equity «di oggi» come divisore su 3 giorni è un'approssimazione dichiarata (`:1247`, `:1277`), con un
errore relativo dell'ordine della variazione dell'equity (pochi per cento di numeri già piccoli); manca l'avviso dell'equity vecchia
della sezione dei pesi (85), qui poco importante. Il 16 novembre il regolamento delle 00 del paper non c'è (riavvio delle 07:36 UTC,
contato dal codice di prima): la prima riga sarà quella delle 08, atteso. Il segno è coerente: il paper scrive «incassato» positivo
quando riceve (`f5.py:613`), Binance lo stesso. Le chiavi coincidono: il paper usa giorno e «HH:MM» dell'ora del regolamento (`f5.py:611`,
`:644`), il demo giorno e ora dell'incasso (`:1253`, `_regolamento` `:951-954`); le classi 00/08/16/«altre» sono le stesse da tutte e due
le parti. Lunghezza: la sezione misura circa 1.100-2.000 caratteri; pesi e funding insieme circa 3.000-4.000; con il taglio dell'agente
(testa e coda da 10.000, `ops_agent.py:79-86`) restano tutte e due nella coda (provato con `truncate`); la testa non cambia.

### Invarianti modificati

Nessuno. Il percorso degli ordini, i limiti fissi, i pulsanti e l'elenco delle letture ammesse dello stato sono invariati. Cambia solo
l'uso: una lettura `income` in più per stato, con lo stesso cliente e lo stesso blocco.

### Decisioni per Alessio

Nessuna decisione nuova: la modifica non tocca limiti, ordini, chiavi né riavvii. Restano aperte quelle di prima (registro): chi può
scrivere l'approvazione del conto vero (54 ii), regole di Firebase da pubblicare con i comandi del demo e del conto vero, chiavi del
conto vero senza prelievo e limitate all'indirizzo della macchina.

### Domande aperte

1. Per la sessione principale: nella colonna «monete demo/paper» della riga «altre» volete le monete o i pagamenti? Il paper pubblica
   per ogni regolamento solo il numero di monete e le 10 più grandi, quindi le monete distinte del paper nelle ore «altre» non si
   ricostruiscono: la scelta più semplice è contare i pagamenti da tutte e due le parti (90).
2. Ripetuta dal 7 novembre: la proposta di leva 10 e perdita giornaliera dalla dashboard (`reports/2026-11-07-limiti-leva-perdita-giornaliera.md`)
   non è mai stata applicata al codice; la voce del registro si chiude come «non applicata»?
