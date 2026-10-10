# Campagna di gruppo — testo completo del Passo 4bis

> **BOZZA del 10 ottobre 2026.** Il proprietario l'ha approvata in anticipo il 2026-10-10 alle 06:35 UTC («devo
> uscire, il testo è approvato appena hai finito, parti con l'esecuzione»). Vale dall'istante del commit che toglie
> la parola BOZZA da questa riga, scritto qui al suo posto: è l'istante che il controllo della sezione 9 usa per il
> branch `research/campagna/GRUPPO`. Finché questa riga dice BOZZA, nessuna sessione di gruppo parte.

Questo file completa il Passo 4bis di `research/PROTOCOLLO.md` (versione 4.5). Il Passo 4bis ha già fissato, prima di
qualunque numero: le monete (punto 1), il giudizio sui trade sommati con il blocco calcolato sui trade di tutte le
monete insieme e le baseline calcolate moneta per moneta e combinate con la media pesata per i trade (punto 2), la
sessione dedicata (punto 4), e il candidato del gruppo che va al vault con quelli delle monete singole e si
trasferisce solo sulle monete fuori dal gruppo (punto 5). Qui si decide il resto (punto 3), con una sola eccezione
al punto 1, spiegata nella sezione 1: il taglio fra costruzione e validazione è lo stesso giorno per tutte le monete.

## 0. Come si legge

1. **Prevalenza.** Per la campagna di gruppo questo file prevale su `PROTOCOLLO.md` nei punti che tratta. Ciò che non
   tratta vale come nel protocollo, leggendo «la moneta» come «le monete del gruppo, con i trade sommati». La tabella
   dell'appendice A dice, regola per regola, come si legge il protocollo per il gruppo.
2. **Cosa legge la sessione di gruppo.** `PROTOCOLLO.md` fino alla sezione 12 compresa (le appendici sono la storia
   delle versioni e non si leggono), questo file per intero, `research/lezioni/metodo.md`, la sezione `gruppo` di
   `research/config/parametri.yaml` e le docstring di `research/src/`.
3. **Una sola lettura per ogni calcolo.** Ogni numero dell'esame di gruppo (stima dei trade, baseline, blocco,
   pavimento, «nettamente», p-value, metriche, verifiche) lo calcola `research/src/gruppo.py` con le funzioni
   della sezione 13, e nessun altro calcolo. La sessione scrive solo le funzioni che creano la strategia.
4. **Parametri.** I numeri di questo file stanno nella sezione `gruppo` di `research/config/parametri.yaml`, scritta
   insieme a questo testo e congelata con lui. Se un numero qui e uno là non coincidono, è un errore: STOP e si
   chiede all'utente.

## 1. Monete e periodi

1. **Le monete** sono le 80 monete idonee che non sono monete di campagna, elencate in
   `research/campagne/GRUPPO/monete.csv`: una colonna `simbolo`, in ordine alfabetico. La posizione di una moneta in
   quel file (da 0 a 79) è il suo numero `j`. L'elenco è congelato con questo testo: nessuna moneta si aggiunge e
   nessuna si sostituisce. Una moneta esce dal gruppo solo nei casi della sezione 2, punto 9.
2. **Le schede.** Per ogni moneta, `research/campagne/GRUPPO/schede/<SIMBOLO>.md`, con lo stesso testo delle schede
   del Passo 1: simbolo valido al 2023-12-31, primo mese di dati, fascia di slippage per lato (sul volume medio del
   2023), fine dell'in-sample. Nient'altro: la sessione non cerca altro sulle monete.
3. **Il taglio comune.** La costruzione di ogni moneta va dal primo giorno del suo primo mese di dati al
   **2023-01-16** compreso (fine della costruzione: 2023-01-16 23:59:59.999 UTC, l'argomento `fine_costruzione_ts`
   di `conta_trade`); la validazione di tutte va dal **2023-01-17** al 2023-12-31 (349 giorni). Lo calcola
   `dati.periodi_gruppo` dai primi mesi delle schede, con numeri interi: il taglio è il primo giorno D in cui la
   somma, su tutte le monete, dei giorni dal primo giorno di dati a D compreso raggiunge (70 × somma dei giorni dal
   primo giorno di dati al 2023-12-31 compreso) // 100. Sui primi mesi delle schede: 93.167 giorni-moneta in tutto,
   65.247 di costruzione, costruzione da 412 a 1.112 giorni per moneta.
4. **Perché il taglio è comune** (eccezione al punto 1 del Passo 4bis, che diceva «ognuna con la divisione 70/30»).
   Con la divisione per moneta la costruzione finirebbe fra l'ottobre 2022 e il maggio 2023 a seconda della moneta,
   e il 34,5% dei giorni di validazione cadrebbe in giorni che sono ancora costruzione di un'altra moneta del
   gruppo (calcolo del coordinamento sui primi mesi delle schede). Le crypto si muovono insieme: guardare la
   costruzione di una moneta in quei giorni vorrebbe dire guardare, in parte, la validazione delle altre. Con il
   taglio comune la validazione viene tutta dopo la costruzione, e la proporzione sul totale resta quasi la stessa
   (27.920 giorni-moneta di validazione contro 27.986). Prezzo: le monete più giovani costruiscono meno giorni.
5. **Validazione con gli indicatori caldi.** Il test di validazione gira, su ogni moneta, sulla serie dall'inizio
   della costruzione al 2023-12-31, e contano solo i trade **entrati** dal 2023-01-17 00:00 UTC in poi.
