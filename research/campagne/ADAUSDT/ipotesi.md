# ADAUSDT — ipotesi (Fase 1)

Scritto il 2026-10-09, prima di qualunque conteggio o test delle varianti qui sotto. Tutte le idee
e tutte le loro varianti sono scritte insieme, prima del primo test (regola 6). Il codice esatto di
ogni variante è in `codice/varianti.py`; questo file dice perché.

## Fatti comuni usati per le previsioni (solo prezzi, nessuna strategia)

Da `codice/costi.py` sui dati di costruzione (2020-01-31 → 2022-10-18). Un giro (andata e
ritorno) costa 0,14% del nozionale (commissione 0,05% + slippage 0,02% per lato). ATR(14) mediano in
percentuale del prezzo: 15m 0,72%; 30m 1,04%; 1h 1,50%; 4h 3,10%; 8h 4,49%; 1d 8,24%. Quindi il costo
di un giro in R, con lo stop a k ATR: 15m 0,19/k; 30m 0,135/k; 1h 0,093/k; 4h 0,045/k; 8h 0,031/k;
1d 0,017/k. Più il funding: nel 2020-2021 il tasso medio era +0,024-0,036% ogni 8 ore (un costo
per i long, un incasso per gli short).

**Stop e bot.** Lo stop massimo del bot è il 6% (`stop_massimo_bot`). Gli stop a 2-3 ATR su 4h
(6-9%) e su 1d (16-25%) lo superano: quelle varianti, se diventassero candidati, il bot non potrebbe
eseguirle così come sono (si dichiara in consegna). La scelta è voluta: lo stop deve stare fuori dal
rumore del timeframe del meccanismo, e restringerlo per il bot cambierebbe l'idea.

**Il «mercato».** ADA nel periodo di costruzione ha avuto un rialzo enorme (2020-2021) e un crollo
(2022): la tendenza di fondo e il legame con BTC sono le spiegazioni noiose più forti per ogni idea,
e le misura la baseline (b) (stesse entrate casuali, stessa direzione e stessa uscita).

Le varianti di ogni idea sono al massimo due (lezioni di metodo): di solito long e short dello stesso
meccanismo, oppure lo stesso meccanismo su due timeframe quando la fonte è a un timeframe che su
questa moneta non darebbe abbastanza trade.

Formato di ogni idea: fonte; affermazione verificabile; sotto-domande; spiegazioni concorrenti (con
cosa prevedono e cosa le smentirebbe); ipotesi completa; varianti.

---

## I-01 — Momentum a serie temporale (una settimana)

**Fonte.** Tobias J. Moskowitz, Yao Hua Ooi, Lasse Heje Pedersen, «Time Series Momentum», Journal of
Financial Economics 104(2), maggio 2012. Per le crypto: Yukun Liu, Aleh Tsyvinski, «Risks and Returns
of Cryptocurrency», NBER Working Paper 24877, agosto 2018 (poi Review of Financial Studies 2021): il
rendimento delle settimane passate predice quello della settimana dopo, legato all'attenzione degli
investitori.

**Affermazione.** Su ADA, dopo una settimana (42 barre da 4 ore) con rendimento positivo, i 7 giorni
successivi rendono in media più di un ingresso a caso nella stessa direzione; dopo una settimana
negativa, rendono meno (per lo short, di più).

**Sotto-domande.** Vale di più nei movimenti grandi o in tutti? In alta volatilità? Chi compra:
investitori al dettaglio che arrivano dopo aver visto il rialzo (attenzione), fondi di tendenza.
Quando: su orizzonti di giorni-settimane, non di ore. Si esaurisce entro 1-4 settimane secondo la
fonte.

**Spiegazioni concorrenti.**
1. *Caso.* Prevede: t contro la (b) vicino a 0. Smentita: t netto e stabile negli anni.
2. *Trend di fondo (2021 rialzo, 2022 ribasso).* Prevede: i long vanno bene solo nel 2021, gli short solo nel 2022, e la (b) nella stessa direzione fa lo stesso. Smentita: battere la (b) in entrambi gli anni.
3. *È solo il mercato (BTC).* Prevede: il segnale funziona solo quando anche BTC ha la settimana nella stessa direzione; la (b) lo assorbe in parte. Smentita: vantaggio anche nelle settimane in cui ADA e BTC divergono (studio dei fallimenti).
4. *Volatilità.* Stop a 3 ATR: dopo settimane forti la volatilità è alta e lo stop largo; il risultato in R potrebbe venire dalla dimensione, non dalla direzione. Prevede: R medio simile a quello della (b) in alta volatilità. Smentita: differenza dalla (b) che resta dentro le stesse fasce di volatilità.
5. *Costi.* 0,015 R a giro più funding (long nel 2021 pagano ~0,1% al giorno). Prevede: lordo positivo, netto vicino a zero per i long. Smentita: netto positivo.
6. *Pochi trade estremi.* Il rialzo del 2021 ha settimane da +50%: prevede R medio che crolla senza i 3 migliori. Smentita: R senza i 3 migliori ancora sopra la (b).
7. *Artefatto dei dati.* Buchi del mark (2022-10-02) e inizio a fine gennaio 2020: pochi trade toccati; prevede nessun effetto sul totale.
8. *Uscita a tempo.* L'uscita a 7 giorni cattura il movimento a caso; prevede (a) ≈ variante. Smentita: battere la (a), che ha la stessa uscita senza la condizione.
9. *Regime di liquidità (2020).* Nel 2020 il volume era basso: movimenti meno informativi. Prevede differenze grandi fra 2020 e 2021-22.
10. *Inversione a breve.* Dopo una settimana forte i primi giorni ritracciano (inversione) e lo stop scatta: prevede molti stop nei primi 2-3 giorni. Smentita: stop distribuiti nel tempo come nella (b).

