# Programma 6 — ottava prova: il funding fra monete con i pesi secondo la volatilità

Scritto il 19 ottobre 2026, sera, **prima di qualunque calcolo** di questa variante. Vale `SESTA.md` e `SETTIMA.md` dove
qui non si dice altro.

## 1. Perché

* In F2 (sesta prova) la parte **stabile** è il funding incassato, circa +40% l'anno in tutte le varianti descrittive
  (`robustezza_F2.md`); la parte **instabile** è il prezzo: +15% l'anno sulle 100 monete più scambiate, −10% sulle monete
  101-200 (settima prova), −0,81% a settimana nel 2020 (`F2_2020.md`).
* A pesi uguali, le monete più agitate pesano quanto le altre, e sono proprio quelle con il funding più estremo (le più
  affollate) e i rimbalzi più forti contro lo short. Il rimedio standard nella costruzione dei portafogli long-short è dare
  a ogni moneta un peso **inversamente proporzionale alla sua volatilità**: ogni posizione porta lo stesso rischio.
* Domanda: con lo stesso rischio per moneta, il funding resta e il prezzo pesa meno?

## 2. Le regole

* Come F2 (segnale: funding dei 7 giorni prima; long il quinto più basso, short il quinto più alto; lato long +1 e short
  −1), ma **dentro ogni lato il peso di ogni moneta è proporzionale a 1/σ**, con σ la deviazione standard dei rendimenti
  giornalieri dei 30 giorni prima del lunedì (almeno 20 giorni; senza, la moneta non entra).
* Una variante sola: **F3** (nel conto del programma 6 le prove diventano **27**).

## 3. Gli esami (tutti e due, nell'ordine)

1. **Sulle 100 monete più scambiate**, dal 4 gennaio 2021: l'esame della sesta prova (le sei condizioni della terza prova
   con lo Sharpe corretto sulle **27** prove).
2. **Conferma sulle monete 101-200**, con lo scarto 0,10%: l'esame della settima prova (le cinque condizioni, p ≤ 0,01).

F3 è **valida** solo se passa **entrambi**. Si riportano anche le settimane del 2020 (come `F2_2020.md`), senza condizione.