6. **Vault**: per tutte dal 2024-01-01 al 2026-09-30 (sezione 9).

## 2. I dati (Fase 0 del gruppo)

1. Prima di caricare un prezzo, una nota nel log con l'elenco delle monete e, per ognuna, inizio della costruzione,
   fine della costruzione e inizio della validazione, presi da `dati.periodi_gruppo`.
2. **Subito**, per le 80 monete e solo fino al 2023-12-31: candele giornaliere del last (servono al filtro di
   liquidità) e funding. Per BTCUSDT, come nelle campagne singole, le candele last su tutti i `timeframe_ammessi`,
   solo come riferimento di mercato.
3. **Quando servono**: last, mark e serie dello stop di un timeframe si scaricano per tutte le monete quando si
   registra la prima variante su quel timeframe, prima del suo `conta_trade`; i timeframe adiacenti quando la Fase 4
   li chiede. Si caricano con `carica_serie_allineate` (Fase 0, punto 2, del protocollo): le barre tolte si scrivono
   in `fase0_dati.md`, per moneta e timeframe. Il file `campagne/GRUPPO/timeframe_in_uso.txt` (un timeframe per
   riga) dice alla sessione successiva cosa riscaricare.
4. Gli indirizzi dei file si costruiscono mese per mese, dal primo mese della scheda al 2023-12. Non si elenca mai
   l'archivio e non si chiede mai la lista dei contratti di oggi: direbbero quali monete sono ancora negoziate (il
   caricatore lo rifiuta, sezione 12).
5. **Impronte.** Le impronte SHA-256 dei file scaricati vanno in `campagne/GRUPPO/impronte/<tipo>_<timeframe>.json`
   (`{simbolo: {file: impronta}}`), scritte una volta al primo scarico, prima di ogni test che usa quei file, e mai
   riscritte; in `fase0_dati.md` una riga per ogni file di impronte, con il suo SHA-256. A ogni sessione nuova,
   prima di qualunque test, si verificano le impronte di ogni moneta: un'impronta diversa è STOP (sezione 5 del
   protocollo).
6. `fase0_dati.md` ha una tabella per moneta: buchi; mesi presenti di last, mark e funding rispetto a quelli
   attesi; barre tolte per timeframe; intervallo del funding nel tempo; volume medio per anno; mesi sotto la
   liquidità minima.
7. **Liquidità.** Un mese con volume medio giornaliero in USDT (colonna `quote_volume` delle candele giornaliere,
   letta con `volume_usdt_da_zip`) sotto 20 milioni non apre posizioni su segnali di barre di quel mese: un solo
   filtro, uguale per `conta_trade`, per il test e per la (a); le stesse barre sono vietate alla (b) e alle
   strategie sfasate (sezione 5). Una posizione già aperta esce con la sua uscita.
8. **Costi e conti per moneta.** Slippage: la fascia della scheda, in costruzione, in validazione e nel vault. A
   costi doppi si raddoppiano commissione e slippage di ogni moneta. Funding, dimensione, leva e liquidazione si
   calcolano moneta per moneta, con il capitale iniziale di `parametri.yaml` (1.000 USDT) per ogni moneta.
9. **Monete che escono.** Nessuna cucitura prima del 2024: un cambio di contratto trovato nei dati prima del 2024 è
   STOP. Una moneta esce dal gruppo solo in Fase 0, prima del primo `conta_trade`, e solo per due motivi: file
   mancanti o impronte diverse dopo 3 tentativi; oppure una storia utile, dopo l'allineamento di last e mark, sotto
   `storia_minima_anni` (2 anni prima del 2024-01-01, Fase 0 punto 4 del protocollo). Si scrive nel log e all'utente; nessuna moneta la sostituisce, ed esce per
   tutta la campagna, vault compreso. I buchi si dichiarano e non si riempiono. Dopo il primo `conta_trade`
   l'elenco è chiuso: un errore su una moneta durante un test che resiste a 3 tentativi rende non valutabile quella
   variante, che consuma budget; una moneta non si toglie mai per una variante.
10. I dati non vanno mai in git.

## 3. Varianti, budget, idee

1. **Budget**: 30 varianti, da usare per intero come nella regola 6, salvo l'avanzo dichiarato nei due casi della
   stessa regola. Al massimo 5 ritocchi per famiglia; al massimo due varianti per fonte (`lezioni/metodo.md`);
   valgono solo fonti pubblicate prima del 2024-01-01, mai gate, registro, paper o altre campagne. L'ordine dei
   ritocchi usa il `t` contro la (b) di gruppo (sezione 5).
2. **Una variante è UNA regola per tutte le monete del gruppo**: stesso timeframe, stessa direzione, stessi
   parametri, e UNA voce del log, con `id` `GRUPPO-NNN`. Una variante non contiene elenchi di monete né parametri
   diversi per moneta. Un filtro che esclude certe barre o certe monete si calcola solo dai dati della moneta stessa
   (e di BTCUSDT) già chiusi alla barra del segnale, con la stessa formula per tutte, in unità che valgono per ogni
   prezzo (percentuali, multipli di ATR, quantili della moneta stessa); anche un filtro nato dai fallimenti
   (Fase 3) non nomina monete.