**Ipotesi completa.** ADAUSDT, meccanismo di sotto-reazione e attenzione, 4h (rendimento a 7 giorni
calcolato ogni 4 ore, così l'ingresso non aspetta la fine della settimana di calendario), posizioni
di 7 giorni.

**Varianti.**
* ADAUSDT-001: 4h, long. Ingresso se il rendimento delle ultime 42 barre è > 0; uscita dopo 42
  barre (all'apertura della barra successiva); stop 3 ATR(14). Motivo: la regola della fonte (segno
  del rendimento passato, tenuta pari alla finestra).
* ADAUSDT-002: 4h, short, stesse regole con rendimento < 0. Motivo: la fonte è simmetrica.

---

## I-02 — Rottura del canale di prezzo (regole delle «tartarughe»)

**Fonte.** Curtis M. Faith, «Way of the Turtle», McGraw-Hill, 2007 (le regole del sistema 1 di
Richard Dennis: ingresso alla rottura del massimo di 20 periodi, uscita al minimo di 10). Il
meccanismo: gli ordini di stop e di ingresso si accumulano oltre i massimi recenti; quando il prezzo
li supera partono acquisti a catena e la tendenza si estende.

**Affermazione.** Su ADA, una chiusura sopra il massimo delle 20 barre da 4 ore precedenti è seguita
da un movimento al rialzo che, uscendo alla chiusura sotto il minimo delle 10 barre precedenti, rende
in media più di un ingresso a caso con la stessa uscita (e simmetricamente per lo short).

**Sotto-domande.** Vale più nelle rotture dopo un periodo calmo? Con volume alto? Chi compra: chi ha
ordini di stop sopra il massimo (short che chiudono), chi segue la tendenza. Quanto dura: giorni.

**Spiegazioni concorrenti.**
1. *Caso.* t vicino a 0 contro la (b).
2. *Trend di fondo.* Long buoni solo nel 2021; la (b) long li ha anch'essa. Smentita: battere la (b).
3. *Solo il mercato.* Le rotture di ADA coincidono con quelle di BTC. Prevede vantaggio solo con BTC che rompe. Smentita: vantaggio anche quando BTC no.
4. *Falsi segnali in laterale.* Prevede molti piccoli stop e pochi grandi guadagni: R asimmetrico, risultato in mano a pochi trade. Smentita: R senza i 3 migliori positivo.
5. *Uscita che fa tutto.* L'uscita al minimo di 10 barre è una regola di tendenza in sé: la (a) la ha uguale. Smentita: battere la (a).
6. *Costi.* 0,023 R a giro con stop a 2 ATR: poco. Prevede costi non decisivi.
7. *Volatilità.* Le rotture avvengono in alta volatilità, stop più largo: misura la (b) sulle barre valide.
8. *Inversione dopo la rottura (falsa rottura).* Prevede ritorno sotto il massimo nelle prime barre e stop.
9. *Funding.* I long nel 2021 pagano funding alto: prevede R dei long peggiore del lordo.
10. *Artefatto dei dati.* Le barre del 2022-10-02 mancanti creano un salto: un trade al massimo.

**Ipotesi completa.** ADAUSDT, ordini accumulati oltre i massimi e minimi recenti, 4h (le regole a 20
e 10 periodi della fonte sono giornaliere: su candele giornaliere ADA darebbe poche decine di
rotture in 2,7 anni; a 4 ore il meccanismo degli ordini oltre i massimi recenti è lo stesso).

**Varianti.**
* ADAUSDT-003: 4h, long. Ingresso se la chiusura supera il massimo (high) delle 20 barre precedenti;
  uscita alla chiusura sotto il minimo (low) delle 10 barre precedenti; stop 2 ATR(14). Motivo:
  regole della fonte, stop a 2 ATR come nella fonte (2N).
* ADAUSDT-004: 4h, short simmetrico (chiusura sotto il minimo di 20, uscita sopra il massimo di 10).

---

## I-03 — Prezzo sopra la media mobile (apprendimento sui fondamentali difficili da valutare)

**Fonte.** Andrew Detzel, Hong Liu, Jack Strauss, Guofu Zhou, Yingzi Zhu, «Learning and
Predictability via Technical Analysis: Evidence from Bitcoin and Stocks with Hard-to-Value
Fundamentals», Financial Management 50(1), 2021 (prima come working paper SSRN, 2018). Anche William
Brock, Josef Lakonishok, Blake LeBaron, «Simple Technical Trading Rules and the Stochastic Properties
of Stock Returns», Journal of Finance 47(5), dicembre 1992. Meccanismo: quando i fondamentali sono
difficili da valutare, gli investitori imparano dal prezzo stesso; il rapporto fra prezzo e media
mobile riassume ciò che si è imparato e predice i rendimenti giornalieri.

**Affermazione.** Su ADA, quando la chiusura giornaliera passa sopra la media mobile a 20 giorni, la
posizione long tenuta finché la chiusura resta sopra la media rende più di un ingresso a caso con la
stessa uscita.

**Sotto-domande.** Vale nelle fasi di incertezza (alta volatilità) più che nelle calme? Chi compra: chi
aggiorna le sue stime guardando il prezzo. Quanto dura: giorni-settimane.

**Spiegazioni concorrenti.**
1. *Caso.* t vicino a 0.
2. *Trend di fondo 2020-21.* Prevede tutti i guadagni nel 2021. Smentita: battere la (b) anche nel 2022 (meno trade).
3. *Solo il mercato.* Le medie di ADA e BTC si incrociano insieme; prevede che il vantaggio sparisca quando BTC è sotto la sua media.
4. *Molti falsi incroci.* Prevede tanti piccoli stop-out per l'uscita alla media, pochi trade grandi: R senza i 3 migliori negativo.
5. *Uscita che fa tutto.* La (a) ha la stessa uscita sotto la media: entra solo quando il prezzo è sopra la media (segnale valido sempre), quindi la condizione (l'incrocio) deve aggiungere qualcosa.
6. *Costi.* 0,006 R a giro: trascurabili; funding dei long alto nel 2021.
7. *Volatilità.* Stop a 3 ATR giornalieri (~25%): lo stop scatta di rado; R guidato dall'uscita.
8. *Pochi trade.* Gli incroci giornalieri sono forse 30-50 in 2,7 anni: probabile scarto per trade minimi (non consuma budget).
9. *Artefatto dei dati.* Due giornate mancanti: effetto trascurabile.
10. *Ritardo della media.* L'incrocio arriva tardi e cattura la parte finale del movimento: prevede R medio negativo e peggiore della (b).

**Ipotesi completa.** ADAUSDT, apprendimento dal prezzo, 1d (la fonte è giornaliera), long (la fonte
studia la previsione dei rialzi e la versione long; lo short sarebbe una seconda idea).

**Varianti.**
* ADAUSDT-005: 1d, long. Ingresso alla chiusura che passa sopra la media semplice a 20 giorni (la
  chiusura precedente era sotto o uguale); uscita alla prima chiusura sotto la media; stop 3 ATR(14).
  Motivo: la regola prezzo/media mobile della fonte con la finestra a 20 giorni, fra le sue finestre.

---

## I-04 — Reazioni eccessive giornaliere: inerzia il giorno dopo

**Fonte.** Guglielmo Maria Caporale, Alex Plastun, «Price overreactions in the cryptocurrency
market», Journal of Economic Studies 46(5), 2019 (working paper CESifo n. 6861, gennaio 2018). Una
giornata è una reazione eccessiva quando il suo rendimento (chiusura su apertura) supera la media
più k deviazioni standard dei rendimenti assoluti dei giorni precedenti. Il loro risultato: il
giorno dopo una reazione eccessiva il prezzo si muove di più nella STESSA direzione (inerzia); la
strategia contraria non rende.

**Affermazione.** Su ADA, dopo un giorno con rendimento oltre la media più una deviazione standard
dei rendimenti assoluti dei 30 giorni prima, il giorno successivo nella stessa direzione rende più di
un giorno preso a caso con la stessa uscita.

**Sotto-domande.** Vale più per i rialzi o per i ribassi? Chi opera: chi arriva tardi sulla notizia,
liquidazioni a catena delle posizioni con leva. Quando: entro un giorno.

**Spiegazioni concorrenti.**
1. *Caso.* t vicino a 0; la fonte stessa dice che la versione con un robot di trading non si distingue dal caso.
2. *Trend di fondo.* I giorni forti al rialzo sono nel 2021: il long vince perché il 2021 sale. La (b) lo misura.
3. *Solo il mercato.* Le giornate forti sono giornate di BTC: prevede inerzia solo se anche BTC ha la giornata forte.
4. *Volatilità a grappoli.* Dopo un giorno grande la volatilità resta alta: lo stop a 2 ATR scatta più spesso, e con l'uscita a un giorno l'R è dominato dal rumore.
5. *Inversione (rimbalzo).* L'opposto della fonte: dopo l'eccesso il prezzo torna indietro. Prevede R medio negativo e sotto la (b).
6. *Costi.* 0,008 R a giro: piccoli. Funding alto dopo i rialzi forti (i long pagano).
7. *Pochi trade estremi.* Pochi giorni enormi fanno tutto.
8. *Artefatto dell'ora di chiusura.* La giornata UTC è arbitraria per un mercato 24 ore: prevede un effetto debole e instabile.
9. *Pochi trade.* Con k = 1 forse il 10-15% dei giorni per lato: vicino al minimo di 70.
10. *Notizie di una sola moneta (aggiornamenti della rete).* Eventi specifici di ADA concentrati in pochi mesi: prevede risultato concentrato in un anno.

**Ipotesi completa.** ADAUSDT, inerzia dopo una reazione eccessiva, 1d (la fonte è giornaliera),
posizione di un giorno.

**Varianti.**
* ADAUSDT-006: 1d, long dopo un giorno con (chiusura/apertura − 1) > media + 1 deviazione standard dei
  rendimenti assoluti dei 30 giorni precedenti; uscita all'apertura del giorno dopo l'ingresso; stop 2
  ATR(14). Motivo: la regola della fonte (30 giorni, k = 1 fra i suoi valori).
* ADAUSDT-007: 1d, short dopo un giorno con rendimento < −(stessa soglia), stessa uscita e stop.

---

## I-05 — Momento infragiornaliero: la prima mezz'ora predice l'ultima

**Fonte.** Zhuzhu Wen, Elie Bouri, Yahua Xu, Yang Zhao, «Intraday return predictability in the
cryptocurrency markets: Momentum, reversal, or both», North American Journal of Economics and
Finance 62, 2022 (Bitcoin 2013-2020; anche Ethereum, Litecoin, Ripple). Prima, per le azioni: Lei Gao,
Yufeng Han, Sophia Zhonghe Li, Guofu Zhou, «Market Intraday Momentum», Journal of Financial Economics
129(2), 2018. Meccanismo dichiarato: investitori informati tardi (momento) e ribilanciamenti di fine
giornata.

**Affermazione.** Su ADA, il segno del rendimento della prima mezz'ora della giornata UTC (00:00-00:30)
predice il segno dell'ultima mezz'ora (23:30-24:00): entrando alle 23:30 nella direzione della prima
mezz'ora e uscendo alle 24:00 si guadagna più che entrando a caso con la stessa uscita.

**Sotto-domande.** Vale nei giorni di prima mezz'ora grande? Nei giorni di annunci? Chi opera alla
fine della giornata UTC: chi chiude o ribilancia sul prezzo di chiusura giornaliero (la candela 1d
delle borse chiude a mezzanotte UTC), i fondi che valutano a mezzanotte.

**Spiegazioni concorrenti.**
1. *Caso.* t vicino a 0.
2. *Costi.* Il movimento tipico di mezz'ora è l'1% e il costo un giro 0,14%: con stop a 1,5 ATR il costo è 0,09 R per trade. Prevede R lordo positivo e netto negativo. Smentita: netto positivo con margine.
3. *Trend di fondo.* Prevede che long e short seguano l'anno (la (b) lo misura).
4. *Solo il mercato.* L'ultima mezz'ora di ADA segue quella di BTC; il segnale è la prima mezz'ora di BTC. Non smentibile qui, ma la (b) entra alla stessa ora a caso solo se la regola lo prevede: qui la (b) entra in barre casuali, quindi un effetto dell'ora del giorno (non del segnale) farebbe battere la (b) senza battere la (a). La (a) entra a ogni barra libera: idem. Spiegazione importante: un effetto «ultima mezz'ora» indipendente dal segno della prima.
5. *Stagionalità dell'ora (non predittività).* Prevede long e short con risultati opposti e la stessa somma; il segno della prima mezz'ora non conta.
6. *Volatilità.* Prima e ultima mezz'ora più volatili: R in valore assoluto più grande, non media.
7. *Artefatto dei dati.* Prime mezz'ore mancanti (giorni senza barre) azzerate: nessun effetto.
8. *Funding a mezzanotte.* Il settlement delle 00:00 cade all'uscita: momento ambiguo, contato solo se costo. Prevede un piccolo costo per i long nel 2021.
9. *Pochi giorni estremi.* Prevede R concentrato in pochi giorni (marzo 2020 escluso dal filtro).
10. *Inversione (non momento).* La fonte trova anche inversione: prevede segno opposto (R negativo e sotto la (b)).

**Ipotesi completa.** ADAUSDT, momento infragiornaliero, 30m (le mezz'ore della fonte), posizione
di una barra.

**Varianti.**
* ADAUSDT-008: 30m, long. Alla chiusura della barra delle 23:00 (cioè alle 23:30), se il rendimento
  della barra 00:00-00:30 dello stesso giorno è > 0, ingresso alle 23:30; uscita all'apertura della
  barra successiva (00:00); stop 1,5 ATR(48 barre da 30 minuti). Motivo: regola della fonte; ATR su un
  giorno di barre.
* ADAUSDT-009: 30m, short se la prima mezz'ora è < 0.

---

## I-06 — BTC guida, ADA segue con ritardo

**Fonte.** Andrew W. Lo, A. Craig MacKinlay, «When Are Contrarian Profits Due to Stock Market
Overreaction?», Review of Financial Studies 3(2), 1990: i rendimenti dei titoli grandi anticipano
quelli dei piccoli (correlazione incrociata con ritardo), perché l'informazione arriva prima dove ci
sono più operatori. Per le crypto il legame BTC-altre monete è studiato in Azhar Mohamad, Imtiaz
Mohammad Sifat, Mohammad Syazwan Mohamed Shariff, «Lead-lag relationship between Bitcoin and
Ethereum: Evidence from hourly and daily data», Research in International Business and Finance 50,
2019 (che trova causalità in entrambe le direzioni e poco spazio per guadagni: una fonte che non
promette il risultato).

**Affermazione.** Su ADA, dopo un'ora in cui BTC sale più di 1,5 deviazioni standard (delle sue ore
dell'ultima settimana) e ADA sale meno di BTC, le 3 ore successive di ADA rendono più di 3 ore prese
a caso; simmetrico al ribasso.

**Sotto-domande.** Vale nei movimenti grandi di BTC (notizie macro)? Chi opera: arbitraggisti e
algoritmi che riallineano le altre monete a BTC; operatori al dettaglio più lenti. Quanto dura: minuti
o ore; se dura minuti, a 1 ora è già sparito.

**Spiegazioni concorrenti.**
1. *Caso.* t vicino a 0.
2. *Riallineamento troppo rapido.* L'effetto dura minuti: a chiusura dell'ora è finito. Prevede R come la (b).
3. *Inversione di BTC.* Dopo un'ora estrema BTC ritraccia, e ADA con lui: prevede R negativo.
4. *Trend di fondo.* Prevede long buoni nel 2021.
5. *Volatilità.* Le ore estreme cadono in fasi volatili: stop a 2 ATR scatta spesso.
6. *Costi.* 0,047 R a giro con stop a 2 ATR: rilevanti se il vantaggio è di pochi centesimi di R.
7. *ADA ha una sua notizia.* Se ADA sale meno di BTC perché ha una sua notizia negativa, il ritardo non si chiude: prevede fallimenti concentrati nei giorni di notizie di ADA (non misurabile qui).
8. *Pochi episodi.* Le ore oltre 1,5 deviazioni sono forse il 7% delle ore; con la condizione su ADA molte di meno, ma centinaia in 2,7 anni.
9. *Artefatto dei dati.* BTC e ADA sulla stessa barra: allineati per ts; nessun prezzo futuro.
10. *È solo il mercato.* Qui il mercato È il segnale: la spiegazione da escludere è che entrare dopo un'ora forte di BTC renda allo stesso modo anche senza la condizione su ADA (la (a) lo misura in parte).

**Ipotesi completa.** ADAUSDT, ritardo nella diffusione dell'informazione da BTC, 1h (il dato più fine
della fonte crypto è orario), posizione di 3 ore.

**Varianti.**
* ADAUSDT-010: 1h, long. Ingresso se il rendimento orario di BTC > 1,5 deviazioni standard dei
  rendimenti orari di BTC delle ultime 168 ore e il rendimento orario di ADA < quello di BTC; uscita
  dopo 3 barre; stop 2 ATR(14).
* ADAUSDT-011: 1h, short simmetrico (BTC < −1,5 deviazioni, ADA sopra BTC).

---

## I-07 — Funding affollato: chi paga troppo per stare long

**Fonte.** Songrun He, Asaf Manela, Omri Ross, Victor von Wachter, «Fundamentals of Perpetual
Futures», arXiv 2212.06888, dicembre 2022. Il funding è il prezzo che i long pagano agli short per
tenere il perpetuo vicino allo spot; quando i long sono troppi il perpetuo sta sopra lo spot e il
funding lo spinge giù. Le deviazioni sono grandi nelle crypto e si richiudono.

**Affermazione.** Su ADA, quando l'ultimo funding è alto (sopra lo 0,03% e al 90° percentile degli
ultimi 90 settlement, cioè 30 giorni), le 24 ore successive rendono meno di 24 ore a caso: lo short
guadagna più della (b). Simmetrico: funding negativo al 10° percentile, long.

**Sotto-domande.** Vale di più quando il funding è estremo dopo un rialzo forte? Chi opera: long con
leva che pagano e prima o poi chiudono; arbitraggisti che vendono il perpetuo e comprano lo spot.
Quanto dura: ore-giorni.

**Spiegazioni concorrenti.**
1. *Caso.* t vicino a 0.
2. *Il funding segue il prezzo.* Funding alto = rialzo appena avvenuto: il segnale è un momento, e lo short perde. Prevede R negativo per lo short.
3. *Trend di fondo.* Funding alto nel 2021 (rialzo): short contro il trend. Prevede short peggiore della media del 2021 ma forse migliore della (b) short.
4. *L'incasso del funding.* Lo short incassa il funding: parte dell'R viene da lì, non dal prezzo. Prevede un vantaggio piccolo e uguale al funding incassato. Si misura col funding nel risultato (il motore lo conta).
5. *Solo il mercato.* Il funding alto è di tutte le monete insieme (euforia): prevede che conti la fase, non ADA.
6. *Volatilità.* Funding estremi in fasi volatili: stop a 2,5 ATR scatta spesso.
7. *Costi.* 0,013 R a giro: piccoli.
8. *Pochi episodi raggruppati.* I funding alti vengono a grappoli di giorni: tanti trade dipendenti, il blocco li raccoglie.
9. *Artefatto: settlement in buchi.* Pochi.
10. *Liquidazioni a catena.* Il meccanismo concreto: prevede guadagni concentrati in pochi crolli (R senza i 3 migliori molto più basso).

**Ipotesi completa.** ADAUSDT, eccesso di posizioni long (o short) pagato col funding, 8h (il ritmo
dei settlement), posizione di 24 ore.

**Varianti.**
* ADAUSDT-012: 8h, short. Ingresso se l'ultimo funding regolato entro la chiusura della barra è
  > 0,0003 e ≥ il 90° percentile dei 90 settlement precedenti; uscita dopo 3 barre; stop 2,5 ATR(14).
* ADAUSDT-013: 8h, long. Ingresso se l'ultimo funding è < 0 e ≤ il 10° percentile dei 90 precedenti;
  stessa uscita e stop.

---

## I-08 — Compressione della volatilità e poi espansione (Bollinger)

**Fonte.** John Bollinger, «Bollinger on Bollinger Bands», McGraw-Hill, 2001 (il «Squeeze»: quando
l'ampiezza delle bande tocca il minimo di un lungo periodo, segue un'espansione; la direzione la dà
la rottura della banda). Meccanismo: la volatilità torna alla media; dopo una fase calma gli ordini
in attesa vengono attivati insieme.

**Affermazione.** Su ADA a 4 ore, se nelle ultime 5 barre l'ampiezza delle bande (4 deviazioni
standard su media 20) ha toccato il minimo delle 120 barre precedenti e la chiusura esce sopra la
banda alta, il movimento che segue (fino al ritorno sotto la media) rende più del caso; simmetrico.

