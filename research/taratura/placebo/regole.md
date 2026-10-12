# Prova a placebo dell'esame delle campagne — regole scritte PRIMA dei numeri

Scritte dal coordinamento il 9 ottobre 2026, su richiesta del proprietario («ok, procedi con la prova e scrivi la
4.5»), prima di calcolare qualunque risultato. Questo file si committa e si pusha prima del lancio: l'hash del
commit va in `risultati.md`. Dopo il lancio le regole non cambiano; un errore trovato si corregge con una voce
nuova in `risultati.md`, che dice cosa è cambiato e perché, e si rilancia tutto.

## 1. La domanda

Sui prezzi **veri**, l'esame con cui una campagna promuove una variante a candidato (sezione 8 del protocollo:
batte nettamente la baseline (a) e la (b), con R medio dopo i costi positivo) e l'asticella della validazione
(p-value contro la (b)) promuovono strategie **senza vantaggio** più spesso di quanto dichiara la sezione 11?

Dichiarato (sezione 11, taratura del 7 ottobre su serie inventate): «netta» fra lo 0 e il 2% dei casi, p-value
sotto 0,10 fra il 6 e l'11%. Il limite scritto nella stessa sezione: «una persistenza di regime fra trade
distanti più di un giorno non è coperta dal blocco». Questa prova misura quel limite sui prezzi veri.

## 2. I dati

