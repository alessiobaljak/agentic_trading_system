# Lezioni di metodo proposte dalla campagna SOLUSDT

Solo errori di metodo e trappole dei dati: niente idee, meccanismi o risultati. Da unire in
`lezioni/metodo.md` al Passo 7.

1. **Il confronto «nettamente» con UNA simulazione casuale è più rumoroso del percentile
   sulle 200.** Lo strumento `differenza_nettamente` ricampiona due serie (candidato e una
   sola corsa casuale, la mediana) e somma i due errori: il margine viene largo e il
   giudizio può dire «non netto» a un candidato che sta sopra tutte e 200 le simulazioni.
   Nella campagna è successo tre volte. Proposta: scrivere nel protocollo quale delle due
   versioni vale (percentile della distribuzione simulata, oppure differenza dalla MEDIA
   della distribuzione con l'errore standard del solo candidato), e usare sempre quella. In
   questa campagna ho rispettato il criterio registrato, come deve essere; la lezione è che
   il criterio va scelto a Passo 0, non interpretato in campagna.
2. **La stima dei trade per le uscite «a condizione» dipende da una durata che non si
   conosce.** Per le regole con uscita al segnale opposto (momentum, canale) ho stimato la
   durata con entrate casuali con la stessa uscita (non usa i risultati del segnale): è una
   regola che vale la pena scrivere nel protocollo, perché la durata «a occhio» (20 barre)
   dava 83 trade e quella misurata (9 barre) ne dava 105: la stessa idea passava o no la
   soglia dei 100 trade secondo un numero inventato.
3. **I dati di riferimento (BTC) vanno scaricati sugli stessi timeframe della moneta,
   prima della Fase 2.** Li avevo a 1h e 1d: a 4h il controllo «è solo BTC» è uscito NaN e
   l'ho corretto con una voce di correzione. Costo zero, ma è un errore evitabile con una
   riga nella Fase 0.
4. **Le serie last e mark hanno buchi in giorni diversi** (5 giorni l'una, 7 l'altra, nel
   2021-2023) e il motore vuole le serie allineate barra per barra: serve un caricatore che
   faccia l'intersezione e dichiari le barre tolte. Andrebbe dentro `src/dati.py`, non nel
   codice della campagna.
5. **Con due anni di costruzione di segno opposto, «R per anno» è l'unico numero che conta.**
   Quasi tutte le varianti direzionali hanno R per anno del segno del buy and hold
   dell'anno: il totale non dice niente. Il protocollo lo chiede già (periodi separati);
   la lezione è che la tabella di consegna deve avere la colonna per anno al centro, non in
   fondo.
6. **Tre trade possono fare un profit factor di 1,6 su 160 trade.** Il controllo «senza i 3
   migliori» ha smontato tre varianti su quattro di quelle con R medio alto. Vale la pena
   renderlo obbligatorio in Fase 2, non solo in Fase 4 (dove non si arriva se la Fase 2 è
   giudicata sul totale).
7. **Il periodo di volume sotto soglia (il 2020) sposta il rapporto costruzione/validazione
   dal 70/30 a 67/33** se la data di divisione resta quella calcolata sul listing. Ho
   tenuto la data (scritta prima dei prezzi) e dichiarato la differenza: il protocollo
   potrebbe dire di calcolare la divisione sul periodo utile, dopo la Fase 0 ma prima di
   qualunque test.
8. **Il log in JSON con 760 impronte dentro `fase0_dati.md` funziona ma pesa**: 894 righe.
   Un file `impronte.json` committato accanto, con il suo hash dentro `fase0_dati.md`,
   sarebbe più leggibile a parità di garanzia.
