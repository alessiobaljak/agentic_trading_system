# Programma 7 — prova 152: il limite alla concentrazione di G1 (voce 13 di `MIGLIORARE_G1.md`)

Scritta il 12 novembre 2026, **prima di ogni calcolo**: nessun risultato è stato guardato. Le regole le committa la sessione principale;
la prova la esegue poi strategy-improver (secondo giro), il giudizio su ciò che passa lo dà backtest-auditor. Nasce dalla revisione di G1
del 12 novembre (`audits/reports/2026-11-12-G1_CONTO_VERO.md`, problema 3): una moneta arriva al 43,7% del capitale (BLZ venduta, 5 febbraio
2024), 65 giorni-moneta costano più del 3% del capitale, e il 5 febbraio 2024 lo short era sceso a 5 monete (voce 13).

**Questa prova non spegne e non sostituisce niente.** G1 resta com'è (paper e demo). Una variante che passa entra **accanto**, mai al suo
posto; sostituire G1 lo decide solo Alessio. `DRY_RUN` resta vero.

## 1. La base: G1 com'è
`PRIMA.md` + `revisione_g1n/nucleo.py`: ogni giorno alle 00:00 UTC, le 100 monete più scambiate, segnale = meno il funding dei 7 giorni,
banda 20%/40%, pesi secondo l'inverso della volatilità a 30 giorni, ogni lato al 100% (esposizione 2), ordine limite per un'ora e poi a
mercato. Periodo dal 4 gennaio 2021 al 4 ottobre 2026. Costi confermati dal proprietario il 7 novembre: 0,05% a mercato, 0,02% a limite;
scarto di prezzo 0,01% su BTC, ETH, SOL e 0,02% sulle altre; funding vero. Il riferimento è il ricalcolo di G1 con lo stesso codice
(la revisione dà Sharpe 1,98, discesa settimanale −28,8%): ogni confronto è con quel ricalcolo, non con un numero a memoria.

## 2. Perché la prova 61 non basta
La prova 61 (G1T, `QUINTA.md`) ha messo un **tetto del 10% per moneta e per lato**: Sharpe 1,87 contro 1,96, discesa −32,6% contro −28,8%,
bocciata perché sposta peso dalle monete calme a quelle agitate. Con ~20 monete per lato un tetto al 10% **morde ogni giorno** su molte
monete: cambia il carattere della strategia. Il problema vero è un altro e **raro**: i giorni in cui il lato ha poche monete (funding
uguale, rango a pari merito) e una sola pesa quasi tutto. Le varianti qui sotto agiscono su quei giorni e quasi non toccano gli altri.
In `tetto_lato` con meno monete del necessario per rispettare il tetto i pesi diventano uguali: questo non è un limite al peso massimo di
una moneta sul capitale se il lato è piccolo, perciò il minimo di monete e la riduzione dell'esposizione sono la parte nuova.

## 3. Le tre varianti (fissate qui, nessuna ricerca dei valori)
Per ogni lato, «n» = monete scelte da G1 quel giorno. Universo e periodo sono quelli del codice di G1: universo fissato per settimana come
`nucleo.universo_giorni`; periodo da `INIZIO` a `FINE` della prova 148 (`an.INIZIO`, `an.FINE`, fine esclusa); esposizione di G1 con i lati
fissi a 1 e 1.

* **V1, tetto 20%**: con n di almeno 5, nessuna moneta pesa più del 20% del suo lato (`nucleo.tetto_lato(w, 0.20)`). Con n sotto 5 **`tetto_lato`
  non si chiama** (con n per 20% sotto 1 metterebbe pesi uguali e cambierebbe l'esposizione): il lato resta com'è.
* **V2, almeno 10 monete per lato, solo nei giorni rari**: la banda di G1 resta **identica** (rango con le medie nei pari merito, come
  `passo_banda`); i giorni normali non cambiano. Solo quando un lato ha n sotto 10 lo si completa con le monete successive nel rango del
  segnale, fino a 10. **Solo lì** i pari merito si rompono con il volume medio in USDT dei 30 giorni prima (`quote_volume` del pannello di
  `research.programma6.seconda`, più alto prima, dato fino a ieri), poi con il simbolo in ordine alfabetico. Pesi con l'inverso della
  volatilità, lato al 100%. **Le monete aggiunte valgono solo per quel giorno**: non entrano negli insiemi che portano la banda al giorno
  dopo. Con l'universo sotto le 20 monete o con il rango che non basta, il lato resta com'è e il giorno si scrive nei risultati. Nel conto
  a 280 USDT, una moneta aggiunta senza filtri di Binance non si aggiunge, e si scrive.
* **V3, minimo 10 con esposizione ridotta, più tetto**: con n sotto 10 i pesi del lato si moltiplicano per n/10 (nessun completamento). Il
  tetto del 20% vale **sul lato già ridotto** (con n di almeno 5, `tetto_lato` applicato al lato ridotto, tetto = 20% del lato ridotto); con
  n sotto 5 vale solo il fattore n/10 e `tetto_lato` non si chiama.

## 4. Il conto
Ogni variante gira con lo stesso codice di G1 (`nucleo.pesi` con la regola in più). Due conti:
1. **Periodo di G1, spese confermate, senza minimi** (come il paper).
2. **A 280 USDT con i minimi di Binance** (motore della prova 148, `ottantaseiesima.py`, filtri `filtri_binance_2026-11-06.json`, capitale
   fisso). Devono rispettare «ogni anno positivo» e il criterio sullo Sharpe **il conto A** (come lo fa il bot oggi) **e il conto A2** (con le
   chiusure permesse); il riferimento è lo stesso conto (A o A2) di G1 con lo stesso motore. Gli ordini saltati per i minimi si contano con
   il contatore `ordini_saltati` del motore.
Sharpe e t: serie **settimanale**, `nucleo.numeri` con `per_anno=52`; t = media / (deviazione standard / radice del numero di settimane).

## 5. Il criterio (di rischio, uno solo e coerente sul peso)
**Misura**: il peso della moneta venduta più pesante, in % del capitale, preso sui **pesi voluti all'apertura** di ogni giorno (le posizioni con
la deriva dei prezzi si riportano a parte, senza decidere). Un rialzo del 100% su una moneta venduta costa esattamente quel peso: la perdita da
+100% e il peso sono la stessa misura, quindi **un solo limite: al massimo il 20% del capitale in ogni giorno** (G1: 43,7%, e anche per le
comprate si riporta il massimo, senza decidere). In V3 il tetto vale sul lato già ridotto.
Per costruzione: **V1** può passare il limite con n di almeno 5 ma **non** con n sotto 5 (lato intatto, fino al 100% di una sola moneta): il
passaggio dipende dai giorni rari. **V2** **non** passa per costruzione (nessun tetto: la moneta con la volatilità più piccola può pesare di
più del 20%). **V3** passa per costruzione con n di almeno 5 (al massimo 20% del lato ridotto, cioè al massimo il 20% del capitale); con n
sotto 5 il peso può arrivare a n/10 del capitale, cioè fino al 40%, e va misurato.

