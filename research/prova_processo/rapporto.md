# Rapporto della prova di processo (Passo 2, punto 4)

Scritto il 7 ottobre 2026 dalla sessione di coordinamento, sul branch `research/coordinamento`,
a tre campagne consegnate: BTCUSDT, ETHUSDT, SOLUSDT. Il protocollo è la versione 4.3.

**Cosa ha letto il coordinamento per scrivere questo rapporto:** i titoli dei commit dei tre
branch di campagna, le date dei commit e delle voci del log, i conteggi delle voci del log per
tipo (senza il testo delle ipotesi), i campi di processo del log (durata, budget, correzioni,
controllo degli strumenti, buchi nei dati, stime dei trade degli scarti, anno della fonte), la
prima riga di ogni `consegna.md`, le tre `lezioni_metodo_proposte.md`, `CHANGELOG.md` e i dati
delle sessioni (durata, costo). **Non ha letto** `ipotesi.md`, `lezioni_moneta.md` né il corpo
delle consegne: il merito delle idee resta chiuso fino al Passo 7, come vuole il protocollo.

## 1. Esito in una riga

Il processo regge: tre campagne complete, log in aggiunta, consegne scritte, periodo di
validazione mai toccato, vault chiuso. **Nessuna delle tre campagne ha trovato una strategia
valida** (prima riga delle tre consegne). Il motivo principale non è il budget né gli strumenti:
è che la ricerca su una moneta sola, con 100 trade minimi per direzione, scarta le idee lente
prima di provarle e non ha abbastanza trade per confermare quelle che mostrano un segnale.
La sezione 5 spiega perché e la sezione 6 propone cosa cambiare.

## 2. Le tre campagne in numeri

