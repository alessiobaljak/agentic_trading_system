# Candidato BNBUSDT-044 — regole

Variante BNBUSDT-044, quarto ritocco della famiglia BNBUSDT-005 (idea I-03, Connors e Alvarez 2008),
diventata candidato in Fase 2 il 9 ottobre 2026. Codice: `codice/varianti.py`, funzione
`i03("1h", vid, max_barre=12, dist_lunga_atr=1.7)` (gli altri argomenti ai valori predefiniti).

| | Regola |
|---|---|
| Moneta | BNBUSDT (perpetuo USDS-M) |
| Timeframe dei segnali | 1h, candele last price |
| Direzione | solo long |
| Ingresso | alla chiusura di una barra a 1h, se: chiusura − media semplice delle ultime 200 chiusure ≥ 1,7 ATR di Wilder a 14 barre; RSI di Wilder a 2 periodi < 5. Ingresso a mercato all'apertura della barra successiva |
| Uscita | alla chiusura della prima barra in cui la chiusura supera la media semplice delle ultime 5 chiusure, oppure alla chiusura della 12ª barra in posizione: si esce all'apertura della barra dopo |
| Stop | 2,5 ATR(14) sotto la chiusura della barra di segnale, sul last price |
| Target | nessuno |
| Filtri | nessun ingresso su segnali di maggio e giugno 2020 (mesi sotto la liquidità minima) |
| Dimensione e leva | regole del bot: rischio 1% per trade, nozionale al massimo 2 volte il capitale, margine isolato, liquidazione sul mark |
| Costi del backtest | commissione 0,05% e slippage 0,02% per lato, funding storico ogni 8 ore |

**Motivo economico.** Come per I-03: un calo brusco di poche ore dentro una tendenza rialzista
viene assorbito da chi fornisce liquidità. Il filtro di distanza dalla media a 200 (nota
BNBUSDT-N024) tiene solo i cali dentro una tendenza chiara: i cali che portano il prezzo vicino
alla media lunga sono più spesso l'inizio di una rottura della tendenza.

**Rischio noto, da prima delle verifiche.** È la stessa famiglia di BNBUSDT-043, scartato perché il
vantaggio spariva entrando un'ora dopo (nota BNBUSDT-N023): è probabile che succeda lo stesso. Il
filtro sceglie le fasi di forte tendenza: lo misura la verifica `scettico_b_tendenza`.
