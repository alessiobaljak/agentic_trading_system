# ETCUSDT — ipotesi (Fase 1)

Scritto prima di qualunque test, il 9 ottobre 2026. Ogni idea ha la sua fonte (pubblicata prima del
2024-01-01), l'affermazione falsificabile, le sotto-domande, almeno 10 spiegazioni concorrenti con la
previsione che fanno e cosa le smentirebbe, l'ipotesi completa e tutte le sue varianti. I numeri dei
trade di ogni variante li dà `conta_trade` e stanno nel log (registrazione o scarto).

## Regole comuni a tutte le varianti (fissate prima del primo test)

* Moneta ETCUSDT, perpetuo USDS-M; segnali sul last price, alla chiusura della barra; ingresso
  all'apertura della barra dopo (motore della sezione 7). Stop sul last, liquidazione sul mark.
* Dimensione e leva del bot: rischio 1% del capitale, leva massima 2, margine isolato (parametri.yaml).
* Costi: commissione 0,05% per lato, slippage 0,05% per lato (scheda della moneta), funding storico.
  Un giro completo costa circa lo 0,20% del nozionale: in R è 0,0020 / distanza dello stop. Con lo
  stop a 2 ATR: sul 4h (ATR tipico ~1,5-2,5%) circa 0,04-0,07 R; sull'1h (ATR ~0,7-1%) circa
  0,10-0,15 R; sull'1d con 1-1,5 ATR (ATR ~5-6%) circa 0,02-0,04 R. Le previsioni sono al netto.
* Stop: sempre in multipli dell'ATR di Wilder a 14 barre del timeframe del segnale, contato dal
  close della barra del segnale. Uno stop oltre il 6% (tetto del bot) il motore lo esegue e si
  dichiara: il bot non potrebbe eseguirlo così com'è.
* Uscita a tempo: «chiudi» alla chiusura della barra in cui la posizione ha raggiunto le barre
  massime, quindi uscita all'apertura della barra dopo.
* Mesi sotto la liquidità minima (Fase 0): nessun ingresso su segnali di quelle barre.
* Indicatori causali: il valore alla barra i usa solo le barre fino a i.
* Le varianti sono una direzione ciascuna. Massimo due varianti per fonte.

Le spiegazioni concorrenti «noiose» compaiono in ogni idea perché il protocollo le vuole per ogni
idea; dove la previsione è la stessa la si ripete in breve.

---

## I-01 — Momento della serie storica a una settimana

**Fonte.** T. J. Moskowitz, Y. H. Ooi, L. H. Pedersen, «Time Series Momentum», *Journal of Financial
Economics* 104(2), 2012 (online 2011). Per le crypto: Y. Liu, A. Tsyvinski, «Risks and Returns of
Cryptocurrency», NBER Working Paper 24877, agosto 2018 (poi *Review of Financial Studies* 2021): il
rendimento di una settimana predice positivamente quello delle settimane successive (1-4 settimane).

**Affermazione falsificabile.** Su ETCUSDT, quando il rendimento delle ultime 7 giornate (42 barre da
4 ore) è positivo, il rendimento delle 7 giornate successive, al netto dei costi, è più alto di quello
di un ingresso a caso nella stessa direzione con la stessa uscita (baseline (b)) e di un ingresso a ogni
barra libera (baseline (a)); simmetricamente per lo short quando è negativo.

**Sotto-domande.** Vale di più dopo movimenti grandi o piccoli? In alta o bassa volatilità? Chi compra
dopo un rialzo: chi insegue il prezzo (attenzione, notizie lente a diffondersi), chi copre short,
chi segue il trend con regole. L'effetto della letteratura è su orizzonti di 1-4 settimane: si
manifesta lentamente, non in ore. Dipende dal regime (2020-2021 rialzo, 2022 ribasso)?

**Spiegazioni concorrenti.**

