# Consegna della campagna BTCUSDT (protocollo 4.4, Passo 3)

Sessione di campagna dell'8 ottobre 2026. Tutti i numeri vengono dal log
(`log.jsonl`, con l'identificativo della voce fra parentesi). Nessun candidato è
«validato»: l'esito dell'asticella è provvisorio e lo conferma il coordinamento al Passo 4.

## In breve

* **Un candidato va al vault, con esito provvisorio: BTCUSDT-V10.** È la rottura di
  volatilità dall'apertura del giorno di Larry Williams, long, a 1 ora.
* È un vantaggio **piccolo e fragile**:
  * in validazione l'R medio è +0,048 e il profit factor 1,13;
  * senza i 3 trade migliori l'R di validazione diventa negativo;
  * in validazione non batte «nettamente» la baseline (b) (t 1,69 contro una soglia di
    2,04);
  * passa l'asticella solo perché è l'unico candidato (p-value 0,048 ≤ 0,10).
* Con 30 varianti provate, un solo candidato rimasto è del tutto compatibile con il caso.

## Budget e varianti

| | |
|---|---|
| Varianti testate (budget) | 30 su 30 |
| Varianti di idee nuove | 25 (25 famiglie), da 17 fonti e 13 meccanismi diversi |
| Ritocchi testati | 5: V31, V32, V33, V35 (famiglia V19), V37 (famiglia V28) |
| Ritocchi sotto i trade minimi (non consumano budget, contano nella famiglia) | 2: V34 (famiglia V19), V36 (famiglia V28) |
| Varianti di idee nuove sotto i trade minimi (scarti) | 5: V12, V13, V23, V24, V26 |
| Candidati di Fase 2 | 5: V10, V11, V32, V33, V35 |
| Caduti in Fase 4 | V32, V33, V35: R negativo a costi doppi e crollo col ritardo |
| Caduto in Fase 5 (scettico) | V11: con lo stop fisso il vantaggio sparisce (S01) |
| In validazione | V10 (unico, famiglia V10) |

## Candidato BTCUSDT-V10

### Regole (congelate in `candidati/V10/regole.md`)

| | |
|---|---|
| Moneta, timeframe, direzione | BTCUSDT, 1h, solo long |
| Ingresso | prima chiusura oraria del giorno UTC sopra apertura del giorno + 0,5 × (high − low del giorno UTC precedente); nessun segnale sulla barra delle 23:00; ingresso all'apertura della barra dopo |
| Stop | apertura del giorno (last price) |
| Uscita | alla chiusura della barra delle 23:00 UTC (si esce alle 00:00); nessun target |
| Dimensione e leva | rischio 1% a trade, leva massima 2 (quantità ridotta al tetto se serve), margine isolato |

**Motivo economico.** Quando il prezzo si allontana dall'apertura di oltre mezzo range del
giorno prima, è arrivato un flusso che tende a continuare fino a fine giornata: ordini
spezzati, chi insegue il movimento, stop degli short.

### Metriche separate per periodo

| | Costruzione (2020-01-01 → 2022-10-18) | Validazione (2022-10-19 → 2023-12-31) |
|---|---|---|
| Trade | 300 | 136 |
| R medio a trade | +0,149 | +0,048 |
| R medio per anno | 2020 +0,345; 2021 +0,015; 2022 +0,046 | 2022 −0,003 (19 trade); 2023 +0,056 (117 trade) |
| R medio senza i 3 migliori | +0,082 | −0,100 |
| Profit factor | 1,36 | 1,13 |
| Drawdown massimo | 12,7% | 13,7% |
| Rendimento | totale +53,2%; per anno 2020 +47,0%, 2021 +1,2%, 2022 +2,9% | totale composto +6,4% (non calcolato per anno) |
| Win rate | 47,7% | 40,4% |
| Baseline (a) | −0,832; t 3,29, netta | −1,342; t 2,23, netta |
| Baseline (b) | −0,306; t 2,35, netta | −0,570; t 1,69, **non netta** (soglia 2,04) |
| Percentile fra le simulazioni casuali | 96,5 | 96,5 |
| Buy and hold long (contesto) | 2020 +302%; 2021 +59%; 2022 (al 18 ott) −58% | 2022 (dal 19 ott) −15%; 2023 +156% |
| Trade ridotti per il tetto di leva | 0 | 10 |
| Violazioni della liquidazione | 0 | 0 |
| Stop oltre il 6% | 16 | 3 |

### Esito delle verifiche della Fase 4 (sui dati di costruzione)

Tutte superate (BTCUSDT-V10-F01..F07, nota BTCUSDT-V10-F):

* robustezza: con k 0,4 e 0,6 il t contro la (b) è 3,07 e 2,23, entrambi netti;
* timeframe adiacenti: 30m t 2,45, 2h t 2,39;
* ritardo di una barra: t 1,87, positivo e sopra la metà di 2,35;
* costi doppi: R +0,076, t 3,59, netta;
* stabilità: 2020, 2021 e 2022 sopra la media della (b);
* trade estremi: senza i 3 migliori R +0,082, sopra la (b);
* regola intra-barra opposta: nessuna differenza (non c'è target);
* liquidazione: nessuna violazione.

**Fase 5, lo scettico (S01).** Con lo stop originale le baseline sono molto negative,
perché gli ingressi a caso hanno lo stop all'apertura del giorno, spesso vicinissimo, e
quindi costi enormi in R. Rifatto il test con lo stop fisso al 2% per il candidato e per le
baseline: R +0,173 contro una (b) di −0,039, t 3,10, netta. L'R è positivo in tutti e tre
gli anni (+0,29, +0,09, +0,11). Il vantaggio di costruzione non è solo un effetto della
normalizzazione.

### Rischi noti

* In costruzione più di metà del rendimento viene dal 2020; nel 2021 l'R è quasi zero.
* In validazione il risultato dipende da pochi trade: senza i 3 migliori è negativo.
* Il p-value di validazione (0,048) viene da un confronto con una (b) depressa dallo stesso
  effetto di normalizzazione visto in costruzione. Il test con lo stop fisso non si rifà in
  validazione, perché la validazione si usa una volta sola. Il p-value è quindi
  probabilmente ottimista.
* Fortuna: 30 varianti, un solo candidato rimasto. Senza alcun vantaggio, ci si aspetta
  circa 0-0,6 varianti «nette» per caso (sezione 11).
* Lo slippage della scheda (0,01% per lato) è ottimista per il 2020, quando il volume era un
  quarto di quello del 2023 (`fase0_dati.md`).

### Asticella (esito provvisorio)

* Candidati che hanno girato in validazione: m = 1.
* p-value contro la (b) di validazione: 0,0478 ≤ (1/1) × 0,10, quindi passa.
* **Esito provvisorio**: lo conferma il coordinamento al Passo 4.

### Criterio del vault (`criterio_vault`, tutte insieme)

1. Profit factor dopo i costi almeno 1,10.
2. Almeno 30 trade.
3. Rendimento totale positivo.
4. R medio sopra il 90° percentile degli R medi delle entrate casuali con la stessa uscita,
   sul periodo del vault.

### Paper

* Frequenza: circa 9 trade al mese (costruzione 300 in 1.022 giorni, 8,8 al mese;
  validazione 136 in 439 giorni, 9,3 al mese).
* Per arrivare a 50 trade (`paper_trade_minimi`) servono circa 5,5-6 mesi.

### Il sistema può eseguirlo così com'è?

No, servono aggiunte (da `config/regole_dimensione.md`):

* il timeframe 1h il sistema lo ha dal vivo;
* una strategia del protocollo può operare solo con l'aggiunta «coppia del protocollo»
  (abilitazione senza il gate), decisione n. 4 del Passo 0;
* l'uscita a ora fissa (fine del giorno UTC) va verificata nella forma che il sistema sa
  eseguire;
* lo stop supera il tetto del 6% in circa il 5% dei trade (16 su 300 in costruzione, 3 su
  136 in validazione): il sistema quei setup li rifiuterebbe. Le regole non cambiano, quindi
  serve una decisione (accettare i trade in meno o rivedere il tetto) prima del Passo 9;
* la tenuta massima è di 23 ore, entro l'orizzonte di 96 barre.

### Previsione (scritta ora, prima del vault)

* **Vault (2024-01 → 2026-09):** probabilità di passare il criterio intorno al 40%.
  * La condizione del 90° percentile casuale è facile per questo candidato: le entrate a
    caso con lo stesso stop hanno R molto negativo.
  * Il punto debole è il profit factor: 1,36 in costruzione e 1,13 in validazione, con un
    calo. Prevedo un profit factor fra 1,00 e 1,20 e un R medio fra −0,02 e +0,10.
* **Trasferimento:** sulle altre monete prevedo che passi il criterio su 0-2 monete. Battere
  nettamente la (b) dentro il controllo «era solo il mercato» sarà favorito dallo stesso
  effetto di normalizzazione, ma il profit factor sopra 1,10 su monete con costi più alti è
  improbabile.

## Le altre idee

Riepilogo in `lezioni_moneta.md`; dettaglio voce per voce nel log.
