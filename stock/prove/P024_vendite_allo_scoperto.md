# Prova 24 — le azioni più vendute allo scoperto (giorni per ricomprarle), con la soglia larga

Regole scritte l'11 novembre 2026 **prima di qualsiasi calcolo** su questi dati, committate prima di lanciare il programma. Idea portata
dalla sessione delle crypto e girata dal proprietario: «le posizioni affollate, che sono la ragione economica di G1 [...] le azioni più
vendute allo scoperto, o più care da prendere a prestito, tendono a fare peggio»; con «la soglia larga per entrare e uscire, come in G1
[...] abbinata a meno peso ai titoli che oscillano di più» e «il controllo dei dati: l'ultimo giorno si usa solo se è completo». Si
conoscevano le prove 1-23 (tutte bocciate) e il fatto che i dati di FINRA esistono dal 2018. Famiglia nuova (posizioni affollate): il
periodo chiuso si può aprire una volta. Contano come **2 prove**.

## Perché dovrebbe funzionare

Chi vende allo scoperto è in media informato: le azioni con molte vendite allo scoperto rendono meno dopo (Asquith, Pathak, Ritter,
*Journal of Financial Economics* 78, 2005; Boehmer, Jones, Zhang, *Journal of Finance* 63, 2008). La misura migliore non è la quota
delle azioni in circolazione ma **i giorni per ricomprarle** (vendute allo scoperto / volume medio giornaliero): Hong, Li, Ni, Scheinkman,
Yan, «Days to cover and stock returns» (NBER 21166, 2015). È lo stesso meccanismo di G1: chi sta dalla parte affollata paga. **Sospetto
scritto prima:** l'effetto è molto più forte nelle aziende piccole e difficili da prendere a prestito, dove venderle costa caro (Engelberg,
Reed, Ringgenberg, *Journal of Finance* 73, 2018); nell'S&P 500 quasi tutte le azioni si prendono a prestito a poco, e il vantaggio può
essere piccolo; i dati del costo del prestito non sono pubblici nel passato (si misureranno solo in avanti).

## I dati

* **Le vendite allo scoperto:** FINRA, due date al mese (`stock/dati/finra.py`), dal 2018. Per ogni titolo e data di regolamento, i
  **giorni per ricomprarle** di FINRA (`daysToCoverQuantity`). **Si usano solo 10 giorni di borsa dopo la data di regolamento** (FINRA
  pubblica dopo circa 7: margine di prudenza contro lo sguardo nel futuro).
* **Il controllo dei dati (punto 3 della sessione crypto):** una data di FINRA si usa solo se ha i giorni per ricomprarle per almeno il
  90% dei titoli che li avevano nella data prima, fra i membri dell'indice; altrimenti si usa la data prima. Allo stesso modo un giorno
  di decisione si usa solo se almeno il 90% dei membri dell'indice ha la barra di quel giorno; altrimenti si salta al giorno dopo.
* **Prezzi:** al giorno di Alpaca non rettificati, con dividendi, frazionamenti e scissioni applicati dal simulatore a più titoli; i
  membri dell'S&P 500 di ogni giorno con i cambi di simbolo (come la prova 11).

## Le regole

**Ogni mese**, all'ultimo giorno di borsa, con l'ultima data di FINRA utilizzabile; ordini a mercato all'apertura del giorno dopo.

* **La classifica:** i membri dell'S&P 500 di quel giorno con i giorni per ricomprarle, dal più alto al più basso.
* **La soglia larga (punto 2):** un titolo **entra** fra le vendite allo scoperto quando è nel 20% più alto della classifica; **esce**
  solo quando scende sotto il 40% più alto. Per gli acquisti (solo variante A) lo specchio: entra nel 20% più basso, esce sopra il 40% più
  basso.
* **I pesi (punto 2):** dentro ogni lato, peso proporzionale a 1 / volatilità (deviazione standard dei rendimenti giornalieri delle 63
  sedute prima), normalizzato perché il lato sommi alla sua quota.

**Variante A — lungo e corto:** 50% del conto comprato nei titoli con meno giorni per ricomprarle, 50% venduto allo scoperto in quelli con
più giorni. Il resto in contanti a rendimento zero.

**Variante B — l'indice meno gli affollati:** 100% del conto nello SPY e 30% venduto allo scoperto nei titoli con più giorni per
ricomprarle (leva lorda 1,3).

* **Periodo:** decisioni dalla prima fine mese con una data di FINRA utilizzabile (con il margine) al 31 dicembre 2024. *(Corretto
  l'11 novembre prima del calcolo: lo scaricamento mostra che i dati partono da gennaio 2018, non da giugno.)* Il periodo chiuso
  (gennaio 2025 → settembre 2026) non si tocca.

## I costi

Come la prova 11: metà della mediana dello scarto misurato per i 34 titoli misurati, per gli altri metà scarto 5 punti base e 2 di
slittamento; commissioni Interactive Brokers «fisso»; **prestito delle azioni vendute allo scoperto 0,5% l'anno** (costo tipico dei titoli
facili da prendere a prestito; nel passato non c'è il dato vero, si dice); interesse sul debito della leva della variante B al 5% l'anno;
costi raddoppiati per la condizione 3.

## L'esame

Per ogni variante: (1) Sharpe annuo con i costi più alto del tenere lo SPY sugli stessi giorni; (2) Sharpe corretto ≥ 0,95 con tutte le
serie del conto; (3) Sharpe sopra zero con i costi doppi; (4) almeno il 60% dei trimestri di prova in guadagno. Accanto, da leggere: il
rendimento del solo lato corto contro lo SPY (il cuore dell'idea), quante operazioni fa la soglia larga rispetto a una soglia stretta
(20% dentro, 20% fuori, solo contata, non per scegliere). Se passa: revisore separato, poi il periodo chiuso una volta, poi il demo di
Alpaca con il costo vero del prestito.
