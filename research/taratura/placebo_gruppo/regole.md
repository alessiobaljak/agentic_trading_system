# Prova a placebo dell'esame di gruppo — regole scritte PRIMA dei numeri

> **BOZZA.** Scritte dal coordinamento il 10 ottobre 2026, prima di calcolare qualunque risultato, come chiede
> `research/campagne/GRUPPO/regole.md`, sezione 11 (approvato in anticipo dal proprietario il 10 ottobre alle 06:35
> UTC). Questo file si committa e si pusha prima del lancio, con le impronte degli strumenti (punto 7) al posto di
> questa riga: l'hash del commit va in `risultati.md`. Dopo il lancio le regole non cambiano; un errore trovato si
> corregge con una voce nuova in `risultati.md`, che dice cosa è cambiato e perché, e si rilancia tutto.

## 1. La domanda

Sui prezzi **veri** delle 80 monete del gruppo, l'esame di gruppo (`regole.md`, sezioni 4-7: trade sommati, blocco
sui trade di tutte le monete, (a) e (b) combinate, pavimento delle strategie sfasate, `contro_baseline`) promuove
strategie **senza vantaggio** più spesso di quanto dichiara la sezione 11 del protocollo, anche quando i loro trade
cadono a grappoli sulle monete negli stessi giorni? La prova del 9 ottobre (`taratura/placebo/`) ha misurato l'esame
moneta per moneta; questa misura l'esame di gruppo.

## 2. I dati

* Le 80 monete di `research/campagne/GRUPPO/monete.csv`, nessun'altra.
* Da data.binance.vision, solo fino al **2023-12-31**, scaricati con `research/src/dati.py` (che rifiuta ogni data
  oltre) in una radice fuori da git: candele a 1 ora e a 4 ore del last e del mark, candele giornaliere del last (per il filtro di liquidità) e del mark,
  funding. Il 10 ottobre lo scarico ha dato, per le 80 monete, 3.061 mesi di candele a 1
  ora del last e del mark e 3.044 mesi di funding (17 mesi senza file: buchi, il funding lì vale zero). Il vault non
  si tocca.
* Due timeframe: 1 ora e 4 ore, dai file mensili di quel timeframe (last e mark) scaricati con `research/src/dati.py`,
  come li scarica la sessione (`regole.md`, sezione 2, punto 3). Si leggono solo con `gruppo.CaricatoreDisco` (anche
  per calcolare gli istanti di segnale), senza un caricatore della prova.
* Periodi, filtro di liquidità, parametri di ogni moneta, costi, last e mark allineati: esattamente quelli della
  sessione di gruppo, perché tutto passa da `research/src/gruppo.py` (`regole.md`, sezioni 1, 2 e 13). Costruzione
  fino al 2023-01-16, validazione dal 2023-01-17 al 2023-12-31.

## 3. Le strategie placebo

Una placebo per timeframe, regola e direzione (long e short separate), con 4 sfasamenti (k da 0 a 3): 6 regole × 2
direzioni × 2 timeframe × 4 = **96 placebo per periodo**.

1. **Regola d'ingresso da manuale**, la stessa della prova del 9 ottobre (`taratura/placebo/regole.md`, punto 3.1),
   calcolata sui prezzi veri di ogni moneta alla chiusura della barra: incrocio delle medie 20/50; RSI(14) che esce
   da 30 (long) o rientra sotto 70 (short); chiusura oltre il massimo (long) o sotto il minimo (short) delle 20 barre
   precedenti; chiusura fuori dalla banda di Bollinger (20, 2) inferiore (long) o superiore (short); incrocio del MACD
   (12, 26, 9) con la sua linea del segnale; rendimento a 10 barre che passa sopra (long) o sotto (short) lo zero.
2. **Lo sfasamento comune.** Un solo intero d per placebo, uniforme fra il margine e L − margine, con seme crc32
   dell'etichetta «GRUPPO|timeframe|regola|direzione|periodo|k». L è il numero di barre della finestra unione del
   periodo contate sul calendario (in costruzione dal primo giorno di dati più antico al 2023-01-16, in validazione dal
   2023-01-17 al 2023-12-31); il margine è 30 giorni di barre (720 a 1 ora, 180 a 4 ore), al massimo L // 4. Gli
   istanti di segnale di **tutte** le monete si spostano dello stesso d, in cerchio sulla finestra unione: due
   segnali dello stesso giorno su monete diverse restano nello stesso giorno, quindi i grappoli fra monete restano
   com'erano, ma cadono in momenti scelti a caso, a più di 30 giorni da dove la regola li ha calcolati. La placebo
   **non ha nessun vantaggio** per costruzione. Un istante spostato che cade fuori dalla finestra della sua moneta, in
   una barra che manca o in una barra vietata (riscaldamento, mesi sotto la liquidità, segnale non valido, e in
   validazione le barre prima del 2023-01-17) si salta e si conta.
3. **L'uscita** (la stessa per placebo, (a), (b) e strategie sfasate), con l'ATR(14) alla barra di segnale, come il 9
   ottobre (punto 3.3): per incrocio delle medie, rottura e MACD stop a 1,5 ATR e target a 2,5 ATR; per RSI,
   Bollinger e momento stop a 2 ATR, nessun target, chiusura dopo 24 barre a 1 ora e 12 a 4 ore.
4. Le prime 60 barre di ogni serie non hanno segnali (riscaldamento).
5. Gli ingressi della placebo si passano a `gruppo.py` con l'argomento `ingressi_placebo` (`regole.md`, sezione 13: gli
   ingressi già calcolati per moneta, al posto della funzione che crea la strategia della variante; la (a), la
   strategia casuale e il segnale restano le funzioni di un modulo come quelli della sessione). Il resto dell'esame è
   identico a quello della sessione. La prova gira senza marcatore di campagna, come chiede `regole.md`.

