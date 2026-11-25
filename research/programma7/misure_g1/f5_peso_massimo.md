# F5: peso massimo per moneta e somma dei pesi sul passato (25 novembre 2026)

Domanda 180 di live-path-reviewer (`reviews/reports/2026-11-25-conto-vero-F5.md`), voce P36 di `docs/backlog.md`. Solo misura, nessuna variante.
Script: `research/programma7/misure_g1/f5_peso_massimo.py`; numeri: `f5_peso_massimo_risultati.json`; una riga per settimana: `f5_peso_massimo_settimane.csv.gz`.
Motore: gli stessi pesi di F5 corretto di `research/programma6/controllo_parita.py` (pannello, sigma a 30 giorni, banda 20%/40%, funding a 7 giorni),
300 lunedì dal 4 gennaio 2021 al 28 settembre 2026 (l'ultima settimana completa prima del 4 ottobre).
Deriva: quantità ferme dal lunedì, prezzi di apertura di ogni giorno (giorni 1..7, il 7 è il lunedì dopo, prima di ribilanciare); conto del giorno =
1 - spese del giro + guadagno dei prezzi (senza funding). Limiti: i massimi dentro il giorno non ci sono; il funding è escluso.

## 1. Alla decisione del lunedì
* Peso più alto di una moneta: **43,7%**, BLZUSDT, 5 febbraio 2024. 99° percentile 24,9%, mediana 9,1%. (G1: 47,8%, stessa moneta e stesso lunedì.)
* Somma dei pesi: sempre 200,0% (due lati da 1). Nessun lunedì sopra il 60% né sopra il 200%.

## 2. Durante la settimana (deriva)
* Peso più alto di una moneta: **44,9%**, BLZUSDT, settimana del 5 febbraio 2024, giorno 3. 99° percentile 34,2%, mediana 9,7%.
* Somma dei pesi più alta: **397,2%**, settimana dell'8 febbraio 2021, giorno 6 (il conto quel giorno era a 0,83 del lunedì: gli short salivano).
  Mediana dei massimi settimanali 209,9%; 90° percentile 231,4%; 99° percentile 268,1%. A fine settimana (giorno 7) il massimo è 364,2%.
  Cinque più alte: 8 feb 2021 (397%), 26 feb 2024 (292%), 5 mag 2025 (285%), 4 gen 2021 (268%), 24 mag 2021 (267%).

## 3. Quante volte si superano i limiti
* 60% per moneta: **0 settimane su 300**, né al lunedì né in settimana (anche sopra il 50%: 0). Il tetto è lontano: il massimo è 44,9%.
* 200% in tutto: al lunedì **0 su 300** (2,0 esatto); in settimana **300 su 300** (anche solo per le spese del giro, che abbassano il conto).
  Sopra 210%: 149 settimane; sopra 225%: 55; sopra 250%: 10; sopra 300%: 1 (8 febbraio 2021).
  Quindi il limite del 200% resterebbe rispettato solo perché si controlla il lunedì sul peso obiettivo; se lo si controllasse sul peso vero in settimana, scatterebbe sempre.

## 4. Caso peggiore: moneta venduta che sale molto
Peggior perdita di una moneta sul conto a fine settimana: **-14,5%**, XRPUSDT, lunedì 25 gennaio 2021: peso -17,9%, salita +81,1%, peso a fine settimana 34,1%.
Poi: ZRXUSDT 1 feb 2021 (salita +99,7%, perdita -13,8%, peso a fine 26,2%); IOTAUSDT 8 feb 2021 (+113,1%, -13,5%, 29,8%);
1000SHIBUSDT 26 feb 2024 (+133,0%, -10,6%, 21,9%); XLMUSDT 4 gen 2021 (+108,3%, -9,1%, 15,5%). Il peso a fine settimana più alto di una moneta venduta è 34,1% (XRP).
Conto più basso in una settimana: 0,833 (8 febbraio 2021). Nessuno stop per posizione: la perdita di una moneta venduta non ha tetto (una moneta che raddoppia fa -100% del suo peso).

## Rischio e idea (non provata)
Il 60% per moneta non è un rischio sul passato (massimo 44,9%). Il rischio è il 200%: il controllo del lunedì non vede la deriva (fino a 397%, 268% al 99° percentile).
Idea per il piano, da non provare ora: se il conto vero userà il tetto del 200% come protezione vera, misurare il peso vero dai prezzi (non dal peso obiettivo) a ogni controllo
e decidere un tetto separato per la somma in settimana (per esempio 300%) o un ribilanciamento a metà settimana; oggi non c'è dato in avanti per sceglierlo.
