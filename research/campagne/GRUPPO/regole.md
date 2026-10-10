# Campagna di gruppo — testo completo del Passo 4bis

> **BOZZA del 10 ottobre 2026.** Il proprietario l'ha approvata in anticipo il 2026-10-10 alle 06:35 UTC, prima che
> fosse scritta («devo uscire, il testo è approvato appena hai finito, parti con l'esecuzione»). Finché questo riquadro
> comincia con «**BOZZA», nessuna sessione di gruppo parte. Il coordinamento chiude la bozza con un commit che cambia
> solo questo riquadro e lo sostituisce per intero con il paragrafo che segue, senza le virgolette « » che qui
> sotto lo racchiudono (il riquadro deve cominciare esattamente con `> **In vigore dal `), con al posto di AAAA-MM-GG HH:MM
> l'istante preso con `date -u` subito prima di quel commit (non le 06:35 dell'approvazione anticipata):
>
> «**In vigore dal AAAA-MM-GG HH:MM UTC** (preso con `date -u` subito prima del commit che lo ha scritto; è l'istante
> che il controllo della sezione 9 del protocollo usa per `research/campagna/GRUPPO`). Testo approvato in anticipo dal
> proprietario il 2026-10-10 alle 06:35 UTC, prima che fosse scritto («devo uscire, il testo è approvato appena hai
> finito, parti con l'esecuzione»).»

Questo file completa il Passo 4bis di `research/PROTOCOLLO.md` (versione 4.5). Il Passo 4bis ha già fissato, prima di
qualunque numero: le monete (punto 1), il giudizio sui trade sommati con il blocco calcolato sui trade di tutte le
monete insieme e le baseline calcolate moneta per moneta e combinate con la media pesata per i trade (punto 2), la
sessione dedicata (punto 4), il candidato del gruppo che va al vault con quelli delle monete singole e che si mette
alla prova di trasferimento solo sulle monete fuori dal gruppo (punto 5). Qui si decide il resto (punto 3), con una
sola eccezione al punto 1, spiegata nella sezione 1: il taglio fra costruzione e validazione è lo stesso giorno per
tutte le monete.

## 0. Come si legge

1. **Prevalenza.** Per la campagna di gruppo questo file prevale su `PROTOCOLLO.md` nei punti che tratta. Ciò che non
   tratta vale come nel protocollo, leggendo «la moneta» come «le monete del gruppo, con i trade sommati». La tabella
   finale dice, regola per regola, come si legge il protocollo per il gruppo.
2. **Cosa legge la sessione di gruppo** (dal proprio branch, dopo il checkout: sezione 12, punto 1). `PROTOCOLLO.md` fino alla sezione 12 compresa (le appendici del protocollo
   sono la storia delle versioni e non si leggono), questo file per intero, `research/lezioni/metodo.md`,
   `research/config/parametri.yaml` (la parte comune e la sezione `gruppo`) e le docstring di `research/src/`.
3. **Riferimenti.** In questo file «sezione N» è una sezione di questo file; le sezioni del protocollo si scrivono
   sempre «sezione N del protocollo» o «Passo N».
4. **Una sola lettura per ogni calcolo.** Ogni numero dell'esame di gruppo (stima dei trade, baseline, blocco,
   pavimento, «nettamente», p-value, metriche, verifiche) lo calcola `research/src/gruppo.py` con le funzioni della
   sezione 13, e nessun altro calcolo. La sessione scrive le funzioni che creano la strategia (sezione 13) e gli
   script di lavoro (scarico dei dati, Fase 0, studio dei fallimenti), mai un calcolo d'esame suo.
5. **Parametri.** I parametri propri del gruppo, cioè quelli che il gruppo cambia o aggiunge rispetto al protocollo,
   sono le chiavi della sezione `gruppo` di `research/config/parametri.yaml`, scritta insieme a questo testo e
   congelata con lui. Se un numero di questo file ha una chiave in quella sezione, i due devono coincidere; se non
   coincidono è un errore: STOP e si chiede all'utente. Gli altri numeri di questo file sono valori della parte
   comune dello stesso `parametri.yaml` (liquidità minima, bootstrap, `criterio_vault`, `storia_minima_anni`,
   `timeframe_ammessi`), regole del protocollo, regole di processo scritte solo qui (i 3 tentativi della sezione 2,
   la soglia di 10 trade della sezione 6, i tempi della sezione 12), oppure descrizioni che non decidono niente
   (giorni-moneta, percentuali, stime): questi non si confrontano con la sezione `gruppo`.

## 1. Monete e periodi

1. **Le monete** sono le 80 monete idonee che non sono monete di campagna, elencate in
   `research/campagne/GRUPPO/monete.csv`: una colonna `simbolo`, in ordine dei caratteri (prima le cifre, poi le
   lettere), a capo LF, impronta SHA-256 `0cf217c3c7c4c23934fa1e37dc908618741cd8082514623b281abcbcdf99d8e2`. La
   posizione di una moneta in quel file (da 0 a 79) è il suo numero `j`. L'elenco è congelato con questo testo:
   nessuna moneta si aggiunge e nessuna si sostituisce.
2. **Le schede.** Per ogni moneta, `research/campagne/GRUPPO/schede/<SIMBOLO>.md`, con lo stesso testo delle schede
   del Passo 1: simbolo valido al 2023-12-31, primo mese di dati, fascia di slippage per lato (sul volume medio del
   2023), fine dell'in-sample. Nient'altro: la sessione non cerca altro sulle monete.
3. **Il taglio comune.** La costruzione di ogni moneta va dal primo giorno del suo primo mese di dati al
   **2023-01-16** compreso (fine della costruzione: 2023-01-16 23:59:59.999 UTC, l'argomento `fine_costruzione_ts`
   di `conta_trade`); la validazione di tutte va dal **2023-01-17** al 2023-12-31 (349 giorni). Lo calcola
   `dati.periodi_gruppo` dai primi mesi delle schede, con numeri interi. Un giorno-moneta è un giorno di dati di una
   moneta (80 monete per un giorno fanno 80 giorni-moneta). Il taglio è il primo giorno D in cui la somma, su tutte
   le monete, dei giorni dal primo giorno di dati a D compreso raggiunge (70 × somma dei giorni dal primo giorno di
   dati al 2023-12-31 compreso) // 100. Sui primi mesi delle schede (calcolo del coordinamento del 10 ottobre, da
   ripetere nel test di `periodi_gruppo`): 93.167 giorni-moneta in tutto, obiettivo 65.216, 65.247 di costruzione,
   costruzione da 412 a 1.112 giorni per moneta.
4. **Perché il taglio è comune.** È un'eccezione al punto 1 del Passo 4bis, che diceva «ognuna con la divisione
   70/30». Con la divisione per moneta la costruzione finirebbe fra il 2022-10-18 e il 2023-05-16 a seconda della
   moneta, e 9.666 giorni-moneta di validazione su 27.986 (il 34,5%) cadrebbero in giorni che sono ancora costruzione
   di un'altra moneta del gruppo (calcolo del coordinamento sui primi mesi delle schede). Le crypto si muovono
   insieme: guardare la costruzione di una moneta in quei giorni vorrebbe dire guardare, in parte, la validazione
   delle altre. Con il taglio comune la validazione viene tutta dopo la costruzione, e i giorni-moneta di validazione
   restano quasi gli stessi (27.920 contro 27.986). Prezzo: le monete più giovani costruiscono meno giorni. Era una
   domanda per il proprietario, rimasta senza risposta perché era fuori: l'ha scelto il coordinamento, nel verso
   prudente, dentro l'approvazione anticipata. Si può tornare alla divisione per moneta solo prima del lancio della
   prova a placebo di gruppo (sezione 11); dopo, servono una prova nuova e un testo nuovo.
5. **Le serie di validazione.** Il test di validazione gira, su ogni moneta, sulla serie dall'inizio della
   costruzione al 2023-12-31 (indicatori caldi), e contano solo i trade **entrati** dal 2023-01-17 00:00 UTC in poi.
   La (b) e le strategie sfasate di validazione girano sulla stessa serie, con tutte le barre prima del 2023-01-17
   vietate agli ingressi.
6. **Vault**: per tutte dal 2024-01-01 al 2026-09-30 (sezione 9).

## 2. I dati (Fase 0 del gruppo)

1. Prima di caricare un prezzo, una nota nel log con l'elenco delle monete e, per ognuna, inizio della costruzione,
   fine della costruzione e inizio della validazione, presi da `dati.periodi_gruppo`.
2. **Subito**, per le 80 monete e solo fino al 2023-12-31: candele giornaliere del last (servono al filtro di
   liquidità) e del mark (servono al controllo della storia, punto 9), e funding. Per BTCUSDT, come nelle campagne singole, le candele last su tutti i `timeframe_ammessi`, per il controllo «è solo
   il mercato» e come dato dei segnali (sezione 3, punto 3).
3. **Quando servono**: last, mark e serie dello stop di un timeframe si scaricano per tutte le monete quando si
   registra la prima variante su quel timeframe, prima del suo `conta_trade`; i timeframe adiacenti quando la Fase 4
   li chiede. Si caricano con `carica_serie_allineate` (Fase 0, punto 2, del protocollo). Ogni sessione
   nuova, prima del confronto delle impronte (punto 5), riscarica sempre i file del punto 2; il file
   `campagne/GRUPPO/timeframe_in_uso.txt` (un timeframe per riga) dice quali altri timeframe riscaricare. La sessione
   ci aggiunge un timeframe, e lo committa, quando lo scarica la prima volta, prima del suo `conta_trade`.
