# LINKUSDT — ipotesi (Fase 1)

Scritte il 9 ottobre 2026, PRIMA di qualunque test di queste idee. Ogni idea ha la sua fonte
(pubblicata prima del 2024-01-01), l'affermazione falsificabile, le sotto-domande, almeno dieci
spiegazioni concorrenti con la previsione che fanno e cosa le smentirebbe, l'ipotesi completa e
tutte le sue varianti con il motivo. Il codice delle varianti è in `codice/varianti.py`; i numeri di
trade li dà `conta_trade` al momento della registrazione nel log.

## Regole comuni a tutte le varianti (fissate prima del primo test)

* Moneta LINKUSDT, perpetuo USDS-M. Segnali sul last, alla chiusura della barra; ingresso
  all'apertura della barra dopo; stop sul last; liquidazione sul mark (motore della sezione 7).
* Costi: commissione 0,05% per lato, slippage 0,02% per lato, funding storico. Dimensione: rischio
  1% del capitale per trade, leva massima 2, margine isolated (parametri.yaml).
* Stop in multipli dell'ATR di Wilder a 14 barre del timeframe della variante, calcolato alla barra
  del segnale e misurato dalla chiusura di quella barra. L'ATR è una misura di volatilità che si
  adatta alla moneta senza guardare risultati.
* Filtro della Fase 0: nessun ingresso su segnali di barre del gennaio 2020 (sotto la liquidità minima).
* Criterio di successo, uguale per tutte (sezione 8): battere nettamente la baseline (a) e la (b) in
  costruzione con R medio dopo i costi positivo.
* Costo di un giro in R (da `codice/costi.py`, ATR mediano in costruzione): stop 2 ATR → 0,082 R a
  15m, 0,058 a 30m, 0,040 a 1h, 0,020 a 4h, 0,014 a 8h, 0,007 a 1d; stop 3 ATR a 1d 0,005 R. Le
  previsioni sotto sono al netto di questi costi e del funding.
* Il bot rifiuta stop oltre il 6% (`stop_massimo_bot`): con l'ATR mediano, uno stop di 2 ATR supera
  il 6% dai 4h in su. Le varianti a 4h, 8h e 1d non sono eseguibili dal bot così come sono; si
  dichiara, e non cambia il test.

## Spiegazioni concorrenti comuni (si declinano per ogni idea)

Per non ripetere dieci volte lo stesso testo, le spiegazioni «noiose» hanno qui la forma generale; in
ogni idea c'è la previsione specifica e cosa la smentisce.

* **Caso**: l'R medio diverso da zero è rumore; previsione: `t` contro la (b) entro ±2, R medio per
  anno di segno variabile; smentita: `t` sopra la soglia e segno uguale in tutti gli anni.
* **Trend di fondo**: la variante guadagna solo perché va nella direzione del mercato del periodo
  (2020-2021 rialzo, 2022 ribasso); previsione: la (b) nella stessa direzione ha la stessa media;
  smentita: la variante batte la (b), che entra a caso nella stessa direzione.
* **È solo il mercato (BTC)**: l'effetto è il movimento comune delle crypto, LINK segue BTC;
  previsione: la stessa regola su BTCUSDT dà lo stesso segno e la differenza con la (b) di LINK sparisce
  se si guarda a BTC; smentita: l'effetto c'è su LINK al netto del caso e non su BTC, o il rendimento di
  BTC nei giorni dei trade non lo spiega.
* **Volatilità**: la condizione seleziona barre di volatilità diversa, e con stop in ATR il risultato
  in R cambia per la forma della distribuzione, non per la direzione; previsione: la (a) e la (b),
  che usano lo stesso stop, spiegano tutto; smentita: battere la (b).
* **Costi**: un vantaggio lordo esiste ma i costi lo mangiano; previsione: R medio lordo positivo e
  netto ≤ 0; smentita: R medio netto positivo anche a costi doppi.
* **Artefatto dei dati**: buchi del mark, barre tolte, funding mal attribuito producono il risultato;
  previsione: il risultato dipende da pochi trade vicino ai buchi; smentita: senza i 3 trade migliori
  e negli anni senza buchi il risultato resta.
* **Pochi trade estremi**: uno o due movimenti enormi (marzo 2020, maggio 2021) fanno la media;
  smentita: R medio senza i 3 migliori ancora sopra la (b).
* **Un solo regime**: l'effetto vive in un anno (es. il 2021) e sparisce negli altri; smentita: R
  medio sopra la (b) in più della metà degli anni.
* **Lookahead o errore di codice**: la variante legge per sbaglio la barra dopo; previsione: crollo
  col ritardo di una barra; smentita: peggioramento graduale (controllo positivo superato, voce N008).
* **Selezione della soglia**: la soglia scelta è quella a cui l'effetto appare per caso; smentita: la
  robustezza a ±20% (Fase 4).

