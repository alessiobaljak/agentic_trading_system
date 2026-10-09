# FTMUSDT — ipotesi (Fase 1)

Ogni idea è scritta qui PRIMA del suo primo test, con tutte le sue varianti. Le idee
nuove vengono da fonti pubblicate prima del 2024-01-01; nessuna viene da risultati del
gate, del registro, del paper o di altre monete.

## Definizioni comuni (valgono per tutte le varianti)

* Barre: candele del last price sul timeframe della variante, allineate al mark con
  `carica_serie_allineate`; ogni indicatore alla barra i usa solo le barre 0..i (chiuse).
* ATR(n): media semplice degli ultimi n true range (max(high, close precedente) −
  min(low, close precedente)).
* Ingresso all'apertura della barra dopo il segnale (motore). Lo stop si calcola dal
  close della barra di segnale.
* «Uscita a tempo dopo N barre»: alla chiusura della barra in cui la posizione è aperta
  da N barre la variante chiede «chiudi» e il motore esce all'apertura successiva.
* Filtro della Fase 0: nessun segnale su barre di mesi sotto la liquidità minima
  (`fase0_dati.md`), uguale per variante, conta dei trade e baseline (a); quelle barre
  sono vietate alla (b).
* Costo di un giro (andata e ritorno): commissioni 0,05% + slippage 0,05% per lato =
  0,20% del nozionale. In R vale 0,20% / distanza dello stop in percentuale.
* Tetto del bot: uno stop oltre il 6% del prezzo il bot non lo esegue
  (`stop_massimo_bot`); le varianti con stop in ATR su candele lente lo superano spesso,
  e questo si dichiara: il motore non lo impone.

Spiegazioni concorrenti «noiose» che valgono per tutte le idee e non si ripetono per
intero in ogni idea (ogni idea ne aggiunge di sue, fino ad almeno 10):

* C1 **Caso**: l'effetto è rumore. Previsione: il `t` contro la (b) sta fra −2 e 2 e
  l'R medio per anno cambia segno. Smentita: «netta» contro la (b) con R positivo in
  più anni.
* C2 **È solo il mercato** (FTM segue BTC e il trend delle crypto). Previsione: le
  entrate casuali nella stessa direzione (b) guadagnano quanto la variante; l'R dei
  trade è correlato al rendimento di BTC nello stesso intervallo. Smentita: la variante
  batte nettamente la (b) e la correlazione con BTC non spiega la differenza.
* C3 **Trend di fondo** (2021 rialzo forte, 2022 ribasso forte). Previsione: un long
  guadagna nel 2021 e perde nel 2022 come le entrate casuali; la (b) assorbe l'effetto.
  Smentita: R sopra la (b) in entrambi gli anni.
* C4 **Volatilità**: la condizione seleziona solo momenti più volatili; in R questo
  non dà vantaggio di per sé, ma cambia l'esposizione ai costi e agli stop. Previsione:
  R simile alla (b), più dispersione. Smentita: R sopra la (b) anche nei sottoinsiemi
  a volatilità simile.
* C5 **Effetto costi**: un vantaggio lordo piccolo sparisce con 0,20% a giro.
  Previsione: R lordo positivo, netto vicino a zero. Smentita: R netto positivo anche a
  costi doppi.
* C6 **Artefatto dei dati** (buchi del mark, barre tolte, candele anomale del 2020).
  Previsione: il risultato dipende da pochi trade vicini a buchi o a candele estreme.
  Smentita: senza i 3 trade migliori l'R resta sopra la (b).
* C7 **Errore di codice / sguardo al futuro**. Previsione: risultato troppo bello e
  crollo col ritardo di una barra. Smentita: il controllo positivo degli strumenti
  passa e il ritardo peggiora gradualmente.
* C8 **Pochi trade estremi**. Previsione: senza i 3 migliori l'R medio scende sotto la
  (b). Smentita: resta sopra.

---

## I-01 — Momento della serie temporale (settimane)

**Fonti.** Tobias J. Moskowitz, Yao Hua Ooi, Lasse Heje Pedersen, «Time Series
Momentum», Journal of Financial Economics 104(2), maggio 2012. Yukun Liu, Aleh
Tsyvinski, «Risks and Returns of Cryptocurrency», NBER Working Paper 24877, agosto 2018
(poi Review of Financial Studies, 2021): nelle crypto il rendimento delle ultime 1-4
settimane predice quello delle successive 1-4 settimane.

**Affermazione verificabile.** Su FTMUSDT, se il rendimento delle ultime 14 candele
giornaliere è positivo (negativo), un long (short) aperto all'apertura del giorno dopo e
tenuto 5 giorni ha R medio dopo i costi più alto delle entrate casuali nella stessa
direzione con la stessa uscita (baseline b) e della stessa regola senza condizione
(baseline a). Falsificabile: `t` contro la (b) ≤ 2 o R medio ≤ 0.

**Sotto-domande.** Vale di più quando il movimento delle 14 giornate è grande (molto
oltre la volatilità)? Vale in rialzo e in ribasso allo stesso modo (le due direzioni
sono varianti separate)? Chi compra dopo un rialzo di due settimane: investitori al
dettaglio che inseguono il prezzo (attenzione, notizie, social), trend follower
sistematici; chi vende dopo un ribasso: liquidazioni a catena, uscite dei fondi. Il
tempo: la fonte parla di 1-4 settimane; 5 giorni sono la parte iniziale dell'effetto.

**Spiegazioni concorrenti** (oltre a C1-C8):

* C9 **Momento = trend del periodo**: nel 2021 FTM è salita tanto che qualunque long
  guadagna, nel 2022 qualunque short. Previsione: la variante long fa bene solo nel
  2021, la short solo nel 2022, come la (b). Smentita: battere la (b) anno per anno.
