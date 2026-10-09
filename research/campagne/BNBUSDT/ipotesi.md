# BNBUSDT — ipotesi (Fase 1)

Scritto il 9 ottobre 2026, prima di qualunque conteggio o test delle idee qui sotto. Ogni idea ha
la sua fonte (pubblicata prima del 2024-01-01), l'affermazione verificabile, le sotto-domande,
almeno 10 spiegazioni concorrenti con la previsione e cosa le smentirebbe, l'ipotesi completa e
tutte le sue varianti con il motivo. Il codice di ogni variante è in `codice/varianti.py`
(funzione indicata). Nessuna idea viene da risultati del gate, del registro, del paper o di altre
monete, né da ciò che so dei mercati dopo il 2023 (regola 8).

## Regole comuni a tutte le varianti

* Serie dei segnali: last price; stop sulla serie last; liquidazione sul mark (sezione 7).
* Ingresso all'apertura della barra dopo il segnale; una posizione alla volta.
* Stop: k volte l'ATR di Wilder (14 barre salvo dove indicato) sotto (long) o sopra (short) la
  chiusura della barra di segnale; nessun target salvo dove indicato. L'ATR è la misura di
  volatilità più comune nella letteratura dei sistemi di trading (Wilder 1978) e rende lo stop
  comparabile fra timeframe.
* Nessun ingresso su segnali di barre di maggio e giugno 2020 (sotto la liquidità minima,
  `fase0_dati.md`).
* Costi: commissione 0,05% e slippage 0,02% per lato, cioè 0,14% del nozionale per giro. In R è
  0,0014 / distanza dello stop. Distanze tipiche di 2 ATR su BNBUSDT (stima a occhio dalla
  letteratura sulla volatilità crypto, da verificare nei risultati): a 30m circa 1% (costo circa
  0,14 R), a 1h circa 1,5-2% (0,07-0,09 R), a 4h circa 3-4% (circa 0,04 R), a 8h circa 4-5%
  (circa 0,03 R), a 1d circa 8-12% (circa 0,015 R). Le previsioni sono al netto di questi costi.
* Il tetto di stop del bot è il 6% (`stop_massimo_bot`): le varianti giornaliere con stop a
  2 ATR lo superano quasi sempre. Il bot non può eseguirle così come sono: si dichiara in
  consegna se diventano candidati.
* La spiegazione concorrente «è solo il mercato» si controlla con la correlazione fra l'R dei
  trade e il rendimento di BTCUSDT nella stessa finestra (`comune.confronto_btc`), accanto a ogni
  risultato; le altre con la (a), la (b), l'R per anno e senza i 3 trade migliori.

---

## I-01 — Momentum a serie temporale settimanale

**Fonte.** Tobias J. Moskowitz, Yao Hua Ooi, Lasse Heje Pedersen, «Time Series Momentum»,
Journal of Financial Economics 104(2), maggio 2012. Per le crypto: Yukun Liu, Aleh Tsyvinski,
«Risks and Returns of Cryptocurrency», NBER Working Paper 24877, agosto 2018 (poi Review of
Financial Studies 34(6), 2021): il rendimento della settimana passata predice quello delle
settimane successive.

**Affermazione verificabile.** Su BNBUSDT, dopo 7 giorni con rendimento positivo, il rendimento
dei 7 giorni successivi, in R, è più alto di quello di un ingresso a caso con la stessa uscita;
simmetricamente per lo short dopo 7 giorni negativi.

**Sotto-domande.** Vale più nei periodi di forte tendenza (2021) che nei laterali? Dipende dalla
dimensione del movimento passato? Chi compra dopo una settimana di salita: investitori piccoli che
inseguono la tendenza (Liu e Tsyvinski parlano di attenzione degli investitori), che arrivano con
ritardo. L'effetto, se c'è, si manifesta su giorni o settimane.

**Spiegazioni concorrenti.**

