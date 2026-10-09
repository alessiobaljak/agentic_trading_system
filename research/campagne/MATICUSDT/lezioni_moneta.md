# MATICUSDT — lezioni della moneta (idee provate, risultati)

Costruzione dal 2020-10-01 al 2023-01-08 (ingressi possibili dal 2021-02-01, filtro di liquidità);
numeri dal log (`log.jsonl`), voci `risultato`. «t» è il `t` contro la baseline (b) (entrate
casuali con la stessa uscita e la stessa direzione); «netta» vuol dire sopra la soglia (circa 2,05).

| Idea | Varianti testate | Esito in costruzione |
|---|---|---|
| I-01 momento settimanale (4h) | long, short | Long: R 0,43 ma senza i 3 migliori −0,05, t 0,73. Short: R −0,33, t −1,89. Il rialzo del 2021 fa tutto. |
| I-02 rottura di canale | — | Sotto i 70 trade anche con il canale di 5 giorni. |
| I-03 rendimento giornaliero anomalo (1h) | long, short | Long: R 0,17, t 1,51 (vicino, non netto), positivo in entrambi gli anni. Short: t 0,51. |
| I-04 prima mezz'ora → ultima (30m) | long, short | R −0,06 / −0,05 come il caso: solo costi. |
| I-05 RSI(2) nella tendenza (4h) | long, short (soglie 10/90) | t 0,60 / −0,83. |
| I-06 lunedì (1d) | long | R −0,05, t −0,59. |
| I-07 funding (8h) | short su funding ≥ 0,05%, long su funding ≤ −0,01% | Short: R −0,28, t −2,27 (dopo funding molto alto il prezzo continua a salire). Long: t −0,24. |
| I-08 volume alto (1d) | long (1,5×; ritocchi 1,3× / 1,4× / tenuta 3 giorni; tenuta 10 sotto i trade minimi) | R fra 0,48 e 1,02, t fra 1,49 e 1,94, mai netto; senza i 3 migliori molto meno; febbraio-maggio 2021 fa gran parte del risultato; la (a) che entra ogni giorno fa già 0,45. |
| I-09 ritorno dopo salti orari (1h) | long dopo −3σ, short dopo +3σ | t −1,62 / −2,70: nelle 6 ore dopo un salto prevale la continuazione. |
| I-10 massimo di 52 settimane | — | 2 trade: il riscaldamento di un anno lascia troppo poco. |
| I-11 media di 50 giorni (1h) | long, short | t −0,80 / −0,35. |
| I-12 compressione di Bollinger | — | Sotto i 70 trade. |
| I-13 squilibrio taker (1h) | long, short + 5 ritocchi dello short | Long: t −0,07. Short: t 2,08 (netto contro la (b), non contro la (a): 1,86). Con BTCUSDT non in rialzo e tenuta 12 ore (MATICUSDT-025) diventa candidato: R 0,149, t (b) 2,12, t (a) 2,41. **Bocciato in Fase 4**: col ritardo di un'ora t 0,53 (R −0,003), a costi doppi t 2,03 sotto la soglia. Nessun errore di lookahead nel codice. |
| I-14 forza relativa contro BTC (4h) | long, short | t 0,67 / −1,41. Come I-01. |
| I-15 illiquidità (4h) | long, short | t 0,09 / −1,47. |

Cosa si è capito (osservato, in costruzione):
* Su MATICUSDT 2021-2022 le uscite lunghe (una settimana, 5 giorni) danno R medi alti trainati da
  pochi trade nel grande rialzo del 2021: senza i 3 migliori quasi sempre sotto o vicino a zero, e
  la (a) e la (b) fanno lo stesso. Il trend di fondo spiega le strategie lente.
* Dopo i movimenti forti (salti orari, funding molto alto, giorni anomali al rialzo) il prezzo tende
  a continuare nelle ore dopo, non a tornare indietro. Nessuna di queste continuazioni è stata
  provata come idea: sarebbero idee nate dal risultato, senza fonte scritta prima.
* Lo squilibrio di vendite aggressive anticipa un debole ribasso nelle ore dopo, ma l'effetto non
  regge un'ora di ritardo né i costi doppi: troppo fragile per un bot che entra con latenza.