* C10 **Ritorno verso la media a 5 giorni** (l'opposto): dopo due settimane forti
  arriva una pausa. Previsione: R sotto la (b). Smentita: R sopra la (b).
* C11 **Effetto dello stop largo**: con 2,5 ATR giornalieri lo stop scatta raramente e
  l'esito è quasi solo l'uscita a tempo; il risultato misura il rendimento a 5 giorni,
  non lo stop. Previsione: pochi stop. Da dichiarare, non smentisce nulla.
* C12 **Funding**: dopo un rialzo il funding è alto e il long lo paga. Previsione: R
  lordo sopra la (b) ma netto no. Smentita: R netto sopra la (b).

**Ipotesi.** FTMUSDT, momento di 2 settimane, timeframe 1d (il meccanismo è in
settimane; 1d è il timeframe più vicino ammesso), una direzione per variante.

**Varianti** (due, una per direzione; massimo due per fonte):

* **I-01-L** (1d, long): condizione close(i)/close(i−14) − 1 > 0; stop = close −
  2,5 × ATR(14); nessun target; uscita a tempo dopo 5 barre. Perché: 14 giorni = due
  settimane, il centro dell'orizzonte della fonte; 5 giorni di tenuta lasciano almeno
  ~70 ingressi in 851 giorni di costruzione; lo stop è di emergenza (il meccanismo è a
  tempo), largo per non trasformare l'idea in un'altra.
* **I-01-S** (1d, short): condizione close(i)/close(i−14) − 1 < 0; stop = close +
  2,5 × ATR(14); uscita a tempo dopo 5 barre.

Nota: stop di 2,5 ATR giornalieri su FTM supera quasi sempre il 6% del bot: se diventa
candidato, il bot non lo esegue così com'è.

---

## I-02 — Rottura del canale di Donchian

**Fonte.** Curtis M. Faith, «Way of the Turtle», McGraw-Hill, 2007 (Sistema 1 delle
Tartarughe: ingresso sulla rottura del massimo di 20 periodi, uscita sulla rottura
opposta di 10 periodi, stop a 2 N con N = ATR di 20 periodi).

**Affermazione verificabile.** Su FTMUSDT a 4 ore, un close sopra il massimo dei 20
high precedenti apre un long che, con uscita sul close sotto il minimo dei 10 low
precedenti e stop a 2 ATR(20), ha R medio dopo i costi più alto della (a) e della (b).
Lo specchio per lo short.

**Sotto-domande.** Funziona solo quando il range precedente è stretto (compressione) o
sempre? Chi entra sulla rottura: ordini stop di chi era corto, trend follower, ordini
di acquisto sopra i massimi; la continuazione dipende dal fatto che questi ordini
arrivino a ondate. In quanto tempo: le uscite su 10 barre a 4 ore danno tenute di
qualche giorno.

**Spiegazioni concorrenti** (oltre a C1-C8):

* C9 **Falsa rottura**: sulle crypto le rotture sono spesso cacce agli stop seguite da
  rientro. Previsione: molti stop e R sotto la (b). Smentita: R sopra la (b).
* C10 **Rottura = trend del periodo**: i long sulle rotture guadagnano solo nel 2021.
  Previsione: R per anno uguale per segno alla (b). Smentita: sopra la (b) nei due anni.
* C11 **Asimmetria delle uscite**: l'uscita sui 10 low lascia correre i guadagni e
  taglia le perdite, cosa che dà R positivi anche con entrate casuali in trend.
  Previsione: la (b), che ha la stessa uscita, guadagna quasi quanto la variante.
  Smentita: differenza netta con la (b).
* C12 **Ritardo dell'ingresso**: entrando all'apertura dopo il close di rottura si
  paga già parte del movimento. Previsione: R peggiore con il ritardo di una barra.
* C13 **Volatilità crescente**: le rotture arrivano quando la volatilità sale, e l'ATR
  di 20 barre è ancora basso: stop troppo stretto rispetto al nuovo regime. Previsione:
  molti stop nelle prime barre.

**Ipotesi.** FTMUSDT, rottura del canale, timeframe 4h: il sistema originale è
giornaliero, ma con 851 giorni di costruzione le rotture di 20 giorni sono poche decine
per direzione; il meccanismo (ordini accumulati oltre gli estremi di un range) non
dipende dalla durata della candela, quindi si usa 4h, dove il range di 20 barre copre
3,3 giorni. Scelta fatta prima di qualunque conteggio, per il numero di trade atteso
della fonte, non per il risultato.

**Varianti:**

* **I-02-L** (4h, long): condizione close(i) > max(high(i−20..i−1)); stop = close −
  2 × ATR(20); nessun target; uscita: close(i) < min(low(i−10..i−1)) → chiudi.
* **I-02-S** (4h, short): condizione close(i) < min(low(i−20..i−1)); stop = close +
  2 × ATR(20); uscita: close(i) > max(high(i−10..i−1)) → chiudi.

**Aggiunta dopo la stima dei trade** (2026-10-09, prima di qualunque test di I-02): le
due varianti a 4h sono scarti (62 trade ciascuna, sotto 70: log FTMUSDT-003 e 004).
Regola 6: allentare uno scarto per raggiungere il minimo, senza aver visto risultati di
quell'idea, è ancora una variante dell'idea nuova. Si scende di un timeframe, con la
stessa regola in barre (il meccanismo non dipende dalla durata della candela, sopra):

* **I-02-L2** (2h, long): come I-02-L, su candele da 2 ore (range di 20 barre = 40 ore).
* **I-02-S2** (2h, short): come I-02-S, su candele da 2 ore.

Restano due varianti testate per la fonte (le due a 4h non sono state testate).

---

## I-03 — Ritorno dopo un movimento estremo (offerta di liquidità)

**Fonti.** Bruce N. Lehmann, «Fads, Martingales, and Market Efficiency», Quarterly
Journal of Economics 105(1), febbraio 1990. Stefan Nagel, «Evaporating Liquidity»,
Review of Financial Studies 25(7), luglio 2012: il ritorno a breve è il compenso di chi
offre liquidità e cresce quando la volatilità è alta.

**Affermazione verificabile.** Su FTMUSDT a 1 ora, dopo un movimento delle ultime 3 ore
più ampio di 3 deviazioni standard (calcolate sui rendimenti a 1 ora degli ultimi 30
giorni, scalati per radice di 3), una posizione nella direzione opposta tenuta 6 ore ha
R medio dopo i costi più alto della (a) e della (b).

**Sotto-domande.** Chi muove il prezzo: liquidazioni forzate dei perpetui a leva,
vendite di panico, notizie. Se è un flusso forzato (liquidazioni), il prezzo torna; se è
informazione (notizia vera), non torna. Quanto dura: la fonte azionaria dice giorni o
settimane; sulle crypto a leva le cascate di liquidazioni si esauriscono in ore.
Condizioni: più forte quando tutto il mercato è in vendita (liquidità scarsa)?

**Spiegazioni concorrenti** (oltre a C1-C8):

* C9 **Informazione**: il movimento estremo porta una notizia e continua. Previsione:
  R sotto la (b), stop frequenti. Smentita: R sopra la (b).
* C10 **Rimbalzo meccanico del rumore** (bid-ask bounce): sui close a 1 ora l'effetto
  è minimo con slippage 0,05%. Previsione: il guadagno lordo è di pochi decimi di
  punto e sparisce coi costi. Smentita: R netto sopra la (b).
* C11 **Movimento di BTC**: l'estremo di FTM è un estremo di tutto il mercato, e il
  rimbalzo è il rimbalzo di BTC. Previsione: R correlato al rimbalzo di BTC; la
  variante non aggiunge nulla al mercato. Da riportare come contesto.
* C12 **Volatilità dopo l'estremo**: dopo un movimento grande la volatilità resta
  alta e lo stop in ATR, calcolato su 24 barre, è troppo stretto. Previsione: molti
  stop nelle prime ore.
* C13 **Grappoli**: gli estremi arrivano a gruppi negli stessi giorni (marzo 2020 non
  c'è, ma maggio 2021, giugno 2022, novembre 2022 sì per tutto il mercato — lo dicono i
  dati del 2021-2022, che sono in costruzione); pochi giorni fanno il risultato.
  Previsione: R per anno instabile, molto peso nei 3 trade migliori.

**Ipotesi.** FTMUSDT, ritorno dopo l'estremo, timeframe 1h (il meccanismo delle
liquidazioni è in ore), una direzione per variante.

