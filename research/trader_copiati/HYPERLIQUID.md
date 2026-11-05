# Copiare i trader migliori di Hyperliquid, in avanti (CH)

Scritto il 1° novembre 2026 alle 12:20 UTC (ora dell'orologio), **prima di raccogliere qualunque posizione**. È l'idea 132 del registro,
la versione automatica e gratuita dell'idea 37 del proprietario («i trader da copiare», 24 ottobre). Fino a qui si è solo provato che la
classifica pubblica di Hyperliquid risponde (48.270 conti) e che le posizioni di un conto si leggono; nessuna posizione è stata salvata
o guardata per decidere qualcosa.

## 1. Perché

* **Su Hyperliquid tutto è pubblico**: la classifica dei conti (guadagno e rendimento di giorno, settimana, mese e da sempre) e le
  posizioni aperte di ogni conto. Su Binance per copiare servono i dati che il proprietario deve mandare a mano; qui si leggono da soli.
* **La domanda è quella del proprietario**: chi è in cima alla classifica sa fare trading, o è stato fortunato? Copiandolo dopo, si
  guadagna?
* **I dubbi scritti prima** (gli stessi dell'idea 37):
  * fra decine di migliaia di conti, i primi del mese sono in buona parte fortuna; chi ha usato più leva sale più in alto;
  * lo storico non si può usare: la classifica è quella di oggi (chi è fallito non c'è più), quindi una prova sul passato sceglierebbe i
    sopravvissuti. **Si misura solo in avanti**;
  * le posizioni si leggono ogni 4 ore (a ogni giro della raccolta delle notizie): chi apre e chiude in giornata non si vede, e si entra
    in ritardo.

## 2. La regola (fissata qui)

* **Chi si copia**: ogni lunedì, al primo giro dopo le 00:00 UTC (e la prima volta il 2 novembre 2026), dalla classifica pubblica
  (`stats-data.hyperliquid.xyz/Mainnet/leaderboard`) i **20 conti con il rendimento del mese più alto** fra quelli con valore del conto
  di almeno 1 milione di dollari, volume del mese di almeno 10 milioni e guadagno del mese sopra zero. L'elenco resta fisso per la
  settimana.
* **Le posizioni**: a ogni giro della raccolta (ogni 4 ore) si legge lo stato di ognuno dei 20 conti (`api.hyperliquid.xyz/info`,
  `clearinghouseState`): per ogni moneta il valore della posizione con il segno, diviso il valore del conto da perpetui
  (`marginSummary.accountValue`). Si salva tutto in `research/trader_copiati/hyperliquid/` (dentro il repo, file piccoli).
* **Il portafoglio copiato**: la media dei 20 conti (ognuno pesa uguale) del peso di ogni moneta; le monete si abbinano ai perpetui di
  Binance (`XYZUSDT` o `1000XYZUSDT`, come la sezione 15 delle regole del paper); le altre restano fuori. Se l'esposizione totale (somma
  dei pesi in valore assoluto) supera 2, tutti i pesi si scalano fino a 2 (come G1, un lato da 1 per parte).
* **Il conto**: i pesi di un giro si tengono fino al giro dopo, sui prezzi orari dei perpetui di Binance, con il costo a mercato sui
  cambi di peso (`seconda.costi_moneta`) e il funding di Binance.
* **I tempi**: dal 2 novembre 2026; un'occhiata a 26 settimane (maggio 2027), **verdetto a 52 settimane** (novembre 2027): regge se lo
  Sharpe dell'anno dopo i costi è sopra 0,5 e sopra quello di G1 negli stessi giorni. Fino ad allora è solo informazione e non entra nel
  bot. Non conta come prova nel conto (come le altre misure in avanti).
* **Per capire, senza decidere niente**: quanta leva usano i 20; quanti conti restano fra i 20 da una settimana all'altra; il rendimento
  del mese dopo dei 20 scelti secondo la classifica stessa.

## Aggiunta del 1° novembre 2026: niente attese fisse

Il proprietario, 1° novembre 2026: «perché il 30 novembre? devo per forza aspettare un mese? [...] verdetto dopo 52 settimane? questo
è inaccettabile, cosa usiamo a fare il backtesting e demo se devo aspettare 52 settimane». Ha ragione: lo aveva già detto il 21 ottobre
(«si giudica sul passato di Binance, il paper è una conferma, non una condizione») e il 24 ottobre («usiamo i dati passati e simuliamo con
paper / live demo per qualche giorno, settimana, ma poi se funziona andiamo live»). Quindi, **da oggi e per tutte le misure in avanti di
questo file** (comprese quelle scritte prima con le 52 e le 104 settimane):
* **niente attese fisse**: le 26, 52 e 104 settimane non sono più condizioni; restano solo come date in cui si rifà il conto per informazione;
* **i numeri vanno al proprietario ogni settimana**, con il confronto con il passato e con G1 negli stessi giorni, detti chiari anche
  quando sono pochi («4 settimane non bastano a dire che funziona» si scrive, ma non blocca niente);
* **cosa decide**: quello che passa la regola del proprietario sul passato (sezione 1 del registro: Sharpe corretto da 0,90 in su, ogni
  anno positivo, t sopra 3) va subito in paper e sul demo; dopo qualche giorno o settimana di demo che esegue come il paper, **i soldi
  veri li decide il proprietario quando li chiede in modo esplicito** (regola di `CLAUDE.md`: `DRY_RUN` resta vero fino ad allora);
* le idee nate dai dati, che sul passato non si possono giudicare in modo pulito, vanno in paper (soldi finti) appena si può, e il
  proprietario decide quando ha visto abbastanza.

## Aggiunta del 5 novembre 2026 (08:40 UTC): due gruppi in più, solo in avanti

Scritto dopo aver visto il conto dei primi 3 giorni (−7,90% in 68 ore, quasi tutto in 4 ore del 4 novembre, quando l'Ether è salito del
5,2%) e la ragione: il portafoglio copiato era venduto per circa 1,75 su 2, quasi tutto Ether, perché la media dei pesi la decidono i
conti con più leva (13 dei 14 conti con posizioni erano corti sull'Ether, con leve da 7 a 16). Il proprietario, lo stesso giorno, ha
chiesto se si possono copiare «le balene». I due gruppi nuovi si misurano **solo da qui in avanti**: i giorni già visti non contano.
Il gruppo di prima resta com'è (regola della sezione 2, senza cambi).

* **Gruppo «balene» (B)**: dalla stessa classifica pubblica, i **20 conti con il valore del conto più alto** fra quelli con volume del
  mese di almeno 10 milioni e guadagno del mese sopra zero (il conto è almeno 1 milione per costruzione). La prima scelta si fa **subito**
  (al primo giro dopo questa aggiunta, il 5 novembre) e vale fino alla scelta di lunedì 9 novembre; poi ogni lunedì al primo giro dopo
  le 00:00 UTC, come il gruppo di prima. Le posizioni si leggono a ogni giro allo stesso modo (un conto che sta nei due gruppi si legge
  una volta). Il portafoglio copiato si fa come nella sezione 2 (media dei pesi dei conti, esposizione scalata a 2 se la supera).
* **Gruppo «a esposizione uguale» (P)**: gli **stessi conti del gruppo di prima**, ma ogni conto con posizioni abbinate ai perpetui di
  Binance viene portato a esposizione totale 2 (i suoi pesi abbinati moltiplicati per 2 diviso la loro somma in valore assoluto) prima
  della media; i conti senza posizioni abbinate contano zero. Così un conto con leva 16 pesa quanto uno con leva 2: si copia la
  direzione di ognuno, non la sua leva. Dal primo giro dopo questa aggiunta.
* **Il conto**: per tutti e due come nella sezione 2 (pesi tenuti fino al giro dopo, prezzi orari di Binance, costo a mercato sui cambi,
  funding di Binance), nello stesso file `HYPERLIQUID_CONTO.md`, accanto al gruppo di prima e a G1 negli stessi giorni quando c'è.
* **Niente attese fisse** (aggiunta del 1° novembre): i numeri vanno al proprietario ogni lunedì; nessuno dei tre gruppi entra nel bot
  senza una regola scritta prima e il suo sì.
