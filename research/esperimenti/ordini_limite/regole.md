# Prova degli ordini limite — regole scritte PRIMA dei numeri

> **BOZZA per il proprietario (13 ottobre 2026).** Diventa «in vigore» con il suo sì, con data e ora; da lì non cambia.
> Un errore trovato dopo il lancio si corregge con una voce nuova in `risultati.md`, che dice cosa è cambiato e
> perché, e si rilancia tutto. Nessun numero viene calcolato prima del sì.

## 1. La domanda

Oggi il bot entra ed esce a mercato, e nel paper i costi valgono 0,095 R a trade: 67,59 USDT su 508 trade, di cui lo
scarto di prezzo è il 44% (ops 0607, 12 ottobre). Gli effetti trovati dalla ricerca valgono 0,04-0,09 R prima dei
costi (`research/confronto/risultati.md`). La domanda è una sola, in tre parti:

1. **Quanto scende il costo per trade** se l'ingresso è un ordine limite invece che a mercato?
2. **Quanti trade saltano**, perché il prezzo non torna sul limite?
3. **Il guadagno lordo peggiora?** Un ordine limite si esegue più volentieri quando il prezzo va contro: è la
   «selezione avversa». Se il lordo scende quanto i costi, il risparmio non esiste.

La prova decide se vale la pena cambiare l'esecuzione del bot (e del gate, che deve simulare la stessa cosa). **Non
cerca strategie nuove**, non promuove nessuna strategia, non tocca il vault, che è stato usato l'11 ottobre e non si
riapre.

## 2. I dati

* Dal 2020-01-01 al 2023-12-31, i dati di costruzione e di verifica delle campagne, scaricati con `research/src/dati.py`
  nelle cartelle `research/data/insample/<SIMBOLO>/` e verificati con le impronte delle campagne (`impronte.json`).
  Nessun dato oltre il 2023-12-31.
* Per ogni strategia: candele last e mark al suo timeframe (30 minuti aggregati da 15 come nelle campagne), funding,
  e BTCUSDT dove la strategia lo usa.

## 3. Le strategie, scelte prima (e perché)

Nove strategie delle campagne, con il codice già sul branch principale (`research/campagne/<SIMBOLO>/codice/`): le
tre del vault e sei fra quelle con un effetto lordo misurato e cadute ai costi. Nessun'altra si aggiunge dopo.

| Strategia | Cos'è | Timeframe, direzione | Perché |
|---|---|---|---|
| BTCUSDT-V10 | rottura dall'apertura del giorno (Williams) | 1h long | candidata del vault: profit factor 1,067 contro 1,10 |
| BNBUSDT-045 | cali bruschi in tendenza, fine settimana | 1h long | candidata del vault |
| ADAUSDT-037 | rottura dell'intervallo d'apertura con due filtri | 15m long | candidata del vault |
| BTCUSDT-V35 | ultima mezz'ora del giorno UTC | 30m short | la famiglia più ripetuta; t 3,58, caduta ai costi doppi |
| ETCUSDT-033 | ultima mezz'ora del giorno UTC | 30m short | stessa famiglia, altra moneta; t 3,62, caduta ai costi doppi |
| SOLUSDT-023 | ultima mezz'ora del giorno UTC | 30m short | stessa famiglia; t 2,78, caduta ai costi doppi |
| AVAXUSDT-V-12 | ultima mezz'ora del giorno UTC | 30m short | stessa famiglia; t 3,52, caduta ai costi doppi |
| FILUSDT-016 | ritardo di FIL rispetto a BTC | 1h long | t 2,35, caduta ai costi doppi (R −0,004) |
| DYDXUSDT-008 | ritardo di DYDX rispetto a BTC | 1h long | passò la Fase 4, in validazione −0,178 R |

Se il tempo lo permette, in coda e solo come informazione: GRUPPO-048 (ritardo delle monete dopo un'ora forte di
BTC, 1h long, sulle 80 monete del gruppo, t 2,06 contro soglia 2,16).

## 4. La regola di esecuzione

### 4.1 L'ordine
Alla chiusura della barra di segnale `k`, la strategia mette un ordine limite al prezzo **P = chiusura della barra
`k`**: un acquisto a P per un long, una vendita a P per uno short. Nessuno scostamento da P.

### 4.2 La validità
L'ordine vale **per la sola barra `k+1`** (una barra del timeframe della strategia: 15 minuti, 30 minuti o 1 ora). Se
alla chiusura di `k+1` non è eseguito, è annullato: il trade non esiste e si conta come **saltato**.

### 4.3 Quando si considera eseguito
* Long: eseguito se il minimo della barra `k+1` è **strettamente sotto** P (il prezzo deve attraversare il limite:
  la posizione in coda non si conosce, e «toccato» non basta). Prezzo di riempimento: P, oppure l'apertura di `k+1`
  se è già sotto P (il mercato apre più in basso: si compra meglio).
* Short: simmetrico. Eseguito se il massimo di `k+1` è strettamente sopra P; riempimento a P, o all'apertura se è già
  sopra.
* Dentro la barra `k+1` il momento del riempimento non si conosce: vale la convenzione del motore, la peggiore per il
  trade (lo stop può scattare nella stessa barra dopo il riempimento, regola «stop prima»).

### 4.4 Dimensione, stop, uscite
* Quantità = capitale × rischio / |P − stop|, con lo stop calcolato dalla strategia come oggi.
* Stop, incassi, trailing, uscita a tempo, filtri, periodi, semi: **tutto come nelle campagne**. Le uscite restano
  **a mercato**.

### 4.5 I costi
* Ingresso eseguito: commissione **maker 0,02% per lato**, scarto di prezzo **zero** (il limite è il prezzo).
* Uscite: come oggi, commissione **taker 0,05% per lato** più lo scarto della fascia della moneta
  (`scheda_moneta.md`, `research/config/parametri.yaml`). Funding come oggi.