**Sotto-domande.** Vale di più dopo compressioni lunghe? Chi opera: ordini di stop e di rottura in
attesa; venditori di volatilità che coprono. Quanto: giorni.

**Spiegazioni concorrenti.**
1. *Caso.*
2. *La volatilità torna, ma senza direzione.* Prevede espansione (|R| grande) ma R medio come la (b).
3. *Trend di fondo.*
4. *Solo il mercato.* Le compressioni di ADA coincidono con quelle di BTC.
5. *Falsa rottura.* Prevede ritorno immediato dentro le bande e uscita alla media con piccola perdita.
6. *Uscita che fa tutto.* La (a) ha la stessa uscita sotto la media.
7. *Costi.* 0,023 R.
8. *Pochi episodi.* Le compressioni al minimo di 20 giorni sono rare: forse 50-100 rotture: conta il numero.
9. *Volatilità dello stop.* Lo stop a 2 ATR in fase calma è stretto: prevede molti stop.
10. *Artefatto dei dati.* Nessuno noto.

**Ipotesi completa.** ADAUSDT, ritorno della volatilità con direzione data dalla rottura, 4h (la fonte
è giornaliera con 6 mesi di storia; a 4 ore 120 barre sono 20 giorni: più episodi, stesso meccanismo).

**Varianti.**
* ADAUSDT-014: 4h, long. Condizione: compressione (ampiezza ≤ minimo delle 120 barre precedenti)
  in una delle ultime 6 barre (5 precedenti e la corrente) e chiusura sopra la banda alta (media 20 +
  2 deviazioni); uscita alla chiusura sotto la media 20; stop 2 ATR(14).