3. **Niente strategie fra monete in questa campagna.** Segnali, filtri e uscite usano solo le candele già chiuse
   della moneta stessa e di BTCUSDT, come nelle campagne singole. Niente classifiche fra monete, forza relativa,
   quote di monete in rialzo o altre grandezze calcolate su altre monete del gruppo. Un'idea che le richiede è uno
   `scarto` con motivo «usa altre monete del gruppo» e non consuma budget. Perché: l'esame di gruppo è tarato
   (sezione 11) solo su regole che guardano una moneta, e l'elenco è fatto di monete vive e liquide nel 2023,
   un difetto che pesa soprattutto sulle classifiche fra monete. È una rinuncia: queste idee non avranno un periodo
   chiuso dopo il vault (sezione 15).
4. **Timeframe**: quelli della sezione 3.4 (15m-1d), con i timeframe adiacenti della Fase 4.
5. **Fase 1.** L'ipotesi vale per tutte le monete del gruppo, mai per un sottoinsieme, e spiega perché il meccanismo
   dovrebbe valere su monete diverse per la stessa ragione. Fra le spiegazioni concorrenti, «è solo il mercato» ha
   due forme, da scrivere sempre: le monete seguono BTC o il trend comune; i trade di monete diverse negli stessi
   giorni sono una sola scommessa ripetuta.
6. **Fase 5**, due domande in più: «Qualche regola, filtro o timeframe favorisce monete che so essere andate bene o
   male dopo il 2023?» e «Quanto pesano le monete più presenti nei trade dei candidati?».

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
   Lo stesso controllo vale per ogni caso di robustezza e per ogni timeframe adiacente della Fase 4 (un caso fuori
   si dichiara e non conta). In validazione e nel vault il tetto non è una condizione: si riportano la quota della
   moneta più presente e l'esito «senza le 3 monete migliori».
4. **Stima per la registrazione della validazione**: somma, su ogni moneta, di trade di costruzione × 349 / giorni
   di costruzione della moneta, dichiarata come stima. `conta_trade` non si usa mai sul periodo di validazione.

## 5. L'esame di una variante (Fase 2 del gruppo)

Tutto sul periodo che si giudica (costruzione, oppure validazione), con i trade di tutte le monete.

