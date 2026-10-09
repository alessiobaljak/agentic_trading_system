# Lezioni di metodo proposte (campagna AVAXUSDT)

Solo errori di metodo e trappole dei dati, niente idee né risultati da riusare.

1. **Il test del ritardo non distingue un lookahead da un effetto breve.** La regola della Fase 4
   («sotto la metà del `t` è un crollo; il candidato non va avanti finché l'errore non è trovato»)
   tratta ogni calo forte come un errore. In questa campagna un candidato è sceso a 0,494 volte il
   suo `t` (serviva 0,5); la ricerca dell'errore (segnali ricalcolati da capo, ingresso alla barra
   giusta, causalità degli indicatori verificata su serie troncate, profilo del rendimento barra per
   barra dopo il segnale) non ha trovato nulla. Un effetto vero che dura poche barre perde una parte
   grande del suo valore quando l'ingresso slitta di una barra. Proposta da valutare fuori dalle
   campagne: affiancare al rapporto dei `t` un controllo diretto del lookahead (la verifica di
   causalità su serie troncate e il profilo per barra), e decidere cosa fare quando il controllo
   diretto è pulito. Non l'ho applicata: ho seguito la regola com'è.
2. **Per una regola legata a un'ora del giorno il ritardo cambia il fenomeno**, non lo ritarda: un
   ingresso alle 23:30 ritardato di una barra entra alle 00:00. Il test misura un'altra strategia.
3. **Verifica di causalità degli indicatori.** Ricalcolare gli indicatori su serie troncate in punti
   casuali e confrontarli con quelli della serie intera costa pochi secondi e prende ogni uso del
   futuro negli array precalcolati (la strategia di controllo con lookahead dichiarato viene
   segnalata subito). Utile a ogni campagna che precalcola indicatori per velocità.
4. **Una barra dentro un buco di dati gonfia la durata media dei trade** (una posizione di
   mezz'ora che attraversa quattro giorni senza mark ne vale 192 barre): la durata media entra
   nella distanza minima degli ingressi della (b). Va guardata quando ci sono buchi lunghi.
5. **Il guardiano rifiuta anche i percorsi relativi verso cartelle ammesse** (`../../../data/...`) e
   ogni lettura dell'uscita di un comando in background (sta in `/tmp`): gli script lunghi devono
   scrivere il loro avanzamento in `data/insample/<SIMBOLO>/`. Anche `cd` nella cartella madre
   `research/` e `git show` sono rifiutati.
6. **Con stop all'apertura del giorno metà delle barre ha il segnale non valido**: la (a) e la (b)
   diventano molto negative (stop stretti, costi alti in R) e il confronto con la (a) diventa facile
   da battere. La (b) resta il confronto che conta (lo dice già il metodo).
7. **Il controllo positivo col ritardo resta sopra la soglia** (t 3,3 su 4.598 trade) per una lieve
   persistenza oraria vera dei prezzi: il criterio «crolla» va letto come rapporto, non come «non è
   più netto».
