# Candidato FILUSDT-025 — rottura di volatilità dall'apertura del giorno, long, 1 ora

Variante diventata candidato in Fase 2 (log: registrazione e risultato FILUSDT-025). Le regole
sotto sono quelle registrate prima del test e non cambiano.

| | Regola |
|---|---|
| Moneta | FILUSDT (perpetuo USDS-M di Binance) |
| Timeframe dei segnali | 1 ora (candele del last), giorni UTC |
| Direzione | long |
| Riferimenti del giorno | apertura del giorno = open della prima barra oraria del giorno UTC; escursione del giorno precedente = massimo degli high − minimo dei low delle barre orarie del giorno UTC precedente |
| Ingresso | alla chiusura di una barra delle ore 00-22 UTC, se close > apertura del giorno + 0,6 × escursione del giorno precedente, ed è la prima barra del giorno con questa condizione → long all'apertura della barra dopo |
| Stop | l'apertura del giorno (sul last) |
| Target | nessuno |
| Uscita | alla chiusura della barra delle 23 UTC, cioè all'apertura del giorno dopo; oppure allo stop |
| Una posizione alla volta | sì; al massimo un ingresso al giorno |
| Filtri | nessuno (il filtro di liquidità della Fase 0 non esclude nessun mese) |
| Dimensione | rischio 1% del capitale per trade: quantità = capitale × 0,01 / |apertura − stop| |
| Leva | effettiva fra 1 e 2, margine isolato; stop medio 5,4% dall'ingresso: nozionale circa 0,19 volte il capitale, leva 1, nessun trade ridotto |
| Costi | commissione 0,05% per lato, slippage 0,02% per lato, funding storico a 8 ore |

**Motivo economico.** Williams (1999), Crabel (1990): un movimento dall'apertura del giorno
ampio rispetto all'escursione del giorno precedente segnala un flusso direzionale (notizie,
ordini grandi) che continua per il resto della giornata; se il prezzo torna all'apertura del
giorno la rottura è fallita (stop).

**Codice.** `codice/varianti.py`, funzione `i13("long", ...)` con i valori predefiniti (k = 0,6,
1 ora); quadro comune in `codice/quadro.py`.

**Esito della Fase 4 (2026-10-09): superate tutte le verifiche** (nota FILUSDT-N011): robustezza,
timeframe adiacenti, stabilità per anno, trade estremi, ritardo di una barra, costi doppi,
liquidazione; regola intra-barra opposta identica. Dubbio aperto per la Fase 5: le baseline (a)
e (b) sono molto negative perché con lo stesso stop all'apertura del giorno un ingresso casuale
ha spesso uno stop vicinissimo e costi enormi in R.

**Eseguibilità nel bot.** Timeframe 1 ora: il bot ha gli indicatori dal vivo a 1 ora; serve il
percorso «coppia del protocollo» del Passo 0 (decisione aperta n. 4) e una regola d'uscita a
orario (fine del giorno UTC), che il bot non ha come tale (ha un orizzonte in barre: con 24 barre
massime la posizione resterebbe aperta oltre la fine del giorno; serve un'aggiunta). Stop medio
5,4%, 29% dei trade con stop oltre il tetto del 6% del bot: quei trade il bot li rifiuterebbe.
