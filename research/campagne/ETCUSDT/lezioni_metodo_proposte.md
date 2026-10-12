# ETCUSDT — lezioni di metodo proposte (solo errori di metodo e trappole dei dati)

Proposte per `lezioni/metodo.md`, da valutare al Passo 7. Nessuna idea né risultato.

## La sessione e il guardiano
* **Le uscite dei comandi in background non si leggono**: stanno sotto `/tmp`, fuori dai percorsi ammessi.
  Gli script scrivono da soli la loro uscita in `data/insample/<SIMBOLO>/` (ammessa, fuori da git).
* **Rifiuti per la forma visti qui**, in aggiunta a quelli già elencati: `sed -i 's/.../.../'` (lo
  scambia per un percorso), `grep` con il motivo `'^--$'`, un commit con `-m` che contiene un indirizzo web,
  `ls` della cartella madre `data/insample/`, lo strumento Workflow (non ammesso in campagna). Per
  modificare un file si usa lo strumento di modifica, non `sed`.
* **Un comando che nomina un file fuori dai percorsi ammessi viene rifiutato anche se non lo legge** (es.
  `ls requirements*.txt`). pytest può mancare nella macchina: si installa con pip senza leggere i file
  del bot.
* **Uno script di note con id fissi, rilanciato dopo un errore, scriverebbe due volte lo stesso id** (qui
  evitato a mano: la nota prima del controllo positivo fallito era già nel log, e il secondo lancio ha
  usato id nuovi più una voce di correzione). Gli id delle note vanno generati o controllati prima di
  scrivere.

## I dati
* **Il primo mese di dati della scheda può cominciare a metà mese** (ETCUSDT: 2020-01-16). Le date restano
  quelle di `periodi_campagna`; i giorni senza dati si dichiarano.
* **Il mark price può mancare per giorni interi anche nella validazione** (qui 2022-10-02 e 2023-02-24): si
  elencano tutti in Fase 0, non solo quelli della costruzione.
* **Uno scarico interrotto perde l'elenco dei CHECKSUM mancanti di quel giro**: lo script di scarico
  dovrebbe scriverlo su file man mano.

## Il metodo
* **Il test del ritardo di una barra non misura un ritardo per le regole legate all'orologio** (es.
  «l'ultima mezz'ora del giorno UTC»): una barra dopo, l'ingresso cade fuori dalla finestra e il test prova
  una regola diversa. Il crollo va comunque cercato come errore (qui non c'era), ma per queste regole
  converrebbe dichiarare prima, nell'ipotesi, che il ritardo cambia la regola.
* **Per le regole legate all'ora del giorno la baseline (b) entra a ore casuali**: battere la (b) può voler
  dire solo «quest'ora è diversa dalle altre». Un controllo utile, da registrare prima: la stessa regola
  senza la condizione dell'ipotesi, solo all'ora scelta, e la stessa condizione alle altre ore (placebo).
* **A 30 minuti i costi da taker valgono circa 0,08 R a trade con lo stop a 2 ATR**: un'idea che batte
  nettamente il caso con R vicino a zero cade quasi sicuramente a costi doppi. Conviene calcolare il
  guadagno lordo in punti base contro il costo del giro già in Fase 3, prima dei ritocchi.
* **I ritocchi seguono il `t` contro la (b), non l'R**: una famiglia che batte il caso perdendo dopo i
  costi riceve tutti i ritocchi (qui 5 su 7), e i ritocchi diventano una ricerca della soglia che rende
  positivo l'R sui dati di costruzione. È quello che la regola chiede; la validazione e la verifica a costi
  doppi sono la difesa.
