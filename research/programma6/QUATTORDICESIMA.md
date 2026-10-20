# Programma 6 — quattordicesima prova: un modello che impara da solo come unire tutti gli indicatori

Scritto il 20 ottobre 2026, mattina, **prima di qualunque calcolo**, dopo l'indicazione del proprietario: «hai accesso a
tutti gli indicatori usati nel mondo del trading [...] puoi fare qualcosa che anni fa era impossibile, capire come unirli
o se usarli singoli per creare strategie che prima non erano mai state pensate [...] non vuol dire inventarle ed andare a
caso come fatto nel primissimo gate [...] usando anche tutti i dati che abbiamo raccolto fino ad ora per imparare».

## 1. Perché così

* Unire gli indicatori «a mano» vuol dire provare molte combinazioni sugli stessi anni: è quello che ha rovinato il primo
  gate (migliaia di prove, le passate perdevano in paper), e ogni prova in più alza la soglia dello Sharpe corretto.
* Il modo con metodo è far **imparare** le combinazioni a un modello, che **ogni 4 settimane** si allena **solo sul
  passato** e decide le 4 settimane dopo, che non ha visto: è una finestra che avanza, quindi tutto il periodo di prova è
  fuori dal campione del modello. Il modello e i suoi valori si fissano **qui, una volta**: niente ritocchi dopo.
* Letteratura: Cakici e altri, «Machine learning and the cross-section of cryptocurrency returns» (International Review
  of Financial Analysis, 2024): 40 caratteristiche, oltre 500 monete, 2017-2023; i modelli separano le monete che rendono
  di più da quelle che rendono di meno anche dopo i costi, **i più semplici vanno meglio** e molto del guadagno viene
  dalle monete piccole e poco liquide. Per questo: due modelli, uno ad alberi e uno lineare semplice, e solo le 100 monete
  più scambiate.

## 2. Gli ingredienti (tutto quello che abbiamo raccolto), ogni lunedì con i dati fino alla domenica

Per ogni moneta, **portati al rango fra le monete dell'universo** (fra −0,5 e +0,5; il valore che manca resta mancante):

* i **28 indicatori di CTREND** (RSI, stocastici, CCI, medie mobili, MACD, volumi, Chaikin, Bollinger: `terza.py`);
* **rendimenti** di 1, 7, 30, 90 e 180 giorni; **volatilità** di 7, 30 e 90 giorni; rendimento giornaliero più alto e più
  basso e asimmetria dei 30 giorni; ampiezza media della giornata (massimo meno minimo sul prezzo) dei 7 giorni;
* **funding** degli ultimi 1, 3, 7 e 30 giorni;
* **acquisti a mercato** (quota del volume) di 1, 7 e 30 giorni; **volume** dei 7 giorni rispetto ai 90; grandezza (mediana
  del volume dei 30 giorni); età della moneta;
* **legame col Bitcoin**: beta, correlazione e volatilità propria dei 90 giorni;
* **posizioni** (dal dicembre 2021): crescita dell'interesse aperto di 1, 7 e 30 giorni; interesse aperto sul volume;
  rapporto long/short delle posizioni dei grandi e dei conti di tutti (media dei 7 giorni) e la loro differenza; rapporto
  fra acquisti e vendite a mercato (media dei 7 giorni).

E, uguali per tutte le monete (per imparare quando un segnale vale e quando no): rendimento del Bitcoin di 7 e 30 giorni,
volatilità del Bitcoin di 30 giorni, funding medio del mercato dei 7 giorni, rendimento medio e dispersione dei rendimenti
di 7 giorni fra le monete.

## 3. Cosa impara e come opera

* **Obiettivo**: il rango del rendimento della settimana dopo fra le monete dell'universo (fra −0,5 e +0,5).
* **Allenamento**: ogni 4 settimane, su tutte le settimane già concluse prima (al massimo le ultime 156, almeno 52).
* **M1, alberi**: `HistGradientBoostingRegressor` di scikit-learn con 300 iterazioni, passo 0,05, al massimo 15 foglie,
  almeno 200 esempi per foglia, regolarizzazione L2 pari a 1, seme 2026; i mancanti li gestisce il modello.
* **M2, lineare**: `Ridge` con alfa 10 sugli stessi ingredienti, i mancanti messi a 0 (il centro dei ranghi), gli
  ingredienti di mercato standardizzati con media e deviazione del solo periodo di allenamento.
* **Portafoglio**: ogni lunedì long il quinto con la previsione più alta, short il più basso, pesi secondo la volatilità dei
  30 giorni (come F3), lato long +1 e short −1, una settimana; costi e funding come la sesta prova.
* Due prove: nel conto del programma 6 diventano **36**.

## 4. L'esame

Dal **3 gennaio 2022** all'ultima settimana completa (i dati sulle posizioni partono dal dicembre 2021): le condizioni della
terza prova (`TERZA.md`, sezione 4) con lo Sharpe corretto sulle **36** prove, gli anni 2022-2026 (almeno 4 su 5) e i
trimestri pieni dal 2022 al 2025. Si riportano anche, solo come informazione: gli ingredienti che contano di più nell'ultimo
modello (importanza per permutazione), la correlazione con F3 e K1, e il risultato sulle monete 101-200 con lo scarto 0,10%.
Se una delle due passa l'esame, entra nel paper.

## Nota tecnica (20 ottobre 2026, prima di qualunque risultato)

Il primo avvio si è fermato al primo allenamento di M1: il modello ad alberi di scikit-learn 1.9.1 non accetta una colonna
**tutta mancante** (le posizioni prima del dicembre 2021). Correzione: a ogni allenamento di M1 si tolgono le colonne tutte
mancanti in quell'allenamento (e le stesse nella previsione). Da una colonna vuota il modello non impara niente, quindi la
regola non cambia. Nessun numero era stato prodotto.
