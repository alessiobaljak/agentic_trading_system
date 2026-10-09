# Candidato BNBUSDT-045 — regole

Variante BNBUSDT-045, quinto e ultimo ritocco della famiglia BNBUSDT-005 (idea I-03, Connors e
Alvarez 2008), trentesima e ultima variante del budget, diventata candidato in Fase 2 il 9 ottobre
2026. Codice: `codice/varianti.py`, funzione `i03("1h", vid, max_barre=12, solo_fine_settimana=True)`.

| | Regola |
|---|---|
| Moneta | BNBUSDT (perpetuo USDS-M) |
| Timeframe dei segnali | 1h, candele last price |
| Direzione | solo long |
| Ingresso | alla chiusura di una barra a 1h che apre di sabato o domenica (UTC), se: chiusura > media semplice delle ultime 200 chiusure e RSI di Wilder a 2 periodi < 5. Ingresso a mercato all'apertura della barra successiva |
| Uscita | alla chiusura della prima barra con chiusura sopra la media semplice delle ultime 5 chiusure, oppure alla chiusura della 12ª barra in posizione: uscita all'apertura della barra dopo |
| Stop | 2,5 ATR di Wilder a 14 barre sotto la chiusura della barra di segnale, sul last price |
| Target | nessuno |
| Filtri | nessun ingresso su segnali di maggio e giugno 2020 |
| Dimensione e leva | regole del bot: rischio 1% per trade, nozionale al massimo 2 volte il capitale, margine isolato, liquidazione sul mark |
| Costi del backtest | commissione 0,05% e slippage 0,02% per lato, funding storico ogni 8 ore |

**Motivo economico.** Un calo brusco di poche ore dentro una tendenza rialzista viene assorbito da
chi fornisce liquidità. Nel fine settimana gli operatori istituzionali sono in gran parte assenti e
la liquidità è più sottile: i cali sono più spesso pressione di liquidità che informazione, e
rimbalzano.

**Rischi noti, da prima delle verifiche.** Il filtro del fine settimana è stato scelto guardando
l'R medio dei 7 giorni della settimana sugli stessi trade di costruzione (nota BNBUSDT-N018): è il
caso più esposto alla fortuna di tutta la campagna. Con 74 trade, molti casi delle verifiche di
robustezza possono scendere sotto il minimo di 70. Stessa famiglia di BNBUSDT-043 e 044, scartati
perché il vantaggio spariva entrando un'ora dopo.
