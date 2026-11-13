# Voce 10: il giorno non spiegato del 30 ottobre (13 novembre 2026)

Script: `voce10_giorno_30_ottobre.py`; numeri: `voce10_risultati.json`. Solo misura, nessuna prova, nessun cambio.

## Risposta corta
Il «30 ottobre» del confronto è un'etichetta sbagliata: la differenza sta nella finestra che parte il **29 ottobre** (dal ribilancio del 29
a quello del 30). Dentro quella finestra il paper fa **+4,40%** e la ricerca **+2,75%**: 1,65 punti in più. Tutte le altre finestre dal 26
ottobre combaciano entro 0,14 punti. Difetto o effetto atteso: **non si può ancora dire**. Mancano i prezzi per moneta del paper e del demo.

## Numeri
Fonte paper: equity scritta dal bot al ribilancio (dopo i costi) in `ops/results/0674, 0675-0679` (righe «[paper_g1] ribilancio del ...»),
rendimento finestra = (equity del ribilancio dopo + suoi costi) / equity prima. Fonte ricerca: pannello, funding vero, ordini limite,
pesi con la stessa partenza del 23 ottobre di `gate2/exports/ricalcolo_g1_ricerca.py` (i pesi hanno memoria).

| finestra (dal ribilancio del) | paper | ricerca | differenza |
|---|---|---|---|
| 26 ott | +2,70 | +2,72 | -0,03 |
| 27 ott | -1,70 | -1,76 | +0,06 |
| 28 ott | -0,99 | -0,85 | -0,14 |
| **29 ott** | **+4,40** | **+2,75** (prezzo 2,60, funding 0,16, spese 0,01) | **+1,65** |
| 30 ott | +1,59 | +1,46 | +0,14 |

- Perché il confronto diceva «30 ott»: la tabella giornaliera del demo e del paper usa l'ultimo valore scritto in ogni giorno, non
  l'equity del ribilancio. Il guadagno della finestra del 29 (+4,40) si spalma fra «29 ott» (+2,25) e «30 ott» (+3,41: circa +2,1 del 29 più
  circa +1,3 del 30). La ricerca ha un giorno per finestra (29: +2,75; 30: +1,46). Quindi il 3,41 contro 1,46 mette a confronto cose diverse.
- Pesi del 29 (ricerca): 24 comprate, 22 vendute. Il paper ha lo stesso numero di monete (log: «long 24, short 22»; 30 ott: 22 e 25, uguale).
  Il paper e la ricerca avevano gli stessi pesi massimi anche il 31 ott (TRX +12,7, BTC -10,6/-10,8). Pesi per moneta del paper il 29: non letti.
- Nella ricerca il 29 ottobre **TRXUSDT pesa +34,7%** e sale +7,2%: da solo +2,50 punti dei +2,60 di prezzo. Le altre monete si compensano
  (ALGO -0,61, HYPE -0,60, USELESS +0,59, SOL +0,57, XRP +0,54). Il 30 TRX pesa +17,7% e scende -6,9% (-1,23).
- Funding: nella ricerca +0,155 (29) e +0,162 (30), il funding è vero. Sul demo +0,059% (29) e +0,224% (30) in giornata (`0703`). Funding
  del paper per giorno: non scritto prima del 6 novembre, quindi non confrontabile.
- Monete in uno e non nell'altro: nel paper l'universo è 100 come nella ricerca; non ho i nomi del paper. Demo: 44 ordini, 1 rifiutato il 30
  (`0678`); la moneta rifiutata di quel giorno non è nominata. Il demo era a 4.992 USDT, quindi minimi pesanti solo sulle monete piccole.

## Cosa non è spiegato
1. **Il prezzo d'ingresso e di uscita**: il paper entra al prezzo mark delle 00:05 (`bot/portafoglio/f5.py`, riga 11), la ricerca all'apertura
   delle 00:00. Con TRX al 34,7% basta un movimento di pochi punti fra 00:00 e 00:05 per muovere la finestra, ma 1,65 punti vorrebbero circa
   +4,8% di TRX in cinque minuti: non lo posso verificare. Le candele da 1 minuto del periodo A sono chiuse dal guardiano di `motore5.py`
   (serve una regola congelata): non l'ho aggirato.
2. **Il demo** fa +5,34 sui due giorni (29+30), la ricerca +4,21, il paper +5,66: anche il demo, che entra con ordini limite alle 00:18, sta sopra
   la ricerca. Questo fa pensare a un effetto dei prezzi di inizio giornata (comune a paper e demo), non a un difetto del solo paper. È un'ipotesi.
3. Dopo il 23 ottobre il gate2 aveva visto circa +1,2 punti di paper sopra la ricerca: qui +1,65 sono quasi tutti in questa finestra, quindi lo
   «scarto dopo il 23 ottobre» e il «giorno 30» sono lo stesso fatto.

## Cosa chiedere alla macchina (per chiudere)
- Dall'archivio del bot (`/portafoglio/f5g1`, il diario delle entrate e delle uscite scritto in `bot/portafoglio/f5.py` righe ~454-461 e
  580-594): per il 29, 30 e 31 ottobre, per moneta: quantità, prezzo mark usato al ribilancio, peso. Non c'è oggi un comando di `ops/` che lo
  stampi: va aggiunto alla lista bianca (lo decide la sessione principale).
- Per il demo: le esecuzioni per moneta del 29-30 ottobre (`/fapi/v1/userTrades`: prezzo, quantità, ora). `state_snapshot` stampa solo
  i totali per giorno (`esecuzioni_per_giorno`).
- Con i prezzi del paper: rifare la finestra 29 con questi prezzi invece delle aperture della ricerca; se il +1,65 sparisce, è l'orario
  (effetto atteso); se resta, è un difetto del paper (prezzo mark o quantità), da dare a chi possiede il codice del paper.

## Verdetto
Non ancora classificabile. Fatto: il «30 ottobre» è un'etichetta; la differenza vera è +1,65 nella finestra del 29, con TRX al 34,7%.
Nessuna variante.

## Nota della sessione principale (13 novembre, 17:00 UTC): il prezzo di TRX nei primi minuti
Lettura pubblica di Binance (`/fapi/v1/markPriceKlines` e `/fapi/v1/klines`, TRXUSDT, 1 minuto), fatta dalla sessione principale per
il solo confronto dell'esecuzione (non è una prova e non usa il caricatore del programma 5): il 29 ottobre apertura 0,32960 alle 00:00,
mark 0,32932 alle 00:05; il 30 ottobre apertura 0,35334 alle 00:00, mark 0,35721 alle 00:05 e 0,35922 alle 00:09. Da apertura ad
apertura (ricerca) TRX fa +7,20%; dal mark delle 00:05 all'equity delle 00:09 del giorno dopo (paper) +9,08%. Con il peso della
ricerca (34,7%) l'orario spiega circa **+0,65 punti** dei +1,65 della finestra del 29 ottobre: un effetto atteso, non un difetto.
Il resto (circa +1 punto) resta da spiegare con i pesi e i prezzi per moneta del paper, che le risposte della macchina non hanno.
