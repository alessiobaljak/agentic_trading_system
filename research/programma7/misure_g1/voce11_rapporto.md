# Voce 11: perché il demo fa meglio del paper dall'8 novembre (13 novembre 2026)

Solo misura. Script: `voce11_demo_contro_paper.py` (`python3 -m research.programma7.misure_g1.voce11_demo_contro_paper`, scrive
`voce11_risultati.json`). Fonti: tabelle «demo contro paper» e «funding e spese» di `ops/results/0738`; equity dell'8 novembre da
`0720, 0721, 0724, 0726, 0728`; pesi e prezzi per moneta dal pannello della ricerca con `applica_stima` (funding di novembre corretto).

## Risposta
**Il paper, a regime, sopravvaluta un po' il conto vero (circa 0,05 punti al giorno, tutto funding). Il vantaggio del demo l'8 novembre
non è merito del demo: è un caso, la moneta JCTUSDT.** Il paper vendeva JCT con un peso di 0,39% del conto; il 8 novembre JCT è salita
del 303% (da 0,00283 a 0,01141, volume 1,8 miliardi). Il demo non l'ha aperta perché 0,39% di 1.000 USDT (3,9) è sotto il minimo di
Binance: il paper ha perso, il demo no. Non è una regola ripetibile: un altro giorno la moneta piccola sale e il demo la perde.

## Tabella giorno per giorno (punti di equity; demo meno paper)
Prezzo = resto: differenza di equity meno differenza di funding meno differenza di spese.

| giorno | demo | paper G1 | differenza | funding | spese | prezzo (resto) |
|---|---|---|---|---|---|---|
| 8 nov | -0,48 | -1,32 | **+0,84** | -0,02 | -0,06 | **+0,92** |
| 9 nov | +0,88 | +0,78 | +0,10 | -0,03 | +0,00 | +0,13 |
| 10 nov | -0,13 | -0,22 | +0,09 | -0,15 | 0,00 | +0,24 |
| 11 nov | -1,25 | -1,38 | +0,13 | -0,16 | +0,00 | +0,28 |
| 12 nov | +0,08 | +0,37 | -0,29 | +0,07 | +0,00 | -0,36 |
| 13 nov (fino alle 04:18) | +0,10 | +0,35 | -0,25 | +0,03 | +0,00 | -0,29 |
| **9-13 nov** | -0,32 | -0,10 | **-0,22** | **-0,23** | +0,01 | **0,00** |
| 8-13 nov | | | +0,62 | -0,25 | -0,05 | +0,92 |

Note: il 8 nov il paper è letto alle 00:09 del 9 (10.478,03; tolto 1,01 USD di spese del ribilancio del 9) contro 10.619,33 del
00:21 dell'8; il demo alle 23:24 (995,20). Giorni 9-13 sono i «fine giorno scritto» di 0738. La somma 0,62 contro i 0,75 delle voci
precedenti (-0,81 contro -1,56) è per l'orario di lettura e per la composizione dei giorni; non c'è altro da quadrare.
Funding e spese sono le due tabelle di 0738 (funding incassato demo 0,942 contro paper 1,172 nei giorni 9-13).

## Giorno 8: cosa teneva il paper, cosa il demo
* Paper: ribilancio alle 00:05, 25 lunghi e 27 corti (0720), tutte le monete, conto 10.000.
* Demo: partenza da vuoto alle 00:17, 48 ordini (45 a limite, 3 a mercato), 19 lunghi e 9 corti subito, 24 e 24 alle 04:18 (0721).
  Mancavano ICP (4,36% corto) e 龙虾 (1,87% corto), rifiutata («Invalid symbol»): 6,2% del conto di vendite non fatte; sotto il minimo 2
  variazioni (0,8%). Scarto 7,5% alle 04:18, 9,2% alle 18:22, 8,9% alle 23:24; a 20:23 compare JCT (+2,2%).
* Esposizione: dal modello (motore della prova 148, 1.000 USDT, partenza da zero): lorda voluta 200% (100% lunghi, 100% corti), tenuta 197%
  (lunghi 99,5%, corti 97,2%); netta voluta 0, tenuta +2,3%. L'esposizione non spiega niente: il demo era quasi uguale al paper.
  Dato che manca: l'esposizione vera del demo ora per ora (0720 dice solo 19/9 posizioni alle 00:17 con 48 ordini in attesa).
