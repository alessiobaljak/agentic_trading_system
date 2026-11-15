# Controllo dopo le prove sulle piccole — il paniere di base contro l'IWM

Calcolato da `python -m stock.prove.p034b` il 2026-11-15 06:11 UTC. **Non è una prova**: misura la base contro cui si sono confrontate le prove 27, 28, 32 e 34 (non entra nel conto). Ogni fine mese tutti i titoli ammessi con i filtri delle prove, tenuti un mese da chiusura a chiusura, meno l'IWM negli stessi giorni; solo il periodo di ricerca, fino al 31 dicembre 2024. Titoli con i dati rotti 10; fondi esclusi 4271.

| Paniere | Come | Mesi | Medio meno IWM al mese | t | Mediana | Mesi sopra l'IWM | Somma per anno |
|---|---|---|---|---|---|---|---|
| A — i titoli di FINRA (prova 32) | pesi uguali | 83 | **-0.13%** | -1.24 | -0.08% | 43% | 2018: -1% 2019: -1% 2020: +3% 2021: -5% 2022: -2% 2023: -1% 2024: -3% |
| A — i titoli di FINRA (prova 32) | pesi per dollari | 83 | **+0.24%** | 0.62 | +0.22% | 52% | 2018: -4% 2019: +5% 2020: +46% 2021: -27% 2022: -13% 2023: +9% 2024: +6% |
| A — i titoli di FINRA (prova 32) | senza «Acquisition» | 83 | **-0.13%** | -1.22 | -0.10% | 43% | 2018: -1% 2019: -1% 2020: +3% 2021: -5% 2022: -2% 2023: -1% 2024: -3% |
| A — i titoli di FINRA (prova 32) | mediana dei titoli | 83 | **-0.53%** | -3.90 | -0.40% | 37% | 2018: -3% 2019: -2% 2020: -19% 2021: -4% 2022: -3% 2023: -5% 2024: -9% |
| B — chi ha un comunicato nel mese (prova 34) | pesi uguali | 106 | **-0.02%** | -0.10 | -0.22% | 42% | 2016: -4% 2017: -1% 2018: +0% 2019: -2% 2020: +15% 2021: -1% 2022: +2% 2023: -0% 2024: -10% |
| B — chi ha un comunicato nel mese (prova 34) | pesi per dollari | 106 | **+0.35%** | 0.67 | +0.26% | 55% | 2016: -8% 2017: -1% 2018: +1% 2019: +5% 2020: +75% 2021: -27% 2022: -14% 2023: +2% 2024: +5% |
| B — chi ha un comunicato nel mese (prova 34) | senza «Acquisition» | 106 | **-0.02%** | -0.10 | -0.22% | 42% | 2016: -4% 2017: -1% 2018: -0% 2019: -3% 2020: +15% 2021: -1% 2022: +2% 2023: -0% 2024: -10% |
| B — chi ha un comunicato nel mese (prova 34) | mediana dei titoli | 106 | **-0.44%** | -3.11 | -0.30% | 37% | 2016: -5% 2017: -4% 2018: -2% 2019: -2% 2020: -21% 2021: +1% 2022: +1% 2023: -2% 2024: -13% |

**Nomi con «Acquisition» (società vuote in attesa di una fusione), media per anno: fra gli ammessi della prova 32 / fra i 50 scelti dalla prova 32:** 2018: 0% / 0% | 2019: 0% / 0% | 2020: 0% / 2% | 2021: 0% / 2% | 2022: 0% / 0% | 2023: 0% / 0% | 2024: 0% / 0%.

Il nome viene dall'elenco di oggi di Alpaca: una società vuota che si è già fusa può avere oggi un altro nome, quindi le quote sono un minimo.
