# Prova 158 — G1 con la leva più alta (esposizione lorda 300% e 400%), con lo stop del conto vero

Regole scritte il 15 novembre 2026 da strategy-improver, **prima di ogni calcolo**: nessun risultato guardato. Richiesta del proprietario
del 15 novembre: «fai anche un'altra prova con una delle strategie G ma alzando la leva». La prova la esegue strategy-researcher
(regole da committare e verificare prima), il giudizio lo dà backtest-auditor. Il numero 158 è quello indicato nella richiesta (nel registro
l'ultima riga vista è la 156: la sessione principale controlla che la 157 sia presa da altro). Non spegne e non sostituisce niente: G1 sul
demo e nel paper restano come sono, la variante vive solo nella ricerca.

## Avviso onesto, da leggere per primo
**Alzare l'esposizione sopra il 200% vuol dire cambiare i limiti fissi del conto vero** (posizioni al massimo il 200% del conto, 60% per
moneta, leva 5: `docs/conto_vero.md`, punto 4b). Questo lo decide **solo il proprietario**, con una decisione scritta; la prova non lo
autorizza, nemmeno se l'esame è superato. Un PASS qui vuol dire solo «sul passato, con queste regole, la leva più alta ha reso di più
senza liquidazioni e con pochi stop»; non vuol dire «alzare i limiti».

## Il perché
* **Moltiplicare i pesi non cambia lo Sharpe**: rendimento, volatilità e spese lorde crescono insieme. Quello che la leva cambia davvero
  e che la prova misura: (1) il rendimento composto e la discesa; (2) i costi e il funding in valore, che crescono con i pesi mentre il
  capitale non cresce; (3) **quante volte si tocca lo stop del conto vero** (chiude tutto, riparte solo col pulsante); (4) **il rischio di
  liquidazione dentro la giornata**, che i dati a fine giornata non vedono.
* Numeri di partenza: G1 sul passato ha discesa massima −30,1% e giorno peggiore −8,5% (prova 120, `programma7/PRIMA.md`,
  `research/programma7/risultati_prima/esame.json`). Con peso ×1,5 la discesa sale intorno a −40% e ×2 oltre −50%, cioè **oltre lo
  stop del −35%**: la domanda vera è quante volte e con che effetto, non lo Sharpe. Sono stime di ordine di grandezza, non risultati.
* Perché si può provare: i pesi di G1 sono già bilanciati fra lato comprato e venduto (G1 neutra in dollari), quindi la leva alta non
  porta un rischio di direzione, solo di coda sui singoli rialzi violenti del lato venduto (esempio visto in avanti: JCTUSDT +303%).

## Il motore (fissato qui)
* `research/programma7/prima.py`, funzione `esegui`, **stesse scelte delle monete di G1** (stessi universo, segnale, `pesi_banda`): non si
  rifà nessuna scelta. Si prende la matrice dei pesi giornalieri `W` e si usa `m × W` con **m = 1 (riferimento), 1,5 (A), 2 (B)**.
* Spese e funding **ricalcolati sulla matrice nuova**: `te.conto(m·W, R, F, costo)` e `cs.spese_a_limite(m·W, R, giorni, simboli, costo)`
  (`programma6/cinquantaseiesima.py`: ordine limite 0,02% dove l'ora lo permette, poi a mercato 0,05%, scarto 0,01% su BTC, ETH e SOL e
  0,02% sulle altre, confermati il 7 novembre). Niente scorciatoie «spese per m».
* Periodo: dal 4 gennaio 2021 (`se.INIZIO`) al 4 ottobre 2026 compreso (`FINE` di `prima.py`), 5,75 anni. Il 2021 e il 2026 sono anni
  parziali e contano tutti e due per «ogni anno positivo».

## Il controllo di parità (prima di ogni altra cosa)
Letto come nelle aggiunte della prova 155 (`NOVANTATREESIMA.md`, «Aggiunta» e «Seconda aggiunta»):
1. Con m = 1 si confronta con `risultati_prima/giorni_G1.csv.gz`. È **valido se lordo, funding, giro e numero di monete coincidono entro
   1e-12 fino al 29 settembre 2026 compreso**. Se una di queste differisce prima del 30 settembre, ci si ferma e lo si scrive.
