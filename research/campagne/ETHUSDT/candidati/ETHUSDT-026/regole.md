# Candidato ETHUSDT-026 — rifiuto al massimo del giorno prima, short (variante I-14a)

Scritto in Fase 4, dopo che la variante e' diventata candidato in Fase 2 sul periodo di
costruzione (2020-01-01 → 2022-10-18). Le regole sono quelle registrate (log, voce
ETHUSDT-026) e non cambiano.

| Campo | Regola |
|---|---|
| Moneta | ETHUSDT (perpetuo USDS-M di Binance) |
| Timeframe dei segnali | 1 ora (candele last price, UTC) |
| Direzione | short |
| Ingresso | alla chiusura di una barra oraria il cui massimo supera il massimo del giorno UTC precedente e la cui chiusura resta sotto quel massimo; si entra short all'apertura della barra successiva, se non c'e' gia' una posizione |
| Stop | massimo della barra del segnale + 0,25 x ATR(14) (Wilder, barre orarie chiuse), con distanza dalla chiusura del segnale al massimo 6% (tetto del bot); scatta sul last price |
| Target | nessuno |
| Uscita | "chiudi" alla chiusura della sesta barra in posizione (la barra d'ingresso conta 1): uscita all'apertura della settima, circa 6 ore dopo l'ingresso |
| Dimensione | rischio 1% del capitale: quantita' = capitale x 0,01 / |apertura - stop| (regole del bot, `config/regole_dimensione.md`) |
| Leva | al massimo 2: se il nozionale supererebbe 2 volte il capitale la quantita' si riduce al tetto (17 trade ridotti su 615 in costruzione); margine isolated per il calcolo della liquidazione |
| Filtri | nessuno; giorno precedente valido solo se e' il giorno di calendario subito prima (con un buco nei dati il giorno dopo non segnala) |
| Codice | `campagne/ETHUSDT/codice/idee.py`, classe `GiornoPrima` con `direzione="short"` (parametri: `uscita=6`, `k_stop=0.25`, `n_atr=14`) |

**Motivo economico (ipotesi, non provato).** Carol L. Osler, «Support for Resistance:
Technical Analysis and Intraday Exchange Rates», FRBNY Economic Policy Review 6(2), 2000: i
livelli di resistenza che gli operatori guardano fanno invertire i movimenti intragiornalieri
piu' spesso del caso. Il massimo del giorno prima e' un livello visibile a tutti sui grafici
giornalieri; chi vende li' (ordini di presa di profitto, venditori alla resistenza) puo'
respingere il prezzo quando lo supera senza tenerlo.

**Esito: SCARTATO in Fase 4** (voce ETHUSDT-N015): non supera i costi doppi (R medio -0,076)
ne' il ritardo di una barra (t 1,27 contro 2,67; nessun errore di lookahead trovato, voce
N014). Supera robustezza, timeframe adiacenti, stabilita', trade estremi e liquidazione. Non
va in validazione.

**Numeri di costruzione (ETHUSDT-026).** 615 trade; R medio +0,023 dopo i costi; senza i 3
trade migliori -0,023; R medio per anno 2020 -0,050, 2021 +0,138, 2022 -0,056; contro la (a)
t 2,76 (netta), contro la (b) t 2,67 con soglia 2,03 (netta); (b) R medio -0,175; percentile
fra le simulazioni 99,5. Il vantaggio misurato e' soprattutto "perdere molto meno di uno short
casuale" in un periodo di rialzo: in assoluto l'R medio e' vicino a zero.
