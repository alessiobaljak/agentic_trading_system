# Programma 7 — undicesima prova: l'inversione di un giorno fra le monete 101-200, con gli ordini limite (G9)

Scritto il 23 ottobre 2026, **prima del calcolo**. Idea 31 della coda di `research/REGISTRO.md` (in giornata, ogni giorno).

## 1. Perché

Chi fornisce liquidità (compra da chi deve vendere in fretta, vende a chi deve comprare) viene pagato con il ritorno indietro dei
prezzi del giorno dopo: è l'inversione di breve periodo (Nagel 2012, *Review of Financial Studies*). Fra le cripto l'effetto
c'è soprattutto nelle monete meno liquide (Zaremba e altri 2021, oltre 3.600 monete; Bianchi, Babiak e Dickerson 2022), mentre fra
le più grandi il giorno dopo continua. L'idea era stata scartata (idea 24) perché a mercato i costi oltre le 100 monete sono troppi;
con gli ordini limite all'apertura il 95% si esegue e il costo scende a un terzo (prova 51). Si guadagna proprio facendo da
controparte, cioè con ordini limite.

## 2. La regola (valori fissati qui)

* **Monete**: le posizioni 101-200 per volume di ogni settimana (`terza.pannello_settimane(da=100, a=200)`, le regole di
  universo di sempre).
* **Ogni giorno alle 00:00 UTC**: il rendimento di ieri (apertura → apertura); **long** il 20% sceso di più, **short** il 20% salito
  di più; senza banda (l'effetto dura un giorno): ogni giorno i due lati si rifanno; pesi secondo l'inverso della volatilità dei 30
  giorni, ogni lato al 100%.
* **Esecuzione**: ogni variazione come ordine limite all'apertura delle 00:00 valido un'ora, poi a mercato alle 01:00 con il
  movimento contro (come G1, `cinquantaseiesima.spese_a_limite`); il costo a mercato di queste monete è 0,05% più lo scarto dello
  0,10% (come la prova 50); funding vero.
* Dal 4 gennaio 2021 al 4 ottobre 2026. Una prova: nel conto diventano **132**.

## 3. L'esame

`terza.esame` e `terza.esito` sulle settimane, Sharpe corretto con l'aggiunta del 23 ottobre, soglia 0,95; si riportano la quota di
ordini eseguiti a limite, le spese, il lordo prima dei costi e la versione tutta a mercato.
