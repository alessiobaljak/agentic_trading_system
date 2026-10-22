# Programma 6 — quarantasettesima prova: la paura nelle opzioni (O1 Bitcoin, O2 Ether)

Scritto il 22 ottobre 2026, notte, **prima di scaricare i dati e di qualunque calcolo**. Idea 16 della coda di
`research/REGISTRO.md`.

## 1. Perché

Chi compra opzioni paga la protezione: la volatilità che il mercato si aspetta (implicita) di solito è più alta di quella
che poi si vede (realizzata). La differenza, il «premio per il rischio di varianza», è grande quando c'è paura; per le borse
è pubblicato che un premio alto anticipa rendimenti più alti nei mesi dopo (Bollerslev, Tauchen e Zhou 2009): chi compra
quando gli altri pagano tanto per proteggersi viene pagato per il rischio. Per Bitcoin ed Ether l'indice della volatilità
implicita a 30 giorni è il **DVOL** di Deribit, dal 2021.

## 2. La regola (valori fissati qui)

* **Dati**: il DVOL giornaliero di Deribit per BTC ed ETH (`get_volatility_index_data`, chiusura del giorno), scaricato una
  volta con l'impronta (`scarico_dvol.py`).
* **Premio** della domenica: DVOL² − (volatilità realizzata dei 30 giorni fino alla domenica, dai rendimenti giornalieri del
  perpetuo, all'anno)², in punti percentuali al quadrato.
* **Posizione** per la settimana (dall'apertura del lunedì a quella del lunedì dopo): **long il perpetuo al 100%** se il
  premio della domenica è **sopra la sua mediana delle 52 domeniche prima**, altrimenti niente.
* **Costi**: a ogni entrata e uscita commissione 0,05% più 0,01% di scarto; il funding dei giorni tenuti.
* **O1** Bitcoin, **O2** Ether. Settimane dal primo lunedì con 52 domeniche di premio (circa aprile 2022) al 5 ottobre 2026.
  Due prove: nel conto del programma 6 diventano **106**.

## 3. L'esame

`terza.esame` e `terza.esito` (intervallo sopra zero, Sharpe corretto sulle **106** prove almeno 0,95, 4 anni su 5 o più,
ultimo anno, costi doppi, trimestri, più del Bitcoin). Si riportano anche la moneta tenuta sempre sulle stesse settimane e la
quota di settimane in posizione.
