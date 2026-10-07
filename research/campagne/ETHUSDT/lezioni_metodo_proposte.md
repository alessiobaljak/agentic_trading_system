# Lezioni di metodo proposte dalla campagna ETHUSDT

Solo errori di metodo e trappole dei dati: niente idee, meccanismi o risultati. Da unire a
`lezioni/metodo.md` al Passo 7. Si aggiorna lungo la campagna; ogni voce dice quando è nata.

## Nate nella Fase 0 e nella Fase 1 (7 ottobre 2026)

1. **Il guardiano legge la shell, non le intenzioni.** Nove rifiuti in una sessione, nessuno
   su una lettura davvero vietata: la parola `.venv` in un comando, `python3 -c`, un heredoc
   con virgolette triple, un trailer di commit su più righe nell'opzione `-m`, `$?`, `2>&1`
   dopo `git push`, la cartella madre `data/insample/` (sono ammesse solo le due sottocartelle),
   la parola «bot» dentro un testo in un heredoc, e la lettura di `src/guardiano.py` stesso.
   Regola pratica per le prossime campagne: file e testi si scrivono con lo strumento di
   scrittura file, mai con heredoc; il messaggio di commit sta in un file dentro
   `data/insample/<SIMBOLO>/` (ammessa e fuori da git) e si passa con `-F`; i comandi di shell
   restano semplici, senza redirezioni né variabili. Da aggiungere al protocollo o alla nota
   di apertura della sessione, così non si perde mezz'ora a campagna.

2. **La regola di stima dei trade va scritta per tipo di uscita, prima dei conteggi.** Una
   sola regola «distanza fra segnali almeno H» va bene per le uscite a tempo fisso ma
   sottostima di 2-3 volte le idee che escono su segnale (cambio di segno, rientro di una
   soglia). In questa campagna la seconda regola è nata dopo aver visto i conteggi dei
   segnali (voce di correzione nel log): meglio che il protocollo la preveda dall'inizio,
   così nessuna campagna deve correggersi.

3. **Le idee a un ingresso a settimana non possono arrivare a 100 trade per direzione** in tre
   anni di costruzione (143 settimane). Il protocollo conta le varianti per direzione e chiede
   i risultati separati: per queste idee la stima è sotto il minimo per costruzione, non per
   dati. Se il coordinamento vuole provarle, serve una regola scritta prima (per esempio:
   una variante «entrambe le direzioni» giudicata sull'insieme, con i risultati per direzione
   dichiarati) oppure contare i trade di più monete insieme, come già prevede la sezione 11.

4. **Il mark price ha buchi che il last non ha.** Su ETHUSDT due giorni interi (2 ottobre
   2022 e 24 febbraio 2023) mancano nelle candele mark a 15 minuti mentre le candele last ci
   sono tutte. Il motore vuole serie allineate: in quelle barre si è usata la candela last
   anche per la liquidazione, e lo si è dichiarato. Da controllare in ogni campagna e da
   scrivere nel caricatore come scelta esplicita, non lasciata al codice della campagna.

5. **La fascia di slippage calcolata sul 2023 è ottimista per l'inizio della storia.** Nel 2020
   il volume medio di ETHUSDT era 723 milioni al giorno con minimi di 45 milioni: fascia da
   0,02-0,05 % per lato, non 0,01 %. Il test a costi doppi copre in parte; una fascia per anno
   sarebbe più onesta per le monete con il 2020 in costruzione.

6. **Il campo del volume delle candele è in moneta base.** `Candela.volume` è in ETH, non in
   USDT: per il volume in USDT serve la colonna `quote_volume` dei CSV (letta direttamente
   dagli zip) oppure l'approssimazione volume × chiusura. Da esporre nel caricatore.