| # | Spiegazione | Previsione | Cosa la smentisce |
|---|---|---|---|
| 1 | Effetto casuale | t contro la (b) vicino a 0 | t contro la (b) oltre la soglia |
| 2 | Trend di fondo della moneta (2020-2021 in forte salita) | il long batte la (b) solo nel 2020-2021, non nel 2022 | R sopra la (b) anche nel 2022 |
| 3 | È solo il mercato (BNB segue BTC) | R del trade molto correlato al rendimento di BTC nella finestra, e lo stesso vale per la (b) | correlazione bassa o vantaggio presente anche a parità di BTC |
| 4 | Volatilità: dopo settimane di salita la volatilità cambia e cambia la distanza dello stop | costi in R diversi fra candidato e (b) spiegano la differenza | differenza di R lordo, non solo di costi |
| 5 | Pochi trade estremi (rally del 2021) | senza i 3 migliori l'R scende sotto la (b) | R senza i 3 migliori ancora sopra la (b) |
| 6 | Artefatto dei dati (buchi del mark, giorni tolti) | risultati diversi attorno ai giorni tolti | nessun trade in quei giorni pesa |
| 7 | Effetto costi: con stop larghi i costi in R sono piccoli per tutti | nessuna differenza dalla (b), entrambe vicine al lordo | — (non spiega un vantaggio, lo rende solo più facile) |
| 8 | Inversione invece di continuazione (eccesso di reazione) | R sotto la (b) | R sopra la (b) |
| 9 | Funding: chi è long dopo una salita paga funding alto | il funding medio in R mangia il vantaggio lordo | funding piccolo rispetto alla differenza |
| 10 | Dipendenza dalla finestra di 7 giorni scelta (data mining dell'orizzonte) | vantaggio che sparisce sui timeframe vicini | vantaggio stabile alla verifica dei timeframe adiacenti |

**Ipotesi.** BNBUSDT, momentum a serie temporale, timeframe 1d (il meccanismo è settimanale e
1d è il timeframe ammesso più lungo che lo misura), posizioni di 7 giorni.

**Varianti.**
* `I-01-L` (`varianti.i01("long")`): alla chiusura giornaliera, se close / close di 7 giorni prima
  − 1 > 0, long; uscita all'apertura dopo 7 barre in posizione; stop 2 ATR(14). Motivo: la
  direzione principale della fonte.
* `I-01-S` (`varianti.i01("short")`): stessa regola con rendimento < 0, short. Motivo: la fonte è
  simmetrica (momentum a serie temporale long e short).

Previsione (al netto di costi di circa 0,015 R): R medio fra −0,05 e +0,10 per il long, fra
−0,10 e +0,05 per lo short; nessuna delle due batte nettamente la (b) (la potenza con circa 70-90
trade è bassa).

---

## I-02 — Rottura del canale di Donchian

**Fonte.** Curtis M. Faith, «Way of the Turtle», McGraw-Hill, 2007 (il sistema 1 delle
tartarughe: ingresso sulla rottura del massimo di 20 periodi, uscita sulla rottura opposta di 10
periodi, stop a 2 volte la volatilità media). Le regole risalgono a Richard Donchian.

**Affermazione verificabile.** Su BNBUSDT a 4h, un ingresso long quando la chiusura supera il
massimo delle 20 barre precedenti, con uscita sulla rottura del minimo di 10 barre, ha R medio
più alto di un ingresso casuale con la stessa uscita e lo stesso stop (e simmetrico per lo short).

**Sotto-domande.** Vale nei periodi di volatilità che cresce? Le rotture false sono più frequenti
nei laterali? Chi opera: chi segue la tendenza e chi ha stop sopra i massimi, la cui esecuzione
spinge il prezzo oltre il livello. In quanto tempo: i trade vincenti durano giorni, i perdenti
poche barre.

**Spiegazioni concorrenti.**

| # | Spiegazione | Previsione | Cosa la smentisce |
|---|---|---|---|
| 1 | Effetto casuale | t contro la (b) vicino a 0 | t oltre la soglia |
| 2 | Trend di fondo 2020-2021 | il long vince solo nel 2020-2021 | R sopra la (b) anche nel 2022 |
| 3 | È solo il mercato | R molto correlato a BTC nella finestra | vantaggio anche dove BTC è fermo |
| 4 | Volatilità: le rotture avvengono con volatilità in aumento, lo stop calcolato con l'ATR passato è stretto | molti stop rapidi, R medio negativo | stop rapidi pochi |
| 5 | Pochi trade estremi (code grasse delle tendenze) | senza i 3 migliori R sotto la (b) | R senza i 3 migliori sopra la (b) |
| 6 | Artefatto dei dati | — | nessun trade nei giorni tolti decide il risultato |
| 7 | Effetto costi (molte rotture false brevi) | costi medi in R alti, R netto negativo | costi in R piccoli rispetto alla differenza |
| 8 | Inversione dopo la rottura (falsa rottura, caccia agli stop) | R sotto la (b) | R sopra la (b) |
| 9 | La (b) entra con la stessa uscita di Donchian: la differenza la fa solo il momento d'ingresso | t piccolo anche se l'R è positivo | t alto |
| 10 | Sovrapposizione col momentum settimanale (I-01): stessa informazione | risultati simili a I-01 | risultati diversi |

**Ipotesi.** BNBUSDT, rottura del canale, 4h (20 barre = poco più di 3 giorni: la versione 1d
darebbe pochi trade in 2,7 anni e la crypto si muove 24 ore su 24; scelto prima di contare),
direzione long e short separate.

**Varianti.**
* `I-02-L` (`varianti.i02("long")`): close > massimo degli high delle 20 barre precedenti → long;
  uscita quando close < minimo dei low delle 10 barre precedenti; stop 2 ATR(20).
* `I-02-S` (`varianti.i02("short")`): close < minimo delle 20 precedenti → short; uscita quando
  close > massimo delle 10 precedenti; stop 2 ATR(20).

Previsione (costi circa 0,04 R): R medio fra −0,10 e +0,10; nessuna batte nettamente la (b).

---

## I-03 — RSI a 2 periodi in tendenza rialzista

**Fonte.** Larry Connors, Cesar Alvarez, «Short Term Trading Strategies That Work», TradingMarkets
Publishing, 2008: comprare quando il prezzo è sopra la media a 200 periodi e l'RSI a 2 periodi è
sotto 5 (o 10), uscire quando la chiusura supera la media a 5.

**Affermazione verificabile.** Su BNBUSDT, in tendenza (close > media a 200), un ribasso brusco di
breve durata (RSI(2) < 5) è seguito da un rimbalzo: l'R medio è più alto di un ingresso casuale con
la stessa uscita e lo stesso stop.

**Sotto-domande.** Vale solo in tendenza rialzista (lo dice la fonte)? Con che dimensione del
ribasso? Chi opera: venditori impazienti o forzati che spingono il prezzo sotto il valore di breve,
fornitori di liquidità che vengono pagati per assorbire. L'effetto è di poche barre.

**Spiegazioni concorrenti.**

| # | Spiegazione | Previsione | Cosa la smentisce |
|---|---|---|---|
| 1 | Effetto casuale | t vicino a 0 | t oltre la soglia |
| 2 | Trend di fondo (il filtro della media a 200 entra solo nei mercati in salita) | la (b), che entra anche fuori tendenza, è peggiore solo per il trend | vantaggio contro la (a), che ha lo stesso stop ma nessun filtro (non spiega da solo) |
| 3 | È solo il mercato | R correlato a BTC | correlazione bassa |
| 4 | Volatilità: dopo un calo brusco l'ATR è alto e lo stop largo, i costi in R scendono | differenza spiegata dai costi in R | differenza nel lordo |
| 5 | Pochi trade estremi | senza i 3 migliori sotto la (b) | sopra la (b) |
| 6 | Artefatto dei dati (barra anomala) | trade concentrati sui giorni tolti | no |
| 7 | Effetto costi a 1h | R netto negativo a 1h, positivo a 4h | positivo a 1h |
| 8 | Il ribasso continua (momentum di brevissimo) | R sotto la (b), molti stop | R sopra la (b) |
| 9 | Uscita asimmetrica: «chiudi sopra la media a 5» taglia presto i guadagni e lascia correre le perdite fino allo stop | R mediano positivo ma media negativa | media positiva |
| 10 | Le regole sono nate su azioni giornaliere, non su crypto infragiornaliere: il meccanismo non si trasferisce | nessun vantaggio su entrambi i timeframe | vantaggio |

**Ipotesi.** BNBUSDT, inversione di breve in tendenza, long, 1h e 4h (la fonte è giornaliera su
azioni; su una moneta che scambia 24 ore su 24 il «breve» di qualche giorno corrisponde a decine
di ore; il giornaliero darebbe pochissimi trade).

**Varianti.**
* `I-03-1h` (`varianti.i03("1h")`): close > SMA(200) e RSI(2) < 5 → long; uscita quando close >
  SMA(5); stop 2,5 ATR(14) (la fonte non usa stop; 2,5 ATR è largo abbastanza da non tagliare il
  rimbalzo e serve al dimensionamento del bot).
* `I-03-4h` (`varianti.i03("4h")`): stesse regole a 4h. Motivo: i costi a 1h pesano circa il
  doppio in R.

Previsione: 1h R medio fra −0,15 e +0,05 (costi alti); 4h fra −0,10 e +0,10; nessuna batte
nettamente la (b).

---

## I-04 — Effetto del lunedì

**Fonte.** Guglielmo Maria Caporale, Alex Plastun, «The day of the week effect in the
cryptocurrency market», Finance Research Letters 31, 2019 (versione di lavoro CESifo 6716,
2017): per Bitcoin i rendimenti del lunedì sono significativamente più alti degli altri giorni;
per le altre monete studiate no, e i profitti della simulazione non si distinguono dal caso.

**Affermazione verificabile.** Su BNBUSDT il rendimento del lunedì (dall'apertura alle 00:00 UTC
alla chiusura) in R è più alto di quello di un giorno preso a caso con la stessa uscita.

**Sotto-domande.** Dipende dal fine settimana precedente (poco volume, movimenti accumulati)? Chi
opera il lunedì: il ritorno dei desk istituzionali e dei mercati tradizionali. L'effetto è di un
giorno.

**Spiegazioni concorrenti.**

| # | Spiegazione | Previsione | Cosa la smentisce |
|---|---|---|---|
| 1 | Effetto casuale (la fonte stessa dice che i profitti non si distinguono dal caso) | t vicino a 0 | t oltre la soglia |
| 2 | Trend di fondo | il long batte la (a) ma non la (b) | — |
| 3 | È solo il mercato (effetto di BTC trascinato su BNB) | R correlato a BTC del lunedì | — (sarebbe comunque un effetto del lunedì, ma non di BNB) |
| 4 | Volatilità del lunedì più alta | stop larghi, R lordo simile alla (b) | R lordo più alto |
| 5 | Pochi lunedì estremi | senza i 3 migliori sotto la (b) | sopra |
| 6 | Artefatto: confine del giorno in UTC diverso da quello della fonte | — | — (si dichiara) |
| 7 | Effetto costi | trascurabile a 1d | — |
| 8 | L'effetto è di Bitcoin e non si estende alle altre monete (la fonte lo trova solo su Bitcoin) | nessun vantaggio su BNB | vantaggio |
| 9 | Ricerca multipla sui giorni della settimana nella fonte (7 giorni provati) | effetto che sparisce fuori campione | — (lo giudica la validazione) |
| 10 | Notizie del fine settimana assorbite il lunedì in un senso preciso | rendimenti del lunedì più dispersi, non più alti | media più alta |

**Ipotesi.** BNBUSDT, stagionalità del giorno, 1d, long un giorno.

**Varianti.**
* `I-04-L` (`varianti.i04()`): alla chiusura della barra della domenica → long all'apertura del
  lunedì, uscita all'apertura del martedì; stop 2 ATR(14).

Previsione: R medio fra −0,05 e +0,05, non batte la (b).

---

## I-05 — Funding estremo come segnale di affollamento

**Fonte.** Maik Schmeling, Andreas Schrimpf, Karamfil Todorov, «Crypto carry», BIS Working Paper
1087, aprile 2023: il premio dei futures sul prezzo a pronti (carry) nasce dalla domanda di leva
di investitori che inseguono la tendenza e dalla scarsità di capitale per l'arbitraggio; con leva
alta e margini che salgono, le liquidazioni nei ribassi rendono frequenti i crolli.

**Affermazione verificabile.** Su BNBUSDT, quando il funding appena pagato è sopra il 90°
percentile dei 90 settlement precedenti (30 giorni), le 24 ore successive hanno, per uno short, R
medio più alto di uno short a caso con la stessa uscita; simmetricamente, funding sotto il 10°
percentile favorisce il long.

**Sotto-domande.** Vale solo quando il funding è alto in assoluto o anche quando è alto rispetto al
mese? Chi opera: long con leva che pagano per tenere la posizione e che vengono liquidati al primo
calo. Quanto dura: ore o giorni.

**Spiegazioni concorrenti.**

| # | Spiegazione | Previsione | Cosa la smentisce |
|---|---|---|---|
| 1 | Effetto casuale | t vicino a 0 | t oltre la soglia |
| 2 | Trend di fondo: il funding alto arriva nei mercati in salita, dove lo short perde | lo short perde contro la (b) nel 2021 | short sopra la (b) anche nel 2021 |
| 3 | È solo il mercato (funding alto su tutte le monete insieme) | R correlato a BTC | correlazione bassa |
| 4 | Volatilità alta quando il funding è estremo | stop larghi, costi in R bassi | differenza nel lordo |
| 5 | Pochi crolli estremi (pochi trade fanno tutto) | senza i 3 migliori sotto la (b) | sopra |
| 6 | Artefatto: il funding usato non era noto alla chiusura della barra | crollo col ritardo di una barra | nessun crollo |
| 7 | Effetto costi | piccolo a 8h | — |
| 8 | Il funding è anche un costo/ricavo diretto: lo short incassa funding alto | il vantaggio è il funding incassato, non il prezzo | R lordo di prezzo sopra la (b) |
| 9 | Il funding alto segnala forza che continua (momentum) | short sotto la (b) | sopra |
| 10 | Il funding di BNB resta spesso fermo al tasso base: il percentile scatta per piccole differenze | segnali rari o rumorosi | — (si guarda la distribuzione nel conteggio) |

**Ipotesi.** BNBUSDT, posizionamento con leva, 8h (allineato ai settlement ogni 8 ore), 24 ore.

**Varianti.**
* `I-05-S` (`varianti.i05("short")`): alla chiusura della barra a 8h, se l'ultimo funding noto
  (settlement entro la chiusura) è strettamente sopra il 90° percentile dei 90 settlement
  precedenti → short per 3 barre (24 ore); stop 2 ATR(14).
* `I-05-L` (`varianti.i05("long")`): funding strettamente sotto il 10° percentile → long per 3
  barre; stop 2 ATR(14).

Previsione: R medio fra −0,10 e +0,10 per entrambe; nessuna batte nettamente la (b).

---

## I-06 — Compressione delle bande di Bollinger

**Fonte.** John Bollinger, «Bollinger on Bollinger Bands», McGraw-Hill, 2001: la larghezza delle
bande ai minimi di sei mesi («squeeze») precede un'espansione della volatilità; la direzione si
legge dalla prima chiusura fuori banda.

**Affermazione verificabile.** Su BNBUSDT a 4h, dopo una compressione (larghezza delle bande al
minimo delle ultime 120 barre negli ultimi 6), una chiusura sopra la banda superiore è seguita da
una salita che l'ingresso casuale con la stessa uscita non ha (e simmetrico sotto la banda
inferiore).

