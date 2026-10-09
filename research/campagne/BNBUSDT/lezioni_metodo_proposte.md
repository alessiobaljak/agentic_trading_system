# BNBUSDT — lezioni di metodo proposte

Solo errori di metodo e trappole dei dati, per `lezioni/metodo.md` al Passo 7.

* **Medie mobili con la somma cumulata e NaN iniziali.** Una media calcolata con la somma cumulata
  propaga un NaN iniziale a tutta la serie: la condizione non è mai vera e la variante esce con 0
  trade, che sembra uno scarto legittimo. Un conteggio di 0 trade va sempre controllato prima di
  registrarlo come scarto (BNBUSDT-N013).
* **Prima di fissare il parametro di un ritocco, guardare la distribuzione della grandezza che si
  taglia, non solo i gruppi.** Un'uscita a tempo di 12 barre su trade con durata mediana 4 non
  tocca quasi nulla e brucia una variante del budget (BNBUSDT-N019).
* **Il guardiano e l'uscita dei comandi in background.** Il file d'uscita di un comando in
  background sta in una cartella temporanea che il guardiano non lascia leggere, e lo strumento di
  monitoraggio non è ammesso: gli script lunghi devono scrivere da soli il loro esito in
  `data/insample/<SIMBOLO>/`, e per aspettarne la fine si usa un comando in background che
  controlla quel file.
* **Messaggi di commit col trailer in `-m`.** Il guardiano legge l'indirizzo della sessione come
  percorso e rifiuta: va sempre `git commit -F` (già in `metodo.md`, ma l'ho sbagliato lo stesso:
  vale la pena metterlo in cima).
* **Un filtro che sceglie le ore volatili abbassa i costi in R e la (b) non lo sa.** Contro la (b)
  normale una regola con un filtro sulla volatilità vince anche solo perché entra dove lo stop è
  largo e i costi pesano meno. La prova utile è la (b) ristretta alle stesse barre del filtro
  (`vieta_extra` in `codice/comune.py`): proporla come verifica standard per ogni candidato con un
  filtro (BNBUSDT-043, N022).
* **Il controllo positivo col ritardo non va a zero se lo stop si calcola dalla barra di segnale.**
  Con il ritardo, una regola che entra dopo un movimento nella sua direzione ha lo stop più largo
  in prezzo e costi più bassi in R della (b): il t non crolla a zero ma a circa 4 (N009). Nel
  controllo positivo va letto anche l'R medio, che deve diventare non positivo.
* **Con il minimo in costruzione a 70 i candidati nati da filtri restano vicini al minimo** e in
  validazione arrivano a 30-32 trade: l'esito dipende da 2-3 trade.
