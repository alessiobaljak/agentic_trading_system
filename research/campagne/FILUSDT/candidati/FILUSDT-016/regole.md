# Candidato FILUSDT-016 — FIL in ritardo rispetto a BTC, long, 1 ora

Variante diventata candidato in Fase 2 (log: registrazione e risultato FILUSDT-016). Le regole
sotto sono quelle registrate prima del test e non cambiano.

| | Regola |
|---|---|
| Moneta | FILUSDT (perpetuo USDS-M di Binance) |
| Timeframe dei segnali | 1 ora (candele del last), riferimento BTCUSDT 1 ora (close del last) |
| Direzione | long |
| Ingresso | alla chiusura della barra i: rendimento di BTCUSDT sulle ultime 4 barre (close[i] / close[i−4] − 1) > +2%, e rendimento di FILUSDT sulle stesse 4 barre < quello di BTCUSDT → long all'apertura della barra i+1 |
| Stop | close[i] − 1,5 × ATR(24) di FILUSDT (ATR di Wilder sulle candele da 1 ora), sul last |
| Target | nessuno |
| Uscita | dopo 8 barre in posizione, all'apertura della barra successiva (posizione di 8 ore), oppure allo stop |
| Una posizione alla volta | un segnale con posizione aperta si ignora |
| Filtri | nessuno (il filtro di liquidità della Fase 0 non esclude nessun mese) |
| Dimensione | rischio 1% del capitale per trade: quantità = capitale × 0,01 / |apertura − stop| |
| Leva | effettiva fra 1 e 2 (tetto del bot), margine isolato; con lo stop medio del 3% il nozionale è circa 0,33 volte il capitale: leva 1, nessun trade ridotto |
| Costi | commissione 0,05% per lato, slippage 0,02% per lato, funding storico a 8 ore |

**Motivo economico.** I prezzi delle monete meno seguite incorporano in ritardo le notizie di
mercato (Hou e Moskowitz 2005); BTC è il riferimento delle crypto e muove per primo
(Sifat, Mohamad, Shariff 2019). Quando BTC sale con forza in poche ore e FIL resta indietro, la
rincorsa di FIL (market maker che aggiornano le quote, operatori che ruotano da BTC alle altcoin)
dovrebbe arrivare nelle ore successive.

**Codice.** `codice/varianti.py`, funzione `i08("long", ...)` con i valori predefiniti; quadro comune
in `codice/quadro.py`.

**Esito della Fase 4 (2026-10-09): SCARTATO per i costi doppi.** Superate robustezza (10 casi,
`t` contro la (b) positivo in tutti, netto in 8), timeframe adiacenti (30m e 2h), ritardo di una
barra (`t` 2,09), stabilità per anno (2 anni su 3), trade estremi, liquidazione; regola
intra-barra opposta identica. A costi doppi batte ancora la (b) ma l'R medio è −0,004: non
positivo. Non va in validazione (log FILUSDT-016-C2 e nota FILUSDT-N010).

**Eseguibilità nel bot.** Timeframe 1 ora: il bot ha gli indicatori dal vivo a 1 ora
(`config/regole_dimensione.md`); serve però il prezzo di BTCUSDT dentro la strategia di FILUSDT e il
percorso «coppia del protocollo» del Passo 0 (decisione aperta n. 4). Posizione di 8 barre: sotto
l'orizzonte di 96 barre del bot. Stop medio 3,0%, 5,4% dei trade oltre il tetto del 6% del bot.
