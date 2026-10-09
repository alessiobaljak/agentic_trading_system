# Ipotesi della campagna GALAUSDT

Protocollo 4.5, Passo 3, Fase 1. Ogni idea è scritta qui PRIMA del suo primo test, con tutte le
sue varianti. Costruzione: dal 2021-09-01 al 2023-04-19 (596 giorni); validazione: dal
2023-04-20 al 2023-12-31 (log, voce GALAUSDT-N001). Minimo in costruzione: 70 trade, cioè in
media un ingresso ogni 8,5 giorni: le idee lente (candele da 1 giorno con segnali rari) rischiano
lo scarto, e lo dice `conta_trade`.

## Regole comuni a tutte le varianti

* Segnali sulle candele last chiuse; ingresso all'apertura della barra dopo; stop sul last,
  liquidazione sul mark (motore della sezione 7). Dimensione: rischio 1% del capitale, leva al
  massimo 2, margine isolato, costi: commissione 0,05% e slippage 0,05% per lato più funding.
* **Stop**: k ATR dal close della barra di segnale (o l'estremo indicato dall'idea), **mai oltre
  il 6% del prezzo**: è il tetto del bot (`stop_massimo_bot`), oltre il quale il bot non apre il
  trade; lo stop si stringe al 6% invece di scartare il trade.
* **Mesi esclusi**: nessun ingresso su segnali di barre dei mesi sotto i 20 milioni di USDT di
  volume medio giornaliero (`fase0_dati.md`); la posizione già aperta esce con la sua uscita.
  Stesso filtro per `conta_trade`, per il test e per la (a); le stesse barre sono vietate alla (b).
* **Costo di un giro in R** (per le previsioni, lezioni di metodo): 0,2% del prezzo (commissioni
  e slippage, andata e ritorno) diviso la distanza dello stop. Con uno stop del 2% sono 0,10 R,
  con uno del 4% 0,05 R, con uno dell'1% 0,20 R. Le previsioni sono scritte al netto dei costi.
* **Previsione numerica**: un intervallo per l'R medio dopo i costi in costruzione; si dice
  «corretta» se l'R medio cade nell'intervallo.
* **Spiegazioni concorrenti comuni** (valgono per ogni idea e non si ripetono per intero; ogni
  idea aggiunge le sue, fino ad almeno 10):
  - C1 **effetto casuale**: prevede un R medio vicino a quello delle entrate casuali (b), `t`
    contro la (b) fra -2 e 2; la smentisce un `t` contro la (b) oltre la soglia.
  - C2 **volatilità**: l'effetto vive solo nei periodi di alta volatilità (fine 2021, maggio e
    novembre 2022); prevede R medio concentrato in pochi mesi; la smentisce un R medio simile
    nei periodi calmi (R per anno, trade estremi).
  - C3 **trend di fondo**: in costruzione GALAUSDT è salita molto fino a novembre 2021 e poi è
    scesa per gran parte del 2022; una regola long (short) può guadagnare solo perché è long
    (short) in un mercato che sale (scende). Prevede che la (b), con la stessa direzione, faccia
    quasi lo stesso; la smentisce un vantaggio netto contro la (b).
  - C4 **artefatto dei dati**: buchi, barre tolte dall'allineamento, candele anomale; prevede
    trade concentrati vicino ai buchi o su barre con range enormi; la smentisce un risultato
    uguale togliendo i trade vicini ai buchi (si guarda solo se emerge un candidato).
  - C5 **effetto costi**: un vantaggio lordo piccolo mangiato dai costi; prevede R lordo positivo
    e R netto negativo; la smentisce un R netto positivo anche a costi doppi.
  - C6 **è solo il mercato**: GALAUSDT segue BTC e il mercato crypto; prevede che la stessa regola
    dia lo stesso segno su BTCUSDT e che i trade vincenti coincidano con i movimenti di BTC; la
    smentisce un effetto che c'è su GALAUSDT anche quando BTC è fermo, o che non c'è su BTC.

---

## I-01 Momentum di serie temporale

1. **Fonte**: Tobias J. Moskowitz, Yao Hua Ooi, Lasse Heje Pedersen, «Time series momentum»,
   Journal of Financial Economics 104(2), 2012. Per le crypto: Yukun Liu, Aleh Tsyvinski, «Risks
   and Returns of Cryptocurrency», NBER Working Paper 24877, agosto 2018 (poi Review of Financial
   Studies 2021): il rendimento passato di una o più settimane predice quello successivo.
2. **Affermazione verificabile**: quando il rendimento di GALAUSDT degli ultimi 7 giorni passa da
   negativo a positivo (da positivo a negativo), il prezzo continua nella stessa direzione per un
   tempo sufficiente a coprire i costi, più di quanto faccia un ingresso casuale nella stessa
   direzione con la stessa uscita.
3. **Sotto-domande**: vale solo con trend forti (fine 2021, 2022) o anche in laterale? Chi
   opera: investitori che reagiscono in ritardo all'informazione e inseguitori di tendenza
   (sotto-reazione e poi sovra-reazione); la durata attesa è di giorni o settimane; con molti
   incroci in laterale l'effetto si diluisce (falsi segnali).
4. **Spiegazioni concorrenti**: C1-C6, più
   - C7 *falsi incroci in laterale*: prevede molti trade brevi in perdita e pochi lunghi in
     guadagno, R medio dominato da 2-3 trade; la smentisce un R senza i 3 migliori ancora sopra la (b).
   - C8 *un solo regime*: tutto il guadagno nel ribasso 2022 per lo short (o nella salita di fine
     2021 per il long); prevede R per anno di segno diverso; la smentisce lo stesso segno nei due anni.
   - C9 *sotto-reazione alle notizie del progetto* (giochi, sblocchi di token): prevede effetto più
     forte dopo grandi movimenti; la smentisce un effetto uguale dopo movimenti piccoli.
   - C10 *liquidazioni a cascata*: un movimento forza le liquidazioni dei contratti a leva e il
     movimento continua; prevede effetto concentrato nelle prime ore dopo l'incrocio; la smentisce
     un effetto che arriva solo dopo giorni.
