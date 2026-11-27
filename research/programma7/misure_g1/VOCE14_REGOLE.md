# Voce 14 di G1 — le notizie delle monete vendute, lette ogni mattina prima dei prezzi

Regole scritte il 21 novembre 2026 alle 20:40 UTC dalla sessione principale, **prima della prima lettura** (domani, 22 novembre, giro
delle 04:17). Il proprietario (21 novembre) ha approvato la prova gratuita proposta: «leggo io le notizie delle monete vendute da G1 ogni
mattina, prima dei prezzi» («Si quella che leggi va bene»). Nessuna spesa: la lettura la fa la sessione principale dentro l'abbonamento,
con l'archivio delle notizie che raccogliamo già (`research/notizie/`) e la ricerca sul web dello strumento della sessione.

**È una misura, non una prova nel conto**: non cambia G1, né il paper né il demo, e non tocca il bot. Se la misura dice che la lettura
serve, una regola nuova (per esempio togliere dal lato venduto le monete segnate) sarà una prova a parte, con le regole scritte prima, e
passerà dal proprietario.

## Il perché
Il punto debole di G1 nel 2026 sono le fiammate delle monete piccole vendute (voce 12: ICNTUSDT +21% e +28% il 19-20 novembre, circa
1,2 punti del conto in due giorni; `misure_g1/voce12_ribasso_18_19nov.py`). Una fiammata ha spesso una causa che si legge prima: una
quotazione su una borsa grande, un riacquisto di monete, un accordo, un premio a chi la tiene. Un modello linguistico legge e giudica
queste notizie meglio di una regola a parole chiave, e per i giorni dopo la data del suo addestramento non può conoscere i prezzi: è una
prova onesta solo in avanti.

## Le regole
1. **Quando**: ogni mattina nel giro delle 04:17, appena arriva la risposta «stato» della macchina (circa alle 04:40 UTC).
2. **Quali monete**: tutte quelle con peso negativo del paper G1 nella tabella dei pesi della risposta «stato» (`/paper_g1/posizioni`,
   l'ultimo ribilancio delle 00:05).
3. **Le notizie**: (a) gli articoli dell'archivio pubblicati (o visti, se manca l'ora) nelle 24 ore prima della lettura, che citano la
   moneta secondo `research/notizie/REGOLE.md` (sezione 2); per le monete fuori dall'elenco dei nomi conta solo la sigla, con le stesse
   regole (`voce14_lettura.py`, funzione `cita`); (b) **al più una ricerca sul web per moneta**, solo per le monete con peso di almeno il
   2% del conto, con il nome della moneta e la parola «news»; conta solo ciò che ha l'ora di pubblicazione prima della lettura. Si
   scrive nel foglio quali ricerche si sono fatte.
4. **Il giudizio**, uno per moneta: «sì» (a rischio di salire) se nelle notizie c'è un fatto **proprio di quella moneta** del tipo che di
   solito la fa salire: quotazione nuova su una borsa grande (Binance a pronti, Coinbase, Upbit, Bithumb, Robinhood, OKX, Bybit),
   riacquisto o distruzione di monete, accordo o integrazione con un'azienda o una rete grande, premio o distribuzione gratuita a chi la
   tiene, aggiornamento della rete nei giorni seguenti, un grande compratore annunciato, un prodotto quotato (fondo, ETF) approvato o
   chiesto; altrimenti «no». Non contano le notizie sul mercato in generale, le analisi del grafico e le notizie negative. Un «sì» va con
   una riga di perché e il collegamento.
5. **Prima dei prezzi**: nel foglio si scrive il giudizio prima di guardare qualunque prezzo del giorno, e il foglio
   (`misure_g1/voce14_letture/AAAA-MM-GG.md`, preparato da `voce14_lettura.py`) si committa e si pusha subito: l'ora del commit è la
   prova. Una lettura committata non si cambia; una correzione si scrive sotto, con la sua ora, e conta solo dall'ora della correzione.
   Una mattina saltata si scrive nel diario e non si recupera.

## La misura (fissata qui, prima di ogni lettura)
6. **Rendimento di una moneta in una mattina**: prezzo mark di Binance (candele a un'ora, `markPriceKlines`) dall'apertura della prima
   ora intera dopo il commit della lettura all'apertura delle 00:00 UTC del giorno dopo (la decisione seguente di G1). Secondo
   orizzonte, solo descrittivo: 24 ore dalla stessa ora.
7. **Il confronto**: per ogni mattina con almeno un «sì», la media del rendimento delle monete «sì» meno la media delle altre monete
   vendute della stessa mattina (così il movimento del mercato si toglie). Si riportano anche: il numero di «sì», quante «sì» sono salite
   più del 10%, quante fiammate sopra il 10% fra le «no» (le fiammate mancate), e il costo per G1 delle monete «sì» (somma di peso ×
   rendimento, in punti del conto).
8. **Quando si giudica**: dopo almeno **20 mattine lette e 20 monete «sì»** (si contano le coppie moneta-mattina). Serve se la media delle
   differenze del punto 7 è almeno **+1 punto** con t almeno 2 (t sulle differenze delle mattine). Se serve, si propone al proprietario
   una regola per G1 da provare in avanti accanto all'originale; se non serve, si scrive il perché e la lettura si ferma, a meno che il
   proprietario dica altro. Il risultato va nel diario di G1 e nel riepilogo del lunedì.
9. Lo script della misura (`voce14_misura.py`) si scrive prima del giudizio e non cambia le regole qui sopra.

## Nota del 27 novembre 2026 (audit del 26 novembre)
L'abbinamento segue `research/notizie/REGOLE.md`, sezione 2, che da oggi conta ARK, HIVE, GENIUS, SATS e APR solo con il «$» (davano abbinamenti falsi: ARK Invest, la società di mining HIVE, la legge GENIUS, le azioni
SATS di Strive, «APR» il tasso annuo). Per APRUSDT, venduta da G1, il foglio non mostra più gli articoli sul tasso annuo. Le ore
dell'archivio si leggono sempre in UTC (`raccolta.ora_utc`).
