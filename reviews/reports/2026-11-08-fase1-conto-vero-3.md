# Revisione della fase 1 del conto vero, terzo giro (modifiche non committate, 8 nov 2026)

Revisore: `live-path-reviewer`. Oggetto: le correzioni dei problemi 47, 48 e 49 del secondo giro
(`reviews/reports/2026-11-08-fase1-conto-vero-2.md`), nello stesso `git diff HEAD -- bot/portafoglio/demo_binance.py
scripts/state_snapshot.py tests/test_demo_binance.py dashboard/app/components/PaperBot.tsx`. Base `4f866a1`. Ho confrontato il codice
con la copia del secondo giro (`scratchpad/fase1/giro2/`): circa 120 righe in `demo_binance.py`, 5 nella fotografia, 2 nella dashboard.

Nota: il coordinatore scrive che `reviews/` è già committata. In questo working tree non lo è: `git status` mostra `INDEX.md`,
`LIVE_PATH_MAP.md` e `REVIEW_LOG.md` modificati, i rapporti del secondo e del terzo giro non tracciati, e HEAD è ancora `4f866a1`.

### Riepilogo e verdetto

**REQUEST CHANGES, per un solo punto breve.** 47, 48 e 49 sono chiusi. La correzione del 48 introduce però una regressione Media (50).
- Il controllo del «riparti» ora legge gli ordini aperti.
- Se quella lettura è in errore, l'errore esce prima delle chiusure da fermo del minuto.
- Quindi, con una posizione rimasta aperta e un «riparti» in attesa (file o dashboard), il demo non richiude più finché la lettura non
  torna. I tentativi restano a 1 e l'allarme del fermo non arriva.
- Senza «riparti» lo stesso caso si chiude al primo minuto: è la protezione dei problemi 32, 36 e 37.
- Nessun problema Bloccante né Alto.

| Problema | Esito | Evidenza |
|---|---|---|
| 47 (stop senza pavimento con un capitale in attesa) | **chiuso** | `demo_binance.py:219-226`; test `tests/test_demo_binance.py:1561`; prova p11: stop a 6.500 anche con il capitale in attesa, fermo a 6.000 |
| 48 («riparti» con il conto non vuoto; pavimento esatto) | **chiuso** | `_riparti_ammesso` `:997-1018`, `:934`; test `:1591`, `:1614`; prove p16 (rifiutato, BUSDT richiuso al minuto dopo), p12 (rifiutato a 6.500), p5 |
| 49 (testi dello stop, ventunesimo pezzo, tentativi con tutto limitato) | **chiuso** | `:204-216`, `:957-965`, `_allarme_del_fermo` `:989-995`; `PaperBot.tsx` e `state_snapshot.py:638-643`; test `:1635`, `:1655`, `:1661`; prova p13: 16 tentativi in 30 minuti, allarme del fermo |
| 50 (nuovo) | **aperto, Medio** | vedi sotto |

Test:
- suite intera `2622 passed, 1 deselected in 166.81s`, come dichiarato;
- firme (con `PYTHONPATH=…/scratchpad/cr`) e guardia dei limiti fissi e dell'avvio: `33 passed`;
- i 6 test nuovi, lanciati sul codice del secondo giro, falliscono tutti: sono veri;
- l'unico test vecchio cambiato (`test_23`) cambia solo il testo dell'allarme («non sopra il 65%»).

`bot/risk/hard_limits.py`, `bot/config.py`, `bot/main.py`, `bot/execution`, `firebase/`, `ops/`: invariati.

Le prove dei due giri prima (`prove_fase1.py`, `prove_giro2.py`) danno l'esito atteso. p1, p3, p17, p2b, p10, p11, p12, p13, p16 sono
corretti; p2 a 5 minuti resta aperto per i 10 minuti di attesa del 418, voluti, e p2b a 13 minuti è chiuso.

### Oggetto

Branch `claude/brave-albattani-1b12fv`, base `4f866a1`, modifiche non committate.
- Pavimento dello stop con la deroga stretta (`_pavimento`).
- Controllo del «riparti» con il conto vuoto e il valore sopra il pavimento (`_riparti_ammesso`).
- Allarme del fermo anche quando il conto non si legge.
- Chiusure al massimo in 20 pezzi.
- Testi dello stop in dashboard e fotografia.

Invarianti coinvolti: stop sul conto, «riparti», chiusure da fermo.

### Checklist A–F (solo i punti toccati da questo giro)

- **A.** Limiti fissi invariati: **OK**. Stop sul conto con il pavimento anche con un capitale in attesa: **OK** (47). Il «riparti» vale
  solo con il conto vuoto e il valore sopra il 65% della fase: **OK**. Chiusure da fermo: **PROBLEMA** 50.
