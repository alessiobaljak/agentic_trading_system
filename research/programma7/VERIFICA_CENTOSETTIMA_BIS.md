# Verifica della prova 169 (regole in `CENTOSETTIMA_BIS.md`), 25 novembre 2026

Modalità verifica: nessun risultato calcolato e nessun rendimento guardato. Regole committate: `d59c79d` (25 novembre 2026, 08:21 UTC).
Letti: le regole, `VERIFICA_CENTOSESTA.md`, `centosesta.py`, `sesta.funding_7`, `ottava.sigma_30`, `prima.universo_del_giorno`, e di
`risultati_centosesta/esame.json` solo l'elenco dei buchi nei dati e lo scarto dei motori (nessun rendimento). `research/data/` non aperto
(solo `test -f` sul pannello: esiste). Non ho caricato il pannello: i buchi del Bitcoin sono quelli già scritti dalla prova 168.

## Esito: eseguibile solo dopo aver chiuso 3 punti bloccanti e 8 ambiguità. Nessun motore da toccare.

## Cosa risulta (chiaro)
* **Allineamento della direzione.** `funding_7(pan, idx)` = somma del funding dei giorni `idx-7 … idx-1` (differenza di somme cumulate): usa
  solo giorni chiusi fino a ieri. `sigma_30` fa lo stesso (rendimenti `m-30 … m-1`). La formula scritta per ER
  (`|C[t-1]-C[t-31]| / Σ_{k=t-30..t-1}|C[k]-C[k-1]|`, 30 termini) ha lo stesso allineamento, a patto che `t` sia la riga `idx` del giorno
  (`idx = giorni - pan["t0"]`) e `C = pan["close"][:, BTCUSDT]`. La chiusura del giorno `idx-1` è l'ultima prima dell'apertura del giorno
  `idx`, quindi niente sguardo avanti. Il controllo scritto: confrontare con `funding_7` che la riga `idx` non cambia se si azzerano i dati
  dal giorno `idx` in poi (test su dati alterati, non sui risultati).
* **Fonte dei prezzi del Bitcoin:** `pan["close"]` del pannello ufficiale (`sc.pannello()`), la stessa colonna usata da `sigma_30`.
* **Buchi del Bitcoin nel periodo:** la prova 168 (`risultati_centosesta/esame.json`, chiave `buchi`) non elenca BTCUSDT fra le monete con buchi
  e non ha giorni senza nessuna candela, per 2021-01-04 – 2026-10-04. Il controllo di 168 però **non guarda prima del 4 gennaio 2021**, e ER
  ha bisogno di 31 chiusure precedenti (dal 4 dicembre 2020). Vedi punto 1.
* **Pesi di G1 e F5:** i passi sono quelli di `centosesta.py` `esegui` (G1: `W1`; F5: `Wt` dalle sole righe del lunedì sul 2020, poi `W5 =
  pr.universo_del_giorno(giorni, ps["lunedi"], Wt)`); nessuna modifica ai motori. La F5 è già quella corretta (parità del 23 ottobre,
  `se.funding_7` arrotondata) perché i pesi si ricalcolano con il codice di oggi.
* **Spese:** `conto_giorni` di `centosesta.py` (`te.conto` + `cs.spese_a_limite`) è riusabile così com'è sul peso del giorno.
* Nei file non c'è ancora `research/trials/centosettima_bis.csv` né `centosettima_bis.py` (previsto). Nessun seme: scrivere seme 0.

## Punti bloccanti

### 1. BLOCCANTE: i dati del Bitcoin prima del periodo non sono controllati
Le regole dicono «prima del calcolo si scrive se i giorni mancanti dell'archivio cadono nel periodo, in particolare su BTC». `buchi_nel_periodo`
guarda solo da `giorni[0]` (4 gennaio 2021). Per ER servono le chiusure da 31 giorni prima (4 dicembre 2020), e per il confronto con F5
la banda parte dal 2020.
*Correzione più prudente:* «Il controllo dei buchi del Bitcoin si fa su `pan["close"]` da `se.INIZIO - 31` al 4 ottobre 2026 (una riga per
giorno, nessun NaN); se manca anche una sola chiusura il giorno interessato e i 30 successivi sono "nessuna direzione" (vedi punto 3) e
si scrive l'elenco nel rapporto. Se mancano più di 5 chiusure del Bitcoin in tutto, la prova si ferma e si segnala».