2. **Le spese del riferimento differiscono per le candele a 1 ora** (nel riferimento 6.105 variazioni su 117.045 senza candele e contate a
   mercato, oggi 137 su 117.037; giorni diversi del 2021, 2022, 2023): non è un errore. Si controlla che anche oggi il numero delle
   variazioni senza candele sia quello dei dati di oggi (circa 137) e che la differenza delle spese stia solo nei giorni con candele
   mancanti nel riferimento; il 2024 e il 2025 devono coincidere.
3. **G1 di confronto è G1 ricalcolato oggi con m = 1**, stesse spese, stesso pannello e stesse candele delle varianti. Si scrive anche il
   suo esame accanto a quello del riferimento.
4. Controlli di coerenza (non soglie, si scrivono): lordo(m) = m × lordo(1) e funding(m) = m × funding(1) entro 1e-12; le variazioni eseguite
   con il limite sono le stesse per ogni m (il peso cambia, l'ora no); le spese per m salgono quasi in proporzione.
Questi controlli valgono **prima** dello stop (senza regola di stop).

## Il conto per ora dentro la giornata (liquidazione e discesa)
* Ogni giorno D alle 00:00 UTC i pesi `m × W[D]` sono frazioni del capitale di quel momento; durante il giorno le quantità restano ferme
  (il ribilancio c'è solo a mezzanotte, come G1). Le spese del giro si pagano alle 00:00; il funding si somma alla chiusura del giorno
  (alla chiusura, non per ora: è piccolo, si dichiara).
* Per ogni moneta con peso non nullo si usano le **candele a 1 ora** (`es.ore_di`, le stesse di `spese_a_limite`). Il valore del conto
  all'ora h = capitale alle 00:00 × (1 + somma dei pesi × (prezzo di h / prezzo delle 00:00 − 1)) − spese del giro.
* **Misura principale, il caso peggiore dell'ora**: per ogni ora, i comprati al minimo e i venduti al massimo **tutti insieme** (limite alto
  del rischio, perché i prezzi non toccano gli estremi nello stesso minuto). Con questo si misura la **discesa dentro la giornata** e la
  liquidazione del criterio.
* **Misura descrittiva, le chiusure orarie**: stesso conto con le sole chiusure di ogni ora (stima più vicina al vero). Si scrivono
  tutte e due: discesa massima, giorno peggiore e quante ore sotto lo stop.
* **Giorni senza candele a 1 ora per una moneta** (pochi, 2021-2023 per le monete nuove): per quella moneta si usa solo la chiusura del
  giorno; si conta quante monete-giorno e che quota del peso (il rischio dentro la giornata è lì **sottostimato**: lo si scrive).

## Il margine di mantenimento di Binance, in modo semplice
Il conto vero e il demo usano il **margine unico** (`CROSSED`, `bot/portafoglio/demo_binance.py`): una posizione perdente può usare tutto il
capitale. Regola della prova:
* **Liquidazione** all'ora h se: valore del conto (con i prezzi del caso peggiore) ≤ **1% del valore totale delle posizioni** a quei
  prezzi (cioè 1% × la somma dei valori assoluti). Il 1% è una semplificazione dichiarata: Binance usa scaglioni da 0,4% (BTC, ETH,
  posizioni piccole) fino a 5% o più per monete poco liquide e per posizioni grandi; si ripete con **2,5%** come controllo descrittivo di
  sensibilità, senza cambiare l'esame. Commissione di liquidazione non contata (aggiungerebbe perdita).
* **Controllo per singola moneta**, descrittivo, come se il margine fosse separato: con leva 5 il margine iniziale è il 20% del valore; una
  posizione venduta si liquida se il prezzo sale di circa il 19% sulle 00:00 (20% meno l'1%), una comprata se scende del 19%.
  Questo controllo **non dipende da m** (leva e margine per moneta sono uguali) e si scrive quante volte, quali monete e che quota del
  portafoglio. Serve al proprietario perché il demo ha leva 5 per moneta.
* Peso per moneta e limite del 60% del conto: si scrive il peso massimo di G1 per moneta e quello con m = 1,5 e 2 (peso × m), e quanti
  giorni superano il **60%** (descrittivo; se superano, la variante non rispetta i limiti attuali nemmeno oltre il 200%).

## Lo stop del conto vero, come regola della prova
Regola scritta in `docs/conto_vero.md` (punto 4b e 4k): stop a **−35% dal massimo** del conto, con il pavimento al **65% del capitale della
fase**; si applica **a tutte le varianti e anche a G1 (m = 1)**, perché il confronto sia lo stesso.
* **Quando scatta**: alla prima ora in cui il valore del conto (chiusura oraria, misura principale per lo stop; il caso peggiore dell'ora
  è solo per la liquidazione) scende a 0,65 × il massimo (il massimo è quello delle ore dall'inizio della fase) oppure a 0,65 × il capitale
  della fase, il livello più alto dei due.
* **Cosa succede**: si chiude tutto a quell'ora, ai prezzi di chiusura di quell'ora, pagando commissione 0,05% (a mercato) più lo scarto
  sul valore chiuso; **la perdita oltre il livello dello stop si tiene** (nessun credito): se il conto è già sotto il pavimento si segna
  «pavimento superato» e di quanto.
* **Dopo lo stop (lettura scelta)**: si resta **fuori (zero rendimento, nessun interesse) fino a mezzanotte del primo lunedì che cade almeno
  3 giorni dopo lo stop**; lì **riparte con i pesi di G1 di quel giorno**, pagando le spese dell'apertura, con il **capitale della fase = il
  valore del conto in quel momento** e il massimo azzerato su quel valore (come «riparti» del punto 4k, che ricomincia una fase nuova).
* **Perché questa lettura**: lo stop del conto vero chiude tutto e riparte **solo con il pulsante** del proprietario, che per decisione
  del 1° novembre riceve i numeri ogni lunedì: il primo lunedì utile dà un tempo realistico di reazione (da 3 a 9 giorni). «Fino al
  ribilancio dopo» sarebbe come non avere lo stop (si rientra la mattina dopo, a metà di un crollo) e «fino a un riavvio senza data»
  non è misurabile. Il restare fuori toglie anche i rimbalzi: costo vero dello stop, che la prova deve mostrare.
* **Sensibilità descrittive, non varianti**: ripartenza dopo 1 giorno e dopo 28 giorni; stop senza ripartenza (fuori per sempre).
* Si segnano: quante volte scatta, le date, la durata fuori, il rendimento perso nelle giornate fuori (di G1 senza stop) e il valore del conto
  al momento dello stop.

## Varianti (fissate, al massimo 2; nessun'altra dopo i risultati)
* **A**: esposizione lorda 300% (ogni lato 150%, m = 1,5).
* **B**: esposizione lorda 400% (ogni lato 200%, m = 2).
Riferimento: G1 con m = 1 (esposizione 200%), anche con lo stop. Conta **2 prove**.

## L'esame
**1. Quello approvato dal proprietario (9 novembre)**, sulla serie **con lo stop** (rendimenti giornalieri dopo le spese, fuori = zero):
* netto positivo dopo le spese e il funding;
* **ogni anno positivo**, 2021 e 2026 parziali compresi (rendimento composto dell'anno solare con lo stop);
* t almeno 3 (media diviso errore standard sui rendimenti settimanali, come `te.esame`);
* **Sharpe corretto almeno 0,80** con `corretto_famiglie` di `programma6/asticella.py` (mazzo completo `mazzo()`, taglio 0,5; esempio
  `audits/repro/prova28_2026-11-11.py`, voce 11).
**Nota, scritta prima**: con la leva lo Sharpe quasi non cambia, quindi **il numero corretto è quasi quello di G1**; A e B sono serie con
correlazione vicina a 1 con G1 (molto sopra il `TAGLIO`), quindi stanno **nella stessa famiglia di G1** e il conto delle famiglie non sale.
Passare questo esame **non dice che la leva aiuta**: dice solo che la strategia di base resta valida. Le differenze vere stanno nei punti 2 e 3.

**2. In più, il criterio per il conto vero** (se manca anche uno solo, la variante è «non adatta al conto vero» anche con l'esame 1 superato):
* **nessuna liquidazione**, con il margine del 1% e il caso peggiore dell'ora (misura principale); la sensibilità al 2,5% e le chiusure
  orarie si scrivono accanto;
* **lo stop toccato al massimo N = 2 volte in 5,75 anni**. Motivo: ogni stop chiude tutto, richiede un'azione del proprietario, fa
  perdere almeno 3 giorni di mercato e almeno le spese di chiusura e riapertura; due volte in 5,75 anni è circa una ogni tre anni, il
  massimo di interventi che un conto piccolo gestito dal telefono può chiedere senza diventare un lavoro. Sopra 2 il costo operativo
  supera il guadagno di leva che la prova mostrerà. N è scritto prima e non si cambia dopo i risultati;
* il peso massimo per moneta con la leva (peso × m) si scrive; sopra il 60% del conto non è un fallimento della prova ma una violazione dei
  limiti attuali, da segnalare al proprietario.

**3. Il rendimento composto anno per anno, con lo stop, contro G1**: tabella 2021 (parziale) … 2026 (parziale) per G1, G1 con stop, A e B
con stop; poi rendimento composto sul periodo, rendimento annuo, discesa massima (a fine giorno e dentro la giornata), spese annue e
funding annuo in punti del capitale, giorno peggiore. **Giudizio descrittivo**: la leva «rende di più» solo se il composto con lo stop
supera quello di G1 con stop **e** i criteri del punto 2 sono tutti rispettati; non si dà un PASS su questo, si scrivono i numeri.
La risposta alla domanda del proprietario è questo punto 3 più il punto 2.

## Controlli descrittivi (non varianti)
Serie senza stop di A e B (discesa, giorno peggiore); correlazione dei rendimenti giornalieri di A e B con G1 (attesa 1); le 10 giornate
peggiori con la moneta responsabile; quota di giorni con perdita oltre il 10% del capitale; peso totale a rischio del lato venduto nei giorni
in cui una moneta venduta sale oltre il 30%.

## Cosa si consegna
Rapporto su file `research/programma7/RISULTATI_NOVANTASEIESIMA.md`, serie giornaliere in `research/programma7/risultati_novantaseiesima/`,
script `research/programma7/novantaseiesima.py`, registro delle varianti in `research/trials/novantaseiesima.csv` (non si tronca, anche
se fallita); a schermo al massimo 20 righe. Non si tocca `research/REGISTRO.md` (lo aggiorna la sessione principale). Nessun vault per data.

## Testo della riga del registro
| 158 | **G1 con la leva più alta** (richiesta del proprietario del 15 novembre; regole di strategy-improver): pesi ×1,5 (esposizione lorda 300%, A) e ×2 (400%, B) sulle stesse scelte di G1, con lo stop del conto vero (−35% dal massimo, fuori fino al primo lunedì almeno 3 giorni dopo, poi riparte), liquidazione misurata con le candele a 1 ora (margine 1%), esame approvato + nessuna liquidazione + stop al massimo 2 volte in 5,75 anni (`programma7/NOVANTASEIESIMA.md`); oltre il 200% servono nuovi limiti del conto vero, decisione solo del proprietario | 2 | da fare | da fare |

## Regole corrette il 15 novembre 2026 dopo la verifica, prima di ogni calcolo (sessione principale)
La verifica di strategy-researcher (`VERIFICA_NOVANTASEIESIMA.md`, 23 punti) ha trovato ambiguità; nessun numero è stato calcolato.
Valgono **le letture proposte nella verifica**, con queste decisioni sulle tre domande aperte:
1. **Il pavimento al 65%** (A1): con il massimo che parte dal capitale e non scende, il pavimento non conta mai; è così anche nella
   formula del conto vero (`docs/conto_vero.md`, punto 4b). La formula resta come scritta; capitale e massimo di fase partono dal valore
   prima delle spese di apertura; il rapporto lo dice.
2. **Composto** (D1): l'equity con lo stop è composta (come il conto vero), e su quella si giudicano lo stop, la liquidazione, ogni anno
   positivo e il rendimento anno per anno; lo Sharpe e il t si calcolano sulle settimane prese dall'equity composta (rendimento della
   settimana = equity a fine settimana / equity a inizio settimana − 1). Se un numero sui settimanali sommati diverge, si scrive accanto.
3. **Nessuna liquidazione** si giudica sulla serie **con lo stop** (il conto vero lo ha); la serie senza stop si scrive accanto come
   controllo, perché se Binance blocca l'indirizzo della macchina lo stop non protegge (`docs/conto_vero.md`, punto 4i).
Le altre letture (A2-A6, B2, E1, E2 e le minori) sono quelle della verifica: chiusura a mercato all'ora dello stop con i costi per moneta,
riapertura con `cs.spese_a_limite` sulla matrice dal vuoto, funding del giorno dello stop pro rata sulle ore, ripartenza al primo lunedì con
data almeno il giorno dello stop + 3, margine per moneta con la formula esatta, «stop al massimo 2 volte» = scatti ≤ 2 (ogni pavimento
superato conta come scatto), Sharpe corretto con `corretto_famiglie` sulle sole «158 A» e «158 B» e G1 in una chiamata a parte.
