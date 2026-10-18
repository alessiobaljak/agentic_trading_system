# M-001 — Ogni mese i segnali che hanno funzionato nei mesi prima

Scheda scritta il 18 ottobre 2026 **prima di qualunque calcolo** (REGOLE.md, sezione 8).

## La procedura

* **Candidate**: tutte le celle a una moneta di `esplora_fase2.celle_moneta` (famiglie F1, G1, F5-F13, P1-P3, L0-L2) e di
  `esplora_calendario.celle` (W1-W5), ognuna nei due versi («segue» e «contro»): circa 900 candidate. Monete: le 24 della
  fase 2 (`strumenti/fase2.py`). Barre di un'ora dal 2020-01-01 (con 100 giorni di storia) al 2026-09-30.
* **Trade di una candidata**: come nell'esplorazione (decisione alla chiusura dell'ora, ingresso all'apertura dell'ora
  dopo, uscita alla chiusura dell'ora t+h, pausa per moneta), con il netto dopo i costi: per lato commissione 0,05% e scarto
  **doppio** (0,02% BTC, ETH, SOL; 0,04% le altre), funding; per G1 anche la gamba di BTC per |β|.
* **Ogni inizio mese** m (dal 2020-07): per ogni candidata, i trade **chiusi** nei L mesi prima di m (uscita prima
  dell'inizio di m): numero, netto medio, t per gruppi di giorni. Si scelgono le **K candidate con il t più alto** fra
  quelle con almeno 30 trade, netto medio > 0 e t ≥ 2, **al massimo 2 per famiglia** e mai i due versi della stessa cella.
  Nel mese m si prendono tutti i trade delle scelte con ingresso nel mese m (anche se escono dopo).
* **Varianti** (giudicate insieme): M-001a L = 6 mesi, K = 10; M-001b L = 3 mesi, K = 10; M-001c L = 12 mesi, K = 10.

## L'esame

REGOLE.md, sezione 8: sul periodo dal 2021-01 al 2026-09 (i mesi del 2020 servono solo da storia), p ≤ 0,005 / 3, costi
doppi, giorno migliore tolto, almeno 4 anni su 6 positivi, V2 positivo, 60% delle monete, e la prova a placebo (il
segno del lordo di ogni trade tirato a caso, 20 ripetizioni: la media dei netti dei trade scelti deve essere non sopra
meno i costi medi, cioè nessun guadagno).
