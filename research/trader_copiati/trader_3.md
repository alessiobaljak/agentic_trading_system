# Trader da copiare n. 3: «PredictionMaster», solo Bitcoin (schermate mandate dal proprietario il 24 ottobre 2026)

Profilo (365 giorni, dalla schermata): ROI +284,36%, guadagno +7.213 USDT (dei copiatori +36.633), Sharpe 2,85, **discesa massima
36,54%**, 194 posizioni vinte su 214 (90,65%), 532 giorni di trading, saldo di margine 9.863 USDT, Bitcoin il 99% delle operazioni.
La curva del guadagno nell'anno sale piano, ma **a febbraio 2026 torna a zero in pochi giorni** (perde tutto quello fatto da
novembre) e poi riparte.

Dati: 118 posizioni chiuse dal 26 giugno al 21 ottobre 2026 (30 schermate; 2 doppie tolte; due possibili buchi fra schermate a
metà agosto e a inizio luglio), trascritte da due lettori separati e **controllate tutte sui prezzi a 1 minuto** (118 su 118 nelle
candele). Programma: `analisi_trader2.py`; tabella: `trader3_posizioni.csv`. Descrittivo, non entra nel conto delle prove.

## Cosa fa

* Solo BTCUSDT, leva 2-4, posizione tipica 13.700 dollari (1,4 volte il margine). 73 long e 45 short.
* **Tiene in media 2 ore** (un quarto sotto i 42 minuti, il 10% oltre le 22 ore).
* **Guadagna poco a ogni operazione e taglia le perdite**: guadagno tipico sul prezzo +0,31% (il 90% sotto +0,74%); la perdita
  peggiore −1,8% sul prezzo (−361 dollari); il prezzo non gli va mai contro più del 4,9%. Niente a che vedere con il trader 2.
* Entra **contro il piccolo movimento appena fatto**: i long dopo un calo (mediana −0,11% nei 15 minuti prima), gli short dopo una
  salita (+0,10%). Commissioni circa 6-11 punti base: usa in parte ordini limite.
* Vinte 104 su 118 (88%): +5.212 dollari; perse 14: −1.615. **Netto +3.597 in 4 mesi**, positivo ogni mese (+36% del margine).

## Ha un vantaggio vero? In questi 4 mesi sì

* Media +0,306% sul prezzo a operazione, deviazione 0,487%: **t 6,8** (il caso darebbe una media così una volta su miliardi).
* **Controllo**: le stesse operazioni (stesso lato e stessa durata) con l'entrata presa a caso entro 3 giorni fanno **+0,003%**
  (51% positive). Quindi non è il Bitcoin salito nel periodo (+27,8%): è il momento in cui entra ed esce.
* **Le riserve**: (1) l'abbiamo scelto da una classifica di migliaia di trader, ma un t di 6,8 regge anche contando migliaia di
  tentativi; (2) le posizioni ancora aperte non si vedono: una perdita tenuta aperta non compare; (3) **la caduta di febbraio 2026**
  (discesa massima 36,5%) dice che anche lui ha periodi in cui il vantaggio sparisce; (4) quattro mesi sono pochi.
* **Si può copiare con una regola?** Probabilmente no: le nostre regole di scalping sul Bitcoin dalle candele (prove 54 e del
  programma 5) perdevano già prima dei costi. Il suo vantaggio sembra stare in come legge i livelli e il libro degli ordini, che le
  candele non mostrano.

## Cosa fare

* È il candidato migliore dei tre per la **copia simulata** («Mock Copy» sul profilo, senza soldi): un solo strumento, perdite
  tagliate, operazioni frequenti (circa una al giorno) che in 30-60 giorni danno già un numero.
* Copiarlo con soldi veri è una decisione del proprietario, fuori dal sistema (che resta senza soldi veri).