1. **I trade sommati** si mettono in un ordine fisso: per istante d'uscita, poi per simbolo in ordine alfabetico, poi
   per istante d'entrata (`statistica.ordina_trade_di_gruppo`). L'R medio del candidato è la media semplice degli R
   di tutti i trade (ogni trade rischia l'1%). N è il numero dei trade, n_j quelli della moneta j, w_j = n_j / N.
2. **Il blocco** è quello del Passo 4bis, punto 2: `lunghezza_blocco` su tutte le entrate e le uscite dei trade
   sommati. La finestra è la posizione più lunga fra TUTTE le monete (almeno un giorno): una sola posizione lunga
   su una moneta allunga la finestra per tutte, e molte uscite nello stesso giorno sono poche scommesse vere.
   k = N // blocco; con k < 3 la variante è non valutabile e consuma budget. La soglia è il quantile 0,97725 della
   t di Student con k − 1 gradi, come nella sezione 8.
3. **La baseline (a) di gruppo.** Per ogni moneta j con n_j > 0 si esegue la (a) della sezione 8 su quella moneta e
   si calcola `baseline_da_trade` sui suoi trade, con il blocco di `lunghezza_blocco` sui SUOI trade: numero A_j,
   errore e_j, deviazione standard dev_j. Numero di gruppo: A = Σ w_j · A_j. Errore: Σ w_j · e_j (come se le monete
   si muovessero insieme: non sottostima mai, e costa poco). Deviazione standard combinata: radice(Σ n_j · dev_j² /
   N), così il pavimento della (a) in `contro_baseline` vale radice(Σ n_j · dev_j²) / N. Una moneta senza trade del
   candidato pesa zero e non ha (a). Se la (a) di una moneta con n_j > 0 è non valutabile, l'errore di gruppo è
   infinito e la variante è non valutabile. Lo calcola solo `statistica.baseline_da_trade_di_gruppo`.
4. **La baseline (b) di gruppo.** Per ogni moneta j con n_j > 0 si esegue `simula_baseline_casuale` come nella
   sezione 8: n_j ingressi, durata media = `durata_media_barre` dei trade del candidato sulla moneta j, barre vietate
   della moneta j (riscaldamento, mesi sotto la liquidità, segnale non valido, e in validazione tutte le barre prima
   del 2023-01-17), 200 simulazioni con **semi da 1000·j a 1000·j + 199** (semi diversi per moneta: con lo stesso
   seme gli ingressi casuali di monete diverse cadrebbero quasi sulle stesse barre, un grappolo senza motivo di
   mercato). La simulazione s del gruppo (s da 0 a 199) ha R medio M(s) = Σ n_j · m_j(s) / Σ n_j, sulle monete che
   hanno trade nella simulazione s della moneta, con i pesi n_j del candidato. Numero: B = media delle M(s);
   errore = deviazione standard delle M(s) / radice(numero di M(s)); pavimento della (b) = deviazione standard
   delle M(s); percentile del candidato fra le M(s), sempre riportato come indizio. Se su una moneta gli ingressi
   non entrano, la variante è non valutabile. Lo calcola solo `statistica.baseline_casuale_di_gruppo`.
5. **Il pavimento a sfasamento comune.** Le entrate casuali della (b) non cadono insieme sulle diverse monete; i
   trade del candidato sì. Per questo, oltre ai pavimenti delle baseline, c'è il pavimento di una strategia senza
   vantaggio con gli stessi grappoli: le **strategie sfasate**. La strategia sfasata s (s da 0 a 199) prende gli
   ingressi del candidato (le barre di segnale) su tutte le monete e li sposta tutti dello stesso intervallo d_s,
   in cerchio sulla finestra del periodo; emette il segnale della variante (stessa direzione, stesso calcolo di
   stop e target) ed esce con la sua uscita (è la stessa `crea_casuale(ingressi)` della (b)). In dettaglio:
   * la finestra è l'unione delle finestre delle monete con trade del candidato: in costruzione dal primo giorno di
     dati più antico fra quelle monete al 2023-01-16 compreso; in validazione dal 2023-01-17 al 2023-12-31; L è il
     numero di barre del timeframe della variante in quella finestra;
   * m = il più alto fra 30 giorni e la durata massima dei trade del candidato nel periodo, in barre, ma non oltre
     L // 4; d_s = m + round(s × (L − 2m) / 199);
   * un ingresso spostato si salta, e si conta, se cade fuori dalla finestra della sua moneta, in una barra che
     manca nella serie della moneta, in una barra vietata o mentre la posizione è aperta;
   * per ogni s: M'(s) = R medio dei trade sommati della strategia sfasata, n'(s) = numero dei suoi trade;
   * pavimento a sfasamento = deviazione standard (con ddof 1) dei valori (M'(s) − media delle M') ×
     radice(n'(s) / N), sulle s con almeno un trade (la radice corregge per i trade saltati).
   Lo calcolano solo `motore.simula_sfasamento_comune` e `statistica.pavimento_sfasamento`.
6. **«Nettamente».** `statistica.contro_baseline` con il dizionario della (a) o della (b) di gruppo e con
   `pavimento_minimo` = il pavimento a sfasamento: l'errore del candidato (bootstrap a blocchi sui trade sommati,
   2000 ricampionamenti, seme 0, corretto per il blocco) non scende mai sotto il più alto fra il pavimento della
   baseline e il pavimento a sfasamento. Il resto è la regola della sezione 8, senza cambiamenti.
7. **Candidato.** In costruzione una variante diventa candidato se batte nettamente la (a) e la (b) di gruppo e il
   suo R medio dopo i costi, sui trade sommati, è positivo. Una variante non valutabile non è un vantaggio. La
   **vicinanza** (ordine dei ritocchi) è il `t` contro la (b) di gruppo.
8. **(c)**: buy and hold per anno, long e short, di ogni moneta con trade, combinato con gli stessi pesi w_j: solo
   contesto, come nella sezione 8.
9. **Si riportano sempre** (solo come informazione, mai come prova): blocco, k, massimo di uscite in un giorno UTC,
   durata massima di una posizione, monete con trade, quota della moneta più presente, effetto grappolo (errore del
   candidato² × N / varianza degli R: quante volte i trade sommati valgono meno di trade indipendenti).

## 6. Fase 3 e Fase 4 del gruppo

1. **Fase 3** come nel protocollo, sui trade sommati. Un filtro nato dai fallimenti è un ritocco e vale per tutte le
   monete (sezione 3, punto 2).
2. **Fase 4**, tutte le verifiche sui trade sommati di costruzione, ognuna registrata prima. «La (b) ricalcolata»
   vuol dire la (b) di gruppo e il pavimento a sfasamento ricalcolati nelle stesse condizioni.
   1. *Robustezza*: ogni parametro numerico ±20% con gli arrotondamenti della Fase 4 del protocollo. Ogni caso si
      conta prima con `conta_trade_di_gruppo`: un caso sotto 700 o oltre il tetto del 10% si dichiara e non conta;
      un caso non valutabile conta come fallito. Nei casi che contano il `t` contro la (b) ricalcolata resta
      positivo, e in almeno metà di essi il candidato la batte nettamente. Se contano meno della metà dei casi
      previsti, la verifica non è superata.
   2. *Timeframe adiacenti* (sezione 3.4): il `t` contro la (b) ricalcolata resta positivo su ognuno che ha 700
      trade e rispetta il tetto; gli altri si dichiarano e non contano; uno non valutabile conta come fallito.
   3. *Direzione*: come nel protocollo.
   4. *Stabilità*: l'R medio supera B in più della metà degli anni di costruzione (anno d'uscita) con almeno 100
      trade sommati.
   5. *Estremi*, tre prove, tutte da superare: (a) senza i 30 trade migliori l'R medio supera ancora B; (b) senza
      tutti i trade usciti nei 3 giorni UTC con la somma di R più alta, l'R medio supera la B ripesata sui trade
      rimasti (Σ n'_j · b_j / N', con b_j la media delle M della moneta j); (c) senza le 3 monete con la somma di R
      più alta, l'R medio supera la B ripesata sulle monete rimaste. La B ripesata usa le b_j già calcolate, senza
      simulazioni nuove; se non resta nessun trade la prova non è superata. Le soglie 100 e 30 sono quelle delle
      campagne singole (10 e 3) moltiplicate per 10, come 700 = 70 × 10. Lo calcola `statistica.estremi_di_gruppo`.
   6. *Regola intra-barra opposta e dettagli del feed*: si dichiara la differenza.
   7. *Ritardo di una barra*: il `t` contro la (b) ricalcolata col ritardo resta positivo e almeno la metà di quello
      senza ritardo; sotto, prima si cerca l'errore, come nel protocollo.
   8. *Liquidazione*: nessuna violazione su nessuna moneta.
   9. *Costi doppi*: commissione e slippage di ogni moneta raddoppiati; il candidato batte ancora nettamente la (b)
      ricalcolata a costi doppi e l'R medio a costi doppi resta positivo.
   Solo da riportare: la quota delle monete con almeno 10 trade il cui R medio supera la propria b_j; l'effetto
   grappolo.
