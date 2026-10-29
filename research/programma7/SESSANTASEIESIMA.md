# Programma 7 — sessantaseiesima prova: comprare il perpetuo quando è sotto il pronti (BP)

Scritto il 29 ottobre 2026 alle 17:06 UTC (ora dell'orologio), **prima di qualunque calcolo dei rendimenti**. È l'idea 102 della coda.
Fino a qui si è misurato solo il premio, non il prezzo (`programma7/BUCO_PERPETUO.md`, descrittiva): nei 366 casi del 2024-2026 in cui
il perpetuo chiude un'ora almeno l'1% sotto il pronti, il buco si dimezza nella prima ora (mediana da −1,39% a −0,66%), ma resta per
ore (−0,31% dopo 4 ore; chiuso del tutto nel 44% dei casi dopo 4 ore, nel 58% dopo 24). Quindi non è una cosa da pochi secondi come il
BNB: è un'operazione che un programma normale può fare.

## 1. Perché

* **Chi vende il perpetuo molto sotto il pronti** non è chi tiene la moneta: sono le posizioni a leva liquidate, o chi chiude in fretta.
  Il prezzo a pronti dice che il valore della moneta non è sceso così tanto.
* **L'indice del premio di Binance** usa i prezzi a cui si compra davvero una quantità normale (il prezzo d'acquisto «d'impatto»): un
  premio a −1,4% vuol dire che si compra il perpetuo l'1,4% sotto il pronti, non solo che l'ultimo prezzo è basso.
* **Il guadagno atteso** è il ritorno del perpetuo verso il pronti (circa un punto in 4 ore, in mediana, dalla misura descrittiva), più
  quello che fa il pronti.
* **I dubbi scritti prima**:
  * il pronti può continuare a scendere: la prova 112 (comprare dopo le cascate di vendite forzate) non ha retto;
  * il ritorno verso il pronti può venire dal pronti che scende, non dal perpetuo che sale;
  * i costi a mercato di due monete (0,42% andata e ritorno) si mangiano metà del ritorno atteso.

## 2. La regola (fissata qui)

* **L'evento**: un'ora che chiude con l'indice del premio di Binance (candele orarie dell'archivio pubblico) a **−1% o sotto**, dopo
  un'ora che chiude sopra −0,5%, al massimo uno ogni 24 ore per moneta; sulle monete dell'universo di G1 nella settimana dell'evento;
  dal 4 gennaio 2021 al 30 settembre 2026 (il periodo della misura descrittiva più gli anni prima, che non sono mai stati guardati).
* **L'operazione**: long il perpetuo della moneta e short il Bitcoin per lo stesso valore, all'apertura dell'ora dopo l'evento; uscita
  all'apertura di 4 ore dopo. Nessuno stop.
* **Costi**: a mercato, come la prova 105 (`ventunesima.COSTO_MONETA` e `COSTO_BTC`, 0,42% in tutto). **Funding**: per ogni
  regolamento delle 00, 08 e 16 UTC dentro la tenuta, un terzo del funding del giorno della moneta (incassato se negativo) e del
  Bitcoin (pagato o incassato per lo short).
* **Una prova a eventi**: nel conto delle prove diventano **224**, le prove a eventi **37**.

## 3. L'esame

* **Come le prove a eventi** (`trentesima.esame`, ricampionamento per settimana): media per evento sopra zero con **p ≤ 0,01**, positiva
  nelle due metà e senza i 5 eventi migliori, **e sopra il controllo** (differenza con p ≤ 0,05). Contando le 37 prove a eventi la
  soglia è **0,00027**.
* **Il controllo**: la stessa operazione sulla stessa moneta in 20 ore prese a caso (seme 2026) fra 30 e 365 giorni prima o dopo
  l'evento, in ore con il premio sopra −0,5% e lontane almeno 24 ore da ogni evento della stessa moneta, nelle settimane in cui la
  moneta è nell'universo.
* **Se regge**, passa da un revisore separato prima del paper.
* **Per capire, senza decidere niente**: le tenute di 1, 2, 8 e 24 ore; senza la copertura del Bitcoin; gli eventi più profondi (−2% o
  sotto); per anno; il 2021-2023 (mai guardato) contro il 2024-2026 (dove è stato misurato il premio); il cambio del premio nelle 4 ore.
