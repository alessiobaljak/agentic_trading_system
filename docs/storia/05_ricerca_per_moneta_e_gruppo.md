# 05 — La prima stagione della ricerca a protocollo (6-13 ottobre 2026)

> Capitolo della storia del progetto: il riepilogo è in [`README.md`](README.md). Scritto il 18 ottobre 2026 da un lettore in sola lettura sul repository, poi ricontrollato da un secondo lettore che ha aperto le fonti e corretto nel testo gli errori trovati (60 affermazioni, 57 giuste, 3 corrette; in più l'elenco delle 326 idee rifatto da zero dai log, 326 righe su 326 uguali). Dove il testo dice «bozza» o «questo pezzo», intende questo capitolo.

Bozza per la storia completa del progetto. Scritta il 18 ottobre 2026 leggendo solo i file del repository e la
storia git (branch principale `claude/brave-albattani-1b12fv` e branch remoti `origin/research/...`). Nessun file
del repository è stato modificato.

**Come leggere i riferimenti.**

* I percorsi senza cartella iniziale stanno sotto `research/`: per esempio `confronto/risultati.md` è
  `research/confronto/risultati.md`. Il diario è `docs/andremo_live.md`, citato con il numero di riga
  dell'intestazione del paragrafo (per esempio «diario r. 3248»).
* Gli orari sono UTC, salvo dove è scritto «ora italiana».
* Dal 12 ottobre tutti i file delle campagne e del coordinamento sono anche sul branch principale (unione del Passo 7,
  `CHANGELOG.md`, riga del 2026-10-12). Prima vivevano sui branch `research/campagna/<MONETA>` e
  `research/coordinamento`. Gli hash dei commit citati sono quelli di quei branch.
* Quando un numero è un mio conteggio (rifatto dai log con uno script di sola lettura) lo scrivo come «mio
  conteggio dai log». Quando è una stima, lo scrivo.

**Le parole che tornano** (sigle interne, con il loro significato):

* **R**: il guadagno di un trade diviso il rischio iniziale (1 R = quanto si perde se scatta lo stop). «R medio» è
  sempre dopo i costi, salvo dove è scritto «lordo».
* **Costruzione** e **validazione**: le due parti dei dati fino al 31-12-2023 (circa 70% e 30%). **Vault**: il periodo
  chiuso dal 01-01-2024 al 30-09-2026, uguale per tutte le monete, da aprire una volta sola.
* **Baseline (a)**: la stessa regola senza la condizione d'ingresso, che entra appena è libera. **Baseline (b)**:
  200 strategie che entrano a caso con la stessa uscita e la stessa direzione. **(c)**: comprare e tenere, solo come
  contesto.
* **t**: di quanti errori standard una variante supera la baseline (b) (salvo dove è scritto «contro la (a)»).
  **«Netta»**: t sopra la soglia, circa 2.
* **Variante**: una regola completa provata, con una sola direzione. **Ritocco**: variante decisa dopo aver visto un
  risultato della stessa idea. **Famiglia**: una variante nuova con i suoi ritocchi. **Scarto**: variante non provata
  perché la stima dei trade era sotto il minimo (non consuma budget).
* **Candidato di Fase 2**: variante che in costruzione batte nettamente la (a) e la (b) con R medio positivo.
* **Coordinamento**: la sessione che organizza (apre le campagne, fa i riepiloghi, non legge le idee). **Campagna**:
  la sessione che studia una moneta (o il gruppo). **Guardiano**: il programma che blocca le letture vietate.
* I nomi come BTCUSDT-V10, ADAUSDT-037, GRUPPO-048 sono gli `id` delle varianti nei log. «L» e «S» = long e short.

---

## 0. In breve

* Dal 6 al 12 ottobre il sistema ha cercato strategie con un **protocollo di ricerca per moneta** scritto prima dei
  numeri (`PROTOCOLLO.md`, versioni 4.3, 4.4 e 4.5): 20 monete scelte con i dati del 2023, una sessione separata e
  cieca per ogni moneta, un periodo chiuso (il vault) aperto una volta sola.
* Il motivo: il gate automatico non trovava un vantaggio (cinque misure, `docs/backlog.md`, voce P0, «Perché»).
* **Prova di processo** (7 ottobre, versione 4.3): BTC, ETH, SOL, nessuna strategia; il rapporto ha portato a
  quattro regole nuove (versione 4.4) e alla decisione di rifare le tre campagne.
* **Campagne valide**: 3 con la 4.4 (8 ottobre) e 17 con la 4.5 (9 ottobre), più una **campagna di gruppo** su 80
  monete (10-11 ottobre). In tutto **630 varianti** (519 da idee nuove, 111 ritocchi) su circa 326 idee con fonte
  (`confronto/risultati.md`, sezione 0; il numero delle idee è un mio conteggio dai log).
* Imbuto: 630 varianti → **45 candidati di Fase 2** → **7 in validazione** → **3 al vault** → **0 passati**, contro
  0,02 passaggi attesi per puro caso (`confronto/risultati.md`, Punto 1).
* I tre bocciati nel vault (11 ottobre): BTCUSDT-V10 (profit factor 1,067 contro 1,10), BNBUSDT-045 (R −0,087),
  ADAUSDT-037 (R −0,164) (`vault/risultati.md`).
* Le **prove sul metodo** dicono che l'esame è affidabile contro il rumore e anzi più severo del dichiarato: con
  strategie finte «netta» lo 0,41% delle volte e p sotto 0,10 il 3,26% (`taratura/placebo/risultati.md`); nel gruppo
  0 su 85 e 2 su 93 (`taratura/placebo_gruppo/risultati.md`). Il prezzo è la poca potenza.
* La lezione centrale: **gli effetti che esistono (ultima mezz'ora del giorno UTC, ritardo delle monete dopo BTC,
  rottura dall'apertura del giorno su BTC) valgono meno del costo di un giro** a 15 minuti-1 ora; e lo **stop
  agganciato a un livello di prezzo** gonfia il confronto con le entrate casuali (`confronto/risultati.md`, sezioni
  3.2-3.3; `lezioni/metodo.md`, «Stop, costi e tetto del bot»).
* Il 12 ottobre il proprietario ha saltato il trasferimento e chiuso la ricerca (Passo 7). Il 13 ottobre sono venuti
  la prova degli ordini limite, lo stop della ricerca automatica del gate e la seconda edizione del protocollo
  (diario r. 3611 e r. 3627).

## Cronologia

| Quando (UTC) | Cosa | Fonte |
|---|---|---|
| 3 ott | Consegnata al proprietario una proposta di protocollo per moneta con vault 2024-2026 («versione 2 in PDF», non nel repo) | diario r. 2754 (controllo del 4 ottobre) |
| 5 ott, mattina | Versione 4.2 consegnata al proprietario; proposta del giorno «P0, il Passo 0» | diario r. 2895 (controllo del 5 ottobre) |
| 6 ott | Versione 4.3 approvata («sì alla 4.3, sì ai branch, vai col Passo 0»); commit 613d552d delle 19:51 | diario r. 2922; `git log -- research/PROTOCOLLO.md` |
| 6 ott, sera | Passo 0: motore, caricatore, statistica, guardiano; 36 difetti trovati e corretti dai revisori; STOP con 6 decisioni | diario r. 2922; `CHANGELOG.md` righe del 2026-10-06 |
| 7 ott, mattina | Passo 0 approvato («ok a tutte, vai col Passo 1»); Passo 1: 20 monete scelte (schede nel commit 73a54d1b delle 05:40) | diario r. 2948 |
| 7 ott, 06:39-13:33 | Prova di processo: BTC, ETH (due sessioni), SOL; nessuna strategia | `prova_processo/rapporto.md` §2 |
| 7 ott, 14:56 | Rapporto della prova (commit bbfaf550), 12 proposte | diario r. 3014 |
| 7 ott, sera | Il proprietario: «sì, rifalle con queste quattro modifiche»; scritta la 4.4 con due giri di revisione | diario r. 3036, r. 3053 |
| 8 ott, 05:08 | 4.4 approvata («ok alla 4.4, archivia e riapri le tre campagne»), commit 632671ec; tre branch archiviati | diario r. 3092 |
| 8 ott, 05:13-11:19 | Le tre campagne 4.4; BTC consegna un candidato (06:47); SOL ferma 4 h 20 su una domanda | diario r. 3102-3143 |
| 9 ott, mattina | Prova a placebo (regole 8b6abf6b, risultati ee34519f): l'esame regge | diario r. 3194 |
| 9 ott, 12:06 | 4.5 approvata («sì alla 4.5 con i tre punti»), commit 89f1d376 | diario r. 3213 |
| 9 ott, 12:13-20:28 | Le altre 17 campagne, tre alla volta | diario r. 3213-3248 |
| 9 ott, 17:35 | Correzione della 4.5: in validazione serve anche R medio positivo (commit c18a5313) | diario r. 3213 (riga delle 19:35 ora italiana) |
| 9 ott, 21:19 | Riepilogo del Passo 4 (commit e6d7e38a): 3 candidati per il vault | `passo4/riepilogo.md` |
| 10 ott, ~05:40 | «sì alla campagna di gruppo, no a rifare Bitcoin» | `passo4/riepilogo.md`, risposta |
| 10 ott, 17:11 | Testo della campagna di gruppo in vigore (commit 6e84ef42); prova a placebo di gruppo lanciata; sessione di gruppo aperta | diario r. 3315 |
| 11 ott, 07:49 | Il gruppo consegna: nessuna strategia (commit 121eb4ab) | diario r. 3485 |
| 11 ott, 17:29 | Il proprietario scrive «APRI IL VAULT» | diario r. 3517 |
| 11 ott, 19:26-21:39 | Vault aperto (de09b557) e giudicato: 0 su 3 (8e831841) | `vault/risultati.md` |
| 12 ott | «Sì, salta e passa alla conclusione»; Passo 7 fatto, branch uniti nel principale | diario r. 3562, r. 3569 |
| 13 ott | Prova degli ordini limite («conviene poco»); gate fermo; seconda edizione in bozza e poi approvata | diario r. 3611, 3627, 3657 |

---

## 1. Il protocollo: cos'era, le versioni, cosa è cambiato e perché

### 1.1 L'idea di fondo

Il protocollo (`PROTOCOLLO.md`, sezione 1) chiede a chi lo esegue di fare il ricercatore quantitativo: non trovare
una strategia che «funzioni sui dati», ma capire se esiste un vantaggio reale, spiegabile e robusto su una moneta.
«Nessuna strategia valida trovata per questa moneta» è scritto come esito frequente e valido. L'organizzazione:

* **Una campagna per moneta**, in una sessione separata, che non vede il lavoro delle altre monete fino al
  confronto finale (Passo 7). Ogni campagna lavora sul suo branch `research/campagna/<MONETA>`: le altre campagne
  non sono fisicamente presenti nella sua sessione (sezione 5).
* **Un guardiano meccanico** (`src/guardiano.py`, registrato in `.claude/settings.json`): legge il marcatore
  `research/.sessione` e rifiuta ogni azione fuori dai percorsi ammessi, i percorsi vietati del bot (dati, log,
  risultati, gate, registro, paper), i segreti e gli altri branch. Senza marcatore non interviene (sezione 2).
* **Prima scrivi, poi testi**: ogni test si registra nel log (`campagne/<MONETA>/log.jsonl`, solo in aggiunta)
  con ipotesi, previsione, parametri, criterio e trade stimati, prima di eseguirlo (regole 2-5).
* **Solo fonti pubblicate prima del 2024**, mai risultati del gate, del registro, del paper o di altre monete
  (Fase 1, punto 1). Per ogni idea almeno 10 spiegazioni concorrenti, fra cui sempre «è solo il mercato».
* **Il coordinamento** (sessione separata) apre le campagne, controlla, fa i riepiloghi, ma non legge ipotesi e
  risultati prima del Passo 7.

### 1.2 Periodi

| Periodo | Regola | Fonte |
|---|---|---|
| In-sample | dall'inizio dei dati della moneta su Binance Futures al 2023-12-31 | `PROTOCOLLO.md` §3.1 |
| Costruzione | i primi (70 × giorni) // 100 giorni, calcolati con numeri interi da `periodi_campagna` di `src/dati.py`, scritti nel log prima di caricare i prezzi | §3.4, Fase 0 punto 1 |
| Validazione | dal giorno dopo la costruzione al 2023-12-31; gira con gli indicatori già caldi e conta solo i trade entrati dopo la costruzione | Fase 0 punto 1 |
| Vault | dal 2024-01-01 al 2026-09-30, uguale per tutte; il caricatore rifiuta ogni data dopo il 2023 finché non esiste `vault/APERTURA.md`, che si crea solo dopo la frase esatta «APRI IL VAULT» | regola 1 |
| Gruppo (solo campagna di gruppo) | taglio comune: costruzione fino al 2023-01-16, validazione dal 2023-01-17 al 2023-12-31 (349 giorni) per tutte le 80 monete | `campagne/GRUPPO/regole.md` §1 |

Esempio: BNBUSDT, primo mese 2020-02, costruzione 1.001 giorni (2020-02-01 → 2022-10-28), validazione 2022-10-29 →
2023-12-31 (`campagne/BNBUSDT/log.jsonl`, voce BNBUSDT-N003).

### 1.3 La scelta delle monete (Passo 1, 7 ottobre)

Criterio scritto prima dei numeri (`universo/selezione_log.md`): contratti perpetui in USDT con dati nell'archivio di
data.binance.vision (anche i delistati), listing prima del 2022-01-01, dati almeno fino a dicembre 2023, volume medio
2023 di almeno 20 milioni di USDT al giorno, le prime 20 per volume 2023.

| Passaggio | Numero |
|---|---|
| Contratti perpetui in USDT con dati nell'archivio | 895 |
| Esclusi per listing dal 2022 in poi | 759 |
| Esclusi per dati finiti prima di dicembre 2023 | 12 |
| Esclusi per volume 2023 sotto 20 milioni | 26 |
| **Idonee** | **100** (24 oggi non più negoziate) |
| **Monete di campagna** | **20** |

Le 20, in ordine di volume 2023 (milioni di USDT al giorno): BTC 11.505, ETH 5.513, SOL 1.104, XRP 811, DOGE 519,
BNB 401, LTC 382, MATIC 374, BCH 339, LINK 319, AVAX 289, ADA 272, TRB 258, FIL 221, 1000SHIB 212, DYDX 201, MASK
199, FTM 199, GALA 198, ETC 197. Slippage per lato: 0,01% BTC, ETH, SOL; 0,02% da XRP a DYDX; 0,05% MASK, FTM, GALA,
ETC. MATICUSDT e FTMUSDT non sono più negoziate con quel simbolo; l'informazione resta sul branch di coordinamento
(`universo/selezione_log.md`, tabella dell'esecuzione; `universo/monete_campagna.csv`). Le altre 80 idonee sono
diventate le monete della prova a placebo e della campagna di gruppo (`universo/monete_idonee_non_campagna.csv`).

### 1.4 L'esame di una variante: soglie e regole

Tutti i valori sono in `config/parametri.yaml` (stato «congelato», approvato il 7 ottobre) e in `PROTOCOLLO.md` §3.4
e §8.

| Regola | Valore | Fonte |
|---|---|---|
| Timeframe dei segnali | 15m, 30m, 1h, 2h, 4h, 6h, 8h, 12h, 1d; durata delle posizioni libera | §3.4 |
| Trade minimi | **100** per direzione in costruzione con la 4.3; **70** in costruzione, 30 in validazione, 30 nel vault dalla 4.4 | §3.4; appendice 3 |
| Stima dei trade | con `conta_trade` di `src/motore.py`, una volta sola, sulle regole esatte che si registrano; sotto il minimo è uno scarto | §8 (dalla 4.4) |
| Budget | 30 varianti per moneta, **da usare per intero** dalla 4.4; prima le idee nuove con fonte, poi i ritocchi in ordine di t; al massimo 5 ritocchi per famiglia; al massimo 2 varianti per fonte | regola 6; §3.4 |
| Baseline (a) e (b) | (a) la regola senza condizione d'ingresso; (b) 200 strategie casuali (semi 0-199) con la stessa uscita e direzione, fuori dalle barre dove il segnale non è valido | §8 |
| «Nettamente» | t = (R medio del candidato − baseline) / errore; errore dal bootstrap a blocchi (2000 ricampionamenti, seme 0), corretto per il blocco, mai sotto il «pavimento» di una strategia senza vantaggio; soglia = quantile 0,97725 della t di Student (circa 2); blocco lungo almeno la posizione più lunga e almeno un giorno; meno di 3 blocchi = non valutabile | §8 (dalla 4.4) |
| Candidato di Fase 2 | batte nettamente (a) e (b) **e** R medio dopo i costi positivo | §8 |
| Verifiche della Fase 4 | robustezza (ogni parametro ±20%), timeframe adiacenti, stabilità per anno, senza i 3 trade migliori, regola intra-barra opposta, ritardo di una barra (il t deve restare almeno la metà), nessuna violazione della liquidazione, costi doppi (battere ancora la (b) a costi doppi con R positivo) | Fase 4 |
| Validazione | un solo candidato per famiglia; una sola esecuzione; trade minimi, asticella di Benjamini-Hochberg al 10% sui p-value contro la (b), e dal 9 ottobre R medio positivo | Validazione punti 1-4 |
| Criterio del vault | tutte insieme: profit factor dopo i costi almeno 1,10; almeno 30 trade; rendimento totale positivo; R medio sopra il 90° percentile di 1000 entrate casuali con la stessa uscita | §3.4 `criterio_vault` |
| Tasso del caso | quota di 1000 strategie casuali che passano lo stesso criterio nel vault | §8 |
| Trasferimento | il candidato gira senza modifiche sulle altre monete; dalla 4.5 il numero di monete richieste cresce con quelle provate (binomiale sotto il 5%, mai sotto 2); probabilità per moneta 0,02 | Passo 6 punto 4; `vault/APERTURA.md` |

Costi e dimensione (`config/parametri.yaml`, sezione `fatti`): commissione taker 0,05% per lato su tutti gli ordini;
slippage per fascia di volume; funding storico vero ai settlement; rischio 1% per trade
(`DEFAULT_RISK_PER_TRADE`, `bot/config.py:162`), leva massima 2, margine isolato, mantenimento 0,025; lo stop
massimo del bot (6%, `MAX_STOP_PCT`) è riportato dal motore di ricerca ma non imposto.

### 1.5 Le versioni e cosa è cambiato

| Versione | Quando | Cosa | Perché | Fonte |
|---|---|---|---|---|
| 2 (PDF) | consegnata il 3 ott | proposta di protocollo per moneta con vault 2024-2026 | — (non è nel repo) | diario r. 2754 |
| 3 | prima del 5 ott | citata solo nell'appendice 1 («la regola c'era nella v3») | non ricostruibile dal repo | `PROTOCOLLO.md`, appendice 1 |
| 4.2 | consegnata il 5 ott mattina | la base delle modifiche dell'appendice 1 | — | diario r. 2895; `docs/backlog.md` voce P0 |
| **4.3** | approvata il 6 ott (commit 613d552d delle 19:51) | rimessi 8h, 12h e 1d (il numero di trade dipende da quanto spesso si entra, non dalla candela); date di delisting solo sul branch di coordinamento; chiusura delle posizioni al delisting; funding contato solo se è un costo quando cade nella stessa candela dell'uscita; divieto di aprire segreti; **un branch per campagna**; test di parità prima del paper; poi i due ritocchi del 6 ott: nomi `research/...` dei branch e **il guardiano** | sapere che una moneta è morta dopo il 2023 spinge verso gli short; «una regola scritta è disciplina, il guardiano è un blocco» | appendici 1 e 2 |
| **4.4** | scritta il 7 ott, approvata l'8 ott alle 05:08 (commit 632671ec) | le quattro modifiche: **una sola stima dei trade** (`conta_trade`); **una sola lettura di «nettamente»** (`contro_baseline`: errore corretto per il blocco, pavimento, soglia di Student, almeno 3 blocchi, 200 simulazioni a semi fissi); **minimo in costruzione da 100 a 70**; **budget usato per intero** con ritocchi ordinati per t, 5 per famiglia, un candidato per famiglia in validazione. In più: criterio scritto per ogni verifica della Fase 4; date con numeri interi; scheda senza data di listing; guardiano rinforzato (storia dei commit solo per la propria cartella, niente strumenti GitHub, fetch solo del proprio branch); un'istanza nuova della strategia a ogni esecuzione | nella prova la stessa idea dava 83 o 105 trade secondo il metodo di stima; una variante era «netta» con un calcolo e non con l'altro; 34 scarti su 44 erano idee lente, 16 stime fra 70 e 99; 34 varianti di budget non spese | appendice 3; `prova_processo/rapporto.md` §3, §5, §9 |
| **4.5** | approvata il 9 ott alle 12:06 (commit 89f1d376) | variante netta contro (a) e (b) ma con R non positivo: entra nell'ordine dei ritocchi; «trovare un vantaggio vero, non finire il compito»; misure di processo in ogni consegna; **sessioni aperte dal coordinamento su delega**, massimo 3 insieme, controllo ogni ora, domande girate subito al proprietario; caricatore unico di last e mark (`carica_serie_allineate`); **campagna di gruppo (Passo 4bis)** prima del vault; numero di monete del trasferimento che cresce con le monete provate; prova a placebo come prerequisito del vault | SOL si era fermata l'8 ott su un caso non scritto (4 h 20 senza risposta); tre campagne avevano scritto tre allineamenti diversi del mark; con R medi di 0,05-0,10 servono 300-500 trade; con l'1% a moneta, 2 passaggi su 80 monete escono il 19% delle volte per caso | appendice 4 |
| 4.5, correzione | 9 ott, 17:35 (commit c18a5313) | in validazione serve anche **R medio dopo i costi positivo**; chi cade per questo resta nel conteggio dell'asticella; vale anche per le consegne già fatte | FILUSDT si è fermata alle 16:21 perché il suo candidato in validazione perdeva (−0,117 R) ma meno del caso (p 0,085): il caso non era scritto | appendice 4, ultima riga; diario r. 3213 |
| Testo del gruppo | in vigore il 10 ott alle 17:11 (commit 6e84ef42), approvato in anticipo alle 06:35 | `campagne/GRUPPO/regole.md`: trade sommati su 80 monete; minimi 700 / 300 / 300; blocco calcolato su tutti i trade insieme; baseline combinate moneta per moneta; **pavimento delle strategie sfasate** (gli ingressi del candidato spostati tutti insieme, che conservano i grappoli fra monete); niente regole fra monete; taglio comune al 2023-01-16 al posto del 70/30; prova a placebo di gruppo prima della validazione | con il 70/30 per moneta il 34,5% dei giorni-moneta di validazione (9.666 su 27.986) sarebbe caduto nella costruzione di un'altra moneta; tre giri di revisione: 75, 54 e 11 rilievi | `campagne/GRUPPO/regole.md` §1, §4, §5; diario r. 3315 |

Nota: le appendici del protocollo dicono che nessuna modifica è stata scelta per far passare o cadere una strategia;
il rapporto della prova ammette che la lettura unica di «nettamente» è nata «anche dall'aver visto» una variante il cui
esito cambiava fra i due calcoli (`prova_processo/rapporto.md` §9, «Come sono nate le modifiche»).

### 1.6 Chi faceva cosa: sessioni, coordinamento, controlli

* **4.3 e 4.4**: le campagne le ha aperte il coordinamento su indicazione del proprietario del 7 ottobre («apri tu in
  autonomia la sessione BTC e poi quando lo ritieni opportuno le altre», diario r. 2968).
* **4.5**: delega scritta nel protocollo (Passo 4 punto 1): messaggio di apertura approvato e identico per ogni moneta
  (`apertura/campagna.md`, commit 27461905), al massimo tre campagne in corso, controllo orario con un promemoria
  programmato (routine `trig_01LGmfrQRrAL3Qm9N9bQJPiB`, diario r. 3213), domande delle campagne girate al proprietario
  «così com'è», controllo che modello e impostazioni siano quelli chiesti (Opus 5.5 con ultracode: richiesta del
  proprietario dell'8 ottobre, diario r. 3120).
* **Il coordinamento non leggeva ipotesi né risultati**: per il riepilogo del Passo 4 ha letto solo conteggi, righe
  d'esito e, per i candidati, trade, p-value, m e segno dell'R di validazione (`passo4/riepilogo.md`, intestazione).
  Le «fughe» involontarie (riassunti automatici delle sessioni con qualche numero) sono state dichiarate nel diario
  (diario r. 3213, righe delle 15:17-18:16 ora italiana).

---

## 2. Le campagne, una per una

### 2.1 La prova di processo (7 ottobre, versione 4.3, minimo 100 trade)

Tre campagne sulle prime tre monete della lista, per provare protocollo e strumenti senza aprire il vault. Il
coordinamento ha poi archiviato i loro branch (`origin/research/archivio/campagna/<MONETA>`) e le campagne sono state
rifatte con la 4.4, da zero, senza leggere l'archivio.

| | BTCUSDT | ETHUSDT | SOLUSDT |
|---|---|---|---|
| Orario dei commit di campagna | 06:40 → 07:34 (55 min) | 10:33 → 13:33 (3 ore; più 17 min persi in una prima sessione) | 08:43 → 09:39 (56 min) |
| Idee registrate (scarti + varianti) / con almeno una variante | 15 / 10 | 23 / 13 | 13 / 10 |
| Varianti testate su 30 | 16 (più 12 verifiche) | 23 | 17 |
| Budget non speso | 14 | 7 | 13 |
| Scarti per stima sotto 100 trade | 11 | 22 | 11 |
| Candidati in validazione | 0 | 0 | 0 |
| Esito | nessuna strategia valida | nessuna strategia valida | nessuna strategia valida |
| Punta del branch archiviato | b60dd847 (consegna 42272a90) | a60898c2 | d1955b4d |

Fonte: `prova_processo/rapporto.md` §2; `git log` dei branch di archivio. Le 56 varianti: 8 sopra il 96°-97° percentile
delle entrate casuali (circa 2 attese per caso), nessuna oltre 2 errori standard a blocchi (rapporto §5, punto 2).
La consegna ETH dell'archivio parla di «22 idee di 17 famiglie», il rapporto di 23 idee registrate: le due fonti
contano in modo diverso (consegna ETHUSDT sul branch di archivio, «In una frase per riga»; rapporto §2).

### 2.2 Le 21 campagne valide

Colonne: «Minuti» dal primo all'ultimo voce del log; «Varianti» = idee nuove / ritocchi / scarti (consegne e
`confronto/risultati.md` §1); «Idee» = idee con almeno una variante provata + idee rimaste solo scarti (mio conteggio
dai log, campo `idea`); «t più alto» contro la (b) in costruzione (log); «F2» = candidati di Fase 2; «Commit» = commit
della consegna sul branch `research/campagna/<MONETA>`.

| Moneta | Vers. e data | Minuti (log) | Varianti | Idee | t più alto (variante, famiglia, tf, dir.) | F2 | In validazione | Nel vault | Esito | Commit |
|---|---|---|---|---|---|---|---|---|---|---|
| BTCUSDT | 4.4, 8 ott | 80 (05:28-06:47) | 25 / 5 / 7 | 15 + 2 | 3,58 (V35, ultima mezz'ora, 30m S, ritocco) | 5 | V10: 136 trade, R +0,048, p 0,048 | **non passa** (PF 1,067) | un candidato al vault | 8634b6ac |
| ETHUSDT | 4.4, 8 ott | 38 (05:20-05:58), poi ricalcolo fino alle 14:06 | 30 / 0 / 4 | 16 + 2 | 2,67 (026, rifiuto del massimo di ieri, 1h S) | 1 | nessuno (026 caduto in Fase 4) | — | nessuna strategia | 8c156fac; ricalcolo f66fcf00 |
| SOLUSDT | 4.4, 8 ott | 352 (05:27-11:19), con 4 h 20 di attesa | 22 / 8 / 9 | 13 + 0 | 2,78 (023, ultima mezz'ora, 30m S, rit.) | 4 | nessuno (costi doppi, ritardo) | — | nessuna strategia | 8eb18045 |
| XRPUSDT | 4.5, 9 ott | 41 | 27 / 3 / 7 | 14 + 1 | 2,33 (V21r3, premio del perpetuo sul mark, 1h L, rit.) | 1 | V21r3: 5 trade, «non si sa» | — | nessuna strategia | 7db8a199 |
| DOGEUSDT | 4.5, 9 ott | 42 | 25 / 5 / 15 (14 per stima, 1 in Fase 4) | 15 + 1 | 2,14 (042, Bollinger, 1h S, rit.) | 1 | nessuno (042: robustezza e costi doppi) | — | nessuna strategia | b0230b27 |
| BNBUSDT | 4.5, 9 ott | 62 | 25 / 5 / 15 | 16 + 2 | 3,96 (045, RSI a 2 periodi, 1h L, rit.) | 3 | 045: 32 trade, R +0,047, p 0,031 | **non passa** (R −0,087) | un candidato al vault | 2e29620a |
| LTCUSDT | 4.5, 9 ott | 34 | 25 / 5 / 6 | 13 + 0 | 1,95 (014, intervallo d'apertura, 1h S, R −0,068) | 0 | — | — | nessuna strategia | 679e303b |
| MATICUSDT | 4.5, 9 ott | 31 | 22 / 8 / 16 | 12 + 3 | 2,21 (026, squilibrio degli ordini, 1h S, rit.); candidato 025: 2,12 | 1 | nessuno (025: ritardo, costi doppi) | — | nessuna strategia | a25cfcbf |
| BCHUSDT | 4.5, 9 ott | 27 | 25 / 5 / 8 | 14 + 0 | 1,62 (002, momento, 1d S) | 0 | — | — | nessuna strategia | 8290ea84 |
| LINKUSDT | 4.5, 9 ott | 39 | 27 / 3 / 4 | 15 + 2 | 2,23 (V24, inversione giornaliera, 1d L; contro la (a) 1,71) | 0 | — | — | nessuna strategia | 6ada6c20 |
| AVAXUSDT | 4.5, 9 ott | 42 | 25 / 5 / 7 | 14 + 0 | 3,52 (V12, ultima mezz'ora, 30m S, R +0,007) | 5 | nessuno (4 ai costi doppi, V14 al ritardo) | — | nessuna strategia | 1fe96b0f |
| ADAUSDT | 4.5, 9 ott | 46 | 22 / 8 / 11 | 12 + 3 | 6,57 (038, intervallo d'apertura, 15m L, rit., R −0,067: netta ma in perdita) | 6 | 037: 82 trade, R +0,624, p 0,014 | **non passa** (R −0,164) | un candidato al vault («con forti riserve») | 47d6b2cc |
| TRBUSDT | 4.5, 9 ott | 61 | 27 / 3 / 14 | 15 + 3 | 1,37 (I-13-S, intervallo d'apertura, 15m S, R −0,129) | 0 | — | — | nessuna strategia | d699162f |
| FILUSDT | 4.5, 9 ott | 146, di cui 92 di pausa | 22 / 8 / 9 | 12 + 4 | 3,40 (035, ultima fascia del giorno, 4h L, rit.); candidato 025: 2,34 | 10 | 025: 87 trade, R −0,117, p 0,085 → fallito | — | nessuna strategia | dff590fa |
| 1000SHIBUSDT | 4.5, 9 ott | 43 | 27 / 3 / 10 | 16 + 0 | 2,15 (030, ultima mezz'ora, 30m S, rit.) | 2 | nessuno (costi doppi) | — | nessuna strategia | 2ee30f61 |
| DYDXUSDT | 4.5, 9 ott | 75 | 21 / 9 / 9 | 12 + 0 | 2,22 (008, ritardo rispetto a BTC, 1h L) | 1 | 008: 83 trade, R −0,178, p 0,968 | — | nessuna strategia | e971c96e |
| MASKUSDT | 4.5, 9 ott | 27 | 25 / 5 / 6 | 14 + 1 | 2,85 (029, inversione dopo una barra estrema, 1h S, rit.) | 1 | 029: 41 trade, R +0,011, p 0,293 | — | nessuna strategia | 3b971314 |
| FTMUSDT | 4.5, 9 ott | 27 | 26 / 4 / 8 | 15 + 0 | 2,22 (036, momento, 1d S, rit.; contro la (a) 1,47) | 0 | — | — | nessuna strategia | e53efc87 |
| GALAUSDT | 4.5, 9 ott | 26 | 28 / 2 / 7 | 16 + 1 | 2,22 (032, last sopra il mark, 1h S) | 1 | nessuno (032: costi doppi) | — | nessuna strategia | 20db9413 |
| ETCUSDT | 4.5, 9 ott | 63 | 23 / 7 / 9 | 13 + 4 | 3,85 (035, ultima mezz'ora, 30m S, rit., R −0,009: netta ma in perdita) | 3 | nessuno (costi doppi, ritardo) | — | nessuna strategia | e9b68c36 |
| GRUPPO (80 monete) | testo del 10 ott, 10-11 ott | 871, di cui 666 di pausa (203 di lavoro) | 20 / 10 / 6 | 13 + 2 | 2,06 (048, ritardo dopo un'ora forte di BTC, 1h L, rit.; soglia 2,16) | 0 | — | — | nessuna strategia per il gruppo | 121eb4ab |

Fonti: righe d'esito di `campagne/<MONETA>/consegna.md`; `passo4/riepilogo.md` (minuti, ritocchi, scarti, candidati);
`confronto/risultati.md` §1 (t più alto, famiglie); `campagne/GRUPPO/consegna.md` («Misure di processo»). I minuti
del log coincidono con quelli del riepilogo entro un minuto (mio conteggio).

**Totali** (`confronto/risultati.md`, sezione 0 e riga «Totali»): 630 varianti, 519 da idee nuove, 111 ritocchi, 45
candidati di Fase 2 (34 da ritocchi, 11 da idee nuove), 7 in validazione, 3 al vault, 0 passati. **Discordanza**: lo
stesso file scrive «197 scarti», ma la somma della sua colonna per campagna fa 187, e nei 21 log le voci «scarto» sono
187 (una delle quali, DOGEUSDT-042, è uno scarto di Fase 4 e non per stima dei trade) (mio conteggio dai log).

**Tempi.** Le campagne della 4.5 hanno lavorato 26-75 minuti ciascuna, FILUSDT 146 con 92 di attesa; la mediana è
41 minuti (mio conteggio dai log; il diario dice «25-85 minuti, mediana circa 41», r. 3248; `confronto/risultati.md`
§4.3 punto 12 dice «25-80 minuti»). Il diario annota: «il tempo non è mai stato il limite; il limite è la potenza»
(diario r. 3143, riga «8 ott, sera»).

### 2.3 Le domande che hanno fermato le campagne

* **SOLUSDT, 8 ottobre, 05:51-10:14**: una variante batte nettamente le due baseline ma ha R medio negativo; entra
  nell'ordine dei ritocchi? La regola non lo diceva. Risposta del proprietario: «sì» (diario r. 3120). È diventata la
  regola 6 della 4.5.
* **FILUSDT, 9 ottobre, 16:21-17:52**: il candidato 025 in validazione perde (−0,117 R) ma batte le entrate a caso con
  p 0,085; «fallito» o «vault»? Il proprietario: «sì, applica la regola a tutti i candidati», poi «fallito» nella
  sessione (`campagne/FILUSDT/consegna.md`, intestazione; diario r. 3213).
* **GRUPPO, 10 ottobre, 19:12**: il controllo positivo degli strumenti non passava per poco (t 1,96 contro 2,07);
  scelta del proprietario: rifarlo con l'uscita a 1 giorno (diario r. 3364; `campagne/GRUPPO/consegna.md`, «Come si
  è lavorato»).

### 2.4 Il percorso della campagna di gruppo

* **Perché**: con R medi di 0,05-0,10 servono 300-500 trade e una moneta ne dà 30-70 per periodo (`PROTOCOLLO.md`,
  Passo 4bis). Proposta già al primo posto nel rapporto della prova (`prova_processo/rapporto.md` §6 punto 1).
* **Monete**: le 80 idonee non di campagna; controllo della storia prima di congelare il testo: 80 su 80 con storia
  sufficiente, la più tarda ROSEUSDT con il primo giorno comune di last e mark il 2021-12-31 (diario r. 3304).
* **Tre sessioni**: la prima (17:12) e la seconda (17:43) si sono fermate perché mancavano pytest e scipy e il guardiano
  vieta pip in campagna; causa trovata: Python 3.13 sulle macchine nuove e numpy 1.26.4 fissato non installabile.
  Correzioni: de2618ae, e761cc05, 2bfb2f99; la terza (18:35) ha lavorato (diario r. 3332, r. 3343).
* **Lavoro**: 30 varianti (20 idee nuove, 10 ritocchi su due famiglie), 6 scarti sotto i 700 trade o per una moneta
  sopra il 10% dei trade; nessuna variante netta contro (a) e (b); validazione mai usata
  (`campagne/GRUPPO/consegna.md`).
* **Lettura della campagna**: «con 80 monete che si muovono insieme, i trade sommati valgono molti meno trade
  indipendenti (effetto grappolo fino a 33)»; gli effetti più vicini (ritardo dopo BTC, rientro del rendimento
  proprio rispetto a BTC) valgono +0,04-0,09 R lordi contro 0,05-0,07 R di costi (stessa consegna, «Cosa dicono i
  numeri»).

### 2.5 I sette candidati in validazione e i tre del vault

| Candidato | Regola, in parole | Costruzione | Validazione | Vault (2024 → set 2026) | Fonte |
|---|---|---|---|---|---|
| **BTCUSDT-V10** | long a 1h alla prima chiusura del giorno sopra apertura + 0,5 × range di ieri (Williams 1999); stop all'apertura del giorno; uscita a fine giorno UTC | 300 trade, R +0,149, PF 1,36 | 136 trade, R +0,048, PF 1,128, p 0,048 (m = 1) | 325 trade, R +0,031, **PF 1,067**, +9,8%; 2024 +0,159, 2025 −0,041, 2026 −0,046; batte ancora la (b) (t 3,01, p 0,0015); tasso del caso 0,1% | `vault/risultati.md`; `vault/BTCUSDT-V10_vault.md` |
| **BNBUSDT-045** | long a 1h: close sopra la media a 200, RSI(2) sotto 5, solo sabato e domenica UTC; uscita sopra la media a 5 o dopo 12 barre; stop 2,5 ATR. Quinto ritocco | 74 trade, R +0,138, PF 2,76 | 32 trade, R +0,047, PF 1,49, p 0,031 | 94 trade, **R −0,087**, PF 0,55, −9,1%; negativo in tutti e tre gli anni; come le entrate casuali (percentile 40); tasso del caso 0,4% | stessi file |
| **ADAUSDT-037** | long a 15m sopra il massimo delle 4 barre 00:00-00:45 UTC, fra le 01:15 e le 19:45; filtri: sopra la media di 20 giorni e BTC in calo nelle 24 ore prima; stop al minimo dell'intervallo; uscita a mezzanotte. Quarto ritocco | 178 trade, R +0,252 | 82 trade, R +0,624 (+0,014 senza i 3 migliori), PF 2,15, p 0,014 | 167 trade, **R −0,164**, PF 0,79, −26,3%, 113 uscite allo stop; tasso del caso 1,5% | stessi file; `campagne/ADAUSDT/consegna.md` |
| XRPUSDT-V21r3 | long a 1h quando il perpetuo è sotto il mark (premio sotto −0,20%). Terzo ritocco | 97 trade, R +0,167 | 5 trade: «non si sa» | — | `campagne/XRPUSDT/consegna.md` |
| FILUSDT-025 | come BTC-V10, su FIL (Williams, 1h long) | 177 trade, R +0,084 | 87 trade, R −0,117, p 0,085: **fallito** per decisione del proprietario | — | `campagne/FILUSDT/consegna.md` |
| DYDXUSDT-008 | long a 1h su DYDX rimasta indietro dopo un'ora forte di BTC (Lo-MacKinlay 1990) | R +0,060 | 83 trade, R −0,178, p 0,968 | — | `campagne/DYDXUSDT/consegna.md` |
| MASKUSDT-029 | short a 1h dopo un'impennata oraria estrema, con filtro del funding. Secondo ritocco | R +0,264 | 41 trade, R +0,011, p 0,293 | — | `campagne/MASKUSDT/consegna.md` |

Passaggi attesi per puro caso sui tre del vault: 0,001 + 0,004 + 0,015 = circa 0,02; probabilità di vedere 0 passaggi
senza alcun vantaggio circa 98% (`confronto/risultati.md`, Punto 1). Il riepilogo del Passo 4 aveva notato, come
indizio: 3 candidati valutabili su 6 sotto la soglia in validazione, contro 0,2-0,6 attesi per caso
(`passo4/riepilogo.md`, «Altri controlli»). Il vault ha chiuso la questione.

**Le riserve erano scritte prima.** BTC: «piccolo e fragile», previsione «circa 40% di passare il vault, profit factor
1,00-1,20» (è venuto 1,067). BNB: il filtro del fine settimana era «il migliore di 7 gruppi per giorno visti sugli
stessi dati», previsione 25-35%. ADA: «più probabilmente fallisce, con R medio vicino a zero o negativo»
(`confronto/risultati.md` §4.1, dalle consegne).

**Il vault in pratica** (`vault/APERTURA.md`): lanciatori committati prima (92946ab2), impronte SHA-256 dei file di ogni
candidato, semi 0-999, serie calda dall'inizio della campagna e trade contati dal 2024-01-01, regola dei dati che
ferma il giro senza consumare il vault se mancano file. Un giorno di mark mancante nel giugno 2026 (96,7% delle barre
allineate in quel mese, solo avviso). Prima di aprire, i lanciatori hanno rifatto la validazione a vault chiuso:
identica per BNB, uguale a meno dell'ultima cifra del p-value per BTC e ADA (diario r. 3525).

**Dopo il vault.** Il Passo 6 (trasferimento sulle altre monete) e il Passo 5 punto 2 (dati del vault delle altre 17
monete) non sono stati fatti, per decisione del proprietario del 12 ottobre (`vault/risultati.md`, ultima sezione).
Non esiste quindi nessun numero fuori campione per le altre 17 monete.

---

## 3. Tutte le idee provate, per famiglia

**Come è fatta questa sezione.**

* Le famiglie sono le 20 etichette del coordinamento (`confronto/risultati.md` §1, prima tabella). I numeri di
  famiglia in grassetto (campagne, varianti, nette, t massimo) sono quelli di `confronto/risultati.md` §3.1-3.2.
* Gli elenchi sotto ogni famiglia sono **un mio conteggio dai log**: per ogni idea (titolo da `ipotesi.md` della
  campagna) la variante con il t più alto contro la (b) in costruzione, con timeframe, direzione (L/S), R medio dopo i
  costi, trade, numero di varianti, ritocchi e scarti dell'idea. Per ETHUSDT e SOLUSDT valgono i numeri ricalcolati
  dopo la correzione del funding dell'8 ottobre (voci «correzione» dei log).
* L'assegnazione di un'idea a una famiglia l'ho fatta dal titolo, allineandola a quella del coordinamento. I miei
  totali coincidono con quelli del coordinamento per 16 famiglie su 20; differiscono di 2-6 varianti per volume,
  continuazione, candele e distribuzione (casi di confine, per esempio LTCUSDT I-11 «continuazione dopo movimenti con
  volume alto» che ho messo in volume). Il coordinamento lo scrive da sé: «un'altra assegnazione cambierebbe i conteggi
  di qualche unità, non il quadro» (`confronto/risultati.md` §6).
* «Solo scarti» = l'idea non è mai stata provata perché tutte le sue varianti stavano sotto i 70 trade (700 per il
  gruppo); fra parentesi le stime di `conta_trade`.
* Una «migliore» non è un risultato: con 630 prove alcune escono sopra 2 anche senza alcun vantaggio (stima: circa 14
  con il 2,3% nominale della soglia, circa 3 con lo 0,41% misurato dalla prova a placebo; sezione 4.4).

Distribuzione dei t di tutte le varianti delle 20 monete (`confronto/risultati.md` §0): media 0,46, deviazione 1,30,
71 sopra 2 e 18 sotto −2. Mio conteggio dai log, dopo le correzioni: 600 varianti, media 0,43, deviazione 1,30, 69
sopra 2, 18 sotto −2, 65 nette contro la (b). La differenza è piccola e non ne conosco la causa.

### 3.A Tendenza

**Momento (tendenza di più giorni).** Il rendimento dell'ultima settimana (o di 1-4 settimane) continua. Fonti:
Moskowitz, Ooi, Pedersen, «Time series momentum», 2012; Liu, Tsyvinski, «Risks and Returns of Cryptocurrency», 2018.
**21 campagne, 52 varianti, 2 nette contro la (b), t massimo 2,22 (FTMUSDT-036, 1d short, ritocco, non netta contro la
(a)); nessun candidato.** R medi alti sui long (ETC 001 +0,42; MATIC I-01 +0,43; GALA 001 +0,98, tutto in 3 trade), ma uguali
alla (b) long: è il rialzo del 2020-21, scritto da 9 campagne (`confronto/risultati.md` §3.1).

* FTM I-01 «Momento della serie temporale (settimane)»: migliore 036 1d S, t 2,22, R +0,033, 109 trade (6 var.; 4 rit.)
* AVAX I-01 «Momentum di serie temporale a 1 giorno»: migliore V02 1d S, t 2,12, R +0,046, 108 trade (2 var.)
* ETC I-01 «Momento della serie storica a una settimana»: migliore 002 4h S, t 1,75, R +0,268, 115 trade (4 var.; 2 rit.)
* BCH I-01 «Momento della serie a una settimana (1d)»: migliore 002 1d S, t 1,62, R +0,109, 93 trade (6 var.; 4 rit.; 1 scarto)
* DOGE I-01 «Momento della serie storica a una settimana»: migliore 002 1d S, t 1,01, R +0,000, 120 trade (2 var.)
* MATIC I-01 «Momento di serie temporale settimanale»: migliore 001 4h L, t 0,73, R +0,427, 150 trade (2 var.)
* 1000SHIB I-01 «Momento della serie (time-series momentum)»: migliore 001 4h L, t 0,67, R +0,221, 171 trade (2 var.)
* GALA I-01 «Momentum di serie temporale»: migliore 002 4h S, t 0,64, R +0,286, 107 trade (2 var.)
* ADA I-01 «Momentum a serie temporale (una settimana)»: migliore 002 4h S, t 0,62, R +0,052, 109 trade (2 var.)
* SOL I-01 «Momentum della serie (time-series momentum)»: migliore 001 1d L, t 0,56, R +0,187, 71 trade (2 var.)
* BNB I-01 «Momentum a serie temporale settimanale»: migliore 002 1d S, t 0,55, R −0,081, 80 trade (2 var.)
* BTC I-01 «Momentum a serie storica (rendimento dell'ultima settimana)»: migliore V02 1d S, t 0,49, R +0,023, 100 trade (2 var.)
* ETH I-01 «Momentum sul prezzo della settimana passata (time-series momentum)»: migliore 001 1d L, t 0,48, R +0,244, 123 trade (2 var.)
* LINK I-01 «Momentum nel tempo a una settimana»: migliore V01 1d L, t 0,46, R +0,079, 90 trade (2 var.)
* FIL I-01 «Momento della serie storica (time-series momentum)»: migliore 001 4h L, t 0,41, R +0,136, 105 trade (2 var.)
* GRUPPO I-01 «Momento a serie storica»: migliore 015 1d L, t 0,39, R +0,036, 3756 trade (2 var.)
* LTC I-01 «Momentum di serie temporale settimanale»: migliore 001 1d L, t 0,39, R +0,069, 118 trade (2 var.)
* XRP I-01 «Momentum a una settimana»: migliore V01 1d L, t 0,34, R +0,091, 125 trade (2 var.)
* DYDX I-01 «Momento della serie su candele giornaliere»: migliore 001 1d L, t 0,19, R −0,002, 81 trade (2 var.)
* MASK I-01 «Momento nel tempo (il rendimento dell'ultima settimana continua)»: migliore 002 4h S, t −0,00, R −0,004, 151 trade (2 var.)
* TRB I-01 «Momentum della serie (time-series momentum)»: migliore I-01-S 4h S, t −0,36, R −0,250, 112 trade (2 var.)

**Rottura del canale.** Il prezzo che esce dal massimo o dal minimo di N barre continua (le «tartarughe»: Faith 2007;
Brock, Lakonishok, LeBaron 1992). **18 campagne, 33 varianti, 0 nette, t massimo 1,26 (MASKUSDT-004, 1h short).** R
medi alti sui long (BTC V03 +0,44 contro +0,27 della (b); BNB I-02 +0,81 con «3 trade del 2021 che fanno tutto»); in
almeno 8 campagne la versione a 4h non arriva a 70 trade (stessa fonte).

* MASK I-02 «Rottura del canale (il prezzo che esce dal massimo recente continua)»: migliore 004 1h S, t 1,26, R +0,127, 140 trade (2 var.)
* LTC I-02 «Breakout di canale (sistema delle «tartarughe»)»: migliore 003 4h L, t 1,07, R +0,171, 85 trade (2 var.)
* BTC I-02 «Rottura del canale di 20 barre (sistema 1 delle «tartarughe»)»: migliore V04 4h S, t 1,00, R +0,173, 75 trade (2 var.)
* XRP I-07 «Uscita dal canale (rottura del massimo di 20 barre)»: migliore V12 4h L, t 0,97, R +0,417, 96 trade (2 var.)
* FTM I-02 «Rottura del canale di Donchian»: migliore 026 2h L, t 0,87, R +0,249, 134 trade (2 var.; 2 scarti)
* SOL I-02 «Rottura del canale (sistema delle tartarughe)»: migliore 003 4h L, t 0,84, R +0,329, 70 trade (2 var.; 1 scarto)
* GRUPPO I-02 «Rottura dell'intervallo di prezzo»: migliore 017 1d L, t 0,71, R +0,110, 871 trade (2 var.)
* AVAX I-02 «Rottura del canale di Donchian a 4 ore»: migliore V23 4h S, t 0,69, R +0,109, 109 trade (2 var.; 2 scarti)
* ETH I-02 «Rottura del canale di Donchian (le regole delle "tartarughe")»: migliore 004 4h S, t 0,69, R −0,046, 81 trade (2 var.)
* DYDX I-02 «Rottura del massimo o del minimo di 50 barre»: migliore 015 1h L, t 0,57, R −0,007, 167 trade (2 var.; 2 scarti)
* ADA I-02 «Rottura del canale di prezzo (regole delle «tartarughe»)»: migliore 004 4h S, t 0,54, R +0,045, 72 trade (2 var.)
* GALA I-02 «Rottura del canale di Donchian (le tartarughe)»: migliore 025 2h L, t 0,49, R +0,775, 89 trade (2 var.; 2 scarti)
* BNB I-02 «Rottura del canale di Donchian»: migliore 004 4h S, t 0,45, R −0,035, 71 trade (2 var.)
* 1000SHIB I-03 «Rottura del canale (Donchian)»: migliore 015 2h L, t 0,36, R +0,547, 102 trade (2 var.; 2 scarti)
* DOGE I-03 «Rottura del canale di prezzo»: migliore 033 4h S, t 0,20, R +0,033, 86 trade (1 var.; 3 scarti)
* BCH I-02 «Rottura del canale dei massimi e minimi (4h)»: migliore 003 4h L, t 0,19, R +0,031, 86 trade (2 var.)
* LINK I-02 «Rottura del massimo (minimo) delle ultime 50 barre»: migliore V03 4h L, t −0,72, R −0,079, 95 trade (1 var.; 1 scarto)
* TRB I-02 «Rottura del canale di prezzo (trading range break)»: migliore I-02-L2 4h L, t −1,46, R −0,175, 72 trade (1 var.; 3 scarti)
* MATIC I-02 «Rottura del canale di 20 giorni (Donchian, «Turtle»)»: solo scarti, mai testata (trade stimati 19, 11, 52, 47)
* FIL I-02 «Rottura del canale dei prezzi (trading range break)»: solo scarti, mai testata (trade stimati 52, 49, 64, 59)
* ETC I-02 «Rottura del canale di prezzo»: solo scarti, mai testata (trade stimati 43, 40)

**Media mobile.** Il prezzo che incrocia una media, o un trend forte misurato con l'ADX (Brock e altri 1992; Detzel e
altri 2018; Wilder 1978). **11 campagne, 20 varianti, 0 nette, t massimo 1,57 (ETCUSDT-025, 4h short)**: «come il caso
nella stessa direzione».

* ETC I-13 «Incrocio di medie mobili»: migliore 025 4h S, t 1,57, R +0,157, 98 trade (2 var.)
* FTM I-13 «Incrocio di medie mobili»: migliore 032 2h L, t 1,12, R +0,515, 115 trade (2 var.; 2 scarti)
* BCH I-13 «Il prezzo sopra la media mobile (1d)»: migliore 031 1d S, t 0,69, R +0,052, 79 trade (2 var.; 2 scarti)
* LTC I-13 «Incrocio con la media mobile e tenuta fissa»: migliore 025 4h S, t 0,35, R −0,030, 149 trade (2 var.)
* SOL I-03 «Incrocio con la media mobile (regola a tenuta fissa)»: migliore 005b 2h L, t 0,30, R +0,343, 81 trade (1 var.; 1 scarto)
* BNB I-10 «Incrocio della media mobile a 50»: migliore 018 4h S, t 0,26, R −0,019, 178 trade (2 var.)
* 1000SHIB I-14 «Incrocio con la media mobile»: migliore 023 4h L, t 0,11, R +0,003, 96 trade (2 var.)
* FIL I-16 «Incrocio del prezzo con la media mobile»: migliore 030 4h L, t 0,05, R +0,254, 143 trade (2 var.)
* BTC I-16 «Prezzo che supera la media mobile di 50 periodi»: migliore V29 4h L, t −0,06, R +0,355, 97 trade (1 var.)
* MATIC I-11 «Prezzo sopra la media mobile lunga (regola a media mobile)»: migliore 015 1h S, t −0,35, R −0,095, 124 trade (2 var.; 2 scarti)
* DOGE I-16 «Incrocio dei movimenti direzionali con trend forte»: migliore 039 1h S, t −0,46, R −0,068, 139 trade (2 var.; 2 scarti)
* ETH I-03 «Prezzo sopra o sotto la media mobile di 50 giorni»: solo scarti, mai testata (trade stimati 34, 47)
* BNB I-15 «Forza della tendenza con l'ADX»: solo scarti, mai testata (trade stimati 46, 46, 46, 53)
* ADA I-03 «Prezzo sopra la media mobile (apprendimento sui fondamentali diffic…»: solo scarti, mai testata (trade stimati 46)

**Cosa ne è stato.** Nessun candidato in nessuna moneta né nel gruppo. La lezione comune è «è l'anno, non la regola»:
un R medio alto non dice nulla senza la (b) nella stessa direzione e senza l'R per anno (`confronto/lezioni_comuni.md`
§1.1). La tendenza è stata ripresa dopo, a barre giornaliere e sul paniere di 80 monete, nella seconda edizione
(`PROTOCOLLO_2.md`, tabella della sezione 2: «da 2 giorni a 60 giorni… è l'orizzonte in cui tendenza e momentum sono
documentati»).

### 3.B Ritorno alla media

**RSI a 2 periodi dentro la tendenza.** Un calo di poche ore dentro un trend rimbalza (Connors, Alvarez, «Short Term
Trading Strategies That Work», 2008). **20 campagne, 40 varianti, 3 nette (tutte BNB), 3 candidati di Fase 2 (BNB
043, 044, 045, tutti ritocchi), 1 in validazione e al vault (BNBUSDT-045, bocciato).** A 4h il long è stato provato su
14 monete e non è mai stato netto (`confronto/risultati.md` §2.2).

* BNB I-03 «RSI a 2 periodi in tendenza rialzista»: migliore 045 1h L, t 3,96, R +0,138, 74 trade (6 var.; 5 rit.; 1 scarto) — **candidato di Fase 2: 043, 044, 045**
* XRP I-08 «RSI a 2 periodi: rientro dentro il trend»: migliore V15 4h S, t 1,61, R +0,042, 161 trade (2 var.)
* LTC I-03 «Ritorno verso la media dopo eccessi di breve (RSI a 2 periodi)»: migliore 006 4h S, t 1,34, R +0,016, 150 trade (2 var.)
* ETH I-04 «RSI a 2 barre: eccesso di breve contro il trend lungo»: migliore 008 4h S, t 1,25, R −0,002, 130 trade (2 var.)
* FTM I-07 «Ritorno di breve dentro il trend (RSI a 2)»: migliore 012 4h L, t 1,11, R +0,029, 86 trade (2 var.)
* MASK I-04 «Ritracciamento a 2 periodi dentro il trend»: migliore 007 1h L, t 1,02, R −0,009, 261 trade (2 var.)
* FIL I-05 «Ritracciamento a breve dentro il trend (RSI a 2 periodi)»: migliore 012 4h S, t 0,94, R +0,045, 176 trade (1 var.; 1 scarto)
* DOGE I-05 «Ritorno dopo l'ipervenduto in un trend (RSI a 2 barre)»: migliore 010 4h S, t 0,91, R +0,007, 101 trade (2 var.)
* AVAX I-03 «Ritorno verso la media con RSI a 2 periodi, a 4 ore»: migliore V06 4h S, t 0,87, R +0,020, 107 trade (2 var.)
* BTC I-04 «RSI a 2 periodi in un trend positivo (ritorno alla media di breve)»: migliore V08 4h S, t 0,82, R +0,003, 120 trade (2 var.)
* BCH I-03 «RSI a 2 periodi nel verso della media lunga (4h)»: migliore 006 4h S, t 0,74, R +0,008, 158 trade (2 var.)
* TRB I-08 «Ritorno di brevissimo periodo nel verso del trend (RSI a 2 barre)»: migliore I-08-S 4h S, t 0,73, R +0,002, 90 trade (2 var.)
* 1000SHIB I-11 «Ritorno alla media in tendenza (RSI a 2)»: migliore 011 4h L, t 0,64, R +0,012, 76 trade (2 var.)
* MATIC I-05 «Ritorno verso la media dopo un ribasso brusco dentro il trend (RSI…»: migliore 012 4h L, t 0,60, R +0,024, 120 trade (2 var.; 2 scarti)
* SOL I-04 «RSI a 2 periodi sopra la media di 200 (Connors)»: migliore 007b 4h S, t 0,60, R +0,017, 101 trade (2 var.; 2 scarti)
* DYDX I-03 «Ipervenduto a 2 barre dentro il trend (ritorno verso la media)»: migliore 004 1h S, t 0,25, R −0,017, 350 trade (2 var.)
* LINK I-10 «Ritracciamento in un trend: RSI a 2 periodi»: migliore V18 4h L, t −0,04, R −0,007, 143 trade (1 var.; 1 scarto)
* ETC I-11 «Ipervenduto a due barre dentro il trend (RSI a 2)»: migliore 014 4h L, t −0,11, R −0,020, 107 trade (2 var.)
* GRUPPO I-12 «Ritracciamento breve dentro il trend lungo»: migliore 029 1d S, t −0,82, R −0,072, 1437 trade (1 var.; 1 scarto)
* GALA I-03 «RSI a 2 periodi con filtro di tendenza (ritorno verso la media)»: migliore 006 4h S, t −1,43, R −0,137, 120 trade (1 var.; 1 scarto)
* ADA I-09 «Ritracciamento breve dentro una tendenza (RSI a 2 periodi)»: solo scarti, mai testata (trade stimati 8, 54)

**Inversione di breve.** Dopo un movimento estremo (un'ora, una barra, 24 ore, una «pompa», una falsa rottura) il
prezzo torna indietro (Lehmann 1990; Jegadeesh 1990; Nagel 2012; Campbell, Grossman, Wang 1993; Kamps, Kleinberg 2018;
Kozlowski e altri 2021). **21 campagne, 61 varianti, 3 nette, 1 candidato (MASKUSDT-029), arrivato in validazione con
p 0,293.** In 9 campagne l'inversione dopo un'ora o una barra estrema va **peggio del caso** (per esempio LINK V05/V06 t
−2,59 e −3,13; ETH I-13 −2,09; BNB I-12 −2,13): «dopo gli eccessi il prezzo continua» (`confronto/risultati.md` §3.1).

* MASK I-03 «Ritorno dopo una barra estrema (eccesso di reazione a breve)»: migliore 029 1h S, t 2,85, R +0,264, 86 trade (7 var.; 5 rit.) — **candidato di Fase 2: 029**
* LINK I-14 «Inversione giornaliera»: migliore V24 1d L, t 2,23, R +0,042, 324 trade (5 var.; 3 rit.)
* BTC I-15 «La «molla» e la «spinta» (falsa rottura)»: migliore V28 4h S, t 1,84, R +0,002, 331 trade (3 var.; 1 rit.; 1 scarto)
* GALA I-04 «Falsa rottura: la spazzata degli stop e il rientro»: migliore 007 1h L, t 0,84, R −0,135, 251 trade (2 var.)
* ETC I-03 «Inversione dopo uno shock di un'ora (fornitura di liquidità)»: migliore 016 1h L, t 0,68, R −0,002, 174 trade (2 var.)
* TRB I-03 «Reazione eccessiva di breve periodo e ritorno»: migliore I-03-S 1h S, t 0,55, R −0,006, 100 trade (2 var.)
* DYDX I-05 «Ritorno dopo un movimento forte con volume alto (liquidità forzata)»: migliore 017 1h L, t 0,38, R −0,013, 143 trade (2 var.; 2 scarti)
* LTC I-04 «Inversione dopo shock di prezzo con volume alto»: migliore 007 1h L, t 0,33, R −0,021, 233 trade (2 var.)
* FIL I-04 «Inversione delle barre estreme con volume alto (domanda di liquidità)»: migliore 009 1h L, t −0,02, R −0,063, 89 trade (2 var.)
* DOGE I-11 «Inversione dopo una barra estrema (fornitura di liquidità)»: migliore 020 1h L, t −0,10, R −0,064, 153 trade (2 var.)
* FIL I-03 «Inversione a breve dopo i movimenti estremi»: migliore 005 1h L, t −0,18, R −0,049, 74 trade (2 var.)
* TRB I-04 «Gonfiamenti coordinati del prezzo e successivo sgonfiamento (pump a…»: migliore I-04-A 1h S, t −0,35, R −0,157, 90 trade (2 var.)
* MASK I-07 «Dopo il pump, lo scarico»: migliore 012b 1h S, t −0,38, R −0,066, 87 trade (1 var.; 1 scarto)
* SOL I-05 «Inversione dopo un movimento estremo (fornitura di liquidità)»: migliore 008 1h L, t −0,48, R −0,078, 127 trade (2 var.)
* AVAX I-13 «Inversione dopo un salto orario estremo»: migliore V27 1h L, t −0,48, R −0,072, 125 trade (2 var.)
* BCH I-09 «Inversione dei movimenti grandi con volume alto (4h)»: migliore 016 4h S, t −0,60, R −0,053, 91 trade (2 var.)
* XRP I-02 «Rimbalzo dopo un movimento orario estremo con volume alto»: migliore V04 1h S, t −0,64, R −0,111, 289 trade (2 var.)
* BTC I-03 «Reazione eccessiva: barre anomale»: migliore V06 4h L, t −0,79, R −0,073, 139 trade (2 var.)
* SOL I-06 «Inversione dei movimenti con volume alto»: migliore 010b 4h L, t −0,83, R −0,079, 86 trade (1 var.; 1 scarto)
* 1000SHIB I-06 «Gonfia e sgonfia (pump-and-dump)»: migliore 019 15m S, t −0,91, R −0,174, 109 trade (1 var.; 1 scarto)
* GRUPPO I-04 «Inversione dopo un movimento forzato con volume anomalo»: migliore 020 1d S, t −0,96, R −0,055, 877 trade (1 var.; 1 scarto)
* FTM I-03 «Ritorno dopo un movimento estremo (offerta di liquidità)»: migliore 005 1h L, t −1,02, R −0,119, 82 trade (2 var.)
* ADA I-15 «Inversione di breve periodo come compenso per chi fornisce liquidità»: migliore 029 4h S, t −1,10, R −0,091, 82 trade (1 var.; 1 scarto)
* 1000SHIB I-02 «Ipereazione a breve e inversione»: migliore 003 1h L, t −1,41, R −0,143, 123 trade (2 var.)
* MATIC I-09 «Ritorno dopo un salto orario (eccesso di reazione)»: migliore 010 1h L, t −1,62, R −0,172, 121 trade (2 var.)
* FTM I-14 «Movimenti con volume alto che tornano indietro»: migliore 034 4h L, t −2,08, R −0,126, 159 trade (1 var.; 1 scarto)
* ETH I-13 «Vendite forzate: la spirale di liquidita' e il rimbalzo»: migliore 024 1h L, t −2,09, R −0,366, 136 trade (2 var.)
* BNB I-12 «Rimbalzo dopo una caduta forzata»: migliore 028 1h L, t −2,13, R −0,178, 176 trade (1 var.; 1 scarto)
* LINK I-03 «Inversione dopo un movimento orario estremo (offerta di liquidità)»: migliore V05 1h L, t −2,59, R −0,192, 178 trade (2 var.)
* GALA I-13 «Pompa e scarico»: migliore 024 1h S, t −2,75, R −0,307, 88 trade (1 var.)

**Cosa ne è stato.** Il ritorno alla media di poche ore è fra le idee che «falliscono ovunque, e che vale la pena non
riprovare così come sono» (`confronto/lezioni_comuni.md` §4). L'unica arrivata al vault (BNB-045) aveva il rimbalzo
«nella prima ora» e un filtro del fine settimana scelto sui dati; nel vault ha fatto come le entrate casuali
(`confronto/lezioni_comuni.md` §1.8). L'osservazione utile è l'opposto: dopo un'ora estrema il prezzo **continua**
(osservato su 14 monete, ma non sfruttabile dopo i costi; diario r. 3569).

### 3.C Rotture legate all'apertura del giorno o a una compressione

**Rottura di volatilità dall'apertura del giorno (Williams).** Si entra quando il prezzo supera l'apertura del giorno
più una frazione del range di ieri (Williams, «Long-Term Secrets to Short-Term Trading», 1999). **9 campagne, 19
varianti (tutte a 1h), 3 nette, 3 candidati (BTC V10 e V11, FIL 025), 2 in validazione, 1 al vault (BTC-V10,
bocciato per PF 1,067).** Il segno dell'R long è positivo su 7 monete su 8, mai netto fuori da BTC e FIL. Tre campagne
hanno scritto la stessa cosa: **lo stop all'apertura del giorno rende le baseline molto negative**; con uno stop a
distanza normale il t scende (FIL da 2,34 a 1,38; BTC V11 da 3,01 a 1,01; BTC V10 resta netta con lo stop fisso al
2%, t 3,10) (`confronto/risultati.md` §2.1).

* BTC I-06 «Rottura di volatilita' dall'apertura del giorno (Larry Williams)»: migliore V11 1h S, t 3,01, R +0,056, 304 trade (2 var.) — **candidato di Fase 2: V10, V11**
* FIL I-13 «Rottura di volatilità dall'apertura del giorno»: migliore 025 1h L, t 2,34, R +0,084, 177 trade (2 var.) — **candidato di Fase 2: 025**
* AVAX I-09 «Rottura della volatilità del giorno (Williams, Crabel), a 1 ora»: migliore V17 1h S, t 1,72, R +0,021, 231 trade (2 var.)
* ETH I-17 «Rottura di volatilita' dall'apertura del giorno»: migliore 033 1h S, t 1,66, R +0,020, 306 trade (2 var.)
* LINK I-09 «Rottura di volatilità dall'apertura del giorno»: migliore V16 1h S, t 1,62, R +0,074, 309 trade (2 var.)
* BCH I-04 «Rottura di volatilità dall'apertura del giorno (1h)»: migliore 008 1h S, t 1,53, R +0,044, 327 trade (3 var.; 1 rit.)
* GALA I-09 «Rottura di volatilità dall'apertura del giorno»: migliore 017 1h L, t 1,29, R +0,144, 181 trade (2 var.)
* FTM I-06 «Rottura di volatilità della giornata (Williams)»: migliore 010 1h L, t 0,96, R +0,028, 227 trade (2 var.)
* DOGE I-04 «Rottura di volatilità dall'apertura del giorno»: migliore 007 1h L, t 0,67, R +0,030, 201 trade (2 var.)

**Rottura dell'intervallo d'apertura.** Si entra sopra il massimo delle prime barre del giorno UTC (Crabel, «Day
Trading with Short Term Price Patterns and Opening Range Breakout», 1990). **6 campagne, 25 varianti (13 ritocchi), 6
nette (tutte ADA), 4 candidati (tutti ADA), 1 in validazione e al vault (ADAUSDT-037, bocciato).** Dentro ADA era
netta «per lo stop, non per la direzione» (nota N011 della campagna); su LTC la stessa regola con lo stop fisso al 3%
passa da t 1,95 a 0,01 (`confronto/risultati.md` §2.3).

* ADA I-13 «Rottura dell'intervallo d'apertura della giornata»: migliore 038 15m L, t 6,57, R −0,067, 1826 trade (7 var.; 5 rit.) — **candidato di Fase 2: 025, 034, 035, 037**
* LTC I-07 «Breakout del range d'apertura della giornata»: migliore 014 1h S, t 1,95, R −0,068, 554 trade (7 var.; 5 rit.)
* TRB I-13 «Rottura del range della prima ora (opening range breakout)»: migliore I-13-S 15m S, t 1,37, R −0,129, 474 trade (5 var.; 3 rit.)
* MASK I-11 «Rottura dell'intervallo d'apertura della giornata UTC»: migliore 020 1h S, t 0,96, R +0,067, 233 trade (2 var.)
* ETC I-16 «Rottura dell'intervallo di apertura della giornata»: migliore 029 1h L, t 0,85, R +0,007, 494 trade (2 var.)
* XRP I-15 «Rottura dell'intervallo di apertura della giornata UTC»: migliore V29 1h S, t 0,37, R −0,036, 658 trade (2 var.)

**Barra più stretta (NR7) e rottura** (Crabel 1990). **6 campagne, 18 varianti, 1 netta, t massimo 2,32 (SOLUSDT-032,
4h short, ritocco, non netta contro la (a)); 7 ritocchi senza candidato.**

* SOL I-07 «Compressione della volatilità e rottura (NR7)»: migliore 032 4h S, t 2,32, R +0,268, 125 trade (5 var.; 3 rit.; 2 scarti)
* GALA I-07 «Barra stretta (NR7) e rottura»: migliore 014 4h S, t 1,80, R +0,074, 137 trade (2 var.)
* DYDX I-10 «Barra stretta e rottura»: migliore 024 4h S, t 1,42, R +0,313, 83 trade (6 var.; 4 rit.; 1 scarto)
* DOGE I-15 «Giorno stretto e rottura del giorno dopo»: migliore 029 1h S, t 1,17, R +0,172, 91 trade (2 var.)
* BTC I-14 «Il giorno piu' stretto di sette (NR7)»: migliore V25 1h L, t 1,11, R +0,207, 74 trade (1 var.; 1 scarto)
* ETH I-05 «Barra piu' stretta delle ultime 7 (contrazione della volatilita')»: migliore 009 4h L, t 0,83, R +0,152, 246 trade (2 var.)

**Compressione delle bande di Bollinger e rottura** (Bollinger, «Bollinger on Bollinger Bands», 2001). **10 campagne
con varianti, 24 varianti, 1 netta, 1 candidato (DOGEUSDT-042, terzo ritocco), caduto in Fase 4: robustezza netta in 6
casi su 14 e costi doppi (t 2,013 contro 2,040)**: «un picco, non un'area stabile». In 7 campagne non è mai arrivata a
70 trade.

* DOGE I-10 «Strettoia delle bande di Bollinger»: migliore 042 1h S, t 2,14, R +0,158, 130 trade (7 var.; 5 rit.; 2 scarti) — **candidato di Fase 2: 042**
* LTC I-09 «Compressione della volatilità e breakout (lo «squeeze» delle bande…»: migliore 016c 2h L, t 1,36, R −0,201, 138 trade (2 var.; 4 scarti)
* TRB I-07 «Compressione della volatilità e rottura (squeeze)»: migliore I-07-L2 1h L, t 1,31, R +0,079, 152 trade (2 var.; 2 scarti)
* 1000SHIB I-10 «Compressione della volatilità e rottura delle bande»: migliore 020 1h S, t 1,27, R +0,214, 78 trade (1 var.; 3 scarti)
* MASK I-09 «Compressione delle bande e rottura»: migliore 016 1h S, t 0,77, R +0,059, 158 trade (2 var.)
* LINK I-17 «Compressione della volatilità e rottura (la «stretta» delle bande)»: migliore V31 1h S, t 0,71, R +0,042, 93 trade (2 var.)
* BNB I-06 «Compressione delle bande di Bollinger»: migliore 025 1h L, t 0,65, R +0,155, 91 trade (2 var.; 2 scarti)
* BCH I-12 «Compressione delle bande di Bollinger e rottura (4h)»: migliore 029 1h S, t 0,63, R +0,033, 105 trade (2 var.; 2 scarti)
* AVAX I-10 «Rottura dopo la compressione delle bande di Bollinger, a 4 ore»: migliore V32 1h S, t 0,50, R +0,020, 239 trade (2 var.; 4 scarti)
* FTM I-09 «Compressione di volatilità e rottura (Bollinger)»: migliore 029 2h S, t −0,06, R −0,022, 94 trade (2 var.; 2 scarti)
* BTC I-07 «Rottura dopo una compressione delle bande di Bollinger»: solo scarti, mai testata (trade stimati 26, 28)
* XRP I-09 «Compressione della volatilità e rottura delle bande»: solo scarti, mai testata (trade stimati 28, 26, 65, 63)
* MATIC I-12 «Compressione della volatilità e rottura (Bollinger)»: solo scarti, mai testata (trade stimati 2, 6, 18, 25)
* ADA I-08 «Compressione della volatilità e poi espansione (Bollinger)»: solo scarti, mai testata (trade stimati 15, 21, 24, 30)
* FIL I-09 «Compressione della volatilità seguita da rottura (Bollinger squeeze)»: solo scarti, mai testata (trade stimati 59, 52)
* ETC I-10 «Compressione della volatilità, poi rottura (bande di Bollinger)»: solo scarti, mai testata (trade stimati 15, 17)
* GRUPPO I-06 «Rottura dopo una compressione della volatilità»: solo scarti, mai testata (trade stimati 126, 143)

**Vicinanza al massimo dell'anno** (ancoraggio). Mai provata: 4 campagne, tutte sotto il minimo di trade.

* BTC I-13 «Vicino al massimo di un anno (ancoraggio)»: solo scarti, mai testata (trade stimati 12)
* MATIC I-10 «Vicinanza al massimo di 52 settimane»: solo scarti, mai testata (trade stimati 2)
* LINK I-12 «Vicinanza al massimo dell'anno»: solo scarti, mai testata (trade stimati 4)
* GRUPPO I-10 «Vicinanza al massimo dell'ultimo anno»: solo scarti, mai testata (trade stimati 46)

**Cosa ne è stato.** Sono le famiglie che hanno dato due dei tre candidati del vault, ed è qui che è nata la lezione
più ripetuta della ricerca, lo **stop agganciato a un livello di prezzo** (sezione 5 e 7). Il protocollo 3 (16 ottobre)
ha poi reso obbligatorie entrate casuali «con la stessa distribuzione di larghezza dello stop del candidato»
(`PROTOCOLLO_3.md`, appendice 3, correzione 1; `CHANGELOG.md`, riga del 2026-10-17).

### 3.D Orari e calendario

**L'ultima mezz'ora (momento dentro la giornata).** Il rendimento della prima mezz'ora, o della giornata fino alle
23:30 UTC, predice l'ultima mezz'ora (Gao, Han, Li, Zhou, «Market intraday momentum», 2018; Shen, Urquhart, Wang,
«Bitcoin intraday time series momentum», 2022; Wen, Bouri, Xu, Zhao, 2022). **18 campagne, 69 varianti (33 ritocchi),
34 nette contro la (b), 25 candidati di Fase 2 (BTC 3, SOL 4, AVAX 4, ADA 2, FIL 7, 1000SHIB 2, ETC 3), 0 in
validazione.** È la famiglia più produttiva e quella che si è fermata tutta in Fase 4: costi doppi o ritardo di una
barra. L'effetto lordo esiste (BTC +0,045 R, SOL +0,04, AVAX +0,065, SHIB +0,08, ETC +0,045 a trade) ma è «più piccolo o
uguale ai costi di un giro (0,05-0,14 R)»; ETC lo misura anche su BTC («è del mercato, non di ETC»)
(`confronto/risultati.md` §3.2).

* ETC I-12 «Momento dentro la giornata: l'ultima mezz'ora segue il resto del gi…»: migliore 035 30m S, t 3,85, R −0,009, 215 trade (7 var.; 5 rit.) — **candidato di Fase 2: 033, 036, 037**
* BTC I-10 «Momentum di giornata (prima mezz'ora → ultima mezz'ora)»: migliore V35 30m S, t 3,58, R +0,045, 141 trade (6 var.; 4 rit.; 1 scarto) — **candidato di Fase 2: V32, V33, V35**
* AVAX I-06 «Momento infragiornaliero: il rendimento del giorno predice l'ultima…»: migliore V12 30m S, t 3,52, R +0,007, 376 trade (7 var.; 5 rit.) — **candidato di Fase 2: V12, R01, R02, R03**
* ADA I-05 «Momento infragiornaliero: la prima mezz'ora predice l'ultima»: migliore 040 30m S, t 3,41, R +0,057, 94 trade (5 var.; 3 rit.) — **candidato di Fase 2: 039, 040**
* FIL I-15 «Momento dentro il giorno (ultima fascia)»: migliore 035 4h L, t 3,40, R +0,112, 89 trade (10 var.; 8 rit.) — **candidato di Fase 2: 032, 033, 034, 035, 036, 038, 039**
* SOL I-09 «Momentum dentro la giornata (prima mezz'ora → ultima mezz'ora)»: migliore 023 30m S, t 2,78, R +0,017, 193 trade (7 var.; 5 rit.) — **candidato di Fase 2: 023, 024, 026, 027**
* ETH I-06 «La prima mezz'ora del giorno prevede l'ultima»: migliore 012 30m S, t 2,31, R −0,039, 489 trade (2 var.)
* 1000SHIB I-08 «Momento interno al giorno»: migliore 030 30m S, t 2,15, R +0,027, 96 trade (5 var.; 3 rit.; 2 scarti) — **candidato di Fase 2: 028, 030**
* XRP I-13 «Momentum dentro la giornata: la prima mezz'ora guida l'ultima»: migliore V25 30m S, t 1,75, R −0,058, 476 trade (2 var.)
* FTM I-11 «Momento dentro la giornata (prima mezz'ora → ultima mezz'ora)»: migliore 021 30m S, t 1,17, R −0,047, 332 trade (2 var.)
* BNB I-11 «Momento infragiornaliero: prima mezz'ora e ultima mezz'ora»: migliore 019 30m L, t 0,91, R −0,070, 491 trade (2 var.)
* DOGE I-02 «Momento intraday: la prima mezz'ora prevede l'ultima»: migliore 004 30m S, t 0,81, R −0,048, 344 trade (2 var.)
* LINK I-04 «Momentum dentro la giornata: la prima mezz'ora prevede l'ultima»: migliore V08 30m S, t 0,71, R −0,045, 495 trade (2 var.)
* MATIC I-04 «Momento intragiornaliero: la prima mezz'ora prevede l'ultima»: migliore 006 30m S, t 0,71, R −0,046, 329 trade (2 var.)
* MASK I-15 «Momento intraday: la prima mezz'ora predice l'ultima»: migliore 026 30m L, t 0,68, R −0,055, 269 trade (2 var.)
* DYDX I-04 «Momento intragiornaliero: la prima mezz'ora predice l'ultima»: migliore 005 30m L, t 0,68, R −0,041, 311 trade (2 var.)
* GALA I-17 «Momentum dentro la giornata»: migliore 035 30m L, t 0,18, R −0,083, 315 trade (2 var.)
* TRB I-10 «Momentum dentro la giornata (prima mezz'ora → ultima mezz'ora)»: migliore I-10-S 30m S, t −0,46, R −0,110, 316 trade (2 var.)

**Stagionalità (lunedì, cambio di mese, ora che si ripete).** Fonti: Caporale, Plastun 2019; Lakonishok, Smidt 1988;
Heston, Korajczyk, Sadka 2010. **19 campagne, 28 varianti, 1 netta, 1 candidato (FILUSDT-024, fascia oraria a 4h
short), caduto ai costi doppi e al ritardo.** Il lunedì long, provato su 19 campagne, non è mai netto: t fra −1,90 (FIL,
«il contrario della fonte») e 1,13 (BTC).

* FIL I-12 «Stagionalità dell'ora del giorno (rendimenti periodici)»: migliore 024 4h S, t 2,20, R +0,025, 458 trade (2 var.) — **candidato di Fase 2: 024**
* LINK I-16 «Periodicità oraria: la stessa ora dei giorni precedenti»: migliore V28 1h L, t 1,65, R −0,035, 7547 trade (2 var.)
* ETH I-16 «La stessa ora dei giorni passati (periodicita' intragiornaliera)»: migliore 030 1h L, t 1,55, R −0,031, 1000 trade (2 var.)
* GRUPPO I-17 «Cambio di mese»: migliore 030 1d L, t 1,23, R +0,081, 1630 trade (1 var.)
* BTC I-05 «Il lunedi'»: migliore V09 1d L, t 1,13, R +0,063, 143 trade (1 var.)
* XRP I-05 «Effetto del lunedì»: migliore V09 1d L, t 1,11, R +0,098, 140 trade (1 var.)
* DYDX I-07 «Il lunedì»: migliore 007 1d L, t 0,92, R +0,021, 81 trade (1 var.)
* ETH I-09 «Il lunedi'»: migliore 017 1d L, t 0,51, R +0,056, 145 trade (1 var.)
* TRB I-06 «Effetto del lunedì»: migliore I-06-L 1d L, t 0,44, R +0,062, 90 trade (1 var.)
* GALA I-14 «Periodicità oraria dei rendimenti»: migliore 030 1h S, t 0,36, R −0,052, 993 trade (2 var.)
* 1000SHIB I-07 «Effetto del lunedì»: migliore 006 1d L, t 0,01, R +0,002, 93 trade (1 var.)
* LTC I-08 «Effetto del giorno della settimana (lunedì)»: migliore 015 1d L, t −0,04, R −0,031, 143 trade (1 var.)
* SOL I-08 «Effetto del giorno della settimana (lunedì)»: migliore 013 1d L, t −0,08, R −0,001, 106 trade (1 var.)
* BCH I-07 «Il lunedì (1d)»: migliore 013 1d L, t −0,16, R −0,022, 143 trade (1 var.)
* FTM I-05 «Effetto del giorno della settimana (lunedì)»: migliore 009 1d L, t −0,37, R −0,013, 101 trade (1 var.)
* BNB I-04 «Effetto del lunedì»: migliore 007 1d L, t −0,38, R −0,004, 128 trade (1 var.)
* ETC I-08 «Effetto del giorno della settimana (lunedì)»: migliore 011 1d L, t −0,43, R −0,021, 129 trade (1 var.)
* MATIC I-06 «Effetto del giorno della settimana (lunedì)»: migliore 007 1d L, t −0,59, R −0,053, 97 trade (1 var.)
* AVAX I-07 «Effetto del lunedì, a 1 giorno»: migliore V13 1d L, t −0,63, R −0,013, 106 trade (1 var.)
* LINK I-05 «Effetto del giorno della settimana: il lunedì»: migliore V09 1d L, t −1,28, R −0,036, 139 trade (1 var.)
* GALA I-10 «Effetto del giorno della settimana (il lunedì)»: migliore 019 1d L, t −1,28, R −0,177, 79 trade (1 var.)
* DOGE I-09 «Effetto del lunedì»: migliore 017 1d L, t −1,29, R −0,057, 101 trade (1 var.)
* GRUPPO I-08 «Giorno della settimana»: migliore 025 1d L, t −1,37, R −0,024, 7116 trade (1 var.)
* FIL I-07 «Effetto del lunedì»: migliore 015 1d L, t −1,90, R −0,210, 114 trade (1 var.)
* BNB I-13 «Cambio del mese»: solo scarti, mai testata (trade stimati 30)

**Cosa ne è stato.** «Lunedì» va fra le idee da non riprovare (`confronto/lezioni_comuni.md` §1.6 e §4). L'ultima
mezz'ora resta «una domanda per il proprietario, non un risultato»: con costi più bassi (ordini limite, monete più
liquide) «potrebbe essere un'altra storia» (ETC, FIL, BTC; `confronto/lezioni_comuni.md` §4). La prova degli ordini
limite del 13 ottobre l'ha misurata su BTCUSDT-V35, SOLUSDT-023, ETCUSDT-033 e AVAXUSDT-V-12: i costi scendono di un
terzo, non abbastanza (`esperimenti/ordini_limite/risultati.md`, «Nota 1» e sezione 2.1). La seconda edizione è
passata a barre giornaliere proprio per questo (`PROTOCOLLO_2.md` §1, punto 2).

### 3.E Volume e flusso degli ordini

**Volume alto, basso o illiquidità.** Il prezzo sale dopo un volume insolito (visibilità) o paga un premio
all'illiquidità (Gervais, Kaniel, Mingelgrin 2001; Amihud 2002). **10 campagne, 18 varianti, 0 nette, t massimo 1,94
(MATICUSDT-016, 1d long, R +1,02 ma la (a) fa già 0,45)**: pochi trade estremi del 2021.

* MATIC I-08 «Premio del volume alto»: migliore 016 1d L, t 1,94, R +1,024, 70 trade (4 var.; 3 rit.; 3 scarti)
* LTC I-11 «Continuazione dopo movimenti con volume alto (scambi informati)»: migliore 020 1h L, t 1,58, R +0,102, 179 trade (2 var.)
* ADA I-10 «Premio dei volumi alti (visibilità)»: migliore 019 4h L, t 1,40, R +0,268, 78 trade (1 var.; 1 scarto)
* BNB I-16 «Shock di illiquidità»: migliore 032 4h L, t 1,20, R +0,096, 176 trade (1 var.)
* 1000SHIB I-05 «Premio del volume alto»: migliore 018 4h L, t 0,97, R +0,470, 85 trade (1 var.; 1 scarto)
* AVAX I-12 «Premio del volume alto, a 4 ore»: migliore V26 4h L, t 0,96, R +0,062, 143 trade (1 var.; 1 scarto)
* DOGE I-06 «Premio del volume alto (visibilità)»: migliore 012 1d S, t 0,68, R +0,002, 74 trade (1 var.; 1 scarto)
* SOL I-12 «Premio dei giorni di volume alto»: migliore 020b 1d L, t 0,57, R +0,088, 78 trade (1 var.; 1 scarto)
* ETC I-06 «Premio del volume alto»: migliore 009 4h L, t 0,50, R +0,462, 73 trade (2 var.)
* BCH I-08 «Il premio del volume alto (1d)»: migliore 027 1d L, t 0,24, R −0,016, 77 trade (1 var.; 1 scarto)
* BNB I-07 «Premio del volume alto»: migliore 027 1d L, t 0,18, R +0,155, 72 trade (1 var.; 1 scarto)
* MATIC I-15 «Premio per l'illiquidità nel tempo (Amihud)»: migliore 021 4h L, t 0,09, R +0,204, 113 trade (2 var.)
* BTC I-17 «Il premio del volume alto»: migliore V30 4h L, t −0,49, R −0,036, 111 trade (1 var.)
* ETC I-15 «Illiquidità alta, rendimento atteso più alto»: migliore 028 4h L, t −1,07, R +0,053, 90 trade (1 var.)
* ETH I-12 «Volume insolito e visibilita'»: solo scarti, mai testata (trade stimati 65, 42)
* LINK I-07 «Premio dei volumi alti»: solo scarti, mai testata (trade stimati 31)
* TRB I-09 «Premio del volume alto»: solo scarti, mai testata (trade stimati 27, 47)
* TRB I-14 «Premio dell'illiquidità nel tempo»: solo scarti, mai testata (trade stimati 25)
* FIL I-10 «Premio dei giorni con volume molto alto (attenzione)»: solo scarti, mai testata (trade stimati 45)
* FIL I-14 «Shock di illiquidità»: solo scarti, mai testata (trade stimati 47)
* MASK I-06 «Premio del volume alto (attenzione)»: solo scarti, mai testata (trade stimati 21, 60)

**Squilibrio degli ordini aggressivi.** La quota di volume comprato a mercato anticipa il prezzo (Chordia,
Subrahmanyam 2004; Evans, Lyons 2002; Silantyev 2019). **15 campagne, 38 varianti, 5 nette, 1 candidato
(MATICUSDT-025, 1h short), caduto al ritardo (t 0,53) e ai costi doppi.** Il segno cambia da moneta a moneta: su BCH e
FIL dopo acquisti aggressivi il prezzo **scende** (t −1,99; R −0,43) (`confronto/lezioni_comuni.md` §3.5).

* MATIC I-13 «Squilibrio fra acquisti e vendite aggressivi»: migliore 026 1h S, t 2,21, R +0,068, 141 trade (7 var.; 5 rit.) — **candidato di Fase 2: 025**
* DYDX I-11 «Squilibrio degli ordini dei taker»: migliore 028 1d S, t 1,57, R +0,026, 199 trade (6 var.; 5 rit.; 1 scarto)
* BNB I-09 «Squilibrio degli ordini aggressivi»: migliore 015 4h L, t 1,50, R +0,103, 181 trade (2 var.)
* BTC I-09 «Squilibrio degli ordini aggressivi»: migliore V16 4h L, t 1,16, R +0,073, 194 trade (2 var.)
* DOGE I-13 «Squilibrio degli ordini aggressivi»: migliore 025 1d S, t 1,01, R +0,002, 338 trade (1 var.; 1 scarto)
* AVAX I-14 «Squilibrio degli ordini aggressivi (compratori contro venditori), a…»: migliore V30 4h S, t 0,99, R +0,037, 114 trade (2 var.)
* XRP I-10 «Squilibrio fra acquisti e vendite aggressive»: migliore V18 1h L, t 0,95, R −0,028, 249 trade (2 var.)
* 1000SHIB I-12 «Squilibrio fra compratori e venditori aggressivi»: migliore 013 1h L, t 0,53, R +0,083, 170 trade (2 var.)
* MASK I-12 «Squilibrio degli ordini aggressivi»: migliore 021 1h L, t 0,20, R −0,035, 595 trade (2 var.)
* LINK I-08 «Squilibrio degli ordini aggressivi»: migliore V14 1h S, t 0,13, R −0,045, 949 trade (2 var.)
* BCH I-11 «Flusso degli ordini aggressivi (1h)»: migliore 020 1h S, t 0,04, R −0,045, 337 trade (2 var.)
* ETH I-15 «Lo squilibrio degli ordini del giorno prevede il giorno dopo»: migliore 028 1d L, t −0,10, R +0,004, 328 trade (2 var.)
* ETC I-07 «Squilibrio degli ordini aggressivi»: migliore 019 1h S, t −0,29, R −0,073, 901 trade (2 var.)
* ADA I-14 «Squilibrio degli ordini aggressivi»: migliore 026 1h L, t −0,41, R −0,043, 281 trade (2 var.)
* FIL I-11 «Squilibrio degli ordini aggressivi (flusso degli ordini)»: migliore 022 1h S, t −1,10, R −0,098, 96 trade (2 var.)

**Cosa ne è stato.** Niente di ripreso. Le idee di volume lente sono cadute sotto i trade minimi in molte monete
(`confronto/lezioni_comuni.md` §1.10). Un dato tecnico utile: la quota di volume comprato a mercato c'è nei file 2020-2023
ma il motore non la porta (sezione 6).

### 3.F Funding e prezzo del perpetuo

**Funding estremo come affollamento.** Un funding molto alto (o molto basso) segnala posizioni affollate che poi
pagano (Schmeling, Schrimpf, Todorov 2023; He, Manela, Ross, von Wachter, «Fundamentals of Perpetual Futures», 2022).
**19 campagne, 33 varianti, 0 nette, t massimo 1,47 (BTCUSDT-V14, 8h short).** In 5 campagne lo short dopo funding
alto va peggio del caso (BCH −2,05; DOGE −2,67; MATIC −2,27; SOL −2,70; LINK −1,64): «dopo il funding alto il prezzo ha
continuato a salire» (`confronto/risultati.md` §3.1). Su DYDX, TRB, ETC e FTM il funding estremo era troppo raro per 70
trade (`confronto/lezioni_comuni.md` §1.5).

* BTC I-08 «Il funding come misura dell'affollamento»: migliore V14 8h S, t 1,47, R +0,069, 119 trade (2 var.)
* MASK I-05 «Funding estremo contro la folla»: migliore 010 8h L, t 1,38, R +0,128, 83 trade (1 var.; 1 scarto)
* BNB I-05 «Funding estremo come segnale di affollamento»: migliore 009 8h L, t 1,16, R +0,064, 147 trade (2 var.)
* XRP I-04 «Funding estremo: leva affollata da una parte»: migliore V08b 8h L, t 0,92, R +0,146, 78 trade (2 var.; 1 scarto)
* GALA I-05 «Funding estremo: il posizionamento a leva affollato»: migliore 010 8h L, t 0,37, R −0,003, 125 trade (1 var.; 2 scarti)
* BCH I-10 «Funding estremo: la parte affollata paga (8h)»: migliore 018 8h L, t 0,22, R −0,018, 103 trade (2 var.)
* DYDX I-06 «Funding affollato»: migliore 019 8h L, t 0,21, R −0,014, 193 trade (1 var.; 3 scarti)
* ADA I-07 «Funding affollato: chi paga troppo per stare long»: migliore 013 8h L, t 0,01, R −0,006, 99 trade (2 var.)
* LTC I-05 «Affollamento della leva misurato dal funding»: migliore 009 8h S, t −0,02, R −0,081, 102 trade (2 var.)
* FTM I-04 «Funding estremo come segnale di posizioni affollate»: migliore 008 8h L, t −0,12, R −0,010, 81 trade (1 var.; 1 scarto)
* 1000SHIB I-04 «Affollamento misurato dal funding»: migliore 017 4h S, t −0,13, R −0,003, 74 trade (2 var.; 1 scarto)
* AVAX I-04 «Funding estremo come segnale contrario, a 8 ore»: migliore V07 8h S, t −0,15, R −0,035, 108 trade (2 var.)
* FIL I-06 «Funding alto o negativo (carry delle crypto)»: migliore 014 8h L, t −0,19, R −0,020, 76 trade (2 var.)
* MATIC I-07 «Funding estremo: il perpetuo lontano dal suo valore torna indietro»: migliore 009 8h L, t −0,24, R −0,007, 171 trade (2 var.)
* GRUPPO I-05 «Affollamento misurato dal funding»: migliore 021 1d S, t −0,27, R −0,034, 2096 trade (1 var.; 1 scarto)
* LINK I-06 «Funding estremo: posizioni affollate»: migliore V11 8h L, t −0,41, R −0,022, 105 trade (2 var.)
* ETH I-08 «Funding alto: la leva di chi insegue il rialzo»: migliore 015 8h S, t −0,43, R −0,144, 111 trade (2 var.)
* SOL I-10 «Funding alto e affollamento dei long»: migliore 017b 8h L, t −0,54, R −0,039, 99 trade (2 var.; 1 scarto)
* DOGE I-08 «Funding estremo: posizioni a leva affollate»: migliore 016 8h L, t −0,98, R −0,037, 159 trade (2 var.)
* TRB I-05 «Funding affollato (chi è affollato paga e viene liquidato)»: solo scarti, mai testata (trade stimati 36, 28, 53, 46)
* ETC I-05 «Funding affollato»: solo scarti, mai testata (trade stimati 67, 59)

**Premio del perpetuo sul mark price (last/mark).** Lo scarto fra prezzo del perpetuo e mark rientra (He e altri
2022). **6 campagne, 15 varianti, 2 nette, 2 candidati (XRP V21r3 1h long; GALA 032 1h short), 1 in validazione (XRP:
5 trade, «non si sa»).** XRP: 84 trade su 97 nel 2020, poi la condizione quasi non scatta; GALA: cade ai costi doppi
(R −0,043) (`confronto/risultati.md` §3.2).

* XRP I-11 «Premio del perpetuo sul mark price»: migliore V21r3 1h L, t 2,33, R +0,167, 97 trade (5 var.; 3 rit.) — **candidato di Fase 2: V21r3**
* GALA I-15 «Scarto fra prezzo del perpetuo e mark price»: migliore 032 1h S, t 2,22, R +0,013, 325 trade (2 var.) — **candidato di Fase 2: 032**
* LTC I-12 «Scarto fra l'ultimo prezzo e il mark price (premio del perpetuo)»: migliore 022 1h S, t 1,32, R +0,011, 175 trade (2 var.)
* FTM I-10 «Premio del perpetuo sul mark price»: migliore 018 1h S, t 1,13, R +0,007, 164 trade (2 var.)
* DYDX I-12 «Il perpetuo caro o economico rispetto al mark»: migliore 020 1h S, t 0,41, R −0,015, 312 trade (2 var.)
* MASK I-14 «Premio del contratto sul mark price»: migliore 025 1h L, t −0,13, R −0,043, 444 trade (2 var.)

**Cosa ne è stato.** «Il funding alto non anticipa un calo: accompagna i rialzi» (`confronto/lezioni_comuni.md` §1.5);
lo short sul funding alto è fra le idee da non riprovare (§4). Il funding molto negativo seguito da long dà un debole
guadagno sulle monete grandi e una perdita sulle piccole: osservazione, non prova (§3.4). Il premio sul mark «c'è solo
dove la liquidità è scarsa» (§1.12).

### 3.G Relazioni con Bitcoin (e fra monete)

**Relazione con BTC.** Ritardo della moneta dopo un movimento forte di BTC, forza relativa, residuo rispetto a BTC,
coppia con BTC (Lo, MacKinlay 1990; Hou, Moskowitz 2005; Koutmos 2018; Sifat e altri 2019; Liu, Tsyvinski, Wu 2019;
Avellaneda, Lee 2010; Gatev e altri 2006; Da, Liu, Schaumburg 2014). **14 campagne, 51 varianti (12 ritocchi), 2
nette, 2 candidati (FIL 016 e DYDX 008, entrambi 1h long), 1 in validazione (DYDX 008: R −0,178).** FIL 016 cade ai
costi doppi (R −0,004); su DYDX la prova dello scettico mostra che «conta solo l'ora forte di BTC», non il ritardo
della moneta. Sul gruppo di 80 monete la stessa idea è la più vicina alla soglia (GRUPPO-048 t 2,06 e GRUPPO-046 t
2,01 contro 2,16), con effetto lordo +0,04-0,09 R contro costi 0,05-0,07 R (`confronto/risultati.md` §3.2). Nel gruppo
erano vietate le regole fra monete diverse da BTC (classifiche, forza relativa fra monete del gruppo:
`campagne/GRUPPO/regole.md` §3 punto 3).

* FIL I-08 «Ritardo di FIL rispetto a BTC (lead-lag)»: migliore 016 1h L, t 2,35, R +0,067, 426 trade (2 var.) — **candidato di Fase 2: 016**
* DYDX I-08 «BTC guida, DYDX segue»: migliore 008 1h L, t 2,22, R +0,060, 161 trade (2 var.) — **candidato di Fase 2: 008**
* GRUPPO I-07 «La moneta che resta indietro rispetto a un movimento forte di BTC»: migliore 048 1h L, t 2,06, R +0,008, 2806 trade (7 var.; 5 rit.)
* GALA I-06 «Ritardo rispetto a BTC»: migliore 011 1h L, t 1,94, R +0,067, 162 trade (4 var.; 2 rit.)
* ADA I-12 «Ritorno del residuo rispetto a BTC»: migliore 022 1h L, t 1,92, R +0,226, 87 trade (2 var.)
* GRUPPO I-19 «Inversione del rendimento proprio della moneta, al netto di BTC»: migliore 051 4h L, t 1,89, R +0,028, 11062 trade (7 var.; 5 rit.)
* ADA I-06 «BTC guida, ADA segue con ritardo»: migliore 010 1h L, t 1,86, R −0,007, 534 trade (2 var.)
* 1000SHIB I-09 «Bitcoin guida, la moneta segue»: migliore 010 1h S, t 1,25, R +0,023, 152 trade (2 var.)
* MASK I-08 «MASK in ritardo su BTC»: migliore 013b 1h L, t 0,96, R +0,025, 112 trade (2 var.; 2 scarti)
* AVAX I-05 «Ritardo di AVAX rispetto a BTC, a 1 ora»: migliore V09 1h L, t 0,94, R −0,009, 269 trade (2 var.)
* XRP I-06 «BTC guida, XRP segue con ritardo»: migliore V10 1h L, t 0,91, R −0,045, 363 trade (2 var.)
* MASK I-13 «Il trend del mercato trascina la moneta»: migliore 023 4h L, t 0,90, R +0,313, 110 trade (1 var.)
* FTM I-08 «Il grande guida il piccolo (BTC prima di FTM)»: migliore 014 1h L, t 0,90, R −0,008, 173 trade (2 var.)
* SOL I-11 «BTC guida, SOL segue (lead-lag)»: migliore 018 1h L, t 0,74, R −0,006, 208 trade (2 var.)
* MATIC I-14 «Forza relativa contro BTCUSDT (momento fra crypto)»: migliore 019 4h L, t 0,67, R +0,410, 161 trade (2 var.)
* ETC I-09 «BTC guida, ETC segue in ritardo»: migliore 020 1h L, t 0,41, R −0,037, 122 trade (1 var.; 1 scarto)
* ETH I-07 «BTC si muove prima di ETH»: migliore 013 1h L, t 0,19, R −0,040, 213 trade (2 var.)
* AVAX I-11 «Forza relativa contro BTC, a 1 giorno»: migliore V20 1d L, t 0,14, R +0,060, 100 trade (1 var.)
* XRP I-14 «Momentum relativo: XRP contro BTC»: migliore V26 1d L, t 0,00, R +0,026, 120 trade (2 var.)
* GRUPPO I-26 «Momento del rendimento proprio della moneta, al netto di BTC»: migliore 034 1d L, t −0,07, R +0,002, 954 trade (2 var.)
* GALA I-11 «Valore relativo rispetto a BTC»: migliore 021 4h S, t −0,79, R −0,162, 82 trade (2 var.)
* ETC I-17 «Valore relativo con BTC (una gamba di una coppia)»: solo scarti, mai testata (trade stimati 48, 47)

**Cosa ne è stato.** «BTC guida, la moneta segue: un effetto piccolo e di regime, sempre sotto i costi»
(`confronto/lezioni_comuni.md` §1.11). È stata ripresa due volte: nella seconda edizione come terza idea, «il ritardo
delle monete dopo un giorno forte di Bitcoin», e il momentum fra monete come seconda (diario r. 3627, r. 3657;
`PROTOCOLLO_2.md`).

### 3.H Altre famiglie

**Continuazione dopo una barra o un giorno anomalo** (Caporale, Plastun 2019/2020; Llorente e altri 2002; Zaremba e
altri 2021). **15 campagne, 35 varianti, 1 netta, 1 candidato (AVAXUSDT-V14, 4h long), caduto al ritardo per 0,015 di
t (1,327 contro 1,342)**: la campagna lo porta come lezione di metodo, non chiede di recuperarlo
(`confronto/risultati.md` §3.1). Mio conteggio: 13 campagne, 29 varianti (differenza di assegnazione).

* AVAX I-08 «Seguire le reazioni eccessive, a 4 ore»: migliore V14 4h L, t 2,68, R +0,200, 113 trade (2 var.) — **candidato di Fase 2: V14**
* GALA I-08 «Movimento grande con volume alto: continuazione»: migliore 015 1h L, t 1,84, R +0,116, 163 trade (2 var.)
* MATIC I-03 «Continuazione dopo un rendimento giornaliero anomalo»: migliore 003 1h L, t 1,51, R +0,169, 113 trade (2 var.)
* ADA I-04 «Reazioni eccessive giornaliere: inerzia il giorno dopo»: migliore 030 1d L, t 1,46, R +0,060, 98 trade (2 var.; 2 scarti)
* ETH I-18 «Dopo una barra grande con volume alto, il prezzo continua (cascata)»: migliore 034 1h S, t 1,18, R +0,015, 127 trade (1 var.)
* 1000SHIB I-13 «Momento dopo un rendimento anomalo»: migliore 021 4h L, t 1,07, R +0,232, 80 trade (2 var.)
* ETC I-04 «Giornate di reazione eccessiva: continuazione il giorno dopo»: migliore 005 1d L, t 0,78, R +0,087, 105 trade (2 var.)
* LINK I-15 «Continuazione dopo un'ora anomala fino alla fine del giorno»: migliore V26 1h L, t 0,62, R +0,040, 159 trade (2 var.)
* BCH I-06 «Inerzia dopo le giornate di sovra-reazione (1d)»: migliore 025 1d L, t 0,44, R +0,006, 94 trade (2 var.; 2 scarti)
* BNB I-08 «Sovrareazione seguita da continuazione»: migliore 034 4h L, t 0,38, R +0,049, 132 trade (2 var.; 4 scarti)
* XRP I-03 «Continuazione dopo un giorno di «sovrareazione»»: migliore V05b 1d L, t −0,28, R −0,064, 103 trade (2 var.; 2 scarti)
* GRUPPO I-03 «Continuazione dopo un giorno anomalo»: migliore 014 1d S, t −0,37, R −0,024, 1405 trade (2 var.)
* LTC I-10 «Inerzia dopo un giorno anomalo»: migliore 018b 1d L, t −0,65, R −0,083, 119 trade (2 var.; 2 scarti)
* ETH I-10 «Dopo un giorno anomalo, il prezzo continua»: migliore 018 1d L, t −1,52, R −0,099, 126 trade (2 var.)
* LINK I-13 «Momentum giornaliero delle monete grandi»: migliore V23 1d S, t −1,98, R −0,058, 322 trade (2 var.)
* DOGE I-12 «Inerzia dopo un giorno anomalo»: solo scarti, mai testata (trade stimati 39, 26, 66, 63)
* GALA I-12 «Reazione eccessiva giornaliera: il giorno dopo continua»: solo scarti, mai testata (trade stimati 20, 15)

**Numeri tondi e livelli** (Osler 2000 e 2003). **16 campagne, 34 varianti, 1 netta, 1 candidato (ETHUSDT-026,
rifiuto del massimo di ieri, 1h short), caduto ai costi doppi (R −0,076) e al ritardo (t 1,27 contro 1,33).** I numeri
tondi veri e propri, su 15 campagne e con fino a 1.800 trade per variante, non sono mai netti: ETH lo chiama «il
risultato più pulito» (`confronto/lezioni_comuni.md` §1.7).

* ETH I-14 «Rifiuto al massimo (minimo) del giorno prima»: migliore 026 1h S, t 2,67, R +0,023, 615 trade (2 var.) — **candidato di Fase 2: 026**
* ADA I-11 «Numeri tondi: gli ordini di stop oltre le soglie tonde»: migliore 020 1h L, t 1,27, R +0,032, 394 trade (2 var.)
* LTC I-06 «Ordini concentrati intorno ai numeri tondi»: migliore 012 1h S, t 1,15, R −0,023, 882 trade (2 var.)
* SOL I-13 «Numeri tondi e ordini di stop (Osler)»: migliore 022 1h S, t 1,14, R +0,000, 480 trade (2 var.)
* 1000SHIB I-15 «Ordini raggruppati ai numeri tondi»: migliore 025 1h L, t 1,04, R −0,020, 1129 trade (2 var.)
* XRP I-12 «Numeri tondi: ordini di stop oltre la soglia»: migliore V22 1h L, t 0,86, R −0,061, 1717 trade (2 var.)
* BNB I-18 «Ordini di stop oltre i numeri tondi»: migliore 040 1h S, t 0,82, R −0,056, 1396 trade (2 var.)
* DOGE I-14 «Numeri tondi e ordini fermi»: migliore 027 1h S, t 0,61, R −0,023, 751 trade (2 var.)
* LINK I-11 «Numeri tondi e stop raggruppati»: migliore V19 1h L, t 0,57, R −0,027, 554 trade (2 var.)
* TRB I-11 «Numeri tondi: accelerazione dopo l'attraversamento»: migliore I-11-S 1h S, t 0,43, R −0,060, 449 trade (2 var.)
* DYDX I-09 «Numeri tondi»: migliore 011 1h S, t 0,37, R −0,020, 373 trade (2 var.)
* FTM I-15 «Ordini di stop oltre i numeri tondi (cascate dopo l'attraversamento)»: migliore 030 1h L, t 0,36, R −0,041, 1846 trade (2 var.)
* ETC I-14 «Ordini ai numeri tondi»: migliore 026 1h L, t 0,19, R −0,054, 549 trade (2 var.)
* ETH I-11 «Il passaggio di un numero tondo fa scattare gli stop»: migliore 020 1h L, t 0,10, R −0,052, 1641 trade (2 var.)
* BCH I-05 «Attraversamento dei livelli tondi (1h)»: migliore 009 1h L, t −0,27, R −0,057, 1382 trade (2 var.)
* GALA I-16 «Numeri tondi: ordini di presa di profitto»: migliore 033 1h S, t −0,83, R −0,057, 383 trade (2 var.)
* BTC I-11 «I numeri tondi (ordini di stop oltre le soglie)»: migliore V21 1h S, t −1,50, R −0,098, 1413 trade (2 var.)

**Candele (martello, stella cadente, posizione della chiusura)** (Nison 1991; Caginalp, Laurent 1998). **4 campagne, 7
varianti, 0 nette, t massimo 1,66 (BTCUSDT-V22, 4h long: senza i 3 migliori −0,03).**

* BTC I-12 «Il «martello» e la «stella cadente»»: migliore V22 4h L, t 1,66, R +0,533, 71 trade (1 var.; 1 scarto)
* GRUPPO I-24 «Candela di inversione dopo un movimento»: migliore 033 1d S, t 0,80, R −0,002, 1652 trade (2 var.)
* TRB I-12 «Posizione della chiusura nella barra (internal bar strength)»: migliore I-12-L 1d L, t 0,35, R +0,036, 112 trade (2 var.)
* TRB I-18 «Ombre di rifiuto (martello e stella cadente)»: migliore I-18-L 4h L, t 0,30, R +0,066, 122 trade (2 var.)
* MASK I-10 «Candela a martello sul minimo (e stella cadente sul massimo)»: migliore 018 1h S, t 0,11, R −0,038, 158 trade (2 var.)

**Distribuzione (volatilità bassa, asimmetria, «lotteria», autocorrelazione)** (Moreira, Muir 2017; Amaya e altri
2015; Boyer e altri 2010; Bali, Cakici, Whitelaw 2011). **7 campagne, 10 varianti, 0 nette, t massimo 0,22
(BCHUSDT-032)**: «la più lontana dal caso in assoluto».

* TRB I-16 «Regime di autocorrelazione (rapporto delle varianze)»: migliore I-16-S 1h S, t 0,39, R −0,043, 203 trade (2 var.)
* BCH I-14 «Volatilità bassa: più rendimento per unità di rischio (1d)»: migliore 032 1d L, t 0,22, R −0,014, 113 trade (1 var.)
* GRUPPO I-11 «Moneta «lotteria» dopo un rialzo estremo di un giorno»: migliore 027 1d S, t −0,02, R −0,038, 798 trade (1 var.)
* 1000SHIB I-16 «Effetto lotteria (rendimento massimo recente)»: migliore 027 4h S, t −0,11, R −0,026, 173 trade (1 var.)
* BNB I-17 «Asimmetria realizzata negativa»: migliore 038 4h L, t −0,24, R +0,179, 89 trade (1 var.; 1 scarto)
* TRB I-17 «Volatilità bassa, rendimento per rischio più alto»: migliore I-17-L 4h L, t −0,36, R −0,003, 90 trade (1 var.)
* TRB I-15 «Preferenza per le lotterie: asimmetria dei rendimenti»: migliore I-15-L2 4h L, t −0,58, R −0,025, 106 trade (2 var.; 2 scarti)
* DOGE I-07 «Domanda da lotteria (effetto del massimo)»: migliore 013 1d S, t −1,02, R −0,112, 71 trade (1 var.; 1 scarto)
* BNB I-14 «Volatilità bassa»: migliore 029 4h L, t −1,10, R −0,036, 353 trade (1 var.)
* FTM I-12 «Rendimento per rischio più alto quando la volatilità è bassa»: migliore 022 1d L, t −1,35, R −0,021, 74 trade (1 var.)

### 3.I Le idee della prova di processo (7 ottobre, versione 4.3)

Sono sui branch di archivio e non sono state unite nel principale (`lezioni/metodo.md`, ultima sezione). Titoli da
`ipotesi.md` dei tre branch `origin/research/archivio/campagna/<MONETA>`; numeri da `confronto/lezioni_comuni.md` §5 e
`prova_processo/rapporto.md` §5.

* **BTCUSDT** (13 idee): rottura del canale; momento a una settimana; prima mezz'ora → ultima mezz'ora; funding
  estremo (e funding negativo assoluto); lunedì; continuazione dopo un giorno anomalo; rottura dell'intervallo
  d'apertura; RSI a 2 periodi; premio del volume alto; compressione di Bollinger; volatilità bassa; NR7; ritorno dalle
  bande di Bollinger. La più vicina: **funding negativo nel decile più basso → «24 ore positive»** (variante V08, long,
  8h), R 0,08, positivo ogni anno, 96° percentile, mai netta, «sparisce a 12 ore»; su di lei le 12 verifiche della
  campagna.
* **ETHUSDT** (22 idee di 17 famiglie secondo la consegna; nell'ipotesi i titoli di 19, più 3 del quarto lotto):
  momento, canale, RSI a 2, candela anomala, ritardo di ETH su
  BTC, coppia ETH/BTC, momento relativo ETH/BTC, fine settimana, prima ora → ultima ora, funding, compressione,
  volume, squilibrio degli ordini, premio sul mark, intervallo d'apertura, ore americane e asiatiche,
  autocorrelazione giornaliera, livelli tondi, vicinanza al massimo a 30 giorni. Nessuna oltre 2 errori standard; 4 su 23
  sopra il 97° percentile.
* **SOLUSDT** (13 idee): momento; funding estremo; sessione americana; fine settimana; continuazione e ritorno dopo
  una barra estrema; canale; ritorno dentro Bollinger; ritracciamento nella tendenza con le medie; ritardo su BTC;
  volume alto; compressione; squilibrio degli ordini. La più vicina: **short sui ritracciamenti in tendenza
  ribassista**, R 0,14, profit factor 1,30, sopra tutte le 200 casuali, p 0,085, «l'unica idea che varrebbe la pena
  riprovare con una regola scritta meglio prima». La campagna 4.5 di SOL ha trovato qualcosa di simile (NR7 short
  sotto la media a 200, R +0,18, non netta contro la (a)).

### 3.J Idee non scritte, ritirate o dichiarate «scritte dopo»

* **Ritirate per contaminazione**: MATICUSDT ha tolto l'idea del ritardo rispetto a BTC dopo aver visto, fra i
  risultati di una ricerca e senza aprirlo, il riassunto di un articolo del 2024 che nominava la moneta (nota
  MATICUSDT-N008 del log; `campagne/MATICUSDT/ipotesi.md`, «Idee scartate prima del test»); GALAUSDT
  ha ritirato la variante 027, scritta dopo aver lanciato i test e arrivata 8 secondi dopo il primo risultato della sua
  idea (`lezioni/metodo.md`, «Ritocchi e budget»).
* **Non scritte perché senza direzione o con troppi pochi trade**: calendario (ora del giorno, giorno della settimana)
  in ADA e MASK, perché la fonte non dà una direzione (MASK: «sarebbe una ricerca fra 7 giorni o 24 ore, cioè scegliere sui dati»); cambio di mese in ADA
  (circa 33 trade) (`campagne/ADAUSDT/ipotesi.md` e `campagne/MASKUSDT/ipotesi.md`, sezioni finali).
* **Scritte dopo i primi risultati, dichiarate**: ETH I-15…I-18; LTC I-11; LINK I-14, I-15; GALA I-14…I-17; la
  seconda tornata di AVAX. Nessuna è arrivata in validazione (`confronto/risultati.md` §4.3, punto 7).
* **Nel gruppo**: niente regole fra monete (classifiche, forza relativa fra monete del gruppo), per scelta del testo
  delle regole (`campagne/GRUPPO/regole.md` §3, punto 3): «una rinuncia».

---

## 4. Le prove sul metodo

La domanda di tutte queste prove: **l'esame promuove il rumore? E vede un vantaggio quando c'è?**

### 4.1 Taratura su serie inventate (7 ottobre, versione 4.4)

Prima delle campagne 4.4, simulazioni con candidati **senza alcun vantaggio** e 30-70 trade (trade indipendenti, a
grappoli nello stesso giorno, R asimmetrici). Esito finale: «netta» fra lo 0 e il 2% dei casi, p-value sotto 0,10 fra
il 6 e l'11% (`PROTOCOLLO.md` §11, «Test sulla media»). Quello che hanno trovato strada facendo, con due giri di
revisione avversaria (`prova_processo/rapporto.md` §9):

* la regola «nettamente» scritta in modo semplice dava falsi positivi dal 4-9% **fino al 30% con pochi blocchi**,
  contro il 2,3% dichiarato;
* con R asimmetrici (molti piccoli guadagni e rare grandi perdite) «netta» arrivava all'8% e il p-value sotto 0,10 al
  24%, finché non è stato aggiunto il **pavimento dell'errore** (l'errore di una strategia senza vantaggio con gli
  stessi trade);
* la verifica a costi doppi «non poteva fallire» e il criterio del ritardo lasciava passare un lookahead.

Correzioni: errore corretto per il blocco, pavimento, soglia della t di Student, almeno 3 blocchi interi, 200
simulazioni a semi fissi (`CHANGELOG.md`, righe del 2026-10-07; test in `src/tests/test_regole_4_4.py`).

### 4.2 Il controllo positivo in ogni campagna

Una strategia che legge di proposito la barra successiva (lookahead dichiarato) deve battere nettamente il caso e
crollare con il ritardo di una barra; si registra come nota e non consuma budget (`lezioni/metodo.md`, «Il metodo»,
dal 7 ottobre). Nella prova di processo l'ha fatto solo ETHUSDT: 30 errori standard, poi profit factor 0,8 con il
ritardo, dieci minuti di lavoro (`prova_processo/rapporto.md` §4.2). Dalle campagne 4.5 è venuta una correzione: col
ritardo il controllo **non va a zero** quando lo stop si calcola dalla barra del segnale (BTC t 8,4; BNB circa 4; AVAX
3,3; DYDX 2,48 contro 46,9 senza ritardo; GALA 3,7), quindi «crolla» va letto come rapporto, guardando anche che l'R
diventi non positivo; e va fatto in entrambe le direzioni e sui timeframe usati (BCH ne ha fatti due)
(`lezioni/metodo.md`, «Baseline, potenza dell'esame…»).

### 4.3 La prova di processo (7 ottobre)

Tre campagne complete con la 4.3, vault chiuso, validazione mai toccata (sezione 2.1). La diagnosi del rapporto
(`prova_processo/rapporto.md` §5):

1. con 100 trade minimi per direzione la ricerca su una moneta **scarta le idee lente prima di provarle**: 34 scarti su
   44 a 4 ore o più lente, metà delle stime fra 50 e 99 trade;
2. quando una variante mostra un segnale, **una moneta sola non ha i trade per confermarlo**: con R medi di 0,05-0,10 e
   deviazioni di 0,5-0,7 R per trade servono 300-500 trade per rendere netto un vantaggio di 0,08 R;
3. le campagne si sono fermate per **mancanza di idee con fonte**, non di budget (34 varianti su 90 non spese);
4. tre campagne hanno usato tre regole di stima e due letture di «nettamente».

Cosa non è emerso come problema: vault chiuso, nessuna campagna ha letto le altre, log in aggiunta su 229 voci, consegne
che dicono «non trovato» invece di forzare un candidato.

### 4.4 La prova a placebo sui prezzi veri (9 ottobre)

Regole committate prima del lancio (commit 8b6abf6b), risultati in `taratura/placebo/risultati.md` (commit ee34519f),
branch di coordinamento.

* **Come**: sulle 80 monete idonee non di campagna, solo fino al 2023, a 1h e 4h, sei regole da manuale (incrocio delle
  medie, RSI 14, rottura di 20 barre, Bollinger, MACD, rendimento a 10 barre) con i segnali **spostati tutti insieme
  nel tempo** di uno sfasamento casuale: i grappoli restano, il vantaggio sparisce per costruzione. Giudicate con gli
  strumenti delle campagne (`taratura/placebo/regole.md` §3-4).
* **Soglie scritte prima**: M1 («netta» in costruzione) 3%, M2 (p sotto 0,10 in validazione) 13%; se superate, STOP e
  si rifanno anche BTC, ETH e SOL (diario r. 3194).
* **Esito**: **M1 = 0,41%** (6 su 1.479; per moneta 0,13-0,74%), **M2 = 3,26%** (44 su 1.348; per moneta
  2,41-4,17%). L'esame regge. Il t delle placebo ha media 0,007 e deviazione 0,815 invece di 1: centrato giusto ma
  **più severo del dichiarato**, quindi con meno potenza.
* **Unica regola sopra il 2%**: l'incrocio delle medie a 1h, 5 su 154 (3,25%): segnali rari e a grappoli lunghi.
* **Un errore trovato prima del lancio**: nella prima versione lo sfasamento stava fra un quarto e tre quarti del
  periodo; toglieva metà del cerchio e dava alle regole contrarie un vantaggio e alle rotture uno svantaggio, con lo
  stesso segno su tutte le monete. Trovato da due revisori indipendenti; su serie sintetiche faceva salire il p sotto
  0,10 al 13,1% contro il 6,2% per l'RSI long (diario r. 3194; `taratura/placebo/regole.md` §3, punto 2).
* **Uso**: la probabilità per moneta del trasferimento è stata fissata a 0,02 (il più alto fra 0,02, 0,0041 e 0,0030)
  e scritta in `vault/APERTURA.md`.
* **Limiti dichiarati**: regole da manuale, non le idee delle campagne; niente funding; stop e mark uguali al last;
  nessuna verifica di Fase 4. Misura i falsi positivi, non la potenza.

### 4.5 Il controllo positivo degli strumenti di gruppo (10 ottobre)

La sessione di gruppo si è fermata perché il suo controllo, con uscita a 7 giorni, non passava contro la (a) (t 1,96
contro 2,07). Il coordinamento l'ha rifatto con gli stessi strumenti e le uscite della prova a placebo
(`taratura/controllo_positivo_gruppo/esito.md`, commit 8ff80d4d):

| Uscita | Passa | t contro la (b) | t contro la (a) | t con 1 barra di ritardo |
|---|---|---|---|---|
| 4h, stop 2 ATR, chiusura dopo 12 barre | sì | 6,15 | 3,43 | 0,74 |
| 4h, stop 1,5 ATR e target 2,5 ATR, senza chiusura a tempo | no | non valutabile | non valutabile | non valutabile |
| 1h, stop 2 ATR, chiusura dopo 24 barre | sì | 6,10 | 4,19 | −0,25 |

Lettura: gli strumenti funzionano; **un'uscita senza tempo massimo rende l'esame di gruppo quasi cieco**, perché la
posizione più lunga di una moneta allunga il blocco per tutte. La sessione l'ha rifatto con uscita a 1 giorno: t 24,45
contro la (b), 9,85 contro la (a), −1,28 col ritardo (`campagne/GRUPPO/consegna.md`).

### 4.6 La prova a placebo dell'esame di gruppo (10-11 ottobre)

Regole chiuse alle 17:10 del 10 ottobre (commit 39d09587) con le impronte di cinque file degli strumenti; lancio di
circa 15 ore in 9 pezzi; un riavvio della macchina senza perdita di righe; risultati in
`taratura/placebo_gruppo/risultati.md` (commit 80f594a4, verifica eddee347).

| Misura | Valore | Limite |
|---|---|---|
| M1: placebo nette in costruzione | **0 su 85** | 2 |
| M2: p sotto 0,10 in validazione | **2 su 93** (2,15%) | 12 |
| M3 costruzione (coda della distribuzione) | 0,19% | 3% |
| M3 validazione | 2,95% | 13% |

* L'esame di gruppo è **ancora più severo** di quello per moneta: deviazione degli z 0,67 e 0,64 invece di 1.
* **Effetto grappolo misurato**: mediana 12,5 in costruzione e 12,2 in validazione: i trade sommati di 80 monete valgono
  circa **un dodicesimo** di altrettanti trade indipendenti.
* Tre controllori indipendenti hanno rifatto i conti dagli esiti grezzi senza smentire l'esito.
* **Una precisazione onesta del file stesso**: l'intestazione «regole chiuse prima di calcolare qualunque risultato»
  alla lettera non è esatta: prima della chiusura hanno girato una prova di fumo (12:56) e un lancio di
  funzionamento sulle 80 monete (15:03) con 4 etichette uguali alla prova vera; le regole che decidono erano però già
  quelle finali nel commit cf03ac39 delle 13:12 (sezione «Verifica indipendente», paragrafo «Da sapere
  sull'intestazione delle regole»).

### 4.7 La prova dell'attaccante sul guardiano (7 ottobre)

Un agente dedicato ha provato a leggere ciò che il guardiano vieta: 106 tentativi, nessuna lettura riuscita per altre
vie. Limite dichiarato: il guardiano giudica le azioni, non il contenuto degli script che la sessione scrive ed esegue
nella sua cartella (`PROTOCOLLO.md` §11, «Il guardiano ha un limite»).

### 4.8 Le letture d'insieme

* **Distribuzione dei t delle 600 varianti**: media 0,46, deviazione 1,30 (`confronto/risultati.md` §0). Rispetto alla
  placebo (media circa 0, deviazione 0,8) la coda alta è più grossa: 71 varianti nette contro la (b) (11,8%) contro lo
  0,41% delle placebo. Il coordinamento lo spiega con **i ritocchi concentrati sulle famiglie vicine alla soglia** (34
  candidati su 45 vengono da ritocchi) e con **la trappola dello stop agganciato a un livello**, non con un vantaggio
  (`confronto/risultati.md`, Punto 1, «Un indizio in più»). Due campagne (BCH e TRB) hanno fatto lo stesso controllo
  sulle loro 30 varianti e scrivono «la forma del caso» (t medio 0,11 e 0,05).
* **Validazione**: 3 su 6 candidati valutabili sotto la soglia, contro 0,2-0,6 attesi per caso
  (`passo4/riepilogo.md`): un indizio che il vault ha smentito (0 su 3, attesi 0,02).
* **Timeframe** (`confronto/risultati.md` §3.3): sotto l'ora t alti e molti candidati (22 su 45) ma nessuno regge i
  costi; a 1h 6 dei 7 validati, in una distribuzione «che somiglia al caso» (18 nette su 242); a 2h, 8h e 1d nessun
  candidato.

---

## 5. Errori di metodo e difetti degli strumenti, con la correzione

### 5.1 Strumenti (motore, caricatore, statistica, guardiano)

| Quando | Difetto | Come è stato trovato | Correzione | Fonte |
|---|---|---|---|---|
| 6 ott | 36 difetti nel Passo 0: motore 14 (gap in apertura, funding nella candela di chiusura, liquidazione con gap, buchi nella serie), dati 5 (candela a cavallo del 2024, `APERTURA.md` vuoto, fine del vault), statistica 3 (bootstrap degenere, entrate casuali, parità di Benjamini-Hochberg), guardiano 10 (marcatore scrivibile, link simbolici, espansioni della shell, git su altri branch), fatti 4 | quattro revisori avversari | corretti prima di qualunque campagna | `CHANGELOG.md`, riga del 2026-10-06 |
| 7 ott | Un test importava `yaml` senza `pyyaml` fra le dipendenze: test di GitHub rossi per 12 esecuzioni | email di job falliti al proprietario | `pyyaml` in `requirements.txt`, la CI copre anche i test della ricerca (45e664d) | `CHANGELOG.md`; diario r. 2978 |
| 7 ott | Stima dei trade fatta in tre modi diversi (la stessa idea dava 83 o 105 trade) | prova di processo | `conta_trade`, una sola stima, con le regole esatte | `prova_processo/rapporto.md` §3.1; `CHANGELOG.md` |
| 7 ott | «Nettamente» con due letture (`differenza_nettamente` confrontava con UNA corsa casuale); simulazioni 100 o 200 a scelta | prova di processo | `contro_baseline` unico, 200 simulazioni a semi fissi | rapporto §3.2-3.3 |
| 7 ott | Il motore copiava le candele a ogni barra (lento: 5 minuti per esame a 1h) | prova di processo (BTC) | vista in sola lettura delle barre chiuse, circa 30 volte più veloce, stessi trade | `CHANGELOG.md`, riga «StoriaChiusa» |
| 7 ott | La scheda della moneta con la data di listing diceva se la moneta è delistata | revisione della 4.4 | tolta la data di listing, resta il primo mese di dati | `CHANGELOG.md`; appendice 3 |
| 7 ott | Guardiano: si potevano leggere storia dei commit, hash degli archivi, strumenti GitHub; `git fetch` senza nome stampava i nomi degli archivi; l'ordine di avvio permetteva di committare sul principale | revisione della 4.4 e attaccante dedicato | regole del guardiano 4.4, test in `test_guardiano_4_4.py` | `CHANGELOG.md`, righe del 2026-10-07 |
| 7 ott | Date in virgola mobile (0,70 × 1430 dà un giorno in meno); ingressi persi nella baseline casuale | revisione della 4.4 | `periodi_campagna` con numeri interi; `barre_vietate_segnale_non_valido` | appendice 3 |
| 8 ott | Il funding nei file di Binance arriva fino a 47 ms dopo l'ora piena (2.233 settlement su 4.383 per BTC 2020-2023) e il motore non lo riconosceva come momento ambiguo | campagna BTCUSDT 4.4 | arrotondato al secondo (2fedf41, portato sul principale con adfb831); ETH ricalcolata: differenza massima −0,0075 R, nessun esito cambiato | `CHANGELOG.md`; diario r. 3120 e righe dell'8 ott |
| 8 ott | Su SOL la correzione non arrivava ai test perché la cache si ricostruiva solo se mancava: 2.083 settlement su 3.688 ancora con i millisecondi, SOLUSDT-015 da netto a non netto | campagna SOLUSDT | la cache porta l'impronta di `src/dati.py` | `lezioni/metodo.md`, «I dati e l'allineamento» |
| 9 ott | Tre allineamenti diversi di last e mark nelle tre campagne della prova | prova di processo, proposta 6 | `carica_serie_allineate` unico | `CHANGELOG.md`, riga del 2026-10-09 |
| 9 ott | Buco del guardiano visibile solo con il git dei server di GitHub: `git log --no-walk HEAD~1 -- <cartella>` stampava il messaggio di un commit del principale; i test fallivano a ogni push dall'8 ottobre | email di GitHub | `--no-walk` vietato (89f1d376) | `CHANGELOG.md`; diario r. 3213 |
| 9 ott | Prova a placebo: sfasamento fra L/4 e 3L/4 che falsava la prova | due revisori prima del lancio | sfasamento su quasi tutto il periodo | sezione 4.4 |
| 9 ott | Trasferimento: con molte monete 2 passaggi escono per caso (19% su 80 monete) | scrittura della 4.5 | `monete_richieste_trasferimento` | appendice 4 |
| 10 ott | Gruppo: con il 70/30 per moneta il 34,5% dei giorni di validazione cadeva nella costruzione di altre monete | scrittura delle regole del gruppo | taglio comune al 2023-01-16 | `campagne/GRUPPO/regole.md` §1 punto 4 |
| 10 ott | Prima e seconda sessione di gruppo ferme: pytest e scipy mancanti, pip vietato in campagna, Python 3.13 con numpy 1.26.4 non installabile; un avviso di Python 3.13 faceva fallire un test del guardiano | le sessioni stesse | script d'avvio che installa da solo le dipendenze (de2618ae, e761cc05); `maxsplit` per nome (2bfb2f99) | diario r. 3332, r. 3343; `CHANGELOG.md` |
| 10 ott | Una sola moneta con meno di 2 trade della (a) rendeva non valutabile una variante di gruppo (2 su 6 validazioni della prova di funzionamento) | prova di funzionamento | regola nuova per le monete con 0 o 1 trade della (a) | `campagne/GRUPPO/regole.md` §5 punto 3 |
| 11 ott | Un test lanciava uno script senza `PYTHONPATH` e falliva solo su GitHub | email di GitHub | corretto; il workflow gira solo sul principale | `CHANGELOG.md`; diario r. 3525 |
| 12 ott | La copia del repository era «a storia limitata» e non permetteva le unioni del Passo 7 | Passo 7 | scaricata la storia completa | diario r. 3569 |
| 13 ott | Prova degli ordini limite: un ordine limite riempito «all'apertura se è già sotto il prezzo» regalava al trade un vantaggio che un ordine limite non ha | scrivendo i test del motore, prima delle corse | riempimento al prezzo del limite | `esperimenti/ordini_limite/risultati.md` §1, correzione 1 |

### 5.2 Regole del protocollo che non coprivano un caso

* **Netta contro (a) e (b) ma con R non positivo**: entrava o no nei ritocchi? Non scritto (SOL, 8 ott). Deciso dal
  proprietario, scritto nella 4.5 (appendice 4, prima riga). Per BTCUSDT, che aveva usato la regola della 4.4, il
  controllo meccanico ha trovato 2 varianti in questo caso (V19 e V31): «la sua scelta dei ritocchi sarebbe potuta
  essere diversa»; il proprietario ha deciso di non rifarla (`passo4/riepilogo.md`, «Altri controlli» e risposta).
* **R positivo in validazione**: chiesto in costruzione, non in validazione (FIL, 9 ott). Corretto il 9 ottobre alle
  17:35, «prima che il coordinamento leggesse l'R di validazione degli altri candidati» (appendice 4, ultima riga).
* **Il test del ritardo boccia per costruzione le regole legate a un'ora del giorno**: una regola che entra alle 23:30
  per l'ultima mezz'ora, ritardata di una barra, entra a mezzanotte e misura un'altra strategia. Su FIL sette candidati
  con la fascia 20-24 UTC sono caduti così; AVAX V14 è caduta con il t a 0,494 volte quello senza ritardo, serviva
  0,5, e la ricerca dell'errore non ha trovato nulla. Tutte le campagne hanno seguito la regola com'era
  (`lezioni/metodo.md`, «Il test del ritardo e il controllo di causalità»).
* **Stabilità con un anno solo**: una regola rara supera la verifica alla lettera con un solo anno con 10 trade (XRP
  V21r3: 84 trade su 97 nel 2020, poi 5 in validazione) (`lezioni/metodo.md`, «Baseline, potenza…»).
* **Il controllo positivo di gruppo con uscite lunghe**: la (a) di gruppo ha poca potenza con tenute di più giorni
  (errore 0,070 R): le idee a 1d su più giorni «partivano svantaggiate» (`campagne/GRUPPO/consegna.md`, «Cosa dicono
  i numeri»).

### 5.3 Errori di metodo nelle campagne

* **Lo stop agganciato a un livello di prezzo** (apertura del giorno, estremo di una barra, minimo di un intervallo,
  una media) è **la trappola più ripetuta**: le baseline entrano anche dove il livello è vicinissimo, il costo fisso
  diviso un rischio minuscolo dà R molto negativi, e una variante che entra solo dove lo stop è largo le batte
  «nettamente» senza alcun potere di previsione. Casi: BTCUSDT (b) a −0,83 R, V11 da t 3,01 a 1,01 con stop fisso al
  2%; LTCUSDT-027 da 1,95 a 0,01; ADAUSDT 6 volte su 6; FILUSDT-025 t 1,38 contro stop normali; BCH, AVAX
  (`lezioni/metodo.md`, «Stop, costi e tetto del bot»). Lo stesso difetto tocca il test del ritardo quando lo stop si
  calcola dalla barra del segnale.
* **Un filtro che sceglie le barre volatili abbassa i costi in R** e la (b) normale non lo sa: il segno è un t che
  cresce a costi doppi mentre l'R scende sotto zero (1000SHIB: 2,08 → 2,56 e 2,15 → 2,48). La prova utile è la (b)
  ristretta alle barre del filtro: ADA-037 dava t 0,63 contro questa (b), dopo aver superato tutte le verifiche
  (`lezioni/metodo.md`, stessa sezione).
* **Ritocchi concentrati**: l'ordine per t concentra 5-8 ritocchi su una o due famiglie, e il candidato che ne esce è
  «il migliore di 5-7 tentativi sugli stessi dati» (SOL, LTC, FIL 8 su 8, DYDX 5+5, ETC, 1000SHIB, BTC 5 ritocchi di
  V19 con R lordo +0,045 contro costi 0,12 R). «È il comportamento della regola, non un errore delle campagne»
  (`lezioni/metodo.md`, «Ritocchi e budget»).
* **Filtri scelti sui dati di costruzione**: il fine settimana di BNB-045, «il migliore di 7 gruppi per giorno»; i due
  filtri di ADA-037 «nati dallo studio dei fallimenti» (`confronto/risultati.md` §2.2-2.3).
* **Errori di codice**: una media mobile con la somma cumulata propagava un valore mancante iniziale e dava 0 trade,
  cioè un falso scarto (BNBUSDT-N013); segnale valutato dopo la condizione che interrompeva `conta_trade` (MASK);
  id duplicati delle note (ETC, evitato); due campi con lo stesso nome persi unendo dizionari (MASK); titolo del commit
  precedente su due commit (FIL); orario delle voci a memoria (GRUPPO-013); previsione numerica dimenticata nella
  registrazione della validazione (BTC N018) (`lezioni/metodo.md`).
* **Varianti aggiunte mentre i test giravano**: GALA, ritirata; FTM I-04 (`lezioni/metodo.md`, «Ritocchi e budget»).
* **Durata dichiarata a memoria**: la consegna BTC della prova diceva «circa 2 ore e 40», la durata vera era 55 minuti
  (`prova_processo/rapporto.md` §2). Dalla 4.5 le misure di processo si prendono dalle date del log.

### 5.4 Errori del coordinamento e della piattaforma

* **Sessione nata senza il permesso di scrivere** (ETH, 7 ott): push rifiutato, 17 minuti di lavoro persi. Da allora la
  sorgente si passa esplicitamente e il primo push si controlla entro mezz'ora (diario r. 3002).
* **Sessione archiviata mentre partiva** (SOL, 8 ott, 05:19): nessun lavoro perso; da allora una sessione si giudica
  ferma solo dopo 20-25 minuti (diario r. 3111).
* **Domande non viste in tempo**: SOL 4 h 20 di attesa, di cui 2 h 40 prima che il coordinamento la vedesse; FIL 55
  minuti prima di essere vista (appendice 4; diario r. 3213). Da qui il controllo orario e le domande girate subito.
* **Impostazioni delle sessioni**: ultracode, chiesto dal proprietario, è mancato in tutte le aperture del 9 ottobre
  tranne l'ultima (ETCUSDT); la causa non è nota (`passo4/riepilogo.md`, «Altri controlli»; diario r. 3120).
* **Letture che il coordinamento non doveva fare**, dichiarate: una nota di chiusura di BTC nella prova (rapporto §9);
  riassunti automatici delle sessioni con qualche numero; la riga d'esito di BNB e la tabella delle verifiche di MATIC
  (diario r. 3213). Nessuna è entrata in un documento letto dalle campagne.
* **Nel vault**: un comando d'attesa sbagliato ha fatto partire ADAUSDT due ore dopo BNBUSDT, senza effetto sui
  risultati (diario r. 3540).
* **Fuori dalla ricerca, stessi giorni**: il 10 ottobre «non eseguire il report giornaliero» è stato applicato solo al
  controllo giornaliero e l'11 mattina è partito il referto settimanale; da allora tutti i report del mattino sono
  fermi (diario r. 3461; `CLAUDE.md`).

---

## 6. Trappole dei dati

Tutte da `lezioni/metodo.md` (sezioni del 7 ottobre e del Passo 7), salvo dove è scritto altro.

* **Il mark price ha buchi che il last non ha**, spesso negli stessi giorni su monete diverse: il 2 ottobre 2022 e il 24
  febbraio 2023 su ETH, LINK, FIL, ETC, GALA e AVAX; il 31 luglio 2022 su LINK, GALA e AVAX; luglio 2021 su LINK e AVAX.
  BTC nella prova: 770 barre a 15 minuti in 7 buchi. FIL ha buchi anche nel last. Nel vault manca un giorno di mark nel
  giugno 2026 (96,7% delle barre allineate) (`vault/risultati.md`). Conseguenze: le regole «da N barre fa» attraversano
  i buchi senza accorgersene; una posizione che attraversa un buco gonfia la durata media (AVAX: mezz'ora che vale 192
  barre), e quindi la distanza fra gli ingressi della (b).
* **Il volume delle candele è in moneta base, non in USDT**: per l'USDT serve la colonna `quote_volume`.
* **Il primo mese della scheda quasi mai è pieno**: XRP dal 6 gennaio 2020, LTC dal 9, ETC dal 16, LINK dal 17, ADA con il
  last solo dal 31 gennaio; 1000SHIB dal 10 maggio 2021 (673 giorni invece di 682), MASK dal 26-27 agosto 2021 (592
  invece di 618), DYDX dal 9-10 settembre 2021. Le date restano quelle scritte prima dei prezzi, ma il minimo di 70
  trade diventa più duro. La prima candela giornaliera è parziale.
* **I mesi sotto la liquidità minima tolgono i trade alle idee lente**: DOGE tutto il 2020 sotto i 20 milioni al giorno
  (costruzione utile da 895 a 711 giorni, 8 scarti su 14 a 1d o 4h); TRB 7 mesi su 28 di costruzione e 5 su 12 di
  validazione; FTM 4 mesi, trade solo in due anni; MATIC ingressi solo dal 1° febbraio 2021; SOL 2020 escluso, divisione
  vera 67/33 invece di 70/30 (`prova_processo/rapporto.md` §3, punto 5).
* **Lo slippage della scheda (calcolato sul volume 2023) è ottimista per il 2020-2021**: ETH nel 2020 faceva 723 milioni
  al giorno con minimi di 45 milioni (0,02-0,05% per lato invece di 0,01%); BCH nel 2020 e 2022 nella fascia 0,05% contro
  0,02% (e i costi doppi, 0,04%, restano sotto); TRB 0,10% contro 0,02%. Solo FTM dichiara la sua fascia prudente
  (`confronto/risultati.md` §4.3, punto 2).
* **Il funding arriva con qualche millisecondo di ritardo** (fino a 47 ms) e una cache vecchia può tenerlo (sezione
  5.1). ICPUSDT, nel gruppo, non ha file di funding per 16 mesi (2021-05 → 2022-08) (`campagne/GRUPPO/consegna.md`).
* **La quota di volume comprato a mercato** (`taker_buy_volume`, decima colonna dei file) c'è in tutti i mesi 2020-2023
  ma il motore non la porta; su un perpetuo il segno non è bilanciato (DYDX: sotto 0,5 in 257 giorni contro 54).
* **Il tetto dello stop del bot (6%) rende fisso lo stop di quasi tutte le idee da 4 ore in su**: ATR giornaliero
  mediano 10% su MATIC, 8% su 1000SHIB, 13,4% su TRB; stop in ATR giornalieri del 30% su FTM; GALA tocca il tetto in 69
  trade su 109 a 4h; nel gruppo 3 ATR a 1d valgono circa il 31%.
* **Una ricerca web può mostrare informazioni dopo il 2023**: MATIC ha visto il riassunto di un articolo del 2024 e ha
  tolto l'idea collegata (nota MATICUSDT-N008).
* **Dati di riferimento di BTC sugli stessi timeframe**: senza, il controllo «è solo il mercato» resta vuoto (SOL
  nella prova, a 4h).
* **Migrazioni dopo il 2023**: MATICUSDT (file fino a settembre 2024) e FTMUSDT non più negoziati con quel simbolo; la
  ricucitura (MATIC → POL, FTM → S) era rimandata al Passo 6, mai fatto (`universo/selezione_log.md`;
  `vault/APERTURA.md`, scelta 6).
* **Il periodo 2020-2023 è un rialzo e un ribasso**: «nel 2020-2021 bastava essere long»; gli short che guadagnano lo
  fanno nel 2022 (`confronto/risultati.md` §3.4). Il 2019 è escluso per tutte (`confronto/risultati.md` §4.3, punto 10).

---

## 7. Lezioni e proposte scritte allora, e cosa è stato messo in pratica dopo

### 7.1 Cosa hanno capito le campagne sulle monete

Da `confronto/lezioni_comuni.md` (sezioni 1, 3 e 4):

* le idee di tendenza guadagnano quanto un ingresso a caso nella stessa direzione: è l'anno, non la regola (§1.1);
* sotto l'ora i costi decidono tutto: 0,05-0,14 R per giro a 30 minuti, 0,05-0,10 a 1h, 0,034 a 4h e 0,012 a 1d nel
  gruppo (§1.2; `lezioni/metodo.md`, «Stop, costi…»);
* il segnale più ripetuto (short sull'ultima mezz'ora dopo una giornata in calo) vale meno dei costi (§1.3);
* dopo un'ora estrema il prezzo continua, non torna indietro (§1.4); il funding alto accompagna i rialzi (§1.5); il
  lunedì e i numeri tondi non hanno nulla (§1.6-1.7);
* «BTC guida, la moneta segue» è un effetto piccolo e di regime, sempre sotto i costi (§1.11);
* tutto si indebolisce fuori dalla costruzione: nessuno dei sette candidati validati ha tenuto l'R di costruzione (§1.13);
* contraddizioni aperte fra campagne (rimbalzo o continuazione dopo un crollo di 4 ore; l'ora o il momento per la fine
  giornata; funding negativo; segno dello squilibrio degli ordini): «dipende dalla moneta, dall'orizzonte o dal periodo»
  (§3).

Idee da non riprovare così come sono (§4): lunedì, numeri tondi, short sul funding alto, ritorno alla media di poche ore,
idee di tendenza giudicate contro zero invece che contro la (b), qualunque idea sotto l'ora con un lordo sotto due giri
di costi.

### 7.2 Le 12 proposte della prova di processo (7 ottobre) e cosa ne è stato

| N. | Proposta (`prova_processo/rapporto.md` §6) | Cosa ne è stato | Fonte |
|---|---|---|---|
| 1 | Campagna di gruppo con i trade contati su più monete | fatta come Passo 4bis della 4.5, 10-11 ottobre, su 80 monete; nessuna strategia | appendice 4; `campagne/GRUPPO/consegna.md` |
| 2 | Regola unica di stima dei trade | 4.4 (`conta_trade`) | appendice 3 |
| 3 | Una sola lettura di «nettamente», 200 simulazioni fisse | 4.4 (`contro_baseline`) | appendice 3 |
| 4 | Controllo positivo obbligatorio in Fase 0 | entrato in `lezioni/metodo.md` come pratica (una nota del log, non una regola) | `lezioni/metodo.md`, «Il metodo»; `PROTOCOLLO.md` §6 |
| 5 | In Fase 2 anche R per anno e «senza i 3 migliori» | 4.4, Fase 2 punto 1 | `PROTOCOLLO.md`, Fase 2 |
| 6 | Caricatore unico per last e mark | 4.5 (`carica_serie_allineate`) | appendice 4 |
| 7 | Nota di apertura delle sessioni | 4.5 (`apertura/campagna.md`) | appendice 4 |
| 8 | Divisione 70/30 sul periodo utile | non adottata: le date restano quelle scritte prima, la differenza si dichiara | `lezioni/metodo.md`, «I dati» |
| 9 | Tetto di due varianti per fonte | entrato in `lezioni/metodo.md` e richiamato dal budget | `PROTOCOLLO.md` §3.4 |
| 10 | Durata e budget non speso dal log | 4.5, «Misure di processo» | appendice 4 |
| 11 | Candidato «debole» (sopra il 90° percentile ma non netto) | no (raccomandazione del rapporto) | rapporto §6 punto 11 |
| 12 | Fascia di slippage per anno | non adottata nella 4.x; riproposta al Passo 7 (proposta 7 qui sotto) | `lezioni/metodo.md`, proposte |

Oltre a queste, il proprietario ha scelto il **minimo da 100 a 70 trade** e il **budget per intero**, e di **rifare** le
tre campagne invece di tenerle (il rapporto raccomandava di non rifarle) (rapporto §9).

### 7.3 Le 12 proposte del Passo 7 (12 ottobre) e cosa ne è stato

Elencate in `lezioni/metodo.md`, «Proposte che toccano una regola del protocollo…», «non decise». Cosa ne è stato nei
protocolli successivi (`PROTOCOLLO_2.md`, approvato il 13 ottobre; `PROTOCOLLO_3.md`, approvato il 16 ottobre;
`PROTOCOLLO_4.md`, approvato il 17 ottobre):

| N. | Proposta | Numero che la sostiene | Dopo |
|---|---|---|---|
| 1 | Verifica con lo stop a distanza fissa, o una (b) con la stessa distribuzione della distanza dello stop | BTC V11 3,01 → 1,01; LTC 027 1,95 → 0,01; ADA 6 su 6; FIL 025 1,38 | **adottata** nel protocollo 3: entrate casuali «con la stessa distribuzione di larghezza dello stop del candidato» (5 fasce), correzione 1 del collaudo, 17 ottobre; tenuta nel protocollo 4 (`PROTOCOLLO_3.md` §10.1 e appendice 3; `PROTOCOLLO_4.md`; `CHANGELOG.md`, riga del 2026-10-17) |
| 2 | (b) ristretta alle barre del filtro | ADA t 0,63; 1000SHIB t che cresce a costi doppi | non trovata nei protocolli 3 e 4 (le entrate casuali sono scelte fra tutte le candele ammesse); da verificare |
| 3 | Ordine dei ritocchi (escludere le varianti con lordo sotto i costi; non insistere su una famiglia smontata; 5+5 ritocchi) | BTC V19; LTC 014; DYDX, FIL, SOL, ETC, MASK, GRUPPO | in parte: la seconda edizione riduce a 18 varianti e 3 ritocchi per famiglia, 12 in tutto (`PROTOCOLLO_2.md` §2); il protocollo 3 tratta ogni filtro nuovo come una variante che consuma un tentativo, con un limite di 40 (`PROTOCOLLO_3.md` §8.3) |
| 4 | Test del ritardo: controllo diretto del lookahead, e cosa fare con le regole legate all'ora | AVAX V-14 a 0,494; FIL 7 candidati | **adottata**: nel protocollo 3 il ritardo diventa «informativo, non decide» (§9.9) |
| 5 | Stabilità: almeno due anni con 10 trade | XRP 84 trade su 97 nel 2020 | in parte: nel protocollo 3 la stabilità si misura su quattro blocchi di tempo (R positivo in almeno 3 su 4, nessun blocco oltre il 50% della somma) (`PROTOCOLLO_3.md`, Fase 4, verifica 3) |
| 6 | R senza i 3 migliori anche in validazione | ADA +0,624 → +0,014 | non trovata come tale; nel protocollo 3 la validazione chiede almeno 60 trade, R positivo, almeno metà dell'R di costruzione, profit factor 1,05 e R positivo a costi doppi (`PROTOCOLLO_3.md`, tabella delle soglie, riga «Validazione»); in costruzione si tolgono i migliori 5% dei trade (verifica 4) |
| 7 | Slippage per anno | BCH 0,05% contro 0,02%; TRB 0,10% contro 0,02% | non trovata (il protocollo 3 lavora su BTC con 0,01%) |
| 8 | Tetto dello stop misurato dall'ingresso atteso o al 5,9% | XRP, 1000SHIB | nel protocollo 3 le distanze di stop si calcolano dal prezzo di ingresso effettivo (`PROTOCOLLO_3.md`, riga 249); il 5,9% non risulta |
| 9 | Previsione numerica nella registrazione della validazione | BTC N018 | il formato del log del protocollo 3 ha il campo «previsione» con numeri (esempio a riga 534); da verificare se è obbligatorio |
| 10 | Prova di causalità per troncamento | SOL, MATIC, TRB, GALA, AVAX | **adottata**: «test di troncamento» (`PROTOCOLLO_3.md` §9.8; `PROTOCOLLO_4.md` §9.8) |
| 11 | Test paralleli con blocco del file | GALA | non verificata |
| 12 | Candidato «debole» | gruppo con molte varianti al 99-100° percentile non nette | non adottata |

### 7.4 Altre conseguenze dirette di questa stagione

* **Costi e ordini limite**: la prova del 13 ottobre su nove strategie delle campagne (parità con i log 13 volte su 13):
  costo medio da 0,062 a 0,039 R, eseguito il 98% degli ordini, ma i trade saltati (2,4%) erano i migliori (R +0,68);
  esito «conviene poco» (`esperimenti/ordini_limite/risultati.md` §2). Il 13 ottobre gli ingressi a ordine limite sono
  entrati comunque nel paper (commit 6d50adfa) e nella seconda edizione (diario r. 3627).
* **Ricerca automatica del gate fermata** il 13 ottobre (`ops/gate_fermo`, commit 4c315e80). L'analisi dei trade del
  paper del 12 ottobre aveva scritto che i dati «per il gate chiedono cambiamenti strutturali (controllo con entrate
  casuali, correzione per i tentativi, fuori campione vero, costi per moneta, un solo regime, niente figlie dai
  quasi-passaggi): cioè il protocollo, che ha dato zero su 630» (diario r. 3594; la decisione al r. 3627).
* **Seconda edizione** (`PROTOCOLLO_2.md` §1-2): candele giornaliere, paniere delle 80 monete del gruppo, poche idee con
  fonte, taglio comune al 2023-01-16, vault 2024-2026 «dichiarato, non rifatto», paper come esame finale. La motivazione
  cita direttamente i numeri di questa stagione.

### 7.5 Errori da non ripetere (sintesi di questa bozza, con le fonti sopra)

Per chi riscrive il gate o un nuovo protocollo:

1. **Non confrontare una regola con entrate casuali che hanno uno stop diverso**: uno stop agganciato a un livello
   rende «netta» una regola senza direzione (sezione 5.3).
2. **Calcolare il costo di un giro in R prima di scegliere il timeframe** e chiedere un lordo di almeno due giri: sotto
   l'ora nessuna idea ha retto (sezioni 3.D, 7.1).
3. **Leggere un candidato nato da ritocchi come il migliore di 5-7 tentativi**: 34 candidati su 45 venivano da ritocchi
   e nessuno ha superato il vault (sezione 4.8).
4. **Non fidarsi di pochi trade**: in validazione 3 trade facevano l'R di ADA-037 (+0,624 → +0,014) (sezione 2.5).
5. **Scrivere prima i casi limite delle regole** (netta ma in perdita; R in validazione; ritardo per le regole
   all'orologio; uscite senza tempo nel gruppo): ognuno ha fermato una campagna (sezioni 2.3 e 5.2).
6. **Tarare l'esame su prezzi veri con strategie finte** prima di usarlo, e scrivere soglie e conseguenze prima: la prova
   a placebo ha trovato un errore prima del lancio e ha dato un numero per il trasferimento (sezione 4.4).
7. **Misurare la potenza, non solo i falsi positivi**: l'esame era più severo del dichiarato (deviazione dei t 0,815 per
   moneta, degli z 0,67 nel gruppo) e i trade di 80 monete valevano un dodicesimo (sezioni 4.4 e 4.6).
8. **Tenere separati i periodi anche fra monete**: con monete che si muovono insieme, la validazione di una può cadere
   nella costruzione di un'altra (sezione 5.1, riga del 10 ottobre).

---

## 8. Cosa resta incerto in questa bozza

* **Versioni prima della 4.3**: la «versione 2 in PDF» del 3 ottobre e la «v3» citata nell'appendice 1 non sono nel
  repository; della 4.2 restano solo le modifiche elencate nell'appendice 1. Non ho potuto ricostruirne il testo.
* **Scarti**: `confronto/risultati.md` scrive 197, la sua tabella per campagna e i log ne danno 187 (sezione 2.2).
* **Distribuzione dei t**: il coordinamento scrive media 0,46 e 71 nette contro la (b) su 600; il mio conteggio dai log
  dà 0,43 e 65 (sezione 3, introduzione). Non so quale campo abbia letto il coordinamento.
* **Durate delle campagne 4.5**: «25-85 minuti» (diario), «25-80» (`confronto/risultati.md`), 26-75 più FIL 146 con 92
  di pausa (mio conteggio dai log).
* **ADAUSDT**: la consegna conta 3 varianti nette con R non positivo (009, 024, 038), ma nel log ADAUSDT-009 non è netta
  contro la (a) (t 1,94); il riepilogo del coordinamento ne conta 2.
* **Idee della prova di processo di ETHUSDT**: 22 idee (consegna sul branch di archivio) o 23 (rapporto).
* **Famiglie**: l'assegnazione delle idee alle famiglie è una scelta (del coordinamento e mia); per 4 famiglie i miei
  totali differiscono da quelli del coordinamento di 2-6 varianti.
* **Sezione 7.3**: lo stato delle proposte 2, 6, 7, 8, 9 e 11 nei protocolli successivi l'ho controllato solo cercando
  parole nei testi di `PROTOCOLLO_2.md`, `PROTOCOLLO_3.md` e `PROTOCOLLO_4.md`; «non trovata» non vuol dire «esclusa».
* **Orari**: il file d'apertura del vault ha nell'intestazione «19:25 UTC», il commit e `vault/risultati.md` dicono
  19:26.
