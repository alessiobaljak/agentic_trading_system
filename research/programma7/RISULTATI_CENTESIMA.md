# Risultati della prova 162 — il funding fra il perpetuo in USDT e quello in USDC della stessa moneta (idea 147)

## Riepilogo
**Esito secondo il criterio scritto: NON PASSA (tutte e due le varianti).** Prova non promettente. Nessun giudizio sulla credibilità (spetta a backtest-auditor).
- A (lenta): netto +0,10% l'anno su capitale (2024 -0,85%, 2025 +1,03%, 2026 -0,08%), Sharpe settimanale 0,09, t 0,15, Sharpe corretto 0,00. Falliscono: ogni anno positivo, t da 3, Sharpe corretto da 0,80. Passa solo il margine (0 giorni a rischio) e il netto positivo (di pochissimo). Sotto il 3% l'anno: anche passando sarebbe «non promosso per poco valore».
- B (veloce): netto -5,55% l'anno (tutti gli anni negativi), Sharpe -6,23, t -10,15. Il funding incassato (+4,6% l'anno) è mangiato dalle spese (10,4% l'anno) per i continui cambi di lato e di numero di monete.
- Il funding lordo è piccolo (A 2,2%, B 4,6% l'anno) e il prezzo non guadagna nulla (A -0,2%, B +0,3%): come previsto dall'avviso onesto delle regole.

## La prova come è scritta (citata, non riformulata) e scala di tempo
Regole: `research/programma7/CENTESIMA.md` (commit f0b0f61), vale la sezione «Chiusura della verifica» (14 punti). Segnale: «d = media per giorno (somma dei
funding pagati nel giorno dal contratto in USDT meno la somma di quelli del contratto in USDC) sulle ultime L giornate intere. Se d > +θ: vendere il perpetuo
in USDT e comprare quello in USDC. Se d < −θ: il contrario. Se |d| ≤ θ: moneta ferma». Varianti: «A (lenta): L = 30 giorni, θ = 0,006% al giorno, decisione solo il
primo giorno di ogni mese. B (veloce): L = 7 giorni, θ = 0,015% al giorno, decisione solo il lunedì.» Pesi uguali, a mercato (0,05% per gamba più scarto 0,01% su BTC/ETH/SOL,
0,02% sulle altre), margine in comune (a rischio sotto il 10% del capitale, liquidato sotto lo 0,5% del valore delle gambe). Scala di tempo: giornaliera, esame sulle
serie settimanali (lunedì). Periodo: dal primo giorno con almeno una moneta non ferma (A 1 marzo 2024, B 19 febbraio 2024) al 30 ottobre 2026.

## Implementazione (file, commit)
- `research/programma7/centesima_dati.py`: scarico (8.467 file scaricati, 125 con risposta 404 ricordati, 0 errori), impronte e buchi in `risultati_centesima/impronte_dati.json`; dati in `research/data/centesima/` (non committati).
- `research/programma7/centesima.py`: la prova (deterministica, nessun seme; circa 1 minuto). Commit: non ancora committato (i file sono nuovi nell'albero; il registro delle varianti scrive il commit di partenza, quello delle regole f0b0f61 o successivo).
- Uscite: `risultati_centesima/giorni_{A,B}.csv.gz`, `settimane_{A,B}.csv.gz` (colonna `netto`, indice = lunedì, formato come le prove 157-161), `esame.json` (tutti i numeri e i controlli), `impronte_dati.json`.

## Varianti provate
2 (A e B), come scritto. Registro: `research/trials/centesima.csv` (una riga ciascuna, esito «non passa»). Nessuna variante fallita o interrotta.

## Risultati
| | A | B |
|---|---|---|
| giorni della serie (fermi) | 974 (0) | 985 (14) |
| monete medie in posizione | 15,5 | 6,9 |
| netto annuo su capitale | +0,10% | -5,55% |
| 2024 / 2025 / 2026 (10 mesi) | -0,85% / +1,03% / -0,08% | -5,36% / -5,08% / -6,30% |
| lordo da prezzo / funding / spese (annui) | -0,18% / +2,21% / 1,94% | +0,27% / +4,56% / 10,38% |
| Sharpe settimanale (dopo `periodo()`), settimane | 0,09 (137) | -6,23 (138) |
| t | 0,15 | -10,15 |
| Sharpe corretto per famiglie (con tutte e due in `nuove`, mazzo 283 serie, 198 famiglie) | 0,00 | 0,00 |
| Sharpe su 365 giorni fino al 30 ottobre (descrizione) | 0,12 | -3,50 |
| discesa più grande (settimanale / giornaliera) | -1,49% / -1,60% | -14,31% / -14,67% |
| giorni a rischio / liquidati (margine in comune) | 0 / 0 | 0 / 0 |
| equity minima oraria, leva massima del conto | 0,993 / 4,1x | 0,993 / 3,0x |
| condizioni dell'esame | netto>0 sì; ogni anno no; t no; corretto no; margine sì | netto>0 no; ogni anno no; t no; corretto no; margine sì |

Controlli descrittivi (tutti in `esame.json`, chiave `controlli`):
- **Regola per gamba isolata** (solo descrizione): A 385 giorni a rischio e 267 liquidati su 974; B 88 e 38 su 971. Con il margine in comune sarebbero 0: il risultato sul margine dipende da quella decisione.
- **Base massima** fra i due prezzi mark (nelle posizioni tenute): 5,85% (ETHFI, ottobre 2025). Su tutte le ore e le monete: percentili 1%-99% da -0,23% a +52%, ma i valori estremi sono quasi tutti di MATIC dopo la fine del contratto (massimo 146%); le altre monete hanno al massimo 2-8% (KAITO 8,0%, ETHFI 5,8%, FIL 5,1%).
- **Persistenza** (stessa segnalazione 30 giorni dopo, sulle coppie moneta-giorno con segnale): A 49,3% stessa, 9,4% opposta, 41,3% ferma; B 23,9% stessa, 9,1% opposta, 67,0% ferma.
- **Differenza media d** per anno e moneta (in % al giorno): in `esame.json`; esempi BTC 2024 +0,0002%, 2025 +0,0002%, 2026 -0,0007%; DOGE +0,0005%, -0,0028%, -0,0037%: quasi tutta sotto la soglia θ (A 0,006%, B 0,015%).
- **Cambi di lato**: A 52 (204 aperture, 32 decisioni, 15,5 monete per decisione); B 48 (567 aperture, 141 decisioni, 6,9 monete). Monete ferme per soglia: A 471, B 3.331 casi moneta-decisione; ferme per giorno senza funding: 0 in tutti e due.
- **Con ordine limite (0,02%)**: A +0,93% l'anno (2024 +0,02%, 2025 +1,88%, 2026 +0,71%; Sharpe 1,40, t 2,27); B -1,08% (Sharpe -1,32). Non è una variante, non cambia l'esito.
- **Senza la moneta migliore**: A senza BIO -0,05% (Sharpe -0,1); B senza ETHFI -6,29%. In A la moneta migliore da sola vale più del netto intero.
- **G1** (settimane comuni 136-137): correlazione giornaliera A 0,01 / B 0,05; settimanale A -0,03 / B 0,02. G1 sulle stesse settimane +63,5% l'anno (Sharpe 2,56); miscela 80/20 con A +50,8% (Sharpe 2,56), con B +50,1% (Sharpe 2,53). Solo come numero.

## Variante migliore e sua sensibilità alle varianti vicine
Migliore: A (netto +0,10%, ancora non promossa). Non si sono provate varianti vicine (non previste). Le due fornite sono diverse in tutto (finestra, soglia, frequenza): A resta intorno a zero, B è chiaramente negativa. Il netto di A è sensibile alle spese: con ordine limite sale a +0,93%, mai vicino al 3%.

## Anomalie e possibili errori di motore o dati
- Mark a 1 ora mancante per tutti i contratti il 29 giugno 2026 (24 ore): riempito col prezzo scambiato a 1 ora come da regola (conteggi per contratto in `esame.json`, `qualita_dati_mark`). Altre ore vuote: solo prima dell'inizio del contratto o dopo la fine (fuori dalle posizioni).
- MATIC: candele 1d e a 1 ora fino a settembre 2024 (ultimo giorno con candele e funding per tutte e due: 11 settembre 2024); funding USDC fino al 21 gennaio 2026; dopo il contratto la base è assurda (fino al 146%). Chiusura forzata scritta in B il 11 settembre 2024. IP: funding fino al 28 giugno 2026, chiusura forzata in A il 29 giugno 2026.
- Il 28 ottobre 2026 (buco noto dell'archivio) non è comparso nelle serie usate (nessuna candela mancante dentro i periodi dei contratti vivi).
- Nessun errore di motore o caricatore trovato. `asticella.serie_programma7` non elenca ancora la 162: il test `tests/test_asticella_mazzo.py` fallirà finché la sessione principale non aggiunge `risultati_centesima/settimane_{A,B}.csv.gz` (non l'ho toccata).
- Limiti scritti nelle regole: riequilibrio giornaliero implicito a costo zero (pesi 1/N); scarto del USDC uguale a quello del USDT (ottimista); meno di 3 anni di dati.

## Varianti non previste che proporrei (non eseguite)
Nessuna con un perché forte: il lordo (2-5% l'anno) è sotto le spese di qualunque frequenza di cambio. Una versione «tieni sempre la stessa coppia per moneta» sarebbe una variante di altra natura: non la propongo.

## Domande aperte
1. Il margine in comune è stato scelto dalla sessione principale: con la regola per gamba isolata A avrebbe 385 giorni a rischio. Conferma che l'esame si legge con il margine in comune.
2. Letture mie non previste dalle regole (nessuna cambia l'esito, ma cambiano i numeri di poco), da confermare:
   a. Orari dei funding arrotondati al minuto più vicino (scarti di pochi millisecondi nell'archivio).
   b. «Storia» = numero di giorni validi (candela e funding per tutti e due i contratti) strettamente prima di D, non necessariamente consecutivi.
   c. Moneta «viva» il giorno D se ci sono le candele di D e D+1 per tutti e due i contratti e D non supera l'ultimo giorno con funding; altrimenti la posizione si chiude all'apertura di D con le spese di chiusura (punto 10) e le altre monete restano a 1/N della decisione, senza riequilibrio.
   d. Margine: prezzo mark orario all'apertura di ogni ora (istante comune delle due gambe, non massimi e minimi dell'ora); equity azzerata a 1 ad ogni decisione (senza i profitti già incassati); funding nel margine sul valore nominale fisso; spese della decisione dentro l'equity dell'ora 0; mantenimento 0,5% sul valore corrente delle due gambe.
   e. Persistenza: segnale giornaliero di ogni variante (con la sua L e θ) confrontato con quello 30 giorni dopo.
   f. «Senza la moneta migliore»: la migliore per somma dei contributi giornalieri; si rifà la prova togliendo la moneta dall'universo (pesi ricalcolati).
   g. Settimana iniziale parziale: la somma dei netti dei giorni presenti.
