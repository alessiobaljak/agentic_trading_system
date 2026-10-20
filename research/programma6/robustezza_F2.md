# Programma 6 — quanto è solida F2 (descrittivo, non è una prova)

Calcolato il 19 ottobre 2026 sera, dopo la sesta e la settima prova, con lo stesso codice (`sesta.py`, `terza.py`). **Non è
una prova e non cambia nessun esito**: sono le domande che si fanno a una candidata prima di misurarla in paper. Le varianti
qui sotto non si usano al posto di F2 (sarebbe scegliere sul passato): F2 resta quella delle regole, con la finestra di 7
giorni.

Settimane dal 4 gennaio 2021; rendimento netto annualizzato; leva lorda 2; costi come la sesta prova salvo dove detto.

| Variante | Settimane | Rendimento/anno | Sharpe | Anni positivi | Dal funding | Dal prezzo |
|---|---|---|---|---|---|---|
| finestra del funding 3 giorni | 301 | +55,7% | 1,18 | 6/6 | +42,7% | +21,4% |
| **finestra 7 giorni (F2)** | 301 | +47,5% | 1,03 | 6/6 | +40,1% | +14,8% |
| finestra 14 giorni | 301 | +38,4% | 0,86 | 5/6 | +39,8% | +4,3% |
| finestra 30 giorni | 301 | +6,5% | 0,14 | 4/6 | +38,6% | −27,9% |
| solo le prime 50 monete | 301 | +35,0% | 0,63 | 6/6 | +41,5% | +1,2% |
| solo dalla 51ª alla 100ª | 281 | +39,8% | 0,66 | 4/6 | +37,8% | +10,5% |
| costi tripli | 301 | +32,6% | 0,71 | 5/6 | +40,1% | +14,8% |

Cosa dice:

* il **funding incassato** vale circa il 40% l'anno in tutte le varianti: è la parte stabile;
* la parte del **prezzo** dipende dalla finestra: positiva con il funding degli ultimi giorni (affollamento recente, che poi
  rientra), negativa con quello di un mese (chi paga funding alto da un mese è in una tendenza vera, e continua a salire);
* regge a **costi tripli** e nelle due metà delle 100 monete, ma non sulle monete dalla 101ª alla 200ª (settima prova), dove
  costi e prezzo si mangiano il funding.

## F3 (ottava prova): dipende da poche monete? (19 ottobre 2026, sera; descrittivo)

Con i pesi secondo la volatilità le monete calme pesano di più (nella settimana dal 2026-10-19 TRX è il 37% del lato long,
BNB il 14% di quello short). Stesso periodo e stessi costi di F3 (tabella aggiornata al 18 ottobre):

| Variante | Rendimento/anno | Sharpe | Anni positivi | Peso massimo medio di una moneta |
|---|---|---|---|---|
| **F3 come da regole** | +51,3% | 1,30 | 6/6 | 13% |
| tetto del 10% per moneta | +50,6% | 1,24 | 6/6 | 10% |
| senza BTC, ETH, BNB, TRX, XMR | +46,9% | 1,12 | 6/6 | 11% |
| senza le cinque e con il tetto | +47,5% | 1,10 | 6/6 | 10% |

Non dipende da poche monete: il risultato resta quasi uguale. F3 resta quella delle regole (nessuna variante la sostituisce).

## M1 (quattordicesima prova): quanto è solido? (20 ottobre 2026; descrittivo)

Stesso periodo (dal 3 gennaio 2022), stesse previsioni del modello, stessi costi salvo dove detto:

| Variante | Rendimento/anno | Sharpe | Anni positivi | Quota delle 5 settimane migliori | Senza le 5 migliori (a settimana) |
|---|---|---|---|---|---|
| **M1 come da regole** | +50,9% | 1,35 | 4/5 | 34% | +0,662% |
| tetto del 10% per moneta | +51,9% | 1,36 | 4/5 | 33% | +0,680% |
| senza BTC, ETH, BNB, TRX, XMR | +43,4% | 1,11 | 4/5 | 42% | +0,492% |
| costi tripli | +33,5% | 0,89 | 4/5 | 50% | +0,326% |

Non dipende da poche monete né da poche settimane; a costi tripli resta positivo. M1 resta quello delle regole.

## F5 (ventiquattresima prova): quanto è solida? (20 ottobre 2026; descrittivo)

Calcolo di `robustezza_F5.py` (`robustezza_F5.json`), dati fino al 19 ottobre, settimane dal 4 gennaio 2021. F5 resta quella
delle regole: nessuna variante la sostituisce.

| Variante | Rendimento/anno | Sharpe | Anni positivi |
|---|---|---|---|
| **F5 come da regole** | +57,4% | 1,93 | 6/6 |
| solo il lato long (netto) | +42,8% | 0,54 | 4/6 |
| solo il lato short (netto) | +16,2% | 0,19 | 3/6 |
| costi doppi | +52,5% | 1,77 | 6/6 |
| costi tripli | +47,6% | 1,60 | 6/6 |
| solo le prime 50 monete | +46,7% | 1,28 | 6/6 |
| solo dalla 51ª alla 100ª | +40,6% | 0,99 | 5/6 |
| tetto del 10% per moneta | +56,6% | 1,85 | 6/6 |
| senza BTC, ETH, BNB, TRX, XMR | +54,6% | 1,64 | 6/6 |
| cambio il giovedì invece del lunedì | +54,4% | 1,71 | 6/6 |

Cosa dice: regge a costi tripli, nelle due metà delle 100 monete, senza le monete più pesanti e con un altro giorno della
settimana. La forza è nei due lati insieme: da soli il long fa 0,54 e lo short 0,19 (ognuno porta il rischio del mercato
intero; insieme si annulla).
