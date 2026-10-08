# Ipotesi della campagna BTCUSDT (protocollo 4.4, Passo 3, Fase 1)

Scritte prima di qualunque test. Ogni variante e' una regola completa, con una sola
direzione; i suoi trade si contano con `conta_trade` una volta sola, sulle regole
scritte qui, e il numero va nel log. Il codice di ogni variante sta in
`codice/varianti.py` con lo stesso identificativo.

## Regole comuni a tutte le varianti

* Moneta BTCUSDT, perpetuo USDS-M. Periodo di costruzione 2020-01-01 → 2022-10-18
  (log, voce BTCUSDT-N002). Il periodo di validazione non si usa fino alla validazione.
* Segnali solo su barre chiuse (serie last price); ingresso all'apertura della barra
  successiva; stop sul last price, liquidazione sul mark price; stop prima del target
  nella stessa barra; costi, dimensione e leva da `config/parametri.yaml` e dalla scheda
  (commissione 0,05% per lato, slippage 0,01% per lato, rischio 1% a trade, leva massima 2,
  margine isolato, margine di mantenimento 2,5%).
* Lo stop si calcola dal close della barra del segnale. Il tetto di stop del 6%
  (`stop_massimo_bot` di `parametri.yaml`) non si impone nel test: si riporta quante
  volte uno stop lo supera, per sapere se la regola si potrebbe eseguire cosi' com'e'.
* Mesi sotto la liquidita' minima: nessuno (fase0_dati.md), quindi nessun filtro mensile.
* Nessuna idea qui e' scelta perche' «so che ha funzionato» dopo il 2023: le fonti
  sono tutte anteriori al 2024 e le regole sono quelle delle fonti, adattate solo dove
  serve (scritto variante per variante). Conosco a grandi linee l'andamento di BTC nel
  2020-2022 (salita fino al 2021, discesa nel 2022): per questo ogni idea che ha un verso
  naturale si prova, dove ha senso, nei due versi, e il confronto che conta e' con
  l'entrata casuale nella stessa direzione (baseline (b)), che il trend di fondo lo ha
  gia' dentro.

## Le spiegazioni concorrenti comuni

Valgono per ogni idea e si aggiungono a quelle proprie di ciascuna (almeno tre per idea).
Ognuna con la previsione che fa e cosa la smentisce.

| # | Spiegazione | Previsione | Cosa la smentisce |
|---|---|---|---|
| C1 | Effetto casuale: il risultato e' rumore | R medio non distinguibile dalla baseline (b); percentile fra le simulazioni casuali vicino a 50 | batte nettamente la (b) e la (a) |
| C2 | Trend di fondo: nel 2020-2021 BTC sale, nel 2022 scende; un long guadagna solo perche' il mercato sale | la (b) nella stessa direzione ha lo stesso R medio; R per anno segue il segno del buy and hold dell'anno | batte la (b) e l'R per anno e' positivo anche nell'anno di segno opposto |
| C3 | «E' solo il mercato»: BTC segue il ciclo generale delle crypto (liquidita', leva del sistema) | come C2: R per anno allineato al buy and hold | R positivo in anni con buy and hold di segno diverso |
| C4 | Volatilita': l'effetto c'e' solo dove la volatilita' e' alta (o lo stop e' largo) | trade vincenti concentrati nei periodi a volatilita' alta; R vicino a zero altrove | R positivo sia nel 2020-2021 sia nel 2022 |
| C5 | Artefatto dei dati (buchi, candele anomale, cambi di feed) | pochi trade estremi su barre anomale | R medio senza i 3 trade migliori ancora positivo e sopra la (b) |
| C6 | Effetto costi: il vantaggio lordo c'e' ma i costi lo mangiano (o viceversa, il risultato netto dipende dai costi scelti) | R lordo positivo, netto vicino a zero | R netto positivo e regge a costi doppi |
| C7 | Pochi trade estremi (code) | R medio dominato dai 3 migliori | R senza i 3 migliori resta sopra la (b) |
| C8 | Errore di calcolo o lookahead | crollo con il ritardo di una barra | il `t` col ritardo resta positivo e almeno meta' |
| C9 | Un solo regime o un solo anno | R per anno positivo in un solo anno | positivo in piu' della meta' degli anni con almeno 10 trade |

Nella tabella di ogni idea scrivo le spiegazioni proprie (P1, P2, ...), cosi' che con
le C1-C9 le spiegazioni concorrenti siano almeno 10 (regola della Fase 1, punto 4).

---

## I-01 — Momentum a serie storica (rendimento dell'ultima settimana)

1. **Fonte.** Tobias J. Moskowitz, Yao Hua Ooi, Lasse Heje Pedersen, «Time series
   momentum», Journal of Financial Economics 104(2), maggio 2012. Per le crypto: Yukun Liu,
   Aleh Tsyvinski, «Risks and Returns of Cryptocurrency», NBER Working Paper 24877, agosto
   2018: il rendimento di BTC delle ultime settimane predice quello della settimana dopo.
2. **Affermazione verificabile.** Se il rendimento di BTC degli ultimi 7 giorni e'
   positivo (negativo), il rendimento dei 7 giorni successivi e' in media piu' alto (piu'
   basso) di quello di un'entrata a caso nella stessa direzione con la stessa uscita.
   Falsa se l'R medio non batte nettamente la (b).
3. **Sotto-domande.** Vale piu' dopo settimane forti che deboli? In alta o bassa
   volatilita'? Chi opera: chi insegue i prezzi (attenzione degli investitori, Liu e
   Tsyvinski), chi si copre in ritardo, chi segue il trend per regola. Quando: la fonte
   parla di 1-4 settimane; qui una settimana di segnale, una di tenuta.