4. Gli indirizzi dei file si costruiscono mese per mese, dal primo mese della scheda al 2023-12, solo con
   `research/src/dati.py`. Non si elenca mai l'archivio e non si chiede mai la lista dei contratti di oggi: direbbero
   quali monete sono ancora negoziate. Il caricatore rifiuta la lista dei contratti e l'indice dell'archivio, e il
   guardiano rifiuta i programmi di rete usati direttamente (curl, wget, gh e simili, sezione 12); uno script può
   comunque aprire la rete, e lì vale solo questa regola.
5. **Impronte.** Le impronte SHA-256 dei file scaricati vanno in `campagne/GRUPPO/impronte/<tipo>_<timeframe>.json`
   (`{simbolo: {file: impronta}}`), scritte una volta al primo scarico, prima di ogni test che usa quei file, e mai
   riscritte; in `fase0_dati.md` una riga per ogni file di impronte, con il suo SHA-256. A ogni sessione nuova,
   prima di qualunque test, si confrontano con `verifica_impronte` i file di ogni moneta con le impronte registrate:
   un file registrato che manca o ha un'impronta diversa è sempre STOP (sezione 5 del protocollo), e non fa mai
   uscire la moneta. Una macchina nuova (manca `research/.sessione`, che non è in git, come `data/`) vale come una
   sessione nuova anche a metà sessione, per esempio alla ripresa da uno STOP: dopo i punti 1 e 2 del messaggio di
   apertura e prima di qualunque calcolo si rifanno i punti 3 e 5 di questa sezione (riscarico e confronto delle
   impronte). In campagna `gruppo.py` si ferma con un errore se una moneta non ha candele del timeframe, funding o
   candele giornaliere del last nel periodo.
6. `fase0_dati.md` ha una tabella per moneta: buchi; mesi presenti di last, mark e funding rispetto a quelli
   attesi; barre tolte dall'allineamento, per timeframe; intervallo del funding nel tempo; volume medio per anno;
   mesi sotto la liquidità minima.
7. **Liquidità.** Un mese con volume medio giornaliero in USDT sotto 20 milioni non apre posizioni su segnali di
   barre di quel mese. Il volume si legge dai file `1d` del last con `volume_usdt_da_zip` (media sui giorni presenti
   nel mese); un mese senza candele giornaliere è sotto la soglia; il mese di una barra è quello della sua apertura
   in UTC. Il filtro lo applica solo `gruppo.py`, con una sola funzione di `research/src/` che dà anche i mesi
   scritti in `fase0_dati.md`: è lo stesso per `conta_trade`, per il test e per la (a), e le stesse barre sono
   vietate alla (b) e alle strategie sfasate. Una posizione già aperta esce con la sua uscita. La sessione non
   scrive il filtro: qui questo file prevale sulla Fase 0, punto 3, del protocollo.
8. **Costi e conti per moneta.** Slippage: la fascia della scheda, in costruzione, in validazione e nel vault. I
   costi doppi sono quelli del motore (`moltiplicatore_costi` = 2, come nelle campagne singole: commissione, slippage
   e funding quando è un costo). Funding, dimensione, leva e liquidazione si calcolano moneta per moneta, con il
   capitale iniziale di `parametri.yaml` (1.000 USDT) per ogni moneta.
9. **Buchi, errori e monete che escono.**
   * Ogni file si scarica al massimo 3 volte. Un mese che la fonte non ha (risposta 404) è un buco. Un file che dopo
     3 tentativi non combacia con il CHECKSUM della fonte, o un errore di rete che resiste a 3 tentativi, è STOP: si
     scrive all'utente e si riprende quando lo scarico riesce. Nessuna moneta esce per un errore di rete.
   * I buchi si scrivono in `fase0_dati.md` per moneta, serie e mese, prima di qualunque `conta_trade` che usa quella
     serie, anche per un timeframe scaricato dopo; non si riempiono; non fanno mai uscire una moneta e non rendono mai
     non valutabile una variante: le barre presenti si usano, quelle assenti no. In un mese senza file di funding il
     motore non addebita funding (né al candidato, né alle baseline, né alle sfasate) e alle funzioni della variante
     quei regolamenti non arrivano.
      * **Storia.** Nessuna moneta esce dal gruppo per conto suo. Con `carica_serie_allineate(simbolo, "1d", primo
     giorno della scheda, 2023-12-31)` il primo giorno presente in entrambe le serie dev'essere prima del 2022-01-01
     (`storia_minima_anni`: dati che cominciano prima del 2022-01-01, la regola del Passo 1). Il coordinamento l'ha
     controllato sulle 80 monete prima di congelare il testo (diario del 10 ottobre 2026: 80 su 80): se in Fase 0 una
     moneta non lo supera, è STOP e decide l'utente. Se l'utente la toglie, esce per tutta la campagna, vault
     compreso, nessuna moneta la sostituisce, e `monete.csv`, i numeri j e il taglio del 2023-01-16 non cambiano.
   * Nessun cambio di contratto prima del 2024: uno trovato nei dati è STOP.
   * Un errore di calcolo su una moneta ferma il test: se è un errore del codice della variante, si corregge senza
     cambiare le regole registrate e si rifà il test, dichiarandolo nel log; se è un errore di `src/`, vale il Passo
     3 del protocollo. Una moneta non si toglie mai per una variante.
10. I dati non vanno mai in git.

## 3. Varianti, budget, idee

1. **Budget**: 30 varianti, da usare per intero come nella regola 6 del protocollo, salvo l'avanzo dichiarato nei
   due casi della stessa regola. Al massimo 5 ritocchi per famiglia; al massimo due varianti per fonte
   (`lezioni/metodo.md`); valgono solo fonti pubblicate prima del 2024-01-01, mai gate, registro, paper o altre
   campagne. Le regole da manuale delle prove a placebo (sezione 11 del protocollo) non sono una fonte, e che l'esame
   sbagli più spesso su un meccanismo o un timeframe non è un motivo per sceglierlo. L'ordine dei ritocchi usa il `t` contro la (b) di gruppo (sezione 5).
2. **Una variante è UNA regola per tutte le monete del gruppo**: stesso timeframe, stessa direzione, stessi
   parametri, e UNA voce del log, con `id` `GRUPPO-NNN`. Una variante non contiene elenchi di monete né parametri
   diversi per moneta. Un filtro che esclude certe barre o certe monete usa gli stessi dati dei segnali (punto 3),
   con la stessa formula per tutte, in unità che valgono per ogni prezzo (percentuali, multipli di ATR, quantili
   della moneta stessa); anche un filtro nato dai fallimenti (Fase 3) non nomina monete.
3. **I dati di una variante.** Segnali, filtri e uscite usano solo: le candele già chiuse della moneta stessa; le
   candele di BTCUSDT già chiuse alla chiusura della barra del segnale; il funding della moneta già regolato entro la
   chiusura della barra. Glieli passa `gruppo.py` (sezione 13). **Niente strategie fra monete in questa campagna**:
   niente classifiche fra monete, forza relativa, quote di monete in rialzo o altre grandezze calcolate su altre
   monete del gruppo. Un'idea che le richiede è uno `scarto` con motivo «usa altre monete del gruppo» e non consuma
   budget. Perché: la prova a placebo dell'esame di gruppo (sezione 11) usa solo regole che guardano una moneta,
   quindi non prova l'esame su regole fra monete; e l'elenco è fatto di monete vive e liquide nel 2023, un difetto
   che pesa soprattutto sulle classifiche fra monete (stima del coordinamento, non misurata). È una rinuncia: queste
   idee non avranno un periodo chiuso dopo il vault (sezione 15).
4. **Timeframe**: quelli della sezione 3.4 del protocollo (15m-1d), con i timeframe adiacenti della Fase 4.
5. **Fase 1.** L'ipotesi vale per tutte le monete del gruppo, mai per un sottoinsieme, e spiega perché il meccanismo
   dovrebbe valere su monete diverse per la stessa ragione. Fra le spiegazioni concorrenti, «è solo il mercato» ha
   due forme, da scrivere sempre: le monete seguono BTC o il trend comune; i trade di monete diverse negli stessi
   giorni sono una sola scommessa ripetuta.
6. **Fase 5**, tre domande in più: «Qualche regola, filtro o timeframe favorisce monete che so essere andate bene o
   male dopo il 2023?», «Quanto pesano le monete più presenti nei trade dei candidati?» e «Ho scelto un meccanismo o
   un timeframe perché la sezione 11 del protocollo dice dove l'esame sbaglia più spesso?».

## 4. Stima dei trade, minimi, concentrazione

1. **Minimi**, sui trade sommati di tutte le monete: **700 in costruzione, 300 in validazione, 300 nel vault**. 300 è
   il valore più basso della premessa del Passo 4bis («servono 300-500 trade»); 700 = 300 × 70 / 30, come
   70 = 30 × 70 / 30 nelle campagne singole.
2. **Stima prima del test.** Prima di registrare una variante, `gruppo.conta_trade_di_gruppo` chiama `conta_trade`
   una volta per moneta, sulle regole esatte che si registrano, con gli stessi parametri, funding e serie del test e
   con la fine della costruzione del gruppo. Nella registrazione vanno `trade_stimati` (la somma),
   `trade_stimati_per_moneta`, `monete_con_trade` e `quota_moneta_piu_presente`. Contare regole che non si
   registrano resta vietato (sezione 8 del protocollo).
3. **Tetto di concentrazione.** Se la somma è sotto 700, oppure se una moneta ha più del 10% dei trade stimati, la
   variante è uno `scarto`: non consuma budget, ma un ritocco scartato così conta fra i ritocchi della sua famiglia.
   Per ogni caso di robustezza e per ogni timeframe adiacente della Fase 4 vale lo stesso controllo, ma un caso fuori
   si dichiara e non conta (sezione 6). In validazione e nel vault il tetto non è una condizione: si riportano la
   quota della moneta più presente e la prova sulle monete (sezione 6).
4. **Stima per la registrazione della validazione**: somma, su ogni moneta, di trade di costruzione × 349 / giorni
   di costruzione della moneta, dichiarata come stima. `conta_trade` non si usa mai sul periodo di validazione.