**Sotto-domande.** Le compressioni lunghe danno movimenti più forti? Chi opera: chi ha ordini
fermi sopra e sotto un intervallo stretto; la loro esecuzione alimenta la direzione. Quanto dura:
giorni.

**Spiegazioni concorrenti.**

| # | Spiegazione | Previsione | Cosa la smentisce |
|---|---|---|---|
| 1 | Effetto casuale | t vicino a 0 | t oltre la soglia |
| 2 | Trend di fondo | il long vince solo nel 2020-2021 | anche nel 2022 |
| 3 | È solo il mercato | R correlato a BTC | correlazione bassa |
| 4 | Volatilità bassa → stop stretti → costi in R alti | R netto negativo con lordo positivo | netto positivo |
| 5 | Pochi trade estremi | senza i 3 migliori sotto la (b) | sopra |
| 6 | Artefatto dei dati | — | — |
| 7 | Effetto costi | costi in R più alti della (b) | simili |
| 8 | Falsa rottura e ritorno nell'intervallo | molte uscite rapide sotto la media | poche |
| 9 | È la stessa rottura di I-02 con un nome diverso | risultati simili a I-02 | diversi |
| 10 | Uscita alla media a 20 troppo vicina: taglia il movimento | R mediano negativo | positivo |

**Ipotesi.** BNBUSDT, rottura dopo compressione, 4h (120 barre = 20 giorni come finestra della
compressione: i «sei mesi» della fonte su candele giornaliere darebbero pochi segnali in 2,7
anni), long e short.

