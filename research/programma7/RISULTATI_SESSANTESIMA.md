# Programma 7 — risultati della sessantesima prova (RRE: l'inclinazione delle opzioni al contrario, sull'Ether)

Regole in `SESSANTESIMA.md` (scritte prima). Operazioni di Deribit sulle opzioni dell'Ether fra le 16 e le 24 UTC, dal 1° aprile 2021.

* Giorni con l'inclinazione: 1959 su 2034; cambi di verso 78 l'anno.
* **RRE (short sopra la mediana dei 90 giorni, long sotto): Sharpe -1.37**, -85.9% l'anno, volatilità 62.7%, discesa -99.7%; spese 9.3% l'anno.
* Per anno: 2021 -195.1%, 2022 -48.1%, 2023 -30.7%, 2024 -158.9%, 2025 -89.9%, 2026 -33.9%.
* Solo short (fuori sotto la mediana): Sharpe -1.15, -51.8% l'anno.
* Correlazione fra il segnale e l'Ether del giorno dopo 0.020 (sul Bitcoin, prova 121: −0,117).
* Sharpe corretto con l'aggiunta 0.00 (81 gruppi); t -3.17; regola del proprietario: no.

**Esito: netto con l'intervallo non sopra zero**

## Cosa abbiamo capito (controllo delle 00:55 UTC, prima di registrare)

* **Il conto è giusto.**
  * Le posizioni sono metà short e metà long (49,6% short) e il segnale c'è in 1.959 giorni su 2.034.
  * L'inclinazione ha valori normali: dal −25,6 al +9,9 fra l'1% e il 99%, nessuno assurdo.
  * L'Ether si muove del 3,7% al giorno.
  * Le posizioni vanno **contro** il rendimento del giorno dopo: correlazione −0,059, che con quella volatilità vale −0,22% al giorno
    prima dei costi.
* **Sull'Ether il verso giusto è quello della letteratura, non quello preso dal Bitcoin.** Quando le opzioni da salita dell'Ether sono più
  care del solito, l'Ether il giorno dopo tende a salire, non a scendere. È il contrario della prova 121, dove però la misura era
  stretta e copriva solo 773 giorni.
* **Esito: no**, e molto netto (Sharpe −1,37, t −3,17). Il verso opposto non si sceglie adesso sull'Ether: l'abbiamo visto.
* **La prova pulita che resta** è il verso della letteratura (Neo 2026: le opzioni da salita care precedono la salita) sul Bitcoin, con
  la stessa misura larga di questa prova, che sul Bitcoin non è mai stata calcolata. È la prova 123, scritta prima del calcolo. Da
  dichiarare: nasce dopo aver visto che sull'Ether questo verso va bene.