## 5. L'esame di una variante (Fase 2 del gruppo)

Tutto sul periodo che si giudica (costruzione, oppure validazione), con i trade di tutte le monete.

1. **I trade sommati** si mettono in un ordine fisso: per istante d'uscita, poi per simbolo in ordine dei caratteri,
   poi per istante d'entrata (`statistica.ordina_trade_di_gruppo`). L'R medio del candidato è la media semplice degli
   R di tutti i trade (ogni trade rischia l'1%). N è il numero dei trade, n_j quelli della moneta j, w_j = n_j / N.
2. **Il blocco** è quello del Passo 4bis, punto 2: `lunghezza_blocco` su tutte le entrate e le uscite dei trade
   sommati. La finestra è la posizione più lunga fra TUTTE le monete (almeno un giorno): una sola posizione lunga su
   una moneta allunga la finestra per tutte, e molte uscite nello stesso giorno sono poche scommesse vere.
   k = N // blocco; con k < 3 la variante è non valutabile e consuma budget. La soglia è il quantile 0,97725 della t
   di Student con k − 1 gradi, come nella sezione 8 del protocollo.
3. **La baseline (a) di gruppo.** Per ogni moneta j con n_j > 0 si esegue la (a) della sezione 8 del protocollo su
   quella moneta e si calcola `baseline_da_trade` sui suoi trade, con il blocco di `lunghezza_blocco` sui SUOI trade:
   numero A_j, errore e_j, deviazione standard dev_j. D è la deviazione combinata radice(Σ n_i · dev_i² / Σ n_i) sulle
   sole monete con almeno 2 trade della (a). Casi:
   * almeno 3 blocchi interi: A_j, e_j e dev_j come escono;
   * meno di 3 blocchi interi e almeno 2 trade: e_j = il più alto fra dev_j e D (l'errore di un trade solo, che non
     scende sotto la dispersione tipica quando dev_j viene da pochissimi trade);
   * esattamente 1 trade: A_j = l'R di quel trade, e_j = D, e nella deviazione combinata la sua dev_j vale D;
   * 0 trade: la moneta resta fuori dal numero A e dalla combinazione della (a) (i pesi si ricalcolano sulle monete
     che hanno la (a)); l'R medio del candidato resta su tutti i trade; si riportano le monete lasciate fuori e la
     quota dei trade del candidato che portano.
   Numero di gruppo: A = Σ w_j · A_j, con w_j = n_j / Σ n delle monete della combinazione. Errore: Σ w_j · e_j, cioè le
   monete trattate come se si muovessero insieme (non sottostima mai; nella simulazione del coordinamento costava al
   massimo circa il 15% di errore in più, stima). Deviazione standard combinata: radice(Σ n_j · dev_j² / Σ n_j) sulle
   monete della combinazione, così il pavimento della (a) in `contro_baseline` è quello di sempre. Una moneta senza
   trade del candidato pesa zero e non ha (a). La variante è non valutabile contro la (a) se nessuna moneta ha almeno 2
   trade della (a), oppure se le monete lasciate fuori portano più del 10% dei trade del candidato. Lo calcola solo
   `statistica.baseline_da_trade_di_gruppo`. (Prima della chiusura della bozza bastava una moneta con meno di 2 trade
   della (a) per rendere non valutabile la variante: con 80 monete una moneta poco liquida nel 2023 lo faceva
   succedere in 2 delle 6 validazioni della prova di funzionamento del coordinamento.)
4. **La baseline (b) di gruppo.** Per ogni moneta j con n_j > 0 si esegue `simula_baseline_casuale` come nella
   sezione 8 del protocollo: n_j ingressi, durata media = `durata_media_barre` dei trade del candidato sulla moneta j,
   barre vietate della moneta j (riscaldamento, mesi sotto la liquidità, segnale non valido, e in validazione tutte
   le barre prima del 2023-01-17), 200 simulazioni con **semi da 1000·j a 1000·j + 199**. I semi sono diversi per
   moneta: con lo stesso seme gli ingressi casuali di monete diverse cadrebbero quasi sulle stesse barre (un
   grappolo di ingressi senza motivo di mercato). m_j(s) è l'R medio della simulazione s della moneta j (s da 0 a
   199) e b_j la media delle m_j(s) con trade. La simulazione s del gruppo ha R medio
   M(s) = Σ n_j · m_j(s) / Σ n_j, dove le due somme corrono sulle sole monete che hanno trade nella loro
   simulazione s, e i pesi n_j sono i trade del candidato. Numero: B = media delle M(s); errore = deviazione standard
   delle M(s) / radice(numero delle M(s)); pavimento della (b) = deviazione standard delle M(s); percentile del
   candidato fra le M(s), sempre riportato come indizio. Una M(s) senza nessuna moneta con trade non esiste e si
   conta. La variante è non valutabile se su una moneta gli ingressi non entrano, se una moneta con n_j > 0 ha meno
   di 2 simulazioni con trade, o se restano meno di 2 M(s). Lo calcola solo `statistica.baseline_casuale_di_gruppo`.
5. **Il pavimento delle strategie sfasate.** Le entrate casuali della (b) non cadono insieme sulle diverse monete; i
   trade del candidato sì (sono «a grappoli»). Per questo, oltre ai pavimenti delle baseline, c'è il pavimento di una
   strategia senza vantaggio con gli stessi grappoli: le **strategie sfasate**. La strategia sfasata s prende gli
   ingressi del candidato (le barre di segnale) su tutte le monete e li sposta tutti dello stesso intervallo d_s, in
   cerchio sulla finestra del periodo; emette il segnale della variante (stessa direzione, stesso calcolo di stop e
   target) ed esce con la sua uscita (è la stessa strategia casuale della (b), con gli ingressi spostati). In
   dettaglio:
   * la finestra è l'unione delle finestre delle monete con trade del candidato: in costruzione dal primo giorno di
     dati più antico fra quelle monete al 2023-01-16 compreso; in validazione dal 2023-01-17 al 2023-12-31; L è il
     numero di barre del timeframe della variante in quella finestra, contate sul calendario (L = durata della
     finestra / durata della barra), buchi compresi;
   * il margine è il più alto fra 30 giorni e la durata massima dei trade del candidato nel periodo, in barre
     arrotondate per eccesso, ma non oltre L // 4; con S = 200 sfasamenti, d_s = margine + arrotondamento di s × (L − 2 · margine) / (S − 1), con le
     metà verso l'alto, per s da 0 a S − 1; se L − 2 · margine + 1 è meno di S, si usano tutti gli sfasamenti interi
     da margine a L − margine, una volta ciascuno, e si dichiara quanti sono;
   * un ingresso spostato si salta, e si conta, se cade fuori dalla finestra della sua moneta, in una barra che manca
     nella serie della moneta, in una barra vietata o mentre la posizione è aperta (anche quando due ingressi della
     stessa moneta cadono nella stessa barra: succede solo con un segnale prima della finestra, per un buco o per il
     ritardo);
   * per ogni s: M'(s) = R medio dei trade sommati della strategia sfasata, n'(s) = numero dei suoi trade;
   * pavimento delle sfasate = deviazione standard (con ddof 1) dei valori (M'(s) − media delle M') ×
     radice(n'(s) / N), sulle s con almeno un trade; con meno di 2 sfasate con trade la variante è non valutabile. La
     radice corregge per i trade saltati: è esatta con trade indipendenti, con i grappoli è un'approssimazione, che la
     prova a placebo della sezione 11 controlla.
   Lo calcolano solo `motore.simula_sfasamento_comune` e `statistica.pavimento_sfasamento`.
6. **«Nettamente».** `statistica.contro_baseline` con il dizionario della (a) o della (b) di gruppo e con
   `pavimento_minimo` = il pavimento delle sfasate: l'errore del candidato (bootstrap a blocchi sui trade sommati,
   2000 ricampionamenti, seme 0, corretto per il blocco) non scende mai sotto il più alto fra il pavimento della
   baseline e il pavimento delle sfasate. Il resto è la regola della sezione 8 del protocollo, senza cambiamenti.
7. **Candidato.** In costruzione una variante diventa candidato se batte nettamente la (a) e la (b) di gruppo e il
   suo R medio dopo i costi, sui trade sommati, è positivo. Una variante non valutabile non è un vantaggio. La
   **vicinanza** (ordine dei ritocchi) è il `t` contro la (b) di gruppo.
8. **(c)**: buy and hold per anno, long e short, di ogni moneta con trade, combinato con gli stessi pesi w_j (in un anno in cui una moneta non ha candele il suo
   termine manca, e si riporta la somma dei pesi delle monete presenti): solo contesto, come nella sezione 8 del protocollo.
9. **Si riportano sempre** (solo come informazione, mai come prova): blocco, k, massimo di uscite in un giorno UTC,
   durata massima di una posizione, monete con trade, quota della moneta più presente, ed effetto grappolo =
   errore del candidato² × N / varianza degli R, con l'errore del bootstrap già corretto per il blocco e preso PRIMA
   di qualunque pavimento, e la varianza con ddof 1 (dice quante volte i trade sommati valgono meno di trade
   indipendenti).
10. **Controllo positivo degli strumenti** (`lezioni/metodo.md`). Prima della prima variante la sessione chiama
   `gruppo.controllo_positivo` con il timeframe, la direzione e il modulo di `campagne/GRUPPO/codice/` con l'uscita
   che userà. `gruppo.py` calcola da sé, su ogni moneta del periodo di costruzione, ingressi che guardano avanti (una
   barra è un segnale se la chiusura della barra dopo è sopra, per il long, o sotto, per lo short, la chiusura della
   barra del segnale), con le stesse barre vietate delle varianti, e li passa alla strategia casuale da un insieme di
   ingressi, lo stesso percorso della (b) e delle sfasate. Li giudica con l'esame di gruppo, senza ritardo e con il
   ritardo di una barra. Passa se senza ritardo batte nettamente la (a) e la (b) di gruppo e se con il ritardo il `t`
   contro la (b) ricalcolata scende sotto la metà di quello senza ritardo. Si registra come `nota`, prima e dopo, senza
   `verifica_di` e senza consumare budget. Se non passa è un errore degli strumenti: STOP, come per un errore di
   `src/`, e nessuna variante si registra. È l'unico calcolo in cui una strategia del gruppo usa barre non chiuse, e
   quelle barre le legge solo `gruppo.py`.

