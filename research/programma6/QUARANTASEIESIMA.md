# Programma 6 — quarantaseiesima prova: le strategie già pronte di TradingView, così come sono

Scritto il 21 ottobre 2026, sera, **prima di qualunque calcolo**, su richiesta del proprietario: «fai tu l'elenco delle più
usate e provale». Idea 17 della coda di `research/REGISTRO.md`.

## 1. L'elenco (fonte: TradingView, scritto prima)

Non c'è un elenco pubblico delle strategie più usate su TradingView. L'elenco oggettivo è quello delle **strategie già
pronte di TradingView** («Built-in Strategies», la sezione di supporto
`tradingview.com/support/folders/43000587406-built-in-strategies/`, letta il 21 ottobre 2026): sono le 20 strategie che
chiunque trova di serie nello Strategy Tester, e da cui parte quasi ogni script della comunità. Con i **valori di serie**
(quelli che si vedono aprendo la strategia, senza toccare niente):

| # | Strategia | Regola (alla chiusura della candela; si opera alla candela dopo) | Ordine |
|---|---|---|---|
| 1 | BarUpDn | long se chiusura > apertura e apertura > chiusura prima; short al contrario | a mercato |
| 2 | Bollinger Bands | media 20, 2 deviazioni; chiusura che rientra sopra la banda bassa → long; che scende sotto la banda alta → short | stop al livello della banda, valido una candela |
| 3 | Bollinger Bands Directed | uguale alla 2 con la scelta del verso; di serie entrambi i versi: **è la 2**, non si conta due volte | — |
| 4 | Channel BreakOut | 5 candele: compra sopra il massimo + 1 scatto, vende sotto il minimo − 1 scatto (codice sulla pagina di supporto) | stop, sempre attivi |
| 5 | Consecutive Up/Down | 3 chiusure in salita di fila → long; 3 in discesa → short | a mercato |
| 6 | Greedy | **esclusa**: il codice non è sulla pagina e non lo so riprodurre con esattezza | — |
| 7 | InSide Bar | candela dentro la precedente: verde → long, rossa → short | a mercato |
| 8 | Keltner Channels | media esponenziale 20 ± 2 ATR(10); chiusura sopra la banda alta → compra sopra il massimo di quella candela finché la chiusura non torna sotto la media; al contrario per lo short | stop |
| 9 | MACD | 12, 26, 9: l'istogramma passa sopra zero → long; sotto → short | a mercato |
| 10 | Momentum | 12: momento e sua variazione positivi → compra sopra il massimo; negativi → vende sotto il minimo | stop, una candela |
| 11 | OutSide Bar | candela che contiene la precedente: verde → long, rossa → short | a mercato |
| 12 | Parabolic SAR | 0,02, 0,02, 0,2: si gira al SAR | stop al SAR |
| 13 | Pivot Extension | pivot a 4 candele a sinistra e 2 a destra: minimo confermato → long, massimo → short | a mercato |
| 14 | Pivot Reversal | 4 e 2: compra sopra l'ultimo massimo di pivot, vende sotto l'ultimo minimo | stop |
| 15 | Price Channel | 20 candele: compra al massimo, vende al minimo | stop, sempre attivi |
| 16 | RSI | 14, 30, 70: l'RSI risale sopra 30 → long; scende sotto 70 → short | a mercato |
| 17 | Stochastic Slow | 14, 3, 3, 80, 20: incrocio di %K sopra %D sotto 20 → long; sotto %D sopra 80 → short | a mercato |
| 18 | Supertrend | ATR 10, fattore 3: cambia verso → si gira | a mercato |
| 19 | Technical Ratings | **esclusa**: unisce 26 indicatori con regole interne che non sono pubblicate per intero (l'unione di molti indicatori è già nella prova 3) | — |
| 20 | Volty Expan Close | 5 candele, 0,75: compra sopra chiusura + 0,75 × media del range vero, vende sotto chiusura − 0,75 × … | stop, una candela |

Restano **17 strategie**. Tutte, come su TradingView, **girano la posizione** (da long a short e viceversa) e stanno quasi
sempre a mercato. Riserva: il codice di serie si vede solo nell'editor di TradingView; le regole qui sopra vengono dalle
pagine di supporto e dal codice di serie (Pine 5) come è noto; nei dettagli minori può differire.

## 2. Come si provano (valori fissati qui)

* **Monete**: l'universo della settimana (le 100 più scambiate, dati corretti), dal 4 gennaio 2021 al 10 ottobre 2026; una
  moneta che esce dall'universo chiude la posizione.
* **Candele**: **4 ore** e **1 giorno**, le più usate per il crypto a più giorni. 17 × 2 = **34 prove** nel conto: diventano
  **104**.
* **Capitale**: diviso in parti uguali fra le monete dell'universo; ogni strategia è long o short **100%** della sua parte
  (come lo Strategy Tester con il 100% del capitale), senza leva in più.
* **Esecuzione**: a mercato all'apertura della candela dopo; gli ordini stop si eseguono quando la candela dopo tocca il
  livello, al livello (o all'apertura, se apre già oltre). Se nella stessa candela si toccano tutti e due gli stop, vale quello
  più vicino all'apertura.
* **Costi veri di Binance**: commissione 0,05% più lo scarto (0,01% BTC, ETH, SOL; 0,02% le altre) per ogni variazione della
  posizione (girare da long a short costa il doppio); il funding di ogni candela con il segno della posizione. Si riporta anche
  il risultato **senza costi** (com'è di serie lo Strategy Tester), per vedere la differenza.

## 3. L'esame

Per ognuna delle 34: `terza.esame` e `terza.esito` (intervallo sopra zero, Sharpe corretto sulle **104** prove almeno 0,95,
4 anni su 6, ultimo anno, costi doppi, trimestri, più del Bitcoin). Si riportano anche il numero di operazioni, la quota
vinta e il risultato senza costi.
