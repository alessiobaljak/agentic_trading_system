# Prova 3 — il rimbalzo dopo le cadute della settimana (le 10 azioni di allora)

Regole scritte il 24 ottobre 2026 **prima di qualsiasi calcolo** su questa idea (idea I3 di `REGISTRO.md`, sezione 2), committate
prima di lanciare il programma. Prima di scriverle si conoscevano le prove 1 e 2 (regole in giornata su SPY e QQQ, bocciate) e il fatto
che nel 2025-2026 comprare e tenere SPY e QQQ ha avuto uno Sharpe di circa 1,05-1,09 (`P002_chiuso.md`). Questa è un'altra famiglia di
idee (più giorni, azioni singole, contro il movimento): il periodo chiuso si può riusare (decisione del proprietario del 24 ottobre).

## Perché dovrebbe funzionare

Chi compra le azioni che sono appena state vendute in massa viene pagato per dare liquidità a chi ha dovuto vendere: Nagel, «Evaporating
liquidity», *Review of Financial Studies* 25 (2012); l'effetto di rimbalzo delle settimane è descritto già da Lehmann, «Fads, martingales,
and market efficiency», *Quarterly Journal of Economics* 105 (1990). **Sospetto scritto prima:** sulle aziende più grandi e scambiate
l'effetto è più debole che sulle piccole; si tiene solo il lato degli acquisti, quindi la prova porta tutto il rischio del mercato; e
nel 2016-2024 le grandi aziende tecnologiche sono salite molto, il che aiuta qualsiasi regola che le compra.

## La regola (nessun parametro scelto guardando i dati)

* **Titoli:** le 10 azioni «di allora» (`stock/universo/dieci_di_allora.csv`, regole in `stock/universo/costruisci.py`), cioè l'elenco del
  mese in cui cade il giorno dell'esecuzione (l'elenco di un mese usa solo dati fino all'ultimo giorno del mese prima, quindi è noto
  alla decisione). Conta come **1 prova** (in tutto 6 nel conto).
* **Periodo:** decisioni da quando c'è l'elenco (esecuzioni da maggio 2016) al 31 dicembre 2024. Prezzi al giorno di Alpaca non
  rettificati, con dividendi, frazionamenti e scissioni applicati dal simulatore a più titoli (`stock/simulatore/portafoglio.py`); le
  scissioni valgono come un incasso pari alle azioni nuove ricevute al prezzo di apertura del giorno di stacco
  (`stock/dati/integrazioni.py`).
* **Segnale:** alla chiusura dell'ultimo giorno di borsa di ogni settimana, per ognuno dei 10 il rendimento delle ultime 5 sedute
  (dalla chiusura di 5 giorni di borsa prima alla chiusura di oggi), corretto per dividendi, frazionamenti e scissioni. Serve la storia
  di 6 chiusure, altrimenti il titolo quella settimana non si considera.
* **Acquisti:** i **3 con il rendimento più basso**, a pesi uguali (un terzo ciascuno del 98% del conto), azioni intere. Ordini a
  mercato all'apertura del giorno di borsa dopo; prima le vendite di ciò che esce, poi gli acquisti. Si tiene fino alla decisione
  della settimana dopo. Niente vendite allo scoperto, niente leva.
* **Titoli spariti:** un ordine per un titolo che il giorno dopo non ha la barra non si esegue e viene contato; un titolo tolto dal
  listino con azioni in mano resta valutato all'ultima chiusura (va detto nei risultati).

* **Cambi di nome** *(correzione del 24 ottobre, scritta dopo il primo calcolo, `P003_risultati_con_errore_FB.md`)*: un titolo che
  cambia simbolo resta lo stesso titolo. FB è diventato META il 9 giugno 2022: si usa META per tutto il periodo (su Alpaca le due storie
  sono identiche fino a quel giorno). Il primo calcolo trattava FB come un titolo sparito dal listino: restava «in mano» senza poter
  essere venduto e bloccava gli acquisti (134 ordini senza barra, 191 rifiutati). È un errore dei dati, non una scelta della regola.

## I costi

* **Scarto:** per ogni titolo, metà della sua mediana misurata (`stock/dati/ESITO_CONTROLLI_UNIVERSO.md`, misura sul primo giorno di
  ogni trimestre 2016-2024, come per i 12 titoli di prova). Per un titolo senza misura: la mediana più alta misurata fra i 34.
* **Slittamento** 0,5 punti base, **commissioni** Interactive Brokers «fisso» (0,005 dollari per azione, minimo 1, massimo l'1%; da
  verificare), versione con i costi raddoppiati, capitale 100'000 dollari. Come le prove 1 e 2.

## L'esame (fissato qui)

Passa la ricerca se sono vere **tutte**:

1. Lo Sharpe annuo con i costi è più alto di quello del **comprare e tenere lo SPY** (con i dividendi) **e** di quello del **comprare e
   tenere gli stessi titoli**: le 10 di allora a pesi uguali, ribilanciate a mercato il primo giorno di borsa di ogni mese, con lo
   stesso simulatore e gli stessi costi (`METODO.md`, sezione 1).
2. Lo Sharpe corretto per i tentativi ≥ 0,95 (stessa procedura delle prove 1 e 2, con tutte le serie del conto, compresa quella del
   periodo chiuso della prova 2).
3. Con i costi raddoppiati lo Sharpe resta sopra zero.
4. Almeno il 60% dei 32 trimestri di prova (2017-2024) in guadagno dopo i costi.

**Se passa:** revisore separato, poi il periodo chiuso (gennaio 2025 → settembre 2026) con l'elenco delle 10 costruito con la stessa
regola, una volta sola, con l'esame della prova 2 (batte il tenere lo SPY e il tenere gli stessi titoli, costi doppi sopra zero, almeno 4
trimestri su 7 in guadagno). Se non passa: bocciata nel registro.