| # | Spiegazione | Previsione | Cosa la smentisce |
|---|---|---|---|
| 1 | Effetto casuale | R medio entro il rumore della (b); `t` contro la (b) tra -2 e 2 | `t` > soglia, stabile negli anni |
| 2 | Trend di fondo del periodo (rialzo 2020-21) | Il long batte la (a) solo perché la (a) entra anche nei ribassi; contro la (b) (stessa direzione, entrate casuali) nulla | Battere la (b), che ha lo stesso trend |
| 3 | «È solo il mercato»: ETC segue BTC | Il segnale su ETC coincide col segnale su BTC; il vantaggio sparisce dove ETC e BTC divergono | Vantaggio anche quando il rendimento a 7 giorni di BTC ha segno opposto |
| 4 | Volatilità: dopo rialzi la volatilità sale e lo stop in ATR si allarga | R simile alla (b), diverso solo il numero di stop | R per trade migliore a parità di distanza dello stop |
| 5 | Pochi trade estremi (es. maggio 2021) | Senza i 3 migliori l'R medio crolla | R medio senza i 3 migliori ancora sopra la (b) |
| 6 | Un solo anno | R positivo in un anno solo | R sopra la (b) in più della metà degli anni |
| 7 | Effetto costi | Lordo positivo, netto nullo | R netto positivo con margine sui costi |
| 8 | Artefatto dei dati (buchi, barre tolte) | Trade concentrati vicino ai buchi | Nessuna concentrazione vicino ai buchi |
| 9 | Inversione a breve dentro la settimana (I-03) che annulla il momento | R positivo solo con uscite lunghe | Il profilo di R per durata non cambia segno |
| 10 | Funding: chi è long in rialzo paga funding alto | R lordo positivo mangiato dal funding | Funding totale piccolo rispetto all'R |
| 11 | Selezione della moneta (ETC sopravvissuta e liquida nel 2023) | Il long beneficia del fatto che la moneta non è morta | Non verificabile in-sample: limite dichiarato |

**Ipotesi.** ETCUSDT, momento a 7 giorni, timeframe 4h (il meccanismo è su orizzonti di giorni-settimane;
il 4h dà uno stop in ATR entro il tetto del bot e un segnale aggiornato più volte al giorno).

**Varianti.**
* **I-01-L** (long): ingresso se close / close di 42 barre prima − 1 > 0; stop 2 ATR(14) sotto il
  close; nessun target; uscita dopo 42 barre. Motivo: l'orizzonte tipico della letteratura (una
  settimana di segnale, una di tenuta).
* **I-01-S** (short): ingresso se lo stesso rendimento è < 0; stop 2 ATR sopra; uscita dopo 42 barre.
  Motivo: il momento è simmetrico nella fonte.

**Previsione (al netto).** Long: R medio fra −0,05 e +0,10, non netto contro la (b). Short: R medio fra
−0,10 e +0,05. Il mio priore è basso: il momento su una moneta sola e 3 anni è debole.

---

## I-02 — Rottura del canale di prezzo

**Fonte.** W. Brock, J. Lakonishok, B. LeBaron, «Simple Technical Trading Rules and the Stochastic
Properties of Stock Returns», *Journal of Finance* 47(5), 1992: la regola «trading range break»
(comprare quando il prezzo supera il massimo delle ultime n sedute e tenere 10 sedute) dà rendimenti
dopo i segnali di acquisto più alti di quelli dopo i segnali di vendita.

**Affermazione falsificabile.** Su ETCUSDT, dopo una chiusura oltre il massimo delle 50 barre da 4 ore
precedenti (circa 8 giorni), il rendimento delle 60 barre successive (10 giorni) è più alto di quello
della (a) e della (b); simmetricamente per lo short sotto il minimo.

**Sotto-domande.** Chi compra la rottura: chi aveva ordini stop sopra il massimo (short che si coprono),
chi segue il trend, chi guarda i massimi (ancoraggio). Vale di più se la rottura avviene con volume alto?
In quanto tempo: le liquidazioni degli short sono immediate, i seguaci del trend lenti.

**Spiegazioni concorrenti.**

