# Collaudo del metodo, protocollo 3: le regole di dettaglio

Scritto dal coordinamento il 16 ottobre 2026, **prima di qualunque calcolo delle prove** (sezione 13bis del
protocollo: «i dettagli che il testo lascia aperti si scrivono in `collaudo_3/regole.md` e si committano prima
del primo calcolo»). Il testo che decide e' `research/PROTOCOLLO_3.md`; qui ci sono solo i dettagli che il
testo non fissa. Si approvano insieme agli esiti allo STOP del Passo 0.

Parte 1: le scelte degli strumenti, che valgono anche per la ricerca. Parte 2: i dettagli delle tre prove.

## Parte 1 — Le scelte degli strumenti (`research/src/catalogo3.py`, `motore3.py`, `statistica3.py`)

Ogni scelta e' scritta nel codice con l'etichetta `SCELTA` o nei commenti della funzione.

### Indicatori (sezione 7.2)

1. **Medie di Wilder** (RSI, ATR, ADX): il primo valore e' la media semplice dei primi n valori, poi
   media = (precedente × (n − 1) + valore) ÷ n. È il metodo di Wilder originale.
2. **Vero range**: parte dalla seconda candela (la prima non ha una chiusura precedente).
3. **RSI**: se la media dei ribassi e' zero vale 100; se anche quella dei rialzi e' zero vale 50.
4. **Stocastico**: minimo dei minimi e massimo dei massimi delle ultime 14 candele, corrente compresa; se
   coincidono, il %K grezzo vale 50.
5. **ATR percentile**: la percentuale delle 500 candele precedenti con ATR/chiusura **strettamente minore**
   di quello attuale; "sopra il 70°" vuol dire piu' di 70, "sotto il 30°" meno di 30.
6. **E11 (funding)**: una soglia di +0,03% o +0,05% vuol dire "funding sopra la soglia", una di 0,00% o
   −0,01% "funding sotto". La candela del segnale e' la prima che inizia a un regolamento o dopo; una candela
   che inizia esattamente all'istante del regolamento conta come "la prima dopo" (come nella 9.5).
7. **Sessioni** e **giorno della settimana**: si guarda l'ora di apertura della candela (UTC).
8. **E10**: candele che aprono fra le 08:00 e le 16:00 UTC; un solo segnale al giorno, la prima chiusura
   oltre il range. **VWAP, range asiatico ed E10** valgono solo se dall'inizio del giorno non manca nessuna
   candela: una sola candela mancante blocca E10 e F7 per il resto di quel giorno.
8bis. **E5**: "dentro le bande" comprende i bordi. **E8**: la condizione «%K sotto 20» (o sopra 80) si guarda
   sulla candela del segnale. **ATR percentile**: con valori tutti uguali la posizione vale 0 (conta come
   "bassa", mai come "alta").

### Riscaldamento e buchi (7.8, 9.6)

9. Una candela puo' dare un segnale solo se dall'inizio del tratto senza buchi sono passate almeno w candele:
   w = 3 × il periodo piu' lungo degli indicatori ricorsivi (EMA, RSI, ATR, ADX, MACD), oppure il periodo
   pieno degli altri se e' piu' lungo (le candele che servono perche' siano definiti alla candela del segnale
   e a quella prima). Per il MACD conta 26 (quindi 78); per l'ATR percentile 3 × 14 + 500 = 542.
10. Gli indicatori si calcolano senza interruzioni anche attraverso un buco; dopo un buco il riscaldamento
    ricomincia (nessun segnale per w candele).

### Motore (sezioni 6, 7.6, 7.7, 9)

11. **Serie dello stop: last o mark**, il primo dei due che tocca (e' quello che fa il bot in paper,
    `config/bot_3.md`, punto 1). Il **salto** all'apertura si guarda sul last: se il last apre gia' oltre
    lo stop si esce all'apertura.
12. **Liquidazione**: prezzo di Binance in margine isolato con la leva del bot (2) e il margine di
    mantenimento di BTCUSDT (0,40%); si controlla per prima nella candela, sul mark (prudente). Con una
    liquidazione si perde il margine.
