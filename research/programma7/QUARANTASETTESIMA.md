# Programma 7 — quarantasettesima prova: il trading a griglia (GR)

Scritto il 26 ottobre 2026, alle 06:29 UTC, **prima di qualunque calcolo**. Strategia 30 del documento del proprietario del 26 ottobre
(«strategie grid backtested su coppie laterali hanno mostrato rendimenti annualizzati del 15-30% al netto delle commissioni»). Mai provata.

## 1. Perché, e il dubbio

Una griglia mette ordini di acquisto sotto il prezzo e di vendita sopra, a distanze fisse: ogni volta che il prezzo scende di un gradino e
risale, guadagna la distanza fra i due ordini, con ordini limite (commissione bassa). Guadagna quando il prezzo oscilla e perde quando va
in una direzione sola (resta con le monete comprate in discesa, o fuori in salita). **Il dubbio scritto prima**: il documento dice «su
coppie laterali», cioè scelte dopo aver visto che erano laterali; una griglia è una vendita di volatilità (guadagna poco spesso e perde
tanto nelle tendenze), e il suo rendimento va separato da quello che fa la moneta (la griglia «lunga» tiene monete). Probabilità bassa.

## 2. La regola (valori fissati qui: quelli tipici dei programmi a griglia delle borse)

* **Monete e periodo**: BTC, ETH, SOL, XRP, DOGE, BNB; dal 1° gennaio 2024 al 30 settembre 2026; candele a 1 minuto.
* **La griglia**: 21 livelli geometrici dal −10% al +10% del prezzo d'inizio (passo 1,0%: (1,1)^(1/10) − 1 ≈ 0,96%, fissato così), un ordine
  per livello; quando un acquisto al livello k si esegue, si mette la vendita al livello k+1, e viceversa.
* **Due versioni**: **GR-L, la griglia lunga** (come a pronti: all'inizio si comprano le monete per gli ordini di vendita sopra il prezzo, 10
  quote; in fondo alla griglia se ne tengono 20), e **GR-N, la griglia neutra dei future** (all'inizio nessuna posizione: vende a ogni
  gradino in salita e compra a ogni gradino in discesa, al massimo 10 quote per lato).
* **Fuori dall'intervallo** (il prezzo supera il livello estremo di un altro gradino): si chiude tutto a mercato e si riparte con una griglia
  nuova centrata sul prezzo di quel momento, con il conto di quel momento.
* **Esecuzione prudente**: in ogni minuto si eseguono solo gli ordini da una parte (acquisti se il minuto chiude sotto l'apertura, vendite
  se chiude sopra), toccati dal minimo o dal massimo del minuto.
* **Costi**: ordini della griglia a limite (0,02%); chiusure alla ripartenza a mercato (0,05% più lo scarto); funding vero per la griglia
  neutra e per la lunga (perpetui), giorno per giorno sulla posizione.
* **Dimensione**: GR-L con il valore delle 20 quote uguale al conto; GR-N con le 10 quote per lato uguali al conto.
* Due prove nel conto (GR-L, GR-N): **196**.

## 3. L'esame

Il portafoglio delle 6 griglie con lo stesso peso, a settimana: `terza.esame`, Sharpe corretto rivisto, t, la regola del proprietario; e
**il rendimento oltre quello che fa la moneta** (la pendenza dei rendimenti giornalieri della griglia su quelli della moneta: la parte che
resta, l'anno). Si riportano per moneta, per anno, quante ripartenze, e il confronto con il tenere le monete.
