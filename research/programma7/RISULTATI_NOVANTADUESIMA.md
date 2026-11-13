# Risultati della prova 154 (la dimensione media dello scambio, idea 140)

## Riepilogo
Esito secondo l'esame scritto prima: **non promettente**, entrambe le varianti (A: 3 giorni su 30; B: 7 giorni su 90). Rendimento netto
annuo A +0,08% (Sharpe 0,00; t 0,01), B -4,7% (Sharpe -0,17; t -0,38). Sharpe corretto per famiglie: circa 0,0001 (A) e 0,00002 (B)
contro 0,80 richiesto. Con il verso al contrario non si recupera nulla di stabile (descrittivo, non una variante).

## La prova come è scritta e scala di tempo
`research/programma7/NOVANTADUESIMA.md`, commit a7c3e08 (regole corrette del 13 novembre, 9 punti chiusi). Segnale S = media di
quote_volume/count sulla finestra corta / sulla lunga; long il quinto con S più alto, short il più basso, banda 20%/40%, inverso della
volatilità a 30 giorni, esposizione come G1 (W, senza beta). Scala: decisione giornaliera alle 00:00 UTC; Sharpe e t sulle settimane (52).

## Implementazione
`research/programma7/novantaduesima.py` (non committato). Lettore di `count` scritto nel file (stessi file e stesse regole di
`seconda.candele`); matrice in cache fuori dal repo. Costi, limite per un'ora, funding: `nucleo.spese_limite` e `an.conto`, come G1.
Controllo su BTC, ETH, SOL: chiusura e volume identici a `seconda.candele` e al pannello (differenza massima 0; 2.506 e 2.243 giorni).
Nessun `count` mancante o sotto 100 su queste tre.

## Varianti provate
2 (A e B), una volta sola, registrate in `research/trials/novantaduesima.csv`. Seme 154.

## Risultati (1.738 giorni con posizioni, dal 1° gennaio 2022 al 4 ottobre 2026, 249 settimane, circa 99,8 monete al giorno con segnale)
| | A | B |
|---|---|---|
| Rendimento netto annuo | +0,08% | -4,7% |
| Discesa più grande (settimane) | -54,6% | -51,3% |
| Sharpe (52 settimane) / t | 0,004 / 0,01 | -0,174 / -0,38 |
| Sharpe giornaliero su 365 giorni | 0,004 | -0,196 |
| Anni (rendimento annuo; 2022, 2023, 2024, 2025, 2026 parziale) | -27,2%, -25,4%, -5,7%, +54,2%, +8,3% | -29,6%, -15,5%, +2,8%, +45,2%, -31,0% |
| Giro medio al giorno | 0,64 | 0,30 |
| Spese annue (con ordine limite) / funding annuo | 11,6% / -2,8% | 5,8% / -5,0% |
| Netto con costi tripli | -23,1% | -16,4% |
| Long da solo / senza i 10 giorni migliori | -9,1% / -37,4% | -13,8% / -43,8% |
| Short da solo / senza i 10 giorni migliori | +9,0% / -28,6% | +8,8% / -28,5% |
| Al contrario (descrittivo): annuo / Sharpe | -22,6% / -0,99 | -8,1% / -0,30 |

Esame: A passa solo «netto positivo»; B nemmeno quello. Falliscono: ogni anno positivo, t da 3, Sharpe corretto, lati senza i 10 giorni.
Sharpe corretto con `corretto_famiglie`: 267 serie, 46 varianti senza serie, 192 famiglie (con A e B in un solo gruppo fra loro,
correlazione sopra il taglio), deviazione fra famiglie 0,62: l'asticella alta resta com'è, non l'ho toccata.
Correlazione settimanale con F5: A -0,01, B +0,03 (249 settimane comuni). Con G1 (ricalcolata con `nucleo.pesi`, stesso universo e
giorni): A 0,11 (giornaliera 0,10), B 0,08 (giornaliera 0,09). Il nome «57 G1» non è dentro `ast.le_prove()` (solo «24 F5»), quindi
G1 è ricalcolata, non presa dal mazzo.

## Variante migliore e sensibilità
A è la migliore ma a zero: il passaggio da 3/30 a 7/90 cambia segno al netto (+0,08% contro -4,7%) e il rendimento dei singoli anni
cambia verso (2024: -5,7% contro +2,8%; 2026: +8,3% contro -31,0%). Nessuna stabilità.

## Anomalie e possibili errori di motore o dati
* Il conto parte il 1° gennaio 2022 (sabato): la prima settimana (lunedì 27 dicembre 2021) conta 2 giorni e compare come «2021» nelle
  serie settimanali (`per_anno` e correlazioni). Non fa differenza per l'esito (2022 e 2023 sono negativi per A e B), ma per «ogni anno
  positivo» le regole indicano 2022-2026: i numeri della tabella sopra non includono il 2021 (ho tolto la riga di quella settimana dalla lettura).
* Nessun errore di motore o dati trovato; lettore di `count` coerente con i caricatori.

## Varianti non previste che proporrei (non eseguite)
Nessuna. Il segnale non ha un segno stabile fra gli anni; non propongo ritocchi.

## Domande aperte
Nessuna che cambi l'esito.

## Letture delle regole che ho dovuto scegliere
1. Giorno con `count` sotto 100: senza dato (regola originale riga 27), oltre a mancante o zero (punto 2 corretto).
2. Il segnale del giorno D usa i giorni D-1 all'indietro (finestra che finisce il giorno prima).
3. Media nelle finestre solo sui giorni validi, con i minimi del punto 3; in più media lunga > 0.
4. Giorno con meno di 20 monete con segnale: nessuna posizione (`passo_banda` come G1).
5. Prima settimana parziale (27 dicembre 2021) inclusa nelle serie settimanali per lo Sharpe e per il mazzo (`periodo` del mazzo la lascia).
6. «Ogni anno positivo»: calcolato sulle medie annue dei settimanali per anno; la settimana 2021 non è considerata nel testo sopra ma nel
   file `esame.json` compare come «2021» negativo.
7. Condizione «lato senza i 10 giorni migliori»: il rendimento annuo del lato (giorni, anno di 365) senza i 10 migliori giorni, sotto zero = fallisce.
8. G1 per la correlazione: ricalcolata con `nucleo.pesi` (stesso universo e giorni), non presa dal mazzo.
9. Fine esclusa `an.FINE` (ultimo giorno 4 ottobre 2026).
