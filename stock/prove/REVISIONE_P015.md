# Prova 15 — la revisione separata (24 ottobre 2026, prima del periodo chiuso)

Fatta da un agente che non ha scritto il codice, in sola lettura, senza guardare i dati dopo il 31 dicembre 2024. Ha rifatto il calcolo
con lo stesso simulatore: SPY 0,947 contro 0,928 del tenere, QQQ 1,077 contro 0,994 (come `P015_risultati.md`). 65 test verdi.

**Esito: nessun errore bloccante.** Verificati: nessun dato del futuro nella volatilità (anche con le chiusure non rettificate SPY 0,953);
esecuzioni all'apertura del giorno dopo (scarto massimo dall'apertura 0,69 punti base, cioè metà scarto più slittamento); leva massima
rispettata (0 ordini rifiutati, esposizione massima 1,509 a fine giornata per il movimento dei prezzi); soglia del 10% come scritta;
interessi sul prestito pagati ogni sera (con l'8% SPY scende a 0,919, con il 10% a 0,886); dividendi corretti anche sulle azioni a
prestito; il confronto con il tenere sugli stessi giorni; le regole committate prima del programma.

## Cose da sapere (nessuna blocca)

| # | Trovato | Peso |
|---|---|---|
| 1 | Sullo SPY il vantaggio è 0,02 di Sharpe e dipende dal tasso: con l'8% invece del 6% la condizione 1 cade (0,919 contro 0,928). Con Interactive Brokers nel 2023-2024 il tasso era intorno al 6,8% (riferimento + 1,5%); nel 2016-2021 più basso. QQQ regge | importante |
| 2 | Con lo Sharpe al netto del tasso dei titoli di stato (stima del revisore con medie scritte a memoria): SPY 0,821 contro 0,815, QQQ 0,96 contro 0,905. Anno per anno la regola ha lo Sharpe più basso del tenere in 9 anni su 9 sullo SPY e 8 su 9 su QQQ: il vantaggio viene dall'essere poco investiti nei passaggi fra un anno e l'altro (2020, 2022) e con la leva negli anni calmi. Esposizione media SPY 1,14, QQQ 0,95 | importante, da leggere |
| 3 | Interessi contati solo nelle sere di borsa (252); un broker vero conta 365/360: circa 6,08% effettivo, trascurabile | minore |
| 4 | I contanti fermi non rendono: prudente | minore |
| 5 | Nessun test diretto degli interessi nel simulatore a più titoli (verificati a mano) | minore |
| 6 | Nessuna ritenuta sui dividendi americani (15%): con la leva media la regola ne incassa un po' di più | minore |
| 7 | Nella tabella la riga «uscite dal mercato» conta le vendite: la regola non esce mai del tutto (esposizione minima 0,22-0,24) | minore |
| 8 | Il conto dell'asticella include le serie del periodo chiuso, che diventano gruppi a parte: la rende più severa, non più generosa | minore |

## In una riga

Il calcolo è onesto. Il dubbio vero per il periodo chiuso è il tasso del prestito: sullo SPY la condizione regge solo sotto il 7% circa.