**Varianti:**

* **I-03-L** (1h, long): z = ln(close(i)/close(i−3)) / (dev. std dei rendimenti
  logaritmici a 1 ora delle ultime 720 barre × √3); condizione z < −3; stop = close −
  2 × ATR(24); nessun target; uscita a tempo dopo 6 barre.
* **I-03-S** (1h, short): condizione z > +3; stop = close + 2 × ATR(24); uscita a
  tempo dopo 6 barre.

---

## I-04 — Funding estremo come segnale di posizioni affollate

**Fonte.** Maik Schmeling, Andreas Schrimpf, Karamfil Todorov, «Crypto Carry», BIS
Working Papers n. 1087, aprile 2023: il carry delle crypto (premio dei futures e
funding dei perpetui) riflette la domanda di leva di investitori che inseguono il trend,
e un carry alto si accompagna a un rischio di crollo (liquidazioni dei long) più alto.

**Affermazione verificabile.** Su FTMUSDT a 8 ore, quando l'ultimo funding pubblicato
è nel decimo più alto degli ultimi 90 giorni ed è sopra 0,01% (il tasso di base),
uno short aperto alla barra dopo e tenuto 3 barre (24 ore) ha R medio dopo i costi (con
il funding incassato) più alto della (a) e della (b). Specchio: funding nel decimo più
basso e negativo → long.

**Sotto-domande.** Il funding alto anticipa il calo (posizioni affollate che si
sciolgono) o accompagna solo un trend che continua? Chi muove il prezzo: i long a leva
che pagano funding e chiudono, o vengono liquidati. Quando: il funding si regola ogni 8
ore, la pressione si dovrebbe vedere in uno o due giorni.

**Spiegazioni concorrenti** (oltre a C1-C8):

* C9 **Funding alto = trend forte che continua**: Previsione: R sotto la (b) per lo
  short. Smentita: sopra la (b).
* C10 **Solo il funding incassato**: lo short guadagna il funding, non il prezzo.
  Previsione: R lordo di prezzo ≈ (b), il vantaggio è il funding (piccolo in R con stop
  larghi). Da misurare separando il funding.
* C11 **Il funding segue il prezzo** (funding alto dopo rialzi): è un momento
  travestito. Previsione: la condizione coincide con rendimenti passati forti; stesso
  segno di I-01. Smentita: effetto anche a parità di rendimento passato.
* C12 **Pochi episodi**: i funding estremi arrivano a grappoli in poche settimane (fasi
  di euforia). Previsione: pochi blocchi, «non valutabile» o R instabile.
* C13 **Intervallo del funding**: se l'intervallo cambia (8h → 4h) il decimo più alto
  non è confrontabile. Da controllare in Fase 0.

**Ipotesi.** FTMUSDT, funding estremo contrario, timeframe 8h (allineato ai
settlement), una direzione per variante.

**Varianti:**

* **I-04-S** (8h, short): f = ultimo funding con settlement ≤ chiusura della barra i;
  condizione f > 0,0001 e f ≥ 90° percentile dei funding delle ultime 270
  settlement (90 giorni); stop = close + 2 × ATR(21); uscita a tempo dopo 3 barre.
* **I-04-L** (8h, long): condizione f < 0 e f ≤ 10° percentile delle ultime 270;
  stop = close − 2 × ATR(21); uscita a tempo dopo 3 barre.

---

## I-05 — Effetto del giorno della settimana (lunedì)

**Fonti.** Guglielmo Maria Caporale, Alex Plastun, «The day of the week effect in the
cryptocurrency market», Finance Research Letters 31, dicembre 2019. Doron Y. Aharon,
Mahmoud Qadan, «Bitcoin and the day-of-the-week effect», Finance Research Letters 31,
dicembre 2019: rendimenti del lunedì più alti degli altri giorni per bitcoin.