4. **Spiegazioni proprie.** P1: inerzia dell'attenzione (ricerche e notizie seguono i
   prezzi): previsione: effetto piu' forte dopo settimane forti; smentita: R uguale per
   ogni intensita'. P2: e' solo il trend lungo (sopra/sotto la media annuale): previsione:
   l'effetto sparisce condizionando al trend lungo; smentita: R positivo anche contro il
   trend lungo. P3: inversione di breve (la settimana dopo restituisce): previsione: R
   negativo; smentita: R positivo.
5. Previsioni e smentite delle C1-C9 come in tabella comune.
6. **Ipotesi.** BTCUSDT, momentum a serie storica, timeframe 1d (il meccanismo e' in
   giorni e settimane: candele piu' corte aggiungono solo rumore), due direzioni.
   * **V01 (long).** Alla chiusura giornaliera, se close / close di 7 barre prima − 1 > 0:
     long. Stop al 6% sotto il close del segnale. Uscita: «chiudi» alla chiusura della 7ª
     barra in posizione (una settimana). Nessun target. Motivo: la regola della fonte con
     una settimana di segnale e una di tenuta; stop al tetto del 6% perche' con una tenuta
     fissa lo stop serve solo da protezione.
   * **V02 (short).** Specchio: se il rendimento di 7 barre e' < 0: short, stop 6% sopra,
     uscita dopo 7 barre. Motivo: la fonte vale nei due versi.

## I-02 — Rottura del canale di 20 barre (sistema 1 delle «tartarughe»)

1. **Fonte.** Curtis M. Faith, «Way of the Turtle», McGraw-Hill, 2007 (sistema 1:
   ingresso sulla rottura del massimo di 20 periodi, uscita sul minimo di 10, stop a 2 N
   con N la media del vero range di 20 periodi).
2. **Affermazione.** Dopo una chiusura sopra il massimo delle 20 barre precedenti il
   prezzo prosegue abbastanza da dare un R medio superiore all'entrata casuale con la
   stessa uscita (stop a 2 N, uscita sul minimo di 10). Falsa se non batte la (b).
3. **Sotto-domande.** Rotture da range stretto o largo? Con volume? Chi opera: chi ha
   ordini di stop sopra i massimi recenti, chi segue i trend per regola, chi copre short.
   In quanto tempo: giorni.
4. **Spiegazioni proprie.** P1: le rotture sono quasi tutte false e il guadagno viene da
   pochi trend lunghi (asimmetria del trend following): previsione: win rate basso, R
   medio dominato da pochi trade; smentita: R senza i 3 migliori positivo. P2: la
   rottura e' solo volatilita' che si espande: previsione: R uguale per long e short;
   smentita: un verso molto diverso dall'altro. P3: liquidazioni a catena dopo la
   rottura (leva alta sui perpetui): previsione: guadagni concentrati nelle prime barre;
   smentita: guadagni distribuiti su tutta la tenuta.
5. Come in tabella comune per C1-C9.
6. **Ipotesi.** Timeframe 4h. La fonte usa candele giornaliere, ma in 1.022 giorni di
   costruzione una rottura di 20 giorni capita poche decine di volte: a 4 ore il
   meccanismo (rottura di un range di qualche giorno) resta lo stesso e i trade bastano.
   * **V03 (long).** Close > massimo degli high delle 20 barre precedenti → long. Stop =
     close − 2 × ATR(20) (media di Wilder del vero range). Uscita: «chiudi» quando il close
     scende sotto il minimo dei low delle 10 barre precedenti. Nessun target.
   * **V04 (short).** Specchio: close < minimo dei low delle 20 barre precedenti → short;
     stop = close + 2 × ATR(20); «chiudi» quando il close supera il massimo degli high
     delle 10 barre precedenti.

## I-03 — Reazione eccessiva: barre anomale

1. **Fonte.** Guglielmo Maria Caporale, Alex Plastun, «Price overreactions in the
   cryptocurrency market», Journal of Economic Studies 46(5), 2019: dopo giorni con
   rendimenti anomali il prezzo del giorno dopo si muove in modo prevedibile.
2. **Affermazione.** Dopo una barra a 4 ore con rendimento oltre 2 deviazioni standard
   (calcolate sulle 180 barre precedenti, 30 giorni) il prezzo delle 6 barre successive
   (un giorno) ha un R medio diverso da quello di un'entrata a caso. V05 dice «prosegue
   nella stessa direzione», V06 dice «rimbalza dopo un crollo»: ognuna e' falsa se non
   batte nettamente la (b).
3. **Sotto-domande.** Dipende dal segno della barra anomala? Dall'ora (sessioni asiatica,
   europea, americana)? Chi opera: liquidazioni forzate (spingono oltre il valore e poi il
   prezzo torna) o arrivo di notizie (il prezzo continua a incorporarle).