5. Previsioni e smentite: scritte sopra per ciascuna.
6. **Ipotesi**: GALAUSDT, momentum di serie temporale, candele da 4 ore (il segnale della fonte
   è settimanale; 4 ore danno un rendimento di 7 giorni aggiornato 6 volte al giorno senza il
   rumore delle candele brevi, e abbastanza incroci per i trade minimi), una variante long e una short.
   - Ingresso: il rendimento delle ultime 42 barre (7 giorni) passa da ≤ 0 a > 0 (long) o da ≥ 0
     a < 0 (short), alla chiusura della barra.
   - Uscita: il rendimento delle 42 barre torna ≤ 0 (long) o ≥ 0 (short). Stop: 2 ATR(14),
     al massimo il 6%. Nessun target.
   - **GALAUSDT-001** long; **GALAUSDT-002** short. Motivo delle due: l'effetto della fonte è
     simmetrico; in costruzione i due anni hanno trend opposti, quindi le due direzioni
     rispondono in modo diverso a C3 e C8.
   - Previsione: R medio dopo i costi fra -0,20 e +0,10 per entrambe; contro la (b) `t` sotto la
     soglia (incroci frequenti in laterale, costi 0,03-0,05 R a giro con stop del 4-6%).

## I-02 Rottura del canale di Donchian (le tartarughe)

1. **Fonte**: Curtis M. Faith, «Way of the Turtle», McGraw-Hill, 2007 (le regole del «Sistema 1»
   delle tartarughe di Richard Dennis: ingresso sulla rottura del massimo o minimo di 20 periodi,
   uscita sulla rottura opposta di 10 periodi, stop a 2 N con N la media del range vero di 20).
2. **Affermazione**: una chiusura oltre il massimo (minimo) delle 20 barre precedenti è seguita da
   un movimento nella stessa direzione che, tenuto fino alla rottura opposta di 10 barre, rende
   più delle entrate casuali con la stessa uscita.
3. **Sotto-domande**: le rotture vere si distinguono dalle false? Chi opera: chi ha ordini fermi
   oltre i massimi (stop dei venditori, ordini di acquisto in rottura); effetto nelle prime barre.
   Le regole originali sono su candele giornaliere: qui si usano 4 ore perché su 596 giorni le
   rotture di 20 giorni sarebbero poche decine.
4. **Spiegazioni concorrenti**: C1-C6, più
   - C7 *false rotture*: prevede tasso di vincita basso (sotto il 35%) con pochi grandi guadagni;
     la smentisce R senza i 3 migliori sopra la (b).
   - C8 *stop a cascata oltre il massimo*: prevede guadagno concentrato nella prima barra; la
     smentisce un guadagno distribuito su molte barre.
   - C9 *un solo regime* (come I-01 C8).
   - C10 *rottura su volume basso è rumore*: prevede risultati peggiori sulle rotture di notte
     (UTC); non si testa come filtro qui (sarebbe un ritocco nato dai fallimenti).
6. **Ipotesi**: 4 ore, ingresso sulla chiusura oltre il massimo (minimo) delle 20 barre precedenti;
   uscita sulla chiusura sotto il minimo (sopra il massimo) delle 10 barre precedenti; stop 2
   ATR(20), al massimo il 6%; nessun target.
   - **GALAUSDT-003** long; **GALAUSDT-004** short.
   - Previsione: R medio fra -0,20 e +0,15; contro la (b) `t` sotto la soglia. Famiglia di
     meccanismo uguale a I-01 (seguire la tendenza), ma con un ingresso diverso (rottura di un
     livello invece che segno del rendimento).

## I-03 RSI a 2 periodi con filtro di tendenza (ritorno verso la media)

1. **Fonte**: Larry Connors, Cesar Alvarez, «Short Term Trading Strategies That Work»,
   TradingMarkets Publishing, 2008 (comprare quando l'RSI a 2 periodi è sotto 5-10 con il prezzo
   sopra la media a 200, uscire quando il prezzo chiude sopra la media a 5).
2. **Affermazione**: dentro una tendenza di fondo, un eccesso di breve periodo contro la tendenza
   (RSI(2) estremo) rientra nelle barre successive più di quanto rientri un ingresso casuale.
3. **Sotto-domande**: l'eccesso è dovuto a chi chiede liquidità in fretta (liquidazioni, vendite
   forzate), compensato da chi la fornisce; il rientro dura poche barre. Vale nei mercati con
   tendenza debole; in un crollo il rientro può non arrivare (servono stop).
4. **Spiegazioni concorrenti**: C1-C6, più
   - C7 *prendere il coltello che cade*: in un crollo l'RSI resta estremo; prevede le perdite
     concentrate nei giorni di crollo (maggio, giugno, novembre 2022); la smentisce un R positivo
     anche escludendo quei mesi.
   - C8 *rimbalzo meccanico del rumore* (rimbalzo fra prezzo denaro e lettera): su 4 ore il rimbalzo
     è troppo piccolo rispetto ai costi; prevede R lordo positivo e netto negativo.
   - C9 *filtro di tendenza che fa tutto*: prevede che la (a) (senza RSI ma... la (a) toglie anche
     il filtro) sia simile; la smentisce il confronto con la (a).
   - C10 *liquidità fornita dai market maker*: prevede effetto più forte nelle ore di basso volume.