**Affermazione verificabile.** Su FTMUSDT, un long aperto all'apertura del lunedì (00:00
UTC) e chiuso all'apertura del martedì ha R medio dopo i costi più alto della (a) (long
ogni giorno con la stessa uscita) e della (b).

**Sotto-domande.** Perché il lunedì: riapertura dei mercati tradizionali e dei flussi
istituzionali dopo il fine settimana a bassa liquidità; notizie accumulate. Vale per
un'altcoin come per bitcoin? Vale in tutti gli anni o solo in uno?

**Spiegazioni concorrenti** (oltre a C1-C8):

* C9 **Data mining delle fonti**: le fonti hanno guardato 7 giorni; il lunedì è il
  migliore per caso su bitcoin in quel campione. Previsione: su FTM nessun effetto.
* C10 **Trend**: con un long di un giorno, il 2021 dà guadagni a ogni giorno.
  Previsione: R uguale alla (a). Smentita: netto sopra la (a).
* C11 **Volatilità del lunedì**: il lunedì è più volatile; in R non cambia nulla.
* C12 **Effetto BTC**: il lunedì di FTM è il lunedì di BTC. Contesto, non smentita.
* C13 **Fuso orario**: il «lunedì» delle fonti potrebbe essere in un altro fuso;
  00:00 UTC è domenica sera in America. Previsione: effetto più debole.

**Ipotesi.** FTMUSDT, lunedì, timeframe 1d, long. Una sola variante: la fonte indica una
direzione sola.

* **I-05-L** (1d, long): condizione: la barra i è una domenica (la barra dopo, in cui si
  entra, è il lunedì); stop = close − 2 × ATR(14); nessun target; uscita a tempo dopo 1
  barra (chiude all'apertura del martedì).

---

## I-06 — Rottura di volatilità della giornata (Williams)

**Fonte.** Larry Williams, «Long-Term Secrets to Short-Term Trading», Wiley, 1999: si
compra quando il prezzo supera l'apertura del giorno più una frazione del range del
giorno prima (rottura di volatilità), e si esce a fine giornata.

**Affermazione verificabile.** Su FTMUSDT a 1 ora, la prima barra della giornata UTC
che chiude sopra apertura del giorno + 0,5 × (high − low del giorno precedente) apre
un long che, chiuso all'apertura del giorno dopo (00:00 UTC) o allo stop, ha R medio
dopo i costi più alto della (a) e della (b). Specchio per lo short.

**Sotto-domande.** Il movimento iniziale di una giornata, quando è grande rispetto
alla volatilità recente, rivela un flusso (notizia, ordini grandi) che continua fino a
fine giornata? Vale di più nelle ore europee e americane? Chi muove: chi entra sulla
rottura, chi copre gli short.

**Spiegazioni concorrenti** (oltre a C1-C8):

* C9 **Esaurimento**: una rottura grande consuma il movimento della giornata; dopo si
  torna indietro. Previsione: R sotto la (b).
* C10 **Ora del giorno**: le rotture arrivano soprattutto in certe ore; la (b), con
  ingressi a ogni ora e uscita a fine giornata, ha tenute di durata diversa. La
  durata media la pareggia solo in parte. Da riportare.
* C11 **Uscita a fine giornata = tenuta breve**: con tenute di poche ore i costi pesano
  di più. Previsione: R lordo positivo, netto vicino a zero.
* C12 **Trend del periodo**: i long sulle rotture guadagnano nel 2021, gli short nel
  2022, come la (b).
* C13 **Il range del giorno prima è un cattivo metro**: dopo giorni piatti la soglia è
  bassa e scatta per rumore. Previsione: R peggiore dopo giorni di range piccolo.

**Ipotesi.** FTMUSDT, rottura di volatilità giornaliera, timeframe 1h (la regola vive
dentro la giornata: serve una candela più corta del giorno), una direzione per variante.

**Varianti:**

* **I-06-L** (1h, long): A = apertura della prima barra della giornata UTC; R = high −
  low del giorno UTC precedente (dalle sue barre a 1 ora); condizione close(i) > A +
  0,5 × R, nessuna barra precedente della stessa giornata ha chiuso sopra la soglia, e
  la barra i non è l'ultima della giornata (23:00); stop = close − 2 × ATR(24); uscita:
  alla chiusura della barra delle 23:00 → chiudi (esce alle 00:00).
* **I-06-S** (1h, short): specchio, close(i) < A − 0,5 × R; stop = close + 2 × ATR(24).

---

## I-07 — Ritorno di breve dentro il trend (RSI a 2)

**Fonte.** Larry Connors, Cesar Alvarez, «Short Term Trading Strategies That Work»,
TradingMarkets Publishing, 2008: si compra quando l'RSI a 2 periodi è sotto 10 e il
prezzo è sopra la media di 200 periodi, e si esce quando il close supera la media di 5
periodi; specchio per lo short.

**Affermazione verificabile.** Su FTMUSDT a 4 ore, con close sopra la media di 200
barre e RSI(2) < 10, un long chiuso al primo close sopra la media di 5 barre (o allo
stop) ha R medio dopo i costi più alto della (a) e della (b). Specchio: close sotto la
media di 200 e RSI(2) > 90 → short, uscita al primo close sotto la media di 5.

**Sotto-domande.** I cali brevi dentro un rialzo sono vendite di chi prende profitto
o di chi viene liquidato, assorbite da chi compra il trend? Quanto dura: la regola
esce di solito in poche barre. Vale anche contro il trend (lo short in un mercato
sopra la media)? Non qui: la fonte lega la direzione al trend.

**Spiegazioni concorrenti** (oltre a C1-C8):

* C9 **Coltello che cade**: sulle crypto i cali continuano (momento a breve).
  Previsione: R sotto la (b), molti stop.
* C10 **Uscita favorevole per costruzione**: uscire al primo close sopra la media di 5
  dà molti piccoli guadagni e poche grandi perdite; anche la (b) lo fa. Previsione: alta
  quota di vincenti sia per la variante sia per la (b); conta solo la differenza in R.
* C11 **Filtro del trend = trend del periodo**: sopra la media di 200 vuol dire 2021.
  Previsione: i long sono quasi tutti nel 2021.
* C12 **Asimmetria degli R**: pochi stop grandi possono cancellare molti piccoli
  guadagni; con poche decine di trade l'R medio è instabile.
* C13 **Costi**: guadagni piccoli (fino alla media di 5) contro un costo fisso per
  giro. Previsione: R lordo positivo, netto vicino a zero.

**Ipotesi.** FTMUSDT, ritorno dentro il trend, timeframe 4h (la fonte è giornaliera:
con 851 giorni i segnali giornalieri sono poche decine; 4h tiene la logica con una
media di 200 barre ≈ 33 giorni), una direzione per variante.

**Varianti:**

* **I-07-L** (4h, long): condizione close > media(200) e RSI(2) < 10; stop = close −
  3 × ATR(20) (di emergenza: la fonte non usa stop); uscita: close > media(5) → chiudi.
* **I-07-S** (4h, short): condizione close < media(200) e RSI(2) > 90; stop = close +
  3 × ATR(20); uscita: close < media(5) → chiudi.

---

## I-08 — Il grande guida il piccolo (BTC prima di FTM)

**Fonti.** Andrew W. Lo, A. Craig MacKinlay, «When Are Contrarian Profits Due to Stock
Market Overreaction?», Review of Financial Studies 3(2), 1990: i rendimenti dei titoli
grandi anticipano quelli dei piccoli (correlazione incrociata ritardata). Per le crypto:
Azhar Mohamad, Imtiaz Mohammad Sifat, Mohammad Syazwan Mohamed Shariff, «Lead-Lag
relationship between Bitcoin and Ethereum: Evidence from hourly and daily data»,
Research in International Business and Finance 50, 2019 (dati orari; trovano una
causalità in gran parte nei due versi, e poco margine per chi opera in giornata: la
fonte è debole e lo si dichiara).

**Affermazione verificabile.** Su FTMUSDT a 1 ora, quando nella barra appena chiusa
BTCUSDT è salito più di 2 deviazioni standard (dei suoi rendimenti a 1 ora delle
ultime 720 barre) e FTM è salito meno di BTC, un long su FTM tenuto 3 ore ha R medio
dopo i costi più alto della (a) e della (b). Specchio per lo short.

**Sotto-domande.** L'informazione di mercato arriva prima su BTC (più liquido, più
seguito) e poi sulle altcoin, con ore o minuti di ritardo? Se il ritardo è di minuti,
a 1 ora l'effetto è già sparito. Chi muove: arbitraggi fra monete, fondi che comprano
un paniere.

