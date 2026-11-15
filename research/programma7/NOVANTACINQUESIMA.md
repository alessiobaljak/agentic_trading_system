# Prova 157 — il funding coperto su Bitcoin ed Ether, senza ricambio (idea 144)

Regole scritte il 15 novembre 2026 dallo strategy-scout, **prima di ogni calcolo**: nessun rendimento, nessuna media, nessun grafico
guardati (solo un controllo che i dati esistano). La prova la esegue strategy-researcher, il giudizio lo dà backtest-auditor. Il numero 157
è libero (ultima nel registro: 156). Non spegne e non sostituisce niente. Richiesta del proprietario del 15 novembre 2026 («un algoritmo in
grado di farmi avere guadagni costanti, giornalieri»).

## Il perché forte
* **Fatto visto indietro e studi seri.** Il guadagno più regolare delle crypto è il funding: chi vuole salire con la leva paga chi vende il
  perpetuo. Comprando a pronti e vendendo il perpetuo per lo stesso valore il prezzo si annulla e resta il funding. Studi verificati il 15
  novembre 2026 (ricerca sul web):
  * Christin, Routledge, Soska e Zetlin-Jones, «The crypto carry trade», lavoro di ricerca della Carnegie Mellon University, 1° agosto 2022
    (non una rivista): sui contratti più scambiati la strategia ha Sharpe annuo dentro il campione fra 7 e 10, legata alla struttura dei
    perpetui. **Attenzione**: quei numeri sono sul periodo dello studio (fino al 2021-2022, quando il funding era altissimo) e prima dei
    costi veri; non valgono per oggi.
  * Schmeling, Schrimpf e Todorov, «Crypto carry», BIS Working Paper n. 1087, aprile 2023 (rivisto a ottobre 2025; secondo un elenco
    risulta accettato da *Management Science*, non verificato sul sito della rivista): il guadagno di comprare a pronti e vendere il future su
    Bitcoin ed Ether supera il 10% l'anno in media (il picco cambia fra le versioni: 40% o 60%); lo spiegano con la domanda di leva
    dei piccoli investitori e con il poco capitale degli arbitraggisti; **un carry alto prevede crolli del prezzo successivi**.
* **Perché la prova 97 non basta.** La 97 (CC) tenne il lato venduto di F5 (373 monete, ricambio ogni settimana): spese 5,1% l'anno
  sul capitale contro il funding, per capitale +4,7% l'anno, Sharpe 1,66 ma Sharpe corretto 0,71 e anni 2022, 2025 e 2026 negativi
  (`RISULTATI_TRENTACINQUESIMA.md`). La causa era il ricambio e le monete piccole. Qui: **due monete sole, le più liquide, nessun
  ricambio** (si esce solo con il funding medio negativo). Idea diversa dalla 97 perché cambiano l'universo e il ricambio; stessa
  famiglia di fonte di guadagno (probabile che il gruppo sia lo stesso: si segna).
* **Avviso onesto, scritto prima.** Il funding di Bitcoin ed Ether è il più basso fra le monete: il guadagno atteso è basso (a occhio
  una cifra, non due, l'anno per capitale) e il 2022-2026 può avere anni piatti o negativi; l'esame per anni positivi e Sharpe corretto
  0,80 può non passare. Il valore della prova è dire se la regolarità c'è dopo i costi. Probabilità: media che sia positiva, bassa che
  passi tutto l'esame.

## Dati (controllo prima di ogni calcolo)
* **Perpetuo**: `research/programma6/seconda.pannello()` (aperture giornaliere e funding vero di BTCUSDT e ETHUSDT dal 1° gennaio 2020;
  funding dai file mensili dell'archivio di Binance, l'ultimo mese pieno è ottobre 2026). Il funding giornaliero è la colonna `funding`
  del pannello, **come la usa G1 in `programma7/prima.py`** (lo stesso indice del giorno; lo short incassa se è positivo).
* **Pronti**: candele giornaliere `BTCUSDT` e `ETHUSDT` dall'archivio pubblico `data.binance.vision/data/spot/monthly/klines/{S}/1d/`
  (verificato il 15 novembre 2026: i file di gennaio 2020, settembre 2026 e **ottobre 2026** esistono per tutte e due). Il loader è
  `trentacinquesima.scarica`/`tabella_pronti` (timestamp in microsecondi dal 2025 già gestiti), con l'elenco dei mesi allungato da
  **2020-12 a 2026-10** (la 97 si fermava a settembre). **Oggi la cartella `research/data/spot_1d/` non c'è in questa copia del
  repository: va scaricata (due coppie, pochi file).**
* **Periodo**: dal **4 gennaio 2021** (`sesta.INIZIO`) al **4 ottobre 2026 compreso** (`prima.FINE`, il 5 ottobre escluso), come la 97 e
  G1; l'anno 2021 intero non c'è (parte il 4 gennaio), il 2026 finisce il 4 ottobre. La media del funding sui 90 giorni prima richiede il
  funding dal 6 ottobre 2020: esiste (dal 2020).
* **Controllo che lo storico ci sia (si ferma e si scrive se manca)**: per BTC ed ETH, apertura del perpetuo e funding presenti in
  tutti i giorni da 90 giorni prima del 4 gennaio 2021 al 4 ottobre 2026; apertura a pronti presente in tutti i giorni dal 4 gennaio 2021
  al 4 ottobre 2026 (nessun buco riempito); il funding dell'ultimo mese non è la media riempita di `seconda.riempi_funding` (verificare
  che i giorni fino al 4 ottobre vengano dai file veri); e per ogni giorno l'apertura a pronti e quella del perpetuo differiscono meno
  del 2% (altrimenti dati sbagliati: ci si ferma). Si scrivono i numeri dei giorni controllati.