6. **Ipotesi**: candele da 4 ore (le regole della fonte sono giornaliere; 4 ore danno abbastanza
   eccessi per i trade minimi e un rientro abbastanza ampio rispetto ai costi). Long: close sopra
   la media semplice a 200 barre e RSI(2) sotto 10; uscita alla chiusura sopra la media a 5 barre.
   Short speculare: close sotto la media a 200 e RSI(2) sopra 90; uscita alla chiusura sotto la
   media a 5. Stop 3 ATR(14), al massimo il 6% (la fonte non usa stop; il bot lo richiede, quindi
   largo). Nessun target.
   - **GALAUSDT-005** long; **GALAUSDT-006** short.
   - Previsione: R medio fra -0,15 e +0,15; tasso di vincita alto (oltre il 55%) con perdite rare
     e grandi.

## I-04 Falsa rottura: la spazzata degli stop e il rientro

1. **Fonte**: Carol L. Osler, «Stop-loss orders and price cascades in currency markets», Journal
   of International Money and Finance 24(2), 2005: gli ordini stop si accumulano appena oltre i
   livelli visibili; quando il prezzo li tocca innescano una cascata, che si esaurisce quando gli
   stop sono stati eseguiti.
2. **Affermazione**: quando una barra da 1 ora scende sotto il minimo delle 48 barre precedenti
   (2 giorni) ma chiude di nuovo sopra quel minimo, gli stop sotto il minimo sono stati eseguiti
   senza che il prezzo trovasse altri venditori, e nelle 24 ore successive il prezzo sale più di
   quanto faccia un ingresso casuale. Speculare per lo short sopra il massimo.
3. **Sotto-domande**: quanto lontano oltre il livello arriva la spazzata? Chi opera: chi ha stop
   sotto i minimi (long a leva) e chi compra le loro vendite forzate; effetto in poche ore.
4. **Spiegazioni concorrenti**: C1-C6, più
   - C7 *rottura vera in ritardo*: il prezzo rientra ma poi rompe davvero; prevede molti stop nelle
     prime ore; la smentisce un tasso di stop non superiore alla (b).
   - C8 *rumore della barra*: ogni barra con ombra lunga rientra un po'; prevede la stessa
     differenza con la (a) e la (b) per qualunque ombra lunga, non solo oltre i minimi.
   - C9 *liquidazioni del mark*: prevede effetto più forte quando anche il mark tocca i livelli.
   - C10 *mercato in laterale*: l'effetto c'è solo nei periodi senza tendenza; prevede R per anno
     molto diverso fra 2021 e 2022.
