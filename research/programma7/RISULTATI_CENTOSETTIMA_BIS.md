# Risultati della prova 169: «G1 o F5 secondo il mercato» (direzione del Bitcoin, 30 giorni)

## Riepilogo
Esito secondo il criterio scritto: **NON PROMETTENTE, tutte e due** (Sharpe corretto 0,61 per A e 0,72 per B, sotto 0,80). Ogni anno positivo e t sopra 3 sono rispettati da entrambe (t 4,78 e 5,05). Nessuna delle due batte G1 o F5 in modo netto: A rende meno di G1 (−1,4 punti l'anno), B un po' di più (+2,0 punti l'anno) ma con le spese dei cambi sopra la metà del guadagno (fallimento utile previsto dalle regole). Codice non committato.

## La prova come è scritta e scala di tempo
Regole: `CENTOSETTIMA_BIS.md` (commit d59c79d, chiusura 160d509; la «Chiusura della verifica» vale su tutto). Pesi di G1 quando ER (Kaufman, 30 giorni, BTCUSDT, solo chiusure fino a ieri) è maggiore o uguale alla soglia, pesi di F5 (giornalieri, costanti dal lunedì) altrimenti; A soglia 0,20, B soglia 0,30; nessuna isteresi. Scala: somma dei giorni per settimana (lunedì 4 gennaio 2021 – 4 ottobre 2026, 300 settimane; ultimo lunedì 28 settembre 2026). Spese del motore ufficiale con ordini a limite, anche al cambio di stato.

## Implementazione
`research/programma7/centosettima_bis.py` (importa `centosesta.py` senza toccarlo), non committato. Esecuzione: `python3 -m research.programma7.centosettima_bis`. Seme: nessuno (0 nel registro). Risultati completi: `risultati_centosettima_bis/esame.json`, `settimane_A.csv.gz`, `settimane_B.csv.gz`, `giorni_A.csv.gz`, `giorni_B.csv.gz` (con colonna `direzione`), `avanti.csv`.

## Varianti provate
2 (A e B), nessun errore. Registro: `research/trials/centosettima_bis.csv` (2 righe più intestazione).

## Risultati (300 settimane; rendimento annuo del netto, Sharpe su 52 settimane)
| | Sharpe | annuo | discesa max | spese annue | Sharpe corr. | t |
|---|---|---|---|---|---|---|
| A (0,20) | 1,99 | +52,7% | −26,8% | 6,6% | 0,61 | 4,78 |
| B (0,30) | 2,10 | +56,1% | −25,4% | 5,6% | 0,72 | 5,05 |
| G1 (serie salvata) | 1,97 | +54,1% | −28,8% | 6,5% | | |
| F5 (serie salvata) | 1,88 | +55,4% | −26,9% | 4,9% | | |
| solo F5 nel motore giornaliero | 1,88 | +52,0% | −23,6% | 4,4% | | |

Per anno (netto medio annuo): 
| anno | A | B | G1 | F5 |
|---|---|---|---|---|
| 2021 | 109,4% | 123,1% | 109,9% | 122,7% |
| 2022 | 26,4% | 29,3% | 31,2% | 31,7% |
| 2023 | 15,7% | 19,9% | 7,7% | 30,7% |
| 2024 | 70,7% | 74,2% | 68,0% | 65,8% |
| 2025 | 63,6% | 62,6% | 72,5% | 50,6% |
| 2026 (39 sett.) | 22,6% | 17,2% | 28,5% | 22,8% |

Giorno peggiore (netto): A e B −9,94% (30 gennaio 2021); G1 −8,50% (stesso giorno); F5 giornaliera −9,94%. Settimana peggiore: A −9,11% (1 giugno 2026), B −9,50% (stessa), G1 −9,36% (stessa), F5 −14,71% (26 febbraio 2024). Ordini: A 114.965, B 112.912; G1 rifatta 117.037, F5 giornaliera 109.751.
Famiglie (conto per famiglie, mazzo come sta con la F5 vecchia, backlog P35): 291 serie, 200 famiglie; gruppi di A e B contengono G1, G11, F5 ecc.

**Cambi di stato e spese**: A 247 cambi in 2100 giorni (40, 45, 60, 44, 34, 24 per anno 2021-2026), spese dei cambi 2,04% l'anno su 6,6% di spese totali; B 159 cambi (33, 40, 24, 22, 20, 20), spese dei cambi 1,32% l'anno su 5,6%. Fallimento utile: A nessun guadagno su G1 (−1,4 punti); B guadagno +1,97 punti l'anno contro spese dei cambi 1,32 (più della metà: scatta).

**Quota di giorni con direzione per anno** (2021…2026): A 51%, 43%, 54%, 40%, 35%, 46%; B 25%, 21%, 33%, 24%, 18%, 35%. Anni «con direzione» (quota ≥ 50%): A 2021 e 2023; B nessuno. Descrittivo: con A il 2023 (anno con direzione secondo la misura) è proprio quello dove G1 va peggio, il contrario dell'ipotesi.
**Netto per stato** (somma dei netti giornalieri, 2021-2026): A con direzione 0,98 (G1 1,02, F5 giornaliera 0,89; 939 giorni), senza 2,06 (G1 2,12, F5 2,10; 1161 giorni). B con 0,54 (G1 0,57, F5 0,29; 538 giorni), senza 2,70 (G1 2,57, F5 2,71; 1562 giorni). Quindi nei giorni con direzione F5 rende meno di G1, nei giorni senza direzione G1 e F5 quasi uguali: la differenza fra le due strategie non si lega bene a ER.

## Variante migliore e sensibilità
B ha Sharpe corretto più alto (0,72), ma sotto la soglia. Le due soglie danno risultati vicini (annuo 52,7% e 56,1%, tutti gli anni positivi in entrambe), quindi non c'è forte sensibilità alla soglia; tuttavia entrambe falliscono l'esame. Non provate altre soglie.

## Anomalie e possibili errori
* Chiusure di BTCUSDT mancanti dal 4 dicembre 2020 al 4 ottobre 2026: nessuna; nessun giorno senza candele; ER calcolabile in tutti i 2100 giorni. Prova dello sguardo avanti: ER identico azzerando i dati dal giorno stesso in poi (assert passato).
* Scarto dei motori sul netto settimanale: G1 0,0073 (soglia 0,01), F5 0,0018 (soglia 0,005): entro i limiti. G1 rifatta dà Sharpe 1,98 contro 1,97 salvata.
* La F5 nel motore giornaliero (pesi costanti con riequilibrio pagato, ordini a limite) non è la F5 settimanale: correlazione 0,976 con la F5 salvata, scarto medio −0,07 punti a settimana, scarto massimo 6,6 punti in una settimana; annuo 52,0% contro 55,4%. Quindi il confronto con F5 vale per il rendimento, non per le spese.
* Il funding degli ultimi giorni del pannello è stimato (nota INDEX); riguarda la sola parte in avanti, che non entra nel conto.

## Varianti non previste che proporrei (non eseguite)
Nessuna per ritoccare la soglia. Se si vuole l'idea: misura sul funding (quanto cambia la classifica), già scritta come idea nel testo delle regole, con regole nuove e numero nuovo.

## Parte in avanti (descrittiva)
Il pannello arriva al 23 novembre 2026. ER dal 16 al 23 novembre: 0,435 / 0,440 / 0,462 / 0,485 / 0,541 / 0,615 / 0,537 / 0,495: sopra 0,30 ogni giorno, quindi A e B avrebbero seguito G1 per tutti gli 8 giorni. Dal 31 ottobre al 25 novembre (25 giorni, letture «stato»): G1 reale +1,9%, F5 reale +8,9% (cumulato). Nel periodo 16-24 novembre del paper G1 ha perso e F5 ha guadagnato: la misura sceglieva G1, cioè la strategia sbagliata in quel periodo. Pochi giorni: non giudica.

## Domande aperte
1. Il periodo avanti dei 25 giorni (31 ottobre – 25 novembre) comprende giorni dopo il 23 novembre dove il pannello non arriva; si è tenuto il confronto reale solo come descrizione. Va bene?

## Letture delle regole che ho dovuto scegliere
* «Ogni anno positivo» = anni di calendario 2021–2026, compreso il 2026 parziale.
* «Guadagno su G1» = annuo variante meno annuo G1 salvata (54,1%); spese dei cambi annue = somma delle spese dei soli giorni di cambio divisa per 2100/365 anni.
* Cambio di stato: giorno con stato diverso dal giorno prima (il primo giorno non conta come cambio; le spese di apertura si pagano come in G1).
* Anni «con direzione»: quota di giorni ≥ 50%.
* Controllo della F5 rifatta: per lo scarto dei motori si è usata la F5 settimanale (`te.conto` sui pesi del lunedì, come in 168), non quella giornaliera.
* Confronto per anno: G1 e F5 dalle serie salvate (`risultati_prima`, `risultati_controllo_parita`).