4. **Spiegazioni proprie.** P1: liquidazioni a catena: dopo un crollo il prezzo torna su
   (V06 positiva, V05 nulla). P2: notizie lente da incorporare: continuazione (V05
   positiva). P3: la barra anomala e' solo l'inizio di un regime di alta volatilita':
   previsione: R vicino a zero in media ma varianza alta; smentita: R medio netto.
5. Come in tabella comune.
6. **Ipotesi.** Timeframe 4h: la fonte usa giorni, ma con soglie di 2 deviazioni
   standard i giorni anomali in costruzione sono poche decine; a 4 ore il meccanismo
   (eccesso e ritorno, o eccesso e continuazione, entro un giorno) e' lo stesso.
   Rendimento della barra = close / close precedente − 1; deviazione standard dei
   rendimenti delle 180 barre precedenti (esclusa quella del segnale).
   * **V05 (long, continuazione).** Rendimento > +2 deviazioni standard → long. Stop 5%
     sotto il close; «chiudi» dopo 6 barre.
   * **V06 (long, rimbalzo).** Rendimento < −2 deviazioni standard → long. Stop 5% sotto
     il close; «chiudi» dopo 6 barre.

## I-04 — RSI a 2 periodi in un trend positivo (ritorno alla media di breve)

1. **Fonte.** Larry Connors, Cesar Alvarez, «Short Term Trading Strategies That Work»,
   TradingMarkets Publishing, 2008: comprare quando l'RSI(2) e' sotto 10 e il prezzo e'
   sopra la media di 200 periodi, uscire quando il close supera la media di 5.
2. **Affermazione.** Un ritracciamento brusco (RSI(2) < 10) dentro un trend positivo
   (close > media di 200) e' seguito da un rimbalzo con R medio superiore all'entrata
   casuale con la stessa uscita. Falsa se non batte la (b).
3. **Sotto-domande.** Dipende da quanto e' profondo il ritracciamento? Dal giorno? Chi
   opera: chi compra i ribassi in un mercato che sale, chi chiude short presi sul
   ritracciamento. In quanto tempo: poche barre.
