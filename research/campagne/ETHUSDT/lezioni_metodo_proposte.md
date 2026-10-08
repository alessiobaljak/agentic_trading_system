# ETHUSDT — Lezioni di metodo proposte

Solo errori di metodo e trappole dei dati (sezione 10): niente idee, meccanismi o risultati.
Restano in questa cartella fino al Passo 7, quando il coordinamento decide cosa entra in
`lezioni/metodo.md`.

## La sessione e il guardiano

* **L'output dei comandi lanciati in background sta in /tmp, fuori dai percorsi ammessi.** Il
  guardiano rifiuta di leggerlo (voce ETHUSDT-N003). Regola pratica: ogni script lungo scrive
  da se' il proprio esito in `data/insample/<SIMBOLO>/` (per esempio `lavoro/lotto.txt`) e la
  sessione legge solo li'. Va scritto in `lezioni/metodo.md`: costa un rifiuto a ogni campagna.
* **Due rifiuti miei per forme gia' note** (`python -c`, `2>&1` dopo `git push`: voci N007 e
  N009). Le lezioni le dicevano gia'; l'errore e' stato non rileggerle prima di un comando
  "veloce". Proposta: uno script `riassunto.py` per leggere i JSON degli esiti, cosi' nessuno
  e' tentato da `python -c`.
* **pytest non era installato** nella macchina della sessione: va installato prima dei test
  del guardiano (voce N001). Anche numpy, scipy e pyyaml.

## Il protocollo

* **Una variante che batte nettamente la (a) e la (b) ma con R medio dopo i costi negativo**
  (ETHUSDT-012) non e' un candidato (sezione 8) e, alla lettera della regola 6, non entra
  nemmeno nell'ordine dei ritocchi, che esclude chi "ha gia' battuto nettamente sia la (a) sia
  la (b)" pensando che sia un candidato. Il testo ha un buco: va deciso se una variante cosi'
  si puo' ritoccare (per esempio per ridurre i costi) o no. Qui non e' contato, perche' le
  idee nuove hanno riempito il budget (voce N013).
* **Il criterio del ritardo chiama "crollo" anche un calo vero di una strategia che non puo'
  vedere il futuro** (ETHUSDT-026: t da 2,67 a 1,27, soglia 1,33). Il protocollo chiede di
  cercare l'errore; un controllo semplice e decisivo e' scrivere quali dati esterni la
  variante legge oltre alle barre chiuse del motore (serie completa, BTC, funding, altre
  colonne): se nessuno, il lookahead non e' possibile (voce N014). Proposta: aggiungere questo
  controllo alla Fase 4, per non lasciare un candidato fermo su un sospetto.
* **Un'idea scelta come il contrario di un fallimento sui dati di costruzione non e' un
  vantaggio solo per questo.** ETHUSDT-034 (dal fallimento sistematico di I-13, con fonte) e'
  venuta vicina al caso (t 1,17): il fallimento veniva in parte dallo stop, non dal
  meccanismo. Il protocollo la ammette (Fase 3), ma la selezione va dichiarata nella
  registrazione, come qui.
* **Il budget si riempie con idee nuove prima dei ritocchi** (regola 6): con 30 unita' e 14
  idee da due varianti, le idee nuove "trovate dopo" (qui I-15 ... I-18, scritte dopo aver
  visto i primi risultati) prendono le ultime unita'. Va dichiarato in `ipotesi.md` che sono
  state scritte dopo, e perche' non nascono da quei risultati.

## Strumenti

* **Contare e registrare nello stesso script.** `codice/registra.py` chiama `conta_trade` e
  scrive SUBITO la registrazione o lo scarto: nessun conteggio resta fuori dal log, e una
  variante gia' contata non si riconta. `codice/lotto.py` mette in serie conta, registrazione
  e test di piu' varianti. Proposta per tutte le campagne.
* **Prova del codice senza conteggi.** Prima di contare, far girare le quattro fabbriche
  (variante, (a), casuale, segnale) su un pezzo di dati e stampare solo "ok" o l'errore
  (`codice/prova_codice.py`): trova i difetti senza vedere numeri di regole non registrate.
* **Memoria della (b) con molti trade.** `entrate_casuali` costruisce una tabella di
  barre x trade in virgola mobile: con 24.500 barre a 1 ora e 1.600 trade sono circa 300 MB;
  a 15 minuti con migliaia di trade si va su piu' GB. Si puo' fare, ma va saputo prima.
* **La (a) con uscita a tempo fa molti piu' trade della variante** (entra a ogni barra
  libera): per uscite di una barra a 30 minuti sono decine di migliaia di trade; il bootstrap
  regge (16 GB di memoria), ma il tempo cresce.

## I dati

* **ETHUSDT: il mark price manca per due giorni interi** (2022-10-02 e 2023-02-24) e per due
  barre singole a 15 minuti; il last price e' completo. Confermata la lezione
  dell'intersezione delle barre.
* **La quota di volume comprato a mercato** (colonna `taker_buy_volume`, la decima dei file
  klines) c'e' in tutti i mesi 2020-2023: si puo' usare, ma le candele del motore non la
  portano e va letta a parte (`Serie.taker` in `codice/comune.py`).
* **Su ETH 2020-2022 l'ATR giornaliero mediano e' il 7%**, sopra il tetto di stop del bot
  (6%): a 1 giorno ogni stop in ATR viene tagliato al 6%, cioe' sotto 1 ATR. Con uno stop
  cosi' stretto un periodo di rialzo vale molto in R anche per entrate casuali (la (b) dei long
  settimanali fa +0,17 R): le previsioni in R vanno fatte guardando la (b), non solo i costi.
* **Lo slippage della scheda (0,01%) viene dal volume del 2023**; nel 2020 il volume era un
  decimo (0,72 miliardi al giorno): per i risultati del 2020 i costi sono ottimisti.
