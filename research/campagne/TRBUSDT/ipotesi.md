# Ipotesi della campagna TRBUSDT (Fase 1)

Scritte tutte prima del primo test di ciascuna idea (regola 6). Ogni idea ha: fonte pubblicata prima
del 2024-01-01, affermazione falsificabile, sotto-domande, almeno 10 spiegazioni concorrenti con la
previsione che farebbero e cosa le smentirebbe, l'ipotesi completa e TUTTE le sue varianti col
motivo. Nessuna idea viene dai risultati del gate, del registro, del paper o di altre monete.

Regole comuni a tutte le varianti (fissate prima del primo test, regola 9):

* segnali alla chiusura della barra, ingresso all'apertura della barra dopo (motore, sezione 7);
* stop calcolato alla chiusura della barra del segnale; dimensione dal rischio dell'1% (regole del
  bot, `config/regole_dimensione.md`); leva massima 2, margine isolato, costi della scheda (taker
  0,05% e slippage 0,02% per lato: 0,14% del nozionale per giro);
* «tenere H barre» vuol dire: alla chiusura della H-esima barra dalla barra d'ingresso compresa
  la variante dice «chiudi» e l'uscita avviene all'apertura della barra dopo;
* nessuna barra di segnale nei mesi sotto la liquidità minima (`fase0_dati.md`);
* ATR = ATR di Wilder a 14 barre del timeframe della variante;
* il bot non accetta stop oltre il 6% del prezzo (`parametri.yaml`, `stop_massimo_bot`): per ogni
  variante si dice se lo stop tipico lo supera (in quel caso il bot non può eseguirla così com'è).

Le spiegazioni concorrenti «noiose» compaiono in ogni idea: caso, volatilità, trend di fondo,
artefatto dei dati, costi, «è solo il mercato» (BTC). Il controllo di «è solo il mercato» usa le
candele last di BTCUSDT dello stesso timeframe (solo come riferimento, mai come segnale).

---

## I-01 — Momentum della serie (time-series momentum)

1. **Fonte.** T. J. Moskowitz, Y. H. Ooi, L. H. Pedersen, «Time series momentum», Journal of
   Financial Economics 104(2), maggio 2012. Per le crypto: Y. Liu, A. Tsyvinski, «Risks and
   Returns of Cryptocurrency», NBER Working Paper 24877, agosto 2018 (momentum della serie a
   orizzonti da una a quattro settimane).
2. **Affermazione.** Su TRBUSDT il rendimento delle ultime 4 settimane predice con lo stesso segno
   il rendimento dei 5 giorni seguenti: dopo un rendimento a 20 giorni positivo un long tenuto 5
   giorni ha R medio dopo i costi positivo e superiore a quello di un long entrato a caso con la
   stessa uscita (e simmetricamente per lo short). Si smentisce se il `t` contro la (b) non supera
   la soglia.
3. **Sotto-domande.** Vale di più con volatilità alta o bassa? Dopo movimenti grandi o piccoli? Chi
   compra dopo un rialzo: investitori che reagiscono in ritardo (sotto-reazione alle notizie),
   chi segue il trend, chi copre posizioni short. Quanto dura: la fonte crypto dice da 1 a 4
   settimane, poi l'effetto svanisce.
4. **Spiegazioni concorrenti** (previsione → cosa la smentisce):
   1. *Caso*: R medio vicino alla (b) → `t` contro la (b) oltre la soglia.
   2. *Trend di fondo*: in costruzione la moneta sale o scende per anni e ogni long (short) guadagna
      → la (b) avrebbe lo stesso R medio; la smentisce un R medio sopra la (b).
   3. *Volatilità*: le perdite sono stop in periodi agitati, i guadagni grandi movimenti →
      il vantaggio sparirebbe togliendo i 3 trade migliori; lo smentisce un R senza i migliori
      ancora sopra la (b).
   4. *È solo il mercato (BTC)*: TRB segue il trend di BTC → i trade vincenti coincidono con
      periodi di BTC in trend; si smentisce se il vantaggio resta negli anni in cui BTC va contro.
   5. *Pochi episodi*: tutto viene da uno o due trend lunghi → R per anno positivo in un solo
      anno; smentito da più anni sopra la (b).
   6. *Artefatto dei dati*: buchi o barre tolte creano salti → poche barre tolte (Fase 0).
   7. *Costi*: il vantaggio lordo esiste ma i costi lo mangiano → R lordo positivo e netto no;
      con 5 giorni e stop larghi i costi pesano poco, smentita se il netto resta positivo.
   8. *Inversione*: a questo orizzonte prevale il ritorno verso la media (altcoin poco liquide) →
      R medio sotto la (b); è la previsione opposta, smentita da R sopra la (b).
   9. *Effetto funding*: in trend rialzista il funding è alto e i long pagano → il long peggiora e lo
      short migliora per il funding, non per il prezzo; si guarda il funding pagato.
   10. *Effetto delle uscite*: con uscita a tempo e stop larghi l'R dipende dalla forma dei
       ritorni, non dal segnale → la (a) (sempre in posizione) avrebbe lo stesso R; smentita se
       batte la (a).
5. (previsioni e smentite sono scritte accanto a ogni spiegazione qui sopra)
6. **Ipotesi completa.** TRBUSDT, momentum della serie, timeframe 4h (il segnale è un rendimento a
   20 giorni = 120 barre; il 4h dà uno stop in ATR sotto il 6% del bot, che a 1d sarebbe circa il
   doppio), una direzione per variante.
   * **I-01-L** long: alla chiusura della barra i, se c[i]/c[i-120] − 1 > 0 e nessuna posizione →
     long; stop c[i] − 2 ATR; nessun target; tenere 30 barre (5 giorni).
   * **I-01-S** short: specchio, rendimento a 120 barre < 0; stop c[i] + 2 ATR; tenere 30 barre.
   Motivo delle due varianti: la fonte afferma l'effetto in entrambe le direzioni; restano separate.

---

## I-02 — Rottura del canale di prezzo (trading range break)

1. **Fonte.** W. Brock, J. Lakonishok, B. LeBaron, «Simple Technical Trading Rules and the
   Stochastic Properties of Stock Returns», Journal of Finance 47(5), dicembre 1992 (regola
   «trading range break»: compra quando il prezzo supera il massimo locale, tienilo 10 giorni).
2. **Affermazione.** Su TRBUSDT una chiusura sopra il massimo delle 50 barre precedenti (4h, circa
   8 giorni) è seguita da 10 giorni con R medio dopo i costi positivo e sopra la (b); specchio per
   la rottura del minimo.
3. **Sotto-domande.** Vale di più se la rottura avviene con volume alto? Dopo una fase di prezzi
   fermi? Chi opera: ordini stop sopra i massimi (chi era short ricopre), chi segue il trend entra
   alla rottura. Effetto atteso nei giorni seguenti, non nelle ore.
4. **Spiegazioni concorrenti**:
   1. *Caso*: R ≈ (b) → smentita da `t` oltre la soglia.
   2. *Trend di fondo*: in un anno di rialzo le rotture al rialzo sono tante e vincenti come
      qualunque long → la (b) lo cattura; smentita da R sopra la (b).
   3. *Falsa rottura*: le rotture tornano indietro (caccia agli stop) → molti stop nei primi giorni,
      R sotto la (b); smentita se R supera la (b).
   4. *Volatilità*: le rotture avvengono in periodi agitati in cui stop e guadagni sono grandi →
      vantaggio concentrato nei 3 trade migliori; smentita da R senza i migliori sopra la (b).
   5. *È solo il mercato*: le rotture di TRB coincidono con quelle di BTC → il vantaggio dipende
      dagli anni di trend di BTC; smentita da vantaggio stabile per anno.
   6. *Pochi episodi*: un solo grande trend fa il risultato → un anno solo positivo.
   7. *Artefatto*: un buco nei dati crea un falso massimo → barre tolte poche, controllo dei salti.
   8. *Costi*: guadagno lordo mangiato dai costi → con 10 giorni il costo è una piccola frazione.
   9. *Funding*: dopo le rotture al rialzo il funding sale e il long paga → funding pagato alto.
   10. *Effetto uscita*: l'R viene dall'uscita a 10 giorni, non dall'ingresso → la (a) uguale;
       smentita se batte la (a).
6. **Ipotesi completa.** TRBUSDT, rottura del canale, 4h (a 1d le rotture dei 50 giorni in 2,3
   anni di costruzione sono troppo poche per 70 trade; il 4h tiene la stessa logica a scala più
   corta).
   * **I-02-L** long: c[i] > max(high[i-50..i-1]) → long; stop c[i] − 2 ATR; tenere 60 barre.
   * **I-02-S** short: c[i] < min(low[i-50..i-1]) → short; stop c[i] + 2 ATR; tenere 60 barre.

---

## I-03 — Reazione eccessiva di breve periodo e ritorno

1. **Fonte.** W. F. M. De Bondt, R. Thaler, «Does the Stock Market Overreact?», Journal of Finance
   40(3), luglio 1985 (dopo movimenti estremi i prezzi tornano indietro). Per orizzonti brevi:
   B. N. Lehmann, «Fads, Martingales, and Market Efficiency», Quarterly Journal of Economics
   105(1), febbraio 1990.
2. **Affermazione.** Su TRBUSDT, dopo un movimento di 6 ore oltre 2,5 deviazioni standard (misurate
   sui 30 giorni precedenti), le 12 ore seguenti vanno in senso opposto: un long dopo un crollo
   (short dopo un'impennata) ha R medio dopo i costi positivo e sopra la (b).
3. **Sotto-domande.** Vale di più se il movimento avviene di notte (UTC) o con poco volume? Chi
   opera: liquidazioni a cascata e stop che spingono il prezzo oltre il valore, poi i fornitori
   di liquidità che comprano lo sconto. In quanto tempo: ore.
4. **Spiegazioni concorrenti**:
   1. *Caso* → `t` oltre la soglia lo smentisce.
   2. *Momentum*: i movimenti estremi continuano (notizie vere) → R sotto la (b).
   3. *Volatilità*: dopo i movimenti estremi la volatilità resta alta e gli stop scattano → molti
      stop; R sotto la (b).
   4. *Trend di fondo*: in un anno di ribasso i crolli non tornano → long perdenti nel 2022.
   5. *È solo il mercato*: i crolli di TRB sono crolli di BTC che rimbalza → si guarda BTC
      nelle stesse ore; il vantaggio deve esserci anche quando BTC non si muove.
   6. *Artefatto*: picchi di una barra (dati errati) creano falsi segnali → controllo delle ombre
      anomale in Fase 0.
   7. *Costi*: il rimbalzo è più piccolo dei costi → R lordo positivo, netto no.
   8. *Pochi trade estremi*: un solo rimbalzo enorme fa il risultato → R senza i 3 migliori.
   9. *Liquidità*: i movimenti estremi avvengono nei mesi sottili, dove lo slippage vero è più
      alto del modellato → dichiarato con la prova a costi doppi.
   10. *Raggruppamento*: i segnali arrivano a grappoli nello stesso giorno, contano come uno →
       il blocco del bootstrap lo copre; previsione: blocco grande.
6. **Ipotesi completa.** TRBUSDT, ritorno dopo reazione eccessiva, 1h (il fenomeno è di ore).
   z = (c[i]/c[i-6] − 1) / deviazione standard dei rendimenti a 6 barre delle 720 barre precedenti
   la barra i (compresa).
   * **I-03-L** long se z < −2,5; stop c[i] − 2 ATR; tenere 12 barre.
   * **I-03-S** short se z > +2,5; stop c[i] + 2 ATR; tenere 12 barre.

---

## I-04 — Gonfiamenti coordinati del prezzo e successivo sgonfiamento (pump and dump)

1. **Fonte.** J. Kamps, B. Kleinberg, «To the moon: defining and detecting cryptocurrency
   pump-and-dumps», Crime Science 7, articolo 18, novembre 2018 (rilevazione con soglie su
   aumento orario di prezzo e volume rispetto a una finestra mobile; dopo il picco il prezzo
   ricade).
2. **Affermazione.** Su TRBUSDT un'ora con volume oltre 5 volte la mediana della settimana
   precedente e rialzo oltre il 3% è seguita da 24 ore di ribasso: uno short ha R medio dopo i
   costi positivo e sopra la (b).
3. **Sotto-domande.** Vale di più nei mesi con poco volume (moneta più facile da spingere)? Chi
   opera: gruppi che comprano insieme e vendono a chi arriva dopo; chi arriva tardi compra il
   massimo. Tempi: il crollo arriva in ore o giorni.
4. **Spiegazioni concorrenti**:
   1. *Caso* → `t` oltre la soglia.
   2. *Notizia vera*: il picco è informazione (quotazioni, partnership) e il prezzo resta su →
      short perdenti, R sotto la (b).
   3. *Squeeze degli short*: il picco nasce da short liquidati e continua → stop frequenti.
   4. *Volatilità*: dopo il picco tutto si muove molto → R dominato dagli stop.
   5. *Trend di fondo*: nel 2022 ogni short guadagna → la (b) short alta; smentita da R sopra la (b).
   6. *È solo il mercato*: picchi di TRB insieme a BTC → si guarda BTC.
   7. *Artefatto*: volume gonfiato in una barra per errore → controllo dei volumi anomali.
   8. *Costi e slippage*: subito dopo il picco lo spread è largo → costi doppi.
   9. *Pochi episodi*: due o tre crolli fanno tutto → R senza i 3 migliori.
   10. *Funding*: dopo un picco il funding sale e lo short incassa → parte del guadagno è funding.
6. **Ipotesi completa.** TRBUSDT, sgonfiamento dopo un gonfiamento, 1h (la fonte lavora su ore),
   short. Volume = volume della barra (in moneta), mediana sulle 168 barre precedenti (esclusa la i).
   * **I-04-A** short se volume[i] > 5 × mediana e c[i]/o[i] − 1 > 3%; stop high[i] + 1 ATR;
     tenere 24 barre.
   * **I-04-B** come A con soglie più basse, volume > 3 × mediana e rialzo > 2% (motivo, prima di
     ogni risultato: non si sa quanti eventi superino le soglie della fonte su una sola moneta).

---

## I-05 — Funding affollato (chi è affollato paga e viene liquidato)

1. **Fonte.** M. Schmeling, A. Schrimpf, K. Todorov, «Crypto carry», BIS Working Papers n. 1087,
   marzo 2023 (carry alto nei futures crypto = domanda di leva degli investitori; predice
   liquidazioni e crolli). Sul meccanismo del funding: S. He, A. Manela, O. Ross, V. von Wachter,
   «Fundamentals of Perpetual Futures», arXiv 2212.06888, dicembre 2022.
2. **Affermazione.** Su TRBUSDT, quando il funding medio delle ultime 3 liquidazioni è nel 10% più
   alto dei 90 giorni precedenti e sopra lo 0,01%, i 3 giorni seguenti vanno al ribasso (short con
   R medio dopo i costi positivo e sopra la (b)); quando è nel 10% più basso e negativo, al rialzo.
3. **Sotto-domande.** Vale di più se il prezzo è già salito molto? Chi opera: long a leva che pagano
   il funding e vengono liquidati a cascata; arbitraggisti che vendono il perpetuo. Tempi: giorni.
4. **Spiegazioni concorrenti**:
   1. *Caso*.
   2. *Il funding segue il prezzo*: è alto perché il prezzo sale e il trend continua → short perdenti.
   3. *Incasso del funding*: lo short guadagna solo il funding, non il prezzo → R viene dal funding.
   4. *Trend di fondo*: 2022 di ribasso → ogni short vince; la (b) lo cattura.
   5. *Volatilità*: funding estremo con volatilità estrema → stop frequenti.
   6. *È solo il mercato*: funding alto su tutte le monete insieme (euforia generale) → BTC scende
      negli stessi giorni.
   7. *Artefatto*: cambi di intervallo del funding (8h, 4h) spostano la scala → controllo
      dell'intervallo in Fase 0.
   8. *Pochi episodi*: pochi giorni di euforia → R senza i 3 migliori.
   9. *Costi*: con 3 giorni i costi pesano poco; smentita se lordo e netto coincidono.
   10. *Squeeze opposto* (per il long): funding negativo = short affollati che ricoprono → è la
       previsione della variante long; smentita da R sotto la (b).
6. **Ipotesi completa.** TRBUSDT, funding affollato, 8h (il funding si liquida ogni 8 ore). f_i =
   media dei 3 ultimi settlement con istante ≤ chiusura della barra i; soglie sui valori di f
   delle 270 barre precedenti (90 giorni).
   * **I-05-S** short se f_i ≥ 90° percentile e f_i > 0,0001; stop c[i] + 2 ATR; tenere 9 barre.
   * **I-05-L** long se f_i ≤ 10° percentile e f_i < 0; stop c[i] − 2 ATR; tenere 9 barre.

---

## I-06 — Effetto del lunedì

1. **Fonte.** G. M. Caporale, A. Plastun, «The day of the week effect in the cryptocurrency
   market», Finance Research Letters 31, dicembre 2019 (rendimenti anomali positivi il lunedì per
   Bitcoin).
2. **Affermazione.** Su TRBUSDT il rendimento del lunedì (00:00-24:00 UTC) è più alto di quello di un
   giorno qualunque: un long aperto all'apertura del lunedì e chiuso all'apertura del martedì ha R
   medio dopo i costi positivo e sopra la (b).
3. **Sotto-domande.** Vale nei mercati in rialzo e in ribasso? Chi opera: il ritorno dei
   professionisti e dei flussi istituzionali dopo il fine settimana, notizie accumulate. Tempi:
   un giorno.
4. **Spiegazioni concorrenti**:
   1. *Caso* (l'effetto della fonte è su Bitcoin, non su TRB).
   2. *Data mining della fonte*: fra 7 giorni uno esce per caso → nessun effetto qui.
   3. *Trend di fondo*: ogni long di un giorno ha l'R del trend → la (b).
   4. *È solo il mercato*: TRB segue il lunedì di BTC → BTC il lunedì.
   5. *Volatilità*: il lunedì è più volatile → R più disperso, non più alto.
   6. *Costi*: un giorno con stop largo costa poco in R; un vantaggio piccolo resta piccolo.
   7. *Pochi trade estremi*: due lunedì enormi → R senza i 3 migliori.
   8. *Fine settimana*: il movimento avviene la domenica e il lunedì torna indietro → R negativo.
   9. *Artefatto*: buchi nei fine settimana → barre tolte in Fase 0.
   10. *Effetto anno*: vale solo in un anno → R per anno.
6. **Ipotesi completa.** TRBUSDT, lunedì, 1d, long. Alla chiusura della domenica (barra 1d il cui
   giorno è domenica) → long; stop 6% sotto la chiusura (il limite del bot: a 1d l'ATR supera il
   6%; con un giorno di durata lo stop è una protezione, non l'uscita); tenere 1 barra.
   * **I-06-L** come sopra. Una sola variante (la fonte afferma solo il lunedì positivo).

---

## I-07 — Compressione della volatilità e rottura (squeeze)

1. **Fonte.** J. Bollinger, «Bollinger on Bollinger Bands», McGraw-Hill, 2001 (la «Squeeze»:
   un'ampiezza delle bande ai minimi precede un'espansione; si entra nella direzione della
   rottura della banda).
2. **Affermazione.** Su TRBUSDT, una chiusura fuori dalla banda dopo una compressione (ampiezza nel
   20% più basso delle 120 barre precedenti) è seguita da un movimento nella stessa direzione nei 5
   giorni dopo: R medio dopo i costi positivo e sopra la (b).
3. **Sotto-domande.** La compressione deve durare? Conta il volume alla rottura? Chi opera: ordini
   accumulati durante la quiete, stop raggruppati vicino ai bordi del range. Tempi: giorni.
4. **Spiegazioni concorrenti**:
   1. *Caso*. 2. *Falsa rottura*: dopo la compressione la rottura torna dentro → stop.
   3. *Trend di fondo* → la (b). 4. *È solo il mercato*: compressioni di tutto il mercato.
   5. *Volatilità*: l'espansione c'è ma senza direzione → R ≈ 0 con dispersione alta.
   6. *Pochi episodi* → R senza i 3 migliori. 7. *Artefatto*: periodi di dati piatti (buchi
   riempiti dalla fonte) sembrano compressioni → barre a volume zero in Fase 0.
   8. *Costi*: lo stop alla banda di mezzo è vicino → costi in R più alti.
   9. *Effetto della sola rottura*: la compressione non aggiunge nulla rispetto alla rottura di I-02
      → simile alla (a) per rotture. 10. *Funding* dopo le rotture al rialzo.
6. **Ipotesi completa.** TRBUSDT, squeeze, 4h. Bande a 20 barre e 2 deviazioni standard; ampiezza =
   4 σ20 / media20; compressione alla barra i−1 se l'ampiezza è ≤ al 20° percentile delle 120
   ampiezze fino a i−1.
   * **I-07-L** long se compressione a i−1 e c[i] > banda alta[i]; stop = media20[i]; tenere 30 barre.
   * **I-07-S** short se compressione a i−1 e c[i] < banda bassa[i]; stop = media20[i]; tenere 30 barre.

---

## I-08 — Ritorno di brevissimo periodo nel verso del trend (RSI a 2 barre)

1. **Fonte.** L. Connors, C. Alvarez, «Short Term Trading Strategies That Work», TradingMarkets,
   2008 (compra se il prezzo è sopra la media a 200 e l'RSI a 2 periodi è sotto 10; esci quando
   chiude sopra la media a 5). L'RSI: J. W. Wilder, «New Concepts in Technical Trading Systems»,
   1978.
2. **Affermazione.** Su TRBUSDT, in trend rialzista (sopra la media a 200 barre di 4h), un ribasso
   brusco di 2 barre (RSI2 < 10) torna su in pochi giorni: long con R medio positivo e sopra la (b);
   specchio in trend ribassista.
3. **Sotto-domande.** Funziona in mercati volatili? Chi opera: venditori impazienti che spingono
   il prezzo sotto il valore in un trend sano; compratori di sconti. Tempi: 1-5 barre.
4. **Spiegazioni concorrenti**: 1. *Caso*. 2. *Momentum di breve*: i cali bruschi continuano.
   3. *Trend di fondo*: il filtro della media a 200 sceglie periodi di rialzo, la (b) senza filtro
   no → la (a) (stessa uscita, senza condizione) lo misura. 4. *È solo il mercato*. 5. *Volatilità*:
   lo stop largo a 3 ATR scatta raramente ma costa molto → pochi trade enormi negativi. 6. *R
   asimmetrici*: molti piccoli guadagni e rare grandi perdite → il pavimento dell'errore lo copre.
   7. *Costi*: uscite rapide e guadagni piccoli → costi in R alti. 8. *Pochi episodi*. 9. *Artefatto*:
   barre errate. 10. *Dipendenza dall'uscita*: uscire sopra la media a 5 garantisce piccoli
   guadagni frequenti a qualunque ingresso → la (a) e la (b) hanno la stessa uscita e lo misurano.
6. **Ipotesi completa.** TRBUSDT, RSI2, 4h (a 1d non si arriva a 70 trade con 200 barre di
   riscaldamento).
   * **I-08-L** long se c[i] > media200[i] e RSI2[i] < 10; stop c[i] − 3 ATR; «chiudi» alla prima
     chiusura sopra media5.
   * **I-08-S** short se c[i] < media200[i] e RSI2[i] > 90; stop c[i] + 3 ATR; «chiudi» alla prima
     chiusura sotto media5.

---

## I-09 — Premio del volume alto

1. **Fonte.** S. Gervais, R. Kaniel, D. H. Mingelgrin, «The High-Volume Return Premium», Journal of
   Finance 56(3), giugno 2001 (un volume insolitamente alto aumenta la visibilità e precede
   rendimenti più alti).
2. **Affermazione.** Su TRBUSDT un giorno con volume oltre 2 volte la media dei 20 giorni precedenti
   è seguito da 5 giorni con R medio dopo i costi positivo e sopra la (b) (long).
3. **Sotto-domande.** Conta il segno del rendimento del giorno? La fonte dice di no. Chi opera: nuovi
   investitori attirati dall'attenzione. Tempi: giorni o settimane.
4. **Spiegazioni concorrenti**: 1. *Caso*. 2. *Pump and dump*: il volume alto è un picco che si
   sgonfia → R sotto la (b) (idea I-04 al contrario). 3. *Trend di fondo*. 4. *È solo il mercato*:
   volume alto di tutto il mercato nei giorni di panico. 5. *Volatilità*: volume e volatilità vanno
   insieme → stop. 6. *Costi*: poco rilevanti a 5 giorni. 7. *Pochi episodi*. 8. *Artefatto*:
   il volume in moneta cambia col prezzo (a prezzo basso più unità) → la media su 20 giorni lo
   attenua. 9. *Notizie*: il volume è informazione, nei due sensi → R ≈ 0. 10. *Anno*: un anno solo.
6. **Ipotesi completa.** TRBUSDT, volume alto, 1d, long (il meccanismo è di giorni).
   * **I-09-L** long se volume[i] > 2 × media(volume[i-20..i-1]); stop c[i] − 2 ATR (a 1d circa il
     doppio del limite del 6% del bot: dichiarato); tenere 5 barre.
   Una sola variante: la fonte afferma un premio, non un'inversione.

---

## I-10 — Momentum dentro la giornata (prima mezz'ora → ultima mezz'ora)

1. **Fonte.** L. Gao, Y. Han, S. Z. Li, G. Zhou, «Market intraday momentum», Journal of Financial
   Economics 129(2), agosto 2018. Per le crypto: «Intraday return predictability in the
   cryptocurrency markets: Momentum, reversal, or both», North American Journal of Economics and
   Finance 62, 2022 (DOI 10.1016/j.najef.2022.101733; autori da confermare sulla pagina
   dell'editore, che la sessione non ha aperto).
2. **Affermazione.** Su TRBUSDT il segno del rendimento della prima mezz'ora UTC (00:00-00:30)
   predice quello dell'ultima mezz'ora (23:30-24:00): R medio dopo i costi positivo e sopra la (b).
3. **Sotto-domande.** Vale nei giorni volatili? Chi opera: chi ribilancia a fine giornata UTC e chi
   reagisce in ritardo alle notizie della notte. Tempi: una mezz'ora.
4. **Spiegazioni concorrenti**: 1. *Caso*. 2. *Costi*: con una mezz'ora il movimento tipico è dello
   stesso ordine dei costi (sezione 11, «Costi a orizzonte corto») → R netto negativo anche con un
   effetto lordo. 3. *Nessuna «giornata» nelle crypto*: mercato continuo, la mezzanotte UTC non è
   speciale. 4. *È solo il mercato*: l'effetto è di BTC. 5. *Volatilità*. 6. *Funding*: alle
   00:00 c'è un settlement, che sposta il prezzo della prima mezz'ora. 7. *Artefatto*: barre
   mancanti a cavallo della mezzanotte. 8. *Trend di fondo*. 9. *Pochi giorni estremi*.
   10. *Inversione*: nelle altcoin poco liquide prevale il ritorno → R sotto la (b).
6. **Ipotesi completa.** TRBUSDT, momentum dentro la giornata, 30m. Alla chiusura della barra
   23:00-23:30: r1 = c/o della barra 00:00-00:30 dello stesso giorno (se manca, nessun segnale).
   * **I-10-L** long se r1 > 0; stop c[i] − 1 ATR; tenere 1 barra.
   * **I-10-S** short se r1 < 0; stop c[i] + 1 ATR; tenere 1 barra.

---

## I-11 — Numeri tondi: accelerazione dopo l'attraversamento

1. **Fonte.** C. L. Osler, «Currency Orders and Exchange Rate Dynamics: An Explanation for the
   Predictive Success of Technical Analysis», Journal of Finance 58(5), ottobre 2003 (gli ordini
   stop si accumulano appena oltre i numeri tondi: attraversato il numero, il movimento accelera).
2. **Affermazione.** Su TRBUSDT, quando la chiusura oraria attraversa un numero tondo (multipli di
   5 USDT sotto 100, di 50 USDT fra 100 e 1000, di 0,5 sotto 10), nelle 12 ore dopo il prezzo
   continua nel verso dell'attraversamento: R medio dopo i costi positivo e sopra la (b).
3. **Sotto-domande.** Conta da quanto tempo il prezzo non tocca quel numero? Chi opera: stop dei
   piccoli operatori raggruppati oltre i numeri tondi. Tempi: ore.
4. **Spiegazioni concorrenti**: 1. *Caso*. 2. *Inversione ai numeri tondi*: Osler dice anche che
   gli ordini di presa di profitto stanno sui numeri tondi e fanno tornare il prezzo → R sotto la
   (b). 3. *Attraversamenti ripetuti*: il prezzo oscilla attorno al numero e genera segnali a
   vuoto → molti stop piccoli. 4. *Trend di fondo*. 5. *È solo il mercato*. 6. *Volatilità*.
   7. *Costi*: stop a 1,5 ATR orari → costi in R non trascurabili. 8. *Scala del prezzo*: un numero
   tondo vale solo per chi guarda quella scala → poco effetto. 9. *Pochi episodi*. 10. *Artefatto*.
6. **Ipotesi completa.** TRBUSDT, numeri tondi, 1h. Passo del livello: 0,5 per prezzi sotto 10, 5
   per prezzi fra 10 e 100, 50 per prezzi fra 100 e 1000 (calcolato sul prezzo c[i-1]).
   * **I-11-L** long se fra c[i-1] e c[i] c'è un livello attraversato al rialzo; stop c[i] − 1,5 ATR;
     tenere 12 barre.
   * **I-11-S** short se attraversato al ribasso; stop c[i] + 1,5 ATR; tenere 12 barre.

---

## I-12 — Posizione della chiusura nella barra (internal bar strength)

1. **Fonte.** A. Pagonidis, «The IBS Effect: Mean Reversion in Equity ETFs», articolo per il premio
   NAAIM, 2013 (dati fino al 12 maggio 2013; riassunto da Quantpedia nel febbraio 2014): una
   chiusura vicina al minimo del giorno (IBS < 0,2) precede un rialzo il giorno dopo, vicina al
   massimo (IBS > 0,8) un calo.
2. **Affermazione.** Su TRBUSDT, IBS = (c − l)/(h − l) del giorno sotto 0,2 → il giorno dopo R medio
   dopo i costi positivo e sopra la (b) per un long; sopra 0,8 → per uno short.
3. **Sotto-domande.** La fonte dice più forte dopo giorni ampi e volatili e a inizio settimana.
   Chi opera: venditori forzati a fine giornata, poi compratori di sconti. Tempi: un giorno.
4. **Spiegazioni concorrenti**: 1. *Caso*. 2. *Momentum*: chiusura al minimo = pressione di vendita
   che continua → R sotto la (b). 3. *Nessuna chiusura nelle crypto*: la «chiusura» UTC non è un
   momento d'asta. 4. *Trend di fondo*. 5. *È solo il mercato*. 6. *Volatilità*. 7. *Costi*
   piccoli a un giorno. 8. *Pochi giorni estremi*. 9. *Artefatto*: barre con high = low.
   10. *Anno*.
6. **Ipotesi completa.** TRBUSDT, IBS, 1d. Stop 6% (come I-06: a 1d l'ATR supera il limite del bot;
   con un giorno di durata lo stop è una protezione).
   * **I-12-L** long se IBS[i] < 0,2; stop c[i] × 0,94; tenere 1 barra.
   * **I-12-S** short se IBS[i] > 0,8; stop c[i] × 1,06; tenere 1 barra.

---

## I-13 — Rottura del range della prima ora (opening range breakout)

1. **Fonte.** T. Crabel, «Day Trading with Short Term Price Patterns and Opening Range Breakout»,
   Traders Press, 1990.
2. **Affermazione.** Su TRBUSDT, la prima chiusura a 15 minuti sopra il massimo della prima ora UTC
   (00:00-01:00) è seguita da un rialzo fino a fine giornata: long con R medio dopo i costi positivo
   e sopra la (b); specchio sotto il minimo.
3. **Sotto-domande.** Vale di più se la prima ora è stretta? Chi opera: chi entra quando il mercato
   «sceglie una direzione» della giornata; stop raggruppati ai bordi del primo range. Tempi: ore.
4. **Spiegazioni concorrenti**: 1. *Caso*. 2. *Nessuna apertura nelle crypto*: la prima ora UTC non è
   speciale → nessun effetto. 3. *Falsa rottura* → stop. 4. *Trend di fondo*. 5. *È solo il
   mercato*. 6. *Volatilità*: i giorni con rottura sono i giorni volatili. 7. *Costi*: stop alla
   parte opposta del range, vicino → costi in R alti. 8. *Funding* alle 00:00 sposta la prima ora.
   9. *Pochi giorni estremi*. 10. *Artefatto* di barre mancanti nella prima ora.
6. **Ipotesi completa.** TRBUSDT, rottura della prima ora, 15m. Range = massimo e minimo delle 4
   barre 00:00-01:00 UTC del giorno (tutte presenti). Solo la PRIMA chiusura fuori dal range del
   giorno conta; nessun segnale dopo le 22:00 UTC.
   * **I-13-L** long alla prima chiusura sopra il massimo; stop = minimo del range; «chiudi» alla
     chiusura della barra 23:45-24:00.
   * **I-13-S** short alla prima chiusura sotto il minimo; stop = massimo del range; «chiudi» alla
     chiusura della barra 23:45-24:00.
