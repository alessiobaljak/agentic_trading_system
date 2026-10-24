# Prova 8 — i titoli appena tolti dall'S&P 500

Regole scritte il 24 ottobre 2026 **prima di qualsiasi calcolo** su questa idea (nuova, idea I12 di `REGISTRO.md`), committate prima di
lanciare il programma. Si conoscevano le prove 1-7 (bocciate). Famiglia nuova (eventi dell'indice, titoli singoli): il periodo chiuso si
può riusare.

## Perché dovrebbe funzionare

Quando un titolo esce dall'indice, i fondi che lo copiano devono venderlo tutti insieme il giorno dell'uscita, a qualunque prezzo: il
prezzo scende più di quanto valga l'azienda e poi recupera nelle settimane dopo. Chen, Noronha, Singal, «The price response to S&P 500
index additions and deletions: evidence of asymmetry and a new explanation», *Journal of Finance* 59 (2004); è lo stesso meccanismo dei
«flussi forzati» che sulle crypto ha dato i soli vantaggi veri (`LEZIONI_DALLE_CRYPTO.md`). **Sospetto scritto prima:** i titoli tolti
sono più piccoli e meno scambiati (costi più alti, non misurati); molti escono perché comprati da un'altra azienda (quelli non
contano: non hanno prezzi dopo); l'effetto è noto da vent'anni e gli speculatori potrebbero anticiparlo.

## La regola

* **Gli eventi:** ogni titolo presente nell'elenco dell'S&P 500 di un giorno e assente in quello del giorno dopo nel file della
  composizione storica (`stock/universo/costruisci.py`, fonte https://github.com/fja05680/sp500). Il giorno dell'uscita è il primo giorno
  in cui il titolo non è più nell'elenco. Periodo: uscite dal 1 maggio 2016 (dopo i primi 4 mesi di dati) al 30 novembre 2024 (così
  l'ultima posizione si chiude entro il 2024). Il periodo chiuso non si tocca.
* **Ingresso:** alla chiusura del giorno di borsa prima dell'uscita si decide (l'uscita è annunciata giorni prima); si compra a mercato
  all'apertura del giorno dell'uscita. Serve che il titolo abbia la barra quel giorno, altrimenti l'evento salta (e si conta).
* **Quanto:** il 10% del valore del conto per titolo, azioni intere, al massimo 10 titoli insieme; se nello stesso giorno ce ne sono più
  di quanti posti liberi, si prendono in ordine alfabetico. Niente leva.
* **Uscita:** si vende a mercato all'apertura del 21° giorno di borsa dopo l'ingresso (si tengono 20 sedute: un mese; numero scelto
  qui, una volta, senza provarne altri). Un titolo che sparisce dal listino nel frattempo (comprato da un'altra azienda) resta valutato
  all'ultima chiusura: si dice quanti.
* Dividendi, frazionamenti e scissioni come nella prova 3.

## I costi

Per questi titoli lo scarto non è misurato: si fissa **prima**, per prudenza, metà scarto = **10 punti base** (lo scarto più largo
misurato fra le 34 grandi è 5,75 punti base) e slittamento = **5 punti base**; commissioni Interactive Brokers «fisso»; versione con i
costi raddoppiati. Dopo il calcolo si misura lo scarto vero negli istanti degli ordini su un campione (come per la prova 2), solo per
sapere se la prudenza bastava: l'esito resta quello dell'esame qui sotto.

## L'esame

Passa la ricerca se sono vere **tutte**: (1) Sharpe annuo con i costi più alto del comprare e tenere lo SPY sugli stessi giorni; (2)
Sharpe corretto ≥ 0,95 con tutte le serie del conto; (3) Sharpe sopra zero con i costi doppi; (4) almeno il 60% dei 32 trimestri di
prova in guadagno. Accanto, da leggere: il guadagno medio per evento e il suo t. Conta come **1 prova**.
