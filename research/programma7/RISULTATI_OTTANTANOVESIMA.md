# Risultati della prova 151 (ottantanovesima): il weekend dei perpetui su azioni, il rimbalzo del lunedi'

Calcolo di `ottantanovesima.py` (seme 2026), una sola variante come scritto in `OTTANTANOVESIMA.md`. Elenco dei contratti: `risultati_ottantanovesima/ELENCO_CONTRATTI.md` (fissato prima del calcolo).

**Esito secondo le regole: dati troppo corti (netto non positivo; 2 trimestri negativi; t -0.20 sotto 3; Sharpe corretto 0.09 sotto 0,80; un lato da solo sotto zero senza i 3 lunedi' migliori)**

* Lunedi' usati: 23 (dal 2026-06-01 al 2026-11-02); saltati per meno di 20 contratti: 21. Contratti per lunedi': min 20, mediana 30, max 30 (contratti dell'elenco con candele: 123).
* Netto: -9.57% l'anno (media per lunedi' x 52), -6.11% sull'intero periodo; discesa piu' grande -16.56%.
* Sharpe -0.31; t -0.20; Sharpe corretto (N=309) 0.09 (solo gruppi: 0.08).
* Settimane positive: 10 su 23. Per trimestre (somma dei rendimenti): 2026Q2 -7.45%, 2026Q3 -4.25%, 2026Q4 7.47%; trimestri negativi 2.
* Lato long -13.29% l'anno, lato short 17.13% l'anno (lordi di costi e funding). Senza i 3 lunedi' migliori, media per lunedi': netto -1.29%, long -0.26%, short -0.76%.
* Scarto di prezzo 0,05% (controllo, non entra nel giudizio): -12.84% l'anno, Sharpe -0.41, t -0.27.
* Costi: lordo 3.84% l'anno; spese 13.77% l'anno (0.26% per lunedi', giro 4 volte il capitale), funding -0.01% per lunedi'; ordini limite eseguiti 95.11%.
* Dove nasce (descrittivo, lordo): prima della Borsa (01:00-13:00) 0.16% per lunedi' (t 0.31); dentro la Borsa (13:00-22:00) -0.09% (t -0.14).
* Lunedi' festivi americani (fatti lo stesso): {"2026-09-07": ["Labor Day", 0.01254]}.

## Letture delle regole

* prezzo 'alle 00:00 del lunedi'' = apertura della candela di 1 ora delle 00:00 UTC; base = apertura della candela delle 22:00 UTC del venerdi' (50 ore prima)
* universo del lunedi': contratti con almeno 40 giorni di storia (prima candela almeno 960 ore prima di lunedi' 00:00) e con tutte le candele che servono (venerdi' 22, lunedi' 00, 01, 02, 13 e 22); fra questi i 30 con piu' volume in dollari (somma del volume in dollari delle candele a 1 ora) delle 672 ore prima
* con 20-29 contratti il quinto = parte intera di n/5 (pesi uguali, ogni lato al 100%)
* ordine d'entrata: limite a 0,02% sull'apertura delle 01:00 per un'ora: preso se il minimo dell'ora e' sotto l'apertura (acquisto) o il massimo sopra (vendita), costo 0,02%; altrimenti mercato 0,05% + scarto piu' lo spostamento del prezzo nell'ora (stessa regola di `cinquantaseiesima.costo_limite`); uscita a mercato 0,05% + scarto
* rendimento di un contratto = apertura 22:00 / apertura 01:00 - 1; funding = tassi dei regolamenti con tempo da 01:00 (incluso) a 22:00 (escluso), long paga, short incassa
* scarto 0,02% (0,01% BTC/ETH/SOL, che qui non ci sono); controllo informativo con 0,05% per tutti
* quarto trimestre = ottobre e primo lunedi' di novembre; trimestre negativo = somma dei rendimenti settimanali sotto zero