### 2. BLOCCANTE: controllo dei motori «scarto piccolo come in 168» senza numero
«Se lo scarto non è piccolo come in 168, la prova non si calcola». In 168 lo scarto massimo del netto settimanale (serie rifatte contro le
salvate) era: G1 0,0073, G11 0,0091, G1N 0,0087, F5 0,0018 (`esame.json`, `scarto_serie_rifatte`). Non c'è una soglia. Inoltre le serie salvate
di G1 sono del 30 ottobre con il pannello di allora (nota di 168, `rifatte.json`): lo scarto può essere più grande ora per il pannello nuovo,
non per un errore.
*Correzione più prudente:* «Si rifanno G1 (`W1`) e F5 (`W5` costante nella settimana, a mercato, come B-con-sola-F5 di 168) e si confronta lo scarto
massimo del netto settimanale con i numeri di 168 sopra; si prosegue se G1 ≤ 0,01 e F5 ≤ 0,005; sopra, ci si ferma e si scrive perché. La F5
rifatta non è la F5 settimanale (riequilibrio giornaliero pagato): per il controllo dei pesi si confronta il lordo e i pesi del lunedì, non
le spese». (Domanda 2 sotto.)

### 3. BLOCCANTE: ER non calcolabile e casi limite non scritti
«Meno di 31 chiusure» non dice cosa succede con un buco *dentro* la finestra (ci sono 31 posti, ma non tutti pieni) né con il denominatore zero.
*Correzione più prudente:* «ER è calcolabile solo se tutte e 31 le chiusure `C[t-31..t-1]` di BTCUSDT sono finite e il denominatore è maggiore
di zero; altrimenti il giorno è "nessuna direzione" (F5)». Il confronto è `ER >= soglia`, con soglia 0,20 e 0,30 esatte (nessun arrotondamento).

## Altre ambiguità

### 4. G1 «virtuale» nei giorni di F5
Le regole dicono «Peso del giorno = W1[g] se direzione, W5[g] altrimenti» e rimandano a `centosesta.py`, dove `W1` e `W5` sono serie intere calcolate
ciascuna per conto suo (la banda di G1 ha memoria, e continua a girare nel calcolo anche nei giorni in cui la variante segue F5). Altra lettura:
G1 riparte con memoria azzerata a ogni cambio di stato. *Correzione:* «`W1` e `W5` si calcolano intere, indipendenti dallo stato, e si
sceglie riga per riga; nessuna memoria azzerata al cambio». Al primo giorno (4 gennaio 2021) le spese di apertura si pagano come in G1.

### 5. Spese di F5 nei giorni di F5: non uguali alla F5 di confronto
Nei giorni "senza direzione" il conto della variante è con ordini limite (`spese_a_limite`) e con il riequilibrio giornaliero di F5; la F5 di
confronto (`risultati_controllo_parita/settimane_F5`) è settimanale a mercato. Quindi le due non sono la stessa spesa neanche in un anno tutto
senza direzione. *Correzione:* scriverlo; nel rapporto dare anche «B con la sola F5» di 168 (stessa funzione `conto_giorni` su `W5`) come
confronto della parte "F5" nello stesso motore, e dire che il confronto con F5 settimanale vale per il rendimento, non per le spese.

### 6. «Spese dovute ai cambi» e «più della metà della differenza con G1»
Non è definito come si isolano. *Correzione:* «cambio di stato = giorno `g` con stato diverso dal giorno prima; spese dei cambi = somma di `spese`
dei soli giorni di cambio (valore per eccesso: il giorno ha anche spese normali, che si riportano a parte)». Il «guadagno» è
`netto annuo variante − netto annuo G1`. Il fallimento utile scatta se spese dei cambi (annue) > metà di quel guadagno quando positivo; se il guadagno è
negativo o zero, i cambi non spiegano la differenza e si scrive soltanto «nessun guadagno su G1».

