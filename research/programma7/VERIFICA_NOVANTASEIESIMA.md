# Verifica della prova 158 (`NOVANTASEIESIMA.md`, commit 810c620) — modalità verifica

Fatto il 15 novembre 2026 da strategy-researcher. Nessuna variante calcolata, nessun commit, registro e regole non toccati.
Controllato: le regole sono committate (810c620, 15 novembre 06:12, prima di ogni calcolo); il registro ha le righe 157 e 159 (il numero 158 è libero
per questa prova); i caricatori citati esistono (`prima.esegui`, `te.conto`, `cs.spese_a_limite`, `es.ore_di`, `ast.corretto_famiglie`, `ast.mazzo`).
Il controllo dei dati (buchi dell'archivio) non è stato lanciato: in modalità verifica non si calcola; va fatto all'inizio dell'esecuzione.

**Esito: la prova NON si esegue senza interpretazioni.** Ci sono 7 ambiguità sullo stop (A1-A7), 5 sulla liquidazione (B1-B5), 2 sul criterio dello
stop (C1-C2), 3 sui rendimenti (D1-D3), 4 sullo Sharpe corretto (E1-E4), più 2 su registro e conti (F1-F2). Per ognuna la lettura proposta.
Quelle da decidere davvero (cambiano i numeri): A1, A2, A3, A5, B2, D1, E1.

## A. Lo stop

**A1. Il pavimento non fa niente, o c'è un errore.** Il livello di scatto è «il più alto fra 0,65 × massimo e 0,65 × capitale della fase». Il massimo parte
dal capitale della fase e non scende mai, quindi 0,65 × massimo è sempre ≥ 0,65 × capitale: il pavimento non conta mai e «pavimento superato» (conto già
sotto il pavimento) può succedere solo per un salto fra un'ora e l'altra. Il pavimento ha senso solo se il massimo parte da un valore più basso del capitale
(per esempio dopo le spese di apertura). *Lettura proposta*: capitale della fase = valore del conto alle 00:00 della ripartenza **prima** delle spese di
apertura; il massimo parte dallo stesso valore e include le chiusure orarie successive (la prima ora è già al netto delle spese di apertura); la formula del
livello si applica com'è scritta, anche se di fatto vale sempre 0,65 × massimo; lo si scrive nel rapporto. «Pavimento superato» = la chiusura oraria è già
sotto il livello di scatto (di quanto: livello meno valore).

**A2. Prezzi e spese alla chiusura.** «Prezzi di chiusura di quell'ora» + «commissione 0,05% più lo scarto sul valore chiuso». *Lettura proposta*: si chiude alla
chiusura della candela a 1 ora h (cioè alle ore h+1:00); spesa = somma sulle monete di |peso corrente in valore| × `costi_moneta` (0,05% + scarto 0,01% o 0,02%
per moneta; è già il vettore `sc.costi_moneta`), mai a limite; il valore delle posizioni è quello alle chiusure orarie (pesi × rapporto di prezzo), non il
valore iniziale. Nessun credito sulla perdita oltre il livello.

**A3. Il valore dell'ora e il suo rapporto con la serie giornaliera.** La serie giornaliera di `te.conto` usa i rendimenti giornalieri `R` del pannello e **somma**
i rendimenti per settimana (`per_settimana`: somma, non composizione). Le candele a 1 ora danno un altro conto (prezzo delle 00:00 e dell'ora 23 possono
differire da `R` di un soffio; il funding non c'è nelle ore). *Lettura proposta*: (i) i giorni normali (senza stop e senza ripartenza) hanno lordo, spese,
funding di `te.conto` e `cs.spese_a_limite` su `m × W`, come rendimento del giorno sul capitale delle 00:00; (ii) le candele a 1 ora servono solo per scoprire
l'ora dello stop, la liquidazione e la discesa dentro la giornata, e per il solo giorno dello stop il rendimento è calcolato con le ore (lordo fino all'ora
dello stop, meno spese del giro delle 00:00, meno spese di chiusura); (iii) prezzo di riferimento delle 00:00 = apertura della candela dell'ora 0 del giorno D;
(iv) si scrive la differenza media fra la chiusura dell'ora 23 e `R` giornaliero (controllo di coerenza, non soglia); (v) capitale a ogni mezzanotte =
capitale precedente × (1 + netto del giorno, con funding); dentro il giorno il funding non c'è (dichiarato nelle regole), quindi il valore orario è al lordo del
funding del giorno.

**A4. Funding e spese del giorno dello stop.** Non scritto. *Lettura proposta*: funding del giorno dello stop = funding del giorno × (ore trascorse / 24), con
le ore = h+1; spese del giro delle 00:00 pagate comunque (già nel valore orario); niente funding dopo.

**A5. Il «primo lunedì almeno 3 giorni dopo».** Non è detto da quale istante si contano i 3 giorni. *Lettura proposta*: dal giorno di calendario (UTC) in cui cade
l'ora dello stop, anche se scatta all'ultima ora; ripartenza = il primo lunedì D con D ≥ giorno dello stop + 3, alle 00:00 UTC (stop di giovedì → lunedì dopo,
4 giorni; di venerdì → lunedì dopo, 3 giorni; di sabato → lunedì fra 9 giorni). Se lo stop scatta all'ultima ora di un giorno e il lunedì cade 3 giorni dopo,
vale lo stesso. Se la ripartenza cade dopo il 4 ottobre 2026 si resta fuori fino alla fine. Sensibilità «dopo 1 giorno» = ripartenza alla mezzanotte
successiva al giorno dello stop (D+1); «dopo 28 giorni» = D+28 (non il lunedì); «fuori per sempre» = mai.

**A6. Spese di apertura alla ripartenza.** «Pagando le spese dell'apertura» non dice se a limite o a mercato. *Lettura proposta*: come ogni giro di G1, cioè con
`cs.spese_a_limite` (limite 0,02% dove l'ora lo permette, poi a mercato), calcolate su una matrice a due righe [zero, m × W del giorno] (variazione da zero), non
con la deriva del giorno prima. Per i giorni normali dopo la ripartenza le spese sono quelle già calcolate sulla serie senza stop (i pesi sono frazioni del
capitale e non dipendono dal suo livello); il giorno della ripartenza sostituisce le spese di quel giorno con quelle di apertura da zero. Il giorno dopo lo
stop (D+1... fino alla ripartenza) nessuna spesa di giro: la variazione «da posizioni chiuse» non si ricalcola con `cu.variazioni` sulla serie senza stop.

**A7. Il «massimo» dopo la ripartenza.** Letto: azzerato al valore del conto alla ripartenza (A1). Il primo giorno della prova (4 gennaio 2021) la fase comincia con
capitale 1 e massimo 1. *Lettura proposta*: nessuna altra fase; le ore del giorno di ripartenza contano già per il nuovo massimo.

## B. Liquidazione dentro l'ora

**B1. Quando e su quali serie si guarda.** *Lettura proposta*: il criterio «nessuna liquidazione» si valuta sulla serie **con lo stop** (fuori non c'è nulla da liquidare;
nell'ora dello stop si guarda anche l'ora stessa, perché lo stop esce alla chiusura e il caso peggiore può precedere la chiusura) per A e B; G1 (m = 1) si riporta
senza giudizio. Si scrive anche il conteggio sulla serie senza stop (descrittivo). Una liquidazione conta una volta per ora; per il criterio basta una.

**B2. Formula del caso peggiore.** Valore del conto all'ora h = capitale × (1 + somma pesi × (prezzo/prezzo delle 00:00 − 1)) − spese del giro; valore delle
posizioni = capitale × somma |peso| × (prezzo/prezzo delle 00:00), con prezzo = minimo per i pesi positivi, massimo per i negativi, nella stessa ora per
tutte le monete. Liquidazione se valore del conto ≤ 1% × valore delle posizioni. *Letture da fissare*: (i) peso = `m × W[D]` frazione del capitale alle 00:00 (non i pesi
derivati) e nessuna deriva fra le ore (quantità ferme); (ii) la spesa del giro si toglie nel conto del criterio come scritto; (iii) il capitale è quello delle 00:00 del
giorno (con la serie con stop, il capitale composto dopo le fasi precedenti; il rapporto valore/posizioni non dipende dal livello del capitale).

**B3. Candele mancanti (cosa fare dove mancano).** Per moneta-giorno senza candele a 1 ora: *lettura proposta*: nessun movimento dentro la giornata e il contributo
appare solo all'ora 23 con la chiusura giornaliera `R` (come scritto: «solo la chiusura del giorno»). Per un'ora singola mancante dentro un giorno che ha le altre:
la chiusura dell'ora precedente portata avanti, minimo e massimo = quella chiusura; si conta quante ore. Si scrive il numero di monete-giorno e la quota di
peso (m × |W|) coperta, anche per anno; rischio dentro la giornata sottostimato lì.

**B4. Margine per singola moneta («descrittivo»).** «Circa il 19%». *Lettura proposta*: formula esatta con margine iniziale 20% e mantenimento 1% del valore
corrente: venduto liquidato se prezzo/prezzo 00:00 ≥ 1,2/1,01 = 1,1881; comprato se ≤ 0,8/0,99 = 0,8081; con il massimo/minimo dell'ora; si conta per
moneta-giorno (prima ora) sulla serie senza stop, una volta sola (non dipende da m), con le monete e il loro peso in G1 (m = 1) come quota del portafoglio.
Se si preferisce la regola semplice ±19% basta dirlo: i risultati cambiano di poco.

**B5. Tetto del 60%.** Peso per moneta = |m × W| (frazione del capitale alle 00:00); giorni con peso > 60% contati per G1, A, B; non si conta la deriva dentro il giorno.
Chiaro, solo da confermare che non si include la deriva.

## C. Il criterio «stop al massimo 2 volte»

**C1.** «Toccato al massimo N = 2 volte in 5,75 anni» = numero di scatti ≤ 2 (compreso 2) nel periodo 4 gennaio 2021 – 4 ottobre 2026, per ogni variante, nella serie
con lo stop con ripartenza dopo il primo lunedì ≥ 3 giorni. *Lettura proposta*: ogni scatto conta, compreso «pavimento superato» e uno che avviene alla ripartenza
stessa; uno scatto in una fase ripartita conta come nuovo; uno scatto la cui ripartenza cadrebbe dopo la fine conta; il criterio vale per A e B (G1 si riporta). Le
sensibilità (1 giorno, 28 giorni, per sempre) hanno un numero di scatti diverso e non entrano nel criterio.

**C2. Un solo criterio a tre punti.** Il criterio 2 chiede tutte e tre: nessuna liquidazione, stop ≤ 2, e il peso per moneta si «scrive» (non è una condizione). *Lettura proposta*:
«non adatta al conto vero» se manca una delle prime due; il terzo punto è solo da riportare; «non rispetta i limiti attuali» se il peso supera il 60% in qualche giorno.

## D. I rendimenti composti anno per anno

**D1. Somma o composizione.** Nel resto del programma i rendimenti settimanali si **sommano** (`per_settimana`), mentre qui si chiede «rendimento composto dell'anno solare con lo stop».
*Lettura proposta*: indici sui settimanali come `te.esame` (t, Sharpe, anni positivi di `te.esame` se li usa); in più, per il punto 3 e per «ogni anno positivo»: composto
dei rendimenti giornalieri della serie con stop, Π(1 + r_giorno) − 1 per anno solare (1 gennaio – 31 dicembre UTC; 2021 da 4 gennaio, 2026 fino al 4 ottobre); rendimento
sul periodo = composto totale; annuo = (1 + totale)^(365/giorni) − 1; discesa a fine giorno sul capitale composto. Giorni fuori = zero. Se `te.esame` dà il suo
«anno positivo» sui settimanali sommati, si scrivono tutti e due e conta quello **composto** (come dice l'esame); se divergono lo si segna.

**D2. Spese annue e funding annuo «in punti del capitale».** *Lettura proposta*: media annua dei rendimenti giornalieri di spese e di funding (somma/anni, come `te.esame`),
con le spese giornaliere della serie con stop (compresi chiusura e riapertura). Per G1 e per A, B senza stop, e con stop.

**D3. Giorno peggiore.** Il giorno peggiore della serie con stop = peggiore rendimento giornaliero (netto a fine giorno); quello dentro la giornata = peggior valore orario / capitale delle 00:00 − 1, con le due misure (caso peggiore e chiusure). Il
«giorno peggiore» dei controlli descrittivi senza stop, come scritto.

## E. Lo Sharpe corretto

**E1. Quali serie entrano.** Le regole dicono «mazzo completo, taglio 0,5» e i nomi «158 A» e «158 B», ma non se G1 con stop entra come serie nuova (nella 155 «155 G1 stessi giorni»
sì). *Lettura proposta*: giudizio sulla chiamata `ast.corretto_famiglie({"158 A": sA, "158 B": sB}, cand)` con le serie settimanali della versione **con stop** (somma dei
giornalieri per settimana, 300 settimane intere dal 4 gennaio 2021); G1 con stop e G1 senza stop si confrontano con chiamate separate (`{"158 G1": s1}`), non insieme ad A e B,
così la famiglia di A e B non cambia perché c'è anche G1. Il conto del registro passa da 322 a 324 (le prove 157 e 159 sono in calcolo, quindi nel mazzo del giorno
della prova possono non esserci le loro serie: non entra nella formula, che conta le famiglie).

**E2. La famiglia non è garantita.** La nota «A e B stanno nella stessa famiglia di G1» è un'attesa: con lo stop le serie di A e B sono ferme in momenti diversi da G1, e
`gruppi` con taglio 0,5 usa la correlazione media del gruppo. Se A o B formano una famiglia a parte (o si fondono diversamente) il numero di famiglie cambia e il
numero corretto con lui. *Lettura proposta*: vale il numero che dà `corretto_famiglie`; si scrive il gruppo e il numero di famiglie con e senza A e B, e le sensibilità
ai tagli 0,3 e 0,7 (come nella 155), descrittive.

**E3. Periodo e serie ferme.** `ast.periodo` taglia le settimane dal 4 gennaio 2021 al 5 ottobre 2026 e toglie le settimane ferme prima della prima operata: le serie con
stop cominciano già operando dal 4 gennaio, quindi 300 settimane (o 299 se l'ultima, quella del 5 ottobre, ricade: l'indice `<= 5 ottobre` la includerebbe, ma non c'è). Da confermare
nel rapporto il numero di settimane usato per `settimane` nei candidati (300 attese). Le settimane fuori (zero) restano nella serie e nei conti di t e Sharpe: lo Sharpe usa anche le settimane ferme.

**E4. Candidati.** `candidate` = `{"158 A": {sharpe, settimane, asimmetria, curtosi}}` presi dall'esame della serie con stop (`te.esame(...)["intero"]`), come nella 155. Servono anche l'asimmetria
e la curtosi della serie con stop (molto cambiate dallo stop).

## F. Registro e conti

**F1.** Il registro delle varianti `research/trials/novantaseiesima.csv`: *lettura proposta* una riga per variante dichiarata (A, B) e una per il riferimento G1 con m = 1 (che le regole non contano
come prova: la prova «conta 2 prove»); le sensibilità e i controlli descrittivi nelle note, non come varianti. Se una variante si ferma per errore, riga con esito di errore.

**F2.** Il controllo di parità (punto 1-4) vale come nella 155; nell'ultima riga della parità il riferimento ha candele diverse (137 variazioni senza candele oggi): da riscrivere nel rapporto; il controllo
«lordo(m) = m × lordo(1)» e quello delle spese per m si fanno su serie **senza** stop, come scritto.

## Cosa serve prima di eseguire

Decisioni della sessione principale (in ordine di peso): A1 (cosa fa il pavimento), A3 (serie giornaliera dai dati giornalieri, ore solo per stop/liquidazione), A5 (da quale istante i 3 giorni), A2/A6
(spese di chiusura e riapertura), B2 (formula), D1 (composto contro somma), E1 (quali serie nel mazzo). Le altre letture si possono confermare in blocco. Per ogni lettura non decisa, eseguirò quella proposta e la scriverò in fondo al rapporto.