**Varianti.**
* `I-06-L` (`varianti.i06("long")`): squeeze e close > banda superiore (SMA20 + 2 deviazioni
  standard) → long; uscita quando close < SMA20; stop 2 ATR(14).
* `I-06-S` (`varianti.i06("short")`): squeeze e close < banda inferiore → short; uscita quando
  close > SMA20; stop 2 ATR(14).

Previsione: R medio fra −0,10 e +0,10; nessuna batte nettamente la (b).

---

## I-07 — Premio del volume alto

**Fonte.** Simon Gervais, Ron Kaniel, Dan H. Mingelgrin, «The High-Volume Return Premium»,
Journal of Finance 56(3), giugno 2001: i titoli con volume insolitamente alto in un giorno o in
una settimana salgono nel mese successivo; la spiegazione è la visibilità, che porta nuovi
compratori.

**Affermazione verificabile.** Su BNBUSDT, dopo un giorno con volume nel 10% più alto degli
ultimi 50 giorni, i 5 giorni successivi hanno R medio long più alto dell'ingresso casuale.

**Sotto-domande.** Conta il segno del rendimento del giorno di volume? (la fonte dice di no). Chi
opera: nuovi investitori attirati dall'attenzione. Quanto dura: settimane.

**Spiegazioni concorrenti.**

