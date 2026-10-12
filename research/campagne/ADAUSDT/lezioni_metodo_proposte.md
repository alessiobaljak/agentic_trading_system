# ADAUSDT — lezioni di metodo proposte (solo metodo e trappole dei dati)

1. **Uno stop che dipende dalla struttura del prezzo (minimo di un intervallo, livello) rende le
   baseline (a) e (b) molto negative.** Le baseline entrano anche dove lo stop è vicinissimo: il costo
   fisso di un giro diventa grande in R. Una variante che entra solo dove lo stop è largo le batte
   «nettamente» senza alcun vantaggio di direzione. Qui è successo 6 volte su 6, e 5 di queste varianti
   sono poi cadute ai costi doppi. Proposta: per queste varianti si riporta sempre, accanto alla (b),
   l'R medio in percentuale del prezzo, o una (b) con la stessa distribuzione della distanza dello stop.
2. **Con uno stop variabile, l'R medio di validazione può essere fatto da pochissimi trade**: qui 3
   trade su 82 valgono quasi tutto l'R. «Nettamente» e l'asticella sono test sulla media e non lo
   vedono. Proposta: in validazione si riporta sempre anche l'R medio senza i 3 migliori, come in
   costruzione (qui c'è, nella consegna).
3. **La prova dello scettico per i filtri nati dallo studio dei fallimenti.** Si rifà la (b) entrando a
   caso solo dove valgono i filtri. Costa una baseline e dice se il vantaggio è il meccanismo o lo stato
   del mercato scelto dai filtri. Qui ha detto «lo stato del mercato» (t 0,63), mentre tutte le verifiche
   della Fase 4 erano superate.
4. **L'ordine dei ritocchi tiene in testa la stessa famiglia fino a 5 ritocchi.** Una variante con t
   alto e R non positivo (qui 024) resta prima anche dopo che i suoi ritocchi sono diventati candidati
   e sono stati scartati. Il budget dei ritocchi si concentra su una famiglia sola; non è un errore, ma
   va saputo.
5. **Il ritardo di una barra su una regola legata all'ora** (entrata alle 23:30 per l'ultima mezz'ora)
   sposta l'ingresso fuori dal meccanismo e dà un «crollo» senza alcun lookahead. Va distinto da un
   errore, guardando il codice.
6. **Il guardiano e le uscite dei comandi in background:** il file di uscita dei comandi lanciati in
   background sta in una cartella temporanea fuori da `research/` e il guardiano ne rifiuta la lettura.
   Gli script devono scrivere le loro uscite in `data/insample/<SIMBOLO>/` o nel log. Anche un grep con
   un'espressione regolare complessa può essere letto come un percorso e rifiutato: meglio un piccolo
   script di riassunto.
7. **Il primo mese di dati della scheda può contenere un solo giorno** (qui 2020-01: last solo dal 31
   gennaio, mark e funding dal 19). Le date di costruzione non si spostano, ma la costruzione utile è più
   corta di quella calcolata.
