# Controllo dopo la revisione della prova 37 — la miscela del demo con le chiusure ufficiali

Calcolato da `python -m stock.prove.p025c` il 2026-11-17 02:35 UTC con il metodo di `P025c_chiusure_ufficiali.md` (scritto prima). **Non è una prova**: stesse regole delle prove 15, 16 e 25, cambiano solo apertura, massimo, minimo e chiusura di SPY e QQQ (Yahoo al posto di Alpaca). Dal 2016-11-01 al 2024-12-31.

**Le due fonti** (giorni oltre 5 punti base di differenza / giorni / differenza massima in punti base): SPY apertura 26/2264 (139), chiusura 81/2264 (287); QQQ apertura 60/2264 (19), chiusura 1/2264 (9).

| Parte | Sharpe prima (Alpaca) | Sharpe con le chiusure ufficiali | Guadagno prima | Guadagno con le chiusure ufficiali |
|---|---|---|---|---|
| P007_SPY | 0.84 | 0.84 | +15.7% | +15.7% |
| P007_QQQ | 0.98 | 0.98 | +27.0% | +27.0% |
| P015_SPY | 0.95 | 0.93 | +205.9% | +200.9% |
| P015_QQQ | 1.07 | 1.07 | +297.0% | +297.0% |
| P016_SPY | 0.94 | 0.93 | +154.0% | +154.0% |
| P016_QQQ | 0.96 | 0.96 | +253.9% | +253.7% |

| | Miscela prima | Miscela con le chiusure ufficiali | Tenere lo SPY (ufficiali) | Metà SPY e metà QQQ (ufficiali) |
|---|---|---|---|---|
| Sharpe con i costi | 1.08 | **1.08** | 0.87 (Alpaca 0.89) | 0.93 |
| Guadagno totale | +139.4% | +138.8% | +219.0% | +289.5% |
| Perdita massima | -14.6% | -14.5% | -33.7% | -30.9% |
| Correlazione giornaliera fra prima e ora | 0.9996 | | | |

**Esito (regola scritta prima):** la miscela resta sopra il tenere lo SPY e metà SPY metà QQQ: resta sul demo come è.