| # | Spiegazione | Previsione | Cosa la smentisce |
|---|---|---|---|
| 1 | Effetto casuale | t vicino a 0 | t oltre la soglia |
| 2 | Trend di fondo | il long vince nel 2021 e perde nel 2022 | vince anche nel 2022 |
| 3 | È solo il mercato (volume alto su tutte le monete nei giorni di crollo o di euforia) | R correlato a BTC | bassa |
| 4 | Volatilità: volume alto = giorni di volatilità alta = stop larghi | costi in R minimi, lordo come la (b) | lordo sopra |
| 5 | Pochi trade estremi | senza i 3 migliori sotto la (b) | sopra |
| 6 | Artefatto: volume in moneta base, gonfiato quando il prezzo è basso | segnali concentrati nel 2020 | distribuiti |
| 7 | Effetto costi | trascurabile a 1d | — |
| 8 | Nelle crypto il volume alto viene dai crolli e dalle liquidazioni: segue un rimbalzo o un'altra discesa, non un premio | R dipende dal segno del giorno | — |
| 9 | La visibilità non vale per una moneta già molto visibile come BNB | nessun vantaggio | vantaggio |
| 10 | Il mese della fonte diventa 5 giorni qui: l'orizzonte sbagliato | nessun vantaggio a 5 giorni | — |

**Ipotesi.** BNBUSDT, attenzione e volume, 1d (il volume insolito è un fatto giornaliero nella
fonte), long 5 giorni (orizzonte più corto del mese della fonte per arrivare ai trade minimi:
scelto prima di contare).

**Varianti.**
* `I-07-L` (`varianti.i07()`): volume del giorno ≥ 90° percentile dei volumi degli ultimi 50
  giorni (compreso il giorno) → long per 5 barre; stop 2 ATR(14).

Previsione: R medio fra −0,05 e +0,10; non batte nettamente la (b).

---

## I-08 — Sovrareazione seguita da continuazione

