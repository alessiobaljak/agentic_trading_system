# Risultati prova 152 (NOVANTESIMA): il limite alla concentrazione di G1

### Riepilogo
Eseguite una sola volta le tre varianti, come scritto (regole: commit d75e3c6, sezione «Seconda correzione»). Esito secondo l'esame scritto:
**nessuna variante passa**. V2 non passa il limite sul peso (per costruzione). V1 e V3 passano tutte le voci del conto 1 e le voci sull'anno
positivo e sullo Sharpe del conto 2, ma **falliscono una sola voce del conto 2: gli ordini saltati per i minimi sono più numerosi di G1**
(V1 +8 su 122.958 nel conto A; V3 +117 nel conto A; V1 +15 e V3 +120 nel conto A2). Il margine è piccolo, la regola è scritta alla lettera e
non si cambia. Passare il criterio di rischio non è passare l'asticella dello Sharpe corretto: giudica backtest-auditor.

### La prova come è scritta e scala di tempo
`research/programma7/NOVANTESIMA.md`. Periodo 2021-01-04 .. 2026-10-04 (2.100 giorni di G1, `an.INIZIO`..`an.FINE`, fine esclusa), universo
per settimana, lati fissi a 1 e 1. Sharpe, t, discesa: serie settimanali (52). Prima del calcolo, riproduzione del 65 di G1.

**Prima fermata (nota)**: con la prima definizione dei giorni-moneta (costo realizzato delle sole vendute) G1 dava **9**, non 65: la prova
si è fermata (nessuna variante calcolata). La definizione è stata corretta nelle regole (escursione peggiore della giornata, comprate e
vendute). Con la definizione corretta G1 dà **65**, il controllo torna (`risultati_novantesima/controllo65.json`).

### Implementazione
`research/programma7/novantesima.py`. G1 del mio ciclo identico a `nucleo.pesi(fisso=(1,1))` (controllo con `array_equal`). Conto 1:
`analisi.conto` (spese a limite come la revisione). Conto 2: `ottantaseiesima.conto_vero` a 280 USDT, conti A e A2. Non committato.

### Varianti provate
3 (V1, V2, V3), una volta ciascuna. Registro: `research/trials/novantesima.csv` (3 righe). Conto delle prove 309 -> 312, una famiglia.

### Risultati (conto 1; G1 = ricalcolo con lo stesso codice)
| | G1 | V1 | V2 | V3 |
|---|---|---|---|---|
| Sharpe | 1,98 | 1,95 (-0,03) | 1,89 (-0,10) | 1,94 (-0,05) |
| Rendimento annuo | +54,4% | +53,5% | +51,7% | +53,7% |
| Discesa settimanale | -28,8% | -31,3% (-2,6 punti) | -29,7% (-0,9) | -30,2% (-1,5) |
| t | 4,76 | 4,68 | 4,53 | 4,65 |
| Sortino | 3,87 | 3,79 | 3,51 | 3,75 |
| Spese annue | 6,4% | 6,4% | 6,5% | 6,2% |
| Peso max venduta (voluto) | 43,7% | 20,0% | 26,6% | 20,0% |
| Peso max venduta con la deriva dei prezzi | 43,8% | 27,1% | 27,5% | 21,3% |
| Peso max comprata (voluto) | 29,3% | 20,0% | 29,3% | 20,0% |
| Giorni-moneta oltre il 3% (misura della revisione) | 65 | 64 | 55 | 50 |
| Giorni con n sotto 10 (lunghi / corti) | 58 / 67 | 58 / 67 | 0 / 0 (completati: 125 lati-giorno, tutti completati) | 58 / 67 |
| Anni 2021-2026 tutti positivi | sì | sì | sì | sì |

Conto 2 (280 USDT, minimi di Binance): Sharpe A / A2, discesa A, ordini saltati A / A2
G1: 1,90 / 1,83, -26,8%, 122.958 / 96.587. V1: 1,87 / 1,80, -29,1%, 122.966 / 96.602. V2: 1,79 / 1,72, -27,9%, 122.355 / 96.824.
V3: 1,86 / 1,80, -27,7%, 123.075 / 96.707. Tutti gli anni positivi in A e A2 per tutte le varianti; Sharpe in calo di al massimo 0,15 per tutte.

Esame scritto: V1 non passa (solo: ordini saltati più di G1, A e A2). V2 non passa (peso 26,6% oltre il 20%; ordini saltati A2 più di G1). V3 non
passa (solo: ordini saltati più di G1, A e A2). Dettaglio per voce in `risultati_novantesima/risultati.json`.

Sharpe corretto (famiglie, asticella dell'11 novembre, 56 famiglie; le tre varianti cadono nello stesso gruppo di F5, F5+M7, K2 e altri):
V1 0,88 (con aggiunta 0,94), V2 0,84 (0,91), V3 0,87 (0,93). Per prova (N = 312): V1 0,62, V2 0,56, V3 0,61.

### Variante migliore e sensibilità
Per il criterio di rischio nessuna passa. V3 è la più vicina nel rischio (peso 20% anche con la deriva 21,3%, giorni oltre 3%: 50, Sharpe -0,05),
V1 perde meno Sharpe (-0,03) ma la discesa peggiora di più (-2,6 punti, entro i 3) e con la deriva una venduta arriva al 27,1%. Il 20% è
scritto e non si è cercato altro.

### Anomalie e possibili errori
Nessun errore di motore o dati. V2 nel conto a 280 USDT: 15 giorni con pesi diversi perché una moneta aggiunta non ha i filtri di Binance e non
si aggiunge (regola). Nessun giorno con rango insufficiente o universo sotto 20. Gli ordini saltati sono dominati da monete con valore sotto il
minimo; la differenza fra varianti e G1 è di 8-237 ordini su ~100.000.

### Varianti non previste che proporrei (non eseguite)
Nessuna.

### Domande aperte
1. Il criterio «ordini saltati non più numerosi di G1» è sensibile a differenze di poche unità (V1: +8): è voluto che bocci una variante che sul
resto è dentro i limiti? (Decide Alessio o la sessione principale; non è stato toccato.)
2. Il peso massimo con la deriva dei prezzi (V1 27,1%) supera il 20% pur con il tetto sul peso voluto: va richiesto un controllo anche sulla deriva?

### Letture che ho dovuto scegliere
- Peso max con deriva: calcolato senza le spese (solo prezzi e funding), riportato a parte.
- Pari merito di V2: ordine di candidati per segnale (a 12 decimali) poi volume medio dei 30 giorni prima (`quote_volume`, nanmean di i-30..i-1),
  poi simbolo; le monete dell'altro lato non si aggiungono mai; l'insieme già scelto (anche con la media nei pari merito) non cambia.
- V3 senza lato (n=0): resta vuoto. Il tetto in V3 si applica con n>=5 sul lato già ridotto.
- Conto 2 per V3 e V1: gli stessi pesi del conto 1; per V2 senza le monete prive di filtri.
- Giorni-moneta oltre il 3%: pesi voluti, escursione dalla candela giornaliera del pannello (massimo/minimo su apertura).
- «Ordini saltati» confrontati con G1 sullo stesso conto (A con A, A2 con A2), senza margine.