3. Le verifiche non cambiano le regole del candidato e non servono a sceglierne un'altra, come nel protocollo.

## 7. Validazione e asticella

1. Dopo la Fase 5, di ogni famiglia va in validazione un solo candidato, quello con il `t` più alto contro la (b) di
   gruppo in costruzione; da lì le sue regole sono congelate. Tutti i candidati si validano insieme, una volta sola.
2. **Prima della validazione** la sessione fa `git pull origin research/campagna/GRUPPO` e controlla che esista
   `research/campagne/GRUPPO/via_libera_validazione.md`: lo scrive il coordinamento quando la prova a placebo di
   gruppo (sezione 11) dice che l'esame regge. Se il file non c'è: STOP, lo scrive all'utente e aspetta.
3. Ogni candidato gira una volta su ogni moneta (sezione 1, punto 5). La (b) di validazione vieta tutte le barre
   prima del 2023-01-17; il pavimento a sfasamento si calcola sulla finestra di validazione.
4. Va al vault solo se: (i) ha almeno 300 trade sommati; (ii) supera l'asticella; (iii) l'R medio dopo i costi dei
   trade sommati è positivo. Chi cade per (i) o (iii) resta nel conteggio m.
5. **Asticella**: `benjamini_hochberg` al 10% sui p-value del campo `p_value` di `contro_baseline`, con i trade
   sommati di validazione, la (b) di gruppo di validazione e il pavimento a sfasamento di validazione. m conta
   tutti i candidati di gruppo che hanno girato in validazione, compresi quelli sotto 300 trade (p-value 1). Il
   gruppo è una campagna a sé: la sua m non si unisce a quelle delle monete singole.
6. Si riportano, senza che decidano: quota della moneta più presente, «senza le 3 monete migliori», effetto
   grappolo. L'esito è provvisorio: lo conferma il coordinamento, che controlla anche il segno dell'R medio sommato.

## 8. Log, consegna, misure di processo

1. **Log** `campagne/GRUPPO/log.jsonl`, con i campi della sezione 6 del protocollo e `id` `GRUPPO-NNN`; una variante
   è una sola voce per tutte le monete. I campi del risultato sono il dizionario di `gruppo.esame_di_gruppo`,
   copiato così com'è: metriche sui trade sommati (profit factor, trade, R medio, R medio per anno d'uscita, R medio
   senza i 30 migliori, drawdown), `per_moneta` (trade e R medio), blocco, numero di blocchi, massimo di uscite in
   un giorno, durata massima, effetto grappolo, `baseline_a` e `baseline_b` con i campi della sezione 6 più pesi,
   numero di monete, semi e pavimento a sfasamento, `percentile_caso` fra le M(s), `buy_and_hold_per_anno` pesato.
2. **Consegna** `campagne/GRUPPO/consegna.md`, come nel Passo 3, più: metriche sommate per periodo e tabella per
   moneta; tutte le verifiche della Fase 4, compresi gli estremi per trade, giorni e monete; monete con trade e
   quota della più presente; massimo di posizioni aperte insieme, per direzione; trade al mese attesi in paper
   calcolati su tutte le monete dell'elenco; previsione per vault e trasferimento (solo fuori dal gruppo). Misure di
   processo come nel protocollo, più i minuti di calcolo per variante e le monete uscite in Fase 0. Esito vuoto:
   «nessuna strategia valida trovata per il gruppo». I file `lezioni_moneta.md` e `lezioni_metodo_proposte.md`
   tengono questi nomi. Nessun candidato si dichiara «validato».
3. I titoli dei commit dicono cosa si è fatto, mai i risultati; in Fase 0 dicono solo quante monete sono scaricate.

## 9. Il vault del candidato di gruppo (lo fa il coordinamento al Passo 5)

1. Il candidato di gruppo gira UNA volta sul vault, su tutte le monete del gruppo meno quelle uscite in Fase 0,
   ognuna con la fascia della sua scheda, il capitale iniziale di 1.000 USDT e le regole del bot.
2. **Passa se valgono tutte insieme** (il `criterio_vault` sui trade sommati):
   1. profit factor dopo i costi almeno 1,10, sul guadagno in USDT di tutti i trade di tutte le monete;
   2. almeno 300 trade sommati;
   3. somma dei guadagni in USDT di tutte le monete positiva;
   4. R medio dei trade sommati sopra il 90° percentile degli R medi sommati di 1.000 **strategie fittizie**.
3. **Le fittizie** sono quelle della sezione 8 del protocollo («stessa moneta, stessa direzione, stesso numero di
   trade, stessa durata media, stessa uscita»), costruite in modo da conservare anche i grappoli fra monete: gli
   ingressi del candidato nel vault spostati tutti dello stesso intervallo, come le strategie sfasate della sezione
   5, punto 5, con 1.000 sfasamenti (d_s = m + round(s × (L − 2m) / 999), s da 0 a 999, L le barre del vault). Con
   entrate casuali indipendenti fra monete la quarta condizione passerebbe per caso molto più spesso del 10%
   dichiarato, perché i trade del candidato cadono insieme sulle monete e le entrate casuali no (stima del
   coordinamento su regole da manuale: circa il 26% invece del 10%).
4. **Tasso del caso**: la quota delle 1.000 fittizie che passano le stesse quattro condizioni, con lo stesso 90°
   percentile (`criterio_vault` con 300 trade minimi, sulle metriche di `motore.metriche_di_gruppo`).