6. **Ipotesi**: candele da 1 ora (la spazzata degli stop e il rientro avvengono in minuti o ore; 1
   ora coglie la barra intera e lascia ai costi un peso accettabile). Long: minimo della barra
   sotto il minimo delle 48 barre precedenti e close sopra quel minimo. Stop: minimo della barra
   meno 0,5 ATR(24), al massimo il 6%; target 2 volte la distanza dello stop; uscita a tempo dopo
   24 barre. Short speculare sul massimo.
   - **GALAUSDT-007** long; **GALAUSDT-008** short.
   - Previsione: R medio fra -0,20 e +0,10 (costo 0,08-0,15 R a giro con stop dell'1,5-2,5%).

## I-05 Funding estremo: il posizionamento a leva affollato

1. **Fonte**: Maik Schmeling, Andreas Schrimpf, Karamfil Todorov, «Crypto carry», BIS Working
   Papers n. 1087, aprile 2023: il premio dei futures crypto (carry, legato al funding dei
   perpetui) riflette la domanda di leva degli investitori al dettaglio che inseguono il trend;
   un carry alto precede rendimenti futuri più bassi e crolli.
2. **Affermazione**: quando il tasso di funding di GALAUSDT è sopra l'85° percentile degli ultimi
   30 giorni (90 regolamenti) ed è positivo, i long sono affollati e nelle 24 ore successive il
   prezzo scende più di quanto faccia uno short casuale; speculare per il funding molto negativo.
3. **Sotto-domande**: il funding estremo precede liquidazioni dei long a leva? Chi opera: chi
   paga funding alto per tenere la leva, e chi incassa vendendo il perpetuo; effetto in ore o
   giorni; il funding regolato è noto solo dopo il regolamento (nessun anticipo nel test).
4. **Spiegazioni concorrenti**: C1-C6, più
   - C7 *il funding segue il prezzo*: è alto dopo una salita; lo short dopo una salita è un ritorno
     verso la media del prezzo, non del posizionamento; prevede lo stesso risultato condizionando
     sulla salita e non sul funding.
   - C8 *incasso del funding*: lo short incassa il funding alto; prevede R positivo dovuto al
     funding più che al prezzo (si guarda il funding pagato).
   - C9 *funding fermo al tetto*: Binance limita il funding; molti valori uguali al tetto rendono il
     percentile poco informativo; prevede segnali a grappoli.
   - C10 *trend che continua*: con il trend forte il funding alto resta alto e il prezzo sale
     ancora; prevede perdite nei periodi di salita (fine 2021).
6. **Ipotesi**: candele da 8 ore, allineate ai regolamenti del funding (00, 08, 16 UTC), perché
   il segnale cambia solo a ogni regolamento. Short: funding regolato più recente sopra l'85°
   percentile dei 90 regolamenti precedenti e sopra 0. Long: sotto il 15° percentile e sotto 0.
   Uscita dopo 3 barre (24 ore); stop 2 ATR(14), al massimo il 6%; nessun target.
   - **GALAUSDT-009** short; **GALAUSDT-010** long.
   - Previsione: R medio fra -0,15 e +0,10.

## I-06 Ritardo rispetto a BTC

1. **Fonte**: Andrew W. Lo, A. Craig MacKinlay, «When are contrarian profits due to stock market
   overreaction?», Review of Financial Studies 3(2), 1990: i rendimenti dei titoli grandi
   precedono quelli dei piccoli (correlazione incrociata con ritardo): l'informazione comune
   arriva prima sui titoli grandi.
2. **Affermazione**: quando BTC fa in un'ora un movimento oltre 2 deviazioni standard e GALAUSDT
   nella stessa ora si è mosso meno di BTC, nelle 3 ore successive GALAUSDT recupera nella
   direzione di BTC più di quanto faccia un ingresso casuale.
3. **Sotto-domande**: quanto dura il ritardo (minuti o ore)? Chi opera: arbitraggisti fra monete e
   chi segue BTC; con molti operatori automatici il ritardo può essere di secondi, e allora non è
   catturabile su barre da 1 ora.
4. **Spiegazioni concorrenti**: C1-C6, più
   - C7 *ritardo già chiuso dentro l'ora*: prevede effetto nullo alla barra dopo; la smentisce un
     movimento successivo nella direzione di BTC.
   - C8 *beta basso*: GALAUSDT si muove meno di BTC per sua natura (non perché è in ritardo);
     prevede nessun recupero.
   - C9 *ritorno verso la media di BTC*: dopo un grande movimento BTC rimbalza e GALAUSDT con lui;
     prevede perdita del long dopo grandi salite di BTC.
   - C10 *notizie solo di BTC* (ETF, macro): non riguardano GALAUSDT; prevede nessun recupero.
6. **Ipotesi**: candele da 1 ora (il ritardo della fonte è di giorni sui titoli, ma sulle crypto
   l'informazione viaggia più in fretta; 1 ora è la candela più corta in cui i costi restano
   accettabili). Long: rendimento di BTC nella barra > 2 deviazioni standard delle 168 barre
   precedenti e rendimento di GALAUSDT nella barra minore di quello di BTC. Short speculare.
   Uscita dopo 3 barre; stop 2 ATR(24), al massimo il 6%.
   - **GALAUSDT-011** long; **GALAUSDT-012** short.
   - Previsione: R medio fra -0,25 e +0,05 (stop dell'1,5-3%, costo 0,07-0,13 R a giro).

## I-07 Barra stretta (NR7) e rottura

1. **Fonte**: Toby Crabel, «Day Trading with Short Term Price Patterns and Opening Range
   Breakout», Traders Press, 1990: dopo la barra con il range più stretto delle ultime 7 la
   volatilità tende a espandersi, e la direzione della prima rottura tende a continuare.
2. **Affermazione**: quando una barra da 4 ore è la più stretta delle ultime 7 e la barra
   successiva chiude oltre il suo massimo (minimo), il prezzo continua in quella direzione più
   di quanto faccia un ingresso casuale con lo stesso stop e target.
3. **Sotto-domande**: la compressione della volatilità precede un'espansione? Chi opera: chi
   piazza ordini in rottura e chi chiude coperture; effetto in poche barre.
4. **Spiegazioni concorrenti**: C1-C6, più
   - C7 *espansione senza direzione*: la volatilità sale ma la direzione è casuale; prevede R ≈ (b).
   - C8 *barre strette nelle ore notturne*: le barre strette sono quelle di basso volume (fine
     settimana, notte UTC); prevede rotture che falliscono quando torna il volume.
   - C9 *stop stretto*: lo stop all'estremo opposto della barra stretta è vicino e il rumore lo
     tocca spesso; prevede molti stop e costo alto in R.
   - C10 *rottura alla barra dopo già esaurita*: prevede perdita nella prima barra dopo l'ingresso.
6. **Ipotesi**: candele da 4 ore (la fonte è giornaliera; 4 ore danno abbastanza barre strette).
   Long: la barra precedente è la più stretta delle ultime 7 (range ≤ minimo dei range delle 7
   barre che finiscono in essa) e la barra corrente chiude sopra il suo massimo. Stop al minimo
   della barra stretta (al massimo il 6%); target 2 volte la distanza dello stop; uscita dopo 12
   barre (2 giorni). Short speculare.
   - **GALAUSDT-013** long; **GALAUSDT-014** short.
   - Previsione: R medio fra -0,20 e +0,10.

## I-08 Movimento grande con volume alto: continuazione

1. **Fonte**: Guillermo Llorente, Roni Michaely, Gideon Saar, Jiang Wang, «Dynamic Volume-Return
   Relation of Individual Stocks», Review of Financial Studies 15(4), 2002: i rendimenti
   accompagnati da volume alto continuano quando il commercio è speculativo (informato) e
   rientrano quando è di copertura; i titoli con molta asimmetria informativa mostrano continuazione.
2. **Affermazione**: un'ora con rendimento oltre 2 deviazioni standard (delle 168 ore precedenti)
   e volume in USDT oltre 2 volte la media delle 168 ore precedenti è seguita da 6 ore nella
   stessa direzione più di quanto lo sia un ingresso casuale.
3. **Sotto-domande**: GALAUSDT è una moneta piccola, con commercio speculativo e asimmetria
   informativa (annunci del progetto, sblocchi di token): per la fonte è il caso della
   continuazione. Chi opera: chi ha l'informazione per primo, poi chi insegue.
4. **Spiegazioni concorrenti**: C1-C6, più
   - C7 *liquidazioni*: il volume alto è fatto di liquidazioni forzate, che si esauriscono: prevede
     rientro, non continuazione.
   - C8 *pompa e scarico* (I-13): il volume enorme sui rialzi è una pompa organizzata: prevede
     rientro sul long.
   - C9 *notizie di BTC*: il volume alto è di tutto il mercato; prevede lo stesso effetto su BTC.
   - C10 *rendimenti a grappoli*: le ore grandi arrivano in gruppi (alta volatilità); prevede che
     l'effetto sparisca con il blocco del bootstrap (errore grande).
6. **Ipotesi**: candele da 1 ora (la fonte è giornaliera; sulle crypto la continuazione da volume
   informato si consuma in ore). Long dopo l'ora in salita con volume alto; short dopo l'ora in
   discesa con volume alto. Uscita dopo 6 barre; stop 2 ATR(24), al massimo il 6%.
   - **GALAUSDT-015** long; **GALAUSDT-016** short.
   - Previsione: R medio fra -0,20 e +0,10.

## I-09 Rottura di volatilità dall'apertura del giorno

1. **Fonte**: Larry Williams, «Long-Term Secrets to Short-Term Trading», Wiley, 1999: comprare
   quando il prezzo supera l'apertura del giorno di una frazione del range del giorno prima
   («volatility breakout»), e chiudere a fine giornata.
2. **Affermazione**: quando nel giorno UTC una barra da 1 ora chiude oltre apertura del giorno +
   0,5 × range del giorno prima (sotto apertura - 0,5 × range), il prezzo continua fino a fine
   giornata più di quanto faccia un ingresso casuale con la stessa uscita.
3. **Sotto-domande**: le crypto non hanno chiusura: la «giornata» UTC ha un significato (chiusura
   delle candele giornaliere, regolamento del funding alle 00)? Chi opera: chi guarda le candele
   giornaliere; l'effetto si consuma nella giornata.
4. **Spiegazioni concorrenti**: C1-C6, più
   - C7 *giornata arbitraria*: la mezzanotte UTC non conta per il mercato crypto; prevede R ≈ (b).
   - C8 *uscita a fine giornata casuale*: prevede risultato guidato dagli ingressi tardivi (poche ore).
   - C9 *volatilità del giorno prima*: dopo un giorno di range grande la soglia è lontana, e si
     entra solo nei giorni eccezionali; prevede trade concentrati nei crolli.
   - C10 *sessione americana*: le rotture vere arrivano con l'apertura dei mercati americani;
     prevede effetto concentrato fra le 13 e le 20 UTC.
6. **Ipotesi**: candele da 1 ora; livello = apertura della barra delle 00:00 UTC ± 0,5 × range
   del giorno UTC precedente completo (24 barre). Ingresso alla prima chiusura oltre il livello
   nel giorno (non nella barra delle 23); stop a 0,5 × range del giorno prima dal close di
   segnale (circa l'apertura del giorno), al massimo il 6%; uscita all'apertura delle 00:00
   (chiusura alla fine della barra delle 23). Nessun target.
   - **GALAUSDT-017** long; **GALAUSDT-018** short.
   - Previsione: R medio fra -0,20 e +0,10.

## I-10 Effetto del giorno della settimana (il lunedì)

1. **Fonte**: Guglielmo Maria Caporale, Alex Plastun, «The day of the week effect in the
   cryptocurrency market», Finance Research Letters 31, 2019: per BTC rendimenti anomali il lunedì
   (più alti degli altri giorni), non per le altre monete studiate.
2. **Affermazione**: il rendimento di GALAUSDT dalla mezzanotte UTC di lunedì alla mezzanotte di
   martedì è più alto di quello di un giorno casuale tenuto con la stessa uscita.
3. **Sotto-domande**: perché il lunedì? Il ritorno degli operatori istituzionali dopo il fine
   settimana, le notizie accumulate. L'effetto si manifesta in un giorno.
4. **Spiegazioni concorrenti**: C1-C6, più
   - C7 *effetto di pubblicazione*: dopo il 2019 l'effetto noto viene sfruttato e sparisce; prevede
     R ≈ (b).
   - C8 *solo BTC*: la fonte lo trova su BTC, non sulle altre monete; prevede nessun effetto su
     GALAUSDT.
   - C9 *fine settimana illiquido*: i movimenti del fine settimana si correggono il lunedì; prevede
     il segno del lunedì opposto a quello del fine settimana (non si testa come filtro qui).
   - C10 *pochi trade*: un lunedì a settimana dà circa 85 trade; il risultato dipende da pochi
     lunedì estremi; prevede R senza i 3 migliori molto più basso.
6. **Ipotesi**: candele da 1 giorno; long all'apertura del lunedì (segnale alla chiusura della
   domenica), uscita dopo 1 barra; stop 2 ATR(14), al massimo il 6%. Una sola variante (la fonte
   dà un effetto in una direzione).
   - **GALAUSDT-019** long.
   - Previsione: R medio fra -0,20 e +0,10.

## I-11 Valore relativo rispetto a BTC

1. **Fonte**: Evan Gatev, William N. Goetzmann, K. Geert Rouwenhorst, «Pairs Trading: Performance
   of a Relative-Value Arbitrage Rule», Review of Financial Studies 19(3), 2006: lo scarto fra
   due titoli che si muovono insieme, quando si allarga di 2 deviazioni standard, tende a
   richiudersi.
2. **Affermazione**: quando il rapporto GALAUSDT/BTC si allontana dalla sua media delle ultime 42
   barre da 4 ore (7 giorni) di oltre 2 deviazioni standard verso il basso (GALAUSDT «a buon
   mercato»), GALAUSDT sale più di un ingresso long casuale finché lo scarto si richiude.
   Speculare per lo short. Qui si opera solo su GALAUSDT, senza la gamba su BTC: il rischio del
   mercato resta (C6).
3. **Sotto-domande**: lo scarto si richiude perché GALAUSDT torna verso BTC o perché BTC torna
   verso GALAUSDT? Solo il primo caso guadagna qui. Chi opera: arbitraggisti fra monete.
4. **Spiegazioni concorrenti**: C1-C6, più
   - C7 *divergenza permanente*: GALAUSDT perde (o guadagna) valore rispetto a BTC per motivi
     propri (sblocchi di token, fine dell'interesse per i giochi); prevede scarti che non si
     richiudono e molte uscite a tempo in perdita.
   - C8 *è BTC che si muove*: lo scarto nasce da un movimento di BTC; prevede R legato al segno di BTC.
   - C9 *ritorno verso la media del prezzo di GALAUSDT*: lo scarto basso coincide con un crollo
     di GALAUSDT; prevede lo stesso effetto di un ritorno verso la media semplice.
   - C10 *uscita sullo scarto*: lo scarto si chiude anche se il prezzo non si muove a favore.
6. **Ipotesi**: candele da 4 ore. Indice: log(GALAUSDT) - log(BTCUSDT); z = scarto dalla media
   delle 42 barre diviso la deviazione standard delle 42 barre. Long con z < -2, short con z > 2;
   uscita quando z torna a 0 o dopo 18 barre (3 giorni); stop 2 ATR(14), al massimo il 6%.
   - **GALAUSDT-020** long; **GALAUSDT-021** short.
   - Previsione: R medio fra -0,20 e +0,10.

## I-12 Reazione eccessiva giornaliera: il giorno dopo continua

1. **Fonte**: Guglielmo Maria Caporale, Alex Plastun, «Price overreactions in the cryptocurrency
   market», Journal of Economic Studies 46(5), 2019: dopo un giorno di rendimento anomalo
   (sopra la media più k deviazioni standard), il giorno dopo il prezzo tende a muoversi nella
   stessa direzione della reazione eccessiva (non a rientrare).
2. **Affermazione**: dopo un giorno UTC con rendimento sopra media + 2 deviazioni standard dei 30
   giorni precedenti (sotto media - 2), il giorno dopo GALAUSDT continua nella stessa direzione
   più di un giorno casuale.
3. **Sotto-domande**: quanti giorni anomali ci sono in 596 giorni? Probabilmente poche decine per
   direzione: la stima dei trade dirà se l'idea si può provare.
4. **Spiegazioni concorrenti**: C1-C6, più
   - C7 *rientro dopo l'eccesso* (opposto della fonte): prevede R negativo.
   - C8 *pochi casi*: prevede risultato dominato da 2-3 giorni.
   - C9 *grappoli di volatilità*: i giorni anomali arrivano insieme; prevede l'effetto solo nei
     mesi di crollo.
   - C10 *notizie che si diffondono in più giorni*: prevede continuazione più forte dopo i giorni
     con volume alto.
6. **Ipotesi**: candele da 1 giorno; ingresso all'apertura del giorno dopo il giorno anomalo, nella
   direzione del giorno anomalo; uscita dopo 1 barra; stop 2 ATR(14), al massimo il 6%.
   - **GALAUSDT-022** long; **GALAUSDT-023** short.
   - Previsione: R medio fra -0,20 e +0,20. Probabile scarto per pochi trade.

## I-13 Pompa e scarico

1. **Fonte**: Josh Kamps, Bennett Kleinberg, «To the moon: defining and detecting cryptocurrency
   pump-and-dumps», Crime Science 7, 2018: le pompe organizzate si riconoscono da un salto di
   prezzo e di volume insieme, seguito dalla ricaduta del prezzo quando gli organizzatori vendono.
2. **Affermazione**: dopo un'ora con rendimento oltre 3 deviazioni standard e volume oltre 3
   volte la media (delle 168 ore precedenti), nelle 24 ore successive il prezzo scende più di
   quanto faccia uno short casuale.
3. **Sotto-domande**: GALAUSDT ha un mercato futures grande: le pompe organizzate sono più tipiche
   delle monete piccole sugli scambi a pronti; la ricaduta può arrivare in minuti. Chi opera:
   chi ha comprato per la pompa vende, e chi è arrivato tardi resta con il prezzo alto.
4. **Spiegazioni concorrenti**: C1-C6, più
   - C7 *notizia vera*: il salto è una notizia vera e il prezzo non ricade (continuazione, I-08):
     prevede perdite dello short.
   - C8 *ricaduta già avvenuta dentro l'ora*: prevede nessun effetto dopo.
   - C9 *squeeze degli short*: il salto è una cascata di liquidazioni degli short, che si esaurisce:
     prevede ricaduta (stessa direzione dell'ipotesi, meccanismo diverso).
   - C10 *pochi casi*: con soglie a 3 deviazioni standard gli eventi sono rari; prevede risultato
     dominato da pochi trade.
6. **Ipotesi**: candele da 1 ora; short dopo l'ora del salto; uscita dopo 24 barre; stop 2 ATR(24),
   al massimo il 6%. Una sola variante (la fonte descrive solo le pompe al rialzo).
   - **GALAUSDT-024** short.
   - Previsione: R medio fra -0,30 e +0,20. Possibile scarto per pochi trade.

---

## Varianti aggiunte dopo gli scarti per pochi trade (2026-10-09, 18:39 UTC)

Scritte dopo la registrazione delle 24 varianti (log, voci da GALAUSDT-001 a GALAUSDT-024) e
PRIMA di qualunque risultato di test: nessun test di queste idee era stato eseguito (la regola 6
ammette di allentare le soglie di uno scarto, senza aver visto risultati, come variante dell'idea
nuova). Gli scarti: GALAUSDT-003 e 004 (41 e 46 trade), 005 (53), 009 (41), 022 e 023 (20 e 15).

* **I-02, GALAUSDT-025 (long) e GALAUSDT-026 (short)**: le stesse regole delle tartarughe (20 e 10
  barre, stop 2 ATR(20) al massimo il 6%) su candele da **2 ore** invece che da 4. Motivo: con 20
  barre da 4 ore le rotture sono troppo rare; la candela da 2 ore tiene i parametri della fonte e
  dimezza la durata del canale (40 ore). Previsione: R medio fra -0,20 e +0,15.
* **I-03, GALAUSDT-027 (long)**: le regole di GALAUSDT-005 su candele da **2 ore** (RSI(2) < 10,
  close sopra la media a 200 barre, uscita sopra la media a 5, stop 3 ATR(14) al massimo il 6%).
  Motivo: in costruzione il prezzo è stato sotto la media lunga per gran parte del tempo e i
  segnali long con il filtro di tendenza sono pochi. Con GALAUSDT-006 fanno le due varianti della
  fonte. Previsione: R medio fra -0,15 e +0,15.
  **RITIRATA** (log, correzione GALAUSDT-N007): il risultato di GALAUSDT-006, prima variante
  testata di I-03, era già nel log (18:39:12 UTC) quando questa variante è stata scritta. Non si
  registra e non si testa.
* **I-05, GALAUSDT-028 (short)**: le regole di GALAUSDT-009 con il **70° percentile** invece
  dell'85° (funding regolato sopra il 70° percentile dei 90 precedenti e positivo, uscita dopo 3
  barre da 8 ore, stop 2 ATR(14) al massimo il 6%). Motivo: con l'85° i segnali sono 41. Con
  GALAUSDT-010 fanno le due varianti della fonte. Previsione: R medio fra -0,15 e +0,10.
* **I-12**: nessuna variante allentata. Per arrivare a 70 trade la soglia dovrebbe scendere verso
  1 deviazione standard, che non è più una «reazione eccessiva» nel senso della fonte: l'idea
  resta uno scarto per pochi trade.

---

## Idee nuove aggiunte dopo i primi risultati (2026-10-09, circa 18:45 UTC)

Dopo i test delle varianti 1-18 restano 12 unità di budget: con le tre varianti allentate valide
(025, 026, 028) ne restano 9, e la regola 6 vuole prima le idee nuove con fonte. Le quattro idee
qui sotto erano nell'elenco di partenza della sessione (scritto prima di caricare i prezzi, ma non
in questo file); sono scritte qui DOPO aver letto la tabella dei risultati delle varianti 1-18, e
lo si dichiara: nessuna è un ritocco di quelle varianti, e nessuna nasce dai loro numeri. Il
rischio da dichiarare è un altro: I-17 è un momentum di breve, e le varianti 1-18 vicine alla
soglia (011, 015, 014, 017) sono di quel tipo. Le altre tre sono famiglie nuove.

## I-14 Periodicità oraria dei rendimenti

1. **Fonte**: Steven L. Heston, Robert A. Korajczyk, Ronnie Sadka, «Intraday Patterns in the
   Cross-Section of Stock Returns», Journal of Finance 65(4), 2010: il rendimento di un titolo in
   una mezz'ora del giorno predice il rendimento nella stessa mezz'ora dei giorni successivi, per
   settimane (ordini di grandi operatori spezzati e ripetuti alla stessa ora, flussi periodici).
2. **Affermazione**: se nelle ultime 20 giornate l'ora h di GALAUSDT ha avuto un rendimento medio
   positivo (negativo) in modo marcato (media divisa per il suo errore oltre 1,5), l'ora h di oggi
   rende più (meno) di un'ora casuale.
3. **Sotto-domande**: le crypto hanno flussi periodici (regolamento del funding alle 00, 08, 16;
   apertura delle borse asiatiche, europee, americane)? Chi opera: operatori che eseguono ogni
   giorno alla stessa ora. L'effetto dura un'ora.
4. **Spiegazioni concorrenti**: C1-C6, più
   - C7 *volatilità per ora* (le ore americane muovono di più, senza direzione): prevede R ≈ (b).
   - C8 *ora del funding*: il movimento attorno ai regolamenti; prevede segnali concentrati alle 00,
     08, 16.
   - C9 *rumore delle 20 osservazioni*: con 20 giorni la media è quasi tutta rumore; prevede R ≈ (b).
   - C10 *costi*: un'ora tenuta con stop di 2 ATR costa circa 0,08-0,10 R; prevede R netto negativo
     anche con un vantaggio lordo piccolo.
6. **Ipotesi**: candele da 1 ora. Per ogni ora del giorno: media e deviazione standard dei
   rendimenti (close/open - 1) di quell'ora nelle ultime 20 giornate in cui c'è; z = media /
   (deviazione / radice di 20). Alla chiusura della barra, se l'ora successiva ha z > 1,5 → long
   (z < -1,5 → short) per una barra; stop 2 ATR(24), al massimo il 6%.
   - **GALAUSDT-029** long; **GALAUSDT-030** short.
   - Previsione: R medio fra -0,20 e +0,05.

## I-15 Scarto fra prezzo del perpetuo e mark price

1. **Fonte**: Songrun He, Asaf Manela, Omri Ross, Victor von Wachter, «Fundamentals of Perpetual
   Futures», arXiv 2212.06888, dicembre 2022: il prezzo del perpetuo si scosta dal prezzo a pronti,
   e lo scarto si richiude per l'arbitraggio e il funding. Il mark price di Binance è costruito dal
   prezzo a pronti (indice) più una media dello scarto: last - mark misura lo scarto di breve.
2. **Affermazione**: quando alla chiusura di un'ora il last è sotto il mark più del solito (scarto
   sotto la media delle 168 ore precedenti di oltre 2 deviazioni standard), nelle 2 ore successive
   il last sale più di un ingresso long casuale (lo scarto si richiude dal lato del perpetuo).
   Speculare per lo short.
3. **Sotto-domande**: lo scarto si chiude in secondi (arbitraggisti automatici) o in ore? Si
   richiude muovendo il perpetuo o l'indice? Solo il primo caso guadagna.
4. **Spiegazioni concorrenti**: C1-C6, più
   - C7 *scarto chiuso dall'indice*: il prezzo a pronti scende verso il perpetuo; prevede R ≈ (b).
   - C8 *scarto chiuso in secondi*: alla chiusura dell'ora lo scarto è già un residuo; prevede nessun
     effetto.
   - C9 *crollo in corso*: last sotto mark durante le vendite forzate; il prezzo continua a scendere;
     prevede perdite del long nei giorni di crollo.
   - C10 *rumore della chiusura*: il last della chiusura è un solo scambio, il mark è una media;
     prevede rientro meccanico piccolo, mangiato dai costi.
6. **Ipotesi**: candele da 1 ora; scarto = (close last - close mark) / close mark; z rispetto a
   media e deviazione delle 168 barre precedenti. Long con z < -2, short con z > 2; uscita dopo 2
   barre; stop 2 ATR(24), al massimo il 6%.
   - **GALAUSDT-031** long; **GALAUSDT-032** short.
   - Previsione: R medio fra -0,20 e +0,05.

## I-16 Numeri tondi: ordini di presa di profitto

1. **Fonte**: Carol L. Osler, «Currency Orders and Exchange Rate Dynamics: An Explanation for the
   Predictive Success of Technical Analysis», Journal of Finance 58(5), 2003: gli ordini di presa di
   profitto si accumulano sui numeri tondi, quindi una tendenza si ferma e torna indietro più spesso
   quando arriva su un numero tondo.
2. **Affermazione**: quando in un'ora il prezzo sale fino al primo numero tondo sopra il close
   precedente e chiude sotto di esso (rifiutato), nelle 24 ore successive scende più di uno short
   casuale. Speculare per il long sul numero tondo sotto.
3. **Sotto-domande**: cos'è «tondo» per una moneta da pochi centesimi? Qui: multipli di metà della
   potenza di 10 del prezzo (per 0,035: 0,030, 0,035, 0,040; per 0,35: 0,30, 0,35, 0,40). Chi
   opera: piccoli operatori con ordini su prezzi tondi.
4. **Spiegazioni concorrenti**: C1-C6, più
   - C7 *qualunque massimo rifiutato rientra*: prevede lo stesso effetto per livelli non tondi
     (stessa logica di I-04).
   - C8 *livelli troppo radi*: con passi del 10-40% del prezzo gli eventi sono pochi; prevede scarto
     o risultato da pochi trade.
   - C9 *stop oltre il tondo*: superato il tondo gli stop accelerano (la stessa fonte); prevede che i
     rifiuti falliscano spesso e in grande.
   - C10 *trend di fondo*: nel ribasso del 2022 i rifiuti sui tondi sopra funzionano solo perché il
     prezzo scende comunque (C3).
6. **Ipotesi**: candele da 1 ora; passo u = 10^floor(log10 close precedente) / 2. Short: livello L =
   primo multiplo di u sopra il close precedente; massimo della barra ≥ L e close < L. Stop: L più
   0,5 ATR(24) (distanza dal close, al massimo il 6%); target 2 R; uscita dopo 24 barre. Long
   speculare con il primo multiplo sotto il close precedente.
   - **GALAUSDT-033** short; **GALAUSDT-034** long.
   - Previsione: R medio fra -0,20 e +0,10.

## I-17 Momentum dentro la giornata

1. **Fonte**: Lei Gao, Yufeng Han, Sophia Zhenzhen Li, Guofu Zhou, «Market intraday momentum»,
   Journal of Financial Economics 129(2), 2018: il rendimento della prima mezz'ora del giorno
   predice quello dell'ultima mezz'ora (operatori informati e ribilanciamenti a fine giornata).
2. **Affermazione**: con la giornata UTC, se la prima mezz'ora (00:00-00:30) chiude in salita
   (discesa), l'ultima mezz'ora (23:30-24:00) rende più (meno) di una mezz'ora casuale.
3. **Sotto-domande**: le crypto non chiudono: c'è un «fine giornata»? La chiusura delle candele
   giornaliere UTC e il regolamento del funding delle 00:00 sono punti di riferimento comuni.
4. **Spiegazioni concorrenti**: C1-C6, più
   - C7 *nessuna giornata nelle crypto*: prevede R ≈ (b).
   - C8 *funding delle 00:00*: chi chiude prima del regolamento muove l'ultima mezz'ora; prevede un
     effetto legato al segno del funding, non della prima mezz'ora.
   - C9 *costi*: una mezz'ora con stop di 2 ATR(48) (circa 1-1,5%) costa 0,13-0,20 R; prevede R netto
     negativo.
   - C10 *pochi grandi giorni*: prevede R dominato dai giorni di crollo.
6. **Ipotesi**: candele da 30 minuti; segnale alla chiusura della barra delle 23:00 (ingresso alle
   23:30), long se la barra delle 00:00 dello stesso giorno ha close > open, short se close < open;
   uscita dopo 1 barra (alle 00:00); stop 2 ATR(48), al massimo il 6%.
   - **GALAUSDT-035** long; **GALAUSDT-036** short.
   - Previsione: R medio fra -0,30 e +0,05.

Ordine di registrazione: 025, 026, 028, poi 029-036. Le varianti oltre la trentesima unità di
budget non si testano.

---

Famiglie di meccanismi coperte dalle idee nuove: seguire la tendenza (I-01, I-02), ritorno
verso la media di breve (I-03), microstruttura e stop (I-04), posizionamento a leva (I-05),
ritardo fra monete (I-06), compressione della volatilità (I-07), volume e informazione (I-08,
I-13), rottura intra-giornaliera (I-09), calendario (I-10), valore relativo (I-11), reazione
eccessiva giornaliera (I-12).
