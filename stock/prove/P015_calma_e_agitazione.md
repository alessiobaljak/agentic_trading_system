# Prova 15 — più investiti quando il mercato è calmo, meno quando è agitato (SPY, QQQ)

Regole scritte il 24 ottobre 2026 **prima di qualsiasi calcolo** su questa idea (idea I16, nuova), committate prima di lanciare il
programma. Famiglia nuova (quanto investire secondo l'agitazione recente): il periodo chiuso si può riusare. Contano come **2 prove**.

## Il ragionamento

Mettendo insieme tre cose osservate in questa ricerca e fuori: (a) i guadagni dell'indice arrivano soprattutto nei periodi calmi, mentre
le perdite grandi arrivano a grappoli nei periodi agitati (marzo 2020, 2022: le perdite massime del 25-35% di tutte le prove sul
tenere); (b) l'agitazione di oggi dice molto su quella delle prossime settimane, mentre la direzione no (le prove 1, 3, 5, 11 sulla
direzione sono bocciate); (c) lo Sharpe, su cui giudichiamo, premia proprio chi evita le perdite grandi. Se si investe di più quando la
volatilità recente è bassa e di meno quando è alta, il rischio diventa più costante e lo Sharpe dovrebbe salire. Lo hanno studiato
Moreira, Muir, «Volatility-managed portfolios», *Journal of Finance* 72 (2017). **Sospetto scritto prima:** Cederburg e altri (*Journal
of Financial Economics* 2020) trovano che fuori dal campione il vantaggio spesso sparisce; i crolli veloci (febbraio 2020) arrivano
quando la volatilità recente è ancora bassa, cioè quando si è più investiti.

## La regola (due numeri, fissati qui senza provarne altri)

* **Titoli:** SPY e QQQ, ognuno da solo; prezzi al giorno con dividendi e frazionamenti (simulatore a più titoli).
* **Agitazione:** alla chiusura dell'ultimo giorno di borsa di ogni settimana, la deviazione standard annua dei rendimenti giornalieri
  delle ultime **21 sedute** (un mese).
* **Quanto investire:** quota = **16% / agitazione** (il 16% è all'incirca la volatilità annua di lungo periodo dell'S&P 500, nota da prima
  del 2016), tagliata fra 0 e **1,5** (leva massima). Si porta la posizione a quota × 98% del conto all'apertura del giorno di borsa dopo.
  Se la differenza dalla posizione attuale è sotto il 10% del conto, non si fa niente (per non pagare costi per piccoli aggiustamenti).
* **Interesse sul prestito** 6% l'anno come la prova 14; costi come le prove precedenti.
* **Periodo:** dal primo venerdì con 22 chiusure (febbraio 2016) al 31 dicembre 2024.

## L'esame

Passa la ricerca se sono vere **tutte**: (1) Sharpe annuo con i costi più alto del comprare e tenere lo SPY e del comprare e tenere lo
stesso titolo, sugli stessi giorni; (2) Sharpe corretto ≥ 0,95 con tutte le serie del conto; (3) Sharpe sopra zero con i costi doppi;
(4) almeno il 60% dei 32 trimestri in guadagno. Se passa: revisore separato, poi il periodo chiuso con l'esame della prova 2.

## L'esame nel periodo chiuso (scritto il 24 ottobre 2026, dopo la bocciatura sul 2016-2024 e prima di aprirlo)

**Eccezione decisa dal proprietario** (24 ottobre: «sì, prova la 15 sul periodo chiuso»): la prova 15 non ha passato la condizione 2
(Sharpe corretto 0,67 e 0,79 contro 0,95), quindi per il metodo non andrebbe sul periodo chiuso. Ci va per decisione del proprietario,
dopo il revisore separato. Lo si scrive qui perché resti chiaro.

Periodo: dal 2 gennaio 2025 al 30 settembre 2026, stessi titoli, stesse regole, stessi costi (scarto misurato sul 2016-2024, interesse
6%). I prezzi di novembre e dicembre 2024 servono solo per avere le 21 sedute di storia: la prima decisione è l'ultimo giorno di borsa
della prima settimana del 2025 (fino all'esecuzione si sta in contanti; il comprare e tenere parte dal 2 gennaio). Si apre **una volta
sola**. Per ogni titolo passa se sono vere **tutte**: (1) Sharpe annuo con i costi più alto del comprare e tenere lo SPY e del comprare e
tenere lo stesso titolo sugli stessi giorni; (2) Sharpe con i costi doppi sopra zero; (3) almeno 4 trimestri su 7 in guadagno. Nel conto:
**1 apertura in più** (28).
