# Programma 7 — cinquantasettesima prova: la crescita degli utenti, a settimana (CU)

Scritto il 28 ottobre 2026 alle 08:20 UTC (ora dell'orologio), **prima di scaricare il dato sugli indirizzi con saldo e prima di
qualunque calcolo**. Fino a qui si è contato solo quante monete hanno il dato: 52 con il perpetuo, 27 a settimana nell'universo
(mediana, fra 16 e 37). È l'idea 87 della coda, dalla ricerca nella letteratura del 28 ottobre. È una prova a settimana.

## 1. Perché

* **Una moneta che conquista nuovi possessori ha più domanda.** Se in una settimana gli indirizzi con un saldo crescono più che nelle
  altre monete, è adozione che accelera, e la domanda porta il prezzo su.
* **Cosa dice la letteratura**: Cong, Karolyi, Tang e Zhao (*Management Science*) trovano +4,0% a settimana fra le monete con la
  crescita più alta e quelle con la più bassa, t 2,8, su 616 monete dal 2014 al gennaio 2021.
* **La direzione scritta prima**: long le monete con la crescita più alta, short quelle con la più bassa.
* **I dubbi scritti prima**:
  * Liu, Tsyvinski e Wu (2021) trovano che il prezzo prende la notizia subito, senza scia;
  * il valore misurato con gli utenti (prova 116), con la stessa fonte e le stesse monete, si è spento dopo il 2022;
  * il dato si può gonfiare con indirizzi spazzatura e distribuzioni di gettoni.

## 2. Dati e regola (fissati qui)

* **Dati**: `AdrBalCnt` (indirizzi con un saldo sopra zero, giornaliero) di CoinMetrics community, salvato in
  `research/data/coinmetrics/` fuori da git. Le monete abbinate ai perpetui sono le stesse della prova 116.
* **Il segnale del lunedì l**: indirizzi con saldo del giorno l − 2 diviso quelli del giorno l − 9, meno 1, cioè la crescita di una
  settimana. I due giorni di ritardo servono alla pubblicazione. Una crescita sopra il 50% in una settimana si scarta: è un errore del
  dato o una distribuzione di massa.
* **Universo, periodo e pesi**: come la prova 116.
  * Le monete delle 100 più scambiate della settimana con il dato, almeno 20 per settimana.
  * Dal 4 gennaio 2021 all'ultima settimana intera.
  * Long il quinto con la crescita più alta, short il quinto con la più bassa, banda 20/40 (`ventiquattresima.pesi_banda`).
  * Pesi secondo l'inverso della volatilità dei 30 giorni, lati uguali in dollari.
  * Cambio delle posizioni ogni lunedì, con i costi a mercato e il funding (`terza.conto`).
* **Una prova a portafoglio**: nel conto delle prove diventano **215**.

## 3. L'esame

* **Come F5** (`terza.esame`, `terza.esito`): lo Sharpe corretto con l'aggiunta sopra 0,95, il t contro 3 e la regola del
  proprietario del 24 ottobre.
* **Se regge**, passa da un revisore separato.
* **Per capire, senza decidere niente**: il verso opposto; per anno; la correlazione con F5 e con la prova 116.
