# Prova 2 — uscita dalla «zona di rumore» dell'apertura (SPY, QQQ)

Regole scritte il 24 ottobre 2026 **prima di qualsiasi calcolo** su questa idea (idea I2 di `REGISTRO.md`, sezione 2), committate
prima di lanciare il programma. Prima di scriverle si conosceva solo il risultato della prova 1 (l'ultima mezz'ora, bocciata: il
vantaggio c'era ma era più piccolo dei costi).

## Perché dovrebbe funzionare

Un movimento che esce dalla fascia normale degli ultimi giorni, misurata minuto per minuto dall'apertura, indica uno squilibrio fra
domanda e offerta che tende a durare nella giornata: Zarattini, Aziz, Barbon, «Beat the Market: An Effective Intraday Momentum Strategy
for S&P500 ETF (SPY)», Swiss Finance Institute Research Paper 24-97 (2024). **Sospetto scritto prima:** il lavoro dichiara uno Sharpe
di 1,33 dal 2007, è recente, molto diffuso e non pubblicato su rivista; usa la leva fino a 4 volte. E dalla prova 1 sappiamo che sullo
SPY una giornata costa circa 0,7-1,7 punti base: questa regola può operare più volte al giorno.

## La regola (i numeri sono quelli del lavoro, nessuno scelto da noi)

* **Titoli:** SPY e QQQ, ognuno da solo. Contano come **2 prove** (in tutto 4 nel conto).
* **Periodo e barre:** come la prova 1 (4 gennaio 2016 → 31 dicembre 2024, minuti di seduta, prezzi non rettificati). Periodo chiuso
  non toccato.
* **La zona di rumore.** Per ogni giorno d e minuto k dall'apertura (k = 0 è la barra delle 9:30): il movimento m(d, k) = |chiusura
  della barra k / apertura della prima barra − 1|. Per oggi, σ(k) = media di m(·, k) nei **14 giorni di borsa precedenti** con seduta
  intera (solo giorni passati). Limite alto = max(apertura di oggi, chiusura di ieri) × (1 + σ(k)); limite basso = min(apertura di
  oggi, chiusura di ieri) × (1 − σ(k)).
* **Il prezzo medio del giorno (VWAP):** dall'apertura alla barra k, somma di (prezzo medio della barra × volume) / somma dei volumi,
  con il prezzo medio e il volume di Alpaca.
* **Le decisioni** si prendono solo alla chiusura delle barre che finiscono alle mezz'ore, dalle 10:00 alle 15:30 (12 volte al giorno),
  con la chiusura c di quella barra:
  * senza posizione: se c > limite alto si compra; se c < limite basso si vende allo scoperto;
  * comprati: si esce se c < max(limite alto, VWAP); se inoltre c < limite basso, si gira allo scoperto;
  * allo scoperto: si esce se c > min(limite basso, VWAP); se inoltre c > limite alto, si gira comprati.
* **Esecuzione:** a mercato all'apertura della barra dopo. **Fine giornata:** ogni posizione si chiude a mercato all'apertura
  dell'ultima barra della seduta (decisione alla chiusura della penultima), come nella prova 1. Niente posizioni di notte.
* **Quanto:** il 98% del valore del conto, azioni intere, **senza leva e senza il dimensionamento per la volatilità del lavoro**
  (lo Sharpe non dipende dalla leva; la leva è una decisione del proprietario). Ordine rifiutato per leva = contato.
* **Giorni esclusi:** i giorni di chiusura anticipata (la fascia di 14 giorni è misurata su sedute intere), il primo giorno, i giorni
  senza 14 sedute intere prima, i giorni segnalati dal controllo dei minuti (`stock/dati/ESITO_MINUTI.md`) e i giorni in cui manca la
  prima barra o la barra di una decisione.

## I costi e l'esame

**Identici alla prova 1** (`P001_ultima_mezzora.md`): metà della mediana dello scarto misurato, 0,5 punti base di slittamento,
commissioni Interactive Brokers «fisso» (da verificare), versione con i costi raddoppiati, capitale 100'000 dollari. Le stesse quattro
condizioni, tutte vere per passare: (1) Sharpe annuo con i costi più alto del comprare e tenere lo SPY; (2) Sharpe corretto ≥ 0,95
con il conto di tutte le prove delle azioni (le 2 della prova 1 e queste 2), gruppi per correlazione ≥ 0,5, V = 1/T sotto i 5 gruppi;
(3) Sharpe sopra zero con i costi doppi; (4) almeno il 60% dei trimestri di prova in guadagno. **In più** (dal `METODO.md`, sezione 1,
che la prova 1 non controllava per QQQ): lo Sharpe deve battere anche il comprare e tenere **lo stesso titolo** (SPY per lo SPY, QQQ
per QQQ).

## L'esame nel periodo chiuso (scritto il 24 ottobre 2026, dopo la revisione e prima di aprirlo)

Solo per QQQ (lo SPY è bocciato). Periodo: dal 2 gennaio 2025 al 30 settembre 2026. Stesso programma, stesse regole, stessi costi (lo
scarto è quello misurato sul 2016-2024, non lo si rimisura sul periodo chiuso prima del calcolo). Si apre **una volta sola**: il
risultato vale com'è, senza ritocchi. QQQ passa se sono vere **tutte**:

1. Sharpe annuo con i costi più alto di quello del comprare e tenere lo SPY e del comprare e tenere QQQ sugli stessi giorni (`METODO.md`,
   sezione 7: al demo va una strategia che batte l'indice dopo i costi).
2. Sharpe annuo con i costi raddoppiati sopra zero.
3. Almeno 4 trimestri su 7 in guadagno dopo i costi.

Se passa, la strategia può andare sul conto demo (quando ci sarà). Se non passa, è bocciata e si scrive nel registro.
