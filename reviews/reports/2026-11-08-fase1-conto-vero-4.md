# Revisione della fase 1 del conto vero, quarto giro: solo il problema 50 (8 nov 2026)

Revisore: `live-path-reviewer`. Oggetto: la correzione del problema 50 (`reviews/reports/2026-11-08-fase1-conto-vero-3.md`), non
committata, nello stesso diff dei giri prima. Rispetto alla copia del terzo giro (`scratchpad/fase1/giro3/`) cambiano solo
`demo_binance.py:927-944` e `:1006-1020`; fotografia e dashboard sono invariate. Base `4f866a1`. La sessione principale dice che
`reviews/` è stata committata da una copia separata (commit sul remoto dopo `4f866a1`): qui non lo vedo, perché il working tree non è
ancora allineato.

### Riepilogo e verdetto

**APPROVE.** Il 50 è chiuso, la correzione non apre problemi Bloccanti, Alti o Medi, e la fase 1 è pronta per il commit dal lato di
questa revisione. Il riavvio resta una decisione di Alessio. Restano due Bassi (51 e 52), non condizioni.

- `_riparti_ammesso` (`:1006-1020`) prende `(RuntimeError, requests.RequestException)` sulla lettura del conto e degli ordini e
  restituisce None; `LimiteBinance` risale come prima.
- Con None, in `_da_fermo` (`:930-944`):
  - il comando della dashboard non si consuma;
  - quello del file torna da eseguire (`eseguito_riparti` rimesso al valore di prima, o tolto se non c'era);
  - le chiusure del minuto continuano.

Prove (`scratchpad/fase1/prova_g4.py`, `prova_g3_riparti.py`, con `PYTEST_CURRENT_TEST=x`):

| Caso | Esito |
|---|---|
| Fermo con BUSDT −20, `openOrders` sempre 503, «riparti» da file o dalla dashboard (la prova del 50) | BUSDT chiuso al primo minuto, 11 tentativi in 10 minuti, allarme del fermo (prima: BUSDT −20, 1 tentativo) |
| Come sopra per 10 minuti, poi gli ordini tornano leggibili | file: `eseguito_riparti` resta vuoto finché non si legge, poi vale **una volta** (`r1`); dashboard: il comando resta vero, poi si consuma e vale una volta |
| Dopo quel «riparti», un «chiudi tutto» nuovo e 4 minuti | resta fermo: il «riparti» vecchio non si ripete (file e dashboard) |
| Conto illeggibile 5 minuti con «riparti» da file in attesa | comando ancora in attesa; quando il conto torna, si rifiuta «conto non vuoto» e BUSDT si chiude nello stesso giro (51) |
| «Riparti» in attesa e 429 su tutte le richieste per 30 minuti | tentativi fermi a 1, nessun allarme del fermo, allarme dei limiti acceso (52) |

Il «riparti» da file rimesso da eseguire non si ripete all'infinito: si riprova a ogni giro solo finché la lettura fallisce (una
lettura del conto e una degli ordini ogni 30 secondi, poca cosa rispetto ai limiti). Al primo giro buono si esegue o si rifiuta, e in
tutti e due i casi `eseguito_riparti` prende il testo e si salva. Non si perde nemmeno se dopo il ritorno qualcosa va in errore:
- con un `LimiteBinance` nelle chiusure lo stato si salva con il valore rimesso;
- con un altro errore lo stato non si salva, e resta quello di prima, ancora in attesa.

Test:
- `test_50_riparti_in_attesa_con_gli_ordini_illeggibili_non_ferma_le_chiusure[file|dashboard]` fallisce sul codice del terzo giro
  (2 fallimenti su 89) e passa ora;
- suite intera `2624 passed, 1 deselected in 168.74s`;
- firme (con `PYTHONPATH=…/scratchpad/cr`) e guardia dei limiti fissi e dell'avvio: `33 passed`;
- `hard_limits.py`, `bot/config.py`, `bot/main.py`, `bot/execution`, `firebase/`, `ops/` invariati.

### Checklist A–F (solo il punto toccato)

- **A**, chiusure da fermo con un «riparti» in attesa e gli ordini illeggibili: **OK**. Gli altri punti di A non sono toccati.
- **C**, errori di lettura nel controllo del «riparti»: **OK**. `LimiteBinance` risale: resto Basso 52.
- **B, D, E**: **NON APPLICABILE** (nessun ordine, indirizzo o segreto nuovo).
- **F**: test vero, suite verde.

### Problemi

**Problema 51 — Basso — `demo_binance.py:934-936` prima di `:950`: quando il conto torna leggibile, il «riparti» in attesa si
controlla prima della richiusura del minuto.**
- Se nel frattempo una posizione è rimasta, il «riparti» si rifiuta («conto non vuoto»), il comando si consuma e solo dopo, nello stesso
  giro, la posizione si chiude.
- Il proprietario deve ripremere. L'allarme `riparti` lo dice, quindi niente si perde in silenzio.
- Correzione possibile: rimandare il «riparti» (None) quando il conto non è ancora segnato `vuoto`, invece di consumarlo.

**Problema 52 — Basso (c'era già nel terzo giro) — `demo_binance.py:937`: con un «riparti» in attesa e tutte le richieste limitate,
i tentativi del fermo non crescono.**
- `LimiteBinance` esce da `_riparti_ammesso` prima del conteggio dei tentativi (`:957-965`), quindi il 49 non vale finché c'è un
  «riparti» in attesa.
- Si vede l'allarme dei limiti. Con tutto limitato niente si può chiudere comunque.
- Correzione possibile: prendere `LimiteBinance` anche lì, contare il tentativo e salvare, come nel minuto.

### Invarianti modificati

Nessuno dei limiti fissi. Cambia solo questo: un errore di lettura nel controllo del «riparti» non ferma più le chiusure da fermo e
non consuma il comando.

### Decisioni per Alessio

1. **Riavvio con la fase 1**, dopo il commit: dal lato di questa revisione si può. Restano da confermare le scelte della sessione
   principale:
   - stop al pavimento del 65% della fase;
   - «riparti» solo a conto vuoto e con la riapertura alla mezzanotte;
   - limiti nel codice con un test di guardia;
   - una moneta oltre il 60% fa saltare la decisione;
   - quando G1 non decide, il demo tiene le posizioni di ieri.
2. Restano le voci di prima: stop per posizione, avvisi sul telefono, `DRY_RUN` falso che ferma il demo, chiavi vere, prelievo,
   regole di Firebase, tetto di 10.000.

### Domande aperte

Nessuna nuova.
