# Quattordicesima revisione del trader AI — obiettivo obbligatorio, bilancio di oggi, più ragionamento

Revisore: live-path-reviewer, 26 novembre 2026. Controllo limitato al commit `d9c8af7` (branch `claude/brave-albattani-1b12fv`;
`e2cc408` è solo l'unione con dati di ricerca, nessun file di `trader_ai/`).

### Riepilogo e verdetto

**APPROVE con condizioni.** Nessun problema Bloccante né Alto. Un Medio (184) e due Bassi (185, 186).

1. **Il tetto dei 5 dollari tiene.** Prima di ogni chiamata si registra il costo più alto possibile (`trader_ai/giro.py:34-37`), calcolato
   con `MAX_TOKENS` (`trader_ai/costi.py:22`, `costi.py:38-42`), e si chiama solo se sta nel rimasto (`costi.py:68-70`). Il pensiero sta
   dentro `max_tokens`, quindi una risposta non può costare più di 16.000 token in uscita. Costo massimo per chiamata: 0,345 dollari con un
   messaggio di 10.000 caratteri, 0,395 con 30.000 (calcolato con `costo_massimo`). Il test `test_il_tetto_non_si_sfora_mai_...`
   (`trader_ai/tests/test_trader_ai.py:62-70`) è aggiornato a 16.000 e passa. Effetto pratico: al costo massimo bastano 12-14 chiamate per
   finire il tetto; poi il modello non si chiama fino a mezzanotte (la posizione resta protetta dallo stop sul conto).
2. **Lo stato vecchio senza `prezzo_mezzanotte` non rompe niente.** `avvio.py:223` usa `st.get("prezzo_mezzanotte")`; con `None`
   `bilancio_di_oggi` salta la riga del prezzo (`messaggio.py:65`). Provato a mano: stato vuoto, `None` e `0.0` danno il bilancio senza
   errori. La riga del prezzo compare dalla prima mezzanotte UTC dopo il riavvio (`avvio.py:158`). Manca un test per questo caso (186).
3. **Nessun Bloccante né Alto.** Il percorso degli ordini non cambia: controllo del fermo, rilettura del conto e `controlla` prima di ogni
   ordine restano (`avvio.py:318-331`); limiti di leva e margine invariati (`trader_ai/limiti.py`, non toccato).

Condizioni prima del riavvio: 184 (tempo massimo della chiamata) e 185 (testi di `REGOLE.md` e del commento in `costi.py`).

### Oggetto

* Commit `d9c8af7`; file: `trader_ai/istruzioni.md`, `messaggio.py` (`bilancio_di_oggi`, parametro `bilancio` di `blocco_memoria`),
  `avvio.py` (righe 37, 158, 222-223), `modello.py` (riga 45, sforzo «high»), `costi.py` (riga 22, 16.000), `REGOLE.md` (versione 6),
  `tests/test_trader_ai.py`.
* Invarianti coinvolti: tetto di spesa giornaliero (sezione 15 di `reviews/LIVE_PATH_MAP.md`): il valore resta 5 dollari, cambia il costo
  massimo per chiamata (da circa 0,27-0,32 a 0,35-0,40 dollari).

### Checklist A–F (solo i punti toccati)

* A. Limiti fissi: `TETTO_GIORNO_DOLLARI = 5.00` invariato (`costi.py:19`); `MAX_TOKENS` è una costante nel codice. OK. Il testo delle
  istruzioni è una scelta del proprietario: non valutato.
* B. Ordini: nessun cambio. OK.
* C. Stato e resilienza: stato vecchio compatibile (vedi punto 2). Chiamata più lunga con tempo massimo invariato a 300 secondi
  (`modello.py:31`): PROBLEMA 184. Il pulsante che chiude tutto non aspetta il blocco per chiudere (`avvio.py:478-491`) e `_esegui`
  ricontrolla il fermo dopo la chiamata (`avvio.py:318-319`): una chiamata più lunga non lo indebolisce. OK.
* D, E. NON APPLICABILE (nessun cambio a chiavi, indirizzi, ambiente).
* F. Test: `TRADER_AI_BLOCCO=/tmp/x.lock python -m pytest trader_ai/tests -q` → **92 passed in 9.78s**. Nuovi:
  `test_bilancio_di_oggi_dice_direzioni_vinte_perse_e_prezzo`, `test_istruzioni_obiettivo_obbligatorio`. Manca il caso dello stato
  vecchio (186).

### Problemi

* **184 — Medio — `trader_ai/modello.py:31` (timeout 300 secondi) con `costi.py:22` (16.000 token) e `modello.py:45` (sforzo «high»).**
  Scenario: con sforzo alto il modello usa più spesso tutto lo spazio; 16.000 token a 50-60 token al secondo sono 270-320 secondi. La
  chiamata scade a 300 secondi: esito «errore», nessuna decisione, e il tetto si scala del costo massimo intero (`giro.py:41`, senza token
  dichiarati) mentre il servizio può averla fatturata lo stesso. Più chiamate perse e budget che finisce prima. Non c'è rischio di sforare
  il tetto. Correzione suggerita: portare il tempo massimo a 600 secondi (l'SDK accetta una chiamata senza flusso con 16.000 token) oppure
  passare alla risposta a flusso; scrivere nel diario la durata di ogni chiamata e contare nel resoconto gli esiti «errore» e «troncata».
* **185 — Basso — testi non aggiornati.** `trader_ai/REGOLE.md:49` dice ancora sforzo `medium` e 12.000 token; `REGOLE.md:54` dice
  «più 12.000 token di risposta»; `trader_ai/costi.py:20-21` dice «12.000 x 20 / milione = 0,24 dollari» (ora 16.000, 0,32). Nella tabella
  delle versioni la riga 6 sta fra la 2 e la 5. Correzione: aggiornare le tre righe e l'ordine della tabella.
* **186 — Basso — `trader_ai/messaggio.py:61-62` e test.** Un'operazione a risultato 0,00 si conta fra le «perse»: al modello arriva
  «0 vinte e 1 perse» per una chiusura in pari. Nessun test copre lo stato salvato senza `prezzo_mezzanotte` né la chiamata dal
  `passo`. Correzione: contare le pari a parte (o scrivere «perse o in pari») e aggiungere un test con lo stato senza la chiave.

### Invarianti modificati

* Nessun valore dei limiti. Cambia il costo massimo per chiamata (0,35-0,40 dollari), quindi il numero minimo garantito di chiamate al
  giorno scende (al costo massimo, 12-14 invece di circa 16-18).

### Decisioni per Alessio

* Il riavvio con queste modifiche tocca il programma che manda gli ordini simulati: serve il suo ok.
* Sapere che con il ragionamento più lungo i 5 dollari possono finire prima di sera: dopo, il trader non decide più fino a mezzanotte
  (le posizioni aperte restano con il loro stop).

### Domande aperte

* Quanto costa davvero una chiamata con sforzo «high»? Dopo un giorno di simulato, guardare nel diario (`costo`, `speso_oggi`) a che ora
  si esaurisce il tetto e quanti esiti «errore» o «troncata» ci sono.
