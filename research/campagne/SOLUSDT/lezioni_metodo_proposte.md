# SOLUSDT — Lezioni di metodo proposte (solo metodo e trappole dei dati)

1. **Una cache delle serie va legata alla versione del caricatore.** La correzione del funding del 2026-10-08
   (istante al secondo) non arrivava ai test perché la cache locale si ricostruiva solo se mancava: nella cache
   2.083 settlement su 3.688 avevano ancora i millisecondi. Soluzione: la cache porta l'impronta di
   `src/dati.py` e si rifà quando cambia. Senza, un risultato (015 contro la (b)) cambiava esito: da netto a
   non netto.
2. **Il test del ritardo e le regole legate a un'ora.** Per una regola che vale a un'ora precisa (ultima
   mezz'ora del giorno) una barra di ritardo sposta l'ingresso in un'altra ora e il t crolla per il meccanismo,
   non per un lookahead. Il protocollo chiede di cercare l'errore: una **prova per troncamento** (regole
   ricalcolate sulla serie tagliata alla barra di segnale, confronto con la serie intera) separa i due casi in
   pochi minuti. Proposta: renderla la prova standard quando il ritardo crolla.
3. **Regola 6: «batte nettamente (a) e (b) ma R non positivo».** Il testo escludeva dall'ordine dei ritocchi le
   varianti nette su entrambe chiamandole candidati; il caso con R ≤ 0 non era previsto. Decisione del
   proprietario dell'8 ottobre: entrano nell'ordine. Proposta: scriverlo nel protocollo.
4. **L'ordine dei ritocchi concentra il budget su una famiglia.** Quando un ritocco diventa candidato esce
   dalla lista e la variante madre resta in cima: i ritocchi tornano sulla stessa famiglia fino al massimo di 5.
   Qui 5 degli 8 ritocchi sono andati alla famiglia di 015 e hanno prodotto 4 candidati, di cui ne sarebbe
   andato in validazione uno solo.
5. **Un filtro che toglie un terzo dei trade porta facilmente sotto 70.** Con 85–101 trade ogni filtro sui
   terzili diventa uno scarto, che non consuma budget ma consuma un ritocco della famiglia.
6. **A 30 minuti i costi decidono tutto.** Con stop di 2–3 ATR i costi di un giro valgono circa 0,05 R: un
   vantaggio lordo sotto 0,05 R non sopravvive ai costi doppi. Conviene calcolarlo prima di scegliere il
   timeframe.
7. **Il guardiano in pratica.** Rifiuta: lo strumento Workflow e i sotto-agenti; `git push ... | tail`; `sed -i`
   con virgolette nel testo (letto come percorso); un ciclo della shell con variabili; `git diff HEAD --stat`
   senza percorso. Tutti aggirabili senza rischi con lo strumento di scrittura dei file e script che accettano
   più argomenti.
8. **Drawdown in validazione.** Va calcolato dai rendimenti dei trade (pnl in percentuale del capitale
   all'ingresso), non da 1000 più la somma dei pnl: il capitale all'inizio della validazione non è 1000.
