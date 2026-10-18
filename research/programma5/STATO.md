# Programma 5: stato e registro delle idee

Regole: `REGOLE.md`. Aggiornato a ogni passo. **Strategie valide finora: 0** (servono 3 per scrivere al proprietario).

## Dove siamo

* 18 ott 2026, sera: regole scritte; candele da 1 minuto e funding delle 12 monete scaricati e verificati; file `metrics`
  in corso (BTC, ETH, SOL, XRP, BNB finiti alle 15:36 UTC).
* I-005, I-006, I-007 (idee a 1 minuto senza interesse aperto) cadute in C: guadagno lordo fra −0,07% e +0,02% a trade,
  contro costi di circa 0,13-0,17%. Lezione: i segnali di pochi minuti sulle candele non pagano i costi; servono
  movimenti più grandi o tenute più lunghe.

## Coda delle idee (in ordine)

| N. | Idea | Perché dovrebbe funzionare | Stato |
|---|---|---|---|
| I-001 | Rimbalzo dopo i crolli fatti di liquidazioni: crollo estremo a 5 minuti con l'interesse aperto che cala | le vendite forzate spingono il prezzo sotto il valore che i compratori pagano; la prima analisi ha visto il rimbalzo (`research/scalping/risultati.md`) | da fare |
| I-002 | Il contrario dopo le salite estreme fatte di short liquidati (interesse aperto che cala) | come I-001, dalla parte opposta | da fare |
| I-003 | Continuazione quando l'esplosione arriva con interesse aperto che cresce (posizioni nuove, non chiusure) | denaro nuovo che entra con una direzione | da fare |
| I-004 | Rapporto long/short dei conti grandi agli estremi, orizzonte 1 giorno | la folla in un verso estremo paga chi sta dall'altra parte | da fare |
| I-005 | Squilibrio degli acquisti aggressivi a 5 minuti durante un'esplosione | chi aggredisce ha informazione o fretta | bruciata in C |
| I-006 | Il prezzo intorno al regolamento del funding quando il funding è estremo | chi chiude prima di pagare il funding sposta il prezzo | bruciata in C |
| I-007 | Le monete dopo BTC al minuto: BTC esplode, le altre seguono in 1-5 minuti | il prezzo di BTC arriva prima nelle altre | bruciata in C |
| I-008 | Premio del perpetuo sullo spot estremo, ritorno nelle ore dopo | l'arbitraggio riporta il perpetuo verso lo spot | da fare |
| I-009 | Rottura dopo la calma con interesse aperto che cresce | la pressione accumulata si sfoga nella direzione delle posizioni nuove | da fare |

## Registro delle idee concluse

| N. | Esito | Numeri (da `idee/I-NNN/C.md`) | Motivo e lezione |
|---|---|---|---|
| I-005 | bruciata in C | netto −0,159% / −0,244% / −0,159% a trade (7.595, 7.595, 1.891 trade); lordo +0,012% / −0,073% / +0,016% | l'intervallo del netto è tutto sotto zero; lo squilibrio degli acquisti aggressivi nell'esplosione non dice la direzione dei minuti dopo più del caso (caso −0,14%) |
| I-006 | bruciata in C | netto −0,182% / −0,165% / −0,169% (5.173, 7.821, 5.090 trade); lordo −0,144% / −0,107% / −0,129% | andare contro il funding estremo prima del regolamento perde sul prezzo quanto un ingresso a caso nella stessa direzione (caso −0,18% / −0,18% / −0,22%): il prezzo segue la tendenza del mese, non il regolamento |
| I-007 | bruciata in C | netto −0,167% / −0,157% / −0,160% (8.445, 8.443, 14.349 trade); lordo +0,007% / +0,017% / +0,013% | le altre monete non restano indietro a BTC in modo sfruttabile: al minuto dopo il ritardo è già recuperato; nessuna moneta positiva |
