# Prova 12 — le azioni meno nervose dell'S&P 500 (bassa volatilità)

Regole scritte il 24 ottobre 2026 **prima di qualsiasi calcolo** su questa idea (idea I14, nuova), committate prima di lanciare il
programma, **e prima di conoscere l'esito della prova 11**. Famiglia nuova (premi per il rischio, decisione mensile): il periodo chiuso si
può riusare. Conta come **1 prova**.

## Perché dovrebbe funzionare

Le azioni che si muovono meno hanno reso, nella storia, quasi quanto le altre ma con molto meno rischio: il loro rapporto fra guadagno e
rischio (lo Sharpe, cioè proprio quello su cui si giudica) è più alto. Ang, Hodrick, Xing, Zhang, «The cross-section of volatility and
expected returns», *Journal of Finance* 61 (2006); Frazzini, Pedersen, «Betting against beta», *Journal of Financial Economics* 111
(2014): molti investitori non possono usare la leva e comprano azioni nervose per avere più guadagno, pagandole troppo. **Sospetto
scritto prima:** l'effetto è famoso, ci sono fondi che lo copiano (che potrebbero averlo consumato); nel 2016-2024 hanno vinto le grandi
aziende tecnologiche, che sono nervose; i titoli tranquilli sono spesso di pochi settori (servizi pubblici, beni di consumo).

## La regola

* **Titoli:** l'S&P 500 del giorno della decisione, come la prova 11 (composizione storica, cambi di simbolo).
* **Segnale:** alla chiusura dell'ultimo giorno di borsa di ogni mese, la deviazione standard dei rendimenti giornalieri delle ultime
  **252 sedute** (corretti per dividendi, frazionamenti e scissioni). Servono 253 chiusure e la barra di oggi.
* **Acquisti:** i **50 con la volatilità più bassa**, a pesi uguali (un cinquantesimo del 98% del conto), a mercato all'apertura del
  primo giorno di borsa del mese dopo; prima le vendite. Si tiene un mese. Niente vendite allo scoperto, niente leva.
* **Periodo:** decisioni da fine dicembre 2016 (prima non ci sono 252 sedute) al 31 dicembre 2024.

## Costi ed esame

Costi come la prova 11 (scarto misurato per i 34, metà scarto 5 punti base e slittamento 2 per gli altri; Interactive Brokers; costi
doppi; 100'000 dollari). Passa la ricerca se sono vere **tutte**: (1) Sharpe annuo con i costi più alto del tenere lo SPY e del tenere
tutto l'indice a pesi uguali (come la prova 11), sugli stessi giorni; (2) Sharpe corretto ≥ 0,95; (3) Sharpe sopra zero con i costi
doppi; (4) almeno il 60% dei 32 trimestri in guadagno (i trimestri del 2016 senza posizioni non contano come guadagno). Se passa:
revisore separato, poi il periodo chiuso.