13. **Dimensione**: capitale fisso 10.000 USDT, rischio 1% del capitale iniziale, leva massima 2 (la leva di
    base del bot). Un trade oltre la leva massima si riduce e si conta. Gli R non dipendono dalla dimensione.
14. Se manca la candela subito dopo il segnale (buco nei dati), il trade non si apre.
15. **Ordine limit**: la validita' si misura in tempo (1 o 3 durate di candela dopo la candela del segnale).
    Nella candela di esecuzione conta solo lo stop: se il prezzo lo tocca si esce **al prezzo dello stop**,
    anche se la candela era gia' aperta oltre (l'ingresso al prezzo limit, in quel caso, e' gia' un'ipotesi
    sfavorevole). Il massimo per il trailing comprende anche la candela di esecuzione.
16. **Uscita a fine giornata (U2s)**: all'apertura della prima candela, dopo quella d'ingresso, che inizia
    alle 21:00 UTC o dopo, guardando l'ora del giorno: un ingresso alle 22:00 o alle 23:00 esce quindi alle
    21:00 del giorno dopo (la mezzanotte non e' "21:00 o dopo").
17. **Funding**: valore della posizione = quantita' × mark price all'istante del regolamento (l'apertura
    della candela mark che lo contiene; su 12h e 1d, dove il regolamento puo' cadere dentro la candela, si
    usa la sua apertura). Un regolamento che cade **esattamente all'apertura** della candela di un'uscita per
    stop o target si conta pieno (la posizione era aperta da prima, l'ordine dei due momenti si conosce); uno
    che cade all'apertura della candela in cui si esegue un ordine limit non si conta (l'ingresso viene dopo).
    La regola «solo se e' un costo» vale per i regolamenti che cadono **dentro** quelle candele, dove l'ordine
    non si conosce (la ragione scritta nella 9.5).
18. **Fine dei dati con una posizione aperta**: chiusura al prezzo di chiusura dell'ultima candela, con
    slippage e commissione taker.
19. **Metriche**: profit factor e drawdown sugli R; somma degli R per anno sull'anno dell'uscita; un trade
    con R esattamente zero sta fra i perdenti nella media dei perdenti. L'R di un trade ridotto dalla leva si
    calcola sul suo rischio iniziale vero (9.7: «÷ rischio iniziale in USDT»), quindi non dipende dalla
    riduzione; le percentuali sul capitale non si usano.
19bis. **Buchi dentro un trade**: la validita' di un ordine limit si misura in tempo, quindi le candele
    mancanti la consumano; l'uscita a tempo (U2) conta solo le candele che esistono.
19ter. **Riempimento severo** (verifica 8 della Fase 4): eseguito se il minimo scende fino a limit × (1 −
    0,0005) compreso («di almeno lo 0,05%»); senza scarto il confronto resta stretto (7.7, regola 2).

### Statistiche (sezione 10 e Fase 4)

20. **Entrate casuali**: ogni simulazione e' una strategia che entra a caso. Quando e' senza posizione e
    senza ordine in attesa, a ogni candela ammessa del periodo entra con la stessa probabilita' q, senza
    guardare i prezzi ne' il candidato; il trade va come lo farebbe la variante con un segnale li' e la
    strategia torna libera alla sua uscita, come il candidato (un ordine limit non eseguito la tiene ferma
    per la sua validita'; un trade con lo stop troppo vicino non si apre). q si tara perche' la strategia
    faccia in media tanti trade quanti il candidato; si tengono le simulazioni che ne fanno esattamente
    tanti, finche' sono 1.000. Un solo generatore con seme 2026 per la taratura e per le simulazioni, in fila.
    Se nemmeno una strategia che entra appena e' libera arriva ai trade del candidato, la prova si ferma
    (STOP). **Correzione prima di qualunque prova:** la prima versione prendeva le candele in un ordine a caso e
    teneva un trade solo se ci stava fra quelli gia' presi; cosi' teneva piu' spesso i trade brevi (quasi
    sempre stop) e faceva sembrare il caso peggiore di quanto e'. L'ha trovato il verificatore indipendente
    delle statistiche: con il candidato in posizione per meta' del tempo il caso perdeva 0,07 R in piu' del
    dovuto, e su 12 candidati senza vantaggio 6 avevano un p-value sotto 0,10 (se ne attende circa 1).
21. **Robustezza (verifica 1)**: per E11 il lato (funding sopra o sotto) resta quello della variante anche
    quando la soglia si sposta. Si spostano anche i parametri fissi del catalogo usati dalla variante
    (per esempio l'ATR 14 dello stop, i periodi del MACD, la finestra di 500 candele); i multipli di
    Bollinger e le soglie di volume si arrotondano a 0,1; le soglie di ADX e dell'ATR percentile all'intero;
    la percentuale dello stop S3 allo 0,1%. Una mossa che non cambia il valore dopo l'arrotondamento non si
    prova.
22. **Blocchi (verifica 3)**: un trade sta nel blocco della sua candela d'ingresso; un blocco senza trade non
    ha R medio positivo.
23. **Trade estremi (verifica 4)**: il 5% si arrotonda per eccesso (150 trade → 8).
24. **Timeframe adiacenti (verifica 2)**: si riscalano anche validita' del limit e numero di candele di S2 e
    U2. Gli arrotondamenti all'intero (qui e nella robustezza) portano le meta' per eccesso (EMA 9 da 1h a 2h
    diventa 5). Il timeframe piu' lungo si salta solo se un elemento della variante non e' ammesso su di
    esso (una variante a 30m con E10 si prova anche a 1h).
24bis. **Robustezza delle soglie di E6 ed E8**: si sposta la soglia della direzione della variante; l'altra
    solo se la variante esce con il segnale opposto (U4), che la usa.
25. **Ritardo (9.9)** per un ingresso limit: stesso prezzo limit, ordine attivo una candela dopo.

## Parte 2 — Le tre prove

### Dati

- Le candele vere di BTCUSDT dal 2020-01-01 al 2022-09-30 (last e mark allineati, funding), dai file mensili
  di data.binance.vision con il CHECKSUM verificato. La fonte non ha BTCUSDT prima del 2020-01
  (`config/parametri_3.yaml`, `fonte_dati`).

### Le serie rimescolate (13bis.1)

- Per ogni timeframe 30 serie, semi da 1 a 30 (`numpy.random.default_rng(seme).permutation`).
- La prima candela resta quella vera; per le altre si prendono i movimenti relativi: apertura ÷ chiusura
  precedente, chiusura ÷ apertura, massimo ÷ apertura, minimo ÷ apertura, volume, e le quattro quote del
  mark ÷ apertura del last. Si rimescolano insieme, candela per candela; il prezzo si ricostruisce dalla
  prima chiusura vera. Gli orari restano quelli veri (anche i buchi restano dove sono); il funding resta
  quello vero.

### Prova A (13bis.2)

- **A.1 Estrazione.** Un generatore con seme 2026. Per ogni variante finta, nell'ordine: timeframe (uno dei
  9, alla pari); direzione; filtro (alla pari fra "nessuno" e i filtri ammessi su quel timeframe, poi i
  valori alla pari); ingresso (alla pari fra quelli ammessi); conferma (alla pari fra "nessuna", C1, C2,
  C3); tipo d'ingresso (M o L alla pari; per L, k e validita' alla pari); stop (S1, S2, S3 alla pari);
  numero di uscite (1 o 2 alla pari), famiglie diverse alla pari (target, tempo, trailing, segnale opposto);
  per il tempo, U2 o U2s alla pari dove U2s e' ammesso; i valori alla pari.
