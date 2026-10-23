# Programma 7 — trading ogni giorno

Scritto il 23 ottobre 2026, prima di qualunque calcolo. Il proprietario: «io voglio anche fare trading tutti i giorni non solo
tenere una settimana (non te l'ho mai chiesto, anche se lo posso accettare come alternativa se è profittevole) [...] ti ho chiesto
di fare trading tutti i giorni».

## 1. Cosa si cerca

Strategie che **ogni giorno** aprono e chiudono posizioni, con regole d'entrata e d'uscita (stop, obiettivo, tempo massimo o cambio
del segnale), sui perpetui USDT-M di Binance, su più monete, che guadagnano dopo i costi in modo ripetibile. F5 (una settimana di
tenuta) resta un'alternativa accettata dal proprietario, non la risposta.

## 2. Cosa sappiamo già (programmi 5 e 6, `research/REGISTRO.md`)

* Gli indicatori da soli, a 5 minuti, 15 minuti, 1 ora, 4 ore e 1 giorno, perdono dopo i costi (prove 1, 2, 34-39, 46, 54): in un
  giorno il prezzo si muove soprattutto per caso, e il costo di ogni operazione è sicuro.
* Il vantaggio che regge è **fra le monete**: chi ha il funding alto (la leva cara) rende meno, chi lo ha basso di più (F5); e
  alcuni **eventi** (le monete al 7° giorno di vita, il funding che tocca il tetto).
* **I costi decidono**: a mercato un giro costa 0,12-0,14%, a limite 0,04% (prove 51, 54, 56).

## 3. Come si lavora (le regole del programma 6 restano)

* Regole scritte prima del calcolo (un file per prova, la riga nel registro), una prova per volta, nel conto unico delle prove.
* Le idee partono dai vantaggi che reggono (la direzione dal funding, gli eventi) e usano gli indicatori per **scegliere il
  momento** dell'entrata e dell'uscita dentro la giornata; le entrate e gli obiettivi a **ordine limite** dove si può.
* Esame: come il programma 6 (`terza.esame` e `terza.esito` sulle settimane, Sharpe corretto con l'aggiunta del 23 ottobre,
  soglia 0,95; accanto il t dello Sharpe contro 3). Si riportano sempre quante operazioni al giorno, la durata media, la quota
  vinte, vincita e perdita medie, i costi.
* Ogni strategia promettente passa da un **revisore separato** prima di andare nel paper.

## 4. La coda delle idee (in quest'ordine; i dettagli si fissano nel file di ogni prova, prima del calcolo)

1. ~~**G1 — F5 ogni giorno**~~ → prova 57: opera ogni giorno (3 entrate e 3 uscite), Sharpe 1,96, corretto 0,94; ma le posizioni
   durano in media 17,5 giorni: non è trading «in giornata».
2. **G2 — lo short del giorno sulle monete con la leva più cara**: entrata a limite su un rimbalzo dentro la giornata, stop e
   obiettivo dalla volatilità, uscita entro la fine del giorno.
3. **G3 — il long del giorno sulle monete con il funding più negativo**, lo specchio di G2.
4. **G4 — le monete nuove al 7° giorno e il funding al tetto con l'entrata scelta dentro la giornata** (oggi entrano a un'ora fissa).
