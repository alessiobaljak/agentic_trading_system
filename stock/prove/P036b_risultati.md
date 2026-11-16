# Controllo dopo la prova 36 — il costo vero degli acquisti fuori seduta

Calcolato da `python -m stock.prove.p036b` il 2026-11-16 07:55 UTC con il metodo di `P036b_costo_fuori_seduta.md` (scritto prima). **Non è una prova**: la prova 36 resta bocciata. Campione: 400 ingressi fuori seduta e 200 in seduta delle 2615 operazioni della prova 36; senza quotazione prima dell'ingresso (o rifiutati da Alpaca) 135; senza operazioni di mercato nel minuto dell'ingresso 1.

La «metà dello scarto quotato» è il costo di chi compra subito al prezzo di chi vende; lo «scarto effettivo» è quanto hanno pagato davvero, rispetto al mezzo, le operazioni di mercato di quel minuto. «Dove apre la barra»: 1 al prezzo di chi vende, 0 al mezzo, −1 al prezzo di chi compra; fra parentesi la quota di barre che aprono da 0,8 in su. I netti tolgono anche lo slittamento 2 + 2 punti base e le commissioni su 10'000 dollari.

| Gruppo | Ingressi | Metà dello scarto quotato, mediana (punti base) | Scarto effettivo, mediana (punti base) | Dove apre la barra, mediana (quota al prezzo di chi vende) | Guadagno dal mezzo prima dei costi | Netto A (quotato) | Netto B (effettivo) | Netto C (come la prova 36) |
|---|---|---|---|---|---|---|---|---|
| fuori seduta, tutti | 266 | 41.6 | 21.4 | -0.03 (30%) | +0.015% | -1.449% (t -1.87, n 266) | -1.022% (t -1.33, n 266) | -0.150% (t -1.07, n 266) |
| dopo la chiusura | 193 | 31.8 | 19.1 | +0.00 (32%) | +0.546% | -0.552% (t -2.08, n 193) | -0.100% (t -0.45, n 193) | -0.036% (t -0.19, n 193) |
| prima dell'apertura | 73 | 75.7 | 28.5 | -0.33 (25%) | -1.390% | -3.820% (t -1.40, n 73) | -3.459% (t -1.27, n 73) | -0.452% (t -5.28, n 73) |
| in seduta | 199 | 3.6 | 2.1 | +0.00 (24%) | +0.597% | +0.241% (t 0.67, n 199) | +0.151% (t 1.23, n 198) | +0.192% (t 1.79, n 199) |
| ora 4:00-6:59 | 12 | 19.0 | 20.9 | -1.00 (17%) | +0.170% | -0.526% (t -1.29, n 12) | -0.376% (t -1.00, n 12) | -0.266% (t -1.09, n 12) |
| ora 7:00-9:29 | 61 | 80.4 | 30.4 | -0.12 (26%) | -1.697% | -4.467% (t -1.37, n 61) | -4.065% (t -1.24, n 61) | -0.489% (t -5.39, n 61) |
| ora 16:00-16:59 | 105 | 39.6 | 19.0 | +0.04 (32%) | +0.432% | -1.012% (t -2.69, n 105) | -0.259% (t -0.92, n 105) | -0.248% (t -1.09, n 105) |
| ora 17:00-17:59 | 56 | 23.7 | 20.3 | +0.10 (30%) | +0.699% | -0.035% (t -0.09, n 56) | +0.004% (t 0.01, n 56) | +0.232% (t 0.73, n 56) |
| ora 18:00-19:59 | 32 | 28.9 | 18.0 | -0.65 (31%) | +0.653% | +0.050% (t 0.07, n 32) | +0.235% (t 0.32, n 32) | +0.193% (t 0.28, n 32) |
