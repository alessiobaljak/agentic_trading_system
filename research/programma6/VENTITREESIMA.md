# Programma 6 — ventitreesima prova: il modello ad alberi con la media di cinque semi (M6)

Scritto il 20 ottobre 2026, mattina, **prima di qualunque calcolo con questi semi sui dati corretti**. Vale
`QUATTORDICESIMA.md` (ingredienti, obiettivo, cadenza, portafoglio, esame) dove qui non si dice altro.

## 1. Perché

* M1 (prova 14) dipende dal seme: sui dati di prima sei semi danno Sharpe 1,35 (il seme della prova), 0,79, 0,93, 1,12,
  1,00, 1,43 (`semi_M1.json`); con i dati corretti del 20 ottobre il seme della prova fa 0,79 (`controllo_zombi.json`). Il
  seme cambia quali righe il modello tiene da parte per fermarsi prima (sopra le 10.000 righe).
* Mediare più modelli uguali con semi diversi toglie la parte del risultato che è lotteria del seme (è il motivo del
  «bagging»): il numero che esce è quello da aspettarsi, non quello di un'estrazione.

## 2. La regola

* Come M1, con i dati corretti del 20 ottobre (pannello e universo con le correzioni in `seconda.py` e `terza.py`).
* A ogni riallenamento si allenano **cinque** modelli identici a M1 con i semi **1, 2, 3, 4, 5** (il 2026 della prova no:
  il suo risultato sui dati corretti è già noto); la previsione di una moneta è la **media dei ranghi** delle cinque
  previsioni fra le monete della settimana.
* Portafoglio, costi ed esame come M1 (`QUATTORDICESIMA.md`, sezioni 3 e 4), dal 3 gennaio 2022, con lo Sharpe corretto
  sulle prove del programma 6, che diventano **47**. Si riportano anche la correlazione con F3 e K1 e lo Sharpe di ogni
  seme da solo (descrittivo).

## 3. Se regge

Se passa l'esame entra nel paper al posto di M1 dalla settimana dopo (M1 resta misurato per confronto); se non passa ma
il suo Sharpe sul passato è almeno quello di M1 sui dati corretti, nel paper si aggiunge come informazione accanto a M1.
