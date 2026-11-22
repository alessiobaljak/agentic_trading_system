# Prova 45b — l'esame da crisi sul periodo chiuso

Calcolato UNA volta da `python -m stock.prove.p045b` il 2026-11-22 10:26 UTC con le regole di `P045b_esame_da_crisi.md` (committate prima). Dal 2025-01-02 al 2026-09-30.

* Giorni con la copertura del giorno prima sotto zero 18, sopra o uguale 419; esclusi dal controllo dei minuti 0; operazioni 18, saltate per la leva 0; per mese: 2025-03 3, 2025-04 6, 2026-03 8, 2026-06 1.
* Nei giorni sotto zero (la regola): 18 operazioni, **+14.44 punti base** a operazione (t 1.17), in guadagno 67%; nei giorni sopra o uguale a zero: 419 operazioni, **-1.61 punti base** a operazione (t -1.61), in guadagno 45%.
* Il mese migliore 2025-04 vale +230.9 punti base lordi; gli altri insieme +29.0. Aprile 2025 da solo: 6 operazioni, **+38.48 punti base** a operazione (t 1.15), in guadagno 67%.
* Guadagno senza costi / con i costi / costi doppi: +2.55% / +2.31% / +2.06%; Sharpe con i costi 0.80; perdita massima -0.8%. Correlazione giornaliera con lo SPY 0.22; tre quarti SPY e un quarto la parte: Sharpe 1.06 contro 1.04 del solo SPY.
* Da leggere: con la chiusura ufficiale di Yahoo nei giorni sotto zero 18 operazioni, +14.44 punti base (t 1.17).

| Condizione | Esito |
|---|---|

**Esito: non si può dire (meno di 20 operazioni).** Conta 1 prova nel registro (un'apertura del periodo chiuso).