* Le commissioni sono quelle del livello base dei futures USDⓈ-M di Binance (taker 0,05%, maker 0,02%), già scritte
  come «da confermare» in `parametri.yaml`: valgono anche qui con la stessa riserva.

### 4.6 Varianti di sensibilità, scritte prima (si riportano, non decidono)
* (a) «toccato»: eseguito se il minimo è **minore o uguale** a P (versione ottimista).
* (b) validità di **due** barre invece di una.
* (c) anche le uscite «a segnale» (non gli stop, non il tempo) con ordine limite alla chiusura della barra del
  segnale d'uscita, validità una barra; se non eseguito si esce a mercato all'apertura della barra dopo.

## 5. Le corse, per ogni strategia

1. **M**: esecuzione a mercato, come nella campagna. Deve riprodurre i numeri della consegna (parità, come l'11
   ottobre per il vault): se non li riproduce, STOP e si cerca l'errore prima di tutto il resto.
2. **L**: esecuzione con la regola della sezione 4.
3. **(b)-M e (b)-L**: le entrate casuali con la stessa uscita (la baseline (b) delle campagne, 200 simulazioni, semi
   0-199, stessi ingressi casuali), eseguite a mercato e con la regola limite. Così il risparmio di costi non viene
   scambiato per un vantaggio: anche il caso risparmia.
4. Le varianti (a), (b), (c) della sezione 4.6, solo in L.

## 6. Le misure (per strategia, sull'intero 2020-2023 con l'R per anno; costruzione e validazione anche separate)

* Trade eseguiti e saltati; **tasso di esecuzione** = eseguiti / segnali.
* **R medio lordo e netto** in M e in L; **costo medio in R** in M e in L.
* **R medio in M dei trade che in L saltano**: dice se saltano i migliori.
* t contro la (b) nella stessa esecuzione (M contro (b)-M, L contro (b)-L); profit factor; R senza i 3 migliori.
* Sulle nove strategie insieme: mediana del tasso di esecuzione, del risparmio di costo e della differenza di lordo.

## 7. Le soglie, scritte prima

Decidono tre condizioni, sulle mediane delle nove strategie:

* **E1, eseguibile:** tasso di esecuzione mediano ≥ 70%. Sotto il 50% la prova dice «non eseguibile»: con questa regola
  il bot non farebbe i trade delle sue strategie.
* **E2, i costi scendono:** il costo medio in R scende di almeno **0,04 R** (atteso: da circa 0,095 a 0,055 o meno).
* **E3, il lordo regge:** la differenza di R lordo fra L e M, in mediana, non è peggiore di **metà del risparmio** di
  costo (R lordo L − R lordo M ≥ −0,5 × risparmio). Se cade, il mercato riempie gli ordini soprattutto quando va contro:
  il risparmio è un'illusione.

Esiti possibili, e basta: **«conviene»** (E1, E2 ed E3 valgono); **«non conviene»** (E3 cade); **«non eseguibile»** (E1
cade). Se E1 ed E3 valgono ma E2 no, «conviene poco»: si riporta il numero e decide il proprietario.

Si riporta, senza che decida: quante delle nove strategie in L battono nettamente la (b)-L con R netto positivo sul
periodo di validazione della loro campagna. È un'informazione, non una promozione: nessuna strategia esce da questa
prova come candidata, perché il periodo chiuso non c'è più.

## 8. Cosa succede dopo (scritto prima)

* **«Conviene»** → proposta al proprietario, non esecuzione: il bot in paper passa a ordini limite d'ingresso con
  questa regola (il percorso live del bot, mai usato, entra già con ordini limite: `parametri.yaml`, nota
  `commissione_taker_per_lato`) e il gate simula la stessa regola; si rimisura in paper. Il gate resta, per la
  selezione, quello che i suoi numeri dicono.
* **«Non conviene»** o **«non eseguibile»** → la voce si chiude con questo numero; i costi restano quelli di oggi e
  l'unica strada per un vantaggio è un'informazione nuova all'ingresso.
* In nessun caso da questa prova nasce una strategia.

## 9. Limiti, detti prima

* Una regola sulle candele non vede il libro degli ordini né la coda: «strettamente attraversato» è una scelta prudente,
  «toccato» quella ottimista; il vero sta in mezzo e non lo misura nessuna delle due.
* Le uscite restano a mercato, con lo scarto stimato per fascia di volume, non misurato sui riempimenti.
* Il 2020-2023 ha liquidità e scarti diversi dal 2026: il risparmio in R è una stima dell'ordine di grandezza.
* Nove strategie scelte perché avevano un effetto lordo: la prova dice cosa succede ai costi e al lordo di quelle, non
  che quelle funzionino.

## 10. Gli strumenti

* Un parametro nuovo del motore di ricerca (`research/src/motore.py`): esecuzione dell'ingresso «mercato» (oggi) o
  «limite» con validità in barre e condizione «attraversato» o «toccato»; nessun cambiamento al percorso «mercato».
  Test su candele sintetiche: eseguito, saltato, apertura oltre il limite, stop nella stessa barra. Voce nel
  `CHANGELOG.md` della ricerca.
* Uno script di prova in questa cartella che, per ogni strategia, fa le corse della sezione 5 con il codice della
  campagna, e scrive `risultati.md` con gli SHA-256 di `motore.py`, `dati.py`, `statistica.py`, `parametri.yaml`,
  dello script e di questo file al momento del lancio.
* Ordine di lavoro: strumenti e test → parità M su tutte e nove → L e (b) → varianti → `risultati.md`. Nessun numero
  di L prima che la parità M sia passata.