| # | Spiegazione | Previsione | Cosa la smentisce |
|---|---|---|---|
| 1 | Effetto casuale | `t` contro la (b) entro ±2 | `t` oltre la soglia |
| 2 | Trend di fondo | Long buono solo nel 2020-21, short solo nel 2022 | Vantaggio contro la (b) in più anni |
| 3 | «È solo il mercato» (rotture insieme a BTC) | Il vantaggio è lo stesso di un ingresso casuale nelle settimane forti di BTC | Vantaggio anche nelle rotture di ETC senza rottura di BTC |
| 4 | Volatilità: le rotture arrivano con volatilità alta | Più stop presi, R medio come la (b) | R migliore della (b) che ha gli stessi stop |
| 5 | Falsa rottura (ritorno nel canale) | Molti stop subito dopo l'ingresso | Quota di stop nelle prime barre simile alla (b) |
| 6 | Pochi trade estremi | Senza i 3 migliori R ≤ (b) | Senza i 3 migliori ancora sopra |
| 7 | Costi e slippage alla rottura | Lordo positivo, netto nullo | Netto positivo |
| 8 | Artefatto dei dati (barre dopo un buco sembrano rotture) | Rotture subito dopo i buchi | Nessuna concentrazione |
| 9 | Sovrapposizione con il momento (I-01) | Stessi trade di I-01 | Trade diversi, risultato diverso |
| 10 | Un solo periodo (es. estate 2022, la «fusione» di Ethereum attesa) | R concentrato in pochi mesi | R distribuito |
| 11 | Funding alto dopo le rotture al rialzo | Costo di funding grande | Funding piccolo |

**Ipotesi.** ETCUSDT, rottura del massimo/minimo di 50 barre, timeframe 4h (la fonte è su sedute
giornaliere; 50 barre da 4h sono circa 8 giorni, il 4h tiene lo stop entro il tetto del bot).

**Varianti.**
* **I-02-L**: ingresso se close > massimo degli high delle 50 barre precedenti; stop 2 ATR sotto;
  uscita dopo 60 barre (10 giorni, come la fonte).
* **I-02-S**: ingresso se close < minimo dei low delle 50 barre precedenti; stop 2 ATR sopra; uscita
  dopo 60 barre.

**Previsione.** R medio fra −0,10 e +0,10 per entrambe; non netto.

---

## I-03 — Inversione dopo uno shock di un'ora (fornitura di liquidità)

**Fonte.** S. Nagel, «Evaporating Liquidity», *Review of Financial Studies* 25(7), 2012: i rendimenti
delle strategie di inversione a breve sono il compenso di chi fornisce liquidità, e crescono quando la
volatilità è alta. Anche N. Jegadeesh, «Evidence of Predictable Behavior of Security Returns»,
*Journal of Finance* 45(3), 1990.

**Affermazione falsificabile.** Su ETCUSDT, dopo una barra di 1 ora con rendimento sotto −3 deviazioni
standard (dei rendimenti orari dei 7 giorni precedenti), le 12 ore successive hanno rendimento più alto
della (a) e della (b) per un long; simmetricamente per lo short dopo +3.

**Sotto-domande.** Chi vende in quell'ora: liquidazioni a catena dei long con leva (nei perpetui sono
ordini a mercato forzati), stop a cascata, notizie. Chi compra dopo: market maker, arbitraggisti. Se è
pressione forzata il prezzo torna in ore; se è notizia, no. Vale di più se il volume è anomalo?

**Spiegazioni concorrenti.**

| # | Spiegazione | Previsione | Cosa la smentisce |
|---|---|---|---|
| 1 | Effetto casuale | `t` entro ±2 | `t` oltre la soglia |
| 2 | Notizia vera (continuazione, non inversione) | R medio negativo per il long | R positivo |
| 3 | Volatilità: dopo lo shock la volatilità resta alta e lo stop in ATR è largo | R come la (b) ma con meno stop | R migliore della (b) |
| 4 | Rimbalzo già all'apertura della barra dopo (il prezzo si riprende nei minuti) | Vantaggio sparisce col ritardo di una barra | Vantaggio anche col ritardo |
| 5 | «È solo il mercato»: shock di tutto il mercato | Rimbalzo uguale a quello di BTC | Rimbalzo di ETC oltre quello di BTC |
| 6 | Trend di fondo | Il long buono solo nel rialzo 2021 | Buono anche nel 2022 |
| 7 | Pochi trade estremi (marzo 2020) | Senza i 3 migliori crolla | Regge |
| 8 | Costi sull'1h (circa 0,1 R a giro) | Lordo positivo, netto nullo | Netto positivo |
| 9 | Artefatto: barre anomale dei dati (prezzi sbagliati, buchi) | Shock vicino ai buchi | Nessuna concentrazione |
| 10 | Liquidazioni sul mark (il mark non scende quanto il last) | Effetto diverso fra last e mark | Non controllabile qui: si dichiara |
| 11 | Funding | Effetto piccolo su 12 ore | — |

