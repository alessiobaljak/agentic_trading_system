# Programma 7 — quarantaseiesima prova: lo scalping con gli indicatori classici a 1 e 5 minuti (SK)

Scritto il 26 ottobre 2026, alle 06:20 UTC, **prima di qualunque calcolo**. Dal documento mandato dal proprietario il 26 ottobre
(`research/trader_copiati/documenti/strategie_scalping_proprietario_26ott.rtf`: 37 strategie di scalping raccolte da siti di trading). Il
confronto con il registro: gli indicatori a 15 minuti, 1 ora, 4 ore e 1 giorno sono già stati provati (prove 1, 34-39, 46: le 17 strategie
pronte di TradingView), lo scalping a 5 minuti e 1 minuto in parte (prova 54: VWAP, rottura della prima ora, spinta del volume); **gli
indicatori classici a 1 e 5 minuti, come li descrive il documento, mai**. Questa prova li fa tutti insieme, con i valori del documento.

## 1. Perché, e il dubbio

Il documento dice che queste regole, con una buona gestione del rischio (stop stretto, rapporto rischio/rendimento almeno 1:2), separano
gli scalper che guadagnano da quelli che perdono. **Il dubbio scritto prima**: a 1-5 minuti i movimenti sono piccoli e i costi di un giro
(circa 0,12-0,14% fra entrata, uscita e scarto) pesano moltissimo; tutte le prove a orizzonte corto fatte finora (54, 75-78, 102 e il
programma 5) hanno perso dopo i costi, e la prova 102 ha mostrato che anche dove il segnale c'è vale meno di un giro. Probabilità bassa.

## 2. I dati, le monete, il periodo

* **Monete**: BTC, ETH, SOL, XRP, DOGE, BNB (le più scambiate, dove lo scalping costa meno), perpetui USDT; candele a 1 minuto verificate
  del programma 5; le candele a 5 minuti fatte da quelle (una candela vale con tutti e 5 i minuti).
* **Periodo**: dal 1° gennaio 2024 al 30 settembre 2026 (le regole sono quelle del documento, non scelte sui dati: decide tutto il periodo).

## 3. Le regole (valori del documento; dove il documento non dice l'uscita, la stessa per tutte, fissata qui)

Uscita comune («stop stretto, rapporto 1:2» del documento): **stop a 1 ATR(14), obiettivo a 2 ATR(14)** dall'entrata, al massimo **60
candele**. Entrata all'apertura della candela dopo il segnale. Una posizione per regola e per moneta alla volta.

1. **EMA 9/21 + RSI(14)**: long quando la EMA 9 incrocia sopra la EMA 21 con l'RSI sopra 50; short al contrario (RSI sotto 50).
2. **La regola della EMA 5** (uscita del documento): short quando una candela chiude tutta sopra la EMA 5 (minimo sopra la EMA) e la candela
   dopo rompe sotto il suo minimo (entrata al minimo rotto); stop sopra il massimo della candela segnale; obiettivo a **3 volte** il rischio.
   Long allo specchio.
3. **RSI(7) 80/20**: short quando l'RSI a 7 scende sotto 80 da sopra; long quando sale sopra 20 da sotto.
4. **Bollinger (20, 2)** (uscita del documento): long quando la chiusura è sotto la banda bassa, short sopra la banda alta; obiettivo alla
   media a 20; stop a 1 ATR.
5. **MACD (12, 26, 9)**: long quando la linea incrocia sopra la linea del segnale, short sotto.
6. **Stocastico (5, 3, 3)**: long quando %K incrocia sopra %D sotto 20; short quando incrocia sotto %D sopra 80.
7. **VWAP del giorno** (uscita del documento): VWAP dalle 00:00 UTC; long quando la candela tocca la VWAP dall'alto (minimo sotto, chiusura
   sopra, chiusura prima sopra) e short allo specchio; **obiettivo +0,5%, stop 0,25%**.
8. **Ritracciamento con EMA e RSI stocastico**: tendenza su quando EMA 9 > EMA 14 > EMA 20; long quando la chiusura è fra la EMA 20 e la
   EMA 9 con l'RSI stocastico (14, 14, 3) sotto 20; short allo specchio (sopra 80, tendenza giù).
9. **Rottura con il volume**: long quando la chiusura supera il massimo delle 20 candele prima con il volume sopra 1,5 volte la media delle
   20; short allo specchio sotto il minimo.

Ogni regola a 1 minuto e a 5 minuti: **18 varianti**, nel conto **194**.

## 4. I costi e l'esame

* **Costi**: entrata e stop a mercato (0,05% di commissione più lo scarto: 0,01% per BTC, ETH, SOL; 0,02% per le altre), obiettivo con un
  ordine limite (0,02%). Funding non contato (tenute di minuti o ore). Si riporta anche il lordo, prima dei costi.
* **Esame**, per ognuna delle 18: media per operazione sopra zero dopo i costi con **p ≤ 0,01/18** (bootstrap sui giorni), positiva nel
  2024, nel 2025 e nel 2026, e su almeno 4 monete su 6. Si riportano operazioni al giorno, quota vinta, lordo e netto per anno e per moneta.
