# Programma 6 — sesta prova: il funding come segnale fra monete

Scritto il 19 ottobre 2026, dopo il via del proprietario («continua a cercare in autonomia, non fermarti, se pensi serva
misurare in paper procedi, hai campo libero fino a che non trovi cosa funziona», 19 ott 2026, sera) e **prima di
qualunque calcolo** di questa prova. Vale `TERZA.md` (settimane, universo, costi, conto) dove qui non si dice altro.

## 1. Perché

* Le prove 1-5 hanno usato prezzi e volumi. Il funding (quello che i long pagano agli short, o il contrario) non è mai
  stato usato **come segnale fra monete**: nel programma 5 solo come costo e intorno al momento del regolamento (I-006).
* **Cao, Luo, Cheng e Dong, «Anatomy of Cryptocurrency Perpetual Futures Returns»** (SSRN 6365329, 2026): su 170 segnali
  fra perpetui, un modello a due fattori, uno dei quali è la **distanza fra perpetuo e prezzo a pronti** (il «basis»),
  spiega tutte le 63 strategie che funzionano. Il funding di Binance è la media di quella distanza (più un piccolo
  interesse fisso): un funding alto vuol dire long affollati e perpetuo caro.
* L'idea economica: chi paga un funding alto paga per la leva; quando i long affollati escono, il prezzo scende verso
  il valore a pronti; chi sta dall'altra parte incassa il funding e il ritorno. Il contrario per i funding negativi.
* Contro: un lavoro su 10 perpetui (Junior, SSRN 6701738) non trova niente con funding e prezzi a 8 ore. Diverso
  orizzonte (qui una settimana) e diverso numero di monete (qui 100).

## 2. Le regole

* **Segnale** di ogni moneta alla chiusura della domenica: la **somma dei tassi di funding degli ultimi 7 giorni**
  (dal file mensile; nelle ultime settimane di ottobre 2026, dove l'archivio non ha ancora il file, il valore stimato
  della seconda prova: si dice nei risultati).
* **Portafoglio** ogni lunedì, fra le 100 monete dell'universo della terza prova: **long il quinto con il funding più
  basso, short il quinto con il funding più alto**; lato long +1 e lato short −1 del capitale; si tiene fino al lunedì
  dopo. Costi e funding (che qui conta due volte: è il segnale ed è incassato o pagato) come nella terza prova.
* Le varianti, **due e solo due** (nel conto del programma 6 le prove diventano **26**):
  * **F1**: pesi proporzionali alla mediana del volume dentro ogni lato (come C1);
  * **F2**: pesi uguali.

## 3. L'esame

Sulle settimane **dal 4 gennaio 2021** (il primo lunedì del 2021) all'ultima completa; le stesse sei condizioni della
terza prova (`TERZA.md`, sezione 4), con lo Sharpe corretto sulle **26** prove e gli anni dal 2021 al 2026 (almeno **4
su 6**); i trimestri pieni da guardare sono quelli del 2021, 2022, 2023, 2024 e 2025. Si riportano anche i due lati da soli e
quanto del risultato viene dal funding incassato e quanto dal prezzo.