---

## I-01 — Momentum nel tempo a una settimana

**Fonte.** Yukun Liu e Aleh Tsyvinski, «Risks and Returns of Cryptocurrency», NBER Working Paper 24877,
agosto 2018 (poi Review of Financial Studies, 2021): il rendimento della settimana passata delle
criptovalute principali prevede quello delle settimane successive (momentum nel tempo). Meccanismo
generale: Tobias Moskowitz, Yao Hua Ooi e Lasse Pedersen, «Time Series Momentum», Journal of
Financial Economics 104(2), 2012.

**Affermazione falsificabile.** Su LINKUSDT, dopo una settimana con rendimento positivo (negativo) il
rendimento dei 7 giorni successivi è più alto (più basso) di quello di 7 giorni presi a caso nella
stessa direzione, al netto dei costi.

**Sotto-domande.** Vale di più dopo settimane forti o anche dopo quelle appena positive (qui: basta
il segno)? Chi muove il prezzo: investitori che inseguono il rendimento recente e reagiscono in
ritardo all'informazione (sottoreazione). In quanto tempo: Liu e Tsyvinski trovano l'effetto su 1-4
settimane; qui si tiene 7 giorni.

**Spiegazioni concorrenti.**
1. Caso: `t` contro la (b) entro ±2.
2. Trend di fondo: con un 2021 molto rialzista il long dopo settimane positive è quasi sempre dentro;
   la (b) long lo cattura uguale. Smentita: battere la (b).
3. È solo il mercato: è il momentum di BTC; la stessa regola su BTC dà lo stesso risultato.
4. Volatilità: dopo settimane forti la volatilità è alta e lo stop in ATR largo; la (a) e la (b)
   hanno lo stesso stop. Smentita: battere la (b).
5. Costi: a 1d i costi sono 0,005 R per giro: non spiegano nulla in nessun senso.
6. Artefatto: le giornate senza mark spostano le chiusure di pochi trade; smentita: senza i 3 migliori.
7. Pochi trade estremi: due o tre rally del 2020-2021 fanno la media.
8. Un solo regime: vale nel 2021 e non nel 2022 (o il contrario per lo short).
9. Inversione mascherata: in crypto alle scadenze brevi si vede anche inversione (Zaremba e altri,
   2021, per le monete piccole); se domina, l'R medio è sotto la (b). Smentita: `t` positivo.
10. Selezione della finestra: 7 giorni sono una scelta della fonte, non dei dati; la robustezza (6 e
    8 giorni) la verifica.

**Ipotesi.** LINKUSDT, momentum nel tempo, timeframe 1d (il rendimento settimanale si misura su
candele giornaliere: è l'unità della fonte), posizione tenuta 7 barre, stop di protezione a 3 ATR(14)
(largo: la fonte non usa stop, lo stop serve solo a dare l'R e a proteggere).

**Varianti.**
* V01 — long se close(i)/close(i−7) − 1 > 0; esce dopo 7 barre. Motivo: la direzione principale della fonte.
* V02 — short se close(i)/close(i−7) − 1 < 0; esce dopo 7 barre. Motivo: la fonte è simmetrica (il momentum vale anche al ribasso).

---

## I-02 — Rottura del massimo (minimo) delle ultime 50 barre

**Fonte.** William Brock, Josef Lakonishok e Blake LeBaron, «Simple Technical Trading Rules and the
Stochastic Properties of Stock Returns», Journal of Finance 47(5), 1992: la regola di rottura
dell'intervallo (prezzo sopra il massimo delle ultime 50, 150 o 200 sedute) dà rendimenti nei 10
giorni dopo superiori a quelli incondizionati.

**Affermazione falsificabile.** Dopo una chiusura sopra il massimo delle 50 barre precedenti (sotto il
minimo), il rendimento delle 10 barre successive è più alto (più basso) di quello di 10 barre prese
a caso nella stessa direzione.

**Sotto-domande.** Chi compra la rottura: chi segue il trend, e chi aveva lo stop sopra il massimo
(ricoperture). Quando: subito dopo la rottura. Dimensione: tutte le rotture, senza filtro di volume.
Timeframe: la fonte usa sedute giornaliere; qui 4h, perché a 1d le rotture delle 50 barre in 1022
giorni sono troppo poche per 70 trade (stima a priori: un paio al mese al più) e la crypto scambia 24
ore su 24: 50 barre da 4 ore sono circa 8 giorni.

**Spiegazioni concorrenti.** 1 caso; 2 trend di fondo (le rotture al rialzo si concentrano nel 2021);
3 è solo il mercato (rotture di BTC nello stesso momento); 4 volatilità (le rotture avvengono quando
la volatilità sale, e lo stop in ATR ne tiene conto: la (b) no, perché entra in barre qualunque);
5 costi (0,02 R a 4h: piccoli); 6 artefatto (buchi del mark nei giorni di luglio 2021); 7 pochi trade
estremi; 8 un solo regime; 9 falsa rottura e ritorno (inversione: chi vende al massimo); previsione:
R medio sotto la (b); 10 selezione della finestra (50 è il valore più corto della fonte; la robustezza
prova 40 e 60). Per ognuna, la previsione e la smentita sono quelle della sezione comune; la 9 si
smentisce con `t` positivo.

**Ipotesi.** LINKUSDT, rottura dell'intervallo, 4h, posizione 10 barre, stop 2 ATR(14).

**Varianti.**
* V03 — long se close(i) > massimo degli high delle 50 barre prima di i; esce dopo 10 barre.
* V04 — short se close(i) < minimo dei low delle 50 barre prima di i; esce dopo 10 barre. Motivo: la
  fonte prova anche la rottura al ribasso (segnale di vendita).

---

## I-03 — Inversione dopo un movimento orario estremo (offerta di liquidità)

**Fonte.** Stefan Nagel, «Evaporating Liquidity», Review of Financial Studies 25(7), 2012: i rendimenti
dell'inversione a breve sono il compenso di chi offre liquidità, e crescono quando la volatilità è
alta; Bruce Lehmann, «Fads, Martingales, and Market Efficiency», Quarterly Journal of Economics 105(1),
1990.

**Affermazione falsificabile.** Dopo un'ora con rendimento sotto −3 deviazioni standard (calcolate sulle
168 ore prima), le 6 ore successive rendono più di 6 ore prese a caso nella direzione long (e
simmetricamente per lo short dopo +3 deviazioni).

**Sotto-domande.** Chi spinge il prezzo nell'ora estrema: vendite forzate (liquidazioni a cascata,
stop), chi ha fretta. Chi lo riporta indietro: chi offre liquidità. Dimensione: solo i movimenti
estremi (3 deviazioni). Tempo: ore; qui 6 ore. Notizie: un movimento da notizia non torna indietro
(spiegazione concorrente 9).

