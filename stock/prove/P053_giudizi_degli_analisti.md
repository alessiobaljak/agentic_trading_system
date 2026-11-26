# Prova 53 — i giudizi degli analisti: comprare dopo una promozione, vendere allo scoperto dopo una bocciatura, coperti con lo SPY

Regole scritte il 26 novembre 2026 **prima di qualsiasi calcolo** (idea I61 di `REGISTRO.md`). Si conoscevano le prove 1-52, in
particolare la 46 (stessa fonte e stessa forma: le notizie dell'archivio di Alpaca, ingresso alla chiusura del giorno dopo, 20 sedute
coperti con lo SPY; il calo arrivava prima di poter entrare) e la 28 (il tono delle notizie). `IDEE_DA_GITHUB.md` scartava i consigli
degli analisti perché servono dati a pagamento: l'archivio delle notizie li riporta nei titoli, e qui si usano quelli. Contano come
**2 prove** (la strategia da sola, e la miscela con lei): 122 e 123 nel conto.

## Perché dovrebbe funzionare

Womack, Journal of Finance 51 (1996): dopo che un intermediario promuove un titolo il prezzo continua a salire per circa un mese (+2,4%),
dopo una bocciatura continua a scendere per mesi (−9,1% in sei mesi per i passaggi a «vendere»). Loh e Stulz, Review of Financial
Studies 24 (2011): una parte dei cambi di giudizio sposta i prezzi anche dopo l'annuncio. Il mercato digerisce lentamente un'opinione
che non è una notizia dell'azienda.

**Sospetti scritti prima (forti):**

* **Barber, Lehavy, McNichols e Trueman, Journal of Finance 56 (2001)**: i portafogli costruiti sui consigli rendono prima dei costi ma
  non dopo; qui le operazioni sono molte;
* **Altınkılıç e Hansen (2009)**: i cambi di giudizio arrivano spesso subito dopo una notizia dell'azienda, che è la vera causa;
* **le 500 grandi** sono le più seguite: la deriva degli studi è più forte nelle piccole;
* **la prova 46**: con le notizie, il movimento arrivava prima di poter entrare;
* **i titoli non dicono sempre a cosa si passa** (da «vendere» a «tenere» è una promozione): si prendono tutte, l'effetto sarà diluito.

## I dati

* **Le notizie:** l'archivio di Alpaca (Benzinga; licenza: mai nel repository, solo conteggi), dal 1° gennaio 2016 al 30 novembre 2024,
  **solo il titolo**. Una **promozione** se il titolo contiene «upgrade», «upgrades» o «upgraded»; una **bocciatura** se contiene
  «downgrade», «downgrades» o «downgraded»; tutte e due: si scarta.
* **Il titolo dell'azienda:** al massimo 3 simboli nella notizia ed **esattamente un membro dell'S&P 500 di allora** (come la prova 46).
* **I prezzi:** barre giornaliere di Alpaca, scaricate dal lavoro di GitHub, mai nel repository.

## La regola (la forma della prova 46)

* **Il giorno dell'annuncio:** lo stesso giorno se la notizia esce prima delle 16:00 di New York in un giorno di borsa, altrimenti il
  primo giorno di borsa dopo.
* **L'ingresso:** alla **chiusura del primo giorno di borsa dopo** quello dell'annuncio (asta di chiusura). Promozione: si compra il
  titolo e si vende allo scoperto lo stesso valore di SPY. Bocciatura: si vende allo scoperto il titolo e si compra lo stesso valore di
  SPY.
* **L'uscita:** alla chiusura della **20ª seduta** dopo l'ingresso (asta di chiusura).
* **Quanto:** il **5%** del valore del conto all'ingresso per il titolo e il 5% nello SPY dalla parte opposta; al massimo **20
  operazioni** aperte insieme; oltre, si salta, in ordine d'ingresso (a pari giorno, alfabetico). Una posizione aperta sullo stesso
  titolo blocca le notizie dopo, finché non esce.
* **Periodo:** annunci dal 4 gennaio 2016 al 30 novembre 2024, uscite entro il 31 dicembre 2024. Il periodo chiuso non si usa.

## I costi

Slittamento di **2 punti base** per lato su titolo e SPY (all'asta, come la prova 46), commissioni di Interactive Brokers «fisso»,
prestito di ciò che si vende allo scoperto **0,5% l'anno** (grandi aziende e SPY, facili da prendere in prestito, come l'IWM della prova
42). Versione con tutti i costi raddoppiati.

## L'esame (uguale alle prove 28 e 30-52)

**Da sola:** (1) Sharpe annuo con i costi più alto del tenere lo SPY sugli stessi giorni; (2) Sharpe corretto ≥ 0,95 con tutte le serie
del conto; (3) Sharpe sopra zero con i costi doppi; (4) almeno il 60% dei trimestri in guadagno.

**Per entrare nella miscela:** Sharpe con i costi sopra zero, anche con i costi doppi; correlazione con la miscela della prova 25 sotto
0,3; la miscela nuova (tre quarti la miscela, un quarto la parte nuova) con lo Sharpe più alto della miscela e del tenere lo SPY; il t
dello Sharpe della parte almeno 1,3, anche senza marzo 2020; la miscela nuova più alta in almeno l'80% di 2000 campionamenti a blocchi
di 20 giorni.

Da leggere accanto (non cambiano l'esito): quante notizie e quante scartate per ogni motivo; per le promozioni e per le bocciature a
parte, il titolo meno lo SPY dalla chiusura prima dell'annuncio all'ingresso (quanto è già successo) e nelle 1, 5 e 20 sedute dopo
l'ingresso, con il t; gli annunci per anno; l'anno per anno.

**Se passa uno dei due esami:** revisore separato, poi il periodo chiuso (dal 2 gennaio 2025 al 30 settembre 2026) **una volta**: la
famiglia «giudizi degli analisti» non l'ha mai usato.
