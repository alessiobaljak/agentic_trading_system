# Risultati della prova 157 (CB: funding coperto su Bitcoin ed Ether, senza ricambio)

Tutti i numeri sono in `risultati_novantacinquesima/esame.json`; serie in `settimane_A.csv.gz`, `settimane_B.csv.gz` (colonna `netto`, indice il lunedì in giorni dall'epoca) e `giorni_A.csv.gz`, `giorni_B.csv.gz`.

### Riepilogo
Le due varianti passano le quattro condizioni dell'esame scritto (netto positivo, ogni anno positivo, t da 3, Sharpe corretto da 0,80): esito secondo l'esame **promettente**, da far attaccare a backtest-auditor. Per capitale circa +10,5% l'anno (A) e +10,3% (B), cioè circa 105 e 103 USDT l'anno su 1.000, ma il 2021 pesa molto (+32% da solo); dal 2022 il rendimento è fra +1% e +14% l'anno. Il rapporto con la prova 97 è molto stretto (correlazione settimanale 0,94): stessa famiglia.

### La prova come è scritta e scala di tempo
Regole in `NOVANTACINQUESIMA.md` (commit 0a0b941 più le regole corrette 049a4ae, sezione finale). Scala: conto giornaliero (apertura-apertura), esame sulla serie settimanale lunedì-domenica, dal 4 gennaio 2021 al 4 ottobre 2026 (2.100 giorni, 300 settimane).

### Implementazione
`research/programma7/novantacinquesima.py` (dati: `novantacinquesima_dati.py`). Nessun commit fatto.

### Varianti provate
2: A (N = 30), B (N = 90). Registro: `research/trials/novantacinquesima.csv`. «Sempre dentro» è solo descrittivo e non è registrato.

### Risultati
| | A (30) | B (90) |
|---|---|---|
| per capitale l'anno / USDT su 1.000 | +10,53% / 105,3 | +10,28% / 102,8 |
| per nozionale l'anno | +15,8% | +15,4% |
| Sharpe settimanale, t | 3,92, 9,41 | 3,88, 9,31 |
| discesa massima settimanale / giornaliera | -0,36% / -0,39% | -0,46% / -0,49% |
| peggiore settimana | -0,13% | -0,12% |
| mesi positivi | 62 su 70 | 62 su 70 |
| giorni: positivi / fuori / dentro e negativi | 1650 / 105 / 345 | 1681 / 41 / 378 |
| spese l'anno (per capitale) | 0,32% | 0,17% |
| con ordini limite (controllo) | +10,63% | +10,33% |
| giri di entrata BTC / ETH | 5 / 6 | 2 / 3 |
| giorni dentro BTC / ETH | 1949 / 1898 | 2055 / 1947 |
| Sharpe corretto (famiglie) | 1,00 | 1,00 |
| correlazione con G1 (giorni / settimane) | 0,06 / 0,14 | 0,06 / 0,16 |
| con Bitcoin (giorni) / con la 97 (settimane) | 0,01 / 0,94 | 0,01 / 0,95 |

Anno per anno, per capitale (anno di calendario sui giorni; funding, base, spese, netto):
* A: 2021 +32,4 / +0,1 / -0,4 / +32,1; 2022 +1,9 / 0,0 / -0,65 / +1,2; 2023 +7,8 / -0,1 / -0,06 / +7,6; 2024 +14,1 / +0,1 / -0,3 / +13,9; 2025 +4,9 / 0,0 / -0,02 / +4,9; 2026 +1,5 / 0,0 / -0,4 / +1,0 (tutto in %).
* B: 2021 +32,8 / +0,05 / -0,26 / +32,6; 2022 +1,9 / 0,0 / -0,13 / +1,75; 2023 +5,7 / -0,07 / -0,02 / +5,65; 2024 +13,0 / +0,08 / -0,08 / +13,0; 2025 +5,5 / 0,0 / -0,03 / +5,5; 2026 +1,35 / 0,0 / -0,5 / +0,9.
* Anni dell'esame (lunedì): tutti positivi in A e B (il più basso: 2026, +1,3% e +1,1%). Netto a costi doppi: +0,20% a settimana (circa +10,2% l'anno) in tutte e due.
* BTC ed ETH separati: nel json (`funding_BTC`, ecc.).
* Sempre dentro (descrittivo): +10,1% l'anno, Sharpe 3,82, un giro per moneta: l'uscita sul funding negativo guadagna poco (A +0,4 punti, B +0,2) e il guadagno è tutto nel funding.

Gruppo: «97 CC», «157 A», «157 B» (stessa famiglia della 97). Condizioni non decisive: intervallo del netto sopra zero, ultimo anno positivo, extra su Bitcoin positivo (+10%), almeno 3 trimestri positivi su 4 in ogni anno pieno.

### Variante migliore e sensibilità
A e B sono quasi uguali (differenza 0,25 punti l'anno, dentro il rumore); per le regole vale la lenta (B), che fa meno giri.

### Anomalie e possibili errori di motore o dati
* **La regola del margine scatta moltissimo**: 57 volte su BTC e 50 su ETH in A, 26 e 48 in B. Con il prezzo salito fino a +327% (BTC) e +391% (ETH) mentre si è dentro, la perdita del perpetuo arriva a 3,4-3,7 volte la riserva (3,8 col massimo del giorno): una vera liquidazione sul perpetuo a leva 2 sarebbe avvenuta. Il conto applica la regola scritta (vendita del pronti, Q cala), ma i soldi ricavati restano fermi a rendimento zero e la liquidazione intragiornaliera non è modellata. Il guadagno del 2021 è il risultato più esposto a questo punto.
* Corrispondenza con la 97: 0,94 e discesa molto bassa (-0,4%): pura raccolta del funding, senza rischio di prezzo nel conto; il rischio vero (borsa, liquidazione, USDT) non è misurato dal passato.
* G1: usato il file `giorni_G1.csv.gz` esistente, non ricalcolato.

### Varianti non previste che proporrei (non eseguite)
Ribilanciamento periodico del margine (rimettere margine senza vendere il pronti) per vedere quanto del 2021 sopravvive a una liquidazione più realistica.

### Domande aperte
1. Regola del margine (letture mie dove il testo non dice): perdita misurata all'apertura del giorno; quantità venduta q = eccesso/(prezzo×(1-0,15%)); la riserva sale dell'eccesso, Q cala di q, costi su tutte e due le gambe; capitale fisso 1 senza capitalizzare. Va bene?
2. Interessi sul contante ricavato dalle vendite: zero (come le regole), ok?
3. Funding calcolato su Q×apertura del perpetuo del giorno.

Letture che ho dovuto scegliere: 1) mark = apertura del perpetuo; 2) capitale del conto = 1 fisso; 3) G1 dal file esistente; 4) mesi positivi sui giorni sommati per mese (70 mesi, gen 2021 - ott 2026); 5) «fuori» = nessuna moneta dentro nel giorno.
