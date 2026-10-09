# Ipotesi della campagna MASKUSDT

Scritte prima di qualunque test (regola 2 e Fase 1). Ogni idea ha: fonte pubblicata prima
del 2024-01-01; affermazione falsificabile; sotto-domande; almeno 10 spiegazioni concorrenti,
ognuna con la previsione che farebbe e cosa la smentirebbe; l'ipotesi completa con tutte le
varianti e il loro motivo. Le previsioni numeriche sono nella sezione «Previsioni», scritta
dopo la descrizione dei dati della Fase 0 (costi in R) e prima del primo test.

Regole comuni a tutte le varianti (fissate prima del primo test, regola 9):

* segnali alla chiusura della barra, ingresso all'apertura della barra dopo (motore, sezione 7);
* una posizione alla volta, una sola direzione per variante;
* stop a k volte l'ATR di Wilder a 14 barre del timeframe, misurato dal close della barra del
  segnale; target, se c'è, a un multiplo della distanza dello stop; uscita a tempo («chiudi»
  alla chiusura della barra, eseguita all'apertura della barra dopo) dove è scritta;
* stop sul last, liquidazione sul mark, funding vero ai settlement, costi della scheda
  (commissione 0,05% e slippage 0,05% per lato);
* filtro di liquidità della Fase 0 (`fase0_dati.md`): nessun ingresso su segnali di barre dei
  mesi sotto 20 milioni di USDT al giorno; uguale per la stima dei trade, il test e la (a);
* il riscaldamento di ogni indicatore della variante blocca il segnale (la (a) parte dalla prima
  barra in cui la variante può entrare, la (b) non entra nel riscaldamento).

Il periodo di costruzione va dal 2021-08-01 al 2023-04-10 (618 giorni): 70 trade sono un
ingresso ogni 9 giorni circa. Per questo nessuna idea è proposta a 12 ore o a 1 giorno con
uscite di più giorni: non arriverebbe ai trade minimi.

Le spiegazioni concorrenti «noiose» compaiono in ogni idea: si scrivono per esteso ogni volta,
perché la previsione che fanno e ciò che le smentisce cambia con l'idea.

---

## I-01 — Momento nel tempo (il rendimento dell'ultima settimana continua)

**Fonte.** Tobias J. Moskowitz, Yao Hua Ooi, Lasse Heje Pedersen, «Time Series Momentum»,
Journal of Financial Economics 104(2), maggio 2012. Per le crypto: Yukun Liu, Aleh Tsyvinski,
«Risks and Returns of Cryptocurrency», Review of Financial Studies 34(6), giugno 2021 (versione
di lavoro NBER 24877, agosto 2018): il rendimento di una settimana predice quello delle settimane
successive.

**Affermazione falsificabile.** Su MASKUSDT, quando il rendimento delle ultime 7 giornate (42
barre da 4 ore) è positivo, le 72 ore seguenti hanno un R medio dopo i costi più alto di un
ingresso casuale long con la stessa uscita; quando è negativo, lo stesso per gli short.
Smentita: l'R medio non supera nettamente la (b).

**Sotto-domande.** Vale più nei periodi di trend del mercato intero (BTC) o anche quando la
moneta si muove da sola? Dipende dalla volatilità (in alta volatilità il momento si spegne,
come nei «crash del momento»)? Chi compra dopo una settimana di rialzo: investitori che
inseguono il prezzo, flussi di attenzione, posizioni che si aprono lentamente. Quando: gli
studi lo vedono da 1 a 4 settimane; qui si tiene 3 giorni per avere abbastanza trade.

**Spiegazioni concorrenti.**

1. *Effetto casuale.* Previsione: R medio vicino a quello della (b), `t` fra -2 e 2. Smentita: `t`
   contro la (b) sopra la soglia.
2. *È solo il mercato* (MASK segue BTC, e BTC ha avuto trend lunghi nel 2021-2022). Previsione:
   l'effetto sparisce nelle settimane in cui BTC e MASK hanno segni opposti. Smentita: l'effetto
   resta quando il segno di MASK è opposto a quello di BTC.
3. *Trend di fondo* (la moneta scende quasi sempre dal 2021: gli short vincono comunque).
   Previsione: la variante short batte la (a) ma non la (b), che entra a caso nella stessa
   direzione. Smentita: batte nettamente la (b).
4. *Volatilità.* Il segnale coincide con periodi di alta volatilità, dove stop e uscite a tempo
   danno R diversi. Previsione: R per trade simile alla (b) con la stessa uscita. Smentita: batte la (b).
5. *Artefatto dei dati* (buchi del mark, barre tolte). Previsione: risultato concentrato nei
   giorni vicini alle barre tolte. Smentita: barre tolte poche e lontane dai trade migliori.
6. *Effetto costi.* Uscite a 3 giorni con stop di circa 5%: i costi pesano poco (circa 0,04 R).
   Previsione: con costi doppi cambia poco. Smentita: con costi doppi l'R medio diventa negativo.
7. *Pochi trade estremi* (un pump o un crollo fanno tutto). Previsione: senza i 3 migliori l'R
   medio va sotto la (b). Smentita: resta sopra.
8. *Un solo anno.* Previsione: tutto il vantaggio nel 2021 (rialzo) o nel 2022 (ribasso).
   Smentita: R medio sopra la (b) in più della metà degli anni con almeno 10 trade.
9. *Inversione a breve* (nelle crypto a 1-3 giorni domina il ritorno verso la media). Previsione:
   R medio sotto la (b). Smentita: R medio sopra.