* ADAUSDT-015: 4h, short simmetrico (chiusura sotto la banda bassa, uscita sopra la media).

---

## I-09 — Ritracciamento breve dentro una tendenza (RSI a 2 periodi)

**Fonte.** Larry Connors, Cesar Alvarez, «Short Term Trading Strategies That Work», TradingMarkets,
2009: comprare quando la chiusura è sopra la media a 200 periodi e l'RSI a 2 periodi è sotto 5,
uscire alla chiusura sopra la media a 5. Meccanismo: chi fornisce liquidità ai venditori impazienti
viene pagato quando il ritracciamento rientra; il filtro di tendenza evita di comprare i crolli veri.

**Affermazione.** Su ADA, in tendenza al rialzo (chiusura sopra la media 200), dopo un RSI(2) sotto
5 il prezzo torna sopra la media a 5 con un R medio più alto di un ingresso a caso con la stessa
uscita.

**Sotto-domande.** Vale nelle tendenze forti? Chi vende: liquidazioni, prese di profitto; chi compra:
chi aspetta i ritracciamenti. Quanto: 1-5 barre.

**Spiegazioni concorrenti.**
1. *Caso.*
2. *Trend di fondo.* Sopra la media 200 nel 2021: i long vincono per il trend; la (b) long entra nelle stesse barre valide.
3. *Solo il mercato.*
4. *Coltello che cade.* Nelle inversioni di tendenza il ritracciamento continua: grandi perdite rare (R asimmetrico).
5. *Uscita alla media 5.* Esce presto: molti piccoli guadagni; il pavimento dell'errore copre l'asimmetria.
6. *Costi.* 1d: 0,006 R; 4h: 0,015 R.
7. *Volatilità.* RSI(2) estremo nei giorni volatili.
8. *Pochi trade su 1d.* Riscaldamento di 200 giorni: la costruzione utile scende a ~2,2 anni; forse 15-30 trade: scarto probabile.
9. *Funding.* Long nel 2021 pagano.
10. *Artefatto.* Nessuno.

