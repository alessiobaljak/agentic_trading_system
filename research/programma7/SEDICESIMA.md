# Programma 7 — sedicesima prova: il premio di Coinbase sul Bitcoin (G14)

Scritto il 24 ottobre 2026, notte, **prima di scaricare i dati e prima del calcolo**. Un'idea nuova (in giornata, ogni giorno).

## 1. Perché

Il «premio di Coinbase» (il Bitcoin su Coinbase in dollari contro il Bitcoin su Binance in USDT) è uno degli indicatori più seguiti
dai trader: quando è positivo, chi compra negli Stati Uniti (anche i fondi, che passano da Coinbase) paga di più, e si dice che il
prezzo salga nelle ore e nei giorni dopo. Non l'abbiamo mai provato: è un dato che non avevamo (le candele di Coinbase sono pubbliche
e si scaricano da qui). Il premio comprende anche la differenza fra dollaro e USDT, come nell'indicatore che usano tutti.

## 2. La regola (valori fissati qui)

* **Dati**: candele da 1 ora del BTC-USD di Coinbase e del perpetuo BTCUSDT di Binance, dal 1 gennaio 2021 al 4 ottobre 2026.
* **Il premio di un'ora**: chiusura di Coinbase / chiusura di Binance − 1. **Il segnale del giorno**: la media del premio delle 24
  ore prima delle 00:00 UTC (almeno 20 ore con tutti e due i dati, altrimenti nessuna posizione).
* **L'operazione**: ogni giorno alle 00:00 UTC, **long** il Bitcoin (perpetuo di Binance) se il segnale è positivo, **short** se è
  negativo, per 24 ore, con tutto il capitale (nessuna leva). Si cambia solo quando cambia il segno.
* Costi: a mercato 0,05% più lo scarto dello 0,01% a ogni cambio di posizione (due volte quando si passa da long a short); funding
  vero del Bitcoin. Una prova: nel conto diventano **137**.

## 3. L'esame

I rendimenti giornalieri sommati per settimana, `terza.esame` e `terza.esito` (che chiede anche di fare più del Bitcoin tenuto),
Sharpe corretto con l'aggiunta del 23 ottobre, soglia 0,95. Si riportano il Bitcoin tenuto sulle stesse settimane, la quota di giorni
long, i cambi di posizione l'anno e il rendimento separato dei giorni long e short.
