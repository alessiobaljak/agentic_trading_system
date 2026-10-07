# Ipotesi della campagna SOLUSDT

Scritto il 2026-10-07 PRIMA di qualunque test (Fase 1 del Passo 3). Ogni idea ha una fonte
pubblicata prima del 2024-01-01 (titolo, autore, data), un'affermazione verificabile, le
sotto-domande, le spiegazioni concorrenti con la previsione di ciascuna, e l'ipotesi
completa (moneta, meccanismo, timeframe, direzione). La stima dei trade si fa contando i
segnali sui dati di costruzione (2021-01-01 → 2023-01-04) e si registra nel log prima
della variante. Nessuna idea viene dai risultati del gate, del registro o del paper del
bot, né da altre monete. Nessuna idea viene da ciò che so dei mercati dal 2024 in poi.

Regole fisse di esecuzione per tutte le varianti (sezione 7 del protocollo e regole del
bot): ingresso all'apertura della barra dopo il segnale; rischio 1% del capitale per
trade; leva massima 2 (il trade si riduce, non si scarta); margine isolato; stop sulla
serie last; stop prima del target nella stessa barra; commissione 0,05% e slippage 0,01%
per lato; funding vero a ogni settlement. Lo stop è sempre definito all'ingresso e non si
muove (il motore non lo prevede): le uscite sono stop, target, oppure chiusura a mercato
decisa dalla strategia su barra chiusa (uscita a tempo o a condizione).

## Spiegazioni concorrenti comuni (valgono per ogni idea)

Per ogni idea, oltre alle sue specifiche, vanno escluse queste dieci. Per ciascuna: cosa
prevede, e cosa la smentirebbe.

| # | Spiegazione | Cosa prevede | Cosa la smentisce |
|---|---|---|---|
| C1 | **Caso.** Non c'è effetto; il risultato è rumore | R medio del candidato dentro la distribuzione delle entrate casuali con la stessa uscita (sotto il 90° percentile); differenza non netta (sotto 2 errori standard) | candidato sopra il 90° percentile delle entrate casuali E differenza netta col bootstrap a blocchi |
| C2 | **È solo il mercato (trend di fondo).** SOL è salita nel 2021 e nel 2023, scesa nel 2022: un long qualunque vince negli anni buoni | il segno del risultato per anno segue il segno del buy and hold dell'anno; una strategia long perde nel 2022 e vince negli altri | R medio positivo in anni di segno diverso; vantaggio sull'entrata casuale (che ha lo stesso trend di fondo) in ogni anno |
| C3 | **È solo BTC.** SOL segue BTC: il segnale su SOL è un segnale su BTC in ritardo o in copia | l'effetto si spiega col rendimento di BTC nelle stesse finestre (beta × BTC); tolto quello, l'R residuo è circa zero | R residuo dopo beta × BTC ancora positivo e netto |
| C4 | **Volatilità, non direzione.** Il segnale coglie momenti di alta volatilità: con target più lontano dello stop (o viceversa), il semplice allargamento del movimento produce R positivo senza prevedere la direzione | lo stesso ingresso nella direzione opposta dà un R simile; l'entrata casuale negli stessi momenti (stessa volatilità) dà lo stesso R | la direzione opposta perde nettamente; l'entrata casuale condizionata allo stesso regime di volatilità perde |
| C5 | **Artefatto dei dati.** Buchi, candele mancanti, timestamp, allineamento last/mark, bordo del periodo | i trade migliori stanno attorno ai buchi o ai bordi; il risultato cambia togliendo quei trade | risultato stabile senza i trade vicini ai buchi (5 giorni mancanti nel last, 7 nel mark) |
| C6 | **Lookahead.** Un indicatore usa, anche per sbaglio, la barra corrente o successiva | il test del ritardo di una barra fa crollare il risultato a zero o sotto | il ritardo peggiora gradualmente, non crolla |
| C7 | **Costi sottostimati.** Il vantaggio è più piccolo dei costi veri (slippage reale, funding) | a costi doppi il profit factor scende sotto 1 | profit factor sopra 1 anche a costi doppi, con margine |
| C8 | **Pochi trade estremi.** Due o tre trade fanno tutto il risultato | togliendo i 3 trade migliori l'R medio va a zero; R mediano negativo | R mediano positivo; R medio ancora positivo senza i 3 migliori |
| C9 | **Un solo periodo.** L'effetto vive in un regime (es. 2021) e sparisce negli altri | R medio positivo in un anno solo | R medio positivo in almeno due anni su tre e nel periodo di validazione |
| C10 | **Regola intra-barra.** Il risultato dipende dall'ordine stop/target dentro la barra, cioè da ciò che non si sa | con la regola opposta (target prima) il risultato cambia di molto; con stop prima è negativo | differenza piccola fra le due regole |
| C11 | **Funding, non prezzo.** Il risultato viene dal funding incassato, non dal movimento | pnl lordo circa zero, funding incassato positivo | pnl lordo positivo anche senza il funding |
| C12 | **Ottimizzazione nascosta.** Il parametro scelto è un picco isolato | parametri vicini danno risultati molto diversi | area stabile attorno al parametro |