Una variante passa se, **sul conto 1**, sono tutte vere:
* peso massimo della venduta più pesante al massimo **20% del capitale** in ogni giorno;
* **Sharpe** settimanale che scende al massimo di **0,15** rispetto al ricalcolo di G1, **discesa settimanale più grande** peggiore al massimo
  di **3 punti**;
* **ogni anno positivo** (2021-2026) e **t almeno 3**.
E sul **conto 2** (A e A2, 280 USDT): ogni anno positivo, Sharpe che scende al massimo di 0,15 dal riferimento omonimo, ordini saltati non più
numerosi di quelli di G1 con lo stesso conto.
Si riportano, senza decidere: giorni con n sotto 10 per lato, Sortino, rendimento, spese, giro, il confronto con la prova 61. **Giorni-moneta
oltre il 3%**: giorni in cui una moneta venduta costa al conto più del 3% del capitale in quel giorno; **prima si riproduce il 65 di G1** con
questa definizione, poi si calcolano le varianti. Se non torna, si scrive e ci si ferma.
I numeri 20%, 0,15 e 3 punti sono fissati qui e non si cambiano dopo aver visto i risultati: 20% è circa metà del caso peggiore di G1; 0,15
è il margine oltre il costo di Sharpe della prova 61 (0,09).

## 6. Il conto delle prove
Entrano **3 varianti** nel conto delle prove: oggi **309 → 312**. Lo Sharpe corretto si calcola con il metodo dell'11 novembre, contando le
**famiglie di prove simili** (`research/programma6/asticella.py`); le tre varianti sono **una famiglia** (limite alla concentrazione, con la
prova 61), e il conto per famiglie si scrive nel risultato accanto a quello per prova. Passare il criterio di rischio **non** vuol dire passare
l'asticella dello Sharpe corretto: la variante che passa va a backtest-auditor, che giudica anche quello.

## 7. Cosa si consegna
`RISULTATI_NOVANTESIMA.md` (tabella: G1, V1, V2, V3 sul conto 1 e sul conto 2, con ogni voce del criterio e l'esito), il codice in
`novantesima.py` (mai nel bot), ogni variante registrata in `research/trials/` **anche se fallisce**. Eventuali giorni senza abbastanza
monete nel rango: si scrivono, non si inventa. Se la regola chiede di spegnere o cambiare G1 nel paper o nel demo: ci si ferma.

## Regole corrette il 12 novembre 2026 dopo la verifica, prima di ogni calcolo
Corretto: (1) sotto 5 monete V1 e V3 non chiamano `tetto_lato`, V3 usa solo n/10; (2) V2 lascia identici i giorni normali, completa solo sotto
10 monete e i pari merito (volume 30 giorni, poi alfabeto) valgono solo lì; (3) le monete aggiunte da V2 valgono un giorno, universo sotto 20 o
rango insufficiente: lato com'è e giorno scritto; (4) un solo criterio sul peso (20% del capitale, pesi voluti all'apertura, V3 sul lato ridotto)
e per ogni variante se passa per costruzione; (5) Sharpe e t settimanali con `numeri(per_anno=52)`; (6) definizione unica dei giorni-moneta oltre
il 3% e riproduzione del 65 prima; (7) conti A e A2 a 280 USDT, contatore `ordini_saltati`, monete senza filtri non aggiunte; (8) universo e
periodo del codice di G1, lati fissi a 1 e 1.
