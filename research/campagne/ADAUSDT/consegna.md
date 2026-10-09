# ADAUSDT — consegna della campagna (protocollo 4.5)

Scritta il 2026-10-09. Log: `log.jsonl` (ogni numero qui sotto ha la sua voce). Idee: `ipotesi.md`.
Codice: `codice/`. Dati: `fase0_dati.md`.

**Esito in una riga:** un candidato, ADAUSDT-037, va in validazione e passa l'asticella in modo
provvisorio (p = 0,014, con m = 1). Ma il suo risultato di validazione dipende quasi tutto da 3 trade.
In più la prova dello scettico della Fase 5 dice che il vantaggio di costruzione viene dallo stato del
mercato scelto dai filtri, non dal meccanismo dell'idea. Lo consegno al vault con forti riserve. Non
lo dichiaro «validato».

## Il candidato ADAUSDT-037

### Regole (congelate in `candidati/ADAUSDT-037/regole.md`, sha256 731a0656…54c9)

ADAUSDT, candele da 15 minuti, **long**. Intervallo d'apertura: massimo e minimo delle 4 barre fra le
00:00 e le 01:00 UTC. Ingresso all'apertura della barra dopo una chiusura che passa sopra il massimo
dell'intervallo (la chiusura precedente era sotto o uguale), fra le 01:15 e le 19:45 UTC. Servono anche
due filtri: la chiusura sopra la media semplice di 20 giorni (1.920 barre), e BTCUSDT in calo nelle 24
ore prima. Stop al minimo dell'intervallo d'apertura, nessun target, uscita alle 00:00 UTC. Dimensione
e leva del bot: rischio 1% per trade, nozionale al massimo 2 volte il capitale, margine isolato. Trade
ridotti per il tetto di leva: 0 in costruzione, 0 in validazione. Violazioni del margine di
liquidazione: 0.

**Motivo economico.** La fonte è Crabel (1990): la rottura dell'intervallo d'apertura prosegue nella
giornata. I filtri vengono dallo studio dei fallimenti della variante senza filtri (024): rotture nella
direzione della tendenza, e forza propria di ADA mentre BTC scende. È un candidato nato da **ritocchi**
(il quarto della famiglia 024), non da un'idea nuova.

### Metriche

| | costruzione (2020-01-31 → 2022-10-18) | validazione (2022-10-19 → 2023-12-31) |
|---|---|---|
| trade | 178 | 82 |
| R medio a trade | 0,252 | 0,624 |
| R medio senza i 3 migliori | 0,109 | **0,014** |
| profit factor | 1,42 | 2,15 |
| win rate | 43% | 39% |
| rendimento per anno | 2020 +26,7%, 2021 +24,2%, 2022 −3,1% | 2022 (ott-dic) −5,4%, 2023 +68,7% |
| R medio per anno d'uscita | 2020 0,399; 2021 0,305; 2022 −0,069 | 2022 −0,683; 2023 0,765 |
| drawdown massimo | 10,5% | non calcolato (la curva del motore parte dal 2020) |
| baseline (a) | −0,736; t 2,31, netta | −1,154; t 3,65, netta |
| baseline (b), 200 simulazioni | −0,137; t 2,51, netta; percentile 98 | −0,312; t 2,28, netta; percentile 99 |
| buy and hold (contesto) | — | 2022 long −32%, 2023 long +142% |

### Verifiche della Fase 4 (costruzione)

Le ha superate tutte (log 037-V01..V05, nota N026):
* costi doppi: R 0,159, netta contro la (b) a costi doppi (t 3,03);
* ritardo di una barra: t 2,05 contro 2,51;
* regola intra-barra opposta: nessuna differenza, perché non c'è target;
* robustezza: 6 casi su 6 con t positivo, 5 su 6 netti. La soglia di BTC è 0, e spostata del 20% resta 0;
* timeframe adiacente 30m: t 2,38;
* stabilità per anno: superata;
* pochi trade estremi in costruzione: superata;
* liquidazione: nessuna violazione.

### Rischi noti (i più importanti per primi)