## I-01 — Momentum di serie temporale (seguire la tendenza)

- **Fonte.** «Time Series Momentum», Tobias J. Moskowitz, Yao Hua Ooi, Lasse Heje
  Pedersen, Journal of Financial Economics 104(2), 2012. Per le crypto: «Risks and
  Returns of Cryptocurrency», Yukun Liu, Aleh Tsyvinski, Review of Financial Studies
  34(6), 2021 (momentum a 1-4 settimane su Bitcoin).
- **Affermazione verificabile.** Su SOLUSDT il segno del rendimento delle ultime N barre
  predice il segno del rendimento delle barre successive: entrare nella direzione della
  tendenza quando il rendimento su N barre cambia segno dà R medio positivo, superiore
  all'entrata casuale con la stessa uscita.
- **Sotto-domande.** A quale scala vale (giorni, settimane)? Vale in entrambe le direzioni
  o solo long (le crypto hanno rialzi lunghi e crolli brevi)? Chi muove il prezzo:
  i flussi al dettaglio che inseguono il prezzo e la diffusione lenta delle notizie; se
  è così l'effetto si manifesta nei giorni successivi al cambio di segno e si esaurisce
  in 1-3 settimane. Sparisce nei mercati laterali (2022 estate)?
- **Spiegazioni concorrenti specifiche.** (S1) È il trend di fondo (C2): nel 2021 e nel
  2023 ogni long vince; previsione: lo short perde sempre, il long vince solo negli anni
  di rialzo; smentita: vantaggio sull'entrata casuale anche nel 2022. (S2) È BTC (C3).
  (S3) Il cambio di segno capita in alta volatilità (C4). Più le comuni C1, C5-C10, C12.
