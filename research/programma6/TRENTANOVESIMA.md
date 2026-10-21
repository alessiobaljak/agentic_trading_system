# Programma 6 — trentanovesima prova: la tendenza del giorno e il ritracciamento a 4 ore (T8)

Scritto il 21 ottobre 2026, mattina, **prima del calcolo**. Vale `TRENTAQUATTRESIMA.md` (monete, candele a 4 ore, costi,
funding, esame) dove qui non si dice altro.

## 1. Perché

Le prove 34-38 dicono: a 4 ore entrare sulla rottura vuol dire comprare tardi (il long perde), entrare contro gli eccessi
vuol dire andare contro la tendenza (lo stop scatta una volta su due). Il modo classico dei trader è la combinazione: si
sceglie il verso con la **tendenza del giorno** e si entra sul **ritracciamento** a 4 ore, cioè si compra un calo dentro una
salita (e si vende un rimbalzo dentro una discesa). Il funding toglie i casi in cui il verso è affollato.

## 2. La regola (valori fissati qui)

* **Tendenza del giorno**: la chiusura del giorno prima sopra la sua media dei **50 giorni** → solo long; sotto → solo short.
* **Ritracciamento a 4 ore**: long quando l'RSI a 14 candele da 4 ore passa sotto **35** (dentro la salita); short quando
  passa sopra **65** (dentro la discesa).
* **Funding**: long solo se il funding dei 7 giorni non è nel 40% più alto dell'universo (i long non sono affollati); short
  solo se non è nel 40% più basso.
* **Entrata** all'apertura della candela dopo; **uscite**: stop a 2 ATR, uscita mobile a 3 ATR dalla chiusura migliore (si
  segue la tendenza), al massimo 42 candele.
* Una prova: nel conto del programma 6 diventano **62**.

## 3. L'esame

Come la prova 34: per operazione (media sopra zero con **p ≤ 0,01**, bootstrap sulle settimane d'entrata, due metà, senza le
5 migliori) **e** come portafoglio (5% a operazione, al massimo 20 aperte; Sharpe corretto sulle **62** prove). Long e short
separati.
