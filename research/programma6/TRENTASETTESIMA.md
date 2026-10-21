# Programma 6 — trentasettesima prova: la rottura a 4 ore con il funding, entrando con l'ordine limite (T6)

Scritto il 21 ottobre 2026, **prima del calcolo**. Vale `TRENTAQUATTRESIMA.md` (T2) dove qui non si dice altro.

## 1. Perché

T2 (la rottura di Donchian a 4 ore con il filtro del funding) fa +0,014% a operazione **dopo** costi di circa 0,14% fra
entrata e uscita: il segnale c'è, sono i costi a mangiarlo. Con l'ordine limite all'entrata la commissione scende allo 0,02%
e lo scarto sparisce. Ma l'ordine limite ha un prezzo nascosto: se il prezzo scappa subito, l'ordine non si esegue, e spesso
sono proprio le rotture migliori. Qui si misura tutto insieme.

## 2. La regola

* Segnali di T2 (stesse monete, stesso filtro del funding, stesso periodo).
* **Entrata**: ordine limite al **prezzo di chiusura della candela del segnale**, valido per la candela dopo: eseguito solo se
  in quella candela il prezzo torna al livello (minimo ≤ livello per il long, massimo ≥ livello per lo short); prezzo
  d'entrata = il livello; commissione da limite **0,02%**, senza scarto. Non eseguito → nessuna operazione.
* **Uscite** come T2 (stop a 2 ATR, uscita mobile a 3 ATR, al massimo 42 candele), a mercato: 0,05% più lo scarto. Prudenza:
  se nella candela d'entrata il prezzo tocca anche lo stop, si esce allo stop nella stessa candela.
* Funding come T2. Una prova: nel conto del programma 6 diventano **61**.

## 3. L'esame

Come la prova 34 (per operazione con **p ≤ 0,01**, e come portafoglio con lo Sharpe corretto sulle **61** prove). Si
riportano anche quante entrate non si eseguono.
