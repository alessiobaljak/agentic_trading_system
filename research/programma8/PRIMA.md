# Programma 8 — prima prova: il lato long di F5 a pronti (S1 a settimana, S2 ogni giorno)

Scritto il 24 ottobre 2026, **prima del calcolo**.

## 1. La regola (valori fissati qui)

* **Le monete**: quelle dell'universo di F5 della settimana (le 100 più scambiate nei future) che hanno la coppia contro USDT a
  pronti su Binance con il prezzo e il volume della domenica (per S2: del giorno prima).
* **Il segnale**: −funding dei 7 giorni dei future (come F5, `sesta.funding_7` con le parità corrette).
* **S1**: ogni lunedì alle 00:00 UTC, si comprano a pronti le monete nel 20% con il segnale più alto e si tengono finché non escono
  oltre il 40% (la banda di F5, solo il lato long); pesi secondo l'inverso della volatilità dei 30 giorni; tutto il capitale
  investito, niente vendite allo scoperto, niente leva. **S2**: lo stesso deciso ogni giorno alle 00:00 UTC.
* **Prezzi**: le candele giornaliere a pronti (apertura → apertura dopo). **Costi**: 0,10% di commissione più lo scarto (0,01%
  BTC, ETH, SOL; 0,02% le altre) su ogni variazione di peso; niente funding.
* **Confronti** (sulle stesse settimane): il **paniere** di tutte le monete dell'universo a pronti con gli stessi pesi (1/volatilità,
  la stessa regola senza la scelta), il Bitcoin tenuto, e il lato long di F5 nei future.
* Dal 4 gennaio 2021 al 4 ottobre 2026. Due prove: nel conto diventano **139**.

## 2. L'esame

`terza.esame` e `terza.esito` sulle settimane (anche «più del Bitcoin»), Sharpe corretto con l'aggiunta del 23 ottobre, soglia
0,95. In più, per capire se la scelta delle monete aggiunge qualcosa: il rendimento **in più del paniere** (S1 − paniere) con il suo
intervallo.
