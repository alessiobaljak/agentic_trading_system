# Prova 26 — risultati

Calcolato da `python -m stock.prove.p026` il 2026-11-12 06:29 UTC con le regole di `P026_tendenza_altre_classi.md` (committate prima). Giorni in comune con la miscela della prova 25: dal 2016-11-01 al 2024-12-31 (2054). Nel conto dell'asticella: 54 serie. Giorni di borsa senza il prezzo di Yahoo: {'TLT': 0, 'IEF': 0, 'GLD': 0, 'DBC': 0, 'EFA': 0, 'EEM': 0}. Ordini eseguiti dalla parte nuova: 354; costi pagati 908 dollari; decisioni 107, fondi dentro in media 3.3 su 6.

| | Parte nuova (tendenza sulle altre classi) | Miscela della prova 25 | Miscela nuova (3/4 + 1/4) | Tenere lo SPY |
|---|---|---|---|---|
| Guadagno totale | +16.3% | +139.4% | +101.3% | +219.0% |
| Sharpe annuo con i costi | 0.34 (costi doppi 0.33; senza costi 0.36) | 1.08 | **1.05** | 0.89 |
| Perdita massima dal picco | -10.2% | -14.6% | -12.3% | -33.8% |
| Anno per anno | 2016: -4.2% 2017: +10.7% 2018: -6.1% 2019: +6.3% 2020: +3.5% 2021: +2.7% 2022: +0.2% 2023: +0.8% 2024: +2.4% | 2016: +2.5% 2017: +20.0% 2018: +0.8% 2019: +16.4% 2020: +13.7% 2021: +16.4% 2022: -12.4% 2023: +22.2% 2024: +17.1% | 2016: +0.8% 2017: +17.7% 2018: -0.9% 2019: +13.9% 2020: +11.2% 2021: +12.9% 2022: -9.3% 2023: +16.5% 2024: +13.3% | — |

* **1.** Sharpe della parte sopra zero, anche con i costi doppi: 0.34 e 0.33 → sì.
* **2.** Correlazione con la miscela sotto 0,3: 0.41 → no.
* **3.** La miscela nuova ha lo Sharpe più alto della miscela (1.08) e del tenere lo SPY (0.89): 1.05 → no.
* Da leggere: Sharpe corretto della miscela nuova 0.05 (gruppi 17, t 3.00).
* Da leggere, ogni fondo da solo con la regola (senza costi, conto semplice): TLT -0.04 (tenerlo -0.08), IEF 0.05 (tenerlo 0.02), GLD 0.33 (tenerlo 0.68), DBC 0.39 (tenerlo 0.43), EFA 0.07 (tenerlo 0.45), EEM 0.38 (tenerlo 0.29).

**Esito: non entra nella miscela: bocciata**
