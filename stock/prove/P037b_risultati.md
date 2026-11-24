# Prova 37b — risultati (esame da crisi sul periodo chiuso)

Calcolato da `python -m stock.prove.p037b` il 2026-11-24 10:34 UTC con le regole di `P037b_esame_da_crisi.md` (committate prima). Dal 2025-01-02 al 2026-09-30, 437 giorni; prezzi di Yahoo.

**Il mese della crisi** (deviazione standard dello SPY più alta): **2025-04**, SPY -0.87% nel mese.

| Condizione | Valore | Passa |
|---|---|---|
| **1.** Paga nella crisi (rendimento con i costi nel mese della crisi > 0) | +2.16% | sì |
| **2.** Paga più di quanto costa (periodo in guadagno con i costi e con i costi doppi) | -4.48% / -7.77% | no |
| **3.** Serve accanto allo SPY (correlazione < 0,3; 3/4 SPY + 1/4 parte con Sharpe più alto) | correlazione +0.03; Sharpe 0.98 contro 1.04 | no |
| **Esito** | | **non passa: la prova 37 è bocciata definitivamente** |

Con i costi: Sharpe -0.45, perdita massima -6.2%; lo SPY: Sharpe 1.04, +32.7%. Dai 10 giorni migliori viene il nan% del guadagno (in logaritmi).

**Mese per mese (da leggere):**

| Mese | La regola, con i costi | Lo SPY | Deviazione standard giornaliera dello SPY |
|---|---|---|---|
| 2025-01 | +0.43% | +2.69% | 0.88% |
| 2025-02 | -0.52% | -1.27% | 0.83% |
| 2025-03 | -2.41% | -5.57% | 1.30% |
| 2025-04 | +2.16% | -0.87% | 3.32% |
| 2025-05 | -2.13% | +6.28% | 1.07% |
| 2025-06 | -1.11% | +5.14% | 0.63% |
| 2025-07 | +0.19% | +2.30% | 0.41% |
| 2025-08 | +2.48% | +2.05% | 0.75% |
| 2025-09 | -0.66% | +3.56% | 0.45% |
| 2025-10 | +0.18% | +2.38% | 0.86% |
| 2025-11 | +1.31% | +0.19% | 0.97% |
| 2025-12 | +0.36% | +0.08% | 0.55% |
| 2026-01 | -0.20% | +1.47% | 0.65% |
| 2026-02 | -0.16% | -0.86% | 0.84% |
| 2026-03 | +0.05% | -4.94% | 1.13% |
| 2026-04 | -1.42% | +10.51% | 0.74% |
| 2026-05 | -1.63% | +5.26% | 0.61% |
| 2026-06 | +1.39% | -1.03% | 1.13% |
| 2026-07 | -0.16% | +0.03% | 0.76% |
| 2026-08 | -2.36% | +2.68% | 0.65% |
| 2026-09 | -0.17% | -0.33% | 0.68% |

**Da leggere accanto (non cambiano l'esito):**

| Versione | Sharpe | Guadagno totale | Perdita massima |
|---|---|---|---|
| costi doppi | -0.81 | -7.8% | -8.8% |
| senza costi | -0.09 | -1.1% | -5.9% |
| un giorno di ritardo | -0.46 | -4.6% | -7.6% |
| con TLT | -0.59 | -6.6% | -10.4% |

Nel conto: 1 prova (115). Il periodo chiuso della famiglia «ribilanciamento» è usato.
