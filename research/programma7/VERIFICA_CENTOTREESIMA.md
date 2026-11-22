# Verifica della prova 165 (regole in `CENTOTREESIMA.md`), 22 novembre 2026

Modalità verifica: nessun calcolo, nessun rendimento guardato, nessun file di `research/data/` aperto. Per i dati dell'archivio pubblico
(`data.binance.vision`) ho letto solo gli elenchi dei nomi dei file (richieste di elenco gratuite, senza scaricare nessun contenuto di mercato);
dei programmi ho letto il codice (`scarico_metrics.py`, `scarico_giorni.py`) e della lista `eventi_finale.csv` solo simbolo, data e ora di annuncio e di chiusura.
Regole committate: `b905724` (22 novembre 2026, 08:13 UTC). Script di verifica (non consegnati): nella cartella temporanea della sessione.

## Esito: NON eseguibile così com'è. Due punti bloccano; gli altri si chiudono con una riga prima del calcolo.

## Copertura dei contratti chiusi (punto dubbio 1)
* `eventi_finale.csv` ha **87 righe e 87 simboli diversi** (nessun contratto doppio). Le regole dicono 85 contratti e per anno 3 / 21 / 29 / 32;
  il file per data di annuncio dà 2022: 12, 2024: 19, 2025: 27, 2026: 29. I numeri delle regole non tornano con il file (vedi punto 6).
* Per **tutti e 87** i nomi dei file dell'archivio esistono: candele giornaliere (`klines/<SIMBOLO>/1d`) e `metrics` giornalieri,
  dall'inizio fino almeno al giorno prima della chiusura (chiusura = ora `h_u` del file). Quindi, **per nome di file, 87 su 87 coperti**
  (limite di 10 mancanti: non scatta).
* Buchi interni nella finestra da 135 giorni prima dell'annuncio fino al giorno prima della chiusura (quella che serve al modello):
  candele: 3 contratti con un giorno mancante, il 5 ottobre 2025 (MILK, SXP, TOKEN); `metrics`: TLM un giorno (10 maggio 2022) e
  **ICP 143 giorni (dal 18 gennaio al 9 giugno 2022)**. Gli altri 82 non hanno buchi.
