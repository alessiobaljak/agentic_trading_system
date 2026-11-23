# Perché il numero «corretto» di G1 scende a ogni prova (analisi del 23 novembre 2026)

Domanda del proprietario (23 novembre): «come cazzo è possibile che lo Sharpe venga influenzato dalle prove che facciamo [...] fai
un'analisi e dimmi se è veramente così».

## Cosa calcola davvero il codice
* `research/programma6/terza.py`, `sharpe_corretto`, chiamato da `asticella.corretto_famiglie`: è il **Deflated Sharpe Ratio** (Bailey e
  López de Prado 2014). Il risultato è `norm.cdf(...)`: **una probabilità fra 0 e 1**, non uno Sharpe. Dice quanto è probabile che lo
  Sharpe vero della strategia sia sopra quello che si otterrebbe per **fortuna** prendendo la migliore fra N prove.
* «La fortuna da battere» (`sr0`) cresce con il numero delle famiglie di prove N e con la dispersione degli Sharpe fra le prove.

## I numeri (mazzo di oggi, 200 famiglie; G1 = serie della prova 57)
* G1 sul passato: Sharpe 1,97, 300 settimane, +54,1% l'anno: **non cambia** con le prove nuove.
* La fortuna da battere: con N = 57 vale uno Sharpe di 1,58 l'anno; con N = 200 (oggi) 1,87; con N = 1.000 2,21.
* La probabilità di G1 con la dispersione di oggi: N = 57 → 0,84; N = 100 → 0,74; **N = 200 → 0,59 (il numero di oggi)**; N = 400 →
  0,45; N = 1.000 → 0,27. Senza la sola serie con Sharpe sopra 3 la dispersione scende da 0,68 a 0,63 e i valori salgono (N = 200 → 0,73).
* Quindi sì: **con il metodo di oggi il numero di G1 continuerebbe a scendere** a ogni prova nuova, senza che G1 cambi.

## Cosa non va nel modo in cui lo usiamo
1. **N è sbagliato per G1.** Il metodo serve a giudicare «la migliore fra N»: G1 è stata scelta quando le prove erano 57. Le prove fatte
   dopo su idee diverse, che non l'hanno mai rimessa in gara, non la rendono più fortunata.
2. **Lo sconto serve quando mancano i dati nuovi.** G1 gira nel paper da fine ottobre e sul demo dall'8 novembre: quei giorni non hanno
   nessuna selezione dentro e sono il controllo vero (ancora pochi: un mese).
3. **Il nome confonde**: «Sharpe corretto» fa pensare a uno Sharpe; è una probabilità. La soglia 0,80 (prima 0,95) è una soglia di
   probabilità.

## Proposta (da decidere con il proprietario, cambia il metodo dell'11 novembre)
* Ogni strategia si giudica **una volta**, con N = le famiglie di prove fatte fino a quando è stata scelta; poi si giudica **in avanti**
  (paper, demo e confronto settimanale), non di nuovo con lo sconto di oggi.
* Le prove nuove si giudicano con N di oggi, come adesso.
* Nei rapporti al proprietario il numero si chiama «probabilità che non sia fortuna».
