# Revisione: la sezione «esecuzioni, commissioni e funding del demo» nella fotografia dello stato — 12 novembre 2026

## Riepilogo e verdetto

**REQUEST CHANGES**, per due cambi piccoli. Non ci sono Bloccanti né Alti. C'è un Medio (79) e due Bassi (80, 81).

La sezione non può mandare ordini né toccare il conto vero:
- usa solo `GET` firmati su tre indirizzi (più l'ora di Binance);
- passa da `ClienteDemo`, che accetta solo `demo-fapi.binance.com`, con le chiavi del demo;
- non scrive niente su Firebase;
- un suo errore non rompe lo «stato».

Il problema è l'ora. La richiesta «stato» parte **ogni giorno alle 00:24 UTC**:
- `ops/results/0731-10nov-stato-ribilancio-1000.md`, `0733-11nov-…`, `0735-12nov-…`;
- è dentro l'ora degli ordini limite del ribilancio di G1 (00:05-01:05, poi il resto a mercato).

La sezione aggiungerebbe lì circa 300-550 di peso, sullo stesso indirizzo del bot del demo.

Il conto dice che non basta per un blocco, se il demo ha il limite di 2.400 al minuto, che però nessuno ha misurato. Ma:
- su un 429 il cliente del demo riprova tre volte;
- su un 418 con un'attesa breve riprova durante il blocco.

Un blocco dell'indirizzo ferma il bot del demo per tutta la sua durata, senza protezioni (`docs/conto_vero.md:74`). La finestra vietata costa niente.

## Oggetto

- Branch `claude/brave-albattani-1b12fv`, modifiche non committate su HEAD `6785d17`:
  - `scripts/state_snapshot.py` (+349: `sezione_demo_esecuzioni`, chiamata in `build()` a `:119`);
  - `tests/test_demo_esecuzioni.py` (nuovo, 8 test).
- Percorso degli ordini: nessuna riga cambiata. La sezione legge il conto demo con il cliente del demo.
- Gira:
  - sulla macchina con la richiesta «stato» (`ops/allowlist.example:25`, `--no-write`; vale dal primo `git pull`, senza riavvio);
  - nel flusso di GitHub `snapshot.yml`, che però non ha le chiavi del demo e scrive «non letto: manca la chiave».

## Checklist A–F

- **A.** Limiti fissi e interruttori: non toccati. **NON APPLICABILE.**
- **B.** Ordini: la sezione non ne manda.
  - `SoloLettura` (`state_snapshot.py:818-842`) rifiuta prima di partire tutto ciò che non è `GET` su `userTrades`, `commissionRate`, `income`, `time`.
  - Test `test_la_funzione_di_sola_lettura_rifiuta_ordini_e_altri_indirizzi`: `POST /order`, `DELETE /allOpenOrders`, `GET /v2/account`, `POST /leverage`, `GET /openOrders` rifiutati, 0 chiamate.
  - L'indirizzo resta quello del demo (`ClienteDemo._url`); le chiavi sono `BINANCE_DEMO_*` (`:965-970`).
  - **OK.**
- **C.** Resilienza:
  - ogni eccezione diventa la riga «non letto» (`:973-983`);
  - un limite di Binance, un errore di rete o un rifiuto fermano tutte le richieste dopo (`_Lettore` `:854-890`; `LimiteBinance` non è un `RuntimeError`, quindi si ferma davvero);
  - tre errori di Binance di fila fermano le esecuzioni;
  - tetto di 180 s, controllato prima di ogni richiesta.
  - **OK**, salvo l'ora (**PROBLEMA 79**) e i ritentativi su 429 e 418 (**PROBLEMA 80**).
- **D.** Paper, demo, conto vero: solo il demo, in sola lettura; il conto vero non è raggiungibile. **OK.**
- **E.** Segreti:
  - gli errori passano da `senza_firma` (`_motivo`);
  - l'errore della chiave stampa solo il tipo (`:994-996`);
  - test con chiave e segreto finti, che non compaiono nell'uscita (nemmeno «signature»).
  - Il resto dell'uscita sono numeri del conto demo (soldi finti) e pesi del paper, già pubblici nel repository.
  - **OK.**
- **F.** Test:
  - `tests/test_demo_esecuzioni.py`: **8 passed**;
  - `python3 -m pytest tests/ -q`: **2777 passed, 1 failed in 191 s**; il fallito è la firma, colpa della libreria del contenitore (passa con la libreria buona, già provato oggi).

## Prove del revisore (`giro12nov/prova_esecuzioni.py`)

1. **Demo realistico** (45 monete, funding ogni 8 ore per 6 giorni, 2 esecuzioni al giorno per moneta): 48 richieste, peso 305, 46 righe, **3.143 caratteri**. La riga del peso è a 3.002 caratteri dall'inizio della sezione.
2. **429 a ogni richiesta:** 4 richieste (1 + 3 ritentativi del cliente, attese 1, 2, 4 s), poi la sezione si ferma e lo «stato» continua.
3. **418 con Retry-After di 5 s:** 4 richieste durante il blocco (attese 5, 5, 5 s). Chi riprova durante il blocco lo allunga, da 2 minuti fino a 3 giorni (`demo_binance.py:96-97`).

## Le verifiche chieste

- **Ordini e conto vero:** impossibile, vedi B e D.
- **Peso e blocco dell'indirizzo:** vedi 79 e 80.
- **Un errore della sezione non rompe lo «stato»:** test `test_un_errore_di_binance_non_ferma_lo_stato`, con un cliente che solleva `KeyError` e Firebase che non risponde: la sezione resta una lista di righe. **OK.**
- **Niente di sensibile nel repository pubblico:** vedi E. **OK.**
- **Limite dei 20.000 caratteri:** vedi 81.

## Problemi

### 79 — Medio — Nessuna finestra vietata: la lettura parte nell'ora degli ordini limite del demo

- **Dove:** `state_snapshot.py:973-983` (nessun controllo dell'ora); la richiesta «stato» di ogni giorno è alle 00:24 UTC.
- **Scenario:**
  - alle 00:24 il demo ha 40-80 ordini limite sul libro e alle 01:05 manda il resto a mercato;
  - la sezione chiede 48-80 richieste (peso 300-550) allo stesso indirizzo;
  - con il limite del demo non misurato, o un altro programma della macchina sullo stesso indirizzo, arriva un 429;
  - il cliente riprova (80), fino a un 418;
  - il bot del demo rispetta tutto il blocco e in quel tempo non controlla lo stop sul conto e non manda il resto a mercato.
- **Correzione:** fra le 23:50 e le 01:45 UTC nessuna richiesta e la riga «non letto: finestra del ribilancio del demo (23:50-01:45 UTC), richiedere dopo». La finestra copre la decisione delle 00:05, l'ora degli ordini limite e il tentativo dopo un errore (30 minuti). Lo «stato» delle 00:24 resta com'è; la sezione si legge con uno «stato» dopo le 01:45. Test con l'ora.

### 80 — Basso — Su 429 e 418 il cliente del demo riprova tre volte

- **Dove:** `demo_binance.py:483-493` (riprova i 429, e i 418 con un Retry-After fino a 10 s). La sezione lo usa così com'è (`state_snapshot.py:965-970`). Prove 2 e 3: 4 richieste ciascuna, la 3 durante un blocco.
- **Correzione:** `SoloLettura` sollevi un'eccezione sua (non `RuntimeError`) al primo 429 o 418, prima che il cliente riprovi. La sezione si ferma al primo segnale. Test.
- Consiglio, insieme: finché il limite del demo non è misurato, `PESO_USATO_MASSIMO` (`:811`) a 600 invece di 1.200.

### 81 — Basso — Con i 20.000 caratteri la coda della sezione rischia il taglio

- **Dove:** l'agente tiene i primi e gli ultimi 10.000 caratteri (`ops_agent.py:79-86`).
- **Misura:** l'ultimo «stato» è già lungo 46.000 caratteri e ne perde 26.469 (`0735-12nov-stato-ribilancio-1000.md`). La sezione nuova entrerebbe a circa 6.420 caratteri, dopo il conto vero. Con 3.143 caratteri la sua ultima riga (richieste e peso usato, quella che serve per controllare 79) finirebbe a circa 9.560: dentro di poco. Se le sezioni prima crescono di 500 caratteri, il peso usato sparisce nel taglio.
- **Correzione:** la riga «richieste, peso, peso usato dall'indirizzo» subito sotto il titolo della sezione. Facoltativo: tagliare la lista delle monete assenti a 10.

## Invarianti modificati

Nessuno del percorso degli ordini. Nuovo: la fotografia dello stato legge il conto demo in sola lettura con la chiave del demo (prima nessuno script fuori dal bot usava quella chiave per il conto demo).

## Decisioni per Alessio

Nessuna nuova. La sezione serve a misurare la commissione vera e il funding del demo, per la revisione di G1 (problemi Alti 1 e 4 di `audits/reports/2026-11-12-G1_CONTO_VERO.md`).

## Domande aperte

- Il limite di peso al minuto del conto demo di Binance: è lo stesso del conto vero (2.400)? Lo dirà la prima lettura, fuori dalla finestra, nella riga «peso usato dall'indirizzo».
- Sulla macchina, altri programmi chiamano `demo-fapi.binance.com` con lo stesso indirizzo (oltre al bot)?

## Secondo giro (12 novembre, sera): APPROVE

79, 80, 81 chiusi, verificati sul codice nuovo. Test: `tests/test_demo_esecuzioni.py` 18 passed; suite intera 2787 passed, 1 failed (la firma).
- **79:** nessuna richiesta dalle 23:50:00 alle 01:44:59 UTC, anche a cavallo della mezzanotte (controllo con il resto della divisione per un giorno, `state_snapshot.py:828-830`, `:1006-1007`). Prova: 0 richieste alle 23:50, 23:59:59, 00:00, 00:05 e 01:44:59, e con l'ora vera alle 00:30; 48 richieste alle 01:45; 23:49:59 fuori. La finestra si controlla solo all'inizio: una sezione partita alle 23:49:59 può durare fino a circa 3 minuti e mezzo, ben prima delle 00:05. Va bene.
- **80:** al primo 429 o 418 il filtro solleva `LimiteInLettura` prima che il cliente riprovi (`:852-855`). Prova: 1 sola richiesta, nessuna attesa (prima 4 richieste e attese di 1, 2, 4 s). Un solo caso resta: un errore d'orario seguito da un 429 sulla rilettura dell'ora lascia partire un'altra richiesta, perché il cliente non fa uscire l'errore della rilettura. Raro e innocuo.
- **Soglia:** 600 (`:811`).
- **81:** la riga del peso è la seconda della sezione (`:1154`): a 82 caratteri dal titolo, prima a 3.002. Le monete assenti sono al massimo 10, con «e altre N».
