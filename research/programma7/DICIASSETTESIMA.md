# Programma 7 — diciassettesima prova: vendere prima degli sblocchi dei token (G15)

Scritto il 24 ottobre 2026, mattina, **prima di scaricare i dati degli sblocchi e prima di qualunque calcolo**. Idea nuova (in coda
come 39 in `research/REGISTRO.md`, provata subito: dati nuovi, tipo «eventi», applicabile a molte monete).

## 1. Perché

Molti token nascono con una parte bloccata (squadra, consulenti, investitori) che si sblocca a date scritte nei documenti del
progetto. Allo sblocco l'offerta di monete vendibili cresce di colpo, e chi le riceve spesso vende o si copre prima vendendo il
perpetuo. Keyrock (2024, oltre 16.000 sblocchi; riassunto da CryptoSlate e BeInCrypto, il testo originale non l'ho letto): circa il
90% degli sblocchi pesa sul prezzo, **il calo comincia fino a 30 giorni prima** e si ferma in circa due settimane dopo; gli sblocchi
della squadra sono i peggiori, quelli degli investitori più ordinati (vendite fuori mercato e coperture), quelli per l'ecosistema
neutri o positivi; sotto l'1% dell'offerta in circolazione l'effetto è piccolo. **Il dubbio scritto prima**: le date sono pubbliche,
quindi il calo potrebbe essere già nei prezzi, e lo short può pagare un funding negativo (molti si coprono): il funding vero è nel
conto. Mai provato nei programmi 5-7.

## 2. I dati (fissati qui)

* **Gli sblocchi**: i calendari pubblici di DefiLlama (`defillama-datasets.llama.fi/emissionsProtocolsList` e
  `/emissions/{protocollo}`, gratuiti), salvati compatti in `research/data/sblocchi/` con l'impronta. Per ogni protocollo:
  gli eventi a gradino (`metadata.unlockEvents`, `cliffAllocations` con categoria e quantità) e le quantità già sbloccate giorno per
  giorno di ogni sezione (`documentedData.data`).
* **La moneta**: il token del protocollo (`metadata.token`) → la sigla con `coins.llama.fi` → il perpetuo USDT del pannello
  (`annunci.perpetuo`, anche con i prefissi 1000 e 1000000). **Controllo**: il prezzo di DefiLlama del token nel giorno dell'entrata
  del suo primo evento usabile deve stare entro il ±20% della chiusura del perpetuo di quel giorno (diviso il prefisso); se no il
  token non si usa (si conta). Il Bitcoin non si usa.
* **Rischio scritto prima**: i calendari sono quelli di oggi; un progetto che ha spostato uno sblocco può comparire con la data
  nuova, e DefiLlama segue i progetti che oggi sono importanti (sopravvissuti). Si dice nei risultati.

## 3. Gli eventi

* Uno sblocco a gradino conta se la sua categoria è **`insiders`** (squadra, consulenti) o **`privateSale`** (investitori): le
  quantità delle due categorie nello stesso giorno (UTC) si sommano.
* **Dimensione** = quantità sbloccata / offerta in circolazione il giorno prima (la somma delle sezioni già sbloccate, tolte quelle
  della categoria `noncirculating`). L'evento conta se la dimensione è **almeno l'1%** e l'offerta del giorno prima è sopra zero
  (il primo giorno del token non conta).
* **Il perpetuo deve esserci**: quotato da almeno 30 giorni all'entrata, volume del giorno prima dell'entrata almeno 2 milioni di
  dollari (come G5), e candele fino al giorno dell'uscita (se il contratto chiude prima, l'evento non si usa: la lezione di E4).
* Se l'entrata di un evento cade prima dell'uscita dell'evento precedente dello stesso token, l'evento non si usa (niente
  operazioni sovrapposte sulla stessa moneta).

## 4. L'operazione

* Short il perpetuo e long il Bitcoin per lo stesso valore all'apertura (00:00 UTC) del giorno **T − 30** (T = il giorno dello
  sblocco); uscita all'apertura del giorno **T + 1**, o prima se la moneta sale del **30%** dall'entrata (l'uscita di N3), con le
  candele giornaliere: se l'apertura è già sopra il livello si esce all'apertura, altrimenti al livello, sempre con l'1% di scarto;
  il Bitcoin si chiude alla chiusura di quel giorno.
* Costi come N3 (`ventunesima.COSTO_MONETA` e `COSTO_BTC`); funding vero dei giorni di tenuta per le due gambe (lo short incassa
  il funding della moneta, il long paga quello del Bitcoin).
* Una prova a eventi, una sola variante: nel conto diventano **140**. Le prove a eventi del conto diventano **17**.

## 5. L'esame

* Come N3 (`trentesima.esame`): media per evento sopra zero con **p ≤ 0,01** (bootstrap sulle settimane d'entrata), positiva nelle
  due metà e senza i 5 eventi migliori. **Per dirla valida** contando tutte le 17 prove a eventi: p ≤ 0,01 / 17 = **0,00059**.
* Il portafoglio: il 5% a operazione, al massimo 20 aperte (`quarantunesima.portafoglio`), Sharpe e Sharpe corretto con l'aggiunta
  (`asticella.corretto_rivisto`), come U1 (prova 41).
* Si riportano anche, per capire e senza decidere niente: la versione senza l'uscita a +30%; il tratto prima dello sblocco (T − 30
  → T) e il giorno dello sblocco (T → T + 1) separati; per anno; per categoria (solo squadra, solo investitori, tutte e due); per
  dimensione (1-3%, 3-10%, sopra il 10%); il funding medio incassato.