**Spiegazioni concorrenti.** 1 caso; 2 trend di fondo; 3 è solo il mercato (i crolli orari di LINK sono
quelli di BTC); 4 volatilità (dopo un'ora estrema la volatilità resta alta: lo stop in ATR si allarga
e l'R si comprime; la (b) entra anche in ore calme); 5 costi (0,04 R a 1h); 6 artefatto (barre vicino
ai buchi); 7 pochi trade estremi (marzo 2020); 8 un solo regime; 9 notizie: il movimento continua
(momentum orario), previsione R medio sotto la (b); 10 soglia scelta (3 deviazioni; robustezza 2,4 e 3,6).

**Ipotesi.** LINKUSDT, inversione dopo un'ora estrema, 1h, posizione 6 barre, stop 2 ATR(14).

**Varianti.**
* V05 — long se il rendimento dell'ora i è sotto −3 volte la deviazione standard dei rendimenti delle
  168 ore prima; esce dopo 6 barre.
* V06 — short se è sopra +3 volte; esce dopo 6 barre.

---

## I-04 — Momentum dentro la giornata: la prima mezz'ora prevede l'ultima

**Fonte.** Dehua Shen, Andrew Urquhart e Pengfei Wang, «Bitcoin intraday time-series momentum»,
Financial Review 57(2), 2022 (online 2021): il rendimento della prima mezz'ora prevede quello
dell'ultima mezz'ora della giornata di Bitcoin; Lei Gao, Yufeng Han, Sophia Zhengzi Li e Guofu Zhou,
«Market intraday momentum», Journal of Financial Economics 129(2), 2018.

**Affermazione falsificabile.** Se la mezz'ora 00:00-00:30 UTC chiude sopra la sua apertura, la
mezz'ora 23:30-24:00 UTC dello stesso giorno rende più di una mezz'ora presa a caso, long (e
simmetricamente short se chiude sotto).

**Sotto-domande.** La fonte definisce la «giornata» con il volume; qui la giornata è quella UTC, la
stessa delle candele giornaliere di Binance (scelta dichiarata, più semplice). Chi opera: chi
ribilancia a fine giornata e chi offre liquidità. Il costo di un giro a 30m (0,058 R) è grande rispetto
al movimento di una mezz'ora: la previsione tiene conto.

**Spiegazioni concorrenti.** 1 caso; 2 trend di fondo; 3 è solo il mercato (la stessa cosa su BTC: è la
fonte); 4 volatilità (le mezz'ore di fine giornata hanno volatilità diversa); 5 costi (0,058 R: un
vantaggio lordo piccolo sparisce); 6 artefatto (le giornate tolte cadono intere); 7 pochi trade
estremi; 8 un solo regime; 9 orario sbagliato: la giornata della fonte non è quella UTC, e l'effetto
non si trasferisce; 10 inversione di fine giornata.

