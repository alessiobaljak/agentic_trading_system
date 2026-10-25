# Prova 23 — risultati

Calcolato da `python -m stock.prove.p023` il 2026-10-25 19:38 UTC con le regole di `P023_giornata_sulle_azioni.md` (committate prima). 33 titoli, dal 2016-05-02 al 2024-12-31 (2182 giorni). Nel conto dell'asticella: 49 serie.

* Giorni esclusi per minuti mancanti (titolo-giorni dentro l'elenco): AVGO 19, BA 6, BAC 1, GOOG 12, GOOGL 368.
* Tenere lo SPY: Sharpe 0.87; tenere le 10 di allora a pesi uguali: Sharpe 0.94.

| | ultima mezz'ora | zona di rumore | prima candela 5 min | prima candela 15 min | inversione |
|---|---|---|---|---|---|
| Ordini eseguiti (con i costi) | 42662 | 38448 | 42034 | 42030 | 2700 |
| Guadagno medio di un posto nei giorni con operazioni, con i costi (t, giorni) | -0.057% (t -17.9, 21331) | -0.025% (t -2.4, 12455) | -0.023% (t -2.6, 21017) | -0.019% (t -2.0, 21015) | -0.041% (t -4.5, 1350) |
| Guadagno senza costi / con i costi / costi doppi | +20.6% / -70.4% / -98.2% | +119.1% / -28.6% / -90.6% | +111.8% / -40.6% / -94.1% | +132.6% / -35.8% / -94.3% | +1.0% / -5.4% / -11.5% |
| Sharpe annuo senza costi | 0.51 | 1.31 | 0.95 | 0.96 | 0.27 |
| **1.** Sharpe annuo con i costi (tenere lo SPY 0.87, le 10 0.94) | -3.20 | -0.52 | -0.58 | -0.43 | -1.47 |
| **2.** Sharpe corretto (soglia 0,95) | 0.00 (gruppi 15) | 0.00 (gruppi 15) | 0.00 (gruppi 15) | 0.00 (gruppi 15) | 0.00 (gruppi 15) |
| **3.** Sharpe con i costi doppi (> 0) | -10.65 | -3.87 | -3.54 | -3.22 | -3.10 |
| **4.** Trimestri in guadagno (60%) | 5 su 32 (16%) | 11 su 32 (34%) | 11 su 32 (34%) | 12 su 32 (38%) | 9 su 32 (28%) |
| Anni in guadagno (da leggere) | 1 su 9 | 2 su 9 | 1 su 9 | 3 su 9 | 0 su 9 |
| Titoli migliori; peggiori (somma dei rendimenti giornalieri / 10, da leggere) | V +0.5%, INTC +0.3%, PLTR +0.2%; peggiori: GOOGL -19.3%, AMZN -14.0%, NFLX -10.8% | AMD +10.6%, TSLA +8.1%, NVDA +4.9%; peggiori: BAC -8.5%, MSFT -7.1%, NFLX -5.5% | AMD +8.2%, NVDA +6.3%, TSLA +6.1%; peggiori: NFLX -16.8%, META -16.7%, AAPL -8.5% | NVDA +10.0%, TSLA +7.8%, AVGO +6.5%; peggiori: BA -10.5%, META -10.4%, BAC -9.4% | MU +0.1%, JNJ +0.1%, GE +0.1%; peggiori: AAPL -1.1%, AMZN -0.9%, META -0.8% |
| **Esito** | **bocciata** | **bocciata** | **bocciata** | **bocciata** | **bocciata** |
