# Lezioni della campagna LINK6 (protocollo 4, Passo 9)

Scritto dal coordinamento il 18 ottobre 2026, sul branch principale, con la delega del proprietario del 17 ottobre
(«procedi in autonimia con gli altri passi», `research/protocollo_4_note.md`, sezione 0). La campagna è chiusa.
File del coordinamento: contiene fatti di altre campagne e del vault di BTC51, quindi resta fuori da ciò che legge
una sessione di ricerca futura (sezione 3 del protocollo).

## In una riga

Il metodo collaudato ha cercato su LINKUSDT con 16 idee e 33 varianti su 40 e non ha trovato candidati: in media le
varianti fanno quanto le loro entrate casuali (−0,030 R contro −0,032 R). **Nessuna strategia valida trovata; il
periodo di validazione e il vault di LINKUSDT restano mai usati da questa campagna.**

## I numeri del percorso

| Tappa | Esito | Fonte |
|---|---|---|
| Collaudo del metodo (primo giro, 17 ott) | prezzi senza vantaggio: 0 su 100 oltre la Fase 2, 14 su 100 con p sotto 0,10; vantaggio inserito da 0,35 R: 88 su 88 trovati; verifica sulle monete di controllo: 40 prove su 40 con il vantaggio, 1 variante finta su 100 la supera senza | `research/collaudo_4/esiti.md` |
| Passo 1, dati (17 ott) | 912 file con il CHECKSUM, impronte uguali al Passo 0 | `fase0_dati.md` |
| Passo 2, prima tornata (18 ott, 06:42-07:25 UTC) | 13 idee, 26 varianti con la Fase 2, nessuna oltre; V-019 (dalla Fase 3) scartata dal controllo sulle monete di controllo | `log.jsonl`, `fase5.md` |
| Passo 2, seconda tornata (07:51-07:54 UTC) | 3 idee nuove, 6 varianti, nessuna oltre la Fase 2; ferma a 33 su 40 per mancanza di idee con un perché | `log.jsonl` (N-010, N-011), `fase5.md` |
| Passi 3 e 4 (08:14 UTC) | niente da validare; «nessuna strategia valida trovata» | `validazione.md`, `consegna.md` |

Fonte dei numeri di questo file, se non detto altrimenti: le voci `registrazione` e `risultato` di `log.jsonl`
(copiato dal branch `research/campagna/LINK6`, commit bb8b444d; i trade di ogni variante restano in `risultati/` sul
branch).

## 1. Idee provate e cosa ne è stato