5. Si riportano, senza che decidano: il confronto con la (b) di gruppo del vault (semi 1000·j + s, blocco sui trade
   sommati, pavimento a sfasamento); la quota della moneta più presente; la tabella per moneta; le monete che
   smettono di avere candele nel vault, a parte.

## 10. Monete che muoiono nel vault, trasferimento, paper, giudizio d'insieme

1. **Chi ha diritto a quali monete.**
   1. Le monete del gruppo sono quelle di `monete.csv` meno quelle uscite in Fase 0, e restano quelle.
   2. Una moneta che smette di avere candele durante il vault resta nella somma fino al suo ultimo giorno con candele
      nei dati del vault. Le posizioni aperte si chiudono come nella sezione 7 del protocollo. Dopo quel giorno non
      apre più posizioni: né il candidato, né la (b), né le fittizie. Minimi e conteggi si giudicano sulla somma.
   3. Una migrazione o ridenominazione confermata sui dati (il vecchio simbolo finisce e il nuovo comincia nello
      stesso mese, con un rapporto di prezzo coerente) si ricuce e continua la moneta del gruppo. Una fusione in un
      contratto che esisteva già non si ricuce: per il gruppo la moneta è morta.
   4. Il contratto che continua o assorbe una moneta del gruppo non entra nel trasferimento del candidato di gruppo;
      per i candidati delle monete singole entra come ogni moneta di verifica.
   5. Le monete del gruppo restano possibili monete di verifica dei candidati delle monete singole (Passo 6), con la
      regola di `universo/monete_verifica_regola.md` e la fascia del volume del vault.
   6. Il candidato di gruppo si giudica su tutte le sue monete; in paper va solo su quelle negoziate all'avvio del
      paper, e lo dichiara il coordinamento al Passo 5.
   L'applicazione per nome di questa regola la scrive il coordinamento sul branch di coordinamento prima di aprire
   la sessione, e non va mai sul branch principale.
2. **Trasferimento del candidato di gruppo** (Passo 6): solo sulle monete fuori dal gruppo (monete di campagna e
   monete di verifica che non sono nel gruppo e non continuano né assorbono una moneta del gruppo). Un candidato di
   gruppo fa pochi trade per moneta, spesso meno dei 30 del vault: moneta per moneta l'esito sarebbe quasi sempre
   «non si sa». Il coordinamento propone di rendere decisiva la prova sui trade sommati di tutte quelle monete, con
   le stesse quattro condizioni della sezione 9 e il controllo «era solo il mercato» contro la (b) di gruppo del
   vault su quelle monete. **Decide il proprietario prima di «APRI IL VAULT»**, e la scelta si scrive in
   `vault/APERTURA.md`; senza una sua scelta vale il Passo 6 com'è, moneta per moneta. Non cambia nulla per la
   sessione di gruppo.
3. **Paper** (Passo 9, solo se il proprietario lo chiede): costruzione, validazione e vault si giudicano sui trade
   sommati, senza limiti di portafoglio. Il bot oggi tiene poche posizioni insieme (`config/regole_dimensione.md`):
   prima del paper il coordinamento rigioca i trade del candidato con i limiti del bot, e il paper si confronta con
   quel rigioco. La consegna riporta il massimo di posizioni aperte insieme, per direzione.
4. **Passo 5**: prerequisiti in più, la consegna del gruppo e l'esito della prova a placebo di gruppo.
   `vault/APERTURA.md` contiene anche il candidato di gruppo con le impronte dei suoi file, le impronte di
   `monete.csv`, delle schede e di questo file, e il rimando al file di coordinamento della sezione 10, punto 1.
5. **Passo 7**: nel giudizio d'insieme il candidato di gruppo conta come un candidato, con il suo tasso del caso; non
   è un'«idea di gruppo». Al punto 3 si unisce anche `research/campagna/GRUPPO`, e le sue lezioni entrano come
   quelle di una moneta.

## 11. La prova a placebo dell'esame di gruppo

1. L'esame di gruppo (sezioni 4-7) è un calcolo nuovo: prima del vault serve la prova che non promuova strategie
   senza vantaggio più spesso di quanto dichiara la sezione 11 del protocollo, anche con i trade a grappoli fra
   monete. La fa il coordinamento sul branch di coordinamento (`research/taratura/placebo_gruppo/`), con regole
   scritte, committate e pushate prima del lancio, con gli strumenti della sezione 13 allo stesso commit della
   sessione: le regole d'ingresso da manuale della prova del 9 ottobre, spostate dello stesso intervallo di tempo
   su tutte le monete insieme (così restano senza vantaggio ma tengono i grappoli), giudicate con l'esame di gruppo.
