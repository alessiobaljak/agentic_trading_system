# Programma 7 — settantunesima prova: il primo flusso di ogni quarto d'ora (QO)

Scritto il 30 ottobre 2026 alle 00:32 UTC (ora dell'orologio), **prima di qualunque calcolo**. È l'idea 108 della coda (dalla ricerca
nelle pubblicazioni del 29 ottobre). Nessun dato di questa prova è ancora stato scaricato.

## 1. Perché

* **Gli algoritmi che eseguono grandi ordini a pezzi partono agli orari tondi** (i minuti 0, 15, 30 e 45 di ogni ora). Il verso del
  primo pezzo dice dove spingerà il resto dell'ordine nelle ore dopo.
* **La fonte**: Kim e Hansen, «The Quarter-Hour Effect: Periodic Algorithmic Trading and Return Predictability in Cryptocurrency
  Futures» (arXiv 2607.09426, luglio 2026, letto). Sui 6 perpetui di Binance BTC, ETH, XRP, SOL, DOGE e ADA, dal gennaio 2021
  all'ottobre 2024: lo squilibrio fra acquisti e vendite aggressivi nei primi 10 secondi dei quarti d'ora prevede il rendimento delle
  4-12 ore dopo, nello stesso verso (10-27 punti base lordi fra il primo e il terzo quartile). Gli autori non fanno una strategia con i
  costi.
* **Si decide sul periodo che lo studio non ha visto**: dal 1° novembre 2024 al 30 settembre 2026.
* **I dubbi scritti prima**:
  * il guadagno lordo dello studio (10-27 punti base) è vicino al costo di un giro (12 punti base a mercato sulle monete grandi);
  * le candele a 1 minuto dicono gli acquisti aggressivi del primo minuto, non dei primi 10 secondi: il segnale è più rumoroso;
  * un altro studio dello stesso mese (Kitron e Wengrowicz, arXiv 2608.21888) trova a 15 minuti un lordo di 1,3 punti base contro 5 di
    costo; lo squilibrio degli acquisti aggressivi (prova 9, I-005 del programma 5) non ha mai retto.

## 2. La regola (fissata qui)

* **Dati**: le candele a 1 minuto dei 6 perpetui dello studio dall'archivio pubblico di Binance (file mensili), con il volume degli
  acquisti aggressivi; si tengono solo i primi minuti dei quarti d'ora e le aperture delle ore. Salvate fuori da git.
* **Lo squilibrio di un quarto d'ora**: nel primo minuto, (acquisti aggressivi − vendite aggressive) / volume del minuto.
* **Il segnale**, ogni 4 ore (alle 00, 04, 08, 12, 16 e 20 UTC): la somma degli squilibri degli ultimi 32 quarti d'ora (8 ore).
* **La posizione per le 4 ore dopo**: long se il segnale è sopra zero e sopra la sua mediana delle 180 decisioni prima (30 giorni),
  short se è sotto zero e sotto la mediana; altrimenti fuori. Ogni moneta per conto suo, con lo stesso peso.
* **Costi**: a mercato, come il Bitcoin delle prove a eventi (`ventunesima.COSTO_BTC`, 0,12% andata e ritorno) ogni volta che si apre
  o si chiude; se la posizione resta nello stesso verso alla decisione dopo, non si paga niente. Funding: un terzo del funding del
  giorno per ogni regolamento delle 00, 08 e 16 UTC dentro la tenuta.
* **Una prova a eventi**: ogni tenuta di 4 ore con una posizione è un'operazione. Nel conto delle prove diventano **230**, le prove a
  eventi **40**.

## 3. L'esame

* **Come le prove a eventi** (`trentesima.esame`, ricampionamento per settimana): media per operazione sopra zero con **p ≤ 0,01**,
  positiva nelle due metà e senza le 5 operazioni migliori. Contando le 40 prove a eventi la soglia è **0,00025**.
* **Il controllo**: la stessa regola con lo squilibrio preso al settimo minuto di ogni quarto d'ora invece che al primo. La regola del
  primo minuto deve rendere **di più** del controllo (differenza delle medie per operazione, ricampionamento per settimana, p ≤ 0,05):
  se il settimo minuto rende uguale, l'orario tondo non conta.
* **Se regge**, passa da un revisore separato prima del paper.
* **Per capire, senza decidere niente**: il lordo; per moneta; per anno; le tenute di 8 e 12 ore.
