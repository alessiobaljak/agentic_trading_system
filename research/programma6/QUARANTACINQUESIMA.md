# Programma 6 — quarantacinquesima prova: gli indicatori per decidere quando entrare (I1, I2)

Scritto il 21 ottobre 2026, sera, **prima del calcolo**, dopo la domanda del proprietario: «perché non provi ad usare
diversi indicatori per capire quando entrare?».

## 1. Perché

Gli indicatori da soli non battono i costi (prove 1, 2B, 3, 34-39). Ma qui l'indicatore non sceglie **che cosa** comprare
o vendere (lo sceglie la strategia che funziona), decide solo **quando** entrare: è il modo in cui i trader usano la
tendenza con un segnale lento (nei cambi e nelle materie prime, il «carry» con il filtro della tendenza).

* **I1 — F5 con la tendenza d'accordo.** In F5 le perdite vengono soprattutto dal lato short (da solo Sharpe 0,19,
  `robustezza_F5.json`): monete dove i long pagano molto e che continuano a salire, perché i long hanno ragione. Si entra
  short solo se il prezzo è già in discesa, long solo se è già in salita.
* **I2 — N3 con l'entrata sulla prima rottura verso il basso.** N3 vende le monete nuove a 7 giorni d'età; perde nelle
  ondate di euforia, quando le monete nuove continuano a salire (prova 33). Si aspetta il primo segno che l'entusiasmo è
  finito: la prima chiusura sotto il minimo dei 5 giorni prima. **Riserva**: gli eventi di N3 sono già stati guardati
  (prove 32 e 33); se passa, va confermata in avanti.

## 2. Le regole (valori fissati qui)

* **I1**: F5 come nella prova 24 (segnale −funding dei 7 giorni, entrata nel 20%, uscita oltre il 40%, pesi secondo la
  volatilità, costi e funding come F5), con una condizione in più **solo per le entrate nuove**: una moneta entra long solo se
  la chiusura della domenica è **sopra la sua media dei 20 giorni**, entra short solo se è **sotto**. Le posizioni già aperte
  restano con la regola della banda di F5. Dal 4 gennaio 2021, come F5.
* **I2**: le monete nuove dei perpetui di Binance della prova 32 (prima candela dal 1 gennaio 2021 al 10 settembre 2026).
  Dal 7° al 37° giorno d'età, alla **prima chiusura giornaliera sotto il minimo dei 5 giorni prima**: short la moneta e long il
  Bitcoin all'apertura del giorno dopo (`trentesima.operazione`), uscita a +30% o dopo 30 giorni, costi come N3. Senza
  rottura entro il 37° giorno, nessuna operazione.
* Due prove: I1 (portafoglio) e I2 (la **decima** prova a eventi, più il suo portafoglio); nel conto del programma 6
  diventano **70**.

## 3. L'esame

* **I1**: `terza.esame` e `terza.esito`, Sharpe corretto sulle **70** prove; si riporta F5 sulle stesse settimane.
* **I2**: per evento media netta sopra zero con **p ≤ 0,001** (0,01 diviso le 10 prove a eventi), due metà, senza i 5
  migliori; come portafoglio (5% a operazione, al massimo 20) `terza.esame` e `terza.esito` sulle **70** prove; si
  riporta N3 (prova 32) per confronto, quante monete non hanno la rottura, i giorni d'attesa.
* VALIDA solo se passa tutto; I2 con la riserva va comunque confermata in avanti.
