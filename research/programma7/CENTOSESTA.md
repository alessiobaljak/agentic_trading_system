# Prova 168 — G1, G11, G1 neutra e F5 insieme sullo stesso conto (idea del proprietario del 22 novembre)

Regole scritte il 22 novembre 2026 dalla sessione principale, **prima di ogni calcolo**. Il proprietario (22 novembre): «provale tutte
e 4 insieme così da capire cosa succede anche sul passato». La esegue strategy-researcher (prima in modalità verifica), il giudizio lo
dà backtest-auditor se promettente. Non spegne e non sostituisce niente.

## Il perché
* Le quattro strategie girano già nel paper, ognuna con 10.000 USDT suoi; su un conto solo Binance tiene **una posizione per moneta**,
  quindi insieme si eseguirebbe la somma dei loro pesi (una miscela), con meno ordini dove le differenze si compensano.
* Sono varianti della stessa idea (il funding fra le monete): G1 decide ogni giorno (prova 57), G11 con il funding più fresco (prova 69),
  G1 neutra con i due lati bilanciati contro il mercato (prova 88), F5 solo il lunedì (prova 24). La correlazione settimanale fra G1 e
  G1 neutra è 0,91 (`allocazione/reports/2026-11-16.md`). La domanda: insieme fanno meglio di G1 da sola (meno discesa, rendimento
  più regolare) o solo la stessa cosa?

## Dati
* Le serie settimanali nette già nel mazzo (`research/programma6/asticella.py`): `programma6/risultati_ventiquattresima/settimane_F5`,
  `programma7/risultati_prima/settimane_G1`, `risultati_tredicesima/settimane_G11`, `risultati_ventiseiesima/settimane_G1N`. Per la
  variante B i pesi giornalieri delle quattro strategie dagli script delle loro prove, senza cambiare i motori.
* **Periodo**: le settimane comuni alle quattro serie (dalla prima settimana in cui tutte e quattro hanno una posizione al 4 ottobre
  2026, `periodo()`).

## Le varianti (fissate, solo 2)
* **A, quattro conti in uno** (nessuna compensazione, la lettura più prudente): ogni strategia un quarto del capitale con le sue spese;
  rendimento della settimana = media dei quattro rendimenti netti della stessa settimana.
* **B, un portafoglio solo**: ogni giorno il peso di ogni moneta = media dei pesi delle quattro strategie (F5 tiene i suoi pesi dal
  lunedì alla domenica); spese (confermate dal proprietario: 0,02% con ordine limite come nel motore di G1, 0,05% a mercato, scarto
  0,01% su BTC, ETH e SOL e 0,02% sulle altre) solo sulle variazioni del peso netto; funding sul peso netto. Se i pesi giornalieri di una
  delle quattro non si ottengono senza toccare i motori, B non si fa e si scrive perché.

## L'esame (regole approvate dal proprietario il 9 e l'11 novembre)
* Come sempre: netto positivo, ogni anno positivo, t almeno 3, Sharpe corretto almeno 0,80 con il conto per famiglie
  (`asticella.corretto_famiglie`, A e B in `nuove`).
* **Il confronto con G1 da sola sulle stesse settimane** (è la domanda vera): Sharpe, rendimento l'anno, discesa massima, giorno e
  settimana peggiori, numero di ordini e spese l'anno. Si scrive anche la correlazione fra le quattro. Nessuna soglia nuova per dire
  «meglio di G1»: le regole della sostituzione dell'allocatore non sono approvate; i numeri vanno al proprietario.

## In avanti, a tavolino (descrittivo, non nel conto)
* Dalle risposte «stato» della macchina in `ops/results/` (una ogni mattina): l'equity di ognuna delle quattro dal primo giorno in cui
  girano tutte e quattro; il conto «un quarto a testa» = media dei quattro rendimenti giornalieri, contro G1 da sola. Lo scrive il
  rapporto e si aggiorna nel confronto del lunedì.

## Chiusura della verifica (22 novembre 2026, sessione principale, prima di ogni calcolo)
Dalla verifica di strategy-researcher (`VERIFICA_CENTOSESTA.md`, 1 punto bloccante). **Dove il testo sopra dice diversamente, vale questa
sezione.** Dove c'era una scelta, si è presa la più prudente.
1. **F5 corretta** (punto bloccante): la serie di F5 è `programma6/risultati_controllo_parita/settimane_F5.csv.gz` (dopo la correzione del
   funding del 23 ottobre, come le altre tre), **a spese di mercato** (più alte di quelle a limite: prudente); la F5 con ordini limite
   (F9) si scrive solo come controllo descrittivo, non è una variante.
2. **Periodo**: dal lunedì 4 gennaio 2021 alla settimana che finisce il 4 ottobre 2026 (300 settimane comuni); F5 per B si calcola dalle
   settimane del 2020 (la banda ha memoria) e si taglia dal 4 gennaio 2021.
3. **F5 dentro B**: pesi costanti ogni giorno dal lunedì alla domenica, con il piccolo riequilibrio giornaliero pagato (lettura
   prudente); controllo descrittivo: B fatta con la sola F5 contro la sua serie settimanale.
4. **Spese di B**: quelle del motore di G1 (`spese_a_limite`) applicate alle variazioni del peso netto, non uno 0,02% fisso.
5. **Le colonne di A**: la media di ogni colonna delle quattro serie (`monete` sommato), perché l'esame le legge tutte.
6. **Giorno peggiore**: solo per G1 e per B; per A la settimana peggiore.
7. **Esito** calcolato con le regole di questa prova (Sharpe corretto 0,80, ogni anno positivo, t da 3), non con la soglia 0,95 di
   `te.esito`.
8. **In avanti**: dal 31 ottobre 2026 (prima risposta «stato» con tutte e quattro), per ogni giorno la risposta più vicina alle 04:15 UTC,
   rendimenti sugli intervalli veri del calendario (il 2-5 novembre come un solo intervallo); niente righe di log.
9. **Buchi dei dati**: prima del calcolo si scrive se i giorni mancanti dell'archivio cadono nel periodo e su quali monete.

## Cosa si consegna
`research/programma7/RISULTATI_CENTOSESTA.md`, serie in `research/programma7/risultati_centosesta/settimane_A.csv.gz` (e
`settimane_B.csv.gz` se B si fa), colonna `netto`, leggibili da `asticella.py`; script `research/programma7/centosesta.py`; varianti in
`research/trials/centosesta.csv`; a schermo al massimo 20 righe. Nessun servizio a pagamento.