### 7. «Anni senza direzione» e «con direzione»
Non è dato come classificare gli anni. *Correzione:* per ogni soglia, un anno è «con direzione» se la quota di giorni con direzione è almeno il 50%, altrimenti «senza»;
puramente descrittivo, e si dà anche la quota per anno (già richiesta). Per sicurezza si riporta il netto di G1, di F5 e della variante *per giorni di stato*
(somma dei netti dei giorni con direzione e senza direzione), che non richiede la classifica degli anni.

### 8. Esame, famiglie e F5 vecchia
`te.esito` ha ancora soglia 0,95 e «meno di 4 anni»: si usa `esito_regole` di `centosesta.py` (le regole lo dicono). `corretto_famiglie` va
chiamata con `nuove = {"169 A": ..., "169 B": ...}` e `candidate = {"169 A": e["intero"], "169 B": e["intero"]}`. Nomi nuovi per non scontrarsi con «168 A/B».
La F5 del mazzo resta la vecchia (la serie `risultati_ventiquattresima`): nota nel rapporto, come in 168. «Ogni anno positivo» = ogni anno di calendario
dal 2021 al 2026, compreso il 2026 parziale (39 settimane), come in 168.
Come in 168, la serie è `settimane_A.csv.gz` / `settimane_B.csv.gz` con le colonne di `pr.COLONNE`; il giorno peggiore da `giorni` della variante.

### 9. Parte in avanti
«Lo stato di ER di ogni giorno dal 16 novembre» richiede le chiusure del Bitcoin dal 16 novembre (e 31 giorni prima). Il pannello arriva «all'ultimo giorno
scaricato» (togliendo i giorni in coda parziali) e non so fin dove sia oggi; le risposte «stato» non danno la chiusura del Bitcoin come serie. Non si scarica niente.
*Correzione:* «si usa il pannello fin dove arriva; i giorni dopo l'ultimo chiuso del pannello non si calcolano; se il pannello arriva prima del 16 novembre la parte
in avanti non si fa e si scrive. Le equity di G1 e F5 reali si leggono come in 168 (`avanti()`: risposta con ora più vicina alle 04:15 UTC, solo dal 31 ottobre
perché è da lì che F5 ha le righe `equity`); il periodo 16–30 novembre ha quindi solo G1 e F5 dalle righe che ci sono, senza interpolare». Non entra nel conto.

### 10. Periodo
Chiaro: 4 gennaio 2021 – 4 ottobre 2026, 300 settimane, `se.INIZIO`, `pr.FINE`; scrivere che l'ultimo lunedì è il 28 settembre 2026.
Il controllo del conteggio: `len(comuni) == 300` come in 168.

## Domande aperte (testuali)
1. I buchi del Bitcoin prima del 4 gennaio 2021 (dal 4 dicembre 2020) si controllano e, se ce n'è uno, che cosa succede (proposta: giorni "nessuna direzione"; più di 5 chiusure mancanti = fermarsi)?
2. Qual è la soglia dello scarto dei motori: G1 ≤ 0,01 e F5 ≤ 0,005 sul netto settimanale (proposta) oppure altra?
3. Un buco dentro la finestra di ER vale «nessuna direzione» (proposta)?
4. `W1` e `W5` si calcolano intere e si sceglie riga per riga (proposta), o G1 riparte con memoria azzerata a ogni cambio?
5. Le spese dei cambi si misurano come somma delle spese dei soli giorni di cambio (proposta)? E il confronto «più della metà della differenza con G1» è sul netto annuo?
6. Gli anni «con direzione» / «senza direzione» si decidono con la quota di giorni ≥ 50%?
7. La parte in avanti si fa solo fino a dove arriva il pannello, senza scaricare niente?
