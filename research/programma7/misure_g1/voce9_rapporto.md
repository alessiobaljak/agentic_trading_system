# Voce 9: lo scarto del demo a 1.000 USDT (13 novembre 2026)

Solo misura. Script: `voce9_scarto_conto_piccolo.py` (si lancia con `python3 -m research.programma7.misure_g1.voce9_scarto_conto_piccolo`,
scrive `voce9_risultati.json`). Fonti: `ops/results/0721, 0724, 0728, 0731, 0733, 0735, 0736, 0738` (righe «posizioni vere contro
volute», «ultima decisione», «peso nel paper G1 delle monete rifiutate o mancanti», tabelle demo-paper); definizione dello scarto in
`bot/portafoglio/demo_binance.py` (`confronta`: somma dei valori assoluti di vero meno voluto, in % del conto, letta ogni ora;
`sotto_il_minimo`: somma delle variazioni che il ribilancio non manda perché sotto quantità o valore minimo, solo per le monete che il
demo ha).

## Risposta (a): da dove viene lo scarto
Quasi tutto da due cause, che si sommano quasi esatte: **variazioni sotto il minimo** + **monete che il demo non ha**.
Scarto misurato dopo ogni decisione, in % del conto (sotto il minimo = decisione del giorno; mancanti = peso nel paper di ICP, 龙虾, IRYS):

| ribilancio | scarto misurato | sotto il minimo | monete mancanti | somma | non spiegato |
|---|---|---|---|---|---|
| 8 nov (23:24) | 8,9 | 0,8 | 6,23 (ICP 4,36 + 龙虾 1,87) | 7,03 | **+1,87** |
| 9 nov (23:31) | 13,9 | 6,7 | 6,93 (ICP 4,57 + 龙虾 1,95 + IRYS 0,41) | 13,63 | +0,27 |
| 10 nov (23:39) | 15,8 | 9,1 | 6,86 (ICP 4,53 + 龙虾 1,92 + IRYS 0,41) | 15,96 | -0,16 |
| 11 nov (23:47) | 12,2 | 10,0 | 2,32 (龙虾 1,90 + IRYS 0,42) | 12,32 | -0,12 |
| 12 nov (15:52) | 11,8 | 10,4 | 2,28 (龙虾 1,86 + IRYS 0,42) | 12,68 | -0,88 |
| 13 nov (03:55) | 10,2 | 8,2 | 2,16 (龙虾) | 10,36 | -0,16 |

Lettura:
* I numeri 8,9 → 13,9 → 15,8 → 12,2 del conto sono quindi: la salita dall'8 al 10 è **sotto il minimo (0,8 → 9,1)**; la discesa all'11 è
  **ICP che esce dal paper** (-4,5), mentre le variazioni piccole saltate restano a 8-10%. Il 13 nov 10,2 = 8,2 + 2,16.
* Le monete mancanti pesano 6,2-6,9 fino al 10 nov (ICP +龙虾+IRYS) e 2,2-2,3 dopo (solo 龙虾, rifiutata ogni giorno: «Invalid symbol»,
  e IRYS fino al 12).
* Il sotto-minimo giornaliero (6-10% del conto) è stabile dal 9 nov: è lo stato di regime a 1.000 USDT, non cresce (atteso dalla prova 148
  per 1.000 USDT: eseguibile il 23% delle variazioni; misurato sui cinque giorni 60 ordini su 276, il 22%: voce 8 del diario).
* **Ordini non eseguiti**: il demo ne conta 39 su 668 non eseguiti a limite (629 su 668, `0738`), ma il dato è cumulato da tutte le fasi
  (anche 280 USDT), quindi non si assegna a un giorno. Nel «non spiegato» dei giorni 9-13 (da -0,9 a +0,3) non c'è traccia di un
  effetto grande: gli ordini non eseguiti, gli arrotondamenti al passo e le variazioni dei prezzi pesano al massimo qualche decimo.
* Non spiegato: **8 nov, +1,9 punti** (a 04:18 era 7,5, a 18:22 9,2, a 23:24 8,9: cresce durante la giornata; la decisione di quel giorno
  fu la prima da zero e il 8 nov ci fu un riavvio, `0724`). Con i soli numeri delle risposte non si può dire se erano ordini non
  arrivati o altro: servirebbe lo scarto per moneta (oggi la macchina mostra solo le monete oltre il 2%).
* Il 12 nov alle 15:52 lo scarto era 0,9 sotto la somma: somme di valori assoluti non si sommano esattamente se una variazione
  saltata e una moneta mancante cadono sulla stessa moneta o il prezzo si è mosso; non è una causa.

