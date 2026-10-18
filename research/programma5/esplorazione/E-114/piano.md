# E-114 — I fattori fra monete sulle 100 monete più scambiate, periodo C2 (fase 2)

Piano scritto e committato il 18 ottobre 2026 **prima del calcolo** (REGOLE.md, sezioni 6bis, 7 e 7bis). Periodo C2; le
100 monete di `universo_top100.json`; barre di un'ora; programma `strumenti/esplora_fattori.py`.

## Perché

Le idee della fase 2 fin qui erano long dopo un movimento, e su V2 hanno fatto quanto il mercato. Un portafoglio **long
le monete con un carattere e short quelle col carattere opposto** non dipende da dove va il mercato: guadagna solo se il
carattere dice qualcosa. La letteratura sulle cripto (per esempio Liu, Tsyvinski e Wu, «Common Risk Factors in
Cryptocurrency», 2022; i lavori sull'effetto «lotteria» delle monete con i salti più grandi) trova premi per volatilità,
salti estremi, liquidità e momento; qui si misurano sulle 100 monete di oggi, dopo i costi.

## Le famiglie (portafoglio come G2 di E-111: long le 10 prime e short le 10 ultime, almeno 40 monete in fila, metà capitale per parte)

Il carattere si misura alla chiusura dell'ora di decisione con le 720 ore prima (30 giorni):

| Famiglia | Carattere | «Segue» = long chi ne ha di più |
|---|---|---|
| G7 | volatilità (deviazione standard dei rendimenti orari) | long le più volatili |
| G8 | beta con BTC | long le più legate a BTC |
| G9 | salto massimo (il rendimento di 24 ore più alto dei 30 giorni) | long le «lotterie» |
| G10 | illiquidità (media di \|rendimento orario\| / volume in USDT dell'ora) | long le meno liquide |
| G11 | distanza dal massimo dei 30 giorni (log prezzo − log massimo) | long le più vicine al massimo |
| G12 | asimmetria dei rendimenti orari | long le più asimmetriche a destra |

h = 24 e 72 ore (decisioni ogni 24 o 72 ore, dalle 00:00 UTC): **12 celle** (24 con i due versi).

## Criteri di promozione

Come G2-G5 di E-111: |lordo| ≥ 0,30% a periodo (per unità di capitale; un giro costa circa 0,13%), stesso segno in ogni
semestre di C2 con almeno 20 periodi, contributo col segno giusto su almeno il 70% delle monete con almeno 10 periodi
nel portafoglio (almeno 20 monete), |t| ≥ 3, almeno 100 periodi. Al massimo 3 idee J; un'idea promossa ha bisogno del
simulatore di portafoglio nel motore a minuti (da scrivere con i test) prima di C2 e V2. Nessuna di queste famiglie è
stata provata su V2.

**Dichiarato**: prima di committare questo piano ho lanciato il programma una volta sulle 24 monete della fase 2 (5 per
parte, almeno 12 in fila) per controllare che girasse: nessuna delle 12 celle oltre |t| 1,3 (la più alta: G12 h72,
+0,24% a periodo). Il piano e i criteri sopra non sono cambiati dopo.
