# Campagna di gruppo — lezioni di metodo proposte

Solo metodo e trappole dei dati (protocollo, sezione 10). Proposte per `lezioni/metodo.md` al Passo 7.

* **Il controllo positivo dipende dall'uscita.** Con un'uscita a più giorni il vantaggio di un ingresso che vede la
  barra dopo si diluisce e può non battere nettamente la (a) di gruppo (t 1,96 con tenuta 7). Fare il controllo
  positivo con l'uscita più corta che la campagna userà, e saperlo prima.
* **La (a) di gruppo ha poca potenza con tenute lunghe.** Il suo errore è la somma pesata degli errori per moneta
  (monete trattate come se si muovessero insieme): con circa 80-140 trade della (a) per moneta vale 0,07 R. Chi
  disegna idee su 1d a più giorni lo sappia prima.
* **Il pavimento delle sfasate decide quasi sempre.** Molte varianti stanno al 99-100° percentile delle simulazioni
  casuali ma non battono il pavimento: guardare l'effetto grappolo e il numero di blocchi prima di innamorarsi del
  percentile. Le idee con ingressi sincronizzati fra monete (calendario, rotture nei rialzi comuni, crolli comuni)
  hanno pochi blocchi.
* **Soglia e trade: c'è un punto di equilibrio.** Allentare una condizione d'ingresso aumenta i blocchi più di
  quanto riduca l'R per trade fino a un certo punto (t 0,91 → 1,44 → 1,80 → 1,89 in I-19), poi si appiattisce.
* **Costi in R prima delle previsioni, per timeframe:** a 1 ora un giro costa circa 0,07 R con stop a 2 ATR; allargare
  lo stop non cambia il rapporto fra costi e movimento.
* **Strumenti di forma:** l'orario delle voci del log va preso dall'orologio della macchina dentro lo script che
  scrive la voce (una volta l'ho scritto a memoria: correzione GRUPPO-013); il messaggio di commit sempre da file
  (`-m` con l'indirizzo della sessione viene rifiutato); niente redirezioni dopo `git push`; le ricerche con schemi
  che contengono «/» vanno fatte con lo strumento di ricerca, non con grep nella shell.
* **Lotti di varianti:** uno script che per ogni variante conta, registra e poi testa, in serie, tiene gli id
  progressivi e la registrazione prima del test; i risultati si scrivono dopo, a parte.
