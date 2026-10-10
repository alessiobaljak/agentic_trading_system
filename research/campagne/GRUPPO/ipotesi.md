# Campagna di gruppo — ipotesi

Ogni idea vale per tutte le 80 monete di `monete.csv`, con una sola regola (regole.md, sezione 3). Le varianti di
un'idea sono tutte scritte qui prima del primo test di quell'idea (regola 6 del protocollo). Dati che una variante
può usare: le candele chiuse della moneta stessa, le candele chiuse di BTCUSDT, il funding della moneta già
regolato (regole.md, sezione 3, punto 3). Mai altre monete del gruppo.

Convenzioni comuni a tutte le idee, se l'idea non dice altro:

* ATR = media di Wilder del vero intervallo su 14 barre, calcolata sulle barre chiuse della moneta.
* Lo stop si calcola dalla chiusura della barra del segnale; l'ingresso è all'apertura della barra dopo (motore).
* «Tenuta N» = la posizione si chiude all'apertura della barra dopo N barre tenute (la barra d'ingresso conta
  come la prima), se stop o target non l'hanno già chiusa.
* La (a) è la stessa uscita entrando a ogni barra libera dalla prima barra in cui la variante può entrare; la
  strategia casuale della (b) e delle sfasate usa la stessa uscita (contratto di `gruppo.py`).
* Il tetto di stop del bot è il 6% (`parametri.yaml`, `stop_massimo_bot`): le varianti con stop in ATR su candele
  giornaliere lo superano quasi sempre (lo dice il costo in R qui sotto); il bot non le può eseguire così come
  sono, e lo si dichiara. Il bot oggi ha indicatori dal vivo solo fino a 1 ora (`config/regole_dimensione.md`).
* Costo di un giro in R (commissione 0,05% per lato più lo slippage della scheda, andata e ritorno, diviso la
  distanza dello stop): calcolato con `codice/costi_in_r.py` sui soli dati di costruzione, scritto in ogni idea.
  **1d** (`lavoro/costi_1d.out`): ATR a 14 giorni / chiusura, mediana per moneta da 6,6% a 13,1% (mediana fra le
  monete 10,5%); stop a 3 ATR = circa 31% di distanza, costo di un giro 0,008 R (mediana fra le monete; massimo
  0,015 R); stop a 2 ATR = circa 21%, 0,012 R (massimo 0,022 R). Il funding (circa 0,01% ogni 8 ore in condizioni
  normali) costa circa 0,03% al giorno, cioè circa 0,001 R al giorno con lo stop a 3 ATR. Su 1d i costi non
  decidono un'idea: decide il movimento.

---

## I-01 — Momento a serie storica

**1. Fonti.**
* Tobias J. Moskowitz, Yao Hua Ooi, Lasse Heje Pedersen, «Time series momentum», Journal of Financial Economics
  104(2), maggio 2012.
* Yukun Liu, Aleh Tsyvinski, «Risks and Returns of Cryptocurrency», NBER Working Paper 24877, agosto 2018 (poi
  Review of Financial Studies 34(6), 2021).