2. **Quando.** La prova parte prima della sessione di gruppo e corre insieme a lei: la sessione non ne vede i
   numeri. Deve essere finita prima della validazione del gruppo (sezione 7, punto 2): se l'esame regge, il
   coordinamento scrive `via_libera_validazione.md` (solo l'esito, nessun numero) sul branch principale e lo unisce
   nel branch della campagna. Se non regge: il coordinamento ferma la sessione di gruppo, porta i numeri al
   proprietario con una correzione proposta, e decide il proprietario.
3. Soglie, scritte prima: quota «netta» contro la (b) in costruzione al massimo 3%; quota con p-value sotto 0,10 in
   validazione al massimo 13%; deviazione standard del `t` contro la (b) in costruzione al massimo 1,10. Il resto
   (dati, combinazioni, controlli di copertura, intervalli) sta nelle regole della prova.

## 12. La sessione di gruppo

1. **Chi la apre**: il coordinamento, su delega del proprietario, con la sorgente del repository, il branch
   principale e il messaggio `research/apertura/gruppo.md` del branch di coordinamento, approvato con questo testo e
   mandato così com'è (una seconda sessione riceve lo stesso testo più «riprendi dalla nota del log»). La campagna
   di gruppo conta fra le tre campagne in corso. Valgono i controlli del Passo 4: modello e impostazioni dopo
   l'apertura, primo push entro 35 minuti, sessione ferma dopo 25 minuti senza aggiornamenti, giro orario sui soli
   titoli dei commit, domande girate subito al proprietario.
2. **Branch** `research/campagna/GRUPPO`, aperto nell'ordine della sezione 9 del protocollo; il controllo della data
   del primo commit del log usa l'istante della prima riga di questo file. Marcatore `research/.sessione` con
   `{"tipo": "campagna", "simbolo": "GRUPPO"}`.
3. **Percorsi ammessi.**
   * Lettura: `PROTOCOLLO.md`, `CHANGELOG.md`, `config/`, `src/`, `lezioni/metodo.md`, `campagne/GRUPPO/`,
     `data/insample/<S>/` per ogni S di `monete.csv`, `data/insample/BTCUSDT/` (mai `campagne/BTCUSDT/`).
   * Scrittura: `campagne/GRUPPO/` tranne `monete.csv`, `schede/`, `regole.md` e `via_libera_validazione.md`, che
     sono in sola lettura; `data/insample/` delle monete dell'elenco e di BTCUSDT; `src/` e `CHANGELOG.md` solo per
     correggere errori, come nel Passo 3.
   * Tutto il resto è vietato, in particolare le altre cartelle di `campagne/`, i dati delle monete di campagna
     diverse da BTCUSDT, `data/insample/GRUPPO/`, `data/placebo/`, `data/vault/`, `universo/`, `taratura/`,
     `apertura/`, `vault/`, `trasferimento/`, `confronto/`, `prova_processo/`, `passo4/` e i `percorsi_vietati`.
4. **Il guardiano** riconosce `GRUPPO` e ammette i dati delle monete di `monete.csv` solo se il file ha l'impronta
   SHA-256 scritta nel guardiano (la sessione non può allargarsi i permessi riscrivendo l'elenco); il caricatore
   rifiuta, in campagna, la lista dei contratti di oggi e l'indice dell'archivio, e con `GRUPPO` i simboli fuori
   dall'elenco e da BTCUSDT.
5. **Operazioni su molte monete** solo con script che leggono `monete.csv`, mai con elenchi di file o glob della
   shell sulla cartella dei dati.
6. **Calcoli lunghi.** Prima di ogni calcolo che dura più di 20 minuti la sessione pusha un commit intitolato
   «calcolo in corso fino alle HH:MM UTC circa»: il coordinamento non la giudica ferma fino a quell'ora più metà
   della durata annunciata. Ogni calcolo si spezza in pezzi sotto le 2 ore e riprende da dove era rimasto
   (`gruppo.py` tiene un file di avanzamento). Se un calcolo supera 3 volte la stima della sezione 14, la sessione
   scrive una nota nel log e lo dice all'utente; l'esito di una variante non cambia per la velocità.

## 13. Gli strumenti (scritti dal coordinamento prima della sessione, con i loro test)

* `dati.periodi_gruppo`: taglio e date per moneta (sezione 1).
* `dati`: in campagna il caricatore rifiuta la lista dei contratti di oggi e l'indice dell'archivio; con `GRUPPO`
  rifiuta i simboli fuori dall'elenco e da BTCUSDT.
* `motore.simula_baseline_casuale`: una chiave in più, `r_medio_per_seme`, l'R medio di ogni seme (vuoto per le
  simulazioni senza trade), senza cambiare nulla per le campagne singole.
* `motore.simula_sfasamento_comune`: le strategie sfasate della sezione 5 e le fittizie della sezione 9.
* `motore.metriche_di_gruppo`: le metriche dei trade sommati con le chiavi del `criterio_vault`.
* `statistica.ordina_trade_di_gruppo`, `statistica.baseline_da_trade_di_gruppo`,
  `statistica.baseline_casuale_di_gruppo`, `statistica.pavimento_sfasamento`, `statistica.effetto_grappolo`,
  `statistica.estremi_di_gruppo`, e `statistica.contro_baseline(..., pavimento_minimo=0.0)` (con 0 è identica a
  prima).
* `research/src/gruppo.py`, l'esecutore unico: `conta_trade_di_gruppo`, `esame_di_gruppo` (test, (a), (b),
  pavimento, confronti, `t`, p-value, percentile, R per anno, estremi, tabella per moneta, posizioni aperte insieme)
  ed `esame_vault` (per il coordinamento). Una moneta per processo, più processi insieme, un file di avanzamento in
  sola aggiunta con l'impronta del codice e la ripresa automatica, combinazioni solo alla fine.
* La sessione scrive solo, in `campagne/GRUPPO/codice/`, le funzioni al livello del modulo che creano la
  strategia: la variante, la sua (a), la sua strategia casuale da un insieme di ingressi, e il calcolo del segnale
  senza la condizione d'ingresso.
