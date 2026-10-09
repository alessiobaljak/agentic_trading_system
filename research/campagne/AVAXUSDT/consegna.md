# Consegna — campagna AVAXUSDT (protocollo 4.5)

## Esito

**Nessuna strategia valida trovata per questa moneta.**

Ho usato tutte le 30 varianti del budget sui dati di costruzione (dal 2020-09-01 al 2022-12-30).
Cinque varianti sono diventate candidati in Fase 2. Nessuna ha superato le verifiche della Fase 4.
Per questo non c'è niente da validare: il periodo di validazione (dal 2022-12-31 al 2023-12-31)
non è stato usato e resta intatto. Non ci sono p-value di validazione né un esito dell'asticella
da far confermare al coordinamento.

## Riepilogo delle idee provate

14 idee in 12 famiglie di meccanismi, ognuna con una fonte pubblicata prima del 2024
(`ipotesi.md`).

| Idea | Varianti (t contro la (b) in costruzione) | Esito |
|---|---|---|
| I-01 Momento a 14 giorni, 1d | V-01 long (0,65), V-02 short (2,12, ma non batte la (a)) | nessun vantaggio |
| I-02 Rottura di Donchian, 4h | V-22 long (0,00), V-23 short (0,69); V-03/V-04 scarti | nessun vantaggio |
| I-03 RSI(2) di Connors, 4h | V-05 (−0,27), V-06 (0,87) | nessun vantaggio |
| I-04 Funding estremo, 8h | V-07 short (−0,15), V-08 long (−1,29) | nessun vantaggio |
| I-05 AVAX in ritardo su BTC, 1h | V-09 (0,94), V-10 (−0,96) | nessun vantaggio |
| I-06 Momento infragiornaliero, 30m | V-11 long (2,79, R −0,001), V-12 short (3,52, candidato); ritocchi R-01..R-05 | candidati scartati in Fase 4 (costi doppi) |
| I-07 Lunedì, 1d | V-13 (−0,63) | nessun vantaggio |
| I-08 Seguire le reazioni eccessive, 4h | V-14 long (2,68, candidato), V-15 short (−1,74) | candidato scartato in Fase 4 (ritardo) |
| I-09 Rottura di Williams/Crabel, 1h | V-16 (0,91), V-17 (1,72) | nessun vantaggio |
| I-10 Compressione di Bollinger | V-31 1h (−0,52), V-32 1h (0,50); quattro scarti a 4h | nessun vantaggio |
| I-11 Forza relativa contro BTC, 1d | V-20 (0,14) | nessun vantaggio |
| I-12 Volume alto, 4h | V-26 (0,96); V-21 scarto | nessun vantaggio |
| I-13 Inversione dopo salti orari, 1h | V-27 (−0,48), V-28 (−1,65) | nessun vantaggio |
| I-14 Squilibrio degli ordini, 4h | V-29 (0,38), V-30 (0,99) | nessun vantaggio |

## I candidati della Fase 2 e perché sono caduti

| Candidato | Costruzione | Fase 4 |
|---|---|---|
| **V-14**: 4h long, dopo una barra con z > 2 (rendimento diviso la deviazione standard delle 180 barre precedenti). Stop a 2 ATR(14), uscita dopo 6 barre | 113 trade, R medio 0,200, profit factor 1,79, drawdown 3,4%. Contro la (a): t 2,48. Contro la (b) (−0,017): t 2,68. Percentile 100. R per anno: 2020 0,04, 2021 0,25, 2022 0,14 | Robustezza superata (10 casi su 10 positivi, 7 netti). Timeframe adiacenti superati (2h t 1,92, 6h t 0,30). Costi doppi superati (R 0,176, t 2,69). Stabilità e trade estremi superati. **Ritardo non superato: t 1,327, serviva 1,342.** Errore di lookahead cercato e non trovato |
| **V-12**: 30m short alle 23:30 UTC, se il giorno è in calo; uscita dopo una barra | 376 trade, R 0,007, t contro la (b) 3,52 | Ritardo t 0,06. Costi doppi: R −0,052 |
| **R-01, R-02, R-03**: ritocchi di V-11 (30m long alle 23:30 se il giorno è in rialzo), con filtri presi dai fallimenti | R da 0,014 a 0,035, t contro la (b) circa 3 | Costi doppi: R da −0,051 a −0,024. R-02 e R-03 cadono anche sul ritardo |

Rischi noti. V-14 ha 98 trade su 113 con stop oltre il 6%: il bot non lo eseguirebbe così com'è.
Non ci sono trade ridotti per il tetto di leva né violazioni della liquidazione. La fascia di
slippage è ottimista per il 2020.

## Misure di processo

Fonte: il log, con l'orologio della macchina; nessuna pausa registrata.

* Durata dalla prima all'ultima voce del log: dalle 14:26:54 alle 15:08:37 UTC del 9 ottobre 2026,
  cioè 41,7 minuti, con e senza pause. Sono minuti di orologio. I test sono stati lanciati a
  gruppi, quindi i tempi per idea misurano soprattutto il calcolo.
* Minuti per idea, dalla prima registrazione all'ultimo risultato:
  * I-01, I-02, I-03, I-04, I-05, I-07, I-08, I-09, I-11, I-12: 3,1 ciascuna (gruppo unico);
  * I-10, I-13, I-14: 1,2 ciascuna;
  * I-06: 14,6 (7 varianti, compresi i 5 ritocchi).
* Spiegazioni concorrenti in `ipotesi.md`: 10 per ognuna delle 14 idee (per I-10 a 1 ora valgono
  le sue 10, più una nota sui costi).
* Varianti: 30. Ritocchi: 5. Famiglie: 25. Scarti sotto i trade minimi, senza consumare budget: 7.
* Candidati in Fase 2:
  * da idee nuove: 2 (V-12, V-14);
  * da ritocchi: 3 (R-01, R-02, R-03).
* Varianti che battono nettamente la (a) e la (b) con R medio dopo i costi non positivo: 1 (V-11).

## Cosa abbiamo capito (con la fonte di ogni numero nel log)

1. Dopo una barra di 4 ore in forte rialzo, AVAXUSDT ha continuato a salire nelle ore successive
   più del caso, anche con BTC calmo. L'effetto dura poche barre: se l'ingresso slitta di 4 ore
   ne perde circa metà (voci V14-F4 e N016).
2. I crolli forti non continuano allo stesso modo: dopo un crollo lo short perde più del caso
   (V-15, V-28). Questa asimmetria è osservata, non provata.
3. A 30 minuti il segno del giorno UTC predice la mezz'ora successiva, in entrambe le direzioni,
   per circa 0,065 R lordi a trade (N013). È però grande quanto i costi: non è sfruttabile.
4. Trend, funding, ritardo su BTC, lunedì, volume, squilibrio degli ordini e ritorno verso la
   media non hanno dato nulla oltre il trend di fondo, che la (b) cattura già.

## Previsione per il vault e il trasferimento

Nessun candidato va al vault da questa moneta.

L'informazione più utile da portare avanti è V-14: un effetto forte in costruzione, caduto per
una regola tarata per scoprire gli errori di lookahead. Lo scrivo in `lezioni_metodo_proposte.md`
(punto 1) perché il coordinamento valuti la regola fuori da questa campagna. Il candidato resta
scartato: non propongo di recuperarlo.