4. **Spiegazioni proprie.** P1: rimbalzo meccanico dopo un eccesso di vendite di breve
   (liquidita' temporanea): previsione: guadagni nelle prime barre. P2: e' solo il trend
   lungo (sopra la media di 200 il mercato sale comunque): previsione: la (b) con lo
   stesso filtro... la (b) entra a caso anche fuori dal filtro, quindi se e' solo trend la
   (a) e la (b) sono vicine al candidato quando il trend domina; smentita: batte la (b).
   P3: nelle crypto il breve e' momentum, non ritorno alla media: previsione: R negativo.
5. Come in tabella comune.
6. **Ipotesi.** Timeframe 4h: la regola della fonte e' giornaliera su azioni; su BTC a
   1d i segnali con il filtro di 200 giorni sono pochi (200 giorni di riscaldamento su
   1.022). A 4 ore la media di 200 copre circa 33 giorni.
   * **V07 (long).** Close > SMA(200) e RSI(2) < 10 → long. Stop = close − 3 × ATR(14).
     Uscita: «chiudi» quando il close supera la SMA(5). Lo stop non c'e' nella fonte:
     serve per dimensionare (rischio 1%), largo per non cambiare la regola.
   * **V08 (short).** Specchio: close < SMA(200) e RSI(2) > 90 → short; stop = close + 3
     × ATR(14); «chiudi» quando il close scende sotto la SMA(5).

## I-05 — Il lunedi'

1. **Fonte.** Guglielmo Maria Caporale, Alex Plastun, «The day of the week effect in the
   cryptocurrency market», Finance Research Letters 31, dicembre 2019: per BTC rendimenti
   del lunedi' significativamente piu' alti degli altri giorni.
2. **Affermazione.** Un long tenuto dal lunedi' 00:00 UTC alla chiusura del lunedi' ha un
   R medio superiore a quello di un long di un giorno entrato a caso. Falsa se non batte
   la (b).
3. **Sotto-domande.** Dipende dal weekend (volume basso, poi arrivo degli operatori
   istituzionali il lunedi')? Dal segno del weekend? Chi opera: chi ha preso decisioni nel
   weekend e opera all'apertura dei mercati tradizionali.
4. **Spiegazioni proprie.** P1: ritorno degli operatori del lunedi' dopo un weekend
   sottile: previsione: effetto piu' forte dopo weekend calmi. P2: l'effetto della fonte
   e' un falso positivo fra 7 giorni testati: previsione: nessun vantaggio. P3: il lunedi'
   e' solo piu' volatile: previsione: R medio vicino a zero ma varianza piu' alta.
5. Come in tabella comune.
6. **Ipotesi.** Timeframe 1d (il meccanismo e' il giorno della settimana), long.
   * **V09 (long).** Alla chiusura della barra di domenica (UTC) → long all'apertura del
     lunedi'. Stop 5% sotto il close; «chiudi» dopo 1 barra. Nessun target.

## I-06 — Rottura di volatilita' dall'apertura del giorno (Larry Williams)

1. **Fonte.** Larry Williams, «Long-Term Secrets to Short-Term Trading», Wiley, 1999:
   entrare quando il prezzo supera l'apertura del giorno di una frazione del range del
   giorno prima, uscire alla fine del giorno.
2. **Affermazione.** Quando il prezzo supera l'apertura del giorno UTC di mezzo range
   (high − low) del giorno precedente, prosegue fino a fine giornata con un R medio
   superiore all'entrata casuale con la stessa uscita. Falsa se non batte la (b).
3. **Sotto-domande.** Vale di piu' nei giorni dopo un range stretto? A che ora arriva la
   rottura? Chi opera: chi entra sui movimenti forti di giornata, chi ha stop sopra.
4. **Spiegazioni proprie.** P1: inerzia di giornata (flussi che si concentrano): R
   positivo soprattutto con rotture presto nel giorno. P2: e' solo volatilita'
   (ingresso tardi su un movimento gia' fatto, poi ritorno): R negativo. P3: costi:
   tenute brevi con movimenti piccoli: R netto negativo anche con lordo positivo.
5. Come in tabella comune.
6. **Ipotesi.** Timeframe 1h (serve vedere il superamento dentro la giornata; la fonte
   entra con un ordine stop, qui all'apertura della barra dopo la chiusura oltre la
   soglia). Giorno = giorno UTC; range del giorno precedente dalle 24 barre orarie di quel
   giorno (serve averle tutte e 24, altrimenti nessun segnale); un solo ingresso per giorno
   e nessun segnale sulla barra delle 23:00 (non resterebbe tempo).
   * **V10 (long).** Close > apertura del giorno + 0,5 × range del giorno prima → long.
     Stop = apertura del giorno. «Chiudi» alla chiusura della barra delle 23:00 UTC
     (uscita all'apertura del giorno dopo).
   * **V11 (short).** Specchio: close < apertura del giorno − 0,5 × range → short; stop =
     apertura del giorno; stessa uscita.

## I-07 — Rottura dopo una compressione delle bande di Bollinger

1. **Fonte.** John Bollinger, «Bollinger on Bollinger Bands», McGraw-Hill, 2001: la
   «Squeeze», cioe' la larghezza delle bande al minimo degli ultimi mesi, precede
   un'espansione di volatilita'; la direzione la dice l'uscita dalle bande.
2. **Affermazione.** Una chiusura fuori dalla banda superiore (inferiore) entro poche
   barre da una compressione delle bande e' seguita da un movimento nella stessa direzione
   con R medio superiore all'entrata casuale con la stessa uscita. Falsa se non batte la
   (b).
3. **Sotto-domande.** Quanto dev'essere stretta la compressione? Chi opera: chi vende
   volatilita' e si copre all'uscita, ordini di stop accumulati ai bordi del range.
4. **Spiegazioni proprie.** P1: dopo la compressione la volatilita' si espande ma in
   direzione casuale: R long e short simili e vicini a zero. P2: false rotture
   («testa e spalle» della squeeze, Bollinger stesso le descrive): R negativo. P3:
   l'effetto e' solo la rottura di un canale (come I-02): R simile a V03/V04.
5. Come in tabella comune.
6. **Ipotesi.** Timeframe 4h. Bande di Bollinger(20, 2) sul close; larghezza = (banda
   superiore − inferiore) / media. Compressione = larghezza al minimo delle ultime 125
   barre (il periodo che Bollinger cita per la Squeeze; a 4 ore circa 21 giorni) in almeno
   una delle ultime 10 barre (compresa quella del segnale).
   * **V12 (long).** Compressione recente e close > banda superiore → long. Stop = close −
     2 × ATR(20). «Chiudi» quando il close scende sotto la media di 20.
   * **V13 (short).** Specchio: close < banda inferiore → short; stop = close + 2 ×
     ATR(20); «chiudi» quando il close supera la media di 20.

## I-08 — Il funding come misura dell'affollamento

1. **Fonte.** Songrun He, Asaf Manela, Omri Ross, Victor von Wachter, «Fundamentals of
   Perpetual Futures», arXiv 2212.06888, dicembre 2022: il funding lega il prezzo del
   perpetuo allo spot e misura lo squilibrio fra chi e' long e chi e' short a leva.
2. **Affermazione.** Quando il funding pagato all'ultimo settlement e' molto alto (i
   long a leva pagano molto per restare), nelle 24 ore successive il prezzo scende piu'
   di quanto farebbe un'entrata short a caso (V14); quando e' negativo (pagano gli short),
   sale piu' di un long a caso (V15). Falsa se non batte la (b).
3. **Sotto-domande.** Conta il livello o la variazione? Chi opera: chi e' a leva e viene
   liquidato, chi fa arbitraggio fra spot e perpetuo (vende il perpetuo caro). In quanto
   tempo: ore o giorni.
4. **Spiegazioni proprie.** P1: il funding alto e' un effetto del trend (sale perche'
   sale): previsione: lo short perde come la (b) short nei mesi di salita. P2:
   l'arbitraggio chiude il divario senza muovere il prezzo: R vicino a zero. P3:
   liquidazioni dei long affollati: discese rapide, guadagni nelle prime ore.
5. Come in tabella comune.
6. **Ipotesi.** Timeframe 8h (le barre coincidono con i settlement 00, 08, 16 UTC). Il
   funding usato e' l'ultimo settlement con ts ≤ chiusura della barra. Soglia alta 0,05%
   per 8 ore, cinque volte il livello base di Binance (0,01%): non scelta guardando i
   dati, ma come multiplo del tasso base.
   * **V14 (short).** Ultimo funding ≥ 0,0005 → short. Stop 5% sopra il close; «chiudi»
     dopo 3 barre (24 ore).
   * **V15 (long).** Ultimo funding < 0 → long. Stop 5% sotto il close; «chiudi» dopo 3
     barre.

## I-09 — Squilibrio degli ordini aggressivi

1. **Fonte.** Tarun Chordia, Avanidhar Subrahmanyam, «Order imbalance and individual
   stock returns: Theory and evidence», Journal of Financial Economics 72(3), 2004: lo
   squilibrio fra acquisti e vendite aggressivi di un giorno predice il rendimento del
   giorno dopo (con segno positivo).
2. **Affermazione.** Quando nelle ultime 24 ore la quota di volume comprato da ordini
   aggressivi (taker) e' fra le piu' alte dell'ultimo mese, il prezzo delle 24 ore
   successive sale piu' di un long a caso con la stessa uscita (V16); specchio per lo
   short (V17). Falsa se non batte la (b).
3. **Sotto-domande.** Persistenza degli ordini (chi spezza un ordine grande in piu'
   giorni) o pressione temporanea che poi rientra? Chi opera: chi accumula, chi copre.
4. **Spiegazioni proprie.** P1: ordini grandi spezzati nel tempo (persistenza dello
   squilibrio): V16 e V17 positive. P2: pressione temporanea che si inverte (gli
   intermediari si rifanno): R negativo. P3: lo squilibrio segue il prezzo (chi compra
   dopo che e' salito): previsione: uguale al momentum di I-01.
5. Come in tabella comune.
6. **Ipotesi.** Timeframe 4h. Squilibrio = (2 × volume taker in acquisto − volume) /
   volume, sommati sulle 6 barre fino a quella del segnale (24 ore). Soglia: sopra il
   90° percentile (sotto il 10°) dei valori delle 180 barre precedenti (30 giorni), una
   soglia relativa, non scelta sui risultati. Colonne `taker_buy_volume` e `volume` dei
   file klines.
   * **V16 (long).** Squilibrio > 90° percentile → long; stop = close − 2 × ATR(14);
     «chiudi» dopo 6 barre.
   * **V17 (short).** Squilibrio < 10° percentile → short; stop = close + 2 × ATR(14);
     «chiudi» dopo 6 barre.

## I-10 — Momentum di giornata (prima mezz'ora → ultima mezz'ora)

1. **Fonte.** Lei Gao, Yufeng Han, Sophia Zhengzi Li, Guofu Zhou, «Market intraday
   momentum», Journal of Financial Economics 129(2), agosto 2018: il rendimento della
   prima mezz'ora predice quello dell'ultima mezz'ora della stessa giornata.
2. **Affermazione.** Nel giorno UTC, se la mezz'ora 00:00-00:30 chiude in rialzo
   (ribasso), la mezz'ora 23:30-24:00 ha un R medio superiore a un long (short) di
   mezz'ora entrato a caso. Falsa se non batte la (b).
3. **Sotto-domande.** Su un mercato che non chiude, «inizio» e «fine» del giorno hanno
   senso? (Le chiusure giornaliere UTC sono quelle dei grafici e dei derivati con
   scadenza.) Chi opera: chi si ribilancia a fine giornata, chi copre posizioni prima del
   cambio di data.
4. **Spiegazioni proprie.** P1: ribilanciamenti di fine giornata nella direzione del
   giorno: effetto piu' forte nei giorni con prima mezz'ora ampia. P2: il giorno UTC non
   e' un confine per BTC: nessun effetto. P3: costi: mezz'ora di tenuta, movimento tipico
   dell'ordine dei costi: R netto negativo anche con un effetto lordo vero.
5. Come in tabella comune.
6. **Ipotesi.** Timeframe 30m. Il segnale arriva alla chiusura della barra 23:00-23:30 e
   guarda la barra 00:00-00:30 dello stesso giorno (deve esserci).
   * **V18 (long).** Prima mezz'ora con close > open → long sull'ultima mezz'ora. Stop 1%
     sotto il close; «chiudi» dopo 1 barra.
   * **V19 (short).** Prima mezz'ora con close < open → short sull'ultima mezz'ora. Stop
     1% sopra; «chiudi» dopo 1 barra.

## I-11 — I numeri tondi (ordini di stop oltre le soglie)

1. **Fonte.** Carol L. Osler, «Currency Orders and Exchange Rate Dynamics: An
   Explanation for the Predictive Success of Technical Analysis», Journal of Finance
   58(5), ottobre 2003: gli ordini stop si accumulano appena oltre i numeri tondi, quindi
   dopo il superamento di un numero tondo il movimento accelera nella stessa direzione.
2. **Affermazione.** Dopo una chiusura oraria che supera (dal basso) un multiplo di 1.000
   USDT, le 4 ore successive hanno un R medio long superiore a un long a caso con la
   stessa uscita (V20); specchio al ribasso (V21). Falsa se non batte la (b).
3. **Sotto-domande.** Vale per tutti i livelli o solo per i multipli di 5.000 e 10.000?
   Chi opera: chi ha ordini stop (short coperti, long protetti), chi entra sulla rottura.
4. **Spiegazioni proprie.** P1: cascata di stop: guadagno nelle prime ore. P2: ordini di
   presa di profitto SUL numero tondo (stessa fonte): il prezzo torna indietro, R
   negativo. P3: a 7.000 USDT un multiplo di 1.000 e' il 14% del prezzo, a 60.000 l'1,7%:
   l'effetto dipende dal livello di prezzo e quindi dall'anno (C9).
5. Come in tabella comune.
6. **Ipotesi.** Timeframe 1h. Superamento: close precedente < K ≤ close attuale, con K
   multiplo di 1.000 (al ribasso: close precedente ≥ K > close attuale). Se in una barra si
   superano piu' livelli conta il piu' lontano dal close precedente.
   * **V20 (long).** Superamento al rialzo → long; stop = K × 0,99 (1% sotto il numero
     tondo superato); «chiudi» dopo 4 barre.
   * **V21 (short).** Superamento al ribasso → short; stop = K × 1,01; «chiudi» dopo 4
     barre.

## I-12 — Il «martello» e la «stella cadente»

1. **Fonte.** Steve Nison, «Japanese Candlestick Charting Techniques», New York Institute
   of Finance, 1991: il martello dopo un ribasso annuncia un rimbalzo, la stella cadente
   dopo un rialzo annuncia una discesa.
2. **Affermazione.** Dopo un martello in un ribasso il prezzo delle 6 barre successive
   sale piu' di un long a caso (V22); dopo una stella cadente in un rialzo scende piu' di
   uno short a caso (V23). Falsa se non batte la (b).
3. **Sotto-domande.** Conta la lunghezza dell'ombra? Il volume? Chi opera: compratori
   che assorbono un'ondata di vendite (liquidazioni) dentro la barra.
4. **Spiegazioni proprie.** P1: assorbimento delle vendite forzate: rimbalzo. P2: i
   pattern a candela non predicono nulla (Marshall, Young e Rose, Journal of Banking &
   Finance 2006, su azioni USA): nessun vantaggio. P3: l'ombra lunga e' solo alta
   volatilita': R vicino a zero, varianza alta.
5. Come in tabella comune.
6. **Ipotesi.** Timeframe 4h. Range = high − low > 0; corpo = |close − open|. Martello:
   ombra inferiore (min(open, close) − low) ≥ 2 × corpo, ombra superiore (high −
   max(open, close)) ≤ 0,1 × range, corpo > 0; ribasso: close < close di 6 barre prima.
   Stella cadente: specchio (ombra superiore ≥ 2 × corpo, ombra inferiore ≤ 0,1 × range,
   close > close di 6 barre prima).
   * **V22 (long).** Martello in ribasso → long; stop = low della barra del martello (se
     sotto il close; altrimenti nessun segnale); «chiudi» dopo 6 barre.
   * **V23 (short).** Stella cadente in rialzo → short; stop = high della barra; «chiudi»
     dopo 6 barre.

## I-13 — Vicino al massimo di un anno (ancoraggio)

1. **Fonte.** Thomas J. George, Chuan-Yang Hwang, «The 52-Week High and Momentum
   Investing», Journal of Finance 59(5), ottobre 2004: chi e' vicino al massimo di 52
   settimane continua a salire, perche' gli operatori usano il massimo come ancora e
   reagiscono in ritardo alle buone notizie.
2. **Affermazione.** Quando il close giornaliero e' entro il 5% dal massimo degli high dei
   365 giorni precedenti, i 5 giorni successivi hanno un R medio long superiore a un long
   a caso con la stessa uscita. Falsa se non batte la (b).
3. **Sotto-domande.** Vale anche sopra il massimo (nuovi massimi)? Chi opera: chi vende
   «al massimo» per ancoraggio e frena la salita, poi cede.
4. **Spiegazioni proprie.** P1: ancoraggio: R positivo. P2: e' solo il trend (vicino al
   massimo vuol dire trend positivo): stesso R della (b) long nei periodi di salita. P3:
   resistenza al massimo: ritorno indietro, R negativo.
5. Come in tabella comune.
6. **Ipotesi.** Timeframe 1d (il meccanismo e' su un anno). Riscaldamento di 365 barre:
   la costruzione utile parte dal 2021.
   * **V24 (long).** Close ≥ 0,95 × massimo degli high delle 365 barre precedenti → long;
     stop 6% sotto il close; «chiudi» dopo 5 barre.
