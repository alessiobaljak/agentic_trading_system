# Prova 51 — le acquisizioni pagate in contanti: comprare l'azienda comprata dopo l'annuncio e tenerla fino alla chiusura dell'affare

Regole scritte il 25 novembre 2026 **prima di qualsiasi calcolo e prima di scaricare le notizie** (idea I59 di `REGISTRO.md`). Si
conoscevano le prove 1-50, in particolare la 46 (le notizie dell'archivio di Alpaca: il calo arriva prima che si possa entrare), la 42
(gli attivisti, regole scritte, ferma) e le 27 e 34 (i filtri delle aziende piccole). Contano come **2 prove** (la strategia da sola, e
la miscela con lei): 118 e 119 nel conto.

## Perché dovrebbe funzionare

Quando un'azienda annuncia che ne compra un'altra pagando un prezzo in contanti per azione, il titolo comprato sale subito ma resta un
po' sotto il prezzo offerto: lo scarto è il premio per chi si prende il rischio che l'affare salti (antitrust, finanziamento, voto). È un
**premio per un rischio**, non un'anomalia che sparisce quando la si pubblica: Mitchell e Pulvino, Journal of Finance 56 (2001), circa
il 4% l'anno sopra il tasso senza rischio dal 1963 al 1998, con un legame quasi nullo con il mercato nei periodi normali e forte nei
crolli; Baker e Savasoglu, Journal of Financial Economics 64 (2002), dallo 0,6 allo 0,9% al mese. Non serve essere veloci: la salita
dell'annuncio la si lascia ad altri, si incassa lo scarto che resta (la lezione della prova 46 qui non pesa).

**Sospetti scritti prima:**

* **gli scarti si sono ristretti** dopo il 2002 (Jetley e Ji, 2010): il premio può essere troppo piccolo per i costi;
* **il prezzo offerto si legge dal titolo della notizia**: un titolo scritto male, un affare in parte in azioni o una proposta non
  vincolante possono passare per buoni;
* **quale simbolo è quello comprato** si deduce dai prezzi del giorno prima (sotto, non dopo): un errore mette in conto l'azienda che
  compra;
* **i crolli**: nel marzo 2020 gli scarti si sono allargati di colpo; la parte può perdere proprio quando la miscela perde;
* **la copertura delle notizie cambia negli anni**: meno affari letti all'inizio del periodo.

## I dati

* **Gli annunci:** l'archivio delle notizie di Alpaca (Benzinga, come le prove 28, 29 e 46; licenza: mai nel repository, mai un
  titolo di notizia nei file pubblicati), dal 1° gennaio 2016 al 31 dicembre 2024. Una notizia conta se il titolo:
  * contiene un prezzo per azione: «$X per share», «$X/share» o «$X a share»;
  * contiene «cash», e non contiene «stock and cash», «cash and stock», «in stock», «shares of», «exchange ratio»;
  * dice un accordo: contiene «to acquire», «to be acquired», «agreement to acquire», «definitive agreement» o «agrees to sell»;
  * non è una voce o una proposta: non contiene «proposal», «proposes», «propose», «offer to acquire», «unsolicited», «considering»,
    «explore», «exploring», «talks», «report», «reportedly», «rumor», «nonbinding», «non-binding», «bid for».
* **L'azienda comprata:** fra i simboli della notizia, quelli con la chiusura del giorno di borsa prima della notizia sotto il prezzo
  offerto, con il prezzo offerto fino al doppio di quella chiusura. Se ne resta **uno solo**, è lui; se nessuno o più d'uno, la notizia
  si scarta e si conta. Per ogni azienda vale **il primo annuncio**: le notizie dopo sullo stesso simbolo (rilanci, conferme) non
  aprono posizioni nuove.
* **I prezzi:** barre giornaliere di Alpaca (tutte le borse, aziende sparite comprese), scaricate dal lavoro di GitHub, mai nel
  repository.

## La regola

* **L'ingresso:** alla **chiusura del primo giorno di borsa dopo** quello della notizia (asta di chiusura). Il salto dell'annuncio è già
  avvenuto e non si conta.
* **I filtri, quel giorno:** chiusura di almeno 5 dollari, mediana dei dollari scambiati nelle 20 sedute prima almeno 2 milioni (come
  le prove 27 e 42); lo scarto (prezzo offerto / chiusura − 1) **sopra zero e al massimo del 50%**. Uno scarto negativo vuol dire che
  il mercato aspetta un rilancio; sopra il 50% è quasi sempre un prezzo letto male: si scartano e si contano.
* **L'uscita:** il primo di tre momenti:
  * l'**ultimo giorno di borsa del titolo** (l'affare si chiude e il titolo sparisce), all'ultima chiusura;
  * **365 giorni** dopo l'ingresso, alla chiusura;
  * il 31 dicembre 2024.
  Nessuna uscita sulle notizie dopo (un affare che salta si tiene fino a uno dei tre momenti: la regola non cerca di indovinare).
* **Quanto:** il **5%** del valore del conto all'ingresso per affare, al massimo **20 affari** insieme; oltre, si salta, in ordine
  d'arrivo (a pari giorno, in ordine alfabetico). Azioni intere. Il resto del conto non rende niente. Nessuna copertura con l'indice.
* **Periodo:** annunci dal 1° gennaio 2016 al 31 dicembre 2024. Il periodo chiuso non si usa.

## I costi

Ingresso e uscita all'asta di chiusura: **slittamento di 2 punti base per lato** (titoli meno scambiati delle 500 grandi, come la prova
42), commissioni di Interactive Brokers «fisso» (0,005 dollari ad azione, minimo 1 dollaro, massimo l'1%). Versione con tutti i costi
raddoppiati.

## L'esame (uguale alle prove 28 e 30-50)

**Da sola:** (1) Sharpe annuo con i costi più alto del tenere lo SPY sugli stessi giorni; (2) Sharpe corretto ≥ 0,95 con tutte le serie
del conto; (3) Sharpe sopra zero con i costi doppi; (4) almeno il 60% dei trimestri in guadagno.

**Per entrare nella miscela:** Sharpe con i costi sopra zero, anche con i costi doppi; correlazione con la miscela della prova 25 sotto
0,3; la miscela nuova (tre quarti la miscela, un quarto la parte nuova) con lo Sharpe più alto della miscela e del tenere lo SPY; il t
dello Sharpe della parte almeno 1,3, anche senza marzo 2020; la miscela nuova più alta in almeno l'80% di 2000 campionamenti a blocchi
di 20 giorni.

Da leggere accanto (non cambiano l'esito): quante notizie lette, quante scartate per ogni motivo (simbolo, filtri, scarto, posti); gli
affari per anno; lo scarto medio all'ingresso; i giorni medi di tenuta; la quota di affari chiusi (titolo sparito entro 365 giorni) e il
rendimento medio di quelli chiusi e degli altri; il legame con lo SPY nei mesi in cui lo SPY perde; marzo 2020 da solo; l'anno per anno.

**Se passa uno dei due esami:** revisore separato, poi il periodo chiuso (dal 2 gennaio 2025 al 30 settembre 2026) **una volta**: la
famiglia «acquisizioni» non l'ha mai usato.
