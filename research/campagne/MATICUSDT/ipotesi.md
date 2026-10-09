# MATICUSDT — ipotesi (Fase 1)

Scritte il 2026-10-09, tutte prima del primo test. Ogni variante ha una sola direzione.

## Regole comuni a tutte le varianti (fissate prima dei test)

* Moneta MATICUSDT, perpetuo USDT di Binance; segnali sul last price a barre chiuse, ingresso
  all'apertura della barra dopo (motore della sezione 7, `src/motore.py`).
* **Stop**: distanza dalla chiusura della barra di segnale = il minore fra 2 ATR(14) di Wilder
  del timeframe e il 6% della chiusura (tetto di stop del bot, `stop_massimo_bot`). Long: stop
  sotto; short: sopra. Nessun target salvo dove scritto.
* **Filtro di liquidità** della Fase 0: nessun ingresso su segnali di barre dei mesi 2020-10,
  2020-11, 2020-12, 2021-01.
* **Riscaldamento**: il segnale non esiste finché un indicatore della variante non è calcolabile.
* Costi: commissione 0,05% e slippage 0,02% per lato, funding storico; un giro vale circa 0,14%
  del nozionale (in R: nota `MATICUSDT-N009`).
* Dimensione, leva e liquidazione: regole del bot (`config/parametri.yaml`).

### Spiegazioni concorrenti comuni (valgono per ogni idea, oltre a quelle proprie)

Per ognuna: previsione e cosa la smentirebbe.

* **C1 Caso.** Prevede: R medio entro il rumore della (b), `t` contro la (b) sotto la soglia,
  diverso da anno ad anno. Smentita: `t` netto, stabile negli anni e senza i 3 trade migliori.
* **C2 È solo il mercato (la moneta segue BTC e il trend delle crypto).** Prevede: lo stesso
  effetto con gli stessi segni nelle entrate casuali della stessa direzione (la (b)), e il
  segnale coincide con mosse di BTCUSDT. Smentita: il candidato batte la (b), che entra a caso
  nella stessa direzione e nello stesso periodo.
* **C3 Trend di fondo (rialzo del 2021, ribasso del 2022).** Prevede: long buoni solo nel 2021,
  short buoni solo nel 2022, e la (b) della stessa direzione altrettanto buona. Smentita: R medio
  sopra la (b) in più anni, compreso quello contrario alla direzione.
* **C4 Volatilità.** Prevede: il segnale cade nei periodi più agitati; R più dispersi ma non più
  alti in media della (b) sulle stesse barre. Smentita: R medio sopra la (b) a parità di stop.
* **C5 Costi.** Prevede: vantaggio lordo che sparisce al netto, soprattutto su timeframe corti.
  Smentita: R medio netto positivo e regge a costi doppi.
* **C6 Artefatto dei dati** (giornate senza mark tolte, primi mesi illiquidi, slippage
  ottimista nel 2021). Prevede: risultato concentrato attorno ai buchi o nei mesi a volume basso
  (2021-02/03). Smentita: risultato uguale togliendo quei periodi.
* **C7 Un solo regime o periodo.** Prevede: l'R medio viene da uno o due mesi (per esempio il
  rialzo di maggio 2021). Smentita: R medio sopra la (b) in più della metà degli anni con
  almeno 10 trade.
* **C8 Pochi trade estremi.** Prevede: senza i 3 trade migliori l'R medio scende alla (b) o
  sotto. Smentita: senza i 3 migliori resta sopra la (b).
* **C9 Effetto della regola di stop.** Prevede: con lo stop a 2 ATR (tetto 6%) il risultato
  dipende da dove cade lo stop più che dall'ingresso: la (a), con lo stesso stop e la stessa
  uscita, rende quanto il candidato. Smentita: il candidato batte nettamente la (a).
* **C10 Funding.** Prevede: per posizioni lunghe il funding spiega parte della differenza
  (gli short incassano quando il funding è positivo). Smentita: il funding medio pagato è
  piccolo rispetto all'R medio.
* **C11 Lookahead o errore del codice.** Prevede: crollo con il ritardo di una barra.
  Smentita: il `t` col ritardo resta positivo e almeno metà.

Le spiegazioni proprie di ogni idea sono sotto (P1, P2, …): ogni idea ne ha almeno 10 contando
quelle comuni, e le proprie sono almeno due.

