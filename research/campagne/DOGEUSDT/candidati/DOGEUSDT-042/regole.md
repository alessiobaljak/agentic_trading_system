# Candidato DOGEUSDT-042 — short all'uscita verso il basso da una strettoia delle bande di Bollinger

Famiglia DOGEUSDT-035 (idea I-10, variante allentata a 1h), terzo ritocco (ritocchi 2 e 3
della campagna: stop 3 ATR, finestra della strettoia di 480 barre). Codice:
`codice/varianti.py` (classe `Strettoia`, voce `DOGEUSDT-042`) e `codice/quadro.py`.

| | |
|---|---|
| Moneta | DOGEUSDT (perpetuo USDS-M) |
| Timeframe dei segnali | 1h, candele del last price, solo barre chiuse |
| Direzione | short |
| Ingresso | alla chiusura della barra i: ampiezza delle bande `4 × dev.std(20) / SMA20` minore o uguale al 20° percentile delle ampiezze delle ultime 480 barre (barra i compresa) **e** close < SMA20 − 2 × dev.std(20) (deviazione standard campionaria). Ingresso short all'apertura della barra i+1. Nessun ingresso se c'è già una posizione, né su barre dei mesi sotto la liquidità minima (Fase 0) |
| Stop | close della barra del segnale + 3 × ATR di Wilder a 14 barre; scatta sul last |
| Target | nessuno |
| Uscita | a tempo: alla chiusura della 12ª barra tenuta si chiude all'apertura della barra dopo |
| Dimensione | rischio 1% del capitale per trade (quantità = capitale × 0,01 / |apertura − stop|), ridotta al tetto di leva 2 se serve |
| Leva e margine | leva effettiva fra 1 e 2, margine isolato per il calcolo della liquidazione (mark price, margine di mantenimento 2,5%) |
| Costi | commissione 0,05% per lato, slippage 0,02% per lato, funding storico ai settlement (8h) |

**Motivo economico (dalla fonte, Bollinger 2001).** I periodi di volatilità bassa precedono
espansioni; la direzione con cui il prezzo esce dalla strettoia indica il movimento. Chi opera:
ordini fermi sopra e sotto un intervallo stretto, che si eseguono in fila quando il prezzo esce.
La variante short guarda solo le uscite verso il basso.

**Cosa il bot non può fare così com'è (fatti del Passo 0).** Il bot non esegue strategie fuori
dal registro scritto dal suo gate; dal vivo ha indicatori a 1h (va bene); lo stop a 3 ATR supera
il tetto del 6% del bot in 13 trade su 130 in costruzione; l'orizzonte di 12 barre sta sotto le
96 del bot. Serve l'aggiunta «coppia del protocollo» del Passo 0.
