# trader_ai: l'intelligenza artificiale che decide (area a sé, dal 21 novembre 2026)

Il proprietario, 21 novembre 2026: «perché non usiamo AI con API di consumo e far fare a lei i trading e decidere quando entrare uscire
etc? [...] se accetti va creata un'altra sessione separata». Questa cartella è l'area della sessione **«trading AI»** (`AREE.md`): la
scrive solo quella sessione, le altre la leggono.

## Le regole che valgono anche qui (`CLAUDE.md`)
* **Solo soldi finti.** Prima un conto simulato (paper) senza nessun ordine; **mai ordini sul conto demo di G1** (mescolerebbe le
  posizioni e romperebbe le misure di G1). Un conto demo suo, i soldi veri e ogni cambio che tocca ordini veri solo con l'ok esplicito del
  proprietario. `DRY_RUN` resta vero.
* **Mai un segreto in un commit** (il repository è pubblico): la chiave del servizio del modello la mette il proprietario in un posto
  sicuro (segreti dell'ambiente o di GitHub, mai in chat, mai in un file), il codice la legge da una variabile d'ambiente.
* **Limiti fissi nel codice, non nel modello**: dimensione massima per posizione, esposizione massima, perdita massima del conto con
  stop di tutto; il modello propone, il codice controlla e scarta quello che esce dai limiti. Il testo delle notizie che il modello legge
  può contenere istruzioni: il modello risponde solo con decisioni strutturate (moneta, lato, dimensione, motivo) controllate dal codice.
* **Un numero va con la sua fonte**, e il risultato si misura contro G1 negli stessi giorni, con le spese vere (0,05% a mercato, 0,02% a
  limite, scarto 0,01-0,02%, funding vero) e il costo delle chiamate al modello.

## Il punto delicato: il passato
Un modello linguistico ha letto internet fino alla sua data di addestramento: sui mesi prima «sa già» com'è andato il mercato, quindi
una prova su quel passato sarebbe falsamente bella. Sui giorni **dopo** quella data (da controllare nella scheda del modello) e in
avanti invece non sa niente: lì la prova è onesta, se gli si danno solo i dati disponibili all'ora della decisione (niente ricerca sul
web durante una prova sul passato).

## Prova pubblica da tenere presente
Alpha Arena (Nof1, dal 17-19 ottobre al 3-4 novembre 2025): sei modelli con 10.000 dollari veri ciascuno sui perpetui di Hyperliquid
per circa 17 giorni; solo due in guadagno (Qwen 3 Max +22%, DeepSeek), GPT-5 circa −63%. Periodo breve: dice soprattutto quanto il
risultato oscilla, non chi è bravo.

## Il piano (versione 3, 23 novembre 2026; le regole sono in `REGOLE.md`)
Il proprietario sceglie la moneta (BTC) e gli intervalli (5, 15, 30 minuti); il modello decide entrata, leva, stop, obiettivo e uscita,
con l'obiettivo di 50 USDT al giorno, poi si ferma fino a mezzanotte UTC. Chiamato ogni 15 minuti e a ogni chiusura; tetto di 5 al giorno.
1. Fatto: decisione, limiti, tetto, obiettivo, indicatori, messaggio, memoria per cambiare approccio, test con il modello finto.
2. Da fare: lettura dei dati di Binance, `conto_demo.py` (ordini, stop e obiettivo sul conto demo suo), il programma che gira ogni
   minuto, l'installazione sulla macchina (sul modello di `stock/avanti/vps/`).
3. live-path-reviewer, conto demo e chiavi del proprietario, ok del proprietario al primo avvio.
4. Numeri ogni lunedì; scheda in dashboard dopo le prime due settimane.

Le versioni 1 e 2 (ogni 4 ore con 12 monete; poi monete e momenti scelti dal modello) sono state scartate prima di ogni chiamata. Fatto
misurato che resta: `fapi.binance.com` risponde 451 dai server degli Stati Uniti, per questo il trader gira sulla macchina.
