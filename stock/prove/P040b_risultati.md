# Controllo dopo la prova 40 — le date di pagamento anno per anno

Calcolato da `python -m stock.prove.p040b` il 2026-11-18 10:41 UTC con il metodo di `P040b_anni_senza_date.md` (scritto prima di guardare i dati). **Non è una prova**: la prova 40 resta bocciata.

| Anno | Dividendi con la data di pagamento (per anno di pagamento) | Dividendi nell'archivio (per anno di stacco) | Anno con dati |
|---|---|---|---|
| 2016 | 0 | 1671 | **no** |
| 2017 | 0 | 1703 | **no** |
| 2018 | 0 | 1740 | **no** |
| 2019 | 66 | 1810 | **no** |
| 2020 | 1367 | 1745 | sì |
| 2021 | 1764 | 1762 | sì |
| 2022 | 1809 | 1813 | sì |
| 2023 | 1810 | 1814 | sì |
| 2024 | 1846 | 1735 | sì |

**Sugli anni con dati (da leggere):** dal 2020-12-31 (primo anno con dati 2020, più 252 giorni per la prima mediana): giorni dentro 520 su 1006 (52%); SPY nei giorni sopra la mediana +5.7 punti base, negli altri +5.6, **differenza +0.1 (t 0.01)**; la regola con i costi Sharpe 0.56 (+27.2%) contro lo SPY 0.86 (+66.8%).
