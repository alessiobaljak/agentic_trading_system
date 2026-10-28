# Programma 7 — cinquantaseiesima prova: il momento dei vicini, deciso ogni giorno (MV)

Scritto il 28 ottobre 2026 alle 06:17 UTC (ora dell'orologio), **prima di qualunque calcolo**. È l'idea 91 della coda, dalla ricerca
nella letteratura del 28 ottobre (`research/letture/letteratura_28ott2026.md`). È trading di ogni giorno, con la decisione alle 00:00
UTC come G1.

## 1. Perché

* **Le notizie arrivano prima ad alcune monete e poi alle loro simili.** Gli investitori guardano poche monete alla volta, quindi
  l'informazione si sparge lentamente.
* Quando le monete che di solito si muovono insieme a una moneta salgono, la moneta le segue nei giorni dopo (il momento della rete:
  Guo, Härdle e Tao 2024, *Journal of Business & Economic Statistics* 42(2), +1,08% al giorno nel 2016-2018, senza costi).
* **La direzione scritta prima**: long le monete i cui vicini sono saliti di più ieri, short quelle i cui vicini sono scesi di più.
* **Cosa c'è di diverso dalle prove già fatte**:
  * I-007 (le altre monete dopo il Bitcoin, al minuto) e I-014 (dopo uno strappo del Bitcoin) guardavano un solo capofila, il
    Bitcoin;
  * I-015 guardava la scossa propria di una moneta rispetto al Bitcoin;
  * qui i «vicini» sono diversi per ogni moneta, e il segnale è il loro movimento, non quello della moneta.
* **I dubbi scritti prima**:
  * la versione al minuto su Binance dura al massimo 10 minuti (Guo, Sang, Tu e Wang 2024);
  * il risultato a 1 giorno è del 2016-2018, su monete piccole e senza costi;
  * ogni giorno si paga un giro.

## 2. La regola (fissata qui)

* **Universo e periodo**: come G1. Ogni giorno, le monete delle 100 più scambiate della settimana, dal 4 gennaio 2021 al 19 ottobre
  2026.
* **I vicini** della moneta j il giorno d:
  * si calcolano le correlazioni dei rendimenti giornalieri (`sc.rendimenti`, da apertura ad apertura) nei 90 giorni da d − 90 a
    d − 1, fra le monete dell'universo del giorno, con almeno 60 giorni validi in comune;
  * i vicini sono le **10 monete più correlate** con j, lei esclusa.
* **Il segnale**: la media dei rendimenti dei 10 vicini nel giorno d − 1. Quel giorno finisce alle 00:00 del giorno d, quindi alla
  decisione il dato è noto.
* **Pesi ed esecuzione**: come G1 (`ventiquattresima.pesi_banda`).
  * Long il quinto con il segnale più alto, short il quinto con il più basso.
  * Banda 20/40, pesi secondo l'inverso della volatilità, lati uguali in dollari.
  * Le variazioni a ordine limite per un'ora, poi a mercato (`cinquantaseiesima.spese_a_limite` del programma 6).
  * Il funding.
* **Una prova a portafoglio**: nel conto delle prove diventano **214**.

## 3. L'esame

* **Come G1**: lo Sharpe corretto con l'aggiunta sopra 0,95, il t contro 3 e la regola del proprietario del 24 ottobre.
* **Se regge**, passa da un revisore separato.
* **Per capire, senza decidere niente**: il verso opposto; la versione senza banda (le posizioni rifatte ogni giorno da capo) tutta a
  mercato; la correlazione con G1; per anno.