- **A.2** La variante numero i (contando tutte le estratte, anche le scartate) gira sulla serie (i mod 30)
  + 1 del suo timeframe. Sotto 150 trade stimati si scarta. Tutte le estrazioni sono in
  `esiti/prova_a_estrazioni.jsonl`. Se per una variante le entrate casuali non trovano posto per tanti trade
  quanti i suoi senza sovrapporli (succede a varianti quasi sempre in posizione), la variante non ha un
  p-value: si riporta a parte e si sostituisce con le estrazioni successive dello stesso generatore, finche'
  100 varianti hanno la Fase 2 completa.
- **A.3** Fase 2 completa con `statistica3.fase2` sull'intera serie (e' tutta periodo di costruzione).
- **A.4 Passa se** al massimo 5 varianti su 100 superano la Fase 2 **e** al massimo 15 hanno un p-value
  sotto 0,10.
- **A.5 Informazioni:** distribuzione dei p-value per decimi, R medio delle 100, R medio delle entrate
  casuali; per chi supera la Fase 2, la Fase 4 con le serie dello stesso seme dei timeframe adiacenti.

### Prova B (13bis.3)

- **B.1** Le regole B1, B2, B3 del testo, scritte in `collaudo.py` (`REGOLE_B`).
- **B.2 Il vantaggio.** La serie si costruisce una candela dopo l'altra; alla chiusura di ogni candela si
  calcolano MACD(12, 26, 9) e ATR(14) sulla serie gia' costruita, con le stesse formule del catalogo. A un
  incrocio nella direzione della regola, a riscaldamento completo (78 candele), le 12 candele successive si
  spostano nella direzione della regola, in parti uguali, fino a P × 1,5 × ATR(14) della candela del segnale
  (la distanza dello stop); poi lo spostamento torna indietro in parti uguali in 240 candele. Gli spostamenti
  si sommano; valgono per apertura, massimo, minimo e chiusura, last e mark. Il volume non cambia. Per B3
  (limit) il segnale e' lo stesso di B1.
