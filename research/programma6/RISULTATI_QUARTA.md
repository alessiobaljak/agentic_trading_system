# Programma 6 — risultati della quarta prova (il rimbalzo dopo i crolli, monete mai usate)

Regole in `QUARTA.md` (scritte prima). La regola congelata I-017c4 del programma 5: long all'apertura dell'ora dopo un crollo di 4 ore con z ≤ −5, uscita dopo 12 ore, pausa 12; costi 0,40% andata e ritorno.

* **Trade**: 3765 su 440 monete, dal 2021-01-01.
* **Netto medio a trade**: +1.771% (intervallo +0.360; +3.110, p 0.0070); lordo +2.065%, funding -0.106%.
* **Il caso**: -0.522% a trade; differenza +2.294% (intervallo +0.885; +3.640).
* **A costi doppi**: +1.371%. **Senza il giorno migliore**: +1.373%.
* **Monete con almeno 5 trade**: 164 positive su 217.
* **Crolli propri** (Bitcoin non in crollo): 1326 trade, -2.008% (intervallo -3.478; -0.673).
* **Ultimo anno** (dal 2025-10-01): 434 trade, -0.349%.
* **Capitale** (10% a trade, per informazione): +115.1% l'anno, Sharpe 0.95, discesa massima -63.7%.

| Anno | Trade | Netto a trade |
|---|---|---|
| 2021 | 435 | +4.719% |
| 2022 | 677 | +0.194% |
| 2023 | 619 | +0.462% |
| 2024 | 1116 | +3.697% |
| 2025 | 670 | -0.176% |
| 2026 | 248 | +0.772% |

**Esito: non positiva nell'ultimo anno**

## Diagnosi dopo l'esame (non cambia l'esito)

* LENDUSDT è nell'universo ma l'archivio non ha le sue candele a 1 ora: resta fuori (536 monete con i dati, 440 con
  almeno un trade).
* I trade con il **mercato in crollo** (z4 del Bitcoin ≤ −3) sono 2.439 ma cadono in **84 giorni** soltanto; i 5 giorni
  migliori (2024-04-13, 2024-03-05, 2022-05-12, 2024-04-12, 2021-05-19) fanno il **56%** del guadagno di quei trade. Il
  crollo più grande dell'ultimo anno, il **10 ottobre 2025**, va al contrario: 96 trade, −4,08% in media.
* I **crolli propri** (il Bitcoin non crolla) perdono: −2,0% a trade su 1.326 trade, intervallo tutto sotto zero. Una
  moneta che crolla da sola di solito continua a scendere.
* Cosa vuol dire: il rimbalzo non è della moneta ma del **mercato** dopo i crolli di tutti, e si regge su pochi giorni,
  tutti già visti dal programma 5 sulle sue 12 monete. Non c'è un altro passato pulito per provarlo: solo il futuro.
