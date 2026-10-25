# Programma 7 — venticinquesima prova: il premio di Coinbase fra le monete (PC)

Scritto il 25 ottobre 2026, alle 04:50 UTC, **prima di scaricare le candele di Coinbase delle monete e prima di qualunque calcolo**
(l'unico dato di Coinbase già scaricato è BTC-USD, prova 72, e l'elenco dei mercati con il primo giorno). Idea 47 della coda di
`research/REGISTRO.md`.

## 1. Perché, e il dubbio

Coinbase è l'exchange degli investitori americani a pronti; il prezzo di una moneta su Coinbase rispetto a Binance (il «premio») dice
dove sta spingendo la domanda americana. Sul Bitcoin da solo il premio non batte il Bitcoin tenuto (prova 72). **Fra le monete** è
un'altra cosa: il premio comune a tutte (il cambio dollaro/USDT) sparisce con il rango, e resta la domanda relativa moneta per
moneta; una domanda a pronti persistente per una settimana è un flusso lento, che dovrebbe continuare a spingere la settimana dopo
(come il denaro che entra nelle prove 9 e 11, che continuava). **Il dubbio scritto prima**: l'arbitraggio fra exchange chiude il premio
in minuti, e la media su 7 giorni potrebbe misurare solo differenze di liquidità fra i mercati, non domanda; probabilità bassa-media.

## 2. I dati

* Le candele a **1 ora** dei mercati `MONETA-USD` di Coinbase per le monete che hanno anche il perpetuo USDT su Binance (306 in
  comune; 129 quotate su Coinbase prima del 2024, 115 prima del 2023), dal 1° gennaio 2023 al 5 ottobre 2026, dall'API pubblica
  di Coinbase (`api.exchange.coinbase.com`, 300 candele per richiesta), salvate in `research/data/coinbase/ore_<MONETA>-USD.csv.gz`
  con l'impronta; le candele a 1 ora di Binance già in archivio (`esecuzione.ore_di`).
* Monete con il prefisso dei multipli su Binance (1000PEPE ecc.): il premio si calcola con il prezzo diviso per il multiplo.

## 3. La regola (valori fissati qui)

* **Universo**: le 100 monete della settimana (come F5) che hanno il mercato su Coinbase con almeno **100 ore** di premio nei 7
  giorni prima del lunedì; se sono meno di **20**, la settimana resta fuori (si conta).
* **Segnale al lunedì**: la media del premio orario (chiusura Coinbase / chiusura Binance − 1) dei 7 giorni prima.
* **Portafoglio come F5**: long le monete che entrano nel 20% con il premio più alto e restano finché sono nel 40% più alto, short
  lo stesso dal basso; pesi secondo l'inverso della volatilità dei 30 giorni; costi e funding come F5 (`seconda.costi_moneta`).
* Dal **2 gennaio 2023** al 5 ottobre 2026. Una prova: nel conto diventano **154**.

## 4. L'esame

`terza.esame` dal 2 gennaio 2023 (anni pieni 2023-2025), Sharpe corretto con l'aggiunta e il t, la decisione del proprietario del 24
ottobre; correlazione con F5 sulle stesse settimane; quante monete per settimana; il verso opposto e il premio medio solo per capire.
