# Lezioni di metodo proposte (GALAUSDT)

Solo metodo e trappole dei dati.

* **Non aggiungere varianti a un'idea mentre i test sono già lanciati.** Qui i test girano in pochi
  secondi: una variante allentata scritta subito dopo aver lanciato i test in background è arrivata
  8 secondi dopo il primo risultato della sua idea ed è stata ritirata. Prima si scrivono tutte le
  varianti, poi si lancia.
* **Conteggio e registrazione nello stesso passo.** Uno script che conta i trade con `conta_trade` e
  scrive subito la registrazione (o lo scarto) evita di contare regole che poi non si registrano.
* **Test paralleli e log unico**: con gli id assegnati prima e un blocco di file sulla scrittura del
  log, tre processi in parallelo non si sovrappongono.
* **Un controllo di causalità meccanico**: calcolare condizione e segnale sulla serie intera e su
  serie troncate e confrontarli trova la lettura del futuro nel codice delle varianti (provato sul
  controllo positivo, che la fa apposta). Costa un minuto per tutte le varianti.
* **Il guardiano rifiuta anche `$` e `$(...)`** in ricerche e cicli di attesa, oltre a quanto già
  scritto: per aspettare la fine dei test in background serve un piccolo script nella cartella del
  codice (il file di uscita dei comandi in background sta fuori da `research/` e non si legge).
* **Le varianti allentate dopo uno scarto vanno scritte con la loro idea**, prima del primo test
  dell'idea: dopo il conteggio di tutte le varianti, prima di lanciare qualunque test.
* **A 1 ora il costo di un giro vale 0,05-0,10 R**: una variante che batte il caso di 0,06 R può
  avere R dopo i costi quasi zero e cadere ai costi doppi. Conviene guardarlo prima di scegliere il
  timeframe, non dopo.