**Fonte.** Guglielmo Maria Caporale, Alex Plastun, «Price overreactions in the cryptocurrency
market», Journal of Economic Studies 46(5), 2019: dopo un giorno di sovrareazione i movimenti del
giorno dopo sono più grandi del normale; scommettere sull'inversione perde, scommettere sulla
continuazione dà profitti che però non si distinguono dal caso.

**Affermazione verificabile.** Su BNBUSDT, quando il rendimento delle ultime 24 ore supera la sua
media di 30 giorni di più di 2 deviazioni standard, le 24 ore successive proseguono nella stessa
direzione più di un ingresso casuale con la stessa uscita.

**Sotto-domande.** Vale di più per i movimenti all'insù o all'ingiù? Chi opera: chi arriva tardi
alla notizia, chi viene liquidato e alimenta il movimento. Quanto dura: un giorno (lo dice la fonte).

**Spiegazioni concorrenti.**

| # | Spiegazione | Previsione | Cosa la smentisce |
|---|---|---|---|
| 1 | Effetto casuale (la fonte stessa: non si distingue dal caso) | t vicino a 0 | t oltre la soglia |
| 2 | Trend di fondo | il long vince nel 2020-2021 | anche nel 2022 |
| 3 | È solo il mercato | R correlato a BTC | bassa |
| 4 | Volatilità: dopo una sovrareazione la volatilità è alta e lo stop a 2 ATR scatta spesso | molti stop, R negativo | pochi stop |
| 5 | Pochi trade estremi | senza i 3 migliori sotto la (b) | sopra |
| 6 | Artefatto dei dati | — | — |
| 7 | Effetto costi | piccolo a 4h | — |
| 8 | Inversione invece di continuazione | R sotto la (b) | sopra |
| 9 | Grappoli di segnali nello stesso episodio (una sola storia contata più volte) | blocco lungo, pochi blocchi | — |
| 10 | La soglia di 2 deviazioni standard è scelta a caso | — (le verifiche di robustezza la spostano) | — |

**Ipotesi.** BNBUSDT, continuazione dopo sovrareazione, 4h con rendimento a 24 ore misurato a ogni
chiusura (la fonte usa il giorno; misurare la finestra di 24 ore ogni 4 ore tiene l'orizzonte
della fonte e permette di arrivare ai trade minimi), uscita dopo 24 ore.

**Varianti.**
* `I-08-L` (`varianti.i08("long")`): r24 = close / close di 6 barre prima − 1; se r24 > media
  degli r24 delle ultime 180 barre + 2 deviazioni standard → long per 6 barre; stop 2 ATR(14).
* `I-08-S` (`varianti.i08("short")`): se r24 < media − 2 deviazioni standard → short per 6 barre.

Previsione: R medio fra −0,10 e +0,10; nessuna batte nettamente la (b).

---

## I-09 — Squilibrio degli ordini aggressivi

**Fonte.** Tarun Chordia, Avanidhar Subrahmanyam, «Order imbalance and individual stock returns:
Theory and evidence», Journal of Financial Economics 72(3), 2004: i grandi operatori spezzano gli
ordini, lo squilibrio fra acquisti e vendite è persistente e lo squilibrio passato predice
positivamente i rendimenti.

**Affermazione verificabile.** Su BNBUSDT, quando la quota netta di volume comprato dagli
aggressori nelle ultime 24 ore (6 barre a 4h) è nel 10% più alto degli ultimi 30 giorni, le 24
ore successive salgono più dell'ingresso casuale; simmetrico per lo short.

**Sotto-domande.** Lo squilibrio predice o è solo il riflesso del movimento già avvenuto? Chi
opera: grandi compratori che spezzano gli ordini su più giorni. Quanto dura: un giorno.

**Spiegazioni concorrenti.**

| # | Spiegazione | Previsione | Cosa la smentisce |
|---|---|---|---|
| 1 | Effetto casuale | t vicino a 0 | t oltre la soglia |
| 2 | Trend di fondo | il long vince nel 2021 | anche nel 2022 |
| 3 | È solo il mercato | R correlato a BTC | bassa |
| 4 | Volatilità | differenza nei costi in R | nel lordo |
| 5 | Pochi trade estremi | senza i 3 migliori sotto la (b) | sopra |
| 6 | Artefatto: il volume degli aggressori nei CSV di Binance ha errori o buchi | segnali concentrati in pochi giorni | distribuiti |
| 7 | Effetto costi | piccolo a 4h | — |
| 8 | Lo squilibrio riflette solo il rendimento passato (è un momentum mascherato) | risultati uguali a I-08 | diversi |
| 9 | Inversione: la pressione dei compratori si esaurisce (la fonte: il segno si inverte a parità di squilibrio corrente) | R sotto la (b) | sopra |
| 10 | Sui futures crypto l'aggressore è spesso chi viene liquidato, non chi ha informazione | nessun vantaggio | vantaggio |

**Ipotesi.** BNBUSDT, flusso degli ordini, 4h con finestra di 24 ore (la fonte è giornaliera),
24 ore.

