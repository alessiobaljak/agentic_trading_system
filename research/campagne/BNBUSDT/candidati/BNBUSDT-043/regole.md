# Candidato BNBUSDT-043 — regole

Variante BNBUSDT-043, terzo ritocco della famiglia BNBUSDT-005 (idea I-03, Connors e Alvarez 2008),
diventata candidato in Fase 2 il 9 ottobre 2026. Codice: `codice/varianti.py`, funzione
`i03("1h", vid, max_barre=12, atr_rel_min=0.015)` (gli altri argomenti ai valori predefiniti).

| | Regola |
|---|---|
| Moneta | BNBUSDT (perpetuo USDS-M) |
| Timeframe dei segnali | 1h, candele last price |
| Direzione | solo long |
| Ingresso | alla chiusura di una barra a 1h, se: chiusura > media semplice delle ultime 200 chiusure; RSI di Wilder a 2 periodi < 5; ATR di Wilder a 14 barre ≥ 1,5% della chiusura. Ingresso a mercato all'apertura della barra successiva |
| Uscita | alla chiusura della prima barra in cui la chiusura supera la media semplice delle ultime 5 chiusure, oppure alla chiusura della 12ª barra in posizione (contando quella d'ingresso): si esce all'apertura della barra dopo |
| Stop | 2,5 ATR(14) sotto la chiusura della barra di segnale, sul last price |
| Target | nessuno |
| Filtri | nessun ingresso su segnali di maggio e giugno 2020 (mesi sotto la liquidità minima, `fase0_dati.md`) |
| Dimensione e leva | regole del bot (`config/regole_dimensione.md`): rischio 1% del capitale per trade, quantità = capitale × 0,01 / distanza dello stop, nozionale al massimo 2 volte il capitale (trade ridotti se serve), margine isolato, liquidazione sul mark price |
| Costi del backtest | commissione 0,05% per lato, slippage 0,02% per lato (fascia della scheda), funding storico ogni 8 ore |

**Motivo economico.** In tendenza rialzista (sopra la media a 200 ore), un calo brusco di poche ore
(RSI a 2 periodi sotto 5) viene da venditori impazienti o forzati che spingono il prezzo sotto il
valore di breve; chi fornisce liquidità viene pagato con il rimbalzo. Il filtro di volatilità e
l'uscita a tempo vengono dallo studio dei fallimenti (note BNBUSDT-N018 e N020): con volatilità
bassa i costi pesano troppo in R, e se il rimbalzo non arriva in mezza giornata il trade tende a
finire sullo stop.

**Rischio noto, da prima delle verifiche.** Il filtro di volatilità sceglie le ore in cui lo stop
è largo in prezzo e i costi pesano meno in R; la baseline (b) entra anche nelle ore calme. Una
parte del vantaggio può essere solo questo: lo misura la verifica `scettico_b_volatile`.

**Eseguibilità nel bot.** Stop di 2,5 ATR orari con ATR ≥ 1,5%: stop di almeno il 3,75% del
prezzo, sotto il tetto del 6% del bot solo quando l'ATR orario è sotto il 2,4% (da verificare sui
trade). Il bot dal vivo ha indicatori a 1h (`regole_dimensione.md`), ma non esegue strategie del
protocollo senza l'aggiunta descritta al Passo 0.
