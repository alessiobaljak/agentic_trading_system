# Programma 6 — terza prova: la tendenza fra monete, da 28 indicatori tecnici (CTREND)

Scritto il 19 ottobre 2026, dopo la seconda prova (`RISULTATI_SECONDA.md`) e **prima di qualunque calcolo** di questa.
Vale tutto `METODO.md` e `SECONDA.md` (dati, universo al tempo giusto, costi) dove qui non si dice altro.

## 1. Cosa abbiamo imparato dalla seconda prova (fonte: `RISULTATI_SECONDA.md`, `risultati_seconda/`)

1. **La regola pubblicata di tendenza non regge come dichiarato.** Solo long sulle 20 monete più scambiate: Sharpe 0,53
   dal 2021 (gli autori dichiarano più di 1,5 sul 2015-2025); dopo l'uscita dell'articolo (aprile 2025) Sharpe 0,25.
2. **Sulle candele di 1 giorno nessuna delle nove famiglie passa.** La più regolare è l'incrocio delle medie (+0,097 R a
   trade, positiva in 5 anni su 5, intervallo −0,022; +0,228). La rottura del canale, quasi a zero sulle 4 ore con
   l'universo di oggi, diventa negativa con l'universo di allora (−0,128).
3. **Seguire il prezzo di una moneta da sola dà al massimo uno Sharpe intorno a 0,5** nel 2021-2026, sia nella prima
   prova sia nella seconda: troppo poco per l'esame (con 6 anni di dati serve circa 0,85 solo per l'intervallo sopra
   zero, di più per lo Sharpe corretto con 21 prove).
4. Quasi tutto il risultato delle prove sulla singola moneta va e viene con il mercato (2022 negativo, 2023-2024
   positivi). Il passo dopo, scritto in letteratura, è guardare la tendenza **relativa**: comprare le monete più forti e
   vendere le più deboli **insieme**, così il verso del mercato pesa poco.

## 2. Cosa si legge prima (19 ottobre 2026)

* **Fieberg, Liedtke, Poddig, Walker e Zaremba, «A Trend Factor for the Cross-Section of Cryptocurrency Returns»**,
  Journal of Financial and Quantitative Analysis (2025, doi 10.1017/S0022109024000747); testo letto dalla copia aperta
  dell'università Corvinus e l'appendice dal sito di Cambridge. Dati: oltre 3.000 monete, **aprile 2015 → maggio 2022**.
  28 indicatori tecnici (RSI, stocastici, CCI, medie mobili da 3 a 200 giorni, MACD, medie del volume, Chaikin, bande di
  Bollinger), combinati con regressioni fra monete su una finestra mobile di 52 settimane e una selezione con la rete
  elastica; ogni settimana si compra il quinto di monete col segnale più alto e si vende il quinto più basso. Dichiarano
  +3,87% la settimana (Sharpe annuo 1,94), +3,39% sulle 100 monete più grandi, e che regge a costi di 0,30-0,40% a giro.
* Segnali contrari: un lavoro su SSRN (Junior, «Failure of Cross-Sectional Alpha Screening on Cryptocurrency Perpetual
  Futures», luglio 2022 → aprile 2026, 10 perpetui di Binance) dice che gli indicatori fra monete **non** funzionano; un
  progetto pubblico vede la forza relativa fallire nel 2025-2026. Quindi l'esito non è scontato.

**Perché è una prova pulita:** i valori li hanno scelti gli autori su dati che finiscono a **maggio 2022**; da **giugno
2022 a oggi (oltre 4 anni)** è fuori dal loro campione e dal nostro. E il metodo stesso impara solo dal passato (52
settimane prima di ogni scelta): è già una finestra che avanza.

## 3. Le regole (dall'articolo; dove l'articolo non dice, la scelta è scritta qui)

* **Dati**: le candele giornaliere e il funding di `SECONDA.md` (737 monete, anche quelle tolte dal listino; gli stessi
  esclusi).
* **Settimana**: da lunedì 00:00 UTC al lunedì dopo. Gli indicatori si calcolano alla chiusura della domenica; il
  rendimento della settimana è dall'apertura del lunedì all'apertura del lunedì dopo (alla chiusura dell'ultimo giorno
  se la moneta viene tolta dal listino).
* **Universo, ogni settimana**: con i dati fino alla domenica, le monete con almeno **200 giorni** di candele (servono
  per la media a 200 giorni), la candela della domenica e la mediana del volume giornaliero in USDT degli ultimi 30
  giorni di almeno 2 milioni; le prime **100** per quella mediana (l'articolo usa le 100 più grandi per capitalizzazione,
  che non abbiamo: il volume è il sostituto più vicino). Una settimana si opera solo con almeno 20 monete.