1. **Il risultato di validazione è fatto di 3 trade.** Senza i 3 migliori, l'R medio scende da 0,624 a
   0,014. Su circa 51 R totali, quei 3 trade ne valgono circa 50. Con uno stop variabile (il minimo
   dell'intervallo), una giornata di rialzo forte con un intervallo stretto vale decine di R.
2. **Prova dello scettico (Fase 5, nota N034).** Entrando a caso, ma solo nelle barre dove valgono i due
   filtri, con lo stesso stop e la stessa uscita, l'R medio in costruzione è già +0,110. 037 (+0,252)
   non batte nettamente questa baseline: t 0,63, percentile 77. Il vantaggio viene dallo stato del
   mercato (ADA sopra la media a 20 giorni mentre BTC scende), non dalla rottura.
3. **I filtri sono nati dai dati di costruzione della stessa famiglia.** La famiglia ha avuto 5
   ritocchi; il candidato è il quarto.
4. **Le baseline sono molto negative per la distanza dello stop.** La (a) e la (b) entrano anche quando
   il prezzo è vicinissimo al minimo dell'intervallo: stop di pochi decimi di punto, e costo di un giro
   grande in R. Una parte del «battere le baseline» viene da qui (nota N011). È lo stesso motivo per cui
   025, 034, 035, 039 e 040 battevano le baseline ma sono caduti ai costi doppi.
5. Il 2022 (costruzione e validazione) è negativo; il rendimento viene dai rialzi del 2020-21 e del
   2023.
6. Slippage della scheda (0,02%): ottimista per il 2020, quando il volume medio era di 60 milioni di USDT
   al giorno (fascia 0,05%).

### Budget, asticella, vault

* Varianti usate: **30 su 30**. 22 da idee nuove (15 idee, 22 famiglie) e 8 ritocchi: 5 nella famiglia
  024, 3 nella famiglia 009. In più 11 scarti per trade minimi, che non consumano budget.
* Candidati in Fase 2: 6. Uno da un'idea nuova (025) e cinque da ritocchi (034, 035, 037, 039, 040).
  Scartati in Fase 4: 025, 034, 035, 039 e 040, tutti per i costi doppi; 040 anche per il ritardo. In
  validazione è andato solo 037, unico superstite della sua famiglia.
* **p-value di validazione 0,0139** contro la (b) di validazione. Benjamini-Hochberg al 10% con m = 1:
  **passa, esito PROVVISORIO** (lo conferma il coordinamento al Passo 4).
* Criterio del vault (`criterio_vault`): profit factor almeno 1,10, almeno 30 trade, rendimento totale
  positivo, R medio sopra il 90° percentile delle entrate casuali con la stessa uscita, tutto sul periodo
  del vault.

### Paper e bot

* Frequenza nel backtest: circa 5,6 trade al mese (178 in circa 31,5 mesi di costruzione utile; 82 in
  14,4 mesi di validazione). Per arrivare a 50 trade servono circa 9 mesi.
* Il bot non può eseguirla così com'è. Servono una strategia scritta in codice e l'abilitazione della
  coppia senza il gate (fatto `esecuzione_strategie_bot` del Passo 0). Il resto è compatibile: candele
  da 15 minuti (il bot le ha dal vivo), stop medio 3,1% in costruzione e 1,6% in validazione (sotto il 6%
  del bot), durata al massimo 23 ore, cioè 92 barre da 15 minuti (sotto le 96 del bot).

### Previsione per il vault e il trasferimento

* **Vault:** il candidato più probabilmente fallisce, con R medio vicino a zero o negativo e profit
  factor sotto 1,10. Il motivo: la prova dello scettico e la dipendenza da pochi trade. Lo può passare
  solo se nel 2024-2026 ci sono di nuovo poche giornate di rialzo forte con intervallo stretto nelle
  condizioni dei filtri: è un risultato da pochi eventi, non un vantaggio ripetibile.
* **Trasferimento:** non mi aspetto che si trasferisca. Il filtro su BTC lo lega alla relazione fra ADA
  e BTC, e lo stop variabile rende l'R di ogni moneta dominato dai suoi giorni estremi.

## Idee provate (riepilogo)

Nessuna delle 15 idee ha dato un vantaggio che regga, tranne con le riserve sopra. Dettaglio in
`lezioni_moneta.md`.

## Misure di processo

Ricavate dal log (`codice/misure.py`) e da `ipotesi.md`. L'orologio è quello della macchina
(`date -u`).

* **Durata:** dalla prima voce (2026-10-09 15:25:34 UTC) all'ultima prima della consegna (16:10 UTC),
  circa 44 minuti, uguale con e senza pause (nessuna pausa registrata). La sessione è una sola.
* **Minuti per idea**, dalla registrazione della prima variante all'ultimo risultato. Le idee sono state
  registrate e testate a lotti, quindi i minuti delle idee nuove sono quasi tutti sotto i 2 minuti:
  I-01 0,5; I-02 0,5; I-04 0,4; I-06 1,2; I-07 1,2; I-10 1,2; I-11 1,4; I-12 1,7; I-14 0,4; I-15 0,4.
  Le idee con i ritocchi durano di più: I-05 27,3 e I-13 22,1. Le idee I-03, I-08 e I-09 non hanno
  varianti testate (solo scarti per trade minimi).
* **Spiegazioni concorrenti scritte in `ipotesi.md`:** 10 per ognuna delle 15 idee (I-01 … I-15).
* **Candidati in Fase 2:** 1 da idee nuove (025), 5 da ritocchi (034, 035, 037, 039, 040).
* **Varianti nette contro la (a) e la (b) con R medio dopo i costi non positivo:** 3 (009, 024, 038).
* Rifiuti del guardiano: 5 (note N002, N003, N005, N009 e N019), tutti per la forma dei comandi; nessuno
  aggirato.
