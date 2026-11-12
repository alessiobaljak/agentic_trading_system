# Controllo dei dati per la prova 28 (il tono delle notizie) — quante notizie ha Alpaca

Calcolato da `python -m stock.prove.p028a` il 2026-11-12 11:08 UTC. Non è una prova: nessun rendimento guardato, solo conteggi. Campione fisso di 30 titoli dell'S&P 500 (uno ogni 17 in ordine alfabetico: A, AIZ, AOS, BAC, BRO, CF, COF, CTAS, DHR, ED, EW, FIS, GILD, HD, IBM, J, KR, LVS, MLM, MU, NVR, PEG, PPL, RMD, SNPS, T, TROW, UNP, VTRS, WY), notizie di marzo di ogni anno.

| Anno | Notizie per titolo nel mese (mediana) | Media | Titoli senza notizie | Minimo–massimo | Titoli con l'elenco troncato (oltre 500) | Titoli citati per notizia (mediana) |
|---|---|---|---|---|---|---|
| 2015 | 1 | 8 | 8 su 30 | 0–32 | 0 | 3 |
| 2016 | 3 | 8 | 4 su 30 | 0–52 | 0 | 2 |
| 2017 | 3 | 9 | 8 su 30 | 0–55 | 0 | 4 |
| 2018 | 2 | 7 | 8 su 30 | 0–52 | 0 | 3 |
| 2019 | 2 | 8 | 8 su 30 | 0–53 | 0 | 2 |
| 2020 | 9 | 13 | 1 su 30 | 0–44 | 0 | 3 |
| 2021 | 5 | 11 | 1 su 30 | 0–55 | 0 | 3 |
| 2022 | 7 | 14 | 0 su 30 | 1–70 | 0 | 2 |
| 2023 | 6 | 13 | 2 su 30 | 0–91 | 0 | 2 |
| 2024 | 7 | 13 | 1 su 30 | 0–109 | 0 | 1 |
| 2025 | 5 | 11 | 2 su 30 | 0–64 | 0 | 1 |

Notizie del campione: 3423; senza riassunto (solo il titolo): 78%; fonti:  1898, benzinga 1525.

| Giorno intero, tutti i titoli | Notizie | Con almeno un titolo citato | Fuori dall'orario di borsa (prima delle 9 o dopo le 16 di New York) |
|---|---|---|---|
| 2016-03-15 | 662 | 613 | 62% |
| 2020-03-16 | 800 | 768 | 50% |
| 2024-03-15 | 928 | 896 | 44% |