* Le 80 monete idonee che **non** sono monete di campagna (`research/universo/monete_idonee_non_campagna.csv`,
  su questo branch di coordinamento: simbolo, primo mese d'archivio, fascia di slippage). Nessuna delle 20
  monete di campagna entra nella prova. La prova vive sul branch `research/coordinamento` (sezione 5).
* Solo candele a 1 ora (klines, last price) dal primo mese d'archivio al **2023-12-31**, con il caricatore
  `research/src/dati.py` (rifiuta ogni data oltre il 2023-12-31 prima di toccare la rete), in
  `research/data/placebo/` (fuori da git). Il vault non si tocca.
* Due timeframe: 1 ora e 4 ore (aggregate dalle candele a 1 ora con `dati.aggrega_candele`, solo gruppi completi).
* Periodi: quelli di `dati.periodi_campagna(primo mese)`, come una campagna: costruzione (primo 70%) e
  validazione (resto fino al 2023-12-31).
* Il filtro della Fase 0, punto 3, come in campagna: nei mesi con volume medio giornaliero sotto 20 milioni di
  USDT (somma dei `quote_volume` a 1 ora per giorno UTC, media sui giorni del mese) la placebo e la (a) non
  aprono posizioni, e quelle barre sono vietate alla (b).
* Semplificazioni dichiarate: niente funding (effetto piccolo, ma non per forza uguale su placebo e (b): i trade
  della placebo sono a grappoli e il funding cambia col regime); serie dello stop e del mark uguali al last price.
* Una moneta con file mensili mancanti fra il primo mese e il 2023-12 si ferma con un errore scritto: nessuna
  moneta si perde in silenzio.

## 3. Le strategie placebo

Per ogni moneta, timeframe, regola e direzione (long e short separate, come la regola 6) c'è una placebo:

1. **Regola d'ingresso da manuale**, calcolata sui prezzi veri alla chiusura della barra:
   incrocio delle medie 20/50; RSI(14) che esce da 30 (long) o rientra sotto 70 (short); chiusura oltre il
   massimo (long) o sotto il minimo (short) delle 20 barre precedenti; chiusura fuori dalla banda di Bollinger
   (20, 2) inferiore (long) o superiore (short); incrocio del MACD (12, 26, 9) con la sua linea del segnale;
   rendimento a 10 barre che passa sopra (long) o sotto (short) lo zero.
2. **Lo sfasamento.** Gli indici delle barre di segnale del periodo si spostano tutti dello stesso sfasamento
   circolare d, intero uniforme fra m e L − m (L = barre utilizzabili del periodo; m = 30 giorni di barre, cioè
   720 a 1 ora e 180 a 4 ore, o L/4 se il periodo è più corto di 4m; seme = crc32 dell'etichetta
   «moneta|timeframe|regola|direzione|periodo|k»). I grappoli di segnali restano com'erano, ma cadono in
   momenti scelti a caso: la placebo **non ha nessun vantaggio** per costruzione. Mediato su tutti gli
   sfasamenti ogni barra è coperta lo stesso numero di volte; 30 giorni superano il trade più lungo e la
   finestra degli indicatori, quindi la placebo non eredita il tempismo della regola. (Prima versione, corretta
   dalla revisione prima del lancio: d fra L/4 e 3L/4 toglieva metà del cerchio, proprio quella vicina ai
   periodi in cui la regola scatta, e su serie sintetiche con un ciclo di mercato dava alle regole contrarie un
   vantaggio e alle rotture uno svantaggio, con lo stesso segno su tutte le monete.)
3. **L'uscita** (la stessa per placebo, baseline (a) e (b)), calcolata con l'ATR(14), media semplice dei true
   range, alla barra di segnale:
   per incrocio delle medie, rottura e MACD stop a 1,5 ATR e target a 2,5 ATR; per RSI, Bollinger e momento
   stop a 2 ATR, nessun target, chiusura dopo 24 barre a 1 ora e 12 barre a 4 ore (si contano le barre, non le
   ore: un buco nei dati non allunga la posizione).
4. Le prime 60 barre di ogni periodo non hanno segnali (riscaldamento). In validazione gli indicatori partono
   dalle ultime 200 barre di costruzione, che non hanno segnali.
5. Costi e dimensione delle campagne (`parametri.yaml`): commissione 0,05% per lato, slippage della fascia della
   moneta, rischio 1% a trade, leva massima 2, margine isolato, mantenimento 0,025, stop prima del target.

## 4. Il giudizio, con gli strumenti delle campagne

* **Costruzione.** Una placebo si giudica solo se ha almeno **70 trade** (altrimenti è uno scarto, come in
  campagna). Baseline (b): `motore.simula_baseline_casuale`, 200 simulazioni con semi 0..199, durata media dei
  trade della placebo, barre vietate = riscaldamento + `barre_vietate_segnale_non_valido`. Baseline (a): la
  stessa uscita entrando a ogni barra libera, `statistica.baseline_da_trade` con il blocco dei suoi trade.
  Confronto: `statistica.contro_baseline` (2000 ricampionamenti, seme 0), blocco da `statistica.lunghezza_blocco`.
* **Validazione.** Ogni placebo ha anche la sua versione sul periodo di validazione (sfasata con il suo seme):
  se ha almeno **30 trade**, p-value contro la (b) calcolata sul periodo di validazione (ingressi casuali solo
  nelle barre di validazione), come l'asticella.

## 5. Le misure e le soglie

Prima di qualunque quota, due controlli, nell'ordine; se uno manca si stampano solo i conteggi e ci si ferma:
* **Copertura:** ci sono tutte le 160 coppie moneta-timeframe (80 × 2). Gli errori si contano e si elencano.
* **Campione:** almeno 1.000 placebo valutabili in costruzione. Se sono meno, si aggiunge un secondo sfasamento
  (k = 1) a tutte le combinazioni, deciso sul solo conteggio. Le placebo del secondo sfasamento sono delle
  stesse monete: aumentano il conteggio più dell'informazione, e l'intervallo per moneta lo dice.

Le misure (il denominatore sono le placebo **valutabili** contro la (b); le non valutabili, meno di 3 blocchi
interi o la (b) che non si costruisce, si contano a parte con il motivo, e si riporta anche M1 contandole come
non nette):
* **M1** — quota di placebo «nette contro la (b)» fra quelle valutabili in costruzione (almeno 70 trade).
  Dichiarato 0-2%. **Soglia: 3%.**
* **M2** — quota di placebo con p-value sotto 0,10 in validazione, fra quelle valutabili con almeno 30 trade di
  validazione. Dichiarato 6-11%. **Soglia: 13%** (circa due errori sopra l'11% con 1.000 placebo, come il 3% sta
  sopra il 2%: con il 12% lo STOP scatterebbe per caso una volta su sette anche con un valore vero dentro il
  dichiarato).
* **Gli intervalli.** Le placebo della stessa moneta sono correlate (una moneta con regimi forti le rende nette
  insieme): l'intervallo che conta è quello al 95% che ricampiona le **monete** (2.000 ricampionamenti, seme 0);
  Wilson si riporta accanto. Si riportano anche quante monete hanno almeno una placebo nella misura e la quota
  portata dalla moneta più presente.
* **Le fasce di trade.** La taratura del 7 ottobre era su 30-70 trade; le placebo a 1 ora ne hanno spesso
  centinaia, e una persistenza di regime pesa di più quando i trade sono tanti. M1 si riporta anche per fascia
  di trade in costruzione (70-149, 150-299, 300 e oltre) e M2 per fascia in validazione (30-69, 70-149, 150 e
  oltre), ciascuna anche per timeframe. Il confronto con il dichiarato si legge sulla fascia più bassa, la più
  vicina alle condizioni della taratura; la decisione resta sul totale, e il rapporto dice quali fasce la portano.
* Solo informative, non decidono: quota di «candidati» (netta contro (a) e (b), R medio positivo, nessuna
  violazione di liquidazione), quota di p sotto 0,10 in costruzione, quota «netta» in validazione, e le misure
  per timeframe, direzione, regola e uscita.
* **Riproducibilità.** Un file di esiti per sfasamento (`esiti_k<k>.jsonl`); ogni riga porta l'hash del commit
  del codice, e il lancio rifiuta codice non committato e righe di un'altra versione.

## 6. Cosa succede dopo (scritto prima)

La decisione si prende sulle stime puntuali del totale. Se una soglia cade dentro l'intervallo per moneta, il
rapporto lo dice: «esito al limite».

* **M1 ≤ 3% e M2 ≤ 13%** → «l'esame regge sui prezzi veri». Si procede con la versione 4.5 e le 17 monete; i
  numeri entrano nella sezione 11 del protocollo al posto della sola taratura su serie inventate.
* **M1 > 3% oppure M2 > 13%** → «l'esame è troppo generoso sui prezzi veri». STOP. Il coordinamento propone una
  correzione della regola e la riprova con una nuova prova a placebo (sfasamento k = 2, stesse regole, file
  separato) e la porta al proprietario. Se la soglia è superata solo nelle fasce con molti trade, la correzione
  riguarda le varianti con molti trade (per esempio un blocco più lungo) e si riprova su quelle fasce. Se il
  proprietario adotta la correzione, vale per tutte e 20 le monete: BTCUSDT, ETHUSDT e SOLUSDT si rifanno (il
  candidato di BTCUSDT resta solo nel conteggio m dell'asticella, Passo 2) e le 17 partono con la regola
  corretta. Il proprietario decide.

## Revisione prima del lancio (9 ottobre)

Due revisori indipendenti, prima di qualunque numero sui prezzi veri (solo serie sintetiche): uno sul disegno
statistico, uno sulla fedeltà del codice agli strumenti delle campagne. Cambiato per loro: lo sfasamento (punto
3.2, il problema che bloccava), il filtro di liquidità, l'uscita a tempo contata in barre, il denominatore delle
valutabili, la soglia di M2 da 12% a 13%, l'intervallo per moneta, le fasce di trade, i controlli di copertura e
di campione prima di qualunque quota, gli errori scritti riga per riga, un file e una versione del codice per
sfasamento.

## 7. Cosa la prova non dice

Non dice se esistono vantaggi veri; non prova le verifiche della Fase 4 (costi doppi, ritardo, robustezza),
che fermano altro rumore; usa regole d'ingresso e uscite fisse, non le idee di una campagna; le monete sono
quelle idonee del 2023, non le monete di campagna. Misura una cosa sola: quante volte l'esame scambia per
vantaggio una strategia che non ne ha, sui prezzi veri.