**Varianti.**
* `I-09-L` (`varianti.i09("long")`): squilibrio = (2 × volume degli aggressori in acquisto − volume)
  / volume, sommati sulle ultime 6 barre; se ≥ 90° percentile delle ultime 180 barre → long 6 barre;
  stop 2 ATR(14).
* `I-09-S` (`varianti.i09("short")`): squilibrio ≤ 10° percentile → short 6 barre.

Previsione: R medio fra −0,10 e +0,10; nessuna batte nettamente la (b).

---

## I-10 — Incrocio della media mobile a 50

**Fonte.** William Brock, Josef Lakonishok, Blake LeBaron, «Simple Technical Trading Rules and the
Stochastic Properties of Stock Returns», Journal of Finance 47(5), dicembre 1992: le regole a media
mobile (fra cui prezzo contro media a 50) danno rendimenti dopo i segnali d'acquisto più alti di
quelli dopo i segnali di vendita.

**Affermazione verificabile.** Su BNBUSDT a 4h, un long all'incrocio al rialzo del prezzo sopra la
media a 50 barre, tenuto finché il prezzo resta sopra, ha R medio più alto dell'ingresso casuale con
la stessa uscita (e simmetrico per lo short).

**Sotto-domande.** Funziona solo nelle tendenze lunghe? Chi opera: chi segue la tendenza. Quanto
dura: giorni.

**Spiegazioni concorrenti.**

| # | Spiegazione | Previsione | Cosa la smentisce |
|---|---|---|---|
| 1 | Effetto casuale | t vicino a 0 | t oltre la soglia |
| 2 | Trend di fondo | long vince nel 2020-2021 | anche nel 2022 |
| 3 | È solo il mercato | R correlato a BTC | bassa |
| 4 | Volatilità | — | — |
| 5 | Pochi trade estremi (una tendenza lunga fa tutto) | senza i 3 migliori sotto la (b) | sopra |
| 6 | Artefatto dei dati | — | — |
| 7 | Effetto costi: molti incroci falsi | costi in R alti, R netto negativo | — |
| 8 | Laterali con incroci a ripetizione | R mediano negativo e molti trade brevi | — |
| 9 | Le regole di Brock e colleghi hanno smesso di funzionare dopo la pubblicazione (lo dice la letteratura successiva) | nessun vantaggio | vantaggio |
| 10 | Stessa informazione della rottura di Donchian (I-02) | risultati simili | diversi |

**Ipotesi.** BNBUSDT, tendenza con media mobile, 4h (a 1d gli incroci in 2,7 anni sono pochi),
long e short.

**Varianti.**
* `I-10-L` (`varianti.i10("long")`): close sopra la SMA(50) e close precedente sotto o uguale alla
  SMA(50) precedente → long; uscita quando close < SMA(50); stop 2 ATR(14).
* `I-10-S` (`varianti.i10("short")`): incrocio al ribasso → short; uscita quando close > SMA(50).

Previsione: R medio fra −0,15 e +0,05; nessuna batte nettamente la (b).

---

## I-11 — Momento infragiornaliero: prima mezz'ora e ultima mezz'ora

**Fonte.** Dehua Shen, Andrew Urquhart, Pengfei Wang, «Bitcoin intraday time series momentum»,
Financial Review 57(2), 2022 (online ottobre 2021): per Bitcoin il rendimento della prima mezz'ora
predice quello dell'ultima mezz'ora; gli autori lo attribuiscono alla fornitura di liquidità.

**Affermazione verificabile.** Su BNBUSDT, se la prima mezz'ora del giorno UTC (00:00-00:30) sale,
l'ultima mezz'ora dello stesso giorno (23:30-24:00) sale più di una mezz'ora presa a caso; simmetrico
per lo short.

**Sotto-domande.** Il «giorno» della fonte è definito dal volume, non dall'orologio: con la
mezzanotte UTC il meccanismo vale ancora? È un adattamento, dichiarato qui. Chi opera: fornitori di
liquidità che riequilibrano le scorte a fine giornata. Quanto dura: mezz'ora.

**Spiegazioni concorrenti.**

| # | Spiegazione | Previsione | Cosa la smentisce |
|---|---|---|---|
| 1 | Effetto casuale | t vicino a 0 | t oltre la soglia |
| 2 | Trend di fondo | irrilevante su mezz'ora | — |
| 3 | È solo il mercato | R correlato a BTC nell'ultima mezz'ora | bassa |
| 4 | Volatilità di fine giornata UTC diversa | costi in R diversi dalla (b) | — |
| 5 | Pochi trade estremi | senza i 3 migliori sotto la (b) | sopra |
| 6 | Artefatto: il confine UTC non è il confine della fonte | nessun effetto | effetto |
| 7 | Effetto costi: a 30m il costo è circa 0,14 R per giro | R netto negativo anche con lordo positivo | netto positivo |
| 8 | Il funding alle 00:00 UTC muove il prezzo attorno alla mezzanotte | R legato al funding | no |
| 9 | Il meccanismo è di Bitcoin e non di BNB | nessun effetto | effetto |
| 10 | Ricerca multipla della fonte su più finestre | nessun effetto fuori campione | — |

