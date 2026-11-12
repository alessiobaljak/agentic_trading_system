# Revisione: conto vero, secondo giro del 12 novembre 2026 (correzioni di 74, 75, 76, 77 e della parte «subito» del 54)

## Riepilogo e verdetto

**APPROVE per il commit** (codice spento; il riavvio che lo carica con l'ok di Alessio). **REQUEST CHANGES per l'accensione**:
restano 54 (ii) Alto (decisione di Alessio), 70 Medio e un Basso nuovo, 78 (il test di guardia del 54 non vede l'errore più
naturale, la costante importata). Chiusi davvero: 74, 75, 76, 77.

## Oggetto

- Il primo giro è committato come `a267c40`: verificato file per file, uguale alla copia rivista (`giro12nov/copia`). Nessun commit
  dopo `a267c40` tocca il percorso degli ordini, `firebase/`, `.github/`, la dashboard o i due script.
- Modifiche non committate su HEAD `7e9adba`: `bot/portafoglio/conto_vero.py` (+92 −41 insieme agli altri), `tests/test_conto_vero.py`
  (+8 test), `dashboard/app/components/strategie/ComandiContoVero.tsx` e `dashboard/app/lib/strategie.ts` (testi). Demo, paper,
  `main.py`, `config.py`, regole: non toccati.

## Checklist A–F (solo ciò che cambia rispetto al primo giro)

- **A.** Limiti fissi e limiti del conto vero invariati; costanti nuove (`APPROVAZIONE_SENZA_RISPOSTA_S` 600, `SECONDA_LETTURA_ENTRO_S`
  5, `OGNI_CONTROLLO_CODICE_DA_SPENTO_S` 600) con test. **OK.**
- **B.** Ordini: nessuna riga cambiata. **OK.**
- **C.** Buco di Firebase: vale l'approvazione letta davvero negli ultimi 10 minuti, sempre con git (74 chiuso). Chiamate da spento
  ridotte (75 chiuso). Fermo riscritto finché arriva (76 chiuso). «Non ancora letta» prima del primo controllo (77 chiuso). **OK.**
- **D.** Separazione invariata; da spento nessuna chiave e nessuna richiesta a Binance (test superati). **OK.**
- **E.** Nessun segreto; commenti del 54 corretti (`conto_vero.py:22-28`, `:90-93`, `ComandiContoVero.tsx:10-14`,
  `lib/strategie.ts:194-195`). Test di guardia: **PROBLEMA 78**.
- **F.** Sotto.

## Test

- `python3 -m pytest tests/ -q`: **2765 passed, 1 failed in 228,21 s**; il fallito è la firma (libreria del contenitore), che passa
  con `PYTHONPATH=<cartella di lavoro>/cripto` insieme ai 98 test del conto vero (99 passed). Il test di guardia del 54 passa.
- Undici mutazioni nuove (`giro12nov/mutazioni2.py`), **11 su 11 fanno fallire un test**: finestra senza limite di tempo; revoca
  letta non ricordata; approvazione ricordata senza git; finestra tolta; da spento ogni minuto; all'accensione nessun controllo
  subito; seconda lettura sempre; versione riscritta con Firebase muto; fermo non riscritto; codice «approvato» prima del primo
  controllo; il bot che scrive la versione approvata.
- Prove del revisore rifatte sul codice nuovo (`giro12nov/test_prove_12nov.py`), con un giro al minuto come il bot vero:
  S1b (buco nel minuto della decisione di G1) **4 ordini lo stesso giorno**, come senza buco; S2b (buco allo scadere dell'ora) il
  resto va a mercato; S3 il fermo arriva su Firebase al primo giro dopo il buco. (S1 e S2 della prima versione, senza giri per un
  giorno o per un'ora, restano bloccate: è giusto, l'ultima lettura vera ha più di 10 minuti.)
- Prova S4, revoca scritta mentre il bot non legge Firebase: ordini ancora ammessi fino al decimo minuto dall'ultima lettura vera,
  bloccati dall'undicesimo; con Firebase di nuovo vivo la revoca vale subito.
- Chiamate a Firebase del conto vero spento e mai acceso con Firebase muto (`prova_firebase_muto.py`): la versione si legge solo
  al primo giro, poi ogni 10 minuti; restano le 2 letture per giro di `_acceso_su_firebase` (del problema 66, già in `ff89531`, non
  di questo giro). Con Firebase vivo: 0 chiamate per giro.
- Dashboard: `tsc --noEmit` senza errori.

## Le tre verifiche chieste

1. **La finestra dei 10 minuti non permette ordini con un codice diverso da quello approvato**: il commit ricordato passa dallo
   stesso confronto di git (`conto_vero.py:455-466`; test `test_74_oltre_dieci_minuti...`, mutazione N3 uccisa). **Né dopo una revoca
   letta**: una risposta vera senza approvazione si ricorda come «nessuna» (`:454-456`) e il buco dopo non riporta la vecchia (test,
   mutazione N2 uccisa). **Dopo una revoca non letta** (Firebase muto per il bot): fino a 10 minuti dall'ultima lettura vera (S4). È
   il prezzo dell'alternativa scelta; va detto ad Alessio. La dashboard non ha ancora un pulsante «Revoca» (oggi si revoca solo
   dalla console di Firebase).
2. **Il test di guardia del 54 è aggirabile per errore banale: sì** (78, sotto).
3. **Con il conto spento nulla cambia per demo e paper**: i loro file non sono toccati; il conto vero spento legge Firebase una volta
   ogni 10 minuti (prima una al minuto) e non scrive la versione con Firebase muto.

## Problemi

### 54 (parte ii) — Alto, aperto (decisione di Alessio)
La parte «subito» è fatta (commenti veri, test di guardia). La protezione vera resta da decidere: chi ha la chiave di
amministratore (il bot, l'agente della macchina riletto dal branch ogni minuto, quattro flussi di GitHub) può scrivere
l'approvazione e il «riparti»; chi spinge sul branch può far girare quel codice.

### 78 — Basso, nuovo — Il test di guardia del 54 non vede la costante importata
- Dove: `tests/test_conto_vero.py`, `test_54_nessun_codice_del_repository_scrive_i_comandi_del_conto_vero`: cerca i quattro nomi come
  testo nei file `*.py *.sh *.yml *.yaml *.js *.mjs *.ts`.
- Applicata la stessa regola a sei esempi: **non segnalati** `from bot.portafoglio.conto_vero import COMANDO_VERSIONE` +
  `fb.set_rtdb(COMANDO_VERSIONE, ...)`, `fb.set_rtdb(cv.COMANDO_RIPARTI, True)`, il nome a pezzi (`'/commands/conto_vero_' +
  'versione_approvata'`), la f-string con `ContoVeroG1.NOME`, un `.json` letto da uno script generico; segnalata solo la scrittura del
  genitore con il nome intero. Nel controllo con l'albero del codice di `conto_vero.py` e `demo_binance.py` sfugge anche un percorso
  tenuto in una variabile senza «COMANDO» nel nome.
- Scenario: uno script di prova scritto da una sessione «per approvare la versione e provare» importerebbe proprio la costante;
  girando sulla macchina o in un flusso di GitHub con la chiave di amministratore, approverebbe senza Alessio e il test passerebbe.
- Correzione: oggi fuori da `conto_vero.py` si importa solo `crea_conto_vero` (`bot/main.py:43`). Il test vieti, fuori da
  `conto_vero.py`, dai test e dalla dashboard, ogni import da `bot.portafoglio.conto_vero` diverso da `crea_conto_vero` e ogni
  attributo `COMANDO_*` del modulo; cerchi anche i pezzi `versione_approvata` e `riparti_conferma`; guardi anche `*.json *.toml *.cfg
  *.ini *.ipynb`; e in `conto_vero.py`/`demo_binance.py` ammetta `set_rtdb` solo su `f"/{self.NOME}/..."` o sulle costanti `COMANDO_*`
  con falso o None. Resta una guardia contro gli errori, come dice il suo testo.

### 70 — Medio, aperto dall'8 novembre, non toccato.

## Invarianti modificati (rispetto al primo giro)

- Firebase muto: vale l'approvazione letta davvero negli ultimi 10 minuti, con git; prima nessuna.
- Da spento la versione si controlla ogni 10 minuti (all'accensione subito); seconda lettura solo se la prima è durata fino a 5 s.
- `/conto_vero/fermo` riscritto finché arriva. Limiti fissi invariati.

## Cosa resta per l'accensione

1. 54 (ii): la decisione di Alessio (raccomandata: un'installazione per i soldi veri che non esegue da sola il codice del branch, la
   chiave di amministratore fuori da GitHub).
2. 78: il test di guardia completo.
3. 70: lo stop prima della prima accensione con posizioni nel conto (decisione di Alessio).
4. Regole pubblicate con i blocchi del demo e del conto vero, e ogni pulsante provato fino in fondo.
5. Le decisioni del primo giro: pulsante «Approva» con il verdetto del revisore e i file cambiati, pulsante «Revoca»; sapere che una
   revoca non letta vale fino a 10 minuti dopo.
6. Una revisione nuova prima dell'accensione.

## Domande aperte

Restano quelle del primo giro (regole pubblicate e con quale utente; utente di git sulla macchina; chiavi vere, prelievo, indirizzo;
identità con cui si spinge su GitHub; modo del conto dei future; `/fapi/v1/income` sul conto vero; G1 o G1 neutra; la leva a 10 da
chiudere come «non applicata»).
