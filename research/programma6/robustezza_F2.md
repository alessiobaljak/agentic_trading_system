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
