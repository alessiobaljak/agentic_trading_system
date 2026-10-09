# LTCUSDT — Lezioni di metodo proposte (solo errori di metodo e trappole dei dati)

1. **Con lo stop ancorato a un livello del prezzo la baseline (b) è più bassa per costruzione.** Quando
   lo stop sta su un livello (massimo o minimo di un range, una media), un ingresso a caso ha spesso
   lo stop vicinissimo: costi in R alti e stop presi dal rumore. La variante entra proprio quando il
   prezzo ha appena superato il livello, con una distanza «naturale». Risultato: t contro la (b) fra
   1,1 e 2,0 senza alcuna direzione (LTCUSDT 013, 014, 016c, 017c, 026, 028, 029, 030). La prova che
   lo smaschera costa una variante: la stessa regola con lo stop fisso (LTCUSDT-027: t da 1,95 a 0,01).
   Chi disegna varianti con lo stop su un livello dovrebbe saperlo prima, e chi ordina i ritocchi per
   `t` le troverà in cima alla lista anche quando non hanno niente.
2. **L'ordine dei ritocchi per `t` è meccanico e può spendere tutti i ritocchi su una famiglia che un
   suo ritocco ha già smontato** (qui: 5 ritocchi della 014 anche dopo la 027). Non è un errore della
   campagna, è un punto da valutare per la regola 6.
3. **La (a) a ogni barra su timeframe orario con lo stop su un livello vale −0,4/−0,8 R** (costi su
   stop vicinissimi): «netta contro la (a)» lì non dice nulla.
4. **Comandi**: il messaggio di commit passato con `-m` che contiene un indirizzo web viene rifiutato
   (letto come percorso); l'uscita dei comandi in background sta in una cartella che il guardiano non
   lascia leggere: gli script lunghi devono scrivere la loro uscita dentro `data/insample/<SIMBOLO>/`.
5. **Il primo giorno di dati può non coincidere con il primo giorno del mese della scheda** (LTCUSDT:
   2020-01-09): la costruzione utile è più corta di quella calcolata, da dichiarare in Fase 0.