**Ipotesi completa.** ADAUSDT, fornitura di liquidità nei ritracciamenti, long, 1d (la fonte) e 4h
(lo stesso meccanismo su barre più corte; serve se a 1d i trade non bastano).

**Varianti.**
* ADAUSDT-016: 1d, long. Chiusura > media semplice 200 e RSI(2) < 5; uscita alla chiusura sopra la
  media semplice 5; stop 3 ATR(14) (la fonte non ha stop: questo è uno stop di sicurezza largo).
* ADAUSDT-017: 4h, long, stesse regole sulle barre da 4 ore.

---

## I-10 — Premio dei volumi alti (visibilità)

**Fonte.** Simon Gervais, Ron Kaniel, Dan H. Mingelgrin, «The High-Volume Return Premium», Journal of
Finance 56(3), giugno 2001: i titoli con volume insolitamente alto in un periodo, a parità di
rendimento, salgono nei periodi successivi, perché il volume li rende visibili a nuovi compratori.

**Affermazione.** Su ADA, dopo una barra con volume in USDT sopra il 90° percentile delle barre
precedenti (50 giorni) e rendimento piccolo (in valore assoluto sotto una deviazione standard), i
5 giorni successivi rendono più di 5 giorni presi a caso (long).

**Sotto-domande.** Vale se il volume alto non viene da un crollo? Chi compra dopo: nuovi investitori
che notano la moneta. Quanto: giorni-settimane.

