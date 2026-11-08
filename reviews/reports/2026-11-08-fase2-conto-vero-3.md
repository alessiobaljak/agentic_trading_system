# Revisione: fase 2 del conto vero, terzo giro (correzioni dei problemi 64-69) — 8 novembre 2026

## Riepilogo e verdetto

**APPROVE per il commit del codice spento** e per il riavvio che lo carica (questo con l'ok di Alessio). **REQUEST CHANGES per
l'accensione**: restano 54 (ii) Alto (decisione di Alessio, già nota), 70 Medio nuovo (con lo stato e la traccia su Firebase persi le
posizioni del bot restano senza stop), il resto del 60 (dashboard, regole) e i Bassi 66 (chiuso in parte), 71, 72. L'accensione
chiede un'altra revisione, dopo la quale si sposta il tag.

Perché il commit del codice spento va bene: con l'interruttore assente e `DRY_RUN` vero il conto vero non fa richieste e non legge
chiavi (test e prova q3 del secondo giro; costruito qui `TradingBot()` con i moduli veri: «spento: manca l'interruttore», 0,0 s); il
demo ha un solo cambio, voluto e provato (stato salvato dopo `parti_da_zero`); `scripts/ops_agent.py` aggiunge due chiamate a GitHub
al minuto (il tag non c'è: `fetch` fallisce, `ls-remote` dà 2) e non può sollevare eccezioni; all'avvio il bot parte anche con
`DRY_RUN` falso. Ricordo che `ops_agent.py` vale sulla macchina dal primo `git pull`, senza riavvio.

## Oggetto

- Modifiche non committate su HEAD `0779553` (codice del percorso = `1a8522f`). Rispetto al secondo giro cambiano solo
  `bot/portafoglio/conto_vero.py` (637 righe), `scripts/ops_agent.py` (`:460`) e `tests/test_conto_vero.py` (969 righe); `config.py`,
  `main.py`, `demo_binance.py` identici al secondo giro (confronto con la copia in `fase2/giro2/`). Copia di questo giro in `fase2/giro3/`.

## Checklist A–F (solo ciò che cambia rispetto al secondo giro; il resto come in `2026-11-08-fase2-conto-vero-2.md`)

- **A.** `hard_limits.py` invariato: OK. Costanti nuove (`conto_vero.py:80-84`, `:95-101`) con test di guardia (`tests/test_conto_vero.py:116-122`):
  OK. Pulsante: funziona anche prima della prima accensione (prova q8: il file `chiudi` chiude). Stop prima della prima accensione:
  spento per scelta (69), PROBLEMA nel caso del 70.
- **B.** Ordini: invariati. OK.
- **C.** Redditi (64): fino a 60 s fa, 15 minuti riletti, doppioni tolti con tipo e `tranId` (`:413-445`); prova q4 rifatta con
  l'orologio finto: la riga posata in ritardo con la stessa ora si conta (−0,9), nessun blocco. Lettura fallita 3 volte → allarme
  `redditi` (q7). Saldo sotto il valore: oltre lo 0,5% (almeno 1 USDT) in 3 letture a un minuto (`_saldo_sotto` `:540-550`). OK.
  Inizio dei redditi all'ora vera dopo le chiusure (`:490`): q5 rifatta, la fase nuova parte da 0, nessun blocco. OK. Firebase muto
  (66): chiuso in parte (sotto). Stato e traccia persi: PROBLEMA (70).
- **D.** Separazione: invariata dal secondo giro (ordini «solo riduzione» con `DRY_RUN` vero se acceso una volta: decisione 1). OK.
- **E.** Tag tolto riconosciuto con `git ls-remote --exit-code` (`ops_agent.py:460`; provato: codice 2 senza il tag). OK. Chi
  approva il tag: 54 (ii), aperto.
- **F.** `python3 -m pytest tests/ -q`: **2688 passed, 1 failed** in 196 s (la firma; con
  `PYTHONPATH=/tmp/claude-0/-home-user-agentic-trading-system/9da12ffe-13c5-5904-8f7e-5ce576103042/scratchpad/cripto` passa). Cinque
  mutazioni a mano: quattro fanno fallire un test (doppioni, tre letture del saldo, ora vera dopo le chiusure, Firebase muto); **il
  ritardo di 60 s tolto non fa fallire niente** (72). Prove del terzo giro in `fase2/giro3/prove_giro3.py` (q4, q4b, q5, q7, q8, r1, r2).

## Stato dei problemi 64-69

| N. | Esito | Evidenza |
|---|---|---|
| 64 | **chiuso** | q4 e q7 rifatte con l'orologio finto (la nota dell'implementatore è giusta: con l'orologio vero e le date di ottobre le mie prove non leggevano i redditi). |
| 65 | **chiuso** | q5: redditi della fase nuova 0,0, capitale 290, nessun allarme. |
| 66 | **chiuso in parte** | Con Firebase muto il «mai acceso» non si tiene (`:335-352`). Ma per quel giro vale lo stesso: prova r1 (pulsante, conto vuoto, file di stato perso, riavvio con Firebase muto al primo giro) → il conto si riarma subito e alla mezzanotte compra senza «riparti» (due ordini limite di apertura). Resta Basso: servono il file perso e Firebase muto proprio al primo giro. Correzione: con Firebase muto e lo stato sconosciuto, niente prima accensione finché Firebase non risponde. |
| 67 | **chiuso** | `ls-remote --exit-code` (codice 2 = il tag non c'è). |
| 68 | **chiuso** | `_da_fermo` (`:466-471`) spegne `stato_perso` al «riparti» accettato. |
| 69 | **chiuso come scelto** | Prima della prima accensione lo stop non chiude (`:459-464`), il pulsante sì (q8). Ha un costo: 70. |
| `conto_non_vuoto` | **ok** | Non si spegne più quando compare un altro motivo (`:527-537`). |

## Problemi

### 54 (parte ii) — Alto, aperto (decisione di Alessio, blocca l'accensione, non il commit)
Invariato: `scripts/ops_agent.py:452-466` porta sulla macchina, forzato, il tag di GitHub; chi può spingere il tag (anche una sessione)
approva il codice dei soldi veri, che gira al primo riavvio (anche un crash). Correzione: tag firmato da Alessio e `git verify-tag` nel
bot, oppure una regola di GitHub che solo lui possa spostarlo.

### 70 — Medio, nuovo — Stato perso e nessuna traccia su Firebase: le posizioni del bot restano senza stop
- Dove: `conto_vero.py:459-464` (senza `acceso_dal` lo stop vale 0), `:335-352` e `_stato_perso` (senza traccia su Firebase il file
  perso vale prima accensione). La traccia è una sola scrittura su Firebase all'accensione (`_scrivi("acceso_dal", …)`), senza
  controllare che sia arrivata (`set_rtdb` restituisce falso se non arriva).
- Prova r2: posizioni del bot aperte, file di stato perso, Firebase senza traccia, perdita del 41%: **nessuna chiusura**; l'unico
  allarme è `ordini_vietati` con «capitale oltre il saldo» (il controllo del conto non vuoto non gira se c'è già un altro motivo).
- Scenario: Firebase non risponde nel minuto dell'accensione (la traccia non arriva) e settimane dopo il file `data/conto_vero.json` si
  perde (ripristino della macchina): il bot vede un conto «non suo», non ordina e non chiude; un crollo arriva fino alla liquidazione.
  Resta solo il pulsante.
- Correzione: tenere lo stop anche prima della prima accensione quando ci sono posizioni (il conto deve essere solo del bot, decisione
  4; il 69 resta una nota per Alessio), e scrivere la traccia su Firebase finché la scrittura non è confermata.

### 60 (resto) — Medio, aperto per la fase 4
Invariato: nessun pulsante né stato del conto vero in dashboard; testata «DRY_RUN · paper»; regole senza il comando.

### 66 (resto) — Basso — Vedi la tabella (prova r1).

### 71 — Basso, nuovo — Il costruttore del conto vero non è protetto in `main.py`
- `bot/main.py:506` crea `ContoVeroG1` senza `try`: un'eccezione nel costruttore (per esempio in `file_caricati` con un modulo strano
  in `sys.modules`) fermerebbe l'avvio di tutto il bot, paper e demo compresi. Oggi non succede (costruito qui con i moduli veri), ma
  il conto vero non dovrebbe poter fermare il resto. Correzione: `try` attorno alla creazione, con il conto vero spento e un allarme.

### 72 — Basso, nuovo — Il ritardo di 60 s dei redditi non ha un test
- Tolto il ritardo (`fine = adesso`) i 62 test del conto vero passano tutti. Il ritardo evita blocchi brevi del controllo del saldo;
  con la rilettura di 15 minuti il danno sarebbe piccolo, ma la costante ha un test di guardia e il comportamento no.

Restano i Bassi 51 e 52 del demo.

## Invarianti modificati

Rispetto al secondo giro: prima della prima accensione lo stop sul conto non chiude (`:459-464`); il blocco per «saldo sotto il
valore» ha una tolleranza e tre letture (`:95-101`, `:540-550`); i redditi si leggono con ritardo, sovrapposizione e doppioni tolti
(`:80-84`, `:396-457`). Gli altri come nel secondo giro. Limiti fissi invariati.

## Decisioni per Alessio

1. Come nel secondo giro (ordini «solo riduzione» con `DRY_RUN` vero; chi approva il tag; limiti; prelievi; blocchi a ogni commit in
   `bot/`; stato perso che chiude tutto; «riparti» da file; pulsante in dashboard; chiave, regole e modo del conto; riavvio).
2. Nuova: prima della prima accensione, con posizioni nel conto, lo stop del bot deve chiuderle o no? Raccomando di sì (70): il conto
   deve essere solo del bot, e così le posizioni del bot restano protette anche se lo stato e la traccia si perdono.
3. Il commit del codice spento: approvato; `ops_agent.py` vale subito sulla macchina; il riavvio che carica il resto, con il suo ok.

## Domande aperte

Restano quelle del secondo giro (identità con cui si spinge su GitHub; utente e lingua di git sulla macchina; modo del conto dei
future; come risponde `/fapi/v1/income` sul conto vero; G1 o G1 neutra lunedì; la proposta della leva a 10 come «non applicata»).