* Dove sta la differenza di prezzo: nel modello la differenza tra le posizioni tenute e quelle volute vale **+1,14 punti** l'8 nov, di cui
  **+1,17 solo JCT** (peso voluto -0,39%, tenuto 0; rendimento +302,9%); tutto il resto -0,03. ICP mancante pesa -0,005 (nel modello ICP
  è tenuta; nel demo no: ICP l'8 nov ha guadagnato +0,18 per il paper, quindi mancarla è costato, non guadagnato). Dalle misure vere:
  +0,92 di prezzo. Il modello arriva a 0,2 punti dal misurato.
* Spese: demo 0,074% contro paper 0,014% (la costruzione da vuoto: 2.289 USDT scambiati, commissione 0,73 USDT, 0738): -0,06.
  Funding: -0,02.
* Il percorso nell'8 nov (equity demo contro paper G1, da 0720/0721/0724/0726/0728): 00:2x -0,04 / 0; 04:xx +0,18 / +0,36; 18:xx
  -0,52 / -2,07; 20:xx -0,59 / -2,87; 23:24 e 00:09: -0,48 / -1,32. Il vantaggio del demo arriva a +2,3 punti alle 20:23 e si ridimensiona a
  +0,84 a mezzanotte: il paper recupera +1,6 punti dalle 20:09 alle 00:09 mentre il demo resta fermo. Il recupero non è spiegato dalla
  candela giornaliera di JCT (a fine giorno è ancora +303%). Servono i prezzi a un'ora di JCT l'8 nov e l'equity del paper ora per ora
  (letture nuove dalla macchina, elenco sotto).

## Giorni 9-13 (a regime)
* Prezzo: somma 0,00 (da +0,28 a -0,36 al giorno: oscilla, non ha segno). Il modello dà per i giorni 9-11 un divario di prezzo
  +0,10, -0,29, +0,05 (somma -0,14), il misurato +0,13, +0,24, +0,28: la parte di prezzo giorno per giorno non si spiega con i soli minimi
  e resta rumore di orario (letture non alla stessa ora) fino a prova contraria.
* Funding: demo meno paper -0,23 su 5 giorni: il demo incassa il 20% in meno (0,942 contro 1,172). Le monete mancanti (ICP fino al 10,
  龙虾, IRYS) spiegano al più un terzo (già in 0738 e `gate2/reports/2026-11-12-G1-funding-commissioni.md`); il resto è fuori
  da questa misura.
* Spese: demo 0,027 contro paper 0,038: +0,011.

## Risposta alla domanda della voce
* **A regime (9-13 nov): il paper sopravvaluta il conto vero di 0,22 punti in 5 giorni (circa 0,045 al giorno)**, quasi tutto funding
  (-0,23); il prezzo è pari. Con 5 giorni, l'oscillazione giornaliera 0,20 (0738): per ora è un ordine di grandezza, non una stima stabile.
* **Alla partenza (8 nov): il paper sottovaluta di 0,84-0,92 punti, per una moneta sola (JCT) sotto il minimo di Binance, non per
  struttura.** Tolto JCT (o tolto il caso), la partenza dal vuoto costa 0,06 di spese in più e quasi nulla di prezzo.
* Il vantaggio del demo (+0,75 al 13 nov) non va letto come «il demo fa meglio»: +0,62 sono un caso di un giorno, -0,22 sono il costo
  vero a regime. Per i soldi veri: contare circa -0,05 punti al giorno del paper (~-20% del funding) e non contare sul caso del minimo.

## Cosa manca (letture nuove da chiedere alla macchina)
1. Equity del paper G1 e del demo ogni ora l'8 novembre (e il prezzo a un'ora di JCTUSDT, candele da 1 h, 8 nov): per spiegare il recupero
   del paper dalle 20:09 alle 00:09.
2. Il peso di JCTUSDT nel paper G1 e se il demo aveva davvero zero JCT (ordine saltato per minimo): posizioni per moneta del demo
   dell'8 nov (oggi la macchina mostra solo oltre il 2%).
3. Per 龙虾: rendimento dell'8 nov (non è nel pannello della ricerca).
