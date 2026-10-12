# Lezioni di metodo proposte dalla campagna FILUSDT

Solo errori di metodo e trappole dei dati. Proposte per il coordinamento, non applicate in questa
campagna (i criteri non si cambiano dopo aver visto i risultati).

1. **Le baseline con uno stop legato a un prezzo di riferimento si gonfiano di costi.** Quando lo
   stop di una variante è un livello di prezzo (l'apertura del giorno, un minimo recente) e non una
   distanza, la (a) e la (b) entrano spesso con lo stop vicinissimo all'ingresso: il costo di un
   giro diviso un rischio minuscolo dà R molto negativi (FILUSDT-025: (b) −0,31 in costruzione,
   −0,39 in validazione, contro −0,04 con uno stop di distanza normale). Il candidato, che entra
   solo dove lo stop è lontano, le batte senza vantaggio di direzione. Proposta: per queste varianti
   riportare anche la (b) con lo stop alla distanza media del candidato (prova S1 di FILUSDT-025),
   oppure vietare alla (b) le barre in cui la distanza dello stop è sotto un minimo scritto prima.
2. **Il test del ritardo boccia per costruzione le regole legate all'ora del giorno.** Una regola che
   entra in una fascia oraria precisa e ci resta una barra (FILUSDT-024, 032-039) crolla col ritardo
   di una barra anche senza nessun lookahead, perché il trade cade nella fascia successiva. Sette
   candidati di questa campagna sono caduti così. Proposta: per le regole a orario, scrivere prima
   un test del lookahead che non sposti la fascia (per esempio entrare un'ora dopo su candele più
   corte), oppure dichiarare in partenza che il protocollo non le ammette, così non consumano budget.
3. **La validazione non chiede R medio positivo.** L'asticella guarda solo il p-value contro la (b):
   con la trappola del punto 1, un candidato che perde in validazione (FILUSDT-025: R −0,117) passa
   (p 0,085, m = 1). Proposta: in validazione valga la stessa frase della Fase 2, «battere il caso
   perdendo meno di lui non è un vantaggio» (R medio dopo i costi positivo).
4. **L'ordine dei ritocchi può spendere tutto il resto del budget su una sola idea.** Qui 8 ritocchi
   su 8 sono andati alla stessa idea (momento dentro il giorno, long e short) perché la variante
   base resta in testa alla lista anche quando i suoi ritocchi diventano candidati e cadono. Non è
   un errore, ma va saputo quando si legge «budget usato per intero».
5. **Trappole pratiche del guardiano** (oltre a quelle di `lezioni/metodo.md`): non si legge il file
   di uscita di un comando in background in `/tmp` (gli script devono scrivere i loro esiti in
   `data/insample/<SIMBOLO>/`); un `cd` nella cartella della campagna seguito da percorsi relativi
   viene rifiutato (si usano percorsi assoluti); niente cicli `for` con variabili della shell.
6. **Il messaggio di commit in un file si dimentica di aggiornare.** Due commit di questa campagna
   hanno il titolo del commit precedente. Conviene scrivere il file del messaggio subito prima di
   ogni commit, nello stesso passo.
7. **I dati di FILUSDT hanno giorni interi mancanti sia nel last sia nel mark, in giorni diversi**
   (last: 2022-02-26/28, 2022-04-01/02; mark: 2022-10-02, 2023-02-24): l'allineamento li toglie
   tutti; le regole che misurano «da N barre fa» attraversano i buchi senza accorgersene (dichiarato
   per I-03, I-08, I-15).
