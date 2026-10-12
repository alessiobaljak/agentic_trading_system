# Lezioni di metodo proposte (MASKUSDT)

Solo metodo e trappole dei dati.

* **Il primo mese della scheda può non essere pieno.** Per MASKUSDT i file di agosto 2021 partono
  dal 26-27: la costruzione utile è di 592 giorni invece dei 618 calcolati dal primo giorno del
  mese. La regola delle date resta; va solo saputo che il minimo di 70 trade è più duro.
* **Nella strategia il segnale (con il riscaldamento) va valutato prima della condizione.** Una
  condizione che legge una finestra di barre fallisce alle prime barre se si valuta prima del
  controllo di riscaldamento: `conta_trade` si interrompe (nessun conteggio prodotto, ma lo si
  deve dichiarare).
* **I nomi dei campi della (b) nel log possono sovrapporsi**: `errore_standard` dell'esito di
  `contro_baseline` (errore della differenza) e quello del dizionario della baseline (errore della
  sua media) hanno lo stesso nome; unire i due dizionari ne perde uno. Tenerli con nomi diversi.
* **Gli script in background non possono scrivere l'uscita dove la sessione la legge** (cartella
  temporanea fuori dai percorsi ammessi): gli script devono scrivere i loro esiti in
  `data/insample/<SIMBOLO>/` e nel log, non sullo schermo.
* **Il messaggio di commit con `-m` contenente l'indirizzo della sessione viene rifiutato** dal
  guardiano: sempre `git commit -F` con il file in `data/insample/<SIMBOLO>/` (già scritto in
  `lezioni/metodo.md`, ricordato perché è capitato).
* **Ritocchi tutti su una famiglia**: con l'ordine della regola 6, quando una sola famiglia è
  vicina alla soglia, i 5 ritocchi vanno tutti lì e il candidato che ne esce è il migliore di 7
  varianti della stessa idea. Qui la validazione lo ha bocciato: è il comportamento atteso del
  protocollo, ma va letto così quando un candidato viene da ritocchi.
