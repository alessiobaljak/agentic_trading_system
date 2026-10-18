# Ipotesi della campagna PANIERE

«Contaminazione dichiarata dal coordinamento (PROTOCOLLO_2, sezione 8, condizione 1): tre strategie intraday della prima edizione sono state giudicate nel vault 2024-2026 l'11 ottobre 2026; questa sessione non ha letto quei risultati né alcun dato dal 2024-01-01, e le idee e le varianti qui sotto sono quelle fissate nel testo prima di qualunque dato.»

## Premessa: cosa è già deciso e cosa no

Le tre idee, le loro fonti e le 18 varianti NON sono scelte di questa sessione: sono quelle della sezione 5 della
seconda edizione, ricopiate parola per parola in `regole.md`, sezione 7. Qui si fa la Fase 1 del protocollo (smontare
l'idea prima del test): affermazione falsificabile, sotto-domande, spiegazioni concorrenti con la loro previsione,
ipotesi completa e motivo di ogni variante. Le previsioni numeriche di ogni variante si scrivono nella sua
registrazione nel log, dopo la conta dei trade e prima del test.

Il terreno è uguale per tutte le varianti (`regole.md`, sezione 3; `config/parametri_2.yaml`, congelato):

* segnali sulle candele giornaliere UTC del last, chiuse; decisione alla chiusura del giorno `t`;
* ingresso con ordine limite al prezzo di chiusura del giorno `t`, valido il solo giorno `t+1`, eseguito se il
  minimo (long) o il massimo (short) del giorno dopo attraversa il prezzo; commissione maker 0,02%, scarto zero;
* stop iniziale a 2,5 ATR(20) dalla chiusura di segnale; uscite a mercato (stop, segnale all'apertura del giorno
  dopo, tempo dopo 60 barre); taker 0,05% più lo scarto della fascia della scheda; funding vero;
* rischio 1% a trade, leva massima 2, isolated; una posizione alla volta per moneta;
* esame di gruppo (`gruppo.py`, `timeframe="1d"`): trade sommati sulle 80 monete, minimi 700 in costruzione e 300
  in validazione, nessuna moneta oltre il 10% dei trade stimati.

### Tre fatti del terreno che pesano su ogni previsione (dal Passo 0, `parametri_2.yaml`, `misure_passo_0`)

1. **La distanza dello stop è grande**: 2,5 ATR(20) giornalieri valgono in mediana il 22,2% del prezzo (fra 13,3% e
   27,8% sulle 80 monete). Un trade che guadagna il 10% vale circa +0,45 R. Il costo di un giro è piccolo: 0,0068 R in
   mediana (fra 0,0043 e 0,0113). I costi non decidono quasi niente: decide la direzione.
2. **Il funding a giorni pesa**: tenere long BTCUSDT nel 2020-2023 per 25 giorni costava o rendeva in media 0,23 R a
   trade (misura del Passo 0, 24 trade). Le varianti long a tenuta lunga pagano il funding dei periodi di euforia;
   le short lo incassano. Va ricordato quando si legge l'R di una variante, perché la (b) lo paga uguale solo se
   entra negli stessi periodi.
3. **Pochi blocchi**: il blocco dell'esame è lungo quanto la posizione più lunga fra TUTTE le monete. Con l'uscita
   a tempo di 60 barre una sola posizione lunga basta a fare blocchi di circa due mesi: in costruzione (circa 1.100
   giorni per le monete più vecchie) restano 6-8 blocchi, la soglia di «nettamente» sale a circa 2,4-2,6, e anche
   +0,3 R a trade può non risultare «netto» (lezione del controllo positivo del Passo 0, `regole.md`, sezione 6).
   Le varianti dell'idea C (uscita dopo 5 giorni, stop raro a 22%) hanno posizioni brevi e molti più blocchi.

Lo stop a 22% è molto oltre il tetto del 6% del bot (`lezioni/metodo.md`): nessuna di queste varianti è eseguibile
dal bot così com'è. È una scelta del testo approvato, non della sessione, e si dichiara in consegna.

---

## Idea A — Tendenza (time-series momentum)

### 1. Fonte
* Moskowitz, Ooi, Pedersen, «Time Series Momentum», Journal of Financial Economics 104(2), 2012.
* Hurst, Ooi, Pedersen, «A Century of Evidence on Trend-Following Investing», Journal of Portfolio Management 44(1), 2017.
* Liu, Tsyvinski, «Risks and Returns of Cryptocurrency», Review of Financial Studies 34(6), 2021 (momentum a 1-4
  settimane nel mercato delle criptovalute).

Tutte pubblicate prima del 2024-01-01.

### 2. L'affermazione, in forma che si può smentire
Su ogni moneta del paniere, dopo una rottura del massimo (minimo) degli ultimi N giorni, o quando il rendimento a 60
giorni e la posizione rispetto alla media a 100 giorni concordano, il prezzo dei giorni successivi continua nella
stessa direzione più di quanto farebbe entrando a caso nella stessa direzione con la stessa uscita. Misura: R medio
dei trade sommati contro la (b) di gruppo (ingressi casuali, stessa uscita, stessa direzione, stesso numero di
trade per moneta). Smentita: `t` contro la (b) vicino a zero o negativo.

### 3. Sotto-domande
* In quali condizioni: dopo movimenti grandi (le rotture di 55 giorni sono più rare e più forti di quelle a 20)?
  Nei mesi di volatilità alta o bassa? Solo nei mercati in salita (2020-2021) o anche in discesa (2022)?
* Chi muove il prezzo: chi entra tardi (flussi che inseguono), chi copre short allo scoperto (long) o chi
  liquida posizioni a leva (short); i fondi che seguono la tendenza.
* Quando e in quanto tempo: settimane (Liu e Tsyvinski: 1-4 settimane); l'uscita a canale N/2 lascia correre.

### 4. Spiegazioni concorrenti (almeno 10), con la previsione e cosa la smentisce
1. **Effetto casuale.** Nessun vantaggio: `t` contro la (b) distribuito come le placebo (media circa 0,
   deviazione circa 0,8). Smentita: `t` sopra 2 su più varianti dell'idea, coerenti fra long e short.
2. **È solo il mercato (forma 1: le monete seguono BTC o il trend comune).** Nel 2020-2021 tutto saliva: un long
   qualsiasi guadagna. Previsione: R medio positivo per i long ma uguale a quello della (b), che entra nella stessa
   direzione negli stessi anni. Smentita: la variante batte la (b), che porta lo stesso trend.
3. **È solo il mercato (forma 2: i trade di monete diverse negli stessi giorni sono una scommessa sola).** Le
   rotture cadono negli stessi giorni su molte monete. Previsione: effetto grappolo alto, pochi blocchi, il
   pavimento delle sfasate decide. Smentita: la variante batte anche il pavimento delle sfasate.
4. **Volatilità.** Le rotture avvengono quando la volatilità cresce; lo stop in ATR si allarga e la size si
   rimpicciolisce, e l'R misura altro. Previsione: R medio diverso dalla (b) solo perché lo stop è diverso;
   costo in R più basso della (b). Smentita: la differenza resta anche guardando il costo medio in R uguale.
5. **Uscita, non ingresso.** L'uscita a canale lascia correre i guadagni e taglia presto: il vantaggio verrebbe
   dall'uscita, che la (b) ha uguale. Previsione: (b) già positiva; variante uguale alla (b). Smentita: variante
   sopra la (b).
6. **Pochi trade estremi.** Due o tre corse enormi (monete che si moltiplicano per 10 nel 2021) fanno la media.
   Previsione: R medio senza i 30 migliori trade vicino a zero; R per anno concentrato nel 2021. Smentita: R positivo
   senza i migliori e in più anni.
7. **Funding.** Il long paga il funding dei periodi di euforia (rotture al rialzo = funding alto), lo short lo
   incassa. Previsione: long peggiore della (b) nei periodi di funding alto, short migliore; differenza fra lordo e
   netto grande. Smentita: differenza di R fra variante e (b) che non cambia togliendo il funding (non misurabile qui
   direttamente: si guarda l'R per anno e la differenza long/short).
8. **Artefatto dei dati.** Il primo giorno di una moneta, i buchi del mark o le giornate tolte dall'allineamento
   creano rotture finte (il massimo di 20 giorni attraversa un buco). Previsione: trade concentrati nei primi mesi di
   una moneta o dopo un buco. Smentita: distribuzione dei trade senza addensamenti dopo i buchi.
9. **Riempimento a limite.** L'ordine limite alla chiusura riempie solo se il giorno dopo torna indietro: dopo
   una rottura vera il prezzo spesso non torna, e l'ordine non riempie; restano le rotture che ritornano (le false).
   Previsione: la variante entra soprattutto nelle rotture che falliscono, R medio peggiore di quello di un ingresso
   a mercato; quota di segnali saltati alta. Smentita: R positivo nonostante la selezione.
10. **Il vantaggio si è consumato dopo il 2021.** Previsione: R positivo nel 2020-2021 e negativo nel 2022 (anno
    d'uscita), poi validazione 2023 negativa. Smentita: R positivo anche nel 2022.
11. **Effetto costi.** Con 0,007 R per giro non può spiegare nulla: previsione, R lordo e netto quasi uguali.
12. **Sopravvivenza.** Le monete sono quelle vive e liquide nel 2023: chi è crollato e morto non c'è, e il long ne
    beneficia. Previsione: long migliore dello short in costruzione anche senza vantaggio; lo vede la (b) solo in
    parte (anche lei entra solo nelle sopravvissute). Smentita: non si smentisce dentro la campagna: si dichiara.

### 5. Ipotesi completa
Su tutte le 80 monete del paniere, a candele giornaliere, la rottura del canale di N giorni (A1) o il segno
concorde di rendimento a 60 giorni e media a 100 (A2) segnala una tendenza che prosegue per settimane, nella
direzione della rottura, perché le informazioni si diffondono lentamente e i flussi seguono il prezzo; il
meccanismo vale su monete diverse per la stessa ragione (stessi partecipanti, stessa leva, stessi flussi).
Timeframe 1 giorno (l'unico del terreno). Direzione: una per variante.

### 6. Le varianti (6), con il motivo
* **A1-20 long / A1-20 short.** Rottura del massimo (minimo) degli ultimi 20 giorni chiusi PRIMA del giorno di
  segnale: alla chiusura del giorno `t`, long se `close[t]` > max(`high[t-20..t-1]`), short se `close[t]` <
  min(`low[t-20..t-1]`). Uscita a segnale: chiusura sotto il minimo (long) o sopra il massimo (short) degli ultimi
  10 giorni chiusi prima del giorno, all'apertura del giorno dopo. Motivo: la rottura breve, il canale di
  Donchian classico a 4 settimane (Liu e Tsyvinski: momentum a 1-4 settimane).
* **A1-55 long / A1-55 short.** Uguale con N = 55 (uscita a 27 giorni: N/2 con N dispari si arrotonda per difetto,
  `55 // 2 = 27`; scelta scritta qui prima di ogni dato). Motivo: la rottura lunga, più rara e più forte.
* **A2 long / A2 short.** Long alla chiusura del giorno `t` se `close[t]/close[t-60] - 1 > 0` e `close[t]` > media
  semplice delle ultime 100 chiusure (giorno `t` compreso); short simmetrico (rendimento < 0 e chiusura < media).
  Uscita a segnale quando una delle due condizioni cade, all'apertura del giorno dopo. Motivo: il segno del
  rendimento (Moskowitz, Ooi, Pedersen) con un filtro di media, che riduce i cambi di segno intorno allo zero.
* Per tutte: stop iniziale 2,5 ATR(20) dalla chiusura di segnale (ATR = media semplice dei true range delle ultime
  20 barre, giorno `t` compreso); nessun target; uscita a tempo 60 barre (del motore); ingresso a limite.

Scelte di scrittura fissate qui, prima di qualunque dato (il testo non le dice, e vanno decise prima):
* «giorni» = barre giornaliere della serie della moneta (le barre tolte dall'allineamento sono buchi; una
  finestra di N barre attraversa i buchi senza accorgersene, come dicono le lezioni di metodo);
* il massimo e il minimo del canale si prendono su `high` e `low` delle barre PRECEDENTI al giorno di segnale;
* la (a) di A1 e A2 entra a ogni barra in cui è libera (stesso stop, uscita e tempo), dalla prima barra in cui la
  variante può calcolare il suo segnale (riscaldamento: N barre per A1, 100 per A2, 20 per l'ATR);
* il segnale «senza la condizione d'ingresso» (`crea_segnale`) è lo stop a 2,5 ATR(20), valido dopo il
  riscaldamento della variante.

### 7. Previsione di famiglia (scritta prima, `regole.md`, sezione 7)
Se in costruzione nessuna variante batte nettamente la (b) di gruppo con R netto > 0, l'idea è morta a questo
orizzonte e non si ritocca oltre il budget. Previsione mia: [Probabile] nessuna variante dell'idea A sarà «netta»
contro la (b), per i pochi blocchi (punto 3 della premessa) prima ancora che per il vantaggio; le short più
probabili delle long ad avere `t` positivo, perché la (b) long è gonfiata dal 2020-2021.

---

## Idea B — Momentum trasversale fra monete

### 1. Fonte
* Liu, Tsyvinski, Wu, «Common Risk Factors in Cryptocurrency», Journal of Finance 77(2), 2022 (fattore momentum sui
  rendimenti di 1-4 settimane).
* Jegadeesh, Titman, «Returns to Buying Winners and Selling Losers», Journal of Finance 48(1), 1993.

### 2. L'affermazione, in forma che si può smentire
Ogni lunedì, le 10 (o 20) monete del paniere con il rendimento più alto delle 4 (o 2) settimane precedenti rendono,
nella settimana dopo, più di un long a caso sulle stesse monete con la stessa uscita; le 10 (o 20) con il
rendimento più basso rendono meno (short sopra la (b) short). Smentita: `t` contro la (b) vicino a zero o negativo.

### 3. Sotto-domande
* Vale nelle code (prime e ultime 10) o in modo diffuso (prime e ultime 20)? Più a 2 o a 4 settimane?
* Chi muove: flussi al dettaglio che inseguono le monete della settimana; notizie assorbite lentamente sulle
  monete meno seguite.
* Quando: la settimana dopo il ribilanciamento (si tiene fino al lunedì dopo).

### 4. Spiegazioni concorrenti (almeno 10)
1. **Caso.** `t` come le placebo. Smentita: `t` alto e coerente fra B1, B2, B3.
2. **È solo il mercato (forma 1).** Le forti sono le più legate al mercato (beta alto): in un mercato che sale
   rendono di più per il beta, non per il momentum. Previsione: long positivo nel 2020-2021, negativo nel 2022, e la
   (b) long sulle stesse monete fa lo stesso. Smentita: batte la (b).
3. **È solo il mercato (forma 2).** I 10 long della stessa settimana sono una scommessa sola. Previsione: blocchi
   pochi, pavimento delle sfasate alto. Smentita: batte il pavimento.
4. **Inversione di breve.** A 1-2 settimane le criptovalute mostrano anche inversione (chi è salito troppo torna
   indietro): B2 (2 settimane) peggiore di B1. Previsione: `t` di B2 negativo. Smentita: B2 ≥ B1.
5. **Volatilità.** Le monete estreme sono le più volatili: lo stop in ATR largo, size piccola, R diverso. Previsione:
   costo in R diverso dalla (b), R vicino alla (b). Smentita: differenza che resta.
6. **Pochi trade estremi.** Una moneta che esplode una settimana. Previsione: R senza i 30 migliori vicino a zero.
7. **Funding.** Le forti hanno funding alto (long caro), le deboli funding basso o negativo (short caro).
   Previsione: il long perde una parte del vantaggio lordo nel funding.
8. **Sopravvivenza.** Le deboli che sono morte non ci sono: lo short sulle deboli sopravvissute è penalizzato
   (le sopravvissute si sono riprese). Si dichiara; non si smentisce qui.
9. **Riempimento a limite.** Il lunedì l'ordine limite riempie solo se il prezzo torna: le forti che continuano a
   correre non entrano. Previsione: quota di segnali saltati alta sui long delle forti, R peggiore della versione a
   mercato.
10. **Artefatto della classifica.** Monete nuove (meno di 90 giorni) o con buchi entrano o escono dalla classifica
    per i dati, non per il prezzo. Previsione: trade addensati vicino all'ingresso di una moneta nel paniere.
11. **Liquidità.** Le estreme sono le meno liquide: lo scarto vero è più alto di quello della fascia. Si guarda il
    test a costi doppi.

### 5. Ipotesi completa
Su tutte le 80 monete del paniere, il lunedì alle 00:00 UTC, le monete con il rendimento a 4 (o 2) settimane fra le
prime 10 (o 20) proseguono nella settimana dopo meglio di un ingresso a caso, e quelle fra le ultime 10 (o 20)
peggio, per sottoreazione alle notizie e flussi che inseguono i vincitori; il meccanismo è lo stesso per ogni
moneta (la classifica è fra monete). Timeframe 1 giorno, ribilanciamento settimanale. Direzione: una per variante.

### 6. Le varianti (6), con il motivo
* **B1 long / B1 short**: classifica sul rendimento delle ultime 4 settimane (28 giorni), prime 10 long, ultime 10
  short. Motivo: il momentum a 4 settimane di Liu, Tsyvinski e Wu.
* **B2 long / B2 short**: come B1 sul rendimento delle ultime 2 settimane (14 giorni). Motivo: il lato breve della
  fonte, dove l'inversione può competere.
* **B3 long / B3 short**: come B1 con le prime e le ultime 20. Motivo: dice se l'effetto sta nelle code o è diffuso.
* Per tutte: entrano in classifica le monete con almeno 90 giorni di storia e il mese liquido; la posizione resta
  aperta se la moneta è ancora nelle sue 10 (20) al lunedì dopo, altrimenti esce a segnale; stop 2,5 ATR(20);
  uscita a tempo 60 barre; ingresso a limite.

**Problema aperto (vedi il log):** con gli strumenti di oggi le funzioni della variante non ricevono le candele
delle altre monete (`gruppo.py`, contratto, punto 3: il contesto contiene solo la moneta, BTCUSDT e il suo
funding) e non possono importare `research/src/paniere.py` (import ammessi: libreria standard, numpy,
`research.src.motore`). Le varianti dell'idea B non si possono scrivere finché il proprietario non decide.

### 7. Previsione di famiglia
Stessa regola dell'idea A. Previsione mia: [Indovino] B3 più vicina al caso di B1, B2 con `t` più basso di B1.

---

## Idea C — Il ritardo delle monete dopo un giorno forte di Bitcoin

### 1. Fonte
* Ciaian, Rajcaniova, Kancs, «Virtual relationships: Short- and long-run evidence from BitCoin and altcoin
  markets», Journal of International Financial Markets, Institutions and Money 52, 2018.
* Il testo cita anche un risultato della campagna di gruppo della prima edizione a 1 ora: come risultato di
  un'altra campagna non è una fonte valida per questa sessione (Fase 1, punto 1, del protocollo) e non l'ho letto;
  vale solo come motivo del proprietario per chiedere l'idea.

### 2. L'affermazione, in forma che si può smentire
Dopo un giorno UTC in cui il rendimento di Bitcoin supera k deviazioni standard dei suoi 60 giorni precedenti, le
monete del paniere che quel giorno sono salite meno di Bitcoin (giorno forte al rialzo) recuperano nei 5 giorni
dopo più di un long a caso con la stessa uscita; simmetrico per lo short dopo un giorno forte al ribasso. Smentita:
`t` contro la (b) vicino a zero o negativo.

### 3. Sotto-domande
* Il ritardo si recupera in 5 giorni o è già assorbito nel giorno stesso? Più con k = 2 (giorni rari e grandi) o
  con k = 1,5?
* Chi muove: i flussi arrivano prima su Bitcoin e poi passano alle altre monete (arbitraggio lento, investitori che
  ribilanciano); il ritardo si chiude se il movimento di Bitcoin regge.
* Quando: i primi 1-5 giorni dopo il giorno forte.

### 4. Spiegazioni concorrenti (almeno 10)
1. **Caso.** `t` come le placebo; pochi giorni forti fanno pochi grappoli. Smentita: `t` alto e coerente fra k.
2. **È solo il mercato (forma 1).** Dopo un giorno forte al rialzo Bitcoin continua (o torna indietro) e tutte
   le monete lo seguono: il long guadagna per il mercato, non per il ritardo. Previsione: anche le monete NON in
   ritardo fanno lo stesso; la (b) non lo cattura perché entra in altri giorni. È il controllo più importante:
   la (b) a caso non tiene il giorno; serve la prova «senza la condizione di ritardo» in Fase 5.
3. **È solo il mercato (forma 2).** Tutti i trade di un giorno forte sono una scommessa sola: 40-60 monete
   entrano lo stesso giorno. Previsione: effetto grappolo enorme, pavimento delle sfasate decisivo. Smentita: batte
   il pavimento.
4. **Inversione del giorno forte.** Dopo un giorno estremo Bitcoin torna indietro: il long dopo un giorno forte al
   rialzo perde. Previsione: R negativo per i long, positivo per gli short di segno opposto.
5. **Beta basso, non ritardo.** Le monete «in ritardo» sono quelle che si muovono meno (beta basso): non
   recuperano, si muovono meno anche dopo. Previsione: R vicino a zero per C1, negativo per le 20 più in ritardo.
6. **Notizie della moneta.** Una moneta è in ritardo perché ha una notizia cattiva sua: non recupera.
   Previsione: le più in ritardo (C2) peggiori di tutte le in ritardo (C1).
7. **Volatilità.** I giorni forti sono giorni di volatilità alta: lo stop in ATR è largo, la size piccola, i costi
   in R più bassi. Previsione: costo medio in R più basso della (b); R simile.
8. **Pochi giorni estremi.** Due o tre giorni forti (marzo 2020, maggio 2021, crolli del 2022) fanno la media.
   Previsione: senza i 3 giorni migliori l'R scende sotto la (b). È una delle tre prove degli estremi.
9. **Riempimento a limite.** Se il recupero comincia subito il giorno dopo (apertura in salita), l'ordine limite al
   prezzo di chiusura non riempie; entrano soprattutto le monete che continuano a scendere. Previsione: quota di
   segnali saltati alta; R peggiore di un ingresso a mercato.
10. **Funding.** Breve tenuta (5 giorni): poco peso. Previsione: R lordo e netto vicini.
11. **Artefatto dei dati.** Una moneta con la candela mancante il giorno forte non ha rendimento: esce dalla
    classifica. Nessun effetto atteso sul segno.
12. **Asincronia delle chiusure.** Tutte le candele chiudono a 00:00 UTC: un «ritardo» misurato sulla chiusura può
    essere solo rumore dell'ultimo minuto. Previsione: effetto piccolo e incoerente.

### 5. Ipotesi completa
Su tutte le 80 monete del paniere, alla chiusura di un giorno forte di Bitcoin, le monete rimaste indietro rispetto
a Bitcoin recuperano nei 5 giorni dopo, nella direzione del giorno forte, perché i flussi e le notizie arrivano
prima su Bitcoin e le altre monete, meno liquide e meno seguite, seguono con ritardo; il meccanismo è lo stesso per
ogni moneta. Timeframe 1 giorno. Direzione: una per variante.

### 6. Le varianti (6), con il motivo
* Giorno forte: `r_BTC[t] = close_BTC[t]/close_BTC[t-1] - 1` oltre `k` volte la deviazione standard (ddof 1) dei
  rendimenti di Bitcoin dei 60 giorni PRECEDENTI (`t` escluso, almeno 40 valori finiti): è la funzione
  `giorni_forti` di `research/src/paniere.py`, con n = 60 e minimo = 40 (`parametri_2.yaml`).
* **C1-1,5 long / C1-1,5 short; C1-2 long / C1-2 short**: dopo un giorno forte al rialzo (ribasso), long (short)
  su ogni moneta con rendimento del giorno `t` inferiore (superiore) a quello di Bitcoin. Motivo: k 1,5 dà più
  giorni, k 2 giorni più rari e forti.
* **C2-1,5 long / C2-1,5 short**: come C1-1,5, solo le 20 monete più in ritardo (rendimento del giorno più lontano
  da quello di Bitcoin nella direzione del ritardo). Motivo: dice se il recupero è più forte per le più in
  ritardo (o se lì domina la notizia della moneta, spiegazione 6).
* Per tutte: uscita a segnale dopo 5 giorni (alla chiusura del quinto giorno dopo quello di segnale si chiede
  l'uscita, che il motore esegue all'apertura del giorno dopo: scelta scritta qui prima di ogni dato); stop 2,5
  ATR(20); ingresso a limite; uscita a tempo 60 barre (non scatta mai prima dei 5 giorni).

**Problema aperto (vedi il log):** C1 si può scrivere con il contesto di oggi (rendimento della moneta e di
Bitcoin, entrambi disponibili alla funzione della variante); C2 no, perché «le 20 più in ritardo» è una
classifica fra monete e le funzioni non ricevono le altre monete. Anche `paniere.py` non si può importare: per C1
la stessa formula di `giorni_forti` andrebbe riscritta nel modulo.

### 7. Previsione di famiglia
Stessa regola delle idee A e B. Previsione mia: [Indovino] effetto piccolo; i long di C1 con `t` più alto degli
short; la forma 2 di «è solo il mercato» (grappoli di 40-60 trade nello stesso giorno) farà pochi blocchi
indipendenti nonostante le posizioni brevi.
