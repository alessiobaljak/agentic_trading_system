# LINKUSDT — lezioni di metodo proposte

Solo errori di metodo e trappole dei dati.

* **Il guardiano rifiuta anche la cartella temporanea della sessione.** L'uscita di un comando lanciato in
  background finisce in `/tmp/...`, che il guardiano non lascia leggere: i comandi lunghi vanno lanciati
  in primo piano con un timeout lungo, oppure devono scrivere da soli il loro esito in
  `data/insample/<SIMBOLO>/`. Lo scarico di tutti i timeframe di BTCUSDT supera i 10 minuti.
* **Altre forme di comando rifiutate**: `sed -i '/testo/d'` (l'espressione fra barre è letta come un
  percorso), il trailer del commit passato con `-m` (l'indirizzo è letto come un percorso), `ls` della
  cartella madre `campagne/`. Il trailer va sempre in un file con `git commit -F`.
* **Siti delle pubblicazioni**: le pagine di istituti come cesifo.org non sono ammesse; la stessa scheda
  si trova su ideas.repec.org.
* **Il mark price di LINKUSDT manca per giornate intere** (2021-07-01, 2021-07-24..27, 2022-07-31,
  2022-10-02, 2023-02-24): l'allineamento toglie quelle giornate su tutti i timeframe.
* **I file dell'archivio partono dal listing (2020-01-17), non dal primo del mese**: il primo mese di
  dati della scheda non dice il primo giorno.
* **Con un'uscita «dopo una barra» la baseline (a) entra un giorno sì e uno no**: alla chiusura della
  barra in cui la posizione è ancora aperta (l'uscita è all'apertura dopo) la strategia non può emettere
  un nuovo segnale. Va saputo quando si legge il numero di trade della (a).
* **Uno script che conta, registra ed esegue in serie** (conta_trade, poi registrazione o scarto, poi
  test, poi risultato) evita di contare regole non registrate e rende impossibile testare prima di
  registrare; se si interrompe dopo la registrazione, riprende dal test senza contare di nuovo.
