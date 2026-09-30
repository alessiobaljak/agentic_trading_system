# Revisione delle voci in sospeso (30 set)

**Come leggere i numeri.**
- **MISURATO**: viene da un risultato della VPS (ops NNNN).
- **DEDOTTO**: l'ho letto nel codice.
- **STIMATO**: viene da un conto o da una simulazione nostra, non dal sistema vero.

**Parole usate.**
- **R**: il risultato di un trade in multipli del rischio. −1R è uno stop pieno.
- **Motore**: il simulatore con cui il gate giudica le strategie.
- **Fuori campione**: i giorni che il gate non aveva ancora visto quando ha scelto la coppia.
- **Margine**: la fascia dentro cui una differenza può essere solo caso.

## 1. In tre righe

- **Oggi nessuna voce in sospeso rende i trade migliori da sola.** Dal 27 set il paper è in pari (+10,19 USDT, somma dei giorni in ops 0371). I suoi numeri sono quelli che darebbe un prezzo casuale con le nostre regole d'uscita: il paper non sa dirci dove intervenire.
- **Serve rispondere a una domanda: il gate sceglie coppie con un vantaggio vero, o solo fortunate?** Le tre cose da fare adesso sono tre misure. Rispondono fra il 7 ottobre e metà novembre, senza toccare il bot, il gate o il numero di trade.
- **Non servono** F2, i ritocchi a uscite, size e freni, l'AI che legge i referti e le formule AI. Rischiare di più in paper non fa imparare più in fretta: il sistema impara in R e contando i trade, non in euro.

## 2. Classifica

### Serve adesso
1. **Scrivere prima le regole delle letture del 3, 7 e 14 ottobre** (H5-a, H5-b, conteggio unico dei segnali, sopravvivenza, regola A4).
   - Oggi il verdetto «è il bot che esegue male» del 7 ott si decide sulla media di tutti i trade, con margine ±0,25R.
   - Sugli stessi segnali il margine è ±0,16R e la differenza è solo +0,04R (ops 0371).
2. **H1-misura: salvare il «voto di affidabilità» (la t) di ogni validata** e dividere il fuori campione per voto.
   - Oggi la t c'è solo per 42 validate su 202, e sono esattamente le 42 non declassate (202 − 160, ops 0363).
3. **Un gruppo di controllo, da oggi**: una fotografia giornaliera delle conferme e un campione di candidate bocciate.
   - Il motore fa +0,12R dopo la validazione (ops 0371). Senza un confronto con le coppie scartate non si sa se il merito è della scelta del gate o del mercato del mese.
   - Il backlog H5 lo scrive già: «non fatto».

### Serve dopo (e quando)
- **H1-soglia-holdout**: chiedere una t minima all'ultimo esame. Dopo H1-misura e H5, non prima di metà ottobre.
  - È l'unica leva vera sulla scelta delle coppie.
  - In simulazione le fortunate che passano scendono dal 13,6% al 2,6% con t ≥ 1,5. Scendono però anche le buone: quelle con PF 2 dal 40,5% al 14,3% (STIMATO).
- **I2-bis: il freno ha un'uscita che non si può raggiungere.** Da sistemare prima di qualunque discorso di denaro vero.
  - Per uscire il massimo toccato mediano deve superare 1,05R.
  - Il paper è a 0,87R (ops 0366), il motore, che guadagna, a 1,03R (ops 0371), un prezzo casuale a 0,81R (STIMATO, simulazione rifatta da me).
- **Tutti i conti per gruppo in R, con un taglio al 27 set** (assorbe FR-misura). Circa 1-2 ore, dopo il 7 ott.
  - Le righe in USDT mescolano size diverse e il periodo del difetto: fino al 26 set −77,93, dal 27 set +10,19 (ops 0371).
- **Una riga «caso» accanto ai numeri del controllo** (vedi il punto 4). Circa 1-2 ore, dopo il 7 ott.
- **Pulizia dei dati che arrivano all'AI** (H2-artefatto-AI, H2-artefatto-esplorative, autopsia separata per 1 ora e 15 minuti di D6-L1). Circa 2-3 ore, insieme a H1-misura perché è lo stesso codice.
  - Il 29 set 21 dei 32 «quasi-passaggi» letti dall'AI erano un segnaposto «0,000» (ops 0341).