**Spiegazioni concorrenti** (oltre a C1-C8):

* C9 **Ritardo di minuti, non di ore**: Previsione: nessun effetto a 1 ora.
* C10 **FTM ha una sua notizia contraria**: se FTM non segue BTC è perché ha un motivo
  suo. Previsione: R sotto la (b).
* C11 **Rimbalzo di BTC**: dopo un salto di BTC, BTC torna indietro e FTM con lui.
  Previsione: R negativo e correlato al ritorno di BTC.
* C12 **Pochi eventi a grappolo**: i salti di BTC oltre 2 deviazioni standard arrivano
  nei giorni di notizie macro. Previsione: pochi blocchi.
* C13 **Il bot non ha BTC nella strategia**: un candidato richiederebbe i dati di un'altra
  moneta nel segnale. Non è una spiegazione, è un limite da dichiarare.

**Ipotesi.** FTMUSDT, BTC guida FTM, timeframe 1h (la fonte usa dati orari), una
direzione per variante. BTC entra solo come riferimento di mercato (barre del last di
BTCUSDT con lo stesso ts; se manca la barra di BTC non c'è segnale).

**Varianti:**

* **I-08-L** (1h, long): rb = rendimento logaritmico di BTC nella barra i, sb = dev.
  std dei rendimenti di BTC delle ultime 720 barre; rf = rendimento di FTM nella barra
  i; condizione rb > 2 × sb e rf < rb; stop = close − 2 × ATR(24); uscita a tempo
  dopo 3 barre.
* **I-08-S** (1h, short): condizione rb < −2 × sb e rf > rb; stop = close + 2 × ATR(24);
  uscita a tempo dopo 3 barre.

---

## I-09 — Compressione di volatilità e rottura (Bollinger)

**Fonte.** John Bollinger, «Bollinger on Bollinger Bands», McGraw-Hill, 2001 («the
Squeeze»: una larghezza delle bande ai minimi dei mesi precedenti annuncia
un'espansione della volatilità; la direzione la dà l'uscita dalle bande).

**Affermazione verificabile.** Su FTMUSDT a 4 ore, quando la larghezza delle bande
(20 barre, 2 deviazioni standard) della barra precedente è nel quinto più basso delle
ultime 120 barre e il close esce sopra la banda alta, un long chiuso al primo close
sotto la media di 20 (o allo stop) ha R medio dopo i costi più alto della (a) e della
(b). Specchio per lo short.

**Sotto-domande.** La volatilità bassa è un equilibrio fragile: quando si rompe, il
movimento è più grande e più persistente di una rottura qualunque? Chi muove: gli stop
accumulati sopra e sotto un range stretto, le opzioni (poche su FTM).

**Spiegazioni concorrenti** (oltre a C1-C8):

* C9 **È la rottura del canale (I-02) con un altro nome**: Previsione: stesso esito di
  I-02 nella stessa direzione.
* C10 **Falsa partenza**: dopo una compressione la prima uscita è spesso nella
  direzione sbagliata («head fake», lo dice la fonte stessa). Previsione: molti stop.
* C11 **L'uscita sulla media di 20 lascia correre**: come in I-02, la (b) con la stessa
  uscita guadagna quasi lo stesso.
* C12 **Pochi segnali**: compressione + uscita sono rari a 4 ore. Previsione: vicino
  al minimo di 70 trade, pochi blocchi.
* C13 **Volatilità che riprende in tutto il mercato**: la compressione è di tutto il
  mercato, non di FTM. Contesto con BTC.

**Ipotesi.** FTMUSDT, compressione e rottura, timeframe 4h (la fonte è giornaliera con
circa 6 mesi di confronto; a 4 ore 120 barre = 20 giorni, per avere segnali sufficienti
in 851 giorni), una direzione per variante.

**Varianti:**

* **I-09-L** (4h, long): bw = 4 × dev. std(20) / media(20); condizione bw(i−1) ≤ 20°
  percentile di bw nelle 120 barre fino a i−1 e close(i) > media(20) + 2 × dev. std(20);
  stop = close − 2 × ATR(20); uscita: close < media(20) → chiudi.
* **I-09-S** (4h, short): stessa compressione e close(i) < media(20) − 2 × dev.
  std(20); stop = close + 2 × ATR(20); uscita: close > media(20) → chiudi.

**Aggiunta dopo la stima dei trade** (2026-10-09, prima di qualunque test di I-09): a 4h
sono scarti (43 e 39 trade: log FTMUSDT-016 e 017). Allentamento della regola 6, senza
risultati di questa idea: stessa regola in barre su candele da 2 ore (bande di 20 barre
= 40 ore, confronto su 120 barre = 10 giorni).

* **I-09-L2** (2h, long) e **I-09-S2** (2h, short): come I-09-L e I-09-S, a 2 ore.

---

## I-10 — Premio del perpetuo sul mark price

**Fonte.** Songrun He, Asaf Manela, Omri Ross, Victor von Wachter, «Fundamentals of
Perpetual Futures», arXiv 2212.06888, prima versione dicembre 2022: il prezzo dei
perpetui si scosta dal prezzo di non arbitraggio (lo spot) più che nelle valute
tradizionali; il funding lo richiama verso lo spot, e una strategia che sfrutta lo
scostamento rende molto anche con costi alti.

**Affermazione verificabile.** Su FTMUSDT a 1 ora, quando il premio del last sul mark
price (close del last / close del mark − 1) è positivo e nel centesimo più alto delle
ultime 720 barre, uno short tenuto 4 ore ha R medio dopo i costi più alto della (a) e
della (b): il perpetuo torna verso il prezzo di riferimento scendendo. Specchio: premio
negativo nel centesimo più basso → long.

**Sotto-domande.** Il mark price di Binance segue l'indice spot (con una correzione per
il premio): un last molto sopra il mark vuol dire acquisti a leva sul perpetuo più
veloci dello spot. Il ritorno avviene col perpetuo che scende o con lo spot che sale?
Solo il primo dà guadagno allo short. In quanto tempo: ore.