**Ipotesi.** ETCUSDT, inversione dopo shock orario, timeframe 1h (lo shock da liquidazioni si misura in
ore; il 15m costerebbe troppo).

**Varianti.**
* **I-03-L**: ingresso long se rendimento della barra < −3 × deviazione standard dei 168 rendimenti
  orari precedenti (barra esclusa); stop 2 ATR sotto; uscita dopo 12 barre.
* **I-03-S**: short se il rendimento > +3 deviazioni standard; stop 2 ATR sopra; uscita dopo 12 barre.

**Previsione.** Long: R medio fra −0,10 e +0,10; short: fra −0,15 e +0,05 (rialzi forti hanno meno
liquidazioni forzate). Non netto.

---

## I-04 — Giornate di reazione eccessiva: continuazione il giorno dopo

**Fonte.** G. M. Caporale, A. Plastun, «Price overreactions in the cryptocurrency market», *Journal of
Economic Studies* 46(5), 2019: dopo giornate di variazione anomala, nei giorni seguenti il prezzo tende
a muoversi nella stessa direzione (momento, non inversione) per BTC.

**Affermazione falsificabile.** Su ETCUSDT, dopo un giorno con rendimento oltre media + 1 deviazione
standard (dei 30 giorni precedenti), il giorno dopo ha rendimento più alto della (a) e della (b) per un
long; simmetricamente per lo short dopo un giorno sotto media − 1 deviazione.

**Sotto-domande.** Chi compra il giorno dopo: chi arriva tardi sulla notizia, chi insegue. Vale di più
dopo giornate estreme? In un giorno o meno?

**Spiegazioni concorrenti.**

| # | Spiegazione | Previsione | Cosa la smentisce |
|---|---|---|---|
| 1 | Effetto casuale | `t` entro ±2 | `t` oltre la soglia |
| 2 | Inversione (I-03) invece di continuazione | R negativo | R positivo |
| 3 | Trend di fondo | Long buono solo negli anni in rialzo | Buono in più anni |
| 4 | «È solo il mercato» | Giornate anomale di ETC = di BTC | Effetto anche nelle giornate solo di ETC |
| 5 | Volatilità | Più stop | R migliore a parità di stop |
| 6 | Pochi trade estremi | Senza i 3 migliori crolla | Regge |
| 7 | Costi | Netto nullo | Netto positivo |
| 8 | Artefatto del confine del giorno UTC | L'effetto dipende dall'ora di taglio | Non controllabile con candele 1d: si dichiara |
| 9 | Un solo episodio (maggio 2021, estate 2022) | R concentrato | R distribuito |
| 10 | Il risultato della fonte vale per BTC e non per ETC | Nessun effetto | — |

**Ipotesi.** ETCUSDT, continuazione dopo giornata anomala, timeframe 1d (la fonte è giornaliera).

**Varianti.**
* **I-04-L**: long se rendimento del giorno > media + 1 deviazione standard dei 30 rendimenti
  giornalieri precedenti; stop 1 ATR(14) sotto; uscita dopo 1 barra (un giorno).
* **I-04-S**: short se < media − 1 deviazione; stop 1 ATR sopra; uscita dopo 1 barra.
Soglia a 1 deviazione (non 2) per avere abbastanza giorni: con 30 giorni di finestra 1 deviazione
lascia circa un giorno su sei per lato.

**Previsione.** R medio fra −0,10 e +0,10; non netto.

---

## I-05 — Funding affollato

**Fonte.** S. He, A. Manela, O. Ross, V. von Wachter, «Fundamentals of Perpetual Futures», arXiv
2212.06888, dicembre 2022: il premio del perpetuo sullo spot (e il funding che lo segue) riflette la
domanda di leva; i premi estremi tornano verso zero e precedono rendimenti opposti.

**Affermazione falsificabile.** Su ETCUSDT, quando l'ultimo funding regolato è sopra lo 0,01% e nel 10%
più alto dei 90 funding precedenti (30 giorni), i 3 giorni successivi hanno rendimento per uno short più
alto della (a) e della (b); quando è negativo e nel 10% più basso, lo stesso per un long.

