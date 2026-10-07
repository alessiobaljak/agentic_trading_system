# Lezioni di metodo

Solo errori di metodo e trappole dei dati: mai idee, meccanismi o risultati. Si legge
all'inizio di ogni campagna. Dopo la prova di processo resta congelato fino al Passo 7.

## 2026-10-06 (Passo 0)
* La rete della sessione di lavoro può bloccare l'host dei dati: si verifica l'accesso
  PRIMA di scrivere un'ipotesi, non dopo (il 6 ott data.binance.vision e fapi.binance.com
  erano bloccati dall'ambiente).

## 2026-10-07 (prova di processo, Passo 2)

Dalle proposte delle tre campagne della prova, filtrate dal coordinamento: solo metodo e
trappole dei dati. Quelle che sono diventate regole stanno nella versione 4.4 del protocollo
(stima dei trade, «nettamente», trade minimi, budget) e qui non si ripetono.

### La sessione e il guardiano
* **Il guardiano legge la forma dei comandi, non le intenzioni.** Nella prova ha rifiutato
  comandi innocui per la loro forma: la parola `.venv` in un comando, `python3 -c`, testi con
  virgolette triple dentro un heredoc, messaggi di commit su più righe dentro `-m`, `$?`,
  `2>&1`, la cartella madre `data/insample/` (sono ammesse solo le sottocartelle della moneta e
  di BTCUSDT), la parola «bot» dentro un testo, la lettura di `src/guardiano.py`. Regole
  pratiche: file e testi si scrivono con lo strumento di scrittura dei file, mai con heredoc; il
  messaggio di commit si scrive in un file dentro `data/insample/<SIMBOLO>/` (ammessa e fuori da
  git) e si passa con `git commit -F`; i comandi restano semplici, senza redirezioni né variabili
  della shell. Con git: la storia dei commit si legge solo per la propria cartella
  (`git log -- research/campagne/<SIMBOLO>/`, senza `-p`); `fetch`, `pull` e `push` solo con il nome
  del proprio branch; `git diff` solo contro HEAD; niente merge, rebase, cherry-pick, revert. Le
  pagine web si aprono solo da siti di pubblicazioni e da Wikipedia. Un rifiuto si registra nel log
  e non si aggira.
* **Il primo push si fa nei primi minuti.** Una sessione della prova è nata senza il permesso di
  scrivere sul repository e lo ha scoperto dopo, perdendo il lavoro locale. Se il primo push
  fallisce: STOP e avvisa l'utente.
* **I test che scrivono nel log vanno in serie.** Gli `id` del log sono progressivi in un file
  solo: due lotti lanciati in parallelo possono prendere lo stesso `id`.

### I dati
* **Il mark price ha buchi che il last price non ha**, in giorni diversi da moneta a moneta
  (anche giorni interi). Il motore vuole le serie allineate barra per barra: in Fase 0 si fa
  l'intersezione delle barre di last, serie dello stop e mark, e si dichiarano le barre tolte
  (il motore conta i buchi che restano). La scelta si scrive prima di ogni test, non nel codice
  delle varianti.
* **`Candela.volume` è in moneta base, non in USDT.** Per il volume in USDT serve la colonna
  `quote_volume` dei CSV, oppure volume per chiusura (un'approssimazione, da dichiarare).
* **I dati di riferimento di BTCUSDT servono sugli stessi timeframe della moneta.** Scaricali
  tutti in Fase 0: senza, il controllo «è solo il mercato» resta vuoto proprio dove serve.
* **La fascia di slippage del 2023 può essere ottimista per gli anni prima**, quando il volume
  era più basso: guarda il volume medio per anno in Fase 0 e dichiaralo; il test a costi doppi
  copre solo in parte.
* **Un periodo tolto perché sotto la liquidità minima sposta la divisione 70/30** calcolata in
  Fase 0 dal primo mese di dati: le date di costruzione e validazione restano quelle scritte
  prima dei prezzi, e la differenza si dichiara in Fase 0.
* **Le impronte dei file sono centinaia**: stanno meglio in un file `impronte.json` accanto a
  `fase0_dati.md`, con l'impronta di quel file scritta dentro `fase0_dati.md`.

### Il metodo
* **Prima della prima variante, un controllo positivo degli strumenti.** Una strategia che legge
  di proposito la barra successiva (lookahead dichiarato), con la stessa uscita e le stesse
  baseline delle varianti vere, deve battere nettamente il caso e crollare con il ritardo di una
  barra. Costa pochi minuti e si registra come nota (non è una variante, non consuma budget): se
  non passa, nessun risultato della campagna vale.
* **Le previsioni si scrivono al netto dei costi.** Prima di scriverle calcola il costo di un
  giro (commissioni e slippage, andata e ritorno) in R, con la distanza tipica dello stop sul
  timeframe: sulle durate brevi i costi sono una parte grande del movimento.
* **In Fase 2 guarda sempre l'R per anno e l'R medio senza i 3 trade migliori**, non solo il
  totale: pochi trade estremi o un solo anno favorevole possono fare un buon totale.
* **La baseline (a) e la (b) misurano cose diverse.** Su timeframe corti la (a) è dominata dai
  costi, e un candidato la batte anche solo entrando meno spesso; il confronto che smaschera è
  la (b), con lo stesso numero di trade.
* **Una stessa fonte non dovrebbe dare più di due varianti fra le idee nuove**: due direzioni per
  due condizioni alzano la probabilità di un falso positivo dentro un'idea sola. I ritocchi della
  regola 6 sono un'altra cosa e si dichiarano con `ritocco_di`.
* **Uno stop in ATR su candele lente supera spesso il tetto di stop del 6% del bot**
  (`config/parametri.yaml`, `stop_massimo_bot`): chi disegna idee lente lo sappia prima, e scelga
  fra stop in percentuale e un'idea che il bot non può eseguire così com'è (da dichiarare).
* **Con poche decine di trade «nettamente» chiede un vantaggio grande rispetto al rumore di un
  singolo trade**: la potenza è bassa (sezione 11). Non è un motivo per cambiare criterio in
  campagna.
