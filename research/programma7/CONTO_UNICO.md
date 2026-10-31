# Il conto unico per i soldi veri: G1 più gli eventi, sul passato (misura descrittiva)

Script `conto_unico.py`. G1 con tutto il capitale (i giorni della prova 57, dal 4 gennaio 2021 al 4 ottobre 2026); in più ogni evento della prova 32 (le monete appena quotate su Binance) e della prova 26 (il funding al tetto) con il 5% del capitale, al massimo 20 aperti insieme, come il paper degli eventi. Il rendimento di ogni evento è spalmato sui suoi giorni: è un'approssimazione, la discesa vera è un po' più grande. Non è una prova e non entra nel conto.

* Eventi usati 664, saltati perché ce n'erano già 20 aperti 11.

| | Rendimento all'anno | Sharpe | Discesa massima | Giorno peggiore |
|---|---|---|---|---|
| G1 da sola | +65.7% | 1.98 | -30.1% | -8.5% |
| G1 più gli eventi | +115.5% | 2.82 | -22.3% | -8.7% |
| Gli eventi da soli (al 5%) | +30.2% | 3.41 | -25.2% | -3.2% |

Per anno (G1 da sola → G1 più gli eventi): 2021 +177.6% → +166.5%, 2022 +32.4% → +36.4%, 2023 +5.9% → +41.0%, 2024 +93.1% → +228.8%, 2025 +92.2% → +279.6%, 2026 +26.4% → +29.7%.

Correlazione fra G1 e gli eventi, giorno per giorno: 0.03.