## 6. Fase 3 e Fase 4 del gruppo

1. **Fase 3** come nel protocollo, sui trade sommati (`esame_di_gruppo` li salva in `campagne/GRUPPO/`, sezione 8).
   Un filtro nato dai fallimenti è un ritocco e vale per tutte le monete (sezione 3, punto 2).
2. **Fase 4**, tutte le verifiche sui trade sommati di costruzione, ognuna registrata prima. «La (b) ricalcolata»
   vuol dire la (b) di gruppo e il pavimento delle sfasate ricalcolati nelle stesse condizioni.
   1. *Robustezza*: ogni parametro numerico ±20% con gli arrotondamenti della Fase 4 del protocollo. Ogni caso si
      conta prima con `conta_trade_di_gruppo`: un caso sotto 700 o oltre il tetto del 10% si dichiara e non conta;
      un caso non valutabile conta come fallito. Nei casi che contano il `t` contro la (b) ricalcolata resta
      positivo, e in almeno metà di essi il candidato la batte nettamente. Se contano meno della metà dei casi
      previsti, la verifica non è superata.
   2. *Timeframe adiacenti* (sezione 3.4 del protocollo): il `t` contro la (b) ricalcolata resta positivo su ognuno
      che ha 700 trade e rispetta il tetto; gli altri si dichiarano e non contano; uno non valutabile conta come
      fallito.
   3. *Direzione*: come nel protocollo.
      4. *Stabilità*: in più della metà degli anni di costruzione (anno d'uscita) con almeno 100 trade sommati, l'R
      medio dei trade usciti nell'anno supera la B ripesata sui trade di quell'anno (come nel punto 5).
   5. *Estremi*, tre prove, tutte da superare. **Prova sui trade**: senza i 30 trade migliori l'R medio supera
      ancora B. **Prova sui giorni**: senza tutti i trade usciti nei 3 giorni UTC con la somma di R più alta, l'R
      medio supera la B ripesata sui trade rimasti. **Prova sulle monete**: senza le 3 monete con la somma di R più
      alta, l'R medio supera la B ripesata sulle monete rimaste. La B ripesata è Σ r_j · b_j / Σ r_j, con r_j i trade
      rimasti della moneta j e b_j quello della sezione 5, punto 4: si usano le b_j già calcolate, senza simulazioni
      nuove. Se non resta nessun trade, la prova non è superata. Le soglie 100 e 30 sono quelle delle campagne singole
      (10 e 3) moltiplicate per 10, come 700 = 70 × 10. Lo calcola `statistica.estremi_di_gruppo`, con le chiavi
      `senza_trade_migliori`, `senza_giorni_migliori` e `senza_monete_migliori`.
      6. *Regola intra-barra opposta e dettagli del feed*: si dichiara la differenza; per il gruppo i dettagli del feed
      sono le barre tolte dall'allineamento di last e mark (sezione 2, punto 6).
   7. *Ritardo di una barra*: il `t` contro la (b) ricalcolata col ritardo resta positivo e almeno la metà di quello
      senza ritardo; sotto, prima si cerca l'errore, come nel protocollo.
   8. *Liquidazione*: nessuna violazione su nessuna moneta.
   9. *Costi doppi* (sezione 2, punto 8): il candidato batte ancora nettamente la (b) ricalcolata a costi doppi e
      l'R medio a costi doppi resta positivo.
   Solo da riportare: la quota delle monete con almeno 10 trade il cui R medio supera la propria b_j; l'effetto
   grappolo.
3. Le verifiche non cambiano le regole del candidato e non servono a sceglierne un'altra, come nel protocollo.

## 7. Validazione e asticella

1. Dopo la Fase 5, di ogni famiglia va in validazione un solo candidato, quello con il `t` più alto contro la (b) di
   gruppo in costruzione; da lì le sue regole sono congelate. Tutti i candidati si validano insieme, una volta sola.
2. **Il via libera, prima della validazione.**
   1. *La sessione.* Scrive nel log la voce `nota` con `pausa_da`, committa tutto con un ultimo commit intitolato
      «pausa per il via libera alla validazione», pusha, e controlla con `git status` che non resti nulla da
      committare e che il branch sia allineato con `origin/research/campagna/GRUPPO`. Poi si ferma (STOP) scrivendo
      all'utente: «pronta per la validazione: serve il via libera (regole.md, sezione 7, punto 2)». Da lì, fino alla
      frase del coordinamento o alla risposta dell'utente, non fa né commit né push.
   2. *Il coordinamento.* Solo se la prova a placebo di gruppo (sezione 11) ha detto che l'esame regge con le cinque
      impronte della sezione 11, punto 1, e solo quando la punta del branch della campagna è il commit «pausa per il
      via libera alla validazione» oppure un commit del coordinamento fatto sopra di lui (una correzione della
      sezione 11, punto 6, o un via libera da riscrivere): (1) `git fetch origin research/campagna/GRUPPO` e
      `git log -1 --format=%s origin/research/campagna/GRUPPO`, e annota la punta con `git rev-parse`; se il titolo è
      «pausa per il via libera alla validazione», annota nel diario quell'hash come hash della pausa; se è un altro,
      va avanti solo se `git log --format=%H <hash della pausa>..<punta>` stampa soltanto hash di commit del
      coordinamento annotati nel diario, altrimenti aspetta il giro successivo; (2) per i soli cinque file, `git cat-file blob <punta>:<percorso> |
      sha256sum`, confrontato con le impronte della prova: se una è diversa, niente via libera e si rifà la prova
      (sezione 11, punto 2); (3) un solo commit sopra la punta, che tocca solo
      `research/campagne/GRUPPO/via_libera_validazione.md`, fatto senza estrarre il branch (con l'API di GitHub su quel
      branch, oppure con `git hash-object`, un indice temporaneo, `git read-tree <punta>`, `git update-index`,
      `git write-tree`, `git commit-tree -p <punta>` e un push senza forzare), intitolato «campagna di gruppo: via
      libera alla validazione»; (4) se il push è rifiutato, si ricomincia da (1); se riesce, annota nel diario l'hash del commit. Su quel branch, fino al Passo 7, il
      coordinamento non usa mai checkout, worktree, diff, `git show` di un commit, `log -p`, `--stat`,
      `--name-only`, `ls-tree`. Il file contiene la riga «esito: l'esame di gruppo regge (regole.md, sezione 11)» e
      cinque righe nel formato di `sha256sum` (`<impronta>  <percorso dalla radice del repository>`) per
      `research/src/gruppo.py`, `research/src/statistica.py`, `research/src/motore.py`, `research/src/dati.py` e
      `research/config/parametri.yaml`. Poi manda nella sessione, nel modo della sezione 12, punto 1, la frase «via
      libera nel branch: rifai il controllo di regole.md, sezione 7, punto 2».
   3. *La ripresa.* Lo STOP lo scioglie quella frase o una risposta dell'utente. La sessione controlla prima che
      `git branch --show-current` stampi `research/campagna/GRUPPO` e che `research/.sessione` esista (se no, rifà i
      punti 1 e 2 del messaggio di apertura); poi fa `git pull --ff-only origin research/campagna/GRUPPO` e controlla
      che il file esista, che nomini tutti e cinque i file e che le impronte siano quelle dei file sul disco
      (`sha256sum`). Se va bene scrive nel log `pausa_a` e valida; se no, torna allo STOP.
   4. *Il controllo dentro lo strumento.* Con il marcatore `{"tipo": "campagna", "simbolo": "GRUPPO"}`,
      `gruppo.esame_di_gruppo` sul periodo di validazione fa lo stesso controllo e rifiuta di partire se non torna,
      qualunque sia la cartella di uscita. Senza un marcatore di campagna (la prova a placebo della sezione 11, che il
      coordinamento fa senza marcatore, e i test) il controllo non c'è: il via libera è il frutto della prova e non
      può esserne la condizione.
3. Ogni candidato gira una volta su ogni moneta (sezione 1, punto 5). La (b) di validazione vieta tutte le barre
   prima del 2023-01-17; il pavimento delle sfasate si calcola sulla finestra di validazione.
4. Va al vault solo se: (i) ha almeno 300 trade sommati; (ii) supera l'asticella; (iii) l'R medio dopo i costi dei
   trade sommati è positivo.
5. **Asticella**: `benjamini_hochberg` al 10% sui p-value del campo `p_value` di `contro_baseline`, con i trade
   sommati di validazione, la (b) di gruppo di validazione e il pavimento delle sfasate di validazione. m (il numero
   di candidati dell'asticella) conta tutti i candidati di gruppo che hanno girato in validazione: chi ha meno di 300
   trade o è non valutabile (contro la (a), contro la (b) o per il pavimento delle sfasate) entra con p-value 1, e chi cade per l'R medio resta nel conteggio. Il gruppo è una
   campagna a sé: la sua m non si unisce a quelle delle monete singole.
6. Si riportano, senza che decidano: quota della moneta più presente, prova sulle monete, effetto grappolo. L'esito
   è provvisorio: lo conferma il coordinamento, che controlla anche il segno dell'R medio sommato.

## 8. Log, risultati, consegna, misure di processo

1. **Log** `campagne/GRUPPO/log.jsonl`, con i campi della sezione 6 del protocollo e `id` `GRUPPO-NNN`; una variante
   è una sola voce per tutte le monete. I campi del risultato sono il dizionario di `gruppo.esame_di_gruppo` (in
   forma JSON), copiato così com'è: metriche sui trade sommati (profit factor, trade, R medio, R medio per anno
   d'uscita, R medio senza i 30 migliori, drawdown), `per_moneta` (trade e R medio), blocco, numero di blocchi,
   massimo di uscite in un giorno, durata massima, effetto grappolo, `baseline_a` e `baseline_b` con i campi della
   sezione 6 del protocollo più pesi, numero di monete, semi e pavimento delle sfasate, `percentile_caso` fra le
   M(s), `buy_and_hold_per_anno` pesato. `esame_di_gruppo` salva anche i trade sommati di ogni test in
   `campagne/GRUPPO/trade/<id>_<periodo>.jsonl`, e il suo file di avanzamento in `campagne/GRUPPO/avanzamento/`:
   si committano, così una sessione nuova riprende da lì.
2. **Consegna** `campagne/GRUPPO/consegna.md`, come nel Passo 3, più: metriche sommate per periodo e tabella per
   moneta; tutte le verifiche della Fase 4, compresi gli estremi per trade, giorni e monete; monete con trade e
   quota della più presente; massimo di posizioni aperte insieme, per direzione; trade al mese attesi in paper
   calcolati su tutte le monete dell'elenco; previsione per vault e trasferimento (solo fuori dal gruppo). Misure di
   processo come nel protocollo, più i minuti di calcolo per variante. Esito vuoto: «nessuna strategia valida
   trovata per il gruppo». I file `lezioni_moneta.md` e `lezioni_metodo_proposte.md` tengono questi nomi. Nessun
   candidato si dichiara «validato».
3. I titoli dei commit dicono cosa si è fatto, mai i risultati; in Fase 0 dicono solo quante monete sono scaricate.

## 9. Il vault del candidato di gruppo (lo fa il coordinamento al Passo 5)

1. Il candidato di gruppo gira UNA volta sul vault, su tutte le monete del gruppo, ognuna con la fascia della sua
   scheda, il capitale iniziale di 1.000 USDT e le regole del bot. Vale il filtro di liquidità della sezione 2, punto
   7, con la stessa funzione, sui file giornalieri del last del vault; le stesse barre sono vietate alle sfasate e alla
   (b) del vault.
2. **Passa se valgono tutte insieme** (il `criterio_vault` sui trade sommati):
   1. profit factor dopo i costi almeno 1,10: somma dei guadagni in USDT dei trade in utile diviso la somma delle
      perdite in USDT dei trade in perdita, su tutti i trade di tutte le monete;
   2. almeno 300 trade sommati;
   3. risultato totale positivo: la somma dei guadagni e delle perdite in USDT di tutti i trade di tutte le monete;
   4. R medio dei trade sommati sopra il 90° percentile degli R medi sommati delle S **sfasate del vault** (S = 1.000;
      a 1d meno, come nella sezione 5, punto 5, e si dichiarano).
3. **Le sfasate del vault** prendono il posto delle «strategie fittizie con entrate casuali» della sezione 8 del
   protocollo: stessa direzione, stessa uscita, gli stessi ingressi del candidato nel vault spostati tutti dello
   stesso intervallo (quelli saltati si contano), come le strategie sfasate della sezione 5, punto 5, con S = 1.000
   e L le barre del vault. Così conservano anche i grappoli fra monete. Con entrate casuali indipendenti fra monete
   la quarta condizione passerebbe per caso molto più spesso del 10% dichiarato, perché i trade del candidato cadono
   insieme sulle monete e le entrate casuali no (stima dalla simulazione approssimata della sezione 15, sui periodi
   di costruzione e di validazione e non sul vault: circa il 26% invece del 10%).
4. **Tasso del caso**: la quota delle S sfasate del vault che passano le stesse quattro condizioni, con lo
   stesso 90° percentile. La condizione dei 300 trade si giudica sul candidato e vale per tutte le sue sfasate: i loro
   ingressi saltati vengono dallo spostamento, non dalla strategia. Profit factor, risultato totale e R medio sopra il
   90° percentile si giudicano su ogni sfasata (`criterio_vault` con `trade_minimi` = 0 sulle metriche di
   `motore.metriche_di_gruppo_da_somme`: per ogni s e per ogni moneta numero dei trade, somma degli R, somma dei
   guadagni e somma delle perdite in USDT). Il 90° percentile si calcola sulle sfasate con almeno un trade; quelle senza trade
   restano nel denominatore e non passano. Si riportano la distribuzione di n'(s) / N e il numero di sfasate senza
   trade.
5. Si riportano, senza che decidano: il confronto con la (b) di gruppo del vault (semi 1000·j + s, blocco sui trade
   sommati, pavimento delle sfasate); la quota della moneta più presente; la prova sulle monete (sezione 6, punto
   2.5); la tabella per moneta; a parte, le monete
   che smettono di avere candele nel vault.

## 10. Monete che muoiono nel vault, trasferimento, paper, giudizio d'insieme

1. **Chi ha diritto a quali monete.**
   1. Le monete del gruppo sono quelle di `monete.csv`, e restano quelle.
   2. Una moneta che smette di avere candele durante il vault resta nella somma fino al suo ultimo giorno con candele
      nei dati del vault. Le posizioni aperte si chiudono come nella sezione 7 del protocollo. Dopo quel giorno non
      apre più posizioni: né il candidato, né la (b), né le sfasate. Minimi e conteggi si giudicano sulla somma.
   3. Una migrazione o ridenominazione si ricuce e continua la moneta del gruppo solo se è nell'elenco che il
      coordinamento scrive sul branch di coordinamento prima di aprire la sessione, con il metodo dei collegamenti
      del Passo 1 (il vecchio simbolo finisce e il nuovo comincia nello stesso mese). Una fusione in un contratto che
      esisteva già non si ricuce: per il gruppo la moneta è morta. Quell'elenco non va mai sul branch principale.
   4. Il contratto che continua o assorbe una moneta del gruppo non entra nel trasferimento del candidato di gruppo;
      per i candidati delle monete singole entra come ogni moneta di verifica.
   5. Le monete del gruppo restano possibili monete di verifica dei candidati delle monete singole (Passo 6), con la
      regola di `universo/monete_verifica_regola.md` e la fascia del volume del vault.
   6. Il candidato di gruppo si giudica su tutte le sue monete; in paper va solo su quelle negoziate all'avvio del
      paper, e lo dichiara il coordinamento al Passo 5.
2. **Trasferimento del candidato di gruppo** (Passo 6): lo si mette alla prova solo sulle monete fuori dal gruppo
   (monete di campagna e monete di verifica che non sono nel gruppo e non continuano né assorbono una moneta del
   gruppo). Un candidato di gruppo fa pochi trade per moneta, probabilmente meno dei 30 del vault su molte monete
   (stima): moneta per moneta l'esito sarebbe spesso «non si sa». Il coordinamento propone di rendere decisiva la
   prova sui trade sommati di tutte quelle monete, con le quattro condizioni della sezione 9 (sfasate su quelle
   monete) e il controllo «era solo il mercato»: battere nettamente (`contro_baseline` con il pavimento delle
   sfasate) la (b) di gruppo del vault su quelle monete, con j la posizione della moneta nell'elenco in ordine dei
   caratteri delle monete fuori dal gruppo e semi 1000·j + s; fascia di slippage della scheda per le monete di
   campagna e del volume del vault per quelle di verifica. **Decide il proprietario prima di «APRI IL VAULT»**, e la
   scelta si scrive in `vault/APERTURA.md`. Senza una sua scelta vale il Passo 6 com'è, moneta per moneta, con i 30
   trade del vault su ogni moneta e la probabilità per moneta dei candidati singoli. In tutte e due le vie il candidato
   di gruppo gira sulle monete fuori dal gruppo solo con `gruppo.esame_vault`, che passa alle sue funzioni le candele
   di quella moneta, quelle di BTCUSDT e il funding di quella moneta, con il filtro di liquidità della sezione 9, punto
   1, attraverso un caricatore del coordinamento passato con `caricatore=` (stesse regole del punto 4), la cui scheda
   dà la fascia di slippage di questo punto. Non cambia nulla per la sessione di gruppo.
3. **Paper** (Passo 9, solo se il proprietario lo chiede): costruzione, validazione e vault si giudicano sui trade
   sommati, senza limiti di portafoglio. Prerequisito in più: il bot sa eseguire la strategia su tutte le monete
   negoziate del gruppo. Il bot oggi tiene poche posizioni insieme (`config/regole_dimensione.md`): prima del paper il
   coordinamento rigioca i trade del candidato con i limiti del bot, sulle monete negoziate, e il paper si confronta
   con quel rigioco. Conferma o bocciatura dopo 50 trade e almeno 3 blocchi interi (`lunghezza_blocco` sui trade del
   paper). La consegna riporta il massimo di posizioni aperte insieme, per direzione.
4. **Passo 5**: prerequisiti in più, accanto a quelli del Passo 5 (che restano, compreso l'esito della prova a
   placebo delle monete singole): la consegna del gruppo e l'esito della prova a placebo di gruppo. Al punto 2 del
   Passo 5 si scaricano anche i dati del vault delle monete del gruppo, comprese le candele giornaliere del last (filtro di
   liquidità, sezione 9, punto 1), fino all'ultimo giorno con candele, ricucendo
   solo le migrazioni del punto 1.3. La cucitura non sta nei file su disco: la fa il caricatore del coordinamento che si
   passa a `gruppo.esame_vault` con `caricatore=` (gli stessi metodi di `gruppo.CaricatoreDisco`): per una moneta
   dell'elenco carica il vecchio simbolo fino al suo ultimo giorno con candele e il nuovo da lì al 2026-09-30, unisce
   last e mark con `motore.ricuci_serie`, prende il funding di ciascun simbolo nel suo tratto e i mesi sotto la
   liquidità di ciascuno (il mese della cucitura è vietato se è sotto la soglia per almeno uno dei due). Codice ed
   elenco stanno solo sul branch di coordinamento, si committano prima di «APRI IL VAULT» e la loro impronta va in
   `vault/APERTURA.md`. `vault/APERTURA.md` contiene anche il candidato di gruppo con le impronte dei
   suoi file, le impronte di `monete.csv`, delle schede e di questo file, il rimando all'elenco del punto 1.3 e la
   scelta del proprietario sul trasferimento (punto 2). Prima del giro il coordinamento controlla che ogni moneta del gruppo abbia i file del vault (candele del timeframe,
   funding e candele giornaliere del last) fino al suo ultimo giorno con candele: senza marcatore `gruppo.py` non si
   ferma da solo. `vault/risultati.md` riporta il totale sommato, la tabella per
   moneta e, a parte, le monete che smettono di avere candele.
5. **Passo 7**: nel giudizio d'insieme il candidato di gruppo conta come un candidato, con il suo tasso del caso; non
   è un'«idea di gruppo». Al punto 3 si unisce anche `research/campagna/GRUPPO`, e le sue lezioni entrano come
   quelle di una moneta.

## 11. La prova a placebo dell'esame di gruppo

1. L'esame di gruppo (sezioni 4-7) è un calcolo nuovo: prima della validazione serve la prova che non promuova
   strategie senza vantaggio più spesso di quanto dichiara la sezione 11 del protocollo, anche con i trade a grappoli
   fra monete. La fa il coordinamento sul branch di coordinamento (`research/taratura/placebo_gruppo/`), senza
   marcatore di campagna, con regole scritte, committate e pushate prima del lancio: le regole d'ingresso da manuale
   della prova del 9 ottobre, spostate dello stesso intervallo di tempo su tutte le monete insieme (così restano senza
   vantaggio ma tengono i grappoli), giudicate con l'esame di gruppo. Gli ingressi spostati si passano a `gruppo.py`
   con l'argomento `ingressi_placebo` (sezione 13). Usa gli strumenti della sezione 13 del branch principale da cui si
   apre la sessione; le sue regole riportano le impronte SHA-256 di `research/src/gruppo.py`, `statistica.py`,
   `motore.py`, `dati.py` e di `research/config/parametri.yaml` (le cinque impronte).
2. **Quando e cosa succede dopo.** La prova parte prima della sessione e corre insieme a lei; la sessione non ne vede
   i numeri. Il via libera della sezione 7, punto 2, porta solo l'esito e le cinque impronte, e vale solo per quei
   file: se durante la campagna uno di essi cambia (una correzione della sessione o del coordinamento), il
   coordinamento rifà la prova intera con i file nuovi, le stesse regole e gli stessi sfasamenti, e solo dopo scrive
   o riscrive il via libera, nel modo della sezione 7, punto 2. Se la prova non regge, il coordinamento ferma la
   sessione e porta i numeri al proprietario con una correzione dell'esame scritta guardando solo i numeri della
   prova, mai le domande della sessione; l'esame corretto si riprova con sfasamenti nuovi, scritti prima, in un file
   separato. Se il proprietario cambia l'esame prima della validazione, `research/campagna/GRUPPO` si archivia come al
   Passo 2 e la campagna riparte da zero su un branch nuovo, con il budget intero e una sessione nuova che non legge
   l'archivio, salvo una scelta diversa del proprietario, scritta nel diario. Se un file cambia dopo che la
   validazione ha girato e la prova rifatta non regge, la campagna non riparte: il candidato di gruppo non va al vault
   e decide il proprietario. Se il proprietario non cambia l'esame, la sessione fermata riprende con una seconda
   sessione (sezione 12, punto 1).
3. **L'esame regge se valgono tutte queste condizioni**, sulle stime puntuali. n sono, per ciascun periodo, le
   placebo valutabili che superano gli stessi controlli della campagna: in costruzione almeno 700 trade e nessuna
   moneta oltre il 10% dei trade di `conta_trade_di_gruppo`; in validazione almeno 300 trade. Servono almeno 80
   placebo così per periodo: se sono meno si aggiungono sfasamenti decisi sul solo conteggio. Ogni placebo ha
   z = Φ⁻¹(1 − p_value) del confronto con la (b), con il p_value di `contro_baseline`: con un esame giusto z è normale
   standard; «netta» vuol dire z > 2,00 e «p sotto 0,10» vuol dire z > 1,2816.
   * in costruzione, le placebo nette sono al massimo ⌊0,03 · n⌋;
   * in validazione, le placebo con p sotto 0,10 sono al massimo ⌊0,13 · n⌋;
   * con μ e σ (ddof 1) degli z di ciascun periodo, 1 − Φ((2,00 − μ) / σ) è al massimo 3% in costruzione e
     1 − Φ((1,2816 − μ) / σ) è al massimo 13% in validazione (con 80-100 placebo le quote contate le sposta una
     placebo sola; questa condizione usa tutte le placebo e tiene insieme centro e larghezza).
   Le soglie 3% e 13% sono quelle della prova del 9 ottobre (`taratura/placebo/regole.md`, punto 5): il 2% e l'11%
   dichiarati dalla sezione 11 del protocollo, più un margine. Il resto (dati, combinazioni, controlli di copertura,
   intervalli, misure riportate senza che decidano) sta nelle regole della prova.
4. La prova di gruppo misura solo l'esame di gruppo sui trade sommati. Per i candidati delle monete singole, e per il
   candidato di gruppo giudicato moneta per moneta al Passo 6, «l'ultima prova a placebo» del Passo 5 e del Passo 6,
   punto 4, resta l'ultima prova dell'esame delle monete singole (`taratura/placebo/`): la prova di gruppo non entra
   nella probabilità per moneta del trasferimento.
5. **Cosa non arriva alla sessione.** Dal lancio della prova alla consegna del gruppo, numeri ed esiti parziali della
   prova di gruppo stanno solo in `taratura/placebo_gruppo/` sul branch di coordinamento: mai sul branch principale né
   su quello della campagna (né in `PROTOCOLLO.md`, `CLAUDE.md`, `CHANGELOG.md`, `lezioni/metodo.md`, `config/`,
   `src/` compresi docstring, commenti e test, `campagne/GRUPPO/`, `docs/`) né in un messaggio di commit. Una
   correzione dell'esame si spiega con la regola che cambia, mai con il numero che l'ha mostrata. Il diario dice solo
   «prova di gruppo in corso», «finita: regge» o «finita: non regge»; i numeri entrano dopo la consegna del gruppo.
6. **Il branch principale non si unisce nel branch della campagna fino al Passo 7.** Una correzione a `src/` nata fuori
   dalla sessione ci arriva con un commit che tocca solo `src/` e `CHANGELOG.md` (la riga dice cosa cambia nel codice
   e «tutte quelle che usano <funzione>», mai chi l'ha trovata né come), fatto come il via libera (sezione 7, punto 2:
   senza estrarre il branch, un solo commit sopra la punta, push senza forzare), e solo quando la sessione è ferma a
   uno STOP con tutto committato e pushato, oppure fra due sessioni; mai mentre lavora. A una sessione ferma il
   coordinamento manda la frase «correzione nel branch: fai git pull --ff-only origin research/campagna/GRUPPO,
   rilancia i test di research/src/tests/ e torna allo STOP in cui eri». Allo stesso modo arriva una correzione di
   `PROTOCOLLO.md`, di questo file o di `config/` approvata dal proprietario durante la campagna: un commit che tocca
   solo quel file, e la frase «correzione di <file> nel branch: fai git pull --ff-only origin
   research/campagna/GRUPPO, rileggi <file> e torna allo STOP in cui eri», con il solo nome del file. Se la correzione
   tocca uno dei cinque file del punto 1, vale il punto 2. Un cambio dell'esame segue il punto 2.

## 12. La sessione di gruppo

1. **Chi la apre**: il coordinamento, su delega del proprietario, con la sorgente del repository, il branch
   principale e il messaggio `research/apertura/gruppo.md` del branch di coordinamento, approvato con questo testo e
   mandato così com'è (una seconda sessione riceve lo stesso testo più «riprendi dalla nota del log»). La sessione
   legge il protocollo e questo file solo dopo il checkout del suo branch: valgono le versioni del branch. La campagna
   di gruppo conta fra le tre campagne in corso. Valgono i controlli del Passo 4: modello e impostazioni dopo
   l'apertura, primo push entro 35 minuti, sessione ferma dopo 25 minuti senza aggiornamenti, giro orario sui soli
   titoli dei commit, domande girate subito al proprietario. Una sessione ferma allo STOP del via libera (sezione 7,
   punto 2) non si giudica ferma.
   **Le frasi.** Oltre al messaggio di apertura, il coordinamento manda in una sessione aperta solo le frasi della
   sezione 7, punto 2, e della sezione 11, punto 6, così come sono scritte. Le manda con un Routine da una sola
   esecuzione nella sessione (`create_trigger` con `persistent_session_id` uguale all'id della sessione, `run_once_at`
   un minuto dopo, la frase come `prompt`), oppure con lo strumento dei messaggi fra sessioni se vede la sessione.
   Insieme si programma un promemoria a 15 minuti: se la frase non è stata consegnata o la sessione non ha lavorato
   dopo, lo scrive subito al proprietario, che può scrivere lui la frase o rispondere nella sessione; la frase non si
   rimanda a ripetizione. Prima di mandare una frase la prima volta, il coordinamento prova il canale su una sessione
   di prova senza marcatore (poi archiviata) e scrive l'esito nel diario. Una sessione archiviata non si riattiva: si
   apre una seconda sessione.
2. **Branch** `research/campagna/GRUPPO`, aperto nell'ordine della sezione 9 del protocollo; il controllo della data
   del primo commit del log usa l'istante scritto dopo «In vigore dal» nell'intestazione di questo file. Marcatore
   `research/.sessione` con `{"tipo": "campagna", "simbolo": "GRUPPO"}`.
3. **Percorsi ammessi.**
   * Lettura: `PROTOCOLLO.md`, `CHANGELOG.md`, `config/`, `src/`, `lezioni/metodo.md`, `campagne/GRUPPO/`,
     `data/insample/<S>/` per ogni S di `monete.csv`, `data/insample/BTCUSDT/` (mai `campagne/BTCUSDT/`).
   * Scrittura: `campagne/GRUPPO/` tranne `monete.csv`, `schede/`, `regole.md` e `via_libera_validazione.md`, che
     sono in sola lettura; `data/insample/` delle monete dell'elenco e di BTCUSDT; `src/` e `CHANGELOG.md` solo per
     correggere errori, come nel Passo 3. `config/` è in sola lettura.
   * Tutto il resto è vietato, in particolare le altre cartelle di `campagne/`, i dati delle monete di campagna
     diverse da BTCUSDT, `data/insample/GRUPPO/`, `data/placebo/`, `data/vault/`, `universo/`, `taratura/`,
     `apertura/`, `vault/`, `trasferimento/`, `confronto/`, `prova_processo/`, `passo4/` e i `percorsi_vietati`.
4. **Il guardiano** riconosce `GRUPPO` e ammette i dati delle monete di `monete.csv` solo se il file ha l'impronta
   scritta nel guardiano (la sessione non può allargarsi i permessi riscrivendo l'elenco); rifiuta in ogni campagna i
   programmi di rete usati direttamente (curl, wget, gh, pip e simili) e gli interpreti con `-m` diversi da
   `-m pytest`, e tiene `config/` in sola lettura. Il caricatore rifiuta, in campagna, la lista dei contratti di oggi e
   l'indice dell'archivio, e con `GRUPPO` i simboli fuori dall'elenco e da BTCUSDT.
5. **Operazioni su molte monete** solo con script che leggono `monete.csv`, mai con elenchi di file o glob della
   shell sulla cartella dei dati.
6. **Calcoli lunghi.** Prima di ogni calcolo che dura più di 20 minuti la sessione pusha un commit intitolato
   «calcolo in corso fino alle HH:MM UTC circa»: il coordinamento non la giudica ferma fino a quell'ora più metà
   della durata annunciata. Ogni calcolo si lancia in background con il tempo massimo dello strumento (7.200.000 ms),
   in pezzi sotto le 2 ore, e riprende da dove era rimasto (sezione 8, punto 1). L'uscita di uno script va sempre in
   due file della cartella della campagna: `python3 -u research/campagne/GRUPPO/codice/<nome>.py >
   research/campagne/GRUPPO/lavoro/<nome>.out 2> research/campagne/GRUPPO/lavoro/<nome>.err` (mai `2>&1`); quando arriva
   la notifica di fine si leggono quei due file. Il file d'uscita che lo strumento indica per un comando in background,
   o dove salva un'uscita troppo lunga, sta fuori dai percorsi ammessi e non si apre; non si usa Monitor. I test di
   `research/src/tests/` si lanciano in primo piano con il tempo di 600.000 ms (durano alcuni minuti). Uno script che chiama `gruppo.py` con più processi tiene la chiamata sotto `if __name__ == "__main__":`. Se un
   calcolo supera 3 volte la stima della sezione 14, la sessione scrive una nota nel log e lo dice all'utente; l'esito di una variante non cambia per
   la velocità.
7. **Storia, commit e push.** In una macchina di sessione la storia è limitata, e il guardiano ammette la storia dei
   commit solo con formati di date e hash: `git log --format='%h %cI' -- research/campagne/GRUPPO/` (anche con
   `--stat` o `--name-only`). Il file del messaggio per `git commit -F` va in `research/data/insample/BTCUSDT/` (fuori
   da git): `data/insample/GRUPPO/` non esiste. Se un push viene rifiutato, la sessione non forza, non unisce e non
   riscrive la storia: scrive nel log una voce `nota`, lo dice all'utente e aspetta (STOP).

## 13. Gli strumenti (da scrivere dal coordinamento prima della sessione, con i loro test)

* `dati.periodi_gruppo`: taglio e date per moneta (sezione 1); una funzione che legge la fascia di slippage dalla
  scheda; la funzione del filtro di liquidità (sezione 2, punto 7).
* `dati`: in campagna il caricatore rifiuta la lista dei contratti di oggi e l'indice dell'archivio; con `GRUPPO`
  rifiuta i simboli fuori dall'elenco e da BTCUSDT.
* `motore.simula_baseline_casuale`: una chiave in più, `r_medio_per_seme`, l'R medio di ogni seme (vuoto per le
  simulazioni senza trade), senza cambiare nulla per le campagne singole.
* `motore.simula_sfasamento_comune`: le strategie sfasate della sezione 5 e le sfasate del vault della sezione 9.
* `motore.metriche_di_gruppo`: le metriche dei trade sommati con le chiavi del `criterio_vault`; `motore.somme_dei_trade`
  e `motore.metriche_di_gruppo_da_somme`: le stesse metriche dalle somme per moneta, per le sfasate del vault.
* `statistica.ordina_trade_di_gruppo`, `statistica.baseline_da_trade_di_gruppo`,
  `statistica.baseline_casuale_di_gruppo`, `statistica.pavimento_sfasamento`, `statistica.effetto_grappolo`,
  `statistica.estremi_di_gruppo`, e `statistica.contro_baseline(..., pavimento_minimo=0.0)` (con 0 è identica a
  prima).
* `research/src/gruppo.py`, l'esecutore unico: `conta_trade_di_gruppo`, `esame_di_gruppo` (test, (a), (b), pavimento,
  confronti, `t`, p-value, percentile, R per anno, stabilità, estremi, tabella per moneta con b_j, posizioni aperte
  insieme, violazioni di liquidazione e trade ridotti per il tetto di leva, controllo del via libera in validazione),
  `controllo_positivo` (sezione 5, punto 10) ed `esame_vault` (per il coordinamento, nel vault e nel trasferimento,
  con il filtro di liquidità sui file del vault). `conta_trade_di_gruppo` ed `esame_di_gruppo` permettono il ritardo di
  una barra, la regola intra-barra opposta e i costi doppi, uguali su tutte le monete e applicati anche alla (a), alla
  (b) e alle sfasate ricalcolate. Una moneta per processo, più processi insieme, un file di avanzamento in sola
  aggiunta con l'impronta del codice e la ripresa automatica, combinazioni solo alla fine.
* **Il marcatore.** `gruppo.py` legge il marcatore come `dati.py`, nel suo posto della radice del progetto e mai nella
  cartella di lavoro o di uscita. Con un marcatore di campagna (qualunque simbolo) fa il controllo del via libera in
  validazione e rifiuta l'argomento `ingressi_placebo`; senza marcatore di campagna (coordinamento, prova a placebo,
  test) accetta `ingressi_placebo` (gli ingressi già calcolati per moneta, al posto della funzione che crea la
  strategia della variante) e non fa il controllo del via libera.
