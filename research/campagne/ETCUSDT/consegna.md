# ETCUSDT — consegna della campagna (Passo 3, protocollo 4.5)

Scritta il 2026-10-09 alle 20:26 UTC dalla sessione di campagna. Tutti i numeri vengono dal log
(`log.jsonl`) e dagli script in `codice/`; nessun numero è stimato a mano. Periodo usato: solo la
costruzione (2020-01-01 → 2022-10-18). Il periodo di validazione (2022-10-19 → 2023-12-31) **non è stato
toccato** e il vault resta chiuso.

## Esito

**Nessuna strategia valida trovata per questa moneta.**

Il budget di 30 varianti è stato usato per intero (23 da idee nuove, 7 ritocchi). Tre varianti, tutte della
stessa famiglia, sono diventate candidati in Fase 2; tutte e tre cadono in Fase 4 (costi doppi e ritardo di
una barra). Nessun candidato arriva alla validazione: nessun p-value, asticella con m = 0, niente da
portare al vault.

## Cosa abbiamo capito (osservato, sui dati di costruzione)

1. **Seguire il trend su ETC nel 2020-2022 rende quanto entrare a caso nella stessa direzione.** Il momento a
   7 giorni (long +0,42 R, short +0,27 R a trade), l'incrocio di medie (long +0,43, short +0,16) e il volume
   alto (long +0,46) hanno R medi alti, ma le entrate casuali con la stessa uscita fanno quasi lo stesso:
   `t` contro la (b) fra 0,4 e 1,75. L'R viene dai trend del periodo, non dal segnale.
2. **Le idee a 1 ora perdono contro i costi.** Squilibrio degli ordini aggressivi, numeri tondi, rottura
   dell'apertura, inversione dopo uno shock, ritardo rispetto a BTC: R medio fra −0,18 e +0,01, nessuna
   batte il caso (`t` contro la (b) fra −1,9 e +0,9). Con lo stop a 2 ATR un giro costa circa 0,1 R.
3. **L'unico segnale che batte nettamente il caso è la continuazione di fine giornata UTC nei giorni in
   calo** (short nell'ultima mezz'ora dopo una giornata negativa, fonte: Gao e coautori 2018; Shen, Urquhart,
   Wang 2022). Contro la (b): `t` 3,15 su 436 trade, e fino a 3,85 nei ritocchi. Ma il guadagno lordo è
   piccolo (circa +0,045 R a trade, 10 punti base nelle giornate in calo, 29 sotto il −5%) e i costi
   (commissioni 0,05% e slippage 0,05% per lato) se lo mangiano: R medio netto da −0,04 a +0,03, negativo a
   costi doppi.
4. **Quell'effetto è del mercato, non di ETC.** Su BTC, nei giorni in calo, l'ultima mezz'ora UTC è la più
   negativa di tutte le 48 mezz'ore (−14,8 punti base lordi, test ETCUSDT-F5-T3). Non dipende dal segno del
   funding (test T4). Senza la condizione sulla giornata (short ogni sera alle 23:30) non batte il caso
   (test T1, `t` 1,29).
5. **Idee che non arrivano a 70 trade in 2,8 anni su una moneta sola:** rottura del canale di 50 barre a 4h
   (43 e 40), funding estremo a 8h (67 e 59), compressione di Bollinger (15 e 17), coppia con BTC (48 e 47),
   ritardo su BTC short (59). Sono scarti, non bocciature: non si sa se funzionano.

## I tre candidati di Fase 2 e perché cadono

