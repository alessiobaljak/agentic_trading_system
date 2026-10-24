# Programma 7 — ventesima prova: sul Bitcoin, contro gli estremi delle 4 ore con un obiettivo piccolo (G18)

Scritto il 24 ottobre 2026, alle 13:45 UTC, **prima di scaricare le candele a 1 minuto del Bitcoin e prima di qualunque calcolo**.
Idea nata dal trader da copiare n. 3 (`research/trader_copiati/trader_3.md`: 118 posizioni sul Bitcoin dal 26 giugno al 21
ottobre 2026, +0,31% a operazione con t 6,8 contro +0,003% delle stesse operazioni con l'entrata a caso). In coda come idea 43.

## 1. Perché

Il trader 3 vende quando il prezzo sta nella parte alta dell'intervallo delle ultime 4 ore dopo una salita (posizione mediana 0,83
contro 0,52 dei minuti a caso, salita delle 4 ore +0,6%), compra nella parte bassa, incassa poco (+0,3%) e taglia le perdite
(al massimo −1,8%). Sul Bitcoin, dentro la giornata, i piccoli eccessi tendono a rientrare (chi fornisce liquidità guadagna dove gli
altri inseguono), e un obiettivo piccolo vicino al prezzo viene toccato spesso. **Il dubbio scritto prima**: con obiettivo 0,3% e
protezione 1,8% una passeggiata a caso vince l'86% delle volte e guadagna zero; le nostre regole di scalping dalle candele perdevano
già prima dei costi (prove 54 e 58-60); il vantaggio del trader potrebbe stare in quello che le candele non mostrano.

## 2. Dati e periodo (fissati qui)

* BTCUSDT perpetuo, candele a 1 minuto dall'archivio pubblico di Binance (file mensili), **dal 1° gennaio 2021 al 25 giugno 2026**
  (il giorno prima della prima posizione del trader che abbiamo visto; il periodo del trader resta fuori).

## 3. La regola (valori fissati qui, vicini alle mediane del trader)

* Al minuto t (chiusura): `pos` = (chiusura − minimo dei 240 minuti fino a t) / (massimo − minimo dei 240 minuti); `r4h` =
  chiusura / apertura di 239 minuti prima − 1.
* **Short** se `pos` ≥ 0,80 e `r4h` ≥ +0,5%; **long** se `pos` ≤ 0,20 e `r4h` ≤ −0,5%.
* Entrata all'apertura del minuto t + 1; **obiettivo 0,3%** a limite; **protezione 1,8%**; al massimo **24 ore**. Se nello stesso
  minuto si toccano obiettivo e protezione, conta la protezione.
* Una posizione alla volta; dopo un'uscita si aspettano 15 minuti.
* Costi: entrata a mercato 0,05% + 0,01% di scarto; obiettivo a limite 0,02%; protezione e uscita a tempo come l'entrata. Funding:
  quello del giorno diviso per le ore tenute (il long paga se positivo).
* Una prova (operazioni + conto): nel conto diventano **143**.

## 4. L'esame

* Operazioni: media sopra zero con **p ≤ 0,01** (bootstrap sulle settimane), positiva nelle due metà e senza le 5 migliori.
* Il conto (tutto il capitale su ogni operazione, leva 1): Sharpe settimanale, ogni anno, Sharpe corretto con l'aggiunta; vale la
  decisione del proprietario del 24 ottobre (da 0,90 in su con ogni anno positivo e t sopra 3 non si boccia).
* **Il caso**: lo stesso numero di entrate al giorno a minuti presi a caso, stesse uscite.
* Per capire, senza decidere niente: solo i long, solo gli short; la quota di obiettivi; e il periodo del trader (26 giugno – 21
  ottobre 2026) come confronto.