La tabella completa, con trade, R medio, entrate casuali e p-value di ogni variante, è in `consegna.md`. In sintesi,
sul periodo di costruzione (2020-01-17 → 2022-09-30, LINK +184% dall'inizio alla fine):

| Famiglia | Idee | Varianti | Migliore | Cosa ne è stato |
|---|---|---|---|---|
| Tendenza (rotture, medie, MACD, RSI a 50, incrocio di medie, VWAP, ore americane) | I-01, I-06, I-08, I-09, I-10, I-13, I-14, I-15 | 16 | V-028 (long all'incrocio EMA 20/50, 1h) +0,242 R, ma casuali +0,165 e p 0,130; 51,6 R su 53,2 nel 2020 | nessuna oltre la Fase 2: il rialzo del 2020, non il segnale |
| Ritorno alla media (Bollinger, RSI agli estremi, stocastico, fine settimana) | I-05, I-07, I-11, I-12, I-16 | 10 | V-033 −0,048 R | perdono tutte, e tutte fanno peggio delle loro entrate casuali |
| Funding contro la folla | I-02 | 2 (+V-019) | V-004 (long con il funding sotto zero, 1h) +0,128 R, p 0,047 | sotto 0,2 R; la modifica V-019 non migliora le monete di controllo (+0,010 R contro +0,05) |
| Volume anomalo | I-04 | 2 | V-007 +0,030 R | no |
| Range asiatico | I-03 | 2 | V-006 +0,005 R | no |

Quello che resta, come conoscenza su LINK (osservato sulla costruzione):

- **Le 32 varianti con la Fase 2 non si distinguono dal caso:** R medio −0,030 contro −0,032 delle loro entrate
  casuali; 16 su 32 battono le proprie entrate casuali; p-value medio 0,478, 5 sotto 0,10 contro 3,2 attesi, prova di
  uniformità p 0,416 (`fase5.md`).
- **I costi non spiegano i fallimenti:** 0,034-0,053 R a trade a 1h e 2h, 0,085 R a 30 minuti; anche prima dei costi
  l'R medio sta fra −0,08 e +0,16 (log, voce N-006).
- **I tre p-value più piccoli (0,001, 0,003, 0,003) sono short di tendenza** (V-021, V-029, V-031) con R medio fra
  +0,010 e +0,084. Gli short battono le proprie entrate casuali in 10 casi su 16, i long in 6 su 16: le entrate
  casuali degli short perdono in media 0,051 R, quelle dei long 0,014 (calcolo sul log). In un periodo che sale, uno
  short qualunque perde, e uno short che entra solo nei ribassi lo batte senza guadagnare.
- **Il funding sotto zero seguito da un acquisto è di nuovo la famiglia migliore**, come su BTC (BTC51: V-012 +0,171 R
  e V-020 +0,223 R in costruzione; `research/campagne/BTC51/lezioni.md`, sezione 1). Su BTC il candidato è caduto nel
  vault 2024-2026 e sulle grandi monete; su LINK la modifica non migliora le monete di controllo. Inferito: è un
  effetto del periodo di costruzione (un mercato che sale, in cui il funding negativo segna un ribasso breve da
  comprare), non una regola generale.

## 2. Errori di metodo e di processo

Nessun errore degli strumenti: le impronte sono rimaste quelle del collaudo, nessuna sessione ha chiesto di
cambiarli. Tre cose del testo e del processo, nessuna con effetto sui risultati:

1. **La sessione ha aspettato il proprietario per 8 ore.** Il Passo 1 è finito alle 22:24 UTC del 17 ottobre; la
   conferma del coordinamento per delega è arrivata alle 22:38, ma la sessione non l'ha presa per buona (un messaggio
   automatico non vale come istruzione del proprietario, sezione 0) e ha aspettato il proprietario, che ha scritto verso
   le 06:40 UTC (log, N-003 e N-004, registrata alle 06:42). Il comportamento della sessione era giusto: era il testo di apertura a non dire
   della delega. Tutto il Passo 2, 33 varianti, ha richiesto circa 17 minuti di lavoro della sessione (06:42-06:56 e
   07:51-07:54 UTC, commit del branch).
2. **Il canale delle richieste: due testi diversi.** `collaudo_4/regole.md`, punto 11, chiede che la verifica sia
   registrata nel log «in un commit precedente a quello della richiesta»; la guida pratica (sezione 3bis) fa
   registrare e chiedere nello stesso commit. R-001 è andata come diceva la guida; la registrazione era comunque
   prima dell'esecuzione (`research/monete_di_controllo_4/R-001.json`, nota).
3. **La guida pratica faceva leggere le versioni con `python3 -c`, che il guardiano rifiuta.** Trovato dalla sessione
   all'avvio, corretto sul principale e sul branch (a0f5b8ad). Il collaudo prova gli strumenti, non i comandi
   della guida sotto il guardiano.

Da tenere presenti, senza un errore:

4. **I tentativi rimasti.** Allo STOP della prima tornata (27 su 40) la sessione proponeva di fermarsi; il
   coordinamento le ha chiesto di usare i rimanenti solo con idee con un perché. Ne ha usate 6 su 3 idee nuove, nessuna
   oltre la Fase 2; due dei tre p-value più piccoli vengono da lì (V-029, V-031), entrambi con R sotto 0,1. La Fase 5
   dice «se restano tentativi, prova famiglie diverse del catalogo», ma non dice se ci si può fermare prima di 40: qui
   l'ha deciso il coordinamento, con la condizione scritta nel messaggio.
5. **Il primo messaggio della routine (07:38 UTC) è risultato consegnato ma la sessione non è ripartita**; è ripartita
   dopo il secondo invio (07:43), e li ha registrati come uno solo (N-010). Lo stato della routine non basta: conta la
   voce nel log della sessione.
6. **Ultracode non era attivo nella sessione di ricerca** (`CLAUDE.md` lo chiede per le sessioni di campagna); il
   proprietario è stato avvisato e la sessione è andata avanti.

## 3. Trappole dei dati

Nessuna nuova (`fase0_dati.md`):

1. **Mark mancanti per giorni interi** (2021-07-01, dal 2021-07-24 al 27, 2022-07-31 in costruzione; 2022-10-02 e
   2023-02-24 in validazione): il mark si prende dal last (sezione 9.6), come su BTC.
2. **Candele a volume zero in mezzo alla serie:** 6 a 15 minuti e 1 a 30 minuti, nel 2021-2022; si tengono. Nessuna
   in coda: la regola dell'ultima candela con scambi non è servita su LINK.
3. **Funding sempre a 8 ore** su LINK nel 2020-2023 (2.963 regolamenti in costruzione): la normalizzazione per i
   segnali non ha cambiato niente su LINK; conta per SOL nel novembre 2022 (`research/passo0_4/fatti_monete.json`).

## 4. Cosa ha funzionato e va tenuto

- **Il branch della ricerca con una storia propria:** la sessione non ha visto il branch principale né i risultati
  delle campagne passate.
- **La sessione che non si fida di un messaggio automatico «a nome del proprietario»:** costa tempo (punto 2.1), ma
  è la difesa giusta.
- **Il controllo della Fase 3 sulle monete di controllo:** l'unica modifica nata dai risultati (V-019) è stata fermata
  prima di consumare la Fase 2 su LINK.
- **La soglia di 0,2 R dopo i costi:** ha fermato i tre p-value piccoli con R vicino a zero, come su BTC (lezioni
  BTC51, punto 9).
- **La sessione che si ferma quando le idee con un perché finiscono**, invece di riempire i tentativi.

## 5. Cosa abbiamo capito, mettendo insieme le campagne

1. **Il metodo vede i vantaggi quando ci sono** (collaudo: 88 serie su 88 con almeno 0,35 R trovate, 0 su 90 senza
   vantaggio), quindi «nessun candidato» è un'informazione, non un difetto dello strumento.
2. **Sulle grandi monete, con le regole classiche del catalogo, a 15 minuti-4 ore, nel 2020-2022 non c'è un vantaggio
   di 0,2 R a trade dopo i costi.** BTC: 40 varianti, un candidato caduto nel vault. LINK: 33 varianti, nessuno.
   Prima ancora la ricerca 4.5 (630 varianti, nessuna oltre il vault) e il paniere a barre giornaliere (18 varianti,
   nessuna valida; `docs/backlog.md`, voce P6).
3. **La soglia dei trade spinge verso le candele brevi, dove i costi pesano di più.** Nel collaudo 400 varianti
   finte su 501 non arrivavano a 150 trade su LINK, e fra le 100 che ci arrivavano 87 erano a 15 minuti, 30 minuti o
   1 ora e solo 3 a 4 ore o più (`research/collaudo_4/esiti.md`); delle 33 varianti vere 25 sono a 30 minuti o 1 ora. Una strategia lenta, con costi più bassi in R, su una moneta sola non arriva ai minimi.
4. **Battere le entrate casuali non vuol dire guadagnare**, soprattutto in un periodo con una direzione: gli short di
   tendenza battono il caso perché il caso perde.

## 6. Cosa cambiare nella prossima versione del protocollo (proposte, decide il proprietario)

In ordine di importanza:

1. **Non ripetere la stessa ricerca su un'altra grande moneta.** Con lo stesso catalogo e gli stessi orizzonti, due
   campagne su BTC e LINK e la ricerca 4.5 dicono la stessa cosa (punto 5.2): mi aspetto lo stesso esito (stima, non
   una misura). Se si continua, va cambiato qualcosa di strutturale: il tipo di idee (fuori dal catalogo delle regole
   tecniche a una moneta), o l'unità di prova (la stessa regola su più monete insieme, perché le strategie lente
   arrivino ai trade minimi con costi più bassi), con la decisione generale della voce P6 del backlog.
2. **La delega del proprietario nel messaggio di apertura**, con le sue parole e la data, così la sessione non aspetta
   ore una conferma che il coordinamento può già dare (punto 2.1).
3. **La regola dei tentativi rimasti scritta nella Fase 5:** si usano solo con idee nuove con un perché scritto prima;
   ci si può fermare prima di 40 scrivendo perché; allo STOP decide il coordinamento (o il proprietario).
4. **Un solo testo per il canale delle richieste:** o «commit precedente» (regole) o «stesso commit, registrazione
   prima della richiesta» (guida), non tutti e due.
5. **Nel Passo 0, i comandi della guida pratica provati sotto il guardiano** dalla sessione di prova, oltre alle
   versioni.
6. **Nella Fase 5, il test dello scettico separato per direzione:** in un periodo che sale, i p-value degli short sono
   più piccoli per costruzione (le loro entrate casuali perdono di più).
7. **Ultracode:** decidere se è un requisito delle sessioni di ricerca; se sì, come garantirlo, visto che l'eredità
   alla creazione non è sicura (`CLAUDE.md`).