* **Il contratto fra `gruppo.py` e le funzioni della sessione** (firme, cosa ricevono, come si importano in ogni
  processo) sta nella docstring di `gruppo.py`, si scrive e si prova prima della prova a placebo, e vale per lei e per
  la sessione con la sola differenza di `ingressi_placebo`. `gruppo.py` costruisce i `Parametri` di ogni moneta da
  `parametri.yaml` e dalla fascia della scheda; carica last, mark e funding con `carica_serie_allineate`; applica il
  filtro di liquidità; passa alle funzioni della variante le candele della moneta, le candele di BTCUSDT già chiuse e
  il funding già regolato (sezione 3, punto 3), mai il simbolo né dati di altre monete. Tutte le funzioni della
  sessione, anche al momento della creazione della strategia, ricevono solo viste delle barre già chiuse e del funding
  già regolato, mai la serie intera. Le funzioni della sessione, al livello del modulo in `campagne/GRUPPO/codice/`,
  creano la strategia della variante, la sua (a), la strategia casuale da un insieme di ingressi e il calcolo del
  segnale senza la condizione d'ingresso; non leggono file.
* Test obbligatori, fra gli altri: con una moneta sola, quella con j = 0 (così i semi della (b) sono da 0 a 199,
  quelli delle campagne singole), e pavimento 0, ogni funzione di gruppo dà gli stessi numeri del percorso delle
  campagne singole, salvo quando la (a) ha almeno 2 trade e meno di 3 blocchi interi (lì il gruppo prende l'errore
  della sezione 5, punto 3, e il confronto è valutabile: test a parte con il numero calcolato a mano); l'esito non
  cambia con l'ordine delle monete né con il numero di processi; due monete calcolate a mano; lo sfasamento è lo
  stesso su tutte le monete; gli ingressi saltati si tolgono e si contano; il filtro toglie gli stessi segnali in
  `conta_trade`, nel test e nella (a), e le stesse barre sono vietate alla (b) e alle sfasate, anche in `esame_vault`;
  una funzione della sessione (anche al momento della creazione) che legge una candela non chiusa o un funding non
  ancora regolato non vede nulla; su una serie sintetica `controllo_positivo` passa senza ritardo e crolla con il
  ritardo; una regola scritta come funzione della variante e la stessa data come `ingressi_placebo` danno gli stessi
  numeri; con il marcatore GRUPPO `ingressi_placebo` si rifiuta e la validazione senza via libera (o con un'impronta
  diversa, o con meno di cinque impronte) si rifiuta anche con una cartella di uscita fuori da `campagne/GRUPPO/`;
  senza marcatore la validazione parte; `periodi_gruppo` dà 2023-01-16 e 349 sulle schede vere; il caricatore con
  `GRUPPO` rifiuta ETHUSDT e accetta AAVEUSDT e BTCUSDT.