| | BTCUSDT | ETHUSDT | SOLUSDT |
|---|---|---|---|
| Sessioni | 1 | 2 (la prima persa, vedi 4.1) | 1 |
| Orologio (dal primo all'ultimo commit di campagna) | 06:40 → 07:34 UTC, 55 minuti | 10:33 → 13:33 UTC, 3 ore (più 17 minuti persi, 08:43 → 09:00) | 08:43 → 09:39 UTC, 56 minuti |
| Commit di campagna | 6 | 25 | 18 |
| Voci del log | 92 | 81 | 56 |
| Idee registrate (scarti + varianti) | 15 | 23 | 13 |
| Idee con almeno una variante testata | 10 | 13 | 10 |
| Varianti testate sul budget di 30 | 16 (più 12 verifiche di Fase 4 su una variante) | 23 | 17 |
| Budget non speso | 14 | 7 | 13 |
| Scarti per stima dei trade | 11 | 22 | 11 |
| Correzioni nel log | 0 | 1 (regola di stima dei trade) | 1 (campo «solo BTC» di 3 risultati) |
| Candidati arrivati alla validazione | 0 | 0 | 0 |
| Costo della sessione (equivalente in dollari) | 15,8 | 5,8 + 22,7 = 28,5 | 17,8 |

Fonti: commit dei branch `research/campagna/<SIMBOLO>`; `log.jsonl` di ogni campagna (conteggi
per tipo e campi di processo); dati delle sessioni di campagna. Totale: 56 varianti testate, 44
scarti, 51 idee, 62 dollari, circa 5 ore di orologio di campagna.

Nota sulla durata di BTCUSDT: la nota di consegna nel log dice «circa 2 ore e 40 minuti», ma il
primo commit di campagna è delle 06:40 e la consegna delle 07:34, e la sessione è stata creata alle
06:39 e si è fermata alle 07:34. La durata vera è 55 minuti. Lezione piccola: la durata si ricava
dalle date del log, non a memoria (sezione 6, punto 10).

### Dove hanno cercato (timeframe e direzione delle registrazioni)

| Timeframe | BTCUSDT (28 registrazioni, verifiche comprese) | ETHUSDT (23) | SOLUSDT (17) |
|---|---|---|---|
| 30 minuti | 2 | 0 | 0 |
| 1 ora | 2 | 14 | 14 |
| 4 ore | 6 | 6 | 3 |
| 8 ore | 13 | 1 | 0 |
| 12 ore | 1 | 0 | 0 |
| 1 giorno | 4 | 2 | 0 |

Direzione: BTCUSDT 10 long e 6 short; ETHUSDT 10 long e 13 short; SOLUSDT 9 long e 8 short.
Fonte: campi `timeframe` e `direzione` delle registrazioni nei tre log.

### Dove sono finiti gli scarti (tutti e 44 per stima dei trade sotto 100)

| Timeframe | BTCUSDT | ETHUSDT | SOLUSDT | Totale |
|---|---|---|---|---|
| 1 ora | 2 | 2 | 6 | 10 |
| 4 ore | 3 | 14 | 5 | 22 |
| 8 ore | 1 | 1 | 0 | 2 |
| 12 ore | 0 | 1 | 0 | 1 |
| 1 giorno | 5 | 4 | 0 | 9 |

34 scarti su 44 sono a 4 ore o più lente. Delle 44 stime, 28 erano fra 50 e 99 trade e 16 fra 70 e
99: la metà delle idee scartate era «quasi» al minimo. Fonte: campi `motivo` e `trade_stimati`
degli scarti nei tre log.

### Le fonti delle idee

Tutte le registrazioni citano una fonte anteriore al 2024, come chiede la Fase 1. L'anno più
antico citato per registrazione: BTCUSDT da 1978 a 2022 (7 fonti su 16 dal 2017 in poi, cioè
specifiche delle crypto); ETHUSDT da 1985 a 2022 (9 su 23 dal 2018 in poi); SOLUSDT da 1985 a
2019 (4 su 17 dal 2018 in poi). Fonte: campo `fonte` delle registrazioni. Le tre campagne hanno
chiuso prima del budget dicendo la stessa cosa: le famiglie di idee con una fonte citabile e un
meccanismo nuovo si sono esaurite, e il resto del budget sarebbe andato in soglie o timeframe
diversi di idee già fallite, cioè selezione sul risultato (note di chiusura di BTCUSDT ed ETHUSDT;
SOLUSDT ha 13 varianti non spese). **Il budget di 30 non è il collo di bottiglia: lo è la scorta
di idee con fonte.**

## 3. Problemi di protocollo (cose che tre campagne hanno interpretato in tre modi)

1. **La stima dei trade non ha una regola unica.** BTCUSDT ha usato un'occupazione dichiarata
   variante per variante (e per una variante la stima non è stata un limite inferiore: 100 stimati,
   72 veri; per un'altra lo è stata in eccesso e l'ha scartata). ETHUSDT ha iniziato con «distanza
   fra segnali almeno H» e ha dovuto aggiungere a metà campagna, con una correzione nel log, una
   seconda regola per le uscite su segnale (la prima sottostimava di 2-3 volte). SOLUSDT ha misurato
   la durata con entrate casuali con la stessa uscita: con la durata «a occhio» (20 barre) un'idea
   dava 83 trade, con quella misurata (9 barre) 105. **La stessa idea passa o non passa la soglia
   dei 100 secondo una regola che oggi sceglie la campagna.** (BTC 1, ETH 2, SOL 2.)
2. **«Nettamente» ha due letture.** Lo strumento `differenza_nettamente` confronta il candidato con
   UNA corsa casuale (la mediana) sommando due errori: SOLUSDT lo ha applicato come registrato e per
   tre volte ha detto «non netto» a un candidato sopra tutte e 200 le simulazioni; per una variante
   la versione a un campione diceva «netta» e quella a due «non netta». ETHUSDT ha riportato sia il
   percentile fra le 200 strategie casuali sia il bootstrap a blocchi, e ha trovato che dicono cose
   diverse (4 varianti su 23 sopra il 97° percentile, nessuna oltre 1,5 errori standard a blocchi).
   BTCUSDT ha chiuso una variante al 96° percentile «non netta» senza un posto nel protocollo per un
   risultato così. (SOL 1, ETH 7, BTC 3.)
3. **Il numero di simulazioni casuali in costruzione non è fissato.** BTCUSDT ne ha usate 100 (50 a
   30 minuti per il tempo di calcolo), le altre due 200. Il protocollo fissa `simulazioni_caso` solo
   per il vault. (BTC 7.)
4. **Le idee lente non arrivano a 100 trade per direzione su una moneta sola.** Un ingresso a
   settimana in 143 settimane di costruzione dà al massimo 143 trade in tutto, cioè sotto il minimo
   per direzione per costruzione, non per dati (ETH 3). Il protocollo lo dichiara nei limiti noti
   (sezione 11) e prevede una regola a parte «contando i trade di più monete insieme, scritta prima
   dei numeri»: la regola non c'è ancora. È il punto della sezione 5.
5. **La divisione 70/30 è calcolata sul listing, non sul periodo utile.** Su SOLUSDT il 2020 è sotto
   la soglia di liquidità e il rapporto vero è 67/33 (SOL 7).
6. **Il controllo «senza i migliori trade» arriva solo in Fase 4**, dove non si arriva se la Fase 2 si
   giudica sul totale: su SOLUSDT tre trade facevano un profit factor di 1,6 su 160 (SOL 6). Lo stesso
   per «R per anno»: con due anni di segno opposto il totale non dice niente (SOL 5).
7. **Previsioni al lordo dei costi.** Su ETHUSDT le previsioni a 1 ora erano ottimiste di 0,1-0,3 di
   profit factor perché non contavano 0,12 % per giro su durate di 1-4 ore (ETH 9).
8. **Una fonte, quattro varianti.** Due direzioni per due condizioni dalla stessa fonte alzano la
   probabilità di un falso positivo dentro un'idea sola (ETH 10).

## 4. Problemi di strumenti e di dati

### 4.1 Strumenti della piattaforma e del coordinamento

- **Sessione nata senza il repo fra le sorgenti.** La prima sessione ETHUSDT, creata con la stessa
  chiamata che aveva funzionato per BTC e SOL, non poteva pushare (403): 17 minuti e 5,8 dollari persi.
  Rimedio applicato: nuova sessione con la sorgente passata esplicitamente e l'istruzione di
  fermarsi se il primo push fallisce. Regola per il coordinamento: passare sempre la sorgente e il
  branch di partenza, controllare il primo push entro mezz'ora.
- **Il guardiano legge la shell, non le intenzioni.** Su ETHUSDT nove rifiuti, nessuno su una lettura
  davvero vietata: la parola `.venv` in un comando, `python3 -c`, un testo con virgolette triple, un
  messaggio di commit su più righe, `$?`, `2>&1`, la cartella madre `data/insample/`, la parola «bot»
  dentro un testo, la lettura di `src/guardiano.py`. Circa mezz'ora persa (ETH 1). Su BTCUSDT e SOLUSDT
  nessun rifiuto registrato. Rimedio: nota di apertura con le regole pratiche (file e testi con lo
  strumento di scrittura, messaggio di commit in un file e `-F`, comandi semplici senza redirezioni).
- **Test di GitHub rossi per 12 esecuzioni** (dalle 07:38 alle 10:05 UTC): un test del revisore
  importava `yaml` senza `pyyaml` fra le dipendenze. Corretto sul principale e portato sul branch BTC
  (`CHANGELOG.md`, 7 ottobre). Non ha toccato i risultati delle campagne.
- **Gli id del log sono progressivi su un file solo**: due lotti lanciati in parallelo possono
  prendere lo stesso id (ETH 12). Le campagne hanno lavorato in serie; da scrivere nella nota di apertura.

### 4.2 Motore e caricatore (`research/src/`)

- **Il mark price ha buchi che il last non ha**, e in giorni diversi: BTCUSDT 770 barre a 15 minuti
  in 7 buchi (nota F0-03 del log); ETHUSDT due giorni interi (2 ottobre 2022, 24 febbraio 2023);
  SOLUSDT 5 giorni il last e 7 il mark nel 2021-2023. Il motore vuole serie allineate: ogni campagna
  ha scritto da sé la regola di riempimento o di intersezione (tre codici diversi per lo stesso
  problema). Va dentro `src/dati.py` con le barre tolte dichiarate (BTC 6, ETH 4, SOL 4).
- **Il campo volume delle candele è in moneta base**, non in USDT: per il volume in USDT serve
  `quote_volume` dagli zip o volume per chiusura. Da esporre nel caricatore (ETH 6).
- **I dati di riferimento BTC vanno scaricati sugli stessi timeframe della moneta** prima della
  Fase 2: su SOLUSDT il controllo «è solo BTC» è uscito vuoto a 4 ore (SOL 3).
- **Il motore è lento a 1 ora e sotto** (fetta delle candele a ogni barra): un esame con 100
  simulazioni dura circa 5 minuti a 1 ora, 8 a 30 minuti con 50 (BTC 8).
- **La fascia di slippage calcolata sul 2023 è ottimista per il 2020**: su ETHUSDT il volume medio
  del 2020 era 723 milioni al giorno con minimi di 45 milioni, cioè 0,02-0,05 % per lato invece di
  0,01 % (ETH 5).
- **`fase0_dati.md` con 760 impronte dentro pesa 894 righe** su SOLUSDT: meglio un `impronte.json`
  accanto, con il suo hash nel file (SOL 8).
- **Un controllo positivo degli strumenti** (una strategia con lookahead dichiarato che deve
  risultare nettamente sopra il caso e crollare col ritardo di una barra) è stato fatto solo su
  ETHUSDT, ha funzionato (30 errori standard, poi profit factor 0,8) ed è costato dieci minuti (ETH 8).

Nessuna campagna ha corretto `src/`: le tre correzioni di processo sono tutte nel codice di campagna.

## 5. Come abbiamo cercato, e perché così non si trova

Il proprietario ha chiesto: «forse stiamo cercando male». La risposta, con i numeri sopra:

1. **La ricerca per moneta singola con 100 trade per direzione esclude le idee lente prima di
   provarle.** 34 scarti su 44 sono a 4 ore o più lente, 9 a candele giornaliere; la metà delle
   stime era fra 50 e 99 trade. Un'idea che entra una volta a settimana non può arrivare a 100 per
   direzione in tre anni su una moneta: la esclude l'aritmetica, non i dati (sezione 3, punto 4).
2. **Quando una variante mostra un segnale, una moneta sola non ha i trade per confermarlo.** Con R
   medi di 0,05-0,10 e deviazioni di 0,5-0,7 R per trade, l'errore standard della differenza è
   0,06-0,13: per rendere «netto» un vantaggio vero di 0,08 R servono 300-500 trade, non 100-150
   (BTC 2). Infatti 8 varianti su 56 sono finite sopra il 96°-97° percentile delle entrate casuali
   (1 su BTCUSDT, 4 su ETHUSDT, 3 su SOLUSDT; per caso se ne aspettano circa 2) e nessuna ha superato
   i 2 errori standard a blocchi. Non è una prova che ci sia qualcosa, perché il percentile conta
   come indipendenti trade che non lo sono (ETH 7); è il segno che il test, così com'è, può quasi
   solo scartare.
3. **Le campagne si sono fermate per mancanza di idee con fonte, non per budget**: 34 varianti su 90
   non spese. Allargare il budget a 30 varianti piene non cambia niente se le famiglie di idee sono
   le stesse. Le fonti citate sono per lo più studi generali di finanza (1978-2012); quelle specifiche
   delle crypto sono 20 su 56 registrazioni.
4. **Tre campagne hanno fatto tre ricerche con tre regole di stima e due letture di «nettamente».**
   Senza regole uniche, un'idea passa su una moneta e cade su un'altra per il metodo, non per il mercato.
5. **Cosa NON è emerso come problema:** il vault è rimasto chiuso, nessuna campagna ha letto le
   altre, il log in aggiunta ha retto 229 voci, le consegne dicono «non trovato» invece di forzare un
   candidato. Il protocollo protegge dal falso positivo; oggi non è attrezzato per trovare il vero
   positivo piccolo e lento.

## 6. Proposte di modifica al protocollo, in ordine di importanza

Da decidere dal proprietario allo STOP. Ogni proposta dice se, adottata, obbliga a rifare le tre
campagne della prova (regola del Passo 2: si rifanno se il cambiamento tocca punti che riguardano
le loro monete).

1. **Campagna di gruppo (nuovo tipo di campagna, Passo 3-bis).** Un'idea con fonte si prova sulle
   stesse regole su un gruppo di monete (minimo 3, fino alle 20 selezionate), con i trade contati
   insieme per i minimi (100/30/30 sull'insieme) e i risultati per moneta sempre dichiarati; passa
   solo se il segno regge su almeno 3 monete e supera il controllo «è solo il mercato». Regole di
   stima e di giudizio scritte prima dei numeri, come già prevede la sezione 11. È la risposta ai
   punti 1 e 2 della sezione 5. Costo stimato: una campagna di gruppo come una campagna singola
   grande (20-30 dollari, mezza giornata), perché i dati in-sample delle 20 monete sono gli stessi.
   Le tre campagne della prova restano valide come «ricerca per moneta singola»: non si rifanno.
2. **Regola unica di stima dei trade** (sezione 8): per le uscite a tempo fisso, segnali distanti
   almeno la durata massima della posizione; per le uscite su segnale, durata misurata con entrate
   casuali con la stessa uscita (mai con i risultati del segnale); occupazione = numero massimo di
   barre in posizione. Tocca gli scarti delle tre campagne: **se adottata, le tre campagne vanno
   rifatte** (budget da capo, branch archiviati), salvo che il proprietario decida di non rifarle e di
   usare la regola solo dal Passo 4 in poi. Raccomandazione: adottarla e NON rifare le tre campagne
   singole, perché la prova ha mostrato che la ricerca singola non è il modo di cercare.
3. **Una sola lettura di «nettamente»** (sezione 8): differenza fra l'R medio del candidato e la
   MEDIA della distribuzione delle entrate casuali, oltre 2 errori standard a blocchi del solo
   candidato; il percentile fra le simulazioni si riporta sempre come indizio, mai come prova;
   `simulazioni_caso_costruzione` = 200 fissato in `parametri.yaml`. Stesso effetto sulle campagne
   della prova del punto 2.
4. **Controllo positivo degli strumenti obbligatorio in Fase 0** (la strategia con lookahead
   dichiarato): dieci minuti, chiude l'obiezione «gli strumenti non vedono niente». Non obbliga a rifare.
5. **In Fase 2, oltre al totale: R per anno e «senza i 3 migliori trade»** obbligatori. Non obbliga a
   rifare (le campagne li hanno riportati dove servivano).
6. **Caricatore unico per last e mark** in `src/dati.py`: intersezione delle barre, barre tolte
   dichiarate, `quote_volume` esposto, dati di riferimento BTC su tutti i timeframe ammessi in Fase 0.
   Correzione di strumenti registrata in `CHANGELOG.md`, da fare dal coordinamento prima del Passo 4.
7. **Nota di apertura delle sessioni**: regole pratiche per non farsi rifiutare dal guardiano, lotti in
   serie, sorgente e branch alla creazione, primo push entro mezz'ora. Non tocca il protocollo.
8. **Divisione 70/30 sul periodo utile** (dopo il filtro di liquidità), scritta prima dei prezzi.
9. **Tetto di due varianti per fonte** in costruzione, oppure dichiarazione esplicita nel log.
10. **Durata e budget non speso nella consegna si ricavano dal log** (date delle voci), con il motivo
    del non speso. Il rapporto della prova dice che 30 varianti bastano: nessuna campagna le ha esaurite.
11. **Candidato «debole»** (sopra il 90° percentile ma non netto) in validazione? Raccomandazione:
    **no.** Terrebbe in piedi l'asticella con p-value già deboli; la potenza si recupera con la
    campagna di gruppo, non abbassando il criterio.
12. **Fascia di slippage per anno** per le monete con il 2020 in costruzione; per ora il test a costi
    doppi copre in parte.

## 7. Lezioni di metodo da unire in `lezioni/metodo.md` al Passo 7

Sono le tre `lezioni_metodo_proposte.md`, tutte compatibili con la regola «mai idee, meccanismi o
risultati». Il coordinamento le condivide tutte; quelle che cambiano il protocollo sono nella
sezione 6, le altre (buchi del mark price, volume in moneta base, dati di riferimento, previsioni al
netto dei costi, lotti in serie, pesi dei file) entrano come lezioni. `lezioni/metodo.md` resta
congelato fino al Passo 7, come prevede la sezione 10.

## 8. Cosa decide il proprietario (STOP del Passo 2)

1. Se adottare la campagna di gruppo (proposta 1) e con quali monete: tutte le 20 della lista, o un
   sottoinsieme. `numero_monete_campagna` può scendere, mai salire.
2. Se adottare le regole uniche di stima e di «nettamente» (proposte 2 e 3) e, in quel caso, se
   rifare le tre campagne singole o lasciarle valide com'è raccomandato.
3. Se procedere al Passo 4 con le altre 17 campagne singole così come sono: raccomandazione
   **no, non prima delle proposte 1-3 e 6**, perché costerebbero circa 20 dollari e un'ora l'una e
   troverebbero quasi certamente «nessuna strategia» per gli stessi motivi della sezione 5.
4. Tutte le modifiche al protocollo passano da una nuova versione del `PROTOCOLLO.md` (4.4) e da
   `parametri.yaml`, approvate prima di aprire qualunque campagna.
