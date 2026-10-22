# Programma 6 — cinquantesima prova: F5 sulle monete dalla 101ª alla 150ª (conferma)

Scritto il 22 ottobre 2026, mattina, **prima del calcolo**. Idea 21 della coda di `research/REGISTRO.md`.

## 1. Perché

F5 (il funding fra monete con la banda) è la strategia più solida fra le 100 monete più scambiate. Il proprietario vuole
strategie per più monete possibili: vale anche oltre le 100? Sulle 101-200 le versioni senza banda (F2, F3) perdevano per i
costi (prove 7 e 8: costi intorno al 19% l'anno). Qui la stessa regola F5, **senza cambiare niente**, sulla metà più liquida
delle 101-200, dove la banda riduce il giro. Sono monete su cui F5 non è mai stata guardata: è una **conferma** (una regola
sola su dati non usati), non conta nel conto delle prove.

## 2. La regola

* Ogni lunedì le monete dalla **101ª alla 150ª** per volume (`terza.pannello_settimane` con `da=100, a=150`), dati corretti.
* F5 com'è (`ventiquattresima.pesi_banda`: segnale −funding dei 7 giorni, entrata nel 20%, uscita oltre il 40%, pesi secondo
  la volatilità dei 30 giorni), si opera con almeno 20 monete.
* Costi delle monete meno scambiate: commissione 0,05% e **scarto 0,10%** (come le prove 7 e 8); funding con il segno.
* Dal 4 gennaio 2021 al 5 ottobre 2026.

## 3. L'esame (quello delle conferme, `settima.esito`)

Confermata se: netto settimanale sopra zero con l'intervallo sopra zero e **p ≤ 0,01**; positiva in almeno tre quarti degli
anni con almeno 26 settimane e nell'ultimo anno; positiva a costi doppi; positiva senza le 5 settimane migliori; il prezzo non
si mangia più di metà del funding incassato. Si riportano anche lo Sharpe, la correlazione con F5 sulle 100 e le spese.
