# Prova 4 — tenere solo di notte (SPY, QQQ)

Regole scritte il 24 ottobre 2026 **prima di qualsiasi calcolo** su questa idea (idea I4 di `REGISTRO.md`, sezione 2), committate
prima di lanciare il programma, e prima di conoscere l'esito della prova 3. Si conoscevano le prove 1 e 2 e il periodo chiuso della
prova 2 (nel 2025-2026 comprare e tenere SPY e QQQ ha avuto uno Sharpe di circa 1,05-1,09). Famiglia diversa dalla prova 2 (non segue
il movimento della giornata: tiene sempre e solo di notte): il periodo chiuso si può riusare.

## Perché dovrebbe funzionare

Il guadagno delle azioni americane arriva quasi tutto fra la chiusura e l'apertura del giorno dopo, mentre durante la seduta è vicino
a zero: Lou, Polk, Skouras, «A tug of war: overnight versus intraday expected returns», *Journal of Financial Economics* 134 (2019);
Cliff, Cooper, Gulen, «Return differences between trading and non-trading hours: like night and day» (2008). Una spiegazione è che di
notte si paga il rischio di tenere la posizione quando non si può vendere. **Sospetto scritto prima:** due operazioni ogni giorno;
dalla prova 1 sappiamo che sullo SPY un giro costa da circa 0,7 punti base (senza slittamento) a 1,7 (con): può mangiare tutto. E la
regola è investita solo di notte, quindi il suo Sharpe va confrontato con quello del tenere sempre.

## La regola (nessun parametro)

* **Titoli:** SPY e QQQ, ognuno da solo. **2 prove** (in tutto 8 nel conto, se la prova 3 ne conta 1).
* **Periodo e barre:** come la prova 1 (4 gennaio 2016 → 31 dicembre 2024, minuti di seduta dal calendario, prezzi non rettificati).
* **Ogni giorno di borsa:** alla chiusura della penultima barra della seduta (di solito le 15:58) si decide di comprare; l'ordine a
  mercato si esegue all'apertura dell'ultima barra (le 15:59). Alla chiusura dell'ultima barra si decide di vendere; l'ordine a mercato
  si esegue all'apertura della prima barra della seduta dopo (le 9:30, l'asta di apertura). Di giorno si resta fuori.
* **Dividendi:** il giorno di stacco il dividendo spetta a chi ha tenuto di notte; il simulatore lo accredita sulla prima barra di quel
  giorno, prima della vendita.
* **Quanto:** il 98% del conto, azioni intere, senza leva.
* **Giorni esclusi:** le notti in cui manca la barra dell'ingresso, della decisione o la prima barra del giorno dopo (l'ordine non si
  esegue e si resta comprati fino alla prima barra utile), e i giorni segnalati dal controllo dei minuti.

## I costi e l'esame

Come le prove 1 e 2: metà della mediana dello scarto misurato (SPY 0,185, QQQ 0,28 punti base), 0,5 punti base di slittamento,
commissioni Interactive Brokers «fisso» (da verificare), costi raddoppiati, capitale 100'000 dollari. **Prudenza:** le esecuzioni
sono a mercato con lo scarto anche se, nella realtà, si potrebbero usare gli ordini d'asta di chiusura e di apertura (senza scarto).

Passa la ricerca se sono vere **tutte**: (1) Sharpe annuo con i costi più alto del comprare e tenere lo SPY e del comprare e tenere lo
stesso titolo; (2) Sharpe corretto ≥ 0,95 con tutte le serie del conto; (3) Sharpe sopra zero con i costi doppi; (4) almeno il 60% dei
32 trimestri di prova in guadagno. Se passa: revisore separato, poi il periodo chiuso con l'esame della prova 2.