## La regola (valori fissati qui)
* **Due monete, ciascuna per conto suo**: BTC ed ETH, metà del nozionale ciascuna (50% e 50%). Se una moneta è fuori, la sua metà resta
  in contanti a rendimento zero (non si ridistribuisce sull'altra; il capitale resta quello pieno: scelta prudente, dichiarata).
* **Segnale**: ogni giorno D alle 00:00 UTC, per ogni moneta, la **media semplice del funding giornaliero degli N giorni D−N … D−1**
  (nota a fine giornata D−1). **Dentro** (acquisto a pronti + vendita del perpetuo per lo stesso valore) se la media è strettamente
  **maggiore di zero**; **fuori** (le due gambe chiuse) se è **minore o uguale a zero**. Una soglia sola, la stessa per uscire e per
  rientrare (nessuna banda: dichiarato, il ricambio atteso è basso perché il funding di base di Binance è positivo di norma).
* **Varianti (al massimo 2, fissate qui, nessun'altra dopo i risultati)**: **N = 30** e **N = 90**. Perché: il funding cambia regime in
  settimane o mesi, quindi 30 giorni reagisce in fretta (esce prima ma entra e esce più spesso: ogni giro costa circa 14 giorni di
  funding normale) e 90 giorni è lento e ricambia poco (esce tardi). Sono i due punti ragionevoli di un'unica regola, non due idee.
  Se passano tutte e due, per il paper vale la **lenta (90)**, scelta qui prima dei risultati perché fa meno operazioni.
* **Esecuzione**: il segnale del giorno D−1 si esegue all'apertura di D, per entrambe le gambe insieme. Nessun ritardo in più e nessun
  ordine diverso da quello dei costi sotto.
* **Primo giorno**: il 4 gennaio 2021 si entra se la media è positiva (costo di entrata pagato). **Ultimo giorno**: si conta anche
  l'uscita finale delle posizioni ancora aperte il 4 ottobre 2026 (prudente).

## Il conto
* **Rendimento del giorno per ogni moneta dentro, per unità di nozionale della moneta**: (rendimento a pronti − rendimento del perpetuo)
  da apertura ad apertura del giorno successivo (la base: quanto il perpetuo si scosta dal pronti) **+ il funding incassato del giorno**
  (funding vero). Il prezzo si annulla per costruzione; senza ribilanciare la deriva delle due gambe (come la 97, dichiarato).
* **Costi**: sul perpetuo 0,05% a mercato più scarto 0,01% (BTC ed ETH) = 0,06% per lato (`seconda.costi_moneta`); a pronti **0,15% per
  lato** (0,10% di commissione di Binance più 0,05% di scarto), uguale alla 97, **prudente** per BTC ed ETH. Un giro (entrata più
  uscita) vale circa 0,42% del nozionale della moneta. Costi sul cambio di posizione di ogni moneta (da 0 a 1 o da 1 a 0). Nessun
  ordine limite nella misura principale; **controllo descrittivo**, non variante: gli stessi conti con il perpetuo a 0,02% (limite) e
  il pronti a 0,10% + 0,01% di scarto.
* **Funding vero** (non medio), nessun riempimento. Senza interessi sul contante fermo e senza interessi sul margine.
* **Capitale**: nozionale a pronti più il margine del perpetuo a leva 2 (metà del nozionale) = **1,5 volte il nozionale**, come la 97.
  Si riportano il rendimento **per capitale (il numero che conta)** e per nozionale, e il guadagno in USDT l'anno su 1.000 USDT.

## Serie e l'esame
* **Serie giornaliera** per capitale; **serie settimanale** sommando i giorni lunedì-domenica (`prima.lunedi_del_giorno`), dal lunedì 4
  gennaio 2021 (il 4 gennaio 2021 è un lunedì) all'ultima settimana intera prima del 5 ottobre (domenica 4 ottobre 2026).
* **L'esame** (regole approvate dal proprietario il 9 novembre): `terza.esame` sulla serie settimanale per capitale, con `sesta.INIZIO` e
  `sesta.ANNI_PIENI`, per **ognuna delle due varianti**. Passa se: netto dopo i costi positivo; **ogni anno positivo** (2021 dal 4
  gennaio e 2026 fino al 4 ottobre sono parziali e **contano tutti e due**); t almeno 3 (sulla serie settimanale, `terza.esito`); Sharpe
  corretto almeno 0,80 con il conto per famiglie: `asticella.corretto_famiglie` con il mazzo completo (`mazzo()`), taglio `TAGLIO` di
  `asticella.py`, le due serie settimanali come serie nuove (nomi `CB30`, `CB90`); esempio `audits/repro/prova28_2026-11-11.py`, voce 11.
  Si scrive il gruppo in cui cadono (probabile quello della 97).
* **Il conto delle prove nel registro**: da **320 a 322** (le due varianti; `research/trials/novantacinquesima.csv`).

## Controlli descrittivi (numeri scritti, senza soglia; li giudica backtest-auditor)
1. **Discesa massima** per capitale (giornaliera e settimanale) e la peggiore settimana; **mesi positivi** (quota e numero) e **giorni
   positivi** (la richiesta del proprietario è di guadagni costanti giorno per giorno: si scrive quanti giorni sono positivi, quanti a
   zero perché fuori, quanti negativi).
2. **Rendimento anno per anno** per capitale e per nozionale (2021 parziale, 2022, 2023, 2024, 2025, 2026 parziale), con scomposizione in
   funding incassato, base e spese; BTC ed ETH separati.
3. **Correlazione con G1** sui giorni comuni e sulle settimane (rendimenti giornalieri `netto` di `risultati_prima/giorni_G1.csv.gz`, per
   le settimane `settimane_G1.csv.gz`), e con la serie della prova 97 (CC) e con BTC. Atteso vicino a zero.
4. **Il caso «sempre dentro»** (nessuna uscita): non è una variante e non passa l'esame; serve a vedere se l'uscita sul funding negativo
   guadagna qualcosa (e quanto costa in giri). Si riportano anche i giorni dentro e i giri per moneta e variante.
5. **Il rischio della borsa e del margine, scritto in chiaro nel rapporto** (il passato non lo misura): tutto il capitale sta su una sola
   borsa (Binance), con tutte e due le gambe: se la borsa si ferma, blocca i prelievi o fallisce (come FTX nel novembre 2022), il rischio
   non è coperto dalla copertura; il perpetuo a leva 2 si liquida se il prezzo sale di circa la metà prima di riportare margine
   (si scrive la salita massima del prezzo in una posizione aperta nel periodo, dalle aperture a pronti), con il costo di vendere il
   pronti per rifare il margine in un rialzo; le liquidazioni automatiche della borsa e le chiusure forzate in caso di crollo; il rischio
   del dollaro digitale (USDT) su cui sta il margine; il funding negativo prolungato negli anni di ribasso (l'esame lo misura sul
   passato). Una ricerca del 2023 (Schmeling e altri) lega il carry alto a crolli futuri: si scrive come cautela.
6. **Il guadagno in USDT l'anno** su 1.000 USDT di capitale, per variante, accanto alla discesa massima: serve al proprietario per
   decidere se il livello (probabilmente basso) vale l'impegno, anche se l'esame passa.

## Cosa si consegna
Rapporto su file in `research/programma7/RISULTATI_NOVANTACINQUESIMA.md`, serie giornaliere in `risultati_novantacinquesima/`, script
`novantacinquesima.py`, registro delle varianti `research/trials/novantacinquesima.csv`, i dati a pronti in `research/data/spot_1d/` (non
committare `research/data/`); a schermo al massimo 20 righe. La sessione principale committa le regole e la riga del registro **prima** del
calcolo; strategy-researcher in modalità verifica chiude le ambiguità prima di calcolare (come per la 155); dopo il calcolo, se
promettente, backtest-auditor.

## Testo della riga del registro
| 157 | CB: il funding coperto solo su Bitcoin ed Ether, senza ricambio: comprare a pronti e vendere il perpetuo per lo stesso valore, dentro se la media del funding sugli ultimi N giorni è sopra zero, fuori altrimenti (N = 30 o 90), capitale 1,5 volte il nozionale, costi del programma 7 più 0,15% a pronti, dal 4 gennaio 2021 (`programma7/NOVANTACINQUESIMA.md`); idea 144 (Christin, Routledge, Soska e Zetlin-Jones 2022; Schmeling, Schrimpf e Todorov, BIS 2023; proprietario 15 novembre) | 2 | da fare | da fare |

## Regole corrette il 15 novembre 2026 dopo la verifica, prima di ogni calcolo (sessione principale)
La verifica di strategy-researcher (`VERIFICA_NOVANTACINQUESIMA.md`) ha trovato ambiguità; nessun rendimento è stato calcolato (solo la
presenza dei dati e lo scarico dei prezzi a pronti, `novantacinquesima_dati.py`, impronte in `risultati_novantacinquesima/`). Le
letture che valgono:
1. **Quantità ferme, niente ribilanciamento gratis (A1)**: all'ingresso si compra a pronti la quantità Q = (capitale della moneta / 1,5)
   / prezzo e si vende la stessa quantità sul perpetuo; Q **non cambia** finché si resta dentro (è il senso di «senza ricambio»: un conto a
   nozionale fisso ribilancerebbe ogni giorno senza pagarne il costo). Il conto giornaliero è in USDT sul capitale della moneta (metà del
   capitale ciascuna): variazione del pronti meno variazione del perpetuo (la base), più il funding vero sul nozionale del giorno (Q per il
   prezzo mark), meno le spese all'ingresso e all'uscita. All'uscita si chiude tutto; al rientro Q si ricalcola dal capitale di quel giorno.
2. **Il margine (descrittivo, con una regola)**: il terzo del capitale fuori dal nozionale è la riserva del perpetuo. Si scrive il caso
   peggiore della perdita del perpetuo contro la riserva; se la perdita aperta del perpetuo supera la riserva, quel giorno si vende a pronti
   quanto basta a coprirla (con lo 0,15% di costo) e si riduce il perpetuo della stessa quantità: Q cala, e lo si scrive.
3. **L'esame (A2)**: valgono le quattro condizioni scritte qui sopra e solo quelle: netto positivo; ogni anno di calendario positivo (2021
   e 2026 parziali contano); t almeno 3, calcolato come Sharpe settimanale per la radice di settimane/52; Sharpe corretto almeno 0,80 con
   `corretto_famiglie` e il mazzo completo, con le serie settimanali «157 A» (30 giorni) e «157 B» (90 giorni) passate insieme in un solo
   calcolo. `terza.esito` non si usa (ha soglie diverse). Il resto è descrittivo.
4. **L'uscita finale (A3)**: il 4 ottobre 2026, all'apertura del 5 come prezzo di uscita, con le sue spese nel giorno 4 ottobre.
5. **Il capitale (A4)**: per capitale = somma dei due conti delle monete sul capitale totale; per nozionale = diviso per il nozionale
   d'ingresso; guadagno in USDT l'anno = media settimanale × 52 × 1.000 (semplice, scritto come tale).
6. **Le letture descrittive (B1-B7)**: il giorno dell'uscita paga le spese e da lì si è fuori; anni di calendario sulla serie giornaliera;
   nel controllo con ordini limite il perpetuo costa 0,02% più lo scarto di 0,01% (come `seconda.costi_moneta`); correlazioni sui
   rendimenti giornalieri netti con G1 ricalcolato e con il Bitcoin, e su quelli settimanali con la prova 97; «sempre dentro» solo
   descrittivo; la salita massima del prezzo come la scrive la verifica.