**Sotto-domande.** Chi paga il funding alto: long con leva, spesso in ritardo sul movimento. Chi è
dall'altra parte: arbitraggisti spot-perpetuo. Il premio si chiude con la discesa del perpetuo o con la
salita dello spot? In giorni o in ore?

**Spiegazioni concorrenti.**

| # | Spiegazione | Previsione | Cosa la smentisce |
|---|---|---|---|
| 1 | Effetto casuale | `t` entro ±2 | `t` oltre la soglia |
| 2 | Funding alto = momento forte (I-01): lo short perde | R negativo per lo short | R positivo |
| 3 | Trend di fondo | Short buono solo nel 2022 | Buono anche nel 2021 |
| 4 | «È solo il mercato» (funding alto ovunque insieme) | Effetto uguale a uno short a caso nei giorni di euforia | Effetto contro la (b) |
| 5 | Lo short incassa il funding e basta | R lordo di prezzo nullo, funding positivo | R di prezzo positivo |
| 6 | Volatilità | Più stop | R migliore a parità di stop |
| 7 | Pochi episodi | Trade a grappolo in poche settimane | Distribuiti |
| 8 | Artefatto del dato di funding (istante del settlement) | — | Dati controllati in Fase 0 |
| 9 | Costi | Netto nullo | Netto positivo |
| 10 | Pochi trade estremi | Senza i 3 migliori crolla | Regge |

**Ipotesi.** ETCUSDT, funding estremo, timeframe 8h (il funding si regola ogni 8 ore).

**Varianti.**
* **I-05-S**: short se l'ultimo funding regolato (istante ≤ chiusura della barra) è > 0,0001 e ≥ al 90°
  percentile dei 90 funding precedenti; stop 2 ATR(14, 8h) sopra; uscita dopo 9 barre (3 giorni).
* **I-05-L**: long se l'ultimo funding è < 0 e ≤ al 10° percentile dei 90 precedenti; stop 2 ATR
  sotto; uscita dopo 9 barre.

**Previsione.** R medio fra −0,10 e +0,10; il long probabilmente sotto i trade minimi.

---

## I-06 — Premio del volume alto

**Fonte.** S. Gervais, R. Kaniel, D. H. Mingelgrin, «The High-Volume Return Premium», *Journal of
Finance* 56(3), 2001: titoli con volume anomalo alto in un giorno (decile alto dei 50 precedenti) hanno
rendimenti più alti nelle settimane dopo (visibilità e attenzione); quelli con volume basso più bassi.

**Affermazione falsificabile.** Su ETCUSDT, quando il volume in USDT delle ultime 24 ore (6 barre da 4h)
è nel 10% più alto delle 300 finestre precedenti (50 giorni), i 5 giorni successivi hanno rendimento per
un long più alto della (a) e della (b); quando è nel 10% più basso, lo stesso per uno short.

**Sotto-domande.** Il volume alto arriva con rialzi o ribassi? Il premio dovrebbe essere indipendente
dal segno del rendimento (fonte). Chi compra dopo: nuovi partecipanti attratti dall'attenzione.

**Spiegazioni concorrenti.**

| # | Spiegazione | Previsione | Cosa la smentisce |
|---|---|---|---|
| 1 | Effetto casuale | `t` entro ±2 | `t` oltre la soglia |
| 2 | Volume alto = crollo in corso (capitolazione), poi altro ribasso | R negativo per il long | R positivo |
| 3 | Volume alto = rottura (I-02) | Stessi trade della rottura | Trade diversi |
| 4 | Trend di fondo | Buono solo nel 2021 | In più anni |
| 5 | «È solo il mercato» (volume alto ovunque) | Effetto come la (b) nei giorni di mercato agitato | Effetto contro la (b) |
| 6 | Volatilità | Più stop | R migliore a parità di stop |
| 7 | Pochi episodi | Concentrati | Distribuiti |
| 8 | Artefatto del volume (volumi gonfiati o cambi di contratto) | Picchi isolati senza prezzo | Controllo dei picchi |
| 9 | Costi | Netto nullo | Netto positivo |
| 10 | Pochi trade estremi | Senza i 3 migliori crolla | Regge |

**Ipotesi.** ETCUSDT, volume anomalo nelle 24 ore, timeframe 4h (volume su un giorno mobile, stop
entro il tetto del bot).