## Risposta (b): quanto costa in rendimento
**Due misure; la prima (demo contro paper) dà il costo, la seconda (ricerca) resta lontana dal paper e non decide.**

1. **Dal demo e dal paper** (tabelle di `0738`, giorni 9-13 nov, in punti di equity): demo -0,33%, paper -0,10%, cioè demo **-0,23**.
   Quel -0,23 è quasi tutto il funding: incassato demo 0,942 contro paper 1,172 (differenza **-0,230**); spese demo 0,027 contro 0,038
   (+0,011). Resto, cioè prezzo, ≈ 0,00 su cinque giorni. Quindi lo scarto non ha dato un costo visibile sul prezzo; il costo che si vede è il
   funding incassato più basso, da cui le monete mancanti spiegano al più un terzo (`gate2/reports/2026-11-12-G1-funding-commissioni.md`).
   Limite: il giorno 8 nov (demo da zero, spese demo 0,074 contro 0,014 del paper) non è nei cinque giorni; i giorni delle due tabelle
   sono di fine giorno scritto, non alla stessa ora esatta.
2. **G1 ricalcolato con i minimi a 1.000 USDT sugli stessi giorni** (`conto_vero` del motore della prova 148 con i filtri veri, banda
   vuota dal 23 ott come il paper, partenza da zero l'8 nov, giorni 8-11 nov; il pannello della ricerca arriva all'11).
   **Correzione del 13 nov (sessione principale)**: la prima versione dava un ricalcolo lontano dal paper per un errore di dati, non per
   dati «provvisori». Nel pannello (`sc.pannello()`) il funding di novembre non esiste: il file mensile non è uscito e il pannello ripete il
   valore del 1° novembre dal 2 all'11 (Bitcoin 1,59 punti base ogni giorno, controllato nello script: riga `controllo_funding_btc_1_11_nov_pb`
   di `voce9_risultati.json`). Il segnale di G1 usa il funding, quindi pesi e funding pagato erano falsi. Rifatto con `applica_stima(pan)`
   (`research/programma6/paper/aggiorna.py`, modifica il pannello sul posto; funding stimato dal premio, 588 monete; Bitcoin ora 2,9, 2,7, 3,0, 1,76,
   3,0, 2,47, 1,06, 2,35, 3,0, 2,35, 1,79 punti base).
   * Pesi: ora lunghi/corti 27/28 il 9 nov (paper 29/27), 28/27 il 10, 29/27 l'11; **ICP entra nei pesi** (-3,9/-4,2% dal 6 al 10 nov, zero l'11:
     come nel paper, dove ICP pesa -4,4/-4,6% e il 11 esce). Prima era assente.
   * Controllo 6-7 nov (ricerca): +2,07% e +0,18% (paper +2,08% e +0,30%, già verificati nel confronto del 9 nov): tornano.
   * 8-11 nov, senza minimi: -1,91, -1,23, +0,93, -2,08, **somma -4,28%**; con i minimi a 1.000 USDT: **-3,25%**. Paper nello stesso tempo (8 nov
     → 12 nov 00:09) **-2,08%**, demo **-0,99%** (`0735`). **Resta lontano**: la ricerca è 2,2 punti sotto il paper, e prima era 3 sotto. Il
     confronto assoluto con il demo non è valido nemmeno ora. La differenza con minimi meno senza (+1,03) è di segno favorevole ai minimi e
     viene da posizioni diverse (ICP, quote saltate), non è un costo: non la leggo come guadagno.
   Resta da capire perché la ricerca sia ancora sotto il paper sull'8-11 (pesi quasi uguali, funding ora stimato): il funding stimato è un
   valore del premio, non quello versato; la ricerca tiene da apertura ad apertura (00:00), il paper dalle 00:05; da guardare insieme con la
   sessione principale. Non lo stimo a occhio.

## Cosa resta non spiegato
* 8 nov: 1,9 punti di scarto (sopra).
* Il costo dei minimi misurato con la ricerca: serve il funding vero di novembre (file mensile non ancora uscito) e lo scarto per moneta dalla macchina (non solo oltre il 2%).
* Perché la ricerca resta 2,2 punti sotto il paper nell'8-11 nov, anche con il funding stimato.

## Proposta (non provata)
Nessuna regola nuova: lo scarto da conto piccolo è il previsto e non costa visibile. Due richieste di dati alla sessione principale:
(1) il funding vero di novembre nel pannello (appena esce il file mensile) e capire il residuo ricerca-paper, poi rilanciare questo script; (2) per i prossimi
scarti, una riga della macchina con lo scarto per moneta intero (non solo oltre il 2%) per chiudere il «non spiegato».
Resta ferma la voce 5 del piano: una banda più larga si prova nel conto solo se questa misura, con dati veri, mostra un costo.
