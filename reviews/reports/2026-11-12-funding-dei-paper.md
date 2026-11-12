# Revisione: il conto del funding dei paper (G1, G11, G1 neutra, F5, eventi) — 12 novembre 2026

## Riepilogo e verdetto

**REQUEST CHANGES per il commit e per il riavvio**, per una correzione di una riga: il problema 82 (Medio). Non ci sono Bloccanti né
Alti.

Il resto è a posto:
- il conto nuovo del funding è giusto e non conta niente due volte, nemmeno al primo giro dopo il riavvio con lo stato di oggi;
- nessuna strategia si spegne e nessun peso cambia;
- il demo di G1 non cambia comportamento;
- le richieste a Binance in più sono poche.

Il problema: il paper di G1 tiene nel suo stato `funding_regolamenti`, con chiavi «AAAA-MM-GG/HH:MM». Lo stato intero va su Firebase
in `/paper_g1/stato_interno`, e il database in tempo reale non accetta chiavi con «/». Il repository stesso lo annota
(`bot/learning/apprendimento.py:493`). Da quel momento la copia su Firebase dello stato del paper di G1 smette di aggiornarsi, e ogni
salvataggio scrive nel registro «RTDB irraggiungibile».

## Oggetto

- Branch `claude/brave-albattani-1b12fv`, modifiche non committate su HEAD `4f61aaf`:
  - `bot/portafoglio/f5.py` (+113 −19);
  - `bot/portafoglio/eventi.py` (+17 −5);
  - `tests/test_paper_f5.py` (6 test nuovi);
  - `tests/test_paper_eventi.py` (1 nuovo).
- Sono file della cartella `bot/portafoglio`, dentro i percorsi della versione del conto vero: dopo il riavvio una versione
  approvata andrebbe riapprovata. Oggi non ce n'è nessuna, quindi non cambia niente.
- Invarianti del percorso degli ordini: nessuno cambia.

## Checklist A–F

- **A.** Limiti e interruttori: non toccati; nessuno spegnimento. **OK.**
- **B.** Ordini: nessuno. Il paper simula soltanto. **NON APPLICABILE.**
- **C.** Stato e resilienza:
  - il funding si legge moneta per moneta dal suo ultimo regolamento contato (`funding_visti`);
  - al ribilancio i regolamenti non ancora pubblicati restano in sospeso al massimo 2 ore con la quantità di prima (`f5.py:557-572`, `:574-631`);
  - negli eventi ogni gamba ha il suo punto (`eventi.py:144-164`);
  - giusto, ma la copia su Firebase del paper di G1 si rompe: **PROBLEMA 82**.
- **D.** Separazione: il demo legge dal file del paper di G1 solo `ultimo_lunedi` e `pesi` (`demo_binance.py:870-874`, `:1130`), che il
  cambio non tocca. Il conto vero, spento, legge allo stesso modo. **OK.**
- **E.** Segreti: nessuno. La scrittura nuova `/paper_g1/funding/{data}/{ora}` la fa il bot con la chiave di amministratore; le regole
  non c'entrano. **OK.**
- **F.** Test:
  - test del paper, delle strategie accese, del demo contro il paper e del poco capitale: **37 passed**;
  - suite intera `python3 -m pytest tests/ -q`: **2795 passed, 1 failed** in 191 s (la firma, colpa della libreria del contenitore);
  - quattro mutazioni a mano, tutte fanno fallire un test: conferma del sospeso tolta, punto per moneta tolto, sospeso al ribilancio
    tolto, eventi con il punto a «adesso».

## Prove del revisore (`giro12nov/test_prove_funding.py`)

- **T1, stato di oggi senza i campi nuovi** (`funding_fino_ms` = il massimo letto, le 08:00 di A già contate): tre giri del codice
  nuovo non ricontano A. B, pubblicato tardi e già perso dal codice di oggi, resta perso (nessun doppione). Le 16:00 si contano per
  tutte e due.
- **T2, riavvio a cavallo del ribilancio** (il codice di oggi alle 00:01 ha letto D delle 00:00): il ribilancio del codice nuovo alle
  00:06 non riconta D, e il sospeso parte dopo le 00:00.
- **T3, le chiavi dello stato di G1**: `/paper_g1/stato_interno` contiene la chiave `funding_regolamenti/2026-10-24/08:00`. Il paper
  F5 non tiene quel campo (solo G1 lo pubblica).

## Le verifiche chieste