## 14. Tempi (stime, servono solo ad annunciare i calcoli lunghi)

Una variante in costruzione, con (b) e pavimento delle sfasate: pochi minuti a 1d e 4h, 5-11 minuti a 1h, 20-45 a
15m; validazione 7-15 minuti a 1h; Fase 4 per candidato 2-3,5 ore a 1h, 4-8 a 15m; Fase 0 a ogni sessione nuova
circa 30 minuti più circa 20 per ogni timeframe in uso. Campagna intera: 2-4 giorni di sessioni. Vault del candidato di gruppo (lo fa il coordinamento): circa 40 minuti a 1h e
circa 3 ore a 15m (stima), in pezzi con il file di avanzamento. (Stime del
coordinamento dal ritmo misurato della prova del 9 ottobre e da prove di velocità del motore; con indicatori pesanti
ricalcolati a ogni barra i tempi possono raddoppiare.)

## 15. Limiti (da riportare nei report finali, oltre a quelli della sezione 11 del protocollo)

* **Potenza bassa (stime da una simulazione approssimata).** Le monete si muovono insieme, e i trade a grappoli
  valgono molto meno di trade indipendenti. In una simulazione approssimata del coordinamento (candele a 1 ora delle
  80 monete fino al 2023, regole da manuale con un vantaggio aggiunto a ogni trade, R senza funding né tetto di leva,
  una (b) semplificata: non gli strumenti della sezione 13) l'incertezza della media dei trade sommati era quella che
  avrebbe avuto circa un decimo dei trade, se fossero stati indipendenti. Nella stessa simulazione, in validazione, un
  vantaggio di 0,10 R per trade sopra la (b) batteva nettamente la (b) circa una volta su tre con 3.000 trade sommati
  o più, e circa 4 volte su 100 con meno trade; un vantaggio di 0,05 R circa una volta su 100; uno di 0,20 R circa una
  volta su sei fra 300 e 999 trade. Battere la (b) non basta: serve anche l'R medio dopo i costi positivo (sezione 7,
  punto 4). «Nettamente» non è l'asticella: con un solo candidato basta un p-value fino a 0,10 e passare è più
  frequente; con cinque candidati o più la soglia di uno solo è circa «nettamente». La premessa del Passo 4bis
  («servono 300-500 trade») vale solo per trade indipendenti: la campagna di gruppo può finire senza candidati anche
  se un vantaggio piccolo c'è.
