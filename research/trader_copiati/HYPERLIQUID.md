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