- **Nessun doppione al primo giro dopo il riavvio:** OK (T1, T2).
- **Nessuna strategia spenta e nessun peso cambiato:** le decisioni (`pesi_del_lunedi`) e gli interruttori non sono toccati. Cambia
  solo il funding contato, che da ora comprende i regolamenti pubblicati tardi: il numero del funding dei paper fa un piccolo salto
  dal riavvio, da dire al confronto settimanale.
- **Il demo di G1:** non cambia (vedi D).
- **Peso delle richieste a Binance:** una chiamata a `fundingRate` per moneta come prima, più le monete uscite al ribilancio con un
  regolamento in sospeso, per al massimo 2 valutazioni (ognuna ogni ora): qualche decina al giorno per paper. Va su
  `fapi.binance.com` pubblico, non sul demo. Nota per il futuro: secondo Binance `fundingRate` ha un limite suo, 500 ogni 5 minuti per
  indirizzo, che il conto vero condividerà.
- **Scrittura nuova su Firebase:** `/paper_g1/funding/{data}/{HH:MM}`, circa 0,5 KB per regolamento, riscritta quando arriva una
  moneta in ritardo. Da 3 a circa 24 regolamenti al giorno (le monete a 1 o 4 ore), cioè circa 25 KB al giorno, mai cancellati
  (pulizia facoltativa).
- **Versione del conto vero:** il cambio tocca `bot/portafoglio`: dopo il riavvio serve una nuova approvazione (oggi non ce n'è
  nessuna).

## Problemi

### 82 — Medio, nuovo — Una chiave con «/» nello stato del paper di G1 rompe la sua copia su Firebase

- **Dove:** `f5.py:585` (lo stato tiene `funding_regolamenti`) e `:609` (chiave `time.strftime("%Y-%m-%d/%H:%M", ...)`).
  `PaperF5.salva` scrive lo stato intero in `/paper_g1/stato_interno` (`f5.py:296-302`).
- **Scenario:**
  - dal primo giro dopo il riavvio Firebase rifiuta ogni scrittura di `/paper_g1/stato_interno`: chiave non valida, senza
    controllo dal lato del client (`firebase_admin` 6.5.0);
  - `set_rtdb` restituisce falso e segna il database come muto (`firebase_client.py:677-679`): ogni ora il registro dice «RTDB
    irraggiungibile» e subito «di nuovo raggiungibile», e il segnale vero di un Firebase giù si confonde;
  - se il file `data/paper_g1.json` si perde o si rovina, `carica` (`f5.py:289-294`) riprende lo stato dalla copia ferma al giorno
    del riavvio: il paper di G1, da cui il demo prende i pesi, riparte da posizioni e capitale vecchi.
- **Correzione:**
  - chiave senza «/» nello stato, per esempio «2026-11-12T08:00» o «2026-11-12 0800», e il percorso pubblicato costruito separando
    data e ora; oppure tenere `funding_regolamenti` fuori dallo stato salvato;
  - test: nessuna chiave dello stato dei paper contiene `. $ # [ ] /`.

## Invarianti modificati

Nessuno del percorso degli ordini. Il funding dei paper si conta moneta per moneta e con i regolamenti in sospeso al ribilancio.

## Decisioni per Alessio

Nessuna nuova. Il riavvio dopo la correzione resta con il suo ok.

## Domande aperte

Nessuna nuova.

## Secondo giro (12 novembre, notte): APPROVE per il commit e per il riavvio (il riavvio con l'ok di Alessio)

- **82 chiuso:** le chiavi dello stato sono «2026-10-24T08:00» (`CHIAVE_REGOLAMENTO`, `f5.py:66`, `:611`); il percorso pubblicato
  resta `/paper_g1/funding/{data}/{ora}` (`:644`). Test sulle chiavi dello stato presenti. Test del paper, degli eventi e delle
  strategie accese: 29 passed. Suite intera: 2797 passed, 1 failed (la firma).
- **83, Basso, nuovo, latente:** uno stato con una chiave nel formato vecchio («2026-10-23/16:00») fa sollevare `ValueError` a
  `time.strptime` (`:631`). Ogni valutazione e ogni ribilancio del paper di G1 si fermerebbero, e il demo resterebbe senza
  decisione nuova (prova fatta). Oggi non può succedere: il formato vecchio non è mai stato committato (`git log -S` vuoto), quindi
  la macchina non può averlo salvato. Correzione consigliata, non bloccante: una chiave che non si legge si toglie (con un `try`),
  così un cambio di formato futuro non ferma G1.
