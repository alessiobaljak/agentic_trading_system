# Scalping sulla volatilità: i risultati della prima analisi

Calcolati il 18 ottobre 2026 dopo le regole (`regole.md`, commit `71576ba5` delle 14:19 UTC, prima dello scarico). Dati:
candele da 1 minuto dei perpetui BTCUSDT, ETHUSDT, SOLUSDT, XRPUSDT, BNBUSDT e DOGEUSDT dal 2020-01-01 (o dal primo mese
disponibile: SOL da settembre 2020, DOGE da luglio 2020, BNB da febbraio 2020) al 2022-12-31: 201 file mensili, tutti con il
CHECKSUM di Binance verificato (`scarico.json`). Script `analisi.py`, numeri in `risultati.json`. Python 3.11.17, numpy
1.26.4, pandas 2.2.2.

**Cambiamenti allo script dopo il primo giro, dichiarati**: ho aggiunto i risultati di tutte le monete insieme divisi per
direzione dell'evento e per anno. Le regole li prevedevano («si riporta anche per anno e per direzione»), ma il primo
giro li dava solo moneta per moneta. Il generatore di numeri casuali è lo stesso, ma con più ricampionamenti in mezzo: gli
intervalli dell'ultimo giro differiscono di qualche millesimo da quelli del primo.

## Cosa sono le «esplosioni»

Un movimento di 5 minuti più grande di 4, 8 o 16 volte il movimento tipico di 5 minuti del giorno prima. Nei tre anni,
sulle sei monete: **59.967** eventi di livello 4, **13.630** di livello 8, **2.239** di livello 16 (dopo ognuno, 60 minuti
senza un altro evento dello stesso livello). Entrata immaginaria all'apertura del minuto dopo.

## In una pagina

1. **Dopo un'esplosione il prezzo si muove molto, ma in media non sa dove.** Nei 15 minuti dopo un evento di livello 8, il
   massimo a favore mediano è fra lo 0,37% (BTC) e lo 0,65% (SOL), e il massimo contro quasi uguale (0,34-0,65%); a 15
   minuti il prezzo si è mosso più del costo di un giro nel 78-89% degli eventi. Ma la direzione, su tutte le monete
   insieme, è quasi nulla a ogni orizzonte, per i livelli 4 e 8: per esempio livello 8 a 15 minuti +0,021% (intervallo
   −0,011; +0,052), contro un costo di un giro di 0,12-0,14%.
2. **Nei momenti agitati i movimenti di 5 minuti tornano un po' indietro, ma troppo poco.** Nel decimo di tempo più
   agitato il prezzo si muove in 5 minuti fra lo 0,27% (BTC) e lo 0,63% (DOGE), cioè 2-5 volte il costo di un giro; la parte
   prevedibile (un leggero ritorno indietro) vale fra 0,002% e 0,026%: da 5 a 60 volte meno del costo a mercato, e meno
   anche del costo con due ordini limite (0,04%). Vale per tutte e sei le monete.
3. **L'unica eccezione: dopo i crolli estremi, il prezzo risale.** Dopo un crollo di livello 16 (1.327 eventi in 416
   giorni), nei 60 minuti dopo il prezzo risale in media dello **0,48%** (intervallo 0,23-0,75%); al netto del costo di un
   giro a mercato **+0,35%** (intervallo +0,09; +0,62). Dopo le salite estreme, niente (−0,22% al netto, intervallo −0,47;
   +0,01). **Ma dipende dall'anno**: il rimbalzo a 60 minuti è dello 0,43% nel 2020, dell'1,18% nel 2021 e solo
   dello 0,10% nel 2022 (sotto il costo di un giro): nei mercati che salgono i crolli rimbalzano, in quelli che scendono
   molto meno.

## Il confronto con il caso

Minuti presi a caso senza esplosioni, con un segno a caso: il movimento a 5, 15 e 60 minuti è fra −0,018% e +0,010% su
ogni moneta (`risultati.json`, «caso»). La deriva dei tre anni non spiega i risultati sopra.

## Cosa abbiamo capito

* **La volatilità da sola non basta allo scalping.** Il prezzo si muove abbastanza da pagare i costi, ma con le sole
  candele la direzione resta un lancio di moneta: seguire o contrastare l'esplosione non paga un giro.
* **C'è un fenomeno vero e grande nei crolli estremi**: il rimbalzo, probabilmente le vendite forzate (liquidazioni a
  catena) che spingono il prezzo troppo in basso. Ma nel 2022 era quasi sparito. Per farne una strategia bisogna capire
  **quali** crolli rimbalzano: è un'informazione che le candele non hanno e che i dati sulle posizioni aperte (quante
  posizioni si chiudono durante il crollo) possono dare.
* **Attenzione al caso**: su 36 combinazioni (3 livelli, 6 orizzonti, 2 direzioni) ne ho guardate molte; il rimbalzo dopo i
  crolli estremi è coerente a 30 e 60 minuti e su ETH, SOL e DOGE, ma resta un'ipotesi finché non lo conferma il 2023,
  che nessuno ha ancora usato per questa domanda.

## Limiti

* Sei monete grandi, 2020-2022 (un rialzo forte e un ribasso), solo prezzi di scambio a 1 minuto: niente libro degli ordini,
  niente scambi uno per uno.
* L'entrata all'apertura del minuto dopo e l'uscita alla chiusura del minuto dell'orizzonte, senza stop: è una misura del
  movimento, non una strategia.
* I costi sono quelli del 2023 per lo scarto di prezzo, ottimisti nei crolli (quando il libro degli ordini si svuota lo
  scarto cresce): proprio dove sta l'unico risultato positivo. Per questo, prima di tutto, va misurato.
