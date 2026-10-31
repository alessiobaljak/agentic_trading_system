# Programma 7 — ottantunesima prova: il momento dei settori (SM)

Scritto il 31 ottobre 2026 alle 12:27 UTC (ora dell'orologio), **prima di qualunque calcolo**. È l'idea 121 della coda, scritta oggi
con la coda quasi vuota. Usa i settori di CoinGecko già scaricati per la prova 142 (G1S), con le stesse regole di abbinamento; della
prova 142 si conosce solo quanto pesavano i settori dentro G1, non come vanno i settori uno contro l'altro.

## 1. Perché

* **Nelle azioni il momento dei settori è uno dei fatti più solidi** (Moskowitz e Grinblatt 1999): i settori saliti di più nei mesi
  prima continuano a salire, e spiegano buona parte del momento delle singole azioni.
* **Nei perpetui delle monete**: la tesi di Luo (Edimburgo, giugno 2025, «Three essays on futures expected returns»; letto solo il
  riassunto) trova il momento delle singole monete debole nei perpetui, ma un momento **per categoria** «forte e diffuso», che
  spiega gran parte di quello delle singole monete. Il perché proposto: i soldi entrano in un racconto (le meme, l'intelligenza
  artificiale, i giochi) e ci restano per settimane, e le monete grandi dello stesso settore si muovono insieme con un ritardo.
* **È una famiglia diversa** da quella che regge (chi paga la leva o la novità perde): non guarda il funding né l'età. Se funziona, è
  una gamba in più per il conto unico, poco legata a G1.
* **I dubbi scritti prima**:
  * il momento delle singole monete a 3 settimane non ha retto (prova 49, Sharpe 0,05), e quello dei vicini deciso ogni giorno è
    stato mangiato dai costi (prova 118);
  * **i settori sono quelli di oggi** (CoinGecko, letti il 31 ottobre): una moneta può aver cambiato racconto, e le monete morte
    prima di oggi possono mancare dalle categorie (finiscono in «altro» e restano fuori);
  * i settori sono pochi (6), quindi ogni lato contiene uno o due settori interi: è una scommessa concentrata;
  * la tesi non dice (nel riassunto) la finestra di formazione: la scelgo qui, 4 settimane, la più usata per il momento delle
    monete (Liu, Tsyvinski e Wu 2022 trovano il momento fra 1 e 4 settimane).

## 2. La regola (fissata qui)

* **I settori**: quelli della prova 142 (`ottantesima.settore_di`, file `research/data/coingecko_settori.json`): meme, intelligenza
  artificiale, giochi, finanza decentralizzata, reti di secondo livello, reti principali; le monete in nessuno di questi («altro»)
  restano fuori, dal segnale e dal portafoglio.
* **L'universo**: ogni lunedì l, le monete dell'universo della settimana (`terza.pannello_settimane`, le stesse di F5), senza il
  Bitcoin, con il perpetuo nato da almeno 37 giorni (come la prova 131) e con la volatilità dei 30 giorni nota.
* **Il segnale**: per ogni moneta il rendimento dalla chiusura del giorno l − 29 a quella del giorno l − 1 (4 settimane, solo prezzi
  già noti il lunedì alle 00:00); per ogni settore con **almeno 5 monete** quel lunedì, la media semplice delle sue monete.
* **Il portafoglio**: se i settori con almeno 5 monete sono almeno 4, si ordinano per segnale; k = il più grande fra 1 e un terzo dei
  settori arrotondato in giù; **long tutte le monete dei k settori saliti di più, short tutte quelle dei k settori saliti di meno**;
  dentro ogni lato i pesi secondo l'inverso della volatilità dei 30 giorni (`ottava.sigma_30`), ogni lato somma 1 (come F5). Con meno
  di 4 settori la settimana è ferma.
* **Il conto**: come F5, a settimana dal lunedì, costi a mercato sul giro e funding (`terza.conto`).
* **Periodo**: dal 4 gennaio 2021 (`sesta.INIZIO`) a fine settembre 2026.
* **Una prova**: nel conto delle prove diventano **241**.

## 3. L'esame (scritto prima)

* Lo stesso delle prove a portafoglio (`terza.esame`, `terza.esito`), con lo Sharpe corretto rivisto per tutte le prove
  (`asticella.corretto_rivisto`) e la regola del proprietario del 24 ottobre (Sharpe corretto da 0,90 in su, ogni anno positivo, t
  sopra 3).
* **Il controllo dei settori mescolati**: 20 volte, le etichette dei settori si rimescolano a caso fra le monete (una volta per giro,
  fisse per tutto il periodo, stessi numeri di monete per settore); la regola identica sui settori finti. Se lo Sharpe vero non sta
  sopra almeno 19 dei 20 finti, il momento non viene dai settori ma dalle singole monete, e la prova non passa anche se lo Sharpe è
  alto.
* **Per capire, senza decidere niente**: la stessa regola con 1 e con 12 settimane di formazione; quante settimane ferme; quali
  settori stanno più spesso da ciascun lato; la correlazione con G1 (settimane della prova 57) e con F5.
