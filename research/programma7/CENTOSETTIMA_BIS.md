# Prova 169 — «G1 o F5 secondo il mercato»: decidere ogni giorno solo quando il mercato ha una direzione

Regole scritte il 25 novembre 2026 da strategy-improver, **prima di ogni calcolo** (nessun numero di questa variante guardato). Le committa
la sessione principale; la esegue strategy-researcher (prima in modalità verifica); il giudizio lo dà backtest-auditor se promettente.
**Non spegne e non sostituisce niente**: G1, G1 neutra, G11 e F5 restano accese, la variante entra accanto.
**Il numero**: 169, assegnato dalla sessione principale il 25 novembre (l'idea sulle opzioni di Deribit in `CENTOSETTIMA.md` non è
stata eseguita e non ha numero).

## Il perché (idea del proprietario, 24 novembre, `docs/andremo_live.md` delle 18:00)
* Nel paper, dal 16 al 24 novembre: F5 (decide il lunedì) +1,4%, G1 (decide ogni giorno) −4,4%, con il mercato che crollava e rimbalzava.
* Sul passato le due si equivalgono con anni opposti (prova 168, `RISULTATI_CENTOSESTA.md`): 2023, senza direzione, F5 +30,7% contro G1
  +7,7%; 2025, di tendenza, G1 +72,5% contro F5 +50,6%.
* L'ipotesi: senza direzione la classifica del funding cambia ogni giorno, e decidere ogni giorno insegue il rumore e paga più spese; con una
  tendenza, decidere ogni giorno prende prima i cambi veri. Quindi: pesi di G1 quando il mercato ha una direzione, pesi di F5 quando no.

## La misura della direzione (una sola, fissata ora)
**Rapporto di efficienza del Bitcoin sui 30 giorni** (Kaufman): `ER = |C[t-1] − C[t-31]| / Σ_{k=t-30..t-1} |C[k] − C[k-1]|`, con C la chiusura
giornaliera di BTCUSDT del pannello (`sc.pannello()`), **solo con giorni chiusi fino al giorno prima** della decisione (stessa
convenzione degli indici di `se.funding_7(pan, idx)` per G1: la riga `idx` usa i dati fino a ieri; il controllo va scritto nella verifica).
* Vale 1 se il prezzo è andato dritto in una direzione, vicino a 0 se ha solo ballato. Non dipende dal livello della volatilità e non ha
  unità: una soglia sola ha senso in ogni anno.
* **Perché questa e non le altre**: (1) la tendenza è proprio ciò che l'idea chiede (G1 vince con tendenza, F5 senza); (2) il Bitcoin è
  il mercato che guida le altre monete e ha la serie più pulita, senza buchi (verifica da confermare); (3) la misura sul funding («quanto
  è cambiata la classifica») è più vicina al meccanismo, ma è fatta con lo stesso dato che decide le posizioni e rischia di ripetere
  G1 stessa: resta come idea scritta, non provata; (4) 30 giorni = la finestra della volatilità già usata da G1 e F5 (`ot.sigma_30`), nessun
  numero nuovo da scegliere.
* Stato del giorno: **direzione** se ER ≥ soglia, **nessuna direzione** altrimenti. Nessuna isteresi, nessun filtro di durata (fissato così
  per non aggiungere numeri da ritoccare): i cambi di stato quindi possono essere frequenti, e le loro spese si pagano per intero.
  Se ER non è calcolabile (meno di 31 chiusure) il giorno è «nessuna direzione» (cioè F5).