- **B.** Chiusure al massimo in 20 pezzi, il resto al minuto dopo dalla posizione vera, sempre «solo riduzione»: **OK** (`:204-216`).
- **C.** Errori delle interfacce: con tutte le richieste limitate i tentativi da fermo crescono e l'allarme arriva (**OK**, p13). Una
  lettura degli ordini in errore con un «riparti» in attesa ferma le chiusure: **PROBLEMA** 50.
- **D, E.** Non toccati: **OK** (nessun indirizzo nuovo, nessun segreto).
- **F.** Test veri; il caso del 50 non è coperto.
- Dashboard e fotografia: testo del livello vero. La compilazione della dashboard non è verificata (lettura di `node_modules` vietata).

### Problemi

**Problema 50 — Medio (introdotto in questo giro) — `demo_binance.py:934` con `:1005`: un «riparti» in attesa con la lettura degli
ordini in errore ferma le chiusure da fermo.**
- `_da_fermo` controlla il «riparti» prima della richiusura del minuto. Il controllo nuovo, `_riparti_ammesso`, legge gli ordini aperti
  (`:1005`) senza prendere l'errore. È voluto, per non perdere il comando (problema 46). Però un `RuntimeError` (per esempio un 503) o
  un guasto di rete esce da `_da_fermo` prima delle chiusure.
- Il comando a file resta nuovo, perché lo stato non si salva; quello della dashboard resta vero. Quindi a ogni giro si ricomincia:
  - si controlla il «riparti»;
  - la lettura degli ordini va in errore;
  - le protezioni si fermano un minuto;
  - nessuna chiusura, nessun tentativo contato.
- Scenario (prova `scratchpad/fase1/prova_g3_riparti.py`):
  - fermo con BUSDT −20 rimasto aperto (chiusura rifiutata);
  - `openOrders` risponde sempre 503;
  - il proprietario scrive «riparti» (o lo preme in dashboard).
  - Dopo 10 minuti BUSDT è ancora −20, con 1 tentativo e nessun allarme del fermo; resta solo `/demo_binance/errore` con il 503.
  - Senza «riparti», nello stesso caso BUSDT si chiude al primo minuto (11 tentativi e allarme).
- È lo stesso effetto del problema 32 (Medio), ristretto ai casi con un «riparti» in attesa. Un «riparti» premuto subito dopo uno stop
  è proprio il caso normale. Per questo è Medio e non Basso.
- Correzione suggerita:
  - in `_riparti_ammesso`, prendere `(RuntimeError, requests.RequestException)` sulla lettura degli ordini (`:1005`, ed eventualmente
    sulla lettura del conto, `:1004`);
  - in quel caso non accettare e non consumare il comando (per esempio restituire `None` e, in `_da_fermo`, non chiamare `_riparti`);
  - proseguire con la richiusura del minuto, che sa già lavorare senza la lista degli ordini (problemi 36 e 37);
  - lasciare che `LimiteBinance` risalga come oggi.
- Test: la prova sopra, con il comando a file e con quello della dashboard. BUSDT deve chiudersi al primo minuto e il comando deve
  restare per il giro dopo.

Nota, non un problema: se alla mezzanotte `parti_da_zero` rifiuta un capitale in attesa mentre il conto aspetta vuoto, il ribilancio
apre con la fase vecchia e lo stop al pavimento può chiudere subito. Non succede in pratica: un conto vuoto non perde valore, e
`conto_ridotto` rifiuta il capitale già al giro prima. Ragionamento, non provato.

### Invarianti modificati

Nessun valore di `hard_limits.py` cambiato. Rispetto al secondo giro:
- il pavimento dello stop cade solo con un capitale in attesa **e** il conto vuoto che aspetta la fase nuova;
- il «riparti» vale solo con il conto vuoto (nessuna posizione, nessun ordine) e con il valore **sopra** il 65% del capitale della
  fase (salvo un capitale nuovo in attesa); se è rifiutato, il comando si consuma e c'è un allarme;
- da fermo, un tentativo conta anche quando Binance limita tutte le richieste;
- chiusure al massimo in 20 pezzi per giro.

### Decisioni per Alessio

1. **Riavvio**: dopo la correzione del 50, per me si può; la decisione resta tua.
2. Restano da confermare le scelte della sessione principale e le decisioni in sospeso del secondo giro: stop al pavimento, «riparti»
   alla mezzanotte, limiti nel codice, moneta oltre il 60%, cosa fare quando G1 non decide, e le voci di prima.
3. In più, il «riparti» ora si rifiuta (e si consuma) se il conto non è vuoto: dopo uno stop con una chiusura fallita va ripremuto
   quando l'allarme del fermo sparisce. Va bene così?

### Domande aperte

1. `reviews/` risulta ancora non committata in questo working tree: il commit a parte è stato fatto altrove o è ancora da fare?
