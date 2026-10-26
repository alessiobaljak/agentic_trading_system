# Programma 7 — quarantottesima prova: vendere le opzioni, la chiamata coperta e la vendita della volatilità (VO)

Scritto il 26 ottobre 2026, alle 06:34 UTC, **prima di qualunque calcolo**. Strategie 27 e 28 del documento del proprietario del 26 ottobre
(«covered call: si tiene l'asset e si vendono opzioni call per raccogliere il premio, generando rendimenti dal 12 al 25% annuo»; il gamma
scalping, cioè comprare la volatilità e coprirsi, è il contrario della seconda regola qui sotto). Mai provate.

## 1. Perché, e il dubbio

Chi vende opzioni incassa un premio perché il mercato paga per assicurarsi: la volatilità implicita (quanto il mercato si aspetta che il
prezzo si muova, nel prezzo delle opzioni) di solito è più alta di quella che poi si vede. È il «premio della volatilità», documentato su
azioni e, per il Bitcoin, nella prova 47 (che lo usava come segnale, non lo vendeva). **Il dubbio scritto prima**: chi vende opzioni
guadagna poco quasi sempre e perde molto nei crolli e nelle salite verticali (è la stessa forma delle fiammate vendute, prove 75-76); il
premio vero lo mangiano lo scarto e le commissioni; e qui **i prezzi delle opzioni non li abbiamo**: si stimano con la formula di Black e
Scholes dalla volatilità implicita di Deribit a 30 giorni (DVOL), che per le opzioni lontane dal prezzo e per quelle a 7 giorni può essere
diversa da quella vera. È un'approssimazione, dichiarata: se il risultato è vicino a zero non dice niente.

## 2. Le regole (valori fissati qui)

* **Dati**: DVOL giornaliero di Deribit per BTC ed ETH (dal 24 marzo 2021; `research/data/dvol`), il valore del giorno prima; prezzi dalle
  candele orarie del perpetuo (alle 08:00 UTC, l'ora delle scadenze di Deribit). Tasso d'interesse zero.
* **CC, la chiamata coperta (mensile)**: l'ultimo venerdì di ogni mese alle 08:00 UTC si tiene 1 moneta e si vende 1 opzione di acquisto con
  prezzo d'esercizio **+10%**, scadenza l'ultimo venerdì del mese dopo alle 08:00. Si misura **la parte delle opzioni** (premio meno quello che
  si paga alla scadenza, sul prezzo d'entrata), che è quello che la chiamata coperta aggiunge al tenere la moneta; si riporta anche il totale.
* **SS, la vendita della volatilità (settimanale)**: ogni venerdì alle 08:00 UTC si vendono 1 opzione di acquisto e 1 di vendita al prezzo di
  quel momento, scadenza il venerdì dopo alle 08:00; nessuna copertura; il risultato della settimana è premio meno |prezzo alla scadenza −
  prezzo d'esercizio|, sul prezzo d'entrata (1 moneta di valore nominale per ogni unità di conto).
* **Costi**: per ogni opzione venduta la commissione di Deribit (0,03% del prezzo della moneta, al massimo il 12,5% del premio) più **il 3% del
  premio** per lo scarto; alla scadenza 0,015% se l'opzione finisce nel denaro.
* Due prove nel conto (CC e SS, ognuna su BTC ed ETH insieme): **198**.

## 3. L'esame

Per ognuna, la serie del portafoglio (BTC ed ETH con lo stesso peso; mensile per CC, settimanale per SS): media sopra zero con **p ≤ 0,01**
(bootstrap), positiva in ogni anno pieno (2022-2025), e la discesa peggiore; per SS anche lo Sharpe corretto rivisto e la regola del
proprietario. Si riportano le perdite peggiori, quante volte la vendita perde, e per moneta. Il gamma scalping del documento (comprare la
volatilità) è lo specchio di SS: si riporta il suo risultato senza contarlo.
