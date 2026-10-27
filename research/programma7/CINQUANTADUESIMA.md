# Programma 7 — cinquantaduesima prova: il premio coreano fra le monete, deciso ogni giorno (KP)

Scritto il 27 ottobre 2026 alle 16:40 UTC, **prima di scaricare i prezzi di Upbit e prima di qualunque calcolo**. Fino a qui si è
guardato solo quante monete dell'universo hanno un mercato in won su Upbit: fra 21 e 67 a settimana, 55 di mediana. È un'idea nuova,
che entra nella coda come 81. È trading di ogni giorno: la decisione si prende ogni giorno come G1, con gli ordini limite.

## 1. Perché

* **I coreani a volte pagano una moneta più di tutto il mondo.** In Corea i soldi non escono e non entrano liberamente, quindi chi
  vorrebbe comprare su Binance e rivendere su Upbit non può farlo in grande. Il prezzo in won può restare sopra quello del resto del
  mondo per settimane (Makarov e Schoar 2020, *Journal of Financial Economics*). Quando il premio di una moneta sale più di quello delle
  altre, è la domanda dei piccoli investitori coreani per quella moneta.
* **Chi compra quello di cui tutti parlano paga troppo.** È la famiglia che per noi regge (N3, la prova 113 sulle monete regalate). Per
  la Corea in particolare, la prova 41 (vendere dopo l'arrivo di una moneta su Upbit) faceva +2,96% a evento, nella stessa direzione,
  ma senza abbastanza sicurezza.
* **La direzione scritta prima**: **short le monete con il premio coreano più alto rispetto alle altre, long quelle con il più basso**,
  su Binance.
* **I dubbi scritti prima**:
  * la stessa idea sul premio di Coinbase (prova 87) non reggeva: la differenza fra le monete era piccola (0,15%) e si arbitraggiava;
  * lì il verso «compra chi ha il premio alto» faceva meglio del contrario.

  Il premio coreano è diverso perché l'arbitraggio è bloccato dalle regole sui cambi, e la prova dice se basta.

## 2. Dati e periodo (fissati qui)

* **Periodo**: dal 4 gennaio 2021 (l'inizio di G1, `sesta.INIZIO`) al 19 ottobre 2026, l'ultima settimana intera con i dati.
* **Universo**: ogni giorno, le monete delle 100 più scambiate della settimana (come G1) che hanno un mercato in won su Upbit.
  * Si usano i 299 mercati in won che esistono oggi (`api.upbit.com/v1/market/all`), abbinati ai perpetui con `annunci.perpetuo`
    (242 abbinati).
  * **Riserva**: i mercati che Upbit ha già chiuso non sono nell'elenco e non si possono scaricare.
* **I prezzi di Upbit**: le candele giornaliere in won (`/v1/candles/days`, giornata da 00:00 a 00:00 UTC, la stessa di Binance),
  salvate in `research/data/upbit/giorni/` fuori da git. Per Binance le chiusure giornaliere del pannello del programma 6.
* **Il premio relativo** della moneta j alla chiusura del giorno t:
  * P = (prezzo in won di j / prezzo in won del Bitcoin) / (prezzo su Binance di j / prezzo su Binance del Bitcoin) − 1;
  * per i perpetui con il prefisso dei multipli (1000PEPE e simili) il prezzo di Binance si divide per il multiplo;
  * così si toglie il cambio fra won e dollaro, e anche il premio di tutto il mercato coreano, che si vede già nel Bitcoin.
* **Dati non validi**, scartati:
  * un |P| sopra il 20%: è una sigla abbinata alla moneta sbagliata, oppure Upbit ha bloccato depositi e prelievi;
  * un giorno con meno di 100 milioni di won scambiati su Upbit: il prezzo può essere fermo.

## 3. La regola

* **Il segnale per il giorno d**: la media di P nei 7 giorni prima (da d − 7 a d − 1), con almeno 5 giorni validi. È lo stesso
  allineamento del funding dei 7 giorni di G1.
* **I pesi**: come G1 (`ventiquattresima.pesi_banda` con il segnale −P medio, la volatilità dei 30 giorni e la banda 20/40).
  * Long il quinto con il premio più basso, short il quinto con il premio più alto.
  * Una moneta già dentro resta finché non esce dal 40% del suo lato.
  * Pesi secondo l'inverso della volatilità, lati uguali in dollari.
  * Almeno 20 monete con il segnale, altrimenti nessuna posizione quel giorno.
* **Esecuzione e costi**: come G1, decisione alle 00:00 UTC, le variazioni a ordine limite per un'ora e poi a mercato
  (`cinquantaseiesima.spese_a_limite`). Il funding come G1.
* **Una prova a portafoglio**: nel conto delle prove diventano **209**.

## 4. L'esame

* **Come G1** (`terza.esame` e `terza.esito`): lo Sharpe corretto con l'aggiunta (`asticella.corretto_rivisto`) sopra la soglia 0,95,
  e accanto il t dello Sharpe contro 3.
* **La regola del proprietario del 24 ottobre**: con lo Sharpe corretto da 0,90 in su, positiva in ogni anno e con il t sopra 3, non
  si boccia.
* **Se regge**, passa da un revisore separato prima del paper.
* **Per capire, senza decidere niente**:
  * il verso opposto;
  * la correlazione con G1 sulle stesse settimane;
  * per anno;
  * quante monete hanno il segnale ogni giorno;
  * la differenza tipica del premio fra le monete (lo scarto fra il quinto più alto e il più basso), da confrontare con lo 0,15% di
    Coinbase.