- **B.3 Controllo:** i segnali che il catalogo trova sulla serie finale devono essere proprio quelli a cui e'
  stato dato il vantaggio (`segnali_uguali`). Se non lo sono, la prova non vale e si cerca la causa.
- **B.4 Passa se, per ognuna delle tre regole:** con P = 0 al massimo 3 serie su 30 superano la Fase 2; e,
  mettendo insieme le prove con P = 0,3 e P = 0,6 (e 0,9 se fatta), fra quelle con un R medio netto di almeno
  0,35 R almeno l'80% supera la Fase 2. Se con P = 0,6 meno di 20 serie su 30 arrivano a 0,35 R, la prova
  di quella regola si rifa' una volta sola aggiungendo P = 0,9 su tutte le 30 serie.
- **B.5 Informazioni:** quante prove con R fra 0,2 e 0,35 superano la Fase 2, accanto a quante "dovrebbero"
  con la regola della 5.2 (R × √trade ÷ 1,2 ≥ 2); per B3 la percentuale di ordini eseguiti; l'R medio delle
  entrate casuali con e senza vantaggio. Se con il vantaggio quella media sale in media di piu' di 0,05 R,
  STOP e decide l'utente.

### Prova C (13bis.4): non eseguibile oggi

La prova C confronta il motore con il codice del bot. Dal Passo 0, punto 3 (`config/bot_3.md`, punto 3)
risulta che oggi il bot **non sa eseguire nessuna variante del catalogo** come la scrive il protocollo, nemmeno
la regola C1 a mercato: mancano gli incroci, le uscite U2, l'ingresso a mercato per strategia, e il bot
applica a tutte le strategie profit-lock, uscita dopo 96 candele e pausa dopo uno stop. Il testo prevede questo
caso solo per l'ingresso limit (C2: «la parita' si fa dopo l'aggiunta al bot e prima del Passo 8»). Per C1 il
caso non e' previsto: si chiede all'utente allo STOP (sezione 0, punto 4).

### Tempo e impronte

- Prima del lancio si stima il tempo (`collaudo.py stima`); oltre 24 ore, STOP.
- In `esiti.md`: per ogni prova i numeri, «passa» o «non passa», e le impronte SHA-256 degli strumenti con
  cui e' girata (`collaudo.py impronte`: catalogo3, motore3, statistica3, statistica, dati, guardiano,
  parametri_3.yaml, collaudo.py e questo file).
