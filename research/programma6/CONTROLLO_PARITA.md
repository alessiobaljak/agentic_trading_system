# Programma 6 — la revisione indipendente di F5 e la correzione delle parità del funding

23 ottobre 2026. Il proprietario: «c'è qualcosa che ci stiamo perdendo?». Un revisore separato (una sessione che non aveva scritto
F5) ha ricontrollato tutto il percorso di F5 cercando errori che gonfiano il risultato: dati futuri, monete sopravvissute, conto dei
pesi, costi, ordini limite. Non ha modificato file; i suoi script sono fuori dal repository. Qui quello che ha trovato, quello che
ho corretto e quanto cambia (`controllo_parita.py`, `risultati_controllo_parita/`).

## 1. L'errore dimostrato: le parità decise dall'arrotondamento

Ogni settimana circa il 7% delle monete ha lo stesso funding dei 7 giorni (spesso quello di base, 0,01% a regolamento).
`sesta.funding_7` lo calcolava come differenza di due somme cumulate, che lascia un residuo di circa 1e-17; quel residuo decideva
l'ordine fra le monete pari, e **non a caso**: segue il funding cumulato (correlazione di rango −0,42) e l'età della moneta
(−0,30), e metteva più spesso le monete vecchie dal lato long. Cambiava lato in 390 casi su 15.324. Con le parità decise a caso
(100 volte) lo Sharpe di F5 va da 1,71 a 1,93, mediana 1,81: il valore pubblicato (1,933) era il più alto.

**Correzione:** `funding_7` arrotondato a 12 decimali; le parità restano parità e prendono il rango medio, come fa già il bot
(`bot/portafoglio/f5.py` somma i regolamenti uno per uno). Vale per tutte le prove che usano il funding dei 7 giorni dalla 57 in
poi e per il paper di ricerca dal prossimo aggiornamento; le prove già fatte restano scritte come erano, con questo file accanto.

| Strategia | Sharpe prima | Sharpe dopo | l'anno dopo | discesa dopo | settimane cambiate | t dopo | Sharpe corretto dopo (con l'aggiunta) |
|---|---|---|---|---|---|---|---|
| F5 | 1,933 | **1,868** | +55,0% | −26,9% | 108 su 302 | 4,50 | 0,90 |
| F5 a ordini limite (F9) | 1,987 | **1,923** | +56,5% | −26,7% | 90 su 302 | 4,63 | 0,92 |
| K2 | 1,720 | **1,745** | +43,4% | −22,7% | 99 su 250 | 3,83 | 0,80 |
| F5 + M7 + K2 | 2,107 | **2,101** | +42,4% | −28,4% | 235 su 250 | 4,61 | 0,94 |

Per anno dopo la correzione, F5: 2021 +122,7%, 2022 +31,7%, 2023 +30,7%, 2024 +65,8%, 2025 +50,6%, 2026 +21,5%: **ancora
positiva ogni anno**. M7 non è ricalcolato (il modello andrebbe riallenato: i suoi ingredienti di funding hanno lo stesso residuo,
ma pesano poco fra circa 70).

## 2. Cosa il revisore ha controllato e trovato giusto

* **Dati futuri: nessuno.** I regolamenti cadono all'ora giusta (54 su 2.722.260 fuori dal secondo, tutti entro il minuto); quello
  delle 00:00 del lunedì va alla domenica (segnale), non alla settimana tenuta; il funding nel conto è quello dalle 08:00 del
  lunedì alle 00:00 del lunedì dopo, con il segno giusto; volatilità, volume e universo usano dati fino alla domenica; il prezzo
  d'entrata è l'apertura delle 00:00 (14.204 posizioni su 14.204).
* **Monete tolte dal listino:** la correzione del 20 ottobre regge (892 simboli, LUNA contata con −99,99%).
* **Conto dei pesi e costi su ogni variazione:** giusti. **Settimane escluse:** nessuna (302 su 302).

## 3. Punti deboli da sapere (non errori)

* **L'ultimo regolamento conta molto:** circa 0,2 di Sharpe viene dal regolamento delle 00:00 del lunedì (senza: 1,73). Non è
  futuro (il tasso è fissato con i dati fino alle 00:00), ma il bot deve leggerlo. **Fatto:** il bot non decide se manca per più
  del 10% delle monete e riprova dopo 30 minuti (`pesi_del_lunedi`, test in `tests/test_paper_f5.py`).
* **Entrare più tardi costa:** alle 01:00 Sharpe 1,92, alle 04:00 1,86, alle 06:00 1,83 (prima della correzione delle parità).
* **Gli ordini limite sono fragili:** il guadagno (+0,06 di Sharpe) assume che l'ordine si esegua se il prezzo va oltre il livello
  anche di poco. Chiedendo che vada oltre dello 0,05%: eseguiti 94,9%, Sharpe 1,87, spese 6,9% l'anno (più che a mercato); dello
  0,10%: 1,77. Gli ordini non eseguiti costano molto (il prezzo è scappato), quindi bastano pochi casi in più per perdere il
  vantaggio. Il bot tiene accanto il costo tutto a mercato: la differenza vera si vedrà solo con ordini veri, che non facciamo.
* **Lo scarto delle altcoin (0,02%) non è mai stato misurato** sui libri degli ordini del 2021: con lo 0,10% per le monete fuori
  dalle prime 50, Sharpe 1,83; con i costi doppi 1,77, tripli 1,60.
* **Funding stimato nelle ultime settimane:** ottobre 2026 non ha ancora il file mensile di Binance, quindi 11.214 valori sono la
  media dei 90 giorni prima (settimane del 28 settembre, 5 e 12 ottobre). Senza quelle settimane Sharpe 1,95: non gonfia, ma non
  sono numeri veri. Voce nel backlog.
* **Concentrazione:** con i pesi secondo l'inverso della volatilità TRX arriva al 32,5% del lato long ed è sopra l'8% in 111
  settimane. È un rischio, non un errore. Voce nel backlog.
* **Stima prudente del revisore** (parità vere, entrata alle 01:00, senza le settimane col funding stimato): Sharpe 1,865,
  +54,7% l'anno, ogni anno positivo.