Famiglia ETCUSDT-023 (idea I-12, momento dentro la giornata), short, timeframe 30m, stop 2 ATR(14),
uscita dopo 1 barra (all'apertura delle 00:00 UTC). Regole complete in `candidati/<ID>/regole.md`.

| | ETCUSDT-033 (R1) | ETCUSDT-036 (R4) | ETCUSDT-037 (R5) |
|---|---|---|---|
| Condizione | giornata < −5% | giornata < −3% e stop ≥ 2,5% del prezzo | giornata < −5% e stop ≥ 2,5% |
| Trade (costruzione) | 124 | 137 | 101 |
| R medio dopo i costi | +0,018 | +0,004 | +0,027 |
| Profit factor | 1,15 | 1,02 | 1,23 |
| `t` contro la (a) / la (b) | 3,60 / 3,62 | 3,23 / 3,14 | 3,53 / 3,51 |
| Percentile fra le entrate casuali | 100 | 99,5 | 100 |
| R per anno (2020 / 2021 / 2022) | +0,047 / +0,020 / −0,003 | +0,038 / +0,010 / −0,026 | +0,083 / +0,026 / −0,007 |
| R senza i 3 migliori | −0,005 | −0,022 | −0,001 |
| **Costi doppi: R medio** | **−0,043** (non superata) | **−0,052** (non superata) | **−0,026** (non superata) |
| **Ritardo di una barra: `t` contro la (b)** | **−1,26** (non superata) | **−0,60** (non superata) | **−0,43** (non superata) |
| Robustezza ±20% | superata (7 casi su 8 contano, `t` > 0 in tutti, netti 6) | superata (9 su 10, netti 8) | superata (9 su 10, netti 8) |
| Timeframe adiacenti (15m, 1h) | superata (3,81; 3,96) | superata (2,63; 3,87) | superata (15m sotto i minimi: 57 trade; 1h 3,96) |
| Stabilità per anno, trade estremi | superate | superate | superate |
| Violazioni di liquidazione | 0 | 0 | 0 |
| Trade ridotti dal tetto di leva | 0 | 0 | 0 |
| Drawdown massimo (costruzione) | 2,4% | 2,9% | 2,5% |

Il crollo col ritardo è stato controllato come chiede la Fase 4 (nota ETCUSDT-N014): nessun errore di
lookahead trovato. La spiegazione inferita è che la regola è legata all'orologio: con una barra di ritardo
si entra alle 00:00, fuori dalla mezz'ora che l'idea descrive. Il candidato non passa comunque, per i costi
doppi.

Le tre soglie (−5%, −3%, 2,5%) sono state scelte sui quartili della Fase 3 dei dati di costruzione: sono la
parte più probabilmente fortunata. Il vantaggio contro il caso invece è di tutta la famiglia, compresa la
variante di partenza (023, R negativo, `t` 3,15).

## Tutte le varianti testate (costruzione)

| n | id | idea | tf | dir | trade | R medio | `t` (a) | `t` (b) |
|---|---|---|---|---|---|---|---|---|
| 1 | 001 | I-01 momento 7 giorni | 4h | long | 128 | +0,421 | +0,75 | +0,38 |
| 2 | 002 | I-01 | 4h | short | 115 | +0,268 | +2,15 | +1,75 |
| 3 | 005 | I-04 giornata anomala | 1d | long | 105 | +0,087 | +0,74 | +0,78 |
| 4 | 006 | I-04 | 1d | short | 101 | −0,112 | −1,15 | −1,13 |
| 5 | 009 | I-06 volume alto | 4h | long | 73 | +0,462 | +0,97 | +0,50 |
| 6 | 010 | I-06 volume basso | 4h | short | 72 | +0,018 | +0,90 | +0,11 |
| 7 | 011 | I-08 lunedì | 1d | long | 129 | −0,021 | −0,41 | −0,43 |
| 8 | 014 | I-11 RSI a 2 | 4h | long | 107 | −0,020 | +0,11 | −0,11 |
| 9 | 015 | I-11 | 4h | short | 118 | −0,054 | −0,58 | −0,29 |
| 10 | 016 | I-03 inversione dopo shock | 1h | long | 174 | −0,002 | +0,45 | +0,68 |
| 11 | 017 | I-03 | 1h | short | 213 | −0,182 | −1,66 | −1,91 |
| 12 | 018 | I-07 squilibrio ordini | 1h | long | 883 | −0,093 | −1,14 | −1,26 |
| 13 | 019 | I-07 | 1h | short | 901 | −0,073 | −0,32 | −0,29 |
| 14 | 020 | I-09 BTC guida | 1h | long | 122 | −0,037 | +0,39 | +0,41 |
| 15 | 022 | I-12 fine giornata | 30m | long | 478 | −0,096 | −0,50 | −0,27 |
| 16 | 023 | I-12 | 30m | short | 436 | −0,037 | +3,16 | +3,15 |
| 17 | 024 | I-13 incrocio medie | 4h | long | 101 | +0,430 | +1,66 | +0,85 |
| 18 | 025 | I-13 | 4h | short | 98 | +0,157 | +1,68 | +1,57 |
| 19 | 026 | I-14 numeri tondi | 1h | long | 549 | −0,054 | +0,18 | +0,19 |
| 20 | 027 | I-14 | 1h | short | 552 | −0,060 | +0,02 | +0,17 |
| 21 | 028 | I-15 illiquidità | 4h | long | 90 | +0,053 | −0,20 | −1,07 |
| 22 | 029 | I-16 rottura dell'apertura | 1h | long | 494 | +0,008 | +0,80 | +0,85 |
| 23 | 030 | I-16 | 1h | short | 498 | −0,020 | +0,76 | +0,70 |
| 24 | 033 | R1 di 023 | 30m | short | 124 | +0,018 | +3,60 | +3,62 |
| 25 | 034 | R2 di 023 (uscita 2 barre) | 30m | short | 436 | −0,015 | +1,94 | +1,94 |
| 26 | 035 | R3 di 023 (giornata < −3%) | 30m | short | 215 | −0,009 | +3,60 | +3,85 |
| 27 | 036 | R4 di 035 | 30m | short | 137 | +0,004 | +3,23 | +3,14 |
| 28 | 037 | R5 di 035 | 30m | short | 101 | +0,027 | +3,53 | +3,51 |
| 29 | 038 | R6 di 002 (stop 3 ATR) | 4h | short | 106 | +0,125 | +1,75 | +1,06 |
| 30 | 039 | R7 di 002 (filtro barra in calo) | 4h | short | 118 | +0,230 | +1,96 | +1,49 |

Scarti (sotto 70 trade, nessun budget): I-02 long 43 e short 40; I-05 short 67 e long 59; I-09 short 59;
I-10 long 15 e short 17; I-17 long 48 e short 47.

## Varianti, famiglie, validazione

* Varianti sul budget: **30 su 30**, di cui **7 ritocchi** (5 nella famiglia ETCUSDT-023, 2 nella famiglia
  ETCUSDT-002); **23 famiglie**; 9 scarti. Ordine dei ritocchi controllato meccanicamente
  (`codice/riepilogo.py`, nota ETCUSDT-N016): ogni ritocco ha preso il primo della lista.
* Validazione: **non eseguita**, perché nessun candidato è sopravvissuto alla Fase 4. p-value: nessuno.
  Asticella (Benjamini-Hochberg al 10%): m = 0, esito provvisorio «nessun candidato», da confermare al
  Passo 4.
* `criterio_vault`, trade al mese in paper, previsione per vault e trasferimento: non si applicano (nessun
  candidato).

## Rischi e limiti noti

* **Costi.** La fascia di slippage (0,05% per lato, dal volume del 2023) è ottimista per il 2020, quando il
  volume medio era 39,9 milioni di USDT al giorno (fascia 0,10%). Le idee a breve orizzonte su ETC vivono o
  muoiono sui costi: con ordini limit in ingresso (come il percorso live del bot) i costi reali
  sarebbero più bassi, ma il protocollo conta tutto come taker.
* **Esecuzione nel bot.** Il bot vivo ha candele 1m, 5m, 15m, 1h: un'idea a 30m richiederebbe l'aggiunta
  decisa al Passo 0. Le varianti del momento a 7 giorni (I-01) hanno stop oltre il 6% (tetto del bot) in circa
  tre trade su quattro: non eseguibili così come sono.
* **Dati.** Il mark price manca per tutto il 2022-10-02 (costruzione) e il 2023-02-24 (validazione): barre
  tolte dall'allineamento. I primi 15 giorni di gennaio 2020 non hanno dati. Mesi esclusi per liquidità:
  2020-06, 2020-09, 2020-10.
* **Potenza.** Con 70-130 trade un vantaggio di qualche centesimo di R non si distingue dal rumore: un
  «nessuna strategia» qui non vuol dire che ETC sia efficiente, vuol dire che con questi costi e questi
  trade non si vede nulla di netto e positivo.
* **Stesso modello, mercato comune** (sezione 11): l'effetto di fine giornata è anche su BTC.

## Misure di processo

Dal log (`codice/misure.py`; date dall'orologio della macchina).

* Durata dalla prima all'ultima voce del log: **61 minuti** (19:24:56 → 20:25:42 UTC), senza pause
  registrate (nessuna attesa di risposte dell'utente; una sola sessione). Le voci successive (questa
  consegna) la allungano di pochi minuti.
* Minuti per idea, dalla registrazione della prima variante all'ultimo risultato, e spiegazioni concorrenti
  scritte in `ipotesi.md`:

| Idea | Minuti | Varianti testate | Scarti | Spiegazioni concorrenti |
|---|---|---|---|---|
| I-01 momento 7 giorni | 12,8 | 4 (2 ritocchi) | 0 | 11 |
| I-02 rottura del canale | 0,0 | 0 | 2 | 11 |
| I-03 inversione dopo shock | 0,6 | 2 | 0 | 11 |
| I-04 giornata anomala | 0,0 | 2 | 0 | 10 |
| I-05 funding affollato | 0,0 | 0 | 2 | 10 |
| I-06 volume alto | 0,1 | 2 | 0 | 10 |
| I-07 squilibrio ordini | 0,8 | 2 | 0 | 10 |
| I-08 lunedì | 0,0 | 1 | 0 | 10 |
| I-09 BTC guida | 0,3 | 1 | 1 | 10 |
| I-10 Bollinger | 0,0 | 0 | 2 | 10 |
| I-11 RSI a 2 | 0,1 | 2 | 0 | 10 |
| I-12 fine giornata | 8,4 | 7 (5 ritocchi) | 0 | 10 |
| I-13 incrocio medie | 0,1 | 2 | 0 | 10 |
| I-14 numeri tondi | 0,6 | 2 | 0 | 10 |
| I-15 illiquidità | 0,1 | 1 | 0 | 10 |
| I-16 rottura dell'apertura | 0,6 | 2 | 0 | 10 |
| I-17 coppia con BTC | 0,0 | 0 | 2 | 10 |

  I minuti per idea sono piccoli perché le varianti di più idee sono state lanciate in lotti già
  registrati in `ipotesi.md`: il tempo di lavoro sta nella scrittura delle ipotesi, del codice e nelle
  Fasi 3-5, non fra registrazione e risultato.
* Varianti diventate candidati in Fase 2: **0 da idee nuove, 3 da ritocchi** (ETCUSDT-033, 036, 037).
* Varianti che hanno battuto nettamente la (a) e la (b) con R medio dopo i costi non positivo: **2**
  (ETCUSDT-023, R −0,037; ETCUSDT-035, R −0,009).

## Il bot

Per quanto trovato al Passo 0 (`config/regole_dimensione.md`): non c'è nulla da portare al bot da questa
campagna.