**2. Affermazione verificabile.** Il segno del rendimento di una moneta nelle ultime settimane predice, con lo
stesso segno, il rendimento della settimana dopo (Moskowitz e altri sui futures di molte classi; Liu e Tsyvinski
trovano nel bitcoin un momento a 1-4 settimane, legato all'attenzione degli investitori). Per il gruppo: un long
aperto quando il rendimento degli ultimi 21 giorni è positivo e tenuto 7 giorni ha un R medio più alto di un long
aperto a caso con la stessa uscita (la (b)) e di un long aperto sempre (la (a)); lo short simmetrico ha un R medio
più alto dei corrispondenti short. Si smentisce se il `t` contro la (b) non è positivo o se non batte nettamente.

**Perché su monete diverse per la stessa ragione.** Il meccanismo proposto (sottoreazione all'informazione e
inseguimento del trend da parte di investitori piccoli, il cui interesse cresce con il prezzo) non dipende dalla
moneta: riguarda chi la compra. Le alt del gruppo hanno la stessa base di investitori al dettaglio del bitcoin.

**3. Sotto-domande.** In quali condizioni: con volatilità alta o bassa? Solo quando anche BTC è in rialzo? Più
nelle monete piccole (slippage 0,10%) che in quelle grandi? Chi opera: investitori al dettaglio che inseguono, fondi
di trend su futures, liquidazioni a catena degli short (per il long) o dei long (per lo short). Quando: Liu e
Tsyvinski misurano il rendimento della settimana dopo; l'effetto, se c'è, si vede in 1-4 settimane.

**4-5. Spiegazioni concorrenti, con la previsione che fanno e cosa le smentirebbe.**
1. *Effetto casuale.* Prevede `t` contro la (b) vicino a 0 e percentile fra le simulazioni vicino a 50. Smentita: `t` sopra la soglia.
2. *È solo il mercato, prima forma: le monete seguono BTC o il trend comune.* Una moneta in rialzo da 21 giorni sta in un mercato in rialzo; il long guadagna con il mercato. Prevede: la (b) long, che entra a caso nella stessa direzione, guadagna quasi quanto la variante; l'R per anno segue il buy and hold di gruppo. Smentita: la variante batte nettamente la (b) e ha R positivo anche nell'anno di ribasso (2022).
3. *È solo il mercato, seconda forma: i trade di monete diverse negli stessi giorni sono una sola scommessa ripetuta.* Prevede: effetto grappolo alto, blocco lungo, pavimento delle sfasate alto, e «nettamente» che cade con il pavimento. Smentita: batte nettamente con il pavimento delle sfasate.
4. *Trend di fondo del periodo.* Il 2020-2021 è stato di forte rialzo e il 2022 di forte ribasso; il long vince per i primi anni e lo short per il 2022. Prevede: R per anno con il segno del buy and hold. Smentita: R positivo in più della metà degli anni con almeno 100 trade.
5. *Volatilità.* Dopo un rialzo la volatilità cresce, lo stop in ATR si allarga e l'R di ogni trade si restringe: nessun vantaggio in R, solo trade più grandi in percentuale. Prevede: R medio simile alla (a), rendimento in percentuale diverso. Smentita: R medio sopra la (a).
6. *Artefatto dei dati.* Buchi e barre tolte dall'allineamento creano rendimenti a 21 giorni falsi. Prevede: segnali concentrati vicino ai buchi. Smentita: pochi buchi (Fase 0) e trade diffusi.
7. *Effetto costi e funding.* In momento positivo il funding è alto e i long lo pagano; lo short lo incassa. Prevede: il long perde il vantaggio dopo il funding, lo short lo guadagna senza vantaggio di prezzo. Smentita: R lordo e netto con lo stesso segno, e costo in R piccolo (sotto).
8. *Pochi trade estremi.* Poche monete che si moltiplicano in una settimana fanno tutta la media. Prevede: senza i 30 trade migliori, senza i 3 giorni migliori o senza le 3 monete migliori l'R scende sotto la (b). Smentita: le tre prove degli estremi superate.
9. *Inversione invece di momento.* Dopo tre settimane di rialzo segue un ritorno indietro (sovrareazione). Prevede: `t` negativo contro la (b) nel long e positivo nello short opposto. Smentita: `t` positivo nel long.
10. *Sopravvivenza dell'elenco.* Le monete sono quelle vive e liquide nel 2023: chi è cresciuto è sovrarappresentato e ogni long ne beneficia. Prevede: (a) e (b) long già positive, variante uguale. Smentita: la variante supera la (b), che ha la stessa sopravvivenza.
11. *Poche monete giovani.* Le monete quotate nel 2021 dominano i segnali (tutte in rialzo appena quotate). Prevede: quota della moneta più presente alta e R per moneta concentrato. Smentita: quota delle monete sopra la propria b_j larga.

**6. Ipotesi completa.** Tutte le 80 monete; meccanismo: continuazione a 1-4 settimane del rendimento passato;
timeframe 1d (il meccanismo è di settimane: candele giornaliere bastano e i costi in R sono piccoli; sotto il
giorno l'idea non dice nulla di più); direzione: una variante per direzione.

Varianti (scritte prima del primo test; modulo `codice/i01_momento.py`):
* **I-01-L** long: `{"direzione": "long", "ritorno_barre": 21, "tenuta": 7, "atr": 14, "stop_atr": 3.0}`. 21
  giorni: tre settimane, al centro della finestra 1-4 settimane di Liu e Tsyvinski; tenuta 7: l'orizzonte di una
  settimana che loro predicono; stop a 3 ATR: solo stop di emergenza, perché l'idea esce a tempo.
* **I-01-S** short: gli stessi parametri con `"direzione": "short"` (rendimento a 21 giorni sotto zero).

Previsione (al netto dei costi): R medio della variante long fra −0,02 e +0,06, `t` contro la (b) fra −1 e +2;
short: R medio fra −0,04 e +0,04, `t` fra −1 e +1,5. Criterio di successo: candidato (batte nettamente la (a) e la
(b) di gruppo, R medio dopo i costi positivo).

---

## I-02 — Rottura dell'intervallo di prezzo

**1. Fonti.**
* William Brock, Josef Lakonishok, Blake LeBaron, «Simple Technical Trading Rules and the Stochastic Properties of
  Stock Returns», Journal of Finance 47(5), dicembre 1992 (la regola «trading range break»: si compra quando il
  prezzo supera il massimo locale degli ultimi 50, 150 o 200 giorni e si tiene 10 giorni).
* Robert Hudson, Andrew Urquhart, «Technical trading and cryptocurrencies», Annals of Operations Research 297,
  2021 (pubblicato in rete nel 2019): le stesse famiglie di regole hanno potere predittivo su bitcoin, ether,
  litecoin e ripple.

**2. Affermazione verificabile.** Una chiusura sopra il massimo delle 50 chiusure precedenti è seguita da 10 giorni
con rendimento più alto del caso; una chiusura sotto il minimo da 10 giorni più bassi. Per il gruppo: l'R medio dei
long aperti alla rottura in su e tenuti 10 giorni supera la (b) e la (a) di gruppo; lo stesso per gli short alla
rottura in giù. Si smentisce con `t` contro la (b) non positivo o non netto.

**Perché su monete diverse per la stessa ragione.** Il massimo di 50 giorni è un livello che tutti vedono:
ordini di acquisto in attesa sopra il massimo, stop degli short e nuovi acquirenti attratti dalla notizia del
nuovo massimo esistono su ogni moneta quotata, e non dipendono da cosa fa la moneta.

**3. Sotto-domande.** Vale di più con volume alto alla rottura? Con BTC anch'esso in rottura? Quanto dura: 10 giorni
come in Brock e altri, o si esaurisce prima? Chi opera: chi compra le rotture (trend follower, investitori al
dettaglio), gli short che chiudono con lo stop sopra il massimo. Quando: all'apertura del giorno dopo la rottura.

**4-5. Spiegazioni concorrenti.**
1. *Effetto casuale.* Prevede `t` vicino a 0. Smentita: `t` sopra la soglia.
2. *È solo il mercato (BTC e trend comune).* Le rotture in su arrivano quando tutto il mercato sale: il long guadagna con il mercato. Prevede: la (b) long quasi uguale; R per anno con il segno del buy and hold. Smentita: batte nettamente la (b) e regge nel 2022.
3. *Una sola scommessa ripetuta.* Le rotture di monete diverse cadono negli stessi giorni (rialzi generali). Prevede: effetto grappolo e pavimento delle sfasate alti, «nettamente» che cade. Smentita: batte nettamente con il pavimento.
4. *Trend di fondo del periodo.* Prevede R per anno con il segno del buy and hold. Smentita: R positivo in più della metà degli anni con almeno 100 trade.
5. *Volatilità.* Le rotture coincidono con l'aumento della volatilità: lo stop in ATR si allarga e l'R si comprime. Prevede R medio simile alla (a). Smentita: R sopra la (a).
6. *Falsa rottura.* Gli ordini sopra il massimo vengono assorbiti e il prezzo torna indietro (caccia agli stop). Prevede `t` negativo. Smentita: `t` positivo.
7. *È solo il momento di I-01.* Una rottura è un caso particolare di rendimento passato positivo. Prevede: risultato simile a I-01, senza informazione in più. Smentita: R sopra quello di I-01 con lo stesso orizzonte (solo come lettura; il giudizio resta la (b)).
8. *Artefatto dei dati.* Buchi nelle serie fanno sembrare una rottura. Prevede segnali vicino ai buchi. Smentita: pochi buchi in Fase 0.
9. *Costi e funding.* Alle rotture in su il funding sale e il long paga. Prevede vantaggio lordo che sparisce al netto. Smentita: costo in R piccolo e R netto positivo.
10. *Pochi trade estremi.* Poche rotture seguite da moltiplicazioni del prezzo. Prevede che le prove degli estremi cadano. Smentita: le tre prove superate.
11. *Sopravvivenza dell'elenco.* Le monete vive nel 2023 sono quelle le cui rotture hanno funzionato. Prevede (a) e (b) long già positive. Smentita: la variante supera la (b).

**6. Ipotesi completa.** Tutte le 80 monete; meccanismo: ordini e attenzione concentrati sul massimo (minimo) di
50 giorni; timeframe 1d (la regola di Brock e altri è giornaliera, e i livelli di 50 giorni si vedono su candele
giornaliere); una variante per direzione. Modulo `codice/i02_rottura.py`:
* **I-02-L** long: `{"direzione": "long", "finestra": 50, "tenuta": 10, "atr": 14, "stop_atr": 3.0}`. 50 giorni e
  10 giorni di tenuta sono la regola più corta di Brock e altri (quella con più segnali); stop di emergenza a 3 ATR.
* **I-02-S** short: gli stessi parametri con `"direzione": "short"` (chiusura sotto il minimo delle 50 precedenti).

Previsione (al netto dei costi): long R medio fra −0,03 e +0,08, `t` contro la (b) fra −1 e +2; short R medio fra
−0,05 e +0,05, `t` fra −1,5 e +1,5. Criterio di successo: candidato.

---

## I-03 — Continuazione dopo un giorno anomalo

**1. Fonte.** Guglielmo Maria Caporale, Alex Plastun, «Momentum effects in the cryptocurrency market after one-day
abnormal returns», Financial Markets and Portfolio Management 34, 2020: nei giorni dopo un rendimento giornaliero
anomalo (fuori da media ± k deviazioni standard) il prezzo tende a muoversi nella stessa direzione.

**2. Affermazione verificabile.** Dopo un giorno con rendimento sopra media + 2 deviazioni standard dei 30 giorni
prima, il giorno dopo rende più del caso; dopo un giorno sotto media − 2 deviazioni, il giorno dopo rende meno. Per
il gruppo: il long tenuto un giorno dopo l'anomalo in su ha R medio sopra la (b) e la (a); lo short dopo l'anomalo in
giù idem. Si smentisce con `t` non positivo o non netto.

**Perché su monete diverse per la stessa ragione.** Un rendimento anomalo attira attenzione e ordini il giorno dopo
(investitori che reagiscono in ritardo, liquidazioni a catena di chi era dall'altra parte): avviene su ogni moneta
con leva e investitori al dettaglio, cioè su tutte le monete del gruppo.

**3. Sotto-domande.** Vale più per gli anomali in su o in giù? Più con volume alto? L'effetto è nel giorno dopo o
continua? Chi opera: chi insegue la notizia, chi viene liquidato. Quando: entro il giorno dopo.

**4-5. Spiegazioni concorrenti.**
1. *Effetto casuale.* Prevede `t` vicino a 0. Smentita: `t` sopra la soglia.
2. *È solo il mercato (BTC e trend comune).* Gli anomali in su arrivano nei giorni di rialzo generale, che continuano. Prevede: la (b) quasi uguale. Smentita: batte nettamente la (b).
3. *Una sola scommessa ripetuta.* Molte monete hanno un giorno anomalo nello stesso giorno. Prevede: uscite massime in un giorno alte, pavimento delle sfasate alto, «nettamente» che cade. Smentita: batte nettamente con il pavimento.
4. *Inversione invece di continuazione.* Il giorno anomalo è una sovrareazione che rientra (I-04). Prevede `t` negativo. Smentita: `t` positivo.
5. *Volatilità.* Dopo un giorno anomalo la volatilità è alta: il giorno dopo ha movimenti grandi in entrambi i sensi e lo stop a 3 ATR non scatta quasi mai; l'R medio resta piccolo. Prevede R vicino a 0. Smentita: R positivo netto.
6. *Trend di fondo del periodo.* Prevede R per anno con il segno del buy and hold. Smentita: R positivo in più della metà degli anni con almeno 100 trade.
7. *Costi.* Con tenuta di un giorno il movimento atteso è piccolo e i costi pesano di più in proporzione (il costo in R resta piccolo perché lo stop è largo, ma l'R lordo atteso è anch'esso piccolo). Prevede R lordo positivo e netto vicino a zero. Smentita: R netto positivo.
8. *Artefatto dei dati.* Un buco nella serie fa sembrare anomalo un rendimento su due giorni. Prevede segnali dopo i buchi. Smentita: pochi buchi.
9. *Pochi trade estremi.* Pochi giorni di continuazioni enormi. Prevede che le prove degli estremi cadano. Smentita: superate.
10. *Funding.* Dopo un rialzo anomalo il funding sale: il long paga di più. Prevede peggioramento netto rispetto al lordo. Smentita: R netto positivo.
11. *Sopravvivenza.* Le monete del gruppo sono quelle i cui rialzi anomali non sono stati seguiti da crolli fatali. Prevede (b) long positiva. Smentita: batte la (b).

**6. Ipotesi completa.** Tutte le 80 monete; meccanismo: reazione ritardata a un movimento anomalo; timeframe 1d
(la fonte misura rendimenti giornalieri); una variante per direzione. Modulo `codice/i03_giorno_anomalo.py`:
* **I-03-L** long: `{"direzione": "long", "finestra": 30, "soglia_dev": 2.0, "tenuta": 1, "atr": 14, "stop_atr": 3.0}`.
  30 giorni per media e deviazione: circa un mese, la finestra corta per misurare cosa è «normale» adesso; 2
  deviazioni: un movimento che succede per caso circa una volta al mese; tenuta 1: il giorno dopo, come la fonte.
* **I-03-S** short: gli stessi parametri con `"direzione": "short"` (anomalo in giù, short il giorno dopo).

Previsione (al netto dei costi): long R medio fra −0,04 e +0,05, `t` fra −1 e +1,5; short R medio fra −0,05 e +0,03,
`t` fra −1,5 e +1. Criterio di successo: candidato.

---

## I-04 — Inversione dopo un movimento forzato con volume anomalo

**1. Fonti.**
* Stefan Nagel, «Evaporating Liquidity», Review of Financial Studies 25(7), luglio 2012: i rendimenti
  dell'inversione a breve termine sono il compenso di chi fornisce liquidità a chi vende (o compra) per forza.
* John Y. Campbell, Sanford J. Grossman, Jiang Wang, «Trading Volume and Serial Correlation in Stock Returns»,
  Quarterly Journal of Economics 108(4), novembre 1993: i movimenti di prezzo con volume alto tendono a invertirsi,
  perché sono spinti da chi ha bisogno di liquidità e non da notizie.

**2. Affermazione verificabile.** Dopo un giorno con rendimento sotto media − 2 deviazioni (30 giorni prima) e
volume oltre il doppio della media dei 20 giorni prima, i 3 giorni dopo rendono più del caso (il prezzo forzato
rientra). Per il gruppo: il long aperto dopo quel giorno e tenuto 3 giorni ha R medio sopra la (b) e la (a); lo
short simmetrico (rialzo anomalo con volume anomalo) idem. Si smentisce con `t` non positivo o non netto.

**Perché su monete diverse per la stessa ragione.** Le vendite forzate (liquidazioni delle posizioni a leva,
chiusure obbligate) avvengono su ogni contratto perpetuo con leva; chi compra in quei momenti chiede un compenso,
qualunque sia la moneta.

**3. Sotto-domande.** Vale più quando anche BTC crolla (vendite forzate generali) o quando crolla solo la moneta
(notizia propria, che non rientra)? Quanto dura il rientro: 1-3 giorni? Chi opera: chi viene liquidato, i
fornitori di liquidità. Quando: entro pochi giorni.

**4-5. Spiegazioni concorrenti.**
1. *Effetto casuale.* Prevede `t` vicino a 0. Smentita: `t` sopra la soglia.
2. *È solo il mercato (BTC e trend comune).* I crolli con volume sono giorni di crollo generale, e il rimbalzo è del mercato intero. Prevede: R per anno con il segno del buy and hold, (b) vicina. Smentita: batte nettamente la (b).
3. *Una sola scommessa ripetuta.* I crolli con volume cadono negli stessi giorni su molte monete (un solo evento ripetuto 80 volte). Prevede: uscite massime in un giorno molto alte, pavimento delle sfasate alto. Smentita: batte nettamente con il pavimento.
4. *Notizia vera, nessun rientro.* Il crollo porta informazione (I-03: continuazione). Prevede `t` negativo. Smentita: `t` positivo.
5. *Volatilità.* Dopo un crollo la volatilità è alta e lo stop a 3 ATR è lontano: grandi oscillazioni senza direzione. Prevede R vicino a 0 con dispersione alta. Smentita: R positivo netto.
6. *Trend di fondo del periodo.* Nel 2022 i rimbalzi falliscono. Prevede R negativo nel 2022. Smentita: R positivo in più della metà degli anni con almeno 100 trade.
7. *Artefatto del volume.* Il volume in moneta base cresce quando il prezzo crolla (stesso valore in USDT, più monete). Prevede che la condizione del volume scatti quasi sempre con il crollo e non aggiunga nulla. Smentita: lo si legge nella stima dei trade (meno trade della sola condizione di prezzo) — da dichiarare, non da misurare con conteggi in più.
8. *Costi.* Spread più larghi nei giorni di crollo: lo slippage vero è più alto della fascia. Prevede che il vantaggio sia piccolo come i costi. Smentita: regge a costi doppi (Fase 4).
9. *Pochi trade estremi.* Pochi rimbalzi enormi (marzo 2020). Prevede che le prove degli estremi cadano. Smentita: superate.
10. *Artefatto dei dati.* Buchi intorno ai crolli (manutenzione delle piattaforme). Prevede segnali vicino ai buchi. Smentita: pochi buchi.
11. *Funding.* Dopo un crollo il funding diventa negativo e il long lo incassa: un guadagno che non viene dal prezzo. Prevede R lordo nullo e netto positivo. Smentita: R lordo positivo.

**6. Ipotesi completa.** Tutte le 80 monete; meccanismo: compenso per la liquidità dopo un movimento forzato;
timeframe 1d (le due fonti usano rendimenti e volumi giornalieri o settimanali); una variante per direzione. Modulo
`codice/i04_inversione_volume.py`:
* **I-04-L** long: `{"direzione": "long", "finestra": 30, "soglia_dev": 2.0, "finestra_volume": 20,
  "volume_multiplo": 2.0, "tenuta": 3, "atr": 14, "stop_atr": 3.0}`. Rendimento anomalo come in I-03 (stessa
  definizione, così le due idee si leggono una contro l'altra); volume oltre il doppio della media di 20 giorni:
  un volume che si vede poche volte al mese; tenuta 3: il rientro della liquidità dura pochi giorni.
* **I-04-S** short: gli stessi parametri con `"direzione": "short"` (rialzo anomalo con volume anomalo).

Previsione (al netto dei costi): long R medio fra −0,05 e +0,10, `t` fra −1 e +2; short R medio fra −0,08 e +0,05,
`t` fra −1,5 e +1. Criterio di successo: candidato. Se la stima dei trade è sotto 700 la variante è uno scarto.

---

## I-05 — Affollamento misurato dal funding

**1. Fonti.**
* Maik Schmeling, Andreas Schrimpf, Karamfil Todorov, «Crypto carry», BIS Working Papers n. 1087, aprile 2023: un
  premio dei futures crypto alto (carry) segnala domanda a leva dei piccoli investitori e precede crolli e
  liquidazioni.
* Songrun He, Asaf Manela, Omri Ross, Victor von Wachter, «Fundamentals of Perpetual Futures», arXiv 2212.06888,
  dicembre 2022: il funding dei perpetui misura lo scarto fra il prezzo del perpetuo e quello a pronti, ed è grande
  e persistente.

**2. Affermazione verificabile.** Quando la somma del funding delle ultime 24 ore supera lo 0,15% (cinque volte il
livello normale di 0,01% ogni 8 ore), i long sono affollati e i 3 giorni dopo rendono meno del caso; quando è sotto
−0,15% sono affollati gli short e i 3 giorni dopo rendono più del caso. Per il gruppo: lo short aperto con funding
alto e tenuto 3 giorni ha R medio sopra la (b) e la (a); il long con funding molto negativo idem.

**Perché su monete diverse per la stessa ragione.** Il funding è lo stesso meccanismo su ogni contratto perpetuo di
Binance: misura quanta leva sta da una parte, e una leva sbilanciata si scarica con liquidazioni su qualunque moneta.

**3. Sotto-domande.** Vale di più quando il funding resta alto da giorni? Quando anche BTC ha funding alto (non lo
possiamo sapere: il funding di BTC non è fra i dati ammessi; si usa solo quello della moneta)? Quanto dura lo
scarico: giorni? Chi opera: investitori a leva da una parte, liquidazioni a catena, chi incassa il funding.

**4-5. Spiegazioni concorrenti.**
1. *Effetto casuale.* Prevede `t` vicino a 0. Smentita: `t` sopra la soglia.
2. *È solo il mercato (BTC e trend comune).* Il funding alto arriva nei rialzi generali; lo short perde finché il mercato sale. Prevede: R per anno con il segno opposto al buy and hold, (b) short simile. Smentita: batte nettamente la (b).
3. *Una sola scommessa ripetuta.* Il funding sale insieme su tutte le monete nei giorni di euforia. Prevede: pochi giorni con molti trade, pavimento delle sfasate alto. Smentita: batte nettamente con il pavimento.
4. *Il funding alto è momento, non affollamento.* Funding alto = domanda forte che continua. Prevede `t` negativo per lo short. Smentita: `t` positivo.
5. *Solo l'incasso del funding.* Lo short incassa funding alto: un guadagno che non viene dal prezzo. Prevede R positivo solo per il funding, prezzo neutro. Smentita: R lordo del funding positivo (lettura del risultato per trade, Fase 3).
6. *Volatilità.* Funding estremi coincidono con volatilità estrema: stop in ATR lontani, R compresso. Prevede R vicino a 0. Smentita: R netto positivo.
7. *Pochi episodi estremi.* Pochi giorni di euforia (fine 2020, 2021) fanno tutti i trade. Prevede: R per anno concentrato; le prove sui giorni e sulle monete cadono. Smentita: superate.
8. *Monete piccole.* Il funding estremo è delle monete poco liquide, dove i costi veri sono più alti. Prevede quota della moneta più presente alta. Smentita: trade diffusi.
9. *Artefatto dei dati.* Mesi senza file di funding: nessun segnale; regolamenti con intervallo diverso. Prevede segnali solo in certi periodi. Smentita: copertura del funding in Fase 0.
10. *Trend di fondo del periodo.* Prevede R per anno con segno legato al buy and hold. Smentita: R positivo in più della metà degli anni con almeno 100 trade.
11. *Troppo pochi segnali.* Soglie estreme danno pochi trade: la variante è uno scarto per la stima, non un test. Prevede trade stimati sotto 700. (È un rischio da dichiarare, non una spiegazione del risultato.)

**6. Ipotesi completa.** Tutte le 80 monete; meccanismo: scarico della leva affollata; timeframe 1d (il funding si
regola ogni 8 o 4 ore: una barra giornaliera ne raccoglie una giornata intera, e lo scarico si aspetta in giorni);
una variante per direzione. Modulo `codice/i05_funding.py`:
* **I-05-S** short: `{"direzione": "short", "finestra_ore": 24, "soglia": 0.0015, "tenuta": 3, "atr": 14,
  "stop_atr": 3.0}`. 0,15% in 24 ore: cinque volte il funding normale (0,01% ogni 8 ore); tenuta 3 giorni.
* **I-05-L** long: gli stessi parametri con `"direzione": "long"` (somma sotto −0,15%: soglia simmetrica).

Previsione (al netto dei costi): short R medio fra −0,05 e +0,10, `t` fra −1 e +2; long R medio fra −0,05 e +0,10,
`t` fra −1 e +1,5 (rischio di scarto per trade sotto 700). Criterio di successo: candidato.

---

## I-06 — Rottura dopo una compressione della volatilità

**1. Fonte.** John Bollinger, «Bollinger on Bollinger Bands», McGraw-Hill, 2001: «the Squeeze», la larghezza delle
bande al minimo di sei mesi annuncia un'espansione della volatilità; la direzione si prende dalla rottura della
banda.

**2. Affermazione verificabile.** Dopo una barra con la larghezza delle bande (20 barre, 2 deviazioni) al minimo
delle ultime 180 barre, una chiusura oltre la banda alta nei 5 giorni seguenti è seguita da un movimento che
continua finché il prezzo non torna alla media; lo stesso in giù. Per il gruppo: l'R medio dei long aperti così e
chiusi al ritorno sotto la media supera la (b) e la (a); idem lo short.

**Perché su monete diverse per la stessa ragione.** La compressione della volatilità è un periodo di equilibrio
fra compratori e venditori; la rottura indica che uno dei due ha prevalso e gli ordini in attesa ai bordi
dell'intervallo si attivano. Il meccanismo è nei partecipanti, non nella moneta.

**3. Sotto-domande.** Le rotture dopo compressione sono più affidabili di quelle normali (I-02)? Vale più con BTC
anch'esso compresso? Quanto dura il movimento? Chi opera: chi aspetta la rottura, gli stop ai bordi.

**4-5. Spiegazioni concorrenti.**
1. *Effetto casuale.* Prevede `t` vicino a 0. Smentita: `t` sopra la soglia.
2. *È solo il mercato (BTC e trend comune).* Compressioni e rotture arrivano insieme su tutto il mercato. Prevede (b) vicina, R per anno con il segno del buy and hold. Smentita: batte nettamente la (b).
3. *Una sola scommessa ripetuta.* Le rotture dopo compressione cadono negli stessi giorni. Prevede pavimento delle sfasate alto. Smentita: batte nettamente con il pavimento.
4. *Falsa rottura.* Dopo una compressione la prima rottura è spesso falsa (Bollinger stesso lo nota: «head fake»). Prevede `t` negativo. Smentita: `t` positivo.
5. *Volatilità.* Dopo la compressione l'ATR è piccolo: lo stop a 3 ATR è vicino e scatta spesso nell'espansione. Prevede molti stop, R medio negativo. Smentita: R positivo.
6. *È solo la rottura di I-02.* Prevede risultato simile a I-02. Smentita: lettura, non giudizio.
7. *Uscita alla media.* L'uscita alla media chiude presto i trend: il vantaggio, se c'è, si perde. Prevede durata media corta e R piccolo. Smentita: R netto positivo.
8. *Troppo pochi segnali.* Le compressioni al minimo di 180 barre sono rare. Rischio di scarto per trade sotto 700.
9. *Trend di fondo del periodo.* Prevede R per anno legato al buy and hold. Smentita: R positivo in più della metà degli anni con almeno 100 trade.
10. *Pochi trade estremi.* Prevede che le prove degli estremi cadano. Smentita: superate.
11. *Artefatto dei dati.* Buchi che riducono la deviazione standard. Prevede segnali vicino ai buchi. Smentita: pochi buchi.

**6. Ipotesi completa.** Tutte le 80 monete; meccanismo: espansione della volatilità dopo l'equilibrio, nella
direzione della rottura; timeframe 1d (Bollinger lavora su candele giornaliere; sei mesi = 180 giorni di una
moneta che si scambia sempre); una variante per direzione. Modulo `codice/i06_compressione.py`:
* **I-06-L** long: `{"direzione": "long", "periodo_bb": 20, "k_bb": 2.0, "finestra_compressione": 180,
  "recenti": 5, "atr": 14, "stop_atr": 3.0}`. 20 e 2 sono le bande standard di Bollinger; 180 giorni: i sei mesi del
  libro; 5 giorni per la rottura dopo la compressione; uscita al ritorno alla media (la banda centrale).
* **I-06-S** short: gli stessi parametri con `"direzione": "short"`.

Previsione (al netto dei costi): R medio fra −0,10 e +0,15 (pochi trade, molta dispersione), `t` fra −1 e +1,5 in
entrambe le direzioni; rischio di scarto per trade sotto 700. Criterio di successo: candidato.

---

## I-08 — Giorno della settimana

**1. Fonte.** Guglielmo Maria Caporale, Alex Plastun, «The day of the week effect in the cryptocurrency market»,
Finance Research Letters 31, dicembre 2019: nel bitcoin i rendimenti del lunedì sono anormalmente alti.

**2. Affermazione verificabile.** Il lunedì (giorno UTC) rende più degli altri giorni. Per il gruppo: un long
aperto all'apertura del lunedì e chiuso alla sua chiusura ha R medio sopra la (b) (long in giorni a caso con la
stessa uscita) e la (a) (long tutti i giorni). Si smentisce con `t` non positivo o non netto.

**Perché su monete diverse per la stessa ragione.** Se l'effetto viene dal calendario degli investitori (notizie e
flussi che arrivano a mercati tradizionali chiusi e si riversano il lunedì), tocca tutte le monete, che hanno gli
stessi investitori e lo stesso calendario.

**3. Sotto-domande.** È un effetto del lunedì intero o delle prime ore? Vale ancora dopo il 2019 (l'articolo usa
dati fino al 2019, la costruzione arriva al 2023)? Dipende dal fine settimana precedente (rialzo o ribasso)? Chi
opera: investitori istituzionali che tornano il lunedì, notizie del fine settimana.

**4-5. Spiegazioni concorrenti.**
1. *Effetto casuale (dati estratti a caso dai giorni).* Prevede `t` vicino a 0. Smentita: `t` sopra la soglia.
2. *È solo il mercato (BTC e trend comune).* Il lunedì rende come il mercato quel giorno. Prevede (b) e (a) vicine. Smentita: batte nettamente la (b).
3. *Una sola scommessa ripetuta.* Tutte le 80 monete entrano lo stesso lunedì: 80 trade per una sola scommessa a settimana. Prevede effetto grappolo massimo, pavimento delle sfasate alto. Smentita: batte nettamente con il pavimento.
4. *Effetto scomparso dopo la pubblicazione.* Prevede R positivo nel 2019-2020 e nullo dopo. Smentita: R positivo in più della metà degli anni.
5. *Trend di fondo.* Prevede R per anno con il segno del buy and hold (come la (a)). Smentita: sopra la (a).
6. *Volatilità del lunedì.* Il lunedì è più volatile, non più alto. Prevede R vicino a 0 e dispersione alta. Smentita: R netto positivo.
7. *Costi.* Un giorno di tenuta: R lordo atteso piccolo e costi relativamente grandi. Prevede R lordo positivo, netto vicino a 0. Smentita: R netto positivo.
8. *Pochi lunedì estremi.* Pochi lunedì di rialzi enormi. Prevede che le prove sui giorni cadano. Smentita: superate.
9. *Funding.* Il regolamento delle 00:00 cade all'ingresso: conta solo se costo. Prevede un piccolo costo sistematico. Smentita: R netto positivo.
10. *Artefatto del fuso orario.* Il «lunedì» dell'articolo potrebbe non essere il giorno UTC delle candele. Prevede nessun effetto sul giorno UTC. Smentita: effetto presente.
11. *Sopravvivenza.* Le monete vive hanno rendimenti medi alti ogni giorno. Prevede (a) positiva. Smentita: sopra la (a).

**6. Ipotesi completa.** Tutte le 80 monete; meccanismo: flussi del calendario che arrivano il lunedì; timeframe 1d
(l'effetto è di un giorno); direzione long (l'unica che la fonte indica). Modulo `codice/i08_lunedi.py`:
* **I-08-L** long: `{"direzione": "long", "giorno_ingresso": 0, "tenuta": 1, "atr": 14, "stop_atr": 3.0}`.

Previsione (al netto dei costi): R medio fra −0,03 e +0,05, `t` fra −1 e +1. Criterio di successo: candidato.

---

## I-10 — Vicinanza al massimo dell'ultimo anno

**1. Fonte.** Thomas J. George, Chuan-Yang Hwang, «The 52-Week High and Momentum Investing», Journal of Finance
59(5), ottobre 2004: i titoli vicini al massimo delle 52 settimane continuano a salire, perché gli investitori usano
il massimo come ancora e reagiscono troppo poco alle buone notizie quando il prezzo gli è vicino.

**2. Affermazione verificabile.** Una moneta con la chiusura almeno al 95% del massimo degli ultimi 365 giorni
rende, nei 30 giorni dopo, più del caso. Per il gruppo: il long aperto in quella condizione e tenuto 30 giorni ha R
medio sopra la (b) e la (a). Si smentisce con `t` non positivo o non netto.

**Perché su monete diverse per la stessa ragione.** L'ancoraggio al massimo è un comportamento degli investitori
(resistenza a comprare vicino al massimo), non della moneta.

**3. Sotto-domande.** Vale anche quando il massimo è stato fatto da poco (una moneta in rialzo continuo)? Più per
le monete con storia lunga (365 giorni di riscaldamento tolgono il primo anno)? Chi opera: chi vende vicino al
massimo per ancoraggio, chi compra dopo la rottura.

**4-5. Spiegazioni concorrenti.**
1. *Effetto casuale.* Prevede `t` vicino a 0. Smentita: `t` sopra la soglia.
2. *È solo il mercato (BTC e trend comune).* Le monete sono vicine al massimo quando tutto il mercato lo è. Prevede (b) vicina, R per anno con il buy and hold. Smentita: batte nettamente la (b).
3. *Una sola scommessa ripetuta.* Vicinanza al massimo negli stessi mesi per tutte (fine 2021). Prevede pavimento delle sfasate alto e pochi blocchi. Smentita: batte nettamente con il pavimento.
4. *È solo il momento di I-01.* Prevede risultato simile a I-01. Smentita: lettura, non giudizio.
5. *Massimo come resistenza.* Il prezzo vicino al massimo torna indietro (doppio massimo). Prevede `t` negativo. Smentita: `t` positivo.
6. *Trend di fondo del periodo.* La condizione vale quasi solo nel 2021: un anno solo. Prevede R per anno concentrato e anni con meno di 100 trade. Smentita: R positivo in più della metà degli anni con almeno 100 trade.
7. *Riscaldamento lungo.* 365 giorni tolgono il primo anno di ogni moneta: restano soprattutto le monete vecchie. Prevede quota della moneta più presente alta per le monete del 2020. Smentita: trade diffusi.
8. *Volatilità.* Vicino al massimo la volatilità è alta; stop in ATR larghi. Prevede R compresso. Smentita: R netto positivo.
9. *Pochi trade estremi.* Prevede che le prove degli estremi cadano. Smentita: superate.
10. *Sopravvivenza.* Le monete vive nel 2023 hanno avuto massimi seguiti da altri massimi. Prevede (a) long positiva. Smentita: sopra la (a) e la (b).
11. *Costi e funding.* Vicino al massimo il funding è alto: il long paga per 30 giorni. Prevede R netto molto sotto il lordo. Smentita: R netto positivo.

**6. Ipotesi completa.** Tutte le 80 monete; meccanismo: ancoraggio al massimo e reazione lenta; timeframe 1d (il
massimo di un anno si misura su candele giornaliere); direzione long (l'effetto della fonte riguarda il lato vicino
al massimo). Modulo `codice/i10_massimo_annuo.py`:
* **I-10-L** long: `{"direzione": "long", "finestra": 365, "quota": 0.95, "tenuta": 30, "atr": 14, "stop_atr": 3.0}`.
  365 giorni: le 52 settimane di una moneta che si scambia sempre; 95%: «vicino» al massimo; tenuta 30: un mese,
  l'orizzonte più corto della fonte (che tiene sei mesi: troppi per i trade minimi).

Previsione (al netto dei costi): R medio fra −0,10 e +0,15, `t` fra −1 e +1,5. Criterio di successo: candidato.

---

## I-11 — Moneta «lotteria» dopo un rialzo estremo di un giorno

**1. Fonte.** Turan G. Bali, Nusret Cakici, Robert F. Whitelaw, «Maxing out: Stocks as lotteries and the
cross-section of expected returns», Journal of Financial Economics 99(2), febbraio 2011: i titoli con il rendimento
giornaliero massimo del mese più alto (simili a biglietti della lotteria) sono sopravvalutati e rendono meno nel
mese dopo.

**2. Affermazione verificabile.** Una moneta che negli ultimi 30 giorni ha avuto un rendimento giornaliero oltre 5
volte la mediana dei suoi rendimenti assoluti degli ultimi 90 giorni rende, nei 30 giorni dopo, meno del caso. Per
il gruppo: lo short aperto in quella condizione e tenuto 30 giorni ha R medio sopra la (b) e la (a). La fonte
confronta titoli fra loro; qui il confronto è con la stessa moneta nel tempo (la (b) entra a caso sulla stessa
moneta), perché le classifiche fra monete sono vietate (regole.md, sezione 3, punto 3).

**Perché su monete diverse per la stessa ragione.** La preferenza per la lotteria è degli investitori al dettaglio:
un rialzo estremo attira compratori che pagano troppo, su qualunque moneta.

**3. Sotto-domande.** Il calo arriva in giorni o in settimane? Vale di più per le monete piccole? Chi opera:
investitori al dettaglio che comprano dopo il rialzo, chi vende loro.

**4-5. Spiegazioni concorrenti.**
1. *Effetto casuale.* Prevede `t` vicino a 0. Smentita: `t` sopra la soglia.
2. *È solo il mercato (BTC e trend comune).* I rialzi estremi arrivano nei mercati in rialzo, che continuano: lo short perde con il mercato. Prevede R per anno opposto al buy and hold, (b) short vicina. Smentita: batte nettamente la (b).
3. *Una sola scommessa ripetuta.* I rialzi estremi cadono negli stessi giorni (rialzi generali). Prevede pavimento delle sfasate alto. Smentita: batte nettamente con il pavimento.
4. *Momento invece di lotteria (I-01, I-03).* Il rialzo estremo continua. Prevede `t` negativo. Smentita: `t` positivo.
5. *Volatilità.* Dopo un rialzo estremo l'ATR è grande, lo stop lontano, R compresso. Prevede R vicino a 0. Smentita: R netto positivo.
6. *Funding.* Dopo un rialzo il funding è alto: lo short lo incassa. Prevede R dal funding, prezzo neutro. Smentita: R lordo del funding positivo (Fase 3).
7. *Pochi trade estremi.* Pochi crolli grandi fanno la media. Prevede che le prove degli estremi cadano. Smentita: superate.
8. *Trend di fondo del periodo.* Il 2022 favorisce ogni short. Prevede R positivo solo nel 2022. Smentita: R positivo in più della metà degli anni con almeno 100 trade.
9. *Soglia relativa.* Con la mediana dei rendimenti assoluti come riferimento, le monete calme fanno scattare la condizione con rialzi piccoli. Prevede segnali concentrati su monete calme. Smentita: trade diffusi.
10. *Sopravvivenza.* Le monete vive nel 2023 sono quelle che dopo un rialzo estremo non sono crollate fino a morire: lo short è sfavorito dall'elenco. Prevede (b) short negativa. (Da dichiarare: è un limite, non una spiegazione da smentire.)
11. *Costi.* Spread larghi dopo i rialzi estremi. Prevede vantaggio che non regge a costi doppi. Smentita: Fase 4.

**6. Ipotesi completa.** Tutte le 80 monete; meccanismo: sopravvalutazione da preferenza per la lotteria;
timeframe 1d (la fonte usa il massimo giornaliero del mese); direzione short. Modulo
`codice/i11_massimo_lotteria.py`:
* **I-11-S** short: `{"direzione": "short", "finestra": 30, "finestra_rif": 90, "multiplo": 5.0, "tenuta": 30,
  "atr": 14, "stop_atr": 3.0}`. 30 giorni: il mese della fonte; riferimento sulla mediana dei 90 giorni della stessa
  moneta (unità valida per ogni moneta); 5 volte la mediana: un giorno estremo per quella moneta; tenuta 30: il mese
  dopo, come la fonte.

Previsione (al netto dei costi): R medio fra −0,10 e +0,10, `t` fra −1,5 e +1. Criterio di successo: candidato.

---

## I-12 — Ritracciamento breve dentro il trend lungo

**1. Fonte.** Larry Connors, Cesar Alvarez, «Short Term Trading Strategies That Work», TradingMarkets Publishing,
2008: comprare quando l'RSI a 2 giorni è molto basso e il prezzo è sopra la media di 200 giorni, uscire alla
chiusura sopra la media di 5 giorni.

**2. Affermazione verificabile.** Dentro un trend lungo al rialzo (chiusura sopra la media di 200 giorni), un
ritracciamento di due giorni (RSI a 2 sotto 10) è seguito da un rimbalzo; l'uscita alla prima chiusura sopra la
media di 5 giorni lo raccoglie. Per il gruppo: l'R medio di questi long supera la (b) e la (a); lo short simmetrico
(sotto la media di 200, RSI a 2 sopra 90, uscita sotto la media di 5) idem.

**Perché su monete diverse per la stessa ragione.** Il rimbalzo viene da chi vende per paura in un mercato che sta
salendo (o compra per euforia in uno che scende) e da chi fornisce liquidità: comportamenti degli investitori, non
della moneta.

**3. Sotto-domande.** Il rimbalzo è più forte quando il ritracciamento è più profondo? Quanti giorni dura? Lo
stop a 3 ATR è troppo stretto per un ritracciamento? Chi opera: chi vende i cali brevi, chi li compra.

**4-5. Spiegazioni concorrenti.**
1. *Effetto casuale.* Prevede `t` vicino a 0. Smentita: `t` sopra la soglia.
2. *È solo il mercato (BTC e trend comune).* Ritracciamenti e rimbalzi sono del mercato intero. Prevede (b) vicina. Smentita: batte nettamente la (b).
3. *Una sola scommessa ripetuta.* Ritracciamenti negli stessi giorni su tutte le monete. Prevede pavimento delle sfasate alto. Smentita: batte nettamente con il pavimento.
4. *Il calo continua (momento a breve, I-03).* Prevede `t` negativo. Smentita: `t` positivo.
5. *Uscita asimmetrica.* L'uscita alla media di 5 giorni chiude presto i guadagni e tiene le perdite fino allo stop: molti piccoli guadagni e poche grandi perdite. Prevede percentuale di trade vincenti alta e R medio vicino a 0. Smentita: R netto positivo.
6. *Riscaldamento lungo.* 200 giorni tolgono i primi mesi: restano le monete vecchie e gli anni dopo il 2020. Prevede quota della moneta più presente alta. Smentita: trade diffusi.
7. *Trend di fondo del periodo.* Il filtro della media di 200 sceglie gli anni di rialzo per il long e il 2022 per lo short. Prevede R per anno con il segno del buy and hold. Smentita: R positivo in più della metà degli anni con almeno 100 trade.
8. *Volatilità.* Prevede R compresso dagli stop larghi. Smentita: R netto positivo.
9. *Costi.* Durate brevi (pochi giorni). Prevede costo in R piccolo ma R lordo atteso anch'esso piccolo. Smentita: R netto positivo.
10. *Pochi trade estremi.* Prevede che le prove degli estremi cadano. Smentita: superate.
11. *La regola è nata sulle azioni.* Sulle crypto il ritracciamento non rientra perché manca chi fornisce liquidità. Prevede `t` vicino a 0. Smentita: `t` positivo.

**6. Ipotesi completa.** Tutte le 80 monete; meccanismo: rimbalzo dopo un ritracciamento breve nel trend lungo;
timeframe 1d (la regola è giornaliera); una variante per direzione. Modulo `codice/i12_rsi2.py`:
* **I-12-L** long: `{"direzione": "long", "periodo_rsi": 2, "rsi_soglia": 10, "media_lunga": 200,
  "media_corta": 5, "atr": 14, "stop_atr": 3.0}`. I numeri del libro: RSI a 2, soglia 10, medie di 200 e 5; uscita
  alla prima chiusura oltre la media di 5; stop di emergenza a 3 ATR (il libro non ne usa).
* **I-12-S** short: gli stessi parametri con `"direzione": "short"` (simmetrica: il libro tratta soprattutto il
  long).

Previsione (al netto dei costi): long R medio fra −0,05 e +0,08, `t` fra −1 e +1,5; short R medio fra −0,08 e +0,05,
`t` fra −1,5 e +1. Criterio di successo: candidato.

---

## I-17 — Cambio di mese

**1. Fonte.** Josef Lakonishok, Seymour Smidt, «Are Seasonal Anomalies Real? A Ninety-Year Perspective», Review of
Financial Studies 1(4), 1988: i rendimenti dall'ultimo giorno di borsa del mese ai primi tre del mese dopo sono più
alti del resto del mese.

**2. Affermazione verificabile.** Dall'apertura dell'ultimo giorno del mese all'apertura del quarto giorno del mese
dopo il rendimento è più alto del caso. Per il gruppo: il long tenuto in quei quattro giorni ha R medio sopra la (b)
e la (a). Si smentisce con `t` non positivo o non netto.

**Perché su monete diverse per la stessa ragione.** Se l'effetto viene da flussi di denaro legati al calendario
(stipendi, versamenti mensili, ribilanciamenti di fine mese), tocca tutte le monete insieme.

**3. Sotto-domande.** Le crypto hanno flussi mensili come le azioni (piani di acquisto periodici)? L'effetto è nei
primi giorni o nell'ultimo? Chi opera: investitori con versamenti periodici, fondi che ribilanciano.

**4-5. Spiegazioni concorrenti.**
1. *Effetto casuale.* Prevede `t` vicino a 0. Smentita: `t` sopra la soglia.
2. *È solo il mercato (BTC e trend comune).* Prevede (a) e (b) vicine. Smentita: batte nettamente la (b).
3. *Una sola scommessa ripetuta.* Tutte le monete entrano lo stesso giorno: una scommessa al mese, circa 36 in costruzione. Prevede pochi blocchi interi, pavimento delle sfasate alto, forse non valutabile. Smentita: valutabile e netta.
4. *Effetto delle azioni, non delle crypto.* Nessun flusso mensile nelle crypto. Prevede `t` vicino a 0. Smentita: `t` positivo.
5. *Trend di fondo.* Prevede R per anno con il segno del buy and hold. Smentita: sopra la (a) in più della metà degli anni.
6. *Pochi mesi estremi.* Pochi cambi di mese con rialzi enormi. Prevede che la prova sui giorni cada. Smentita: superata.
7. *Volatilità.* Prevede R compresso. Smentita: R netto positivo.
8. *Costi e funding.* Quattro giorni di tenuta: costi piccoli in R. Prevede R netto vicino al lordo. (Controllo, non spiegazione.)
9. *Artefatto del calendario.* Il mese UTC delle candele può non coincidere con quello dei flussi (fusi orari). Prevede nessun effetto. Smentita: effetto presente.
10. *Sopravvivenza.* Prevede (a) positiva. Smentita: sopra la (a).
11. *Scadenze dei futures trimestrali e delle opzioni (fine mese).* Movimenti legati alle scadenze, non ai flussi. Prevede effetto solo nei mesi di scadenza trimestrale. Smentita: effetto in tutti i mesi (lettura in Fase 3).

**6. Ipotesi completa.** Tutte le 80 monete; meccanismo: flussi di calendario a cavallo del mese; timeframe 1d;
direzione long. Modulo `codice/i17_inizio_mese.py`:
* **I-17-L** long: `{"direzione": "long", "tenuta": 4, "atr": 14, "stop_atr": 3.0}`. Ultimo giorno più i primi
  tre, come la fonte.

Previsione (al netto dei costi): R medio fra −0,05 e +0,08, `t` fra −1 e +1; rischio di non valutabile per pochi
blocchi (tutte le monete negli stessi giorni). Criterio di successo: candidato.

---

## I-07 — La moneta che resta indietro rispetto a un movimento forte di BTC

**1. Fonte.** Dimitrios Koutmos, «Return and volatility spillovers among cryptocurrencies», Economics Letters 173,
dicembre 2018: gli shock di rendimento passano dal bitcoin alle altre crypto, e il bitcoin è la fonte principale
del contagio.

**2. Affermazione verificabile.** Quando BTC fa in un'ora un movimento oltre 2 deviazioni standard delle ultime 168
ore e la moneta in quella stessa ora ne ha fatto meno della metà, nelle 4 ore dopo la moneta recupera nella
direzione di BTC. Per il gruppo: il long (BTC in su, moneta indietro) tenuto 4 ore ha R medio sopra la (b) e la (a);
lo short simmetrico idem.

**Perché su monete diverse per la stessa ragione.** L'informazione comune arriva prima sul mercato più liquido (BTC)
e poi, con un ritardo dovuto all'attenzione e agli arbitraggisti, sulle alt: vale per ogni alt meno liquida di BTC,
cioè per tutte quelle del gruppo.

**3. Sotto-domande.** Quanto dura il ritardo: minuti (allora a 1 ora è già sparito) o ore? Vale di più per le monete
piccole (slippage 0,10%)? Chi opera: arbitraggisti fra BTC e alt, investitori lenti. Quando: entro poche ore.

**4-5. Spiegazioni concorrenti.**
1. *Effetto casuale.* Prevede `t` vicino a 0. Smentita: `t` sopra la soglia.
2. *È solo il mercato, prima forma.* La moneta segue BTC anche dopo: se BTC continua, la moneta guadagna senza ritardo da recuperare. Prevede: risultato simile per monete che hanno seguito e per quelle indietro (lettura in Fase 3). Smentita: batte nettamente la (b).
3. *È solo il mercato, seconda forma: una sola scommessa ripetuta.* Il segnale scatta nella stessa ora su molte monete (lo shock di BTC è uno solo). Prevede uscite massime in un giorno altissime, effetto grappolo e pavimento delle sfasate alti. Smentita: batte nettamente con il pavimento.
4. *Il ritardo è già sparito in un'ora.* Gli arbitraggisti chiudono la distanza in minuti. Prevede `t` vicino a 0. Smentita: `t` positivo.
5. *Inversione di BTC.* Dopo un'ora estrema BTC torna indietro e la moneta che non l'ha seguito aveva ragione. Prevede `t` negativo. Smentita: `t` positivo.
6. *Moneta indietro per un motivo suo.* La moneta non segue perché ha una notizia propria opposta. Prevede `t` negativo. Smentita: `t` positivo.
7. *Costi.* A 1 ora lo stop a 2 ATR è di circa il 2-3% e un giro costa 0,2-0,3%: circa 0,1 R. Prevede R lordo positivo e netto negativo. Smentita: R netto positivo e regge a costi doppi.
8. *Volatilità.* Le ore estreme di BTC sono ore di volatilità alta: stop in ATR larghi. Prevede R compresso. Smentita: R netto positivo.
9. *Artefatto dei dati.* Barre mancanti di BTC o della moneta in quell'ora. Prevede segnali solo dove le serie hanno buchi (esclusi dal codice: servono barre contigue). Controllo, non spiegazione.
10. *Pochi trade estremi.* Pochi crolli di marzo 2020 o maggio 2021. Prevede che le prove sui giorni cadano. Smentita: superate.
11. *Trend di fondo.* Prevede R per anno legato al buy and hold. Smentita: R positivo in più della metà degli anni con almeno 100 trade.

**6. Ipotesi completa.** Tutte le 80 monete; meccanismo: diffusione lenta da BTC alle alt; timeframe 1h (il
ritardo è di ore al massimo: 1 ora è il timeframe ammesso più vicino che non sia dominato dai costi come 15 e 30
minuti); una variante per direzione. Modulo `codice/i07_ritardo_btc.py`:
* **I-07-L** long: `{"direzione": "long", "finestra": 168, "soglia_dev": 2.0, "frazione": 0.5, "tenuta": 4,
  "atr": 14, "stop_atr": 2.0}`. 168 ore: una settimana per la deviazione di BTC; 2 deviazioni: un'ora estrema;
  metà del movimento: la moneta è «indietro»; tenuta 4 ore; stop a 2 ATR (a 1 ora 3 ATR sarebbero quasi sempre
  oltre il movimento atteso).
* **I-07-S** short: gli stessi parametri con `"direzione": "short"`.

Previsione (al netto dei costi): R medio fra −0,12 e +0,05, `t` fra −1 e +1,5. Criterio di successo: candidato.

---

## I-19 — Inversione del rendimento proprio della moneta, al netto di BTC

**1. Fonte.** Zhi Da, Qianqiu Liu, Ernst Schaumburg, «A Closer Look at the Short-Term Return Reversal», Management
Science 60(3), marzo 2014: l'inversione a breve termine è forte nella parte del rendimento che non viene dal
mercato (il residuo), quella spinta da pressione di liquidità e non da notizie comuni.

**2. Affermazione verificabile.** Quando la moneta, nelle ultime 24 ore, è scesa molto più di quanto spiega il
movimento di BTC (residuo con z sotto −2), nelle 24 ore dopo il residuo rientra. Per il gruppo: il long aperto così
e tenuto 6 barre da 4 ore ha R medio sopra la (b) e la (a); lo short simmetrico idem.

**Perché su monete diverse per la stessa ragione.** Una vendita propria di una moneta senza una notizia comune
(liquidazioni sulla moneta, uscite di un grande detentore) chiede liquidità e paga un prezzo che poi rientra: il
meccanismo è nei partecipanti, non nella moneta. Togliere la parte di BTC lascia solo questa pressione.

**3. Sotto-domande.** Quanto dura il rientro? Vale anche quando il residuo è una notizia vera (non si può sapere)?
Più per le monete piccole? Chi opera: chi vende per forza, chi fornisce liquidità.

**4-5. Spiegazioni concorrenti.**
1. *Effetto casuale.* Prevede `t` vicino a 0. Smentita: `t` sopra la soglia.
2. *È solo il mercato, prima forma.* Togliere BTC non basta: il residuo è il trend comune delle alt (che non sta in BTC). Prevede (b) vicina. Smentita: batte nettamente la (b).
3. *È solo il mercato, seconda forma: una sola scommessa ripetuta.* Residui negativi per molte alt insieme (le alt che scendono più di BTC in un giorno di vendite sulle alt). Prevede pavimento delle sfasate alto. Smentita: batte nettamente con il pavimento.
4. *Notizia propria vera.* Il residuo è informazione e continua. Prevede `t` negativo. Smentita: `t` positivo.
5. *Beta instabile.* Il beta di 30 giorni sbaglia e il residuo è rumore del modello. Prevede `t` vicino a 0. Smentita: `t` positivo.
6. *Volatilità.* Dopo un residuo estremo l'ATR è alto: R compresso. Prevede R vicino a 0. Smentita: R netto positivo.
7. *Costi.* A 4 ore lo stop a 2 ATR è di circa il 5% e un giro costa 0,2-0,3%: circa 0,05 R. Prevede vantaggio lordo che regge appena. Smentita: R netto positivo e regge a costi doppi.
8. *Funding.* Dopo un crollo proprio il funding diventa negativo e il long incassa. Prevede guadagno dal funding. Smentita: R lordo positivo.
9. *Pochi trade estremi.* Prevede che le prove degli estremi cadano. Smentita: superate.
10. *Trend di fondo.* Prevede R per anno legato al buy and hold. Smentita: R positivo in più della metà degli anni con almeno 100 trade.
11. *Artefatto dei dati.* Buchi nelle serie: il codice vuole tutte le coppie contigue, quindi i buchi tolgono segnali e non li creano. Controllo, non spiegazione.

**6. Ipotesi completa.** Tutte le 80 monete; meccanismo: rientro della pressione di liquidità propria della moneta;
timeframe 4h (24 ore in 6 barre: abbastanza barre per stimare il residuo, costi in R ancora piccoli); una variante
per direzione. Modulo `codice/i19_residuo.py`:
* **I-19-L** long: `{"direzione": "long", "orizzonte": 6, "finestra_beta": 180, "soglia_z": 2.0, "tenuta": 6,
  "atr": 14, "stop_atr": 2.0}`. Orizzonte 6 barre = 24 ore, come il rendimento giornaliero della fonte (che usa
  rendimenti settimanali o mensili delle azioni: per le crypto un giorno è l'orizzonte a cui la liquidità rientra);
  beta su 180 barre = 30 giorni, stimato prima del movimento; tenuta 24 ore; stop a 2 ATR.
* **I-19-S** short: gli stessi parametri con `"direzione": "short"`.

Previsione (al netto dei costi): long R medio fra −0,05 e +0,08, `t` fra −1 e +2; short R medio fra −0,08 e +0,05,
`t` fra −1,5 e +1. Criterio di successo: candidato.