- **D6-IPOTESI: le idee AI servono?** Misura dopo il 7 ott, contando coppie per origine e non R: con 30 trade il margine è ±0,33R.
  - Valgono circa metà della spesa AI, ~1,52 $ al giorno (STIMATO su ops 0362).
  - Da questa misura dipendono D6-L1 (riusare le idee, −1,04 $ al giorno) e D6-L4 (un modello più economico).
- **I6-misura**: R per numero di posizioni già aperte, e una colonna «senza tetto» nel simulatore. Circa 1,5 ore, dopo il 7 ott. Il tetto in sé non serve.
- **E4-gemelle, pulizia**, dopo il 7 ott (o il 14).
  - Ci sono almeno 8 gruppi di strategie identiche con nomi diversi (ops 0365). Non raddoppiano il rischio.
- **Costi in R e risultato lordo; commissioni vere e scivolamento degli stop.** Prima del denaro vero.
  - I costi del paper sono 29,66 sui −68,65 (diario, 30 set).
- **C4 e C4-misura (chiudere prima degli annunci USA).** Parcheggiate fino al denaro vero.
  - Nel paper toccano 1 trade su 189: il FOMC del 16 set, −4,19 (ops 0371).
- **Correggere la scritta «quarto di size»** nel controllo e nel backlog (30 minuti). Con gli stop tipici la size non è davvero un quarto (punto 4).
- **D7 (il segreto del modello vuoto)**: 5 minuti di pulizia, toglie un avviso falso ogni lunedì.
- **D6-L3 (risposta più corta dell'ombra)**: solo se tieni l'ombra accesa.

### Scelta tua
- **Filtro monete dell'AI: spegnerlo, dargli i dati o lasciarlo** (D6-FILTRO insieme a D7-filtro-monete). Nessun effetto visibile sui trade; costa ~0,45 $ al giorno (STIMATO su ops 0372).
- **Ombra AI: spegnerla o tenerla** (D6-OMBRA). Nessuna parte del sistema la usa. Costa 0,29-0,75 $ al giorno più ~1.200 letture Firebase al giorno (ops 0362; diario, 28 set).

### Non serve
- **F2** (coppie in paper dopo una sola conferma).
  - Il 70-77% delle coppie a 1-2 conferme non ripassa (backlog H1).
  - Il gate sta già allargando da solo: 562 coppie diventano idonee entro il 7 ott (ops 0363). Dettaglio al punto 3.
- **J12, rilanciare lo strumento `ingressi`.** L'obiettivo era avere almeno l'80% dei trade del paper con un ingresso del motore vicino. Oggi è l'81%, 62 su 77 (ops 0371). Si chiude.
- **FR-leva** (togliere prima le coppie che il gate abbandona).
  - Il −0,23R su 45 trade viene quasi tutto dal periodo del difetto della sessione, già corretto.
  - Negli stessi giorni le declassate fanno +0,065R su 27 trade e le attive −0,039R su 45: il dato non le distingue (ops 0291, 0360).
- **H1 con t ≥ 3 sulle finestre.** La t mediana delle validate è 2,23 (ops 0363): ne toglierebbe la maggior parte, e su dati già usati per sceglierle.
- **H2, un holdout diverso per ogni candidata.** Non riduce la fortuna della singola candidata e toglie l'esame sul mercato recente.
- **I9, tenere sempre il keep 0,75 fra le scelte.**
  - I trade con 0,75 sono 5 in tutto, a R −0,14 (ops 0358).
  - Il gate sceglie il keep più alto anche su un prezzo casuale (STIMATO).
- **A3, rischio uguale su ogni trade.** Non cambia nessun R. Alzando il tetto per posizione ci starebbero 1-3 posizioni insieme, contro un massimo misurato di 9 (ops 0360).
- **E4-adx.** Su 92.257 trade l'ADX è la variabile che conta meno: +0,002, l'ultima su 18 (ops 0368). Da togliere dal backlog.
- **B4, l'AI che legge i referti.**
  - La stessa domanda posta a 92.257 trade storici non trova nessuna condizione utile: 0 finestre su 3 (ops 0368).
  - Su 143 referti anche il puro rumore produce un «filo comune» da +0,21R apparenti (STIMATO).
- **B1, formule inventate dall'AI.** Lo stesso vocabolario a 1 ora passa lo 0,94%, a 15 minuti lo 0,20% (ops 0363): il limite sono i costi, non le parole.
- **I2, spegnere il freno nel paper.** Non cambia nessun R né il numero di trade: raddoppia solo il saldo finto.
- **I6, rimettere il tetto di 5 posizioni.**
  - Toglierebbe il 15-18% dei trade in ordine d'arrivo, non i peggiori (STIMATO).
  - Su 71 rifiuti, zero sono per rischio o per margine (ops 0370).
- **D6-L2, idee AI una volta al giorno.** Le altre strade sono migliori: D6-L1 se le idee servono, lo spegnimento se non servono.

### Dove analisti e critici non erano d'accordo: cosa ho deciso
- **Raccolta per il gruppo di controllo.** L'analista diceva «dopo il 7 ott», i due critici «adesso». Scelgo **adesso**: la lettura ha bisogno di 14 giorni di dati salvati prima, e la raccolta costa 2-3 ore.
- **I2-bis.**
  - L'analista proponeva di ritarare la condizione sul massimo toccato, il critico trader di toglierla. Scelgo **toglierla**. Ho rifatto la simulazione su prezzo casuale: dà 0,81R, sotto la soglia di 1,05R come il motore che guadagna. La condizione scatta sia con vantaggio sia senza, quindi non dice niente.
  - Era sbagliata anche la frase «le declassate pesano otto volte meno»: l'ho verificato nel codice.
- **H5-a.**
  - I segnali non presi vanno confrontati con il portafoglio del motore (critico trader). Ho verificato: anche il motore apre solo 995 dei suoi 2.203 segnali (ops 0371).
  - «Il 60% del divario viene dai segnali non presi» va scritto «non si sa», perché il margine è ±0,15R (critico statistico).
- **Filtro monete.** Tre verdetti diversi, quindi lo metto fra le scelte tue.
  - Ho controllato i giri. Il 29 set il filtro falliva sempre ed era di fatto spento: 232 monete, 2h03. Il 30 set era acceso: 229 monete, 2h01 (ops 0343, 0363). L'effetto netto è di poche monete.
- **C4-misura.** L'analista la dava utile, il critico trader da parcheggiare. La **parcheggio**: nel caso migliore sposta circa 0,001R sul trade medio.
- **H1-misura.**
  - La passata una tantum è obbligatoria, non facoltativa.
  - Per una differenza piccola servono 5-7 settimane, non 3. Il conto 42 = 202 − 160 l'ho ricontrollato su ops 0363.
- **D6-IPOTESI.** Cambio il metro: si contano le coppie per origine, non l'R.
- **F2.** La confidenza nel «no» sale da media ad alta.
  - Aggiungo io un motivo: il «quarto dei soldi» su cui F2 contava per limitare il danno, con gli stop tipici, quasi non agisce.

## 3. Le voci in dettaglio

### A. Regole delle letture di ottobre, scritte prima (Serve adesso)

**Cosa vuol dire.** Il 7 ottobre il sistema deve dire dove sta il problema: nel gate, che sceglie male, o nel bot, che esegue male. Oggi, per dire «è il bot», confronta la media di tutti i trade del motore con la media di tutti i trade del paper.

Un esempio inventato, solo per spiegare: su UB il motore apre 5 trade e il paper 3. Gli altri 2 il paper non li ha presi perché aveva già una posizione aperta su UB con un'altra strategia. La media di tutti mescola due cose diverse: come il bot ha eseguito i 3 trade presi insieme, e il fatto che gli altri 2 non poteva prenderli.

La proposta separa le due cose:
- Il verdetto «esecuzione» si decide solo sui trade aperti insieme da paper e motore, e solo quando sono almeno 30.
  - Oggi sono 62: motore +0,05R, paper +0,01R, differenza +0,04R, margine ±0,16R (ops 0371).
- Lo stesso segnale si conta una volta sola: stessa moneta, stessa candela, stessa direzione. Oggi due strategie gemelle fanno due trade identici nel motore e uno solo nel paper.
- Il margine si calcola per giornata, perché nelle giornate nere perdono tutti insieme (19, 23 e 26 set, ops 0371).
- I segnali che il paper non ha preso si confrontano con il portafoglio del motore, che tiene anche lui una posizione per moneta. Il motore ne apre il 45% (995 su 2.203); il paper ha preso 62 segnali su 117, il 53% (ops 0371).
- Il report stampa due righe: «coppie ancora validate» e «tutte le coppie operate». Le coppie uscite si rigiocano fino al giorno in cui sono uscite.
- Per la lettura del 3 ottobre (declassate contro attive):
  - si confronta solo dal 27 set alle 19:40 UTC;
  - si scrive «uguale» solo se il margine esclude ±0,15R, altrimenti «non si decide».

Tutto va scritto nel diario, con la data, prima delle letture.

**Cosa cambia e cosa no.** Cambiano solo il report `portafoglio` e il testo delle regole. Bot, gate, size, uscite e trade restano com'erano. Le soglie restano quelle di oggi: almeno 80 trade del motore e un margine di 2 errori standard.

**Perché serve.**
- MISURATO (conti su ops 0371). Il divario di +0,12R si divide in tre pezzi:
  - +0,04R: lo stesso segnale eseguito peggio;
  - circa +0,07R: i segnali non presi, con margine ±0,15R, quindi non si sa;
  - circa +0,01R: i 15 trade del paper senza un segnale del motore.
- STIMATO (simulazione di un analista):
  - Se il bot eseguisse davvero peggio di 0,10R, il 7 ott la riga «stessi segnali» lo troverebbe nel 43-55% dei casi, la media di tutti nell'11-20%.
  - Se il divario venisse solo dai segnali presi, la regola di oggi direbbe «è il bot» per sbaglio nel 4-9% dei casi il 7 ott e nel 16% il 14 ott.
- Il problema della sopravvivenza (DEDOTTO):
  - Il motore rigioca solo le coppie validate oggi.
  - Le prime rimozioni vere cadono intorno all'8 ott, fra le due letture, e per costruzione escono le peggiori.
  - Se sulle coppie uscite il motore facesse come il paper (45 trade a −0,23R), il suo +0,12R scenderebbe a circa +0,02R (STIMATO). È la stessa grandezza su cui si decide.

**Cosa può andare storto.**
- Si cambia una regola dopo aver visto il primo numero.
  - Oggi la riga accoppiata è piccola: sceglierla abbassa la probabilità di un verdetto «è il bot», dal 19-34% all'8-15% al 7 ott (STIMATO).
  - Per questo la ragione va scritta adesso, e deve essere di struttura (stesso segnale, stesso mercato), non il numero di oggi.
- Con tre letture la probabilità che una suoni per caso sale da ~2,5% a ~7% (STIMATO). Il report deve dirlo.
- Con i numeri di oggi, il 7 ott la risposta più probabile resta «non si decide». La regola non crea un verdetto: evita quello sbagliato.

**Riduce i trade?** No.

**Costo.**
- Circa una giornata di lavoro (stima mia, sommando quelle degli analisti).
- Nessuna lettura Firebase in più, salvo forse le spec delle coppie uscite (da verificare).
- Nessun riavvio: `portafoglio` prende il codice dal repo.
- Il report oggi gira in 324 s, contro il limite di 900 s del canale (ops 0371): da tenere d'occhio.

**Come e quando sapremo.**
- 3 ott: la lettura A4 dice «uguale», «diverso» o «non si decide», con il margine.
- 7 ott: tre verdetti separati (scelta delle coppie, esecuzione sullo stesso segnale, segnali presi), ognuno col suo margine.
- 14 ott: rilettura con le due righe della sopravvivenza.
- Ha funzionato se il verdetto viene dalla riga giusta, non se il numero sale.

**Se non funziona.** Si torna al commit precedente. La riga «motore − paper su tutti» resta comunque stampata come riassunto.

### B. H1-misura: il voto di affidabilità di ogni validata (Serve adesso)

**Cosa vuol dire.** La t è un voto: dice quanto il guadagno medio di una strategia è grande rispetto a quanto oscilla da un trade all'altro.
- Una strategia che vince poco ma sempre ha una t alta.
- Una che ha fatto un solo colpo grosso ha una t bassa.
- Esempio: SAHARAUSDT|gen_95aff747 ha t 1,24, fra le più basse (ops 0363).

La misura:
- salvare la t di tutte le validate, anche quella dell'ultimo esame di 45 giorni;
- nel report, dividere il fuori campione in «t alta» e «t bassa»;
- se le coppie con t bassa perdono dopo la validazione e quelle con t alta guadagnano, chiedere al gate una t minima (H1-soglia-holdout) toglierebbe le fortunate.

**Cosa cambia e cosa no.**
- Il registro salva un campo in più: circa 20 KB, da 423 a ~443 KiB su 879 (STIMATO).
- Il report ha una divisione in più.
- Una passata una tantum calcola subito la t di tutte le 202 validate.
- Non cambiano le coppie validate, i trade né il bot.

**Perché serve.**
- È l'unica strada, sui dati veri, verso la sola leva che può migliorare la scelta delle coppie.
- La simulazione dice che la t all'ultimo esame separa davvero le buone dalle fortunate, a differenza dei «10 trade» del 29 set: il rapporto buone/fortunate sale da 3,0 a 5,4 con t ≥ 1,5 (STIMATO).
- Il prezzo però è alto: le nuove validate scenderebbero a ~25-30% di oggi (STIMATO). Prima di pagarlo bisogna vedere se sui dati veri la t prevede qualcosa.
- La passata una tantum è indispensabile (DEDOTTO). La t si scrive solo quando una coppia ripassa il gate (discover_strategies.py:2616), e le declassate non ripassano. Senza la passata, «t alta» contro «t bassa» sarebbe solo attive contro declassate con un altro nome.

**Cosa può andare storto.**
- La t di oggi non è identica a quella del giorno della validazione. Le finestre scorrono di 7 giorni su anni di dati, quindi è quasi uguale (DEDOTTO).
- La t cresce col numero di trade: «t alta» può voler dire solo «tanti trade». Per questo va stampata anche la t divisa per la radice del numero di trade.

**Riduce i trade?** No.

**Costo.**
- 2-3 ore di codice e test.
- La passata una tantum usa 15-17 minuti di VPS. Supera il limite di 900 s del canale, quindi va lanciata in sfondo come `ingressi-completo`.
- Serve una riga nuova nella lista bianca, che sta solo sulla VPS: **la devi aggiungere tu a mano**.
- Nessuna lettura Firebase in più e nessun riavvio del bot.

**Come e quando sapremo.**
- La regola si scrive prima: R medio del motore fuori campione per t ≥ 2 contro t < 2, col margine.
- Prima occhiata il 7 ott.
- Se la differenza è grande (circa 0,3R), bastano ~100 trade per gruppo: fra il 7 e il 14 ott.
- Se è piccola (circa 0,15R), ne servono ~500 per gruppo, cioè ~1.000 trade del motore: 5-7 settimane, verso metà novembre. Con l'effetto di giornata anche di più (STIMATO).

**Se non funziona.** Se la t non prevede niente, H1-soglia-holdout si chiude con un numero. Il campo in più si può lasciare o togliere.

### C. Gruppo di controllo, da oggi (Serve adesso)

**Cosa vuol dire.** Due raccolte che partono subito:
- A ogni giro si salvano, con la data, circa 50 candidate bocciate con almeno 30 trade, scelte a caso fra le ~24.000 valutate.
- Ogni giorno si fotografano le conferme di ogni coppia.
  - Una coppia che il 1 ott ha 1 conferma resta nel gruppo «1 conferma», anche se poi conferma ancora.
  - Così i trade buoni non si spostano da un gruppo all'altro.

Dopo 14 giorni il motore rigioca tutti questi gruppi sui giorni successivi alla loro data: validate, 2 conferme, 1 conferma, bocciate.

**Cosa cambia e cosa no.** La discovery scrive due piccoli file locali sulla VPS. Non cambiano i verdetti del gate, il bot, il paper né i trade.

**Perché serve.**
- H5 dice se le validate guadagnano dopo essere state scelte, non se guadagnano *perché* sono state scelte.
- Se le bocciate fanno come le validate, il gate non seleziona e il +0,12R è del mercato del mese. In quel caso nessuna modifica al bot migliorerà i trade: la leva è rendere il gate più severo.
- Se le validate battono le bocciate oltre il margine, il gate funziona e il problema è altrove.
- C'è già un indizio (MISURATO, ops 0368, ma su dati usati per scegliere): anche le bocciate guadagnano nella storia, +0,38% a trade contro +0,51% delle passate.
- Risponde anche alla domanda di F2 («servono 3 conferme?») in ~15 giorni invece che in anni.

**Cosa può andare storto.**
- Il motore è più ottimista del paper (+0,12R contro +0,001R): questa misura dice se il gate sceglie bene, non come esegue il bot.
- Se il campione non è davvero casuale, per esempio solo quasi-passaggi, la misura è distorta.
- Due settimane di mercato possono essere particolari.

**Riduce i trade?** No.

**Costo.**
- Adesso: 2-3 ore per la raccolta (STIMA).
- Dopo il 7 ott: circa mezza giornata per l'analisi, più una voce ops in sfondo da aggiungere sulla VPS, con 10-25 minuti di VPS a giro (STIMATO).
- Zero letture Firebase in più, nessun riavvio.

**Come e quando sapremo.**
- La regola si scrive prima: R medio del motore dopo la data, per gruppo, col margine per giornata.
- Prima lettura intorno al 15 ott, dopo H5.

**Se non funziona.** Si cancellano i file e si toglie il codice. Nessun trade è stato toccato.

### D. Filtro monete dell'AI (Scelta tua)

**Cosa vuol dire.**
- Prima di ogni giro a 15 minuti l'AI legge solo i nomi delle 200 monete più scambiate e ne esclude alcune («meme», «quotata da poco»).
- Il 30 set alle 09:13 ha escluso QUSDT per «storia insufficiente». QUSDT però ha 393 giorni di candele e 8 coppie validate (ops 0365, 0371, 0372).
- Le monete che hanno già coppie vengono comunque rimesse dentro (93 il 30 set, ops 0372). Il filtro decide solo dove nascono coppie nuove.

**Le tre strade.**
- **Spegnerlo** (`AI_UNIVERSE_FILTER=false`): −0,45 $ al giorno (STIMATO). Restano le regole fisse: 365 giorni di storia minima e le 200 monete più scambiate.
- **Dargli i dati** (giorni di storia, volume, volatilità): 1-2 ore di lavoro, +0,16 $ al giorno.
- **Lasciarlo com'è.**

**Cosa cambia sui trade.** Niente di misurabile, in nessuna delle tre. Il giro con il filtro di fatto spento (29 set) e quello con il filtro acceso (30 set) differiscono di 3 monete e 2 minuti (ops 0343, 0363).

**Cosa può andare storto.**
- Spegnerlo: fa cercare anche su qualche moneta in più, della stessa qualità media.
- Dargli i dati: con la volatilità davanti, l'AI potrebbe escludere le monete agitate anche se il prompt dice di non farlo.

**Costo.** Una riga nel `.env` della VPS, da cambiare a mano. Non ho verificato se il giro la rilegge senza un riavvio.

**Come sapremo.** La riga SPESA AI di `ai-stato` scende. Il numero di monete del giro resta intorno a 230.

**Tornare indietro.** Si rimette la variabile a `true`.

**Il mio consiglio:** spegnerlo. È un giudizio che non si può ripetere uguale e non passa dal gate, e non serve.

### E. Ombra AI (Scelta tua)

**Cosa vuol dire.** Ogni volta che il bot ha dei segnali, l'AI risponde a «cosa faresti tu al posto del bot?». La risposta si salva e basta: nessuna parte del sistema la legge.

**I numeri.**
- 229 decisioni. Su 179 trade aperti dal bot, 153 veti: l'85% (ops 0362).
- Usata come veto toglierebbe circa 85 trade su 100, contro il tuo «non limitare la quantità».
- Non può mai passare dal gate, perché la risposta di un modello non si ripete uguale.
- Costo: 0,29-0,75 $ al giorno più ~1.200 letture Firebase al giorno, su una quota di letture Firebase che il 28 set si era esaurita.

**Le due strade.**
- **Spegnerla**: `AI_SHADOW_ENABLED=false` nel `.env` e riavvio del bot. È una modifica a mano, e il riavvio è di pochi minuti.
- **Tenerla** come curiosità. Se vuoi prima sapere se i veti avevano ragione, serve 1 ora per correggere `shadow_report`. Con 25 accordi contro 153 veti, però, una differenza sotto ~0,38R non si leggerebbe (STIMATO).

**Cosa cambia sui trade.** Niente, in nessuna delle due strade.

**Tornare indietro.** Si rimette la variabile a `true`.

### F. Le due voci che aspettavano il tuo sì: F2 e J12

**F2: far entrare una coppia nel paper dopo la prima conferma, con un quarto dei soldi.**
- Esempio: una strategia su DOT passa oggi il primo esame e domani il bot la opera, senza aspettare le altre due conferme.
- Perché no:
  1. Il 70-77% delle coppie a 1-2 conferme non ripassa (backlog H1): la maggior parte è fortuna.
  2. Il paper non può dire se funziona. Per vedere 0,10R di differenza servono ~1.140 trade per gruppo, cioè oltre 800 giorni al ritmo dell'esplorativo (STIMATO).
  3. Il bot tiene una posizione per moneta, quindi le candidate prenderebbero il posto delle validate: il 6-17% dei loro segnali andrebbe perso (STIMATO).
  4. Il «quarto dei soldi», con gli stop tipici, quasi non agisce (punto 4): le candidate rischierebbero quasi come le validate.
  5. Il gate sta già allargando da solo. Entro il 7 ott 562 coppie a 2 conferme diventano idonee (ops 0363), e se ne attendono ~130-170 validate nuove (STIMATO).
  6. Cambierebbe il paper nel mezzo della misura del 7-14 ott.
- La domanda che c'è dietro F2 («servono davvero 3 conferme?») la risolve il gruppo di controllo (voce C) in ~15 giorni.
- Se dopo il 14 ott vuoi comunque più esplorazione: allargare l'esplorativo che c'è già (tetto di 3 posizioni) alle coppie a 1-2 conferme. È una preferenza, non un miglioramento.

**J12: il paper entra dove entra il motore?**
- L'obiettivo era almeno l'80% dei trade del paper con un ingresso del motore entro 2 candele.
- Oggi è l'81%, 62 su 77 (ops 0371). Era il 54% il 26-27 set (ops 0304).
- Il rilancio dello strumento `ingressi` non serve più.
- Limite: il conto copre solo le coppie ancora validate, dal 25 set.
- Proposta: chiuderla scrivendo questo numero.

## 4. Cose importanti che mancavano nel backlog

1. **I numeri del paper sono quelli del caso.** L'ha trovato il critico trader; ho rifatto io la sua simulazione e dà gli stessi numeri. Prezzo casuale con le nostre uscite, confrontato col paper (ops 0360, 0366):

   | | Caso | Paper |
   |---|---|---|
   | Stop | 46% | 44% |
   | Stop per ingresso / per uscita | 48,5% / 51,5% | 47% / 52% |
   | Massimo toccato mediano | 0,81R | 0,87R |
   | Arrivati al primo target | 17% | 11% |
   | Vinti | 54% | 56% |
   | R medio | −0,067 | −0,084 (±0,09) |

   - Quindi «39 stop di ingresso contro 43 di uscita» e «88% senza primo target» non sono diagnosi: sono la forma delle regole d'uscita.
   - Su un prezzo senza vantaggio nessuna regola d'uscita crea profitto; si risparmiano solo i costi.
   - Le proposte del mattino basate su queste classi vanno fermate.
2. **Sopravvivenza nel fuori campione.** Le prime coppie tolte cadranno intorno all'8 ott, fra le due letture, e il motore smetterà di vederle. Il suo numero diventerà più ottimista proprio mentre si decide (statistico; DEDOTTO da optimize.py, PURGE_FAILS=2).
3. **La lettura A4 del 3 ott non può dire «uguale».** Con ~62 contro ~82 trade il margine è ±0,29R (STIMATO): «uguale» vorrebbe dire solo «non si vede». La regola va scritta prima.
4. **Il «quarto di size» quasi non agisce.** Il fattore si applica prima del tetto per posizione (risk_manager.py:139-148, main.py:1554-1566).
   - Con uno stop dell'1,3% una declassata rischia lo 0,125%, un'attiva lo 0,130%.
   - Il controllo scrive «size ridotta», ma non è vero.
   - Non tocca niente di ciò che si impara (tutto è in R). Chi un giorno volesse ridurre il danno delle coppie deboli deve sapere che oggi questa manopola non lo fa.
5. **Il gruppo di controllo.** Il backlog H5 lo cita in una frase («non fatto»), ma non esiste come voce.
6. **I2-bis.** La condizione del freno sul massimo toccato non è scritta nella voce I2 e rende l'uscita dal freno impossibile.
7. **L'AI riceve numeri sbagliati.**
   - A ogni giro legge «su 1320 valutazioni ne passano 0», un numero fermo al 21 set (ops 0362, 0365, 0372). Oggi il gate valuta 24.503 candidate e ne passano 48 (ops 0363).
   - Il giro a 15 minuti legge l'autopsia della passata a 1 ora credendola sua (ops 0345, 0372).
8. **Costi e scivolamento.**
   - I costi pesano 29,66 sui −68,65 (diario, 30 set).
   - Motore e paper chiudono lo stop esattamente al suo prezzo, senza scivolamento (executor.py:549-563). Sulle monete poco scambiate un ordine vero esce peggio.
   - Da verificare prima del denaro vero.
9. **Righe in USDT che portano fuori strada.** «Regime neutro −58,30», «long contro short» e i conti per strategia mescolano size piena, mezza e ridotta, e il periodo del difetto. Vanno rifatti in R, con il taglio al 27 set.

## 5. Da dove partire, e le domande

**Il mio consiglio.**
- Prima la **A**: la regola del 3 ott va scritta entro venerdì 2, il resto prima del 7 ott, la parte sulla sopravvivenza entro il 14.
- In parallelo la **C**: ogni giorno di ritardo sposta di un giorno la sua lettura.
- Poi la **B**, facendo nello stesso lavoro la pulizia dei dati per l'AI.
- Uscite, size e freni non si toccano finché il 7-14 ott non dice se il problema è il gate o il bot.

**Le domande.**
1. **A: sì** al pacchetto delle letture? Comprende: riga «stessi segnali» per il verdetto sul bot, minimo di 30 trade accoppiati, conteggio unico dei segnali, margine per giornata, confronto col portafoglio del motore, due righe per le coppie uscite, regola del 3 ott.
2. **B: sì** a salvare la t e a lanciare una volta la passata su tutte le 202 validate? Richiede che tu aggiunga una riga alla lista bianca sulla VPS.
3. **C: sì** ad avviare da oggi la raccolta del gruppo di controllo (fotografia delle conferme e 50 bocciate a giro)?
4. **Filtro monete AI:** spegnerlo, dargli i dati o lasciarlo?
5. **Ombra AI:** spegnerla o tenerla?
6. **Chiudo F2** come «non si fa» e **J12** come «fatta, 81%», scrivendo il perché nel backlog?

**Cosa non ho fatto.**
- Non ho modificato il repo e non ho lanciato i test: il compito era in sola lettura.
- Ho ricontrollato su ops 0343, 0363 e 0371 i numeri principali, e ho letto il codice del rischio e della size.
- Ho rifatto la simulazione del prezzo casuale (`rw_firma.py`).
- Le altre simulazioni degli analisti non le ho rifatte: i loro numeri restano STIMATI.