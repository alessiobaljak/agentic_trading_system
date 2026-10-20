# Programma 6 — diciassettesima prova: sei modelli in gara, scelti ogni volta solo col passato (M4, M5)

Scritto il 20 ottobre 2026, mattina, **prima di qualunque calcolo**. Vale `QUATTORDICESIMA.md` (ingredienti, obiettivo,
cadenza, portafoglio, esame) dove qui non si dice altro.

## 1. Perché

Il proprietario: «fai girare modelli su modelli». Provare tanti modelli e tenere il migliore sul passato è proprio l'errore
del primo gate. Il modo con metodo è mettere la **scelta del modello dentro la finestra che avanza**: ogni 4 settimane i modelli
si allenano sul passato **tranne le ultime 12 settimane**, si guarda chi ha previsto meglio quelle 12 settimane (che il modello
non ha visto), e si usa quello, riallenato su tutto il passato, per le 4 settimane dopo. Così la scelta usa solo il passato e la
prova resta una sola.

## 2. I sei modelli (valori fissati qui)

1. **alberi** come M1 (`HistGradientBoostingRegressor`: 300 iterazioni, passo 0,05, 15 foglie, almeno 200 esempi per
   foglia, L2 1);
2. **alberi bassi**: lo stesso con 7 foglie e almeno 400 esempi per foglia;
3. **foresta** (`RandomForestRegressor`: 200 alberi, profondità al massimo 6, almeno 200 esempi per foglia, il 30% degli
   ingredienti per ogni scelta);
4. **alberi casuali** (`ExtraTreesRegressor`: gli stessi valori della foresta);
5. **lineare** come M2 (`Ridge`, alfa 10);
6. **rete neurale piccola** (`MLPRegressor`: due strati da 32 e 16, regolarizzazione 0,001, fermata anticipata, al massimo
   200 giri).

Seme 2026 per tutti. Per i modelli 3-6 il dato che manca vale 0 (il centro dei ranghi) e gli ingredienti di mercato sono
standardizzati con il solo periodo di allenamento; i modelli 1-2 i mancanti li gestiscono da soli.

## 3. Le due varianti (due prove: nel conto del programma 6 diventano **40**)

* **M4, la scelta**: a ogni riallenamento si sceglie il modello con il legame di rango medio più alto fra previsione e
  rendimento nelle 12 settimane tenute da parte (a parità, l'ordine della lista); lo si riallena su tutto il passato.
* **M5, la media**: la media dei ranghi delle previsioni dei sei modelli, tutti riallenati su tutto il passato.

Portafoglio, costi ed esame come M1 (`QUATTORDICESIMA.md`, sezioni 3 e 4), con lo Sharpe corretto sulle **40** prove. Si
riporta anche quante volte ogni modello è stato scelto.
