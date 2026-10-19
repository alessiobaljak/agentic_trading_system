# Programma 6 — risultati della seconda prova

Regole in `SECONDA.md` (scritte prima). Dal 2021-01-01 all'ultimo giorno scaricato; universo mese per mese con i soli dati di allora, fra tutte le monete dell'archivio.

## Parte A — la regola pubblicata (Zarattini, Pagani e Barbon 2025)

| Variante | Rendimento/anno | Intervallo (giorno) | Volatilità | Sharpe | Sharpe corretto | Discesa massima | Anni positivi | Ultimo anno | Dopo l'articolo (anno; Sharpe) | Costi doppi (giorno) | In più del BTC/anno | Esposizione media | Esito |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| A1 | +3.7% | -0.006%; +0.028% | 6.9% | 0.53 | 0.28 | -14.1% | 4/6 | -0.1% | +1.5%; 0.25 | +0.0093% | +1.3% | 0.08 | netto con l'intervallo non sopra zero |
| A2 | +2.3% | -0.012%; +0.026% | 9.4% | 0.25 | 0.10 | -14.8% | 5/6 | +3.5% | -2.4%; -0.24 | +0.0047% | +3.8% | 0.13 | netto con l'intervallo non sopra zero |
| A3 | +6.6% | -0.014%; +0.052% | 13.8% | 0.48 | 0.23 | -22.4% | 4/6 | -5.5% | -0.1%; -0.01 | +0.0166% | +0.6% | 0.21 | netto con l'intervallo non sopra zero |
| sempre | +5.2% | -0.028%; +0.058% | 19.5% | 0.27 | 0.11 | -32.4% | 4/6 | -10.0% | +5.3%; 0.26 | +0.0136% | -4.1% | 0.27 | confronto |

Bitcoin sempre comprato: +34.1% l'anno, Sharpe 0.60, discesa massima -76.7%; dopo l'articolo +12.9% l'anno, Sharpe 0.31.

### Per anno (rendimento netto annualizzato)

| Variante | 2021 | 2022 | 2023 | 2024 | 2025 | 2026 |
|---|---|---|---|---|---|---|
| A1 | +7.7% | -5.4% | +12.5% | +7.2% | -2.9% | +2.8% |
| A2 | +4.8% | +5.9% | +2.8% | +3.1% | -5.1% | +2.7% |
| A3 | +5.5% | -10.8% | +23.1% | +25.6% | -6.1% | +0.7% |
| sempre | +17.3% | -30.0% | +32.2% | +14.8% | -6.6% | +3.3% |

## Parte B — le famiglie della prima prova a 1 giorno, con le finestre che avanzano

| Famiglia | Trade | R a trade | Intervallo | Netto a trade | Sharpe (con tetto) | Rendimento/anno (con tetto) | Sharpe corretto | PBO | Anni positivi | Ultimo anno (R) | Esito |
|---|---|---|---|---|---|---|---|---|---|---|---|
| bollinger_ritorno | 1459 | -0.008 | -0.105; +0.092 | +0.827% | -0.06 | -2.1% | 0.03 | 0.34 | 4/6 | +0.093 | netto con l'intervallo non sopra zero |
| compressione | 559 | -0.077 | -0.238; +0.096 | -2.016% | -0.46 | -10.2% | 0.01 | 0.52 | 2/4 | +0.177 | netto con l'intervallo non sopra zero |
| incrocio | 1004 | +0.097 | -0.022; +0.228 | +1.716% | 0.47 | +20.5% | 0.19 | 0.28 | 5/5 | +0.167 | netto con l'intervallo non sopra zero |
| keltner | 821 | -0.142 | -0.270; -0.001 | -3.051% | -0.67 | -22.2% | 0.02 | 0.80 | 0/6 | -0.032 | netto con l'intervallo non sopra zero |
| macd_adx | 510 | +0.026 | -0.144; +0.251 | -0.354% | 0.17 | +5.2% | 0.15 | 0.18 | 2/3 | +nan | netto con l'intervallo non sopra zero |
| rottura | 1161 | -0.128 | -0.248; +0.001 | -2.462% | -0.80 | -29.5% | 0.01 | 0.25 | 1/6 | -0.125 | netto con l'intervallo non sopra zero |
| rsi_ritorno | 1502 | -0.009 | -0.107; +0.089 | +0.876% | -0.07 | -2.5% | 0.02 | 0.45 | 2/6 | -0.006 | netto con l'intervallo non sopra zero |
| rsi_spinta | 1240 | -0.017 | -0.128; +0.105 | -0.647% | -0.13 | -4.2% | 0.03 | 0.32 | 2/6 | +0.042 | netto con l'intervallo non sopra zero |
| supertrend | 1209 | +0.022 | -0.104; +0.146 | +0.528% | 0.14 | +5.2% | 0.07 | 0.43 | 4/6 | +0.047 | netto con l'intervallo non sopra zero |
