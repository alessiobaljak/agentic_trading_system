# Programma 6 — nona prova: gli acquisti aggressivi e il «biglietto della lotteria» fra monete

Scritto il 19 ottobre 2026, sera, **prima di qualunque calcolo** di questi due segnali. Vale `OTTAVA.md` (pesi secondo la
volatilità, esame sulle 100 monete e conferma sulle 101-200) dove qui non si dice altro.

## 1. Perché

* L'ottava prova dice che fra monete l'**affollamento** (funding alto: tanti long che pagano) si paga: le monete affollate
  rendono meno nella settimana dopo, e sulle 100 monete più scambiate in ogni anno dal 2021 (`RISULTATI_OTTAVA.md`).
* Due altri modi di misurare l'affollamento, con dati che abbiamo già (le candele giornaliere hanno il volume comprato a
  mercato), mai usati come segnale fra monete:
  * **G1, gli acquisti aggressivi**: la quota del volume in USDT dei 7 giorni prima comprata con ordini a mercato. Molti
    compratori impazienti = affollamento (stessa idea del funding, misurata sugli scambi invece che sulla leva).
  * **G2, il biglietto della lotteria**: il rendimento giornaliero più alto dei 30 giorni prima. Nelle azioni e nelle
    crypto i titoli con un grande salto recente rendono meno dopo, perché attirano chi compra la speranza di un altro salto
    (Bali, Cakici e Whitelaw 2011 sulle azioni; Li, Urquhart, Wang e Zhang 2021, «MAX momentum in cryptocurrency markets»,
    trovano però anche l'effetto opposto nel breve: si giudica qui).
* Nel programma 5 (E-114) salti e asimmetria erano tra i fattori provati a 1 ora su 2024-2025/06: nessuna cella promossa.
  Qui l'orizzonte è la settimana e il periodo è dal 2021, con l'universo al tempo giusto.

## 2. Le regole

* Ogni lunedì, fra le 100 monete dell'universo della terza prova: **long il quinto con il segnale più basso, short il
  quinto con il più alto** (poco affollate contro molto affollate), pesi inversamente proporzionali alla volatilità dei 30
  giorni prima, lato long +1 e short −1, tenuta una settimana; costi e funding come la sesta prova.
* **G1**: segnale = somma del volume comprato a mercato in USDT dei 7 giorni prima / somma del volume in USDT dei 7 giorni
  prima (almeno 5 giorni con volume).
* **G2**: segnale = il rendimento giornaliero (chiusura su chiusura) più alto dei 30 giorni prima (almeno 20 giorni).
* Due varianti, due prove: nel conto del programma 6 diventano **29**.

## 3. Gli esami

Come l'ottava prova, per ognuna: (1) sulle 100 monete dal 4 gennaio 2021 le sei condizioni con lo Sharpe corretto sulle
**29** prove; (2) conferma sulle monete 101-200 con lo scarto 0,10% (le cinque condizioni, p ≤ 0,01). **Valida** solo se
passa entrambi. Si riporta anche la correlazione settimanale con F3.
