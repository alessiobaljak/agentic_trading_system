# Programma 6 — decima prova: CTREND con il funding e gli acquisti aggressivi fra gli indicatori

Scritto il 19 ottobre 2026, sera, **prima di qualunque calcolo** di questa variante. Vale `TERZA.md` dove qui non si dice
altro.

## 1. Perché

* CTREND (terza prova) impara da solo, ogni settimana e solo dalle 52 settimane prima, quanto vale ogni indicatore e in che
  verso (la regressione fra monete), e tiene solo quelli che hanno aiutato (la rete elastica). Ha perso nel 2024 (−79%).
* Nelle prove 6-9 due dati che CTREND non vede si sono mostrati informativi fra le monete liquide: il **funding** (alto =
  long affollati, la moneta rende meno: F2, F3) e la **quota di acquisti a mercato** (alta = la moneta continua a salire:
  G1 al rovescio). Il secondo verso l'ho visto dopo il calcolo: per questo **non lo scelgo io**. Li do a CTREND come
  indicatori in più, e il verso e il peso li stima la regressione sulle 52 settimane prima, come per gli altri 28.
* Domanda: con queste due informazioni nuove, il metodo di CTREND regge meglio, anche nel 2024?

## 2. Le regole

* **C4** = C1 (`TERZA.md`, sezione 3: le 100 monete più scambiate, regressioni pesate col volume, rete elastica, quinti,
  lato long +1 e short −1, pesi col volume) con **30 indicatori**: i 28 di CTREND più
  * `funding_7d`: la somma del funding dei 7 giorni prima (come `sesta.py`);
  * `acquisti_7d`: la quota del volume in USDT dei 7 giorni prima comprata a mercato (come G1 in `nona.py`).
* Tutto il resto identico a C1. Una variante, una prova: nel conto del programma 6 le prove diventano **30**.

## 3. L'esame

Come la terza prova (`TERZA.md`, sezione 4), dalle settimane del 6 giugno 2022, con lo Sharpe corretto sulle **30** prove;
e in più la conferma sulle monete 101-200 con lo scarto 0,10% (le cinque condizioni di `SETTIMA.md`, p ≤ 0,01), dalla prima
settimana in cui il metodo dà un segnale. **Valida** solo se passa entrambi.