---

## I-01 Momento di serie temporale settimanale

1. **Fonte.** Moskowitz, T. J., Ooi, Y. H., Pedersen, L. H., «Time series momentum», Journal of
   Financial Economics 104(2), maggio 2012. Per le crypto: Liu, Y., Tsyvinski, A., «Risks and
   Returns of Cryptocurrency», NBER Working Paper 24877, agosto 2018 (poi Review of Financial
   Studies 34(6), 2021): forte momento di serie temporale a 1-4 settimane (rendimento di una
   settimana positivo → rendimento della settimana dopo più alto).
2. **Affermazione falsificabile.** Su MATICUSDT, dopo una settimana con rendimento positivo
   (negativo) il rendimento della settimana dopo è più alto (più basso) di quello di una
   settimana presa a caso, al netto dei costi, misurato in R con lo stop comune.
3. **Sotto-domande.** Vale solo con trend forti o anche con rendimenti appena positivi? Più nel
   rialzo 2021 che nel ribasso 2022? Chi opera: investitori che reagiscono in ritardo
   all'attenzione (Liu e Tsyvinski la legano all'attenzione degli investitori) e chi segue il
   trend; l'effetto è lento (giorni-settimane).
4. **Spiegazioni proprie.** P1 Attenzione ritardata (la tesi della fonte): prevede effetto più
   forte dopo settimane con volume in crescita; smentita se non c'è differenza. P2 Il momento è
   solo quello di BTC (l'effetto della fonte è più forte su Bitcoin): prevede che il segnale di
   MATICUSDT aggiunga nulla rispetto a quello di BTCUSDT nello stesso istante; smentita se il
   candidato batte la (b) anche quando i due segnali differiscono. P3 Lo stop a 6% taglia le
   settimane: con volatilità settimanale molto sopra il 6% lo stop scatta spesso prima che il
   momento si realizzi; prevede molti stop e R medio vicino a −1 nei perdenti.
5. **Ipotesi completa.** MATICUSDT, momento di serie temporale; timeframe 4h (il segnale è
   settimanale, ma su 4h si entra a ogni barra libera e si arriva ai trade minimi; con barre
   giornaliere e tenuta di 7 giorni i trade sarebbero al massimo circa 100 in tutto, metà per
   direzione); tenuta 1 settimana.
6. **Varianti.**
   * **V-01 long**: rendimento delle ultime 42 barre (7 giorni) > 0 → long; uscita dopo 42
     barre; stop comune. Motivo: la direzione della fonte.
   * **V-02 short**: rendimento delle ultime 42 barre < 0 → short; uscita dopo 42 barre;
     stop comune. Motivo: il momento della fonte è simmetrico (anche negativo).

## I-02 Rottura del canale di 20 giorni (Donchian, «Turtle»)

1. **Fonte.** Faith, C. M., «Way of the Turtle», McGraw-Hill, 2007 (Sistema 1: ingresso sulla
   rottura del massimo di 20 giorni, uscita sul minimo di 10 giorni; regola di R. Donchian).
   Per le crypto: Hudson, R., Urquhart, A., «Technical trading and cryptocurrencies», Annals of
   Operations Research, online agosto 2019: le regole di rottura di canale sono fra le classi
   con prevedibilità e profitto.
2. **Affermazione.** Su MATICUSDT, dopo una chiusura sopra il massimo dei 20 giorni precedenti il
   prezzo continua a salire più che dopo un ingresso a caso, finché non rompe il minimo di 10
   giorni (simmetrico per lo short).
3. **Sotto-domande.** Le rotture funzionano dopo periodi calmi o anche nel mezzo del trend?
   Quanto durano? Chi compra: chi segue il trend, gli stop dei venditori allo scoperto sopra i
   massimi, gli acquisti per attenzione dei nuovi massimi.
4. **Spiegazioni proprie.** P1 Ricoperture degli short sopra i massimi (prevede salti veloci
   nelle prime barre dopo la rottura; smentita se il guadagno arriva solo molto dopo). P2 Le
   rotture sono false nei mercati laterali (prevede R negativo nei periodi senza trend del
   2022; smentita se reggono anche lì).
5. **Ipotesi completa.** Timeframe 4h (rotture viste a ogni chiusura di 4 ore; 20 giorni = 120
   barre, 10 giorni = 60 barre).
6. **Varianti.**
   * **V-03 long**: chiusura > massimo degli high delle 120 barre precedenti → long; uscita
     quando la chiusura < minimo dei low delle 60 barre precedenti; stop comune.
   * **V-04 short**: chiusura < minimo dei low delle 120 barre precedenti → short; uscita
     quando la chiusura > massimo degli high delle 60 barre precedenti; stop comune.

## I-03 Continuazione dopo un rendimento giornaliero anomalo

1. **Fonte.** Caporale, G. M., Plastun, A., «Momentum effects in the cryptocurrency market after
   one-day abnormal returns», Brunel University Working Paper 19-17, ottobre 2019 (poi Financial
   Markets and Portfolio Management 34, 2020): nei giorni con rendimento anomalo i prezzi
   continuano nella direzione dell'anomalia fino alla fine del giorno, e l'anomalia si può
   riconoscere prima della fine del giorno.
2. **Affermazione.** Su MATICUSDT, quando il rendimento dall'apertura del giorno (00:00 UTC)
   supera la media più una deviazione standard dei rendimenti giornalieri dei 30 giorni
   precedenti, il prezzo sale ancora fino alla fine del giorno più che dopo un ingresso a caso
   nelle stesse ore (simmetrico al ribasso).
3. **Sotto-domande.** Vale più nelle prime ore (anomalia riconosciuta presto)? Dipende da notizie?
   Chi opera: ritardatari che inseguono la mossa, liquidazioni a catena degli short (o dei long).
4. **Spiegazioni proprie.** P1 Liquidazioni a catena (prevede effetto più forte quando anche il
   funding era sbilanciato; smentita se non c'è relazione). P2 Mossa di BTC (prevede che lo
   stesso giorno BTCUSDT abbia la stessa anomalia; smentita se l'effetto c'è anche nei giorni
   anomali solo per MATICUSDT). P3 Il resto del giorno è corto (se l'anomalia arriva tardi resta
   poco tempo: prevede R vicino a zero per i segnali delle ultime ore).
5. **Ipotesi completa.** Timeframe 1h. Soglia: media ± 1 deviazione standard (k = 1) dei
   rendimenti giornalieri (chiusura su chiusura) dei 30 giorni precedenti il giorno corrente.
   Segnale al primo superamento della soglia nel giorno, solo su barre di segnale dalle 00:00
   alle 21:00 UTC (ne restano almeno due); uscita alla chiusura della barra delle 23:00 (si
   esce all'apertura del giorno dopo).
6. **Varianti.**
   * **V-05 long**: rendimento dall'apertura del giorno passa sopra media + 1 deviazione standard.
   * **V-06 short**: rendimento dall'apertura del giorno passa sotto media − 1 deviazione standard.

## I-04 Momento intragiornaliero: la prima mezz'ora prevede l'ultima

1. **Fonte.** Shen, D., Urquhart, A., Wang, P., «Bitcoin intraday time-series momentum»,
   Financial Review 57(2), 2022 (manoscritto accettato settembre 2021): il rendimento della
   prima mezz'ora predice positivamente quello dell'ultima mezz'ora. Sul mercato azionario:
   Gao, L., Han, Y., Li, S. Z., Zhou, G., «Market intraday momentum», Journal of Financial
   Economics 129(2), 2018.
2. **Affermazione.** Su MATICUSDT il rendimento dell'ultima mezz'ora del giorno UTC (23:30-24:00)
   ha lo stesso segno del rendimento della prima mezz'ora (00:00-00:30) più spesso e di più che
   un'ultima mezz'ora qualunque, al netto dei costi.
3. **Sotto-domande.** La fonte usa il volume per definire il «giorno» (Bitcoin non chiude mai);
   qui si usa la mezzanotte UTC, che è anche il confine delle candele giornaliere di Binance. Vale
   di più con prima mezz'ora molto mossa? Chi opera: chi fornisce liquidità e la ritira (tesi
   della fonte), ribilanciamenti a fine giornata.
4. **Spiegazioni proprie.** P1 Mezzanotte UTC non è l'apertura giusta (prevede effetto nullo
   perché il giorno del mercato di MATICUSDT ha un altro inizio; non smentibile qui, si
   dichiara). P2 I costi superano il movimento di mezz'ora (un giro vale circa 0,055 R con stop a
   2 ATR di 30m: prevede R lordo positivo e netto negativo).
