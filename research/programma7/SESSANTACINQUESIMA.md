# Programma 7 — sessantacinquesima prova: la rotazione fra le altcoin e il Bitcoin (RA)

Scritto il 29 ottobre 2026 alle 16:41 UTC (ora dell'orologio), **prima di qualunque calcolo**. È un'idea nuova, la 101 della coda:
nel registro non c'è nessuna prova sul rapporto fra le altcoin, prese tutte insieme, e il Bitcoin. Le prove sulla tendenza erano tutte
su una moneta alla volta (prove 1, 36, 39, 46) o fra monete (prove 3, 49).

## 1. Perché

* **Il denaro si sposta a ondate** fra il Bitcoin e le altcoin: ci sono mesi in cui le altcoin fanno molto meglio del Bitcoin (le
  «stagioni delle altcoin», per esempio l'inizio del 2021 e la fine del 2024) e periodi lunghi in cui fanno molto peggio. Chi compra al
  dettaglio entra tardi e insegue, quindi le ondate durano settimane.
* **La tendenza su un indice** funziona meglio che su una moneta sola: l'indice di tante altcoin toglie il rumore delle singole monete.
  La tendenza nel tempo è documentata su molti mercati (Moskowitz, Ooi e Pedersen 2012) e sul mercato delle crypto (Liu e Tsyvinski 2021).
* **Si decide ogni giorno**, come G1, ma si cambia posizione solo quando cambia la tendenza.
* **I dubbi scritti prima**:
  * le altcoin perdono contro il Bitcoin quasi sempre dal 2022 (è la famiglia di N3 e di N1-N2): la regola potrebbe guadagnare solo
    perché resta quasi sempre venduta sulle altcoin. Per questo c'è il confronto con «sempre venduta» (sezione 4);
  * nelle svolte la tendenza arriva tardi e paga due volte;
  * le prove sulla tendenza di una moneta alla volta non hanno mai retto.

## 2. La regola (fissata qui)

* **L'indice delle altcoin**: ogni giorno le monete dell'universo di G1 (le 100 più scambiate del lunedì, `prima.universo_del_giorno`)
  tranne il Bitcoin, a pesi uguali; il rendimento del giorno è la media dei rendimenti dall'apertura all'apertura dopo
  (`seconda.rendimenti`). Lo scarto del giorno è il rendimento dell'indice meno quello del Bitcoin.
* **Il segnale**, preso ogni giorno alle 00:00 UTC con gli scarti fino al giorno prima: per ognuna delle tre finestre di 20, 60 e 120
  giorni, +1 se la somma dei logaritmi di (1 + scarto) nella finestra è sopra zero, −1 se è sotto. Il peso w è la media dei tre: −1,
  −1/3, +1/3 o +1. Le tre finestre sono quelle usuali della tendenza a più velocità, non scelte su questi dati.
* **La posizione**: long l'indice delle altcoin per w (diviso in parti uguali fra le monete del giorno) e short il Bitcoin per w; con w
  negativo il contrario. La somma è zero: si guadagna solo dallo scarto fra le altcoin e il Bitcoin.
* **Il conto**: come G1 (`cinquantaduesima.conto`, cioè `terza.conto` con le spese degli ordini limite di `cinquantaseiesima`), con il
  funding di ogni moneta.
* **Periodo**: dal 4 gennaio 2021 (`sesta.INIZIO`) al 5 ottobre 2026 (`prima.FINE`); il segnale dei primi giorni usa gli scarti dal
  2020.
* **Una variante**: nel conto delle prove diventano **223**.

## 3. L'esame

* **Come le prove a portafoglio** (`terza.esame`, `terza.esito`, Bitcoin come riferimento): lo Sharpe corretto con l'aggiunta sopra 0,95,
  il t contro 3 e la regola del proprietario del 24 ottobre (corretto da 0,90, ogni anno positivo, t sopra 3).
* **E in più**: lo Sharpe di RA deve essere sopra quello di «sempre venduta sulle altcoin» (w = −1 sempre, stesso conto). Se non lo è, la
  regola non aggiunge niente alla deriva già nota delle altcoin.
* **Se regge**, passa da un revisore separato prima del paper.
* **Per capire, senza decidere niente**: «sempre comprata» (w = +1); ognuna delle tre finestre da sola; i giorni con w a +1, +1/3,
  −1/3 e −1; quante volte cambia w in un anno; per anno; la correlazione con G1; lo scarto dell'indice contro il Bitcoin per anno.