- **Ipotesi completa.** SOLUSDT; meccanismo: inseguimento della tendenza da parte dei
  flussi al dettaglio e diffusione lenta delle informazioni; timeframe **4h** (il
  meccanismo è di giorni-settimane: con candele da 4 ore 30 barre sono 5 giorni, e si
  entra entro poche ore dal cambio di segno; la candela giornaliera renderebbe troppo
  pochi ingressi, lo dirà la stima); direzione **long e short, separate**. Regola:
  rendimento su 30 barre (5 giorni) che passa da negativo a positivo → long (il
  contrario → short); stop a 2 ATR(14 barre) dall'ingresso; uscita quando il rendimento
  su 30 barre torna del segno opposto (chiusura a mercato all'apertura della barra dopo),
  oppure stop. Nessun target.
- **Previsione.** R medio fra 0,05 e 0,20 per il long; short vicino a zero o negativo.
  Profit factor long 1,1-1,4. Vince la metà o meno dei trade con vincite lunghe.

## I-02 — Funding estremo come segnale contrario (carry)

- **Fonte.** «Crypto Carry», Maik Schmeling, Andreas Schrimpf, Karamfil Todorov, BIS
  Working Papers n. 1087, aprile 2023 (il carry dei perpetui, cioè il funding, è alto
  quando i long a leva sono affollati e precede i crolli). «Fundamentals of Perpetual
  Futures», Songrun He, Asaf Manela, Omri Ross, Victor von Wachter, arXiv 2212.06888,
  dicembre 2022 (il funding come differenza fra perpetuo e spot).
- **Affermazione verificabile.** Quando il funding di SOLUSDT è estremo (sopra l'alto
  percentile della sua storia recente) il rendimento successivo del perpetuo, funding
  compreso, è negativo per i long: uno short aperto dopo un settlement a funding estremo
  ha R medio positivo (incasso del funding più ritorno del prezzo), superiore all'entrata
  casuale. Simmetrico: funding estremamente negativo → long.
- **Sotto-domande.** Quanto estremo (90°, 95° percentile su 30 giorni)? L'effetto è nel
  prezzo o solo nel funding incassato (C11)? Quanto dura: fino al prossimo settlement,
  o giorni? Chi opera: i long a leva che pagano il funding e vengono liquidati nelle
  discese; chi incassa il carry (arbitraggisti spot-perpetuo) spinge il prezzo del
  perpetuo verso lo spot.
- **Spiegazioni concorrenti specifiche.** (S1) Il funding alto coincide con i rialzi
  forti del 2021: lo short perde nel prezzo più di quanto incassa (C2, segno opposto).
  (S2) Solo funding (C11). (S3) Il funding segue il prezzo, non lo precede: il segnale
  arriva dopo il movimento (previsione: ritardo di una barra non cambia nulla, e il
  rendimento dopo il segnale è casuale). Più C1, C3-C10, C12.
- **Ipotesi completa.** SOLUSDT; meccanismo: affollamento dei long a leva e carry;
  timeframe **1h** (il settlement è ogni 8 ore: si entra all'ora dopo il settlement
  estremo, le posizioni durano fino a 24 ore); direzione **short** (funding alto) e
  **long** (funding basso), varianti separate. Regola: all'ultimo settlement il tasso è
  sopra il 95° percentile dei 90 settlement precedenti (30 giorni) e sopra +0,03%
  (altrimenti «estremo» non significa niente) → short; stop a 2 ATR(24) dall'ingresso;
  uscita a tempo dopo 24 barre (3 settlement incassati) o stop. Simmetrico per il long
  con tasso sotto il 5° percentile e sotto −0,03%.
- **Previsione.** Short: R medio 0,05-0,15 con il funding dentro; senza funding
  (pnl lordo) vicino a zero. Long dopo funding negativo: R medio 0-0,10. Trade pochi:
  rischio di stare sotto il minimo (lo dirà la stima).

## I-03 — Ora del giorno: la sessione americana

- **Fonte.** «Bitcoin time-of-day, day-of-week and month-of-year effects in returns and
  trading volume», Dirk G. Baur, Daniel Cahill, Keith Godfrey, Zhangxin (Frank) Liu,
  Finance Research Letters 31, 2019 (volume e rendimenti concentrati nelle ore di
  mercato americane).
- **Affermazione verificabile.** Il rendimento di SOLUSDT nelle ore della sessione
  americana (13:00-21:00 UTC) è sistematicamente diverso da zero e dal resto della
  giornata: un long aperto alle 13:00 UTC e chiuso alle 21:00 UTC ha R medio positivo
  superiore a entrate casuali di 8 ore.
- **Sotto-domande.** L'effetto è un drift (C2) o un vero effetto di sessione (vale anche
  nel 2022)? Chi opera: flussi istituzionali e al dettaglio americani, apertura delle
  borse. Dura 8 ore. Vale nei giorni feriali e non nel fine settimana?
- **Spiegazioni concorrenti specifiche.** (S1) È il trend (C2): nel 2021 e 2023 tutte le
  ore salgono; previsione: l'effetto ha il segno dell'anno; smentita: la sessione
  americana batte le altre ore anche nel 2022. (S2) È la volatilità (C4): la sessione è
  solo più volatile. Più C1, C3, C5-C10.
