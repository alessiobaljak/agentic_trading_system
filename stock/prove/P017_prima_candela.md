# Prova 17 — la direzione della prima candela dopo l'apertura (5 e 15 minuti, SPY e QQQ)

Regole scritte il 25 ottobre 2026 **prima di qualsiasi calcolo** su questa idea (idea I19, del proprietario: «un trader che analizza
gli indicatori nei 5/15 minuti subito dopo l'apertura del mercato per capire la direzione e poi faceva l'ordine»), committate prima di
lanciare il programma. Famiglia: regole in giornata che seguono il movimento dell'apertura, la **stessa della prova 2** (la zona di
rumore): il periodo chiuso per questa famiglia è già stato usato dalla prova 2, quindi **non si può riusare**; se una variante passa la
ricerca, la conferma sarà il demo, non il periodo chiuso. Contano come **4 prove** (5 e 15 minuti × SPY e QQQ).

## Perché dovrebbe funzionare

All'apertura arrivano tutti gli ordini accumulati nella notte: la direzione dei primi minuti dice da che parte sta lo squilibrio, che
spesso dura nella giornata. La regola precisa è quella di Zarattini e Aziz, «Can day trading really be profitable? Evidence of
sustainable long-term profits from opening range breakout (ORB) day trading strategy vs. benchmark in the US stock market» (SSRN 2023),
su QQQ. **Sospetto scritto prima:** è degli stessi autori della prova 2, che sul periodo chiuso non ha retto; usa la leva fino a 4 volte;
sulle crypto le regole di questo tipo perdevano dopo i costi; e sullo SPY un giro costa circa 0,7-1,7 punti base (prova 1).

## La regola (i numeri del lavoro)

* **Candela d'apertura** di N minuti (N = 5 e, a parte, N = 15): dalla barra delle 9:30 alla barra delle 9:30 + N − 1; apertura,
  massimo, minimo e chiusura dei suoi minuti.
* **Direzione:** se la candela chiude sopra la sua apertura si compra; se sotto, si vende allo scoperto; se uguale, niente.
* **Ingresso:** a mercato all'apertura della barra subito dopo la candela (le 9:35 o le 9:45), con il 98% del conto, azioni intere, senza
  leva.
* **Stop:** al minimo della candela per gli acquisti, al massimo per le vendite. Vale già nella barra dell'ingresso (al tocco; un'apertura
  oltre lo stop si paga tutta).
* **Obiettivo:** 10 volte il rischio (R = distanza fra il prezzo d'ingresso e lo stop), a ordine limite (solo se il prezzo passa oltre).
* **Fine giornata:** se né lo stop né l'obiettivo sono stati toccati, si esce a mercato all'apertura dell'ultima barra della seduta.
  Niente posizioni di notte.
* **Giorni esclusi:** le chiusure anticipate e i giorni segnalati dal controllo dei minuti; i giorni senza le barre della candela.
* **Periodo, barre e costi:** come le prove 1 e 2 (2016-2024, minuti di seduta, metà della mediana dello scarto misurato, 0,5 punti base
  di slittamento, Interactive Brokers «fisso», costi doppi).

## Le prove di robustezza (solo da leggere, non per scegliere)

Con le stesse regole, l'obiettivo a 5R, 20R e senza obiettivo (si esce solo con lo stop o alla chiusura), e il risultato anno per anno.
Servono a capire se il risultato dipende da un numero preciso (la regola buona ha un «altopiano», non un picco). Non si sceglie la
variante migliore: vale la regola principale (10R). Le varianti contano nel registro come prove viste.

## L'esame

Per ogni coppia (N, titolo): (1) Sharpe annuo con i costi più alto del tenere lo SPY e del tenere lo stesso titolo; (2) Sharpe corretto
≥ 0,95 con tutte le serie del conto; (3) Sharpe sopra zero con i costi doppi; (4) almeno il 60% dei 32 trimestri in guadagno. Se passa:
revisore separato, poi il demo (il periodo chiuso di questa famiglia è consumato).
