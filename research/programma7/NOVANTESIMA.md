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
Per ogni lato, «n» = monete scelte da G1 quel giorno.

* **V1, tetto 20%**: nessuna moneta pesa più del 20% del suo lato (`nucleo.tetto_lato(w, 0.20)`, l'eccesso va alle altre in proporzione).
  Se n è minore di 5 il lato resta com'è (nessuna correzione). Perché 20% e non 10%: morde solo nelle code (con n=20 il peso medio è 5%).
* **V2, almeno 10 monete per lato, completando dal rango**: se n è minore di 10, si aggiungono le monete successive nel rango del segnale
  (subito fuori dalla banda) fino ad arrivare a 10; pesi con l'inverso della volatilità, lato al 100%. **Pari merito nel rango**: chi ha
  lo stesso funding a 7 giorni (a 1e-12) si ordina per volume medio in USDT dei 30 giorni prima, più alto prima; se ancora pari, per simbolo
  in ordine alfabetico. La regola vale anche per chi sta già nella banda (taglio fra monete uguali: scelte con lo stesso ordine).
  L'ordine si decide col dato fino a ieri compreso, mai col futuro.
* **V3, minimo 10 con esposizione ridotta, più tetto**: se n è minore di 10 il lato non si completa: i suoi pesi si moltiplicano per n/10
  (esposizione del lato n/10 invece di 100%); poi tetto 20% come V1. Perché: tiene fuori dal conto le monete peggiori invece di prenderle
  per riempire; costa il funding di un lato ridotto nei giorni rari.

## 4. Il conto
Ogni variante gira con lo stesso codice di G1 (`nucleo.pesi` con la regola in più). Si fanno **due conti**:
1. **Periodo di G1, spese confermate, senza minimi** (come il paper).
2. **A 280 USDT con i minimi di Binance** (motore della prova 148, `ottantaseiesima.py`: filtri `filtri_binance_2026-11-06.json`, capitale fisso, il
   conto A come lo fa il bot oggi e A2 con le chiusure permesse). Il riferimento è G1 su 280 USDT con lo stesso motore (A: Sharpe 1,90).

## 5. Il criterio (di rischio, non «Sharpe più alto»)
Una variante passa se, **sul conto 1**, tutte queste sono vere:
* il **peso massimo di una moneta** in qualunque giorno è al massimo il **20% del capitale** (G1: 43,7%);
* la **perdita di un rialzo improvviso del 100%** sulla moneta venduta più pesante del giorno è al massimo il **15% del capitale** in ogni
  giorno (il peso massimo venduto, in frazione del capitale, al massimo 15%);
* lo **Sharpe** scende **al massimo di 0,15** rispetto al ricalcolo di G1 e la **discesa settimanale più grande** peggiora al massimo di 3
  punti;
* **ogni anno positivo** (2021, 2022, 2023, 2024, 2025, 2026) e t almeno 3.

E sul **conto 2** (280 USDT): ogni anno positivo, Sharpe che scende al massimo di 0,15 dal riferimento A, e gli ordini saltati per i minimi
non più numerosi di quelli di G1.
Si riportano anche (senza decidere): giorni con n minore di 10 per lato, giorni-moneta oltre il 3% del capitale (G1: 65), Sortino,
rendimento, spese, giro, e il confronto con la prova 61.
I numeri 20%, 15%, 0,15 e 3 punti sono fissati qui perché: 20% = metà del caso peggiore di G1, 15% = mezzo punto sopra il tetto che il
bot usa per un rischio per operazione (3% del capitale con stop di +20% circa), 0,15 = circa il costo di Sharpe che la prova 61 ha già
accettato di rischiare (0,09) più un margine. Non si cambiano dopo aver visto i risultati.

## 6. Il conto delle prove
Entrano **3 varianti** nel conto delle prove: oggi **309 → 312**. Lo Sharpe corretto si calcola con il metodo dell'11 novembre, contando le
**famiglie di prove simili** (`research/programma6/asticella.py`); le tre varianti sono **una famiglia** (limite alla concentrazione, con la
prova 61), e il conto per famiglie si scrive nel risultato accanto a quello per prova. Passare il criterio di rischio **non** vuol dire passare
l'asticella dello Sharpe corretto: la variante che passa va a backtest-auditor, che giudica anche quello.

## 7. Cosa si consegna
`RISULTATI_NOVANTESIMA.md` (tabella: G1, V1, V2, V3 sul conto 1 e sul conto 2, con ogni voce del criterio e l'esito), il codice in
`novantesima.py` (mai nel bot), ogni variante registrata in `research/trials/` **anche se fallisce**. Eventuali giorni senza abbastanza
monete nel rango: si scrivono, non si inventa. Se la regola chiede di spegnere o cambiare G1 nel paper o nel demo: ci si ferma.
