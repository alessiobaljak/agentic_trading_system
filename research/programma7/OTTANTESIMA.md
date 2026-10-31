# Programma 7 — ottantesima prova: G1 dentro ogni settore (G1S)

Scritto il 31 ottobre 2026 alle 08:01 UTC (ora dell'orologio), **prima di qualunque calcolo**. È l'idea 120 della coda. Non cerca uno
Sharpe più alto: toglie un rischio in vista dei soldi veri, come la prova 124 (G1M).

## 1. Perché

* **G1 confronta il funding di tutte le monete insieme.** Così può finire con quasi tutte le monete di un settore comprate e quasi tutte
  quelle di un altro vendute (per esempio le meme contro le reti principali): allora il guadagno o la perdita dipende da come va un
  settore contro l'altro, non da chi paga la leva.
* **Il funding confrontato fra monete simili** misura meglio l'affollamento della singola moneta. Nelle azioni i fattori resi neutri per
  settore hanno di solito meno rischio a parità di rendimento.
* **I dubbi scritti prima**:
  * i settori di CoinGecko sono quelli di oggi (una moneta può aver cambiato settore), e molte monete sono in più settori;
  * con meno monete per settore il confronto è più rumoroso;
  * se il guadagno di G1 viene proprio dal confronto fra settori, questa versione rende meno.

## 2. La regola (fissata qui)

* **I settori** (CoinGecko, `coins/markets` per categoria, letti il 31 ottobre 2026): a ogni moneta il primo settore di questo elenco in
  cui compare: meme (`meme-token`), intelligenza artificiale (`artificial-intelligence`), giochi (`gaming`), finanza decentralizzata
  (`decentralized-finance-defi`), reti di secondo livello (`layer-2`), reti principali (`layer-1`, poi `smart-contract-platform`); le
  monete in nessuno di questi vanno in «altro». La moneta si abbina al perpetuo con la sigla (`annunci.perpetuo`).
* **Il segnale**: lo stesso di G1 (meno il funding dei 7 giorni, `sesta.funding_7`), trasformato in **rango percentuale dentro il settore**
  fra le monete dell'universo del giorno; i settori con meno di 5 monete quel giorno si uniscono ad «altro».
* **Il portafoglio**: tutto il resto come G1 (`prima.py`): banda 20/40 sul rango dentro il settore (`ventiquattresima.pesi_banda`), pesi
  secondo l'inverso della volatilità, decisione ogni giorno, ordini limite, costi e funding; dal 4 gennaio 2021 al 5 ottobre 2026.
* **Una variante di G1**: nel conto delle prove diventano **240**.

## 3. L'esame (scritto prima, sui rischi, come la prova 124)

* **G1S passa se**:
  * la **discesa massima** è più bassa di quella di G1;
  * lo **Sharpe** non scende di più di 0,10 sotto quello di G1.

  Tutti e due calcolati con lo stesso codice e gli stessi dati.
* **Se passa**, è una versione da proporre per i soldi veri al posto di G1, dopo un revisore separato.
* **Per capire, senza decidere niente**: quanto pesa in media il settore più comprato e quello più venduto in G1 e in G1S; il giorno
  peggiore; per anno; la correlazione con G1.
