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

## Il piano (21 novembre 2026; le regole sono in `REGOLE.md`)
1. **Codice e test con un modello finto**, prima della chiave: l'elenco delle monete (`universo.py`), i dati tagliati all'ora della
   decisione, il messaggio al modello, i limiti fissi (`limiti.py`), il simulatore degli ordini con spese, funding e stop, il diario.
   Il modello finto risponde a caso dentro lo schema: serve a provare che il codice scarta ciò che esce dai limiti.
2. **La prova sul passato** (1° luglio – 20 novembre 2026, ramo «mercato»), appena c'è la chiave. Gira in una sessione come questa o
   su GitHub Actions a mano; risultato contro G1, il solo Bitcoin e i contanti.
3. **Il paper in avanti** su GitHub Actions, a orario ogni 4 ore (come le azioni con `azioni_avanti.yml`): legge i dati, chiama il
   modello, simula, salva stato e diario in `trader_ai/avanti/` e committa. Non tocca il bot sulla macchina.
4. **La scheda in dashboard** (`dashboard/app/components/trader_ai/`) quando ci sono le prime due settimane di numeri.

### Stima del costo delle chiamate (stima, non misura: la misura arriva con le prime chiamate)
Un messaggio con 12 monete sono circa 7.000 token in entrata (circa 2.000 fissi, che vanno in cache) e circa 3.000 in uscita contando il
pensiero del modello. Con i prezzi di Opus 5.5 (4 e 20 dollari al milione) fanno circa **9 centesimi a decisione**: circa 55 centesimi al
giorno, **circa 16 dollari al mese per ramo** in avanti, e **circa 75-80 dollari** per la prova sul passato (858 decisioni). Con 1.000
USDT di conto, 16 dollari al mese sono l'1,6% al mese, circa il 19% all'anno: il trader deve guadagnare almeno questo solo per pagare le
chiamate. Per questo si guardano sempre due numeri, prima e dopo il costo delle chiamate.

### Dove prendere i prezzi in avanti (controllato il 21 novembre 2026 da questa sessione)
Le pagine dell'API dei futures di Binance (`fapi.binance.com`) rispondono **451** («posto non permesso») ai server degli Stati Uniti:
le ha date a questa sessione e, con ogni probabilità, le darà anche a GitHub Actions (che gira negli Stati Uniti). Rispondono invece i
file pubblici `data.binance.vision` (ma arrivano con circa un giorno di ritardo), le candele spot di `data-api.binance.vision`, l'API
pubblica di OKX e quella di Hyperliquid. La proposta: in avanti le decisioni usano i prezzi e il funding dei perpetui di OKX dell'ora
della decisione; il conto ufficiale si ricalcola ogni giorno con le candele e il funding di Binance dai file pubblici, appena escono.