5. **Ipotesi completa.** Timeframe 30m. Segnale alla chiusura della barra delle 23:00 (che chiude
   alle 23:30): ingresso all'apertura delle 23:30, uscita dopo una barra (all'apertura delle
   00:00 del giorno dopo); la direzione viene dal segno della barra delle 00:00 dello stesso
   giorno (chiusura contro apertura).
6. **Varianti.**
   * **V-07 long**: prima mezz'ora con rendimento > 0.
   * **V-08 short**: prima mezz'ora con rendimento < 0.

## I-05 Ritorno verso la media dopo un ribasso brusco dentro il trend (RSI a 2)

1. **Fonte.** Connors, L., Alvarez, C., «Short Term Trading Strategies That Work», TradingMarkets
   Publishing, 2009: sopra la media mobile di 200, comprare quando l'RSI a 2 periodi chiude sotto
   5 e uscire quando la chiusura torna sopra la media mobile di 5. RSI: Wilder, J. W., «New
   Concepts in Technical Trading Systems», 1978.
2. **Affermazione.** Su MATICUSDT, in tendenza al rialzo (chiusura sopra la media di 200 barre),
   dopo un ribasso brusco (RSI a 2 sotto 5) il prezzo rimbalza fino alla media di 5 più di quanto
   faccia dopo un ingresso a caso (simmetrico per lo short in tendenza al ribasso).
