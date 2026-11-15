# Risultati della prova 158 — G1 con la leva più alta (A = 300%, B = 400%) con lo stop del conto vero

Eseguita il 15 novembre 2026 da strategy-researcher. Regole: `NOVANTASEIESIMA.md` (810c620, corretta in 049a4ae). Codice: `novantaseiesima.py` (non
committato). Numeri completi: `risultati_novantaseiesima/esame.json`. Commit del registro: 049a4ae. Seme 158 (nessun elemento casuale).

## Riepilogo
* **Esito secondo l'esame scritto prima: NON promettente, per A e per B.** Tutto passa (netto positivo, ogni anno positivo, t 4,7, nessuna liquidazione con lo
  stop, stop 1 e 2 volte su un massimo di 2) **tranne lo Sharpe corretto con le famiglie: 0,74 (A) e 0,76 (B), contro la soglia 0,80**. Anche G1 ricalcolato oggi
  con lo stesso metodo dà 0,75: il numero è quello di G1, come previsto dalla nota delle regole.
* La leva non cambia lo Sharpe (1,96-1,98 per tutte e tre) ma cambia il resto: rendimento composto sul periodo G1 +1.758%, A +6.699%, B +24.443%; discesa a fine
  giorno −30,1%, −42,1%, −46,8%; **discesa dentro la giornata nel caso peggiore −49%, −71%, −91%**.
* Il peso per moneta supera il 60% del conto in 5 giorni con A e in 21 giorni con B (G1: mai, massimo 43,7%): A e B violano i limiti attuali del conto vero anche
  oltre il 200% di esposizione.
* Alzare i limiti del conto vero lo decide solo il proprietario; questa prova non lo autorizza.

## La prova come è scritta e scala di tempo
Vedi `NOVANTASEIESIMA.md` e le letture della sua ultima sezione. Scala: giornaliera (pesi di G1, ribilancio a mezzanotte), con candele a 1 ora per lo stop, la
liquidazione e la discesa dentro la giornata; Sharpe e t sulle 300 settimane dell'equity composta (4 gennaio 2021 – 4 ottobre 2026 compreso).