**Varianti.**
* **I-06-L**: long se il volume USDT delle ultime 6 barre è ≥ al 90° percentile delle stesse somme delle
  300 barre precedenti; stop 2 ATR sotto; uscita dopo 30 barre (5 giorni).
* **I-06-S**: short se ≤ al 10° percentile; stop 2 ATR sopra; uscita dopo 30 barre.

**Previsione.** R medio fra −0,10 e +0,10; non netto.

---

## I-07 — Squilibrio degli ordini aggressivi

**Fonte.** T. Chordia, A. Subrahmanyam, «Order imbalance and individual stock returns: Theory and
evidence», *Journal of Financial Economics* 72(3), 2004: lo squilibrio fra acquisti e vendite
aggressivi persiste (ordini spezzati) e predice positivamente il rendimento del periodo dopo.

**Affermazione falsificabile.** Su ETCUSDT, quando lo squilibrio dei taker in un'ora,
(acquisti taker − vendite taker) / volume, è nel 5% più alto delle 168 ore precedenti, le 6 ore dopo
hanno rendimento per un long più alto della (a) e della (b); nel 5% più basso, lo stesso per uno short.

**Sotto-domande.** Chi compra aggressivo: chi ha informazione o urgenza, e spezza l'ordine nel tempo.
Persistenza in minuti o ore? Lo squilibrio è già nel prezzo della barra?

**Spiegazioni concorrenti.**

| # | Spiegazione | Previsione | Cosa la smentisce |
|---|---|---|---|
| 1 | Effetto casuale | `t` entro ±2 | `t` oltre la soglia |
| 2 | Già nel prezzo (impatto immediato, poi inversione) | R negativo | R positivo |
| 3 | Persistenza solo in minuti | Vantaggio sparisce col ritardo | Regge col ritardo |
| 4 | «È solo il mercato» | Squilibrio insieme a BTC | Effetto oltre BTC |
| 5 | Trend di fondo | Buono in un anno solo | Più anni |
| 6 | Volatilità | Più stop | R migliore a parità di stop |
| 7 | Costi sull'1h | Netto nullo | Netto positivo |
| 8 | Artefatto: il campo dei taker manca o è sbagliato in alcuni mesi | Picchi di squilibrio nei mesi anomali | Controllo del campo |
| 9 | Liquidazioni (ordini forzati a mercato contano come taker) | Squilibrio estremo = liquidazioni, poi inversione (I-03) | R positivo |
| 10 | Pochi trade estremi | Senza i 3 migliori crolla | Regge |