* **Sopravvivenza.** Le monete del gruppo sono quelle liquide nel 2023 e quotate prima del 2022: chi è morto prima
  non c'è.
* **Strategie fra monete escluse** (sezione 3, punto 3): dopo il vault non avranno un periodo chiuso.
* **Funding nei segnali.** La prova a placebo di gruppo usa solo regole sulle candele: non prova l'esame su regole
  basate sul funding, le cui entrate possono cadere a grappoli più stretti fra le monete (stima del coordinamento, non
  misurata). Per un candidato che usa il funding, l'effetto grappolo riportato dice quanto ci si allontana dai casi
  della prova.
* **Filtro di liquidità.** Il filtro legge il volume di tutto il mese della barra: in un mese in cui una moneta crolla
  o smette di avere candele, il candidato può non entrare anche nei giorni prima. È uno sguardo avanti di al massimo
  un mese, lo stesso della Fase 0 del protocollo, e vale uguale in costruzione, validazione e vault. In costruzione il
  verdetto di gennaio 2023 usa anche il volume dei giorni dal 17 al 31, che sono di validazione.
* **Il bot e molte monete.** Non è verificato che il bot sappia eseguire una strategia su decine di monete, e i suoi
  limiti di portafoglio la cambierebbero (sezione 10, punto 3).
