# Prova 11 — il rimbalzo dopo le cadute della settimana, su tutte le azioni dell'S&P 500

Regole scritte il 24 ottobre 2026 **prima di qualsiasi calcolo** su questo universo, committate prima di lanciare il programma (idea
I3 allargata: decisione del proprietario del 24 ottobre, «sì, allarga a tutte le azioni dell'S&P 500»). Si conosceva la prova 3 (la
stessa idea sulle 10 più scambiate: bocciata, Sharpe 0,91 contro 0,94). È la stessa famiglia della prova 3 ma un universo diverso: conta
come **1 prova nuova** (20 nel conto).

## Perché dovrebbe funzionare, e perché qui più che nella prova 3

Chi compra le azioni appena vendute in massa viene pagato per dare liquidità (Lehmann 1990; Lo, MacKinlay, *Review of Financial
Studies* 3, 1990; Nagel, *Review of Financial Studies* 25, 2012). Negli studi l'effetto è più forte sulle aziende meno grandi e meno
seguite, che la prova 3 non aveva. **Sospetto scritto prima:** il rimbalzo di una settimana è uno degli effetti più noti e più
sfruttati dai fondi veloci; i titoli che cadono di più sono spesso quelli con notizie vere (che non rimbalzano); e con 20 titoli
cambiati ogni settimana i costi sono alti.

## La regola

* **Titoli:** ogni settimana, quelli che erano nell'S&P 500 l'ultimo giorno di borsa della settimana (composizione storica,
  `stock/universo/costruisci.py`), con i 18 cambi di simbolo del 2016-2024 (`stock/universo/cambi_di_nome.csv`: si usa il simbolo nuovo,
  che su Alpaca ha la storia di prima). Prezzi al giorno di Alpaca non rettificati; dividendi, frazionamenti e scissioni applicati dal
  simulatore a più titoli.
* **Segnale:** alla chiusura dell'ultimo giorno di borsa della settimana, il rendimento delle ultime 5 sedute di ogni titolo (corretto
  per dividendi, frazionamenti e scissioni). Servono 6 chiusure e la barra di oggi.
* **Acquisti:** i **20 con il rendimento più basso**, a pesi uguali (un ventesimo del 98% del conto), azioni intere, a mercato
  all'apertura del giorno di borsa dopo; prima le vendite di ciò che esce. Si tiene fino alla settimana dopo. Niente vendite allo
  scoperto, niente leva.
* **Periodo:** decisioni dal primo venerdì con 6 chiusure (gennaio 2016) al 31 dicembre 2024.

## I costi (fissati prima)

* Per i 34 titoli con lo scarto misurato (`stock/dati/ESITO_CONTROLLI_UNIVERSO.md`): metà della mediana misurata + 0,5 punti base di
  slittamento, come la prova 3.
* Per tutti gli altri, **per prudenza**: metà scarto **5 punti base** (scarto 10: più del 33° dei 34 misurati) + **2 punti base** di
  slittamento. La stima dello scarto dai soli prezzi giornalieri (Abdi e Ranaldo 2017) è stata provata sui 34 misurati e non funziona
  (dà zero per Apple e 46 punti base per Microsoft): non si usa.
* Commissioni Interactive Brokers «fisso», costi raddoppiati, capitale 100'000 dollari. Dopo il calcolo si misura lo scarto vero negli
  istanti degli ordini su un campione, solo per sapere se la prudenza bastava.

## L'esame

Passa la ricerca se sono vere **tutte**: (1) Sharpe annuo con i costi più alto del comprare e tenere lo SPY e del **comprare e tenere
gli stessi titoli** (tutti i titoli dell'indice a pesi uguali, ribilanciati a mercato il primo giorno di borsa di ogni mese, stessi
costi); (2) Sharpe corretto ≥ 0,95 con tutte le serie del conto; (3) Sharpe sopra zero con i costi doppi; (4) almeno il 60% dei 32
trimestri in guadagno. Se passa: revisore separato, poi il periodo chiuso (una volta sola).