**Ipotesi.** ETCUSDT, squilibrio dei taker, timeframe 1h (la persistenza dell'ordine spezzato è di ore).

**Varianti.**
* **I-07-L**: long se lo squilibrio della barra è ≥ al 95° percentile dei 168 precedenti; stop 2 ATR
  sotto; uscita dopo 6 barre.
* **I-07-S**: short se ≤ al 5° percentile; stop 2 ATR sopra; uscita dopo 6 barre.

**Previsione.** R medio fra −0,15 e +0,05; non netto.

---

## I-08 — Effetto del giorno della settimana (lunedì)

**Fonte.** G. M. Caporale, A. Plastun, «The day of the week effect in the cryptocurrency market»,
*Finance Research Letters* 31, 2019: per BTC rendimenti anomali positivi il lunedì.

**Affermazione falsificabile.** Su ETCUSDT un long tenuto dall'apertura del lunedì (UTC) all'apertura del
martedì ha rendimento più alto della (a) (un long in un giorno qualunque) e della (b).

**Sotto-domande.** Chi compra il lunedì: flussi istituzionali alla riapertura dei mercati tradizionali.
Vale per una moneta minore? È stabile negli anni?

**Spiegazioni concorrenti.**

| # | Spiegazione | Previsione | Cosa la smentisce |
|---|---|---|---|
| 1 | Effetto casuale (data mining di calendario della fonte) | `t` entro ±2 | `t` oltre la soglia |
| 2 | Trend di fondo | R simile alla (a) | Sopra la (a) |
| 3 | «È solo il mercato» | Se c'è, è di BTC | — |
| 4 | Un solo anno | R concentrato | Distribuito |
| 5 | Volatilità del lunedì più alta | Più stop | — |
| 6 | Pochi trade estremi | Crolla senza i 3 migliori | Regge |
| 7 | Costi | Netto nullo | Netto positivo |
| 8 | Artefatto del confine del giorno UTC | — | Non controllabile: si dichiara |
| 9 | Effetto del fine settimana (sabato-domenica) opposto | — | — |
| 10 | Effetto scomparso dopo la pubblicazione | Nessun effetto | — |

**Ipotesi.** ETCUSDT, lunedì, timeframe 1d.

**Variante.**
* **I-08-L**: long se la barra appena chiusa è una domenica (UTC); stop 1 ATR(14) sotto; uscita dopo
  1 barra.

**Previsione.** R medio fra −0,10 e +0,05; non netto (priore molto basso).

---

## I-09 — BTC guida, ETC segue in ritardo

**Fonte.** K. Hou, «Industry Information Diffusion and the Lead-lag Effect in Stock Returns», *Review of
Financial Studies* 20(4), 2007: le notizie comuni si diffondono prima nei titoli grandi e seguiti, poi
nei piccoli. Per le crypto: D. Koutmos, «Return and volatility spillovers among cryptocurrencies»,
*Economics Letters* 173, 2018 (BTC principale trasmettitore).

**Affermazione falsificabile.** Su ETCUSDT, dopo un'ora in cui BTC sale più di 2 deviazioni standard
(delle 168 ore precedenti) mentre ETC sale meno della metà di BTC, le 4 ore dopo hanno rendimento di ETC
per un long più alto della (a) e della (b); simmetricamente per lo short.

**Sotto-domande.** In quanto tempo ETC si allinea: minuti (allora alla barra dopo è già fatto) o ore? Chi
porta il prezzo: arbitraggisti fra monete, robot che seguono BTC.

**Spiegazioni concorrenti.**

| # | Spiegazione | Previsione | Cosa la smentisce |
|---|---|---|---|
| 1 | Effetto casuale | `t` entro ±2 | `t` oltre la soglia |
| 2 | Ritardo già chiuso entro l'ora | R come la (b) | R sopra la (b) |
| 3 | ETC è rimasta indietro per un motivo suo (debolezza propria) | R negativo | R positivo |
| 4 | Inversione di BTC che trascina ETC | R negativo | — |
| 5 | Trend di fondo | Buono in un anno solo | Più anni |
| 6 | Volatilità | Più stop | — |
| 7 | Costi sull'1h | Netto nullo | Netto positivo |
| 8 | Artefatto: barre di BTC mancanti allineate male | — | Allineamento per ts |
| 9 | Pochi trade estremi | Crolla senza i 3 migliori | Regge |
| 10 | «È solo il mercato» (qui è l'ipotesi stessa: si controlla che non sia un ingresso a caso nelle ore di BTC forte) | — | — |

**Ipotesi.** ETCUSDT, ritardo su BTC, timeframe 1h.

**Varianti.**
* **I-09-L**: long se rendimento orario di BTC > 2 deviazioni standard (168 ore precedenti di BTC) e
  rendimento orario di ETC < 0,5 × quello di BTC; stop 2 ATR sotto; uscita dopo 4 barre.
* **I-09-S**: short se BTC < −2 deviazioni e ETC > 0,5 × BTC (cioè scende meno della metà); stop 2 ATR
  sopra; uscita dopo 4 barre.

**Previsione.** R medio fra −0,15 e +0,05; non netto.

---

## I-10 — Compressione della volatilità, poi rottura (bande di Bollinger)

**Fonte.** J. Bollinger, *Bollinger on Bollinger Bands*, McGraw-Hill, 2001 (lo «squeeze»: la banda più
stretta da mesi precede un'espansione; la direzione la dà l'uscita dalle bande).

**Affermazione falsificabile.** Su ETCUSDT, quando la larghezza delle bande (4 deviazioni / media a 20)
ha toccato il minimo delle 120 barre precedenti nelle ultime 5 barre e il close esce sopra la banda
alta, le 30 barre da 4h dopo hanno rendimento per un long più alto della (a) e della (b);
simmetricamente sotto la banda bassa per lo short.

**Sotto-domande.** Chi muove dopo la compressione: ordini accumulati ai bordi del range, opzioni (poche
su ETC), seguaci del trend. Quanto dura l'espansione?

**Spiegazioni concorrenti.**

| # | Spiegazione | Previsione | Cosa la smentisce |
|---|---|---|---|
| 1 | Effetto casuale | `t` entro ±2 | `t` oltre la soglia |
| 2 | Falsa rottura | Molti stop presto | Stop come la (b) |
| 3 | La volatilità torna alla media ma senza direzione | R ≈ (b) | R sopra la (b) |
| 4 | Trend di fondo | Buono in un anno solo | Più anni |
| 5 | «È solo il mercato» | — | Effetto contro la (b) |
| 6 | Sovrapposizione con la rottura (I-02) | Stessi trade | Trade diversi |
| 7 | Stop stretto (ATR basso dopo la compressione) | Stop presi presto, costi in R alti | — |
| 8 | Costi | Netto nullo | Netto positivo |
| 9 | Pochi trade estremi | Crolla senza i 3 migliori | Regge |
| 10 | Artefatto dei buchi (barre piatte) | Compressioni false vicino ai buchi | Nessuna concentrazione |

**Ipotesi.** ETCUSDT, squeeze e rottura, timeframe 4h.

**Varianti.**
* **I-10-L**: long se min(larghezza delle ultime 5 barre) ≤ minimo delle 120 barre prima di esse e close >
  media(20) + 2 deviazioni(20); stop 2 ATR sotto; uscita dopo 30 barre.
* **I-10-S**: short, stesso squeeze e close < media(20) − 2 deviazioni(20); stop 2 ATR sopra; uscita dopo
  30 barre.

**Previsione.** R medio fra −0,10 e +0,10; probabile sotto i trade minimi.

---

## I-11 — Ipervenduto a due barre dentro il trend (RSI a 2)

**Fonte.** L. Connors, C. Alvarez, *Short Term Trading Strategies That Work*, TradingMarkets, 2009:
comprare quando l'RSI a 2 periodi è sotto 10 e il prezzo è sopra la media a 200, uscire quando il
close supera la media a 5 (vendere lo specchio).

**Affermazione falsificabile.** Su ETCUSDT a 4 ore, con close sopra la media a 200 barre e RSI(2) < 10,
il long fino al close sopra la media a 5 barre ha R più alto della (a) e della (b); lo specchio short con
close sotto la media a 200 e RSI(2) > 90.

**Sotto-domande.** Chi vende a fondo: chi esce in fretta su un calo breve dentro un trend. Il ritorno è
in barre. Vale di più nei trend forti?

**Spiegazioni concorrenti.**

| # | Spiegazione | Previsione | Cosa la smentisce |
|---|---|---|---|
| 1 | Effetto casuale | `t` entro ±2 | `t` oltre la soglia |
| 2 | Molti piccoli guadagni e rare grandi perdite (R asimmetrici) | Win rate alto, R medio nullo | R medio positivo con il pavimento dell'errore |
| 3 | Trend di fondo (il filtro della media a 200 sceglie il rialzo) | Batte la (a) ma non la (b) | Batte la (b) |
| 4 | Il calo è l'inizio di un'inversione del trend | Stop presi | — |
| 5 | Costi sul 4h con uscite rapide | Netto nullo | Netto positivo |
| 6 | Volatilità | — | — |
| 7 | «È solo il mercato» | Effetto come la (b) | Contro la (b) |
| 8 | Pochi trade estremi | Crolla senza i 3 migliori | Regge |
| 9 | Un solo anno | Concentrato | Distribuito |
| 10 | Il risultato della fonte è su azioni con inversione a breve; le crypto hanno più momento | Nessun effetto | — |

**Ipotesi.** ETCUSDT, RSI(2) estremo dentro il trend, timeframe 4h (la regola su candele giornaliere
non darebbe abbastanza ingressi in tre anni).

**Varianti.**
* **I-11-L**: long se close > media(200) e RSI(2) < 10; stop 3 ATR sotto (la fonte non usa stop: uno
  largo serve solo alla dimensione); uscita quando close > media(5), al più dopo 20 barre.
* **I-11-S**: short se close < media(200) e RSI(2) > 90; stop 3 ATR sopra; uscita quando close <
  media(5), al più dopo 20 barre.

**Previsione.** R medio fra −0,10 e +0,10; non netto.