**Spiegazioni concorrenti** (oltre a C1-C8):

* C9 **Lo spot raggiunge il perpetuo**: il premio si chiude con lo spot che sale (il
  perpetuo era in anticipo). Previsione: R sotto la (b) per lo short.
* C10 **Artefatto del mark**: il mark price è una media e ritarda; in una barra di
  forte rialzo il close del last è sopra il mark solo per costruzione. Allora il
  premio è un momento travestito. Previsione: la condizione coincide con barre di forte
  rialzo; stesso segno di I-03-S.
* C11 **Buchi del mark**: le barre con mark anomalo (prima dei buchi) danno premi
  enormi e falsi. Previsione: segnali concentrati vicino ai buchi dichiarati in Fase 0.
* C12 **Funding**: il premio alto alza il prossimo funding, che lo short incassa: in
  4 ore cade al più un settlement. Effetto piccolo.
* C13 **Grappoli**: premi estremi a grappoli nei giorni euforici.

**Ipotesi.** FTMUSDT, premio del perpetuo, timeframe 1h, una direzione per variante.

**Varianti:**

* **I-10-S** (1h, short): p = close last / close mark − 1; condizione p > 0 e p ≥
  99° percentile delle ultime 720 barre; stop = close + 2 × ATR(24); uscita a tempo dopo
  4 barre.
* **I-10-L** (1h, long): condizione p < 0 e p ≤ 1° percentile delle ultime 720 barre;
  stop = close − 2 × ATR(24); uscita a tempo dopo 4 barre.

---

## I-11 — Momento dentro la giornata (prima mezz'ora → ultima mezz'ora)

**Fonte.** Dehua Shen, Andrew Urquhart, Pengfei Wang, «Bitcoin intraday time-series
momentum», Financial Review 57(2), maggio 2022 (manoscritto accettato settembre 2021):
il rendimento della prima mezz'ora della giornata predice quello dell'ultima mezz'ora;
gli autori lo attribuiscono all'offerta di liquidità. La fonte definisce la giornata con
il volume (il mercato non chiude); qui la giornata è quella UTC, e lo si dichiara.

**Affermazione verificabile.** Su FTMUSDT a 30 minuti, se il rendimento della prima
mezz'ora della giornata UTC (00:00-00:30) è positivo, un long aperto alle 23:30 e chiuso
alle 00:00 ha R medio dopo i costi più alto della (a) e della (b). Specchio per lo short.

**Sotto-domande.** Chi muove l'ultima mezz'ora: chi riequilibra a fine giornata (fondi
con valutazione giornaliera alle 00:00 UTC), chi chiude posizioni di giornata. Perché
la prima mezz'ora conterrebbe l'informazione: notizie della notte asiatica, flussi
d'apertura. Il movimento atteso in 30 minuti è dello stesso ordine dei costi (sezione
11, «Costi a orizzonte corto»): serve un effetto grande.

**Spiegazioni concorrenti** (oltre a C1-C8):

* C9 **Costi**: con una tenuta di 30 minuti il costo di un giro (0,20%) è circa un
  decimo di R con stop di 2 ATR a 30 minuti. Previsione: R netto negativo anche con un
  effetto lordo vero.
