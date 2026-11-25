# Tredicesima revisione del trader AI — obiettivo del giorno al 3%

Revisore: live-path-reviewer, 25 novembre 2026. Controllo limitato al commit `5222579` (branch `claude/brave-albattani-1b12fv`).

### Riepilogo e verdetto

**APPROVE con condizioni.** Nessun problema Bloccante né Alto. Un Medio (176) e un Basso (177).

La regola di chiusura funziona come prima, cambia solo la soglia: stesso confronto (`conto >= conto_mezzanotte + soglia`), stessi due
punti di controllo (`trader_ai/avvio.py:195` chiude tutto e ferma fino a mezzanotte; `trader_ai/giro.py:32` non chiama il modello),
stesso conto della mezzanotte (`trader_ai/avvio.py:158`, preso dal saldo al cambio di giorno UTC). La soglia ora è
`conto_mezzanotte * 0.03` (`trader_ai/limiti.py:46-47`): 30 USDT su 1.000.

Condizione: correggere le righe 40 e 92 di `trader_ai/REGOLE.md`, che dicono ancora «50 USDT» (problema 176), prima del primo avvio.

### Oggetto

* Commit `5222579`; file: `trader_ai/limiti.py`, `messaggio.py`, `avvio.py` (solo il testo del resoconto, riga 518), `istruzioni.md`,
  `REGOLE.md`, `README.md`, `tests/test_avvio.py`, `tests/test_trader_ai.py`.
* Invariante coinvolto: obiettivo del giorno (sezione 15 di `reviews/LIVE_PATH_MAP.md`), da 50 USDT fissi al 3% del conto della mezzanotte.

### Checklist A–F (solo i punti toccati)

* A. Limiti fissi: la soglia resta una costante nel codice (`trader_ai/limiti.py:14`, `OBIETTIVO_GIORNO_QUOTA = 0.03`), non in
  configurazione né in variabili d'ambiente. Nessun altro uso del vecchio nome `OBIETTIVO_GIORNO_USDT` nel repo (ricerca). OK.
  Cambio voluto dal proprietario, testo citato nel commit e in `limiti.py:4-5`. OK.
* B. Ordini: nessun cambio nel percorso degli ordini; la chiusura all'obiettivo è la stessa chiamata `self.c.chiudi` (`avvio.py:196`). OK.
* C. Stato: `conto_mezzanotte` sempre valorizzato prima del controllo (`avvio.py:155-158`, `avvio.py:252`). OK. Arrotondamenti:
  provati 1.000, 1.040, 987,65 e 1.234,56: la soglia scatta al valore atteso. OK.
* D, E. NON APPLICABILE (nessun cambio a chiavi, indirizzi, ambiente).
* F. Test: `TRADER_AI_BLOCCO=/tmp/x.lock python -m pytest trader_ai/tests -q` → **90 passed in 9.73s**. Il test a
  `tests/test_trader_ai.py:76-77` fallirebbe se la soglia si calcolasse sul conto attuale invece che su quello della mezzanotte
  (1.030 × 3% = 30,90 → 1.030 non basterebbe); `test_messaggio_dice_obiettivo_memoria_e_scarto` controlla «mancano 10.00» con conto
  1.020. `test_valori_fissati_dal_proprietario` fissa 0,03. OK.

### Problemi

* **176 — Medio — `trader_ai/REGOLE.md:40` e `:92`.** Le regole scritte dicono ancora «guadagnato 50 USDT dalla mezzanotte UTC» e
  «conto ≥ conto a mezzanotte UTC + 50 USDT», mentre titolo e tabella dicono versione 5 al 3%. Scenario: chi controlla il primo giorno
  (o il riconciliatore) confronta il codice con le regole e trova due soglie diverse; non si sa quale valga. Correzione: scrivere
  «3% del conto della mezzanotte UTC (30 USDT su 1.000)» nelle due righe.
* **177 — Basso — `trader_ai/limiti.py:43-47`.** Con conto della mezzanotte a zero (conto finito) la soglia è zero e il programma scrive
  «obiettivo del giorno raggiunto» e si ferma, invece del messaggio «FERMO: il conto non basta più» (`avvio.py:207`), che viene dopo.
  Nessun ordine sbagliato, solo un evento fuorviante. Correzione facoltativa: considerare raggiunto l'obiettivo solo se
  `conto_mezzanotte > 0`. Cosmetico, stessa riga: nella tabella delle versioni di `REGOLE.md:120` la 5 sta prima della 4.

### Invarianti modificati

* Obiettivo del giorno: da `conto >= conto_mezzanotte + 50` a `conto >= conto_mezzanotte × 1,03` (`trader_ai/limiti.py:42-47`).
  Su 1.000 USDT la soglia scende da 50 a 30 USDT e segue il conto (sale se il conto sale, scende se scende).

### Decisioni per Alessio

* Nessuna nuova. Il 3% è suo (25 novembre). Restano quelle delle revisioni precedenti per il primo avvio.

### Domande aperte

* Nessuna.