**Ipotesi.** LINKUSDT, 30m, entra alla chiusura della mezz'ora 23:00-23:30 UTC, esce dopo 1 barra
(alle 00:00), stop 2 ATR(14).

**Varianti.**
* V07 — long se la mezz'ora 00:00-00:30 dello stesso giorno ha chiuso sopra l'apertura.
* V08 — short se ha chiuso sotto.

---

## I-05 — Effetto del giorno della settimana: il lunedì

**Fonte.** Guglielmo Maria Caporale e Alex Plastun, «The day of the week effect in the cryptocurrency
market», Finance Research Letters 31, 2019: rendimenti anomali (più alti) il lunedì per Bitcoin.

**Affermazione falsificabile.** Il rendimento del lunedì (UTC) di LINKUSDT è più alto di quello di un
giorno preso a caso, long.

**Sotto-domande.** Perché il lunedì: rientro dei flussi istituzionali e delle notizie del fine
settimana, volume basso nel weekend. Solo long (la fonte trova rendimenti più alti, non più bassi).

**Spiegazioni concorrenti.** 1 caso (52 lunedì l'anno: rumore grande); 2 trend di fondo; 3 è solo il
mercato (è l'effetto di BTC della fonte); 4 volatilità (il lunedì è più volatile: con stop in ATR l'R
cambia); 5 costi (trascurabili); 6 artefatto (giornate tolte); 7 pochi lunedì estremi; 8 un solo
regime (l'effetto della fonte è di anni precedenti); 9 è il fine settimana a essere diverso, non il
lunedì; 10 effetto pubblicato e quindi arbitrato via (previsione: assente).

**Ipotesi.** LINKUSDT, 1d, entra all'apertura del lunedì (segnale alla chiusura della domenica),
esce dopo 1 barra, stop 2 ATR(14).

**Varianti.** V09 — long il lunedì. Una sola variante: la fonte non dà una direzione short.

---

## I-06 — Funding estremo: posizioni affollate

**Fonte.** Maik Schmeling, Andreas Schrimpf e Karamfil Todorov, «Crypto carry», BIS Working Paper 1087,
aprile 2023: il carry dei futures crypto (che nei perpetui si vede nel funding) è molto variabile, nasce
dalla domanda con leva di chi insegue il trend e dalla scarsità di arbitraggio, e la leva alta dei
long affollati si associa a crolli violenti.

**Affermazione falsificabile.** Quando l'ultimo funding è sopra il 90° percentile dei 270 settlement
precedenti (90 giorni), le 24 ore successive rendono meno di 24 ore prese a caso (short); quando è sotto
il 10° percentile, rendono di più (long: short affollati che ricoprono).

**Sotto-domande.** Chi muove il prezzo: liquidazioni dei long con leva quando il prezzo scende un po';
arbitraggisti che vendono il perpetuo. Quando: nei giorni dopo. Soglia: percentile mobile, così si
adatta ai livelli di funding diversi degli anni (2021 molto più alto).

**Spiegazioni concorrenti.** 1 caso; 2 trend di fondo (il funding alto è nei rialzi: lo short perde con
il trend); 3 è solo il mercato (il funding di LINK segue quello di tutto il mercato); 4 volatilità;
5 costi e funding stesso (lo short incassa il funding alto: un piccolo guadagno che non è un vantaggio
di prezzo; previsione: R medio positivo ma vicino alla (b), che incassa lo stesso funding solo se entra
negli stessi momenti); 6 artefatto (settlement nei buchi); 7 pochi trade estremi; 8 un solo regime
(2021); 9 il funding alto segnala forza (momentum) e non affollamento: previsione R medio sotto la (b)
per lo short; 10 soglia (90° percentile; robustezza).

**Ipotesi.** LINKUSDT, 8h (il funding si paga ogni 8 ore: una barra per settlement), posizione 3 barre
(24 ore), stop 2 ATR(14). Il funding usato alla barra i è l'ultimo settlement con istante non oltre la
chiusura della barra i.

**Varianti.**
* V10 — short se l'ultimo funding è sopra il 90° percentile dei 270 settlement precedenti.
* V11 — long se è sotto il 10° percentile.

---

## I-07 — Premio dei volumi alti

**Fonte.** Simon Gervais, Ron Kaniel e Dan Mingelgrin, «The High-Volume Return Premium», Journal of
Finance 56(3), 2001: i titoli con volume insolitamente alto in un giorno (decile più alto della
finestra di 50 giorni) rendono di più nei giorni e nelle settimane dopo (più visibilità, più domanda).

**Affermazione falsificabile.** Dopo un giorno il cui volume in USDT è fra i 5 più alti delle ultime 50
giornate (quella compresa), i 10 giorni successivi rendono più di 10 giorni presi a caso, long.

**Sotto-domande.** Chi compra: chi scopre la moneta per la visibilità. Il segno del giorno ad alto
volume non entra (nella fonte il premio vale per i giorni con rendimento piccolo; qui non si filtra:
spiegazione 9). Durata: la fonte trova il premio da 10 a 100 giorni; qui 10.

**Spiegazioni concorrenti.** 1 caso; 2 trend di fondo (volumi alti nei rialzi del 2021); 3 è solo il
mercato; 4 volatilità (volumi alti con volatilità alta, stop larghi); 5 costi (trascurabili a 1d); 6
artefatto (giornate tolte); 7 pochi trade estremi; 8 un solo regime; 9 i volumi alti sono crolli
(capitolazione) e il segno conta: previsione risultato diverso fra giorni rossi e verdi; 10 soglia.

**Ipotesi.** LINKUSDT, 1d, posizione 10 barre, stop 3 ATR(14).

**Varianti.** V12 — long se il volume in USDT della barra i è fra i 5 più alti delle 50 barre
terminanti in i. Una sola variante: la fonte parla di premio (long).

---

## I-08 — Squilibrio degli ordini aggressivi

**Fonte.** Tarun Chordia e Avanidhar Subrahmanyam, «Order imbalance and individual stock returns:
Theory and evidence», Journal of Financial Economics 72(3), 2004: lo squilibrio fra acquisti e vendite
aggressivi prevede positivamente il rendimento del periodo dopo (chi divide gli ordini continua a
comprare).

**Affermazione falsificabile.** Dopo un'ora in cui la quota di acquisti aggressivi (volume taker buy in
USDT diviso il volume in USDT) è sopra il 95° percentile delle 720 ore precedenti, le 4 ore successive
rendono più di 4 ore a caso, long; e simmetricamente sotto il 5° percentile, short.

**Sotto-domande.** Chi: grandi ordini spezzati in pezzi, che continuano nelle ore dopo. Quanto dura: la
fonte trova l'effetto sul giorno dopo; qui 4 ore, perché in crypto lo stesso meccanismo è più rapido
(scelta dichiarata). Dato: colonna taker_buy_quote_volume dei file klines.

**Spiegazioni concorrenti.** 1 caso; 2 trend di fondo; 3 è solo il mercato (lo squilibrio di LINK segue
quello di BTC); 4 volatilità; 5 costi (0,04 R); 6 artefatto (il dato taker può mancare o essere diverso
nel 2020); 7 pochi trade estremi; 8 un solo regime; 9 l'acquisto aggressivo esaurisce la domanda e il
prezzo torna indietro (inversione); 10 soglia (95°).

**Ipotesi.** LINKUSDT, 1h, posizione 4 barre, stop 2 ATR(14).

**Varianti.**
* V13 — long se la quota di acquisti aggressivi dell'ora i è sopra il 95° percentile delle 720 ore prima.
* V14 — short se è sotto il 5° percentile.

---

## I-09 — Rottura di volatilità dall'apertura del giorno

**Fonte.** Larry Williams, «Long-Term Secrets to Short-Term Trading», Wiley, 1999: comprare quando il
prezzo sale oltre l'apertura del giorno di una frazione dell'escursione del giorno prima (rottura di
volatilità); Toby Crabel, «Day Trading with Short Term Price Patterns and Opening Range Breakout», 1990.

**Affermazione falsificabile.** La prima ora del giorno UTC in cui il prezzo chiude sopra apertura del
giorno + 0,5 × (massimo − minimo del giorno prima) è seguita, fino alla fine del giorno, da un
rendimento più alto di quello di ore prese a caso, long (simmetrico short).

**Sotto-domande.** Chi: chi segue il movimento e chi è costretto a ricoprire. Quando: lo stesso giorno.
Una sola entrata al giorno per direzione (la prima ora che supera la soglia). L'uscita è alla fine
del giorno UTC (apertura delle 00:00), come nella fonte (si esce alla chiusura della seduta).

**Spiegazioni concorrenti.** 1 caso; 2 trend di fondo; 3 è solo il mercato; 4 volatilità (le giornate
con rottura sono volatili); 5 costi (0,04 R); 6 artefatto (giornate tolte); 7 pochi trade estremi;
8 un solo regime; 9 falsa rottura (inversione intraday); 10 coefficiente 0,5 (robustezza 0,4 e 0,6).

**Ipotesi.** LINKUSDT, 1h, uscita a fine giornata UTC, stop 2 ATR(14).

**Varianti.**
* V15 — long alla prima chiusura oraria del giorno sopra apertura del giorno + 0,5 × escursione di ieri,
  se la barra non è l'ultima del giorno.
* V16 — short alla prima chiusura sotto apertura − 0,5 × escursione di ieri, stesse condizioni.

---

## I-10 — Ritracciamento in un trend: RSI a 2 periodi

**Fonte.** Larry Connors e Cesar Alvarez, «Short Term Trading Strategies That Work», TradingMarkets, 2008:
comprare quando il prezzo è sopra la media a 200 periodi e l'RSI a 2 periodi è sotto 10; uscire alla
prima chiusura sopra la media a 5 periodi.

**Affermazione falsificabile.** In un trend rialzista (chiusura sopra la media a 200), un eccesso di
ribasso di brevissimo periodo (RSI(2) < 10) è seguito da un rimbalzo: il trade fino alla chiusura
sopra la media a 5 rende più di un ingresso a caso con la stessa uscita.

**Sotto-domande.** Chi: chi compra le correzioni nel trend; vendite eccessive di breve. Durata: pochi
periodi. La fonte non usa stop: qui uno stop di protezione a 3 ATR(14) e un'uscita di sicurezza dopo 20
barre (scelte dichiarate, per dare un R e non tenere posizioni senza fine).

**Spiegazioni concorrenti.** 1 caso; 2 trend di fondo (il filtro della media a 200 seleziona il 2021);
3 è solo il mercato; 4 volatilità; 5 costi; 6 artefatto; 7 pochi trade estremi; 8 un solo regime;
9 la correzione continua (momentum di breve); 10 soglie (10 e 200; robustezza).

**Ipotesi.** LINKUSDT, long. La fonte lavora su sedute giornaliere: V17 a 1d; a 1d però con 200 barre di
riscaldamento i segnali in costruzione possono essere sotto 70, quindi V18 è la stessa regola a 4h
(scritta ora, prima di contare i trade di V17: una seconda scala dello stesso meccanismo, non
un allentamento dopo uno scarto).

**Varianti.**
* V17 — 1d: long se close > media semplice a 200 e RSI(2) < 10; esce alla prima chiusura sopra la
  media a 5 o dopo 20 barre; stop 3 ATR(14).
* V18 — 4h: stessa regola, in barre da 4 ore.

---

## I-11 — Numeri tondi e stop raggruppati

**Fonte.** Carol Osler, «Currency Orders and Exchange Rate Dynamics: An Explanation for the Predictive
Success of Technical Analysis», Journal of Finance 58(5), 2003: gli ordini stop si raggruppano appena
oltre i numeri tondi; quando il prezzo li attraversa, gli stop scattano e il movimento accelera nella
stessa direzione.

**Affermazione falsificabile.** Dopo una chiusura oraria che attraversa al rialzo un numero tondo (dalla
chiusura precedente sotto a quella attuale sopra o uguale), le 4 ore dopo rendono più di 4 ore a caso,
long; simmetrico short per gli attraversamenti al ribasso.

**Sotto-domande.** Numero tondo: multiplo di metà della potenza di 10 sotto il prezzo (prezzo fra 1 e 10:
multipli di 0,5; fra 10 e 100: multipli di 5), scelto prima dei dati. Chi: gli stop di chi aveva
venduto (sopra) o comprato (sotto). Tempo: ore.

**Spiegazioni concorrenti.** 1 caso; 2 trend di fondo; 3 è solo il mercato; 4 volatilità; 5 costi
(0,04 R); 6 artefatto; 7 pochi trade estremi; 8 un solo regime; 9 i numeri tondi sono anche dove si
mettono i take profit: il prezzo rimbalza (inversione, l'altra metà di Osler); 10 scelta del passo dei
numeri tondi.

**Ipotesi.** LINKUSDT, 1h, posizione 4 barre, stop 2 ATR(14).

**Varianti.**
* V19 — long dopo un attraversamento al rialzo di un numero tondo.
* V20 — short dopo un attraversamento al ribasso.

---

## I-12 — Vicinanza al massimo dell'anno

**Fonte.** Thomas George e Chuan-Yang Hwang, «The 52-Week High and Momentum Investing», Journal of
Finance 59(5), 2004: chi ancora le aspettative al massimo dell'anno reagisce in ritardo quando il prezzo
gli si avvicina o lo supera; i titoli vicini al massimo dell'anno continuano a salire.

**Affermazione falsificabile.** Dopo una chiusura giornaliera sopra il massimo dei 365 giorni precedenti,
i 20 giorni dopo rendono più di 20 giorni a caso, long.

**Spiegazioni concorrenti.** 1 caso; 2 trend di fondo (2021); 3 è solo il mercato; 4 volatilità; 5 costi;
6 artefatto; 7 pochi trade estremi; 8 un solo regime; 9 esaurimento al massimo (inversione); 10 finestra
(un anno: quella della fonte).

**Ipotesi.** LINKUSDT, 1d, long, posizione 20 barre, stop 3 ATR(14). Con 365 giorni di riscaldamento e
dati dal 2020-01-17 i segnali in costruzione partono dal 2021: è probabile che resti sotto 70 trade
(scarto), e non si allenta.

**Varianti.** V21 — long se close(i) > massimo degli high delle 365 barre prima; esce dopo 20 barre.

---

## I-13 — Momentum giornaliero delle monete grandi

**Fonte.** Adam Zaremba, Mehmet Huseyin Bilgin, Huaigang Long, Aleksander Mercik e Jan Szczygielski, «Up or
down? Short-term reversal, momentum, and liquidity effects in cryptocurrency markets», International
Review of Financial Analysis 78, 2021: nelle crypto il rendimento di ieri prevede quello di oggi; per la
massa delle monete è inversione (illiquidità), per le monete più grandi e scambiate è momentum.

**Affermazione falsificabile.** LINK è fra le monete grandi e liquide (220-540 milioni di USDT al giorno
negli anni di costruzione): dopo un giorno positivo il giorno dopo rende più di un giorno a caso, long; dopo un
giorno negativo rende meno, short.

**Spiegazioni concorrenti.** 1 caso; 2 trend di fondo; 3 è solo il mercato (momentum giornaliero di
BTC); 4 volatilità; 5 costi (0,007 R); 6 artefatto; 7 pochi trade estremi; 8 un solo regime; 9 per LINK
domina l'inversione (la moneta non è abbastanza grande): R medio sotto la (b); 10 soglia zero (nessuna:
basta il segno).

**Ipotesi.** LINKUSDT, 1d, posizione 1 barra, stop 2 ATR(14).

**Varianti.**
* V22 — long se il rendimento della barra i (close/close precedente − 1) è positivo.
* V23 — short se è negativo.

---

# Seconda tornata di idee (scritta il 9 ottobre 2026 alle 15:00 UTC, dopo V01-V23, prima dei loro test)

**Dichiarazione.** Le idee I-14 e I-15 sono nate dallo studio dei fallimenti (voce N009 del log):
I-13 (momentum giornaliero) e I-03 (inversione dopo un'ora estrema) hanno perso contro il caso in
modo sistematico. Sono idee nuove con una fonte propria, come chiede la Fase 3, ma la scelta di
provarle è stata guidata dai risultati di costruzione: il rischio di aver trovato rumore è più alto
che per le prime tredici, e lo dice anche la validazione, che giudica una volta sola. I-16 e I-17
non vengono dai risultati.

## I-14 — Inversione giornaliera

**Fonte.** Adam Kozlowski, Michael Puleo e Jian Zhou, «Cryptocurrency return reversals», Applied
Economics Letters 28(11), 2021 (online 2020): fra 200 criptovalute il rendimento passato si inverte a
frequenza giornaliera, settimanale e mensile; l'effetto è il compenso di chi offre liquidità ed è più
forte nelle monete meno liquide.

**Affermazione falsificabile.** Dopo un giorno UTC negativo il giorno dopo rende più di un giorno a caso,
long; dopo un giorno positivo rende meno, short.

**Sotto-domande.** Chi: chi offre liquidità a chi ha venduto (comprato) con fretta; chi prende profitto.
Quando: il giorno dopo. Dimensione: tutti i giorni, solo il segno (la fonte ordina per rendimento,
qui la moneta è una sola).

**Spiegazioni concorrenti.** 1 caso (319-352 trade: il rumore è piccolo, ma la scelta di provarla viene
dai risultati: è il rischio principale); 2 trend di fondo; 3 è solo il mercato (inversione giornaliera di
BTC); 4 volatilità (i giorni dopo un ribasso sono più volatili: lo stop in ATR si allarga); 5 costi
(0,007 R); 6 artefatto; 7 pochi trade estremi (marzo 2020); 8 un solo regime; 9 rimbalzo dopo i soli
crolli grandi (la media la fanno pochi giorni); 10 è il rovescio di V22 e V23: se il loro risultato è
rumore, questa variante lo rispecchia e la validazione lo scopre.

**Ipotesi.** LINKUSDT, 1d, posizione 1 barra, stop 2 ATR(14).

**Varianti.**
* V24 — long se il rendimento della barra i è negativo.
* V25 — short se è positivo.

## I-15 — Continuazione dopo un'ora anomala fino alla fine del giorno

**Fonti.** Guglielmo Maria Caporale e Alex Plastun, «Momentum effects in the cryptocurrency market after
one-day abnormal returns», CESifo Working Paper 7917, 2019 (poi Financial Markets and Portfolio
Management 34, 2020): nei giorni con rendimento anomalo il prezzo continua nella direzione del movimento
fino alla fine del giorno. Danial Saef, Odett Nagy, Sergej Sizov e Wolfgang Karl Härdle, «Understanding
jumps in high frequency digital asset markets», arXiv 2110.09429, 18 ottobre 2021: un salto positivo durante il giorno rende
probabile un rendimento positivo a fine giornata, e viceversa; nessun effetto sul giorno dopo.

**Affermazione falsificabile.** Dopo un'ora con rendimento oltre 3 deviazioni standard delle 168 ore
prima, la posizione nella direzione del movimento tenuta fino alla fine del giorno UTC rende più di
ingressi a caso con la stessa uscita.

**Sotto-domande.** Chi: liquidazioni a cascata e stop che scattano, chi insegue il movimento. Quando:
lo stesso giorno (le fonti dicono fino a fine giornata, non oltre). L'ora anomala si misura come in
I-03 (stesso indicatore già scritto prima dei risultati); non si entra se l'ora anomala è l'ultima del
giorno.

**Spiegazioni concorrenti.** 1 caso; 2 trend di fondo; 3 è solo il mercato (le ore anomale di LINK sono
quelle di BTC, ed è BTC a continuare); 4 volatilità; 5 costi (0,04 R); 6 artefatto (ore vicine ai
buchi); 7 pochi trade estremi; 8 un solo regime; 9 è lo specchio di V05 e V06: con un'uscita diversa
(fine giornata invece di 6 ore) può non valere; 10 la soglia 3 è presa da I-03 e non è ottimizzata.

**Ipotesi.** LINKUSDT, 1h, uscita a fine giorno UTC, stop 2 ATR(14).

**Varianti.**
* V26 — long dopo un'ora sopra +3 deviazioni standard.
* V27 — short dopo un'ora sotto −3 deviazioni standard.

## I-16 — Periodicità oraria: la stessa ora dei giorni precedenti

**Fonte.** Steven Heston, Robert Korajczyk e Ronnie Sadka, «Intraday Patterns in the Cross-Section of
Stock Returns», Journal of Finance 65(4), 2010: il rendimento di una mezz'ora è correlato positivamente
con quello della stessa mezz'ora dei giorni precedenti, per molte settimane (flussi ricorrenti a ore
fisse).

**Affermazione falsificabile.** Se la media dei rendimenti della prossima ora (stessa ora UTC) nei 20 giorni
precedenti è positiva, quell'ora rende più di un'ora a caso, long; se negativa, meno, short.

**Sotto-domande.** Chi: flussi ricorrenti (ribilanciamenti, fixing, orari di borse e sessioni, funding
alle 00, 08, 16 UTC). La fonte è sulle azioni e trasversale; qui una sola moneta nel tempo. Con un'ora di
posizione il costo (0,04 R) è grande rispetto all'effetto atteso, che nella fonte è di pochi punti base.

**Spiegazioni concorrenti.** 1 caso; 2 trend di fondo; 3 è solo il mercato; 4 volatilità (ore diverse,
volatilità diverse); 5 costi (l'effetto è minuscolo: previsione R medio negativo); 6 artefatto; 7 pochi
trade estremi; 8 un solo regime; 9 i flussi a ore fisse sono quelli del funding (ore 00, 08, 16), e
l'effetto vive solo lì; 10 finestra di 20 giorni (robustezza 16 e 24).

**Ipotesi.** LINKUSDT, 1h, posizione 1 barra, stop 2 ATR(14).

**Varianti.**
* V28 — long se la media dei 20 rendimenti della stessa ora nei 20 giorni precedenti è positiva.
* V29 — short se è negativa.

## I-17 — Compressione della volatilità e rottura (la «stretta» delle bande)

**Fonte.** John Bollinger, «Bollinger on Bollinger Bands», McGraw-Hill, 2001: a una fase di volatilità
minima (bande strette) segue un'espansione; la direzione si prende dalla rottura della banda.

**Affermazione falsificabile.** Se nelle ultime 5 ore l'ampiezza delle bande (20 ore, 2 deviazioni) ha
toccato il minimo delle 120 ore precedenti e ora la chiusura esce sopra la banda alta, le 12 ore
dopo rendono più di 12 ore a caso, long (simmetrico sotto la banda bassa, short).

**Spiegazioni concorrenti.** 1 caso; 2 trend di fondo; 3 è solo il mercato; 4 volatilità (dopo la stretta
la volatilità sale per costruzione: lo stop in ATR è stretto all'ingresso e l'R si gonfia o si sgonfia);
5 costi (0,04 R); 6 artefatto; 7 pochi trade estremi; 8 un solo regime; 9 falsa rottura; 10 soglie
(20, 2, 120, 5).

**Ipotesi.** LINKUSDT, 1h, posizione 12 barre, stop 2 ATR(14).

**Varianti.**
* V30 — long alla rottura della banda alta dopo una stretta.
* V31 — short alla rottura della banda bassa dopo una stretta.

Se una variante di queste quattro idee resta sotto i 70 trade non consuma budget; il budget rimasto
dopo le idee nuove va ai ritocchi nell'ordine della regola 6.