3. **Sotto-domande.** Il rimbalzo vale anche quando il ribasso è dovuto a notizie? Quanto dura?
   Chi opera: fornitori di liquidità che comprano le vendite forzate, ricoperture.
4. **Spiegazioni proprie.** P1 Ribasso informato (se il ribasso porta informazione il rimbalzo non
   arriva: prevede perdite grandi sui ribassi più profondi). P2 Lo stop stretto taglia il
   rimbalzo (prevede molti stop subito dopo l'ingresso). P3 Il libro è su azioni giornaliere: su
   una crypto a 4 ore l'effetto può non esserci.
5. **Ipotesi completa.** Timeframe 4h (su barre giornaliere le occasioni sarebbero troppo poche:
   circa 700 giorni liquidi; dichiarato come adattamento). Medie di 200 e 5 barre di 4h.
6. **Varianti.**
   * **V-09 long**: chiusura > media(200) e RSI(2) < 5 → long; uscita quando chiusura > media(5).
   * **V-10 short**: chiusura < media(200) e RSI(2) > 95 → short; uscita quando chiusura < media(5).

## I-06 Effetto del giorno della settimana (lunedì)

1. **Fonte.** Caporale, G. M., Plastun, A., «The day of the week effect in the cryptocurrency
   market», Finance Research Letters 31, 2019: per Bitcoin i rendimenti del lunedì sono più alti
   degli altri giorni.
2. **Affermazione.** Su MATICUSDT il rendimento del lunedì (00:00-24:00 UTC) è più alto di quello
   di un giorno preso a caso.
3. **Sotto-domande.** Vale dopo un fine settimana calmo? Chi opera: i flussi istituzionali che
   riprendono a inizio settimana.
4. **Spiegazioni proprie.** P1 Effetto di Bitcoin e non della moneta (prevede che lo stesso lunedì
   BTCUSDT salga; non distinguibile senza un altro confronto). P2 Effetto degli anni 2013-2017 della
   fonte, scomparso dopo (prevede R nullo in ogni anno).
5. **Ipotesi completa.** Timeframe 1d; segnale alla chiusura della domenica, ingresso all'apertura
   del lunedì, uscita dopo una barra (apertura del martedì). Stop comune (6%).
6. **Varianti.** **V-11 long** il lunedì. (Una variante: la fonte non indica un giorno negativo
   stabile.)

## I-07 Funding estremo: il perpetuo lontano dal suo valore torna indietro

1. **Fonte.** He, S., Manela, A., Ross, O., von Wachter, V., «Fundamentals of Perpetual Futures»,
   arXiv 2212.06888, prima versione 13 dicembre 2022: le deviazioni del prezzo del perpetuo dal
   valore di non arbitraggio sono grandi nelle crypto e si riducono; il funding è proporzionale
   alla deviazione.
2. **Affermazione.** Su MATICUSDT, quando l'ultimo funding è molto positivo (perpetuo caro, long
   affollati) il prezzo del perpetuo scende nelle 24 ore successive più che dopo un ingresso a
   caso; quando è negativo (perpetuo a sconto) sale. Limite noto: la fonte usa il funding per un
   arbitraggio (perpetuo contro spot), non per una scommessa di direzione; qui si prova solo la
   parte della convergenza che passa dal prezzo del perpetuo.
