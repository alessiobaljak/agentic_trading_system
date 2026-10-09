# Lezioni di metodo proposte (campagna DOGEUSDT)

Solo errori di metodo e trappole dei dati.

* **Il filtro di liquidità può togliere un terzo della costruzione.** Per DOGEUSDT tutti i mesi
  del 2020 sono sotto i 20 milioni al giorno: la costruzione utile scende da 895 a 711 giorni e
  le idee a 1d e 4h perdono trade. Conviene guardare i mesi illiquidi prima di scegliere i
  timeframe delle idee.
* **Il guardiano rifiuta comandi di servizio comuni**, oltre a quelli già in `metodo.md`: la
  lettura dell'uscita dei comandi in background (l'ambiente la scrive fuori dai percorsi
  ammessi), lo strumento di monitoraggio, i percorsi relativi con `..` o senza la radice
  `research/`, `sed` con testi che contengono spazi, `-m` ripetuti nel commit. Soluzione che ha
  funzionato: ogni script scrive le sue uscite in `data/insample/<SIMBOLO>/` e un piccolo script
  in Python aspetta una parola in quel file; le modifiche ai file con lo strumento di modifica.
* **Lo scarico di circa 1.200 file mensili con il CHECKSUM richiede 20-30 minuti** e può
  interrompersi: lo script deve riprovare per mese e scrivere un suo log, perché un errore in
  background non è leggibile.
* **Pytest può mancare nella macchina della sessione**: va installato prima dei test del
  guardiano (`pip install pytest numpy scipy pyyaml`).
* **I ritocchi della regola 6 tendono a concentrarsi su una famiglia sola**: quando le idee nuove
  sono tutte lontane dalla soglia, la prima della lista resta prima anche dopo i suoi ritocchi, e
  i 5 ritocchi diventano una salita su una variante. Qui la salita ha prodotto un candidato al
  limite della soglia che la Fase 4 ha fermato: le verifiche di robustezza e dei costi doppi sono
  il freno che serve, e vanno fatte prima di ogni entusiasmo.