## 4. Il giudizio

* **Costruzione**: `gruppo.conta_trade_di_gruppo` e `gruppo.esame_di_gruppo` come per una variante della sessione.
  Una placebo sotto 700 trade sommati o con una moneta oltre il 10% è uno scarto e non si giudica. È valutabile se il
  confronto con la (b) è valutabile.
* **Validazione**: la stessa placebo, sfasata con il suo seme sulla finestra di validazione, si giudica se ha almeno
  300 trade sommati: p_value contro la (b) di gruppo di validazione, con il pavimento delle sfasate.
* Il controllo del via libera di `esame_di_gruppo` in validazione c'è solo con un marcatore di campagna (`regole.md`,
  sezione 7, punto 2): la prova gira senza marcatore e non lo incontra (è la prova che produce il via libera).

## 5. Le misure e le soglie (`regole.md`, sezione 11, punto 3)

Prima di qualunque quota, due controlli, nell'ordine; se uno manca si stampano solo i conteggi e ci si ferma:
* **Copertura**: ci sono tutte le 24 combinazioni × 4 sfasamenti × 2 periodi; gli errori si contano e si elencano.
* **Campione**: almeno **80** placebo valutabili in costruzione (con almeno 700 trade e nessuna moneta oltre il 10%) e
  80 in validazione (con almeno 300 trade). Se in un periodo sono meno, si
  aggiungono sfasamenti k = 4, 5, … a tutte le combinazioni, decisi sul solo conteggio.

Ogni placebo valutabile ha z = Φ⁻¹(1 − p_value) del confronto con la (b). L'esame **regge** se valgono tutte:
* **M1**: in costruzione, le placebo «nette» contro la (b) sono al massimo ⌊0,03 · n⌋ (n = valutabili in costruzione);
* **M2**: in validazione, le placebo con p sotto 0,10 sono al massimo ⌊0,13 · n⌋ (n = valutabili in validazione);
* **M3**: con μ e σ (ddof 1) degli z di ciascun periodo, 1 − Φ((2,00 − μ) / σ) è al massimo 3% in costruzione e
  1 − Φ((1,2816 − μ) / σ) è al massimo 13% in validazione.

Le soglie 3% e 13% sono quelle della prova del 9 ottobre (il 2% e l'11% dichiarati più un margine); la M3 usa tutte le
placebo, perché con 80-100 placebo le quote contate le sposta una placebo sola. Si riportano, senza che decidano:
μ e σ degli z per periodo; le stesse misure calcolate **senza** il pavimento delle sfasate (cioè con il solo pavimento
della (b)); sulle placebo dove il pavimento delle sfasate decide, la deviazione standard di (R medio − B) divisa per
il pavimento (se supera 1,10, la correzione da proporre al proprietario è togliere la radice di n'/N dal pavimento,
`regole.md` sezione 5, punto 5); la quota di placebo con R medio sopra il 90° percentile delle proprie sfasate in
validazione (atteso circa 10%); l'effetto grappolo; la quota della moneta più presente; gli intervalli al 95%
ricampionando le 24 combinazioni (2.000 volte, seme 0); le misure per timeframe, direzione e regola.

**Riproducibilità.** Un file di esiti per sfasamento (`esiti_k<k>.jsonl`); ogni riga porta l'hash del commit del
codice e le cinque impronte del punto 7, e il lancio rifiuta codice non committato o con impronte diverse.

## 6. Cosa succede dopo (scritto prima)

* **M1, M2 e M3 reggono** → «l'esame di gruppo regge sui prezzi veri». Il coordinamento scrive il via libera quando la
  sessione di gruppo lo chiede (`regole.md`, sezione 7, punto 2), con le cinque impronte del punto 7. I numeri restano
  su questo branch fino alla consegna del gruppo (`regole.md`, sezione 11, punto 5).
* **Una cade** → «l'esame di gruppo non regge». STOP: il coordinamento ferma la sessione di gruppo e porta i numeri
  al proprietario con una correzione dell'esame scritta guardando solo i numeri di questa prova; la correzione si
  riprova con sfasamenti nuovi (k da 10 in su), stesse regole, in un file separato. Se il proprietario cambia l'esame,
  vale `regole.md`, sezione 11, punto 2 (archivio del branch e campagna da rifare). Decide il proprietario.
* Se una delle cinque impronte cambia durante la campagna, la prova si rifà intera con i file nuovi, le stesse regole
  e gli stessi sfasamenti, prima del via libera.

## 7. Gli strumenti (impronte SHA-256 al commit del lancio)

Da scrivere al posto della riga BOZZA prima del lancio: `research/src/gruppo.py`, `research/src/statistica.py`,
`research/src/motore.py`, `research/src/dati.py`, `research/config/parametri.yaml`, con l'hash del commit del branch
principale da cui vengono. Il codice della prova (`placebo_gruppo.py`, `esegui.py`, `riassunto.py`) sta in questa
cartella e non entra nelle impronte.

## 8. Cosa la prova non dice

Non dice se esistono vantaggi veri; non prova le verifiche della Fase 4; usa regole d'ingresso e uscite fisse, non
le idee della sessione; usa solo regole che guardano una moneta (le strategie fra monete sono escluse dalla campagna,
`regole.md` sezione 3, punto 3). Dove decide il pavimento delle sfasate regge in parte per costruzione, perché la
placebo e il pavimento spostano gli ingressi allo stesso modo: per questo riporta le misure senza pavimento. Misura
una cosa sola: quante volte l'esame di gruppo scambia per vantaggio una strategia che non ne ha, sui prezzi veri.