**Spiegazioni concorrenti.**
1. *Caso.*
2. *Trend di fondo.*
3. *Solo il mercato.* Il volume di ADA è alto quando tutto il mercato si muove.
4. *Il volume anticipa la volatilità, non la direzione.* Prevede |R| grande, R medio come la (b).
5. *Distribuzione.* Volume alto senza movimento = grandi venditori assorbiti: prevede ribasso dopo (R negativo).
6. *Costi.* Trascurabili a 1d e 4h.
7. *Funding.* Long pagano nel 2021.
8. *Pochi episodi* a 1d.
9. *Artefatto del volume.* Il volume in USDT cresce col prezzo: in rialzo ogni giorno ha volume «alto» rispetto al passato. Prevede segnali concentrati nei rialzi del 2021. La (b) entra a caso nelle stesse barre valide: misura il trend, non questo legame.
10. *Notizie specifiche.* Gli aggiornamenti della rete di ADA portano volume: non misurabile qui.

**Ipotesi completa.** ADAUSDT, attenzione dopo un volume insolito, long, 1d (la fonte usa giorni e
settimane) e 4h (stesso meccanismo con finestra di 50 giorni e tenuta di 5 giorni espresse in barre).

**Varianti.**
* ADAUSDT-018: 1d, long. Volume in USDT della barra > 90° percentile dei 50 giorni precedenti e
  |chiusura/apertura − 1| < 1 deviazione standard dei rendimenti dei 30 giorni precedenti; uscita
  dopo 5 barre; stop 3 ATR(14).
* ADAUSDT-019: 4h, long, stesse regole con 300 barre (50 giorni) per il volume, 180 (30 giorni) per
  la deviazione, uscita dopo 30 barre (5 giorni).

---

## I-11 — Numeri tondi: gli ordini di stop oltre le soglie tonde