- **Ipotesi completa.** SOLUSDT; meccanismo: flussi concentrati nelle ore americane;
  timeframe **1h**; direzione **long** (giorni feriali). Regola: segnale alla chiusura
  della barra delle 12:00 UTC (ingresso all'apertura delle 13:00), stop a 3 ATR(24),
  chiusura a mercato all'apertura delle 21:00 UTC (8 barre). Nessun target.
- **Previsione.** R medio 0,00-0,05; molto probabilmente non netto rispetto all'entrata
  casuale. È l'idea più «noiosa» e serve da controllo del metodo.

## I-04 — Giorno della settimana: il fine settimana

- **Fonte.** «Seasonality in cryptocurrencies», Lars Kaiser, Finance Research Letters 31,
  2019; Baur, Cahill, Godfrey, Liu 2019 (sopra).
- **Affermazione verificabile.** I rendimenti di SOLUSDT del fine settimana (da sabato
  00:00 a lunedì 00:00 UTC), a volumi bassi, hanno segno sistematico, oppure vengono
  ritracciati il lunedì (la liquidità che torna corregge i movimenti sottili).
- **Sotto-domande.** Segno del fine settimana? Il lunedì ritraccia il movimento del fine
  settimana? Chi opera nel fine settimana: solo il dettaglio e gli algoritmi; il lunedì
  tornano gli operatori professionali.
- **Spiegazioni concorrenti specifiche.** (S1) trend (C2). (S2) il movimento del fine
  settimana è piccolo e i costi lo mangiano (C7). Più C1, C3-C6, C8-C10.
- **Ipotesi completa.** SOLUSDT; meccanismo: ritorno della liquidità il lunedì che
  corregge i movimenti del fine settimana; timeframe **4h**; direzione: **contraria al
  movimento del fine settimana** (long se il fine settimana è stato negativo oltre 1
  ATR(42) e short se positivo). Regola: segnale alla chiusura della barra 20:00-24:00
  UTC di domenica; stop a 2 ATR(42 barre = 1 settimana); chiusura a mercato dopo 6
  barre (24 ore, fine lunedì). Variante separata: il segno puro del fine settimana
  (long da sabato 00:00 a lunedì 00:00) se il conteggio lo permette.
- **Previsione.** Circa 105 fine settimana in costruzione: la variante «ritraccio» avrà
  meno di 100 segnali (serve un movimento oltre 1 ATR): probabile scarto per pochi
  trade. R medio atteso 0-0,05.

## I-05 — Continuazione dopo una barra estrema (cascata di liquidazioni)

- **Fonte.** «Price overreactions in the cryptocurrency market», Guglielmo Maria
  Caporale, Alex Plastun, Journal of Economic Studies 46(5), 2019 (dopo un giorno di
  rendimento anomalo il movimento del giorno dopo è nella stessa direzione, cioè
  momentum, non ritorno). «Market Liquidity and Funding Liquidity», Markus K.
  Brunnermeier, Lasse Heje Pedersen, Review of Financial Studies 22(6), 2009 (spirali di
  liquidità: le perdite forzano vendite che fanno altre perdite).
- **Affermazione verificabile.** Dopo una barra di SOLUSDT con rendimento oltre 3
  deviazioni standard (delle ultime 100 barre), le barre successive continuano nella
  stessa direzione: entrare nella direzione dello shock dà R medio positivo, superiore
  all'entrata casuale.
- **Sotto-domande.** Quanto grande lo shock (2, 3, 4 deviazioni)? Vale di più al ribasso
  (liquidazioni dei long, che sono la maggioranza) che al rialzo? Quanto dura la
  continuazione: ore. Chi opera: i liquidati a forza e chi ferma le perdite.
- **Spiegazioni concorrenti specifiche.** (S1) ritorno invece di continuazione (è l'idea
  I-06, opposta): previsione: la direzione dello shock perde. (S2) volatilità (C4): dopo
  lo shock tutto si muove di più, e lo stop stretto scatta prima. (S3) BTC (C3): lo
  shock è di BTC. Più C1, C2, C5-C10, C12.
- **Ipotesi completa.** SOLUSDT; meccanismo: spirale di liquidità e liquidazioni a
  catena; timeframe **1h**; direzione **quella dello shock, long e short separate**.
  Regola: rendimento della barra oltre 3 deviazioni standard dei rendimenti delle 100
  barre precedenti → ingresso nella stessa direzione; stop a 1,5 ATR(24); uscita a tempo
  dopo 12 barre o stop. Nessun target.
- **Previsione.** Short dopo shock negativo: R medio 0,05-0,15; long dopo shock positivo:
  circa zero. Probabilmente molti trade fermati dallo stop (volatilità alta dopo lo shock).

## I-06 — Ritorno dopo una barra estrema (esaurimento della liquidità)

- **Fonte.** «Does the Stock Market Overreact?», Werner F. M. De Bondt, Richard Thaler,
  Journal of Finance 40(3), 1985 (iper-reazione e ritorno). Brunnermeier e Pedersen 2009
  (sopra): dopo la spirale, chi fornisce liquidità è ricompensato dal ritorno del prezzo.
- **Affermazione verificabile.** Dopo lo stesso shock di I-05 ma con la barra successiva
  che NON continua (chiude dalla parte opposta allo shock: la spirale si è esaurita),
  entrare contro lo shock dà R medio positivo, superiore all'entrata casuale.
- **Sotto-domande.** Serve la conferma della barra dopo? Quanto dura il ritorno: ore o
  un giorno? Chi opera: fornitori di liquidità e arbitraggisti.
- **Spiegazioni concorrenti specifiche.** (S1) è I-05 al contrario (continuazione).
  (S2) il ritorno è già avvenuto nella barra di conferma e si entra tardi (previsione: il
  ritardo di una barra lo cancella, ma anche senza ritardo è vicino a zero). Più C1-C10,
  C12.
- **Ipotesi completa.** SOLUSDT; meccanismo: esaurimento della spirale e ritorno verso il
  prezzo di prima; timeframe **1h**; direzione **contraria allo shock, long e short
  separate**. Regola: barra oltre 3 deviazioni standard (100 barre) seguita da una barra
  di segno opposto → ingresso contro lo shock; stop a 1,5 ATR(24) oltre l'estremo dello
  shock; target al punto medio della barra dello shock; uscita a tempo dopo 24 barre.
- **Previsione.** Long dopo shock negativo: R medio 0,05-0,15 (il ritorno dopo le
  liquidazioni dei long è il caso più frequente); short dopo shock positivo: circa zero.

## I-07 — Rottura di canale (Donchian / Turtle)

- **Fonte.** «Way of the Turtle», Curtis M. Faith, McGraw-Hill, 2007 (regole dei Turtle:
  ingresso sulla rottura del massimo di 20 giorni, uscita sul minimo di 10, stop a 2
  ATR). Richard Donchian, regola del canale a 4 settimane (anni '60).
- **Affermazione verificabile.** Su SOLUSDT la rottura del massimo delle ultime 20 barre
  (chiusura sopra il massimo precedente) è seguita da continuazione: un long sulla
  rottura con stop a 2 ATR e uscita sul minimo di 10 barre ha R medio positivo,
  superiore all'entrata casuale con la stessa uscita.
- **Sotto-domande.** A quale scala (20 barre da 4 ore = 3,3 giorni; 20 giorni sarebbe
  troppo lento per 100 trade)? Long e short simmetrici? Chi opera: gli stop di chi è
  short sopra il massimo e gli ordini di chi segue le rotture.
- **Spiegazioni concorrenti specifiche.** (S1) trend di fondo (C2): le rotture al rialzo
  vincono solo nel 2021 e 2023. (S2) falsi segnali in laterale (previsione: win rate
  sotto il 35% e R medio negativo nel 2022). Più C1, C3-C10, C12.
- **Ipotesi completa.** SOLUSDT; meccanismo: ordini di stop e inseguimento sopra i
  massimi; timeframe **4h**; direzione **long e short separate**. Regola: chiusura
  sopra il massimo delle 20 barre precedenti → long; stop a 2 ATR(20); uscita a mercato
  quando la chiusura è sotto il minimo delle 10 barre precedenti, o stop. Simmetrico
  per lo short.
- **Previsione.** Long: profit factor 1,0-1,3, win rate 35-45%, R medio 0,0-0,15. Short:
  R medio circa zero. Risultato probabilmente dominato dal 2021.

## I-08 — Ritorno alla media dentro le bande di Bollinger

- **Fonte.** «Bollinger on Bollinger Bands», John Bollinger, McGraw-Hill, 2001 (bande a
  20 periodi e 2 deviazioni; chiusura fuori banda come eccesso).
- **Affermazione verificabile.** Su SOLUSDT una chiusura sotto la banda inferiore (media
  20, 2 deviazioni) è seguita da un ritorno verso la media: un long con target alla
  media mobile ha R medio positivo, superiore all'entrata casuale con la stessa uscita.
- **Sotto-domande.** Vale nei mercati laterali e fallisce nei trend (dove la banda viene
  «cavalcata»)? Serve un filtro di tendenza? Quanto dura il ritorno: ore. Chi opera:
  fornitori di liquidità e chi compra «a sconto».
- **Spiegazioni concorrenti specifiche.** (S1) nei trend forti (2021, 2022) la banda si
  cavalca e lo stop scatta spesso (previsione: win rate basso e R medio negativo in
  quegli anni). (S2) C4 e C10: stop e target vicini, la regola intra-barra conta.
  Più C1-C3, C5-C9, C12.
- **Ipotesi completa.** SOLUSDT; meccanismo: eccesso di breve periodo e fornitura di
  liquidità; timeframe **1h**; direzione **long e short separate**. Regola: chiusura
  sotto la banda inferiore (20, 2) → long; stop a 1,5 ATR(20) sotto il minimo della barra
  del segnale; target alla media mobile a 20 della barra del segnale; uscita a tempo dopo
  24 barre. Simmetrico per lo short.
- **Previsione.** Win rate alto (55-65%) ma R medio vicino a zero (target vicino, stop
  lontano): profit factor 0,9-1,1. Probabile fallimento sulle baseline.

## I-09 — Ritracciamento nella tendenza (medie mobili)

- **Fonte.** «Simple Technical Trading Rules and the Stochastic Properties of Stock
  Returns», William Brock, Josef Lakonishok, Blake LeBaron, Journal of Finance 47(5),
  1992 (regole di medie mobili: prezzo sopra la media lunga = tendenza).
- **Affermazione verificabile.** Su SOLUSDT, con il prezzo sopra la media mobile lunga
  (200 barre), un ritracciamento fino alla media corta (20 barre) è seguito dalla
  ripresa della tendenza: un long al ritracciamento ha R medio positivo, superiore
  all'entrata casuale condizionata alla stessa tendenza.
- **Sotto-domande.** Vale solo long (i rialzi delle crypto sono lunghi, i ribassi
  brevi)? Il ritracciamento deve toccare la media o chiudere sotto? Chi opera: chi
  «compra il ribasso» nelle tendenze.
- **Spiegazioni concorrenti specifiche.** (S1) è solo il trend (C2): l'entrata casuale
  nelle stesse fasi di tendenza (prezzo sopra la media lunga) fa lo stesso; questa è la
  baseline giusta per l'idea. (S2) BTC (C3). Più C1, C4-C10, C12.
- **Ipotesi completa.** SOLUSDT; meccanismo: acquisti sui ribassi dentro una tendenza
  riconosciuta; timeframe **1h**; direzione **long** (variante short simmetrica solo
  se il conteggio lo permette). Regola: chiusura sopra la media a 200 barre e minimo
  della barra sotto la media a 20 barre, chiusura sopra la media a 20 (il ritracciamento
  è stato comprato) → long; stop a 2 ATR(20) sotto il minimo della barra; target a 2
  volte la distanza dello stop; uscita a tempo dopo 48 barre.
- **Previsione.** R medio 0,0-0,10; vantaggio sull'entrata casuale condizionata alla
  tendenza probabilmente non netto.

## I-10 — Ritardo di SOL rispetto a BTC

- **Fonte.** «Virtual relationships: Short- and long-run evidence from BitCoin and
  altcoin markets», Pavel Ciaian, Miroslava Rajcaniova, d'Artis Kancs, Journal of
  International Financial Markets, Institutions and Money 52, 2018 (i prezzi delle
  altcoin dipendono da Bitcoin nel breve periodo).
- **Affermazione verificabile.** Quando BTC fa un movimento forte nelle ultime 4 ore e
  SOL si è mosso meno della sua beta, SOL recupera il ritardo nelle ore successive: un
  ingresso su SOL nella direzione del movimento di BTC ha R medio positivo, superiore
  all'entrata casuale.
- **Sotto-domande.** Esiste ancora un ritardo a 1 ora, con gli arbitraggisti? Quanto
  dura: 1-4 ore. Chi opera: gli arbitraggisti fra monete e chi segue BTC.
- **Spiegazioni concorrenti specifiche.** (S1) non c'è ritardo, c'è contemporaneità: il
  movimento di SOL è già avvenuto nella stessa barra (previsione: R zero). (S2) C4.
  Più C1-C3, C5-C10, C12.
- **Ipotesi completa.** SOLUSDT; meccanismo: diffusione del movimento di BTC alle
  altcoin con ritardo; timeframe **1h**; direzione **quella di BTC, long e short
  separate**. Regola: rendimento di BTC su 4 barre oltre 2 deviazioni standard (dei
  rendimenti a 4 barre delle 100 barre precedenti) e rendimento di SOL su 4 barre
  inferiore a 1,0 volte quello di BTC (beta di SOL su BTC è di norma sopra 1: SOL è
  «in ritardo» se ha fatto meno di BTC) → ingresso nella direzione di BTC; stop a 1,5
  ATR(24); uscita a tempo dopo 4 barre o stop.
- **Previsione.** R medio circa zero: i mercati del 2021-2023 erano già arbitrati a
  questa scala. È un'idea che mi aspetto di scartare in Fase 2.

## I-11 — Premio del volume alto

- **Fonte.** «The High-Volume Return Premium», Simon Gervais, Ron Kaniel, Dan H.
  Mingelgrin, Journal of Finance 56(3), 2001 (un volume insolitamente alto attira
  attenzione e precede rendimenti positivi).
- **Affermazione verificabile.** Su SOLUSDT una barra con volume oltre 3 volte la media
  delle 50 barre precedenti è seguita da rendimento positivo (indipendentemente dal
  segno della barra): un long dopo la barra ad alto volume ha R medio positivo,
  superiore all'entrata casuale.
- **Sotto-domande.** Vale a scala giornaliera (la fonte) o anche a 4 ore? L'attenzione
  dura giorni. Chi opera: i nuovi arrivati attirati dall'attenzione, che comprano.
- **Spiegazioni concorrenti specifiche.** (S1) i volumi alti sono nei crolli: il long
  entra nei crolli (previsione: R negativo nel 2022). (S2) C2, C4. Più C1, C3, C5-C10,
  C12.
- **Ipotesi completa.** SOLUSDT; meccanismo: attenzione e nuovi compratori; timeframe
  **4h** (la fonte è giornaliera, ma a 1 giorno le barre di costruzione sono 734 e la
  stima dei trade sarà sotto il minimo: l'attenzione a 4 ore è la stessa idea su scala
  più corta, dichiarato); direzione **long**. Regola: volume della barra oltre 3 volte
  la media delle 50 precedenti → long; stop a 2 ATR(20); uscita a tempo dopo 18 barre
  (3 giorni) o stop.
- **Previsione.** R medio 0,0-0,10, dominato dal 2021. Probabilmente non netto.

## I-12 — Compressione della volatilità e rottura

- **Fonte.** Bollinger 2001 (sopra): la «squeeze», larghezza delle bande al minimo di
  N periodi, precede un'espansione; la direzione la dà la rottura.
- **Affermazione verificabile.** Su SOLUSDT, quando la larghezza delle bande (20, 2) è
  al minimo delle ultime 100 barre, la prima chiusura fuori banda è seguita da
  continuazione: un ingresso nella direzione della rottura ha R medio positivo,
  superiore all'entrata casuale con la stessa uscita.
- **Sotto-domande.** Quanto stretta la compressione? La rottura è vera o falsa (quante
  tornano dentro)? Chi opera: chi aspetta la rottura con ordini condizionati.
- **Spiegazioni concorrenti specifiche.** (S1) è I-07 con un filtro (stesso
  meccanismo): previsione: risultati simili a I-07. (S2) C4. Più C1-C3, C5-C10, C12.
- **Ipotesi completa.** SOLUSDT; meccanismo: ordini condizionati accumulati durante la
  compressione; timeframe **1h**; direzione **quella della rottura, long e short
  separate**. Regola: larghezza delle bande (20, 2) al minimo delle 100 barre
  precedenti nella barra prima, e chiusura fuori banda → ingresso; stop a 2 ATR(20);
  target a 3 volte la distanza dello stop; uscita a tempo dopo 48 barre.
- **Previsione.** R medio 0,0-0,10, win rate basso (30-40%). Probabilmente non netto.

## Idee scartate senza test (nessun budget)

- **Effetto del settlement del funding** (movimenti attorno alle 00/08/16 UTC): non ho
  una fonte pubblicata prima del 2024 con titolo e autore; non si testa.
- **Momentum intragiornaliero** («Market intraday momentum», Lei Gao, Yufeng Han, Sophia
  Zhengzi Li, Guofu Zhou, Journal of Financial Economics 129(2), 2018): il meccanismo
  dipende dall'apertura e dalla chiusura di una borsa; le crypto non le hanno. Si
  scarta per meccanismo non trasferibile.
- **Cicli di settimane o mesi** (stagionalità mensile di Kaiser 2019): richiedono candele
  oltre 1 giorno o troppo pochi trade: scarto per regola 10.
