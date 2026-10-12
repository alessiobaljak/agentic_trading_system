# MATICUSDT — lezioni di metodo proposte (solo metodo e trappole dei dati)

* **I comandi e il guardiano.** Rifiutati per la forma, anche se leciti: più comandi git uniti con
  `&&` e una pipe; `cd` nella cartella `research/`; la lettura del file di uscita di un comando in
  background (sta sotto `/tmp`, fuori dai percorsi ammessi); `python -c`. Regola pratica: ogni
  script lungo scrive il suo rapporto in un file dentro la cartella della campagna o in
  `data/insample/<SIMBOLO>/`, e lo si legge da lì.
* **Contare tutte le varianti prima di registrarle accelera e non costa nulla:** i conteggi dicono
  subito quali idee non arrivano a 70 trade; allentare le soglie si scrive in `ipotesi.md` prima
  del primo test di quell'idea.
* **Con il tetto di stop del 6% e una moneta molto volatile** (ATR giornaliero mediano 10%) le
  idee su barre da 4h in su hanno di fatto lo stop fisso al 6%: le loro R dipendono dalla durata
  della tenuta più che dall'ingresso. Conviene saperlo prima di scegliere idee lente.
* **Un risultato di ricerca web può portare informazioni dopo il 2023 sulla moneta** (titolo e
  riassunto di un articolo del 2024). Scrivere nel log cosa si è visto e togliere l'idea collegata.
* **Il ritardo di una barra boccia anche senza lookahead.** Un effetto vero ma di poche ore crolla
  col ritardo di un'ora quanto un errore di codice; il controllo meccanico (ricalcolo del segnale
  sulla serie troncata alla barra) distingue i due casi in pochi minuti e conviene farlo sempre
  quando il ritardo fa crollare il `t`.
* **I ritocchi in sequenza su una sola famiglia** (cinque, scelti guardando il risultato
  precedente) hanno portato un candidato appena sopra la soglia che non ha retto le verifiche:
  il tetto di 5 ritocchi non basta da solo a evitare la salita a tentativi; la Fase 4 l'ha fermata.