* **I 28 indicatori** come nell'appendice A dell'articolo: rsi (14 giorni, medie semplici di guadagni e perdite),
  stochRSI (14), stochK (14), stochD (3), cci (20, costante 0,015); sma 3, 5, 10, 20, 50, 100, 200 giorni divise per la
  chiusura; macd (EMA 12 − EMA 26) / EMA 12 e la sua differenza dalla EMA 9; volsma 3, 5, 10, 20, 50, 100, 200 giorni del
  volume in USDT divise per il volume del giorno; volmacd e la sua differenza dalla EMA 9; chaikin (21 giorni);
  boll_low, boll_mid, boll_high (20 giorni, 2 deviazioni) divise per la chiusura, boll_width. Le EMA con α = 1/(1+L)
  come nell'appendice. Ogni settimana ogni indicatore si trasforma nel **rango fra le monete**, portato fra −0,5 e +0,5.
* **Regressioni**: ogni settimana, per ogni indicatore, il rendimento della settimana sul rango della settimana prima,
  fra le monete dell'universo, **pesate** con la mediana del volume (al posto della capitalizzazione). Coefficienti
  **mediati sulle 52 settimane** prima; previsione di ogni indicatore = media dell'intercetta + media della pendenza ×
  rango di oggi.
* **Selezione (rete elastica)**: sulle 52 settimane prima, il rendimento sulle 28 previsioni fatte allora (ognuna con i
  soli dati di allora), pesato come sopra, con la rete elastica a metà fra L1 e L2 e la forza scelta con il criterio di
  Akaike corretto; il segnale **CTREND** è la media delle previsioni con il coefficiente **positivo**. Se nessuna è
  positiva, la settimana non si opera.
* **Portafoglio**: si ordinano le monete per CTREND; si compra il quinto più alto e si vende allo scoperto il quinto più
  basso; dentro ogni lato i pesi sono proporzionali alla mediana del volume; il lato long vale +1 e quello short −1 del
  capitale (leva lorda 2). Si riporta anche il risultato di ogni lato da solo.
* **Costi**: come in `SECONDA.md`: commissione a mercato 0,05% più lo scarto (0,01% BTC, ETH, SOL; 0,02% le altre) su ogni
  variazione di peso (con i pesi che derivano col prezzo durante la settimana), il funding con il segno della posizione.

Le varianti, **tre e solo tre**, contano come tre prove (in tutto il programma 6 diventano **24**):

* **C1** (quella dell'articolo): come sopra.
* **C2**: la combinazione semplice, cioè la media delle 28 previsioni senza la rete elastica (la formula 9 dell'articolo).
* **C3**: C1 con tutto a pesi uguali (regressioni senza pesi, pesi uguali nei due lati).

## 4. L'esame (per C1, C2, C3)

Sulle **settimane che iniziano dal 6 giugno 2022** (il primo lunedì fuori dal campione dell'articolo) all'ultima
settimana completa. Una variante è **valida** se tutte e sei:

1. rendimento netto settimanale medio positivo con l'intervallo al 95% sopra zero (bootstrap a blocchi circolari di 4
   settimane, 10.000 volte);
2. **Sharpe corretto** ≥ 0,95 con le **24** prove del programma 6;
3. positiva in almeno **4 anni su 5** (2022 da giugno, 2026 fino a ottobre) e nell'ultimo anno (dal 2025-10-01);
4. positiva a costi doppi;
5. positiva in almeno **2 trimestri su 4** in ogni anno pieno (2023, 2024, 2025): la tendenza fra monete non deve
   dipendere da un solo periodo;
6. rendimento in più rispetto al Bitcoin (l'intercetta della regressione sui rendimenti settimanali del Bitcoin) positivo.

Si riportano anche, senza che contino per l'esame: lo Sharpe dal primo segnale possibile, i due lati da soli, il giro
settimanale, lo Sharpe dopo l'aprile 2025.

## 5. Cosa non si fa

* Nessun valore si cambia dopo aver visto i risultati; un'idea nuova va in una quarta prova scritta prima, e le prove si
  sommano nel conto.
* La leva lorda 2 è quella del portafoglio dell'articolo (un lato long e uno short pieni); un livello diverso non cambia
  lo Sharpe e si discute solo dopo. `DRY_RUN` resta vero.
