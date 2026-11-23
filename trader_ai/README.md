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

## Il piano (versione 2, 23 novembre 2026; le regole sono in `REGOLE.md`)
Il modello sceglie da solo monete, momenti, entrate e uscite; il codice fissa solo limiti di rischio, tetto di spesa (5 al giorno) e dati.
1. Codice e test con un modello finto: panoramica di tutti i perpetui, dettaglio delle monete scelte, schema della risposta, limiti
   fissi, sveglia (tempo scelto dal modello e allarmi di prezzo), conto del budget, diario.
2. live-path-reviewer sul codice che manda ordini; il collegamento sulla macchina lo scrive la sessione delle crypto
   (`RICHIESTE_CRYPTO.md`); il conto demo nuovo e le chiavi li crea il proprietario; ok del proprietario al primo avvio.
3. Numeri ogni lunedì; scheda in dashboard (`dashboard/app/components/trader_ai/`) dopo le prime due settimane.
4. Nessuna prova sul passato (costerebbe circa 700 dollari: `REGOLE.md`, sezione 8), salvo richiesta del proprietario.

La versione 1 (ogni 4 ore, 12 monete fisse, solo simulata su GitHub Actions) è stata scartata prima di ogni chiamata: frequenza e monete
erano esempi del messaggio di avvio, non richieste del proprietario. Da quella versione resta un fatto misurato: `fapi.binance.com`
risponde 451 dai server degli Stati Uniti (sessioni cloud, GitHub Actions), per questo il trader gira sulla macchina.
