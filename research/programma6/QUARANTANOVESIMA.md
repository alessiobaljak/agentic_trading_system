# Programma 6 — quarantanovesima prova: il momento e la dimensione fra monete (X1, X2)

Scritto il 22 ottobre 2026, mattina, **prima del calcolo**. Idee 18 e 19 della coda di `research/REGISTRO.md`. È la prima prova
giudicata con l'asticella rivista (`ASTICELLA.md`).

## 1. Perché

Liu, Tsyvinski e Wu («Common Risk Factors in Cryptocurrency», *Journal of Finance* 2022) trovano che fra le criptovalute
contano tre fattori: il mercato, la **dimensione** (le monete più piccole rendono di più) e il **momento** (le monete salite di
più nelle tre settimane prima continuano a salire nella settimana dopo). Nel programma 6 il momento c'è solo dentro i modelli e
fra i 28 indicatori della prova 3, mai da solo; la dimensione mai. Si provano tutti e due fra le 100 monete più scambiate, con la
banda di F5 per i costi.

## 2. Le regole (valori fissati qui)

* **Monete**: l'universo della settimana (le 100 più scambiate, `terza.pannello_settimane`, dati corretti).
* **X1 — momento**: il rendimento dalla chiusura della domenica di 3 settimane prima alla chiusura della domenica prima del
  lunedì; **long** chi è salito di più, **short** chi è salito di meno.
* **X2 — dimensione**: la mediana del volume dei 30 giorni prima come misura della dimensione (non c'è la capitalizzazione);
  **long** le più piccole, **short** le più grandi.
* Per tutte e due la banda di F5 (`ventiquattresima.pesi_banda`: si entra nel 20% di testa o di coda, si esce oltre il 40%),
  pesi secondo l'inverso della volatilità dei 30 giorni, ogni lato al 100%; costi e funding come F5 (`terza.conto`).
* Dal 4 gennaio 2021 al 5 ottobre 2026. Due prove: nel conto diventano **109**.

## 3. L'esame

`terza.esame` e `terza.esito`, con lo Sharpe corretto **rivisto** (`asticella.py`: gruppi di prove simili a correlazione media
0,5, varianza degli Sharpe dei gruppi), soglia 0,95; si riportano anche il calcolo di prima, il t dello Sharpe, la correlazione
con F5 e il gruppo in cui cade ognuna.