**Ipotesi.** BNBUSDT, momento infragiornaliero, 30m (la durata della finestra della fonte), una
barra.

**Varianti.**
* `I-11-L` (`varianti.i11("long")`): alla chiusura della barra delle 23:00 UTC, se la barra delle
  00:00 dello stesso giorno ha chiuso sopra l'apertura → long all'apertura delle 23:30, uscita alle
  00:00; stop 2 ATR(14).
* `I-11-S` (`varianti.i11("short")`): se ha chiuso sotto → short.

Previsione: R medio fra −0,20 e 0 per entrambe (costi); nessuna batte nettamente la (b).

---

## I-12 — Rimbalzo dopo una caduta forzata

**Fonte.** Markus K. Brunnermeier, Lasse Heje Pedersen, «Market Liquidity and Funding Liquidity»,
Review of Financial Studies 22(6), 2009: quando il capitale degli intermediari si restringe, le
vendite forzate e i margini che salgono creano spirali di liquidità; i prezzi si allontanano dal
valore e poi tornano.

**Affermazione verificabile.** Su BNBUSDT, dopo un'ora con una caduta dall'apertura alla chiusura
più grande di 3 volte l'ATR precedente, le 12 ore successive salgono più di un ingresso casuale con
la stessa uscita.

**Sotto-domande.** Più grande la caduta, più forte il rimbalzo? Chi opera: chi viene liquidato (vende
senza guardare il prezzo) e chi fornisce liquidità. Quanto dura: ore.

**Spiegazioni concorrenti.**

| # | Spiegazione | Previsione | Cosa la smentisce |
|---|---|---|---|
| 1 | Effetto casuale | t vicino a 0 | t oltre la soglia |
| 2 | Trend di fondo | il long vince nel 2021 | anche nel 2022 |
| 3 | È solo il mercato (cadute di tutto il mercato) | R correlato a BTC | bassa |
| 4 | Volatilità alta dopo la caduta: stop scattano | molti stop | pochi |
| 5 | Pochi trade estremi | senza i 3 migliori sotto la (b) | sopra |
| 6 | Artefatto: barre anomale nei dati | trade su barre isolate senza volume | no |
| 7 | Effetto costi | 0,07-0,09 R a 1h | — |
| 8 | La caduta continua (cascata di liquidazioni) | R sotto la (b) | sopra |
| 9 | Grappoli: più cadute nello stesso episodio | pochi blocchi | — |
| 10 | Le cadute vere sono rare: troppo pochi trade | scarto per trade minimi | — |

**Ipotesi.** BNBUSDT, spirale di liquidità, 1h (le liquidazioni avvengono in minuti e ore), long 12
ore.

**Varianti.**
* `I-12-3` (`varianti.i12(3.0)`): close − open < −3 ATR(14) della barra precedente → long 12 barre;
  stop 2 ATR(14).
* `I-12-2` (`varianti.i12(2.0)`), solo se `I-12-3` resta sotto i trade minimi (allentare la soglia
  di uno scarto senza aver visto risultati, regola 6): soglia a 2 ATR.

Previsione: R medio fra −0,10 e +0,15; non batte nettamente la (b).

---

## I-13 — Cambio del mese

**Fonte.** Josef Lakonishok, Seymour Smidt, «Are Seasonal Anomalies Real? A Ninety-Year
Perspective», Review of Financial Studies 1(4), 1988: i rendimenti attorno al cambio del mese
(ultimo giorno e primi tre) sono più alti degli altri giorni.

**Affermazione verificabile.** Su BNBUSDT, i 4 giorni dall'ultimo del mese al terzo del mese dopo
hanno R medio più alto dell'ingresso casuale con la stessa uscita.

**Sotto-domande.** Vale per una moneta senza stipendi né fondi che investono a inizio mese? È un
meccanismo dei mercati azionari (flussi di inizio mese).

**Spiegazioni concorrenti.** 1 caso (t vicino a 0); 2 trend di fondo (vince solo in salita); 3 è solo
il mercato (correlato a BTC); 4 volatilità (costi in R); 5 pochi mesi estremi (senza i 3 migliori);
6 artefatto del confine UTC; 7 costi (trascurabili); 8 i flussi di inizio mese non esistono in crypto
(nessun effetto); 9 scadenze mensili dei derivati (effetto opposto); 10 troppo pochi mesi (circa 33
trade in costruzione: scarto previsto per trade minimi).

**Ipotesi.** BNBUSDT, stagionalità mensile, 1d, long 4 giorni.

**Varianti.**
* `I-13-L` (`varianti.i13()`): alla chiusura della barra che precede l'ultimo giorno del mese →
  long per 4 barre; stop 2 ATR(14). Previsione: sotto i 70 trade, quindi scarto.