3. **Sotto-domande.** Il ritorno arriva dal perpetuo o dallo spot? In quanto tempo? Chi opera:
   arbitraggisti che vendono il perpetuo caro, long a leva che chiudono per il costo del funding.
4. **Spiegazioni proprie.** P1 Funding alto = trend forte (prevede che il funding alto segni la
   continuazione del rialzo, cioè short perdenti). P2 La convergenza avviene dallo spot (prevede
   nessun effetto sulla direzione del perpetuo). P3 Incasso del funding (prevede che il guadagno
   degli short venga dal funding incassato, non dal prezzo).
5. **Ipotesi completa.** Timeframe 8h (l'intervallo del funding). Valore: il tasso dell'ultimo
   settlement con istante entro la chiusura della barra di segnale. Soglie scritte prima: il tasso
   base di Binance è 0,01% per 8 ore; estremo positivo ≥ 0,05% (5 volte il base); negativo ≤
   −0,01% (gli short pagano almeno quanto pagano di norma i long). Uscita dopo 3 barre (24 ore).
6. **Varianti.**
   * **V-12 short**: funding ≥ 0,05%.
   * **V-13 long**: funding ≤ −0,01%.

## I-08 Premio del volume alto

1. **Fonte.** Gervais, S., Kaniel, R., Mingelgrin, D. H., «The High-Volume Return Premium»,
   Journal of Finance 56(3), giugno 2001: un titolo con volume insolitamente alto in un giorno
   (il più alto della finestra di 50 giorni) ha rendimenti più alti nei giorni e nelle settimane
   dopo (visibilità che attira compratori).
2. **Affermazione.** Su MATICUSDT, dopo un giorno con volume in USDT insolitamente alto rispetto ai
   50 giorni precedenti, il rendimento dei giorni successivi è più alto di quello di un ingresso a
   caso, qualunque fosse il segno del giorno.
3. **Sotto-domande.** Vale più se il giorno di volume è stato di rialzo? Chi opera: nuovi
   compratori attirati dalla visibilità; chi vende allo scoperto è poco (nelle azioni).
4. **Spiegazioni proprie.** P1 Il volume alto accompagna i massimi delle mosse e poi c'è il
   ritorno (prevede R negativo). P2 Il volume alto è un giorno di notizie (prevede effetto che
   dipende dal segno del giorno).
5. **Ipotesi completa.** Timeframe 1d (il volume della fonte è giornaliero).
6. **Varianti.**
   * **V-14 long**: volume in USDT del giorno > massimo dei 49 giorni precedenti (il più alto
     della finestra di 50, definizione della fonte); uscita dopo 10 barre.
   * **V-15 long**: volume del giorno > 2 volte la media dei 50 giorni precedenti (soglia più
     bassa, scritta prima di contare: con la definizione della fonte i segnali giornalieri sono
     pochi); uscita dopo 5 barre.

## I-09 Ritorno dopo un salto orario (eccesso di reazione)

1. **Fonte.** Wen, Z., Bouri, E., Xu, Y., Zhao, Y., «Intraday return predictability in the
   cryptocurrency markets: Momentum, reversal, or both», North American Journal of Economics and
   Finance 62, 2022: nelle crypto ci sono sia momento sia ritorno intragiornalieri, i loro schemi
   cambiano attorno ai grandi salti di prezzo, e il ritorno viene da eccesso di reazione a
   informazioni non fondamentali.
2. **Affermazione.** Su MATICUSDT, dopo una barra oraria con rendimento oltre 3 deviazioni
   standard (delle 168 ore precedenti), nelle 6 ore dopo il prezzo torna indietro più che dopo un
   ingresso a caso.
3. **Sotto-domande.** Ritorno più forte dopo i ribassi (liquidazioni) o dopo i rialzi? Quanto
   dura? Chi opera: fornitori di liquidità dopo le liquidazioni forzate.
4. **Spiegazioni proprie.** P1 Salto informato (notizia): prevede continuazione, non ritorno.
   P2 Rimbalzo meccanico di una barra (spread) che i costi mangiano.
5. **Ipotesi completa.** Timeframe 1h; uscita dopo 6 barre.
6. **Varianti.**
   * **V-16 long**: rendimento dell'ultima ora < −3 deviazioni standard.
   * **V-17 short**: rendimento dell'ultima ora > +3 deviazioni standard.

## I-10 Vicinanza al massimo di 52 settimane

1. **Fonte.** George, T. J., Hwang, C.-Y., «The 52-Week High and Momentum Investing», Journal of
   Finance 59(5), ottobre 2004: i titoli vicini al loro massimo di 52 settimane continuano a fare
   meglio (gli investitori ancorati al massimo reagiscono in ritardo alle buone notizie).
2. **Affermazione.** Su MATICUSDT, quando la chiusura è entro il 5% del massimo delle 52 settimane
   precedenti, il rendimento dei 10 giorni dopo è più alto di un ingresso a caso.
3. **Sotto-domande.** Il massimo di 52 settimane richiede un anno di riscaldamento: dal 2021-10-22.
4. **Spiegazioni proprie.** P1 Ancoraggio (tesi della fonte). P2 Pochi episodi nel periodo (dopo
   il riscaldamento resta poco più di un anno di costruzione).
5. **Ipotesi completa.** Timeframe 1d; uscita dopo 10 barre.
6. **Varianti.** **V-18 long**: chiusura ≥ 0,95 × massimo degli high delle 365 barre precedenti.

## I-11 Prezzo sopra la media mobile lunga (regola a media mobile)

1. **Fonte.** Brock, W., Lakonishok, J., LeBaron, B., «Simple Technical Trading Rules and the
   Stochastic Properties of Stock Returns», Journal of Finance 47(5), dicembre 1992 (regola «1-50»:
   comprare quando il prezzo passa sopra la media di 50 giorni). Per le crypto: Hudson e Urquhart
   (sopra), classe delle medie mobili.
2. **Affermazione.** Su MATICUSDT, dopo che la chiusura passa sopra (sotto) la media dei 50 giorni,
   il prezzo continua nella stessa direzione finché non ripassa la media, più che dopo un
   ingresso a caso.
3. **Sotto-domande.** Molti falsi incroci nei mercati laterali; la prova a placebo del protocollo
   segnala che gli incroci di medie hanno segnali a grappoli (sezione 11): il bootstrap a blocchi
   lo copre solo in parte, lo dichiaro come rischio di falso positivo.
4. **Spiegazioni proprie.** P1 Seguire il trend (tesi). P2 Falsi incroci a grappoli (prevede
   molti trade brevi in perdita nel 2022).
5. **Ipotesi completa.** Timeframe 4h; media di 50 giorni = 300 barre.
6. **Varianti.**
   * **V-19 long**: chiusura passa sopra la media(300) (barra prima sotto o uguale) → long; uscita
     quando la chiusura torna sotto la media(300).
   * **V-20 short**: chiusura passa sotto la media(300) → short; uscita quando torna sopra.

## I-12 Compressione della volatilità e rottura (Bollinger)

1. **Fonte.** Bollinger, J., «Bollinger on Bollinger Bands», McGraw-Hill, 2001: la «stretta»
   (larghezza delle bande al minimo di sei mesi) precede un'espansione della volatilità; la
   direzione si prende dalla rottura della banda.
2. **Affermazione.** Su MATICUSDT, una rottura della banda di Bollinger (20, 2) quando la larghezza
   delle bande è stata vicina al minimo degli ultimi sei mesi porta a una mossa nella direzione
   della rottura più grande di un ingresso a caso.
3. **Sotto-domande.** La «stretta» si definisce come larghezza al suo minimo dei 6 mesi precedenti
   (qui: entro il 10% sopra il minimo, nelle ultime 20 barre). Chi opera: rotture di range
   dopo periodi di accumulo; stop sopra e sotto il range.
4. **Spiegazioni proprie.** P1 Rottura falsa (rientro nella banda). P2 Volatilità che torna senza
   direzione (prevede R nullo ma con dispersione alta).
5. **Ipotesi completa.** Timeframe 4h; bande su 20 barre, 2 deviazioni standard; sei mesi = 1080
   barre; uscita quando la chiusura torna oltre la media di 20 (dalla parte opposta) o dopo 30
   barre (5 giorni).
6. **Varianti.**
   * **V-21 long**: chiusura > banda alta e la larghezza minima delle ultime 20 barre ≤ 1,1 ×
     minimo della larghezza delle 1080 barre precedenti.
   * **V-22 short**: chiusura < banda bassa con la stessa condizione.

## Varianti aggiunte dopo i conteggi (scritte prima del primo test di queste idee)

Scritte il 2026-10-09 dopo gli scarti `MATICUSDT-S01`…`S11` (sotto i 70 trade), prima di vedere
qualunque risultato di queste idee (regola 6: allentare le soglie di uno scarto senza aver visto
risultati è ancora una variante dell'idea nuova). Al massimo due varianti testate per fonte.

* **I-02, V-23 long / V-24 short** (canale di 5 giorni). Hudson e Urquhart provano le rotture di
  canale con finestre da 5 a 250 giorni (insieme di regole di Sullivan, Timmermann e White, 1999):
  5 giorni è la finestra più corta della classe. 4h; ingresso: chiusura oltre il massimo (minimo)
  delle 30 barre precedenti; uscita: chiusura oltre il minimo (massimo) delle 15 barre precedenti;
  stop comune.
* **I-05, V-25 long / V-26 short** (RSI a 2 sotto 10 / sopra 90): Connors e Alvarez riportano anche
  soglie fino a 10; il resto uguale a V-09 / V-10.
* **I-08, V-29 long** (volume del giorno > 1,5 volte la media dei 50 giorni precedenti, uscita dopo
  5 barre): soglia più bassa; resto come V-15.
* **I-11, V-27 long / V-28 short** (stessa regola «1-50» su barre di 1h: media di 1200 barre = 50
  giorni). Il timeframe più fine vede più incroci della stessa media. Rischio dichiarato: la prova
  a placebo segnala che gli incroci di medie a 1h hanno «netta» per caso più spesso del 2%
  (sezione 11 del protocollo).
* **I-12, V-30 long / V-31 short** (stretta su una finestra più corta): larghezza minima delle
  ultime 20 barre ≤ 1,2 × minimo delle 360 barre precedenti (60 giorni invece di 6 mesi); resto come
  V-21 / V-22.

## I-13 Squilibrio fra acquisti e vendite aggressivi

1. **Fonte.** Chordia, T., Subrahmanyam, A., «Order imbalance and individual stock returns: Theory
   and evidence», Journal of Financial Economics 72(3), 2004: lo squilibrio degli ordini di un
   giorno predice positivamente il rendimento del giorno dopo (chi spezza ordini grandi continua a
   comprare). Per le crypto: Silantyev, E., «Order flow analysis of cryptocurrency markets»,
   Digital Finance 1, 2019 (lo squilibrio dei trade spiega i movimenti di prezzo del perpetuo).
2. **Affermazione.** Su MATICUSDT, dopo 6 ore con una quota di volume comprato dagli aggressori
   (taker buy) insolitamente alta, il prezzo sale nelle 6 ore dopo più che dopo un ingresso a caso
   (simmetrico per le vendite).
3. **Sotto-domande.** Lo squilibrio predice o solo accompagna (Silantyev: contemporaneo)? Chi opera:
   chi spezza ordini grandi in più ore.
4. **Spiegazioni proprie.** P1 Solo contemporaneo (prevede nessun effetto dopo). P2 Squilibrio da
   liquidazioni forzate (prevede ritorno, non continuazione).
5. **Ipotesi completa.** Timeframe 1h. Squilibrio delle ultime 6 barre = somma del volume taker buy
   / somma del volume − 0,5 (colonna `taker_buy_volume` dei file klines). Soglia: media + 2
   deviazioni standard (− 2 per lo short) dello stesso squilibrio sulle 720 barre precedenti (30
   giorni). Uscita dopo 6 barre; stop comune.
6. **Varianti.** **V-32 long** sopra la soglia alta; **V-33 short** sotto la soglia bassa.

## I-14 Forza relativa contro BTCUSDT (momento fra crypto)

1. **Fonte.** Liu, Y., Tsyvinski, A., Wu, X., «Common Risk Factors in Cryptocurrency», NBER Working
   Paper 25882, maggio 2019 (poi Journal of Finance, 2022): il momento fra crypto (chi ha reso più
   delle altre nelle ultime settimane continua a rendere di più) è uno dei tre fattori.
2. **Affermazione.** Su MATICUSDT, dopo una settimana in cui ha reso più di BTCUSDT, nella settimana
   dopo rende più di un ingresso a caso nella stessa direzione (simmetrico: dopo una settimana
   peggiore di BTCUSDT rende meno).
3. **Sotto-domande.** È diverso dal momento della moneta da sola (I-01)? Lo è quando la moneta sale
   meno di BTCUSDT pur salendo. Chi opera: rotazioni di capitale fra crypto.
4. **Spiegazioni proprie.** P1 È il momento assoluto travestito (prevede gli stessi trade di I-01).
   P2 Ritorno della forza relativa (prevede R negativo).
5. **Ipotesi completa.** Timeframe 4h, 42 barre (7 giorni), uscita dopo 42 barre, stop comune. Il
   confronto usa le chiusure di BTCUSDT sugli stessi istanti (solo riferimento di mercato).
6. **Varianti.** **V-34 long**: rendimento di 42 barre di MATICUSDT > quello di BTCUSDT; **V-35
   short**: minore.

## I-15 Premio per l'illiquidità nel tempo (Amihud)

Scritta il 2026-10-09 dopo i risultati delle varianti 1-11, che sono di altre idee; questa idea non
nasce da quei risultati ma dalla ricerca di famiglie di meccanismi non ancora usate (la liquidità).

1. **Fonte.** Amihud, Y., «Illiquidity and stock returns: cross-section and time-series effects»,
   Journal of Financial Markets 5(1), 2002: nel tempo, un'illiquidità attesa più alta porta
   rendimenti attesi più alti (compenso per l'illiquidità); la misura è la media di |rendimento| /
   volume in valuta.
2. **Affermazione.** Su MATICUSDT, quando l'illiquidità dell'ultima settimana è sopra la sua mediana
   dei 90 giorni precedenti, il rendimento della settimana dopo è più alto di un ingresso a caso;
   quando è sotto, più basso.
3. **Sotto-domande.** L'illiquidità alta coincide con i ribassi (volume che si secca)? Chi opera:
   fornitori di liquidità che chiedono un compenso più alto; capitale che torna quando la
   liquidità torna.
4. **Spiegazioni proprie.** P1 L'illiquidità alta segue i crolli e il ritorno è solo rimbalzo
   (prevede R concentrato dopo i ribassi). P2 In crypto il volume è guidato dall'attenzione, non
   dalla liquidità (prevede l'opposto: volume alto → rialzo, cioè illiquidità alta → R basso).
5. **Ipotesi completa.** Timeframe 4h. Illiquidità = media sulle ultime 42 barre (7 giorni) di
   |rendimento della barra| / volume in USDT della barra; confronto con la mediana dei valori della
   stessa misura nelle 540 barre precedenti (90 giorni). Uscita dopo 42 barre; stop comune.
6. **Varianti.** **V-36 long**: illiquidità sopra la mediana; **V-37 short**: sotto la mediana.

## Idee scartate prima del test

* **Anticipo di BTCUSDT su MATICUSDT (lead-lag).** Scartata per contaminazione (nota
  `MATICUSDT-N008`). Nessun budget.

## Fonti consultate

Quelle sopra, più: Mohamad, Sifat, Mohamed Shariff, «Lead-lag relationship between Bitcoin and
Ethereum: Evidence from hourly and daily data», Research in International Business and Finance 50,
2019 (per l'idea scartata); Eross, McGroarty, Urquhart, Wolfe, «The intraday dynamics of bitcoin»,
Research in International Business and Finance 49, 2019 (volume e volatilità per ora; nessuna
previsione di direzione, quindi nessuna idea).
