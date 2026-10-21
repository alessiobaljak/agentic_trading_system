# Programma 6 — quarantunesima prova: lo short dopo l'arrivo su Upbit (U1)

Scritto il 21 ottobre 2026, primo pomeriggio, **prima di qualunque calcolo sui prezzi**. Idea nuova, mai provata (non è nel
registro: le prove 18, 30, 32 riguardano le monete nuove dei perpetui, la 21 gli annunci di Binance). Prima di scriverla si
è guardato solo l'elenco delle date d'arrivo su Upbit (`scarico_upbit.py`), senza prezzi di Binance.

## 1. Perché

Upbit è la borsa più grande della Corea. Quando una moneta che si scambia già nel mondo arriva sul suo mercato in won, il
prezzo sale di colpo anche su Binance: i compratori coreani entrano in poche ore e chi lo sa prima compra per rivendere a
loro. Dopo l'arrivo l'attenzione si spegne e i nuovi compratori non hanno altri da cui farsi ricomprare la moneta: il prezzo
tende a tornare indietro nei giorni dopo («si compra la voce, si vende la notizia»). Si vende su Binance **dopo** la prima
fiammata, non la si insegue. È lo stesso schema di N3 (le monete nuove scendono dopo l'euforia dell'inizio), con un evento
diverso: qui la moneta esiste già da tempo e cambia solo il pubblico.

## 2. La regola (valori fissati qui)

* **Eventi**: la prima ora di scambi di ogni mercato `KRW-<moneta>` di Upbit (la prima candela a 1 ora; gli annunci di
  Upbit non si raggiungono da qui) dal **1 gennaio 2021** al **20 settembre 2026**, per le monete che hanno il perpetuo
  USDT-M su Binance (`annunci.perpetuo`, anche con i prefissi 1000, 1000000, 1M) con la prima candela giornaliera almeno
  **7 giorni** prima del giorno d'arrivo. Esclusi il Bitcoin, le monete stabili (`trentesima.STABILI`) e i contratti esclusi
  del programma (`seconda.ESCLUSI`).
* **Stessa moneta, non un omonimo**: il prezzo del primo giorno su Upbit (won) diviso la chiusura dello stesso giorno su
  Binance (dollari, corretta per il prefisso) deve stare fra **900** e **1.700** won per dollaro; altrimenti è un'altra
  moneta con la stessa sigla e non si usa.
* **Entrata**: short la moneta e long il Bitcoin per lo stesso valore (come N3) all'apertura della candela a 1 ora di
  Binance che comincia **2 ore** dopo la prima ora di Upbit (dopo la fiammata).
* **Uscita**: dopo **7 giorni** (168 ore) all'apertura della candela; uscita di protezione se la moneta sale del **30%** sopra
  il prezzo d'entrata (al livello, con l'1% di scarto, come N3).
* **Costi** come N3 (`ventunesima.COSTO_MONETA` per la moneta, `COSTO_BTC` per il Bitcoin) e il funding dei giorni tenuti,
  incassato sullo short della moneta e pagato sul long del Bitcoin.
* Una prova a eventi (la **settima** del programma) e un portafoglio (nel conto del programma 6 diventano **64**).

## 3. L'esame

* **Per evento**: media netta sopra zero con **p ≤ 0,0014** (0,01 diviso le 7 prove a eventi del programma; bootstrap sulle
  settimane d'arrivo), positiva nelle due metà e senza i 5 eventi migliori.
* **Come portafoglio** (lezione 22: una regola buona per evento può essere cattiva da tenere): il 5% del capitale a
  operazione, al massimo 20 aperte, la settimana somma le operazioni chiuse; `terza.esame` e `terza.esito` con lo Sharpe
  corretto sulle **64** prove.
* **VALIDA** solo se passa tutte e due.
* Si riportano anche (per capire, non per scegliere): la prima reazione (dall'apertura 24 ore prima della prima ora di
  Upbit all'entrata), il risultato a 1, 3 e 14 giorni senza l'uscita di protezione, il risultato per anno, quante uscite di
  protezione e quanti eventi si sovrappongono a N3 (moneta con meno di 37 giorni di perpetuo).
