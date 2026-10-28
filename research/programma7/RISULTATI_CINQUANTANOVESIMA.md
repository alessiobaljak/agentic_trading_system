# Programma 7 — risultati della cinquantanovesima prova (RR: l'inclinazione delle opzioni sul Bitcoin, ogni giorno)

Regole in `CINQUANTANOVESIMA.md` (scritte prima). Operazioni di Deribit fra le 22 e le 24 UTC, dal 1° aprile 2021.

* Giorni con l'inclinazione: 773 su 2034; cambi di verso 16 l'anno.
* **RR (long sopra la mediana dei 90 giorni, short sotto): Sharpe -0.34**, -10.6% l'anno, volatilità 31.2%, discesa -61.6%; spese 1.9% l'anno.
* Per anno: 2021 +0.0%, 2022 +0.0%, 2023 +3.5%, 2024 -14.6%, 2025 -32.2%, 2026 -15.9%.
* Solo long (fuori sotto la mediana): Sharpe 0.11, +1.8% l'anno, discesa -30.7%.
* Correlazione fra il segnale e il Bitcoin del giorno dopo -0.117, della settimana dopo -0.036.
* Sharpe corretto con l'aggiunta 0.00 (81 gruppi); t -0.78; regola del proprietario: no.

**Esito: netto con l'intervallo non sopra zero**

## Cosa abbiamo capito

* **I dati sono completi, la misura è stretta.** Ogni giorno ci sono fra 383 (2021) e 921 (2025) operazioni nelle due ore. Quelle con la
  scadenza a 20-45 giorni e il delta giusto bastano solo in 773 giorni su 2.034. Nel 2021 e nel 2022 non si arriva mai ai 45 giorni
  validi per la mediana, e la strategia resta ferma (0%). È la regola scritta prima, non un errore.
* **Il segnale va al contrario di quanto previsto.** Quando le opzioni da salita costano più del solito, il Bitcoin del giorno dopo
  tende a scendere: la correlazione è −0,117 sul giorno dopo e −0,036 sulla settimana dopo. Così la regola long/short perde (Sharpe
  −0,34; 2024 −14,6%, 2025 −32,2%) e quella solo long fa quasi zero (0,11).
* **La lettura** che si adatta alla nostra famiglia («chi paga la leva o la novità perde»): chi compra opzioni da salita care è
  l'entusiasmo dei piccoli, non chi sa qualcosa, e paga troppo, come chi paga il funding alto.
* **Esito: no.** Il verso opposto non si sceglie adesso, dopo averlo visto. Si scrive come idea nuova (94) da provare su dati diversi:
  l'Ether, con una misura più larga (tutte le operazioni del giorno).