* Test obbligatori, fra gli altri: con una moneta sola e pavimento 0 ogni funzione di gruppo dà gli stessi numeri
  del percorso delle campagne singole; l'esito non cambia con l'ordine delle monete né con il numero di processi;
  due monete calcolate a mano; lo sfasamento è lo stesso su tutte le monete; gli ingressi saltati si tolgono e si
  contano; `periodi_gruppo` dà 2023-01-16 e 349 sulle schede vere.

## 14. Tempi (stime, servono solo ad annunciare i calcoli lunghi)

Una variante in costruzione, con (b) e pavimento a sfasamento: pochi minuti a 1d e 4h, 5-11 minuti a 1h, 20-45 a
15m; validazione 7-15 minuti a 1h; Fase 4 per candidato 2-3,5 ore a 1h, 4-8 a 15m; Fase 0 a ogni sessione nuova
circa 20 minuti più circa 20 per ogni timeframe in uso. Campagna intera: 2-4 giorni di sessioni. (Stime del
coordinamento dal ritmo misurato della prova del 9 ottobre e da prove di velocità del motore.)

## 15. Limiti (da riportare nei report finali, oltre a quelli della sezione 11 del protocollo)

* **Potenza bassa.** Le monete si muovono insieme e i trade a grappoli valgono molto meno di trade indipendenti: in
  una prova del coordinamento con regole da manuale, l'errore della media sommata era quello di circa un decimo
  dei trade. Un vantaggio di 0,10 R per trade passerebbe la validazione circa una volta su tre solo con 3.000 trade
  sommati o più, e quasi mai sotto; 0,05 R praticamente mai; 0,20 R circa una volta su sei fra 300 e 999 trade
  (stime su regole da manuale con un vantaggio aggiunto). La premessa «300-500 trade bastano» del Passo 4bis vale
  solo per trade indipendenti. La campagna di gruppo può finire senza candidati anche se un vantaggio piccolo c'è.
* **Sopravvivenza.** Le monete del gruppo sono quelle liquide nel 2023 e quotate prima del 2022: chi è morto prima
  non c'è.
* **Strategie fra monete escluse** (sezione 3, punto 3): dopo il vault non avranno un periodo chiuso.
* **Il bot e molte monete.** Non è verificato che il bot sappia eseguire una strategia su decine di monete, e i suoi
  limiti di portafoglio la cambierebbero (sezione 10, punto 3).
* **Il guardiano** giudica le azioni, non gli script (sezione 11 del protocollo); il divieto di leggere le appendici
  del protocollo è un'istruzione, non un blocco.
* **Mark e funding** delle 80 monete non sono mai stati scaricati prima: la loro copertura si scopre in Fase 0.
* **La prova a placebo di gruppo** usa lo stesso spostamento comune del pavimento: dove il pavimento decide, la prova
  regge in parte per costruzione; per questo riporta anche le misure senza pavimento.

## Appendice A — come si legge il protocollo per il gruppo

| Dove nel protocollo | Per il gruppo |
|---|---|
| §3.1 `in_sample` | Dall'inizio dei dati di ogni moneta al 2023-12-31; costruzione e validazione con il taglio comune (sezione 1) |
| §3.4 `trade_minimi`, `budget_varianti_per_moneta` | 700 / 300 / 300 sui trade sommati; 30 varianti per il gruppo (sezioni 3-4) |
| §3.4 `simulazioni_baseline_casuale`, `semi` | 200 per moneta, semi 1000·j + s (sezione 5, punto 4) |
| §3.4 `criterio_vault`, `simulazioni_caso` | Sui trade sommati, con 1.000 fittizie a sfasamento comune (sezione 9) |
| §4 regola 1 (vault chiuso) | Uguale, per tutte le 80 monete |
| §4 regola 6 (variante, ritocco, famiglia) | Una variante è una regola per tutte le monete (sezione 3) |
| §4 regola 7 (indipendenza) | La sessione non legge le campagne delle monete singole né il coordinamento (sezione 12) |
| §5 cartelle | `campagne/GRUPPO/` con `monete.csv`, `schede/`, `regole.md`, `log.jsonl`, `fase0_dati.md`, `impronte/`, `ipotesi.md`, `codice/`, `candidati/`, `consegna.md`, lezioni |
| §6 log | `id` `GRUPPO-NNN`, una voce per variante, campi della sezione 8 di questo file |
| §7 parametri e slippage | Per moneta, dalla scheda; capitale 1.000 USDT per moneta (sezione 2, punto 8) |
| §8 stima dei trade | `conta_trade_di_gruppo`, con il tetto del 10% (sezione 4) |
| §8 baseline, «nettamente», vicinanza | Sezione 5 |
| §8 asticella | Sezione 7, con m del solo gruppo |
| §8 tasso del caso | Sezione 9 |
| §9 apertura della sessione | Sezione 12 e `apertura/gruppo.md` |
| Passo 3, Fase 0 | Sezione 2 |
| Passo 3, Fasi 1, 3, 5 | Sezione 3 (Fase 1 e Fase 5) e sezione 6 (Fase 3) |
| Passo 3, Fase 2 | Sezione 5 |
| Passo 3, Fase 4 | Sezione 6 |
| Passo 3, Validazione | Sezione 7 |
| Passo 3, Consegna | Sezione 8 |
| Passo 4, controlli | Sezione 12, punto 1 |
| Passo 5 | Sezioni 9 e 10, punto 4 |
| Passo 6 | Sezione 10, punto 2 |
| Passo 7 | Sezione 10, punto 5 |
| Passo 9 | Sezione 10, punto 3 |
| §11 limiti | Sezione 15, in più |