## Le varianti (fissate ora, solo 2: cambia solo la soglia)
* **A, soglia 0,20** (direzione se ER ≥ 0,20).
* **B, soglia 0,30** (direzione se ER ≥ 0,30).
Le soglie sono scelte senza guardare la distribuzione di ER sul passato; ognuna è una variante registrata, anche se fallisce. Nessun'altra
soglia si prova dopo aver visto i risultati (se ne vuole un'altra è una prova nuova con regole nuove). Nel rapporto si scrive, solo come
descrizione, la quota di giorni «con direzione» per ogni anno e per ogni soglia.

## Come si costruisce il portafoglio (motori già usati dalla prova 168, senza toccarli)
* **Pesi giornalieri**, come in `research/programma7/centosesta.py` (`esegui`, stessi passi della verifica `VERIFICA_CENTOSESTA.md`):
  `W1 = vq.pesi_banda(np.where(np.isfinite(sig), -se.funding_7(pan, idx), np.nan), Ud, sig)` per G1; per F5
  `Wt = vq.pesi_banda(... sigma_30 e funding_7 sulle righe del lunedì ..., ps["U"], sg)` calcolato **dalle settimane del 2020** (la banda ha
  memoria), tagliato da `se.INIZIO`, poi `W5 = pr.universo_del_giorno(giorni, ps["lunedi"], Wt)` (pesi costanti dal lunedì alla domenica,
  con il piccolo riequilibrio giornaliero pagato: lettura prudente già scelta in 168).
* **Peso del giorno** = `W1[g]` se direzione, `W5[g]` altrimenti. Nessuna miscela: un solo insieme di pesi per giorno.
* **Spese e funding** con `conto_giorni` di `centosesta.py` (`te.conto` + `cs.spese_a_limite`): le spese confermate dal proprietario il 7
  novembre (0,05% a mercato, 0,02% a limite, scarto 0,01% su BTC, ETH e SOL e 0,02% sulle altre), applicate alle variazioni del peso
  fra un giorno e l'altro, **compreso il passaggio da G1 a F5 e viceversa** (è la regola «al cambio di stato le spese vere»). Funding sul
  peso del giorno. Nessun vault per data.
* **Periodo**: lunedì 4 gennaio 2021 – settimana che finisce il 4 ottobre 2026 (300 settimane, come la prova 168), per confrontare con
  `risultati_prima/settimane_G1` e `risultati_controllo_parita/settimane_F5` (F5 a spese di mercato, la scelta di 168). Prima del calcolo si
  scrive se i giorni mancanti dell'archivio cadono nel periodo (come `buchi_nel_periodo`), in particolare su BTC.
* **Controllo dei motori**: si rifanno G1 e F5 coi pesi sopra e si confrontano con le serie salvate (scarto massimo del netto settimanale,
  come in 168); se lo scarto non è piccolo come in 168, la prova non si calcola e si scrive perché.

## L'esame (regole approvate dal proprietario il 9 e l'11 novembre)
* Per ogni variante: netto positivo, **ogni anno positivo**, **t almeno 3**, **Sharpe corretto almeno 0,80** con il conto per famiglie
  (`asticella.corretto_famiglie`, A e B in `nuove`; il mazzo come sta, ricordando in nota come in 168 la F5 vecchia). Esito calcolato con
  `esito_regole` di `centosesta.py`, non con la soglia 0,95 di `te.esito`.
* **Il confronto sulle stesse 300 settimane con G1 e con F5** (è la domanda vera): Sharpe, rendimento l'anno, per anno (2021–2026), discesa
  massima, giorno e settimana peggiori, numero di ordini e spese l'anno, numero di cambi di stato l'anno e spese dovute ai cambi.
  Controllo descrittivo: lo stesso nei soli anni «senza direzione» e «con direzione» secondo la misura (non è una condizione).
  Nessuna soglia nuova per dire «meglio di G1» o «meglio di F5»; i numeri vanno al proprietario.
* **Cosa è un fallimento utile**: se i cambi di stato mangiano il guadagno (spese dei cambi più della metà della differenza con G1) o se una
  sola delle due soglie regge, si scrive e basta.
* Se una variante è promettente va a backtest-auditor; solo dopo il suo PASS può entrare nel paper, accanto alle originali (lo decide la
  sessione principale). Demo e soldi veri solo con l'ok del proprietario.

## In avanti (descrittivo)
Dalle risposte «stato» di `ops/results/`: lo stato di ER di ogni giorno dal 16 novembre e quale delle due strategie la variante avrebbe
seguito, contro G1 e F5 reali nello stesso periodo. Non entra nel conto: 9 giorni sono pochi per giudicare.

## Chiusura della verifica (25 novembre 2026, sessione principale, prima di ogni calcolo)
Dalla verifica di strategy-researcher (`VERIFICA_CENTOSETTIMA_BIS.md`, 3 punti bloccanti). **Dove il testo sopra dice diversamente, vale
questa sezione.** Dove c'era una scelta, si è presa la più prudente.
1. **Buchi del Bitcoin** (bloccante): il controllo parte da 31 chiusure prima del 4 gennaio 2021 (4 dicembre 2020); un giorno senza la
   chiusura del Bitcoin nella finestra conta come «senza direzione» (pesi di F5); più di 5 chiusure mancanti in tutto il periodo: la prova
   si ferma e si scrive.
2. **I motori** (bloccante): G1 e F5 rifatte con i pesi devono stare entro **0,01** (G1) e **0,005** (F5) di netto settimanale dalle serie
   salvate, in ogni settimana; oltre, ci si ferma e si scrive.
3. **Rapporto di efficienza non calcolabile** (bloccante): calcolabile solo con tutte e 31 le chiusure finite e il denominatore sopra zero;
   altrimenti «senza direzione» (F5). Il confronto con la soglia è «maggiore o uguale», senza arrotondamenti.
4. I pesi giornalieri di G1 e quelli di F5 si calcolano interi, ogni giorno, e si sceglie riga per riga secondo lo stato del giorno (G1
   «virtuale» nei giorni di F5); al cambio di stato si paga il passaggio dai pesi tenuti ai pesi nuovi.
5. Controllo descrittivo in più: la stessa costruzione con la sola F5 (tutti i giorni «senza direzione») contro la serie settimanale di F5.
6. «Spese dei cambi» = spese dei soli giorni in cui lo stato cambia; «la differenza con G1» = sul netto annuo.
7. Un anno è «con direzione» se almeno metà dei suoi giorni lo sono; si scrive anche il netto della variante nei giorni di ciascuno stato.
8. Esame con le regole della prova (Sharpe corretto 0,80 per famiglie, ogni anno positivo, t da 3), nomi «169 A» e «169 B» in
   `corretto_famiglie`; si annota che il mazzo ha ancora la F5 vecchia (backlog P35).
9. Parte in avanti: solo fin dove arriva il pannello dei prezzi, senza scarichi nuovi; descrittiva.

## Cosa si consegna
`research/programma7/RISULTATI_CENTOSETTIMA_BIS.md`, serie in `research/programma7/risultati_centosettima_bis/settimane_A.csv.gz` e
`settimane_B.csv.gz` (colonna `netto`, leggibili da `asticella.py`), script `research/programma7/centosettima_bis.py` (nuovo, che importa
i motori senza toccarli), varianti in `research/trials/centosettima_bis.csv` (anche quelle fallite); a schermo al massimo 20 righe.
Nessun servizio a pagamento. La riga nel registro la scrive la sessione principale.