**Fonte.** Carol L. Osler, «Currency Orders and Exchange Rate Dynamics: An Explanation for the
Predictive Success of Technical Analysis», Journal of Finance 58(5), ottobre 2003. Gli ordini di
presa di profitto si ammassano sui numeri tondi (inversioni lì), gli ordini di stop appena oltre (dopo
l'attraversamento il movimento accelera).

**Affermazione.** Su ADA, quando la chiusura oraria attraversa al rialzo un livello tondo (multipli
di 0,005 sotto 0,10 USDT, di 0,05 fra 0,10 e 1, di 0,5 fra 1 e 10), le 12 ore successive rendono più
del caso; simmetrico al ribasso.

**Sotto-domande.** Vale più per i livelli molto tondi (0,1, 1, 2)? Chi opera: ordini di stop di chi è
short sopra il livello. Quanto: ore.

**Spiegazioni concorrenti.**
1. *Caso.*
2. *Il numero tondo come resistenza (presa di profitto).* L'altra metà di Osler: dopo l'attraversamento il prezzo torna sotto. Prevede R negativo.
3. *Il livello non conta: è un momento orario.* Attraversare un livello vuol dire essere saliti: prevede R uguale a quello dopo una qualsiasi ora in salita (la (a) entra a ogni barra, non lo misura del tutto).
4. *Trend di fondo.*
5. *Solo il mercato.*
6. *Costi.* 0,062 R a giro con stop a 1,5 ATR: importanti.
7. *Ordini nei libri di Binance diversi dal cambio.* Le crypto quotate in USDT con 4 decimali: i tondi contano meno. Prevede nessun effetto.
8. *Attraversamenti ripetuti.* Il prezzo oscilla attorno al livello: tanti segnali vicini, trade dipendenti.
9. *Volatilità.*
10. *Artefatto dei dati.* Nessuno.

**Ipotesi completa.** ADAUSDT, ordini di stop oltre i numeri tondi, 1h (attraversamenti visibili
senza il rumore di 15 minuti), posizione di 12 ore.

**Varianti.**
* ADAUSDT-020: 1h, long. Passo = 0,5 × 10^floor(log10(chiusura precedente)); ingresso se
  floor(chiusura/passo) > floor(chiusura precedente/passo); uscita dopo 12 barre; stop 1,5 ATR(14).
* ADAUSDT-021: 1h, short simmetrico (attraversamento al ribasso).

---

## I-12 — Ritorno del residuo rispetto a BTC

**Fonte.** Marco Avellaneda, Jeong-Hyun Lee, «Statistical arbitrage in the U.S. equities market»,
Quantitative Finance 10(7), 2010: la parte del rendimento di un titolo non spiegata dal fattore
comune (il residuo) torna verso la media; si entra quando il residuo cumulato supera 2 deviazioni
(«s-score») e si esce quando rientra sotto 0,5.

**Affermazione.** Su ADA, quando il residuo cumulato delle ultime 24 ore rispetto a BTC (beta stimato
sulle ultime 720 ore) è sotto −2 deviazioni, ADA recupera rispetto al caso nelle ore dopo (long);
simmetrico sopra +2 (short). Qui senza copertura con BTC: la posizione è solo su ADA.

**Sotto-domande.** Vale se il residuo nasce da una notizia di ADA? Chi opera: arbitraggisti fra monete,
pressione di vendita temporanea. Quanto: ore-1 giorno.

**Spiegazioni concorrenti.**
1. *Caso.*
2. *Senza copertura il residuo è rumore rispetto al movimento di BTC.* Il rendimento di ADA è dominato dal fattore comune: prevede R come la (b) anche se il residuo rientra.
3. *Il residuo ha una ragione (notizia): non rientra.* Prevede R negativo per il long.
4. *Trend di fondo.*
5. *Volatilità.*
6. *Costi.* 0,047 R.
7. *Beta instabile.* Il beta cambia nel tempo: residui finti. Prevede segnali in fasi di cambiamento.
8. *Pochi episodi indipendenti.* Le soglie a 2 deviazioni scattano in grappoli.
9. *Artefatto.* Ore mancanti di BTC o ADA: residuo azzerato (pochi casi).
10. *Momento relativo.* L'opposto: ADA che resta indietro continua a restare indietro (momento fra monete): prevede R negativo per il long.

**Ipotesi completa.** ADAUSDT, ritorno del residuo, 1h (la fonte usa dati giornalieri; a 1 ora i
residui di 24 ore sono più numerosi), posizione fino a 24 ore.

**Varianti.**
* ADAUSDT-022: 1h, long. s = somma dei residui orari delle ultime 24 ore divisa per (deviazione dei
  residui delle 720 ore × radice di 24); ingresso se s < −2; uscita se s > −0,5 o dopo 24 barre; stop 2
  ATR(14).
* ADAUSDT-023: 1h, short se s > 2; uscita se s < 0,5 o dopo 24 barre.

---

## I-13 — Rottura dell'intervallo d'apertura della giornata

**Fonte.** Toby Crabel, «Day Trading with Short Term Price Patterns and Opening Range Breakout»,
Traders Press, 1990: la rottura del massimo o del minimo dei primi minuti della sessione tende a
proseguire nella giornata. Meccanismo: la prima ora fissa il campo di battaglia; la rottura mostra chi
ha più fretta.

**Affermazione.** Su ADA, la prima chiusura a 15 minuti sopra il massimo della prima ora UTC
(00:00-01:00), prima delle 20:00, seguita fino alla fine della giornata con stop al minimo della prima
ora, rende più di un ingresso a caso con lo stesso stop e la stessa uscita; simmetrico.

**Sotto-domande.** Vale in un mercato 24 ore, dove la «sessione» UTC è una convenzione? Vale più nei
giorni con prima ora stretta? Chi opera: chi apre a inizio giornata UTC (Asia mattina).

**Spiegazioni concorrenti.**
1. *Caso.*
2. *La sessione UTC non esiste per le crypto.* Prevede nessun effetto.
3. *Costi.* Stop a distanza dell'ampiezza della prima ora (spesso 1-2%): 0,07-0,14 R a giro.
4. *Trend di fondo.*
5. *Solo il mercato.*
6. *Falsa rottura.*
7. *Volatilità.*
8. *Uscita a fine giornata.* L'(a) ha la stessa uscita: la condizione deve aggiungere.
9. *Più rotture al giorno.* Rientri e nuove rotture danno trade dipendenti.
10. *Artefatto.* Giorni senza la prima ora completa esclusi.

**Ipotesi completa.** ADAUSDT, rottura dell'intervallo d'apertura, 15m, fino alla fine della giornata.

**Varianti.**
* ADAUSDT-024: 15m, long. Intervallo = massimo e minimo delle 4 barre 00:00-01:00 (complete); ingresso
  alla chiusura che passa sopra il massimo (la precedente era sotto o uguale), solo per barre che
  aprono prima delle 20:00; stop al minimo dell'intervallo; uscita alla chiusura della barra delle
  23:45 (cioè all'apertura delle 00:00).
* ADAUSDT-025: 15m, short simmetrico.

---

---

# Seconda serie (scritta il 2026-10-09 alle 15:41 UTC)

Scritta dopo i conteggi della prima serie (8 scarti per trade minimi: 005, 006, 007, 014, 015, 016,
017, 018) e mentre le 17 varianti registrate erano in test, PRIMA di leggere qualunque loro
risultato. Due idee nuove (I-14, I-15) e due allentamenti di idee rimaste senza alcuna variante
testabile (I-04, I-08): la regola 6 dice che allentare le soglie di uno scarto per raggiungere i
trade minimi, senza aver visto risultati, è ancora una variante dell'idea nuova. Per I-04 e I-08 le
varianti testate restano due per fonte (le prime due sono scarti, non testate).

## I-14 — Squilibrio degli ordini aggressivi

**Fonte.** Tarun Chordia, Avanidhar Subrahmanyam, «Order imbalance and individual stock returns:
Theory and evidence», Journal of Financial Economics 72(3), 2004: i grandi operatori spezzano gli
ordini nel tempo, quindi lo squilibrio fra acquisti e vendite aggressive è persistente, e lo squilibrio
passato predice positivamente i rendimenti successivi.

**Affermazione.** Su ADA, quando lo squilibrio degli ultimi 24 ore (acquisti meno vendite aggressive,
cioè dei «taker», sul volume) è sopra il 90° percentile delle ultime 720 ore, le 24 ore successive
rendono più del caso (long); simmetrico sotto il 10° percentile (short).

**Sotto-domande.** Lo squilibrio dei taker su Binance misura davvero ordini informati o il rumore degli
operatori al dettaglio con leva? Vale con volume alto? Quanto dura: ore-giorni (gli ordini spezzati).

**Spiegazioni concorrenti.**
1. *Caso.*
2. *Lo squilibrio è il prezzo già mosso.* Acquisti aggressivi = prezzo salito nelle 24 ore: il segnale è un momento a 24 ore. Prevede lo stesso R di un ingresso dopo 24 ore in salita (non misurato dalla (a)).
3. *Inversione per pressione temporanea.* La fonte stessa: controllando lo squilibrio corrente il segno si inverte. Prevede R negativo dopo squilibri estremi.
4. *Trend di fondo.*
5. *Solo il mercato.* Lo squilibrio di ADA segue quello di tutte le monete.
6. *Liquidazioni.* Gli acquisti aggressivi estremi sono chiusure forzate di short: finite quelle, il prezzo torna. Prevede R negativo per il long.
7. *Costi.* 0,047 R a giro.
8. *Volatilità.*
9. *Artefatto del dato taker.* La colonna taker_buy_volume misura il lato aggressivo secondo Binance; barre senza dato → squilibrio 0 (pochi casi).
10. *Grappoli.* Squilibri estremi consecutivi: trade dipendenti.

**Ipotesi completa.** ADAUSDT, ordini spezzati e persistenti, 1h, posizione di 24 ore.

**Varianti.**
* ADAUSDT-026: 1h, long. Squilibrio = somma su 24 barre di (2 × quota taker − 1) × volume, divisa per il
  volume delle 24 barre; ingresso se sopra il 90° percentile dei valori delle 720 barre precedenti;
  uscita dopo 24 barre; stop 2 ATR(14).
* ADAUSDT-027: 1h, short se sotto il 10° percentile.

## I-15 — Inversione di breve periodo come compenso per chi fornisce liquidità

**Fonte.** Stefan Nagel, «Evaporating Liquidity», Review of Financial Studies 25(7), 2012 (NBER WP
17653, 2011): i rendimenti delle strategie di inversione a breve sono il compenso di chi fornisce
liquidità, e crescono quando il mercato è sotto stress. Anche Bruce N. Lehmann, «Fads, Martingales,
and Market Efficiency», Quarterly Journal of Economics 105(1), 1990.

**Affermazione.** Su ADA, dopo un calo di 24 ore (6 barre da 4 ore) oltre 2 deviazioni standard dei
rendimenti a 24 ore dei 60 giorni precedenti, le 24 ore successive rendono più del caso (long);
simmetrico dopo un rialzo eccessivo (short).

**Sotto-domande.** Vale di più in fasi di stress (volatilità alta)? Chi vende: chi deve ridurre
(liquidazioni, margini); chi compra: chi fornisce liquidità e vuole un premio. Quanto: 1-5 giorni.

**Spiegazioni concorrenti.**
1. *Caso.*
2. *Momento (l'opposto).* Prevede R negativo: i cali continuano (cfr. I-04, inerzia).
3. *Trend di fondo.* Long dopo i cali nel 2022 = contro il trend.
4. *Solo il mercato.*
5. *Volatilità.* Dopo i cali la volatilità è alta: stop a 3 ATR largo, R con varianza alta.
6. *Coltello che cade.* Crolli veri (maggio 2021, giugno e novembre 2022): poche perdite enormi.
7. *Costi.* 0,015 R: piccoli.
8. *Funding.* Dopo i cali il funding scende: i long pagano poco.
9. *Grappoli.* Le soglie scattano per più barre consecutive dello stesso evento: trade dipendenti, blocco lungo.
10. *Pochi trade.* Eventi a 2 deviazioni: forse 5% delle barre per lato, ma a grappoli: conta il numero.

**Ipotesi completa.** ADAUSDT, premio per la liquidità dopo movimenti eccessivi, 4h (rendimento a 24
ore aggiornato ogni 4 ore), posizione di 24 ore.

**Varianti.**
* ADAUSDT-028: 4h, long. Ingresso se il rendimento delle ultime 6 barre < −2 deviazioni standard dei
  rendimenti a 6 barre delle 360 barre precedenti; uscita dopo 6 barre; stop 3 ATR(14).
* ADAUSDT-029: 4h, short se il rendimento > +2 deviazioni.

## I-04, varianti allentate (le prime due erano scarti: 62 e 52 trade)

* ADAUSDT-030: come 006 (1d long dopo reazione eccessiva al rialzo) con k = 0,5 invece di 1. Motivo:
  raggiungere i trade minimi; la fonte usa più valori di k e l'affermazione (inerzia dopo un movimento
  insolitamente grande) resta la stessa con una soglia più bassa.
* ADAUSDT-031: come 007 (1d short dopo reazione eccessiva al ribasso) con k = 0,5.

## I-08, varianti allentate (le prime due erano scarti: 15 e 21 trade)

* ADAUSDT-032: come 014 (4h long, compressione e rottura della banda alta) con la compressione
  misurata sul minimo delle 60 barre precedenti (10 giorni) invece di 120. Motivo: trade minimi; il
  meccanismo (volatilità al minimo recente, poi espansione) è lo stesso con una memoria più corta.
* ADAUSDT-033: come 015 (short) con 60 barre.

## Idee considerate e non scritte come varianti

* **Effetti di calendario (ora del giorno, giorno della settimana)**: Dirk G. Baur, Daniel Cahill,
  Keith Godfrey, Zhangxin (Frank) Liu, «Bitcoin time-of-day, day-of-week and month-of-year effects in
  returns and trading volume», Finance Research Letters 31, 2019: trovano effetti che cambiano nel
  tempo, senza una direzione stabile. Senza un'affermazione con un segno non si scrive una regola
  falsificabile: non usata.
* **Effetto del cambio di mese** (Ariel, 1987): un ingresso al mese dà circa 33 trade in costruzione,
  sotto il minimo: non scritta.