## Implementazione (file, commit)
`research/programma7/novantaseiesima.py` (usa `prima.py`, `te.conto`, `cs.spese_a_limite` con candele in memoria, `ast.corretto_famiglie`). Serie in
`risultati_novantaseiesima/`: `settimane_A.csv.gz`, `settimane_B.csv.gz`, `settimane_G1.csv.gz` (colonna `netto`, indice il lunedì in giorni dall'epoca, rendimento
della settimana dall'equity composta con lo stop), `giorni_*_con_stop.csv.gz`, `parita.json`, `esame.json`. Il registro porta il commit 049a4ae (il codice è non committato).

## Varianti provate
3 serie (2 varianti + riferimento) più il controllo di parità: A (m = 1,5), B (m = 2), G1 con stop (m = 1, riferimento, non conta come prova). Sensibilità
dello stop (ripartenza dopo 1 giorno, dopo 28 giorni, fuori per sempre) e serie senza stop: descrittive, non varianti. Registro: `research/trials/novantaseiesima.csv`
(4 righe: parità, A, B, G1 con stop).

## Controllo di parità (m = 1, prima dello stop)
* Valido: lordo, funding, giro e numero di monete coincidono entro 1,0e-16 / 1e-16 / 4,4e-16 / 0 fino al 29 settembre 2026, riferimento `giorni_G1.csv.gz`.
* Spese diverse in 337 giorni del 2021, 365 del 2022, 243 del 2023, 8 del 2026 (fino al 29 settembre), **0 nel 2024 e nel 2025**; somma 0,3665 oggi contro 0,3774.
  Variazioni senza candele a 1 ora oggi **137 su 117.037** (eseguite con il limite 114.550): coerente con le regole. Dopo il 29 settembre 5 giorni diversi (scritto,
  non è un errore).
* Coerenza: lordo(m) e funding(m) = m × quelli di m = 1 (differenza massima 5,6e-17); spese: A = 1,513 × G1, B = 2,037 × G1 (salgono più che in proporzione: il
  limite si esegue più spesso a mercato con pesi più grandi; vedi anomalie).

## Risultati (serie con lo stop, equity composta; G1 di confronto = G1 ricalcolato oggi con stop)
| | G1 (200%) | A (300%) | B (400%) |
|---|---|---|---|
| Composto 2021 (da 4 gen) | +177,9% | +336,2% | +558,0% |
| 2022 | +33,0% | +50,3% | +67,4% |
| 2023 | +6,4% | +7,9% | +8,2% |
| 2024 | +93,1% | +161,1% | +286,7% |
| 2025 | +92,2% | +161,7% | +252,2% |
| 2026 (fino al 4 ott) | +27,3% | +40,7% | +51,2% |
| Composto sul periodo | +1.758% | +6.699% | +24.443% |
| Annuo composto | +66,2% | +108,3% | +160,4% |
| Sharpe (settimane dall'equity) | 1,97 | 1,96 | 1,98 |
| t (settimane) | 4,73 | 4,71 | 4,77 |
| Sharpe / t sui settimanali sommati (accanto) | 1,98 / 4,76 | 1,98 / 4,75 | 2,01 / 4,83 |
| Discesa massima a fine giorno | −30,1% | −42,1% | −46,8% |
| Discesa massima dentro la giornata, chiusure orarie | −30,6% | −42,7% | −47,5% |
| **Discesa dentro la giornata, caso peggiore dell'ora** | **−49,4%** | **−71,0%** | **−90,8%** |
| Giorno peggiore (a fine giorno) | −8,5% (30 gen 2021) | −12,8% | −17,0% |
| Spese annue (punti del capitale) | 6,4 | 9,7 | 13,2 |
| Funding annuo (punti; negativo = incasso) | −28,1 | −42,1 | −55,7 |
| Stop scattati | 0 | 1 | 2 |
| Giorni fuori | 0 | 2 | 12 |
Senza stop: composto G1 +1.758%, A +6.693%, B +22.156%; discesa a fine giorno −30,1%, −42,2%, −52,5%; caso peggiore dentro l'ora −49%, −71%, −91%.
Il costo medio per giro è nelle spese annue (a limite dove l'ora lo permette: 114.550 variazioni su 117.037 con il limite, 137 senza candele).

## Stop (quando)
* A: 16 gennaio 2024 ore 3 (valore dell'ora sotto il livello di scatto di 0,007 del capitale; valore del conto dopo 6,07 contro livello 6,08); riparte il 19 gennaio; 2 giorni fuori.
* B: 6 gennaio 2024 ore 14 (sotto il livello di 0,047; riparte il 12 gennaio, 5 giorni fuori) e 6 agosto 2026 ore 17 (sotto di 0,064; riparte il 14 agosto, 7 giorni fuori).
* G1: nessuno scatto. Rendimento di G1 senza stop nelle giornate fuori: A −0,4%, B −7,6% (lo stop ha evitato quelle perdite, nessun rimbalzo perso in totale).
* **Il pavimento al 65% del capitale della fase non conta mai** (il massimo parte dal capitale e non scende): lo scatto è sempre 0,65 × massimo. Come deciso dalla sessione principale.
* Sensibilità (composto sul periodo, scatti): ripartenza dopo 1 giorno A +6.661% (1), B +22.705% (2); dopo 28 giorni A +5.897% (1), B +22.670% (2); **fuori per sempre**
  A +507% (1 scatto), B +1.022% (1 scatto): lo stop senza ripartenza costa quasi tutto il rendimento (esce prima dell'inizio dei grandi rialzi del 2024-2025).

## Liquidazioni
* **Con lo stop, margine 1%, caso peggiore dell'ora: 0 per G1, A e B. Anche con il margine 2,5%: 0.** Senza stop: 0 e 0 per tutte e tre.
* Il caso peggiore dentro l'ora (comprati al minimo e venduti al massimo insieme) arriva a −91% del capitale di mezzanotte per B: nessuna liquidazione solo perché il
  margine unico lo permette, ma con un solo passo ulteriore sarebbe stata vicina.
* Controllo per singola moneta (margine separato, leva 5, formula esatta: venduta liquidata a +18,8%, comprata a −19,2% sul prezzo delle 00:00): **2.368 coppie moneta-giorno su
  110.755** (quota del portafoglio per coppia in media il 3,1% del capitale con m = 1), 440 monete usate; non dipende da m. Importante per il demo con leva 5 per moneta.
* Candele a 1 ora: 96 coppie moneta-giorno su 110.755 senza candele (quota del peso 0,08%: 2022 0,43%, 2023 0,02%, 2025 0,02%, 2021, 2024, 2026 zero), più 87 ore mancanti dentro giorni con candele
  (portata avanti la chiusura). Differenza fra la chiusura dell'ora 23 e il rendimento giornaliero: media 0,019%, massima 1,4%. Il rischio dentro la giornata è lì sottostimato.

## Sharpe corretto (`corretto_famiglie`, mazzo completo, taglio 0,5; 273 serie + 48 senza serie)
* A 0,741 (t 4,71), B 0,762 (t 4,77), con 194 famiglie; G1 con stop (chiamata a parte) 0,747. Tutte e tre nel gruppo di G1 (con le prove 57 G1, 155, 156, 148 B...), il numero di famiglie non sale.
* Tagli descrittivi: 0,3 → 144 famiglie, A 0,750, B 0,771; 0,7 → 231 famiglie, A 0,624, B 0,649.

## Esame
| | A | B |
|---|---|---|
| Netto positivo | sì | sì |
| Ogni anno positivo (composto) | sì | sì |
| t almeno 3 (4,71 / 4,77) | sì | sì |
| **Sharpe corretto almeno 0,80** | **no (0,74)** | **no (0,76)** |
| Nessuna liquidazione con lo stop | sì | sì |
| Stop al massimo 2 volte | sì (1) | sì (2) |
| Peso per moneta sotto il 60% (descrittivo) | no: 5 giorni, massimo 65,6% | no: 21 giorni, massimo 87,5% |
Esito: **non promettente** (manca solo lo Sharpe corretto; il giudizio sul criterio per il conto vero non è dato perché l'esame 1 non è superato, ma i due criteri
sarebbero rispettati, mentre i limiti attuali del conto vero no).
Punto 3, descrittivo: il composto con lo stop è maggiore di quello di G1 con stop (+6.699% e +24.443% contro +1.758%), ma i criteri del conto vero sono tutti rispettati solo contando
liquidazioni e stop: il tetto del 60% per moneta è superato.

## Controlli descrittivi
* Correlazione giornaliera senza stop con G1: 0,9999997 (A), 0,9999988 (B).
* Peggiori giornate di G1/A/B: 30 gennaio 2021 (−8,5% / −12,8% / −17,0%, responsabile XRP venduta, −9,0 punti per G1), 21 febbraio 2021 (NEO), 11 febbraio 2021 (IOTA).
* Quota di giorni con perdita oltre il 10%: G1 0, A 0,10% (2 giorni), B 0,19% (4 giorni).
* Giorni con una moneta venduta oltre +30% nel giorno: 168; peso totale del lato venduto in quei giorni: 100% (G1), 150% (A), 200% (B) del capitale.

## Variante migliore e sua sensibilità
Per rendimento composto B (+24.443%), per Sharpe corretto B (0,76): nessuna supera 0,80, quindi nessuna variante è migliore ai fini dell'esame. Le sensibilità dello stop sono
sopra: lo stop con ripartenza fa poca differenza (A 6.699 contro 6.693 senza stop; B 24.443 contro 22.156 senza stop), senza ripartenza il rendimento crolla.

## Anomalie e possibili errori di motore o dati
1. Con m = 1,5 e 2 le variazioni eseguite col limite sono 114.535 invece di 114.550 (le «stesse per ogni m» delle regole): differenza di 15 su 117.037, dovuta con ogni probabilità alla
   soglia 1e-9 su |variazione| di `spese_a_limite` (il peso cambia, qualche variazione piccolissima supera o no la soglia). Non indaga né corregge il motore.
2. Le spese A e B salgono più che in proporzione (1,51 e 2,04 volte): probabile effetto della deriva dei pesi e del lato a mercato quando le variazioni sono grandi; descrittivo.
3. Nessuna liquidazione dentro l'ora nemmeno a −91% del conto per B: dipende da margine unico e margine dell'1% (semplificato, Binance usa scaglioni più alti per monete poco liquide).
4. Il controllo per moneta dà 2.368 coppie moneta-giorno (2,1%): ha poca incidenza per il margine unico ma è alto per un demo con leva 5 per moneta.

## Varianti non previste che proporrei (non eseguite)
Nessuna. Un controllo utile per il proprietario: il tetto del 60% per moneta (limite attuale) applicato come regola di pesi di G1 con m = 1,5; non eseguito.

## Domande aperte
1. La differenza di 15 variazioni col limite fra m = 1 e m > 1 va indagata? (anomalia 1).
2. Le «chiusure orarie» per lo stop sono qui le chiusure di ogni ora del giorno; lo stop reale usa la lettura del bot (ogni minuto?): ha senso una sensibilità sullo stop con i minuti?

## Letture che ho dovuto scegliere (oltre a quelle già scritte nell'ultima sezione delle regole)
* Livello di scatto controllato sulle chiusure orarie, massimo corrente aggiornato con ogni chiusura oraria e con l'equity a mezzanotte.
* Giorno di ripartenza: il rendimento di quel giorno usa le spese di apertura da zero (`spese_a_limite` su matrice [0, m×W]); i giorni successivi quelli ordinari.
* Funding del giorno dello stop pro rata (ore trascorse / 24); funding giornaliero come in `te.conto` negli altri giorni.
* Una moneta-giorno senza candele all'ora 0 conta come «solo chiusura»; ore mancanti isolate: chiusura portata avanti, minimo e massimo uguali alla chiusura.
* Discesa dentro la giornata: valore orario / massimo corrente (chiusure e valori alle 00:00 dell'intera equity), anche per il caso peggiore.
* Rendimento «annuo composto» = (equity finale)^(1/(2100/365,25)) − 1.
* Lo Sharpe corretto di G1 con stop è calcolato in una chiamata a parte («158 G1»).