10. *Funding* (in trend il funding si sposta nella direzione del trend e il costo cancella
    l'effetto). Previsione: R lordo positivo e netto nullo. Smentita: il funding totale è piccolo
    rispetto al guadagno.
11. *Lookahead nel codice.* Previsione: il ritardo di una barra lo fa crollare. Smentita: col
    ritardo il `t` resta almeno a metà.

**Ipotesi completa.** MASKUSDT, momento nel tempo a 7 giorni, timeframe 4 ore (la misura è di
giorni: la candela da 4 ore dà un segnale aggiornato sei volte al giorno senza scendere nel
rumore intraday).

* **I-01-L** long: rendimento delle ultime 42 barre > 0. Stop 2 ATR(4h), nessun target, uscita
  dopo 18 barre (72 ore). Motivo: la direzione del segnale della fonte.
* **I-01-S** short: rendimento delle ultime 42 barre < 0. Stessa uscita. Motivo: la fonte è
  simmetrica; le due direzioni sono due varianti.

---

## I-02 — Rottura del canale (il prezzo che esce dal massimo recente continua)

**Fonte.** William Brock, Josef Lakonishok, Blake LeBaron, «Simple Technical Trading Rules and
the Stochastic Properties of Stock Returns», Journal of Finance 47(5), dicembre 1992 (regola di
rottura del massimo o del minimo dell'intervallo recente).

**Affermazione falsificabile.** Su MASKUSDT a 1 ora, quando il close supera il massimo delle
48 barre precedenti (2 giorni), le 24 ore seguenti hanno R medio dopo i costi più alto di un
ingresso long casuale con la stessa uscita; simmetrico per il minimo e lo short. Smentita: non
batte nettamente la (b).

**Sotto-domande.** La rottura conta di più se arriva dopo un periodo calmo? Chi compra sulla
rottura: ordini di stop degli short, chi segue i massimi, liquidazioni degli short (nei futures
con leva la rottura di un livello fa scattare stop e liquidazioni a catena). Quanto dura: le
cascate di stop durano ore; l'uscita a 24 ore copre il primo giorno.

**Spiegazioni concorrenti.**

1. *Effetto casuale.* Previsione: `t` contro la (b) fra -2 e 2. Smentita: `t` sopra soglia.
2. *È solo il mercato.* Le rotture di MASK coincidono con rotture di BTC. Previsione: l'R medio
   delle rotture senza rottura di BTC nelle stesse ore è vicino a zero. Smentita: è come le altre.
3. *Trend di fondo.* Previsione: batte la (a) ma non la (b). Smentita: batte la (b).
4. *Falsa rottura* (nelle monete piccole le rotture rientrano spesso: caccia agli stop).
   Previsione: R medio sotto la (b) e molti stop nelle prime ore. Smentita: R sopra la (b).
5. *Volatilità.* Le rotture arrivano in barre ampie; lo stop in ATR si allarga e l'R per trade
   cambia scala. Previsione: nessuna differenza dalla (b), che usa lo stesso stop. Smentita: batte la (b).
6. *Effetto costi.* A 1 ora lo stop di 2 ATR è circa 2-3%: il giro costa circa 0,08-0,10 R.
   Previsione: con costi doppi l'R medio scende di circa 0,1 R. Smentita: crolla molto di più.
7. *Artefatto dei dati.* Previsione: rotture concentrate dopo i buchi (un salto dopo un buco
   sembra una rottura). Smentita: pochi trade vicini ai buchi.
8. *Pochi trade estremi.* Previsione: i 3 migliori fanno quasi tutto. Smentita: senza di loro
   resta sopra la (b).
9. *Un solo anno.* Previsione: vantaggio solo nel 2021. Smentita: più della metà degli anni.
10. *Lookahead.* Il massimo delle 48 barre precedenti esclude la barra del segnale: col ritardo di
    una barra il `t` deve restare almeno a metà.
11. *Funding:* dopo le rotture al rialzo il funding sale e costa ai long. Previsione: funding
    totale negativo per il risultato ma piccolo. Smentita: il funding cancella il guadagno.

**Ipotesi completa.** MASKUSDT, rottura del canale di 48 barre, timeframe 1 ora (la cascata di
stop dura ore: la candela oraria la vede senza il rumore dei 15 minuti).

* **I-02-L** long: close > massimo dei high delle 48 barre precedenti. Stop 2 ATR(1h), nessun
  target, uscita dopo 24 barre.
* **I-02-S** short: close < minimo dei low delle 48 barre precedenti. Stessa uscita.

---

## I-03 — Ritorno dopo una barra estrema (eccesso di reazione a breve)

**Fonte.** Narasimhan Jegadeesh, «Evidence of Predictable Behavior of Security Returns», Journal
of Finance 45(3), luglio 1990; Bruce N. Lehmann, «Fads, Martingales, and Market Efficiency»,
Quarterly Journal of Economics 105(1), febbraio 1990: i rendimenti estremi di breve periodo
tendono a rientrare.

**Affermazione falsificabile.** Su MASKUSDT a 1 ora, dopo una barra con rendimento sotto -3
deviazioni standard (deviazione dei rendimenti orari delle 168 barre precedenti), le 6 ore
seguenti hanno R medio long più alto di un ingresso long casuale con la stessa uscita; dopo una
barra sopra +3 deviazioni, lo stesso per lo short. Smentita: non batte nettamente la (b).

**Sotto-domande.** L'eccesso viene da liquidazioni forzate (vendite a mercato di chi ha leva) o
da notizie vere? Le notizie danno movimenti che restano, le liquidazioni movimenti che
rientrano. Chi compra dopo il crollo: chi fornisce liquidità e incassa il premio. In quanto
tempo: ore.

**Spiegazioni concorrenti.**

1. *Effetto casuale.* Previsione: `t` fra -2 e 2. Smentita: `t` sopra soglia.
2. *È solo il mercato* (la barra estrema è un crollo di tutto il mercato, e il mercato rimbalza).
   Previsione: l'effetto c'è solo quando anche BTC ha una barra estrema. Smentita: c'è anche senza.
3. *Notizia vera* (il movimento continua). Previsione: R medio sotto la (b). Smentita: sopra.
4. *Rimbalzo del prezzo fra bid e ask* (rumore di microstruttura). A 1 ora e con un -3 deviazioni
   il rimbalzo di un tick è piccolo rispetto allo stop. Previsione: effetto solo nella prima
   barra, mangiato dallo slippage. Smentita: l'effetto regge con costi doppi.
5. *Volatilità.* Dopo una barra estrema la volatilità resta alta: lo stop in ATR è largo e gli R
   sono più piccoli in valore assoluto. Previsione: nessuna differenza con la (b). Smentita: batte la (b).
6. *Trend di fondo.* Previsione: la variante short va meglio solo perché la moneta scende.
   Smentita: batte la (b) nella stessa direzione.
7. *Artefatto dei dati* (una barra «estrema» dopo un buco: il rendimento misura più ore).
   Previsione: molti segnali subito dopo i buchi. Smentita: pochi.
8. *Effetto costi.* 6 ore con stop 2-3%: circa 0,08-0,10 R a giro. Smentita: regge a costi doppi.
9. *Pochi trade estremi.* Smentita: senza i 3 migliori resta sopra la (b).
10. *Un solo anno.* Smentita: più della metà degli anni.
11. *Lookahead.* Smentita dal ritardo di una barra (atteso un calo forte ma non un crollo: un
    effetto di poche ore perde molto con un'ora di ritardo, e lo si dichiara).

**Ipotesi completa.** MASKUSDT, ritorno dopo una barra oraria estrema, timeframe 1 ora (le
liquidazioni a catena si vedono in un'ora; a 15 minuti i costi sono dello stesso ordine del
movimento, sezione 11).

* **I-03-L** long: rendimento logaritmico della barra < -3 × deviazione standard dei rendimenti
  delle 168 barre precedenti. Stop 2 ATR(1h), target 2 ATR (rapporto 1), uscita dopo 6 barre.
* **I-03-S** short: rendimento > +3 deviazioni. Stessa uscita.

---

## I-04 — Ritracciamento a 2 periodi dentro il trend

**Fonte.** Larry Connors, Cesar Alvarez, «Short Term Trading Strategies That Work»,
TradingMarkets Publishing, 2009 (RSI a 2 periodi sotto 10 con il prezzo sopra la media a 200,
uscita alla chiusura sopra la media a 5).

**Affermazione falsificabile.** Su MASKUSDT a 1 ora, con il close sopra la media semplice di
200 barre e l'RSI a 2 barre sotto 10, il long con uscita alla chiusura sopra la media di 5
barre ha R medio più alto di un long casuale con la stessa uscita. Simmetrico per lo short.
Smentita: non batte nettamente la (b).

**Sotto-domande.** Il ritracciamento in un trend è un'occasione (chi aspettava un prezzo
migliore compra) o l'inizio dell'inversione? Funziona solo con trend forte? A 1 ora la media
di 200 barre è circa 8 giorni: un trend di settimane.

**Spiegazioni concorrenti.**

1. *Effetto casuale.* Smentita: `t` sopra soglia.
2. *È solo il mercato.* Previsione: i ritracciamenti di MASK sono quelli di BTC; l'effetto
   sparisce quando BTC non ritraccia. Smentita: c'è anche senza.
3. *Rimbalzo di microstruttura.* Previsione: tutto il guadagno nella prima barra. Smentita:
   regge con un'ora di ritardo.
4. *Uscita asimmetrica* (uscire alla prima chiusura sopra la media di 5 dà molti piccoli
   guadagni e rare grandi perdite: R medio alto ma fragile). Previsione: win rate alto, R medio
   vicino alla (b), che ha la stessa uscita. Smentita: batte la (b).
5. *Trend di fondo.* Smentita: batte la (b).
6. *Volatilità.* Smentita: batte la (b) con lo stesso stop.
7. *Effetto costi* (uscite rapide: molti giri). Previsione: a costi doppi R negativo. Smentita: resta positivo.
8. *Artefatto dei dati.* Smentita: pochi trade vicini ai buchi.
9. *Pochi trade estremi.* Smentita: senza i 3 migliori resta sopra.
10. *Un solo anno.* Smentita: più della metà degli anni.
11. *Fuori scala.* La regola nasce sulle azioni a 1 giorno; a 1 ora potrebbe non valere.
    Previsione: nessun effetto. Smentita: effetto netto.

**Ipotesi completa.** MASKUSDT, ritracciamento a 2 periodi, timeframe 1 ora (a 1 giorno i
trade sarebbero troppo pochi in 618 giorni; la regola usa solo rapporti fra medie e RSI, che
non hanno unità di tempo).

* **I-04-L** long: close > media 200 e RSI(2) < 10. Uscita alla prima chiusura sopra la media di
  5 barre; stop 3 ATR(1h) (la fonte non ha stop: il bot lo vuole, largo per non cambiare la
  regola); uscita di sicurezza dopo 48 barre; nessun target.
* **I-04-S** short: close < media 200 e RSI(2) > 90. Uscita alla prima chiusura sotto la media di
  5; stessa protezione.

---

## I-05 — Funding estremo contro la folla

**Fonte.** Maik Schmeling, Andreas Schrimpf, Karamfil Todorov, «Crypto Carry», BIS Working
Papers n. 1087, aprile 2023: un carry (premio dei futures, funding) alto segnala domanda
speculativa con leva e predice rendimenti futuri più bassi e crolli.

**Affermazione falsificabile.** Su MASKUSDT, quando l'ultimo tasso di funding regolato è fra il
10% più alto dei 270 settlement precedenti (90 giorni), le 24 ore seguenti hanno R medio short
più alto di uno short casuale con la stessa uscita; quando è fra il 10% più basso, lo stesso
per i long (gli short affollati vengono schiacciati). Smentita: non batte nettamente la (b).

**Sotto-domande.** Il funding alto è causa (costo che spinge a chiudere i long) o sintomo
(folla con leva che si fa liquidare)? Funziona solo con funding sopra lo 0,01% base? Il
funding si regola ogni 8 ore: il segnale cambia solo ai settlement.

**Spiegazioni concorrenti.**

1. *Effetto casuale.* Smentita: `t` sopra soglia.
2. *È solo il mercato* (il funding è alto su tutte le monete nei rialzi del mercato). Previsione:
   l'effetto segue i rialzi e i crolli di BTC. Smentita: c'è anche fuori da quelli.
3. *Trend di fondo.* Lo short vince perché la moneta scende. Smentita: batte la (b).
4. *Il funding alto segue il rialzo* (e allora è il ritorno dopo un rialzo, I-03, non il
   funding). Previsione: l'effetto sparisce controllando il rendimento delle 24 ore prima.
   Smentita: regge (da verificare solo se diventa candidato, Fase 5).
5. *Momento.* Funding alto in trend forte: lo short perde. Previsione: R sotto la (b). Smentita: sopra.
6. *Il funding incassato fa il risultato* (lo short incassa il funding alto). Previsione: R
   lordo nullo, netto positivo per il funding. Smentita: R lordo positivo. Si dichiara.
7. *Volatilità.* Smentita: batte la (b) con lo stesso stop.
8. *Artefatto dei dati* (settlement mancanti, intervallo cambiato). Smentita: copertura
   completa del funding in `fase0_dati.md`.
9. *Pochi trade estremi.* Smentita: senza i 3 migliori resta sopra.
10. *Un solo anno.* Smentita: più della metà degli anni.
11. *Effetto costi.* A 8 ore lo stop di 2 ATR è circa 6-8%: costi piccoli. Smentita: regge a costi doppi.

**Ipotesi completa.** MASKUSDT, funding estremo, timeframe 8 ore (il segnale si aggiorna a ogni
settlement, ogni 8 ore). Il tasso usato alla chiusura della barra è l'ultimo settlement con
istante entro la chiusura; la soglia è il 90° (10°) percentile dei 270 settlement precedenti,
escluso il corrente.

* **I-05-S** short: funding > 90° percentile dei 270 precedenti e > 0. Stop 2 ATR(8h), nessun
  target, uscita dopo 3 barre (24 ore).
* **I-05-L** long: funding < 10° percentile dei 270 precedenti e < 0,0001 (sotto il tasso base).
  Stessa uscita.

---

## I-06 — Premio del volume alto (attenzione)

**Fonte.** Simon Gervais, Ron Kaniel, Dan H. Mingelgrin, «The High-Volume Return Premium»,
Journal of Finance 56(3), giugno 2001: un volume insolitamente alto attira attenzione e predice
rendimenti più alti nei giorni e nelle settimane seguenti.

**Affermazione falsificabile.** Su MASKUSDT a 4 ore, quando il volume in USDT delle ultime 6
barre (24 ore) supera 2,5 volte la media delle 24 ore dei 49 giorni precedenti, il long tenuto 5
giorni ha R medio più alto di un long casuale con la stessa uscita. Smentita: non batte
nettamente la (b).

**Sotto-domande.** Il volume alto viene con prezzo in salita o in discesa? La fonte trova
l'effetto per entrambi. Chi compra dopo: nuovi investitori che hanno «visto» la moneta. Quanto
dura: giorni o settimane.

**Spiegazioni concorrenti.**

1. *Effetto casuale.* Smentita: `t` sopra soglia.
2. *È solo il mercato* (volumi alti su tutto il mercato nei giorni di crollo e rimbalzo).
   Smentita: effetto anche quando il volume di BTC non è alto.
3. *Pump e scarico* (nelle monete piccole il volume alto è spesso un pump, seguito da un
   crollo). Previsione: R sotto la (b). Smentita: R sopra.
4. *Trend di fondo.* Smentita: batte la (b).
5. *Volatilità.* Dopo il volume alto la volatilità è alta, lo stop largo. Smentita: batte la (b).
6. *Artefatto dei dati* (volume mancante o doppio nei file). Smentita: barre senza volume
   contate in Fase 0 e poche.
7. *Pochi trade estremi.* Smentita: senza i 3 migliori resta sopra.
8. *Un solo anno.* Smentita: più della metà degli anni.
9. *Effetto costi.* 5 giorni, stop circa 7%: costi minimi. Smentita: regge a costi doppi.
10. *Funding* (dopo i volumi alti il funding sale e costa ai long). Smentita: funding piccolo.
11. *Lookahead* (il volume della barra del segnale è noto alla chiusura). Smentita dal ritardo.

**Ipotesi completa.** MASKUSDT, volume alto, timeframe 4 ore (il volume di un giorno si misura
su 6 barre aggiornate ogni 4 ore).

* **I-06-L** long: volume in USDT delle ultime 6 barre > 2,5 × media dei volumi di 6 barre delle
  294 barre precedenti (49 giorni). Stop 3 ATR(4h), nessun target, uscita dopo 30 barre (5
  giorni). Solo long: la fonte è un premio, non una regola simmetrica.
* **I-06-Lb** (aggiunta dopo lo scarto di I-06-L per i trade minimi, 21 trade stimati, prima di
  qualunque test dell'idea; regola 6: allentare le soglie di uno scarto senza aver visto risultati
  è ancora una variante dell'idea nuova): volume delle 6 barre > 1,5 × il riferimento; uscita dopo
  12 barre (2 giorni) invece di 30, perché con 5 giorni di posizione gli ingressi possibili in 592
  giorni sono al massimo circa 120. Stop 3 ATR(4h). Previsione: R medio fra -0,20 e +0,10, non
  batte nettamente la (b).

---

## I-07 — Dopo il pump, lo scarico

**Fonte.** Josh Kamps, Bennett Kleinberg, «To the moon: defining and detecting cryptocurrency
pump-and-dumps», Crime Science 7, articolo 18, novembre 2018; Tao Li, Donghwa Shin, Baolian Wang,
«Cryptocurrency Pump-and-Dump Schemes», SSRN 3267041, 2018: rialzi rapidi con volume anomalo
nelle monete piccole sono spesso seguiti da un rientro.

**Affermazione falsificabile.** Su MASKUSDT a 1 ora, dopo 3 barre con rendimento cumulato sopra
+3 deviazioni standard (dei rendimenti a 3 barre delle 168 barre precedenti) e volume in USDT
delle 3 barre sopra 3 volte la media a 3 barre delle 168 precedenti, lo short tenuto 24 ore ha R
medio più alto di uno short casuale con la stessa uscita. Smentita: non batte nettamente la (b).

**Sotto-domande.** Il pump è coordinato (gruppi) o nasce da una notizia? Senza notizie rientra.
Chi vende dopo: gli organizzatori e chi ha comprato prima. In quanto tempo: ore o un giorno.

**Spiegazioni concorrenti.**

1. *Effetto casuale.* Smentita: `t` sopra soglia.
2. *È solo il mercato.* Smentita: effetto anche quando BTC non sale nelle stesse ore.
3. *Notizia vera* (il prezzo resta su). Previsione: R sotto la (b). Smentita: sopra.
4. *Momento* (il pump continua per ore, short schiacciati). Previsione: molti stop. Smentita: R sopra la (b).
5. *Trend di fondo.* Smentita: batte la (b).
6. *Volatilità.* Smentita: batte la (b) con lo stesso stop.
7. *Artefatto dei dati.* Smentita: pochi segnali dopo buchi.
8. *Pochi trade estremi* (uno o due grandi pump fanno tutto). Smentita: senza i 3 migliori resta sopra.
9. *Un solo anno.* Smentita: più della metà degli anni.
10. *Funding* (dopo il pump il funding sale: lo short incassa). Si dichiara il funding.
11. *Effetto costi.* Smentita: regge a costi doppi.

**Ipotesi completa.** MASKUSDT, scarico dopo il pump, timeframe 1 ora.

* **I-07-S** short: rendimento delle ultime 3 barre > 3 deviazioni e volume delle ultime 3 barre
  > 3 × la media a 3 barre delle 168 precedenti. Stop 2 ATR(1h), nessun target, uscita dopo 24 barre.
* **I-07-Sb** (solo se I-07-S è uno scarto per i trade minimi, prima di qualunque test
  dell'idea): soglie allentate a 2,5 deviazioni e 2 volte il volume. Motivo: stessa idea, soglie
  meno rare.

---

## I-08 — MASK in ritardo su BTC

**Fonte.** Imtiaz Mohammad Sifat, Azhar Mohamad, Mohamed Shariff Bin Mohamed Shariff,
«Lead-Lag relationship between Bitcoin and Ethereum: Evidence from hourly and daily data»,
Research in International Business and Finance 50, dicembre 2019; Pavel Ciaian, Miroslava
Rajcaniova, d'Artis Kancs, «Virtual relationships: Short- and long-run evidence from BitCoin and
altcoin markets», Journal of International Financial Markets, Institutions and Money 52, 2018.

**Affermazione falsificabile.** Su MASKUSDT a 1 ora, quando BTC ha chiuso l'ora con un
rendimento sopra +2 deviazioni standard (delle 168 ore precedenti di BTC) e MASK nella stessa
ora ha fatto meno della metà del rendimento di BTC, il long MASK tenuto 4 ore ha R medio più
alto di un long casuale con la stessa uscita; simmetrico al ribasso per lo short. Smentita: non
batte nettamente la (b).

**Sotto-domande.** Chi arriva in ritardo: i market maker delle monete piccole aggiornano le
quotazioni dopo BTC, gli arbitraggi fra monete costano. Quanto ritardo: minuti o ore? A 1 ora
il ritardo di minuti non si vede.

**Spiegazioni concorrenti.**

1. *Effetto casuale.* Smentita: `t` sopra soglia.
2. *Ritardo di minuti, non di ore* (l'aggiustamento finisce dentro l'ora). Previsione: R
   vicino alla (b). Smentita: R sopra.
3. *MASK si muove per conto suo* (notizie proprie). Previsione: nessun recupero. Smentita: recupero.
4. *È solo il mercato* (BTC continua a salire, MASK con lui). Previsione: l'effetto è il momento
   di BTC, e sparisce se BTC rientra nell'ora dopo. Si dichiara.
5. *Trend di fondo.* Smentita: batte la (b).
6. *Volatilità.* Smentita: batte la (b) con lo stesso stop.
7. *Artefatto dei dati* (barre di BTC e MASK non allineate, buchi diversi). Previsione: segnali
   vicino ai buchi. Smentita: allineamento per ts esatto e pochi buchi.
8. *Effetto costi* (4 ore, stop 2-3%: circa 0,1 R a giro). Smentita: regge a costi doppi.
9. *Pochi trade estremi.* Smentita: senza i 3 migliori resta sopra.
10. *Un solo anno.* Smentita: più della metà degli anni.
11. *Lookahead.* Smentita dal ritardo.

**Ipotesi completa.** MASKUSDT con BTCUSDT come riferimento, timeframe 1 ora (i dati sono a
barre: il ritardo più corto che si può provare con costi sopportabili).

* **I-08-L** long: rendimento BTC della barra > 2 deviazioni (168 barre di BTC) e rendimento
  MASK della barra < 0,5 × rendimento BTC. Stop 2 ATR(1h), nessun target, uscita dopo 4 barre.
* **I-08-S** short: rendimento BTC < -2 deviazioni e rendimento MASK > 0,5 × rendimento BTC
  (cioè è sceso meno della metà). Stessa uscita.
* **I-08-Lb** e **I-08-Sb** (aggiunte dopo che I-08-L e I-08-S sono state scartate per i trade
  minimi, 58 e 36 trade stimati, prima di qualunque test dell'idea; regola 6): soglia su BTC a
  1,5 deviazioni invece di 2, il resto uguale. Motivo: stessa idea, movimenti di BTC meno rari.
  Previsione per entrambe: R medio fra -0,15 e +0,05, non batte nettamente la (b).

---

## I-09 — Compressione delle bande e rottura

**Fonte.** John Bollinger, «Bollinger on Bollinger Bands», McGraw-Hill, 2001 (capitolo sulla
«compressione»: una larghezza delle bande al minimo precede un'espansione; la direzione la dà
la rottura della banda).

**Affermazione falsificabile.** Su MASKUSDT a 1 ora, quando la larghezza delle bande (4
deviazioni delle 20 barre divise per la media a 20) ha toccato nelle ultime 10 barre il proprio
20° percentile delle 500 barre precedenti e il close esce sopra la banda superiore, il long con
target a 2 volte lo stop ha R medio più alto di un long casuale con la stessa uscita;
simmetrico sotto la banda inferiore per lo short. Smentita: non batte nettamente la (b).

**Sotto-domande.** La calma precede davvero il movimento (volatilità che torna alla media) e
la direzione della prima rottura è quella giusta? Chi muove: ordini accumulati fuori
dall'intervallo stretto.

**Spiegazioni concorrenti.**

1. *Effetto casuale.* Smentita: `t` sopra soglia.
2. *Ritorno della volatilità senza direzione.* Previsione: movimento ampio ma direzione a caso,
   R vicino alla (b). Smentita: R sopra.
3. *Falsa rottura.* Previsione: molti stop. Smentita: R sopra la (b).
4. *È solo il mercato.* Smentita: effetto anche quando BTC non rompe.
5. *Trend di fondo.* Smentita: batte la (b).
6. *Stop stretto in fase calma* (ATR piccolo dopo la compressione: lo stop è stretto, i costi in
   R alti, e il tetto di leva riduce la dimensione). Previsione: molti trade ridotti, costi
   alti. Si dichiara.
7. *Artefatto dei dati.* Smentita: pochi segnali vicino ai buchi.
8. *Effetto costi.* Smentita: regge a costi doppi.
9. *Pochi trade estremi.* Smentita: senza i 3 migliori resta sopra.
10. *Un solo anno.* Smentita: più della metà degli anni.
11. *Lookahead.* Smentita dal ritardo.

**Ipotesi completa.** MASKUSDT, compressione e rottura, timeframe 1 ora.

* **I-09-L** long: compressione (come sopra) e close > media 20 + 2 deviazioni. Stop 2 ATR(1h),
  target 4 ATR (rapporto 2), uscita dopo 48 barre.
* **I-09-S** short: compressione e close < media 20 - 2 deviazioni. Stessa uscita.

---

## I-10 — Candela a martello sul minimo (e stella cadente sul massimo)

**Fonte.** Steve Nison, «Japanese Candlestick Charting Techniques», New York Institute of
Finance, 1991; Gunduz Caginalp, Henry Laurent, «The predictive power of price patterns»,
Applied Mathematical Finance 5(3-4), 1998 (le figure di inversione a candele hanno potere
predittivo sulle azioni dell'indice S&P 500).

**Affermazione falsificabile.** Su MASKUSDT a 1 ora, una barra con ombra inferiore almeno doppia
del corpo, ombra superiore non oltre un quarto dell'escursione della barra e minimo uguale al
minimo delle ultime 24 barre (barra compresa) è seguita da 12 ore con R medio long più alto di
un long casuale con la stessa uscita; la figura opposta sul massimo, per lo short. Smentita:
non batte nettamente la (b).

**Sotto-domande.** L'ombra lunga è il segno che i venditori sono stati assorbiti (liquidazioni
finite)? Vale di più dopo una discesa lunga? In quanto tempo: ore.

**Spiegazioni concorrenti.**

1. *Effetto casuale.* Smentita: `t` sopra soglia.
2. *È solo il ritorno dopo una barra estrema* (I-03). Previsione: l'effetto c'è solo quando la
   barra è anche estrema. Si dichiara se diventa candidato.
3. *È solo il mercato.* Smentita: effetto anche quando BTC non fa la stessa figura.
4. *Trend di fondo.* Smentita: batte la (b).
5. *Volatilità.* Smentita: batte la (b) con lo stesso stop.
6. *Rumore della figura* (a 1 ora le ombre lunghe sono frequenti e senza significato).
   Previsione: R uguale alla (b). Smentita: R sopra.
7. *Artefatto dei dati* (ombre false per errori nei file). Smentita: le barre dei segnali hanno
   ombre plausibili rispetto al mark.
8. *Effetto costi.* Smentita: regge a costi doppi.
9. *Pochi trade estremi.* Smentita: senza i 3 migliori resta sopra.
10. *Un solo anno.* Smentita: più della metà degli anni.
11. *Lookahead.* Smentita dal ritardo.

**Ipotesi completa.** MASKUSDT, martello e stella cadente, timeframe 1 ora.

* **I-10-L** long: martello al minimo delle 24 barre. Stop 2 ATR(1h), target 2 ATR (rapporto 1),
  uscita dopo 12 barre.
* **I-10-S** short: stella cadente (ombra superiore almeno doppia del corpo, ombra inferiore
  non oltre un quarto dell'escursione) al massimo delle 24 barre. Stessa uscita.

---

## I-11 — Rottura dell'intervallo d'apertura della giornata UTC

**Fonte.** Toby Crabel, «Day Trading with Short Term Price Patterns and Opening Range
Breakout», Traders Press, 1990: la rottura dell'intervallo dei primi minuti o della prima ora di
contrattazione indica la direzione della giornata.

**Affermazione falsificabile.** Su MASKUSDT a 1 ora, il primo close fra le 02:00 e le 12:00 UTC
fuori dall'intervallo (massimo e minimo) delle barre 00:00 e 01:00 UTC dà un ingresso nella
direzione della rottura con R medio, fino alla fine della giornata UTC, più alto di un ingresso
casuale nella stessa direzione con la stessa uscita. Smentita: non batte nettamente la (b).

**Sotto-domande.** Nelle crypto la giornata non ha un'apertura vera: la mezzanotte UTC è
l'apertura della candela giornaliera, su cui molti calcolano livelli e su cui si regola il
funding (00:00). La rottura viene dagli ordini dell'Asia (mattina) o da quelli europei? Una
rottura sola al giorno.

**Spiegazioni concorrenti.**

1. *Effetto casuale.* Smentita: `t` sopra soglia.
2. *Nessuna apertura vera* (l'intervallo delle 00-02 è un intervallo qualsiasi). Previsione: R
   uguale alla (b). Smentita: R sopra.
3. *È solo il mercato* (la direzione della giornata è quella di BTC). Smentita: effetto anche
   quando BTC va dall'altra parte.
4. *Falsa rottura.* Smentita: R sopra la (b).
5. *Trend di fondo.* Smentita: batte la (b).
6. *Volatilità.* Smentita: batte la (b) con lo stesso stop.
7. *Effetto costi* (stop di 1,5 ATR a 1 ora: circa 0,1 R a giro). Smentita: regge a costi doppi.
8. *Artefatto dei dati.* Smentita: giornate con buchi poche.
9. *Pochi trade estremi.* Smentita: senza i 3 migliori resta sopra.
10. *Un solo anno.* Smentita: più della metà degli anni.
11. *Funding alle 08:00 e 16:00* (il settlement dentro la giornata cambia il risultato). Si dichiara.

**Ipotesi completa.** MASKUSDT, intervallo d'apertura, timeframe 1 ora.

* **I-11-L** long: primo close della giornata (fra la barra delle 02:00 e quella delle 11:00
  comprese) sopra il massimo delle barre delle 00:00 e 01:00 UTC; un solo ingresso al giorno
  (il primo close fuori dall'intervallo, da qualunque lato: se il primo è sotto, la variante
  long quel giorno non entra). Stop 1,5 ATR(1h), nessun target, uscita alla chiusura della barra
  delle 23:00 UTC.
* **I-11-S** short: lo stesso con il primo close sotto il minimo.

---

## I-12 — Squilibrio degli ordini aggressivi

**Fonte.** Tarun Chordia, Avanidhar Subrahmanyam, «Order imbalance and individual stock returns:
Theory and evidence», Journal of Financial Economics 72(3), giugno 2004: lo squilibrio fra
acquisti e vendite aggressive predice il rendimento successivo nella stessa direzione (chi ha
informazione divide gli ordini nel tempo). Per le crypto: Nikolai Silantyev, «Order flow
analysis of cryptocurrency markets», Digital Finance 1, 2019.

**Affermazione falsificabile.** Su MASKUSDT a 1 ora, quando la quota del volume comprato da
ordini aggressivi (colonna `taker_buy_quote_volume` dei file Binance, divisa per
`quote_volume`) nelle ultime 3 barre è sopra il 90° percentile delle 500 barre precedenti, il
long tenuto 6 ore ha R medio più alto di un long casuale con la stessa uscita; sotto il 10°
percentile, lo short. Smentita: non batte nettamente la (b).

**Sotto-domande.** Lo squilibrio è informazione (continua) o pressione temporanea (rientra)?
Chi divide gli ordini su più ore. Quanto dura: ore.

**Spiegazioni concorrenti.**

1. *Effetto casuale.* Smentita: `t` sopra soglia.
2. *Pressione temporanea* (lo squilibrio sposta il prezzo e poi rientra). Previsione: R sotto la
   (b). Smentita: R sopra.
3. *È solo il prezzo passato* (lo squilibrio coincide con barre salite: è momento). Si dichiara
   se diventa candidato.
4. *È solo il mercato.* Smentita: effetto anche quando BTC non ha lo stesso squilibrio.
5. *Trend di fondo.* Smentita: batte la (b).
6. *Volatilità.* Smentita: batte la (b) con lo stesso stop.
7. *Artefatto dei dati* (la colonna può mancare o essere zero in alcuni file). Smentita:
   copertura della colonna dichiarata.
8. *Effetto costi.* Smentita: regge a costi doppi.
9. *Pochi trade estremi.* Smentita: senza i 3 migliori resta sopra.
10. *Un solo anno.* Smentita: più della metà degli anni.
11. *Lookahead.* Smentita dal ritardo.

**Ipotesi completa.** MASKUSDT, squilibrio degli ordini aggressivi, timeframe 1 ora.

* **I-12-L** long: quota comprata delle ultime 3 barre > 90° percentile delle 500 precedenti.
  Stop 2 ATR(1h), nessun target, uscita dopo 6 barre.
* **I-12-S** short: quota < 10° percentile. Stessa uscita.

---

## I-13 — Il trend del mercato trascina la moneta

**Fonte.** Yukun Liu, Aleh Tsyvinski, Xi Wu, «Common Risk Factors in Cryptocurrency», Journal of
Finance 77(2), aprile 2022: un fattore di mercato spiega gran parte dei rendimenti delle crypto,
e il momento del mercato si trasmette alle monete.

**Affermazione falsificabile.** Su MASKUSDT a 4 ore, quando BTC chiude sopra la sua media di 42
barre (7 giorni) e la pendenza della media è positiva (media di oggi sopra quella di 6 barre
prima), il long MASK tenuto 3 giorni ha R medio più alto di un long casuale con la stessa
uscita. Smentita: non batte nettamente la (b).

**Sotto-domande.** MASK reagisce al trend di BTC con un ritardo di giorni? O il trend del
mercato è già nel prezzo? Funziona solo nei rialzi forti.

**Spiegazioni concorrenti.**

1. *Effetto casuale.* Smentita: `t` sopra soglia.
2. *Il trend di BTC è già nel prezzo di MASK.* Previsione: R uguale alla (b). Smentita: R sopra.
3. *È il momento di MASK* (I-01). Si dichiara se diventa candidato.
4. *Trend di fondo di MASK.* Smentita: batte la (b).
5. *Inversione* (dopo una settimana di rialzo il mercato rientra). Previsione: R sotto la (b).
6. *Volatilità.* Smentita: batte la (b) con lo stesso stop.
7. *Artefatto dei dati* (barre di BTC mancanti). Smentita: allineamento esatto, barre mancanti contate.
8. *Pochi trade estremi.* Smentita: senza i 3 migliori resta sopra.
9. *Un solo anno.* Smentita: più della metà degli anni.
10. *Effetto costi.* Smentita: regge a costi doppi.
11. *Funding* (in rialzo il funding costa ai long). Si dichiara.

**Ipotesi completa.** MASKUSDT con BTCUSDT come riferimento, timeframe 4 ore.

* **I-13-L** long: BTC close > media 42 di BTC e media 42 di BTC > media 42 di BTC di 6 barre
  prima. Stop 2 ATR(4h) di MASK, nessun target, uscita dopo 18 barre. Solo long: la fonte parla
  del premio del mercato; lo short sarebbe un'idea diversa senza fonte propria.

---

## I-14 — Premio del contratto sul mark price

**Fonte.** Songrun He, Asaf Manela, Omri Ross, Victor von Wachter, «Fundamentals of Perpetual
Futures», arXiv 2212.06888, dicembre 2022: lo scarto fra il prezzo del perpetuo e quello a
pronti è ampio e tende a rientrare; il funding esiste per riportarlo a zero.

**Affermazione falsificabile.** Su MASKUSDT a 1 ora, quando lo scarto fra close del last e close
del mark ((last - mark) / mark) è sopra il 95° percentile delle 720 barre precedenti, lo short
tenuto 8 ore ha R medio più alto di uno short casuale con la stessa uscita; sotto il 5°
percentile, il long. Smentita: non batte nettamente la (b).

**Sotto-domande.** Lo scarto rientra muovendo il last (utile al trade) o il mark e l'indice (il
pronti che sale: inutile)? Il mark di Binance è già una media dell'indice e dello scarto: la
differenza col last è lo scarto di breve periodo.

**Spiegazioni concorrenti.**

1. *Effetto casuale.* Smentita: `t` sopra soglia.
2. *Rientra il pronti, non il perpetuo.* Previsione: R uguale alla (b). Smentita: R sopra.
3. *Lo scarto è momento* (i compratori del perpetuo anticipano il pronti). Previsione: R sotto la (b).
4. *Rumore di chiusura* (il close del mark e quello del last sono presi in istanti un po'
   diversi). Previsione: segnali a caso. Smentita: R sopra la (b).
5. *È solo il mercato.* Smentita: effetto anche senza movimento di BTC.
6. *Trend di fondo.* Smentita: batte la (b).
7. *Volatilità.* Smentita: batte la (b) con lo stesso stop.
8. *Artefatto dei dati* (buchi del mark). Smentita: barre tolte dichiarate e lontane dai segnali.
9. *Effetto costi.* Smentita: regge a costi doppi.
10. *Pochi trade estremi.* Smentita: senza i 3 migliori resta sopra.
11. *Un solo anno.* Smentita: più della metà degli anni.

**Ipotesi completa.** MASKUSDT, scarto last-mark, timeframe 1 ora.

* **I-14-S** short: scarto > 95° percentile delle 720 barre precedenti e > 0. Stop 2 ATR(1h),
  nessun target, uscita dopo 8 barre.
* **I-14-L** long: scarto < 5° percentile e < 0. Stessa uscita.

---

## I-15 — Momento intraday: la prima mezz'ora predice l'ultima

Scritta il 9 ottobre dopo i test delle idee I-01 … I-14 (nessun risultato di quelle idee entra
qui: è un meccanismo diverso, con la sua fonte, cercato perché le idee con fonte vanno usate prima
dei ritocchi, regola 6).

**Fonte.** Lei Gao, Yufeng Han, Sophia Zhengzi Li, Guofu Zhou, «Market Intraday Momentum»,
Journal of Financial Economics 129(2), agosto 2018: il rendimento della prima mezz'ora predice
quello dell'ultima mezz'ora della giornata. Per le crypto: Zhuzhu Wen, Elie Bouri, Yahua Xu,
Yang Zhao, «Intraday return predictability in the cryptocurrency markets: Momentum, reversal,
or both», North American Journal of Economics and Finance 62, 2022.

**Affermazione falsificabile.** Su MASKUSDT a 30 minuti, il segno del rendimento della barra
00:00-00:30 UTC predice il segno della barra 23:30-24:00 UTC dello stesso giorno: il trade nella
direzione del primo rendimento, tenuto solo l'ultima mezz'ora, ha R medio più alto di un
ingresso casuale nella stessa direzione con la stessa uscita (una barra). Smentita: non batte
nettamente la (b).

**Sotto-domande.** Nelle azioni il meccanismo è l'informazione della notte che arriva
all'apertura e il ribilanciamento di fine giornata; nelle crypto la «giornata» è convenzionale
(candela giornaliera UTC, settlement del funding a 00:00). Chi opera alle 23:30: chi chiude o
copre posizioni prima della candela giornaliera e del settlement.

**Spiegazioni concorrenti.**

1. *Effetto casuale.* Smentita: `t` sopra soglia.
2. *Nessuna giornata vera* (mezzanotte UTC è un istante qualsiasi). Previsione: R uguale alla (b). Smentita: R sopra.
3. *Effetto costi* (una sola barra da 30 minuti: il movimento tipico, circa 0,5-1%, è dello stesso
   ordine del costo di un giro, 0,2%; con stop di 2 ATR circa 0,08 R). Previsione: R medio vicino a
   -0,08. Smentita: R medio positivo e regge a costi doppi.
4. *È solo il mercato* (BTC fa lo stesso). Si dichiara.
5. *Settlement del funding a 00:00* (il trade si chiude esattamente al settlement: momento
   ambiguo, contato solo se costo). Previsione: piccolo costo in più. Si dichiara.
6. *Trend di fondo.* Smentita: batte la (b) nella stessa direzione.
7. *Volatilità.* Smentita: batte la (b) con lo stesso stop.
8. *Artefatto dei dati* (giornate con buchi). Smentita: poche giornate con buchi.
9. *Pochi trade estremi.* Smentita: senza i 3 migliori resta sopra.
10. *Un solo anno.* Smentita: più della metà degli anni.
11. *Lookahead.* Il segnale è noto alle 00:30, l'ingresso è alle 23:30: col ritardo di una barra
    il trade cade nella barra dopo, a cavallo della mezzanotte. Si dichiara.

**Ipotesi completa.** MASKUSDT, momento intraday, timeframe 30 minuti (la fonte lavora a mezz'ore).

* **I-15-L** long: alla chiusura della barra delle 23:00 UTC, se la barra delle 00:00 UTC dello
  stesso giorno ha chiuso sopra la sua apertura. Stop 2 ATR(30m), nessun target, uscita dopo 1
  barra. Previsione: R medio fra -0,15 e +0,02, non batte nettamente la (b).
* **I-15-S** short: lo stesso se la barra delle 00:00 ha chiuso sotto la sua apertura. Previsione
  uguale.

## Ritocchi (regola 6, dopo la nota MASKUSDT-N005: idee con fonte esaurite)

Ogni ritocco si sceglie con `codice/ordine_ritocchi.py` (prima della lista per `t` contro la (b))
e si scrive qui prima del test.

* **R-1, ritocco di MASKUSDT-006** (I-03-S, short dopo barra > +3 deviazioni; prima della lista
  con `t` 1,54). Cambia l'uscita: target da 1 a 2 volte lo stop (4 ATR) e uscita a tempo da 6 a
  12 barre. Motivo (Fase 3, nota MASKUSDT-N006): le 50 uscite a tempo a 6 ore hanno R medio
  +0,20, il rientro non è finito. Stessa entrata, stesso stop. Previsione: R medio fra -0,05 e
  +0,20; `t` contro la (b) fra 0,5 e 2; probabilmente non netto.
* **R-2, ritocco di MASKUSDT-028** (prima della lista con `t` 2,08; famiglia MASKUSDT-006, secondo
  ritocco). Aggiunge un filtro nato dai fallimenti (nota MASKUSDT-N007): nessun ingresso se
  l'ultimo funding regolato entro la chiusura della barra del segnale è negativo. Il resto come
  028. Previsione: circa 85 trade, R medio fra +0,05 e +0,35, `t` contro la (b) fra 1,5 e 3; può
  essere netto, ma il filtro è al limite del rumore e in validazione può sparire.
* **R-3, ritocco di MASKUSDT-028** (dopo 029, che è candidato e quindi fuori dalla lista: prima
  della lista è di nuovo 028 con `t` 2,08; famiglia MASKUSDT-006, terzo ritocco). Cambia solo
  l'uscita a tempo, da 12 a 24 barre. Motivo (nota MASKUSDT-N007): le 63 uscite a tempo a 12 barre
  hanno R medio +0,55. Nessun filtro del funding. Previsione: R medio fra 0 e +0,25, `t` contro la
  (b) fra 1 e 2,5. Se diventa candidato, in validazione va comunque un solo candidato della
  famiglia (quello con il `t` più alto).

## Previsioni (scritte dopo la Fase 0, prima del primo test)

Costi di un giro in R dalla Fase 0: circa 0,06 R a 1 ora con stop di 2 ATR, 0,07 R con 1,5 ATR,
0,04 R con 3 ATR; circa 0,03 R a 4 ore con 2 ATR, 0,02 R con 3 ATR; 0,02 R a 8 ore. Una entrata
casuale ha quindi R medio atteso di circa meno il costo (la (b) del controllo positivo a 1 ora con
uscita dopo una barra: -0,05 R). Il prior generale, da fonti costruite su altri mercati e su
orizzonti più lunghi, è che la maggior parte di queste regole NON batta nettamente la (b) su una
moneta sola con 70-300 trade: la potenza è bassa (sezione 11).

| Variante | R medio dopo i costi previsto | Batte nettamente la (b)? |
|---|---|---|
| I-01-L | da -0,15 a +0,10 | no |
| I-01-S | da -0,10 a +0,15 | no |
| I-02-L | da -0,15 a +0,05 | no |
| I-02-S | da -0,10 a +0,10 | no |
| I-03-L | da -0,10 a +0,10 | forse (il meccanismo delle liquidazioni è il più specifico ai futures) |
| I-03-S | da -0,15 a +0,05 | no |
| I-04-L | da -0,10 a +0,05 | no |
| I-04-S | da -0,10 a +0,05 | no |
| I-05-S | da -0,10 a +0,15 | no, ma è la fonte più recente e specifica alle crypto |
| I-05-L | da -0,15 a +0,15 | no |
| I-06-L | da -0,20 a +0,10 | no |
| I-07-S / I-07-Sb | da -0,15 a +0,15 | no |
| I-08-L | da -0,15 a +0,05 | no (a 1 ora il ritardo di minuti non si vede) |
| I-08-S | da -0,15 a +0,05 | no |
| I-09-L | da -0,15 a +0,10 | no |
| I-09-S | da -0,15 a +0,10 | no |
| I-10-L | da -0,15 a +0,05 | no |
| I-10-S | da -0,15 a +0,05 | no |
| I-11-L | da -0,15 a +0,05 | no |
| I-11-S | da -0,15 a +0,05 | no |
| I-12-L | da -0,15 a +0,05 | no |
| I-12-S | da -0,15 a +0,05 | no |
| I-13-L | da -0,15 a +0,10 | no |
| I-14-S | da -0,15 a +0,05 | no |
| I-14-L | da -0,15 a +0,05 | no |

Il criterio di successo è lo stesso per tutte (sezione 8, Fase 2): batte nettamente la (a) e la
(b) con `contro_baseline` e ha R medio dopo i costi positivo.

## Idee considerate e non registrate

* **Effetto del giorno della settimana o dell'ora** (Guglielmo Maria Caporale, Alex Plastun, «The
  day of the week effect in the cryptocurrency market», Finance Research Letters 31, 2019): non
  ha un meccanismo che dica la direzione su MASK; sarebbe una ricerca fra 7 giorni o 24 ore,
  cioè scegliere sui dati. Non registrata.
* **Nessuna idea viene da quello che si sa del 2024-2026** (regola 8).
