# I fatti gravi del giorno prima: la reazione dopo la notizia, letta ogni mattina (idea 158 del registro)

Regole scritte il 22 novembre 2026 dalla sessione principale, **prima della prima lettura** (23 novembre, giro delle 04:17). Il
proprietario (22 novembre): «non si tratta di predire prima [...] ma sai benissimo la reazione ci sarà dopo gli annunci, dopo gli
articoli» e poi «Scrivi la regola e procedi da domani». Nessuna spesa: la lettura la fa la sessione principale dentro l'abbonamento,
con l'archivio delle notizie che raccogliamo già (`research/notizie/`, dal 30 ottobre 2026).

**È una misura in avanti, non una prova nel conto**: non cambia G1, né il paper né il demo. Se dopo i casi scritti sotto serve, diventa
una strategia con le regole scritte prima, nel conto delle prove, con il flusso di sempre.

## Il perché
* Dopo una notizia con una direzione chiara il prezzo reagisce, ma una regola fissa non basta: sulle crypto vendere dopo ogni attacco
  informatico fa +3,94% a operazione su 28 casi (prova 146), dopo ogni annuncio di chiusura di un perpetuo +7,89% su 77 (prova 107), dopo
  ogni quotazione su Coinbase +4,03% su 104 (prova 105), con il 57-67% di operazioni vinte, il guadagno da pochi casi grossi e segnali che
  si spengono; sulle azioni la sessione «trading stock» (prova 46 del suo registro, `stock/REGISTRO.md`, 22 novembre) trova che dopo le
  dimissioni del capo di un'azienda dell'S&P 500 il calo arriva **prima** di poter entrare (−1,17% contro l'indice, t −3,02) e dopo, in
  media, niente su 243 casi: Nvidia è stata l'eccezione.
* Quindi il valore non sta nella notizia in sé, che il mercato prezza subito, ma nel **distinguere caso per caso** quelle la cui
  conseguenza continua per giorni (un attacco da 200 milioni con la squadra sparita, un'uscita per scandalo con indagini aperte) da
  quelle già finite (un attacco piccolo rimborsato, un pensionamento): è ciò che un modello che legge fa meglio di una formula.
* Sul passato fino a metà 2026 il modello sa già com'è andata ogni notizia: la prova onesta è solo in avanti, da domani.

## Le regole
1. **Quando**: ogni mattina nel giro delle 04:17, insieme alla lettura delle monete vendute da G1 (voce 14), prima di guardare
   qualunque prezzo del giorno. Il foglio lo prepara `python3 -m research.notizie.fatti_gravi`.
2. **Quali notizie**: gli articoli dell'archivio pubblicati (o visti, se manca l'ora) nelle 24 ore prima della preparazione del foglio.
   Per una moneta segnata si può fare **al più una ricerca sul web** per capire meglio il caso; conta solo ciò che ha l'ora di
   pubblicazione prima della lettura, e si scrive nel foglio.
3. **Quali monete**: quelle citate negli articoli secondo `research/notizie/REGOLE.md` (sezione 2) che hanno il perpetuo in USDT su
   Binance (l'elenco dei nomi del mese). Bitcoin ed Ether valgono anche per le notizie sul mercato intero.
4. **Il giudizio**: per ogni moneta, «fatto grave» **sì** solo se c'è un fatto suo (o del mercato, per Bitcoin ed Ether) che secondo chi
   legge continuerà a muovere il prezzo **nei giorni dopo**, non solo nei minuti: per esempio attacchi e furti, crolli o fallimenti di
   chi la emette, cause e sanzioni delle autorità, chiusura su una borsa grande, uscita della squadra o del fondatore per scandalo,
   vendita annunciata di un grande possessore, sblocco grande non atteso (verso il basso); quotazione su una borsa grande, fondo quotato
   approvato, accordo con un'azienda grande, riacquisto grande, aggiornamento importante della rete nei giorni seguenti (verso l'alto).
   Per ogni «sì»: la **direzione** (su o giù), la **forza** (1 probabile, 2 molto probabile), le **ore** fra la prima notizia e la
   lettura, una riga di perché e il collegamento. Le notizie generiche, le analisi del grafico e le previsioni di prezzo non contano.
5. **Prima dei prezzi**: il foglio (`research/notizie/fatti_gravi/AAAA-MM-GG.md`) si committa e si pusha subito; l'ora del commit è la
   prova. Una lettura committata non si cambia; una correzione si scrive sotto, con la sua ora, e conta solo da lì. Una mattina saltata
   si scrive nel diario e non si recupera. Una stessa moneta già segnata nei 7 giorni prima nella stessa direzione non si conta di nuovo.

## La misura (fissata qui, prima di ogni lettura)
6. **Il rendimento di un caso**: prezzo mark di Binance (candele a un'ora) dall'apertura della prima ora intera dopo il commit, a **1, 3 e
   7 giorni**; per le monete diverse dal Bitcoin si toglie il rendimento del Bitcoin nella stessa finestra; il segno si gira per i casi
   «giù» (positivo = la direzione scritta era giusta). Spese di andata e ritorno tolte: 0,14% (0,12% per Bitcoin, Ether e Solana); il
   funding non entra nella prima misura (si scrive come limite).
7. **Il giudizio**, dopo almeno **40 casi** (la misura principale è a 7 giorni): serve se la media netta è almeno **+1%** a caso con t
   almeno 2 (t sui casi; si scrive anche il t con i casi dello stesso giorno messi insieme) e la direzione è giusta in almeno il 55% dei
   casi. Si riportano anche: i casi di forza 2 da soli, quelli con la notizia di meno di 6 ore e di più di 12, su e giù separati.
8. Se serve, si propone una strategia (regole scritte prima, nel conto delle prove, backtest-auditor; il paper lo decide la sessione
   principale, il demo e i soldi veri il proprietario). Se dopo **80 casi** non serve, la lettura si ferma e si scrive il perché, a meno
   che il proprietario dica altro. Lo script della misura (`fatti_gravi_misura.py`) si scrive prima del giudizio e non cambia queste regole.
