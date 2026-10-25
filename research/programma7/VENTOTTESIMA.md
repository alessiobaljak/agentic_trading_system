# Programma 7 — ventottesima prova: N3 solo per le monete davvero nuove (N3V)

Scritto il 25 ottobre 2026, alle 06:40 UTC, **prima di qualunque calcolo sui rendimenti**. Idea 58 della coda di
`research/REGISTRO.md`. Il controllo di fattibilità fatto prima ha contato solo gli abbinamenti (nessun rendimento guardato, la
lezione dell'idea 56): delle 613 monete nuove di Binance (prova 32), dal 2023 (da quando i dati di Gate.io coprono) 307 sono nate
su Binance entro 3 giorni dal contratto di Gate e 26 non sono mai state su Gate; 90 avevano il contratto su Gate da almeno 30
giorni prima; 61 fra 4 e 29 giorni; 21 su Gate dopo; 108 (2021-2023) con il contratto di Gate più vecchio della copertura.

## 1. Perché

Il perché di N3 (chi compra la novità nei primi giorni paga troppo e poi il prezzo scende) vale di più quando la moneta **nasce** con
il perpetuo di Binance: il prezzo non è ancora stato scoperto da nessuno. Se invece la moneta aveva già un perpetuo su Gate.io da
settimane o mesi, il prezzo è già passato dalla fase della novità altrove, e la vendita al 7° giorno su Binance dovrebbe rendere
meno. **Il dubbio scritto prima**: Gate quota tante monete piccole e il suo prezzo può contare poco; e i gruppi non sono grandi.

## 2. La regola

* **Le operazioni della prova 32**, identiche (`risultati_trentaduesima/eventi_N3B.csv`), dal 1° gennaio 2023 in poi.
* **Gruppo A, «davvero nuove»**: il contratto di Gate (`SIGLA_USDT`, primo giorno dai file giornalieri di Gate) nasce entro ±3
  giorni dal perpetuo di Binance, oppure non esiste. **Gruppo B, «già scoperte»**: il contratto di Gate esiste da almeno 30 giorni
  prima. Le altre (4-29 giorni prima, Gate dopo, copertura mancante) restano fuori e si contano.
* Una prova a eventi: nel conto diventano **159**, le prove a eventi **24**.

## 3. L'esame

* **A rende più di B**: la differenza delle medie sopra zero con p ≤ 0,05 (bootstrap sulle settimane dentro ciascun gruppo, come la
  prova 83); e A da sola passa l'esame di N3 (p ≤ 0,01, due metà, senza le 5 migliori). Se la differenza non c'è, N3 resta com'è.
* Si riportano le due parti per anno, la quota di uscite a +30%, e i gruppi esclusi con la loro media (solo per capire).
