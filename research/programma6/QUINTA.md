# Programma 6 — quinta prova: lo short dopo il crollo della sola moneta

Scritto il 19 ottobre 2026, subito dopo la quarta prova e **prima di qualunque calcolo** di questa. Vale `QUARTA.md`
dove qui non si dice altro.

## 1. Da dove viene

* **Quarta prova** (`RISULTATI_QUARTA.md`, diagnosi): sulle 440 monete mai usate, il long dopo un crollo di 4 ore della
  **sola moneta** (il Bitcoin non crolla, z4 del Bitcoin sopra −3) perde **−2,0% netto a trade** (1.326 trade, intervallo
  −3,48; −0,67, costi 0,40%): la moneta che crolla da sola continua a scendere.
* **Programma 5, I-015** (`research/programma5/STATO.md`): «la discesa propria coperta con BTC nel 2023 continua invece di
  tornare» (V: −0,31%, −0,58%, −0,38% per il long).
* Perché: un crollo della sola moneta di solito ha una notizia sua (un furto, uno sblocco di gettoni, una delisting, un
  problema della squadra); le notizie cattive si digeriscono in più ore, e il prezzo continua nel verso del crollo.
* Il fenomeno è stato **visto** sulle 440 monete della quarta prova: quelle ora sono la costruzione. La conferma si fa
  sulle **altre** monete: le 100 di `research/programma5/universo_top100.json`, su cui questa regola (short, filtro sul
  Bitcoin) non è mai stata calcolata. Il programma 5 ha fatto su di loro esplorazioni a ore (anche di crolli) sul periodo
  2024-01 → 2025-06: la conferma è quindi pulita per la regola, meno per i dati; lo si scrive qui.

## 2. La regola (scritta adesso, senza guardare le 100 monete)

* Candele da **1 ora** delle 100 monete (`research/data/p6/<SIMBOLO>_1h.pkl`, fatte dai minuti verificati del programma 5;
  un'ora vale con almeno l'80% dei minuti).
* `z4` come nella quarta prova (σ oraria delle 720 ore prima, almeno 500, presa 4 ore prima).
* **Segnale** alla chiusura dell'ora t se `z4` della moneta ≤ **−5** e `z4` del Bitcoin nella stessa ora **> −3** (il
  Bitcoin stesso non entra: il filtro sarebbe impossibile).
* **Short** all'apertura dell'ora dopo, **uscita** alla chiusura dell'ora t+12; pausa di 12 ore dopo un segnale. Niente
  stop, niente obiettivo (come la regola della quarta prova, di cui è il rovescio).
* Universo mese per mese come nella quarta prova (mediana del volume ≥ 10 milioni, almeno 30 giorni di candele).
* **Costi**: 0,05% di commissione e **0,15%** di scarto a ogni lato (0,40% andata e ritorno); funding con il segno dello
  short (incassa il funding positivo, paga quello negativo).
* **Il caso**: 20 short a un'ora a caso nello stesso mese e nella stessa moneta, stessa tenuta e stessi costi.

## 3. L'esame

Dal 2021-01-01 all'ultima ora disponibile (17 ottobre 2026). **Confermata** se tutte e sette:

1. netto medio a trade positivo, intervallo al 95% sopra zero e p ≤ 0,01 (bootstrap a blocchi di giorni, 10.000 volte);
2. il netto supera quello del caso, con l'intervallo della differenza sopra zero;
3. positiva in almeno 4 anni su 6 e nell'ultimo anno (dal 2025-10-01);
4. positiva a costi doppi;
5. positiva su almeno il 55% delle monete con almeno 5 trade;
6. positiva senza il giorno migliore;
7. con almeno **100 trade** (sotto, il risultato non si legge).

Una sola regola, una sola prova. Se è confermata, la si porta anche sulle 440 monete della quarta prova solo come
descrizione (non come prova: lì è nata).