* C10 **Effetto solo su bitcoin**: la fonte studia bitcoin; su un'altcoin i flussi di
  fine giornata sono diversi. Previsione: nessun effetto.
* C11 **Giornata UTC diversa da quella della fonte**: Previsione: effetto più debole.
* C12 **Rumore a 30 minuti**: R per trade molto dispersi; i blocchi sono molti (un
  trade al giorno), quindi l'errore è stimato bene: qui il caso si vede.
* C13 **Funding alle 00:00**: l'uscita coincide con un settlement; il motore lo conta
  solo se è un costo (momento ambiguo). Effetto piccolo ma sistematico contro il long
  in funding positivo.

**Ipotesi.** FTMUSDT, momento dentro la giornata, timeframe 30m (la regola è in mezz'ore),
una direzione per variante.

**Varianti:**

* **I-11-L** (30m, long): condizione: la barra i è quella delle 23:00 (si entra alle
  23:30) e close(barra 00:00 dello stesso giorno) > open(stessa barra); stop = close −
  2 × ATR(48); uscita a tempo dopo 1 barra.
* **I-11-S** (30m, short): rendimento della prima mezz'ora negativo; stop = close + 2 ×
  ATR(48); uscita a tempo dopo 1 barra.

---

## I-12 — Rendimento per rischio più alto quando la volatilità è bassa

**Fonte.** Alan Moreira, Tyler Muir, «Volatility-Managed Portfolios», Journal of Finance
72(4), agosto 2017: la volatilità a breve si prevede, il rendimento atteso no; quindi il
rendimento per unità di rischio è più alto quando la volatilità recente è bassa.

**Affermazione verificabile.** Su FTMUSDT, un long aperto all'apertura del giorno dopo
che la volatilità realizzata degli ultimi 30 giorni è sotto la sua mediana degli
ultimi 180 giorni, tenuto 5 giorni con stop in ATR, ha R medio dopo i costi (cioè
rendimento per unità di rischio) più alto della (a) e della (b).

**Sotto-domande.** Su una crypto, la volatilità bassa è calma prima del movimento o
assenza di interesse? Le fasi di alta volatilità del 2021-2022 sono crolli e bolle:
i rendimenti per unità di rischio peggiori? Il long è l'unica direzione della fonte
(il premio per il rischio è di chi tiene l'attività).

**Spiegazioni concorrenti** (oltre a C1-C8):

* C9 **Premio per il rischio assente nelle crypto**: senza un premio medio positivo non
  c'è nulla da riscalare. Previsione: R vicino a zero come la (b).
* C10 **Volatilità bassa = mercato laterale**: in laterale il long a 5 giorni non va da
  nessuna parte. Previsione: R vicino a zero, pochi stop.
* C11 **Volatilità bassa prima dei crolli**: la calma del 2022 precede crolli
  (maggio, novembre). Previsione: R negativo nel 2022.
* C12 **Lo stop in ATR riscala già il rischio**: in R anche la (b) è riscalata per
  volatilità; la condizione aggiunge solo la scelta dei periodi. Previsione: differenza
  piccola.
* C13 **Trend del 2021**: i periodi a volatilità bassa del 2021 cadono in rialzo.

**Ipotesi.** FTMUSDT, volatilità bassa, timeframe 1d (la fonte è mensile, il meccanismo
è lento; 1d è il timeframe più lungo ammesso), long. Una variante: la fonte dà una
direzione sola.

* **I-12-L** (1d, long): vol30 = dev. std dei rendimenti logaritmici giornalieri degli
  ultimi 30 giorni; condizione vol30 < mediana di vol30 negli ultimi 180 giorni; stop =
  close − 2,5 × ATR(14); uscita a tempo dopo 5 barre.

---

## I-13 — Incrocio di medie mobili

**Fonti.** William Brock, Josef Lakonishok, Blake LeBaron, «Simple Technical Trading
Rules and the Stochastic Properties of Stock Returns», Journal of Finance 47(5), dicembre
1992 (regole di medie mobili 1-50, 1-150, 5-150, 1-200). Robert Hudson, Andrew Urquhart,
«Technical trading and cryptocurrencies», Annals of Operations Research 297, 2021
(online 2019): le stesse famiglie di regole su bitcoin e altre crypto.

**Affermazione verificabile.** Su FTMUSDT a 4 ore, quando la media di 10 barre incrocia
verso l'alto quella di 50, un long chiuso all'incrocio opposto (o allo stop) ha R medio
dopo i costi più alto della (a) e della (b). Specchio per lo short.

**Sotto-domande.** È lo stesso meccanismo di I-01 e I-02 (trend), con un'uscita diversa:
il trend è persistente abbastanza da superare i falsi incroci? Il rischio principale è
che non aggiunga nulla alle altre idee di trend: lo dirà il confronto.

**Spiegazioni concorrenti** (oltre a C1-C8):

* C9 **Falsi incroci in laterale**: molte piccole perdite. Previsione: quota di vincenti
  bassa e R dipendente da pochi trade lunghi (C8).
* C10 **Stesso effetto di I-02**: Previsione: segno del risultato uguale a I-02 nella
  stessa direzione.
* C11 **L'uscita sull'incrocio opposto lascia correre**: la (b) con la stessa uscita
  guadagna quasi uguale.
* C12 **Ritardo delle medie**: l'incrocio arriva tardi, dopo gran parte del movimento.
  Previsione: R negativo dopo i costi.
* C13 **Trend del periodo**: long nel 2021, short nel 2022.

**Ipotesi.** FTMUSDT, incrocio di medie, timeframe 4h (con 851 giorni le regole
giornaliere della fonte danno pochi incroci; 10 e 50 barre a 4 ore ≈ 1,7 e 8,3 giorni),
una direzione per variante.

**Varianti:**

* **I-13-L** (4h, long): condizione media(10)(i) > media(50)(i) e media(10)(i−1) ≤
  media(50)(i−1); stop = close − 3 × ATR(20); uscita: media(10) < media(50) → chiudi.
* **I-13-S** (4h, short): incrocio verso il basso; stop = close + 3 × ATR(20); uscita:
  media(10) > media(50) → chiudi.

---

## I-14 — Movimenti con volume alto che tornano indietro

**Fonte.** John Y. Campbell, Sanford J. Grossman, Jiang Wang, «Trading Volume and Serial
Correlation in Stock Returns», Quarterly Journal of Economics 108(4), novembre 1993: i
movimenti di prezzo accompagnati da volume alto tendono a invertirsi (pressione di
liquidità di chi deve scambiare), quelli con volume basso molto meno.

**Affermazione verificabile.** Su FTMUSDT a 1 giorno, dopo un giorno con rendimento
sotto −1 deviazione standard (rendimenti degli ultimi 60 giorni) e volume (in moneta)
oltre 1,5 volte la media dei 30 giorni precedenti, un long tenuto 2 giorni ha R medio
dopo i costi più alto della (a) e della (b).

**Sotto-domande.** Il volume alto in un giorno di calo è vendita forzata (liquidazioni,
fondi in uscita) o informazione (molti che sanno qualcosa)? La fonte dice che nel primo
caso il prezzo torna. Su un'altcoin le notizie proprie sono frequenti (C9). Tempo: la
fonte usa rendimenti giornalieri e settimanali.

**Spiegazioni concorrenti** (oltre a C1-C8):

* C9 **Informazione**: il volume alto accompagna una notizia; il calo continua.
* C10 **È I-03 su un altro orizzonte**: stesso segno di I-03-L. Contesto.
* C11 **Mercato**: i giorni di calo con volume alto sono giorni di calo di tutto il
  mercato; il rimbalzo è di BTC.
* C12 **Pochi eventi**: condizioni doppie su 1d danno poche decine di segnali: forse
  sotto 70 (scarto).
* C13 **Volume in moneta**: con il prezzo che cambia molto, il volume in FTM e in USDT
  non coincidono; la regola usa il volume in moneta della candela (Candela.volume),
  confrontato con i 30 giorni precedenti, dove il prezzo cambia meno.

**Ipotesi.** FTMUSDT, inversione dopo volume alto, timeframe 1d, long (la fonte parla di
inversione in entrambi i versi; si prova il verso del calo, quello delle vendite
forzate). Una variante.

* **I-14-L** (1d, long): r = rendimento logaritmico del giorno; condizione r < −1 ×
  dev. std(r, 60 giorni) e volume(i) > 1,5 × media(volume, 30 giorni precedenti);
  stop = close − 2 × ATR(14); uscita a tempo dopo 2 barre.

---

## I-15 — Ordini di stop oltre i numeri tondi (cascate dopo l'attraversamento)

Scritta il 9 ottobre 2026 dopo aver visto i risultati delle varianti 1-13 (nessuna netta
contro la (b)); l'idea viene da una fonte e da una famiglia di meccanismi non ancora
toccata (struttura degli ordini), non dai risultati.

**Fonti.** Carol L. Osler, «Currency Orders and Exchange Rate Dynamics: An Explanation
for the Predictive Success of Technical Analysis», Journal of Finance 58(5), ottobre
2003: gli ordini di take profit si raccolgono sui numeri tondi, gli stop loss appena
oltre; quindi i trend rallentano o si invertono ai numeri tondi e accelerano dopo averli
attraversati. Carol L. Osler, «Stop-loss orders and price cascades in currency markets»,
Journal of International Money and Finance 24(2), 2005: dopo l'attraversamento di un
livello tondo il prezzo si muove più in fretta nella stessa direzione.

**Affermazione verificabile.** Su FTMUSDT a 1 ora, quando il close attraversa verso
l'alto un numero tondo (passo = 10^(⌊log10 prezzo⌋ − 1): 0,01 sotto 1 USDT, 0,1 da 1 a 10)
che il close precedente non aveva superato, un long tenuto 3 ore ha R medio dopo i costi
più alto della (a) e della (b). Specchio per lo short.

**Sotto-domande.** Su FTM, mercato con molti piccoli operatori, gli stop si mettono
davvero oltre i tondi (0,50, 1,00, 2,00)? I tondi «forti» (1,00) contano più di quelli
deboli (0,47)? Qui il passo li tratta allo stesso modo: si dichiara. Tempo: le cascate
della fonte durano minuti o ore.

**Spiegazioni concorrenti** (oltre a C1-C8):

* C9 **Il tondo non conta su FTM**: Previsione: R come la (b).
* C10 **Take profit al tondo successivo**: il movimento si ferma al prossimo tondo.
  Previsione: guadagni piccoli, mangiati dai costi.
* C11 **Il passo cambia con il prezzo**: sotto 1 USDT il passo dello 0,01 vale 1-10%;
  sopra 1 USDT il passo dello 0,1 vale 3-10%: attraversamenti più rari sopra 1.
  Contesto da riportare per anno.
* C12 **Ogni attraversamento è un momento a 1 ora**: la condizione seleziona barre in
  salita. Previsione: stesso segno del momento a breve; la (b) non lo cattura.
* C13 **Il close attraversa ma il movimento era già avvenuto dentro la barra**: si
  entra dopo la cascata. Previsione: R peggiore, sensibile al ritardo.

**Ipotesi.** FTMUSDT, attraversamento dei numeri tondi, timeframe 1h, una direzione per
variante.

* **I-15-L** (1h, long): passo P = 10^(⌊log10 close(i−1)⌋ − 1); L = il più piccolo
  multiplo di P strettamente sopra close(i−1); condizione close(i) ≥ L; stop = close −
  2 × ATR(24); uscita a tempo dopo 3 barre.
* **I-15-S** (1h, short): L = il più grande multiplo di P strettamente sotto close(i−1)
  (o uguale a close(i−1) se ne è un multiplo, escluso); condizione close(i) ≤ L; stop =
  close + 2 × ATR(24); uscita a tempo dopo 3 barre.