* Storia corta: 1000BTTC ha `metrics` dal 26 gennaio 2022 (meno di 90 giorni prima dell'annuncio del 4 aprile 2022); 42, COMMON, RVV, MEMEFI
  e simili hanno solo 4-5 mesi di storia. Non sono errori, ma per la regola «almeno 90 giorni» hanno righe valide solo in parte.
* **Attenzione, i file continuano dopo la chiusura.** Per 78 dei 86 contratti controllati l'archivio ha candele giornaliere **fino a oggi o a date
  fuori dalla chiusura vera** (per esempio ANT, CVX, OMG, ICP, TLM, SC, BLZ, CVC, tutti i 2025 e 2026 fino al 21 novembre 2026); i `metrics` di molti
  finiscono a date di pulizia dell'archivio (15 luglio 2024, 10 marzo 2025, 23 gennaio 2026, 15 ottobre 2026) che non sono la chiusura. Senza aprire i
  dati non posso dire se quei giorni siano candele vere (contratto ancora vivo, o rinviato come OMG, AKRO, BLZ) o riempite. Quindi **l'ultimo file
  dell'archivio non dice quando il contratto è stato chiuso**: la chiusura la dà solo l'annuncio.

## Ambiguità e punti non eseguibili

1. **BLOCCANTE: l'interesse aperto non è disponibile per l'universo che serve.** Le regole dicono di leggerlo da `research/data/p6m/<SIMBOLO>.pkl`.
   Ma `scarico_metrics.py` (docstring e `giorni_che_servono`) scarica solo «le monete e i giorni che servono alle prove settimanali fra le 100 monete più
   scambiate (ogni settimana dell'universo e i 30 giorni prima)», dal dicembre 2021. La prova chiede invece: (a) per ogni contratto vivo ogni giorno
   (anche fuori dalle 100 più scambiate, e i contratti poi chiusi sono per lo più poco scambiati), (b) 90 giorni di interesse aperto prima di ogni giorno
   (30 + i 60 prima), (c) ogni giorno e non solo il lunedì. Il file di una moneta delle prime 100 ha al massimo 30 giorni prima di ogni lunedì: non
   bastano per la variazione (60 giorni prima) né per i giorni non lunedì, e per le monete fuori dalle 100 il file può non esistere. Non l'ho aperto (vietato),
   ma dal codice lo scarico così com'è non copre la prova. I nomi dei file `metrics` dell'archivio, invece, sì (vedi sopra).
   *Correzione proposta (la più prudente):* «Prima del calcolo la sessione principale estende lo scarico dei `metrics` (stessa funzione `riassunto`:
   valore dell'interesse aperto = ultima riga del giorno, la 23:55 UTC) a tutti i perpetui USDT del pannello giornaliero, anche chiusi, dal 1° dicembre 2021
   al 31 ottobre 2026, con verifica del CHECKSUM, in un file nuovo (non `p6m`, che non si tocca); se un contratto del pannello non ha `metrics`, non entra
   nell'universo di quel giorno e il numero di esclusi si scrive nel rapporto prima dei risultati. Se lo scarico completo non è fatto, la prova non parte.»
2. **BLOCCANTE: chi sono i contratti «chiusi» e quando.** La chiusura (e il «vivo») va fissata dall'annuncio, non dall'archivio (vedi sopra: i file
   continuano dopo la chiusura per 78 su 86). Inoltre 87 contratti includono casi che l'archivio mostra vivi oggi (ICP, TLM, SC, CVC, BLZ e altri) o rinviati
   (OMG, AKRO, BLZ: la `REVISIONE_107.md` li conta come chiusura). Le regole non dicono cosa fare di questi per (i) l'etichetta, (ii) il giorno di uscita,
   (iii) il «vivo» a D.
   *Correzione proposta:* «Un contratto conta come chiuso a partire dall'ora di annuncio `h_e` del file e la sua chiusura è `h_u` del file (come nella 107,
   senza ricontrollo); da `h_e` in poi non è più nell'universo (nessuna riga di modello oltre il giorno prima dell'annuncio, nessuna candela o interesse
   aperto dopo `h_u` si usa, anche se l'archivio li ha). Prima del calcolo si scrive nel rapporto l'elenco dei contratti il cui volume giornaliero nel pannello
   è ancora positivo più di 7 giorni dopo `h_u`: restano nel modello come chiusi, ma il rapporto dà i risultati anche senza di loro.»
3. **Il momento di ogni passo (richiesto).** Non scritto in ore. *Correzione:* «A ogni decisione D (apertura 00:00 UTC) sono noti solo i dati con ora
   precedente a D 00:00. Un annuncio è noto a D se `h_e` è prima delle 00:00 UTC di D (non basta la data). Le quattro misure del giorno t usano i giorni
   t−30 … t−1 (30 giorni interi) e t−90 … t−31 (i 60 prima); il giorno t non entra mai. L'interesse aperto del giorno x è il valore dell'ultima riga di x
   (23:55). Un contratto è 'vivo a D' se ha candele e `metrics` in tutti i 90 giorni D−90 … D−1 e non è annunciato (`h_e` < D). I giorni mancanti nei 90: il contratto non
   è ammissibile quel giorno (nessuna interpolazione).»
4. **Le etichette dell'allenamento (richiesto).** Il testo mescola due insiemi: «per ogni contratto chiuso con annuncio prima di D» e poi «una riga di un
   contratto non ancora annunciato vale no solo se t+45 ≤ D−1». Non è detto se i contratti mai chiusi o non ancora annunciati a D entrano nell'allenamento
   (cambia la frequenza di base: con soli i chiusi il modello vede quasi solo positivi e il punteggio è insensato). *Correzione:* «Le righe sono tutte le
   coppie (contratto, giorno t) con contratto vivo a t secondo il punto 3, anche contratti che poi vengono chiusi dopo D o non vengono mai chiusi, con t + 45 ≤ D−1
   (vale per positivi e negativi, per non usare ciò che a D non si sa). Etichetta = 1 se `h_e` del contratto cade fra le 00:00 di t e le 00:00 di t+45 giorni
   e `h_e` < D 00:00; altrimenti 0. Un contratto annunciato prima di t non ha righe in t (era già escluso). Per i contratti annunciati dopo D−1 l'etichetta è 0 (non
   si sa ancora)». Dove la riga di un contratto sia di un giorno t con `t + 45 > D − 1`, non entra, anche se il positivo è noto (conservativo).
5. **Ranking del giorno t.** «Posizione in classifica fra tutti i contratti vivi quel giorno»: non è detto con quali contratti si classifica un giorno di
   allenamento t (tutti i vivi, o solo i non annunciati) e come si trattano i pari. *Correzione:* «Come a D: contratti vivi secondo il punto 3 a quel giorno,
   Bitcoin ed Ether esclusi dal ranking, posizione = (rango − 1)/(n − 1) con pari a rango medio; (a) e (b) si classificano sul logaritmo naturale; (c) e (d)
   = media dei 30 giorni diviso la media dei 60 giorni prima (nessun logaritmo); un denominatore zero rende il contratto non ammissibile quel giorno.»
6. **I numeri sugli eventi.** Le regole dicono 85 contratti (3 / 21 / 29 / 32) e «la 107 ne ha usati 77»; il file ne ha 87 con distribuzione diversa.
   *Correzione:* «La fonte unica è `eventi_finale.csv` (87 righe); i numeri 85 e 3/21/29/32 della sezione "Rischi" sono descrittivi e si sostituiscono nel rapporto con
   i conti veri del file; il limite 'più di 10 mancanti' si applica alle 87 righe».
7. **Data di partenza.** Dal file: gli annunci prima del 2024-05-07 00:00 UTC sono 14 (11 nel 2022, 3 il 25 marzo 2024: i due del 6 maggio 2024 sono alle 06:00
   UTC, dopo l'apertura del 6); il quindicesimo cade il 6 maggio 2024. Con «annunciate **prima di quel giorno**» la prima data possibile è il 7 maggio 2024, quindi
   **A parte il 1° giugno 2024** e **B parte lunedì 13 maggio 2024** (martedì 7 maggio non è lunedì). *Correzione:* scrivere queste due date nelle regole, sapendo che
   dipendono dai 87 eventi e dal punto 2 (se ICP o altri vengono tolti il conto cambia, e va rifatto con la lista che si scrive prima). Gli anni dell'esame: 2024 parziale
   (A da giugno: 7 mesi; B da maggio: oltre 8 settimane), 2025, 2026 fino a ottobre.
8. **Cosa vuol dire 'forza 1,0'.** Non è definito il modo. *Correzione:* «`sklearn.linear_model.LogisticRegression(penalty='l2', C=1.0, solver='lbfgs', max_iter=1000)`,
   senza pesi e senza bilanciamento delle classi, quattro numeri già in [0,1] senza altra scalatura, intercetta non penalizzata (lbfgs), nessun seme necessario. Se il
   modello non converge, quel giorno nessuna posizione e si segnala».
9. **«Almeno 10 contratti chiusi con righe valide».** Non è detto cosa conta. *Correzione:* «contratti con almeno una riga positiva valida (etichetta 1 e t + 45 ≤ D − 1)».
10. **Meno di N monete ammissibili.** *Correzione:* «si prendono tutte quelle ammissibili, valore di ogni short = capitale / N (non /numero), il long Bitcoin = somma degli short effettivi».
11. **Capitale fisso o composto, riequilibrio.** Come nella verifica della 163: non scritto. *Correzione:* «Rendimento in frazione di un capitale fisso (nessuna capitalizzazione, come
    nelle serie 157-163: controllare nel codice), quote fisse fra una decisione e l'altra, nessun riequilibrio giornaliero; il long Bitcoin si ritara solo alle decisioni e
    quando una moneta esce per protezione, pagando le spese».
12. **Protezione del +30%.** Non detto se si guarda il massimo giornaliero o orario, né il prezzo preciso. *Correzione:* «Massimo giornaliero della candela del pannello: se supera
    prezzo di entrata × 1,30, uscita a prezzo di entrata × 1,30 × 1,01 (scarto 1% peggiore, a mercato), con spese; la moneta non rientra fino alla decisione dopo (dove può essere
    scelta di nuovo). Il giorno di entrata si guarda dal suo massimo dopo l'apertura; senza candele orarie non si ricostruisce l'ordine nel giorno».
13. **Uscita per annuncio.** «Ultimo giorno prima della chiusura»: *Correzione:* «Si esce all'apertura delle 00:00 UTC del giorno di `h_u` meno uno (l'ultima apertura con candela intera);
    se l'annuncio e la chiusura cadono nello stesso giorno, a quell'apertura la moneta è già annunciata e non si può più rientrare. Una moneta annunciata durante la tenuta ma non
    chiusa prima della decisione dopo (rinvii OMG, AKRO, BLZ) esce alla decisione dopo (esclusa dal punto 'annunciati prima di D esclusi'), non resta».
14. **Prezzo e funding.** *Correzione:* «Il prezzo del giorno D è l'apertura delle 00:00 UTC (pannello); rendimento giornaliero = apertura D+1 diviso apertura D meno 1; il funding
    del giorno si somma dal pannello (`seconda.py`), solo fino al 31 ottobre 2026, mai la stima dei 90 giorni (`seconda.riempi_funding`)».
15. **Il controllo A / B / C.** «A = giorno prima dell'annuncio» è singolare. *Correzione:* «A = tutti i giorni di tenuta di una moneta che sarà annunciata durante quella tenuta,
    fino al giorno prima di quello dell'annuncio; B = il giorno dell'annuncio (anche se a metà) e i successivi fino all'uscita; C = monete non annunciate nella tenuta. 'Le 5 monete
    migliori' = le 5 con il netto totale più alto. 'La maggior parte' = più del 50% del netto totale, solo se il totale è positivo».
16. **Il confronto con la selezione a caso.** «La media di A e di B sopra il 95° percentile» si può leggere in due modi (media dei due, o ciascuna). *Correzione:* «ciascuna variante separatamente:
    il suo rendimento netto medio settimanale deve superare il 95° percentile del suo rendimento netto medio settimanale nelle 1.000 estrazioni (stesso periodo, stesso insieme di monete
    ammissibili a ogni decisione, nuova estrazione a ogni decisione, stesse spese e stessa protezione, seme 2026); passano solo se lo superano tutte e due». Il testo dice A e B 'la media': si legge così, scritto nell'elenco finale.
17. **Spese e ultimo giorno.** Valgono come nella verifica 163: *Correzione:* «Per ogni scambio di valore V: V × (0,05% + scarto 0,01% su BTC, ETH, SOL; 0,02% le altre); posizioni aperte all'ultima apertura (1° novembre 2026) si chiudono
    pagando le spese (conservativo)». Il controllo con scarto doppio (0,04%) del punto dubbio 5 è descrittivo e non cambia la decisione.
18. **Serie settimanali e anni.** *Correzione:* «settimane lunedì-domenica, rendimento della settimana = somma dei giorni netti; anni di calendario; t = Sharpe settimanale annualizzato × radice(settimane/52); le serie
    si chiamano `centotreesima_A` e `centotreesima_B` in `nuove` di `asticella.corretto_famiglie`». Dire anche in quale famiglia si trova la 107 (la 107 non è in `nuove` come serie settimanale: confermare il nome in `asticella.py`).
19. **Punto dubbio 2 e 4.** Si chiudono con il punto 3 e 4. Il punto 5 (scarto più alto): la correzione è il controllo a 0,04% già scritto; non cambia l'esame.

## Punti verificati e a posto
* I nomi dei file giornalieri (candele e `metrics`) esistono per tutti i 87 contratti fino almeno al giorno prima della chiusura dell'annuncio.
* Il pannello giornaliero (`scarico_giorni.py`, `seconda.pannello`) include anche i contratti tolti dal listino (docstring); da usare per l'universo vivo.
* Serie di netto e famiglie: `asticella.corretto_famiglie(nuove, candidate)` come nelle altre prove.
* Il file dei risultati e dei registri: percorsi e nomi già scritti.

## Domande aperte (testuali)
1. Lo scarico dei `metrics` per tutti i perpetui USDT del pannello (anche chiusi), dal 1° dicembre 2021 al 31 ottobre 2026, lo fa la sessione principale prima del calcolo (punto 1)? Senza, la prova non parte.
2. I contratti il cui archivio continua dopo la chiusura dell'annuncio (ICP, TLM, SC, CVC, BLZ, ecc.) restano come «chiusi» dall'annuncio con i risultati anche senza di loro (punto 2)?
3. La prima decisione sono A il 1° giugno 2024 e B lunedì 13 maggio 2024 (punto 7), da scrivere nelle regole?
4. Il confronto con la selezione a caso si legge «ciascuna variante sopra il suo 95° percentile» (punto 16)?
5. Il capitale è fisso, senza capitalizzazione, come nelle prove 157-163 (punto 11)?
