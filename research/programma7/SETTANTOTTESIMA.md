# Programma 7 — settantottesima prova: vendere quando una moneta arriva su Hyperliquid (QH)

Scritto il 31 ottobre 2026 alle 00:21 UTC (ora dell'orologio), **prima di qualunque calcolo dei rendimenti**. È un'idea nuova, la 117 della
coda, scritta con la coda vuota. Fino a qui si sono solo contati gli eventi dal primo funding di ogni moneta nello storico di Hyperliquid
già scaricato per la prova 135: 64 monete arrivate su Hyperliquid quando avevano già il perpetuo di Binance da almeno 30 giorni (2023: 36,
2024: 15, 2025: 9, 2026: 4).

## 1. Perché

* **Hyperliquid è la piattaforma degli speculatori sulla catena**: quando quota una moneta, arriva una nuova folla che compra a leva. È
  la famiglia dell'effetto Coinbase (prova 105): l'attenzione di un pubblico nuovo fa salire il prezzo, che poi torna indietro.
* **Dalla prova 135 sappiamo** che su Hyperliquid la leva in eccesso non porta perdite, anzi; quindi il verso non è scontato. Lo si
  scrive qui: si vende.
* **I dubbi scritti prima**:
  * l'effetto Coinbase si è spento dal 2025, e con le quotazioni di OKX non c'era (prova 106);
  * gli eventi sono pochi e quasi tutti del 2023;
  * lo storico di Hyperliquid c'è solo per le monete ancora quotate oggi (sopravvivenza): le monete tolte, spesso quelle andate male, mancano.

## 2. La regola (fissata qui)

* **L'evento**: il giorno del primo funding di una moneta su Hyperliquid (dai file di `research/data/hyperliquid/`, la prova 135), se il
  perpetuo della stessa moneta su Binance esiste da almeno 30 giorni; dal 12 giugno 2023 (un mese dopo l'inizio dello storico, per non
  prendere le monete che c'erano già) al 20 settembre 2026.
* **L'operazione, come la prova 105** (`quarantatreesima.operazione`): short il perpetuo di Binance e long il Bitcoin per lo stesso valore
  dall'apertura del giorno dopo l'evento, uscita a +30% o dopo 7 giorni; costi a mercato e funding.
* **Una prova a eventi**: nel conto delle prove diventano **238**, le prove a eventi **43**.

## 3. L'esame

* **Come le prove a eventi** (`trentesima.esame`, ricampionamento per settimana): media per evento sopra zero con **p ≤ 0,01**, positiva
  nelle due metà e senza i 5 eventi migliori, **e sopra il controllo** (differenza con p ≤ 0,05). Contando le 43 prove a eventi la soglia
  è **0,00023**. Con 64 eventi la prova ha poca forza, e va detto prima.
* **Il controllo**: la stessa operazione sulle stesse monete in 20 giorni presi a caso (seme 2026) fra 60 e 365 giorni dopo l'evento, come
  la prova 105.
* **Se regge**, passa da un revisore separato prima del paper.
* **Per capire, senza decidere niente**: le tenute di 3 e 14 giorni; la moneta contro il Bitcoin nei 7 giorni prima dell'evento; per anno.
