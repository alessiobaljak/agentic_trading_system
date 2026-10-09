# DYDXUSDT — lezioni di metodo proposte (solo metodo e trappole dei dati)

1. **Le uscite dei comandi in background stanno in una cartella che il guardiano non fa leggere.** Uno
   script lungo deve scrivere il suo riepilogo in `data/insample/<SIMBOLO>/` (o nel log), altrimenti
   l'uscita si perde (qui: l'elenco dei file accettati senza CHECKSUM remoto non è stato letto).
2. **Il guardiano legge come percorso il testo di `sed -i 's/.../.../'` e di `git commit -m` con
   «Claude-Session: https://...»**: per modificare un file usare lo strumento di modifica, per i commit
   sempre `-F` con il messaggio in un file.
3. **Il primo mese della scheda può essere più largo dei dati veri** (qui i dati partono il 9-10 settembre
   2021, il periodo dal 1° settembre): le date non si spostano, ma la costruzione utile è più corta e va
   detto.
4. **Nella robustezza, metà dei parametri può non toccare la condizione d'ingresso** (finestre di
   stima, periodo dell'ATR, numero minimo di valori): quei casi «reggono» quasi per costruzione. Conviene
   leggere a parte i casi che cambiano la condizione.
5. **Il test dello scettico più utile è togliere la parte dell'ipotesi che porta il meccanismo** (qui la
   condizione «DYDX è rimasta indietro»): se il risultato non cambia, il motivo economico dichiarato non è
   quello che lavora. Va fatto in Fase 5 come verifica registrata, prima della validazione.
6. **Il controllo positivo ritardato può restare «netto»** (qui `t` 2,48 con il ritardo, contro 46,9
   senza): il criterio «sotto metà» basta per il lookahead, ma ricorda che un `t` poco sopra 2 su una moneta
   così volatile non è raro.
7. **La regola dell'ordine dei ritocchi porta tutti i ritocchi su 1-2 famiglie** quando i `t` sono tutti
   bassi: qui 5 ritocchi alla famiglia 013 e 5 alla 014, poi il budget è finito. Non è un errore della
   campagna, ma il coordinamento potrebbe valutare se è l'uso migliore delle ultime varianti.