* **Il guardiano** giudica le azioni, non gli script (sezione 11 del protocollo); il divieto di leggere le appendici
  del protocollo è un'istruzione, non un blocco. L'intestazione del protocollo, che la sessione legge, dice che il
  candidato di BTCUSDT c'è; la sezione 11 del protocollo riporta la prova a placebo fatta su queste stesse 80 monete
  (solo strategie senza vantaggio) e nomina la regola da manuale che l'esame promuove più spesso per caso.
* **Copertura dei dati.** Fuori dalla sessione il coordinamento ha scaricato le candele giornaliere di last e mark
  (controllo della storia: 80 su 80) e, per la prova a placebo, le candele a 1 ora e a 4 ore di last e mark e il funding. I loro
  conteggi non arrivano alla sessione, che misura da sé la copertura in Fase 0, per ogni timeframe che scarica.
* **La prova a placebo di gruppo** usa lo stesso spostamento comune del pavimento: dove il pavimento decide, la prova
  regge in parte per costruzione; per questo riporta anche le misure senza pavimento.
* **Le sfasate hanno meno trade** del candidato (ingressi saltati): profit factor e 90° percentile su meno trade sono
  più larghi; il tasso del caso viene un po' più alto e la quarta condizione del vault un po' più severa (verso
  prudente).

## Tabella finale — come si legge il protocollo per il gruppo

| Dove nel protocollo | Per il gruppo |
|---|---|
| §2 Il guardiano | Riconosce GRUPPO e le monete di `monete.csv` con l'impronta; programmi di rete e `-m` diversi da pytest rifiutati; `config/` in sola lettura (sezione 12, punto 4) |
| §3.1 `in_sample` | Dall'inizio dei dati di ogni moneta al 2023-12-31 |
| §3.4 `divisione_costruzione_validazione` (70/30 per moneta) | Taglio comune: costruzione fino al 2023-01-16, validazione dal 2023-01-17 (sezione 1) |
| §3.4 `trade_minimi`, `budget_varianti_per_moneta` | 700 / 300 / 300 sui trade sommati; 30 varianti per il gruppo (sezioni 3-4) |
| §3.4 `simulazioni_baseline_casuale`, semi | 200 per moneta, semi 1000·j + s (sezione 5, punto 4) |
| §3.4 bootstrap, `minimo_blocchi_bootstrap`, `livello_nettamente` | Uguali, sui trade sommati, con il blocco su tutte le monete e il pavimento delle sfasate (sezione 5, punti 2 e 6) |
| §3.4 `criterio_vault`, `simulazioni_caso` | Sui trade sommati, con le sfasate del vault (sezione 9) |
| §4 regola 1 (vault chiuso) | Uguale, per tutte le 80 monete |
| §4 regola 6 (variante, ritocco, famiglia) | Una variante è una regola per tutte le monete (sezione 3) |
| §4 regola 7 (indipendenza) | La sessione non legge le campagne delle monete singole né il coordinamento (sezione 12) |
| §5 cartelle | `campagne/GRUPPO/` con `monete.csv`, `schede/`, `regole.md`, `log.jsonl`, `fase0_dati.md`, `impronte/`, `timeframe_in_uso.txt`, `trade/`, `avanzamento/`, `lavoro/` (uscite degli script), `ipotesi.md`, `codice/`, `candidati/`, `consegna.md`, lezioni; `via_libera_validazione.md` solo sul branch della campagna |
| §5 e Passo 4, punto 1 (il coordinamento unisce il principale nei branch aperti) | Mai in `research/campagna/GRUPPO` fino al Passo 7: le correzioni arrivano con un commit solo, a sessione ferma (sezione 11, punto 6) |
| §6 log, `trade_stimati` di validazione | `id` `GRUPPO-NNN`, una voce per variante (sezione 8); stima di validazione × 349 / giorni di costruzione per moneta (sezione 4, punto 4) |
| §6 controllo positivo degli strumenti (`lezioni/metodo.md`) | Solo con `gruppo.controllo_positivo` (sezione 5, punto 10) |
| §7 «Serie» (candele last per i segnali) | Candele chiuse della moneta, candele chiuse di BTCUSDT e funding regolato entro la chiusura della barra, passati da `gruppo.py` (sezione 3, punto 3) |
| §7 parametri, slippage, costi doppi | Per moneta, dalla scheda; capitale 1.000 USDT per moneta; `moltiplicatore_costi` (sezione 2, punto 8) |
| §7 cambi di contratto, delisting | Prima del 2024 un cambio di contratto è STOP (sezione 2, punto 9); nel vault sezione 10, punto 1 |
| §8 stima dei trade | `conta_trade_di_gruppo`, con il tetto del 10% (sezione 4) |
| §8 baseline, «nettamente», vicinanza | Sezione 5 |
| §8 asticella | Sezione 7, con m del solo gruppo |
| §8 tasso del caso | Sezione 9 |
| §9 apertura della sessione | Sezione 12 e il messaggio di apertura del gruppo |
| Passo 3, percorsi ammessi | Sezione 12, punto 3 |
| Passo 3, Fase 0 (compresi la storia minima e il filtro di liquidità) | Sezione 2: la storia corta è STOP e decide l'utente (controllo del coordinamento: 80 su 80); il filtro lo applica `gruppo.py` |
| Passo 3, Fasi 1, 3, 5 | Sezione 3 (Fase 1 e Fase 5) e sezione 6 (Fase 3) |
| Passo 3, Fase 2 | Sezione 5 |
| Passo 3, Fase 4 | Sezione 6 |
| Passo 3, Validazione | Sezione 7 (con il via libera) |
| Passo 3, Consegna | Sezione 8 |
| Passo 4, controlli | Sezione 12, punto 1 |
| Passo 5 | Sezioni 9 e 10, punto 4 |
| Passo 6 | Sezione 10, punto 2, e sezione 11, punto 4 |
| Passo 7 | Sezione 10, punto 5 |
| Passo 9 | Sezione 10, punto 3 |
| §11 limiti | Sezione 15, in più |
